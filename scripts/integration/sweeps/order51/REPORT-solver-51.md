## solver-51 hand-back (Order 51, Opus 5.5)

All ten items are done and the full gates are green. E291 was built because the census came back clean. The B618 probe was answered but not built. Nothing pushed; none of my processes are running.

- **Tip:** `3afe9fd77772465771d242708e4bb74207dc2e46` on branch `solver-51` (worktree `/home/reed/code/vilan-lang/vilan/.claude/worktrees/solver-51`)
- **Base:** C1 `5e17cb59`, rebased onto C2 `9947ec5f` as you asked.
  - Only `CHANGELOG.md` conflicted; both sides kept.
  - Parity check: all 1,506 upstream entries are kept, my entries are added, each with its family marker.

### B607 estate count (first, as asked)
Mixed integer shifts are excluded. The count is **0 everywhere**:
- kolt copy: 0
- the website's `src` (a `cp -r` copy): 0
- the examples (all 11): 0
- `vilan/benchmarks`: 0
- std: 0
- the corpus (145 programs): 0
- the native test programs: 0

So **no kolt patch** was written.

### Commits (oldest first)
1. `9a373b9e` **B607** (breaking). `&`, `|` and `^` over two different integer types now get B579's sentence. Any bitwise operator over a float, shifts included, gets a new sentence: "computes on the bits of an integer, but an operand is `f64`, a float…". The spec's §5.8 now states the rule. Mixed shifts still compute, on both backends.
2. `44d080ff` **B609** (fix), plus std `impl [type T: Eq; _] with Eq {}` and the tuple version `impl type T: (2..: Eq) with Eq {}`.
3. `9e12857e` **M133 solver half** (performance, no bump). Details below.
4. `fc1bf1c4` **B611** (fix). macro_std's `GenericParameter` gains `is_const`, so derives write `const N`. This completes E283's array half, and fixed arrays now count as `Hashable` fields.
5. `23d168d1` **B604** (fix). An annotated `let`, a reassignment, or a tuple/list built over a closure parameter that hasn't been typed yet now waits for it, then checks.
6. `77338f5a` **B552** (fix). A local built from such a parameter (`let d = k * 2`) also waits, so the callee's `U` gets its arguments. **The JS transformer needed no arm**: the corpus is byte-identical, and the filed repro runs natively.
7. `33cc536b` **B608** (diagnostics).
8. `68fee114` B552 follow-up: the pin's program rewritten as a raw string, because the ledger's line-continuation gate flagged it. Test only, no CHANGELOG entry.
9. `89c71229` **E295** (diagnostics). The message now reads "…; `tag` is provided by `impl type T: Leaf with Tag`, and `i32` does not implement `Leaf`".
10. `ccdcc329` **B616** (fix). An array literal inside a list element's tuple, nested list or variant payload is now built as the fixed array its annotation states. Both backends run it.
11. `1ed942d1` **E291** (breaking). In expression position a spaced `<` after a name is a comparison, so `a < b > (c)` is two comparisons. A spaced list followed by `::` or `{` (`List <i32>::new()`) is refused with the tight spelling and read tight. **E284 is retired**: ledger row 705 removed from the TSV and marked retired in the prose ledger. Estate: 0, from lang-50's census re-run on the current trees. The grammar spec's §3.6 states the rule.
12. `3afe9fd7` B604/B552 cost follow-up: the new waits only scan the value when its first read left an unknown type. No CHANGELOG entry (the items are unreleased).

### M133 numbers
- reactive-ui `check`: 1,653.4M → 1,646.6M instructions.
- A165's `Slot` arm now costs 2.23M instead of 3.37M. The rest is `platform_color`/`async_infer`, which is incr-51c's half.
- kolt: computed `impl_bounds_hold` calls fall from 35,031 to 7,565; inclusive cost 210M → 191M under callgrind.
- To check the memo was safe, every served answer was recomputed and compared across the 5,493-test inference suite, kolt, the website, the examples and the corpus. No answer differed.

