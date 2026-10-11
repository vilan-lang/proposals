## solver-50 hand-back (Order 50, Opus 5.5)

**Tip `98ef881d`** on branch `solver-50`. Nothing pushed. **Base `4b19da3b`** (origin/next after debug-50 merged). I launched at C1 `7b0c238f`, rebased onto C2 `f99dc28e` after B601 as you asked, then onto `4b19da3b` before hand-back. Both rebases conflicted only in CHANGELOG. Every family marker survived; `cut-release.sh --out` dry-run classifies all 12 entries. Worktree: `.claude/worktrees/solver-50`. `LANE-STATUS.md` is untracked. None of my processes are running.

### Commits (12; one item each, each with its CHANGELOG entry)
| sha | item | family |
|---|---|---|
| 271d929c | B596: a struct literal runs its fields in written order on JS | miscompile |
| 9b47340a | B599: fill-from-use | feature |
| 1d00ec2c | B602: `f64 * i32` refused (v0.48.0) | breaking |
| 94ff0cb2 | B598: a trait the calling file doesn't reach is no candidate at its call | fix |
| 6fc7911a | B600: a hole no binding holds is refused at the call | diagnostics |
| 77e08903 | B601: the dyn narrowing is reported once | diagnostics |
| 219c5d40 | B592: `List<[T; n]>` directs inner array literals | fix |
| a43c3625 | B593: function items in a list take their closure type | fix |
| 622a3b45 | B595: a blanket's static on a concrete head binds the blanket's `T` | fix |
| 49e02691 | E289: the element-hole message names `Option` | diagnostics |
| b6af11e2 | E290: tuple view refusals say "the tuple's slot", not "payload" | diagnostics |
| 98ef881d | E287 halves (c) and (d) only | diagnostics |

**M133: measured, not built.** Details are under "Not done" below.

### Where the items' premises were wrong
- **B599:** it is not a bare-trait-parameter gap. No argument ever filled a hole, even at a concrete parameter (`let o = None; take(o)` with `take(o: Option<str>)` was refused). The receiver side only worked for `push`.
  - There was also a root cause underneath: substitution re-minted holes on every ask. So the hole in `Cell::new(None)`'s binding was never the slot a later use filled.
  - The fix has three parts: an argument fills its own holes, a method call fills its receiver's holes, and holes keep one identity (minted once per `None`/empty-list site, and a generic bound to a fixed value is that value, not a copy).
- **B602:** `+`, the comparisons and `==` already refused float/integer pairs. Only `-`, `*`, `/`, `%` let them through, and `f64` against `f32` too.
  - An integer literal, or a `let` bound to one, takes the float's type, so `1 / 4.0` stays legal.
  - A fractional literal beside a typed integer (`2.5 * count`) is now refused. It failed the native build (rustc E0277), so it is in scope.
- **B601:** the readiness probe and the directed ask were not the cause. Typing a reference re-types the binding it names under the same constraint, so the binding's own entity reported a second time.
- **B593:** `[double, triple]` had no element type at all, not just uncallable elements. I fixed it by coercing function items to their closure type inside the list literal.
- **E287:** halves (a) (a name in the length position, a parser change) and (b) (the substituted length 0) are lang-50's ground: array-lengths S1 and S4 turn the length into a type. I left them there.

### Gates (on the final rebased tip)
- Full suite (`--cargo-profile ci-test -E 'not binary(deep_nesting)' -j 6`): **10229/10229**. Within it:
  - inference 5428
  - check_scope_differential 15
  - native_differential 254
  - corpus 13 (no golden moved)
  - ci_ignored_pins 12
  - hygiene 3
  - diagnostics_ledger 25
  - docs 12
- Native differential in sweep mode (`VILAN_NATIVE_DIFFERENTIAL=1`): **254/254**.
- `cargo clippy --workspace --all-targets -- -D warnings`: clean. `cargo fmt --check`: clean. `vilan fmt --check .`: clean.
- `scripts/ci-local.sh perf`: T2 green, growth x1.931.
  - This box is the reference 9800X3D, so I also gated against the reference ceilings: every row ok, x0.93–x0.98 of ceiling.
  - Tip against base `f99dc28e` in instructions: x1.0008 to x1.0043. Worst rows are rpc x1.0043, fullstack x1.0034, browser x1.0032. No bump row added.
  - Two fixes cut my own cost from about +0.6%: B600 now records only user-file operands and builds its lookup maps only when a candidate exists, and the per-argument clones are gone.
- Late writes: 0 (math and kolt counters).
- Kolt cold-check peak RSS: base 263,364 KB, tip 263,284 KB (flat).

### B602 estate, by location
| location | sites |
|---|---|
| kolt copy (with `src/lucide` + `src/search-dict`) | 0 |
| website `src` | 0 |
| examples (11) | 0 |
| std | 0 |
| corpus `vilan/test` | 0 |
| book fences (docs gate) | 0 |
| `vilan/benchmarks` | 5, fixed in the B602 commit with `.as_f64()` (realtime.vl:159, report.vl:20, throughput.vl:96/112/131) |

