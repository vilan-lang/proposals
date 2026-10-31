# Lengths as data — A178

- status: BUILT 2026-10-31 - S1 + S2 landed on next (lane std-a178 @5d984949, merged 7911d954; rides v0.54.0); S3 = the owner's codemod (sweeps/order55/a178/dp_codemod.py, proven byte-identical on kolt). Approved as written; what did not survive contact: no associated consts (`Length::root_px()`), `zero()` is the arithmetic zero, `dp(0)` renders `0rem`, a `dp` inside a `calc` is written in rem, a css block's undotted `border(dp(1))` writes rem (owner Q4 in owner-questions55.md)
- tracker: A178 (filed 2026-10-31 by kolt); touches A8, A106, B340
- area: `std::web::style` — `Length`, the property builders, the hole vocabulary

## 0. The problem, in one line

`Length` is its CSS text, so an app keeps every number as an `f64` until the
call site and converts there: kolt writes `rem(n / 16)` 540 times, keeps its
spacing constants as `f64` because a `Length` cannot be added to or scaled, and
has five spellings for one idea. The `/ 16` encodes "16px = 1rem" at every site.

## 1. What a length is

```
export struct Length {
	value: f64,   // the number, for a unit length; 0 for a text length
	unit: Unit,   // which kind
	text: str,    // the whole value, for a text length ("auto", "0", "var(--space-4)", "calc(..)", raw); "" otherwise
	root: str,    // the token's `:root` line, as today ("" when none)
}

export enum Unit { Dp, Px, Rem, Em, Pct, Vh, Vw, Text }
```

Two kinds of length, one type:

- **A unit length** is `value` + `unit` (`Px`, `Rem`, `Em`, `Pct`, `Vh`, `Vw`,
  and the new `Dp`, §2). It renders as `{value}{unit}` at the edge, exactly as
  the constructors render today — `Length::px(8)` still comes out `8px`,
  `Length::rem(0.5)` still `0.5rem`. Nothing an existing program wrote changes
  its CSS.
- **A text length** keeps `text` whole: `auto`, the bare `0`, `var(--w)`,
  `calc(..)`, `raw(..)`, and the tokens `space(step)` mints (their `root` line
  rides along as today). The representation does not model what is inside the
  text; it never did.

`CssValue` keeps its contract: `css_text()` renders either kind, `css_root()`
is `root`. Nothing outside std reads the fields (kolt constructs no `Length {..}`
literal and reads no `.text`), so the field change is not breaking for the
estate; the struct literal is std's own.

## 2. The design pixel: `dp`

The missing unit is the one kolt already uses in every `/ 16`: a pixel *at the
root size*, 1/16 rem, meant as a design measurement rather than a CSS unit.

```
Length::dp(8)    // hole alias: dp(8)
```

A `Dp` length carries **no unit preference**. The property that receives it
picks the unit (§4): `padding(dp(8))` renders `padding:0.5rem` so it follows the
user's text size; `border(dp(1), gray(300))` renders `border:1px solid ..` so a
hairline stays a hairline. Outside any property (`piece(dp(8))` in a string) it
renders in rem, the default role.

