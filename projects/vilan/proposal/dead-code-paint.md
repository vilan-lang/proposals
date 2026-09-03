# Dead-code paint for top-level items (E124)

> **Status: PAPER, 2026-09-03.** Measured against `next` at `635e3728`
> (post-Order-25, the b194 merge) on the dev machine — WSL2, load average
> 49–60 throughout, which is E114's measuring condition and means the
> *ratios* are the claim, not the absolute milliseconds. The exhibit is
> kolt at its 2026-09-03 state: one `[package]`, three entries
> (`client` browser, `server` node, `probe` node), 1,828 lines of
> hand-written source across 12 files plus the lucide build hook's
> 18,198-line generated module. No compiler change lands from this lane;
> the probe instrumentation described in §8 was reverted.
>
> **The finding that reframes the ruling.** The ruling of 2026-09-03
> defines a dead top-level item as one that "NO entry reaches … by the
> bundle's own definition." Measured, that definition does not survive
> contact with the emitter. Taking the union of the reachability walk
> across all three kolt entries and applying it to every top-level `fun`
> and module-level `let` in kolt's own source: **1,943 items, 84 reached,
> 1,859 gray — 95.7% of the package painted dead.** And that is the
> *narrow* reading. On the literal reading — an item is dead if the
> bundle does not contain it — **every `struct`, every `enum` and every
> `trait` in the language is dead**, used or not: they are type-level
> only, the transformer has no arm for them, and a `Point { x = 1, y = 2 }`
> emits `[ 1, 2 ]` with no declaration anywhere (§1.2, probe P2).
>
> The 1,859 are not one problem. They are four, and only one of them is
> the paint working as intended:
>
> | class | items | verdict |
> |---|---|---|
> | a `generated` root the manifest already declares (lucide) | 1,815 | exempt — §1.5 |
> | reached only from a `const` module-binding initializer | 27 | **walk hole** — §1.6 |
> | a binding the `context` pass rewrites out of existence | 1 | **walk hole** — §1.7 |
> | genuinely unreferenced (`get_client`, overlay's builder API) | 16 | the paint working |
>
> **The recommendation.** Build it — the true grays are real and worth
> finding — but not as ruled and not from the analysis in hand. Narrow
> the definition to the two item kinds the pruner has an opinion about
> (§1); close the two walk holes and honour the `generated` root *before*
> the first gray ships, because a suppressor marker cannot be the answer
> (it would take 1,859 of them on kolt, which is precisely the file-
> switching DX loss the owner's reservation 1 refuses); and compute the
> union out of band on a package clock, because the LSP analyzes the
> **open file** as the entry and for 9 of kolt's 12 files there is no
> `main` in the program at all — the walk has no root to start from (§2.1,
> probe P5).
>
> The union walk itself is cheap: **8.2 ms for all three kolt entries**
> at best, 13.3 ms typical under load, against E114's 6.2 ms for the
> unreachable-code walk. The union's *inputs* are not: one full analysis
> per entry, 0.4–2.0 s each, and M21's `BASE_CACHE` cannot amortize them
> because the edit that invalidates an entry's world is exactly an edit
> to a module that entry loads (§2.3).

§1 defines "reached" against the pruner as built and enumerates what
roots it. §2 is the multi-entry union — which analysis has it, which does
not, and what it costs. §3 is staleness. §4 is the library rule and the
workspace boundary. §5 is `[doc(hidden)]` and the reserved marker. §6 is
the pins, the false-gray ledger and the sequence. §7 is the owner's
questions. §8 is the probe ledger.

---

## 1. The definition, precisely

### 1.1 What the pruner is, and where

There is one reachability walk in the compiler and it is
`platform_color::Traversal` (`crates/vilan-core/src/platform_color.rs`,
`walk` at :319). It serves two consumers off one traversal:

- **admission** — `platform_color::check` (:64), `platform: Some(..)`:
  check, prune at the first off-platform node, chain-render the
  violation;
- **binding reachability** — `platform_color::reachable_bindings` (:251),
  `platform: None`: collect, prune nothing.

The emitter calls the second at `transformer.rs:2414` and keeps only the
module-level bindings it returns. Nothing else in the compiler computes
reachability; `bundle-splitting.md`'s route-chunk membership is the same
walk run once per arm, and the LSP's `platform_color::requirements` (:542)
is a *caller-ward* BFS over the same `edges` for an entry-independent
answer.

### 1.2 The walk's universe is functions, closures and module bindings — and nothing else

`CallGraph`'s node vocabulary is exactly `Node::Function(Id)` and
`Node::Closure(Id)` (`call_graph.rs:63`), plus module-level bindings
carried alongside as `global_references` / `initializer_calls`. There is
no node for a `struct`, an `enum`, a `trait` or an `impl` block, because
there is nothing to emit for them.

**Probe P1** — a package whose `main` calls one function, with an unused
struct, enum, function and binding beside it. Emitted:

```js
function used() {
	return 7;
}
console.log("" + used());
```

`struct Unused`, `enum Color`, `fun never_called` and `let never_read`
all emit nothing. So far so good — that is the tree-shake.

**Probe P2** — the same shapes, all *used*: a `Point` constructed and
read, a `Color` matched, a `trait Greet` with an impl called. Emitted:

```js
function greet(self) {
	return "(" + self[0] + "," + self[1] + ")";
}
const p = [ 1, 2 ];
const c = [ 0 ];
console.log(greet(p));
```

`struct Point` emits nothing. `enum Color` emits nothing. `trait Greet`
emits nothing. Only the impl *method* — an ordinary function — emits.
**A used type and an unused type are byte-identical in the bundle.**

> **Determination 1.** "Dead by the bundle's own definition" is not
> defined for `struct`, `enum`, `trait` or `impl` declarations, and
> cannot be made so by any refinement of the pruner: the pruner answers a
> question about emitted code, and types are not emitted. Top-level gray
> covers exactly two item kinds — **top-level `fun` (including impl and
> trait-impl members) and module-level `let`.** A type declaration nobody
> mentions is a real thing a user might want painted, but it is a
> *type-reference* analysis, not this one, and it is out of scope for
> E124. It should not be filed as a gap in this paper's design; it is a
> different analysis with a different index.

### 1.3 What roots reachability today

Two roots, both in `Transformer::assemble` (`transformer.rs:2370–2415`):

1. **`main`** — `global_scope.name_to_id_map["main"]`, resolved to a
   `Function`. A program without one is refused: *"Cannot execute program
   without a main function."* This is the only source-level root.
2. **the route gate** — `chunk_gate.swap_split` and `chunk_gate.preload`,
   passed as `extra_roots`. Nothing in source calls `View.swap_split`;
   the emitter selects it at a recognized `swap` call, so its module
   state (the pending signal) would otherwise be shaken out from under it
   (`bundle-splitting.md` §2).

That is the whole root set. Every other thing the ruling names as a root
is in fact reached through an ordinary edge, or is not a root at all:

| named in the ruling | what it actually is |
|---|---|
| `[rpc]` | **not a root.** `analyzer::service_impl_source` (:39570) *synthesizes source* for a `dispatcher(self)` method that routes each `[rpc]` method. That is real AST with real call edges, so kolt's `[rpc]` methods are reached from `main` through `store.dispatcher()` (`src/server.vl:20`). An `[rpc]` method on a service no entry installs is genuinely dead, and should gray. |
| `[expose]` | **not a root, and not an item marker.** `[expose]` is a *struct-field* attribute (`parsing.rs:4865`, in `parse_struct_field`) that gives the generated client a typed `RemoteSource` mirror. It has no bearing on item reachability. |
| derive-generated impls | **not a root, and invisible to paint.** Derives expand through `analyzer::derive_impl_source` into `DERIVED_SOURCE`, a sentinel `SourceId` with no path (`analyzer.rs:38495`, `derived_origin`). They never land in a user file's id range, so a file-scoped paint cannot reach them even by accident. |
| macros | **not a root.** Macro expansion produces source before analysis; the graph sees the expansion. Correct as the ruling states it. |
| `export` | **not a root and not a surface.** `export` re-exports an *import*; it creates no new item. |

**The edges the walk follows**, for the record (`platform_color.rs:365–435`):
`calls_of` + `initializer_calls_of` (resolved `Function`/`Closure`/
`External`; `Variant` is a no-op; `Indirect(Value)` adds nothing under
the creator rule; every other `Indirect` fans out through
`async_infer::dispatch_candidates_for`); `global_references_of` (F6 — a
reference runs the initializer); `function_references_of` (fn-to-closure
coercion charges at the reference site); `closure_children_of` and
`initializer_closures_of` (the creator rule); and
`program.drop_call_edges` (synthetic teardown, `destruction.md` §8).

### 1.4 Use the walk, never emission

Emission is **stricter** than the walk in two places: assembly keeps only
bindings `referenced_globals` saw emitted code touch
(`transformer.rs:2569`), and functions emit on demand through
`emit_instance`. Both are narrower than `reachable_bindings`, which
over-approximates deliberately — an unresolved dispatch keeps *every*
candidate.

> **Determination 2.** Paint reads the **walk**, never the emitted output
> and never `referenced_globals`. Over-approximation is the safe
> direction: a missed gray is late, a false gray is a lie. This also
> settles the const-in-a-function-body case for free (§1.6).

### 1.5 The `[platform]` fence, and the generated root

**The fence is not a pruning condition for paint.** In collect mode
`platform` is `None`, so `requirement_of`'s guard never fires and the
walk descends into off-platform code freely. The right answer to "is a
`[platform]`-fenced item dead on this platform or kept?" falls out of the
union without a special case: **each entry carries its own platform, so a
browser-only item is reached by the browser entry's walk and lives in the
union.** It is dead only if no entry of any platform reaches it. Do not
borrow `check_fences`' entry-independent fence roots (:147) — those exist
to check a *promise* for every possible instantiation, not to assert a
use.

**The generated root is a pruning condition, and it already exists.**
`[package] generated = "src/lucide"` (and `[library] generated`,
`manifest.rs:84` / :183) already declares a directory as machine-written
and already keeps `vilan fmt` off it. kolt's lucide module declares
**1,820 top-level `fun`s, of which the union reaches 5** — the app names
four icons (`search`, `paintbrush_vertical`, `messages_square`, `plus`)
out of 1,791. The paint as ruled would fade an 18,198-line file wall to
wall, on every keystroke, forever, and the correct user response is to do
nothing, because the file is regenerated from a pinned upstream tag and
its exhaustiveness is its purpose.

> **Determination 3.** A file under a declared `generated` root gets **no
> top-level gray**. Not a new key, not a new marker: the manifest key
> exists, kolt already sets it, and it already means "this is not code you
> maintain." Locals and unreachable-code paint may stay — they are
> file-local and harmless — but the top-level gray must not fire there.

### 1.6 Walk hole 1 — `const` module-binding initializers

`CallGraph::build` **deliberately drops** the edges out of a
`const`-marked module binding (`call_graph.rs:200–204`):

```rust
if const_exprs.contains(&initial) {
    continue;
}
```

with the stated reason: *"A `const`-marked initializer is evaluated by
the compile-time interpreter and serialized as a value, so at runtime it
is data, not code — skipped."* That is right for emission and wrong for
paint. **Probe P3**:

```
fun table_row(n: i32): i32 { n * n }
let squares = const table_row(7);
fun main() { print(i"{squares}"); }
```

emits `const squares = 49;` and nothing else. `table_row` is unreached,
unemitted — and deleting it breaks the build.

This is not hypothetical. It is **every gray in kolt's `theme.vl`**: 32
items, 5 reached, 27 gray, and all 27 trace to two lines —
`let _page_defaults = const page_defaults();` and
`let default_theme = const Theme::new(…)`. `Theme::new`, `to_declarations`,
`paint_ink1`, `ghost`, `script_label` and the rest are called only from
const initializers, so the graph has no edge to them at all.

The **in-body** case is already safe, and the reason is §1.4:
`CallGraph::build` runs *before* `const_eval::evaluate`
(`lib.rs:719` vs :752), so a `const` expression inside a function body
still contributes its call edge even though the emitter later folds it
away. **Probe P4** confirms it: `folded_in_body` emits nothing yet the
walk reports it reached.

> **Determination 4.** The paint's walk must follow const module-binding
> initializer edges. The cheapest correct shape is a second, paint-only
> collection pass that fills `initializer_calls` / `global_references` /
> `initializer_closures` for const bindings too, kept beside the emission
> graph rather than replacing it — the emission graph's skip is
> load-bearing (a const binding must not drag a `node:` import into a
> browser bundle) and must not be disturbed. **This is a compiler change,
> not an LSP change, and it is the first slice.**

### 1.7 Walk hole 2 — a binding the `context` pass rewrites away

`lib.rs:719` reads:

```rust
let call_graph =
    context::thread_contexts(program).unwrap_or_else(|| call_graph::CallGraph::build(program));
```

`thread_contexts` **rewrites the program** — an ambient context stops
being a module-level binding read and becomes a hidden parameter — and
returns the graph for the rewritten program. So the graph the walk uses
is the post-rewrite one, in which the context binding has no readers left.

kolt's `src/app_context.vl:14` is exactly this:

```
let app_context = Context<AppContext>::new();
fun get_route(): SignalCell<Route> { app_context.get() }
```

`get_route` is reached; `app_context` is not. The emitted client contains
no `Context` at all, and `get_route` compiled to

```js
function get_route($gh) {
	return $gh[2];
}
```

The binding is genuinely not a runtime entity — the walk is not wrong
about the bundle. But `let app_context = Context<AppContext>::new();` is
a live, load-bearing declaration in the ambient-owner idiom
(`ambient-owner.md`), the shipped way to hold app-wide state, and graying
it tells the user to delete the thing the whole file exists for.

> **Determination 5.** A module-level binding consumed by
> `context::thread_contexts` is exempt from top-level gray. The pass
> knows which bindings it rewrote; it must record them
> (`program.context_bindings`, or a flag on the rewrite) rather than have
> the paint re-derive it from a type test on `Context<_>`.

### 1.8 The jumpiest true gray — a trait impl member

The walk's dispatch refinement is **per instantiation**: a resolved
receiver descends into exactly the impl member that instantiation selects;
only an unresolvable receiver falls back to every candidate. **Probe P4**
declares `impl Sq with Shape` and `impl Ci with Shape`, constructs only a
`Sq`, and the dump reports `Sq::area` reached, `Ci::area` unreached.

That is *correct* by the definition and it is the definition's sharpest
edge: **whether a trait impl member is gray depends on which types are
constructed anywhere in the package.** Construct one `Ci` in any entry
and twelve grays across the file vanish at once. Nothing is wrong here,
but it is the class most likely to read as noise, and §6.2 pins it.

### 1.9 What is not a root, and needs no rule

- **Build hooks.** `[build] run` and `[[build.hook]] run` are shell
  command lines (`manifest.rs:618–626`); kolt's is
  `node scripts/lucide.mjs`. They root nothing in Vilan. A hook that runs
  *Vilan* code does so through a declared entry, which the union already
  covers.
- **Test entries.** The language has none. If they arrive they are
  entries, and the union covers them by construction — which is the
  argument for expressing them as `[entry.<name>]` rather than as a
  parallel concept.

---

## 2. The multi-entry union: which analysis computes it, and where

### 2.1 The structural obstacle: the LSP's program has no entry in it

The LSP analyzes **the open file as the entry**. `Program::sources`'
own doc (`analyzer.rs:38116`): *"`sources[0]` is the entry file, the rest
are `std` modules."* `Document::analyze` passes the open file's path as
`entry_path` (`document.rs:1163`).

So when the user edits `src/store.vl`, the program in hand is rooted at
`store.vl`. It has no `main`.

**Probe P5** — the probe reports `NO-MAIN` for every kolt file that is
not one of the three declared entries:

```
check src/store.vl    → NO-MAIN  functions 1094  graph-nodes 1212
check src/views.vl    → NO-MAIN  functions 3001  graph-nodes 3163
check src/overlay.vl  → NO-MAIN  functions  974  graph-nodes 1026
check src/shared.vl   → NO-MAIN  functions  946  graph-nodes  979
check src/client.vl   → main present, 3002 functions, 624 ids reached
```

**For 9 of kolt's 12 hand-written files the reachability walk has no root
to start from.** The ruling's framing — "per landed analysis of one entry
the LSP has that entry's reachability" — holds only when the open file
*is* an entry, which on kolt is 3 files out of 12 and in general is the
minority of any package.

> **Determination 6.** The union cannot be assembled from "the entry's
> own analysis plus the other entries' cached reachability." There is no
> entry analysis in hand at all for most files. **Every** term of the
> union — including the one for the entry the open file belongs to — must
> come from a separately computed, cached per-entry reachability set.

### 2.2 What the walk costs, once you have the graph

The measured walk (`reachable_nodes`, the same traversal returning
visited node ids as well as bindings; min of 25 runs per analysis, so
the number is a floor, not a mean):

| entry | functions | graph nodes | module bindings | walk (best) | walk (typical, loadavg ≈57) | ids reached |
|---|---|---|---|---|---|---|
| `client` | 3,002 | 3,166 | 44 | **3.87 ms** | 8.5–12.5 ms | 624 |
| `server` | 1,253 | 1,366 | 19 | **2.23 ms** | 2.2–2.7 ms | 542 |
| `probe`  | 1,086 | 1,174 | 16 | **2.12 ms** | 2.1–2.4 ms | 325 |
| **union** | — | — | — | **8.22 ms** | **13.3 ms** | — |

Against E114's ledger — 6.2 ms for the unreachable walk, 2.8 ms for
locals, 65 ms for imports on the same exhibit — the union is **the second
most expensive thing on the debounced diagnostics path and roughly 2× the
walk E114 had to optimize 19× to afford.** It is affordable, but it is
not free, and it is not something to add without the pin E114 had
(§6.1).

Two notes on the shape. The walk is *not* proportional to the file being
edited; it is proportional to the entry's whole program, which is E121's
finding restated (§1.4a there: cost grows with the codebase, not the
file). And the client's walk is 1.8× the server's for 2.3× the nodes,
so the coefficient is roughly linear in graph nodes at **≈1.2 µs per
node** at best, ≈3 µs under load.

### 2.3 What the union's *inputs* cost, and why the base cache cannot help

The walk needs a `CallGraph`, which needs a completed analysis. Measured
per entry (`VILAN_PHASE_TIMING`, cold CLI process, so `BASE_CACHE` starts
empty — the LSP's base would be warm):

| entry | `load+walk` | `base` | `checks` | `post-passes` |
|---|---|---|---|---|
| `client` | 839–1,191 ms | 702–1,374 ms | 1,324–2,051 ms | 811 ms |
| `server` | 1,222 ms | 264 ms | 423 ms | — |
| `probe` | 393 ms | 90 ms | 122 ms | — |

**Analyzing the other two entries per keystroke is not on the table**, and
M21's `BASE_CACHE` does not rescue it. The cache stores the pre-entry
`World` and is content-validated per hit: on a key match it re-reads every
recorded non-entry source and compares hashes (`analyzer.rs:41345`), with
the document overlay consulted first, so **a buffered edit to a sibling
module evicts the world of every entry that loads it.** M21 put the
`pkg::` sibling set into the key for exactly this reason (*"sibling
modules LOAD INTO the world"*). The common editing case — typing in
`views.vl`, which `client.vl` loads — is precisely the case the cache
cannot serve.

### 2.4 The recommendation: a package-level union on its own clock

Not per keystroke, not on the diagnostics path's own analysis. A
**per-package union task**:

- **Trigger.** The union recomputes when a package source's *content*
  changes and the editor is at rest: `did_save` (which already analyzes
  inline and sweeps dependents, `main.rs:2248`) plus an idle timer well
  above `DEBOUNCE_MS` (150 ms). It never runs inside the debounce.
- **Work.** One analysis per declared entry, off the request path
  (`spawn_blocking`, as `analyze_and_publish` already is), then one
  `reachable_nodes` walk per entry, then the union.
- **Product.** A set of **`(canonical path, name span)` keys**, never
  entity ids. Ids are minted per analysis and are not comparable across
  the three programs — the union in §1's exhibit was taken in Python on
  `(path, span)` for exactly this reason. `Function::name_span`
  (`analyzer.rs:707`) is the natural key: unique per declaration, already
  the anchor for go-to-definition and rename.
- **Cache.** Per package root, invalidated by content hash of the entry
  set's transitive closure — which is what the analysis already computes
  and what `Document::depends_on` already records.
- **Consumer.** `publish::diagnostic_groups` (`publish.rs:372`) gains a
  fourth `faded` producer beside the three E114 shipped, reading the
  union rather than the program in hand.

The entries themselves come from the manifest, which the LSP already
parses on **every** analysis (`resolve_project_context`,
`document.rs:111`) and already iterates per entry —
`platform_color::file_platform_choices` (:885) runs
`package_modules_reachable_from` once per declared entry, per keystroke,
today, to decide the open file's platform color. **The entry list is in
hand and the per-entry iteration is already paid for**; what
`ProjectContext` does not do is keep the entry list after the call
(`document.rs:39`), and it will have to.

> **Determination 7.** The per-entry reachability sets are cached at
> package granularity, keyed by `(canonical path, name span)`, computed
> off the debounced path, and the paint serves the last completed union.
> The LSP has no per-entry cache today — every cache in `Backend` is
> per-URI or per-path — so this is new machinery, and it is the largest
> single piece of work in the item.

### 2.5 The cheaper first slice, if the union is too much

`file_platform_choices` already computes, per entry, per keystroke, the
set of package modules that entry reaches — a **module-level** walk over
the import graph (`analyzer.rs:40981`, whose own doc says *"the language
server asks it per keystroke"*). Its union across entries is free, it is
already correct, and it answers a coarser question: **is this whole file
reached by any entry?**

A file no entry imports is unambiguously dead, has none of §1's four
false-gray classes (a `generated` root would still need the exemption),
and needs no new cache. It is worth naming as a separable slice because
it is the part of E124 that costs nothing, and because a package with a
genuinely orphaned module is a more common and more valuable find than a
single unreferenced `fun`.

---

## 3. Staleness

### 3.1 The precedent, and why it does not transfer unchanged

E121's Q1 ruling: *"stale-but-unmarked on the keystroke path: tokens YES,
hints SPLIT (withheld inside the edit window, otherwise served
unchanged)"*, with the reasoning at `editor-latency.md` §2.1.3 — *"a
wrongly-coloured identifier is a cosmetic error that the next analysis
corrects … a hint that is wrong is not a cosmetic error — it is a lie
about a type"* — and Q4: *"a withheld hint beats a possibly-wrong one."*

A top-level gray is neither. It is not cosmetic like a token colour: a
gray is a **claim** — "nothing in this package uses this" — and the user's
response to it is to delete code. And it is not local like a hint: the
fact that falsifies it lives in *another file*, so no amount of anchor
re-mapping in this file can rescue it. E121's own Case 4 names this
exactly: *"another module was edited — this file's analysis is stale
wholesale, and no amount of local anchoring helps."*

### 3.2 The asymmetry that settles it

The two staleness errors are not equally bad:

- **A stale gray on a now-used item** — the user just added the first
  call in another file. The paint says "dead" about live code. This is
  the worst outcome paint has.
- **A missing gray on a now-unused item** — the user just deleted the
  last call. The paint is silent about dead code. It is *late*, and
  nothing bad follows from lateness.

So the rule is asymmetric, and it is the direct analogue of E121 Q4 and
Q5 applied to the one half that can lie:

> **Determination 8 — the staleness rule.**
>
> **A top-level gray may be arbitrarily stale in the direction of fewer
> grays, and must never be served stale in the direction of more.**
> Operationally: when a file changes, every gray whose item lives in a
> file that the changed file could add a use to is **withdrawn
> immediately** and restored only when the union recomputes. A use can
> only be added from a file that imports the item's module (or from the
> item's own file), which is a relation the LSP already tracks as
> `Document::depends_on` and already sweeps in `reanalyze_dependents`
> (`main.rs:1485`) — inverted, it is exactly the set to withdraw.
>
> Withdrawal is instant and needs no analysis. Restoration is slow and
> rides §2.4's clock. This is E121 Q5's "upgraded on land" with the
> polarity that matters: **downgraded on edit, upgraded on land.**

The consequence, stated plainly so it is not discovered later: **during
an active editing burst, top-level gray in the touched dependency cone is
off.** It returns when the editor settles. That is correct for a paint
whose value is "you may delete this" — it is acted on at rest, not
mid-keystroke — and it is the opposite of E114's locals and unreachable
paint, which are file-local, cheap, and stay on throughout.

### 3.3 The gates E114 already established, inherited unchanged

All three E114 producers are gated on
`self.diagnostics.is_empty() && !self.is_stale()` (`document.rs:3252`,
:3303, :3357). Top-level gray inherits that gate and needs it more, for
the reason `editing-dx.md` §2.2 documents: a salvaged parse can lose a
whole block (`parse_block` skips the balanced region, `parsing.rs:2066`)
or the entire file tail (`scan_balanced` returns `None` for a
never-closing region, :816). **A smaller program reads to a reachability
walk as a deader one.** A broken file anywhere in the package must
suppress the package's grays, not merely its own — which the §3.2 rule
already delivers, since a broken file is a changed file.

E114's `_`-led exemption also carries: `let _page_defaults = const
page_defaults();` in kolt is `_`-led *and* const, and the `_` alone
should have kept it quiet.

---

## 4. The library rule and its boundary

### 4.1 The rule, restated with its structural reason

A `[library]` gets **no top-level gray**. The reason is not policy, it is
the manifest: `struct Library` (`manifest.rs:171`) has **no `entry`, no
`entries`, no `target`, no `default_entry`** — it carries `layer` instead.
Validation refuses entries on a non-package outright
(`manifest.rs:1092`): *"a library has no entries; a workspace's entries
live in its member packages."* There is no root to walk from, so there is
no union, so there is nothing to say. Locals and unreachable code stay
painted; they need no entry.

### 4.2 The boundary: a workspace member library consumed by a sibling

**Is the sibling's reachability available?** Yes, mechanically. `[project]
packages` lists members (`manifest.rs:225`); a member depends on a sibling
by path (`DependencySource::Path`, resolved at `manifest.rs:1919`);
`resolve_workspace` walks the graph and the `member` flag rides into
`PackageSpec` and into the `BaseCacheKey`'s workspace fingerprint
(`analyzer.rs:41300`), where E90's demotion carve-out already treats a
member's code as the user's own. So the workspace is known, the member
relation is known, and the sibling app's entries could in principle be
walked.

**Should it count? No.** Three reasons, in order of weight:

1. **It re-creates the fork risk the rule exists to prevent.** The owner's
   reservation 2 is solid-js: signals over a wire needed internal
   ownership functions Solid does not export, and the cost was forking the
   whole package. A member library is `[library]` because someone means it
   to be reusable. Graying on "the one sibling that consumes it today does
   not call this" is an instruction to delete surface that the *second*
   consumer needs — and the second consumer is the next commit.
2. **The cost multiplies in the wrong shape.** kolt's union is three
   analyses for one package. A member library's union would be over every
   dependent member's entry set, so the per-package task of §2.4 becomes a
   per-workspace task whose cost is the workspace's total entry count. The
   union is already the largest cost in the item.
3. **It destroys the rule's legibility.** *"A `[library]`'s items are
   never gray"* is a rule a user can hold in their head. *"…unless it is
   a workspace member, in which case it is grayed against its dependents'
   entries"* is a rule that will be experienced as the paint being
   randomly wrong in one repo and right in another.

> **Determination 9.** A `[library]` gets no top-level gray, workspace
> member or not. The `member` flag is not a licence to gray.

The obvious counter — "but in a closed workspace the library really does
have a complete consumer set" — is real, and it is an *opt-in*, not a
default. It changes the design, so it is Q3 in §7 rather than a
determination here.

### 4.3 The mirror case, and a caution

A `[package]` may also be imported — nothing stops a path dependency on
one — but a `[package]` has entries, so the union is defined and the gray
fires. If someone consumes a `[package]` as a library, its items will be
grayed against *its own* entries and the consumer's uses will not count.
That is a real trap. It is not new (the same reachability already
determines what a `[package]` build emits), and the fix is to declare the
thing a `[library]`, which is what the manifest sections are for. Worth a
line in the diagnostic's steer, not a special case in the design.

---

## 5. `[doc(hidden)]`'s role, and the marker that is reserved

### 5.1 `[doc(hidden)]` — shipped, and orthogonal

`[doc(hidden)]` parses on functions in the ordered attribute prefix
(`parsing.rs:4499`, `parse_doc_hidden_attribute`) and is recorded on the
function; it omits the item from completion and nothing else. It shipped
2026-07-02 (`transport-rpc.md`:238) and std uses it on externs.

Its role in E124 is exactly what the ruling says and no more: it is the
**soft surface tool for a `[library]`** — curate what a consumer
*discovers* without forbidding access, which is the whole answer to the
under-exported-package fork. It is the thing a library author reaches for
instead of the top-level gray they are not going to get.

> **Determination 10.** `[doc(hidden)]` neither causes nor suppresses
> gray. An item can be undiscoverable and still live; an item can be
> prominent and still be dead. Coupling them would make the completion
> list a place where dead-code decisions get made.

### 5.2 The reserved marker

Reserved, named, and **not built**:

- **Spelling.** `[keep]` — a bare marker attribute, no argument, parsed
  by `eat_marker_attribute("keep")` beside `[must_use]` in the ordered
  prefix `[deprecated] [extern] [must_use] [rpc] [trait_only]
  [doc(hidden)] [platform]` (pinned in `bundle-boundaries.md`:244), added
  to `KNOWN_ATTRIBUTE_MARKERS` (`parsing.rs:647`) and to the two
  highlighting grammars the three-place rule and `grammar_sync.rs` hold
  to it.
- **What it suppresses.** Exactly one thing: **the top-level dead-item
  gray on the item it marks.** Not unused imports, not unused locals, not
  unreachable code, not completion.
- **What it does not do.** It does not keep the item in the bundle. The
  pruner still shakes it out; nothing about emission changes. `[keep]` is
  a claim about the *editor*, and the gap between that and what the name
  promises is the strongest argument for a different spelling — `[used]`,
  or `[reachable]`, says what is actually being asserted. Raised as Q4.
- **Why it is not built.** The ruling's condition — *"add it only when the
  first false gray appears"* — has been met three times over in §1, and
  in every case the marker is the wrong instrument. Shipping the ruled
  paint on kolt with `[keep]` as the escape hatch would require **1,859
  markers**, 1,815 of them in a generated file that a build hook rewrites
  on the next tag bump. **A suppressor marker at that density *is* the
  file-switching DX loss the owner's reservation 1 refuses.** The
  exemptions of §1.5–1.7 are the answer; the marker stays reserved for the
  case they do not cover — a genuinely reflection-reached item — which
  kolt does not have.

---

## 6. Pins, the false-gray ledger, and the sequence

### 6.1 Pins the build will need — per case, not per example

E114's lesson was that a *pin*, not a budget, caught the 118 ms regression
("broke the recolor pin's settle deadline under load"). The same shape
applies.

**Definition (§1)**
1. A top-level `fun` no entry reaches is gray.
2. A module-level `let` no entry reaches is gray.
3. A `struct`, `enum`, `trait` and `impl` block is **never** gray, used
   or unused — the both-directions pin, because the failure is
   silent-and-total.
4. A `fun` reached only through a `[service]`'s synthesized
   `dispatcher()` is **not** gray; the same `[rpc]` method on a service no
   entry installs **is** gray.
5. A derive-generated member never produces a range in a user file.
6. A `fun` reached only from a `const` module-binding initializer is
   **not** gray (§1.6).
7. A `fun` reached only from a `const` expression inside a function body
   is **not** gray (the already-safe half — pin it so a reordering of
   `post_analysis_passes` cannot silently break it).
8. A binding rewritten by `context::thread_contexts` is **not** gray
   (§1.7).
9. Nothing under a declared `generated` root is gray (§1.5).
10. A `[platform("browser")]` item reached by the browser entry is **not**
    gray in a package whose other entries are node.
11. A trait impl member for a type constructed nowhere **is** gray; the
    same member becomes not-gray when any entry constructs the type
    (§1.8) — one pin, two states.

**Union (§2)**
12. An item reached by exactly one of three entries is not gray (the
    union is a union).
13. Editing a non-entry file still produces the package's grays — the
    `NO-MAIN` case (P5), which is the pin that would have caught the
    ruling's premise.
14. A package with one entry and a package with three produce the same
    grays for an item only one of them reaches.

**Staleness (§3)**
15. Adding the first use of a grayed item **in another file** withdraws
    the gray before the union recomputes (§3.2 — the lie-prevention pin).
16. Deleting the last use of an item does **not** have to gray it
    immediately (lateness is allowed — the pin asserts the paint is not
    required to be fast here, so a later optimization cannot be justified
    by it).
17. A broken parse anywhere in the package suppresses the package's
    top-level grays.

**Library (§4)**
18. A `[library]`'s top-level items are never gray.
19. A `[library]` that is a workspace member consumed by a sibling
    `[package]` is still never gray (§4.2).

**Cost (§6.3)** — the settle-deadline pin, in E114's shape, asserting the
diagnostics path still settles with the fourth producer added.

### 6.2 The false-gray ledger — the worst outcomes, ranked

| # | case | scale on kolt | mitigation |
|---|---|---|---|
| 1 | a generated module painted wall to wall | 1,815 items, 18,198 lines | §1.5, the `generated` manifest key |
| 2 | const-initializer-only callees | 27 — 26 of them in `theme.vl` | §1.6, a paint-only graph pass |
| 3 | every type declaration in the language | all of them | §1.2 / D1, narrow the definition |
| 4 | a `Context` binding the compiler rewrites away | 1 | §1.7, record the rewrite |
| 5 | a stale gray on an item just used from another file | unbounded | §3.2, withdraw on edit |
| 6 | a broken parse shrinking the program | unbounded | §3.3, E114's gate, package-wide |
| 7 | a `[package]` consumed as a library | — | §4.3, steer to `[library]` |

Cases 1–4 are certain and measured; 5–6 are the mechanism's own; 7 is a
user error the steer should name.

### 6.3 Cost, against the diagnostics path

The union walk adds **8.2 ms best / 13.3 ms typical** on kolt, against
E114's 6.2 ms + 2.8 ms + 65 ms. On the §2.4 design it is not paid on the
debounced path at all — the debounced path reads a cached set — so the
diagnostics-path cost is a hash lookup plus a span map. The real cost is
**three full analyses per union recompute** (0.4–2.0 s each, cold), paid
on the save/idle clock, off the request path.

### 6.4 Sequence — one lane, four slices, red-first

- **S1 — close the walk holes (compiler).** The paint-only const-edge
  pass (§1.6) and the context-binding record (§1.7). Pins 6, 7, 8.
  Nothing user-visible ships; this is the slice that makes everything
  after it honest, and it must be first.
- **S2 — the definition and the per-entry set (compiler).** A supported
  `reachable_items(program, entry) -> Set<(path, name_span)>` beside
  `reachable_bindings`, narrowed to `fun` + module-level `let`, honouring
  the `generated` root. Pins 1–5, 9–11.
- **S3 — the union cache (LSP).** `ProjectContext` keeps the entry list;
  a per-package union task on the save/idle clock; the cache keyed by
  content hash. Pins 12–14, and the cost pin.
- **S4 — the paint and the staleness rule (LSP).** The fourth `faded`
  producer in `publish::diagnostic_groups`, `HINT` + `Unnecessary` as
  E114 established, and the withdraw-on-edit rule over the inverted
  `depends_on` relation. Pins 15–17.

The library rule (pins 18–19) is a guard in S2 and costs nothing.

S1 and S2 are worth landing even if S3/S4 are deferred: they make
`vilan build`'s tree-shake describable and give §2.5's free
module-level slice somewhere to sit.

---

## 7. Questions for the owner

Only where the answer changes the design.

**Q1 — Is the narrowed definition acceptable?** §1.2 restricts top-level
gray to `fun` and module-level `let`, because `struct`/`enum`/`trait`
emit nothing whether used or not and the pruner has no opinion about
them. An unreferenced `struct` is a real thing a user might want faded,
but finding it is a type-reference analysis, not this one. **Recommend:
accept the narrowing and do not file the type case as a gap in E124.**

**Q2 — Is a paint that is off during an editing burst acceptable?**
§3.2's asymmetric rule withdraws grays in the edited dependency cone
immediately and restores them only when the union settles, so during
active typing in `views.vl` the grays in `theme.vl` are absent rather
than stale. The alternative is serving them stale — which is E121 Q1's
"tokens YES" stance — and accepting that the paint can call live code
dead for one union's clock. **Recommend: withdraw. A gray is a claim the
user acts on by deleting, and E121 Q4's "withheld beats possibly-wrong"
applies to claims more than to hints.**

**Q3 — Should a workspace `[library]` be able to opt in to gray?** §4.2
decides no by default. A library author whose consumers are all inside
the workspace has a genuinely complete picture, and the honest surface
for saying so is a manifest key (`[library] closed = true`, or similar),
not a per-item marker. It is one line of manifest against per-item
annotations, so it does not re-open reservation 1. **Recommend: not in
v1; revisit when a workspace library exists to want it.** (Today none
does.)

**Q4 — Is `[keep]` the right spelling for the reserved marker?** It
suppresses an editor decoration and changes nothing about emission, so
the name promises more than it delivers; `[used]` or `[reachable]` states
the actual assertion. The marker is not built either way, but the
spelling is the thing that gets copied into papers and grammars before it
is built. **Recommend: reserve it under a name that says "this is
reached", not "keep this".**

**Q5 — Should the free module-level slice (§2.5) ship first, on its
own?** "This file is imported by no entry" is already computed per
keystroke, has none of the false-gray classes, needs no cache, and is
arguably the more valuable find. It is also a different decoration (a
whole file, not a range) and might belong in the explorer rather than the
editor. **Recommend: yes as a slice, but decide where it renders before
building it.**

---

## 8. The probe ledger

All probes against `next` at `635e3728`, release build, WSL2, load
average 49–60. The instrumentation was two throwaway additions —
`platform_color::reachable_nodes` (the same `Traversal`, returning
visited node ids as well as bindings) and an env-gated block after
`install_call_graph` that timed the walk min-of-25 and dumped
`(kind, canonical path, span, name, reached)` per item — both reverted
before this paper was committed.

| # | question | answer |
|---|---|---|
| P1 | do unused top-level items emit? | no — `struct`, `enum`, `fun`, `let` all absent from the bundle |
| P2 | do *used* types emit? | no — `Point`/`Color`/`Greet` emit nothing; `Point { x = 1, y = 2 }` → `[ 1, 2 ]` |
| P3 | is a const-module-binding callee reached? | **no** — `table_row` unreached and unemitted; deleting it breaks the build |
| P4 | is an in-body const callee reached? is a trait impl member per-instantiation? | reached = yes (graph precedes const-eval); `Sq::area` reached, `Ci::area` not |
| P5 | does a non-entry file's analysis have a root? | **no** — `NO-MAIN` for `store.vl`, `views.vl`, `overlay.vl`, `shared.vl` |
| P6 | what does the union walk cost? | 3.87 / 2.23 / 2.12 ms best (client/server/probe), 8.22 ms union |
| P7 | what does one entry's analysis cost? | `load+walk` 393–1,222 ms, `checks` 122–2,051 ms, cold |
| P8 | what would the paint gray on kolt? | 1,943 items, 84 reached, **1,859 gray** — the §1 table |

**The union, per file** (all three entries, `(path, name_span)` keys):

| file | items | reached | gray |
|---|---|---|---|
| `src/lucide/lib.vl` | 1,820 | 5 | 1,815 |
| `src/theme.vl` | 32 | 5 | 27 |
| `src/overlay.vl` | 31 | 19 | 12 |
| `src/store.vl` | 16 | 16 | 0 |
| `src/views.vl` | 13 | 13 | 0 |
| `src/interact.vl` | 8 | 8 | 0 |
| `src/prefs.vl` | 7 | 6 | 1 |
| `src/app_context.vl` | 5 | 2 | 3 |
| `src/routes.vl` | 5 | 5 | 0 |
| `src/client.vl` | 2 | 1 | 1 |
| `src/probe.vl` | 2 | 2 | 0 |
| `src/server.vl` | 2 | 2 | 0 |
| **total** | **1,943** | **84** | **1,859** |

std and dependency code in the same programs: 1,152 items, 452 reached.
Not painted — not the user's code — but the ratio is the same story, and
it is N48's territory.

**The true grays, in full** — kolt's hand-written source with the
§1.5–1.7 exemptions applied, each one confirmed by grep:

- `app_context.vl` — `get_app_context`, `get_client`: declared, never
  called anywhere. (The `app_context` binding beside them is §1.7's
  exemption, not a find.)
- `theme.vl` — `themes`: imported by `prefs.vl` and never used, so
  E114's unused-import paint already flags the import. The other **26**
  grays in the file are all §1.6: `Theme::new`, `to_declarations`,
  `page_defaults` and the `paint_*` / `ink*` accessors are called only
  from `const` initializers, and the `var_*` bindings are unreached only
  because those accessors are.
- `prefs.vl` — `Prefs::notify`.
- `overlay.vl` — twelve builder members (`menu`, `below`, `beside`,
  `dismissable`, `margin`, `strategy`, `panel_style`, `is_open`,
  `open_at`, `open_at_pointer`, `toggle`, `has_scrim`). Four are
  referenced only from commented-out doc examples in the same file;
  `open_at` is called only from `open_at_pointer`, which is itself dead.
  A small overlay API the app does not currently call.
- `client.vl` — none. `_static_estate` is `_`-led *and* const, so E114's
  existing exemption and §1.6 both cover it.

**Sixteen true finds out of 1,859 grays** is the number that sizes this
item. The finds are real and worth having — twelve of them are a whole
unused API surface, which is exactly what the paint is for. The ratio is
why the exemptions come first.
