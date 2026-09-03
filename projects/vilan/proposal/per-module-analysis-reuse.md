# Per-module analysis reuse — M19 tranche 2 (E121's diagnostics path)

> **Status: PAPER, 2026-09-03.** Measured against `next` at 635e3728
> (Order 25 sealed: M19 tranche 1's `Type`-keyed bound memo, M21's `pkg::`
> base-cache key, M22, N43's honest phase labels, the keystroke path) on
> the dev machine — 16 cores, WSL2 — with two throwaway probes patched
> into a scratch worktree and reverted: a per-check timer plus a
> per-source entity census in `analyzer.rs`, and a repeat-analysis driver
> in `keystroke.rs`. **No compiler change lands from this lane.** The
> exhibits are a copy of kolt (read-only evidence, never integrated) and
> the E121 keystroke gate's own generator at 1,791 functions.
>
> **Provenance, stated once and meant.** Every measurement below was taken
> under a **1-minute load average of 33 to 96** — a thirteen-lane day on a
> 16-core box. Two kinds of number appear, and they are not equally
> trustworthy. The **wall** numbers (the `VILAN_PHASE_TIMING` phase lines)
> are inflated 2–3× and wander run to run by 1.7×; nothing rests on their
> absolute value, only on ratios between runs taken minutes apart under
> the same load, or on counts that do not move at all (entities,
> substitutions, impls). The **CPU** numbers — §1.5's headline, whole-
> process user + system time around each analysis — are load-independent
> by construction, and they agree with perf-25's quiet-machine record to
> within 6%, which is the cross-check that says so. The building lane
> should still re-record §1.3's wall table on a quiet box.

---

> **The finding that changes this tranche's size.** M19's tracker entry
> sizes tranche 2 as *"a rewrite: one `Analyzer` mints entity ids
> sequentially by load order, so a module's declarations and typed bodies
> are not addressable independently of what loaded before"*. **On the path
> that matters, that is already false.** M21 (Order 25) put every
> non-entry source — std **and** the entry package's own siblings — into
> the base-cached `World`, and a cache hit **clones that world**
> (`analyzer.rs:41344`). The clone carries `Analyzer::entity_id`,
> `source_ranges` and every table with it; the entry then walks **last**
> (`analyzer.rs:43341`). So on a hit the modules occupy a byte-identical
> id **prefix** `[0, W)` and the edited buffer occupies the suffix
> `[W, ∞)`. The work order's option (c) — *"keep sequential ids but freeze
> a prefix per module in load order"* — is not a design to build. **It is
> the shape the tree already has, and nothing exploits it past std.**
>
> What is missing is not identity. It is that **every module-local check
> re-runs over that unchanged prefix on every keystroke**, and the one
> seam that skips such work (`frozen_entity`, `analyzer.rs:27992`) is
> restricted to std — because std is pinned *diagnostic-clean* by a
> differential gate and a package module is not.
>
> **The number.** Six in-process analyses of kolt's client leg, each with
> a distinct buffer and no module changed — a keystroke — cost **965 ms of
> process CPU** apiece once warm (`base 0.0ms`: M21's world, lucide
> included, comes back from the cache). The same program with lucide
> stubbed out (E106's method: 1,791 icon functions → 4, nothing else
> touched) costs **162 ms**. **83% of a warm keystroke's analyzer CPU is
> spent re-analyzing ONE module whose content did not change** — a module
> that is 74,580 of the program's 97,070 entities (77%) and accounts for
> 17,571 of its 18,540 recorded call substitutions (95%). Cold, the same cut takes
> `checks` from 1,898 ms to 190 ms (90%) and the post-passes from 765 ms
> to 173 ms (77%).
>
> **The recommendation, in three sentences.** Do not build per-module id
> spaces and do not content-hash ids — the prefix a base-cache hit
> already hands back is the module boundary, and the two id rewrites cost
> 97 `Id`-bearing `Program` fields, 144 `Analyzer` fields and twelve sites
> that read raw id order — two of them *semantically* (method
> resolution's tie-break, emission order) — for a property the clone
> already provides. Instead **generalize
> the frozen-source seam from `std_sources` to every source in the cached
> world** — for the diagnostic checks *and* for the table builders behind
> them, which are a third of the phase and have no replay problem at all —
> and pay for the fact that a package module is not diagnostic-clean by
> **caching the module's own diagnostics beside the world and replaying
> them** — they are already span-addressed into the
> module's own text and already attributed per source by
> `diagnostic_sources`, so replay is a splice, not a re-derivation.
> Gate soundness the way S1 gated its own skip: a **differential** that
> analyzes the whole corpus both ways and demands byte-identical
> diagnostics, warnings and emitted JS, plus a per-source *dirty* bit that
> refuses reuse for any module whose type slots the entry's `build()`
> actually moved.

§1 is the cost model with numbers. §2 is the identity problem and why two
of its three doors are refused. §3 is diagnostics replay and the
family-by-family classification. §4 answers the invalidation-key question
with a census — and the answer is that the import closure is the **wrong**
key, while the base cache's existing world key is the right one. §5
sequences four tranches with a gate each. §6 is the owner's questions.

---

## 1. The cost model

### 1.1 What is already reused, and what is not

The tracker's framing predates M21. Read the pipeline as it stands:

| stage | site | reused across analyses today? |
|---|---|---|
| parse of a module | `parse_clean_cached` (`lib.rs:266`) | **yes** — content-keyed, process-global (E12) |
| load + walk of every non-entry module | the load loop, `analyzer.rs:41843`+ | **yes on a hit** — the modules are *inside* the stored `World` |
| `resolve_world` (the pre-entry fixpoint) | `analyzer.rs:43238` | **yes on a hit** — the world is stored after it; the phase line reads `base 0.0ms` |
| the entry's own walk | `analyzer.rs:43341` | no, and correctly so — it is the edited buffer |
| `build()` = `resolve_world` + `finalize_build` | `analyzer.rs:33317` | **no** — the queues are drained, so the modules' share is small, but `finalize_build`'s commit tail is whole-program |
| the ~39 checks | `analyzer.rs:43361`–`43543` | **no** — whole-program, std alone skipped via `frozen_entity` |
| the post-passes | `lib.rs:699` | **no** — whole-program table scans |

So M19 tranche 2 is **not** "cache the module's declarations and typed
bodies". M21 already did that. Tranche 2 is exactly two things:

1. the ~39 **checks** stop re-deriving answers about a module's own
   bodies, and
2. the **post-passes** stop rebuilding whole-program tables from scratch.

Everything the tracker item says about entity ids is a constraint on how,
not a prerequisite to be built first.

### 1.2 Method

`VILAN_PHASE_TIMING=1` is the instrument (N43 made its labels honest); it
prints two stderr lines per top-level analysis —

```text
[vilan phase] load+walk {}ms base {}ms build {}ms checks {}ms
[vilan phase] post-passes {}ms contexts+graph {}ms async-infer {}ms … dispatch-refine {}ms
```

— from `analyzer.rs:44043` and `lib.rs:807`. Two throwaway lines were
patched in beside them for this lane and reverted afterwards:

- `[m19 checks]` — every `analyzer.check_*` / `infer_*` / `plan_*` call
  between `phase_checks_start` and the phase print, wrapped in a
  `PhaseClock` and printed sorted descending. 39 entries.
- `[m19 shape]` — total entities, distinct sources, `implementations`,
  `method_call_substitution`, `expr_id_to_expr_map`, sealed frozen ranges,
  and the per-source entity counts read off `Analyzer::source_ranges`.

The counterfactual is E106's, unchanged: a second copy of the kolt exhibit
with `src/lucide/lib.vl` cut from 1,791 icon functions to the four
`views.vl` actually calls, and nothing else touched. Everything else in
the program — 53 sources, 417 impls, the same std, the same entries — is
identical between the two copies, which is what makes the difference
attributable.

Subject: `vilan check src/client.vl` — kolt's client leg, the file M23
names as the one that never hits the base cache. Four runs of each copy,
interleaved, loadavg 86–96 throughout.

### 1.3 The table

Milliseconds, `min / median` of four runs. **Read the ratio column, not
the milliseconds** (see the provenance warning).

| phase | kolt with lucide | lucide stubbed to 4 | ratio (min) | what the module costs |
|---|---:|---:|---:|---:|
| `load+walk` | 1041 / 1123 | 624 / 945 | 1.7× | 40% |
| `base` (`resolve_world`) | 969 / 1031 | 139 / 220 | **7.0×** | 86% |
| `build` | 17 / 18 | 11 / 28 | 1.5× | 34% |
| **`checks`** | **1898 / 2218** | **190 / 281** | **10.0×** | **90%** |
| **post-passes** | **765 / 1106** | **173 / 360** | **4.4×** | **77%** |
| — `contexts+graph` | 391 / 542 | 40 / 63 | 9.9× | 90% |
| — `async-infer` | 169 / 281 | 44 / 89 | 3.9× | 74% |
| — `const-pass` | 167 / 219 | 69 / 174 | 2.4× | 59% |
| — `dispatch-refine` (a slice through the two above) | 76 / 94 | 20 / 32 | 3.7× | 73% |
| — `platform-color` | 25 / 43 | 20 / 35 | 1.2× | 21% |

And the counts, which do not move between runs at all:

| shape | kolt with lucide | stubbed | ratio |
|---|---:|---:|---:|
| entities (`source_ranges`) | 97,070 | 22,609 | 4.3× |
| of which `lucide/lib.vl` | **74,580 (77%)** | 119 | — |
| expressions (`entity_map`) | 116,053 | 24,020 | 4.8× |
| recorded call substitutions | **18,540** | **969** | **19.1×** |
| `implementations` | 417 | 417 | 1.0× |
| sources | 53 | 53 | 1.0× |
| sealed frozen ranges (std) | 80 | 80 | 1.0× |

Three things to take from this.

**(a) The checks phase is superlinear in the module.** 4.3× the entities
buys 10× the checking, because the two costs that dominate are quadratic
or fixpoint-shaped, not per-entity: 19× the call substitutions, and a
resource/drop planner that walks every scan root.

**(b) `implementations` does not grow.** 417 impls either way. The trait
surface a module contributes is tiny next to the *bodies* it contributes.
That matters for §4: the thing that makes reuse hard (global impl
visibility) is not the thing that makes analysis expensive.

**(c) The one module is 77% of the program's entities and 90% of its
checking.** No amount of memoizing inside a check reaches that; only not
running the check over those entities does.

### 1.4 Where the checks phase actually goes

The `[m19 checks]` split, medians of three runs with the range beside
them, and the class §3.3 assigns each entry. A **separate batch** from
§1.3's, taken later under loadavg ~66 with the probe extended to cover the
statements the first cut missed — which is why the phase total reads
2,675 ms here against §1.3's 1,898–3,249 range. The timed entries sum to
2,738 — **102%** — so the split accounts for the phase, and the 2% is
timer overlap and drift under load, not a gap.

| entry | ms, median (range) | shape | class |
|---|---:|---|:--:|
| `plan_resource_drops` | 387 (348–601) | per scan root; walks every body | A |
| `liveness::LastUse::compute` | 345 (301–398) | last-use dataflow over every body | D |
| the ten `compute_*` site passes | 343 (231–433) | clone / box / view-site tables | D |
| `check_resource_moves` | 264 (123–301) | per body | A |
| `infer_bumps` | 211 (162–345) | call-graph fixpoint | D |
| `check_view_value_reads` | 165 (90–187) | per read | A |
| `check_invalidation` | 165 (92–184) | per view-liveness site | A |
| `check_generic_bound_satisfaction` | **149 (67–175)** | instantiation-driven — **tranche 1's** | C |
| `check_resource_generic_instantiations` | 114 (60–171) | per instantiation | A |
| `check_view_escape` | 112 (66–142) | per body | A |
| `check_container_resource_arguments` | 82 (70–88) | per call site | A |
| `check_hmr_transfer_bounds` | 74 (25–101) | per `dev::stash` site | A |
| `check_mutable_arguments` | 69 (49–109) | per call site | A |
| `check_resource_any_coercion` | 68 (45–124) | per coercion site | A |
| `check_view_arguments` | 61 (30–143) | per call site | A |
| `check_element_attribute_shadowing` | 31 (11–41) | per element | A |
| `record_drop_sink_argument_types` | 25 (12–25) | per sink call | A |
| the hover-label render | 24 (18–62) | one label per typed expression | D |
| `check_deprecated` | 23 (19–50) | two full `entity_map` passes | A |
| `build_drop_glue` | 16 (13–25) | per resource type | A |
| the remaining 24 | < 4 each | mostly < 1 | — |

Rolled up by class: **A ≈ 1,658 ms (62%), D ≈ 903 ms (34%), C ≈ 149 ms
(5.6%), B ≈ 1 ms.** Everything in A and D is a **walk over bodies or
sites** whose answer is about the module the body is in. **That is 96% of
the phase, and it is exactly the class a per-source skip removes and
exactly the class no memo can help** — the bodies are all distinct.

**Tranche 1 worked, and it moved the bottleneck.** Editor-perf found
`check_generic_bound_satisfaction` at 63% of a 2,284 ms `checks`; with the
`Type`-keyed memo landed it is **5.6% of the phase**, and the four largest
occupants are now a drop planner, a liveness dataflow, ten site
computations, and a move checker.

**A note on class D, because the first cut of this probe missed it.**
Timing only the `analyzer.check_*()` statements left 780 ms of the phase
unattributed. It is not overhead: it is
`liveness::LastUse::compute(&analyzer)` and the ten `compute_*` passes
that follow it (`compute_capture_clone_sites`, `compute_resource_types`,
`compute_clone_sites`, `compute_return_clone_sites`,
`compute_parameter_entry_clones`, `compute_boxed_locals`,
`compute_primitive_views`, `compute_scalar_view_refs`,
`compute_scalar_view_calls`, `compute_hmr_bindings`), plus the eager
render of a hover label for every one of 116,053 typed expressions. They
produce **tables, not diagnostics**, which makes them *easier* to freeze
than a check — there is nothing to replay, only a table to keep — and at
34% of the phase they are not optional for T1.

Two structural notes read out of the tree while classifying these:

- `plan_resource_drops` opens with `if !self.declares_a_resource() { return; }`
  (`analyzer.rs:8765`, predicate at `:8939`) — *any* struct or enum in the
  **whole program** marked `resource` switches on 350–600 ms of planning
  over every module. On the stub copy it costs 14–34 ms, because the
  program still declares a resource but has 74k fewer entities to plan
  over. This is a **whole-program predicate gating per-body work**, and
  §4 files it as a census entry.
- `check_deprecated` (`analyzer.rs:19375`) makes two full passes over
  `function_calls` and `expr_id_to_expr_map` and then asks
  `self.std_sources.contains(&source)` **per site**, through
  `source_of_id` — a **linear scan of `source_ranges`**
  (`analyzer.rs:27955`), not the binary search `frozen_entity` uses. At 53
  sources and 116k expressions that is most of its 19–50 ms. It is a free
  fix for whoever is in there, and T0 is the moment to take it.

### 1.5 What a keystroke pays, warm — the measurement that decides it

The numbers above are `vilan check`, a one-shot process: the base cache is
cold, so `load+walk` and `base` are paid in full. Under the LSP they are
not. P5 drives six in-process `Document::analyze` calls on one entry, each
with a distinct content (a trailing comment — a keystroke that changes the
buffer and no module), and reads **whole-process CPU** (`getrusage`,
user + system) around each. **CPU is load-independent, so these numbers
*are* comparable to perf-25's quiet-machine record** — and they agree with
it, which is the cross-check.

Per keystroke, warm (analysis 2 onward; `base 0.0ms` on every one, so the
world — including lucide's 74,580 entities — comes back from the cache):

| subject | warm CPU, min / median of five | vs kolt |
|---|---:|---:|
| **kolt client leg, with lucide** | **965 / 1,033 ms** | 1.00× |
| kolt client leg, lucide stubbed to 4 | **162 / 177 ms** | **0.17×** |
| E121's generated exhibit, 1,791 functions | **50 / 57 ms** | 0.05× |

(perf-25 recorded 1,140 / 910 ms of LSP CPU per keystroke on views.vl on a
quiet machine. 965 ms here, under loadavg 47–60, on the client leg. The
instrument agrees with itself.)

**One condition on these numbers, stated plainly.** P5 drives
`Document::analyze` with only the entry in the overlay, so M9's rule never
fires and client.vl **hits** the base cache — `base 0.0ms` on every warm
rep. In a real session with views.vl also open, M23 says it never hits and
`base` is 1,357–2,713 ms instead. So the table above is the **post-M23**
shape: it measures the world this paper's tranches are designed for, not
the world an editor has today. That is deliberate — T1 and T2 are inert
without M23 — and it is why §5 puts M23 ahead of everything.

**So the answer to the work order's first question is a measured number,
not an estimate: 83% of a warm keystroke's analyzer CPU — 803 of 965 ms —
is spent re-analyzing ONE module whose content did not change.**

Where it goes, scaling the phase line's wall by the run's own CPU/wall
ratio (0.41 for the full copy, 0.30 for the stub — the divergence is why
this is an estimate and the totals above are not):

| warm, per keystroke | kolt with lucide | stubbed | the module's share |
|---|---:|---:|---:|
| `load+walk` (the world clone + revalidating 53 sources) | ~14 ms | ~6 ms | 57% |
| `base` | **0** | **0** | — |
| `build` | ~4 ms | ~1 ms | — |
| **`checks`** | **~720 ms** | ~75 ms | **90%** |
| **post-passes** | **~225 ms** | ~81 ms | **64%** |
| **total (measured, not scaled)** | **965 ms** | **162 ms** | **83%** |
| `lsp-index` — the editor tables, outside `analyze` | 110–584 ms wall | 65–88 ms wall | ~80% |

Two riders.

**(a) The 500 ms mandate is not reachable by making this work faster.** It
is reachable by not doing it: the stub copy — the same program, the same
53 sources, the same 417 impls, one module smaller — already answers a
keystroke in 162 ms.

**(b) `lsp-index` is a fifth cost nobody has costed.** The editor tables
the server builds over each analysis (`document.rs:1257`) run 110–584 ms
of wall per keystroke on the full copy against 65–88 ms on the stub — the
same ~80% attribution, outside `analyze` and therefore outside every
budget this paper's tranches touch. It is not on T1/T2's path; it is filed
here so the next lane's arithmetic is not surprised by it.

### 1.6 A finding the gate lane needs: the generated exhibit does not
### exercise this path

E121's Q6 ruled the gate's exhibit **generated** and sized like
kolt-with-lucide, and the keystroke-path lane built it
(`keystroke.rs:1742`, `exhibit_module`). Measured with the same probes:

| | generated exhibit (1,791 fns) | kolt client leg | ratio |
|---|---:|---:|---:|
| entities | 21,589 | 97,070 | 4.5× |
| expressions | 21,726 | 116,053 | 5.3× |
| **recorded call substitutions** | **104** | **18,540** | **178×** |
| `checks`, cold | 108–121 ms | 1,898–3,249 ms | 18× |
| post-passes, cold | 7 ms | 765–1,405 ms | 110× |
| **warm CPU per keystroke** | **50 ms** | **965 ms** | **19×** |

The generator matches kolt's **function count** and nothing else about its
**shape**: its bodies are `let base = frame(seed); base + k` over `i32`,
with no `View`, no generic instantiation, no method chain. Real lucide
icons return `View` and chain `.child(<path … />)` four to a dozen times,
which is where the 18,540 substitutions come from.

That is fine for what the exhibit was built for — E121 §6.2 wanted a
**keystroke-path** subject, and the path it gates costs 0.8 ms on it. It
is **not** a subject for the diagnostics budget, and `diagnostics_budget`
(`keystroke.rs`, `#[ignore]`d at ~925 ms) is asserted on it — **at 50 ms
of warm CPU it would pass the 500 ms budget today, on a program that never
had the problem.** A diagnostics-path gate needs the generator to emit
**view-shaped** bodies — a `View` return, a chained builder, one generic
call per body — or it will go green on the wrong exhibit. **This is a find
for the gate, filed in §6 as a question rather than assumed.**

---

## 2. The identity problem

### 2.1 What the id space actually does on the hit path

`Id` and `TypeId` are dense monotonic counters minted **per occurrence**
(`new_entity_id`, `analyzer.rs:4210`; `type_id_for_type`,
`analyzer.rs:15039`). That is E121 §3.1's "one structural fact", and it is
true. But the conclusion the tracker drew from it — that a module's
entities are not addressable independently of what loaded before them —
does not survive M21:

1. Modules load and walk **inside the world-building loop**, before the
   entry is touched.
2. Each file's walk pushes a `SourceRange { start, end, source }`
   (`analyzer.rs:37687`); the ranges are **disjoint by construction**
   because the counter only grows.
3. `base_cache_store` stores that world with its `entity_id` counter
   (`analyzer.rs:43264`); `base_cache_lookup` returns `world.clone()`
   (`analyzer.rs:41344`) and `PhaseMarks::started_at` zeroes only the
   clock (`analyzer.rs:41593`).
4. The entry walks **after** the clone, from `entry_walk_start =
   analyzer.entity_id` (`analyzer.rs:43340`).

**Therefore, across two analyses that hit the same base-cache entry, every
module entity has the same id, in the same `SourceRange`, in the same
order.** The invalidation is already exact and already content-based: the
key is `BaseCacheKey` (platform, std seeds, workspace fingerprint, macro
budgets, entry prelude, package root + sibling set) and **every loaded
source's content is re-hashed per hit** (`analyzer.rs:41338`).

The empirical half: six in-process analyses of kolt's `client.vl`, each
with a distinct entry content, print an identical `[m19 shape]` line —
same 97,070 entities, same per-source counts, same 53 sources. With load
order fixed and ids monotone, identical window **sizes** in identical
**order** is identical windows.

### 2.2 The three doors, costed

**(a) Per-module id spaces with a global remap — `(module, local)`.**
Refuse. The blast radius, counted in the tree:

- `Program` has **123 public fields, of which 97 carry an `Id`, `TypeId`
  or `SourceId`**; `Analyzer` has **191 fields, of which 144 do**. A pair
  id changes the key type of substantially all of them.
- **Twelve sites treat the raw id as an ORDER**, and two of them are
  semantic, not cosmetic:
  - `declaration_order(member_id) -> member_id.0` (`analyzer.rs:13871`),
    which is the **tie-break in method resolution** —
    `impl_member_candidates` sorts its candidates by it
    (`analyzer.rs:13123`). Change the order and you change which impl a
    call selects.
  - `functions.sort_by_key(|id| id.0)` (`transformer.rs:9714`) and
    `pending.sort_by_key` (`:9515`), which are **emission order** — B33's
    dependency-ordered module-level bindings ride on it.
  - The rest (`analyzer.rs:4478, 7177, 8912, 8954, 12373`,
    `async_infer.rs:1768`, `chunks.rs:216`, `context.rs:498, 874, 1150`)
    are determinism sorts, and a determinism sort over a pair is fine —
    but only if the pair's order agrees with load order, which is to say:
    only if you rebuild exactly the property you already have.
- `frozen_entity`'s binary search (`analyzer.rs:27992`) and
  `seal_frozen_ranges`' disjointness argument (`:27969`) both rest on
  monotone `u32` ids.

So (a) buys nothing the clone does not already give, and pays for it with
a change to ~240 fields and two semantic orderings. **Refused.**

**(b) Stable ids by content hash of the declaration.** Refuse, and the
refusal is already written in the tree. `type_id_for_type`'s comment
(`analyzer.rs:15040`) states the invariant:

> *"Each call mints a fresh id; types are intentionally not interned …
> inference resolves a type in place by mutating
> `type_id_to_type_map[id]` — an `Unknown` slot becoming concrete, a
> deferred accessor id resolving — so any mutated id must stay unshared."*

A content-hashed `TypeId` is **shared by construction**, which is the one
thing the solver forbids: two occurrences that hash alike would share a
slot, and resolving one would resolve the other. B77/B95 are the
regressions that established this. `get_type_by_type_id`'s doc
(`analyzer.rs:15085`) records the one measured attempt to change the
regime — 71 of 218 call sites become borrow errors — and calls the two
accessors "a permanent pair, not a migration".

Content-hashing `Id` (entities, not types) is not forbidden by that, but
it is (a) again: the same ~240 fields, plus the loss of the order that
`declaration_order` and the transformer depend on. **Refused.**

**(c) Freeze a prefix per module in load order, and reuse while its
inputs are unchanged.** **Take it — and note that step one is already
done.** The prefix exists (`source_ranges`), its disjointness is proved
(`seal_frozen_ranges`), its stability across analyses is the base-cache
clone, and its invalidation is the per-hit content validation. The
mechanism that consumes it exists too (`frozen_entity`, ~22 call sites)
and is deliberately scoped to std. §3 is what it costs to widen that
scope; §5 sequences it.

### 2.3 What keys on ids, and what the widening therefore touches

The work order asks which tables key on ids. Answer, by consumer:

| consumer | keys on | affected by widening `frozen_ranges`? |
|---|---|---|
| `entity_map` / `entity_scope_map` / `span_map` / `variables` / `functions` / `parameters` / `scopes` | `Id` | **no** — the ids do not move; only which entities a check *visits* changes |
| references (`reference_count`, `member_name_spans`, `struct_initializer_field_spans`, `type_references`) | `Id` + `SourceId` | **no**, but see §3: they are filled during the **walk**, which a hit already reuses |
| dispatch (`generic_dispatch`, `binary_op_dispatch`, `try_dispatch`, `lift_dispatch`, `bound_dispatch_traits`, `method_call_substitution`) | `Id` per call site | **no** for identity; **yes** for §4 — these are what the post-passes read |
| the keystroke path's symbol index (`keystroke.rs:546`) | **module name + declaration name**, never an id, with a per-module `ShapeStamp` | **no** — it is already the per-module shape this paper argues for, one layer up |
| the transformer | `Id` order | **no** under (c); **yes** under (a) |

The symbol index is worth calling out as precedent: E121's keystroke lane
already built a per-module, content-stamped, name-keyed structure and it
did not need an id rewrite either.

---

## 3. Diagnostics replay

### 3.1 The wall S1 put up, and why a package module hits it

`frozen_entity`'s doc (`analyzer.rs:27983`) is explicit:

> *"Definition-site checks skip such entities: their diagnostics depend
> only on std's own content, which is pinned clean by the differential
> gate's invariant test. Use-site and instantiation-driven checks must
> never consult this."*

The soundness argument has **two** halves, and only one of them is about
scope:

1. **The std-clean invariant** — every std module under full scan produces
   zero diagnostics and zero warnings, so the definition-site diagnostics
   the skip elides are *known not to exist*
   (`crates/vilan-core/tests/check_scope_differential.rs`).
2. **The differential sweep** — the whole corpus analyzed both ways must
   agree byte-for-byte on diagnostics, warnings and emitted JS.

A package module fails (1) by construction: a user's module can have
errors, and the whole point of the diagnostics path is to publish them. So
widening the seam means **replacing (1) with replay** — the skipped
diagnostics are not zero, they are *remembered* — while keeping (2)
unchanged as the gate.

### 3.2 What a cached module's diagnostics actually need

Read `error.rs`. A diagnostic is

```rust
pub struct Error { pub span: Span, pub msg: String,
                   pub note: Option<Note>, pub trace: Vec<TraceHop> }
pub struct Note  { pub span: Span, pub msg: String,
                   pub source: Option<SourceId> }
```

with two parallel vectors on the `Program`: `diagnostic_sources:
Vec<SourceId>` and `warning_sources: Vec<SourceId>`, built at
`analyzer.rs:43959` from the `diagnostic_source_marks` the walk and
`attribute_new_diagnostics` laid down (E1/B112).

Four properties, each checked:

- **Spans are byte offsets into the owning source's own text.** Unchanged
  module content ⇒ unchanged spans. Nothing to relocate. ✔
- **`msg` is already rendered.** It may name a type or an item from
  another module, but every such module is in the same validated world, so
  the rendering is stable under the same key. ✔
- **`Note.source` and every `TraceHop.note.source` carry a `SourceId`
  INDEX, not a path.** Those index the world's `sources` vector, which the
  clone preserves. Stable **today**; it becomes a live constraint the
  moment any tranche reorders or prunes `sources`, so it belongs in the
  replay unit's invariant, written down. ✔ with a condition.
- **Order is normalized at the end**, by `sort_in_step(&mut diagnostics,
  &mut diagnostic_sources, &roots)` (`analyzer.rs:38734`). Replayed
  diagnostics spliced in before that sort reproduce the published order
  regardless of when they were spliced. ✔

So the replay unit is small and already well-formed:

```text
ModuleDiagnostics { source_hash, diagnostics: Vec<Error>,
                    warnings: Vec<Error>, sources_fingerprint }
```

keyed per `SourceId` inside the cached world's sibling structure, filled
by the first analysis that ran the checks, spliced by every later one.

### 3.3 Module-local versus world-dependent: the family classification

The work order asks which diagnostic families are module-local. The
honest partition is three-way, not two — and the third class is the one
that decides the design.

All 39 timed entries are placed; the four classes partition them.

**Class A — module-local given the world (safe to freeze and replay,
subject to the guard at the end of this section).** The answer depends on
the module's own bodies plus types the world already resolved. The entry
does not appear in a module's bodies, so it cannot supply a new site.

`check_readonly_mutation`, `check_mutable_arguments`,
`check_mutable_references`, `check_view_bindings`, `check_view_arguments`,
`check_view_value_reads`, `check_view_escape`, `check_invalidation`,
`check_reseat_escape`, `check_element_attribute_shadowing`,
`check_must_use`, `check_deprecated`, `check_tuple_spreads`,
`check_hmr_transfer_bounds`, `check_container_resource_arguments`,
`check_resource_any_coercion`, `check_resource_moves`,
`check_resource_generic_instantiations`, `record_drop_sink_argument_types`,
`plan_resource_drops`, `check_drop_impls`, `build_drop_glue`,
`check_wire_boundary`, `check_json_boundary`, `check_hashable_boundary`,
`check_partialeq_boundary`, `check_rpc_signatures`, `check_expose_fields`.

**That is 28 of the 39 timed check calls, and by §1.4 it is ~62% of the
phase's milliseconds** (the last six are each under 1 ms and are in the
class for completeness, not for their cost).

**Class B — whole-program by definition (must keep running; ~1 ms).**
Coherence and conformance, where the *point* is to compare declarations
across the program: `check_trait_conformance`,
`check_duplicate_inherent_members`, `check_duplicate_block_members`,
`check_duplicate_trait_impls`. An impl written in the **entry** can make a
**module's** impl a duplicate, so these can never be frozen per module.
Measured cost on the full exhibit: **0.2–20 ms combined.** Leave them
whole-program; nothing is gained by touching them.

**Class C — instantiation-driven, and the entry can reach into a
module (the class that needs a guard).** `check_generic_bound_satisfaction`
and `check_binding_trait_constraints` walk `method_call_substitution`,
which is keyed by *call site id* — so a call site **inside** module M is
M's own. But `analyzer.rs:43227` records the two-phase invariant that
makes the class real:

> *"`resolve_world` runs BEFORE the entry walks — resolution only, no
> commit tail; `finalize_build` runs once, in the post-entry `build()`, so
> constraints the entry may still bind stay open."*

A module-level generic left open by `resolve_world` can be **ground by
the entry**, which moves a type slot a module call site reads. Class A is
not immune either: a resource classification or a view verdict can turn on
the same slot.

**This is the soundness hole, and it has a cheap, exact answer.** Every
write that *changes* a type slot goes through **one** function,
`write_type_slot` (`analyzer.rs:15074`) — which already distinguishes a
world-changing write from a fresh mint and an idempotent rewrite, and
counts the first kind into `type_map_writes` for S3b's fixpoint exit. Two
small additions make it a per-module guard:

1. **Stamp a type id's source at mint.** `new_type_id`
   (`analyzer.rs:15033`) is a dense monotonic counter, so a `Vec<SourceId>`
   indexed by `TypeId` and filled from `self.current_source_id` — the same
   field `set_current_source` and `attribute_new_diagnostics` already
   maintain per walk — costs one push per mint and one index per read.
   (`Id`s already have this through `source_ranges`; `TypeId`s are a
   separate counter and do not.)
2. **Set a per-source dirty bit in `write_type_slot`**, on exactly the
   writes it already calls world-changing.

After `build()`, a module with a clear bit had *no* slot it owns moved by
the entry's resolution, and its Class A and Class C answers are the ones
the cache holds. A module with a set bit falls back to full checking, for
that analysis only. The dirty set is also the honest **diagnostic** for
whoever debugs a T1 miss: it names the module and the analysis.

The expected hit rate is high and measurable before a line of the cache is
written — which is what makes it §5's T0 (a *measurement* gate, not a
build).

**Class D — table builders and effect fixpoints, which produce no
diagnostics at all: 34% of the phase, and the class the first cut of this
probe missed.** `liveness::LastUse::compute` (345 ms), the ten `compute_*`
site passes (343 ms), `infer_bumps` (211 ms), the hover-label render
(24 ms), `infer_borrows`, `rewrite_view_assignment_targets`,
`plan_last_use_drop_extents`, `seal_frozen_ranges`.

There is nothing to *replay* here — the output is a table the later passes
and the editor read — so freezing means **caching the table**, which is a
strictly easier job than replaying a diagnostic: no span to validate, no
attribution to preserve, no publication semantics to argue about. Three
notes:

- The two biggest, `LastUse` and the `compute_*` group, are per-body and
  per-site walks whose rows are keyed by entity id — and §2.1 is exactly
  the guarantee that those ids do not move. A cached world's rows for its
  own entities are re-usable verbatim; only the entry's rows are new.
- **`infer_bumps` is a monotone call-graph fixpoint** whose per-function
  verdict grows only as its callees' do (`analyzer.rs:16347` states the
  monotonicity). A module function's callees are all in the world, so the
  world's verdicts are a **sound seed**: iterate from the entry's nodes
  only, never from empty.
