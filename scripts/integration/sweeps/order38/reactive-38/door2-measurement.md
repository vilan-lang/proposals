# A110 door 2, MEASURED — lane reactive-38, Order 38 (2026-09-21)

Door 2 is **not built**. This file is the measurement the brief (R4) asked for, for
`reactive-turns.md`'s "order within a wave" section. Everything here was produced on a
throwaway branch, `door2-scratch`, cut from the lane branch **after** door 1 landed
(`2f93d7a2`); nothing from it is merged. The two instruments are saved as patches beside
this file: `door2-variant1.patch` and `door2-variant2.patch`.

The baseline for every number below is **door 1 as committed** (`2f93d7a2`), not
`0fa109eb`: door 2 is an addition to the liveness flag, and measuring it against a tree
without the flag would charge it for door 1's work.

---

## 1. What was instrumented

The rule, from A110 door 2: **drain derivations to a fixpoint, then run effects in
ascending subscriber `id`.**

Derivations are tagged at creation. A real build would carry a `Subscriber.kind` set by an
`on_change_derived` primitive; tagging through the trait is awkward (`Source::map` calls
`Source::on_change`, which for a generic source is not `observe`), so the instrument sets
a module-level flag around the derivation's own `on_change`/`sub` call and `observe` reads
it into the `Subscriber`. The ORDER this produces is the same either way, which is what is
being measured. The five tagging sites are `Source::map`, `combine`, both `flatten`s
(the outer subscription *and* the rolling inner one) and `selector`.

Two instruments, because the first one's cost is an artefact of its own naivety:

- **Variant 1 — partition + sort.** `drain` re-partitions `turn.pending` into derivations
  and effects on every inner iteration, runs the derivations to a fixpoint, then insertion-
  sorts the effect half by id and runs it. This is the shape the item's "a sort per wave"
  sentence describes, and it is the expensive one: the partition copies the whole pending
  list per iteration.
- **Variant 2 — bucketed.** `Turn` carries a second queue, `pending_derived`; `enqueue`
  routes by class at insert time and keeps the EFFECT queue ascending by id with an
  ordered insert (entries arrive close to in order already, so the scan is short). `drain`
  then drains the derivation bucket to a fixpoint and runs the effect queue as it stands.
  This is the item's "or a bucketed insert", and it is the shape a real build should take.

Variant 2 also had to change one thing that is **not** door 2: it replaces
`turn.queued.write() = NativeMap::new()` (a fresh dedup map per wave) with a per-id
`remove` as each subscriber leaves a queue, because with two queues there is no single
wave boundary at which the whole map may be cleared. That change is measurable on its own,
so a third build isolates it.

- **Control — door 1, per-id `queued` removal only.** No phase split, no ordering. This is
  the like-for-like baseline for variant 2.

## 2. Per-wave cost, in Ir

Measured by SLOPE, so node's startup cancels out: the same program built at 5,000 and at
25,000 waves, `Ir(25k) − Ir(5k)` over 20,000. One wave is four derivations off one root
(two of them a second level deep, so the derivation phase is a real fixpoint and not one
pass) and eight effects spread over the root and the derivations, so the effect half has
something to order. The effects write a plain `Shared` cell and never a signal, so a wave
stays one wave. Program: `bench/app.vl` beside this file.

`callgrind` Ir, never wall. **Read the `--jitless` column**: it is the interpreter tier,
it is what the C14 measurements in `signal-cell-representation.md` §13 used, and it is
load-independent. The JIT column is recorded and is NOT trustworthy here — V8's tiering
decisions are time-dependent and the host's loadavg moved between 8 and 40 across these
runs (ten other lanes), which shows up as the implausible *negative* deltas.

| build | Ir/wave, `--jitless` | vs door 1 | Ir/wave, JIT | vs door 1 |
|---|---|---|---|---|
| door 1 (`2f93d7a2`) — the baseline | **166,325** | — | 47,646 | — |
| control (per-id `queued` removal only) | **185,507** | +11.5 % | 30,559 | −35.9 % |
| **door 2, variant 2 (bucketed)** | **229,042** | **+37.7 %** | 38,429 | −19.3 % |
| door 2, variant 1 (partition + sort) | **367,285** | **+120.8 %** | 61,653 | +29.4 % |

