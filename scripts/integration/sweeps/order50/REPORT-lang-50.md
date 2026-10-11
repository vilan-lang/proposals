## lang-50 hand-back (Order 50, Opus 5.5)

All five slices are built, plus S4 (named lengths). The branch is rebased onto the new next, and every gate is green. Nothing is pushed.

**Tip** `56131686`. **Base** `940ce8ec` (the solver-50 merge). I started on `f99dc28e`, then rebased before hand-back as you asked. Worktree: `/home/reed/code/vilan-lang/vilan/.claude/worktrees/lang-50`, branch `lang-50`.

**S2 is on the branch** (also noted in `LANE-STATUS.md`). std's `impl [type T: Debug; _] with Debug` is in S5, inside debug.vl.

### Commits (oldest first)
| sha | item / slice | family |
|---|---|---|
| 4dd26392 | S1, R2: `Type::Array(TypeId, TypeId)` plus `Type::Length(n)`. Byte-identical output | feature |
| 24a04e0d | S2: impl heads `[type T; _]` and `[type T; const N]` (A163) | feature |
| 84f90f0b | S3: `<const N>` on fun/struct/enum/trait, numbers as generic arguments, kind checks | feature |
| 809deddf | Fix: a directed array literal at an open element types by its items. This bug predates this order (it reproduces on v0.47.0) | fix |
| 8e08fc9f | S5: std array impls (A161 Items, A166 PartialEq, Hashable, Debug, `to_list`, `iter`), plus `std/collections.md` | feature |
| 1c386d28 | S6: book and spec (D15) | feature |
| b688841e | S4: named lengths, plus E287 halves (a) and (b) (taken into my items as you directed) | feature |
| 56131686 | Five ci-class `[[bump]]` rows for S5's std growth | in S5's entry |

Each slice has its own CHANGELOG entry with a family marker. After the rebase all 35 entries on next are still there, plus my 7, each with its marker. There are 20 `NEW` ledger rows, and row 20 is re-keyed; the proposals ledger has the matching prose rows.

### Where the premises were wrong
- **The contract-hash pin can't be written** (paper §3). No contract can hold an array today, because arrays aren't Wire. The renderer does write the resolved number. Filed as E296.
- **S0 and S0b were already done** (B582, B590), and F122 already boxes large arrays.
- **`Eq` is not in S5.** `impl [type T: Eq; _] with Eq {}` is refused. A subtrait impl over a structural subject can't reach its supertrait's impl through an element's sub-bound. Tuples fail the same way on v0.47.0. Filed as B609.
- **The directed-literal door needed a fix** (809deddf). A literal at an open element answered with the callee's own `T`, which left `T` unbound natively.
- **§5.3 read the const rule as hypothetical, but it was a live bug.** While building, `const N + 1` folded `N` to 0 and printed a wrong value silently. It is now refused.
- **The paper's "`<const N>` means nothing but a length" assumed `_`/`const N` could reuse TypeBinder.** It can for `_`, but `const N` needs its own node (`Node::LengthBinder`) so the formatter can print it back and it can appear at a const parameter's argument position (`impl Ring<type T, const N>`).
- **E287 (c) and (d) landed with solver-50.** The rebase kept their empty-array message and my suffix refusal. I updated their pin `e287_a_suffixed_length_other_than_usize_is_refused` to my wording, inside the S4 commit.

### Gates (rebased tip)
- **Full suite** (`--cargo-profile ci-test -E 'not binary(deep_nesting)' -j 6`): 10,268 run, 10,267 passed, 31 skipped. The one failure was solver-50's E287 pin, which still expected the old message. I updated it and the targeted run passed 35/35. Before the rebase, the tip passed 10,227/10,227.
- That run includes `ci_ignored_pins`, `hygiene`, corpus, `check_scope_differential`, the native differential in default mode, and the four editor differentials.
- **Native differential, sweep mode** (`VILAN_NATIVE_DIFFERENTIAL=1`): 258/258.
- **S1 on its own** was byte-identical: corpus, inference, the native sweep, the four differentials and `check_scope_differential` gave 437/437.
- **clippy** `-D warnings`, **cargo fmt --check** and **vilan fmt --check .** are all clean.
- **Perf** (`ci-local.sh perf`): T2 green. Against next @f99dc28e, each binary measured from its own tree's std, instructions rose 0.13% (genapp:46) to 0.91% (example:math). That is a constant cost from the four std impls every program loads. The bump rows cover the ci subjects above 0.4%; that number was measured before the rebase.
- **Late writes**: 0 on kolt, at every phase.
- **kolt cold-check RSS**: base median about 264–265 MB, tip about 269–271 MB, roughly +2%, inside the 3% limit.

