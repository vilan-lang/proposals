# Incremental analysis — why an edit re-analyses the whole entry, and the staged way out (M110)

> Status: **PAPER, drafted 2026-10-03** for the owner to rule on (Q1–Q10).
> Written by lane papers-b-46 of Order 46. Nothing in the compiler, kolt or the
> website changed. Every claim about today's behaviour is a line that was read
> or a probe that was run on the installed `vilan 0.43.0 (fe092e8d1)`. Source
> is cited at `next` @7ee822af (`.claude/worktrees/integration`) and, for the
> language server's entry-world code, at editor-46's branch @5f56923d
> (`.claude/worktrees/editor-46`), which is where M104 lives until it merges.
>
> No cargo build and no LSP session was run: four lanes were building on the
> machine (loadavg 7–13). The LSP numbers are editor-46's (`REPORT-editor-46.md`,
> instructions from its callgrind and `lsp-latency.py` runs) and Order 45's
> (`REPORT-perf-b-45.md`), and are marked as cited. What I measured myself is
> static (censuses of kolt and std, kolt's git history) plus one
> `VILAN_PHASE_TIMING=passes vilan check` of a scratch copy of kolt's working
> tree.
>
> Probes and scripts: `scripts/integration/sweeps/order46/papers-b-46/incr/`.
> `probes/i1`–`i7` are the invalidation probes, re-run by `probes/run_all.sh`
> (output `probes/run_all.out`). `census.py` counts functions, inferred
> returns, impls and blankets (`census-kolt.txt`, `census-std.txt`).
> `edit_classes.py` classifies every changed item in a repository's history
> (`edit-classes-kolt*.txt`). `hot_set.py` computes, per module, what a split
> world would have to re-walk (`hot-set-kolt-client.txt`). `phase-kolt-0430.txt`
> is the phase split.
>
> Related: M110 (this item), M104 (entry-world analysis, ruled 2026-10-02 and
> 2026-10-03), M19 and `per-module-analysis-reuse.md` (the reuse that exists),
> M99 (what it cannot reach), M73/M79 and `analysis-reuse.md` §6.16 (the world
> resolve), M101 (the post passes, the const cache), M56/M57 (the entry's
> share; the differential's blind spot), M105 and `performance-gates.md` (the
> gates and the ruled optimization order), M106 (cost-based suggestions), M107
> (the superlinear passes), E121 and `editor-latency.md` (the latency mandate),
> `opaque-returns.md` (ruled; it narrows what a body edit leaks).

## 0. The ask, and the answer up front

The owner asked: *"why does this happen per-keystroke? Ideally, a document
change would recalculate against the known graph where only specific areas are
invalidated (depending on what changed)."*

**Why it happens.** Four facts, in order of how much they cost today.

1. **It is per pause, not per keystroke, but every pause pays for the whole
   entry.** The server waits 150 ms after the last edit (`DEBOUNCE_MS`,
   editor-46's `vilan-lsp/src/main.rs:56`), then runs one analysis of the edited file's
   entry world (M104), and cancels it at the next checkpoint if another edit
   arrives (M26). What it runs is the whole pipeline: load and walk every
   module, resolve the world, solve every constraint, run about sixty checks,
   then the whole-program passes, then the editor tables (§1).
2. **Since M104, the one reuse mechanism misses on almost every edit.** M19's
   reuse only works on a base-cache *hit*. A hit requires every loaded file
   except the entry to be byte-identical to the stored world
   (`analyzer.rs:66657-66666`). Under M104 the edited file is a *module* of the
   entry's world, not the entry, so the check fails, the world is rebuilt, and
   it is stored again (`analyzer.rs:66935`, a full clone) for the next edit to
   evict. Every edit outside the entry file now costs a cold client world:
   editor-46 measured 14.26–14.35 G instructions for `model.vl`, `views.vl` and
   the css file alike, about 1.3 s of CPU (§1.4).
3. **Nothing records what an answer depended on.** The analyzer's products are
   about 200 tables keyed by ids minted per *occurrence* in load order. Type
   inference is one constraint fixpoint over the whole world, not one per
   function. Four passes run in the *reverse* dependency direction (a callee's
   facts flow up to its callers). So nothing can say "this edit touched only
   these" (§1.3, §2).
4. **This language makes a body edit non-local more often than Rust does.** A
   body edit can change an inferred return type (37% of kolt's hand-written
   functions infer theirs, and 57% of the function bodies the owner has
   edited were in those). It can make every caller async, give every caller a
   hidden context parameter, change the element type of a module-level
   binding that sibling functions read, fail a `const` in another function,
   or make a browser entry reach a node-only call. An impl in a module the
   user never imported changes method resolution. Each of these is a probe
   that ran (§2).

**The answer.** The graph the owner describes is the right end state. It
cannot be reached by one rewrite without stopping the language for many
orders. A query system in the salsa style would have to replace the
per-occurrence type slots, the global fixpoint and the reverse passes all at
once (§3.1). It can be reached by **firewalls built inside today's pipeline**,
each of which ships a measured win on its own. Each one also introduces a
boundary that a query system would need anyway.

- **S0 — instrument (S).** An *interface fingerprint* per item (its resolved
  signature, its inferred return and its effects: async, contexts, platform
  requirement, mutation verdicts) and a *global-facts fingerprint* (impl
  headers, trait declarations, resource-ness), printed per analysis. This
  measures what a real keystroke invalidates, which nothing measures today.
- **S1 — hot-set worlds (M), the cheapest firewall.** Store the entry's world
  *minus* the edited module and the modules that import it, and re-walk only
  that hot set. M19's reuse becomes reachable again. On kolt the hot set is
  0.5–15% of the package's lines for every module except the generated lucide
  file (87%). The measured analogue is a `views.vl` keystroke before M104,
  when M19 still hit: 9.27 G against 14.35 G today, which is −35% (§4.2).
- **S2 — prefix tables (M–L)**, **S3 — seeded whole-program passes (M–L)**,
  **S4 — the const cache (M).** These take the passes M19 cannot reach (M99) off
  the unchanged part of the world. Together with S1 they are the path to
  E121's 500 ms (§5).
- **S5–S7 — the function firewall (spike, then L).** Item-level id windows,
  so an unchanged item keeps its ids across edits; the interface firewall, so
  importers are reused when the edited module's interface did not move; and
  per-item records, so a body keystroke re-checks one function. This is where
  the query model starts. It needs a spike before anyone sizes it (§3.3, §5).

**Find References stays whole-entry by construction.** Every slice keeps the
analysed world equal to the entry's whole world. Only the work done on it
changes (§4.5).

**No behaviour difference from a clean analysis** is gated, not argued. Every
slice runs a new *edit-replay differential*: corpus packages times scripted
edits, incremental against clean, comparing diagnostics, editor tables and
emitted JS byte for byte. A planted invalidation bug must turn it red. There
is also a `VILAN_INCREMENTAL=verify` mode for dogfooding on kolt (§6).

**The CLI gets the same graph.** `--watch` and HMR are long-lived processes
and get every slice directly. A cold `vilan check` gets it when the records
are persisted. The records are designed to be persistable from S0 on: no
`TypeId`s, no addresses, content keys only. The on-disk *world* stays where the
ruled optimization order put it. Per-module records also partition the checks
phase for parallel analysis (§7).

## 1. What an LSP analysis runs today

### 1.1 The pipeline, stage by stage

One analysis of the client world. Each stage is listed with what it reads,
what it writes and its scope. Numbers are thread-CPU milliseconds from one
`VILAN_PHASE_TIMING=passes vilan check` of kolt's client entry on 0.43.0, at
loadavg 7–11 (`phase-kolt-0430.txt`). They are inflated by load; read them as
shares.

| # | stage | site | reads | writes | scope | kolt client |
|---|---|---|---|---|---|---:|
| 1 | project context (E113 platform walk, manifest closure) | `document.rs:1874` (`resolve_project_context`) | `vilan.toml`, the `pkg::` import graph | platform, workspace | package | (LSP only) |
| 2 | parse + desugar the entry | `lib.rs:744`, `:835-837` (css, elements, lift) | entry text | tree | file | small |
| 3 | world: load + walk every module, macro registration and expansion | `analyzer.rs:67357` (`analyze_inner`) | every reachable file (parse cache; open buffers parse into owned allocations, M9) | entities, scopes, spans, constraints; ids minted in load order | whole world | load+walk 400 |
| 4 | `resolve_world` (imports, preludes, binder bounds, locals, types, conformance, divergence, contexts, **the constraint fixpoint**) | `analyzer.rs:55009` | the queues the walk filled | resolved names, type slots (mutated in place) | whole world | base 412 (fixpoint 387) |
| 5 | base cache: lookup (content-validated) or store (a clone) | `analyzer.rs:66644`, `:66915` | `BaseCacheKey`, every loaded file's hash | a stored world | whole world | — |
| 6 | entry walk, then `build()` = `resolve_world` again plus finalize | `analyzer.rs:69869`, `:69896`, `:54675` | the world, the entry | the same tables | whole world | build 18 |
| 7 | checks: Class A (reusable), B (coherence), C (instantiation-driven), D (tables), resources, drops, liveness | `analyzer.rs:69956-70700` | all tables | diagnostics, more tables | whole world | checks 771 |
| 8 | `post_analysis_passes`: impl admission, labels, **contexts + call graph**, **async inference**, view suspensions, drop rules, **platform colour**, **const pass**, contract hashes, init order, lifetime steers | `lib.rs:997-1219` | the finished `Program` | diagnostics, result tables, the tree rewrite (contexts) | whole program | post-passes 464 (const 222, contexts 106, async 78, platform 42) |
| 9 | editor tables: entity and field spans, `ReferenceIndex::build`, platform requirements, the landed walk (`capture_landed`), the completion index | `document.rs:1978-2043`, `:2172` | the program | per-document tables | whole program (references) / file | ~5% (editor-46) |
| 10 | further platform legs: one more full analysis per extra platform of a shared module | `document.rs:2057-2124` | — | diagnostics | whole world again | ×2 for `shared.vl` |
| (CLI) | emission walk, chunking, transform | — | — | JS | whole program | 398 |

The largest check passes in that run were `compute_resource_types` (235 + 54
ms), `check_generic_bound_satisfaction` (204 + 26),
`check_resource_generic_instantiations` (41), `infer_bumps` (35),
`check_container_resource_arguments` (35), the drop extents and capture plan
(34), `plan_resource_drops` (28), `compute_clone_sites` (25),
`check_resource_moves` (22) and `LastUse::compute` (20). The CLI printed
`reused 0/85`, because the CLI never hits.

### 1.2 Where a keystroke's instructions go (cited)

editor-46's callgrind of a client-world keystroke, on its tip:

| part | share |
|---|---:|
| `analyze_over_world` (stages 6–7) | 35.8% |
| `post_analysis_passes` (stage 8); const-eval alone 16% | 30.5% |
| `resolve_world` (stage 4) | 19% |
| `platform_color::check` | 3.2% |
| union-leg walk (now deferred to the idle clock) | 3.0% |
| `ReferenceIndex::build` | 1.8% |
| `capture_landed` | 1.6% |
| `refined_edges` | 1.5% |

Stages 3–8 are more than 90% of a keystroke, and every one of them runs over
the whole world.

### 1.3 What M19's reuse skips, and why it cannot reach the hot passes

M19 (`per-module-analysis-reuse.md`) reuses an unchanged module's work when
three terms hold (`analyzer.rs:69932-69986`):

1. the world came from a base-cache **hit**, so every module entity has the
   same id in the same window as last time (§2.1 of that paper);
2. the entry did not move the module's type slots (T0's dirty bit);
3. a checks record exists for this key and content.

A fourth term, M76's, applies when the world is entry-shaped: the module must
not reach the open file through `pkg::`.

What it then skips:

- **Class A**: thirteen checks routed through `reusable_entity`
  (`analyzer.rs:70147-70161`). Their diagnostics are replayed from a record.
- **Class D tables** (T1b) and the drop planner's enrolment (T1c).

What it cannot skip, and why:

- **Class B and C** (`analyzer.rs:70162-70183`): coherence and
  instantiation-driven checks. An entry impl can make a module's impl a
  duplicate, and an entry call can ground a module's generic. They keep running
  over every module. `check_generic_bound_satisfaction` is the largest
  (204 ms above).
- **`compute_resource_types`** (`analyzer.rs:70677`): its key space is the
  whole interned type table, and "an interned id is nobody's to own"
  (`analyzer.rs:30365-30379`, recorded as not restorable).
- **The fixpoint** (stage 4 on a miss, stage 6 always), and **every post pass**
  (stage 8). These are global by construction.
- **Anything at all on a miss.** Term 1 is a hit.

M99 measured the consequence on a full hit: `reused 53/53` still paid 96% of
`checks`. Before M104 that was the best case. After M104 it is out of reach,
which is §1.4.

### 1.4 What M104 did to it

M104 (ruled) analyses the edited file's *entry* once and serves every open
file of that world from it (`analyze_world`, editor-46 `main.rs:2053-2120`).
That removed the per-dependent sweep: with `model.vl` and three importers open,
settling fell from 41.61 G (4 analyses) to 14.70 G (1). But the entry is now
`client.vl`. The file being edited is one of its modules, so it is inside the
stored world, and `base_cache_lookup_locked` refuses the world because one
loaded file's content moved (`analyzer.rs:66657-66666`). It evicts it
(`:66706-66716`), the analysis builds the world cold, and `base_cache_store`
clones the whole world back into the cache (`:66935`). The next keystroke
evicts that clone in turn.

The cited numbers fit no other reading. Every edit converges on one cost,
which is a cold client world:

| edit (editor-46, kolt @984a1dfb) | base fe092e8d (own-file worlds) | tip (entry world) |
|---|---:|---:|
| `model.vl` alone | 2.37 G | 14.26 G |
| leaf `views.vl` | 9.27 G | 14.35 G |
| css file | 10.10 G | 14.25 G |
| `shared.vl` (two worlds) | 2.82 G | 17.50 G |
| `model.vl` + 3 importers open, all settled | 41.61 G | 14.70 G |

Only a keystroke in the entry file itself (`client.vl`) still hits. At the
reference machine's measured rate of about 11 G instructions per CPU-second
(`performance-gates.md` §2.4), 14.3 G is about 1.3 s of CPU, where E121's
diagnostics target is 500 ms (about 5.5 G).

This is not an argument against M104. The ruling was right, and it fixed the
owner's reported case. It means the reuse has to be re-keyed for the shape
M104 created, and that is S1.

## 2. What a typical edit really invalidates

### 2.1 Five kinds of edit, and how far each reaches

What a correct incremental analysis would have to redo for each kind of edit.
"Interface" means the item's resolved signature plus its inferred return type
plus its effects (§3.2).

| edit | must redo, at minimum | can reach further when |
|---|---|---|
| **body** of a function | that body's checks and its share of the fixpoint | its inferred return moves (i1); its effects move: async (i6), a context read (i2), a platform requirement (i5), a `bumps`/`borrows` verdict; it constrains a module binding's inferred type (i7); a `const` calls it (i4); it adds an instantiation of a generic, which runs that generic's instantiation-driven checks for the new arguments |
| **signature** (parameters, written return, generics, bounds) | the item, and every caller and every user of its type | always reaches the users. With no orphan rule it also reaches modules outside the import closure when the item is a trait member or an impl's |
| **import** line | the module's scope resolution, its prelude interaction, and its own checks | an `export import` re-export reaches importers; an `only`/selector changes impl admission (B318) for that file |
| **type shape** (struct/enum fields, variants, a trait's members) | every user of the type, every impl of it, and derive output (the derive re-expands) | always global through the impl table: the generated impls change it, and `declares_a_resource()` can switch the drop planner on for the whole program (`per-module-analysis-reuse.md` §4(2)) |
| **macro or derive input** (an item under `[derive]`, a `[service]`, a `macro {}` block) | the expansion (cached by content, M33), then whatever the generated items change | the generated items are impls or items, so usually the impl table, which is global |

### 2.2 The probes: body edits whose effect lands outside the body

Each probe is a before/after pair where only one function body changes
(`probes/run_all.out`).

- **i1 — inferred return.** `fun make() { 1 }` becomes `{ "one" }`. The error
  lands in `main` (`Expected i32, but got str instead`).
- **i2 — a context read.** `leaf()` gains `flavor.get()`. The coverage error
  names `leaf`, `middle` and `top`, three functions away from the edit, and the
  context pass gives each of them a hidden parameter.
- **i3 — impl visibility.** `user.vl` calls `foo.greet()` and never imports
  `impls.vl`. It checks clean while *main.vl* imports `impls.vl`. Remove that one
  line from `main.vl` and `user.vl` gets `Foo has no method 'greet'`. On 0.43.0
  there is still no orphan rule.
- **i4 — const.** `size()`'s body changes, and `main`'s `const size() * 2`
  fails (`const evaluation failed in 'size'`), with the error at `main`'s const
  site.
- **i5 — platform colour.** `label()`'s body starts calling `args_count()`.
  The browser entry now fails, and the error lands on `args_count`'s body,
  which nobody edited (`reachable from the entry: main → label → args_count →
  args`).
- **i6 — async.** `leaf()` starts sleeping. The emitted JS makes `leaf`,
  `middle` and the top level async, and threads a hidden `$a`/`$b` context
  argument through both callers' signatures.
- **i7 — a module binding's inferred type.** `mut items = [];` takes its
  element type from a `push` inside `add()`. Change that push to a string and
  the sibling `show(): i32 { items[0] + 1 }`, which neither calls nor is called
  by `add`, gets `Expected i32, but got str`.

i2, i5 and i6 are the reverse-direction passes. i7 is the global fixpoint:
inference crosses function boundaries through shared slots, not only through
calls. `Context<T>` takes its value type from its first `run`
(`spec/contexts.md` §8.1) for the same reason.

### 2.3 How often a body edit can move an interface

Static censuses (`census.py`, heuristic line patterns):

| | functions | inferred return | impls | blanket impls | module bindings, type inferred |
|---|---:|---:|---:|---:|---:|
| kolt, hand-written (28 files, 5.8k lines) | 256 | **95 (37%)** | 55 | 0 | 31 of 31 |
| kolt, generated `lucide` (18.2k lines) | 1,820 | 0 | — | — | — |
| std (71 files, 43k lines) | 2,411 | 523 (22%) | 638 | 48 | — |

kolt's view-building functions (`channel_component`, the modal builders,
`views.vl`, `sidebar.vl`, `login_page.vl`) all infer their return, and that is
where the owner types most. In the owner's own `wip` commits
(`edit-classes-kolt-wip.txt`), 294 function bodies changed under an unchanged
signature, and **167 of them (57%) were in functions with an inferred return**.

Commits are too coarse to stand in for keystrokes. Even the `wip` commits are
dominated by import churn from version migrations: 61% of (commit, file)
pairs touched an import. So this census bounds how often an interface *can*
move, not how often it *does*. S0 measures the second.

### 2.4 What is global no matter what the edit is

- **The impl table.** `impl_member_candidates` filters every impl in the loaded
  program by subject and by nothing else (i3). Blanket impls make the reach
  total.
- **Whole-program predicates.** `declares_a_resource()`, `option_enum_id`, the
  intrinsic resolution block that scans impls for std's lang types.
- **The constraint fixpoint.** One loop over every queued constraint in the
  world (`resolve_world`'s `fixpoint` stage, 79–96% of the pass per M73).
- **The four reverse passes.** `refined_edges` (dispatch per entry of a
  generic's owner), `thread_contexts` (rewrites the tree), `async_infer`
  (asyncness per instantiation), and the const pass (reverse reachability from
  `asset::emit`).

These are what every architecture below has to answer.

## 3. The candidate architectures, and what blocks each in this language

### 3.1 Door A — a dependency-tracked query system (salsa-style)

**The shape.** Memoized queries with recorded dependencies:
`parse(file)`, `item_tree(file)`, `signature(item)`, `infer_body(fn)`,
`impls_for(type)`, `check(fn)`, `const_value(site)`. An edit invalidates
`parse(file)`, and revalidation walks the dependency graph and re-executes
only the queries whose inputs moved. This is rust-analyzer's architecture, and
it is the graph the owner describes.

**What blocks it here.**

1. **Type slots are mutated in place and minted per occurrence.**
   `type_id_for_type` says so (`analyzer.rs:23507-23518`): "types are
   intentionally *not* interned … inference resolves a type *in place*". A
   query's result must be an immutable value that can be compared with last
   time's. Today's types are cells inside one analysis.
2. **Inference is one fixpoint, not one per body.** A query `infer_body(fn)`
   needs a body's inference to depend only on its inputs. i7 and `Context<T>`
   show bodies writing each other's slots through module bindings. Rust
   forbids that (module statics need written types). This language allows it,
   so `infer_body` would need a "module bindings' types" query that reads
   *every* body that constrains them.
3. **Four passes run backwards.** A query graph answers "callers depend on
   callees" naturally. Asyncness, contexts and platform requirements flow from
   callees to callers, and `refined_edges` flows from call sites into
   generics. Each becomes a fixpoint *query* over a strongly connected
   component of the call graph. That is possible (salsa supports cycles with
   fixpoint iteration), but each one is a reformulation, not a port.
4. **About 200 tables keyed by id, and about 1,400 id sites**
   (`analysis-reuse.md` §4; `per-module-analysis-reuse.md` §2.2: 97 of 123
   `Program` fields and 144 of 191 `Analyzer` fields carry an id). Two of them
   use raw id order *semantically*: `declaration_order` is the method
   resolution tie-break (`analyzer.rs:21394`), and the transformer's emission
   order sorts by id.

**Verdict.** It is the right end state and the wrong first step. Taken as one
step it is a new analyzer, XL, with the language frozen while it is built and
every behaviour re-verified at the end. **Rec: do not start it as a rewrite.**
Build the firewalls below so that each boundary they create is one this door
needs: the world prefix, the item interface, per-item records, seeded
fixpoints. Then decide after S4 is measured whether the remaining gap is worth
the rest (Q1).

### 3.2 Door B — firewalls inside today's pipeline (recommended)

A firewall is a point where a cheap comparison proves that everything past it
is unchanged. Four of them fit today's pipeline, cheapest first.

1. **The world prefix (S1).** Ids are monotone in load order, and a world
   cloned from the base cache keeps every module entity at the same id
   (`per-module-analysis-reuse.md` §2.1, proved and pinned). Anything that loads
   *before* the edited module, and does not import it, is a prefix that need not
   be re-walked or re-resolved. Today the prefix ends just before the entry. S1
   moves its end to just before the **hot set**: the edited module plus every
   module that imports it, transitively, closed over import cycles. Global
   facts the hot set can still change (its impls, its resource declarations)
   are covered by the machinery that already guards the entry's: the dirty bit
   for type slots, and Class B and C re-running.
2. **Prefix tables (S2).** Tables over the prefix whose inputs are entirely in
   the prefix can be stored with the world: resource classification of prefix
   type ids, the instantiation-driven checks at sites in clean modules, liveness
   and clone sites of clean bodies, the reference index's prefix rows. They are
   reused when the dirty bits are clear **and** the global-facts fingerprint is
   unchanged. Only the suffix is computed. This is M99's answer.
3. **Seeded fixpoints (S3).** The contexts, async and platform passes are
   monotone fixpoints over the call graph. Seed each from the stored world's
   settled result and iterate only from the hot set's nodes and what reaches
   them. This is `per-module-analysis-reuse.md`'s T2, never built.
4. **The interface firewall (S6).** If the edited module's interface
   fingerprint and the global facts are unchanged, its importers' work is
   reusable. Under today's ids it is not: importers load after the edited
   module, so their ids shift when it grows. That makes this door depend on
   Door C.

**What blocks it.**

- **Inferred returns and opaque returns** are handled by putting the inferred
  return *in* the interface fingerprint. A body edit that leaves the inferred
  type alone stays local. Once opacity lands (`opaque-returns.md`, ruled), a
  `fun f(): Trait` exposes only the trait plus what §2.6 of that paper says
  still leaks, so annotated component functions become firm firewalls.
- **Effects** (async, contexts, platform requirement, `bumps`/`borrows`) go in
  the fingerprint too (i2, i5, i6).
- **Module bindings with inferred types** (i7): their resolved types are part
  of the *module's* interface. A body edit that moves one fails the firewall
  for every reader.
- **Blanket impl selection and the missing orphan rule:** the global-facts
  fingerprint (impl headers, where-clauses, member signatures, and the impls
  derives generate). A body edit inside an impl method does not move it.
- **Monomorphization:** emission only. For diagnostics the instantiation-driven
  checks are per call site. A body edit that adds a call site adds checks at
  that site, which is inside the hot set.
- **`refined_edges`** depends on every call site of a generic's owner. With
  S1 it is recomputed for hot-set sites against the world's settled answers,
  and it is already memoized on the resolved `Type`.
- **The context pass rewrites the tree** (deletes and mints call edges,
  `lib.rs:974-996`). Seeding has to replay the world's rewrite onto the clone,
  or keep the rewrite as a table instead of a mutation. The second is cleaner,
  and S3 has to choose.
- **Const-eval:** results keyed by content (S4).
- **Macro expansion:** already content-keyed and on disk (M33). Expansion
  output feeds the impl table, so it is covered by the global-facts
  fingerprint.
- **Platform colouring:** requirement summaries are effects, so they are in the
  fingerprint. Reachability from the entries is recomputed, which is a cheap
  graph walk. M104's further legs (`shared.vl` pays two worlds) each get their
  own hot-set world.
- **Stable ids across edits:** S1–S4 need none beyond what the clone already
  gives, because the hot set is re-walked whole. S5 onwards needs them.

### 3.3 Door C — finer reuse of today's tables by id windows

**The shape.** Today ids are dense: each walk continues from the last id. A
*window* gives each item (or each module) its own id range with slack after
it. An edit inside item *k* re-mints only ids inside *k*'s window, so every
other item keeps its ids, and every id-keyed table row for it stays valid if
its inputs did not move. Order is preserved (windows are laid out in load
order), so `declaration_order` and the transformer's sorts are unchanged. The
earlier papers considered pair ids and content-hash ids and refused both
(`per-module-analysis-reuse.md` §2.2). Neither of them is this.

**Why it is plausible.** The tables are hash maps keyed by id
(`type_id_to_type_map: HashMap<TypeId, Type>` at `analyzer.rs:4857`,
`entity_map: HashMap<Id, …>` at `:61114`), so gaps cost nothing. Only three
places assume density, and each can be fixed:

- two loops that iterate an id range densely (`analyzer.rs:16185`, `:62196`);
- `type_id_sources`, a `Vec` indexed by `TypeId` (`analyzer.rs:23501`).

**What blocks it.** Type ids are minted in two places. The walk mints them in
item order, so they window cleanly. The *fixpoint* mints them in fixpoint
order, interleaved across items. Windowing those means every `new_type_id`
inside the solver must know which item it is minting for (the constraint's
anchor). The analyzer already tracks the current *source* for diagnostic
attribution (`set_current_source`). Tracking the current *item* everywhere the
solver mints is a deep change, and an error in it shares slots between items:
exactly what B77 and B95 established must never happen.

There is also the TypeId boundary law (`editor-latency.md` §3.6): no `TypeId`
may cross a record. An importer's resolved types today embed `TypeId`s minted
inside the module it calls. Windows keep those ids stable for an *unchanged*
item, which is the point. They do nothing for an item that changed.

**Rec: a spike before any build (S5).** Window the walk's ids per item. Make
the three density sites sparse. Stamp the fixpoint's mints with the anchor
item. Then run the existing corpus differential with windows forced on. If it
is byte-identical, S6 (the interface firewall) and S7 (per-item records) are
buildable. If not, the spike's red cases are the design input.

### 3.4 What each door buys against the targets

| target | A (queries) | B (firewalls S1–S4) | C (windows + S6–S7) |
|---|---|---|---|
| E121 diagnostics < 500 ms (≈ 5.5 G) on kolt | yes | likely; S1 alone measured analogue −35%, S2–S4 estimated (§5) | yes |
| a body keystroke re-checks one function | yes | no: it re-checks the hot set (≥ 1 module plus its importers) | yes (S7) |
| E121 keystroke path < 10 ms | unchanged: the path never type-checks | unchanged | unchanged |
| Find References whole-entry | by query over the entry | by construction (the world is the entry's) | by construction |
| behaviour identical to a clean analysis | re-verify everything once | per slice, by the differential | per slice, by the differential |
| size | XL, all at once | M, M–L, M–L, M; each ships | spike S–M, then L, L |

## 4. The cheapest firewall: hot-set worlds (S1)

### 4.1 The design

- **The key.** `BaseCacheKey` gains the hot set: the canonical paths of the
  edited module, every module that imports it within the entry's world, and
  the import cycles they sit in. The key already has a precedent for naming
  an excluded module: `entry_open_module` (M70, `analyzer.rs:65435-65466`).
- **The store.** The world is built and stored **without** the hot set's
  modules. The prefix is loaded, walked and resolved. Then the hot set is
  loaded, walked and resolved into the clone, the way the entry is today.
- **The hit.** The next keystroke in any hot-set module has the same key. The
  prefix's contents are validated as today, and they are unchanged by
  construction because the edit is in the hot set. It clones, walks the hot
  set, and M19's reuse applies to every prefix module (terms 1–3).
- **What changes for M19.** Term 1 becomes "a hit on the hot-set key". Term
  2's dirty bit and M76's alias census already treat the post-store region as
  suspect. The hot set *is* the post-store region, so both apply unchanged.
- **The alias case.** A prefix module that imports a hot-set module cannot be
  in the prefix. That is what the hot set's closure means, and it is why the
  closure is taken over the reverse import graph.

### 4.2 How big the hot set is on kolt

`hot_set.py` over kolt's client world (27 package modules, 23,755 lines, plus
std):

| edited module | hot set (modules) | hot-set lines | share of package lines |
|---|---:|---:|---:|
| `client.vl` (the entry) | 1 | 118 | 0.5% |
| `views.vl` | 2 | 355 | 1.5% |
| `login_page.vl` | 3 | 630 | 2.7% |
| `command_palette.vl` | 3 | 674 | 2.8% |
| any of the seven-module cycle (`app_context`, `app_overlay`, `channel`, `prefs`, `sidebar`, `styles`, `theme`) | 11 | 2,568 | 10.8% |
| `model.vl` | 12 | 2,753 | 11.6% |
| `shared.vl` | 14 | 3,183 | 13.4% |
| `lib::search.vl` | 13 | 3,581 | 15.1% |
| `lucide/lib.vl` (generated) | 12 | 20,769 | 87.4% |

std is in the prefix for every row. lucide is in the prefix for every row but
its own, and it is generated (`generated = "src/lucide"` in kolt's manifest),
so nobody types in it. kolt's seven-module import cycle sets the floor for
most files. That is an observation about kolt, not a defect.

### 4.3 What S1 is expected to buy, and what it is not

The measured analogue is the pre-M104 numbers, when each open module was its
own entry and M19 hit: `views.vl` 9.27 G against 14.35 G today (−35%), and the
css file 10.10 G against 14.25 G (−29%). S1 gives back that reuse inside the
entry world, which pre-M104 analysis did not have. So expect roughly **−30% to
−35%** on every kolt edit outside lucide and the entry. Not more, because M99
holds: the hot passes still run over the whole world. That ceiling is why S2
and S3 exist.

What S1 also removes is the per-keystroke store. Today every edit clones the
whole world into the cache (`analyzer.rs:66935`) for the next edit to evict.
Under S1 the stored world does not contain the edited file, so it survives the
edit. Its cost is not measured (find 1).

### 4.4 Gates for S1

- The **edit-replay differential** (§6): the hot-set path against a clean
  analysis, byte-identical.
- M19's existing corpus differential (`check_scope_differential.rs`) with the
  hot-set key forced on.
- **Counter pins** (M105 S5's `VILAN_COUNTERS`): a `views.vl`-shaped keystroke
  re-walks 2 modules; a cycle member re-walks its cycle plus importers; a
  keystroke in the entry re-walks 1. Each pin is proven non-vacuous with a
  planted "hot set = whole world".

### 4.5 Find References under S1

The analysed world is still the entry's whole world. Only *how* it is built
changes. `ReferenceIndex::build` sees every module, so references and rename
stay whole-entry, which is the owner's condition on the M104 hybrid. S2 may
split the index into a prefix half (stored with the world) and a hot-set half
(rebuilt). The query answer is their union, and the differential compares the
index too.

## 5. The staged path

Each slice ships a measured win, or a measurement that stops the next one.
The instructions column is an **estimate** unless marked measured: none of
S1–S7 can be measured without building it. The starting point is editor-46's
14.3 G for a non-entry keystroke on kolt, and E121's target is about 5.5 G.

| slice | what | size | expected (kolt, non-entry keystroke) | basis |
|---|---|---|---|---|
| S0 | interface + global-facts fingerprints; `[vilan phase] hot-set n/m interface-moved k global-moved b`; a scripted kolt session (ten keystrokes in each of `views.vl`, `theme.vl`, `model.vl`, a css block) reporting per edit what moved | S | unchanged | — |
| S1 | hot-set worlds | M | ≈ 9–10 G (−30–35%) | measured analogue: pre-M104 `views.vl` 9.27 G and css 10.10 G with M19 hitting |
| S2 | prefix tables: resource classification, Class B/C at clean sites, liveness and clone sites, reference-index prefix | M–L | checks phase toward the hot set's share; estimate 6–7 G | the checks phase is 771 of ~2,065 ms analysis CPU in the CLI split; its four largest passes are 520 ms |
| S3 | seeded contexts / async / platform passes | M–L | estimate 5–6 G | contexts + async + platform are 226 ms of the post passes |
| S4 | the const cache: a result keyed by its site's content, the content hashes of its callee closure, its tracked input files and std's stamp | M | −16% of what remains; estimate 4–5 G, **inside E121** | editor-46: const-eval 16% of a keystroke; the CLI split puts const-interp at 186 of 222 ms |
| S5 | spike: item-level id windows (§3.3) under the corpus differential | S–M | none; a yes/no | — |
| S6 | the interface firewall: importers reused when the edited module's interface and the global facts did not move | L | a body keystroke re-walks one module; estimate 2–3 G | the hot set shrinks from 11 modules to 1 for a cycle member |
| S7 | per-item records: a body keystroke re-checks one function | L | estimate floor ≈ clone + one body + the seeded passes | — |

**The decision points.** Stop after S4 if E121 is green on kolt at two seals
(the ruled rule from M105). Do S5 only if the owner wants the "one function"
target for its own sake, or if a larger app shows S1–S4 are not enough. S5 is
a spike so that this decision is made on evidence.

**Order against the ruled optimization order** (M105: M103 → M104 → M107 →
M101 → allocator probe → M100 → on-disk world cache → parallel analysis).
S0–S1 sit naturally after M104, because they repair its reuse. S2–S4 *are*
M101 (S4 is its const cache) and M99. S5–S7 sit with "parallel analysis"
near the end, because they share its prerequisite, which is independent
per-item work.

## 6. Proving "no behaviour difference from a clean analysis"

Every slice lands behind the same gate. The gate exists before the first
reuse does.

1. **The edit-replay differential (new, built in S0).** For each corpus
   package (the examples, the generated kolt-shaped app from M105 S4, and
   multi-module fixtures written for it), apply a scripted edit from each
   class in §2.1:
   - flip a body literal's type;
   - add a context read to a leaf;
   - add a sleep (async);
   - add a node-only call to a shared module;
   - push a different type into a module binding;
   - change a written return;
   - rename a field;
   - add an impl in an unimported module;
   - flip a derive;
   - add an import;
   - edit a `const` callee.

   Then analyse incrementally and cleanly. Compare diagnostics and warnings
   (message, span, attributed source), `entity_spans` and the hover/hint
   tables for every open file, the `ReferenceIndex`, and the emitted JS. All
   must be byte-identical. Each edit is also undone and compared again: the
   undo is where stale-cache bugs live.
2. **Non-vacuity.** Each slice plants the bug it guards against (omit impl
   headers from the global-facts fingerprint; omit async from the interface;
   skip the hot set's reverse closure). The differential must turn red. M57 is
   the lesson: a differential whose corpus never exercised the seam stayed
   green over a planted bug.
3. **`VILAN_INCREMENTAL=verify` in the language server.** After each
   incremental analysis lands, run a clean one in the background and log any
   difference with the edit that produced it. This is the dogfooding mode for
   the owner on kolt, off by default.
4. **Counters, not timings, in the normal gate** (M105's tier 1): modules
   re-walked per edit, functions checked per edit, records replayed. Timings
   live at the seal (tier 3).
5. **No special case for a broken body.** A keystroke that leaves a body
   unparseable can move its inferred return to an error type. The firewall
   treats that as a change, because a clean analysis would see the same
   thing. S0 measures how often it happens mid-typing (Q10).

## 7. The CLI: the same graph, persisted and parallel

- **`vilan run --watch` and HMR** are long-lived processes. Every slice
  applies directly: the round's edited file defines the hot set. M22 (watch
  recompiles every leg) and M19's original HMR complaint are the same problem.
  Emission (398 ms of kolt's client check) is the next cost there, and it is
  out of scope here.
- **A cold `vilan check`** pays load+walk and base (about 812 of about 2,065
  analysis ms in the split above) before any record can help. The world cannot
  be written to disk as it is. It holds per-process addresses: 229 fields, 46
  borrowing `'src`, `&str` into leaked parse-cache texts (`analysis-reuse.md`
  §6.15). So the on-disk *world* stays where M105 ruled it: step 7, its own
  build.
- **The records persist from day one.** S0's fingerprints, S2's prefix tables
  and S4's const results are content-keyed and carry no `TypeId` and no
  address: the law `editor-latency.md` §3.6 already enforces for M19's records.
  Persisting them is a serialization slice, beside M33's on-disk expansion
  table, which is the precedent. With the on-disk world in place, a cold check
  after a one-file edit becomes a hit on a hot-set key: the same graph,
  persisted.
- **Parallel analysis.** Per-module records partition the checks phase (the
  largest, 771 ms) by source, and the hot set and the prefix are independent
  until the fixpoint. That is the shape `performance-gates.md` §7.3's Amdahl
  estimate assumed (×1.8–2.5 wall on 8 cores within an entry). The fixpoint
  stays serial until S5–S7 make it per item.

## 8. What could not be measured without building

- **What a real keystroke invalidates.** No recorder exists. The censuses in §2
  bound what *can* move; S0 measures what *does*.
- **S1–S7's numbers.** S1's figure is a measured *analogue* (pre-M104 reuse),
  and the rest are estimates from phase shares.
- **The per-keystroke base-cache store under M104**, its clone plus
  `base_cache_world_bytes`. It is visible in a callgrind of the tip and not
  measured (find 1).
- **The hit's own cost**: the world clone and the re-read and re-hash of every
  loaded file (`per-module-analysis-reuse.md` T3). It sets S7's floor.
- **Whether Class B/C prefix records are sound under the hot-set shape.** That
  is T0's dirty-bit census re-run on a hot-set world, which is part of S2.
- **Any LSP timing.** I ran no language server. Every LSP figure here is
  editor-46's or perf-b-45's, at loadavg 5–16.

## 9. Finds, for the integrator to file

Written to `sweeps/order46/newitems46-papers-b.json`.

1. **M?1 — since M104, a keystroke in any module of an entry world misses the
   base cache and re-stores the whole world.** The lookup refuses a world when
   any loaded file other than the entry changed (`analyzer.rs:66657-66666`).
   Under M104 the edited file is such a module, so every edit evicts the stored
   world, rebuilds it cold and clones it back (`:66935`). The next edit evicts
   it again. M19's reuse is unreachable for every edit but the entry's.
   editor-46's numbers converge on 14.26–14.35 G for `model.vl`, `views.vl`
   and the css file alike. Measure the store's share in a callgrind of the tip.
   The fix is S1, but a stop-gap that skips the store when the open buffer is
   inside the world is XS. Sizing XS (stop-gap) / M (S1).

## 10. Open questions, each with a recommendation

- **Q1. The strategy.** **Rec:** firewalls inside today's analyzer (Door B),
  each slice measured; no query-system rewrite now. Each boundary is built so
  that Door A can adopt it. Revisit after S4 (§3.1, §5).
- **Q2. S1's hot set.** **Rec:** the edited module plus its reverse import
  closure within the entry's world, closed over import cycles; the rest is the
  stored prefix. One world per (entry, hot set), under M24's existing budget
  (§4).
- **Q3. The gate.** **Rec:** the edit-replay differential, with a planted
  regression per slice, blocking for every slice from S1 on; plus
  `VILAN_INCREMENTAL=verify` for dogfooding on kolt (§6).
- **Q4. Inferred returns.** **Rec:** no language change. The inferred return
  and the effects go in the interface fingerprint. M106 may later *suggest* an
  annotation on an exported function whose inferred return keeps moving, as an
  info hint (§3.2).
- **Q5. The const cache key** (`const-eval.md` §4's open question). **Rec:** the
  site's own content, plus the content hashes of every function in its callee
  closure (from the call graph), plus its tracked input files, plus std's
  stamp (S4).
- **Q6. The function firewall.** **Rec:** a spike (S5) after S4 is measured.
  Build S6–S7 only if E121 is still red, or the owner wants the one-function
  target for its own sake (§3.3).
- **Q7. Persistence.** **Rec:** every record is content-keyed and
  `TypeId`-free from S0, so the CLI's cache is a serialization slice. The
  on-disk world stays at step 7 of the ruled order (§7).
- **Q8. A body edit that moves an effect.** **Rec:** async, contexts, platform
  requirement and the `bumps`/`borrows` verdicts are all in the interface. Any
  change re-checks the item's callers' hot set, never a guess (§2.2).
- **Q9. Counters for the gate.** **Rec:** modules re-walked, functions checked
  and records replayed per edit join M105's tier-1 counters, with pins per
  slice (§6).
- **Q10. Broken bodies mid-typing.** **Rec:** no special case. S0 reports how
  often an inferred return goes to an error type between keystrokes; if it is
  common, the cost is visible and the owner decides with the number (§6).

## 11. Slices

| slice | content | size | gate | what exists |
|---|---|---|---|---|
| S0 | interface fingerprint per item (canonical resolved signature, inferred return, effects) and global-facts fingerprint (impl headers, trait members, resource-ness, generated impls); the `hot-set`/`interface-moved` phase line; the scripted kolt session; the edit-replay differential harness, running clean-vs-clean | S | the harness green on itself | `VILAN_PHASE_TIMING`, M19's records, `check_scope_differential.rs`, E126's exhibit generator |
| S1 | hot-set worlds: the key, store without the hot set, walk it over the clone, M19 terms re-pointed | M | edit-replay differential; counter pins; planted whole-world hot set red | `entry_open_module` (M70), M76's alias census, T0's dirty bit |
| S2 | prefix tables (resource classes, B/C at clean sites, liveness and clone sites, reference-index prefix), gated on dirty bits and the global-facts fingerprint | M–L | differential; planted fingerprint omission red | T1b/T1c's record law |
| S3 | seeded contexts / async / platform fixpoints; the context rewrite as a table | M–L | differential (emitted JS is the assertion for contexts); a "one seeded pass" counter | `refined_edges`' memo; T2's sketch |
| S4 | the const cache by callee-closure content | M | differential with const edits; a hit counter | M33's content-keyed expansion table |
| S5 | spike: item-level id windows, sparse density sites, anchor-stamped fixpoint mints, run under the corpus differential | S–M | byte-identical or a list of red cases | `source_ranges`, `seal_frozen_ranges` |
| S6 | the interface firewall over windowed ids | L | differential; a "body edit re-walks one module" pin | S0, S5 |
| S7 | per-item records: a body keystroke re-checks one function | L | differential; a "functions checked = 1" pin | S6 |

S0 and S1 go first, and S1 should follow M104's merge directly: it repairs the
reuse M104 removed. S2–S4 are M101's and M99's work under one gate. S5 is
decided after S4 is measured.
