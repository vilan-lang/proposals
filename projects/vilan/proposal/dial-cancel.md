# A dial that can be cancelled, and a dial with a deadline (A179)

- status: DESIGN 2026-11-02 (integrator; lane std-56 builds it; rides v0.54.0)
- item: A179 — `connect_with` can't be timed out: the dial has no deadline and ignores cancellation
- lineage: `std::task`'s nurseries (the race idiom), `rpc.vl` `dial_socket` /
  `dial_with_backoff` (A47 typed failures, A52 `Unavailable`), `time.vl` `sleep`
  (already passes the ambient `CancelSignal`)

## 1. The fault

`dial_socket(url, protocols)` opens a WebSocket and, through
`dial_with_backoff`, retries with a backoff sleep until it opens, the server
refuses, or the backoff gives up. Neither the socket open nor the retry loop
reads the ambient nursery's `CancelSignal`, so:

- `nursery(|n| Task::race([dial, sleep(ms)]))` waits for the hung dial at the
  nursery's join — the race idiom the task docs teach does nothing here;
- racing OUTSIDE a nursery leaves the dial running, and a socket it opens later
  is owned by nothing.

Kolt's connect loop shows "Can't reach Kolt" after 4 s but cannot abandon a
hung first attempt.

## 2. The mechanism

### 2.1 Door (a): the dial honours the ambient `CancelSignal`

`dial_with_backoff` reads `ambient_signal()` once at entry. While a signal is
present:

- the backoff's `sleep` already aborts on it (time.vl) — the loop must treat
  that abort as the end of the dial, not as one failed attempt;
- the socket open registers an abort listener on the signal: on abort the
  half-open socket is closed (`close()` on the host socket; the `onopen` /
  `onclose` handlers unhooked first so the close is not read as a drop to
  reconnect from) and the pending open settles with a new
  `DialFailure::Cancelled`;
- an abort that lands AFTER the socket opened is not the dial's business: the
  duplex is returned as today, and the nursery's cancel reaches the calls made
  through it as it does now.

`DialFailure::Cancelled` maps to `RpcError::Cancelled` in
`dial_for_service_with`, and to the sentence `"the dial was cancelled"` in
`connect_socket*`'s `Err(str)`.

### 2.2 Door (b): a deadline, on top of (a)

```
/// Run `dial` with a deadline: `Err(RpcError::Timeout)` when `ms` elapse
/// before it answers. The dial is cancelled (door (a)), so no socket it would
/// have opened later is left running.
export fun dial_within<T>(ms: i64, dial: (async || Result<T, RpcError>) context ambient_nursery): Result<T, RpcError>
```

Built on `nursery`: the body spawns the dial and a `sleep(ms)`; `Task::race`
over the two; whichever wins, `n.cancel()` the other; a timer win answers
`Err(RpcError::Timeout)`; a dial win answers its result. Nothing is generated:
it wraps `connect`, `connect_with`, `connect_socket` and any hand-written dial
alike — `dial_within(4000, || KoltClient::connect_with(url, codec, protocols))`.

Natively the dial is the Rust runtime's; the same two arms (`Cancelled`,
`Timeout`) exist there and `dial_within` is the same std code over the native
nursery. If the native socket open cannot be aborted mid-connect, the lane says
so: the deadline still answers on time (the race), and the abandoned open is
closed when it settles.

### 2.3 Why two variants

`Timeout` is a judgement about TIME ("retry later, say so"), `Cancelled` about
the CALLER's intent (nothing to report). A UI shows one and not the other.
Both are new arms on `RpcError`: a `match` over every arm gains two (kolt
matches by arm with a fallthrough; the lane's estate census says whether any
exhaustive match exists in std, the website, the corpus or kolt's copy).

## 3. Not done here

- No timeout option on the generated client (`connect_with_timeout`): the
  wrapper composes with every dial and the generator stays as it is.
- Cancelling an in-flight CALL (`client.method()`) is already the nursery's:
  unchanged.

## 4. Pins

1. A dial against a port nothing listens on, inside a nursery cancelled after
   the first backoff: the dial answers `Cancelled` promptly (the harness's own
   sequencing: the cancel is issued from a task that waits for the first
   attempt's failure to be observed, never a sleep) — both backends.
2. A dial against a listener that accepts TCP and never completes the upgrade
   (a raw `net` server the test holds open), cancelled: the half-open socket is
   closed, the dial answers `Cancelled`, the server sees the connection close.
3. `dial_within(ms, …)` against the same held-open listener answers
   `Err(Timeout)`, and the listener sees the close (no socket left running).
4. `dial_within` around a dial that succeeds answers `Ok` and the timer does not
   fire later (no stray cancel of the duplex: a call through it after the
   deadline would have passed succeeds).
5. An abort that lands after the socket opened leaves the duplex `Connected`.
6. The two new `RpcError` arms print and `Debug`-render as the others.

## 5. Docs

`docs/std/rpc.md` (the client section): cancellation and `dial_within`;
`docs/std/task.md` if it names `dial` among the IO wrappers that bridge the
signal; CHANGELOG feature entry (A179), one bold head.

## 6. Owner questions

- Q1: `dial_within` as a free function over any dial (rec) vs a generated
  `connect_with_timeout`. Rec: the free function.
- Q2: `RpcError::Timeout` and `RpcError::Cancelled` as two arms (rec) vs one.
