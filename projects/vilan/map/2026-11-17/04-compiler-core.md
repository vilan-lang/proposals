# 04 — Compiler core and tooling: what exists, how complete, what is stale

Survey date 2026-11-17. Read-only. Code read at `/home/reed/code/vilan-lang/vilan/.claude/worktrees/integration` on branch `next` @6edafda5 (2026-11-16, the v0.56.1 fold). Nothing was built or run. Every number below comes from a file, a `git log` or a `wc`/`grep` count, and the source is named next to it. Tracker = `/home/reed/code/vilan-lang/proposals/projects/vilan/tracker/` (INDEX.md: 217 open rows, which matches the 217 files in `items/`). Where the tracker and the code disagree, this report follows the code and says so.

---

## Part A — The pipeline as built

### A.1 `crates/vilan-core/src` (83 `.rs` files, 232,148 lines)

| file | LOC | role |
|---|---:|---|
| `analyzer.rs` | **96,573** | name resolution, world loading/drain, type solver (constraints, fixpoint), the checks phase (~61 distinct `check_*/compute_*/plan_*` passes run under `unless_cancelled!`, analyzer.rs:92242-92580), editor tables, records |
| `analyzer/` (18 files) | 11,531 | split-out tables: `hover_labels` 1,657, `item_records` 1,446, `id_windows` 1,140, `liveness` 1,100, `dbg_stack` 825, `held_tables` 739, `r11_records` 474, `retain_tables` 385, `r11_candidates` 335, `cell_borrows` 305, … |
| `formatter.rs` (+`formatter/` 706) | 21,037 | `vilan fmt` |
| `transformer.rs` (+`transformer/` 1,973) | 17,927 | the JS emitter |
| `parsing.rs` | 17,395 | the parser |
| `manifest.rs` | 5,508 | `vilan.toml`, dependencies |
| `context.rs` | 4,736 | the context pass (hidden context parameters) |
| `interpreter.rs` | 4,471 | the const interpreter |
| `macros.rs` | 3,746 | macro expansion |
| `async_infer.rs` | 3,630 | async coloring/inference |
| `const_eval.rs` | 3,361 | const evaluation |
| `bindgen.rs` (+`bindgen/dts.rs` 1,455) | 2,875 | `.d.ts` to externals |
| `platform_color.rs` | 2,733 | platform coloring |
| `lexing.rs` | 2,516 | the lexer |
| `lib.rs` | 1,986 | entry points (`analyze_source*`, `post_analysis_passes` lib.rs:1239, phase timing) |
| `dispatch_refine.rs` | 1,960 | dispatch refinement |
| `impl_select.rs` | 1,609 | impl selection |
| `const_cache.rs` | 1,433 | the content-keyed const-site cache (memory, plus disk for the CLI) |
| `incremental.rs` | 1,425 | M110's measurement and gate surface (fingerprints, census, clean analysis, plants), world-cache/std-prefix switches |
| `init_order.rs` | 1,394 | module init order |
| `call_graph.rs` | 1,335 | the call graph |
| `prefix_file/` (`mod.rs` 589, `codec.rs` 954) | 1,543 | the persisted std prefix on disk |
| `mono.rs` | 448 | monomorphization helpers |
| `world_cache.rs` | 304 | prune/clean/budget for `~/.vilan/cache/worlds` |

Stages, in order:

- **Lex and parse.** `lexing.rs` is 2.5k lines and `parsing.rs` is 17.4k. `lib.rs` keeps a clean-parse cache (`parse_clean_cached`, lib.rs:665). The parser recovers from errors (B680 is about the cascade it leaves behind).
- **Macros.** `macros.rs` is 3.7k lines. Derives and `macro fun` run before analysis. On the CLI the expansion table is persisted on disk (`~/.vilan/check-cache`, M33/N92).
- **Analysis.** `analyzer.rs` plus `analyzer/` is about 108k lines. Its stages are load and walk (the drain), base, the world resolve (the constraint fixpoint), `build`, then the **checks phase** of about 61 passes: moves, drops, liveness (`LastUse`), clone sites, cell borrows, view escape, bound audit, and so on. The phase names come from the genapp phase split in `/home/reed/.vilan/perf-verdicts/perf-e9c25ab0….json`: load+walk, base, build, checks, contexts+graph, async-infer, platform-color, const-pass, init-order, emission-walk, program-drop.
- **Post-analysis passes.** `lib.rs::post_analysis_passes` runs `context.rs` (4.7k, plus the `call_graph.rs` 1.3k), `async_infer.rs` (3.6k), `platform_color.rs` (2.7k), the const pass (`const_eval.rs` 3.4k plus `interpreter.rs` 4.5k plus `const_cache.rs` 1.4k), and `init_order.rs` (1.4k).
- **Emission.** The JS transformer is about 19.9k lines with its submodules. The Rust backend is a separate crate, `vilan-rust`: a single 19,380-line `lib.rs` plus `dbg.rs`.
- **Formatter.** `formatter.rs` is 21k lines and stands apart from analysis.

