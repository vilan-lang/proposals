# A first-class `css { … }` block — the element syntax's twin on the style side (kolt.local 016)

> Status: **S1 AND S2 SHIPPED 2026-08-28** (cycle 36, order 18, lane
> `css-block-s2`; §11 carries each slice's record). All six open questions
> RULED 2026-08-28 (§12), Q3 among them — the `css` keyword is TAKEN, so S2
> builds on a real keyword rather than the contextual gate the draft
> designed. Prior status: DRAFT 2026-08-27 (cycle 33, work order 15, lane
> `css-block-paper`), for owner review; design-only, no code, no suite.
> Tracker: `../projects/kolt.local/tracker/items/016.md`; it should become
> PROPOSED with this paper as its record. The direction was RULED
> 2026-08-26 — the paper is the deliverable that ruling asked for, not a
> re-litigation of it.
>
> The owner's ruling, verbatim (2026-08-26): *"using DSL for this would be
> poor. Instead it should fall under the same class as the element syntax
> with first-class support. Beyond syntax highlight, we get all of the other
> language features: auto complete, code actions, inline diagnostics, etc."*
>
> That makes completion, code actions and inline diagnostics **requirements
> of the design**, not niceties, and it rules out a macro or string DSL as
> the implementation class. Both obligations are discharged below: §7 is the
> three features, §1 is the head-on answer to the recorded rejection
> (`ui-styling.md` §8) that the item flags.
>
> **The paper's one-sentence answer**, since §5 is the question everything
> else hangs on: a `css` block is **sugar over the `style()` chain exactly as
> element syntax is sugar over the `view` chain** — a pure pre-analysis
> desugar to `Style::raw` and the condition combinators, name-blind, with
> **no third emission channel, no new emitter code, and not one byte of
> change to the atomic model**.

---

## 0. The charter, and what changed since the item was filed

Item 016 was held for one cycle on purpose. `std::style::declare` shipped in
Order 13 (kolt.local 032), and it is the surface this paper has to argue
against — not a hypothetical one. As it stands today in
`vilan/std/src/style.vl`:

```vilan
struct Declarations { text: str }

fun declarations(): Declarations
impl Declarations {
    fun raw(self, property: str, value: str): Declarations
    fun color(self, property: str, value: Color): Declarations
    fun length(self, property: str, value: Length): Declarations
}

fun declare(selector: str, body: Declarations)
```

used as:

```vilan
const declare(i"[data-theme=\"{id}\"]", declarations()
    .color("--color-ink", Color::hex("#fafafa"))
    .color("--color-ground", Color::hex("#161616")))
```

`declare` is a good API and this paper does not propose retiring it. It is
const-only, mints no class, joins no `Style`, rehashes nothing, and its
ordering is a stated invariant (`@layer vilan`, so an unlayered `Style`
always wins) rather than a byte-order convention. Everything 032 ruled
stands.

But read that call again with the owner's ruling in hand. The selector is a
string. The property name is a string. The value, in the `raw` case, is a
string. **Every token that a CSS author actually types is inside a string
literal**, and a string literal is opaque to the whole toolchain: no
completion on `--color-ink`, no hover, no go-to-def, no highlighting, and —
§7.3 shows this is worse than it sounds — no diagnostic anchored anywhere
near the mistake. `declare` is an *expression* form that nonetheless pays the
entire DSL toll. That is not an argument against `declare`; it is the
argument for this paper, and it is what §1 turns on.

---

## 1. The recorded rejection, answered

`ui-styling.md` §8 rejected the macro DSL — *this proposal's own first
draft* — in these words:

> **The macro DSL** (this proposal's own first draft) — semantics identical,
> but every consumer pays the DSL toll: no hover/go-to-def/typed diagnostics
> inside the block, custom syntax highlighting, macro-grade error spans. The
> expression form gets the whole toolchain for free and composes with
> functions/impls/match natively.

The item flags this and is right to. Here is the answer, in three moves.

### 1.1 The toll is a property of *macros*, and mechanically so

Every item on §8's list follows from one fact about vilan macros: **a macro
body has no tree.** `parse_argument_span` keeps only spans; the formatter
proves it by recovering macro arguments from the source text rather than
reprinting them (`Printer::print_argument_spans`, `formatter.rs:3589` — *"A
macro's arguments are syntax (the parser keeps only their spans, not a
tree)"*). No tree means no hover target, no definition to jump to, no typed
node to diagnose, no semantic tokens, and error spans no finer than an
argument. `element-syntax.md` §8 states the same mechanism from the other
side: macro arguments *must parse as vilan expressions before the macro sees
them*, and markup does not.

So §8's true principle is not "expression form good, block form bad". It is
**tree good, no-tree bad** — and core grammar, lowered before analysis, has a
tree. That is exactly what the element syntax demonstrated: it is a block
form, it is not an expression form, and it has hover, go-to-def, typed
diagnostics, semantic tokens, linked editing, and completion inside its head.

### 1.2 §8's positive claim is *satisfied*, not overturned

§8's other half — "the expression form … composes with functions/impls/match
natively" — is a requirement this design meets rather than an argument it has
to defeat. A `css` block **is an expression**; it evaluates to a `Style`; it
is written inside `const` like every other style; `+` still combines named
styles; `match` still selects between them; a const function still returns
one. It composes natively because it lowers to the chain that composes
natively (§5). The block does not replace the chain, deprecate it, or change
it — the two forms mix freely in one file, one function, one expression,
which is the same sentence `element-syntax.md` opens with about the `view`
chain.

Nothing in §8 is reversed. The rejected alternative was `macro css!(…)`, and
this is not that.

### 1.3 The sting: §8's own argument now cuts against the shipped `declare`

This is the part the item asked for and the part that matters.

§8's worst-named toll is "macro-grade error spans". Measure `declare`'s
against it. Const-time validation in `style.vl` is a `panic`, and
`const_eval.rs`'s `State::failure_error` (line 1174) says what a panic
becomes:

> *"The primary span stays the `const` expression — the interpreted tree
> carries no positions, so there is no inner span to move to (const-eval.md
> §8.2)."*

So a typo'd property in a declaration block:

```vilan
const declare(":root", declarations()
    .raw("--color-ink", "#fafafa")
    .raw("colr", "red"))                  // ← the mistake
```

squiggles **the whole `const declare(…)` expression, every line of it**, with
the message `const evaluation failed in \`check_declaration\`: …` and a
related-information jump into `vilan/std/src/style.vl`. Not the `colr`
token. Not even the `.raw(…)` link. The user's own code is underlined
wholesale and the only precise location offered is inside std.

That is **coarser than macro-grade**. A macro at least retains argument
spans; const-eval retains none, because `js::Node` carries no position on any
variant and the const pass evaluates the compiled tree (const-eval.md §8.2,
where finer spans are a recorded, expensive, deferred open question).
`vilan/docs/appendix/errors.md:663` documents the consequence to users
already.

Which yields the discharge in one line:

> **§8 rejected the macro DSL because it had no tree. `declare`'s strings
> have no tree either, so the shipped expression form pays every toll §8
> named and one worse. The `css` block is the first surface in this area
> that actually escapes the toll, because it is the first one made of
> tokens.**

Under the block, `colr` is a token with a span, checked before const-eval
ever runs, and the squiggle is on `colr`. Token-grade — finer than
macro-grade, and far finer than what ships today.

---

## 2. What it looks like

```vilan
import std::ui::style::{ style, space, Color, Display };

let card = const css {
    display: flex;
    flex-direction: column;
    gap: {space(4)};
    padding: {space(4)};
    background: {Color::gray(50)};
    border-radius: {Length::px(8)};

    .hover {
        background: {Color::gray(100)};
    }

    .md {
        padding: {space(6)};
    }

    .dark {
        background: {Color::gray(900)};
    }
};

let active = const css { padding: {space(6)}; };

view.class(card + active);   // padding resolves to space(6) — LAST WINS, always
```

and it is exactly, byte-for-byte in the emitted CSS, this:

```vilan
let card = const style()
    .raw("display", "flex")
    .raw("flex-direction", "column")
    .raw("gap", space(4))
    .raw("padding", space(4))
    .raw("background", Color::gray(50))
    .raw("border-radius", Length::px(8))
    .hover(style().raw("background", Color::gray(100)))
    .md(style().raw("padding", space(6)))
    .dark(style().raw("background", Color::gray(900)));
```

The second form is what the desugar produces. The first is what an author
who has ever written CSS can read without being taught anything.

---

## 3. The one rule

Element syntax has one rule and the whole feature falls out of it. So does
this one, and it is deliberately the *same shape*:

> **A `css` block builds one `Style`. An undotted `property: value;` is a
> declaration and lowers to `.raw(property, value)`. A dotted `.name { … }`
> is a condition combinator and lowers to `.name(style() … )`, the block's
> own chain passed as its last argument.**

The dot is load-bearing twice over, as it is in the element head.
Semantically it marks the boundary between *what this style declares* and
*under what condition it declares it*. Mechanically it is the disambiguator
that keeps the desugar **name-blind**: undotted always means a declaration,
dotted always means a combinator, so the grammar never consults `Style`'s
method list — and adding a method to `Style` can never change what existing
`css` means.

Three consequences worth stating out loud, each mirroring one the element
syntax already banked:

- **Every future condition combinator works on the day it ships, with no
  grammar change.** `.hover`, `.focus`, `.active`, `.disabled`, `.dark`,
  `.sm`/`.md`/`.lg`/`.xl`, `.attribute("data-open", "true")`, `.pseudo("first-child")`
  all work now because they exist now; a `within(…)` or a `children(…)`
  (§9) would work the day it lands.
- **Nesting order is combinator order.** `render_rule` nests the four
  condition axes *"the way CSS nests them — media outermost, then the dark
  ancestor selector, then the attribute suffix, then the pseudo-class"*, and
  the outside-in call order (`md(dark(attribute(…, hover(…))))`) is required
  at the call site with a const-time refusal for any other order. In a block
  the textual nesting **is** that order, so the shape that is legal is the
  shape that reads correctly, and the refusal becomes a lowering-time
  diagnostic with a real span instead of a const-eval panic.
- **Written order is preserved; nothing is reordered, deduped or merged at
  lowering.** What you write is the chain you get. (Whether `vilan fmt` may
  *canonically reorder* it afterwards is §8, and the answer is subtler than
  it looks.)

---

## 4. Grammar & lexing

### 4.1 The lexer does not change — and here that costs something

`element-syntax.md` §3 opens with *"the lexer does not change"*, and the
architecture that forced it still holds: lexing is context-free by spec
(`lexical.md` §7) and by construction (`tokenize()` completes before the
parser exists). This design keeps that rule. It is not free.

What the lexer already admits, checked against `crates/vilan-core/src/lexing.rs`:

- **Dimensions lex as one token.** `read_optional_suffix` (line 348) gives
  `1px` → `Number("1", None, Some("px"))` and `1.5rem` →
  `Number("1", Some("5"), Some("rem"))`. CSS's own value shape was already a
  vilan token. This is a genuine gift and it is why the value grammar is
  cheap.
- **Hyphenated names work** by span adjacency, the mechanism element syntax
  already uses for `aria-label`: `-` is in the operator charset
  (`-:!*/+=|&^?%`), so `flex-direction` is three span-adjacent tokens and
  `--color-ink` is five. Custom properties need nothing new.
- **`%`, `(`, `)`, `,`, `:`, `;`, `"…"`, `[`, `]`, `*`, `>`, `+`, `~`?** — all
  present except `~`. Percentages, `url("…")`, `calc(1rem + 2px)`,
  `[data-theme="dark"]`, `translateX(…)` all lex.

The two bytes that do **not** lex, and the honest consequences:

- **`#`** is in no charset, so `color: #333;` is a *lex error* before the
  parser exists. **This is refused rather than worked around, and it is the
  right refusal**: the vilan spelling is `color: {Color::hex("#333")};`,
  which routes the colour through the `Color` type that carries its own
  `:root` token line. A raw hex in a `css` block would be the one spelling
  that can silently produce a dangling `var()`-free literal outside the token
  system. The diagnostic quality problem this creates is real and is solved
  in §7.3 by a `LexError` rule code — the `UNESCAPED_BRACE` precedent.
- **`@`** is in no charset, so `@media`, `@supports`, `@font-face` cannot be
  written. The media query's spelling is `.md { … }`, which is the existing
  combinator; `@supports` and `@font-face` are non-goals (§10). Note that
  `declare`'s `check_selector` **already refuses at-rules by design** — *"a
  group at-rule holds rules, not declarations"* — so the lexer and the
  shipped std surface refuse the same thing for independent reasons, which is
  a good sign rather than a coincidence.
- Consequently `#id` selectors are unwritable. `[id="x"]` is the spelling.
  Named as a cost; nobody in the estate writes `#id` selectors.

### 4.2 The `css {` atom, and the ambiguity question

The item asks whether `<`-style ambiguity is a concern the way it was for
elements. **Yes, and more so** — and the difference is worth being precise
about, because element syntax got a gift here that this feature does not.

`<` could not begin an expression, so elements occupied *empty grammar
space*, and `element-syntax.md` could truthfully write "the `no_struct`
condition mode is untouched (an element is not a struct initializer)". `css {`
is brace-initial and therefore occupies the *same* shape as a struct
literal. Three findings settle it:

1. **`css` was not a keyword** (`KEYWORDS`, `lexing.rs:61`) when this was
   written. It was a struct *field* (`Length.css`, `Color.css`), a *method*
   (`Length::css(expression)`), and a struct-initializer field name
   (`Length { css = …, root = "" }`) in std, and a hard keyword breaks all
   three. **Q3 ruled otherwise and the keyword was TAKEN (2026-08-28):** the
   field is now `.text`, the method `Length::raw`, and every position that
   used to spell the word refuses with a message naming both renames. What
   follows is therefore the record of the alternative, not the shipped
   design; the shipped gate is the keyword itself plus a `{`.
2. **The recommendation is a contextual gate: `css` immediately followed by
   `{`, in atom position only.** Two tokens of lookahead. It never reaches
   field position (`value.css`), never reaches path position
   (`Length::css(…)`), never reaches struct-field position (`css = …`), and
   never touches the `emit("css", …)` channel tag, which is a string. The
   entire collision surface is *a struct literal for a type named exactly
   `css`, in expression position* — and vilan's types are Capitalized by
   convention, so std has none and the estate has none.
3. **The bodies are disjoint anyway, which makes the residual collision
   loud rather than silent.** vilan struct initializers use `field = value`
   (`Length { css = i"{value}px", root = "" }`); a css declaration uses
   `property: value;`. A mis-parse cannot quietly mean something else — it
   fails at the first `:`. That is the property the element syntax's dot rule
   was chosen for, arriving here for free.

**`no_struct` must be honored.** Unlike an element, a `css` block *is*
brace-initial, so `if css { … }` would mis-parse if the atom fired in
condition position. The block is suppressed in `no_struct` mode exactly as a
struct literal is; parenthesize to use one there. This is a deviation from
element syntax's story and the paper states it rather than inheriting the
sentence.

### 4.3 The grammar

```text
css-block    = "css" "{" { css-item } "}" ;         (* atom position; no_struct suppresses *)
css-item     = declaration | nested-rule ;
declaration  = property ":" value ";" ;
property     = { "-" } NAME { "-" NAME } ;          (* NAME = IDENT or any keyword; span-adjacent *)
nested-rule  = "." IDENT [ "(" [ expression { "," expression } [ "," ] ] ")" ] "{" { css-item } "}" ;
value        = value-piece { value-piece } ;        (* to the ";" at brace depth 0 *)
value-piece  = hole | TOKEN ;                       (* any token that is not ";" or "{" or "}" *)
hole         = "{" expression "}" ;
```

Notes, each earned:

- **The `;` is required after every declaration**, including the last. CSS
  makes it optional; vilan does not, because the formatter may never invent
  a token (the token-equality net, §8) and because a required terminator
  makes value-scanning decidable in one pass. A missing one is a parse error
  suggesting it — and `MISSING_TERMINATOR_MESSAGE` already has an **"Insert
  `;`" quickfix** in the server (`document.rs:2624`), which this reuses.
- **A value is a span**, sliced at desugar. The parser holds no source; this
  is the mechanism element syntax already uses for tag and attribute names
  (`node.rs:167`: *"A SPAN, not a slice … the desugar pass slices the text
  where the source is in scope"*).
- **A nested rule's head takes ordinary vilan expressions in its parens**, so
  `.attribute("data-open", "true") { … }` and `.pseudo("first-child") { … }`
  work with no special casing.
- **Holes are `{expr}`**, the same spelling as an element child. One hole
  spelling across the language.

---

## 5. What it lowers to — the crux

### 5.1 One target: the `style()` chain. No third channel.

**A `css` block compiles TO a `Style` chain.** It does not emit beside one,
and it does not introduce a third channel. Lowering is a pure `Node → Node`
desugar in the pre-analysis slot where `lift::rewrite_items` runs — the same
slot `elements::rewrite_items` occupies — so the analyzer, transformer and
interpreter never see a css node, and the codegen/interpreter equivalence
gate is not exposed at all.

Concretely, **the emitter does not change**. `Style::rule` stays the one
chokepoint; `class_hash`, `render_rule`, `without_covered`,
`family_longhands`, the `@media` sort band, the `*.sX` shorthand marker, the
`@layer vilan` rule from 032 — none of it is touched, extended, or
re-litigated. A program written entirely in `css` blocks emits a stylesheet
byte-identical to the same program written in chains, and that is a pin, not
a hope (§13).

### 5.2 Declarations lower to `raw` — and *that* is what makes it name-blind

The obvious design — `padding: 1rem;` → `.padding(…)` — is the one to
refuse, for the reason `element-syntax.md` §8 already recorded when it
rejected "undotted chain form resolved by name lookup": the desugar is
pre-analysis and name-blind, a method list in the grammar couples the parser
to std, and adding a method to `Style` would silently change what existing
code means.

The escape is a property of the shipped model that is easy to miss, and it
is the technical key to this whole paper. From `style.vl`:

> *"`raw` writes slots like any other method, so its properties are placed by
> this table too — `border_none()` IS `raw("border", "none")`."*

`Style::raw(property, value)` writes **the identical slot** the typed method
writes, participates in the identical family table, produces the identical
content hash, and obeys the identical last-wins merge. `.padding(space(4))`
and `.raw("padding", space(4))` are the same rule. Therefore:

> **Every declaration in a `css` block lowers to exactly one
> `.raw(property, value)` call.** One row in the lowering table. Name-blind.
> Total — there is no CSS property the block cannot express, because `raw`
> is `ui-styling.md` §2.3's escape hatch and the block inherits it whole.

The lowering table, complete:

| Written | Lowers to |
|---|---|
| `css { … }` | `style()` followed by the items in written order |
| `prop: <one hole>;` | `.raw("prop", <the hole's expression>)` |
| `prop: <anything else>;` | `.raw("prop", <the value's source slice as a str, holes interpolated>)` |
| `.name { … }` | `.name(style() … )` |
| `.name(a, b) { … }` | `.name(a, b, style() … )` |

The two value rows are one rule with two spellings of the argument: a value
that is *exactly one hole and nothing else* passes the expression through
untouched, so `gap: {space(4)};` keeps a `Length` and its `:root` token line;
anything else becomes a `str` (an i-string when it contains holes). Both
paths call the same method and the **type system** decides what the value
means — §5.3 of `element-syntax.md`'s principle, verbatim: *"What may fill a
child position or an attribute value is decided by the type system, not the
grammar."*

That is what §6 is for.

### 5.3 Nested rules lower to combinators, also name-blind

`.hover { … }` → `.hover(style() … )`. The rule is general: **a dotted head
lowers to a method call with the block's own chain appended as the final
argument.** Checked against every combinator that exists — `hover`, `focus`,
`active`, `disabled`, `dark`, `sm`/`md`/`lg`/`xl` all take
`(self, inner: Style)`; `attribute` takes `(self, name, value, inner)`;
`pseudo` takes `(self, name, inner)`. Inner-last is universal, and it is a
convention worth writing down in `style.vl` so it stays so.

### 5.4 Above `declare`, not instead of it

The item asks: does the block subsume `declare`, sit above it, or compile to
it? **It sits above it and should eventually compile to it — but not in v1.**

The two are not the same thing, and 032 already drew the line correctly:
*"`Style` is how you dress an ELEMENT … A declaration block is how you
declare something the element model cannot reach."* A `:root` token table has
no element and no class; it cannot be a `Style` and should not pretend to
be.

But `declare`'s *strings* are indefensible under the ruling (§0, §1.3), and
the fix is the same grammar with a selector head:

```vilan
const css [data-theme="iron-dark"] {
    --color-ink: {Color::hex("#fafafa")};
    --color-ground: {Color::hex("#161616")};
};
```
lowering to exactly the `declare(selector, declarations()…)` call that ships
today — same layer, same ordering invariant, same const-time refusals, now
with every token visible to the toolchain.

**It is deferred to a later slice for two reasons, both concrete.** First,
scope: it doubles the grammar and the headless form is where the users are.
Second, and decisively, **it needs a token a contextual gate cannot
provide**: `css [` collides with indexing a variable named `css`, and
`css :root` with a path. The headed form therefore requires promoting `css`
to a real keyword — which requires renaming `Length::css`, `Color::css` and
the `css` struct field on both value types. That is three std sites, one row
in `KEYWORDS`, one `Token` variant, one `KEYWORD_ROLES` row and a grammar
regeneration; **cheap in alpha, and impossible after beta.** It was Q3 in
§12 because the window, not the work, was what made it urgent.

> **DONE 2026-08-28** (Q3, "Take the keyword"). The promotion shipped ahead
> of S2, and the census found the paper's three sites and nothing else in
> std — plus one compile-gated doc fence, one corpus call site and the vilan
> snippets in the Rust tests. `Length::css(…)` is `Length::raw(…)`; the
> `.css` field of a `Length`/`Color` is `.text`; no golden moved, because
> both value types const-fold and the field name never reaches the emitted
> JavaScript. **The headed form's door is open**; the slice itself still
> sits after S5, per §11.

Until then `declare` keeps its current spelling, unchanged and undeprecated.

---

## 6. The std groundwork (S1) — typed values in `raw`

`element-syntax.md`'s first slice was **std groundwork that shipped before
any grammar and was valuable on its own**: text nodes, the `Slot` and
`AttrValue` traits, and `child`/`attr` widened over them. This paper's S1 is
the exact structural analogue, and it passes the same test.

Today `Style::raw` is `fun raw(self, property: str, value: str): Style`.
`Declarations::raw` is the same. So `style().raw("padding", space(4))` does
not compile, and the workaround — reaching for the `.css` field —
**silently drops the token's `:root` line and produces a dangling
`var(--space-4)`**. That is a live hazard in the shipped surface, unrelated
to this proposal: `with_length` and `with_color` carry `value.root` onto the
sheet and `raw` has no way to.

S1 closes it:

- A `CssValue` trait over `str`, `Length` and `Color` (the `Slot`/`AttrValue`
  precedent; naming is Q1 in §12).
- `Style::raw` and `Declarations::raw` widened over it, the `Length`/`Color`
  impls emitting `value.root` exactly as `with_length`/`with_color` do.
- Every existing call site type-checks unchanged (`str` satisfies the bound).
  §9.1 of `element-syntax.md` already probed what widening costs on the
  repo compiler: bounded generics are **fully monomorphized**, trait calls
  emit as direct calls, and the churn was *symbol renaming, nothing
  structural*. That probe was for `child`/`attr`; it should be re-run for
  `raw`, but there is no reason to expect a different answer.

This is why S1 is honest rather than ceremonial: it fixes a real dangling-token
bug, it makes `.raw("padding", space(4))` writable in chains today, and it is
what lets §5.2's one-row lowering table be name-blind and still typed.

---

## 7. The three features the ruling requires

### 7.1 Completion

**Where it lives.** Post-K9 the engine is `crates/vilan-ide`
(`Analysis::completion(offset)`, `completion.rs:609`), depending on
`vilan-core` only so it builds for wasm; the LSP's `Document::completion` is
a one-line delegation and the playground reaches the same code through
`crates/vilan-wasm`. Anything designed here lands in the editor **and** the
playground at once (`playground-completion.md` §3).

**How it knows it is in a block.** By E67's exact precedent, which is the
only "completion inside a nested sub-language" machinery that exists. The
desugar retires the node before analysis, so completion cannot learn from the
analyzed `Program` that the cursor is inside markup; instead
`Analysis::open_tag_end` (`completion.rs:739`) runs
`vilan_core::parsing::parse(live_text)` **afresh per request** and finds the
innermost element containing the offset — accepting both a parsed
`Node::Element` *and* a `Node::Error` spanning `<…>`, which is what recovery
leaves mid-keystroke — then `in_element_head` token-walks to confirm the
cursor is at the head's own bracket depth. A `css` block follows this
verbatim: raw re-parse, innermost `Node::Css`-or-`Node::Error`, token walk to
establish whether the cursor is in property position, value position, or
inside a hole. Cheap, independent of analysis succeeding, and already proven.

**What it offers, and — the part that matters — where the vocabulary comes
from.** E67 explicitly *refused* to invent an HTML attribute list, on the
ground that it "would be a second source of truth with nothing to gate it:
exactly the drift the item asked to avoid". That refusal is the first
objection this design has to clear, and it clears it on a real disanalogy:

> **The CSS property vocabulary is not invented. It already exists in the
> tree, and it is already gated.** `STYLE_PROPERTY_METHODS`
> (`formatter.rs:574`, ~65 rows) maps every `Style` property method to the
> slots it writes, and `crates/vilan-core/tests/style_table_sync.rs` holds it
> to the method bodies with six tests including
> `every_style_method_is_claimed_by_the_canonical_order_table` and
> `every_property_rows_slots_match_the_method_body`.

So property completion reads std's own typed surface through a table a test
already refuses to let drift — the opposite of the HTML case, and the
opposite of the Tailwind coupling `ui-styling.md` §8 rejected in its third
bullet. (The table lives in `formatter.rs` and `vilan-ide` depends on
`vilan-core`, so it needs `#[doc(hidden)] pub` exposure — the pattern the
corpus tripwire already uses for `sort_style_chains`.)

Four positions, four answers:

| Cursor | Offers | Source |
|---|---|---|
| property position (`disp\|`) | CSS property names | `STYLE_PROPERTY_METHODS` slots |
| property position, `--\|` | custom properties declared in this build | the block's own declarations in the live parse (v1: nothing; Q4) |
| dotted head (`.\|`) | condition combinators | `STYLE_CONDITION_METHODS` (14 rows, already gated) |
| inside a hole (`{\|}`) | ordinary expression completion | unchanged — a hole is an ordinary expression |

Value-position completion (offering `flex` after `display:`) is deliberately
**not** v1: it needs a property→enum map that does not exist and would be the
invented second source of truth E67 refused. It is Q4.

### 7.2 Code actions

The server has six actions today, and a shape worth knowing: **every quickfix
is diagnostic-message-driven** — `Document::quickfixes` (`document.rs:2368`)
iterates published diagnostics and pattern-matches their message text. There
is no refactor-kind action and no `executeCommand` infrastructure at all.
That splits this design's actions cleanly into the cheap and the new.

**Cheap — quickfixes, following the existing pattern exactly.** Every
refusal in §4.1 and §7.3 ships with its fix:

1. `#333` in value position → **"Wrap as `{Color::hex("#333")}`"**.
2. `@media (min-width: 768px) { … }` → **"Use `.md { … }`"**.
3. `!important` → **"Remove `!important`"**, with the note explaining that a
   `Style` never needs it (merge is a record update).
4. Unknown property `colr` → **"Change to `color`"**, built the way the
   field-rename fix already is: `closest_name_suggestion` strips
   ``did you mean `X`?`` off the diagnostic's own note, *so the fix cannot
   disagree with the diagnostic it fixes* (E58c).
5. Missing `;` → **"Insert `;`"**, the existing quickfix, unchanged.
6. Out-of-order nesting (`.dark { .md { … } }`) → **"Reorder to
   `.md { .dark { … } }`"**.

**New — one refactor, and its cost is real.** **"Convert to a `style()`
chain"** and its inverse **"Convert to a `css` block"** are mechanical
because the lowering is total and one-to-one (§5.2), and they are the
estate's migration path. They would be the **first `refactor.rewrite` action
in the server**: a new `CodeActionKind` in the capability declaration
(`main.rs:1659`), a non-diagnostic-driven code path in `code_action`
(`main.rs:2319`), and a row in `book_sync.rs:637`'s
`server_code_action_titles` gate, which scrapes titles out of `main.rs` to
hold the book's editor page in sync. Named as new machinery rather than
smuggled in as free.

### 7.3 Diagnostics

This is where the ruling bites hardest and where the design pays off most,
because it is the axis on which `declare` fails today (§1.3).

Anchors, by kind:

| Fires | Anchored at | When |
|---|---|---|
| unclosed block, missing `;`, `:` where a value was expected | the offending token | parse |
| unknown property name | **the property name's span** (warning, not error) | lowering/analyzer |
| `!important`, `@`-rule, bare `#hex` | the offending token run | lowering (lex, for `#`) |
| condition combinator in the wrong nesting order | the inner head's span, note at the outer | lowering |
| wrong-typed hole (`gap: {true};`) | the hole's expression | analyzer, as a `CssValue` trait-bound error with a secondary span at the bound |
| everything `check_declaration` refuses today | **the declaration's own span** | lowering |

The last row is the whole argument. Those checks exist and are correct;
today they fire as const-eval panics that underline the entire `const`
expression and point into `style.vl` (§1.3). **The block does not add
validation — it re-anchors validation that already exists onto tokens that
now have spans.** Nothing about `check_declaration`'s *rules* changes; only
where the squiggle lands.

Two honest limits:

- **Unknown properties are a warning, not an error.** `raw` admits any
  property by design (`ui-styling.md` §2.3 — the tail must not block), so
  refusing `-webkit-mask-composite` would break the escape hatch the block
  inherits. It rides the existing warning channel, which has exactly three
  producers today (`must_use`, element syntax's `text(…)`-attribute
  warning, deprecation) and no lint framework — so this is a fourth producer,
  not a new subsystem.
- **The `#` case is a *lex* error and cannot be anything else**, because the
  lexer is context-free and finishes before the parser exists. The mitigation
  is precedented: `LexError` carries a `rule` code (`UNESCAPED_BRACE` is the
  existing one), so a rule for `#` can say *"`#` is not a vilan token; in a
  `css` block write a colour as `{Color::hex(\"#333\")}`"* and carry
  quickfix 1. Good enough, and stated rather than hidden.

**The design gate that follows from element syntax's own S5 pain.** When
element syntax reached its LSP slice, *"the desugar's scaffolding spans were
the real fix"* — the wide generated spans had painted `<div` as a function
and attribute names as methods, and a generated `.child` link shared its
hole's exact span and tie-broke nondeterministically. That was repair work in
S5 for a decision made in S2. So:

> **The css desugar's generated accessors take zero-width anchors from the
> first commit, and the AST carries the property-name span, the value span,
> and the per-declaration span whether or not S2 uses them.** The ruling
> makes completion and actions requirements; the way a design honors that in
> its *first* slice is by cutting the spans they will need.

---

## 8. The formatter

**A correction the paper has to make first.** Markup does *not* print
verbatim from a source slice. That was the S2 stopgap
(`formatter.rs`, commit `41028f68`: *"An element expression prints from
source, verbatim — the same mechanism as i-strings"*) and S3 removed it four
hours later (`6c3e2eb1`): today `Printer::print_element` (`formatter.rs:3104`)
is a full structural printer that re-indents markup, splits it by budget,
normalizes `<div/>` to `<div />`, and re-attaches interior comments. The only
surviving source slices in the element path are lexical atoms — tag and
attribute names, which span several tokens.

Three consequences for this design.

**1. A printer arm is mandatory in the same slice as the grammar.** There
are exactly three `_ => self.bailed = true` fallbacks (`formatter.rs:2307`,
`3533`, `4138`), the bail set is asserted **empty**
(`parse_differential.rs::current_bail_set`), and a bail returns the file
unformatted while `--check` calls it clean. A grammar slice without a printer
arm would silently stop formatting every file containing a block. The
element-syntax arc's answer applies: **S2 ships a verbatim source-slice
passthrough** (which satisfies the token net trivially and keeps the bail set
empty), **S3 ships the canonical printer.**

**2. The token-equality net dictates what may be normalized.** `format`
re-lexes its own output and compares token streams, so any distinction to be
*preserved* must be recorded in the AST (the `ElementBody.self_closing` and
`ElementChild::{Hole,Bare}` precedents) and any distinction to be *erased*
must lex identically. The css consequences: whether a value was written
`{space(4)}` or `{ space(4) }` is whitespace and may be normalized; whether
a declaration ended in `;` may not be normalized *away*, which is the second
reason §4.3 requires it always.

**3. The chain-order sorter — and the answer is not what it first looks
like.** kolt.local 006's sorter has two gates that must agree: the token
gate `starts_style_builder` (`formatter.rs:772`) demands the literal
three-token run `style` `(` `)` not preceded by `.` or `::`, and the AST gate
`Printer::is_style_builder` (`2894`) demands a bare argument-less call on the
accessor `style`. **Neither fires on a `css` block**, because the formatter
reparses source and never sees the desugar, and there is no `style ( )` token
run in the source.

So the block is *exempt by construction* — and that is a problem, not a
relief, because it creates two ways to write a style with different
canonicalization. Two facts decide the answer:

- Sorting a `css` block **is** semantics-preserving, for exactly the reason
  sorting a chain is: declarations lower to `.raw`, `raw` writes slots
  through the same family table, and 006 shipped the proof
  (`an_order_sensitive_fixture_resolves_the_same_slots`, in
  `crates/vilan-cli/tests/style_chain_order.rs` — note the CLI path; the
  archive note and `formatter.rs:513` both cite a `vilan-core` path that does
  not exist).
- Sorting a **headed** block (§5.4) would **not** be, because it lowers to
  `declarations()`, where order is what the block declares. 032 already found
  this hazard and closed it — but note *how*: `declarations()` is spared
  **only because its root identifier differs**. There is no positive "this is
  a declarations chain, skip it" check. The pin is
  `a_declarations_chain_is_never_reordered_by_the_style_chain_sort`
  (`style_chain_order.rs:586`), whose design is the anti-vacuity fix: it
  builds the *same* link text under two roots and asserts opposite outcomes.

**Recommendation: the headless block gets canonical declaration order in S3,
sharing one order function with the chain sorter; the headed form never
does.** That the two forms differ in whether the formatter may reorder them
is a further argument for making them visibly different syntax, which §5.4
already does. The rank tables are keyed by *method* name and a block writes
*CSS property* names, so S3 derives the property rank from the same rows
(each carries its slot family) under the same `style_table_sync.rs` gate — a
derivation, not a fourth hand-maintained table. And, as the printer already
does for chains, **any block containing a comment is refused outright**
rather than reordered.

---

## 9. Does it subsume 009, 014, 015?

### 009 (child/descendant combinators) — it gives them a home, not an answer

The block gives 009 a spelling the moment 009 has a semantics: `& > * + * { … }`,
or in this grammar's dotted style `.children { … }` / `.divide { … }`
lowering to whatever combinator 009 mints. Selectors do get a home.

But **009's actual problem is untouched by syntax.** 014's correction states
it exactly: a descendant rule `.sX > *` has specificity (0,1,0), which
**ties** with a child's own base rule and resolves by class-hash lexical
order — the action-at-a-distance `ui-styling.md` §1 declares structurally
impossible. A prettier spelling does not break the tie.

One contribution, offered as material for 009 rather than as a ruling here:
**032's layer trick generalizes to exactly this.** 032 replaced a byte-order
convention with a cascade invariant — *"unlayered styles beat layered ones
whatever their specificity, so a `Style` always wins against a declaration
block"*. Emit combinator rules inside `@layer vilan` and the same sentence
becomes *"a child's own `Style` always wins against a rule reaching in from an
ancestor"*: deterministic, checkable, stated, and preserving §1's promise in
the only form it can survive — the element's own style is the last word. It
costs what 032's version costs, symmetrically: a combinator rule cannot
override an unlayered declaration either.

**Verdict: 016 does not subsume 009. It removes 009's syntax question and
leaves its cascade question, and the block must not ship the spelling before
009 rules the semantics.**

### 014 (the theme axis) — it sharpens the fork and strengthens (b)

014's correction is emphatic that 009 and 014 do not collapse: 014 needs an
**ancestor** guard (`[attr] .sX`, 0,2,0, beats the base rule cleanly), 009
wants a **descendant** combinator (`.sX > *`, 0,1,0, ties). The paper takes
that as given, and observes that the block *makes the distinction
typographic rather than argumentative*: in CSS nesting the two differ purely
by which side of the combinator `&` sits on, so a design that admitted both
would spell them `[data-theme="x"] & { … }` and `& > * { … }` — visibly
different, impossible to conflate, which is what 014 asked for.

Beyond that the block does **not** resurrect fork (a). 014's recommendation
is (b) — exit the theme axis to `Color::var` plus a declaration block — and
**this paper strengthens (b)**, because (b)'s weakest point was that
`declare`'s recipe is written in strings, and §5.4's headed form is precisely
the fix. If the owner takes (b), the sequence is: 032 (shipped) → 016's
headed form → deprecate `Style::dark` toward a spelling that finally has
completion and diagnostics. If the owner later wants (a) on its own merits,
the block's grammar already has the space and needs no change.

**Verdict: 016 does not subsume 014, and does not need to. It makes 014(b)
materially better and leaves 014(a) available.**

### 015 (style variants) — orthogonal, and honestly so

015 is about abstraction *within* the construct-in-const rule: kolt's
`button_style`/`icon_button_style` duplicate because each branch re-`const`s a
variant of a base. A `css` block is still a const expression producing a
`Style`; `+` still combines, `match` still selects, const functions still
const-evaluate per call site. **Nothing in 015 gets easier or harder.** The
one small thing it buys is legibility of the base+delta exhibit — two blocks
read more clearly as base and delta than two chains do — which is not an
answer to 015 and should not be counted as one.

**Verdict: 016 does not address 015. 015 needs its own design note starting
from the `button_style` exhibit, exactly as its item says.**

---

## 10. Non-goals

Each recorded so declining it is a decision, not an omission.

- **At-rules of any kind** — `@media`, `@supports`, `@font-face`,
  `@keyframes`. `@` does not lex; `.md`/`.lg` are the media spelling;
  `@font-face` is left to its own item exactly as 032 left it.
- **`!important`** — refused with a fix, permanently. Merge is a record
  update; a `Style` that needed `!important` would be a `Style` that had lost
  the property the whole model is for.
- **Bare `#hex` values** — `{Color::hex("…")}` is the spelling (§4.1).
- **Bare selectors inside a headless block** — every nested rule is a dotted
  combinator. Arbitrary selectors are `declare`'s job (§5.4).
- **Combinators** (`>`, `+`, `~`, `&`) — blocked on 009, grammar space
  reserved (§9).
- ~~**`css` as a hard keyword in v1**~~ — **overtaken by Q3's ruling: the
  keyword was taken 2026-08-28**, which is what opens the headed form's door.
  The contextual gate was never built.
- **Value-position completion** and **a CSS value grammar** — no typed value
  parsing inside the block; values are token runs and holes. Typed values
  arrive through holes, which is where the type system already lives.
- **Composing styles inside a block** (`css { .add(base); … }`) — `+` outside
  the block is the combinator, unchanged from `ui-styling.md` §1. Grammar
  space is free if this is ever wanted.
- **Retiring or deprecating `declare`, or the `style()` chain** — neither
  moves. The two forms mix freely.

---

## 11. Slices

The element-syntax shape, with an honest first slice. Suite-gated, docs in
the same commit, per-case pins.

- **S1 — std groundwork: typed values in `raw`. SHIPPED** (before this lane;
  `CssValue` is in `vilan/std/src/style.vl` and `Style::raw` /
  `Declarations::raw` are generic over it). The `CssValue` trait over
  `str`/`Length`/`Color`; `Style::raw` and `Declarations::raw` widened over
  it, with the `Length`/`Color` impls carrying `value.root` onto the sheet.
  Re-run the §9.1 monomorphization probe on the repo compiler before
  committing. **No grammar.** *Standalone value:* it fixes a live
  dangling-`var()` hazard (reaching for `.css` to get a token into `raw`
  drops its `:root` line) and makes `.raw("padding", space(4))` writable in
  chains today. Docs: `guide/styling.md`'s escape-hatch section, CHANGELOG.
- **S2 — grammar and desugar, together. SHIPPED 2026-08-28** (branch
  `css-block-s2`, two commits: the keyword promotion, then the block).
  `Node::Css` (`CssBody`, `CssItem::{Declaration, Nested}`, `CssValuePiece`)
  carrying the property-name, value and per-declaration spans **and
  zero-width scaffolding anchors from the first commit** (§7.3, asserted
  directly in `css.rs`'s own tests); the atom arm driven by the real
  keyword; the body parser; `crates/vilan-core/src/css.rs` in the pre-lift
  slot at **six** src sites and one test harness (macro-generated blocks
  covered and pinned, as elements had to be); the verbatim source-slice
  printer passthrough; the `#`/`@`/`!important` refusals; corpus program
  `vilan/test/css-block.vl` with `.mjs` and `.css` goldens. The gate holds
  in both halves: **byte-identical emitted CSS and byte-identical emitted
  JS** against the same program written as a chain, plus the tree-level
  form of the same claim (the desugar builds the very nodes a written chain
  parses to, span-stripped `Debug` equality per lowering-table row).
  Deviations and findings, recorded:
  - **The atom arm is in `parse_chain_head`, not `parse_atom`.** An atom does
    not know `no_struct`, and §4.2's suppression rule is exactly what has to
    be honored — so the block sits beside the struct initializer, under the
    same gate. The refusal in condition position names the fix
    (parenthesize), rather than reading as the keyword-rename refusal.
  - **The block's body COMMITS.** The draft's decline-and-recover shape put
    every broken item through the delimiter recovery, whose last-resort
    message claims a region is unclosed when it plainly closed, and threw
    away the missing-`;` the author needs. Each item now reports for itself
    and the body skips to the next `;`, E49's recorded lesson from the
    element head. The reason it cannot ride the farthest-failure channel is
    worth knowing: a block in statement position is parsed TWICE — once by
    `parse_assignment`'s speculative place probe — and the speculative pass
    leaves the enclosing statement's own terminator note farther along than
    anything inside the block.
  - **Value pieces PARTITION the value's span**, rather than starting at each
    run's first token: slicing from the token would drop the space a hole is
    separated by, and `calc({w} + 2px)` would render `calc(w+ 2px)` where the
    i-string it lowers to keeps the space. The two are now byte-identical,
    pinned.
  - **The css pass runs BEFORE the element pass**, and descends into markup
    itself, so a block written in an element's head or a child hole
    (`<div .styled(const css { … })>`) is a chain before the element desugar
    reaches it.
  - **A block needs `style` in scope.** The desugar generates `style()`, so a
    block without `import std::style::style` fails on the generated accessor
    — which is why that one accessor keeps a REAL span (the `css` keyword's),
    while every other generated accessor is zero-width: the diagnostic
    underlines the word that asked for a `Style`.
  - **A `Length` or `Color` hole in a MIXED value renders as its runtime
    tuple**, not as its CSS text — `padding: calc({space(4)} + 2px);` puts
    `var(--space-4),:root{…}` on the sheet. This is not a block defect: the
    i-string twin `i"calc({space(4)} + 2px)"` does the same thing today, so
    the equivalence gate holds and the underlying gap is that `str + Length`
    type-checks at all. Filed as a finding, not fixed here.
- **S3 — formatter.** The canonical printer replaces S2's passthrough:
  one declaration per line, nested rules at +1, the block's own budget
  behavior; canonical declaration order derived from
  `STYLE_PROPERTY_METHODS` under the `style_table_sync.rs` gate and sharing
  one order function with the chain sorter; comment attachment via item
  spans, and outright refusal to reorder any block containing a comment.
  `assert_construct` pins per form (token identity, no-silent-bail, canonical
  form, idempotence, round-trip).
- **S4 — docs and editors.** *(S2 shipped the `guide/styling.md` section its
  own surface needed — "The `css` block", compile-gated, and the anchor the
  keyword hover deep-links to; the spec pages, the tour phrasebook and the
  TextMate `#css` rule remain S4's.)* `spec/grammar.md` (the `css-block` productions,
  the atom-position and `no_struct` prose), `spec/lexical.md` (the two bytes
  that do not lex and why), `guide/styling.md` (both forms side by side,
  compile-gated), `tour/coming-from-javascript.md` (a CSS phrasebook), and
  the TextMate grammar's `#css` repository rule
  (`editors/vscode/syntaxes/vilan.tmLanguage.json`; hand-written, regex-level,
  as `#elements` is — there is no tree-sitter grammar in the repo).
- **S5 — LSP and playground tails.** Semantic tokens for property names and
  condition heads, from a second raw parse (the `keyword_hover`/markup-tokens
  pattern, `document.rs:1862`); completion in the four positions of §7.1,
  landing in the editor and the playground at once through `vilan-ide`; the
  six quickfixes; the convert-between-spellings refactor with its
  `book_sync.rs` row. **The gate on the whole arc: S5 requires no S2 rework.**
  If it does, S2 got the spans wrong — which is exactly what happened to
  element syntax and is the one mistake this plan is shaped to avoid.

The headed form (§5.4) is **not** in this arc. It is a sixth slice gated on
Q3, and on the `css` keyword promotion being taken before beta.

---

## 12. Open questions for the owner

> **RULED 2026-08-28 (the owner): all six.** Q2 — the formatter sorts the
> headless block canonically, sharing the chain sorter's order. Q3 —
> **"Take the keyword"**: `css` is promoted to a hard keyword now
> (renaming `Length::css`, `Color::css` and the `css` struct field — the
> three std sites — plus the grammar regeneration; family breaking), which
> opens the headed form's door; the headed slice itself stays sequenced
> after S5 per §11. Q4 — property and combinator names in v1; value
> completion only behind a gate that does not exist yet. Q5 — unknown
> property is a WARNING, and the lint-framework question files separately.
> Q6 — as recommended: the method spelling, on the element syntax's
> precedent; no CSS-flavored media form. S2 is UNBLOCKED and builds ON the
> keyword rather than the contextual gate.

**Q1. The trait name.** `CssValue`? `DeclValue`? `StyleValue`? It sits beside
`Slot` and `AttrValue`, which are short and unqualified. *Recommendation:*
`CssValue`.

**Q2. Does the headless block get canonical declaration order in `vilan fmt`
(§8), or is authoring order preserved?** Sorting is provably
semantics-preserving here and consistency with the chain sorter argues for
it; against it, CSS authors group declarations meaningfully and a block is
more prose-like than a chain. *Recommendation:* sort — one canonical output
is the formatter's stated design, and a block that formats differently from
the chain it desugars to is a wart.

**Q3. Promote `css` to a real keyword before beta?** The contextual gate
serves v1 at zero cost, but the headed form (§5.4) needs a hard keyword, and
promoting one requires renaming `Length::css`, `Color::css` and the `css`
struct field. That is three std sites and a grammar regeneration — cheap in
alpha, impossible after the v0.40.0 beta contract. **This is the only
question with a deadline attached.** *Recommendation:* decide the headed
form's fate this cycle; if it is wanted at all, take the keyword now.

**Q4. How far does completion go inside a block?** Property names from
`STYLE_PROPERTY_METHODS` are free and gated. Value completion
(`display: fl|` → `flex`) needs a property→value map that does not exist, and
building one is the invented second source of truth E67 refused for HTML
attributes. *Recommendation:* property and combinator names in v1; value
completion only if a gate for it can be written first.

**Q5. Unknown property — warning, error, or silent?** §7.3 recommends
warning, so `raw`'s escape hatch survives. But the warning channel has three
producers and no lint framework, no per-rule severity, and no allow/deny; a
fourth producer with a "did you mean" note may be the point at which one is
wanted. *Recommendation:* warning now, and file the lint-framework question
separately rather than growing one here.

**Q6. Should `.md`/`.dark` keep their method spellings inside a block, or
should the block admit a CSS-flavored spelling for the media case?** The
method spelling is name-blind and future-proof (§3); a CSS-flavored one would
read better to a web developer and would be the block's first coupling to
std's method list. *Recommendation:* method spelling, on the element
syntax's precedent — the dot keeps the rule decidable on one token forever.

---

## 13. Test plan (per case, as always)

- **Parser** — fixtures per form: every declaration shape; hyphenated and
  custom properties; keyword property names; dimension values (`1px`,
  `1.5rem`, `50%`); `calc(…)`, `url("…")`, comma lists; one-hole values;
  mixed text-and-hole values; nested rules with and without arguments;
  nesting three deep; `css` as a variable, a field, a method and a struct
  field name still parsing (the contextual gate); `if css { … }` under
  `no_struct`. Errors: missing `;`, unclosed block, `#` in a value, `@` at
  item position, `!important`, a bare selector, a value containing a stray
  `{`. Recovery fixtures in `parser_recovery.rs`.
- **Lowering** — span-inclusive snapshots per row of §5.2's table; written
  order preserved; the one-hole vs mixed-value split; nested heads with
  arguments; zero-width scaffolding anchors asserted directly.
- **Equivalence — the arc's headline gate** — the corpus program written
  twice, as a block and as the chain it desugars to, with **byte-identical
  emitted CSS and byte-identical emitted JS on both twins**. A program with
  no `css` block emits a byte-identical sheet (the 032 property, restated).
- **Inference** — each `CssValue` impl dispatching in a hole; a hole of an
  unimplemented type failing with the trait named and a secondary span at the
  bound; a `Length`/`Color` hole emitting its `:root` line exactly once.
- **Const-time fences re-anchored** — for each `check_declaration` refusal, a
  pin that the diagnostic now lands on the declaration's own span rather than
  the `const` expression. These are the pins that prove §1.3.
- **Formatter** — `assert_construct` per form; idempotence; a file mixing
  chains and blocks; a block with a comment refusing to reorder; the bail set
  still asserted empty; the declaration-order pin built anti-vacuously the
  way `a_declarations_chain_is_never_reordered_by_the_style_chain_sort` was.
- **LSP** — semantic tokens for property names and condition heads including
  the non-overlap invariant; completion in each of §7.1's four positions,
  including mid-keystroke over a `Node::Error`; one pin per quickfix; the
  `book_sync.rs` title gate.
- **Docs gate** — every example in this paper's final book page compiles.

---

## 14. Alternatives rejected

- **A macro DSL** (`macro css!(…)`) — the ruling's own words, and §1.1's
  mechanism: macro arguments keep spans, not a tree, so hover, go-to-def,
  typed diagnostics, semantic tokens and fine error spans are all
  unavailable by construction. It is also mechanically blocked: macro
  arguments must parse as vilan expressions before the macro sees them, and
  `display: flex;` does not.
- **A string-argument surface** (`style().css("display:flex")`) — this is
  `declare`'s shape, and §1.3 measures what it costs: every token opaque, and
  diagnostics anchored on the whole `const` expression with the only precise
  location inside `style.vl`.
- **Lowering declarations to typed property methods** (`padding:` →
  `.padding(…)`) — rejected on `element-syntax.md` §8's recorded ground: the
  desugar is pre-analysis and name-blind, a method list in the grammar
  couples the parser to std, and adding a method to `Style` would silently
  change what existing code means. `raw` writes the same slot (§5.2), so
  nothing is lost.
- **A third emission channel** for block-shaped CSS — rejected as the single
  most expensive possible answer. The atomic model's guarantees are
  properties of one chokepoint (`Style::rule`); a second producer would have
  to re-derive slot keys, family coverage, hashing, the sort bands and the
  layer rule, and would put two things in the sheet that could disagree.
- **One block form discriminated by its content** (top-level declarations →
  `Style`, top-level selectors → `declare`) — rejected on 032's own recorded
  ground: it makes the surface's meaning depend on the first byte of its
  argument, which is exactly why `check_selector` refuses at-rules. The
  headed/headless split (§5.4) is a *grammar* fact, decided before the first
  `{`.
- **Changing the lexer to admit `#` and `@`** — rejected. Lexing is
  context-free by spec and by architecture, and `#` cannot be admitted
  globally without taking a byte from the language's future. The costs are
  bounded, each has a spelling and a quickfix (§7.2), and `{Color::hex(…)}`
  is the better spelling on its own merits.
- **Verbatim CSS** (a true subset, no holes) — rejected: it would forfeit
  §8's surviving requirement that the form compose with functions, impls and
  `match` natively. Holes are what make `gap: {space(4)};` a token reference
  rather than a copied literal.
