## native-52: rebase onto C1 done, every gate green

**Branch `native-52`, new tip `896c9621`, base `029d5ab4` (C1).** Nothing is pushed and nothing of mine is still running. `native-52-STATUS.md` is untracked and current.

### Commits after the rebase
| commit | was | item | family |
|---|---|---|---|
| a9d7d558 | 1092eaf2 | F135 slice 1 | fix |
| 9b3d07c8 | f58b1c60 | F?2 | miscompile |
| 93a880dd | 5e82daa6 | F136 | fix |
| b6883224 | 04a2bb2b | F137 | fix |
| f268911c | d2771ee4 | F?3 | miscompile |
| f6d5894d | 757c784a | F135 slice 2 | fix |
| 896c9621 | dc883ba2 | your one-line retarget of the F138 pin | (no entry) |

### Conflicts and how they were resolved
- **CHANGELOG.md, at the F135 commit only.** Your `## Unreleased` entries (B619, M141, N173, N174, M142) come first, then mine. The parity check reads 11 entry heads and 11 family markers.
- **analyzer.rs merged without a conflict, but needed one adaptation.** `compute_clone_sites`' rewrite keeps the live walk, and my F135 loop sits inside it, applied to each live `Expr::Call`.
  - The loop now gets the call index through the lazy `calls_index(self)` instead of an eager `&calls`.
  - It also skips any cell that is never written in place before asking for the index, so a served keystroke that reaches no such read still builds no index.
- **Carried as you asked:** the read-spine receiver test (B274's arm through `shared_read_spine_cell`), plus `shared_read_spine_cell`, `reaches_an_in_place_write` and `one_span_space`.
- **The derive-span scoping is in all four places:** `spans_an_in_place_write` and the three call-index walks (`spans_a_call_reaching_a_write`, `function_reaches_an_in_place_write`, `reaches_an_in_place_write`).
- **Not scoped:** `spans_a_cell_hazard`, which now shares the B457 index, does not get the derive-span scoping; my items never needed it there.

### Gates at 896c9621
- **Full suite** (`--cargo-profile ci-test -E 'not binary(deep_nesting)' -j 6`): 10542/10542 passed, 32 skipped.
  - `ci_ignored_pins` 12/12, `hygiene` 3/3, `corpus` 14/14.
  - The core differentials: `check_scope_differential` 16/16, `permutation_differential` 7/7, `edit_replay_differential` 24/24, `replay_differential` 2/2, `infer_differential` 148/148.
  - `native_differential` 275/275, with the copy, leak and shared censuses matching their tables.
- **Native sweep mode** (`VILAN_NATIVE_DIFFERENTIAL=1`): 275/275. Triple 130/128/2/0 (unchanged); platform-bound 9/6/3/0, async 7/4/3/0.
- **Deep-nesting canary at 1536 KiB:** 18/18.
- **vilan-lsp binary:** 1103/1103 passed, 21 skipped.
- **clippy** (`--workspace --all-targets -D warnings`), **`cargo fmt --check`** and **`vilan fmt --check .`**: all 0.
- **`ci-local.sh perf`:** T2 green, growth x1.928.
- **kolt cold-check RSS:** median 265,240 KB at the tip vs 265,868 KB on 0.49.0, which is −0.2%. The base is the installed 0.49.0, not a release build of C1.

The rest of my earlier report stands. Analyzer functions, now as of the C1 form:
- **Changed:** `compute_clone_sites` (the F135 loop and the B274 receiver arm), `spans_an_in_place_write`, `spans_a_call_reaching_a_write`, `function_reaches_an_in_place_write`.
- **New:** `shared_read_spine_cell`, `reaches_an_in_place_write`, `one_span_space`.
