# The std prefix — std analyzed once per toolchain build and loaded by every process (M120 door (b), M36 §6.15, N157, E292 door (c))

> Status: **DRAFT 2026-10-10 — for the owner's ruling (Q1–Q12).** Written by lane papers-50 of
> Order 50 against `vilan 0.47.0 (5fe24f868)` = `origin/next` @5fe24f86, read in
> `vilan/.claude/worktrees/integration`. Nothing in the vilan tree, kolt or the website changed.
> Every claim about today's behaviour is a probe that was run or a line that was read, and says
> which. Instructions are `scripts/perf_count.py`'s `instructions:u` (three runs each, spread
> under 0.01%); CPU milliseconds are `VILAN_PHASE_TIMING=passes` medians of three at loadavg 4–9
> (other lanes were building), so the CPU columns are for SHARES and the instruction column is the
> number. kolt is a `cp -r` copy of the owner's working tree carrying `src/lucide` and
> `src/search-dict`.
>
> Probes, tools and raw output: `scripts/integration/sweeps/order50/papers-50/probes/`
> (`programs/` the five probe packages, `tools/` the census scripts, `out/` every run cited).
> Finds and their repros: `papers-50/finds/`, filed to `newitems50-papers.json`.
>
> Related: M120 (the std growth tax; door (b) is this paper), M36 and `analysis-reuse.md` §6.15
> (the 2026-09-07 spike: "the world holds per-process ADDRESSES"), N157 (one std world per test
> process), E292 (the true E121 rows; door (c) the server leg), M110 and
> `incremental-analysis.md` (§7 sketched the persisted form; S6's windows are this order's
> incr-50), `analyzer-pass-map.md` (§3 the passes; §4.1 the post-settle mints, M134), M19 and
> `per-module-analysis-reuse.md` (the records), M121/B553 (the reach record), S4's
> `const_cache.rs`, M33 (the on-disk expansion table — the one cross-process cache that exists),
> M67/M24/M50 (the base cache's budget), B422 (std roots in the key), spike-49's final report.

## 0. The ask, and the answer up front

**The ask.** Analyze std ONCE per toolchain build and LOAD it in every process: a cold
`vilan check` stops paying its std floor, every nextest process stops re-analyzing std (N157),
and kolt's server leg stops re-analyzing std on every pause (E292 door (c), M120's +17% on
that row at v0.47.0).

**The answer.**

1. **std is most of a small program and two thirds of kolt's server leg** (§1.1). An empty web
   program is 1.37 G instructions and all of it is std (an empty node program is 0.24 G and is
   std too: a program that does not even parse pays it). Of kolt's legs, std alone — the same
   std modules with no package code — is 2.36 G of the client's 11.09 G (21%) and 2.22 G of the
   server's 3.39 G (66%).
