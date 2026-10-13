## incr-51c: C3 after the rebase onto solver-51

P1 is rebased onto `origin/next` and every gate is green again. The new tip is **`0a5fd8f7`** (std-prefix P1, family `performance`), on base **`a0b697a0`** (the solver-51 merge). It replaces `6938bbca`. Nothing is pushed and none of my processes are running.

### The rebase
- **Only CHANGELOG.md conflicted.** I kept both sides: solver-51's ten entries stay, and my P1 entry sits above them with its `<!-- family: performance -->` marker. The marker parity check reads 41 heads and 41 markers (next had 40/40).
- **analyzer.rs merged on its own.** solver-51's M133 memo and the rest of its work are intact, and my prefix block in `analyze_inner` is unchanged. My diff never touched `resolve_world`.
- **Functions changed:** the same list as in the C3 report. Nothing new.

### Gates on `0a5fd8f7`
- **Full suite** (`--cargo-profile ci-test -E 'not binary(deep_nesting)' -j 6`): 10,518/10,518 passed, 32 skipped. Within it:
  - ci_ignored_pins 12, hygiene 3, corpus 14
  - check_scope_differential 16, permutation_differential 7, edit_replay_differential 23
  - native_differential 270, id_windows 10, vilan-lsp 1,103
- **Native differential, sweep mode:** 270/270.
- **Deep-nesting canary at 1536 KiB:** 18/18.
- **Lint and format:** clippy `-D warnings`, `cargo fmt --check` and `vilan fmt --check .` are clean.
- **The three differentials plus corpus with `VILAN_STD_PREFIX=on`:** 49/60, the same split as before the rebase.
  - Corpus is green, and no divergence assertion fired anywhere.
  - All five new prefix pins pass.
  - The 11 failures are the pins written for the existing S1/S7 hot-set and record shapes, which I listed in the C3 report: hot-set/record census counts, S1/S7-only plants, and two package-table pins that a std-only prefix cannot meet.
- **`ci-local.sh perf`:** T2 green. Tip vs next on the same box ranges from −0.052% to +0.055% (worst `example:walkthrough` +0.055%, `plain:320` −0.052%). No bump row.
- **Late writes:** 0 on kolt.
- **RSS on kolt** (9-run medians): next 275,612 and 275,788 KB; tip 275,624 and 277,740 KB. That is +0.0% and +0.7%, within the 3% gate.

### E292's six rows
Today's kolt, release, `--runs 5`, errors 0 on every row. The box was quiet this time (load average 0.7–1.0). CPU ms / instructions G, next → tip:

| Row | next | tip |
|---|---|---|
| leaf | 590 / 4.30 | 600 / 4.30 |
| leaf + pause | 1470 / 10.46 | 1500 / 10.46 |
| world | 630 / 4.64 | 610 / 4.64 |
| shared | 240 / 1.66 | 230 / 1.66 |
| model importers open | 720 / 5.45 | 700 / 5.45 |
| css | 780 / 6.53 | 790 / 6.53 |

- Instructions are identical, as expected with the prefix off by default.
- The harness refuses "model.vl keystroke" and "parse break" because their anchors are gone from today's kolt.
- E292 stays open: leaf and the pause row are close to the 500 ms CPU target but not under it, and css is 790 ms.

The finds, the owner questions and the uncommitted paper note in `std-prefix.md` are unchanged from the C3 report.
