# Integration helpers

The orchestrator's tools for a work order's integration and close, kept here so they stop being
rebuilt every order (the session scratchpad is wiped between and sometimes during sessions).

| script | job |
|---|---|
| `merge_lane.sh <lane> [nextest-spec…]` | merge `origin/<lane>` into the integration worktree with `--no-commit`, union CHANGELOG hunks and restore family markers, renumber the lane's `NEW` ledger rows from HEAD's max + 1 (HEAD's rows never touched), map them into `diagnostics_ledger.rs`, commit, build, gate, fmt-check, push |
| `merge_fold.sh <lane> <allow-edit or -> [spec…]` | `merge_lane`, then fold conflicted TEST files by whole function name; stops on a non-test conflict, a test-module conflict, or a red gate (never pushes red) |
| `fold_tests_by_name.py` | the fold: HEAD's file + the lane's new top-level `fn`s; `--allow-edit` takes the lane's version of a named existing fn |
| `changelog_union.py`, `renumber_ledger.py`, `apply_row_mapping.py` | the three mechanical resolutions `merge_lane` runs |
| `seal.sh` | union, clippy, the Windows cross-check, audit, fmt, changelog parity on the tip |
| `file_items.py <spec.json> [--check]` | validate-all-then-mutate tracker filing (`\|` escapes a pipe in a title) |
| `close_batch.py <spec.json> [--check]` | validate-all-then-mutate closes: item file gone, INDEX row dropped, tombstone appended |

Rules the scripts embody: a merge helper never rewrites HEAD's rows; test files merge by whole
functions, test modules by whole modules from each original (by hand); every hand fold is followed
by `cargo fmt`; a red gate stops the chain. `VILAN_INTEGRATION` overrides the worktree path.
