# `std::tuple` — a tuple you can walk, keyed by position (A122)

> **Status: PROPOSED 2026-09-24** (work order 41, lane papers-41; tracker
> [[A122]], with [[B183]]'s family). Nothing here is ruled. The owner's
> pseudo-syntax of 2026-09-21 and the integrator's read of it (recorded on
> A122) are the INPUT; this paper tests both against the compiler and says
> where each holds. §9 is the open-questions set, one recommendation each.
>
> **Every claim below about what the compiler does today was run**, on
> `vilan 0.40.0 (1265ea5d3)` (`next` @1265ea5d), over scratch copies. The
> probes are kept at `scripts/integration/sweeps/order41/papers-41/probes/`
> (`a122_NN_*.vl` is probe PNN; P15/P15b are P01/P06 on `--backend rust`),
> `run_probes.sh` re-runs all of them, and `results-1265ea5d.txt` is the run
> this paper quotes.
>
> **The build is AFTER I5 S2** (a position is born `usize`, and a key is a
> position) **and after A124 S2c** (`divorce`'s return type names a node,
> §6.3) — Order 42 at the earliest, behind the train.

## 0. The ask, and the answer in one paragraph

kolt wants `divorce` — the reverse of `reactive::combine`: one derived source
per position of a tuple-valued source. The 2-arity form is three lines and
runs today (P01); the GENERIC form cannot be written, in userland or in std,
because nothing can walk a value of type `T: (2..)` or read it at a position.
The owner's sketch gives the two missing pieces library spellings — `entries()`
and `get(key)` on a std `tuple` module — and the integrator's read sharpened it
to a `Tuple` trait over every tuple, with a key type `TupleKey<T, U>` that
carries both the family it indexes and the element type at its position.

**This paper recommends that design, with four corrections the probes forced.**
(1) The blanket `impl type T: (2..) with Tuple` does not parse today — an impl
binder takes a trait bound, never a tuple bound (P07) — so the grammar gains
one alternative. (2) `map` cannot be an ordinary trait method, for the reason
B183 revision 2 proved (§R3.1: one closure has one type, a tuple has `n`); it
is the comprehension's SPELLING, desugared to `(x in t => e)` before typing —
one mechanism, two spellings, and the direction matters. (3) The owner's loop
`for (key, value) in fresh.entries()` is refused today whatever `entries()`
returns (B209, P05), so the design needs one more typing rule: a `for` over a
MAPPED tuple checks its body once, parametrically, at the element template.
(4) **The comprehension the whole design rests on miscompiles** whenever an
element occupies more than one slot — and `entries()`'s elements are pairs, so
it would always hit it (P16, P17; shipped `combine` has the same defect). The
fix — emit the abstract arm unrolled at each instance, which the JS emitter's
monomorphization already makes possible — is A122's precondition and is worth
filing on its own today.

Sized **M–L** as the item said, plus the layout fix (§8 F-a, S–M) ahead of it.

## 1. Ground truth — the probe ledger

