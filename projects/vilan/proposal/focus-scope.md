# Focus scopes — a tabbable query, a trap, and a restore (A121)

Tracker A121. Written by lane papers-39 of Order 39, on vilan `next` @c3f7d1a3
(`vilan 0.40.0 (c3f7d1a38)`). The owner is asked to rule §10 (six questions);
the build is §9, as S1 then S2.

**There is no browser on this host, so every behavioural claim below is derived
from the HTML specification and from `std::dom`'s bindings, not measured.**
§8 lists exactly which claims are untested and what would test them. What IS
measured is that the whole surface COMPILES against today's std — the design is
written out as a userland module and built for a browser target
(`probes/a121_focus_scope`, 9,610 bytes of emitted bundle) — and which DOM reads
std does not have (`probes/a121_missing_bindings`, read off the emitted JS).

Related: A45 (`View::on_mount` / `View::autofocus` / `Element::focus`, CLOSED
Order 27 — the neighbour this stands on), B271 (`autofocus` is frame-aware and
bounded, CLOSED Order 30 — the timing rule this design is forced by), A59
(`bounding_rect`, `observe_resize`), A96 (the HMR socket teardown, for the
`Owner::defer` shape), `proposal/ambient-owner.md` (`Owner::take`/`defer`),
`proposal/router.md` §5.1–§5.2 (the listen/`Subscription` discipline this
reuses).

Probes: `scripts/integration/sweeps/order39/papers-39/probes/a121_focus_scope/`
(the design, in userland, built for the browser) and
`probes/a121_missing_bindings/` (the four DOM reads, with what each one emits),
re-runnable with `probes/run_all.sh`.

---

## 1. The requirement, and what kolt has instead

kolt's overlay driver, `lib/overlay.vl:531-541`, inside the `relayout` pass that
flips the panel visible:

```vilan
if !focused.read() {
	focused.write() = true;
	if panel_element.query_selector_all("[x-autofocus]").get(0) is Some(let target) {
		target.focus();
	} else {
		// FIXME: Focus the panel is such a way that tab moves to the first tab-able thing.
		//        Or even better, make the overlay the only tab-able container (opt-in/opt-out),
		//        even for menus, without making the top-level container inert (which, in the
		//        case of menus, would be wrong).
		panel_element.focus();
	}
}
```

Three things are being asked for, and one thing there does not work.

