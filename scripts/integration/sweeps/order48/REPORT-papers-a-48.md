## papers-a-48 report: the analyzer pass map (M110's prerequisite for Order 49)

The paper is written: `/home/reed/code/vilan-lang/proposals/projects/vilan/proposal/analyzer-pass-map.md` (735 lines). Nothing is committed in proposals or in the vilan tree. Analysis found 5 new items, including one real editor bug (B?1, below).

**How it was measured.** All on next @e75bc57c, release build, against a copy of the owner's kolt working tree (the uncommitted store patch included). No git was run in kolt.
- **`vilan check` of kolt:** 18.93 G instructions (hardware counter), 3.675 s CPU. Callgrind on the profiling build gives 17.74 G.
- **Per-pass split:** `VILAN_PHASE_TIMING=passes VILAN_COUNTERS=1`, median of 5 runs. Load was 17–21, so the CPU figures are read as shares.
- **Editor:** `lsp-latency.py --source` on a release `vilan-lsp`.
  - A `views.vl` keystroke the hot-set world serves: 9.97 G.
  - A `model.vl` keystroke the impl guard refuses: 14.11 G.
  - Pass medians are over 6 analyses of each kind.
- **`--explain-cost`:** it attributes solver work to declarations, not to passes (the top client entry is `sidebar_shell` at 9,287 units), so it informs S5–S7, not this table.

### The pass table in brief

The served-keystroke share is out of 1,510 ms of analysis CPU.

| pass | kolt check share (≈ instructions) | served keystroke | depends on load order? |
|---|---|---|---|
| drain + walk (parse, macros, walk) | 12.7% (2.4 G) | 4.4% | yes: ids are minted in load order (pinned by design); B573 twin selection; B554 |
| `resolve_world`, pre-entry (fixpoint 15.5%) | 17.6% (callgrind 3.16 G) | 0 (S1 skips it) | yes: B553, failures are reported before the entry walks |
| `build()` (resolve again + `finalize_build`) | 1.1% | 2.2% | data flow only |
| bound audit `check_generic_bound_satisfaction` | 7.2% (callgrind 1.92 G) | **13.5%** | data flow; Class C |
| `infer_bumps` / `infer_borrows` | 3.2% | 2.9% | call-graph fixpoints |
| Class A window (14 checks) | ~2% | 1.7% | **yes: B?1** |
| R10 / R11 / moves / drop planning | ~7% | ~5.5% | data flow |
| liveness, capture plan, clone sites, resource types, label tables | ~10.7% | ~13% | data flow; one tree rewrite comes before them |
| contexts + call graph | 5.5% | 10.2% | rewrites the tree; the graph is built 4 times on kolt |
| async inference | 5.0% | 7.4% | must follow the context rewrite |
| platform colour | 2.1% | 3.2% | data flow |
| const pass | 14.7% (callgrind 3.92 G = 22%) | **29.8%** | **skipped whenever the program has any diagnostic** |
| emission (CLI only) | 5.9% | — | skipped on errors |

### Special cases to delete, and the invariant that replaces each

- **B553:** global facts are registered before any failure is reported. M121 door (b) covers the impl half; the Context half is untraced.
- **B554:** a diagnostic's location must not depend on file names; report the conflict at the declaration and name every push.
- **B560, E267 (closed) and B561 (open):** one function enumerates every module, nested ones included.
- **Macro-reference order (incr-47) and B547:** a resolution that picks between candidates waits until the candidate set is complete. The macro-reference fallback is still a first match in load order.
- **B573 and B?2:** the analyzer's configuration is fixed before its first pass, and a stored world never renders a workspace fact its key does not include.
- **B?1:** a Class A check may skip a reused body only if every table it writes for a later pass is recorded or recomputed.
- **M?5:** never pick by first match in a load-ordered table, and never store an index into one.

The paper (§6) also lists what the edit-replay differential proves and what it does not. Its main blind spot: both its legs share the clean pipeline, so B553, B554, B573 and B?2 cannot show up in it. A permutation differential (same package, reversed file names) is proposed.

### Questions for the owner, with recommendations
1. **S2's first table:** the bound audit's prefix call sites, keyed through M123's memo. Ask solver-48 to key that memo without TypeIds. If M123 doesn't confirm, start with the label tables (lowest risk).
2. **S3:** no pass reorder needed. It does need:
   - the context rewrite and `[track_caller]`'s locations turned into tables, so one call graph can be stored;
   - seeds computed from the prefix alone, so a deleted `get()` can shrink the result;
   - borrows and bumps added to the list;
   - M121 door (b) landed first.
3. **S5 spike must assert:**
   - every walk-minted id stays inside its item's window;
   - the four ruled positional answers and the M?5 sites are unchanged;
   - no TypeId is shared across items, counting the ~16k slots checks mint after types settle;
   - the permutation differential is green (except B554);
   - the corpus is byte-identical with windows forced on.
4. Build the permutation differential in Order 49, before S2, with B554 pinned as its known red.
5. Set the platform when the analyzer is constructed; render `platform_reason` and `prelude_repair` when a diagnostic is published.
6. Extend M19's Class A contract to tables. Fix B?1 by recording the suspension checks for every body, and add a "post-pass verdict in a prefix module" case to the differential.
7. Replace the M?5 first-match sites with the ruled ranking before door (b) reorders `implementations`.
8. Keep the clean-program gates, and write "valid only for a clean program" into S4's cache key.
9. Keep the map current: a lane that adds or moves a pass updates §3 in the same commit, keyed by the `[vilan pass]` names.

### Finds filed
In `sweeps/order48/newitems48-papers-a.json`; repros under `sweeps/order48/papers-a-48/finds/`, scripts under `papers-a-48/tools/`.
- **B?1 (reproduced in the LSP, the real bug):** the editor drops a module's view-across-suspension errors on every reusing analysis. `vilan check` refuses the program. The LSP shows the errors on the cold analysis, then `[]` after one keystroke in the entry, and still `[]` after the keystroke is undone. Under S1 the errors flicker. The cause is `check_invalidation`'s `reusable_entity` filter: reused bodies are never enrolled in `view_suspension_checks`, and nothing records it. Repro: `finds/suspend_reuse` and `finds/suspend_reuse_hot`, driven by `lspprobe.py`.
- **B?2 (reproduced):** same root as B573. A module's diagnostic note says "analyzed under node" in a browser build; `platform_reason` and `prelude_repair` are also read before they are assigned.
- **N?3:** three `resolve_world` phase buckets are mislabelled (`contexts`, `locals`, and the parts hidden inside `conformance` and `binder-bounds`).
- **M?4:** S3's list is missing `infer_borrows` and `infer_bumps` (104 ms on the client leg).
- **M?5:** four first-match-by-load-order sites. Found by reading the code; no diverging repro was built.

**For incr-48 (not filed, M122 is theirs):** M122's answer is measured. A broken keystroke is 23% cheaper because the const pass is skipped whenever any diagnostic exists (`const_eval.rs:862`), plus emission on the CLI (14.53 G against 18.93 G).

### Worktree to reap
`/home/reed/code/vilan-lang/vilan/.claude/worktrees/papers-a-48`, branch `papers-a-48` at e75bc57c. It has no commits and no source changes. Its `target/` holds the release and profiling builds, the kolt copies and the logs under `target/papers-a-48-scratch/`. No processes are left running.