**Maintainability fact:** `analyzer.rs` is one file of **96,573 lines** with 1,630 `fn` items. It is 42% of vilan-core's source by itself. The other single-file giants are `vilan-lsp/src/document.rs` (33,445), `formatter.rs` (21,037), `vilan-rust/src/lib.rs` (19,380), `transformer.rs` (17,927), `parsing.rs` (17,395) and `vilan-lsp/src/main.rs` (12,113). Activity concentrates in the largest file: `analyzer.rs` took 356 commits since 2026-10-01, against 113 for `transformer.rs` and 50 for `parsing.rs`. F26 (open) records that monomorphization resolution exists twice, once in `transformer.rs` and once in `vilan-rust`, and that only the differential holds them together.

### A.2 Other crates (src LOC / tests LOC)

- `vilan-cli` (17,333 / 112,679): the `vilan` binary. Its commands are `init`, `build`, `check`, `run`, `fmt`, `test`, `bindgen`, `upgrade` and `cache {prune,clean,warm}`. It also holds HMR (`hmr.rs` 2,308), watch and `fix`. Most corpus and e2e tests live here.
- `vilan-lsp` (66,218 / tests inline): the language server. `document.rs` 33k, `main.rs` 12k, `keystroke.rs` 3,960, `references.rs` 3,202.
- `vilan-ide` (9,910): editor helpers shared by the LSP: completion, quick fixes, html attributes.
- `vilan-embedded` (715 / 774): carries std and `macro_std` in the binary and materializes them at `~/.vilan/std-cache/<hash>/`.
- `vilan-wasm` (1,143 / 1,444): the playground compiler. The compile logic is plain Rust with a thin wasm-bindgen layer.
- `vilan-rust` (19,859): the emit-Rust (native) backend, F1 S1a onward.
- Runtime crates: `vilan-rt` 17,690, `vilan-rt-gfx` 27,868 (outside the workspace), plus webview, poll, net, sqlite, term, crypto, image, signal.

---

## Part B — Incremental analysis

### B.1 The design

- **M110 paper.** `proposals/projects/vilan/proposal/incremental-analysis.md` (752 lines, "PAPER drafted 2026-10-03"). The owner ruled Q1–Q10 as recommended on 2026-10-03: firewalls inside today's pipeline rather than a salsa rewrite ("door B" in §3.2). Slices from §5/§11:
  - S0: fingerprints, census, and the edit-replay differential.
  - S1: hot-set worlds. The base world is stored without the edited module and its reverse-import closure; the hot set is walked over a clone.
  - S2: prefix tables.
  - S3: seeded contexts, async and platform passes.
  - S4: the const cache.
  - S5: the id-windows spike.
  - S6: the interface firewall over windowed ids.
  - S7: per-item records.
- **std-prefix paper.** `proposal/std-prefix.md`, slices P0–P6b in §13 and §14. P3 persists a std-only prefix world on disk. P6b makes it the CLI default.
- **Supporting papers.** `editor-latency.md` (E121's mandate: under 10 ms on the keystroke path, under 500 ms to errors), `analyzer-pass-map.md`, `lsp-snapshot-consistency.md`.

### B.2 What landed (evidence)

From `tracker/items/M110.md` (the history log; the item itself is still OPEN) and the `archive.md` tombstones:

| slice | landed | evidence |
|---|---|---|
| S0 + edit-replay differential | Order 47 | M110.md 2026-10-05: "S0, the edit-replay differential and S1 are on next" |
| S1 hot-set worlds | Order 47; M121 (all kolt files served) closed 2026-10-09 | M110.md; archive M121 |
| S4 const cache | Order 48 (`const_cache.rs`); on disk for the CLI by M135, closed 2026-10-13 | archive M135 (kolt client const pass 258 to 47 ms) |
| P0 permutation differential, S2a bound-audit record, S2b label tables | Order 49 | M110.md C1–C3 |
| S5 spike | Order 49 (spike-49 "byte-identical on every leg") | M110.md 2026-10-10 |
| S3a/S3b (mutation-log form) | Order 50 | M110.md 2026-10-10 |
| S6 id windows | Order 50 (56975c4b); on for every editor analysis, OFF for a cold `vilan check` | M110.md |
| S7 per-item records | Order 51 (incr-51b) | M110.md 2026-10-13 |
| S7b item-grain checks (M142) | Order 52 | archive M142; leaf 470 ms at that seal |
| M148, M149, M150, M152, M154, M155 (R11 sets per region), M159 (lone document seeded), M160, M161 | Order 54 | archive tombstones, all CLOSED 2026-10-16 |
| std-prefix P0 (M144), P1, P2, P3, P4, P5, M158 | Orders 53–54 | archive M144; `prefix_file/`, `world_cache.rs`; M36.md 2026-10-16 (suite −10.2% CPU) |
| P6a (M157) | Order 55, closed 2026-10-27 | archive M157 |
| M188 Retain rows, M189 capture memo, hover index, const staged liveness | Order 56 wave 1, closed 2026-11-03 | archive; M110.md 2026-11-04: served leaf 9.85 to 7.81 G (−20.7%) |
| **P6b: CLI default `VILAN_STD_PREFIX=on`** | **NOT built** | `crates/vilan-cli/src/main.rs:428-433` says "`VILAN_STD_PREFIX=off` (the CLI's default)"; std-prefix.md:958 put it in Order 56; tracked only inside M36.md |

There has been no incremental-analysis work since Order 56 wave 1. `git log --since=2026-11-04` on `incremental.rs`, `keystroke.rs` and `retain_tables.rs` shows only M202 (typed elements).

### B.3 Where the caches live (code)

- **In-process base cache.** In `analyzer.rs` (`CHECKED_CACHE_DEFAULT_BUDGET` = 64 MiB at analyzer.rs:84886; base cache resident budget 192 MiB per M67). It holds hot-set worlds keyed by the import set plus the hot set. It is process-global; `BASE_CACHE_LOCK` at `crates/vilan-lsp/src/document.rs:11382` serializes the test pins that read it.
- **Keystroke path.** `crates/vilan-lsp/src/keystroke.rs` (3,960 lines). Semantic tokens, inlay hints and completion are answered in O(file) from the last landed analysis, re-mapped by a two-sided anchor, with a declaration-shape stamp and a per-module symbol index. This path never type-checks.
- **Records.** Per-item records over id windows (`analyzer/item_records.rs`, `id_windows.rs`), the R11 rows, Retain rows and hover records.
- **On disk.** Three caches:
  1. The macro expansion table, at `~/.vilan/check-cache/<hash>` for `vilan check` and `dist/.cache` for build. CLI default on.
  2. The const-site cache, `<cache dir>/.cache/const-sites` (`const_cache.rs:869`, set by `cli/main.rs:4946`). CLI default on; the LSP keeps it in memory only.
  3. The persisted std (+ dependency tier) prefix world, `~/.vilan/cache/worlds/<key>/std.world` + `std.checks` (`prefix_file/`, `world_cache.rs`). It is on by default in the **language server** (`vilan-lsp/src/main.rs:8211-8219`). In the **CLI it is off** unless `VILAN_STD_PREFIX=on` or `vilan cache warm` is used. The test suite uses it via `VILAN_TEST_WORLD_CACHE`.

### B.4 What an edit re-analyzes today

Read from M110.md, the S1 design in paper §4.1, M159, and M194:

- One keystroke runs **one analysis of the entry's world** (M104's hybrid). A lone open document is analyzed as its own file-mode entry. A second open document of the same world switches to the entry world.
- **Prefix.** The prefix (std, plus every module outside the hot set) comes from the base cache as a clone.
- **Hot set.** The hot set is the edited module, every module that imports it, and their import cycles. On kolt it ranges from 1 module (the entry) to 11–14 modules (the seven-module cycle, `model.vl`, `shared.vl`) per paper §4.2. It is re-walked and re-resolved.
- **Checks.** The checks phase runs at item grain over live ranges, and per-item records serve unchanged items. But every Class A/D pass still sweeps an "always-live" lane of about **126k entities** (derived bodies, `DERIVED_SOURCE`), which are never filed (M194, open).
- **Post passes.** These are seeded from records. Contexts replay, and const hits come from the content-keyed cache.
- **Granularity.** The answer is therefore neither "whole world" nor "one function". It is roughly the hot set's modules plus a whole-program residue in the checks and post passes. The paper's S7 goal, "a body keystroke re-checks one function", is not met in effect.

