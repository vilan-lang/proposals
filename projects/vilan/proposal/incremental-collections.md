# Incremental collections — a change structure for `std::reactive` (A112)

Tracker A112. Written by lane papers-38 of Order 38, on vilan `next` @0fa109eb
(`vilan 0.40.0 (0fa109eb7)`), which is the toolchain every number below was measured
on. The owner is asked to rule §13 (four questions); the build is Order 39's, as S1
then S2.

Related: A54 (`KeyedCell`, CLOSED Order 31 — the machinery this lifts), A39
(`Delta`, the wire vocabulary), A98 (`each`'s settled-run order pass, CLOSED
Order 36), A110 (wave order — door 2 is the sibling paper, `reactive-turns.md`
§ "order within a wave"), A99 (the `each`/`map_each` naming argument), A111
(keep-alive `swap`, a paper-not-queued), B359 (the trait-default hijack, RULED R1 and
fixed this order by lane solver-38), `proposal/reactive-traits.md` §2–§4,
`proposal/transport-rpc.md` §8, `proposal/positional-slots.md` §3e,
`proposal/signal-cell-representation.md` §6.

Probes: `scripts/integration/sweeps/order38/papers-38/probes/` — nine programs and a generated-cost template,
each with its captured output, re-runnable with `probes/run_all.sh` (add `--cost` for
the callgrind leg). Every claim below that a probe can check is named beside its
probe.

---

## 1. The ask, and the answer up front

The owner asked for this:

```vilan
let my_list: Signal<List<str>> = Signal::new(List<str>::new());
let my_nums = my_list.map_collection(|x| { print("ran"); x.parse_f64().unwrap_or(0f) });
my_list.push("10.5"); // only one "ran"
```

…with a worry attached: doing it by intertwining signals and lists means
re-implementing every collection method on a cell, which is anti-DRY. Is there a
generic system, and does it extend to derivations of a different type?

**There is, it is 25 years old, and std already has half of it in the wrong layer.**
The system is a *change structure*: a type `A` gets a change type `ΔA` and an apply
`⊕`; every operator `f: A → B` gets a derivative `f': A → ΔA → ΔB`; the law is

```
f(a ⊕ da) == f(a) ⊕ f'(a, da)
```

For `map g` the derivative of "three elements arrived at position 4" is "three
*mapped* elements arrived at position 4" — `g` runs three times and **nothing else is
looked at**. Not N cache checks: zero. (Cai/Giarrusso et al., *A Theory of Changes
for Higher-Order Languages*, PLDI 2014; the shipped relatives are Jane Street
`Incr_map`, .NET DynamicData changesets, Solid's `mapArray`, and differential
dataflow.)

The DRY answer is separate and simpler: **the collection method names are trait
DEFAULTS over one primitive per shape.** `push(x)` is `splice(len, 0, [x])`,
`remove_at(i)` is `splice(i, 1, [])`, `clear()` is `splice(0, len, [])` — a dozen
one-liners written once and shared by every cell kind. Both receiver spellings work
on the shipped toolchain (§6), so the everyday `self` surface and the batch
`&mut self` surface stand on the same single primitive.

And the half std already has is `KeyedCell<K, T>` (A54, `rpc.vl`): a bounded op log,
per-consumer cursors, a lag fallback, and a `Source<List<T>>` view over the same one
notification. It lives in `std::rpc` because its product is `Delta<K, T>`, a
`std::wire` type. Lifting the log and the cursors into `std::reactive` behind a
shape-neutral op vocabulary is slice S1, and it moves no wire byte (§10).

The number that decides the order of the slices is not `map_each`'s. It is `each`'s:

> One push into a 1,000-row `each` costs **358,454,848 Ir** in `each`'s scan half
> today, and **22,347 Ir** on the delta path — a factor of **16,040**. And the scan
> half is **quadratic**: 95.1 M Ir at 500 rows, 358.5 M at 1,000, 1,369.9 M at 2,000
> (3.77× and 3.82× per doubling). `probes/each_cost_template.vl`,
> `probes/each_cost.out`.

That is §9, and it is a bug finding as much as a design argument: `reconcile`'s
key-matching scan is O(N²) per change and nothing in the tracker records it.

## 2. What the item asked for, restated as the three layers

1. **An op vocabulary per SHAPE, not per method.** Sequence:
   `Splice(at, removed, inserted)`, `SetAt(at, previous, value)`, `Reset(list)`,
   `Move(from, count, to)`. Map: `Put`/`Delete`. Set: `Add`/`Remove`. Positional is
   the sequence primitive; keyed addressing is a position index on top of it —
   exactly `KeyedCell.positions`.
2. **One delta-source trait** in `std::reactive`: a `Source<C>` that also answers
   `cursor()` / `drop_cursor(c)` / `since(c) -> List<Op>`. `KeyedCell`'s machinery,
   lifted. `std::rpc`'s keyed forward becomes ONE consumer translating sequence ops
   plus keys into `Delta<K, T>`; `Delta` stays the wire vocabulary and
   `std::reactive` still imports nothing from `std::wire`.
