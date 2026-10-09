## native-48: final report

**Branch and base.** Branch `native-48`, tip **d4093edf**, worktree `vilan/.claude/worktrees/native-48`, not pushed.
- Base is origin/next @e75bc57c. It had not moved at my final `git fetch`, so I did not rebase. Every number below is from this base plus my commits.
- There are 19 commits: one per item, plus one fix that blocked F97 and one commit that re-points two pins. Each item commit carries its `## Unreleased` CHANGELOG entry (19 entries, 19 family markers).
- `LANE-STATUS.md` is untracked.

**Whole set (platform-free).** Base 130 enumerated / 103 identical / 27 refused / 0 broken. Tip **130 / 126 / 4 / 0**. Async (7/4/3/0) and platform-bound (9/6/3/0) are unchanged.
- The brief's 129/102 was one program short; I measured 130/103 at e75bc57c.
- **23 programs flipped to identical:** arena, css-block, expression-lift, fixed-arrays, for-mut-container, generic-method-return, lift-chain, match-patterns, math, multiline-string, preflight, resource, resource_exit, resource_take, self-return, set, side-effect-let, spread-parameters, style-when, style, theme, try-assert, tuple-spread.
- **Still refused (4):**
  - async-await: by design.
  - signal-update: by design.
  - transparent-references: F99's alias half, not done.
  - capture-clones: its new wall is analyzer find F?3.

### Items

Every pin is in `native_differential` with its own `native/*.vl` fixture and its own program name. Every fixture is `vilan fmt`-clean and red on 0.45.0.

- **F49 + F103 — fixed, 79a5ddf8 (`miscompile` + `performance`).**
  - **Cause:** a captured `mut` binding lives in a cell, and every read of it called `get()`, which clones the whole value.
  - **Fix:**
    - A field, tuple-slot or subscript read is a link of F62's scoped-borrow spine over the cell. Subscripts are settled first and are now bounds-checked in vilan's words; the `Shared`-view spine gets that too.
    - A `&self` call or `&` argument holds a view of the cell (`Shared::borrow`, new) in the call's own block. The view is taken after the by-value arguments are evaluated.
    - Reading intrinsics (`len`, `get`, `contains`, the `str` readers) read through the same view.
    - A value already read out of a cell is no longer cloned a second time.
  - **The base had a silent wrong answer:** `w.measured(w.add("c"))` printed 5 natively and 6 on JS. It now prints 6.
  - **Evaluation order:** the answer is written into spec/memory.md §6.9 as a new "Native note".
  - **Decision to confirm:** when another argument carries a closure that *writes* the binding, the `&` callee gets the old copy instead of a refusal.
  - **Measured:**
    - Store probe s1: 83.05M → 76.45M Ir (−7.9%); `woken.get()` no longer appears.
    - rpc example: `writer.get()` 1 → 0.
    - kolt's server: `&this.get()` 13 → 0. It still builds natively at the tip (checked on a copy).
  - **Pins:** `a_field_read_on_a_boxed_binding_copies_the_field_alone_on_both_backends` (`boxed_field_reads.vl`; 22 → 1 whole copies) and `a_shared_loan_of_a_boxed_binding_reads_through_its_cell_on_both_backends` (`boxed_self_calls.vl`; 16 → 2, plus the 5/6 answer).
- **F102 — fixed, 65263176 (`fix`).**
  - **What it does now:** a native compile-time refusal, as F39 was answered. It refuses a call that holds a `&mut` view of a boxed binding while another argument carries a closure that reaches that binding. It finds the closure as a literal, a `let`-bound closure (aliases followed), one the literal calls by name, or one held in a value a `let` built.
  - **Runtime half:** a closure that arrives another way still aborts, and `REENTRANT_READ`'s sentence now names this shape.
  - **Why only native:** I did not add an analyzer half, because rule 4 permits scalar content writes like c9's. Filed as owner question F?6.
  - **Pins:** `a_closure_reaching_a_binding_under_its_mut_view_is_refused_by_name` (six refused shapes plus control `closure_beside_a_mut_view.vl`) and `a_closure_under_a_mut_view_the_compiler_cannot_see_stops_with_the_runtimes_sentence`.
