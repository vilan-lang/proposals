## suite-48 report

**Tip `7eacd6c3` on `origin/next` @`b63e0e5b`** (the editor-48 merge). Branch `suite-48` in `vilan/.claude/worktrees/suite-48`. Nothing is pushed.
- I rebased four times. The bases went dfe0c5fc → ecf3aef5 (native-48) → 4b4a63c6 (std-48) → 8ab08bb2 (incr-48, which brought S4) → b63e0e5b (editor-48).
- The only conflicts were CHANGELOG prepends. I kept both sides each time. After each merge I re-checked the CHANGELOG with the cut's own awk under three awks: 0 problems.
- After my last gate run, `next` gained incr-48b (`1177489a`). It touches CHANGELOG.md, `analyzer.rs`, `incremental.rs` and `edit_replay_differential.rs`. `git merge-tree` with my tip is clean. I am waiting for your rebase order.
- Logs are under `target/suite-48-scratch/`. `LANE-STATUS.md` is current and untracked.

### Per item

**N142 — done, `c473c66f`.**
- docs-47's patch applied cleanly. All seven `analyzer.rs` comments now use the `[..] export` spelling, and none of the old spelling is left in the file.
- One more pre-B485 spelling is left in `parsing.rs:531`; filed as N?5.

**N150 — done, `db131ef9`.**
- The premise was right. The edit inserts a space inside `\t\t`, and the completion anchor `\t\tself.uuid.hash()` is looked up in the edited buffer, so every run died.
- The anchor is now `("self.uuid.hash()", len("self."))`, editor-47's scratch fix.
- `anchor_problems` now applies each scenario's edit and refuses a hover or completion anchor that the edit destroys.
- Every committed scenario's anchors land on kolt's working tree.
- Pin: `perf_gate_script::the_lsp_harness_checks_the_keystroke_anchors_against_the_edited_text`. It is red against the old script; I checked that by hand.

**N148 — done, `e7b65f0c`.**
- `measure_all` now measures exactly the subjects `--subject` names.
- The new `subject_problem` refuses an unparseable subject by name (`plain:many`, `exmaple:canvas`, a missing example) before anything is measured.
- The same commit makes the test helper stop leaving an untracked `scripts/__pycache__` in the checkout. The existing tests had that leak too.

**N152 — done, `078ffe25`.**
- **The construct:** mawk 1.3.4 20200120 has no regex intervals. It reads `/^-{3,}[ \t]*$/` as literal text, so a `---` rule stayed inside the entry above it and the rewrite printed it again beside its own separator.
- **Fix:** the pattern is now `/^---+[ \t]*$/`. Nothing else in the scripts used an interval outside `grep -E`.
- **Red first:** the old script under mawk 20200120 reproduces the runner's exact three reds. On the real CHANGELOG, the new rewrite is byte-identical under mawk 20200120, mawk 20250131 and gawk 5.1.0.
- **Floors:** the script's header now states what it needs. Python ≥ 3.11 is checked with the other reds before anything changes. Before, the apply step silently skipped the perf report and ratchet when `python3` was missing, and died after the version bump when it was too old.
- **Pins:** `the_cuts_awk_programs_use_no_regex_interval` and `an_applying_cut_refuses_a_python_older_than_3_11_before_changing_anything`.

**N147 — done, `1544217b`. The item's premise was half wrong.**
- The refusal was always emitted, and the analysis's normalized list already put it first.
- **Real cause:** the CLI renders errors that carry a note or trace as it meets them, but held plain errors until after the loop. So every noted error printed above every plain one: std's `PartialOrd` conformance errors (noted into `compare.vl`) above the refusal, and in general a line-11 noted error above a line-8 plain one.
- **Fix:** the new `report_plain` renders each plain error in place. Codegen refusals and parse errors keep the closing `report`. Warnings now print after the errors; before, they printed ahead of the plain errors.
- **Pins:** `diagnostics::n147_a_noted_error_prints_in_its_place_not_ahead_of_every_plain_one` and `n147_a_split_toolchain_refusal_leads_the_terminal_rendering` (both red against the old binary, checked by hand), plus `relocated_std::n147_*` for the analysis-order half, which was already green.

**N151 — done, `7eacd6c3`. Measured first.**
- **Method:** a nextest target runner recorded each test process's CPU (user+sys, children included) over a full run.
- **Base dfe0c5fc:** 9,797 tests, 13,002 CPU-s, 3,712 s wall at load 33–49.
- **Where the CPU goes:**

| binary | CPU-s | share |
|---|---:|---:|
| `inference` (5,212 tests at 0.91 s each) | 4,737 | 36% |
| `edit_replay_differential` (its corpus leg alone: 923) | 1,180 | 9.1% |
| `vilan_lsp` | 1,110 | 8.5% |
| `native_differential` | 1,049 | 8.1% |
| `replay_differential` | 515 | 4.0% |