3. **Operators written once against the ops.** What an operator costs is decided by
   its algebra, and that is the "derivations of a different type" answer (§8).

Layer 2's coalescing is free and is already how the turn scheduler behaves: writes in
one turn produce ONE notification, and the consumer drains every op at the settle.
Measured — `probes/probe_law_randomized.vl` asserts exactly one notification per turn
across 400 turns of 1–4 ops each, and `probes/probe_keyed_cell_today.vl` shows the
shipped `KeyedCell` doing it today (four writes in one `turn`, one drain:
`Insert(4@3) Update(3) Remove(1) Insert(5@3)`).

## 3. The op vocabulary, per shape

### 3.1 Sequence — the primitive shape

```vilan
export enum SeqOp<T> {
	/// `removed` left, `inserted` arrived, both at `at`.
	Splice(i32, List<T>, List<T>),
	/// The element at `at` was `previous` and is now `value`.
	SetAt(i32, T, T),
	/// The collection BECAME this list.
	Reset(List<T>),
	/// `count` elements moved from `from` to `to`, unchanged.
	Move(i32, i32, i32),
}
```

Three of the four arms differ from A112 as filed, and each difference is a correction
the probes forced:

- **`Splice` carries the removed VALUES, not a count.** A112 wrote
  `Splice(at, removed, inserted)` without saying what `removed` is; it has to be a
  `List<T>`. The O(1) derivative of a fold over a group — `sum`, `count`, `mean` — is
  "add what arrived, subtract what left", and a count cannot say what left, so the
  operator would have to read the collection, which is the O(N) rerun this item
  exists to delete. The same payload is what makes an op invertible (undo; and
  `Delta::Remove(key)` in the wire translation needs the key of the element that
  *went*, which only the value carries). Measured: `probes/probe_fold_needs_removed.vl`
  — 400 random turns, a group-fold `sum` maintained purely from op payloads, 0
  failures against the naive sum, and the derivative looked at 1,324 elements where
  the rerun looked at 5,475. With `removed: i32` the `Remove` translation and the
  fold derivative are both unwritable.