- **F107 — fixed, 42c2a5e5.** Each `Task` layer in a written-`async` callee's return is now one more await. The call's type reads as the payload everywhere, which also fixes `print(make())`. Pin: `an_async_function_returning_a_task_answers_the_value_on_both_backends` (`async_task_returns.vl`, including the interleaving order).
- **F104 — fixed, b0691a8e.** A closure whose body diverges now writes its return type; rustc had inferred `!`. Pin: `a_closure_whose_body_diverges_builds_on_both_backends` (`diverging_closures.vl`).
- **F105 — fixed, 2fee1812.** `variant_payload_types` resolved only the head of the payload type (`List<Tree<T>>`), so nested elements were minted at `any`. It now resolves the whole type. Pin: `a_generic_variant_nested_in_a_variants_list_builds_on_both_backends` (`nested_generic_variants.vl`).
- **F106 — fixed, d08f6be8.** `settled_value_type` is widened to rebuild the whole recorded type under the call's substitution, and every pattern subject reads it: match, is, conjunction and destructure. This is also F92's `is` half. Pin: `a_generic_call_as_a_pattern_subject_is_identical_on_both_backends` (`generic_call_subjects.vl`).
- **F92 — fixed, bd46dcc7.**
  - **Fix:** a field read off a call now names its struct through the call's substitution (`call_value_head`). A trait default's `Self` is read off the receiver. A `?.` binder's type comes from its own entity, where it had none before.
  - **Pin:** `a_field_read_off_a_generic_call_is_identical_on_both_backends` (`generic_call_fields.vl`, plus 3 corpus programs).
- **F108 — native half done, 1a3f8a01 (`diagnostics`).**
  - **Fix:** a refusal raised in another file's body now carries that file. One found in a library body is drawn at the user's call, with the body and file named. This also fixed a refusal inside a user module that the base drew over the entry's `import` line.
  - **Open:** the solver half (grounding `push_many([])`) is not done. The program is still refused natively.
  - **Pin:** `a_refusal_inside_another_files_body_names_where_to_look`.
- **F99 — half done, 4e2a969f.**
  - **Done:** an `Option<&T>` used straight away as a by-value or `&` argument now has its payload read out (`.cloned()`), so arena.vl runs.
  - **Not done:** a view binding that aliases another (transparent-references.vl). Modelling it with cell handles hits two-borrows-in-one-statement panics; the double evaluation in `same(c) /= 10` is one example. It needs a real design.
  - **Pin:** `an_option_of_a_shared_view_consumed_in_place_is_identical_on_both_backends` (`payload_view_reads.vl`).
- **A `main` that returns its exit code — fixed, 3f7ff1c7.** This was pre-existing and blocked resource_exit.vl; it is not a tracker item. The emitted code was invalid Rust. It now goes through `vilan_rt::main_guard_exiting`. `compare` now compares a program-chosen exit code (anything other than 0 or 1). Pin: `a_main_answering_its_exit_code_exits_with_it_on_both_backends` (`exit_code_main.vl`).
- **F97 — fixed for non-generic structs, edd7afa1 (`feature`).**
  - The resource's `drop` is now a Rust `Drop` impl.
  - A struct with two or more fields that need teardown declares those fields in reverse order, so they drop in reverse.
  - A binding is dropped after the statement holding its last read. It drops at the same point the JS transformer closes its `finally`: I copied that resolution logic, so widening and nesting match (copy filed as F?8).
  - F37 no longer moves a field out of a value whose type has a `Drop` impl (E0509).
  - Still refused by name: a generic resource with `Drop`, and an enum with `Drop` (F?7).
  - F56's "still refused" pin is renamed and its struct half flipped.
  - **Pin:** `a_resource_with_a_drop_impl_tears_down_in_the_same_order_on_both_backends` (`resource_teardown.vl`).
- **F95 — fixed, 09d6bbbc.** A `HashSet` loop walks the set's table values in insertion order. `for e in &mut c` calls the recorded `next_mut` on the place itself. Pin: `a_for_over_a_set_or_a_containers_next_mut_is_identical_on_both_backends` (`set_and_container_loops.vl`).
- **F100 — fixed, d71d9fb8.** Covers the triple-quoted string, `[v; n]`, `is_finite`, and fixed-arrays.vl's other walls (array `len()`, array patterns, array literals). The doubled backtick in the refusal message is fixed. Pin: `the_small_lowerings_are_identical_on_both_backends` (`small_lowerings.vl`).
- **F98 — fixed, c0e72300.** A typed decoder turns a const value in the JS layout into a native struct, tuple, enum or `NativeMap` (which covers `Style`, `HashMap` and `HashSet`). A `void` const is the unit. A native build now writes the CSS sidecar the way JS does (`vilan-cli/src/native.rs`). Pin: `a_const_aggregate_is_identical_on_both_backends` (`const_aggregates.vl`).
- **F93 — fixed, 7b14cfc8.**
  - **Fix:** a guarded leg is Rust's guard. A str-backed variant nested inside a pattern becomes a guard over a binder.
  - **Also:** an operator over two different numeric widths, which the analyzer admits, is now refused by name instead of failing in rustc (F?3).
  - **Pin:** `a_guarded_match_leg_is_identical_on_both_backends` (`guarded_legs.vl`).
