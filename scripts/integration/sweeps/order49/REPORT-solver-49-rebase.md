## solver-49: rebase report (onto lang-a-49's next)

The branch is rebased onto lang-a-49's next and every gate you asked for is green.

**Tip:** `solver-49` @ **e8ef8a5a**, 20 commits on origin/next @ **82e5114e**, not pushed. The commit list and order are unchanged from my main report. `LANE-STATUS.md` (untracked) is current, and the temporary base worktree is reaped.

### Conflicts
- **CHANGELOG and ledger TSV:** both kept. The NEW ledger rows stay at the tail.
- **A164 commit, `type_mismatch_message`:** my `null`-value wording for `expected`/`got` stays first. lang-a's B569 label-contradiction block now sits after it, so it uses those same strings.
- **E285 commit, `with_fragment_steer`:** merged in this order:
  - my factored `is_fragment_at_a_view` check;
  - then lang-a's B569 §3.2 one-slot labelled-literal steer;
  - then its `with_label_contradiction_fixes` tail.

  `place_type_id` and `with_label_contradiction_fixes` are kept intact.
- **`Type::Tuple(elems, TupleLabels)`:** the 3-way merge carried it into my code (for example `type_value_has_hole`). No hand edits were needed, and the tree compiles with no further fixes.

### Gates on e8ef8a5a
- `cargo fmt --check` clean; `cargo clippy --workspace --all-targets -D warnings` clean.
- `cargo nextest run --workspace -j 6`: **10077 / 10077 passed**, 31 skipped.
- `native_differential` with `VILAN_NATIVE_DIFFERENTIAL=1`: **232 / 232**. The corpus census is **130 enumerated / 127 identical / 3 refused by name / 0 broken**; capture-clones.vl stays identical.
- `scripts/ci-local.sh perf`: green, T2 verdict green, growth x1.938. Late writes are 0 on every line.

### Perf rows: tip vs a release build of 82e5114e
Release builds, instructions:u, in millions. Every row is cheaper, mostly from M132.

| subject | 82e5114e | tip | ratio |
|---|--:|--:|--:|
| math | 258.7 | 254.3 | x0.983 |
| watch | 327.1 | 320.5 | x0.980 |
| browser | 1,454.1 | 1,435.8 | x0.987 |
| fullstack | 3,071.8 | 3,005.1 | x0.978 |
| router | 1,713.5 | 1,660.3 | x0.969 |
| reactive-ui | 1,864.2 | 1,805.7 | x0.969 |
| ssr | 3,851.8 | 3,710.2 | x0.963 |
| canvas | 1,464.3 | 1,444.7 | x0.987 |
| rpc | 2,015.9 | 1,892.0 | x0.939 |
| todo | 5,029.2 | 4,725.4 | x0.940 |
| walkthrough | 5,111.6 | 4,831.8 | x0.945 |
| genapp:46 | 8,807.6 | 8,759.7 | x0.995 |
| plain:160 | 3,080.3 | 2,924.5 | x0.949 |
| plain:320 | 6,222.0 | 5,666.4 | x0.911 |

No ci bump is needed; the ceilings can be ratcheted down at the seal. B596 stays with Order 50 as agreed.
