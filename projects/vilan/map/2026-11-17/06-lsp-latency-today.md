# The language server on today's Kolt: measurement and diagnosis (lane lsp-58, 2026-11-17)

Step 1 of tracker M208. Measured with a release build of `next` @eba9c211 plus the harness commit
`4ee5c2e2` (branch `lsp-58`); the installed 0.56.1 agrees within 0.1% on every row. Raw outputs are
on the owner's machine under `~/.vilan/gates/lsp-58/` (`runs/`, `probes2/`, `session/`, `passes/`,
`skip/`, `callgrind/`, `n208/`, `census/`, `before/`, `after/`).

**How to read the numbers.** The machine never went quiet (load 3.2 to 19.7 all session). Every
CPU-ms figure was taken under load and is inflated, about 1.3x at load 7 to 9. INSTRUCTION counts
(G = billions, from the edit to idle) are the primary figure; they reproduce the v0.56.1 seal within
0.7% (old leaf 7.54 G here, 7.487 G at the seal). All runs used private caches.

## 1. The harness (commit 4ee5c2e2 on `lsp-58`)

- **Both layouts.** `scripts/lsp-latency.py` detects Kolt's layout (the new one when
  `src/shared/lib.vl` sits beside `src/client/main.vl`). Each layout has its own scenario table. The
  old table is untouched: on the old exhibit the anchors, their offsets and the instruction counts
  are the same before and after (leaf 7.534 → 7.536 G). The new table keeps every row name and
  points each role at today's file: `src/client/app/views.vl`, `src/shared/lib.vl`,
  `src/client/app/model.vl`, `src/client/ui/styles.vl`, `src/client/channels/channel.vl`.
  `perf/budgets.toml` and the E121 state are unchanged.
- **Generated inputs** for both layouts from one shared list. Today's Kolt tracks a symlink that
  dangles in a `git archive` copy and crashed the harness before its first edit; fixed.
- **A `--probes` mode:** the entry's cold open; a burst of ten keystrokes 80 ms apart; hover,
  completion, inlay hints and tokens asked while an analysis runs; a switch to a second file.
- **N208's second defect, found and fixed.** `vilan check` keeps a per-package macro and const-site
  table keyed by the copy's path and stamped with the compiler build. A same-source seal ran both
  compilers in ONE copy, so every measured run missed that cache (46.1 G); a seal with a separate
  tip tree had two warm tables (33.7 G). The const-site table is about 9.4 G of the gap, the macro
  table about 2.9 G. `perf_gate.py seal` now always gives the tip its own copy. The next
  same-source seal's absolute Kolt row will read about 27% lower and about 75 MB less; past ratios
  stand.

## 2. Today's Kolt against the exhibit the gate has been measuring

| Row | Old exhibit, G | Today's Kolt, G | Ratio | CPU ms old / new (under load) |
|---|---:|---:|---:|---|
| leaf keystroke | 7.54 | 8.64 | x1.15 | 1400 / 1500 |
| leaf + pause | 22.00 | 27.60 | x1.25 | 4580 / 4950 |
| leaf, world mode | 9.99 | 11.68 | x1.17 | 1770 / 2200 |
| shared module | 1.58 | 3.59 | x2.27 | 440 / 940 |
| model | 3.68 | 5.61 | x1.52 | 680 / 1320 |
| model, importers open | 18.41 | 23.04 | x1.25 | 2230 / 3530 |
| css (role changed, see below) | 8.49 | 1.89 | x0.22 | 1400 / 550 |
| parse break | 15.40 | 17.43 | x1.13 | 2240 / 2850 |
| parse repair | 15.89 | 17.58 | x1.11 | 2230 / 2870 |

- **Sizes.** Today 161 files and 85,050 lines; the old exhibit 127 files and 69,997. The client
  world: 186 files and 851,766 entities against 164 and 749,970.
