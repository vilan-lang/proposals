# The tuple comprehension — widening a built form (B183)

> **Status: PROPOSED 2026-09-01** (work order 24, lane papers; tracker
> item [[B183]]).
>
> **The finding that reframes the ask: the comprehension is already
> built.** `(x in xs => e)` parses, types, lowers and runs on the shipped
> compiler; it is in the normative grammar (`docs/spec/grammar.md` §3.6),
> in the spec prose (`docs/spec/types.md` §5.9), and std's `combine` is
> its one live caller. The owner's B183 sketch is therefore not a new
> feature — it is **three widenings and one addition** to a form that
> exists, and each of the four is separable and separately priced.
>
> The sketch's two load-bearing sentences are both **contradicted by the
> build**. "Compile-time expansion (tuples have known arity)" — the
> shipped lowering is a *runtime* `source.map(closure)`, explicitly
> arity-independent (§3.2). "Each element's EXP type-checks at its own
> element type" — the shipped typing checks the body **once**, abstractly,
> against the pack's element binder `U` (§3.3). The two facts are the same
> fact seen twice, and together they mean the owner's semantics is a
> **re-implementation of the form's middle**, not a relaxation of a guard.
>
> That re-implementation also **surfaces a live garbage run** (P8): a
> comprehension body that writes `+` over the abstract element `U` is
> accepted today and concatenates at runtime — `two1`, the B179 family's
> signature. It is [[B174]]'s shape, reached from inside std's own
> variadic machinery, and this paper hands it to the census as a hit.
>
> Everything below was probed mechanically against a debug build of
> `vilan 0.40.0 (f30897ee0)`. Thirteen programs; the ledger is §7 and the
> sources are in the lane scratchpad.

## 1. The ask

From the owner (2026-09-01, off the B179 operand-role ruling):

> `(item in tuple => EXP)` maps a tuple element-wise; the multi-tuple
> form zips — `(a in aa, b in bb => a + b)` — which is enough to
> implement a generic `(a, b) + (c, d)`. Compile-time expansion (tuples
> have known arity), so each element's EXP type-checks at its own element
> type — heterogeneous tuples work where the elements do, and the result
> tuple's shape falls out per-element.

With four questions attached: arity mismatch between zipped tuples;
nesting; whether the binder is a pattern; and the composition with
[[B170]]'s now-reachable tuple impls, where `impl (i32, i32) with Add`
becomes *writable* through the comprehension — a slice of [[B3]]'s
variadic territory without the variadic machinery. Plus a grammar
collision check on `in`, now that the EBNF gate exists.

## 2. What is already built

### 2.1 The grammar has it, normatively

`docs/spec/grammar.md` §3.6, in the atom production:

```text
atom    = literal | IDENT | IDENT generic-args | struct-init
        | "(" expression ")" | tuple | list
        | tuple-comprehension | macro-invocation | macro-block
        | element | css-block ;
tuple-comprehension = "(" IDENT "in" secondary-expr "=>" expression ")" ;
```

and §3.9's type production carries the comprehension's type-level
sibling:

```text
     | "(" IDENT "in" type ":" type ")"          (* mapped tuple, §5.9 *)
```

`docs/spec/types.md` §5.9 ("Variadic tuples") is the prose. It specifies
the whole family: **tuple bounds** (`T: (2..)` for arity, `T: (..: Display)`
for elements), the **mapped type** `(U in T: F<U>)`, **spread parameters**
`...items: T`, **tuple-value spreads** `..e`, and — in one sentence —

> A **tuple comprehension** `(x in xs => e)` is the value-level mapping
> form.

One sentence is the entire normative specification of the form this paper
is about. That is the first thing to fix regardless of what else ships.

### 2.2 The parser has it, and it backtracks cleanly

`crates/vilan-core/src/parsing.rs:5375`, `parse_tuple_comprehension`:

