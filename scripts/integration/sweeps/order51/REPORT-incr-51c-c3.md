## incr-51c: hand-back at C3 (P1, the in-process std-only prefix)

P1 is built and every gate is green. It is opt-in: `VILAN_STD_PREFIX=on`, off by default. With the prefix forced on, all three differentials agree with the clean analysis. One limitation for P2: with the prefix on, the language server is slower per keystroke today, so P2 has to layer it under S1 rather than switch it on as is.

- **Branch `incr-51c`:** rebased onto C2 (`9947ec5f`) as you asked; it was a no-op. Tip is **`6938bbca`**. Nothing pushed.
- **My processes:** none running. The `merge_lane_local.sh solver-51` / nextest run, the CI watcher and `~/.cargo/bin/vilan-lsp` that are live now are not mine.
- **Base for this checkpoint:** C2 `9947ec5f`, whose tree is identical to my P0 `56b36ee8`.
- **The commit:** `6938bbca` **std-prefix P1**, family `performance`, with its CHANGELOG entry.

### What P1 does
It uses M110 S1's hot-set shape with every package module hot (std-prefix.md §4.2–4.4, Q1–Q12 as recommended).

- **The stored world is std alone.** The drain skips every package path: modules, pure namespaces and the entry alias.
- **The key is the std closure.** New `std_closure` computes it from the always-loaded modules, std's `lib.vl` and preludes, and every std request the entry and the package write, closed over std's own imports.
  - Different spellings of one std set share a prefix; a superset never serves a subset.
  - If a drain loads a different set than the key names, the world is used but not stored. No such mismatch occurred on kolt, the examples or the corpus.
