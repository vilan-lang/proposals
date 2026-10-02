# Keywords and attributes — which one a marker becomes, and the order they stack in (B485, B445)

> Status: **RULED 2026-10-01** — Q1–Q11 as recommended (the owner); the build is queued for Order 46. Drafted 2026-10-01 (R-j: a paper this order,
> nothing built). Tracker B485 (the owner's item) and B445 (the stacking order).
> Written by lane papers-45 of Order 45 against `vilan 0.42.0 (6e6830dfc)`,
> reading `next` @6e6830df. Nothing in the compiler or std changed. Every claim
> about today's behaviour is a probe that was run or a line that was read.
>
> The census of positions is syntax-45's, generated from the parser's tables:
> `scripts/integration/sweeps/order45/syntax-45/marker-census.md` (cited as
> "the census", §n). The site counts and the probes are this lane's:
> `scripts/integration/sweeps/order45/papers-45/probes/`, re-run by
> `run_all.sh <scratch>`, output in `run_all.out`. `census/census.py` counts
> every marker over std (`std/src` + `macro_std`, 71 files), `examples`
> (29 files) and kolt (29 files at 984a1df plus the owner's uncommitted edits);
> `census/wider_tree.out` adds the test corpus, the book and the Rust sources.
> `order/order_matrix.py` writes every stacking order the parser sees.
>
> Related: B413 (`resource` became `[resource]`), B414 and
> `contextual-keywords.md` (which words are reserved), B415 (`mod self;`),
> E227 (`[hint]`), G24 (`const let`/`const fun`), B318 (`visibility.md`),
> R-d/F60 (`[must_use]` on the pipe node types, this order).
>
> **Amendment (ruled 2026-10-02):** Q10 covers DECLARATIONS only. Field and variant attributes (`[expose]`, `[reactive(..)]`, `[internal(..)]`) stay inline on the member's own line.

## 0. The ask, and the answer up front

The language marks declarations two ways: keywords (`export`, `external`,
`async`, `const`, `macro`, `lazy`, `own`, `mut`, `dyn`, `borrows`, `context`,
`sync`) and bracket attributes (`[resource]`, `[platform(..)]`, `[deprecated]`,
`[internal]`, `[must_use]`, `[rpc]`, `[expose]`, `[service]`, `[derive(..)]`,
`[hint(..)]`, …). Nothing says which one a new marker becomes. B413 has already
moved one word across.

**The answer.**

1. **A rule that fits the language as it stands (§4).** A word is a KEYWORD
   when it changes what may be written after it, or when a reader needs it on
   the signature line to know how a use calls, passes, receives, awaits or
   evaluates the declaration. Everything else is an ATTRIBUTE: labels,
   generated companions, host bindings, platform fences, and the class of a
   declared type. One proviso applies: skipping an attribute must never mislead
   a reader silently, so every effect it has on a use is a diagnostic at that
   use.
2. **Under that rule nothing has to move (§5).** Every keyword passes one of
   the two keyword tests. Every attribute passes the proviso; the four nearest
   calls were probed (`[resource]`, `[trait_only]`, `[platform]` on an impl,
   `[must_use]`). The moves the item asks about cost from 3 to about 1,100
   sites each, and none of them helps a reader. The recommendation is that no
   marker changes spelling. `[resource]` stays an attribute.
3. **What does need to change is the ORDER (§6).** vilan is the only one of
   the six languages compared here that puts visibility *before* attributes.
   The parser takes exactly one order per declaration kind. It refuses every
   adjacent swap, and none of those refusals steers (29 of 29 probed). One
   gives a wrong steer (`import std::reactive::derive;`). The formatter then
   splits `export` from `fun` across lines. The proposal is attributes, then
   keywords, then the declaration word:
   - attributes in any order, which the formatter prints canonically;
   - keywords in one order, refused with a steer when swapped;
   - each attribute on its own line, and the keywords on the signature line.

   The canonical attribute order is today's production order, so no attribute
   changes its place among the others. Only `export` moves: 84 std sites, 33 inside Rust test sources and 3
   in the book, all rewritten by `vilan fmt`. examples and kolt have none.
   B445's `[platform("browser")] export impl` becomes the canonical spelling.

Eleven questions (§9), each with a recommendation. Three slices (§10).

## 1. The census

The census (§1, generated from `lexing::KEYWORDS`,
`lexing::CONTEXTUAL_KEYWORDS` and `parsing::KNOWN_ATTRIBUTE_MARKERS`) classes
every marker by what it changes. The five classes are the item's. Site counts
are `census.py`'s (std / examples / kolt). Positions are the census's §2.4,
abbreviated.

| marker | spelling | class (the census) | where it may sit | std | ex | kolt |
|---|---|---|---|--:|--:|--:|
| `export` | hard keyword | visibility/linkage | before any item; `export(in P)`; `export *;`; before `import` | 1,034 | 12 | 28 |
| `external` | hard keyword | visibility/linkage | before `fun` (a `;` body), `struct` (no body) | 537 | 74 | 3 |
| `async` | hard keyword | typing/semantics | before `fun`/`external`; expression prefix; closure type | 97 | 6 | 7 |
| `const` | hard keyword | typing/semantics | `const let`, `const fun`, expression prefix | 0 | 15 | 109 |
| `macro` | hard keyword | code generation | `macro fun`, `macro m(..)`, `macro { }` | 19 | 0 | 0 |
| `mut` | hard keyword | typing/semantics | binder (`mut x = ..`), parameter, `&mut` | 881 | 20 | 83 |
| `own` | contextual | ownership class | parameter head | 276 | 0 | 14 |
| `lazy` | contextual | typing/semantics | module `let`, parameter head | 5 | 0 | 2 |
| `dyn` | contextual | typing/semantics | type position | 20 | 0 | 0 |
| `borrows` | contextual | typing/semantics | after a return type | 3 | 0 | 0 |
| `context` | contextual | typing/semantics | after a return type or a closure type | 49 | 0 | 2 |
| `sync` | contextual | typing/semantics | opening a closure type | 38 | 0 | 1 |
| `[extern(..)]` | attribute | visibility/linkage | function prefix (with `external`) | 408 | 67 | 2 |
| `[platform(..)]` | attribute | visibility/linkage | most item heads; `mod self;` | 0 | 62 | 0 |
| `[must_use]` | attribute | tooling only | function prefix | 54 | 0 | 1 |
| `[deprecated(..)]` | attribute | tooling only | item heads, re-exports | 7 | 0 | 0 |
| `[internal(..)]` | attribute | tooling only | item heads, fields, variants | 25 | 0 | 0 |
| `[hint(..)]` | attribute | tooling only | struct/enum heads | 26 | 0 | 0 |
| `[resource]` | attribute | ownership class | struct, enum, trait heads | 26 | 0 | 0 |
| `[trait_only]` | attribute | typing/semantics | trait method prefix | 0 | 0 | 0 |
| `[derive(..)]` | attribute (std macros) | code generation | struct/enum heads | 10 | 8 | 12 |
| `[service(..)]` | attribute (std macro) | code generation | struct heads | 0 | 3 | 1 |
| `[client_service]` | attribute | code generation | struct heads | 0 | 0 | 0 |
| `[rpc]` | attribute | code generation (+ a Wire check) | method prefix | 0 | 12 | 12 |
| `[expose(..)]` | attribute | code generation | service fields | 0 | 3 | 0 |
| `[user_macro]` | attribute (user macro) | code generation | `struct`/`enum`/`fun` heads | 0 | 0 | 0 |

Notes on the table:

- **`[lints]` is not a source attribute.** It is the `vilan.toml` table that
  turns on `internal_use = "warn"`. The item lists it by mistake.
- **`[doc(hidden)]` is retired** and refused with a steer (B318). It is still
  in the known-marker table so that the steer can fire.
- **Two attributes have no customer.** `[trait_only]` and `[client_service]`
  have zero sites in std, examples, kolt and the test corpus. Only the
  compiler's own Rust tests use them (47 and 70 occurrences).
- **`[platform]` is the canvas bindings.** All 62 sites are in
  `examples/canvas`. std fences by directory (`std/browser/`,
  `std/process/`), not by attribute.
- **`const` has three roles and one word.** In kolt, 106 of its 109 sites are
  expression-prefix `const`; the other 3 are `const let`. std has none.

**The five classes do not decide the spelling.** Three of them are split today:

- **ownership:** `own` is a keyword, `[resource]` an attribute;
- **visibility/linkage:** `export`/`external` are keywords, `[extern]`/`[platform]`
  attributes;
- **code generation:** `macro` is a keyword, `[derive]`/`[service]`/`[rpc]`
  attributes.

So "a marker's class picks its spelling" is not a rule this language follows.
§4's rule is about where a reader needs the word, and it accounts for all
three splits.

## 2. What the near calls actually change (probed)

These four attributes and one keyword sit closest to the line, so each was
probed (`probes/census/`).

- **`[resource]`.** On a leaf with no `Drop`, `let b = a; … a.id` is refused
  ("use of `a` after it was moved: a resource has a single owner",
  `resource_erasure.vl`). Delete the attribute and the same program compiles
  and copies (`resource_erased.vl`). `Drop` on a type without the attribute is
  refused with a steer to add it (`resource_drop_on_data.vl`). Containment
  infers the class for aggregates (memory.md §6.8), so the attribute is
  *required* only at leaves and is a *check* everywhere else.
- **`[trait_only]`.** A call on the concrete type is refused with a steer
  ("reach it through a `Named` bound"). A call through the bound runs
  (`trait_only.vl`).
- **`[platform("browser")]` on an impl.** A node file that calls the method is
  refused, naming the impl's platform. The call does NOT silently fall back
  to a blanket impl (`platform_impl_dispatch.vl`). This was the one place an
  attribute could have changed dispatch without a diagnostic. It cannot.
- **`[must_use]`.** A dropped result warns. Deleting the attribute changes only
  that warning (`must_use.vl`).
- **`const fun`.** A plain `fun` is const-callable as well (G24 kept Zig's
  rule), so `const fun` changes no call site *today*. What it adds is a check
  at the declaration: a body that reaches `Date.now` is refused there, not at a
  distant `const` call (`const_fun.vl`, `const_fun_broken.vl`). It is a
  promise about how the function can be evaluated, written on the signature,
  and an API keeps that promise across versions. That makes it a signature
  word, the same way `const fn` is in Rust.

## 3. How other languages draw the line

No language has a purely semantic rule. Every one with attributes puts some
typing in them:

- **Rust:** `#[derive(Copy)]` decides move or copy, `#[repr]` decides layout,
  `#[non_exhaustive]` decides what a downstream `match` must cover.
- **Swift:** `@escaping`, `@Sendable` and `@MainActor` are typing.

They agree on the following, and the agreement is what vilan's split follows:

| | Rust | Swift | Kotlin | C# | Zig | vilan today |
|---|---|---|---|---|---|---|
| visibility | `pub` kw | `public` kw | `public` kw | `public` kw | `pub` kw | `export` kw |
| host declaration | `extern` kw | — | `external` kw | `extern` kw | `extern` kw | `external` kw |
| host binding detail | `#[link_name]` | `@objc(name)` | `@JsName` | `[DllImport(..)]` | `extern "lib"` | `[extern(..)]` |
| colouring | `async` kw | `async` kw | `suspend` kw | `async` kw | — | `async` kw |
| compile-time | `const fn` kw | — | `const val` kw | `const` kw | `comptime` kw | `const` kw |
| param ownership | `mut`/`&` | `consuming`/`borrowing`/`inout` kw | — | `ref`/`in`/`out` kw | — | `own`/`&`/`mut` |
| type class | `#[derive(Copy)]` attr | `~Copyable`, `indirect` | `data`/`value` kw | `ref struct`, `record` kw | `packed`/`extern struct` kw | `[resource]` attr |
| deprecation | `#[deprecated]` | `@available(*, deprecated)` | `@Deprecated` | `[Obsolete]` | (no marker) | `[deprecated]` |
| result use | `#[must_use]` | `@discardableResult` (inverse) | — | — | discard is an error | `[must_use]` |
| platform | `#[cfg]` | `@available(iOS ..)` | `expect`/`actual` kw | `[SupportedOSPlatform]` | (comptime) | `[platform]` |
| generation | `#[derive]`, attr macros | attached macros `@Observable` | `@Serializable` (plugin) | source-gen attrs | comptime | `[derive]`, `[service]`, macros |
| **order** | attrs, then `pub`, then fixed `const async unsafe extern` | attrs, then modifiers (any order) | annotations first by convention; modifiers any order | attrs, then modifiers (any order) | no attrs; fixed | **`export`, then fixed attrs, then fixed kws** |

In more detail:

- **Rust.** Keywords cover visibility, colouring, compile-time evaluation, the
  host declaration and the trait-object former. The function qualifiers come in
  one fixed order (`const async unsafe extern "C" fn`). Attributes cover
  everything about the item, some of it semantic (`derive(Copy)`, `repr`,
  `cfg`, `non_exhaustive`). Attributes come first and are in any order.
- **Swift.** Declaration modifiers are keywords in any order, including
  ownership (`consuming`, `borrowing`, `inout`) and `lazy`. Attributes (`@`)
  precede them and carry both metadata and some typing (`@escaping`,
  `@Sendable`, global actors). Move-only is spelled in the conformance list,
  `~Copyable`. That is neither a keyword nor an attribute.
- **Kotlin.** Modifiers are *soft* keywords, contextual the way B414 made six
  of vilan's. Kotlin spells more as keywords than anyone: host declarations
  (`external`), multiplatform (`expect`/`actual`), even generation
  (`data class`). Annotations hold deprecation, host names and
  compiler-plugin triggers.
- **C#.** Closest to vilan in shape. `[DllImport("lib")] static extern int f();`
  is vilan's `[extern("f")] external fun f(): i32;`: the keyword says the body
  is elsewhere, and the attribute says where. Attributes always come first.
  Modifiers may be in any order, and a style rule (IDE0036) fixes the order the
  formatter prints.
- **Zig.** No attribute syntax at all. Every marker is a keyword or a
  `comptime` construct, and discarding a non-void result is an error, so
  `must_use` is the default. Zig is the extreme case, and it shows what the
  bracket buys: a place for metadata that does not grow the keyword list.

**The lesson.** The keyword side is stable across all five: visibility,
colouring, compile-time evaluation, the host declaration and parameter
conventions. The attribute side is stable too: deprecation, host-binding
detail, platform availability and generator triggers. Type class is the one
contested row, with Rust on the attribute side and the others on the keyword
side. And in all four languages that have attributes, attributes come first.

## 4. The rule

Write a **keyword** when either test holds:

- **K1, grammar.** The word changes what may be written after it:
  - `export` wraps a statement and takes `(in PATH)` or `*`;
  - `external` licenses a `;` body;
  - `macro` declares a compile-time function, or opens an invocation or block;
  - `const` and `async` are also expression prefixes.
- **K2, signature.** A reader of the signature line, or of a type expression,
  needs the word to know how a use calls, passes, receives, awaits or
  evaluates the declaration:
  - `async`, `const fun`, `lazy`;
  - `own`, `&`, `mut` at a parameter;
  - `borrows`, `context`, `sync`, `dyn`.

Write an **attribute** for everything else about a declaration: its labels, its
generated companions, its host binding, its platform fence, and the class of a
declared type. One **proviso**: skipping the attribute while reading must never
mislead silently. Every effect it has on a *use* must surface as a diagnostic
at that use, or not at all.

How the splits in §1 fall out:

- **Ownership.** `own` is on the signature (K2). `[resource]` is about the
  type, and every effect it has on a use is policed (moves are refused, `Drop`
  requires it), so it passes the proviso.
- **Visibility/linkage.** `export` and `external` shape their syntax (K1).
  `[extern]` and `[platform]` are a binding and a fence, and the proviso holds
  (§2).
- **Generation.** `macro fun` declares a different *kind* of function (K1).
  The bracket triggers are attributes, and a missing generated item is a loud
  error by construction.

The rule is about reading, not about reserving words, and two facts make that
safe:

- **B414 made keywords cheap.** A new word can be contextual: it reads as a
  keyword only at its position and stays a name everywhere else. Reserving an
  identifier is no longer the cost of a keyword.
- **The bracket is shared with user macros.** A built-in attribute name is
  excluded from user macro attributes (`is_known_attribute_marker`), so a new
  attribute reserves a macro name, just as a keyword reserved an identifier.

Neither spelling is free, and neither is expensive. That leaves only the
reader's question.

**The rule and the order (§6) are the same idea.** Attributes sit *above* the
signature, and keywords sit *in* it. A reader who skips every bracketed line
still reads every use correctly. The keyword line is the contract.

## 5. The candidate moves, each way, with what each would cost

The rule moves nothing. The item names these candidates, and each is weighed
below. Costs are the sites a codemod would touch: std / examples / kolt, then
the test `.vl` corpus / the book / Rust test sources
(`census/wider_tree.out`; the Rust column counts string occurrences in
`crates/`, most of them `.vl` source held in Rust tests).

### 5.1 Keyword → attribute

| move | rule | sites (std/ex/kolt; tests/book/Rust) | rec |
|---|---|---|---|
| `export` → `[export]` | K1 holds (wrapper, `(in ..)`, `*;`, re-export) | 1,034 / 12 / 28; — / many / many | **stays** |
| `external` → `[external]` | K1 holds (the `;` body) | 537 / 74 / 3; 2 / 59 / 366 | **stays** |
| `const fun` → `[const]` | K2 holds (a promise callers rely on, §2) | 0 / 0 / 0; 0 / 5 / 58 | **stays** |
| `lazy let` → `[lazy]` | K2 holds (evaluation; and `lazy` at a parameter changes the call) | 0 / 0 / 2; 0 / 4 / 57 | **stays** |
| `macro fun` → `[macro]` | K1 holds (a compile-time function; `macro m(..)`/`macro { }` are expression forms) | 19 / 0 / 0; 6 / 5 / 121 | **stays** |

- **`export`.** All five other languages spell visibility as a keyword. vilan's
  `export` is also grammar: `export import a as b` re-exports, `export *;`
  marks the whole module, and `export(in pkg)` narrows the reach. An attribute
  would need all three as argument forms. **Door (a)**, stays. **Door (b)**,
  `[export]`, about 1,100 corpus sites for no reader gain. **Rec: (a).**
- **`external`.** It licenses the `;` body, which is K1. Kotlin, C#, Rust and
  Zig all use a keyword. **Rec: stays.** §5.3 takes up its pairing with
  `[extern]`.
- **`const fun`.** It is the one keyword that changes no call site today,
  because plain funs are const-callable. It stays because it is a promise on
  the signature: removing it later is a breaking change for any caller that
  evaluates the function in a `const` position. Rust's `const fn` is a keyword
  for the same reason. Zero corpus sites either way. **Rec: stays.**
- **`lazy` and `macro`.** Both are K2 and K1 respectively. **Rec: stay.**

### 5.2 Attribute → keyword

| move | rule | sites (std/ex/kolt; tests/book/Rust) | rec |
|---|---|---|---|
| `[resource]` → contextual `resource struct` | proviso holds (§2) | 26 / 0 / 0; 8 / 50 / 536 | **stays an attribute** |
| `[platform(..)]` → a keyword | proviso holds (§2) | 0 / 62 / 0; 0 / 29 / 188 | **stays** |
| `[trait_only]` → a keyword | proviso holds (§2); the census classes it typing | 0 / 0 / 0; 0 / 0 / 47 | **stays** |
| `[must_use]` → a default (Zig/Swift) | not a spelling question | 54 / 0 / 1 | **out of scope** (R-d this order) |
| `[derive]`, `[service]`, `[rpc]`, `[expose]` | generation; a missing item is loud | 10+0+0+0 / 8+3+12+3 / 12+1+12+0 | **stay** |
| `[deprecated]`, `[internal]`, `[hint]` | tooling only | 58 / 0 / 0 | **stay** |

- **`[resource]`.** This is the item's real question, now that `[resource]`
  changes move semantics and marks traits.

  The case for a keyword:
  - it changes what every use may do;
  - Kotlin, C# and Swift spell type class as keywords or conformances;
  - with B414, `resource` before `struct`/`enum`/`trait`/`external` can be
    contextual, so `Resource<T>` and a function named `resource` would not be
    bitten. That bite was B413's reason.

  The case for the attribute:
  - the rule's proviso holds: a reader who misses `[resource]` cannot misread
    a use, because a second use after a move is refused at that use, and a
    destructor needs the attribute to exist;
  - containment infers the class for every aggregate, so the attribute is a
    *check* on most of its sites;
  - Rust spells the same decision `#[derive(Copy)]`, an attribute;
  - B413 ruled this five days ago and moved 405 sites. Moving back touches
    26 std sites, 8 in the test corpus, 50 in the book and 536 occurrences in
    Rust test sources.

  **Door (a)**, it stays an attribute. **Door (b)**, contextual
  `resource struct`. **Rec: (a).** The rule accounts for it, and nothing a
  reader does changes.
- **`[platform(..)]`.** Kotlin's `expect`/`actual` is the only keyword
  precedent. It is a fence, and the proviso holds: a call across platforms is
  refused, never re-dispatched (§2). **Rec: stays.**
- **`[trait_only]`.** The one attribute the census classes as
  typing/semantics. It narrows where a method resolves, and an attempt to reach
  it the wrong way is refused with a steer, so the proviso holds. It has no
  customer outside the compiler's tests. **Rec: stays.** It might be worth
  asking whether it should exist at all, but that is a separate question
  (Q11).

### 5.3 One fact written twice: `[extern(..)]` with `external`

`external fun` without an `[extern(..)]` binding is refused ("an external needs
an `[extern(..)]` binding saying what the host calls it"). `[extern]` without
`external` is refused too. Each of the 542 `external fun` sites therefore
writes the same fact twice: the body is the host's. The doors:

- **(a) Keep both.** This is C#'s `[DllImport] extern`. The keyword sits on
  the signature line (K1, the `;` body) and the binding detail sits above it.
- **(b) The binding implies the keyword:** `[extern("f")] fun f(): i32;`.
  Cost: `external` removed from 542 `external fun` corpus sites, and the `;`
  body is then licensed by an attribute, which breaks K1.
- **(c) The keyword takes the binding:** `external("f") fun f(): i32;`. Cost:
  477 corpus rewrites of `[extern(..)]` (plus 2 / 46 / 249 in the tests, the
  book and the Rust sources), and the grammar for four binding forms in
  keyword position.

**Rec: (a).** The pair is checked in both directions, so it cannot drift.

## 6. One ORDER for stacked markers (B445)

### 6.1 Today

The parser takes one total order per declaration kind:

- **fun:** `export`, then the ordered attribute prefix (`[deprecated]`,
  `[internal]`, `[extern]`, `[must_use]`, `[rpc]`, `[trait_only]`,
  `[platform]`), then `async`, then `external`, then `fun`;
- **struct:** `export`, then `[derive]`/`[service]`/a user macro, then
  `[deprecated]`, `[internal]`, `[hint]`*, `[platform]`, `[resource]`, then
  `external`, then `struct`.

The census (§3) states the full order for each position. `parse_function`'s doc
comment calls the attribute order "a faithful quirk". `grammar.md` §3.2 makes
`export` first normative: "A declaration carrying attributes is wrapped as a
whole, with the marker ahead of them".

**Every inversion is refused, and none of the refusals steers.**
`order/order_matrix.py` writes each kind's full canonical stack and then every
adjacent swap of it. The full stacks all check clean. Of the 29 swaps:

- **Inverted attribute stacks** are read as an *expression statement* (a list
  literal, then an index). They report "cannot find 'deprecated' in this
  scope" or "expected `;` to end this statement".
- **`[derive(PartialEq)] export struct`** steers wrongly: "cannot find 'derive'
  in this scope; import it first (`import std::reactive::derive;`)".
  `std::reactive::derive` is the pipe combinator.
- **`[resource]` before a label or `export`** says "it may label only a
  `struct`, an `enum` or a `trait` declaration", although it is on a struct.
- **In an `external fun` stack**, the misparse drops the `[extern]` binding,
  and the *first* error printed is the semantic one ("`external fun f` names no
  body: an external needs an `[extern(..)]` binding"). The parse error comes
  second.
- **`external async fun`** reports "function 'f' must have a body or be
  declared `external`", although it is declared `external`.
- **`const fun` and `const let` take no attribute in either order**
  (`const_labels.vl`, and the census's "do not stack" lists). A `const fun`
  cannot be `[deprecated]`, so the deprecation policy cannot reach one. This is
  a find (§8).

**The formatter splits the signature.** `vilan fmt` on today's canonical
stacks (`order/fmt_today.vl` → `fmt_today.out`) keeps `export` glued to the
FIRST attribute and gives each later attribute its own line:

```
export [deprecated("use g")]
[must_use]
[platform("node")]
async fun f(): i32 {
```

`export` and `fun` end up four lines apart. For a type, `[resource]` stays on
the declaration line (`[resource] struct H {`), because until B413 it was a
keyword in that slot. In std, 508 attribute lines already stand alone and 26
share a line with their declaration word (all 26 are `[resource]`).

### 6.2 The proposal

**One order: attributes, then keywords, then the declaration word.**

```
[deprecated("use g")]
[must_use]
[platform("node")]
export async fun f(): i32 { … }

[hint(Pipe<U>)]
[resource]
export struct Derive<S, T, U> { … }
```

1. **Attributes are accepted in any order** before the keywords. The formatter
   prints them in one canonical order, today's production order, so no
   attribute moves:
   - generation: `[derive]`, `[service]`, `[client_service]`, user macro
     attributes;
   - labels: `[deprecated]`, `[internal]`, `[hint]`;
   - binding: `[extern]`;
   - checks: `[must_use]`, `[rpc]`, `[trait_only]`;
   - fence: `[platform]`;
   - class: `[resource]`.

   A user macro attribute receives the item with every built-in attribute,
   wherever each was written.
2. **Keywords take one order:** `export`, then `const` or `lazy`, then
   `async`, then `external` or `macro`, then the declaration word. A swapped
   pair is refused with a steer that names the order ("write `export async
   external fun`") instead of "cannot find" or "expected `;`".
3. **Layout:** each attribute on its own line above the signature, and the
   keywords and the declaration word on the signature line. That includes
   `[resource]`, which today sits on the declaration line in the slot the old
   keyword held. Keeping it there would need a slot for one attribute *after*
   the keywords (`export [resource] external struct`), an exception to the
   one order. Under §4 the class is not a signature word, so it goes above with
   the other attributes (Q10).

**Why attributes first:**

- **Precedent.** All four languages with attributes put them first. A
  newcomer's `[platform("browser")] export impl` (B445's exhibit) is the
  expected spelling, not a mistake.
- **The signature line.** The keywords a caller needs (§4, K2) end up on one
  line with the name, so `export async fun name(` can be read, and grepped, as
  one line. Today the formatter puts `export` on a different line from `fun`
  whenever attributes are present.
- **Attributes are about the whole statement, `export` included.** A
  `[deprecated]` re-export already reads that way:
  `[deprecated("use pkg::inner::DeltaCursor")] export import … as KeyedCursor;`.

**What the other order had going for it:**

- **The wrapper.** `export` is a statement wrapper, so writing it outermost
  mirrors the tree. But the parser reads the attributes, then `export`, then
  the declaration, and attaches the attributes to the declaration. Nothing
  else in the tree has to change.
- **`^export` finds the surface.** It still does, because with attributes on
  their own lines `export` starts the signature line.

### 6.3 Migration

| step | release | what |
|---|---|---|
| 1 | v0.43.0 | The parser accepts attributes in any order, before or after `export` (B445 as briefed: "accept both orders"). `vilan fmt` rewrites to the canonical order and layout. A swapped keyword pair is refused with a steer. |
| 2 | v0.43.0 | std reformatted: 84 `export [..]` sites (82 declarations, 2 deprecated re-exports), and the 26 one-line `[resource]` heads reflowed. The Rust test sources' 33 `export [` strings are rewritten or left, since the parser still accepts them. The book's 3 are rewritten. examples and kolt have none (kolt uses `export *;`). |
| 3 | v0.44.0 | `export` before an attribute is refused, with a steer and a quick fix (the deprecation policy's one release). |

`grammar.md` §3.2's sentence reverses. The `function`, `struct`, `enum`,
`trait`, `impl` and `labelled-let` productions gain a free-order attribute
group ahead of `export`.

## 7. Risks

- **Free attribute order loses the parser's grip on what it is reading.**
  Today the fixed prefix is what makes `[x]` at a statement head an attribute
  rather than a list literal. Free order means peeking past each `]` for the
  next `[` or a keyword. This is an LL(k) lookahead the parser already does for
  user macro attributes (`parse_macro_attributed_item`). The expression reading
  of `[a] [b] fun` is never a valid program.
- **Two orders for one release** means diffs that only reorder. The formatter
  makes that a single commit per package.
- **The B445 lane (syntax-45) builds before this is ruled.** Its brief says
  "accept both orders" when the paper has not landed, and this paper's step 1
  *is* accepting both orders, so nothing the lane builds needs undoing.

## 8. Finds (met while probing, for the integrator to file)

1. **Out-of-order markers give no steer, and one gives a wrong one.** This is
   B445 generalised, M (diagnostics). All 31 adjacent swaps are refused with
   "cannot find '<attr>' in this scope" or "expected `;`". The misparse can put
   a later semantic error first. `[derive(..)] export struct` steers to
   `import std::reactive::derive;`. `[resource] [deprecated(..)] struct` says
   `[resource]` "may label only a struct, an enum or a trait". Repro:
   `probes/order/order_matrix.py` and `order_matrix.out`. Rec: §6.2 makes most
   of these legal. A swapped keyword pair gets a steer that names the order.
2. **`const fun` and `const let` cannot carry `[deprecated]`, `[internal]` or
   `[must_use]` in either order.** M, because the deprecation policy cannot
   reach a const function. Repro: `probes/census/const_labels.vl`. Rec: the
   labels lead the `const` declaration as they lead a `fun`, which is §6.2's
   order.
3. **A stale steer predates G24.** `const x = 1;` in a body says "Vilan has no
   const declarations; write `let x = const ..`". `const let` exists and is
   legal there (the census, B4). L. Repro: `probes/census/const_stale_steer.vl`.
   Rec: steer to `const let x = 1;`.

## 9. Open questions, each with a recommendation

- **Q1. The rule.** K1 (grammar) and K2 (signature) make a keyword. Everything
  else is an attribute, under the proviso that skipping it never misleads
  silently. **Rec: adopt it,** and write it into the spec beside the keyword
  table, so that the next marker is decided by it.
- **Q2. `export` and `external` stay keywords.** **Rec: yes** (K1; every
  comparable language).
- **Q3. `[resource]` stays an attribute.** **Rec: yes** (door (a), §5.2). The
  proviso holds, B413 stands, and reversing it costs about 620 sites.
- **Q4. `const fun` and `lazy` stay keywords.** **Rec: yes** (K2: a promise
  and an evaluation).
- **Q5. `[extern(..)]` and `external` stay a pair.** **Rec: yes** (door (a),
  §5.3).
- **Q6. The order is attributes, then keywords, then the declaration word.**
  **Rec: yes** (§6.2). It reverses `grammar.md` §3.2's "marker ahead of them".
- **Q7. Attribute order.** **Rec: free order,** formatter-canonical in
  today's production order (no attribute moves).
- **Q8. Keyword order.** **Rec: one order** (`export`, `const`|`lazy`,
  `async`, `external`|`macro`), refused with a steer when swapped. There are at
  most three keywords per declaration, and they are the signature.
- **Q9. Migration.** **Rec:** both orders in v0.43.0 with the formatter
  rewriting; the old order refused with a quick fix in v0.44.0.
- **Q10. Layout, and where `[resource]` sits.** **Rec:** each attribute on
  its own line, `[resource]` included; the keywords and the declaration word on
  the signature line. The alternative, `[resource]` kept on the declaration
  line after the keywords, is a one-attribute exception to Q6's order.
- **Q11. `[trait_only]` and `[client_service]` have no customer.** **Rec:
  keep both, untouched.** They are transport-rpc's (§3.2, §9.3), and the
  question is that paper's, not this one's.

## 10. Slices

| slice | content | size | owner |
|---|---|---|---|
| S1 | Parser: attributes in any order, before or after `export` (B445). A swapped keyword pair refused with a steer naming the order. `const fun`/`const let` take the label prefix (find 2). The stale `const` steer (find 3). Ledger rows `NEW`. | S | syntax lane (lexing.rs/parsing.rs) |
| S2 | Formatter: canonical attribute order and §6.2's layout. std reformatted (84 sites). `grammar.md` §3.2/§3.3 and the EBNF. The spec gains §4's rule. | S | syntax lane |
| S3 | v0.44.0: `export` before an attribute refused, with a steer and a quick fix. | XS | syntax lane |

Nothing here changes what any program means. S1 and S2 are additive. S3 is the
one breaking step, and it waits a release.
