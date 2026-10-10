## lang-a-49: B569 named tuple fields. All four slices are done.

**Tip `574df2d4`** on branch `lang-a-49`, worktree `vilan/.claude/worktrees/lang-a-49`. Not pushed.
- Base: `origin/next` @`b04e912a`. I rebased first onto C3 (`77b23af2`) and then onto `b04e912a`, as you asked, and re-ran all the gates after the second rebase.
- Commits, one per slice:
  - `1a79bf8f` S1 (breaking)
  - `4b77f971` S2 (feature)
  - `e6c7e135` S3 (feature)
  - `574df2d4` S4 (feature)
- Each commit has its own `## Unreleased` CHANGELOG entry and `NEW` ledger rows. The ledger TSV is regenerated per commit, so every commit's tail is in order with no duplicates.
- `LANE-STATUS.md` is untracked and current.

### S1: DONE (breaking). An assignment is only legal where its value is thrown away
- **Where it lives:** the parser, in `assignment_head` / `parse_discarded` / `refuse_valued_assignment` in `parsing.rs`. Assignment stays legal as a statement, a block's tail, a `match` arm, a closure's expression body, and a `then`/`else` branch of a form that itself stands in one of those. Everywhere else it is refused with a message naming the statement to write. The tree keeps the assignment, so the rest of the file still analyzes.
- **Where the steers ended up:** after S2/S4, `name = value` inside parentheses is never an assignment.
  - The in-parentheses steer now fires on two cases instead: the statement `(x = 5);`, and a one-slot labelled literal landing where a non-tuple is wanted.
  - `takes(x = 5)` now gets S4's named-argument refusal, which names the assignment.
  - `const x = 3;` is left to the analyzer's existing `const let` steer.
- **Estate:** counted with the tree's own parser on this branch: **0 of 1,765 assignments need rewriting.**

  | Estate | Refused / total |
  |---|---|
  | std + macro_std | 0 / 1,154 |
  | corpus + crates | 0 / 494 |
  | examples | 0 / 9 |
  | kolt working tree (a `cp -r` copy) | 0 / 91 |
  | website `src` | 0 / 17 |

  Every docs fence still compiles.
- **Pins:**
  - `parsing::tests::b569_an_assignment_stands_where_its_value_is_discarded`, `b569_an_assignment_is_refused_where_its_value_is_used`, `b569_a_multi_line_assignment_is_steered_by_its_place`
  - `named_tuples::b569_assignment_runs_wherever_its_value_is_discarded`, `b569_an_assignment_used_as_a_value_is_refused`
  - native `b569_assignment_in_a_discarded_position_is_identical_on_both_backends`
  - The `parse_expr_regression` assignment fixtures moved to the decliner list plus whole-file statements.

