# Transport / RPC library (roadmap P6)

Two Vilan processes communicate and move data across a wire — client↔server and
server↔server. The largest remaining *Next up* item (XL). This proposal settles the
**model and philosophy** before any build.

**The shift in this revision.** An earlier draft made the library a *generator*: a
`[service]` trait that emitted a server dispatcher and a client stub, with
`[derive(Json)]` serializing whole structs. We've since concluded that an RPC library
can only do so much before it begins encroaching on application logic or collapsing
under its own configuration surface. So the library's job is narrower and more
durable: **be a guide, not the structure.** It provides a few sharp primitives and an
established paradigm — it *nudges* the developer toward the correct shape rather than
generating it. The systems help build the right structure; they are not themselves
that structure. The core we already have (a `Transport` seam, a codec) is usable
today; what's left is to settle *how* one is meant to use it.

## 1. Requirements (from the roadmap)

- **Data crosses without hand-written codecs** — a derive handles encode/decode; the
  developer never writes a serializer by hand.
- **Pluggable transports** — HTTP / WebSocket / in-process as built-ins, *custom
  transports first-class* (not privileged over built-ins).
- **An explicit, narrow exposure surface** — what's remotely callable is opt-in and
  small; nothing is reachable by default.
- **The reactive north star** — a remote handle: the server holds a writable `Signal`,
  the client sees a read-only `Source` whose `.sub(..)` subscribes over the transport.

## 2. The pieces

| Piece         | Role                                                                                             | Form                                                                                                                                          |
| ------------- | ------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------- |
| **Codec**     | value ⇆ bytes — the *format*                                                                     | a `trait` — JSON default; binary later                                                                                                        |
| **Transport** | moves frames over the wire — a dumb pipe                                                         | a `trait` — request/response (HTTP) or **duplex** (WebSocket)                                                                                 |
| **Protocol**  | the *semantics* over a transport + codec                                                         | **RPC** (request/response) and **Reactive** (pub/sub) — siblings                                                                              |
| **Service**   | the *server* surface; the client requestor is a generated projection of it (two signatures — §4) | a hand-writable foundation (`call` + `Dispatcher`), optionally sugared by a `[service(Client)]` struct (`[rpc]` methods + `[expose]` signals) |

The stack composes bottom-up: a **codec** turns values into bytes, a **transport** moves
those bytes as frames, and a **protocol** layers the *meaning* on top — request/response
for RPC, publish/subscribe for reactive. Keeping *protocol* distinct from *transport* is
what lets a plain HTTP request/response transport carry RPC with no reactive machinery
shoehorned in, and a reactive `Source` ride a duplex transport, without either concern
leaking into the other (§5, §8). Transport and codec are a protocol's two dependencies —
composed *under* it, as siblings.

Within the RPC protocol the **guide-not-generator** line is drawn precisely: the dispatch
plumbing — the server router and the client requestor — is a hand-writable foundation
(`call` + `Dispatcher`, §4.1), which the compiler can *generate* from a `[service(Client)]` struct
(§4.2) as sugar, so a remote call reads like a local one. But it generates **only
the plumbing**: the *structure* — which types cross the wire (`[derive(Wire)]`, §3) and how
a domain type projects to its wire shape (`to_wire`, §3) — stays the developer's. The
library owns the mechanical encode→route→decode that is identical every time; that is what
makes a remote call *seamless* without dictating your shape — the "C" in RPC, paid for
honestly (§7: latency and failure stay visible).

It is **peer-symmetric**: "client" and "server" are just *who hosts the methods* vs
*who calls them*. Server↔server is the same mechanism with an HTTP/WS transport between
two Node processes; client↔server is the same with the browser calling over HTTP.

## 3. The data boundary: `[derive(Wire)]`

This is the heart of the new model. Data crosses the wire **only** as a *Wire type* — a
struct or enum that opts in with `[derive(Wire)]`. One rule governs it, and the rule is
the entire safety story:

> **Every field of a `[derive(Wire)]` type must itself be Wire.** A non-Wire field is a
> *compile error*, not a silently-omitted field.

This inverts the usual "remember to strip the sensitive field before sending" chore —
the thing a developer means to do later and forgets, leaking a password hash — into a
property the type system enforces *by construction*. Sensitivity becomes a property of
a **type**, declared once, not a checklist re-applied at every call site:

```vilan
// server-side

[derive(Wire)]
struct Uuid {
	// ...
}

// NOT `[derive(Wire)]` — a password hash must never reach the wire, so the type that
// holds it is simply not Wire. Nothing containing one can be Wire either.
struct Password {
	hash: str,
}

impl Password {
	fun set(self, plaintext_password: str) {
		self.hash = bcrypt::hash(plaintext_password, bcrypt::gen_salt());
	}
}

impl Password with PartialEq<str> {
	fun eq(self, plaintext_password: str): bool {
		bcrypt::compare(self.hash, plaintext_password)
	}
}

// The rich domain type. It holds a `Password`, so it *cannot* derive `Wire` — and the
// compiler says so. There is no way to "accidentally" send a `User`.
struct User {
	id: u32,
	username: str,
	password: Password,
}

impl User {
	// The explicit projection from the domain type to its wire shape. Developer-
	// written, so it can diverge from the source arbitrarily.
	fun to_wire(self): WireUser {
		WireUser {
			uuid = self.get_uuid(),     // a *computed* field — `User` has no `uuid`
			username = self.username,   // `id` and `password` simply don't cross
		}
	}
}

[derive(Wire)]
struct WireUser {
	uuid: Uuid,
	username: str,   // or could be `username: Signal<str>` — see §7
}

impl WireUser {
	// A manual subscription accessor: a plain `Signal<str>` field is the easy path,
	// but writing the `Source` by hand is sometimes what you want.
	fun get_username(self): Source<str> {
		// ...
	}
}

// A server method producing the wire shape — one `[rpc]` method of a `[service]` (§4).
// The projection is the only place the boundary is crossed, and it is explicit.
fun get_user(id: i32): Option<WireUser> {
	// ...look up the domain `User` (password and all), then project...
	Some(user.to_wire())   // `User` itself never crosses; only the wire shape does
}

// client-side — the generated `[service]` stub reads like a local call (§4, §7)
let john = accounts.get_user(1);   // -> Result<Option<WireUser>, RpcError>
```

What this buys, beyond the leak guarantee:

- **The wire shape diverges freely from the source.** `WireUser.uuid` is *computed* in
  `to_wire` and is not a field of `User` at all; `User.id` and `User.password` never
  appear. The client's view of an entity is whatever the projection chooses to expose —
  nothing more.
- **References travel as handles.** The same mechanism sends an arena `Handle` (or a
  reactive `Source`, §7) in place of an owned value — a "pointer" across the wire,
  resolved on the far side — because the projection decides what each field *means*.
- **No skip-lists, nothing to forget.** We considered per-field `[skip]` attributes and
  auto-projection; both were rejected. A skip-list is exactly the annotation a
  developer forgets. Here the boundary is a *type you write on purpose*, and the
  compiler refuses to let a non-Wire type slip across. Decode produces the Wire type
  directly (a `WireUser`), with no vestigial always-empty fields.

The cost is honest verbosity: a domain type and its wire twin, plus a `to_wire`. The
paradigm accepts that — the explicitness *is* the feature — but it is the first place
**syntactic sugar** would earn its keep (a derive that scaffolds a projection for the
encodable fields, which the developer then edits), and that sugar is a deliberately
later, additive step, never the default.

### 3.1 What is Wire

Wire-by-default: scalars, `str`, `bool`, `List<T: Wire>`, `Option<T: Wire>`, and
`[derive(Wire)]` structs/enums (nested). Mechanically this reuses the existing
`Json`/`FromJson` round-trip (`std::json`); `Wire` is the *capability marker* that says
"this is intended for, and permitted on, the wire" — distinct from `Json`, which is
general-purpose serialization with no exposure semantics. The current codec gaps carry
over and are *codec* limits, not RPC limits (they lift as the derives improve):

- ⛔ **`Map<K, V>`** — no JSON impl yet; use a derived struct or `List<Pair>` until Map
  serialization lands (backlog I1).
- ⛔ **`List<List<T>>`** — a collection directly nested in a collection doesn't
  round-trip yet (the dispatch-time monomorphization gap); wrap the inner list in a
  one-field Wire struct for now.

### 3.2 Keeping ubiquitous derives out of the way: `[trait_only]`

The Wire boundary is most useful when `[derive(Wire)]` is cheap to put on *everything* —
but a `Wire` derive on every struct (alongside `Debug`, `Json`, …) would bury each type's
real API under generated methods (`encode`, `decode`, `to_json`, …) and invite **name
collisions** with a type's own `id`/`name`/`encode`. Two attributes keep the namespace
clean. Both are *general language features*, not RPC-specific, so they likely warrant
their own small proposal that this one depends on; they are recorded here because they
are what makes ubiquitous `Wire` livable.

- **`[trait_only]`** — a trait method so marked is reachable *only through the trait*,
  never promoted onto a concrete type's method surface. Vilan has no `dyn`, so "through
  the trait" means *through a trait bound* (`fun f(x: ToJson)` is sugar for
  `f<T: ToJson>`): the method resolves on a trait-bounded receiver but not on the bare
  concrete type.

  ```vilan
  trait ToJson {
      [trait_only]
      fun to_json(self): str;
  }
  impl Point with ToJson { fun to_json(self): str { i"{'x':{self.x},'y':{self.y}}" } }

  point.to_json()        // ✗ error: no method `to_json` on struct `Point`
  stringify(point)       // ✓
  fun stringify(value: ToJson): str { value.to_json() }   // ✓ — via the bound
  ```

  This is stronger than Rust's "the trait must be in scope to call its method": it forbids
  the direct call *even with the trait in scope*. That extra restriction is the point — it
  buys **collision-safety**: a type's own `id`/`encode`/`to_json` is never shadowed by, nor
  shadows, a blanket-derived one; clutter alone would only need `[doc(hidden)]` below. The
  cost is that the convenient `point.to_json()` is gone — you go through the trait
  deliberately.

  **✅ The mechanism shipped (2026-07-02):** `[trait_only]` on a trait's method declaration
  excludes it from concrete-type member resolution — instance calls, statics
  (`Pt::make()`), and inherited defaults alike — while the trait-bound paths (`value.tag()`
  under `T: Marker`, `T::make()`) resolve as before; the "no method" diagnostics say *why*
  and name the trait. An inherent same-name method stays reachable (the collision-safety
  point, pinned by test). One pre-existing, independent gap surfaced and is pinned
  `#[ignore]`d: on a name collision, a *bound call's* monomorphized dispatch resolves the
  concrete type's inherent method instead of the trait's inherited default (the
  transformer's name-based dispatch lookup — reproduces without `[trait_only]`).

  **Derived trait methods are `[trait_only]` by default — settled, but the flip is
  deferred.** A `[derive(Wire)]` / `[derive(Json)]` / `[derive(Debug)]` should generate
  `[trait_only]` methods, so "derive on everything, clutter nothing" is the default; a trait
  opts a method back *out* when the concrete-type call is genuinely wanted. **Why deferred:**
  the derive-generated bodies themselves call the methods *concretely* — a derived `to_json`
  emits `self.field.to_json()` on concrete field types, and decode emits
  `Point::from_json_value(..)` statics — so flipping the std trait declarations today would
  break the generated code (and every direct `.to_json()` in the corpus, the rpc example's
  envelope handling, …). The flip needs the derive codegen (and the touched call sites) to
  route through bound-generic helpers (`fun encode<T: Json>(value: T): str`) first — its own
  migration slice, best taken with (or after) `[service(Client)]` generation so the
  generated client/dispatcher is born bound-clean.

- **`[doc(hidden)]`** — Rust-style: the method stays fully callable, but the language server
  omits it from completion. A *tooling* concern only, with no resolution change, for methods
  you want reachable-if-typed but not in the `.` menu. Where `[trait_only]` changes *what
  resolves*, `[doc(hidden)]` changes only *what is suggested*. **✅ Shipped as a parsed,
  recorded marker (2026-07-02)** — its consumer is editor *completion*, which the language
  server doesn't offer yet; the flag is on `Function` for when it does.

## 4. Exposure: the two-signature split, the foundation, then `[service]` sugar

An RPC endpoint has **two faces with different types**, and getting that right is the whole
design:

```vilan
// server — the real implementation, a clean local body
fun get_user(uuid: str): Option<WireUser> { /* look it up */ }

// client — a requestor that can fail at the wire
fun get_user(uuid: str): Result<Option<WireUser>, RpcError> { /* send, await, decode */ }
```

They differ by a `Result<_, RpcError>` layer *and* by their body. Crucially, they **cannot be
one function whose signature varies by caller**: that would require the compiler to know each
call site's "side," which is *undefined* for server↔server — a server calling another
server's endpoint is a *client* of it yet a *server* in its own right, so there is no global
side to switch on. So the two faces are **two functions in different namespaces**, not one
function the compiler bends. The **server face is the source of truth** (real logic); the
**client face is a mechanical projection** of it — wrap the return in `Result`, swap the body
for a wire call.

That reframes `[service]`/`[rpc]` as **sugar over a foundation that stands on its own**
(§4.1), not a mandatory system: both faces are ordinary Vilan, hand-writable, and read well
*without* the sugar. The sugar (§4.2) only generates the client face — and the server
routing — from the server declaration.

### 4.1 The foundation — an ergonomic hand-written API (no compiler features)

> **Re-plumbed onto the codec, single-pass (settled 2026-07-02).** The original foundation
> carried args/results as pre-encoded JSON strings inside a JSON envelope — the measured
> ~15% double-encoding. The envelope is now written in ONE pass through §6.2's `Codec`:
> args describe themselves directly into the envelope's serializer (heterogeneous args as
> a list of describe-closures), and the server pulls each argument straight from the
> positioned deserializer — **in declaration order, exactly once** (the schema-ordered
> binary format requires it; generated handlers obey by construction, hand-written ones
> by contract). On the wire, JSON args are now plain values (`{"method":"add","args":[1]}`
> — no escaping), and the reply is `{"Success":<value>}`. A decode failure poisons the
> request's deserializer; the handler checks `decode_failed(request)` BEFORE running the
> impl and returns `RpcError::Decode(reason)` — validating decode, end to end. The codec
> is chosen at wiring time on both sides (`Client { transport, codec }`,
> `dispatcher().into_protocol(codec)`); format choice stays deployment-wide (Q6). The
> reactive protocol rides the codec too since the reactive-on-codec follow-up (§8's
> amendment): typed mirrors, single-pass `Update` envelopes, binary over WS.

**Client:** one helper turns a typed call into a wire round-trip; the developer never touches
the envelope, the await, or the error layer:

```vilan
// Encode the request in one pass, await the round-trip, decode the reply as `T`.
// Infrastructure failures — transport, decode, a remote error — are `Err(RpcError)`.
fun call<T: Wire, Tx: Transport>(
    transport: Tx, codec: Codec, method: str, args: List<|Serializer| void>,
): Result<T, RpcError>

// A typed client is a thin holder over a transport + codec; each method is one line.
struct AccountsClient<Tx: Transport> { transport: Tx, codec: Codec }
impl AccountsClient<type Tx> {
    fun get_user(self, uuid: str): Result<Option<WireUser>, RpcError> {
        call(self.transport, self.codec, "get_user", [|s: Serializer| uuid.describe(s)])
    }
}
```

**Server:** a `Dispatcher` routes requests to your handlers; the handlers stay plain
functions returning domain values. `RpcRequest` is a *handle* over the request's
deserializer (not decoded data); `arg` pulls the next argument at its parameter type,
`decode_failed` gates the impl, `reply` captures the result as a describe-closure
(`RpcOutcome`) that the protocol encodes into the reply envelope:

```vilan
Dispatcher::new()
    .on("get_user", |req| {
        let id: i32 = arg(req, 0);
        match decode_failed(req) {
            Some(let reason) => RpcOutcome::Failure(RpcError::Decode(reason)),
            None => reply(lookup(id).map(|u| u.to_wire())),
        }
    })
```

This is exactly `examples/rpc`'s hand-written dispatch/stub, **distilled into a reusable
API** — and it is the API the developer wants *whether or not* the sugar exists, which is
why it is built first and why the sugar is optional.

### 4.2 `[service]` / `[rpc]` / `[expose]` — sugar that generates the client from the server

