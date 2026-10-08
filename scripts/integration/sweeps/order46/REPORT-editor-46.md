The editor-46 branch tip is **d98c22ef** (d98c22ef1a4c6e843cced8c0f84ef82de5e361fe), rebased onto origin/next @71cd1731 after syntax-46 merged. That is seven commits, nothing pushed. M104's acceptance is met: with `model.vl` and its three importers open, a keystroke now runs one analysis and every open file settles at 1.03x the single-document instruction count (41.61 G → 14.70 G). The cost is that a keystroke in a module open alone got slower, because it now pays its entry's whole world. That is the main thing for the owner (point 1 below).

I was not allowed to write `REPORT-editor-46.md`, so the full report is below; please save it under `sweeps/order46/`. New finds are in `proposals/scripts/integration/sweeps/order46/newitems46-editor.json` (placeholder ids E?1–E?4, B?1). `LANE-STATUS.md` in the worktree is untracked.

## Status per item
| item | status | sha |
|---|---|---|
| M104 entry-world analysis | Landed; acceptance met | 8f914dbd |
| M101 | Re-measured. Two editor-table cuts landed with M104. What remains is const-eval, which is not this lane's. | 8f914dbd |
| E245 | Re-measured; not reproduced. Idle hover is 1.4 ms on the base and 2.1–2.6 ms on the tip, under E121's 10 ms. | — |
| E249 blanket-impl members in completion | Landed | 874e033c |
| E250 import fix at every position | Landed (census below) | 9f6e56e7 |
| E251 Organize Imports removes duplicates | Landed (code action only) | aa6bc892 |
| E246 hover shape under a rule, after the docs | Landed | 7fa703f4 |
| E247 (R-a) status bar menu, and E248 stop/start | Landed | 6fb51c61 |
| B520 quick fixes (editor half) | Landed after the rebase | d98c22ef |
| E214 | Nothing to build. editor-43's overtype pins still pass on the tip; it closes at the owner's word, as its stamp says. | — |

## Headline numbers
Method: `scripts/lsp-latency.py --kolt ~/code/kolt --commit 984a1dfb --runs 5`, profiling builds, medians. The base run was at load 5; the tip run was at load 9–16 with four other lanes going. Instructions are the figure to compare; CPU ms is inflated by load on this host.

