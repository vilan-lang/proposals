# `Style`'s condition model — conditions as values (A95)

**Status.** PAPER, Order 34 (lane `paper-style-34`, drafted 2026-09-13 against
vilan `e4d192e3`). A95 was RULED to the paper at the Order 34 GO (R2): the
redesign is not built this order, and the two fences beside it are —
B311's (a `:` in a `pseudo` name refused when the call is WRAPPED) and A93's
(`child_relation`'s token checked against the two shipped relations). Both
landed in this lane. What follows is the design the Order 35 slices build,
the three places the owner's sketch cannot be spelled in this language and
what is recommended instead, and the census that says what a migration costs.

The paper it extends: `ui-styling.md` §0bis.2 (the condition grammar),
§0bis.4 (the family marker), §0bis.6 (the relation axis, the band ledger);
`css-block.md` §5 (the lowering), §7.1 (completion), §15 (compact styling);
`style-variants.md` (A36's `when`).

---

## 0. What is wrong today, in one paragraph

A condition is a COMBINATOR WRAPPING an inner style — `hover(inner)`,
`attribute(name, value, inner)` — one condition per axis slot, nested
outside-in in a fixed order (`media` → relation → attribute → pseudo).
Four things follow, and all four are the same fact wearing different clothes:

1. **Two pseudo-classes on one rule are unspellable.** `hover(not(active(s)))`
   means `:not(:hover):active`, not `:hover:not(:active)` — A89's `not` negates
   the condition OUTSIDE it, which is the only reading a marker can have. The
   author reaches for the free-form `pseudo` name, writes the compound as a
   string, and that string carries the slot key's own `:` — **B311's
   miscompile**, measured this lane on the item's own exhibit:
   `attribute("data-open", Some("true"), pseudo("hover:not(:active)", s))`
   emitted `.s2jb016[data-open="true"]:hover{opacity:0.5}`, the `:not(:active)`
   gone and nothing saying so.
2. **`not` had to be a MARKER** (A89) — a pending `!` on the inner's condition
   that the enclosing combinator consumes — because which selector is negated
   is a fact about the condition outside it. The marker costs three refusals
   of its own (unwrapped at application, double negation, under a media
   condition) and one cascade-band ruling.
3. **The nesting order is memorised or met as a refusal.**
   `md(within(attribute(hover(..))))` is the only legal spelling of that set,
   and six of std's condition refusals exist to say so.
4. **Every wrap mints an intermediate style whose rules land dead on the
   sheet** — B308, measured: kolt 11 dead rules / 562 B of 9,144 B of class
   rules, the corpus `style.css` 27.6%, a four-level nest emitting five rule
   sets of which four are dead.

None of these is a bug in a combinator. They are the shape: a condition that
is a WRAPPER can only ever hold one of each axis, in one order, and a
condition that is a STRING can carry the machinery's own delimiters.

---

## 1. (a) The model — a condition is a value

A `Style` is base declarations plus a set of RULES; a rule is a CONDITION SET
plus declarations. The condition set is the new thing; everything else already
ships.

**Condition values.** Four kinds, matching the four axes `render_rule` already
consumes:

| Kind | Constructors | Renders |
|---|---|---|
| `Pseudo` | `hover()`, `focus()`, `active()`, `disabled()`, `first()`, `last()`, `pseudo(name)` | `:hover` … |
| `Element` (new, §2.4) | `element(name)` | `::selection`, `::before` |
| `Attribute` | `attribute(name)` (presence), `attribute(name).eq(v)` | `[name]`, `[name="v"]` |
| `Relation` | `within(condition)` — e.g. `within(attribute("data-theme").eq("dark"))`, `within(attribute("open"))`; `children()`, `divide()` | `[name] .sX`, `.sX > *`, `.sX > :not(:first-child)` |
| `Media` | `sm()`, `md()`, `lg()`, `xl()`, `media(min_width)` | `@media (min-width: …)` |

`.not()` is a method on every kind but `Media` (§5.2), returning the same kind
negated. A89's `Option<str>` argument folds into the constructor pair:
`attribute(name)` IS the presence form, `attribute(name).eq(v)` the exact one,
so the `Option` that every call site has had to spell since A89 disappears from
the surface.

**A condition SET** is one or more conditions intersected. `Condition + Condition`
is the set constructor — `+` already means "merge these two" everywhere else in
this system (`Style + Style`), and a set is a value you can name:

```vilan
let interactive = hover() + active().not() + attribute("disabled").not();
```

**Attaching a set.** One method, `Style::on(conditions, inner)`:

```vilan
style()
    .padding(space(4))
    .on(hover() + active().not(), style().color(Color::blue(600)))
    .on(md() + within(attribute("data-theme").eq("dark")), style().background(ink))
```

`inner`'s base declarations become a rule under `conditions`; `inner`'s own
rules carry `conditions` too, **intersected** — which is this paper's answer to
the item's open question *"does `.on` on a style that already has rules apply
to the rules too?"*: yes, and that is what makes nesting mean anything.

**Nesting.** `a.on(X, b.on(Y, s))` gives `s` the set `X ∪ Y`. There is no
order to get wrong — `hover() + md()` and `md() + hover()` are the same set and
canonicalise to the same key (§2), so the six nesting-order refusals go.

**Merging.** `+` on `Style` is unchanged: per-slot, per-family, right wins.
A95 changes what a slot's condition field can hold, not how slots merge.

### 1.1 The one place the owner's sketch cannot be spelled — and it is load-bearing

The item and the brief both write the block head as
`.on(hover(), active().not()) { … }` and the chain as
`style().color(c).on(hover(), active().not(), attribute("disabled").not())` —
conditions as a variadic argument list. **Neither is expressible against the
shipped language, and the reason is not a missing feature but two shipped
rules meeting.**

- **A spread parameter is rejected on an `impl` member.** Probed at `e4d192e3`
  with the installed compiler: `fun take(self, ...items: (i32, i32))` is
  refused with *"a spread parameter is only available on a free `fun`: it is
  part of the signature, and a method is reached by dispatch … Declare a tuple
  parameter (`items: T`) and call it `m((a, b))`"* (`grammar.md` §139 states
  the same rule). So `Style::on` cannot take a variadic at all.
- **A spread parameter must be LAST**, and the `css` block's dotted-head
  lowering appends the block's own chain as the **final argument**
  (`css-block.md` §5.3, shipped and pinned). So even on a free function the two
  requirements are contradictory: `.on(a, b) { … }` would have to lower to
  `.on(a, b, style()…)`, with the variadic in the middle.
- **Vilan has no overloading**, so `on` cannot be arity-1 in a chain and
  arity-2 in a block head.

**Recommendation: `on` takes ONE condition argument and the inner style,
`fun on<C: IntoConditions>(self, conditions: C, inner: Style): Style`,** with
`IntoConditions` implemented by `Condition` and by `ConditionSet` so both
`.on(hover(), s)` and `.on(hover() + active().not(), s)` are one method. This
is exactly the generic-bounded parameter `Style::raw<V: CssValue>` already is,
it keeps the **inner-last convention** §5.3 asked to be written down, and it
needs no grammar change, no language change and no new lowering rule. The cost
is the one reading the sketch wanted and does not survive:
`style().color(c).on(hover())` — declarations first, condition after. The block
gives it back (§4), which is what the block is for.

Two alternatives were priced and are recorded as rejected in §11: a
`List<Condition>` argument (`.on([hover(), active().not()], s)` — parses today,
probed, but spends brackets on the common one-condition case and has no
natural `let`-bound spelling), and lifting the spread fence for `impl` members
(a language change riding a std redesign, and still blocked by "spread must be
last").

---

## 2. (b) Canonicalisation

The slot key stays THREE fields, `media:condition:property`, and the condition
field stays a space-joined token list in axis order. That is the whole of the
compatibility argument and it is worth stating before the rules:

> **Every rule expressible today canonicalises to the condition string it has
> today, so every already-emitted class name is byte-identical.** §0bis.2's
> argument (class names are content hashes of `key|declaration`, and
> cross-program determinism is shipped) transfers verbatim — A95 is a surface
> change, not a sheet change. New rules (two pseudos; a guard and a child
> relation together) mint new keys, which is what new rules do.

### 2.1 The order

The set sorts into the shipped slot order and nothing else moves:

1. **media** — field 0 of the key, at most one (§2.3).
2. **relation** — the ancestor guard `^[name="v"]` first, then the child
   relation `>*` / `>*+*` (§2.5 admits both in one set).
3. **attributes** — `[name]`, `[name="v"]`, any number.
4. **pseudo-classes** — any number.
5. **pseudo-element** — at most one, always last (§2.4).

Within a repeatable slot the tokens sort **lexically by the rendered token**,
not by written order. The reason is the same one §0bis.2 gave for not widening
the key: two authors writing `hover() + focus()` and `focus() + hover()` mean
one rule and must get one class, or the content hash stops being a function of
the meaning. Compound-selector order is semantically free in CSS
(`.sX:hover:focus` ≡ `.sX:focus:hover`, identical specificity), so a canonical
order costs nothing and buys determinism.

**A fixed TABLE of pseudo-classes was considered and is rejected.** `pseudo(name)`
admits arbitrary names, so a curated order can never be total, and a table
would need its own `style_table_sync` gate for a property the lexical rule
gives for free and can never leave stale. Recorded, with the counter-argument
that a table could put `:hover` before `:focus` for readability: the emitted
line is not read by people, and `vilan fmt` orders the SOURCE (§2.6).

A negated token sorts by its BARE token, with the negated form immediately
after the plain one. That is a readability choice with a second use: it makes
the contradiction check (§2.2) a scan of adjacent pairs rather than a quadratic
comparison.

### 2.2 Duplicates and the one refusal

- **Equal conditions merge.** `hover() + hover()` is `hover()`. Set semantics.
- **A condition and its negation REFUSE** at const time, curated, one ledger
  row: `hover() + hover().not()` is a rule that can never match, and a rule
  that can never match is always a mistake rather than an intent.
- **Two different values of one attribute are NOT refused.**
  `attribute("x").eq("a") + attribute("x").eq("b")` renders `.sX[x="a"][x="b"]`,
  which matches nothing — the same defect the refusal above catches, one step
  further out. It is left admitted in v1 and recorded here rather than fudged:
  catching it needs the canonicaliser to reason about attribute VALUE equality,
  which is a different and larger claim than "this exact token and its
  negation", and the narrow rule is the one A95 ruled. **Open question (i).**

### 2.3 One media per set

Two breakpoints in one set is `@media (min-width: 640px) and (min-width: 768px)`,
which is the narrower one written twice. Refuse, one message naming the
narrower — it is the same class of refusal as the contradiction and it keeps
field 0 of the key single-valued, which `assemble_assets`' numeric `@media`
sort band depends on (B35).

### 2.4 The pseudo-ELEMENT, and why the set needs it

kolt writes `pseudo(":selection", ..)` today (`views.vl:77`) — a leading colon
smuggled through the free-form name so that `render_rule`'s `":" + token`
produces `::selection`. Under A95 `pseudo(name)` refuses a `:` outright (that
is the whole point), so the pseudo-element needs a value of its own:
`element("selection")` → `::selection`.

It is a separate KIND rather than another `Pseudo`, for two reasons that are
facts about CSS and not preferences: a pseudo-element must come last in a
compound selector and nothing may follow it, and at most one may appear. Both
are canonicaliser rules, both are checkable, and both are unstatable if
`::selection` is just another pseudo token. `element(..).not()` is refused
(`:not(::selection)` is not valid CSS).

### 2.5 A guard AND a child relation in one set

Today `within(.., children(..))` is refused — "no relation wraps a relation",
which is the one-per-slot rule doing the only thing a nesting model can do.
Under a set the two are not the same slot: a `within` guard is a PREFIX
(`[data-theme="dark"] .sX`) and a child relation is a SUFFIX (`.sX > *`), and
`[data-theme="dark"] .sX > *` is an ordinary, useful selector that the relation
axis has never been able to spell.

**Recommendation: admit it, and LAYER it.** §0bis.6's layer split is asymmetric
on purpose — `within` unlayered because its rules dress the element itself,
`children`/`divide` layered because their rules reach IN — and a rule doing
both reaches in. So the rule that decides is *"a rule carrying a child relation
emits inside `@layer vilan`, whatever else conditions it"*, which is the
existing rule stated over a set instead of over a nest. `within`'s unlayered
standing is untouched for every rule that dresses the element.

Two guards, or two child relations, in one set: refuse (`within(a) + within(b)` — where `a`/`b` are conditions
means an ancestor carrying both, which is `[a][b] .sX` — arguably meaningful,
definitely not ruled; `children() + divide()` is a contradiction). **Open
question (ii).**

### 2.6 What the formatter becomes

`STYLE_CONDITION_METHODS`/`ConditionAxis` (`formatter.rs:914`) sorts condition
LINKS in a chain by axis today. Under A95 there is one condition link per rule
(`on`), so the table's job moves inward: it becomes the canonical order over
the condition VALUES inside an `on` head, and `vilan fmt` rewrites
`.on(md() + hover() + attribute("x"), ..)` to
`.on(md() + attribute("x") + hover(), ..)` — the same sort, one level down.
The `not` row (recorded on the pseudo axis because "a marker's axis is whatever
its enclosing combinator turns out to be") loses its apology: `.not()` is a
method on the value it negates and sorts with it.

The kept sugar (`hover(inner)`, `md(inner)`, §6) keeps the table's present job
for as long as it exists, so the table is extended rather than replaced.

---

## 3. (c) The band survives — shown, not asserted

`ui-styling.md` §0bis.6's ledger rests on one mechanism: `assemble_assets` has
no comparator, it sorts lines lexically with a numeric override for `@media`
min-widths, and the cascade BAND is the first byte of the rendered line
(`*` < `.` < `:` < `@layer` < `[` < media). The band is therefore decided by
the OUTERMOST kind present, and §0bis.6 states the ledger tie by tie.

**`render_rule` is not touched by A95.** The canonicaliser produces the same
condition string shape `render_rule` consumes today, in the same axis order, so
the first byte is computed the same way from the same axes:

| Set contains | First byte | Band, per §0bis.6 |
|---|---|---|
| nothing, or attributes and/or pseudos only | `.` (or `*.` for a shorthand) | base |
| an un-negated `within` guard | `[` | after `:`, before media |
| a NEGATED `within` guard | `:` | the pseudo band (A89's one recorded band move) |
| a child relation | `@` (`@layer vilan{`) | the layer band |
| any media | the `@media` numeric group | last |

Every row is today's row. The two shapes A95 newly admits do not add a row:

- **Two pseudo-classes** (`.sX:hover:not(:active)`) — first byte `.`, base
  band, specificity (0,3,0) by `:not(x)` counting as `x`, which is A89's
  already-pinned arithmetic. It beats each of its (0,2,0) parts on specificity,
  never on the sort — the §0bis.2 rule verbatim.
- **A guard plus a child relation** (`@layer vilan{[data-theme="dark"] .sX > *}`)
  — first byte `@`, the layer band, by §2.5's rule. It does not move the
  unlayered `within` rules that exist today, because it is a rule those
  programs do not have.

The §0bis.4 family marker survives for the same reason it survived the relation
axis: a condition prefix is byte-identical across a family pair, so `*` (0x2A)
vs `.` (0x2E) still decides inside whatever band the pair lands in.

**The one thing to pin at the build**, because it is exactly the class of bug
B35 was: the corpus `.css` golden must move by ADDITION only. Every program
written against today's surface, recompiled against the canonicaliser, must
produce a byte-identical stylesheet. That is stateable as a test and is
recommended as slice 1's acceptance gate (§9).

---

## 4. (d) The block spelling

`css-block.md` §5.3's name-blind rule is *"a dotted head lowers to a method
call with the block's own chain appended as the final argument"*, and §5.2's
rule is that the head is an ordinary expression list the lowering passes
through. Both were probed at `e4d192e3` against the installed compiler and both
hold for what A95 needs:

- a head carrying a composed expression:
  `.attribute("data-" + "open", Some("true")) { color: blue; }` compiles and
  emits `[data-open="true"]` (probe `p2.vl`);
- a head carrying a list literal and an index: `.pseudo(["hover", "focus"][0]) { … }`
  compiles and emits `:hover` (probe `p5.vl`).

So the spelling is:

```vilan
const css {
    padding: {space(4)};

    .on(hover() + active().not()) {
        color: {Color::blue(600)};
    }

    .hover { text-decoration: underline; }

    .add { color: inherit; }
}
```

- **`.on(<condition or set>) { … }`** lowers, name-blind, to
  `.on(<set>, style()…)` — the arity-2 method of §1.1, with no new lowering
  rule and no grammar change.
- **`.hover { … }`** stays exactly as it is: the one-condition sugar is an
  arity-2 method (`hover(self, inner)`), which is what the block head already
  wants (§6).
- **`.add { … }` with no head** is a plain nested merge — `add(self, other)`,
  arity 2 in the block, which flattens into the parent. Recommended kept as the
  owner asked, and `vilan fmt` can offer the flatten as a fix (E167's
  neighbourhood).
- **No bare selectors.** `css-block.md` §10's refusal stands, and E153's
  `:hover {` steer (*"the answer is a DOT"*) gets one more reason to exist:
  under A95 the dotted head is where conditions become values.

The free condition constructors (`hover()`, `attribute(..)`, `within(..)`, `md()`)
belong in `std::style::prelude`, which is ambient **inside a block and nowhere
else** (A70) — so `.on(hover() + active().not()) { … }` needs no import, and
outside a block it is `style::hover()` or an ordinary import. **Probed: a free
function named `hover` and a `Style::hover` method coexist** (probe `p3.vl` —
`hover()` resolves to the free function, `style().hover(..)` to the method),
so adding the constructors does not shadow the sugar.

---

## 5. (e) What A95 closes — and the one thing it does not

### 5.1 B311 — closes, completely

`pseudo(name)` refuses a `:` outright once two pseudo-classes are spellable as
two values; `attribute`/`within` names and values are already fenced. No
condition is then a string that carries the key's own delimiter, so the
mis-aligned split cannot happen. **The interim fence built this order is what
keeps that honest**: it refuses only the WRAPPED case, so kolt's nine unwrapped
raw tokens keep compiling until A95 rewrites them.

### 5.2 A89's marker — closes

`not(inner)` as a marker exists only because a wrapper cannot say which
selector it negates. A value can: `hover().not()` is the negation applied
where it belongs. All three of A89's refusals go with it — an unwrapped `not`
is not constructible, `not(not(..))` becomes `x.not().not()` (refuse, same
reasoning: a double negation is a spelling mistake), and the media case stays
as a refusal on `Media::not()` (`@media not (..)` is its own grammar and no
ruling has reached it). The negated-guard band move (`:not([..]) .sX` opening
with `:`) is a `render_rule` fact and is unchanged.

### 5.3 A93 — closes

`children()` and `divide()` become relation VALUES and `child_relation` is
deleted with its token. The fence built this order is the bridge: it holds the
token to the two shipped relations from now until the method goes away.

### 5.4 B308 — REDUCED and CHEAPENED, not closed. The item's claim is too strong.

> **Superseded by §12 (owner, 2026-09-13):** B308 CLOSES through G23's end-of-evaluation hook
> — emission moves to a scheduled finaliser that emits the live set once. The analysis below
> stands as the record of why a chain-time redesign alone could not close it.

A95's item says B308 "dies structurally (a rule set is a value, emitted once at
application)". **That is not what the mechanism supports, and the paper says so
rather than letting a slice discover it.**

`Style::raw` emits at construction (`rule` → `emit("css", ..)`), `emit` is
const-only, and every APPLICATION path (`styled`, `bind_styled`, the element
class path) is runtime code through `class_list` — which is exactly what lane
styles-33 recorded when it found B308 "NOT IMPLEMENTABLE as ruled". Under A95
the inner style handed to `.on(conds, inner)` has already emitted its own
unconditioned rules by the time `on` re-mints them under the composed
condition. The dead rule is still dead.

What A95 does change is the COUNT and the COST:

- **Count.** Today a nest emits one dead rule set per level:
  `md(within(attribute(hover(x))))` is four dead sets for one applied class
  (measured, B308). Under A95 that is ONE `.on(md() + within(..) + attribute(..) + hover(), x)`
  — one intermediate, one dead set. On the measured shapes that is the
  difference between B308's "a 4-level nest emits 5 rule sets, 4 dead" and
  "2 rule sets, 1 dead".
- **Cost of the real fix.** B308's priced design (2) — retraction at
  consumption, `__retract_asset`, ~20 interpreter lines plus a const-only
  extern — needed `retract_inner` at **five** call sites (`hover`, `attribute`,
  `within`, `pseudo`, `child_relation`). Under A95 there is exactly **one**
  re-minting site, `on`. The design shrinks to one call site.

**Recommendation:** B308 stays open, `A95 reduces it`, and design (2) is
scheduled as a slice OF the A95 build (§9 slice 4) rather than as a separate
item — which is where the owner's ruling "A95 closes it structurally" was
pointing even if the mechanism is not quite structural.

There is one design that WOULD close it outright and it is recorded in §11:
route a conditioned body through `Declarations` (which never emits; `declare`
puts it on the sheet) instead of through `Style`. It is rejected because
`Declarations` has no family table, no `+`, and no class, and because it would
break the `hover(inner: Style)` sugar and all 318 call sites in §7.

---

## 6. (f) What stays

- **`hover(inner)` and every named combinator, as SUGAR for `on`.**
  `fun hover(self, inner: Style) { self.on(hover_condition(), inner) }` — one
  line each. **Recommendation: KEEP**, and the census is the argument: 318
  combinator call sites across std, kolt, the docs, the corpus and the test
  suites (§7), of which **278 are single-condition sugar shapes** that need
  no change at all if the sugar stays. Keeping it turns a mechanical rewrite of
  every styled program into an opt-in improvement of the ~25 sites that
  actually want two conditions. Deleting it buys uniformity and costs a
  tree-wide edit for nothing the reader gains.
  The naming collision this creates is real and is handled: the free
  constructor `hover()` and the method `Style::hover(inner)` coexist (probed,
  §4), but they are two spellings of one idea, and the reference page must say
  which is which in one sentence.
- **`when(condition, delta)` (A36)** — RUNTIME conditions, unchanged and
  untouched. A95 is const-time composition; `when` selects between two styles
  that already exist. `style-variants.md` §15.4's ruling (compute when the
  state changes the RULE SET, custom properties when it changes a VALUE, data
  attributes only for a contract outside the style system) is unaffected.
- **`Declarations` / `rule` / `declare`** — same values, same channel.
  `declare`'s selector string is `css-block.md` §5.4's headed-form slice, not
  this one.
- **`raw`**, and `css-block.md` §6's typed-value groundwork.
- **The class-list emission and the split gate.**
- **`attribute`'s and `within`'s const-time name/value fences** — one token, no
  quotes, spaces or `:`. They become the constructor's fences.

**Deleted:** `child_relation` (A93), `Style::not` as a marker (A89), the
`Option<str>` value argument on `attribute`/`within` (folded into `.eq`), and
`pseudo`'s freedom to carry a `:` (B311).

---

## 7. (g) The migration census

Counted over `e4d192e3` (this lane, `census2.py`): every `.<combinator>(` or
`.<combinator> {` occurrence whose enclosing 320 characters carry a style
context (`style()`, `style::`, `Style`, `css {`, `s()`, `declarations()`),
hand-corrected for the four style sites the context window missed and for the
prose and non-style mentions (`View::children`, `List::first`) it caught. `when` is excluded — it stays (§6).

| Surface | Sites | Files |
|---|---|---|
| std (`vilan/std`) | 20 | 1 (`style.vl` itself) |
| kolt (`~/code/kolt/src`) | 39 | 4 |
| docs (fenced code) | 47 | 4 |
| docs (prose mentions of a combinator) | 21 | 7 |
| corpus (`vilan/test`) | 47 | 3 |
| `examples/` + templates + benchmarks | 1 | 1 |
| cli tests | 5 | 2 |
| core tests | 159 | 4 |
| **Total (code sites)** | **318** | **19** |

Per method, across all surfaces:

| Method | Sites | Under A95 |
|---|---|---|
| `hover` | 71 | sugar — no change |
| `attribute` | 50 | sugar, but the `Option` argument goes: `attribute("x", Some("v"), s)` → `attribute(attribute("x").eq("v"), s)` or the sugar keeps its `Option` |
| `within` | 47 | same as `attribute` |
| `md` | 27 | sugar — no change |
| `not` | 27 | **REWRITTEN**: the marker becomes `.not()` on the condition it negates |
| `divide` | 24 | sugar — no change (17 of them kolt's) |
| `children` | 22 | sugar — no change |
| `pseudo` | 18 | **REWRITTEN where the name carries a `:` or a leading `:`** — 10 sites, all kolt's |
| `focus` | 6 | sugar |
| `lg` / `sm` / `media` | 14 | sugar |
| `active` / `disabled` / `first` / `last` | 9 | sugar |
| `child_relation` | 3 | **DELETED** — 2 are std's own `children`/`divide` bodies, 1 is kolt's, already commented out |

**The shape of the migration, stated plainly.** With the sugar kept (§6), the
sites that MUST change are:

- **27 `not` sites** — the marker's whole estate. Mechanical in the common
  shape (`X(not(Y(s)))` → `X(cond_Y().not(), s)`) and needing a human where the
  negation's target is only clear from the nesting.
- **10 kolt `pseudo` sites** carrying a `:` — B311's estate, and the reason
  B311's fence is on the WRAP rather than on the name: kolt keeps compiling
  until A95 rewrites them.
- **3 `child_relation` sites**, two of which are std's own.
- **~97 `attribute`/`within` sites** IF the `Option` is dropped from the sugar
  too; zero if the sugar keeps its present signature and only the new `on`
  surface uses `.eq`. **Recommendation: keep the sugar's `Option`** for one
  release, deprecate, then drop — the `[deprecated("use …")]` attribute exists
  and is exactly this.

**What E167's converter can rewrite mechanically.** E167 (the `css` block
converter, built this order in lane `editor-34`) turns a `style()` chain into a
block. Its machinery is precisely what an A95 codemod needs and it is worth
saying which half transfers:

- **Transfers.** The seed (any path whose last segment is `style` called with
  no arguments), the chain walk, and the split rule (the first unconvertible
  link ends the block and the rest becomes a postfix chain). A combinator link
  is a *convertible* link for E167 today, so the walk already knows how to take
  `hover(inner)` apart into a head and a body.
- **Does not transfer.** The `not` rewrite. `not` is the one combinator whose
  meaning depends on its ENCLOSING link, so a converter that reads one link at
  a time cannot place the negation; it needs the parent. That is a two-link
  window, not a rewrite of the walk, and it is the one place the codemod has to
  be written rather than derived.
- **Neither.** The 10 kolt `pseudo` sites carrying a compound: the string has
  to be PARSED into conditions (`"hover:not(:active):not([disabled])"` is three
  conditions), which is a small CSS-compound parser. Worth writing — it is ~30
  lines and it converts the exact estate that has no other path — but it is
  codemod work, not converter work.

---

## 8. (h) The re-measure plan

Three measurements exist and each has a prediction A95 must be held to. All
CPU-time or callgrind-Ir, never wall (Order 34 mechanics).

1. **`css-block.md` §15.3 — compact styling, measured on the SHEET.** The
   three kolt styles that section counted no longer exist (N85:
   `button_style_base` gone, `default_panel_style` moved to
   `src/app_overlay.vl:6`, `views.vl:332` meaningless), so the per-site
   character counts are an Order 30 record and not a re-run. Measure what
   survives a refactor instead: kolt's emitted class-rule bytes, **11,020 B
   at `9b22ec36`** after B308's close took them from 11,986 (§13).
   *Prediction:* S2 does not move the sheet for a style with one condition per
   rule, and SHRINKS it for kolt's button, whose four raw `pseudo` compounds
   become one `.on(hover() + active().not() + attribute("disabled").not())`
   head — one class where there were four. Report the byte delta and the
   corpus `.css` goldens' own, and say which styles contributed it.
2. **A84's class-list cost.** `when` chain 26.8 µs per rendered button, a const
   style 6.7 µs, a const style with the class list hoisted to a `const` str
   0.05 µs. *Prediction: unchanged.* A95 does not touch `class_list` or the
   slot walk. Re-run as a regression, not as a claim.
3. **B308's dead share.** kolt 11 dead rules / 562 B of 9,144 B (10.7% of
   class-rule bytes); corpus `style.css` 27.6%. *Prediction:* the corpus share
   falls sharply (its 4-level nests become 1-level), kolt's falls less (its
   nests are shallow). Measure with B308's own method — a sheet class absent
   from the bundle — before and after slice 2, and use the delta to size
   slice 4 (the retraction).