**`px` keeps meaning CSS px.** An explicit `Length::px(..)` or `Length::rem(..)`
is never re-unitized, as A178 asks; the docs' `width(px(200))` measures 200px
and stays so. That rule needs a spelling for "exactly this CSS unit" and a
spelling for "this many design pixels", so re-meaning `px(8)` as the design
length (A178's alternative) would leave no way to say the first — and the 82
`px(` sites in kolt are mostly hairlines, which render px under either reading.
The name is the owner's call (§8 Q1); `dp` is proposed because it is two letters
in a hole, it is not a CSS unit (no reader expects `8dp` in a stylesheet), and
its meaning in the platforms that use it — a pixel independent of the device —
is the meaning here.

## 3. Arithmetic, conversion, comparison

Operators, through the std traits (`Add`, `Sub`, `Mul<f64>`, `Div<f64>`;
`operators.vl` has no `Neg`, and `dp(-4)` is the negative margin):

| expression | result |
|---|---|
| `dp(8) + dp(4)` | `dp(12)` — same unit, same unit |
| `rem(1) + rem(0.5)` | `rem(1.5)` |
| `rem(0.5) + dp(1)` | `rem(0.5625)` — `Dp` is defined as 1/16 rem = 1 px at root, so it **bridges** `Px` and `Rem`: the other side's unit wins |
| `px(8) + dp(1)` | `px(9)` |
| `px(8) + rem(0.5)` | `calc(8px + 0.5rem)` — not the same at any root size but 16; the truthful answer is CSS's |
| `space(4) * 2`, `space(4) + px(1)` | `calc(var(--space-4) * 2)`, `calc(var(--space-4) + 1px)` — a token or any text length composes through `calc`, the root line kept |
| `dp(8) * 1.5`, `dp(8) / 2` | `dp(12)`, `dp(4)` |
| `em(1) + pct(50)` | `calc(1em + 50%)` |

The rule is three lines: same unit → same unit; `Dp` with `Px`/`Rem` → the
named unit; anything else → `calc` of the two renderings. A `calc` result is a
text length and keeps composing (`(space(4) + px(1)) * 2` →
`calc((var(--space-4) + 1px) * 2)`).

Conversion is explicit and only where it is defined: `as_rem()` on `Px`/`Dp`/
`Rem`, `as_px()` on `Px`/`Dp`/`Rem`, `as_dp()` likewise, all through the one
constant `Length::ROOT_PX = 16`. On `em`/`pct`/`vh`/`vw`/text they panic — at
const time, since chains are built in `const` expressions, so a misuse fails the
build. **No app-level root-size setting** (A178 §2 floats one): the root size
that matters is the browser's, which the app cannot know, and `rem` exists so
the app does not have to; a settable constant would be a hidden global that
makes `dp(16)` mean different things in two files. If a project really designs
at another root, `Length::dp_at(root, value)` is the door, not a setting (Q2).

Comparison: `PartialOrd` between lengths of one unit, or between `Dp`/`Px`/`Rem`
through the constant; mixed otherwise panics at const time ("compare lengths in
one unit; convert first"). `Eq` is structural.

## 4. The unit a property prefers

Each property builder passes a **role** to `with_length`; the role decides how a
`Dp` length renders and nothing else (an explicit unit is untouched):

- **`Role::Rem`** (spacing and sizing, follows the text size): `gap`, `padding*`,
  `margin*`, `width`/`height`/`size`/`min_*`/`max_*`, `inset`/`top`/`right`/
  `bottom`/`left`, `radius`, `font_size`, `letter_spacing`, `line_height_length`.
- **`Role::Px`** (hairlines, stay crisp at any text size): `border*` widths,
  `outline_width`, `outline_offset`, `box_shadow` offsets/blur/spread, the
  `translate`/`transform` lengths if any builder takes them.

The table lives beside the builders in `style.vl` (one word per builder), and
`docs/std/style.md`'s property table gains a column. `radius` under rem is a
taste call (Tailwind's choice; Q3). `with_length` today is
`self.raw(property, value)` through `CssValue`; it becomes
`self.raw(property, value.rendered(role))`, and `css_text()` stays the
role-less rendering (rem).

## 5. Tokens, scales, the runtime channel

- `space(step)` is unchanged (a text token with its root line); it now also
  adds, scales and compares as §3 says — through `calc`, since a token's value
  is the theme's, not the program's.
- Kolt's `Scale` (B340's customer, `src/lib/scale_step.vl`) is REPLACED: its
  `size(n)` is `0.25rem * n`, which is `dp(4 * n)` exactly, and every one of its
  60 sites feeds a rem-role property (gap 28, margin/padding 20, size/width/
  height/min 7, radius 3) — so the migration renders byte-identical CSS and the
  struct and its file are deleted. `Callable` stays a language feature; it just
  loses this customer. S3 BAKES the multiplication: `size(4)` becomes `dp(16)` at the
  site, no step constant kept (the owner, 2026-10-31: the quarter-rem step only
  mirrored Tailwind's model; design pixels need no step).
- `view.style_var(name, source)` takes a `Flow<str>` today; a
  `style_var_length<S: Flow<Length>>` that maps through `css_text` is a one-line
  door (not in A178; Q4).

## 6. What kolt's code becomes

```
let bar_inset = 4f;                 →  const let bar_inset = dp(4);
gap(rem(bar_inset / 16));           →  gap(bar_inset);
padding(rem(0), rem(bar_inset / 16)); → padding(dp(0), bar_inset);
height(rem(bar_height / 16));       →  height(bar_height);
rem(8 / 16)  (163 sites)            →  dp(8)
rem(-4 / 16)                        →  dp(-4)
width(rem(448 / 16))                →  width(dp(448))
border(px(1), gray(300))            →  unchanged (or dp(1): same CSS)
size(4) / size(2)  (60 sites)       →  dp(16) / dp(8)  — the scale's step baked in; scale_step.vl deleted
```

A codemod does the bulk: `rem\((\w+) / 16\)` → `dp($1)` (540 sites) and the
constants' declarations by hand (nine in `styles.vl`); the tool lives in
proposals beside the css codemod from Order 37. The number formatting is exact:
every `n / 16` kolt writes is a binary fraction, so `dp(6)` renders `0.375rem`
as `rem(6 / 16)` does today, and the stylesheet's class hashes do not move.

## 7. Slices

- **S1 — the representation** (std; non-breaking): `value`/`unit`/`text`/`root`,
  every constructor, `CssValue` as today; the operators and conversions of §3;
  pins: each row of §3's table renders as written, idempotent hashes for every
  existing golden (the std/examples/website/kolt stylesheets byte-identical).
- **S2 — `dp` and the roles** (std + the prelude + docs): `Length::dp`, the hole
  alias, `Role` and the table of §4, `docs/std/style.md` + `guide/styling.md`.
  Estate: zero moves (nothing writes `dp` yet).
- **S3 — kolt's migration** (the owner's, with the codemod from proposals; the
  Kolt task "Spacing: one spelling for lengths").
- Doors: `style_var_length` (§5); `Ord` over lengths for `max_of` in layout
  code; a `Length::min/max/clamp` trio rendering `min()`/`max()`/`clamp()`
  (today `raw`).

Sizing: S1 S, S2 S, together one std lane (Order 56; after N186 in the
tooling order nothing here is on the hot path, but the asset channel's const
checks must still pass — `emit` is reached only from the builders, unchanged).

## 8. Questions for the owner

1. **The name** of the design unit: `dp` (proposed), `design`, `du`, or re-mean
   `px` (argued against in §2).
2. **No root-size setting** (§3) — agree, or want `dp_at(root, ..)` / a const?
3. **`radius`** under rem (proposed) or px?
4. **`style_var_length`** in S2 or left as a door?
5. **`Dp` bridging `Px`/`Rem`** in arithmetic (§3) — or strict same-unit with
   `calc` for everything mixed? (Bridging is what makes `size(2) + dp(1)` data;
   strict is simpler to explain.)
