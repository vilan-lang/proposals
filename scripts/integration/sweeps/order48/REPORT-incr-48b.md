## incr-48b: the CI perf regression from the incr-48 merge, fixed

The `ci` rows are back under their ceilings by every check I could run here. Commit **`6d34df79`** on branch `incr-48b`, worktree `vilan/.claude/worktrees/incr-48b`, one commit on `origin/next` `8ab08bb2`, family `performance`, with its CHANGELOG entry. Nothing is pushed. Next has since moved to `b63e0e5b` (editor-48). Against it, `analyzer.rs` merges cleanly and only `CHANGELOG.md` conflicts, because both sides appended to `## Unreleased`; keep both. I did not rebase, since you named 8ab08bb2 as the base.

### The split
Measured with instructions:u on `vilan check`, minimum of 3 runs, using `perf_gate.measure_subject` and a scratch build with switches that are not committed. "Base" is the merge's parent, `4b4a63c6`, which CI passed on the same ceilings.

| subject | the merge | merge, reach record off | merge, const cache off | both off |
|---|---|---|---|---|
| math | x1.0062 | x1.0006 | x1.0062 | x1.0006 |
| watch | x1.0067 | x1.0007 | x1.0067 | x1.0007 |
| router | x1.0064 | x1.0000 | x1.0064 | x1.0000 |
| browser | x1.0071 | x1.0005 | x1.0071 | x1.0005 |

All of the regression was the reach record. The const cache's key hashing costs under 0.001% and is unchanged.

### The fix
I could not make the record conditional on a hot seed. B553's fix needs it on the CLI too: an entry impl a module calls is only found through the record. Instead, which questions get recorded is now read off the late files' syntax before anything resolves (`ReachFilter`; the late files are the entry and, in a hot-set world, its modules):

- **An impl on a struct or enum the late files declare asks for nothing.** No stored module can name such a type, and derive and `[service]` output is written on the late file's own item.
- **An inherent impl on a foreign type** asks for its member names only.
- **A foreign trait impl, or an item macro,** asks for everything.
- **Late files with none of these record nothing.** That covers every gate example: even router's entry impls are on its own types.

The filter is part of the base cache's key, so a world recorded for one set of late impls is never served to another.

### Measured after the fix (instructions:u, ratio to 4b4a63c6: the merge → this commit)
| subject | the merge | this commit |
|---|---|---|
| math | x1.0062 | x1.0004 |
| watch | x1.0067 | x1.0007 |
| browser | x1.0071 | x0.9997 |
| router | x1.0064 | x1.0002 |
| fullstack | x1.0029 | x0.9998 |
| reactive-ui | x1.0072 | x1.0007 |
| canvas | x1.0071 | x1.0004 |
| rpc | x1.0058 | x1.0003 |
| todo | x0.9986 | x0.9999 |
| ssr | x1.0005 | x1.0008 |
| walkthrough | x0.9954 | x1.0005 |

- **`ci` class under callgrind:** `perf_gate.py gate --class ci --counter callgrind` on this commit gives T2 green, every row between x0.96 and x0.989 of its ceiling. This machine's callgrind counts run 1–2% below CI's, so that run cannot show the regression by itself. The numbers to trust are the hardware-counter ratios above: within +0.08% of the parent CI accepted.
- **kolt session:** `theme.vl`, `model.vl` and `styles.vl` are still served from the hot-set world, with `hot-refusal` 0 on all four files and late writes 0. Clean keystrokes cost 6.91 / 6.85 / 6.80 G, the same as before the fix. Those three hot sets still record everything, because `prefs.vl`'s `impl HashMap<..> with Json` is a foreign trait impl; that is LSP-only cost.

### The pin
- **New counter:** `Census::reach_questions`, also printed on the `VILAN_COUNTERS` line as `reach-questions=`.
- **Pin:** `edit_replay_differential::a_check_whose_late_files_write_no_foreign_impl_records_nothing`. A check of a package with no foreign impl records 0 questions; B553's entry-impl package records more than 0. With the filter planted to record everything, the pin goes red at 1,899 questions.

### Gates on 6d34df79
- `cargo nextest run --workspace -j 6`: 9835 of 9835 passed, 35 skipped. That includes `edit_replay_differential`'s 11 tests, both legs, and every plant still red (`HotSetReplay`, `PrefixUnvalidated`, `ImplGuardOff`, `UseInferredGuardOff`, `ConstCacheUnvalidated`, `ConstKeyWithoutWorld`).
- `native_differential` with `VILAN_NATIVE_DIFFERENTIAL=1`: 202 of 202.
- clippy `--workspace --all-targets -D warnings` and `cargo fmt --all --check`: clean.
- `ci-local.sh vilan-fmt`, `windows` and `perf` (local class): all green.
- The machine was loaded throughout (load average 19–48), which is why I report instruction counts and not CPU time.
- Not verified: CI's Windows runtime (only the cross-clippy ran here).

### Functions touched (analyzer.rs)
- New: `ReachFilter` and `ReachFilter::of`.
- Changed: `ImplReachLog` (new `filter` and `questions` fields), `begin_impl_reach_log` (takes the filter), `end_impl_reach_log` (writes the census), `note_member_query` and `note_trait_query` (filtered), `BaseCacheKey` (new `reach` field), and `analyze_inner` (computes the filter and records only when there is one).
- incremental.rs: `Census::reach_questions`, and the counters line in `report`.
- No new `[vilan pass]` name.