- The hover-label render costs 24 ms, not the hundreds one might guess
  from 116,053 `pretty_print_type` calls. It is in this class for
  completeness; it is not worth a tranche of its own.

---

## 4. The invalidation key — is `(module × transitive imports)` right?

**No.** Answered with the census the work order asks for. Four families
let a change outside a module's import closure change its analysis, and
one of them is fatal to the import-closure key by itself.

**(1) Impl visibility is whole-program. There is no orphan rule.**
`Analyzer::implementations` is a flat `Vec` (`analyzer.rs:3010`), and
member resolution reaches it through `implementations_by_member`
(`:3020`), a `name -> Vec<index>` map over **every impl in the loaded
program**. `impl_member_candidates` (`analyzer.rs:13064`) filters that row
by subject-type comparison and by nothing else — **no import check, no
visibility check, no module scoping**. `satisfies_trait_bound`
(`analyzer.rs:4310`) scans the same `Vec` linearly. So `impl Foo with
Greet` written in a module nobody imports makes `Foo: Greet` hold
everywhere, and `x.foo()` in a module that never heard of the impl's file
resolves to it. Blanket impls (`impl type T with Into<T>`,
`analyzer.rs:6076`) make the reach total. **A trait impl in an unrelated
module can change any module's analysis. The import closure is not a
sufficient key.**

