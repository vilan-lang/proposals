# Order 31 — the rpc order (drafted 2026-09-09, off vilan next @c3ed9239)

The owner's focus: "improving the rpc system — the last feature blocking a functional
system in kolt." Design: `proposals/projects/vilan/proposal/transport-rpc.md` §9 (read it
whole before touching anything; §9.5 lists the rulings). Rulings in force (owner,
2026-09-09): R1 `[service(X, client = H)]` + `[client_service]`; R2 `[expose]` stays as
sugar, `expose:` hash entry verbatim; **R3 REVISED — demand decides (below)**; R4
notifications only in v1, the receive-loop fix lands now; R5 no `bind_each` sibling, the
keyed `Source` impl IS built; R6 refuse the keyed-map mismatch at the attribute, keep 429;
R7 a source-returning method is a getter by declaration; R-A38b option (a) — the
generator honours `&mut self` — plus `mut self` REFUSED on an `[rpc]` method.

**R3 as ruled (replaces §9.5's R3 and §9.2's `Release(channel)` paragraph).** Demand
decides the server lifetime of a DYNAMIC channel; no new frame:
1. Client: lease 1→0 defers to the ambient turn's settle (shipped, `RemoteSource::release`
   → `at_settle`), and THEN takes one microtask second look before sending `Unsubscribe`
   (`flush_close` hops `queue_microtask` once and re-checks `closing`). A dispose→mount
   anywhere inside one macrotask sends nothing. Same for the keyed lease.
2. Server: `Unsubscribe` on a DYNAMIC channel (one minted inside a reply — mark the
   `Capability` at export) is `revoke`: forwards stopped, capability dropped, source
   freed. `[expose]` field channels stay demand-only (A41: they have no origin and are
   re-attached positionally).
3. Client re-acquire (0→1) on a dynamic mirror whose channel was released re-issues its
   `origin` call, rebinds to the fresh channel and subscribes (the `rebind` path); the
   cached last value stays as the seed until the first `Update`.
