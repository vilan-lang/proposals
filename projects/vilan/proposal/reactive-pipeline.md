# Reactive pipeline — every combinator is a cold node, `get()` pulls, a notification carries no value (A124)

> Status: **DRAFT** (awaiting owner review). R1–R5 were RULED by the owner on
> 2026-09-22 before this paper was written and are quoted at the section they
> govern; everything else ends in a recommendation, not a ratification. §9 is
> the open-questions set.
>
> Origin: tracker A124, filed 2026-09-21 as a read-tracked `computed` paper and
> REWRITTEN 2026-09-22 against the owner's `kolt/src/lib/reactive2.vl` sketch
> and the eight probes at `sweeps/order39/probes/a124_*.vl`. The first filing is
> withdrawn; §0 says why and what survives of it.
>
> **Everything below about what the language does today was run, not recalled.**
> The probe ledger (§1.3) was re-checked on `next @49de3915`, and the model
> itself was BUILT: `vilan/std/src/reactive_pipeline.vl` is the S1 probe — the
> cold-node pipeline over today's `Source`, with no compiler change — and every
> number in §6 and §7 comes off it under callgrind. Where the paper says "costs
> N Ir", N was measured on this tree.

## 0. The problem and the thesis

Today every combinator on `Source` returns a `SignalCell`. `map` allocates a
cell, seeds it by running the transform once, subscribes to its upstream and
hands the cell back (`vilan/std/src/reactive.vl`, `Source::map`); `combine`,
`flatten`, `selector` and — since A123, this order — `switch` and `and_then` do
the same. A derivation is therefore **state**: a five-deep chain is five cells,
five subscriptions and five stored values, recomputed eagerly on every write to
the root whether or not anything is looking.

The thesis of the owner's sketch is that a derivation should be a **description**
instead: `map` returns a node holding its upstream and its transform, `get()`
pulls through the chain, and nothing is stored anywhere except at the two ends —
the root cell that owns the value, and an explicit `.cell()` where a consumer
wants caching or sharing. That is Kotlin's Flow/StateFlow split with `stateIn`
as `.cell()`, or Rx's cold observables plus a BehaviorSubject; naming the
precedent puts its known costs on the table from the start (per-subscriber
recomputation, the combineLatest glitch, the initial value at materialisation),
and this paper answers each of them.

**What the measurement says.** A five-deep derivation on this tree, `node
--jitless` under callgrind, slope between 1 and 201 iterations:

| a five-deep derivation | cold pipeline | today's five cells | ratio |
|---|---:|---:|---:|
| build it, read it once | 51,455 Ir | 125,278 Ir | **0.41×** |
| per frame: one write, one pull read | 10,323 Ir | 44,725 Ir | **0.23×** |
| per frame: one write, one pushed leaf | 12,436 Ir | 42,864 Ir | **0.29×** |

The cold chain is cheaper on all three, and the reason is structural rather than
clever: it allocates two objects per node instead of a cell, a subscriber, a
subscription and their three `Shared`s, and it does no work at all for a chain
nothing is reading. The cost it *adds* is real and is stated at §6.2 — N leaf
subscribers on one chain means N evaluations of every transform in it — and
`.cell()` is the priced answer to that.

**Why the first filing is withdrawn.** The read-tracked `computed` needed an
ambient frame consulted on every `get()`, an untracked-callback footgun, and a
reversal of `reactive-batching.md`'s explicit-tracking stance. The pipeline keeps
that stance INTACT — every dependency is structural, written in the node's type —
and reaches the same "one primitive" answer the other way round: not one function
that discovers its dependencies, but one trait whose combinators are all the same
kind of thing. The first filing's claim that a lazy pipeline "doubles the
vocabulary" does not survive the sketch: the root IS a `Source`, the result of
`map` IS a `Source`, and only `.cell()` re-enters state. What DOES survive is
§2.5's relocation argument — totality is not avoided, only moved to the fallback —
and §8's "an effect writing a cell is a state machine, not a missing combinator".

## 1. Ground truth

### 1.1 What the sketch is

`kolt/src/lib/reactive2.vl` (pseudo-code; it does not compile, and it is not
meant to): a `Source<T>` trait with `map` and `sub`; an `Initial<T>` root that
owns a value and implements it; a `Map<T, O>` node that implements it and owns
nothing; `inspect(label, source: dyn Source<T>)` subscribing at the leaf. Seven
claims are made for it. Scored against this tree:

| the sketch's claim | verdict |
|---|---|
| lazy, with no tracking cost | **real** — a cold node has nothing to compute until someone pulls or subscribes; §7 measures zero evaluations for a chain with no leaf |
| async natively | **real, and the largest ergonomic gain** — a pending value is written on `T` and the `Option` appears once, at the fallback, instead of threading through every `map` (§2.5) |
| declarative and inspectable | **real** — a node tree is a value; it can be printed, dev-tooled, and middleware (an equality check, a debounce) is one more node |
| no intermediates | **real for a single consumer only** — where a derivation is shared a `.cell()` reappears, and it IS a cell (§6.2) |
| arbitrary caching | **real** — same mechanism, placed by the consumer |
| dynamic tracking via a node | **real** — that is `switch`/`and_then` as nodes (A123, landed this order as cells), not read-tracking |
| shorter type names via `dyn` | **real, and the one language feature** (§3) |

### 1.2 The names

The sketch renames today's `SignalCell<T>` to `Initial<T>` and keeps `Signal<T>`
as the writable trait beside the read trait `Source<T>` — the same three-way
split the library already has (`Source` reads, `Signal` writes, `SignalCell` is
the canonical cell that implements both). This paper writes the node structs with
the sketch's names where it quotes the sketch and otherwise keeps today's, and
records the rename as an open question (§9, Q1) rather than deciding it: the
root is written over its whole life, so `Initial` names only its first value; and
every `SignalCell<T>` annotation in std, kolt, the corpus, the docs and the
website moves with it, which is a breaking change whose only payer is a name.

### 1.3 The probe ledger — re-run on `next @49de3915`

`sweeps/order39/probes/a124_*.vl`, verified again on this tree:

| probe | spelling | result |
|---|---|---|
| a | trait requirement `fun dbl(self): Src<T>;` with impls returning nodes | REFUSED — "a trait is not a value type … a generic for a return" (B253) |
| b | `let count: Source<i32> = Signal::new(0)` then `.map` | runs (B161's bound-style binding) |
| c | a `Source<i32>` STRUCT FIELD holding a root and, separately, a mapped cell | runs — but both literals ground to `SignalCell<i32>`, so it is not a mixed test |
| d | `source: dyn Source<T>` parameter | parse error — `dyn` is not a token |
| e | bare `Source<T>` parameter (B186) taking a derived source | runs, `5 15` |
| f | free `fun doubled(): Source<i32>` | REFUSED (B253) |
| g | field grounded per literal with TWO node types, one `List` of both | REFUSED — `Expected Holder<Root> (this literal's element type), but got Holder<Dbl<Root>>` |
| h | the blanket-adapter spelling: `r.dbl().dbl().mapn(f)` through a bare-trait consumer and a trait-typed field | runs, `v=12` twice |

**And h now has a std-scale twin that is not a probe but a module.**
`vilan/std/src/reactive_pipeline.vl` builds the whole model — the cold trait, the
three node structs, `.cell()`, the leaf — over today's `Source`, with no compiler
change, against the real `SignalCell`, `Subscription`, `Owner` and turn
machinery. It compiles, it runs, and §7 is its numbers. **The model is buildable
today, minus `dyn`.** That is the single most load-bearing fact in this paper:
the redesign is not a rewrite of the reactive core, it is a re-placement of where
state sits, and the core's existing machinery carries it unmodified.

## 2. The model, in five parts

### 2.1 The trait

> **R1, RULED 2026-09-22.** `get` stays on the trait.

`Source<T>` carries exactly what it carries today:

```vilan
export trait Source<T> {
	fun get(self): T;
	[must_use]
	fun on_change(self, observer: |T| void): Subscription;
	// sub / effect / effect_on_change / scoped_effect stay DEFAULTS over those two
}
```

A node's `get` is `f(upstream.get())`, which is what makes every cold chain
pull-readable and is the lazy derivation with no tracking machinery anywhere.
Keeping `get` is also what keeps the trait object-safe — §3 depends on it.

Every combinator is a **blanket method** on `S: Source<T>` returning a concrete
node:

```vilan
export impl type S: Source<type T> {
	fun map<U>(self, transform: sync |T| U): Map<S, T, U>
	fun switch<U, I: Source<U>>(self, select: sync |T| I): Switch<S, T, I>
	fun combine<Y, B: Source<Y>>(self, other: B): Combine<S, B>
	fun cell(self): SignalCell<T>
}
```

which is the spelling `flatten` and A123's two already use. A combinator is NOT a
trait requirement: the return-position existential is refused (B253, RULED keep
2026-09-07; probes a and f), and a generic requirement is what makes a trait
non-object-safe anyway (`trait-objects.md` P13). The blanket form is therefore
not a workaround — it is the only form that is simultaneously admissible,
extensible by a third party, and compatible with `dyn`.

### 2.2 Nodes are cold and stateless

A node holds its upstream and its operation. Nothing else. Written out, as built
in S1:

```vilan
/// `map` as a node. The transform is held PLAIN (`|T| U`, not `sync |T| U`):
/// the `sync` contract is accepted on a parameter and not on a field, so it is
/// checked at the combinator that builds the node — the J2 pattern `std::rpc`
/// already uses.
export struct Map<S, T, U> {
	up: S,
	transform: |T| U,
}

export impl Map<type S: Source<type T>, T, type U> with Source<U> {
	fun get(self): U {
		(self.transform)(self.up.get())
	}
	fun on_change(self, observer: |U| void): Subscription {
		self.on_settle(|| observer(self.get()))
	}
}

/// `switch` as a node (A123's dynamic dependency, cold): which inner source to
/// follow is decided by the upstream's CURRENT value, at every read.
export struct Switch<S, T, I> {
	up: S,
	select: |T| I,
}

export impl Switch<type S: Source<type T>, T, type I: Source<type U>> with Source<U> {
	fun get(self): U {
		(self.select)(self.up.get()).get()
	}
	fun on_change(self, observer: |U| void): Subscription {
		self.on_settle(|| observer(self.get()))
	}
}

/// `combine` over a PAIR; the n-ary family is the same body with one more
/// field, over a tuple bound.
export struct Combine<A, B> {
	left: A,
	right: B,
}

export impl Combine<type A: Source<type X>, type B: Source<type Y>> with Source<(X, Y)> {
	fun get(self): (X, Y) {
		(self.left.get(), self.right.get())
	}
	fun on_change(self, observer: |(X, Y)| void): Subscription {
		self.on_settle(|| observer(self.get()))
	}
}
```

Two properties follow and both are measured in §7:

1. **Construction does nothing.** `map_node` allocates the node and returns. No
   cell, no subscriber, no evaluation. A five-deep chain built and never read
   costs the five allocations and stops there.
2. **N subscribers means N evaluations** — by design, not by defect. The
   consumer that wants sharing writes `.cell()`, and §6.2 prices when that is
   the right call.

**On `Switch` and the rolling registration.** `Switch` is the one node that
cannot be purely stateless at the *subscription* level: a downstream told
"something settled" must keep being told when the NEW inner changes, and only a
live registration can do that. Its `get` is still pure (select, then pull), and
its state is one `Option<Subscription>` that the attach owns and the teardown
releases — A28's story exactly, inherited from `flatten`.

### 2.3 Notifications carry no value; leaves pull

> **R2, RULED 2026-09-22 as recommended.** A notification carries NO payload and
> the leaf pulls through `get()`; ONE subscriber id per leaf chain, so door 2's
> dedup absorbs a diamond's duplicate. With the owner's note: **cells are welcome
> MID-CHAIN.** A complex mapping finished with `.cell()` (the owner's name; not
> `memo()`) gets an efficient cached value; cells at EVERY step is what is
> inefficient. `.cell()` is therefore one more node, composable anywhere.

The protocol is a second, no-payload attach beside `on_change`:

```vilan
/// The no-payload half. A trait requirement and not a blanket, for one reason:
/// a node must FORWARD the observer to its upstream untouched. A blanket over
/// `S: Source<T>` could only write `self.on_change(|_value| observer())`, and
/// for a node that is the payload path — the transform runs to produce a value
/// the blanket then throws away, once per hop. (Measured: with the blanket
/// form, the five-deep chain's one-leaf settle costs 15 evaluations instead of
/// 5, and two leaves cost 30 instead of 10.)
export trait Cold<T> with Source<T> {
	[must_use]
	fun on_settle(self, observer: || void): Subscription;
}
```

- the root: `fun on_settle(self, observer) { self.on_change(|_value| observer()) }`
  — the one place a `Subscriber` is minted;
- `Map`: `self.up.on_settle(observer)` — **forwarded, not wrapped**; no
  subscriber minted, no transform run;
- `Combine`: one forward per arm;
- `Switch`: a forward that re-attaches the inner on every outer settle;
- the leaf: `source.on_settle(|| observer(source.get()))`.

So a settle walks the chain's *registration* once at attach time and thereafter
costs one call plus one pull per leaf. This is TC39 Signals' and Solid 2.0's
push-pull split, with the pull being ordinary `get`.

**Against `reactive-turns.md` §7 and A110 door 2.** Door 2's rule is
"derivations run to a fixpoint first; then effects run in ascending subscriber
id", and it needs two things of the pipeline:

- *Derivation class.* A cold node has no subscriber of its own, so it has no
  class: the only subscribers a chain mints are the root registration the leaf
  threads down, and `.cell()`'s. `.cell()` marks its registration
  `as_derivation()` exactly as `map` does today, so phase 1 settles a cached node
  before any effect runs. Everything else settles by *being pulled*, which is
  ordering-free — a pull always reads the root's current value, and the root is
  written before any subscriber runs.
- *The diamond.* `combine((a.map(f), a.map(g)))` receives two notifications per
  change of `a`. Under the payload protocol that is the combineLatest glitch —
  the first notification carries a half-updated pair. Under pull it is not: the
  leaf reads `(f(a), g(a))` from the settled root **both times**. The remaining
  defect is a duplicate CALL, and R2's answer is one subscriber id per leaf
  chain, so `enqueue`'s dedup (`reactive.vl`, keyed on `subscriber.id`) collapses
  it to one.

> **Finding — R2's "one id" is std work, and this is the line it costs.** S1
> measures the diamond firing **twice** per settle with a settled pair both times
> (`(20,102)(20,102)`, pin
> `a124_s1_a_diamond_pulls_a_settled_pair_and_fires_twice`). It cannot do better,
> because `observe` mints `fresh_id()` itself, once per attach, and a chain that
> forwards one observer through two arms still reaches the root twice and mints
> two ids. Collapsing the duplicate needs the leaf to mint ONE `Subscriber` and
> every registration in its chain to carry that id — i.e. `on_settle` (or
> `observe`) taking an id rather than minting one. That is a small, contained
> change to `reactive.vl` and it belongs in S2's scope with a pin of its own.
> The pin at `crates/vilan-cli/tests/reactive_lifetimes.rs:1036`
> (`a110_door2_an_effect_reads_a_derivation_chains_final_value_once`) re-derived
> under the cold arms reads: the VALUE claim holds by construction (every read is
> a pull of settled state, so `fixpoint=5/11` cannot become `5/3`), and the COUNT
> claim is what the threaded id buys.

### 2.4 State at the ends

The root cell owns the value and is unchanged — `SignalCell<T>` with its two
`Shared`s, its subscriber list and door 1's liveness bit.

`.cell()` is the ONE stateful node:

```vilan
fun cell(self): SignalCell<T> {
	let cached = SignalCell::new(self.get());
	as_derivation();
	let _owned = register_with_owner(self.on_settle(|| {
		cached.set(self.get());
	}));
	cached
}
```

A cell holding the last value, owner-tied like today's `map` (A28) and marked a
derivation (door 2). Its result is a `SignalCell`, which is itself a source, so a
chain continues straight through it — that is what "composable anywhere" means,
and it is the difference between this and Kotlin's `stateIn`, which terminates a
flow. It is where a shared derivation, a `get()` in a hot loop, a
`dyn`-typed field wanting a concrete type, or a heterogeneous collection
materialises.

> **RULED 2026-09-25 (the owner, after Order 41's seal; A124 Q-no-cycle, A130).**
> A `.cell()` at MODULE level is a leak by design unless released: while anything
> is subscribed to it, its root keeps a strong loop — root list → subscriber
> record → node → root — that no owner will ever cut (reactive-41's no-cycle gate
> found exactly this shape under the flip, §11). So the gate's exemplar builds its
> `.cell()` under an owner; `.cell_global()` is the spelling that says a
> program-lifetime cell is meant (the gate excludes it by name); and `.cell()`
> written directly in a module binding's initializer is REFUSED with a steer to
> either. The refusal is static only (R-e): a cell built at module init through a
> call is the documented remainder. Order 42 (reactive-42) builds it inside the
> flip's commit.

### 2.5 Pending values are outside the trait — `Resource<T>`

> **R5, RULED 2026-09-22.** The pending family is `Pending<T>` or `Resource<T>`
> — the paper picks, with `Resource<T>` recommended, since it can go from settled
> BACK to pending when an upstream changes, and the paper states that state
> machine — with BOTH `.or(default)` → `Source<T>` and `.optional()` →
> `Source<Option<T>>`. Sub-question for the paper: on re-pend, does `.or` reset
> or hold?

**The paper picks `Resource<T>`.** `Pending<T>` names one of its three states and
so is wrong two thirds of the time; `Task<T>` is taken by the executor and means
a one-shot; `Resource<T>` is Solid's word for exactly this object and carries the
re-pending behaviour in its ordinary reading ("the resource for *this* id").

A task, a fetch, or a stream that has not emitted is NOT a `Source`: it cannot
answer `get`. It is its own small family with `map`/`then` of its own, and it
becomes a `Source` only through a fallback.

**The state machine, stated.**

```
                 ┌──────────── an upstream source changes ────────────┐
                 v                                                    │
   [pending] ──(the fetch settles)──> [settled v] ──(re-fetch)──> [pending]
       │                                   │                          │
       │                                   └──(the fetch fails)──> [failed e]
       └──(the fetch fails)──────────────────────────────────────────>┘
```

- **pending → settled.** The first completion.
- **settled → pending.** A `Resource` built over a source re-fetches when that
  source changes. This is the state today's `SignalCell<Option<T>>` model layer
  cannot distinguish from "loaded, and empty", and it is the whole reason the
  family is not just an `Option`.
- **failed** is a third state and not a settled `Err`: a failed resource can be
  retried, and a retry is a re-pend.

**The two fallbacks, both required by R5.**

```vilan
impl Resource<type T> {
	/// Total, with a stand-in until (and while) pending.
	fun or(self, default: T): impl Source<T>
	/// Total, with absence as a value — `None` while pending or failed.
	fun optional(self): impl Source<Option<T>>
}
```

`.optional()` is the honest one and is what a model layer wants; `.or(default)` is
the one a view wants, because a `0` or an empty list paints.

**The sub-question: on re-pend, does `.or` reset or hold?** The paper
recommends **reset**, and a third op for the other reading:

- `.or(default)` **resets to `default`** while pending. It is the only answer
  consistent with `.optional()`, which must answer `None` (it has no value to
  report); a `.or` that holds would make `x.or(0)` and
  `x.optional().map(|v| v.unwrap_or(0))` two different programs, which is exactly
  the kind of quiet divergence the library has spent three papers removing.
- `.latest(default)` **holds** the last settled value across a re-pend and only
  shows `default` before the first one. That is the "keep the old list visible
  while the new one loads" behaviour every real UI eventually wants, and it is
  better as a NAME than as a mode: the two are different products (one flickers
  to a spinner, one shows stale data), and a reader should be able to tell which
  one a call site chose without reading a boolean.

A `.is_pending(): impl Source<bool>` rides beside them for the spinner, which is
what keeps `.latest` honest.

## 3. `dyn Source<T>` — the delta to `trait-objects.md`

> **R3, RULED 2026-09-22.** `dyn Source<T>` over the object-safe core (`get`,
> `on_change`), explicit keyword, no resources; AND a bare `Trait` at a struct
> FIELD is REFUSED for now with a steer to `dyn Trait` (B184's hidden generic at
> fields is withdrawn at that position; parameters (B186) and bindings (B161) are
> unchanged).

This section is a **delta** to `trait-objects.md`, not a replacement: that paper's
§6 representation, §7 coercion rule, §8 resource refusal and §9 precedence
analysis stand as written. Four things change.

### 3.1 The trigger is met, for the first time, by an application

`trait-objects.md` §3.5 DECLINED trait objects and named three criteria for a
revisit, all three required: a registry that is (a) genuinely open, (b) needs the
trait's *checked* surface rather than a closure field, and (c) cannot be a
generic because the set is assembled where the literal is built. A pipeline field
is all three at once, and probe g is the evidence for (c): a `Holder` over a root
and a `Holder` over a mapped node are `Holder<Root>` and `Holder<Dbl<Root>>`, one
`List` of both is refused, and B184's hidden parameter is viral through every
embedding struct. §3.5 also named where it would first appear — "`Transport` and
`Source` (§4)". It appeared at `Source`.

### 3.2 The object-safety census, re-run for `Source` only

`trait-objects.md` §4's three disqualifiers are: no receiver (a static), `Self` in
a return, and a generic member. Against today's trait:

| member | kind | object-safe? |
|---|---|---|
| `get(self): T` | requirement | **yes** — receiver, no `Self`, no generic |
| `on_change(self, observer: \|T\| void): Subscription` | requirement | **yes** |
| `sub`, `effect`, `effect_on_change`, `scoped_effect`, `scoped_effect_on_change` | defaults over the two | yes, and they need no slot — a default is emitted once over the object |
| `map`, `switch`, `and_then`, `combine`, `flatten`, `cell` | BLANKETS, not members | not slots at all — §3.4 |

**The core is exactly two slots, `get` and `on_change`**, which is what R3 says
and is what a vtable for `Source<T>` carries. Nothing in the redesign adds a
requirement: every combinator is a blanket, deliberately (§2.1), and that is also
what keeps the trait object-safe as the library grows. `trait-objects.md` §4's
recommendation stands unchanged — object safety is a per-trait property the
compiler computes, and a non-object-safe trait in object position is refused
naming the **disqualifying member**, not the trait.

`Signal<T>` (the writable half) is object-safe too on the same test (`set`,
`notify` are receiver-taking and `Self`-free; `new` is a static and would be the
one disqualifier, so a `dyn Signal<T>` is out unless `new` moves — which the
paper does not ask for, because nothing wants to store a writable pipeline
behind erasure).

### 3.3 Drop glue for a resource-free object

`trait-objects.md` §8 designed the glue and then recommended refusing resources
in v1, "a choice with a known price". R3 takes that refusal. The consequence for
this design is the pleasant one: **a `dyn Source<T>` needs no `$drop` slot at
all.** Every value it can hold is a node struct or a cell — plain aggregates of
`Shared`s and closures, with no `Drop` body and no affine obligation — so
scope-end teardown of a `dyn`-typed binding is the ordinary aggregate teardown
the compiler already emits, with nothing dispatched. The vtable is two slots,
not three.

What a `dyn` holder still owes is *subscription* teardown, and that is unchanged
and not a drop question: a chain's registrations belong to the ambient `Owner`
(A28), which releases them whether or not the holder is erased.

### 3.4 The blanket over the object

`impl dyn Source<T> with Source<T>` — Rust's `Box<dyn Iterator>` shape — is what
makes every blanket combinator apply to an object: `map`, `switch`, `and_then`,
`combine`, `cell` are written over `S: Source<T>`, the object satisfies
`Source<T>`, so a field-held pipeline can be mapped further without being
un-erased. This is the one addition to `trait-objects.md`'s plan, and it is the
difference between a `dyn` that is a dead end and a `dyn` that is a node.

### 3.5 The field refusal, and what it costs

R3 withdraws B184's hidden generic **at fields** and refuses a bare `Trait` there
with a steer to `dyn Trait`. Parameters (B186, probe e) and bindings (B161, probe
b) are unchanged, which matters: those two are where the bare spelling reads well
and costs nothing, because the generic is ordinary and monomorphizes.

The estate cost of the refusal is the dyn-40 lane's census, not this paper's, but
one correction belongs here, because A124's own filing got it wrong and the brief
inherited the error:

> **Correction.** A124 (and `briefs40.md`) name `Searchable<T>` and
> `InputLayer<T>` as kolt's bare-trait struct fields. They are **not traits** —
> both are `struct` declarations (`kolt/src/lib/search.vl:5`,
> `kolt/src/lib/input_system.vl:77`), and a census of kolt on 2026-09-22 finds
> **zero** struct fields whose declared type is a trait name. The only traits
> declared anywhere in kolt are in the `reactive2.vl` sketch itself. The closest
> real phenomenon is type-parameter erasure through `any`
> (`StackedLayer.layer: InputLayer<any>`, `lib/input_system.vl:33`;
> `StorageKeyAllocator.keys: Set<StorageKey<any>>`, `lib/storage.vl:36`) — which
> is the same need answered by the same feature, and is worth the dyn lane
> knowing about, but it is not the breaking surface the brief expects. Kolt's
> bare-trait spellings are all in parameter position (`comp/login.vl:72`, `:174`;
> `channel.vl:280`, `:353`) and in one local annotation, and R3 leaves all of
> them alone.

## 4. Kolt, classified

Census of `/home/reed/code/kolt/src` (excluding the generated `src/lucide`) on
2026-09-22, at kolt `9a057c6`. Counting rule for a "reactive map": a `.map(` on a
signal, cell, source, or the result of one — `Option`/`Result`/`List`/`Iterator`
maps excluded, comments excluded.

### 4.1 The derivations

**55 reactive maps** in live application code (plus one in the sketch). Each was
classified by how many places read its result:

| class | count | share | what the redesign does with it |
|---|---:|---:|---|
| **single-consumer** — one binding, one hole, one `get`, one `effect` | 38 | 69 % | a cold node; no cell allocated, no subscriber minted |
| **shared** — two or more readers | 8 | 15 % | an explicit `.cell()`, which is what it already is |
| **stored** — written into a struct field or a module-level container | 8 | 15 % | a `dyn Source<T>` field (or a `.cell()`, §4.3) |
| unclear (one generic helper with two fates per call site) | 1 | 2 % | `model.vl:134`, `map_safe` — see §4.4 |

| file | maps | single | shared | stored |
|---|---:|---:|---:|---:|
| `views.vl` | 23 | 15 | 4 | 4 |
| `channel.vl` | 11 | 10 | 1 | 0 |
| `model.vl` | 6 | 2 | 2 | 1 |
| `theme.vl` | 5 | 4 | 1 | 0 |
| `store.vl` | 3 | 3 | 0 | 0 |
| `lib/overlay.vl` | 2 | 2 | 0 | 0 |
| `lib/search.vl` | 2 | 0 | 0 | 2 |
| `client.vl`, `comp/login.vl`, `lib/storage.vl` | 3 | 2 | 0 | 1 |

The eight that need a `.cell()`: `views.vl:263`, `:441`, `:702`, `:705`;
`channel.vl:21`; `model.vl:85`, `:111`; `theme.vl:125`.

**Read the 69 %.** Today every one of those 38 sites allocates a cell, a
subscriber, a subscription and three `Shared`s, and recomputes eagerly on every
upstream write, to serve exactly one reader that could have pulled. That is the
redesign's whole case, and it is two thirds of the application.

**The densest site is worth quoting**, because it is also A123's:

```
channel.vl:35   let author = message.map(|x| x.map(|x| x.author.user())).flatten().map(|x| x.flatten());
channel.vl:40   ui::when_some(reactive::combine((message, author)).map(|(m, a)| m.zip(a)), |pair| {
channel.vl:41     let (message, author) = divorce(pair);
channel.vl:20   fun divorce<A, B>(source: SignalCell<(A, B)>): (SignalCell<A>, SignalCell<B>) {
channel.vl:21     (source.map(|(a, _)| a), source.map(|(_, b)| b))
```

Seven cells per message row, of which two are read twice and five serve one
reader each. Under A123 line 35 is already one call (`message.and_then(|m|
m.author.user())`); under the pipeline the row costs one `.cell()` at `pair` and
nodes for the rest.

### 4.2 The signal-typed fields — 19 across 10 structs, and 3 need `dyn`

A124's claim of **19 signal-typed struct fields across 10 structs holds exactly**.
What matters for §3 is what each one STORES:

| struct.field | file:line | stores |
|---|---|---|
| `Searchable.table` | `lib/search.vl:7` | **always a derived pipeline** (`list.map(..)`) |
| `AppContext.route` | `app_context.vl:16` | **always a derived pipeline** (`current_path().map(..)`) |
| `Command.name` | `views.vl:548` | **mixed** — derived at `:581`, `:597`, `:629`, `:647`; a root cell at `:613`, `:621`, `:663`, `:672`, `:681`, and both kinds live in ONE list literal |
| the other 16 | — | always a root `Signal::new` cell |

**Only three of the nineteen need `dyn Source<T>`**, and `Command.name` is the
one that needs it *irreducibly*: it is probe g's refusal, in production, in a
single list literal. The other sixteen keep a concrete `SignalCell<T>` and are
untouched by R3's refusal, because a concrete type is not a bare trait.

Two adjacent categories the 19 does not count, and the migration will meet:
`GlobalStore.users` (`store.vl:105`) is a `Memo<UserId, SignalCell<Option<User>>>`
— a signal-typed *value* inside a table, not a field — and `Prefs` holds nine
`StorageSignalCell<..>` fields, a concrete wrapper that `impl … with Signal<T>`,
so signal-*behaving* and not signal-*typed*.

### 4.3 Where a `.cell()` beats a `dyn`

A stored derivation has two spellings under the redesign: erase it
(`dyn Source<T>`, keep it cold, pay §6.2's per-leaf cost at every read) or
materialise it (`.cell()`, store a `SignalCell<T>`, pay one cell). The rule the
census suggests:

- **`.cell()` when the field is read by more than one place or read hot** —
  `Searchable.table` is read by every keystroke of a filter, so it materialises.
- **`dyn Source<T>` when the field's *type* is what varies** — `Command.name`,
  where the whole difficulty is that two literals in one list disagree about the
  pipeline, and nothing about the value wants caching.
- `AppContext.route` can take either; it is read in four places, so `.cell()`.

So R3's feature is load-bearing for **one** kolt field today, and for the general
shape (a list of heterogeneous pipelines) that field is an instance of. That is a
narrow win, and the paper says so plainly: `dyn` is not what makes the pipeline
pay, it is what makes the pipeline *storable*.

### 4.4 A124's other counts, corrected

The census verified every number in A124's kolt paragraph. Three are wrong and
two hold only as raw greps; the classification above uses the corrected ones.

| A124 said | verdict | actual |
|---|---|---|
| 59 `.get()` reads | textually true | 49 reactive reads (8 are `Context::get`, 1 `StorageKey::get`, 1 a comment) |
| 74 `.map(` chains | raw grep | 55 reactive (2 comments, 16 `Option`/`List`/`Iterator` maps, 1 sketch) |
| 15 `combine` sites | **wrong** | **5** — `channel.vl:40`, `theme.vl:217`, `views.vl:471`, `:704`, `:770`. (`combine` also appears twice in `src/lucide` as an ICON NAME, which is where the inflation came from) |
| 6 `flatten` | raw grep | **2** reactive — `channel.vl:35`, `model.vl:134`; the other four are `Option::flatten` and a comment |
| 8 `effect` | **holds** | 8 |
| 19 signal fields / 10 structs | **holds exactly** | 19 / 10 |
| 32 signal-typed parameters | **wrong** | **11** parameters (37 if signal-typed *return types* are counted too, which is 26 more) |
| one memo table of shared cells, `store.vl:105` | holds as a location, undercounts | **6** memo-of-cells tables: `store.vl:105` plus five module-level ones in `model.vl` (`:42`, `:59`, `:60`, `:61`, `:115`) |

The last row is the interesting correction: **kolt already hand-rolls `.cell()`
six times.** A memo table keyed by id, whose values are cells shared between
every consumer of that id, is precisely the materialisation node this design
makes a method — and it is the strongest evidence that `.cell()` is a real
primitive and not a concession.

## 5. Migration

> **R4, RULED 2026-09-22.** Kolt migrates; same names; the v0.41.0 cut may come
> BEFORE the migration if that works better — it is not a blocker on the cut.

Same names means `map`, `combine`, `switch`, `and_then` and `flatten` keep their
spellings and change their RETURN TYPES, from `SignalCell<U>` to a node. What
breaks, precisely:

1. **Every annotation that names the result type.** `let x: SignalCell<U> =
   s.map(..)` becomes `let x = s.map(..)`, or `s.map(..).cell()` where the cell
   is wanted. In kolt that is the 19 fields' three derived cases plus every
   annotated local; in std it is the internal uses in `std::ui`, `std::rpc` and
   `std::router`.
2. **Every call that writes to a derivation.** There are none by contract — a
   derived cell is read-only by convention today — but `SignalCell`'s inherent
   `update` is reachable on one, and a node has no `update`. The compiler finds
   these; they are a rename to `.cell()`.
3. **Nothing about `Source`-typed parameters**, which is the large surface: 11 in
   kolt, 32 in std. A node satisfies `Source<T>`, so a parameter written against
   the bound takes one unchanged. This is why the migration is finite.

**The order this paper recommends** (each step green before the next):

- **S2a — the protocol.** `on_settle` (or `observe` taking an id) in
  `reactive.vl`, the threaded leaf id, the diamond's count pin. No surface
  change; door 2's pins re-run.
- **S2b — the nodes.** `Map`, `Switch`, `Combine` and `.cell()` shipped, with the
  combinators still returning cells, so nothing moves yet. `.cell()` is the
  first new public name.
- **S2c — the flip.** The combinators return nodes. This is the breaking step;
  it rides the same train as I5's `usize` change, and the estate sweep is one
  pass over `SignalCell<` annotations.
- **S3 — kolt**, at the owner's word, after the flip.

`dyn` (the dyn-40 lane, this order) is INDEPENDENT of all four and can land
first, which is what R-a asked and what §3 supports: the object's core is `get` +
`on_change` whether a combinator returns a cell or a node.

## 6. The cost table

All Ir figures: callgrind, `node --jitless`, the slope between 1 and 201
iterations so that node's startup (~168 M Ir) and the graph's construction
cancel. Measured on `next @49de3915` + A123, loadavg 25–59 across the runs — Ir
is an instruction count and does not move with load.

### 6.1 Per read, per frame, per chain

| a five-deep derivation | cold pipeline | five `map` cells | ratio |
|---|---:|---:|---:|
| construct, then read once | 51,455 Ir | 125,278 Ir | 0.41× |
| per frame: one root write, one leaf `get()` | 10,323 Ir | 44,725 Ir | 0.23× |
| per frame: one root write, one pushed leaf | 12,436 Ir | 42,864 Ir | 0.29× |

Both models print the same total on the same program, which is the control.

**Allocation per node.** A cold `Map` is one struct plus its stored closure — two
objects, and on this backend a struct is a bare array. Today's `map` allocates a
`SignalCell` (a struct over two `Shared`s), a `Subscriber` (four fields, one of
them its own liveness `Shared`, one of them a closure), a `Subscription` (a
`Weak`, two `Shared`s) and the observer closure — nine objects and three `Shared`
cells, per node, per chain. The 2.4× construction gap above is that difference,
measured.

**C14's arena applies to `.cell()` only.** The owner-arena work in
`signal-cell-representation.md` is about cells; a cold node has no cell to place
in an arena, so the redesign shrinks C14's subject rather than competing with it.

### 6.2 What the cold model costs, stated plainly

**N leaf subscribers on one chain evaluate every transform N times.** S1 measures
it: 5 evaluations for one leaf on a five-deep chain, 10 for two, and the numbers
are the pins. Today's cells evaluate once regardless of the number of readers.
Three things keep this from being the design's defeat:

1. **69 % of kolt's derivations have exactly one reader** (§4.1), where the cold
   model is strictly cheaper.
2. **`.cell()` is where the other 31 % goes**, and it restores today's behaviour
   exactly — one evaluation, one cached value — at the one site that needs it
   rather than at all of them. S1 pins the placement working: two leaves below a
   cell run the segment ABOVE it once and the segment below it twice.
3. **The crossover is computable.** A cold chain of depth d with k leaves costs
   k·d transform applications per settle plus k pulls; the cell model costs d
   applications plus k reads plus d cell writes and d subscriber walks. At the
   measured per-node costs on this tree, one leaf is always cheaper cold; two
   leaves are cheaper cold for trivial transforms (12.4k×2 against 42.9k) and the
   answer flips as the transform gets expensive. **Rule for the guide: one
   reader, leave it cold; two or more, or an expensive transform, `.cell()` it.**

### 6.3 The native backend

A `dyn Source<T>` on `vilan-rust`/`vilan-rt` is a fat pointer: the value pointer
plus a vtable pointer, with **two slots** (`get`, `on_change`) and — per §3.3 —
no drop slot, because the object holds no resource. That is F1's shape and
`trait-objects.md` §6.1's forward-compatibility claim ("(value, vtable) survives
as a two-word pair, which is what a fat pointer is"), confirmed for this trait.
Cold nodes themselves need nothing new natively: they are plain generic structs
and monomorphize exactly as the corpus's other generics do.

## 7. S1 — what was built, and what it showed

`vilan/std/src/reactive_pipeline.vl`, this order, no compiler change. It is
exported but re-exported through no prelude and imported by no other std module:
it is evidence, not surface. Four pins hold its numbers
(`crates/vilan-core/tests/inference/lifetimes.rs`), each shown red with its
mechanism planted back:

| claim | measured | red when |
|---|---|---|
| a five-deep cold chain with NO subscriber evaluates zero times across three root writes; one `get()` then costs five | `0 → 0 → 5` | the node registers at construction: `0 → 45 → 50` |
| one leaf costs five evaluations per settle, two cost ten | `5`, `10` | `on_settle` goes through the payload path: `15`, `30` |
| a `.cell()` between runs the segment above it once and the segment below per leaf | `upper=2 lower=6` | `.cell()` does not register upstream: `0`, `0` |
| a diamond's leaf reads a SETTLED pair, twice | `(20,102)(20,102)` | `Combine` registers one arm: `(20,102)` once |

Three things S1 found that the design did not predict:

1. **The payload-path blanket is a trap.** Writing `on_settle` as a blanket over
   `S: Source<T>` (`self.on_change(|_| observer())`) instead of a trait
   requirement triples the evaluation count, because every hop computes a payload
   it discards. The no-payload attach has to be a REQUIREMENT that each node
   overrides, which is why §2.3 spells it as one.
2. **One id per leaf chain is not free** (§2.3's finding) — `observe` mints the
   id, so S2 owes a threaded one.
3. **A malformed impl subject cascades into every dispatch of its trait.** While
   building S1, an impl subject written with one type argument too many
   (`Switch<S, T, I, U>` against `struct Switch<S, T, I>`) IS refused at its own
   spelling — but the refused impl still enters the candidate set with an
   UNKNOWN subject, so every later dispatch of that trait also fails, with
   *"both `SignalCell<T>` and `unknown` provide it and neither impl subject is
   more specific"*, pointed at innocent call sites in USER code while the real
   error sits last in the list. `inference/traits.rs` already pins the
   corresponding rule for fields (`a_refused_field_does_not_cascade_through_its_uses`);
   a refused impl subject wants the same. Repro:
   `sweeps/order40/reactive-40/unknown_impl_subject_cascades.vl` — one struct,
   one over-applied impl, one call.

## 8. What is NOT a derivation, and stays an effect

`theme.vl:128` and `:145`, `views.vl:707`, `channel.vl:370` each pair a source
with `.effect(|x| other.set(..))` where `other` is ALSO written by the user — a
selection index reset when the filter changes, a form field seeded from data.
That is a state machine with two writers, not a transform; no combinator library
expresses "derived default, user-overridable" except as an effect writing a cell
(Solid's `createWritableMemo` is the same thing with a name). Those sites are
already spelled right. A `reset_on(source, |x| initial)` helper would be sugar,
not a primitive. Recorded here so that "every effect+signal pair is a missing
combinator" is not the reading taken from §4's numbers.

## 9. Open questions

- **Q1 — the root's name.** Keep `SignalCell<T>`, or take the sketch's
  `Initial<T>`? *Rec: keep `SignalCell`.* The root is written over its whole
  life, so `Initial` names only its first value; the rename moves every
  annotation in std, kolt, the corpus, the docs and the website, and buys a
  shorter word. `Signal<T>` stays the writable trait and `Source<T>` the read
  trait either way, which is the split the sketch and the library already agree
  on.
- **Q2 — `.or` on a re-pend** (R5's sub-question). *Rec: `.or` RESETS to the
  default; `.latest(default)` holds.* §2.5 argues it: a holding `.or` would make
  `x.or(0)` and `x.optional().map(|v| v.unwrap_or(0))` different programs.
- **Q3 — does `.cell()` take an equality check?** Today's cell notifies
  unconditionally (`set` never compares) and `Selector` exists because of it.
  *Rec: `.cell()` does NOT compare, and a `.distinct()` node does* — one more
  node, composable anywhere, `T: PartialEq` at that method only, which keeps
  `.cell()` usable for a `T` with no equality.
- **Q4 — is `on_settle` public?** It is a second attach on the read trait, and a
  third-party node needs it. *Rec: yes, public and documented as the node
  author's requirement, with `on_change` remaining the one every application
  writes.*
- **Q5 — does the flip (S2c) ride the v0.41.0 breaking train or wait?** *Rec:
  wait one order behind I5.* R4 already frees the cut from the migration; two
  breaking trains in one cut makes a bisect between them impossible.

## 10. The recommendations, collected

1. **Build it.** The model is buildable today over the existing core (§1.3), it
   is cheaper on all three measured shapes (§6.1), and it costs one stated thing
   — N evaluations for N leaves — with a priced answer (§6.2).
2. **The pending family is `Resource<T>`**, with `.or` (resets), `.optional()`,
   `.latest(default)` and `.is_pending()` (§2.5).
3. **`dyn Source<T>` over exactly `get` + `on_change`**, explicit, resource-free,
   no drop slot, with `impl dyn Source<T> with Source<T>` so the blankets reach
   the object (§3). Independent of the node work; it can land first.
4. **`.cell()` is the one stateful node**, composable anywhere, marked a
   derivation, owner-tied (§2.4) — and kolt's six hand-rolled memo tables are the
   evidence that it is a primitive (§4.4).
5. **S2a first: the threaded subscriber id.** It is the one piece of R2 that S1
   could not demonstrate and the one the diamond's count depends on (§2.3).
6. **Correct the record on kolt's numbers** (§4.4) and on the bare-trait fields
   (§3.5) before either is used to size a migration.

## 11. As built (Order 41, lane reactive-41, 2026-09-24)

S2a and S2b landed on `next` (bb798cbc, 29c0f2bb; the guide's "Where a derivation
lives", b3fa0a47); S2c was PREPARED as a saved patch and is Order 42's, the
train's last car. Where the build differs from §2 and §5, the build is right and
this section says so.

**S2a — the protocol (bb798cbc).** §2.3's `on_settle(self, observer: || void)`
could not carry one id per leaf chain: a bare closure has no id to thread. It
takes the leaf's `Subscriber` RECORD instead (id, class, liveness), and it is a
DEFAULTED member of `Source`, not a requirement — a requirement would have broken
every implementation. So §2.3's separate `Cold<T>` trait and S1's probe of it are
retired. `observe` is now mint + attach: `mint_subscriber` is the one place the
door-2 derivation mark is spent. The default bridges over `on_change` and wakes
through the DRAINING turn only; reading the ambient turn would give the member a
hidden context parameter, which a native `dyn` slot refuses. **The diamond fires
ONCE in a turn** (the pin reds with a fresh id per registration) — **and still
TWICE inline**, with no turn open, which §2.3 did not say: the dedup is the
turn's, so outside one each arm's registration notifies the leaf. Re-run for
this section (`sweeps/order42/papers-42/probes/asbuilt/diamond_inline.vl`):
`in a turn: (30,103)`, `inline: (40,104)(40,104)`.

**S2b — the nodes (29c0f2bb).** `Map<S, T, U>`, `Switch<S, T, I, U>`,
`Combine<T>` over `(U in T: dyn Source<U>)`, `Distinct<S, T>`; `.cell()`,
`.distinct()`; and `Resource<T>` / `ResourceState<T>` with `.or` (resets, Q2 as
recommended), `.latest`, `.optional`, `.is_pending`. §2.1's `Map<S, U>` and
`Switch<S, I>` do not compile as written: a field's type must name every type it
mentions, and the transform is a field, so the upstream's `T` is a struct
parameter. The transform is held plain (`|T| U`) because `sync` is accepted on a
parameter and not on a field; it is checked where the node is built. Four
compiler defects shaped the rest, each named at its site in `reactive.vl`:

- **B409** (a default inherited through an impl whose bound names the SAME trait
  checks that bound at the implemented argument) → the upstream bound is a
  private `Upstream<T>` blanket under a second name;
- **B410** (an override of a trait default is not selected through a bound when
  the trait's argument is a tuple) → every node's `on_change` calls its OWN
  `on_settle` on `self`, never through the bound;
- **B411** (a default's closure parameter is typed with the unsubstituted binder
  through a nested `type I: Source<type U>`) → `Switch` binds `U` directly, as a
  fourth, phantom parameter;
- **B398** (a mapped-tuple position over `dyn` does not coerce its elements) →
  `Combine`'s inputs arrive already erased, and its constructor cannot erase them.

(A124's 2026-09-24 stamp attaches B411 to the arity; reading `reactive.vl`, the
`T` parameter is the field rule above and B411 is `Switch`'s fourth parameter.)
The combinators still returned `SignalCell`; the node constructors were exported
`[internal]` (`map_node`, `switch_node`, `combine_node`, `resource_node`,
`Resource::pending`). `.cell()` does not compare (Q3 as recommended), is
owner-tied and a derivation, and **adds no `Shared` site** — it builds on
`SignalCell::new`, so the census moved 140 → 143 by `Switch`, `Distinct` and
`Resource`'s two cells less the S1 probe's, NOT by the `.cell()` count. `dispose`
became `release_under` (the release body given its turn) and the nodes `detach`
context-free; eight goldens moved, runtime-identical. The S1 probe module was
deleted and its four pins re-pointed at the real nodes.

**S2c — PREPARED, not landed** (`sweeps/order41/reactive-41/`: `s2c-flip.patch`
builds on b3fa0a47; `s2c-combine.patch` builds and throws until B398). Nineteen
tests red under it: five on B408 (a blanket method unreachable through an
abstract bound — every generic `s.map(..)` once `map` is a blanket), eight A25
pins, four behaviour pins to re-derive, one diagnostic, and the no-cycle gate
(§2.4's ruling note). The estate census under the flip: std ui/router 0, rpc 4
(the mirrors' own `map`), corpus 4 goldens, examples 9, split 1, Rust-test `.vl`
consts 30 (11 fixed by `.cell()` in the patch), website 0, playground 1
(`client.vl:22`), kolt 17 sites + 6 cascades. Seven defects filed: B408–B412,
B398 confirmed, F37.

**Ruled after the seal (2026-09-25), for Order 42:** B408 first in the solver
lane, B398 for `combine`; A25's owner-strict law moves from the mirrors' `map` to
the SUBSCRIBING LEAF; the no-cycle ruling and A130 (§2.4); `Resource<T>` keeps
its TYPE name and only its constructor respells (`resource` is a keyword — B413
dissolves it, and `contextual-keywords.md` §4.6 says what frees the word).

**Order 42 (reactive-42) — the flip.** ⟦INTEGRATOR: reactive-42 had not reported
when papers-42 closed. Fill from its report: the S2c commit sha; which of B409 /
B410 / B411 retired their workaround (the `Upstream` blanket, the per-node
`on_settle` calls, the phantom `U`) and which remain; the `Resource` constructor's
spelling; `.cell_global()` and the module-level refusal's ledger row; the
`shared_census` number; goldens moved; the A25 pins' re-derivation; kolt's 17 + 6
written out for the owner.⟧
