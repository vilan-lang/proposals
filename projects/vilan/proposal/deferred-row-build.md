# The deferred row build — `each` stops building rows its own drain cuts (A131)

Tracker A131. Written by lane papers-43 of Order 43 on 2026-09-28, against vilan
`next` @762c6aa5 (content-identical to `main` @1a33340f; `vilan 0.41.1
(1a33340f2)`). Nothing in the compiler tree changed. Every claim about the tree
is a line that was read (cited `file:line`, std paths under `vilan/std/src/`) or a
probe that was run.

Probes: `scripts/integration/sweeps/order43/papers-43/probes/a131/` —
`run_all.sh <scratch>`, output in `run_all.out`. Three programs:

- `walk/` is Order 42's `walk-diagnostic.vl`, ported to `usize` indexes. The
  sweep copies no longer compile on 0.41.1, because they predate the I5 flip.
- `trace/` is the same walk, plus the id of every row `each_by` built that the
  settled list does not hold, and the op that minted it.
- `control/` is the in-tree pin program `A112_S3_WALK`, verbatim.

Each is built with `target = "browser"` and run under the shared DOM stub.

Related: A112 (the delta-driven `each`, `incremental-collections.md` §9 and S3),
A129 (the keyed span match, RULED 2026-09-25 as `incremental-collections.md` §13
Q5), A98 (settled rows), A91 (the order pass), `reactive-turns.md` (the drain).

---

## 0. The ask, and the answer up front

A129 gave a `Splice`'s span the keyed match. The ruling's sentence was "**the op
path never builds more than the pass**" (`incremental-collections.md` §13 Q5).
The 300-turn walk's `each_by` went from 1,078 rows to 575, against the
whole-list pass's 557. The 18 left over are rows **built and cut inside one
drain**. The op path applies each op as it arrives. The pass reads only the list
the drain settles on, so it never meets these rows.

**The answer.**

1. **The number reproduces on today's toolchain.** It is `by=575` against
   `pass_by=557`, 18 turns at +1 each (§1).
2. **The 18 are five classes, not the two the item named.** Only 5 of them come
   from inside one `edit`. The other 13 cross separate ops in one `batch`, and 2
   are rows a `Reset`'s pass built that a later op cut (§1.2). A producer-side
   fold inside `ListCell::edit` would therefore recover only 5.
3. **There are two consumer-side designs that recover all 18.**
   - The one this paper recommends, if it is built, needs no op algebra. A row
     that arrives is recorded as a **pending slot** (item, key and, for
     `each_by`, its cell), not built. Cutting a pending slot costs nothing. At the
     end of the drain's callback, the surviving pending slots are built in
     position order (§3).
   - The algebraic alternative folds the drain's ops into a net splice set
     first. It needs a composition std does not have (§2.3) and a law it does not
     pin, and it cannot fold a `Move`.
4. **What deferral costs the per-op path.** Each op pays one check of whether the
   slot is pending. A cut of a real row next to a pending one pays a scan for the
   next real marker. The end of the callback pays one pass over the pending set.
   A drain with no insert pays nothing (§4).
5. **What is observable.** `render` runs in position order, not op order. It runs
   after every removal in the drain. And it runs fewer times.

**Rec: PARK, and correct the record.** There is still no exhibit. kolt never
takes the op path at all: its four `each_values` sites are over
`SignalCell<List<..>>` or a `.map(..)`, so they take the pass. The cost is 18
builds in 575 (3.1 %) on a walk built to provoke them. Q5's ruled sentence
should be stamped with its honest limit: "never more than the pass **within an
op**; rows built and cut across ops in one drain are A131's". The design in §3 is
the door, sized **M**, for the day an exhibit arrives. The one question for the
owner (§7) is whether the ruled sentence was meant per drain. If it was, build
§3 in Order 44.

## 1. Provenance — the 18 rows

### 1.1 The walk and its numbers

Order 42's `sweeps/order42/collections-42/a129/walk-diagnostic.vl` is the program
behind the numbers:

- 300 turns, each one `batch` holding `1 + next_random(4)` ops (`:92`, `:96`),
  drawn from a seeded MINSTD sequence with seed 7 (`:14-20`).
- Every row id is fresh (`:23-29`).
- The op menu (`:102-162`): push, `insert_at`, `remove_at`, `set_at` with the same
  key and with a fresh one, `move_range`, `pop`, `remove_range`, `truncate`,
  `set` (a `Reset`), `reconcile_to` (edit one element, append one), and an `edit`
  whose body is `insert_at(at, fresh()); remove_at(0); push(fresh())`
  (`:157-161`).
- One cell is mounted six times (`:76-84`): `each`, `each` over `map_each`,
  `each_values` and `each_by` on the op path, and two controls (`each`, `each_by`)
  over `walk.map(|l| l)`. A `map` keeps no log, so the controls take the pass.
- Rows are counted in the render closures (`:54-57`).
- The DOM is checked against the cell every turn, and a turn is printed when the
  op path built more than the pass did (`:166-181`).

The in-tree pin is `ui_rows.rs`'s `A112_S3_WALK`
(`crates/vilan-cli/tests/ui_rows.rs:4746`), asserted by
`a112_s3_the_random_walk_holds_through_each` (`ui_rows.rs:4967-4980`). The tail
is `renders=2061 by=575 rerun=12258 pass=653 pass_by=557`. Its doc comment
already names this class (`ui_rows.rs:4955-4966`): "The 18 rows `by` still builds
beyond the pass are rows BUILT AND CUT INSIDE ONE DRAIN … the rest are no span's
to recover."

Order 42's `results.txt` (`sweeps/order42/collections-42/a129/results.txt:1-14`,
collections-42 @c64bf317) records the history:

- before: `by=1078 pass_by=557`
- span match only: `by=584`
- span match + `live_ops` (a `Reset` supersedes the drain's earlier ops):
  `by=575`, shipped

**Re-run today** (`run_all.out`, `vilan 0.41.1 (1a33340f2)`): all three
programs print `by=575 … pass_by=557`. The diagnostic prints exactly 18 turns,
each `op = pass + 1`. `control/` reproduces the pin's tail byte for byte.

### 1.2 The five classes

`trace/` records, per turn, the row ids `each_by` built that the settled list does
not hold, and which op minted each one (`run_all.out`):

| class | built by | cut by (same drain) | rows | turns |
|---|---|---|---|---|
| 1 | `edit(at=0)`'s `insert_at(0, x)` | the same `edit`'s `remove_at(0)`: two ops in one log, `Splice(0,[],[x])` then `Splice(0,[x],[])` | 5 | 83, 99, 188, 229, 292 |
| 2 | `edit(at≠0)`'s trailing `push` | a later `remove_range` / `remove_at` / fresh-key `set_at` | 3 | 161, 289, 291 |
| 3 | `walk.push` | a later `pop` / `truncate` / `remove_at` | 4 | 145, 231, 234, 300 |
| 4 | `reconcile_to`'s appended row | a later `pop` / `remove_at` | 4 | 112, 166, 169, 244 |
| 5 | a `Reset` (`walk.set`), built by `reconcile_pass` | a later `pop` / `remove_at` | 2 | 19, 288 |

Two findings the item did not have:

- **Class 5 survives `live_ops`.** `live_ops` drops the ops BEFORE a drain's last
  `Reset` (`browser/ui.vl:1406-1438`). The `Reset`'s own rows can still be cut by
  an op AFTER it.
- **Only class 1 lives inside one `edit`.** `edit` records one op per mutation,
  with no folding (`delta.vl:829-842`: "Four mutations inside one `edit` are one
  notification and four ops"). The other 13 rows cross ops that were separate
  `ListCell` calls in one `batch`.

The `each` runs have their own excess. `renders=2061` over three op-path `each`
runs, against `pass=653` for one run, is 102 above 3 × 653. That excess mixes
these transients with `each`'s rebuild of a changed item (§4.1). This paper does
not decompose it. The keyed 18 are the clean measurement.

## 2. The op path today

### 2.1 Producer

Every `ListCell` write mutates the list in place, records one op, and publishes
once (`splice`, `delta.vl:944-954`). `pop` is `splice(size-1, 1, [])`
(`delta.vl:479-484`). `edit` runs its body on a `Tracked` recorder, then records
every op it collected (`delta.vl:838-840`). The log is `DeltaLog`
(`delta.vl:144-310`); `since` copies out the ops since a cursor
(`delta.vl:271-295`).

### 2.2 Drain and consumer

A `batch` (`reactive.vl:666-678`) defers the notifications and drains once
(`drain`, `reactive.vl:408-485`), so each consumer's effect runs once per turn
and sees every op of the turn together. The consumer is `place_each`
(`browser/ui.vl:1480-1783`) and its keyed twin `place_each_by`
(`browser/ui.vl:1786-2080`). A source with a log attaches
`effect_on_change(|_| for op in live_ops(source.delta_since(cursor)) { match op … })`
(`browser/ui.vl:1714-1771`, `:2012-2070`). **Every op is applied immediately,
one after another:**

- **`Splice`.** A splice that only removes or only inserts goes to `splice_rows`
  (`:1664-1702`; keyed `:1967-2001`). One that does both goes to
  `reconcile_span(at, removed.len(), inserted)` (A129, `:1724-1728`; keyed
  `:2021-2025`).
- **`SetAt`.** In `each`, the same key with an equal item costs nothing and
  anything else is `splice_rows(at, 1, [value])`. In `each_by`, a same-key write
  goes into the row's cell (`:2030-2048`).
- **`Reset`.** `reconcile_pass(items)`.
- **`Move`.** The list after the move is rebuilt from `row_items` and handed to
  the pass (`:1749-1769`; keyed `:2054-2068`).

**The build** is one call shape everywhere:
`run_with_owner(owner, || region.open_row_before(render(item), reference))`
(`splice_rows` `:1696`; the span pass's `Refresh` / `Fresh` arms in
`reconcile_span`; keyed with `render(cell)` over a fresh `SignalCell`, `:1995`).
`open_row_before` makes a marker text node, stages the content in a fragment and
does one `insert_before` (`:716-723`).

**The cut** is `region.cut_row(going, end)` (`:732-736`, an `extractContents`
from the row's marker to `end`), then `owner.dispose()` and `drop_row`
(`:1666-1678`). `end` is the next row's marker, or the anchor for the last row
(`:1670-1674`).

**SSR is not involved.** The process twin has no op path (`process/ui.vl:613-619`:
"a server render IS only a first build"), and nothing hydrates.

### 2.3 The algebra the item assumed

The item says "Splice ∘ Splice composition — the law pin already covers the
algebra." **It does not.** No composition function exists in std: a search for
compose / coalesce / net / fold over `delta.vl`, `reactive.vl`, both `ui.vl`
twins and `rpc.vl` finds none, and the only drain-level rewrite is `live_ops`.
The law pin, `crates/vilan-cli/tests/delta_log.rs:133`
(`the_derivative_law_holds_across_four_hundred_randomized_turns`, running
`vilan/test/delta-law.vl`), asserts that applying a drain's ops ONE AFTER ANOTHER
to a mirror reaches `source.get()`. That pins the sequence's semantics. It would
be the natural oracle for a composition (compose-then-apply = apply-in-sequence),
but it pins none today.

## 3. The design — pending slots, built at the end of the callback

### 3.1 The change

The consumer's bookkeeping gains one parallel list, `row_pending: Shared<List<bool>>`.
The alternative is making `row_rows` a `List<Option<Row>>`. The parallel list is
chosen because `row_rows` IS the region's held list (`region.hold_rows`,
`browser/ui.vl:1628-1633`), and a region must never hold a row that is not in the
document. Three rules replace the immediate build:

1. **Arrive.** Every build site does the same thing: `splice_rows`' insert loop,
   `reconcile_span`'s `Fresh` arm, and its `Refresh` arm after the old row is
   dropped. Each pushes the item and key into `row_items` / `row_keys` as today.
   For `each_by` it also mints the row's `SignalCell` (cheap, and a later
   same-key `SetAt` writes into it). It marks the slot pending, and does NOT call
   `render`, mint an `Owner` or touch the DOM.
2. **Cut.** Removing a pending slot removes its bookkeeping entries and nothing
   else: no `cut_row`, no `dispose`, no `drop_row`. A same-key `SetAt` on a
   pending slot writes its item (and, keyed, its cell) as it does for a real row.
   A real row whose right-hand neighbour is pending takes as its `end` the next
   REAL marker to the right, or the anchor.
3. **Settle.** After the `for op in live_ops(..)` loop, at the end of the same
   `effect_on_change` callback, every pending slot is built in ascending position:
   `run_with_owner(owner, || region.open_row_before(render(..), next_real_marker(i)))`.
   The slot then becomes real. Building left to right keeps `render`'s call order
   the list's order. Each build lands just inside the first real marker after it,
   so a run of consecutive pending slots placed in order stays in order. That is
   `splice_rows`' own argument (`:1686-1688`), and it is why the scan never needs
   a just-built marker.

`reconcile_span` needs one more rule. Its order pass cuts and re-inserts moved
rows by marker (A91's two halves, `:1560-1650`). A pending slot has no marker
and no nodes. It is left out of the cut and insert halves. Its `Keep` keeps it
pending, and `row_references` (A98, `browser/ui.vl:1445`) skips it when choosing each row's `reference`.
The whole-list pass (`whole`, `:1624-1633`) cannot hand pending slots to
`hold_rows`. It settles first: a `Reset` or `Move` arm that runs the whole pass
while slots are pending builds those slots before the pass reads the run. This
case is rare, because a `Reset` rebuilds from the list anyway.

### 3.2 Why not the algebra

The alternative folds `live_ops(..)` into a normalized list of disjoint net
splices before applying anything. A `Splice` composes with a `Splice`, and a
`SetAt` folds into a pending insert. A `Reset` anywhere already nets to
`Reset(settled)`, which would also recover class 5. It has three drawbacks:

- **It needs a function std does not have**, with a law nobody pins (§2.3).
- **`Move` is not a splice.** It either composes too, which is new algebra, or
  ends the fold, which leaves a hole.
- **The saving is per consumer anyway.** Folding at the producer instead
  (`ListCell::edit`, `delta.vl:838-840`) catches only class 1 (5 of 18), and it
  changes the op count every consumer sees (`map_each`, `KeyedCell`'s forward).

Pending slots need no algebra. They are the pass's own insight, "build only what
the settled list holds", applied at the granularity the op path already has.
The oracle is the one the tree already runs: the walk's per-turn DOM check
(`walk-diagnostic.vl:175-181`) and `delta-law.vl`'s mirror.

## 4. What it costs, and what it changes

### 4.1 The cost table

| path | today | with pending slots |
|---|---|---|
| per op, `Splice` insert of k | k builds (render + owner + marker + fragment + `insert_before`) | k list inserts + k flags (+ k cells for `each_by`) |
| per op, `Splice` remove of k | k cuts (`extractContents` + dispose + marker remove) | for a real row, the same, plus a scan past pending neighbours for `end`; for a pending slot, a list remove only |
| per op, `SetAt` same key | `each_by`: `cell.set`; `each`: nothing if equal, else a rebuild | the same, for a real or a pending slot. `each`'s rebuild of a pending slot is a write, so a pending row changed twice builds once. |
| per op, span pass | as today | as today, pending slots skipped in the cut/insert halves |
| end of callback | nothing | one ascending walk over the pending positions; each pays one build plus a scan to the next real marker, bounded by the consecutive pending run |
| a drain with no insert | — | zero. The pending set is empty, and the settle is one length check. |
| memory | — | one `bool` per row. The ops are already materialized as `List<SeqOp<T>>` by `delta_since` before the loop (`:1715`), so holding them costs nothing new. |

**The walk's expected numbers:** `by` drops 575 → 557. `renders` drops by at
least the same transients in each of the three `each` runs. The pin's tail
(`ui_rows.rs:4970`) moves, and the move is the deliverable.

### 4.2 What becomes observable

1. **`render`'s call count and order.** Rows build after every removal in the
   drain, in position order, not op order. A counter inside `render` (the walk's)
   sees fewer calls. Nothing in std or kolt reads that order.
2. **What `render` reads is unchanged.** `ListCell` mutates `items` before it
   publishes (`delta.vl:949-953`), so `source.get()` inside `render` already reads
   the SETTLED list in both designs. A transient row today renders against a list
   that does not contain its item. That is an argument FOR deferral.
3. **Effects minted inside a build run later in the same callback.** `effect`
   calls its observer at once (`reactive.vl:1274-1277`). The subscriptions of
   transient rows are no longer created and disposed.
4. **A build that writes the same list** behaves the same in both designs. The
   write is logged and re-enqueues the effect for the drain's next wave
   (`reactive.vl:458-480`). Today's loop iterates a snapshot, and so does the
   deferred one.
5. **Mid-drain DOM.** A transient row's nodes exist briefly today. No paint
   happens mid-task, but a layout read inside `render` sees the intermediate
   rows. Deferral removes that intermediate state.

## 5. Pins, if built

- **The walk's tail moves** (`ui_rows.rs:4970`): `by=557`, equal to `pass_by`.
  The ruled sentence then holds per drain, and `renders` goes to its new value.
- **One pin per class** (§1.2), each a two-op `batch` or `edit` asserting
  `built=<settled count>` under the cost harness. Class 1:
  `edit(|l| { l.insert_at(0, x); l.remove_at(0); })` builds 0. Class 5:
  `set([a, b]); pop()` builds 1.
- **A pending neighbour's `end`:** a real row cut beside a pending slot leaves
  the document equal to the list (the per-turn DOM check, applied to that shape).
- **`each_by`'s cell:** a pending slot written by a same-key `SetAt` and then
  settled renders the LAST value, with one build.
- **The law:** `delta-law.vl`'s mirror is unchanged. The consumer is the only
  code touched.

## 6. Sizing

**M, about 3 days, one reactive lane.** The work is in `browser/ui.vl` only: both
twins' `splice_rows`, the `reconcile_span` build arms and order-pass skips, the
settle step, `row_pending`, and the `hold_rows` settle-first rule. There is no
compiler change, no process-twin change and no wire change. Goldens: none (the
emitted JS of user programs is unchanged). The one pin tail that moves is the
walk's. One CHANGELOG entry (perf, not breaking): a `render` count drops, which
no contract promises.

## 7. For the owner

- **Q1 — was A129's "the op path never builds more than the pass" meant per
  drain?**
  - **Rec: read it per op, and stamp the limit.** The ruling is met within any
    op, and the 18 rows (3.1 %) are A131's. That keeps A131 **PARKED** until an
    exhibit shows a transient row that is expensive: its build cost times how
    often a build and a cut land in one drain. The number to watch stays
    575 vs 557.
  - If the sentence was meant per drain, build §3 in Order 44, M.
- **Q2 — if built: pending slots (§3) or the net-splice fold (§3.2)?**
  - **Rec: pending slots.** They recover all five classes, need no algebra and no
    `Move` story, and leave the producer and every other consumer alone.

**For the record.** `incremental-collections.md` §13 Q5 still carries its
unfilled `⟦INTEGRATOR: collections-42 had not reported …⟧` placeholder
(`incremental-collections.md:818-822`). This paper's §1.1 has the walk numbers
it asks for (`by` 1,078 → 575 against 557).
