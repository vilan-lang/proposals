# A `[service]` as a plain HTTP API (A120)

*Handed back by lane papers-39 of Order 39 as a new section for
`proposal/transport-rpc.md` — it belongs directly after §9.6c (the awaited
`void`), as **§9.7**, because it is the last thing §9's transport story leaves
unsaid: §9 designed the socket in full and never gave the connectionless leg a
client. Written on vilan `next` @c3f7d1a3 (`vilan 0.40.0 (c3f7d1a38)`), which is
the toolchain every number below was measured on, node 24.2.0.*

Tracker A120. Related: A78 (a handle service on the connectionless leg,
CLOSED Order 32 — its runtime refusal is measured below), A107 (the awaited
`void`, CLOSED Order 38 — §9.6c), A40 (the credential at the handshake), A48/A52
(the refusal statuses), A92 (the sync handle stub — the precedent for a
constructor that makes no call), B363 (`unit-literal.md`, this lane's sibling
paper, which retires §9.6c's reason for `Option<RpcError>`), F18 (the native
server, Order 39's other HTTP lane).

Probes: `scripts/integration/sweeps/order39/papers-39/probes/` — five packages
for this section (`a120_http_leg`, `a120_stub_over_http`, `a120_refusals`,
`a120_content_type`, plus `find_json_reader`/`find_arity`/`find_export_impl`
for the three finds), each with its captured output, re-runnable with
`probes/run_all.sh`. Every claim below that a probe can check is named beside
its probe.

---

## 1. The ask, and the answer up front

kolt cannot use a `[service]` for its login door, because login must succeed
*before* a socket can be authorized — the token the handshake carries is what
login returns. So kolt hand-writes the whole path three times over: a plain
`mod KoltAuth` instead of a service (`store.vl:51`), a hand
`match parse_path(request)` building JSON responses inside `on_request`
(`server.vl:31`), and `fetch::post("/api/login", body)` +
`Result<AccountToken, str>::from_json` on the client (`comp/login.vl:77`
and `:179`). Its own two FIXMEs ask for a service that is only an HTTP API.

**The client already exists. It has no constructor, no refusals, and one
decoding hole that an arbitrary caller can walk through.**

The generated client is `struct <Name>Client<T: Transport>` — the transport is a
type PARAMETER (`rpc.vl`, `client_struct = struct_of(..).generics("<T: Transport>")`),
and every plain stub, plus `verify()` and `contract_hash()`, lives on the
unconstrained `impl <Name>Client<type T>`. Only `connect`, `connect_with` and
`with_handlers` are pinned to `impl <Name>Client<SocketTransport>`. So this
compiles and runs today, on the shipped toolchain, with no socket, no
handshake, and no compiler change:

```vilan
export fun auth_over_http(base: str): AuthClient<HttpTransport> {
	AuthClient<HttpTransport> {
		transport = HttpTransport { url = base + "/auth/rpc" },
		codec = json_codec(),
	}
}
```

`probes/a120_stub_over_http` builds that for a browser leg AND a node leg and
runs the node one:

```
--- the generated stub over HttpTransport, no socket
login: token=tok-ada user=ada
login2: app error wrong password
echo: 41
--- the awaited void stub (A107) over HttpTransport
  [server] touch(via-stub)
touch: acked
--- verify(): the contract check an http client CAN make
verify: true
```

Four things are proven there and each is load-bearing: a `Result`-returning
method round-trips both arms; a plain method round-trips; **the awaited `void`
of §9.6c works over the POST leg and the handler runs before the ack**; and
`verify()` — the contract hash comparison — is reachable, so an HTTP client can
check the surface it was built against.

So A120 is not a mechanism item. **It is a constructor, four refusals, a status
table, and one bug.** That is §4–§8, and the bug (§8) is the only part that
must land before kolt's login is safe to expose.

## 2. The premise check

Per the Mechanics rule, the item's text is a hypothesis. Three of its clauses
hold and one is understated:

- *"The connectionless `POST {mount}rpc` leg EXISTS on the server"* — **true**,
  and it is installed beside every mounted service by `ServerBuilder::build`'s
  fold (`rpc_server.vl`, `service_response`). Measured end to end in
  `probes/a120_http_leg`.
- *"What is missing is a CLIENT that speaks it without a socket"* — **half
  true, and this is the correction the paper turns on.** The client TYPE speaks
  it already; what is missing is the constructor and the refusals. The item
  reads as though a stub had to be generated; nothing has to be generated that
  is not.
- *"…and a story for a service that is ONLY that"* — **true**, and that story
  is §5 (what such a service may not declare) and §6 (how it is gated).
- The item names `rpc_http.rs` as the server side. There is no such file; the
  leg is `rpc_frame_response` in `vilan/std/src/process/rpc_server.vl`, in
  vilan. (The Rust crate the item is remembering is the HTTP *server*, not the
  rpc leg.)

## 3. What the POST leg answers today — measured

`probes/a120_http_leg` mounts four services on one builder — a shared
`Service::new`, one with a handle-returning method, one behind `authorize`, and
one `Service::factory` — and then POSTs hand-built JSON envelopes at its own
port from `on_start`. Every row below is that probe's output verbatim.

| what was POSTed to `{mount}rpc` | status | body |
|---|---|---|
| `{"method":"echo","args":[7]}` | **200** | `{"Success":107}` |
| `login` returning `Ok(token)` | **200** | `{"Success":{"Ok":{"token":"tok-ada","user":"ada"}}}` |
| `login` returning `Err("wrong password")` | **200** | `{"Success":{"Err":"wrong password"}}` |
| a `void` method (A107's awaited ack) | **200** | `{"Success":true}` — and the handler printed BEFORE the reply |
| `__contract` | **200** | `{"Success":"d82b084e"}` |
| `__attach` | **200** | `{"Failure":{"Remote":"unknown connection"}}` |
| an unknown method | **200** | `{"Failure":{"Remote":"unknown method: nosuch"}}` |
| a body that is not JSON | **200** | `{"Failure":{"Decode":"malformed JSON"}}` |
| `echo` with NO arguments | **200** | **`{"Success":NaN}`** ← §8 |
| a handle-returning method | **200** | `{"Failure":{"Remote":"`watch` returns a signal handle, …"}}` (A78's sentence) |
| any method on an `authorize`d service | **401** | `{"Failure":"Unauthorized"}` |
| any method on a `Service::factory` service | **501** | a plain-text sentence, **not an envelope** |
| `GET {mount}rpc` | **200** | `{"Failure":{"Decode":"malformed JSON"}}` — the method is never checked |
| a path no service claims | 404 | the app's `on_request` answer |

Read as a design document, that table says six things.

1. **Status is 200 for everything the protocol itself decides.** An unknown
   method, a garbled body and an application `Err` are all 200. Only the two
   std-side REFUSALS (401, 501) and the fallback (404) carry another status.
2. **An application error is inside `Success`.** `Result<AccountToken, str>`'s
   `Err` arm is a value that crossed successfully, and the leg treats it that
   way. This is right, and §7 keeps it.
3. **`__contract` is reachable**, so an HTTP client has a version check.
4. **`__attach` is not**, and says so in one sentence — which is exactly the
   boundary §5 draws: mirrors need a connection.
5. **The 501 is not an envelope**, so a vilan client meeting it gets
   `Decode("unrecognized reply envelope")` rather than a typed failure
   (measured in §7).
6. **`GET` on the rpc route is answered as though it were a POST with an empty
   body.** Nothing reads `request.method()`.

## 4. `over_http` — the constructor

```vilan
export impl <Name>Client<HttpTransport> {
	/// Reach this service over its connectionless `POST {mount}rpc` route —
	/// no socket, no handshake, no mirrors. `mount` is the SAME string
	/// `connect` takes (`"/"`, `"/auth/"`): the route is plain concatenation,
	/// exactly as `Service::at` forms it.
	fun over_http(mount: str, codec: Codec): <Name>Client<HttpTransport> {
		<Name>Client<HttpTransport> {
			transport = HttpTransport { url = mount + "rpc" },
			codec,
		}
	}
}
```

Four decisions, each with its reason.

**It is SYNC and it makes no call.** `connect` verifies the contract with one
round trip, and that is right for a socket: the connection is long-lived, so
one trip amortizes over every call it carries. Over HTTP there is no
connection, so "once per client value" is an arbitrary unit — a client value
may serve exactly one call, and a login form constructs one per mount. A92
already set this precedent for the handle stub ("SYNC, and it makes no call"),
and the check has a better home: `verify()` is on the generic impl and reachable
(measured, §1), so a caller who wants it asks for it. The docs sentence is
"an HTTP client is unversioned unless you call `verify()`".

**It takes the MOUNT, not the endpoint URL.** `connect("/admin/", codec)` and
`over_http("/admin/", codec)` then read the same, and a service moved to another
mount moves one string on each side. `HttpTransport { url }` stays the raw door
for a client pointed at another origin.

**It is named `over_http` and not `connect_http`.** The item's spelling reads
well but `connect` means "there is now a connection", which is the one thing
this does not do — and §9.2's whole lease story hangs off that word. `over_http`
says the transport and claims nothing.

**It is generated only for a service an HTTP client can actually hold** — §5.

## 5. What is refused, and where

The client struct's FIELD LIST is already the refusal, and it is total.
`probes/a120_refusals` builds three hand-written literals and reads the
diagnostics:

```
Error: `ExposedClient` expects 3 fields, but got 2 instead: `tally` is missing.
Error: `HandleyClient` expects 3 fields, but got 2 instead: `reactive` is missing.
```

- An **`[expose]`d field** puts a `RemoteSource<T>`/`KeyedSource<K, T>` field on
  the client, which only `connect`'s `__attach` can fill — and `__attach` over
  POST answers `unknown connection` (§3). Refused structurally.
- A **handle-returning method** puts a `reactive: ReactiveClient` field on the
  client (`if any_handle`), which only `connect` mints. Refused structurally.
  The runtime refusal A78 left behind is still the right *server*-side answer
  for a hand-built protocol, and it still fires (§3).
- A **notification-bearing service** — `[service(C, client = H)]` — is **NOT
  refused, and this is the one real hole.** `PeerClient<HttpTransport>` built
  clean in the same probe. The reverse direction then silently does nothing:
  `with_handlers` is `SocketTransport`-only so the HTTP client can never receive,
  and the server's `notify(connection, ..)` on the connectionless leg finds no
  client channel and drops by design ("a connection that has already closed
  silently drops it"). That is a service whose declared second direction is
  dead, with no diagnostic anywhere.

So the generator's rule is one line: **emit `over_http` when the client struct
has exactly its two base fields (`transport`, `codec`) and the service declares
no `client = H`.** For every other service `over_http` simply is not there, and
the diagnostic an author meets is the field list's, which already names the
missing field and therefore the reason.

That leaves the *early, named* refusal, which is what `[service(http)]` would
buy. The paper recommends it as an **opt-in marker, not a mode**:
`[service(AuthClient, http)]` asserts "this service is an HTTP API", and the
expansion then refuses AT THE DECLARATION, in the attribute's own vocabulary
and spanned on the offending member —

```
an `http` service's method `watch` returns a signal handle, and a handle's
reply is a channel id minted in a CONNECTION's capability table, which the
connectionless POST leg has none of: return the value, or drop `http` and
reach this service over the socket transport
```

— rather than at the far-away call site that could not build a client. It is a
marker and not a mode because *which transports reach a service* is a property
of the mount and of each method, not of the struct: kolt's `KoltStore`
legitimately wants both the day it grows a REST-ish leg beside its handles.
**Q1 in §12.**

## 6. `authorize`, and the login that mints the socket's token

This is the part of the item that is really a design question, and the
measurement settles half of it: **a service with `authorize` refuses its POST
leg outright, 401, with a typed `Failure(RpcError::Unauthorized)` envelope**
(§3). That is deliberate and documented at the site — the SSE and POST legs
"carry no handshake … no place for a credential the browser could have put
there — so there is nothing for `authorize` to gate and they are refused rather
than left as the open back door around it."

So **an HTTP-only service cannot be gated today.** And kolt's shape is the right
one and does not change:

```
  POST /auth/rpc   ── ungated ──▶  KoltAuth::login  ──▶  AccountToken
                                                            │
  ws:// …/         ── authorize(handshake.token()) ◀── rpc_protocols(token)
```

The login door is a *separate, ungated* service, and the token it returns is
what `rpc_protocols(credential)` puts on the socket handshake for `authorize` to
read back with `Handshake::token()`. Nothing about that composition needs
building: it is what kolt already does by hand, and turning `KoltAuth` into a
`[service]` leaves it intact.

What A120 *adds* is the gate for the HTTP leg itself, for the services that come
after login. The claim "the POST leg carries no place for a credential" is true
of the WebSocket handshake and false of a POST: `std::http::Request` has
`header(name)` today. So:

```vilan
fun authorize_request(own self, check: async |Request| Result<Session, Reject>): Service
```

A **second** hook, not `Handshake`'s. `Handshake::token()` reads the
`"token."` SUBPROTOCOL convention, which a POST has no analogue of; a POST's
credential home is `Authorization: Bearer …` or a cookie, and silently
answering `None` from `token()` on a request that carried a perfectly good
header is worse than having two hooks. The composition rule, written down:

| the service declares | the socket upgrade | `POST {mount}rpc` |
|---|---|---|
| neither hook | open | open (today) |
| `authorize` only | gated | **401, unchanged** — no silent back door |
| `authorize_request` only | open | gated per request |
| both | gated | gated, each in its own vocabulary |

The `Session` an `authorize_request` proves has nowhere per-connection to
live — there is no connection — so it reaches the handler the only way a
connectionless request can carry anything: on the `RpcRequest`, beside the
`connection: i32` that is already stamped there for exactly this reason. A
`Service::factory` service stays 501 on this leg whatever the hook says,
because the instance, not the identity, is what a POST cannot supply.
**Q2 in §12.**

## 7. Status codes

Today's answer is "200 for everything the protocol decides" (§3), and the
reason it has survived is that **`HttpTransport::call` never reads
`response.status()`** — it reads the body and hands it to the codec. Measured,
`probes/a120_stub_over_http`, a stub pointed at four different answers:

```
404 echo: Decode("unrecognized reply envelope")     ← the app's 404 text body
501 echo: Decode("unrecognized reply envelope")     ← the factory refusal's text
401 echo: Unauthorized                              ← decoded from the ENVELOPE
```

The 401 arrives correctly *because its body is an envelope*, not because the
status was read. So moving the statuses off 200 breaks no vilan client — which
is what makes the following a non-breaking change, and what makes it worth
doing, because the statuses are the contract for everything that is *not* a
vilan client: curl, a `fetch` in a page, a proxy, a load balancer, a browser
devtools panel, a monitoring probe.

**The rule: the ENVELOPE is the vilan client's contract; the STATUS is
everyone else's, and the two never disagree.**

| outcome | status | why |
|---|---|---|
| `Success(..)` — including an application `Err` arm | **200** | the call happened and the value crossed; an application error is a VALUE, not an HTTP failure. This is what kolt's hand leg already does. |
| `Failure(Decode(..))` | **400** | the caller's bytes were wrong |
| `Failure(Unauthorized)` | **401** | unchanged from today |
| `Failure(Unavailable)` | **503** | A52's arm, and its documented meaning |
| `Failure(Remote("unknown method: …"))` | **404** | the method is the resource |
| `Failure(Remote(..))` — a handler that failed | **500** | the server's fault |
| `Failure(Contract(..))` | **409** | the two sides disagree about the surface |
| a non-POST on `{mount}rpc` | **405**, `Allow: POST` | measured: a GET is answered 200 today |
| `Service::factory` on this leg | **501**, and now **as an envelope** | so a vilan client reads `Remote(..)` instead of `Decode(..)` |

And the counterpart on the client, which is the same change read from the other
end: **`HttpTransport::call` reads the status and answers
`Err(RpcError::Transport(..))` for a body that is not an envelope**, so a
proxy's 502 HTML page stops being a `Decode` error blaming the codec.

### 7.1 The crash that must go with it

`probes/a120_stub_over_http`'s last case points a client at a closed port:

```
TypeError: fetch failed
    at node:internal/deps/undici/undici:15482:13
  [cause]: Error: connect ECONNREFUSED 127.0.0.1:59999
```

**The process dies.** `Transport`'s own doc says "a transport can FAIL (a
dropped socket, an unreachable host) — `Err(reason)` is the infrastructure
path", and `HttpTransport::call` does not honour it; its comment admits as much
("an unreachable host still surfaces as the host fetch's rejection — HTTP-level
robustness is recorded beyond-v1"). For a *socket* client that was tolerable:
`SocketTransport` has the whole dial-and-backoff machinery and nobody reaches
for `HttpTransport` in production. A120 makes `HttpTransport` the production
path for a login form, and a login form on a dropped network must say "offline",
not take the page down. So the `fetch` is wrapped and the rejection becomes
`Err(reason)`, which `call` already maps to `RpcError::Transport`.

## 8. The hole an arbitrary caller walks through — and why it blocks the item

`{"method":"echo","args":[]}` answered `{"Success":NaN}` (§3). That is not an
`echo` quirk. `probes/find_json_reader` takes the rpc layer out of it entirely
and reads two `i32`s out of a JSON list through `std::json`'s codec reader:

```
[1,2]     arity=2 left=1 right=2 failed=(not poisoned)
[1]       arity=1 left=1 right=NaN failed=(not poisoned)
[]        arity=0 left=NaN right=0 failed=unexpected end of document
["x",2]   arity=2 left=NaN right=2 failed=(not poisoned)
[null,2]  arity=2 left=0 right=2 failed=(not poisoned)
[true,2]  arity=2 left=1 right=2 failed=(not poisoned)
[1.5,2]   arity=2 left=1.5 right=2 failed=(not poisoned)
```

**A `[rpc]` method's declared parameter types are not enforced on the wire.** A
short (but non-empty) argument list, a string where an `i32` was declared,
`null`, `true`, and a fraction where an integer was declared all produce a value
and leave the deserializer UNPOISONED — so `decode_failed`, which the generated
route does consult (verified in the emitted dispatcher), answers `None` and the
handler runs on `NaN`. `begin_list` even RETURNS the arity and the route ignores
it. Only the empty list trips, and only because the document ended.

For a vilan↔vilan socket this never fires: both sides were generated from one
surface and the contract hash refuses a client that disagrees. **For an HTTP API
the caller is arbitrary** — that is the whole point of the item — so this is the
one thing that must land before kolt's login is exposed. It is filed as a FIND
(see the lane report); the item it becomes is A120's first slice, and the fix
has two layers worth doing in order:

1. **The route gates on arity.** `open_request` already holds `arity`;
   a route whose method declares *n* parameters and whose envelope carries
   fewer answers `Failure(Decode("…expects 2 arguments, got 1"))`. One line in
   `route_block`, one field already on `RpcRequest`. Cheap, and it closes the
   short-list half.
2. **The reader poisons on a type mismatch.** `i32::rebuild` over a JSON string,
   `null`, `bool` or a non-integer number is a decode failure, not a coercion.
   This is `std::json`'s codec reader, not the rpc layer, and it is the half
   that matters for `["x",2]`.

## 9. CSRF and same-origin posture

The POST leg reads its body as bytes and sniffs nothing, and it requires no
header. So the question is whether a cross-site HTML form can reach it — which
turns entirely on the content type, because a form POST can only produce the
three CORS-safelisted ones (`text/plain`,
`application/x-www-form-urlencoded`, `multipart/form-data`).

`probes/a120_content_type` asks the server what it actually received:

```
--- the SHIPPED HttpTransport, text frame (json codec)
  [server] POST /rpc content-type=text/plain;charset=UTF-8
--- HttpTransport::call directly, a Binary frame
  [server] POST /rpc-bytes content-type=text/plain;charset=UTF-8
--- a hand fetch with NO header chained
  [server] POST /bare content-type=text/plain;charset=UTF-8
--- a hand fetch with the header chained
  [server] POST /typed content-type=application/json
```

**`HttpTransport` sends `text/plain;charset=UTF-8`** — the host's default for a
string body, and precisely the one safelisted type a cross-site form can
produce. So a cross-origin form submission is indistinguishable, on the wire,
from the shipped client.

This is not exploitable today, and the reason is worth stating so the fix is not
mistaken for an incident: **no vilan service is gated on an ambient
credential.** The only gate is the subprotocol token at the upgrade, which a
form cannot send, and kolt's token lives in `prefs` (a `StorageKey`), not in a
cookie — a token read by script and put in a header is CSRF-immune by
construction. The hazard arrives the moment §6's `authorize_request` exists and
somebody reads a cookie in it.

So the posture, and it costs one line on each side:

- **`HttpTransport` sets `Content-Type`** — `application/json` for a text frame,
  `application/octet-stream` for a binary one. It should anyway: the leg's
  replies already carry both (`rpc_frame_response`), and a request that does not
  say what it is is a request a proxy may rewrite.
- **The leg requires a non-safelisted content type**, answering 400 otherwise.
  That single check makes a cross-site form structurally unable to reach any
  `[service]`, for every service, whether or not its author thought about CSRF —
  which is the property to want, because the author who did not think about it
  is the one who needs it.
- **The guide says the rest in two sentences**: a credential in a header is
  CSRF-immune; a credential in a cookie needs `SameSite=Lax` *and* this check,
  and std will not read a cookie for you.
- **CORS stays the app's.** `on_request` and `Response::builder().set_header`
  are right there, a service's mount is known, and std guessing an allowed
  origin list is std making a security decision with no information. The guide
  carries the three-line recipe. **Q3 in §12.**

## 10. kolt's three sites, rewritten

This is the worked example the item asks for. Nothing below needs anything from
§5–§9 except §4's constructor and §8's arity gate.

**`store.vl:51` — `mod KoltAuth` becomes a service.** The FIXME goes; the bodies
do not move.

```vilan
[service(KoltAuthClient, http)]
struct KoltAuth {}

impl KoltAuth {
	[rpc]
	fun register(self, username: str, password: str): Result<AccountToken, str> {
		// …unchanged: the module-level `db` by loan, exactly as today
	}

	[rpc]
	fun login(self, username: str, password: str): Result<AccountToken, str> {
		// …unchanged
	}
}
```

It is a `struct` with no fields rather than a `mod` because `[service]` reads a
struct, and an empty one is honest: the door has no state, the database is
module-level by loan. `http` is §5's opt-in marker — this service declares no
handle, no `[expose]` and no `client =`, so it would get `over_http` anyway; the
marker is what makes a later `SignalCell` return a refusal at the method instead
of a puzzle at the call site.

**`server.vl:31` — the hand `match parse_path(request)` deletes.** All of it:
`parse_path`, the `ApiRoute` enum, the `get_post_var` closure, the three
`Response::builder()` chains, the `List<List<str>>::from_json` decode. One line
goes on the builder chain beside the store's:

```vilan
	Server::builder()
		.port(59401)
		.with_service(Service::new(KoltAuth {}.dispatcher().into_protocol(json_codec())).at("/auth/"))
		.with_service(Service::factory(|connection| store_for(connection), json_codec())
			.authorize(|handshake| authorize_connection(handshake)))
		.serve_build(build)
		.cache_build(..)
		.on_request(|request| /* the page, and nothing else */)
```

Two services on one builder, picked by longest mount, answering before
`on_request` — which is `with_service`'s documented shape and is what the
existing gated store already relies on. **`/api/login` becomes `/auth/rpc`**;
that is the one URL kolt's users would notice, and it is a URL no bookmark
holds.

**`comp/login.vl:77` and `:179` — the hand `fetch` deletes.** Both forms
collapse to the same three lines:

```vilan
let auth = KoltAuthClient::over_http("/auth/", json_codec());

// in the submit handler:
match auth.login(username.get(), password.get()) {
	Ok(let outcome) => match outcome {
		Ok(let token) => get_prefs().token.commit_set(Some(token)),
		Err(let message) => show_error(message),      // login.vl:89's own TODO
	},
	Err(let failure) => show_error(offline_text(failure)),
}
```

What that deletes, beside the `fetch`: the `[["username", …], ["password", …]]`
list-of-pairs body (the wire is the envelope now, and the arguments are typed),
the `.to_json()`, the `Result<AccountToken, str>::from_json` and its `_ =>`
parse-error arm — because a decode failure is now `Err(RpcError::Decode(..))` in
the same `match` as everything else, which is exactly what login.vl:90's
"json parse error" print was standing in for. The two TODOs at `login.vl:89`
and `:193` ("show the error to the user") stop being blocked on a third error
shape.

And the shape that was hidden in the hand version becomes visible: **the
`Ok(Err(message))` nesting is the point.** The outer arm is "did the call
happen", the inner is "what did the server decide", and §7's status rule is that
same distinction read on the wire.

One thing kolt keeps: `Result<AccountToken, str>` as the return type, with
`AccountToken` already `[derive(Wire, Json)]`. No type moves.

## 11. Slices

### S1 — the decode gate (S, and it comes first)

The route's arity check, and the JSON reader poisoning on a type mismatch (§8).
This is A120's prerequisite and not really A120's feature: it is what makes any
`[service]` safe to point an arbitrary caller at.

**Exit:** a service-layer pin per row of §8's table — a short list, a string
where an `i32` was declared, `null`, `true`, a fraction — each answering
`Failure(Decode(..))` with the parameter named, over the POST leg and over
`local_rpc`; the too-MANY-arguments case still answering `Success` (extra
arguments are ignored on purpose, and a pin says so); `find_json_reader`'s
seven-line table as a corpus program with the expectations asserted. Every
existing rpc golden must be unmoved — a correct client sends correct bytes, so
nothing should feel this.

### S2 — `over_http` and the four refusals (M)

§4's constructor, generated under §5's rule; the `client = H` case not
generated; `[service(http)]` as §5's opt-in marker with its three refusals
(handle return, `[expose]`, `client = H`) spanned on the offending member.

**Exit:** `probes/a120_stub_over_http`'s node leg as a service-layer pin,
rewritten on `over_http` — the four calls, the awaited void, `verify()`; a
`assert_fails` pin per refusal with its message; a pin that a handle-free
service's contract hash is **byte-identical** (78bdada7 is the shipped control
and this slice must not move it — nothing here touches the surface string, and
the pin is what proves it); the browser leg of the same probe still building,
which is what proves the client is reachable from a page.

### S3 — the status table and the transport's failure path (M)

§7's arm-to-status map; the 501 as an envelope; 405 on a non-POST;
`HttpTransport::call` reading the status and wrapping the `fetch` rejection
(§7.1); `Content-Type` set on the request and required by the leg (§9).

**Exit:** one e2e pin per row of §7's table, asserting the status AND that a
vilan stub still decodes the same `RpcError` it does today (the envelope and
the status never disagree); a pin that a closed port answers
`Err(RpcError::Transport(..))` and the process SURVIVES — red first, because
today it does not; a pin that a `text/plain` POST is refused 400 and an
`application/json` one is not.

### S4 — `authorize_request` (M)

§6's second hook, its `Session` on the `RpcRequest`, and §6's four-row
composition table as four pins.

**Exit:** the table, per row; a pin that a service with `authorize` alone STILL
answers 401 on the POST leg (the no-back-door property, which S4 must not
weaken); a pin that a `Service::factory` service stays 501 under
`authorize_request`.

### S5 — kolt (not vilan's)

§10, at the owner's word, after S1+S2.

Sizing: S1 S + S2 M + S3 M + S4 M. S1+S2 is the item's answer; S3 and S4 are
what make it a first-class leg rather than a back door that happens to work.

## 12. Open questions, each with a recommendation

**Q1 — `[service(http)]`: a marker, a mode, or nothing?**

> **Rec: an opt-in MARKER (§5).** The structural refusal already exists and is
> total — a handle- or `[expose]`-bearing client cannot be built over
> `HttpTransport`, measured — so nothing is needed for *correctness*. What the
> marker buys is the refusal arriving at the METHOD instead of at a call site
> that could not build a client, and it buys it only for an author who asked.
> Not a mode, because which transports reach a service is a property of the
> mount and of each method: kolt's `KoltStore` will want both legs. The
> alternative (no marker at all) is defensible and costs one paragraph in the
> guide instead of one attribute argument.

**Q2 — `authorize_request`, or `Handshake` from a request?**

> **Rec: a SECOND hook (§6).** `Handshake::token()` reads the `"token."`
> subprotocol convention; a POST's credential lives in a header, and having
> `token()` answer `None` for a request that carried a perfectly good
> `Authorization` header is a trap. The alternative — `Handshake::from_request`
> with an empty protocol list — is one fewer concept and silently breaks every
> `authorize` written against `token()` the day somebody mounts an HTTP leg.

**Q3 — does std do CORS?**

> **Rec: NO (§9).** `on_request` plus `set_header` is already the whole
> mechanism, a service's mount is known, and an allowed-origin list is a
> security decision std has no information for. The guide carries the recipe.
> What std DOES do is the content-type check, because that one protects an
> author who never thought about CSRF — which is the author who needs it.

**Q4 — `over_http` or `connect_http`?**

> **Rec: `over_http` (§4).** `connect` means "there is now a connection", and
> §9.2's lease semantics hang off that word. The item's `connect_http` reads
> better in isolation and would be the wrong promise. `http` alone
> (`KoltAuthClient::http("/auth/", codec)`) is the third option and is too
> terse to say that a transport was chosen.

**Q5 — should an application `Err` ever be a non-200?**

> **Rec: NEVER (§7).** `Result<AccountToken, str>`'s `Err` arm is a value that
> crossed successfully. A server that answered 401 for "wrong password" would be
> claiming the CALL was unauthorized, which is a different fact, and it is the
> fact §6's gate reports. kolt's hand-written leg already answers 200 for both
> arms; this is that choice, written down. The cost is honest and should be
> stated in the guide: a monitoring dashboard reading statuses alone cannot see
> application errors, and the reason is that they are not errors of the
> transport.

Two things this paper has decided rather than asked, and will re-open if the
owner disagrees: `over_http` makes **no call** (§4 — A92's precedent, and a
login form constructs a client per mount), and the **envelope and the status
never disagree** (§7 — which is what makes S3 non-breaking for every vilan
client, measured).

## 13. What this does not do

- **Mirrors, handles and the reverse direction over HTTP.** They need a
  connection by construction (§5), and the leg that has one is the socket.
  Long-polling or SSE-as-a-reply-lane is not in scope and is not wanted: the
  socket already exists.
- **A REST surface.** `{mount}rpc` stays one POST route with a method name in
  the envelope. Per-method paths, path parameters, verbs and content
  negotiation are a different paper, and nothing asks for one — kolt's own
  hand-written leg was two POST routes with a JSON body.
- **OpenAPI, or any schema export.** The contract hash is the version check
  (§3, §4) and it is opaque by design. A readable schema is worth wanting the
  day a non-vilan client is a real customer.
- **Cookies.** std reads none and sets none, before or after this section.
- **The native leg.** Order 39's F18 builds `vilan-rt::http`; this section is
  about the JS server's POST route and the client that reaches it. The two meet
  when `std::rpc_server` runs natively, which is Order 40's.
- **B363.** §9.6c's `Option<RpcError>` stands on "the language has no unit
  literal", which the sibling paper `unit-literal.md` shows is false. The stub's
  return type is that paper's to move, not this one's; nothing in §1–§12 depends
  on which shape it has.
