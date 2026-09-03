# The tuple comprehension — the suite question (B183, revision 2)

> **Status: PROPOSED 2026-09-03** (work order 26, lane b183-paper-2;
> tracker item [[B183]]). Revision 1 (work order 24) is kept intact
> below, from "# The tuple comprehension — widening a built form"
> onward; nothing in it is deleted, and the three places revision 2
> **overturns** it are named in §R1.4.
>
> **The owner's word, 2026-09-03:** *"If `a in aa => EXP` maps and
> `a in aa, b in bb => EXP` zips then perhaps a whole suite of monadic
> transformations should exist."*
>
> **The short answer: no — and the reason is a type-theoretic one, not a
> taste one.** Over a list the comprehension body has ONE type, so a
> closure suffices and a method wins; over a tuple the body has `n`
> types, so only a *syntactic template instantiated n times* can express
> it, and no closure — variadic or otherwise — ever can (§R3.1). `=>`
> earns its keep on tuples for exactly the reason it earns nothing
> anywhere else. The suite that follows from that is **map and zip, and
> nothing else**: filter cannot fix an arity, fold produces a scalar and
> already has a spelling (`for`), flat_map already has one (the
> tuple-value spread `..e`), enumerate collides with zip at the comma,
> and chunk is arity surgery that belongs to [[B3]]. Every language that
> shipped a statically typed tuple suite — Swift 5.9, Scala 3 — shipped
> map and zip and stopped (§R3.4).
>
> **Two new measurements changed the design**, and neither was in
> revision 1:
>
> 1. **`for x in tuple` already exists, is undocumented, and binds
>    `any`** (§R1.1). It runs. Over `(1, "two", true)` the body
>    `x + 1` prints `2`, `two1`, `2`. `let s: str = x` is accepted and
>    prints `undefined`. `for e in &mut tuple` compiles, emits, runs and
>    **silently discards the write**. The spec says `any` is "produced
>    at host boundaries"; a tuple literal is not a host boundary, so
>    this is a spec violation, not an ergonomic gap. It is also the
>    *only* way the suite's consuming half (fold, any/all, for_each) is
>    reachable today — unsoundly.
> 2. **A method cannot be called on a tuple receiver at all** (§R1.2) —
>    not through an inherent impl, not through a trait impl, at arity 2,
>    concretely, with everything written out by hand. Revision 1 said
>    `aa.map(|a| …)` "needs variadic generics to type". The truth is
>    harder: it needs *method resolution on tuple receivers*, which does
>    not exist at any arity. [[B170]] made tuple impls reachable through
>    the **operator** dispatch path only; `(1,2).add((3,4))` is still
>    "cannot call method 'add' on (i32, i32)".
>
> Twenty-six programs against a debug build of `vilan 0.40.0
> (635e37289)` — `origin/next` at the lane's start. Twelve ran, fourteen
> were refused; the ledger is §R8.

## R1. Ground truth added since revision 1

### R1.1 `for x in tuple` exists, binds `any`, and is unsound three ways

Revision 1 never asked whether the suite's consuming half was already
reachable. It is. `for x in xs` over a tuple parses, checks, emits and
runs — and the binder's type is `any`.

The mechanism is a fallthrough, not a decision. `iterable_element_type`
(`crates/vilan-core/src/analyzer.rs:23891`) has arms for `List`/`Set`,
for `[T; n]`, for a struct or enum with a `next`, for `Self` inside a
trait default, and for a trait-bounded generic. **There is no
`Type::Tuple` arm**; a tuple reaches `_ => None`, and
`finalize_build`'s commit does `.unwrap_or(Type::Any)` — the
give-up default written for "an empty, never-pushed list". The
emission side then lowers it as a native `for…of`, which works,
because a flat tuple is a JS array.

Three exhibits, all on `origin/next`:

```vilan
fun main() {
	let xs = (1, "two", true);
	for x in xs {
		print(x + 1);          // R1:  2  /  two1  /  2
	}
}
```

`two1` is the B179 family's signature — but [[B174]] closed on
2026-09-01 and this is **not** a B174 hit. B174 bounds an unbounded
*generic* left operand; here the left operand is `any`, which the spec
makes absorbing ("`any` unifies with every type in both directions",
`docs/spec/types.md:915`). The bound-checking fix cannot see it. The
defect is upstream: a tuple should never have produced `any`.

```vilan
fun main() {
	let xs = (1, "two");
	for x in xs {
		let s: str = x;        // accepted
		print(s.len());        // R18:  undefined  /  3
	}
}
```

`any` launders into `str` through an ordinary annotation.

```vilan
fun main() {
	mut xs = (1, 2, 3);
	for e in &mut xs {
		e = e + 1;
	}
	print(xs.0);               // R17:  1   — the write is GONE
	print(xs.1);               //       2
}
```

The lending walk emits `__replace(e, e + 1)` with `e` bound to a JS
number; `Object.assign` on a primitive target coerces to a wrapper and
the tuple slot is never touched. It compiles clean, runs, and does
nothing.

