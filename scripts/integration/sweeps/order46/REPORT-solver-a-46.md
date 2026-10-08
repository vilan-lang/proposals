# solver-a-46: Order 46 report

The REPORT file was not written. The tool environment refuses report files from a subagent, so the full report follows here for the integrator to save as `sweeps/order46/REPORT-solver-a-46.md`.

**Branch tip: `solver-a-46` @ 251643bb** (base origin/next @fe092e8d). Nothing pushed. `LANE-STATUS.md` is untracked in the worktree and lists every sha.

## Per item

**Items 1–2. B511: FIXED, c2947dfb.**
- What was wrong: a blanket's subject IS its binder. `impl_binder_generics` only read a nominal subject's arguments, so `Same::same(a, &b)` dropped its receiver binding. JS then emitted the un-instanced body (`self === other` printed `false`, even for `1` vs `1`), and native refused the call.
- The fix: the whole subject is walked now.
- Same route for two more receivers:
  - A bounded generic receiver reaching the trait only through a blanket (`resolve_blanket_through_bounds_in`, narrowed to the named trait). It was refused "bare trait type 'Same'".
  - A tuple or array receiver (`Swap::swapped((1, "one"))` was typed as the bare trait).
- Pins:
  - `inference::traits`: `b511_a_qualified_call_to_a_blankets_member_is_monomorphized`, `b511_a_qualified_call_reaches_a_blanket_through_a_bound_and_a_tuple_subject`
  - `native_differential`: `a_qualified_call_to_a_blankets_member_is_monomorphized_on_both_backends`
- Red on 0.43.0. No golden moved.

**B514 + B512: FIXED, one commit (they share code), c762c571.**
- B514, the emitter: `*if/match/{..}` over scalar views reads through. It asks the tail leaves (`collect_value_tail_leaves`) and evaluates a computed pair once.
- B514, the analyzer: the same conditional read as a value without `*` (a by-value argument, `print`, an operand) is refused per leaf with row 15's sentence.
- B512: reproduced as a real JS-vs-native divergence. JS aliased the chosen place; native copied it.
  - The ruling's refusal door is built: a `let` initialized by a conditional of views is refused at each leaf (B496's sentence), and `*` copies.
  - The other door (make it a true view binding) is filed as a design item.
- Pins:
  - `borrows`: `b514_a_dereferenced_conditional_of_scalar_views_reads_the_value`, `b514_a_conditional_of_scalar_views_read_as_a_value_is_refused`, `b512_a_let_initialized_by_a_conditional_of_views_is_refused`, `b512_the_spelled_copy_of_a_conditional_view_is_a_copy`
  - `native_differential`: `a_dereferenced_conditional_of_scalar_views_reads_the_value_on_both_backends`
- Docs: `spec/memory.md`. No golden moved.

**Item 3. B441: FIXED, e450f0b7.**
- A tuple pattern of another arity, or over a non-tuple (`let (a, b) = 5;` compiled too), is refused. This holds for `let`, `for`, a closure parameter and `match`.
- A shape that is still open (a generic, a tuple family, a hole) keeps today's reading.
- Pins (`tuples`):
  - `b441_a_tuple_pattern_of_another_arity_is_refused` (10 forms)
  - `b441_a_tuple_pattern_of_the_values_shape_destructures_at_every_depth` (the nested forms that keep working)
- Two `NEW` ledger rows. Docs: `spec/grammar.md`.

**Item 4. B498: FIXED, 0fd71de9.**
- Reproduced only through a bound: `f.fresh()` with `F: Fresh<T>`. A direct call and a qualified call both worked.
- The JS `dispatch_to_member` now uses `impl_select::bind_subject_and_bounds`, as native always has.
- **Two corpus goldens move, both runtime-identical** (judged with node):
  - `reactive-selector` loses one duplicate instance (12382 → 12246 B).
  - `reactive-on-change` renumbers its temporaries.
  - I confirmed the attribution by rebuilding with the hunk reverted: both goldens match again.
- Copy census unchanged.
- Pins: `traits::b498_a_static_call_on_a_nested_binder_reached_through_a_bound_is_grounded`, plus a native differential pin.

