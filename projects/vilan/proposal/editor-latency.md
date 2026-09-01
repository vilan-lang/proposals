# Editor latency — the two paths (E121)

> **Status: PAPER, 2026-09-01.** Measured against `next` at 33692bb2
> (post-Order-24, editor-perf's 2.2× included) on the dev machine — 16
> cores, WSL2 — with the scripted LSP sessions §7 lists. No compiler
> change was made in this lane; the deliverable is the design. The
> exhibit is kolt with lucide (1,791 generated functions) plus a
> synthetic series at 4 / 500 / 1,791 / 5,000 functions of one shape,
> which is what turns "slow on a large codebase" into a coefficient.
>
> **The finding that reframes the mandate.** E121 states that "every
> request rides the SAME whole-program analysis — tokens, hints,
> completion, and errors all wait for it." **Measured, that is false, and
> the truth is more interesting.** No request handler waits: every one is
> an `.await`-free read of the last landed snapshot (`main.rs:1638`),
> and on views.vl the whole five-provider burst answers in ~15 ms while
> diagnostics take ~1.1 s. What is true is the two things underneath it:
> every request **recomputes from the whole program on every keystroke**
> (so its cost scales with the codebase, not the file), and it answers
> from a snapshot that is **up to one debounce plus one full analysis
> stale, with nothing marked and no re-mapping** beyond B38's tail. The
> keystroke path is therefore not absent — it is unbuilt, unbudgeted and
> already 1.5× over the mandate's 10 ms on the exhibit. The diagnostics
> path is 2.2× over its 500 ms.

§1 is the budget as measured. §2 designs the split the mandate asks for.
§3 is incrementality and what the analyzer's architecture does to it. §4
is scheduling. §5 sequences the rewrites. §6 defines the gate. §7 is the
probe ledger, the determinations, and the owner's questions.

---

## 1. The budget today, per request type

### 1.1 Method

A scripted LSP session (`latdrive2.py`, §7) drives the real `vilan-lsp`
release binary over a **copy** of kolt — the owner's tree is never
written to. Per file it appends a probe block (a valid function with a
local, a call, a module-qualified call and a trailing comment), waits for
the open analysis to land, then measures each provider two ways:

- **warm** — five samples with no analysis in flight; this is the cost of
  the request itself;
- **hot** — one keystroke, then all five providers fired at once the way
  an editor fires them, each timed **from the edit**; then diagnostics
  waited for.

The hot/warm distinction is the one that answers "does it wait": if a hot
number tracks the diagnostics number, the request waits. Every row
carries the 1-minute loadavg (M13's method) and the server process's
CPU delta (utime+stime — M15's load-robust clock, and the one that
matters here because the dev machine ran 13 other lanes during this
order).

### 1.2 The table

kolt with lucide, `next` at 33692bb2. `views.vl` is the large,
lucide-reaching file; `theme.vl` is const-heavy and reaches no package
module; `syn5000` is the synthetic 5,000-function module in views.vl's
place. Medians; wall in the first column, process CPU beside it.

| subject | request | warm wall | warm CPU | hot (from edit) | budget | verdict |
|---|---|---|---|---|---|---|
| views.vl (1,791) | semanticTokens/full | 12.2 ms | 10 ms | **12.3 ms** | 10 ms | **over** |
| views.vl | inlayHint | 0.3 ms | 0 ms | 13.8 ms† | 10 ms | over in burst |
| views.vl | completion (scope, 125 items) | 1.9 ms | 0 ms | 14.8 ms† | 10 ms | over in burst |
| views.vl | completion (`style::`, 49 items) | 1.1 ms | 0 ms | 15.1 ms† | 10 ms | over in burst |
| views.vl | hover | 0.4 ms | 0 ms | 15.3 ms† | 10 ms | over in burst |
| views.vl | **publishDiagnostics** | — | — | **1111 ms** (1071–1358) | 500 ms | **2.2× over** |
| theme.vl (no `pkg::`) | semanticTokens/full | 1.2 ms | 0 ms | 1.3 ms | 10 ms | ok |
| theme.vl | the whole five-provider burst | — | — | 3.1 ms | 10 ms | ok |
| theme.vl | **publishDiagnostics** | — | — | **200 ms** (197–208) | 500 ms | ok |
| syn5000 views.vl | semanticTokens/full | 14.7 ms | 20 ms | 14.9 ms | 10 ms | **over** |
| syn5000 views.vl | the whole burst | — | — | 18.9 ms | 10 ms | **over** |
| syn5000 views.vl | **publishDiagnostics** | — | — | **1236 ms** (1137–1517) | 500 ms | **2.5× over** |

Recorded at loadavg **8.4–11.0** (16 cores) — the order's other lanes
were running, and the wall column must be read with that beside it. The
CPU column is the load-robust one and is what §1.4 reasons from.

† **The burst is serial.** The five hot numbers are not five independent
latencies: they are cumulative, and their increments (1.5, 1.0, 0.3,
0.2 ms) are exactly the individual warm costs. The server answers the
burst one request at a time, so the number an editor actually
experiences is **the last one — 15.3 ms on views.vl, 18.9 ms on
syn5000, 3.1 ms on theme.vl**. That is the keystroke-path figure to
gate on, and it is the mandate's 10 ms budget times 1.5 and 1.9.

### 1.3 Where the analysis time goes

The `VILAN_PHASE_TIMING` line, one per LSP analysis, per keystroke on
views.vl (medians, same session):

| bucket | views.vl (1,791) | theme.vl | what it is |
|---|---|---|---|
| `lsp-context` | 7.7 ms (89 ms on the first) | 7.7 ms | `resolve_project_context` (`document.rs:107`) — walk to `vilan.toml`, parse it, run E113's reachability. **Uncached, every keystroke.** |
| `lsp-analyze` | 886 ms | 31 ms | the analysis proper |
| ⤷ `load+walk` | 38 ms | 2.5 ms | module discovery, parse, macro expansion, the per-file walk |
| ⤷ `base` | **160 ms** | **0.0 ms** | `resolve_world()` — **M21 in the wild** |
| ⤷ `build` | 4 ms | 1.3 ms | import fixpoint, prelude, constraint fixpoint |
| ⤷ `checks` | **578 ms** | 19 ms | the ~40-call check sequence (`analyzer.rs:42019+`) — **M19's residue** |
| ⤷ `post-passes` | 90 ms | 8 ms | call-graph 43, async-infer 18, const-eval 27 |
| `lsp-index` | 38 ms | 5 ms | `entity_spans` + `ReferenceIndex::build` + attribution, rebuilt in full |
| `lsp-legs` | 0.0 ms (`legs 0`) | 0.0 ms | E113's extra analysis per further reaching platform — not charged here |
| debounce | 150 ms | 150 ms | `DEBOUNCE_MS` (`main.rs:35`) |

The two lines are the same session's evidence for two filed items.
**M21 is visible as a single number**: views.vl carries `pkg::` imports
and pays `base` 160 ms on **every** keystroke; theme.vl carries none,
hits `BASE_CACHE` on its second analysis, and pays **0.0 ms** from then
on. **M19 is visible as `checks`**: 578 ms against theme.vl's 19 ms,
for a file of comparable size — the difference is the 1,791 unchanged
functions the check sequence walks again.

Buckets plus debounce reconcile with the wall: 7.7 + 886 + 38 + 150 =
1082 ms against a measured 1111 ms median.

### 1.4 The coefficient — what "large codebase" costs

The synthetic series (4 / 500 / 1,791 / 5,000 functions of one shape,
the same views.vl consumer, the four icons it actually calls always
present) gives the marginal cost per generated function. Recorded under
lane load — **the wall column is unusable at loadavg 54–60 and is
omitted; the CPU column is what M15's method exists for**:

| generated functions | keystroke CPU (median) | loadavg |
|---|---|---|
| 4 | 290 ms | 53.7–55.7 |
| 500 | 445 ms | 59.7–60.3 |
| 1,791 | 925 ms | 58.6–59.6 |

That is a straight line: **≈ 285 ms fixed, plus ≈ 0.36 ms of CPU per
function in the reachable program, per keystroke.** Read against the
mandate it says something sharper than any single measurement:

> On today's architecture the 500 ms diagnostics budget is spent at
> **≈ 600 generated functions**. kolt is at 1,791. The budget is not a
> tuning problem; it is exceeded by a *third* of the exhibit.

And it says where the ceiling is. Even a perfect keystroke path leaves
the diagnostics path at ~0.36 ms/function; the only way 500 ms survives
a codebase that grows is for the per-keystroke work to stop being
proportional to the whole program. That is §3.

### 1.5 What actually waits for what

The charter asks which requests wait for the full analysis. The answer,
read out of both the code and the measurement:

**None of them.** `Backend::fenced` (`main.rs:1642`) runs every query
handler's body synchronously over a snapshot guard, and the invariant is
stated in its own doc comment (`main.rs:1638`): *"Every query handler's
body is `.await`-free — pure work over a snapshot guard."*
`semantic_tokens` (`document.rs:2096`), `inlay_hints`
(`document.rs:2065`), `completion` (`document.rs:3273`) and `hover`
(`document.rs:1769`) all read `self.documents`, and if no program has
landed they answer empty rather than block. The measurement agrees: the
burst returns in 15 ms while the analysis it would have waited for takes
886 ms.

**What is actually wrong is three other things**, and they are what the
mandate's two paths must fix:

1. **Every request recomputes over the whole program.**
   `semantic_tokens()` re-walks `program.functions`, `structs`, `enums`,
   `traits`, `variables`, `parameters`, the whole `entity_map`,
   `member_name_spans` and `type_references`, then sorts and de-overlaps
   (`document.rs:2101-2298`) — **on every request**, for a file whose own
   token count is 468. The `semantic_token_cache` (`main.rs:460`) is only
   a delta baseline and is never read back to skip the work. Completion
   re-tokenizes the entire live buffer per keystroke
   (`completion.rs:1095`) and `auto_import_completions`
   (`completion.rs:1774`) iterates every child module's whole
   `name_to_id_map` under `std` and `pkg`; `import_completions` reads the
   **filesystem** per request (`modules_in_root`, `analyzer.rs:39347`).
   This is why views.vl's tokens cost 12.2 ms and theme.vl's cost 1.2 ms
   for half as many tokens — the cost tracks the program, not the file.
2. **The answers are stale and unmarked.** They describe the last landed
   text, which is up to one debounce plus one full analysis old — on
   views.vl, up to ~1.3 s of typing. There is no re-mapping onto the
   current tree except B38's byte-identical **tail**
   (`compute_retained_tail`, `document.rs:1687`), which salvages only
   what lies after the edit.
3. **Superseded analyses are discarded, never cancelled.** There is no
   `$/cancelRequest` handling and no cancellation token anywhere in
   `vilan-lsp`. A superseded analysis runs to completion and is thrown
   away at `land` (`main.rs:1414`) or at `plan_publish`
   (`publish.rs:104`). At 950 ms of CPU per views.vl analysis and a
   150 ms debounce, sustained typing starts an analysis roughly every
   350 ms and each runs ~950 ms — **up to three of them in flight at
   once, two of them already garbage**. That is where a session's
   responsiveness goes under real typing, and it is invisible to any
   single-keystroke measurement.

One more, adjacent: `did_open` runs `Document::analyze` **inline on the
async handler** (`main.rs:2131`), not on `spawn_blocking` as
`analyze_and_publish` does (`main.rs:1354`) — so opening views.vl blocks
a tokio worker for the full 1.1 s. The session trace names it: *"slow
request: didOpen took 1112 ms"*.

---

## 2. The two paths

### 2.1 The keystroke path — never type-checks

**What it may read**

- the live buffer's text and `LineIndex`;
- the **parse** of the live buffer, through `PARSE_CLEAN_CACHE`
  (`lib.rs:212`, content-keyed on `content_hash`, `lib.rs:270`) — parse
  only;
- the last completed analysis's `Program`, **read-only and only through
  the re-mapping defined below**;
- a per-module **symbol index** (new, §2.1.4), keyed by module content
  hash.

**What it may not read**

- anything that runs `Analyzer`: no `resolve_world`, no `build`, no
  check sequence, no post-passes;
- `resolve_project_context` (`document.rs:107`) — 7.7 ms warm, 89 ms
  cold, uncached, and it walks E113's reachability graph;
- the filesystem. Completion's `read_dir` per request
  (`analyzer.rs:39347`) moves behind the index.

#### 2.1.1 The re-mapping: a two-sided anchor

B38 already built half of it. `compute_retained_tail`
(`document.rs:1687`) takes the longest common byte **suffix** of the
outgoing analyzed text and the incoming one, trims it forward to a line
boundary, and shifts the tokens inside it by a constant offset. Its
honesty argument is the one to keep, verbatim from the source
(`document.rs:1681`): *"Identity of BYTES is the whole honesty argument:
the suffix is literally the same text, so positions are exact."*

Generalize it to both sides. Given the analyzed text `A` and the live
buffer `B`:

- `p` = the longest common byte **prefix**, trimmed **back** to a line
  boundary (to the start of the line containing the first difference);
- `s` = the longest common byte **suffix**, trimmed **forward** to a
  line boundary, clamped so `p + s ≤ min(|A|, |B|)`;
- an analyzed token entirely inside `[0, p)` maps to itself, shift 0;
- an analyzed token entirely inside `[|A| − s, |A|)` maps by the constant
  shift `|B| − |A|`;
- tokens in the middle window `[p, |A| − s)` have **no image** and are
  dropped.

The middle window is exactly the region the user is editing, and it is
served from **syntax alone**. That is the whole mechanism: positions in
the two anchors are exact by byte identity, and the window between them
is never guessed at.

#### 2.1.2 When the re-mapping is unsafe

Position-exact is not semantically-exact, and the charter asks for the
line between them. The anchors are always position-exact. They become
**semantically** stale when the edit inside the middle window changes
what a name in an anchor *resolves to*:

1. a top-level declaration is added, removed or renamed (`fun`, `struct`,
   `enum`, `trait`, module-level `let`) — every use of that name
   anywhere may change classification;
2. an `import` line changes — the file's whole name resolution moves;
3. a signature or type annotation changes — call sites in the anchors
   change;
4. **another module** was edited — this file's analysis is stale
   wholesale, and no amount of local anchoring helps.

Cases 1–3 have a discriminator that costs no type-checking. Hash the
module's **top-level item headers** — the ordered list of
`(kind, name, header-span text)` for every top-level item, plus every
`import` line — straight off the parse that the keystroke path already
has. Call it the **declaration-shape stamp**. If the buffer's stamp
equals the analyzed text's stamp, no name's resolution can have moved,
because nothing that binds a name changed. Case 4 is caught by the
existing `Document::depends_on` (`document.rs:1595`) against the world
revision (`main.rs:511`).

That yields three states, and they are the honest vocabulary for the
owner's question:

| state | condition | tokens | hints | completion | hover |
|---|---|---|---|---|---|
| **exact** | stamp matches, no dependency moved | anchors re-mapped + syntax in the window | anchors re-mapped, **withheld in the window** | index + buffer scope | anchors only |
| **stale** | stamp changed, or a dependency moved | anchors re-mapped, **any identifier not in the analyzed scope table falls back to syntax** | anchors re-mapped, unchanged (see below) | index + buffer scope | anchors only |
| **unusable** | no anchor (paste replaced the file) | syntax only | withheld | index + buffer scope | lexical keyword hover (`document.rs:1773`) |

In every state the answer is served in O(file), and in no state does the
keystroke path type-check.

#### 2.1.3 Semantic tokens and inlay hints, specifically

**Tokens** split cleanly. Everything syntax can decide — keywords,
literals, comments, operators, punctuation, and an identifier's lexical
role — is a function of the current buffer's token stream, costs
O(file), and is *never* stale. Only the resolution-dependent part (is
this name a function, a struct, a variable; `readonly`, `declaration`,
`defaultLibrary`) needs the analysis, and that part is what the anchors
carry. A wrongly-coloured identifier is a cosmetic error that the next
analysis corrects, and the middle window — where the user's eyes are —
is syntax-only and therefore always right.

**Hints are different, and the difference should decide the policy.**
`inlay_hints()` (`document.rs:2065`) is a linear scan of
`program.variables` rendering an inferred type per `let`. A hint has no
syntax-only fallback: there is nothing to show. And a hint that is wrong
is not a cosmetic error — it is a **lie about a type**, which is the one
thing an inlay hint exists to tell the truth about.

The recommendation, which is also owner question Q1:

- **withhold hints inside the middle window, always.** A hint on the line
  you are typing is simultaneously the most likely to be wrong and the
  least useful; and withholding there is invisible, because the hint was
  about to move anyway.
- **serve the anchors unchanged in the stale state — do not flicker.**
  VS Code has no affordance for a dimmed or provisional hint; the only
  available "mark" is not sending it, which makes hints blink on and off
  across a typing burst. A hint that is briefly one analysis old is a
  smaller harm than a display that strobes. `inlayHint/refresh` is
  already sent when an analysis lands (`main.rs:1596`), so the correction
  arrives on its own.

#### 2.1.4 Completion: a per-module symbol index

Completion cannot be re-mapped — it is a query at a cursor, not a
projection of a previous answer. It needs an index, and the mandate says
so: *"invalidated only by that module's edits."*

```
struct ModuleSymbols {
    content_hash: u64,           // the parse cache's own key (lib.rs:270)
    exports:      Vec<SymbolEntry>,   // name, kind, origin tier, doc, signature label
    analysis_epoch: u64,         // which analysis filled the resolution-derived fields
}
struct SymbolIndex { by_module: HashMap<ModulePath, ModuleSymbols> }
```

The property that makes this work: **a module's export list is a
function of its own syntax alone** — the names and kinds it declares, and
their header text. It does not depend on that module's imports. So the
index is buildable from a *parse*, needs no analysis, and an edit to
module `X` invalidates exactly `X`'s entry and nothing else. Doc strings
and signature labels are likewise syntactic. What is *not* syntactic — a
re-export's target, a type-driven member list — is carried from the last
analysis with `analysis_epoch` beside it, so a consumer can tell a
syntactic fact from a resolved one.

Completion then becomes: locals from the buffer's own parse (a scope walk
over the syntax tree, O(file)), plus an index lookup, plus the existing
keyword and snippet tables. The whole-buffer `tokenize`
(`completion.rs:1095`) shrinks to an incremental lex of the current line,
which is all `cursor_context` needs; `auto_import_completions`'
per-module `name_to_id_map` sweep (`completion.rs:1774-1820`) becomes the
index read; `modules_in_root`'s `read_dir` (`analyzer.rs:39347`) is
served from the index and never touches the disk on the keystroke path.

**Hover** takes the strictest rule, because it is the one provider for
which "no answer" is an acceptable answer: serve only from the anchors,
and fall back in the middle window to the lexical keyword hover that
already exists (`document.rs:1773`). Its lookup structure should also
stop being a linear filter — `entity_at` (`analysis.rs:98`) filters
`entity_spans` and takes a `min_by_key` over the whole vector; sorting it
once at build time makes it a binary search, which the `ReferenceIndex`
beside it already does (`references.rs:209`).

### 2.2 The diagnostics path

May read everything. Must gain three properties it does not have.

- **Debounced.** It already is, at a fixed 150 ms (`main.rs:35`). §4
  argues for making it adaptive and says why the adaptive rule retires
  itself once the mandate is met.
- **Cancellable.** It is not, at all. §4.2 designs cooperative
  checkpoints. This is the single change with the largest effect on how
  a *session* feels, as opposed to how a keystroke measures.
- **Incremental.** §3.

What it may **not** do, which is a constraint the current code violates
in one place: it may not run on a request-handling thread. `did_open`'s
inline analysis (`main.rs:2131`) should go through `spawn_blocking` like
`analyze_and_publish` does (`main.rs:1354`).

---

## 3. Incrementality

### 3.1 The one structural fact

`Id` and `TypeId` are dense monotonic counters minted **per occurrence,
not per meaning**: `new_entity_id` (`analyzer.rs:3893`), `new_scope_id`
(`analyzer.rs:14385`), `new_type_id` (`analyzer.rs:14594`). The type
case is the load-bearing one — `type_id_for_type`
(`analyzer.rs:14600`) mints a fresh id on every call, and the comment
above it states the reason that any redesign must respect:

> *"Each call mints a fresh id; types are intentionally not interned …
> inference resolves a type in place by mutating
> `type_id_to_type_map[id]` — an `Unknown` slot becoming concrete, a
> deferred accessor id resolving — so any mutated id must stay
> unshared."*

Everything downstream inherits it. This is editor-perf's finding that
**an id-keyed memo memoizes nothing**: on kolt, 17,802 distinct type ids
produced 32 distinct impl-selection answers
(`dispatch_refine.rs:449-464`).

The proven way out is already in the tree, and it is doctrine now
(`type_.rs:31-35`): **switch the key from the id to the resolved
`Type`.** `Type` derives `Hash`/`Eq` for exactly this purpose, and that
one change is editor-perf's 2.2×. One honest limit to record: `Type` is
a *shallow* structural key — `Struct(Id, Vec<TypeId>)` carries argument
**ids**, so two shallow-equal `Type`s are equal only because the consumer
walk recurses through those same ids (the soundness argument at
`dispatch_refine.rs:461-465`). It is sound **within one analysis** and
worth 2.2×; it does **not** survive a keystroke, because the ids are
minted fresh next run. A memo that survives keystrokes needs a genuinely
content-derived key, which is §3.5.

### 3.2 M19 — per-module analysis caching

**What must become per-module.** Nothing in the analyzer represents *one
analyzed module's declarations and typed bodies*. `Module`
(`analyzer.rs:1875`) is three fields — an id, a name, and a list of
entity ids pointing back into the flat tables. `LoadedModule`
(`analyzer.rs:37654`) is purely syntactic and *is* content-addressed
(it is what `parse_clean_cached` hands back, `lib.rs:265`) — but it
caches **parse**, not analysis. The `Analyzer` (`analyzer.rs:2457`) is
one flat bag of ~200 side tables for the whole program.

**The one per-file structure that exists** is `SourceRange`
(`analyzer.rs:36516`) — `{ start, end, source }`, the half-open
**entity-id window** each file's walk produced, collected in
`Analyzer::source_ranges` (`analyzer.rs:2676`). Because `entity_id` only
grows, the windows are disjoint by construction. That is the precedent
to generalize, and it already has one exploitation: S1's frozen ranges
(`seal_frozen_ranges`, `analyzer.rs:27411`; `frozen_entity`,
`analyzer.rs:27434`), consulted by ~22 check sites to skip std entities.

**And its rule is the wall M19 runs into.** `analyzer.rs:27425-27433`:
*"Definition-site checks skip such entities … Use-site and
instantiation-driven checks must never consult this."* That is why the
biggest single occupant of the `checks` bucket cannot be skipped —
`check_generic_bound_satisfaction` (`analyzer.rs:4262`, called at
`analyzer.rs:42036`) is instantiation-driven, because a std generic's
bound is violated by a *user's* type argument. So it pays for every std
and every generated call site, every keystroke.

**Can it be memoized on inputs?** Yes, and by the E106 template exactly
one pass over. Its cost is
`|method_call_substitution| × avg(|substitution|) × |implementations|²`,
and its two inner calls both read the value type only through
`type_id_to_type_map`: `satisfies_trait_bound` (`analyzer.rs:4315`,
defined `analyzer.rs:3993`) scans `self.implementations` linearly per
call, and `unrankable_bound_impls` (`analyzer.rs:4329`) runs even on the
success path. Key them on `(Type, required_trait_id, required_arguments)`
and `(Type, trait_id)` and the same collapse applies: 1,791 identically
shaped generated functions ask the same question 1,791 times for one
answer. Two obstacles to name honestly: `satisfies_trait_bound` takes
`&mut self` (it calls `reconcile_type`, which mints type ids), and the
required arguments are re-substituted per call
(`analyzer.rs:4300-4308`), so they are themselves fresh ids and need the
same `Type`-level normalization before they can be part of a key. A
third, smaller: the function eagerly deep-clones the whole
`method_call_substitution` map (`analyzer.rs:4267-4271`) on every run
purely to release a borrow.

**Can it be made incremental?** Only after a module boundary exists. The
design shape: an analyzed-module unit keyed on
`(content_hash, hash of every dependency's content_hash)`, holding the
module's declarations and typed bodies in *module-local* id space, with
a relocation table into whole-program id space at compose time. That is
the rewrite §3.5 says needs its own paper.

**Can it move off the diagnostics path?** No. Bound satisfaction is a
diagnostic.

### 3.3 M21 — the `pkg::` base-cache bypass

The condition is one line, `analyzer.rs:40358`:

```rust
&& collect_module_refs(&nodes.0, "pkg").is_empty()
```

A purely **syntactic** scan of the entry's AST: any entry file containing
a single `import pkg::…` is neither served from nor stored into
`BASE_CACHE` (`analyzer.rs:39798`). The practical consequence is that
**every multi-module Vilan application entry misses the cache**, and the
measurement in §1.3 is the price: `base` 160 ms per keystroke on
views.vl against 0.0 ms on theme.vl.

There is a **second** bypass the tracker item does not name, and it
matters for the fix. Inside `expand_entry_over_world`,
`analyzer.rs:40096` returns "this world never loaded a module the
generated code demands" on any `pkg::` reference, and the caller
(`analyzer.rs:40384-40394`) then throws the hit away and recurses into
`analyze_inner` with `allow_cache = false` — a full cold rebuild. So even
a cacheable entry whose *macro expansion* emits a `pkg::` reference pays
twice.

**The fix, and why the bypass exists.** The stated rationale
(`analyzer.rs:40303-40311`) is that `pkg::` siblings "expand or load
inside the world-building loop, so such entries build fresh." That names
the actual work: world-building today interleaves (i) resolving **std**,
which depends only on the entry's std reference set, with (ii) loading
**package** modules, which is per-entry. Split them. The cached value is
std's world — a package import does not change std's world — and packages
are loaded on top of the cached world afterwards. `BaseCacheKey`
(`analyzer.rs:39762`) already keys on `std_seeds` plus a workspace
fingerprint and validates content per hit (`analyzer.rs:39936-39942`), so
the key needs no change; what needs changing is where the package load
happens relative to the store point. M21's own pin (an entry with one
`pkg::` import hits the cache on its second analysis) is the right gate.