- **Cold open of the client entry:** 45.08 G, 6.9 s, 846 MB peak (old: 34.15 G, 5.0 s, 680 MB).
  Peak memory over a full run: 2,595 MB against 2,076 MB.
- **Quiet estimates** (the seal's quiet figures scaled by the instruction ratio; not measured):
  about 1,250 ms for the leaf, about 2,180 ms for the parse break.
- **The css row changed role.** Today's `styles.vl` imports `theme` as a library package, so
  opened alone it is a tiny world. The same `css { }` block typed with the entry open costs 21.5 G
  per keystroke.

**The keystroke path** (the under-10-ms half of the mandate, never in a release report before):
completion, inlay hints and tokens stay at or under 3.5 ms (completion around a parse break 4.5 to
6.9 ms). HOVER is the slow one: 5 to 9 ms of CPU on an idle server, 1.8x the old exhibit, and 11.6 to
18.9 ms wall at the parse break and with the model's importers open.

## 3. Beyond diagnostics latency

- **A burst of ten keystrokes** started exactly one analysis: nothing queued, nothing cancelled.
  Last keystroke to its diagnostics: 1.9 s wall (1.6 s on the old exhibit).
- **Requests during an analysis** are answered from the last finished analysis in under 6.5 ms.
- **Switching to a second file:** opening `channel.vl` beside the leaf costs 9.8 s of CPU. The first
  keystroke there costs 30.35 G (a base-cache miss); later ones 21.9 G each, about 3.3 s of CPU
  under load.
- **The biggest cost met in ordinary editing:** a keystroke in any widely imported module with the
  entry open. Theme, model, styles and channel each re-walk 43 to 51 of the world's 87 modules:
  about 21 G, about 3 s of CPU under load. **No E121 row measures this.** The only world-mode row
  edits the leaf, which re-walks 2.

## 4. One leaf keystroke, profiled (callgrind, 9.14 G in the measured window)

| Phase | Instructions | Share | CPU ms (under load) |
|---|---:|---:|---:|
| Working out the file's platform (re-reads and re-parses both entries' import graphs every keystroke) | 0.50 G | 5.4% | ~156 |
| Load and walk | | | 95 |
| Build (`resolve_world` is 0.12 G and 19 ms of it; its fixpoint 4.3 ms) | | | 78 |
| Checking passes | | | 581 |
| Copying the stored world on a cache hit | 0.30 G | 3.3% | |
| Const pass (1,227 hits, 0 misses) | 0.78 G | 8.6% | 126 |
| Contexts and call graph | 0.69 G | 7.5% | 143 |
| Async inference | 0.17 G | 1.9% | 36 |
| Dispatch refinement | 0.29 G | 3.1% | 45 |
| Editor tables (the reference index; sorting is 0.21 G of it) | 0.55 G | 6.1% | 118 |
| Landed walk for the keystroke path | 0.32 G | 3.4% | 46 |
| Platform requirements in the server | 0.17 G | 1.8% | |
| Publishing, and requests asked during the window | 0.73 G | 7.9% | |

Load, walk, build and the checking passes together are 4.67 G; callgrind cannot split them (the code
is inlined), so their split is CPU ms from the phase lines. The largest checking passes, in ms:
`infer_bumps` 62, `check_generic_bound_satisfaction` 59, `LastUse` 49, `plan_resource_drops` 41,
`check_resource_moves` 27, `check_container_resource_arguments` 26. 57 passes of 1 ms or more sum
to 569 ms.

## 5. What the profile says about each planned lever

- **M194 (derived bodies never filed).** Today's Kolt has 152,559 derived-body ids in the live set,
  99.7% of the 153,030 the checking passes sweep per leaf keystroke (old exhibit: 125,029,
  confirming the item's "~126k"). Priced with a temporary, UNSOUND build that skips them (never
  committed): leaf 8.65 → 7.98 G, **−0.67 G, −7.7%**; world mode −0.68 G; parse break −0.32 G. A
  real version pays to restore rows, so less. High confidence on the count, medium on the saving.
