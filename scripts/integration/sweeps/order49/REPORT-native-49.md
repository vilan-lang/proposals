## native-49: final report

The lane is done. The tip is **703efbd8** on branch `native-49`, in the worktree `vilan/.claude/worktrees/native-49`. Its base is origin/next @445c9346, which had not moved at my last fetch. There are 15 commits; nothing is pushed. `LANE-STATUS.md` is untracked.

Two commits carry no CHANGELOG entry of their own:
- **011650c0** narrows two of my earlier commits and rewrites their two entries.
- **703efbd8** adds the `## Unreleased` heading. My helper had mistaken the comment's mention of it for the section.

The section holds 12 entries, each with a family marker.

### Items

**F113: DONE** (e17bea5c, fix)
- A pattern over the view a `borrows` call returns now copies the pointee first (`(*call).clone()`, helper `copy_a_pattern_subject`). This covers `is`, `match`, the `?` lift and a destructuring `let`.
- Pin: `f113_a_pattern_over_a_borrows_calls_view_binds_copies_on_both_backends` (`native/view_call_subjects.vl`).
- capture-clones.vl is still refused, at B579 (the mixed-width operator).

**F114: DONE** (d90eba95, performance)
- `cell_view_place` now accepts a spine over a `Shared` view, for reading intrinsics only.
- Pin: `f114_a_reading_intrinsic_over_a_shared_views_field_reads_in_place_on_both_backends`. It asserts the emitted `main` has no copy left except three std calls.
- The premise was incomplete. `HashSet::contains`, `HashMap::get` and `contains_key` are std methods, not intrinsics, so they still copy. Filed as F?1.

**F116: DONE** (61c20239, feature)
- A generic resource with `Drop` now calls the `drop` instance its own type arguments bind (new `DropImpl`/`drop_impl`).
- An enum with `Drop` gets a Rust `Drop` impl.
- A by-value `match` that consumes a `Drop` value now holds it undropped (`ManuallyDrop`) and reads each capture out. This is destruction.md R6: the subject's own teardown is suppressed, as on JS. Before, rustc refused it (E0509).
- A guarded leg on such a match is refused by name.
- Pins: `f116_a_generic_resource_and_an_enum_with_drop_tear_down_alike_on_both_backends`. F56's enum pin was flipped from a refusal to Identical and renamed `a_resource_enum_with_drop_and_its_struct_twin_build_natively`.

**F117: DONE** (9335aed5, fix)
- A member of a bare-trait impl now reads its `Self` as the receiver it was instantiated for. This reuses the existing trait-default rewrite (`current_self_type`/`current_self_traits`).
- Pin: `f117_a_self_in_a_bare_trait_impl_member_is_the_receiver_on_both_backends`.

**F118: DONE** (60dfbe03, feature)
- New `vilan_rt::TupleKey` and `tuple_get`.
- `TupleLen`, `TupleKeys`, `TupleEntries` and `TupleGet` are now emitted against the instance's concrete tuple.
- A `for` over a tuple is unrolled, one body per position; `break` and `continue` go through labelled blocks.
- `bind_generics_against` now reads the declared side as written. Without that, a tuple of tuples rebound the wrong slot.
- Pins: `f118_the_tuple_blankets_are_identical_on_both_backends`, and A152's zip/unzip pin flipped to `zip_some_and_unzip_are_identical_natively`.

**F119: DONE natively** (0c53912c, fix)
- I took the native door; the analyzer is untouched.
- A function item's own type now renders as its closure type, keyed per item.
- `function_value` builds the value at that type.
- A call through a binding of an item now uses that item's parameter conventions. `let b = bump; b(&mut count)` was a pre-existing E0308.
- Pin: `f119_a_blanket_method_on_a_function_item_is_identical_on_both_backends`.

**F120: DONE** (ecbfa6e7, fix)
- An `async` block's body is now awaited once per `Task` layer its value carries.
- Pin: `f120_a_nested_async_block_is_assimilated_on_both_backends`.

**F109: premise wrong, closed as fixed.** Its repro already printed 1 on 0.46.0, because F100 had lowered the literal. The real wall was F121 (below).

**F121: DONE** (36787f7f, fix)
- Added `Js for [T; N]` to vilan-rt.
- Pin: `f121_a_fixed_array_prints_and_a_struct_holding_one_builds_on_both_backends`. F109's repro is at the head of that pin.

**F122: NOT TAKEN.** Moving large arrays off the stack is a rendering decision that waits on the array-lengths paper (Q12). Note that a boxed array's `clone` would still go through the stack in debug builds.

**N154: DONE** (4306c552, tooling)
- New module `vilan_core::teardown` with `statement_teardown`, `region_end` and `drops_nontrivially`. It is pure over `Program`.
- It sits outside `analyzer/`, so it stays clear of incr-49's core. vilan-core's `lib.rs` gained one line: `pub mod teardown;`.
- The transformer's `own_teardown_extent`, `widen_over_declarations` and `resolve_extent` moved into it. vilan-rust's copy is deleted.
- No behaviour change: the corpus is byte-identical, and the F97/F116 pins and resource*.vl pass.
- `ci-local.sh perf`: T2 green, growth x2.004. No analyzer function was touched, and the pass map is unchanged.