This is the **cheapest** item in the paper: one seam, 160 ms/keystroke,
no new data structure, and a filed pin.

### 3.4 The whole-program post-passes

All three run from `post_analysis_passes` (`lib.rs:697`). Measured on
views.vl they are 90 ms of the 886 — no longer the 1.2 s editor-perf
found, because the `refined_edges` memo already landed. What remains:

| pass | site | needs the whole program? | verdict |
|---|---|---|---|
| `dispatch_refine::refined_edges` | `dispatch_refine.rs:317` | **yes** — an `OnConstraint` site's answer depends on every call site anywhere that instantiates the owning generic | **memoize harder**, don't incrementalize. The memo (`dispatch_refine.rs:465`) is declared *inside* the per-site loop, so its 32 answers are recomputed per site; hoist it above the loop, and share one across the two callers (`const_eval.rs:1734` and `context.rs:636`) that pass overlapping sites. |
| the const pass (`const_eval::check_const_only`) | `const_eval.rs:1610` | **yes** — it is a reverse-reachability fixpoint ("does any runtime path reach `asset::emit`") | **move off the keystroke path entirely, and incrementalize the rest.** The actual const *evaluation* is ~20 ms and is already insensitive to program size (11.9 ms at 1,791 icons vs 11.0 ms at four); the cost was the shared `refined_edges` call at `const_eval.rs:1734`. The fixpoint is monotone over the reverse call graph with a handful of roots (`program.asset_channel_fns`), which is the textbook shape for an incremental reachability structure. |
| `context::thread_contexts` | `context.rs:62` | **yes** — context threading is a global dataflow | **memoize**, and respect the ordering invariant: it returns `Some(graph)` only when it applied no rewrite (`context.rs:83`, `:96`) and `None` after `apply` (`context.rs:100`), because the rewrite deletes and mints call edges. Its `refined_edges` call is `context.rs:636`. |

