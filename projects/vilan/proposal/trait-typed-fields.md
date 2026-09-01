# A trait annotation on a struct field, grounded once program-wide (B184)

> **Status: PROPOSED 2026-09-01** — DISCUSSION REQUIRED before any build
> (work order 24, lane papers; tracker item [[B184]]).
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
