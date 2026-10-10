## tools-49 report

**Tip `1fdcb6ee` on branch `tools-49`, base `445c9346`.** I did not rebase. LANE-STATUS.md is untracked and stale; the commit list below is current. Ten commits:
- `66e076ee` N156
- `1fdcb6ee` N156 follow-up
- `8a8a5ff5` N161
- `d534bf6e` N155
- `fcaaeac1` N155 goldens
- `071864b8` N139
- `df52bab1` N160
- `b00faeb5` E280
- `712d55a6` E286
- `7041d5d4` B586

Each item has its pins and an `## Unreleased` CHANGELOG entry. Families are `tooling` or `fix`; I created the `## Unreleased` section.

### Per item (all DONE)

**N156.**
- **What changed.** `[profile.ci-test]` in Cargo.toml inherits `dev` with `vilan-core` at opt-level 1. `scripts/ci-local.sh test` and `doctest` select it through `TEST_PROFILE=${VILAN_TEST_PROFILE:-ci-test}`. The default dev/test profiles are untouched.
- **Pin.** `n156_the_suite_legs_run_under_ci_test_and_the_default_profile_is_untouched` in `ci_local_script`.
- **Premise correction.** The profile alone breaks `deep_nesting`. Its three declared-stack pins plant a chain whose walk needs about 12.6 MiB unoptimized, and at opt-level 1 it fits. A full suite under `ci-test` showed exactly three reds, all `deep_nesting`. That binary is also the Windows stack canary, whose strength is the unoptimized frame. So `leg_test` now runs the suite with `-E 'not binary(deep_nesting)'` and runs `cargo nextest run -p vilan-core --test deep_nesting` once on `dev`, on shard 1 only. It keeps both exit statuses.
- **`seal.sh`.** I edited `proposals/scripts/integration/seal.sh` in place. The union, doctest and native-differential legs use `ci-test`. The union excludes `deep_nesting`. The existing canary leg runs it on the default profile. The diff is `sweeps/order49/tools-49/seal-ci-test-profile.diff`.
- **No nextest profile.** The nextest overrides live under `profile.default`, and the cargo profile is what moves cost, so a nextest profile buys nothing.

**N156 numbers** (all under shared load, other lanes and CI running):

| Measurement | Default (O0) | `ci-test` (O1) |
|---|---|---|
| `inference` 41-test sample, CPU (load 12–17) | 25.3 CPU-s (user 23.4 + sys 1.9) | 7.9 CPU-s (user 6.3 + sys 1.6) |
| `inference` whole binary, 5,268 tests, children CPU | 5,841 CPU-s, wall 1,610 s (load 19–29) | 1,726 CPU-s, wall 352 s (load 19–40) |
| Full suite, 9,936 tests | 9,935 pass, wall 2,457 s (load 12–35); the 1 red was the corpus goldens, regenerated | 9,933 pass, wall 1,839 s (load 17–37); the 3 reds were the `deep_nesting` pins, now split out |

- **Ratio.** About 3.2–3.4x CPU on `inference`. The whole-suite wall only dropped about 25% under this load, since the box was saturated and not every binary is analysis-bound.
- **Smoke.** `VILAN_CI_PARTITION=1/400 scripts/ci-local.sh test doctest` is green: 150 tests plus the 18-test `deep_nesting` run on `dev`.
- **Edit tax.** I took the ~17 s versus ~80 s analyzer-rebuild figures from the item and did not re-measure them. A cold O1 build of `vilan-core` plus the `inference` binary took about 83 s wall here.

**Exact command CI and the seal must run:**
- **CI.** `scripts/ci-local.sh test` and `scripts/ci-local.sh doctest`, which ci.yml and release.yml already call. Nothing else changes except the patch below.
- **Seal.** `seal.sh` as edited. Without the script, the union is `cargo nextest run --workspace --cargo-profile ci-test -E 'not binary(deep_nesting)'`, and `cargo test -q --doc --workspace --profile ci-test`.

**ci.yml patch:** `/home/reed/code/vilan-lang/proposals/scripts/integration/sweeps/order49/tools-49/ci-test-profile.patch` (the integrator pushes it).
- **What it changes.** The `test` job's `rust-cache` `shared-key` becomes `suite-ci-test-${{ matrix.os }}`.
- **Why.** Artifacts now land in `target/ci-test/`, so the old key holds a useless `target/debug`.
- **Nothing else needed.** release.yml's `gate` job has no cache.
- **Cost.** Expect one cold run, and shard 1 also builds `vilan-core` on `dev` for `deep_nesting`.

**N161.** `perf_gate.py ratchet --release` now resets only the bumps whose class a measurement covered. A classless bump is reset only when every class with a row for that subject was measured.
- **Path 1.** `--ci-from FILE` absorbs a `ci` bump from a `ci` measured JSON.
- **Path 2 (what the cut uses).** `cut-release.sh` passes `--ci-run-of "$TARGET" --ci-repo "$CI_REPO"`. Only when a bump is waiting, python runs `gh run list --workflow ci.yml --commit SHA` for the green run and then `gh run download <id> -n perf-measured`. It re-adopts the `ci` rows from that artifact at the commit the cut tags from. That is the commit whose CI the cut already requires to be green, and the release commit changes versions and prose only.
- **Left in place.** With no `gh`, no green run, or no artifact, the bump stays in budgets.toml and the ratchet prints `KEPT … (reason)`.
- **Pins in `release_scripts`:**
  - kept (reference-only verdict, also kept when `--ci-run-of` is given but no `gh`);
  - absorbed from a given file;
  - fetched through a `gh` shim;
  - no green run;
  - the cut's call wiring, held as text because the apply step cannot run in a fixture.