The shared observation: all three call `refined_edges`, and the call
graph is deliberately built **once** and threaded through
(`lib.rs:665-696`). One memo, hoisted and shared, is most of the
remaining post-pass cost.

### 3.5 What the analyzer's architecture does to all of this, and the rewrite

Three things fight incrementality, in order of how hard they fight:

1. **Ids are per-occurrence.** §3.1. Any cross-analysis memo is
   defeated at the key. A fix has two shapes: *intern* types with a
   separate mutable slot class for inference variables (the comment at
   `analyzer.rs:14601` sketches exactly this and its sharp edge — a
   correct interner must exclude `Unknown`/`Unresolved` and anything
   later mutated), or move to a **two-level id** — `(module content
   hash, within-module ordinal)` — so an unchanged module's entities
   keep their names across analyses. The second is what a module cache
   needs anyway.
2. **There is no module boundary.** §3.2. `SourceRange`'s entity-id
   windows are the seed; a real boundary is a struct that owns a
   module's declarations and typed bodies, plus a relocation step. Note
   the one existing mechanism that already discriminates by source
   (`frozen_entity`) is explicitly restricted to definition-site checks,
   so it cannot be widened into this — it must be built beside it.
3. **The whole-program passes are passes over tables, not queries over
   a graph.** Each one scans `program.entity_map` /
   `program.function_calls` / the whole call graph from scratch.
   Incrementality here means reformulating them as demand-driven queries
   with recorded dependencies, which is a different program.

