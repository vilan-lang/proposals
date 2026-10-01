# perf-kolt-45 — why `vilan check` on kolt is slow (investigation, 2026-10-01; Opus; condensed by the integrator)

**A v0.42.0 compiler regression, not kolt's code.** Quiet machine: `vilan check .` on kolt HEAD = 8.0–8.6 s wall, 7.2–7.8 s user, **1,087 MB** peak RSS. v0.41.1 on kolt f04d4cb = 2.53 s wall, 2.30 s user, 280 MB. Trigger: A142 R39 (25c740d3, `[resource] trait Flow`/`Pipe`) makes every std reactive generic called with a pipe an R11 "generic instantiated at a resource".

Client entry, thread-CPU ms [v0.41.1]; `checks` totals 4,248:
1. `compute_resource_types` 2,352 [76], +481 MB — 1.78M roots, memo misses on non-interned types (→ M95)
2. R11 `check_resource_generic_instantiations` 570 [10.6], +109 MB — 27 instances × ~53k minted ids (→ M94)
3. `compute_clone_sites` 815 [13] — B457's summary is O(functions × expressions) (→ M96)
4. emission walk `transformer::diagnose` 846 [188] — impl selection per `select_member` (→ M98)
5. post-passes 1,300 [710] — `refined_edges` computed twice (→ M97); `lib/search.vl` const-interp 213
6. Program drop 290

Not concentrated in any kolt module: cost follows the import closure (empty file 417 ms; `lucide/lib.vl` 1,094; `model.vl` 1,934; anything reaching the ui/theme stack 4.1–5.0 s; `client.vl` 5.7 s). Entries are checked SERIALLY (first member alone; → M100). CLI reuse is in-process only (`reused 0/N` cold); in `--watch`, a full server hit (53/53) still pays 96% of `checks`, and the client re-pays everything on a `model.vl` edit (→ M99). `~/.vilan/check-cache` is macro tables only, unpruned (→ N137).

Fixes M94 + M95 + M96 + M97 should return the client to ~2 s CPU and ~400 MB. Instrumented build: worktree `perf-kolt-45` (`VILAN_PASS_TIMING=5`).
