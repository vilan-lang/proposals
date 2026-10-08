## editor-47 report

**Tip:** `0c258b4b` on branch `editor-47` (worktree `vilan/.claude/worktrees/editor-47`), not pushed. It sits on `origin/next @0af433fb`, after the solver-47 merge, which itself came after native-47 and docs-47.

**Bases:**
- Started from `c43d6ab9`.
- Rebased twice: onto `99285bc4` (docs-47 had moved the ledger, the docs and the CHANGELOG), then onto `0af433fb` (solver-47).
- All gate numbers below are from `0c258b4b` on `0af433fb`.

**incr-47 is not merged yet,** so I have not rebased onto it. A trial `git merge-tree` against `incr-47` conflicted only in `CHANGELOG.md`. Two of my analyzer edits sit in its area:
- E262 moves `resolve_context_clauses` inside `resolve_world`.
- E253 adds a field that `analyze_over_world` copies into `Program`.

### Items

| item | verdict | sha | what the cause really was |
|---|---|---|---|
| B536 (reorder fix) | FIXED | fb84b996 + 0c258b4b | `parsing::marker_order_fix` existed but was never wired up. The LSP now publishes `marker-order/*` codes, offers a quick fix per head, and offers a file-wide "Write all N declaration heads in the order". The splice logic shared by the three file-wide fixes moved into one `spliced_edit` helper. |
| B515/B535 (import-trait fix) | FIXED | 766ca2a0 + 0c258b4b | Offered on the B535 refusal and on the no-method steer. Each gets a per-call fix, a file-wide "Import all N traits this file calls", and is included in Add All Missing Imports. After solver's flip, the fix reads `analyzer::trait_scope_import` / `TRAIT_SCOPE_CODE`. The path written comes from the add-import candidate scan, because the message's own path is wrong for a nested pkg module (find B?1). |
| E253 | FIXED (premise wrong) | 243b9748 | The `context` clause was not the cause: the find's own program was refused (`MemoCell::new` does not exist). The real cause: a method call whose **closure argument's body is refused** waits on that closure's generic return to the end and never wires, so it leaves no record. The analyzer now keeps `Program::unwired_method_calls` (editor only), and hover/definition resolve through it. The ignored pin is un-ignored and now uses clean closures. |
| E263 | FIXED | d1cf0dd0 | Closure-literal parameter rewritten in the type's mode ("Take the parameter as `&str`"), or an adapter around a named one-parameter closure ("Adapt it: `\|c\| g(*c)`"). Lives in `vilan_ide::closure_mode_fix`. `book_sync` now reads `\|` in table cells. |
| E264 | FIXED | b7ae8628 | Completion filters `parsing::STEERED_ELEMENT_ATTRIBUTES`; `.autofocus` was already offered as a method. |
| E261 | FIXED | dca08f2d | A steer in `unify_arm_bodies` when both arms implement std's `Flow`. One ledger row `NEW`. |
| E262 | FIXED (premise partly wrong) | cec48ce7 | A program's own context clauses were written into their types only *after* conformance ran. `resolve_context_clauses` now runs just before conformance; inference and docs suites stay green. The premise "conformance refuses the copied line" is false: conformance never compares the clause (find B?4). B249's pin, which asserted the clause-less text, now asserts the clause. |
| E254 | NOT DONE | — | Deferred. It is a change to the LSP world/twin layer, which incr-47 owns and is rewriting now, and the owner ruled 2026-10-03 that it can wait for a later order. |
| E265 | FIXED | 06f8fffd | The printer wrapped an `if`/`match` in parentheses in every operand position, but after an operator it is an atom. It now prints bare after an operator and down the left spine of a right operand. Separately, the safety net named the wrong line: the line of a deleted trailing comma rather than the change. It now aligns the token streams across deletions so the decline names the right line. |
| N141 | FIXED | 97965ea0 | `assert_formats` now asserts that `reprint` succeeded. **None of the ten identity pins (or any other caller) turned red.** |
| E269 | FIXED | 170e7287 | A bare `import std::web;` resolved to the namespace and never reached the moved-path refusal; it now gets that refusal. The edit keeps the binding name (`prelude as web`). The same rule now aliases any moved leaf whose new last segment differs (`rpc_server` → `rpc::server as rpc_server`). A `self` in the old web brace list is fixed too, no longer left for a hand. |
| E267 | FIXED | b62197f5 | The auto-import walk and `import_candidates` now descend pkg's (and dependencies') nested modules, as they already did for std. |
| B560 (added) | FIXED | adc854cd | `import_steer_inner` built paths from the module's leaf name. It now builds every loaded module's full path (root scopes, then `module_children_scopes`) and compares hits by that path. That also fixes nested std modules, which were spelled `pkg::delta::ListCell`. |
| E270 (added) | FIXED | 7e440530 | The TextMate rule now also matches a line-leading `then` (`^\s*`) with the same right-hand guard. A leading `else` and the hljs theme were already fine. The LSP sends no semantic token for `then`, so the grammar's colour is what shows. |
| E121 rows | PENDING | — | Needs incr-47 merged and a quiet box (load was 13–22 all day). Not measured. |