**Be concrete about the size of this.** (1) and (2) together are the
incremental analyzer, and they touch `Analyzer`'s ~200 tables, every
`Id`-keyed map, and the `Program` construction at `analyzer.rs:42596`.
**That is a paper of its own** — this one should not pretend to sequence
it. What this paper claims is that the first four steps of §5 are worth
most of the mandate without it, and that they are the right preparation
for it: the `Type`-keyed memo is the id fix in miniature, and M19's
cache is the module boundary in miniature.

---

## 4. Debouncing and scheduling

### 4.1 What runs where

Today: handlers run on tokio workers; the analysis runs on
`spawn_blocking` (`main.rs:1354`) which then spawns and **joins** a fresh
128 MiB-stack OS thread (`document.rs:909`, needed for chumsky's
recursion and nested macro worlds). `did_open` is the exception and
should not be (§1.5).

Under the two paths that becomes a rule rather than an accident:

- **the keystroke thread** — every query handler, plus the buffer edit,
  plus the incremental lex and parse of the edited module (through the
  parse cache), plus the symbol-index update for that module. All
  O(file). Never touches `Analyzer`.
- **the analysis thread** — one at a time per document, cancellable,
  producing diagnostics and the next snapshot to anchor against.

The keystroke path must not be able to be blocked by the analysis
thread. Today it cannot be, because handlers read a `DashMap` guard and
`land` is documented as synchronous-by-construction — *"the map guard is
taken and dropped here, never held across the caller's `await`"*
(`main.rs:1405`). That property is load-bearing and should get a note
saying so.