**What does not work: the `else` branch is a no-op.** The panel is
`<div .styled(panel_frame_style + overlay.panel_style)>` (`overlay.vl:473`) and
nothing in either style sets `tabindex` — `grep tabindex` over
`lib/overlay.vl` finds nothing. `HTMLElement.focus()` focuses a *focusable
area*, and a `div` with no `tabindex` is not one, so the call returns having
done nothing and focus stays wherever it was — usually on the button that opened
the overlay, which is behind the scrim. `std::dom::Element::focus`'s own doc
comment lists the preconditions as "connected, rendered, visible and not inert
AT THE CALL" and **omits focusable**, which is the omission that let this be
written. (Derived from the HTML spec's focusing steps, not measured — §8.)

**What is asked for, as three separable things:**

1. **A first-tabbable query.** "Tab moves to the first tab-able thing" — which
   means either focusing the first tabbable descendant, or focusing the panel in
   a way that puts the next Tab there. The first is simpler and is what every
   dialog implementation does.
2. **A containment**, opt-in per overlay — "make the overlay the only tab-able
   container … even for menus".
3. **Without `inert`.** And the parenthetical gives the reason: for a menu,
   inerting the page is wrong. It is also wrong for a third reason kolt does not
   state — `inert` removes the subtree from the accessibility tree and blocks
   pointer events, so it is not a focus tool, it is a "this subtree does not
   exist" tool.

Plus the two the FIXME does not mention and every implementation needs: **a
restore on close**, and **nesting**, because kolt's submenus are overlays
attached from inside their parent's body.

## 2. The answer, in shape

```vilan
// std::dom
impl Element {
	fun tabbable(self): List<Element>;      // in Tab order
	fun focus_first(self): bool;            // → did it take?
	fun tab_index(self): i32;               // new binding, one line (§7)
}

// std::ui
export enum FocusContainment { Contain, Wrap }

export struct FocusScope { .. }

/// Install the scope; it focuses NOTHING until asked.
export fun focus_scope(root: Element, containment: FocusContainment): FocusScope;

impl FocusScope {
	fun focus_initial(self): bool;          // idempotent; the SHOW calls it
}

impl View {
	/// The chained sugar, on `autofocus`'s bounded clock.
	fun focus_scope(self, containment: FocusContainment): View;
}
```

Five decisions carry the design, and each is forced by something already in the
tree rather than chosen.

## 3. The tabbable query is a WALK, not a selector

The literature's shape for this is one big selector —

```
a[href], area[href], input:not([disabled]), select:not([disabled]),
textarea:not([disabled]), button:not([disabled]), iframe, object, embed,
summary, audio[controls], video[controls], [contenteditable], [tabindex]
```

— and the probe wrote it that way first (`probes/a121_focus_scope/src/focus.vl`
carries it as `tabbable_selector()`, and the emitted bundle has the string in
it). **It should not ship that way**, and the argument is the test harness:

`crates/vilan-cli/tests/support/dom/stub.js` — the DOM the whole `ui_rows` /
`reactive_lifetimes` suite runs against — implements `querySelectorAll` as a
**tag-name comparison** (`if (child.tagName === selector)`), and `matches`
**throws** for anything but `":focus"`:

```js
matches(selector) {
    if (selector !== ":focus") throw new Error("the stub knows only :focus, got " + selector);
    return global.activeElement === this;
}
```

So a selector-driven query is not pinnable in the harness this project tests the
DOM layer with, and the failure mode is a thrown error rather than a wrong
answer. Two better reasons follow the first:

- **An ancestor check cannot be a selector honestly.** `inert`, `hidden` and a
  closed `<details>` disable a whole SUBTREE. `[inert] *` expresses that only if
  the engine has descendant combinators, and it still misses the case where the
  scope root itself is inside an inert ancestor. A parent walk — five lines, and
  `Element` has no `parent` binding yet (§7) — is exact.
- **The predicate is per-element anyway.** `tab_index() < 0`, `[disabled]`,
  a 0×0 box: each is read off the element, and reading them off elements the
  walk already has in hand is cheaper than a second selector pass.

So: **the SELECTOR is the documented DEFINITION of what is tabbable, and the
implementation is a walk that implements it.** The doc comment carries the
selector, so a reader can compare std's answer with the literature's and with
what a browser does.

The order is the part usually got wrong, and it is worth writing into the doc
comment: **within the scope, Tab order is positive `tabindex` values first in
ascending order, then everything else in document order.** That is the HTML
spec's sequential focus navigation order restricted to a subtree, and it is why
`tabbable` answers a `List` in that order rather than `querySelectorAll`'s
document order.

The one predicate a walk still cannot answer with today's bindings is
`visibility: hidden`, which keeps its box — so `offset_width`/`offset_height`
cannot see it. That needs a computed style (§7), and the honest interim is the
doc sentence: *a `visibility: hidden` element is reported as tabbable and the
platform will refuse to focus it, so `focus_first` answers `false` and the
caller retries.* Which is exactly B271's contract, so nothing new is being
invented for it.

## 4. Containment without `inert`: a keydown wrap plus a `focusin` guard

Two mechanisms, and they answer two different questions.

**The wrap** answers "Tab pressed while focus is inside the scope". A
capture-phase `keydown` listener (on the window, so no handler inside the panel
can swallow it first) that fires only when the event's target is in the scope:
on Tab from the last tabbable it `prevent_default()`s and focuses the first; on
Shift+Tab from the first it focuses the last. Between the ends it does nothing
at all, and the platform moves focus. That is the whole of `Wrap`, and it is
what a MENU wants: focus cycles while it is open, a click outside dismisses it
through the pointerdown path kolt already has, and the rest of the page is
untouched — no `inert`, no attribute written anywhere outside the panel.

**The guard** answers "focus arrived somewhere it should not have" — Tab
reaching the scope from outside, a programmatic `focus()`, a click on a
background input, the browser's address bar cycling back into the document. A
capture-phase `focusin` listener that, when the target is outside, pulls focus
back. That is the whole of `Contain`, and it is what a MODAL wants.

Why the guard and not `inert`: the guard touches nothing outside the panel, so
the page stays pointer-live and stays in the accessibility tree, which is
A121's requirement stated three ways. Its honest cost is that focus visibly
lands on the background element for one event before being pulled back, where
`inert` would never let it land — assistive technology may announce that
element. `inert` is the better answer for a true modal and should be mentioned
in the doc comment as the app's own escape hatch (`set_attribute("inert", "")`
is one line and `remove_attribute` is its documented other half), with the
sentence that it is not what `Contain` does and why.