And the gate that is not a measurement: **the corpus `.css` golden must move by
ADDITION only** (§3).

---

## 9. (i) Slices for Order 35, and sizing

**S1 — the condition values, behind the existing surface. M.**
`Pseudo`/`Element`/`Attribute`/`Relation`/`Media` structs, `.not()`, `.eq()`,
`Condition + Condition`, `IntoConditions`, the canonicaliser (§2) and its
refusals (contradiction, two media, two guards, pseudo-element placement).
`Style::on(conditions, inner)` built on it. **Every existing combinator
re-expressed as sugar over `on`** in the same change, so the acceptance gate is
byte-identity: the corpus, std, the examples, the docs and kolt all emit
identical stylesheets. No new surface is documented yet. This is the slice
whose whole value is that nothing changes.

**S2 — the new surface. M.** `on` in the reference and the guide, the free
constructors in `std::style::prelude`, the `css` block head
(`.on(<set>) { … }` — no lowering change, §4), `pseudo`'s `:` refusal,
`element(name)`, `child_relation` deleted, the guard+child-relation set
admitted and layered. Ledger rows for the new refusals. **BREAKING** for the
27 `not` sites and the 10 kolt `pseudo` sites; the codemod (§7) lands here.

**S3 — the tooling. M.** `STYLE_CONDITION_METHODS` becomes the canonical order
over condition VALUES (§2.6); `vilan fmt` sorts an `on` head; `css-block.md`
§7.1's completion tables gain the constructors after `.on(` and after `+`;
`style_table_sync` extended to hold the value constructors to the canonicaliser
the way it holds the property methods to the slot table.