### 4.2 Cancelling a superseded analysis

None exists. The design:

- The analysis already samples the world revision before it starts
  (`let started_at = revision.load(...)`, `main.rs:1353`) and stamps it
  onto the result (`main.rs:1362`). Give the analysis a
  `should_continue: &dyn Fn() -> bool` that compares `started_at` to the
  live `revision` — one relaxed atomic load.
- **Where to check.** Four places, all already loops: the per-file walk
  (every N entities), the constraint fixpoint (`resolve_constraints`,
  `analyzer.rs:27441`, per round), the ~40-call check sequence
  (`analyzer.rs:42019+`, between calls), and the per-site loops in the
  post-passes (`dispatch_refine.rs:395`, `const_eval.rs:1678`). At one
  atomic load per check-sequence entry and per thousand entities, the
  instrument costs nanoseconds against a 950 ms analysis.
- **What it returns.** A `Cancelled` outcome that `analyze_and_publish`
  drops without landing and without publishing. `land`
  (`main.rs:1407`) and `plan_publish` (`publish.rs:98`) keep their
  existing stamp checks unchanged — cancellation is an optimisation on
  top of a correctness mechanism that already works, and must not become
  the thing correctness depends on.
- **`reanalyze_dependents`** (`main.rs:1482`) sequentially awaits one
  full analysis per dependent with **no supersession check between
  them**. It should check the revision between dependents; that is a
  three-line change and on a shared module it is worth an entire
  analysis per stale round.