- **std resolves alone and records every question it asks the impl table.** Then the package registers its modules and namespaces, walks, and resolves over std's answers before the entry walks (new `resolve_package_over_prefix`). This keeps the canonical two-phase order, with std's half done first.
- **The guard runs after that resolve.** A package impl that could answer a question std asked refuses the prefix (`impl-reached`).
- **Other refusals:** a dependency, a package prelude, a reference to the entry module (`pkg::<entry>`), and a module whose text defines a macro.
  - A refusal is remembered per package (the prefix key plus the package's paths), not per prefix.
  - A refused analysis falls back to S1's hot set if the editor named one, otherwise to the canonical world (new `AnalysisShape::std_prefix`, `refusing`, `without_prefix`).
- **S7's item records are off for prefix worlds.** With them on, the main classes-package differential diverged at one step. That is finding B?2 below.
- **Census:** new `prefix-world`, `prefix-hits`, `prefix-refusals` and `prefix-refusal`.

**Functions changed** (analyzer.rs only; no mono.rs or emitter change):
- In analyzer.rs:
  - Changed: `analyze_inner` (the prefix block, `refusal_key`, prefix hits, the drain's package deferral, the closure check before store, both hot-load sites), `load_hot_modules` (namespaces first), `shape_after_hot_load`, `shape_after_impl_reach`, and the `enable_item_records` call site.
  - New: `package_reach`, `hot_set_of`, `std_prefix_set`, `std_closure`, `resolve_package_over_prefix`, `note_hot_refusal`, `note_prefix_refusal`.
  - `hot_set_closure` is now split into the new helpers above.
  - New const `ALWAYS_LOADED_STD`; new fields `HotSet`/`HotWorld::namespaces`, `HotSet::std_prefix`, `BaseCacheKey::std_prefix`.
- In incremental.rs: `std_prefix()`, `set_std_prefix()`, the census fields and both census lines.
- In fx.rs: `shuffling()` is now `pub(crate)`.

### Where the paper's premises were wrong
1. **The S1 shape alone did not agree with the clean analysis.** §4.4 says S1's shape with every package module hot is enough. It needed the package's own resolve before the entry walks; S1's hot modules resolve together with the entry instead.
2. **The use-inferred guard's premise does not carry over.** S1's third guard isn't needed under the prefix, because the package walks in canonical order after std. The one divergence I saw there came from S7's item records (B?2).
3. **The guard is coarser than §4.2 suggests.** Kolt's client is refused on member `get`. The question was asked about an unknown receiver, which admits every impl. With the guard switched off, a minimal fixture holding only that impl answers exactly like the clean analysis.

### Measured
- **Refusals with the prefix forced on:**

| Estate | Result |
|---|---|
| Corpus | 137 of 145 files built over the prefix, 0 refusals (the other 8 are uncacheable) |
| Examples | 8 served; `fullstack` refused (`dependencies`); `todo` refused (`defines-a-macro`) |
| Kolt | server served; client refused (`impl-reached`, member `get`: `impl ProxySignal<T> with Signal<T>`) |

- **Sharing in one process:** a two-entry package whose entries share one std closure goes from 1.40 G to 0.56 G instructions with the prefix on (−60%).
- **Cost of a single cold analysis with it forced on:** `math` +6.4%, `reactive-ui` +2.2%, kolt +21% instructions and +25% RSS (its client builds twice: the refused attempt plus the fallback).
- **The language server with it forced on (informational):** leaf keystroke 4.30 → 4.54 G, `shared.vl` keystroke 1.66 → 1.86 G. Switching the prefix in place of S1 is worse per keystroke.

### Gates on `6938bbca`
- **Full suite** (`--cargo-profile ci-test -E 'not binary(deep_nesting)' -j 6`): 10,496/10,496 passed, 32 skipped. Within it:
  - ci_ignored_pins 12, hygiene 3, corpus 14
  - check_scope_differential 16, permutation_differential 7, edit_replay_differential 23
  - native_differential 270, id_windows 10, vilan-lsp 1,103
- **Native differential, sweep mode:** 270/270.
- **Deep-nesting canary at 1536 KiB:** 18/18.
- **Lint and format:** clippy `-D warnings`, `cargo fmt --check` and `vilan fmt --check .` are clean.
- **`ci-local.sh perf`:** T2 green. P1 vs C2 on the same box: −0.049% to +0.051%, so no bump row. Late writes are 0 on kolt, with the prefix on as well.
- **RSS on kolt** (9-run medians, prefix at its default off): −0.0% and −0.7%.
- **New pins, all green:**
  - `edit_replay_differential::every_edit_class_answers_what_a_clean_analysis_answers_over_the_std_prefix`: 102 analyses, 102 over the prefix, 92 prefix hits, 0 divergences.
  - `edit_replay_differential::packages_with_one_std_closure_share_one_std_prefix`
  - `edit_replay_differential::a_package_impl_a_std_question_reaches_refuses_the_std_prefix`
  - `permutation_differential::the_classes_package_answers_the_same_over_the_std_prefix`
  - `check_scope_differential::corpus_agrees_with_and_without_the_std_prefix`: emitted JavaScript identical byte for byte.
- **Whole binaries with the env forced on** (edit_replay, permutation, check_scope and corpus): 49/60.
  - Corpus is green; no divergence assertion failed.
  - The 11 failures are pins written for S1/S7's shapes:
    - census expectations for hot sets and records: `every_edit_class_answers_what_a_clean_analysis_answers` (S7 record counts), `a_keystroke_rewalks_its_hot_set_and_nothing_else`, `a_check_whose_late_files_write_no_foreign_impl_records_nothing`;
    - plants that only S1/S7 paths trigger: `the_differential_sees_a_binding_the_hot_set_should_have_decided`, `the_differential_sees_a_hot_impl_the_prefix_needed`, `the_differential_sees_a_bound_audit_served_without_its_record`, `the_differential_sees_a_bound_record_kept_over_a_moved_impl`, `the_differential_sees_an_item_record_served_over_a_dirty_dependency`, `the_differential_sees_a_prefix_served_unvalidated`;
    - two package-table pins whose subject can't exist over a std-only prefix: `an_edited_module_is_not_served_its_old_tables`, `a_stale_restored_table_moves_the_emitted_javascript`.
- **E292's six rows** (release, `--runs 5`, errors 0; **load average 7–8 because other lanes were building, so CPU is noisy and instructions are the reading**). C2 → P1, CPU ms / instructions G:

| Row | C2 | P1 |
|---|---|---|
| leaf | 850 / 4.30 | 730 / 4.30 |
| leaf + pause | 2140 / 10.47 | 1960 / 10.47 |
| world | 870 / 4.64 | 770 / 4.64 |
| shared | 280 / 1.66 | 250 / 1.66 |
| model importers open | 920 / 5.45 | 900 / 5.46 |
| css | 1030 / 6.53 | 1040 / 6.53 |

  - Instructions are equal, as expected with the prefix off by default.
  - "model.vl keystroke" and "parse break" are gone from today's kolt: the harness refuses them because their anchors are missing. E292 stays open.

### Finds
Filed in `sweeps/order51/newitems51-incr-51c.json`, now 5 items:
- **B?2:** S7's dirty-records check misses an edited module's push into an unedited module's use-inferred binding when the world is a prefix world.
- **M?2:** the guard's refusal of kolt's client is conservative (unknown receivers versus impls on types the package itself declares).
- **Q?1:** how dependencies and package preludes should take the prefix; P1 refuses both.
- **M?1 and B?1** carry over from the C2 hand-back.

I also added an "As built (P1)" note to `std-prefix.md`, uncommitted in the proposals checkout for you to commit.

### Questions for the owner
1. **How should P2 adopt the prefix?** I recommend layering: the language server keeps S1's hot sets and builds S1's misses over a pinned std prefix. Replacing S1 is measured worse per keystroke (+5.6% leaf, +12% `shared.vl`). Fixing B?2 should come first so item records can stay on.
2. **Should the guard stop matching impls on package-declared types against questions asked about an unknown receiver (M?2)?** I recommend investigating the std site that looks up `get` first, then narrowing it in both S1 and P1. Today it refuses kolt's client, and I found no case where letting it through changes an answer.
3. **Dependencies (Q?1):** I recommend making them hot like the package in P2, proven by the differentials. Keep refusing package preludes until a case needs them.
4. **Should P1 stay off by default until P2?** I recommend yes. A single cold check with the prefix forced on costs 2–6% (+21% when it is refused and builds twice); the payoff is only within one process, where two entries sharing a std closure measured −60%.
