# Bundle boundaries — a function attribute that marks a fetch seam (M18)

> **Status: DESIGN NOTE 2026-09-01 — pushed to the extremes at the owner's
> request; recommendation awaiting a ruling.** Nothing here is built. The
> owner's idea, verbatim intent: bundle splitting's key issue is finding the
> boundaries, so let a function ATTRIBUTE mark one — the compiler sees the
> calls to `lucide_icon`, fetches the separate bundle first, then runs the
> code. The owner's own caveat is the charge: *"I haven't pushed it to the
> extremes yet so I don't know if it'll hold up."* This paper pushes. The
> short answer is that the **idea holds and one door is clearly right**
> (§3.4), that the **shipped chunk runtime does not** carry it without two
> named changes (§1.6, §4.1), and that **one extreme genuinely breaks**
> (nested boundaries, §4.1) with a measured, one-line-shaped fix.
>
> Every number below is a measurement taken for this paper against
> `0.40.0 (f30897ee0)`; the ledger is §6.

## 0. The thesis, and where it departs from `bundle-splitting.md`

`bundle-splitting.md` §0 states a doctrine this proposal appears to
contradict, and the contradiction is worth facing on the first page:

> **Thesis: the split is inferred, not annotated.** No keyword […] an
> annotation would be the Solid mistake with extra steps.

That thesis was about *route* boundaries, and about them it was right: the
router `match` already is a split point, so annotating it would have been
ceremony over information the compiler already had. The lucide measurement
(kolt.local 038) is the counterexample the thesis did not anticipate. There
is no structural seam anywhere near `lucide_icon`. It is an ordinary
function in an ordinary module called from four ordinary call sites, and it
drags 940 KB behind it. Nothing in the program's *shape* says "this is a
boundary" — the only thing that says so is the *weight*, and weight is not
a seam the analyzer can find by pattern-matching syntax.

So the honest statement is not "annotation was wrong, annotation is right",
it is: **inference finds structural boundaries; nothing but a declaration
finds a weight boundary.** The two mechanisms are complementary, they share
the entire runtime, and the doctrine survives intact if the attribute is
held to the same measure-first bar route splitting was (§7 D8).