**The headline: door 2 costs +23.5 % per wave** (229,042 against the control's 185,507),
once the `queued`-bookkeeping change it drags in is held constant — and **+37.7 %** if you
charge it for that change too. Written the naive way, as a partition and a sort per wave,
it costs **2.2×**, and that number should not be the one the ruling is made on.

**Door 1's own cost, for scale.** The same bench on `0fa109eb` (no liveness flag) reads
**152,387 Ir/wave** jitless, so door 1 itself is **+13,938 Ir/wave, +9.1 %** — one wave here
is 12 notifications (4 derivations + 8 effects), which puts the flag at **≈1,162 Ir per
notification** on the interpreter tier, the same order as C14 S3's measured +590 Ir for its
weak upgrade. Door 2 is therefore about 2.5× door 1's price for the ordering it buys.

Raw Ir totals, for anyone re-deriving the slopes:

| build | jitless 5k | jitless 25k | JIT 5k | JIT 25k |
|---|---|---|---|---|
| `0fa109eb` (no flag) | 918,974,396 | 3,966,716,438 | 424,102,588 | 894,778,823 |
| door 1 | 988,825,692 | 4,315,329,527 | 688,734,332 | 1,641,663,704 |
| control | 1,085,355,613 | 4,795,504,457 | 429,829,095 | 1,041,008,425 |
| variant 2 | 1,302,574,534 | 5,883,416,659 | 516,177,134 | 1,284,747,881 |
| variant 1 | 1,996,185,885 | 9,341,883,774 | 717,966,517 | 1,951,031,963 |

**A side finding for the perf family, not for door 2.** The control line is a change of one
statement — a fresh `NativeMap` per wave versus a per-id `remove` — and it moves the
interpreter tier +11.5 % and the JIT −35.9 %. The JIT figure is the untrustworthy column,
so this is a candidate to MEASURE properly rather than a result; it is recorded because
door 2 cannot be costed without separating it, and because if the JIT direction survives a
quiet host it is a free win on the drain's hot path independent of door 2.

## 3. What CHANGES, behaviourally

### 3.1 The corpus: nothing

126 of the 131 corpus programs (the five `corpus_harness::NOT_RUN` entries excluded: a
host clock, a random draw, a database, the host environment, and `nursery.vl`'s
timer-decided print order) were built from a staged copy of `vilan/test` with each build
and run under node. **Zero programs print anything different.** Not one corpus program
distinguishes the two orders — which is itself the evidence that the corpus does not
cover this rule, not that the rule is unobservable. (Lane papers-38 measured the same
thing independently over 130 programs and got the same zero.)

### 3.2 The suite: three pins move, and one of them is the instrument's fault

Run under the variant-2 build: vilan-cli `reactive_lifetimes`, `reactive_channels`,
`reactive_selection`, `ui_rows`, `ssr_differential`, `dom_events`, `router`, `hmr_swap`,
`examples`, `source_bindings`, `debounce`, `storage_handle` (90 tests) — then
`service_layer`, `rpc_http`, `cancellation`, `owned_nursery`, `streaming`,
`ssr_fullstack`, `hmr`, `style_when` (71 tests, **all pass**) — then vilan-core
`interpreter` and `docs` (154 tests, **all pass**). The whole-workspace run was started
and abandoned: the host was carrying ten lanes and it had cleared 21 of 7,742 tests when it
was stopped, so this is a targeted list of every binary that RUNS a reactive program and
reads what it printed, not the full suite. Corpus byte-identity is excluded by
construction (the std source changed, so every reactive golden moves).

Three move:

1. **`ui_rows::a110_nested_swaps_on_one_source_build_no_orphan_subtree_on_sign_out`** —
   the improvement. `builds=3 teardowns=3` → `builds=2 teardowns=2`. See §3.3.
2. **`reactive_lifetimes::a110_a_disposed_observer_does_not_fire_from_a_wave_the_drain_already_took_out`**
   — its `later-wave` half reorders: `later-wave-fired=0` → `later-wave-fired=1`, with the
   inner observer firing LIVE before the outer disposes. This is the sibling-observer case
   of §3.4, not a regression: the observer that fires is not a disposed one.
3. **`reactive_lifetimes::a_disposed_exemplar_holds_no_reactive_cycle`** — the standing
   no-cycle gate goes from `unmounted reachable=122 cycles=0` to `unmounted reachable=124
   cycles=1`, an 8-node SCC reading
   `system / Context | closure/(anonymous) | system / Context | closure/(anonymous) |
   Array | Array | Object | Array`. **This is the INSTRUMENT, not the rule.** The
   derivation tag is applied by wrapping each combinator's `on_change` call in
   `as_derivation(|| ..)`, which adds a closure that carries the ambient contexts — two
   `Context` objects and two closures is exactly what the SCC names. A real build tags at
   an `on_change_derived` primitive and adds no closure anywhere. It is recorded because
   the build slice MUST re-run this gate and is not entitled to assume the instrument's
   reading: `cycles=1` unmounted is the one number in the suite that may never be
   regenerated.

Nothing in `service_layer`, `rpc_http`, `streaming`, `cancellation`, `owned_nursery`,
`ssr_fullstack`, `hmr`, `hmr_swap`, `router`, `dom_events`, `reactive_channels`,
`reactive_selection`, `examples`, `style_when`, `interpreter` or `docs` notices the
change. In particular the whole server/rpc half — where a turn per request is the cadence —
is indifferent to it.

### 3.3 The nested-swap DOM shape: door 2 removes the wasted build

This is the measurement that matters, and it is the shape the item was filed from — an
OUTER `swap` keyed on a projection of the route around an INNER `swap` keyed on the route
itself, the idiom that stops the outer form rebuilding on every navigation. The pin is
`ui_rows.rs`'s `a110_nested_swaps_on_one_source_build_no_orphan_subtree_on_sign_out`,
which counts inner page builds against page-owner disposals.

Signing out **inside a turn** — the cadence every `View.on` dispatch and `mount_root`
establishes:

| build | inner page builds | page-owner disposals |
|---|---|---|
| `0fa109eb` (before door 1) | crashes: `TypeError: Cannot read properties of null (reading 'insertBefore')` | — |
| door 1 | 3 | 3 |
| door 1 + door 2 | **2** | **2** |

Door 1 makes the shape survive; door 2 makes it stop doing the work. The third build under
door 1 is A110 face 1 exactly: the inner form renders once for a value the outer is about
to tear down, because the wave runs in subscription order and the outer reaches the source
one derivation later. Under door 2 the derivation reaches the outer effect in phase 1, the
outer's effect precedes the inner's in id order, and the inner is disposed before its turn
comes — so the render never runs. **This is the one shape in the tree where door 2 is
visible, and it is the one apps are told to write.**

### 3.4 A110's own probe is NOT a shape door 2 improves

The item's probe (and lane papers-38's `probe_scrub_misses_draining_turn.vl`) creates the
INNER effect before the outer observer, so the two are siblings rather than a nesting.
Under door 2 the inner's id is the LOWER one, so ascending-id order runs the inner FIRST,
before the outer disposes anything:

```
door 1:            outer disposes the inner boundary   /  inner fired 0 times
door 1 + door 2:   INNER fired with 1 (boundary disposed: false)
                   outer disposes the inner boundary   /  inner fired 1 times
```

The observer fires either way under door 2 — but LIVE, which is face 1's wasted build and
not face 2's leak. Door 2 did not break anything here; it reordered two independent
observers, which is what the rule says it will do. The claim "id order IS
parent-before-child" holds **only where the forms are genuinely nested** — a parent form's
effect is created during its `place`, its child's during its `render` — and it says nothing
about two siblings. The paper should say that in those words, because it is the difference
between "door 2 fixes A110's probe" (false) and "door 2 fixes the shape A110 was filed
from" (true, §3.3).

### 3.5 Door 2 does NOT subsume door 1

Door 2 touches `drain` only. Outside a turn, `SignalCell::notify` walks a snapshot of the
subscriber list depth-first: there is no wave, so there is nothing to phase-split or sort,
and a disposed observer in that snapshot still fires. Measured on the door-2 build without
door 1's flag this is unchanged. Door 1 is a prerequisite, not an alternative — and the
open question it leaves is whether the INLINE path should form a wave at all, so that one
ordering rule covers both cadences, or whether "no ambient turn means depth-first, as
today" stays the contract.

