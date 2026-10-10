## incr-49 — final report (C1, C2, C3 handed back; C3 re-handed back at 79366e1d)

**Tip `79366e1d` on branch `incr-49`** (worktree `vilan/.claude/worktrees/incr-49`), above next `71d61dde` (your merge of my C2 tip 434dcf77). Commits above next, in order: `7e0f4dec` (M110 S2b: the label-table record), `1595cc04` (merge of 71d61dde, clean), `21e0e72a` (S2b: the label rows filed only for a seeded analysis), `32af01c7` (C3b: A167's `std::rpc::mirror` seed keyed on the service's surface), `79366e1d` (the hover fix: a reused module's labels skipped only when its record restored them). Nothing pushed. `LANE-STATUS.md` untracked, current. The C3 merge sha never arrived; `git merge origin/next` is the first thing to do when it does (expect a clean merge). The last two checkpoint reports went by `SendMessage` because this hand-back channel was spent at C1; this message is the record.

### What landed on next already (C1, C2)
- **P0** the permutation differential (`tests/permutation_differential.rs`, three permutations, id-free normalized observation; B554 the known red, `#[ignore]`d; the post-pass class in the ERD; the harness shared in `tests/replay_harness/packages.rs`), plus the Windows normalizer fix (6bae4173 on next).
- **P1** B575 (the suspension enrolment rows recorded and replayed), B576 (publish marks: `platform_reason`/`prelude_repair` rendered where the lists leave the analyzer), N153 (the `resolve_world` marks).
- **P2** M128 (the four first-match sites ranked or proved; the for-in `next` lookup admitted under the looping file — the real order dependence).
- **S2a** the bound audit as a Class A window with per-module questions and the late-impl validity test (`late_impl_answers`), two plants, counters; ~−7% on a leaf keystroke, ~−1% on a cold check.
- **A167** store-49's analyzer admission reviewed and applied, the a153 pin un-ignored.

### On the branch, gated, awaiting merge
- **S2b** (7e0f4dec + 21e0e72a + 79366e1d): `expr_types`/`declaration_labels` recorded per module in `ModuleTables` (id order, priced), restored through `RestoredTables`, the builders skipping an id only through `label_row_restored` (the module's record carried rows); rows filed only on a seeded analysis (the cold-check tax: the ungated record cost +0.5–1.25% per cold check; gated, within 0.088% of C2's tree). Measured first: ~0.5 MB of strings per stored world on kolt (0.2% of the editor's 774 MB). Plants `LabelTablesUnrecorded` and the pin `a_reused_module_keeps_its_labels_without_a_seed` (red under the old skip — the C3 merge gate's four empty hovers — green on the fix). Gain: −0.5% of a served keystroke (4.46 → 4.44 G, 5.30 → 5.27 G on the same std).
- **C3b** (32af01c7): `service_seeds` keyed on a function in the file returning `Store<T>`/`StoreSome<P>`, not on the file's imports; kolt's `sources-walked` back to 58/89; leaf 4.44 → 4.28 G, world mode 5.27 → 5.18, pause 15.49 → 14.97; the remainder over C2 is std's growth (M120). Pins `a167_a_service_without_a_store_return_does_not_load_rpc_mirror` (kolt's shape, non-vacuous) and the control.
- **HELD / re-planned:** S3a/S3b for Order 50 (R-l, your recommendation = mine): the design note is in the pass map §7.2 (the emitter-table form L vs the mutation-log form M, recommended; the consumer census 279/68/48 reads in vilan-rust, 19/34/26 in the transformer, seven passes; worth ~183 ms of ~480 served). (c) the graph-once half skipped as not M (the post-rewrite patch needs a per-node remove across six maps and the reverse index). R11 and the shared-cells/capture-plan tables held with reasons in §7.1 (whole-program inputs; cross-module anchors).

### Gates on 79366e1d
Full suite 9,974 of 9,974 (26 slow), 33 skipped; `cargo clippy --workspace --all-targets -D warnings` clean; fmt clean; vilan-lsp 1,084 of 1,084 (the four hovers back); the four differentials 38 of 38 (the B554 pin skipped); `ci-local.sh perf` T2 green, growth x2.005, cold rows within 0.088% of C2's tree.

### Numbers (release, kolt scratch copy; instructions:u, G; load stated in the checkpoint messages)
Session table, complete-statement / mid-typing medians, base 445c9346 → C2 d7da47a7 → C3 1595cc04: views 5.53/4.92 → 5.21/4.60 → 5.44/4.82; theme 5.84/5.48 → 5.71/5.35 → 6.00/5.63; model 5.78/5.50 → 5.68/5.41 → 5.98/5.70; styles 5.74/5.46 → 5.60/5.32 → 5.89/5.60; hot-world refusals 0 everywhere. The C2→C3 rise is store-49's std (434dcf77 without S2b: 4.46/5.30 against 4.44/5.27 with it), of which C3b removed the mirror seed. E121's seven rows (base → C3 → C3b where re-taken): leaf 4.55 → 4.44 → 4.28; +pause 11.62 → 15.49 → 14.97; world mode 5.36 → 5.27 → 5.18; shared 1.62 → 1.68; model 1.70 → 1.79; importers open 6.04 → 6.27; css 6.40 → 6.80; parse break 6.41 → 6.75. Counters on kolt: late-writes 0, reach-questions 0, const-hits 56/112, bound-sites-served > 0 on served keystrokes, labels 18,207 rows / 253 KB (client leg).

### Proposals checkout (UNCOMMITTED, for you to commit)
`analyzer-pass-map.md` §3.2 (N153 rows), §3.3 (B576), §3.4 (B575, the bound audit as S2a), §5.6 (the four sites replaced; a fifth ruled positional place: a trace's same-depth hops), §7.1 (the four S2 rows), §7.2 (the S3 design note). `sweeps/order49/newitems49-incr.json`: M?1 (two admitted default homes with different trait arguments collapse by load order; repro `sweeps/order49/incr-49/finds/default_next_two_homes/`).

### Questions for the owner
None open beyond R-l (ruled). Notes: the reactive_selection ratio pin trips under load (green alone); the "+ pause" row's +4 G between C2 and C3 is std growth times three legs, not the analyzer's — M120.

### State of the box
No job of mine runs; the throwaway worktrees are removed; the kolt copy stays under `target/incr-49-scratch/` for the seal; scratch logs there carry every measurement cited.
