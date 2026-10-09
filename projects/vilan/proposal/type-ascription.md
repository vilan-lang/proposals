# Type ascription — `EXP as T`, a constraint and never a cast, and per-stage hints in its spelling (B571, E278)

> Status: **DRAFT 2026-10-08 — for the owner's ruling.** Written by lane papers-b-48 of
> Order 48 against `vilan 0.45.0 (e75bc57c3)` = `origin/next` @e75bc57c, read at that
> commit in the worktree `vilan/.claude/worktrees/papers-b-48`. Nothing in the vilan tree
> changed. Every claim about today's behaviour is a probe that was run or a line that was
> read, and says which.
>
> Probes: `scripts/integration/sweeps/order48/papers-b-48/probes/b571/` (cited `aN`),
> re-run by `probes/run_all.sh <scratch>`, output in `probes/run_all.out`. The estate counts
> come from `papers-b-48/census/` (a walker over the tree's own lexer and parser).
>
> Related:
> - B571 (this paper) with the owner's two stamps of 2026-10-05, the second **RULED FINAL**
>   on the spelling; E278 (the editor half: per-stage inlay hints in this spelling);
> - B570 (`auto-annotations.md`: `as auto T`) and B569 (`named-tuple-fields.md`), written
>   beside it;
> - E227 (`inlay-hint-abbreviation.md`, built: `[hint(Trait<..>)]`, `~Pipe<T>` hints);
>   E261 (built: the `dyn Flow` steer on two pipe stages); B161 / B539 (a bare trait at a
>   `let` is checked and the binding keeps the concrete type); B495 (closure parameter
>   modes adopt the position's); B414 (contextual words); B248/B259 (a block-like form is
>   complete at its brace); R-k (a member dot is span-adjacent to its member).

## 0. The ask, and the answer up front

The owner's sketch:

```vilan,fragment
let x = SignalCell::new([ 1, 2, 3 ] as List<usize>);

let y = a() as A
    .b() as B
    .c() as C;
```

**Ruled (2026-10-05, final on the spelling):** `as` is a type CONSTRAINT (ascription), never
a cast. A `<` opens a generic list only when it touches the type name (`List<usize>`); a
spaced `as usize < y` is a comparison; the formatter writes both canonically. `as (T)` is
the escape hatch. Declined: `of`, `of<T>`/`as<T>`, `as(T)` required.

**The answer.**

1. **`EXP as T` types exactly as `let tmp: T = EXP` does** — the expected type flows into
   `EXP` (a literal `5 as f64`, an empty `[] as List<str>`, `None as Option<i32>`, a generic
   call's result), every coercion an annotated binding performs is performed (`stage as dyn
   Flow<i32>` erases: E261's inline spelling), and a mismatch is refused. **It is not a
   binding**: no copy, no drop point, no name. The value goes on to wherever `EXP` would have
   gone. It is a value, never a place.
2. **It is a POSTFIX in the chain tier**, so `.b()` continues after the type and
   `a + b as T` is `a + (b as T)`. Because vilan's binary operators are homogeneous, that
   reading and `(a + b) as T` type the same in every case but a comparison or an `is` test (both answer `bool`). `as` stays
   contextual (it is a legal name today, a07); it is read only after a complete operand,
   where no name can stand, the rule `then` already lives by.
3. **The type's end** is the type grammar's own end, with one new rule (the ruled whitespace
   rule) and nothing else. The formatter ALREADY writes every generic list tight and every
   comparison spaced (§5.2), so formatted code obeys the rule today; the estate has **0
   spaced generic lists**.
4. **Refusals teach once.** `n as f64` on an `i32` is refused with the conversion that exists
   (`n.as_f64()`, the message a11 already prints) and one sentence: `as` names a type, it
   does not convert. `obj as Concrete` on a `dyn` is refused: nothing narrows an object.
5. **E278**: on a chain split one stage per line, each line that ends a stage hints its type
   as `as T` — abbreviated `as ~Pipe<i32>` where E227 abbreviates — and a code action writes
   it: the full type, or the bare trait (`as Pipe<i32>`, which B161 checks and keeps
   concrete) for a hinted node, or `as auto T` once B570 lands.
6. **Estate: `as` in expression position = 0**, by construction: `let a = 1 as f64;` is a
   parse error today (a01), so every file that parses has none. All 24 `as` tokens in std,
   the corpus, the examples, the docs, kolt and the website are import aliases, and no
   binding or function is named `as`.

## 1. Ground truth (0.45.0)

| probe | program | result |
|---|---|---|
| a01 | `let a = 1 as f64;` | parse error at `1`: "expected `;` to end this statement" |
| a02 | `let xs = [];` (unused) | checks, runs — find B?1 |
| a02b | `let xs = []; print(xs.len());` | checks, runs `0`; natively refused at emission — find B?1 |
| a03 | `let o = None;` (unused) | checks; natively emitted as `let o_9696 = None;` untyped — find B?1 |
| a03b | `let xs = make();`, `fun make<T>(): List<T>` | "cannot infer 'T' for this call: nothing it is passed binds it, and its result is typed by it. Write the type — on the binding the result lands in (`let value: … = …`), or as the call's type argument (`make<…>(…)`)" |
| a04 | `let xs: List <i32> = [1, 2];` (spaced, type position) | checks — `<` after a type name opens generics whatever the spacing |
| a05 | `let xs = List <i32>::new();` (spaced, expression) | checks |
| a06 | `List<i32>::new()`, `pick<f64>(1, 2)` | check; generic head and generic call |
| a07 | `fun as(v: i32)`, `let as = 5; print(as);` | checks, prints `5` — `as` is a legal name |
| a08 | `let state: dyn Flow<i32> = match pick { true => Source::constant(1), false => cell.derive(..) };` | checks: the annotation erases both legs |
| a09 | the same with no annotation | E261's steer: "… two stages of different types meet only as one erased flow: annotate where the value lands, `let state: dyn Flow<T> = ..` …" |
| a10 | `let a: f64 = 5; let xs: List<str> = []; let o: Option<i32> = None;` | checks; `5`, `0`, `true` |
| a11 | `let n: i32 = 3; let x: f64 = n;` | "Expected f64, but got i32 instead. There are no implicit numeric conversions; convert with `.as_f64()`" |
| a12 | `let n = match true { .. }.max(0);` | refused: "a `match`, `if`, `for` or `{` form is COMPLETE at its closing brace …" (value position too) |
| a13 | `a < b`, `(a < b, c > b)` | comparisons, as expected |
| a14/a15 | `pick <f64>(1, 2)`; `a < b > (c)` | the first is a generic call; the second is ALSO read as a generic call, "cannot call this as a function: it is i32" — find E?1 |
| a16 | `let doubled: Pipe<i32> = cell.derive(\|v\| v * 2);` | checks; `doubled` keeps `Derive<SignalCell<i32>, i32, i32>` (B161) |
| fmt1 | `vilan fmt` over `List <i32>`, `a<b`, `List <i32>::new()` | rewritten to `List<i32>`, `a < b`, `List<i32>::new()` |

Read in the tree:

- `as` is a `Token::Ident`, not a keyword (`token.rs`: no `As`); the import alias reads it
  by word. The chain tier is `Parser::parse_chain` (`parsing.rs:5075`); the type grammar has
  one door, `Parser::parse_type` (`:7643`), whose generic list is
  `parse_generic_arguments` (`:6781`), which reads `<` with no adjacency test (a04).
- Contextual words with a type-head rule already exist: `dyn` is "the trait-object marker at
  a type head, except `dyn::`" (`parse_type_atom`, B414).
- The block-like rule (`refuse_block_like_continuation`, `:3278`) refuses an operator token
  or a `.` after a `match`/`if`/`for`/`{` brace; a word after it is not an operator token,
  so `match .. {} as T` today ends the expression at `}` and fails on `as`.

## 2. What it means

### 2.1 A constraint, typed as an annotated binding

`EXP as T` checks `EXP` with `T` as its expected type, through the same path an annotated
`let`'s initializer takes, and has type `T` — or, where the annotated binding would keep a
narrower type, that narrower type (§2.3). It **directs inference**: everything a10 shows an
annotation doing, `as` does inline, where no `let` is at hand:

```vilan,fragment
SignalCell::new([1, 2, 3] as List<usize>)   // the literal's elements are usize
total(values) / (count as f64)              // refused if count is not already f64 (§6)
make() as List<str>                         // a03b's hole, filled in place
None as Option<i32>
```

### 2.2 Not a binding

Rule 1 (`memory.md` §6.1) copies at every binding. An ascription adds none: `f(xs as
List<i32>)` passes `xs` exactly as `f(xs)` does, under the argument's own rule; `big as T`
in a chain copies nothing. It has no drop point and no name. For a resource it moves exactly
when the unascribed expression would.

### 2.3 The coercions, all of them the annotated binding's

| coercion | `let` today | `as` |
|---|---|---|
| an unsuffixed literal takes the type | `let a: f64 = 5` (a10) | `5 as f64` |
| an empty list, `None`, a generic call's result takes its arguments | a10, a03b | `[] as List<str>`, `None as Option<i32>`, `make() as List<str>` |
| a value becomes a trait object (`spec/types.md` §5.12: "explicit and positional") | a08 | `stage as dyn Flow<i32>`; a tuple re-built by projection as §5.12 says |
| a bare trait is checked and the concrete type KEPT (B161; B539 carries its arguments in) | a16 | `cell.derive(..) as Pipe<i32>` — still `Derive<..>` after |
| a named `fun` coerces to a matching closure type (§5.8) | `let t: \|str\| i32 = measure` | `measure as \|str\| i32` |
| a tuple variant coerces to a closure (§5.8) | `let f: \|i32\| Option<i32> = Some` | `Some as \|i32\| Option<i32>` |
| a closure literal's parameters adopt the position's modes (B495) | `let typed: \|&str\| void = \|c\| ..` | `(\|c\| ..) as \|&str\| void` |
| `Never` yields to the type | `let x: i32 = panic(..)` | `panic(..) as i32` |
| a labelled literal matches by name (B569) | `let p: (x: f64, y: f64) = (y = 7, x = 5)` | `(y = 7, x = 5) as (x: f64, y: f64)` |

**E261 inline.** `match pick { true => Source::constant(1), false => cell.derive(..) } as dyn
Flow<i32>` is a08 without the `let`, given §4.3's admission of `as` after a brace. The
steer a09 prints gains the inline spelling: "annotate where the value lands, `let state: dyn
Flow<T> = ..`, or ascribe the `match`: `match .. { .. } as dyn Flow<T>`".

## 3. The word

Ruled final; recorded here with the reasoning, because a reader from Rust will meet it.

- **Swift's `as` is exactly this**: an upcast or bridging coercion the compiler guarantees,
  with `as!` and `as?` for the checked casts. TypeScript's `as` is close (an assertion that
  changes no value, though it may lie). Rust's and Kotlin's `as` convert or cast.
- **vilan has no cast to collide with.** The conversions are METHODS (`n.as_f64()`,
  `spec/types.md` §5.8), and there is no downcast of a `dyn` (§5.12: "a `dyn Trait` never
  narrows back"). So every Rust/Kotlin reading of `x as T` is a refusal with a steer, never
  a silent different meaning (§6).
- **The near-collision to teach.** The conversion methods are spelled `as_*`. The book says
  it once: *the method converts, the keyword constrains* — `n.as_f64()` makes an `f64`;
  `n as f64` says `n` already is one. a11's existing message is the refusal's first half.
- **Declined** (2026-10-05): `of` (reads as membership; a new contextual word);
  `of<T>`/`as<T>` (a nested `>>` fights the lexer); `as(T)` required (sound, the second
  choice, but two characters on every use for an edge the formatter normalises); `:` (as
  in `let x: T`), which collides with B569's labels and reads badly mid-chain.

## 4. The grammar

### 4.1 The production

```text
chain    = path { call-suffix | postfix } ;
postfix  = "." member | "[" expression "]" | "!" | "(" … ")" | "?." member | "?"
         | ascription ;                          (* NEW *)
ascription = "as" [ "auto" ] ascribed-type ;     (* `auto`: B570 *)
ascribed-type = type ;   (* with §5.1's whitespace rule on every generic list in it *)
```

`as` is CONTEXTUAL (B414's discipline): it is read as an ascription only after a complete
operand, where no name can otherwise stand — vilan never puts two names side by side — so
`let as = 5;`, `fun as(..)` and `print(as)` keep working (a07), and `import a::{b as c}`
is untouched. The estate holds no binding, field or function named `as` (§9), so making it
a hard keyword would also cost nothing; contextual is still the cheaper promise to keep.

### 4.2 Chain continuation

After the type the chain goes on: `a() as A .b() as B .c() as C` is
`((((a() as A).b()) as B).c()) as C`. A type never contains a `.` (paths are `::`), a `[`
after a complete type is an index, and a `(` after a complete type is a direct call
(§5.3), so continuation is unambiguous. `x as T?` is `(x as T)?` and `x as T!` is
`(x as T)!` — types have no `?`/`!`. Over several lines the chain breaks before each dot
(R-k), so the owner's layout parses as written.

### 4.3 After a block-like form

a12: a `.` or an operator after a `match`/`if`/`for`/`{` brace is refused, in value position
too, because at a statement's head it would begin a new statement. `as` cannot begin a
statement. **Recommendation: admit `as` after the brace everywhere** — `match k { .. } as
dyn Flow<i32>` — since it has no second reading at any position; a `.` after the
ascription's type continues as in §4.2. The alternative (keep the rule uniform; write
`(match k { .. }) as T`) is Q4's fallback.

## 5. Where the type ends

### 5.1 The whitespace rule (RULED)

In an ascribed type, a `<` opens a generic list **only when it is span-adjacent to the name
before it** — the R-k discipline already used for `.member`, `/>`, `</` and `<<`/`>>`.

```vilan,fragment
xs as List<usize>        // generic list
n as usize < limit       // (n as usize) < limit
n as usize<limit         // a generic list `usize<limit>`: refused — `usize` takes no arguments
```

A generic list closes at its matching `>`; a `>` after that is a comparison, so `x as
List<i32> > y` reads. Inside a generic list the rule recurses (`HashMap<str, List<i32>>`
is all tight already). The refusal for a spaced list says what was read: "`as List` then
`< i32 >`: a generic list after `as` touches its type, `List<i32>`".

### 5.2 Why the rule costs nothing

- **The formatter already writes it.** `vilan fmt` rewrites `List <i32>` to `List<i32>`
  (type and expression positions) and `a<b` to `a < b` (fmt1). Formatted code obeys the rule
  today; only unformatted code can meet it, and there the refusal names the fix.
- **The estate has no spaced generic list.** Over std, the corpus, the examples, the docs
  fences, kolt and the website, every `<` written after a capitalised name with whitespace
  between is a comparison (4 sites, all corpus: `E < 2.719f`, `Less < Equal`,
  `Greater < Equal`, and one string); 0 are generic lists. (A regex census over the same
  991 files, comments stripped.)
- **Its reach.** The rule binds in ascribed types, the one type position followed by more
  expression. Everywhere else (a04, a05) a spaced generic list keeps parsing as today and
  the formatter tightens it. Extending the rule to EXPRESSION position (`a < b > (c)` read
  as comparisons, not as the generic call a15 shows) would give one rule for the language
  and fix E?1's message; it is Q3, separable, and breaks nothing formatted.

### 5.3 The other ends

| after `as` | the type ends | note |
|---|---|---|
| a path `T`, `m::T` | after the last segment, or after its tight generic list | `::` belongs to the path |
| `dyn Trait<..>` | as a path | B414's `dyn` rule |
| a tuple type `(A, B)`, a labelled one, a mapped `(U in T: F<U>)` | at its `)` | a following `(..)` is a direct call on the value; `.0` reads a slot |
| `(T)` | at its `)` | the ruled escape hatch: `n as (usize) < limit` |
| `[T; n]` | at its `]` | |
| `&T`, `&mut T` | after `T` | §6.3: views |
| a closure type `\|A\| R` | after `R`, read greedily as every closure type is | `R` is optional and may itself be a closure type; the formatter prints a closure type after `as` parenthesized, `as (\|i32\| i32)`, so a reader never has to find `R`'s end |
| `context ..` after a closure type | after the clause | `context` is contextual and cannot be confused with a continuation |

## 6. Precedence and its consequences

As a chain postfix, `as` binds tighter than every prefix and binary operator.

| written | reads | note |
|---|---|---|
| `a + b as f64` | `a + (b as f64)` | homogeneous `+`: `a` is constrained to `f64` too, so it types as `(a + b) as f64` would |
| `-x as f64` | `-(x as f64)` | the same type either way |
| `a < b as T` | `a < (b as T)` | the one tier where the readings differ: the comparison is `bool`. Write `(a < b) as bool` to ascribe the result |
| `await p as T` | `await (p as T)` | `T` must then be the PROMISE type. A mismatch whose `T` is the awaited type steers: "ascribe the awaited value: `(await p) as T`" |
| `&x as &T` | `&(x as &T)` | refused (a value is never a view); steer `(&x) as &T`. Rare: `as` on a place has no reason to name a view |
| `x as T is Some(let v)` | `(x as T) is …` | `is` is tier 10 |
| `c then a as T else b` | `c then (a as T) else b` | |

The `await` row is the wart of the postfix choice; the chain example cannot have it any
other way, and the steer makes it one edit.

## 7. Refusals

| written | refusal |
|---|---|
| `n as f64`, `n: i32` | a11's message, with `as` named: "`n` is `i32`, and `as` names the type a value already has; it does not convert. Convert with `n.as_f64()`." The fix applies (`check --fix` already applies a11's) |
| `x as Foo`, `x: Bar` | "`x` is `Bar`, not `Foo`" — with the chain STAGE named when it is one (§8) |
| `obj as Concrete`, `obj: dyn Trait` | "a `dyn Trait` never narrows back to the type it erased (§5.12); `as` cannot downcast. Keep the concrete value before erasing it, or `match` on an enum" |
| `s as i32`, `s: str` | the plain mismatch ("`s` is `str`, not `i32`"); a string is parsed, never converted, and the message says nothing more than a `let` would |
| `x as T` where `T` is a bare trait `x` does not implement | B161's message at a `let` |
| `(p as Point).x = 1` | "an ascription is a value, not a place: write `p.x = 1`" (§7.1) |

### 7.1 Value or place

**A value.** An ascription that coerces (erasure, a closure re-typing) has no place to write
through, and one that does not coerce adds nothing to `p.x = 1`. Reads through an ascription
are transparent (§2.2); writes are refused with the steer. This also keeps views out of it:
there is no `&mut (x as T)`.

## 8. Diagnostics

- **A mismatch at a chain stage names the stage**: "`.b()` returns `Derive<..>`, not `B`
  (ascribed here)", spanned on the ascription with a secondary label on the stage's call.
  That is the point of per-stage ascription: the error stops at the FIRST stage that
  disagrees instead of surfacing at the chain's end.
- **"Cannot infer" steers gain the inline spelling.** a03b's message becomes "… Write the
  type — on the binding the result lands in (`let value: … = …`), as the call's type
  argument (`make<…>(…)`), or ascribe the call (`make() as List<…>`)". The steers for an
  empty list and a bare `None` (find B?1 asks the checker to refuse those holes at all)
  carry the same third clause.
- **E261's steer** gains the inline spelling (§2.3).
- **A spaced generic list after `as`** (§5.1) and **a postfix-precedence surprise** (the
  `await` and `&` rows of §6) each have their own steer.
- Each new message is a ledger row (`diagnostics-ledger.md`).

## 9. The estate

- **`as` in expression position: 0.** a01 is a parse error, so no file that parses has one;
  std, the corpus, the examples, kolt and the website all check, and the docs fences that
  parse contain none.
- **Every `as` token, counted by the census walker over the lexer**: 24 (std 22, corpus 1,
  docs 1; kolt, the website and the examples 0) — all import aliases (`import
  std::web::style::{hover as hover_condition, ..}`-style lists, and `Response as
  HostResponse` in `std/src/rpc.vl:24`).
- **Names spelled `as`: 0** (a07 shows they are legal).
- **Spaced generic lists: 0** (§5.2).

Nothing breaks. The new surface is additive.

## 10. The formatter

- `as` with one space on each side; the type printed canonically (generic lists tight); a
  closure type after `as` parenthesized (§5.3).
- **A chain with an ascription on more than one stage breaks one stage per line**, each
  ascription at the end of its stage's line, the next line opening with `.`:

  ```vilan,fragment
  let y = a() as A
  	.b() as B
  	.c() as C;
  ```

  A single ascription follows the ordinary chain rule (on one line if it fits).
- `as (T)` is kept as written when it is the escape (`as (usize) < y`); a redundant `as (T)`
  with nothing after it prints as `as T`.
- The formatter stays syntactic; nothing here needs analysis.

## 11. E278 — per-stage inlay hints, in this spelling

**Today** a hint is per BINDING: `Document::landed_hints` (`vilan-lsp/src/document.rs:4672`)
walks `program.variables`, skipping annotated ones, and prints `: T`, or E227's
abbreviation `: ~Pipe<T>` where a `[hint]` gives one (`analyzer/hint_labels.rs`).

**E278** adds a hint per chain STAGE:

- **Where**: a method or pipe chain split one stage per line; the hint sits at the end of
  each line that ENDS a stage (not inside a multi-line argument), and not on a stage already
  ascribed (as an annotated binding gets none), nor on the last stage when the chain's value
  lands in an annotated position.
- **What**: ` as T`, spelled as hover spells the type, with E227's abbreviation —
  ` as ~Pipe<Option<str>>` — under the same `vilan.inlayHints.abbreviate` switch, the full
  type in the hint's tooltip.
- **The code action** ("Ascribe this stage") writes what makes the file read as the editor
  did, minus the marker that cannot be written:
  - an unabbreviated hint writes its type: `.b() as List<usize>`;
  - an abbreviated one writes the BARE TRAIT: `.derive(..) as Pipe<Option<str>>`. At an
    ascription a bare trait is B161's reading (a16): checked against the trait, the value
    keeps its concrete type, so the chain after it is unchanged and the ascription does not
    churn when an upstream stage is added;
  - with B570, a second action writes `as auto T`: the toolchain keeps it current (§12).
  - A "ascribe every stage" source action applies it down the chain.
- **The data**: the analyzer already types every call node; the hints need a per-stage
  label table (the call's id → its rendered type and its E227 abbreviation) for the focus
  file's multi-line chains, rendered by the same `hint_labels` renderer. No new analysis.
- **Pins** in `vilan-lsp/src/document.rs` beside `inlay_hint_abbreviates_a_hinted_node`
  (`:31393`): a three-stage chain hints each line; an ascribed stage hints nothing; a hinted
  node abbreviates; the code action's text round-trips through `vilan check` clean; the
  abbreviated action writes the bare trait and the following stage still resolves its
  concrete members.

## 12. Interactions

- **B570 (`auto`).** `as auto T` is an ascription the toolchain writes and keeps: it does
  NOT direct inference (B570's "output only"), it is checked equal to the stage's inferred
  type, a stale one is refused by `check`/`build` with a `--fix`. `as auto` with no type is
  filled. So `a() as auto A .b() as auto B` is E278's hints frozen into the file, and the
  first stage whose inferred type moves is the first stale one — the same localisation §8
  gives a written ascription, without directing anything.
- **B569 (labels).** An ascribed tuple type may carry labels; the type ends at its `)`; a
  labelled literal under `as` matches by name (B569 §4.1).
- **E227.** The hint abbreviates; the code action writes the bare trait (§11).
- **Opaque returns** (`opaque-returns.md`, ruled door (ii)). At an ascription there is "no
  other side", as at a `let`: a bare trait is checked and the concrete type kept. Opacity
  stays a property of returns.

## 13. Finds (filed to `newitems48-papers-b.json`)

1. **B?1** — a binding whose type nothing determines checks clean: `let xs = [];
   print(xs.len());` and `let o = None;` pass `vilan check` and run on JS; natively the first
   is refused at emission with F1 S1b's scope message (blaming the backend for a hole in
   inference) and the second is emitted untyped, `let o_9696 = None;` (rustc cannot infer
   it; not built here). The generic-call twin (a03b) is refused with a steer. Repro
   `finds/uninferable_binding_checks_clean.vl`. §8's steer extends that refusal.
2. **E?1** — `a < b > (c)`, spaced, reads as the generic call `a<b>(c)`: "cannot call this as
   a function: it is i32" (a15). No program is lost (the comparison chain is ill-typed:
   `bool` has no ordering), so this is the message. Repro
   `finds/comparison_read_as_generic_call.vl`. Q3 would remove the reading.

## 14. Open questions, each with a recommendation

- **Q1. Typing.** `EXP as T` types as `let tmp: T = EXP` — expected type in, every
  annotated-binding coercion (§2.3), mismatch refused — but adds no binding (no copy, no drop
  point). **Rec: yes, as stated.**
- **Q2. Precedence.** A chain postfix (`a + b as T` is `a + (b as T)`), or Swift's
  infix tier below arithmetic. **Rec: postfix**, which the per-stage chain requires, with the
  `await`/`&` steers of §6.
- **Q3. The whitespace rule's reach.** Ascribed types only, or also expression position
  (`IDENT < … > (` reads as comparisons when spaced, a generic call when tight). **Rec:
  ascribed types now (ruled); expression position as a separate small item after a census**
  — the formatter already writes every generic call tight, so it would break only
  unformatted code, and it fixes E?1.
- **Q4. `as` after a block-like form.** Admit (`match .. { .. } as dyn Flow<T>`), or keep
  B248's rule uniform and parenthesize. **Rec: admit everywhere** — `as` cannot begin a
  statement, so the rule's reason does not apply — and the E261 steer names the inline form.
- **Q5. Value or place.** **Rec: a value**; writes through an ascription refused with the
  steer (§7.1); reads transparent.
- **Q6. `as` as a word.** Contextual (as `then`), or hard. **Rec: contextual.** It costs
  nothing to keep a07's programs legal, and the estate has no such name either way.
- **Q7. The numeric refusal's fix.** `check --fix` rewrites `n as f64` to `n.as_f64()`, or
  only reports. **Rec: rewrite** — it is a11's fix, already machine-applied, and the
  author's intent is unambiguous once `as` cannot convert.
- **Q8. E278's code action on an abbreviated hint.** Write the full type, the bare trait, or
  nothing. **Rec: the bare trait** (B161: checked, concrete kept), so the written file reads
  as the hint did and does not churn with upstream stages; the full type stays one hover
  away.
- **Q9. A closure type after `as`.** Greedy, as everywhere, with the formatter
  parenthesizing; or parentheses required. **Rec: greedy + formatter parentheses** — the
  owner declined required parentheses for `as(T)` generally, and the formatter makes the
  canonical form the readable one.

## 15. Slices

| Slice | Content | Size | Needs |
|---|---|---|---|
| S1 | Parser: the `as` postfix in `parse_chain`, contextual; an ascribed-type mode of `parse_type` whose generic lists require adjacency (§5.1); `as` after a block-like brace (Q4); `Node::Ascribe`. Analyzer: the annotated-binding path with no binding (§2); value-only (§7.1). Both emitters see the inner expression. Pins: every row of §2.3 on both backends; the precedence rows; the whitespace rows; a07 still legal | M | — |
| S2 | Diagnostics: the refusals (§7), the stage-naming mismatch, the `await`/`&` steers, "or ascribe it" on cannot-infer and E261; `check --fix` for the numeric one; ledger rows | S | S1 |
| S3 | Formatter (§10); book: the tour's types page, grammar §3.6/§3.7, types §5.8's "the method converts, the keyword constrains" | S | S1 |
| S4 | E278: per-stage hints, the code actions, the source action, pins (§11) | S | S1 |
| S5 | `as auto T` | S | S1, B570's S1 |
