# Reactive maps and sets — the Map and Set shapes, and the order a hash collection keeps (A138, I10)

> Status: **DRAFT, for ruling** (2026-09-29). Tracker A138, with I10 folded in:
> an ordered map is a shape question, so the ordering strategy is decided here.
> Written by lane papers-44 of Order 44 against `vilan 0.41.1 (07e8db372)`, while
> the same order builds I9's rename. Names below are I9's: `HashMap<K, V>` in
> `std::hash_map` and `HashSet<T>` in `std::hash_set`. The probes still spell
> `Map`/`Set`, because that is what 0.41.1 has. Nothing in the compiler or std
> changed. Every claim about today's behaviour is a probe that was run or a line
> that was read (std paths under `vilan/std/src/`, kolt paths under `kolt/src/`,
> runtime paths under `crates/`).
>
> Probes: `scripts/integration/sweeps/order44/papers-44/probes/maps/`, re-run by
> `probes/run_all.sh`, output in `probes/run_all.out`.
>
> Related: A142 (`reactive-layers.md` §6: collections per shape, R9, R23, R33),
> A142 S7 (`store.md`, this order's sibling paper: a store's map field is this
> paper's keyed node), A112 (`incremental-collections.md` §3.2, where `MapOp` and
> `SetOp` were recorded "not slated"), A54 and A79 (`KeyedCell`), I1
> (`hashable-keys.md`), I8 (`get_or_insert`, its maps half), I9 (the rename), A39
> (`Delta`, the `Patch` frame).

## 0. The ask, and the answer up front

A138 asked for reactive hash maps and sets at parity with `ListCell`:

- writes that ARE the deltas;
- an `each_by` over a map's entries driven by ops;
- a keyed `Patch` over the wire driven by ops;
- a census of `KeyedCell<K, T>` (`rpc.vl`), which "is a keyed collection cell
  whose writes ARE deltas": is it already the reactive map with a list face?

I10 asked whether the hash collections should take an injected ordering
strategy, and said a native `HashMap` iterates "in none".

**The answer.**

1. **Per-key tracking is the reason to build this.** kolt reads one message out
   of a coarse map with `messages.map(|x| x.get(message)).cell()`
   (`kolt/src/store.vl:257`). With 1,000 keys observed that way, 1,000
   single-key writes run **1,000,000 projections in 30.5 s**. A toy `MapCell`
   whose `at(key)` depends on that key only runs **1,000 observers in 1 ms**
   (`per_key.vl`, §1.3).
2. **`KeyedCell` is an insertion-ordered map whose values carry their key,
   shown as a list.** Its surface is a map's: insert-or-replace, remove by key,
   update by key, a wholesale set. Its machinery is a sequence's: a positional
   log and a position index that every removal re-indexes. So a removal from the
   front costs O(n): **412 ms** for 1,000 front removes from 10,000, against
   **12 ms** from the back. It has no per-key subscription: every write wakes
   every observer (§2). **Rec**: build `MapCell`, then re-found `KeyedCell` on it
   with its surface and wire bytes unchanged (S3).
3. **The Map and Set shapes are recorded and unused.** `MapOp` and `SetOp` exist
   in `delta.vl` with the "what left" payloads the fold derivatives need, and a
   `DeltaLog<MapOp<K, V>>` works as it stands (§1.1). This paper slates them.
4. **Order is already pinned, and the item's premise is stale.** Since F1 S1a the
   native `Map` is an index map, **insertion-ordered because a JS `Map` is**
   (`crates/vilan-rt/src/lib.rs`, `pub struct Map`). Both backends print the same
   order after an overwrite, a remove and a re-insert (`order.vl`). What is left
   is to pin the remove-and-re-insert case and to fix one native defect: removed
   keys are never compacted (§6.1; §8, find 1).
5. **The ordering decision (I10).** A map's *op vocabulary* is order-free, and
   only its *positional face* (`entries()`, `each_by`) sees an order. So:
   - insertion order is the contract of `HashMap`/`HashSet`;
   - an order by key is a separate `SortedMap`/`SortedSet` whose comparator is a
     constructor **value**, not a type parameter;
   - an order by anything else is a view, `entries().sort_by(..)`, which the
     reactive side maintains in O(log n) per op and seals with `.memo()`.

   Door (a), a strategy type parameter on every hash map, is declined (§6.3).