**(2) Whole-program predicates gate per-module work.**
`declares_a_resource()` (`analyzer.rs:8939`) is `structs.values().any(…
resource) || enums.values().any(…)`. Adding `resource struct X` anywhere
switches on `plan_resource_drops` — 470–653 ms on this exhibit — for every
module in the program. Same shape: `option_enum_id`,
`primitive_struct_ids`, `try_trait_id`, the intrinsic resolution block at
`analyzer.rs:43622`+ which scans `implementations` for std's `str`/`List`/
`NativeMap`/`JsonValue`/`Shared`/`Option` impls.

**(3) Four passes run in the REVERSE dependency direction — a module's
answers depend on its DEPENDENTS.** This is the family the import closure
gets exactly backwards:

- `dispatch_refine::refined_edges` (`dispatch_refine.rs:349`): *"an
  `OnConstraint` site is resolved per ENTRY of the function owning the
  constraint"* (module doc, `:24`). A generic function in module M has its
  dispatch edges decided by every call site of M's function **anywhere**,
  including in the entry.
- `context::thread_contexts` (`context.rs:62`): global dataflow that
  **rewrites** the tree — deletes call edges and mints new ones for the
  hidden context argument (`lib.rs:667-698`). A module function gains a
  parameter because of who calls it.
- `async_infer::infer` (`lib.rs:748`): asyncness is inferred forward, but
  `adapted_instances` monomorphizes a generic's asyncness **per
  instantiation** — the call site's, not the definition's.