**S4 — B308's retraction, at its one remaining site. M.**
B308's priced design (2), now with one `retract_inner` call instead of five
(§5.4). Measured before and after by the dead-share method.

**S5 — the estate. S–M.** The `attribute`/`within` `Option` deprecation
(§7), the guide and reference rewrites, kolt's migration at the owner's word.

**Sizing overall: L**, four M slices and one S–M, and S1 is the one that can be
landed and shipped alone because it changes nothing a user can see.

---

## 10. Open questions

Each carries a recommendation, which is what a lane builds if no ruling comes.

- **(i) Two different values of one attribute in a set** (§2.2) —
  `attribute("x").eq("a") + attribute("x").eq("b")` matches nothing.
  *Rec: admit in v1, record.* Refusing it means the canonicaliser reasons about
  value equality, which is a larger claim than the ruled one.
- **(ii) Two ancestor guards in a set** (§2.5) — `within(a) + within(b)` (two conditions)
  renders `[a][b] .sX`, one ancestor carrying both, which is meaningful and
  unruled. *Rec: refuse in v1* (one guard per set), with the message naming the
  attribute-on-the-element form; widen later if a real program asks.
- **(iii) `on`'s argument shape** (§1.1) — the generic `IntoConditions` vs a
  `List<Condition>`. *Rec: the generic bound*, `Style::raw<V: CssValue>`'s own
  shape.
