# The generic left operand — the estate census behind B174's breaking step

> **Status: CENSUS 2026-09-01**, ruling awaited (work order 24, lane
> papers; tracker item [[B174]]). This is a numbers paper, not a design
> paper: [[B179]]'s operand-role ruling already settled the *semantics*,
> and [[B169]] and the b179 lane closed the right-operand family. What
> was deferred was the LEFT operand, on the stated ground that refusing
> it "is a bound requirement on every such default — the breaking
> generics change b148's SCOPE note deferred", and that closing it
> "needs the deliberate breaking step (census the estate's trait defaults
> first)."
>
> **This is that census, and the number is one.**
>
> One trait default in the entire estate writes a native operator over
> its trait's own unbounded parameter. It is a compiler test fixture. The
> only other unbounded-left-operand site in the estate is **the
> `#[ignore]`d pin that asserts the refusal** — which the change turns
> green rather than breaks. Total migration: **one `<T>` → `<T: Add>`
> edit and one `#[ignore]` removed.** No std change, no corpus change, no
> docs change, no kolt or website change.
>
> The census also found that **the spec already prescribes the bound**
> (`docs/spec/types.md:653` and the prose at `:632-633`), so B174 makes
> the specification true rather than changing it.
>
> And it found one thing the ruling must decide that the item does not
> name: **"require a bound" is not the same rule as "require the RIGHT
> bound"**, and today a wrong bound is as good as none (§6, P4).
>
> Estate swept mechanically at `vilan` @ `f30897ee`, kolt and the website
> at their live checkouts (both read-only); worktree clones excluded.
> Behaviour probed against a debug build of `vilan 0.40.0 (f30897ee0)`.

## 1. What was counted

**The hit shape.** Inside a `trait` declaration's **default-bodied**
member (a `fun` with a body written in the trait itself, not in an
`impl`), an expression applying a native operator where the LEFT
operand's static type is a generic parameter of the trait, or `Self`, or
an associated binder — and that parameter carries **no bound that admits
the operator**. The canonical shape, from the item:

```vilan,fragment
trait Doubler<T> {
	fun once(self): T;
	fun twice(self): T { self.once() + self.once() }   // ← the shape
}
```

**Why trait defaults specifically.** This is the *breaking* half. A free
function that hits the same refusal is fixed by editing its own
parameter list — `fun bump<T>` becomes `fun bump<T: Add>`, a local edit
with no consequences. A trait default cannot be fixed locally: adding a
bound to the trait's parameter changes the **trait**, and therefore every
`impl` of it and every bound that names it. That asymmetry is why the
item asked for the trait-default number.

**The operator set, corrected.** The charge named 21 operators. **Five of
them do not exist in vilan.** `is_assignment_operator`
(`parsing.rs:696-698`) accepts exactly `=  +=  -=  *=  /=  %=`; there is
no `&=`, `|=`, `^=`, `<<=`, `>>=` in the grammar and zero occurrences in
the estate. The real set is **16 binary** (`+ - * / % << >> & ^ | == != <
<= > >=`) **plus 5 compound**, the compound forms inheriting their base
trait (pinned at `platform.rs:5366`).

**Method.** Every `.vl` file; every fenced block in `.md` — the
`vilan`-tagged fences, the `vilan,fragment` ones, and bare fences alike;
and every vilan source embedded in
Rust — both `r#"…"#` raw strings and ordinary escaped `"…\n…"` literals,
with `{{`/`}}` format-brace unescaping. Trait headers located by regex,
bodies by brace matching, members split into abstract (`;`-terminated)
versus default-bodied, and every default body screened for the operator
set. Then, for the second surface (§5), every construct declaring an
unbounded generic parameter was enumerated and **all 110** of its
operator-bearing lines classified by hand.

## 2. Population

| Bucket | Trait declarations | Default-bodied members |
|---|---|---|
| std (`vilan/std/`) | 42 | 35 |
| macro_std | 0 | 0 |
| test corpus (`vilan/test/`) | 9 | 4 |
| examples + benchmarks | 0 | 0 |
| docs fences (`vilan/docs/**.md`) | 31 | 5 |
| crates Rust fixtures (`crates/`) | 377 | 66 |
| project templates (`crates/vilan-cli/templates/`) | 0 | 0 |
| kolt (read-only) | 0 | 0 |
| vilan-website (read-only) | 0 | 0 |
| vilan-playground | 0 | 0 |
| **Total** | **459** | **110** |