- `const_eval::check_const_only` (`const_eval.rs:1610`): a reverse
  reachability fixpoint from `program.asset_channel_fns` — "does any
  runtime path reach `asset::emit`". Adding a call in the entry can refuse
  a function in a module.

**(4) The ambient axes.** Platform (E119: a std layer file is a different
type per target), the entry package's prelude, the macro budgets, the
workspace shape. These are **already in `BaseCacheKey`** and are the
reason it has the fields it has — evidence that this census has been run
once before, for the world, and got the right answer.

### 4.1 The key that is right, and it already exists

Every one of (1)–(4) is a function of **the world plus the entry**, and
nothing else. And that is precisely what `BaseCacheKey` plus the per-hit
content validation of every loaded source already establishes:

> a base-cache hit means *every source in the program except the entry has
> byte-identical content, under an identical platform / prelude / macro
> budget / workspace / sibling set.*

So the invalidation key for module reuse is **not** `(module content ×
transitive import contents)`. It is:

```text
BaseCacheKey  ×  every loaded source's content hash  ×  "the entry did not
                                                        move this module's
                                                        type slots"
```

The first two terms are validated today, on every hit, for free. The third
is §3.3's dirty bit. That is the whole key, and it is strictly *stronger*
than the import closure — which is why it can be sound in the presence of
(1) and (3), and the import-closure key cannot.