- **(iv) Does the sugar keep its `Option<str>`?** (§7) *Rec: yes for one
  release, then `[deprecated]`, then drop* — it is 97 call sites and there is a
  language feature for exactly this.
- **(v) Is `+` the right spelling for intersection?** It means "merge" for
  `Style` and "and" for a condition set; `.and()` is the alternative.
  *Rec: `+`.* One operator, one reading ("both of these at once"), and it is
  what makes `let interactive = hover() + active().not();` read as a value.
- **(vi) B308's standing** (§5.4) — the item's "closes structurally" is too
  strong. *Rec: B308 stays open and becomes slice 4 of the A95 build.*
- **(vii) `element(name)` vs keeping the leading-colon hatch** (§2.4).
  *Rec: the value.* kolt's one site is the whole estate, and a hatch that
  survives the redesign is the hatch the redesign exists to remove.

---

## 11. The owner's sketch — where this paper diverges, and why

1. **`.pseudo(pseudo("hover"))` → `.on(hover())`.** Recorded in the item and
   agreed: the axis is named once. §1.
2. **`.set(property, Length)`** — a typed `raw`, `css-block.md` §6's S1
   groundwork. Taken as-is; it is orthogonal to the condition model and is not
   slice-scheduled here.
3. **`.on(hover(), active().not())` as a variadic** — **cannot be spelled**
   (§1.1: spread is refused on an `impl` member, must be last, and the block
   lowering appends the inner). The paper recommends one condition-set
   argument. This is the divergence that matters and it is the reason the paper
   was asked for.
