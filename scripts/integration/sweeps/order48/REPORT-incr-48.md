## incr-48 report

**Tip `121fe6e9`** on branch `incr-48`, rebased onto origin/next `dfe0c5fc` (debug-48's merge). The original base was `e75bc57c`; the rebase conflicted only in CHANGELOG, and I kept both sides. Nothing is pushed. Since the rebase, next has moved on to `ecf3aef5` (native-48's merge). That touches none of my files except CHANGELOG, so I did not rebase again. Worktree: `vilan/.claude/worktrees/incr-48`. Scratch, logs, binaries and the kolt copy are under `target/incr-48-scratch/`. `LANE-STATUS.md` is untracked and current.

### Commits

| commit | sha | family |
|---|---|---|
| M121 + B553 (impl half) | 418ac4f2 | performance + fix |
| B573 (+ B576's platform half) | ca4af8f6 | miscompile |
| M110 S4 const cache (+ M122) | 121fe6e9 | performance |

### 1. M121 door (b) + B553 — done, accepted
- **Where the premise was wrong.** The door as written was "pre-walk the hot set's impl headers and member signatures into the prefix". It cannot serve kolt:
  - Every member of the impls kolt's prefix could reach has an inferred return (`styles.vl`'s and `theme.vl`'s `impl Style`), so a signature gives the prefix nothing it could use.
  - The impl subjects and signatures name types that only resolve in the hot module's own scope (`styles.vl` imports `theme`, which is also hot).
  - A pre-walked stub stored in the base cache would carry stale spans after any keystroke above it.
- **What I built instead: the reach record (`ImplReachLog`).**
  - The resolve that runs before the store records every question it asks of the impl table: each member looked up and each trait asked after, with the receiver type and whether a package source or only std asked.
  - After `build()`, each impl that joined the world later is tested against that record using the lookup's own `impl_subject_admits`. Members count both directly declared and those inherited through traits it provides (closed over supertraits).
  - If a hot impl answers a recorded question, the hot set is refused (`hot-refusal impl-reached`). This replaces `hot_impls_stay_in_the_hot_set`, which refused by spelling.
  - If an entry impl answers a question a package source asked, the analysis is rebuilt in the deferred order. That is `AnalysisShape::defer_resolve`: the world resolves once, after the entry walks, and is not cached.
  - Questions std asks do not count against entry impls. Otherwise a user blanket impl in the entry would make std's own calls ambiguous; finding B?1 shows a module blanket already does this.
- **The real cause of kolt's refusals had a second layer.** Once the impl guard passed, every kolt hot set hit `generated-new-module`.
  - `load_hot_modules` compared a derive's generated paths raw (`compare::PartialEq`) against the loaded modules, so any hot set that derives anything was refused.
  - Paths are now resolved to their module first. A std module the generated code genuinely needs is learned per hot set (`HotLoadRefusal::Demands`) and loaded into the next prefix.
- **The use-inferred-binding guard stands**, as the brief asked.
- **B553 impl half is closed.** B553's context half is **not an order question**: the deferred order reports `T` unbounded too, while a `run` in any module grounds it. It is pinned ignored and filed as B?2 for the solver.

### B573 — done (added mid-order)
- **Fix:** `analyzer.platform = platform` is now set right after `Analyzer::new()` in `analyze_inner`. Platform is part of `BaseCacheKey`, so this is safe for stored worlds.
- **Your question — yes, the hot-set world had the same hazard.** `load_hot_modules` selects the hot modules' twins on the stored world's analyzer, which carried the default platform. The same line closes it: a stored world now carries its key's platform. `a_hot_twin_module_keeps_its_platforms_twin` pins it and was red without the line.
- No golden moved.
- **B576:** its platform half is fixed by the same line (pinned). Its other half is not a one-line move: `platform_reason` and `prelude_repair` are read by the pre-entry resolve, but they are deliberately left out of the cache key. They need to be rendered when a diagnostic is published (for example a marker substituted at the end of `analyze_over_world`, after M19's records are filed) rather than when the stored world resolves. Left open.

### 2. M110 S4, the const cache — done
- **New module:** `const_cache.rs`. Its key and the differential tests are the three bullets below.
- **The key** is a hash of the program the pass lowers for a site:
  - the world declarations it reaches (std included), memoized by address within one pass;
  - its imports, helpers, prelude (folded dependencies arrive there as their values) and the expression itself;
  - the budgets, the closure-result flag, the compiler version, and "a clean program" (the pass-map paper's recommendation 8).
  - It contains no entity id.
- **Project reads are revalidated, not trusted.** Each `read` / `read_dir` / `digest` / `bundle` / `stage` / `staged` call is recorded with its answer. A cached run is served only after every call answers the same again, which also re-registers inputs, facts and staged lines as a fresh run would. If the replay disagrees, the site runs afresh and is fed the answers already obtained, so no call is made twice. Failed evaluations are not cached. Clean analyses bypass the cache. Hits and misses are on the census and the `VILAN_COUNTERS` line (`const-hits` / `const-misses`); it serves `vilan check` and the LSP alike.
- **The differential gained three const edits:**
  - an input file a site reads, edited;
  - a std function a site calls (`math::minmax`), edited through the std overlay — the std bump;
  - a callee whose value changes while the site's own text does not.
- **Results:**
  - kolt `vilan check` (both entries, one process): 17.71 G → 15.90 G.
  - On a clean keystroke the const pass becomes a hit (the session table's clean rows).
  - Recording costs nothing measurable on a cold check (17.51–17.55 G at base against 17.47–17.54 G for M121).

### 3. M122 — measured, closed by S4
A broken keystroke was cheaper because `const_eval::evaluate` returns early whenever the program has a diagnostic. Phase timing on kolt: post-passes take about 790 ms on a clean keystroke against about 270 ms on a broken one; the const pass is about 440 ms of that, about 400 ms of it in the interpreter. An editor needs the pass's diagnostics on a clean program, so a clean keystroke cannot skip the pass. With the cache, a clean keystroke now costs what a broken one does. This matches the pass-map paper's measurement.

### B554 — analysed, not fixed
The blame lands on whichever push comes first in walk order, and walk order is the drain's name order. That is the solver's element-slot rule: blame the declaration, or name both pushes. It sits outside my files. Its only effect on the hot-set world is through the use-inferred guard, which stands and refuses that shape. kolt has no such binding.

### Session table (S0's ten keystrokes per file, world mode, release builds, instructions:u per keystroke)
Taken on binaries built from the e75bc57c base. Load was 9–40 throughout, so compare instructions, not CPU.

| file | hot set | base clean / broken (G) | tip clean / broken (G) | first keystroke at tip (stores the prefix) | hot-refusal at base → tip |
|---|---|---|---|---|---|
| `views.vl` | 2/29 | 10.12 / 5.88 | **6.56** / 5.88 | 12.12 | 0 → 0 |
| `theme.vl` | 11/29 | 14.00 / 10.1 | **6.91** / 6.55 | 12.16 | 11 `impl` → **0** |
| `model.vl` | 12/29 | 13.86 / 10.0 | **6.84** / 6.57 | 11.60 | 11 `impl` → **0** |
| `styles.vl` | 11/29 | 13.89 / 10.05 | **6.83** / 6.55 | 10.27 | 11 `impl` → **0** |

- At the tip, every keystroke after the first is a base-cache hit. Sources walked drop from 89 to 11 / 12 / 11.
- Late writes are 0 on all 183 counter lines.
- With M121 alone (before S4), clean keystrokes were 10.46 / 10.43 / 10.40 G for theme / model / styles.

### E121 rows (`lsp-latency.py`, 5 runs, base e75bc57c vs tip)
The machine was **not quiet**: load 34–40, with the full suite and other lanes running. Treat the instruction counts as the numbers; CPU times are inflated.

| row | base: G / CPU to diagnostics ms | tip: G / CPU to diagnostics ms |
|---|---|---|
| leaf keystroke | 9.15 / 1810 | 5.61 / 1340 |
| leaf keystroke, world mode | 9.97 / 2020 | 6.41 / 1400 |
| model.vl keystroke | 1.99 / 490 | 1.99 / 470 (green) |
| model.vl keystroke, importers open (cpu_ms) | 14.11 / 3230 | 7.14 / 1580 |
| css keystroke | 10.56 / 2090 | 8.22 / 1870 |
| parse break | 10.57 / 2050 | 8.26 / 1970 |
| shared.vl keystroke | no reading | no reading |

The shared.vl row cannot run on any tree because of a harness bug (filed as N?3). Its keystroke splits its own completion anchor.

### The differential
- **Both legs green**, 10/10 tests on the rebased tip.
- **Classes leg:** 62 incremental analyses, 45 of them hot-set worlds, 26 served from the cache. It now also covers:
  - M121's shapes: a hot inherent impl with inferred returns on a prefix type, and a hot trait impl on a prefix type (both asserted served); a hot `PartialEq` a prefix `==` dispatches through.
  - B553's entry-impl package: the entry's keystrokes defer; the calling module's keystrokes are served as a hot set.
  - B573's browser twin module.
  - The three S4 const edits.
- **Corpus leg:** 580 analyses, 536 hot-set worlds (484 before the generated-path fix), 134 from the cache.
- **Every plant still turns it red:** `HotSetReplay`, `PrefixUnvalidated`, `ImplGuardOff` (now the reach probe switched off), `UseInferredGuardOff`, and the new `ConstCacheUnvalidated` and `ConstKeyWithoutWorld`.

### Pins
- `inference::modules::b553_a_trait_impl_written_in_the_entry_serves_a_module`, `b553_an_inherent_entry_impl_with_an_inferred_return_serves_a_module`, `b553_a_static_member_of_an_entry_impl_serves_a_module` (all three red at base).
- `b553_an_entry_operator_impl_serves_a_module` (the shape the old order already answered).
- `b553_a_module_context_grounded_only_by_an_entry_run`: `#[ignore = "B553: …"]`.
- `inference::modules::b573_a_modules_platform_twins_are_chosen_for_the_builds_platform` (red without the fix).
- `module_resolution::b576_a_modules_twin_note_names_the_builds_platform` (red without the fix).
- `edit_replay_differential::a_hot_twin_module_keeps_its_platforms_twin` (red without the fix).
- `the_differential_sees_a_const_site_served_without_its_reads` and `the_differential_sees_a_const_key_without_its_callees`.
- The classes leg's new assertions: served impls are hot-set worlds with warm hits; the entry-impl package defers; the const cache served sites.

### Gates (rebased tip 121fe6e9 over dfe0c5fc)
- `cargo nextest run --workspace -j 6`: 9799/9799 passed, 35 skipped.
- `native_differential` with `VILAN_NATIVE_DIFFERENTIAL=1`: 182/182.
- clippy `--workspace --all-targets -D warnings`: clean. `cargo fmt --all --check`: clean.
- `ci-local.sh vilan-fmt`, `windows`, `perf`: all green; T2 verdict green, growth x1.938.
- Late writes 0 (kolt check and session).
- The pre-rebase tip (on e75bc57c) also passed the full suite, 9786/9786.
- Not verified: CI's Windows runtime (only the cross-clippy ran here).

### Needs a ruling
1. **Door (b) as built.** M121's door was delivered as the reach record rather than a signature pre-walk, for the reasons in section 1. Accept, or say what else was wanted.
2. **B553's deferred order.** When an entry impl is reached, the analysis is rebuilt cold and uncached. It is correct, but every keystroke in such an entry pays a full analysis. No entry in the estate reaches one.
3. **B576's unkeyed facts.** Render them at publish (my recommendation), or add them to the cache key.

### Finds (`sweeps/order48/newitems48-incr.json`; repros under `sweeps/order48/incr-48/finds/`)
- **B?1:** a user's exported blanket impl in a module makes std's own `items.describe(..)` calls in `wire.vl` ambiguous; the same blanket in the entry is invisible to std.
- **B?2:** B553's context half — an entry `run` does not ground a module's `Context::new()` even when the world resolves after the entry walks.
- **N?3:** `lsp-latency.py`'s shared.vl scenario breaks its own completion anchor with its keystroke, so it never completes.

### Functions touched
**`analyzer.rs`:**
- New:
  - types: `ImplReachLog`, `ImplReached`, `AnalysisShape` (with `FIRST`, `without_hot`, `uncached`, `deferred`), `HotLoadRefusal`;
  - free functions: `note_receiver`, `shape_after_impl_reach`, `shape_after_hot_load`, `hot_generated_demands`, `learn_hot_generated_demands`;
  - Analyzer methods: `begin_impl_reach_log`, `end_impl_reach_log`, `note_member_query`, `note_trait_query`, `impl_reach`;
  - static `HOT_GENERATED_DEMANDS`; Analyzer field `impl_reach`; `World` field `resolve_deferred`.
- Removed: `hot_impls_stay_in_the_hot_set`.
- Changed:
  - `analyze_inner`: signature takes `AnalysisShape`; platform set early (B573); `reuse_allowed` respects deferral; the record wraps the pre-entry resolve; the reach verdict is handled at both `analyze_over_world` calls; the hot-load retry.
  - `analyze_cancellable` (call site).
  - `analyze_over_world`: returns `Result<Option<Program>, ImplReached>`; runs the verdict right after `build()`; computes `hot_sources`; the prelude-seed gate reads `resolve_deferred`.
  - `hot_set_closure`: refusal reasons; adds learned demands.
  - `load_hot_modules`: takes `platform`; returns `Result<(), HotLoadRefusal>`; resolves generated paths.
  - `resolve_constraints`: records which source asked.
- Instrumented with record calls: `impl_member_candidates`, `inherited_default_candidates`, `inheriting_impls_of_declared_homes`, `trait_impl_rows`, `type_implements_trait`, `declares_call_member`, `callable_call_signature`, `bind_trait_qualified_call`, `resolve_try_assert`, `resolve_field_accessor`.

**`incremental.rs`:** `Census` gains `resolve_deferred`, `const_cache_hits`, `const_cache_misses`; `Plant` gains `ConstCacheUnvalidated` and `ConstKeyWithoutWorld`; `report` prints the new phase and counter fields.

**`const_eval.rs`:** `State.world_hashes`, `State::new`, `evaluate` (resets the counts), and `evaluate_inner`'s explicit branch (goes through the cache). **`const_cache.rs`** is new. **`lib.rs`:** `mod const_cache`, and `post_analysis_passes` writes the const census.

**vilan-lsp scheduling:** untouched.

**For the pass map's §3:** no new `[vilan pass]` name.
- M121 adds recording around the pre-entry `resolve_world` and an `impl_reach` verdict between `build` and the checks in `analyze_over_world`.
- S4 caches evaluation inside `const-pass`, specifically `const-interp`; `const-lower` still runs every time.