### 4.3 The debounce

`DEBOUNCE_MS = 150` is right when the analysis costs 50 ms (theme.vl:
150 + 50 = 200 ms measured, comfortably inside budget) and wrong when it
costs 950 ms — at 150 ms the queue fills faster than it drains.

Proposal: **adaptive**, `debounce = clamp(0.3 × last_analysis_wall,
150 ms, 500 ms)`. theme.vl keeps 150 ms. views.vl today waits 285 ms,
which roughly halves the number of in-flight superseded analyses without
materially changing the perceived error delay (1111 → ~1250 ms, against
a path that is 2.2× over budget either way). And the rule **retires
itself**: once §5 lands and the analysis is under 350 ms, the clamp
returns 150 ms permanently. It is a bridge, not a feature — which is the
right thing to say to the owner, whose instinct will be that a longer
debounce is a defeat.

The debounce already restarts from the **last** keystroke
(`on_change` re-spawns per edit and the generation counter supersedes,
`main.rs:1711-1729`), which is the correct shape.

### 4.4 What the editor shows meanwhile

Existing diagnostics stay on screen until a new analysis lands — the
server publishes only on land, and E117's ghost (a superseded publish
landing last) is closed by the revision stamp. The remaining question is
whether a diagnostic known to be stale should be marked. **No** — VS Code
has no affordance for it, the only available mark is removal, and
removing errors while the user types is exactly the flicker that made
E117 feel broken. Tokens and hints follow §2.1's table.

