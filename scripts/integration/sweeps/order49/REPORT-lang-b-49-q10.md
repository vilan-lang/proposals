lang-b-49 Q10 commit is done: sha 69909408, on e3b01166, on base b61f00bd. It is 14 commits ahead of next and not pushed. A cold check now builds no stage hints and no `auto` fills, and a pin holds the count at zero. Your perf target is met on genapp and on the eleven example rows, but not on plain: plain:160 +0.167%, plain:320 +0.177% against your 0.1%. I think 0.1% on plain is inside build-to-build noise; the measurements are below.

**How a cold check skips them**
- **The flag.** There is a new front-end fact, `Workspace::reading_aids`. Only the language server sets it, in `Document::analyze_in_context`, which every document analysis goes through, twin legs included.
- **Why not `hot_seeds`.** I did not reuse the seeded test that `labels_recorded` uses. Many editor analyses run with no seeds: first open, the file's own analysis, the LSP tests. They would have lost their stage hints.
- **What is gated.** `stage_hints` and the `auto_fills` table are built only under the flag.
- **What still runs on the CLI.** `check_auto_annotations` runs on every analysis: the stale refusal and the unfilled warning, both carrying the `--fix` rewrite. Under a `[check] auto` opt-in, the opt-in warnings are still written on a cold check. Only the points the opt-in covers are typed and spelled, and no table is filled.
- **Base cache.** The flag is out of the base cache key, like `hot_seeds`. The raw records the walk keeps (chain links, fill points, annotated landings) are still kept on every analysis. So a stored world serves either kind of caller, and only the per-analysis tables are skipped.
- **Counter and pins.** A new thread counter, `counters::reading_aids_rendered`, counts each stage hint and fill point considered.
  - `inference::ascription::e278_a_cold_check_renders_no_reading_aid` checks a cold check gives `(0, 0, 0)` and the editor flag builds both tables. It goes red with the gate removed.
  - `b570_a_cold_check_under_the_opt_in_renders_only_what_it_covers` covers the opt-in case.
  - `e278_a_stage_hint_is_served_on_a_module_reused_after_an_edit_elsewhere` is still green.

**Other cost I removed, found with callgrind against b61f00bd**
- B571's write-through refusal ran a pass over every expression, with a `reusable_entity` binary search each, on every analysis. It now runs only when the program has an ascription. This was the largest piece: about +0.4% on every row.
- `peel_ascriptions`, the emitter's copy peel (via a new `Program::has_ascriptions`) and `auto_written_type_id` now return early when their table is empty.
- The walk no longer works out a chain link's head; it used a map insert and lookup per method call. `stage_hints` works the heads out in one pass. `auto_fill_points` is now a Vec, deduplicated when read.
- I corrected `parse_type`'s B142 comment: `parse_type_atom` now has two callers, both depth-bounded.

**Perf rows** (`ci-local.sh perf`, local class, base b61f00bd vs 69909408). T2 is green; growth is x1.937.

| row | change |
|---|---|
| genapp:46 | +0.050% |
| plain:160 | +0.167% |
| plain:320 | +0.177% |
| math | +0.218% |
| watch | +0.160% |
| browser | +0.192% |
| fullstack | +0.149% |
| router | +0.155% |
| reactive-ui | +0.112% |
| ssr | +0.055% |
| canvas | +0.165% |
| rpc | +0.120% |
| todo | +0.060% |
| walkthrough | +0.088% |

**Why I stopped at +0.17% on plain**
- **What the remaining +4.9M on plain:160 is.** About 3.9M is parser and about 1.1M is analyzer. Most of the parser share is inlining shifts: `parse_generic_arguments` and `parse_type_atom` now show as separate functions, where the base inlined them, with unchanged bodies.
- **Two parser restructurings that should not change behaviour made it worse.** One kept the plain generic-list path inline; the other moved `auto` to `parse_type_inner`. They put plain at +0.21% to +0.23%, so I reverted both.
- **`memcmp` alone moves more than your threshold.** With identical call counts (781,236 `HashMap<&str,_>::get` calls), its cost differs by 4.4M between the base and tip builds, about 0.15% of plain:160. That is larger than the 0.1% target, so I would rather report it than keep chasing layout.

**Gates on 69909408**
- fmt and clippy `-D warnings`: clean.
- vilan-lsp binary: 1101/1101.
- inference: 5394/5394.
- vilan-core differentials (parse, edit_replay, permutation, check_scope, infer, replay, release): 342/342.
- vilan-cli with `VILAN_NATIVE_DIFFERENTIAL=1` (native full, ssr, release_scripts, check_fix, corpus): 307/307.
- I did not re-run the full workspace suite after this commit.

The CHANGELOG entry is marked `family: tooling`; the commit message lists every change and pin. LANE-STATUS.md is updated and untracked. The scratch base worktree and its target directory are removed.

**Decision for you:** accept plain at +0.17% given the noise above, or tell me what further cut you want before merging.
