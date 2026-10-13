## editor-52: final report (Order 52, Opus 5.5)

**Branch `editor-52` in `vilan/.claude/worktrees/editor-52`.** Base 697c9517, tip **623ff568**, 20 commits. Nothing pushed. `editor-52-STATUS.md` is untracked. No processes are left running: the temporary base worktree I built for measurement has been removed.

### Commits

| sha | item | family |
|---|---|---|
| b661b48d | E313: a module view reads its own hover rows | fix |
| adc044d7 | E305: head event/attribute names hover as the link they lower to | fix |
| eff097ed | E303: element heads mint no stage hints (RULED: hide) | fix |
| 6d0f252c | E311: a function reached through a path paints as Function; TextMate css argument lists balance | fix |
| 3d5e7988 | E299: `mod` line on every function hover | feature |
| ada5cb4c | E298: a module segment hovers as its module | feature |
| be7f5f38, d3237033 | E307: field hover names its owning struct (second commit fixes one pin E307 missed) | feature |
| 83ffb2e4 | E304: a label always states its return type (`: void` / inferred) | feature |
| 908e2039 | E308: pins only | fix |
| c0a7037e, 623ff568 | E310: trait in a parameter type, with its implementors in reach; the implementors list is computed for the editor only | feature |
| 8ca5865c | E312: a derive answers with the impls it writes; two-facet import leaf; refused derive leads with the refusal | feature |
| 19a5fdde | E306: variant in value position, with its enum chunk | fix |
| 2de37a46 | E300: match arm fence (`match on T` / variant / captures) | feature |
| 9f184a6b | E301: inlay hint tooltip and type-name click, via `inlayHint/resolve` | feature |
| eb2b5ed6, b2394a8d | E302: `vilan.inlayHints.chains = "changes"`; book appendix updated | feature |
| fb96f28b | B620 editor half: non-View head methods only at 3 typed characters | feature |
| 4ec00da4 | N172: `[build] dbg` in the schema and manifest completion | tooling |

Every commit has a `## Unreleased` CHANGELOG entry with a family marker.

### Functions changed in the analyzer core (listed arms; tell incr-52a)
- **`analyzer.rs`:**
  - `resolve_pattern`: pattern sites are now recorded for every non-std file.
  - `analyze_over_world`: the call-signature loop filters by file; the hover-row tail takes `HoverRows`.
  - `render_function_signature` (E304): falls back to `inferred_return_types`.
  - New field `Workspace::generated_root`, and doc changes on the Program fields.