## 1. Ground truth

### 1.1 The shapes as recorded

`delta.vl` carries both op enums, marked "Recorded, not slated: nothing asks for
a reactive `Map` cell yet":

```vilan
export enum MapOp<K: Hashable, V> {
	Put(K, Option<V>, V),   // the key, what was there, what is there now
	Delete(K, V),           // the key and the value that left
	Reset(Map<K, V>),
}

export enum SetOp<T: Hashable> {
	Add(T),
	Remove(T),
	Reset(Set<T>),
}
```

`per_key.vl` records them through std's own `DeltaLog` with no change. A cursor
taken before two puts, two removes (one of them of an absent key) reads:

```
Put(3, Some(429), 99)
Put(3, Some(99), 100)
Delete(3, 100)
```

The absent remove recorded nothing. `KeyedCell` follows the same rule: "no op is
recorded, so nothing crosses the wire".

### 1.2 The customers

| Site | Today | What it wants |
|---|---|---|
| `kolt/src/store.vl:108` `channels: SignalCell<Map<u53, ChannelRecord>>` | a coarse cell; writes by `update(\|&mut m\| m.insert(..))` | a `MapCell`; `insert` is a `Put` |
| `kolt/src/store.vl:110` `messages: SignalCell<Map<u53, Message>>` | the same | the same |
| `kolt/src/store.vl:257` `get_message` | `messages.map(\|x\| x.get(message)).cell()`: one projection per asked id, every one rerun on every write | `messages.at(message)` (§4) |
| `kolt/src/store.vl:196` `get_channels` | `channels.map(\|x\| x.keys()).cell()`: every write rebuilds the key list | `channels.keys()`, a set pipe (§5) |
| `kolt/src/store.vl:111` `users: Memo<UserId, SignalCell<Option<User>>>` | a hand-kept map of cells (`memo.vl`, I8) | `get_or_insert` on a map; the cells are per-key handles |
| `kolt/src/prefs.vl:20` `last_used_commands: StorageSignalCell<Map<usize, Instant>>` | a storage-backed coarse map | stays coarse: it is small and persisted whole |
| `rpc.vl` `expose_keyed_map` | a map exposed by diffing two snapshots per change per connection (`keyed_diff`) | `expose_map_cell`, op-driven (§7) |

The per-key precedent is already in std. `Selector` (`reactive.vl`) keeps one
`SignalCell<bool>` per *asked* key, in a `NativeMap` keyed by `key.hash()`, and
two writes per change "whatever the row count". `at(key)` is `Selector`'s shape
with a value in it.

### 1.3 Per-key tracking, measured

`per_key.vl` has two arms over the same 1,000 keys, each key observed once,
then 1,000 writes to single keys:

- **coarse**: kolt's shape. One `SignalCell<Map<i32, i32>>`, and per key
  `all.map(|m| m.get(key)).cell()`.
- **keyed**: a toy `MapCell`, which is a `Shared<Map<K, V>>`, a
  `DeltaLog<MapOp<K, V>>`, one whole-map notification, and a per-key
  `SignalCell<Option<V>>` minted on first `at(key)`.

```
coarse: n=1000 writes=1000 projection_runs=1000000 observer_calls=1000000 ms=30523
keyed:  n=1000 writes=1000 observer_calls=1000 ms=1
```

The coarse arm's cost is not only the million runs. Each run receives the whole
map as a value: the `map` node reads its source with `get()`, and
`SignalCell::get` copies the value out. So each run copies a 1,000-entry map,
about 30 µs a run. A CPU profile of the arm puts 60% of its time in the JS
emit's `__clone`, and 18% in the collector. Every coarse observer also wakes,
because `.cell()` never compares (R7).

`probes/run_all.out` shows the same counts. Its wall times were captured with the
machine's load average near 60, with other lanes building, and read 168 s and
11 ms.

