solver-c-46: final report. The tool refused the REPORT file, so the full text is below; please save it as `sweeps/order46/REPORT-solver-c-46.md`. New finds are in `proposals/scripts/integration/sweeps/order46/newitems46-solver-c.json`.

**Branch tip: `solver-c-46` @ c65e309f** (base `origin/next` @c7c1e3bc). Six commits, nothing pushed.
- B495 S0, mechanical: 6b01a09c. B495 itself: c7bed73c, plus follow-up c65e309f.
- B509 S1 + B528: f3533645. B509 S2 + M109: be1b05a5.
- B538: e0c7a8fe.
- Every gate is green except the known hygiene red, which is not this lane's.
- Nothing needs the owner's ruling. One thing to confirm, at the end.

---

# solver-c-46: Order 46 report

Branch tip `solver-c-46` @ c65e309f, on `origin/next` @c7c1e3bc (which holds solver-b-46). Worktree `vilan/.claude/worktrees/solver-c-46`; `LANE-STATUS.md` (untracked) lists the shas. Every gate below ran on the tip.

## Per step

| # | item | status | sha |
|---|---|---|---|
| 1 | B495 S0: `Type::Closure` gains a fourth slot (mechanical) | DONE. Every gate byte-identical; corpus + inference 5130/5130 on that commit. | 6b01a09c |
| 1 | B495 S1–S3: modes in the type, adoption inside unification, the refusal, both emitters read the type, printers | DONE | c7bed73c |
| 1 | B495 follow-up: two literals that become one value adopt together. Found after S1; it was a silent wrong value. | DONE | c65e309f |
| 2 | B509 S1 + B528: a view subject binds payload views; Q4 refusal; rule 4 to the last use; the steers | DONE | f3533645 |
| 2 | B509 S2 + M109: std's `Option` steps and the derive's single-payload step write in place; copy-count pin | DONE | be1b05a5 |
| 3 | B538: tuple assignment targets, both backends | DONE | e0c7a8fe |

For the sweep, these can close:
- B495, B527, F69, B509, B528, B538.
- B534 in full: its third position is closed here; solver-b-46 closed the other two.
- M109 in part. The single-payload write-back is gone. The multi-payload step keeps its copy (Q6), and its dead write-back clone remains.

### 1. B495 (closure-type-views.md, RULED Q1–Q5)

**Representation.**
- `type_.rs` gains `Mode { Value, View, MutView }` and `ParameterMode { Written(Mode), Open(Id) }`. The type is now `Type::Closure(params, ret, contexts, modes)`.
- One refinement of the paper's `Vec<Option<Mode>>`, not a ruling change: the open slot names the literal's parameter (`Open(parameter_id)`). Adoption inside unification has to know which literal adopts, and the type has no other link back to it.
- An empty modes vector means "unstated". These are the analyzer's synthesized expectations (`|T| U` for an element walk), and they constrain no mode.

**Where modes come from.**
- The walk writes `Written` for every parameter of a written closure type.
- A literal's type carries `Written` where the parameter spells a type or a view (`|c: str|`, `|c: &str|`, `|&mut list|`), and `Open(id)` where it is bare.
- A named function's, a `Callable`'s and a variant constructor's coerced closure type carry their declared conventions.

**Adoption (Q3).** It happens where the two types meet:
- in `reconcile_type`'s closure arm (`reconcile_parameter_modes`);
- in the closure literal's inference arm, against its expectation. This goes through the active substitution when the expectation is a generic bound to a closure type (`List<|&mut T| void>::push`, `hold<T>`).

Details:
- An adopted view sets the parameter's `convention`, which is what the emitters and checks read.
- An adopted value is remembered in `adopted_parameter_modes`, so a second, different mode is refused.
- An untyped bare parameter also takes the position's parameter type at the reconcile (B13's channel at the binding). Without it, v1's `*c` read an aggregate.
- Two open parameters of different literals that meet are linked, so both adopt. That is the follow-up commit (`if c { |x| .. } else { |y| .. }` bound and re-typed).
- Nothing adopts after the constraint fixpoint (`types_settled`). No slot is written late: the inference suite runs with M108's debug assert and is green.

**Refusal (Q2/Q4).**
- Modes take part in `Type`'s derived `Eq`/`Hash`, in `compare_type_rigid` and in `same_type_structure`. Two different written modes do not reconcile.
- One `NEW` diagnostic row, raised through `type_mismatch_message` so every mismatch site uses it: "this closure takes `str` by value where its type takes a view `&str`: a value closure and a view closure are different types, and no adapter is inserted; … adapt the value closure with one that copies the view's value out: `|c| f(*c)`".
- It has variants for the reverse direction, for `&mut`, for `&` against `&mut`, and "this closure's parameter N" when there are several parameters.
- Quick-fix data was not built (filed as E?1).
- Impl identity (`same_impl_type`) still ignores modes, as it ignores clauses.

