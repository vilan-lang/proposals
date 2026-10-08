## perf-46: final message (the REPORT file write was refused, so the report text is below for the integrator to save as `sweeps/order46/REPORT-perf-46.md`)

**Branch tip: `perf-46` @64146888.** It is off `origin/next` @fe092e8d with no rebase. Worktree: `vilan/.claude/worktrees/perf-46`. Nothing pushed.

**Status per item**
- **M108: done.** @6f483d85; @3bddf3e8 removes the CLI's last world clones. The CLI's peak memory on kolt is now below v0.42.1's. The LSP is still 6% above it.
- **M107: done.** @9cfc2192. The doubling test is met: 24k → 49k lines costs x1.94 in instructions, against x2.99 on v0.43.0.
- **M105: S2–S8 landed.** @f03701e7 (S2–S4), @95f67815, @cbb558fc (S6), @66852fb9 (S7), @ddfd70f4 and @4099163a (S8), @349088c7 (S5). S2's actual runner measurement can only come from the CI job's own runs.
- **M106: first slice done.** @349088c7, landed with S5 because the ruling ties them. `vilan check --explain-cost` ranks declarations by work counts, never time.
- **M100: done.** @3bddf3e8. Every entry starts at once.
- **N137: done.** @29b3e0e8. The check-cache is bounded and `vilan cache clean` exists.
- Docs: @5a02865a. The mdBook anchor golden was regenerated with mdbook v0.5.4 @64146888.

### Headline numbers

All figures: release builds, macro tables warm, hardware `instructions:u`, peak RSS from `wait4`/VmHWM. The machine was shared (loadavg 2–20).

| | v0.42.1 | v0.43.0 | tip |
|---|---:|---:|---:|
| kolt @984a1dfb `vilan check` instructions | 33.40 G | 25.63 G | **23.61 G** (23.50 G sequential) |
| kolt `vilan check` peak RSS | 259 MB | 328 MB (364 cold) | **251 MB** (198 MB sequential) |
| kolt working tree: instructions / RSS | — | 26.47 G / 431 MB | **25.00 G / 284 MB** |
| LSP VmHWM (harness: leaf + importers-open `model.vl`, 2 runs) | 650 MB | 865 MB | **687 MB** |
| LSP instructions to idle, importers-open `model.vl` | 58.12 G | 41.21 G | **35.56 G** |
| Doubling test, plain 160 → 320 modules | — | 6.40 → 19.16 G = **x2.99** | 2.88 → 5.57 G = **x1.94** |
| Plain 320 → 640 modules | — | — | 5.57 → 13.00 G = x2.33 (filed) |
| kolt wall, client+server (informational, load ~2.5) | — | — | 2.12 s sequential → 1.87 s overlapped |

A dry run of the new seal (tip against v0.43.0 on kolt) read CPU x0.856, RSS x0.855, instructions x0.921. It came out red only because loadavg was 7, which is the load guard working as designed.

### M108: where the memory went and what changed