### 1.4 Order, measured

`order.vl` inserts `a b c`, overwrites `a`, removes `b`, re-inserts `b`, and
inserts `d`:

```
[ 'a', 'c', 'b', 'd' ]     keys, JS and native alike
[ 10, 3, 20, 4 ]
[ 3, 2, 1 ]                 a set: insert 3 1 2, duplicate 3, remove 1, insert 1
[ 5, 1, 3 ]                 to_map from pairs
```

An overwrite keeps its place. A removed and re-inserted key goes to the end. The
two backends agree. The native runtime says why (`crates/vilan-rt/src/lib.rs`,
`pub struct Map`):

> `Map<K, V>` — INSERTION-ORDERED, because a JS `Map` is and the differential
> compares what a program prints when it walks one.

Its layout is a `HashMap<K, usize>` index over a `Vec<Option<(K, V)>>` of entries.
`native_differential.rs` pins the overwrite case ("A re-insert keeps the ORIGINAL
position"). It does not pin remove-then-re-insert. std's own doc comments already
promise the order (`map.vl` `keys`: "in insertion order"; `set.vl`: "`for x in
set` yields real `T`s in insertion order").

**Find 1.** A removal takes the entry (`self.entries[slot].take()`) and never
compacts the vector. A native map that has churned through many keys walks
every tombstone on every iteration. Release builds, three runs each
(`churn_native_*.vl`, timed from outside):

| Keys churned through (one live at the end) | Key walks | user CPU |
|---|---|---|
| 0 | 2,000 | 0.000–0.001 s |
| 200,000 | 0 | 0.005–0.015 s |
| 200,000 | 2,000 | 0.130–0.162 s |

That is about 60 µs a walk to find one key, where the JS `Map` takes 1–2 ms for
all 2,000 walks (`churn.vl`). Memory is held the same way: 200,000 dead slots
for a map of one.

## 2. `KeyedCell`, censused against a map face

### 2.1 What it is

`KeyedCell<K, T: Keyed<K>>` (`rpc.vl`) is, in its own doc's words, "a sequence
cell, plus a position index by key hash, plus the wire translation". It holds:

- `elements: SignalCell<List<T>>`: the collection and the one notification;
- `positions: Shared<Map<Hash, usize>>`: where each key sits;
- `log: DeltaLog<SeqOp<KeyedElement<K, T>>>`: positional ops, with the key
  carried on each element so the wire translation never re-keys.

### 2.2 Against a map face

| | `KeyedCell` today | A map face |
|---|---|---|
| Keyed by | the element, `T: Keyed<K>`, projected once per write | the map's key; `V` carries nothing |
| Order | insertion: `insert` appends a new key and replaces a held one in place | insertion (§6) |
| Writes | `insert(value)` (append or replace), `remove(key)`, `update(key, f)`, `set(list)` | `insert(k, v)`, `remove(k)`, `update(k, f)`, `clear`, `set(map)`, `reconcile_to(map)`, `get_or_insert(k, make)` |
| Reads | `Source<List<T>>`; `locate(key)`: a snapshot `(position, element)` | `Source<HashMap<K, V>>`; `get(k)`; **`at(k)`, a per-key source** |
| Subscriptions | one, the list's: two updates to two keys wake the list observer twice (`keyed_census.vl`) | per key |
| Op log | positional `SeqOp`, translated to `Delta` in `since` | keyed `MapOp`, order-free; the positional face derives `SeqOp` (§5) |
| Remove | O(n): `remove` re-indexes everything after the hole (`reindex(list, at)`) | O(1) keyed, O(log n) for the positional face's rank |
| A set | `KeyedCell<str, str>` with `impl str with Keyed<str>` works (`a,b,c`) | `SetCell<T>` |
| The wire | op-driven `Patch` (`expose_keyed_cell`) | op-driven `Patch` from `MapOp`, no `key_of` (§7) |

The remove row, measured (`keyed_census.vl`):

```
remove x1000 from 10000: front ms=412 back ms=12
```

The same probe under the captured run's load read 942 and 2.

### 2.3 The verdict

The item's hypothesis holds for the *surface*: every `KeyedCell` operation is a
map operation on an insertion-ordered map whose value knows its own key, and its
`Source<List<T>>` is that map's values in order. It is false for the
*machinery*: `KeyedCell` is built as a sequence, so it pays a sequence's
re-index on removal, and it cannot offer a per-key subscription without a second
index.

**Rec.** `MapCell<K, V>` is the primitive. `KeyedCell<K, T>` becomes a thin
wrapper over a `MapCell<K, T>`:

- `insert(value)` is `insert(value.key(), value)`;
- its list face is the values in insertion order;
- its positional ops come from the map's rank index (§5);
- its `since` translation reads `MapOp` instead of `SeqOp`.

A54's pins hold unchanged: the byte-identical service hash, the re-key-nothing
pin, and the 10× rows < 3× cost ratio. The front removal drops to O(log n). That
is S3.

## 3. The cells

### 3.1 Names

The shapes are named `MapOp`/`SetOp`, not after a type. The cells follow the
shapes:

- **`MapCell<K, V>`**: a cell of the Map shape, backed by a `HashMap<K, V>`;
- **`SetCell<T>`**: a cell of the Set shape, backed by a `HashSet<T>`.

`ListCell` already fits, since `List` is the sequence shape's one type. The
alternative, `HashMapCell`/`HashSetCell`, names the backing, and a sorted cell
would then need a type of its own. Under this paper's order decision (§6) it
does not: the order is a constructor value on the cell's positional face (Q1).

Both live beside `ListCell` (`delta.vl`, re-exported from `std::reactive`).

### 3.2 `MapCell<K: Hashable, V>`

Handle receivers (`self`), like `ListCell`: a copy of the handle is the same cell.

| Member | Op recorded | Notes |
|---|---|---|
| `new()`, `of(map)` | nothing | a cursor minted after reads the map as its start |
| `insert(k, v)` | `Put(k, previous, v)` | `previous` is `None` for a new key |
| `remove(k)` | `Delete(k, v)` | an absent key records nothing and publishes nothing |
| `update(k, mutate: sync \|&mut V\| void)` | `Put(k, Some(before), after)` | in place; an absent key is a no-op |
| `get_or_insert(k, make: \|\| V): V` | `Put(k, None, made)` on a miss | I8's maps half; a hit records nothing |
| `clear()` | `Reset(empty)` | |
| `set(map)` (`Signal`) | `Reset(map)` | never compares (R7) |
| `reconcile_to(map)` (`V: PartialEq`) | `Put`/`Delete` per changed key | the compat door, as `ListCell::reconcile_to` |
| `edit(body: sync \|&mut TrackedMap<K, V>\| void)` | one op per mutation, one notification | the batch door, as `ListCell::edit` |
| `get(k)`, `contains_key(k)`, `len()`, `peek(read)` | — | reads; `peek` lends the map in place (M86) |
| `at(k)` | — | the per-key handle (§4) |

It implements `Source<HashMap<K, V>>`, `Signal<HashMap<K, V>>` and
`DeltaSource<HashMap<K, V>, MapOp<K, V>>` (`cursor`, `since`, `reader`), over
one `DeltaLog<MapOp<K, V>>`. A lagging cursor gets `Reset(map)`. The structure
is `ListCell`'s: the map in a `Shared`, the notification in a
`SignalCell<i32>`, and the op recorded before the one notification.

### 3.3 `SetCell<T: Hashable>`

| Member | Op | Notes |
|---|---|---|
| `insert(x): bool` | `Add(x)` if new | `true` when it was new; a held element records nothing |
| `remove(x): bool` | `Remove(x)` if held | |
| `clear()`, `set(set)` | `Reset` | |
| `reconcile_to(set)` | `Add`/`Remove` per difference | no `PartialEq` needed beyond `Hashable`'s |
| `contains(x)` | — | the per-element handle, `Source<bool>` (§4) |

A138 asked whether a set adds anything beyond `MapCell<T, void>`. A
`Map<str, void>` does work (`void_value.vl`). The set is still its own type over
a shared body, for two reasons. Its op vocabulary is smaller: `Add` carries no
"what was there". And its read face is `contains(x): bool`, not
`at(x): Option<void>`. An alias would hand set consumers `Put(x, Some(()), ())`.

### 3.4 The faces

R23 gave sequences `CollSource<T>` (read), `CollSignal<T>` (the write trait) and
`ListCell<T>` (the cell), and R33 gave `CollPipe<T>` (an operator's move-only
result). The Map and Set shapes get the same four:

| | Map | Set |
|---|---|---|
| read trait | `MapSource<K, V>`: `get`, `at`, `keys`, `values`, `entries`, plus the delta feed | `SetSource<T>`: `contains`, `len`, plus the delta feed |
| write trait | `MapSignal<K, V>`: the writes of §3.2 | `SetSignal<T>`: the writes of §3.3 |
| cell | `MapCell<K, V>` | `SetCell<T>` |
| pipe | `MapPipe<K, V>`, sealed with `.memo()` into a `MapSource` | `SetPipe<T>` |

vilan has no associated types, so a shape's op is a trait *parameter* (A112 §4).
`MapSource<K, V>` is declared `with DeltaSource<HashMap<K, V>, MapOp<K, V>>`.

## 4. Per-key tracking: `at(key)` and `contains(x)`

`map.at(k)` is a copyable handle, the map plus a key:

- It implements `Source<Option<V>>`: `get()` reads the key, and a subscription
  lands on that key's **slot**.
- It implements `Signal<Option<V>>`: `set(Some(v))` is `insert(k, v)`, and
  `set(None)` is `remove(k)`.

A slot is a notification-only `SignalCell`, allocated when the first
subscription arrives and kept in a table keyed by `k.hash()`, as `Selector`
does. Writing key `k` wakes `k`'s slot if one exists: one hash probe per op, and
nothing for keys nobody watches. `Reset` wakes every live slot, because a reset
cannot say which keys changed without comparing, and a cell never compares
(R7). `reconcile_to` wakes only the keys it recorded.

**Slot lifetime.** `Selector::of` defers a key's removal to the ambient owner,
because its handle is minted under a row. `at(k)` is data and has no owner, so
the slot counts its subscriptions and goes with the last one (Q4). The table then
stays the size of what is watched.

**In the pipe model.** `at(k)` is a `Source`, not a pipe: it has state to read
(R29). So `messages.at(id).derive(render)` starts a pipe from it, and two
consumers of one `at(k)` need no seal.

**In a store.** A `HashMap` field of a `Store` is a keyed node with this same
slot table (`store.md` §2.7). There `at(k)` is a `Store<Option<V>>`, which can
project further into `V`'s fields when `V` derives `Storable`. `MapCell::at`
returns a `MapEntry<K, V>` handle with the same two traits. When the Store's S3
lands, the keyed node reuses the cell's body (Q5).

## 5. The operators

Operators are written once per shape against `MapOp`/`SetOp`, with the
derivative law of A112 §5. Each returns a move-only pipe (R29). Each takes a
closure result through `IntoFlow` (R31), so a closure that returns a reactive
value is followed per key (R9), and one that returns a plain value never
subscribes. Each per-key closure run gets its own owner (§6.4 of the base
paper).

| Operator | In → out | Extra state | Per op |
|---|---|---|---|
| `at(k)` | Map → `Source<Option<V>>` | a slot per watched key | O(1) for key `k`; nothing for other keys |
| `keys()` | Map → `SetPipe<K>` | none | O(1): a new key's `Put` → `Add`; an overwrite → nothing; `Delete` → `Remove` |
| `values()`, `entries()` | Map → `CollPipe<V>`, `CollPipe<(K, V)>` | the **rank index** (§6.2) | O(log n): a new key → `Splice(rank, [], [..])`, an overwrite → `SetAt(rank, ..)`, a delete → `Splice(rank, [..], [])` |
| `map_values(f)` | Map → `MapPipe<K, U>` | the output map, for `Put`'s "what was there" | one call of `f` per `Put` |
| `filter(p)` | Map → `MapPipe<K, V>` | a kept flag per key | one call of `p` per `Put`; a flip emits `Put` or `Delete` |
| `count()`, `sum_by(f)` | Map → `Source` | the accumulator | O(1): add what arrived, subtract what left |
| `min_by(f)`, `max_by(f)` | Map → `Source<Option<..>>` | an ordered multiset | O(log n) |
| `sort_by(cmp)` | Map or Coll → `CollPipe` | an order-statistic tree | O(log n); I10's door (c) (§6) |
| `contains(x)` | Set → `Source<bool>` | a slot per watched element | O(1) |
| `union`, `intersection`, `difference` | Set × Set → `SetPipe<T>` | a count per element (0–2) | O(1) |
| `index_by(key)` | Coll → `MapPipe<K, T>` | a count per key | O(1); a repeated key keeps the last, as `to_map` does |
| `group_by(key)` | Coll → `MapPipe<K, CollSource<T>>` | a `ListCell` per group | deferred (S5) |

`keys()` is kolt's `get_channels` (`store.vl:196`): a set pipe, sealed with
`.memo()` where it is shared, that changes only when a key arrives or leaves.
kolt writes the channel map only to create or delete a channel (a rename writes
the record's own `name` cell), so today's cost there is not extra wakes. It is
that each write hands every consumer a new whole key list to diff, where the
pipe hands it one `Add` or `Remove`.

The positional face is what `each_by(map.entries(), ..)` consumes. It is also
where order lives, which is §6's point.

## 6. Order (I10)

### 6.1 What is already true

Insertion order is the behaviour of both backends and the documented promise
(§1.4). The remaining work:

- **Pin** remove-then-re-insert in `native_differential.rs` beside the overwrite
  case (XS).
- **Fix find 1**: compact the native entries vector when dead slots outnumber
  live ones (S). Compaction preserves order, so nothing observable moves, and it
  bounds memory and walks by the live count.
- **Say it in I9's doc comments.** I9's text says the new names "say the contract
  (`Hashable` keys, no order)". The contract is **insertion order**, and the
  doc comments on `std::hash_map::HashMap` and `std::hash_set::HashSet` should
  say so. A reader coming from Rust will otherwise assume there is none. This is
  a note for the collections-44 lane, which is writing those files now.

### 6.2 Why order is a shape question, and where it lives

A `MapOp` names keys, not positions. `Put(k, ..)` means the same thing whatever
order the map keeps, so every operator in §5 except the positional face is
order-free. Only `values()`/`entries()`, and through them `each_by` and the
wire's `Delta::Insert(key, value, at)`, need a *position*:

- **Insertion order**: a new key goes at the end; a delete leaves a hole. Rank =
  the number of live slots before the key's slot, which a Fenwick tree over the
  slots answers in O(log n). The native runtime's entry vector is already this
  layout, so the rank index sits beside it. It is the same structure the base
  paper's `filter` uses for its output positions (§6.2 there).
- **Key order**: rank = the key's place under the comparator, from an
  order-statistic tree. An overwrite never moves a key.
- **Value order**: rank depends on the value, so an overwrite can become a
  `Move`. That is `sort_by`, an operator (§5), not a property of the map.

So the "rank index beside the hash index" that door (a) proposed is exactly the
positional face's index. It is needed only where something consumes positions.

### 6.3 The doors, weighed

- **(a) One type with a strategy parameter**, `HashMap<K, V, O = Insertion>`,
  with `O: Ordering<K, V>` supplying a rank.
  - Every signature that names a map would carry a third parameter, unless
    defaulted struct parameters work. They do not today: a struct accepts a
    default at its declaration and never applies it, so `Ordered<str, i32>` is a
    different type from the literal's `Ordered<str, i32, Insertion>`
    (`find_struct_default_param.vl`, find 2).
  - Every map would pay a rank index, including the ones nothing ever iterates.
  - One type would carry two key contracts, `Hashable` for lookup and a
    comparator for order.
  - `Ordering` is already taken by `std::compare::Ordering`.
- **(b) Separate types**: an insertion-ordered `HashMap`, a `SortedMap<K, V>`
  ordered by key, and a comparator-ordered form. The item worried that this
  "multiplies types". It stops at one extra pair if the comparator is a
  constructor *value*: `SortedMap::new()` for `K: Ord`, and
  `SortedMap::by(|a, b| ..)` for any key. A value needs no type parameter, and
  a sorted map needs no `Hashable`.
- **(c) No strategy in the collection**: `entries().sort_by(..)`, cached where
  hot. For a plain map that is a sort per read. For a reactive map it is the
  `sort_by` operator, maintained in O(log n) per op and sealed with `.memo()`.
  That is not "sorting on every read", which was I10's objection.

**Decision (recommended):**

1. Insertion order is the contract of `HashMap`/`HashSet` (§6.1).
2. Key order is `SortedMap<K, V>`/`SortedSet<T>`, built when a customer asks,
   with the comparator as a constructor value.
3. Any other order is door (c).
4. Door (a) is declined. It asks every map to pay for what one map in a hundred
   uses, and it needs a language item (find 2) to be tolerable.

The owner asked for "a per-collection order chosen at construction rather than
by sorting on every read". Point 2 gives key order at construction. Point 3
gives every other order without a sort per read on the reactive side.

**On the cell.** `MapCell`'s op log is order-free, so a sorted map's cell shares
every operator. Only its positional face ranks by the comparator instead of by
insertion. `MapCell::sorted_by(cmp)` can therefore be a constructor of the same
cell whose rank index is an order-statistic tree, rather than a
`SortedMapCell` (Q1).

## 7. The wire

Today a map is exposed by diffing (`rpc.vl` `expose_keyed_map`):

- each change, each subscribed connection runs `keyed_diff` over two snapshots;
- a `key_of` closure names each value's key, because `Delta` is keyed and the
  values alone do not say.

A `MapCell` needs neither. Its `MapOp` carries the key, and `expose_map_cell`
forwards ops:

| `MapOp` | `Delta<K, V>` |
|---|---|
| `Put(k, None, v)` | `Insert(k, v, rank)`: the end, under insertion order |
| `Put(k, Some(_), v)` | `Update(k, v)` |
| `Delete(k, _)` | `Remove(k)` |
| `Reset(m)` | `Reset(m.values())` |

The mirror is the existing `KeyedSource<K, V>`. `Patch` does not move, `Delta`
does not move, and the edge between `std::reactive` and `std::wire` stays in
`std::rpc`, as A112 §10 required. The macro that exposes a `[expose(keyed)]`
field (`rpc.vl`, the field walk that already recognizes `KeyedCell` and `Map`
fields) learns `MapCell` as a third keyed form. `SetCell` needs a keyed element
to cross the wire (`Delta<T, T>`) and waits for a customer.

## 8. Finds (bugs met while probing, for the integrator to file)

1. **The native `Map`/`Set` never compact removed entries.** `remove` takes the
   slot (`self.entries[slot].take()`) and leaves it in the vector. A native map
   that has seen 200,000 keys and holds one walks 200,000 slots per iteration:
   0.130–0.162 s for 2,000 key walks, against 0.000–0.001 s for a fresh map
   (release, user CPU). Memory stays at the high-water mark. Repro:
   `probes/maps/churn_native_{0_2000,200000_0,200000_2000}.vl`; JS twin
   `probes/maps/churn.vl`.
2. **A struct's defaulted type parameter is accepted and never applied.**
   `struct Ordered<K, V, O = Insertion>` compiles. A signature's
   `Ordered<str, i32>` is then a different type from the literal's
   `Ordered<str, i32, Insertion>`: "Expected Ordered<str, i32>, but got
   Ordered<str, i32, Insertion> instead". Traits honour theirs
   (`PartialEq<B = Self>`). Either refuse the default on a struct, or fill it.
   Repro: `probes/maps/find_struct_default_param.vl`.
3. **(Noted, not a defect) `Map`/`Set` have no `PartialEq`.** This is Q8's
   recommendation, not a bug. It is listed so the integrator can route it with
   I9.

## 9. Open questions, each with a recommendation

- **Q1. The cell names.** `MapCell`/`SetCell` (shape names) or
  `HashMapCell`/`HashSetCell` (backing names). **Rec: `MapCell`/`SetCell`**, with
  key order as a constructor (`MapCell::sorted_by(cmp)`) if S4 is built, not as
  another type.
- **Q2. `KeyedCell`.** Keep it as it is, or re-found it on `MapCell`. **Rec:
  re-found it** (S3). The surface and the wire bytes stay the same, and removal
  stops being O(n).
- **Q3. `SetCell`.** An alias of `MapCell<T, void>`, or its own type. **Rec: its
  own type over a shared body** (§3.3).
- **Q4. Per-key slot lifetime.** Owner-deferred, as `Selector` does, or counted
  per subscription. **Rec: counted**, because `at(k)` is data with no owner (§4).
- **Q5. `at(k)`'s type.** A `MapEntry<K, V>` now, which becomes the Store's
  keyed node when `store.md` S3 lands. **Rec: yes**, and the two slices share the
  slot table so that there is one per-key implementation.
- **Q6. What `Reset` wakes.** **Rec: every live key slot** (a cell never
  compares, R7). `reconcile_to(map)` is the door that wakes only changed keys.
- **Q7. The ordering strategy (I10).** **Rec: §6.3's decision.** Insertion order
  is the contract; `SortedMap`/`SortedSet` with a comparator value when asked;
  any other order is door (c). Door (a) is declined.
- **Q8 (RULED 2026-09-29 as recommended; built with I9 in Order 44's collections-44). `PartialEq` on `HashMap`/`HashSet`.** They have none today
  (`store/map_eq.vl`, `store/set_eq.vl`), so `reconcile_to` on a map of maps
  cannot compare, and a struct holding a map cannot derive `PartialEq`. The
  native runtime already carries an order-*sensitive* equality that nothing can
  reach (`lib.rs`, `impl PartialEq for Map`). **Rec: add both to I9's types,
  order-insensitive**: two maps are equal when they hold the same keys with
  equal values. Order is presentation, and the runtime impl follows.
- **Q9. `clear()`: one `Reset` or a `Delete` per key.** **Rec: `Reset`.** It is
  one op, and per-key owners are released by the consumer's `Reset` path, as for
  `ListCell::clear`, which is a splice of everything.

## 10. Slices

| Slice | Content | Size | Needs |
|---|---|---|---|
| S0 | Pin remove-then-re-insert in `native_differential.rs`; compact the native map's tombstones (find 1); insertion order written into `HashMap`/`HashSet`'s doc comments | S | I9's files (collections-44) |
| S1 | `MapCell`/`SetCell` with the writes and reads of §3; `MapSource`/`MapSignal`/`SetSource`/`SetSignal`; the `DeltaSource` impls over `DeltaLog<MapOp>`/`DeltaLog<SetOp>`; `at(k)`/`contains(x)` with counted slots; `get_or_insert` (I8's maps half on the cell); `PartialEq` for `HashMap`/`HashSet` (Q8) | M | I9; A142 S1 (the faces are `Source`s, and `at(k).derive(..)` is a pipe) |
| S2 | The operators of §5 except `group_by`: `keys`, `values`/`entries` with the Fenwick rank, `map_values`, `filter`, `count`/`sum_by`, `min_by`/`max_by`, the set algebra, `index_by`; `MapPipe`/`SetPipe`; per-key owners; `IntoFlow` following | M | S1; A142 S4 (`CollPipe`, `IntoFlow`, per-element owners) |
| S3 | `KeyedCell` re-founded on `MapCell` (A54's pins byte-identical); `expose_map_cell` and the `[expose(keyed)]` field walk learning `MapCell` | S–M | S1, S2 (the rank) |
| S4 | `SortedMap`/`SortedSet` (comparator value), and `MapCell::sorted_by`: on a customer's ask | M | S2 |
| S5 | `group_by` | M | S2 |

Nothing here is breaking. It is new surface, except S3, whose pins must hold
byte for byte. The build queues for Order 45 after I9 lands.

