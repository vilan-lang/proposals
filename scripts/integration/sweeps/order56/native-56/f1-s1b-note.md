F1 S1b note (lane native-56, Order 56): the native WebSocket dial inherits A179's two cancel arms.
Today the rust backend refuses the host type `WebSocket` (rpc.vl :489), so `dial` (:1021) -> `dial_attempt`
(:1037) -> `dial_with_backoff` (:1119) never build natively; what is JS-only inside them is exactly the host
surface: `new_web_socket` + the seven `WebSocket` externs (transmit, transmit_bytes, set_binary_type,
set_on_message/close/error, close), `dial_promise` (a host Promise as a first-call-wins one-shot), and the
explicit-cancel arm's `on_abort(signal, handler) -> AbortHook` / `detach()` (`__dial_on_abort`, transformer.rs).
The backoff's `sleep_on(ms, signal)` is `__sleep`, which already lowers natively with an explicit signal, and
`dial_within` (:6560) is plain std (nursery + Timer + Task::race + n.cancel()) that already runs natively over
any dial (native_differential::a179_*) - so the DEADLINE arm comes for free once the dial exists and honours
the nursery's cancel, i.e. the deadline arm reduces to the explicit arm. The native dial needs: (1) in vilan-rt
a dependency-free ws:// CLIENT - non-blocking TCP connect registered as an executor `IoSource` (the stdin and
server sockets' pattern), the HTTP/1.1 upgrade request offering the subprotocol list (`vilan-rpc` +
`token.<credential>`), Sec-WebSocket-Accept check, RFC 6455 client framing (masked text/binary, close,
ping/pong) reusing the server half's frame codec where it lives, and the `Socket`-style callback surface the
seven externs map onto; (2) in the executor a callback hook on a `CancelSignal` - `on_abort(handler) ->
AbortHook` that runs at `Nursery::cancel` (at once if already aborted) and a `detach` that removes it - beside
today's park-only `cancel_waiters`; `close()` while CONNECTING must abandon the connect without a second
upgrade (undici's extra empty TCP connection is a JS-side quirk the native pins need not reproduce); (3) the
emitter mapping for the host type and the Promise one-shot. Pins: `dial_cancel.rs`'s six orderings run on the
native client too (stdin/held-listener orderings, the four plants), plus a native-server <-> native-client
differential. wss:// (TLS) is OUT: it needs a dependency ruling (R8, vilan-rt takes none). Sizing: M - one
Opus lane, about 600-900 lines of vilan-rt + ~100 emitter + pins; no analyzer or std surface change.
