tools-52 report. Four items are committed and their gates are green. L24 is skipped because no one told me the Windows runner is registered. Nothing is pushed and none of my processes are running.

**Tip and base**
- Tip: `154e340a1fbfba64ae7a740b07d815ffe78a8178`, branch `tools-52`, worktree `/home/reed/code/vilan-lang/vilan/.claude/worktrees/tools-52`.
- Base: `origin/next` `697c9517`. I did not rebase.

**Commits**
1. `338f60a0` N174, tooling.
   - **Harness:** `scripts/lsp-latency.py` skips a scenario whose anchors are missing, by name, with the reason on stderr.
     - The JSON carries `skipped: [..]` plus `skipped_reasons`. A skipped `parse break` also lists `parse repair`.
     - The run refuses only when no scenario is left.
   - **Re-anchoring on kolt:** `model.vl keystroke`'s References probe now asks `fun global()`, the mirrored store's reader. It is used in `sidebar.vl` and `views.vl`, which are not open.
     - `parse break` and `parse repair` now edit `channel_name.adopt(channel.current_name());` in `channel.vl`, a statement over a `g.channels()` boundary. Shapes are kept; figures are new series.
   - **Gate:** `scripts/perf_gate.py` prints the rows measured and the skipped list beside the LSP rows. It is red on a skipped mandate row, on the tip side or the base side, and a note on an informational one.
     - `perf/budgets.toml` gained `mandate = true` on leaf, css and parse break, and a `series` string. The report prints the series string as a break note under the E121 table.
   - **Seal script:** `scripts/integration/seal.sh` in the proposals checkout is edited (comment plus two grep patterns); you commit it.
   - **Pins:** two new pins in `perf_gate_script.rs`, red against the base scripts first.
2. `ba583735` N173, tooling. `vilan test` builds the source map and runs node with `--enable-source-maps`. The new pin `a_failing_test_names_vl_lines_in_its_stack` in `source_maps.rs` was red before the change.
3. `07feebd8` M141, performance. `const_eval::evaluate` on kolt's client drops from 209.9 M to 187.1 M instructions (about -11%); the whole check drops 24.8 M (-0.28%).
   - `check_const_only` memoises `candidates_of` per (import scope, name): -13 M.
   - It builds the refined dispatch edges lazily, in a new `refined_runtime_callers` method.
   - The explicit pass's `Expr::Local` index holds only the locals inside a `const` expression: -10 M. The inference sweep keeps the full index.
   - Two pins in `inference/bounds.rs` hold the laziness, using a new `const_eval::const_only_refinements()` counter. One guards free locals among locals outside every const in `inference/const_eval.rs`; it passed before and after, since it is an equivalence guard.
4. `154e340a` B619, tooling. New `counters::late_round_mints()`, printed as `late-round-mints=N` on the `VILAN_COUNTERS` line. Three pins are in `inference/macros.rs`.

**Listed arm in analyzer.rs for B619**
- **Where:** the module drain's round loop.
  - `let mut drain_round` is declared before the `loop {`.
  - `count_late_round_mint()` is called in `for (origin, name, module) in discovered`, when `drain_round > 0 && !in_macro_world()`.
  - `drain_round += 1` sits after the `to_load.is_empty()` break check.
- **Coordination:** nothing else changed in `analyzer.rs`, `mono.rs` or an emitter. This lane needs rebasing onto C1 before it merges.
- **Not done:** the refusal itself waits for the std-prefix P3 key check, as the item says.

**Where the item premises were wrong**
- **M141:**
  - `ConstWorld` is already built once per `evaluate`; `new` is 4 M instructions.
  - The reach is computed once per site (169 `reach_from` calls for 166 sites, no retries), so "cache it per site" has nothing to win.
  - The pass was 29 ms on today's tree at load 2.5, not 47, and about 19 ms of it was neither lowering nor interpretation.
  - The real shape is the capability check at 70 M, the local index at 30 M, `prepare` at 42 M and the const cache at 32 M.
  - The lazy edge build saves nothing on kolt. R is non-empty there through std's style functions; it only helps programs with no runtime path to a channel verb.
  - The target of "warm pass under about 20 ms" is not reached (about 26 ms now). The rest is filed.
- **N174:**
  - The harness actually had one missing anchor (`fun messages(self)`, the References probe) in the `model.vl keystroke` row, which the item described as a dead row. Its edit anchors still land on today's kolt.
  - The `parse break` anchors were gone, and `g.channels()` does not appear in `channel.vl` at all. I used the nearest statement that reads through that boundary.
- **B619:**
  - "No instance" holds for the estate. A real instance exists: a derive whose generated impl imports `std::path::basename`, beside a written `import std::time::now;`.
  - Under the installed 0.49.0, `vilan build` of that program and of the same program with a redundant written `import std::path::basename;` emit different bundles; `now` and `basename` swap places.
  - So the item's "would still reorder the output" is confirmed. It is filed as a find with a repro.