```rust
/// `(binder in source => body)` — a tuple comprehension. The `in` distinguishes
/// it from a tuple/group atom (and the `=>` from the mapped *type* `(U in T:
/// F)`); `source` is a secondary expression, `body` a full expression.
/// Backtracks when the `(binder in` shape is absent.
```

`in` is a **hard keyword** (`lexing.rs:76`, `("in", Token::In)`), so it
can never be an identifier and the `(IDENT in` prefix can never be a user
expression. The form is attempted in atom position and backtracks. This
matters for §6.

### 2.3 The analyzer, transformer, formatter, CSS/element walkers,
call graph, liveness, init-order and interpreter all carry the node

`Node::TupleComprehension` / `Expr::TupleComprehension(binder, source,
body)` is threaded through `node.rs:406`, `analyzer.rs:179`,
`transformer.rs:3442`, `formatter.rs:4573`, `lift.rs:350`,
`css.rs:382`, `elements.rs:322`, `call_graph.rs:621`,
`init_order.rs:905`, `analyzer/liveness.rs:674`. There is no
half-built seam here; the form is a first-class expression.

### 2.4 One live caller in the whole estate

`std/src/reactive.vl:699-707`, inside `combine`:

```vilan,fragment
fun combine<T: (2..)>(sources: (U in T: SignalCell<U>)): SignalCell<T> {
	let snapshot = || (source in sources => source.get());
	let derived = SignalCell::new(snapshot());
	let _owned = (source in sources => register_with_owner(source.sub(|_| {
		derived.set(snapshot());
	})));
	derived
}
```

Two uses, both in one function. `combine` runs (P5). Its doc comment
already records the family's known ceiling:

> Widening the elements would need each one to be *some* `Source<U>`, a
> per-element EXISTENTIAL, and the mapped-tuple form has no place to bind
> it: `(U in T: Source<U>)` is refused because vilan has no trait
> objects... `combine` widens when the mapped-tuple grammar can bind a
> bound per element, not before.

That is a *different* ceiling from the one this paper lifts, and the two
should not be confused: `combine`'s is about binding a **bound** per
element; B183's is about admitting a **concrete tuple** as a source at
all.

## 3. What is NOT built — the three gaps, measured

### 3.1 The source must be a mapped tuple. A concrete tuple is refused.

This is the whole of B183's first ask, and it is one guard:

```
Error: a tuple comprehension's source must be a mapped tuple, got (i32, i32, i32)
   ╭─[ t01.vl:3:11 ]
 3 │     let ys = (x in xs => x + 1);
   │              ─────────┬────────
   │                       ╰──────── a tuple comprehension's source must be a mapped tuple, got (i32, i32, i32)
```

The refusal is byte-identical in shape for a heterogeneous concrete tuple
(P3, `got (i32, str)`) and — the surprising one — for a **spread pack**
(P2, `got T`). A `...items: T` with `T: (1..)` is *not* a mapped tuple:
only a parameter whose written type is literally `(U in T: F<U>)`
qualifies. So the form is narrower than "works over packs"; it works over
mapped packs, which in practice means it works where `combine` uses it
and essentially nowhere else.

**The refusal is well-worded and steers nowhere.** It names the source
type and stops. A reader who wrote the owner's spelling learns that
"mapped tuple" is a thing without learning what to do. Whatever this
paper's fate, that message wants a steer.

### 3.2 The lowering is a runtime `.map`, not a compile-time unroll

`crates/vilan-core/src/transformer.rs:3442`, the comment is the record:

```rust
Expr::TupleComprehension(binder_id, source_id, body_id) => {
    // A flat tuple is a JS array, so the comprehension lowers to a
    // runtime `source.map((x) => body)` — arity-independent, no
    // monomorphization needed. The binder is the closure parameter.
```

One JS closure, one `Array.prototype.map`. This is a genuinely good
choice for the case it was built for — a mapped pack whose elements all
go through the same `SignalCell<U> → U` shape emits one closure and works
at every arity with no code growth. It is also **structurally incapable**
of the owner's semantics: you cannot emit one closure body that performs
`i32` addition for element 0 and something else for element 1. Per-element
typing *requires* per-element emission.

So "compile-time expansion" is not a description of the build; it is a
request to replace the build's back half.

### 3.3 The body is typed once, abstractly — and native operators escape

The body is checked against the pack's element binder `U`, not against
each element. Method calls are checked properly against `U` and refuse
(P8c):

```
Error: cannot call method 'len' on U
 3 │     (b in boxes => b.v.len())
```

Native operators are **not**. P8b, over `(Box<i32>, Box<str>)`:

```vilan,fragment
fun f<T: (1..)>(boxes: (U in T: Box<U>)): T {
	(b in boxes => b.v + 1)
}
// f((Box { v = 1 }, Box { v = "two" }))  →  r.0 = 2,  r.1 = "two1"
```

`two1`. The B179 family's exact garbage-run signature, produced from
inside the variadic machinery std ships. The left operand of `+` is typed
`U` — an unbounded generic parameter of the enclosing function — and
[[B174]] is precisely "an unbounded generic LEFT operand of `+` still
concatenates". **This is a B174 hit**, and §5 hands it to the census as
one.

Two things follow. First, B174's fix (require a bound on the operand)
lands *here* as much as in trait defaults, and would refuse P8b's body
until it is written `T: (..: Add)` or the element bound admits `+`.
Second, the owner's per-element typing would refuse P8b for a different
and better reason: element 1 is a `str`, `str + i32` is not the
element's own legal expression, and the refusal would name the element.
The two fixes are complementary, not alternatives — B174 closes the
abstract case, B183's typing closes the concrete one.

### 3.4 The zip form does not parse

```
Error: found ',' expected '=>'
 4 │     let cc = (a in aa, b in bb => a + b);
   │                      ┬
   │                      ╰── found ',' expected '=>'
```

A clean, correctly-placed parse error — the production takes exactly one
binder. This is the one part of B183 that is genuinely an **addition**
rather than a widening.

## 4. The design, written to a decision

### 4.1 Semantics: the source is any tuple of known arity

**Rule.** A tuple comprehension's source may be any expression whose type
is a tuple whose arity is known at check time. Three cases, and they are
not the same case:

| Source type | Arity known? | Element types known? | Verdict |
|---|---|---|---|
| A concrete tuple `(A, B, C)` | yes | yes, individually | **admit — per-element** |
| A mapped tuple `(U in T: F<U>)` | no (T abstract) | no, only the shape | **admit — abstract** (as today) |
| A bare generic pack `T: (2..)` | no | no | **refuse** — nothing to map through |

The middle row is what ships today and must keep shipping; `combine`
depends on it and its one-closure lowering is right for it. The top row
is B183. **The two rows have different typing and different emission**,
and the paper's central recommendation is that they be built as two arms
of one form rather than one arm generalized:

- **Concrete arm.** Arity is `n`. The body is checked `n` times, once
  per element, with the binder bound to that element's own type. The
  result type is the `n`-tuple of the `n` body types — heterogeneous in
  and heterogeneous out. Emission is an **unrolled tuple construction**,
  `n` copies of the body, no closure and no `.map`.
- **Abstract arm.** Unchanged: one abstract check against `U`, one
  closure, one runtime `.map`.

The third row is a refusal that today is spelled awkwardly (`got T`) and
should say what it means: a pack has no known element sequence, so map it
after it is mapped, or declare the parameter as a mapped tuple.

**Why two arms and not one.** A single generalized arm would have to
choose one emission. Unrolling the abstract arm is impossible (no arity).
Closing over the concrete arm loses per-element typing, which is the
entire ask. The forms genuinely differ; making that explicit in the
implementation is cheaper than pretending otherwise, and it keeps
`combine` byte-identical, which is the green negative this widening must
carry.

### 4.2 The zip form

**Grammar.**

```text
tuple-comprehension = "(" comprehension-binding { "," comprehension-binding }
                      "=>" expression ")" ;
comprehension-binding = IDENT "in" secondary-expr ;
```

**Rule.** All sources must be tuples of known arity, and **all arities
must be equal**. The body is checked `n` times with all `k` binders bound
simultaneously to the `i`-th element of each source. Result: the
`n`-tuple of body types.

**Arity mismatch: refuse, naming both arities and both sources.** The
owner's own instinct ("refuse, surely") is right and there is no second
reading. The message should be shaped like the type-mismatch family and
name the two spans:

> `a zipped comprehension's sources must have the same arity: 'aa' has 2
> elements, 'bb' has 3`

with the second source's span as a secondary label. **The zip form is
concrete-arm only**: zipping two abstract packs would require proving
their arities equal, which the tuple-bound system cannot express today
(`T: (2..)` and `S: (2..)` are two independent ranges). Refuse an
abstract source in a multi-binder comprehension, and say so — that
refusal is a *feature boundary*, not a bug, and it should be in the spec
sentence from day one.

### 4.3 Nesting

Nesting **parses today** and is refused for a real reason. P9b:

```
Error: cannot access field '0' on type (U in T: U)
 3 │     (b in boxes => (c in boxes => c.v).0)
```

The inner comprehension over an abstract source correctly produces a
mapped tuple `(U in T: U)`, and positional access on a symbolic mapped
tuple is not supported. That refusal is correct and stays.

Under the concrete arm, nesting is unremarkable: the inner comprehension
over a concrete tuple has a concrete tuple type, and `.0` on it works
like `.0` on any tuple. **Recommend: admit nesting on the concrete arm,
with no special rule** — it falls out. The one thing to pin is that the
binders shadow ordinarily and that an inner binder shadowing an outer one
is legal and means what it says.

### 4.4 The binder is an IDENT, not a pattern — recommend keeping it so

P7: `((a, b) in boxes => a)` is a parse error ("unclosed `(` in
expression"), because the production says `IDENT`.

The owner asked whether the binder should be a pattern. **Recommendation:
no, not in this item.** Three reasons, in order of weight:

1. **It collides with the zip form at the same character.** `(a, b) in
   pairs` and `a in aa, b in bb` both begin `( a , b`-ish and both bind
   two names. A parser can be made to tell them apart, but a *reader*
   cannot, and the two mean very different things — destructure one
   source's elements versus zip two sources. Shipping both is a
   readability cost with no compensating power: `(p in pairs => p.0 +
   p.1)` already says the first, in one more character.
2. The concrete arm's per-element typing makes `p.0` type exactly, so
   the destructuring buys nothing the positional access does not.
3. It is separable. If the owner wants it later, it lands cleanly once
   the zip form's spelling is settled and habituated.

If the owner overrules this, the pattern must be **irrefutable** (names
and nested tuples only), matching `let`'s rule in §3.4 of the grammar.

### 4.5 The B170 composition — the payoff, and its exact size

[[B170]] made tuple impls reachable. The hand-written impl compiles and
runs today (P10b):

```vilan,fragment
impl (i32, i32) with Add {
	fun add(self, b: (i32, i32)): (i32, i32) {
		(self.0 + b.0, self.1 + b.1)
	}
}
// (1, 2) + (3, 4)  →  (4, 6)
```

The comprehension body it *wants* is refused today (P11) by §3.1's guard.
With the zip form it becomes:

```vilan,fragment
impl (i32, i32) with Add {
	fun add(self, b: (i32, i32)): (i32, i32) {
		(x in self, y in b => x + y)
	}
}
```

**Be honest about the size of this win.** For a 2-tuple it saves nothing
— four tokens against four. It pays at arity 4 and above, and it pays
most in *not repeating the index*, which is where the hand-written form
goes wrong (`self.2 + b.1` is a typo the type checker cannot see when the
elements share a type). That is a real but modest ergonomic win, and it
is the honest case for B183's zip half. It is **not** variadic generics
and should not be sold as such: each arity still needs its own `impl`
block. B3's territory is the one that writes `impl (..T) with Add` once;
this writes the *body* once per arity, not the impl.

### 4.6 One thing this does NOT fix — and it is already filed

P12: `(1, 2) + (3, 4, 5)`, through the impl above, runs and prints `4`.
The declared `b: (i32, i32)` did not refuse a 3-tuple. That is [[B180]]
("the dispatch path never checks a nominal left's declared B") reaching
tuple impls, already filed and already on the queue. Recorded here as a
datapoint, not as a new find: **B183 must not ship on top of it**, because
a zipped comprehension whose arity check is correct sitting inside an
impl whose operand check is not is a worse state than today.

## 5. The `in` collision check against the EBNF

The charge asks for a grammar collision check. Here it is, and it comes
with a caveat about what the gate does.

**`in` appears in exactly three productions** in `docs/spec/grammar.md`:

| Line | Production | Position |
|---|---|---|
| 292 | `for-expr = "for" IDENT "in" condition-expr block` | statement/expression, after `for` |
| 334 | `tuple-comprehension = "(" IDENT "in" secondary-expr "=>" expression ")"` | atom |
| 496 | `type = … \| "(" IDENT "in" type ":" type ")"` (mapped tuple) | type |

`in` is a hard keyword, so it never appears as an identifier and none of
the three can be reached by user naming. The three are disambiguated by
**what precedes the `in`**, not by what follows it: `for` opens the
first; `(` IDENT opens the second and third; and the second and third are
told apart by the token after the source (`=>` versus `:`) — and by
being in expression versus type position, which never overlap.

**The proposed zip production collides with nothing.** It extends the
second production *after* the `(IDENT in` prefix has already committed
the parse away from every other atom (a tuple `(a, b)` cannot reach it —
`a` would have to be followed by `in`). The only new decision is at the
comma after a source, where the parser today expects `=>`; it would then
accept `,` and expect another `IDENT in`. That decision point has exactly
one other reading — nothing — which is why today's error there is a clean
`found ',' expected '=>'`.

**The caveat, which the charge should hear.** `crates/vilan-cli/tests/grammar_ebnf.rs`
gates the EBNF for keyword coverage (both directions), attribute markers,
the `extern-args` rot site, and internal closure. Its own header says:

> Emphatically: **this is not a parser-equivalence check.** It says
> nothing about whether the parser accepts the language these productions
> describe. In particular it does not check that a production's SHAPE
> matches the parser's...

So the EBNF gate would **not** have caught, and will not catch, a
divergence between the zip production and the parser. Writing the
production is necessary and is not sufficient; the pins are what hold it.
Whoever builds this should add the zip form to the differential corpus at
`crates/vilan-core/tests/parse_differential.rs`, which already carries
the single-binder form (line 219, `("tuple_comprehension", "fun t(): T {
(x in xs => x + 1) }")`) — note in passing that this very fixture is the
§3.3 shape and will need a bound once B174 closes.

## 6. Scope, in build order

Four separable pieces. They are listed in dependency order and each is
independently shippable.

1. **Spec the form properly.** §5.9's one sentence becomes a subsection:
   the two arms, the typing rule for each, the emission note, the
   refusals. Zero code. Do this even if nothing else ships — the form is
   in the language and is one sentence documented.
2. **Steer the two existing refusals.** "source must be a mapped tuple"
   gains a steer; the `got T` case says what a pack lacks. Small,
   contained, valuable today.
3. **The concrete arm.** Per-element typing, unrolled emission, the
   result-shape rule, nesting falling out. This is the bulk, and it is
   the one that must carry a green negative: `combine`'s emission
   byte-identical, pinned.
4. **The zip form.** Grammar production, parser, the equal-arity refusal
   naming both spans, the abstract-source refusal, the B170 exhibit as a
   corpus program. Depends on 3 and on [[B180]] being closed.

## 7. Probe ledger

Thirteen programs against a debug build of `vilan 0.40.0 (f30897ee0)`.
**Five compiled and ran; eight were refused.** Sources are in the lane
scratchpad.

**Refused (8).**

| # | What it shows | Diagnostic (head) |
|---|---|---|
| P1 | **The ask, verbatim** — `(x in xs => x + 1)` over `(i32, i32, i32)` | `a tuple comprehension's source must be a mapped tuple, got (i32, i32, i32)` |
| P2 | A **spread pack** `T: (1..)` is not a mapped tuple either | `…must be a mapped tuple, got T` |
| P3 | A heterogeneous concrete `(i32, str)` | `…must be a mapped tuple, got (i32, str)` |
| P4 | **The zip form** — the parser's verdict | `found ',' expected '=>'` at the comma |
| P7 | **A pattern binder** `((a, b) in boxes => a)` | `unclosed '(' in expression: expected a matching ')'` |
| P8c | A `str`-only method over an abstract pack — the control for P8b | `cannot call method 'len' on U` |
| P9b | **Nesting**, `.0` on the inner result | `cannot access field '0' on type (U in T: U)` |
| P11 | **The B170 payoff** — the impl body as a comprehension | P1's message, `got (i32, i32)` |

**Compiled and ran (5).**

| # | What it shows | Output |
|---|---|---|
| P5 | std's `combine((a, b))` — the form's one live caller, heterogeneous | `1` / `two` |
| P6 | A **user-written** mapped-tuple fn + comprehension, heterogeneous | `1` / `two` |
| P8b | **GARBAGE RUN** — `(b in boxes => b.v + 1)` over `(Box<i32>, Box<str>)` | `2` / **`two1`** |
| P10b | [[B170]]'s tuple impl of `Add`, hand-written | `4` / `6` |
| P12 | `(1, 2) + (3, 4, 5)` through that impl — [[B180]], already filed | `4` |

## 8. Determinations

1. **The comprehension is built and shipped.** B183 is a widening of an
   existing form plus one addition, not a new feature. The item's
   framing should be corrected before it is scheduled.
2. **The owner's two stated semantics are both contradicted by the
   build.** The lowering is a runtime `.map` (arity-independent, one
   closure), and the body is typed once abstractly against the element
   binder. Per-element typing requires per-element emission; the two are
   the same change.
3. **Build it as two arms, not one generalized arm.** Concrete source →
   per-element typing, unrolled emission. Mapped source → today's
   abstract typing and `.map`, unchanged and pinned byte-identical.
   A bare pack stays refused, with a better message.
4. **The zip form is the only genuine addition**, and it is
   concrete-arm only: equal arities enforced, abstract sources refused
   (the tuple-bound system cannot prove two ranges equal).
5. **Arity mismatch refuses, naming both sources and both arities** —
   a two-span diagnostic, as the owner expected.
6. **Nesting needs no rule**; it falls out of the concrete arm. Today's
   refusal on a nested *abstract* result is correct and stays.
7. **The binder stays an `IDENT`.** A pattern binder collides visually
   with the zip form for no power the positional access lacks. Separable,
   deferrable, recommended deferred.
8. **The B170 payoff is real and modest.** It saves nothing at arity 2,
   pays from arity 4, and its true value is removing repeated indices.
   It is not variadic generics and must not be sold as such — each arity
   still writes its own `impl`.
9. **§3.3 is a [[B174]] hit inside std's own machinery**, handed to the
   census: a native `+` over the unbounded element binder `U` runs and
   concatenates (`two1`). The differential fixture at
   `parse_differential.rs:219` is the same shape.
10. **B183 must not ship before [[B180]] closes.** A correct arity check
    inside an impl whose operand check is broken is worse than today.
11. **The EBNF gate will not hold this.** It is explicitly not a
    parser-equivalence check; the production must be written *and* pinned
    in `parse_differential.rs`.

## 9. Recommendation

**BUILD, in the order of §6, and split the item.** Pieces 1 and 2 (spec
the form, steer the refusals) are cheap, are owed regardless, and should
go to any lane with capacity. Piece 3 (the concrete arm) is the feature
the owner actually asked for and is a real build — a second typing path
and a second emission path — worth doing because the form is already in
the language and currently serves exactly one function in std. Piece 4
(zip) should be **held until piece 3 lands and [[B180]] closes**, and
should be re-priced then against the honest payoff in §4.5, which is
smaller than the sketch implies.

Do **not** build it as one generalized arm. That is the one shape that
cannot work.

## 10. Owner questions

1. **The item's framing.** B183 reads as a new-feature proposal. The form
   ships today, in the grammar and the spec, with one std caller. Do you
   want the item rewritten to the widening it actually is, and split into
   the four pieces of §6, before it is scheduled?

2. **Two arms, confirmed?** The concrete arm (per-element typing,
   unrolled) and the mapped arm (abstract typing, one `.map`) genuinely
   differ in both typing and emission. The paper recommends building them
   as two explicit arms of one form. The alternative — one generalized
   arm — cannot preserve `combine`'s emission. Confirm the split?

3. **`combine`'s emission as a green negative.** The paper wants
   `combine`'s lowered output pinned byte-identical across the widening.
   Is that the right gate, or do you accept an unroll there too (it would
   grow the output per call site and per arity)?

4. **The zip form: hold or build?** §4.5 prices the B170 payoff honestly
   — nothing at arity 2, real from arity 4. Is that enough to build the
   only genuinely new syntax in the item, or does it wait for a second
   motivating use?

5. **The pattern binder — deferred, agreed?** The paper recommends
   keeping `IDENT` because a pattern binder is visually confusable with
   the zip form and buys nothing over `p.0`. Any objection to deferring
   it as its own item?

6. **The abstract-source refusal in a zip.** Zipping two packs would
   need the tuple-bound system to prove two arity ranges equal, which it
   cannot express. The paper refuses it and writes the boundary into the
   spec sentence. Do you want that boundary permanent, or filed as
   future work alongside `keyof` and the type-level spread?

7. **The §3.3 garbage run.** `(b in boxes => b.v + 1)` over a
   heterogeneous pack prints `two1` today. It is [[B174]]'s shape and
   this paper hands it to the census. Should it also be filed on its own,
   since it is reachable from std's shipped variadic machinery and B174's
   fix has not been ruled?

8. **Spec §5.9's one sentence.** The comprehension has one sentence of
   normative prose for a form that is fully built and threaded through
   ten compiler modules. Should the spec subsection land now,
   independently of any of the code pieces?
