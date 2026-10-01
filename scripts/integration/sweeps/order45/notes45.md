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