| # | Program | Result on 1265ea5d3 |
|---|---|---|
| P01 | `divorce2<A, B>` by hand: `(source.map(\|w\| w.0), source.map(\|w\| w.1))`; three `set`s — position 0 moves, position 1 moves, nothing moves | runs; **`left fired 3, right fired 3`** — every output fires on every source change, including a no-op `set` |
| P02 | the generic form over a VALUE: `(x in source.get() => SignalCell::new(x))`, `source: SignalCell<T>` | `a tuple comprehension's source must be a mapped tuple, got T` |
| P03 | `whole.0` at `whole: T`, `T: (2..)` | `cannot access field '0' on type T` |
| P04 | B368: `for (i, w) in words.iter().enumerate()` and `for (n, s) in pairs` | runs: `0:a` … `2y` |
| P04b | `for x in (1, "two")` | B209's refusal: ``cannot iterate `(i32, str)`: a tuple is a fixed sequence of independently typed elements …`` |
| P05 | `for c in cells`, `cells: (U in T: SignalCell<U>)` | the same refusal, mapped arm: ``… A mapped tuple's elements have no positions to read yet, so the element-wise form here is the comprehension`` |
| P06 | the abstract arm: `(c in cells => c.get())` answering `T`; `(c in cells => SignalCell::new(c.get()))` answering `(U in T: SignalCell<U>)` | runs: `1 b` / `1 b (copies do not follow)` |
| P07 | `impl type T: (2..) with Arity { … }` | **parse error: `found '2' expected a type`** |
| P07b | the per-arity fallback: `impl (type A, type B) with Arity` beside `impl (type A, type B, type C) with Arity` | runs: `2` / `3` — B210 made tuple receivers resolve methods |
| P08 | `(x in self => …)` inside a blanket over `T: (2..)` | unreachable — the impl does not parse (P07); P02 is the same question |
| P09 | `(U in T: dyn Source<U>)` as a parameter, called with `(a, b)` of `SignalCell`s | **checks clean, then `TypeError: s[1].get is not a function` at run time** — a MISCOMPILE (§8 F-b) |
| P09b | controls: `dyn Source<i32>` at a plain parameter, and at a concrete tuple parameter `(dyn Source<i32>, dyn Source<str>)` | both run: `1` / `1 b` |
| P10 | `(x in (1, 2) => x + 1)` — the concrete arm | `… must be a mapped tuple, got (i32, i32)` (B183's piece 3, unbuilt) |
| P11 | `struct Key<T, U> { at: i32 }` and `(U in T: Key<T, U>)` — a key naming both the family and the element | runs: `0` — phantom parameters and an outer `T` inside a mapped template are both accepted |
| P12 | `T: (2..: PartialEq)` then `c.get() == c.get()` inside `(c in cells => …)` | ``… `U` is unbounded …`` — **the pack's element bound does not reach the comprehension's `U`** (§8 F-c) |
| P12b | the same bound, then `a == b` on the pack | ``… `T` is unbounded …`` — the pack is not comparable, and the sentence calls a tuple-bounded `T` unbounded (§8 F-d) |
| P13 | the round trip `divorce2(combine((a, b)))`, two writes to `a` alone | `a2=3 b2=b fired_a=2 fired_b=2` — `b`'s output fires for `a`'s writes |
| P14 | the owner's selector `import std::list::{ (impl _: (2..))::{ len } };` | `found '2' expected a type` — the same production as P07 |
| P15 | P01 on `--backend rust` | refused: ``does not emit a value of an unbound generic type parameter (parameter 1 of `divorce2`)`` |
| P15b | P06 on `--backend rust` | refused: ``does not emit a value of type `a mapped tuple` yet`` |
| P16 | the abstract arm with a MULTI-SLOT element: `reads((SignalCell::new((1, 2)), SignalCell::new("c")))` destructured as `((a, b), c)`; and a template that is a pair, `(c in cells => (7, c.get()))` | **`a=1,2 b=c c=undefined`** and **`p.1.0=undefined`** — a MISCOMPILE (§8 F-a) |
| P17 | the same through SHIPPED `std::reactive::combine`: `combine((point, label))` with `point: SignalCell<(i32, i32)>` | **`x=1,2 y=c l=undefined`**, before and after a `set`; the control `((1, 2), "c").1` reads `c` |
| P18 | a trait requirement `fun cells(self): (U in Self: Option<U>)`, and `(U in T: Option<U>)` over a `T` with no tuple bound | both accepted — a mapped type's source is not checked for a tuple bound in a signature, so §2.1's trait declares as written |

### 1.1 Where the record was wrong

- **"B318's `(impl _)` selector admits `impl type T: (2..) with Tuple`"** — the
  selector would, but the impl it would select cannot be written: the
  impl-subject binder is `( "type" IDENT | "_" ) [ ":" bound-list ]`
  (`docs/spec/grammar.md` §3.9) while a tuple bound is a separate production
  that only a generic PARAMETER takes (§3.3, `generic-param = … ( bound-list |
  tuple-bound )`). P07 and P14 are the same refusal. The fix is one
  alternative in one production (§4.1). The selector is not needed at all: a
  plain `import std::tuple::Tuple;` brings every impl in the files on the path
  (`docs/spec/names.md` §4.3), so importing the trait is importing the blanket.
- **A122's headline — "kolt channel.vl:19 writes the signature with `// TODO:
  Implement`"** — stale. kolt (9a057c6 plus the owner's uncommitted edits) has
  the 2-arity hand form at `src/channel.vl:26`, written with pattern closures
  (`source.map(|(a, _)| a)`), used at `:47` on
  `reactive::combine((message, author)).map(..)` — so kolt's one call site IS
  the round trip P13 measures.
- **"B368 admits a tuple pattern in a `for` header, so the comprehension binder
  can take the same production"** — B368 runs (P04), but the pattern is not what
  stands in the way of the owner's loop: the LOOP is refused, over a tuple value
  (P04b) and over a mapped tuple (P05), by B209's rule. §4.4 is the one new
  typing rule that admits the loop the design needs.
- **std's own comment on `combine`** (`vilan/std/src/reactive.vl:1412`, "`(U in
  T: Source<U>)` is refused because vilan has no trait objects") is stale since
  dyn-40: `(U in T: dyn Source<U>)` is ACCEPTED — and miscompiles (P09).
- **B183 revision 2's "a tuple receiver has no method resolution at any
  arity"** (§R1.2) is history: B210 closed it (2026-09-03) and P07b runs. What
  revision 2 argued ONE level up still stands and is load-bearing here: no
  closure can map a tuple (§R3.1). §3 builds on exactly that.
- **B183 revision 2's green negative for the concrete arm — "std `combine`'s
  emission byte-identical"** — cannot hold: `combine`'s emission is wrong for a
  multi-slot element (P17), so the fix MUST move it (§8 F-a).

## 2. The design

### 2.1 The module

```vilan
// vilan/std/src/tuple.vl
/// A position in every tuple of the family `T`, typed at the element it names.
/// Minted only by `keys()` / `entries()`; there is no public constructor, so a
/// key always names a position `T` really has, at the type it really has there.
export struct TupleKey<T, U> {
	at: usize,
}

/// Every tuple of arity two or more, walked by position.
export trait Tuple {
	/// The arity, as a value.
	fun len(self): usize;
	/// One key per position, each at its own element type.
	fun keys(self): (U in Self: TupleKey<Self, U>);
	/// `(key, value)` per position.
	fun entries(self): (U in Self: (TupleKey<Self, U>, U));
	/// The element at `key` — in THIS tuple or in any tuple mapped from it (§4.3).
	fun get<U>(self, key: TupleKey<Self, U>): U;
	// `map(|x| e)` is the comprehension `(x in self => e)` — §3. It is declared
	// for the docs and the editor, and typed by the desugar, never by a signature.
}

export impl type T: (2..) with Tuple { … }
```

The trait's declaration is writable today — a requirement naming `Self` as a
mapped source is accepted (P18); the impl is what needs §4.1. Imported as
`import std::tuple::Tuple;` (or `std::tuple::{ Tuple, TupleKey }` where a
signature names the key). The trait is found the way `Try` and `Lift`
are, by name in its std module (`analyzer.rs:60431`), because two of its members
are typed by rules no signature can state (§3, §4.3).

**Not in it, deliberately:** `values()` — the owner's sketch has it, and a
tuple's values are the tuple (`t.values().map(f)` is `t.map(f)`); `filter`,
`fold`, `enumerate` and the rest of B183 revision 2's refused suite, for its
reasons (§R2); a `set(key, value)` — a tuple is a value, and `mut t` plus
`t = …` is the write.

### 2.2 The owner's sketch, rewritten

The sketch, as recorded on A122:

```vilan
let signals: (U in T: SignalCell<U>) = source.get().values().map(|initial| Signal::new(initial));
source.effect(|fresh| {
	for (key: TupleKey<T>, value: T) in fresh.entries() { signals.get(key).set(value); }
});
```

under this design reads

```vilan
let signals: (U in T: SignalCell<U>) = source.get().map(|initial| SignalCell::new(initial));
let _effect = source.effect(|fresh| {
	for (key, value) in fresh.entries() {
		signals.get(key).set(value);      // key: TupleKey<T, U>, value: U — per position
	}
});
```

and it types: `fresh.entries()` is `(U in T: (TupleKey<T, U>, U))`; the loop
checks its body once at a rigid `U` (§4.4); `signals.get(key)` is
`SignalCell<U>` by §4.3; `.set(value)` takes the `U`. The owner's two named
hazards are exactly the two rules: (1) "`TupleKey<T>` indexes any tuple DERIVED
from `T`" is §4.3; (2) "tuple `.map` must return a tuple typed as a derivative
of `T` so it can be indexed later" is §3 — `map`'s answer is `(U in T: F<U>)`,
a tuple of the family `T`, which a `TupleKey<T, U>` indexes.

§6 argues `divorce` should NOT be written this way — an effect writing `n`
cells is the state machine the pipeline paper warns about — but the sketch is
the test of the typing, and it passes.

## 3. `map` is the comprehension's spelling, not a method

B183 revision 2 §R3.1 is the argument, and it survives B210: a tuple
`(A0, …, A_{n-1})` is a family indexed by position, so mapping it needs a
different function at every index, and **one closure value has one type**. No
signature `fun map<F>(self, f: F): …` can be written — there is no `F`.

So `t.map(|x| e)` is admitted only with a closure LITERAL in the argument, and
it DESUGARS, before typing, to the comprehension `(x in t => e)`: the literal's
parameter is the comprehension's binder and its body is the template. One
mechanism — the comprehension's elaborator — types both spellings, and there is
no second rule to keep in step. The direction is forced: the comprehension
cannot desugar INTO a method call with an ordinary closure, because that
closure would need `n` types.

What the rule refuses, and what the refusal says: `t.map(f)` with `f` a named
closure VALUE — "`map` over a tuple takes a closure literal: its body is checked
once per position, and a closure value has one type. Write `t.map(|x| f(x))`."
A generic function `f<U>(x: U)` passed by name is the same refusal until
fn-coercion can carry a generic (it cannot today).

**What `map` is for, therefore:** discoverability (it completes after `t.`,
the comprehension does not) and the chain — `a.zip(b).map(|(x, y)| x + y)`
reads left to right. The comprehension stays the core form; `combine`'s body
keeps it, and the book teaches both as one thing (§9 Q5).

## 4. The typing work

Six pieces. None of them is a new kind of type: `Type::Mapped(binder, source,
template)` (`type_.rs:118`) already carries the per-position `U` as a generic
id, and every rule below reads or substitutes that id.

### 4.1 The blanket's binder takes a tuple bound (grammar, S)

`( "type" IDENT | "_" ) [ ":" ( bound-list | tuple-bound ) ]` in the
impl-subject binder, and the same in an `impl-selector`'s `type` (P14 then
parses — harmless, and consistent). Impl selection matches a tuple receiver
against a tuple-bounded binder with the rule a generic parameter already uses
(`docs/spec/types.md` §5.9: arity inside the range, every element satisfying
the element bound). B98's coherence rule (`check_duplicate_trait_impls`) sees
one impl. The EBNF gates (`grammar_ebnf`, `grammar_sync`) move.

### 4.2 A `T: (2..)` value is `(U in T: U)` — the comprehension takes it (S)

The analyzer already REDUCES the identity mapping to its source
(`reduce_identity_mapped`, `analyzer.rs:37483`, B211: `(U in T: U)` IS `T`).
The comprehension's source rule (`Expr::TupleComprehension`,
`analyzer.rs:36299`) needs the converse: a source whose type is a tuple-bounded
generic `T` is read as `Mapped(fresh U, T, U)`. P02's refusal becomes a pass;
`(x in source.get() => …)` types. This is what lets the blanket's own bodies
walk `self`, and it is independently what the item's piece (1) asked for.

### 4.3 A key indexes the whole family (M — the heart of it)

`get<U>(self, key: TupleKey<Self, U>): U` is an ordinary signature for the
identity case: `t.get(key)` with `t: T` and `key: TupleKey<T, U>` answers `U`.
The family rule is one extra case in the reconciler:

> **A `TupleKey<T, U>` is a `TupleKey<(V in T: F<V>), F[V := U]>`.** A key for
> `T` is a key for every tuple mapped from `T`, at the mapped element type.

With it, `signals.get(key)` — `signals: (V in T: SignalCell<V>)`, `key:
TupleKey<T, U>` — answers `SignalCell<U>` with no special case in `get`
itself. The FAMILY check is the `T` equality the reconciler already does; two
tuples of different families (`T` and `S`, both `(2..)`) are never
interchangeable, which is the whole point — their arities are unrelated.

The substitution `F[V := U]` is the operation `Mapped`'s own expansion already
performs per element when `T` resolves (`type_.rs:114`: "each element `X` maps to
`F[U := X]`"); here it is applied with a generic `U` rather than a concrete `X`.
That is the "per-position `U` reified in a key type" the item sized.

**Scope.** A `U` minted by a loop or comprehension over `entries()` is rigid
inside that body and out of scope outside it. A key or value typed at it cannot
escape — an outer binding's type was fixed before the loop and cannot mention
`U`, so the assignment is refused by the ordinary rigid-generic mismatch. Worth
one pin; not worth a new message.

**No integer indexing.** `whole[i]` with an integer `i`, and `whole.0` at a
generic `T` (P03), stay refused; the refusal gains the steer: "a tuple of
family `T` is read at a `TupleKey<T, U>` from `keys()` or `entries()` — the key
carries the element's type, an integer cannot". This is the item's "the
indexed read refused OUTSIDE a comprehension with a message naming the rule",
restated for keys.

### 4.4 A `for` over a mapped tuple checks its body once (S–M)

The owner's loop needs it and today it is B209's refusal (P05). The rule:
**over a MAPPED tuple `(U in T: F<U>)`, the `for` binder takes the template
`F<U>` with `U` rigid, and the body is checked ONCE** — parametrically, exactly
as the comprehension's body already is. It is sound for the reason B209's
refusal existed: the refusal was about a binder with NO type (`any`); this
binder has one, and the body can use only what `U`'s bounds promise.

Emission is a runtime loop over the instance's elements — with §4.6's layout
caveat. The CONCRETE-tuple loop (`for x in (1, "two")`) is untouched: it stays
B209's refusal, and whether it should unroll is B183's open Q2, the owner's.
Parametric typing is a third answer to that Q2 (`x` rigid, `x + 1` refused,
moving values between keyed slots admitted) and §9 Q2 raises it without
deciding it.

### 4.5 `map`'s desugar and `entries`/`keys`/`len` (S)

§3's desugar is a rewrite at the call node before analysis, keyed on the
receiver being tuple-typed and the method being `Tuple::map`. `entries`, `keys`
and `len` are std bodies over an intrinsic that knows the instance's positions
(§4.6) — ordinary signatures, no new typing.

### 4.6 Emission — the layout problem and the unroll (M; the precondition)

The comprehension lowers to a runtime `source.map((x) => body)`
(`transformer.rs:4752`, "arity-independent, no monomorphization needed"). That
comment's premise is false: **tuples store FLAT** (`types.md` §5.9 — "a
tuple-typed element occupies its elements' slots"), so a runtime `.map` over the
JS array is correct only when every source element and every template result is
ONE slot wide. P16 and P17 are the two ways it breaks: a multi-slot SOURCE
element (a `SignalCell<(i32, i32)>`'s value) and a multi-slot TEMPLATE (a pair).
`entries()` returns pairs, so it would hit the second on every call.

The JS emitter already monomorphizes generic calls ("A call to a generic
function/method is compiled to a specialized instance chosen by its concrete
type arguments", `transformer.rs:5266`, with M16's body sharing), so at
emission time `T` IS concrete in every instance. **The fix is to emit the
abstract arm UNROLLED at each instance**: the element offsets computed from the
concrete `T`, the body emitted once per position into the flat layout — the
typing stays abstract (checked once), the emission becomes per-position. It is
B183 revision 2's "concrete arm" emission, reached through instances rather than
through concrete sources, and it is the same unroll the native backend needs
(which refuses mapped tuples outright today, P15b). `get(key)` with a key known
only at run time lowers, per instance, to a read at the key's slot offset — a
table of offsets per instance in JS, a `match` over the positions whose element
type IS `U` natively (the other arms are unreachable by §4.3 and emitted as
`unreachable!()`).

This is worth building BEFORE A122 and on its own, because it is a live
miscompile in shipped std (§8 F-a). M16's sharing keeps the cost down: two
instances whose layouts agree render alike and share one body.

### 4.7 Sizing

| Piece | Where | Size |
|---|---|---|
| §4.6 the unrolled emission — the layout fix | `transformer.rs` (the comprehension lowering), a layout helper over `Type::Tuple`; the pins P16/P17 | **S–M, ahead of A122, filable today** |
| §4.1 the tuple-bound impl binder | `parsing.rs`, `docs/spec/grammar.md`, impl selection | S |
| §4.2 a `T` value as a comprehension source | `analyzer.rs` (the comprehension's source rule) | S |
| §4.3 the key's family rule | `analyzer.rs` (the reconciler: one arm), `std/src/tuple.vl` | **M** |
| §4.4 the parametric `for` over a mapped tuple | `analyzer.rs` (`iterable_element_type`'s mapped arm), the transformer's loop | S–M |
| §4.5 `map`'s desugar; `entries`/`keys`/`len` | the call-node rewrite; std | S |
| the native half (the unroll, `get`'s match) | `vilan-rust` | M, and it waits on F1's mapped-tuple support |
| the book: `std::tuple`'s page, `types.md` §5.9's keys and the `for` rule | docs | S |

**M–L in total** for the JS build (the item's estimate holds), with the layout
fix as its S–M precondition and the native half as a separate M.

## 5. The spellings, side by side

### 5.1 `divorce`, three lines beside `combine`

```vilan
/// The reverse of `combine`: one derived source per position.
export fun divorce<T: (2..)>(source: SignalCell<T>): (U in T: SignalCell<U>) {
	source.get().keys().map(|key| source.map(|whole| whole.get(key)))
}
```

`keys()` is `(U in T: TupleKey<T, U>)`; the `map` template is checked once at a
rigid `U`, where `whole.get(key)` is `U` and `source.map(..)` is (before S2c)
`SignalCell<U>`; the answer is `(U in T: SignalCell<U>)`. `source.get()` is read
once, at construction, only for its positions. (The comprehension spelling is
the same line: `(key in source.get().keys() => source.map(|whole|
whole.get(key)))`.) §6.3 gives the signature after the flip.

### 5.2 The round trip

`divorce(combine((a, b)))` re-derives `a`'s and `b`'s values (P13, by hand at
arity 2). The pin the item asks for is that program at arity 2 and 3, over
`divorce` itself.

### 5.3 B183's zip: `a.entries().zip(b.entries())`

`zip` is the same desugar with two sources — B183's multi-binder form,
`(x in a, y in b => (x, y))` — and the key family decides when it types:

- **Same family** (`a: (V in T: F<V>)`, `b: (W in T: G<W>)`): the arities are
  equal by construction, and the answer is `(U in T: (F<U>, G<U>))`. This is the
  case the abstract arm could never prove before (B183 revision 1 §4.2 refused
  multi-source abstract comprehensions because two arity RANGES cannot be proven
  equal); the family makes it one `T` equality.
- **Two concrete tuples**: equal arity or the refusal naming both arities
  (B183 revision 1 §4.2, unchanged).
- **Two different abstract families**: refused, naming both families.

`a.entries().zip(b.entries())` gives each position both keys and both values;
`a.zip(b)` is the key-free form. B183's motivating case,
`impl (i32, i32) with Add { fun add(self, b: (i32, i32)): (i32, i32) {
self.zip(b).map(|(x, y)| x + y) } }`, needs the CONCRETE arm as well — a rigid
`U` has no `+` — so zip is B183's piece 4 plus that arm, and **not part of
A122's build**; `divorce` does not need it.

## 6. `divorce` and when its outputs fire

### 6.1 The claim, measured

**Every output fires on every source change.** P01: three writes to the source
(position 0 moved; position 1 moved; nothing moved) fire EACH output three
times. P13: two writes to `a` alone fire `b`'s output twice. The derivation per
position — `source.map(|whole| whole.get(key))` — subscribes to the WHOLE
source, and today's `SignalCell::set` does not compare (A124 Q3's premise). The
owner's effect form writes all `n` cells per run and fires the same way.

### 6.2 No gate in `divorce` — and why

A `PartialEq`-gated write per position would make an output fire only when ITS
position moved. The paper recommends against building it into `divorce`:

1. **The ruled composition already exists.** A124 Q3 (RULED 2026-09-22):
   `.cell()` does not compare, and a separate `.distinct()` node carries `T:
   PartialEq`. So the gate is `divorce(s).0.distinct()` at the consumer that
   wants it, at a CONCRETE `U`, where the bound is checkable — and nowhere else.
2. **The bound is not expressible usefully today.** A gated `divorce` needs every
   element `PartialEq` — `T: (2..: PartialEq)` — and P12 shows that bound does
   not reach the comprehension's `U`, so the body could not call `==` anyway
   (§8 F-c). A gate would also narrow `divorce` to comparable elements, and
   kolt's own use divorces an `Option<Message>` pair.
3. **kolt's use does not want it.** channel.vl:47 divorces inside a `when_some`
   body where both halves render from one payload; an extra comparison per
   position per change buys nothing there.

### 6.3 The signature through the train

- **Before A124 S2c** (combinators return cells): `(U in T: SignalCell<U>)`, as
  §5.1 — `n` cells and `n` subscriptions, each a derivation (A110 door 2's
  `as_derivation` mark, once per output, the way `combine` leaves it).
- **After S2c** (A122's build lands here, §7): `source.map(..)` returns a node,
  `Map<S, T, U>` (reactive-pipeline.md §2.2 — nameable: the transform is held as
  `|T| U`). So `divorce<T: (2..), S: Source<T>>(source: S): (U in T: Map<S, T,
  U>)` — cold: no evaluation until a leaf subscribes, `n` leaves means `n` pulls
  of the whole source (§6.2 of that paper), and `.cell()` per position where a
  consumer wants state. `(U in T: dyn Source<U>)` is the other spelling and is
  NOT recommended until §8 F-b is fixed (it miscompiles).
- **Not the owner's effect form.** An effect writing `n` cells is a state
  machine with its own initial-value and ordering questions
  (reactive-pipeline.md §8); the derivation form has neither.

## 7. Order and slices

A122's positions are BORN `usize` (I5 ruling 4's "born `usize`" precedent,
A112's `Splice(at, ..)`), so the build follows I5 S2; its `divorce` names a
node, so it follows A124 S2c. Both are Order 42's train (briefs41 R-a). So:

- **Now (any order): §8 F-a, the layout fix** — a miscompile in shipped
  `combine`, S–M, independent of everything else. Recommended for Order 42's
  non-train lanes or the first order after.
- **A122 S1 (M)** — §4.1 grammar, §4.2 the `T` source, §4.3 keys and `get`,
  `std::tuple` with `len`/`keys`/`entries`/`get`; pins: `get` through a mapped
  family, the key refused across families, an escaping `U` refused, the integer
  read refused with the steer.
- **A122 S2 (S–M)** — §4.4 the parametric `for` over a mapped tuple; the owner's
  sketch (§2.2) as a pin.
- **A122 S3 (S)** — §3's `map` desugar, `divorce` beside `combine`, the book;
  pins: `divorce` at arity 2 and 3, the round trip, the firing counts of §6.1
  STATED (every output fires on every change), the closure-value refusal.
- **Separately**: zip (B183 piece 4, with the concrete arm, piece 3); the native
  half with F1's mapped-tuple support.

Order 42 at the earliest for S1, after the train merges — the item's text and
the brief agree.

## 8. Finds — defects met while probing, not fixed here

**F-a (HIGH, MISCOMPILE) — the tuple comprehension ignores the flat layout, and
shipped `combine` returns a mis-shaped tuple.** P17, through std alone:

```vilan
import std::reactive::{ SignalCell, combine };
fun main() {
	let point = SignalCell::new((1, 2));
	let label = SignalCell::new("c");
	let ((x, y), l) = combine((point, label)).get();
	print(i"x={x} y={y} l={l}");        // x=1,2 y=c l=undefined
}
```

The emitted `combine` builds `[[1, 2], "c"]` by a runtime `.map`; the caller
reads the flat layout `[1, 2, "c"]` at slots 0, 1, 2. Same defect for a template
that is a tuple (P16). Every `combine` whose inputs hold tuples is affected;
kolt's one `combine` holds two `Option`s and is not. Fix: §4.6. `vilan check`
is clean; the native backend refuses the program (P15b), so the differential
cannot see it.

**F-b (MISCOMPILE) — a mapped tuple of `dyn` elements skips the coercion.**
`fun reads<T: (2..)>(sources: (U in T: dyn Source<U>)): T` accepts `(a, b)` of
`SignalCell`s and throws `s[1].get is not a function`: the JS object pair
(dyn-40's representation) is never built for a mapped-tuple element, while the
same coercion at a plain and at a concrete-tuple parameter works (P09b). Either
coerce per element at the call (the instance knows each element's type) or
refuse `dyn` inside a mapped template until then.

**F-c — a pack's element bound does not reach the comprehension's `U`.** `T:
(2..: PartialEq)` is enforced at the call (`types.md` §5.9) but `(c in cells =>
c.get() == c.get())` refuses `==` on `U` (P12). The element bound should be a
bound on `U` inside every mapped type over `T`.

**F-d (diagnostic) — "`T` is unbounded" for a tuple-bounded `T`** (P12b). The
sentence should say the tuple bound constrains arity and elements, not the pack.

**F-e (record) — two stale sentences**: A122's headline (kolt's line and TODO,
§1.1) and `reactive.vl:1412`'s "no trait objects".

## 9. Open questions, with a recommendation each

**Q1 — `map` admits only a closure literal.** §3 shows no signature can type a
closure VALUE there. *Rec: yes — the literal is the template; a value is refused
with the steer `t.map(|x| f(x))`.*

**Q2 — the parametric `for` over a mapped tuple (§4.4).** The owner's sketch
needs it; B209 refuses it today. It is sound (the binder has a type), and it
does not touch the CONCRETE-tuple loop, which stays B183's Q2 (unroll or
refuse) — though parametric typing is a third answer to that Q2 worth the
owner's eye. *Rec: admit it for mapped tuples in A122 S2; leave the concrete
loop to B183 Q2.* (If the owner would rather keep `for` refused, `entries()` is
consumed by the comprehension alone and §2.2's sketch is written as `(entry in
fresh.entries() => …)` — workable, and uglier for a statement body.)

**Q3 — may userland construct a `TupleKey`?** A public constructor lets a program
mint `TupleKey<(i32, str), str> { at = 0 }` — a key that lies. *Rec: no public
constructor; keys come from `keys()`/`entries()` only* (the field is private
under B318's default).

**Q4 — does `divorce` gate on `PartialEq`?** *Rec: no* (§6.2): `.distinct()` at
the consumer is the ruled composition (A124 Q3), and the bound would not reach
the body today (F-c).

**Q5 — keep the comprehension syntax beside `map`?** *Rec: keep it* — it is the
core form both spellings are typed by, `combine`'s body, and the zip form's
home; the book teaches `t.map(|x| e)` and `(x in t => e)` as one thing.

**Q6 — `values()`** from the owner's sketch. *Rec: omit* — the tuple is its
values.

**Q7 — the layout fix ahead of A122.** F-a is a shipped miscompile and A122's
`entries()` cannot work without it. *Rec: file F-a now as its own item (HIGH,
MISCOMPILE), fix it by §4.6's unroll in the first order with room — it is not
train work and need not wait for Order 42's train.*

## 10. The recommendations, collected

1. **Build `std::tuple`**: the `Tuple` trait over every `T: (2..)` with `len`,
   `keys`, `entries`, `get`, and `map` as the comprehension's spelling;
   `TupleKey<T, U>` with no public constructor (§2).
2. **One grammar alternative** — a tuple bound on an impl binder (§4.1); the
   owner's `(impl _: (2..))::{ … }` selector is then unnecessary: `import
   std::tuple::Tuple;` brings the blanket.
3. **One mechanism**: `t.map(|x| e)` desugars to `(x in t => e)` before typing
   (§3); the reverse is impossible.
4. **The key's family rule**, `TupleKey<T, U>` indexes every `(V in T: F<V>)` at
   `F[V := U]` — the M of the item's M–L (§4.3).
5. **A parametric `for` over a mapped tuple** (§4.4), leaving the concrete loop
   to B183 Q2.
6. **`divorce` as a derivation per position, three lines beside `combine`**
   (§5.1), with NO `PartialEq` gate — every output fires on every source change,
   stated in its doc and pinned; `.distinct()` is the gate (§6).
7. **Fix the flat-layout miscompile first** (§8 F-a; §4.6's per-instance
   unroll), and file F-b, F-c and F-d.
8. **Order**: the layout fix whenever there is room; A122 S1–S3 after Order
   42's train (I5 S2 for the `usize` positions, A124 S2c for `divorce`'s node
   type); zip and the native half separately (§7).
