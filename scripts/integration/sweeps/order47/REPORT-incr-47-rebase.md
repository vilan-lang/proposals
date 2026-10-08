## incr-47: rebased onto debug-47 `6e3413e1`

**New tip is `b92847b0`** (b92847b0c…). It is three commits on base `6e3413e1` (debug-47's rebased tip, which sits on origin/next `db2df5f1`), done with `git rebase 6e3413e1`. No stash, no config change, no push.

| commit | was | now |
|---|---|---|
| S0 | 306940ee | `d3a71caf` |
| Q3 differential | b7cc8fc1 | `37440a5a` |
| S1 | 974d5dc4 | `b92847b0` |

The kolt row that moved most: a world-mode keystroke in `views.vl` costs **8.80 G on the tip against 12.34 G on the base (−29%)**. The full table is below.

### Conflicts and how each was resolved
Only the S0 commit conflicted; Q3 and S1 applied clean.
- **`CHANGELOG.md`.** next already has an `## Unreleased` section full of the other lanes' entries. I kept all of it, put my three `family: tooling` entries at the end of that section separated by `---` as the other lanes do, and dropped my duplicate heading.
- **`scripts/lsp-latency.py`.** N145 re-anchored the `shared.vl keystroke` scenario next to my `leaf keystroke, world mode` row. Kept both: my scenario first, then N145's comment and the new anchors.
- **No code conflicts.** The seams in your list (solver-47's `resolve_world`/`resolve_import`, perf-47's `analyze_over_world` and Program literal, debug-47's track_caller pass in `post_analysis_passes` and its `resolve_call_subject` changes, store-47's field-syntax files) all merged without touching my lines. The S0 commit's tree builds on the new base.
- **B547 against my queued macro-name references.** They still work together: the differential's corpus leg includes `arena`'s `[derive(Wire)]`, and it passes.
- **One fold-in during the rebase: `[track_caller]` is now part of a function's interface fingerprint** (and an external's), because a caller's emitted call changes when it flips. This was squashed into the S0 commit with `--autosquash`.
- **The two new errors (B535, B536).** No program in `edit_replay_differential.rs` or in my LSP test call sites calls a trait method without importing the trait, or writes attributes out of canonical order. Nothing needed changing.

### The differential on the rebased tip
- **Run:** `cargo nextest run -p vilan-core --test edit_replay_differential -j 6`, exit 0, 7 of 7 passed.
- **Both legs green:** every edit class, and the corpus re-hosted as modules.
- **The re-walk counter pins hold:** a leaf re-walks 2 sources, a cycle member 3, a shared module 3, the entry 1; planting the whole package as hot still moves every count.
- **Each planted bug still turns it red:**
  - `HotSetReplay` (a hot module served stale from its record);
  - `PrefixUnvalidated` (the stored prefix served without its content check);
  - `ImplGuardOff` (the impl guard dropped);
  - `UseInferredGuardOff` (the guard on prefix bindings whose first use decides their type dropped).

### The kolt table on the new base
Release builds of both sides, the same prepared kolt copy, medians of 5, instructions:u. Load average was 1.3 to 9 during the runs, so compare instructions rather than CPU.

| row | base 6e3413e1: G / CPU to diagnostics | tip b92847b0: G / CPU to diagnostics |
|---|---|---|
| `views.vl` keystroke, world mode | 12.34 G / 1970 ms | **8.80 G / 1030 ms (−29%)** |
| `model.vl` + importers open | 12.72 G / 1840 ms | 12.76 G / 1740 ms (unchanged: refused) |
| `model.vl` + importers open, every open file settled | 1850 ms | 1740 ms |
| lone leaf `views.vl` | 8.05 G / 880 ms | 8.05 G / 900 ms |
| leaf keystroke + 3 s pause | 18.49 G | 18.50 G |
| lone `model.vl` | 1.84 G / 290 ms | 1.84 G / 280 ms |
| css keystroke (lone) | 9.31 G | 9.30 G |
| parse break / repair | 9.31 / 9.44 G | 9.31 / 9.42 G |
| Find References (lone `model.vl`), first / warm | 8.30 G / 0 | 8.30 G / 0 |
| peak VmHWM | 1221 MB | 854 MB |

- **perf-47's ~38% cut does not show in these rows.** It was a cut to a cold `vilan check`, and the keystroke rows barely moved: the world-mode `views.vl` base is 12.34 G here, against 12.58 G on the old base.
- **The peak-memory pair is noisy rather than a finding.** The previous pair was 931 MB against 980 MB.
- **The re-run session** (ten keystrokes per file, world mode):
  - `views.vl`: a hot-set world on every keystroke, 9 cache hits, 2 sources walked; 8.94–8.95 G per clean keystroke and 5.5 G per broken one.
  - **`theme.vl` (11/27), `model.vl` (12/27) and `styles.vl` (11/27) are still refused by the impl guard on every keystroke:** 33 `hot-refusal impl` lines, 86 sources walked, 12.45–12.64 G clean.
  - Late writes are 0 on all 243 counter lines.

### Gates on b92847b0
- **Full suite** (`cargo nextest run --workspace -j 6`): exit 0, 9731 of 9731 passed, 35 skipped.
- **Native differential** with `VILAN_NATIVE_DIFFERENTIAL=1`: 177 of 177.
- **Clippy** with `-D warnings`: exit 0. **`cargo fmt --check`:** exit 0.
- **`ci-local.sh`:** vilan-fmt ok, windows ok, perf ok. The CLI's counts on the new base include todo at 5.32 G and genapp:46 at 9.67 G.
- **Late writes are zero:** the inference suite asserts it and passed, and the session above reads 0.
- **Not verified here:** CI's Windows runtime (only the cross-clippy ran).

The owner's rulings are noted (S4 ahead of S2 in Order 48; the hot-set world's id order is fine since it is never emitted; the macro-reference change rides S1). S2–S4 were not built.