**N158: DONE** (9e113501, tooling)
- New `legs_in_parallel`: a `thread::scope` with up to four workers. Results come back in list order, and a leg's panic is resumed with its own message.
- Each test and worker gets its own cargo target directory, to avoid the cargo lock and same-name binary races. A cold vilan-rt build takes about 3 s.
- The 15 panic-path programs each get their own file name now.
- Pin: `parallel_legs_answer_in_order_and_resume_a_legs_panic`.
- Wall times, before → after:

| test | measured alone | inside the full binary run |
|---|---|---|
| default suite | 86.4 → 36.8 s | 144.4 → 36.4 s |
| panic paths | 78.4 → 33.6 s | 115.8 → 32.8 s |
| leak census | 52.6 → 24.8 s | 105.8 → 24.1 s |
| copy census | 30.3 → 18.0 s | 43.7 → 17.0 s |

- Load during the "alone" runs was about 14–20 before and about 21–26 after; in the full-binary runs it was 14–28.

**F99, aliasing half: FILED.** The note is `sweeps/order49/native-49/F99-aliasing-loans.md`.
- The model groups each root's view bindings into a loan group.
- If the members' live intervals nest, Rust reborrows are enough.
- If they interleave (transparent-references.vl does), the root goes into the cell a captured `mut` binding already uses, and views become lens handles. A compound write settles the place once, which fixes native-48's double evaluation. A `&mut` call is refused when another argument reaches the same root.
- It is not S (I estimate M): the nesting test needs an ordered access list that no record holds today, and every view read and write path needs to learn about handles.
- Filed as F?2. The refusal stays as it is.

**Two silent wrong answers I found and fixed:**
- **7a139432, then scoped in 011650c0** (miscompile):
  - A tuple, fixed array or enum variant holding two values that owe a teardown dropped them in Rust's declaration order; vilan drops them in reverse. It is now refused by name, but only for a binding the block drops whole.
  - My first version also refused resource_take.vl's `Couple::Two`. That variant is consumed by its `match`, so it never hit the bug, and the program had regressed to refused. 011650c0 fixed that.
  - Pin: `an_aggregate_with_two_teardowns_is_refused_by_name_rather_than_reordered`.
- **b4074acd, then scoped in 011650c0** (miscompile):
  - A generic operator over a type with a written impl used Rust's structural `==`. `Loose`'s one-field `eq` gave `true` natively and `false` on JS, through a generic `!=`, a `List` and an `Option`.
  - It now reads `generic_dispatch` the way the JS emitter does. Scalars, `bool` and backed enums keep the Rust operator (`compares_natively`); without that the copy census moved.
  - Pin: `a_generic_operator_calls_the_written_impl_on_both_backends`.

### Whole-set triple
None of my items flips a corpus program, so the triple never moved:
- **Platform-free: 130 / 126 / 4 / 0**, at the base and at the tip. The four refused are async-await, signal-update, transparent-references (F99) and capture-clones (B579).
- Async: 7 / 4 / 3 / 0.
- Platform-bound: 9 / 6 / 3 / 0.
- Both native modes ran: the default-mode subset in the full suite, and the whole-set mode at the tip, which passed 219/219 including the three whole-set tests.
- The copy census and the leak census both match their committed tables; neither moved.

### Gates at the tip
- `cargo nextest run --workspace -j 6`: 9935 run, 9934 passed, 32 skipped, at load about 30.
- The one failure was `init::the_fullstack_template_builds_both_entries_and_serves_them` ("served page should be the shell"). It passed 3/3 when rerun alone at load 34, so I read it as a load flake and did not file it.
- `ci_ignored_pins`, `hygiene` and `corpus`: 28/28.
- clippy `--workspace --all-targets -D warnings`: clean. `cargo fmt --check`: clean.
- ci-local `vilan-fmt` and `windows`: green.
- I did not touch `dbg.rs`, `show.rs`, `inspect.rs`, or the context or `[track_caller]` emission sites.

### Finds
Filed in `sweeps/order49/newitems49-native.json`, with repros in `sweeps/order49/native-49/finds/`:
- **B?1:** a list literal of array literals under `List<[i32; 2]>` is refused by the analyzer.
- **A?1:** `[T; n] == [T; n]` is refused. std has no array `PartialEq` blanket, and the error tells you to write a per-length impl.
- **B?2:** calling an element of a list of function items is refused ("cannot call this as a function").
- **F?1:** std methods over a `Shared` view's field still copy the field (the remainder of F114).
- **F?2:** the F99 aliasing-loans design, as the item's next step.

### Questions for the owner
1. **Is R6 confirmed for a consumed `Drop` enum?** A by-value `match` that consumes it skips the enum's own `drop` body on JS, and on native as now emitted. My recommendation is yes, since R6 says the subject's teardown is suppressed. But a payload bound to `_` then leaks without its teardown; I recommend the spec says so explicitly.
2. **F99's order.** I recommend building the reborrow lowering first (no runtime cost) and the cell-and-handle lowering as its own slice.
3. **F122.** I recommend waiting for the array-lengths paper's Q12 ruling. Boxing alone is not enough, because cloning a boxed array still goes through the stack in debug builds.
4. **N158's extra target directories.** It adds up to 12 per-test-and-worker cargo target directories under `CARGO_TARGET_TMPDIR`, each with about 3 s of cold vilan-rt build. I recommend keeping this, since the cargo lock was the bottleneck.

The F99 note is in the proposals repo, which the integrator commits.
