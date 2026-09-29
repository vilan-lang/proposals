# Reactive layers — sources and move-only pipes, tracked reads as sugar, collections per shape (A142)

> Status: **RATIFIED DESIGN, unbuilt** (2026-09-29, revision 2). The owner ruled
> R1–R16 in conversation before the first revision was written, and Q1–Q12 on
> reading it (R17–R28). The same day the owner asked whether transformations
> should be `Source`s at all. A prototype on 0.41.1 (Appendix A) answered no, and
> the owner adopted the **move-only pipe** model (R29). That supersedes R16–R19
> and dissolves the cold-node problem the first revision spent §4.2 on. Each
> ruling is quoted where it governs and collected in §10. The pipe model raised
> Q15–Q20, ruled as recommended the same day (R30–R35), and Q13–Q14 followed
> (R36–R37). §11 keeps the questions; none remains open.
>
> Origin: the owner's second `kolt/src/lib/reactive2.vl` sketch (2026-09-29).
> This file name was reused: A124's paper answered an earlier sketch at the same
> path. The design began with a question: is the per-struct "signal colouring"
> heft a principle of reactivity, or a side effect of the model vilan has today?
> §1 answers it; the rest is the model the sketch and the rulings settled on.
>
> Probed on `vilan 0.41.1 (07e8db372)`: the language gaps the sketch runs into
> are filed as B458–B462, and the prototype found B463 (§9). The paper builds no
> std code; the std surface it cites is `next @07e8db37`.

## 0. Summary

Three layers, each built only from the one below it:

1. **The base.** Two kinds of reactive value:
   - A **`Source`** has state and can be read: a root cell, a sealed memo, a
     constant, a remote mirror, a transient.
   - A **`Pipe`** is a transformation: a *description* with no `get()`. It is
     move-only (a `[resource]`) and is consumed exactly once, by sealing it
     (`.memo()`, `.cell()`, `.transient()`, `.sample()`) or by a consumer (an
     effect, a UI binding).

   Because every pipe has exactly one consumer, every body in it runs once per
   change of its input, so every body can own things, start tasks and track
   reads (§3, §4). `TransientSource` covers values that come and go (§5).
2. **Collections, per shape.** A sequence, a map and a set each have one change
   vocabulary (`SeqOp`/`MapOp`/`SetOp`, A112) and one set of operators written
   against it. An operator follows whatever reactive value its closure returns,
   so flattening is not a combinator (§6).
3. **Sugar.** Tracked reads: `.track()` inside any body a pipe runs (§7). Later,
   `Store`, which generates the fine-grained version of a type automatically
   (§8).

## 1. Is the heft a principle? (the question the sketch answers)

**The part that is unavoidable.** A read can be invalidated only as precisely as
the write that changed it was described. For fine-grained updates, every write
must say *what* changed and every read must say *what it looked at*. Somebody has
to produce both:

- the runtime, by intercepting every access (MobX, Vue);
- the programmer, one reactive twin per type (vilan before this paper);
- the compiler, from the type's shape (a `Store`, §8).