**Acceptance: seven-row run, 5 runs each**
- **Setup:** a `cp` copy of the owner's kolt at `dee494ab` with `src/lucide` and `src/search-dict` carried; the installed 0.49.0 (`~/.vilan/bin`) against a release build of my tip. Nothing was skipped on either side.
- **Rows:** all seven rows measured, plus `parse repair`. The break has 1 error, the repair 0.
- **Instructions agree between base and tip within 0.5%.** In G (base → tip):

| Row | Base | Tip |
|---|---|---|
| leaf keystroke | 4.29 | 4.27 |
| leaf + pause | 10.44 | 10.38 |
| shared.vl | 1.66 | 1.64 |
| model.vl | 1.62 | 1.61 |
| model.vl, importers open | 5.44 | 5.42 |
| css | 6.51 | 6.49 |
| parse break | 6.50 | 6.47 |
| parse repair | 6.61 | 6.59 |

- **Not quiet:** the host load was 10 to 17 because the other lanes were building, so the CPU-ms columns are noisy and instructions are the figure to trust. Tip CPU to diagnostics ranged 450 to 1900 ms against targets of 500 ms. `perf_gate.py e121` on the tip JSON: no blocking row red.
- **References probe:** the new anchor answers 4 locations in 3 files.

**Gates, all on the tip tree**
- `cargo fmt --all --check` exit 0; `vilan fmt --check .` exit 0; clippy with `-D warnings` exit 0.
- Full suite, `--cargo-profile ci-test -E 'not binary(deep_nesting)' -j 6`: 10527 tests, 10527 passed, 32 skipped. That covers `ci_ignored_pins`, `hygiene`, `corpus`, `check_scope_differential` and the default-mode native differential.
- Native differential in sweep mode (`VILAN_NATIVE_DIFFERENTIAL=1`): 270 of 270 passed, 1 skipped.
- Deep-nesting canary at `VILAN_CANARY_STACK_KIB=1536`: 18 of 18.
- `scripts/ci-local.sh perf`: green, `T2 VERDICT: green`, late writes zero, growth x1.930. Local class has no ceilings.
- RSS, kolt cold check (`rss-probe.py`, 5 runs, two rounds): base median 269.7 and 275.2 MB, tip 265.6 and 265.8 MB. Within 3%.
- Not run: the vilan-lsp binary tests, since I touched no records, tables or the server; and L24.

**Finds filed**
- File: `/home/reed/code/vilan-lang/proposals/scripts/integration/sweeps/order51/newitems51-tools-52.json`. The brief's path is `order51`, but the existing finds directory is `order52/tools-52/finds`, so the repro `b619_generated_only_module.vl` is under both; the second location is an extra copy. Say which you want.
- `M?1`: M141's ranked residue.
  - `refined_edges` runs twice per analysis (71 M in the context pass, 36 M in the const check), sharing `impl_members_for_bound` scans.
  - The local scan costs 20 M and wants the analyzer to record a const expression's locals (core).
  - `reach_from` costs 17.5 M and wants a memo.
  - The `ConstWorld` drop costs 5.8 M and `live_tokens_of` 5.7 M.
- `N?2`: `seal.sh`'s default `VILAN_PERF_KOLT_COMMIT=984a1dfb` pre-dates the mirrored-store exhibit. A bare `seal.sh` now goes red on the base-side skip of `parse break`, which is by design. The seal must pass the copy of the owner's tree as `VILAN_PERF_KOLT_DIR` and a commit.
- `B?3`: B619's real instance (above).

**Files outside my ownership**
- `crates/vilan-core/src/counters.rs`: the new counter.
- `crates/vilan-core/src/analyzer.rs`: the listed arm.
- `tests/inference/{bounds,const_eval,macros}.rs`: pins.
- No other lane's file is touched beyond the arm. `tools-52-STATUS.md` is untracked.

**Questions for the owner**
1. Re-seeding the E121 series. `parse break` is a new series with `green_seals` 0 (already was). `model.vl keystroke`'s edit anchor is unchanged, so I kept its count of 2 and its blocking flag; only its References probe is new. Recommendation: keep it and let the seal's first reading judge.
2. Should the next seal's base be a committed `cp` of kolt at `dee494ab` or later (the Mechanics already say so), with `seal.sh` refusing to run on the stale `984a1dfb` default (find `N?2`)? Recommendation: yes, refuse.
3. M141's remaining 187 M: do you want the shared `refined_edges` memo (dispatch_refine.rs and context.rs, solver or core territory) in Order 52, or Order 53? Recommendation: Order 53, after S7b settles. It is the largest single saving, about 50 to 60 M instructions across both calls.
4. B619's refusal. Keep it as the P3 key check's, as the item says, or fix the order at the drain by resolving a macro's generated `std::`/`pkg::` references before the first round mints? Recommendation: keep the P3 refusal; the estate reads zero.
5. L24: tell me when `vilan-windows` is registered and I will land the routing. It is ready under `proposals/scripts/integration/runner/windows/`.
