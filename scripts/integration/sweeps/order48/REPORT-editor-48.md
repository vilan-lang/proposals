## editor-48 report

**Tip:** `d0cbdc7d` on branch `editor-48` (worktree `vilan/.claude/worktrees/editor-48`), not pushed. **Base:** `origin/next @e75bc57c`. I fetched just before this report and next has not moved, so I have not rebased onto incr-48 yet. Every number below is from the tip on that base.

Five of six items are done; **E254 is held**, because it needs a pass-driver fix that belongs to incr-48. On the way to E254 I found a **miscompile**: a module's platform-fenced twins are compiled under the wrong platform.

### Items

| item | verdict | sha | the real cause |
|---|---|---|---|
| **E279** sticky spans | DONE (premise mostly wrong) | 57f6a80f | Most of it already existed. Diagnostics were already shifted and republished at once (E242), hints already followed edits (E232), and semantic tokens already used the delta protocol over the keystroke anchor. What was missing: **caret requests** (hover, definition, references, the completion leg pick) converted the live position through the *analyzed* index, and the **outline** was drawn in analyzed coordinates. Both were pinned as S1's "answer the analyzed snapshot", so a line typed above the caret answered about the line above it. **Quick fixes** were refused outright while stale. And a diagnostic's same-file related information did not follow the edit. |
| E254 | **HELD — blocked on B?1** | — | Built and pinned, then reverted to a patch, because it needs a driver change. Details below. |
| E273 | DONE | 09f49539 | `closure_mode_mismatch_message` only matched a closure type on both sides. A function item is `Type::Function`, so it fell through to the generic mismatch. It now reads the function as the closure type it coerces to and names it ("the function `count` takes …"). The editor offers the one-parameter adapter. Ledger row 632 already covers the wording, so no new row. |
| E274 | DONE | bc546510 | The member table grouped impls by nominal type only. Each member now carries its impl's subject, and a typed receiver keeps only the impls the solver selects (`impl_select::applying_implementations`), one per name. It falls back to every impl when the receiver selects none. |
| B561 | DONE | 6a927be9 | `import_path_of` used the module's leaf name. B560's path walk is now a shared `module_import_paths`, used by both the steer and this refusal. |
| B572 | DONE (premise partly wrong) | d0cbdc7d | std's export index now records re-exports and spells each name at its shortest public path; a re-export wins a tie, and two re-exports tied at the shortest leave the declaring module. The editor's add-import candidates use the same rule. **Wrong premise:** `vilan check --fix` writes no imports at all. **Knock-on:** `std::reactive::delta`'s names now steer to `std::reactive::ListCell` / `SequenceCell`, which is the spelling the book uses. B560's std pin and editor-47's nested-std-trait pin were changed deliberately to match. |

**E254, what blocks it and what is saved.**
- **The blocker (B?1):** `analyze_inner` walks the modules and selects their twins *before* `analyzer.platform = platform` is set (around analyzer.rs:74938 vs :75715), so module twins are chosen under the default platform. Moving that one line up fixes it; I verified this, but did not commit it because `analyze_inner` is incr-48's.
- **Why not ship E254 alone:** a twin file served from a world would then show the wrong twin. Today it is analyzed as its own entry, which selects correctly.
- **What is saved:** the full patch, about 314 lines, is at `sweeps/order48/editor-48/e254-held.patch`:
  - `world.rs` routes a twin file to its primary entry's world, unless no reaching entry's platform admits one of its twins.
  - `view_of` records the twins that world fences out.
  - `Document::twin_leg_from` and `install_twin_legs` build the legs.
  - `attach_twin_legs` runs in `land_world` after the views land. It reads `analyze_world`'s existing output and changes nothing in the drivers.
  - Its two pins pass with the one-line fix applied.

### Pins
- **E279** (all red when the old behaviour was planted back):
  - `sticky_span_tests` (15 tests, new file). They cover:
    - a line typed above / text before on the same line / an edit inside (grows, then truncates) / after / across one end of a diagnostic, each with `analyses.counts()` at zero;
    - hover, definition, references and the outline on the live lines, through an edit log and through a whole-text replacement;
    - a quick fix carried along, and one withheld;
    - Organize Imports alone still refused.
  - `keystroke::tests::e279_*` (4) and `publish::tests::e279_related_information_in_the_same_file_follows_the_edit`.
  - Nine existing pins were rewritten to the ruled contract: five S1 "analyzed snapshot" pins (hover, member hover, definition, references, symbols) and four code-action refusal pins.
