# solver-b-46: Order 46 report

**Branch tip: `solver-b-46` @ 564a76c9** (base `origin/next` @7ee822af, which holds syntax-46, native-46 and solver-a-46). 16 commits, nothing pushed. `LANE-STATUS.md` (untracked, in the worktree) lists every sha. Every gate below ran on the tip.

## Per item

| # | item | status | sha |
|---|---|---|---|
| 1 | B522 non-place assignment target | FIXED | 0b33558e |
| 2 | B532 sub-trait object's supertrait table | FIXED | ddd3b685 |
| 2 | B533 (neighbour) | LEFT: not the same fix | — |
| 3 | B529 rule 4 at a part of the root | FIXED | 93ee4f87 |
| 4 | B531 `2 * true` | FIXED | 57c86371 |
| 5 | opaque returns S0: B491, B490, B489 | FIXED | 61000fc1, d18beb84 (+0e7e2570 tidy), 2894350c |
| 5 | opaque returns S1 (`Type::Opaque`), S2 (trait-method opaques, std's 14 `dyn Pipe` sites) | NOT REACHED | — |
| 6 | B516 | FIXED | e26a923e |
| 6 | B447 | FIXED | 27c14fec |
| 6 | B440 (+ B442's bound-elsewhere shape) | FIXED | 2362f957 |
| 6 | B513 | FIXED | 74c9adb3 |
| 6 | B518 | FIXED | 10572e5e |
| 6 | B497 | FIXED | 8e741b2b |
| 6 | B508 | FIXED | 7cdda670 |
| 6 | B534 (two of three positions) | FIXED in part | 564a76c9 |
| 6 | B499 | NOT REPRODUCED | — |
| 6 | B530 | STOPPED (diagnosis filed) | — |
| 6 | B442 single-parameter repro | LEFT (message filed) | — |
| 6 | B501 | NOT REACHED | — |

### 1. B522: FIXED, 0b33558e
- Reproduced: `(x + 1) = 2`, `-x = 1`, `!b = true` checked clean and the JS threw `Invalid left-hand side` at load. So did `seven() = 1`, `x.abs() = 3`, `1 = 2`, `[x] = [1]`, `Some(x) = Some(1)` and `(if c {x} else {x}) = 4`.
- The fix is a new Class A check, `check_assignment_places`, routed through `reusable_entity`. A target must be:
  - a binding, a field, a tuple slot or an element;
  - a tuple of places;
  - or a call that returns a `&mut` view (`cell.write() += 1`).
- `*x`, `?.` and unresolved targets keep their own refusals. One diagnostic per assignment, at the first non-place, naming its kind.
- The rule sits in the analyzer, not the parser, because the view-returning call is a place and only resolution can tell it apart.
- Pins (`inference::borrows`):
  - `b522_an_assignment_to_something_that_is_not_a_place_is_refused`: 13 targets, each refused exactly once.
  - `b522_every_place_shape_still_assigns`.
- One `NEW` ledger row. Docs: `grammar.md` §3.4.
- **New find B?1:** a tuple target that holds an element, a nested tuple or a tuple-typed binding is a place, but both emitters miscompile it. Filed, not fixed.

### 2. B532: FIXED, ddd3b685
- The fix: both emitters built each object-table slot by asking at the OBJECT's trait application (`Named<str>`). A supertrait's member fell to the by-name lookup, which takes the first `Shape` impl.
- New `mono::object_member_preference`, shared by both emitters: the slot is selected at the DECLARING trait's application, with the clause chain's arguments substituted down. Native's private `object_member_declaration` moved into `mono` beside it.
- Pins:
  - `dyn_objects::b532_an_object_over_a_subtrait_answers_from_the_supertraits_instantiation`: one level, two levels, a concrete clause (`Big with Shape<str>`), the other instantiation, and a call through a bound.
  - `native_differential::an_object_over_a_subtrait_answers_from_the_supertraits_instantiation_on_both_backends`.
- **Residual:** a clause argument in a nested form (`with Shape<Option<T>>`) is still resolved only at the top of each position.
- **B533 is left.** It is a different path (`trait_args_for_pattern`'s first-provider fallback).

### 3. B529: FIXED, 93ee4f87
- The item's hypothesis was too narrow. The hole was not specific to wrapped captures: E1 fired only on a WHOLE-root reassignment, so `bag.items = [..]` under `let q = &mut bag.items[0]` passed as well.
- The fix:
  - New `compute_view_anchors` (it mirrors `compute_view_origins`' sources): each view records WHERE under its root it points.
    - A `&place` view: exactly that place.
    - A `for e in &mut c` view: an element of `c`.
    - A `borrows` call's view or a wrapped capture: anywhere under the lent place.
  - An assignment to an AGGREGATE place is an event in two cases: it is a prefix of a live view's path, or it overlaps a call view's lent place.
  - Scalar writes stay legal. They are content writes, which §6.4 permits.
- Pins (`inference::borrows`):
  - `b529_a_write_to_the_part_of_the_root_a_live_view_points_into_is_refused`: six shapes, the papers-46 probe first.
  - `b529_a_write_beside_a_live_view_is_still_legal`.
- One `NEW` ledger row. Docs: `memory.md` §6.4 (the spec already said "or an enclosing place").
- Family `breaking`. The corpus, docs, examples and kolt carry no such write.
- The payload-views paper is NOT built.

### 4. B531: FIXED, 57c86371
- The fix: a native number's `-` `*` `/` `%` and its bitwise and shift operators refuse a grounded right operand that is not a number. The refused operands are `bool`, `str`, a struct or an enum.
- B196's `f64 * i32` carve-out stands.
- Pin: `platform::b531_a_non_numeric_right_operand_of_a_numbers_arithmetic_is_refused` (nine expressions).
- One `NEW` ledger row. Docs: `types.md`.
- Family `breaking`. Kolt and the estate carry none.

### 5. Opaque returns: S0 built; S1 and S2 NOT REACHED
- **B491, 61000fc1.**
  - The trait-method refusal now steers to `dyn Holder<i32>`, with its arguments.
  - Ledger row 596 is re-keyed: the slot is now `{application}`; the fragments are unchanged.
  - Pin: `traits::b491_*`.
- **B490, d18beb84** (tidy 0e7e2570).
  - A bare-trait `[rpc]` return is refused ONCE, at the method: "… a bare-trait return hides the body's type from the caller, and what crosses the wire for a hidden type is not designed — return `MemoCell<i32>`, the type the body builds" (Q9).
  - The three generated-code restatements stand down. The service's origin is recorded, and its "in code generated by this attribute" diagnostics are dropped in the analysis tail, once every pass has spoken.
  - B253's steer drops its stale "a generic for a return" clause.
  - Pin: `generics::b490_*` (exactly one diagnostic). One `NEW` ledger row.
  - Paper find 5 (the `.cell()` and `.memo()` naming) is already fixed on the base.
- **B489, 2894350c.**
  - New constraint `OpaqueReturn` (priority 12, after `CallSubject`). It reads the annotation through the tail type's ONE impl of the trait, using the new `type_expected_through_impl`.
  - It then fills the holes the tail left where they stand (new `fill_holes_from`) and checks the tail against the result.
  - `SignalCell::new(None)` under `Source<Option<i32>>` is now `SignalCell<Option<i32>>`, and it runs natively.
  - Pins:
    - `traits::b489_a_bare_trait_returns_arguments_reach_the_body`: block tail, `if` arms, a generic argument, a two-parameter trait, and the typing.
    - `native_differential::a_bare_trait_returns_arguments_reach_the_body_on_both_backends`.
  - **Paper find 2 does NOT reproduce on this base** (o5: a generic return instantiated twice, natively one type for both). It is pinned in the same native probe.
  - **The paper's §1.3 is wrong about the `let`.** `let a: Source<Option<i32>> = SignalCell::new(None)` has the same hole. A post-build fill there was tried and is not enough; filed as B?2.
- **S1 and S2 were not reached.** This is capacity, not a ruling problem. Nothing in Q1–Q11 is unbuildable.
  - S1 is a new `Type` variant touching about 75 match sites (Dyn's count), member lookup, both mono reveals, the printer and hover.
  - I judged a half-built S1 worse than none, since it is the breaking slice.
  - The design is ready to start from: `Opaque(definer, captured)`; the call type taken from `opaque_returns`; member lookup borrowed from the `Generic(constraint)` arm; reveal through the definer's inferred return under `captured`.
- **What users see from this lane:** S0 only, nothing hidden yet. The before and after examples are the three items above.
- **Estate count:**

  | where | bare-trait returns |
  |---|---|
  | kolt | 0 (one `dyn Flow` return, `model.vl::transient_of`, which A150 removes) |
  | std | 0 |
  | examples | 0 |
  | corpus | 0 |

  **No kolt patch is needed: nothing moves.**

### 6. Inference
- **B516, e26a923e.**
  - The binding's readiness probe was undirected. A literal whose body needs the parameter can never type that way.
  - Fix:
    - A binding annotated with a closure type now probes in that direction.
    - An annotated binding whose type IS its annotation keeps the annotation's type id. This is the key B465's view adoption reads.
  - Side effect: B400's refusal now stands alone. Before, it carried a spurious "`list` is never given a type" next to it.
  - Pin: `generics::b516_*`.
- **B447, 27c14fec.** B389's literal-element rule now reaches a tuple literal element (literal tuples only, under a fully determined expectation). Pin: `tuples::b447_*`.
- **B440, 2362f957.**
  - `invert_mapped` gains two paths:
    - A constant template binds nothing at any element, so it only checks.
    - A family already bound in the call checks against the template expanded over that binding, which also holds the arity.
  - With it, B442's `None` takes the family's element when another parameter binds `T`.
  - Pins: `tuples::b440_*`, `tuples::b442_*`.
- **B513, 74c9adb3.**
  - B406's expectation step now also takes a closure literal with unannotated parameters. The bound must be a closure type of the literal's arity and fully determined.
  - Pins: `generics::b513_*`, plus `native_differential::a_closure_arguments_parameters_take_the_annotated_result_on_both_backends`.
- **B518, 10572e5e.** The printer now writes a closure-typed parameter in parentheses: `|(|i32| void)| void`. Pin: `generics::b518_*`.
- **B497, 8e741b2b.** The steer now spells `: HashMap<str, i32>`. A sweep found no other `Map<`/`Set<` in any steer. Pin: `platform::b497_*`.
- **B508, 7cdda670.** A `Type::Closure` receiver now takes the impl-member route, so blankets reach closures. Pin: `traits::b508_*` (arities and a field).
- **B534, 564a76c9: two of its three positions.**
  - The return position is fixed: adoption now reads a function's return tail leaves.
  - The annotated binding (called or not) was closed by B516.
  - NOT taken: a generic parameter instantiated with the closure type (`List<|&mut ..|>::push`). Its written type is `T`, so there is no written closure type to read.
  - Pin: `borrows::b534_*`.
- **B499: NOT REPRODUCED.** Probe: `print(Source::get(cell).keys().len())` on a `HashMapCell<str, i32>`, and `Source::get(cell).len()` on a list cell. Both check and run on the base.
- **B530: STOPPED.**
  - Two hole-closing hooks in `resolve_variable` were tried and withdrawn. Instrumentation shows neither runs for the binding.
  - The cause: `mut found = Maybe::Nothing` never grounds in the fixpoint. It is committed to `Maybe<any>` afterwards, and the reassignments are never consulted.
  - Diagnosis and recommendation filed as B?3.
- **B442 (single parameter): left.** With no other evidence for the element, a refusal is right, but the message reads as a mismatch. Filed as B?4.
- **B501: NOT REACHED.**

## Pins, goldens, censuses
- Every new pin was red on the 0.43.0 toolchain, judged by probe before the fix. B489's JS-only half was made non-vacuous with a typing assertion.
- No corpus golden moved. The copy-elision census is unchanged. No `.vl` fixture was added.
- No arm or local was added to `walk_expr_node_inner`, so the expr-walk frame was not re-measured.
- Ledger:
  - Five `NEW` rows: B522, B529, B531, B490, plus the B529 part-reassignment row counted in that five.
  - One re-key: row 596's slot is now `{application}`.

## Gates on the tip (564a76c9)

| gate | result |
|---|---|
| inference | 5112/5112 (1 skipped, pre-existing) |
| native_differential, default mode | 156/156 |
| native_differential, `VILAN_NATIVE_DIFFERENTIAL=1` | 156/156 |
| check_scope_differential | 15/15 |
| corpus | 13/13 |
| copy_elision_census | 2/2 |
| diagnostics_ledger | 25/25 |
| module_resolution | 224/224 |
| docs | 12/12 |
| service_layer | 59/59 |
| reactive_channels | 40/40 |
| vilan-lsp + vilan-ide | 993/993 (21 skipped) |
| `cargo clippy --workspace --all-targets -D warnings` | clean |
| `cargo fmt --check` | clean |
| `vilan fmt --check .` (the `vilan-fmt` leg's command, debug binary) | clean |

## Instructions on kolt `vilan check`
Callgrind, release binaries, the same scratch copy of kolt, warm.

| binary | instructions | vs 0.43.0 |
|---|--:|--:|
| `vilan 0.43.0` (fe092e8d) | 26,594,199,402 | — |
| base 7ee822af (solver-a-46's tip, as solver-a reported) | 26,729,932,301 | +0.51% |
| this tip | 26,760,564,328 | +0.63% |

- This lane's own share is **+0.11%**.
- kolt on the tip: 0 errors and 23 warnings, all of them B515's (solver-a). None of this lane's refusals fire in kolt.

## Internals changed (for reactive-46, store-46 and perf-46)

**analyzer.rs, new:**
- `check_assignment_places` and `first_non_place` (B522; added to the `class_a_checks!` list).
- `place_path`, `call_hands_back_a_view`, `compute_view_anchors`; the types `PlaceStep`, `AnchorDepth`, `ViewAnchor`; `InvalidationViolation::PartReassignment`; and `InvalidationScan.view_anchors` (B529).
- The field `rpc_opaque_return_origins` and `service_attribute_origin` (B490).
- `Constraint::OpaqueReturn` with its anchor and priority arms, `resolve_opaque_return`, `type_expected_through_impl` and `fill_holes_from` (B489).
- `tuple_literal_holds_unsuffixed_numeric` (B447) and `untyped_closure_literal_arity` (B513).

**analyzer.rs, changed:**
- `check_invalidation` and `scan_invalidation`'s `Assignment` arm.
- The native-left non-`+` operator block (B531).
- `check_rpc_signatures`.
- The diagnostics tail in `analyze` (B490's filter, applied just after `diagnostic_sources` is computed).
- `bare_trait_in_value_position`'s message.
- The bare-trait drain arm: the trait-method message, plus `OpaqueReturn` pushed for an opaque return.
- `resolve_variable`: the probe direction and the annotation-id retention (B516).
- The `Expr::List` arm of `infer_type_path` (B447).
- `invert_mapped` (B440).
- `bind_literal_generics_from_expectation` (B513).
- `resolve_method_call`'s nominal arm now admits `Type::Closure` (B508).
- `pretty_print_type_inner`'s `Closure` arm (B518).
- The never-determined steer text (B497).
- `adopt_closure_parameter_views` (B534).

**Elsewhere:**
- mono.rs: `object_member_declaration` (moved here) and `object_member_preference` (new).
- transformer.rs: `emit_vtable`.
- vilan-rust: `ensure_object_impl`; its private `object_member_declaration` was removed. This is the B532 native half, outside the opaque-returns exception; native-46 had already merged.

**Notes for the other lanes:**
- **perf-46:** `compute_view_anchors` is one more whole-program fixpoint, beside `compute_view_origins`, inside `check_invalidation`.
- **reactive-46 and store-46:** a `[service]` struct whose `[rpc]` method returns a bare trait now yields exactly ONE diagnostic.
- **reactive-46 and store-46:** B529 refuses aggregate writes under a live view into a part of the root. Watch for it in new store code.

## New finds
In `sweeps/order46/newitems46-solver-b.json`:
- **B?1:** tuple assignment targets holding an element, a nested tuple or a tuple-typed binding miscompile. JS throws at load; native gets rustc E0070.
- **B?2:** a trait-annotated `let` does not carry the trait's arguments into its initializer (B489's twin; the paper's §1.3 claim is wrong).
- **B?3:** B530's root cause: the nullary-variant binding never grounds in the fixpoint.
- **B?4:** an underdetermined mapped-tuple element is reported as a mismatch.

## Needs the owner's ruling
- **Opaque returns S1/S2 are not built.** Should they ride v0.44.0 at this seal (R-f lists "the opaque-returns build" as breaking)? Or carry to Order 47, where S1 starts from the design note above? Only S0 shipped here, and S0 is not breaking.
- **B529 is family `breaking`:** an aggregate write into a viewed part of the root is now refused. Nothing in the estate is affected. It joins R-f's breaking list if the cut wants it named.
