## spike-49 — FINAL addendum: every leg BYTE-IDENTICAL; red list EMPTY; stood down

**Tip `c761e214` on `spike-49`** (above `81454646`, `6988cf9d`; base `origin/next @95bf20a9`), not pushed, family tooling, spike — no CHANGELOG entry; branch kept as evidence (R-i: the owner's word). `LANE-STATUS.md` untracked, final. **Nothing of mine runs** (the one leftover `cargo build --release -p vilan-cli`, PID 2476558, has cwd `.claude/worktrees/incr-49-rss` — another lane's, not touched).

### The per-leg verdicts (all logs under `target/spike-49-scratch/`, summary in `gates-summary.txt`)
| leg | `VILAN_ID_WINDOWS` | verdict |
|---|---|---|
| `pins-2`/`pins-3` (`tests/id_windows_spike.rs`: layout, containment with the `cross` plant, anchoring with the `anchor-off` plant, census-mode ids, the line) | — | 5/5, both runs |
| `diffs-types` = `replay_differential` + `check_scope_differential` + `edit_replay_differential` + `permutation_differential` | types (type ids relocated into their anchors' windows) | **40/40, 0 skipped** (439.7 s) |
| `diffs-all` | all (entity, type AND scope ids relocated) | **40/40** (391.5 s) |
| `diffs-walk` | walk (windows + room, nothing relocated) | **40/40** (385.6 s) |
| `corpus-types` (the `.mjs` goldens through the debug binary) | types | **13/13** |
| `corpus-all` | all | **13/13** |
| `native-types` (`VILAN_NATIVE_DIFFERENTIAL=1`, 233 tests) | types | first run 220/233 — the 13 reds were ALL my `[vilan windows]` stderr line inside the compiled program's asserted stderr (instrument noise, no behaviour); fixed in `c761e214` (the line and the dump print only under `VILAN_COUNTERS`, as the counters line does); **re-run `native-types-2`: 233/233** |
**RED LIST: EMPTY.** The corpus differential is byte-identical with windows forced on in every mode, the permutation differential green with no known red (B554 closed), the M128 classes and the post-pass class green, every existing plant still red-as-planted. Neither predicted red (`frozen_entity` over a relocated resolve-time entity in `all`; a B217 re-anchor through a generated window in `types`) showed on the corpus — each remains a differential class to ADD in S6, not a finding.

### The session rows (views.vl, ten keystrokes, world mode, instructions to idle in G; hot-world refusals 0; `session-<mode>.log`)
| mode | keystroke 1 (cold world) | mid-typing (2–6, 8) | complete-statement (7, 9, 10) |
|---|---|---|---|
| 0 (off) | 10.90 | 4.66–4.67 | 5.24–5.25 |
| types | 10.96 | 4.68–4.69 | 5.26 |
| all | 10.93 | 4.67–4.68 | 5.25–5.26 |
+0.3–0.4% per served keystroke in either relocating mode = the census's binary searches (per constraint anchor, per world-changing write); a landed form keeps the anchor and drops the census. Cold kolt check: off 14.135/14.168 G; census 14.213; walk 14.233; types 14.248; all 14.238 (+0.5–0.8%).

### The sizing evidence (new since the full report; `windows-dump.txt`, kolt both legs, 6,830 windows under `types`)
Fixpoint type mints per item: p50 7, p90 59, p99 480, max 5,203 (sum 255,842 against the walk's 48,527); 2,702 items (40%) mint none; the fixpoint/walk ratio is p50 2.9×, p90 28×, p99 54×, max 219×. Items overflowing a window sized as a WALK RATIO: ×8 1,966, ×16 1,228, ×32 378, ×64 22. The top eight items (generated `lucide_lookup_*`-class bodies, 3–5k mints each against 30–200 walk mints) are what a ratio cannot predict. Entity-lane fixpoint mints never overflow at 1.5× walk (24,578 relocated, 0 spilled in `all`).

### S6/S7 recommendation — final
- **S5 does not land** (R-i: the owner's word; the branch is the evidence and S6's skeleton: `walk_module_items`, the per-constraint anchor, the modes, the census, the pins).
- **S6 (interface firewall over windowed ids), L — PROVEN BUILDABLE** on the corpus: windows in load order holding every walk mint (the four ruled positional answers and the fifth unchanged, by the permutation differential); every anchored fixpoint mint of an item can live in the item's window in ALL THREE lanes with no observation, label, JS byte, native byte or permutation answer moving; `writes_other == 0` (no constraint rewrites another item's slot); 31% of an item's recorded expression types point into another item's window (the record's dependency edges). Needs: type windows sized from the item's PREVIOUS analysis's demand (×1.5; first analysis ratio ×8 + spill; an item that overflows on a re-walk is re-laid out at the end of the id space — it changed), the run-length `type_id_sources` (the padding costs 4 B per slack slot), anchors for the resolve's prepped drains (5,486 + 2,634 unanchored mints per client leg — each prepped row carries an entity id), two new differential classes (`frozen_entity` over a relocated resolve-time entity in a std item; a B217 re-anchor through a generated-expansion window). Gates: the six legs above byte-identical under `all`, a "body edit re-walks one module" pin, `relocated_outside_anchor == 0` and `writes_other == 0` as standing counter pins.
- **S7 (per-item records, the edited item's diagnostics first), L** — blocked only by M134 (filed by you): the 18,619 post-settle type mints per client leg with no per-body anchor in six resource/bound passes (`compute_resource_types`, `check_container_resource_arguments`, `check_resource_moves`, the bound audit, `check_resource_generic_instantiations`, `plan_resource_drops`); one anchor hook per pass (M) before a body can be re-checked alone, then the records (L). Gate: "functions checked = 1" + the edited item's diagnostics published first (ruled).

### Not tried
The ci rows (`ci-local.sh perf`) and E121's seven rows; the run-length `type_id_sources`; splitting inline `mod` items into windows; anchoring the prepped drains and the checks' bodies (S7's first step); callgrind; the two new differential classes named above.

### Finds / proposals
M134 filed by you (the unanchored post-settle mints). Nothing else to file: no behaviour red, no pass added/moved (pass map §3 untouched; proposals untouched).

### Questions for the owner (recs unchanged)
1. S6 sizes type windows from the previous analysis's per-item demand — rec yes (a walk ratio overflows 1,228 items at ×16, 22 even at ×64).
2. Land the census hooks ahead of S6 as a skeleton — rec no (+0.5% cold until compiled out); land with S6.
3. `writes_other == 0` as a standing counter pin — rec yes, in S6's gate.

Scratch: `target/spike-49-scratch/` (census-*.log/.perf, windows-dump.txt, census-dump.log, pins-*.log, diffs-*.log, corpus-*.log, native-types*.log, session-*.log, gates-summary.txt, sessions-summary.txt, the scripts, the kolt copy, bin-1/). The kolt copy stays for you to reap. Stood down.
