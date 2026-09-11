# Positional slots — `when`, `swap` and `each` as `Slot` VALUES

Tracker A85. Written by lane ui-32 of order 32, on vilan `next` @65af4be0 plus this
order's A71 (`202aadee`), which is this design's first brick and is already shipped.
The owner is asked to rule **the surface** (§9); the build is the order after.

Related: A71 (the anchor primitive — built), A46 (fragment syntax), B253 (a trait in
return position stays refused), A42 (the `bind_each` siblings), B268 (the child
contract), `proposal/ambient-owner.md` §4/§5, `proposal/element-syntax.md` §5/§7,
`proposal/bundle-splitting.md` §2/§4.

---

## 1. What is already true (A71, this order)

`trait Slot { fun place(self, parent: View) }` (`browser/ui.vl`, process twin in
`process/ui.vl`) is the child contract, six arms: `View`, `str`, `List<View>`, and a
`Source` of each. `View::child<C: Slot>` is the one universal child position, and
element syntax lowers every `{x}` hole to it.

A71 added the missing primitive and used it everywhere the module appended:

- `std::dom` gained `Element::insert_before(child: Element, anchor: Text)` and
  `Text::remove`.
- `std::ui` gained `Region { parent: Element, anchor: Text }` with `open(parent)` /
  `insert(child)` / `close()`. `open` appends an EMPTY TEXT NODE at the parent's
  current end — which is the caller's position in the chain — and `insert` puts a
  child before it. Re-inserting a live element MOVES it, so the same call is a
  reconciler's order pass.
- `when`, `swap`, `bind_each`, `bind_each_values`, `bind_each_by` and the
  `Source<View>` / `Source<List<View>>` Slot arms each open a region where they are
  called and insert into it. Signatures are unchanged; the region is internal.
- The anchor is an empty text node rather than a comment because it serializes to
  NOTHING, which is what keeps a browser tree and the `@process` twin's HTML string
  byte-comparable (`ssr_differential`); a `<!---->` would not. The process twin
  declares `Region` for the twin-surface gate (E34) and calls it nowhere: a server
  render is one pass in source order, so appending already IS inserting before the
  anchor.
- Cost, measured on a 1,000-row `bind_each` driven through a refresh, a reorder and a
  rebuild: **one extra node and one extra host insertion per region, zero per row**
  (4,003 host insertions before; 4 appends + 4,000 `insertBefore` after), +5.8M Ir
  (+0.22%) under callgrind on a jitless node.

So the mechanism A85 needs exists and is paid for. **What is left is the SURFACE**:
today the three forms are METHODS ON THE PARENT, which means a conditional or a keyed
run that is not the parent's only content still costs a wrapper element — not for
position any more, but because there is no way to spell "this is one child of mine".

## 2. The ask, restated

Three things, one mechanism:

1. **A fragment as one child.** `List<View>` already is (the static arm); A46's
   `<>..</>` is its literal. Position when the list is reactive: solved by A71.
2. **A positional conditional.** `<nav>{brand}{when(logged_in, || account())}{footer}</nav>`.
   Today the `when` is a method on `nav` — it is *placed* correctly since A71, but it
   cannot be written between `brand` and `footer`, so the ordering of the chain is
   `nav.child(brand).when(..).child(footer)` and the reader has to know that a
   dotted link and a child interleave.
3. **A positional keyed run.** `<ul>{header}{each(items, key, row)}</ul>` — same story.

## 3. The design

### 3a. The values

Three free functions in `std::ui`, each returning a struct that implements `Slot`:

```vilan
fun when<S: Source<bool>>(
	condition: S,
	body: (sync || View) context owner_scope,
): Conditional<S>

fun swap<T: PartialEq, S: Source<T>>(
	source: S,
	render: (sync |T| View) context owner_scope,
): Swap<T, S>

fun each<T: PartialEq, K: PartialEq, S: Source<List<T>>>(
	source: S,
	key: sync |T| K,
	render: (sync |T| View) context owner_scope,
): Each<T, K, S>

fun each_values<T: PartialEq, S: Source<List<T>>>(..): EachValues<T, S>       // A42
fun each_by<T, K: PartialEq, S: Source<List<T>>>(..): EachBy<T, K, S>         // A42
```

**The closures are FIELDS, not type parameters.** That is load-bearing, not a style
choice: a helper returning one of these has to be able to NAME the type (§6), and a
type parameterized by a closure's own type is unnameable. So:

```vilan
struct Conditional<S: Source<bool>> {
	condition: S,
	body: (sync || View) context owner_scope,
}

impl Conditional<type S: Source<bool>> with Slot {
	fun place(self, parent: View) {
		// exactly today's `View::when` body, against a region
		let region = Region::open(parent);
		...
	}
}
```

Each `place` is the method's existing body verbatim, with `Region::open(parent)`
where the method has `Region::open(self)`. No new semantics are introduced anywhere
in this item: A71 already moved the bodies onto regions, and this moves the call site
that opens one from the method to `place`.

### 3b. The methods become sugar

```vilan
fun when<S: Source<bool>>(self, condition: S, body: (sync || View) context owner_scope): View {
	self.child(when(condition, body))
}
```

…and likewise for `swap`, `bind_each`, `bind_each_values`, `bind_each_by`. **Nothing
breaks**: every existing call site, every doc page, every corpus program and kolt all
keep compiling and behaving identically, because `child` places at the parent's
current end, which is where the method appended its region anyway. The docs steer to
the value form where position matters; the method form stays right for "this element's
content IS the conditional/run", which is the common case.

The naming question the owner should settle with the surface: the free functions
`when`/`swap` share a name with the methods (fine — method vs free function resolve
differently) but `each` deliberately does NOT share `bind_each`'s. Recommendation:
the value forms are `when` / `swap` / `each` / `each_values` / `each_by`, and the
methods keep `bind_each*`. The `bind_` prefix means "one property kept in sync" on
every other method in the module; a value that *is* a child has no property to bind,
and `{each(items, key, row)}` reads as markup where `{bind_each(..)}` reads as a
setter that has escaped.

### 3c. What element syntax does with them

Nothing new. `{expr}` lowers to `.child(expr)` and `child<C: Slot>` dispatches. So
`<ul>{header}{each(items, key, row)}{when(more, || footer_row())}</ul>` is already
legal the day the values exist — which is the point of having built the child contract
as a trait.

### 3d. The SSR twin

`process/ui.vl` grows the same five free functions and five structs, and their `place`
pushes the content into the parent's child list at the position `place` runs — no
anchor, exactly as §1 records for the shipped `Region` there. The twin-surface gate
(E34) enforces the name parity; `ssr_differential` will need its shared component
extended with one value-form hole to hold the shapes against each other.

### 3e. Ownership

Unchanged (`ambient-owner.md` §5). A row and a `when` body run under a fresh `Owner`;
the region belongs to the enclosing boundary and its `defer` closes it. `place` runs
in the caller's ambient scope, which is the same scope the method ran in, so no
boundary moves.

## 4. The fragment interplay (A46)

- A46's `<>..</>` lowers to a `List<View>` LITERAL. That is A46's build and this item
  does not change it.
- A `Source<List<View>>` of fragments keeps position through the region — **shipped in
  A71**, which is the half A46's recommendation left open.
- A46's third form, "a component returns multiple roots" (a fragment that MOVES and
  DIES as a unit), is exactly a region VALUE: `fun toolbar(): Group` where `Group`
  holds a `List<View>` and a region, placing all of them before one anchor and
  removing them together. **Price**: the struct and its `Slot` impl are ~40 lines and
  need no new machinery; what it costs is a fourth thing in the estate that is
  "several nodes with one identity", beside `List<View>`, `Each` and `Source<List<View>>`.
  Recommendation: do NOT build `Group` with this item. The three positional forms cover
  every exhibit in the census (§7); a `Group` has no call site yet, and the honest
  version of "a component returns multiple roots" is `fun toolbar(): List<View>` plus
  the static arm until one appears.

## 5. The one implementation risk, to probe first

**A struct field typed as a context-carrying closure** — `body: (sync || View) context
owner_scope` — is the only part of §3a that is not already a shape std writes. Context
is passed as a hidden parameter at the CALL (visible in emitted JS as the extra `$xx`
arguments), and every existing context-carrying closure in std is a PARAMETER, applied
in the same function that received it. Storing one in a struct and applying it later,
from `place`, must resolve the ambient owner at `place`'s call and not at the value's
construction — which is what is wanted, and is what `child(when(..))` needs to mean —
but nothing pins it today.

Step 0 of the build is a five-line probe: a struct with such a field, constructed
outside a boundary, applied inside one. If it does not hold, the fallback is that the
value forms take their bodies at `place` time through a trait the app implements,
which is materially worse ergonomics, and the item should come back for a ruling
rather than ship that.

