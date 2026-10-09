## native-48 is rebased onto origin/next @dfe0c5fc and every gate is green

New tip is **967fea09** on branch `native-48`, 19 commits on top of dfe0c5fc (debug-48's merge). Not pushed. A final `git fetch` shows origin/next still at dfe0c5fc. All numbers below are from this tip.

### Conflicts
- **`CHANGELOG.md` was the only file that conflicted.** It conflicted at five of my commits: F49+F103, F102, F108, F99 and F97. Both sides were adding entries at the top of `## Unreleased`.
  - I kept both sides each time: debug-48's entries first, then mine, with a `---` separator.
  - Checked after: no conflict markers anywhere, one `## Unreleased`, 25 entries with 25 family markers (debug-48's 6 plus my 19), one marker per `---`-separated block.
- **`vilan-rust/src/lib.rs` merged without a conflict.** That includes debug-48's `ObjectTrait.show` field and its `ensure_object_trait` / `ensure_object_impl` `dbg_show` emission, beside my edits to `ensure_struct`, `ensure_enum`, `closure` and `call_expression`.
  - `vilan-rt/src/lib.rs`, `native_differential.rs` and `memory.md` also merged cleanly.
  - I did not edit `dbg.rs`, `show.rs` or the `dbg_*` fixtures.
  - The tree builds, is fmt-clean and clippy-clean; the suites below are on this merged code.

### Commits after the rebase
| commit | new sha |
|---|---|
| F49+F103 | f25f67d5 |
| F102 | 088a7b5d |
| F107 | e6e63cfe |
| F104 | 7da1522a |
| F105 | 53508d20 |
| F106 | 45be71ab |
| F92 | 0797aca6 |
| F108 (native half) | 88ac03d7 |
| F99 (half) | 461a4d44 |
| exit-code `main` | ff765293 |
| F97 | ecd4413f |
| F95 | 36247783 |
| F100 | d499eb2a |
| F98 | f56e1574 |
| F93 | d1486cd2 |
| F94 | be6d307d |
| F101 | 45651869 |
| F96 | a89c2026 |
| pin re-points | 967fea09 |

### Whole-set triple
| set | base e75bc57c | tip 967fea09 |
|---|---|---|
| platform-free | 130 / 103 / 27 / 0 | **130 / 126 / 4 / 0** |
| async | 7 / 4 / 3 / 0 | 7 / 4 / 3 / 0 |
| platform-bound | 9 / 6 / 3 / 0 | 9 / 6 / 3 / 0 |

Columns are enumerated / identical / refused / broken. The tip numbers match what I measured before the rebase.
- **Still refused (platform-free):**
  - async-await and signal-update, both by design.
  - transparent-references: the aliasing-views half of F99, not done.
  - capture-clones: blocked by an analyzer gap I filed as F?3 (`-`, `*`, `/` and `%` accept mixed integer widths, while `+`, `<` and `==` refuse them).

### Censuses
Neither census moved, so I regenerated nothing. `the_native_copy_census_matches_its_table` and `the_native_leak_census_matches_its_table` both pass against the committed tables.

### Gates on 967fea09
| gate | result |
|---|---|
| `cargo nextest run --workspace -j 6` | 9810 run, 9810 passed, 34 skipped (load was 40–55, 4888 s) |
| `native_differential` with `VILAN_NATIVE_DIFFERENTIAL=1` | 202/202, including both census tables and the three whole-set tests |
| `check_scope_differential` | 15/15 (in the full suite) |
| `cargo clippy --workspace --all-targets -- -D warnings` | clean |
| `cargo fmt --all --check` | clean |
| `ci-local.sh vilan-fmt` | green |
| `ci-local.sh windows` | green |
| `ci-local.sh perf` | T2 verdict green, growth x1.939 |

No analyzer function was touched, so there is no late-write count to report.

Everything else in my earlier report still stands: the per-item causes, the pins, the 8 finds in `sweeps/order48/newitems48-native.json`, and the rulings asked for.