- **E273:** `inference::borrows::e273_a_named_function_with_the_other_mode_gets_the_mode_steer`, `closure_mode_tests::a_named_function_is_adapted`, `closure_mode_fix::tests::a_named_functions_refusal_is_read_and_adapted`.
- **E274:** `completion::tests::e274_a_store_handle_is_not_offered_another_instantiations_projections`, `e274_an_inherent_impl_at_other_arguments_is_not_offered` (red with the filter planted off).
- **B561 / B572:** `module_resolution::b561_a_nested_package_traits_import_is_spelled_at_its_full_path`, `b572_a_reexported_std_name_is_steered_to_its_public_module`, `trait_import_tests::a_reexported_std_name_is_imported_from_its_public_module` and `a_nested_std_trait_is_imported_from_its_public_module`. All were planted red.

### E279 latency (kolt `views.vl`, leaf keystroke)
- **Setup:** release build at 57f6a80f, 5 runs, on a `cp -r` kolt copy with one planted type error so a shifted set exists to publish. Load average was 19–27 because other lanes were running.
- **`didChange` to the shifted publish:** median **6.6 ms** wall (runs: 23.9 / 8.5 / 6.6 / 0.5 / 0.5).
- **`didChange` to the analysed publish:** median **1551 ms** wall, **1240 ms** CPU, 5.36 G instructions.
- The keystroke path stayed at or under 2.4 ms per request.
- The shifted publish itself is E242's existing mechanism; E279 adds the caret and quick-fix half.

### Decisions for you
1. **B?1** is a miscompile in incr-48's driver with a one-line fix. E254 can land from the held patch after that fix.
2. E279 changes S1's ruled behaviour for caret requests and quick fixes. That is what E279 asks for, but it overturns an earlier ruling. Rename and Organize Imports alone still decline while the buffer is ahead of the analysis.
3. B572 moves the steer's spelling for every name `std::reactive` re-exports from `delta`.

### Finds (`sweeps/order48/newitems48-editor.json`, repros in `sweeps/order48/editor-48/finds/`)
- **B?1 (miscompile):** a module's twins are selected under the default platform, so a browser bundle ships the `@process` twin. Root cause and fix are above. Repro: `module_twin_platform/`.
- **B?2:** a generic bound naming an unimported trait (`fun keep<T: Storable>`) gets no import steer. Repro: `bound_trait_steer/`.
- **E?3:** a file opened into a world another document already holds (`serve_from_held_world`) never has its further worlds analyzed, so the node leg's diagnostics are missing until the next edit. I found it by reading the code and confirmed in an LSP test probe that no kept world exists afterwards. The repro (`held_world_further/`) is the open order; no single file there shows a visible diagnostic.

### Gates (tip d0cbdc7d on base e75bc57c)
| gate | result |
|---|---|
| `cargo nextest run --workspace -j 6` | **9802 passed, 34 skipped**, exit 0 (load about 20–27) |
| `native_differential` with `VILAN_NATIVE_DIFFERENTIAL=1` | **177/177** |
| clippy `--workspace --all-targets -D warnings` | clean |
| `cargo fmt --all --check` | clean |
| `ci-local.sh vilan-fmt`, `windows`, `perf` | all green; T2 green, growth x1.938 |
| VS Code tests (scratch copy, main checkout's `node_modules` via symlink) | 28/28, `tsc` clean |

No load generators are left running, and I ran no git command in kolt. `LANE-STATUS.md` is current and untracked.

### Functions touched
- **analyzer.rs** — beyond the two steer functions the launcher named:
  - `closure_mode_mismatch_message` (E273, which the item requires);
  - `build_std_indexes_if_needed` (B572's re-export index);
  - `import_steer_inner`, `import_path_of`, and the new `module_import_paths`.
  - Nothing else; there is no late-write impact.
- **vilan-lsp:**
  - `main.rs`: the hover, completion, goto_definition, references, rename and document_symbol handlers; `location_for`, `location_for_path`, `to_lsp_symbol`, the new `edit_trails`, `code_action`.
  - `document.rs`: new `edit_trail`, `request_offset`, `live_range_of` / `live_range_through`, `live_quickfixes`, `live_add_all_missing_imports_edit`. The quick-fix helpers now read the analyzed text. `import_candidates` gained the facade rule.
  - `keystroke.rs`: `EditTrail::follow_span`, `follow_untouched`, `back`, `back_span`.
  - `publish.rs`: `follow_edit` (related information).
- **vilan-ide:** `completion.rs` (`MemberTable`/`TableMember`, `push_methods`, `nominal_member_completions`), `closure_mode_fix::mismatch`.
- **Docs:** `appendix/editor.md`, `spec/names.md`.
- **E121:** not re-checked, because N150 has not landed.