Two of the 375 grep-level `trait X {` lines in `crates/` are genuine
**Rust** traits, not embedded vilan, and were excluded:
`vilan-core/src/interpreter.rs:255` (`pub trait AssetReader`) and
`vilan-cli/src/main.rs:752` (`trait CommandFailure`).

**One bucket boundary, declared.** The docs figure counts **every** fence
in `vilan/docs/**.md`, including bare ones. Restricting strictly to
`vilan`-tagged fences drops the docs trait count from 31 to ~19. **The
hit count is 0 either way**, so the boundary does not move any number
this paper is arguing from.

Three buckets are worth stating explicitly because they are the ones the
owner would most fear: **kolt declares no traits at all** (19 `.vl`
files; the word `trait` never appears), **the website declares none** (30
`.vl` files), and **the templates declare none** (5 `.vl` files). The
applications are entirely unexposed to this change.

## 3. The hits — one

| # | file:line | Trait | Member | Expression | Parameter / bound |
|---|---|---|---|---|---|
| 1 | `crates/vilan-core/tests/inference/macros.rs:3522` | `Doubler<T>` (decl `:3518`) | `twice` (decl `:3521`) | `self.once() + self.once()` | `T` — **unbounded** |

Per bucket: std **0**, macro_std **0**, test corpus **0**, examples +
benchmarks **0**, docs fences **0**, crates fixtures **1**, templates
**0**, kolt **0**, website **0**, playground **0**.

**Breaking surface = 1 site.**

### 3.1 The site, in full

`crates/vilan-core/tests/inference/macros.rs` — `#[test]` at `:3512`,
`fn an_inherited_default_on_a_generic_subject_dispatches()` at `:3513`,
raw string opening `:3516`, asserting output `"42\n"` at `:3537`. The
docstring at `:3505-3511` attributes it to B14's slice —
`resolve_inherited_default` matching generic impl subjects nominally. The
embedded program:

```vilan
import std::io::print;

trait Doubler<T> {
	fun once(self): T;

	fun twice(self): T {
		self.once() + self.once()
	}
}

struct Holder<T> {
	value: T,
}

impl Holder<type T> with Doubler<T> {
	fun once(self): T {
		self.value
	}
}

fun main() {
	print(Holder { value = 21 }.twice());
}

main();
```

**It works by luck.** P1 reproduces it: `42`. P2 instantiates the *same
trait default* at `str` and gets the garbage the item is about:

```vilan,fragment
fun main() { print(Holder { value = "ab" }.twice()); }   //  →  abab
```

So the one fixture in the estate that carries the shape is one type
argument away from demonstrating the bug it is silently relying on.

### 3.2 Its fix spelling

```diff
-trait Doubler<T> {
+import std::operators::Add;
+
+trait Doubler<T: Add> {
 	fun once(self): T;
 	fun twice(self): T { self.once() + self.once() }
 }
```

`Add` is `std/src/operators.vl:31`. P3 confirms it compiles and still
prints `42`. The test's purpose — that an inherited default dispatches on
a generic impl subject — is untouched; the bound is orthogonal to what it
asserts.

## 4. What the refusal would say

The right-operand family already has excellent, fully-reasoned wording,
shipped by the b179 lane. P5 shows it:

> `+` adds two values of the same type, but the operands are `i32` and
> `T`: `T` is wider than what `i32`'s `add` accepts. That set is `i32`
> itself, and no trait names it, so no bound on `T` can prove membership
> — a bound promises a trait's methods, never that the parameter IS
> `i32`. Convert the value explicitly and declare the operand `i32`, or
> put a left operand there whose `Add` declares a `B` that admits `T`.

The left operand's refusal is a **different and simpler** message,
because the left operand is exactly where a bound *does* work — that is
[[B179]]'s ruling, that the operator belongs to the left operand. Proposed:

> `+` dispatches through its LEFT operand, but `T` is an unbounded
> generic parameter, so there is no `add` to dispatch to. Bound it with
> the operator's trait — `<T: Add>` — or write a concrete type here.

with the trait-parameter case naming where the parameter is declared:

> …`T` is declared without a bound on `trait Doubler` here.

Per-operator, the bound named in the steer comes from
`operator_trait_method` (`analyzer.rs:3398-3422`) — §6's table.

