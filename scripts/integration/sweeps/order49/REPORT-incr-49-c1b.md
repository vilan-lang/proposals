## incr-49 — CHECKPOINT C1b (the Windows fix for the permutation differential)

**Tip `5411f6da`** on `incr-49`; nothing pushed. The fix is the one commit the integrator asked for, but the branch carries two commits BEFORE it that were already made when the priority note arrived — read the shape before merging:

| commit | what | state |
|---|---|---|
| a5d02cb0 | **M110 S2a** (the bound audit's record; family performance) | gated locally: ERD 12/12 + permutation 5/5 (bound plants red, served counter asserted), clippy vilan-core clean; NOT yet through the full suite or `ci-local.sh perf` (those come at C2) |
| d7da47a7 | `git merge origin/next` (e95b8f44) at that boundary — clean, CHANGELOG union auto-merged, merged tree builds | — |
| **5411f6da** | **the Windows fix** (family tooling) — `crates/vilan-core/tests/permutation_differential.rs` + CHANGELOG | gates below |

If you want C1b to land alone, `git cherry-pick 5411f6da` onto next applies cleanly (it touches only the test file and the CHANGELOG's `## Unreleased` head); otherwise merging the branch brings S2a along, which is gated as stated but has not had the suite. My recommendation: cherry-pick 5411f6da now (unblocks every Windows run), take S2a with C2.

### The fix
Cause as you read it: `normalize` relativized a row's package path by stripping `format!("{}/", root.display())`; on Windows the row carried `D:\a\…\vilan_m110_perm_…_6716_0\main.vl`, nothing matched, each leg kept its own directory and the sort put them in different orders. Now every path token and the root are compared with `\` read as `/` (`slashed`), the root's PROSE occurrences (a const read's resolved path) are replaced in either spelling, and the nesting prefix (`deep/`) and the renaming map read the slashed form; `canonical_offset` looks files up by the slashed relative path. Unit test `the_normalizer_reads_a_windows_hosts_rows`: a `NestedReversed` permutation of a two-file package, a rendering written with `D:\a\vilan\vilan\target\tmp\…\deep\pa_model.vl` offsets in a path token and in prose, normalized back to `<pkg>/model.vl` with canonical offsets — red before the fix (it kept the backslashed root in prose), green after.

### Gates on 5411f6da
- `cargo nextest run -p vilan-core --test permutation_differential --test edit_replay_differential -j 6`: **19 of 19 passed**, 1 skipped (the B554 pin) — this includes S2a's gates.
- `scripts/ci-local.sh windows`: **green** (the cross-compile clippy leg; the runtime is CI's to verify, as always).
- `cargo fmt --all --check` clean. Load during the runs 6–12 (the base measurements of C2 were running beside them; instruction counts unaffected).

### Early C2 numbers (taken while this ran; tip = d7da47a7 which is S2a + the merge, base = 445c9346, release builds, `scripts/lsp-latency.py --runs 5`, kolt scratch copy; load 1–12, so read the instructions)
| E121 row | base G / CPU-to-diag ms | tip G / ms |
|---|---|---|
| leaf keystroke | 4.55 / 590 | **4.23** / 600 |
| leaf keystroke + pause | 11.62 / 2320 | 10.90 / 2100 |
| leaf keystroke, world mode | 5.36 / 1070 | **5.05** / 730 |
| shared.vl keystroke | 1.62 / 350 | 1.60 / 240 |
| model.vl keystroke | 1.70 / 350 | 1.65 / 260 |
| model.vl keystroke, importers open | 6.04 / 930 | 5.96 / 740 |
| css keystroke | 6.40 / 960 | 6.38 / 840 |
| parse break | 6.41 / 1240 | 6.36 / 800 |

Tip session (clean keystrokes 2–10, hot-set world served, 0 refusals on all four files): views.vl 4.60 G, theme.vl 5.35, model.vl 5.41, styles.vl 5.32 (the complete-statement keystrokes 5.21 / 5.71 / 5.68 / 5.60). The base session is still being taken; the full comparison, the counters (`bound-sites-served`) and the S2b findings come in the C2 report. Premise note already: the audit's 13.5% was measured before M123's memo landed; after it the audit on a served keystroke is nearer 0.4 G, of which S2a serves the prefix's share — the −0.3 G on the leaf rows is that.

### Next from here
C2: finish the base session, state S2b (R11 and the shared-cells/capture-plan tables are HELD with reasons — their rows are not functions of the prefix as the paper assumed; written up in the pass map's §7.1, uncommitted), run the full suite + `ci-local.sh perf` on the S2a tree, hand back. Tell me when 5411f6da (or the branch) is on next and I will `git fetch origin && git merge origin/next` at the next boundary.
