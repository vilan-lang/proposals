# Style variants — the base+delta recipe

Status: **DESIGN NOTE, 2026-08-31 — RECOMMENDATION AWAITING OWNER RULING**
(kolt.local 015). Every claim about what compiles today is probe-verified
against `vilan 0.39.0 (2ad39dd09)`, the installed dev build from `next`; §7
lists the probes and what each one refused. The note recommends **no new std
surface** and **no compiler change** — it recommends a spelling, and §8 asks
the owner whether that spelling wants documenting or one small method.

`css-block.md` §9 ruled this note's scope: *"016 does not address 015. 015
needs its own design note starting from the `button_style` exhibit, exactly as
its item says."* This is that note.

## 0. The exhibit

kolt's `src/views.vl` carries two near-duplicate functions (lines 21–67 at
kolt `ab451d4`, "migrate to vilan v0.39.0" — 47 lines):

```vilan
fun button_style(disabled: bool, selected: bool) {
    let base = const style()
        .display(Display::Flex)
        .gap(Length::rem(4f / 16f))
        .align_items(AlignItems::Center)
        .radius(Length::rem(4f / 16f))
        .script_label()
        .padding_x(Length::rem(8f / 16f))
        .padding_y(Length::rem(4f / 16f))
        .width(Length::raw("fit-content"))
        .user_select(UserSelect::Off);

    if selected {
        ret const base.color(Theme::primary_a()).background(Theme::primary_a().alpha(0.15));
    }

    if disabled {
        ret base;
    }

    const base
        .cursor(Cursor::Pointer)
        .hover(style().background(Theme::primary_a().alpha(0.1)))
        .active(style().background(Theme::primary_a().alpha(0.15)))
}

fun icon_button_style(disabled: bool, selected: bool) { /* a different base, the same 13-line tail */ }
```

The two bodies differ **only in the base chain**. The 13 lines after it — the
`selected` branch, the `disabled` branch, and the pressable tail — are restated
verbatim per surface. That is the duplication 015 filed.

The constraint that produces it is deliberate and stays: `ui-styling.md` §3's
construct-in-const rule, enforced by call-graph reachability into
`std::asset::emit`. Everything below lives **inside** that rule; nothing here
proposes an exception to it, and §6 shows the rule's enforcement surface gets
*smaller* under the recommendation, not larger.

## 1. What actually forces the duplication

Not the const rule as such. Exactly one mechanic:

> **A function parameter is a runtime value, so a `const` expression cannot
> read one.** (`const-eval.md` §1: "A parameter or runtime local errors at the
> reference".)

So the obvious factoring — *pass the base in, extend it under `const`* — is
refused at the reference, not at the emission (P1):

```
Error: `base` is a runtime value; a `const` expression reads only compile-time-known bindings
 6 │     const base.cursor(Cursor::Pointer)
   │           ──┬─
```

That is a property of `const`, not of styling, and it is not going to change:
the whole judgement `const` makes is *"every free variable here is known at
compile time"*.

But the conclusion people draw from it — *"therefore the delta cannot be
factored out"* — is **false**, and this is the note's first finding. Two exits
already exist and both are shipped:

1. **Drop the inner `const` and let the caller supply it.** A function that
   builds style is const-only by reachability; it may take a `Style` parameter
   freely, because inside a `const` expression the parameter is bound during
   const evaluation. `fun pressable(base: Style): Style { base.cursor(..)… }`
   compiles, and `const pressable(button_base)` folds (P6). Written as an
   `impl Style` extension it is exactly the shape `theme.vl` already uses for
   `script_label` and `paint_ink2` (P2).
2. **Don't extend at all — merge.** `Style + Style` is runtime-legal and
   resolves per property *and per family* (`without_covered`), which is the
   same resolution a chain performs. So `base + pressable_state` computes what
   `const base.cursor(..)…` computes — and it may take its base from a runtime
   parameter, because `+` emits nothing (P3, P7).

Probed: the class list `base + delta` produces is **byte-identical** to the one
the equivalent chain produces, and so is the emitted stylesheet (P3, and the
whole-exhibit diffs in §3).

The item asks "what is the smallest thing that removes the duplication?" The
answer is: **nothing in the compiler.** The duplication has been removable
since `+` shipped on 2026-07-10; what was missing is a written recipe.

**One correction to the item's premise, which matters for §6.** The item says
`button_style` "*is*" a const function that "const-evaluates per call site". It
is not: it is an ordinary **runtime** function whose `const` sub-expressions
were folded in place, and the branch survives into the JS. It *can* be const-
called — `const button_style(true)` folds the whole call, arguments and all
(P5) — but only where every argument is const-known, which is never true at
kolt's real call sites (`x == Route::Messages`). So "const functions with const
params" is not the lever it looks like; the lever is that a **const-only
function may take a `Style` parameter freely** (P6), which is a different fact
and is already true.

## 2. Four candidate spellings

Each is the whole exhibit rewritten, built and run — same `theme.vl`, same
harness — at 2, 3 and 6 interactive surfaces. "Surfaces" is the axis that
matters: the exhibit has two today, and every new button-shaped thing kolt
grows adds one.

**(A) As shipped.** Base chain plus three restated branches, per surface.

**(B) Const factoring.** The deltas as `impl Style` extension methods
(`selected_state`, `pressable_state`), still applied inside a per-branch
`const`:

```vilan
if selected { ret const base.selected_state(); }
if disabled { ret base; }
const base.pressable_state()
```

**(C) Runtime deltas + `+`.** The deltas as named module-level const styles,
and **one** selector function taking the base as a runtime parameter:

```vilan
fun interactive(base: Style, disabled: bool, selected: bool): Style {
    if selected { ret base + selected_state; }
    if disabled { ret base; }
    base + pressable_state
}
```

**(D) Attribute conditions.** No selector function at all: one const style per
surface carrying the whole state axis on the attribute condition
(`ui-styling.md` §0bis.6), and the markup switches the states.

```vilan
impl Style {
    fun interactive_states(self): Style {
        self
            .attribute("data-selected", "true", style().color(..).background(..))
            .attribute("data-pressable", "true", style().cursor(..).hover(..).active(..))
    }
}
```

### The measurements

Source lines, the style-defining region only, comment lines excluded:

| route | n=2 | n=3 | n=6 | per surface |
|---|---|---|---|---|
| (A) as shipped | 47 | 69 | 136 | **+22.3** |
| (B) const factoring | 50 | 67 | 119 | +17.3 |
| (C) deltas + `+` | 44 | 55 | 89 | **+11.3** |
| (D) attribute conditions | 32 | 40 | 65 | +8.3 |

Emitted bundle, bytes (node target, single file — the deltas are the honest
number; the constant is the shared prelude):

| route | n=2 | n=3 | n=6 | per surface |
|---|---|---|---|---|
| (A) as shipped | 7906 | 10956 | 20130 | **+3056** |
| (B) const factoring | 7906 | 10956 | 20130 | +3056 |
| (C) deltas + `+` | 6710 | 7643 | 10480 | **+942** |
| (D) attribute conditions | 4308 | 5946 | 10880 | +1643 |

Emitted stylesheet, lines:

| route | n=2 | n=3 | n=6 |
|---|---|---|---|
| (A), (B), (C) | 56 | 59 | 62 |
| (D) attribute conditions | 61 | 64 | 67 |

Three things fall out of the tables, and each is worth stating plainly.

- **(B) does not pay.** It is *longer* than (A) at n=2 (the `impl` block is
  overhead before it is leverage) and its bundle is byte-for-byte identical to
  (A)'s at every size. That is not a surprise once you look: `const-eval.md`
  §1 says "the result literal replaces the expression at its site", so a
  per-branch `const` inlines a **whole serialized `Style` map per branch**.
  Factoring the *source* of a branch changes nothing about how much of it the
  bundle carries. (A) and (B) ship 3 kB per new surface for this reason.
- **(C) costs the atomic model exactly nothing.** At n=2, n=3 and n=6 the
  stylesheet is byte-identical to (A)'s and all six class lists are
  byte-identical to (A)'s. It is the same styles, reached differently.
- **(D) is smallest on source and, up to about five surfaces, on bundle — then
  it loses.** Its marginal is 1643 bytes against (C)'s 942, because every
  surface's const style now serialises its base *and* five conditioned slots;
  the measured crossover is between n=3 and n=6 (at n=6, (D) is 10880 bytes
  against (C)'s 10480). Its stylesheet cost is a flat **+5 lines at every
  size** — a constant, not a per-surface tax, because the extra rules are the
  conditioned twins of declarations the sheet already carries and the channel
  dedups them.

## 3. Recommendation

> **Base + delta. Keep the base a const `Style` binding per surface; keep each
> variant a named const `Style` delta; select and merge at runtime with `match`
> / `if` and `+`. One selector function per state axis, taking the base as an
> ordinary runtime parameter.** For an enumerated variant set rather than a
> boolean state, the same shape with a **const table** — built from data at
> const time, looked up at runtime (§5).

It is (C). It is the shortest spelling that keeps variant selection in **value
semantics** — which is the property `ui-styling.md` §1 is built on and the one
(D) trades away — and it is the only candidate proven to change nothing about
the stylesheet.

The exhibit under it, in full:

```vilan
// The two states an interactive surface has, as named deltas. Each is a const
// style in its own right; `+` merges one onto any base at runtime.
let selected_state = const style()
    .color(Theme::primary_a())
    .background(Theme::primary_a().alpha(0.15));

let pressable_state = const style()
    .cursor(Cursor::Pointer)
    .hover(style().background(Theme::primary_a().alpha(0.1)))
    .active(style().background(Theme::primary_a().alpha(0.15)));

// One selector for every interactive surface: the base is a runtime Style,
// because `+` is runtime-legal.
fun interactive(base: Style, disabled: bool, selected: bool): Style {
    if selected {
        ret base + selected_state;
    }
    if disabled {
        ret base;
    }
    base + pressable_state
}

let button_base = const style()
    .display(Display::Flex)
    .gap(Length::rem(4f / 16f))
    .align_items(AlignItems::Center)
    .radius(Length::rem(4f / 16f))
    .script_label()
    .padding_x(Length::rem(8f / 16f))
    .padding_y(Length::rem(4f / 16f))
    .width(Length::raw("fit-content"))
    .user_select(UserSelect::Off);

let icon_button_base = const style()
    .padding(Length::rem(4f / 16f))
    .script_label()
    .text_align(TextAlign::Center)
    .radius(Length::rem(4f / 16f))
    .user_select(UserSelect::Off);

fun button_style(disabled: bool, selected: bool) {
    interactive(button_base, disabled, selected)
}

fun icon_button_style(disabled: bool, selected: bool) {
    interactive(icon_button_base, disabled, selected)
}
```

**47 lines → 44 on the table's measure (48 as written above, four of them the
comments the rewrite adds); 7906 bundle bytes → 6710.** At two surfaces the
line count is close to a wash and the note says so rather than dressing it up —
the win is the *slope*: a third surface costs 22 lines under (A) and 11
under (C), of which zero are restated variant logic. `chip_style` in the n=3
probe is its whole content and nothing else:

```vilan
let chip_base = const style()
    .display(Display::Flex)
    .script_label()
    .radius(Length::rem(12f / 16f))
    .padding_x(Length::rem(10f / 16f))
    .user_select(UserSelect::Off);

fun chip_style(disabled: bool, selected: bool) {
    interactive(chip_base, disabled, selected)
}
```

**Every call site in `views.vl` is untouched.** The signatures are preserved,
so `icon_button_style(false, false)`, the reactive
`bind_styled(get_route().map(|x| icon_button_style(false, x == Route::Messages)))`
and the per-site merge `button_style(false, false) + (const style()…)` all keep
working verbatim — probed together on the browser target (P13). The refactor is
entirely local to the two functions.

The recipe transfers unchanged to the `css { }` block spelling as it ships
today (P14) — `let pressable_state = const css { cursor: pointer; .hover { … } };`
then the same `+`. css-block.md §9's verdict holds in both directions: the
block does not answer 015, and 015's answer does not need the block.

## 4. What each candidate costs the atomic model

The constraint is deliberate and stays; here is the ledger against it.

| | class count per element | program class count / dedup | construct-in-const reachability | merge semantics |
|---|---|---|---|---|
| (A) as shipped | baseline | baseline | const expressions scattered through every selector body | record update |
| (B) const factoring | identical to (A) | identical to (A) | same, plus const-only `impl Style` methods | record update |
| **(C) deltas + `+`** | **identical to (A)** | **identical to (A) — byte-proven** | **smaller: emission is confined to module-level const bindings; selector functions contain no `const` at all** | record update |
| (D) attributes | larger, permanently | +1 conditioned rule per declaration, plus the recorded unconditioned twin — constant, not per-surface | one const binding per surface | **cascade** |

Four points, each earned by a probe or a measurement:

- **Class count and dedup are untouched by (C).** A delta hashes on
  `key|declaration`, and `+` inserts the already-minted entry — so the class a
  delta contributes is the same class the equivalent chain link would have
  minted. Proven at the exhibit's scale: identical stylesheet and identical
  class lists at n=2, n=3, n=6.
- **(C) shrinks the const-only frontier.** Under (A), `button_style` is a
  runtime function containing const expressions, and the const-only
  reachability check has to walk into every selector body. Under (C), emission
  happens in four module-level `let … = const …` bindings and the selector
  functions are plain runtime code. That is the same rule enforced over a
  smaller and more legible surface — abstraction *within* the rule, which is
  what 015 asked for.
- **(D) moves resolution out of value semantics.** `.sX[data-selected="true"]`
  and `.sX[data-pressable="true"]:hover` on the same property are (0,2,0) and
  (0,3,0): with both attributes set the browser resolves them, not the merged
  map. `ui-styling.md` §1's "specificity fights are structurally impossible"
  is a claim about the `Style` value, and (D) opts an element's state axis out
  of it. It is also *lossy in one direction*: CSS can override a declaration
  and cannot remove one, so the exhibit's `selected` shape — which **drops**
  the pointer cursor and hover — is expressible only by not setting the other
  attribute, i.e. by putting the mutual exclusion back in the caller.
- **(D)'s reactive site is clumsier.** `bind_attr` takes a `Signal<str>`, so
  the exhibit's `x == Route::Messages` has to become
  `if x { "true" } else { "false" }` (P13). `bind_styled(Signal<Style>)`
  already takes the value.

None of the four constructs a `Style` at runtime; all four are inside §3's
rule; (D) is the only one that pays for it somewhere else.

**Where (D) is still the right recipe** — and it should be documented as a
sibling, not suppressed: state the markup already carries. A `[data-open]`
disclosure, an `aria-expanded`, a `[data-density]` mode, anything an ancestor
sets and many descendants read. There the attribute exists whether or not the
style uses it, the state is not a value the component holds, and `within`/
`attribute` are exactly the mechanism `ui-styling.md` §0bis.6 shipped for it.
The dividing line the recipe should state: **if a component already holds the
state as a value, select with `+`; if the DOM already carries the state as an
attribute, select with `attribute`.** The exhibit is the first case.

## 5. The variant table, and generated variants

For an *enumerated* variant set — `Primary` / `Danger` / `Ghost`, not two
booleans — the same base+delta shape is spelled as a const table. Both index
forms work today (P4):

```vilan
let table = const [
    base.background(Color::blue(600)).color(Color::white()),
    base.background(Color::red(600)).color(Color::white()),
    base.color(Color::gray(600)),
];

fun variant(k: Kind): Style {
    match k {
        Kind::Primary => table[0],
        Kind::Danger => table[1],
        Kind::Ghost => table[2],
    }
}
```

and, for open string keys, `const` a `Map<str, Style>` and `get` it at runtime.
`Style` is plain data (a struct over `Map<str, (str, str)>`), so it survives
const serialisation and the table is a literal in the bundle.

The stronger form, and the one that answers "a recorded variant table" as the
item phrased it: **the table is generated from data at const time** (P11).

```vilan
struct Variant { name: str, fill: Color, ink: Color }

fun variant_table(rows: List<Variant>): Map<str, Style> {
    mut out: Map<str, Style> = Map::new();
    for row in rows {
        out.insert(row.name, base.background(row.fill).color(row.ink));
    }
    out
}

let variants = const variant_table([
    Variant { name = "primary", fill = Color::blue(600), ink = Color::white() },
    Variant { name = "danger",  fill = Color::red(600),  ink = Color::white() },
    Variant { name = "muted",   fill = Color::gray(100), ink = Color::gray(600) },
]);
```

That compiles, emits three rules and a `:root` line per token, and looks up at
runtime. Two facts worth recording because they are easy to guess wrong:

- **Const-time closures over const-only functions are fine.** `const-eval.md`
  §2's conservative rejection of an indirectly-passed const-only function is
  about making the value in *runtime* code; `const palette.map(|c| tint(base, c))`
  const-evaluates the closure and compiles (P10). So a generated variant table
  may be built with the ordinary iterator vocabulary.
- **The list is the recommended index when the keys are an enum**, because
  `match` is exhaustive-checked and the map is not: `variant("nope")` silently
  takes the `None` arm. Use the map only where the key really is open.

Recommendation for tables: **prefer the enum + `match` form; reach for the
generated map when the variants genuinely come from data.** Either way the
table's entries are const styles and the lookup is runtime — the same
base+delta discipline, indexed instead of branched.

## 6. Mechanism or recipe?

**Recipe.** The note recommends adding nothing to std.

The case for that is the measurement, not taste: the recommended spelling is
built entirely from `const` bindings, `impl Style`, `match`/`if`, and `+` — all
shipped since 2026-07-10 — and it produces a byte-identical stylesheet with a
3.2× smaller per-surface bundle cost than the shape kolt hand-wrote. Nothing
in the four rewrites was blocked on a missing std surface. What was missing is
the sentence *"factor the delta, not the branch"*, and sentences belong in
`guide/styling.md`.

Three mechanisms were considered and are recommended against:

- **A `Variants<K, V>` std type.** Buys nothing over `Map<str, Style>` and a
  `match`, both of which work (§5); it would add a type to learn and a second
  way to spell a lookup, against `ui-styling.md` §0bis.3's standing rule that a
  name buying nothing over what exists is surface, not expressiveness.
- **Const parameters** (letting `const expr` read a parameter when the
  enclosing call is itself const). This is the feature the duplication *looks*
  like it wants, and it is unnecessary: P6 shows the same factoring achieved by
  **removing** the inner `const` and letting the call site supply it. It would
  also be a real change to `const`'s one judgement, for a case that already has
  two exits.
- **A `Style::when(condition, delta)` runtime combinator.** The one genuinely
  plausible addition — see Q3 below. It is *five lines and no emission*, it
  works in user code today (P15), and it turns a three-branch selector into a
  chain:

  ```vilan
  base
      .when(selected, selected_state)
      .when(!selected && !disabled, pressable_state)
  ```

  The note does not recommend it, because the exhibit's states are mutually
  exclusive and `if`/`match` says that more honestly than two independent
  `when`s — but it is the owner's call, not the note's, and it is the only
  candidate where std would be adding something rather than renaming
  something.

The one place the recipe genuinely stops, stated so no one rediscovers it: **a
condition cannot be lifted onto an already-built `Style` at runtime.**
`style().hover(s)` reaches `emit` and is refused outside `const` (P12), so
"take this whole base and put it under `md`" is a const-time construction and
always will be. That is not a gap in the recipe; it is the construct-in-const
rule doing its job, and it is why deltas are written as *deltas* — a delta
carries its own conditions and merges flat.

## 7. Probes

All against `vilan 0.39.0 (2ad39dd09)`; each was compiled, and each program
that could run was run.

| # | what | result |
|---|---|---|
| P1 | `const base.cursor(..)` where `base` is a function parameter | **REFUSED** — "`base` is a runtime value; a `const` expression reads only compile-time-known bindings" |
| P2 | `impl Style` delta method called inside a `const` chain | compiles |
| P3 | the same delta reached by chain vs by `+` | compiles; identical class lists (`sbiovxm s1onu0uk` both ways) and identical CSS |
| P4 | const `List<Style>` indexed by an enum `match`; const `Map<str, Style>` looked up at runtime | both compile and run |
| P5 | `const button_style(true)` — a whole selector function const-called with literal arguments | compiles, folds to the branch's map |
| P6 | delta as a const-only **free function** over a `Style`, applied to a const-known local via `const interactive(base)` | compiles |
| P7 | deltas as named const styles applied by runtime `+`, base a runtime parameter | compiles; class lists and CSS byte-identical to P6 |
| P8 | one const style carrying `.attribute("data-selected", "true", …)` | compiles |
| P9 | a `Style` constructed inside a runtime branch | **REFUSED** — "`pick` (it reaches `asset::emit`) is compile-time-only; evaluate this call inside a `const` expression" |
| P10 | a const-only function reached through a closure — `const palette.map(\|c\| tint(base, c))` | compiles; **REFUSED** first when `palette` was a runtime `let` (same message as P1) |
| P11 | generated variant table: struct rows → `const variant_table([..])` → `Map<str, Style>` → runtime `get` | compiles and runs |
| P12 | lifting a condition onto a built style at runtime — `style().hover(s)` | **REFUSED** — const-only, as P9 |
| P13 | the recommendation at the reactive site (browser target): `.styled(fn(..))`, `.bind_styled(sig.map(fn))`, `+` with a per-site const delta, `.bind_attr` for route (D) | all four compile |
| P14 | the recipe in the `css { }` block spelling | compiles; a bare `#ffffff` inside a block is refused with the hole message |
| P15 | `impl Style { fun when(self, condition: bool, delta: Style): Style }` in user code | compiles and runs — no std change needed to have it |

The four whole-exhibit rewrites (A)–(D) were each built at 2, 3 and 6 surfaces;
(B) and (C) were diffed against (A)'s stylesheet and class lists at every size.

## 8. Owner questions

1. **Recipe or mechanism?** The note recommends documenting base+delta in
   `guide/styling.md` and adding nothing to std. Accept, or does the owner want
   a std surface for variants?
2. **Is `interactive(base, disabled, selected)` the shape to document** — one
   selector function per *state axis*, taking the base as a runtime parameter —
   or should the recipe stay at the smaller "hoist the deltas, keep one
   function per surface" step, leaving the shared selector to each app?
3. **Does `Style::when(condition, delta)` ship?** Five lines, runtime-legal, no
   emission, works in user code today (P15). It buys a chain spelling for
   independent boolean state and buys nothing for mutually exclusive states.
   The note does not recommend it and does not object to it.
4. **Is route (D) documented as a sibling recipe, and on what line?** The note
   proposes: *select with `+` when the component holds the state as a value;
   select with `attribute` when the DOM already carries it.* (D) is measurably
   shorter in source and, below ~5 surfaces, in bundle — but it moves that
   element's state resolution from the merged map into the cascade, which §1
   claims is structurally impossible for a `Style`. Is that trade worth
   documenting, or should the guide keep (D) for ancestor state only?
5. **Enum table or map table as the recommended n-ary form?** The note prefers
   `enum` + `match` for exhaustiveness and reserves the const `Map` for keys
   that are genuinely open. Confirm, or make the map the primary spelling?
6. **Does kolt's `views.vl` get rewritten under this?** The rewrite is local to
   the two functions, preserves both signatures, and emits a byte-identical
   stylesheet — a candidate for a narrow graft, or left until kolt grows a
   third interactive surface and the slope starts to bite?
7. **Is the (B) finding worth recording in `ui-styling.md` §1?** That a
   per-branch `const` inlines a whole serialized `Style` map per branch — so
   branch duplication in the source is branch duplication in the bundle
   (3056 bytes per surface here) — is a consequence of `const-eval.md` §1's
   in-place serialization that nothing currently states where a styling author
   would read it.