2. **The ceiling of a persisted world is the in-memory hit, and the hit removes 53% of std**
   (§1.2). Measured as a second analysis in one process: std's load, walk and base resolve go,
   its Class A checks replay — and its checks tail and post passes (47% of std's cost) run again
   on every analysis, hit or not. A persisted prefix buys the 53% in every process; the 47% is
   M134/S7's (std bodies never re-checked), not this paper's.
3. **The blocker is not the serializer.** After the walk the analyzer runs on its own IR, not on
   ASTs: every address-keyed structure §6.15 named (the three macro maps, the registry's anonymous
   blocks, the generated-item trees) is read ONLY by the walk (`analyzer.rs:38806`, `:38837`) and
   is dead once std has walked; the AST-pointing tables that live on (`span_map`, 57,356 rows of
   `&'src Span` on kolt's client std; six check queues drained after the store) can hold the
   `Span` by value or be pre-drained for std; strings can borrow from the file. What blocks a
   cross-process std world is that **std's ids are not a function of std** (§1.4): on kolt's
   client std's 55,693 entity ids are cut into at least nine runs by package ids, 5,632 of them
   minted after 81k package ids, because the canonical drain loads a std module when a package
   module first asks for it. The same reachable set even emits in a different order depending on
   who imports it (find B603).
4. **So the prefix is defined by two rules and one guard** (§4): the canonical order becomes
   **std-first** (every std module of the closure minted before any package module — one
   emission reorder, no behaviour change), **std resolves alone** (package impls never answer
   std's own pre-entry lookups — already true of the entry's impls), and the **reach record**
   (M121) refuses the prefix when a package impl could have answered a question std asked. Then a
   std world is a pure function of (analyzer build, std content, platform, std module set), and
   S6's windows make its id layout a table the prefix carries (§3).
5. **The form** (§5): one file per (platform, std module set) — the analyzer's tables as flat,
   versioned rows per id lane, strings borrowed from the file buffer, derived indices and memos
   rebuilt or dropped, M19's records and S2's tables in the same file. Estimated 3.5–5 MB for the
   empty web program's std, 6–8 MB for kolt's client std; load 10–40 ms against 180–340 ms of
   analysis. **The key** (§6): format version × an analyzer source hash × std's content hash ×
   platform × the std module set (closure, not the entry's seeds) × macro limits.
6. **The doors** (§7). (a) A file beside the materialized std (`~/.vilan/std-cache/<hash>/`),
   written on the first miss: empty web 1.37 → ~0.7 G (−49%), kolt server leg 3.39 → ~2.4 G
   (−29%), client 11.09 → ~10.0 G (−9%), N157 ≈ 1,500–2,300 of the suite's 13,002 CPU-s (12–18%) —
   recommended. (b) A fork-server for nextest — declined: a custom harness for vilan-core's 39
   test binaries and the other crates' (L), and (a) reaches nextest unchanged. (c) The server leg
   in the LSP — **measured first: a quarter of the row is the base cache's budget**: the pause's
   two entry worlds evict each other under M67's 192 MiB (the server world rebuilt cold, std
   included, on 4 of 6 pauses); a budget that holds them takes the row from 14.54 to 10.76 G
   (x0.74, find E294). Then a pinned in-process std-only prefix (P1) makes every remaining miss
   skip std.
7. **Six slices** (§13): P0 std-first order (S, after S6 lands), P1 the in-process std-only
   prefix (M), P2 the LSP pins it + the budget (S), P3 the serializer (M–L), P4 the key and
   `vilan cache` (S), P5 the suite (S). P1 alone is the in-process half of N157 and door (c);
   P3–P5 are the cross-process half.

## 1. Ground truth (0.47.0)

### 1.1 The three measurements: std's share per pass

The probe for "std's share" is a package whose entry imports exactly the std modules a leg loads
and has no other code (`programs/kolt-std-client`, `programs/kolt-std-server`): the module SETS
were verified identical to kolt's (`ranges.py` over each `--debug` dump's `sources`), and the
std entity counts come out identical too (55,693 and 53,128), so std's walk does not depend on
the package. Columns are CPU ms; percentages are std's share of the leg's pass.

| pass | empty web (all std) | kolt client: leg / std alone | kolt server: leg / std alone |
|---|---:|---:|---:|
| load+walk (drain, expansion, walk) | 61 | 237 / 102 (43%) | 149 / 96 (64%) |
| base (pre-entry `resolve_world`) | 36 | 255 / 73 (29%) | 76 / 72 (95%) |
| build (entry walk, second resolve) | 3.4 | 20 / 6.4 | 11 / 6.6 |
| checks + extraction tail | 60 | 434 / 119 (27%) | 160 / 116 (73%) |
| post-passes | 15 | 404 / 33 (8%) | 64 / 27 (42%) |
| emission walk + program drop | 4.1 | 119 / 7.8 | 32 / 6.9 |
| **total CPU** | **180** | **1,469 / 341 (23%)** | **492 / 325 (66%)** |
| **instructions** | **1.371 G** | **11.091 G / 2.360 G (21%)** | **3.385 G / 2.224 G (66%)** |

Inside std's checks (kolt client's set, CPU ms): the extraction tail's remaining tables 18.1, drop
extents/shared cells/capture plan 13.4, `check_container_resource_arguments` 11.2, `infer_bumps`
9.8, `compute_resource_types` 9.3, `check_resource_generic_instantiations` 8.8, `LastUse` 8.6,
`compute_clone_sites` 8.0, `plan_resource_drops` 7.6, `check_resource_moves` 6.2. Inside std's
post passes: contexts + call graph 16.1, async 8.4, const 3.4, dispatch-refine 2.7
(`out/phase-table.md`).

Other floors, instructions: `vilan --version` 0.6 M; a program that fails to PARSE 0.240 G (std
is analyzed anyway); empty node program 0.2415 G; empty web program on node 1.238 G. perf-47's
"1.23 G of 1.48 G" is the web prelude's increment over the empty node program, whose 0.24 G is
std's base prelude: the whole floor is std.

### 1.2 What an in-memory hit already removes — the ceiling of a persisted world

`vilan check --watch`, the entry touched once: the second analysis is a base-cache hit (records
replayed for every std source). Its instructions are the difference of two runs
(`out/instructions.txt`):

| subject | cold | hit | the hit removes |
|---|---:|---:|---:|
| empty web | 1.397 G | 0.647 G | 0.750 G (54%) |
| kolt client's std alone | 2.401 G | 1.126 G | 1.275 G (53%) |
| kolt server's std alone | 2.261 G | 1.060 G | 1.201 G (53%) |
| empty node | 0.250 G | 0.099 G | 0.151 G (60%) |

Per pass (kolt client's std, CPU, in the watch process at a higher load than §1.1's): load+walk 152
→ 18 (the clone and the re-hash of 60 files), base 108 → 0, checks 146 → ~104 (Class A replayed),
build, post passes and the tail unchanged. So **a persisted world can buy at most 53% of std**,
minus what loading it costs; the other 47% is std's bodies walked again by the whole-program checks
tail and post passes on every analysis — the resource/bound passes M134 names, the rest of the
extraction tail, and the post passes S3 seeds. That half needs M134's anchors and S7's per-item
records with std frozen; it is §9's interaction, not this paper's build.

### 1.3 The server leg in the editor, measured (E292 door (c))

`lsp-latency.py --source <kolt copy> --scenario "leaf keystroke + pause"`, installed
`vilan-lsp 0.47.0`, five runs, the server's own `VILAN_COUNTERS` lines read per analysis
(`finds/pause_worlds_evict/`):

| budget | CPU to idle | instructions | server world (58 sources) | client entry world (89) |
|---|---:|---:|---|---|
| default (M67, 192 MiB) | 2,870 ms | 14.54 G | 4 misses, 2 hits | 4 misses, 2 hits |
| `VILAN_BASE_CACHE_BUDGET_MIB=4096` | 2,030 ms | 10.76 G | 1 miss, 5 hits | 2 misses, 4 hits |