## 5. The second surface — non-breaking, and it is empty

B174's fix refuses the shape *wherever* it appears, not only in trait
defaults. So the honest total is the trait-default count plus every other
site that would newly refuse. Every construct in the estate declaring an
unbounded generic parameter was enumerated, all 110 of its
operator-bearing lines classified by hand, and separate passes run over
every generic-typed closure parameter and every tuple comprehension.

| Bucket | Free fns + inherent-impl methods | Closures | Comprehensions |
|---|---|---|---|
| std | 0 | 0 | 0 |
| macro_std | 0 | 0 | 0 |
| test corpus | 0 | 0 | 0 |
| examples + benchmarks | 0 | 0 | 0 |
| docs fences | 0 | 0 | 0 |
| crates fixtures | **1** | 0 | 0 |
| templates | 0 | 0 | 0 |
| kolt | 0 | 0 | 0 |
| website | 0 | 0 | 0 |
| playground | 0 | 0 | 0 |

**The one is the pin itself.**
`crates/vilan-core/tests/inference/platform.rs:5704` —
`fun bump<T>(value: T): T { value + 1 }` — is the body of
`fn an_unbounded_generic_left_operand_of_addition_is_rejected()` (`:5685`),
carrying `#[ignore = "B174: an unbounded generic LEFT operand still
escapes the check…"]` at `:5682-5684`. **Closing B174 un-ignores it
rather than breaking it.** The non-breaking migration cost is nil.