**Persistent cache between `vilan check`/`vilan build` runs:** partly yes. On by default: the macro table and the const sites. Opt-in only: the persisted std prefix world (P6b unbuilt). No analysis of package code persists. `vilan check` never uses id windows (S6 is OFF for a cold check, by design).

### B.5 What remains, and what it is parked on

| item | what remains | parked on / status |
|---|---|---|
| M194 | derived bodies never filed; ~126k always-live entities per keystroke | named in M110.md 2026-11-04 as "the next lever"; no lane since; also parks A185 S3b (the reactive lens's T4) |
| P6b (in M36) | CLI default std prefix | needs P6a (done), P5 (done), M158 (done), so nothing blocks it; scheduled for Order 56, not built |
| M163 | const pass / drop-plan slice | design question first |
| M99 | a full reuse hit still pays 96% of checks | partly answered by S7/S7b |
| M73 / M79 | `resolve_world` per keystroke; the constraint fixpoint is 79–96% of the pass | paper first |
| M19 | unchanged package module re-analyzed per LSP analysis/HMR round | "next M55/M56/M57" (stale text) |
| M56, M57 | the entry's share; the replay differential blind to R10 | M57 is an owner question |
| M140 | 192 MiB base-cache budget no longer holds kolt (worlds ~74 MB each) | re-measure |
| E297 | publish the edited item's diagnostics first | design question for the owner |
| M27 | `lsp-index` editor tables 110–584 ms per keystroke (old measurement) | |
| E121 / E292 | the 500 ms mandate | see below |

### B.6 The percentage

- **By slices: about 94% (15 of 16).** M110 S0–S7 are all landed (8 of 8), plus the S7b/S7c follow-ups. std-prefix P0–P6b: 7 of 8 landed, P6b missing.
- **By outcome: about 45%.** E121's leaf mandate is 500 ms CPU to diagnostics. The v0.56.1 measurement is **1,090 ms** (500 / 1,090 = 46%), on an exhibit three times larger than the one the mandate was first met on. The interim target ruled 2026-11-03 is 1,500 ms (`perf/budgets.toml` `[[e121]]`). The leaf was under 500 ms at v0.50.0 through v0.53.0 (470, 410, 330, 500 ms) on the smaller kolt.
- **Plain user-visible state:** a keystroke in a leaf file of today's kolt costs about 1.1 s of CPU before diagnostics refresh. A css edit costs about 1.2 s and a parse break about 1.9 s. Hover, completion and tokens are served from the landed analysis without type-checking. A cold `vilan check` of kolt costs about 5.3 s of CPU and 594 MB of RSS with no package-level reuse between runs.

---

## Part C — Performance, with numbers

### C.1 The gates

**`perf/budgets.toml` (280 lines).**
- Twelve subjects: eleven examples (math, watch, browser, fullstack, router, reactive-ui, ssr, canvas, rpc, todo, walkthrough) and `genapp:46`.
- Each subject has two classes:
  - `reference`: `instructions:u` on the owner's 9800X3D, file tolerance 1%.
  - `ci`: callgrind on the CI runner, row tolerance 0.5%.
- Ceilings are ratcheted from measurements and judged cumulatively. A `[[bump]]` row lives one release.
- `[[growth]]`: plain:160 to plain:320 at most x2.3 per doubling.
- `[[e121]]` rows, each `green_seals = 5, blocking = true`:

| E121 row | target | mandate row |
|---|---:|:---:|
| leaf keystroke | 1,500 ms | yes |
| shared.vl keystroke | 500 ms | |
| model.vl keystroke | 600 ms | |
| model.vl keystroke, importers open | 3,000 ms | |
| css keystroke | 1,300 ms | yes |
| parse break | 2,500 ms | yes |

Each row's `series` note says these are interim targets ruled 2026-11-03 at about 1.1x the quiet estimate, and that "the 500 ms mandate stays the arc's goal".

**`scripts/perf_gate.py`** (1,184 lines) reads and writes the budgets, ratchets them, and judges T2 (instruction counts), T3 (kolt `vilan check` CPU and instructions at x1.10, peak RSS at x1.05 against the previous release) and the LSP rows (judged on instructions; CPU reported).

**`scripts/lsp-latency.py`** (1,374 lines, E236) drives `vilan-lsp` over stdio through a fixed edit script on a kolt copy. It prints CPU to the last `publishDiagnostics`, the keystroke-path latencies, VmHWM and edit-to-idle instructions. Its banner reads "E121's targets: <10 ms on the keystroke path, <500 ms to errors" (line 1120). The keystroke-path (<10 ms) figures are **not** carried into the release reports.

### C.2 Latest measurements

**T2, `instructions:u` (reference class):**

| subject | v0.56.0 (`perf/report-v0.56.0.md`) | v0.56.1 (`perf/report-v0.56.1.md`) |
|---|---:|---:|
| example:math | 254,905,987 | 254,903,536 |
| example:watch | 316,415,026 | 316,413,200 |
| example:browser | 1,382,575,320 | 1,382,573,045 |
| example:fullstack | 2,896,342,147 | 2,896,359,275 |
| example:router | 1,510,779,691 | 1,510,810,425 |
| example:reactive-ui | 1,539,651,227 | 1,539,704,591 |
| example:ssr | 3,297,770,717 | 3,297,847,237 |
| example:canvas | 1,395,806,305 | 1,395,807,414 |
| example:rpc | 1,581,050,614 | 1,581,111,500 |
| example:todo | 3,957,661,982 | 3,957,272,507 |
| example:walkthrough | 4,156,775,338 | 4,156,300,467 |
| genapp:46 | 7,516,332,480 | 7,516,636,655 |
| plain:160 / plain:320 | 2.926 G / 5.861 G (x2.003 per doubling) | 2.927 G / 5.862 G (x2.003) |

**T3, kolt `vilan check`** (`/home/reed/.vilan/perf-verdicts/perf-<sha>.json`, the tip side):

| release | kolt source | CPU | instructions | peak RSS | ratios vs previous release |
|---|---|---:|---:|---:|---|
| v0.56.0 (eca174d4) | prepared tree `kolt-tip` | 4.230 s | 33.70 G | 530,324 kB | CPU x1.015, RSS x1.040, instr x0.999 |
| v0.56.1 (e9c25ab0) | kolt@76067e7a | 5.273 s | 46.15 G | 593,976 kB | CPU x1.005, RSS x1.009, instr x1.001 |

**LSP rows** (`proposals/scripts/integration/sweeps/order58/seal-561-perf2.log` and `seal-58-run2.log`, tip side):

| row | v0.56.0 CPU / instr | v0.56.1 CPU / instr |
|---|---|---|
| leaf keystroke | 1120 ms / 7.487 G | 1090 ms / 7.487 G |
| leaf keystroke + pause | 3240 ms / 21.888 G | 3270 ms / 21.883 G |
| shared.vl keystroke | 350 ms / 1.535 G | 350 ms / 1.535 G |
| model.vl keystroke | 580 ms / 3.631 G | 590 ms / 3.628 G |
| model.vl, importers open | 2080 ms / 18.322 G (report: 2120) | 2100 ms / 18.320 G (report: 2150) |
| css keystroke | 1230 ms / 8.435 G | 1220 ms / 8.436 G |
| parse break | 1980 ms / 15.354 G | 1930 ms / 15.350 G |
| parse repair | 1990 ms / 15.835 G | 1970 ms / 15.838 G |

All six E121 rows are green against the interim targets. `model.vl` sits at 590 of 600 ms and css at 1,220 of 1,300 ms, so both are within 2–7% of red. At v0.55.0 both were RED (blocking): model 700 ms and css 1,410 ms (`report-v0.55.0.md`).

**Most expensive phase**, from the genapp:46 thread-CPU split in the verdict JSONs:

| phase | v0.56.0 | v0.56.1 |
|---|---:|---:|
| load+walk | 297 ms (the report's headline, 29%) | 205 ms |
| base | 223 ms | 223 ms |
| checks | 285 ms | 286 ms (the report's headline, 31%) |
| contexts+graph | 86 ms | 84 ms |
| emission-walk | 30 ms | 30 ms |
| const-pass | 23 ms | 17 ms |
| async-infer | 21 ms | 21 ms |
| program-drop | 19 ms | 17 ms |
| platform-color | 15 ms | 15 ms |

The checks phase has been the headline in 12 of 14 reports (33%, 33%, 33%, 37%, 30%, 34%, 31%, 32%, 30%, 34%, 32%, 36%, then load+walk in v0.56.0, then 31%).

### C.3 Trend

Each row comes from a `perf/report-v*.md` paired with its verdict JSON in `/home/reed/.vilan/perf-verdicts/`. **The kolt exhibit changes several times**, so the absolute kolt columns are only comparable within one exhibit.

| release | seal sha | kolt exhibit | kolt CPU | kolt instr | kolt RSS (MB) | leaf ms | css ms | parse break ms | genapp:46 instr |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| v0.44.0 | 9fab0ff5 | 984a1dfb | 2.390 s | 25.43 G | 271 | 860 | 940 | 970 | 9.873 G |
| v0.45.0 | 19e78198 | a05fcb60 | 1.679 s | 15.71 G | 271 | 300 | 400 | 430 | 9.674 G |
| v0.46.0 | e12a83a4 | a05fcb60 | 1.617 s | 12.94 G | 271 | 250 | 350 | 360 | 8.758 G |
| v0.47.0 | 83385995 | 249ec8f0 | 1.756 s | 13.84 G | 269 | 580* | 780 | 840 | 8.302 G |
| v0.48.0 | 68f25eb1 | e01e59a8 | 1.550 s | 13.18 G | 269 | 550 | 750 | 760 | 7.759 G |
| v0.49.0 | 070653d2 | dee494ab | 1.709 s | 13.28 G | 352 | 580 | 790 | — | 7.664 G |
| v0.50.0 | 99b6013e | dee494ab | 1.841 s | 14.18 G | 356 | 470 | 750 | 740 | 7.677 G |
| v0.51.0 | 9716b72f | d48ab612 | 1.715 s | 13.74 G | 326 | 410 | 650 | 610 | 7.414 G |
| v0.52.0 | 6c460ca4 | 611d86f7 | 1.649 s | 13.35 G | 325 | 330 | 600 | 620 | 7.143 G |
| v0.53.0 | c50a0a58 | 46c5b59c (prepared tip) | 1.696 s | 11.84 G | 240 | 500 | 720 | 740 | 7.169 G |
| v0.54.0 | 16a4da05 | 3fb5d742 (about 3x the program, N186) | 4.277 s | 33.75 G | 510 | 1150 | 1260 | 1980 | 7.387 G |
| v0.55.0 | 302d355a | c7454052 | 5.905 s | 45.97 G | 595 | 1170 | 1410 | 2230 | 7.388 G |
| v0.56.0 | eca174d4 | prepared tree `kolt-tip` | 4.230 s | 33.70 G | 530 | 1120 | 1230 | 1980 | 7.516 G |
| v0.56.1 | e9c25ab0 | 76067e7a | 5.273 s | 46.15 G | 594 | 1090 | 1220 | 1930 | 7.517 G |

\* E292 (open) says the v0.45–v0.47 low rows were measured on a kolt missing generated `src/lucide` (N165), which made every analysis stop early at half its cost. Treat 250–300 ms as invalid.

Reading the trend:

- **Compiler cost on a fixed subject is flat to slightly rising since v0.52.0.** genapp:46 went from 9.87 G at v0.44 down to 7.14 G at v0.52 (−28%), then rose to 7.52 G at v0.56.1 (+5.2% from the low). The bump rows name std growth (M120 class), typed elements (M202, x1.0008–x1.0054) and B740's Option contexts (M204, x1.0162).
- **The examples rise about 1% per order** through recurring bump rows.
- **Scaling is linear.** Growth per doubling went from x2.99 at v0.43 (budgets.toml comment) to x1.93 at v0.44–v0.53 and x2.00 now.
- **The kolt figures track kolt's size more than the compiler's.** Same-source ratios are about x1.00 at every seal from v0.54 on.
- **Anomaly, not determined.** kolt@c7454052 read 46.1 G as the v0.55 seal's base (under 0.54.0) but 33.7 G as the v0.56.0 seal's base (under 0.55.x), while v0.55.0's own ratio was x0.997. A 27% drop with no compiler change suggests the Order 58 exhibit copy differed: the lucide package moved (F184: "a declared dependency is analysed whole (+21% check instructions)"), and the harness may know kolt's old layout. The v0.56.0 absolute kolt row should not be trusted for trend.
- **The leaf keystroke is flat** at about 1.1 s from v0.54 to v0.56.1 on the current exhibit. No incremental work has landed since Order 56 wave 1.

### C.4 Open performance items (tracker section M: 43 open)

Grouped by my reading:

| group | count | items |
|---|---:|---|
| Compiler CPU (check/analysis cost) | 11 | M10 (mechanize the BASE_CACHE transmute claim), M17, M54 (`LastUse` clones, `source_of` linear scan), M56, M106 (cost-based suggestions), M120 (std growth tax on every program), M136, M139, M141, M202, M204 |
| LSP latency / incremental | 10 | M19, M27, M57, M73, M79, M99, M101, M110, M163, M194 |
| Memory / RSS | 1 | M140 (192 MiB budget no longer holds kolt) |
| Build / suite speed / output shape | 3 | M18 (bundle boundary), M36 (per-process cold floor; P6b), M59 (persist the leg record; HMR tiering) |
| Emitted-code runtime cost (codegen) | 4 | M88 (devirtualize a single-implementor `dyn`), M193 (enum copies at reactive seams), M199 (match over a Shared read copies), M201 |
| std runtime performance | 8 | M62, M173 (K² keyed gone), M183, M184, M196 (JS HashSet x1.25), M197 (O(n²) unsubscribe), M198 (no streaming digest), M200 (keyed store write O(n)) |
| Not performance (features/cleanup filed under M) | 6 | M174, M178, M180, M192 (stale comment cleanup), M205, M206 |
| Native runtime performance | 0 in M | they sit in section F: F165 (readiness loop per-turn cost; poll scales with connection count), F179 (virtual list O(n) inserts), F180 (`kit::text_area` 42 ms/key at 1k lines, 0.49 s at 10k) |

**The 8 most valuable, by my reading:**

1. **M194.** Derived bodies are never filed, so every Class A/D pass re-walks about 126k always-live entities per keystroke. It is the named next lever for the leaf and css rows, and it also unparks A185 S3b.
2. **E121 / M110 (the outcome).** The leaf is at 1,090 ms against the 500 ms mandate, and the paper's per-function goal is unmet. M79 (`resolve_world` per keystroke; the fixpoint is 79–96% of that pass) is the other structural lever.
3. **P6b (tracked in M36).** Make the persisted std prefix the CLI default. All prerequisites have landed. M158 measured −5.1% on kolt client and −22.2% on kolt server checks over a loaded prefix, and −20.8% on the corpus.
4. **M140 plus the RSS trend.** kolt check RSS is 594 MB, and the LSP cache budget no longer holds two kolt worlds.
5. **M197.** O(n²) unsubscribe in `std::reactive`: leaving kolt's Table page takes 69–102 s.
6. **M200.** A keyed store write is O(list length): 5.3 s for one batch over 32,000 rows.
7. **M120.** The std growth tax: every std addition taxes every program's check. It is the recurring cause of the 1% bump rows.
8. **M204 / M88 / M199.** Emitted-code costs on hot paths. B740's Option contexts alone cost genapp x1.016.

### C.5 Known cliffs (quadratic or pathological, named in open items)

- **M197.** Unsubscribe is O(n²) with a clone each: 56k cells on one shared cell take 69–102 s.
- **M173.** Keyed replica `gone` diffs every watched key: K² copies, 1.05M at 1,024 keys.
- **M200.** `Store<List<T: Keyed>>::by_key` scans on every read and write: 5,325 ms per batch at 32,000 rows.
- **F180.** `kit::text_area` reshapes the whole text as one paragraph twice per change: 42 ms per key at 1,000 lines, 0.49 s at 10,000.
- **F179.** Virtual list inserts and removals are O(n); positions break past 4 million dp.
- **A131.** The delta-driven `each` builds rows that are cut in the same drain; fixing it needs a redesign.
- **M54.** `Program::source_of` is a linear scan of about 60 ranges; `collect_unfollowable_loans` is 68% of a warm `LastUse`.
- **M36.** 3.5–5 s floor per test process for the CLI-spawning test binaries.
- **N200.** `permutation_differential` corpus test runs 400–670 s against a 900 s timeout.
- **N189.** Under plain `cargo test`, twelve shards serialize on SWITCH_LOCK for 3,264 s.
- **F165.** poll/WSAPoll scale with the connection count.
- **Resolved cliff:** whole-check growth was superlinear at v0.43 (x2.99 per doubling) and is now linear (x2.003).

---

## Part D — Tooling completeness

Open counts are from INDEX.md. "Last touched" is the last non-release commit on the path.

- **Language server — mature but over budget.**
  - Advertised capabilities (`crates/vilan-lsp/src/main.rs:4144-4233`): incremental text sync with open/close/save, hover, linked editing range, definition, references, rename with prepare, document symbols, document formatting, on-type formatting (`<`), completion (triggers `.` and `:`), inlay hints with resolve, semantic tokens (full plus delta, and range), code actions (organize imports, quickfix, refactor.rewrite, fix-all imports, fix-all auto) and executeCommand (session summary).
  - **Not advertised:** signature help, workspace symbols, document highlight, go to implementation or type definition, call or type hierarchy, folding ranges, selection ranges, code lens, range formatting, pull diagnostics.
  - Last touched 2026-11-16 (eca174d4). 122 commits since 2026-10-01.
  - Open: E121, E182, E288, E292, E297, E334, E343 (7), plus LSP-facing M items (M27, M101, M140, M194, …).
- **Formatter (`vilan fmt`, `--check`, `vilan-fmt: skip`) — working, edge tail.** Last touched 2026-11-16. 56 commits to `formatter.rs` since 2026-10-01. Open: E339, E348, E349, E350, E351, E363 (6), all layout edges or polish.
- **Debugger — working, JS only.** `vilan-dap` is not a crate. It is an inline adapter inside the VS Code extension (`editors/vscode/src/dap/`, 2,871 lines). It speaks DAP to the editor and CDP to node's inspector (`vilan run --inspect-brk`), and prints values by static type from the `.vdbg.json` sidecar.
  - Capabilities: conditional breakpoints, evaluate for hovers, clipboard context, terminate, configurationDone. Requests: launch, setBreakpoints, setExceptionBreakpoints, threads, stackTrace, scopes, variables, evaluate, continue, next, stepIn, stepOut, pause.
  - I found nothing for the native (Rust) backend.
  - Last touched: `dap/` 2026-11-02; `debug.ts` 2026-11-09 (E361, shipped v0.55.1).
  - Open: E257 (paper row still "design discussion" though S7 shipped), E344 (2).
- **Test runner (`vilan test [--watch]`) — minimal.** `discover_tests` (`cli/main.rs:6544`) takes a single file, or the `*_test.vl` files directly in one directory, or the project root. It never recurses into subfolders. Tests pass by exiting 0. There is no per-test reporting, filtering or assertion library beyond `assert`. The function was last changed 2026-06-18 (7a185466). Open: E368 (1).
- **Packages / dependencies — partial.** `vilan.toml` supports `path` and `git` dependencies pinned by tag or rev (`git_dep.rs`, content-addressed cache `~/.vilan/git-deps/`). There is no lockfile; it is not needed with exact pins. A **registry is not supported**: manifest.rs:1610 says "registry dependency `{name}` is not yet supported". `manifest.rs` was last touched 2026-11-11 and `git_dep.rs` 2026-09-24. Open: E366, E367, F184, B712 (4).
- **Build hooks (`[build] run`, `generated` roots) — working with gaps.** Open: G9 (a workspace member's `[build] run` never runs, silently), G12, E365 (std gaps for porting build steps: no process spawn, gzip or patterns), M59 (4).
- **Wasm playground (`vilan-wasm`) — working, idle.** Last non-release commit 2026-10-03 (f8a969f0). Open: K29 (1), plus K section 4 rows in all.
- **HMR / dev server (`vilan run --watch`, `hmr.rs` 2,308 lines) — working, idle.** Last touched 2026-10-13 (52717f4c), with 1 commit since 2026-10-01. Open: M19, M59 (2). The HMR round does not use S6 id windows ("`--watch`/HMR wait for S5's id windows", M110.md); I did not find whether that happened since (not determined).
- **Docs gate (`crates/vilan-core/tests/docs.rs`) — enforced.** Every fenced example in `vilan/docs/` compiles; there are 725 ```` ```vilan ```` fences. Last touched 2026-11-10. Open: N47, N197 (2).
- **VS Code extension — current.** `editors/vscode/src` is 6,790 lines (TS, including tests). It has the language client, debug configuration and the DAP. Last non-release change 2026-11-09. No open item names it specifically (E62 is a Zed extension). The directory holds 13 old `.vsix` files from 0.34 to 0.54, which is clutter.

---

## Part E — Language and solver health

### E.1 Open rows per section (INDEX.md, 217 total)

| section | open |
|---|---:|
| A reactive | 24 |
| B type system & solver | 55 |
| C memory model | 2 |
| D docs | 1 |
| E LSP & tooling | 23 |
| F native | 24 |
| G macros & const | 4 |
| I collections | 3 |
| J concurrency | 3 |
| K web | 4 |
| L release | 5 |
| M performance | 43 |
| N hygiene | 26 |

INDEX.md lines 133–138 hold a stray fragment of an E row: a code fence and an "E238 (ruled door (b)…" tail with no ID column. One row's head was lost in an edit.

### E.2 Correctness debt: miscompiles and unsoundness

**Open and unfixed in code** (no fix commit found by `git log --grep`):

- **B748**: MISCOMPILE (JS). A copy of a unit-only enum changes when the original is written through `&mut` (`let copy = a; set(&mut a)` moves `copy`). Native keeps the copy.
- **B749**: MISCOMPILE (JS). `if x` and `!x` over a `&bool` view read the `(base, key)` pair, so `if x` is always true and `!x` always false.
- **B684**: miscompile (JS) and backend defect (native). A readonly `&` at a `&mut` parameter checks clean and writes through on JS; native is refused by rustc.
- **B685**: miscompile (JS). `opt.unwrap_or(&0) + 1` over a `None` `Option<&i32>` prints `0,01` on JS and `1` natively.
- **B679**: backend divergence. An `Option` reaching `any` through a generic body is `[0, 1]` on JS and `1` natively. Commit 72eebcd1 (M175) mentions B679; whether it fixed it is not determined.
- **B728**: native wrong value. `usize::max`/`min` go through f64, losing precision above 2^53.
- **B700**: silent wrong resolution. When an imported module and an imported function share a name, the function wins and no import is refused.
- **B717**: native leak. The reactive lens leaves counted cells live at exit (for example 184 of 537 in lens-laws). Not yet in the leak census.
- **Silent wrong behaviour in std, not the compiler:** B702 (`revoke` sends no frame), B703 (base-slot acks never sent, a client leak), B704 (one bad base drops the rest of a Subscribe frame), A186 (a no-turn write can dispose its own owner mid-handler, silently).
- **Native emission that rustc refuses** (loud, not miscompiles): B699, B705, B708, B729, B730, B732, B733, B736, B750, F150, F155. Parity divergences: F159 (JSON key order), F161 (sqlite REAL vs INTEGER), A176 (what `any` holds).

**Open in the tracker but fixed in code (stale rows):**

- **B713** (MISCOMPILE, shared hoisted index temp). Fixed by 53135cdb, an ancestor of next, and in the CHANGELOG under v0.55.0 (CHANGELOG.md:351). Still listed open.
- **B715** (MISCOMPILE, supertrait default method's T unbound). Fixed by 98b7334f/be5a6bab. The item says "FIXED … OPEN for the owner's review of the fix's one caveat".
- **B737** (context requirement charged to every call of a trait default). Fixed at 70399859 (ancestor of next). The item says FIXED; INDEX still lists it.
- **C13** (unsoundness: a closure over a view parameter escapes through a storing callee). Closed by C16's commit e56b1227 (2026-09-17), which says "C13's pinned-and-ignored case … is un-ignored here", and the pin is live at `crates/vilan-core/tests/inference/borrows.rs:7389`. The item still says "OPEN — pinned `#[ignore]`d". Two months stale.

### E.3 Owner rulings and design questions pending

- **Design questions:** A176 (what `any` holds), E297 (publish the edited item first), M163 (const/drop slice).
- **Owner questions:** F115 (language vs backend refusal), M57 (edit a shared test function), A106 door 2, F181 (BSL-1.0 revisit).
- **Discussions with no ruling:** A37 (owner unsure of the value), F15, F17, F27 (write-once UI and platform layers), A173 / E257 (the owner's papers), B298 (behind trait-typed-fields Q3), A97 (wire contract), A87, A111, I10, M62.
- **Ruled and awaiting build:** F175 (R1–R13), A183 (the import foundation paper; A181/A182 slices landed), B711 (struct keys; paper), A180 (marker trait on result type), P6b (CLI std prefix default).

### E.4 Big language features, status word each

| feature | status | evidence |
|---|---|---|
| `dyn` | **Shipped** | A124's flip put `dyn Source<T>` at fields. Optimization M88 (devirtualize single implementor) open; B612 diagnostic. |
| `lazy` | **Shipped** | A100 S1+S2, A103 retrofit (Orders 36–37). No open row. |
| const (`const let`/`const fun`, const eval) | **Mostly built** | G24 ruled and built. G2 "const-eval tail", G12, E367 (`asset::read` in a dependency) open. |
| Macros / derives | **Built, tail** | G29, G9 (build hooks), B614 and B678 (a derive generates code that does not parse). |
| Concurrency (J) | **Partial** | J4 free-spawn lint, J5 async recorded opens, J8 no public cancel handle (an `async ||` parameter silently runs outside the nursery). |
| Memory model (C) | **JS-complete, native in progress** | C2 is blocked on F4's native memory story. C13 is stale (fixed). C14 (Rc/owner arena, Weak) S1–S3 landed. B717 lens leak natively. |
| Reactive lens (A185) | **Half-built** | S1, S2, S3, S5 on next. S3b parked on M194. S4 waits on B711. S6 (wire) and S7 (Store) pending. The INDEX row still says "DRAFT, Q1-Q10 open", but it was ruled 2026-11-08. |
| Native backend and GUI (F) | **In progress** | Rust backend, gfx, webview shell slice 1, kit. Follow-ups F166/F167/F182 and 11 native rustc-refusal bugs in B. |
| Struct keys (B711), import foundation (A183) | **Paper** | |
| Variadic generics (B3), `!`/`?.` (B11), fixed arrays (I2), iterator adapters (I3) | **Tails** | The rows carry no detail. |

### E.5 What looks stale

- **The tracker drifted from the code in several places:**
  - B713, B737 and C13 are fixed in code but open in INDEX. B715 is fixed and awaiting review.
  - M110 is open although every paper slice is built; its live remainder is M194, the mandate and P6b.
  - E292's title describes the v0.46–v0.47 measurements, and the series was re-anchored (N186, closed).
  - F1's row says "ONE backend (the JS emitter)" while `vilan-rust` exists.
  - A185's row says "DRAFT, Q1-Q10 open" although it was ruled with four slices landed.
  - M19's text says "next M55/M56/M57".
  - M36.md carries P6b, which was scheduled for Order 56 and not built.
  - E257 still reads "design discussion" although `vilan-dap` shipped.
- **Papers:** `incremental-analysis.md` still says "Status: PAPER, drafted 2026-10-03"; `std-prefix.md` says "DRAFT 2026-10-10 — for the owner's ruling". Both were ruled and built.
- **Chronicle:** `proposals/tracker/chronicle.md` has no Order 56–58 entries.
- **Measurement drift:** the v0.56.0 T3 kolt row (33.7 G on the same kolt sha that read 46.1 G a release earlier) suggests the exhibit copy changed. budgets.toml's `ci` ceilings for math are still "v0.54.0's seal". The E126 exhibit (E343) is a third of kolt's size, and its gate E334 fails on its own exhibit.
- **No incremental-analysis work** since 2026-11-04. The leaf row is flat at about 1.1 s.
- **Test discovery:** `discover_tests` unchanged since 2026-06-18.
- **Repository root clutter:** 13 old `.vsix` files under `editors/vscode/`; eight `REPORT-*-43/44.md` files and a `suite.log` at the repository root.
