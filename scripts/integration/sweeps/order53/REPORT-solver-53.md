# REPORT — solver-53 (Order 53, Opus 5.5)

- **Base (C1):** `6fe278caaf5aedd841c7aeb6a7e4a51a0a00aefc` (origin/next)
- **Tip:** `385dfb898e77101793498985f531e4e51f63c4cd` on branch `solver-53` (worktree `vilan/.claude/worktrees/solver-53`). Nothing pushed.
- All seven items done, plus native-53's B?2. std-53's A?1 is taken with B627 (same seam).

## Commits

| sha | item | family |
|---|---|---|
| `4878e13f` | B628: a literal's `None` field takes the parameter another field fixed | fix |
| `af6ea4ea` | B627 (+ std-53's A?1): a method's expectation reaches its receiver call; an undetermined static is refused | fix |
| `f0fd694c` | E319 + E320 (one commit: they share the new field-miss helper) | diagnostics |
| `8a56789d` | F141: an assignment through `Shared::read()` is refused | diagnostics |
| `11f4919e` | B626: a module scalar read only through a view is declared on JS | miscompile |
| `c816c1d1` | M147 (1): a bound selection asks admission only of the impls that can answer it | performance |
| `e9c08894` | native-53's B?2: a lent place's root re-bound by a later argument is refused | diagnostics |
| `385dfb89` | Ledger index rows (`diagnostics-ledger.tsv`) for B627/E320/F141/B?2; the E319/E320 pin heads as raw literals. No CHANGELOG entry (it completes the four items above). | — |

Each item commit carries its `## Unreleased` entry with a family marker. My entries sit together at the end of the section, after a `---`.

## Where the premises were wrong

- **B628:** the item thought a literal argument was "left unresolved". It was OVERWRITTEN: `reconcile_type`'s bound-generic arm appended a `T := T` self-map after recursing on the context's `T := str` (the `None` types as `Option<T>` against the field's `Option<T>`), and the literal folds bindings in order. Swapping the two fields compiled. Fix: no self-map is appended after the recursion.
- **B627:** as stated. Two additions the item did not foresee:
  - an `external` member's own return-only generic (`to_array<const N>`) was never recorded from an expectation, so A?1's `xs.to_array().unwrap()` needed `record_external_return_generics`;
  - the "never fully determined" refusal had to follow where the value lands. A broader first version refused the corpus's `Signal::new(HashMap::new())` and kolt's `Shared::new(HashMap::new())` field.
- **B626:** wrong. The analyzer's `reference_count` for `LIMIT` was already 1 (I checked by instrumenting). The binding was dropped at ASSEMBLY by the module-binding tree-shake (F6, `referenced_globals`): `transformer.rs`'s `scalar_view_of_place` names a boxed scalar's cell without recording the reference. The fix is one line in the emitter (a listed arm), not in the analyzer core.
- **M147 (1):** wrong in its main remedy. The per-(subject type, member, bound) memo already exists on `Program` (M97's `bound_selection_memo`), and both calls already share it. `bounds::a_refinement_after_the_passes_computes_no_selection_the_passes_already_made` pins exactly that; kolt's client makes 406 selections, none twice.
  - The real cost was filter ORDER: `ImplAdmission::admits_impl` ran over every impl for every selection (175,122 calls, 18 M) ahead of M103's member filter.
  - The program-wide scans cannot be shared between the two calls: the context pass rewrites the program between them, and each refines over its own call graph (before vs after the rewrite). They are now one `RefineIndex::build` per call.
- **E319 / E320 / F141:** as stated.
  - E320's static case (`p.origin`) needs a direct lookup, because a static is no method candidate of a receiver.
  - E119's twin note now takes a `TwinMember` kind: a field miss asks the other twin for a FIELD only, a method miss for a method.
- **B?2 (native-53):** as stated, scoped to the RE-BIND. The in-place twin (rustc E0499) is filed as my B?3.

## Gates (final tip `385dfb89`)

- **Full suite:** `--cargo-profile ci-test -E 'not binary(deep_nesting)' -j 6`: **10,672 run, 10,672 passed**, 37 skipped. This includes `ci_ignored_pins`, `hygiene`, `corpus` (goldens byte-identical, none regenerated), `check_scope_differential`, `diagnostics_ledger`, the vilan-lsp binary and `native_differential` in default mode. The first full run had 2 `diagnostics_ledger` failures (missing TSV rows; a nested-indent literal read as a lost continuation); `385dfb89` fixed both.
- **Native differential, sweep mode** (`VILAN_NATIVE_DIFFERENTIAL=1`): **288/288**.
- **Deep-nesting canary** (1536 KiB, dev profile): **18/18**.
- **Clippy** (`-D warnings`): clean. **`cargo fmt --check`:** clean. **`vilan fmt --check .`:** clean.
- **`scripts/ci-local.sh perf`:** T2 green; growth x1.931.
  - Against the `reference` ceilings, every subject is within its limit, at x0.968–x0.989 (math 250.4 M / 253.3 M, watch 312.4 M / 316.5 M, todo 4,145 M / 4,210 M, genapp:46 7,627 M / 7,759 M).
  - std is not grown, so no `[[bump]]` rows.
- **kolt's client check** (`check src/client.vl`, release, `instructions:u`, steady state): base C1 8,026.8 M → tip 8,027.5 M (+0.009 %).
  - An intermediate tip read +42.5 M. Callgrind diffs traced it to B627's bound check running `infer_type` for every bare static call, and to B?2's scan sorting every call. Both were reordered cheap-first and folded into their commits.
- **kolt cold check RSS** (`rss-probe.py`, 5 runs, `MALLOC_ARENA_MAX=1` on both sides): base 276,324 KB → tip 274,536 KB median. The box was loaded (load average 2.4–9); instructions are the measure.
- **M147, callgrind inclusive on kolt's client** (profiling builds): `dispatch_refine::refined_edges` 107.9 M → 92.0 M.
- **The edit-replay and id-window differentials:** green inside the suite. No drain, prefix or `const_cache` code was touched.
- `ci-local.sh windows` was not needed: no platform-gated code.

## Functions changed

- **`analyzer.rs`**
  - Changed: `reconcile_type`; `resolve_method_call` (the `Found` arm); `infer_type_path` (the external-callee arm); `check_generic_bound_satisfaction_declarations` (B403's block); the residual sweep in `finalize_build`; `note_spaced_generic_call`; `names_something_generic`; `resolve_field_accessor` (the struct arm's refusal); `overlaid_std_type_note`, `twin_declaring_member` and `declares_member_on` (`TwinMember`); `check_assignment_places`; the checks list (adds `check_lent_root_rebinds`).
  - New: `receiver_directed_by_expectation`, `record_external_return_generics`, `undetermined_value_flows_on`, `settled_type_carries`, `refuse_missing_struct_field`, `written_method_call`, `spine_rooted_at_a_read`, `refuse_write_through_read`, `check_lent_root_rebinds`, `place_root_binding`, `rebind_of_within`, `binding_is_closure_captured`, `refuse_lent_root_rebind`.
  - New field: `Analyzer::swept_residual_generics`. It is transient (cleared and filled per analysis) and is not a record.
- **`transformer.rs`** (emitter, listed arm for B626): `scalar_view_of_place`.
- **`dispatch_refine.rs`:** `impl_members_for_bound_uncached` (filter order), `refined_edges_timed` (new `RefineIndex`), new counter `bound_selection_admission_tests`.
- **`mono.rs`:** untouched.
- **Ownership:** nothing in `incremental.rs`, `lib.rs`'s drivers, the drain or `const_cache.rs`.

## Pins (each proven red before its fix)

- **`generics`:** `b628_*` (3), `b627_*` (4).
- **`ascription`:** `e319_*` (2), `e320_*` (2).
- **`borrows`:** `f141_*` (2), `b626_*` (1), `a_lent_places_root_rebound_by_a_later_argument_is_refused`, `a_settled_value_or_a_captured_root_still_compiles`.
- **`bounds`:** `m147_a_bound_selection_asks_admission_only_of_the_impls_that_can_answer_it` (red at 317/317 with the old order).
- **`native_differential`:**
  - `b628_*` → `native/literal_none_field.vl`
  - `b627_*` → `native/expected_type_through_a_receiver.vl`
  - `b626_*` → `native/module_scalar_view.vl`

## Ledger and estate

- **Estate, counted first:** kolt (copy), the website (copy), the 11 examples and the corpus all check clean at the tip. F141's, B?2's and B627's refusals each have 0 sites, so nothing is breaking.
- **`proposal/diagnostics-ledger.md`** (the integrator commits it): four NEW rows (B627, E320, F141, B?2) appended. Row 821 (E309) is amended for E319's member form.
- **`crates/vilan-cli/tests/diagnostics-ledger.tsv`:** four NEW rows.

## Finds filed

`sweeps/order53/newitems53-solver-53.json`, repros in `sweeps/order53/solver-53/finds/`. Placeholders are per file; my B?2 is not native-53's.

1. **B?1:** B627 residue. An argument at a NON-generic parameter (`take(make().unwrap_or(5))`) has no expectation to hand down, so it is still refused "cannot infer".
2. **B?2:** a literal no field grounds, settled only by a later annotated binding, runs on JS and is refused natively. Same on v0.50.0.
3. **B?3:** the in-place twin of native-53's B?2. `log.items.push({ log.items.push(1); 9 })`: JS prints 2, rustc E0499.
4. **B?4:** B627 residue. An undetermined static as an unannotated function's tail is still an internal error on JS.

std-53's A?1 is fixed by `af6ea4ea`; please allocate its id and close it with B627.

## Questions for the owner

1. **F141's scope.** Should any assignment into a field of a call returning a VALUE (`make().count = 3`) be refused the same way? **Rec:** yes, in a later order, with the estate counted first. It is the same lost-write rule.
2. **B?3.** Should `check_lent_root_rebinds` widen to in-place writes of the lent place? **Rec:** yes, next order. Same §6.4 rule 4 and same steer; rustc refuses it today as a "backend defect".
3. **B627's refusal positions.** Should the walk continue through an inferred function's tail into its call sites? **Rec:** yes, as B?4 (XS-S).
4. **M147's remainder.** `refined_edges`' self-cost (~57 M) is per-call program scans that cannot be shared across the context rewrite. **Rec:** leave it. If more is wanted, index impls by member name once per program, which would take most of the remaining ~20 M of selection work.
