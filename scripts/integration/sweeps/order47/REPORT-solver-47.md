# solver-47: Order 47 report

The lane is done. Every gate below is green on the final tip. Two items were not fully fixed: B443 is stopped on a solver gap, and B549 has the same cause as B548. No owner ruling is needed (see the last section).

**Branch tip: `solver-47` @ 28542715.** Base is `origin/next` @e5e15ca7 (= v0.44.0 folded), with no rebase. That is 19 commits, nothing pushed. The worktree is `vilan/.claude/worktrees/solver-47`, and `LANE-STATUS.md` there (untracked) lists every sha.

## Per item

Every new pin was red on the base: on the installed `vilan 0.44.0 (e5e15ca7b)` binary, or by planting the bug back (B533).

| item | status | sha | pins |
|---|---|---|---|
| B533 | FIXED (+ doc tidy 28542715) | e5ba36ef | `inference::traits::b533_a_bound_provided_at_two_instantiations_binds_from_the_expectation` |
| B539 | FIXED | 9511465a | `traits::b539_*`, `native_differential::a_trait_annotated_bindings_arguments_reach_its_initializer_on_both_backends` |
| B540 (closes B530) | FIXED | 26259d97 | `generics::b540_*`, `native_differential::a_nullary_variant_binding_grounds_from_its_reassignment_on_both_backends` |
| B541 | FIXED | a2fa7a2c | `tuples::b541_*` |
| B542 | FIXED | ed6a260c | `generics::b542_*`; std's `unzip` is back in its impl (`unzip_cell` removed); the `a152_*` pins run it |
| B543 | FIXED | 5c5933b3 | `tuples::b543_*` |
| B544 | FIXED | 9e0d7899 | `borrows::b544_*` |
| B545 | FIXED, refusal half only | 54d83444 | `borrows::b545_*` |
| B537 | FIXED (door b) | 4c1423ae | `returns::b537_*` |
| B547 | FIXED | 1d73ff6d | `module_resolution::b547_*` |
| B501 | FIXED in part | e2e2e9cc | `generics::b501_*`, plus an ignored remainder pin |
| B438 | FIXED | 7200dcd6 | `generics::b438_*` |
| B149 | FIXED on JS and in the analyzer | 7c56b30d | `std_surface::an_async_function_returning_a_task_types_as_the_value` (replaces the ignored pin and the residual pin) |
| B500 | FIXED | 69749ec5 | `traits::b500_*` |
| B443 | STOPPED | — | — |
| B367 | REPRODUCED: the refusal is reachable; pinned | c957e5bf | `module_resolution::b367_*` |
| B549 | NOT FIXED: same fault as B548 | aebc3598 | `module_resolution::b549_*` (node side passes; browser side `#[ignore = "B549: …"]`) |
| B535 (B515's flip) | FLIPPED | dec12a39 | see "The flips" |
| B536 flip | FLIPPED | 65e79c02 | see "The flips" |

Notes per item:
- **B533:** Unranked providers that disagree now bind nothing (`PatternProviders::Ambiguous`). The call's expectation or a written type argument decides. A call nothing decides is refused, naming both instantiations. Breaking edge: an unannotated call that silently picked `i32` is now refused (the estate has none).
- **B539:** The item's diagnosis held: a trait annotation resolves to `Unknown`, so the initializer was typed with no direction. The initializer is now typed toward the annotation read through the value's one impl (B489's `type_expected_through_impl`).
- **B540:** The item's hypothesis about the readiness probe was wrong. The binding grounds at once to `Maybe<hole>`, and the reassignment reconciled with the hole and bound nothing. Two changes:
  - the reassignment now fills the hole;
  - a method call on a `mut` binding whose type has a hole waits for that binding's pending reassignments, until the fixpoint stalls.
- **B542:** B403's "a bare `Type::f()` in its own impl means `Self`" now gives way only where an argument decides the parameter and `Self` would refuse it. So no program that compiled changes meaning.
- **B543:** A mapped type whose source is itself mapped now composes. Also, on JS, `entries()` on a family with no concrete layout emitted `[ ]`, so a loop over it silently ran zero times. That was a pre-existing wrong answer, and `emit_tuple_intrinsic` now builds the pairs over the receiver, as `keys()` does.
- **B544:** A whole write inside the guarded block now gets B528's steer. A guard's continuation local still steers to `mut`; the two are told apart by where the write stands.
- **B545:** Under a view subject, a write to a capture inside a tuple pattern, or `mut` on one, is refused with a steer to bind the tuple whole and write `pair.0`. Not built: the paper's one-slot tuple leaf as a view (the JS pair). The `mut` refusal is family `breaking` (the estate has none).
- **B537:** The return check stands down when the body's last statement starts at an unbound `return` that B523 steered. Each shape now gets one diagnostic.
- **B547:** A macro marker now binds an import only on the import fixpoint's reporting pass, after the re-export that shadows it has bound.
- **B501:** Under an expectation, an argument's binding to another call's open generic is released, and a call argument is typed toward the decided parameter. Free calls, method calls and return-tail expectations are fixed. Not reached: a call nested at another call's parameter (`takes(counted(source(..)))`); it is pinned `#[ignore = "B501: …"]`.
- **B438:** A call whose argument was refused no longer also says "cannot infer" (free-call path).
- **B149:** A call to a function written `async` now types as `assimilated_task_payload` of its declared return. Breaking: `let h: Task<i32> = make()` is now refused (estate 0). The native side is not fixed; it is filed as F?2.
- **B500:** The cause was not the Wire check. The macro surface (`construct_type_expr`) handed a module-qualified type to `[service]` as one opaque name with no arguments.
- **B443:** The two std blankets (`compare.vl`'s position-by-position `eq`, `hash.vl`'s `canonical_hash`) make tuple `==` and tuple keys work on JS. But member selection then admits a tuple-bounded blanket subject for non-tuple receivers ("'Option<usize>' is not a tuple …"); about 20 inference pins went red. Reverted, filed as B?2, and the attempted std files are kept in `finds/`.
- **B367:** The four-module reproducer is now refused at `c`, as visibility.md §3.5 states. The fix the refusal names (`import pkg::b::{ #(impl _) };` in `c`) runs. So the refusal is not dead code.
- **B549:** `document.vl` belongs to the process layer and imports `pkg::web::ui::{ render, escape_attribute, escape_text }`. In a browser build that import binds the browser twin of `ui`. That is B548's fault (a twin import binds the build platform's side, whatever platform the importing file is), so the fix belongs in resolution, not std: moving the escapers would not help, because `render` is process-only too. B548 was not taken.

**Goldens and censuses:** no corpus golden moved. The marker census was regenerated for B536: attribute pairs moved from "either order" to "one order only". No change to the copy or native censuses.

**Ledger:**
- re-keyed rows 581 (B533's `{why}`) and 618 (B535's new wording);
- three `NEW` rows: B541's message and B545's two messages;
- B533's ambiguity clause is a fragment inside 581's `{why}`, which the prose ledger should mention.

## Did the binding family have one cause?

No. There are six separate code paths. The shared theme is a type argument taken from a source that is no evidence (a first provider, a hole, a block's `Self`), or never told what it could have been:
- B533: the provider fallback in `trait_args_for_pattern`.
- B539: a trait annotation resolves to `Unknown`, so the initializer had no direction.
- B540: a hole the reassignment never filled.
- B541: diagnostic wording only.
- B542: B403's `Self` reading.
- B543: nested mapped substitution did not compose.

## The flips (R-c)

Both flipped, with the estate migrated first. Counts at the warning, before the flip:

| where | B515 trait not in scope | B536 attribute order |
|---|--:|--:|
| std | 0 | 0 |
| corpus (`vilan/test`, 298 programs checked) | 0 | 0 |
| docs fences | 0 (already gated) | 0 (docs gate green after the flip) |
| examples | **2**: `todo` and `walkthrough`'s `client.vl` call `.debug()`; both now import `Debug` | 0 |
| kolt (scratch copy of the owner's working tree) | 0 | 0 |
| Rust test fixtures | 3 native `.vl` fixtures, plus inline programs in about 30 tests: ui_rows, chunks, transport_robustness, reactive_channels, hmr_swap, module_resolution (b401 helper, b519, b535), collections, maps, macros, traits, tuples' `from_json` ×6, markdown ×5, markdown_golden, base_cache, one vilan-lsp test. All now import their trait. | 3 parse tests that deliberately write other orders (now assert the refusal and the read) |

**Kolt patch: none needed.** The copy checks clean under both flips.

**A fix to the fix data the editor will read.** The B515 warning's import was wrong for nested std modules: it spelled `pkg::delta::CollPipe`, which no user file can write. A std trait's import is now spelled from std's export index, so it reads `std::reactive::delta::CollPipe`.

**What the quick fixes (editor-47) will read:**
- **B535:**
  - the diagnostic is now an error;
  - the code is `vilan_core::analyzer::TRAIT_SCOPE_CODE` = `"trait-scope/not-imported"`;
  - the fix data is `vilan_core::analyzer::trait_scope_import(message) -> Option<&str>`, the full import statement (e.g. `import std::display::Display;`);
  - the span is the member's name;
  - where to insert it among the imports is the editor's choice.
- **B536:**
  - the diagnostic is now an error (a parse rewrite refusal; `parse_with_warnings`' warnings list is now always empty);
  - `parsing::MarkerOrderDiagnostic::of_message` → `Attributes`, code `marker-order/attributes`, and `is_warning()` now returns false;
  - the edit is still `parsing::marker_order_fix(source, message, span) -> MarkerOrderFix { code, title, span, replacement }`;
  - `vilan fmt` still formats a file whose only errors are marker-order refusals (one line in `formatter.rs`'s `parse`).

Docs updated: `spec/names.md` §4.6 (the trait-import rule) and `spec/grammar.md` §3.2. CHANGELOG entries are family `breaking` for both flips.

## Gates on the final tip (28542715)

| gate | result |
|---|---|
| `cargo nextest run --workspace -j 6` | 9654/9654 passed, 34 skipped |
| native_differential with `VILAN_NATIVE_DIFFERENTIAL=1` | 163/163 |
| deep_nesting at `VILAN_CANARY_STACK_KIB=1536` | 18/18 |
| `cargo clippy --workspace --all-targets -D warnings` | clean |
| `cargo fmt --check` | clean |
| `scripts/ci-local.sh vilan-fmt` | green |
| `scripts/ci-local.sh perf` | T2 green; growth plain 160 → 320 is x1.938 (limit x2.3) |
| `scripts/ci-local.sh windows` | green |

- The late-write count stays zero: on kolt with `VILAN_COUNTERS=1`, every phase reads `late-writes=0`, and the inference suite ran with M108's assert.
- No arm or local was added to `walk_expr_node_inner`.
- The full suite ran under load 26–33.

## Instructions on kolt's `vilan check`

Measured with `scripts/perf_count.py`, release binaries, on the same scratch copy, three runs each. Each binary got its own std through `VILAN_STD`, because the copy sits under the worktree and would otherwise pick up the tip's std.

| binary | runs (instructions:u) |
|---|---|
| base: installed `vilan 0.44.0 (e5e15ca7b)`, base std | 25,419,306,871 / 25,384,583,307 / 25,305,385,480 |
| tip 28542715 | 25,448,873,087 / 25,436,393,505 / 25,441,640,590 |

The tip is +0.2% against the base median (+0.5% against the base's third run). Peak RSS is 258–266 MB on both.

## Functions touched

**analyzer.rs, new:**
- `PatternProviders`, `trait_args_providers_for_pattern`, `same_type_arguments`, `ambiguous_bound_providers` (B533).
- `direction_through_trait_annotation` and field `binding_trait_annotations` (B539).
- `fill_binding_holes_from_reassignment`, `fill_holes_admitting`, `receiver_awaits_reassignment`, and field `reassignments_pending` (B540).
- `underdetermined_mapped_argument`, `written_text_of` (B541).
- `self_reading_bindings` and field `static_subject_self_bindings` (B542).
- Field `guard_continuation_captures` (B544).
- `collect_tuple_leaf_captures` (B545).
- Field `unbound_return_starts` (B537).
- `release_bindings_to_foreign_generics`, `decided_call_argument_direction` (B501).
- Field `calls_with_refused_arguments` (B438).
- `pub TRAIT_SCOPE_CODE`, `pub trait_scope_import`, `TRAIT_SCOPE_MARK` (B535).

**analyzer.rs, changed:**
- `trait_args_for_pattern`.
- `check_generic_bound_satisfaction`'s never-silent invariant: the B533 wording and the B438 stand-down.
- `resolve_variable` (B539, B540).
- `fill_holes_from`, which now delegates.
- `resolve_method_call` (B540 wait).
- `wire_prepped_assignment` (B540).
- `resolve_call_subject`'s free path (B541, B542, B501, B438).
- `resolve_world`: the static-path `Self` partition (B542) and the guard-continuation pass (B544).
- `substitute_type`'s `Mapped` arm (B543).
- `capture_write_refusal` (B544, B545).
- `check_mut_captures_under_view_subjects` (B545).
- `check_return_position` (B537).
- `resolve_prepped_local` (B537).
- `resolve_import` (B547).
- `infer_type_path`'s `Call` arm (B149).
- `check_trait_method_scope` (B535).

**mono.rs, impl_select.rs:** untouched.

**Elsewhere:**
- `macros.rs`: `construct_type_expr` (B500).
- `transformer.rs`: `emit_tuple_intrinsic` (B543's JS fallback).
- `parsing.rs`: `canonicalize_marker_run` and `MarkerOrderDiagnostic::is_warning`; `record_warning` removed (B536).
- `formatter.rs`: `parse` admits `AttributeOrder`.
- std: `reactive.vl` (`unzip` back in its impl).

## Finds

Filed in `sweeps/order47/newitems47-solver.json`, with repros under `sweeps/order47/solver-47/finds/`:
- **F?1:** natively, a `match` whose subject is a generic call returning a user generic enum is refused "unbound generic type parameter". The same subject bound by a `let` first, or the same shape over std's `Option`, runs.
- **F?2:** natively, a call to an `async fun` returning a `Task` is not assimilated (rustc E0369). This is B149's native half.
- **B?1:** `Cell::new(label)` inside the impl block that declares `new` is refused with the message "Expected str, but got str".
- **B?2:** a tuple-bounded blanket subject is admitted for non-tuple receivers. This is B443's blocker; the attempted std blankets are kept beside it.
- **B?3:** a written `Task<Task<str>>` annotation is not assimilated the way a formed one is.

## For the owner and the integrator

Nothing needs a ruling. Things to know:
- B501's nested remainder stays open under B501 (ignored pin).
- B545's view-for-a-one-slot-leaf half is not built.
- B443 waits on B?2.
- B549 waits on B548 (Order 48).
- The two example edits touch `vilan/examples`, which is docs-47's area.
- Breaking families this lane adds to the cut: the two flips, B533, B545's `mut` refusal, and B149's handle spelling. Each estate count is 0 apart from the flip sites listed above.
