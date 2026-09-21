# Reactive turns — flush is scoped, not global (A6 redesigned)

Status: **SHIPPED 2026-07-09** — `get_safe` (§5.1), the Turn machinery +
server boundary (§5.2–5.3), the `std::ui` boundary, and CONTINUATION
SETTLING all landed the same day; §5.5's optimistic-reconcile follow-on
remains recorded. The `AtSuspension` "async-lowering hook" turned out
unnecessary: for an async extent, `turn`'s own drain fires at the body's
first suspension (the body returns its promise there), and a write landing
AFTER the turn settled schedules one **microtask drain** — each continuation
segment settles as one coalesced wave (per-set settling would have
re-glitched multi-input observers), with no compiler insertion at all. The
policies therefore CONVERGE for async extents in v1 (`FlushPolicy` states
intent and keeps the API stable). **`turn_async` + `optimistic` shipped
same-day**, closing §5.5: `turn_async(body)` is the true held-across-await
transaction — its body is `async`-typed (J2 SHIPPED 2026-07-10: `async || T`
closure types make calls through the value implicitly awaited; the original
spawn-then-flatten workaround is gone), holds every notification (the turn never
reaches `settled` mid-flight, so the continuation microtask never fires
early), and settles once — same-signal writes coalesce to their final value.
`optimistic(signal, value, commit)` is the reconcile lifecycle: paint now,
await the commit, then confirm or roll back, returning the outcome. **A6 is
COMPLETE**; the cadence split for directly-awaiting `turn` bodies remains
the one recorded refinement.

**2026-08-04 — §5.5's follow-on now has a record of its own:
`optimistic-lifecycle.md`** (A14). `optimistic` stays exactly as shipped and
is still the one-shot spelling; what it could not do — being a free function
over a bare signal — is hold state, so it has no observable pending or
rejected status and it corrupts the cell when two writes overlap. An
`Optimistic<T>` cell wraps the signal and adds both. §5's plan item 4 (the
`AtSuspension` optimistic-paint corpus shape) and item 5 are closed there,
Rust-side rather than in the corpus: the corpus gate byte-compares emitted
JS without running it, so ordering cannot be pinned in a `.vl` program.

