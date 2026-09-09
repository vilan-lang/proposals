MERGED (five lanes, in the order they landed): rpc-smalls-31 (09d8e78a), mutself-31 (f53d999c),
reverse-31 (f139af8a; three append-append conflicts by hand — both new analyzer fns, both guide
sections in order, the anchor golden regenerated), handles-31 (4962ce93; the generator's route and
stub hunks composed by hand: `route_outcome` takes the replier, the notification arm ahead of the
handle arms; one missing brace cost a 122-red gate round before the amend), keyed-31 (cc2a49b1;
the channels test file folded by name, nine fns and five consts; one semantic clash git merged
textually — `Capability.dynamic` missing at the keyed-cell export — fixed by one field), and one
integrator docs commit (65af4be0: the interleave caveat, B287). Twenty-two commits, 26 files,
+6,074/−322. Ledger rows 407–411 assigned (next 412); CHANGELOG parity 283/283.

SEALED 2026-09-09 at 65af4be0: union 6872/6872 (22 skipped); clippy, the Windows cross-check, audit and fmt green
locally; CI GREEN on all eleven jobs (run 34383623175: ubuntu 16 and 16 min, Windows 19 and 20). The order's verdicts, against the owner's
framing that rpc was the last feature blocking a functional kolt: PER-CONNECTION MUTABLE STATE —
the generated dispatcher declares `mut self` and the routes capture the binding, so `&mut self`
writes the connection's instance in place (B272), and `mut self` is refused so the silent loss
cannot recur; the owner's `is_authenticated: bool` sketch compiles as written. RETURN-TYPED
HANDLES — `fun get_message(id): SignalCell<MessageBody>` reaches the client as a
`RemoteSource<MessageBody>` minted from a channel id, with the demand-decides release rule the
owner reversed R3 to: a hundred handles cost ten forwards, a released one is revoked and re-minted
from its origin with the cached value painted first, a never-leased one goes with its owner, and
the order added zero wire frames (A74). CLIENT-DECLARED FUNCTIONS — `[client_service]` on the
browser struct, `client = H` on the server's, a typed proxy through the connection, one reverse
lane, notifications only, and the receive loop no longer serializing a chunk's frames (A75, B281,
red-first). THE KEYED PATH — the delta cell takes a change from 12× growth over 10× rows to 1.3×,
and the client's apply path was the bigger half (A54); the keyed mirror is a `Source` (A55); the
keyed-map mismatch is refused at the attribute and 429 stands well-founded (A56). Eight closes
(A53 answered, A54, A55, A56, A74, A75, B272, B281); fifteen filed (B282–B287, A76–A81, E159, M60,
N70). Rulings the lanes left for the owner: the microtask hop's scope (dynamic-only as built, or
every mirror at the cost of four A25 pins); the keyed per-key hop; B287 (an awaiting `&mut self`
handler may now be interleaved — refuse or document); same-module handlers only; an awaitable ack
for a void method's forward stub; bare `[expose]` over a `KeyedCell` as the keyed channel.

PROCESS:
- No SendMessage in this build: a running lane cannot be steered. mutself-31's two items for
  reverse-31 became merge-time checks (the `mut self` guard on `[client_service]` came free
  through the shared arm; the interleave caveat was one integrator sentence). Rule: brief for
  the interaction up front, or plan a merge-time check.
- The merge validator refused a multi-file test target (`tests/inference/main.rs`); it accepts
  that layout now. Attribute refusals pin in vilan-core's `inference`, wire behaviour in
  vilan-cli's `service_layer` — in the mechanics block.
- A hand-composed generator block came out one brace short and the whole `[service]` macro
  failed to parse: 122 red, the HMR pins burning 300 s each. Rule: brace-count and smoke-compile
  (`--test examples`, 15 s) before the gates — the DOM-stub rule again.
- Two lanes added a field and a construction site to one std struct; git merged it textually and
  seven keyed pins went red on "`Capability` expects 3 fields". Rule: grep every `Name {` after a
  merge that touched a struct's shape.
- The lanes' scratchpad is shared: keyed-31 read mutself-31's probe file. Lanes namespace
  scratch by lane name.
- A heredoc terminator ends an `&&` chain; the GO commit went through with an INVALID spec once.
- One ssh timeout to GitHub on a proposals push, retried clean. No `git stash`, no pattern kills,
  no 1Password outage. notes31.md is the record.