## 5. Nesting is a STACK, and the containment test is not `contains`

kolt's overlays are **portals**: `driver.attach(overlay, body)` is
`driver.container.child(when(overlay.open, ..))` (`overlay.vl:31-35`), so a
submenu opened from inside a menu's body mounts into the DRIVER'S CONTAINER, as
a *sibling* of its parent's panel. `parent_panel.contains(submenu_panel)` is
therefore **false**, and any containment test written on DOM ancestry yanks
focus out of a submenu the moment it opens.

That is exactly why kolt's driver already walks a LAYER STACK for pointer-downs
(`is_within_or_above`, `overlay.vl`) instead of asking the DOM. The focus scope
needs the same structure, for the same reason, and it should be std's rather
than every driver's:

- `focus_scope` pushes `(id, root, containment)` onto a module-level stack and
  pops it in `owner.defer` — so a scope's lifetime is its boundary's, by
  construction, and a per-open owner (which is what kolt's `attach` gives every
  overlay) makes it exactly one open.
- **The guard belongs to whichever `Contain` scope is TOPMOST at event time**,
  read from the stack in the handler rather than captured at registration. That
  is what makes a nested scope take over and hand back: every `Contain` scope
  registers a guard, and all but the topmost return immediately.
- **A focus is allowed if its target lies inside the topmost `Contain` scope's
  root, or inside the root of any scope ABOVE it** — which, by construction, are
  its own children. `within_or_above`, generalised from kolt's pointer version.

`probes/a121_focus_scope` implements that stack and its two helpers and builds;
the structure is `overlay.vl`'s, read for focus instead of for pointers.

## 6. Timing: the SHOW calls `focus_initial`, and that is B271's ruling

`focus_scope` **focuses nothing**. This is the decision that keeps the design
from re-opening a closed bug.

B271 (CLOSED Order 30) established the rule the hard way: `focus()` needs a
target that is connected, RENDERED and visible *at the call*, kolt's panel is
`visibility: hidden` until a `ResizeObserver` callback places it, and
`on_mount`'s microtask runs before the frame's rendering step — so the first
attempt always failed. `View::autofocus` was made frame-aware and bounded
(microtask, next frame, the frame after, stop), and its doc comment closes with
the sentence this design obeys:

> *"the formal shape for an overlay is that focus is a consequence of the SHOW —
> a hook the driver runs when it flips visibility, or `<dialog>.showModal()`,
> whose focusing steps run once the dialog is rendered — not a retry."*

kolt already writes it that way: its focus call is inside `relayout`, after
`set_style_property("visibility", "visible")`. So:

- **`focus_scope(root, containment)` installs the trap and the guard and
  returns a handle.** The trap has no timing requirement at all — a listener
  works whenever it is registered — so this can and should happen at mount.
- **`FocusScope::focus_initial()` takes the focus, and the driver calls it at
  the show.** Idempotent (latched in a `Shared<bool>`), and answering whether
  it took, so a driver whose show hook may fire before layout can call it again
  on the next `relayout` — which is what kolt's `focused` flag is already
  doing, one layer up.
- **`View::focus_scope(containment)` is the chained sugar** for the ordinary
  case with no show hook: install at mount, and take the initial focus on
  `autofocus`'s exact bounded clock (microtask, frame, frame, stop). It stands
  to `focus_scope` as `View::autofocus` stands to `View::on_mount` — the same
  relation, in the same file, so there is one pattern and not two.

`focus_initial`'s own order is: **the first `[autofocus]` descendant, else
`focus_first()`, else the root at `tabindex="-1"`.** The last rung is kolt's
own fallback made to work — a `tabindex="-1"` element is programmatically
focusable and *not* tabbable, which is precisely right for a panel with nothing
to focus, and it is what `panel_element.focus()` was trying to be (§1).

### 6.1 `autofocus`

`View::autofocus()` and a scope's `focus_initial` both want to focus something,
and today the scope cannot see the author's choice: `autofocus` calls `focus()`
and writes no attribute, so there is nothing to look for. Two consequences and
one change:

- **`View::autofocus()` should also set the `autofocus` attribute.** The HTML
  attribute is inert for a dynamically inserted element — that is *why* A45
  exists — so setting it costs nothing at runtime and makes the author's choice
  readable: to the scope, to devtools, and to a test that asserts markup. This
  also retires kolt's private `[x-autofocus]` convention onto the standard
  attribute.