The price is honest and worth stating: reuse is **all-or-nothing per
world**. Edit `theme.vl` and every module's cached checks for
`client.vl`'s world are gone, because `theme.vl` is in it. That is the
same granularity M21 chose for the world itself, it matches what an editor
session actually does (one buffer moves at a time, and the modules it
imports do not), and it needs no dependency graph at all. A finer key —
per-module, with a real dependency graph and a resolution of (1) and (3) —
is a second paper, and §5 does not pretend to sequence it.

---

## 5. The tranches

Four, each gated, the first small enough for one lane. Expected CPU is
against §1.5's **measured** warm keystroke: **965 ms today on kolt's
client leg, 500 ms mandated, and 162 ms is what the same program costs
with the one unchanged module out of it** — that last number is the floor
this sequence is walking toward, and it is a measurement, not a model.

### T0 — the dirty-bit census (one lane, measurement only, ships one line)

**Do.** §3.3's two additions: stamp each `TypeId`'s source at
`new_type_id` (`analyzer.rs:15033`) into a `Vec<SourceId>`, and set a
per-source dirty bit in `write_type_slot` (`analyzer.rs:15074`) on the
writes it already calls world-changing. Print the set under
`VILAN_PHASE_TIMING` as `[vilan phase] entry-dirty <n>/<sources>`. Nothing
else changes; no reuse is attempted.