> **`Client::connect` (settled + shipped 2026-07-02)** — the promised connect-time
> enforcement, fully generated. `Client::connect(url, codec)` (a static on the concrete
> `impl Client<SocketTransport>`) opens the WebSocket, **verifies the contract hash
> first** — a drifted server is a clean `Err(RpcError::Contract(..))`, never decode
> garbage (Q6's enforcement, finally) — then calls the generated `__attach` route with
> the socket's connection id and wires one `RemoteSource` mirror per `[expose]`d field
> from the returned channel list (declaration order). The server half is symmetric:
> the generated dispatcher gains `__attach`, answered from a runtime **session
> registry** (`std::rpc`'s `register_session`/`drop_session`/`session_of`), and
> `std::rpc_server::serve_service(port, protocol, fallback, on_ready)` is
> `serve_connected` with that registry as its connection lifecycle — the whole
> manual dance (per-connection `ReactiveServer`s, an app-written `attach`, mirror
> construction) collapses. Manual wiring stays available (`serve_connected` +
> your own attach) for SSE clients and custom session state; `connect` is the
> WebSocket path.

The service is a **per-connection struct + impl** — the source of truth. `[service(Client)]`
on it generates a sibling client type (named by the argument — `[service]` alone defaults to
`<Struct>Client`); `[rpc]` marks a method callable over the wire; `[expose]` marks a `Signal`
field the client may observe:

```vilan
[service(Client)]
struct Session {
    [expose] status: Signal<str>,        // observable by the client (mirrored — §8)
    user_id: Shared<Option<i32>>,        // private session state — never crosses the wire
}

impl Session {
    // an async action: takes `self` (it awaits), mutating through the Signal/Shared handles
    [rpc] fun login(self, name: str, password: str): Result<void, LoginError> {
        let ok = await verify(name, password);
        if ok {
            self.user_id.write() = Some(id_of(name));
            self.status.set("online");
            Ok()
        } else {
            Err(LoginError::BadCredentials)
        }
    }
    // auth is manual (Q4): ordinary body logic over the session state `login` populated
    [rpc] fun rename(self, name: str): Result<WireUser, LoginError> {
        match self.user_id.read() {
            Some(let id) => Ok(rename_user(id, name)),
            None => Err(LoginError::NotAuthenticated),
        }
    }
}

// the server instantiates one per connection; the generated dispatcher owns it
fun on_connect(): Session {
    Session { status = Signal::new("offline"), user_id = Shared::new(None) }
}
```

- **`[service(Client)]`** names the generated client type. The struct *instance is the
  connection's session* — created on connect, owned by the generated dispatcher, so its state
  persists across that connection's calls (Q9).
- **`[rpc]`** marks a method **callable over the wire** — opt-in; the `[rpc]` methods *are* the
  surface (anything else is unreachable remotely — the attack-surface guarantee). Its signature
  must be **Wire-compatible** (every parameter and the return Wire, or `Option`/`Result`/`List`
  of Wire); a non-Wire `[rpc]` method is a clear compile error. **Auth is manual (Q4):** an
  auth `[rpc]` (`login`) populates session state and other methods check it in their body —
  no auth attribute; a declarative `[rpc(auth)]` gate is deferred sugar, reconsidered only if
  real services show the check as repeated boilerplate.
- **`[expose]`** marks a `Signal<T>` field the client may observe — private by default,
  observable only when marked, and only a `Signal` can be (exposure *is* observation; a plain
  value has nothing to subscribe to — Q9). `T` must be Wire. Any `[expose]`d field pulls in the
  reactive protocol, so the connection must be **duplex** (a pure-`[rpc]` service stays
  request/response).

From that the compiler emits the §4.1 foundation:

- a **dispatcher** that owns the per-connection `Session`, routes each `[rpc]` frame to
  `session.method(..)` (decode → call → encode), and registers each `[expose]`d signal in the
  §8 capability table; and
- a **client**, `Client::connect(transport)`, whose `[rpc]` methods are the `Result`-wrapped
  `call(..)`s (round-trip; §7) and whose `[expose]`d fields surface as read-only `Source<T>`
  mirrors (§8 `RemoteSource`).

```vilan
let client = Client::connect(socket);     // duplex — because `status` is exposed
await client.login("john", "hunter2");    // round-trip -> Result<Result<void, LoginError>, RpcError>
client.status.sub(|s| print(s));          // observe the mirrored server signal locally
```

The client is a **sibling type, not an `impl`** of anything the server wrote — its `[rpc]`
returns carry the extra `Result<_, RpcError>` layer (§7) and its `[expose]`d state is read-only
`Source<T>`, so it *cannot* share a signature with the server struct. The generated halves are
*only* this glue; the Wire types and `to_wire` projections stay yours (§2, §3).

## 5. Transport — the pipe (two shapes)

A transport is a dumb byte pipe; it moves encoded frames and knows nothing of methods or
subscriptions (that is the protocol's job, §7/§8). It comes in **two shapes**, matched to
what a protocol needs:

```vilan
// request/response — the shape the RPC protocol needs (HTTP, in-process)
trait Transport {
	// Send an encoded request frame, get the encoded reply. The explicit `Promise` marks
	// the round-trip as a place the caller `await`s deliberately (§7).
	fun call(self, request: List<u8>): Promise<List<u8>>;
}

// full-duplex — the shape the reactive protocol needs (WebSocket): either end may send a
// frame at any time, so the server can push unprompted.
trait DuplexTransport {
	fun send(self, frame: List<u8>);
	[must_use] fun on_frame(self, handler: |List<u8>| void): Subscription;
}
```

Built-ins:

- **HTTP** (`HttpTransport`) — **✅ shipped (2026-07-02)** — `impl Transport`: POSTs the
  request frame to the endpoint URL and reads the reply frame from the response body, over
  the host `fetch` (browser/node/deno/bun — a *base* std module). The server side is
  `std::rpc_server`'s `rpc_response` (composable into any `on_request`) / `serve_rpc` mount, which
  runs each frame in the wire-turn `batch`. Verified end-to-end by a CLI test: a Node process
  serves a generated dispatcher and calls itself over localhost — `verify()` (the generated
  Q6 contract check over the built-in `__contract` route) plus stateful round-trips.
  Request/response only — no reactive over plain HTTP.
- **In-process** (`LocalTransport`) — `impl Transport`: runs the server's dispatch in the
  same process. The substrate for **unit tests** (no network). (What `examples/rpc` uses.)
- **WebSocket** (`SocketDuplex`) — `impl DuplexTransport`: the true bidirectional pipe.
  **✅ shipped 2026-07-02** (unblocked by bits-and-bytes — the I2 gate; the RFC 6455
  parser is vector-pinned, and the realtime CLI test runs the SSE scenario verbatim over
  the socket — the drop-in promise held at one changed line):
  - **Client** (`connect_socket(url)`, base-layer `std::rpc`): the HOST `WebSocket` class,
    which browser, node (22+), deno, and bun all provide globally — no framing in-language.
    `connect_socket` awaits `open`, then the server announces `__conn:<id>` as its first
    text frame (the same handshake `SplitDuplex` speaks), so `.connection` and the app's
    `attach` flow are IDENTICAL — the literal drop-in swap: `connect_split(base)` →
    `connect_socket(url)`, nothing else changes.
  - **Server** (in `serve_connected`): node has no WS server, so the RFC 6455 server half
    is written in vilan — the `Upgrade` handshake on the http server's `upgrade` event
    (`Sec-WebSocket-Accept` = base64(SHA-1(key+GUID)) via a `node:crypto` extern) and the
    frame layer over the raw socket. `serve_connected` serves BOTH wires on one port:
    upgrade requests become WS connections, `/events`+`/send` stay SSE+POST — same
    `on_connect(id, DuplexEnd)`/`on_disconnect(id)`, same app code, clients pick.
  - **The frame layer** (`std::ws`, base — pure byte logic, unit-testable off-node):
    encode (unmasked server frames; 7/16/64-bit lengths) and a stateful parser (partial
    buffers, client masking via XOR, fragmentation reassembly, ping→pong, close). v1
    carries the duplex/reactive traffic as TEXT frames (opcode 0x1) — the reactive
    protocol is JSON-over-text either way; binary frames are wired when the reactive
    protocol goes codec.
  - **Multiplexing (settled 2026-07-02, second slice)**: the socket carries BOTH
    protocols via channel prefixes at the transport seam — `d:<frame>` for
    duplex/reactive traffic, `r:<id>:<frame>` for RPC — so the §4.1 envelope is
    untouched (the correlation id is transport framing, not wire format). The client's
    `SocketDuplex` gains a `transport()` view implementing `Transport`: `call` registers
    the id in a pending map, sends `r:`, and resolves the promise when the correlated
    reply lands; the server's upgrade path routes `r:` frames through the mounted
    protocol (a wire turn, reply written back with the same id) and `d:` frames to the
    app's `DuplexEnd`. The `__conn` announcement stays unprefixed (it precedes routing).
    Since the reactive-on-codec follow-up the socket carries BOTH kinds: text frames
    keep these prefixes, binary WS messages use tag bytes (`0x64` duplex, `0x72` +
    4-byte LE id RPC) — so a binary codec's requests AND updates ride the socket
    natively (`binaryType = "arraybuffer"` + a host-level kind check on `data`).
- **Asymmetric duplex** (`SplitDuplex`) — **✅ shipped (2026-07-02)** — a `DuplexTransport`
  *implementation* composing two directed channels internally: Server-Sent Events for
  server→client (`GET {base}/events`, read via fetch streaming + `TextDecoder` — works in the
  browser and node/deno/bun alike) and HTTP POST for client→server (`{base}/send?c=<conn>`).
  The server side is `std::rpc_server::serve_connected` (SSE + send + `/rpc` + a fallback route,
  every inbound frame a wire turn); each connection hands the app a fresh `DuplexEnd`, and the
  client `bridge`s its `SplitDuplex` into one — so `ReactiveServer`/`ReactiveClient` ride the
  real wire *unchanged*. The protocol still sees one `DuplexTransport`; the split is hidden in
  the transport — which is where the "duplex is two pipes" case belongs, not in the protocol's
  interface. Verified by a CLI test: two sessions over real SSE, one RPC mutation observed by
  both. Connections also **end**: the SSE stream's `close` (tab closed, network gone) scrubs
  the server-side wire and fires `serve_connected`'s `on_disconnect(id)`, and the app disposes
  that session's `ReactiveServer` (now `Disposable`; `expose` retains its source→mirror
  subscriptions so teardown actually releases the exposed sources) — without this a
  long-running server leaks a session per ever-connected client.

A custom transport (message queue, IPC pipe, WebRTC, a test double) is just an `impl` of the
shape it can provide — first-class, no registry.

## 6. Codec — the format (data ⇆ bytes)

> **Status (2026-07-03): IMPLEMENTED — the whole arc.** The correction below is kept as the
> record of the honest inventory that triggered the codec slice; everything it lists as
> missing has since landed: prerequisites (bits-and-bytes.md), the §6.1 visitor (records,
> then the trait shape — follow-up #4), both codecs (§6.2), the single-pass envelope
> re-plumb (double-encoding ~15% → ~0.2%), validating decode incl. `RpcError::Decode` and
> the guarded `try_parse_json` (a malformed frame is a sticky decode error, never a crash),
> and the reactive protocol on codecs (§8's amendment — typed mirrors, binary over WS).
>
> **Status (record corrected 2026-07-02): designed, NOT implemented.** Earlier revisions
> marked the `Codec` trait shipped (Q2, phase 1); it never was — no `Codec`, no
> `JsonCodec` exists anywhere. What shipped hardwires JSON at every seam:
> `[derive(Wire)]` expands to the same `to_json`/`from_json` as `[derive(Json)]` (plus
> the boundary check — that check is Wire's real identity today); transports move `str`
> frames; the §4.1 foundation (`call`/`arg`/`reply`) and the protocol envelopes are
> `Json`/`FromJson`-bound, and `[service(Client)]` generation emits over them; the
> reactive runtime erases to JSON `Signal<str>` mirrors and `Update(i32, str)` frames.
> Two costs are already visible: **double encoding** (args/results are individually
> encoded, then the envelope is encoded again — JSON-escaped-inside-JSON on every call;
> quantify in the phase-6 benchmarks), and `RpcError::Decode` is declared but never
> constructed (decode is happy-path — backlog I3).
>
> **Agreed plan (2026-07-02): prerequisites first, codec last.**
> 1. **Hex literals + bitwise/shift operators** (compiler; backlog I2) — binary framing
>    needs `0xFF`, `&`/`|`/`^`/`<<`/`>>`.
> 2. **`Bytes`** (std over the host `Uint8Array`; backlog I2's immediate want) — a
>    binary codec produces bytes, not text.
> 3. **The `Serializer`/`Deserializer` visitor + `[derive(Wire)]` retarget** — derived
>    code *describes* fields to a serializer instead of concatenating JSON;
>    `[derive(Json)]` stays as-is.
> 4. **Validating decode** (backlog I3, folded in) — the `Deserializer` returns
>    `Result`, finally constructing `RpcError::Decode`.
> 5. **The `Codec` trait + `JsonCodec` + a binary codec**, and protocols/transports
>    parameterized by it. Note the transport asymmetry: HTTP POST bodies carry bytes
>    fine, but SSE is a text protocol — `SplitDuplex`'s server→client leg stays textual
>    (JSON or base64) until the WebSocket transport (gated on the same I2) lands.

`[derive(Wire)]` settles *what* crosses and its *structure*; the **codec** settles the
*format* — the actual bytes. Keeping the two apart is what lets the same Wire types ride
JSON (readable, for development) or a compact binary format (fast, for production) with no
change to the types:

```vilan
trait Codec {
	fun encode<T: Wire>(self, value: T): List<u8>;
	fun decode<T: Wire>(self, bytes: List<u8>): Result<T, RpcError>;
}
```

- **Bytes, not `str`.** A binary format is not text, so the codec produces `List<u8>` (a
  stand-in until a real byte-array type lands — §11) and the transport moves bytes; JSON is
  just UTF-8 bytes. (The hand-written `examples/rpc` uses `str` because it is JSON-only; this
  generalizes that to bytes.)
- **Wire describes, the codec formats.** For "any serializer" to be real — not JSON with
  extra steps — `[derive(Wire)]` targets a `Serializer`/`Deserializer` visitor: the derived
  code *describes* a value's fields to a serializer, and `JsonSerializer` / `BinarySerializer`
  decide the bytes, so a binary codec carries no intermediate allocation. (A simpler first
  cut is a format-neutral `WireValue` tree each codec converts to/from — one allocation, but
  easy to ship. JSON ships first either way.)
- **The codec is a value, chosen at wiring time** — so the choice is *programmatic*, not a
  build flag baked into the derive. Switch by environment by constructing it at startup:
  `let codec = if Env::is_prod() { BinaryCodec::new() } else { JsonCodec::new() };` then
  `Accounts::connect(transport, codec)`. A `vilan.toml`/env setting is just one way to pick
  that value.
- **Both sides must agree on the format**, or negotiate it (a content-type announced on
  connect). Switching codecs is a deployment-wide decision across the client and server
  packages — the same drift concern as Q6. A self-describing binary format (MessagePack /
  CBOR-like) needs no shared schema; a compact one (protobuf-like) leans on the shared `Wire`
  type for field order.
- The **codec rejects malformed input** (decode → `Result`), so a hostile or stale payload is
  a clean `err`, never a panic or a type-confusion.

The codec also encodes the **invocation envelope** — an invocation is `(method name,
arguments)`, a reply is a result or an error — itself a Wire type, handled uniformly. In
JSON:

```jsonc
// request envelope                  // reply — success / failure
{ "method": "get_user",              { "ok": { "id": 42, "username": "ada", "handle": "@ada" } }
  "args": [42] }                      { "err": { "kind": "unauthorized", "message": "…" } }
```

The method name is a string (debuggable; a numeric id is a later compaction); `args` is
positional — the dispatcher knows each method's parameter order, so it decodes argument *i*
at the *i*-th parameter's type.

### 6.1 The visitor, in detail (codec prerequisite 3 — agreed 2026-07-02)

The format-independence mechanism: a Wire value *describes itself* to a `Serializer`, and
*rebuilds itself* from a `Deserializer` — the derive emits the description, the codec owns
the bytes. Proven hand-written first (a struct + enum with hand impls against
`JsonSerializer`), then generated.

> **UPGRADED to the trait shape (2026-07-02, follow-up #4)** — the compiler gaps that
> forced the record pivot are fixed (generic trait methods through bounds, incl. statics
> — the own-generic ordered-values channel covers method AND free calls). The design:
> traits `Serialize`/`Deserialize` carry the visitor surface; `Wire` is
> `describe<S: Serialize>` / `rebuild<D: Deserialize>` and monomorphizes to direct calls;
> the codecs' writers/readers implement the traits natively. The closure RECORDS remain —
> **as the codec-as-a-value erasure only**: `Serializer`/`Deserializer` keep their names
> and fields and now `impl` the traits by delegation, so `Codec { writer, reader }`, the
> RPC seam, and `|s: Serializer|` argument closures are untouched. Direct entry points
> (`encode_json`/`decode_json`, `encode_binary`/`decode_binary`) pass the writer/reader
> straight through — zero records, the measured fast path. A struct field and a
> same-named trait method coexist (probed), which is what lets the records implement
> their own vocabulary.
>
> The original pivot note, for the record:
>
> **v1 shape (settled by probe, 2026-07-02): the serializer/deserializer are CLOSURE
> RECORDS, not traits.** The trait design below hit two compiler gaps: a trait method
> with its own generics (`fun describe<S: Serializer>`) **silently no-ops when
> dispatched through a generic bound** (a miscompile — pinned `#[ignore]`), and an impl
> can't bind a trait's argument (`impl T with Describe<type S: Serializer>` — "cannot
> find type 'S'"). So v1 uses the house trait-object stand-in (`Dispatcher`/`DuplexEnd`
> precedent): `struct Serializer`/`struct Deserializer` whose fields are closures, and
> `trait Wire` has plain methods `describe(self, serializer: Serializer)` /
> `rebuild(deserializer: Deserializer)` — bound dispatch of plain trait methods is
> proven. A codec constructs the record once per encode/decode (closures capturing its
> state); the cost is dynamic calls through the record, not intermediate allocations.
> When either compiler gap closes, the records become traits and monomorphize to zero
> cost — signature-compatible for derived code either way. Also settled: the
> deserializer, too, takes `begin_variant(name, arity)` (JSON wraps arity>1 payloads in
> an array), plus `null_value()` so `Option::None` is consumed, not just peeked.

The trait-shaped target (post-gap):

```vilan
// std::wire — the codec-neutral vocabulary (base layer).
trait Wire {
	fun describe<S: Serializer>(self, serializer: S);
	fun rebuild<D: Deserializer>(deserializer: D): Wire;   // static, like FromJson
}

trait Serializer {
	// Aggregates: a struct is `begin_struct(n)`, then per field
	// `field(name)` + the value's own describe, then `end_struct`. A list is
	// `begin_list(n)` + elements; an enum variant `begin_variant(name, arity)` +
	// payloads (externally tagged — today's JSON shape). `Option::None` is
	// `null()`; `Some` describes its value bare (JSON compat).
	fun begin_struct(self, fields: i32);
	fun field(self, name: str);
	fun end_struct(self);
	fun begin_list(self, length: i32);
	fun end_list(self);
	fun begin_variant(self, name: str, arity: i32);
	fun end_variant(self);
	fun null(self);
	fun str_value(self, value: str);
	fun i32_value(self, value: i32);
	fun u32_value(self, value: u32);
	fun f64_value(self, value: f64);
	fun bool_value(self, value: bool);
}

trait Deserializer {
	// The mirror, pull-based. `field(name)` positions the cursor: a JSON
	// deserializer looks the name up (order-independent, self-describing); a
	// binary one advances positionally and ignores the name — the shared Wire
	// type IS the schema (§6's compact-format note). `variant_tag()` reads the
	// enum discriminator for the rebuild's match; `begin_list` returns the
	// element count; `is_null()` distinguishes `None` before a value read.
	fun begin_struct(self);
	fun field(self, name: str);
	fun end_struct(self);
	fun begin_list(self): i32;
	fun end_list(self);
	fun variant_tag(self): str;
	fun begin_variant(self, name: str);
	fun end_variant(self);
	fun is_null(self): bool;
	fun str_value(self): str;
	fun i32_value(self): i32;
	fun u32_value(self): u32;
	fun f64_value(self): f64;
	fun bool_value(self): bool;
	// The sticky error (below).
	fun fail(self, reason: str);
	fun failed(self): Option<str>;
}
```

- **Errors are sticky, not thrown** (the I3 design, absent `?`/try — Q10): a missing
  field, wrong-shaped value, or unknown variant calls `fail(reason)` once; every
  subsequent value read returns a zero value without side effects, so the generated
  rebuild stays linear straight-line code (no per-read `Result` matching). The
  top-level `decode` checks `failed()` at the end and returns
  `Err(RpcError::Decode(reason))` — the first failure, named precisely (field/type).
  A poisoned deserializer never half-succeeds: the decode result is discarded.
- **Scalars, `List`, `Option`** get hand-written `Wire` impls in `std::wire`,
  mirroring `std::json`'s. `JsonSerializer`/`JsonDeserializer` live in `std::json`
  (over its existing `JsonValue` infrastructure); the binary pair comes with the
  codec slice, writing/reading `std::bytes` `Bytes`.
- **The derive retarget is additive**: `[derive(Wire)]` emits `describe`/`rebuild`
  impls ALONGSIDE today's `to_json`/`from_json` (everything shipped stays green);
  the codec slice then re-plumbs the RPC runtime onto `Codec`, and the JSON pair
  becomes one codec among two. `[derive(Json)]` is untouched throughout.
- **Order of work**: hand-written proof first (std::wire + the JSON pair + tests
  over hand impls), derive retarget second, codec third — prove before generating.

### 6.2 The codec, concretely (settled 2026-07-02)

The frame and the codec value (both in `std::wire`; the compiler gaps shape the codec
as a record factory, like the serializer records themselves):

```vilan
// What a transport moves. JSON rides text transports allocation-free (SSE is
// text-only, so SplitDuplex's server→client leg REQUIRES this arm); binary
// rides byte-capable ones (HTTP POST bodies today, WebSocket later).
enum Frame {
	Text(str),
	Binary(Bytes),
}

// A codec is a factory of encoder/decoder records: `writer()` yields a fresh
// Serializer plus the finisher that produces the frame; `reader(frame)` yields
// the Deserializer a value rebuilds from (handed a frame of the wrong kind, it
// arrives pre-poisoned — a sticky decode error, not a crash).
struct Codec {
	writer: || (Serializer, || Frame),
	reader: |Frame| Deserializer,
}

fun encode<T: Wire>(codec: Codec, value: T): Frame;             // describe + finish
fun decode<T: Wire>(codec: Codec, frame: Frame): Result<T, str>; // rebuild + failed()
```

`std::json::json_codec()` wraps the existing `JsonWriter`/`JsonReader`.
`std::binary::binary_codec()` is the compact pair over `std::bytes` —
**schema-ordered and length-prefixed**: the shared Wire type is the schema, so
structs write no field names or counts and lists write a `u32` count then bare
elements. Little-endian throughout:

| value            | encoding                                                      |
| ---------------- | ------------------------------------------------------------- |
| `i32` / `u32`    | 4 bytes LE                                                    |
| `f64`            | 8 bytes IEEE-754 LE (a `DataView` extern joins `std::bytes`)  |
| `bool`           | 1 byte (0/1)                                                  |
| `str`            | `u32` byte length + UTF-8 bytes                               |
| `List`           | `u32` count + elements                                        |
| struct           | fields in declaration order, nothing else                     |
| enum variant     | tag as a `str` (length-prefixed name) + payloads in order     |
| `Option`         | 1 marker byte: `0x00` = None, `0x01` + value = Some           |

The variant tag stays the *name* for v1 (robust to reordering, debuggable); a
numeric-index compaction is the same later step as method-name→id (§6). A
truncated frame fails sticky (`unexpected end of frame`) — the validating
decode covers hostile input in both formats.

The `Option` marker forced one visitor addition: `Serializer.some_value()`,
called by `Option::describe` before a present value. JSON's writer no-ops it
(a bare value, exactly today's format — which also keeps JSON's pre-existing
`Some(None)` ≡ `None` collapse, a property of the format, not the visitor);
binary writes the `0x01`. Without it, `Some(0)` and `None` would both start
`0x00` — schema-ordered bytes have no self-description to disambiguate with.

**The runtime re-plumb ✅ shipped (2026-07-02, single-pass — §4.1)**: `Transport`
moves `Frame` (HTTP POSTs text or bytes and reads the reply in kind); the
envelope is written in one pass (request args describe into the envelope's
serializer; the reply is `{"Success":<value>}` — measured overhead fell from
~15% to ~0.2%, 27 bytes of framing on a 14 KB payload); `RpcRequest` is a
deserializer handle, `arg` pulls positionally, `decode_failed` gates generated
impls (a garbled request is `RpcError::Decode`, pinned — the JSON reader also
fails sticky on document underflow now); the codec is chosen at wiring time on
both sides (`Client { transport, codec }`, `into_protocol(codec)`), and binary
RPC runs end-to-end over real HTTP via `serve_connected`'s byte-reading `/rpc`
(the JSON codec reads binary frames as UTF-8, so byte mounts need no
sniffing). Benchmarks now bracket both codecs live (~855 binary vs ~778 JSON
calls/sec over localhost; half the bytes on the wire). Known bounds:
`rpc_response`/`serve_rpc` ride the text `Server` API and serve text codecs
only (binary belongs on `serve_connected`); the reactive protocol stays
JSON-over-text until the WebSocket slice. Format choice is deployment-wide
(both sides must agree — the Q6 contract-hash/negotiation concern).

## 7. The generated stub: async and errors

The client requestor generated from the `[service(Client)]` struct (§4.2) *is* the seamless call —
`accounts.get_user(42)` reads like a method call. Sketched:

```vilan
// generated client requestor — a *sibling* type, not an impl of the service struct
// (its return carries the extra `Result` layer; §4.2). One method shown.
fun get_user(self, id: i32): Result<Option<WireUser>, RpcError> {
	let request = encode_request(self.codec, "get_user", [self.codec.encode(id)]);
	let reply = await (self.transport).call(request);     // round-trip
	decode_reply(self.codec, reply)                       // Result<Option<WireUser>, RpcError>
}
```

- **Async is seamless and honest.** The stub `await`s the transport, so it is async and a
  caller auto-awaits it — including when the transport is reached through a trait bound,
  since effect-polymorphic async now propagates through an indirect dispatch (no `dyn`, so
  every instance resolves to a statically-known impl; ✅ shipped). Latency stays *visible* as
  an `await`: the stub reads like a method call, not like a free local one — the RPC fallacy
  avoided.
- **The `T` → `Result<T, _>` shift is the contract's, and the generator owns it (Q3,
  settled).** The `[service]` method declares the *logical* signature — `get_user(id):
  Option<WireUser>` — and the server `impl` returns exactly that, a clean local body. The
  round-trip can fail, so the **generated client stub wraps the return in
  `Result<_, RpcError>`** — the developer never writes the wrapping. `RpcError` is a derived
  enum: `Transport(str) | Decode(str) | Remote(str) | Unauthorized`. The two sides differ by
  exactly one `Result` layer, applied by codegen, not by hand: the honest client without the
  noisy server.

## 8. The reactive north star — a second protocol (the capstone)

> **SHIPPED ON THE CODEC (2026-07-03, follow-up #5).** The section below described the
> protocol before the codec existed; the built runtime kept its shape (capability table,
> channel ids, subscribe/update/unsubscribe) and moved everything JSON-shaped onto §6.2:
>
> - **`DuplexTransport` carries `Frame`**, not `str`. `SplitDuplex` stays text-only (its
>   server→client leg is SSE): sending a binary frame through it **panics** client-side —
>   a loud wiring error the moment a binary codec first subscribes — and the server's SSE
>   leg drops binary defensively. `SocketDuplex` carries both: WS *text* messages keep the
>   `d:`/`r:<id>:` prefixes; WS *binary* messages carry a 1-byte channel tag (`0x64` 'd' =
>   duplex frame, `0x72` 'r' + 4-byte LE request id = RPC) — which also removes
>   `SocketTransport`'s binary panic: **binary RPC rides the socket**.
> - **The reactive envelopes are single-pass over the codec** (`encode_update` writes
>   `Update{channel, payload}` with the payload *described inline* — the last
>   double-encoding, gone). The `ReactiveFrame` derive type and the per-source JSON
>   mirror `Signal<str>`s are deleted. `expose<T: Wire>` now stores a **starter** per
>   channel — a closure that subs the *typed* source on the client's first Subscribe —
>   so an unsubscribed exposed source retains nothing at all.
> - **Mirrors are typed end to end**: `source<T: Wire>(channel)` returns a
>   `RemoteSource<T>` (`cache: Signal<Option<T>>`, `get(): Option<T>`, `sub(|T| void)`) —
>   `T` binds from the annotated `let` at the call site; the generated client emits
>   `RemoteSource<Element>` from the `[expose]`d field's `Signal<Element>` type, and app
>   code subscribes to *values*, not JSON (`client.todos.sub(|list| …)`). `RemoteSource`
>   no longer implements `Source<str>`; the `Option` replaces the `""` sentinel. A
>   malformed update is dropped (sticky decode error checked per frame), never delivered.
> - `ReactiveServer::new(wire, codec)` / `ReactiveClient::new(wire, codec)`: the codec is
>   chosen at wiring time like RPC's; `register_session` threads the `RpcProtocol`'s, so
>   `serve_service` keeps its signature. The vestigial `Protocol` trait (nothing consumed
>   it) is retired.

A `Signal`/`Source` is **not data** — it is a *capability*: a live reference to server state
plus an ongoing event stream. So it does not ride the Wire/codec model as a value. It is the
concern of a **second protocol**, sibling to RPC, that shares the same pure codec but requires
a **duplex** transport (§5):

```vilan
struct ReactiveProtocol<Tx: DuplexTransport, Cx: Codec> {
	transport: Tx,   // moves frames both ways (a WebSocket, or a `SplitDuplex`)
	codec: Cx,       // the *same* pure Wire codec RPC uses
	// the capability table: exported/imported `Source`s by channel id, and live subscriptions
}

// client code only ever sees a `Source<T>`; the protocol makes a *remote* one behave locally
let reactive = ReactiveProtocol { transport = socket, codec = codec };
let count: Source<i32> = reactive.source(handle);   // `handle` arrived over the wire (below)
let _ = count.sub(|n| print(i"count = {n}"));        // subscribes over the socket
```

**How a capability crosses — the Cap'n Proto capability-table pattern.** A `Source<T>` never
serializes as a value. Where a reply (or a `to_wire` projection) contains one, the reactive
protocol *exports* it into a per-connection table and puts a plain-Wire **`ChannelId`** on the
wire in its place; the receiving side *imports* that id into a `RemoteSource<T>` bound to its
protocol. So the three worries dissolve, each landing in the right layer:

- the **handle** is a `ChannelId` — a Wire id in the capability table, nothing more, so the
  codec only ever sees an integer;
- the **update payloads** are plain Wire `T` values — the codec encodes/decodes those exactly
  like any other value;
- **subscribe / update / unsubscribe** are frames the *protocol* sends over the duplex
  transport: `sub` sends a subscribe frame for the id, the server forwards its signal's updates
  as encoded-`T` frames, and `dispose()` (the existing `Disposable`/`Owner` machinery) sends an
  unsubscribe.

None of that touches the codec (pure) or the transport (a dumb pipe): the signal semantics live
in exactly one place, `ReactiveProtocol`. And because it is bound `Tx: DuplexTransport`, a
reactive protocol over a plain `HttpTransport` is a **compile error** — you cannot claim a
subscription works where the transport can't push. (A `Source` is therefore "Wire" only
*through* a reactive protocol that supplies the table, so a payload carrying one must ride the
reactive protocol, never plain RPC — the honest constraint.)

The same export/import-by-id pattern is how *any* live reference would cross — a remote object,
an arena `Handle`, a callback — so the capability table is worth designing generically even if
`Source` is the first, and at first only, capability.

The pieces this needs, all in the reactive phase:

1. **A `Source`/`Signal` split in `std::reactive`** — a read-only `Source<T>` (`get`/`sub`/`map`)
   that `Signal<T>` implements (adding `set`/`set_with`), so the remote handle implements
   `Source` and client code can't write a server signal. (The reactive README designs the API
   for this; it also intersects the signal-batching revision drafted separately.)
2. **A `DuplexTransport`** (WebSocket, §5) — plus its `SplitDuplex` fallback (SSE + POST) for
   WebSocket-less environments.
3. **The `ReactiveProtocol` + capability table** — export/import of `Source`s by id, the
   subscribe/update/unsubscribe frame protocol, and the connection-scoped lifecycle: exported
   sources reclaimed when the connection drops or the client `Owner` disposes — a natural fit
   for the existing `Owner` scopes.

## 9. Sessions, handles, and the other direction

> **Added 2026-09-08 (Order 30, lane rpc-paper-30).** This section is new and sits
> where it belongs — directly after §8, whose capability table it finishes. The five
> sections that followed §8 shift by one: former §9–§13 are now §10–§14 (the
> externally-cited phased plan is §12, marked *(was §11)* at its heading).
>
> It folds four tracker items into one design — **A53** (a generic source field),
> **A54** (a `Delta`-producing cell), **A55** (the mirror seams), **A56** (two rpc
> rulings) — on the owner's instruction of 2026-09-07, and answers the three points
> of their sketch below. It is a DESIGN section: §9.1 is verified against the tree
> today, §9.2–§9.4 are unbuilt, and §9.5 is the ruling list.

The owner's sketch, 2026-09-07 — the exhibit this section is written against:

```vilan
[service_server(MyClientService)]
struct MyServerService { is_authenticated: bool }   // per connection
impl MyServerService {
	[rpc] fun login(&mut self, username: str, password: str) { … self.is_authenticated = true; … }
	[rpc] fun get_user(self, user_id: UserId): SignalCell<User> { … }   // client sees `RemoteSource<User>`
	[rpc] fun ping_requesting_client(self) { let client = get_client(); client.ping(); }   // context api
}
[service_client] struct MyClientService {}
impl MyClientService { [rpc] fun ping(self) { print("ping from the server"); } }
```

Their three points, in their words: (1) `[expose]` may be the wrong primitive — an rpc
function returning a signal HANDLE is more versatile, because kolt's
`get_messages(conversation, amount): List<MessageId>` plus
`get_message(id): SignalCell<MessageBody>` lets the client subscribe only to what is on
screen; (2) the struct is instantiated per client connection; (3) there must be a way to
call functions declared on the client. And the mechanism they name: "Signal handles will
need tracking (arena?); the client just sees the handle and a server subscription is only
triggered once the client maps the handle to a local Signal."

Point (2) is built (§9.1 — with one hole). Point (1) is §8's unbuilt half, and §9.2
designs it to the end. Point (3) is §9.3. The arena they ask for already exists: it is
§8's per-connection **capability table** (`ReactiveServer.sources`, `std/src/rpc.vl:1391`),
and the disconnect that drops it whole is the arena's free.

### 9.1 Per-connection MUTABLE state — built, with one hole (VERIFIED)

The per-connection instance shipped in Order 27 as A38 (`archive.md:360`):
`Service::factory(build: |Connection| S, codec)` (`std/src/process/rpc_server.vl:491`)
calls `build` once per connection and hands the instance to
`build(connection).dispatcher_for().into_protocol(codec)` — so every route in that
connection's `Dispatcher` closes over THAT instance and no other. `Connection { id,
session, remote_addr }` (`rpc_server.vl:112`) carries what `authorize`
(`rpc_server.vl:562`) proved at the handshake, so the constructor can read the identity.
kolt has used it since 2026-09-07 (`kolt/src/store.vl:94`: `[service(KoltClient)] struct
KoltStore { user: str, … }`), and the pin
`a_factory_service_builds_one_instance_per_connection`
(`crates/vilan-cli/tests/service_layer.rs:864`) holds the shape.

What the sketch asks for on top is the plain-field mutation:
`[rpc] fun login(&mut self, …) { self.is_authenticated = true; }`. **This lane verified
it against the tree, and it does not work.** The pin
`a_mut_self_rpc_mutation_is_lost_where_a_shared_field_survives`
(`crates/vilan-cli/tests/service_layer.rs`, added by this lane) records both halves:

- **`&mut self` on an `[rpc]` method is REFUSED at expansion.** The generated dispatcher
  is `fun dispatcher(self)` (`std/src/rpc.vl:3249` — `fun_of("dispatcher").parameter("self")`)
  and each route calls `self.{method}(…)` from a closure that captured that `self`
  (`rpc.vl:3188`, `rpc.vl:3193`). Calling a `&mut self` method on it needs a mutable
  receiver the generated function does not declare, so the build stops with:

  ```text
  Error: in code generated by this attribute: cannot mutate immutable 'self'; declare it
  `mut self` to mutate this function's copy, or `&mut self` to mutate the caller's value.
  ```

  The span is the **struct** (the `[service]` attribute), not the method, and the remedy
  it offers is the receiver the author already wrote. Filed by this lane as a B item; not
  fixed here.

- **`mut self` compiles and silently loses the mutation.** It is the receiver the macro
  admits. The handler mutates its own copy — `login` returns `true` — and the instance
  the dispatcher holds is untouched, so the very next call on the SAME connection reads
  the old value. Measured:

  ```text
  a-before:conn-0/plain:false/held:false
  a-login-plain:true       ← the handler's copy saw it
  a-login-held:true
  a-after:conn-0/plain:false/held:true    ← `plain` did not survive the call
  b-after:conn-1/plain:false/held:false   ← and the second connection is untouched, as designed
  ```

- **The spelling that works is a `Shared`/`Signal` field**, which is exactly what Q9's
  "Mutable session state" sub-ruling (§14) already predicted for the async case:
  `held: Shared<bool>`, written `self.held.write() = true`. Per-connection, persistent
  across calls, invisible to the other connection.

**Decision.** Per-connection mutable state is BUILT and the sketch's `is_authenticated`
works today — spelled `Shared<bool>`, not `bool`. The gap is ergonomic and diagnostic,
not structural: Q9 ruled `&mut self` "the idiomatic in-place receiver" for sync state,
and the generator does not honour it. Two ways to close it, and the paper prefers the
first: (a) the generator emits `fun dispatcher(&mut self)` and per-route mutable
re-borrows when any `[rpc]` method takes `&mut self`, which is what Q9's ruling
described; or (b) the attribute REFUSES `&mut self` in its own vocabulary — "an `[rpc]`
method cannot take `&mut self`; hold mutable session state in a `Shared<T>` field" — and
Q9's ruling is amended to say so. What must not stand is today's third state: `mut self`
compiling and losing the write with no diagnostic at all. **Open for the owner: R-A38b in
§9.5.**

### 9.2 Return-typed signal handles — §8's unbuilt half, designed

§8 built the capability table and the `ChannelId` on the wire, but only ever exports a
source that a `[expose]`d FIELD named at compile time. The other half — "where a reply
contains one, the reactive protocol *exports* it into a per-connection table and puts a
plain-Wire `ChannelId` on the wire in its place" — was never built. This is that half,
and it is the owner's point (1).

**The mapping rule.** A `[rpc]` method whose RETURN type is a source becomes a stub
whose return type is the corresponding mirror:

| server writes | client stub returns |
| --- | --- |
| `SignalCell<T>` / any `S: Source<T>` | `Result<RemoteSource<T>, RpcError>` |
| `KeyedCell<K, T>` (A54) | `Result<KeyedSource<K, T>, RpcError>` |
| `Option<SignalCell<T>>` | `Result<Option<RemoteSource<T>>, RpcError>` |

The generator already renders return types into the stub and into the contract surface
(`rpc.vl:3145` — `surface + ")->" + method.return_type.render()`; `rpc.vl:3302` — the
stub's `.returns(i"Result<{…render()}, RpcError>")`), so the mapping is one rewrite in
both places. **The contract hash covers the MAPPED types**: the surface entry for
`get_message(MessageId) -> SignalCell<MessageBody>` is written
`get_message(MessageId)->RemoteSource<MessageBody>;`, so a server that changes a handle
return to a plain value moves the hash and a stale client is refused before it can decode
a `ChannelId` as a `MessageBody`. That is the honest direction: the hash names what the
CLIENT will see, because the client is who it protects.

**On the wire the reply carries a plain-Wire `ChannelId`** — an `i32` today
(`fresh_channel`, and `impl i32 with Wire` at `std/src/wire.vl:287`), so the codec sees an
integer and nothing else, exactly as §8 designed. The export happens inside `reply(…)`'s
turn: the outcome encoder asks the connection's `ReactiveServer` for a channel
(`ReactiveServer::expose`, `rpc.vl:1415`), which pushes a `(channel, Capability{start,
resolve})` pair onto `self.sources` and returns the id. **That table IS the arena the
owner asks for**, and it is per-connection by construction: `accept_socket` builds one
`ReactiveServer` per socket (`register_session`, `rpc_server.vl:497`) and
`drop_session` drops it on disconnect (`rpc_server.vl:498`), so a dropped connection
frees every handle it ever minted in one act. No separate arena, no ids that outlive
their connection, no cross-connection handle confusion.

**The mirror is lazy, and that is the shipped lease semantics, not a new rule.**
`ReactiveServer::expose` stores a *starter* closure and subscribes nothing
(`rpc.vl:1389-1390`: "Nothing subscribes — or is retained — until a client asks"), and
the client's `RemoteSource` sends `Subscribe` only on the 0→1 lease
(`RemoteSource::acquire`, `rpc.vl:2338`) and defers `Unsubscribe` at 1→0 to the turn's
settle (`release`, `rpc.vl:2354`). So the owner's "a server subscription is only
triggered once the client maps the handle to a local Signal" is already true of every
mirror this runtime mints: a client that calls `get_messages` for a hundred ids and
`get_message` for each of them, but renders ten, holds ten forwards. `remote-sources.md`
is the paper for that rule and nothing here changes it.

**The mirror remembers the call that minted it.** `RemoteSource` gains one field — the
minting call: `origin: Option<(str, List<|Serializer| void>)>`, the method name and the
argument describers, which is exactly the pair `call` already takes
(`rpc.vl:1101-1106`). This is what makes a dynamic handle REBINDABLE and retires A41's
refuse-clearly branch. Today `reattach_mirrors` (`rpc.vl:2878`) rebinds only the
generated field mirrors, positionally, from the fresh `__attach` reply, and a handle an
application method minted is set to `Waiting` and abandoned (`invalidate_dynamic`,
`rpc.vl:2049-2058`) because "the fresh session never minted it, and no protocol form exists
yet to ask for it again". With `origin` the protocol form exists: after the contract
re-verify and the positional `__attach` rebind, `reattach_mirrors` re-issues each
watched dynamic mirror's own call and rebinds it to the channel the fresh reply names.
`invalidate_dynamic` and `invalidate_on_reconnect` (`rpc.vl:2854`) stay as the escape
for a hand-wired mirror with no origin, and stop being the only answer.

Two consequences to state out loud. **Replay re-runs a server method**, so only a method
the macro can see is a minting getter is eligible, and even then "getter" is the author's
claim, not the compiler's — see R7. And **only WATCHED mirrors are replayed**
(`count > 0`, the test `rebind` already applies at `rpc.vl:2384`): a handle the client
holds but never subscribed to costs one call it does not need.

**`Release(channel)` — the frame the dynamic path needs.** Lease-zero sends
`Unsubscribe`, and `Unsubscribe` deliberately does NOT drop the capability: A41 recorded
that dropping the `sources` entry on unsubscribe made every remount silently dead
(`rpc.vl:1565-1573`), because an `Unsubscribe` is client-local demand hitting zero and
`acquire` re-subscribes on the same id when a view remounts. Withdrawal is its own verb,
`ReactiveServer::revoke` (`rpc.vl:1612`), and today only the app can call it. A dynamic
mirror needs the client to be able to say it: when a mirror minted by a call reaches zero
leases AND is disposed — the handle itself dropped, not merely unwatched — it sends
`Release(channel)`, and the server runs `revoke`, stopping every forward and dropping the
capability so the starter closure and the source it captured are released. Without this,
a long session scrolling ten thousand messages retains ten thousand capabilities until
the socket closes, which is precisely the leak `revoke`'s doc comment describes
(`rpc.vl:1599-1610`). **`[expose]`d field mirrors never send `Release`** — they are minted
once per connection and must survive a remount — so the frame is emitted only by a
mirror carrying an `origin`. That is the one behavioural difference between the two kinds
of mirror, and it is exactly the difference A41 identified.

**`[expose]` becomes sugar.** `[expose] tasks: SignalCell<List<Task>>` is
`[rpc] fun tasks(self): SignalCell<List<Task>>` whose mirror the generated client holds
as a FIELD, minted once at `connect` and rebound positionally on reconnect — which is
what `__attach` does today (`rpc.vl:3355-3362`). Nothing about the field path changes;
it is re-described in terms of the general mechanism. **The one thing that must not
follow is the hash.** The exposure surface entry is its own shape today
(`expose:{name}:{element};` at `rpc.vl:3161`, deliberately so — A39 kept the plain form
byte-identical), and desugaring it into `tasks()->RemoteSource<List<Task>>;` would move
every existing service's contract hash for no semantic change. Keep the `expose:` entry.
**R2 in §9.5.**

**A53 — the generic source field stops mattering.** A53 stopped because
`[expose] items: SignalCell<T>` on a generic `Store<type T>` cannot work: `ServiceItem`
carries no generics, and the contract hash is built from WRITTEN types, so every
instantiation hashes identically and a `Store<Task>` client would connect to a
`Store<Note>` server (`items/A53.md`; `archive.md:506`). The return-typed handle answers
the motivating case without touching that: `fun items(self): SignalCell<Task>` writes the
element type in the METHOD SIGNATURE, where the hash already reads it
(`rpc.vl:3145`) and where the stub already renders it (`rpc.vl:3302`). A service that
wants two element types writes two methods, and they hash differently. The residual —
`[service]` on a *generic struct* — is unchanged and unwanted: it remains refused, and
A53 closes as **answered by §9.2, not built**, with the refusal standing (the diagnostic
is already there).

**A55 — the two mirror seams.** (i) `KeyedSource` is still not a `Source`; A52 gave
`RemoteSource` the impl (`impl RemoteSource<type T> with Source<Option<T>>`,
`rpc.vl:2184`) and left the keyed twin bare. Under §9.2 a keyed handle is a first-class
return type, so the impl is required, not optional:
`impl KeyedSource<type K, type T> with Source<Option<List<T>>>`, on the same counted
lease (`acquire`/`release` at `rpc.vl:2562`/`rpc.vl:2581`) — no second mechanism, exactly
as `RemoteSource`'s impl comment argues. (ii) The `or([])` seam: a
`RemoteSource<List<T>>` is a `Source<Option<List<T>>>`, so `bind_each` takes `or([])`.
**Answer: no sibling.** `or([])` is the binding SAYING what an unseeded list renders as,
and a `Source<Option<List<T>>>` overload of `bind_each` would either invent `[]` silently
or need the same argument under another name. The `Option` is the truth — a mirror has
not been told anything yet — and one character of ceremony per list binding is the right
price for it. A55 closes with the impl to build and the sibling declined. **The impl is
work; the seam is a ruling (R5).**

**A56 — both questions land here.** (i) The keyed-Map key mismatch. Today
`[expose(keyed = K)]` over a `SignalCell<Map<K2, V>>` silently prefers the WRITTEN
argument over the map's own key type (`rpc.vl:3093-3098`: "A written argument wins: it is
what the author said the key is"), and the disagreement surfaces later as a plain type
error at the mirror, in generated code the author never wrote. **Answer: refuse at the
attribute.** The macro has both types in hand at `rpc.vl:3086-3098` and can say so in the
field's own vocabulary — one new ledger row — which is the same standard `check_expose_fields`
already meets for a non-source field (B202, `rpc.vl:3050-3070`). Under §9.2 this refusal
is *more* load-bearing, not less: a keyed handle in a return position names `K` in the
written type, so the two spellings must agree on what a key is. (ii) `authorize_timeout`
answering 429. A48 chose 429 because a timeout "is a limit, not a judgement"
(`archive.md:446`), and A52 then landed `Reject::Unavailable` → 503 for the app's OWN
refusal, with the eligibility rule stated as `tells_the_client` = did the APP decide
(`archive.md:506`). **Answer: keep 429, and it is now well-founded rather than merely
chosen** — 503 is reserved for a judgement the app made, and std timing out the app's
verifier is std's limit, not the app's judgement. The distinction A52 built is exactly
the one that keeps 429 correct. Say so on A48's tombstone and close A56. **R6 records
it for the owner's signature.**

**What A54 has to be for this to pay.** The keyed handle is only worth returning if a
keyed channel is cheap per change, and today it is not: `keyed_diff` re-keys two
snapshots and `KeyedSource::apply` reaches `index_of` per op, both O(N) — 1.08 ms per
change per connection at 1,000 rows and 8.83 ms at 10,000 (`items/A54.md`;
`archive.md:508`). That is irreducible while the source is `List`-valued, because only
the MUTATION knows what changed. A54's `KeyedCell<K, T>` — `insert`/`remove`/`update(key)`
producing `Delta<K, T>` ops directly — is therefore a PREREQUISITE of the keyed half of
§9.2, not a parallel nicety, and its mapped return type (`KeyedCell<K, T>` →
`KeyedSource<K, T>`) is the row in the table above. The plain `SignalCell<T>` half of
§9.2 has no such dependency and can ship first.

### 9.3 Client-declared functions — the other direction

The owner's point (3). Three pieces: a dispatcher on the client, a `call` on the server's
end of the connection, and a way for a handler to reach its caller.

**The client-side dispatcher is the existing one.** `Dispatcher` (`rpc.vl:1167`),
`RpcProtocol::respond` (`rpc.vl:1067`) and the whole `arg`/`reply`/`decode_failed`
foundation are direction-agnostic — nothing in them knows which side of a socket they sit
on. A struct with `[rpc]` methods on the client generates the same `dispatcher()` and the
same `contract_hash()`; what changes is only who mounts it. So the client half is
generation, not runtime.

**The server side needs a `call`, and `DuplexEnd` has none.** `DuplexEnd`
(`rpc.vl:124`) declares `send` and `on_frame` and nothing else — it is a dumb frame pipe
with no correlation. Correlation lives one layer up, in `SocketDuplex.pending:
Shared<List<PendingCall>>` (`rpc.vl:478`) and `settle_pending` (`rpc.vl:538`), and only
on the client. The server end must grow the same two: a pending table and a
`fresh_id()`-minted request id per outgoing call.

**How the router tells a request from a reply, in each direction.** Today it does not
have to, because each side plays exactly one role, and this is the fact the design must
respect:

| lane | today's meaning at the client | today's meaning at the server |
| --- | --- | --- |
| text `r:<id>:<payload>` | a REPLY → `settle_pending` (`rpc.vl:634-648`) | a REQUEST → `protocol.respond` (`rpc_server.vl:1119-1140`) |
| text `d:<payload>` | a reactive frame → the duplex handler (`rpc.vl:649`) | a reactive frame → `wire_end.send` (`rpc_server.vl:1144-1150`) |
| binary `0x72` + 4-byte LE id | a REPLY (`rpc.vl:661-666`) | a REQUEST (`rpc_server.vl:1155-1175`) |
| binary `0x64` | a reactive frame | a reactive frame |

The `r:` lane's id namespace belongs to the client. Reusing it for server→client calls
would collide two `fresh_id()` counters and make `r:7:` ambiguous on both ends.
**The design adds one lane, not one flag**: text `s:<id>:<payload>` and binary tag
`0x73` ('s'), carrying requests minted by the SERVER and their replies, in the server's
own id namespace. Then each side reads the prefix and knows its role without a direction
bit: `r:` → the client settles, the server dispatches; `s:` → the server settles, the
client dispatches. Both routers already ignore unknown prefixes and unknown tags for
forward compatibility (`rpc.vl:632`, `rpc.vl:654`), so an old client meeting a new server
DROPS `s:` frames silently — which means the server's call never settles. That is the
one compatibility hazard, and it is answered by the contract hash: a client whose
handler struct the server does not know about hashes differently, and the connection is
refused before any `s:` frame is sent.

**The proxy is typed and reaches the handler through `Connection`, not through ambient
context.** The factory already hands the constructor a `Connection`
(`rpc_server.vl:112`), which is where per-connection facts belong and where the identity
already lives. It gains one member, typed by the attribute:

```vilan
[service(KoltClient, client = KoltHandlers)]
struct KoltStore { user: str, client: KoltHandlersProxy }

Service::factory(|connection: Connection| KoltStore {
	user = connection.session.identity,
	client = connection.client(),          // typed `KoltHandlersProxy` — the attribute says so
}, json_codec())
```

`connection.client()` is generic over the handler type the attribute named, so the
service struct holds a typed proxy field and every method reaches it as `self.client`.
An ambient `get_client()` is the owner's spelling and it is genuinely nicer for a helper
five frames down a call stack — but it is *sugar over this*, not an alternative to it: a
`context` value the generated route establishes around each handler call, resolving to
the same proxy. Build the field first; add the context only if a real call stack asks for
it. Making the ambient form primary would put the connection in a dynamic variable when
the connection is already a value the factory holds, and would make a service whose
method is called from two connections silently correct-by-luck.

**Naming.** The paper recommends extending the shipped attribute rather than replacing
it:

- `[service(KoltClient)]` — unchanged, the generated client stub's name. Every existing
  service keeps compiling and keeps its hash.
- `[service(KoltClient, client = KoltHandlers)]` — the same, plus the name of the
  struct whose `[rpc]` methods this server may call.
- `[client_service] struct KoltHandlers {}` — on the handler struct, generating its
  dispatcher and the `KoltHandlersProxy` type the server's stub calls through.
- Both attributes on one struct is peer-to-peer, and needs no new spelling.

The owner's `[service_server(MyClientService)]` / `[service_client]` pair is the
alternative. It reads better in isolation — `server`/`client` say which side you are on,
where `service`/`client_service` says it once and by convention — but it renames the
shipped attribute, moves every existing service's diagnostics, and loses the property
that the *argument* is always "the type generated for the other side". **Recommendation:
keep `[service(…)]`, add `client = …` and `[client_service]`. R1.**

**Async coloring.** A server→client call is a wire round-trip, so its stub is
`async |…| Result<T, RpcError>` exactly like the client→server one, and `call`'s existing
body serves unchanged (`rpc.vl:1101`). Under vilan's effect polymorphism the caller
auto-awaits, so the handler that calls it becomes async — which the dispatcher already
supports: `Route.handler` is `async |RpcRequest| RpcOutcome` (`rpc.vl:1162`) and
`RpcProtocol.dispatch` is async (`rpc.vl:1063`). A `Task` is what a handler holds if it
wants to fire several client calls and join them; nothing new is needed for that.

**The reentrancy hazard, and it is real.** An `[rpc]` handler runs inside a turn:
`turn(FlushPolicy::AtEnd, || protocol.respond(…))` (`rpc_server.vl:1130`, and the binary
twin at `rpc_server.vl:1167`). `turn` with an AWAITING body "holds EVERY notification —
before the first suspension and in every continuation — until the body has fully
completed, then settles once" (`std/src/reactive.vl:203-207`). So a handler that awaits a
server→client call **holds its whole flush turn open for a network round-trip**: every
`Update` its own signal writes owe is queued behind the client's answer. A client handler
that calls back on the same connection therefore waits on a server whose turn is waiting
on it — and the only thing that saves it is that the router keeps dispatching.

Today the router *nearly* does. Frames arrive as chunks (`socket.on_bytes("data",
receive)`, `rpc_server.vl:1184`), and each chunk's events are handled in a loop:
`for event in parser.feed(chunk) { … turn(…, || protocol.respond(…)) … }`
(`rpc_server.vl:1117-1176`). Across chunks there is no problem — node calls `receive`
again whether or not the previous call's promise settled. **Within one chunk there is:**
the loop awaits the async `respond` before parsing the next event, so two frames that TCP
coalesced into one read are serialized. If handler #1 awaits a client call whose answer
arrives in that same read, it deadlocks — and on a fast local link coalescing is the
common case, not the rare one. This is a concrete, present-tree hazard, not a
speculative one.

What the turn/flush model must say, then, is three sentences:

1. **The router never blocks on a handler.** `receive` must dispatch every parsed event
   before awaiting any of them — parse the chunk into a list of events, start each
   handler, and let the event loop interleave. This is a change to `rpc_server.vl`'s
   receive loop and is a prerequisite of any awaited server→client call.
2. **A held turn is per handler, not per connection.** Two handlers in flight on one
   connection settle independently; `turn` already establishes a fresh turn per call
   (`reactive.vl:209`), and `batch` joins the ambient one (`reactive.vl:257`), which is
   the correct composition as long as the two handlers do not share a synchronous extent.
3. **An awaited server→client call is a suspension point in the wire turn, and the
   paper must say the reply is not atomic with it.** A handler that writes a signal,
   awaits a client call, and writes again publishes ONE wave at the end — which is the
   held turn's documented promise and is what an app wants — but it means a client that
   answers the call and then reads its own mirror sees the state from *before* the
   handler started. That is not a bug to fix; it is a sentence the guide owes.

**Fire-and-forget first.** A notification — `[rpc] fun ping(self)` with no return, called
as `self.client.ping()` and never awaited — needs no pending table, no correlation id, no
reply lane, and cannot deadlock or hold a turn. It is `s:` with the id field unused (or
simply a `d:`-adjacent one-way tag), and it covers the whole of the owner's exhibit
(`ping_requesting_client`) and most of what a server actually wants to say to a browser:
"your data moved", "you were signed out", "reload". **The cheap first form, and possibly
the only v1 form — R4.**

### 9.4 What this costs and what it retires

| today | under §9.2/§9.3 | status |
| --- | --- | --- |
| `[expose] f: SignalCell<T>` (`rpc.vl:3161`, `rpc.vl:3207`) | sugar for a zero-arg getter; mirror still a client field; **surface entry kept as `expose:`** so the hash does not move | kept, re-described |
| `[expose(keyed = K)]` (A51) | sugar for a getter returning `KeyedCell<K, T>` (A54) | kept, re-described |
| `ReactiveServer::expose_keyed` / `expose_keyed_map` / `expose_keyed_with` (`rpc.vl:1441`, `:1452`, `:1464`) | unchanged runtime; now also reached from a return position | kept |
| `ReactiveClient::attached_source` / `attached_keyed_source` (`rpc.vl:1952`, `:1987`) | unchanged — the field path | kept |
| `ReactiveClient::source(channel)` (`rpc.vl:1932`) — the hand-rolled runtime escape | subsumed: the generated stub mints the mirror with its `origin` | **retired** (kept as the hand-wired escape, no longer the only dynamic path) |
| `invalidate_dynamic` (`rpc.vl:2049-2058`) + `invalidate_on_reconnect` (`rpc.vl:2854`) | dynamic mirrors carry `origin` and are re-issued by `reattach_mirrors` | **retired for generated mirrors**; kept for origin-less hand-wired ones |
| the app calling `ReactiveServer::revoke` by hand (`rpc.vl:1612`) | driven by the client's `Release(channel)` at dispose | kept, now also client-driven |
| `RemoteSource` lease `Subscribe`/`Unsubscribe` (`rpc.vl:2338`, `:2354`) | unchanged | kept |
| — | `impl KeyedSource with Source<Option<List<T>>>` (A55) | **new** |
| — | `KeyedCell<K, T>` (A54) | **new, prerequisite of the keyed half** |
| `DuplexEnd { send, on_frame }` (`rpc.vl:124`) | plus a server-side pending table and `call` | **extended** |

**Wire frames added.** Two, and one lane:

- `Release(channel)` — client → server, on a dynamic mirror's dispose (distinct from
  `Unsubscribe`, which stays demand-only; A41's distinction, now expressible by the
  client).
- text `s:<id>:<payload>` / binary tag `0x73` — the reverse-direction RPC lane, in the
  server's own id namespace, replies included. `r:`/`d:`/`0x72`/`0x64` are untouched.

Nothing in the `Update`/`Patch`/`Subscribe`/`Unsubscribe` envelope set changes, so every
existing frame recording stays valid.

**The contract-hash change.** Three edits, and the paper is deliberate about which move
existing hashes:

1. A source in a return position renders as its MAPPED client type
   (`get_message(MessageId)->RemoteSource<MessageBody>;`) — new surface, no existing
   service affected, since no shipped service can return a source today.
2. The `expose:` entry is KEPT verbatim (`rpc.vl:3161`) — so every service that exists
   today hashes exactly as it does now. This is the reason `[expose]` stays as sugar
   rather than being desugared literally.
3. A `client = KoltHandlers` service appends the client surface to its own, e.g.
   `client:ping()->void;` — moving the hash of any service that declares one, which is
   correct: the two sides must agree on both directions, and no shipped service declares
   one.

**Migration for kolt's store** — the three TODOs, in the owner's own file:

- `store.vl:93`, on `KoltStore`: *"Consider how client functions can be called from the
  server for two-way communication."* → §9.3: `[service(KoltClient, client =
  KoltHandlers)]`, a `client: KoltHandlersProxy` field built from
  `connection.client()`, and `[client_service] struct KoltHandlers {}` in the browser
  entry. The first use is a notification (R4's cheap form): the store telling a
  connection that its session was revoked.
- `store.vl:102-109`, on `messages`: *"how a client would subscribe to only the messages in
  the current conversation and not the entire conversation … `get_messages(conversation,
  amount): List<MessageId>` and `get_message(message: MessageId): SignalCell<MessageBody>`
  … returning `RemoteSource<MessageBody>` … the client can get the last 100 message ids
  but only subscribe to the details for the ones on screen."* → §9.2 verbatim. Drop
  `[expose] messages: SignalCell<List<str>>` (`store.vl:111`), add the two methods, and
  the lease rule does the rest: a hundred handles, ten forwards.
- The third, at `store.vl:96-99` (*"Tasks are one list across workspaces (the client
  derives per-workspace views); per-entity channels are a later refinement"*) → also
  §9.2: `fun tasks_in(workspace: i32): KeyedCell<i32, Task>` is the per-entity channel,
  once A54 exists. Until then `[expose] tasks` stays and the client keeps deriving.

kolt's `workspaces`/`tasks` exposures keep working through the whole migration, because
`[expose]` is kept (item 2 above) and its hash does not move.

### 9.5 Rulings for the owner

**R1 — the attribute spelling.** Recommend `[service(KoltClient, client = KoltHandlers)]`
on the server struct and `[client_service]` on the handler struct, both attributes on one
struct for peer-to-peer. The alternative is the owner's
`[service_server(MyClientService)]` / `[service_client]`, which reads better in isolation
but renames the shipped attribute and moves every existing service's diagnostics. §9.3.
> **RULED 2026-09-09 (owner): as recommended.** Built by lane reverse-31 (Order 31).

**R2 — does `[expose]` stay?** Recommend YES, as sugar for a zero-argument getter, with
its `expose:` contract-surface entry kept verbatim so no shipped hash moves. The
alternative (delete it; write the getter) is one fewer concept but moves every existing
service's hash and costs kolt two rewrites for no behaviour change. §9.2, §9.4.
> **RULED 2026-09-09 (owner): YES.** Verified empirically by handles-31: a handle-free service hashes byte-identically (78bdada7 frozen at c3ed9239).

**R3 — the release policy.** Recommend EXPLICIT: `Unsubscribe` stays demand-only
(lease-zero, unchanged), and a new `Release(channel)` is sent when a mirror carrying an
`origin` is disposed. Lease-zero release alone is the alternative and it is wrong for the
same reason A41 recorded — a remount re-acquires on the same id, and a channel dropped at
lease-zero is silently dead. §9.2.
> **RULED 2026-09-09 (owner): REVERSED — demand decides; no `Release` frame.** Out of the owner's own SolidJS auto-dispose experience (the unmount-then-mount window inside one tick): lease-zero defers to the turn's settle and then one microtask look; an `Unsubscribe` on a DYNAMIC channel is a revoke; a re-acquire re-mints from the mirror's `origin` (the cached value stays as the seed); a never-leased handle goes with its ambient owner. The `origin` field closes A41's long-gap remount, which was this paper's reason for the frame. As built (handles-31), the hop is the ORIGIN-CARRYING mirror's only: applied to every mirror it reds four ratified A25 pins (`remote-sources.md` §2's promise that a close with no ambient turn goes now), and the keyed per-key lease got no hop — both open for the owner (§9.6).

**R4 — may a server→client call be awaited in v1, or notifications only?** Recommend
NOTIFICATIONS ONLY in v1: fire-and-forget needs no pending table, no reverse reply lane,
and cannot deadlock, and it covers the owner's exhibit and kolt's first use. Awaited
calls need §9.3's receive-loop change (the same-chunk serialization is a real deadlock
today) and a turn/flush sentence in the guide; both are v2 work with a red-first pin
available. §9.3.
> **RULED 2026-09-09 (owner): NOTIFICATIONS ONLY in v1; the receive-loop fix landed now (B281).** Awaited calls are A81.

**R5 — A55's `bind_each` sibling.** Recommend NO SIBLING: `or([])` is the binding saying
what an unseeded list renders as, and the `Option` is the truth about a mirror that has
not been told anything. `impl KeyedSource … with Source<Option<List<T>>>` IS to be built.
§9.2.
> **RULED 2026-09-09 (owner): NO SIBLING; the impl built** (keyed-31).

**R6 — A56's two.** (i) Recommend REFUSING a `[expose(keyed = K)]` whose argument
disagrees with the `Map`'s own key type, at the attribute, in the field's vocabulary —
one new ledger row; today the written argument silently wins (`rpc.vl:3093-3098`).
(ii) Recommend KEEPING 429 for `authorize_timeout`: 503 is the app's judgement
(`Reject::Unavailable`, A52) and a std timeout is std's limit, not the app's judgement.
Record on A48's tombstone and close A56. §9.2.
> **RULED 2026-09-09 (owner): as recommended** — the refusal at the attribute (ledger row 407) and 429 kept, both by rpc-smalls-31; the rationale was already at the site (A52's lane) and the ruling record joined it.

**R7 — replay idempotence (raised by this lane).** `reattach_mirrors` re-issuing a
mirror's `origin` call re-runs a server method after a reconnect. Recommend that the
handle return type IS the opt-in — a method returning a source is a getter by
declaration — with the sentence in the guide that such a method must be safe to re-run.
The alternative is an explicit `[rpc(replayable)]`, which is honest but adds an attribute
the author will forget. §9.2.
> **RULED 2026-09-09 (owner): the handle return type IS the opt-in;** the guide carries the must-be-safe-to-re-run sentence (handles-31).

**R-A38b — the `&mut self` hole (raised by this lane, §9.1).** `&mut self` on an `[rpc]`
method is refused with a diagnostic pointing at the struct and recommending the receiver
the author wrote; `mut self` compiles and silently loses the write. Recommend (a) the
generator honours `&mut self` as Q9 ruled, or failing that (b) the attribute refuses it
in its own vocabulary and Q9's ruling is amended. What must not stand is the silent loss.
Filed as a B item by this lane.
> **RULED 2026-09-09 (owner): option (a), plus `mut self` REFUSED on an `[rpc]` method** (B272, mutself-31, ledger row 408). The mechanism was smaller than (a) assumed — see §14 Q9's amendment.

### 9.6 As built — Order 31 (2026-09-09)

Five lanes built §9.1's hole, §9.2's plain half and §9.3's notification half; what
follows is where the tree deviates from the design above, so a reader of §9.2–§9.4
knows which sentences are now history.

- **§9.1 (B272).** The generated `dispatcher()` declares `mut self` and every route
  captures that BINDING (spec §6.9), so a `&mut self` method writes the connection's
  instance in place — no `Shared<S>` cell (built, measured, rejected: a copy per
  connection, C9's resource pin regressed, a reflection field it forced). `mut self` on
  an `[rpc]` method is refused at the attribute, span on the method.
- **§9.2 recognition is the WRITTEN spelling.** `SignalCell<T>` and
  `Option<SignalCell<T>>` only; the table's "any `S: Source<T>`" row is not
  implementable — the expansion runs before types resolve. A user `Source` type in a
  return position falls to the ordinary `[rpc]` Wire refusal; the element-Wire refusal
  is ledger row 411.
- **The export is the ROUTE's, not the outcome encoder's.** `reply_source(request, ..)`
  over `RpcProtocol.connection`, stamped by `Service::new`/`factory` at the upgrade and
  carried on the `RpcRequest`; `-1` on `local_rpc` and the connectionless POST leg is an
  honest runtime failure (A78 asks for the compile-time refusal).
- **`origin` is a struct** (`Origin { method, describers, reissue }`), not a pair: the
  mirror holds the reactive duplex, not the rpc transport, so the re-issue seam is a
  closure.
- **R3 as ruled, and the hop's scope.** `Capability.dynamic`; `Unsubscribe` on a dynamic
  channel runs `revoke` (`release_demand`; `stop` itself unchanged, so a hand
  `session.stop` keeps A41's meaning); `acquire` re-mints; `release_unleased` is the
  owner hook; `flush_close` hops one microtask — for origin-carrying mirrors only (see
  R3's note). **This order added ZERO wire frames**; reverse-31 added one LANE.
- **§9.3 without a pending table.** No `fresh_id`, no correlation, `DuplexEnd` UNTOUCHED
  (§9.4's "extended" row is wrong); the reverse channel is a per-connection registry in
  `std::rpc` fed by the socket layer. The proxy method is SYNC and void; the
  async-coloring paragraph is A81's. The `s:` id bytes (`0x73` + 4-byte LE 0) exist and
  are reserved. `connection.client()` is generic over a std trait (`ClientProxy`), `P`
  resolved from the field's declared type — a generated `Connection` member would
  collide across services. The handler instance rides `.with_handlers(instance)` on the
  CONNECTED client, which is what makes "refused before any `s:` frame" hold by
  construction (connect verifies the contract first), with an `early_serve` queue for a
  server that notifies at `on_connect`. The `client:` entries are a SUFFIX of the
  surface — what makes the byte-identical claim mechanical. Void `[rpc]` methods are
  legal only on a client-side struct; the handler must be a same-module sibling (v1).
- **A54's "irreducible" was the SERVER half's truth only.** The client half
  (`KeyedSource::apply` reaching `index_of` per op, a `SignalCell` copying on `get`/`set`)
  was reducible without changing the source type and is fixed. Carry the RATIO: for 10×
  rows the diff path costs 12.1×, the cell 1.32× (0.0078 → 0.0103 ms per change per
  connection). A bare `[expose]` over a `KeyedCell<K, T>` field is the direct spelling;
  `keyed = K` remains what a `SignalCell<List<T>>` needs. The cell drops `T: PartialEq`
  from the exposed element. `keyed_log_limit = 1024` → `Reset` on lag (open: per-cell?).
- **Deferred, tracked.** The keyed RETURN mapping (`KeyedCell` → `KeyedSource` in a reply)
  is A79 — unblocked by A54 and A74, unbuilt. Awaited server→client calls are A81. The
  interleave hazard the receive-loop fix opens for an awaiting `&mut self` handler is
  B287 (stated in the guide, unenforced).
- **Owner questions left by the lanes.** The hop on every mirror or dynamic-only; the
  keyed per-key hop; a curated refusal for a user `Source` return; `reattach_mirrors`'
  new `replay` parameter on a public std fn; same-module handler only; an awaitable ack
  for a void method's forward stub; the `__contract` route on a client-only struct;
  bare `[expose]` over a `KeyedCell` as the keyed channel (the type decides).
> **STANDING AS BUILT (Order 32's sweep, 2026-09-11) — not a ruling.** These eight were listed
> as record-only defaults in Order 32's briefs (P-list, `briefs32.md`), the owner said "adjust
> order or go" without objecting, and nothing in Order 32 moved them: the hop stays dynamic-only,
> the keyed per-key lease has no hop, `replay` stays on `reattach_mirrors`, handlers stay
> same-module, a void forward stub stays sync void, `__contract` stays on a client-only struct,
> bare `[expose]` over a `KeyedCell` is the keyed channel, `keyed_log_limit` stays 1024. The
> curated refusal for a user `Source` return is folded into the sync-stub question (P1). Still
> OPEN for an explicit ruling: P1–P3 (the SYNC unleased handle stub returning `RemoteSource<T>`
> with `Absent`/`Failed`, server dedup by source identity with lease counting, std `Memo`, A79 in
> the same shape — the rpc-32 brief stands in `briefs32.md`) and B287 (P4).

## 10. Where it lives

A `[library]` package, `std::rpc` (or a standalone `rpc` library), providing the stable
core: the `Transport` and `DuplexTransport` shapes + built-in transports, `RpcError`, the
envelope types, and the reactive runtime with its capability table (all shipped; the
server-side mounts live in the process-layer `std::rpc_server`). The codec seam shipped
too — `Codec`/`Frame` live in `std::wire`, with `json_codec()` (`std::json`) and
`binary_codec()` (`std::binary`) as the two implementations (§6.2). The `[derive(Wire)]` derive, the
`[service]`/`[rpc]` generation (dispatcher + stub), and the `[trait_only]`/`[doc(hidden)]`
attributes are **compiler** features, not library code (§11). The application's own domain types, their
Wire twins, the `to_wire` projections, and the `[service]` contract live in the app —
typically a shared `common`-style `[library]` for the contract + Wire types both sides
import, with the server and client packages depending on both, exactly like the current
`common`/`client`/`server` workspace.

## 11. Prerequisites & dependencies

Small, independently-useful std extensions (Phase 0) plus the compiler features the
paradigm needs:

- **`std::fetch` gains POST/body/headers** — ✅ **shipped** (commit 7340518). `post(url,
  body)` / `get(url)` builders + `.header(..)` + `.send()`.
- **`std::http` exposes the request body** — ✅ **shipped** (commit 593742a).
  `request.body(): str`; `Server::start` reads the stream eagerly and passes it in,
  since the indirectly-called handler can't suspend.
- **Effect-polymorphic async** — ✅ **shipped**: auto-await propagates through a
  trait-bounded dispatch (§7), so an indirect transport call awaits correctly.
- **`[derive(Wire)]`** — a new derive: the all-fields-Wire check (the §3 rule, the safety
  boundary) plus the encode/decode glue against the `Serializer` visitor (§6). A *derive over
  a struct/enum* — squarely in the shape `expand_derives` already handles.
- **`[rpc]` + `[expose]` attributes + signature checks — ✅ shipped (2026-07-02).** `[rpc]`
  marks a method callable over the wire; every non-`self` parameter and the return must be
  Wire (checked with a clear, spanned diagnostic; a typeless parameter is rejected — the
  dispatcher decodes at declared types). `[expose]` marks a struct field observable by the
  client; it must be a `Signal` of a Wire element. Both are syntactic checks over the same
  `is_wire_type` as `[derive(Wire)]` (trait-satisfaction is unsound for containers), collected
  during the walk and validated once all modules' Wire names are known. Inert markers until
  `[service(Client)]` generation consumes them.
- **`[service]` generation — ✅ shipped (2026-07-02).** From a `[service(Client)]` struct's
  same-module `[rpc]` impl methods + `[expose]` fields, the compiler generates:
  `Session::dispatcher(self)` (one route per `[rpc]` method over the §4.1 `Dispatcher`,
  handlers capturing the session), the sibling `Client<T: Transport>` (`Result`-wrapped
  requestor methods + a `RemoteSource` mirror per `[expose]`d field), and a shared
  `contract_hash(self)` on both sides (djb2 over the canonical surface). Generation *over a
  struct+impl*, beyond the struct/enum derives; resolves Q1; the runtime it emits over is
  `std::rpc` (§10, also shipped). `examples/rpc` runs byte-identically on the generated code.
  **v1 scope:** the service struct and its `[rpc]` impls must share a module; service structs
  are concrete (no generics); the client is constructed literally
  (`Client { transport, status = … }` — `Client::connect` + hash *enforcement* on connect
  arrive with the real transports, phase 4); mirror observers decode the JSON value at the
  concrete site (a typed mirror wrapper is a later refinement).
- **`[trait_only]` + `[doc(hidden)]` — ✅ shipped (2026-07-02).** The namespace-hygiene
  attributes (§3.2): `[trait_only]` excludes a trait method from concrete-type member lookup
  (instance, static, and inherited-default paths) while trait-bound resolution is untouched,
  with the "no method" diagnostics naming the trait; `[doc(hidden)]` is a parsed, recorded
  marker awaiting LSP completion. The **derived-methods-`[trait_only]`-by-default flip is
  deferred** (§3.2: the derive codegen itself calls concretely; needs bound-helper routing —
  its own migration slice with/after `[service(Client)]` generation).
- **A byte-array type for binary codecs** — a binary `Codec` produces bytes, not text (§6).
  `List<u8>` is the stand-in for now (probably easiest); a proper fixed `[u8]`/`Bytes` array
  type is the real want (added to the backlog). Binary *framing* also needs hex literals and
  bitwise/shift operators — the same backlog item (I2) gating the WebSocket frame codec.
  JSON-only needs nothing here (UTF-8 `str`).
- **Codec derives** — Map serialization (backlog I1) and the `List<List<T>>` fix widen what
  crosses; not blockers (work around as in §3.1).
- **The reactive protocol** — the `Source`/`Signal` split, a `DuplexTransport` (+ its
  `SplitDuplex` fallback), and `ReactiveProtocol` with its capability table (§8) — for the
  reactive phase only.

## 12. Phased plan (XL → shippable slices) *(was §11 — the number `benchmarks/README.md` and `p6-followups.md` cite)*

0. **Substrate** (S) — ✅ **SHIPPED** (commits 7340518, 593742a): `fetch` POST/body/headers
   + `http` `Request::body()`, with the full round-trip verified end-to-end.
1. **Runtime, hand-written** (M) — ✅ **done** (record corrected 2026-07-02: an earlier
   revision of this line claimed `Codec`/`JsonCodec` here — they were never written; the
   codec seam remains §6 design): `Transport`/`RpcError`, `LocalTransport` +
   `HttpTransport`, the envelope types, and a **manually-written** dispatcher + stub
   proving an end-to-end client↔server call with the `Result` error model and async.
   Pinned the wire format and the runtime first (the project's "prove it before
   generating it"); the runtime has since been promoted to `std::rpc` (phase 3) and
   `HttpTransport` is proven over a real socket (phase 4).
2. **`[derive(Wire)]`, `[rpc]`, and `[trait_only]`** (L) — the data boundary and the
   exposure check: the all-fields-Wire rule and its diagnostics, the `[rpc]` signature
   check, the `Wire` round-trip against the `Serializer` visitor, and the
   `[trait_only]`/`[doc(hidden)]` attributes so derived methods stay out of the way (§3.2,
   derived methods `[trait_only]` by default). Convert the `examples/rpc` payloads from
   `[derive(Json)]` to `[derive(Wire)]` with explicit `to_wire` projections — the first
   dogfood. **In the same pass, bring every example up to the latest project structure**
   (platform model + library packages): current `vilan.toml` conventions, the shared
   `common` `[library]`, per-package `platform`.
3. **`[service]` generation — seamless remote functions** (L) — **✅ shipped (2026-07-02)**:
   the dispatcher + client sibling generated from a `[service(Client)]` struct (§4.2, §7),
   `Result` wrapping applied by codegen (auth stays manual body logic — Q4), and the
   **contract hash** emitted on both sides (Q6 v2 — *enforcement* on connect lands with
   phase 4's real transports, where a mismatch becomes a clean `RpcError` instead of silent
   decode garbage). `examples/rpc` migrated to the generated form (byte-identical output),
   and the runtime moved to `std::rpc` (§10).
4. **`DuplexTransport` + server↔server** (L) — **HTTP half ✅ shipped (2026-07-02)**:
   `HttpTransport` + the RPC mount (now `std::rpc_server`) + generated `verify()` contract enforcement,
   with a real-network CLI test (server↔itself over localhost is server↔server in mechanism —
   same binary, two roles). **Duplex half ✅ shipped (2026-07-02) as the `SplitDuplex`
   fallback** (settled): SSE + POST over pure `std::http`/`fetch`, `serve_connected` on the
   server, `connect_split` + `bridge` on the client — the reactive runtime rides it unchanged,
   and the multi-session realtime CLI test passes (two sessions, one mutation, both observe).
   Remaining, non-blocking: the true WebSocket `SocketTransport` (also `impl Transport` by
   correlation, so RPC and reactive multiplex over one socket) — **gated by a finding**: Node
   has no built-in WS *server*, and RFC 6455 framing in-language is blocked on bitwise ops + a
   byte type (backlog I2); when either lands (or a deno-layer/host-shim route is chosen), WS
   becomes a drop-in `DuplexTransport` swap. `transport.flush()` (the buffered turn) waits for
   a transport that actually buffers — WS.
5. **Reactive north star — `ReactiveProtocol`** (L) — the `Source`/`Signal` split, the
   capability table (export/import `Source`s by id), and the subscribe/update/unsubscribe frame
   protocol over the duplex transport (§8). The capstone.
6. **Validation: example apps + benchmarks** (M; agreed 2026-07-02) — build/update the example
   projects on the finished stack. Headline: a **todo app with server-side data storage**
   (browser client ↔ server over HTTP RPC), whose milestone is **realtime sync** —
   multiple sessions connected and subscribed to the todo list, every mutation flowing to all of
   them through the reactive protocol + wire turn. **Todo app ✅ shipped (2026-07-02)** as
   `examples/todo`: a three-package workspace (`common` holds `[derive(Wire)] Todo` +
   `[service(TodoClient)] TodoStore`; the generated `TodoClient` imports cleanly into the
   browser bundle), realtime sync over SplitDuplex verified end-to-end (two live sessions each
   observing the other's add/toggle/remove), and persistence as a plain signal subscription
   (`todos.sub → fs::write_file`, reloaded via the new `fs::exists` on boot, ids seeded past
   the stored maximum). The slice also closed the **connection lifecycle** gap it exposed:
   `serve_connected` gained `on_disconnect(id)` (an SSE stream's `close` scrubs the wire and
   tells the app), and `ReactiveServer` is now `Disposable` — `expose` *retains* its
   source→mirror subscriptions (previously discarded, so a session could never be torn down)
   and `dispose()` releases every forward and mirror; pinned by a CLI test where a subscribed
   client process dies and a surviving session still observes later mutations.
   **Benchmarks ✅ shipped (2026-07-02)** as `vilan/benchmarks` (`vilan run vilan/benchmarks`;
   harness + deterministic frame counts CI-pinned): payload sizes make the JSON
   double-encoding a number (~15% envelope overhead on a 200-item list; the §6.2 binary codec
   halves the payload — 7,094 vs 14,181 B — before the runtime even rides it); coalescing
   counted at the wire (100 lone sets → 100 update frames, 100 in one `batch` → **1**, an RPC
   handler's 3 writes → **1** alongside the reply); sequential round-trip throughput
   (~286k calls/sec in-process vs ~820 over localhost HTTP on the dev machine — illustrative,
   machine-dependent); and realtime fan-out (3 real SSE sessions × 50 mutations settle in
   ~75 ms, a deterministic subscribe+1-per-mutation frame count per session). Re-run after
   the §6.2 re-plumb for the binary-frames comparison. **Phase 6 is complete.**

The agreed build order within phases 2–3 (2026-07-02): the `[rpc]`/`[expose]` checks first, then
the `[trait_only]`/`[doc(hidden)]` hygiene attributes (§3.2), then `[service(Client)]`
generation, then the real transports (phase 4), then phase 6's apps + benchmarks.

7. **Sessions, handles, and the other direction** (L; §9) — **✅ Order 31, 2026-09-09**:
   per-connection mutable state through `&mut self` (B272), return-typed signal handles
   with the demand-decides release rule (A74), client-declared functions as notifications
   (A75), the receive loop made non-blocking (B281), the delta cell and the keyed mirror
   as a `Source` (A54, A55), the keyed-map refusal (A56). Left: the keyed return mapping
   (A79), awaited reverse calls (A81), the `&mut self`-across-await rule (B287).

The **codec** slice is complete (see §6's status block): the agreed order ran
prerequisites → visitor → both codecs → the single-pass re-plumb, and the benchmarks
bracketed it as planned (JSON double-encoding ≈15% measured before; binary halves
payloads; the trait-shaped visitor added +18%/+14% on the direct paths). Phases 0–2 are the usable core (typed
request/response with the Wire boundary); 3 makes the calls seamless (generated stubs);
4–5 are the reactive/streaming reach. Each is independently valuable and testable.

## 13. Test plan

- **Wire round-trips** — every supported payload shape (scalars, `List`, `Option`,
  nested derived Wire structs/enums) `encode → decode` to an equal value; the §3.1 gaps
  asserted as *known* (so fixing them flips a test green, à la the `#[ignore]` pattern).
- **The Wire rule** — a `[derive(Wire)]` on a struct with a non-Wire field is a clean
  compile *error* (pinned like the analyzer's other diagnostics); a Wire twin of the
  same data compiles. This is the safety property, so it gets a first-class test.
- **The `[rpc]` signature check** — an `[rpc]` method taking/returning a non-Wire type
  fails to compile; a Wire-compatible one passes.
- **`LocalTransport` end-to-end** — an invocation dispatched in-process, no network:
  request → dispatch → reply → decoded result; plus the error paths (unknown method →
  `err`, malformed args → `Decode`, a manual auth check without identity → its app error).
- **HTTP transport** — a CLI/integration test (like `workspace.rs`) builds a tiny
  client/server workspace and exercises a real `fetch`→`http` round-trip under Node.
- **Exposure** — a non-`[rpc]` method is *not* dispatchable; an off-surface method name
  is rejected.
- **`[service]` generation** — golden-test the dispatcher + stub the `[service]` derive
  emits, then compile-and-run a full client↔server round-trip through the generated pair
  (mirrors the derive tests); confirm the generated client returns `Result<T, RpcError>`
  while the trait/impl is `T`.
- **`[trait_only]` / `[doc(hidden)]`** — a `[trait_only]` method is callable through a
  trait bound but a clean compile *error* on the bare concrete type; a derived trait's
  methods are `[trait_only]` without annotation; a `[doc(hidden)]` method stays callable
  but is absent from the language server's completion list.
- **Reactive protocol** (Phase 5) — a `Source` exported to a `ChannelId` round-trips to a
  working `RemoteSource` over an in-memory `DuplexTransport` pair; `sub` receives the server
  signal's updates and `dispose()` unsubscribes; and a `ReactiveProtocol` over a
  request/response `Transport` is a clean compile *error* (the `DuplexTransport` bound).

## 14. Settled decisions vs open questions

**Settled:** the library is a *guide* for structure and a *generator* for plumbing —
Transport + Codec are the stable core; the dispatch plumbing is a **hand-writable
foundation** (`call` on the client, a `Dispatcher` on the server; §4.1) that a `[service(Client)]`
struct can *sugar* by generating it (§4.2), never a mandatory system. An endpoint has **two
signatures** — the server face returns `T`, the client face `Result<T, RpcError>` — so they
are **two functions**, not one the compiler bends by caller side (undefined for
server↔server); the server face is the source of truth and the client a generated *sibling*
projection (only the glue — the Wire types and `to_wire` projections stay the developer's). `[derive(Wire)]` is the data boundary with
the all-fields-Wire rule (sensitivity is a type property; no skip-lists); explicit
`to_wire` projections (the wire shape diverges freely from the domain type); `[rpc]`
marks the exposed surface with a Wire-compatibility signature check; `[expose]` publishes a
`Signal` field to the client as a mirrored `Source` (§8); `[trait_only]` keeps
derived methods off the concrete type (default for derives) and `[doc(hidden)]` keeps them
out of completion. The codec is the *format* (bytes, not `str`), chosen as a runtime value
so JSON↔binary is a programmatic / env switch; JSON is the default and only codec at first.
**Transport and codec compose *under* a protocol, not each other:** RPC (request/response) and
Reactive (pub/sub) are sibling protocols over a transport + codec, so plain HTTP RPC carries no
reactive machinery. The transport is a dumb pipe in two shapes — request/response (`Transport`;
HTTP/in-process) and full-duplex (`DuplexTransport`; WebSocket, or a `SplitDuplex` of SSE+POST);
the reactive protocol requires the duplex shape (a compile error otherwise). A `Signal`/`Source`
is a *capability*, exported as a `ChannelId` into a per-connection table (Cap'n Proto style) so
the codec stays pure. `Result<T, RpcError>` on the client, applied by codegen;
effect-polymorphic async (auto-await through the indirect transport call); peer-symmetric.

**Open questions** (Q1–Q9 settled; Q10 parked on a general `?`/try operator; kept numbered so
cross-references hold):

- **Q1 — client invocation form. ✅ Settled (refined):** the seamless call is **sugar over a
  hand-writable foundation** (§4.1) — `call<T>` on the client, a `Dispatcher` on the server —
  not a mandatory system. A `[service(Client)]` struct (§4.2) generates that foundation; the client is
  a generated *sibling*, not an `impl` of the trait (the two-signature split). The compiler
  generates only the glue, never the structure.
- **Q2 — codec abstraction. ✅ Settled in design; record corrected 2026-07-02.** An
  earlier revision said "ship the `Codec` trait now" and later notes marked it done — it
  never shipped. Implementation hardwired JSON end-to-end instead (`Wire` derives =
  `Json`+`FromJson`, `str` frames, a Json-bound foundation — §6 status block). The design
  stands: bytes output and a `Serializer` visitor so a binary codec is zero-overhead.
  Agreed order: prerequisites (hex/bitwise, `Bytes`, the visitor retarget, validating
  decode), then the `Codec` trait with `JsonCodec` + a binary codec (§6).
- **Q3 — the `T` vs `Result<T, _>` asymmetry. ✅ Settled:** the `[service]` method declares
  `T`, the server `impl` returns `T`, and the generated client stub wraps it in
  `Result<T, RpcError>` — codegen owns the one-layer difference, not the developer (§7).
- **Q4 — auth. ✅ Settled: manual (for now).** Identity lives in the **per-connection session
  struct**, populated on connect or by an auth `[rpc]` (`login`); authorization is ordinary
  body logic reading that state — §4.2's `rename` shows the pattern
  (`match self.user_id.read() { None => Err(NotAuthenticated), .. }`). No `[rpc(auth)]`
  attribute: a declarative gate is deferred sugar, revisited only if real services show the
  check as repeated boilerplate (it would then need a predicate convention, e.g.
  `fun authorized(self): bool`).
- **Q5 — addressing/config. ✅ Settled: programmatic — the transport owns its address.** A
  transport is constructed with its endpoint (`HttpTransport::new("https://api.example.com/rpc")`;
  a port + mount path on the server side); the client type stays address-agnostic (it just holds
  a transport), and *where* the string comes from — hardcoded, env var, config file, CLI flag —
  is the developer's choice, not a library config surface. One endpoint serves the whole service
  (the envelope carries the method name), so there are no per-method routes to configure. A
  browser transport may later default to same-origin (a transport nicety). The one residual —
  multi-service on one server (a mount path per service vs a service field in the envelope) — is
  decided with `[service(Client)]` generation.
- **Q6 — versioning. ✅ Settled: runtime errors for v1; a contract hash in v2 (rides with
  `[service]` generation).** v1: both sides build from one workspace, so the compiler guarantees
  the contract at build time and drift is deploy hygiene. The shipped failure modes: a renamed or
  removed method → a clean `RpcError::Remote("unknown method: …")`; a changed Wire *shape* →
  silent garbage (`from_json` doesn't validate — missing fields decode to `undefined`), the mode
  v2 exists to close. v2, with `[service(Client)]` generation (which holds the whole surface):
  emit a **contract hash** (method names + Wire shapes, normalized), sent on connect (WS) or as a
  header (HTTP); a mismatch is a clean `RpcError` *before* any decode — and can drive a "new
  version, please refresh" UX for the stale-browser-tab case. Separately backlogged (I3):
  **validating `from_json`** — decode errors instead of `undefined`, codec hardening that closes
  silent garbage for *all* malformed input, beyond version skew.
- **Q7 — projection sugar. ✅ Deferred by decision.** `to_wire` stays explicit — it *is* the
  paradigm (the wire shape diverges freely from the domain type, §3). A scaffolding derive is
  additive and waits until the explicit form has proven itself; out of scope for the initial
  build.
- **Q8 — `Map` payloads. ✅ Launch without.** Structs / `List<Pair>` cover the initial
  payloads; Map serialization (backlog I1) is pulled in when a real payload needs it
  (prove-first), not up front.
- **Q9 — service-declaration form. ✅ Settled — the canonical §4.2 form.**
  The form is `[service(Client)] struct Session { .. } impl Session { .. }`, generating
  a sibling `Client` requestor — *not* a `[service]` trait or a `mod` of free functions. The
  decisive advantage is **per-connection state**: the struct *instance* is the connection's
  session (created on connect, owned by the generated dispatcher so state persists
  across a connection's calls), which a trait/module has nowhere to hold. It subsumes the
  stateless case (a fieldless struct) and converges with the connection/turn layer
  (`reactive-batching.md`) — one object carries session state, the method surface, and the
  flush turn. The generated client stays a *sibling type* (§4.2). Three sub-questions, now resolved:
  - **Reader methods. ✅ Round-trip.** Every client method is a wire round-trip (`async` +
    `Result`) — simplest, uniform. The reactive-mirror path (a `Signal` field mirrored via §8,
    read cheaply and locally — the RPC+reactive+batching north star) is **deferred**; the escape
    hatch is that a client can read the mirrored signal directly, or hand-add a method to the
    generated `Client`.
  - **Error layering. ✅ Keep the uniform wrap — nested `Result` and all.** The client wraps the
    server's *exact* return `T` in `Result<T, RpcError>`, always — so a server method returning
    `Result<void, LoginError>` yields `Result<Result<void, LoginError>, RpcError>` on the client.
    Clunky to match, but `RpcError` stays the *uniform outer error* across every method, which is
    what lets generic client code (retry wrappers, error boundaries) hold; a merged
    `CallError<App>` would vary the error type per-method and break those consumers. No merging.
  - **Field exposure. ✅ Private by default; `[expose]` a `Signal` field.** Service-struct fields
    are server-private session state; a field is client-visible only via an explicit `[expose]`,
    and only if it is a `Signal<T>` (Source) — exposure *means* the client observes it, and only
    something observable can be mirrored (a plain value has nothing to subscribe to; a one-time
    read is what a method is for). The generated `Client` then carries a `Source<T>` for it (a §8
    `RemoteSource`), so `client.x` is a local, always-current mirror — the cheap read the
    round-trip default deferred, recovered per-field. The element `T` must be Wire; and reactive
    push needs a duplex transport (§8), so exposing any field constrains the connection to duplex
    (a pure-RPC service with no exposed fields stays request/response). Net split at the service
    surface: **methods = RPC actions (round-trip); `[expose]`d Signals = observable state.**
  - **Mutable session state. ✅ By nature — `&mut self`+plain for sync, `Signal`/`Shared` for
    async/exposed.** `&mut self` is the idiomatic in-place receiver (as `Arena`/`List`/`Map` use),
    so the connection *owns* the session and re-borrows `&mut self` per call with no `Shared` —
    ideal for *synchronous* state transitions with plain fields. But a view can't be held across an
    `await` (no-view-across-await, an intended-but-deferred rule), so an async method takes `self`
    by value (as every transport's `async fun call(self, ..)` already does); persisting a mutation
    through a by-value `self` then requires a `Shared<T>`/`Signal<T>` field (`self.x.write() = ..`).
    So: exposed or async-touched state → `Signal`/`Shared`; sync-only private state → plain field +
    `&mut self`. Default lean: `Signal`/`Shared` (await-safe, matches the reactive code), plain
    `&mut self` as the sync optimization — a `&mut self` method is itself a promise that it does
    not await. No auto-wrapping magic; the field type is the developer's and signals the method's
    nature.
    > **Built, 2026-09-09 (B272, ruling R-A38b option (a)).** Q9's prediction holds and the
    > mechanism is smaller than it assumed: the connection does own the session and a
    > `&mut self` method does mutate it in place per call, with no `Shared` — not because
    > the generator re-borrows a cell, but because the generated `dispatcher()` declares
    > `mut self` and every route captures that BINDING (spec §6.9), so a `&mut self` call
    > through any route reaches it; `dispatcher()` runs once per connection under
    > `Service::factory`, so the write survives to that connection's next call and no other
    > connection sees it. Two clauses amended. First, **`mut self` is REFUSED on an `[rpc]`
    > method** (span on the method): it is the receiver whose copy is discarded when the
    > handler returns — the silent loss §9.1 measured; the admitted spellings are
    > `&mut self` (a write the next call must see), `Shared<T>`/`Signal<T>` (state something
    > other than a method body must reach) and an `[expose]`d cell (state with a wire behind
    > it). Second, the async clause is over-cautious as built: an `async fun f(&mut self)`
    > `[rpc]` method compiles today and its write persists, because the no-view-across-await
    > rule is still deferred and the awaits sit inside the callee; "a `&mut self` method is
    > itself a promise that it does not await" therefore has NO enforcement behind it, and it
    > became load-bearing the moment B281 let one connection's handlers interleave — B287,
    > stated in the guide, ruled by the owner.
- **Q10 — server-handler decode ergonomics.** `arg(req, i)` reads clean on the happy path; a
  malformed argument wants `arg -> Result<T, RpcError>` + a `?`/try to stay terse (else a
  handler regrows a per-argument match). This is really a **general error-handling dependency**
  (a `?`/try operator), not an RPC-specific decision — the foundation works today with the
  happy path plus an explicit decode-failure reply. Track as a prerequisite; revisit when
  `?`/try lands.

## Appendix: compiler quirks the hand-written example surfaced
## (moved 2026-08-03 from `examples/rpc/README.md`, where they were
## design history in a reader-facing document)

The example was worth building partly because it surfaced compiler bugs the
service generation later leaned on. All were fixed and pinned; the README
carried their full archaeology until the D7-tail cleanup moved it here (the
complete text is in git history at `vilan/examples/rpc/README.md`; the
reader-facing language lesson — parenthesized field-projection receivers and
struct-level bounds — stayed in the README).

1. **Derives only expanded in the entry file** — imported `[derive(Json)]`
   types had no `from_json`. Fixed (3592343): expansion runs in every module.
2. **Parenthesized receiver + struct-level bound** — intended syntax, not a
   bug; kept in the README as teaching.
3. **The generic-field object stub miscompiled to the abstract method** —
   field access now substitutes the receiver's type arguments, and a generic
   struct initializer no longer publishes an unbound type while deferred
   (backlog B1, class B; pinned by `generic_field_method_dispatch_runs` and
   neighbors in inference.rs).
4. **`from_json` element inference through an indirect return path** lowered
   to the abstract method — fixed by return-type-driven body inference with
   `resolve_match` propagating the expected type into each leg (pinned:
   `from_json_return_type_flows_through_match_arm`).
5. **A generic element serialized inside a closure** lost its bound AND its
   call-site derivation — fixed by substituting parameterized bound arguments
   in the `Type::Generic` resolution arm, deriving bound-only generics from
   the concrete argument's impl, and deferring calls with unbound own-generics
   while an argument is unresolved. The closure-capture case that closed the
   B1 cluster.

What the example validated end-to-end: the data boundary, both transports,
the codec, both protocols, the capability table, over-the-wire subscription,
the wire turn, and the per-connection session. The `[service(Client)]`
generation runs the example byte-identically to the hand-written form it
mechanized. Still open at the move: the real transports (HTTP + WebSocket)
with `Client::connect`, contract-hash enforcement on connect, and
`transport.flush()` for the buffered turn; `param: SomeTrait` as a bound
remains aspirational syntax; the capability table stores `str` absent trait
objects.
