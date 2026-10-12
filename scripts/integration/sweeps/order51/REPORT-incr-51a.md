incr-51a hand-back at checkpoint C0. Both items are done, every gate is green, nothing is pushed, and none of my processes are still running.

**Branch:** `incr-51a` in `/home/reed/code/vilan-lang/vilan/.claude/worktrees/incr-51a`
- Base: ca407da0 (origin/next). Tip: **2642fae8**.

**Commits:**
1. **c49ae5ee — N169 (family: performance).** The walk's frame is smaller, and the canary at 1536 KiB is green.
   - `walk_expr_node_inner` was 27,184 B and `walk_expr_node` 1,024 B per level (debug). They are now 5,048 B and 584 B, so every level shares 5,648 B. Optimized, that is 640 B.
   - One level of the canary's chain went from 28,208 B to 8,288 B. The canary now fits from about 900 KiB (it needed 1,552 KiB before).
   - `VILAN_COUNTERS` prints `[vilan walk-frame] per-level=<N>B` once per process.
2. **2642fae8 — E294 budget half (family: performance).** The base cache's budget is now sized by the session's entry worlds.
   - The "leaf keystroke + pause" row went from 14.25 G to **10.55 G** instructions (x0.74).
   - The server world misses on **1 pause in 6** (it was 4 in 6).

**Functions changed in analyzer.rs** (no mono.rs or emitter changes):
- N169:
  - `walk_expr_node`: its depth refusal moved to a new cold method, `refuse_walk_depth`.
  - `walk_expr_node_inner`: lost 23 arms to new `#[inline(never)]` methods, with bodies moved verbatim: `walk_member_accessor_entity`, `walk_let_entity`, `walk_lift_region_entity`, `walk_for_in_entity`, `walk_assign_entity`, `walk_if_entity`, `walk_let_destructure_entity`, `walk_export_entity`, `walk_call_entity`, `walk_import_entity`, `walk_match_entity`, `walk_ascribe_entity`, `walk_macro_invocation_entity`, `walk_struct_initializer_entity`, `walk_binary_entity`, `walk_macro_block_entity`, `walk_multiline_string_entity`, `walk_use_entity`, `walk_try_assert_entity`, `walk_lift_entity`, `walk_for_entity`, `walk_is_entity`, `walk_func_return_entity`.
  - New `refuse_in_walk`: the walk's eight fixed-message refusals now call it.
  - `analyze_over_world`: one call to `depth_stats::report_walk_frame_once` added.
  - In `depth_stats.rs`: `enter_walk_level`, `leave_walk_level`, `report_walk_frame_once`.
- E294:
  - `BaseCacheState` has a new `session_entries` field, and `retained_keys` / `budget_in_force`.
  - `evict_to_budget` changed: the bound is now the flat budget plus every retained world a session entry names, and none of those worlds can be evicted.
  - `base_cache_admit` now also learns the session entries' keys.
  - New: `redeclare_entries`, `set_base_cache_session_entries`, `base_cache_session_entries`, `base_cache_budget_in_force`.
- Late writes stay at 0 (12 counters lines on kolt).

**vilan-lsp changes (E294):**
- `declare_live_entries` now also declares every declared entry of every package an open document belongs to. It reads them with `dead_items::entry_paths`, and the set is withdrawn when a package's last document closes.
- The session trace's `base_cache_budget` now reports the bound in force.
- The M67 walk harness declares the entries the same way the server does. `VILAN_E294_SESSION=0` gives the old flat policy.

**Where the premises were wrong:**
- **N169, where the frame grew:** the window bookkeeping is not on the recursion's path at all. The id windows wrap each module item in `walk_module_items`, below the walk, and they are off on these analyses.
- **N169, the bisect:** it does not hold. The commit before S6 (56975c4b^) also fails at 1536 and passes at 1552, exactly like the base. S6 added only about 7 KB of baseline and nothing per level.
- **N169, what the canary actually measures** (read with gdb at the overflow):
  - 33 levels at 28,208 B each. The frame had regrown about 1.8 KB per level, one arm at a time, since Order 44.
  - About 636 KB of the analysis's own baseline under the walk. `analyze_inner`'s frame alone is 214 KB unoptimized.
  - The item's "fits 1664 KiB" was loose: the real threshold was 1,552 KiB.
- **E294:** the eviction premise holds on v0.48.0 (4 of 6 misses reproduced). The "+9% VmHWM at 4096 MiB" did not reproduce: on the base, 4096 MiB read 906 MB against 1,029 MB at the default budget.

**Gates, all at the tip:**
- Full suite (`--cargo-profile ci-test -E 'not binary(deep_nesting)'`): 10,274/10,274 passed, 31 skipped. Within it:
  - `ci_ignored_pins` 12, `hygiene` 3, `corpus` 13
  - `check_scope_differential` 15
  - `native_differential` default mode 259, `edit_replay_differential` 19, `permutation` 6