## 4. For the ruling

The question the owner is asked (A110 door 2): **is effect order within one wave part of
the contract?** What the measurement says:

1. **Nothing in the tree depends on the current order** — 126 corpus programs print
   identically, and of 315 targeted tests exactly three move (§3.2): the one door 2 is
   for, one sibling-observer reorder, and one instrument artefact. So adopting the rule
   breaks no pin that is not itself about the rule.
2. **The rule buys one real thing**: the nested-form shape stops building a subtree it is
   about to destroy (§3.3). That is a correctness-shaped win for an app whose inner arm is
   `unreachable` for the outer's new value — the panic the item names.
3. **It costs +23.5 % per wave** implemented as a bucketed insert, and 2.2× implemented
   naively (§2). The bucketed form is the one to cost.
4. **It must be stated for NESTED forms, not for sibling observers** (§3.4), or the rule
   promises something it does not deliver.
5. **It rides on door 1** (§3.5), and it leaves the inline cadence unordered.

Recommendation from this lane: **take the rule, as a contract about nested forms, built as
a bucketed queue** — and say explicitly in `reactive-turns.md` that effect order among
INDEPENDENT observers of one source is NOT part of the contract, so the id order is an
implementation consequence there rather than a promise. +23.5 % on a wave is real, and the
alternative is that every app that writes the idiom the guide teaches pays a full subtree
build per navigation and hopes its arms are total.

## 4a. Against lane papers-38's own measurement

papers-38 measured door 2 independently before this file existed, and the two agree where
they overlap — **zero output differences** over the corpus (their 130 programs, this lane's
126 runnable ones), and **door 2 alone does not stop a disposed observer firing**, so door
1 is a prerequisite. Their cost figures are "2.15× per settle for the phase split, 5.33×
with a naive id sort"; this lane's naive form (partition + insertion sort) is 2.21×
jitless, and the figure this lane adds is the **bucketed** one, which the other measurement
did not cost: **+23.5 % per wave** like-for-like (§2). The two differences to reconcile are
the shape measured (their settle, this file's wave, with four derivations and eight
effects) and the fact that this file's baseline is the door-1 commit rather than
`0fa109eb`.

Two things this file has that theirs cannot: the **nested** shape's numbers (§3.3 — the
one place in the tree door 2 is visible, and the reason §3.4 matters), and the **SCC
gate's** reading under the instrument (§3.2, item 3), which the build slice must re-run.

## 4b. FIND-2 is not door 2's to fix

Door 2's phase split does not repair `Subscription::dispose`'s pending-queue scrub, which
resolved its turn with `turn_scope.get_safe()` alone and therefore never ran for a dispose
reached from inside a drain (papers-38's FIND-2, fixed in this lane at `2b06202c`). With
two queues the scrub has to cover BOTH of them, so door 2's build slice inherits the fixed
version and must extend it — the variant-2 patch beside this file already does.

## 5. Reproducing

```
# from the lane worktree, on a throwaway branch off the door-1 commit
git switch -c door2-scratch 2f93d7a2
git apply <this directory>/door2-variant2.patch    # or variant1.patch
cargo build
<this directory>/measure-ir.sh <label>             # per-wave Ir, both tiers
<this directory>/capture-corpus.sh <label>         # every corpus program's stdout
diff -rq <this directory>/out-base <this directory>/out-<label>
```
