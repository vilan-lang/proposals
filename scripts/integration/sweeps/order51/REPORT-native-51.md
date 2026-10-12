## native-51: final report

All nine listed items are done. I also took the two items the integrator handed over mid-lane, F134 and N170. The whole-set native triple is unchanged at **130/128/2/0**, the same as base; none of the items changes a corpus program. The deep-nesting canary is RED; that is the base's N169, explained under Gates.

**Branch `native-51`, tip `589bd4ee`, base `ca407da0`.** It lives in the worktree `vilan/.claude/worktrees/native-51`. Nothing is pushed and I have not rebased: `origin/next` has moved to `765c931d` (fix-51 merged). Each commit carries its own `## Unreleased` entry with a family marker, 11 of each (parity checked). `native-51-STATUS.md` is untracked and current. I rewrote my own unpushed B606 commit once to fold in a clippy fix (`&slot` became `slot`) and replayed the three commits after it.

### Commits
| item | commit | family | pin |
|---|---|---|---|
| F129 | 8a438612 | miscompile | `f129_a_copy_out_of_a_cell_is_taken_after_the_later_arguments_on_both_backends` (+ ignored `f129_a_later_argument_that_replaces_…`) |
| F132 | a6f38100 | fix | `f132_an_array_literal_inside_a_tuple_or_a_printed_value_builds_the_array_on_both_backends` |
| F131 | 3e92425c | fix | `f131_an_array_literal_against_a_generic_callees_binders_builds_the_array_on_both_backends` |
| F133 | 48b90602 | fix | `f133_an_array_of_closures_in_an_aggregate_builds_on_both_backends` (plus the map's named refusal) |
| B605 | 52e4af61 | fix | `b605_a_generic_function_over_a_dyn_pipe_builds_on_both_backends` |
| B606 | 5432eeb1 | fix | `b606_a_mirrored_stores_handle_as_a_dyn_source_builds_on_both_backends`, `b606_a_mirrored_stores_states_tell_the_same_on_both_backends` (A153's `states()` is now native) |
| F91 | 569b000e | fix | `f91_an_is_capture_in_an_if_conditions_conjunction_reaches_the_body_on_both_backends` |
| F130 | 2696ff5d | diagnostics | `printing_a_host_handle_is_refused_at_compile_time` (gains a second probe) |
| N167 | cab9faa4 | diagnostics | `a_refusal_inside_another_files_body_names_where_to_look` (gains a std probe; red with the anchor disabled) |
| F134 | 1c0c00d0 | fix | `f134_a_literal_leg_over_a_view_subject_matches_natively` |
| N170 | 589bd4ee | tooling | none new; the corpus, both native modes and the copy census are unchanged |

Every new pin was red on the base 0.48.0 toolchain, either a wrong answer or a rustc/emitter refusal. The new probe programs are under `crates/vilan-cli/tests/native/`.

### Where the item text was wrong, or more was going on
- **F129 (decision 1 below):**
  - Taking the copy last, as R-h ruled, is JS's answer only when the later argument writes the cell **in place** (push, insert).
  - When the later argument **replaces** the copied place whole (`cell.write().items = [..]`, or re-binding a captured `w`), JS keeps the old object and the late native copy sees the new one. On base this shape matched; it now diverges. It is pinned `#[ignore]` and filed as F?1.
  - The same hole already existed in §6.9's views (`w.measured(swap())`).
  - So that the late copy changes nothing else, it applies only where:
    - the copied type is one JS hands on by reference (a struct, `List`, map or set, fixed array, or `dyn`);
    - JS takes no copy at the call itself (`clone_sites`);
    - a later argument runs code.
  - Scalars, `str`, enums, tuples and `own` parameters keep the early read.
  - Other arguments that run code are settled in order first; that includes a `&` argument that computes a value, such as `&grown(cell)`.
  - Spec §6.7 says "`read()` copies", which is the base's answer for both shapes.
- **F132:** the cause was a tuple literal handing its WHOLE type to every element, plus `print`'s argument having no expected type at all. The variant-payload case was really the `print` seam. The emitter still hands each element its slot's type now, but the analyzer itself refuses `List<([i32; 2], bool)> = [([1, 2], true)]` (filed B?2).
- **F131:** two paths positioned arguments under the caller's binding instead of the instance's: overloaded operators, and calls dispatched through a bound. The dispatched path is a separate case that the generic `check` probe needed.
- **F133:** `[derive(PartialEq)]` over closures is refused by the checker, so the equality can't be observed from vilan; the item was really about the emitted Rust aggregate building at all. It also exposed an existing bug: an enum payload holding `Option<closure>` was a rustc refusal on base (`reference_eq(&a0, …)` over the reference its match leg binds). Both are fixed.
- **B605:**
  - The analyzer does record `P` for the call. The real causes:
    - an object type counted as closed whatever its arguments (`is_grounded` on `Dyn`);
    - the object call reading the receiver's recorded type instead of the one settled at the call;
    - an argument erased into `dyn Source<Option<P>>` building its object table at the callee's own `P`.
- **B606:**
  - The arity mismatch runs both ways:
    - `attach_observer`'s implementation takes fewer hidden context parameters than the declaration threads.
    - The `Source` blanket's `start` takes more (`turn_scope` and `ambient_nursery`, which `Flow::start` never threads).
  - Hidden parameters are now matched by the context they thread.
  - A missing safe-flavour context gets `None`, which is JS's `undefined`.
  - A missing strict one is still refused by name.
  - The analyzer half is filed as B?3.
- **Kolt acceptance:** the exhibit is `src/model.vl`, which is browser-entry code; the native backend builds one entry and no browser target. The exact shape (`let motd: dyn Source<Option<str>> = g.motd()`) is the B606 pin and prints identical bytes. Kolt's server entry emits natively on both base and tip (`--stdout`; I did not run a cargo build).
- **F130:** the vilan type of a never-suspending task is `Promise<i32>`, not `Task<i32>`, when `std::task` isn't in the program. That type has no native rendering, so the old rendered-type check never saw it. It is now refused by its vilan type, `Task` or `Promise` (filed B?4 for the inconsistent typing).
- **F91:** fixed as a Rust let-chain in `if` conditions only; a `&&` chain in a value position keeps its `match`. Vilan has no `while`.
- **N167:** a reachable std probe exists: `std::fs::copy_dir` checks clean, and its body reaches a host binding the native backend doesn't emit.
- **F134 / N170:** both premises held. F134's pin checks the native output directly, because JS only gives the same answer after B577 (fix-51); it should become a `compare` once both are on one tree.

### Gates (on tip 589bd4ee)
- **Full suite** (`--cargo-profile ci-test -E 'not binary(deep_nesting)' -j 6`): 10280/10280 passed, 32 skipped. Within it `ci_ignored_pins` 12/12, `hygiene` 3/3, `corpus` 13/13, `check_scope_differential` 15/15; the native differential's default mode with the copy census, leak census and cycle census all pass.
- **Native sweep mode** (`VILAN_NATIVE_DIFFERENTIAL=1`, whole binary): 267/267 passed. The triple is 130/128/2/0 at base, after F129, at the pre-F134 tip and again at the final tip. The two still refused are `async-await.vl` and `signal-update.vl`.
- **clippy** `--workspace --all-targets -D warnings`: 0. **cargo fmt --check**: 0. **vilan fmt --check .**: 0.
- **`scripts/ci-local.sh perf`:** T2 green, growth ×1.929. No analyzer.rs or mono.rs changes, so no pass-map change and no `[[bump]]` row.
- **Kolt cold-check RSS:** median 260,276 KB on tip vs 267,232 KB on base (−2.6%). The check path doesn't touch vilan-rust.
- **Deep-nesting canary (1536 KiB): RED**, 17/18; `a_thirty_level_chain_still_fits_libtests_own_two_mib_thread` overflows. This is the base's N169 (incr-51a's). `crates/vilan-core` has no diff against `ca407da0`, and vilan-core doesn't depend on vilan-rust.

### Functions changed (vilan-rust/src/lib.rs, the emitter; analyzer.rs and mono.rs untouched)
- **Existing:** `call_arguments_adapting`, `binary` (operator dispatch path), `emit_dispatch`, `dispatch_to_member`, the `Expr::Tuple` arm, `place_argument`, `is_grounded`, the `call_expression` dyn-method branch, `erase_into_object`, `ensure_object_impl`, the enum equality legs in the enum emission, `reference_equality_reaches`, `check_reference_equality` (message), `if_branch`, `refuse_unprintable`, `str_literal_pattern`, `type_of`, and `declared_return_type`'s doc.
- **New:** `defers_its_cell_copy`, `aliases_on_the_js_backend`, `runs_no_code`, `computes_a_value`, `object_slot_arguments`, `capturing_let_chain`, `release_captures`, `async_handle_name`.
- **New fields:** `dispatched_bindings`, `erasing_argument`.
- **vilan-rt:** `ReferenceEq` for `[T; N]` and `HeapArray<T, N>`.
- Nothing in dbg.rs or the transformer was touched.

### Finds filed
Six entries in `proposals/scripts/integration/sweeps/order51/newitems51-native-51.json`, repros in `sweeps/order51/native-51/finds/`:
- **F?1:** F129's residue, the replacement shape (decision 1).
- **B?1 (JS):** `read(&seven())` passed to a `&i32` parameter crashes on JS with a TypeError; it prints 8 natively. This is fix-51's territory.
- **B?2 (checker):** a list of tuples holding array literals is refused against its annotation.
- **B?3 (context pass):** the declaration's hidden-context union misses the blanket impl's `start`, so JS passes `undefined` at a `dyn` `start` call.
- **F?2 (native):** a struct holding a map of closures (a handler table) is still refused by name.
- **B?4 (checker):** `async e` is typed `Promise<T>` or `Task<T>` depending on whether `std::task` is loaded.

The ignored F129-residue pin's reason currently leads with `F129`; it should be retargeted to F?1's allocated id when you assign it.

### Decisions for the owner
1. **F129's semantics.** Spec §6.7 says `read()` copies, which was the base's answer for both shapes; JS's aliasing is the outlier, a gap in the analyzer's copy policy (B457 copies when the callee writes the cell, but not when a later argument does). R-h's copy-last answer matches JS for in-place writes and now diverges for whole-place replacement, which the base got right. The alternative is to fix JS instead: copy a `Shared::read()` argument at the call when a later argument reaches an in-place write of that cell. My recommendation is to keep R-h for this order and settle the language rule next order: either §6.7's "`read()` copies" stands and JS changes (my preference, since it answers both shapes and both backends), or the spec states aliasing with this replacement exception. Either way the ruling is about a semantics trade, which is yours.
2. **B606 passing `None`.** When an implementation needs a safe-flavour context that the trait declaration doesn't thread, the object table now hands it `None`, matching JS's `undefined`. My recommendation is to keep it as a stopgap and have the context pass fix the union (B?3), so a `dyn` call threads the caller's real context.
3. **F133's next shape (F?2).** Should maps of closures get reference equality too? I recommend yes, next native order: handler tables are a common shape and the equality is unobservable from vilan.
4. **F134's pin.** I recommend switching it to a `compare` once fix-51's B577 and this branch are both on next.

All my processes are stopped.
