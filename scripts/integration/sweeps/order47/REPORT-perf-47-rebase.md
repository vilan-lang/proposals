## perf-47 is rebased onto `origin/next` @0af433fb and green — tip **@558f00b05399d968aa97ff92960b81a78487db07**, not pushed

Worktree `vilan/.claude/worktrees/perf-47`, branch `perf-47`: 11 commits on 0af433fb (native-47, docs-47 and solver-47 merged), 24 files changed. Every number below is against this new base.

### Conflicts and how each was resolved

- **`crates/vilan-core/src/analyzer.rs`** (in the M118 commit) — solver-47's B533 split `trait_args_for_pattern` into a thin wrapper over the new `trait_args_providers_for_pattern`, which returns `PatternProviders` (`One` / `Ambiguous` / `Fallback`).
  - I kept B533's wrapper and providers logic whole and moved my M118 fast path to the top of `trait_args_providers_for_pattern`.
  - The fast path: when the receiver is a `dyn` of the asked trait itself and what the bound wrote agrees with the object's arguments, it returns `PatternProviders::One(object arguments)`.
  - It can never be `Ambiguous`, because an object carries exactly one instantiation. B533's `ambiguous_bound_providers` already skips `Type::Dyn` receivers, so its refusal is unaffected.
  - `trait_args_for` auto-merged with my fast path intact. The M111 Program-field edits and the M109/M90 additions auto-merged.
- **`CHANGELOG.md`** (in the M111 commit only) — kept both sides, under the one `## Unreleased`: the merged lanes' entries first, then my ten, after a `---` separator.
  - Checked after: no conflict markers, one `## Unreleased`, 37 entry heads for 37 family markers.
- **Clean merges:** `perf/budgets.toml` kept docs-47's two `[[bump]]` rows (reactive-ui and router x1.012) beside my `ci` rows. vilan-rust merged cleanly with native-47's changes.

### Re-checking M118 against B533

I re-ran the identical-answers comparison on the rebased tree with a temporary patch:
- Wherever the object fast path answered, the old scan, through B533's new logic, was run too. A panic fired on any differing answer or on an `Ambiguous` result.
- Run over corpus, inference, docs and module_resolution (5,434 tests), plus the kolt tree, the store-patched copy, v10 and v11: **zero mismatches and zero `Ambiguous`**.
- The one test that failed under the patch was `m118_a_derive_on_a_trait_object_costs_what_its_annotated_form_does`. That was expected: running the old scan alongside mints the very slots that pin counts.
- The patch is reverted. The tree is clean apart from the untracked `LANE-STATUS.md`.

### The flips

None of my new test programs needed a change. They declare their traits in the file, import `Ordering`/`Flow` explicitly, and write no attributes. The full suite is green under both errors.

### Goldens and censuses

Nothing new moved on the rebase. My one deliberate golden (`vilan/test/tuple-access.mjs`) and the copy-elision census (587 → 586) came through the rebase unchanged. The native copy and leak censuses did not move.

### kolt `vilan check`, re-taken

Scratch copy of kolt's working tree, `VILAN_STD` = the base's std. Hardware `instructions:u` via `scripts/perf_count.py`. Release builds with one codegen unit of 0af433fb and 558f00b0. Load was 18–30, so counts only.

| | base 0af433fb | tip 558f00b0 | change |
|---|---:|---:|---:|
| kolt, sequential | 25.29 G / 208.9 MB | 15.49 G / 208.7 MB | −38.8% |
| kolt, overlapped | 25.41 G / 263.0 MB | 15.64 G / 264.8 MB | −38.4% |
| kolt + an unused `Store` import | 25.75 G | 15.78 G | |
| kolt + store exhibits patch | 27.54 G (+8.9%) | 16.16 G (+4.4%) | |
| v10 (M118 original form) | 27.53 G | 15.49 G | |
| v11 (annotated) | 26.34 G | 15.49 G | |

- **v10's `find`:** 45,435 work units at base, 1,872 at tip, against `messages` at 1,147.
- **`--explain-cost` top ten:** the solver columns are identical on both sides (browser leg 493,527 units at base). The selections column now counts at tip:

  | declaration | selections |
  |---|---:|
  | sidebar_shell | 18 |
  | create_search_modal | 43 |
  | `<module level>` | 34 |
  | create_theme_modal | 24 |
  | channel_component | 8 |

  The rest are 0.
- **Late writes:** 0 at every checkpoint, both legs.

### Gate subjects (M instructions)

`perf_gate.py measure` and `ci-local.sh perf`. The base was measured fresh. The base's plain:640 used a fresh check-cache, because the tip's 65,536-entry tables would otherwise warm the base and hide M113.

| subject | base 0af433fb | tip 558f00b0 | change |
|---|---:|---:|---:|
| math | 244.5 | 245.3 | +0.3% |
| watch | 309.8 | 309.1 | −0.2% |
| browser | 1,487.9 | 1,483.0 | −0.3% |
| fullstack | 3,229.3 | 3,190.9 | −1.2% |
| router | 1,910.6 | 1,748.0 | −8.5% |
| reactive-ui | 2,625.6 | 1,950.0 | −25.7% |
| ssr | 4,177.6 | 4,044.7 | −3.2% |
| canvas | 1,492.1 | 1,488.0 | −0.3% |
| rpc | 2,108.4 | 2,074.6 | −1.6% |
| todo | 6,094.8 | 5,281.6 | −13.3% |
| walkthrough | 6,376.2 | 5,444.5 | −14.6% |
| genapp:46 | 9,887.7 | 9,632.4 | −2.6% |
| plain:160 | 2,903.2 | 2,909.7 | +0.2% |
| plain:320 | 5,627.8 | 5,642.7 | +0.3% |
| plain:640 | 13,131.9 | 11,226.9 | −14.5% |

- **Doubling:** 160 → 320 is x1.939 (base x1.939). 320 → 640 is x1.99 (base x2.33).
- **After docs-47's element-syntax conversion:** reactive-ui and router are well under their ceilings × the new x1.012 bumps.

### Gates on 558f00b0

| gate | result |
|---|---|
| `cargo nextest run --workspace -j 6` | 9674 passed, 34 skipped |
| `native_differential` with `VILAN_NATIVE_DIFFERENTIAL=1` | 169/169 |
| `cargo clippy --workspace --all-targets -- -D warnings` | clean |
| `cargo fmt --check` | clean |
| `ci-local.sh vilan-fmt` | green |
| `ci-local.sh windows` | green |
| `ci-local.sh perf` | T2 verdict green, growth x1.939 |

### Unchanged from my earlier report

- The M117 verdict: the store exhibits patch can go to kolt, at +4.4% (its std paths need migrating).
- The seven finds in `sweeps/order47/newitems47-perf.json`.
- The functions-touched list, apart from M118's: the fast path now sits in `trait_args_providers_for_pattern` instead of `trait_args_for_pattern`, and `trait_args_for` keeps it as before.
- The owner questions: whether kolt takes the store patch; pinning the CI `perf` job's toolchain (M?4); and M?2's semantics, which B533's ambiguity rule now also touches.