**Why first.** The whole design rests on the claim that a keystroke in the
entry moves type slots in *few or no* modules. If that is false — if
every keystroke dirties lucide — T1 is worthless and the lane finds out
for the cost of a `Vec` and two lines instead of a rewrite. It is also the
natural moment to take §1.4's free fix: give `source_of_id`
(`analyzer.rs:27955`) the binary search `frozen_entity` already uses, so
`check_deprecated`'s 45 ms of linear scanning goes away with it.

**Gate.** On a scripted kolt session (views → theme → client, ten
keystrokes each), record the dirty count per analysis. **Pass condition:
the module holding the bulk of the entities is clean on ≥ 90% of
keystrokes.** Record the number either way; a red gate here is a finding,
not a failure.

**Expected CPU after: unchanged (965 ms).**

### T1 — freeze and replay the world's modules through the checks

**Do.**
1. Seal `frozen_ranges` from **every source in the cached world**, not
   just `std_sources` — a second range set, `world_ranges`, beside the
   existing one, so std's stricter guarantee is not weakened by
   association.
2. Gate the widened set on T0's dirty bit: a dirty module drops out of
   `world_ranges` for that analysis.
3. Route the **Class A** checks (§3.3's 28, 62% of the phase) through it.
   Class B and C keep the std-only set.
4. Do **Class D** too — it is 34% of the phase and it is the *easier*
   half: keep the cached world's rows for `LastUse` and the ten
   `compute_*` passes (both keyed by entity id, which §2.1 pins), and seed
   `infer_bumps` from the world's verdicts instead of re-running the
   fixpoint from empty. No replay semantics are involved; these are
   tables, not diagnostics. **A T1 that skips class D leaves a third of
   the phase on the floor and will miss its own projection.**
5. Record each module's own diagnostics and warnings (§3.2's replay unit)
   into a `CHECKED_CACHE` keyed by `BaseCacheKey`, filled by the first
   analysis that ran them, spliced in before `sort_in_step` by every
   later one.

