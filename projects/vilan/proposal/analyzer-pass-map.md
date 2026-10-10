# The analyzer pass map — every pass, what it reads and writes, what order it needs, what it costs on kolt, and which S2/S3 table it becomes (M110)

> Status: **PAPER, drafted 2026-10-08** for the owner to rule on (Q1–Q9).
> Written by lane papers-a-48 of Order 48, the prerequisite the owner ruled for
> Order 49's S2 and S3 and for the S5 spike (M110, ruled 2026-10-05). Nothing in
> the compiler, kolt or the website changed. Source is cited at `next`
> @e75bc57c (the v0.45.0 fold), read in the worktree
> `vilan/.claude/worktrees/papers-a-48`; `analyzer.rs:N` is a line of that tree.
>
> Every number is measured here, on 2026-10-08, against a scratch copy of the
> owner's kolt working tree (the uncommitted store-exhibits patch included):
>
> - **instructions:** `scripts/perf_count.py` (hardware `instructions:u`) on a
>   release build; `callgrind` Ir on the `profiling` build for the functions
>   that survive inlining;
> - **per-pass CPU:** `VILAN_PHASE_TIMING=passes VILAN_COUNTERS=1 vilan check`,
>   the median of five runs (load average 17–21, so CPU is read as SHARES and
>   converted to instructions only as an estimate, marked "≈");
> - **the editor:** `scripts/lsp-latency.py --source <copy>` on a release
>   `vilan-lsp`, scenarios "leaf keystroke, world mode" (a `views.vl` keystroke
>   served by M110 S1's hot-set world) and "model.vl keystroke, importers open"
>   (refused by S1's impl guard), three runs each, with the server's own
>   `[vilan pass]` lines; the medians are over six analyses of each kind.
>
> Probes, repros and scripts: `scripts/integration/sweeps/order48/papers-a-48/`
> (`finds/` holds the repros of §5 and §9; `finds/lspprobe.py` drives
> `vilan-lsp` over stdio). The raw phase logs are in the worktree's
> `target/papers-a-48-scratch/`.
>
> Related: M110 and `incremental-analysis.md` (§1 the pipeline, §3.2 door B,
> §5/§11 the slices), M121 (door (b), incr-48 this order), M19 and
> `per-module-analysis-reuse.md` (the Class A/B/C/D windows), M99, M101 (the
> post passes), M122 (broken keystrokes), M123 (the bound audit), B553, B554,
> B560/B561/E267, B547, B573, `const-eval.md` §8.4 (E35's one call graph),
> `method-resolution.md` §2 (the id order as the declaration order).

## 0. The answer up front

**The analysis runs in six phases, and every one covers the whole entry
world:** the loader's drain (a load ⇄ macro-expansion fixpoint), the module
walk, the pre-entry `resolve_world` (the "base", the stored world), the entry
(and hot set) walk with `build()`, about fifty checks and the extraction tail
in `analyze_over_world`, and the twenty-odd whole-program
`post_analysis_passes`. The front ends add their own tail: the CLI's emission,
the editor's tables. §2 splits the phases into eleven stages; §3 is the table,
pass by pass, with inputs, outputs, mutations, order dependence, cost and the
S2/S3 role.

**Where kolt's cost is** (§4). A `vilan check` of kolt is 18.93 G
instructions over two legs. The pre-entry `resolve_world` is 17.6% of the CPU
(its constraint fixpoint 15.5%), the checks phase 33.4%, the post passes 28.1%
(the const pass alone 14.7%; callgrind puts it at 22.1% of instructions), the
load and walk 12.7%, emission 5.9%. A keystroke the editor SERVES from a
hot-set world (`views.vl`) is 9.97 G; its analysis is 1,510 ms of CPU, and
four passes are 61% of it: the const pass (450 ms; S4, incr-48, this order),
the bound audit `check_generic_bound_satisfaction` (203 ms), the context pass
with its call graph (154 ms) and async inference (112 ms). A keystroke S1
refuses (`model.vl`) is 14.11 G and pays the whole world.

**Most order dependence is data flow, and it is already pinned by
construction**: the passes that must run after the fixpoint, after the
async set, after the context rewrite, after the tree is final. Those are
listed per pass in §3 and are not to be deleted. **The ones to delete are
the special cases** (§5), where an answer depends on the ORDER of loading
rather than on the program: B553 (the entry's impl and first `run` arrive
after the modules committed), B554 (blame by file name), the top-level-only
walks (B560/E267 closed, B561 open), the macro-reference order (fixed in S1;
its fallback still picks by load order) and B547's marker deferral, B573
(module twins selected before the platform is set) and its diagnostic sibling
(B?2, found here), the first-match sites over load-ordered tables (M?5,
found here), and one this paper found by mapping the Class A window: **a
module's E3 view-across-suspension errors disappear from the editor on every
reusing analysis** (B?1, a Class A check feeds a post pass through a side table
the record does not carry). Each gets the invariant that replaces it.

**What the edit-replay differential proves** (§6): that an incremental analysis
answers what a clean one does, for the observation it renders and the edits
its corpus makes. It cannot prove that the clean analysis is itself
independent of load order: B553, B554, B573 and B?2 are present in both of its
legs. A **permutation differential** (the same package under reversed file
names) is the missing gate.

**For Order 49** (§7, §10). S2's first table should be the bound audit at
prefix call sites (the largest check left on a served keystroke, 13.5%), keyed
through M123's memo. S3 needs **no pass reorder**; it needs the two tree
rewrites of the post-pass region (the context pass's, and `[track_caller]`'s
hidden locations) recast as tables, its seeds computed over the prefix ALONE,
and the two analyze-time effect fixpoints (`infer_borrows`, `infer_bumps`,
104 ms on the client leg) added to its list. The S5 spike must assert window
containment, unchanged positional answers (four ruled tie-breaks and the
M?5 sites), no `TypeId` shared across items (post-settle mints included), and
a green permutation differential.

## 1. Method, and what each number is

| what | instrument | figure |
|---|---|---|
| `vilan check` of kolt, instructions | `perf_count.py`, release @e75bc57c | **18.93 G**, CPU 3.675 s, peak RSS 325.7 MB |
| the same, under callgrind | `profiling` build | 17.74 G Ir (the dynamic loader and the build differ) |
| the same with one error added to `views.vl` | `perf_count.py` | **14.53 G (−23.2%)**, CPU 3.106 s |
| per-pass CPU | `VILAN_PHASE_TIMING=passes`, median of 5 | two legs: **server** (node: 58 sources, 147 functions checked) and **client** (browser: 89 sources, 2,206 functions checked); 3,631 ms CPU in all |
| editor, served keystroke | `lsp-latency.py`, `leaf keystroke, world mode` | **9.97 G** to idle, 1,770 ms CPU to diagnostics; `reused 87/88`, `sources-walked=2`, `functions-checked=138` |
| editor, refused keystroke | `model.vl keystroke, importers open` | **14.11 G**, 2,800 ms; `hot-refusal impl`, `sources-walked=89` |

The per-pass split prints a pass only when it cost at least 1 ms or minted
1,000 type slots (`lib.rs:1645`), so a pass missing from a table below cost
less than a millisecond on both legs. The "≈ G" column is the pass's CPU share
of the 3,631 ms times 18.93 G. Where callgrind can see the function (it was not
inlined into its driver), its Ir is given instead and is exact. The two
disagree most on the const pass, whose interpreter retires more instructions
per millisecond than the solver does (2.79 G by share, 3.92 G by callgrind).

`--explain-cost` attributes the SOLVER's work to declarations (attempts,
inferences, selections, slots, impl rows): 508,113 work units on the client leg,
the top being `sidebar_shell` (9,287), `create_search_modal` (8,067) and
two generated `lucide_lookup_*` functions (5,602 and 5,287). It is the right
instrument for S5–S7's per-item questions. It does not split by pass, so the
pass costs below come from the phase split.

## 2. The pipeline at a glance

In order, for one analysis of one entry. "World" means everything loaded
for the entry; "prefix" is S1's stored world (the world minus the hot set).

| # | stage | driver, site | scope | kolt CPU (server / client ms) |
|---|---|---|---|---:|
| 1 | parse the entry, desugar (`css`, elements, lift), infer the platform | `lib.rs:835` `analyze_source_unfenced` (the CLI parses in `main.rs`) | entry | small |
| 2 | the base-cache key, the hot set, lookup | `analyzer.rs:72921` `analyze_inner` | — | — |
| 3 | **the drain**: load every reachable module (canonical min-heap order), register macros once, expand, re-seed loads until none are left | `analyzer.rs:73802`–`74640` | world (hot set deferred) | load+walk 150 / 313 |
| 4 | entry-cycle refusals, prelude exports and seeds, **the module walk** (twins, declarations, queued work), std's and dependencies' `lib.vl`, the lang-item ids | `analyzer.rs:74641`–`75299` | world | (in load+walk) |
| 5 | **`resolve_world`, pre-entry** ("base"): ten stages, the constraint fixpoint last | `analyzer.rs:75303` → `59275` | prefix | base 146 / 494 |
| 6 | S1's use-inferred guard, the store, `load_hot_modules`, `expand_entry_over_world` | `analyzer.rs:75314`–`75486` | hot set, entry | — |
| 7 | `analyze_over_world`: configuration, **the entry walk**, `build()` = `resolve_world` again + `finalize_build` | `analyzer.rs:75553`–`75715` | entry + hot set | build 12 / 28 |
| 8 | reuse setup (M19), the two effect fixpoints, the checks (Class A window, Class B/C, R10–R12, records, coherence) | `analyzer.rs:75717`–`76146` | world (Class A: non-reused) | checks 272 / 939 |
| 9 | the extraction tail: intrinsics, the view-assignment rewrite, liveness, copy and clone plans, resource types, the editor's labels, the `Program` | `analyzer.rs:76148`–`77390` | world | (in checks) |
| 10 | `post_analysis_passes`: admission, labels, platforms, **contexts + the call graph**, `[track_caller]`, **async**, the effect checks, **platform colour**, **the const pass**, contract hashes, init order, the fingerprints | `lib.rs:1119`–`1351` | whole program | post-passes 111 / 911 |
| 11 | front-end tails: CLI emission (`diagnose` / `transform` / `transform_split` / `vilan_rust::emit`), CLI-only `refuse_release_dbg` and `const_eval::infer`; the editor's tables and further legs | `main.rs:7029`–`7380`; `document.rs:1993`–`2345` | whole program | emission 42 / 172 |

Two facts about this shape matter for everything below.

1. **`resolve_world` runs twice per analysis** (`analyzer.rs:75303` and, through
   `build()`, `:75679`). The first resolves everything the modules queued; the
   second resolves what the entry and the hot set queued, over the first's
   settled answers. This two-phase shape is not an S1 artefact: every analysis
   has it, cached or not, CLI or editor. It is what makes the base cache
   possible, and it is the root of B553.
2. **The analyzer's configuration is not fixed when the first pass runs.**
   `Analyzer::new()` (`analyzer.rs:7022`) takes no arguments; `platform`,
   `platform_reason` and `prelude_repair` are assigned in `analyze_over_world`
   (`:75598`–`:75604`), after stages 3–6 have read them (`source_paths` is
   assigned before the base resolve too, `:75302`, so it is not late).
   That is B573 and B?2.

## 3. The pass table

Columns: **reads** (the inputs that matter for invalidation), **writes**
(the analyzer or `Program` fields it fills or mutates; "diag" = diagnostics
and warnings), **order** (what it must follow, what must follow it, which
fixpoint it is or joins; ⚠ marks a dependence on load order rather than on
data), **cost** (median CPU ms, server / client leg; ≈ G or callgrind Ir),
**S-role** (what Order 49 makes of it: S1 = handled by the hot-set world
already, S2 = a prefix table, S3 = a seeded fixpoint, S4 = the const cache,
— = stays per analysis).

The writes column comes from reading each function and from a static census
(`papers-a-48/tools/writes.py`): every `self.<field>` the function or its
callees (five levels) assign or extend. It over-approximates the callees'
writes, and it can miss a write made through a local borrow, so every row was
also read.

### 3.1 Stage 3–4: the drain and the walk (`analyze_inner`)

| pass | site | reads | writes | order | cost | S-role |
|---|---|---|---|---|---|---|
| key + hot set | `:72979`–`:73192` (`hot_set_closure` `:72611`) | entry text's `std::`/`pkg::`/dependency paths, workspace, hot seeds | `BaseCacheKey`, `HotSet`, the census | syntactic, before any load; the hot set is the reverse import closure of the seed, closed over cycles | small | S1 |
| base-cache lookup | `base_cache_admit` | key, every loaded file's hash | (a cloned world on a hit) | a hit skips stages 3–5 entirely | clone (M115's cost, unmeasured) | S1 |
| **the drain** | `:73802`–`:74640` | `read_source` (overlays first), the parse cache, std and package roots | `modules`, `scopes`, `module_id_by_name`, `packages`, `sources`, `source_hashes`, module entity ids, parse diagnostics | a min-heap on `load_order_key` (WO-1b, M107): load order is a pure function of the reachable set, independent of import order; hot modules are held back (S1); ⚠ every later id is minted in this order | parse of module files 0.86 G Ir (both legs, cached across legs) | S1 |
| macro registration | `:74432` | every file loaded at the FIRST settle (entry, modules, dependency libs) | the `MacroRegistry` | built once, `get_or_insert_with`: "macro definitions must be reachable WITHOUT expansion" (`:73741`); a module reached only through generated code registers nothing, by that rule | `register_file` 0.03 G Ir | S1 (guard: a hot module defining a macro is refused) |
| macro expansion | `:74503`–`:74636` | each not-yet-expanded file, its macro scope, M33's content-keyed table | `generated_by_source`, `macro_item_invocations`, `macro_failed_sites`, `macro_expression_expansions`, new load requests | a fixpoint with the drain: generated `import`s re-enter `to_load`; the entry is pre-marked expanded when cacheable (the §6.13 hoist) | `expand_source` 0.06 G Ir | S1; M33 already content-keyed |
| entry-cycle refusals | `:74671`–`:74741` | declared entries, every package module's `pkg::` imports | diag, `entry_cycle_refused_imports` | after the drain, before the walk | small | — |
| prelude exports + seeds | `:74743`–`:74813` | each loaded tree's importables, each origin's prelude | `prelude_exports`, `prelude_seeds` | before the walk; consumed by `seed_preludes` in stage 5 | small | S1 |
| **twin selection** | `:74821` → `select_platform_twins` `:48150` | the module's `[platform(..)]` items, **`self.platform`** | `fenced_out_names`, the fenced-out item set | ⚠ **reads `platform` before `:75598` assigns it** (B573: every module's twins chosen for node) | small | S1 |
| **the module walk** | `:74816`–`:74880` → `walk_expr_nodes` `:36361` | each module tree in load order | entities, scopes, spans, `source_ranges`, type slots (minted), `implementations` (one row per impl block, pushed in walk order), every `prepped_*` queue, `pending_macro_references`, `macro_name_to_id` | ⚠ ids and walk-minted type ids follow load order, and that order is SEMANTIC in four places (§5.6); the walk itself does no name resolution (no scope lookup in any `walk_*` body except `Self` in the local type scope): names are queued for stage 5 | `walk_expr_nodes` 0.11 G Ir | S1 (S5 windows its ids) |
| generated walks | `walk_generated_expansion` `:24365` | `generated_by_source` | as the walk | after each file's own walk | (in the walk) | S1 |
| std and dependency `lib.vl` | `:74845`–`:74880` | std's root `lib.vl`, each dependency's | as the walk | after the modules (std's root walks last of std, by design) | small | S1 |
| lang items | `:74883`–`:75298` | std module scopes by name (`io`, `option`, `operators`, `drop`, `tuple`, `web::dev`, …) | `panic_fn_id`, `option_enum_id`, `try_trait_id`, `primitive_struct_ids`, `promise_struct_id`, … (about forty) | after the std walk, before stage 5; std is always in the prefix, so never invalidated by a package edit | small | S1 |

### 3.2 Stage 5: `resolve_world` (`analyzer.rs:59275`), ten stages

Run once pre-entry (the "base") and again in `build()`. CPU is the client leg's
median, base / build; the server leg is about a quarter of it.

| stage (phase-line name) | what | reads | writes | order | cost | S-role |
|---|---|---|---|---|---|---|
| (top) | `resolve_macro_references` `:47280` | `pending_macro_references` | `type_references` | M110 S1 moved it here from the walk: it used to depend on whether the macro's module had walked yet; ⚠ its fallback is a first match over `modules` in load order (§5.6) | small | — |
| `imports` | the import fixpoint: retry until a pass binds nothing, then a REPORTING pass | `prepped_imports`, scopes | bindings, `import_targets`, `import_reaches`, aliases, diag | a fixpoint (re-exports chain); B547: a macro MARKER binds only on the reporting pass, so an item re-exported later wins the collision | 0.9 / 0.0 | S1 |
| `preludes` | `seed_preludes` | `prelude_seeds`, settled imports | scope bindings (yielding to explicit imports) | after every import, before any name resolves (nothing may have memoized a lookup the prelude changes) | 0.1 / 0.0 | S1 |
| `use-drain` | `use` statements | `prepped_uses` | scope bindings | after preludes | 0.0 / 0.0 | S1 |
| `binder-bounds` | binder-bound inheritance (an `impl Wrapper<type T>` walked before its struct's bound) | `prepped_binder_inheritance` | `generic_bounds` links | after every declaration exists | small | S1 |
| `locals` | the desugar-minted std items (B270), then the first part of the bare-name locals | `prepped_std_items`, `prepped_locals` | resolved names, constraints | locals a guard clause may publish WAIT (B222) for the divergence stage | 14.6 / 0.0 (was timed as `binder-bounds`; N153) | S1 |
| `assignments` | the assignment drain (`wire_prepped_assignment`); guarded assignments wait like guarded locals | `prepped_assignments` | assignment wiring | after the first-part locals | 0.6 / 0.0 (was `locals`; N153) | S1 |
| `types` | written type annotations, static accessors, `dyn` annotations, existential grounding, the impl subjects and trait lists of the `implementations` rows the walk pushed (`walk_impl_entity`, `:38989`) | `prepped_type_locals`, `prepped_type_static_accessors`, `prepped_trait_impls`, scopes | type slots, impl subjects (⚠ the rows are in walk order) | before the context clauses and conformance | 27.1 / 0.4 | S1 |
| `context-clauses` | `resolve_context_clauses` (B242/E262) | context clauses on parameters and members | the clause on each type | after the import fixpoint, before conformance (a clause is part of a parameter's type) and before the fixpoint | (was inside `conformance`; N153) | S1 |
| `conformance` | trait-impl conformance | `prepped_trait_impls` | diag | after the clauses | 3.2 / 0.0 | S1 |
| `divergence+guards` | `compute_divergence_leaves`, guard continuations, the waiting locals and assignments | the call subjects resolved so far | `divergence_leaves`, `guard_continuation_captures` | the B222 two-part drain: a name a guard may publish resolves only after this | 4.0 / 4.1 | S1 |
| `admission` | `build_lookup_admission` (B401) | import rows, selector subjects | `LookupAdmission` | after the import and type drains, before the first lookup; rebuilt per resolve because the entry's statements arrive between the two | 2.3 / 2.3 (was `contexts`; N153) | S1 |
| `fixpoint` | `resolve_constraints` + `wake_ready_constraints` + backstops (literal-let expectations, let-bound closures from call sites, one stall pass) | every queued constraint | type slots IN PLACE, resolutions, `generic_dispatch`, `function_calls`, member resolutions, diag | the global inference fixpoint; monotone, dependency-driven; ⚠ a constraint that fails here is REPORTED here, so a module's failed member lookup commits before the entry's impls exist (B553) | **436 / 1.5**; `resolve_constraints` 2.84 G Ir | S1 (prefix); S5–S7 make it per item |

### 3.3 Stages 6–7: the hot set, the entry and `build()`

| pass | site | reads | writes | order | cost | S-role |
|---|---|---|---|---|---|---|
| S1 use-inferred guard | `:75314` | prefix modules' element slots and non-ground types | the refusal | after the base resolve, before the store, so a refused world is never stored | small | S1 |
| base-cache store | `base_cache_store` `:75441` | the world | a cloned world in the cache | after the guard | clone (unmeasured, M115) | S1 |
| `load_hot_modules` | `:71851` | the hot set's files | as the drain + walk, for the hot set only; calls `select_platform_twins` (⚠ B573 again, `:72104`) | after the store, on hit and miss alike | sources-walked 2 on `views.vl` | S1 |
| `expand_entry_over_world` | `:71726` | the entry, the stored registry | entry expansions; the gensym counter continues from the prefix's | after the store, identically on hit and miss (§6.13) | small | S1 |
| configuration | `analyze_over_world` `:75598`–`:75604` | the workspace | `platform_reason`, `prelude_repair` (and `source_paths`, `reuse_prefix_len`); `platform` is set at construction since B573 | the two unkeyed facts are rendered only at PUBLISH (`render_publish_marks`, where the lists leave the analyzer; B576, Order 49): a diagnostic the pre-entry resolve produces carries a mark, never the fact | — | — |
| the entry walk | `:75618`–`:75671` | the entry tree, its prelude | as the module walk; `seed_preludes` for the entry scope | after the configuration (so the entry's twins are right) | small | — (always walked) |
| `build()` = `resolve_world` + `finalize_build` | `:58821`, `:61791` | the entry's and hot set's queues, the settled prefix | as stage 5; then for-in protocol, operator overloading, binder-bound inheritance, unary operands, integer literal ranges, negative unsigned constants, resource erasures, bare payload variants, starved closure parameters, post-solve diagnostics | `finalize_build` reads the settled types; the second resolve sees only what was queued since the first | build 12 / 28; `finalize_build` 0.16 G Ir | — |
| `types_settled = true` | `:75715` | | the late-write counter arms | every slot write after this is a late write (M108: 0 on kolt) | — | — |

### 3.4 Stage 8: reuse setup, effect fixpoints and the checks

Class A (M19 T1): routed through `reusable_entity`, skipped for a reused module,
diagnostics replayed from its record. Class B (coherence) and C
(instantiation-driven) run over every module on every analysis. The served
column is the median CPU of a `views.vl` keystroke the editor served from the
hot-set world (§4.2).

| pass | site | reads | writes | order | cost (server / client; served) | S-role |
|---|---|---|---|---|---|---|
| reuse candidates, record lookup, seal ranges, replay | `:75717`–`:75801` | `entry_dirty_sources`, alias census, the checks record | the frozen/world/table ranges, replayed diag | before every check that can add a diagnostic | small | (M19 itself) |
| `infer_borrows` | `:25725` | bodies, the call graph of resolved calls | `Function.borrows` | "before any check reads it" (readonly-mutation, scalar views); a monotone call-graph fixpoint (the sixth inferred-effect worklist) | <1 / 3.0; 2.5 | **S3** (M?4) |
| the `bumps` native table | `:75810`–`:75891` | std container impls | `bumps_tabled`, `Function.bumps` | seeds `infer_bumps` | small | S3 seed |
| `infer_bumps` | `:25971` | bodies, tabled verdicts | `Function.bumps`, `External.bumps` | the seventh worklist: callee → caller, a dispatched callee counts as bumping; before `check_invalidation` (E2 keys off it) | **16.2 / 100.8; 43.6** | **S3** (M?4) |
| wrapped view captures, mut captures under view subjects, entry `main` parameters | `:75900`–`:75907` | settled types | `wrapped_view_captures`; diag | before the checks that consult them | small | S2 |
| lazy bindings and arguments | `record_lazy_bindings`, `record_lazy_arguments` | call sites, parameters | `lazy_*` tables | OUTSIDE the Class A window on purpose (lowering input), before rule 3's capture ban and R9 | 1.4 / 7.9; 5.7 | S2 |
| `classify_dbg_calls` | `:75918` | `dbg` calls | `dbg_statement_calls`, `dbg_argument_types` | before the ownership checks and both emitters | small | S2 |
| `mark_dbg_stack_modules_unrecordable` (debug-49, Order 49) | `analyzer/dbg_stack.rs` | `dbg_stack_calls` | `reuse_unrecordable` | before the Class A windows: a module holding a `dbg_stack()` call is never recorded, so the two per-site records below (E281, E282) re-derive on every analysis (B575's rule, by recompute) | nil without a `dbg_stack()` call | — |
| **Class A**: assignment places, readonly mutation, mutable arguments, lazy arguments, mutable references, view bindings, view arguments, view value reads, must-use, deprecated, element attribute shadowing, view escape, **`check_invalidation`**, reseat escape | `:75949`–`:75963` | settled types, bodies | diag; `check_invalidation` writes **`view_suspension_checks`** for a post pass (recorded per module and replayed for a reused body since B575, Order 49); `check_lazy_arguments` writes `lazy_argument_resource_refusals` (read by R9, which skips the same bodies); `check_invalidation` writes **`dbg_stack_invalidated`** (E282, debug-49: the capture views a `dbg_stack()` call may not read) for the expansion, never for a reused body — its module is unrecordable | after the effect fixpoints; the rule (Q6, RULED): a windowed check that writes a table a later pass reads records it or computes it for every body | client total ≈ 70; served ≈ 25 (the window works) | S1/M19 already |
| Class B/C: Wire, JSON, Hashable, PartialEq boundaries, `[rpc]` signatures, `expose` fields, `[hint]` attributes | `:75966`–`:75974` | settled types, the impl table | diag, `rpc_refused_*`, `expose_refused_*` | after every name resolves and every impl's provided set is closed | small | S2 |
| **`check_generic_bound_satisfaction`** | `:8004` | every call site's settled instantiation, the impl table, blanket proofs | diag; mints type slots (+1,242 client; none for a reused module's sites since S2a) | Class A window of its own since M110 S2a (Order 49): a reused module's sites are skipped and their refusals replayed from M19's record, which also carries the module's QUESTIONS (call, constraint, trait); a module one of whose questions a late impl (past the reach log's floor) answers is re-audited instead — the audit asks after the store, so M121's verdict never sees its questions; the three declaration walks stay Class C; runs after the coherence checks it reads | **36.0 / 224.6; 203.2**; 1.92 G Ir (10.8%) — S2a: served sites on `bound-sites-served` | **S2a, built** (Q1) |
| binding trait / existential / hidden-nominal constraints, opaque returns, written nominal bounds, tuple spreads | `:75978`–`:75985` | binding types, the impl table | diag; slots (+2) | the binding-position twins of the bound audit, same place, same reason | small (written bounds 3.4 / 4.1) | S2 |
| `check_tuple_literal_labels`, `check_named_arguments` (B569 S2/S4, lang-a-49, Order 49) | after `check_tuple_spreads` | `tuple_literal_label_problems` (written by the tuple rule in inference, the only place a literal's landing type is known; withdrawn when a later inference matches), `named_arguments` (walk), `spread_packs` | diag only | Class C, after every inference; both READ their tables (never take them), so a stored world carries them to the next analysis | nil without a labelled literal or a named argument | — |
| `check_hmr_transfer_bounds` | `:76008` | `dev::stash`/`take` sites | diag; re-infers through `&mut self` (a mint and a slot write) | deliberately NOT Class A: its mint is read later and a record may not carry a `TypeId` | <1 / 3.9; 3.8 | — (inert unless `web::dev` loads) |
| R10 `check_container_resource_arguments` (Class A, second window) | `:76034` | containers, generic externs | diag, `reported_container_structures` (recorded: R11's dedup set) | before R11 | 27.6 / 39.4; 6.5; slots +5,695 | S1/M19 already |
| R12 + moves (Class A, third window) | `:76037`–`:76038` | resource places | diag, `resource_value_places`, `partial_move_roots` (whole-program, not filtered), **`dbg_stack_moves`** (E281, debug-49: the moved bindings at each `dbg_stack()` call; its module unrecordable) | R1–R9 before R11 and drop planning | moves 15.4 / 35.2; 20.4; slots +3,728 | S1/M19 already |
| record store | `take_reuse_record` `:76050`–`:76064` | the windows' derived diagnostics, and (B575, Order 49) `view_suspension_checks`' enrolment rows per module | the checks record | after the last Class A window; before every post pass, so no post-pass VERDICT is ever recorded — a post pass re-decides the recorded enrolment on every analysis | small | (M19) |
| R11 `check_resource_generic_instantiations` (+ drop-sink argument types) | `:76071`–`:76072` | instantiations, R10's set | diag; slots (+321); `dbg_stack_moves`' generic half (E281) | Class C | **14.5 / 56.6; 53.0**; 0.47 G Ir | S2 |
| `plan_resource_drops` | `:76078` | resource classification, scopes | `dropped_bindings`, `overwrite_drops`, `drop_*` | after the move checker | 16.2 / 55.4; 7.9 (T1c's enrolment record) | S2 (already half) |
| `Drop`/`Callable` impls, trait conformance, exposed unexported types, trait-method scope (B515), class written twice (A155), written autofocus (A157), plain reaches, four duplicate checks, drop glue | `:76082`–`:76132` | the impl table, member sets, import reaches | diag, `drop_methods`, `scoped_reach_checks`, `blanket_residues`, `drop_glue`, `drop_call_edges` | coherence (Class B): the duplicates after conformance and in a fixed order (inherent, block, trait) so a program with several reports them in that order | each < 7 ms | S2 (Class B, global-facts keyed) |

### 3.5 Stage 9: the extraction tail

Everything here runs after the cancellation boundary (`:76148`): on a cancelled
analysis it does not run at all, because it reads the slots the fixpoint fills.

| pass | site | reads | writes | order | cost (server / client; served) | S-role |
|---|---|---|---|---|---|---|
| `Context` and intrinsic tables | `:76160`–`:76465` | impls of std's lang types | the intrinsic map | ⚠ first match over `implementations` (std's, always prefix) | small | S1 |
| `expand_dbg_stacks` (debug-49, Order 49; debugging.md S2) | `analyzer/dbg_stack.rs` | `dbg_stack_calls`, the scopes, `dbg_stack_moves`, `dbg_stack_invalidated`, view origins | **the tree** (one minted `Expr::Local` argument per binding a `dbg_stack()` call reads; post-settle `Id` mints), `dbg_stack_sites` | after every check and R11 (they judge the program as written), before the last-use dataflow (the reads are uses) | nil without a `dbg_stack()` call | — (re-done per analysis; its module is unrecordable) |
| `rewrite_view_assignment_targets` | `:76470` | view assignments | **the tree** (bare assignments to a view become write-through) | a TREE REWRITE: every liveness answer below must follow it | small | — (a rewrite: re-done on each clone) |
| `liveness::LastUse::compute` | `:76476` | the final tree | `last_use` | after the rewrite ("a liveness answer about a tree that no longer exists is worse than none") | 13.6 / 49.8; 18.4 | S2 (T1b already records rows) |
| drop extents, shared cells, written roots, shared reads, shared place lets, **capture plan** | `:76481`–`:76501` | `last_use`, the tree | `shared_cells`, `shared_read_bindings`, `shared_place_lets`, the capture plan | each after the one before it (B267 → M90 → B53: the capture plan decides which captures own nothing before rule 2) | 19.1 / 65.9; **59.6** (not reduced on a hit) | S2 |
| `compute_resource_types` | `:32322` | the whole interned type table | `HashSet<TypeId>`; slots (+4,741) | "an interned id is nobody's to own" — not restorable as-is | 25.2 / 46.5; 40.8 | S2 only after S5 (Q3) |
| clone sites, return clone sites, parameter entry clones, the view classifications, boxed locals, scalar views | `:76505`–`:76518` | all of the above | the copy and view plans | clone sites after the capture plan | clone sites 24.7 / 62.8; 17.5 | S2 (T1b records rows) |
| T1b record, HMR bindings, hint labels, expression types and labels, declaration labels, member headers, type definitions, pattern labels, reference hovers, alias spans, `[rpc]` origins | `:76520`–`:76986` | settled types | the editor's label tables | rendered strings keyed by id: a pure function of the settled types | **28.2 / 55.8; 46.5** | **S2** (Q1's fallback) |
| hidden impls, declaring scopes, exposed private types, object-reachable members, item costs, the `Program` | `:77092`–`:77390` | | `Program` | last | (in the above) | — |

### 3.6 Stage 10: `post_analysis_passes` (`lib.rs:1119`)

One call graph is built here and shared (E35, `const-eval.md` §8.4). The served
column is the editor's hot-set keystroke.

| pass | site | reads | writes | order | cost (server / client; served) | S-role |
|---|---|---|---|---|---|---|
| `build_impl_admission`, scoped exports, unlowered externals, global property externs | `lib.rs:1145`–`:1159` | `only`/selectors, `export(in ..)`, externals | the admission map, diag | first: the context pass's candidate lists and emission read the map | `build_impl_admission` 0.01 G Ir | S2 (global facts) |
| `labels::check` | `:1163` | labels, `[internal]` uses | warnings | over the finished program | 0.02 G Ir | S2 |
| `record_declared_platforms` | `:1166` | files' and impls' `[platform(..)]` | `declared_requirements` | before every pass that asks what a function requires | small | S3 (input) |
| **`context::thread_contexts`** (+ `CallGraph::build`) | `:1181`; `context.rs:62` | every `Context` get/run/new site, the call graph | **the tree**: hidden parameters, threaded arguments, `get()` → local, `run(v, f)` → `f(v)`; `entity_map`, `function_calls`, `generic_dispatch`, `method_call_substitution`, `next_entity_id`; coverage diag | builds its own graph; when it rewrites, the graph is rebuilt after it (kolt rewrites on both legs: four graph builds, 0.20 G Ir); coverage checks are DEFERRED to one warning when the program already has errors (`context.rs:138`) | **26.9 / 174.2; 153.8**; 0.63 G + 0.20 G Ir | **S3**, once the rewrite is a table (Q2) |
| `track_caller::thread_locations` | `:1186` | `[track_caller]` functions, the graph | **the tree**: a hidden trailing `Location` parameter and argument per call; `next_entity_id` | after the graph (it appends arguments, never calls, so the graph stays true) | 0.004 G Ir | S3 companion: local per call site, re-run on hot nodes |
| **`async_infer::infer`** | `:1197` | the graph, async externs, `await`s, dispatch candidates | `async_functions`, `async_values`, `awaited_calls`, `adapted_instances`, `suspending_calls` | callee → caller fixpoint; after the context rewrite (a lowered `run(v, f)` is a call to `f`) | **47.5 / 135.0; 112.4**; 0.86 G Ir | **S3** |
| `check_view_suspensions` | `:1205` | `view_suspension_checks`, the async set | diag | decides what `check_invalidation` enrolled (B?1) | 0 | — (must see every body's enrolment) |
| call-site admission, async drops, context drops, lazy argument effects | `:1213`–`:1228` | the admission map, the async set, `context_dependent_functions` | diag | each after the fact it reads is settled | 0.04 G Ir | — |
| **`platform_color::check`** | `:1230` | the graph, declared requirements, entry `main` | diag | reachability from `main`, per instantiation; the editor also calls `platform_color::requirements` for hover | **18.1 / 59.5; 48.4**; 0.40 G Ir | **S3** (summaries) + a cheap re-walk |
| **`const_eval::evaluate`** | `:1245` | `const` sites, the graph, tracked input files | `const_results`, `const_assets`, `const_input_files`, `const_bundled_files`, `const_facts`, `const_snapshot_bindings`; diag | **skipped when the program has any diagnostic** (`const_eval.rs:862`); its `check_const_only` shares `dispatch_refine` with the context pass | **9.3 / 525.6; 450.1**; 3.92 G Ir (22.1%) | **S4** (incr-48) |
| `contract_hash::resolve_contract_hashes` | `:1258` | `[service]` surfaces | **`const_results`** (a second writer of the table) | must follow the const pass's assignment of `const_results` | 0.01 G Ir | S4 must keep or recompute these rows |
| install graph, module-level cells (A130), lifetime steers (A135/A136) | `:1262`–`:1275` | the installed graph | diag | over the installed graph | 0.02 G Ir | — |
| `init_order::check_cycles` | `:1277` | initializer dependencies | diag | **skipped when the program has any diagnostic** (`init_order.rs:123`) | small | — |
| `normalize_diagnostic_order` | `:1284` | both lists | their order | THE seam for diagnostic order (E38): nothing after it adds a diagnostic | small | — |
| `incremental::report` | `:1349` | the finished program (effects included) | the census; fingerprints under `VILAN_INCREMENTAL` | after every pass, because an interface includes the effects the passes settle | 922 Ir unarmed | (S0) |

### 3.7 Stage 11: the front ends' own passes

| pass | where | reads | writes | order | cost | S-role |
|---|---|---|---|---|---|---|
| `track_caller::refuse_release_dbg` | CLI `main.rs:7037` | `dbg` calls, the build options | diag | after the post passes; CLI only | small | — |
| `const_eval::infer` | CLI only (`const_eval.rs:1027`, pinned out of `analyze_source`) | `let` initializers, the explicit results | extra folds | skipped on any diagnostic; never in the editor | — | — |
| emission (`diagnose`, `transform`, `transform_split`, `vilan_rust::emit`) | CLI | the program | JS / Rust | skipped on errors; its pre-passes: `NameSeed::build`, `init_order::initialization_order`, `platform_color::reachable_bindings` (the second reachability walk), demand-driven monomorphization with `impl_select` (M111's memos), vtables, `chunks::plan` | 41.6 / 172.0 ms; `diagnose` 0.98 G Ir | — |
| editor tables | `document.rs:2111`–`2172` | the program | `entity_spans`, field spans, `ReferenceIndex`, platform requirements, the landed walk, the completion index | after the analysis; references stay whole-entry | lsp-index 55.7, lsp-landed 26.0, lsp-context 41.8 (served) | S2 (the reference index's prefix half, per the paper) |
| further platform legs, the verify mode | `document.rs:2625` (one further leg), `:140` (`verify_against_clean`) | — | another whole analysis per extra platform; a clean analysis beside each under `VILAN_INCREMENTAL=verify` | — | ×2 for `shared.vl` (cited) | each leg gets its own hot-set world |

## 4. Where the cost is

### 4.1 `vilan check` of kolt, by phase

Median CPU of five runs; "≈ G" is the share of 18.93 G; callgrind Ir where the
function is visible.

| phase | server ms | client ms | share | ≈ G | callgrind |
|---|---:|---:|---:|---:|---:|
| load + walk | 150.3 | 312.6 | 12.7% | 2.41 | parse 0.86 G, walk 0.11 G, expand 0.06 G |
| base (pre-entry `resolve_world`) | 145.7 | 494.1 | 17.6% | 3.34 | `resolve_world` 3.16 G (both calls) |
| — of which the fixpoint | 126.7 | 436.1 | 15.5% | 2.93 | `resolve_constraints` 2.84 G |
| build | 11.9 | 27.6 | 1.1% | 0.21 | `finalize_build` 0.16 G |
| checks (stages 8–9) | 272.0 | 939.4 | 33.4% | 6.32 | `analyze_over_world` 6.02 G incl. build |
| — bound audit | 36.0 | 224.6 | 7.2% | 1.36 | 1.92 G |
| — `infer_bumps` | 16.2 | 100.8 | 3.2% | 0.61 | (inlined) |
| — clone sites | 24.7 | 62.8 | 2.4% | 0.46 | (inlined) |
| — drop extents, shared cells, capture plan | 19.1 | 65.9 | 2.3% | 0.44 | (inlined) |
| — the remaining tables and labels | 28.2 | 55.8 | 2.3% | 0.44 | (inlined) |
| — R11 | 14.5 | 56.6 | 2.0% | 0.37 | 0.47 G |
| — resource types | 25.2 | 46.5 | 2.0% | 0.37 | (inlined) |
| — `plan_resource_drops` | 16.2 | 55.4 | 2.0% | 0.37 | 0.22 G |
| — R10 | 27.6 | 39.4 | 1.8% | 0.35 | (inlined) |
| — `LastUse::compute` | 13.6 | 49.8 | 1.7% | 0.33 | (inlined) |
| — moves | 15.4 | 35.2 | 1.4% | 0.26 | (inlined) |
| post passes | 110.5 | 910.5 | 28.1% | 5.32 | `post_analysis_passes` 6.02 G |
| — const pass | 9.3 | 525.6 | 14.7% | 2.79 | 3.92 G |
| — contexts + graph | 26.9 | 174.2 | 5.5% | 1.05 | 0.63 + 0.20 G |
| — async inference | 47.5 | 135.0 | 5.0% | 0.95 | 0.86 G |
| — platform colour | 18.1 | 59.5 | 2.1% | 0.40 | 0.40 G |
| emission walk | 41.6 | 172.0 | 5.9% | 1.11 | `diagnose` 0.98 G |
| program drop | 10.3 | 32.3 | 1.2% | 0.22 | — |

Type slots minted AFTER `types_settled` on the client leg: 15,998 of 210,704
(the counter's `settled-slots`), by the bound audit (+1,242), R10 (+5,695),
moves (+3,728), R11 (+321), drop planning (+127), resource types (+4,741) and
the tail (+45). Late writes (writes to a settled slot) are 0. This matters for
S2 (§7.1) and S5 (§7.3): a check that mints is not a pure reader.

### 4.2 An editor keystroke, served and refused

Medians of six analyses each, CPU ms (`[vilan pass]` and `[vilan phase]` lines
of the server).

| part | refused (`model.vl`, 14.11 G) | served (`views.vl`, 9.97 G) | served share of `lsp-analyze` |
|---|---:|---:|---:|
| load + walk | 372.8 | 65.9 | 4.4% |
| base | 451.2 | 0 | — |
| build | 28.0 | 32.5 | 2.2% |
| checks | 890.2 | 602.9 | 39.9% |
| — bound audit | 192.3 | **203.2** | **13.5%** |
| — drop extents, shared cells, capture plan | 65.1 | 59.6 | 3.9% |
| — R11 | 56.6 | 53.0 | 3.5% |
| — remaining tables and labels | 55.0 | 46.5 | 3.1% |
| — `infer_bumps` | 96.8 | 43.6 | 2.9% |
| — resource types | 49.9 | 40.8 | 2.7% |
| — moves | 35.8 | 20.4 | 1.4% |
| — `LastUse::compute` | 50.3 | 18.4 | 1.2% |
| — clone sites | 55.8 | 17.5 | 1.2% |
| — `plan_resource_drops` | 58.0 | 7.9 | 0.5% |
| — the Class A window (14 checks) | ≈ 70 | ≈ 25 | 1.7% |
| post passes | 815.9 | 787.2 | 52.1% |
| — const pass | 460.8 | **450.1** | **29.8%** |
| — contexts + graph | 164.7 | **153.8** | **10.2%** |
| — async inference | 113.8 | **112.4** | **7.4%** |
| — platform colour | 48.3 | 48.4 | 3.2% |
| `lsp-analyze` | 2,572.4 | 1,510.3 | 100% |
| `lsp-context` / `lsp-index` / `lsp-landed` | 47.2 / 58.0 / 28.8 | 41.8 / 55.7 / 26.0 | — |

Read across, the served keystroke has already lost what S1 can remove (load,
walk, base: −758 ms) and what M19's windows can skip (the Class A checks, most
of drop planning, half of liveness and the clone sites). What is left is the
const pass (S4, this order), the Class C checks and the tail's tables (S2), and
the post-pass fixpoints (S3). After S4, the bound audit is the largest single
pass left, and contexts + async + platform + `infer_bumps` together are 358 ms.

### 4.3 What a broken keystroke skips (M122's answer, measured)

kolt with one ill-typed function appended to `views.vl`: 14.53 G against 18.93
G (−23.2%). The client leg's const pass reads 0.0 ms, against 525.6 ms clean,
and the emission walk does not run. Three passes are gated on a CLEAN program:
the const pass (`const_eval.rs:862`), the init-order cycle check
(`init_order.rs:123`) and the context pass's coverage refusals (deferred to one
warning, `context.rs:138`). In the editor, which never emits, the const pass
accounts for most of the difference S0's session saw (12.7 against 9.3 G). This is M122
(incr-48's); it is recorded here because it is an order dependence of a kind the
map has to name: **these three passes depend on whether ANY diagnostic exists
anywhere in the world**, so an error in one module suppresses another module's
const diagnostics, and a const-cache record (S4) is valid only for a clean
program.

## 5. The order-dependent special cases to delete

Each is a place where an answer depends on load order, walk order or the
timing of a configuration write, rather than on the program. Each gets the
invariant that replaces it. §6 says which of them the differential can see.

### 5.1 B553 — the entry's impls and first `run` arrive after the modules committed

**What.** `impl Foo with Greet` in the entry is invisible to a module's
`foo.greet()` ("`Foo has no method 'greet'`", reproduced here: `finds/b553`),
and a module's `Context::new()` grounded only by an entry `run` reports `T`
unbounded. Both work when the impl or the `run` sits in any module.

**Why.** §2's fact 1: the modules' constraints are resolved, and their failures
REPORTED, by the pre-entry fixpoint; the entry walks afterwards. An element
slot grounded only by the entry does NOT fail (probed: `mut bag = []` in a
module, `bag.push(1)` only in the entry, checks clean), because an unresolved
slot stays queued into `build()`; a failed member lookup does not stay queued.

**The invariant.** *Global facts precede every commitment*: every impl header
and member signature in the world (prefix, hot set and entry) is registered
before the first fixpoint, and no constraint that a later-walked file could
satisfy is reported before the last resolve. M121 door (b) (incr-48) builds the
first half: a pre-walk of the hot set's and the entry's impl headers and member
signatures into the prefix. The context half is not traced here; the probe
above suggests the shape of its fix: a `Context`'s type left open into
`build()`, as the plain element slot already is, rather than bound-checked at
the base resolve.

### 5.2 B554 — blame by file name

**What.** Two modules push `1` and `"two"` into one `mut bag = []`; the error
lands on whichever push's module loads later in name order (reproduced:
`finds/b554` reports at `bag.vl:3`, `finds/b554z` — the same program with the
second module renamed `z_spoil.vl` — at `z_spoil.vl:3`).

**Why.** The element slot takes the FIRST push in walk order, and walk order is
the drain's `(tier, index, name)` order.

**The invariant.** *A diagnostic's location is a function of the program, not of
the file names*: an element-type conflict on a module binding is reported at the
binding's declaration (the one place that is independent of order), naming
every push that disagrees. S1 refuses this shape today by its use-inferred
guard; the guard can stand down for it once the invariant holds.

### 5.3 The top-level-only walks — B560 (closed), E267 (closed), B561 (open)

**What.** Walks that enumerate "every module" by the root scopes alone: the
"import it first" steer spelled a nested module by its leaf (B560), the
auto-import table skipped nested modules (E267), and `import_path_of`
(`analyzer.rs:55170`) still spells `pkg::<leaf>::<name>` for a trait in a nested
package module (B561, editor-48 this order). It is also a first match over
`modules` in load order (§5.6).

**The invariant.** *One enumerator of the module tree.* Every walk over "all
modules" goes through one function that yields every loaded module, nested
ones included, with its full path; B560's fix inside `import_steer_inner` is
that function's first draft. A census test in the style of the marker census
can list the walks that iterate `modules` or `module_children_scopes` directly.

### 5.4 The Class A window's side tables — B?1 (found here)

**What.** `check_invalidation` (Class A) enrols E3's implicit-suspension checks
in `view_suspension_checks` for the bodies it does not skip; the post pass
`check_view_suspensions` decides them once the async set is known. On a reusing
analysis a reused module enrols nothing, its record does not carry the
enrolment, and the post pass runs after `take_reuse_record` so its verdicts are
never recorded. Reproduced (`finds/suspend_reuse`, driven by
`finds/lspprobe.py`): `vilan check` refuses the module twice ("an async function
cannot take '&mut' parameters …"); the editor publishes both errors on the cold
analysis, `[]` after one keystroke in the entry (`reused 25/25`), and still `[]`
after the keystroke is undone. Under S1 (`finds/suspend_reuse_hot`) the errors
flicker: present on the hot-set miss, gone on the next hit (`reused 25/26`).

**Why it is an order case.** The pass order is right (the post pass must follow
async inference); what breaks is the window's contract. M19 states it for
diagnostics ("adding a check here without routing it through `reusable_entity`
is exactly that bug"); nothing states it for the TABLES a windowed check writes.

**The invariant.** *A Class A check may skip a reused body only if every table
it writes for a later pass is recorded or recomputed.* For this one the cheap
fix is to enrol every body (the enrolment is the cheap part of the check; only
the check's own diagnostics are reusable). The static census of §3 (`writes.py`)
lists the other Class A side tables: `lazy_argument_resource_refusals` (read by
R9, which skips the same bodies: consistent), `reported_container_structures`
(recorded), `resource_value_places` and `partial_move_roots` (computed over the
whole program, not filtered: consistent). Only `view_suspension_checks` breaks
the rule today.

### 5.5 B573 and B?2 — configuration written after the passes that read it

**What.** `analyze_inner` walks the modules, selects their platform twins
(`:74821`, and `:72104` for a hot module) and runs the pre-entry resolve on an
analyzer whose `platform` is `Platform::default()` (node); `analyze_over_world`
assigns the real platform later (`:75598`). B573 (editor-48's find) is the
miscompile: a browser bundle ships the `@process` twin. B?2 is the same root
read by diagnostics: a module's note says "`View` here is std's browser twin —
this file is analyzed under node" in a browser build (`finds/p1_note`; the entry
says "under browser", `finds/p1_note_entry`). The fenced-out steer
(`:54176`) and the web-prelude steer (`:54215`, which reads `prelude_repair`) have
the same exposure.

**The invariant.** *The analyzer's configuration is fixed before its first
pass*: `platform` is assigned at construction in `analyze_inner` (it is in
`BaseCacheKey`, so a stored world built under it is keyed by it). The two facts
deliberately kept OUT of the key, `platform_reason` and `prelude_repair`, must
not be rendered into a diagnostic a stored world carries: render them when the
diagnostic is published, or key them. The rule generalizes: a stored world may
hold only what its key determines.

### 5.6 Answers chosen by position — M?5 (found here)

The canonical order IS meaningful in four ruled places, and a reordered world
must keep them: `declaration_order` (method resolution's tie-break,
`method-resolution.md` §2), B57's least-entity-id rule (`:8669`), the
emission order (declarations sorted by id) and the C1 rule that every
whole-program check sorts its reports by id. S5's windows preserve all four,
because windows are laid out in load order.

A fifth ruled place, found by the permutation differential (Order 49): a
requirement trace's hops (E78) are ordered by depth and, at one depth, by id —
the C1 rule inside one diagnostic. The differential reads a trace as the set of
its hops for that reason; S5's windows must keep the order.

Four more places were positional by ACCIDENT (each replaced by a content-defined
rule in Order 49, M128 — the ranking for `callable_call_signature`, the scope
chain for the macro fallback, the block's id for `for_each_next_providers` and
`declined_default_calls`, a proof of uniqueness for `import_path_of`; and the
loop's `next` lookup admitted under the looping file, which the first-match
had hidden): `resolve_macro_reference`'s fallback
(`:47304`, the first module in load order whose macro namespace has the name),
`callable_call_signature` (`:45923`, the first impl in load order that declares
`call` and admits the subject — it does not rank a blanket against a concrete
subject as `rank_member_candidates` does), `import_path_of` (`:55178`), and
`for_each_next_providers` (`:61970`, which stores an impl's INDEX in
`implementations` as a table value). In S1's world the hot modules load after
the prefix; under M121 door (b) the hot set's impl headers join the prefix's
`implementations` in a new position. **The invariant**: *an answer is chosen by a
content-defined rule (the ruled ranking, or the scope chain), never by the first
match in a load-ordered table; an index into a load-ordered table is never a
stored value.* No diverging repro was built (code-read); each site wants a
differential class that puts two candidates in different load positions.

### 5.7 Already fixed, and what they teach

- **The macro-name reference order** (incr-47, rides S1): `[derive(Wire)]`'s
  reference to its `macro fun` was recorded at the walk, so whether it resolved
  depended on whether the macro's module had walked yet. It is queued at the
  walk and resolved at the top of `resolve_world`. The fallback in §5.6 is its
  residue.
- **B547** (solver-47): a macro marker bound by an import stood in for an item
  of the same name that a later re-export would bring (`Storable`, the trait and
  the derive). Markers now bind only on the import fixpoint's reporting pass.

The lesson of both is the walk/resolve split: *the walk declares, the resolve
resolves, and a resolution that picks between candidates waits until the set of
candidates is complete.* The walk honours it (§3.1); §5.1, §5.2 and §5.6 are the
places the resolve does not yet.

## 6. What the edit-replay differential proves, and what it does not

`crates/vilan-core/tests/edit_replay_differential.rs` (M110 Q3) analyses each
scripted edit incrementally and cleanly and compares `render_observation`
(`incremental.rs:639`), then undoes the edit and compares again.

**It proves, for its corpus and its edits:**

1. diagnostics and warnings, in published order, with file, span, message, note
   and trace, are identical to a clean analysis;
2. every hover type label, declaration label and inlay hint at its (file,
   span) is identical;
3. every name resolution (`entity_map`'s references) and every `type_references`
   row (macro-name references included) is identical;
4. the emitted JS is byte-identical to a clean analysis built in the SAME
   shape, where the program has no errors;
5. the four plants (`HotSetReplay`, `PrefixUnvalidated`, `ImplGuardOff`,
   `UseInferredGuardOff`) turn it red, and the counter pins bound what a
   keystroke re-walks.

**It does not prove:**

1. **That the clean analysis is independent of load order.** Both legs share
   the two-phase resolve, the drain's order and the late configuration, so
   B553, B554, B573 and B?2 are invisible to it by construction. The missing
   gate is a **permutation differential**: the same package with its file names
   reversed (and, separately, its modules nested one level deeper), compared on
   an id-free observation. B554 is its expected red today.
2. **Post-pass verdicts on reused modules.** No classes-leg module carries a
   diagnostic that a post pass decides, and corpus programs are clean, so B?1 is
   green. Add a class: a prefix module with an E3 suspension refusal, a
   context-coverage refusal, a platform refusal and a const failure, each edited
   around.
3. **Tables it does not render**: `unwired_method_calls` (editor-47), the
   platform requirements hover, the completion index, the landed walk, entity and
   field spans, member headers, pattern labels, reference hovers, type
   definitions, the async set and the context rewrite except through JS, and the
   const results except through JS.
4. **JS of an incremental world against the canonical world** (only against the
   same-shape clean one), and JS of any program with an error.
5. **The editor's further platform legs** and its union legs.
6. **Cross-process validity** of anything persisted (no record is persisted yet).
7. **That a skipped check's mints were not read** (§4.1's post-settle slots): the
   observation is id-free, which hides a shifted `TypeId` unless an answer moves.

## 7. What Order 49 builds from the map

### 7.1 S2: prefix tables

A prefix table is a pass whose output for prefix entities is a function of
prefix inputs plus the global facts, recorded with the world and replayed when
the dirty bits are clear and the global-facts fingerprint is unchanged. Ranked
by what is left on a served keystroke (§4.2) and by risk:

| candidate | served ms | inputs beyond the prefix | risk | rec |
|---|---:|---|---|---|
| the bound audit at prefix call sites | 203.2 | the impl table (global facts), callee interfaces | Class C: an entry or hot call grounds a module generic, but that dirties the module (T0); mints 1,242 slots | **first** (Q1), keyed through M123's memo |
| drop extents, shared cells, capture plan | 59.6 | `compute_shared_cells` unions cell identity over EVERY module's bodies (a hot module can clone or store a prefix cell) and the capture plan and shared reads read `collect_written_roots`, which is whole-program (a hot module writes a prefix binding) — measured in Order 49 (incr-49, S2b): not a function of the prefix alone; only the drop extents (per body, after liveness) are | NOT a prefix table as written; a per-module table needs the cell unions split by module with a cross-module seam | HELD (Order 49 finding) |
| R11 at prefix instantiations | 53.0 | the impl table; R10's set (recorded) | its refusals anchor at the INSTANTIATION with a note into the callee's body (`emit_generic_leak`), so a prefix callee's rows belong to the instantiating module, which may be hot: a per-module record needs the instance keyed by (callee, types) with the note's source carried — found in Order 49 (incr-49) | HELD after the bound audit (S2a built) |
| the tail's label tables | 46.5 (27.3 for "the remaining tables, labels and records" at Order 49's tip, after S2a) | none (settled types) | lowest: strings by id; MEASURED on kolt (incr-49, `VILAN_COUNTERS` `labels` line): `expr_types` 18,207 rows / 253 KB, declarations 3,183 / 156 KB, member headers 797 / 24 KB, hints 38 per client leg — ~0.5 MB of strings, ~1.5 MB with the maps, 0.2% of the editor's 774 MB RSS at a kolt keystroke | **built** (S2b, Order 49): `ModuleTables::expr_types` / `declaration_labels`, restored through `RestoredTables`, the builders skipping `table_entity` ids; plant `LabelTablesUnrecorded`; measured −0.5% of a served `views.vl` keystroke (4.46 → 4.44 G, 5.30 → 5.27 G world mode) on the same std |
| resource types | 40.8 | the whole interned type table | not restorable until types are windowed | after S5 |
| moves, liveness, clone sites | 20.4, 18.4, 17.5 | none | low; T1b already records rows | as they come |
| the reference index's prefix half | (in lsp-index 55.7) | none | low | editor side |

Two rules from the map bind every S2 table. **A pass that mints slots** (the
bound audit, R10, R11, moves, resource types) changes every later `TypeId` when
it is skipped; the table is sound only if no output depends on a post-settle
`TypeId`'s value, which S2 has to assert (a census over the tail's readers).
**A pass gated on a clean program** (§4.3) records nothing for a broken one.

### 7.2 S3: seeded fixpoints

The fixpoints over the call graph: contexts (+ the graph), async, platform
colour, and the two analyze-time ones the paper's list missed, borrows and
bumps (M?4). On a served keystroke: 153.8 + 112.4 + 48.4 + 43.6 + 2.5 = 361 ms.

What the map says about them:

- **No reorder is needed.** Async must follow the context rewrite (a lowered
  `run(v, f)` is a call to `f`), the effect checks must follow async, the const
  pass reads the same graph. The order in `post_analysis_passes` is the data
  flow.
- **Two tree rewrites must become tables.** The context pass deletes and mints
  call edges and parameters (and forces a second graph build: four on kolt);
  `[track_caller]` appends a parameter and an argument per call. A seeded pass
  cannot start from a stored graph that a rewrite has invalidated. Recast both as
  tables the emitters read (the hidden-parameter table already exists as
  `context_hidden_parameters`), and the graph is built once and stored with the
  prefix. `rewrite_view_assignment_targets` (stage 9) is the third rewrite; it is
  per body and runs before the tables, so it can stay.
- **Seeds come from the prefix alone.** Reusing last keystroke's settled sets is
  unsound for a deletion: an edit that removes the hot set's only `get()` must
  shrink the need set, and a monotone fixpoint cannot shrink from a seed that
  already contains it. Seed each fixpoint from a result computed over the prefix
  with hot callees as unknowns (stored with the world), then iterate from the
  hot set's nodes and their callers.
- **Dispatch is the leak.** Each of the five treats a dispatched call by its
  candidates (async, platform, contexts) or conservatively (bumps). A hot impl
  is a candidate for a prefix call site only through an impl header the prefix
  can see, which is exactly what M121 door (b) puts in the prefix. S3 depends on
  door (b) landing.

**Order 49's finding on S3a (incr-49, read at next 71d61dde).** "Tables the
emitters read" (Q2) under-counts the consumers: the rewrite edits the tree
every later pass reads — `CallGraph::build` (the lowered `run` edges),
`async_infer`, `platform_color`, `dispatch_refine`, `check_call_site_admission`,
the const interpreter, `init_order`, the chunk planner — and the emitter surface
is 279 `argument_ids` + 68 `.parameters` + 48 `Expr::Local` reads in
`vilan-rust/src/lib.rs` and 19 / 34 / 26 in the JS transformer, most inside the
debug and native lanes' files. That is an L change across two backends and seven
passes. Two forms for Order 50:

- **the emitter-table form** (L): four tables — the hidden parameters per
  function in order, the threaded arguments per call, the `get()` → parameter
  reads, the lowered `run` calls — consulted by every consumer above; sequenced
  AFTER the debug and native lanes, never beside them; gated by the native
  differential and the contexts/`track_caller` corpora byte-identical.
- **the mutation-log form** (M, recommended): the rewrite's edits recorded per
  PREFIX function with the ids they mint (a record keyed by the world like S2a's
  and S2b's: replayed on a hit, recomputed for the hot set, planted red), the
  emitters and the later passes untouched, the native differential trivially
  green. S3b's seeds then come from the stored prefix results (the context
  fixpoint's need set, the async set, the platform colours, `borrows`/`bumps`
  verdicts) with hot callees as unknowns, iterated from the hot set's nodes and
  their callers. The one M piece safe alone: the call graph built once per
  analysis and stored with the prefix, hot nodes added over it (~20–40 ms of a
  served keystroke; the four cold builds are 0.20 G Ir).

What S3 is worth at Order 49's tip (served `views.vl` keystroke, medians over 42
served analyses): contexts+graph 97 ms, async 52, platform 13, `infer_bumps`
19, `infer_borrows` 1.4 — ~183 ms of a ~480 ms analysis; the 361 ms above was
measured before M123's memo and S4.

### 7.3 S5: the spike

The map gives the spike its assertions (Q3): every walk-minted id inside its
item's window; the four ruled positional answers and the §5.6 sites unchanged;
no `TypeId` shared between two items' windows, counting the fixpoint's mints
AND the 15,998 post-settle mints of §4.1 (those are minted by checks, not by
the solver, and have no anchor item today); the permutation differential green
(B554 excepted until it closes); the corpus differential byte-identical with
windows forced on.

## 8. The seams this order

| seam | incr-48 (world, base cache, drivers, const pass, LSP scheduling) | solver-48 (inference, checks, `impl_select`, mono) | others |
|---|---|---|---|
| M121 door (b)'s pre-walk | the new pass between the drain and the base resolve | the impl registration it calls (`walk_impl_entity`'s headers) and the lookups that read them | §5.6's first-match sites (any lane that touches them) |
| B573 + B?2 | `analyzer.platform` at construction; the unkeyed facts rendered late | — | editor-48's E254 waits on it |
| B?1 | the record (`ModuleTables`) if recorded | `check_invalidation`'s enrolment if enrolled for every body | — |
| M123 (the bound audit's memo) | S2 stores it in Order 49 | builds it this order | ask: key it canonically (no `TypeId`) so S2 can persist it |
| S4 (the const cache) | builds it | — | `contract_hash` writes the same table (§3.6) |
| `resolve_world` | its top (macro references) and its call sites | its stages | layout-48: resolution and the loader's module paths (B548) |
| post passes | the order | — | debug-48: `[track_caller]` (§7.2's second rewrite) |
| Class B checks | — | — | std-48: A155's class-twice check (A162's flip) runs in the coherence block |

## 9. Finds, for the integrator to file

Written to `sweeps/order48/newitems48-papers-a.json`, repros under
`sweeps/order48/papers-a-48/finds/`.

1. **B?1** — the editor drops a module's E3 view-across-suspension errors on every
   reusing analysis (§5.4). Reproduced in the editor; the CLI is right.
2. **B?2** — B573's other readers: a module's pre-entry diagnostics render the
   default platform ("analyzed under node" in a browser build); `platform_reason`
   and `prelude_repair` are read early too (§5.5).
3. **N?3** — three of the `resolve_world` split's buckets time something else:
   `contexts` times `build_lookup_admission`, `locals` times the assignment
   drain, and the context clauses and the first-part locals sit inside
   `conformance` and `binder-bounds` (§3.2).
4. **M?4** — S3's list misses `infer_borrows` and `infer_bumps` (§7.2).
5. **M?5** — four answers chosen by first match over load-ordered tables (§5.6).

Measured for incr-48's M122 (not filed: the item is open and owned): the broken
keystroke's saving is the const pass, gated on a clean program (§4.3).

## 10. Questions for the owner, each with a recommendation

- **Q1. S2's first table.** **Rec:** the bound audit's verdicts at prefix call
  sites, recorded per source and replayed when the source is not dirty, the
  global-facts fingerprint is unchanged and the callees' interface fingerprints
  are unchanged; keyed through M123's memo, which solver-48 should key
  canonically this order. It is 13.5% of a served keystroke, the largest pass
  left after S4. If M123 does not confirm, start with the tail's label tables
  (3.1%, the lowest risk) to build the record machinery (§7.1).
- **Q2. S3's shape.** **Rec:** no pass reorder. Recast the context rewrite and
  `[track_caller]`'s locations as tables, store one call graph with the prefix,
  seed each fixpoint from a prefix-only result, and add `infer_borrows` and
  `infer_bumps` to the list. S3 waits for M121 door (b) (§7.2).
- **Q3. The S5 spike's assertions.** **Rec:** window containment for walk ids;
  the four ruled positional answers and §5.6's sites unchanged; no `TypeId`
  shared across items, post-settle mints included; the permutation differential
  green except B554; the corpus differential byte-identical with windows forced
  (§7.3).
- **Q4. A permutation differential as a gate.** **Rec:** build it in Order 49
  before S2 lands: kolt-shaped fixtures and the classes leg under reversed file
  names and one extra nesting level, compared on `render_observation`; B554 is
  pinned as its known red until it closes (§6).
- **Q5. The configuration rule.** **Rec:** `platform` is set at construction
  (B573's one line), and a stored world never renders an unkeyed workspace fact;
  `platform_reason` and `prelude_repair` are rendered at publish (§5.5).
- **Q6. The Class A contract.** **Rec:** extend M19's rule to tables: a windowed
  check that writes a table a later pass reads must record it or compute it for
  every body. Fix B?1 by enrolling every body, and add the post-pass class to the
  differential (§5.4, §6).
- **Q7. First-match answers.** **Rec:** replace §5.6's four sites with the ruled
  ranking (or the scope chain for the macro fallback) before door (b)'s pre-walk
  reorders `implementations`, or prove each unreachable for the reordered part;
  one differential class per site.
- **Q8. Passes gated on a clean program.** **Rec:** keep the gates (they protect
  the transformer and the init-order relation), and write the rule into S4's key:
  a const record is valid only for a clean program; M122 decides whether the
  editor should run the const pass on a broken one (§4.3).
- **Q9. Keeping the map true.** **Rec:** the pass order lives in three drivers
  and drifts by one pass per order; a lane that adds or moves a pass updates §3's
  table in the same commit, and the `[vilan pass]` names (the `stringify!` of the
  call) are the table's keys, so a script can diff the two at a seal.

## 11. Slices this map implies for Order 49

| slice | content | size | gate |
|---|---|---|---|
| P0 | the permutation differential; the post-pass class in the edit-replay differential | S | green on itself; B554 pinned red |
| P1 | B?1 (enrol every body), B573 + B?2 (configuration at construction), N?3 | XS–S | the new classes green |
| P2 | §5.6's first-match sites ranked | S | one class per site |
| S2a | the bound audit's prefix table on M123's memo | M | edit-replay differential; a planted fingerprint omission red |
| S2b | the tail's label tables; the capture plan; R11 | M | as S2a |
| S3a | the context rewrite and `[track_caller]` as tables; one stored graph | M | emitted JS identical (the contexts and `track_caller` corpora) |
| S3b | seeded contexts, async, platform, borrows, bumps | M–L | differential with effect edits (the §6 classes add a removal of a `get()`, a `sleep`, a node call) |