- Native differential, sweep mode (`VILAN_NATIVE_DIFFERENTIAL=1`): 259/259.
- Deep-nesting canary (dev profile): 18/18 at 1536 KiB and 18/18 at 2 MiB.
- `cargo clippy --workspace --all-targets -- -D warnings`, `cargo fmt --check` and `vilan fmt --check .`: all clean.
- `ci-local.sh perf`: T2 verdict green. Every subject is between -0.063% and +0.002% against the base on the same box. No bump row needed.
- kolt cold check:
  - RSS median 268,732 KB against the base's 265,564 KB (+1.2%).
  - Instructions flat within noise: median 13.377 G against 13.359 G over 7 alternating runs.

**Pins:**
- N169: `the_walks_per_level_frame_is_printed_once_under_the_counters` (CLI). It is red on the base binary, which prints no line.
- N169: `the_walks_own_probe_refuses_the_chain_when_the_visitors_fit` now declares 4.5 MiB instead of 8. The 490-link walk (about 4.7 MiB now) fit under the old 7 MiB floor. The measured window runs from about a 3.6 MiB declaration (the syntactic visitors fit) to about 5.7 MiB (the walk is still refused).
- E294: `the_session_entries_worlds_are_sized_into_the_budget` (core). Red before the eviction change: 1 world retained instead of 3.
- E294: `the_packages_entries_size_the_base_cache_while_a_document_is_open` (server). Red with the declaration removed: it reads (0, 0) instead of (2, 2).
- The S6 pins and the differentials are untouched.

**The lsp-latency rows** (release build, lucide-carrying kolt copy at `target/incr-51a-scratch/kolt`, 5 runs):
- Two of the seven rows are refused by the harness because their anchors are gone from today's kolt: "model.vl keystroke" and "parse break". I measured the six that run.

| row | base instructions | tip instructions |
|---|---:|---:|
| leaf keystroke | 4.30 G | 4.30 G |
| leaf keystroke + pause | 14.25 G | 10.55 G |
| world mode | 4.66 G | 4.66 G |
| shared.vl | 1.67 G | 1.67 G |
| model.vl, importers open | 5.45 G | 5.45 G |
| css keystroke | 6.53 G | 6.54 G |

- CPU was **not quiet**: loadavg was 9–16 because the other lanes were building.
  - Pause row CPU to idle: base 2,850–3,360 ms, tip 2,160–3,170 ms.
  - The other rows are within noise.
- Pause-row VmHWM: median 1,002 MB against the base's 995 MB. Ranges: tip 954–1,290, base 972–1,029.
- Resident cost, from M67's walk sweep at 192 MiB: about 140 MB more held at the end (665 → 803 MB). That buys 18 misses instead of 20 on the scan and 27 instead of 29 out of 30 on the working set.

**Finds filed** (`sweeps/order51/newitems51-incr-51a.json`; repro in `sweeps/order51/incr-51a/finds/analysis_baseline_frames.md`):
- **N?1:** the analysis's debug-profile stack baseline under the walk is about 636 KB. `analyze_inner` is 214 KB, `analyze_over_world` 83 KB, and four `catch_unwind` layers of about 28 KB each move `Program` by value. After N169 this baseline is about 70% of what the canary measures.
- **M?1:** M67's 192 MiB figure is stale on today's kolt. Its own sweep misses 20 of 20 on the scan and 29 of 30 on the working set, against the 17/19 and 21/30 M67 recorded.

**Proposals edits, uncommitted for the integrator:** `proposal/std-prefix.md` §1.3 gains a "budget half landed" paragraph. No pass moved, so the pass map is untouched.

**Questions for the owner:**
1. **E294's memory:** should the sized-in amount be capped (for example at the flat budget, so the bound can at most double) for packages with many entries? Kolt's two entries add about 147 MiB of weight. I recommend no cap now and revisiting only if a package with more than 2 entries shows up, since the clock already pays one analysis per entry every pause.
2. **M?1:** re-measure and re-rule M67's flat figure now, or wait for P1/P2? I recommend re-measuring at Order 52's P2, because the pinned prefix changes what a miss costs.
3. **N?1:** queue the baseline-frame work, splitting `analyze_inner` and boxing the `Program` through the `catch_unwind` layers? I recommend it after S7 (sizing S–M); it is not urgent, since optimized frames are a small fraction.
4. **The canary's margin:** the canary now fits from about 900 KiB. Should the seal tighten it to 1,280 KiB to warn earlier? I recommend keeping 1536 (R-i as ruled) and recording the threshold at each seal.

My status file is `incr-51a-STATUS.md` in the worktree (untracked).