**Gate.** Three pins:
- **The differential**, extended: `check_scope_differential.rs`'s corpus
  sweep re-run with the widened set forced on, demanding byte-identical
  diagnostics, warnings and emitted JS. This is S1's own gate and it is
  the load-bearing one.
- **The replay pin**: a package module with a deliberate error, analyzed
  from a dependent twice; the second analysis publishes the identical
  diagnostic, at the identical span, attributed to the identical file.
- **The red-first pin**: a planted freeze-disable switch (S1's
  `full_scan_checks_forced` has the shape) must move the phase number and
  must not move the diagnostics.

**Expected CPU after.** Classes A and D are 96% of the phase, and the
stub copy shows what the same phase costs with the module gone (282 ms
wall against 2,675). `checks` ~720 ms of CPU → **~80–150 ms**. Total
**~330–420 ms**. **The mandate is met**, with margin thin enough that T2
is not optional — and thin enough that a T1 which skips class D misses
it.

### T2 — the post-passes over a frozen world

**Do.** The three whole-program passes, in the order §1.3 ranks them:
`contexts+graph` (391 ms, 90% attributable), `async-infer` (169 ms, 74%),
`const-pass` (167 ms, 59%). None of them can be frozen per module — §4(3)
is exactly about them — so the move is different: **memoize the
world-only half.** Each pass is a fixpoint or a dataflow over the call
graph; seed it from the cached world's settled result and iterate only
from the entry's nodes and their reverse-reachable set. `refined_edges`'
memo is the template, and E121 §3.4's three specific fixes (hoist the memo
above the per-site loop, share it across `const_eval.rs:1734` and
`context.rs:636`) are still unbuilt and belong here.

**Gate.** The same differential (emitted JS is the real assertion for
`thread_contexts`, which rewrites the tree), plus a pin that a keystroke
performs **one** seeded pass, not a rebuild — counter-asserted, the way
`generic_bound_checks()` counts tranche 1.

**Expected CPU after.** post-passes ~225 → **~90–110 ms**. Total
**~230–320 ms** — approaching the 162 ms the stub copy already answers a
keystroke in, which is the honest floor for this program until T3.

### T3 — the world clone, and the hit's own cost