- **Both mechanisms may then fire, and that is harmless.** `focus_initial`
  prefers the `[autofocus]` descendant, `autofocus`'s own retry focuses the same
  element, and focusing an already-focused element is a no-op. Neither has to
  know about the other, which is worth more than eliminating the redundancy.
- The doc sentence: *inside a focus scope, `autofocus` marks which element the
  scope should start on; outside one it focuses on its own bounded clock. It
  means the same thing in both places.*

## 7. What `std::dom` is missing — measured

`probes/a121_missing_bindings` declares four bindings in the shapes `std::dom`
already uses and reads what each EMITS (the whole 208-byte bundle):

```js
document.activeElement();                                   // ← WRONG: a call
__dom_active_element();                                     // ← needs a helper
console.log("tabIndex=" + root.tabIndex);                   // ← works, 1 line
console.log("visibility=" + __dom_computed_style(root, "visibility"));
```

| read | binding | cost |
|---|---|---|
| `Element::tab_index` | `[extern(get, "tabIndex")]` | **one line.** The DOM reflects the attribute here, defaulted per tag, which is exactly the predicate §3 wants |
| `Event::related_target` | `[extern(get, "relatedTarget")]` | **one line.** On a `focusout`, where focus WENT — the read that tells a scope "focus left me, and to there" |
| `document.activeElement` | needs a **runtime helper** `__dom_active_element` | `[extern("document.activeElement")]` emits `document.activeElement()`, a call to a property, exactly as `window()`'s doc comment predicts for a global property. The helper goes beside `__dom_window` / `__dom_bounding_rect` / `__dom_query_all` in `transformer.rs`'s `EXTERN_HELPERS` + `helper_source`, and in the interpreter's twin |
| a computed style | needs a **runtime helper** `__dom_computed_style` | same place. `getComputedStyle(el).getPropertyValue(name)` |
| `Element::parent` | `[extern(get, "parentElement")]` | **one line**, for §3's ancestor walk |

**And one read is available TODAY with no new binding:** `query_selector(":focus")`
— the module-level document query. `probes/a121_focus_scope` uses it for the
restore, and it emits `document.querySelector(":focus")`. It is not the same
thing as `activeElement` and the difference is worth knowing both ways: `:focus`
does not match when the DOCUMENT itself is not focused (another window has it)
and `activeElement` falls back to `<body>`. For *"is focus still mine?"* at
disposal, `:focus` is the better question. For *"where was focus before I
opened?"*, `activeElement` is — a scope opened by a keyboard shortcut while the
window was unfocused would remember nothing from `:focus`. So the helper is
worth adding, and the interim (S1 shipping on `:focus`) is correct for the
common case.

The restore, with both conditions, from the probe:

```vilan
owner.defer(|| {
	// pop the stack …
	if root.contains(query_selector(":focus")) && restore.is_connected() {
		restore.focus();
	}
});
```

Both guards matter. **Restore only if focus is still ours** — an app that moved
focus deliberately while the overlay was open keeps it. **Restore only if the
remembered element is still there** — the button that opened the overlay may
have been removed by the very action the overlay took, and focusing a detached
element sends focus to `<body>`, which is worse than leaving it.

## 8. What is untested, and what would test it

Named per the brief, because there is no browser on this host.

**Measured:**

- the whole surface compiles against today's `std::dom` / `std::ui` /
  `std::reactive`, in userland, for a browser target — `probes/a121_focus_scope`,
  9,610 bytes emitted, with the selector, both listeners, the stack and the
  restore in it;
- what each of the five bindings emits — `probes/a121_missing_bindings`;
- that the test harness's `querySelectorAll` matches tag names only and its
  `matches` throws for any selector but `":focus"` — read from
  `crates/vilan-cli/tests/support/dom/stub.js`, which is what §3's walk is
  argued from.

**NOT measured, all of it behaviour:**

1. that `focus()` on a `div` with no `tabindex` is a no-op (§1) — HTML spec's
   focusing steps;
2. that the keydown wrap actually keeps focus inside (§4);
3. that the `focusin` guard pulls focus back, and that it does so before
   assistive technology announces the background element (§4);