**Item 4. B510: FIXED, 11d644d6.**
- Three holes:
  - `Self` inside a default is typed as the bare trait, and the bound derivation answered from the first implementor ("Expected T, but got i32"). It now answers from the trait's own parameters and supertrait chain.
  - That binder was dropped as foreign, so a closure literal in the call got the callee's `U`. It now binds.
  - JS bound the callee's `F` to the trait type itself. `resolve_binding_type_id` maps it to the type the instance is for.
- Pins: `traits::b510_a_trait_default_passing_self_to_a_generic_over_its_trait_runs`, plus a native differential pin.

**Item 5. B515: R-g door (b) built, 5391a169, plus follow-up 251643bb.**
- New post-build pass `check_trait_method_scope`. It warns at the member's name:
  - "`to_string` is `Display`'s, and this file does not import `Display`: … Import it (`import std::display::Display;`) — this is an error from v0.45.0"
- What counts as in scope: the file imports the trait, or a name from the trait's module, or a name from the block's module; or the prelude binds one; or the file declares it. A derived block counts as its attribute's file.
- Skipped: calls through a bound, std, frozen files, dependencies, generated code.
- **The count:**

| Where | Sites |
|---|---|
| kolt | 23, in 8 files |
| corpus | 5 |
| docs runnable fences | 27 (272 fences with `main` checked) |
| examples | 0 |
| website | 0 |
| playground | 0 |
| **Total** | **55** |

- By trait:
  - kolt: Display 6, Debug 5, Iterator 5, Json 2, FromJson 2, SetPipe 2, CssValue 1
  - docs: mostly Iterator defaults and the pipe sealers `CollPipe`/`SetPipe` `memo`
- Because of the count, door (b): a warning this release, an error in v0.45.0.
- 251643bb: eight of the suite's own embedded test programs (`service_layer`, `reactive_channels`) assert a clean stderr and called `.debug()`/`.hash()` this way. They now import `Debug`/`Hashable`.
- Pins (`modules`): `b515_a_trait_method_resolved_through_another_modules_import_warns`, `b515_a_trait_in_scope_does_not_warn`.
- One `NEW` ledger row. Family marked `tooling`, because it only warns this release; R-f listed B515 as breaking.

**Item 6. B439: NOT REPRODUCED.**
- Already fixed and pinned on base by 5dbc8430 ("solver-a-45: B467 + B439"). The tracker has drifted.
- Probe: `edits.push(|&mut list| list.push(7))` compiles and prints 2 on 0.43.0.
- The native leg is F69's.
- Three neighbouring false refusals turned up while probing; filed as B?3.

**Item 7. B502: FIXED, 53be8c24.**
- Reduced: it needs one type implementing `Shape` twice behind a `dyn`. It was never "T bound across calls".
- `derive_generics_from_bounds` now reads an object's own trait chain first.
- Pins: `dyn_objects::b502_a_trait_object_binds_a_bounds_arguments_from_its_own`, plus a native differential pin.

**Item 8. B455: FIXED as ruled (B), 00f182b8.**
- `(impl Box with One)` now works in: the parser (binders refused), the formatter (prints it, sorts by full text), `grammar.md` and `names.md`.
- Both admission maps take a block only if its `with` clause names the trait.
- The trait resolves in the importing file's scope, like the subject, so the file must import it.
- `ImplAdmission.whole_blocks`: a whole-block selector now admits a marker block.
- The empty slot is gone. A tail that names nothing now says "The blocks it reaches provide `describe`" (or "nothing — select the block whole").
- A non-trait after `with` is refused.
- Pins: `module_resolution::b455_*` ×4, plus the formatter's `a_selector_naming_its_trait_round_trips_and_sorts`.
- One `NEW` ledger row.

## Gates on the tip

