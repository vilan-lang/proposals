# Importer reuse: the stub split (M208 lever 1)

> Status: **DRAFT 2026-11-18, for the owner's ruling.** Stage 1 (design only) of lane incr-58,
> written against `vilan` `next` @02e3b989. No mechanism is built. Every claim is marked
> `[ran]`, `[read]` or `[inferred]`.
>
> The question it answers: an edit re-analyzes every module that imports the edited one, whether
> or not its interface moved. On Kolt that is about 21 G instructions per keystroke in a widely
> imported file against about 11 G for a leaf (survey
> `projects/vilan/map/2026-11-17/06-lsp-latency-today.md`). Can importers be reused, soundly?
>
> The answer: not by the mechanism M110's S6 implied (the stored world cannot hold an importer,
> ids are not stable enough, and today's fingerprint is not a complete interface). A different
> mechanism can be sound, the STUB SPLIT, and it depends on `auto` annotations
> (`auto-annotations.md` slice S5): a module qualifies only when every item another module can
> reach has its type written or `auto`-annotated.
>
> Three decisions for the owner are in section 12: whether importer reuse may depend on `auto`
> annotations, whether Kolt's opt-in (315 annotations today) is an acceptable price, and whether
> the smaller win of section 9 goes first.
>
> Related: M208, M110, B570 (`auto-annotations.md`), M140, M19, E369; `incremental-analysis.md`,
> `analyzer-pass-map.md`. The lane's probe and session outputs are on the owner's machine under
> `~/.vilan/gates/incr-58/`.

## 0. The conclusion up front

1. **The saving is real and it is the size the map said.** [ran] On a quiet machine (load
   0.8 to 0.9) a keystroke in theme, model or styles with the entry open costs 20.9 to 22.6 G
   instructions and 2,074 to 2,327 ms of analysis CPU; the same keystroke in a leaf costs
   10.9 to 12.0 G and 1,165 ms. The whole gap is the importers being hot: resolving them
   again (+270 ms), checking them again (+520 ms), loading and walking them (+75 ms).

2. **Stage 2 as the brief wrote it cannot be built on what exists, for two independent
   reasons.**
   - **There is nowhere to keep an importer.** The stored world is, by construction, the
     world WITHOUT every module that imports the edited one. A world that holds resolved
     importers necessarily holds the old edited module too, and nothing can take a module
     out of a world. The id windows of S6 do not make this possible: a window's start is a
     running sum of the sizes of every window before it, so one changed body moves every
     later id in the hot set, and 28% of an item's solver mints spill to a shared tail. S7's
     records cope by storing ids relative to their window and re-basing on replay; a stored
     WORLD holds absolute ids at about 1,400 sites and cannot be re-based.
   - **The fingerprint is not an interface.** [ran] Of 22 valid probes, 6 move something
     an importer shows while the fingerprint of the edited module does not move: the callee
     starts keeping a closure it is handed (a new view-escape error in the importer), a
     generic body stops being move-clean (a new R11 error at the importer's instantiation),
     a `const` callee runs out of fuel, `[deprecated]`, `[must_use]`, a removed `export`.
     A seventh (a second context read) leaves the fingerprint still while, by the paper's
     own probe i2, the callers gain a hidden parameter.

3. **What can be built soundly is a different mechanism, and it merges stages 2 and 3.**
   Keep the importers in the stored world by keeping only the edited module's BODIES out
   of it: walk the edited module's declarations (a "stub": everything but function bodies
   and binding initializers) with the prefix, resolve the importers against the stub, store,
   and walk the bodies after the store, where the hot set walks today. No id is ever
   reused, nothing is ever removed from a world, and "interface unchanged" is a hash of
   text known before anything is walked. It is sound only for a module whose visible items
   all have a type readable from the parse (written, or `auto T` fully written), which is
   exactly what `auto` annotations were ruled for. Today's Kolt does not qualify without
   its opt-in (315 annotations); with it, on a copy, the estimate is 21 G -> 11 to 12.5 G.

4. **That mechanism has two prerequisites that do not exist, so the honest stage-1 outcome
   is "prerequisites, with a spike to settle them", not "proceed to stage 2 as designed".**
   - **P1, a split walk**: a module walked in two phases, declarations then bodies.
   - **P2, positions**: the stored world holds the stub's byte offsets, and every body
     edit moves the offsets of everything below it. 42 analyzer fields carry a `Span`
     directly, more through entity rows.
   A third, **P3, an effects gate**, is needed only for the second half of the saving.

