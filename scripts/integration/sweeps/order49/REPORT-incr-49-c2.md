## incr-49 — mini checkpoint C1b (the Windows fix), with S2a's numbers so far

**Tip `5411f6da`** on `incr-49`. The branch above next's `e95b8f44` holds, in order: `a5d02cb0` (M110 S2a, committed before your priority note arrived), `d7da47a7` (the merge of `origin/next` at e95b8f44, clean — CHANGELOG united itself, both sides' `## Unreleased` entries present), `5411f6da` (the Windows fix, family tooling). Nothing pushed. `LANE-STATUS.md` untracked, current.

### The fix (5411f6da)
Cause confirmed from your panic text: `normalize` relativized rows by stripping a `/`-spelled root, so on Windows every row kept its leg's backslashed absolute directory and the two legs never matched. Now: a row's path token and the root are compared with `\` read as `/` (`slashed`), the root's prose occurrences (a const read's resolved path) are replaced in both spellings, and the nesting prefix and renaming map follow on the slashed form. Unit test `the_normalizer_reads_a_windows_hosts_rows` feeds a Windows-shaped rendering (`D:\a\vilan\vilan\target\tmp\vilan_m110_perm_x_1_0\deep\pa_model.vl …`, in a token and in prose) through the normalizer and asserts the canonical `<pkg>/model.vl` rows with the offsets mapped. CHANGELOG entry written.

**Gates on 5411f6da:** `permutation_differential` + `edit_replay_differential`: 19 of 19 passed, 1 skipped (the B554 pin). `scripts/ci-local.sh windows`: green. `cargo fmt --check` clean.

**How to take it:** if you want only the fix beside store-49, `git cherry-pick 5411f6da` onto next applies cleanly (it touches only `tests/permutation_differential.rs` and CHANGELOG). If you merge the branch you also take S2a (a5d02cb0): its gates so far are the two differentials (green, with the two new plants red under their plants), clippy clean, `fmt` clean — the FULL suite and `ci-local.sh perf` have not yet been run on it (they are C2's, which I was measuring toward). Say which; I will run the full suite + perf next either way.

### S2a as built (a5d02cb0) — the premise correction
The audit's questions are asked AFTER the store, so M121's reach verdict never sees them: the first build (skip reusable sites, record the window) was caught by the new `bound_audit` package — an impl moved in a hot module left the prefix's old verdict in place (the real guard did not refuse). The built version is precise: the recorded-sites walk files, per module, the (call, constraint, trait) questions beside its refusals (`ModuleDiagnostics::bound_questions` / `bound_diagnostics`, kept apart from the Class A rows); a module's refusals replay only while no impl past the stored world's floor answers one (`late_impl_answers`, the verdict's own `impl_subject_admits` test), else the module is re-audited (`bound_recompute_ranges`); a module whose question a late impl answered at RECORD time is never recorded as replayable. The three declaration walks stay Class C (split into `check_generic_bound_satisfaction_declarations`; `push_bound_refusals` shared). Plants: `BoundAuditUnrecorded` (questions kept, refusals dropped) and `BoundRecordUnguarded` (replayed without the late-impl test) — `ImplGuardOff` deliberately leaves this package green, which is the design. Counters `bound-sites-served` / `bound-sites-checked`; the gate asserts served > 0. The mints census: no `Program`/editor/cache/record reader uses a post-settle `TypeId` across two analyses (listed in the CHANGELOG entry). The post-pass packages replay in the gate only now (the plants no longer replay them: ~48 analyses each).

### Numbers (release, kolt scratch copy; load 6–11 during both runs, other lanes active — instructions are the numbers, CPU ms indicative)
E121 rows, `lsp-latency.py --runs 5`, base 445c9346 vs tip d7da47a7 (instructions:u to idle, G; CPU to diagnostics ms):
| row | base | tip |
|---|---|---|
| leaf keystroke | 4.55 G / 590 | **4.23 G** / 600 |
| leaf keystroke + pause | 11.62 / 2320 | 10.90 / 2100 |
| leaf keystroke, world mode | 5.36 / 1070 | **5.05** / 730 |
| shared.vl keystroke | 1.62 / 350 | 1.60 / 240 |
| model.vl keystroke | 1.70 / 350 | 1.65 / 260 |
| model.vl keystroke, importers open | 6.04 / 930 | 5.96 / 740 |
| css keystroke | 6.40 / 960 | 6.38 / 840 |
| parse break | 6.41 / 1240 | 6.36 / 800 |
Session table (ten keystrokes per file, world mode; medians, G): views.vl complete-statement 5.53 → **5.21**, mid-typing 4.92 → **4.60**; theme 5.84 → 5.71 / 5.48 → 5.35; model 5.78 → 5.68 / 5.50 → 5.41; styles 5.74 → 5.60 / 5.46 → 5.32; hot-world refusals 0 on all four files at both. The win is ~0.3 G on a leaf keystroke (−7%) and ~0.1–0.15 G on the cycle files: the paper's 13.5% was measured before M123's memo (solver-48) cut the audit itself to ~a third, and the cycle files' hot sets carry `prefs.vl`'s foreign `impl HashMap with Json`, so modules with a `Json` bound over a `HashMap` are re-audited by design. All eleven ci rows were within ±0.09% at C1; S2a's cold-check cost will be measured with the perf leg before C2.

### S2b findings (for the C2 report; no code yet)
- `compute_shared_cells` unions cell identity over EVERY module's bodies (a hot module can clone or store a prefix cell) and the capture plan / shared reads read `collect_written_roots`, which is whole-program (a hot module writes a prefix binding): NOT prefix tables as the pass map's §7.1 assumed; only the drop extents are per body. Pass map §7.1 annotated (proposals, uncommitted).
- R11's refusals anchor at the instantiation with a note into the callee's body (`emit_generic_leak`): a prefix callee's rows belong to the instantiating module, which may be hot — HELD, noted in §7.1.
- The label tables (strings per expression, ~150k rows on kolt) are the one clean prefix table left; their cost is memory per stored key — a question for the owner before building.

### Next from here
On your word: either run the full suite + `ci-local.sh perf` on the branch now (for the merge of S2a) or continue S2b; then the C2 hand-back with the full-suite count, the perf rows and these tables re-taken on a quiet box if one appears.
