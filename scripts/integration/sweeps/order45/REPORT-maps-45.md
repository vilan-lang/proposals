# maps-45 REPORT (condensed by the integrator; Opus, 552k tokens) — tip 32d8b8ff on ba2eebd9 (rebase onto reactive-45's merge OWED)

Commits: S0 a5b92e2f (pin), S1 acc5e232 + 32d8b8ff (`MapCell`/`SetCell`, faces, per-key handles, counted slots; `KeySlot` exported for the reach rule), S2 ace570b7 (map operators as pipes), S3-part a4e34b8f (an `[rpc]` method may return `MapEntry`/`MemoEntry`; touches two match arms in analyzer.rs, rpc.vl, macros.rs).

Surface: `KeySlots` (watch/observe/wake/wake_all/watched/identity); `MapCell<K: Hashable, V>` — `new`/`of(own)`/`with_limit`, `insert`, `remove`, `update(k, |&mut V|)`, `get_or_insert`, `clear` (one Reset; nothing on empty), `set`, `notify`, `get(k)`, `contains_key`, `len`, `is_empty`, `peek`, `at(k): MapEntry<K,V>`, `edit(|&mut TrackedMap|)`, `reconcile_to(own target)`, `logged`, `watched`; implements Source/Signal<HashMap<K,V>>, DeltaSource<_, MapOp>, MapSource. `MapEntry<K,V>`: Source + Signal<Option<V>>, `key()`, stable `identity()`. `SetCell<T>`: `insert`/`remove` (bool), `clear`, `contains(x): SetEntry<T>` (Source<bool>), `reconcile_to`. Operators (blanket over `MapFlow`): `keys()`, `values()`/`entries()` (Fenwick rank), `map_values`, `filter(|K, V| R: IntoFlow<bool>)`, `count()`, `sum_by`; `MapPipe`/`SetPipe` seal to `MapMemo`/`SetMemo` (`at(k): MemoEntry`).

Deviations: `get(k)`/`at(k)` are INHERENT (no overloading; `MapSource`/`SetSource` are markers) — so the whole map is read through a `Source` bound, an annotated `Source::get(cell)`, or `peek` (B499); `sum_by`'s measure is a plain number (B484 workaround); `filter` takes `(key, value)`; a filter pipe's order is arrival order; a write fires two notifications (the key's slot, then the map). Not built: `min_by`/`max_by`, set algebra, `index_by`, the `KeyedCell` re-founding.

Measurement (1,000 watched keys, 1,000 single-key writes, JS, load ~22): coarse 1,000,000 projections / 77,189 ms; keyed `at(key)` 1,000 observer calls / 3 ms.

Gates on ba2eebd9: nextest 9183/9185 → the 2 (`check_scope_differential`, `KeySlot` unexported) fixed in 32d8b8ff, targeted re-run 59/59; whole-set native 106/106; fmt, clippy, `vilan fmt --check` std clean; docs gate 265; shared census 180 → 194. Native: `MapCell`, `MapEntry`, the operators but `keys()` build; `SetCell` + `keys()` refused by name (F72); `peek` not emitted (as `ListCell::peek`).

Kolt patch: `sweeps/order45/maps-45/kolt-maps-45.patch` (applies to kolt's current `src/store.vl`; `channels`/`messages` as `MapCell`s, `get_message` returns `messages.at(id)` — same client type, no hash move; `get_channel` a view over `channels.at(id)`; `get_channels` stays coarse until F72). Checked on a scratch copy: server checks clean and builds natively.

Finds: (1) sub-trait bound → inherent method — COVERED by B473 on next (integrator verified: NaN on ba2eebd9, 7 on next); FILED F72, F73, B498, B499. For store-45: reuse `KeySlots`.