4. **`style().color(c).on(hover())`** — the postfix reading, unspellable for
   the same reason (no overloading). The block gives it back (§4).
5. **"B308 dies structurally"** — reduced and cheapened, not closed (§5.4). **RULED (§12): closed
   through G23's build-step hook.**

### Recorded rejections

- **A `List<Condition>` argument** (`.on([hover(), active().not()], s)`).
  Parses today (probed, `p5.vl`), and loses on the common case: one condition
  is the overwhelming majority of 318 sites and would pay two brackets for a
  set it does not have.
- **Lifting the spread fence for `impl` members.** A language change riding a
  std redesign, and it does not even solve the problem — a spread must be the
  last parameter and the block lowering appends the inner after it.
- **A curated pseudo-class ORDER table** (§2.1). Cannot be total over
  `pseudo(name)`, and needs a gate to buy what lexical order gives free.
- **A fourth key field for the condition set.** §0bis.2's argument, still
  decisive: it rehashes every class name in every build for nothing a user sees.
- **Routing a conditioned body through `Declarations` to close B308** (§5.4).
  It works — `Declarations` never emits — and it costs the family table, `+`,
  the class, and every one of the 318 call sites.
- **A `not` free function kept beside `.not()`.** Two spellings of one idea,
  and the method is the one that carries A95's whole argument (the negation is
  applied where it belongs).

