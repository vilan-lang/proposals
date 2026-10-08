## debug-47 rebase report

**The branch is rebased onto `origin/next` db2df5f1 and every gate is green.** New tip: **`6e3413e1`** on branch `debug-47` (not pushed), 9 commits on the new base.

| commit | slice |
|---|---|
| afd2b978 | S0 |
| 12f734eb | S1 |
| 307ef698 | S1b |
| e9ac751f | S4 |
| eb5e5d06 | E259 |
| e17f41b0 | N136 |
| 0db29891 | pin re-reads |
| 59052e2c | lazy site locator |
| 6e3413e1 | **new:** goldens and censuses regenerated on the rebased tree |

### Conflicts and how each was resolved
Code merged without conflicts: `analyzer.rs`, `transformer.rs`, `parsing.rs`, `vilan-rust/src/lib.rs`, `list.vl`, `grammar.md`, `tuples.rs`. These are the files where solver-47, perf-47, native-47 and store-47 also moved things.

- **At S0 (afd2b978):**
  - `CHANGELOG.md`: kept both sides, next's entries first, then mine, with a `---` separator added.
  - `diagnostics-ledger.tsv`: kept both sides; next's rows 638–661 first, then my `NEW` rows.
  - `marker_census.golden.md`: took next's side, then regenerated it at that commit with the rebuilt binary (`VILAN_REGENERATE_MARKER_CENSUS=1`). It now has `[track_caller]` in solver's canonical order; the only other change is renumbering. `[track_caller]` keeps rank 6 in `attribute_rank`, between `must_use` and `rpc`, which solver's now-erroring order check reads. Grammar fragments were regenerated as well; nothing moved.
- **At E259 (eb5e5d06):** `CHANGELOG.md` again. I took next's side and inserted only that commit's own entry; my S1/S1b/S4 entries now sit after next's entries under `## Unreleased`, each with its family marker.
- **At N136 (e17f41b0):** `vilan/test/tuple-access.mjs` (perf-47's golden). Took next's side.
- **At the pin re-read commit (0db29891):** `native-copy-census.tsv` (native-47's new 4th column). Took next's side.

### Goldens and censuses
I reset every corpus golden and the split fixture to next's, rebuilt with this branch, and judged them with `regen_goldens.sh`:
- **123 corpus goldens moved.** 122 are runtime-identical. `f64-print-negative-zero` now prints `0` three times: the N136 fix, plus two integer cases I added to its source.
- **What moved is only the three expected kinds:**
  - S0's location arguments and the `__panic` helper;
  - E259's instance names, and the `$` temporaries renumbering because instances no longer use them;
  - N136's `String(..)` wrap on numeric prints.
- **Split fixture:** `app.js` and the three route chunks moved, by names and locations.
- **Censuses:** the copy census (now 4 columns) and the leak census each gain one row, `f64-print-negative-zero`.
- **Unchanged against next:** the `infer_preset` goldens and the markdown anchor golden.

### Gates on 6e3413e1
| gate | result |
|---|---|
| `cargo nextest run --workspace -j 6` | 9724 passed, 0 failed, 35 skipped |
| native_differential with `VILAN_NATIVE_DIFFERENTIAL=1` | 177/177 passed |
| deep_nesting at `VILAN_CANARY_STACK_KIB=1536` | 18/18 passed |
| clippy `-D warnings`, `cargo fmt --check` | green |
| ci-local vilan-fmt, wasm, windows | green |
| ci-local perf | T2 verdict green; growth x1.938 (limit x2.3) |

My fixtures and pins needed no edits for B535/B536: they already import the traits they call and order their attributes canonically.

### Instruction counts, re-taken against the new base
The base is a release build of db2df5f1 (made in a temporary worktree, since removed), run with its own std; the tip is a release build of 6e3413e1.

| subject | change |
|---|---|
| **kolt `vilan check`** (scratch copy) | **16,769,348,801 → 16,830,890,522 (+61.5M, +0.37%)**; exit 0, no errors or warnings |
| math | +1.97% |
| watch | +1.87% |
| browser | +0.58% |
| fullstack | +0.52% |
| router | +0.64% |
| reactive-ui | +0.82% |
| ssr | +0.55% |
| canvas | +0.68% |
| rpc | +0.84% |
| todo | +0.58% |
| walkthrough | +0.34% |
| genapp:46 | +0.31% |
| plain:160 / plain:320 | +0.35% / +0.34% |

Kolt measures 16.77G here, not the ~15.5G you quoted; the copy or the counter may differ from perf-47's run.

The share is unchanged from before the rebase. A program that never calls `dbg` pays no printer cost. The cost is the fixed S0/S4 part: the `track_caller` pass, location arguments, and the grown `debug.vl` that every program loads.

The rulings you listed (E275, E276, E277, N149, block-tail move) are not built in this rebase.
