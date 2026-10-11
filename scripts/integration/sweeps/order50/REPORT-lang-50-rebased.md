## lang-50: rebased onto C3 (ff35bf64), every gate green

The branch is rebased onto `origin/next` @ff35bf64 and the full gates pass. Nothing is pushed.

**Tip:** `8f37597e`, branch `lang-50`, worktree `/home/reed/code/vilan-lang/vilan/.claude/worktrees/lang-50`. The rebase applied all 8 commits with no conflicts, CHANGELOG included.

**`check_written_nominal_bounds`:** git merged it cleanly. M134's `set_check_anchor_type(type_id)` is set first in the loop, and my kind check (`generic_argument_kind_error`) sits inside the argument loop as before. My new `check_call_generic_argument_kinds` only reads, so it sets no anchor.

**CHANGELOG parity:** next has 36 Unreleased entries and the tip has 43. None are missing and every entry still has its family marker.

### Commits (oldest first)
| sha | slice | family |
|---|---|---|
| fe289fae | S1 R2 (`Type::Array(TypeId, TypeId)` + `Type::Length`) | feature |
| e7116057 | S2 impl heads `[type T; _]` / `[type T; const N]` (A163) | feature |
| 88d5f7fe | S3 `<const N>`, numeric generic arguments | feature |
| 9dd095e1 | fix: directed array literal at an open element (B609 territory; a bug already on v0.47.0) | fix |
| b06bab6b | S5 std array impls (A161, A166, Hashable, Debug, to_list, iter; no Eq) | feature |
| 474b84d9 | S6 book and spec (D15) | feature |
| 47bec1c5 | S4 named lengths + E287 halves (a) and (b) | feature |
| 8f37597e | ci `[[bump]]` rows for S5's std growth | covered in S5's entry |

### Gates on 8f37597e
- **Full suite** (`--cargo-profile ci-test -E 'not binary(deep_nesting)' -j 6`): 10,269 run, 10,269 passed, 31 skipped. Per binary:

| binary | passed / failed |
|---|---|
| corpus | 13 / 0 |
| native_differential (default mode) | 258 / 0 |
| edit_replay_differential | 19 / 0 |
| replay_differential | 2 / 0 |
| permutation_differential | 6 / 0 |
| infer_differential | 148 / 0 |
| check_scope_differential | 15 / 0 |
| id_windows | 8 / 0 |
| vilan-lsp | 1,101 / 0 |
| ci_ignored_pins | 12 / 0 |
| hygiene | 3 / 0 |
| inference | 5,463 / 0 |
| docs | 12 / 0 |

- **Native differential in sweep mode** (`VILAN_NATIVE_DIFFERENTIAL=1`): 258 run, 258 passed.
- **`cargo clippy --workspace --all-targets -- -D warnings`**, **`cargo fmt --all --check`** and **`cargo run -p vilan-cli -- fmt --check .`** are all clean.
- **`scripts/ci-local.sh perf`:** green, T2 verdict green. Instructions (instructions:u) against a release build of ff35bf64, each binary measured from its own tree's std:

| subject | change |
|---|---|
| example:math | +0.92% |
| example:watch | +0.82% |
| example:browser | +0.42% |
| example:reactive-ui | +0.42% |
| canvas, router, ssr, todo, fullstack, rpc, walkthrough | +0.25 to +0.36% |
| plain:160 | +0.24% |
| plain:320 | +0.15% |
| genapp:46 | +0.16% |

  Every row exits 0 on both binaries, and late writes are 0 on kolt. The bump rows are math 1.01, watch 1.009 (raised from 1.008 after this re-measure), and browser, reactive-ui and ssr at 1.005 each. All are estimated from instructions:u and should be re-taken at the seal.
- **kolt cold-check RSS** (`scripts/rss-probe.py`, a copy outside any checkout with lucide and search-dict, both binaries check it clean). Two rounds of 5 runs each:

| | round 1 median | round 2 median |
|---|---|---|
| base (ff35bf64) | 263,868 KB | 264,048 KB |
| tip | 270,048 KB | 270,468 KB |

  That is +2.3%, within the 3% gate, and the ~6 MB rise is consistent across runs. The new std impls load in every program, so this is most likely their cost. Since it sits near the limit, it should be watched at the seal.

### Analyzer, mono and emitter functions changed
Unchanged from my previous report; nothing new came in with this rebase.

### Questions for the owner
The five questions and my recommendations stand as filed with you.

All of my processes are stopped. `LANE-STATUS.md` is updated (untracked).