There is fresh evidence that closure typing is not uniform across these positions.
This lane added `View::link_to` to `std/browser/router.vl` — an INHERENT IMPL METHOD
whose body passes a closure to the process twin's generic `on_event<E>(.., sync |E| void)`
— and the call inside the closure body (`plain_left_click(event)`, whose parameter is
the concrete `Event`) did NOT pin `E`, where the same body in a FREE FUNCTION did:
a process build failed with "cannot call method 'prevent_default' on E". An explicit
`|event: Event|` fixes it and is now written down at the site. Whatever the solver is
doing differently there is worth knowing BEFORE a struct field joins the picture, and
it is filed from this lane as its own candidate.

## 6. B253's spelling cost

A trait in CHILD position is the universal bound (`child<C: Slot>`) and needs nothing.
A trait in RETURN position — `fun footer(): Slot` — is the existential, and B253
(order 29) RULED it stays refused: vilan has no opaque-type kind and no trait objects
(`trait-objects.md`, ratified 2026-08-07). So a helper that returns one of these values
spells the concrete type:

```vilan
fun account(): Conditional<SignalCell<bool>>
fun theme_rows(): Each<Theme, Theme, SignalCell<List<Theme>>>
```

The first is fine. The second is the shape that hurts, and it is the shape a generic
list helper takes: `Each<T, K, S>`'s three parameters are all *inferable at the call*
and all *unwritable at the return*.

**Whether that is bearable is an empirical question, and §7 answers it for the one
real app.** The short version: kolt has **zero** helpers that would return a positional
slot today, and exactly **one** it would plausibly grow. So B253 does not reopen on
this item's evidence — which is the outcome A85 said to look for ("if it is unbearable
in practice, B253 reopens on THAT exhibit — not before").

## 7. The kolt census (read-only, `~/code/kolt/src` at 2026-09-11)

Counting only UI positional forms. `styles.vl`'s six `.when(..)` calls are
`Style::when` (A36) and are NOT this — a different trait, a different meaning; anyone
grepping this census must exclude them, which is itself a finding about the name.

**Ten positional forms, in three files:**

| # | site | form | host element |
|---|---|---|---|
| 1 | `channel.vl:28` | `bind_each_values(messages, ..)` | **bare `<div/>`** |
| 2 | `views.vl:70` | `swap(client.map(is_some), ..)` | `<div>` with `toggle_attr` + `styled` |
| 3 | `views.vl:123` | `swap(get_route(), ..)` | `<div>` with a real `min-width` style |
| 4 | `views.vl:127` | `swap(Channel::find(id), ..)` | **bare `<div/>`** |
| 5 | `views.vl:202` | `bind_each_values(channels, ..)` | `<div>` with `flex_col` + `gap` |
| 6 | `views.vl:204` | `swap(Channel::find(channel_id), ..)` | **bare `<div/>`** |
| 7 | `views.vl:564` | `bind_each_values(filtered_themes, ..)` | styled `<div>`, **plus one sibling child** |
| 8 | `views.vl:608` | `swap(theme_delay_enabled, \|x\| icon(..))` | the `<button>` itself |
| 9 | `views.vl:776` | `bind_each_values(filtered_commands, ..)` | styled `<div>`, **plus one sibling child** |
| 10 | `lib/overlay.vl:544` | `container.when(overlay.open, ..)` | the portal container |

**Wrapper elements whose only job is to hold a position: 3** (rows 1, 4, 6). All three
are bare `<div>`s carrying exactly one dotted link and no style, no attribute and no
other child.

**But only ONE of the three is removed by this item as specified**, and that is the
sharpest thing this census says:

- Row 1 (`channel.vl:28`) is a plain CHILD of a styled `<div>`. It becomes
  `<div .styled(padding)>{each_values(messages, ..)}<form ../></div>` — **removed**.
- Row 4 (`views.vl:127`) is the result of a `swap` RENDER closure, which is typed
  `|T| View`. A slot cannot be returned there.
- Row 6 (`views.vl:204`) is a `bind_each` ROW, and the reconciler moves one ELEMENT per
  row. A row that is a region is a different (L-sized) reconciler.