The guards are inconsistent, which is the tell that none of this was
designed: **field access on `any` is refused** ("cannot access field
'0' on type any", R23, over a tuple of tuples) and **method calls on
`any` are refused** ("cannot call method 'len' on any", R26), but
native binary operators and annotation-directed binding both go
through.

**This is filable on its own and should not wait for B183.** Two
readings, and the paper prefers the second:

- **Refuse it.** A tuple is not iterable; say so, and name the
  destructuring or positional access that replaces it. Cheap, honest,
  and it deletes the hole today.
- **Unroll it.** `for x in aa { body }` over a concrete tuple checks
  and emits the body once per element, with `x` bound to that
  element's own type. That is *the same elaboration the concrete arm
  of the comprehension needs* (§R2.1) — one machine, two spellings —
  and it is what makes the suite's consuming half (fold, any/all,
  for_each) well-typed without any new syntax at all (§R2.4).

### R1.2 A tuple receiver has no method resolution, at any arity

Revision 1's central argument for syntax over methods was that
`aa.map(|a| …)` "needs variadic generics — [[B3]] — to type". That
argument is correct but weaker than the facts. Written out by hand at a
fixed arity, with no variadic machinery anywhere, the call is still
refused:

```vilan
impl (i32, i32) {                                   // R2
	fun mapped<U>(self, fn: |i32| U): (U, U) {
		(fn(self.0), fn(self.1))
	}
}
// (1, 2).mapped(|x| x * 10)
//   Error: cannot call method 'mapped' on (i32, i32)
```

A **trait** impl fares no better (R5, R6), and neither does the trait
impl std itself relies on:

```vilan
import std::operators::Add;
impl (i32, i32) with Add {
	fun add(self, b: (i32, i32)): (i32, i32) {
		(self.0 + b.0, self.1 + b.1)
	}
}
// (1, 2) + (3, 4)          →  R9:   4 / 6      — RUNS
// (1, 2).add((3, 4))       →  R10:  cannot call method 'add' on (i32, i32)
```

So [[B170]]'s "tuple impls are reachable" is precisely and only about
the **operator dispatch path**. The method-call path never looks at a
tuple receiver; a tuple has no methods, not even `len` (R27).

Three consequences, and they are the load-bearing ones for this paper:

1. **"Suite as methods" is not a variadic-generics question.** It is
   blocked one level lower, by a gap nobody has priced. Anyone who
   answers the owner's suite question with "make them methods" is
   proposing method resolution on tuple receivers *first*, then
   variadic generics *on top*, to get what a template gives for free.
2. **The comprehension is not competing with a method call**, because
   there is no method call. Revision 1's §4.5 framing ("saves four
   tokens") understated its own case: there is no rival spelling.
3. **A `.sum()` / `.fold()` termination on a tuple value is
   unreachable**, which removes one of the two candidate spellings for
   the fold form before the design starts (§R2.4).

### R1.3 The comprehension is still tuple-only, and says so twice

```
(x in o  => x + 1)   over Option<i32>  →  R7:  must be a mapped tuple, got Option<i32>
(x in xs => x + 1)   over List<i32>    →  R8:  must be a mapped tuple, got List<i32>
```

Same guard, same message. Generalizing `=>` to those types is a design
choice nothing forces, and §R3.3 argues against it.

### R1.4 Three corrections to revision 1

1. **Revision 1 §3.3's garbage run is CLOSED.** `(b in boxes => b.v + 1)`
   over `(Box<i32>, Box<str>)` printed `two1`; on `origin/next` it is
   refused with B174's message — "`+` on `U` needs `U: Add` — a
   parameter promises only what its bounds promise" (R16). Revision 1's
   **determination 9 is now historical**, and its owner question 7 is
   answered by [[B174]] closing on 2026-09-01. The differential fixture
   at `parse_differential.rs:219` (`fun t(): T { (x in xs => x + 1) }`)
   still carries the unbounded shape and should be re-read against the
   closed rule.
2. **Revision 1's determination 10 is discharged.** [[B180]] closed
   2026-09-01. "B183 must not ship before B180 closes" is satisfied;
   the zip form's stated blocker is gone.
3. **Revision 1 §4.5 and owner question 4 under-price the zip form.**
   They price it against a hand-written impl body. §R1.2 shows there is
   no method spelling at all, and §R1.1 shows the only reachable
   element-wise walk is unsound. The comprehension is not a convenience
   over a working alternative; over a *heterogeneous* tuple it is the
   only well-typed element-wise construct the language can have.

## R2. The suite, form by form

The rule that generates every row: **a tuple is fixed-arity and
heterogeneous, so every form is compile-time unrolled, and the only
question is whether the unroll is well-typed and whether the spelling
earns its place.** Below, `aa : (A0, A1, A2)`, and `E[a := aa.i]` is the
body with the binder substituted by the `i`-th element access.

| Form | Unrolls to | Result type | Expressible today | Verdict |
|---|---|---|---|---|
| **map** `(a in aa => E)` | `(E[a:=aa.0], E[a:=aa.1], E[a:=aa.2])` | `(τ0, τ1, τ2)`, `τi` = body's type at element `i` | by hand, repeating an index per element | **SYNTAX — the core** |
| **zip** `(a in aa, b in bb => E)` | `(E[a:=aa.0,b:=bb.0], …)`, arities equal | `(τ0, τ1, τ2)` | by hand, two indices to keep in step | **SYNTAX — the core** |
| **enumerate** | map with an extra compile-time `i32` constant in scope | `(τ0, τ1, τ2)` | by hand (R4) | **REFUSE — spelling collides with zip** |
| **fold** | left-nest `((init ⊕ aa.0) ⊕ aa.1) ⊕ aa.2` | a **scalar**, `τ` of the last step | by hand (R25); unsoundly via `for` (R13) | **NO NEW SYNTAX — it is the `for` loop** |
| **any / all** | fold with a `bool` accumulator, short-circuiting | `bool` | by hand (R14) | **NO NEW SYNTAX — it is a fold** |
| **filter** | *nothing* — arity is not statically known | undefined | no | **REFUSE, all four readings** |
| **flat_map** | `(..G(aa.0), ..G(aa.1), ..G(aa.2))` | the concatenation, arity `Σ` | **verbatim today** (R3) | **HOLD — one-token grammar extension later** |
| **chunk / windows** | pure arity surgery, no body | a tuple of tuples | no | **REFUSE — it is [[B3]]'s territory** |