- **`analyzer/hover_labels.rs`:**
  - `PatternSite`, `PatternLabel` and `ReferenceHover` now carry a source.
  - New: `HoverRows`, `banks_hover_rows`, `renders_hover_rows`, `implementors_in_reach` (reads `trait_reach_by_file`).
  - Changed: `record_pattern_variant`, `record_pattern_wildcard`, `pattern_labels`, `reference_hovers` (adds the implicit-parameter arm and `implemented_by`), `generic_owners`, `type_definitions` (a type parameter's definition block is no longer shared by rendered label).
- **`analyzer/written_types.rs`:** `stage_hints`, plus a new `element_link`.
- No changes to `mono.rs` or any emitter. Late writes are unaffected.

### Where the premises were wrong
- **E313:** no entity span starts inside a word. The real cause is that the hover rows (E241 patterns, E240 type-position names, E237 definitions, E206 call labels) were rendered for the entry file only. Since M104 an open module is served as a view of its entry's world, and the view read the entry's rows at its own byte offsets. In kolt, `channel.vl`'s `cut` picked up a `None` pattern written in `client.vl` at the same bytes.
- **The same cause** was behind E305 (`on:`/`.styled` answering `RpcError::Unauthorized`), E308 (the second line already existed in a file's own analysis; empty own-substitution was not the problem), E306's binding half (the kolt sweep now reads 57/57 enum bindings with their chunk), E300's bare `Option`, and part of E310/E312.
- **E305:** the desugar's spans were fine. Only the event and attribute names needed work: they are minted string literals.
- **E311:** the server-side gap had nothing to do with css. `Type::f()` went unpainted everywhere, because the call's entity spans the whole path and lost to `Theme`'s type token where they overlap. The TextMate gap was real: a nested `)` closed the argument list early.
- **E307:** there are no struct-variant enums in vilan, so that case does not exist.
- **E303:** the doubled hint came from the element's own last link and the parent's `.child(..)` link, which both end at `/>`.

### Gates
- **Full suite** (`--cargo-profile ci-test -E 'not binary(deep_nesting)' -j 6`): 10541/10542. The one failure was `book_sync::editor_page_settings_are_the_extensions` (the book's settings table lacked `inlayHints.chains`), fixed in b2394a8d and green on rerun. Within that suite: corpus 14, check_scope_differential 16, native_differential 270, ci_ignored_pins 12, hygiene 3.
- **Native differential, sweep mode:** 270/270.
- **vilan-lsp binary at the tip:** 1126/1126.
- **Deep-nesting canary at 1536 KiB:** 18/18.
- clippy, `cargo fmt --check` and `vilan fmt --check .` are clean. Docs and book_mirrors 14/14. The extension's `npm test` passes 28/28 and `tsc` is clean.
- **`perf_gate` against a base built the same way:** cold rows +0.003% to +0.083%, growth ×1.93, T2 green. I added no `[[bump]]` row; this is within the 1% tolerance.
- **kolt cold check RSS (medians):** base 277.9 / 275.2 MB, tip 275.8 / 275.7 MB.
- **lsp-latency on kolt, keystroke columns** (hover / completion / inlay / tokens, wall ms): unchanged within noise, e.g. leaf 3.2/1.1/0.4/0.5 → 3.0/1.1/0.4/0.5.
- **lsp-latency, cost of an edit:** the analysis now costs more. Instructions to idle rose +1.3% (leaf and world-mode rows) and +0.6% (css), and VmHWM rose 816 → 843 MB. Both come from rendering the hover rows for every file of the world; see find M?1.
- **New ignored kolt probes and sweeps** (all reasons start with the tracker id; set `VILAN_EDITOR_KOLT` to run): `kolt_probe`, `kolt_hint_probe`, `kolt_token_probe`, `kolt_no_hover_splits_a_word`, `kolt_no_hover_span_starts_inside_a_word`, `kolt_every_enum_binding_hovers_with_its_chunk`. All are green on the kolt copy.

### Finds
Filed in `proposals/scripts/integration/sweeps/order52/newitems52-editor-52.json`. The brief names `order51/editor-52/finds/` for repros; I used `order52/editor-52/finds/` (the directory that exists), and it is still empty because every repro lives in a test.
- **E?1:** a type in the middle of a module path (`style::Length::px`) gets no token.
- **M?1:** the hover rows are re-rendered on every keystroke for every file; S2b-style records would spare the files not being edited.
- **E?2:** a signature drops an implicit parameter's trait arguments (`username: Signal` instead of `Signal<str>`).
- **E?3:** a returned `None` hovers as `Option::None`, without the instantiation.

### Questions for the owner
1. **M?1:** the hover-row cost (+1.3% instructions per keystroke, +27 MB peak on kolt's world). I recommend recording these rows per module under S2b in the incremental lane next order, rather than restricting them to open files: a module opened into an existing world is served without re-analysis, so an open-files rule would leave it without rows.
2. **Generated files:** kolt's `src/lucide` (the declared `generated` root) renders no hover rows. It holds 17,601 of the world's 23,042 generic call sites. I recommend keeping that.
3. **E301 needs `inlayHint/resolve`:** a client without resolve support sees only the plain tooltip of an abbreviated type. I recommend keeping it this way, which keeps the keystroke path flat.
4. **E304 changes a diagnostic's text:** the conformance steer's suggested declaration now carries `: void` or the inferred return type too. I recommend keeping it; the result is still valid code.
5. **E299 entry spelling:** an entry file reads `mod pkg::client`, and only a file outside any package reads `mod pkg`. I recommend keeping it, since that is how siblings spell the module.
6. **E300 `is` tests:** an `is` test reads `match on T` like a match leg, as the item asked. Keep that, or say `is on T`? I recommend keeping it.
7. **E310 `[hint]`-host note:** not implemented. I recommend filing it when a hinted trait needs it.
8. **The rebase onto incr-52a's C1** will meet my arms in `analyze_over_world`, `hover_labels.rs` and `written_types.rs`. I'll rebase and re-run the full gates when you say.