So the honest tally is **1 wrapper removed, 2 blocked on "a render closure may yield a
Slot"**. For `swap` that is a small extension (a region inside a region, and `Swap`'s
render typed `|T| C` for `C: Slot`); for `Each`'s rows it is a redesign of the order
pass, which is A85's own §(e) and should stay out of the first build. The paper
recommends shipping the surface with `View`-returning closures and filing the
render-yields-a-slot widening as its own item, with rows 4 and 6 as its exhibits.

**Helpers that would return a positional slot: 0 today.** kolt's view helpers
(`app_shell`, `sidebar`, `channel_component`, `not_found_component`, `icon`) all return
real element trees. The one that WOULD appear is the theme modal / command palette
pair (rows 7 and 9), which are the same 20 lines twice — a filtered list plus a
`show`-gated "No matches :(" — and the natural extraction is
`fun filtered_list<T>(items: SignalCell<List<T>>, render: ..): Each<T, T, SignalCell<List<T>>>`.
That is the whole of B253's cost in this estate: one generic helper, one mouthful of a
return type, and it is writable.

**A latent bug the census found (no kolt change owed).** Rows 7 and 9 write
`.bind_each_values(..)` as a dotted link and the empty-state `<div .show(..)>` as a
CHILD. Element syntax desugars the dotted links BEFORE the children (`elements.rs`), so
the run was placed first and the empty-state element after it — and then, before A71,
every filter keystroke re-appended the rows BEHIND the empty-state div. It was never
visible because `show` hides that div exactly when rows exist. A71 fixes it; it is
recorded here because it is the plainest evidence that "put it last" was a rule nobody
could actually follow.

**Two stale comments in kolt, for the follow-up list:** `views.vl:606` says
"HACK: Swap needed because embedded signals of `View`s don't work correctly (they get
stringified)" — that is B268, fixed; with A71 the site can be a plain `{signal}` child
and keeps its position. `views.vl:213`'s `draggable("false")` and its comment are B293,
now std's job.

## 8. Costs this item must pay that are not in the value structs

1. **Bundle splitting hooks on the METHOD.** `chunks.rs:90` finds the split-eligible
   call with `view_method(program, "swap")` and rewrites it to `View::swap_split`
   (`bundle-splitting.md` §2/§4). An app that adopts the value form `swap(route, render)`
   would **silently stop splitting** — the worst possible failure mode, since the build
   still succeeds and the bundle is merely whole again. The build must either teach the
   recognizer the value form (a second `Id`, and a `Swap`-value gate beside
   `swap_split`) or refuse a `split = true` entry whose route swap is a value. This is
   not optional and it is the largest single piece of work in the item.
2. **`platform_color.rs:248`** reads `View.swap_split` and the bindings its body reads;
   same widening.
3. **Docs**: `guide/ui.md` (the child contract and the three forms), `std/browser.md`
   (the View table plus the new free functions), `guide/routing.md` (the page container
   is the exhibit everyone copies).
4. **Pins**: `ui_rows.rs` for each value form in a middle position (A71's five pins are
   the template), `ssr_differential` for the twin, `split.rs` for cost 1.

## 9. The ruling asked, and the sizing

**Ruling (the surface).** Ship the five value forms `when` / `swap` / `each` /
`each_values` / `each_by` in `std::ui` (and their process twins), as structs with
concretely-typed closure FIELDS implementing `Slot`, with the five parent methods
rewritten as one-line sugar over them and their signatures unchanged. Render closures
keep returning `View` in v1. `Group` (A46's multi-root) is NOT built. B253 stays as
ruled — the census does not reopen it.

Three sub-questions the owner may want to answer with it:

- **Q1 — the names.** `each` beside `bind_each` (recommended), or `bind_each` for both?
- **Q2 — the split gate (§8.1).** Teach the recognizer the value form (recommended,
  and priced into the M below), or refuse a value-form swap in a `split = true` entry
  for v1 and say so in the diagnostic?
- **Q3 — render closures yielding a `Slot`.** File as its own item with kolt rows 4
  and 6 as exhibits (recommended), or fold the `swap` half into this build?

**Sizing: M.** The value structs and their `Slot` impls are mechanical — each `place`
is a body that already exists — and the methods-as-sugar rewrite is five lines each
with no migration. The M is made of three things and not of the structs: the
context-carrying closure field must be probed first (§5), the split recognizer must
learn the value form (§8.1), and the process twin plus `ssr_differential` must move in
step. Roughly: ~250 lines of std across the two twins, ~120 lines in `chunks.rs` /
`transformer.rs`, ~300 lines of pins, three docs pages. An L only if Q3 is folded in.