### S2: DONE. Labels on a tuple's positions
- **Representation:** `Type::Tuple(Vec<TypeId>, TupleLabels)`, defined in `type_.rs`. `PartialEq` always answers true and `Hash` writes nothing, so labels are carried but never compared, and mono can never split an instance on them. The settled-type interner in `type_id_for_type` only shares a slot when the labels also print alike.
- **Syntax:** `Node::Labelled` covers both a type slot (`x: f64`) and a literal entry (`x = 5`). The parser enforces every slot labelled or none, and each label once.
- **What the analyzer does:**
  - **Literal by name:** the tuple rule in `infer_type_path` matches a labelled literal by name and records the layout in `tuple_literal_layouts`. Both emitters evaluate the entries in the order written, then store them in the type's order (JS: `const` spills in the transformer's Tuple arm; native: a `{ let … }` block).
  - **Reconcile:** two differently ordered label sets are refused when a label sits at a different position, in both `reconcile_type` and `compare_type_rigid`.
  - **Messages and quick fixes:** `type_mismatch_message` names the label that moved, and `with_label_contradiction_fixes` spells both rewrites when the value is a place. The editor offers them as two quick fixes (new `vilan_ide::tuple_label_fix`, wired into `document.rs`'s quick fixes).
  - **Member access:** `p.x` reads and writes the slot (`tuple_element` / `resolve_field_accessor`).
  - **Other:** label refusals are reported by the new pass `check_tuple_literal_labels`. The printer, hover and inlay hints print labels. A mapped tuple keeps its source's labels (`substitute_type`, `invert_mapped`). An `impl` on a labelled tuple is refused in `walk_impl_entity`. The formatter prints labels.
- **Pins:**
  - `named_tuples::b569_*` (14)
  - parser grammar pins
  - LSP `named_tuple_tests` (hover, both fixes, the rename case)
  - native `b569_labelled_tuples_are_identical_on_both_backends` and `b569_labels_never_split_a_native_instance`
  - I planted the bug by disabling the native layout, and the native pin went red.
- **Contract hash:** nothing new is pinned for tuples, because on this tree **no tuple can reach a contract**. The `[rpc]` and `[derive(Wire)]` checks are syntactic and refuse a tuple (finding B?2 below). All the existing B525 hash pins are unchanged and green. The renderer's tuple arm reads elements only.
- **Tuple blankets:** `PartialEq`, `Hashable` and `Debug` still apply to labelled tuples (pinned).
- **Where the paper was wrong about the tree:**
  - "A join checks later arms against the first arm as today" is not true: arms are typed only against their expected or peer type. I built it: a labelled first arm becomes the constraint for later arms.
  - A concrete tuple comprehension is not a thing (spec §5.9). Labels ride only on mapped-family expansion.
  - `Debug` for tuples already exists (B443, Order 48) and prints positionally.
  - The paper does not say what order a by-name literal evaluates in. I built evaluation in the order written.
  - M108 interns types after they settle, so the interner needed the label-aware share described above.
  - The paper estimated ~126 + 13 `Type::Tuple` sites; the real count is 159 in vilan-core plus 25 in vilan-rust.

### S3: DONE. Patterns by name, and labels in `dbg`
- **Patterns:** `let (y = top, x = left) = p;`, `(x = 0, y = let v)`, `is`, `for` binders, and the one-slot `(x = a)` all work. `Pattern::Labelled` maps to `WalkPattern::Labelled`, and `resolve_by_name_tuple_pattern` places each element at its label's slot, so everything downstream sees an ordinary positional pattern. The pattern must name exactly the value's labels.
- **`dbg`:** prints `(x = 5.0, y = 7.0)`.
  - `printer.rs`: the tuple arm of `shape_of` now carries each entry's opening text, plus a new `printer::label_key`.
  - In debug-49's files I changed only the key line and the Tuple arm of `transformer/dbg.rs::printer_for` and of `vilan-rust/src/dbg.rs::native_printer_for`.
  - A tuple printed inside a generic body prints positionally (labels erased), whatever order the instances were created in.
- **Pins:**
  - `named_tuples::b569_a_pattern_destructures_by_name`, `b569_a_by_name_pattern_is_checked_against_the_labels`, `b569_dbg_prints_labels_where_they_are_written`
  - native `b569_labels_print_and_destructure_the_same_on_both_backends` (committed goldens `native/dbg_labels.*`)

### S4: DONE. Named arguments through a spread parameter
- **What works:** `draw(x = 1, y = 2)` and `draw(y = 2, x = 1)` against `...at: (x: f64, y: f64)`.
  - It builds on B581's door (a): the collected pack is the labelled literal.
  - Arguments are evaluated in the order written.
  - A fixed parameter before the pack is passed by position.
  - A one-slot pack works.
- **Refusals:** the pack's arguments must be all named or none (checked in `collect_spread_arguments`). A name that no pack collects is refused by the new pass `check_named_arguments`. There are no defaults.
- **No signature-help popup exists**, so the call completion's tab stops are the labels instead (`vilan_ide::call_parameter_names`).
- **Pins:**
  - `named_tuples::b569_a_spread_parameter_takes_named_arguments`, `b569_named_arguments_are_checked`
  - `parsing::tests::b569_an_argument_may_be_named`
  - LSP tab-stop pin
  - native `b569_named_arguments_are_identical_on_both_backends`

### What C3 asked for
- New fixture `LABELS_FIXTURE` in `replay_harness/packages.rs`, plus `edit_replay_differential::b569_a_reused_modules_tuple_labels_render_as_a_clean_analysis_renders`. A reused prefix module with labelled returns and bindings, a by-name literal and pattern, a named-argument call and a label refusal renders the same as a clean analysis, both on keystrokes elsewhere and on an unseeded hit. It is green.
- The two new passes read their tables and never take them. A plant that made them destructive did not turn the pin red, so table persistence is not load-bearing today.

### Perf (instructions:u, base `b04e912a` against tip, quiet window)
- Every row is between +0.07% and +0.29%, under the 0.5% line. T2 verdict green; growth x2.020.

  | Row | Change |
  |---|---|
  | math | +0.282% |
  | watch | +0.267% |
  | genapp:46 | +0.225% |
  | browser | +0.198% |
  | plain:160 | +0.099% |
  | plain:320 | +0.079% |

- Measured on the rebased tree, S2 alone is about +0.12% and S3+S4 add about +0.16%.

### Gates
- **Full suite on the final tree: 10,039 tests.** 10,037 passed. The other two, both in `diagnostics_ledger`, failed on a duplicate left in the ledger TSV by the rebase. I deduplicated it (the only change after that run) and re-ran that binary: 25/25 green.
- Native differential in full-corpus mode: 229/229.
- `fmt` and `clippy -D warnings` clean.
- `markdown_anchors.golden` was regenerated with mdbook 0.5.4 for three new headings.

### Docs and other files
- Updated: grammar.md (§3.4, §3.6, §3.9, §3.10), types.md (§5.1 and a new "Labelled tuples" section under §5.9), the tour (values-and-types, functions-and-closures, memory-model).
- Two files I did not own:
  - `context.rs:796` (incr-49's) needed a one-token `, _` because the variant changed; it was forced to compile. The same edit hit `mono.rs` and `const_eval.rs`.
  - I edited the pass map in proposals (uncommitted, for you to commit) with one new row for the two passes.
- Ledger row 229's count in the proposals prose needs updating: `RULE_STATEMENT_SITES` went 62 → 64.

### Findings filed
In `sweeps/order49/newitems49-lang-a.json`, repros under `sweeps/order49/lang-a-49/finds/`:
- **B?1 (miscompile):** a struct literal evaluates its fields in declaration order on JS but in written order natively, so the two backends disagree on side effects.
- **B?2 (diagnostics):** a tuple-typed `[rpc]` parameter or `[derive(Wire)]` field is quoted as `_` in the refusal. This is `render_type`. Widening it breaks the derive's generated code, so it needs a separate quoting path.
- **F?1 (native gap):** `draw(..(3, 4))`, a spread of a tuple literal, is refused natively but runs on JS. This was already true on base.

### Questions for the owner, with my recommendations
1. **By-name literals evaluate in the order written** (built that way; the paper was silent). Keep it, and fix struct literals (B?1) to match.
2. **The join rule:** a labelled first arm constrains later arms (built). Keep.
3. **`dbg` inside a generic body erases only the outermost tuple's labels.** A labelled tuple nested inside a substituted type still shows its labels, which may belong to whichever instance was emitted first. Accept for now; full erasure needs the instances' substitutions erased in both emitters.
4. **Named-argument completion** inserts positional placeholders named after the labels. Keep it; consider a `x = ${1}` snippet later.
5. **A by-name pattern must name every label**, like a literal does. Keep; a rest form (`..`) would be its own item.
6. **No corpus program for labelled tuples**, to avoid moving the three censuses. Add one at the seal if you want corpus-level coverage.