- **Attribution.** The new `VILAN_COUNTERS=1` lines plus massif, on kolt's client before the fix:
  - building the world: 112 MB;
  - storing a clone of that world in the base cache: +72 MB;
  - the checks passes: +67 MB.
  - Within the checks, `check_generic_bound_satisfaction` added 18 MB and 204k type slots. `check_resource_moves` added 33 MB, because the type table rehashed past 2^20 buckets (one 68 MB allocation, massif's peak). `compute_resource_types` added 11 MB and 299k slots.
  - Of the analysis's 782k type slots, 604k were minted by the checks, each a copy of a type that already existed.
- **Fix.** After the constraint fixpoint, no type slot is rewritten. A new `types_settled` flag marks that point; any later write is counted and refused by a `debug_assert`, and the count is zero across inference, corpus, examples and kolt. From that point `type_id_for_type` interns, and the new `substitute_type_id` reuses a slot its substitution cannot change.
  - Result on the client: 192k slots (14k from the checks), and peak live heap 277 → 227 MB.
  - M100 then stops storing world clones in a one-shot check whose entries can never share one.
- **What is left:** the LSP's +6%. It is the base cache the server legitimately keeps (192 MiB budget) plus std's growth since v0.42.1.

### M107: six quadratic lookups

A callgrind diff of 160 vs 320 modules found six lookups that each scanned something growing with the package. Each now reads an index that gives the scan's exact answer:
1. Member lookup is split by the impl's subject head (lazy, and the full scan runs beside it in debug builds as a check).
2. The two inherited-member scans read a new by-trait index instead of every impl.
3. `type_implements_trait` reads a new provided-trait index instead of every impl.
4. Assignment wiring finds its variable through a position index instead of scanning the constraint queue.
5. The module-load drain uses a heap instead of re-resolving and re-scanning every pending module.
6. Source-range and derived-origin lookups binary-search, falling back to the scan if any ranges ever overlap.

The item's "platform_color x3.8" was #6, the "`analyze_inner` HashMap x3.9" was #5, and the rest fell with #1–#4. What is left: x2.33 per doubling above 50k lines, filed as M?3.

Pins:
- M108: `the_checks_mint_a_type_once_and_not_once_per_call_site` (30 slots per function with the fix planted out, 4 with it).
- M107: `m107_impl_lookups_examine_rows_linear_in_the_package` (x3.47 planted out, x2.00 with the fix).
- S8: the E121 pin went red with its reset rule removed.
- M100: the store-policy pin went red with the policy removed.

### M105 slices: what each one enforces

- **S2.** `scripts/perf_count.py` counts `instructions:u`, falls back to callgrind's count where there is no hardware counter (2.9% higher), and reports each child's own peak RSS. Whether GitHub's runners expose the counter is answered by the CI job's uploaded JSON (filed as M?4).
- **S3.** The new required `perf` job (`ci-local.sh perf`, added to `check`'s needs) runs `perf_gate.py gate` against `perf/budgets.toml`:
  - each row is held to its ceiling +1% times any bump rows, cumulatively, and only on the machine class it was measured on;
  - the growth row (plain 160 → 320 ≤ x2.3) holds everywhere.
  - Ceilings exist for the `reference` class only (examples 29.8 G, the generated app 9.9 G). The `ci` class reports its counts and refuses only on growth until a seal adopts the job's JSON.
- **S4.** `scripts/perf_genapp.py` writes a seeded, deterministic kolt-shaped app. `perf_gate.py calibrate --kolt` compares its phase split with kolt's: every phase is within 10 points except the emission walk (5.3% vs 23.9%), filed as M?2.
- **S5.** `VILAN_COUNTERS=1` prints the solver's work counts (attempts, inferences, selections, slots, impl rows), settled slots, late writes, bound checks and the heap at each phase boundary. Not done: analyses per LSP edit, which is editor-46's layer.
- **S6.** `cut-release.sh` refuses a commit with no green `perf-<sha>.json`, failing closed. `--allow-perf-regression "<reason>"` overrides and writes a `> Performance:` note into the release section. Three pins.
- **S7.** `perf.yml` is a nightly report: CI counts, the ignored perf pins run in release, a callgrind top 25 of the generated app, and a macOS row. `perf_gate.py report` renders a verdict and names the costliest phase; the cut writes `perf/report-vX.Y.Z.md`.
- **S8.** Six `[[e121]]` rows report red until green at two consecutive seals, then block (`perf_gate.py e121`, also run by the seal). Two pins.

### Gates on the tip

| gate | result |
|---|---|
| full suite | 9404/9406; the 2 failures were the anchor golden from my docs heading, regenerated and re-run green |
| inference | 5080/5080 (twice) |
| corpus | green, no golden moved |
| native differential | green in both modes (138/138) |
| `check_scope_differential` | green |
| docs, `release_scripts`, `ci_local_script`, `release_gate`, `ci_ignored_pins`, `perf_gate_script` | green |
| clippy | clean |
| Windows cross-clippy | clean |
| `cargo fmt` | clean |
| `vilan fmt` on tracked `.vl` | clean |

On `vilan fmt`: run over `.` locally, the walk enters my scratch under `target/`, because this worktree's `target/` has no CACHEDIR.TAG. That is local only; the tracked tree is clean. The lane added no `.vl` fixtures.

### Functions touched (for solver-a-46's merge)

**analyzer.rs:**
- Type minting and substitution: `type_id_for_type`, `new_type_id`, `write_type_slot`, `substitute_type` (Closure/Array arms), `substitute_argument_types`, `substitute_type_id` [new], `check_generic_bound_satisfaction` (required_arguments only).
- Member and trait lookup: `impl_member_candidates`, `nominal_member_rows` / `trait_impl_rows` / `nominal_rows` [new], `inheriting_impls_of_declared_homes` (now `&mut self`), `inherited_default_candidates`, `type_implements_trait`, the `trait_ids.push` site plus the provided-trait index rebuild.
- Constraint fixpoint: `wire_prepped_assignment`, `variable_constraint_position` [new], `resolve_constraints`, `cost_owner` / `ranked_item_costs` [new].
- Source ranges and derived origins: `source_of_id`, `derived_origin_row` [new], `declaring_module_source`, `admitting_source_of`, `redirect_derived_diagnostics`, `Program::source_of` / `source_lookup` / `derived_origin`.
- Analysis driver: `analyze_inner`'s module drain plus `load_order_entry`, `analyze_over_world`, the base-cache store call site, the Program literal.

**Other files:** new module `counters.rs`; `lib.rs` pass marks; vilan-cli `main.rs` (global allocator, `check_workspace`, `print_cost_report`, `cache_clean`, `expansion_cache_root`); vilan-embedded (check-cache bound and `VILAN_CHECK_CACHE`); `.cargo/config.toml` (points the suite's check-cache at `target/`).

### Seams and notes for the integrator

- **editor-46:** nothing in the LSP session layer was touched. `vilan-lsp` does not install the counting allocator yet; `CountingAllocator` and `arm_from_env()` are ready for it.
- **`seal.sh`** should call `scripts/perf_gate.py seal --tip … --base … --kolt … --class reference [--lsp-json BASE TIP] [--advance]` instead of `perf_compare.py`. It writes the verdict the cut now requires. A v0.44.0 cut needs that verdict to be green, or the override.
- **First run of the new toolchain:** the first check by a toolchain built from this branch prunes the dev machine's `~/.vilan/check-cache` once. It currently holds 24,745 tables (495 MB).

### New finds

In `sweeps/order46/newitems46-perf.json`:
- **M?1:** `impl_select::applying_implementations` is about 32% of kolt's check. The emitter's member selection misses its memo. This is the next big lever.
- **M?2:** the generated app's emission-walk share is 18.6 points off kolt's.
- **M?3:** x2.33 per doubling above 50k lines.
- **M?4:** adopt the CI class's ceilings after reading the job's first ~10 runs.

### Needs the owner

1. **M108's v0.43.0 exception.** Close it on the CLI figure (251 MB, under v0.42.1's 259), or restate it as the LSP's +6% (687 vs 650 MB)? I recommend closing it.
2. **Branch protection.** The `perf` job is in `check`'s needs, as ruled in Q4. Making it a required status in branch protection is a settings change only you can make.
3. **M100's memory cost.** Overlapping the entries costs memory only when they could share a world. The one-shot store skip removes that cost for client+server packages.