The pause runs two union analyses, one per declared entry, after the keystroke's own (a hit on
`views.vl`'s world). Neither entry is LIVE (only `views.vl` is open), so M67's exemption does not
cover them; beside the live `views.vl` world the two entry worlds (74 and 37 MB resident by the
clone's heap, counted in M50's weighted currency by the budget) do not stay together — the misses
say so: each store evicts the other leg's world, and the next pause rebuilds it cold, std
included, which is two thirds of the server leg. **A quarter of the row is this** (3.78 of 14.54
G), and every eviction is priced at a cold world, std's growth included. Whether std's growth is
also what tipped the worlds over the budget between v0.46.0 and v0.47.0 (the seal's x1.17) needs
the base binary under the same two budgets — not run here. Find E294; the budget is P2's first
half.

### 1.4 What std mints, and in what order

From `--debug` dumps (`ranges.py`, `progcensus.py`; `out/`):

| | empty web | kolt client's std | kolt server's std |
|---|---:|---:|---:|
| std sources / text | 41 / 0.94 MB | 60 / 1.63 MB | 55 / 1.51 MB |
| std entity ids (+ std's own generated) | 35,695 (+818) | 55,693 (+1,327) | 53,128 (+1,327) |
| type slots at the store / after the analysis | 58,722 / 66,019 | 97,141 / 108,484 | 92,392 / 103,218 |
| post-settle mints (M134's) | 6,186 | 9,300 | 8,877 |
| scopes / functions / impls | 5,727 / 1,710 / 556 | 8,665 / 2,400 / 711 | 8,137 / 2,341 / 687 |
| resident world (the base cache's clone) | 20.9 MB | 35.5 MB | 34.2 MB |

The two legs share 53 std modules (1.43 MB of text); the client alone loads `browser/web/ui`,
`display`, `web::{dev, dom, router, storage, style::prelude}`, the server alone
`process/web/ui` and `web::document`. Std's post-settle mints are half of kolt client's 18,619.

**The order.** Three lanes are counters (`entity_id`, `scope_id`, `type_id`, `analyzer.rs:8012`,
`:25464`, `:25731`) plus `SourceId` and the macro site counter. The drain loads modules from a
min-heap on `load_order_key` (std tier 0, dependencies 1, package 2; `:77550`), but only among
the modules KNOWN so far (`:78871`): a std module first requested by a package module is loaded
after that package module, and module nodes are minted at load. On kolt's client:

- eight package module-node ids sit inside std's first 92 ids;
- std's 55,693 ids fall in at least nine runs separated by package ids; the last two runs
  (136,234–141,892: 5,632 ids — `rpc::server`, `http`, `fs`, `path`, `ws`, `build`, `db`, `memo`,
  `crypto`, `watch`, `process`, the `@process` modules package code asks for) come after the
  package's 81k ids (lucide among them);
- on the server leg, 3,982 std ids come after 594 package ids.

Type ids follow: the walk mints per item in this order, the fixpoint mints wherever the global
fixpoint happens to settle (spike-49: 2.9× the walk at p50, 54× at p99), the tail mints after
settle. **A std item's ids therefore depend on the package around it.** Programs reproduce their
own ids exactly across processes — the hasher is constant-seeded (`fx.rs`) and the goldens hold
ids in emitted bytes — but no two programs with different packages agree on std's.

Find B603 is the visible edge (repro `finds/load_order_by_import_site/`): a
package module imports `std::path`; adding a redundant `import std::path;` to the entry (the
reachable set unchanged) moves `pkg::a`'s function after std's in the emitted module. On kolt's
server, `import std::db;` in the entry reorders 18 lines of `server.mjs`. WO-1b's comment says the
order is "a function only of WHICH modules are reachable"; it is not.

### 1.5 The base cache's key, and why it is process-bound

`BaseCacheKey` (`analyzer.rs:74975`) carries: `platform`; `std_roots` (canonical paths, B422);
`std_seeds` (the ENTRY's sorted `std::` references, not the closure); `workspace` (rendered
dependency rows); `macro_limits`; `entry_prelude`; `entry_pkg` (root + sibling refs, M21);
`entry_open_module` (M70); `hot` (S1: the hot set's paths and the load requests its modules
write, as `&'static str`); `reach` (M121's filter). Every field is plain data. What is
process-bound is the VALUE and the map:

- `BASE_CACHE` is a `static` in memory; a `World<'static>` borrows the parse cache's leaked texts
  and ASTs, the display-name interner, leaked macro expansions, and (for overlays) M23's claims.
- The world is package-specific: it holds std AND every package module but the entry (or the
  hot set), so two programs never share one even when their std is identical.
- `std_seeds` keys by what the entry names, so two entries with the same std closure but
  different spellings mint two worlds; the docs gate's 279 analyses hit 166 times (N157).
- `CHECKED_CACHE` (M19's records), the const cache, macro `WORLDS`/`EXPANSIONS`/`PARSES`, the
  parse cache, `NAMES`, `HOT_*` and the fingerprints are sixteen more process-global statics; only
  M33's expansion table reaches the disk.

## 2. The blocker census

`tools/fields.py` over `pub struct Analyzer` (`analyzer.rs:4115–6270`), `World` (`:77230`) and
the types they hold; runtime rows from the `--debug` dumps of kolt client's std. §6.15 counted 229
analyzer fields; there are now **415**: 243 maps or sets, 264 mention `Id`, 88 `TypeId`, 41
`SourceId`, 69 carry `'src` (38 as a plain `&'src str`/`&'src Span` reference, 35 through a
`'src`-generic type), 4 hold `&'static str`, 3 are keyed by `usize` addresses, 4 are `RefCell`s, 2
hold an `Arc`. 103 types in vilan-core carry the lifetime; the 18 entity types the tables hold
(`Function`, `Scope`, `Struct`, `Trait`, `Implementation`, `Constraint`, `Expr`, …) carry 38
`&'src str` fields between them and **no AST node** — after the walk the analyzer runs on its own
IR (`expr_id_to_expr_map`, the entity tables), which is what makes the census short.

| # | class | where | std rows (kolt client's set) | read after the walk? | in the prefix |
|---|---|---|---:|---|---|
| 1 | AST address as key | `macro_item_invocations`, `macro_expression_expansions`, `macro_failed_sites` | 37 / 0 / 0 | **no** — only `walk_expr_node` (`:38806`, `:38837`) | dropped |
| 2 | AST address as key | `MacroRegistry::blocks_by_module`, `GeneratedItems::expressions` | 0 / 0 (std has no `macro { }` block, no expression macro) | only while expanding that module | dropped |
| 3 | leaked AST | `GeneratedItems::nodes` (World's `generated_by_source`) | 37 expansions (Wire 14, PartialEq 13, Storable 10, Debug 9, Json 4, Hashable 1) | the walk, and S1's hot guard (std's generated code names no `pkg::`) | dropped |
| 4 | compiled macro world | `MacroDef::world: RefCell<Option<Arc<World>>>` | lazily, on an M33 miss | yes, to expand a package derive | skipped; recompiled on demand (the rest of `MacroDef` is owned data) |
| 5 | pointer into an AST | `span_map: HashMap<Id, &'src Span>` | 57,356 | yes (diagnostics, labels, notes) | a `Span` by value (8 bytes either way) — a mechanical tree change |
| 6 | pointer into an AST | six `*_to_check` queues of `&'src Node` rows (`WireTypeCheck` for wire/hashable/partialeq/json, `RpcSignatureCheck`, `ExposeFieldCheck`) | std's derive items | yes — drained AFTER the store (`:81106` vs `:80505`), so every hit re-runs std's Wire/Json/rpc boundary checks | pre-drained for std (their only output is diagnostics; std is diagnostic-clean by the frozen-source seam) |
| 7 | `Spanned<&'src str>` | `module_platforms` | 13 fenced std modules | yes | strings borrowed (row 8) |
| 8 | `&'src str` | 38 fields, the entity types, every `Scope`'s bindings | most rows | yes | borrowed from the file buffer (`#[serde(borrow)]`); the analyzer compares strings by content — its only pointer-identity uses are rows 1–2's casts |
| 9 | `&'static str` | `primitive_struct_ids` keys, `prepped_conditions`, `asset_channel_fns`, suspension signatures | ~50 | yes | content, interned on load |
| 10 | derived index | `source_range_index`, `derived_origin_index`, `tuple_member_index`, `impl_reach` (`RefCell`s); `member_row_index`, the impl head rows | rebuildable | yes | rebuilt (they already build "if needed") |
| 11 | memo | `bound_proof_memo`, `bound_provider_memo` (`Arc`), M123's, `impl_select`'s | — | yes | dropped |
| 12 | shared value | `impl_namespaces: Vec<Arc<ImplNamespace>>`, `TupleLabels(Arc<[Box<str>]>)` | small | yes | content |
| 13 | id lanes | `Id`, scope ids, `TypeId`, `SourceId`, the macro site counter | 55,693 / 8,665 / 97,141 / 60 / 37 | everything | **reproduced exactly** — needs §4's std-first order |
| 14 | paths | `sources: Vec<PathBuf>`, `std_layer_sources`, `MacroDef::file` | 60 | yes | re-rooted on load (B422) |
| 15 | per-analysis | phase marks, `overlay_claims`, live entries | — | — | never stored (a world with overlays is refused, §6.15's rule) |

**What remains hard is row 13 and nothing else of the 15.** Rows 1–3 are dead data once std has
walked; 4, 10, 11 are caches; 5–9, 12, 14 are a serializer's ordinary work. §6.15's decision
("blocked on (1)–(4), each a change to how the macro engine identifies its own sites") assumed the
stored world would be walked again; a std prefix never is.

## 3. What S6's windows give, and what they do not

S6 (incr-50, this order; spike-49 proved it on every leg) lays ids out in per-item WINDOWS in load
order: an item's walk mints, its anchored fixpoint mints and (after M134) its tail mints live in
its own range, entity windows at 1.5× the walk, type windows sized from the item's previous demand,
`writes_other == 0` pinned.

- **What it gives the prefix.** (1) Within std, an item's ids stop depending on its neighbours'
  fixpoint traffic: the fixpoint no longer interleaves std items' type ids. (2) The layout becomes
  DATA — a window table (item → entity base/size, type base/size) — which the prefix carries, so a
  loaded std is laid out by the table, not re-derived. For std the demand is exact (the prefix's own
  analysis), so std's windows need no slack. (3) `writes_other == 0` is the statement that no
  package constraint rewrites a std slot: a loaded prefix's type rows are immutable after load,
  which is what lets one loaded prefix serve several worlds and, later, be shared structurally.
  (4) The run-length `type_id_sources` keeps the gaps free.
- **What it does not give.** Windows are laid out IN LOAD ORDER, and load order is §1.4's: std's
  windows still start wherever the package left the counters. Program independence needs the order
  itself to put std first (§4.1). With it, S6's table for std is a function of the std module set
  alone.
- **Which tables still need a fixup on load:** rows 10 (rebuild), 14 (re-root), the counters
  (`entity_id`, `scope_id`, `type_id`, the macro site counter continue from the prefix's ends — the
  S1 hot world already carries `macro_site_counter`), the global and `pkg` scopes (the package layer
  adds children, as `load_hot_modules` does), and the base cache's own entry (a loaded prefix is
  inserted as a stored world, so `--watch` and the LSP reuse it in-process).

## 4. The prefix, defined

### 4.1 Std-first (Q2)

The canonical drain finishes discovery before it mints: modules are parsed and their requests
followed as today (parsing mints nothing), then module nodes, `SourceId`s and the walk proceed in
`load_order_key` order over the COMPLETE reachable set — std (sorted), dependencies, package. This
is what WO-1b's comment already claims; B603 is the gap. Cost: one reorder of emitted declarations
for programs whose package modules discover std modules (single-file programs are unmoved: every
std import is an entry seed); no type, diagnostic or behaviour moves, and the permutation
differential holds the answers. The native backend's names carry ids (`vilan-rust/src/lib.rs:2391`)
and JS sorts functions by id (`transformer.rs:107`), so the corpus and native goldens regenerate
once (the reorder is the whole diff).

### 4.2 Std resolves alone (Q3)

Today the pre-entry `resolve_world` resolves std and the package modules in one fixpoint, so a
package impl on a FOREIGN subject (kolt has them: `impl View`, `impl Document`, `impl Style`,
`impl Store<Account>`, `impl Source<..>`) is visible to std's lookups. The entry's impls are
already not: "what std's lookups answer is std's to decide" (`ImplReachLog::asked_by_std`,
`analyzer.rs:306`), and B583 narrowed std's candidates to std traits. The prefix extends the
entry's rule to the package: std's world resolves first and alone; the package resolves over its
settled answers (S1's hot-set shape with the hot set = every package module). The guard is the
reach record as it exists: the prefix's resolve records std's questions; a package impl that could
answer one refuses the prefix and the analysis is built canonically, cold (M121's ruled behaviour
for an entry impl reached by a module). P1 measures how often that fires on the corpus, kolt and
the examples; the rule can harden from guard to language once it has held a release.

### 4.3 The key: the std module set (Q4)

The prefix is keyed by the std CLOSURE, not by the entry's seeds: (entry seeds ∪ every package
module's std requests) closed over std's own import graph, which is static per toolchain and ships
in the prefix index (60 or 55 rows for kolt). The package modules are parsed anyway; the closure
costs microseconds; two spellings of one std set share one prefix. A program whose std set has no
prefix builds one (cold, then written); a superset prefix never serves a subset program (extra
std modules can change answers — B598 is one).

### 4.4 Contents

The std-only world after its base resolve (the S1 store point with hot = every package module),
with: the window table; std's lang-item ids (about forty, set after the std walk from
`analyzer.rs:79933`); the macro registry's `by_module` (std's ~40 macro functions); the reach
record of std's own questions; M19's `WorldChecks` for std's sources (Class A diagnostics are
known-absent; the record is what makes them replay) and S2a/S2b's per-module tables (the
bound-audit questions, `expr_types`, `declaration_labels`); and the counters' ends. Not the ASTs,
not the parse cache, not the memos.

## 5. The serialization form

**Flat tables per id lane, versioned** (Q12). A header (format version, the key's fields in
clear, a checksum), a string table, then one section per lane: entities (`Id`-keyed rows by kind —
functions, variables, parameters, structs, enums, traits, closures, modules, scopes with their
bindings), expressions (`expr_id_to_expr_map`), types (the `TypeTable` as slot → tagged `Type`),
the residual constraint queues, the per-source records, the window table. serde is already a
vilan-core dependency (with `derive`); the derives go on the world's types with `#[serde(borrow)]`
on every `&'src str`, so strings point into the leaked file buffer and provenance never has to be
recovered (§6.15's "the tag is the work" disappears: the tag is the buffer). `indexmap`'s `serde`
feature is a feature, not a dependency; the binary format is ~300 lines in-tree (no bincode).

**Size, estimated from the counts** (not measured — §10): types ~8 bytes a slot (tag, a varint
id, an argument list) → 0.5 MB empty web / 0.8 MB kolt client's std; entity, scope and span rows
(entity_map 63,259, span_map 57,356, entity_scope_map 52,367, type_references 18,923, the scopes'
bindings) ~6–8 bytes each → 1.5–2.5 MB; labels 0.4 MB; records and the rest ~1 MB; std's text
(the string table borrows `source_texts`) 0.94 / 1.63 MB. **Total ≈ 3.5–5 MB for the empty web
program's std, 6–8 MB for kolt's client std** — against 20.9 / 35.5 MB resident, the usual 1:4–1:6
of a map-heavy heap.

**Load, estimated:** the in-memory hit's clone plus re-hash costs 4.4 ms (empty web) to 18 ms
(kolt client's std) of CPU; a decoder building the same maps costs 2–3× a clone → **10–40 ms**
(0.05–0.25 G), against 180 / 341 ms of analysis. For the materialized std the per-file re-hash can
go (the directory is keyed by `CONTENT_HASH` and complete by construction); for the tree's std
(tests) it stays.

The two alternatives, rejected: a **fixed-address image** (allocate the std world in an arena,
`mmap` it back at the same address) needs no field-by-field encoder but every pointer into the
binary (row 9) moves under ASLR, every allocation of the build must be routed to the arena, and it
does not port to Windows' allocation rules (L24) — L for less certainty. **Inputs only** (persist
parsed ASTs, re-resolve) buys the parse share, a fifth of the floor (§6.15).

## 6. The invalidation rule

The file name is the hash of, and the header repeats in clear:

1. **the format version** (bumped by hand, like `DISK_FORMAT`);
2. **the analyzer's build identity** (Q5): a hash of vilan-core's own sources computed by a build
   script, the `CONTENT_HASH` pattern of `vilan-embedded/build.rs`. Not `VILAN_BUILD_SHA`: that
   stamp lives in the cli/lsp crates, goes stale on a `-dirty` tree by its own comment
   (`build_stamp.rs`), and every test binary links vilan-core but none of those crates. One hash for
   every test binary of a build means one prefix per build, not one per binary;
3. **std's content**: `vilan_embedded::CONTENT_HASH` for the materialized std; for a std at another
   root (the tree's, `VILAN_STD`), the hash of the loaded std files the drain already computes
   (`source_hashes`, the E12 rule);
4. **the platform** (layers choose files: `web::ui` is two files; std has no item-level twins — all
   13 of its `[platform]` uses are whole-module `mod self` fences — so the IR is otherwise
   platform-independent; Q8 keeps one prefix per platform anyway);
5. **the std module set** (§4.3) and **the macro limits**;
6. the std ROOT only as a re-rooting input, not a key: B422's hazard is a world read against the
   wrong `sources`, and the loader re-roots every path on load, so a prefix built from the tree's
   std serves the materialized copy of the same std (equal content hash) at its own paths.

Rules carried over from §6.15: a corrupt, truncated or version-mismatched file is a MISS, never a
fatal; writes are temp-file + rename; the file cache refuses a world holding overlays and never
serves into a macro world; and **off** under `VILAN_HASH_SHUFFLE` and in
`incremental::clean_analysis` (Q11). A cross-process claim (`std::fs::File::lock`, stable since
Rust 1.89; the tree pins 1.98) lets the first of six concurrent nextest processes build while the
others wait a bounded time or build unwritten — M44's claim/wait, across processes.

## 7. The doors, sized on the three measurements

The prefix saving on each subject is §1.2's "hit removes" minus §5's load; the remaining cost is
the hit residue plus the package.

| door | empty web | kolt client cold check | kolt server cold check | N157 (suite) | LSP pause row | size |
|---|---:|---:|---:|---:|---:|---|
| today | 1.371 G | 11.09 G | 3.39 G | inference 4,737 of 13,002 CPU-s | 14.54 G | — |
| (a) file beside the toolchain | ~0.7 G (−49%) | ~10.0 G (−9%) | ~2.4 G (−29%) | −1,500…−2,300 CPU-s (12–18%) | as P2 | P0+P1+P3+P4: M–L |
| (b) fork-server for nextest | — | — | — | same ceiling, no load cost, only for pre-warmed sets | — | L (+ harness) |
| (c) LSP: budget, then pinned in-process std prefix | — | — | — | — | 10.76 G with the budget alone (x0.74); each remaining miss −1.2 G per leg | P2: S (+P1) |

**(a) A cache file beside the toolchain.** `~/.vilan/std-cache/<CONTENT_HASH>/prefix/` by
default — the prefix lives and is pruned with the std tree it was built from (`vilan cache prune`
already owns that root; L21/N137) — and `VILAN_WORLD_CACHE=<dir>|off` overrides it (§6.15's env-var
design, reasons unchanged). Written lazily on the first miss of a set; `vilan cache warm` (optional)
builds the empty-program sets for CI images. It serves the CLI, `--watch`'s first round, the LSP's
first analysis per set, and every test process. N157's arithmetic: an `inference` test is 967 ms
CPU of which load+walk + base is 517 ms (suite-48's sample, debug profile); the prefix removes about
that plus std's Class A checks and costs a debug-profile load of 50–150 ms → 350–450 ms × 5,212
tests.

**(b) A fork-server.** One process builds std, forks per test: no serializer, no relocation, every
address valid. But nextest owns the spawn; a target runner (suite-48 already used one to record
CPU) can forward a request, yet the child must then run ONE libtest test by name inside a forked
process, which the stable libtest harness cannot do — each of vilan-core's 39 test binaries (and
the other crates') would need a custom `harness = false` main with its own registry (no
`inventory`: vilan-core takes no new dependencies). It serves only the sets the server pre-warmed,
and (a) reaches nextest with no harness change. **Rec: decline** (Q7).

**(c) The server leg in one LSP process.** §1.3: a quarter of the row is eviction. In order: the budget
(E294's door: size M67's budget to the session's declared entries, or declare every entry a world
serves as live) takes the row to 10.76 G; then P1's std-only prefix, pinned per (platform, std set)
and never evicted (35 MB for kolt's client std), turns every remaining miss — an evicted world, an
entry world whose module moved — into a package-only rebuild: −1.2 G for the server world, −1.3 G
for the client entry's (§1.2's "removes"). Sharing ONE prefix between the browser and the node leg
is not on offer: their std sets differ (60 vs 55 modules) and `web::ui` is a different file per
platform; it waits for per-module records (§9, S7).

## 8. The estate of readers that would need a cross-process id

Because the prefix reproduces ids exactly, no reader translates an id; what matters is who READS an
id that another process wrote, and each is listed with how it stays right:

| reader | ids it holds | stays right because |
|---|---|---|
| the prefix's own tables | all three lanes | written and read under one key |
| M19's `WorldChecks` / `ModuleDiagnostics` (`bound_questions: (Id, TypeId, Id)`, suspension rows, `drop_roots`) | `Id`, `TypeId`, `SourceId` (`sources_fingerprint` is an index check) | persisted in the same file, same key |
| S2a/S2b `ModuleTables` (`expr_types`, `declaration_labels`) | `Id` | same file |
| the reach record (`Type` receivers with ids) | `Id` | same file |
| JS emission (functions sorted by id, `transformer.rs:107`, `:3797`) | order | §4.1 makes the order a function of the reachable set; the goldens move once |
| native names (`name_<id>`, `vilan-rust/src/lib.rs:2391`, `:3448`, `:4511`) | `Id` | same; the native goldens move once |
| `--debug` dumps | all | diagnostic output, not compared across processes |
| S0 fingerprints, the const cache, M33's expansions, contract hashes (djb2 over resolved spellings) | none | id-free by construction (the persistence rule, `editor-latency.md` §3.6) |
| HMR state transfer | string keys (`hmr_binding.key`; not traced further here) | to be confirmed in P0's gate |

## 9. Interactions

- **M110 S6 (incr-50, this order).** P0 lands after S6 or inside it: S6 changes the layout, P0
  changes the order the layout follows. Rec: P0 as the slice right after S6's C2, so S6's
  differential classes are not re-proven twice. S6's `writes_other == 0` pin becomes P3's
  immutability premise.
- **M134 and S7.** The 47% a prefix leaves (§1.2) is the six resource/bound passes, the tail and the
  post passes walking std's bodies again. With M134's anchors and S7's per-item records, std's items
  are records like any unchanged item and the prefix carries them; that is when a cold check stops
  paying std at all (up to kolt server −66%, empty web ~−95%, less the load) and when à la carte std (per-module
  records at fixed windows, any subset of std from one file, cross-leg sharing) becomes possible.
- **M19's records and S2a/S2b.** Persisted with the world (Q9). Their premise "std's diagnostics are
  known absent" is what lets row 6's queues be pre-drained.
- **M121 / B553, the reach record.** §4.2's guard, unchanged in kind: `asked_by_std` questions count
  against PACKAGE impls (today they count against hot impls only).
- **S4's const cache.** Content-keyed and id-free, so it needs no prefix to persist — and it is the
  cheapest cold-check door on kolt's client (const pass 173 ms CPU, `const-misses=112` on every cold
  run; find M135). It can share P4's directory rules but is independent of P0–P3.
- **`[platform]` fences and layers.** Per §6 item 4: one prefix per platform; deno and bun share
  `@process` with node and could share node's prefix once P1's differential says the IR is equal
  (Q8).
- **B422 (std roots).** §6 item 6: the loader re-roots.
- **M33's expansion table.** The prefix's precedent (format line, corrupt = miss, cap). Its stamp
  names the version and macro_std, not the build (find G28); §6 item 2's hash should stamp it too.
- **M67 / M24 / M50, the budget.** A pinned prefix is a live exemption of known size; the worlds over
  it no longer need to be counted at std's weight once they share it (structurally, later).
- **Macro worlds.** Compiled lazily on an M33 miss (kolt's first cold run compiled 5 + 2); a loaded
  registry recompiles exactly as today.
- **The playground (wasm).** No filesystem. A prefix could be embedded in the bundle (≈4–5 MB raw for
  the web set); Q10 says not now.
- **L24 (Windows).** §5's file form is portable; the image form would not be.

## 10. What could not be measured without building

- The file size and the load time (§5 estimates from counts and from the clone's cost).
- How often §4.2's guard refuses the prefix (P1 counts it; kolt's foreign-subject impls are the
  case to watch).
- Peak RSS with a loaded prefix (likely lower: std is never parsed, so the parse cache holds no std
  ASTs; P3's gate).
- The debug-profile load cost that N157's estimate assumes (50–150 ms).
- Whether deno/bun produce node's std IR (P1's differential with the platform swapped).

## 11. Finds (filed to `newitems50-papers.json`; repros under `papers-50/finds/`)

1. **B603** — the canonical drain is not a function of the reachable set: a std module first asked
   for by a package module loads after it, so a redundant entry import of an already-reachable std
   module reorders the emitted module (`load_order_by_import_site/run.sh`; on kolt's server, 18
   lines). P0's fix.
2. **E294** — the LSP's pause analyses evict each other's worlds under M67's 192 MiB: the server world
   rebuilt cold (std included) on 4 of 6 pauses, the client entry's on 4 of 6; at 4096 MiB 1 and 2;
   the row 14.54 → 10.76 G, CPU to idle 2,870 → 2,030 ms, VmHWM +9% (`pause_worlds_evict/`).
3. **G28** — the macro-expansion table's stamp is `toolchain <version>` + macro_std's hash: every
   dev build between releases shares the previous build's expansions, so a change to the macro
   engine or the interpreter is served stale output from `dist/.cache` and `~/.vilan/check-cache`
   (`expansion_table_stamp/run.sh` prints the header).
4. **M135** — S4's const cache is content-keyed and id-free but in memory only: every cold check of
   kolt's client re-evaluates its 112 missed const sites (const pass 173–251 ms CPU)
   (`const_cache_in_memory/run.sh`).

## 12. Open questions, each with a recommendation

- **Q1. The unit.** One file per (platform, std module set) holding the std-only world and its
  records; or per-module records now; or inputs only. **Rec: the per-set world** — per-module needs
  S7 and fixed windows, inputs-only buys a fifth.
- **Q2. Std-first canonical order** (one emitted-declaration reorder for multi-module programs, the
  goldens regenerated once, B603 fixed). **Rec: yes**, as P0 right after S6's C2.
- **Q3. Std resolves alone** — package impls never answer std's own pre-entry lookups, as the entry's
  already do not. **Rec: yes**, with the reach record refusing the prefix (cold canonical build) when
  a package impl could have answered; harden to a rule after a release without refusals on the
  estate.
- **Q4. Key by the std closure, not the entry's seeds.** **Rec: yes** — std's import graph ships in
  the prefix index; the in-memory base cache can take the same key in P1.
- **Q5. The build identity** — a vilan-core source hash from a build script, not `VILAN_BUILD_SHA`.
  **Rec: yes**, and the expansion table (G28) stamps it too.
- **Q6. Where and when.** `~/.vilan/std-cache/<CONTENT_HASH>/prefix/`, `VILAN_WORLD_CACHE=<dir>|off`,
  written lazily on a miss, bounded with the check-cache's byte rule, `vilan cache warm` optional.
  **Rec: as stated.**
- **Q7. Door (b), the fork-server.** **Rec: decline** — L and a custom harness for every test
  binary, for a ceiling (a) reaches without touching nextest.
- **Q8. Door (c).** **Rec: the budget first (E294, S), then the pinned in-process prefix (P1/P2)**;
  one prefix per platform; deno/bun on node's only after P1's differential; no cross-leg sharing
  before per-module records.
- **Q9. M19's records and S2's tables in the prefix file.** **Rec: yes** — without them a loaded std
  re-checks its Class A sites and the saving drops from 53% to about 45%.
- **Q10. The playground.** **Rec: no prefix in the wasm bundle for now**; measure the bundle cost
  against the compile saving first.
- **Q11. Off under `VILAN_HASH_SHUFFLE` and in `clean_analysis`.** **Rec: yes** — the differentials
  compare a prefixed analysis against a clean one, so the clean one must not read it.
- **Q12. The encoding.** serde derives with `#[serde(borrow)]` and an in-tree binary format; a
  hand-written encoder; or a fixed-address image. **Rec: serde** — already a dependency, strings
  borrow from the file, the image does not port.

## 13. Slices

| Slice | Content | Size | Needs | Gate |
|---|---|---|---|---|
| P0 | Std-first canonical order: discovery completes, then module nodes, `SourceId`s and the walk in `load_order_key` order over the whole reachable set (B603) | S | S6 (C2) | the B603 repro byte-identical with and without the redundant import; the permutation differential; corpus + native goldens regenerated with a reorder-only diff (checked by a sorted-lines comparison); `ci-local.sh perf` |
| P1 | The in-process std-only prefix: a std-only world (hot = every package module) stored under (platform, std closure, macro limits); package worlds built over it; std resolves alone; `asked_by_std` counts against package impls (refuse → canonical); counters `prefix-hits`/`prefix-refusals` | M | P0 | edit-replay, permutation and check-scope differentials with the prefix forced on; corpus byte-identical; refusals counted on kolt, the examples and the corpus; late writes 0; RSS within 3% |
| P2 | The LSP: M67's budget holds the session's entry worlds (E294), and the std prefix is pinned live per (platform, set) | S | (budget: none); P1 | lsp-latency's seven rows, CPU and instructions; the pause row ≤ 10.8 G; server world misses ≤ 1 in 6 |
| P3 | The serializer: derives across the world's types (row-by-row list of §2: dropped, rebuilt, by value, borrowed), `span_map` by value, std's `*_to_check` pre-drained, the format (header, version, checksum), the load fixups (§3), temp + rename, the cross-process claim | M–L | P1 | a **round-trip differential**: every corpus program and kolt's two legs analyzed over a LOADED prefix vs a BUILT one, byte-identical (observation, JS, native); a corrupt/truncated/foreign-version file is a miss (pins); load time and size reported |
| P4 | The key and housekeeping: vilan-core's build hash, the std content hash, the closure index, `VILAN_WORLD_CACHE`, `vilan cache prune/clean/warm`, the byte bound; G28's stamp | S | P3 | the cold-check rows (empty web, kolt both legs) in instructions; a rebuilt vilan-core misses; an edited std misses |
| P5 | N157: the suite points `VILAN_WORLD_CACHE` at `target/`; suite CPU measured against suite-48's 13,002 CPU-s | S | P4 | full suite green; inference CPU per test reported |
| — | M135 (the const cache on disk) | S | none | kolt client cold const pass ≤ 10% of today's |