The second half of the thesis — "the Solid mistake with extra steps" — is a
real hazard and this design must answer it. Solid's `lazy()` is easy to
forget because forgetting it is *silent*: the app still works, just fatter.
The answer here is §7 D9: the toolchain already measures both emissions
(`chunks.rs`'s `SplitCost`, shipped) and already warns when a split costs
more than it defers. The same instrument, pointed at boundary candidates,
turns "easy to forget" into "reported on every build".

## 1. What exists — the route boundary, exactly as built

Everything M18 needs at runtime is already in the tree, and it is worth
being precise about what it is, because three of its properties are load
bearing in ways that only show up when boundaries stop being route arms
(§1.6). The fixture is `crates/vilan-cli/tests/split/`; the planner is
`crates/vilan-core/src/chunks.rs`; the emitted shape below is the fixture's
byte-pinned golden, reproduced for this paper (probe P1).

### 1.1 The partition

`chunks::plan` recognizes exactly one shape: a `match` on the parameter of a
`View.swap` render closure (`chunks.rs`, `splittable_sites`). It then runs
the reachability walk once from the eager root — `main` plus every
module-level binding, with the recognized arms' call edges held out — and
once per arm. Membership is a three-way verdict:

- reachable from the eager root → **eager**;
- reachable from exactly one arm and nothing else → **that arm's chunk**;
- reachable from two or more arms → **shared, which v1 sends eager**.

Two residence rules ride along: std is never chunked (`chunks.rs`'s
`std_sources` guard — it is the shared runtime, eager by residence), and app
code is chunkable wherever it lives, because entry-only attribution planned
zero chunks for the common real shape (pages in a `views` module).

### 1.2 The registry, and the forwarders

Cross-chunk references ride a runtime registry, not ESM exports
(`bundle-splitting.md` §3). The emitted eager bundle carries five helpers
(`__chunk_registry`, `__chunk_arm`, `__chunk_ready`, `__chunk_load`,
`__chunk_preload`) and, at the end of the module, the url map and the
registrations:

```js
__vilan_chunks.url[0] = "app.Route_Home.js";
__vilan_chunks.url[1] = "app.Route_Docs.js";
__vilan_chunks.url[2] = "app.Route_NotFound.js";
__vilan_chunks.fn.$X = $X;
__vilan_chunks.fn.$ai = $ai;
__vilan_chunks.fn.LABEL = LABEL;
__vilan_chunks.fn.panel = panel;
__vilan_chunks.fn.view = view;
```

A chunk is a module that reads what it needs out of the registry, defines
its own functions, and registers them back:

```js
const __vilan_chunks = globalThis.__vilan_chunks;
const $X  = __vilan_chunks.fn.$X;
const $ai = __vilan_chunks.fn.$ai;
const panel = __vilan_chunks.fn.panel;
const view  = __vilan_chunks.fn.view;
function docs_page(page, $aK, $aL) { … }
function docs_nav(page, $aM, $aN) { … }
__vilan_chunks.fn.docs_nav = docs_nav;
__vilan_chunks.fn.docs_page = docs_page;
```

And on the eager side, every chunked function the eager scope NAMES gets a
**forwarder** so the call sites are emitted with no knowledge of the split
at all:

```js
function docs_page(page, $aK, $aL) {
	return __vilan_chunks.fn.docs_page(page, $aK, $aL);
}
```

The rename is taken once over the whole program and the chunk declarations
are lifted out afterwards (`transformer.rs`'s `transform_split`), which is
why both sides agree on names by construction and a chunk's function bodies
are byte-identical to a single-file build's.

### 1.3 The gate: fetch-then-run, upstream of a sync render

`View.swap`'s render callback is `sync` (`ui.vl`), so it cannot await a
chunk. The wait therefore sits **upstream of the swap**: `std::ui` gains
`View.swap_split`, which holds a gated `SignalCell<T>` the underlying `swap`
watches, and the emitter retargets a recognized `swap` call onto it,
rebinding the type argument by position. The gate's own body, as emitted:

```js
$bk(source, (value) => {
	const mine = generation.v + 1; generation.v = mine;
	clear_chunk_error($aT);
	const arm = __chunk_arm(value);
	if (__chunk_ready(arm)) { set_chunk_pending(false, $aT); advance(value); }
	else {
		set_chunk_pending(true, $aT);
		__chunk_load(arm, () => …advance(value)…, (reason) => …chunk_error…);
	}
});
```

Three facts about that shape matter downstream. **What renders during a
fetch is the previous route's view** — the signal simply has not advanced.
**The continuation opens its own turn** (`turn(FlushPolicy::AtSuspension,
..)`; the arrival lands outside every turn, so the navigation's DOM work
settles as one wave, exactly as an event handler's would —
`reactive-turns.md` §2). And **the boot preload is planted by the emitter**
immediately before the statement that mounts the swap, because `swap_split`
is the last call in its view chain and would otherwise not ask for the boot
chunk until the whole shell had been built.

### 1.4 Failure, retry, and generation

- A failed fetch reports to the console, leaves the route where it was, and
  publishes the reason on `std::router::chunk_error(): Signal<Option<str>>`
  beside `pending(): Signal<bool>`.
- **The retry mechanism is that there is none to write.** A failed attempt
  is not remembered as in flight (`delete chunks.pending[arm]` on the
  rejection path), so the next navigation to that arm refetches.
- **Latest wins by generation**: each value taken from the source claims the
  next generation and a continuation applies only if it is still the latest
  — `Draft::push`'s guard, same shape.
- `pending`/`chunk_error` publish only on a real change, so an ordinary
  navigation over loaded code notifies nothing.

### 1.5 The manifest

`dist/<leg>.chunks.json` is written on **every** build of a browser leg,
chunks or none (`fullstack-dx.md` §10.3, ratified 2026-08-11): `leg`,
`entry`, `styles`, `classic_script`, `chunks[]`, `assets[]`.
`std::build::build_of(leg)` reads it into a `LegBuild` and
`ServerBuilder::serve_build` installs one route per artifact, so nothing in
a server names a route or a chunk. A leg's chunk namespace belongs to its
LAST build: every write of the leg sweeps `<leg>.<arm>.js`.

### 1.6 The three constructional facts M18 breaks

The route partition guarantees, by construction, three things the shipped
runtime quietly depends on. **User-declared boundaries void all three.**

1. **A chunk is addressed by the route value's variant tag.** That is all a
   gated `SignalCell<T>` carries at the gate — which is why a second
   splittable match declines the whole split today (two route enums would
   alias each other's tags). An attribute-declared boundary has no variant
   tag at all. It needs a **key of its own** (§2.1).

2. **No chunk ever references another chunk's private function.** Anything
   two arms reach is eager, so a chunk's non-std dependencies are always
   eager. That is what makes the chunk preamble's *snapshot* —
   `const panel = __vilan_chunks.fn.panel;` at evaluation time — safe.
   Probe P3 shows it is not safe once boundaries can nest: a chunk evaluated
   before the chunk it depends on binds `undefined` **permanently**, and
   still throws after the dependency registers. This is §4.1, and it is the
   one thing in this paper that outright breaks.

3. **Nothing calls a chunked function except through the gate.** The
   forwarder is a safety net, not a path: "a call that somehow beat its
   chunk throws at the forwarder rather than returning `undefined`". Probe
   P2 confirms the throw is a bare `TypeError: … is not a function`. Under
   M18 the forwarder stops being a net and becomes **the boundary itself** —
   every call to a `[split]` function goes through it — so its behaviour
   before arrival is no longer an error case; it is the semantics (§3).

One smaller fact, found in P2 and worth recording because it constrains
§4.4: **`chunks.loaded[arm]` is written by `__chunk_load`, never by the
chunk.** A chunk that is evaluated by some other route — a bare `import()`,
an HMR re-evaluation, a `<script>` a server inlined — registers its
functions but leaves `__chunk_ready` reading false. The registry's
bookkeeping is owned by the loader alone.

## 2. The attribute

### 2.1 Spelling

Three candidates, and the choice follows from §1.6's fact 1.

- **`[split]`** — one word, mirrors the manifest's `split = true`, and says
  what it does. Its defect is that it says *whether*, not *which*: every
  `[split]` function would need its own chunk, because there is nothing in
  the annotation to group two of them by.
- **`[boundary]`** — the same, with a vaguer word. Rejected: `split` is
  already this tree's word for this operation (the manifest key, the CLI
  flag, `transform_split`, `--print-chunks`), and a second word for one
  concept is a tax on every reader.
- **`[chunk("icons")]` — named chunks.** The name IS the key §1.6 fact 1
  says the mechanism needs, and it is the only candidate that lets two
  functions share a fetch. It also makes the emitted artifact predictable
  (`dist/<leg>.chunk.icons.js`) instead of derived from a mangled function
  name, and it gives the shared-code question (§4.2) a place to be
  *answered by the author* rather than inferred.

**Recommended: `[chunk("<name>")]`, with `[split]` as sugar for
`[chunk("<function name>")]`.** The named form is the primitive; the bare
form is what a one-function boundary writes, and it desugars, so there is
one mechanism. A chunk name is an identifier-shaped string, checked like a
leg name, so `<leg>.chunk.<name>.js` cannot collide (`chunks.rs`'s
`chunk_file_name` reasoning: a leg name holds no `.`).

**Where it sits in the attribute chain.** Function attributes are an
ORDERED prefix, a faithful parser quirk with a pin of its own: `[deprecated]
[extern] [must_use] [rpc] [trait_only] [doc(hidden)] [platform]`
(`parsing.rs`'s `parse_function`; out-of-order declines, pinned by
`function_attributes_out_of_order_decline`). `[chunk(..)]` goes **after
`[platform(..)]`**, immediately before `async?/external?`, for one reason:
`[platform]` is a *fence* and `[chunk]` is a *placement*, and the fence must
be readable without knowing the placement. Adding a marker is a three-place
change held by a test: `KNOWN_ATTRIBUTE_MARKERS` in `parsing.rs`, the
VS Code grammar, and the docs theme's grammar, with
`crates/vilan-cli/tests/grammar_sync.rs` as the gate.

### 2.2 What it may decorate

**Functions only, in v1.** Precisely:

- **A free function** — yes. The exhibit.
- **A method in an `impl`** — yes, mechanically (a method is a `Node::Func`
  reached through `parse_impl`), but see §7 Q3: a method's receiver is a
  value that must exist before the fetch, which is fine, but a *trait*
  method's boundary would have to be per-impl, and dispatch through a bound
  would have to consult the registry per instance. Recommend: allowed on an
  inherent `impl` method, refused on a `trait` declaration, deferred on a
  trait `impl`.
- **A module** — no, and this is a real refusal rather than a scoping
  decision. `bundle-splitting.md` §1's load-bearing simplification is that
  **module-level bindings never split**: B33's initialization order is a
  global correctness invariant (non-hoisted `const` in topological load-time
  order) and partitioning it across asynchronously-evaluated files
  reintroduces exactly the TDZ class B33 killed. A `[chunk]` on a module
  would have to move that module's bindings, so it is refused for the same
  reason and with the same words. What an author actually wants when they
  reach for a module annotation — "put this generated 636 KB file behind a
  fetch" — is served exactly by one `[chunk]` on the module's one public
  entry point, because reachability does the rest (§5).
- **An `impl` block, a struct, an enum** — no. `[service]` and `[derive]`
  wrap items and generate code; `[chunk]` places *emitted function bodies*
  and has nothing to say about a type. A struct's methods each take the
  attribute themselves if they want it.

### 2.3 What crosses it — the invariant

This is the part of the design that is *free*, and it is worth saying why
loudly, because it is what makes M18 much cheaper than it looks.

> **Only CODE moves across a bundle boundary. Values do not.**

A chunk is a JavaScript module evaluated in the same realm, on the same
heap, that assigns functions into a plain object. An argument passed across
a boundary is passed by the ordinary calling convention to an ordinary
function; a return value comes back the same way. There is **no wire, no
codec, no serialization step, and therefore no serializability
constraint** — unlike `[rpc]`, whose arguments must be `wire`-shaped
because they genuinely travel. A `[chunk]` function may take and return
closures, `Shared` cells, signals, `View`s, DOM `Element`s, anything at all.

Three consequences follow, and the third is the sharp one:

1. **The type checker needs no new rule for the argument and return types.**
   Whatever a plain call admits, a boundary call admits.
2. **The context-threading pass needs no new rule either.** Hidden
   parameters (`owner_scope`, `turn_scope`) are ordinary arguments after
   threading, and the golden shows them crossing already: `docs_page(page,
   $aK, $aL)` in the eager forwarder and `docs_page(page, $aK, $aL)` in the
   chunk are the same signature.
3. **The ONLY thing the boundary changes is WHEN the call may run.** So the
   entire design question is the one the owner named the crux: what the
   call site's *type* becomes when the callee may not be there yet. Nothing
   else about the boundary is interesting. §3 is the whole proposal.

One corollary worth pinning as a rule rather than discovering later: **a
`[chunk]` function's own module-level bindings stay eager**, by §2.2's B33
argument. A `[chunk]` function that reads a module `const` reads it through
the registry exactly as `docs_page` reads `LABEL` today.

## 3. The call-site type — the crux

A call across the boundary must await a fetch. Three doors.

### 3.1 Door (a) — the attribute makes the function async

Honest, and the shortest thing to specify: `[chunk("icons")] fun
lucide_icon(name: str): View` is inferred `async`, the fetch is a suspension
point in its prologue, and asyncness propagates callee → caller exactly as
`async_infer.rs` already propagates it.

**It is not merely infectious. For a View-returning function it is a
compile error at the first call site.** `View.swap`, `View.when` and
`View.bind_each` all declare their render parameters `sync`:

```
fun when<S: Source<bool>>(self, condition: S, body: (sync || View) context owner_scope): View
fun swap<T: PartialEq, S: Source<T>>(self, source: S, render: (sync |T| View) context owner_scope): View
```

`async-polymorphism.md` §A.2 is explicit that a `sync` parameter opts out of
adaptation and that passing an async closure there is a refusal, not a
widening. So door (a) does not make view code awkward; it makes view code
**not compile**, at every reactive mount in the language, and the fix at
each site is to restructure the view — which is the thing M18 exists to
avoid. The infection also reaches `main` through every intermediate view
helper, and `main` is where the "views are sync" contract is anchored.

Door (a) is correct and usable for **non-View** returns in already-async
code, which is exactly door (c) (§3.3). As a general answer it is refused.

### 3.2 Door (b) — suspense-shaped, developed

The proposal: a boundary function that returns `View` keeps its `View`
return type and its `sync` colour. What it returns immediately is a
**placeholder**, and the placeholder fills reactively when the chunk lands.

#### 3.2.1 What the placeholder is — not a `Source<View>`

The tracker item sketches "a `Source<View>` that starts empty". Probing the
shipped `std::ui` surface says the better answer is one level lower and
already built. There is no `Suspense` node in `std::ui`, no `fallback`, no
`bind_view` — and none is needed, because `View.when` **is** the primitive:

```
/// Conditional CONTENT — the state-dropping boundary: while `condition` is
/// true the body's view is mounted under a fresh owner; when it turns false
/// the owner is disposed and the content removed.
fun when<S: Source<bool>>(self, condition: S, body: (sync || View) context owner_scope): View
```

So the lowering of a door-(b) boundary call is a source-to-source rewrite
the emitter can perform with no new std surface and no new node type:

```vilan
// what the author writes
[chunk("icons")] fun lucide_icon(name: str): View { … }
…
row.child(lucide_icon("search"))

// what the boundary lowers the CALL to (schematically)
row.child({
	let ready: SignalCell<bool> = SignalCell::new(chunk_ready(ICONS));
	let failed: SignalCell<Option<str>> = SignalCell::new(None);
	if !ready.get() {
		chunk_load(ICONS,
			|| turn(FlushPolicy::AtSuspension, || ready.set(true)),
			|reason: str| turn(FlushPolicy::AtSuspension, || failed.set(Some(reason))));
	}
	view("vilan-boundary")
		.when(ready, || lucide_icon("search"))       // the real call, deferred
		.when(failed.map(is_some), || boundary_error())
})
```

**Probe P8 ran exactly this shape, in vilan, on shipped primitives**, with
an `async { sleep(1); … }` spawn standing in for `chunk_load`'s
continuation. First paint and the fill:

```
first paint:      <main><h1>shell</h1><span></span></main>
after the fill:   <main><h1>shell</h1><span><i>icon:search</i></span></main>
```

The signature stayed sync, the shell painted without waiting, and the
subtree arrived under `when`'s own owner. Door (b)'s user-visible semantics
are not speculative; they run today.

Four properties of that lowering are load bearing:

- **The payload is a THUNK, not a value.** `when`'s body is
  `(sync || View)`, so the real call is named *inside* a closure. This is
  not a stylistic choice — it is what makes reachability tractable. If the
  boundary returned a `Source<View>` that the caller filled, the caller
  would have to *name* the chunked function to produce the value, and the
  chunked function's body would be reachable from an eager root. A thunk
  keeps the naming inside the deferred region, which is precisely the shape
  `chunks.rs`'s arm-attributed hold-out already knows how to walk.
- **The placeholder is an EMPTY element, not a spinner.** `when` mounts
  nothing while false, so the boundary costs one wrapper element and no
  content — P8's `<span></span>`. A spinner is an application decision, and
  it composes as a third `when` on the negation (or, better, off a
  `pending()`-shaped signal, §3.2.3).
- **The wrapper element is unavoidable and must be admitted.** `when` is a
  method on a `View`, so the boundary needs *some* element to hang the
  conditional child from. A `View` cannot be conjured from nothing and then
  replaced in place without a parent. So a door-(b) boundary call inserts
  one extra element into the DOM. Naming it (`<vilan-boundary>`, an unknown
  element, `display: contents` by default) makes it visible in the inspector
  and CSS-neutral; hiding it would be a lie. This is a real cost and §7 Q1
  puts it to the owner.
- **`View` is not a borrow.** The memory model's "no view across `await`"
  rule is about *loans* (`view-invalidation.md` §3: "a view across `await`
  *is a view stored in a struct*"), not about `std::ui::View`, which is an
  ordinary struct value. Nothing in the rule touches this lowering. The
  collision is one of vocabulary, and it is worth a sentence in the docs if
  this ships.

#### 3.2.2 Errors and retries

`when(failed.map(is_some), || …)` is the surface, and the retry story is
inherited from §1.4 without change: a failed fetch is not remembered as in
flight, so anything that re-runs the boundary call refetches. The
difference from the route gate is that a route has a natural retry event
(navigate again) and a boundary does not — a view that failed to fill just
sits there.

**Recommended: a boundary publishes its own state, and the two shipped
signals generalize.** `std::router::pending()`/`chunk_error()` are already
re-exports of `std::ui::chunk_pending`/`chunk_failure`, which are
module-level `SignalCell`s in `ui.vl`. The honest generalization is
per-chunk rather than global:

```vilan
fun chunk_state(name: str): Signal<ChunkState>   // Ready | Fetching | Failed(str)
fun chunk_retry(name: str)                        // clears Failed, re-enters the fetch
```

with `router::pending()` re-expressed as "any route chunk is fetching" so no
existing app changes. §7 Q4 asks whether the owner wants the per-chunk
surface at all or is content with a console report plus a silent empty
placeholder, which is the v1 route behaviour.

#### 3.2.3 SSR — the boundary must inline server-side

The server renders synchronously and there is no fetch server-side. Three
facts make this cheap rather than a second design:

1. **The process `std::ui` twin has no `swap_split` and never will.**
   `std_twin_parity.rs` compares the two twins' declared surfaces with a
   reasoned allowlist, and `View.swap_split` is already one of the
   deliberate divergences: emitter-selected, never written by a user, and a
   process build never splits, so its absence **degrades the chunk gate away
   instead of breaking a build**. `View.when` exists in both twins, so a
   door-(b) lowering degrades the same way — but only if the lowering is
   emitter-side and platform-aware.
2. **So the rule is: a `[chunk]` attribute is a no-op on a non-browser
   target, and on a browser leg without `split = true`.** The call lowers
   to a plain call, the function is emitted eagerly, and the attribute
   contributes nothing — exactly as `chunks::plan` returns an empty plan and
   the emitter changes no call today, which is what makes the flag's absence
   byte-identical.
3. **Hydration is where this gets interesting and where it should stop.**
   The server inlines the icon; the client boots, mounts a placeholder, and
   fetches. For a non-hydrating SSR setup (this tree's `examples/fullstack`
   shape — server markup, then a client that mounts its own tree) the
   sequence is server-icon → client-empty → client-icon, which is a visible
   flash. The genuine fix is `<link rel="modulepreload">` in the served
   HTML, which the compiler does not write **but a server now has
   `chunks.json` to write from** — `bundle-splitting.md` §S3 already names
   this as "the real first-paint fix and […] a page's decision, not a
   compiler's". A boundary chunk that is preloaded lands in the same tick as
   the bundle and the flash disappears. §7 Q5 records this as the one SSR
   question worth ruling on, and recommends: **v1 does not hydrate, does not
   suppress the flash, and documents the preload line.**

#### 3.2.4 The turn model

The arrival lands outside every turn, so it must open one, and the shipped
gate already shows the exact spelling: `turn(FlushPolicy::AtSuspension, ||
…)`. Three consequences, all of them already paid for by the route gate:

- **One turn per arrival, not per fill.** If three boundary calls share a
  chunk, the single `__chunk_load` continuation flips one `ready` signal
  and the three `when`s settle in one wave — the dedup on enqueue is the
  glitch-freeness (`reactive-batching.md`), and it applies per turn
  (`reactive-turns.md` §1).
- **`AtSuspension` is right, not `AtEnd`.** The continuation is UI work, and
  §2's table gives `AtSuspension` to every `std::ui` boundary.
- **Drain affinity covers the rest.** A `set` with no ambient turn joins the
  currently draining one, so a fill that cascades into derived signals
  coalesces inside the arrival's own settle.

There is one genuinely new interaction, and it is benign: **a boundary call
evaluated *during* a drain starts its fetch inside that drain.** The fetch
is not a suspension of the drain (it is a fire-and-forget `import()` whose
continuation opens a fresh turn), so the drain settles as it would have. The
budget-bounded flush is untouched.

#### 3.2.5 Non-`View` returns

Door (b) has nothing to offer them, and pretending otherwise is where this
design would go wrong.

- **A `Future<T>` / `Task<T>` reading** *is* door (a) with a different
  spelling: the caller must await, so the caller becomes async, so the
  infection is identical. It buys only that the infection is visible in the
  return type — which this language deliberately does not do (asyncness is
  inferred and never written in return types, `execution.md` §7.3). Refused
  as a second colour system.
- **A `Source<T>` reading** — "the call returns a signal that starts empty
  and fills" — is coherent for `T` a plain value and is genuinely useful
  (`Signal<Option<Config>>` filling when a config chunk lands). But it
  changes the return type, so it is not the no-type-change property that
  makes door (b) worth having; it is a *different feature* wearing the same
  attribute. **Refused for v1**, recorded as the natural v2 (§7 D7).
- **`void` returns** are fine and need no ceremony: a `[chunk]` function
  returning `void` lowers to `chunk_load(name, || f(args), report)` — a
  fire-and-forget, which is the correct reading of "call this when you can".
  This is worth having in v1 because it costs nothing.

**So door (b)'s scope is exactly: `View` returns get the placeholder, `void`
returns get fire-and-forget, everything else is a compile error naming door
(c).** That refusal is the design's honesty: a diagnostic that says *"a
`[chunk]` function returning `Option<View>` cannot be called from sync code;
mark a `View`-returning wrapper instead, or call it from an async
position"* is a better artefact than a second return-type protocol.

### 3.3 Door (c) — restrict to already-async positions

The router's trick, generalized: `[chunk]` is legal only where a suspension
already is — an event handler body, a route body, an `async` function, a
`nursery` task. The call is then an ordinary inferred-async call with an
`import()` in front of it, and **nothing in the type system changes at
all**.

Its cost is stated plainly: it does not cover the exhibit. `lucide_icon` is
called from a view chain, not a handler. Door (c) would make the owner's own
motivating case illegal.

But it is not a losing door — it is the **complement** of door (b), and it
is free. Door (b) covers `View` and `void`; door (c) covers every other
return type in the positions where awaiting is already legal. They share one
attribute, one runtime, one manifest, and one diagnostic.

### 3.4 Recommendation

**Door (b) for `View` (placeholder that fills reactively through
`View.when`) and `void` (fire-and-forget), door (c) for every other return
type, and a diagnostic at the seam between them. Door (a) is refused.**

The costs of the others, stated:

- **Door (a)** costs a compile error at every reactive mount in the language
  (`sync` render parameters refuse async bodies, `async-polymorphism.md`
  §A.2), and an asyncness infection reaching `main`. It is not a worse
  ergonomic; it is a non-starter for the case that motivated the feature.
- **Door (c) alone** costs the exhibit. It is otherwise the cheapest thing
  in this paper and ships as half of the recommendation.
- **Door (b) alone** costs a refusal on non-`View` returns — which is the
  diagnostic above, and which door (c) then answers.

What door (b) costs *on its own terms*, and these should be weighed: one
extra DOM element per boundary call site (§3.2.1); a first paint that shows
an empty hole rather than the content, with no compiler-provided spinner; an
SSR flash unless the page writes a preload link (§3.2.3); and a lowering
that is emitter-side and platform-conditional, which is a new kind of
emitter rewrite even though `swap_split`'s retarget is a close precedent.

## 4. The extremes

### 4.1 Nested boundaries — THIS BREAKS

A `[chunk("a")]` function that calls a `[chunk("b")]` function. Under door
(b) both call sites lower to `when`-gated thunks, so the *semantics* are
fine: the outer placeholder fills with a view that itself contains an inner
placeholder that fills. Two round trips, sequential, visible — correct and
unsurprising.

**The emitted runtime does not survive it.** A chunk snapshots its
dependencies at evaluation time:

```js
const panel = __vilan_chunks.fn.panel;   // by VALUE, at module evaluation
```

Probe P3 built a second-level chunk in exactly that shape and evaluated it
before its dependency's chunk. The binding took `undefined`, and it **stayed
`undefined` after the dependency registered**: the call still threw
`TypeError: docs_nav is not a function`. A `const` initialized from a
missing property is not a live view of that property.

This never fires today because §1.6's fact 2 holds by construction. Under
M18 it fires whenever two chunks reference each other's functions, which
nested boundaries do by definition, and which §4.2's shared-chunk option
does too.

Two fixes, and the second is right:

- **Order the fetches.** Emit a dependency edge per chunk and have
  `__chunk_load` fetch a chunk's dependencies first. This preserves the
  snapshot (and its zero per-call cost) but serializes round trips that
  could have been parallel, and needs a dependency graph in the chunk map.
- **Stop snapshotting cross-chunk names.** Emit a cross-chunk call as a
  property read at the call site — `__vilan_chunks.fn.docs_nav(page, …)` —
  exactly as the eager forwarder already does. The cost is one property
  lookup per cross-chunk call, on a megamorphic-ish object; the benefit is
  that arrival order stops mattering entirely and the mechanism needs no
  graph. The forwarder proves the shape is already emittable.

**Recommended: stop snapshotting, keep the snapshot only for names the
partition proves eager.** The eager registrations happen in the entry's own
module evaluation, strictly before any chunk can be fetched, so a snapshot
of an eager name is sound and stays free. Only chunk→chunk references pay
the property read. That is a precise, measurable change to
`transform_split`, and it is the single largest piece of implementation work
M18 implies.

### 4.2 Shared code between chunks

Two boundaries reaching one helper. The route partition's answer is "shared
goes eager", which it calls monotone, correct, and a loss of optimization
only. **At boundary granularity that answer is catastrophic, and the
measurement is unambiguous.**

Probe P7 is probe P4's program with a second route arm that also calls
`lucide::lookup`. The plan flips completely:

| | eager functions | chunk `Icons` | eager bundle | verdict |
| --- | --- | --- | --- | --- |
| one boundary (P4) | 4 (0 shared) | 1819 fns, 1,023,521 B | **18,079 B** | saves 935,242 |
| two boundaries (P7) | 1822 (**1818 shared**) | 1 fn, 504 B | **958,680 B** | adds 4,704 |

Every byte of the icon table is reachable from two arms, so all of it goes
eager and the first load returns to its unsplit weight — the chunks are
reduced to the two four-line page functions. The rule that costs nothing
when the shared set is one `panel` helper costs 940 KB when the shared set
*is the thing you were trying to defer*, and at boundary granularity two
call sites over one table is the ordinary case, not the exotic one.

So M18 must extract shared chunks, and there are exactly two shapes:

- **Dedup into a common chunk.** The set reachable from ≥ 2 boundaries and
  from nothing eager becomes its own chunk, fetched by whichever boundary
  gets there first. This is strictly better on bytes and strictly worse on
  round trips (a boundary now waits on two fetches). It also *requires*
  §4.1's fix, because the common chunk and the boundary chunks reference
  each other.
- **Duplicate into both.** No new fetch, no ordering problem, and the shared
  bytes are paid twice — but paid *lazily*, which is the whole point. For
  the lucide shape (1791 icons over one 8-line `lucide_frame`) duplication
  is obviously right; for two boundaries sharing a large parser it is
  obviously wrong.

**The named-chunk spelling (§2.1) dissolves the choice.** `[chunk("icons")]`
on both functions puts them in the *same* chunk, so there is nothing to
share; two different names is an explicit statement that the author wants
two fetches. So v1 needs a rule only for what the author did not decide:
**code reachable from two differently-named chunks and nothing eager is
DUPLICATED into both, and the build reports the duplicated bytes.** It is
the monotone-and-correct choice at this granularity (no ordering, no extra
round trip), it degrades gracefully (the report tells you to merge the
names), and it inverts route splitting's default for a stated reason rather
than by accident.

**M16's instrument is directly reusable here** and is the reason
duplication is affordable. M16 (closed 2026-09-01) decides T-independence by
comparing the EMITTED body, name-stripped through `rename_node` — never text
substitution, because a literal containing another instance's name would
fake a match — and merges only when the walk pushed no keyed emission of its
own. Its 37 merged bodies took the split fixture down 9.38% (105 → 88
functions). The same emitted-body comparison, run across chunk boundaries
rather than across monomorphized instances, is exactly the measurement
"would duplicating this cost anything?" needs: two chunks that would each
carry a byte-identical body are the dedup candidates, and the rest is
genuinely distinct code. **Recommendation: duplicate by default, and use
M16's comparator to report the duplicated mass per build.**

### 4.3 The reachability pruner at a boundary

This is the extreme M18 needs to hold most, because the whole exhibit is a
pruning story, and **it holds**. Probe P4's `--print-chunks`:

```
chunk `Route::Icons(..)`: 1819 functions, ~584841 bytes
  (a_arrow_down, …, lucide_frame, lookup, lucide_lookup_a, …, zoom_out)
eager: 4 entry functions (0 shared by 2+ arms)
```

Three properties, each confirmed rather than assumed:

- **The pruner descends through the boundary, not around it.** `lookup`
  names 25 sub-lookups which name 1791 icons which name `lucide_frame`; all
  1819 landed in the chunk, none eager.
- **Std stays eager by residence**, so the chunk reads `view`, `text`,
  `$Z`, `$af`, `__substring` out of the registry rather than carrying
  copies. The chunk's preamble in P4 is five lines.
- **A function reachable only through the boundary is not reachable
  eagerly**, which is what makes the eager count fall to 4. Probe P5 is the
  control: replacing the by-name lookup with a direct per-icon spelling
  prunes 1790 icons away entirely, at 13,162 B whole. The pruner was never
  the problem; the string dispatch was, and a boundary is what lets a string
  dispatch exist without being on the critical path.

The one thing to watch: `chunks.rs` computes reachability over the
**node-level** call graph, and its byte figure is a *source-span estimate*
(`~584841`), not the emitted size (1,023,521). Any `--print-boundaries`
report must keep that distinction as visible as `--print-chunks` does.

### 4.4 A boundary inside a const or generated module

Two different questions that look like one.

**Generated modules: no interaction at all, and this is the exhibit.**
`src/lucide/lib.vl` is 635,947 bytes written by a `[[build.hook]]` whose
freshness is a content stamp over declared `inputs`/`outputs`, recorded in
`dist/.build-hooks.json`. The hook produces `.vl` source; the compiler then
sees ordinary functions with ordinary spans (E100 gave generated modules
real spans). A `[chunk]` in generated source is a `[chunk]` like any other,
and the generator emits it as text. The only new obligation is on the
generator's author: the attribute must be *generated*, which means the
generator must know the chunk name — one string. §5 shows the shape.

**`const`: a hard refusal, and it is the same refusal as §2.2's.**
`const-eval.md`'s world evaluates at compile time; a boundary is a runtime
fetch. A `[chunk]` function called from a `const` initializer would have to
either run at compile time (in which case the code is in the eager bundle
anyway, as a folded value — no boundary) or defer (in which case a module
binding's initialization is asynchronous, which is precisely the TDZ class
B33 killed). **Refuse `[chunk]` on any function reachable from a
module-level binding's initializer, with a diagnostic naming the chain**,
which is the shape `platform_color.rs` already uses for fence violations
("the error names the chain"). This is checkable with machinery that exists:
the eager root already includes `program.module_level_bindings()`.

### 4.5 HMR

`vilan run` ignores `split` in every form — plain `run`, `run --watch`, and
`run --watch --no-hmr` — and says so once
(`note_split_ignored`, `main.rs`; the doctrine is `bundle-splitting.md`
§10). The reasoning was that HMR classifies by whole-bundle byte diff and
swaps a whole Blob URL with a per-leg version counter, so per-chunk swapping
needs per-chunk versions, a classifier per file, and a re-registration
story — and the mode being optimized was a net loss at every scale in the
tree.

**`[chunk]` must inherit that decision unchanged, and it inherits it more
comfortably than route splitting did.** A dev build compiles every `[chunk]`
function eagerly, `chunk_ready` reads true for every name (which is already
the behaviour in any build with no chunk map — "`swap_split` is `swap` one
derived signal deeper"), and door (b)'s lowering degrades to `when(always
true, thunk)`, i.e. a plain mount behind one wrapper element. The
development experience is a program with no fetches in it.

One consequence must be written down rather than discovered: **the wrapper
element (§3.2.1) must exist in dev too.** If the dev lowering elided it, a
CSS selector that worked in development would break in production. So the
degradation is "the fetch goes away", never "the boundary goes away".

The re-fetch question — "what happens to an already-fetched chunk when the
bundle hot-swaps?" — is therefore moot in v1 by the same doctrine. Recorded
for the day it is not: HMR's swap disposes the root owner, clears the
container, and re-evaluates a fresh Blob; a stale `globalThis.__vilan_chunks`
would survive that, holding functions from the *previous* build against a
new eager scope that renamed everything. **The registry would have to be
version-keyed** (the per-leg version counter is already minted and already
substituted into the shim as `__VILAN_HMR_VERSION__`), and P2's find applies:
`loaded` is written by the loader, so a re-evaluated chunk does not
re-announce itself. That is at least a slice of work, and it is not v1's.

### 4.6 The build record: manifest and stamp

The manifest needs one new array and no new file. Today's `chunks[]` entries
are `{ arm, tag, file }` — route-shaped. Boundaries are not arms and have no
tag, so they need their own list rather than a widened one:

```json
{
  "leg": "client",
  "entry": "client.js",
  "styles": null,
  "classic_script": true,
  "chunks":     [ { "arm": "Route::Home", "tag": 0, "file": "client.Route_Home.js" } ],
  "boundaries": [ { "name": "icons", "file": "client.chunk.icons.js", "functions": 1819, "bytes": 1023521 } ],
  "assets": []
}
```

Three properties fall out for free, each because the manifest already works
this way:

- **`serve_build` needs no change.** It installs one route per artifact, and
  `LegBuild` grows one field. A server that never named a route still never
  names one.
- **The namespace sweep already covers it.** A leg's chunk namespace belongs
  to its last build, discriminated by the `<leg>.` prefix plus a non-empty
  segment — `<leg>.chunk.<name>.js` is inside that namespace by
  construction, so removing a `[chunk]` attribute removes its file, and a
  renamed chunk does not leave a stray.
- **`build_of` keeps its one real distinction**: a leg never built is a
  named error; a leg with no boundaries is `"boundaries": []`, a positive
  statement.

The `[[build.hook]]` **stamp is a different mechanism and must not be
confused with this one** (they meet only in the exhibit): the stamp is a
content digest over a hook's command, declared inputs and declared outputs,
kept in `dist/.build-hooks.json`, and it decides whether a *generator* runs.
It has no opinion about chunks. The one interaction worth recording is
benign and good: because the stamp is content-based, adding a `[chunk]`
attribute to a generator's output template changes the generator, restales
the hook, and regenerates — which is what you want.

### 4.7 `[service]` / `[rpc]` across a boundary

The most interesting composition in the paper, and it works — for a reason
worth stating precisely.

`[service(TodoClient)]` decorates a **struct**; `[rpc]` decorates a method.
The macro generates two halves from one declaration: on the server a
`dispatcher()` that wires each method body as a route closure, and on the
client a stub struct whose per-method bodies are `call(self.transport,
self.codec, "name", [...])` and nothing else, plus a `contract_hash()` both
sides verify. **Platform coloring** (`platform_color.rs`) is what keeps the
server half out of the browser: `dispatcher()` creates the closures
containing user bodies, so it is `@process`-coloured; the stub creates none,
so the browser build compiles the same module, generates the same stub and
hash from the signatures, and *never reaches the body*.

That gives three clean answers:

- **`[chunk]` on an `[rpc]` method is meaningless and should be refused.**
  The method's body is server-side; the browser never emits it; there is
  nothing to defer. The diagnostic writes itself, and it is the same
  reachability argument platform coloring already makes.
- **`[chunk]` on a client-side function that *uses* a service is
  fine, and is a good idea.** The generated stub is small, but everything
  built on top of it — a whole admin panel's worth of calls, decoders and
  views — is ordinary app code and defers like any other. The stub itself
  is reached from the eager side too (the transport is dialed at boot), so
  it stays eager by the ordinary rule.
- **A boundary cannot straddle the client/server line, and the existing
  fence already says so.** Platform coloring is checked over reachable code
  from each entry; a `[chunk]` changes *when* code runs, never *where*. Two
  separate mechanisms, no interaction, and the fence's error still names the
  chain.

One residue, filed rather than solved: `contract_hash()` is computed from
the surface string and verified at connect. If a client's service usage sits
behind a boundary, the *verification* still happens at connect (eagerly),
because the transport is eager — so a contract drift is still caught before
any deferred code runs. That is the desirable ordering and it happens by
accident; if the transport ever becomes lazy, the check must not follow it.

## 5. The lucide exhibit, worked end to end

The exhibit under the recommended door, with the numbers it gives.

### 5.1 The generated module's shape

`scripts/lucide.mjs` writes `src/lucide/lib.vl` — 1791 `fun`s over a shared
`lucide_frame()`, plus a two-level dispatch (`lookup` → 25
`lucide_lookup_<letter>` → the icon). It gains **one line**: the attribute
on the one entry point the app calls, and a `View`-returning wrapper for it,
because door (b) does not cover `Option<View>` (§3.2.5):

```vilan
/// The by-name entry point. `[chunk]` puts the whole table — the dispatch,
/// the 1791 icons and the frame they share — behind one fetch.
[chunk("icons")]
fun icon(name: str): View {
	match lookup(name) {
		Option::Some(let built) => built,
		Option::None => view("span").class("lucide-missing"),
	}
}
```

That fence compiles as written today, minus the attribute (probe P9).
`lookup` and the 25 sub-lookups keep their signatures and need no
attribute — reachability carries them (§4.3, probe P4: 1819 functions
followed the one entry point into the chunk). The generator's change is a
string; the `[[build.hook]]`'s content stamp restales on it and regenerates.

kolt's four call sites go back to what 038 wanted before the bundle forced
the owner's hand — kolt's own `icon(..)` wrapper around the new by-name
entry point, rather than around a per-icon spelling:

```vilan
{icon(lucide::icon("search")).styled(text_icon_style)}
```

and the per-icon spellings remain available and unchanged for anything that
does not need a runtime name.

### 5.2 The numbers

Measured on `0.40.0 (f30897ee0)` against a program that puts the real
1791-icon dispatch behind the *shipped* structural boundary — the closest
honest proxy for `[chunk("icons")]`, since it exercises the same partition,
the same registry and the same fetch (probes P4–P6):

| shape | first load | fetched on first icon |
| --- | --- | --- |
| by-name dispatch, no boundary | **953,321 B** | — |
| by-name dispatch behind a boundary | **18,079 B** | 1,023,521 B |
| per-icon spellings (038's shipped choice) | **13,162 B** | — |

Read the middle row against the other two and the case is made:

- **The boundary takes 935,242 B off the first load** — 98.1% of the
  program — and the app still has by-name icons.
- **Against per-icon spellings, by-name-behind-a-boundary costs +4,917 B on
  first load** instead of +940,159 B. That is a **191× reduction in the
  price of the ergonomics**, on the same measurement axis 038 used to price
  them at 645× (038's ratio is against kolt's own eager baseline; the shapes
  differ, the conclusion does not).
- **Of that +4,917 B, only ~648 B is the dispatch's own eager residue** —
  the forwarder plus its registry lines. The other **4,269 B is the route
  gate's fixed cost**, measured in isolation by building the per-icon
  program both ways (probe P6: 17,431 split vs 13,162 whole). **A `[chunk]`
  boundary does not need the route gate**: no gated signal, no
  `swap_split` retarget, no boot preload, no generation guard, no arm
  keying. Door (b)'s lowering needs `chunk_load`, `chunk_ready`, the
  registry and one `when` per call site — a strict subset. So the honest
  expectation for the attribute is *lower* fixed cost than 4,269 B, and §7
  D9 makes measuring it a gate rather than a hope.

For the record, the constant moved since it was last written down.
`bundle-splitting.md` §9 measured the fixture at +4,957 B added / 1,019 B
deferred and put the fixed cost at 5.4–6.1 KB. Today the same fixture
measures **+4,561 B added / 1,024 B deferred** (probe P1) and the two
lucide-shell programs put the gate at **4,269 B** — consistent with M16's
emitted-body dedup, which closed the same day this note was written and took
the split fixture down 9.38%. §9 was right to record the constant as a
measurement of a moment.

### 5.3 First paint versus first icon

The sequence under door (b), on a cold load:

1. **First paint** pays 18,079 B — the shell, the router, the reactive
   runtime, `std::ui`, and one forwarder. The icon's slot is a
   `<vilan-boundary>` element containing nothing.
2. **The fetch** starts when the boundary call is *evaluated*, which is when
   the view chain is built — i.e. during the mount, not after it. There is
   no route to preload from and no `chunk_preload` plant to make: the call
   site itself is the earliest knowable point, which is a strict improvement
   on the route gate's problem (`bundle-splitting.md` §S3 had to plant a
   preload because `swap_split` was the *last* call in its chain).
3. **First icon** costs one round trip and 1,023,521 B — which is the honest
   cost of a by-name table and is exactly what the boundary exists to keep
   off step 1. An app that mounts icons above the fold should preload
   (`<link rel="modulepreload">` written by the server from
   `chunks.json`, §3.2.3); an app whose icons are in a menu should not.
4. **Every later icon** is free: the chunk is evaluated once,
   `chunk_ready("icons")` is true, and door (b)'s lowering mounts the real
   subtree with no `when` transition at all (the signal is seeded true at
   construction — the `if !ready.get()` in §3.2.1's lowering).

The one thing this exhibit does *not* show, and it should be said: **1 MB
behind one boundary is a lot to fetch at once.** The named-chunk spelling
gives the escape (`[chunk("icons-common")]` on the frame and the twenty
icons an app actually uses, `[chunk("icons-rest")]` on the dispatch), but
whether an author should ever be doing that by hand is §7 Q6.

## 6. Probe ledger

Toolchain: `vilan 0.40.0 (f30897ee0)`, built once as a debug binary in a
detached read-only worktree of the compiler repo at `f30897ee`. Nothing was
committed there. All probe programs are scratch files outside both
repositories; none is proposed for the tree.

| # | what was run | what it showed |
| --- | --- | --- |
| **P1** | `crates/vilan-cli/tests/split/project` rebuilt with `--print-chunks` | All five goldens byte-identical. Plan: 1 site, 3 chunks, 7 eager functions (1 shared). Verdict **+4,561 B added / 1,024 B deferred** (19,476 split vs 14,915 whole) — against `bundle-splitting.md` §9's +4,957 / 1,019. §5.2. |
| **P2** | node + the fixture's DOM stub: call `__vilan_chunks.fn.docs_page` before its chunk lands, then `import()` the chunk and re-inspect | Before: slot `undefined`, the forwarder's call throws `TypeError: … is not a function`. After a bare `import()`: the slot is a function, registered names are `$X, $ai, LABEL, docs_nav, docs_page, panel, view` — but **`chunks.loaded` is still `{}`**, so `__chunk_ready` reads false. The loader owns the bookkeeping; a chunk never announces itself. §1.6. |
| **P3** | a hand-built second-level chunk in the emitter's exact shape (`const docs_nav = __vilan_chunks.fn.docs_nav;`), evaluated **before** its dependency's chunk | The `const` binds `undefined` and **stays** `undefined` after the dependency registers: `TypeError: docs_nav is not a function`. The snapshot is by value at evaluation time. **§4.1 — the break.** |
| **P4** | a router program whose one arm calls kolt's real `lucide::lookup` (1791 icons, `lib.vl` copied read-only), built with `split = true --print-chunks` | Chunk `Route::Icons(..)`: **1819 functions, ~584,841 source bytes**; 4 eager functions, 0 shared. Artifacts: `client.js` **18,079**, `client.Route_Icons.js` **1,023,521**, Home 299, NotFound 252, manifest 341. Verdict: **saves 935,242 B on first load, defers 1,024,072** (18,079 vs 953,321 whole). The pruner descends through the boundary; std stays eager by residence (5-line chunk preamble). §4.3, §5.2. |
| **P5** | the same program with the arm calling `lucide::search()` directly, whole | **13,162 B**. The per-icon control: 1790 icons pruned away. §5.2. |
| **P6** | P5's program built `split = true` | **17,431 split vs 13,162 whole → +4,269 B added, 1,554 B deferred.** Isolates the route gate's fixed cost on the same shell, which is what lets §5.2 attribute ~648 B of P4's +4,917 to the dispatch itself. |
| **P7** | P4's program with a **second** arm also calling `lucide::lookup` | Plan: **1,822 eager functions, 1,818 of them shared by 2+ arms**; the `Icons` chunk collapses to 1 function / 504 B. Eager bundle **958,680 B** (from 18,079), verdict flips from *saves 935,242* to *adds 4,704*. "Shared goes eager" sends the whole table to the first load. **§4.2.** |
| **P8** | a vilan program implementing door (b)'s lowering on **shipped primitives only** — sync `fun … : View`, `SignalCell<bool>`, `View.when`, an `async { sleep(1); turn(AtSuspension, …) }` spawn standing in for `chunk_load`'s continuation — run under the fixture's DOM stub | First paint `<main><h1>shell</h1><span></span></main>`; after the arrival `<main><h1>shell</h1><span><i>icon:search</i></span></main>`. Sync signature, shell painted without waiting, subtree mounted under `when`'s own owner inside a turn. **§3.2.1 — door (b)'s semantics are not speculative.** |
| **P9** | §5.1's exhibit fence, minus the attribute, compiled | Builds clean — the qualified `Option::Some(let built)` pattern over an `Option<View>` returned by a generated-module lookup is written as the paper shows it. |

Read, not run, and load bearing: `chunks.rs` in full; the fixture's five
goldens; `ui.vl`'s `swap`/`swap_split`/`when`/`bind_each` and the
`chunk_*` externs; `parsing.rs`'s ordered function-attribute prefix and
`KNOWN_ATTRIBUTE_MARKERS`; `platform_color.rs`'s module contract;
`analyzer.rs`'s `service_impl_source`; `hmr.rs`'s `classify` and
`main.rs`'s `note_split_ignored`; `std/src/process/build.vl`'s `LegBuild`.

**Not probed, and therefore not claimed.** No implementation of the
attribute was attempted; every statement about what the *attribute* would
emit is reasoning from the machinery, not measurement of it. The P4–P7
figures are for the shipped ROUTE boundary standing in for a declared one,
which is exactly right for the reachability and byte questions (same
partition, same registry, same fetch) and is an *over*-estimate on fixed
cost (§5.2). §7 D9 turns that estimate into a gate.

## 7. Determinations, and what the owner must rule

### Determinations

- **D1. The idea holds.** A function attribute is the right instrument for a
  weight boundary, it composes with everything in the tree, and the runtime
  it needs is 90% built. §0, §1.
- **D2. Only code crosses a boundary.** No serialization constraint, no new
  type rule, no new context rule. The entire design question is the call
  site's timing. §2.3.
- **D3. Door (b) for `View`, door (c) for the rest.** Door (a) is refused
  because `sync` render parameters *refuse* async bodies — it does not make
  view code awkward, it makes it not compile. §3.1, §3.4.
- **D4. `View.when` is the placeholder; no new std node is needed.** Proven
  running in P8. The payload must be a thunk, not a value, or reachability
  cannot defer it. §3.2.1.
- **D5. Nested boundaries do not hold as built.** The chunk preamble
  snapshots dependencies by value at evaluation time (P3). Fix: emit
  chunk→chunk references as call-site property reads, exactly as the eager
  forwarder already does; keep the snapshot for eager names only. This is
  the largest piece of implementation work M18 implies. §4.1.
- **D6. "Shared goes eager" must be inverted at boundary granularity.**
  P7: it returns 940 KB to the first load. Duplicate by default; use M16's
  name-stripped emitted-body comparator to report the duplicated mass. §4.2.
- **D7. `[chunk]` is refused on modules, on `const`-reachable functions, on
  `[rpc]` methods, and on non-`View`/non-`void` returns in sync positions.**
  Each refusal has an existing rule behind it (B33's initialization order,
  `const-eval`'s compile-time world, platform coloring, door (c)). §2.2,
  §3.2.5, §4.4, §4.7.
- **D8. `[chunk]` inherits `split`'s posture wholesale**: a `vilan build`
  decision, ignored by every `run` form, degrading to a plain call on a
  non-browser target and on a leg that did not ask to split — the property
  that makes the flag's absence byte-identical. §3.2.3, §4.5.
- **D9. Ship it measure-first or not at all.** `SplitCost` already emits a
  leg both ways and warns when the split costs more than it defers.
  `[chunk]` must ride the same instrument — a `--print-boundaries` report
  and a per-boundary verdict line — before any of §3's lowering is written.
  That is also the answer to "the Solid mistake with extra steps": a
  forgotten boundary is reported, and a boundary that does not pay says so.
  §0, §4.3.

### Questions

- **Q1. The wrapper element.** Door (b) inserts one `<vilan-boundary>`
  element per boundary *call site* (§3.2.1) — `display: contents`, but real,
  and present in dev too so selectors do not drift (§4.5). Acceptable, or is
  a DOM-neutral fill (marker nodes and manual insertion, i.e. a new
  `std::ui` primitive rather than `when`) worth the machinery?
- **Q2. `[chunk("icons")]` versus `[split]`.** The named form is
  recommended because the name is the key the runtime needs and the lever
  the shared-code question wants (§2.1, §4.2). Does the owner want the bare
  `[split]` sugar at all, or is one spelling better than two?
- **Q3. Methods.** Allowed on an inherent `impl` method, refused on a
  `trait` declaration, deferred on a trait `impl` (§2.2). Is the deferral
  right, or should trait impls be refused outright in v1 so there is no
  half-answer?
- **Q4. The per-boundary state surface.** `chunk_state(name)` /
  `chunk_retry(name)`, with `router::pending()` re-expressed over it (§3.2.2)
  — or v1 ships the route behaviour (console report, empty placeholder, no
  retry event) and adds the surface when something needs it?
- **Q5. SSR.** Recommendation: v1 does not hydrate, does not suppress the
  server-icon → empty → client-icon flash, and documents the
  `<link rel="modulepreload">` line a server can write from `chunks.json`
  (§3.2.3). Is an unsuppressed flash acceptable for v1?
- **Q6. Chunk granularity as an authoring task.** 1 MB behind one boundary
  is a lot to fetch at once (§5.3). The named form lets an author split it
  by hand. Should the toolchain instead *report* a boundary above some
  measured mass, the way it reports a split that does not pay — and is that
  a v1 obligation or a later one?
- **Q7. The order of work.** This paper's recommendation implies four
  slices: (1) `--print-boundaries`, analysis-only, on the existing partition
  machinery (D9); (2) the registry change that makes chunk→chunk references
  safe (D5) — independently valuable, since it is the thing that would let
  route splitting ever extract shared chunks; (3) the attribute, the
  emission and the duplication rule (D6); (4) door (b)'s lowering plus door
  (c)'s admission and the diagnostic between them. Slice 2 is a change to
  shipped, byte-pinned emission with no user-visible feature attached to it.
  Does the owner want it taken as its own item, ahead of the attribute?

## Correction to §4.1 / D5 (lane m20, 2026-09-01)

The shipped emitter never reached P3's `TypeError` shape: its preamble
is filtered by `eager_names.contains(name)`, so a SIBLING chunk's name
got no binding whatsoever and the call site dangled with a
`ReferenceError` — the same root (no live cross-chunk reference form),
one step worse than §4.1 recorded. M20 shipped the call-site registry
read for sibling names (eager names stay snapshotted, sound by
construction); the wrong-order pin now resolves where the shipped
emitter threw `ReferenceError` and the snapshot form threw
`TypeError`. Zero cross-chunk references on today's route partition —
inert on every plan v1 can make. M20 removes the ORDERING hazard only:
a call before the provider is fetched still throws, loudly and now
recoverably; arranging the fetch is the attribute's (M18's).