- **The std share:** in a 41-test inference sample there were 1.12 analyses per test. load+walk 343 ms + base 174 ms = 53.5% of a test's CPU is the std world it builds before its own program; std's part of the checks and post-passes comes on top.
- **Door (a)'s premise does not hold.** nextest runs every test in its own process, so a std world built in-process dies with its test. That is the same limit E30 recorded in suite-speed.md.
  - Where one process does run many analyses, the base cache already shares them: the docs gate serves 166 of its 279 analyses (`VILAN_COUNTERS`).
  - The differentials' clean legs are cold by design.
  - So I built no shared prefix. "The differential green with the shared prefix on" has nothing to switch on. The edit-replay differential is green in every run.
- **Door (b):** a priority-90 tier in `.config/nextest.toml` for the next long tests:
  - the edit-replay binary
  - the docs gate
  - check_scope's two corpus legs
  - `examples`
  - the corpus golden
  - native_differential's four longest legs

  They used to start at +850 to +1843 s; now they start within the first 7 minutes.
- **Door (c):**
  - `style_chain_order`'s two tests build their fixtures concurrently: 152/102 s → 23/32 s wall alone, CPU flat.
  - `examples::every_example_builds` builds concurrently: 76 → 22 s.
  - I also tried running the edit-replay step's two clean legs side by side. It measured no win under load, so I dropped it.
- **Before/after:** CPU is flat, as expected (13,002 → 13,475 CPU-s, with 71 more tests on newer bases). Suite wall went 3,712 s → 2,983–3,188 s, but load and base differ between runs, so I am not claiming that number.
- **The load < 2 gate was never available.** The box sat at load 18–52 for the whole order, so no wall figure here meets the gate's condition.
- **What actually moves the suite's CPU** is building `vilan-core` at opt-level 1 in the test profile:
  - an inference test drops from 967 to 307 ms (3.15×);
  - but each `analyzer.rs` edit's rebuild goes from 17–20 s wall (16 CPU-s) to 78–87 s (~200 CPU-s).
  - Filed as N?1 for a ruling.

**M125 — re-run only, no change made. S4 IS on next now.**
- Before S4 reached next (tip on 4b4a63c6), calibrate was red, twice: const-pass 2.9–3.2% (genapp) against 14.4–14.5% (kolt).
- With S4 (8ab08bb2) and on the final tip (b63e0e5b) it is green, four runs: 2.2–2.4% against 8.2–8.9%. const-pass is still the phase closest to the 10-point threshold, at about 6.5 points.
- Kolt is a `cp -r` copy, and it checks clean under the tip.
- The item's generator change would move genapp:46's ceilings. Rec: leave it until a seal shows drift again.

### Needs a ruling
1. **N?1:** the test-profile opt-level trade above.
2. **N?4:** whether internally parallel tests should declare nextest `threads-required` (only measurable at a seal).

### Finds
In `sweeps/order48/newitems48-suite.json`; repros in `sweeps/order48/suite-48/finds/`.
- **N?1:** opt-level 1 for `vilan-core` in the test profile, with the measurement script `finds/test-profile-opt-level.sh`.
- **N?2:** door (a) needs a cross-process std world (M36) or a fork-server harness. A shared prefix across different std imports also needs a seed-independent world. Notes in `finds/std-prefix-per-test-process.md`.
- **N?3:** native_differential's four long legs are serial loops. They belong to the native lane, so I left them and priority-start them instead.
- **N?4:** the 8- and 16-way test pools ignore `-j 6`.
- **N?5:** the `parsing.rs:531` comment.

### Gates
Final base b63e0e5b, tip 7eacd6c3. The same set was green on ecf3aef5, 4b4a63c6 and 8ab08bb2.

| gate | result |
|---|---|
| `cargo nextest run --workspace -j 6` | 9868/9868 passed, 35 skipped; 3,188 s wall at load 20–30 |
| `native_differential`, `VILAN_NATIVE_DIFFERENTIAL=1` | 202/202 |
| `edit_replay_differential`, `check_scope_differential` | green, inside the suite |
| `cargo clippy --workspace --all-targets -- -D warnings` | 0 |
| `cargo fmt --all --check` | 0 |
| `ci-local.sh vilan-fmt`, `windows` | ok |
| `ci-local.sh perf` | T2 green, growth x1.938 |
| `release_scripts` + `perf_gate_script` | 49/49 under mawk 1.3.4 20200120 and under gawk 5.1.0 (both extracted from Ubuntu debs into scratch), and in the full suite under the system's mawk 20250131 |

### Functions touched outside the harness
- **`crates/vilan-cli/src/main.rs`:** `compile_to_js` (plain errors rendered in place; new local `rendered_errors`), `report` (now calls the new `report_plain`), and `report_plain` itself.
- **`crates/vilan-core/src/analyzer.rs`:** comments only (N142). No analyzer, mono or emitter code changed.
- **Scripts:** `cut-release.sh`, `lsp-latency.py` (`anchor_problems`, the scenario), `perf_gate.py` (new `subject_problem` and `selected_subjects`; `measure_all` changed).

Nothing was refused by a permission layer. No load generator was left running, and I killed only my own nextest run, by PID.