**Algebraic data** (structs, tuples, `Option`, `Result`) carries its change
structure in its definition. Its fields and variants are the places that can
change, so the fine-grained version can be generated. **Abstract data**
(`List`, `Map`, `Set`) hides it: a list's buffer does not say "three elements
arrived at position 4". Its change vocabulary must be declared, once per
*shape*, which is what `delta.vl` already does ("an op vocabulary per collection
SHAPE (not per method)").

**The part that came from the model.** Two costs multiplied:

- *The data side*: reactivity lived on values, so every container wanted a
  reactive twin.
- *The dependency side*: every shape a source can hide inside wanted its own
  join. `flatten`, `FlattenOption` and `AndThen` exist today, and
  `reactive.vl`'s own comment records that a third, composite `flatten`
  "cannot be added beside these two".

Neither cost is a principle. §6 removes the dependency side for collections: an
operator follows whatever reactive value its closure returns. §7 removes it for
arbitrary code: tracked reads. §8 removes the data side for algebraic types.
What remains is irreducible, and it grows with *shapes and operators*, never
with *user types*. It is:

- one change vocabulary per abstract shape;
- keys for sequence identity (`each_by`);
- hand-written stateful derivatives for non-linear operators (sort, group,
  top-k);
- the encapsulation boundary: a type's private fields are opaque unless its
  author opts in;
- equality, for cutting propagation short.

## 2. The layering rule

> **R6 (RULED).** Tracked reads are an optional layer stacked on the base.
> `.track()` registers a source with the nearest tracking scope through the
> context API. `derive` and `effect` open a tracking scope for their bodies. The
> method `derive` is not sugar over the free `derive`; the free `derive` is sugar
> over the base.

> **R12 (RULED).** `Store` (fine-grained versions of types, generated
> automatically) is a sugar layer, not a fundamental.

A higher layer may only use what a lower layer exposes: `Subscriber`,
`on_settle`, the turn, owners, `DeltaLog`. The base never knows the tracking
layer exists. The one exception is that its callbacks *clear* the tracking
context (§7.3), and clearing is a no-op when the layer is absent.

## 3. The base: sources and pipes

> **R29 (RULED, 2026-09-29, superseding R16–R19).** Transformations are not
> `Source`s. `derive`, `switch` and the other combinators return a **pipe**: a
> move-only description with no `get()`. A pipe is consumed exactly once, by a
> sealing operation that turns it into a `Source`, or by a consumer. `.memo()`
> and `.cell()` exist only on pipes, so `SignalCell::cell()` no longer exists.

### 3.1 The four traits

| Trait | What it is | Examples |
|---|---|---|
| `Source<T>` | Has state; `get()` reads it. Ordinary data: copying one copies a handle. | `SignalCell`, a sealed memo, `Source::constant(v)`, a remote mirror, a `TransientSource` |
| `Signal<T>` | A writable `Source`: `set`, `notify`, `set_with`. | `SignalCell`, a `.cell()` |
| `Flow<T>` | Anything a pipeline can start from. It carries the combinators and the consuming operations, and every one of them takes `own self`. A blanket impl covers every `Source`; for those, `own self` is a copy. | every `Source`, every pipe |
| `Pipe<T>` | `with Flow<T>`: a transformation. The node types are `[resource]` and carry the sealing operations. | `derive`, `switch`, `distinct` and the other nodes |

The names `Flow` and `Pipe` are R30.

**A pipe is its own instance.** It can be started only once, so a stateful
stage keeps its instance state in its own node: `switch` its current inner and
generation, `distinct` its last key. A124's nodes carry over nearly unchanged.
They stop implementing `Source`, become `[resource]`, and are consumed rather
than read. `on_settle` forwarding stays as it is: a sealed five-stage chain puts
one subscriber on its root and evaluates the stages fused, once per change.

**The values a flow carries are data.** A pipe cannot travel *through* a flow,
because the values are copied into every consumer. Flattening therefore applies
to flows of `Source`s, and a selector builds a fresh inner pipe on each call
(§3.2).

### 3.2 The surface

| Surface | What it is | Ruling |
|---|---|---|
| `Flow.derive(f)` | Today's `Source.map`, renamed so it does not collide with a collection's (or a type's) `map`. Returns a pipe. | **R1** |
| `Flow.switch(f)` | A dynamic dependency: `f` selects an inner flow per outer value. It must **build** that flow; a closure cannot capture a prebuilt pipe. | — |
| `Flow<Option<T>>.switch_some(f)` | `f: \|T\| I` with `I: Flow<U>`, giving a pipe of `Option<U>`. `None` detaches. | **R8** |
| `Flow<bool>.then_some(s)` | `s: Source<T>`, giving a pipe of `Option<T>` that follows `s` while true and detaches while false. It takes a `Source` because it restarts the inner flow each time the flag turns true, and a pipe can start only once. | — |
| `Flow<Option<S: Source<U>>>.flatten()` | `switch_some(\|x\| x)`. | — |
| `Flow<Option<T>>.and_then(f)` | Kept for the Kleisli form, `f: \|T\| Flow<Option<U>>`. | — |
| `Source::constant(v)` | A `Source`: `get()` is `v`, subscriptions are no-ops. It fits a static value into a reactive position. | **R3** |
| `.distinct()` / `.distinct_by(f)` | Notify only when the value (or `f(value)`) changed. The value passed downstream is the whole `T`. | **R7** |
| `Flow.effect(f)` | Consumes the flow; every run of `f` gets its own owner (§4). Today's `sub`, `on_change` and `effect_on_change` move to `Flow` the same way. | **R2** |
| `Pipe.memo()` / `Pipe.cell()` / `_global` twins | Seal into a read-only `Source` or a writable `Signal` (§3.3). | **R11**, **R20** |
| `Pipe.sample()` | A one-off read: start, take the value, release (§3.3). | **R32** |
| `Pipe<Task<..>>.transient()` | Seal a flow of tasks into a `TransientSource` (§5). | **R37** |

> **R7 (RULED).** Equality is opt-in. `SignalCell::set` never compares.
> `.distinct()` and `.distinct_by(f)` are selectors that propagate a
> notification only when the value, or `f`'s result, changed.

### 3.3 Sealing (R11, R20, R29)

Each sealing operation takes `own self`, so a pipe is sealed at most once.

- **`.memo()`** gives a read-only `Source` backed by one `SignalCell`. Nothing
  downstream can `set` a derivation. `TransientSource::state()` (§5) is one of
  these (R28).
- **`.cell()`** gives the writable cell. A local `set` holds until the next
  upstream change overwrites it. That is a legitimate pattern (a local override
  of a derived value), and the documentation says so.
- **`.memo_global()` / `.cell_global()`**: A130's lifetime, one of each face.
- **`.sample()`** (R32) starts the pipe, returns its current value and releases
  it, including anything its bodies created. It replaces the one thing A124's
  cold nodes gave that pipes do not: reading a derivation without subscribing
  (§4.3). Its cost is written at the call: `on_click(|| submit(total_of(cart).sample()))`
  runs the chain once per click, visibly.

**Sharing is sealing.** Two consumers of one derived value need a `Source`
between them:

```
let total = cart.derive(|c| c.sum()).memo();   // one instance, one run per change
text(total);                                    // a Source is data: pass it anywhere
badge(total.derive(|t| t > 100));               // each consumer builds its own pipe
```

Handing the same *pipe* to two consumers is a compile error (§3.4). The
diagnostic for `.get()` on a pipe steers to `.memo()` or `.sample()`. Today's
message suggests importing `Source` instead, so this is part of S1.

### 3.4 Why move-only (the evidence, Appendix A)

The prototype shows two separate effects:

- **Removing `get()` from transformations** gives the owner's second point:
  `cell.memo()` is refused ("`Cell<i32>` has no method 'memo'"). It also makes
  every *single* instance coherent: a body runs only inside the consumer that
  started it, once per change.
- **It does not stop duplication.** Two `.memo()`s on one *copyable* pipe both
  compile, and the body runs twice per change (`runs=4` where one instance runs
  it twice).

**Making pipes `[resource]` with `own self` consumers turns that into a compile
error**: "use of `p` after it was moved: a resource has a single owner". This
also covers branching (`let q = p.derive(..); p.memo();`). Roots stay data: a
`SignalCell` passed twice to a function taking `own x: Flow<i32>` is simply
copied.

The language enforces two more things, both correct:

- A closure cannot capture a prebuilt pipe ("a closure cannot capture the
  resource"). Selectors build their inner flows.
- A struct holding a pipe becomes a resource by containment (§6.8 of the spec).
  A model layer therefore stores sealed `Source`s, or exposes methods that
  *build* pipes (§4.3).

**B463 must hold for this to be sound.** A trait default method whose receiver
is the loan `self` can move `self` into an aggregate when `Self` is a resource.
The prototype hit this with `derive(self)`: branching went undetected and the
resource was copied. A concrete impl refuses the same body. Until B463 is fixed,
every combinator and every sealing operation is written `own self`, which the
prototype confirms closes the gap.

## 4. Owners: every body runs in exactly one instance

> **R2 (RULED).** `.effect` always wraps its body in an owner, which is released
> when the body re-runs.
>
> **R14 (RULED).** `derive` gets a per-run owner too. "Any body where a signal
> change causes computation should be per-run owner wrapped."

Under R29 this holds for **every** body a pipe runs: `derive`, a `switch`
selector, `effect`, a collection operator's per-element closure (§6.4), and the
free `derive` (§7). A pipe runs only inside the one instance that consumed it,
and inside that instance each stage runs once per change of its input. So "a
run" always means "one run per change", and a per-run owner is always coherent.
This merges today's `effect`/`scoped_effect` pair (A114) into one form.

### 4.1 Allocating the owner lazily (accepted)

Most leaf effects register nothing, so a run's owner is created on the body's
**first registration** (the first `take`, `on_cleanup`, nested `effect`, seal or
lease). A run that registers nothing costs one null check.

**Tasks are owned.** A task started during a run belongs to that run's nursery
and is cancelled when the run is released. So `src.derive(|x| async ..)` cancels
the superseded fetch when `src` changes, which is half of §5's latest-task-wins
rule for free.

### 4.2 What this replaced (history)

Revision 1 asked what a **cold** `derive` does with a per-run owner. A124's cold
node ran its body when it was *read*, not when its input *changed*. With N
readers per change, a per-run owner released one reader's resources on the next
reader's pull. The options were:

- (A) promote to a cache automatically;
- (B) key each run to the upstream version;
- (C) refuse and steer to a cached `derive_memo`.

(C) was ruled (R17–R19). R29 dissolves the problem instead: a pipe has no
readers, only its one consumer. `derive_memo` never ships. The cold-body
refusal and the rule that a cold derive opens no tracking scope go with it.

### 4.3 What the pipe model costs

1. **A derivation cannot be read without subscribing.** Every shared or
   imperatively read derived value is sealed, at the cost of a cell and a
   subscription. A124's cold nodes gave free, unsubscribed pull reads (its
   measured 0.23–0.41× cases). `.sample()` is the explicit replacement for a
   one-off read. A rough scan of kolt found no sites that read a derivation
   chain directly with `.get()`, and 31 `.cell()` sites, which are already
   sealed. The scan is a regex and can miss values stored and read later.
2. **Storing a pipe makes the holder move-only.** Model layers store sealed
   `Source`s, or offer methods that build pipes on request. Naming a returned
   pipe type needs `dyn` today (`fun open_channel(self): dyn Pipe<Channel>`), or
   a written node type. That makes **B460** (a bare trait in return position)
   more valuable than revision 1 assumed: it is the pipe model's
   `impl Iterator`.
3. **Selectors build and `then_some` takes a `Source`**, because a pipe starts
   once (§3.2).
4. **The B463 dependency** (§3.4).

Against those costs: the owner problem is gone in every form, `derive_memo` is
gone, `.cell()` on a cell is gone, and double instantiation is a compile error
instead of silent duplicate work.

## 5. Transient sources

> **R4 (RULED).** The sketch's `TaskState` folds into `TransientState`.
> **R13 (RULED).** `Failed` is generic in its error and carries the stale value.
> `Gone` is spelled `Absent`, today's `rpc.vl` `Status::Absent`. **R5 (RULED).**
> A `TransientSource<T>` is a `Source<Option<T>>`. `Refreshing` does NOT read as
> `Some`; `.latest()` opts in to the stale value.

```
export enum TransientState<T, E> {
	Pending,                 // nothing yet
	Ready(T),
	Refreshing(T),           // a newer value is on its way; T is the last one
	Failed(E, Option<T>),    // failed; the last value, if there was one
	Absent,                  // "there is no such source", as of now (a later ask may find one)
}

export trait TransientSource<T, E> with Source<Option<T>> {
	// `get()`: Ready(v) is Some(v); every other state is None.
	fun state(self): dyn Source<TransientState<T, E>>;   // sealed, read-only (R28)

	/// A fresh pipe per call. Opts in to the stale value: Ready(v), Refreshing(v)
	/// and Failed(_, Some(v)) are Some(v).
	fun latest(self): dyn Pipe<Option<T>>;               // a bare trait return waits on B460

	/// A fresh pipe per call: Pending or Refreshing.
	fun is_pending(self): dyn Pipe<bool>;
}
```

- **A task is a transient that never leaves its answer.** A single `Task<T>`
  goes Pending, then Ready or Failed(e, None), and stops. That is
  `TaskSource<T, E>` (R24).
- **A flow of tasks is a transient that refreshes.**
  `src.derive(|x| async ..).transient()` (R37) goes from `Ready(v)`
  to `Refreshing(v)` when a new task starts. **The latest task wins:** the
  superseded task is cancelled with its run (§4.1), and a reply that arrives
  anyway is dropped, so it never overwrites a newer one. A plain `derive`
  suffices here, because the body runs once per change inside the one instance.
- **Remote mirrors map onto it.** `rpc.vl`'s `Status` maps as
  `Waiting`→`Pending`, `Ready`→`Ready`, `Absent`→`Absent`, and
  `Failed(RpcError)`→`Failed(RpcError, stale)`. A mirror already "keeps whatever
  it last held", which is exactly the stale value `Failed` now carries. A
  `RemoteSource` implements `TransientSource<T, RpcError>`.
- **`Absent` stays** because it is what lets a UI tell a spinner (`Pending`) from
  "not found". Both read `None` through `get()`.

A binding over `get()` goes blank during every refresh. A UI that should keep
showing the old value while it refreshes binds `latest()` (R27).

## 6. Collections, per shape

The shapes and their change vocabularies are A112's: `SeqOp` (splice, set-at,
move, reset), `MapOp`, `SetOp`. The derivative law is unchanged:
`f(a ⊕ da) == f(a) ⊕ f'(a, da)`. A collection *type* joins by declaring its
shape. std writes this once per type; a user collection that wraps a std one
inherits it. Operators are written once per shape.

The faces follow §3:

- `CollSource<T>` reads (R23);
- `CollSignal<T>` is the write trait (R23);
- `ListCell<T>` is the concrete cell (R23);
- a collection operator returns a move-only **collection pipe** (named
  `CollPipe<T>`, R33). It is sealed with `.memo()` into a
  `CollSource`, or consumed by `each`/`each_by`.

### 6.1 Operators follow the reactive value their closure returns

> **R9 (RULED, the owner on rough edge (a)).** Collection operators do not open
> a tracking scope per element. A closure may *return a reactive value*, and the
> operator follows it per element. Tracking stays sugar:
> `.filter_map(|src| derive(|| src.track()))`, with a shorthand to be added. A
> built-in scope could not be removed later; a scope built on top can always be
> added.

So the sketch's lines work as written. `gns.map(..)` is a pipe with two
consumers below, so it is sealed first (§3.3):

```
let gns = ListCell::of([1, 2, 3]);
let gns_data: CollSource<dyn TransientSource<str, RpcError>> = gns.map(|id| get_data_source(id)).memo();
let gns_is_loading: Source<bool> = gns_data.any(|src| src.is_pending()).memo();
let gns_loaded: CollSource<str> = gns_data.filter_map(|src| src).memo();
```

**A closure returning a plain value must not pay for this.** An operator's
closure result is bounded on a result trait with specificity tiers (B158, spec
§5.4), as `MaybeSignal` does:

```
export trait IntoFlow<T> { .. }                              // R31 (R22 named it IntoSource)
export impl type T with IntoFlow<T> { .. }                   // a plain value: a constant, no subscription
export impl type F: Flow<type T> with IntoFlow<T> { .. }     // a source or a pipe: started per element
```

The pipe case is new under R29. `is_pending()` returns a fresh pipe for each
element, and the operator starts it inside that element's instance.
`MaybeSignal` itself does not fit: its `bind` takes a callback rather than
returning a value. The compiler picks the implementation per closure when it
generates code, so `filter(|x| x > 3)` never subscribes and never allocates.

**Which operators flatten.** A returned reactive value is followed only where
the operator's output shape is fixed:

| Operator | Closure result | Flattens a returned flow? |
|---|---|---|
| `filter`, `any` (R21), `all`, `count` | `bool` | yes: only the `Flow` impl can produce a `bool` from a flow |
| `filter_map` | `Option<U>` | yes: `\|x\| x` over a flow of `Option<T>` binds `U = T` |
| `map` | `U` (free) | **never** for a returned `Source`: `gns.map(get_data_source)` is a collection *of* sources. A returned *pipe* is started per element and its value carried (R35), since a pipe cannot be an element. |
| `CollPipe<S: Source<U>>.flatten()` | — | the explicit flatten for a collection of `Source` elements (§3.1) |

Nothing here is ambiguous: a closure returning `Option<Source<X>>` to
`filter_map` binds `U = Source<X>` and does not flatten. One risk for the build:
choosing an implementation from a closure's return type while `U` is still
undetermined is B434's family, and `filter_map(|x| x)` will be the first thing
to meet it.

### 6.2 What following a flow costs

Each element whose closure returned a real flow holds one subscription through
it. A change there re-reads one element and emits one op:

- **`filter`/`filter_map`**: an element that flips between in and out becomes a
  `Splice` insert or remove at its *output* position. That position is the count
  of kept elements before it: a Fenwick tree over kept/dropped gives it in
  O(log n), and it is updated by the input's splices.
- **`any`/`all`/`count`**: a counter. It adds what arrived and subtracts what
  left, O(1) per change. The "what left" payload in `delta.vl` exists for this.
- **`map`**: a changed element is `SetAt(i, old, new)`.

An element's position moves under splices, so each element's runner keeps a
**stable slot id** and looks up its current index when it emits.

### 6.3 Boundary conversions: coarse into granular

> **R10 (RULED, rough edge (b)).** Accepted as below.

Turning a flow of `List<T>` into a granular collection can only ever be a diff:
the coarse source threw the change description away upstream (§1).

- **`.coll_by(key)`**: a keyed reconcile, reusing the `ReconcilePlan` that
  `each_by` already runs. O(n) per change with hashing, and it can emit `Move`.
- **`.coll()`**: a positional fallback, `T: PartialEq`. Trim the common prefix
  and suffix, then splice. O(n), and minimal for the common edits (append,
  insert one, remove one).
- Both return a collection pipe. A *writable* local copy seeded from a coarse
  source is `Draft`-shaped, a different thing.
- The real fix is upstream: keep the source of truth granular (`ListCell`,
  `KeyedCell`, A138), so a diff happens only at boundaries such as fetch
  results and wire snapshots.

The sketch's first rough edge, `Source<List<Source<Option<T>>>>` into a list of
`T`, is then two steps, each written once per shape: `.coll_by(key)` (or
`.coll()`), then `.filter_map(|x| x)`.

### 6.4 Per-element owners

An operator's closure runs once per element that arrives, and again per element
that changes. Each such run gets an owner, released when the element leaves or
re-runs. That is how `gns.map(get_data_source)` releases a mirror's lease when
its id is removed.

## 7. Tracked reads (sugar)

> **R6 (RULED)**, and the owner's acceptance of the three points below
> (2026-09-29).

### 7.1 The mechanism

Tracking is a context: `tracking: Context<TrackScope>`. `Source::track(self): T`
does `get()` and registers `self` with `tracking.get()`.

- It uses the **strict** `get`, not `get_safe`. A `track()` outside any scope is
  a compile error.
- Because vilan's contexts are threaded at compile time as hidden parameters,
  `track()` does no run-time lookup. Only `track()` consults the scope; `get()`
  never does.
- `track()` exists on `Source`, because it reads. Following a *pipe* inside a
  body means sealing it, or building the body as a flow.

### 7.2 Which forms open a scope

Every body a pipe runs opens one, because under R29 every such body runs inside
one instance that can remember its dependencies between runs:

- `derive` (so `count.derive(|c| c + other.track())` follows `other` too);
- a `switch` selector;
- `effect`;
- the free `derive(|| body)`, a pipe whose only dependencies are the ones it
  tracks.

A stage with tracked reads compares the new dependency list against the old one
after each run (reusing edges in order), subscribes to whatever is new, and
wakes in the turn's derivation phase (`as_derivation`). The push-pull turn keeps
it free of glitches.

Collection operators open no scope (R9). Tracking there is
`|x| derive(|| ..)` (§6.1).

### 7.3 Callbacks clear the scope

A closure created inside a `run` **captures** the context. So a callback minted
inside a tracking scope (an `on_change` observer, an event handler) and invoked
later would register with a scope that has already closed.

Rule: every base callback position (`on_change`, `effect_on_change`, UI event
handlers) runs its callback under `tracking.clear(..)`. `clear` is B458, and it
doubles as the user-facing `untrack`.

### 7.4 What this reverses

`reactive-batching.md` says "Vilan tracks explicitly", and its `untrack` row
reads N/A. A124's paper withdrew a tracked `computed` for three reasons:

1. **"An ambient frame consulted on every `get()`."** Here only `track()`
   consults it, and without any run-time lookup.
2. **"The untracked-callback footgun."** §7.3 closes it, statically.
3. **"A reversal of the explicit-tracking stance."** The base keeps that stance;
   tracking is an opt-in layer on top.

When S6 lands, both papers get a paragraph pointing here.

## 8. `Store` (sugar, later)

`Store::new(value)` would generate the fine-grained version of `T` from its
shape:

- one cell per scalar leaf;
- one lazily allocated slot per struct field;
- for an enum, a discriminant cell plus the live variant's payload;
- a collection's declared shape (§6).

Projections such as `app.channels.at(id).name` are cheap, copyable handles: a
root plus a path the compiler knows. They are `Source`s (and `Signal`s), not
pipes, because they have state to read. Writing a whole value diffs it against
the old one and wakes only the leaves that changed. Writing the same enum
variant patches its payload, so subscriptions into that payload survive.

The one constraint this puts on the base: `Signal` must allow a *lens*
implementation, where `set` on a projection writes back through the root.
Nothing in §3 blocks that. This gets its own paper when the base has shipped.

## 9. The language items

| Item | What | Used by |
|---|---|---|
| B458 | `Context::clear`: the context is not established inside `body` | §7.3, `untrack` |
| B459 | `then`/`else`: `EXP then EXP else EXP`; statements `EXP then STMT;`, `EXP else STMT;`, `EXP then STMT else STMT;` | the sketch throughout; **R15**: the guard's `is` bindings reach the rest of the block when the `else` exits |
| B460 | a bare trait in return position (reopens B253) | **more valuable under R29**: returning pipes from model methods (§4.3); §5's trait methods (`dyn` until then) |
| B461 | bare traits nested in annotations | `CollSource<TransientSource<str>>` and similar |
| B462 | enum variants as closures | `count.derive(Some)` |
| B463 | affine hole: a trait default with the loan `self` can move a resource `Self` | **the move-only guarantee** (§3.4); until fixed, combinators use `own self` |

None of them blocks the std work. Each has a working spelling today: `dyn`,
`|x| Some(x)`, `if` blocks, written generics, `own self`.

## 10. Rulings (2026-09-29)

| # | Ruling |
|---|---|
| R1 | `Source.map` is renamed `derive` (now on `Flow`). |
| R2 | `effect` wraps each run's body in an owner, released on re-run. The owner is allocated lazily (§4.1, accepted). |
| R3 | `Source::constant(v)` replaces `StaticSourceCell`. |
| R4 | `TaskState` folds into `TransientState`. |
| R5 | `TransientSource<T>` is a `Source<Option<T>>`. `Refreshing` reads `None`; `.latest()` opts in to the stale value. |
| R6 | Tracked reads are an optional layer: `track()` goes through the strict `Context::get`, and base callbacks clear the scope. |
| R7 | Equality is opt-in: `.distinct()` and `.distinct_by(f)` (not `.when`, which clashes with the `when` view form and `Style::when`). |
| R8 | `switch_some`, not `and_then_some`. |
| R9 | Collection operators follow a returned reactive value; per-element tracking stays sugar. |
| R10 | Boundary conversions as §6.3. |
| R11 | `.cell()` is split into a read-only and a writable name (§3.3). |
| R12 | `Store` is a sugar layer. |
| R13 | `Failed` carries a generic error and the stale value; `Gone` is spelled `Absent`. |
| R14 | Bodies that run because an input changed get a per-run owner. Under R29 that is every body a pipe runs. |
| R15 | B459's guard `EXP else STMT;`: the condition's `is` bindings extend to the rest of the block when the `else` exits. |
| ~~R16~~ | ~~Derived values are `Source`s.~~ **Superseded by R29**: a derivation is a pipe until it is sealed. A *sealed* derivation is a `Source`. |
| ~~R17~~ | ~~Q1 → (C): a cold derive body gets no owner and no tracking scope.~~ **Superseded by R29** (§4.2). |
| ~~R18~~ | ~~`derive_memo(f)`.~~ **Superseded by R29**: never ships. |
| ~~R19~~ | ~~A cold derive opens no tracking scope.~~ **Superseded by R29**: every body a pipe runs opens one (§7.2). |
| R20 | `.memo()` (read-only) and `.cell()` (writable), with `_global` twins; now only on pipes. |
| R21 | `any`, not `some`. |
| R22 | The collection operators' result trait is `IntoSource<T>`; renamed `IntoFlow<T>` by R31. |
| R23 | `CollSource<T>` (read), `CollSignal<T>` (write trait), `ListCell<T>` keeps its name. |
| R24 | The one-shot task is `TaskSource<T, E>`. |
| R25 | `TransientSource<T, E>` is generic in `E`. |
| R26 | `Source::constant` does not replace `MaybeSignal`'s static arm. |
| R27 | A binding takes whatever reactive value it is handed; the documentation shows `latest()` for lists that refresh. |
| R28 | Accessors such as `TransientSource::state()` hand back the read-only face. |
| R29 | Transformations are move-only pipes, not `Source`s; they are consumed once, by sealing or by a consumer (§3). |
| R30 | Q15 → the traits are `Flow<T>` (anything a pipeline starts from; combinators and consumers; blanket over `Source`) and `Pipe<T>` (a move-only transformation; the sealing operations). |
| R31 | Q16 → R22's `IntoSource<T>` is renamed `IntoFlow<T>`, with a pipe case. |
| R32 | Q17 → `Pipe.sample()` ships in S1. |
| R33 | Q18 → the collection pipe is `CollPipe<T>`. |
| R34 | Q19 → no `Flow.share()` in S1; a parameter read twice asks for a `Source`, and the caller seals. |
| R35 | Q20 → `map` starts a returned pipe per element and carries its value; it still never flattens a returned `Source`. |
| R36 | Q13 → over a flow of `Task<Result<T, E>>`, `.transient()` lifts `Err(e)` into `Failed(e, stale)`; over a flow of bare `Task<T>`, `E` is `str` (the panic's message). |
| R37 | Q14 → the sealing operation from a flow of tasks to a transient is `.transient()`. |

## 11. Questions

Q1–Q12 were ruled on 2026-09-29 as R17–R28. Q1–Q3 (the cold-node options,
`derive_memo`, and scopes in cold bodies) are superseded by R29 and are
recorded in §4.2. Q13–Q20 were ruled as recommended the same day (R30–R37).
No question remains open.

- **Q13 (RULED, R36).** The error type of a task transient. Tasks fail by panic, which is
  untyped. **Rec**: over a flow of `Task<Result<T, E>>`, `.transient()` lifts
  `Err(e)` into `Failed(e, stale)`; over a flow of bare `Task<T>`, `E` is `str`
  (the panic's message).
- **Q14 (RULED, R37).** The name of the sealing operation from a flow of tasks to a
  transient. **Rec `.transient()`.**
- **Q15 (RULED, R30).** Trait names. **Rec `Flow<T>`** (anything a pipeline starts from: the
  combinators and consumers, blanket over `Source`) and **`Pipe<T>`** (a
  move-only transformation: the sealing operations).
- **Q16 (RULED, R31).** Rename R22's `IntoSource<T>` to **`IntoFlow<T>`**, now that it has a
  pipe case. **Rec yes.**
- **Q17 (RULED, R32).** `Pipe.sample()`: a one-off read that starts, reads and releases.
  **Rec yes**, in S1: it is the only replacement for the unsubscribed pull read
  that cold nodes gave.
- **Q18 (RULED, R33).** The collection pipe's name. **Rec `CollPipe<T>`**, beside
  `CollSource`/`CollSignal`.
- **Q19 (RULED, R34).** A `Flow.share()` for generic code that takes `own x: Flow<T>` and
  needs to read it twice: the identity on a `Source`, `.memo()` on a pipe.
  **Rec not in S1.** A parameter that must be read twice asks for a `Source`,
  and the caller seals. Add it when generic code needs it.
- **Q20 (RULED, R35).** `map` whose closure returns a **pipe**. A pipe cannot be a value in a
  collection (§3.1), so the only thing it can mean is "start it per element and
  carry its value". **Rec**: `map` starts a returned pipe per element, while
  still never flattening a returned `Source` (a `Source` is data and can be the
  element). Without this, per-element tracking in `map` is spelled
  `gns.map(|x| derive(..).memo()).flatten()`: an extra cell per element.

## 12. Slices

| Slice | Content | Needs |
|---|---|---|
| S1 | The split: `Flow`/`Pipe` with `[resource]` nodes and `own self` throughout; `derive` (renamed `map`), `switch`, `switch_some`, `then_some`, `flatten`, `distinct_by`, `Source::constant`; sealing with `.memo()`/`.cell()`/`_global`/`.sample()`; consumers moved to `Flow`; the steering diagnostic for `.get()` on a pipe | B463 (or `own self` everywhere); breaking, kolt migrates |
| S2 | Per-run owners on every pipe stage, lazily allocated (merging `scoped_effect`); tasks owned by their run | S1 |
| S3 | `TransientState`, `TransientSource`, `TaskSource`, `.transient()` with latest-task-wins, `RemoteSource` implementing it, `latest()` | S2 |
| S4 | Collection pipes (`CollPipe`), `IntoFlow`, and flow-following `filter`/`filter_map`/`any`/`all`/`count`/`flatten`, `map` starting a returned pipe (R35), with per-element owners, stable slot ids and the Fenwick index | S2; B434's family |
| S5 | Boundary conversions: `.coll_by(key)`, `.coll()` | S4 |
| S6 | Tracked reads: the `tracking` context, `track()`, scopes in every pipe body, the free `derive`, callbacks clearing the scope | B458, S2 |
| S7 | The `Store` paper | S4, S6 |

The language items (B458–B463) run independently of these slices, except B463's
tie to S1.

## Appendix A. The prototype (0.41.1)

Written against 0.41.1 with its own toy root (`Cell`, whose `watch` takes a
wake-up closure), not std's `SignalCell`, so it isolates the type surface from
the turn machinery. `Up` and `Pipe` here are the paper's `Flow` and `Pipe`.

```vilan
trait Up<T> {
	fun start(own self, react: |T| void);        // instantiate: react now, then once per change

	fun derive<U>(own self, f: |T| U): Map<Self, T, U> {
		Map<Self, T, U> { up = self, f }
	}

	fun switch<I: Up<U>, U>(own self, select: |T| I): Switch<Self, T, I, U> {
		Switch<Self, T, I, U> { up = self, select }
	}
}

impl type S: Src<type T> with Up<T> { .. }      // every root is a flow; `own self` copies it

[resource]
struct Map<S, T, U> { up: S, f: |T| U }         // a description: no `get`

trait Pipe<T> with Up<T> {
	fun memo(own self): Cell<T> { .. }           // start once, feed a cell
}
impl Map<type S: Up<type T>, T, type U> with Pipe<U> {}

[resource]
struct Switch<S, T, I, U> { up: S, select: |T| I }   // its generation lives in its instance
```

| Case | Result |
|---|---|
| `c.derive(f).derive(g).memo()`; `c.set(5)`; three reads | fused, one run per change; reads run nothing (`m=11 11 11 runs=2`) |
| `c.memo()` on a root | refused: `Cell<i32> has no method 'memo'` |
| `c.derive(f).get()` | refused (the message steers to the wrong fix; S1) |
| two `.memo()`s on one copyable pipe | both compile; the body runs twice per change (`runs=4`) |
| the same, `[resource]` + `own self` | refused: "use of `p` after it was moved: a resource has a single owner" |
| `q = p.derive(..); p.memo()` with `derive(own self)` | refused at the second use |
| the same with `derive(self)` | **accepted and wrong** (`4 3`): B463 |
| a root passed twice to `own x: Up<i32>` | fine: roots are data |
| a counting `switch` selector, sealed, read three times | one run per outer change (`made=1`, then `2` after a flip) |
| a selector returning a captured prebuilt pipe | refused: "a closure cannot capture the resource" |
