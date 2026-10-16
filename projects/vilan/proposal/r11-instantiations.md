# R11's instantiations on a served keystroke — the largest remaining checks row, and how to make it a record (incr-52a's Q1)

> Status: **DRAFT 2026-10-16 — for the owner's ruling (Q1–Q4).** Written by lane incr-53c of
> Order 53 against `origin/next` @3cbd78ca (C2) plus the lane's own commits (none of which touch
> R11), read in `vilan/.claude/worktrees/incr-53c`. A paper, not a slice: nothing in the tree
> changed for it. Every claim about today's behaviour is a line that was read or a probe that was
> run, and says which. CPU milliseconds are `VILAN_PHASE_TIMING=passes` rows of the language
> server (`scripts/lsp-latency.py --source <kolt copy>`, three runs, loadavg ~4 with other lanes
> building): they are SHARES; the instance counts are exact. kolt is a `cp -r` copy of the owner's
> working tree carrying `src/lucide` and `src/search-dict`.
>
> Related: destruction.md §4 (R11) and §6 (exactly-once), incremental-analysis.md (M110),
> per-module-analysis-reuse.md (M19's records), analyzer-pass-map.md §5 (the checks), incr-52a's
> report (S7b: R11's seed rows and lazy sets), incr-53a's report (M149's row families, the
> move-scan fold R11 now reads), M94 (the lexical candidate index), B463 (inherited defaults),
> B469 (the per-instantiation `Drop` question), B344 (lazy parameters at an instantiation).

## 0. The ask, and the answer up front

**The ask** (incr-52a, Order 52, Q1): `check_resource_generic_instantiations` is whole-program by
construction — an instantiation discovered by PROPAGATION reports at the inner call in the CALLEE's
body, which is another module's — so it cannot join M19's per-module windows or M110 S7's item
records, and after S7b it is the largest row of a served keystroke's checks phase (~30 + 12 ms).
Write the doors: a structural dedup key that carries the propagation chain, per-callee records
with a cross-module validator, a two-phase pass; their sizes, their interactions with the row
families, and a recommendation.

**The answer.**

1. **The row is real and it is almost all instantiation scans** (§1.2): on today's served kolt
   keystroke R11 is 1.1–8.6 ms of seed walk (1.1–1.4 when S7b's seed rows serve), 7–11 ms of
   whole-program sets and 30–42 ms of instantiations, every keystroke, for **34 instances on the
   client leg and 23 on the server's** — about a millisecond per instance.
2. **Every instance's callee is std** (§1.3, probed): on kolt's client 34 of 34 (20 inherited-default
   ADMISSIONS, 11 seeded by calls, 3 propagated), on the server 23 of 23 (20 admissions), and
   **zero violations** on either. The callee bodies, the resource sets and the propagation edges
   are therefore functions of the stored world — the same on every keystroke — and what the
   keystroke can change is only (a) which calls seed an instance and (b) the concrete types an
   instance's `Drop` question (B469) is asked about.
3. **So the door is a record per INSTANCE, keyed by what the verdict reads** (§3, door B): the
   instance `(callee, resources)` plus a digest of the `Drop`-relevant facts of its known
   instantiation types; the record holds the instance's violations (anchored in the callee's body,
   spoken at whatever call reports it), its propagation edges and its sibling verdicts
   (exactly-once, drop forwarding, containers, lazy). A served keystroke replays the worklist over
   records for cold callees and scans only hot ones. Expected: 30–42 ms → ~1–2 ms, and the 7–11 ms
   of sets go too (they are built at the first LIVE instance, of which a served kolt keystroke has
   none). Size M.
4. **The "structural dedup key carrying the propagation chain" is not needed** (§3, door A): the
   dedup key `(callee, resources)` is already structural; what a chain would buy — knowing which
   call reports first — is reproduced exactly by re-running the cheap worklist over the records in
   the clean analysis's order, which the records make affordable.
5. **Recommendation: door B, in Order 54, as a row family in M149's shape** (§5), with the
   instance records filed with the world's checks record and validated by the callee's module
   being cold, the resource-trait set and the `Drop`-nominal digest — and, once P3's file carries
   M19's record (incr-53b's M?2), riding the persisted prefix for std's instances.

## 1. Ground truth

### 1.1 The pass as it is

`Analyzer::check_resource_generic_instantiations` (`analyzer.rs`, read at C2) runs in the checks
phase when the program declares a resource (`declares_a_resource`). It is a worklist over
**instances** `R11Instance { callee, resources, call_id, site }`, deduplicated by
`(callee, resources)` in `enqueued`:

- **Seeds.** First `seed_inherited_default_admissions` (B463): for every `impl` whose subject is a
  resource, every trait default the subject inherits is an instance with
  `resources = [the declaring trait's Self marker]`, `site = Admission` — whether or not anything
  calls it, because every instantiation of such a subject runs it with a resource `Self`. Then
  `r11_discover` over every call in `function_calls` order, under NO known generic resources, so a
  call seeds an instance only when one of the callee's generic parameters is bound to a CONCRETE
  resource. Since S7b the walk asks only the live calls and the restored `r11_seed_calls` rows (the
  calls that seeded an instance when their module or item was last walked).
- **Per instance.** At the first instance the five whole-program sets are built (the move scan's
  fold of loaned captures and value crossings since M149, and M94's three lexical candidate
  indexes over every binding, every place expression and every `is` test). Then, sliced to the
  callee's declaration (`LexicalCandidates::within`): the delta resource bindings, places and `is`
  refinements under the instance's parameter set; the body's calls and closures
  (`r11_body_calls_and_closures`); the `Drop` question's known instantiation types
  (`r11_instantiation_types`, B469); the partial-move roots; the affine scan
  (`scan_instantiated_body`, the one implementation of R1–R9); then the siblings —
  `check_own_generic_exactly_once`, `check_generic_drop_forwarding`,
  `check_instantiation_container_resources`, and `check_lazy_parameters_at_instantiation` when
  nothing else spoke (B344).
- **Reporting.** `emit_r11_violations` speaks at the INSTANCE's `call_id` (the caller's file, B112)
  with the detail anchored in the callee's body; an admission speaks at the impl
  (`emit_inherited_default_violations`). The FIRST call to enqueue an instance is the one that
  reports it.