### Where the items' premises were wrong or incomplete
- **B609:** a tuple whose element bound is the *same* trait as the supertrait impl's already worked. Only a sub-bound failed, and arrays failed even with `const N`. The tuple-family Eq line already worked before the fix.
- **B611:** fixing the binders was not enough on its own. The Hashable derive's field check also rejected every array field (fixed here). Default, Json and Wire derives over array fields fail for a separate reason: std has no array impls of those traits (filed as B?3).
- **B604:** wider than `.map` results. Any receiver typed after the closure body is checked (a call result too) skipped the check, and so did reassignments and tuple/list values.
- **B552:** worse than filed. `|k| { let d = k * 2; d }` recorded **no** `U` at all, so an annotated `let` over the result checked clean.
- **B608:** a file that imports neither trait still reaches std's `Wire`, so its steer names `Wire` only. That is consistent with what B598 does for the method call.
- **E291:** after the change, `pick <f64>(1, 2)` gets three cascaded refusals (filed as E?1).
- **B618 (probe only):** premise confirmed. The consistent answer is that `async e` is always `Task<T>`, by putting `std::task` in the always-loaded set. That is load order and worlds (incr-51c's area), so not XS and not built.

### Gates on the final tip
| Gate | Result |
|---|---|
| `cargo fmt --check` | 0 |
| clippy `-D warnings` | 0 |
| `vilan fmt --check .` | 0 |
| Full suite, `ci-test`, excluding `deep_nesting` | 10,513 / 10,513 passed, 32 skipped |
| `ci_ignored_pins` | 12 / 12 |
| `hygiene` | 3 / 3 |
| `corpus` | 14 / 14 |
| `check_scope_differential` | 15 / 15 |
| Native differential, default mode | 270 / 270 |
| Native differential, sweep mode (`VILAN_NATIVE_DIFFERENTIAL=1`) | 270 / 270 (1 skipped) |
| Deep-nesting canary at 1536 KiB | 18 / 18 |
| `scripts/ci-local.sh perf` | green (growth ×1.93) |

- **Perf against C2 on release builds:** every ceilinged row is between −0.51% and +0.05%. `plain:160` and `plain:320` are +0.33%; they are growth rows only, not ceilings.
- **Late writes:** 0.
- **kolt cold-check RSS** (median of 5): 271.5 MB against 283.5 MB at base, about 4% lower.

### Functions changed in analyzer.rs (no mono.rs or emitter changes)
- **B607:** `finalize_build`
- **B609:** `impl_subject_covers` and `align_subject_binders` (new), used by the conformance walk's supertrait-member search
- **M133:**
  - `impl_bounds_hold` now fronts the memo; the old body is `impl_bounds_hold_computed`
  - new: `open_impl_bounds_memo`, `close_impl_bounds_memo`, `impl_bounds_memo_key`, `ground_key`, `rigid_boundary_scope`, and the struct `ImplBoundsMemo`
  - `resolve_world`: two lines open and close the memo around the fixpoint loop. This sits beside incr-51c's area; only those two lines.
- **B611:** `resolved_type_is_hashable`
- **B604/B552:** `resolve_variable`, `value_awaits_a_closure_parameter`, and the new `ungrounded_binding_initializer`
- **B608:** `traits_reached_at` (new), plus `resolve_world`'s static-accessor refusal
- **E295:** `blanket_static_bound_note` (new)
- **B616:** the list-literal arm of `infer_type_path`, and the new `literal_elaborates_an_array`
- **E291:** removed `spaced_generic_calls` and `with_spaced_generic_reading`

### Files outside analyzer.rs
- **Listed arm in another lane's file:** macros.rs `construct_generic_parameters` now writes `is_const`. Please tell tools-51, since macro_std's `GenericParameter` shape changed.
- **Parser** (`parsing.rs`): `parse_expression_generic_arguments` and `ParseErrorReason::SpacedGenerics`.
- **Formatter** (`formatter.rs`): one arm accepting `SpacedGenerics`.
- **std:** `compare.vl` (the two Eq lines), `reactive/store.vl` (`store_bare_binders`).
- **macro_std:** `meta.vl`.
- **Docs:** spec `types.md` and `grammar.md`, std `traits.md` and `collections.md`.

### Ledger and other proposals-side edits (yours to commit)
- **Ledger:** NEW rows for the B607 float sentence, E295 and E291's `SpacedGenerics`, in both the TSV and `proposals/projects/vilan/proposal/diagnostics-ledger.md`. Row 705 (E284) deleted from the TSV and marked retired in the prose. Ledger tests pass.
- **Finds:** `/home/reed/code/vilan-lang/proposals/scripts/integration/sweeps/order51/newitems51-solver-51.json`, with repros in `sweeps/order51/solver-51/finds/`:
  - **B?1:** std's `Eq` is missing for `bool`, `List`, `Option` and `Result`.
  - **B?2:** `[derive(Hashable)]` refuses generic fields (`T`, `List<T>`).
  - **B?3:** Default, Json and Wire derives fail over array fields; std has no array impls, and the Default generator spells `[i32; 2]::default()`.
  - **F?1 (native):** a generic enum's derived `PartialEq` (`match (self, other)`) is refused with "generic type instantiated at any".
  - **E?1:** after E291, a spaced generic call gets three cascaded refusals and none mentions the spacing.

### Questions for the owner
1. **E291 is breaking and retires E284.** Should the order keep it in v0.49.0 next to B607? Rec: yes. The estate is 0 in every tree, and the formatter already writes every list tight.
2. **B618:** should `async e` always be `Task<T>`, by loading `std::task` with every program? Rec: yes, as an incr-lane item in Order 52, measured as the cost of loading `task.vl` cold.
3. **B?1:** add the four missing std `Eq` lines now? Rec: yes. They are additive one-liners; B609 makes the generic ones conform through the element bound.
4. **E?1:** a single steer at a spaced `<` whose left side is a generic function or type, replacing the cascades? Rec: yes, XS–S, next order.
5. **B?3:** queue array-lengths' second std wave (Default, Json/FromJson and Wire for `[T; N]`)? Rec: yes, one item covering std and the Default generator.

The untracked status file is `solver-51-STATUS.md` in the worktree.