### Functions changed (analyzer.rs, mono.rs, emitters)
- **Analyzer, new:** `walk_array_length`, `length_type_id`, `substitute_length`, `array_lengths_agree`, `length_kind_error`, `generic_argument_kind_error`, `check_call_generic_argument_kinds`, `walk_generic_argument`, `named_length`, `inside_a_const_expression`.
- **Analyzer, changed:** `array_length_literal`, `register_subject_binders`, `register_generic_parameters`, `walk_type_node` (Number and LengthBinder arms), the `prepped_type_locals` drain (kind check and named lengths), `resolve_prepped_local` (new `Expr::LengthValue`).
- **Analyzer, comparators:** `reconcile_type`, `compare_type_rigid`, `impl_subject_matches`, `same_impl_type_shape`, `same_type_structure`, `bound_argument_agrees`, `annotation_admits`.
- **Analyzer, generic walks:** `collect_generics`, `collect_residual_generics`, `type_is_fully_determined`, `type_is_ground`, `collect_subject_binders`, `substitute_type`, `substitute_member_type`, `substitution_fixed`.
- **Analyzer, other:** `infer_type_inner` (directed literal, Repeat), the subscript, the pattern array arm, `drop_members`, `check_written_nominal_bounds`, the B424 message, `pretty_print_type_inner`, `render_type_canonical`.
- **mono.rs:** `collect_type_generics`.
- **impl_select:** `subject_shape_matches`, `instantiation_agrees`, `bind_subject`, `collect_subject_binders`.
- **transformer:** `write_type_key`, Repeat, ArrayLen, LengthValue, plus the new `array_length` / `array_length_or_report`.
- **vilan-rust:** `write_type_key`, `substituted`, `deeply_resolved`, `rust_type`, `bind_parameters`, `is_grounded`, `is_closed_in_itself`, `nominal_struct`, `nominal_enum`, the list literal (now uses its own count), heap sizing, Repeat, LengthValue.
- **Mechanical arms in other lanes' files:** printer.rs, liveness.rs, call_graph.rs, init_order.rs, track_caller.rs, hint/hover/written labels. Also one additive hunk in debug.vl, which is debug-50's file.
- **Pass map:** I added a row for `check_call_generic_argument_kinds`, in the proposals checkout, not committed.

### Finds
They are in `sweeps/order50/newitems50-lang-50.json`, with repros in `lang-50/finds/`.
- **B610:** the directed-literal bug, already fixed in 809deddf.
- **B609:** structural subtrait through an element sub-bound. This is what blocks `Eq`.
- **F131:** natively, a nested array literal passed where a generic `[T; N]` is expected emits its inner literals as `Vec`s. Example: `grid == [[1, 2], [3, 4]]`.
- **E296:** an `[rpc]` array parameter is refused twice, and the second refusal names the type `_`.
- **N168:** a toolchain inside a vilan checkout reads that checkout's std. One std edit poisoned a running suite of mine.

The same file carries updates for E291, E287, D15, A161, A163, A166 and A170.

**E291 census** (`lang-50/census/e291.py` and `.out`): spaced generic lists number 0 across std, corpus, book, examples, benchmarks, macro_std, native tests, kolt (with lucide), website and playground. The only 2 are in the Rust tests: `ascription.rs`'s E284 pins, which test this very reading. There are 1,679 tight heads. A170 stayed declined.

I also appended a build record as §16 of `array-lengths.md`.

### Questions for the owner
1. **A literal index in a length-generic body** (§5.3 is ambiguous). I admit it and keep the runtime check, which panics with vilan's message on both backends. Rec: keep that.
2. **Should arrays be Wire?** `impl [type T: Wire; const N] with Wire` can now be written. Rec: wait until someone asks (paper Q13), and fix E296's message either way.
3. **`Eq` for arrays and tuples.** Rec: fix B609 in the solver lane, then add `impl [type T: Eq; _] with Eq {}` (one line).
4. **The five ci `[[bump]]` rows.** They are estimates from instructions:u, not callgrind. Rec: accept them and re-take at the seal.
5. **Merge order.** debug.vl gets one array-Debug hunk from me, and `check_written_nominal_bounds` has a kind check at the top of its loop, which incr-50's M134 anchors may also touch. Rec: merge lang-50 after C3 as planned and resolve those by hand.

No lane processes are running.