4. Tab order with positive `tabindex` values present (§3);
5. the `visibility: hidden` case (§3);
6. the restore, and its two guards (§7);
7. nesting: a submenu inside a menu, a menu inside a modal (§5);
8. `autofocus` and `focus_initial` not fighting (§6.1);
9. that a scrolled overflow container's off-screen-but-laid-out children are
   still tabbable (they are; the 0×0 test does not catch them, which is
   correct).

**What would test them: the shipped stub, with four additions**, and this is
the honest reason §3 chose a walk:

- `tabIndex`, read off the attribute with a per-tag default;
- `parentElement` (the stub has `parent` internally already);
- **`focus()` dispatching a `focusin` event** — today it sets
  `global.activeElement` and pushes to `focusLog` and dispatches nothing, so
  the containment guard cannot fire;
- `getComputedStyle`, table-driven like `global.boxes` is for A59.

With those, claims 2, 3, 4, 6, 7 and 8 are all pinnable in `ui_rows.rs`'s
existing harness — `dispatchEvent(input, "keydown", { key: "Tab", shiftKey: false })`
already works (`dispatchEvent` takes an `extra` object and fires window capture
listeners first, which is the phase §4 registers in). Claims 1, 5 and 9 need a
real engine and stay documented rather than pinned, which is the same place A45
and B271 left the iOS-Safari case.

## 9. Slices

### S1 — the query, and the scope (M)

