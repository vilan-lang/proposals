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

## syntax-45 — REPORTED 2026-10-01 (tip b2caf49a off 6e6830df; Opus) — NOT merged yet: HELD to merge after the std-editing lanes
- LANDED 4/4: the census (e0476402; generator `tests/marker_census.rs` + golden), B445 (37f234ef; both orders parse), B446 (6ea9c9d6; premise CORRECTED — any failed parameter binder mis-reported at the previous `>`), and the B485 fmt FLIP (b2caf49a; attributes, then `export` + keywords, then the declaration word; std reformatted, 84 sites in 17 files). Not done (Order 46): Q10 `[resource]` on its own line, Q7, Q8, the v0.44 refusal.
- Gates at the tip (base 6e6830df): nextest 9160/9160 (41 skipped), fmt, clippy, `vilan fmt --check` std + examples clean.
- WHY HELD: the flip moves `export` on 84 std lines that solver-a (shared.vl/delta.vl), reactive-45, maps-45 and store-45 are editing. Merging it last, the integrator takes next's std at conflicts and re-runs the MERGED `vilan fmt` over std (mechanical); merging it first would hand every std lane a conflict on each `export` line.
- Finds FILED: B492, B493, B494. Lesson for briefs46: lanes log under their own `target/<lane>-scratch/` (native-45 clobbered syntax-45's suite log in the shared scratchpad).
- Slot → maps-45 resumed (told to rebase onto ba2eebd9).

## web-45 (K25) — REPORTED + MERGED 2026-10-01 (vilan-website main f1d51b2: 3e22fb6 the fix, f1d51b2 the gate; Opus, 155k tokens; no cargo)
- The four seeded examples were NOT broken (live `examples.js` = the repo's). What was: (1) the editor restores the visitor's buffer from localStorage, so anyone who opened the counter before v0.42.0 kept getting the old `count.map` counter, auto-run into an error; (2) the landing page's reactive code panel still spelled `map` (built from token spans, so 34b54bf's text search missed it); (3) the diagnostic demo's underline one column short.
- Fix: a retired-example fingerprint list (`playground/retired-examples.json`, kept by `gen-examples.mjs`) — a restored buffer that is verbatim a retired example opens the current one. Gate: `tests/examples.test.mjs` (every shipped program compiles clean, runs under the DOM stub, the landing panels read back) in the harness ci.yml + deploy.yml run; ci.yml also fetches the wasm and runs the smoke. Red with the fixes reverted (7 failures).
- For the vilan repo (not filed yet → with K26/Order 46): `wasm-smoke.mjs` could compile the website's examples at release time; the book's run-button snippets were not audited. `vilan fmt --check` drifts on the site's main (five files, pre-existing).

## solver-a-45 — REPORTED 2026-10-01 (tip 2477ae79; REPORT-solver-a-45.md) — MERGING (native_differential.rs folded by name: 7 fns + 7 consts; the native copy census regenerated over the merged tree)
- LANDED 7/7: B473, B467+B439, R-c (B483 B466 B465), B474, B453, B444, B464 (BREAKING). Finds FILED: F69 F70 B495 B496.
- Slot → editor-45 resumed (told: rebase before E236; E240/E241 after the arc; E242 only if time). store-45 launches when the merge is pushed.

## solver-b-45 — REPORTED 2026-10-01 (tip 3f89b642 on ba2eebd9; REPORT-solver-b-45.md) — rebase onto solver-a-45's merge OWED, then merge
- LANDED 12 + F65; B455 STOPPED (ruled (B), Order 46); B489 not done (rides opacity). Finds FILED: F71, B497.
- INTEGRATOR OWES on next: `vilan fmt` over `crates/vilan-cli/tests/native/` (five native-45 fixtures red on CI's vilan-fmt leg); the Windows pin fix for perf-45's per-pass split (78627243 on release/0.42) carried to next.
- solver-a-45 MERGED @51de7eb9 (pushed; gates native_differential 111, corpus, inference 4970, copy_elision_census, release_scripts, split green). On next after it: 9ed87261 (the Windows pin fix, cherry-picked from release/0.42's 78627243), baa57390 (five native fixtures formatted). solver-b-45 told to rebase onto baa57390. solver-a worktree + branch reaped. store-45 launches when solver-b's rebase is in (cap).

## maps-45 — REPORTED 2026-10-01 (tip 32d8b8ff on ba2eebd9; REPORT-maps-45.md; the kolt patch saved) — rebase onto reactive-45's merge OWED
- LANDED S0 + S1 + S2 + S3's wire-reply half. Keyed `at(k)`: 3 ms vs 77 s coarse. Finds FILED F72 (blocks native `SetCell`/`keys()`), F73, B498, B499; its find 1 is B473, verified fixed on next.
- Slot → **store-45 LAUNCHED** off baa57390 (S1 + S2; S3 if maps-45 merges in time).
- v0.42.1: release commit pushed on release/0.42 (cut-release --commit; body written); CI verifying it; tag follows.

## reactive-45 — PHASE 1 REPORTED 2026-10-01 (tip 8e49e5c6 on ba2eebd9; REPORT-reactive-45-phase1.md) — NOT merged; phase 2 after solver-b-45's merge (it rebases then)
- LANDED J7+M92 (a context.rs change — solver-b's file, ~30 lines), the F62 field writes, M93, A146, A135's tail, R-k, A144 (BREAKING in principle; no existing hash pin moved). Finds FILED B500, B501, F74.

## solver-b-45 — REBASED 2026-10-01 onto baa57390 (tip 08aadca3; nextest 9231/9231; copy census 567) — MERGING (merge-solver-b-45.log)
## editor-45 — REPORTED 2026-10-01 (tip b228cd4c on baa57390; REPORT-editor-45.md) — merges LAST
- LANDED 10/10: the hover arc, E234, E241, E240, B437 (a real JS miscompile) + B436, E236 (harness + baseline), E242. Finds FILED M101 (a keystroke costs 1.1–1.3 s CPU on kolt; post-passes 57%), M102, B502, B503.
- solver-b-45 MERGED @d9d786ed (pushed; ledger row 604 assigned, 219/220 edited in place; gates native_differential 116, corpus, inference 5004, copy census, diagnostics_ledger, release_scripts, split green). Reaped. reactive-45 resumed: rebase + PHASE 2. Ledger prose OWED in diagnostics-ledger.md: 604 (B482), 219/220 (B478), 576 + 575 (reactive-45), the two solver-a rows.

## store-45 — REPORTED 2026-10-01 (tip 1ac5ce4c on baa57390; REPORT-store-45.md) — S1 + S2 landed; merges after maps-45 (rebased)
- A compiler touch for the ruled `[reactive(..)]` field attribute (parser, formatter, macros, grammars) — overlaps syntax-45 and editor-45 at the merge. Deviation for the OWNER: `StoreSome<P>` as its own type (Q6 vs Q8).
- Nine finds FILED: B504–B506 (three HIGH JS miscompiles in the view family), F75–F77, B507–B509.
- TWO LANES ADDED off d9d786ed (the order's first priority is miscompiles, and the native refusals block what the order built): **solver-c-45** (B504, B505, B506, B496) and **native-b-45** (F72 FIRST, F76, F73, F75; F71/F74 if time). Running with reactive-45 phase 2: three lanes.
- v0.42.1: tag pushed @f2cbb7f3 after CI green on the release commit; release.yml running.

## reactive-45 — FINAL REPORT 2026-10-01 (tip 1658fc57 on d9d786ed; REPORT-reactive-45-final.md) — MERGING (merge-reactive-45.log)
- Phase 2 LANDED: `own` on `SignalCell::new`, B482's std half (BREAKING; + a context.rs fix without which native refused every `effect`), F60 as a TYPE rule (no struct-level `[must_use]` exists), the workarounds removed. Finds FILED F78, B510.

## reactive-45 — MERGED 2026-10-01 @e76e506c (ledger row 605 assigned; 576 edited in place; gates native_differential 119, corpus, inference 5022, copy census, diagnostics_ledger, check_scope_differential 15 (vilan-core's, not vilan-cli's — the first spec was wrong), release_scripts, split green). Reaped.
## v0.42.1 — PUBLISHED 2026-10-01 (tag f2cbb7f3; release run 36953316628 GREEN 17/17; 10 assets)
- The cut: release/0.42 from v0.42.0, six perf cherry-picks + `commit:` markers, 78627243 (the Windows pin fix — the first CI run was red on `test (windows-latest, 1)`: no thread CPU clock, so no `[vilan pass]` line), `cut-release.sh --commit 0.42.1` → f2cbb7f3, CI 36949385432 green on it, then the tag.
- The fold by hand (next had moved): main 44f45dd3 (`Merge v0.42.1 — main catches the release train`); main into next c619d663 (CHANGELOG: the six perf entries moved under `## v0.42.1`; traits.rs took next's) + c93a672c + the header fix — the integrator's fold script DROPPED B473's entry with its neighbour (two entries shared one `---` chunk) and then wrote the restore inside the header comment; both fixed, parity 40/40, `cut-release --dry-run 0.43.0` parses the section. LESSON: fold CHANGELOG sections by marker+head, never by splitting on rules.
- `fold-release.sh v0.42.1` running (docs.yml, deploy.yml, the manifest, the toolchain in both locations): fold-v0421.log.
- maps-45 resumed: final rebase onto next.
- v0.42.1 FOLDED: book + site deployed, manifest v0.42.1, toolchain `vilan 0.42.1 (44f45dd3b)` both locations + the 0.42.1 vsix. Chronicle entry written.

## 2026-10-02 — WSL restarted by the owner (30 GB, 16 cores, 4 GB swap, swappiness 10, earlyoom). Every worktree clean; maps-45 (rebased, b2650cbe), solver-c-45 (5ffd8674, 4 commits), native-b-45 (b6a15fe8, 6 commits) RESUMED to finish gates and report. Cap raised to five lanes, jobs 6.

## solver-c-45 — REPORTED 2026-10-02 (tip 7477edc5 on e071b662; REPORT-solver-c-45.md) — MERGING
- LANDED 4/4 (B504, B506, B505, B496) with one shared cause; no golden moved. Finds FILED B511 (HIGH), B512, F79–F81. store-45 told at its rebase which workarounds can go.
- solver-c-45 MERGED @611cb003 (pushed; gates native_differential 123, corpus, inference 5030, copy census, release_scripts, split). Reaped.
## maps-45 — FINAL (rebased tip b2650cbe on e071b662; nextest 9272/9272; native 121/121; shared census 192; copy census 571) — MERGING (merge-maps-45.log)
- After the rebase: B473 and B484 workarounds removed (`sum_by` follows its measure), B482's rule in `MapCount`/`MapSum`, `identity()` on the cells/memos/`SetEntry`. The kolt patch unchanged and re-checked. The harness's interference flag: the lane killed nothing; it removed its own gate logs.

## native-b-45 — REPORTED 2026-10-02 (tip ed357d74 on e071b662; REPORT-native-b-45.md) — merges after maps-45, with the maps pin flipped
- LANDED 6/6: F72, F76, F75, F73 (already fixed at base; pinned + the defect beside it), F71, F74. Native `SetCell`, `keys()`, observing a `StoreSome`, the A146 mirror all build now. Finds FILED B513, F82.
- maps-45 MERGED @f67def61 (pushed; markdown golden regenerated into the merge; gates native_differential 125, corpus, inference 5045, copy census, reactive_channels 38, service_layer 59, check_scope_differential 15, release_scripts, split). Reaped. native-b-45 resumed: rebase onto f67def61, flip the maps pin + stale notes, F79–F81 if small. store-45 rebases after native-b merges (it flips its own pin and drops the B504/B506 workarounds); its S3 goes to Order 46 — the order closes instead.
- native-b-45 REBASED onto f67def61 (tip 6204a0c4, 11 commits): the maps pin flipped (renamed `a138_map_and_set_cells_build_the_same_on_both_backends`; + `map_keys_pipe.vl`, `map_entry_writes.vl`), stale notes removed, **F79, F80, F81 LANDED** (656a25fa, 67d28ddf, 6204a0c4). nextest 9293/9293; native 134/134. MERGING. Find FILED B514 (JS: `*if` over a scalar view prints the pair).
- native-b-45 MERGED @4656ad9f (pushed; gates native_differential 134, corpus, inference tracking+maps, release_scripts, split). Reaped. store-45 resumed: rebase onto 4656ad9f, drop the B504/B506/F79/B505 workarounds, flip its F75 pin, B482's rule, `identity()`. **perf-b-45 LAUNCHED** off next: M103 (bisect + fix the 25–30% LSP regression; BLOCKS the cut), M104 (the multi-document `model.vl` settle), M101's caches if time.

## The owner (2026-10-02): performance must be GATED — M105 FILED; `perf_compare.py` written and wired into `seal.sh` (tip vs the previous release on kolt: check CPU + RSS, and the LSP harness when the tree has it; red past x1.10; smoke-run release vs release: x0.96, green). Paper lane papers-b-45 launched.

## store-45 — REBASED 2026-10-02 onto 4656ad9f (tip 0380a96b; nextest 9321/9322 → fixed; native 136/136; shared census 196) — one more commit owed before the merge: A147 (maps' `KeySlots::identity` collides with cell identities — WRONG VALUE on next), which the lane fixes with one std minting function. Finds FILED A147, F83, B515, B516.
- **A148, M106, K27 FILED** (the owner, 2026-10-02): the `Hash` prefix on the reactive map/set cells (unreleased — cheapest before the cut; which names take it is the owner's); compiler optimization suggestions; `then` is highlighted in VS Code and the book but NOT in the playground editor.
- RULED (the owner): A148's scope as recommended → lane rename-45 after store-45 merges; K27 now (web lane resumed); M106 as recommended — COMPLEXITY counts, not time; Order 46.

## web-45b (K27) — MERGED + DEPLOYED 2026-10-02 (vilan-website main 06efc1f)
- The playground's keyword lists are generated from `vilan --print-keywords` (28 reserved, 14 contextual); contextual words painted only in position (`then`, `as`, `context`, `dyn`, `lazy`, `only`, `sync`; `with`/`own`/`jump`/`borrows` no longer everywhere); `resource` removed, `css` added. Gate `tests/keywords.test.mjs` (245 checks) in the harness CI and deploy run. For the vilan repo: neither toolchain grammar paints `only`; `--print-keywords` could emit positions.

## papers-b-45 — REPORTED + MERGED 2026-10-02 (proposals main eb2ef88; performance-gates.md, 6,755 words; Opus, 209k tokens)
- Measured on v0.42.1 (load 6–24): wall spread 242%; CPU 62% (CV 6.9% at steady load, +37% under 16 busy loops; the LSP row 2× from load alone); `instructions:u` 1.2 ppm; callgrind Ir 0.12 ppm; peak RSS 0.04%. kolt's check is ~100% serial; Amdahl: parallel analysis ×1.79–2.48 on 8 cores, entries overlapped too ×2.31–3.21; M100 alone ×1.22. Per 1,000 lines: vilan 36 → 107 ms (6k → 49k), kolt 122–143; `cargo check` on syn 24–31; `tsc` 5–11.
- Q1–Q12 OWNER (three tiers: counters + shape tests in every gate; instruction budgets in a required CI `perf` job; CPU limits on the quiet reference machine at the seal and the cut; the cut refuses without a green verdict). Slices S1–S8.
- Finds: **M107 FILED (HIGH: check is close to quadratic in package size)**; `perf_compare.py` fixed by the integrator — per-child usage via `os.wait4` (the RSS ratio was ×1.00 by construction), a load guard (`--max-load 2`), a discarded warm-up run; the LSP leg still only prints (the harness is on editor-45, unmerged). malloc+free are 21.7% of kolt's check (allocator probe — in the paper's order).
- **performance-gates.md Q1–Q12 RULED as recommended** (the owner, 2026-10-02). Status line, stamps (M105, M106, M107), go-items45's Order 46 queue.

## store-45 — MERGED 2026-10-02 @276f4ed2 (final tip 7c65dc69: A147 fixed with `std::shared::fresh_identity()`; nextest 9323/9323; merge gates native_differential 136, corpus, inference store+maps+tracking 98, diagnostics_ledger, check_scope_differential, vilan-core lib 931, release_scripts, split). Reaped. A142 S7's S1 + S2 are on next.
- **rename-45 LAUNCHED** (A148) off 276f4ed2; **syntax-45 resumed** for its rebase (redo the std reformat, the `reactive` census row, B488/B492/B507 if small). editor-45 gets one small rebase after both. perf-b-45 still running (M103 blocks the cut).
- Ledger prose WRITTEN 2026-10-02 (604–610; amendments to 15, 219, 220, 229, 575, 576 and the view-parameter row).

## rename-45 (A148) — REPORTED 2026-10-02 (tip 2d5d471d on 276f4ed2; nextest 9323/9323; native 136/136) — MERGING
- `HashMapCell`, `HashSetCell`, `HashMapEntry`, `HashSetEntry`, `HashMapMemo`, `HashSetMemo`, `TrackedHashMap`; modules `std::hash_map_cell`/`std::hash_set_cell`; shape names and `MemoEntry`, `MapKeys`/`MapValues`/`MapEntries`/`MapMapValues`/`MapFilter` kept. One grep hit left: the CHANGELOG's old → new list.
- The kolt patch rewritten (names) and `get_channels` moved to `channels.keys()` (same `MemoCell<List<u53>>` return; checks clean, builds JS + native; runtime unverified — the client leg has the owner's in-progress errors).
- NOTE for the syntax-45 merge: tree-wide `vilan fmt --check` is red on eight `tests/native/*.vl` fixtures (pre-existing on next; CI's vilan-fmt leg) — the reformat at that merge covers them.
- rename-45 MERGED @c848659d (pushed; gates native_differential 136, inference maps+traits+store 380, docs 12, shared_census, markdown_golden, reactive_channels 38, release_scripts, split). Reaped. LESSON for briefs46: resolve a gate's crate from the tree (`find crates -path '*/tests/<name>.rs'`), never from memory — two merges stopped at exit 8 this order.

## perf-b-45 — REPORTED 2026-10-02 (tip 86f4466e on 276f4ed2; REPORT-perf-b-45.md) — MERGING
- **M103 FIXED**: the regression was maps-45; kolt's check is now 30% UNDER v0.42.1 by instructions (24.40 → 17.01 G). M104: one fix landed, the entry-world design is the OWNER's (diagnostics would change). M107: two of five passes. Peak memory still +20% → M108 FILED; E244 FILED.
- RULED (the owner): M104 → the entry-world design (Order 46 FIRST in editor); the cut goes ahead with M108 as a written exception (the seal's memory leg will read red).
- perf-b-45 MERGED @44d63c90 (pushed; gates vilan-core lib 932, vilan-lsp 930, inference bounds+resources+traits 1265, std_surface, corpus, native_differential, copy census, split, release_scripts). Reaped.

## syntax-45 — REBASED 2026-10-02 (tip 7fdf9ca8 on 276f4ed2; nextest 9336/9336) — MERGING onto 44d63c90
- New on the rebase: the `reactive` census row; **B488, B492, B507 LANDED** (53494611, 2f48900f, f9ae62c7); a formatter fix for two shapes next's own fixtures use (87850c24 → B517 FILED); the std reformat REDONE (113 `export [..]` heads in 21 files) + 8 native fixtures formatted. Rule-site count 59 → 60 (`EXPORT_IS_WRITTEN_ONCE`); ledger row 22 re-keyed.
- The merge: three std conflicts (delta.vl and the two renamed cell files) taken from next and re-formatted with the MERGED compiler; `ci-local.sh vilan-fmt` green before the commit.
- Q10 and field attributes: the ruled paper covers declarations only; field/variant attributes print inline, unchanged — a separate ruling if the owner wants them on their own lines. Left for Order 46: Q10 for `[resource]`, Q7, Q8.
- Ledger prose WRITTEN (row 22, row 229 → 60).
- syntax-45 MERGED @4fdf7cc1 (pushed; markdown golden regenerated; gates vilan-core lib 940, inference 5075, parse_differential, marker_census, deep_nesting 18, module_resolution 216, corpus, native_differential 136, diagnostics_ledger, markdown_golden, shared_census, split, docs, check_scope_differential, release_scripts). Reaped. editor-45 resumed for its FINAL rebase (+ E244's pause row and instruction column in the harness). Then the seal.