**2026-07-18 — `turn_async` MERGED INTO `turn`** (post-v0.9.0, user's call):
adaptation (async-polymorphism.md Part A) made the pair redundant — `turn`'s
body is now a plain `(|| T) context turn_scope` parameter, so a synchronous
body selects the atomic instance and an awaiting body adapts into exactly
the old `turn_async` semantics (the drain awaits the body's whole chain).
The split existed only because (a) pre-adaptation, asyncness had to be
declared on the parameter type, and (b) the directly-applied-closure await
hole (fixed in Part B slice 2) made an async body through `turn` mis-drain.
`batch` keeps its `sync` fence deliberately: its join-the-ambient arm has
unresolved semantics for async bodies (the outer extent would settle while
the joined body still runs — drain-affinity territory). The generic-void
edge (a `|| T` body at `T = void` must adapt, not spawn) is pinned.

Three implementation findings amended the design:

1. **Injected bodies, not captured** (`turn` AND `batch`): a batch body is a
   literal at the call site, created BEFORE the extent exists —
   capture-at-creation would hand it the caller's (usually absent) turn. Both
   enter through `run`, which supplies the turn to the deferred literal;
   `batch`'s join arm re-establishes the CURRENT turn (same queue, outer
   settle).
2. **Drain affinity — the one runtime device.** A notify fired during a
   drain may `set` (a derived recomputing), but notifiers are closures
   created anywhere; compile-time capture cannot hand them the draining
   turn. A `set` with no ambient turn joins the currently draining one
   (a module-level stack, pushed/popped around the synchronous drain loop —
   it can never cross an `await` or interleave extents). This is what keeps
   cascades coalescing (the glitch-free dedup) inside their own settle.
3. **The boundary must sit where user code is called DIRECTLY.** Stored
   handler closures capture at REGISTRATION (nothing), so wrapping an outer
   dispatch in a turn cannot reach them. `[service]`-generated routes wrap
   their bodies in `turn(AtEnd, ..)` — the generated literal contains the
   direct call into the user's handler method, so the turn threads
   compile-time into real handler code. MANUAL `dispatcher.on(|req| ..)`
   handlers self-`batch` (one line, documented). **The `std::ui` boundary
   SHIPPED the same way** (same-day follow-up): the host stores only a plain
   ADAPTER — `View.on` takes a clause-typed handler and registers
   `|| turn(AtSuspension, || handler())`, so each DOM dispatch (and each
   `bind_value` write-back, and `mount_root`'s initial build) runs in its
   own turn with zero user ceremony. Enabled by two B15 extensions shipped
   with it: clauses on `let` annotations (a named injected closure —
   forwards, `run`-body, and direct calls all work), and clause ADOPTION —
   an unannotated closure-literal binding passed into a clause position
   adopts the clause (`let add = || ..; .on("click", add)`, the idiomatic
   pattern both example apps already used).

Supersedes A6's original sketch ("auto-`flush` on the next microtask") — the
microtask hook dissolves into boundary-established turns. Prerequisite
sub-slice: `get_safe` (ambient-owner.md §2.1's recorded tail — shipped with
strict/safe flavors on the threading pass).

## 0. The problem

Today's scheduler (`std/src/reactive.vl`) is one module-level value: a single
`pending: Shared<List<Subscriber>>`. `set` commits its value immediately and,
inside a `batch`, defers only the *notification*; `flush()` drains the global
queue to quiescence.

The failure, found in review before A6 could bake it in:

> An HTTP server has two requests in flight from two clients, each mutating
> signals its own client subscribes to. Request A finishes and flushes —
> and drains **B's** pending notifications too, pushing B's half-done state
> to B's subscribers mid-request.

Three observations sharpen it:

- **It is latent today only by accident.** A handler that never awaits runs
  to completion, so no second request can interleave with its batch. The
  moment handlers suspend (any I/O between writes), interleaving begins.
  A6 exists precisely to let handlers span awaits — the original A6 sketch
  (a global microtask auto-flush) makes the failure *routine*: whichever
  microtask fires first drains every request's queue.
- **Global flush is non-composable even single-client.** Any library calling
  `flush()` mid-operation publishes a stranger's half-settled state.
- **The diagnosis:** the global queue conflates *cadence* (when
  notifications settle: microtask, batch end) with *identity* (whose writes
  settle together). `batch` gets away with it synchronously because a
  synchronous extent has one implicit owner; suspension breaks exactly that
  implication.

## 1. The model: a turn is the ambient transaction

A **`Turn`** owns a pending-notification queue and a flush policy. It is
established for a dynamic extent through `std::context` — the same machinery
as `owner_scope`, with the same property that makes it correct here: hidden
parameters are captured by continuations, so **a request's turn follows its
own awaits while interleaved requests keep theirs** (proven by the A5
substrate probes). This is the compile-time, statically-verified equivalent
of the `AsyncLocalStorage` pattern Node SSR frameworks use against this same
global-singleton bug class.

```vilan
turn_scope: Context<Turn>

// Establish a fresh turn for `body`'s dynamic extent (B15 injected closure).
fun turn<T>(policy: FlushPolicy, body: (|| T) context turn_scope): T

// Drain the AMBIENT turn's queue to quiescence (per-turn wave budget).
fun flush()

// Join the ambient turn if one is established (a no-op wrapper — preserving
// today's nested-batch outermost-flush semantics exactly), else a fresh
// at-end turn. `batch` dissolves into the model instead of being a sibling.
fun batch<T>(body: || T): T
```

- `Signal.set` reads the ambient turn via **`get_safe`**: established →
  enqueue the notification there; not established → notify inline (today's
  non-batch behavior, unchanged — top-level init and timers stay legal).
- `flush()` drains only the ambient turn. Request A can no longer touch
  request B's queue *by construction*.
- Dedup — "one settle fires each subscriber once", the glitch-freeness —
  becomes per-turn (a subscriber may be pending in two turns at once when a
  shared signal changes in both; dedup keys on `(turn, subscriber)`).
- The drain-wave budget (cascade cutoff) moves from the global scheduler to
  the turn.

## 2. Cadence: flush policy rides the turn

The original A6 wanted an auto-flush so users stop hand-writing `batch`.
Turns subsume it without any global hook, because **boundaries** establish
turns:

| Boundary | Establishes | Default policy |
|---|---|---|
| `std::ui` event listeners (`on_click`, …) | a turn per event dispatch | `AtSuspension` |
| `mount_root` / `comp` initial run | a turn per mount | `AtSuspension` |
| `serve_connected` / RPC dispatch | a turn per request/message | `AtEnd` |
| explicit `turn(policy, body)` | opt-in | caller's choice |

Policies:

- **`AtSuspension`** — flush the turn's queue at each `await` boundary and
  at extent end. The UI mental model: optimistic paint before the await,
  settle again after. (This is the "async turns" half of A6's name: each
  synchronous segment between suspensions settles as a unit.)
- **`AtEnd`** — transactional: one settle when the extent completes. The
  server default: a request's subscribers see its writes as one wave.

Writes with no ambient turn notify inline — so code that never opts in
behaves exactly as today, and the "forgot to batch" problem disappears for
UI code because the *boundary* owns the turn, not the user.

## 3. Interactions with the shipped model

- **`owner_scope` is orthogonal** and composes: a closure needing both
  writes `(|| void) context (owner_scope, turn_scope)` — the multi-context
  clause shipped with B15.
- **C3/E3 (view-invalidation) is satisfied by construction**: a `Turn` is an
  ordinary value (`Shared`-backed queue); context threading carries values,
  never views, across awaits.
- **`ReactiveServer`/SSE realtime sync is the live testbed**: its dispatch
  is exactly the boundary that must establish a per-session turn, and the
  P6 realtime example is the regression program for the two-clients
  scenario.
- **Eager value commit is unchanged** — see the honest limit in §4.

## 4. The honest limit: notification isolation, not value isolation

`set` commits the value immediately; turns isolate the *notification waves*.
For the motivating scenario — each client subscribed to its own signals —
that is a complete fix: B's subscribers are simply not in A's queue. But two
turns writing the **same shared** signal still interleave at the value
level: a subscriber notified by A's flush reads whatever B has committed so
far. That is inherent to shared mutable state under eager commit.
Alternatives recorded and *not* taken here: per-turn value staging
(copy-on-write signal values with commit-on-flush) is a real cost and the
wrong default for signals that are *meant* to be shared; the
optimistic-write → `await` → reconcile lifecycle (A6's second half) is the
application-level answer and builds ON turns as a separate slice.

## 5. Implementation plan

1. **`get_safe`** (the A5 tail, ambient-owner.md §2.1's sketch): the
   possibly-established context read. The hidden parameter for
   `get_safe`-reachable regions carries `Option<T>`; strict-`get` regions
   keep the bare flavor and the existing coverage fence; covered→safe
   boundaries `Some`-wrap; safe-only roots synthesize `None`. Pins for the
   flavor split, the boundary wrap, and the fence staying intact for
   strict reads.
2. **`Turn` + `turn_scope` + policies in `std::reactive`**: per-turn
   queue/dedup/budget; `set` routes via `get_safe`; `flush` drains the
   ambient turn; `batch` rewritten as join-or-create (its existing corpus
   behavior must hold byte-for-byte at the OUTPUT level — the goldens will
   change with the std source and are regenerated only after run
   verification, per the standing discipline).
3. **Boundaries**: `std::ui` event listeners and `mount_root` wrap in
   `AtSuspension` turns; `serve_connected`/RPC dispatch wraps in `AtEnd`.
4. **The isolation regression**: a corpus program with two interleaving
   async tasks, each writing its own signal and flushing — asserting each
   subscriber fires only on its own turn's settle (the two-requests
   scenario, distilled); plus the `AtSuspension` optimistic-paint shape.
5. **A6's remaining half** (optimistic-write → reconcile) stays a recorded
   follow-on riding turns. *Closed 2026-08-04 — `optimistic-lifecycle.md`.*

## 6. Out of scope

- Per-turn value staging (§4 — recorded, not taken).
- Cross-turn ordering guarantees for shared signals (last-flush-wins is
  accepted and documented).
- Scheduler fairness beyond the per-turn wave budget.

## 7. Order within a wave (A110 door 2)

### 7.1 The rule

> Within one settle, **derivations run to a fixpoint first; then effects run in
> ascending subscriber id.**

Two halves, and both are needed:

- **Derivations first, to a fixpoint.** A `map`/`combine`/`flatten`/`selector`
  subscriber exists to publish a value, not to act on one. Running every derivation
  the wave can reach — and every derivation those writes reach, until nothing new is
  enqueued — before any effect runs is what makes an effect see a *settled* graph.
  This is the glitch-freeness `enqueue`'s dedup already promises, extended from "each
  subscriber fires once" to "each subscriber fires once, on final values".
- **Effects in ascending subscriber id.** `fresh_id` is monotonic and module-level
  (one counter for the program), and a parent form's effect is created when the
  parent is placed, before anything its render closure creates. So ascending id
  **is** parent-before-child, with no owner-depth bookkeeping anywhere.

### 7.2 Why today's order is wrong, and for two different reasons

`drain` takes the pending queue out as a *wave* and runs it in **subscription
order** — the order the subscribers were attached to the cell that fired. Two
failures follow, and they are the two faces A110 filed.

**Face 1, in a turn: child settles before parent.** The shape is the one the guide
should teach — project the coarse key so the outer form does not rebuild on every
navigation:

```vilan
{swap(get_route().map(shell_of), |shell| match shell {   // OUTER: coarse key
  Shell::Login => ..,
  Shell::App => <div>{swap(get_route(), |route| ..)}</div>,  // INNER: fine key
})}
```

Both forms now stand on one source, and the outer reaches it **through a
derivation**, so the outer is always one wave behind the inner. `route`'s subscribers
are `[the map's, the inner form's]`; wave 1 runs both, the map's write enqueues the
outer effect for wave 2, and the inner form builds *now* — for a value the outer is
about to tear down. A wasted build, and a panic if that arm is `unreachable`.

`probe_a110_door2_nesting.vl`, which is `place_swap`'s shape reduced to the
scheduler, on today's std:

```
outer: shell=0 — dispose the old boundary, render the new one
--- one set that CHANGES the shell, inside a turn ---
  INNER fired with 200 (live)
outer: shell=1 — dispose the old boundary, render the new one
inner boundaries built=3 inner fired live=2 inner fired dead=0
```

The inner fires, live, with a value its enclosing form is about to exclude, and only
then does the outer tear it down.

**Face 2, outside a turn: a disposed observer fires.** `SignalCell::notify`'s inline
arm iterates `self.subscribers.read()` — a snapshot. The map's subscriber runs first
and cascades depth-first: derived → outer effect → the inner boundary is disposed and
its subscription removed from the *list*, but the snapshot still holds it, so it is
called next. `probe_a110_wave_order.vl` case 1:

```
inline: outer disposes the inner boundary
inline: INNER fired with 200 (boundary disposed: true)
```

**Face 2 is not door 2's.** It is a leak — a `swap` then builds a subtree under a
fresh `Owner` that the boundary's `defer` has already run and will never dispose, and
`open_row` inserts before an anchor `region.close()` already removed — and it is
fixed by door 1 (a per-subscriber liveness flag that `Subscription::dispose` lowers,
skipped by both the inline loop and `drain`'s wave loop), which lane reactive-38
built in Order 38 and which changes no ordering. This section is about face 1 only.

### 7.3 Why ascending id is the right order — and what A110's own probe does not show

The claim is that ascending subscriber id is parent-before-child. It is, and the
measurement is one line:

```
parent effect id=7  child effect id=8  (parent < child: true)
route's subscriber count = 2 (the derivation and the child; the parent rides the derived cell)
```

(`probe_a110_wave_order.vl` case 3.) The second line is the load-bearing one: the
parent is **not on the cell's subscriber list at all** — it rides the derived cell —
so no ordering read off one cell's list can ever put the parent first. The id is
global, which is exactly why it can.

**A correction to A110 as filed.** The item's own probe — two independent
subscriptions on one cell, the inner created first — is a demonstration of face 1 and
is *not* a case door 2 fixes. Running its effects in ascending id runs the INNER
first, because the inner effect was created first, and its output does not change:

```
--- case 2: IN A TURN ---   (baseline AND door 2, identical)
turn:   INNER fired with 200 (boundary disposed: false)
turn:   outer disposes the inner boundary
```

That is not a defect in the rule. It is that "parent before child" is a statement
about *creation order matching nesting*, which a real form guarantees (the outer's
render closure is what creates the inner) and a hand-written pair of siblings does
not. So the pin door 2 owes must be written on the nesting shape —
`probe_a110_door2_nesting.vl`, where the outer's `sub` builds the inner boundary —
and the item's own probe must **not** be used as its pin.

### 7.4 What door 2 needs beside itself — two findings

Door 2's ordering rule, built alone, flips the order and still fires the disposed
observer. Measured across four scratch stds (`probes/door2_measurement.out` §1):

| instrument | result on the nesting probe |
|---|---|
| baseline (today) | inner fires BEFORE the outer, live — `built=3 live=2 dead=0` |
| door 2, phase 2 off a snapshot | outer first, inner still fires — `live=0 dead=2` |
| door 2, phase 2 off the live queue | outer first, inner still fires — `live=0 dead=2` |
| door 2 + the draining-turn scrub | outer first, inner fires **ZERO** times — `live=0 dead=0` |

**Finding one: phase 2 must not iterate a dead snapshot.** An effect that disposes a
child subscription has to be able to remove that child from the queue phase 2 is
walking. Taking the parked queue out into a local and iterating it makes that
impossible. Either pop off the live queue, or — better, and what the cost numbers
below use — keep a keyed **park set** beside the queue that `dispose` lowers in O(1)
and that phase 2 checks before each call. The second shape is door 1's liveness bit,
one scope up: if door 1 lands first (it did — Order 38), phase 2 should read *its*
flag and need nothing of its own.

**Finding two, and it is a bug on its own — `Subscription::dispose`'s pending-queue
scrub is dead code for every dispose reached from inside a settle.** `dispose` reads
its turn with `turn_scope.get_safe()` and nothing else, where `notify` and
`defer_to_turn` both read "the ambient turn, **else the currently draining one**"
(`draining_turns`). But `turn` calls `drain(fresh)` *after* `turn_scope.run(fresh,
body)` has returned, so a drain runs **outside** the turn's context extent, and a
dispose from inside a notify — which is every form's teardown, since a form's own
effect is what disposes the previous instantiation — reads `None` and scrubs nothing.

`probe_scrub_misses_draining_turn.vl` isolates it with no door-2 machinery at all: a
victim effect enqueued for wave 2 by a derivation, and disposed later in wave 1 by a
sibling effect.

```
=== TODAY ===
disposer: trigger=1 — disposing the boundary
  VICTIM fired with 10 — BOUNDARY ALREADY DISPOSED
victim fired live=0 dead=1
--- control: dispose from the turn's BODY ---
control fired live=0 dead=0

=== WITH THE ONE-LINE FALLBACK ===
disposer: trigger=1 — disposing the boundary
victim fired live=0 dead=0
--- control: dispose from the turn's BODY ---
control fired live=0 dead=0
```

The control — the same dispose made from the turn's *body*, where `turn_scope` is
established — is correct either way. So the scrub works exactly when the disposer is
not inside a settle, and never otherwise. The scrub's own doc comment promises the
opposite ("a disposed observer never fires, even if a `set` earlier in the same
extent already enqueued it"), and §4's honest limit in this paper already records the
*other* extent's queue as out of reach; this is a third case nobody wrote down. The
fix is the four lines `notify` already has:

```vilan
let ambient = match turn_scope.get_safe() {
	Some(let established) => Some(established),
	None => draining_turns.read().last(),
};
```

It is independent of both doors and should land as its own item with the probe above
as its pin, whether or not door 2 is ruled.

### 7.5 The cost

callgrind Ir under `node --jitless`, per settle, on the graph door 2 costs most on:
one source, one derivation, 40 effects on the source and 10 on the derived — 50
effects parked per settle — and one `set` per turn. Per-settle Ir is the slope
between 1 and 201 turns, so node's startup and the graph's construction cancel.
loadavg 8.6–24.0 across the runs (nine other lanes were building; Ir is an
instruction count and does not move with load).

| instrument | Ir per settle | vs today |
|---|---|---|
| today | 418,341 | 1.00× |
| the phase split alone (park set, append order) | 898,917 | 2.15× |
| the phase split + ascending-id order | 2,227,882 | 5.33× |

Read: the **phase split** costs +115% — about 9,600 Ir per parked effect, and most of
that is a second `NativeMap` (one `contains`+`insert` when parking, one
`contains`+`remove` when running) which a real build reuses from the existing
`queued` map. The **ascending-id order** costs a further +1.33 M Ir, 60% of the
total, and it is an insertion sort: 1,275 comparisons plus ~1,250 element moves at
k=50, O(k²). A bucketed insert keyed on the id, or a real sort, removes most of it.

So **5.33× is an upper bound on a scratch implementation**, both halves of which have
a known cheaper shape, and the absolute figure is 2.2 M Ir per settle at fifty
effects — against ~170 M Ir just to start node. A UI settle with fifty effects in one
wave is already an unusual wave; the common one is a handful.

(A fourth instrument, which read and rewrote the whole `Shared<List>` per park and
per pop, measured 33×. It is recorded in `probes/door2_measurement.out` only to say
why it is not the number: `Shared<List>` copies, so a queue must be mutated in place
or the settle is O(k²) *element copies*. That is a trap for whoever builds this.)

### 7.6 Which pins change — the estate, swept

Every `.vl` program in `vilan/test` (131 files, 130 run clean on this host), plus
every `.vl` in `vilan/examples` and `vilan/benchmarks` (36 files, 4 run clean — the
rest need a browser, a port or a fixture), run under today's std and under the
door-2 std, exit codes and stdout compared:

- **test corpus: zero output differences, zero exit-code differences** — 130 of 130.
- examples and benchmarks: two files differ, both **noise** —
  `benchmarks/src/main` prints wall-clock rates and `examples/walkthrough/src/server`
  prints node's pid inside an `ExperimentalWarning`.

**Nothing in the estate changes its observable order.** That is the argument for
building it — and equally the reason the pin must be *added* with it, because the
corpus does not contain the shape door 2 exists for. The pins door 2 owes:

1. `probe_a110_door2_nesting.vl` as a `reactive_lifetimes` case: after the outer
   disposes, the inner observer fires ZERO times, and the outer's render runs before
   the inner's effect.
2. A derivation-fixpoint case: a two-deep derivation chain feeding one effect, with
   the effect asserting it saw the *final* value once, not each intermediate.
3. The cost pin: a per-settle Ir figure in the perf ledger, so a later regression in
   the queue's shape is visible (the `Shared<List>` trap above is exactly the
   regression to guard).
4. `probe_scrub_misses_draining_turn.vl`, which belongs to finding two and lands with
   it whatever door 2 is ruled.

**Goldens.** The corpus gate is a byte-comparison of *emitted JS*, not of runtime
output, so door 2 moves every golden that carries `std::reactive`'s `drain`. Under
Order 38's Mechanics R8 that is a regeneration rather than a stop-and-decide,
*because* §7.6's sweep shows the runtime output byte-identical — which is the
evidence the rule asks for and the reason the sweep was run.

### 7.7 Solid's precedent

Solid runs **computations before effects** and, within effects, parents before
children: `createMemo` bodies are pulled to a fixpoint during the update phase, and
render effects (`createRenderEffect`) run top-down so a parent's DOM exists before a
child's binding touches it. The two-phase settle proposed here is that rule with
vilan's own vocabulary — `map`/`combine`/`flatten`/`selector` are the computations,
`effect`/`sub`/`bind_*` and the `std::ui` forms are the effects — and the id order is
vilan's answer to Solid's owner-tree walk: Solid knows the tree because it *builds*
one, and vilan gets the same order out of a monotonic counter because the tree's
construction order is the counter's order.

The thing Solid does that this does not is pull a memo **on read** rather than push
it on write. That is a different design (lazy derivations), it is out of scope here,
and `incremental-collections.md` §11.2 declines it for the same reason: `map` is
eager and making one derivation lazy would put a second lifecycle rule beside A28's.

### 7.8 What A111 would inherit

A111 (keep-alive `swap`) needs `Owner::suspend()`/`resume()`, and `resume` has to
re-run each of a parked subtree's effects once against the current value. **`resume`
inherits this section's rule**: the re-runs are effects, so they go in ascending
subscriber id, which is parent-before-child inside the resumed subtree — a parked
subtree's own owners were created in nesting order, so their effects' ids are already
in it. That is the whole of A111's dependency on door 2, and it is the reason the two
should be ruled in this order rather than together: without door 2, `resume` would
have to invent an order of its own.

### 7.9 The ruling asked

> **Is the order in which effects run within one settle part of the contract?**

Today it is subscription order, which is an implementation detail nobody documented
and which no app can usefully rely on (it depends on which cell fired and in what
order bindings were attached). Door 2 replaces it with a rule an app *can* rely on —
parent before child, on settled values — and that is a promise, so it is the owner's
to make.

> **Rec: YES, make it a contract, and build door 2 in Order 39.** The estate proves
> the change is invisible today (§7.6: 130 of 130 corpus programs byte-identical),
> the cost is bounded and has a cheaper shape than the one measured (§7.5), the
> alternative is that every nested form on one source needs the app to route around
> std (kolt's `page_content` latch, which is what door 3 in A110 is), and the rule is
> the one Solid already ships so it is the order a framework user expects. Build it
> **on top of door 1's liveness flag** rather than beside it — finding one in §7.4 is
> that door 2's phase 2 needs exactly that flag — and land finding two's one-line
> scrub fix first, on its own, since it is a bug either way.

Two things this section has decided rather than asked, and will re-open on the
owner's word: the pin is written on the nesting shape and **not** on A110's own probe
(§7.3), and the parked queue is a keyed set plus an append-only list rather than a
sorted insert (§7.5 — it is 60% of the measured cost).

### 7.10 The second measurement, and the ruling (2026-09-21)

Lane reactive-38 measured door 2 independently, on its own instrument
(`scripts/integration/sweeps/order38/reactive-38/door2-measurement.md`, both instrument
patches beside it), and the two agree on everything that decides the question and differ
only where the instruments do. **Agree:** no corpus program changes its output (126
runnable programs there, 130 here); A110's own probe is a SIBLING pair and not a shape
door 2 changes; door 2 does not subsume door 1 — built alone it still fires the disposed
observer. **Differ, by construction:** the cost. §7.5's 2.15× (phase split) and 5.33×
(naive id sort) are per settle at 50 effects; reactive-38 built the queue BUCKETED and
read **+23.5 % Ir per wave** against a like-for-like control (229,042 vs 185,507), with
the naive partition-and-sort at 2.2×. The bucketed figure is the design's; the naive
ones are what not to build. Of 315 targeted tests exactly three move under its
instrument: the nested-`swap` pin IMPROVES (builds/teardowns 3/3 → 2/2 — door 2 removes
the wasted build door 1 can only tear down), one sibling-observer reorder, and the
no-cycle gate's `unmounted cycles 0 → 1`, which is the INSTRUMENT's wrapper closure and
which the build slice re-measures.

Since this section was written, door 1 and §7.4's scrub fix both LANDED (Order 38, lane
reactive-38: 2f93d7a2, 2b06202c), so door 2 builds on them rather than beside them.

**RULED (the owner, 2026-09-21), as recommended.** Effect order within one settle IS a
contract — **about nested forms only**: a parent form's effect runs before anything its
render created, which ascending subscriber id gives because `fresh_id` is monotonic.
Order among INDEPENDENT observers of one source is explicitly NOT part of the contract.
Built bucketed, on top of door 1's liveness flag, in Order 39. The inline (no-turn) notify
forming a wave — one rule for both cadences — is NOT Order 39's; it is recorded here as
the rule's boundary. Kolt's `page_content` latch retires when the build lands.