**Do.** What is left is `load+walk` on a *hit*: a full deep clone of the
`Analyzer`'s ~191 tables (`analyzer.rs:41344`) plus a `read_source` +
`content_hash` of every loaded source (`analyzer.rs:41338`), per keystroke
— 52 file reads on kolt. Both are proportional to the program. The clone
exists because the analysis mutates the world; a copy-on-write layer over
the world's immutable half, or `Arc`-sharing the tables the entry provably
never mutates, is the shape. The revalidation can ride the LSP's file
watcher instead of re-reading every source per analysis — M25 makes the
same move one seam over, caching `modules_in_root`'s per-request
`read_dir` on the manifest fingerprint.

**Sequence after M24**, which changes what is stored, and after T1/T2,
which change what "provably never mutates" means.

**Expected CPU after: ~150–200 ms**, i.e. the stub copy's measured 162 ms
for the whole program. This is headroom, not the mandate.

### T4 — the finer key (a paper, not a lane)

Per-module invalidation with a real dependency graph, which requires
answers to §4(1) (impl visibility: an orphan rule, or a per-module impl
index) and §4(3) (the reverse-direction passes). Not needed for the 500 ms
mandate. Filed so the boundary is visible.

### The order, and what it depends on

```text
M23  the entry that imports an open buffer never hits the cache
 │   (T1 and T2 are INERT without it — they key on the hit)
 ▼
T0   the dirty-bit census — one line, one measurement
 ▼
T1   freeze + replay the world's modules through the checks
 ▼
T2   the post-passes over a frozen world          ── M26 cancellation
 ▼
M24  base-cache eviction (changes what is stored)
 ▼
T3   the world clone and the hit's own cost
```

**T1 and T2 are worthless until M23 lands.** M23 is the finding that an
entry importing an open buffer never stores or hits a base world — which
is every keystroke in `client.vl`. This paper's whole mechanism keys on
the hit. M23 first, then T0.

---

## 6. Questions for the owner

**Q1 — Is "all-or-nothing per world" acceptable as the reuse
granularity?** §4.1's key means editing any module in the program throws
away every module's cached checks for that world, not just the edited
one's dependents. It matches what an editing session does and it needs no
dependency graph; the alternative is T4, a second paper, and it needs an
orphan rule. *Recommend: yes, accept the coarse key.* A decision is
needed because it sets whether T4 is ever scheduled.

**Q2 — May a package module's cached diagnostics be replayed at all, or
must every published diagnostic be re-derived each analysis?** The S1 seam
was allowed to skip work only because std's diagnostics are *known
absent*. T1 replaces that with *remembered*, which is a weaker promise:
the differential gate proves the two agree on the corpus, not on every
program. This is a semantics-level change to what a published diagnostic
is, and it is the same class of question §7.9.4 of `leak-soak.md` raised
before M9 was built. *Recommend: yes, with the differential as the
standing gate.*

**Q3 — Should the diagnostics-path gate get a view-shaped exhibit?**
§1.6: the generated exhibit matches kolt's function count and misses its
cost by 18× on `checks` and 178× on call substitutions, so
`diagnostics_budget` could go green on a program that never had the
problem. Fixing it means the generator emits `View`-returning, chained,
generically-instantiating bodies — still generated, still nothing copied
from any application, per E121's Q6 standing rule. *Recommend: yes, and treat
it as a prerequisite of T1's gate rather than a separate item.*

**Q4 — `plan_resource_drops` is 470–653 ms and switches on for the whole
program the moment any type is `resource`.** Under T1 it is frozen per
module and the question is moot for the editor. But the same predicate
governs `vilan build`, where nothing is frozen. Is a build-time cost of
that shape acceptable, or should the planner be scoped to the reverse
reachability of the resource types actually declared? *Recommend: file it
separately; it is not on E121's path.* Flagged because measuring it is
this lane's find and it will not be visible again once T1 hides it.

**Q5 — Does the owner want the `Note.source` index invariant written into
the replay unit as an assertion, or as a comment?** §3.2: replayed notes
carry `SourceId` indices into the world's `sources` vector. It is stable
today and silently breaks if any future tranche reorders or prunes
`sources` — the failure mode being a note pointing at the wrong file,
which is exactly the harm E1/B112 exist to stop. An assertion costs a
comparison per replayed note. *Recommend: assertion.*

---

## 7. Probe ledger

Every number in this paper, and how to re-create it. Both compiler patches
were made in a scratch worktree off `next` at 635e3728 and reverted; the
proposals repo is the only thing this lane commits.

| # | what | how |
|---|---|---|
| P1 | the phase split, cold | `VILAN_PHASE_TIMING=1 vilan check src/client.vl` on a kolt copy |
| P2 | the per-check split | throwaway: wrap each `analyzer.check_*()` between `phase_checks_start` and the phase print in a `PhaseClock`, print sorted. **Wrap the non-`check_*` statements too** — `liveness::LastUse::compute`, the ten `compute_*` passes, the hover-label render, the intrinsic-resolution block — or 780 ms of the phase (29%) is silently unattributed, which is what the first cut of this probe did |
| P3 | the shape census | throwaway: print `source_ranges` entity counts per source, `implementations.len()`, `method_call_substitution.len()`, `expr_id_to_expr_map.len()`, `frozen_ranges.len()` beside the phase line |
| P4 | the lucide counterfactual | a second kolt copy with `src/lucide/lib.vl` cut to the four icons `views.vl` calls, everything else identical (E106's method) |
| P5 | the warm keystroke, and the id-stability check | throwaway `#[ignore]` test in `keystroke.rs`: six in-process `Document::analyze` calls on one entry, a distinct trailing comment each time, `getrusage(RUSAGE_SELF)` around each; compare the `[m19 shape]` lines and read the CPU |
| P6 | the generated exhibit | `keystroke.rs`'s `exhibit_module(1791)` + `EXHIBIT_ENTRY` written to a throwaway package, `vilan check` under the same instrument |

Load average at each measurement is recorded in the lane's log and ranged
33–96. **§1.3's wall ratios are between runs taken minutes apart under the
same load; its absolute milliseconds are not comparable to perf-25's
quiet-machine record and are not used for any claim. §1.5's CPU numbers
are, and they match it.**

One correction to the work order, for the record: it cites `editing-dx.md`
§7.9 for the BASE_CACHE / M9 / frozen-source material. §7.9 is
`leak-soak.md`'s — M9's design pass and the six-way borrower inventory
that ruled path-keyed eviction unsound. `editing-dx.md` is E49's
diagnostics-DX charter and has no §7.9.
