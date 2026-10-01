# Order 45 — running record (the integrator)

- GO 2026-10-01 (briefs45.md). The owner: "Go" — every ask as recommended; both papers ruled; nine lanes.
- Eight lanes launched at GO off vilan next @6e6830df (worktrees `vilan/.claude/worktrees/<lane>-45`; papers-45 in `proposals/.claude/worktrees/papers-45`); model Opus for every lane: solver-a-45, solver-b-45 (rebases onto solver-a's merge), native-45 (takes M91), reactive-45 (PHASE 1: J7+M92, M93, A146, A144, R-k, A135's tail; phase 2 after solver-b merges), maps-45 (S0–S2; rebases onto reactive-45), syntax-45 (census first), editor-45, papers-45. store-45 launches after solver-a-45 merges (it needs B465 + B466).
- Owed by the integrator before the seal: `seal.sh` gains `ci-local.sh wasm` and the 1.5 MiB `deep_nesting` run.
- seal.sh: the wasm leg and the 1.5 MiB canary added (the canary needs `VILAN_CANARY_STACK_KIB` read in deep_nesting.rs — an integrator commit on next at the first merge).

## papers-45 — REPORTED + MERGED 2026-10-01 (proposals main 7178967; f52b4db keywords-vs-attributes.md 5,369 words, c6165f2 opaque-returns.md 4,674 words; Opus, 317k tokens)
- B485's paper: Q1–Q11 OWNER. Nothing changes spelling; the order does (attributes → keywords → declaration word; `export` after the attributes; v0.43 accepts both, v0.44 refuses the old). syntax-45's "accept both orders" for B445 is its step 1.
- B460's opacity paper: Q1–Q11 OWNER. Rec: make a bare-trait return OPAQUE now (reversing "checked, not hidden") — no site in std, examples or kolt uses one yet; build after B473 + B474.
- Seven finds FILED (newitems45-papers.json): B486–B491, F65 (native MISCOMPILE: a generic bare-trait-returning function's instances share one return type). Find 8 (the `[rpc]` fresh-handle warning names `.cell()`) is reactive-45's item 9 already.

## Owner rulings mid-order (2026-10-01)
- **Both papers RULED as recommended**: keywords-vs-attributes.md Q1–Q11; opaque-returns.md Q1–Q11 (a bare-trait return becomes OPAQUE, reversing Order 44's door (i); build after B473 + B474 → Order 46). Status lines, stamps (B485, B486, B489), go-items45.
- **E240, E241 FILED** (the owner's hover items: generic parameters and bounds; match-case patterns). editor-45 told: take them after the arc if time.
- **E242 FILED** (the owner): error spans stay pinned to their code through edits until the next paint. Not handed to editor-45 (its plate is full); Order 46 unless it reports early.

## WSL2 CRASH 2026-10-01 ~16:30 — memory exhaustion (eight lanes + the perf agent compiling at once; 24 GB, swap=0)
- Every agent stopped; the repos are intact (`git fsck` clean), every lane's commits and working tree survived: solver-a-45 30b6eb56 (B473), solver-b-45 87ad8c66 (B475), native-45 c7faf517 (F62 F57 F60 F61 F63 F64), syntax-45 37f234ef (census, B445), maps-45 ac7c2836 (S0; S1 files uncommitted), reactive-45 and editor-45 uncommitted work only.
- RESUMED under a CAP: four agents at a time, `CARGO_BUILD_JOBS=4`, nextest `-j 4`, never two cargo invocations per lane. First four: solver-a-45, native-45 (+F65 if time), syntax-45 (told the marker order is RULED attributes-first — its B445 fmt output is the other way), the kolt perf investigation (+ peak RSS). Waiting for a slot: solver-b-45, reactive-45, maps-45, editor-45; store-45 after solver-a's merge.
- RULE for briefs46: a lane cap of four and the jobs caps, until the machine has swap.

## perf-kolt-45 — REPORTED 2026-10-01 (investigation; REPORT-perf-kolt-45.md)
- v0.42.0 REGRESSED kolt's check 3.3× CPU / 3.9× memory (7.5 s vs 2.3 s; 1,087 MB vs 280 MB); trigger R39's resource traits → R11 over every pipe generic. FILED M94–M100, N137. Lane **perf-45** launched in the freed slot (the same agent, its worktree): M94, M96, M97, then M95; M98/M100 if time. Touches analyzer.rs — merges after solver-b-45, rebased.

## native-45 — REPORTED 2026-10-01 (tip 6984d3a0, 15 commits; REPORT-native-45.md) — merging FIRST (it touches no solver file)
- LANDED F62 F57 F61 F63 F64 F52 F54 F55 M91; F60's native half is a pin (premise corrected); F65 STOPPED → solver-b-45 (the analyzer's inferred return is the last call site's). Finds FILED: F66 F67 F68 E243.
- Integrator commit on next before the merge: 523ff681 (the walk canary honours `VILAN_CANARY_STACK_KIB`; the PARSER canary has no margin at 1.5 MiB in a debug build and stays at 2 MiB).
- Slot → solver-b-45 resumed (with F65 + the B476 repro).
- native-45 MERGED @eb8a8840 (pushed; gates native_differential, vilan-rt, ci_ignored_pins, release_scripts, split green; merge-native-45.log). Worktree + branch reaped.

## perf-45 — REPORTED + MERGED 2026-10-01 @ba2eebd9 (lane tip e5818d76; Opus, 525k tokens; merge-perf-45.log)
- LANDED M94 (86f700d1), M96 (4c01a08e), M97 (9659b4be), M95 (91bac36d; the memo made cheap rather than the set narrowed — consumers are `copy_applies` (JS) and `is_resource_type` (native)), M98 both halves (12f33bf5 `VILAN_PHASE_TIMING=passes` + the emission-walk/program-drop row; e5818d76 `applying_implementations` memoized). M100 NOT started (≤0.6 s wall now) → Order 46. M99 re-measured: a `model.vl` edit in `--watch` — client 0/82 reused, `checks` 730 ms (was 5,183); server 53/53, 110 ms (was 900).
- Kolt (load ~14): wall 10.4–11.3 → 3.95–4.09 s; user 9.0–9.4 → 3.33–3.53 s; peak RSS 1,087 → 258 MB. v0.41.1 (on kolt f04d4cb): 2.37–2.80 s / 2.03–2.14 s / 247 MB. Output byte-identical; no golden moved; lane gates 9156/9156, native both modes.
- Pins: M94, M95, M97, M98 each red with the fix planted back; M96 none (behaviour pins + goldens).
- Left for Order 46: `contexts+graph` 470 vs 170 ms, the emission walk 683 vs 188 ms (`maxima`/`subject_outranks`, the wanted-at-arguments path), M100; `const-interp` 259 ms is kolt's own `lib/search.vl`.
- Merge: CHANGELOG union (2 hunks, parity 15/15); gates inference resources/bounds/traits 1196, diagnostics phase_timing, corpus, release_scripts, split green. Worktree + branch reaped. Slot → reactive-45 resumed (phase 1; told F62 merged).
- solver-b-45 STOPPED B455's remainder for a spelling ruling ((A) `(impl Box)::One` vs (B) `(impl Box with One)`) — put to the owner.

## Owner rulings (2026-10-01, evening)
- **The perf fix NOW, both ways**: a dev toolchain from next @ba2eebd9 installed (install-dev-ba2eebd9.log), AND **v0.42.1** cut with only perf-45's six commits — `release/0.42` from the tag, cherry-picks f3d81234 d9ff9478 85f06178 80b650bb 9676e5ae 3d1791a3 + `commit:` markers (41d02223, adc771d0), pushed for CI (run 36941187043); the cut follows green. The markers must be cherry-picked to next too (§7.3).
- **B455 → (B)** `(impl Box with One)`; Order 46. solver-b-45 told.
- **K25 now** (lane web-45, launched — no cargo), **K26 later** (Order 46). K25, K26 FILED.
- Swap: the owner disabled it on purpose (WSL2 pegged CPU/disk at the memory limit); the cap of four stands.
