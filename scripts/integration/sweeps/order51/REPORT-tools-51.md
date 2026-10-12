tools-51 report (Sonnet 5.5). Nothing pushed, all my processes stopped. L24 skipped (nobody said the Windows runner is registered).

BASE ca407da0, TIP cbcb1cb2d1a9fcf2962a209c2b61102be80c563d, branch tools-51 in /home/reed/code/vilan-lang/vilan/.claude/worktrees/tools-51. Status file: tools-51-STATUS.md (untracked).

COMMITS (each with its Unreleased entry and marker)
1. 4b050131 N166, tooling. `perf_gate.py seal --rss-threshold` (env `VILAN_PERF_RSS_THRESHOLD`, default 1.05) judges the T3 kolt row's peak RSS; CPU, instruction and LSP rows stay on `--threshold`. The seal prints `T3 thresholds: CPU and instructions 1.10, peak RSS 1.05`, the red names the RSS threshold, and the verdict and report carry `rss_threshold`. Planted red pinned: +7% is red, +4% green, env and flag loosen it. I added one doc line to `proposals/scripts/integration/seal.sh`; the integrator commits it.
2. 59732718 N168, fix, plus cbcb1cb2 N168 (docs), tooling.
3. 6a72354c G28, tooling.
4. 37ae2f6e N159, tooling.
5. 821fb7e2 M135, performance.
6. 55fd7799 B597 + E296, diagnostics.

WHERE THE PREMISES WERE WRONG, AND WHAT I DID
- N168: there is no debug-only `crates/vilan-cli/../../vilan/std` read. Both effects came from one thing, the ancestor walk for `vilan/std/vilan.toml` in vilan-cli's `std_dir` and vilan-lsp's `discover_std_dir`. I removed the walk entirely, so a binary reads `$VILAN_STD` or its own embedded std (materialized under `~/.vilan/std-cache`) and nothing else. This is slightly stronger than the brief for release builds: a dev build also reads the embedded std unless `VILAN_STD` is set. The embedded std is re-embedded on every std edit, so cargo and nextest see edits after their build step.
  - Pins: an installed binary beside a poisoned stand-in checkout compiles clean (and fails through `$VILAN_STD`); the same for the LSP. N56's bare-file pin (a bare file took the shell's checkout) is inverted. Full suite showed no other test depended on the walk.
  - Also changed: AGENTS.md has a new bullet, and `editors/vscode/README.md` no longer promises a checkout's working tree (`vilan.stdPath` or `VILAN_STD` is the door). Test comments and `harness_scratch.rs` exemption texts are updated.
  - Practical effect: editing std in an editor now needs `vilan.stdPath`.
- G28: new `crates/vilan-core/build.rs` hashes vilan-core's `src/**` plus `Cargo.toml` (SHA-256, 64 bits) and exposes `vilan_core::BUILD_ID`. The macro-expansion header gains a `build` line, and a table from another build is a miss. `vilan cache clean` is unchanged. The std prefix's later key can read the same constant; M135's table already does. `sha2` is now also a build-dependency (Cargo.lock unchanged). Pins in `tests/build_id.rs` and `macro_expansion_cache.rs`.
- N159:
  - Capped sites: `replay_differential`, edit-replay, permutation and check-scope corpus legs, docs gate, CLI corpus, `marker_census`, `examples`, `style_chain_order`, and `native_differential`'s leg workers.
  - Premise wrong: `interpreter` has no internal pool (its corpus is one test per program), so I left it. `corpus.rs`'s `WORKERS=4` and `eight_concurrent_runs…` are deliberate concurrency properties and stay.
  - Mechanism: `crates/vilan-core/tests/test_pool/mod.rs`, which vilan-cli includes via `#[path]`. `VILAN_TEST_POOL=n` wins, otherwise 2 under nextest (detected by the `NEXTEST` env), otherwise the width the test asked for. A scan pin (`tests/test_pool_rule.rs`) fails any new `.div_ceil(` chunked pool that skips the cap.
  - Measured:
    - Edit-replay corpus leg alone: peak threads 32 to 6; CPU 8m58 to 5m40; wall 3m27 to 4m38 (single runs on a loaded box).
    - Whole suite, uncapped vs capped: CPU 87.9 to 90.0 min (+2%, 12 new tests), i.e. total CPU unchanged; wall 737 s to 863 s on a loaded box (other lanes building).
- M135: stayed S, no analyzer-core change.
  - What I built: the disk layer is in `const_cache.rs`, with a text format, a hand-rolled encoder and decoder, temp+rename writes, and corrupt-is-a-miss. There is one flush call at the end of `const_eval::evaluate` and one `set_disk_root` line in the CLI. The table is `<package cache dir>/.cache/const-sites`, beside the macro-expansion table, stamped with format, toolchain and `BUILD_ID`. A `const let` closure snapshot carries an entity id, so it is not persisted.
  - Premise partly wrong. The brief's target was kolt client const pass <= 10% of 173-251 ms. Measured on a release build, quiet-ish box, `check src/client.vl`: const pass 258 to 47 ms CPU (18%), const-interp 208 to 6, second check `const-hits=168 const-misses=0`. The remaining ~32 ms is not evaluation (lowering 9 ms, the const checks, reach walk, liveness scan), so a result cache cannot reach 10%. Filed as M?1.
  - RSS: my first version was +4.4% over the base (duplicate buffers). I restructured it to render the file from the in-memory cache at flush, and it is now +0.4% (base 267.9 MB, tip 269.9 / 268.9 MB; `scripts/rss-probe.py`, 5 runs x 2).
