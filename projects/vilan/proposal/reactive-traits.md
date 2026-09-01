# Reactive traits — `Source` reads, `Signal` writes, `SignalCell` stores (A32, B161, B162)

> **Status: PROPOSED 2026-08-31** (work order 22, cycle 40; tracker items
> [[A32]], [[B161]], [[B162]], with [[B157]], [[B158]] and [[A33]] as the
> composition neighbours). Written to the owner's rulings on A32 (`Signal`
> DOES become a trait; the canonical impl is named `SignalCell`), B162
> (trait-associated functions "should definitely be supported") and B161
> (the semantics stated exactly). This paper elaborates those rulings and
> never contradicts them; the numbered **owner questions** in §13 are the
> owner's.
>
> Every claim about the shipped language was probed against the installed
> `vilan 0.39.0 (2ad39dd09)`. The probes are transcribed in §11 with their
> verdicts — forty-three programs, of which twenty-two compiled and ran
> and twenty-one were refused. Every count was taken mechanically against `vilan`
> @ `2acb3f41`, kolt @ its 0.38.0 migration, the website @ its v0.38.0
> deploy, and the playground.
>
> **Two soundness holes were found on this design's critical path** and are
> reported in §8. Neither is caused by A32; both are load-bearing for it.

## 1. The ask, and the finding that reframes it

The ask (A32, owner, 2026-08-29): custom signal logic — a persisted
signal, a debounced one, a clamped one — implementable while staying
compatible with everything that consumes signals. The motivating shape,
verbatim: *a component takes `Signal<u32>`; the user passes an impl whose
`set` clamps (write 1000, store 800), satisfying the component's bound
with custom write logic.*

A32 already recorded the first reframing: **the read half is shipped.**
`std::reactive`'s `Source<T>` (`reactive.vl` §429) declares `get` and
`sub` and defaults `effect`, and kolt's `StorageSignal<T>` implements it
today.

This paper's probes find a second, larger reframing. **Almost every
mechanism the writable trait needs is already shipped too**, and what is
missing is far smaller than A32 assumed:

| Mechanism the design needs | Shipped on 0.39.0? | Probe |
|---|---|---|
| A trait extending another (`trait Signal<T> with Source<T>`) | **yes**, with upcast and completeness checking | P7b/c/d/e |
| A trait member reached through a bound | yes | P1 |
| A trait function with no `self` (a *static*), declared in a trait | **yes** — it parses and analyzes cleanly | P5a |
| That static implemented per impl, called as `Impl::func(…)` | **yes** | P5d |
| That static called through a bound, `H::func(…)`, dispatching per impl | **yes**, correctly per impl | P5g, P5h |
| A *default body* on such a static, inherited through a bound | **yes** | P14 |
| An impl *overriding* that default, reached through a bound | **yes** | P14 |
| `Trait::func(args)` on the bare trait name | **no** — `cannot find 'new' in Holder` | P5, P5c |
| `Impl::func` reaching a default the impl did not declare | **no** — `cannot find 'spawn' in A` | P14 |
| A trait name as a binding/parameter annotation | no — the trait-is-not-a-type refusal, identical in four positions | P3, P4 |
| A blanket impl over a bound (`impl type S: Trait<…> with Other`) | no — accepted, then ICEs ([[B158]]) | P6b, P12b |

So B162 is not a new feature so much as **two missing lookup paths** on a
resolution machine that is otherwise complete, and B161 is a **narrowing
of one existing diagnostic** plus an inference edge. The design below is
sized accordingly.

The remaining honest gap is the one A32 named: the *consumers*. Every
reactive binding in `browser/ui.vl` takes the concrete struct, so a custom
`Source` cannot feed one (P2: `Expected Signal<i32>, but got Doubler
instead.`) — that is [[A33]], and §9 states what A32 changes about it.

## 2. The trait pair

```vilan,fragment
trait Source<T> {                       // shipped, unchanged
	fun get(self): T;
	[must_use]
	fun sub(self, observer: |T| void): Subscription;
	fun effect(self, observer: |T| void) { … }        // default
}

trait Signal<T> with Source<T> {        // new: the writable half
	fun new(value: T): SignalCell<T> { SignalCell::new(value) }   // B162
	fun set(self, value: T);
	fun notify(self);
	fun set_with(self, transform: sync |T| T) { self.set(transform(self.get())); }
	fun update(self, mutate: sync |&mut T| void) { … }            // see below
}
```