### Pins (by name)
- **vilan-lsp:**
  - `marker_order_tests::*` (7)
  - `trait_import_tests::*` (8, including `a_nested_std_trait_is_imported_from_where_it_is_declared` and `a_nested_package_trait_is_imported_from_where_it_is_declared`)
  - `closure_mode_tests::*` (4)
  - `member_admission_tests::hover_on_a_call_taking_a_context_closure_names_the_member` (un-ignored) and `hover_on_a_call_whose_closure_is_refused_names_the_member`
  - `element_head_offers_autofocus_as_the_method_only`
  - `e270_a_line_leading_then_carries_no_semantic_token`
  - `a_nested_package_modules_item_is_an_auto_import_candidate_at_its_full_path`, `a_nested_package_modules_item_is_an_add_import_target`
  - `moved_std_path_tests::the_old_web_prelude_as_a_module_keeps_its_name`
  - `narrowed_edit_tests`
- **vilan-ide:** `trait_import::tests` (3), `closure_mode_fix::tests` (4).
- **vilan-core:**
  - `inference::dyn_objects::e261_*` (2), `inference::platform::e262_the_declare_steer_keeps_a_callbacks_context_clause`
  - `formatter::block_like_operands::*` (3), `formatter::reformats::an_identity_pin_over_a_declined_source_fails`
  - `parsing::e269_the_old_web_prelude_as_a_module_keeps_its_name`
  - `module_resolution::b560_*` (3)
- **vilan-cli:** `grammar_sync::e270_then_leading_its_line_is_coloured_in_both_grammars`, `check_fix::e269_the_web_prelude_imported_as_a_module_is_fixed_keeping_its_name`.
- **Existing pins I changed, deliberately:**
  - B249's clause text.
  - A154's three-file `--fix` pin now expects `rpc::server as rpc_server`.
  - The "for a hand" `--fix` pin now uses a reach marker instead of `self`.
  - parsing's E268 `self` case moved into the E269 test.
- Every new negative pin was planted red once.

### Decisions for you
- **E254:** I left it, per the owner's ruling and because incr-47 holds that layer. Confirm it carries to Order 48.
- **B?2:** an owner question. Spec R4 says `e.method()` auto-derefs any view, but a scalar view receiver (`n.abs()` with `n: &i32`) is refused.
- **E269 behaviour change:** `--fix` now writes `as <old>` for every moved module that is the import's leaf and whose new last segment differs. Today that is `web` and `rpc_server`.

### Finds (`sweeps/order47/newitems47-editor.json`, repros under `editor-47/finds/`)
- **B?1:** B535's import statement uses the leaf name for a nested *package* module (`pkg::shapes::Area`). solver-47 fixed the std half; `import_path_of` could reuse B560's path walk.
- **B?2:** a method on a scalar view is refused, contrary to transparent-references R4.
- **E?3:** a named *function* with a mismatched mode gets the generic mismatch instead of B495's steer, and so no adapter fix.
- **B?4:** conformance ignores a callback parameter's `context` clause, in both directions.

### Gates (tip 0c258b4b on 0af433fb)
- `cargo nextest run --workspace -j 6`: **9706 passed, 33 skipped**, exit 0 (load 12–20).
- Earlier passes: 9680 on c43d6ab9, 9686 on 99285bc4.
- clippy `--workspace --all-targets -D warnings`: clean.
- `cargo fmt --all --check`: clean.
- `ci-local.sh vilan-fmt`: green.
- `ci-local.sh windows`: green.
- `ci-local.sh perf`: T2 green, growth x1.939 (limit x2.3), local class with no ceilings. Not measured as a delta against my own base.
- VS Code extension: `npm test` 28/28 and `tsc` clean, run in a scratch copy using the main checkout's `node_modules` through a symlink.

### Functions touched
- **analyzer.rs:**
  - `Analyzer` fields and `new` (`unwired_method_calls`)
  - `resolve_method_call` (the Found arm records the member before each `Deferred`)
  - `wire_method_call`
  - `Program` and `analyze_over_world` construction
  - `unify_arm_bodies` and the new `erased_flow_arm_steer`
  - `resolve_world` (the `resolve_context_clauses` position)
  - `resolve_import` (the E269 namespace branch)
  - `import_steer_inner` (B560)
  - No new arms in `walk_expr_node_inner`.
- **parsing.rs:** `moved_std_module_edit`, new `import_tail_at`, `STEERED_ELEMENT_ATTRIBUTES`; `MOVED_WEB_SELF_REASON` removed.
- **formatter.rs:**
  - `diverging_span` and new `deletion_aligned_index*`
  - `print_split_right`, new `print_left_operand` / `print_bare_block_like`
  - the `Binary` arm, `print_split_binary_chain`
  - a new `Printer` field
- **vilan-lsp / vilan-ide:** `quickfixes`, `add_all_missing_imports_edit`, `import_candidates`, the hover/definition walks, `source_call_subject`, `hover_label`, publish codes, `AutoImportOrder::build`, `attribute_completions`.
- **Docs I edited despite the docs-47 ownership:** `book_sync` forces the editor appendix to match the server, so `vilan/docs/appendix/editor.md` changed; `appendix/cli.md` got a few lines for E269.

LANE-STATUS.md is current and untracked in the worktree.