- **Red check.** The four behavioural pins were red against the old `perf_gate.py`.

**N155.**
- **Site.** The negative number came from the debounce loop's `Timer::after_for(deadline.since(now()))`, not from the test. A host that stalled past the deadline between `run` and the loop's first `now()` produced it.
- **Fix.** `sleep` and `Timer::after` clamp at 0. Because the clamp is in std, both backends get it. The loop clamps its remaining time as well. I chose the clamp over refusing a negative delay.
- **Pin.** `n155_a_deadline_already_past_fires_and_writes_nothing_to_stderr`: a negative `Timer::after`, a negative `sleep`, and a `Debounce` with a negative delay, with stderr asserted empty. It was red before with node's `TimeoutNegativeWarning`.
- **Goldens.** The std change moved 4 corpus goldens (time, await-postfix, adapt, nursery). `regen_goldens.sh` judged all four runtime-identical.
- **Not run.** I did not run `ci-local.sh perf`: no analyzer, mono or emitter code changed, and the box was never quiet.

**N139.** The audit found that the 50 ms windows only ever carry "it fired before the marker". That claim is guaranteed by timer ordering and is not margin-bound, so widening would cost without helping. The margin-bound claims keep 10x or more (2 s window against a 100 ms gap, 1 s against 10 ms, 200 ms against a 2 s sleep). I wrote the reasoning into `debounce.rs` and the Draft debounce pins in `platform.rs` (comments only). It is audited, not widened.

**N160.** The comment now spells the derived export as `[derive(Wire)] export struct S` and says the rotated form is the parser's own.

**E280.**
- **Fix.** After `serve_from_held_world` serves the file, `did_open` sweeps only the further worlds that no kept world and no open entry holds. Everything already analyzed is passed to `reanalyze_dependents` as answered.
- **Pin.** `e280_a_module_served_from_a_held_world_still_gets_its_further_world` asserts exactly one analysis started and the node world kept. It was red before, with 0 analyses.

**E286.**
- **Fix.** `infer_platform` now takes `pkg_root` and `workspace`. `declares_only_browser` is applied to `pkg::` and `<dependency>::` imports, plus a dependency's browser-only layer.
- **Leak caught by an existing pin.** Reading user-edited modules through `parse_clean_cached` leaked one tree per distinct content, and the `overlay_module_reclaim` pins (`ParseCleanCacheText`) went red. So `pkg::` and dependency files parse into an owned, dropped tree. Only std stays cached.
- **Limits.** The dependency's `lib.vl` re-exports are not followed.
- **Pins.** Two in `module_resolution`, each with a no-declaration control. They were red with the arm disabled.

**B586.**
- **Fix.** `file_project` roots a `[library]` file at the deepest layer root containing it, else the base root. It still gets no platform and no entries.
- **Beyond the item.** I also made the file a module (`EntryMode::OpenFile`). Without that, every library file answered "Cannot execute program without a main function", so the repro could never pass.
- **Pins in `module_paths`:** a nested base-root file and a nested layer file. Red before.

### Gates
- **Full suite, default profile.** 9,936 tests; one red, the 4 corpus goldens, then regenerated and re-run green. This run predates only the commits `fcaaeac1`, `1fdcb6ee` and the follow-up script/pin edits.
- **Re-run since.** Targeted binaries: `release_scripts`, `ci_local_script`, `release_gate`, `ci_ignored_pins`, `hygiene`, `module_paths`, `debounce`, `perf_gate_script`, `workspace`, `module_resolution`, `corpus`, `split`, all green. The `vilan-lsp` suite showed 4 reds from the E286 cache leak, since fixed; the `overlay_module_reclaim` set and E280 re-ran green, but the full `vilan-lsp` binary was not re-run after the leak fix, only inside the full default-profile run.
- **Other checks.** `cargo clippy --workspace --all-targets -- -D warnings` is clean and `cargo fmt --check` is clean.

### Finds
Filed in `sweeps/order49/newitems49-tools.json` with placeholder ids, repros under `sweeps/order49/tools-49/finds/`:
- **B?1.** Library file mode resolves no `[library.dependencies]`.
- **N?1.** `vilan check <std file>` still errors on 11 of 70 std files: intrinsic externs, layer files reaching base modules via `pkg::`, and an `[internal]` field.
- **N?2.** Re-measure the nextest priority tiers under `ci-test`.
- **E?1.** E286 does not follow a dependency's `lib.vl` re-exports.

### Questions for the owner
1. **Is the `deep_nesting` exception right?** I recommend yes: keep it on `dev`, so the Windows canary keeps its worst-case frames.
2. **Should I fix B?1** by resolving the dependency workspace for library files in file mode? I recommend yes, as an S item next order. I didn't try it because that plumbing assumes a `[package]` manifest.
3. **For N?1, close it as "std is not checked as an entry" or analyze std's own directory as std?** I recommend closing with a doc note.