So there is no kolt or website patch for B602. Kolt, the website and the examples also check clean under B600 and the rest of the tip.

One optional kolt patch for B599: `sweeps/order50/solver-50/kolt-b599-optional-annotation.patch` drops the annotation at `src/sidebar.vl:65`. Verified clean under the tip; not applied.

### Functions changed (analyzer.rs and the emitter; mono.rs and impl_select.rs not touched)
- **transformer.rs** `walk_entity_inner`, struct-literal arm (B596).
- **analyzer.rs:**
  - **B599:** new `fill_holes_from_use`, `type_value_mentions_any`, `stable_variant_use_holes`, field `variant_use_holes`. Changed `infer_type_path` (Local arm), `substitute_type` (Generic arm), `resolve_call_subject` (argument loop), `resolve_method_call` (receiver), `resolve_method_arg_check`.
  - **B602:** `finalize_build` (B579's arm), new `adapts_to_a_float_peer`.
  - **B598:** `resolve_method_call` (ambiguous-traits case), new `trait_reach_by_file`, `impl_member_providing_files`, `candidates_reached_at`, field `entry_scope_id` (set in `analyze_inner`); `check_trait_method_scope` refactored onto the shared reach helper.
  - **B600:** new `refuse_expression_holes` (runs inside B580's sweep), `record_hole_operand`, `call_leaves_a_generic_open`, `call_result_carries_an_open_generic`, field `hole_operands`; records added in the three call resolvers.
  - **B601:** `refuse_dyn_narrowing`.
  - **B592, B593:** `infer_type_path`, list-literal arm.
  - **B595:** `resolve_world`, static-accessor arm.
  - **E289:** `element_hole_refusal`.
  - **E290:** `capture_write_refusal`, `check_mut_captures_under_view_subjects`, new enum `TupleLeaf`.
  - **E287:** `array_length_literal`, `resolve_subscript`.
- **Ledger:** 3 new rows (two for B600, one for E287). Keys reworded for rows 669 (E289) and 633, 634, 658, 659 (E290).
- **Other files:** spec `types.md` (B599). One existing native pin rewritten: `a_refusal_inside_another_files_body_names_where_to_look`. Its std probe (`Option::None.is_some()`) is now refused at `vilan check` by B600.
- **New native probes:** `struct_literal_written_order.vl`, `fill_from_use.vl`, `float_integer_operands.vl`, `list_of_fixed_arrays.vl`, `listed_function_items.vl`, `blanket_static_heads.vl`.
- B596, B598, B601 and B600's pins were each shown to fail with the fix disabled.

### Not done: M133
On reactive-ui, the Slot blankets' remaining cost sits in method resolution: `impl_member_candidates` → `impl_bounds_hold` → `bind_subject_bound_binders` → `trait_args_providers_for_pattern` (about 28–46M Ir inclusive of 1.69G), plus incr's post passes (`platform_color::reachable_bindings` 62M, `callee_substitution` 32M). The bound-proof check after inference is already cached per type (M123), so door (a) has nothing left there. The remaining work is a memo inside method resolution, or post-pass work in incr's files. I did not want to rush a cache whose key has to respect B401 admission and M121's reach record.

### Finds filed (`newitems50-solver.json`; repros under `sweeps/order50/solver-50/finds/`)
- **B607:** `&`, `|`, `^` over two integer types, and any bitwise operator on a float, check clean; the native build refuses.
- **B608:** B598's static twin. `List::describe([1, 2])`'s refusal steers to `Wire`, a trait the file never imports.
- **E295:** `i32::tag(1)`, where the blanket's bound doesn't admit `i32`, says only "cannot find 'tag' in i32".
- **N167:** the native "construct is in X's body" note has no reachable std probe after B600.

### Questions for the owner
1. **Should the two B600 refusals ride v0.48.0 as diagnostics or as breaking?** They refuse programs that ran on JS, but each was already a native build failure. Estate is 0. Rec: diagnostics, noted beside B602 in the release notes.
2. **Do E287 (a) and (b) move to lang-50 (array-lengths S1/S4) and E287 stay open?** Rec: yes. The parser's length grammar and `Type::Array`'s length are theirs now.
3. **Who builds M133 and when?** Rec: Order 51, split between a solver memo of `impl_bounds_hold` per (impl, ground receiver), keyed by the impl count and B401's declined set, and an incr pass narrowing `platform_color`'s dispatch walk by the bound's head. Measure with `VILAN_STD` variants as M131 did.
4. **Should B607 be refused at v0.48.0 alongside B602?** Rec: refuse the mixed pairs under `&`, `|`, `^` and floats under any bitwise operator, after counting the estate. Leave mixed integer shifts legal, as in Rust.
5. **Should B599 extend to unify-only positions (an `if` arm's `None` beside `Some(1)`, a reassignment's weaker side)?** Rec: no, not without a measured need. Those positions don't strand a hole today; B600's refusal now catches the case that did.