- **F94 — fixed, 12651cb2.** Covers spread parameters, tuple spreads, the empty pack `()`, and the one-element tuple type `(T,)`. Pin: `a_spread_parameter_and_a_tuple_spread_are_identical_on_both_backends` (`spread_packs.vl`).
- **F101 — fixed, 05d71e3f.** A mapped tuple expands to a concrete tuple for each instantiation. A tuple comprehension is unrolled, with each slot emitted under the binder's own generics at that slot's type. Pin: `a_mapped_tuple_and_its_comprehension_are_identical_on_both_backends` (`mapped_tuples.vl`).
- **F96 — fixed, 6fe8a620.** A user `Lift` goes through the container's own `map`/`and_then` with a synthesized capturing closure, and a region nests lazily. A user `Try` becomes `verdict` plus `from_bad`. The capture-prelude code is factored out and shared with closure literals. Pin: `a_user_lift_container_and_a_user_try_are_identical_on_both_backends` (`user_lift_and_try.vl`).
- **d4093edf — re-points two pins.** F100 and F101 removed the walls those pins expected. F108's module half now refuses F25's print-of-a-function. A152's zip/unzip now expects the `TupleKeys` wall.

### Censuses
Neither native census moved; both table tests are green at the tip. No corpus golden moved.

### Gates
- `cargo nextest run --workspace -j 6` at 6fe8a620: 9797 run, 9795 passed, 2 failed, 34 skipped. The 2 failures were the pins re-pointed in d4093edf. Both pass on rerun, and the whole native_differential binary passes at the tip.
- `native_differential` with `VILAN_NATIVE_DIFFERENTIAL=1` at d4093edf: **197/197**.
- `check_scope_differential`: 15/15.
- clippy `-D warnings`: clean. `cargo fmt --check`: clean.
- ci-local `vilan-fmt` and `windows`: green. `perf`: T2 green, growth x1.938.
- No analyzer function was touched.

### Needs a ruling
- **F?6:** should F102's refusal belong to the language (both backends) or stay native-only? My recommendation is native-only.
- **F49:** confirm the old-copy fallback when a closure writes the binding beside a `&` view.
- **Family markers:**
  - F49 is `miscompile`, because of the 5/6 answer.
  - F103 is `performance`.
  - F97 through F101 are `feature`.
  - F102, F104–F107, F92 and F93 are `fix`; so is the exit-code `main` fix (3f7ff1c7).
  - F108 is `diagnostics`.
- **The brief's refused-list descriptions are shifted against the tracker.** It calls F99 "non-plain const", which is F98; F97 "for over iterator", which is F95; and F95 "guarded legs", which is F93. I followed the tracker IDs and did all of them except F99's alias half.

### Finds
Eight filed in `sweeps/order48/newitems48-native.json`, with repros in `sweeps/order48/native-48/finds/`.
- **F?1 (JS miscompile):** an `Option<&str>` element view given to `unwrap_or` returns the (base, key) pair.
- **F?2 (JS):** `&` of a call result passed to a generic `&T` throws a `TypeError`.
- **F?3 (analyzer):** `-`, `*`, `/` and `%` accept mixed integer widths, while `+`, `<` and `==` refuse them.
- **F?4 (native):** destructuring a view returned by a `borrows` call binds references.
- **F?5 (native perf):** a reading intrinsic over a `Shared`-view field still copies the field.
- **F?6:** the F102 owner question above.
- **F?7 (native):** generic and enum resources with `Drop`.
- **F?8 (refactor):** the teardown-extent logic is duplicated between the JS transformer and vilan-rust.

### Emitter functions touched
Almost everything is in `vilan-rust/src/lib.rs`.
- **Calls and arguments:** `call_arguments_adapting`, `call`, `call_expression`, `emit_intrinsic`, `object_call`, `binary`.
- **Field reads, spines and copies:** `shared_view_field_read` (now on the new `cell_spine` / `spine_path` / `cell_view_place`), `copy_a_consumed_place_read`, `subject_is_a_place`, `owned_field_spine_root`, `field_name`, `type_of`, `settled_value_type`.
- **Types:** `declared_return_type`, now split with `signature_return_type` and `assimilated_return`; `rust_type_inner`, for 1-tuples and mapped tuples.
- **Patterns:** `match_expr`, `pattern`, `collect_pattern_bindings`, and the destructure / conjunction / if-let / `is` subject sites.
- **Blocks, loops and literals:** `emit_block`, which gained the teardown plan; the for-each lowering and `for_each_iterator`; `const_value`, plus `const_struct`, `const_tuple` and `const_variant`.
- **Functions and types:** `closure`, with the capture helpers factored out; `function_body`, for the exit-code `main`; `ensure_struct` and `ensure_enum`; `variant_payload_types`; `parameter_parts_at`.
- **Lifts and asserts:** `try_assert`, `std_lift`, `std_lift_region`.
- **Host bindings:** `scalar_host_binding`.
- **New helpers:** the F102 guard, F97 teardown, F101 tuple-family and F96 lift/try functions.

### Changes outside vilan-rust
- **vilan-rt:** `Shared::borrow`, `main_guard_exiting`, and the `REENTRANT_READ` sentence. I did not touch `dbg.rs`, `show.rs` or `inspect.rs`.
- **vilan-cli:** `native.rs` writes const assets.
- **Spec:** `vilan/docs/spec/memory.md` §6.9 gains the native note.