---

## 5. The rewrites, sequenced

Each step's gain is measured from §1 where the phase line attributes it,
and estimated where it does not — marked accordingly. Budgets are
views.vl on the exhibit.

| # | step | expected gain | basis |
|---|---|---|---|
| 1 | **M21** — split std-world resolution from package loading so a `pkg::` entry hits `BASE_CACHE`; fix the second bypass at `analyzer.rs:40096` too | **−160 ms/keystroke** (1111 → ~950) | **measured**: `base` 160 ms on views.vl vs 0.0 ms on theme.vl, §1.3 |
| 2 | **M19** — the module analysis cache; and, as its first tranche, the `Type`-keyed memo on `check_generic_bound_satisfaction` (`analyzer.rs:4315`, `:4329`) | tranche: **−200 to −400 ms** of the 578 ms `checks`; full cache: down to the 285 ms fixed floor of §1.4 | tranche **estimated** from the E106 collapse ratio (32 answers / 17,802 questions) applied to the same shape; floor **measured** (§1.4's N=4 row) |
| 3 | **M22** — a watch round recompiles only the reaching leg | HMR, not the LSP: 4.0 s → ~0.6 s per round | measured by editor-perf, tracker M22 |
| 4 | **cancellation checkpoints** (§4.2) + the `reanalyze_dependents` revision check + adaptive debounce | no change to single-keystroke latency; **removes up to 2 of 3 concurrent analyses** under sustained typing | **estimated** from 950 ms CPU/analysis against a 150 ms debounce, §1.5(3) |
| 5 | **the keystroke path** (§2.1): two-sided anchor, declaration-shape stamp, per-module symbol index, tokens split syntax/semantic, sorted `entity_spans` | **15.3 ms → under 5 ms**, and — the point — **independent of codebase size** | **estimated**; the size-dependence it removes is measured (12.2 ms at 1,791 vs 14.7 ms at 5,000 for the same 468 tokens, §1.2) |
| 6 | **cache `lsp-context`** — `resolve_project_context` keyed on the manifest's content hash plus the reachability inputs | **−7.7 ms/keystroke**, −89 ms on the first | **measured**, §1.3 |
| 7 | **hoist and share the `refined_edges` memo** (§3.4); incrementalize the const-only reachability fixpoint | **−30 to −60 ms** of the 90 ms post-passes | **estimated** from the memo's per-site scope and the three call sites |
| 8 | **the incremental analyzer** — content-derived ids, a real module boundary, passes as queries | what remains between step 2's floor and 500 ms on a codebase that keeps growing | **needs its own paper** (§3.5) |

**Steps 1–3 are M21/M19/M22 as the charter requires.** One note on
ordering within them, from the measurement rather than from the filing:
**M21 is the better first move** — it is one seam, no new data structure,
a filed pin, and 160 measured milliseconds, where M19's full form needs
the module boundary that does not exist. M19's *first tranche* (the
`Type`-keyed memo on bound satisfaction) is independent of the boundary
and should be taken with M21, before the cache itself.

**Step 5 does not depend on steps 1–4** and is what the mandate names
first. It can run as a parallel lane the moment §2.1's states are ruled
on, which makes owner question Q1 the gating decision for the whole
paper.

---

## 6. The exhibit and the gate

### 6.1 The exhibit

kolt with lucide — 1,791 generated functions reachable from views.vl —
is the right "large codebase" because it is the owner's own, and it is
where every datapoint in E106 came from. But a gate **cannot** depend on
the owner's checkout. The exhibit must be generated, and this lane's
probe already generates it: a synthetic module of N functions of one
shape over a shared wrapper, plus a views-shaped consumer that calls
four of them. The series at N = 4 / 500 / 1,791 / 5,000 is what produced
§1.4's coefficient, and N = 1,791 is the gate's subject because it is
kolt's size.

### 6.2 The gate

A pin family under the **thread clock** — M15's method, and for M15's
exact reason: this order recorded loadavg 8 to 70 on one machine, wall
readings moved by 5×, and CPU readings did not. Every assertion is on
CPU time; wall is recorded beside it and never asserted.

**`keystroke_path_budget`** — on the generated exhibit at N = 1,791,
after an analysis has landed on the views-shaped file: fire semantic
tokens, inlay hints, completion and hover as one burst, and assert

- each individually under 10 ms of CPU, **and**
- the burst total under 10 ms of CPU — because §1.2 measured that the
  server answers a burst serially, so the sum is what the editor
  experiences.

**`diagnostics_budget`** — one keystroke on the same file, wait for
`publishDiagnostics`, assert **CPU under 500 ms**. Note what this
resolves: the debounce is a `tokio::time::sleep` and accrues **no CPU**,
so a CPU-clocked assertion is automatically debounce-exclusive. That is
the honest answer to owner question Q3 and it costs nothing to adopt.
Wall is recorded beside it with the loadavg, per M13.

