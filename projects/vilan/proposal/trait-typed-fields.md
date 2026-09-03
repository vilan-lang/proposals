# A trait annotation on a struct field (B184)

> **Status: REVISION 2, 2026-09-03** — DISCUSSION REQUIRED before any
> build (work order 26, lane b184-paper-2; tracker item [[B184]]).
> Revision 1 (work order 24, 2026-09-01) is preserved below the rule,
> unedited. Where the two disagree, revision 2 says so and says why.
>
> **What revision 2 is for.** The owner read revision 1 and asked two
> things: whether an `impl Trait` grammar is worth its noise, and how
> four specific programs should be decided under the one-instantiation
> rule. Answering the second requires stating the rule, and stating the
> rule turns out to be the whole discussion — because *three different
> rules* fit the phrase "all instantiations use the same concrete type",
> the four cases agree on three of them, and the fourth case is the only
> program that tells them apart. §R2 names the three; §R3 decides the
> cases; §R4 answers the grammar question.
>
> **The finding that reframes revision 2.** The language has already
> decided the owner's four cases — one level down, at the `let`
> position, where [[B161]] shipped. `let a: X = A {}` and
> `let b: X = B {}` in one scope both compile and both run (R5);
> `mut a: X = A {}` followed by `a = B {}` is refused, naming the
> initializer that grounded the binding (R7). That is *per binding*, not
> program-wide, and it is not a near-miss: it is the exact four-case
> pattern the owner is asking about, with three of the four already
> answered in shipped code. [[B186]] answers them the same way one step
> further out — `fun tell(v: X)` accepts an `A` and a `B` in one program
> (R6), minting one implicit generic per parameter. **Revision 1 read
> the ask as a new solver mode. Under the per-binding rule it is not:
> it is sugar over `struct C<S: X> { x: S }`, with byte-identical
> emission (R9), and the entire "what is the program" reservation that
> drove revision 1's HOLD (§3.2, §3.3) evaporates, because nothing is
> global any more.**
>
> **Recommendation: BUILD the per-binding rule (§R2.2), as one lane.**
> Answer to the owner's fourth case: **VALID.** Answer to the grammar
> question: **bare `x: Trait`, no `impl` keyword.** §R5 states both, with
> the price of the recommendation stated in the same breath — the
> per-binding rule does *not* deliver the two kolt sites §5.3 argues
> from, and that is the honest cost of choosing it.
>
> Everything in revision 2 was probed against a debug build of
> `vilan 0.40.0 (635e37289)` (`next` @ `635e3728`). Thirty-two programs,
> R1–R32; the ledger is §R6. Compiler citations are read from the same
> detached worktree and given repo-relative. Revision 1's probes keep
> their P-numbers and were **not** re-run except where §R1 says they
> were.

## Revision 2 — the owner's questions

### R1. What changed under the paper since revision 1

Revision 1 recommended an order: *fix the hole, let [[B182]] land, then
re-ask.* All three happened within two days, and the re-ask is this
section's premise, so it is worth pinning what the compiler now does.

| Revision 1 said | Today | Probe |
|---|---|---|
| The bare nominal `Holder` is **accepted** and erases its parameter — `seven1`, plus an ICE (P11, P4/P5) | **Refused**, at every position: `` `C` takes 1 type argument, 0 given — write `C<S>` with `S` supplied here `` | R10 (parameter), R11 (field), R26 (module-level type argument) |
| One bare-trait field prints **two generated-code cascades before the root** (P17) | **One report**, at the field's annotation, with the construction sites silent | R1–R4 |
| The parameter half is "being built by a sibling lane" | Shipped ([[B186]]): `fun tell(v: X)` takes an `A` and a `B` in one program | R6, R12 |
| — | [[B194]] shipped; B188's arity gate on derived source **removed** | (read, not probed) |

So revision 1's §6 vacancy exists exactly as it was ordered to: the bare
nominal is a **named refusal** today, and giving it a meaning is now a
*narrowing of a diagnostic*, not a reinterpretation of an accepted
spelling. Revision 1's determinations 1–3 are discharged. Determination 7
("the owner's actual pain was B182") is discharged too, and the owner
came back anyway — which is itself an answer to revision 1's question 5.

The four cases, run verbatim, all refuse identically today, at the
**declaration**:

```
Error: 'X' is a trait, not a type: a trait is not a value type (vilan has no
trait objects), so no value can have this type. Here a trait names a
parameter's bound, not a value type; write `fun f(x: X)` for a parameter, or a
generic for a field/return — `<T: X>`, with 'T' written here.
   ╭─[ R1:6:15 ]
 1 │ trait X {}
   │       ╰── 'X' is declared here, as a trait
 6 │ struct C { x: X }
   │               ╰── …
```

One report, at `struct C { x: X }`, for all four programs (R1–R4). The
construction sites are silent — B182's provenance suppression
(`refused_annotation_slots`, `analyzer.rs:33831`) doing its job. The
message's own steer already names the two positions the language *does*
accept, which is §R4's consistency argument in the compiler's own words.

### R2. The rule, three ways

The owner's filing says: *"all instantiations of the struct use the same
concrete type for the field."* The ambiguity is in **instantiation**. It
can mean the written construction expression, or the runtime value, and
those give different languages.

#### R2.1 (a) Program-wide — one type per FIELD, globally

`struct C { x: X }` gives `C` a hidden type parameter with **one
argument for the whole program**, unified across every `C { x = … }`
site. `C` stays monomorphic: it names one type everywhere, takes no type
arguments at any mention, and a function written `fun tell(c: C)` is an
ordinary non-generic function.

- **The four cases.** 1 valid, 2 valid, 3 invalid, **4 invalid** — the
  two sites disagree about the one global argument.
- **Emission.** Nothing new. One struct, one shape; the JS is what a
  concrete `struct C { x: A }` emits.
- **The analyzer.** The hidden argument is a slot on the **struct
  entity**, filled by the first construction site and checked by the
  rest — `resolve_slot_unification` (`analyzer.rs:28250-28283`) is
  exactly this shape, and closure-parameter fill
  (`:26998-27047`) is the closer precedent, with its
  `closure_parameter_fill_sites` map so the conflict can name the site
  that filled. `impl` selection reads the slot: `c.x.who()` resolves by
  looking the struct's slot up, not the expression's type.
- **A mixed program is a refusal.** Two sites at two types must be
  named together — revision 1 §3.1 specifies the diagnostic and finds
  `check_duplicate_trait_impls` (`analyzer.rs:5351-5427`) to copy,
  entity-id ordering included.
- **The cost revision 1 measured, unchanged.** This rule can only be
  discharged by an analysis that *contains* the construction sites, and
  **in two of the three ways this compiler is invoked, that analysis
  does not exist** — `vilan check` on the declaring module analyzes it
  as its own entry and its import closure runs away from every
  construction site (P18); the LSP does the same for every open buffer
  (`vilan-lsp/src/document.rs:832`, `:950`). Revision 1 §3.2/§3.3 and
  determinations 8–11 are unaffected by anything that has shipped since.
- **What it buys that nothing else does.** `C` is a *name*, not an
  application, so it can be written where inference has nothing to run
  on: a module-level `Context<C>::new()` and a bare return type
  `fun get(): C`. Those are revision 1 §5.3's two kolt sites, and they
  are the whole of (a)'s advantage.

#### R2.2 (b) Per binding — a HIDDEN PARAMETER, one argument per value

`struct C { x: X }` desugars to `struct C<#0: X> { x: #0 }`, where `#0`
is a parameter the author never writes and never sees in a type
argument list. Every **mention** of `C` in a type position mints a fresh
implicit generic for `#0`, bound where that mention is grounded. `C` is
really `C<impl X>`; `fun tell(c: C)` is `fun tell<#0: X>(c: C<#0>)`, a
generic function.

- **The four cases.** 1 valid, 2 valid, 3 invalid, **4 valid** — two
  values, two hidden arguments, two monomorphizations.
- **Emission.** Nothing new, and this is checkable rather than
  arguable: R9 writes the desugaring out by hand
  (`struct C<S: X> { x: S }`, `fun tell<S: X>(c: C<S>)`) and gets
  two monomorphized bodies, `$a` calling `A`'s `who` and `$b` calling
  `B`'s, with the values plain arrays. That is the same census result
  B186 reported for the parameter half: **byte-identical JS to the
  written generic.**
- **The analyzer.** The hidden parameter lives where a written one
  lives — on the struct's declared-parameter list — with one bit set
  saying it is not counted by the arity check. Every mention runs
  `mint_implicit_generic` (declared `analyzer.rs:20362`, called at
  `:33802`), B186's function, from the same arm that already narrows
  `let` (`:33791`) and parameter (`:33800`) annotations.
  `impl` selection needs **no new code at all**: the field's type is a
  `Type::Generic`, bound at the construction site, and that is the case
  impl selection already handles for every written generic.
- **A mixed program is not a refusal.** It compiles, and it is R9: two
  `C`s at two types, both used, both dispatching correctly.
- **The cost.** Two, and they are the mirror image of (a)'s advantage.
  First, **hidden genericity is viral in exactly the way written
  genericity is** — a `struct Outer { c: C }` gains a hidden parameter
  of its own, transitively, and so does anything holding an `Outer`.
  The virality is invisible, which is the point, but it is real and it
  surfaces the moment a mention has nothing to bind it. Second, and
  decisively for the kolt exhibit: **the two sites revision 1 §5.3
  argues from stay unwritable.** A module-level `Context<C>::new()`
  has no value to ground `#0` from (R26 is the refusal today, in the
  written spelling), and a return type `fun get(): C` has no inference
  direction (R24: `cannot infer 'S' for this call; its bound ': X'
  cannot be checked`). Under (b), the author's fix at both sites is
  what it is today — name `SignalCell`.