**Deleted and replaced.**
- Gone: the side table `closure_type_parameter_views` (Analyzer and Program), the post-inference pass `adopt_closure_parameter_views`, and `callee_parameter_type_ids`.
- `closure_callee_views` now reads the callee's type.
- Natively, the four side-table reads now read the type (`Program::parameter_mode`, `Program::closure_parameter_views`).
- native-46's F69/F77 stopgaps are retired: `None if already_a_reference` in `closure_call_arguments`, and `positioned_closure_carries_views`. Their pins stay green.

**Q2 estate count.** This is the breaking edge: a written mode meeting a different written mode. The count is **0** everywhere:

| where | how checked | result |
|---|---|---|
| std | every std gate | 0 |
| corpus | corpus gate | 0 |
| examples | 11 `vilan check`s | 0 |
| docs | fence gate | 0 |
| kolt | `vilan check` on a scratch copy | 0; output clean and identical to the base |

So it ships as a refusal, not as Q2's one-release warning.

Grep census at the base:

| shape | std | corpus | examples | docs | kolt |
|---|--:|--:|--:|--:|--:|
| annotated `let` of a view closure type | 0 | 0 | 0 | 0 | 0 |
| view closure type in a type position | 61 | 15 | 0 | 22 | 0 |

Kolt's three `update(|&mut ..|)` literals spell the same mode as their positions, so they are unaffected.

