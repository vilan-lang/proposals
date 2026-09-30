# native-44 — FINAL report (2026-09-30; saved by the integrator — the lane's tool environment refused the report file twice). Branch rebased onto d3560fad; four new commits.

| item | verdict | sha | pins (native_differential) |
|---|---|---|---|
| F56 | LANDED (merged @453bd3cc) | 834de493 | three (see the partial report) |
| F53 | LANDED (merged) | 6465fc7b | `a_closure_body_erased_to_an_object_is_identical_on_both_backends` |
| parity 1 (a field read off a `Shared` read; a closure returning a captured value) | LANDED (merged) | 78097e9f | `a_field_read_off_a_shared_read_is_identical_on_both_backends` |
| F58 | LANDED | 469adbca | `a_blanket_reached_through_a_list_source_bound_builds_the_same_on_both_backends` |
| F59 | LANDED | 092014b4 | `a_field_read_on_an_inferred_return_is_identical_on_both_backends` |
| parity 2 (`Option<Shared<List<closure>>>`) | LANDED | 59f689ed | `an_option_of_a_cell_of_closures_builds_the_same_on_both_backends` |
| B470 native half | LANDED | 9d565f4e | `a_resource_trait_object_is_moved_into_its_consuming_members_natively` |
| censuses | DONE inside 469adbca | — | the native copy + leak census tests |

Every new pin failed against d3560fad's emitter first.

- **F58** (premise confirmed; 20-line std-free repro): the `Flow` blanket over every `Source` takes its `T` from the receiver's own `Source` impl — for `ListCell<E>` that is `List<E>` written in the providing impl's own parameter `E`, which the native substitution never bound. Fix: `impl_select::bind_provider_binders` (additive, native-only; solver's file) binds those parameters from the receiver; two receivers binding one differently → left unbound, refused by name. Workarounds removed: `std::delta::map_each` attaches with `on_change` again; `mint_subscriber` private again; `delta-law.vl` drops its `observe` helper (its `attach_observer` override stays — that is the leak fix). Both programs print identically natively; leak census `live=0`. Goldens `delta-law.mjs`, `list-cell.mjs` moved (runtime identical); JS copy census 543 → 547 (delta-law 25→26, list-cell 52→55); native copy census moved only in eliminated copies.
- **F59** (premise confirmed): `declared_return_type` reads the return type the callee's emitted signature uses (written or inferred); B460's checked returns take the same path.
- **Parity 2**: a struct holding `Option<Shared<List<closure>>>` was refused by name (the shape reactive-44 rebuilt S2's `OwnerCell` to avoid). vilan-rt gains `ReferenceEq` for `Shared`/`Weak` (identity, like JS `===`); the emitter's reference-equality check accepts a cell as a leaf. `OwnerCell` left as built (going back to the `Option` is reactive's call).
- **B470 native half**: the erasure point already built the `Dyn` pair without copying; the copy was at the OBJECT TABLE's slot (copying the pipe out from behind a borrow at every `start`/`on_change`/`effect`). Fix: a slot whose member takes `own self` now takes `self: Rc<Self>` and calls `vilan_rt::unshare` (moves when unique — always, for a `[resource]` object; copies when shared); at the call site a receiver at its last use hands its pointer over with `Dyn::into_object`, any other passes a counted copy. `dyn Source<T>` stays data and keeps its copy. Pins: the mixed-arm selector, a `dyn Flow` passed to an `own` parameter and consumed once — same bytes on both backends, no copy in the emitted Rust.
- **Censuses**: native copy census regenerated (only eliminated copies moved); native leak census unmoved — all 34 rows `live=0`, every pipe program included; list-cell stays 0.
- **Parity sweep**: the whole corpus + all 27 reactive test programs natively at the tip: every reactive program identical except four refused for pre-existing reasons (crypto, signal-update, spread-parameters, time). `reactive.vl` shows `live=9` natively on d3560fad too — its `.memo()` never under an owner, by design; not in the census set.

## Finds (not fixed)
1. a52 miscompile (JS): natively the same wrong dispatch surfaces as rustc E0308 (B474).
2. `flatten_total_join_bare.vl`: a pipe never consumed (`outer.flatten();`) is refused natively 'unbound generic type parameter (#3823)' while JS runs it → F60.
3. `spawn_in_injected_nursery_closure.vl` DIVERGES: JS prints 'unhandled task error … AbortError' twice on cancelling a detached nursery; native prints nothing (the JS side suspected — a cancellation should not report as unhandled) → noted on J7.
4. Carried: crypto.vl E0382 at base (F57); `a.write().n = a.write().n + 1` refused by name natively (needs a temporary); `check_scope_differential::std_sources_are_recorded_and_the_entry_is_not` possibly flaky under load.

## Ledger: none. ## Gates at 9d565f4e
native_differential default 90/90 (incl. both census tests); `VILAN_NATIVE_DIFFERENTIAL=1` 127/97/30/0; async differential 7/4/3/0; corpus 12; split 13; examples 6; copy_elision_census 2; shared_census 2; check_scope_differential 15; inference 4877 (+9 ignored); vilan-rt 80; clippy `-D warnings` + fmt clean. Each intermediate commit `cargo check`s; the final tree is the one the gates ran on.