- **Propagation.** The callee's own calls are discovered again under the instance's resources: a
  generic passing its resource `T` to another generic instantiates that one too, and its
  `call_id` is the inner call — inside the callee's body.

That last point is incr-52a's whole finding: a propagated instance's diagnostic lands in the
callee's module, so a per-item record of "what this item's calls instantiated" would either report
it twice (the callee's record and the caller's) or lose it (neither, once the caller is cold).

### 1.2 The row, measured

Served keystrokes, kolt copy, today's tip (`[vilan pass]` CPU ms, three runs each, load ~4):

| row | world-mode `views.vl` keystroke | lone-document `views.vl` keystroke |
|---|---:|---:|
| R11: the seed walk | 1.1–1.4 (8.1–8.6 on the run that files the rows) | 1.2–2.1 |
| R11: the whole-program sets | 6.9–11.1 | 3.8–4.5 (server leg) / 7.3–10.4 (client) |
| R11: the instantiations | 29.9–41.9 | 5.4–5.5 (server) / 30.2–40.0 (client) |

incr-52a measured 54–60 ms before S7b and 29–40 + 12 after; incr-53a's quiet base read ~30 + ~8.
The seed walk is already a record (S7b); what remains is the sets and the instances.

### 1.3 What the instances are (probe)

A temporary counter in the worklist (not committed; `VILAN_R11_PROBE`), `vilan check` on kolt's two
legs:

| leg | instances | admissions | seeded by a call | propagated | callees in std | violations |
|---|---:|---:|---:|---:|---:|---:|
| client | 34 | 20 | 11 | 3 | 34 | 0 |
| server | 23 | 20 | 2 | 1 | 23 | 0 |

