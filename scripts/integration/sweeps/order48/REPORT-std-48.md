## std-48 report

**Tip:** `ec034704` on branch `std-48`, worktree `/home/reed/code/vilan-lang/vilan/.claude/worktrees/std-48`. Not pushed.
**Base:** `origin/next` @`dfe0c5fc`. I started on `e75bc57c`; debug-48 was merged into next in between and touched `analyzer.rs` and `CHANGELOG.md`, so I rebased before the gates. Every gate number below was taken on the rebased tree.

Seven of the nine items are closed in six commits. **A161 is blocked: its premise is wrong** (details under A161). Two commits each carry a pair of items (A159+A160, E271+E272), because each pair shares one function and one set of pins.

### Items

**A159 + A160 — `7836df8f` (diagnostics). Closed.**
- Cause: `check_class_written_twice`'s list of class writers left out `bind_attr("class", ..)` and `toggle_attr("class", ..)`.
- Cause: its sentence assumed the later writer always stays. When the earlier writer is a binding, the binding writes again on every change, so the two take turns.
- Fix: both methods are now writers, under the same literal-`"class"` test `.attr` gets.
- Fix: a new function, `class_value_is_binding`, reads the value type that the `attr` call bound for its `V` (from `own_generic_call_bindings`). That is needed because a call's result type is not stored on the argument. When the earlier writer is a binding, the message now says the two writers "take turns".
- One new ledger row.