| Gate | Result |
|---|---|
| Full `cargo nextest run --workspace -j 6` @00f182b8 | 9416 run, 9408 passed, 8 failed |
| Those 8 failures | All B515 warnings in embedded test programs; fixed in 251643bb; `service_layer` + `reactive_channels` re-run 99/99 |
| inference | 5092/5092 |
| native_differential, default | 143/143 |
| native_differential, `VILAN_NATIVE_DIFFERENTIAL=1` | 143/143 |
| check_scope_differential | 15/15 |
| corpus | 13/13 |
| copy_elision_census + diagnostics_ledger | green |
| module_resolution, docs, lsp/ide | green |
| `cargo fmt --check` | clean |
| `cargo clippy -p vilan-core -p vilan-cli --all-targets -D warnings` | clean |
| `vilan fmt --check` | clean over crates, vilan, editors, npm, homebrew, assets, scripts |

- On `vilan fmt`: the CI leg scans `.`, which includes my `target/` scratch .vl files (N138, syntax-46's fix). No `.vl` fixture was added or edited.
- No arm or locals were added to `walk_expr_node_inner`.
- **Instructions on kolt `vilan check`** (callgrind, release, kolt copy):

| Binary | Instructions |
|---|---|
| base 0.43.0 | 26,594,700,883 |
| tip | 26,729,932,301 |
| Change | +0.51% (includes rendering the 23 B515 warnings) |

## New finds

Written to `sweeps/order46/newitems46-solver-a.json` with placeholder ids:
- **B?1, a JS miscompile.** On a type implementing `Shape` twice, `dyn Named<str>` (supertrait `Shape<str>`) answers `area` from the `Shape<i32>` table: it prints 4, not "big". Rustc refuses natively. Same on 0.43.0.
- **B?2.** With two instantiations of a bound's trait, `T` binds from the first provider and ignores the expectation: `let s: str = measure(Square{..})` is refused.
- **B?3, B465's family.** A closure literal for a `&mut` parameter is refused "cannot mutate immutable" in three positions: a return, a generic parameter like `List<|&mut ..|>::push`, and an annotated `let` that is never called.
- **F?1, native.** `*{ &m }` is refused by rustc (E0614). Same on 0.43.0.
- **A?1, design.** A conditional of views as a real view binding: the door B512 did not take.
- **B?4.** B515's v0.45.0 flip. First migrate the corpus (5) and docs (27) sites, apply kolt's patch, and give the warning its quick fix (editor). Owner question below.

## Kolt patch

`sweeps/order46/solver-a-46/kolt-b515-imports.patch`
- Adds the imports for all 23 sites in 8 files. Imports only.
- `git apply --check` passes against kolt HEAD.
- On a copy, `vilan check` is clean afterwards.
- It is the owner's to apply.

## For the integrator and solver-b-46 (which rebases onto me)

- **Changed internals:**
  - `callee_bindable_generics` now includes blanket and tuple subject binders.
  - `derive_generics_from_bounds` has new `Type::Trait` (Self) and `Type::Dyn` arms, and the receiver filter admits Trait.
  - New: `resolve_blanket_through_bounds_in`.
  - JS `dispatch_to_member` binds bound binders.
  - `resolve_binding_type_id` is applied at instance entry.
  - `check_view_value_reads` gained `collect_view_leaves`.
- **The B515 warning will hit new pins** that call trait methods (`.debug()`, `.to_string()`, Iterator defaults, `.hash()`) without importing the trait. Any harness that asserts a clean stderr will go red. reactive-46 and store-46 should know.
- **New struct fields.** `node::ImplSelector` has `trait_` and `trait_text`; any new constructor (syntax-46, editor-46's organizer) must set them to `None`. `ImportImplSelector` has `trait_type`. `ImplAdmission` has `whole_blocks`.
- **Ledger:** 4 `NEW` rows (B441 ×2, B515, B455) need prose. `IMPL_SELECTOR_SHAPE` text is unchanged.
- **CHANGELOG:** I created `## Unreleased`. There are 9 entries; each has its family marker.
- **Docs touched:** `spec/memory.md`, `spec/grammar.md`, `spec/names.md`. No count words.

## Needs the owner's ruling

1. **Before B515's v0.45.0 flip:** most docs sites are `Iterator` defaults (`filter`, `map`, `to_list`, …) and pipe `memo`. Should `Iterator` (and perhaps the pipe sealers) join the base prelude? Otherwise every iterator chain needs `import std::iterator::Iterator;`.
2. **A?1:** does the language want a conditional of views to be a view binding (Rust-like), or does B512's refusal stand?