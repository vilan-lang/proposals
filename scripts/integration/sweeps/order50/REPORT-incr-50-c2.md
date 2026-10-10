# incr-50 — CHECKPOINT C2 (S6, the interface firewall over windowed ids) — report (received as a lane message, 2026-10-10)

Tip `56975c4b` on branch `incr-50` above `origin/next @7b0c238f` (the C1 merge). Above next: `9d4f1ea0`, `e07527a2`, `d67745ea` = spike-49's three commits cherry-picked from `spike-49 @c761e214` (one analyzer.rs conflict, the S3 seam field vs the spike's report field, both kept); `56975c4b` = S6 (family performance). The spike branch can be deleted now.

## What S6 built (R-b)
- Windows for all three id lanes laid out by the walk (`walk_module_items`, one window per top-level item in load order), every anchored mint relocated into its anchor's window (the spike's `all`) — ON for every EDITOR analysis (seeded, or reading aids), OFF for a cold `vilan check`; `VILAN_ID_WINDOWS=all|off|census|walk|types` forces a mode. Gated because forced-on windows cost kolt's cold check +0.9% instructions (13.32 vs 13.21 G) and +3.1% peak RSS (273.9 vs 265.6 MB): every slack type slot is a hole in the dense `Vec<Option<Type>>` type table. Gated: 13.22–13.24 G vs C1's 13.20–13.21; RSS 261.8 vs 267.9 MB.
- Type windows sized from the item's previous demand (`WINDOW_DEMAND`, keyed by the source PATH + item ordinal, written by `record_demand`; ×1.5 of the demand incl. spill). FIRST ANALYSIS ×4 OF THE WALK, NOT ×8 (deviation): ×8 padded a stored world past vilan-lsp's retention pin (4,892 KiB per released document vs its 4,240 bound; off 3,778, ×4 2,890) while overflow barely moves (×4 2,110 windows, ×8 1,860 of 4,602). An overflowing item spills to the tail and records its demand. Pin: a second analysis of the classes package reads a type span of 16,829 vs 34,901 with zero overflow.
- Run-length `type_id_sources` (`TypeSourceRuns`); tally currency stays one SourceId per minted slot (the M11/M41 census pin; 192 B run-length).
- Anchors for the resolve's prepped drains: std items/locals/assignments by the row's entity (`set_drain_anchor`), annotations and static accessors by the slot's window (`set_anchor_type`), impl conformance by the block's scope (`set_anchor_scope`); cleared before `finalize_build`. Unanchored resolve-phase type mints 5,486 → 3,057; finalize_build's 2,634 → 1,791; M134's six check passes keep 11,877 (C3).
- The stored world's windows inherited on a HIT only (`IdWindows::inherit`); the entry's windows keyed by its own path with fresh ordinals.
- "Body edit re-walks one module" pin: the leaf keystroke lays out exactly items(views.vl)+items(main.vl) windows and inherits more than it lays out (kolt: `windows-laid-out=43 windows-inherited=4578`).
- Standing counter pins: `relocated_outside_anchor == 0` on every leg. `writes_other == 0` IS NOT AN INVARIANT (find M139): a push into another module's use-inferred binding is such a write (the ERD classes leg reads 49); pinned at 0 on the leaf package and the spike's default pin, reported elsewhere; the drains' cross-item grounding split out as `writes_drain_other` (71 on kolt). It is the cross-item edge S7's per-item records must carry.
- The two new differential classes as the `id_windows` fixture (ERD + permutation): a derived prefix module, desugars, a bound refusal naming the derived type, three edits. Green — neither predicted red appears.
- The census only in debug builds or under `VILAN_COUNTERS`.

## Counters on kolt (release, served views.vl keystroke, world mode)
`graphs-replayed=2 context-log-replayed=1 seeded-passes=1 post-records-filed=0 windows-laid-out=43 windows-inherited=4578 windows-overflowed=1877 window-writes-other=0 window-outside-anchor=0`; late-writes 0. Client world 4,621 windows: entities walk 59,408 / 60 unwindowed / 4,784 relocated / 0 spilled; types walk 20,866 / 66,818 relocated / 15,667 spilled / unanchored resolve 3,057, build 1,791, checks 11,877; scopes walk 8,647 / 103 unwindowed; writes own=153 other=0 drain-other=71 tail=29; expr→type containment own 3,754 / foreign 1,532 (29%) / tail 50. The 1,877 overflowing windows are the stored world's (×4 at the world build; lucide_lookup-class items spill; sized right at the next world build) — a datum for S7.

## Session table (release, kolt copy; medians over keystrokes 2–10; instructions G / CPU ms; C1 → S6; loads 1.6 / 2–7)
views 4.62/620 → 4.64/680 complete, 4.14/570 → 4.15/620 mid; theme 5.15/680 → 5.16/710, 4.78/640 → 4.79/675; model 5.16/720 → 5.13/720, 4.88/675 → 4.85/670; styles 5.03/650 → 5.05/700, 4.75/610 → 4.76/755 (load spike). +0.2–0.4% instructions per served keystroke.

## E121's seven rows (CPU ms / instructions G; C1 at load 1.6 → S6 at load 2–7)
leaf 550/4.10 → 580/4.11; +pause 1880/13.72 → 2050/13.83; world 590/4.45 → 700/4.47; shared 210/1.58 → 220/1.59; model 230/1.61 → 260/1.62; importers open 670/5.44 → 910/5.42; css 770/6.31 → 950/6.41; parse break 750/6.29 → 960/6.42. Instructions +0.2% served, +1.6–2% on a whole-file re-walk. CPU load-polluted. E292 stays open: the remaining ms are the checks' resource/bound tail (~125 ms) and the walk (C3/S7).

## Gates (final tree 56975c4b)
`VILAN_ID_WINDOWS=all`: the four differentials 42/42, corpus goldens 13/13, native differential 247/247 — byte-identical; native 247/247 under the default. Full suite (ci-test, not deep_nesting) 10,188/10,188, 31 skipped; deep_nesting green; id_windows_spike 7/7; clippy -D warnings clean; fmt clean; vilan fmt --check clean. `ci-local.sh perf` T2 green (ci rows unchanged vs C1). RSS 261.8 MB vs C1's 267.9; forced on 266–269.

## Pass map (uncommitted, committed by the integrator)
§3.1 the module walk row; §3.2 the `locals` and `types` rows; §7.3 retitled "S5: the spike — and S6 as built". No pass added/removed/reordered. Find: M139 (writes_other is not an invariant — the cross-item edge S7 carries; S).

## Questions for the owner (recs)
1. ×4 not ×8 for the first analysis's type windows — accept ×4.
2. `writes_other == 0` pinned where it holds, counted everywhere, S7's records carry the edge (M139) — accept.
3. Windows off on a cold check (the 0.1%/3% gates vs the dense type table) — accept; a paged type table lifts it if the std prefix wants windows on a cold world.
4. tests/id_windows_spike.rs keeps the spike's name — rename at the C3 merge.

## C3 starts from
origin/next at the merge of this tip; M134 — one `set_anchor` per body in the six post-settle passes (compute_resource_types, check_container_resource_arguments, check_resource_moves, the bound audit, check_resource_generic_instantiations, plan_resource_drops); the census should read 0 of today's 11,877; then E292's rows again. Binaries bin-base/bin-c1b/bin-s6/bin-c2b and the kolt copy under target/incr-50-scratch/ for the seal.