**A162 — `80ae79d4` (breaking, R-a). Closed.**
- The double-write warning is now an error, pushed through `push_in_source`. Message and steer are unchanged.
- **Estate before the flip: 0** in std (exempt by design), the corpus (148 programs), the docs fences, the examples (11), the templates, the website (`src/` plus the 4 playground examples) and kolt (scratch copy of the owner's working tree).
- My first count missed one place: the test suite's own fixtures. `element_head_order.rs`'s order-sensitive fixture deliberately wrote class twice to demonstrate the sorter's barrier and its last-wins pair. I moved that demonstration to `title`, which follows the same last-wins rule. This is folded into the A162 commit and noted in its CHANGELOG entry.
- Docs: the styling guide's Traps section.

**B568 — `bfba2955` (breaking, R-b). Closed.**
- A new function, `refuse_internal_field_write`, called from `resolve_struct_initializer`, refuses the literal under `labels::internal_field_out_of_reach` with the field's reason text.
- It reports once per literal: at the first internal field the literal writes, or at the struct name when it writes none. That check runs before the field-count message, which would otherwise tell the author to add the internal fields.
- **Destructuring:** vilan has no struct pattern. `let Store { root, .. } = s` and a `Store { root = let r }` match arm are already refused by the parser, so no pattern can reach an internal field. This is pinned.
- **Estate: 0** (same bodies as A162). One ledger row. Docs: `spec/grammar.md`.

**E271 + E272 — `812d7191` (diagnostics). Closed.**
- E271: inside `check_generic_bound_satisfaction`, a failed `Slot` bound on a desugar-generated `.child` (recognised by its zero-width member span) now goes to `element_hole_refusal`.
  - The error is spanned on the hole and says what a hole accepts.
  - For a number or bool it suggests the i-string form (`{i"{5}"}`). For a `Source` of one it suggests `.derive(|value| i"{value}")`; `is_source_of_text` checks std's `Flow` at each text type the value's type mentions.
  - The "bound declared here" note on std's `child` is dropped for these errors.
  - A hand-written `.child(5)` keeps the old message.
- E272: `with_fragment_steer` adds "A fragment `<>…</>` is a `List<View>`, not one `View`: wrap its children in one element…" to the mismatch at a declared return, a `let` annotation, an argument and a struct field.
  - A fragment is recognised as a list literal whose source span starts with `<`; written lists keep the plain message.
- Two ledger rows. Docs: Building UI.

**K30 — `92fb01f1` (tooling). Closed.**
- `templates/browser/counter.vl` and `templates/fullstack/src/client.vl` now use element syntax.
- New pin `init::the_ui_templates_write_their_view_in_element_syntax`; the browser-build test also checks the text children reach the bundle.

**B555 — `ec034704` (diagnostics). Closed.**
- Premise partly wrong: `import std::js::null::{ .. }` does not work either. Every spelling stops at the `null` keyword.
- The module holds only the `null` value's type, which every program loads anyway, so nothing needs importing. It is now refused with that reason (`NULL_MODULE_IS_NOT_IMPORTED`, at the keyword), rather than the generic import-path error.
- `RULE_STATEMENT_SITES` goes 61 → 62; the ledger prose for row 229 needs the same number.

**A161 — no commit. Blocked; needs your ruling.**
- std cannot write `impl [T; n] with Items<T>`. An impl subject's array length must be an integer literal, so there is no way to say "every length", and every comparator checks lengths by value.
- The native backend also generates one instance per concrete type, so it would need the length substituted per receiver.
- Supporting this means either I2 (const-generic lengths, already blocked on its design) or a narrower "any length" impl head (`impl [type T; _]`). That touches the parser, the solver, mono and both emitters, which are outside this lane.
- F109 (native emits an annotated array literal as `vec!`) would block the native differential first.
- I filed the narrow door as A?1 with the four pieces it needs, and recommend you rule whether it gets its own slice before I2.

### Pins by name
- `inference::styling`: `a159_bind_attr_and_toggle_attr_on_class_are_class_writers`, `a159_bind_attr_and_toggle_attr_on_other_names_are_not_class_writers`, `a160_an_earlier_binding_writer_is_reported_as_taking_turns`, `a160_an_earlier_static_writer_keeps_the_last_write_sentence`, `a162_an_element_that_writes_its_class_twice_is_refused_naming_both_writers` (was A155's warning pin), `a155_one_class_write_per_element_is_silent` (now also compiles its program).
- `inference::store`: `b568_a_struct_literal_writing_an_internal_std_field_is_refused`, `b568_a_literal_that_writes_no_internal_field_is_refused_at_the_struct_name`, `b568_a_packages_own_internal_field_is_constructed_as_before`, `b568_no_pattern_names_a_field_so_none_reads_an_internal_one`.
- `inference::modules`: `e271_a_hole_holding_no_text_is_refused_at_the_hole_with_the_text_form`, `e271_a_written_child_call_keeps_the_bound_refusal`, `e272_a_fragment_where_a_view_is_wanted_is_named_with_the_fix`, `e272_a_written_list_where_a_view_is_wanted_is_not_called_a_fragment`, `b555_importing_the_null_module_is_refused_once_with_the_steer`.
- `parsing::tests::b555_an_import_of_the_null_module_is_steered_at_the_keyword`.
- `init::the_ui_templates_write_their_view_in_element_syntax`.
- Red first: the A159, A160 and E271/E272 pins ran red before the fix. The B568 pins went red when I temporarily disabled the new check, then green when restored.

### Gates (all on base `dfe0c5fc`)
- **Full suite** (`cargo nextest run --workspace -j 6`): 9802 of 9805 passed, 34 skipped, run at load 30–58. The 3 failures were mine:
  - the 2 `element_head_order` fixture tests (A162);
  - `grammar_ebnf::n113`, because a line of my grammar.md paragraph started with `literal ` and the test read it as the grammar rule; re-wrapped.
- I folded those fixes into their commits and re-ran those two test binaries: 19/19 green. I did not re-run the whole hour-long suite for that test-fixture and prose change.
- **Native differential** with `VILAN_NATIVE_DIFFERENTIAL=1`: 182/182. The default mode is part of the suite run.
- **`check_scope_differential`:** 15/15.
- **Clippy** `-D warnings`: clean. **`cargo fmt --all --check`:** clean.
- **`scripts/ci-local.sh`:** `vilan-fmt`, `windows` and `perf` all green. The perf T2 verdict is green; most rows have no ceiling for the `local` class, so they were reported rather than enforced.
- **kolt `vilan check`, instructions** (release builds, scratch copy):
  - warm runs: base 17.449 G / 17.526 G, tip 17.481 G / 17.428 G — no measurable difference;
  - cold runs: 19.15 G base vs 18.83 G tip.
- No std `.vl` changed, so the std twins could not diverge.

### Analyzer functions touched
- `check_class_written_twice`
- `class_value_is_binding` (new)
- `resolve_struct_initializer`
- `refuse_internal_field_write` (new)
- `check_generic_bound_satisfaction` (the E271 handoff, and dropping the note for hole errors)
- `element_hole_refusal` (new)
- `is_source_of_text` (new)
- `with_fragment_steer` (new), called from `check_return_position`, `resolve_variable`, `resolve_call_subject` (the argument mismatch) and `check_field_value`

The E272 calls and the E271 handoff sit in inference code that solver-48 owns. Each is a one-line call into a new helper; the existing logic is untouched.

### Needs your ruling or the integrator's attention
1. **A161:** whether the narrow "any length" impl head (A?1) gets its own slice ahead of I2.
2. **Ledger prose:** the proposals-side `diagnostics-ledger.md` still needs four new rows (written `NEW` in the tsv) and row 229's count changed to 62. I did not edit the proposals ledger.
3. **Seal:** A162 and B568 needed no kolt migration (0 sites each).

### Finds filed
In `sweeps/order48/newitems48-std.json`, repros under `sweeps/order48/std-48/finds/`:
- **A?1:** the "any length" array impl head, which is A161's door.
- **B?1:** `impl [type T; 3] with X` cannot bind its element ("cannot find type 'T'"), although impl selection already binds through array elements.
- **E?1:** a fragment written directly inside another fragment gets the plain list-element mismatch, with no fragment hint.
- **A?2:** `null`'s type cannot be written (`let x: null = null;` is refused), yet error messages name it.
- **A?3:** should an `Option<View>` be allowed in a hole (as a `Slot`)?

I also hit F109 (already filed): `[T; n]` literals are emitted as `vec!` natively.

Nothing was blocked by a permission prompt.

`LANE-STATUS.md` in the worktree is current and untracked.