`trait X with Y` is the shipped supertrait grammar (spec §5.5, "`trait X
with Y` makes `Y` a supertrait: implementing `X` requires `Y`"), and the
probes confirm it carries the semantics this design needs: a `<S:
Signal<u32>>` bound reaches `Source`'s members (P7c), an impl of the
sub-trait alone satisfies a super-trait bound (P7e), and an impl that
provides neither half is refused by name (P7d). No new grammar.

### 2.1 Each member, and why it sits where it sits

The shipped `Signal` struct's public surface is `new`, `set`, `notify`,
`set_with`, `update`, `map`, `flatten` (on nested), plus the free
`combine` and `observe`, and the `Slot`/`AttrValue` impls. Member by
member:

- **`new`** — a trait-associated function with a **default body** (B162),
  returning the canonical cell **concretely**: `fun new(value: T):
  SignalCell<T>`. Deliberately *not* `Self`. `Signal::new(1)` is a bare
  qualified path with no receiver and no bound in scope, so a `Self`
  return would have nothing to resolve against; a concrete return is the
  only spelling that keeps today's call sites working. §6 settles the
  resolution rules.
- **`set`** — a **requirement**. This is where the whole feature lives:
  the clamp, the persistence write, the debounce enqueue. No default is
  possible or wanted.
- **`notify`** — a **requirement**. Publishing without changing the value
  is a real operation (`Signal::update` and `Signal::set` share it), and
  no generic body can reach an arbitrary impl's subscriber list. An impl
  that stores elsewhere must say what "publish" means for it; kolt's
  `StorageSignal` already writes this member by hand.
- **`set_with`** — a **default** of exactly the shipped body,
  `self.set(transform(self.get()))`. std's own `set_with` is that line
  and kolt's `StorageSignal::set_with` is that line copied; making it a
  default deletes the copy. Overridable by an impl that can do better.
- **`update(mutate: sync |&mut T| void)`** — the one genuinely hard
  placement. Its value (A18, `signal-update.md`) is *in-place* mutation
  with one notify, and a generic default can only do
  read-copy-mutate-write-back — precisely the copy A18 existed to avoid.
  Recommendation: **declare it on the trait with the read-modify-write
  default**, and let `SignalCell` override with the in-place body. The
  alternative — leave `update` inherent on the cell — locks a component
  bounded on `Signal<List<T>>` out of the one method that collection
  actually wants, which is the exact shape A18 was filed for. The default
  pays a copy and the doc comment must say so. Owner question Q4.
- **`map`** — belongs on **`Source`**, not on `Signal`: a derivation only
  reads. A generic default is mechanically possible — P16 compiles a trait
  default with its own type parameter (`fun derive<U>(self, transform:
  sync |T| U)`) and runs it. But it costs correctness: a default written
  over `sub` runs `transform` **twice** at creation, because `sub` fires
  its observer immediately, whereas std's `map` seeds once through the
  private `observe` (subscribe *without* the first call — the comment at
  `reactive.vl` §465 says exactly this: "a derivation seeds its own first
  value and must not pay for a second `transform`"). Widening `map` needs
  an `observe`-shaped member on `Source` first. Recommendation: **out of
  scope for A32** — leave `map` inherent on the cell and hand the widening
  to A33 with the `observe` question attached. Owner question Q5.
- **`flatten`** — stays on the cell (`impl SignalCell<SignalCell<type U>>`).
  A generic flatten wants `impl type S: Source<type U> …`, and a `type`
  binder inside a *bound* does not resolve today (P12: `cannot find type
  'T'`). §9 treats this as B158's business.
- **`combine`**, **`observe`**, **`optimistic`** — free functions over
  the concrete cell; A33's widening surface, not A32's.

### 2.2 The clamp exhibit

A32 states the exhibit and this paper ran it. Under placeholder trait
names (`Signal` is still the struct on 0.39.0), the exhibit **compiles and
runs today** (P8) — the whole design's dispatch behaviour is already
available; only the spellings are not:

```vilan,fragment
struct Clamped { inner: SignalCell<u32>, max: u32 }

impl Clamped with Source<u32> {
	fun get(self): u32 { self.inner.get() }
	[must_use]
	fun sub(self, observer: |u32| void): Subscription { self.inner.sub(observer) }
}

impl Clamped with Signal<u32> {
	fun set(self, value: u32) {
		let capped = if value > self.max { self.max } else { value };
		self.inner.set(capped);
	}
	fun notify(self) { self.inner.notify(); }
}

// The component. It bounds on the writable trait and knows no impl.
fun width_control<S: Signal<u32>>(width: S) {
	width.set(1000u32);
	print("component read back: " + width.get().to_string());
}

width_control(SignalCell::new(0u32));            // component read back: 1000
let clamped = Clamped::new(0u32, 800u32);
width_control(clamped);                          // component read back: 800
print("owner sees: " + clamped.get().to_string()); // owner sees: 800
```

P8's actual output, verbatim:

```
component read back: 1000
component read back: 800
owner sees: 800
observer: 0
observer: 800
```

**The semantics this pins**, matching A32's ruling: after `set(1000)`,
`get` reads `800` — the setter's caller, the component and every observer
all see the transformed value, because there is only one value and the
impl decided it. Equality and no-op-notify ride the impl: `SignalCell`
notifies unconditionally (as it does today — `set` never compares), and an
impl that wants "don't publish an unchanged value" writes that in its own
`set`. The trait promises **nothing** about notification frequency, and
the guide must say so.

The last two lines of the transcript are the observer half: a subscriber
attached to the clamped impl saw `0` then `800`, never `1000`. The
transform is not a view — it is the store.

## 3. `SignalCell` — the canonical cell

Take the owner's name. `SignalCell` is honest (it is a cell), it is
self-documenting next to a `Signal` that is now a contract, and it is
nearly invisible in daily code because `Signal::new` remains the everyday
spelling. `Cell` alone is too generic and Rust-laden; `State` and `Atom`
are framework-flavoured. This paper found no better candidate and
recommends it be taken as ruled.

What moves in std:

- `struct Signal<T>` → `struct SignalCell<T>` (1 site).
- `impl Signal<type T> with Source<T>`, `impl Signal<type T>`, `impl
  Signal<Signal<type U>>`, and the four `impl Signal<str> with
  Slot`/`with AttrValue` heads in `browser/ui.vl` and `process/ui.vl` →
  `SignalCell` (7 sites).
- The one struct literal `Signal { value = …, subscribers = … }` (1 site).
- Every std *field* and *return* typed `Signal<T>` (§5).
- `Signal::new` **does not move** (B162) — 97 call sites in `.vl` across
  the estate and 27 more in docs prose stay exactly as written.

## 4. The name is compiler-privileged — the census's sharpest finding

`Signal` is not an ordinary std struct. The compiler recognises it **by
string** in three places, and std's own macro layer in a fourth:

1. **HMR transfer classification.** `crates/vilan-core/src/analyzer.rs`
   §37700 resolves `std::reactive`'s scope entry literally named
   `"Signal"` into `primitive_struct_ids` at bootstrap, and
   `hmr_transfer_form` (§6216) and the transferability walk (§6297) key
   off that id: a `Signal<T>` *binding* carries its payload across a hot
   swap (`hmr.md` §4), a bare `Signal` *component* is excluded. The source
   comment says "`Signal` is otherwise recognized only syntactically, so
   its id is captured nowhere else."
2. **`[expose]` field checking.** `check_expose_fields` (§11679) matches
   the field's **written type node** — `Node::AccessorWithGenerics(
   "Signal", arguments)` — to find the element type it must check is a
   wire type.
3. **`[service]` surface generation** (§34705) does the same syntactic
   match to render each exposed field's element.
4. **std's own `service` macro**, `std/src/rpc.vl` §1716:
   `if field.type_.name == "Signal" && field.type_.arguments.len() == 1`.

Consequences the migration must carry:

- (1) is a one-line rename to `"SignalCell"`, and it is the *right*
  target: HMR's transfer rule is about the cell's representation, not
  about the contract.
- (2), (3) and (4) match on **what the user wrote in a struct field's
  annotation**. Under B161 a field annotation may not name a trait (§7),
  so every `[expose]` field is spelled `SignalCell<T>` and the rename is
  again mechanical. But the syntactic match is a real ceiling: a custom
  `Source` — kolt's `StorageSignal`, a `RemoteSource` — can never be
  `[expose]`d, and neither can a field written through a type alias. A32
  does not fix that and should not pretend to. Owner question Q7.

## 5. The breaking census

Mechanical, over `.vl` sources, counting the token `Signal` in the
`std::reactive` sense (the corpus's unrelated `enum Signal` in
`test/match-patterns.vl` — 18 occurrences — and the `*Signal`-suffixed
names are excluded throughout). Classified by syntactic position, because
position is exactly what decides an occurrence's fate:

| Position | std | corpus | examples | bench | kolt | website | playground | **total** | Fate |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `struct Signal<T>` declaration | 1 | – | – | – | – | – | – | **1** | renames |
| `impl Signal…` heads | 7 | – | – | – | – | – | – | **7** | renames |
| struct literal `Signal { … }` | 1 | – | – | – | – | – | – | **1** | renames |
| `Signal::new(…)` | 15 | 20 | 19 | 2 | 20 | 18 | 3 | **97** | **unchanged** |
| return type | 15 | 1 | – | – | 1 | – | – | **17** | **must become `SignalCell`** |
| struct field | 6 | – | 3 | 1 | 9 | – | 1 | **20** | **must become `SignalCell`** |
| parameter | 26 | 1 | 21 | – | 9 | 11 | 1 | **69** | **may stay `Signal`** (anonymous bound, §7) |
| `let`/`mut` annotation | 7 | 2 | 7 | 1 | 2 | 4 | – | **23** | **may stay `Signal`** (the constraint, §7) |
| `import` line | 2 | 8 | 10 | 2 | 10 | 9 | 2 | **43** | may need both names |

Occurrences, not lines: a line like `let gated: Signal<T> =
Signal::new(source.get());` (`browser/ui.vl` §478) contributes to both the
annotation row and the constructor row.

Outside `.vl` source:

- **Compiler (Rust):** 565 `Signal` tokens across 34 files — 73 in
  `crates/*/src`, **492 in `crates/*/tests`** (inference fixtures,
  formatter snapshots, CLI integration tests). This is the single largest
  bucket in the estate and is almost entirely fixture text.
- **Docs:** 161 tokens across 22 `.md` files under `vilan/docs`, of which
  27 lines carry `Signal::new` (unchanged) and 78 lines carry `Signal<`
  (each needs reading for position). `spec/types.md` §5.4's own example
  `impl Signal<Signal<type U>> { … }` is among them; §5.5's
  trait-is-not-a-type paragraph must be amended by B161 regardless.
- **Website:** two occurrences are *drawings of code* in
  `src/art.vl` (`"] entries: Signal<List<Note>>,"` as a string literal in
  an SVG-ish diagram, and `Signal<i32> ` in a dataflow node label) — they
  break nothing but are wrong on the page the day this ships, and the
  website is in the breaking census by standing rule.
- **A stale kolt worktree** (`kolt/worktrees/connection-v3`) carries 2 more
  field sites; not counted above.

### 5.1 Is the rename breaking for user code?

**Yes, in exactly two positions, at 16 sites outside std.** A field and a
return type need a real type, so B161 leaves them refused for a trait
name; every such annotation must be rewritten to `SignalCell<…>`:

- struct fields outside std: **14** — kolt 9 (`Prefs` ×4, `StorageSignal`
  ×1, `AppContext` ×2, `Store` ×2), examples 3 (all `[expose]`),
  benchmarks 1, playground 1 (`[expose]`);
- return types outside std: **2** — kolt's `get_route()`, and the corpus's
  `gather` in `spread-parameters.vl`.

Everywhere else, user code is **source-compatible**: 97 `Signal::new`
calls unchanged, 69 parameter annotations unchanged (and silently
widened), 23 `let`/`mut` annotations unchanged (and silently narrowed to
constraints), imports unchanged unless a file needs the cell by name.

That is a small breaking surface for a rename of this reach, and the
reason is entirely B161. The estate holds **129 annotation sites** naming
`Signal` as a type (20 fields, 17 returns, 69 parameters, 23 bindings).
Without B161 every one of them must be rewritten to `SignalCell` — **75
of them outside std**. With B161 only fields and returns must move: **37
sites, 16 of them outside std**. **B161 is not a companion convenience;
it is what makes A32 affordable.**

One further compatibility note: `<V: Signal<i32>>` — a *struct* used as a
generic bound — is accepted at the bound today and fails only at the first
member call (`cannot call method 'get' on V`, P11). So nobody in the
estate can have written a working `Signal` bound, and the spelling starts
working under A32 with no collision. (That the bound position accepts a
struct at all is a separate diagnostic gap, noted in §8.3.)

## 6. B162 — trait-associated functions

### 6.1 What is already true

The probes reduce B162 to a small, precise job. On 0.39.0:

- A trait declaring `fun new(v: i32): Cell { Cell::make(v) }` — no `self`,
  with a body — **compiles cleanly** (P5a). The grammar admits it now.
- A **body-less** trait static (`fun spawn(v: i32): Cell;`) is admitted,
  is enforced by the completeness check with a clean diagnostic when an
  impl omits it (P5e — *"'Cell' does not implement trait 'Holder': missing
  'spawn'; declare `fun spawn(v: i32): Cell`"*), is callable as
  `Impl::spawn(…)` (P5d), and is callable **through a bound** —
  `fun build<H: Holder>(seed: H) { H::spawn(3) }` — dispatching correctly
  per impl (P5g, and P5h: two impls, `3` and `300`).
- A **defaulted** static is inherited through a bound by an impl that
  does not declare it, and **overridden** through a bound by one that
  does (P14: `3`, then `30`).

So "body-less requirements admitted or deferred" is settled by
observation: **they are already admitted and already work.** B162 need not
decide it — only preserve it.

### 6.2 What is missing

Two lookup paths, both reported today as `cannot find '<name>' in <X>`:

1. `Trait::func(args)` — the bare trait name as a path head (P5, P5c).
2. `Impl::func(args)` where the impl **inherited** the default and did not
   declare it (P14: `A::spawn` not found, though `B::spawn` — the
   overrider — resolves, and `through(A)` reaches the default fine).

### 6.3 The recommendation

**`Trait::func(args)` resolves statically to the trait's default body.**
There is no receiver, so there is nothing to dispatch on; the default is
the only answer. This is not a new category — spec §5.5 already blesses
"the head of a qualified path (`Display::show(x)`)" as a position where a
trait's name stays legal, and P13 shows the receiver-bearing form working
today and correctly picking an impl's override. `Trait::func` is that rule
with the receiver removed, which removes the dispatch with it.

**Impls may override — and the override is unreachable at `Trait::`.**
Override is already shipped (P14) and removing it would be a regression.
The rule is one sentence: an override is reached at `Impl::func`, and
through a bound at `T::func`; `Trait::func` always means the default.
The exhibit needs no override, and this is why it does not want one:
`Signal::new(1)` must mean "the canonical cell", always, in every file,
with no context-dependence. A design where `Signal::new` could mean
something else depending on an in-scope bound would be a footgun with no
compensating use.

**Fix the `Impl::func` asymmetry.** `A::spawn` should reach the inherited
default, exactly as `a.hello()` reaches an inherited default method today
(P13). The current "cannot find" is an inconsistency, not a decision.

**The day-one refusal.** `Trait::func` for a **body-less** requirement
must be a named compile error, never today's accept-then-ICE (B158's
cousin, reproduced in §9.1). Recommended wording, in the house shape:

```
'spawn' is a requirement of trait 'Holder' with no default body, so
`Holder::spawn` has no implementation to call — a static has no receiver to
select one from. Call it on a type that implements the trait
(`Cell::spawn(…)`), or through a bound (`fun f<H: Holder>() { H::spawn(…) }`).
```

anchored at the call, with a secondary span at the trait's declaration
("declared here, with no body") in the same style as P5e's and P3's
two-span diagnostics.

**Not covered, by promise:** associated *constants* on types (`i32::MAX`'s
stopgap). A sibling in the eventual static-member design; B162 delivers
functions on traits only.

## 7. B161 — a trait annotation as a checked constraint

### 7.1 The semantics, as ruled

A trait written as a binding's annotation is **not a type and not a
`dyn`** — it is a **constraint** on the inferred value type. `count`'s
type is still the impl's:

```vilan,fragment
let count: Signal<i32> = SignalCell::new(1);   // count : SignalCell<i32>
```

The annotation does two things: (a) it **checks** that the inferred type
implements the trait, and (b) it **feeds inference** — `Signal<i32>`
supplies `T = i32` to the initializer. Two branches must still unify to
**one concrete type by ordinary inference, before the trait is
consulted**:

```vilan,fragment
let s: Signal<i32> = if c { SignalCell::new(1) } else { SignalCell::new(2) };  // legal
let s: Signal<i32> = if c { SignalCell::new(1) } else { OtherSignal::new(2) }; // ILLEGAL:
                              // ordinary branch mismatch, never a trait error
```

This is the bounded-generic rule ported to bindings: one concrete type per
binding, checked wide, kept narrow.

**Implementation mandate:** §8.1 reports that `if`-expression arms are
**not unified at all** on 0.39.0 — the illegal line above is *accepted*
today, taking the first arm's type. B161's stated rule therefore cannot be
delivered until that hole is closed. The fix is not B161's feature work;
it is a prerequisite, and B161 must not ship on top of it.

### 7.2 The positions, each ruled

Spec §5.5 today: *"That rule is enforced at the annotation, in every value
position — a binding, a parameter, a return type, a field, a generic
argument (`List<Display>`) — and reported where the trait's name is
written."* Probes confirm it, in four positions, with **byte-identical
wording** (P3, P4):

> `'Source' is a trait, not a type: a trait is not a value type (vilan has
> no trait objects), so no value can have this type. Declare a generic
> parameter bounded by the trait instead — `<T: Source>` — and write 'T'
> here.`

B161 **narrows** this, position by position:

| Position | Fate | Why |
|---|---|---|
| `let` / `mut` binding | **becomes the checked constraint** | The ruled semantics. |
| **parameter** | **becomes an anonymous bound** — `fun f(v: Signal<i32>)` is `fun f<V: Signal<i32>>(v: V)` | Recommended: **admit.** See §7.3. |
| **return type** | **stays refused**, with a new steer | A return type must be a real type; the callee picks it, so there is no inference direction to run and nothing for a constraint to constrain. |
| **struct field** | **stays refused**, with a new steer | A field needs a real type. Storable trait values without `dyn` is B157's recorded residual, not this feature. |
| **generic argument** (`List<Signal<i32>>`) | **stays refused**, with a new steer | A homogeneous collection of an *anonymous* bound is not a thing; the caller means either `List<SignalCell<i32>>` or a generic parameter. |

The diagnostic keeps **one error identity** and gains **position-aware
steers** — today's single text is position-blind, which is exactly what
must change:

- at a **return**: *"…a return type must name a concrete type. Write the
  implementation's name (`SignalCell<i32>`), or make the function generic
  and let the caller choose (`fun f<S: Signal<i32>>(…): S`)."*
- at a **field**: *"…a struct field must name a concrete type. Write the
  implementation's name (`SignalCell<i32>`), or make the struct generic
  over it (`struct Holder<S: Signal<i32>> { inner: S }`)."*
- at a **generic argument**: *"…write the implementation's name, or make
  the enclosing declaration generic."*

This is a narrowing, not a repeal: the trait-is-not-a-type rule still
holds everywhere a value's storage is being named, and `let x: Display =
bag;` remains an error only because `bag` — well typed — must still *be*
something; under B161 it becomes a **constraint failure** if `Bag` does
not implement `Display`, and legal if it does. That is the intended
change, and §13 Q8 asks whether the owner wants it for *every* trait or
only where it is opted into.

### 7.3 Weighing the parameter position

**For:**

- It is what makes A32 affordable: **69 of the estate's 129 annotation
  sites are parameters** (§5), and parameters plus bindings are 92 of the
  129. Admitting the position is most of the difference between a 129-site
  migration and a 37-site one.
- The desugaring is *exactly* the spelling the language already has
  (`fun f<V: Signal<i32>>(v: V)`), so there is no new semantics to
  specify — only a surface.
- It makes A33's widening a **rename with no signature churn**: every
  `bind_text(source: Signal<str>)` becomes `bind_text(source:
  Source<str>)` and is thereby generic, with no `<V: …>` lists spreading
  through `ui.vl`.
- It never breaks a caller. The anonymous bound is strictly *more*
  permissive than the concrete parameter it replaces.

**Against, honestly:**

- It makes a function **silently generic**, which changes its emission
  shape. A33 already carries a green negative — "the emission must stay
  byte-identical for existing `Signal` callers" — and this feature is how
  that negative gets tested. If monomorphization is not free here, the
  cost lands on every `ui.vl` binding.
- It hides arity: a reader cannot tell from `fun f(a: Signal<i32>, b:
  Signal<i32>)` that the function has two type parameters.
- The two parameters are **independent**. `fun swap(a: Signal<i32>, b:
  Signal<i32>)` under the sugar accepts a `SignalCell` and a `Clamped`;
  the concrete spelling it replaces did not. This is *more* permissive, so
  no call breaks — but a function that genuinely needs both arguments to
  be the same type must say so with an explicit generic, and the guide
  must show that.

**Recommendation: admit it**, with (b) and (c) written into the guide
section and (a) carried as a measured pin in whatever lane builds it.

### 7.4 The inference-direction benefit: the annotation as a typed hole

The second half of the ruling — the annotation *feeds* inference — is a
real ergonomic gain and is already how concrete annotations behave. P15
compiles both halves of:

```vilan,fragment
let empty: Signal<List<i32>> = Signal::new([]);   // the annotation supplies the element type
```

Under B161 the trait annotation does the same work without pinning the
impl: `let count: Signal<i32> = SignalCell::new(1)` gives `T = i32` to the
initializer while leaving `count : SignalCell<i32>`. That is a typed hole
— the programmer states the *contract* they want and lets inference find
the *representation* — and it is the single most useful thing the feature
does beyond the migration it enables.

## 8. Two soundness holes on this design's critical path

Found by this lane's probes on the shipped 0.39.0 compiler. Neither is
caused by A32; both sit directly under it, and both should be filed.

### 8.1 `if`-expression arms are not unified — and the mismatch escapes

`match` legs **are** checked (P10f: *"match legs have mismatched types:
expected i32, but got str instead."*). `if`/`else` arms are **not**:

```vilan,fragment
fun main() {
	let c = false;
	let mixed = if c { 1 } else { "two" };
	print(mixed + 1);
}
```

compiles and prints `two1` (P10e). The binding's static type is taken from
the **first arm**, and the other arm's value flows out unchecked. It
escapes through a declared return type as well (P10g):

```vilan,fragment
fun pick(c: bool): i32 { if c { 1 } else { "two" } }
fun main() { print(pick(false)); }        // prints: two
```

and through a concrete annotation (P10c): `let mixed: Signal<i32> = if c {
Signal::new(1) } else { Other::new(2) };` is accepted.

This is **the rule B161's ruled semantics rest on**. B161 says the illegal
branch pair "fails at branch unification with the ordinary mismatch, never
a trait error" — today it does not fail at all. B161 cannot be built as
ruled until this is fixed; the fix belongs to the type checker, not to
B161. **Recommend filing as a bug, high severity** (it is a plain
soundness hole in a core expression form, independent of every feature in
this paper).

### 8.2 A supertrait's type argument is not substituted through a sub-trait bound

With `trait Sig<T> with Src<T>`, a function bounded on the **sub**-trait
sees the **super**-trait's members with their parameter *unsubstituted*:

```vilan,fragment
fun bad<S: Sig<u32>>(s: S): str { s.get() }   // accepted; returns a u32
fun main() { print(bad(C { v = 7 }) + "!"); } // prints: 7!
```

(P9d.) The leaked `T` behaves as a wildcard that unifies with anything.
Calling a method on the result fails instead, with a confusing message —
`cannot call method 'to_string' on T` (P9c) — which is how the hole
surfaces in practice.

The boundary is precise, and it is *only* the supertrait path:

- the sub-trait's **own** members substitute correctly (P9e: `Expected
  u32, but got str instead.`);
- a bound on the super-trait **directly** substitutes correctly (P9c's
  `via_super`, and P9f against std's own `Source<u32>`: `Expected str, but
  got u32 instead.`).

std is not exposed today because `Source` has no sub-trait. **`trait
Signal<T> with Source<T>` is the first one**, and the exhibit's own
`width.get()` walks straight into it — P8 needed `let seen: u32 =
width.get();` to pin the type before it could call `to_string`.
**Recommend filing as a bug; A32 is blocked on it.**

### 8.3 Two smaller diagnostic gaps, noted in passing

- A **struct** used as a generic bound (`<V: Signal<i32>>`) is accepted at
  the bound and fails only at the first member call, with `cannot call
  method 'get' on V` (P11). The bound position should refuse a non-trait
  by name. (Harmless for A32 — it is why no estate code can have a
  `Signal` bound — but it is a poor error.)
- `own` is a reserved word: `fun own<…>(…)` fails with `found 'fun'
  expected an expression`, which does not say so.

## 9. Composition — B157, B158, A33

### 9.1 B158 is A32's hardest dependency, and A32 raises its stakes

Today `impl Signal<str> with Slot` and `impl Signal<str> with AttrValue`
(in both `browser/ui.vl` and `process/ui.vl`) are what make a signal
usable in element syntax — `<div>{name_signal}</div>`. Under A32 they
become `impl SignalCell<str> with …`, which **narrows** element syntax to
the canonical cell: a `Clamped`, a `StorageSignal`, a `RemoteSource` would
not be a `Slot`. The fix is a blanket over a bound —

```vilan,fragment
impl type S: Source<str> with Slot { … }
```

— and that is [[B158]], which is **ruled to be supported with the
specificity rule** but is not built: the form parses, is accepted at
declaration, and ICEs at the first dispatch, reproduced verbatim on 0.39.0
(P6b, P12b):

```
internal: a call resolved to `MaybeSignal`'s requirement `peek`, which has
no body — emitting it would produce an empty function and a runtime
`TypeError`. The receiver's type could not be resolved to a concrete
implementation at this call; please report this program
```

So **A32 without B158 is a narrowing of element syntax**, and that is the
strongest argument for building them in one arc.

**A gap B158's builder must also close.** Only the *monomorphic* bounded
blanket is spellable. A binder inside a bound does not resolve:

```vilan,fragment
impl type S: Src<type T> with Maybe<T> { … }   // cannot find type 'T'   (P12)
impl type S: Src<i32> with Maybe<i32> { … }    // parses, then ICEs      (P12b)
```

B157's whole point — `impl S with MaybeSignal<T>` over `S: Signal<T>`,
generic in `T` — needs the first form. The spec (§5.4) says the subject
pattern's `type X: Bounds` binders declare the impl's generics; a binder
appearing inside a *bound* is outside that sentence. **Recommend: B158's
lane extends the binder scope to bounds, and says so in the spec section
it is already chartered to write.** Owner question Q9.

### 9.2 B157's `MaybeSignal` over trait-`Signal`

Once B158 lands, B157's family is:

```vilan,fragment
trait MaybeSignal<T> { fun bind(self, react: |T| void); }
impl type T with MaybeSignal<T>             { fun bind(self, react: |T| void) { react(self); } }
impl type S: Source<type T> with MaybeSignal<T> { fun bind(self, react: |T| void) { self.effect(react); } }
```

The second impl is the change A32 makes: today B157 writes `impl
Signal<type T> with MaybeSignal<T>` against the struct, which admits only
the cell; over the *trait* it admits every custom source, which is exactly
B157's stated goal ("one family of bounds, not three"). Coherence is
unchanged and remains sound by B158's specificity rule — the blanket is
the least-specific tier and a bounded impl outranks it wherever both
match. The `not Signal` negative bound B158 already refused stays refused,
and A32 strengthens the reason: under trait-`Signal`, "is it a signal?" is
an *open* question that any user impl can newly answer `yes` to, so a
negative bound would make adding an impl a breaking change in user code as
well as in std.

### 9.3 A33's write-back pair, and a correction

A33 says to widen the read-only bindings to `Source` and leave the
write-back pair — `bind_value`, `bind_draft` — concrete "until A32's
write-side ruling". This paper supplies the ruling: **the write-back
consumers bound on trait-`Signal`.**

`browser/ui.vl` has 13 concrete-`Signal` parameter sites and
`process/ui.vl` mirrors 10 of them. Under A32 they split:

- **read-only → `Source<…>`**: `style_var`, `bind_text`, `bind_class`,
  `bind_styled`, `bind_attr`, `bind_each`, `when`, `show`,
  `chunk_preload`, and the two internal `source:` parameters at
  `ui.vl` §405/§475;
- **write-back → `Signal<…>`**: `bind_value` and the internal
  `write_back_value`;
- **`optimistic` / `Optimistic::over(signal: Signal<T>)`** — a *writer*
  (it sets the value back on confirm/reject), so it bounds on
  trait-`Signal` too. A33's audit does not list it; it should.

**A correction to A33 as filed:** `bind_draft` does **not** take a
`Signal` — its parameter is `Draft<str>` (`browser/ui.vl` §267,
`process/ui.vl` §215), a struct built over two cells. It is therefore not
part of the write-back *pair*; whether `Draft` should itself become a
trait, or stay a concrete type over trait-`Signal` internals, is a
separate question (Q6). The write-back set A32 rules on is
`bind_value` + `write_back_value` + `Optimistic::over`.

## 10. Migration

The order matters, because two of the steps are blocked on §8.

1. **Fix §8.1 (`if`-arm unification) and §8.2 (supertrait substitution).**
   Prerequisites, not features. B161 as ruled and the exhibit as written
   both depend on them.
2. **B162's two lookup paths** + the body-less refusal (§6.3). Nothing
   else in this paper works without `Signal::new` surviving.
3. **B161's `let` and parameter positions** + the position-aware steers +
   the spec §5.5 amendment. This is what makes step 4 a 37-site change
   instead of a 129-site one.
4. **The rename**, in one commit per repo: `struct`/`impl`/literal (9
   sites), std's 21 field-and-return sites, the compiler's 4 name-keyed
   sites (§4), and the 16 breaking user sites (§5.1). `Signal::new` is not
   touched.
5. **The trait declaration** (`trait Signal<T> with Source<T>`) and
   `impl SignalCell<type T> with Signal<T>`.
6. **B158**, then the `Slot`/`AttrValue` blankets (§9.1) — without which
   the rename narrows element syntax.
7. **A33's widening** — now a rename, not a signature rewrite (§7.3).
8. **Docs and the website**: 22 doc files, `spec/types.md` §5.4's example
   and §5.5's paragraph, and the website's two code-drawings (§5).
9. **The corpus's 492 Rust fixture tokens**, mechanically.

The compiler's `crates/*/tests` fixtures (§5) dominate the diff line count
and dominate nothing else; they should land in their own commit so the
semantic change stays reviewable.

## 11. Probe ledger

Forty-three programs against `vilan 0.39.0 (2ad39dd09)`. **Twenty-two
compiled and ran; twenty-one were refused.** Sources are in the lane
scratchpad.

**Compiled and ran (19).**

| # | What it shows | Output |
|---|---|---|
| P1 | A custom `Source` impl and std's `Signal` both satisfy `<S: Source<i32>>` | `value = 21` / `value = 1` |
| P5a | A trait carrying a no-`self`, default-bodied static compiles cleanly | `7` |
| P5d | A body-less trait static is callable as `Impl::func` | `7` |
| P5g | …and through a bound, `H::spawn(3)` | `3` |
| P5h | …dispatching correctly per impl, two impls | `3`, `300` |
| P7b | `trait Extended with Base` parses and runs | `1` |
| P7c | A sub-trait bound reaches the super-trait's members | `5` |
| P7e | An impl of the sub-trait alone satisfies a super-trait bound | `9` |
| P8 | **The clamp exhibit** — component, custom impl, observers | `1000` / `800` / `800` / `0` / `800` |
| P9 | Sub-trait bound, super-trait method returned directly | `1`, `2` |
| P9b | …with a generic impl in scope too | `2`, `3` |
| P9d | **§8.2 soundness hole**: `fun bad<S: Sig<u32>>(s: S): str { s.get() }` | `7!` |
| P10 | Mixed-type `if` arms accepted (unused) | `1`, `unreachable` |
| P10b | …and used | `1` |
| P10c | …under a concrete annotation naming one arm's type | `1` |
| P10d | Primitive mismatch across `if` arms, accepted | `1` |
| P10e | **§8.1 soundness hole**: `if c { 1 } else { "two" }`, then `+ 1` | `two1` |
| P10g | …escaping through a declared `: i32` return | `two` |
| P13 | Impls override trait *method* defaults; `Trait::method(recv)` picks the override | `HI p` / `hello q` / `HI p` |
| P14 | Static defaults inherited **and** overridden through a bound | `3`, `30`, `50` |
| P15 | A concrete annotation as a typed hole | `0`, `0` |
| P16 | A generic trait default (`fun derive<U>`) over `sub` | `6` |

**Refused (12).**

| # | What it shows | Diagnostic (head) |
|---|---|---|
| P2 | **A33's gap**: a custom `Source` cannot feed a concrete-`Signal` consumer | `Expected Signal<i32>, but got Doubler instead.` |
| P3 | Trait-is-not-a-type at a **`let`** | `'Source' is a trait, not a type…` |
| P4 | …identical wording at **parameter**, **return**, **field** | same text, three positions |
| P5 | `Trait::func` for a **defaulted** static | `cannot find 'new' in Holder` |
| P5b | The default is not inherited as an inherent static | `cannot find 'new' in Cell` |
| P5c | `Trait::func` for a **body-less** requirement | `cannot find 'spawn' in Holder` |
| P5e | An impl omitting a body-less static | `'Cell' does not implement trait 'Holder': missing 'spawn'…` |
| P5f | No turbofish spelling (`build::<Cell>()`) | `found '::' expected ',' or ')'` |
| P6 | The blanket path, first attempt (context coverage, not the ICE) | *context `owner_scope` is read here, but this code can be reached without an enclosing `run`* |
| P6b | **B158's ICE**, bare blanket | *internal: a call resolved to `MaybeSignal`'s requirement `peek`, which has no body…* |
| P7 | `trait Extended: Base` is not the grammar | `found 'trait' expected an expression` |
| P9c | §8.2 surfacing as a bad message | `cannot call method 'to_string' on T` |
| P9e | The sub-trait's own member substitutes correctly (control) | `Expected u32, but got str instead.` |
| P9f | A non-supertrait bound substitutes correctly (control) | `Expected str, but got u32 instead.` |
| P10f | `match` legs **are** unified (the control for §8.1) | `match legs have mismatched types: expected i32, but got str instead.` |
| P11 | A struct as a bound fails only at the member call | `cannot call method 'get' on V` |
| P12 | A `type` binder inside a bound does not resolve | `cannot find type 'T'` |
| P12b | The monomorphic bounded blanket ICEs | B158's internal error |

## 12. Determinations

1. **Take `SignalCell`.** No better candidate was found; `Signal::new`
   keeps the everyday spelling invisible.
2. **`trait Signal<T> with Source<T>`** — shipped supertrait grammar, no
   new syntax (§2, P7b–e).
3. **Trait membership**: `new` (default static, concrete `SignalCell<T>`
   return), `set` and `notify` required, `set_with` defaulted, `update`
   defaulted with a documented copy; `map`/`flatten`/`combine` stay on the
   cell for now (§2.1).
4. **B162 = two lookup paths**, not a new feature (§6.2). `Trait::func`
   resolves statically to the default; overrides stay reachable at
   `Impl::func` and through bounds; body-less requirements are already
   admitted and stay; `Trait::func` on a body-less requirement is a named
   refusal from day one.
5. **B161 admits the `let` and parameter positions**; return, field and
   generic-argument stay refused with position-aware steers; the
   trait-is-not-a-type diagnostic keeps one identity and gains three
   steers; spec §5.5's position list is amended (§7.2).
6. **B161 is A32's affordability**: it turns a 91-site migration into a
   16-site one (§5.1).
7. **Two soundness holes must be fixed first** — `if`-arm unification
   (§8.1) and supertrait substitution (§8.2). Both should be filed as
   bugs; A32 and B161 are blocked on them respectively.
8. **B158 belongs in the same arc**: without the blanket-over-a-bound,
   A32 narrows element syntax to the canonical cell (§9.1). Its lane must
   also make binders resolve inside bounds.
9. **The compiler privileges the name `Signal`** in three places plus one
   std macro; the rename is mechanical there but exposes a real ceiling on
   `[expose]` (§4).
10. **A33 correction**: `bind_draft` takes `Draft<str>`, not a `Signal`;
    the write-back set is `bind_value`, `write_back_value`, and
    `Optimistic::over` (§9.3).

## 13. Owner questions

1. **`SignalCell` — confirmed?** The paper recommends taking the name as
   proposed. Nothing better surfaced, and the everyday spelling
   (`Signal::new`) is unchanged. Any objection to it being the name that
   lands in std, the spec, the docs and the website in one cycle?

2. **`Trait::func` resolves to the default body, always — agreed?** With
   no receiver there is nothing to dispatch on, so `Signal::new(1)` means
   the canonical cell in every file regardless of what bounds are in
   scope. Impls may still override, reachable at `SignalCell::new` and
   through a bound (`H::new`). Do you want the override reachable at
   `Signal::new` under any circumstance?

3. **Should `Impl::func` reach an inherited default?** Today `A::spawn`
   is "cannot find" when `A` does not declare it, though the same default
   is reachable through a bound and an inherited *method* is reachable on
   a value. The paper calls this an inconsistency and recommends fixing
   it. Confirm?

4. **`update` on the trait, with a copying default?** Declaring it gives
   every impl an `update` (so a component bounded on `Signal<List<T>>` can
   use it) at the cost of a default that does read-copy-mutate-write-back
   — the copy A18 existed to avoid — with `SignalCell` overriding
   in-place. The alternative is to leave `update` inherent on the cell and
   lock generic consumers out. Which?

5. **`map` on `Source` — now, or with A33?** A generic default is
   mechanically possible (probed) but runs `transform` twice at creation,
   because `sub` fires immediately while std's `map` seeds through the
   private `observe`. Widening it properly needs an `observe`-shaped
   member on `Source` (a `sub` without the first call). Do that in A32, or
   hand `Source::map` + the `observe` member to A33?

6. **What happens to `Draft` and `Optimistic`?** `bind_draft` takes
   `Draft<str>`, not a `Signal`, so it is not part of the write-back pair
   as A33 filed it. Should `Draft` become a trait too, stay a concrete
   struct built over trait-`Signal` internals, or stay exactly as it is?

7. **`[expose]` matches the field's spelling syntactically.** The
   compiler (analyzer.rs §11679, §34705) and std's `service` macro
   (`rpc.vl` §1716) look for the literal type name `Signal`, so a custom
   `Source` — kolt's `StorageSignal`, a `RemoteSource` — can never be
   `[expose]`d, and neither can a field written through an alias. A32
   renames the string and changes nothing else. Accept that ceiling, or
   file the widening as its own item?

8. **B161: every trait, or opted-in?** As ruled, *any* trait name in a
   `let` or parameter position becomes a constraint — so `let x: Display =
   bag;` stops being an error and starts being a check. That is a large
   surface for a feature motivated by one pair. Do you want it universal,
   or restricted (an attribute, or only traits with a `Self`-free
   constructor)?

9. **Binders inside bounds** (`impl type S: Source<type T> with
   MaybeSignal<T>`) do not resolve today, which blocks B157's generic
   blanket. Should B158's lane extend binder scope into bounds and write
   it into the spec section it is already chartered for, or is that its
   own item?

10. **The two soundness holes** (§8.1 `if`-arm unification, §8.2
    supertrait substitution) were found by this lane and are not filed.
    They are prerequisites for B161-as-ruled and for A32's exhibit
    respectively. Should they be filed as ordinary bugs on the vilan
    tracker, or carried as gates on this arc?

11. **The parameter sugar makes functions silently generic**, which puts
    A33's "emission stays byte-identical" green negative under real
    pressure across 26 std parameter sites. Is a measured emission pin the
    right gate, or do you want the sugar held until A33 has measured the
    monomorphization cost?

## 14. As built — Order 23, reactive-replumb (2026-08-31)

The arc shipped whole (vilan `b3b492ae`/`f11494d8`/`09ab5713`/`4a58b706`
plus traits-core's `5ee496da`). Where the build diverged from the paper,
the build is the record:

1. **§7.3 did NOT ship.** B161 admits the trait-as-constraint reading at
   the `let` position ONLY — parameter, return, field and every nested
   spelling still refuse. §5's census arithmetic ("37 sites, 16 outside
   std") rested on the parameter sugar; the real breaking surface was
   173 estate occurrences, every parameter site moved to `SignalCell`
   or an explicit bound. The parameter sugar remains unbuilt and
   unruled (question 11 stands).
2. **§2.1's `update` recommendation was OVERRULED** — the owner locked
   `update` out of the trait; it is inherent to `SignalCell` alone,
   pinned both ways. §12.3's contrary determination is void.
3. **§9.2 shipped as `impl type S: Source<type T> with MaybeSignal<T>`**
   — `bind` only reads, so `Source` is the right bound; a component
   that writes back asks for `Signal<T>` directly.
4. **§9.3's `Optimistic::over` is not buildable as written**: the type
   STORES its signal in a field, and a field must name a real type —
   widening means an `Optimistic<T, S>` arity change at every use. The
   free `optimistic` fn was widened to `<T, E, S: Signal<T>>`; the type
   awaits a determination (recorded in std's doc comment).
5. **§4/Q7's `[expose]` ceiling is removed at the CHECK only** — it
   reconciles against nominal `std::Source` per the ruling. `[service]`
   client generation runs at macro time before types resolve, so it
   still reads the element off the field's sole type argument; a source
   whose element is not its one type argument renders `_` and errors at
   the generated site. Standing residual.
6. **§8's two holes were closed before this lane ran** (Order 22:
   B163 if-arm unification, B164 supertrait substitution).
7. **Signal::new's default body emits a one-hop trampoline** per
   program (trait body → SignalCell::new), visible in corpus goldens.
   Priced: cheap, recorded as a consequence of the Trait::func ruling.
8. **Type::func does NOT inherit a trait's default body** (traits-core's
   deliberate boundary): `SignalCell::new` is its own inherent
   declaration. If the owner ever wants type-path fallback to the
   trait's body, it is a one-filter change plus pins — unruled today.

Three general fixes the build forced, each now pinned: trait-associated
functions bind the TRAIT's generics from the call; a bound-site call no
longer inherits context requirements from a same-named member on an
unrelated trait (without which `MaybeSignal` was unshippable); and
`impl_select` grounds a bound's binder before its instantiation tier
(a `holder<V: Maybe<Cell>>` miscompile, only reachable since B165).