- **M79/M73 (the solve per keystroke).** `resolve_world` is 0.12 G, 1.3%. The items' premise is
  stale for a served keystroke. High confidence.
- **Editor tables (M27).** 0.87 G together, 9.5%. High confidence.
- **Cache behaviour (M140).** Over 40 keystrokes in 4 files: 36 hits, 4 misses, one on each file's
  first keystroke, because each file's re-walk set is a different cache key. A miss costs +7.5 to
  +17 G. The 192 MiB budget is exceeded, not obeyed: the cache held 3 to 5 worlds weighing 462 to
  737 MiB. A Kolt world now weighs about 150 MiB, not 74.
- **`auto` annotations S5: certain it was never built, and neither was importer reuse.**
  - The interface fingerprint is computed only when `VILAN_INCREMENTAL` is `measure` or `verify`
    (`incremental.rs`), from the finished program after the post-passes; its own comment says it
    "changes no answer, only what the phase line reports".
  - The set of modules re-walked is the reverse-import closure with NO interface test
    (`hot_set_closure` in `analyzer.rs`). The session confirms it: the sources walked equal that
    set on every keystroke, even when no interface moved.
  - `incremental.rs`, `item_records.rs` and `id_windows.rs` never mention `auto`. A written `auto`
    type is read only by the walk, for callers.
  - Importer reuse plus S5 would take keystrokes in theme and styles (0 of 20 moved an interface)
    and model's 6 clean keystrokes from about 21 G to about 11 G. Model's other 4 moved
    `Channel::create`'s inferred return mid-edit, which `auto` would stop.
  - The opt-in would write **315** annotations in today's Kolt (51 returns, 264 bindings; 240 in
    `src/`, 75 in `lib/`), counted from the compiler's own warnings. Kolt has 4 today.
  - Medium-low confidence on the size, high on the mechanism.
- **What no tracker item named:** working out the file's platform costs 0.50 G on every keystroke
  (it was 28 ms at Order 50); copying the stored world on a cache hit costs 0.30 G; the const pass
  costs 0.78 G when every site is a cache hit; idle hover costs 5 to 9 ms.

## 6. Levers, ranked by measured saving per keystroke on today's Kolt

| # | Lever | Saving | Applies to | Item |
|---:|---|---|---|---|
| 1 | Importer reuse when the interface did not move, then `auto` S5 and Kolt's opt-in | ~10 G (21 → ~11 G) | widely imported files with the entry open; nothing on the leaf | M110 (S6 as designed), B570 S5 |
| 2 | Base-cache misses on a file switch, and the budget | 7.5 to 17 G per switch | the first keystroke in each newly edited file | M140, M19 |
| 3 | Editor tables | up to 0.87 G | every keystroke | M27 |
| 4 | Const pass on full hits | up to 0.78 G | every keystroke | M163 |
| 5 | Contexts and call graph | up to 0.69 G | every keystroke | pass map §7.2 |
| 6 | Derived bodies filed | up to 0.67 G | every keystroke | M194 |
| 7 | Cache the file's platform choice per import graph | ~0.50 G | every keystroke | M209 |
| 8 | No world copy on a cache hit | ~0.30 G | every keystroke | M210 |
| 9 | Dispatch refinement | ~0.29 G | every keystroke | none |
| 10 | `resolve_world` | up to 0.12 G | every keystroke | M73, M79 |

The leaf needs about −4.6 G to reach 500 ms on a quiet machine. Levers 3 to 10 together reach about
3.8 G at their upper bounds.

## 7. Not measured

- Quiet CPU ms: the load never went under 2.0.
- Whether a cached world survives a return to an earlier file.
- Real savings from M194, S5 and importer reuse: the figures are bounds from temporary builds and
  estimates from the cheapest comparable keystroke.