### R2.1 map — the core, and the only form that must be built

```vilan
let aa = (1, "two");
let bb = (a in aa => wrap(a));
//  unrolls to:  (wrap(aa.0), wrap(aa.1))
//  types as:    (Wrapped<i32>, Wrapped<str>)   — body re-checked per element
```

The body is a **template**, elaborated once per element and type-checked
at that element's own type. The result is the `n`-tuple of the `n` body
types; heterogeneous in, heterogeneous out. Emission is an unrolled
tuple construction — no closure, no `.map`. This is revision 1 §4.1's
concrete arm, unchanged, and it stands.

Expressible today: yes, by writing `(wrap(aa.0), wrap(aa.1))`. **The
comprehension's whole value is that the index is written once instead of
`n` times** — which is where the hand-written form goes wrong, silently,
when the elements share a type.

### R2.2 zip — the core's second half

```vilan
let cc = (a in aa, b in bb => a + b);
//  unrolls to:  (aa.0 + bb.0, aa.1 + bb.1)
//  types as:    the 2-tuple of the two body types
```

All sources must be tuples of known arity, and all arities must be
**equal** — refuse otherwise, naming both sources and both arities
(revision 1 §4.2, unchanged). Abstract (mapped-pack) sources are refused
in a multi-binder comprehension because the tuple-bound system cannot
prove two arity ranges equal.

Same value as map, doubled: two indices that must stay in step. `self.2
+ b.1` is a typo the type checker cannot see when the elements share a
type, and the comprehension makes it unwritable.

### R2.3 enumerate — refuse, on spelling

The unroll is trivial: bind an extra name to a compile-time `i32`
constant, `0` at element 0 and so on, and elaborate the body per element
as usual. Result type: the `n`-tuple of body types. Implementation cost:
nearly zero once the concrete arm exists, because the index is already
known at the unroll site.

**The spelling is what kills it.** The obvious form —

```vilan
(i, a in aa => …)
```

— is one comma away from the zip form `(a in aa, b in bb => …)`, and a
reader parsing left to right cannot tell "index and element over one
source" from "element and element over two sources" until they reach the
second `in`, or its absence. An alternative keyword (`(a at i in aa =>
…)`) avoids the collision at the cost of a new keyword in an atom
position for a form that buys nothing: the index is a literal you can
already write.

**Refuse.** File the spelling as future work if a use appears.

### R2.4 fold / reduce — no new syntax; the answer is a sound `for`

The owner's `(a in aa => a).sum()` shape is **unreachable**: it needs a
method on a tuple value, and §R1.2 shows there are none at any arity.
That leaves two candidates.

**(a) A fold form inside the comprehension.**

```vilan
(acc = 0, a in aa => acc + a)
//  unrolls to:  ((0 + aa.0) + aa.1) + aa.2
```

