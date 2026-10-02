# reactive-45 PHASE 1 REPORT (condensed by the integrator; Opus) — tip 8e49e5c6 on ba2eebd9; phase 2 after solver-b-45's merge

| item | sha | note |
|---|---|---|
| J7 + M92 | 30c73c4d | COMPILER CHANGE in `context.rs` (~30 lines): a closure literal born under an `ambient_nursery` clause engages spawn registration (the gate was off unless the program called `nursery`/`enter`). M92 premise CORRECTED (not std-only): `Owner::renew` carries an unspawned nursery into the next epoch; new `Nursery::has_spawned()` ([internal]) in transformer.rs (`__nursery_has_spawned`), vilan-rt, vilan-rust, the interpreter. A late spawn through a carried run's closure is cancelled one run late, never leaked. |
| OwnerCell/TrackRuns field writes (F62) | 031a0eeb | five TrackRuns transition functions removed; stale comments corrected |
| M93 | c2a25bcc | the Tracker's lists are one cell made at the first `track()`; `trackers_allocated()` |
| A146 | afbb12e7 | `identity()` for ListCell, KeyedCell, RemoteSource, KeyedSource; the mirror half pinned on JS only (F74) |
| A135 tail | 9b0bca32 | row 576 re-keyed: names `.{seal}()` and `.{seal}_global()` |
| R-k | ed7333d4 | `.transient()` in the module-binding refusal; `transient_global()` on both arms |
| A144 (R-f) | f10db29c | BREAKING; premise CORRECTED on sizing: the macro writes a `$N$` template + a typed closure to `rpc::resolved_contract_hash`; new post-analysis pass `contract_hash.rs` fills each slot with its resolved type and stores the djb2 in `const_results`. NO existing hash pin moved (the canonical rendering equals a plain spelling); only aliased / renamed-import / module-path spellings move onto their plain twin. |
| fmt, native copy census | 39b6bad5, 8e49e5c6 | |

Gates on ba2eebd9: nextest 9181/9182 → the one (native copy census) regenerated in 8e49e5c6; native_differential 106/106 both modes; fmt, clippy, `vilan fmt --check` std clean.
Goldens: corpus reactive, reactive-flatten, reactive-on-change, reactive-owner, reactive-selector, list-cell, signal-update + 4 split. Shared census 180 → 178. JS copy census 578 → 589. Native leak census: 0 live everywhere. Ledger: no NEW rows; 576 re-keyed; 575 also fires for `.transient()`.
Kolt: no edit needed; its hash does not move. Release note: std and compiler must match (a 0.42.0 compiler over this std panics at `resolved_contract_hash`).
Finds FILED: B500, B501, F74.
