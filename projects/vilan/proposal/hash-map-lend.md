# A `HashMap` read or written in place: `peek`, `modify`, `update` — and the store's keyed step (B689 + M182)

- status: DESIGNED 2026-10-31 (integrator, at the owner's "Fix B689"); building in lane b689
- items: B689 (a field read through a store's `some()` copies the whole value), M182 (a map's value can't be changed in place)
- area: Standard library (`std::hash_map`, `std::js::native_map`, `std::reactive::store`), the three backends' map intrinsics, `vilan_rt::Map`

## 1. The fault, located

B689 says the copy is in the store's variant reader. It is not: every store
step lends in place except ONE — the keyed step. `Store<HashMap<K, V>>::at(key)`
(`store.vl:758`, and its `StoreSome` twin at `:787`) reads

```
|held: &HashMap<K, V>, f: |&Option<V>| void| {
	let value = held.get(key);   // a COPY of the whole value
	f(&value);
}
```

because `HashMap::get` is "a copy of the value stored under `key`" and the map
has no in-place read. On JS that is two deep clones per read: `__map_get` clones
the stored `(K, V)` pair, and `Some(entry.1)` clones the value again (the repro's
`get` at `main.mjs:130-134`). Natively `Map::get(&k).cloned()` clones the pair and
`entry.1` clones again. Everything below the key step — `some()`,
the derive's `title()` projection, `lent_option` — hands the place through and
copies only the leaf, exactly as documented.

The write side is the same shape: `at`'s write closure copies the value out,
lets the consumer write the copy, and re-inserts it (a third copy in `insert`).

M182 is the same missing primitive seen from user code: grouping into a map's
list is take-a-copy, push, put-back, O(n²).

## 2. Why the fix is not "lend the entry"

A `Store<Option<V>>`'s lend hands its consumer an `&Option<V>` — a reference to
an `Option<V>` that EXISTS. A map stores `V`s; its "maybe" is a table miss. On
JS a `[0, value]` wrapper that aliases the stored value is a free view. Natively a
`&Option<V>` cannot be made from an `&V` in safe Rust, and `vilan_rt` is
`#![forbid(unsafe_code)]` — the bitwise `ManuallyDrop<Option<V>>` view is out
by policy. The `Option<&T>` transient the language already has (C5.2;
`Weak::get`, `Arena::get`) is the other shape and does not convert.

So the `Option<V>` must exist in memory. `vilan_rt::Map` already keeps one per
slot: `entries: Vec<Option<(K, V)>>`, the tombstone a removal leaves. Moving the
tombstone onto the VALUE — `Vec<(K, Option<V>)>` — makes every present entry's
value a real `Option<V>` place, lent for free, and a removal a `take()` of it.
That is a runtime-internal change; `iter`, `remove`, `compact` adjust.

The remaining obstacle is `HashMap`'s own layout: it stores `(K, V)` pairs in a
`NativeMap<(K, V)>`, so the runtime's `Option` wraps the PAIR and `.1` is a
place of type `V` again. Three layouts were weighed:

- **`NativeMap<(K, Option<V>)>`** — an always-`Some` invariant inside the map
  with `expect`s at six sites, and `entries()` copying twice. Rejected: an
  invariant a type could carry is a smell.
- **A two-parameter `NativeMap<K, V>` that stores the original key natively** —
  a second runtime map type, `HashSet` on a different shape, the I1-era
  two-parameter bound gap to re-check, the const-map lowering to rework.
  Rejected on churn.
- **Two tables, `keys: NativeMap<K>` and `values: NativeMap<V>`, both keyed by
  the canonical `Hash`** — no invariant, no new runtime type, every method of
  `HashMap` simpler than today (`eq` walks hashes, no re-hash of `K`). Costs a
  second index per map and two inserts per write. CHOSEN.

Every mutation of a `HashMap` touches both tables inside one method
(`insert`, `remove`, `modify`'s insert and remove), which is what keeps them
in step; the pair they replaced existed to keep `K` and `V` from desyncing when
a key was mutated after insertion (I1), and two tables written together keep
that property.

## 3. The surface

### 3.1 `NativeMap` (internal; `std::js::native_map`)

```
external fun lend<U>(self, key: Hash, read: |&Option<V>| U): U;
external fun lend_mut<U>(&mut self, key: Hash, write: |&mut Option<V>| U): U;
```

`lend` calls `read` once with the slot under `key` — `&Some(value)` in place
while the key is present, `&None` otherwise — and answers what `read` answers.
`lend_mut` does the same with a writable slot, and when `write` returns the
table reflects the slot: a slot left `None` is removed (its key gone from
`contains_key`, `len`, iteration), a slot made `Some` under an absent key is
inserted AT THE END (a new key goes last, as `insert` does), a present key keeps
its place whatever was written. The value is never cloned by either.

Two new intrinsics, `MapLend` / `MapLendMut`, bound beside `MapGet` in the
analyzer's `NativeMap` table (`analyzer.rs:90940`); `captures.rs:391`'s
classification gains neither (both run user code).

Per backend:

- **JS** (`transformer.rs`, helpers beside `__map_get` at `:2662`):
  `__map_lend(map, key, read)` is `read(map.has(key) ? [ 0, map.get(key) ] : [ 1 ])`;
  `__map_lend_mut(map, key, write)` builds the same view, calls `write`, then
  `map.set(key, view[1])` when `view[0] === 0` (a present key keeps its position,
  an absent one appends) or `map.delete(key)`. No `__clone` in either — the
  `&`/`&mut` discipline is what makes the alias safe, as `descend`'s closures
  already rely on.
- **native** (`vilan-rust/src/lib.rs:16196` and `vilan_rt::Map`, `lib.rs:1442`):
  `Map::lend(&self, key: &K, read: impl FnOnce(&Option<V>) -> U) -> U` reads
  `&self.entries[slot].1` or `&None`; `Map::lend_mut(&mut self, key: K, write) -> U`
  lends `&mut self.entries[slot].1` and afterwards removes an emptied slot
  (index, `live`, the compaction rule as `remove`) — or, for an absent key, lends a
  fresh `None` and inserts when it came back `Some`. Rendering: the closure is
  the `Rc<dyn Fn>` a vilan closure already is; `(*read)(view)` inside the
  runtime's `impl FnOnce` call, or the runtime takes `&dyn Fn` — the lane picks
  what the existing closure-taking externals (`Context::run`, `listen`) do.
- **interpreter** (`interpreter.rs:2547`): the map's entries are `(key_value,
  value)` with `Rc`-shared aggregates, so `__map_lend` hands `option_some(value.clone())`
  (an `Rc` alias — the in-place view, as JS) and `__map_lend_mut` writes the
  slot back from the view after `call_value` returns, removing on `None`.

### 3.2 `HashMap` (`std::hash_map`)

```
struct HashMap<K: Hashable, V> {
	keys: NativeMap<K>,      // the original key, so `keys()` answers real `K`s
	values: NativeMap<V>,
}

impl HashMap<type K: Hashable, type V> {
	/// Read the slot under `key` in place: `&Some(value)` while the key is held,
	/// `&None` otherwise. Copies nothing; what `read` copies out is its own.
	fun peek<U>(self, key: K, read: |&Option<V>| U): U

	/// Write the slot under `key` in place. Leave it `None` and the key is gone;
	/// make it `Some` under an absent key and the key is inserted (last).
	fun modify<U>(&mut self, key: K, write: |&mut Option<V>| U): U

	/// Change the value under `key` where it is — the one `missing` makes,
	/// inserted first, when there is none (M182's grouping idiom:
	/// `groups.update(key, [], |list| list.push(row))`, O(1) per push).
	fun update(&mut self, key: K, lazy missing: V, change: |&mut V| void)
}
```

`get` becomes `self.peek(key, |slot| *slot)` — one copy of the value instead of
two, for every map read in every program. `get_or_insert` goes through `modify`
(one copy, of the answer). `keys`, `values`, `entries`, `contains_value`, `eq`,
`Debug`, `to_map`, `Default` read the two tables; `entries()` zips two snapshots
of one insertion order.

`missing` is `lazy` rather than M182's `|| V` because that is the ratified
spelling for "evaluated only on the miss" (`unwrap_or(lazy fallback)`,
`expect(lazy message)`; proposal/lazy.md). `change` runs on the freshly made
value too, as M182's `entry(key).or_insert_with(missing)` then a mutation does.

F123's curated lookups (`vilan-rust/src/lib.rs:13529`: `HashMap::get`,
`contains_key`, `HashSet::contains` run no user code) stay as they are;
`peek`/`modify`/`update` run user code by construction and are not added.

### 3.3 The store (`std::reactive::store`)

`Store<HashMap<K, V>>::at` and the `StoreSome` twin become

```
self.descend(StoreStep::Key(key.hash()),
	|held: &HashMap<K, V>, f: |&Option<V>| void| held.peek(key, f),
	|held: &mut HashMap<K, V>, f: |&mut Option<V>| void| held.modify(key, f))
```

— the key step lends like every other step, and a write through `at(key)`
lands in place (no copy out, no re-insert). `value_at` and the `Storable` map
diff (`store.vl:151-255`) read `values` instead of `table`; the diff's own
copies are a separate matter (left as they are, noted below).

## 4. Semantics that are new, and pinned

1. `peek` on an absent key reads `&None`; on a present key `&Some(v)` and `v`
   is the stored value (a write through `modify` is seen by the next `peek`).
2. `modify` leaving `None` removes: `contains_key` false, `len` down by one,
   gone from `keys()`/`values()`/`entries()`; on both backends.
3. `modify` making `Some` under an absent key inserts LAST; under a present key
   the position is kept (insertion order is the contract, reactive-maps-sets.md Q7).
4. `update` on a miss inserts `missing` then applies `change`; on a hit only
   `change`; `missing` is not evaluated on a hit.
5. A store read through `at(key).some().field().get()` copies only the leaf:
   pinned as CODEGEN SHAPE — the B689 repro compiled by the inference harness
   has no `__clone` call in the `at` step's closures nor in `__map_lend` — plus
   the B689 repro's three timings printed by the native probe and a node run in
   the lane's report (a timing is a report, not a gate: `benchmarking under load`).
6. `get` through `peek` answers the same values as before (the corpus goldens
   move where the emitted `get` changed; a deliberate regeneration after a diff
   read, per CLAUDE.md).
7. `vilan_rt::Map` unit tests: tombstone-on-value keeps `iter` order, `remove`
   then `compact` after the M91 threshold, `lend_mut` insert-at-end / remove /
   keep-position, `len` and `live`.
8. The native differential (`crates/vilan-cli/tests/native/`) runs a program
   exercising 1-4 and the store's `at` read/write/remove on both backends.

## 5. Docs

- `docs/std/collections.md` §`HashMap<K, V>`: the three methods in the
  signature block, a paragraph "Reading and writing in place" with the grouping
  idiom, and `get`'s line saying it is one copy.
- `docs/std/store.md` §Collections: `at(key)` lends the slot in place on both
  backends; a write through it lands in place.
- CHANGELOG `## Unreleased`: a `family: fix` entry (B689) and a
  `family: feature` entry (M182); the layout change is internal and named in
  the fix entry.

## 6. Left out, by name

- The `Storable` diff for a map (`store.vl:190-260`) still copies each
  compared value (`value_at`); a lend-based diff is a follow-up (file as M).
- `HashMapCell` (`reactive/hash_map_cell.vl`) reads through `HashMap::get`;
  its `at(key)` handle could lend too (follow-up).
- `HashSet` keeps `NativeMap<T>` as it is.
- A `List::group_by` (M182's "possibly also") is not built.

## 7. For the owner

- Q1 The names `peek` / `modify` / `update` — `peek` follows `ListCell::peek`
  and `HashMapCell::peek` (the in-place read), `update` is M182's own word.
  Rename at review if `modify` beside `update` reads wrong; a rename is a
  one-line codemod.
- Q2 `lazy missing: V` over `|| V`: the lane builds `lazy`; say if `|| V` is
  wanted.
- Q3 Two tables per map (a second index) over the always-`Some` wrapper — the
  trade in §2.
