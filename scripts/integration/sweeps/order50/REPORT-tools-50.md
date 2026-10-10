## tools-50 report

**Tip `2f3a600b` on branch `tools-50`, base `5fe24f86`** (not rebased, not pushed). Six commits, all trailered `Claude Sonnet 5.5`:
- `84b7d5eb` N164
- `150063b9` N165
- `4d692760` B594
- `cccc52fa` N162
- `17456942` N163
- `2f3a600b` fmt (the new pins)

Five CHANGELOG entries under a new `## Unreleased`, parity 5/5 (N162 and N163 are `tooling`, B594 is `fix`). `LANE-STATUS.md` is untracked. `proposals/scripts/integration/seal.sh` is edited in place, for the integrator to commit.

**Gates**
- **Full suite:** `cargo nextest run --workspace --cargo-profile ci-test -E 'not binary(deep_nesting)' -j 6` gave **10158/10158 passed, 31 skipped**. That is 890 s at load 9-15, run on the final tip.
- **Per-item gates:** `perf_gate_script` (20 pins), `release_scripts`, `ci_local_script`, `ci_ignored_pins`, `hygiene`, `module_paths`, `module_resolution`, `docs`, and the whole vilan-lsp binary (1176/1176) are green.
- **Lint:** fmt and clippy `-D warnings` on vilan-lsp and vilan-cli are clean.
- **Not run:** `deep_nesting` and the ci-local wasm leg, as in the brief.