- **Where it is already the language's answer.** At the `let`
  position, shipped: R5 runs `let a: X = A {}` and `let b: X = B {}` in
  one scope and prints `A` / `B`. At the parameter position, shipped:
  R6 runs `tell(A {})` and `tell(B {})` through one `fun tell(v: X)`
  and prints `A` / `B`. **Both are (b), one and two levels down.**

#### R2.3 (c) Dynamic — the field holds any `X` and dispatches at runtime

Not on the table, and the item's parenthetical asked the right question
to establish why.

**Is a trait-typed local monomorphized or dispatched dynamically?
Monomorphized. Statically. Per binding.** R8 emits R5 — two locals, one
`X` annotation each, two different implementing types — and the whole
program is:

```js
function who(self)  { return "A"; }
function who2(self) { return "B"; }
const a = [  ];
const b = [  ];
console.log(who(a));
console.log(who2(b));
```

Two top-level functions, resolved at compile time. A struct value is a
bare array with **no tag, no header, no type word**. There is nowhere
for a vtable pointer to live and nothing at runtime that could select an
impl. [[B161]]'s shipped semantics say the same thing from the front:
the annotation is a *constraint*, "a CONSTRAINT on the value's own type,
which stays '{type_label}'" (`analyzer.rs:5174`), and R7 proves the
binding really does carry the concrete type — `mut a: X = A {}` then
`a = B {}` is `Expected A, but got B instead`, with the note *"the
variable's type was inferred from this initializer (A)"*.

And the language ruled on it: **trait objects were DECLINED**
(`proposal/trait-objects.md`, RATIFIED 2026-08-07, Q1). Choosing (c) at
the field position would reopen a ratified decision, invent the
`(value, vtable)` representation that paper priced, and make the field
the one place in vilan where dispatch is not static. It is listed here
for completeness and to record that the probe answers the item's
question, not because it is a live option.

#### R2.4 The three, side by side

| | (a) program-wide | **(b) per binding** | (c) dynamic |
|---|---|---|---|
| `C` is | monomorphic | `C<impl X>` | monomorphic, boxed |
| Case 4 | invalid | **valid** | valid |
| `fun tell(c: C)` | ordinary | generic over `#0` | ordinary |
| Desugaring that exists | none | **`struct C<S: X> { x: S }`** | none |
| Emission | unchanged | **unchanged** (R9) | new: a vtable per impl |
| Grounded from | every construction site, globally | the mention's own binding, locally | not grounded |
| Analysis unit needed | one entry's *reverse* import closure — does not exist (P18) | **the current one** | — |
| LSP: declaring file alone | grounds nothing, ever (rev 1 §3.3) | **grounds normally** | — |
| Module-level `Context<C>` | **works** | refuses (R27) | works |
| `fun get(): C` | **works** | refuses (R24) | works |
| Precedent in shipped vilan | none | **B161 (`let`), B186 (parameter)** | none — declined 2026-08-07 |
| New whole-program check | yes, a fourth category | **no** | no |

The table is the argument. (a) buys two spellings and costs the
language its first whole-program uniqueness rule, in an architecture
revision 1 measured and found cannot host it. (b) buys the ordinary
value positions, costs those two spellings, and is **already how the
language behaves at both positions where the surface shipped**.

### R3. The four cases, decided

Under the recommended rule, **(b)**. Today's behaviour is probed for
each; today all four refuse at the declaration (§R1), so the "today"
column reports what the *closest legal spelling* does — which is the
desugaring, and therefore what the sugar would inherit.

#### Case 1 — `{ let c1 = C { x = A {} }; let c2 = C { x = A {} }; }`

**VALID.** Two bindings, two hidden arguments, both `A`. Nothing to
decide: it is valid under all three rules, and the owner marked it
"valid in theory" correctly.

*Today:* refused at the declaration (R1). The desugaring runs — two
`C<A>` bindings share one emitted body (R9's `c1`/`c3` are the two
`C<A>` values in that probe).

#### Case 2 — `{ mut c1 = C { x = A {} }; c1 = C { x = A {} }; }`

**VALID.** The reassignment's type is `C<A>`; the binding's type is
`C<A>`; they agree. Valid under all three rules.

*Today:* refused at the declaration (R2). The desugaring runs — R9's
`mut c3 = C { x = A {} }; c3 = C { x = A {} };` is this program with the
parameter written, and prints `A`.

#### Case 3 — `{ mut c1 = C { x = A {} }; c2 = C { x = B {} }; }`

The item flags that `c2` is undeclared. Both readings, decided:

**As written: INVALID, and not for a B184 reason.** `c2 = …` with no
`let`/`mut` is a plain scope error, and it is the error the compiler
reports today *in addition to* the declaration refusal:

```
Error: cannot find 'c2' in this scope
   ╭─[ R3:9:2 ]
 9 │     c2 = C { x = B {} };
   │     ╰── cannot find 'c2' in this scope
```
(R3.) It is the same refusal for a `str`, and no rule chosen here
changes it. Whatever B184 ships, this program stays invalid on its
first line of trouble.

**As intended (`c1 = C { x = B {} }`): INVALID.** The binding `c1` was
grounded at `C<A>` by its initializer; `C<B>` is a different type. This
is the owner's "invalid", and the important part is *why*: under (b) it
is invalid for a rule the language already has and already enforces
with the right message. R28 runs the desugaring:

```
Error: Expected C<A>, but got C<B> instead.
   ╭─[ R28:9:7 ]
 8 │     mut c1 = C { x = A {} };
   │              ╰── the variable's type was inferred from this initializer (C<A>)
 9 │     c1 = C { x = B {} };
   │          ╰── Expected C<A>, but got C<B> instead.
```

That diagnostic needs no new machinery, and it is the same shape R7
already produces one level down for `mut a: X = A {}; a = B {}`. Under
(a) the case is also invalid, but for a different and much larger
reason — the global argument — and the message would have to be the
two-site refusal revision 1 §3.1 specifies, which does not exist.

**One thing (b) must decide that this case exposes:** how the hidden
argument *prints*. B186's convention is that an implicit generic
displays under **no name — the trait's name displays**. Applied here
that convention yields `Expected C, but got C instead.`, which is
useless. The hidden argument must show, and the natural spelling is
the desugaring's: `C<A>` / `C<B>`. That is a deviation from B186's
display rule, it is forced, and it is question Q3 in §R8.

#### Case 4 — `{ let c1 = C { x = A {} }; let c2 = C { x = B {} }; }`

**VALID.** This is the decision, and it goes to (b).

Three reasons, in the order they should be weighed.

1. **The language already decided it, twice, in shipped code.** R5:
   `let a: X = A {}; let b: X = B {};` in one scope — compiles, runs,
   prints `A` then `B`. That is case 4 at the `let` position, and
   [[B161]] shipped it as valid. R6: `fun tell(v: X)` called with an
   `A` and a `B` — compiles, runs, prints `A` then `B`. That is case 4
   at the parameter position, and [[B186]] shipped it as valid, minting
   one fresh generic per annotation on purpose. Ruling case 4 **invalid**
   at the field would make the field the one position in the language
   where a trait annotation means "and every other one of these must
   agree with you" — an inconsistency the author would meet by writing
   two structs.
2. **It is the only rule the architecture can host.** Ruling it invalid
   *is* choosing (a), and revision 1's §3.2/§3.3 stand undisturbed: the
   analysis that would have to see both `let`s does not exist when the
   declaring module is checked alone (P18) or when it is the open
   buffer.
3. **It costs nothing to emit.** R9 is case 4 with the parameter
   written: two `C`s at two types, `tell` called on both, and the JS is
   two monomorphized bodies. There is no runtime consequence to decide.

**The consequence for a function taking `C` — say it plainly.** Under
(b), `fun tell(c: C): str` is **generic**. It is `fun tell<#0: X>(c:
C<#0>)`, monomorphized per hidden argument, and R9's emission shows the
two bodies (`$a`, `$b`). Four things follow, and each is a thing the
owner is agreeing to:

- Two mentions of `C` in one signature are **two independent** hidden
  parameters, exactly as two `X` parameters are today (R12) — so
  `fun both(p: C, q: C)` accepts a `C<A>` and a `C<B>`, and a body that
  assigns one to the other is asking for a check the compiler does not
  currently perform (see §R7's finding F1).
- `tell` cannot be an entry the emitter monomorphizes once; it is a
  template. This is already true of every `fun f(x: Trait)` in the
  estate and the census found the emission unchanged, so the cost is
  known to be zero.
- A `C` in a **return type** has no binding source and must refuse —
  R24's `cannot infer 'S' for this call; its bound ': X' cannot be
  checked` is the shape it inherits. This is the existential case, it is
  a genuinely different feature (Rust's `-> impl Trait`, not its
  argument-position `impl Trait`), and it should be out of scope for a
  first lane. Q2 in §R8.
- A `C` as a **type argument** with nothing to ground it — the
  module-level `Context<C>::new()` — refuses, R27.

### R4. The `impl Trait` grammar question

The owner: *"I know it would [help differentiate] but it comes at the
cost of extra noise. Is the value high enough? You'd have to learn how
traits as type annotations work anyways, so I don't see a huge win from
requiring it."*

**Recommendation: bare `x: Trait`.** The owner's own reasoning is the
strongest argument on the table and the probes support it; what follows
is the evidence, including the one place where a real ambiguity was
found — and why `impl` does not fix that one either.

#### R4.1 Consistency — the argument that decides it

Both positions where a trait annotation has shipped are **bare**:

```vilan,fragment
let count: Signal<i32> = SignalCell::new(1);   //  B161 — bare
fun render(v: Display) { … }                   //  B186 — bare
```

Requiring `impl` at the field makes the field the only position that
needs it. The alternatives are worse: requiring it everywhere is a
breaking change to two shipped features, and the compiler's own steer
would have to be rewritten — today it reads *"write `fun f(x: X)` for a
parameter"* (R1), teaching the bare spelling in the very message an
author hits on the way to this feature. A language that spells one
constraint three ways depending on position has not saved anyone from
learning how the constraint works; it has given them three things to
learn instead of one.

#### R4.2 The editor already differentiates — probed

**PROBED, and the answer is yes.** The LSP classifies a name in a type
position from the **entity it resolved to**, not from its spelling:
`Expr::Trait(_) => TokenKind::Interface`, `Expr::Struct(_) =>
TokenKind::Struct` (`vilan-lsp/src/document.rs:2444-2450`), and the two
are distinct entries in the published legend — `"interface"` at index 3,
`"struct"` at index 1 of `TOKEN_TYPES` (`:792-805`). R16 runs
`Document::semantic_tokens()` over a file with a trait `X` and a struct
`A`, both used in the same annotation position:

```
trait decl X          = Interface
trait-in-param X (v: X) = Interface
struct decl A         = Struct
struct-in-param A (a: A) = Struct
```

So in any editor with semantic highlighting on, a trait annotation is
**already a different colour from a struct annotation**, in the same
position, with no keyword. The `impl` token would be marking a
distinction the editor makes for free, and would make it twice.

#### R4.3 The reader without an editor — the real cost, priced

This is where the grammar's case actually lives, and it should not be
waved away: reading `x: N` in a diff, a review comment or a book page,
you cannot tell whether `N` is a trait or a struct without looking it
up.

But the objection proves more than the owner is asking for. Vilan's
type-annotation grammar has **never** encoded the sort of a name.
`x: N` is equally silent about whether `N` is a struct or an enum, and
nobody proposes `x: enum N`; `Option<T>` and `List<T>` are spelled the
same and are different sorts. Encoding one sort distinction and not the
others buys inconsistency, not clarity — and the one it would encode is
the one the compiler is *most* insistent about naming when it matters
(R1's refusal opens `'X' is a trait, not a type` and carries a note at
the trait's declaration with its own `SourceId`, so it renders
cross-file in the CLI and as related information in the LSP).

#### R4.4 Error quality when a struct and a trait are confused

Two directions, and they are not symmetric.

**A trait where a struct was meant** — well served. R1's message names
the sort, states the rule, offers both working spellings, and points at
the declaration. Nothing about it improves under an `impl` grammar; the
author who wrote `x: X` meaning a struct would write `x: X` under either
grammar and get the same message.

**A struct where a trait was meant** — poorly served, and worth filing.
R17 writes a struct as a bound:

```vilan,fragment
struct S { v: i32 }
fun f<T: S>(x: T): i32 { x.v }        //  S is a STRUCT, used as a bound
```

Accepted silently. The only report is downstream and about something
else: `cannot access field 'v' on type T`. There is no *"'S' is a
struct, not a trait — a bound must name a trait"*, which is the exact
mirror of R1's message and does not exist. **This is a message gap, not
a grammar gap** — `x: impl S` would be equally accepted, since `impl`
marks the position, not the sort of what is written there. Filing it is
§R7's F3.

#### R4.5 What Rust's `impl` / `dyn` split buys that vilan does not need

In Rust, `impl Trait` is meaningful **because `dyn Trait` exists**. The
two words name two representations with different sizes, different
costs, different object-safety rules and different lifetimes; the
programmer must pick, so the grammar makes them pick. `impl` is not the
marker "a trait is written here" — it is the marker "**statically**
dispatched", and it earns its keep by contrast.

Vilan has no `dyn`. Trait objects were **DECLINED**
(`proposal/trait-objects.md`, RATIFIED 2026-08-07), and §R2.3's emission
probe shows the model that decision left behind: a value is a bare
array, dispatch is resolved at compile time, and there is exactly one
way a trait annotation can mean anything. A keyword whose job is to
distinguish two dispatch strategies, in a language with one, marks a
distinction with nothing on the other side of it. **The erasure model is
precisely what makes `impl` unnecessary**: because nothing is boxed and
nothing carries a vtable, there is no second reading for the bare
spelling to be confused with.

#### R4.6 The one real ambiguity found — and why `impl` does not fix it

The brief asked for bare *unless a probe shows a real ambiguity the
analyzer cannot resolve*. One was found, and it is worse than an
ambiguity — it is a silent, order-dependent resolution.

**A trait and a struct may share a name in one file, with no
diagnostic** (R18). Which one `x: N` means is decided by **declaration
order**:

```vilan,fragment
trait  N { fun who(self): str; }
struct N { v: i32 }
fun f(x: N): i32 { x.v }
fun main() { print(f(N { v = 41 })); }     //  R19: runs, prints 41 — N is the STRUCT
```

```vilan,fragment
struct N { v: i32 }
trait  N { fun who(self): str; }
fun f(x: N): i32 { x.v }
fun main() { print(f(N { v = 41 })); }     //  R20: refused — N is the TRAIT
```

R20's second report is the tell: `cannot initialize a non-struct: N`, at
a line that plainly initializes a struct declared three lines up.

**But `impl` does not fix it, and the controls say why.** The collision
is **sort-blind**: two structs with one name (R22), two traits with one
name (R23), a struct and an enum with one name (R24) are all accepted
identically, last-writer-wins, with no diagnostic. It is not "trait and
struct are confusable"; it is "**no duplicate top-level type
declaration is refused at all**". Under an `impl` grammar, `x: impl N`
in R20 would still resolve `N` by declaration order and still pick the
wrong entity — the keyword says which *sort was meant*, and the resolver
never consults intent. The fix is to refuse the second declaration
(§R7's F3), and it is worth doing regardless of B184.

So the probe that could have argued for the grammar argues instead for a
one-line refusal elsewhere, and leaves the grammar question where the
owner left it.

**The recommendation, in the two sentences the brief asks for.** Spell
it bare — `x: Trait` — because both positions where the surface already
shipped are bare, because the editor already paints a trait and a struct
as different token types in the same position (R16, probed), and because
`impl` earns its keep in Rust only by contrast with `dyn`, which vilan
declined in 2026-08 and whose absence is exactly what makes one
unambiguous reading of a trait annotation possible. The costs of bare
are real but small and better paid elsewhere: the reader without an
editor is no worse off than they already are for struct-versus-enum, and
the one genuine ambiguity the probes found — a trait and a struct
sharing a name, resolved by declaration order (R18/R19/R20) — is a
missing duplicate-declaration refusal that `impl` would not fix.

### R5. Recommendation, and the build's shape

**BUILD (b), the per-binding rule, as ONE lane.** Spelled bare.

Revision 1 recommended HOLD, and revision 2 changes that recommendation.
It should be clear which fact does the changing: **not** that anything
in revision 1's measurement was wrong — §3.2 and §3.3 stand exactly as
written, and every determination about "the program", the LSP and the
fourth category of whole-program check remains true. What changed is
that those are all objections to **(a)**, and the owner's four cases,
read against what shipped since, point at **(b)** — where none of them
apply, because nothing is global.

**Why one lane and not an arc.** Under (b) the feature is a surface over
a spelling that exists, compiles and runs today (R9), and every piece of
machinery it needs shipped in the last three days:

| Piece | What exists | New work |
|---|---|---|
| The annotation is not a value-position mistake | the same arm already narrows `let` (B161, `analyzer.rs:33791`) and parameter (B186, `:33800`) annotations | a third narrowing branch, keyed on a field-annotation side table |
| Minting the hidden parameter | `mint_implicit_generic` (`analyzer.rs:20362`, called at `:33802`) | called with the struct as owner instead of the function |
| Not counting it in the arity check | `written_application_arity_error` + the declared-parameters side table (B188) | one flag on the declared-parameters side table B188 built — a table B194 has already revised once, so the shape is precedented |
| Grounding it at a construction site | ordinary generic inference (R9 runs it) | none |
| `impl` selection reading the field | the field's type is a `Type::Generic`; already handled | none |
| Emission | byte-identical to the written generic (R9, and B186's census) | none |

**Out of the lane, deliberately.** The return position (`fun get(): C`)
is an existential and a different feature (§R3, case 4's consequences);
the module-level type-argument position (`Context<C>`) has no binding
source and refuses. Both should refuse in the first lane with the
message R24/R27 already produce, and both are §R8's Q2.

**The price, stated once.** (b) does not deliver revision 1 §5.3's two
kolt sites — the module-level `Context<AppContext>` and the bare
`fun get_prefs(): Prefs`. Those were the strongest form of the owner's
argument, and they are the one thing (a) buys that (b) does not. What
(b) does deliver is every ordinary value position: the declaration reads
`theme: Signal<Theme>` instead of naming five implementations, and
consumers that pass, hold and return `Prefs` by value stay bare. The
website's nine-field struct (§5.1) is the case where that is worth the
most.

**Pins per case**, red-first, each claimed by a planted wrong rule:

| Pin | Program | Expected | Reddened by |
|---|---|---|---|
| `field_trait_two_bindings_same_type` | case 1 | runs | any rule that refuses |
| `field_trait_mut_reassigned_same_type` | case 2 | runs | a per-*mention* rule that mints a second generic at the reassignment |
| `field_trait_undeclared_name_is_a_scope_error` | case 3 as written | `cannot find 'c2' in this scope`, and **only** that once the annotation is legal | a rule that reports a type error first |
| `field_trait_mut_reassigned_other_type` | case 3 as intended | `Expected C<A>, but got C<B> instead.` + the initializer note | rule (a) — refuses, but with the global message; rule (c) — accepts |
| `field_trait_two_bindings_different_types` | **case 4** | runs, prints `A` then `B` | **rule (a)** — this is the discriminating pin |
| `field_trait_consumer_is_generic` | `fun tell(c: C)` called on both | two monomorphized bodies in the emitted JS | rule (a) — one body |
| `field_trait_return_position_refuses` | `fun get(): C` | the `cannot infer` refusal | a lane that quietly makes returns existential |
| `field_trait_type_argument_position_refuses` | module-level `Context<C>` | the arity refusal | as above |
| `field_trait_emission_matches_written_generic` | case 4 vs its desugaring | **byte-identical** JS | any rule with a runtime component |
| `field_trait_nested_holder_is_hidden_generic` | `struct Outer { c: C }`, built and read | runs | a lane that stops the virality at one level |

### R6. Probe ledger

Thirty-two programs against a debug build of `vilan 0.40.0 (635e37289)`
(`next` @ `635e3728`), numbered R1–R32; sources in the lane scratchpad.
**Fourteen refused, eighteen compiled** — and two of the eighteen are
garbage runs (§R7). Revision 1's P-numbers are a separate namespace and
were not re-run except as §R1 records.

**The four cases, verbatim (R1–R4).** All four refuse identically, at
`struct C { x: X }`, one report each; R3 additionally reports the
undeclared `c2`.

| # | What it shows | Result |
|---|---|---|
| R1 | case 1 verbatim | `'X' is a trait, not a type…` at the field, once |
| R2 | case 2 verbatim | the same, once |
| R3 | case 3 verbatim | the same, **plus** `cannot find 'c2' in this scope` |
| R4 | case 4 verbatim | the same, once |

**What the shipped positions already do (R5–R8, R12).**

| # | What it shows | Result |
|---|---|---|
| R5 | **case 4 at the `let` position** — `let a: X = A {}`, `let b: X = B {}` | runs: `A` / `B` |
| R6 | **case 4 at the parameter position** — one `fun tell(v: X)`, two types | runs: `A` / `B` |
| R7 | **case 3-as-intended at the `let` position** — `mut a: X = A {}; a = B {}` | refused: `Expected A, but got B instead.` + *"the variable's type was inferred from this initializer (A)"* |
| R8 | **The dispatch question** — R5's emitted JS | two top-level functions `who`/`who2`, values are `[ ]`; **static, monomorphized, no vtable** |
| R12 | two same-trait parameters are two independent generics | runs |
| R16 | **LSP semantic tokens** (`Document::semantic_tokens()` under a patched probe test, reverted) | trait decl and trait-in-annotation = `Interface`; struct decl and struct-in-annotation = `Struct` |

**The desugaring, run (R9–R11, R26–R28).**

| # | What it shows | Result |
|---|---|---|
| R9 | **(b)'s existing spelling** — `struct C<S: X>`, cases 1/2/4 and a consumer | runs `A`/`B`/`A`; emission is **two monomorphized bodies** `$a`, `$b` |
| R10 | bare `C` as a parameter, after [[B188]] | refused: `` `C` takes 1 type argument, 0 given `` |
| R11 | bare `C` as a field, after [[B188]] | the same refusal |
| R26 | control — a module-level `Box<C<A>>`, arguments named | accepts |
| R27 | **the module-level site** — `Box<C>`, `C` bare | refused: the arity message |
| R28 | **case 3 as intended, desugared** | refused: `Expected C<A>, but got C<B> instead.` + the initializer note |

**The return position (R24, R25).**

| # | What it shows | Result |
|---|---|---|
| R24 | `fun make<S: X>(): C<S>` — the existential, written | refused: `cannot infer 'S' for this call; its bound ': X' cannot be checked` |
| R25 | `fun make(): X` — the bare trait in a return | refused: `'X' is a trait, not a type…` |

**The grammar question's probes (R17–R23).**

| # | What it shows | Result |
|---|---|---|
| R17 | a **struct** written as a bound (`fun f<T: S>`) | **accepted**; only `cannot access field 'v' on type T` downstream |
| R18 | `trait N` and `struct N` in one file | **accepted, no diagnostic** |
| R19 | …`trait N` first: `x: N` is the **struct** | runs, prints `41` |
| R20 | …`struct N` first: `x: N` is the **trait** | refused, incl. `cannot initialize a non-struct: N` at a struct literal |
| R21 | control — two `struct N` | accepted, no diagnostic |
| R22 | control — two `trait N` | accepted, no diagnostic |
| R23 | control — `struct N` + `enum N` | accepted, no diagnostic |

**The two garbage runs (R13–R15, R29–R32).**

| # | What it shows | Result |
|---|---|---|
| R13 | cross-assigned generics, empty structs | runs, `A` — the wrong impl, unobservable |
| R14 | **GARBAGE RUN** — the same with fields: `swap(A{tag}, B{n,label})` | **`A/7`** — an `i32` through a declared `: str` |
| R15 | control — the same with **written** generics `<P: X, Q: X>` | **`A/7`** — not B186's doing |
| R29 | a body narrows its caller's generic (`need_a(x)` for `x: X`) | accepted |
| R30 | **GARBAGE RUN** — …called with a `B` | **`9`** — an `i32` through a declared `: str` |
| R31 | control — written bounded generic `<T: X>` | **`9`** |
| R32 | control — **unbounded** generic `<T>` | **`9`** |

### R7. Findings this lane owes elsewhere

Three, all reproduced, none caused by this design, all on its path
because (b)'s hidden parameter **is** a generic.

**F1 — a generic parameter can be cross-assigned to another generic's
slot, and the call dispatches to the wrong impl. GARBAGE RUN.**

```vilan,fragment
fun swap(a: X, b: X): str { mut c = a; c = b; c.who() }
fun main() { print(swap(A { tag = "aa" }, B { n = 7, label = "bb" })); }
```
Accepted. Prints **`A/7`** (R14) — `A`'s `who` reading field 0 of a `B`,
so an `i32` escapes a declared `: str` return. **Not B186-specific**: the
written-generic control `fun swap<P: X, Q: X>(a: P, b: Q)` does the same
(R15). The emitted body calls `who` (A's impl) unconditionally.

**F2 — a body may bind its caller's generic to a concrete type.
GARBAGE RUN.**

```vilan,fragment
fun need_a(a: A): str { a.tag }
fun f(x: X): str { need_a(x) }        //  narrows the caller's generic to A
fun main() { print(f(B { n = 9 })); }
```
Accepted (R29/R30). Prints **`9`** — an `i32` through a declared `: str`
return. Controls: the same with a written bounded generic `<T: X>`
(R31) and with an **unbounded** `<T>` (R32) — both accepted, both print
`9`. The root is `reconcile_type`'s `(_, Type::Generic(constraint_id))`
arm (`analyzer.rs:19393`), which binds a generic the body has no right
to bind — the arm `trait-objects.md` §1.4 already flagged as "the leak",
now shown to leak in a second direction. Same family as [[B174]] and
[[B188]], different surface.

**F3 — no duplicate top-level type declaration is refused, and the
winner is decided by declaration order.** A trait and a struct (R18), two
structs (R21), two traits (R22), a struct and an enum (R23) — all
accepted with no diagnostic, last-writer-wins, and the loser's uses fail
downstream with messages about something else (R20: `cannot initialize a
non-struct: N` at a struct literal). §R4.4's missing *"'S' is a struct,
not a trait"* at a bound (R17) belongs with it.

### R8. Questions for the owner

Only the four where the answer changes the design.

**Q1 — case 4, which is the whole decision.** The paper recommends
**valid**: `let c1 = C { x = A {} }; let c2 = C { x = B {} }` compiles,
`C` is really `C<impl X>`, and a `fun tell(c: C)` is generic over the
hidden parameter and monomorphized per argument. The reason is that
your two shipped positions already answer it that way — R5 runs two
`let a: X` bindings at two types, R6 runs one `fun tell(v: X)` at two
types — and ruling the field the other way makes it the one position in
the language where a trait annotation constrains other people's code.
**The price is that `Prefs` then cannot be written bare at a
module-level `Context<Prefs>` or as a bare return type**, which were
revision 1 §5.3's two strongest sites. Do you take the consistency and
give up those two sites, or is the monomorphic `C` (rule (a)) what you
actually wanted — in which case revision 1's §3.2/§3.3 reservations come
back in full and the answer is an arc, not a lane?

**Q2 — the return position, in or out.** `fun get_prefs(): Prefs` is the
*existential* case: the callee picks the hidden argument, callers see an
opaque type. It is a different feature from the argument position (in
Rust they share a keyword and little else), and the language refuses it
today in the written spelling (R24) and in the bare-trait spelling
(R25). The recommendation is to refuse it in the first lane and file it
separately. Do you want it refused, or is the bare return type enough of
the ask that the lane should carry it?

**Q3 — how the hidden argument prints.** [[B186]] chose that an implicit
generic displays under **no name — the trait's name displays**. At a
field that convention produces `Expected C, but got C instead.` for
case 3, which is useless. The recommendation is that the hidden argument
**shows**, in the desugaring's spelling: `Expected C<A>, but got C<B>
instead.` That is a deliberate deviation from B186's display rule, at
the one place the rule does not work. Agreed?

**Q4 — F1 and F2, two garbage runs, both pre-existing.** `swap(A, B)`
prints `A/7` (R14) and `f(B { n = 9 })` prints `9` through a declared
`: str` (R30), both from `reconcile_type`'s `(_, Generic)` arm binding a
generic that the body has no right to bind — reproduced with written
generics, bounded and unbounded, so neither is B186's doing. They are on
B184's path only because (b)'s hidden parameter is a generic and would
inherit them. File as their own item now, ahead of the lane, the way
[[B188]] went ahead of this one?

---

# Revision 1 — 2026-09-01 (work order 24)

> **Status when written: PROPOSED 2026-09-01** — DISCUSSION REQUIRED
> before any build (work order 24, lane papers; tracker item [[B184]]).
> Preserved unedited. Its recommendation (HOLD the sugar, build the
> hole) was carried out: [[B188]] closed 2026-09-01, [[B182]] shipped,
> and [[B186]] shipped. Revision 2 above supersedes §9's recommendation
> and §10's questions 1, 2 and 5 (discharged); §3.2, §3.3 and
> determinations 8–11 remain true and are the reason revision 2
> recommends the per-binding rule rather than the program-wide one.
>
> **This paper is the FIELD half only.** The parameter half ([[B186]],
> `fun f(x: Trait)` as a per-call implicit generic) is ruled WANTED and is
> being built by a sibling lane in this order; its semantics are settled
> by the reactive paper §7.3 and nothing here re-opens them. The two
> features share a *surface* and share nothing else — §2.3 states the
> contrast precisely, because conflating them is the main way this
> discussion could go wrong.
>
> **The finding that reframes the ask.** The owner asks for a spelling
> that lets a field's type parameter go unwritten. That spelling **already
> exists and is already accepted** — not as `field: Trait<…>`, but as the
> bare nominal `Holder` for a `struct Holder<S>`. Today the compiler takes
> it, silently drops the parameter, and produces either a **garbage run**
> (P11: a `str` escapes a declared `: i32` return and prints `seven1`) or
> an **ICE** telling the user to report their program (P4/P5). So the
> question in front of the owner is not "should we add a way to leave the
> parameter unwritten" — there is one, and it is broken. It is: **what
> should leaving it unwritten mean?** B184 is one answer. Refusing the
> bare nominal is the other. Doing nothing is not on the list.
>
> Everything below was probed mechanically against a debug build of
> `vilan 0.40.0 (f30897ee0)`. Seventeen programs, including a two-file
> package (P18) that pins what "the program" means; the ledger is §7. The
> estate figures come from mechanical sweeps of `vilan` @ `f30897ee`,
> kolt and the website at their live checkouts (both read-only). Compiler
> citations are read from a detached read-only worktree at the same tip
> and are given repo-relative.
>
> **Recommendation: HOLD the sugar, BUILD the hole.** §8 states it.

## 1. The ask

From the owner (2026-09-01, off the kolt store migration):

> Allow `field: SomeTrait<…>` as a CHECKED CONSTRAINT ([[B161]]'s reading
> extended from `let` to fields), with the implementation requirement that
> ALL instantiations of the struct use the same concrete type for the
> field — the struct stays monomorphic, the field's real type inferred
> once program-wide from its construction sites. Effectively a
> program-inferred generic parameter the author never writes.

The motivation is real and this paper does not dispute it. §5 measures it:
**27 struct fields across the estate** are typed by a signal
implementation, in structs whose genericity — were it written out — would
be *viral* and, at two live sites, **unwritable**. The ask is well aimed.
What follows is about whether the mechanism can carry it.

## 2. The semantics, precisely

### 2.1 What is proposed

A field annotated with a trait is a **constraint**, not a type. The struct
gains a type parameter the author never writes; the parameter is
**grounded once, program-wide**, by unifying every construction site of
the struct. The struct's own name stays **monomorphic** — `Holder` names
one type everywhere, with no type arguments at any use site.

```vilan,fragment
struct Holder {
	count: Signal<i32>,      //  proposed: a constraint
}

let h = Holder { count = SignalCell::new(1) };   //  grounds count : SignalCell<i32>
fun read(h: Holder): i32 { h.count.get() }       //  Holder needs no arguments — ever
```

The monomorphism is the *whole* payoff and it must be stated that way.
The sugar's value is **not** saving the `<S: Signal<i32>>` on the
declaration — that is one line, written once. Its value is that **every
other mention of `Holder` in the program stays bare**. §5.3 shows two
sites in kolt where that is the difference between a spelling that exists
and one that does not.

### 2.2 Contrast with the explicit generic

```vilan,fragment
struct Holder<S: Signal<i32>> { count: S }       //  today, and it works (P2)
```

This compiles, infers `S` at construction, and runs (P2). It is not
broken and it is not going away. What it costs is **viral genericity**:
every consuming function (P3), every containing struct (P15), and every
type-argument position that names `Holder` must carry `S`. The cost is
not the declaration; it is the closure of everything that mentions it.

### 2.3 Contrast with [[B186]] — and why they are not the same feature

| | [[B186]], parameter | **B184, field** |
|---|---|---|
| Desugars to | `fun f<T: Trait>(x: T)` | *nothing that exists* |
| Instantiations | **many** — one per call, per type | **one** — program-wide |
| Grounded from | the call site, locally | every construction site, globally |
| Existing spelling | yes, exact | no |
| Breaks a caller? | never (strictly more permissive) | n/a |
| Emission | monomorphized per type (M16 shares bodies that don't mention `T`) | one struct, one shape |
| Is it sugar? | **yes** — a surface over a spelling | **no** — a new solver mode |

The rows that matter are the last three. B186 is a *surface*: it names a
desugaring the language already has, and every question about it is a
question about ergonomics. B184 has **no desugaring**. "A generic
parameter grounded once program-wide" is not `struct Holder<S: Signal<i32>>`
with the `S` elided — that struct is genuinely polymorphic and can be
built at two types in one program. B184's struct cannot. It is a *third*
thing, between monomorphic and generic, and the language has no other
example of it.

That is not an argument against it. It is an argument that the two must
not be ruled together, must not ship together on the theory that they are
"the same family", and that B186 shipping tells you **nothing** about
whether B184 can.

### 2.4 The rule's real content: a global uniqueness obligation

Strip the surface and B184 says: *this struct has a type parameter, and
the program must use exactly one argument for it.* That is a **whole-program
uniqueness constraint**, and it is the first one the language would have.
Every existing rule is local: a binding has one type (checked at the
binding), a call's generic is inferred (at the call), a bound is
discharged (at the site). B184's rule can only be discharged by looking at
*all* of a program at once.

Three consequences the discussion has to face, in ascending order of
difficulty. §3 takes them.

## 3. The solver shape

### 3.1 Two construction sites at different types must refuse, naming both

The refusal is the feature's core and it has an exact shape:

> `Holder`'s field `count` is constrained by `Signal<i32>` and must have
> ONE type across the program, but it is built at two: `SignalCell<i32>`
> here, and `StorageSignalCell<i32>` at ‹second span›. Write the field's
> type explicitly, or make the struct generic over it
> (`struct Holder<S: Signal<i32>>`).

Naming both sites is not decoration. A one-span version of this message
is unactionable — the site it names may be the correct one, and the
author has no way to find the other.

**The machinery exists and there is a precedent to copy.**
`Error` carries `note: Option<Note>` where `Note { span, msg, source }`,
and a populated `source: Option<SourceId>` makes the secondary label
**cross-file** (`error.rs:12-56`); the CLI renders it as an ariadne
sub-label with its own `file:line:col` header and the LSP as
`DiagnosticRelatedInformation` (`vilan-lsp/src/publish.rs:192-232`). The
two-user-site precedent is `check_duplicate_trait_impls`
(`analyzer.rs:5351-5427`): primary span at the *second* impl, note at the
first with **its own source**, an inline "by module 'X'" clause when the
two are in different files (`:5628-5633`), and — the part to copy —
**deterministic ordering by entity id** so "the same program always
reports the same one of a pair as the second" (`:5352-5354`), a rule the
`normalize_diagnostic_order` gate (`lib.rs:768-773`) would enforce.

Two cautions, both from the same reading. First, the house doctrine is
*"one, not a list — diagnostics stay terse"* (`error.rs:5-6`); `trace` is
the deliberate exception, reserved for context-coverage refusals. A
diagnostic naming N construction sites would be the second exception and
should be argued as one. Second, the closest existing shape — closure
first-call conflict, §3.4 — uses `Note::here` and is **same-file only**;
B184's would have to populate `source`, which is a small change but not
the zero it looks like.

The harder half: **which two sites?** With four construction sites at
three types, the refusal must pick a pair, and any pair it picks is
arbitrary. The honest shape is probably *"built at N types across M
sites"* with every site labelled — a diagnostic the compiler does not
emit anywhere today outside `trace`.

### 3.2 What is "the program"? — it is **one entry's import closure**, and that closure runs the wrong way

This is where the paper's recommendation comes from, so it is worth being
slow. The answer is not open; it is in the code, and it is worse for
B184 than the item's "moving target" phrasing suggests.

**There is exactly one `Analyzer` per analysis** (`analyzer.rs:38627`),
and its unit is **one entry file plus the modules that entry transitively
imports** (`analyze`, `analyzer.rs:38404`; the load worklist at
`:39355-39388`). `sources[0]` is always the entry. **A file that nothing
in the closure imports is never loaded and never checked.**

Now notice the direction. A struct is declared in `store.vl`. Its
construction sites are in `main.vl`, which **imports** `store.vl`.
`store.vl`'s own import closure therefore contains `main.vl` **never** —
imports point from the user to the declaration, and the analysis follows
imports. So:

> **The module that declares the struct can never, in its own analysis,
> see the evidence B184's rule needs.**

This is not a theoretical worry. The CLI checks exactly that module alone
— file mode gives a non-entry module `CompileGoal::CheckModule` and
analyzes it **as an entry** (`main.rs:3501-3504`, `:3045`). P18 is the
demonstration, in a two-file package:

```
$ vilan run .                      # whole unit, two sites at two types
7
seven                              # ← the unsoundness, across modules

$ vilan check src/store.vl         # the DECLARING module, alone
src/store.vl: no errors            # ← neither construction site in view
```

Three further facts compound it:

1. **One package can have several entries, each a wholly independent
   analysis.** `[entry.<name>]` (`manifest.rs:39-42`) lowers to a
   workspace with one member per entry, and `check` checks them all
   (`main.rs:3415-3428`, `:3874-3893`). The blessed fullstack template
   *is* "one package, two entries" (`init.rs:11`). A shared module is
   re-analyzed from scratch per entry, and **nothing above `compile_unit`
   deduplicates across them** — which is [[B182]]'s "printed once per
   entry", now located. The client entry and the server entry see
   *different subsets* of a shared struct's construction sites, and each
   subset is individually consistent.
2. **A standalone `[library]` is not type-checked at all.**
   `check_library` verifies only the platform import contract
   (`main.rs:1713-1732`). A library struct's construction sites are in
   applications the library has never seen, and the library has no
   analysis in which to ground anything.
3. **A file is checked once per platform colour**, and every leg's
   diagnostics are reported (`main.rs:451-459`, E113).

So "the program" resolves to **one entry's reachable closure**, and the
three readings the item invites are not three readings of one mechanism
— they are three *different features*:

- **Per-entry** (the only one that fits the existing architecture). The
  field grounds from the construction sites *that entry reaches*. The
  struct is then not one type in the package but one type per entry; the
  shared module already emits per-leg, so the build tolerates it. But a
  nominal type meaning something different depending on who imported it
  is a strange thing to make true, and it means `store.vl` checked alone
  grounds nothing at all.
- **Per-package.** Requires a genuinely cross-entry pass. **No such pass
  exists anywhere in this compiler**, and no cross-analysis state about
  user code survives one `analyze()` call — `Id`/`TypeId`/`SourceId` are
  per-analysis fields reset each run (`analysis-reuse.md` §0). This is
  new architecture, not a new check.
- **Per-library-consumer.** Makes the grounded type part of the library's
  published surface — which is exactly what the trait spelling existed to
  avoid — or grounds the same library type differently in two
  applications.

### 3.3 The LSP, where it is not a latency problem but an *evidence* problem

The compiler is not only a batch compiler, and the interactive answer is
sharper than "a moving target".

**The LSP analyzes each OPEN FILE as its own entry.** `Document::analyze`
passes the open document's own path as `entry_path`
(`vilan-lsp/src/document.rs:832`, `:898`, `:950`); project context comes
from the nearest manifest but **never substitutes the package's entry for
the open file** (`:87-147`). A document enters the map only on `did_open`
(`vilan-lsp/src/main.rs:1918-1955`).

Combine that with §3.2's import direction and the consequence is exact,
not probabilistic:

> Opening `store.vl` — the file that *declares* the struct — yields an
> analysis with **zero construction sites**. Not "sites the session has
> not got to yet." Zero, by the shape of the import graph, forever.

So hover on `h.count` in the declaring file cannot report a type at all;
opening `main.vl` yields one set of sites; opening a second entry yields
another. **The refusal diagnostic would appear, disappear, and change
identity based on which buffers are open** — and the identity change is
the part that cannot be engineered away, because the analyses genuinely
have different evidence.

The two standing papers on this ground —
[`analysis-reuse.md`](analysis-reuse.md) and
[`lsp-snapshot-consistency.md`](lsp-snapshot-consistency.md) — both bear
directly:

- `lsp-snapshot-consistency.md` establishes the two-snapshot law (live
  text versus analyzed program, S3/S4). It gives the LSP no package-wide
  view; the unit stays "one open buffer as an entry".
- `analysis-reuse.md` §6.5 classifies every whole-program check as
  **definition-site** (skippable for frozen std), **use-site-driven**, or
  **instantiation-driven**. B184's check is none of the three: it is
  **construction-site-driven**, and it is inherently unskippable and
  unfreezable — a fourth category, added to the pass whose measured cost
  is already ~30 ms of a ~115 ms analysis. §6.9's latent fixpoint bug
  (quiescence widened to count `type_map_writes`, because "any program
  whose closure-typing writes landed in the fixpoint's final quiet round
  was at the mercy of constraint-order luck") is the exact ordering
  hazard a new construction-site unification would enlarge.

**This is the paper's central reservation**, and it is stronger than the
item anticipates. Not "the analysis unit is a moving target" but: *in two
of the three ways this compiler is invoked, the analysis that would have
to enforce B184's rule does not contain the facts the rule is about.*

### 3.4 What exists to build on — more than I first assumed, and it is instructive

The paper's first draft said "nothing". That was wrong, and the
precedents are worth naming because they show both that the shape is
buildable **and** what its natural scope is.

- **Slot unification** (`resolve_slot_unification`, `analyzer.rs:28250-28283`)
  is precisely B184's shape: one type slot, evidence pushed from many
  sites, the first non-`Unknown` push *fills*, later pushes are *checked*
  against it. Its refusal is the familiar `Expected {expected}, but got
  {got} instead.` — and it names **only the second site**, with no note
  and no first-site span.
- **Closure-parameter fill** (`analyzer.rs:26998-27047`) is closer still,
  and is the single best precedent: a type parameter the author never
  wrote, grounded from a *use* site, first-call-site-wins, with a
  dedicated `closure_parameter_fill_sites` map recording *who filled it*
  (`:27011-27013`) so the conflict diagnostic can carry a note at the
  first call — *"the parameter's type was inferred from this, the
  closure's first call ({expected})"* (`:27032-27038`). Its limitation is
  instructive too: the note uses `Note::here`, so it is **same-file
  only**.
- **The constraint store already outlives every function body** and is
  analysis-wide across modules (`Constraint`, `analyzer.rs:1917-1924`;
  the queues are `Analyzer` fields at `:2530`/`:2536`, drained by
  `resolve_constraints` inside `resolve_world`). So "unify evidence from
  distant sites within one analysis" is a solved problem.
- **Whole-program effect inference exists** — `async_infer.rs` propagates
  asyncness callee → caller over the call graph. Note how it handles
  unresolvable dispatch: *over-approximate* — "a dispatched method is
  treated as async if **any** candidate is async". **A type has no such
  join.** Where the effect analysis can shrug, B184 must refuse.

So the machinery is there **for one analysis**. What is not there is
anything that crosses one, and §3.2 is why that matters.

Now the other half of the answer: the spelling B184 wants to give meaning
to is **already accepted with a different, broken meaning**. This is the
finding from the front matter and it is the strongest single fact in the
paper:

```vilan,fragment
struct Holder<S> { inner: S }
fun read(h: Holder): i32 { h.inner }        //  bare nominal — ACCEPTED today
```

- **P6** — it compiles and runs.
- **P8** — the same bare-nominal parameter accepts `Holder { inner = 7 }`
  and `Holder { inner = "seven" }` in one program. Two construction sites
  at different types: exactly B184's refusal case, accepted silently.
- **P9** — a bare-nominal *field* (`struct Outer { h: Holder }`) does the
  same.
- **P11** — the garbage run. `read(Holder { inner = "seven" })` through a
  declared `: i32` return, then `+ 1`, prints **`seven1`**. The B179
  family's signature, in a fresh carrier.
- **P4/P5** — when the erased parameter's method resolves to a body-less
  trait requirement, the same shape **ICEs**: *"internal: a call resolved
  to `Get`'s requirement `take`, which has no body… please report this
  program"*. Reachable from ordinary user code with no std involvement.
- **P12** — the control: writing `Holder<i32>` refuses correctly
  (`Expected Holder<i32>, but got Holder<str> instead.`). So the checking
  works; it is the missing type argument that turns it off.
- **P10** — too *many* arguments is caught (as a type mismatch). Only the
  under-supplied case is unchecked.

So a generic type's argument list is not arity-checked when it is
under-supplied, the parameter is erased rather than inferred or refused,
and both the unsound path and the ICE path follow from that one gap.

**This should be filed as a bug today, independently of B184's fate.**
It is a soundness hole of the same class as the two the reactive paper
found (§8.1, §8.2) and it is not caused by anything on this design's path.

## 4. Generated code — settled, and the answer is favourable

The item's third question: *the `[service]` macro reads field types at
macro time — must grounding precede expansion, or must the macro read the
inferred type?* Probed, and the answer is **neither**.

**The macro does not need the inferred type.** `std/src/rpc.vl:1782-1799`
reads, for each `[expose]`d field, only `field.type_.arguments` — the
*written* type's argument list — and takes argument 0 as the element:

```vilan,fragment
if field.type_.arguments.len() == 1 {
	match field.type_.arguments.get(0) {
		Some(let element) => exposed_elements.push(element.render()),
		None => exposed_elements.push("_"),
	}
}
```

For a field written `Signal<List<i32>>` this yields `List<i32>` — the
same element it yields for `SignalCell<List<i32>>`. The field's *name*
is never read. The macro is already indifferent to which of the two is
written.

**The generated code is already generic over the field's type.** It calls
`std::rpc`'s `fun expose<T: Wire, S: Source<T>>(self, source: S): i32`
(`rpc.vl:1169`) — `S` is inferred from the argument. So the generated
site does not need the field's type at expansion; it needs it at
type-check of the expansion, which is after grounding either way.

**The compiler's `[expose]` check already reads the RESOLVED type**, not
the written one. `analyzer.rs:12152`, `check_expose_fields`, calls
`field_type_id.get_type(self)` and explicitly skips ungrounded fields:

```rust
// A field that never grounded is another diagnostic's business.
if matches!(field_type, Type::Unknown | Type::Unresolved) { continue; }
```

then reconciles via `trait_args_for(&field_type, source_trait_id)`. Under
B184 a grounded field would satisfy this check with no change at all.

**The question's premise — "must grounding precede expansion?" — is
answered NO, and it could not be answered yes.** Macro expansion runs
entirely inside the load loop, *before* any constraint resolves:
per file the analyzer registers macros, expands them, then walks
(`analyzer.rs:39390-39530`), and only after the load loop settles does
`resolve_world()` run (`:39992`) and `build()` (`:40103`). `macros.rs:1-5`
states it outright — macro text is spliced "before analysis". Grounding
needs `build()`; `build()` consumes what the loader produced; the loader
is fed by expansion. **Grounding cannot precede expansion without
inverting the pipeline.**

Nor can a macro read an inferred type. The reflection vocabulary is
explicitly syntactic — `macro_std/src/meta.vl:3-7`: *"Shapes are v1:
**syntactic, not semantic** (a `TypeExpr` is a *written* type,
renderable back to text; **nothing here is resolved**)."* `Field` carries
`type_: TypeExpr`, "its **written type**" (`:44-48`). There is exactly one
dataflow from the analyzer into a macro — the gathered `[rpc]` methods —
and it is also syntax.

**Determination: the macro half of B184 is a non-issue anyway, because
neither half needs what it cannot have.** Both the std macro and the
compiler check already read exactly the right thing, and the only
requirement B184 imposes is a *scheduling* one inside the analyzer:
`check_expose_fields` must run after grounding. It already does (a
deferred post-pass over collected checks, which is why the `Unknown` skip
exists).

**One thing B184 would actually IMPROVE.** The reactive paper §14(5)
records a standing residual: the macro reads the element off the field's
*sole type argument*, so "a source whose element is not its one type
argument renders `_` and errors at the generated site." That is a
coincidence today — `SignalCell<Note>` happens to put its element in
argument 0. Under B184 the written type is the **trait**, whose type
argument *is* the element by the trait's own declaration
(`trait Signal<T> with Source<T>`, `reactive.vl:488`). Writing
`Signal<Note>` would make the macro's reading correct **by construction**
rather than by luck. That is a genuine, unremarked point in the feature's
favour, and it is the one place where the sugar does structural work
rather than cosmetic work.

**What is NOT a non-issue is [[B182]], and this lane reproduced it
minimally.** P17 — a `[service]` struct with **one** bare-trait field —
produces three errors, and the two cascade errors from generated code
print **before** the root:

```
Error: in code generated by this attribute: cannot infer 'S' for this call; its bound ': Source<T>' cannot be checked
Error: in code generated by this attribute: cannot infer 'T' for this call; its bound ': Wire' cannot be checked
Error: 'Signal' is a trait, not a type: …
```

That is kolt's 53-error pile-up in its smallest reproducible form, and it
is handed to B182's lane as a fixture. Note what it means for B184: **the
owner's experience of the feature's absence is B182's bug, not B184's
gap.** Had the root printed first and alone, the migration would have
read "write `SignalCell` here", which is a two-second fix. Much of the
motivation for B184 is the *diagnostic*, and B182 is already filed.

## 5. The kolt exhibit — and where the explicit spelling runs out

### 5.1 The estate's field census

Struct fields whose type is a signal implementation, live checkouts, work
trees excluded:

| Location | Fields | Structs |
|---|---|---|
| std (`reactive.vl`, `rpc.vl`) | 6 | 4 |
| kolt (`app_context`, `store`, `prefs`, `overlay`) | 12 | 6 |
| website (`playground_page.vl`) | 9 | 1 |
| **Total** | **27** | **11** |

Two of the 27 are the `[expose]`d fields of `KoltStore` that started the
item. The website's nine are one struct — which is the noise headline:
the explicit spelling makes it `struct …<A: Signal<str>, B: Signal<List<DiagRow>>,
C: Signal<List<ConsoleRow>>, D: Signal<bool>, E: Signal<bool>,
F: Signal<str>, G: Signal<str>, H: Signal<str>, I: Signal<str>>`, and
every consumer repeats all nine.

### 5.2 kolt's `Prefs` — the mixed struct, which is the honest case

`prefs.vl:10-16` is the exhibit the item should be argued from, more than
`KoltStore`:

```vilan,fragment
struct Prefs {
	theme: SignalCell<Theme>,
	theme_selection_delay_enabled: SignalCell<bool>,
	sidebar_width: StorageSignalCell<f64>,      // ← a CUSTOM Signal impl
	sidebar_collapsed: SignalCell<bool>,
	sidebar_dock: SignalCell<SidebarDock>,
}
```

Four canonical cells and one custom implementation, side by side. This is
the shape the trait spelling is *for*: the author wants to say "these are
all signals" and not care which. The explicit spelling costs five type
parameters (P13 confirms it compiles and runs), repeated at every
consumer.

Note also `probe.vl:29-30`, where kolt already writes the trait at a
`let`:

```vilan,fragment
let observed: Signal<i32> = Signal::new(-1);
```

[[B161]] shipped that. The asymmetry — the trait is writable at a binding
and not at a field two lines away — is the ergonomic complaint, stated
exactly.

### 5.3 Where the explicit spelling is not merely noisy but **unavailable**

`app_context.vl` is the site that makes the case:

```vilan,fragment
struct AppContext {
	client: KoltClient<SocketTransport>,
	token: SignalCell<str>,
	route: SignalCell<Route>,
	prefs: Prefs,                       // ← Prefs, bare
}

let app_context = Context<AppContext>::new();      // ← module level

fun get_prefs(): Prefs { app_context.get().prefs }  // ← a bare return type
```

Follow the virality. Make `Prefs` generic in five parameters and:

- `AppContext` must gain all five (a field of a generic type is generic),
  plus its own two, for **seven**;
- `Context<AppContext>` at **module level** must name all seven — and a
  module-level binding has **no construction site to infer from**. There
  is nothing at that line for inference to run on;
- `get_prefs(): Prefs` must name five arguments in a **return position**,
  where the reactive paper §7.2 already ruled there is no inference
  direction to run.

So at these two sites the explicit generic is not a noisy alternative —
it is **not a spelling that exists**. The author's only option is to name
the concrete implementations, which is what kolt does. That is the
strongest form of the owner's argument and it is worth having stated
precisely, because it is *also* the strongest argument for the
monomorphism in §2.1: a monomorphic `Prefs` can be named bare at a
module-level `Context<…>` and in a return type, and a generic one cannot.

**The counter-argument, equally honest:** at both of those sites, naming
`SignalCell` costs nothing and is arguably clearer. `Prefs` has exactly
**one** construction site (`Prefs::new()`, `prefs.vl:19-27`), so the
program-wide inference B184 proposes would have exactly one site to
consult. A feature whose global solver has one input is a feature that
could be a local annotation. Across the estate, the pattern holds: every
one of the 11 structs in §5.1 has a single construction site. **The
global unification has, today, nothing to unify.** That is either
reassuring (the refusal will never fire) or damning (the machinery is
unearned), depending on the owner's read, and it is question 4 in §9.

## 6. What refusing the bare nominal would look like — the alternative

If B184 is declined, §3.4's hole still must close, and the closure is a
refusal:

> `Holder` is generic over 1 type parameter, but no type arguments were
> written. Write them (`Holder<i32>`), or make this declaration generic
> and forward them (`fun read<S>(h: Holder<S>)`).

Cheap, local, entirely conventional, and it converts P11's garbage run
and P4/P5's ICE into one clear message. It also **creates the vacancy**
B184 would later fill: once the bare nominal is a named refusal, giving
it B184's meaning is a narrowing of a diagnostic — the same shape B161
took at the `let` position — rather than a reinterpretation of something
already accepted. That ordering is strictly better than the reverse and
it costs nothing to take now.

## 7. Probe ledger

Seventeen programs against a debug build of `vilan 0.40.0 (f30897ee0)`
(numbered P1–P18; P7 was folded into P5). **Nine compiled and ran; eight
were refused** — two of the refusals are internal errors, counted as
refusals. Sources are in the lane scratchpad; P18 is a two-file package
under `pkgprobe/`.

**Refused (8).**

| # | What it shows | Diagnostic (head) |
|---|---|---|
| P1 | **The ask, verbatim** — `count: Signal<i32>` at a field | `'Signal' is a trait, not a type… Declare a generic parameter bounded by the trait instead — '<T: Signal>'` (+1 cascade, `cannot call method 'get' on unknown`) |
| P4 | **ICE** — a bare generic nominal as a parameter, std trait | `internal: a call resolved to 'Source''s requirement 'get', which has no body… please report this program` |
| P5 | …the same with a **user** trait, no std | `internal: a call resolved to 'Get''s requirement 'take', which has no body…` |
| P10 | Too *many* type arguments **is** caught | `Expected Holder<i32, str>, but got Holder<i32> instead.` |
| P12 | **Control** — the written argument refuses correctly | `Expected Holder<i32>, but got Holder<str> instead.` |
| P14 | No wildcard type argument (`Holder<_>`) | `cannot find type '_'` |
| P16 | A qualified impl path (`impl X with std::reactive::Signal<…>`) is not the grammar | `found 'impl' expected an expression` |
| P17 | **[[B182]] minimally** — `[service]` + one bare-trait field, root printed **last** | 2 generated-code cascades, then `'Signal' is a trait, not a type…` |

**Compiled and ran (9).**

| # | What it shows | Output |
|---|---|---|
| P2 | The **explicit generic**, inferred at construction | `1` |
| P3 | …and a consumer restating the bound — the virality tax | `1` |
| P6 | **A bare generic nominal is ACCEPTED** as a parameter | `7` |
| P9 | …and as a **field** (`struct Outer { h: Holder }`) | `7` |
| P8 | …**built at two different types in one program** | `7` / `seven` |
| P11 | **GARBAGE RUN** — `str` through a declared `: i32`, then `+ 1` | **`seven1`** |
| P13 | kolt's `Prefs` shape, five explicit parameters, with a consumer | `400` |
| P15 | The full explicit spelling one level down (`h: Holder<SignalCell<i32>>`) | `1` |
| P18 | **The analysis-unit exhibit** — a two-file package. `vilan run .` accepts two construction sites at two types across modules; `vilan check src/store.vl` — the **declaring** module alone — reports `no errors`, with neither site in view | `7` / `seven`, then `src/store.vl: no errors` |

## 8. Determinations

1. **The spelling is already accepted, with a broken meaning.** A generic
   nominal written without its arguments is taken, the parameter erased,
   and the result is a garbage run (P11, `seven1`) or an ICE telling the
   user to report their program (P4, P5). Under-supplied type arguments
   are not arity-checked; over-supplied ones are (P10).
2. **That hole should be filed and closed now, independently of B184.**
   It is a soundness bug of the reactive paper's §8 class, is not caused
   by this design, and its fix — a named refusal (§6) — is cheap and
   local.
3. **Closing it first is the right ORDER for B184**, not merely a
   prerequisite: it turns a later B184 into a *narrowing of a diagnostic*
   (B161's shape at the `let` position) rather than a reinterpretation of
   an accepted spelling.
4. **B184 is not sugar and shares no desugaring with [[B186]].** B186
   names an existing spelling; B184's "one instantiation program-wide" is
   a third thing between monomorphic and generic, with no existing
   example in the language. Ruling them together would be an error.
5. **The monomorphism is the payoff, not the elided parameter.** The
   value is that every *other* mention of the struct stays bare (§5.3),
   not that the declaration is shorter.
6. **The macro half is a non-issue.** `std`'s `[service]` reads only the
   written type's argument list (`rpc.vl:1791`) and never the type's
   name; the generated call is generic over the field type
   (`rpc.vl:1169`); and the compiler's `[expose]` check already reads the
   **resolved** type and skips ungrounded fields (`analyzer.rs:12152`).
   Grounding need not precede expansion, and no macro needs to read an
   inferred type.
7. **The owner's actual pain was [[B182]], not B184's absence.** P17
   reproduces the cascade at one field: two generated-code errors print
   before the root. Fix the ordering and the migration reads "write
   `SignalCell` here."
8. **"The program" is decided, and it is one ENTRY's import closure**
   (`analyzer.rs:38404`, `:39355-39388`) — *not* a package. **Imports run
   the wrong way for this feature**: a struct's construction sites live
   in modules that import it, so the declaring module's own analysis
   never loads them. P18 demonstrates it: `vilan check src/store.vl`
   reports `no errors` with two conflicting construction sites sitting in
   the sibling file. The CLI checks exactly that module alone (file mode
   gives a non-entry module `CompileGoal::CheckModule` and analyzes it as
   an entry, `main.rs:3501-3504`).
9. **The per-package reading is new architecture, not a new check.** No
   cross-entry pass exists anywhere in the compiler, and no state about
   user code survives one `analyze()` call. A package may have several
   entries (`manifest.rs:39-42`), each a fully independent analysis with
   its own subset of construction sites — which is where [[B182]]'s
   "printed once per entry" comes from. A standalone `[library]` is **not
   type-checked at all** (`main.rs:1713-1732`), so a library struct has
   no analysis in which to ground anything.
10. **The LSP interaction is the load-bearing reservation, and it is an
    EVIDENCE problem, not a latency one** (§3.3). The LSP analyzes each
    **open file as its own entry** (`vilan-lsp/src/document.rs:832`,
    `:950`). Opening the declaring file therefore yields **zero**
    construction sites — by the shape of the import graph, permanently —
    so hover cannot report a type at all, and the refusal changes
    identity with which buffers are open.
11. **B184's check would be a fourth category of whole-program check.**
    `analysis-reuse.md` §6.5 classifies them as definition-site (skippable
    for frozen std), use-site-driven, or instantiation-driven. A
    construction-site-driven check is none of the three, and is inherently
    unskippable and unfreezable — added to a pass already measured at
    ~30 ms of a ~115 ms analysis.
12. **The solver precedents DO exist, within one analysis.** Slot
    unification (`analyzer.rs:28250`) is the exact shape — one slot, many
    sites, first-fills, later-checked. Closure-parameter fill
    (`:26998-27047`) is closer still: a parameter the author never wrote,
    grounded from a use site, first-call-wins, with a
    `closure_parameter_fill_sites` map so the conflict can name the first
    site. `check_duplicate_trait_impls` (`:5351-5427`) is the cross-file
    two-user-site diagnostic to copy, entity-id ordering included. What
    does not exist is anything crossing an analysis.
13. **The global solver has nothing to unify today.** All 11 structs in
    the estate census (§5.1) have exactly one construction site. The
    refusal in §3.1 — the feature's core mechanism — would not fire
    anywhere in the estate as it stands.
14. **The estate motivation is real but small and concentrated**: 27
    fields, 11 structs, and the two sites where the explicit spelling is
    genuinely *unavailable* (a module-level `Context<AppContext>` and a
    bare return type, §5.3) are both in kolt.
15. **One point in the feature's favour, unremarked in the item**: under
    B184 the `[service]` macro's element reading becomes correct **by
    construction** rather than by coincidence, closing the reactive
    paper's §14(5) standing residual for any field that uses the sugar
    (§4).

## 9. Recommendation

**HOLD B184. BUILD the hole it stands on.**

Concretely, in order:

1. **File and fix the under-supplied type-argument hole** (§3.4, P11's
   `seven1` and P4/P5's ICE). This is a bug, it is not B184, and it
   should not wait on a design discussion.
2. **Let [[B182]] land.** It is filed, and it removes most of what made
   the kolt migration painful. Re-ask the owner afterwards whether the
   field spelling still bites; the honest expectation is that it bites
   much less.
3. **Then rule on B184 with the numbers in §5** — 27 fields, 11 structs,
   every one with a single construction site — and with a decision on
   §3.2's readings of "the program" *in hand*, since that decision is the
   feature.

The case for holding is not that the ask is bad. It is this: B184's rule
can only be discharged by an analysis that contains the struct's
construction sites, and **in two of the three ways this compiler is
invoked, that analysis does not exist**. `vilan check` on the declaring
module analyzes it as its own entry, and its import closure runs away
from every construction site (P18). The LSP does the same on every open
buffer. So the feature is not "hard in the editor" — it is *undefined*
for the file the author is most likely to have open, which is the one
that declares the struct.

Against that: a concentrated ergonomic win (27 fields, 11 structs, two
genuinely unwritable sites), on a mechanism — the language's first
whole-program uniqueness rule — whose core refusal has, in the entire
estate, no site where it would fire.

If the owner wants it anyway, the buildable version is the **per-entry**
reading of §3.2 — the only one that fits the architecture — with the
consequence stated up front that a struct grounds per entry, that the
declaring module checked alone grounds nothing, and that hover in that
module answers "not grounded here". It should be scoped as an **arc, not
a lane**: a fourth category of whole-program check (§3.3), a new class of
diagnostic (§3.1), an LSP reconciliation against two standing papers, and
a spec section.

## 10. Owner questions

1. **The under-supplied type argument.** `fun read(h: Holder): i32` for a
   `struct Holder<S>` is accepted today and prints `seven1` for a `str`
   (P11); the same shape ICEs when the erased parameter's method is a
   body-less requirement (P4, P5). Should this be filed as an ordinary
   bug now — refuse the bare nominal — independently of B184's fate?

2. **Order.** The paper argues closing that hole *first* is strictly
   better, because it turns a later B184 into a narrowing of a named
   refusal rather than a reinterpretation of an accepted spelling. Agreed?

3. **"The program" is one entry's import closure, and imports run the
   wrong way.** A struct's construction sites are in modules that import
   it, so the declaring module's own analysis never sees them — P18:
   `vilan check src/store.vl` reports `no errors` with two conflicting
   sites in the sibling file. Per-entry is the only reading that fits the
   architecture (per-package needs a cross-entry pass that does not exist
   anywhere; a `[library]` is not type-checked at all). **Do you accept a
   struct that grounds per entry, and a declaring module that grounds
   nothing when checked alone?** The feature cannot be specified without
   this answer.

4. **The solver has nothing to unify.** Every one of the 11 signal-holding
   structs in the estate has exactly one construction site, so B184's
   refusal would never fire today. Does that read as *reassuring* (the
   rule is cheap because it is rarely tested) or as *damning* (a global
   mechanism for what is locally decidable)?

5. **Is [[B182]] most of the ask?** P17 reproduces the kolt cascade at one
   field: the root prints last, behind two generated-code errors. Once
   B182 lands and the refusal reads "write `SignalCell` here" as its
   first and only line, how much of B184's motivation survives?

6. **The LSP reservation** (§3.3), which is sharper than the item
   anticipates. The LSP analyzes each **open file as its own entry**, so
   opening the file that *declares* the struct yields **zero**
   construction sites — permanently, by the import graph's shape, not as
   a latency artefact. Hover on `h.count` there cannot report a type at
   all. Is that acceptable, or is it the thing that decides against the
   feature? The answer should be reconciled against
   [`lsp-snapshot-consistency.md`](lsp-snapshot-consistency.md) and
   [`analysis-reuse.md`](analysis-reuse.md) before any build.

7. **Library types, where the problem is worse than a choice.** A struct
   with a trait-typed field, exported from a library, has construction
   sites the library never sees — and a standalone `[library]` is **not
   type-checked at all** today (`check_library` verifies only the
   platform import contract, `main.rs:1713-1732`). So there is no
   analysis in which the library could ground the field. Either the
   grounded type becomes part of the library's published surface (which
   the trait spelling existed to avoid), or the same library type grounds
   differently in every consuming application. Which — or should
   trait-typed fields simply be refused on exported types?

8. **The field refusal's steer.** The reactive paper §7.2 specified a
   position-aware steer at a field — *"a struct field must name a concrete
   type. Write the implementation's name (`SignalCell<i32>`), or make the
   struct generic over it"* — and what shipped is the position-blind text
   (P1). Should that steer land now as its own small item, regardless of
   B184? It is the message every author hits on the way to asking for
   this feature.

9. **Scope, if it is built.** The paper's read is that B184 is an arc, not
   a lane: a new solver mode, a new class of diagnostic (N types across M
   sites), an LSP reconciliation, and a spec section. Does that match your
   sense of its size, or is there a smaller version — a per-package
   grounding with a single-site fast path — you would rather see scoped?
