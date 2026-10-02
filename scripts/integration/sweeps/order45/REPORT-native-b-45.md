# native-b-45 REPORT (condensed by the integrator; Opus) — tip ed357d74 on e071b662; 6/6 LANDED (all in crates/vilan-rust/src/lib.rs)

| item | sha | note |
|---|---|---|
| F72 | 9ec75820 | `is_grounded` treated `Type::Trait` as closed: a BOUNDED parameter's constraint resolves to its bound, so `Op<T>` read as closed and the enum was minted over "a trait object" |
| F76 | 29d28661 | a bare variant now uses the constructor's rule (the recorded type, else the POSITION); a payload is a position of its own (F66) |
| F75 | ab088d0f | F58's `bind_provider_binders` applied where a trait DEFAULT is specialized (`effect`, `effect_on_change`) |
| F73 | cbe83113 | CORRECTED: the repro already built at the base; fixed beside it — a struct literal's field expectation keeps the instance's bindings while the value renders |
| F71 | f6cee081 | `default_instance` COMPOSES onto the caller's substitution |
| F74 | 4546735b | CORRECTED: not the wrapper — `keyed_mirror_of`: an unconstrained closure parameter takes its type from the closure type it renders into; a `Shared` around an empty literal gets its binding's type written |
| ed357d74 | | CHANGELOG rebuilt, copy census regenerated |

Shared cause: the native emitter cannot mint a substituted TypeId (→ F82).
Gates on the rebased tip: nextest 9260/9260 (32 skipped); native_differential 125/125 both modes; corpus 128/100/28/0 (unchanged); check_scope_differential 15/15; fmt, clippy clean. Copy census: scalar payload rows only. Leak census 0 live.
PINS TO FLIP (verified on a scratch tree of tip + maps-45 + store-45): maps-45's `a138_map_and_set_cells_build_the_same_on_both_backends_or_are_refused_by_name` — `set_walk.vl` becomes Identical; `keys()` and `MapEntry::set(None)` build natively (kolt's `get_channels` can use `channels.keys()`). store-45's `a142_s7_observing_a_store_some_is_refused_by_name_natively` will PANIC — move the observer into `native/store_struct.vl` and retire the pin. reactive-45's two "JS-only" notes on A146's mirror half are stale.
Finds FILED: B513, F82.