Every callee is a std function (a trait default for the admissions — `Flow`/`Pipe`-family defaults
on kolt's resource subjects — a std generic for the calls). Nothing kolt wrote is instantiated at a
resource, and nothing reports.

## 2. What an instance's verdict reads

Read off §1.1's steps, for one instance `(callee, resources)`:

1. **The callee's body** — its expression tree, its bindings and places, its lexical closures.
   For a std callee: the stored world's, identical on every hit (§2.1 of the std-prefix paper).
2. **The resource set**, as constraint ids of the callee (or the trait's `Self` marker) — the
   callee's own ids — and `type_is_resource_with` over the body's types, which reads the program's
   resource TRAITS and `[resource]` nominals. A package can add neither to a std type's
   resource-ness without writing an impl the B401/M121 reach machinery already records.
3. **The known instantiation types** (B469) — the concrete type each resource parameter stands for
   at THIS instance's reporting call (an admission's impl subject, an inherited default's receiver,
   a call's recorded arguments). They are asked one question: does the aggregate hold a `Drop`
   anywhere inside (`collect_partial_move_roots`). This is the one input a package type flows into.
4. **The whole-program sets, sliced to the callee** — loaned captures and value crossings whose
   ids are the callee's own; the candidate indexes, sliced to its span. For a std callee these are
   std's rows.
5. **The propagation edges** — the callee's calls and the resources each binds under the
   instance's set: a function of (1) and (2).
6. **Who reports** — the first enqueuing call, in seed order then BFS order: the one input that is
   about the WHOLE program, and the reason the pass cannot be cut per item.

Only (3) and (6) can move on a keystroke for a cold callee; (3) only when the reporting call's
concrete type changes `Drop`-ness, (6) only when a hot call seeds or stops seeding an instance
ahead of a cold one.

## 3. The doors

### Door A — a structural dedup key that carries the propagation chain (incr-52a's sketch)

Key each instance by `(callee, resources, chain)` where `chain` is the sequence of callees from the
seeding call, so a per-item record could say "this item's calls instantiated these chains" and a
replay could reconstruct who reports.

- It changes the DEDUP semantics: today two chains reaching one `(callee, resources)` are one
  instance reporting once; keyed by chain they are two, and the second must be suppressed again by
  the old key — so the chain is metadata, not a key.
- What it would buy is (6): knowing which call reports first. But re-running the worklist itself
  is cheap — the seed walk is 1.1–1.4 ms with S7b's rows, the BFS over 34 instances is
  microseconds — once each instance's SCAN is a record. The chain does not have to be recorded; it
  is recomputed.
- Size M; value: none beyond door B's. **Not recommended.**

### Door B — a record per instance, with a cross-module validator

File, per world (with M19's checks record — `WorldChecks` — as M110 S3 filed the post-pass
record), one row per instance the world's analysis scanned:

```text
key:     (callee, resources, drop_digest)
value:   violations (anchored in the callee body; spoken at the reporting call)
         propagation edges: [(inner call, child callee, child resources)]
         exactly-once / drop-forwarding / container / lazy verdicts (each anchored in the body,
           or at the reporting call, as their emitters already split them)
```

`drop_digest` is a hash over the `Drop`-nominal set restricted to the instance's known
instantiation types — the digest M149's item asked for and M149 found unnecessary for the move
scan, needed here because B469's question IS per instantiation. An instance whose known types are
all std's has a digest of std facts alone.

A served analysis runs the worklist as today — seeds (S7b's rows and the live calls), dedup,
first-enqueuer-reports, BFS — but for an instance whose callee is COLD and whose key has a record,
it emits the recorded verdicts at the current reporting call and enqueues the recorded edges,
scanning nothing; a hot callee, or a key without a record, is scanned live (building the sets
lazily, as now). Validators: the callee's source is cold (`Program::cold_entity` on the callee),
the record's world matches (the record lives with the checks record, keyed by the base-cache key
and the cold fingerprint), and the `Drop` digest is recomputed from the CURRENT known types.

- **Soundness.** Every input of §2 is either part of the key, cold by the validator, or recomputed
  ((6) by re-running the worklist). A hot module adding a `Drop` impl to a type an instance asks
  about moves the digest; a hot module adding a resource impl to a std type is a written impl the
  reach record already refuses the prefix over (M121), and the records sit under the same key.
- **Differential.** The edit-replay differential's classes package needs one resource fixture whose
  hot module (a) seeds a std instance, (b) stops seeding it, (c) changes a reporting type's
  `Drop`-ness, (d) adds a violation to a hot generic's instantiation; the plant serves a record
  past a moved digest.
- **Expected.** kolt's served keystroke: 34 cold instances read from records — 30–42 ms → ~1–2 ms —
  and no live instance, so the sets (7–11 ms) are never built. ~40 ms of a ~150–180 ms checks
  phase.
- **Size M.** The record rows are M149's shape (`row_families.rs`: a family filed only by an
  analysis that derived it, its own live lane); the new parts are the key's digest and the
  replay arm in the worklist.

### Door C — a two-phase pass

Phase 1, per module and recordable: for every generic function and every SUBSET of its type
parameters, the instance verdict and edges ("the R11 summary"), filed with the module's M19 record.
Phase 2, whole-program and cheap: seed, propagate over summaries, report in order.

- Subsets are exponential in a function's type-parameter count, and almost none are ever
  instantiated at a resource (kolt instantiates 34 of std's thousands of generic members) — so
  phase 1 must be LAZY, at which point it is door B with the record filed per callee module
  instead of per world.
- Per-module filing has one advantage: a std callee's summaries could ride the PERSISTED std
  prefix (P3) and serve the first analysis of a process too. Door B gets the same once M19's
  record rides the file (incr-53b's M?2).
- Size M–L. **Door B first; C is B's filing refined, later.**

## 4. Interactions

- **The row families (incr-53a, M149/M150/M148).** R11 already reads the move-scan fold for two of
  its five sets; door B adds a family ("r11-instances") in the same shape and lane discipline. The
  three LEXICAL indexes (M?2 in incr-53a's finds: "R11's span indexes over the whole world, 7.5–14
  ms") become unnecessary on a served keystroke under door B (no live instance) and stay as they
  are for a live one; making them rows is M?2's own slice and independent.
- **S7b's seed rows.** Unchanged and still needed: they are (6)'s input.
- **M144/P3.** Instances are keyed by std ids, which M144 made a function of std alone; a record
  keyed `(callee, resources)` is valid in the canonical and the std-prefix shapes alike (the
  package's own ids never appear in a std instance's key). P3's file does not carry checks records
  yet (incr-53b's M?2, Order 54 with P5).
- **M152's dependency tier.** A dependency's generics are cold in a served world exactly as std's
  are; door B covers them with no extra rule.
- **The lone-document keystroke.** M104's hybrid gives a lone open document its own unseeded
  analysis (no hot seed → no post-pass record filed or read; this lane's find). Door B's records
  live with M19's checks record, which a lone document's base-cache HIT does replay — so door B
  serves both rows, unlike S3's post-pass records.

## 5. Questions for the owner

1. **Door B in Order 54** — an "r11-instances" row family keyed `(callee, resources,
   drop_digest)`, validated by a cold callee and the world's checks key, replayed through the
   unchanged worklist (so who-reports stays the clean analysis's), with the four-shape resource
   fixture and a planted stale-digest record in the edit-replay differential? **Rec: yes** — the
   largest served row (~40 ms with its sets), all of it std work kolt never edits.
2. **Door A (the propagation chain as a key)?** **Rec: no** — the dedup key is already structural;
   the chain is recomputed by the worklist for free once the scans are records.
3. **Door C (two-phase, per-module summaries)?** **Rec: not now** — it is door B filed per module,
   worth doing when M19's record rides P3's file (std's instances then serve a process's first
   analysis).
4. **The lexical indexes (incr-53a's M?2) separately?** **Rec: after door B, and only if a live
   instance on a served keystroke is common** — on kolt there is none, so door B removes them from
   the served row without touching them.