5. **There is a smaller win that needs no prerequisite**, found by the per-pass profile:
   about 335 ms of the 909 ms gap is three costs that are paid for hot importers and need
   not be (section 9). It is not importer reuse and I did not build it.

My recommendation is in section 12.

---

## 1. What I measured [ran]

`scripts/lsp-latency.py --session` on a copy of `~/.vilan/perf-exhibit/kolt-now`, release
build of this worktree (`vilan-lsp 0.56.1 (02e3b989b)`), private caches,
`VILAN_PHASE_TIMING=passes`, `VILAN_INCREMENTAL=measure`. Load average 0.79 / 0.96 / 2.85
before, 0.90 / 0.92 / 2.50 after. Raw: `session/NEW-passes.{txt,json,server.stderr}`; the
table script is `session/passes.py`.

Instructions reproduce lane lsp-58's to the second decimal (theme 20.85 to 21.89 G, model
20.90 to 22.07, styles 21.48 to 22.56, views 10.88 to 12.02).

Median CPU ms per analysis, clean program (the const pass runs):

| phase | views (hot 2/87) | theme (46/87) | model (43/87) | styles (51/87) |
|---|---:|---:|---:|---:|
| `lsp-analyze` | 1,165 | 2,074 | 2,089 | 2,327 |
| load + walk | 190 | 266 | 252 | 271 |
| build (the second resolve) | 66 | 345 | 345 | 372 |
| - of which the fixpoint | 7 | 270 | 269 | 347 |
| checks | 476 | 993 | 1,019 | 1,164 |
| post-passes | 527 | 572 | 565 | 625 |
| `lsp-context` / `lsp-index` / `lsp-landed` | 146 / 94 / 35 | 144 / 96 / 35 | 149 / 97 / 36 | 148 / 112 / 38 |

