## editor-47: rebased onto 569fea15, all gates green

**The branch:** tip is `45fbdbd2` (`editor-47`), base is `569fea15`, which is origin/next 501a31e4 plus the incr-47 merge. Not pushed.

**The 14 commits on the new tip:**

| item | commit |
|---|---|
| B536 | aabb1f93 |
| B515 | 1f07fc78 |
| E253 | 303bafa6 |
| E263 | 9d864bb6 |
| E264 | a1833ab7 |
| E261 | b4ab2a75 |
| E262 | 1b99ab49 |
| E270 | e93b0ec5 |
| N141 | c9935e82 |
| E265 | 662842b6 |
| E269 | 65bfa744 |
| E267 | d7e1ce96 |
| B560 | 2e5563ee |
| B535/B536 adaptation to solver's flips | 45fbdbd2 |

### Conflicts and how I resolved them
Only one commit stopped: E261.
- **`CHANGELOG.md`:** I took 569fea15's file and re-added E261's entry under `## Unreleased`. Checked after the rebase: one `## Unreleased`, all 14 of my entries present once, no conflict markers.
- **`diagnostics-ledger.tsv`:** union. Upstream's numbered rows (through 665, debug-47's `dbg` rows) come first, and my single `NEW` row (E261's steer) sits at the tail.

Every other commit applied cleanly. That includes the analyzer, document.rs, formatter.rs and completion.rs seams.

### What moved under me, and what I checked
- **incr-47, `resolve_world`:** my E262 move (`resolve_context_clauses` before conformance) sits beside the new macro-reference call at the top; there was no textual overlap.
- **incr-47, `analyze_over_world`:** it still copies `unwired_method_calls` into `Program` (line 77218).
- **incr-47, the edit-replay differential:** it passes with E262's pass-order move and E253's table in place; it is part of the suite run below.
  - One thing not covered: E253's table lives in analyzer state. On a hot-set keystroke, a call in a stored prefix module relies on the stored world carrying the table. The differential's hover comparison only covers this if a fixture holds a call whose closure body is refused. I did not add one.
- **store-47, `completion.rs`** (`push_field_syntax` and the rest): merged cleanly, and the element-head, member-admission and auto-import pins still pass.
- **debug-47, `[track_caller]` and `formatter.rs` function-head printing:** no conflict with E265; the formatter tests are green in the suite.

### Gates on 45fbdbd2 (base 569fea15)
| gate | result |
|---|---|
| `cargo nextest run --workspace -j 6` | **9777 passed, 34 skipped**, exit 0 (load 2–7) |
| `native_differential` with `VILAN_NATIVE_DIFFERENTIAL=1` | **177/177** |
| `cargo clippy --workspace --all-targets -D warnings` | clean |
| `cargo fmt --all --check` | clean |
| `ci-local.sh vilan-fmt`, `windows`, `perf` | all green; T2 green, growth x1.938 (local class, no ceilings) |
| VS Code extension (scratch copy, main checkout's node_modules) | `npm test` 28/28, `tsc` clean |

### E121's six rows (taken: load was under 4)
Measured on kolt, 5 runs each, release builds of both sides, each with its own std. Kolt was copied with `cp -r` into scratch, minus `.git`; no git command was run in kolt. Load average was 0.81 / 0.90 at the base run and 0.90 / 0.89 at the tip run.

**The harness needed a one-line local fix first** (filed as N?5). The `shared.vl keystroke` scenario cannot run as committed. N145 re-anchored its edit and its completion request on the same text, `\t\tself.uuid.hash()`. The completion request is resolved after the edit, so the run stops with "the completion anchor … is not in src/shared.vl". I measured with a scratch copy of the script whose completion anchor is `("self.uuid.hash()", len("self."))`. That is the only difference; the committed script is untouched.

Each cell is base → tip, medians over 5 runs.

| row | metric (budgets.toml) | CPU ms | instructions to idle (G) | VmHWM MB |
|---|---|---|---|---|
| leaf keystroke | diagnostics_cpu_ms | 870 → 870 | 8.99 → 9.00 | 457 → 654 |
| shared.vl keystroke | diagnostics_cpu_ms | 220 → 230 | 1.51 → 1.51 | 507 → 655 |
| model.vl keystroke | diagnostics_cpu_ms | 260 → 240 | 1.84 → 1.84 | 507 → 655 |
| model.vl keystroke, importers open | cpu_ms | 1620 → 1630 | 13.79 → 13.78 | 616 → 833 |
| css keystroke | diagnostics_cpu_ms | 1070 → 1070 | 10.28 → 10.28 | 781 → 833 |
| parse break | diagnostics_cpu_ms | 1070 → 1050 | 10.28 → 10.28 | 794 → 833 |

- **Against the 500 ms target:** shared.vl and model.vl are green; leaf, importers-open, css and parse break are red. My lane does not move CPU or instructions on any row.
- **Keystroke path:** every request is at or under 2.3 ms, well inside 10 ms.

**Peak memory (VmHWM) is higher on the tip, and I have not attributed it.** It is not an E121 metric, and it is noisy:
- A second 3-run pass of two rows read 518 vs 456 (leaf keystroke) and 562 vs 529 (shared.vl) — still higher on the tip, but by much less than the first run's ~200 MB on the leaf row.
- My guess is E267, since the auto-import table now walks kolt's nested `src/lib/*` modules. That is unmeasured.
- The integrator may want a VmHWM look at the seal.

### Finds
- The integrator has already filed my earlier finds as B561, B562, E273 and B563.
- New: **N?5**, the harness anchor bug above, in `newitems47-editor.json`.

### Cleanup
- The temporary base worktree `.claude/worktrees/editor-47-base` has been removed.
- The base release target is left at `target/editor-47-scratch/base-target`.
- `LANE-STATUS.md` is current.

### Functions touched
Unchanged from my previous report. Nothing was added by this rebase beyond the two record merges (CHANGELOG and ledger).
