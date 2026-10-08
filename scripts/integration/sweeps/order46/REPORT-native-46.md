native-46: tip **f8b2a785** on branch `native-46` (16 commits off origin/next @fe092e8d, not rebased). Worktree: `/home/reed/code/vilan-lang/vilan/.claude/worktrees/native-46`. Everything is fixed or pinned and every gate is green. One choice needs your ruling (F68, at the end).

The tool environment refused the REPORT file. The full text is below for the integrator to save as `sweeps/order46/REPORT-native-46.md`. The new finds were written to `proposals/scripts/integration/sweeps/order46/newitems46-native.json` (6 items, placeholder ids). The F83 sha is in the worktree's `LANE-STATUS.md`.

## One line per item
- **F83** FIXED a2ddae1a (+3f0916af). The filed premise was wrong: it is not the turn drain. Every `cell.write() op= v` aborted natively, because the value's `borrow_mut` was still alive when `set` ran. The value is now computed first.
- **F66** FIXED 7e804c48. I built the program that breaks (rustc E0308 four times on 0.43.0). A variant built inside a generic instance now takes its type arguments from the position, then the payload, then the recorded type.
- **New find, fixed** 6620ad0f. A closure's expression body was emitted at the closure type's expectation, which refused `|k: i32| Maybe::Just(k + 1)`.
- **F70** FIXED 29769178. It is a silent miscompile: `((1, 2), 3).0.1` printed 3 natively where node prints 2. `tuple-access.vl` now builds natively.
- **F82** FIXED d3c240fe. I built the minted-type overlay the item recommended. F73's guard is gone and its tolerant pin is now strict.
- **F67** FIXED d3ac6cac. A closure literal's cast now writes its return type.
- **F69 + F77** FIXED 9bc6a8ec. One fix covers both; neither builds without both halves.
- **F48** NOT REPRODUCED at base. Pinned in ea8c100d.
- **F51** NOT REPRODUCED at base. Pinned in d44815fe. `KeyedSource::or` builds natively.
- **F78** NOT REPRODUCED at base. Pinned in f0b2ae49.
- **F68 + B503** FIXED 420b184a. One printer rule (node's `console.log`) on both backends. No JS golden moved.
- **E243** FIXED e25a0553. `vilan run`'s `Bundled` lines now go to stderr.
- **New find, fixed** f8b2a785. Natively a tuple inside a tuple printed as a nested array; it now prints flat, as on JS.

## Needs your ruling
- **F68's rule.** The item asked whether JS output should change. I kept JS output as it is and ported node's layout to the native backend, so no golden moved. The other option, one line on both backends, would change JS stdout for every long list.

## Other notes
- **F78:** std can now make `Flow::on_change`/`sub` defaults natively (tested on a std copy, identical on both backends). That is reactive-46's call. Written as `observe_flow(self, ..)`, it runs into B510's JS internal error.

---

# REPORT-native-46

Tip f8b2a785 on base fe092e8d. All numbers below are from the tip unless a row says otherwise.

## Items

| item | verdict | sha | note |
|---|---|---|---|
| F83 | FIXED | a2ddae1a (+3f0916af) | **Premise corrected.** The drain was not the cause: every `cell.write() op= v` aborted. The set path emitted `(cell).set(*(cell).borrow_mut() + 1)`, and the value's `borrow_mut` temporary lives to the end of the statement, so `set` met it. The value is now computed in a `let` before the set, for the write view, a captured `mut` and a module-level `mut`. The corpus always spells this `x.write() = x.read() + 1`, which is why nothing caught it. 3f0916af declares the new corpus program in `corpus_harness`; the infer, release and interpreter differentials caught the missing row. |
| F66 | FIXED | 7e804c48 | Inside `Maybe<T>::map<U>`, `Maybe::Just(f(x))` recorded the receiver's `Maybe<T>`, so the `(str, i32)` instance built `Maybe<(str, i32)>` (rustc E0308 x4 on 0.43.0). `variant_arguments` now reads the position, then the payload (both under the instance), then the recorded type. The recorded type still comes first when it names no generic parameter, so an analyzer-settled `dyn` argument wins. `Option`/`Result` were only latent, because their paths name no instance. |
| new find | FIXED | 6620ad0f | A closure's expression body was handed the closure type as its expectation instead of the return type, so `\|k: i32\| Maybe::Just(k + 1)` was refused. Filed as F?1 (fixed); the remainder is F?2. |
| F70 | FIXED (miscompile) | 29769178 | `let t = ((1, 2), 3); print(t.0.1)` printed **3** natively and 2 on node. That is a silent wrong value when the neighbour has the same type, and rustc E0308 otherwise. The emitter wrote the JS backend's flat offset as a Rust tuple index; it now uses the recorded index chain (`tuple_index_paths`) at reads, places and Shared-view reads. |
| F82 | FIXED | d3c240fe | New `minted_types` overlay plus `type_entry` (all 21 direct `type_id_to_type_map` reads now go through it) and `substituted()`. A swapped literal's field types are rebuilt with the literal's own arguments. F73's guard is retired and its tolerant `SWAPPED_LITERAL_PROBE` pin is now strict. |
| F67 | FIXED | d3ac6cac | The `Rc<dyn Fn>` cast now writes the closure's return type. It comes from the same helper the body uses (`closure_return_position`), else the literal's recorded type. Not written for async or floating closures, or bodies that return a view. |
| F69 | FIXED | 9bc6a8ec | Shared fix with F77, two rules. First: at a closure call whose type records no views, a written `&`/`&mut` argument is passed as written (B464's rule). Second: an unannotated closure parameter takes the position's written closure type when that type records views. The fixture is the B467 inference pin built natively. |
| F77 | FIXED | 9bc6a8ec | Same fix as F69. F77's JS half is B516 (solver). |
| F48 | NOT REPRODUCED, pinned | ea8c100d | Already identical at base; F44's counted closure literal closed it. No CHANGELOG entry, because no behaviour moves. |
| F51 | NOT REPRODUCED, pinned | d44815fe | Already identical at base (F63/F64 closed it). The `KEYED_MIRROR_IS_A_SOURCE` program from reactive_channels is identical at base and tip. The pin fails at base only because of F67's `\|\| row.name`. No CHANGELOG entry. |
| F78 | NOT REPRODUCED, pinned | f0b2ae49 | Already identical at base. I also built delta-law, list-cell and the reactive corpus against a std copy with `on_change`/`sub` written as `Flow` defaults and eight pipe impls' copies removed: identical on both backends. The miniature pin calls `self.start()` in the default, because passing `self` to a generic over `Flow` hits a JS internal error (B510's shape). No CHANGELOG entry. |
| F68 | FIXED | 420b184a | New `crates/vilan-rt/src/inspect.rs` ports node v24's `util.inspect` rules: grouped columns (numbers padded at the start), the 80-column break, the depth-2 cut to `[Array]`, `... n more items`, splitting long nested strings, and node's string quoting. Every native rendering goes through it; `js_tuple` is replaced by `js_items`, and the emitted struct/enum impls are updated. **JS output unchanged.** |
| B503 | FIXED | 420b184a | At the `any` boundary the JS backend now maps a list (or fixed array) of trait objects, at any depth of lists, to their values. The native `Js::js_hosted` renders the same split. A trait object inside an `Option` or a struct field still prints as its `[ value, {} ]` pair on both backends. |
| E243 | FIXED | e25a0553 | `write_bundled` takes a `BuildReport` (stdout or stderr). The run paths (single run, both watch rounds) report on stderr; `vilan build` and the workspace build keep stdout. `estate.vl` moved from the outside list to the required list. Docs updated in `appendix/cli.md`. |
| new find | FIXED | f8b2a785 | A tuple nested in a tuple printed nested natively (`[ 1, [ 2, 'x' ] ]` against node's `[ 1, 2, 'x' ]`, since JS stores tuples flat). New `Js::js_tuple_slots` flattens them. Filed as F?6 (fixed). |

Fixup commits: 00c75f03 and b7e6a1e1 (two fixtures reformatted to `vilan fmt` layout).

## The transformer.rs change (solver-a-46 owns the file)

There is one change, in commit 420b184a, inside `host_arguments` (the B436 function, around line 8839). Its inline `is_object` check is replaced by two new private helpers placed right after it: `holds_a_hosted_object` and `hosted_value`, about 60 lines in all. Nothing else in the file is touched. The new code only runs for an argument at an `any` host parameter whose type is `dyn` or a list/array of (lists of) `dyn`.

## Fixtures and pins

All tests are in `crates/vilan-cli/tests/native_differential.rs` unless noted.
- **F83:** corpus program `vilan/test/shared-compound-write.vl` (+ `.mjs`), added to `DEFAULT_SUITE` and so to the leak and copy censuses.
- **F66:** `native/generic_instance_variants.vl`.
- **Closure-body find:** `native/closure_body_positions.vl`.
- **F70:** `native/nested_tuple_slots.vl`.
- **F82:** `native/swapped_struct_literals.vl`.
- **F67:** `native/local_closure_returns.vl`.
- **F69/F77:** `native/closure_view_parameters.vl`.
- **F48/F51/F78:** `native/reassigned_closures.vl`, `native/captured_returns.vl`, `native/default_hook_through_blanket.vl`.
- **F68/B503/tuple find:**
  - `native/print_layout.vl` (test `print_lays_values_out_by_nodes_rule_on_both_backends`);
  - `vilan_rt::inspect` unit tests (8, asserting node v24's exact bytes);
  - JS pin `inference::dyn_objects::b503_printing_a_list_of_trait_objects_prints_their_values`.
- **E243:** `the_js_run_reports_its_bundled_resources_on_stderr`. It holds on Windows because it checks only for the word `Bundled` on each stream, never a path spelling.
- Every pin was red on 0.43.0 except the three NOT-REPRODUCED pins.

## Censuses moved
- **Native leak census:** one new row, `shared-compound-write 38 0`. Still 0 live everywhere.
- **Native copy census:** one new row, `shared-compound-write 8 28`. No other row moved.
- **JS copy-elision census:** one new row, `shared-compound-write 16`. Total 571 → 587 (the new row only).
- **Whole-set native differential:** 129 enumerated / 102 identical / 27 refused / 0 broken. My first measurement, with the new program and F66, was 129/101/28/0; `tuple-access.vl` became identical with F70.
- **Platform-bound differential:** 9 / 6 / 3 / 0 (`estate.vl` now required).
- **Async differential:** 7 / 4 / 3 / 0, unchanged.
- **JS goldens:** none moved, so nothing needed regenerating.

## Gates
- **`native_differential` with `VILAN_NATIVE_DIFFERENTIAL=1`** (whole binary, so both modes) at the tip: 149/149 passed, sweep numbers as above. This includes the native leak gate and the copy census.
- **`check_scope_differential` + `docs`:** 27/27. Run at 420b184a; the two later commits touch only vilan-rt rendering and a test manifest.
- **vilan-cli + vilan-core suites, without native_differential:** 8098 of 8101 passed at 420b184a. The three failures were `every_corpus_program_has_a_test_of_its_own` in infer/release/interpreter, all caused by the undeclared new corpus program. 3f0916af fixed it, and the re-run is green (9/9, including the new per-program tests). The corpus byte gate is green.
- **vilan-rt:** 87/87, and the inspect tests 8/8.
- **Clippy** (`--workspace --all-targets -D warnings`) and **`cargo fmt --all --check`:** clean.
- **`scripts/ci-local.sh vilan-fmt`:** green. I first had to move my scratch probes off `.vl` and delete 21 leftover test files under `target/tmp` (the N138 problem of the leg scanning `target/`).
- No analyzer pass was touched, so no instruction counts are owed.

## New finds (`newitems46-native.json`, placeholder ids)
- **F?1** (fixed 6620ad0f): a closure expression body was emitted at the closure type's expectation.
- **F?2:** a closure handed to a generic callee without a written return is still refused (`apply(4, |k| Maybe::Just(k * 10))`). The callee's parameter type is read unsubstituted.
- **F?3:** a variant constructor used as a method receiver with a literal payload is refused natively (`Maybe::Just(3).and_then(f)`).
- **B?4** (solver): `mut found = Maybe::Nothing` inside a generic body, assigned later, stays `Maybe<any>`, and native refuses it.
- **E?5** (syntax lane): `vilan fmt` declines `print(adders[2](30));`.
- **F?6** (fixed f8b2a785): a nested tuple printed nested natively.
- **Not filed, because B510 already covers it:** a trait default passing `self` to a generic over the same trait is a JS internal error. It matters for F78's std simplification.

## For the owner
- **F68:** I implemented node's layout natively with no JS change. Choosing "one line on both backends" instead would change JS stdout and needs your word; it would be a small follow-up on top of `vilan_rt::inspect`.
- **F78:** the std simplification (`Flow::on_change`/`sub` as defaults) now works natively. It is reactive-46's call, and it needs B510 first if written as `observe_flow(self, ..)`.