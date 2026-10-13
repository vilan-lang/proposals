# The served keystroke's checks phase after S7b, per pass (incr-52a, Order 52)

How taken: `VILAN_COUNTERS=1 VILAN_PHASE_TIMING=passes scripts/lsp-latency.py --source <kolt copy @dee494ab, lucide carried> --lsp <bin>/vilan-lsp --runs 3 --scenario "leaf keystroke, world mode" --scenario "leaf keystroke"`, base (697c9517) and tip built from the same tree state, run back to back under the SAME load (the other four lanes were building: load 10–11 during both runs; the base's quiet-box figure for the same row is 280 ms checks at load 3). The rows below are the last served world-mode keystroke of each run (records-served=39/43, hot-set world, base-cache hit). CPU ms per `[vilan pass]` line; a pass under 2 ms is left out.

| pass | base ms | S7b ms |
|---|---:|---:|
| the drop extents, shared cells and capture plan (six held passes) | 59.5–65.7 | 5.5–8.8 (`compute_shared_read_bindings`; `collect_held_rows`, the fold and the three other decisions each < 2) |
| R11 `check_resource_generic_instantiations` | 53.7–57.9 | 34.3–39.7 + 10.5–13.2 (its five whole-program sets, now built once at the first instantiation) — the instantiations' own work; the seed walk < 2 |
| `check_generic_bound_satisfaction` (the bound audit) | 19.1–25.5 | 31.6 (noise; the 392 live sites' own audits — M143's premise was wrong, the walk to skip was not the cost) |
| `compute_resource_types` | 20.3–26.8 | 3.3–3.6 |
| `infer_bumps` | 21.5 | 21.2 (the ~200 live bodies' scans; the externals are rows now) |
| `liveness::LastUse::compute` | 18.1–22.4 | 16.5–18.6 |
| `check_resource_moves` | 12.1–17.3 | 16.0 (its whole-program helper sets: M?1) |
| `compute_clone_sites` | 16.2–16.4 | < 2 |
| the remaining tables, labels and records | 18.4–22.3 | 12.7–17.0 (+ the label tables 4 + the partition 6.5, marked separately now) |
| the stage hints and auto fills | 11.5–16.6 | 2.8–3.0 |
| the view, clone and hmr plans | 6.4–8.4 | 11.9–12.4 (noise; three of its sweeps routed after this run) |
| `plan_resource_drops` | 6.9–7.4 | 6.3–8.9 |
| `check_view_escape` | 6.7 | 4.2 |
| `check_container_resource_arguments` (R10) | 4.7–7.1 | 6.9 |
| `check_invalidation` | 4.5 | 5.5 |
| `record_lazy_arguments` | 4.6 | 6.3 (M?2) |
| `check_class_written_twice` | 4.3–4.8 | < 2 (in the Class A window now) |
| (phase line) checks | 342–367 | 221–270 |

Whole keystroke, instructions (load-independent): leaf 4.29 → 3.43/3.44 G (−20 %), leaf world mode 4.63 → 3.81 G (−18 %). `live-ranges=24 live-entities=12550` on the served world-mode keystroke (of ~150k entities).

Peak RSS of the server on the single-document leaf row: base 496–567 MB over runs, S7b 649–659; with `MALLOC_ARENA_MAX=1` base 506, S7b 512 — glibc per-thread arena fragmentation from the larger transient working set (the live held rows), not retained data (the checked cache totals 2.3 MB on this row; the cold check's peak RSS is −1.8 %). The world-mode row: 844 → 836.

## The cold check (T2's rows, `perf_gate.py measure`, instructions:u, base → S7b)

| subject | base | S7b | |
|---|---:|---:|---:|
| example:browser | 1,368,898,215 | 1,350,880,813 | −1.32 % |
| example:canvas | 1,377,833,410 | 1,359,122,664 | −1.36 % |
| example:fullstack | 2,873,237,469 | 2,820,940,940 | −1.82 % |
| example:math | 249,075,402 | 247,671,967 | −0.56 % |
| example:reactive-ui | 1,642,860,053 | 1,624,394,378 | −1.12 % |
| example:router | 1,531,341,517 | 1,512,769,970 | −1.21 % |
| example:rpc | 1,766,112,628 | 1,735,752,521 | −1.72 % |
| example:ssr | 3,447,474,577 | 3,390,066,757 | −1.67 % |
| example:todo | 4,306,876,257 | 4,226,822,672 | −1.86 % |
| example:walkthrough | 4,433,311,647 | 4,344,475,949 | −2.00 % |
| example:watch | 314,636,898 | 308,897,021 | −1.82 % |
| genapp:46 | 7,666,862,470 | 7,647,404,852 | −0.25 % |
| plain:160 (growth row) | 2,828,482,959 | 2,845,154,460 | +0.59 % |
| plain:320 (growth row) | 5,455,178,391 | 5,488,542,060 | +0.61 % |

Every ceiling subject comes in under the base (the view bindings and origins computed once, the calls index on first ask, fewer type queries); the two plain packages — 160/320 trivial modules, growth-ratio subjects with no ceiling (x1.93 ≤ x2.3 holds) — pay +0.6 % for the held walk's row materialization on a check that serves nothing. Three cold-check costs were found and removed on the way (callgrind on plain-160 and genapp-46): the iterator's un-inlined `next` (+2 %), the walk/sweep threshold (a walk of a package half the size of its table is slower than the sweep: `WALK_BELOW_PERMILLE` 500 → 200), the shape asked after the range instead of before it (the base's `.values().filter_map(shape).filter(reusable)` order, restored by `live_entries_where`), the value seams expanded unconditionally (the base expanded them only with a candidate; restored), and a `Vec` of conventions cloned per call (54k clones on genapp; a reference now).