The checks gap, by pass (theme minus views, ms): the bound audit +177 (it is module grain:
a re-walked file's sites are all live), `compute_clone_sites` +94, the item-record decision
+63 (it prints as `seal_frozen_ranges`, the first mark after it), `compute_resource_types`
+30, `check_resource_moves` +15, the label tables +15, the stage hints +14,
`check_view_escape` +13, `LastUse` +10, `plan_resource_drops` +10, R10 +10, held rows +10,
`check_invalidation` +9. The post-passes barely move (+45): they are whole-program already.

Counters on a theme keystroke: `sources-walked=46`, `records-replayed=140`,
`records-served=1594 records-stale=208`, `bound-sites-checked=15762` (leaf: 5,170),
`live-entities=244808` (leaf: 153,752). Peak resident memory of the session server 2,552 MB.

---

## 2. Why the stored world cannot hold an importer today

- **The hot set is the reverse import closure, with no test.** [read]
  `hot_set_closure`, `analyzer.rs:88708-88766`: the frontier loop at `:88753-88758` adds
  every importer of every hot module; nothing compares anything.
- **The stored world is the world minus the hot set, and the hot set is loaded after the
  store on hit and miss alike.** [read] `analyzer.rs:89096-89115` (the key's `hot` half is
  the missing paths), `:89338` (`load_hot_modules` over the served world), `:88652-88661`
  (the layered build: store, then load the hot modules; the plain miss path I did not read
  line by line). The stated reason is at `incremental-analysis.md`
  section 4.1: "A prefix module that imports a hot-set module cannot be in the prefix."
- **Every reuse built since assumes that closure.** [read] M19's reusable sources are the
  prefix sources the entry did not dirty (`analyzer.rs:92480-92496`); the post passes'
  cold set is "ids below the boundary minus the warm ranges" (`:83366-83458`); the cold
  call graph is cut by id (`call_graph.rs:214-268`) and extended with the fresh nodes
  (`:275-307`). None of them has a notion of a cold module that reads a hot one.
- **No function removes a module, an item or an id range from a world.** [ran] A grep
  of `analyzer.rs` and `analyzer/` finds no remove / unload / retract / purge / truncate
  of a source, and not one `.remove` on the entity, expression or type-slot maps. The
  world only grows past its store point, and the type-slot write attribution
  (`analyzer.rs:28020-28024`) is the only thing that reaches back.

## 3. Id stability: what S6 gives and what it does not

- **A window's start is a running sum.** [read] `id_windows.rs:693-750` (`close`): the
  room added is a function of the item's own walk mints (entities, scopes) and of its
  recorded demand (types); the counter then jumps past it (`:745-746`), and the next
  window opens at the counter (`:655-687`). So an edit that changes one item's walk mints
  moves the start of every later window: the rest of the edited file and every hot module
  walked after it.
- **The stored world's windows are inherited; the hot set's are laid out again on every
  analysis.** [read] `analyzer.rs:89329-89334`, `id_windows.rs:642-653`. [ran] On kolt:
  `windows-laid-out=1936 windows-inherited=7325` per theme keystroke.
- **Solver mints are not confined to the window.** [read] `id_windows.rs:803-831`: with
  no room left the mint goes to the global tail. [ran] On a kolt keystroke: types
  `anchored-in=463753 spilled=185125` (28% spilled), `unanchored=r12984/b15208`,
  `windows-overflowed=2333`. Entities do stay in their windows (`spilled=0`).
- **S7 lives with this by never storing an absolute id.** [read] `item_records.rs:27-34`:
  rows are "re-based on replay by the window's new start", diagnostics "re-based by the
  item's new text offset", and the validator names another item's slot by window key and
  offset (`:285-293`).
- **So the answer to the brief's question (2) is no.** A re-walked module's ids are not
  stable enough for an importer's stored tables to stay valid: the declaration ids of
  every item after the edit move, the type ids an inferred interface is made of are
  minted during the body's walk and solve, and some are in the shared tail. Adding or
  removing an item also shifts every later item's ordinal, which is the windows' key
  (`id_windows.rs:664-672`).
- **And pinning the windows would not be enough.** [inferred] Re-walking a module into
  the same ids REUSES ids with new meaning. Every id-keyed memo in the analyzer (the bound
  audit's, impl selection's, the dispatch refinement's, substitution sharing) is safe
  today only because an id is never reused within a world. That invariant is what B77 and
  B95 were about. I would not break it.

## 4. Is today's fingerprint a complete interface? No. [ran + read]

What the fingerprint holds [read] `incremental.rs:898-1069`: per function, its declaration
label (`analyzer.rs:26213-26299`: name, generics, parameters, return, `borrows`, `bumps`,
the DECLARED context clause) plus `track_caller`, `element`, `async`, a BOOLEAN "context
dependent", the declared contexts, `borrows`, `bumps`, the platform requirement; per struct
and enum its label; per module binding its type label and requirement; globally the impl
headers with member names, trait names with member names, resource types. It is computed
only in `incremental::report` (`incremental.rs:1104-1109`, called at `lib.rs:1489`), after
every post pass.

The probe: `probes/incr58_probe.rs` (a scratch test, run in this worktree and removed; 24
edits of a `lib.vl` that a `user.vl` imports, each analysed clean before and after;
results `probes/fingerprint-probe-results.md`). Two of the 24 are invalid and count for
nothing (I wrote an array length the language does not have, and a type alias item it does
not have). Five more carried an unrelated error of mine both before and after the edit
(the dispatch, trait-default, R11, `Drop` and opaque-return rows); the row each reports is
the diagnostic the edit ADDED, which is unambiguous in each, but a pass gated on a clean
program did not run in those five.

| # | Fact an importer's analysis reads | Where it is computed | In the fingerprint today | Can a body-only edit move it | Evidence |
|---|---|---|---|---|---|
| 1 | Written signature: parameters, written return, generics and bounds | walk + `types` stage | yes (label) | no | [read] |
| 2 | INFERRED return type | body solve | yes (label) | **yes** | [ran] moves; importer error |
| 3 | Module binding's inferred type (incl. use-inferred, `Context<T>` by first `run`) | body solve, possibly another module's body | yes (`let` row) | **yes** | [read]; i7 in the paper |
| 4 | Opaque return's hidden concrete type (a written bare trait is transparent today) | body solve | yes (label prints the concrete type) | **yes** | [ran] importer's message names the hidden impl |
| 5 | `auto T`, fully written | parse | yes (label reads the written `T`, `analyzer.rs:26253-26256`) | no | [read] `auto_annotations.rs:84-122` |
| 6 | Struct fields, enum variants | parse + `types` | yes (label) | no | [read] |
| 7 | Impl headers, which members an impl provides, trait member names, resource-ness | walk | yes (global facts) | no | [read] |
| 8 | Async colour of a function | `async_infer` | yes | **yes** | [ran] moves |
| 9 | Async colour reached through a generic's dispatch, a trait default, a `Drop` body, a returned closure | `async_infer` | yes, on the callee's own row | **yes** | [ran] all four move |
| 10 | Hidden context parameters: WHICH contexts | `context::thread_contexts` | **no: one boolean** | **yes** | [ran] a second read, both contexts run: fingerprint still. [inferred] callers gain a threaded argument (the paper's i2; I compared no JS). With the second context NOT run the fingerprint did move, I do not know through which field |
| 11 | Platform requirement | `platform_color` | yes (the layer, not the chain) | **yes** | [ran] moves |
| 12 | `borrows`, `bumps` verdicts | `infer_borrows`, `infer_bumps` | yes | **yes** | [ran] bumps moves; importer error |
| 13 | C16 retaining summary (does the callee keep the closure it is handed) | `retain_tables.rs`, folded per asked callee | **no** | **yes** | [ran] fingerprint still; NEW ERROR in the importer |
| 14 | R11 move-cleanliness of a generic body per instantiation | `check_resource_generic_instantiations` | **no** | **yes** | [ran] fingerprint still; NEW ERROR at the importer's call |
| 15 | `const` evaluability and value of a callee | `const_eval` | **no** | **yes** | [ran] fuel exhaustion: fingerprint still; NEW ERROR in the importer |
| 16 | `[deprecated]`, `[must_use]` | parse | **no** | no (attribute) | [ran] both: fingerprint still; new warning in the importer |
| 17 | Visibility: `export`, `export *`, `export import` | parse + import stage | **no** | no | [ran] `export` removed: fingerprint still; importer message changes |
| 18 | `[internal]`, `[rpc]`, `[trait_only]`, the platform fence, `has_body` of a trait member, field attributes | parse | **no** [read] `Function` fields `analyzer.rs:1433-1515` against the label | no | [read], not probed |
| 19 | Lazy-argument effects, cell write summaries (`call_reaches_a_write`), drop glue edges | checks, post passes | **no** | **yes** | [read] only; not probed |
| 20 | Positions of the module's declarations (go-to-definition, notes and traces that point into it) | parse | no, by design | **yes** (every edit above them) | [ran] |
| 21 | Doc comments | parse | no | no | [ran] no rendered importer row moved; the server's hover path not read |
| 22 | A module binding's VALUE | - | no | yes | [ran] nothing an importer shows moved |

So rows 10, 13, 14, 15 and 19 are body-level facts that move with the "interface" still:
the dangerous ones. Rows 16 to 18 are not body facts, but a reuse keyed on the fingerprint
would serve them stale too.

**Rows 14 and 15 guard themselves in today's pipeline** [read, inferred]: R11 walks every
instantiation on every analysis and asks a reused module's calls only where they seeded
one (`analyzer-pass-map.md` section 7.3, S7b's note (a)); the const cache is keyed by the
content of everything a site reaches (S4). Neither verdict is stored in a module's record.
**Row 13 does not**: `check_view_escape` is Class A, so its verdict IS in the record.
**Row 12 does not either** [read, inferred]: `infer_bumps` treats table-restored functions
as seeds and rescans only a moved verdict's LIVE callers (`analyzer-pass-map.md` section
3.4), so a cold caller of a function whose verdict moved keeps its old one.

## 5. Whole-program passes: which tolerate a hot set smaller than the import closure

"Tolerates" means: with an importer cold and the module it imports re-walked, the pass
still derives the importer's answer from the current program.

| Pass | Where its cold input comes from | Tolerates | Basis |
|---|---|---|---|
| contexts + call graph | cold graph halves recorded per cold set; the rewrite's cold rows compared with the record before the post-rewrite graph is served (`analyzer.rs:83397-83414`) | yes, if cold call rows name stable callee ids | [read]; the analysis and `apply` run whole-program on every keystroke |
| async inference | cold seed = least fixpoint "with every hot callee unknown" (`:83415-83419`); cold instance record with its reads logged (M138) | yes by design; a DIRECT cold-to-hot call is a kind of read it has never met | [read] design only; `async_infer.rs` uses `cold_entity` at 12 sites I did not audit one by one |
| platform colour | none: a forward walk from `main` per analysis | yes | [read] pass map 7.2 |
| const pass | per-site cache keyed by reach content | yes | [read] |
| dispatch refinement, init order, lifetime steers, module-level cells, view suspensions | recomputed, or decided per analysis from recorded enrolments | yes | [read] pass map 3.6 |
| bound audit | module record, with its own late-impl guard | yes for impls; the callee's BOUNDS must be in the unchanged part | [read] |
| R11 | instance records keyed by callee and types | yes (a re-walked callee is scanned live) | [inferred] |
| held tables, move tables, lazy tables | per-region contributions, decisions over every candidate on every analysis | yes | [read] pass map 7.3 |
| **Class A module records** (14 checks, R10, R12 and moves) | the module's remembered diagnostics | **no**: they bake in the callee's `borrows`, `bumps`, retaining summary, attributes | [ran] rows 12, 13, 16 |
| **`infer_borrows` / `infer_bumps`** | restored rows as seeds | **no** for a cold caller of a moved verdict | [inferred] from the pass map's description |
| class D tables, label rows, hover rows of a cold importer | restored | positions and labels of the imported item are baked in | [inferred] |

So the post passes are mostly ready (they were built for "hot callee unknown"), and the
checks phase's records are not.

---

## 6. The mechanisms I considered, and why each stands or falls

| | Mechanism | Verdict |
|---|---|---|
| A | **As briefed**: re-walk the edited module, fingerprint it, and if equal take the importers from a stored full world | Falls: sections 2 and 3. There is no stored world that holds them, and making one needs retraction (B). |
| B | **Retraction**: store the full resolved world; on an edit remove the old module's rows and re-walk it into pinned windows | Falls for now. Needs (i) a purge of 482 analyzer fields by id range, (ii) pinned windows, (iii) id REUSE, which every id-keyed memo forbids, (iv) proof that no importer row names a body-minted type id. XL, and each part is a census where one missed table is a silent stale answer. |
| C | **Shadow**: keep the old module in the world for importers to point at, walk the new one beside it | Falls: whole-program passes follow importers' calls into the OLD bodies. An alias between the two at about 1,400 id sites. |
| D | **Narrow analysis + frozen importers in the server** (analyse the edited file alone, keep the importers' last diagnostics) | Falls: unsound. A module analysed without its entry's world loses impls it never imports (i3) and types its importers ground. That is what M104 was ruled to fix. |
| E | **Item-grain hot set** from last analysis's recorded read edges | Possible in principle, larger than everything else here, and it does not use the interface at all. Not pursued. |
| F | **Walk importers before the store, resolve them after** (the open-module shape M70 already has) | Sound and small, saves only the walk (+75 ms of 909). Not worth it alone. |
| **G** | **The stub split** (section 7) | Stands, with prerequisites P1 and P2. |

## 7. The design I recommend: the stub split

### 7.1 The idea

A module's top-level items are walked in two phases:

- **phase 1, the stub**: every declaration and everything in it that is not a body:
  imports, exports, attributes, struct and enum shapes, trait and impl headers, every
  function's and method's signature, every module binding's name and written type;
- **phase 2, the bodies**: function, method and trait-default bodies, and binding
  initializers.

For the EDITED module only, phase 1 runs where the module loads today in a world with no
hot set; its importers walk and resolve against it in the pre-store resolve; the world is
stored; phase 2 runs after the store, where `load_hot_modules` runs today. The stored
world is therefore "everything except the edited module's bodies and the entry". Its key
is today's key with the edited module's STUB HASH in place of its content hash.

What this buys, structurally:

- nothing is ever removed from a world, and no id is ever reused: the two invariants
  everything since S1 rests on stand;
- an importer's ids for the edited module's declarations are prefix ids, identical on
  every hit by the same proof M19 uses;
- "interface unchanged" is a hash comparison done before any walk. A half-typed body
  cannot move it.

### 7.2 Eligibility: when the stub IS the interface (level 1, types)

The split is sound only if nothing an importer's RESOLVE reads from the module depends on
a body. So a module is eligible only when, for every item another module can reach
(exported, in an `export *` file, an inherent method of a reachable type, an impl member):

- a function's return is written and holds no bare trait (row 4: a written bare trait is
  transparent today), or is `auto T` fully written (`auto_written_type_id`,
  `auto_annotations.rs:92-99`), or the body is syntactically void (no tail expression and
  no `ret` with a value): that bit is part of the stub hash;
- a module binding's type is written or `auto T` fully written (this removes row 3,
  including the use-inferred and `Context<T>` cases);
- the module defines no macro (S1's existing refusal) and is not the entry.

Anything else, or any doubt: not eligible, and the analysis takes today's closure path
unchanged. `auto` already gives the semantic guarantee this needs: in a clean analysis
too, "everything outside reads `T`" (`auto-annotations.md` section 3), so the clean and
the split analyses agree even while the annotation is stale.

This is `auto` annotations' slice S5, and it is why the mechanism merges the brief's
stages 2 and 3. A module with an inferred visible type keeps today's cost until it is
annotated. A later, optional slice could treat last analysis's inferred types as "virtual
annotations" and compare after the bodies resolve; I do not recommend it now (the clean
analysis has no annotation there, so equivalence would have to be proven case by case).

### 7.3 The decision procedure

```
On an editor analysis of a declared entry, seeded with the edited file E:

 1. H = today's closure of E (hot_set_closure).
    H has no module but E          -> today's path (nothing to gain).
 2. E not eligible (7.2)           -> today's path.
 3. stub = E's text with every body and initializer elided, plus the
    "syntactically void" bit of each unannotated function.
    key = today's key with hot = { bodies of E }, and hash(stub).
 4. Look the split world up under key.
    HIT   -> clone it.
    MISS  -> if this stub was seen on the previous analysis too, or the file
             parses clean: build the split world over S1's stored prefix
             (walk E's stub and the importers, resolve, run S1's guards,
             store), then go on as a hit.
             Otherwise (a stub seen once, mid-typing): today's path, and
             remember the stub. A broken parse must not mint a world.
 5. Walk E's bodies over the clone; walk the entry; build().
 6. Guards, each refusing to today's path and remembering the refusal as
    S1's guards do (refuse_hot_world):
      - S1's use-inferred guard, over E's bodies (a body grounds another
        module's binding);
      - B553's entry-impl guard, unchanged;
      - a body of E wrote a slot of another prefix module: that module is
        dirty (T0, unchanged) and is checked live.
 7. Checks. E is always live. Importers:
      slice A: WARM. Their module records are not served; they are checked
               live. Nothing remembered about them is trusted.
      slice B: COLD if E's effects digest (level 2, 7.4) equals the one
               filed with the world; otherwise warm, as in slice A.
 8. Post passes: as today, cold = prefix minus warm ranges. E's
    declarations are in a warm range, so every graph and seed re-derives
    its nodes.

Whenever the comparison cannot be made (no stored stub, a parse that does
not recover the item structure, an unknown item kind): today's path.
```

Widening is always to the FULL closure, never to "the importers that read what moved". I
chose that because the read edges an importer has on the edited module are not all
explicit (row 9: a scope end that drops a type, a dispatch through a bound), and a wrong
narrow set is a stale diagnostic.

### 7.4 Level 2, effects (slice B only)

A cold importer's record bakes in body-level facts of what it calls (section 4, rows 12
and 13, and row 19 unverified). Slice B files, with the split world, a digest of those
facts for every function of E, recomputes it after `infer_borrows` / `infer_bumps` and
the retain fold on each keystroke, and serves importers' records only when it is equal.
The list of facts must come from an audit of the 14 Class A checks, R10, R12, the move
scan and the class D tables, not from my probes: I found three by probe and reading, and
I have not done that audit. Until it is done, slice A (importers warm) is the only
version I would call sound.

### 7.5 Prerequisite P1: the split walk

[read] `walk_func_entity` (`analyzer.rs:44438` onward) walks the signature and then the
body in one call; the walker's dynamic state at that point is small
(`return_type_stack`, `current_source_id`, `current_impl_subject_name`, three `walking_*`
flags, the scope stack, the window being laid out). Phase 1 must insert the `Function` row
with a placeholder body, phase 2 must restore that state per body and patch the row.
[inferred] Feasible because "the walk itself does no name resolution"
(`analyzer-pass-map.md` section 3.1; I did not verify that sentence in code).
Not yet known: which pre-store code reads a function's body (it would now meet a
placeholder), and how generated (`[derive]`) items of the edited module split.