**Pins.** Each was red on the base binary, run before the build.
- `inference::borrows`:
  - `b495_a_literal_adopts_its_positions_views_through_a_let_and_a_generic_identity`
  - `b495_two_literals_bound_as_one_value_adopt_its_mode_together`
  - `b495_a_literal_nested_in_a_written_view_closure_type_adopts_its_views` (Option, List, `Holder<T>`, `List::push`, which is B534's third position)
  - `b495_a_value_closure_and_a_view_closure_are_different_types` (five refusals)
  - `b495_a_closure_types_modes_print_with_the_type`
- `native_differential::a_closure_literal_takes_its_positions_parameter_modes_on_both_backends` (`native/closure_parameter_modes.vl`)

### 2. B509 (payload-views.md, RULED Q1–Q7) + B528 + M109

**S1: a view subject binds payload views.** `compute_wrapped_view_captures` learns a third subject kind: a `Reference` over an enum place (`match &mut held`, `&held is ..`, including a view-parameter subject). Every `let` capture reached through variant payloads, nested variants included, is a view of the subject's mode. `Program::payload_view_captures: HashMap<Id, bool>` carries them to the emitters.
- **JS:**
  - An aggregate payload binds the slot's own reference, with no clone (`binding_or_param_is_view` already skips views).
  - A scalar payload binds the `(enum, slot)` pair. For a generic payload this is decided per instance (`binding_holds_a_scalar_view_pair`), on both the `match` path and the `is` alias path.
- **Native:**
  - The backend already emitted `match &mut held { Some(p) => .. }` with Rust's binding modes.
  - `names_a_mutable_loan` now knows a `&mut` payload capture, so it is reborrowed at a `&mut` position. Before, `f(p0)` emitted `&mut p0` (rustc E0596); it showed up the first time the derive wrote in place.

**Q4.** A `mut` capture under a view subject is refused (`NEW` row): "`mut p` would bind a COPY of the payload, but this matches a view (`&mut held`), whose captures are views into the payload: bind `let p` to write the payload in place, and write `*p` where a copy is wanted".

**Q3/Q5, rule 4.**
- solver-b-46's `compute_view_anchors` and `compute_view_origins` now take the payload captures. The subject's place is the origin, anchored exactly; a view-parameter subject forwards its own anchors.
- `subject_view_roots` reads a `Reference` leaf.
- A match capture (payload or wrapped) and an `is` capture are live from the arm's start to their last use:
  - the scan counts each capture's uses in its arm (`binding_use_count`) and drops it from the live set when it passes the last one;
  - a use inside a loop or a closure in the arm keeps the capture live for the whole arm.
- Refused while the capture is still to be used:
  - `held = None`;
  - `outer.held = None` (a part reassignment);
  - `reset(&mut outer.held)`;
  - `n = None` under `&mut n is Some(let v)`.
- Legal: `let next = P { x = p.x + 1 }; held = Some(next);`.

**B528.**
- A write through a copy capture says so (`NEW` row): "cannot mutate 'p': it is a COPY of the payload the pattern takes out of `held`, so a write to it (or to `mut p`) would not reach `held` — to write the payload in place, match a view of it, `match &mut held` (or `&mut held is ..`), whose `let` captures are writable views".
- A write through a readonly payload view says so (`NEW` row): "cannot write through 'p': this matches `&held`, a readonly view … match `&mut held`".
- A whole rebind of an `is` capture keeps the old wording, because B222/B237's guard continuation is an ordinary local. That leaves the scalar trap `if held is Some(let v) { v += 1 }`, filed as B?1.

**S2: std writes in place.**
- `Store<Option<P>>::some()`, `StoreSome<Option<P>>::some()` and the derive's single-payload step are now `match &mut held { V(let p0) => f(p0), .. }`.
- The multi-payload step keeps its copy (Q6).
- The A142 store pins (inference `store::`, native `a142_s7_*`) are green and unchanged.

**The cost, counted not timed** (`b509_a_through_variant_write_copies_nothing`). The pin instruments the emitted `__clone` and counts every call over the paper's probe: 2,000 writes of one scalar inside a payload holding a 10,000-element list.
- The in-place shapes make **0** copies.
- The old shapes (the control) make at least 4,000 calls.
- Through std's own handles (`online().since().patch(n)` on a derived enum, and `some().since().patch(n)`), 199 more writes add only the written leaves.
- On the base std, **ONE write made 20,034 `__clone` calls**. I measured this by planting the old `store.vl` back, and the pin went red.
- For information: the old b7 spelling still takes 337 ms here. std no longer uses it.

**Pins.**
- `inference::borrows`:
  - `b509_a_view_subject_binds_its_payload_captures_as_views` (aggregate fields, whole payload, view-parameter subject, scalar, `is`, several payloads, a nested variant, read views)
  - `b509_a_payload_view_in_a_generic_body_writes_through_at_every_instance` (`i32`, a struct, `str`)
  - `b509_a_mut_capture_under_a_view_subject_is_refused` (`&mut` and `&`, once each)
  - `b509_rule_4_guards_the_subject_until_the_captures_last_use` (five refusals, one legal last use)
  - `b528_a_write_to_a_copy_or_readonly_capture_steers_to_the_view_subject`
  - `b509_a_through_variant_write_copies_nothing`
- `native_differential::a_payload_view_writes_the_enum_in_place_on_both_backends` (`native/payload_views.vl`)

**A breaking edge the paper did not list.** Under `match &place` a capture is now a readonly view, so a scalar payload read as a value needs `*v`, as a loop view's does.
- The estate has no `match &` or `match &mut` subject: 0 at the base in std, the corpus, the examples, the docs' fences and kolt.
- The docs had three prose mentions of `match &slot` for resource loans; views agree with them.
- It is marked in the BREAKING entry.

**Not taken.** A capture inside a tuple sub-pattern under a view subject stays a copy, and `mut` there is not refused. This is the B528 trap one pattern level down, filed as B?2.

### 3. B538

- **JS:** a tuple target that a destructuring pattern cannot spell (an element, a nested tuple, a tuple-typed element) becomes the value in a temporary plus one ordinary write per leaf at its flat offset:
  - an element goes through `__at_put`;
  - a tuple-typed leaf comes from a `slice`;
  - a multi-slot tuple position is written slot by slot.
- A tuple of plain places keeps its destructuring, so `(a, b) = (b, a)` is byte-identical and no golden moved.
- **Native:** `mutable_place` now renders a tuple target element by element as places. The tuple-typed binding had been read through rule 1's `.clone()` (E0070). Nested targets already built.
- **Pins:** `inference::tuples::b538_a_tuple_target_of_elements_nested_tuples_and_tuple_typed_places_assigns_each` and `native_differential::a_tuple_target_of_places_assigns_each_on_both_backends` (`native/tuple_assignment_targets.vl`). Both were red on the base; JS threw at load.

## Probes, base and tip, both backends run

The native rows were built and run (`vilan run --backend rust`), not read.

| probe | JS before (base c7c1e3bc) | native before | JS after (tip) | native after |
|---|---|---|---|---|
| v1 let re-typed | `out=Oslo,0` (miscompile) | refused, "an unresolved type" | `out=Oslo` | `out=Oslo` |
| v2 value ↔ view | refused, but for the wrong reason (a mis-adoption made the by-value closure's body fail "a view can't be read as a value") | same | refused both ways with the B495 row | same |
| v3 generic identity | `out=Bergen,0` (miscompile) | rustc E0599/E0308 | `out=Bergen` | `out=Bergen` |
| v4 bare literal in `Option`/`List` | refused, "cannot mutate immutable 'x'" | same | 11 / 111 | 11 / 111 |
| v5 generic struct field | 6 | 6 (via native-46's stopgap) | 6 | 6 (reads the type) |
| v6 control | right | right | right | right |
| v7 annotated `let`, `&mut` | 101 (B516 had fixed it) | 101 | 101 | 101 |
| v7b annotated `let`, read | `Oslo` (B516) | `Oslo` | `Oslo` | `Oslo` |
| v8 spelled view, capture/loop | 11 / 111 | 11 / 111 (stopgap) | 11 / 111 | 11 / 111 (reads the type) |
| v9 controls | right | right | right | right |
| b1(1) bare `Some(mut p)` | copy, `held.x=1` | copy, `held.x=1` | unchanged (Q2 keeps the copy) | unchanged |
| b2 `match &mut held` + `let p` | refused, "declare it mut" | same | `held.x=2` | `held.x=2` |
| b3 / b3b `Some(&mut p)` | parse error | same | unchanged (door B not taken) | unchanged |
| b4 wrapped view, `for &mut` | 7, 8 | 7, 8 | 7, 8 | 7, 8 |
| b5 `some_mut` through a bare match | refused (escape) | same | unchanged | unchanged |
| b8 loop precedent | refused | refused | refused | refused |
| b9 wrapped capture, subject written | refused (solver-b-46's B529) | refused | refused | refused |
| b10 `match &held`, read | `x=1` | `x=1` | `x=1` (now a readonly view) | `x=1` |
| b11 liveness | legal | legal | legal | legal |
| b12 bare match on a view parameter, write | refused, "declare it mut" | same | refused with B528's COPY steer | same |
| b12b `match &mut` on a view parameter, read | `p.x=1` | `p.x=1` | `p.x=1` | `p.x=1` |

## Hover and printer

A closure type prints its modes wherever it prints: `|&str, &mut i32, bool| void`. That covers:
- the analyzer's `pretty_print_type`;
- hover and inlay-hint labels (`hint_labels`);
- `contract_hash`'s render. A closure cannot reach a service surface, so no contract hash moves.

A literal's open parameter prints the mode it adopted, and prints as by-value until it adopts.

## Goldens, censuses, ledger

- **Goldens:** no corpus golden moved; corpus was 13/13 at every step.
- **Censuses:** the copy-elision census is unchanged. The native leak and copy censuses ran green inside `native_differential` in both modes.
- **Ledger:** four `NEW` rows — B495's mode refusal, B509's `mut`-capture refusal, and B528's copy-capture and readonly-view refusals.
- **CHANGELOG (`## Unreleased`):** six entries, each with its family marker:
  - B495: `miscompile`, and `breaking` for the mode-in-equality refusal;
  - B509: `feature`, and `breaking` for the `mut`-capture refusal and the readonly-view read;
  - B509 S2: `fix`;
  - B538: `miscompile`.
- **Docs:** `spec/memory.md` (closure-type modes; matching by view and its rule-4 range) and `tour/memory-model.md` (a `match &mut` / `is` example, run).
- **Expr-walk frame:** not touched; no arm or local was added to `walk_expr_node_inner`. `deep_nesting` passes at `VILAN_CANARY_STACK_KIB=1536`.

## Gates on the tip (c65e309f)

| gate | result |
|---|---|
| `cargo nextest run --workspace -j 6` | 9570 run, 9569 passed. The 1 failure is `hygiene::no_tracked_file_contains_an_absolute_home_path`, the known red, from `editors/vscode/src/test/menu.test.ts:27` (not this lane's). |
| `native_differential` with `VILAN_NATIVE_DIFFERENTIAL=1` | 159/159 |
| `deep_nesting` at `VILAN_CANARY_STACK_KIB=1536` | 18/18 |
| `cargo clippy --workspace --all-targets -D warnings` | clean |
| `cargo fmt --check` | clean |
| `scripts/ci-local.sh vilan-fmt` | green |
| `scripts/ci-local.sh perf` | T2 verdict green. Growth, plain 160 → 320 modules: x1.941 (limit x2.3). Class `local` has no ceilings, so counts are reported, not enforced. |

## Instructions on kolt `vilan check`

Measured with `scripts/perf_count.py`: release binaries, the same scratch copy of kolt, warm, third of three runs each. The machine was shared (load 14–16).

| binary | instructions:u | peak RSS |
|---|--:|--:|
| base c7c1e3bc | 24,398,620,992 | 283.4 MB |
| tip c65e309f | 24,475,115,786 | 289.7 MB |
| change | **+0.31%** | +2.2% |

- Kolt on the tip checks clean (0 errors, 0 warnings), identical to the base.
- Where the cost comes from: four new whole-program scans for payload captures, the modes vector on every closure type, and the per-capture use counts.

## Internals changed (reactive-46, store-46 and layout-46 rebase onto this)

**type_.rs**
- New `Mode` and `ParameterMode`.
- `Type::Closure` now has four fields. Every new match site needs the fourth (`_`), and a constructed closure type must state its modes; use `Vec::new()` only for a synthesized expectation.

**analyzer.rs, new**
- Free function `convention_mode`.
- B495 methods: `resolved_parameter_mode`, `adopt_parameter_mode`, `reconcile_parameter_modes`, `parameter_modes_compatible`, `function_parameter_modes`, `closure_literal_modes`, `fill_open_parameter_type`, `link_open_parameters`, `closure_mode_mismatch_message`.
- B495 state: fields `adopted_parameter_modes` and `open_parameter_links`; `Closure::parameter_modes`.
- B509 methods: `reference_subject_mode`, `payload_view_capture_modes`, `payload_view_capture_subjects`, `collect_payload_captures`, `check_mut_captures_under_view_subjects`, `capture_write_refusal`, `binding_use_count`, `enter_capture_views`, `collect_is_capture_views`.
- B509 state: `InvalidationScanState::capture_uses`.
- On `Program`: `parameter_mode`, `closure_parameter_views`, `payload_view_captures`.

**analyzer.rs, changed**
- Typing:
  - `reconcile_type`'s closure arm: modes, and the open-parameter type fill.
  - The closure arms of `compare_type_rigid` and `same_type_structure`.
  - The coerced closure types: `function_closure_type` / `function_closure_type_recorded`, `callable_closure_type`, and the variant constructor's.
  - The walk's `Node::ClosureType` arm and the closure literal's inference arm.
  - `closure_value_type_id`, which now reads any expression's recorded type.
  - `closure_callee_views`.
- Messages:
  - `pretty_print_type_inner`.
  - `type_mismatch_message`.
  - The call path's argument-mismatch push, now deduplicated.
- Rule 4 and captures:
  - `compute_wrapped_view_captures`, `compute_view_origins`, `subject_view_roots`, `compute_view_anchors`.
  - `scan_invalidation`: its Match arm, plus a new `Local` arm.
  - `scan_invalidation_if`.
  - `check_readonly_mutation`.

**Removed**
- `closure_type_parameter_views` (Analyzer and Program), `adopt_closure_parameter_views`, `callee_parameter_type_ids`.

**transformer.rs**
- `payload_view_capture_value`, `binding_holds_a_scalar_view_pair` (now covers payload captures), `tuple_target_destructures`, `assign_tuple_target_leaves`, and the `Expr::Assignment` arm.

**vilan-rust**
- `write_type_key`, `rust_type_inner`'s closure arm, `reentrant_view_read` and `closure_call_arguments` read the type's modes.
- `positioned_closure_carries_views` is removed.
- `names_a_mutable_loan` covers payload captures; `mutable_place` covers tuple targets.

**std**
- `store.vl`: the two `Option` write steps and the derive's single-payload write string (`store_enum_impls`). store-46 edits the same file; the three hunks are small and self-contained.

**For reactive-46 and store-46**
- std code that hands a value closure to a position whose type is written as a view closure is now refused. None exists today.
- `match &mut place` is the in-place spelling for any new through-variant step.
- Rule 4 now refuses a write to the subject before the capture's last use.

## New finds (`newitems46-solver-c.json`)

- **B?1:** a whole write to a bare `is` capture (`if held is Some(let v) { v += 1 }`) still steers to `mut`, and the `mut` copy's write does not reach `held`. This is B528's residual.
- **B?2:** under `match &mut place`, a capture inside a tuple sub-pattern is still a copy, and `mut` there is not refused.
- **E?1:** B495's mode refusal carries no quick-fix data.

Noted, not filed: adoption is a side effect of `reconcile_type`, and some candidate-selection paths call it speculatively. A literal probed against two candidates whose written modes differ would adopt the first. Nothing in the estate or the suite reaches this.

## Not reached

- B495's quick fix (E?1). Everything else in the three items is built.

## For the owner

Nothing blocks. One thing to confirm: B509's paper says S1 is not breaking, but `match &place` now makes its captures readonly views, so a scalar payload read as a value needs `*v`. I marked it BREAKING; the estate count is 0.