| edit | base fe092e8d: CPU ms / instr G (analyses) | tip d98c22ef: CPU ms / instr G (analyses) |
|---|---|---|
| model.vl + 3 importers open — every open file settled | **6230 / 41.61 (4)** | **2920 / 14.70 (1)** |
| model.vl alone | 300 / 2.37 | 2590 / 14.26 |
| leaf keystroke (views.vl) | 1140 / 9.27 | 2090 / 14.35 |
| leaf keystroke + 3 s pause | 2840 / 21.92 (3) | 2420 / 16.90 (2) |
| shared.vl (both entries' worlds) | 370 / 2.82 | 2170 / 17.50 (2) |
| css keystroke | 1510 / 10.10 | 2300 / 14.25 |
| opening model.vl beside its importers | 740 ms | 80 ms |
| peak memory (VmHWM) | 1027 MB | 874 MB |

- **No stale world:** a world whose analysis read an open buffer that has since moved lands on no document and publishes nothing. A deterministic pin covers it, and it goes red with the check removed.
- **Completion keystroke path:** 0.9 → 2.7–4.9 ms. This is E249's call into the solver, memoized per program per receiver type, so the first completion after each analysis pays it. Still under 10 ms.

## Needs the owner's ruling
1. **The single-document cost moved the other way, as the M104 ruling implies.** A keystroke in a module open on its own now pays its entry's whole world:
   - `model.vl` alone: 2.37 → 14.3 G.
   - `shared.vl`, which both entries reach: 2.82 → 17.5 G (it pays both worlds).
   - Time to the module's own diagnostics rises with it; E242 keeps squiggles on their code meanwhile.
   - The biggest lever left is M101's const-eval cache: about 16% of each analysis, and it still needs the const-eval.md §4 design.
2. **E?4 — where `self as name` sorts.** E251 merges an aliased module import as `self as j`, as ruled. The printer's E146 rule sorts it among the names (`{ Json, JsonValue, self as j }`), while E251 says `self` goes first. Ranking it first would change `vilan fmt` output in syntax's formatter.rs.
3. **Twin files keep their own analysis under M104** (filed as E?2). A file holding platform-fenced twins is not yet served from an entry's world; kolt has none.

---
## Full report

### M104 — what was built
- **Which world (`world.rs`, `RootResolver`):** worked out from the manifest and the import graph, using the same walk platform colouring takes.
  - The primary world is the first entry in build order (browser first) that reaches the file.
  - Further worlds are the first reaching entry of each other platform, which keeps E113's legs.
  - A file keeps its own analysis when it is a declared entry, no entry reaches it, it is outside any `[package]`, or it holds twins.
- **Serving a module from its entry's program (`Document::view_of`):** a view's "focus" is the module's own source in the entry's program.
  - `AnalyzedProgram` is now shared through an `Arc`, and its memory is reclaimed when the last holder lets go.
  - Shared across a world's views: the program, the reference index, platform requirements, and the program-wide half of the completion index (`CompletionIndex::sharing_world`). Import edits stay per document.
  - Every `SourceId(0)` that meant "this document" now reads the focus. vilan-ide's `Analysis` gained a `focus` field; `entity_spans` takes the focus; the playground passes `SourceId(0)`.
- **Server (`analyze_world` / `land_world`):**
  - One analysis per world, landing a view on every open document whose primary world it is.
  - A keystroke in any of a world's documents is scheduled under the entry's key, so a burst of typing is one analysis per world.
  - Worlds of closed entries are kept in `Backend::worlds` while a document they serve is open, and retired at the last close (diagnostics cleared, schedule closed). An entry that closes while it still serves open documents moves its analysis to the kept worlds.
  - The entry owns and publishes every diagnostic in its world; a view publishes only its own paint (unused imports, dead code). A closed entry publishes no paint.
  - The dependency sweep answers each world once, re-analyzes a document its old world no longer reaches, and creates further worlds that should exist.
  - Opening or refocusing a file of a world another document already holds builds its view without analyzing.
- **M101's share:**
  - The union leg's reachability walk (about 0.28 G per analysis) now runs only when the dead-code clock asks for it.
  - `ReferenceIndex::build` sorts with an unstable sort by key; the stable sort was 0.29 of its 0.33 G.
- **Pins:**
  - `entry_world_tests`:
    - one analysis for four open documents, and the same with the entry closed;
    - diagnostics owned by the entry's world;
    - the deterministic stale-world pin;
    - break-and-fix rounds;
    - an orphan module keeps its own analysis;
    - a world's lifetime and retirement;
    - both legs of a shared module;
    - opening a file of a held world analyzes nothing;
    - the E247 platform answer.
  - `world::tests` covers root resolution and a view's hover, hints, tokens and refusals.
  - Two pins are proven non-vacuous: the stale-world pin and the closed-entry count go red when their fix is removed.

### M101 / E245 — what is left
- Callgrind of a client-world keystroke on the tip (shares are for the two analyses in the window):

| part | share |
|---|---|
| `analyze_over_world` | 35.8% |
| `post_analysis_passes` (const-eval alone: 16%) | 30.5% |
| `resolve_world` | 19% |
| `platform_color::check` | 3.2% |
| union-leg walk (now deferred) | 3.0% |
| `ReferenceIndex::build` (sort fixed) | 1.8% |
| `capture_landed` | 1.6% |
| `refined_edges` | 1.5% |

- Editor tables are now about 5% of a keystroke; the rest is the analysis core (perf-46) and const-eval.
- E245 did not reproduce. My hypothesis is that a hover which moved focus paid M63's release plus the allocator trim; M104 now serves a refocused document from its held world.

### E249 — which receivers missed, and why
- It was not the nested `type T` binder. The editor's member table grouped impls by the nominal type their subject names, so no blanket member was ever offered on any receiver.
- Members that were missing everywhere:
  - `switch_some` / `and_then` / `flatten` (`Flow<Option<type T>>`);
  - `distinct` / `switch` / `track` (`Flow<type T: PartialEq>`, `Flow<type T>`);
  - `then_some` (`Flow<bool>`);
  - a user's own `impl type T: PartialEq with Same` on an `i32`.
- Fix: completion asks the solver's existing selection, `impl_select::applying_implementations(program, Some(focus), receiver_type, None)`. That is a read-only call to an existing function, so I added no new solver entry point.
- Hover on a blanket member's call already worked; the server has no signature help to miss.
- New find E?1: hover and go-to-definition answer nothing on a call whose argument is a closure with a `context` clause (`switch_some(|v| ..)`, `switch`). The analysis leaves no entity record for the call. Pinned `#[ignore]`d.

### E250 — position census
- **Already worked:**
  - expression: `cannot find 'X'`;
  - annotation, generic argument, bound, impl subject, static-call receiver, variant type, parameter and return type: `cannot find type 'X'`.
- **Fixed now:**
  - struct literal head: `unknown struct: X`;
  - `match` and `is` pattern heads: the message names the whole path, so the fix takes its head;
  - an impl's `with` trait: `cannot find trait 'X'`.
- **Not positions:**
  - `[derive(X)]`: a std derive resolves with no import (pinned clean);
  - an element tag is a string lowered to `view("tag")`;
  - `let` takes no path pattern.

### E251
- **What merges:**
  - identical statements collapse; `export`, `use` and `only` stay distinct;
  - a repeated name in a group drops;
  - a line over a module that has a brace group joins it;
  - a module import beside a member import merges into `{ self, … }`, and `self as j` keeps its alias.
- **What stays as written:**
  - an alias is not a duplicate;
  - distinct single members with no group stay separate lines, as the existing canonical pins require;
  - statements with trailing comments, reach markers, selectors or nested paths.
- The result is idempotent.
- Two older pins now expect `pkg::a::{ self, b }`, per the GO revision.
- The merge sits in syntax's formatter.rs: one new function plus one call in the organizer. It rebased clean.
- New find E?3: a duplicate import carries no warning.

### E247 / E248 / B520 / E246
- **E247:**
  - The status item reads `vilan 0.43.0`, or `vilan (stopped)` in the warning colour; the tooltip keeps the platform and its reason.
  - The menu's rows are decided in `menu.ts` with no `vscode` import, and pinned by `menu.test.ts`.
  - Information rows: platform and why, the entry's world, the server version, and the last analysis' counts (files, entities, impls — never milliseconds).
  - Toggle rows: one per live feature switch.
  - Action rows: restart / stop or start / status / output channel.
  - `vilan/analysisPlatform` gains `world` and `work`, captured with the analysis so a background tab still answers.
  - New commands are declared in `package.json`. The vsix was not packaged or installed.
- **E248:**
  - Stop logs the session profile, clears the client's diagnostics and disposes the client.
  - Nothing restarts it — not a settings change, not a crash policy — until Start, Restart or a window reload.
- **B520:**
  - The quick fix uses syntax-46's `foreign_spelling_fix`, keyed on the exact message.
  - The diagnostic is published with `ForeignSpelling::code()` as its LSP code.
  - It also works for a module served from its entry's world.
  - Pinned by `foreign_spelling_tests`.
- **E246:** the type's shape now sits under a horizontal rule and comes last, after the doc comment. Pinned in the hover goldens.

### Gates (all on the rebased tip)
- vilan-lsp + vilan-ide nextest 1044/1044, including the hover goldens and book_sync.
- vilan-core lib + docs 963/963.
- `vscode_extension` 26/26, which also runs the extension's own `npm test` (28/28); `tsc` is clean.
- `cargo clippy --workspace --all-targets -D warnings` and fmt are clean.
- No `.vl` fixture added and no golden moved. inference and corpus were not run: vilan-core changed only in the organizer, which the formatter unit tests cover.
- No `#[cfg(windows)]` pin. The M104 pins wait on counts and texts rather than sleeps, and compare paths canonical on both sides, so they should hold on Windows.

### Rebase notes
- The rebase onto 71cd1731 brought conflicts only in `CHANGELOG.md`. I kept both sides and put a `---` rule between all of this lane's entries.
- For A154 (layout-46): the E250 pins spell `std::fetch`, `std::json`, `std::hash` and `std::hash_map`; E251 spells `std::json`; E249 spells `std::reactive`. Re-read them after layout-46 merges. No new LSP code hard-codes a std path.

### New finds (`newitems46-editor.json`)
- **E?1:** hover and go-to-definition are empty on a call taking a context closure.
- **E?2:** twin files are not yet served from an entry's world under M104.
- **E?3:** a duplicate import carries no warning.
- **B?1:** `let x: i32 = 2 * true;` checks clean, and the JS build prints 2.
- **E?4:** where `self as name` sorts, versus E251's "`self` first" (owner's call).