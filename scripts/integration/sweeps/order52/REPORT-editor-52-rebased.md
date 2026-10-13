## editor-52: post-rebase report (Order 52, Opus 5.5)

**`editor-52` is rebased onto origin/next e4255f60 and every gate is green.** The new tip is **a5d70c75**, 22 commits over next. Nothing was pushed. My temporary `editor-52-base` worktree is removed, no processes of mine are running, and `editor-52-STATUS.md` is untracked.

### Rebase
- **Conflicts:** only the first commit (E313) conflicted:
  - In `analyze_over_world`, both sides changed the same lines. I kept S7b's `phase_pass_mark("the class D partition and the records")` and my `type_definitions(&expr_type_ids, &hover_rows)` call.
  - In CHANGELOG, each side's entries are kept, with my entries after next's.

  The other 19 commits applied without conflict.
- **`stage_hints` after the merge:** S7b's restored-row skip (`hint_row_restored`) runs first, then my E303 element-link skip.
- **The hover-row tail** still renders every file's rows after S7b's held fold.
- **New commits (2) since the earlier report:**

| sha | item | family |
|---|---|---|
| 9e229ae0 | E313: a cold view keeps its rows on a served keystroke — a pin that a keystroke in one module, served from the stored world (`base-hits=1`, `records-served=1`), leaves a cold module's view with its pattern, call-label and definition rows; the E313 CHANGELOG entry names it | fix |
| a5d70c75 | N176: the language server caps glibc's malloc arenas at one | tooling |

The full list, in order (the first 20 are the earlier report's commits, with new shas): E313 (two commits), E305, E303, E311, E299, E298, E307 (two), E304, E308, E310 (two), E312, E306, E300, E301, E302 (two), B620 editor half, N172, N176.

### N176
- **Change:** `memory::limit_arenas()` calls `mallopt(M_ARENA_MAX, 1)` first thing in `main`, on glibc targets only. If the environment already sets `MALLOC_ARENA_MAX`, it is left to glibc, so a run without the cap is still possible.
- **Setting:** I chose 1 over 2 on the numbers below.
- **Measurement:** the tip binary on the kolt copy, all seven rows plus the opening rows, 3 runs each, load 8–16.

| | default arenas | 2 arenas | 1 arena |
|---|---|---|---|
| peak VmHWM | 1006 MB | 932 MB | 716–732 MB |
| leaf row VmHWM | 652 MB | 536 MB | 514–533 MB |

- **The cap built into the binary**, with no environment variable, measured leaf 532 MB.
- **Instructions to idle are unchanged** by the cap (leaf 3.45 / 3.45 / 3.43 G).
- **Keystroke columns** (hover / completion / inlay / tokens) stay under 5 ms in every configuration.
- **One weaker signal:** with one arena, some idle-CPU completion and inlay readings came in higher (css idle completion 2.5–3.3 ms against 1.6–1.8). On a box at load 8–16 that may be noise; a quiet re-take at the seal would settle it.

### The editor rows' cost, re-taken on the merged tree
Next against my tip, both with `MALLOC_ARENA_MAX=1` so arena noise is out.

| row | instructions to idle, next → tip | change |
|---|---|---|
| leaf | 3.37 → 3.43 G | +1.8% |
| leaf + pause | 8.34 → 8.47 G | +1.6% |
| world mode | 3.74 → 3.79 G | +1.3% |
| importers open | 4.55 → 4.61 G | +1.3% |
| css | 5.66 → 5.71 G | +0.9% |
| parse break | 5.64 → 5.69 G | +0.9% |
| parse repair | 5.77 → 5.81 G | +0.7% |
| shared.vl keystroke | 1.32 → 1.32 G | flat |
| model.vl keystroke | 1.28 → 1.29 G | flat |

- **Instructions:** the earlier +1.3% is confirmed, at +0.7..+1.8% on the moving rows.
- **Peak VmHWM:** 711 → 716..727 MB, so +5..16 MB. That corrects the earlier +27 MB.
- **Why the earlier figure was off:** without the cap the two sides read 900 vs 1006 MB, and that gap was arena fragmentation, not the rows.
- **Keystroke columns** do not move.
- I updated the M?1 find with these figures.

### Gates on a5d70c75
- **Full suite** (`--cargo-profile ci-test -E 'not binary(deep_nesting)' -j 6`): 10580/10580.
  - corpus 36
  - check_scope_differential 16
  - permutation_differential 7
  - edit_replay 24
  - native_differential 278
  - ci_ignored_pins 12
  - hygiene 3
  - the vilan-lsp binary 1127
- **Native differential, sweep mode** (`VILAN_NATIVE_DIFFERENTIAL=1`): 278/278.
- **vilan-lsp binary on its own:** 1127/1127.
- **Deep-nesting canary at 1536 KiB:** 18/18.
- **Lint and format:** clippy (workspace, all targets, `-D warnings`), `cargo fmt --check` and `vilan fmt --check .` are all clean.
- **Extension:** `npm test` 28/28; `tsc` typecheck clean.
- **`scripts/ci-local.sh perf`:** green, T2 verdict green, growth ×1.928.
  - Cold rows against next's own release binary: +0.009% to +0.083% (todo −0.70%, which is noise).
  - No `[[bump]]` row; this is within the 1% tolerance.
- **kolt cold-check RSS medians, interleaved:** next 267.9 / 273.2 MB, tip 265.2 / 264.9 MB.
- **CHANGELOG parity:** 32 bold heads and 32 family markers under `## Unreleased`, every entry of next's and mine with its marker.

### Finds
Still four, in `sweeps/order52/newitems52-editor-52.json`:
- **E?1:** a type in the middle of a module path (`style::Length::px`) paints nothing.
- **M?1:** the hover rows are re-rendered on every analysis for every file; numbers updated as above.
- **E?2:** a signature drops an implicit parameter's trait arguments (`username: Signal` instead of `Signal<str>`).
- **E?3:** a returned `None` hovers as `Option::None`, without the instantiation.

### Questions for the owner
1–7 stand as in the first report. One new:

8. **N176's arena count.** Keep one arena? I recommend yes: it was the only setting that brought the peak back under next's uncapped 900 MB, and instructions do not move. A quiet seal re-take would confirm the idle-CPU columns.