---

## 12. Rulings (owner, 2026-09-13)

The owner's five numbered replies answer §11's five divergences (the owner's own correction:
"I wrote my responses for the paragraph 11 section, not the open questions"); §10's seven
recommendations are accepted as written ("the recs look good"), with the note that the ruling
on divergence 5 dissolves some of them too. Recorded:

**§11 — the divergences.**
1. `.pseudo(pseudo("hover"))` → `.on(hover())` — **accepted.**
2. `.set(property, Length)` as the typed `raw` — **accepted.**
3. The variadic `.on` cannot be spelled — **understood.**
4. The postfix reading unspellable, the block gives it back — **understood**; "`.on(CONDITION,
   STYLE)` is fine with me": the two-argument form is the ruled surface.
5. "B308 dies structurally" was too strong — **RULED, and further than §5.4 went:** a proper
   BUILD-STEP HOOK for styling fixes the whole class for good. Const evaluations push their rules
   to a global; a hook the build runs at the end reads it, processes it (drop what no applied
   class references) and emits the CSS in one go — which dissolves "X is already emitted before
   Y is known" instead of retracting it. To make it automatic, const evaluation gains a way to
   SCHEDULE a function to be called at the end of evaluation; multiple scheduling requests call
   it once. Filed as **G23**; B308 is re-pointed at it and CLOSES through it — `Style::rule`
   stops emitting at construction and appends to the registry, the scheduled finaliser emits
   the live set once. The retraction design is withdrawn; G23 is the FIRST slice of A95's build,
   because every later slice's emission behaviour is simpler once emission is late.

**§10 — the open questions: every recommendation accepted** — (i) admit, (ii) refuse in v1,
(iii) the generic bound, (iv) `Option<str>` for one release then `[deprecated]`, (v) `+`,
(vii) `element(name)`. **(vi) is superseded** by divergence 5's ruling: B308 does not stay open
as slice 4 — it closes on G23, which becomes slice 1. What else the hook dissolves: §5.4's
"reduced and cheapened, not closed" (now closed); the recorded rejection "routing a conditioned
body through `Declarations` to close B308" (no longer a candidate for anything); and §8's
re-measure gains a second number — the stylesheet after the finaliser drops the dead sets is the
compact-styling reading css-block §15.3 wanted.

**`within` takes a CONDITION, not an attribute name** (owner, on §1's table and example):
`within("data-theme").eq("dark")` would lock the ancestor guard to attributes. The spelling is
`within(attribute("data-theme").eq("dark"))` — or, through the sugar,
`within(attribute("data-theme", Some("dark")))` — so a guard can carry any condition value
(`within(hover())` for a hovered ancestor, `within(attribute("open"))` for presence). §1's
table, §1's example and §2.5/§10(ii) are corrected above; the canonical order of a guard's own
conditions is the set's order, unchanged.

---

## 13. As built — Order 35 (2026-09-13, lane style-35)

**G23, B308 on it, and S1 landed; S2 (the new surface — BREAKING for 37 sites), S3 (tooling) and
S5 (the estate) are Order 36's.**

- **G23.** `asset::schedule_at_end(finaliser)` — a scheduled function is recorded by its EMITTED
  name (an anonymous closure is refused: its scope dies with the run that made it) and runs once
  after the LAST const expression of a compile's const pass, per leg; under `run --watch` that is
  the end of the ROUND (recompiled legs re-schedule and re-emit, untouched legs keep their sidecar
  through the artifact record); a finaliser may schedule another; a panic fails the build naming
  the function. **One correction to §12 (vi) and G23's item:** "the const evaluations push to a
  GLOBAL" is not achievable with the hook alone — every const site has its own interpreter scopes,
  so no vilan global spans two `const` expressions; the registry is HOST-held and exposed as two
  new channel verbs, `asset::stage(kind, token, line)` and `asset::staged(kind)`.
- **B308 closed.** `Style::rule` stages under its class token and schedules `flush_stylesheet`;
  a token is LIVE when a const result names it (a string, one of its words — `class_list` joins —
  or a substring), which is sound and over-approximate in the safe direction. Dead share,
  controlled: kolt's sheet 12.1 % → 0 (11,986 → 11,020 B), the corpus's `style.css` 31.4 % → 0,
  `css-block.css` 29.1 % → 0, `theme.css` 24.1 % → 0; the three goldens moved by subtraction only.
  The retraction design (§5.4) is withdrawn, as ruled.
- **S1.** `Condition`, `IntoConditions`, `+`, `.not()`, `.eq()`, the free constructors, the
  canonicaliser with its five refusals, `Style::on<C: IntoConditions>(conditions, inner)`, every
  combinator re-expressed as a fence pass plus one `on`; `render_rule` walks the canonical tokens
  once, which is what makes two pseudo-classes on one rule and a guard beside a child relation
  reachable. **Gate: 145 built artifacts byte-identical** (131 corpus bundles + 5 sheets, two
  styling examples × 3, kolt × 3), run three times. Sixteen new rows; `"on"` joined
  `STYLE_BARRIER_METHODS`.
- **Two forced divergences from §1/§9:** (1) the five condition KINDS are ONE type — `trait
  Add<B = Self>` returns `Self`, so `Pseudo + Attribute` cannot exist; `Condition` carries its kind
  in the token, and `.eq()` on a non-attribute or `.not()` on a breakpoint are const-time refusals
  (§1.1's own precedent); `IntoConditions` has one implementor, kept as S2's seam. (2)
  `within(condition)` REFUSES a non-attribute condition in S1: the guard's selector travels inside
  the slot key `media:condition:property`, where a pseudo-class's `:` mis-aligns the split (B311's
  grammar) — `within(hover())` is refused naming the working form, and widening it needs a KEY
  change (S2 or later). §12's `within(hover())` example is not yet spellable.
- **Still to decide before S2:** whether the sugar's six nesting refusals go with the codemod (S1
  kept them verbatim — deleting them would make refused programs compile with no spelling to steer
  to); `Condition::eq` vs a future `PartialEq::eq` (rename to `.value(..)` then, or never derive).
  §8's re-measure exhibits no longer exist in kolt (N85); the number that moved is the sheet.

## 14. As built — Order 36 (2026-09-14, lane style-36)

**S2 (breaking), S3 and S5 landed; A95's arc is complete.** Six commits on `style-36`: `f70f7941` (B311/B322), `7abec3ee` (the surface), `806dbfdf` (the tooling), `e6dd697b` (the estate), `66cf15b8` and `1e8416b8` (two finds).

- **S2.** `pseudo(name)` refuses a `:` at the NAME, steering to the two values the string stood in for; `slot_of` is the one total reader of a slot key and every former `key.split(":")` reads its `Slot` record's fields. The `not` MARKER is retired for `Condition::not` (`Style::not` and its three refusals gone), `child_relation` is DELETED, `element(name)` and the guard+child-relation set are documented, and the free constructors join `std::style::prelude` so the block head `.on(<set>) { … }` needs no import and no lowering change. **R1** kept the six nesting refusals with `.on(<set>)` steers; **R2** kept `.eq()` and wrote "never derive `PartialEq` on `Condition`" at the type.
- **R3, and one correction to it.** The ruling's purpose — `within(hover())` and `within(attribute("open"))` — lands, and the slot's identity IS a record (`Slot`, read through `slot_of`); what does NOT happen is storing the triple beside each slot, which was built and measured at **+26,201 B (+9.4 %)** on kolt's client bundle for facts no runtime reader asks about. What actually unblocks the guard is that it carries its inner TOKEN (`^hover`) rather than its rendered selector (`^:hover`), which holds no `:` at all; the joined key stays, which is also what keeps every already-minted class name byte-identical. Cost: 438 bytes of code, once.
- **B311 and B322 close together**, and B322 needed no surviving fence: `Style::add`'s split is the reader's now, and `media`'s width and `raw`'s property pay the property fence the declaration writer always paid.
- **S3.** `STYLE_CONDITION_METHODS` is read twice — combinator links and condition VALUES — with `ConditionAxis` gaining the model's own split (`Guard`/`Child`/`Element`); `vilan fmt` sorts an `on` head (`sort_on_heads` is the net's matching token pass); css-block §7.1 gains the condition-value row; `style_table_sync` gate 6 holds each row's axis to the byte its constructor builds, in both directions.
- **S5.** `Style::attribute`/`Style::within`'s `Option<str>` is `[deprecated]` for one release with the `.eq()` steer, and the estate moved ahead of it: the corpus builds with the warning at 0.
- **GATE: 145 built artifacts, every stylesheet byte-identical** against `9b22ec36` — the 130 guard-free programs and the 4 guard-writing ones alike. Five corpus `.mjs` goldens move by emitted std code and the new `const` bindings; kolt's bundle +54 B, the two examples' −384 B each. Eight ledger rows `NEW`, six retired, one re-keyed.
- **Three corrections to the paper.** (1) §1's `let interactive = hover() + active().not();` needs `const` — a `const` expression reads only compile-time-known bindings. (2) §2.5's "two guards refuse" is now four refusals, one per non-element axis. (3) S1's guard was a latent MISCOMPILE, not merely a limitation: `within(attribute("x").not())` emitted `![x] .sX{…}`, invalid CSS, in silence.

**kolt (read-only re-census):** one S2-breaking site, `src/styles.vl:138` `.pseudo(":placeholder")` → `.on(style::element("placeholder"))`. Nothing else.