- **`SetAt` carries both values**, for the same reason and at the same cost.
- **`Move` is in the vocabulary from S1.** A112 left it optional ("+ `Move` if a
  reorder should not be a Reset"). It should be admitted now, because adding an arm
  to a public op enum later is a breaking change to every `match` in every consumer,
  and because a reorder is exactly the case where the splice-pair encoding loses
  information a consumer needs: a `Splice` that removes an element and a `Splice`
  that re-inserts it are, to a per-element owner, a disposal and a rebuild. A `Move`
  says "same element, new place", which is what `each`'s row order pass and a
  per-element owner both need. The default derivative for a consumer that does not
  care is the splice pair. Nothing in S1 or S2 *emits* a `Move` (only a
  reorder-aware writer does), and `std::rpc`'s translator lowers it to
  `Delta::Reset` — which is what a reorder produces on the wire today — so `Delta`
  does not move.
- `Reset` is unchanged, and stays the honest escape hatch: the wholesale write, the
  lag fallback, and the compat path (§7).

`SetAt` is deliberately not `Splice(at, [old], [new])`, though it means the same
thing to the collection: for `map_each` and for `each` the two are different events
(an element changed in place, versus one left and another arrived), and the
difference is whether the per-element owner survives.

### 3.2 Map and Set

```vilan
export enum MapOp<K, V> {
	Put(K, Option<V>, V),   // key, what was there, what is there now
	Delete(K, V),
	Reset(Map<K, V>),
}

export enum SetOp<T> {
	Add(T),
	Remove(T),
	Reset(Set<T>),
}
```

Same rule: every arm carries what left. `Put`'s `Option<V>` is the difference between
an insert and an overwrite, which a group fold over the values needs.

These are recorded, not slated: nothing in the tracker asks for a reactive `Map` or
`Set` cell yet, and §8's `index_by`/`group_by` (List → Map) is the first consumer
that would. They are written here so that the delta-source trait's shape is chosen
against more than one collection.

## 4. The delta source — one struct, one thin trait

`KeyedCell` today is a cell plus six members of log machinery (`record`, `trim`,
`cursor`, `drop_cursor`, `since`, and the `keyed_log_limit` constant). Three cell
kinds want it — a local `ListCell`, the keyed cell, and an optimistic/remote cell —
and copying it three times is the anti-DRY failure one layer up from the one the item
complains about. So the recommendation is **a value type plus a forwarding trait**:

```vilan
/// One consumer's place in a log: the sequence number it has been told through.
/// Identified rather than compared, because two consumers may legitimately sit at
/// the same sequence.
export struct DeltaCursor {
	id: i32,
	at: Shared<i32>,
}

/// A bounded op log with per-consumer cursors — `KeyedCell`'s machinery, lifted
/// and made generic in the OP rather than in the collection.
export struct DeltaLog<O> {
	ops: Shared<List<O>>,
	version: Shared<i32>,
	base: Shared<i32>,
	cursors: Shared<List<DeltaCursor>>,
}

export impl DeltaLog<type O> {
	fun new(): DeltaLog<O>;
	/// Append one op. Trims FIRST, so a log whose consumers are all current holds
	/// one op and a log with no consumers holds (at most) the op just recorded.
	fun record(self, op: O);
	fun cursor(self): DeltaCursor;
	fun drop_cursor(self, cursor: DeltaCursor);
	/// Everything `cursor` has not been told, and advance it. A cursor behind
	/// `base` has lost history and is answered with `None`, which the CELL turns
	/// into its shape's `Reset`.
	fun since(self, cursor: DeltaCursor): Option<List<O>>;
	fun trim(self);
}

/// A source whose WRITES are its deltas. `C` is the collection, `O` its op.
/// vilan has no associated types (analyzer.rs:17031), so both are parameters.
export trait DeltaSource<C, O> with Source<C> {
	fun cursor(self): DeltaCursor;
	fun drop_cursor(self, cursor: DeltaCursor);
	fun since(self, cursor: DeltaCursor): List<O>;
}
```

`since` on the LOG answers `Option<List<O>>` and `since` on the SOURCE answers
`List<O>`: the log does not know what a `Reset` is for its op type, and the cell
does. That is the only place the two layers need to know about each other, and it is
three lines in each cell:

```vilan
fun since(self, cursor: DeltaCursor): List<SeqOp<T>> {
	match self.log.since(cursor) {
		Some(let ops) => ops,
		None => [SeqOp::Reset(self.get())],
	}
}
```

The bound `DeltaSource<C, O> with Source<C>` is what makes the operators generic in
the CELL rather than in `ListCell`: `map_each` takes an
`S: DeltaSource<List<T>, SeqOp<T>>`, so it serves the local cell, the keyed cell and
anything an app writes.

`keyed_log_limit = 1024` becomes `delta_log_limit` in `std::reactive`, with its
comment unchanged: in practice nothing reaches it, because a consumer drains at the
settle of the turn that wrote, so the log is as long as one turn's writes.

### 4.1 What the shipped machinery actually does — measured, and two corrections

`probes/probe_keyed_cell_today.vl` drives the real `KeyedCell` and prints:

```
no cursor: log=1 version=2 base=1
fresh cursor: since= (empty)
one turn, four writes: since=Insert(4@3) Update(3) Remove(1) Insert(5@3)
after drain: log=4 (trimmed to what the one cursor is owed)
parked past keyed_log_limit: since=Reset(1104)  base=1031 version=1106
two live cursors, one op: log=76
no cursors again: log=1
collection holds 1106 rows
```

Two things there are worth writing into the lifted doc comment, because they are
easy to state wrongly:

- **"With no cursors the log holds nothing" is off by one.** `record` trims and then
  pushes, so a log with no consumers holds exactly the op just recorded — `log=1`,
  not 0. Harmless, and the doc should say it.
- **The log is trimmed at the next WRITE, not at the drain.** After the one cursor
  drained four ops the log still held four (`log=4`); they go on the next `record`.
  A cell that is written once and then read forever holds one op's worth of history
  for ever. Also harmless, and also worth saying.

The lag path works exactly as A54 designed it: a cursor parked behind `base` gets one
`Reset` carrying the collection, and the log stays bounded by the limit even while
a parked cursor exists (`base` jumped to 1031 under 1,106 writes).

## 5. The law, as a property test

The law is only observable at a settle, where it reads:

```
derived.get() == source.get().map(g)
```

`probes/probe_law_randomized.vl` is that property test. A seeded MINSTD Lehmer
generator (`state * 16807 % 2^31-1`) drives 400 turns; each turn opens ONE `batch`
and draws 1–4 ops from `{push, insert_at, remove_at, set_at, clear, set(whole)}`,
biased to grow. Four readers watch one cell whose log limit is 30:

| reader | what it exercises |
|---|---|
| `derived` | `map_each(g)`, cursor always current |
| `mirror_near` | a cursor drained every 3rd turn — normally answered with OPS |
| `mirror_far` | a cursor drained every 20th turn — normally PAST `base`, answered with a `Reset` |
| the reference | the naive rerun, recomputed from scratch every turn |

Asserted every turn: the law for `derived`; the law for whichever mirror drained;
exactly ONE notification per turn whatever the op count; and the `g` call count.

```
turns=400 checks=555 failures=0
lagging cursors: ops drained=845 resets=56
g calls: incremental=1223 (splice/set_at=806, reset=414) naive-rerun=6651
final length 11, log held 30 ops, base 1006, version 1036
```

555 checks, zero failures, both cursor paths exercised (845 ops and 56 `Reset`s), and
the coalescing claim holds 400 times out of 400. The call-count split is the honest
shape of the win: 806 calls are the incremental ones (one per inserted or updated
element, which is the floor), 414 are the price of the generator's wholesale `set(whole)`
writes, and the naive rerun would have made 6,651.

The spot-check counts from `probes/probe_c_self_receivers.vl` are the same law read
at named events rather than at random:

```
seeded: calls=0
3 pushes: calls=3 derived=[4 4 1 ] law=true
remove_at(1): calls=3 derived=[4 1 ] law=true
extend x2: calls=5 derived=[4 1 2 4 ] law=true
insert_at: calls=6 derived=[4 2 1 2 4 ] law=true
set_at: calls=7 derived=[6 2 1 2 4 ] law=true
clear: calls=7 derived=[] law=true
set(whole) = Reset: calls=10 derived=[1 2 3 ] law=true
```

k pushes → exactly k calls; a `remove_at` → zero; `clear` → zero; `set(whole)` of
three elements → three. The owner's `print("ran")` example prints once.

**The pin S2 owes** is `probe_law_randomized.vl` as a corpus program with its
counters asserted rather than printed (the corpus gate compares emitted bytes, so
the assertions have to be in the program: a `panic` on a mismatch, and the printed
tail is the golden).

## 6. The receiver question — two traits, one primitive

The open question in A112 was the receiver: `List`'s mutators are
`external fun push(&mut self, ..)`, a cell handle's are `self`. Three probes, all
re-run on 0fa109eb:

### 6.1 Probe C — `self` receivers, the owner's spelling. WORKS.

```vilan
export trait SequenceCell<T> {
	fun size(self): i32;
	fun splice(self, at: i32, removed: i32, inserted: List<T>);

	fun push(self, value: T)                 { self.splice(self.size(), 0, [value]) }
	fun insert_at(self, at: i32, value: T)   { self.splice(at, 0, [value]) }
	fun remove_at(self, at: i32)             { self.splice(at, 1, []) }
	fun extend(self, values: List<T>)        { self.splice(self.size(), 0, values) }
	fun clear(self)                          { self.splice(0, self.size(), []) }
	fun truncate(self, length: i32)          { .. }
}
```

`impl ListCell<type T> with SequenceCell<T>` writes exactly TWO members — `size` and
`splice` — and inherits the rest. `let my_list: ListCell<str> = ..; my_list.push("10.5")`
on a plain `let`, no `mut`, which is what a cell handle should read like.
`probes/probe_c_self_receivers.vl`, output in §5.

### 6.2 Probe A — `&mut self` receivers, the batch surface. WORKS.

```vilan
export trait Sequence<T> {
	fun size(self): i32;
	fun splice(&mut self, at: i32, removed: i32, inserted: List<T>);

	fun push(&mut self, value: T)  { self.splice(self.size(), 0, [value]) }
	..
}
```

A `Tracked<T>` recorder — a plain list plus the ops that produced it — implements
only `size` + `splice` and inherits the rest; `cell.edit(|&mut list| ..)` hands the
body a `&mut Tracked<T>`, then appends the recorded ops and writes the value ONCE.
`probes/probe_a_mut_receivers.vl`:

```
one edit, four mutations: notifications=1 ops=4 calls=3 list=[c seed bbb ] derived=[1 4 3 ] law=true
fill<S: Sequence<str>>: notifications=2 ops=6 calls=5 list=[c seed bbb from-fill-1 from-fill-2 ] derived=[1 4 3 11 11 ] law=true
clear: notifications=3 ops=7 calls=5 list=[] derived=[] law=true
```

Four mutations inside one `edit`: **one notification, four ops**, correct contents,
and the law holds. This is the spelling that lets a body written against the BOUND
run on a recorder — `fun fill<S: Sequence<str>>(target: &mut S)` is in the probe and
works — which is the "generic code serves a list and a recorder alike" half of the
ask.

### 6.3 Probe B — `List<T>` itself adopting the trait. MISCOMPILES, and that is B359.

`impl List<type T> with Pusher<T> {}` type-checks and emits a call to a function
nothing defines. `probes/probe_b_list_adopts_trait.vl` on 0fa109eb:

```
face 1 — direct route:
inherent push x
inherent push x
count 2
face 1 — generic-bound route:
trait push
count 0
face 2 — List adopting the trait (expect ReferenceError):
	$e(self, value);
	^
ReferenceError: $e is not defined
```

This is B359 verbatim (the item reads `$b`; the gensym differs, nothing else does),
it is RULED R1 = (a) — inside a default body `self.name(..)` is the TRAIT's member,
always — and lane solver-38 fixes it this order. **This paper does not design around
it.** It is read as evidence for one thing only: the two routes to one default
disagreed on the shipped toolchain, and a design that put `List` among the
implementors would have been standing on the disagreement.

### 6.4 The answer

**ONE trait cannot serve both receiver kinds, and it does not need to.**

- `SequenceCell<T>` (`self`) is the everyday surface: `my_list.push(x)` on a cell
  handle.
- `Sequence<T>` (`&mut self`) is the `edit` surface, over a recorder — and, once
  B359's fix lands, over a plain `List<T>` too, which is what makes a body written
  against `Sequence<T>` reusable off the reactive graph entirely.
- Both stand on the SAME single primitive, spelled twice.

The duplication is the default one-liners twice: a dozen lines each way. §13 Q2 asks
whether a macro should stamp both from one list; the recommendation is no.

Side note, recorded in case it is not intended (it probably is): inside
`impl ListCell<type T>`, a bare `ListCell::new()` binds `T` from `Self` even against
a `ListCell<U>` annotation ("Expected ListCell<U>, but got ListCell<T>").
`ListCell<U>::new()` is the spelling, and every probe uses it. `Type::func` inside
its own impl reading as `Self::func` is consistent with B162's rule for
`Signal::new`.

## 7. Purity, the per-element owner, and the index hazard

`map_each(g)` runs `g` once per element, ever. So **`g` must be pure in the
element**: a `g` that reads another signal produces a value the operator will never
recompute, because there is no second op to recompute it from. That is not a defect
to be patched, it is what buys the cost table; the question is what the impure case
is served by.

Solid's answer is a per-element owner, and it is the right one — it is the `each` row
discipline (`browser/ui.vl` `place_each`'s `row_owners`) one layer down: an owner
minted on insert, disposed on remove and on `Reset`, and itself `take`n by the
enclosing boundary.

**But a per-element owner alone is wrong, and the probe is a crash.** The obvious
shape gives each element an owner and lets the element's effect write its result back
*at its index*. `probes/probe_per_element_index_hazard.vl`:

```
3 pushes: g=3 owners=3 derived=[2 3 4 ]
scale=10: element effects fired 3 derived=[20 30 40 ]
index out of bounds: the length is 2 but the index is 2
```

The effect captured `at` when its element was inserted; the next `Splice` shifted
every later element one place; the effect then wrote to a position that was not its
own — here, past the end. **A position is not an identity.** The element needs a
stable handle, and the handle that already exists in std is a per-element CELL: it is
what `each_by` hands its render closure (`place_each_by`, A42), and it is what the
derived collection should hold for a reactive element.

So the corrected shape, `probes/probe_per_element_owner.vl`: the derived cell is a
`ListCell<SignalCell<U>>`, each element's effect writes through its OWN cell, and the
owners are kept in step with the elements by the one loop that reads them at the
moment an op names a position.

```
3 pushes: g=3 owners=3 derived=[2 3 4 ]
scale=10: element effects fired 3 derived=[20 30 40 ]
after remove_at(1), scale=100: effects fired 2 derived=[200 400 ] g=3
reset([7,8]): disposed 2 owners, made 5 total, derived=[700 800 ]
after boundary.dispose(), scale=1000: effects fired 0 (expected 0)
owners made=5 disposed-by-hand=3 (the rest went with the boundary)
```

`g` runs 3 times and never again (`g=3` after the removal and after two more
changes of the second signal); a change of the second signal fires one effect per
LIVE element, so a removal takes its element out of the wave (3 → 2); a `Reset`
disposes every live element owner before minting new ones; and after the boundary is
disposed the second signal fires ZERO element effects.

**What this means for the slices.** `map_each`'s contract is "pure in the element",
`ListCell<U>` out, and that is S2. The reactive-element case belongs to the consumer
that definitionally has one — `each`, whose render closure builds DOM under an owner
— and that is S3, where the row owner already exists and the row cell already exists.
A standalone `map_each_by` returning `ListCell<SignalCell<U>>` is recorded here and
left to S4, if an exhibit asks.

**A110's ordering applies to the row discipline**, and this is the one place the two
papers touch: a per-element owner is created by the enclosing form's own effect, so
its subscriber id is strictly higher than that form's, and door 2's ascending-id rule
puts the parent's disposal before the child's build. Under today's subscription-order
wave the child can build for an element the parent is about to remove — which is
exactly A110 face 1, read at element granularity instead of at form granularity. See
`reactive-turns-order-within-a-wave.md` §7.3.

## 8. Operators as derivatives — the cost table

What an operator costs is decided by its algebra. This is the "does it extend to
derivations of a different type?" answer: yes, and the *extra state* column is the
price.

| operator | extra state | per op | status |
|---|---|---|---|
| `map_each(g)` | the output list | 1 call of `g` per inserted/updated element | MEASURED (§5) |
| group fold — `sum`, `count`, `mean` | the accumulator (needs an inverse) | O(1) | MEASURED (§3.1) |
| `filter_each(p)` | kept flags + index translation (Fenwick) | 1 call of `p`, O(log N) | by construction |
| `sort_by(key)` | order-statistic tree | O(log N) | by construction |
| monoid-only fold — `min`, `max`, `concat` | segment tree | O(log N) | by construction |
| arbitrary fold | — | O(N) rerun, honestly labelled | by construction |
| `index_by` / `group_by` (List → Map) | the map | O(1), emits `MapOp`s | by construction |
| `each` (the UI consumer) | its rows | O(|op|) instead of O(N²) | MEASURED (§9) |
| joins / `flat_map` | — | out of scope (differential dataflow) | — |

Two rows are measured on this toolchain, one is measured as a *deletion* rather than
as an operator, and the rest are the standard algebra, written here so the paper is
honest about which is which. The table's shape is A112's; the two MEASURED rows and
the `each` row are this paper's additions, and the `Splice`-carries-values correction
in §3.1 is what makes the group-fold row possible at all.

The distinction the table turns on — group versus monoid — is why "write it once over
the ops" is a real claim rather than a slogan: `sum` has an inverse, so a removal is a
subtraction; `min` does not, so a removal has to re-derive from a tree. Both are
written against the same four `SeqOp` arms.

## 9. `each` is the operator that matters — measured

A112's own aside is the load-bearing claim: "`each` is one more consumer — it applies
ops to its rows directly instead of `reconcile`-ing the whole list per change, which
for UI is the bigger win than `map_each`". It is, by four orders of magnitude.

**What `each` does today, per change.** `place_each`'s effect reads three `Shared`
lists out (three N-element copies), calls `reconcile(old_keys, old_items, list, key,
same)`, runs A98's two `settled_steps` scans and `row_references`, then four more
O(N) bookkeeping loops, then writes three fresh N-element lists back. A98 (CLOSED
Order 36) fixed the DOM half of this — at 1,000 rows an append went from 1,000 row
cuts to 0 and from ~4,000 host insertions to one — and left the SCAN half alone.

**`reconcile` is quadratic.** Its inner loop walks `old_keys` from index 0 for every
new item, skipping `claimed` entries:

```vilan
for item in items {
	let item_key = key_of(item);
	mut index = 0;
	for index < old_keys.len() {
		if !claimed[index] && old_keys[index] == item_key { .. jump break; }
		index += 1;
	}
}
```

For a list that did not reorder, item *i* matches at index *i* and walks *i+1*
entries to get there, so a pass is N(N+1)/2 iterations — 500,500 at 1,000 rows,
whatever the change was.

**Measured.** `probes/each_cost_template.vl` generates two programs from one source:
the scan path (`reconcile` + A98's scans + the bookkeeping loops, with the DOM calls
removed and nothing else changed) and the delta path (one `Splice` applied to the row
list in place, no keys and no items held at all). Both keep their state in `Shared`
cells exactly where `place_each` keeps it, so the copies each one really pays are
counted. Per-change Ir is the slope between two repeat counts, so node's startup and
the initial N-row build cancel. callgrind Ir under `node --jitless`;
loadavg 16.3–20.7 across the runs (nine other lanes were building — Ir is an
instruction count and does not move with load, and the loadavg is recorded per the
Mechanics rule).

| | per-change Ir |
|---|---|
| `each`'s scan half today, 1,000 rows | **358,454,848** |
| the delta path, 1,000 rows | **22,347** |
| ratio | **16,040×** |
| scan half, 500 rows | 95,084,350 |
| scan half, 2,000 rows | 1,369,893,884 |

3.77× from 500 to 1,000 and 3.82× from 1,000 to 2,000: quadratic, confirmed
empirically as well as by reading the loop. A cross-check without the slope agrees to
1.2% (`probes/each_cost.out`).

The DOM half is excluded from both sides deliberately: A98 already measured and
pinned it, and a probe cannot call the DOM under node. So the 358 M Ir is work the
delta path **deletes**, not work it shrinks — on the delta path there is no plan, no
key list, no item list and no settled-run scan, because the op already says where the
change is.

**This is also a FIND.** Nothing in the tracker records `reconcile`'s quadratic scan;
A54 recorded the O(N) keyed-diff cost on the wire and A98 the DOM mutation count.
It is filed in the report as a candidate item, and it is a reason to take S3 even if
S2 is deferred: a `List`-valued `SignalCell` feeding `each` pays it today, at every
change, at 1,000 rows and up.

## 10. `KeyedCell` after the lift

`KeyedCell<K, T>` becomes **a `ListCell<T>` plus a position index by key hash plus
the wire translation**, and nothing else moves:

- **Its public surface is unchanged**: `new`, `insert`, `remove(key)`,
  `update(key, |&mut T|)`, `set`, `locate`, `cursor`, `drop_cursor`, `since`, plus
  `Source<List<T>>`. `since` keeps returning `List<Delta<K, T>>` — it is the one
  translating consumer, reading `SeqOp<T>` out of the lifted log and mapping it:
  `Splice(at, [], [x])` → `Insert(x.key(), x, at)`, `Splice(at, [old], [])` →
  `Remove(old.key())` (which is why §3.1's removed values are required),
  `SetAt(at, _, v)` → `Update(v.key(), v)`, `Move` → `Reset`, `Reset` → `Reset`.
- **The `Patch` frame does not move**, `Delta` does not move, and the service hash of
  a handle-free service stays byte-identical (78bdada7's pin). `std::reactive` still
  imports nothing from `std::wire`: `SeqOp` is a `std::reactive` type, `Delta` a
  `std::wire` one, and the edge between them lives in `std::rpc`, where it lives
  today.
- **`T: Keyed<K>` stops being a requirement of the LOG** and becomes a requirement of
  the keyed cell only. That is the whole reason a `List<str>` can have a delta source
  at all: `KeyedCell` demands keys because its consumer is a wire protocol that
  addresses elements by key, and a local derivation addresses them by position.
- `keyed_log_limit` → `delta_log_limit`, in `std::reactive`, with `KeyedCell` reading
  it from there. A54's sentence about it stands: in practice nothing reaches it.
- `KeyedCursor` → `DeltaCursor`. It is `export`ed, so this is a rename in a public
  surface; §13 Q4 asks how it is spelled after the lift.

What the lift is *not*: it is not a behaviour change. S1's exit test is that every
existing rpc pin — `reactive-keyed`, the keyed forward's, `expose_keyed_cell`'s
byte-identical hash pin — passes unchanged, and that the ratio pin A54 landed (10×
rows costs < 3×) still reads what it read.

## 11. The compat path, and cursor lifetime

### 11.1 `set(whole_list)`

A plain `set(list)` records `Reset`, and `Reset`'s derivative is N calls of `g`.
That is the honest answer: replacing N elements costs N derivations, and the probe
shows it (`set(whole) = Reset: calls=10` for three elements over a seven-call
history).

A112 offers a second door — diff the whole list into ops when `T: PartialEq` or
`T: Keyed<K>`, paying N cheap compares for zero derivations on retained elements —
and `reconcile`/`keyed_diff` already exist to do it. **The recommendation is that
this is NOT what `set` does.** A silent O(N) compare inside a setter is the cost
this item exists to remove, and §9 is the measurement of what a hidden per-change
scan is worth. A caller who genuinely holds a whole new list and wants element
preservation should say so, at its own name:

```vilan
fun reconcile_to(self, list: List<T>)        // ListCell<T: PartialEq>
```

which diffs and records the resulting ops. `set` stays `Reset`. A plain
`SignalCell<List<T>>` adapts through the same door: it has no log, so anything
derived from it is on the `Reset` path by construction, which is exactly today's
behaviour and exactly what "a `SignalCell` is not a delta source" should mean.

### 11.2 Cursor lifetime

Three rules, all forced by the machinery rather than chosen:

1. **A derived cell's cursor pins the log.** `trim` keeps everything the laggiest
   live cursor is owed, so a cursor nobody drains holds history until the limit drops
   it — measured: with a cursor parked at sequence 6 under 1,106 writes the log held
   76 ops and `base` had jumped to 1031, so the memory stayed bounded and the parked
   consumer got a `Reset` (§4.1).
2. **The cursor is dropped by the owner the derivation was made under.**
   `register_with_owner`'s rule (A28): a derivation made inside a boundary dies with
   it, one made at module level lives as long as its source. `drop_cursor` goes in
   the same `Subscription::release` hook that `KeyedCell`'s forward already uses.
3. **A derivation with no subscribers should hold no cursor** — A112's third bullet.
   The recommendation is to **not** do this in S2, and to say why rather than leave
   it implied: `map` does not do it either. A `map` derivation subscribes eagerly at
   construction and recomputes whether or not anything reads the result; making
   `map_each` lazy would make it the only lazy derivation in `std::reactive` and
   would put a second lifecycle rule beside A28's. If lazy derivations are wanted
   they are wanted for `map` too, and that is a different paper. What `map_each`
   should do is the cheap half: `drop_cursor` on disposal, so a dead derivation stops
   pinning history. Rule 1 then bounds the cost of the eager choice.

## 12. Slices

### S1 — the lift (M)

`DeltaCursor`, `DeltaLog<O>`, `DeltaSource<C, O>` and `delta_log_limit` into
`std::reactive`; `SeqOp<T>`, `MapOp<K, V>`, `SetOp<T>` beside them; `KeyedCell`
re-based on the log, keeping its whole surface and translating `SeqOp` → `Delta` in
`since`. `KeyedCursor` becomes a re-export of `DeltaCursor` (or is renamed with a
migration note — §13 Q4).

**Exit:** every existing rpc pin green unchanged, including
`expose_keyed_cell`'s byte-identical service-hash pin and A54's ratio pin; a new
`-p vilan-core --test inference` pin that `std::reactive` imports nothing from
`std::wire` (a grep pin is honest here and cheap); the log's two documented
off-by-one behaviours (§4.1) pinned as stated rather than as assumed. **Goldens
move** — std source changes, so `std::reactive`'s emitted bodies change; regenerate
after run verification.

### S2 — `ListCell` and the two traits (M–L)

`ListCell<T>` (a `SignalCell<List<T>>` + a `DeltaLog<SeqOp<T>>`); `SequenceCell<T>`
with `size` + `splice` required and a dozen defaults; `Sequence<T>` with the
`&mut self` primitive and the same dozen; `Tracked<T>` and
`ListCell::edit(|&mut list| ..)`; `map_each(g)` over any
`S: DeltaSource<List<T>, SeqOp<T>>`; `reconcile_to` for the compat door.

**Exit:** `probe_law_randomized.vl` as a corpus program with its counters asserted
(a `panic` on a mismatch), `probe_c_self_receivers.vl`'s and
`probe_a_mut_receivers.vl`'s call counts as `reactive_lifetimes` cases, the
four-mutations-one-notification pin, and a `List<str>` walking the owner's original
example with one `ran`. Needs B359's fix only if `List<T>` is put among the
implementors, which S2 does NOT do (the recorder and the cells are the
implementors); doing it is a one-line addition once solver-38's fix has landed, and
is worth a pin of its own then.

### S3 — the delta-driven `each` (M)

`each` becomes a `DeltaSource` consumer: on `Splice`/`SetAt`/`Move` it applies the op
to its rows directly (`open_row_before` / `cut_row` / `insert_row` / row-owner
disposal, all of which A91 and A98 already built), and it keeps the reconcile path
for a `Reset` and for a plain `Source<List<T>>`. The per-element owner discipline is
§7's, with the row cell as the stable handle.

**Exit:** the §9 measurement as a pin — one push into 1,000 rows runs zero
`reconcile` passes and builds one row (the shape A98's pin already asserts, extended
to the plan count); `ui_rows` and `ssr_differential` unchanged for a `Source`-fed
`each`; the process twin gets the same consumer or a sentence saying why not.
**This is the slice with the measured need**, and if only one slice is built it
should be this one plus the S1 it stands on.

### S4 — the second-order operators (M+, deferred)

`filter_each(p)` with its Fenwick index translation; the group folds
(`sum`/`count`/`mean`) whose derivative §3.1 measured; `map_each_by` returning
`ListCell<SignalCell<U>>` for a reactive element; `index_by`/`group_by` if a `MapOp`
consumer appears. Each is an exhibit's to ask for, and each is written against the
same four arms.

Sizing: S1 M + S2 M–L + S3 M + S4 M+ — the first three are one order's work, S4 is
demand-driven. B359 rides beside, not in front.

## 13. Open questions, each with a recommendation

> **RULED (the owner, 2026-09-21) — all four as recommended.** Q1 `map_each` / `filter_each`; Q2 two
> hand-written default lists, no macro; Q3 `Move` is an op from S1 (the wire translator lowers it to
> `Delta::Reset`); Q4 `KeyedCursor` → `DeltaCursor` in `std::reactive`, with a deprecated re-export in
> `std::rpc` for one release. The two decisions this paper made without asking stand (`Splice` carries the
> removed VALUES; `set(whole)` records `Reset`, the diff door is `reconcile_to`). Slice order: S1 (the
> lift) → S3 (the delta-driven `each`) → S2 (`map_each`). Order 39's.

**Q1 — the names.** `map_each` / `filter_each` beside `each`, or `map_collection`
(the owner's word), or `map_incremental`?

> **Rec: `map_each` / `filter_each`.** A99's naming argument applies exactly: the
> forms are named for what they iterate, `each` is the name the collection surface
> already has, and `_each` is then a suffix that means "element-wise, incrementally,
> one call per element" in three places instead of a new word in one.
> `map_collection` says the wrong thing — the whole point is that it does *not* map
> the collection.

**Q2 — one macro stamping both traits' defaults, or two hand lists?**

> **Rec: two hand lists.** It is twelve one-liners twice. A macro buys 12 lines and
> costs a macro: the engine's expansion in every diagnostic that touches a default
> body, a second place to look when `push` misbehaves, and an `#[expand]`-shaped
> dependency between `std::reactive` and the macro engine that nothing else in the
> reactive core has. Revisit if a third receiver kind appears.

**Q3 — `Move` as an op, or a `Reset`?**

> **Rec: `Move(from, count, to)` IS an op, admitted in S1.** §3.1 argues it: adding
> an arm to a public op enum later breaks every consumer's `match`, and a reorder is
> precisely where the splice-pair encoding loses the fact that the element is the
> same one — which a per-element owner and `each`'s order pass both need. Nothing in
> S1/S2 emits it; the wire translator lowers it to `Delta::Reset`, which is what a
> reorder sends today, so `Delta` does not move.

**Q4 — `KeyedCursor`: re-export or rename?** S1 makes the cursor shape-neutral, and
`KeyedCursor` is `export`ed from `std::rpc`.

> **Rec: rename to `DeltaCursor` in `std::reactive`, and keep
> `export let KeyedCursor = DeltaCursor`-shaped re-export in `std::rpc` for one
> release**, deprecated per `proposal/deprecation.md`. Nothing in the tree names the
> type outside `rpc.vl` (the census is S1's first task and is expected to read zero
> outside std), so the re-export is for app code we cannot see. A hard rename is the
> alternative and is a `breaking` note on a type no app has any reason to hold.

Two things this paper has decided rather than asked, and will re-open if the owner
disagrees: `Splice` carries the removed values (§3.1 — measured, and the keyed
translation is unwritable without it), and `set(whole_list)` records `Reset` with the
diff door at its own name `reconcile_to` (§11.1).

## 14. What this does not do

- **Joins and `flat_map`** — differential dataflow territory, out of scope, and the
  cost table says so rather than pretending.
- **Lazy derivations.** §11.2: `map_each` is as eager as `map`, and making either
  lazy is a different paper.
- **A reactive `Map` or `Set` cell.** `MapOp`/`SetOp` are recorded so the trait's
  shape is chosen against more than one collection; nothing asks for the cells.
- **Value staging.** `reactive-turns.md` §4's honest limit is unchanged: ops isolate
  notification, not value.
- **A111's keep-alive.** A parked subtree's cursor is a live cursor, so keep-alive
  and cursor lifetime meet; that meeting is A111's to describe, and A111 stays a
  paper-not-queued.
- **B359.** Ruled and fixed elsewhere this order. §6.3 reads its probe as a bug.