Three near-misses are **already refused** today (right-operand shape,
closed by B169/B179 — not new refusals):
`platform.rs:4837` (`"v=" + value`, asserted to fail, *"has no string
form"*), `platform.rs:4857` (`total + value`, asserted to fail), and
`docs/spec/types.md:644`, a doc fragment already annotated
`// error: 'T' is unbounded`.

The remaining 106 operator-bearing lines have operands that are `i32`
(indices, cursors, generation counters, refcounts — `arena.vl`,
`list.vl`, `iterator.vl`, `rpc.vl`, `reactive.vl`), `bool`, or a
`str`-typed struct field (`Boxy<T> { value: T, tag: str }`, where
`self.tag + ".map"` is `str + str`), or are scan artifacts — signature
lines carrying `&mut T` / `Option<T>`, unary `*` and `&`, `=>` arrows,
closure pipes. **Zero have a `T`-typed operand.**

**Comprehensions and closures are clean.** All seven tuple comprehensions
in the estate (`reactive.vl:700`, `:705`; `test/spread-parameters.vl:37`,
`:39`; `tuples.rs:2318`; `modules.rs:469`; `borrows.rs:375`) apply no
native operator to a binder — std's `combine` and its sibling `gather`
contain method calls only. One near-hit deserves recording as a
**control**, not a hit: `std/src/browser/ui.vl:446`, inside
`source.effect(|value: T| { … previous == value … })`, under
`fun swap<T: PartialEq, S: Source<T>>` (`ui.vl:431`) — std **already
spells the operator's bound** for a `T`-vs-`T` comparison in a closure
body, and the doc comment at `:417` says why. That is the house style
B174 would make mandatory.

**One companion paper's find, ruled out.** The tuple-comprehension paper
([`tuple-comprehension.md`](tuple-comprehension.md) §3.3) reports a
garbage run — `(b in boxes => b.v + 1)` over a heterogeneous pack printing
`two1` — and flagged it as a possible B174 hit. It is the same *shape* but
**not an estate site**: the program is that paper's own probe, and the
syntactically identical fixture at `parse_differential.rs:219`
(`("tuple_comprehension", "fun t(): T { (x in xs => x + 1) }")`) feeds
only `all_sources()` and the token/formatter round-trip — the analyzer
never runs on it, `xs` is an unresolved free identifier and nothing binds
`x` to a generic. Its twin at `parsing.rs:6596` is the same story.
**Neither counts.** But the probe stands as evidence that the shape is
reachable from the comprehension body, and B174's fix would cover it.

## 6. The `Ordering` question, settled — and the one the ruling must decide

### 6.1 `compare.vl` is out of scope, flatly

An earlier reading flagged `std/src/compare.vl`'s `PartialOrd`/`Ord`
defaults as possible hits, because they apply `<`, `<=`, `>`, `>=` inside
trait defaults. **They do not qualify**, and the paper states it without
hedging:

- `:13-17` — `enum Ordering { Less = -1, Equal = 0, Greater = 1 }`, a
  concrete backed enum.
- `:19` `trait PartialOrd<B = Self> with PartialEq<B>`; `:20`
  `fun partial_compare(self, b: B): Option<Ordering>`.
- `:23, :27, :31, :35` — `lt`/`le`/`gt`/`ge`. The operand `x` is bound by
  `is Some(let x)` destructuring `Option<Ordering>`, so `x: Ordering`.
  The parameter `B` reaches only `self.partial_compare(b)`, never an
  operator.
- `:39` `trait Ord with Eq + PartialOrd`; `:40` `fun compare(self, b:
  Self): Ordering`. At `:43, :51` — `min`/`max` — the operand is
  `self.compare(b)`, i.e. `Ordering`. **`Self` never appears as an
  operand.**
- `:58` `clamp` — no operator at all.

**B174 does not touch `compare.vl`.** Noted in passing: there is no
`impl Ordering with PartialOrd` anywhere in std, so those six comparisons
are native-on-a-backed-enum resolved by discriminant — a separate
question, unaffected either way.

### 6.2 "A bound" versus "the RIGHT bound" — the ruling's real content

The item says the fix is "a bound requirement". The census found that is
under-specified, and P4 shows why:

```vilan,fragment
import std::display::Display;
trait Doubler<T: Display> {              // ← a bound, but not Add
	fun once(self): T;
	fun twice(self): T { self.once() + self.once() }
}
// Holder { value = "ab" }.twice()  →  abab
```

A bound of `Display` — which does not provide `add` — leaves the shape
**exactly as broken as no bound at all**. The carrier is
`analyzer.rs:33435-33458`: the `provides` check only *records* a
dispatch, and a bound that does not provide the operator's method falls
through to the **same native emission** as an unbounded parameter. There
is no else-refuse on the left side.

So the ruling has to choose:

- **"Require a bound"** — cheap, and closes the item as written, but
  leaves P4's `<T: Display>` compiling to concatenation. That is a
  smaller hole than today's, and still a hole.
- **"Require a bound that provides the operator's method"** — the real
  fix, and the one that matches the right operand's existing posture:
  `platform.rs:5335` (`T: Display` with `+`) and `:5497` (`T: Display`
  with `==`) are both already asserted to **fail** on the right. Today
  the two sides disagree about what a bound has to prove.

**The paper recommends the second**, on the ground that the first leaves
the estate's single hit fixable by a bound that does not fix it, and that
the asymmetry with the right operand is itself a defect.

### 6.3 Which bounds are nameable

From `operator_trait_method` (`analyzer.rs:3398-3422`):

| Operator | Trait | Declared at |
|---|---|---|
| `+` | `Add` | `std/src/operators.vl:31` |
| `-` | `Sub` | `:37` |
| `*` | `Mul` | `:43` |
| `/` | `Div` | `:49` |
| `%` | `Rem` | `:55` |
| `<<` | `Shl` | `:61` |
| `>>` | `Shr` | `:67` |
| `&` | `BitAnd` | `:73` |
| `^` | `BitXor` | `:79` |
| `\|` | `BitOr` | `:85` |
| `==`, `!=` | `PartialEq` | `std/src/compare.vl:3` (`!=` dispatches to `eq`, negated by the transformer — `analyzer.rs:3410-3412`) |
| `<`, `<=`, `>`, `>=` | `PartialOrd` | `std/src/compare.vl:19`, via `lt`/`le`/`gt`/`ge` (`analyzer.rs:3413-3419`) |

The 5 compound forms inherit their base trait (`platform.rs:5366` pins
`fun bump<T: Add>(…) { total += value; }`).

**Two operators have no nameable bound: `&&` and `||`.** They fall to
`_ => None` at `analyzer.rs:3420`; `BinaryOp::And`/`Or`
(`node.rs:1132-1136`) are bool-only and non-overloadable. If a default
ever wrote `a && b` over an unbounded `T` there would be **no writable
fix** — the author would have to change the type. **Estate census: zero
such sites**, so it is a theoretical gap, but the ruling should say what
the refusal tells that author. (Related, and already filed: [[B181]]
covers `&&`/`||` from the B179 arc.)

## 7. The spec already says this

The strongest single argument for taking the breaking step is that the
normative specification **already prescribes the bound**, and the
compiler does not enforce it.

`docs/spec/types.md:653`:

```vilan,fragment
fun sum<T: Add>(first: T, second: T): T { first + second }  // the parameter is on the LEFT
```

and the prose at `:632-633`:

> A parameter on the LEFT is a different question: there the bound
> selects an impl and the operator dispatches through it, which is what
> `T: Add` is for.

**B174 makes the spec true rather than changing it.** That reframes the
"breaking generics change" from a policy decision into a conformance fix
— and the census says the conformance gap is one fixture.

Two further precedents show the policy is already house law elsewhere:

- **Vilan already refuses a trait default that requires an undeclared
  bound.** `crates/vilan-core/tests/inference/iterators.rs:2865` pins
  `trait Walk<T> { … fun to_set(mut self): Set<T> { … } }` as
  `assert_fails_with("generic parameter 'T' is missing the bound ':
  Hashable'")`. Same policy shape, already shipped, for methods.
- **And it refuses a member call on an unbounded parameter.**
  `std_surface.rs:1671-1693` pins `trait Holder<T> { fun describe(self):
  str { self.item().label() } }` failing with `"cannot call method
  'label' on T"`.
- Std's own comments treat it as settled law: `std/src/set.vl:99-101`
  and `std/src/map.vl:102-103`.

**Operators are the only remaining escape from the unbounded-parameter
check inside a trait default.**

## 8. The control set — what is already spelled correctly

~29 sites already carry the bound and would not break. The representative
ones, by bucket:

| Bucket | Sites | Examples |
|---|---|---|
| std | 2 | `math.vl:40` `minmax<T: Ord>` (`a <= b`); `browser/ui.vl:446` `swap<T: PartialEq>` (`previous == value`) |
| test corpus | 3 | `generic-equality.vl:15` `<T: PartialEq>` (`a == b`), `:23` (`a != b`); `numeric-types.vl:22` `halve<T: Div>` (`value / divisor`) |
| docs | 1 live + 5 error-annotated fragments | `types.md:644-653` |
| crates fixtures | ~23 | `macros.rs:1969` `<T: Div>`, `:1970` `<T: Shr>`, `:1971` `<T: BitAnd>`, `:2050` `<T: Add>`; `platform.rs:4442` `<T: PartialOrd>`; `generics.rs:751`, `platform.rs:1175`, `:1256`, `tuples.rs:978` `<T: PartialEq>`; and `platform.rs:5725` `<T: Add>` — the left-operand one |
| kolt / website / playground / examples / benchmarks / macro_std / templates | 0 | kolt has only two generic constructs at all (`prefs.vl:34`, `:53`, `impl StorageSignalCell<type T>`), neither containing an operator; the website and playground declare zero generics |

Four trait defaults apply an operator with a **bounded** trait parameter
in scope — `std_surface.rs:1712`, `:1772`, `:1807`, and
`docs/tour/data-and-traits.md:235` — but in all four the operator's
**left** operand is already `str`, so they are controls for "bounded
parameter plus operator in a default", not for the `T op T` shape.

## 9. Probe ledger

Five programs against a debug build of `vilan 0.40.0 (f30897ee0)`.
Sources are in the lane scratchpad.

| # | What it shows | Result |
|---|---|---|
| P1 | **The one hit**, reproduced verbatim at `i32` | `42` — works by luck |
| P2 | The **same trait default** instantiated at `str` | **`abab`** — the garbage run |
| P3 | **The fix spelling** `trait Doubler<T: Add>` | `42` — compiles, unchanged behaviour |
| P4 | **The scope caveat** — `<T: Display>`, a bound that does not provide `add` | **`abab`** — a wrong bound is as good as none |
| P5 | The **right-operand control**, already refused (b179's wording) | *"`+` adds two values of the same type… no bound on `T` can prove membership…"* |

## 10. Determinations

1. **The breaking surface is ONE site**:
   `crates/vilan-core/tests/inference/macros.rs:3522`, `trait Doubler<T>`'s
   `twice`. Not in std, not in the corpus, not in docs, not in examples
   or templates, and not in kolt or the website — the applications
   declare no traits at all.
2. **The non-breaking surface is ZERO live sites.** The only other
   unbounded-left-operand site in the estate is the `#[ignore]`d B174 pin
   (`platform.rs:5704`), which the change turns **green**.
3. **Total migration: one `<T>` → `<T: Add>` edit plus one `#[ignore]`
   removed.** The test's purpose is untouched.
4. **The item's premise — that this is a large breaking change — does not
   survive the census.** The fear was reasonable and the number is one.
5. **The spec already prescribes the bound** (`docs/spec/types.md:653`,
   prose at `:632-633`). B174 makes the specification true rather than
   changing it.
6. **The policy is already house law for methods**: a trait default
   requiring an undeclared bound is refused (`iterators.rs:2865`,
   `'T' is missing the bound ': Hashable'`), as is a member call on an
   unbounded parameter (`std_surface.rs:1671`). **Operators are the only
   remaining escape.**
7. **The operator set is 16 binary + 5 compound, not 21.** `&= |= ^=
   <<= >>=` do not exist in the grammar (`parsing.rs:696-698`).
8. **`compare.vl` is out of scope**, settled flatly in §6.1: every
   operand in `PartialOrd`/`Ord`'s defaults is the concrete `Ordering`
   enum, never the parameter and never `Self`.
9. **"Require a bound" ≠ "require the RIGHT bound", and the ruling must
   say which.** A `<T: Display>` bound leaves the shape exactly as broken
   (P4), because `analyzer.rs:33435-33458` falls a non-providing bound
   through to the same native emission. The right operand already checks
   adequacy (`platform.rs:5335`, `:5497`). The paper recommends requiring
   adequacy, to end the asymmetry.
10. **`&&` and `||` have no nameable bound** (`analyzer.rs:3420`), so for
    them "add a bound" is not a writable fix. Zero estate sites; the
    ruling should still say what that author is told. Related: [[B181]].
11. **The refusal's wording** should follow §4 — simpler than the right
    operand's, because the left operand is exactly where a bound works,
    and naming the trait-parameter declaration site when the operand is a
    trait's own parameter.

## 11. Recommendation

**TAKE THE BREAKING STEP.** The deferral was priced against an unknown
estate; the estate is one test fixture. Specifically:

1. Close [[B174]] by refusing a native operator whose left operand is a
   generic parameter **without a bound that provides the operator's
   method** (§6.2's second reading, not the first).
2. Edit `macros.rs:3518` to `trait Doubler<T: Add>` and add the import.
3. Remove the `#[ignore]` at `platform.rs:5682-5684`; the pin at `:5685`
   goes green.
4. Add the refusal's wording (§4) with a red-first pin carrying the
   pre-fix garbage run, `abab` (P2) — matching the b179 lane's practice
   of recording the garbage each refusal replaces.
5. Say in the spec section what an author of `a && b` over an unbounded
   `T` is told, since no bound can be named there.

The one judgement call left for the owner is §6.2, and it is the
difference between closing the item and closing the hole.

## 12. Owner questions

1. **The number is one — does that settle it?** The breaking surface is a
   single compiler test fixture, the non-breaking surface is zero live
   sites plus the pin that turns green, and the applications are entirely
   unexposed. Is that enough to take the step now, in a FIX-NOW lane?

2. **"A bound" or "the right bound"?** Today `<T: Display>` on the left of
   `+` compiles to concatenation exactly as `<T>` does (P4). Closing the
   item as literally written leaves that. The paper recommends requiring
   a bound that *provides* the operator's method, which also ends the
   disagreement with the right operand (`platform.rs:5335`, `:5497`
   already fail there). Which do you want?

3. **`&&` and `||`.** No trait names them, so no bound can fix a `T && U`
   in a default. Zero sites today. Should the refusal there simply say so
   and steer to changing the type, or should this be folded into
   [[B181]]?

4. **The spec is already right.** `types.md:653` prescribes `<T: Add>` for
   a left-operand parameter and the compiler does not enforce it. Does
   that change how you want the item framed — a conformance fix rather
   than a breaking generics change — and does it change its priority?

5. **Anything outside the swept estate?** The census covers std,
   macro_std, the corpus, examples, benchmarks, docs fences, crates
   fixtures, templates, kolt, the website and the playground. Worktree
   clones under `.claude/worktrees/` were excluded as working copies (~40
   full clones; if you want them counted, the crates figures multiply).
   Is there a corpus outside those ten buckets that should be checked
   before the step?