### N164 — DONE
- **Mechanism, not the premise.** Load cannot reproduce the red on Linux. Forty busy loops (load 35 on 16 cores) gave `started=8` every time, and SIGSTOP stalls did not fold the burst either.
- **What fails.** The pin had only a 20 ms margin: the server's debounce task for keystroke k wakes at t+150 ms and keystroke k+1 supersedes it at t+170 ms. A host with more than 20 ms of timer-wake jitter makes every debounce task see a newer generation and return, so ONE analysis starts.
- **Reproduction.** I took the old sleep to `DEBOUNCE_MS - 40` and got the exact CI message, "1 started".
- **Fix (door (a)).** Each keystroke waits (1 ms poll, liveness-bounded) until the server's `started` counter passes where it stood when the keystroke was sent. A fixed 20 ms in-flight span follows, counted from that start, and then the next keystroke goes. The non-vacuity premise is now `started >= KEYSTROKES` (8). The `started - cancelled <= 2` and `landed <= 2` assertions are untouched.
- **Proof under load.** Eight runs of the new binary at load 23-30 (sibling lanes' cargo builds and native runs) all gave `started=8 landed=1 cancelled=7`. The load was other lanes' work, not a generator of mine. The full suite also ran under load 9-15.
- **Same-shape sleep, left alone.** The second burst measurement in the file (the CPU-ratio pin) has the same sleep, but folding can only make it cheaper per keystroke, so it cannot go red from folding. Details are in the finds README.

### N165 — DONE
- **Harness check.**
  - `scripts/lsp-latency.py` gains `--vilan` (default: the `vilan` beside `--lsp`; it refuses if none is found) and `unclean_copy`. It runs `vilan check .` in the copy under the same `VILAN_STD`, before anchors and before the first edit. On a non-zero exit it prints the compiler's errors and "Nothing was run."
  - `perf_gate.py seal`'s `refuse_unchecked_sources` now runs for every seal, base and tip. It used to run only with `--tip-kolt`.
  - Behaviour change to flag: a same-source seal used to note a compiler disagreement and measure anyway; it now refuses.
- **Real-kolt check.** On a `cp` copy of kolt the harness checks clean, and `leaf keystroke` reads 4.33 G, matching the true row. The same copy with `src/lucide` removed is refused with the 56-style `cannot find 'lucide'` errors.
- **Pins (all in `perf_gate_script.rs`), red against the old scripts:**
  - `the_lsp_harness_refuses_a_copy_that_does_not_check_clean_under_the_compiler_it_drives` (includes the no-compiler-found refusal).
  - `the_lsp_harness_carries_lucide_and_an_archive_that_lacks_it_goes_red`.
  - `a_seal_on_one_shared_source_refuses_when_either_compiler_rejects_it`.
  - `the_seals_kolt_row_reports_the_median_of_fresh_runs_peak_rss`.
  - `the_rss_probe_reads_each_fresh_runs_own_peak_not_the_max_over_children`.
- **Rss-probe red-first caveat.** That last pin was red only because the script was absent. I did not re-prove it against the old probe's `RUSAGE_CHILDREN` bug.
- **`scripts/rss-probe.py`** is new, over `perf_count.peak_rss` (Popen plus `wait4`'s per-child rusage). It prints each run's KB and the median, and exits 1 if any run fails.
- **T3 RSS.** The kolt row now takes the median of the fresh-process runs, not the max, and lists each run (`peak_rss_runs_kb` is in the verdict). It falls back to a fresh `peak_rss` run when the counter is callgrind. `perf_count.measure` was already per-child via `wait4`, so the old reading was valid; the change from max to median is the one real gate change.
- **Floor.** `ru_maxrss` carries a roughly 10 MB floor from the forking Python. It is invisible at kolt's 260 MB but would matter for tiny commands, and the probe's docstring says so.

**`seal.sh` edits.** The union/doctest/native/clippy/fmt/wasm/canary legs are untouched. This is what changed:
- **Env vars the integrator sets:**
  - `VILAN_PERF_KOLT_DIR` is the base's kolt, a clone COPY with the working tree committed inside it (default `~/code/kolt`).
  - `VILAN_PERF_KOLT_COMMIT` is the commit in that copy.
  - `VILAN_PERF_THRESHOLD` is passed through as `perf_gate.py seal --threshold`.
  - Existing and unchanged: `VILAN_PERF_TIP_KOLT`, `VILAN_PERF_BASE`, `VILAN_PERF_LSP_BASE`, `VILAN_PERF_ADVANCE=1`.
- **New: `VILAN_SEAL_PERF_ONLY=1`** runs the perf leg alone. That is how `sweeps/order49/perf-leg.sh` was used; the old file is left as the historical record.
- **Harness calls** now pass `--vilan` (base: `$VILAN_PERF_BASE`; tip: `$W/target/release/vilan`).
- **Hole closed.** A failed or refused harness leg used to leave the LSP rows out silently and let the T2/T3 verdict stand. It now sets the leg RED (`pf=1`) and prints the leg's log path.
- **Grep widened.** The grep now matches `T3 ` (so the RSS line shows), and the refusal lines from the harness logs are echoed.
- **Final verdict line** prints `skipped` for legs not run.
- **Syntax checked.** `bash -n` passes. The script lives in the proposals repo, so no tree pin covers it; the harness and gate behaviour it calls are pinned.
- **Integrator to-do.** briefs50's Mechanics still names `sweeps/order49/rss-probe.py`; it is now `scripts/rss-probe.py`.

### N163 — DONE
- **Measurement.** One full ci-test run took 762.7 s at `-j 6` and load 10-25, which is 4,572 test-seconds and throughput-bound, so ordering only moves the tail. Per-test wall came from JUnit. I also measured per-test CPU for 18 candidates, each run alone.
- **What moved from opt-level 0:**

| Test | Before | Now |
|---|---|---|
| edit_replay corpus | 293 s | 97 s (839 CPU-s, because it fans out 16 ways) |
| docs | 212 s | 29 s |
| check_scope corpus | 100 s | 23 s |
| native legs | 119-184 s | 22-32 s |
| replay_differential | 60-170 s | 24 s |

- **New ranking in `.config/nextest.toml`:**
  - **Tier 100:** `binary(edit_replay_differential)` (corpus 97 s, nine edit-class tests 34-42 s each), `binary(permutation_differential)` (three tests of 36-45 s; it was UNTIERED, and its corpus leg is 297 CPU-s), `dependent_edit_measurement` (35 s), and the ledger's `n99_` test (35 s on one thread). The raised `slow-timeout` is kept for this tier.
  - **Tier 90 (15-35 s):**
    - leak_measurement, `style_chain_order`, `replay_differential`
    - docs `every_doc_example_compiles`
    - check_scope `corpus_agrees_*`
    - seven native_differential tests (the default suite, s0_, the leak/copy census, a138_, a142_, mapped-tuple, platform-bound)
    - `binary(diagnostics_ledger)`
    - two WAITING tests: `transport_robustness`' retry budget and `service_layer`' socket test, each about 25 s of wall for about 1.5 CPU-s. These hold a slot idle, so they are free only if started early.
    - `marker_census` moved from 100 to 90, keeping its timeout.
  - **Dropped:** `examples` every_example_builds (6.5 s) and `corpus` golden (13.8 s) are no longer long.
- **Check on the filters.** `nextest list` counts the tier-100 filter at 25 tests and the tier-90 filter at 60, and the config parses.
- **Not proven.** I did not prove the new order shortens a run. The load differed between my two full runs, so the totals (762 s vs 890 s) are not comparable.
- **Serial group.** The `wall-clock-waits` group sums to 148 s, well under the makespan, so it needs no priority.

### N162 — DONE (closed with the doc note, as ruled)
- **Premise corrections:**
  - It is 12 of 71 files now, not 11 of 70: `rpc/mirror.vl` joined `store.vl` on the `[internal]` shape.
  - Five files fail on bodyless `external fun`s, five on layer `pkg::` imports, and two on the `[internal]` rule.
  - None of the three causes is `file_project`'s. The first and third are in the analyzer: `check_unlowered_externals` and the B568 internal-field rule, which is incr-50's core. The second is module loading's layer overlay. None is the small fix, and the core is off-limits this wave.
- **Where the note is.** `vilan/docs/appendix/cli.md`, under `vilan check [file]` ("std is not checked as an entry"). There is no pin, since pinning the artifact would pin what we want gone.

### B594 — DONE
- **Fix.** `file_project`'s `[library]` arm now hands the unit `package_dir: Some(<library dir>)`. `resolve_workspace` already reads `[library.dependencies]`, so the item's worry that the plumbing assumes a `[package]` manifest was wrong. The library's prelude comes along, as in the editor.
- **Pin.** `b594_a_library_file_resolves_the_librarys_dependencies` in `module_paths`. It was red against the old `main.rs`. It covers a top-level file, a nested file, the directory form, and a control where an undeclared dependency is still refused.
- **Side effect checked.** The std file-mode failure count is unchanged at 12 after the fix.
- **Doc.** One sentence added to `cli.md`.

### Finds
- **Filed:** `sweeps/order50/newitems50-tools.json` holds one item, `N166`.
  - The seal's T3 row judges peak RSS against the CPU threshold, while lanes are told to hold kolt's RSS to 3%.
  - Rec: add `--rss-threshold` (default 1.05) and a `VILAN_PERF_RSS_THRESHOLD` pass-through in `seal.sh`. XS.
- **Repros/READMEs:** `sweeps/order50/tools-50/finds/n_burst_pin_margin/` and `n_rss_threshold/`.
- **Notes only, no item:** the second burst pin has the same shape but cannot go red (above), and `rpc/mirror.vl` is the 12th std file (in N162).

### Questions for the owner (each with my rec)
1. **RSS gate.** Should the seal gate RSS on its own tighter threshold (N166)? Rec: yes, 1.05. RSS is deterministic with the median-of-fresh-runs reading, and a 10-20% CPU threshold would have passed Order 49's +13% cliff.
2. **Same-source seals.** Keep the new behaviour (refuse when either compiler rejects the shared source) instead of the old note-and-measure? Rec: keep. A breaking tip needs `--tip-kolt` anyway, and a rejected program's ratios are not a measurement.
3. **`perf-leg.sh`.** Delete `sweeps/order49/perf-leg.sh` now that `VILAN_SEAL_PERF_ONLY=1` replaces it? Rec: keep it as the Order 49 record and use the env var from now on.
4. **N162 (std as an entry).** Should std ever be checkable as an entry? Rec: no, keep the doc note. Fixing (a) and (c) needs the analyzer core to know it is checking std, and the sixth cause is layer overlay in module loading. Revisit only if the std-prefix paper's persisted-std work makes "analyze std as std" a natural mode.