- E296 + B597: the message sites (Wire field messages, Hashable/PartialEq field messages, the rpc ones, handle element/key) now quote through a new `render_type_quoted`. It handles tuple (labelled too), array, closure, view and `async`/`sync`/`dyn`, also nested (`List<[u8; 2]>`). `render_type` itself, which feeds derive codegen, is untouched. For an `[rpc]` type that is a tuple, array, closure or view, the `[service]` attribute's generated-code restatement stands down by reusing B490's `rpc_opaque_return_origins` filter, so there is one refusal naming the type. Pins cover array, tuple, labelled tuple, tuple return, closure parameter and derive-field quoting. `module_resolution.rs`'s expected text changed from `_` to `|i53| i53`. The brief said "listed arm in macro_std", but the text is built in analyzer.rs, not macro_std.
- K29: premise already satisfied. The website's `worker.js` already spells `std::web::prelude` (done with the v0.44.0 site rewrite). The owner ruling says no per-version spelling is needed, but the brief asked for one. The patch spells `std::web` for wasm before 0.44 and `std::web::prelude` otherwise, keyed on `glue.version()`. It is at `/home/reed/code/vilan-lang/proposals/scripts/integration/sweeps/order51/tools-51/website-k29.patch` and dry-run applies with `patch -p1` to `vilan-website/src/playground/worker.js`. It touches no website git.

FUNCTIONS CHANGED IN analyzer.rs (no mono.rs, no emitter)
- New: `render_type_quoted` and `render_type_in`; `render_type` is now a thin wrapper.
- `check_wire_boundary` (message sites only).
- The rpc signature check (`check_rpc_wire_signatures`, my name for it; I did not look it up): the quote swaps, plus the origin insert for non-nominal types.
- A few sibling message sites for Hashable/PartialEq field messages and handle element/key.
- No hot path touched. Late writes stay zero.
- Perf run twice: `scripts/ci-local.sh perf` with `VILAN_PERF_CLASS=reference`, all 12 rows at x0.98-0.999, growth x1.929, T2 green. The second run was on the final tip.
- Also touched, outside my usual files: `const_eval.rs` (one flush line) and `lib.rs` (the `BUILD_ID` constant).

GATES (final tip, ci-test profile unless noted)
- Full suite `-E 'not binary(deep_nesting)' -j 6`: 10291/10291 passed, 31 skipped.
- Native differential: 259/259 in the default mode and 259/259 under `VILAN_NATIVE_DIFFERENTIAL=1`.
- `ci_ignored_pins`, hygiene, corpus, `check_scope_differential`, `diagnostics_ledger`, `harness_scratch`, `agents_map`: 72/72.
- clippy `--workspace --all-targets -D warnings`: clean. `cargo fmt --check`: ok. `vilan fmt --check .`: ok.
- Deep-nesting canary `VILAN_CANARY_STACK_KIB=1536`: RED on `a_thirty_level_chain_still_fits_libtests_own_two_mib_thread`. It is the base's known red since 68f25eb1 (N169, incr-51a's item); I did not touch the module walk or any recursive pass, and did not rebuild a pristine base to re-confirm.
- The vilan-lsp record/table gate was not triggered (no records or tables moved).
- No rebase done.

FINDS
- Filed in `/home/reed/code/vilan-lang/proposals/scripts/integration/sweeps/order51/newitems51-tools-51.json`: `B?1` and `M?1`.
- B?1: `[derive(Wire)]` fields (any non-Wire type, nominal included) and nominal non-Wire `[rpc]` parameters still draw generated-code restatements at the attribute ("Password has no method 'describe'", "cannot find 'rebuild'", "this expression cannot be used as a type" for a closure field). Repros in `sweeps/order51/tools-51/finds/`.
- M?1: the warm const pass keeps ~32 ms CPU of non-evaluation work.

ONE SIDE EFFECT TO KNOW
While measuring M135 I ran `rm -rf ~/.vilan/check-cache/*` (262 entries, a regenerable cache) to get a cold start. Nothing else was lost.

QUESTIONS FOR THE OWNER (recommendation first)
1. N168 removes the ancestor walk for dev builds too (the brief said debug under an explicit env only; this is the same thing for the CLI and the server). OK to keep? Rec: yes. Std authors in an editor set `vilan.stdPath` (README updated).
2. Is M135's result acceptable (warm const pass 18% of cold, not <= 10%)? Rec: accept, and queue M?1 for the non-evaluation remainder (touches fix-51's const_eval/ConstWorld files).
3. Seal RSS threshold: 1.05 is now a hard gate on the median of 5 fresh runs. kolt's noise floor in my 5 runs was +-1% on the median. Rec: keep 1.05.
4. L24: tell me when `vilan-windows` is registered and I will do the routing; `runner/windows/` is prepared.
5. Note for the integrator: `seal.sh` documents `VILAN_PERF_RSS_THRESHOLD` (my edit sits in the proposals tree, uncommitted); the website patch is saved but unpushed.