4. Owner hook: a dynamic mirror minted under an ambient owner (the owner-OPTIONAL read,
   `register_with_owner`'s shape) that never reached one lease sends its release when that
   owner disposes. No owner → lives with the connection (documented).

## Mechanics (every lane)
- Worktree `vilan/.claude/worktrees/<lane>` branched from `origin/next` (c3ed9239); push
  the branch; NEVER touch the main checkout; NEVER `git stash`; kill only PIDs you
  recorded, never by pattern; kolt (`~/code/kolt`) is READ-ONLY and nothing is copied
  from it into vilan.
- One commit per item, message = the CHANGELOG entry's first sentence; CHANGELOG entry
  under the right family with its marker (`<!-- family: breaking|miscompile|fix|feature|
  performance|tooling|diagnostics -->`); the parity gate is `--test release_scripts`.
- Diagnostics: a new message is a ledger row written `NEW` in
  `crates/vilan-cli/tests/diagnostics-ledger.tsv` (the integrator numbers; next id 407)
  and a prose row is NOT yours. A message whose FIRING changes (not its text) means you
  run `-p vilan-lsp` too — the quickfix and steer pins live there (Order 30's lesson).
- Shared test files (`service_layer.rs`, `reactive_channels.rs`, `reactive_lifetimes.rs`,
  `rpc_http.rs`, `ui_rows.rs`): ADD whole new `fn`s only; never edit an existing fn or a
  shared const — if you must, say so in the report with the exact fn name. New test
  BINARIES are welcome (add to `.config/nextest.toml` if the suite lists them; mirror in
  `build_hooks` if that table exists for them).
- Tests: `cargo nextest run -p vilan-cli --test <name>` targeted, never plain `cargo
  test`; verify binary names with `ls crates/vilan-cli/tests/` (`corpus` is the
  corpus binary; `docs`, `release_emission`, `module_resolution` are vilan-core). The
  whole `-p vilan-core` run is the merge gate, not yours, but
  `-p vilan-core -E 'test(every_std_module_is_clean_under_full_scan)'` IS yours (std
  edits). Building while nextest runs overwrites live test binaries — iterate with
  lib-only `cargo build`. Clippy `--all-targets -D warnings` and `cargo fmt --all --check`
  before every push.
- A parser rule statement added anywhere bumps `RULE_STATEMENT_SITES`.
- Perf claims: CPU time (`getrusage`) or callgrind Ir + loadavg at measurement, never
  wall; sub-1% claims need a profile diff.
- Report (final message): per item — commit sha, what landed, the pins (names), numbers;
  FINDS (pre-existing bugs, design gaps) as candidate items with evidence; OPEN Qs for the
  owner; anything you could not finish and why. Corrections to this brief are welcome and
  expected — say what was wrong.
- Model: Opus. The lane's own gate list is per lane below.

## Lane handles-31 — TOP: return-typed signal handles (§9.2, plain half) + R3 as ruled
Items: A-handles (new, the integrator files it as the order's top item) + R3 + R7 + the
`origin` replay + the owner hook; A53 is closed by this (answered, not built — the
generic-struct `[service]` refusal STAYS).
Build:
1. Generator (`std/src/rpc.vl` ~3126–3160 surface, ~3302 stub): an `[rpc]` method whose
   return type is `SignalCell<T>` / any `S: Source<T>` / `Option<SignalCell<T>>` renders in
   the stub as `Result<RemoteSource<T>, RpcError>` (`Option<RemoteSource<T>>` for the
   option form) and in the CONTRACT SURFACE as the MAPPED type
   (`get_message(MessageId)->RemoteSource<MessageBody>;`). The `expose:`/`keyed:` entries
   are untouched — PIN: a service with no handle return hashes BYTE-IDENTICAL to the
   shipped hash (compute it at c3ed9239 and freeze it in the pin); PIN: a handle return
   changed to a plain value moves the hash. `T: Wire` is required — a refusal in the
   attribute's vocabulary when it is not (ledger NEW row). DO NOT touch the dispatcher's
   receiver/cell shape or the route's `self.{method}(…)` call site (mutself-31 owns them);
   you own the return-type rendering and the reply path.
2. Reply path: the route for such a method exports the returned source through the
   connection's `ReactiveServer::expose` (`rpc.vl:1415`) with the capability marked
   DYNAMIC, and puts the `ChannelId` (i32) on the wire as the reply. Find how a route
   reaches the connection's `ReactiveServer` (`session_of(connection)`, `rpc.vl:1311`;
   `register_session`, `rpc_server.vl:497`) — the route needs the connection id; say how
   you threaded it (the `Connection` the factory holds is the honest source).
3. Client: the stub mints a `RemoteSource<T>` from the reply's channel with
   `origin = (method name, the argument describers)` — the pair `call` takes
   (`rpc.vl:1101`). `ReactiveClient::source(channel)` (`rpc.vl:1932`) is the runtime
   escape it subsumes; keep it for origin-less hand-wired mirrors.
4. R3 as ruled, all four points. Server: `"Unsubscribe" => self.stop(channel)`
   (`rpc.vl:1649`) becomes `revoke` for a dynamic channel. Client: `flush_close`'s
   microtask second look (`reactive.vl:59` `queue_microtask` is the primitive; do NOT
   change `at_settle`'s inline rule for everyone — the hop is the mirror's). Re-acquire on
   a released dynamic mirror re-issues `origin` (async: the acquire stays sync, the
   re-mint settles the rebind). Owner hook via the owner-optional read.
5. Reconnect: `reattach_mirrors` (`rpc.vl:2878`) re-issues each WATCHED dynamic mirror's
   origin after the positional `__attach` rebind; `invalidate_dynamic` (`rpc.vl:2049`) is
   retired for generated mirrors, kept for origin-less ones.
6. Docs: the rpc guide page gets the handle section (mapping table, lease rule, R7's
   "must be safe to re-run" sentence, the owner-hook sentence); transport-rpc.md is the
   integrator's (proposals), not yours — put the paper-facing corrections in the report.
Pins (new fns in `reactive_channels.rs` / `service_layer.rs`, red-first where a plant
exists): (a) round trip: `get_message(id)` → the mirror seeds from the server's first
Update; (b) LAZY: 100 handles minted, 10 leased → the server's `live` holds 10 forwards;
(c) same-turn dispose/rebuild → 0 frames; (d) same-MACROTASK cross-turn remount → 0
frames (RED without the microtask hop — plant: remove the hop); (e) lease-zero past the
hop → the server's `sources` no longer holds the channel; a later acquire re-mints (the
getter ran twice, the mirror rebinds, the value is right, the seed painted before the
round trip); (f) owner dispose releases a never-leased handle; (g) reconnect replays a
watched dynamic mirror (the unix reconnect pin in `reactive_channels.rs` is the model);
(h) the two hash pins; (i) `[expose]` field channel survives an Unsubscribe (A41's pin
stays green — it is the control). Exhibit: kolt's shape — `get_messages(conversation,
amount): List<MessageId>` + `get_message(id): SignalCell<MessageBody>` in a pin AND in
`vilan/examples/rpc` (one method; keep its README honest).
Gates: `-p vilan-cli --test reactive_channels --test service_layer --test
reactive_lifetimes --test rpc_http --test corpus --test release_scripts`; the std
full-scan test; `-p vilan-lsp` (the attribute's diagnostics change firing).
Family: feature (the handles), fix (nothing), diagnostics (the Wire refusal).

## Lane reverse-31 — client-declared functions, notifications only (§9.3, R1, R4)
Items: A-reverse (new; the integrator files it) + the receive-loop fix (a B item the
integrator files: "two frames coalesced into one read are serialized by the receive
loop — an awaiting handler holds the second").
Build:
1. `[client_service]` on a struct in the browser entry: generates `dispatcher()` +
   `contract_hash()` through the SAME generator (direction-agnostic) and a
   `<Name>Proxy` type with one method per `[rpc]` fn, each `sync`, returning nothing —
   v1 is notifications: a `[client_service]` method with a return type is REFUSED
   ("notifications only in v1 …", ledger NEW row).
2. `[service(KoltClient, client = KoltHandlers)]`: the server's contract surface appends
   `client:ping()->void;` per handler method (PIN: a service without `client =` hashes
   byte-identical; one with it moves — and the client side computes the SAME string).
   `client = X` where X lacks `[client_service]` is refused (ledger NEW row).
3. `Connection::client()` returns the typed proxy (`rpc_server.vl:112`); the attribute
   names the handler type so `connection.client()` types without an annotation — say
   how (a generated `impl Connection` accessor named per service, or a typed field the
   factory closure receives; pick, justify). The service struct holds it as a field;
   `self.client.ping()` sends text `s:<id>:<payload>` / binary tag `0x73` (`'s'`) on the
   server's end of the socket, id unused (0) in v1. `DuplexEnd`/`SocketDuplex` grow the
   send only — no pending table (R4).
4. Client router (`route_socket_frame`/`route_socket_bytes`, `rpc.vl:633/655`): `s:` →
   the handler struct's dispatcher, run under `turn(FlushPolicy::AtEnd, …)` like a
   server handler. The handler INSTANCE reaches the client at connect — recommend
   `KoltClient::connect_with(url, codec, protocols)` gaining a `.with_handlers(instance)`
   (or a fourth argument); the contract check at `__contract` covers both directions.
   An old client drops unknown `s:` frames silently (`rpc.vl:632/654`) — PIN: the hash
   mismatch refuses the connection BEFORE any `s:` frame is sent.
5. THE RECEIVE-LOOP FIX (present-tree hazard, prerequisite of v2's awaited calls):
   `rpc_server.vl` ~1117–1176 awaits each event's `respond` before parsing the next of
   the same chunk. Change: parse the chunk into its events, START every handler's turn,
   let the event loop interleave; per-handler turns settle independently. RED-FIRST PIN:
   two frames coalesced into one read where handler 1 awaits a `Shared` flag that only
   handler 2 sets → today handler 2 never runs (bound the wait in retries/CPU, not wall
   — M27's rule); after: both complete. Order of REPLIES is not promised — say so in the
   guide.
6. Guide: §9.3's three sentences (the router never blocks on a handler; a held turn is
   per handler; an awaited server→client call is a suspension point — v2) into the rpc
   docs page; the `[client_service]` section with the kolt exhibit: `session_revoked()`.
Pins (new fns in `service_layer.rs`): the notification round trip (server calls
`self.client.ping()`, the browser-side handler runs under a turn and writes a signal the
pin reads); the two hash pins; the refusal pins; the receive-loop pin; a peer-to-peer
struct (both attributes) compiles and both directions work.
Gates: `-p vilan-cli --test service_layer --test rpc_http --test reactive_channels
--test corpus --test release_scripts`; std full-scan; `-p vilan-lsp`.
Family: feature; fix (the receive loop); diagnostics.

## Lane mutself-31 — B272 / R-A38b(a): the generator honours `&mut self`
Build: the generated dispatcher holds the per-connection instance in a cell
(`Shared<S>`) and each route whose method takes `&mut self` re-borrows it mutably for
the call (`rpc.vl:3188–3195` the routes, `:3246` `fun_of("dispatcher")`); a method
taking `self` is unchanged; `mut self` on an `[rpc]` method is REFUSED at expansion in
the attribute's vocabulary, span on the METHOD ("an `[rpc]` method's `mut self` copy is
discarded after the call — write `&mut self` to mutate this connection's instance, or
hold the state in a `Shared<T>` field"; ledger NEW row). The struct-span diagnostic B272
records disappears with the refusal of the case that produced it — say so. You own the
dispatcher's receiver/cell shape and the route call site; DO NOT touch return-type
rendering or the reply path (handles-31 owns them).
Pins (`service_layer.rs`, new fns; the existing
`a_mut_self_rpc_mutation_is_lost_where_a_shared_field_survives` at :2421 is the lane's
to REPLACE — say its new name): `&mut self` write survives to the next call on the same
connection and is invisible to the other connection; `mut self` refused (a must-fail
pin); the owner's sketch (`is_authenticated: bool`, `login(&mut self, …)`) compiles and
works; the factory pin at :864 stays green.
Docs: the rpc guide's "mutable session state" paragraph (Q9's spelling) — `&mut self` is
the idiomatic receiver, `Shared<T>` for state a stored callback must reach.
Gates: `-p vilan-cli --test service_layer --test rpc_http --test corpus --test
release_scripts`; std full-scan; `-p vilan-lsp`.
Family: fix (B272), diagnostics.

## Lane keyed-31 — DROPPABLE: A54 `KeyedCell<K, T>` + A55's keyed `Source` impl
Build: (1) `KeyedCell<K: Hashable + PartialEq, T: Keyed<K> + PartialEq>` in
`std::reactive` (or beside `KeyedSource` in rpc.vl — pick, justify): `insert`, `remove`,
`update(key, |&mut T|)`, `set(list)`, `get`, a `Source<List<T>>` view for local bindings;
its writes produce `Delta<K, T>` ops DIRECTLY so `expose_keyed_*` (`rpc.vl:1441–1464`)
forwards ops without `keyed_diff` (`rpc.vl:1779`) — O(1) per change vs O(N).
`[expose(keyed = K)]` over a `KeyedCell<K, T>` field takes that path; over a
`SignalCell<List<T>>` it keeps the diff (unchanged). The RETURN mapping
(`KeyedCell` → `KeyedSource` in a reply) is NOT this order's — it needs handles-31's
mapping machinery; leave it and say so. (2) A55: `impl KeyedSource<type K, type T> with
Source<Option<List<T>>>` on the shipped counted lease (`acquire`/`release` at
`rpc.vl:2562/2581`), no second mechanism; R5: no `bind_each` sibling. (3) Measure: A54's
numbers (1,000 rows 1.08 ms/change/connection, 10,000 rows 8.83 ms, `getrusage`) against
the cell — report the ratio at both sizes with loadavg; a perf pin with the RATIO (4×
rows < 8× cost or tighter), not a wall bound.
Pins (`reactive_channels.rs`, new fns): a keyed cell's insert/remove/update reach the
client as element-grained patches (frame count per change = 1); the keyed mirror binds
through `Source` (`bind_each(keyed.or([]), …)` shape); the diff path unchanged for a
`SignalCell<List<T>>` field (control).
Gates: `-p vilan-cli --test reactive_channels --test service_layer --test corpus --test
release_scripts`; std full-scan.
Family: feature (A54, A55), performance.

## Lane rpc-smalls-31 — A56 (R6)
Build: (i) `[expose(keyed = K)]` over a `SignalCell<Map<K2, V>>` whose written `K`
disagrees with `K2` is REFUSED at the attribute, in the field's vocabulary
(`rpc.vl:3086–3098` — the macro holds both types; ledger NEW row; a "must fail" pin +
the agreeing form still compiles); (ii) `authorize_timeout` keeps 429 — write the
rationale at the site (`rpc_server.vl`, the A48 comment): 503 is the app's judgement
(`Reject::Unavailable`), a std timeout is std's limit; a doc line in the rpc guide's
status table. Also: sweep the rpc guide page for any sentence §9 made false (e.g. "a
dynamic channel is re-run by the app" — A41's old escape) and correct it; list what you
changed.
Gates: `-p vilan-cli --test service_layer --test rpc_http --test corpus --test
release_scripts --test docs`(vilan-core: `-p vilan-core --test docs`); `-p vilan-lsp`.
Family: diagnostics, fix.

## Ownership map (conflict avoidance in rpc.vl)
- Generator return-type rendering (surface ~3142, stub ~3302) + reply path + client
  mint + R3 client/server + reattach: handles-31.
- Generator dispatcher receiver/cell + route call site (~3188–3195, ~3241–3248) +
  `mut self` refusal: mutself-31.
- Contract-surface `client:` entries + `[client_service]` + proxy + `s:` lane + router +
  `Connection::client()` + receive loop (rpc_server.vl): reverse-31. (The surface
  builder at ~3126–3160 is touched by handles-31 AND reverse-31 — different lines; the
  integrator resolves; each lane keeps its change to its own entry kind.)
- `expose_keyed_*` / `keyed_diff` / `KeyedSource` impl / new `KeyedCell`: keyed-31.
- `check_expose_fields`' keyed-map arm (~3086–3098) + `authorize_timeout` comment + guide
  sweep: rpc-smalls-31.
Landing order (integrator): mutself-31 → rpc-smalls-31 → keyed-31 → reverse-31 →
handles-31 (the largest, merged last over the generator changes; hand-resolve the
surface builder if both touched it). Docs-touching merges regenerate the mdBook golden
(merge_lane does it).

## At the sweep (integrator, proposals)
- transport-rpc.md: §9.1 hole CLOSED (B272), §9.2/§9.3 marked BUILT with the deviations
  (R3 as ruled replaces `Release(channel)`; the keyed return mapping deferred), §9.5
  rulings recorded with the owner's date, §12 slice 7 added, §14 Q9 amended.
- Close: A53 (answered), A54, A55, A56, B272, the receive-loop B; A48 tombstone note.
- Kolt migration at the owner's word: the three TODOs (store.vl:93, :102–109, :96–99
  stays) + Order 30's 23 recipe errors.