It types: a **left fold with a changing accumulator type**, where
`acc_0 = init` and `acc_{i+1}` is the body's type at `acc_i` and element
`i`. The hand-written version proves it (R25 — accumulating
`(1, "two", true)` into a `str` runs and prints `1twotrue`, the
accumulator's type changing at each step).

It is still the wrong feature. It makes a form whose delimiters and name
say "tuple" sometimes produce a **scalar**, it introduces a second
binding shape (`acc = init`) into a production that has exactly one, and
it is a third comma-separated thing in a production already carrying zip
and (rejected) enumerate.

**(b) The `for` loop, made sound.** This is the recommendation.

```vilan
mut total = 0;
for x in aa {
	total = total + x;
}
```

Today this *runs* and is unsound (R12 gives `6` over `(1,2,3)`; R13
gives `1two3` over `(1,"two",3)`), because the binder is `any`. Under
§R1.1's second reading — **unroll the loop, check the body once per
element at that element's own type** — the homogeneous case keeps
working, the heterogeneous case refuses *at the element that fails*,
naming it, and the fold form needs no syntax at all. Short-circuit
(`jump break`, `ret`) falls out of the unroll, so `any`/`all` come free.

**This is the paper's one structural claim about the suite:** the
comprehension's per-element elaboration and a sound tuple `for` are the
*same machine*. Build it once and the language gets the whole
value-consuming half of the suite — fold, reduce, any, all, for_each —
with no new production, while closing a live defect.

### R2.5 any / all — a fold, therefore nothing

`(a in aa => p(a))` produces a `bool`-tuple; reducing it needs a
termination, and §R2.4 supplies one. Written directly today as
`p(aa.0) && p(aa.1)` (R14). No syntax.

### R2.6 filter — refuse, and the refusal is formal

Four readings, and the charge names two of them. All four fail:

1. **A tuple of a different arity.** A predicate over runtime values
   cannot fix an arity at check time, so there is no result *type* to
   write. This is not a difficulty; it is undefinability. Refuse.
2. **A `const` predicate fixing the arity.** `const` shipped
   (2026-07-10). A predicate that is const-evaluable per element does
   fix the arity — but the result *type* would then depend on a
   const-evaluation result, which is dependent typing entering by the
   back door, and the elaborator would have to run the const evaluator
   from inside type checking. Refuse; it prices as a language feature,
   not a comprehension form.
3. **A heterogeneous `Option`-tuple**, arity preserved:
   `(Option<A0>, Option<A1>, Option<A2>)`. This is **well-typed** — and
   it is *literally a map*: `(a in aa => if p(a) { Some(a) } else
   { None })`. It earns no syntax because the syntax already exists.
   Refuse as a form; document it as the answer to "I wanted filter".
4. **Collapse to a `List`.** Needs a join type over the elements.
   Vilan has no union types and no trait objects (`docs/spec/types.md`
   §5.11), so a join exists only for a homogeneous tuple — a form that
   works for `(i32, i32)` and refuses `(i32, str)` is worse than none.
   Refuse.

The formal statement is in §R3.2: a guard needs `mzero`/`mplus` at a
statically unknown grade, and a fixed-arity product has neither. Haskell
needed `MonadPlus` for exactly this and Scala 3's tuple suite ships
`Map`/`Zip`/`Concat` and **no filter**, for exactly this reason.

### R2.7 flat_map — already expressible verbatim; hold the sugar

The tuple-value spread `..e` (`docs/spec/types.md` §5.9) makes the
concatenation writable today, and it runs:

```vilan
fun twice(x: i32): (i32, i32) { (x, x) }
let ys = (..twice(xs.0), ..twice(xs.1));   //  R3 — (i32, i32, i32, i32)
```

Once the concrete arm exists, the natural spelling is a **spread body**:

```vilan
(a in aa => ..g(a))
//  unrolls to:  (..g(aa.0), ..g(aa.1))
//  types as:    the concatenation, arity = Σ arity(g(A_i))
```

Grammatically that is one change — the comprehension's body position
becomes an `entry` (§3.6's `entry = spread | expression`) rather than an
`expression`. The result arity is known because each `g(A_i)`'s arity is
known. It is the cheapest genuine addition in the suite and it is not
needed for the motivating case. **Hold**, behind the core, as a
one-line extension.

### R2.8 chunk / windows — [[B3]]'s territory, not this item's

`(a, b, c, d)` → `((a, b), (c, d))` has **no body**: there is no
per-element expression, only a re-shaping of the type. It is the
value-level twin of the type-level spread `(..T, U)` and `keyof`, both
already recorded as B3's future work in the spec (§5.9). Refuse from
B183; file to B3's tail if a use appears.

## R3. The monad question, honestly

### R3.1 What a tuple is, and why no closure can map it

A tuple type `(A0, …, A_{n-1})` is a **finite heterogeneous product**
indexed by position — a function from `Fin n` to types. That single fact
generates every answer below.

`fmap :: (a -> b) -> f a -> f b` needs `f` to have **one** element type.
A tuple has `n`. So the comprehension's map is not `fmap`; it is a
**natural transformation between indexed families**, taking a type-level
function `F` and a term-level family `∀i. A_i → F(A_i)`. And here is the
point:

> **The comprehension supplies that family by elaboration — the body is
> a syntactic template instantiated `n` times, once per index, checked
> at a different type each time. A closure cannot do this. A closure is
> a single value of a single type.**

This is why the question "syntax or method?" has a decisive answer, and
why the answer does not depend on [[B3]] at all. Variadic generics would
let you *write* `fun map<T: (..)>(t: T, f: ???)` — and then you would
have to write `???`, and there is no type there, because the argument
must be a different function at every index. Variadic generics widen
what a signature can *say*; they do not make one closure have `n` types.
A template is the only construct that does, and a template needs syntax.

Haskell hit the same wall from the other side: `instance Functor ((,) a)`
maps only the **second** component of a pair, because that is the only
position with a free type variable. The asymmetry is not an oversight;
it is the same fact.

### R3.2 Which laws hold, for which forms

| Law | Statement over tuples | Holds? |
|---|---|---|
| Functor identity | `(a in aa => a) ≡ aa` | **Yes**, definitionally under the unroll |
| Functor composition | `(b in (a in aa => f(a)) => g(b)) ≡ (a in aa => g(f(a)))` | **Yes** for pure `f`,`g`; effect order is left-to-right in both, so it survives effects |
| Applicative `pure` | `pure x = (x, …, x)` | **No** — arity-indexed; there is no single `pure`, so tuples are a *family* of applicatives (one per arity), not an Applicative |
| Lax monoidal (zip) | `zip` with unit `()` | **Yes, up to isomorphism** — associativity holds modulo `((a,b),c) ≅ (a,b,c)`, identity modulo `((),a) ≅ a`; vilan's `..e` makes the flattening writable but not automatic |
| Monad `join` | `join` on a tuple-of-tuples = concatenation | **Yes as a *graded* monad** — grade = arity, grading monoid `(ℕ, +)`; concatenation is associative with `()` as unit |
| Monad `>>=` | `m a → (a → m b) → m b` | **Not even well-typed** — `flat_map`'s result type is `concat(S_0,…,S_{n-1})`, not `T`'s type |
| MonadPlus (guards) | `mzero` / `mplus` at an unknown grade | **No** — the formal reason filter is refused (§R2.6) |

Read the table as a design brief rather than an ornament. The two rows
that hold **on the nose** are exactly the two forms recommended for
syntax. The rows that hold **only up to isomorphism or grading** are
exactly the forms recommended to hold (flat_map) or refuse (chunk). The
rows that **fail** are exactly the forms recommended to refuse (filter,
and any attempt to give the suite an Applicative-style interface). The
laws and the ergonomics agree, which is the sign the boundary is in the
right place.

Corollary worth stating in the spec: **because there is no `pure`,
nothing in the suite can be derived from a shared interface.** Every
form is an elaboration rule that must be written out. A "suite of
monadic transformations" over tuples is therefore not a suite in the
sense that word usually carries — there is no common abstraction the
members are instances of, only a list of separately-specified unrolls.
That is a strong reason to keep the list short.

### R3.3 Should `=>` generalize to `Option` / `Result` / `List`?

**No.** Over those types the comprehension buys no power and costs a
fourth spelling.

Each has exactly **one** element type, so the body is checked once and
the form collapses to a plain `fmap` — which is to say, to `.map`, which
ships. The template machinery that justifies the syntax on tuples has
nothing to do on a list.

And the surfaces it would collide with are all shipped:

- **`.map` / `.and_then` / `.filter` / `.zip` on `Option`**
  (`std/src/option.vl`) and the mirror set on `Result`. The Option monad
  already has bind, map, filter and zip as methods.
- **`e?.m…` — lift** (`docs/spec/types.md` §5.10). `o?.len()` *is*
  Option's map-and-flatten, with the flattening rule spelled out. A
  comprehension over `Option` would be a third way to write it.
- **`e!` — try-assert** (§5.10). This is the sequencing half of the
  Option/Result monad — vilan's `?`-operator analogue, dispatching
  through `Try`/`Verdict`. `!` and `?.` together cover bind and map;
  there is nothing left for a comprehension to do.
- **The iterator adapters** ([[I3]], shipped 2026-08-06):
  `map`, `filter`, `take`, `skip`, `enumerate`, `zip`, `chain`, `fold`,
  `for_each`, `count`, `any`, `all`, `rev`, `to_list` on `Iterator`, plus
  `map`/`filter`/`fold`/`for_each`/`sum`/`product` on `List`. A list
  comprehension would be a **fourth** spelling of map-and-filter.

There is also a governing precedent. I3's owner ruling of 2026-08-06
refused §4 option (ii) and fixed the principle as **"one meaning per
name, lazy spellings via `.iter()` only"**. A general comprehension is
that same question one level up: a second syntax for a meaning that
already has one. The ruling should carry.

**The asymmetry, stated once:** over a list the body has one type, so a
closure suffices and a method wins; over a tuple the body has `n` types,
so only a template works and syntax wins. Generalizing `=>` would apply
the tuple justification to the case where it does not hold.

### R3.4 What other languages did

| Language | Tuple / pack suite | What it teaches |
|---|---|---|
| **Python** | Comprehensions over any iterable, `if` guards, nested `for`; `zip()` is a function. Tuples are iterable and dynamically typed | Nothing transfers — there is no compile-time arity, so the heterogeneity problem never arises. `mypy` joins a heterogeneous tuple's elements, losing exactly what B183 wants to keep |
| **Haskell** | List comprehensions; `MonadComprehensions` (GHC 7.2, 2011) generalizes them to any monad. Tuples: `instance Functor ((,) a)` maps only the last component | **The strongest external evidence against "one syntax, a whole suite":** the generalization needed a *class per form* — `Monad` for the bind, `MonadPlus` for the guard, `MonadZip` for the parallel bind — and remains a rarely-used extension |
| **Rust** | No comprehensions. No tuple map. std implements traits for tuples up to arity 12 **by macro**; variadic generics remains unlanded after a decade of RFCs. The suite lives on `Iterator` | The negative control: given the choice, Rust took per-arity macro impls over syntax, and tuples got nothing. Vilan's [[B170]] just reached the same per-arity-impl place — and §R1.2 shows only the operator half of it |
| **Scala 3** | `Tuple.Map[T, F]`, `Tuple.Zip`, `Tuple.Concat`, `*:`; `tup.map(f)` typed by match types plus `inline` | The closest positive prior art, and it ships **map, zip, concat, take/drop/size — and no filter**, for exactly §R2.6's reason |
| **Swift 5.9** (SE-0393/0398) | Parameter packs: `(repeat f(each x))` is a pack-expansion expression in a tuple literal, elaborated per element. Multiple packs in one expansion **zip**, same-shape enforced | The owner's sketch, shipped, by a language that reached it independently — and it stopped at exactly these two forms |
| **C++17** | Fold expressions `(... + args)` over a parameter pack; `std::apply` + a fold is the tuple `for_each` idiom | The one language that gave the **fold** syntax rather than the map — and pays for it in diagnostics. Note it chose the *consuming* half; §R2.4 gives vilan that half through `for` instead |
| **TypeScript** | Mapped types over tuples: `{ [K in keyof T]: F<T[K]> }`. No value-level counterpart; `.map` over a tuple erases to an array | Vilan's `(U in T: F<U>)` **is** this, already. TS has the type half without the value half — the exact reverse of B183's gap, and evidence the two halves are separable |

**The reading.** Every language that shipped a statically typed tuple
suite shipped **map and zip and stopped** (Swift, Scala 3). The one that
generalized comprehensions monadically (Haskell) paid a class per form
for it. The one that chose the fold (C++) chose the consuming half, which
vilan can have from `for`. **Nobody shipped tuple filter.** The owner's
two forms are, empirically, the whole suite.

## R4. Recommendation

**Build map and zip. Refuse the rest. Fix the `for` loop.**

### R4.1 The minimal core, in order

Revision 1's four pieces stand, with one new piece ahead of them and
one blocker discharged.

0. **Fix `for x in tuple` (§R1.1).** Independent of B183, filable on
   its own, and it should not wait: the binder is `any`, the write in a
   `&mut` walk is silently discarded, and `any` launders through an
   annotation. Two acceptable outcomes — refuse the loop, or unroll it.
   **Prefer the unroll**, because it is the same elaboration the
   concrete arm needs and it delivers the suite's whole consuming half
   (§R2.4). If the order has no room for the unroll, ship the refusal
   now and unroll later; a refusal is forward-compatible with an unroll,
   and `any` is not.
1. **Spec the form.** `docs/spec/types.md` §5.9's one sentence becomes a
   subsection: the two arms, the typing rule for each, the emission
   note, and — new in revision 2 — **the refusals, written down**:
   filter, chunk, a non-tuple source, and unequal arities. A form whose
   boundary is documented does not get re-asked.
2. **Steer the two existing refusals** ("source must be a mapped tuple";
   the `got T` pack case), and add a steer for the suite's refusals:
   filter → "write the `Option` map"; `.sum()` on a tuple → the `for`
   loop.
3. **The concrete arm — map.** Per-element typing, unrolled emission,
   the result-shape rule, nesting falling out. Green negative: std
   `combine`'s emission byte-identical.
4. **The zip form.** [[B180]] closed 2026-09-01, so revision 1's
   blocker is discharged. Grammar production, the equal-arity refusal
   naming both spans, the abstract-source refusal, the [[B170]] exhibit
   as a corpus program.

### R4.2 What to refuse, and say so in the spec

- **filter, in all four readings** (§R2.6). The arity-preserving
  `Option`-tuple reading is a *map* and needs no syntax; the other three
  are undefinable, dependent-typed, or homogeneous-only.
- **enumerate** (§R2.3) — the spelling collides with zip at the comma,
  and the index is a literal you can write.
- **chunk / windows** (§R2.8) — no body, therefore not a comprehension;
  it is [[B3]]'s type-level territory.
- **A fold form inside the comprehension** (§R2.4) — it would make a
  tuple-shaped production sometimes yield a scalar. The `for` loop is
  the fold.
- **Generalizing `=>` to `Option`/`Result`/`List`** (§R3.3) — no power
  gained, a fourth spelling added, against I3's standing "one meaning
  per name" ruling.
- **The suite as methods on a tuple value** — blocked below variadic
  generics (§R1.2), and wrong in principle (§R3.1): the body is a
  template, not a closure.

### R4.3 What to hold, not refuse

- **A spread body** `(a in aa => ..g(a))` as flat_map (§R2.7) — one
  grammar token once the concrete arm exists, and the concatenation
  already types. Hold behind the core; it closes no doors either way.
- **Method resolution on a tuple receiver** (§R1.2) — a real gap,
  currently unfiled and unpriced. It is not needed for B183 and should
  not be bundled into it, but the owner should know it exists before
  anyone proposes tuple methods again.

### R4.4 Does the core still deliver `(a, b) + (c, d)`?

**Yes, and more cleanly than revision 1 could argue.**

```vilan
import std::operators::Add;
impl (i32, i32) with Add {
	fun add(self, b: (i32, i32)): (i32, i32) {
		(x in self, y in b => x + y)
	}
}
```

The operator dispatch path reaches this impl today (R9 runs `(1,2) +
(3,4)` → `4`/`6`), [[B180]] closed the operand check that revision 1
held it behind, and the zip body is the only piece missing. Each arity
still writes its own `impl` block — this is not variadic generics and
must not be sold as such — but the *body* is written once per arity
without repeating an index.

Two corrections to revision 1's pricing (§4.5, "saves nothing at arity
2, pays from arity 4"):

- The rival it priced against does not exist. There is no `self.map(…)`
  and no `self.zip(b).map(…)`; a tuple has no methods (§R1.2). The
  comprehension is not a shorter way to write something; over a
  heterogeneous tuple it is the only well-typed way.
- The other reachable element-wise walk — `for x in self` — is
  **unsound** (§R1.1). Pricing the comprehension against it was pricing
  it against a defect.

## R5. The desugarings, pinned

Every form, as source → unroll → type. These are the examples the spec
subsection should carry.

```vilan
// Given:
let aa: (i32, str)  = (1, "two");
let bb: (i32, str)  = (10, "!");

// --- map: BUILD ---------------------------------------------------------
(a in aa => wrap(a))
//  ⇒  (wrap(aa.0), wrap(aa.1))
//  :  (Wrapped<i32>, Wrapped<str>)          body checked twice, at i32 and str

// --- zip: BUILD ---------------------------------------------------------
(a in aa, b in bb => a + b)
//  ⇒  (aa.0 + bb.0, aa.1 + bb.1)
//  :  (i32, str)                            arities must be EQUAL, else refuse

// --- flat_map: HOLD (one grammar token) ---------------------------------
(a in aa => ..g(a))
//  ⇒  (..g(aa.0), ..g(aa.1))
//  :  the concatenation; arity = Σ arity(g(A_i))
//     writable TODAY as the right-hand side, without the sugar

// --- filter: REFUSE -----------------------------------------------------
(a in aa if p(a) => a)
//  ⇒  nothing — a runtime predicate does not fix an arity
//     the arity-preserving reading IS a map, so write it:
(a in aa => if p(a) { Some(a) } else { None })
//  ⇒  (if p(aa.0) {…} else {…}, if p(aa.1) {…} else {…})
//  :  (Option<i32>, Option<str>)

// --- fold: NO NEW SYNTAX — this is the `for` loop -----------------------
mut total = "";
for a in aa {                    // UNROLLED, body checked per element
	total = total + a.to_string();
}
//  ⇒  { total = total + aa.0.to_string(); total = total + aa.1.to_string(); }
//  :  str                                   a scalar, not a tuple
//     TODAY: the binder is `any` and this is unsound (§R1.1)

// --- enumerate: REFUSE (spelling) ---------------------------------------
(i, a in aa => (i, a))
//  ⇒  ((0, aa.0), (1, aa.1))     — types fine; the COMMA collides with zip
//  :  ((i32, i32), (i32, str))

// --- chunk: REFUSE (no body; B3's territory) ----------------------------
//  a re-shaping of the TYPE with no per-element expression
```

## R6. Probe ledger — revision 2

Twenty-six programs against a debug build of `vilan 0.40.0 (635e37289)`
(`origin/next` at the lane's start). **Twelve ran, fourteen were
refused.** Sources are in the lane scratchpad.

**Ran (12).**

| # | What it shows | Output |
|---|---|---|
| R1 | **`for x in (1,"two",true) { print(x + 1) }`** — the loop exists, binder is `any` | `2` / **`two1`** / `2` |
| R3 | **flat_map by hand** — tuple-value spread over per-element results | `2` (the 4th element) |
| R4 | enumerate by hand — `((0, xs.0), (1, xs.1))` | `1` / `b` |
| R9 | [[B170]]'s tuple `Add` impl through the **operator** path | `4` / `6` |
| R12 | fold via `for` over `(1,2,3)`, homogeneous | `6` |
| R13 | **GARBAGE RUN** — the same fold over `(1,"two",3)` | **`1two3`** |
| R14 | `all`/`any` by hand over a `bool` tuple | `false` / `true` |
| R17 | **SILENT NO-OP** — `for e in &mut xs { e = e + 1 }`; emits `__replace(e, e+1)` on a JS number | `1` / `2` — **unchanged** |
| R18 | **`any` launders into `str`** — `let s: str = x` from the loop binder | **`undefined`** / `3` |
| R19 | the shipped abstract arm's emission — `boxes.map((b) => b[0])` | `1` / `two` |
| R24 | the zip form's unroll, hand-written | `11` / `two!` |
| R25 | **heterogeneous fold by hand** — accumulator type changes per step | `1twotrue` |

**Refused (14).**

| # | What it shows | Diagnostic (head) |
|---|---|---|
| R2 | **inherent impl on `(i32,i32)`, method by name** | `cannot call method 'mapped' on (i32, i32)` |
| R5 | **trait impl on `(i32,i32)`, method by name** | `cannot call method 'doubled' on (i32, i32)` |
| R6 | trait impl taking a closure — the "tuple method" route | `cannot call method 'map_pair' on (i32, i32)` |
| R7 | the comprehension over `Option` | `must be a mapped tuple, got Option<i32>` |
| R8 | the comprehension over `List` | `must be a mapped tuple, got List<i32>` |
| R10 | **[[B170]]'s own impl, called by method name** | `cannot call method 'add' on (i32, i32)` |
| R11 | the same through `Add::add(..)` | bare trait type — unrelated, recorded for completeness |
| R15 | `for e in &mut xs { *e = *e + 1 }` | `cannot assign through '*'` — the steer, then R17 |
| R16 | **revision 1 §3.3's garbage run, re-run** | `` `+` on `U` needs `U: Add` `` — **[[B174]] closed it** |
| R21 | the zip form's parse verdict | `found ',' expected '=>'` |
| R22 | a filter guard `(a in aa if p => a)` | `found 'if' expected '=>'` |
| R23 | `for p in ((1,2),(3,4)) { p.0 }` — field access on the `any` binder | `cannot access field '0' on type any` |
| R26 | method call on the `any` binder | `cannot call method 'len' on any` |
| R27 | **a tuple has no methods at all** | `cannot call method 'len' on (i32, str, bool)` |

## R7. Determinations — revision 2

1. **The suite is map and zip.** Nothing else in the owner's list earns
   syntax: filter cannot fix an arity, fold produces a scalar and is the
   `for` loop, any/all are folds, enumerate collides with zip at the
   comma, flat_map is the tuple-value spread, and chunk has no body and
   belongs to [[B3]].
2. **Tuples are not a monad, and the precise failure is `pure`.** A
   fixed-arity product has an arity-indexed `pure`, so it is a *family*
   of applicatives, not an Applicative; `flat_map` is well-typed only as
   a **graded** monad over `(ℕ, +)`; the ordinary `>>=` signature does
   not type at all. Functor identity and composition hold on the nose
   for map — which is exactly the form recommended for syntax.
3. **The laws and the ergonomics agree.** The two forms that satisfy
   their laws on the nose are the two recommended; the ones that hold
   only up to isomorphism are the ones held; the ones that fail are the
   ones refused. That agreement is the evidence the boundary is right.
4. **No `pure` means no shared interface**, so a "suite" over tuples is
   a list of separately-specified unrolls, not instances of one
   abstraction. A strong reason to keep the list at two.
5. **`=>` must not generalize to `Option`/`Result`/`List`.** Those have
   one element type, so the body is checked once and the form collapses
   to `.map` — which ships, alongside `?.` (lift), `!` (try-assert) and
   I3's fourteen iterator adapters. It would be a fourth spelling,
   against I3's standing "one meaning per name" ruling.
6. **NEW DEFECT — `for x in tuple` binds `any`.** The loop exists,
   is undocumented, and is unsound three ways: `x + 1` over
   `(1,"two",true)` prints `two1`; `let s: str = x` prints `undefined`;
   `for e in &mut xs { e = e + 1 }` compiles, runs and discards the
   write. `iterable_element_type` has no `Type::Tuple` arm and takes the
   `Any` give-up default written for empty lists. The spec says `any` is
   "produced at host boundaries" — a tuple literal is not one.
   **Filable independently of B183.**
7. **NEW FIND — a tuple receiver has no method resolution at any
   arity.** Inherent impls, trait impls and [[B170]]'s own `Add` impl
   are all unreachable by method name; only the operator dispatch path
   reaches a tuple impl. "Suite as methods" is therefore blocked one
   level below [[B3]], by a gap nobody has priced.
8. **The comprehension earns syntax for a reason independent of
   [[B3]].** Its body is a *template instantiated n times, checked at n
   types*; a closure is one value of one type. Variadic generics widen
   what a signature can say; they cannot make one closure have `n`
   types. This is a stronger argument than revision 1's and it does not
   depend on the variadic tail ever landing.
9. **The fold's answer is a sound `for` loop, not a new form.** The
   per-element unroll the concrete arm needs is the same elaboration a
   sound tuple `for` needs; building it once delivers fold, reduce,
   any, all and for_each with no new production, and closes
   determination 6's defect in the same stroke.
10. **Revision 1's determination 9 is historical** — [[B174]] closed
    2026-09-01 and its §3.3 garbage run now refuses (R16). Revision 1's
    owner question 7 is answered.
11. **Revision 1's determination 10 is discharged** — [[B180]] closed
    2026-09-01; the zip form's stated blocker is gone.
12. **Revision 1 under-priced the zip form.** It priced against a
    hand-written impl body, but there is no method spelling at all
    (determination 7) and the only reachable element-wise walk is
    unsound (determination 6). Over a heterogeneous tuple the
    comprehension is not a convenience — it is the only well-typed
    element-wise construct the language can have.
13. **The census says two forms.** Swift 5.9's pack expansion and Scala
    3's `Tuple.Map`/`Zip` are the two shipped statically typed tuple
    suites, and both stopped at map and zip. Haskell's monad
    comprehensions needed a class per form. Nobody shipped tuple filter.

## R8. Owner questions — revision 2

Only where a decision changes the design.

1. **The suite: map and zip, and the rest refused?** The paper
   recommends building exactly the two forms you named and writing the
   refusals into the spec — filter (all four readings), enumerate (the
   comma collides with zip), chunk (no body; [[B3]]), and a fold form
   inside the comprehension (it would make a tuple-shaped production
   yield a scalar). Confirm the boundary, or name the one you want
   priced?

2. **The fold: is a sound `for x in tuple` the right answer?** Today
   that loop binds `any` and prints `1two3` over `(1,"two",3)`. The
   paper wants it **unrolled** — the body checked once per element at
   that element's own type — which gives fold, reduce, any, all and
   for_each with no new syntax and closes the defect. The alternative is
   to **refuse** the loop outright and leave the consuming half to
   positional access. Unroll, or refuse?

3. **The `for`-over-tuple defect: file it now, separately?** It is
   independent of B183 and unsound three ways (`two1`; `let s: str = x`
   → `undefined`; a `&mut` walk that silently discards the write). It is
   a spec violation — `any` is specified as "produced at host
   boundaries" and a tuple literal is not one. File as its own item
   ahead of the B183 work, or fold it into the concrete arm's lane?

4. **`=>` stays tuple-only?** Generalizing to `Option`/`Result`/`List`
   buys no power — those have one element type, so the body is checked
   once and the form *is* `.map` — and adds a fourth spelling beside
   `.map`, `?.`, `!` and I3's adapters, against I3's standing "one
   meaning per name" ruling. Is that ruling meant to carry here, or do
   you want the general comprehension priced anyway?

5. **The tuple-method-resolution gap: do you want it filed?** A tuple
   receiver resolves no methods at all — not an inherent impl, not a
   trait impl, not [[B170]]'s own `Add` impl by name. It is not needed
   for B183 and the paper does not bundle it, but it is the real reason
   "make the suite methods" cannot be answered by [[B3]] alone. File it,
   or leave it in this paper's record?

6. **flat_map's spread body — hold or build with the core?** `(a in aa
   => ..g(a))` is one grammar token once the concrete arm exists (the
   body position becomes an `entry`), and the concatenation already
   types — `(..g(aa.0), ..g(aa.1))` runs today. The paper holds it
   behind the core because the motivating case does not need it. Hold,
   or take it in the same lane?

---

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