**Red-first proof.** M15's discipline: a planted regression must red it.
For the keystroke gate, plant a whole-program walk in `semantic_tokens`
(restoring the shape §2.1 removes) and watch it red; for the diagnostics
gate, plant real work — a spin loop, **not** a sleep, since a sleep
accrues no CPU and would prove the gate blind rather than honest.

**Where it lives.** `crates/vilan-lsp/`, beside the `perf_baseline`
module `document.rs` already carries, `#[ignore]`d so the PR gate never
pays for it, with a seconds-long smoke pin that does — the discipline
`perf-baseline.md` established.

**When it can be built.** The moment step 1 or step 5 lands. The gate
does not depend on either: it can be written red today against the
current 15.3 ms and 1111 ms, and it is arguably *better* written red
first, so that the first path to land is the thing that greens it.

---

## 7. Ledger, determinations, and the owner's questions

### 7.1 Probe ledger

| # | probe | subject | result |
|---|---|---|---|
| P1 | scripted LSP session, warm/hot per provider | kolt-copy views.vl, theme.vl | §1.2; providers never wait; burst is serial |
| P2 | same | synthetic 5,000-function tree | §1.2; tokens 14.7 ms for the same 468-token file |
| P3 | `VILAN_PHASE_TIMING` per LSP analysis | both files | §1.3; `base` 160 ms vs 0.0 ms — M21 in the wild |
| P4 | synthetic series N = 4 / 500 / 1,791 | keystroke CPU | §1.4; ≈285 ms + 0.36 ms per function |
| P5 | completion position sweep | views.vl | scope 125 items 2.5 ms; `style::` 49 items 1.5 ms; inside a comment, 0 items 0.3 ms |
| P6 | staleness detector (hot payload vs settled payload) | comment-mode edits | 0 of 6 differed — as expected: a comment edit changes no token; the typing-mode run is what exercises it |
| P7 | `vilan check` phase line, CLI | views.vl at 1,791 and 5,000 | corroborates P3 outside the LSP |

All probes ran against a **copy** of kolt; the owner's tree was read and
never written. The compiler worktree was detached at `origin/next`
33692bb2 and nothing was committed to it.

### 7.2 Determinations

- **D1. E121's premise is corrected.** No request waits for the
  analysis. The keystroke path's problem is that every request
  recomputes over the whole program, and that its answers are
  unmarked-stale with no re-mapping beyond B38's tail. §1.5.
- **D2. The keystroke path is 1.5× over budget today and grows with the
  codebase** — 15.3 ms on kolt, 18.9 ms on the 5,000-function tree, for
  a file whose own token count never changed. §1.2.
- **D3. The diagnostics path is 2.2× over budget, and the budget is
  spent at ≈600 generated functions** on today's architecture:
  ≈285 ms + 0.36 ms per reachable function, per keystroke. §1.4.
- **D4. Superseded analyses are never cancelled**, so sustained typing
  runs up to three concurrent 950 ms analyses of which two are already
  garbage. This is invisible to single-keystroke measurement and is the
  best available explanation for the *session*-shaped half of E106.
  §1.5(3).
- **D5. M21 is the cheapest measured win in the paper** — 160 ms per
  keystroke, one seam, a filed pin — and should lead, with M19's
  `Type`-keyed memo tranche beside it. §5.
- **D6. A cross-keystroke memo cannot be keyed on `Type` as it stands.**
  The 2.2× memo is sound *within* an analysis only, because `Type`
  carries per-run argument ids. Cross-analysis memoization needs
  content-derived ids, which is the incremental-analyzer paper. §3.1.
- **D7. The gate should be CPU-clocked**, which makes it
  debounce-exclusive by construction and load-proof by M15's evidence.
  §6.2.

### 7.3 Owner questions

**Q1 — the gating one. Is stale-but-unmarked data acceptable on the
keystroke path, and does the answer differ for tokens and hints?** The
paper's recommendation (§2.1.2, §2.1.3): **tokens yes** — the middle
window you are typing in is syntax-only and therefore always right, and
a briefly mis-coloured identifier outside it is cosmetic. **Hints,
split** — withhold inside the middle window always, but serve the
anchors unchanged when stale rather than flickering them off and on,
because VS Code's only available "mark" is removal. Q1 gates step 5,
which is the step the mandate names first.

**Q2 — what debounce feels right?** It is 150 ms today. The paper
proposes adaptive, `clamp(0.3 × last analysis, 150, 500)` ms — a bridge
that retires itself once the analysis drops under 350 ms. Does the owner
prefer a fixed 150 ms and a longer queue, or a temporarily longer
debounce and fewer wasted analyses? (§4.3)

**Q3 — does the 500 ms include the debounce?** The paper reads it as
*keystroke to error on screen*, which does include it — and then
observes that a **CPU-clocked** gate excludes it automatically, since a
sleep accrues no CPU. If the owner means wall-inclusive, the analysis
budget is 350 ms, not 500; if CPU-exclusive, it is 500. The difference
does not change any step's ordering, but it changes what §6.2 asserts.

**Q4 — is a withheld hint acceptable where a possibly-wrong one would
otherwise appear?** Specifically: while you type on a line, that line's
inlay hints disappear until the analysis lands. The alternative is a
hint that may be a lie about a type.

**Q5 — is "semantic highlighting shouldn't lag" satisfied by
*syntactic* highlighting in the region being edited, upgraded to
semantic when the analysis lands?** That is the mechanism §2.1 relies
on, and it is worth confirming it matches what the owner sees when they
say the highlighting lags.

**Q6 — is the generated exhibit acceptable as the gate's subject?** The
gate cannot depend on `~/code/kolt`. The paper proposes a generated
1,791-function module of one shape. If the owner wants the gate to
track *kolt specifically*, that is a different instrument — a recorded
row in a ledger, not a red/green pin.