`Element::tab_index` / `Element::parent` (§7's one-liners);
`Element::tabbable()` as §3's walk with the selector in its doc comment;
`Element::focus_first()`; `FocusContainment`; `focus_scope` with the stack,
the keydown wrap, the `focusin` guard and the `:focus`-based restore;
`FocusScope::focus_initial`; `View::focus_scope` on `autofocus`'s clock;
`View::autofocus` also setting the attribute (§6.1). The process twin
(`process/ui.vl`) gets `View::focus_scope` as a generic no-op, exactly as A45's
`on_mount`/`autofocus` did.

**Exit:** the four stub additions (§8) first, each with a pin of its own so a
harness change is not silently load-bearing; then one `ui_rows` case per §8
claim 2, 3, 4, 6, 7, 8, each asserting `activeElement` by name through the
stub's `focusLog`; a red-first pin for the `div`-with-no-tabindex fallback
(focus goes to the root only after `tabindex="-1"` is written — plant the
missing attribute and watch it go red); `guide/` fence showing the overlay
shape; the `autofocus`-attribute change's own pin, because it moves markup that
existing page-level assertions may read.

### S2 — the two helpers (S)

`__dom_active_element` and `__dom_computed_style` into
`transformer.rs`'s helper table and the interpreter's twin; `Element::parent`
already landed in S1; the restore re-based on `active_element()`; `tabbable`'s
`visibility: hidden` predicate.

**Exit:** the emission pinned (the helper's source is a `&'static str` and the
corpus is byte-compared, so the goldens move — regenerate after run
verification); a stub `getComputedStyle` and the `visibility: hidden` case as a
pin; the `activeElement`-vs-`:focus` difference stated in both doc comments.

### S3 — `Event::related_target` and a `focusout` path (S, deferred)

The `focusout` + `relatedTarget` route is the other way to detect focus
leaving, and it is better for one case the `focusin` guard handles awkwardly:
focus leaving the DOCUMENT entirely (to the browser chrome), where
`relatedTarget` is null and a guard should do nothing rather than pull focus
back into a page the user has left. Worth building when an exhibit complains;
`Contain`'s guard is correct without it, just noisier.

### S4 — kolt (not vilan's)

`overlay.vl:531-541` becomes, at the owner's word:

```vilan
let scope = focus_scope(panel_element, if overlay.modal {
	FocusContainment::Contain
} else {
	FocusContainment::Wrap
});
// …inside `relayout`, after the visibility flip:
let _took = scope.focus_initial();
```

The `focused: Shared<bool>` latch goes (the scope has one), the
`[x-autofocus]` query goes (the standard attribute, found by the scope), the
dead `panel_element.focus()` goes, and the FIXME goes. kolt's `Overlay` gains
one field to say which containment it wants, which is A121's "opt-in/opt-out"
at the place the app already configures everything else about an overlay.

Sizing: S1 M + S2 S + S3 S. S1 is the item; S2 is what makes two of its
predicates exact rather than documented.

## 10. Open questions, each with a recommendation

**Q1 — a selector or a walk?**

> **Rec: a WALK, with the selector as the documented definition (§3).** The
> shipped DOM stub matches tag names only and its `matches` throws, so a
> selector-driven query is unpinnable in the harness this project tests the DOM
> layer with; an ancestor check for `inert`/`hidden` is exact as a walk and
> approximate as a selector; and the predicates are per-element anyway. The
> alternative is one `query_selector_all` call and a real-browser-only test
> suite, which this project does not have.

**Q2 — `Contain` and `Wrap`, or one mode?**

> **Rec: TWO (§4), and the opt-OUT is not calling `focus_scope` at all.** A
> menu wants the wrap and not the guard — kolt says so in its FIXME's
> parenthetical — and a modal wants both. One mode would have to be the modal's,
> which would make every menu pull focus back from the page the menu deliberately
> leaves live. A third arm for "Tab out dismisses me" is not needed: under
> `Wrap` focus never leaves by Tab, and a click outside already dismisses
> through the pointerdown path.

**Q3 — where does the initial focus happen?**

> **Rec: the SHOW calls it; the scope never focuses by itself (§6).** This is
> B271's own closing sentence, and kolt already implements the show hook. The
> alternative — `focus_scope` focusing on `autofocus`'s bounded clock — is the
> `View::focus_scope` sugar, and it is offered for the ordinary case; making it
> the only door would re-open B271 for every overlay that becomes visible during
> layout, which is the only kind kolt has.

**Q4 — should `View::autofocus()` set the `autofocus` attribute?**

> **Rec: YES (§6.1).** The attribute is inert for a dynamically inserted
> element, so it costs nothing, and it is what makes the author's choice
> readable to a scope, to devtools and to a markup assertion. It retires kolt's
> `[x-autofocus]`. The cost is honest and needs its own pin: it moves emitted
> markup, and an existing page-level assertion may read it.

**Q5 — `inert` at all?**

> **Rec: NOT in `Contain`, and NAMED in the doc comment as the app's escape
> hatch.** A121 requires the page stay live, and `inert` also removes the
> subtree from the accessibility tree and blocks pointers — it is a "this does
> not exist" tool, not a focus tool. But it is genuinely the stronger answer for
> a true modal, `set_attribute`/`remove_attribute` are already the documented
> boolean-attribute pair, and a doc comment that pretends otherwise would be
> teaching the wrong thing. A `FocusContainment::Inert` arm is the alternative
> and is declined: it would make std decide that a dialog should be
> pointer-dead, which is the app's call.

**Q6 — does the scope stack live in std or in the driver?**

> **Rec: STD (§5).** The containment test cannot be DOM ancestry, because an
> overlay is a portal and a submenu is a sibling — so *something* must hold the
> nesting, and if std does not, then every driver writes kolt's
> `is_within_or_above` again, for focus, beside the one it already has for
> pointers. A module-level stack popped by `Owner::defer` is the same lifetime
> discipline the rest of `std::ui` uses. The alternative — `focus_scope` taking
> a parent scope as an argument — makes the caller thread the nesting it already
> expressed by where it called from.

One thing this paper has decided rather than asked, and will re-open if the
owner disagrees: **the trap is installed at mount and the focus is taken at the
show, as two separable acts** (§6) — which is what makes a scope usable by a
driver that owns its own visibility flip, and is why `FocusScope` is a value
rather than only a `View` method.

## 11. What this does not do

- **Arrow-key navigation.** A menu's Up/Down, a toolbar's Left/Right, a grid's
  two-dimensional walk: these are ROVING TABINDEX, a different mechanism
  (`tabindex="-1"` on every item and one `0`), and they belong to whatever
  builds the menu. `tabbable()` is the query they would be written over.
- **Focus rings.** `:focus-visible` is CSS and the app's.
- **`<dialog>` and `showModal()`.** The platform's own modal does most of this
  correctly, including the top layer and the backdrop, and it is the right
  answer for an app that wants a modal and nothing else. It is not the right
  answer for kolt's overlay system — one element per open, no positioning
  control, no submenu story — and B271 already records the shape. A `<dialog>`
  binding is worth its own item.
- **`aria-modal` / `role="dialog"` / the label.** The a11y attributes an
  overlay owes are the app's markup, not a focus mechanism, and std writing
  `role` for you is std guessing what the subtree is.
- **Focus on route change.** A router that moves focus to the new page's
  heading is `std::router`'s, and it wants `focus_first` — which is why
  `focus_first` is on `Element` and not private to the scope.
- **`Element::blur`.** Nothing here needs it; the restore focuses a new target
  rather than clearing.