### 7.6 Prerequisite P2: positions

The stored world holds the stub's byte offsets as of the keystroke that built it, and a
body edit shifts every declaration below it. That violates the pass map's rule "a stored
world may hold only what its key determines" (section 5.5) unless handled. [read] by a
grep of the struct, 42 of the analyzer's 482 fields carry a `Span` directly (`span_map` holds `&'src Span` into the
old parse tree), and entity rows carry more (`name_span`). Two ways, both a census:

- (a) shift every span-bearing row of the edited source on the clone, by a per-item
  delta (S7 does exactly this for its records, `item_records.rs:60-181`);
- (b) give the stub its own source whose text is the stub (byte-identical across body
  edits) and translate to file coordinates where results leave the analyzer.

I lean to (b) because nothing inside the analysis then sees two coordinate systems, but
I have not read the server's per-document tables closely enough to cost it. This is the
part I am least sure of, and it is the part most likely to produce a wrong position
rather than a wrong diagnostic.

### 7.7 Cache keys and memory

- **One stored world still serves edits to ONE file.** Each edited file has its own
  split world (everything minus ITS bodies), as each has its own hot-set world today. So
  the file-switch miss (7.5 to 17 G) is NOT removed by this design. A design that removed
  it would keep one full world and retract the edited module's bodies from it: that is
  mechanism B's purge, restricted to bodies, and it is a later arc. I say so plainly
  because the brief asked.
- **Memory.** A split world is a full Kolt world, about 150 MiB, against a smaller
  hot-set prefix today (the world minus 46 modules). If the S1 prefix is also kept, as
  step 4's cheap rebuild wants, that is one more world per actively edited file. The
  cache already holds 3 to 5 worlds against a 192 MiB budget
  (`BASE_CACHE_RESIDENT_BUDGET`, `analyzer.rs:83744`); this design makes M140 more
  urgent, not less. I would build the split world without retaining the S1 prefix for
  it and accept a full rebuild on a stub change, then measure.
- **A stub change costs a miss.** A signature edit or a new item today costs a 21 G hit;
  under the split it costs a world build (about 29 G, the first-keystroke figure) unless
  step 4's rebuild over the S1 prefix is kept. Step 4's "seen twice" rule is there so
  that mid-typing garbage does not pay it.

### 7.8 The cold path and resident memory

- A cold `vilan check` / `vilan build` names no hot seed, so step 1 never runs and no
  world is split. What the cold path would newly execute is one branch per top-level
  item in the walk ("defer this body?"). I expect that to be unmeasurable against the
  0.5% gate; I have not measured it, and stage 2 must (the callgrind ci rows).
- Nothing in this design computes a fingerprint on the served path either: level 1 is a
  hash of text the parse already holds.

---

## 8. How the gates would exercise it, and the plants

Fixtures (the 22 valid probe edits are written and can become `Edit`s in
`replay_harness/packages.rs`), each in two forms, "moves" and "does not move", each with
a body edit ABOVE the item so positions shift:

written return changed; `auto T` gone stale (callers must keep reading `T`); impl added /
removed in the edited module; `export` removed; `[deprecated]` / `[must_use]` added; async
colour (direct, through a generic's dispatch, through a trait default, through `Drop`,
through a returned closure); context read added, replaced, a second one; platform
requirement; `bumps`; `borrows`; retaining summary; R11; `const` callee (value, fuel);
opaque return's hidden type (must be INELIGIBLE); inferred return and inferred binding
(must be INELIGIBLE); item added, removed, reordered; a parse break inside a body; a
body edit inside an import cycle; a body that pushes into another module's binding.

| Plant | The bug | Must turn red on |
|---|---|---|
| `StubAlwaysEqual` | the stub comparison always says unchanged | written return, impl, `export`, attributes |
| `StubOmitsAttributes` | attributes left out of the stub hash | `[deprecated]`, `[must_use]` |
| `SplitServesIneligible` | eligibility always true | inferred return, inferred binding, opaque return |
| `StubSpansUnshifted` | P2 skipped | every "edit above the item" fixture (positions) |
| `EffectsGateOff` (slice B) | the effects digest always equal | `bumps`, `borrows`, retaining summary |
| `EffectsDigestWithoutRetain` (slice B) | one fact left out | retaining summary |
| `SplitBodiesReplayed` | E's own record served | any edit in E |
| `SplitUseInferredGuardOff` | step 6's first guard dropped | the push into another module's binding |

The edit-replay differential compares the split analysis with a clean one on every
fixture, edit and undo; the permutation differential runs the same fixtures under
reversed names and deeper nesting (the split changes WHEN a module's bodies walk, which
is exactly what it watches); `check_scope_differential` and `replay_differential` cover
the records of warm and cold importers; `prefix_roundtrip_differential` is untouched
unless the split world is persisted. `VILAN_INCREMENTAL=verify` on both exhibits' recorded
sessions is the dogfooding gate, and on Kolt it only says something after the opt-in.

One limit to state now: the observation the differentials compare does not render the
context rewrite, the async set or const results (pass map section 6, "tables it does not
render"). Row 10 (which contexts) is visible only in emitted JS. The differential's JS
leg covers it for clean programs; the fixtures for it must be clean programs.

## 9. What can be had without the prerequisites (not importer reuse)

From the per-pass table, three costs are paid for hot importers and need not be:

| Cost | ms of the 909 gap | Why it is paid | What would remove it |
|---|---:|---|---|
| bound audit at module grain | 177 | a re-walked file's sites are all live (S7 left it so: the question names a type id of another window) | serve a hot ITEM's sites when its record is served |
| `compute_clone_sites` | 94 | not read; it is 14 ms on the leaf | to be diagnosed |
| item-record decision | 63 | the signature of 1,802 items computed per keystroke | cheaper validator, or skip items whose dependencies' text is unchanged |

About 335 ms, perhaps 3.5 G of the 10 G gap, under the existing differentials and with
no new world shape. I measured the costs; I did not diagnose the second or build any.

## 10. Estimated saving per scenario

Instructions, kolt-now, entry open. "Today" is measured; the rest are estimates from the
profile (the leaf row is the floor: its hot set is the edited module and the entry).

| Scenario | Today | Slice A (importers warm) | Slice B (importers cold) | Section 9 alone |
|---|---:|---:|---:|---:|
| theme / model / styles body keystroke, module ELIGIBLE (after Kolt's opt-in) | 20.9 to 22.6 G | about 16 to 17.5 G (saves walk, resolve, item-record decision: about 420 of 909 ms) | about 11 to 12.5 G | about 17.5 to 19 G |
| the same, module NOT eligible (today's Kolt, by a rough grep of the exhibit: theme has 2 unannotated module bindings and 3 of 5 functions with no written return, styles 18 bindings, model 9 of 146 functions, channel 17 of 30; some of those functions may be void) | 20.9 to 22.6 G | unchanged | unchanged | about 17.5 to 19 G |
| a keystroke that moves an effect (slice B) | - | - | slice A's figure for that keystroke | - |
| a signature edit, a new item | about 21 G | about 21 G with the S1 prefix kept, about 29 G without | same | unchanged |
| the leaf | 10.9 to 12.0 G | unchanged | unchanged | unchanged |
| a file switch (first keystroke) | 29 to 30 G | unchanged | unchanged | unchanged |
| model's 4 of 10 keystrokes that moved `Channel::create`'s inferred return | 20.9 to 22.1 G | eligible only once it is annotated; then as row 1 | | |

Confidence: high that the gap is what the table in section 1 says; medium on slice A's
split of it; low on slice B until the effects audit exists.

## 11. What I could not verify

1. That the walk does no name resolution, so a body can be walked later (pass map
   section 3.1; not checked in code).
2. Which pre-store code reads a function body and would meet phase 1's placeholder.
3. How generated (`[derive]`, `[service]`) items of the edited module split.
4. That every post pass tolerates a DIRECT call from a cold node to a re-walked one
   (section 5 is from the design comments and `call_graph.rs`; `async_infer.rs` and
   `context.rs` not audited site by site).
5. The complete list of body-level facts a Class A or class D record bakes in (three
   found; the audit is not done). Row 19 is read, not probed.
6. Which of P2's two forms is cheaper, and the server's per-document tables for a
   module whose declarations are prefix ids and whose bodies are not.
7. That every reader of an `auto` item reads the written type. I found five sites
   (`analyzer.rs:26255`, `:51245`, `:51532`, `:62443`, `:62674`); method calls through an
   impl and static accessors not traced.
8. How many of Kolt's modules are eligible after the opt-in. The 315 figure is lsp-58's;
   I did not run `check --fix` on a copy.
9. The cold path's cost of the walk's new branch.
10. The context-set probe compared the rendered observation only, not emitted JS.
11. Whether a split world can be built over S1's stored prefix the way P2 layers a world
    over the std prefix (it looks like the same shape; not tried).
12. Nothing here was measured on the old exhibit (`order58b/kolt`).

## 12. Prerequisites and recommendation

**Prerequisites for sound importer reuse**: P1 (split walk), P2 (positions), and for the
second half P3 (the effects audit and digest). None exists.

**Recommendation: do not proceed to stage 2 as designed.** A fingerprint comparison in
front of today's world shape would have nothing to reuse, and a fingerprint-gated record
replay would be unsound on at least rows 13 and 16 to 18. Instead, in this order:

1. **A spike of the stub split** (P1 and P2 only, slice A, behind a switch, never
   committed to `next`), in the manner of the S5 spike: yes or no on (i) the split walk
   byte-identical on the corpus and the native differential with the split forced for
   every module, (ii) positions correct on the "edit above the item" fixtures, (iii) the
   edit-replay and permutation differentials green with the plants above red, (iv) a
   measured row on a COPY of kolt-now with the opt-in applied. If (i) or (ii) fails, the
   red cases are the design input, as they were for S5.
2. **In parallel or first, section 9**: about a third of the gap, no new mechanism,
   helps every module including the ones that will never be annotated.
3. **Slice B only after the effects audit**, with one plant per fact.
4. **The file switch** (M140) stays its own lever; this design does not help it and
   raises the cache's pressure.

The owner's decisions this needs: whether importer reuse may depend on `auto`
annotations (I think it must, and the paper already ruled it would for the pre-walk
decision); whether Kolt's opt-in is acceptable as the price; and whether section 9 is
wanted first.
