# `std::router` — history-API routing (backlog A10)

Status: **SETTLED 2026-07-11** (design reviewed in conversation; the decision
points below were resolved explicitly). Driven by the Kolt migration
(`kolt-migration.md` §2.3): nested layouts (`layout_main` / `layout_workspace`
are the target shapes), the `/w/ORG/WS/*` path scheme, a link component, and a
current-route signal composing with `show` / `bind_*`.

## 1. The model: routes are an enum, not pattern strings

Conventional routers (`@solidjs/router`, react-router) are built around
pattern strings — `<Route path="/w/:org/:ws">` — with params read back as
strings by name at runtime. That is the stringly-typed shape vilan exists to
avoid: a typo'd param name is a runtime `undefined`, a dead link is a 404
discovered by clicking, and the route tree is a registration DSL with its own
matching semantics.

In vilan, **the URL is just a wire format for a typed value**. An app declares
its route space as an enum (nested enums mirror nested layouts), and writes an
inverse pair of ordinary functions:

```vilan
[derive(PartialEq)]
enum Route {
    Home,
    Login,
    Workspace(str, WorkspaceRoute),   // /w/{org}/{...}
    NotFound,
}

[derive(PartialEq)]
enum WorkspaceRoute {
    Overview,          // /w/acme
    Tasks,             // /w/acme/tasks
    Task(i32),         // /w/acme/task/42
}

fun parse(path: str): Route { .. }    // segments() + match — total, returns NotFound
fun href(route: Route): str { .. }    // the inverse; links take Route VALUES
```

Everything downstream is language, not framework:

- **Nested layouts are nested functions.** `app(route)` matches the outer
  enum and hands `Workspace`'s payload to `workspace_layout(org, inner)`,
  which matches the inner enum. No route-tree registration, no outlet
  indirection, no context lookup for params — the payload IS the param,
  already typed.
- **Guards are `if`s.** An auth gate is a branch in the match, not a
  framework hook.
- **Dead links don't compile.** `link` takes a route value; the printed path
  goes through `href`, so every link is derivable from the enum.

The `parse`/`href` pair is deliberately hand-written in v1: it is small
(one arm per route), totally testable, and keeps the router out of the
business of pattern semantics. A `[derive(Route)]` generating the pair from
path attributes is recorded below as later sugar, adopted only if real apps
show the boilerplate is worth killing.

## 2. The std surface

Deliberately thin — three pieces.

### 2.1 `std::router` (browser layer)

```vilan
fun current_path(): Signal<str>    // location.pathname, live across pushState + popstate
fun navigate(path: str)            // history.pushState + signal update
fun segments(path: str): List<str> // "/w/acme/tasks" → ["w", "acme", "tasks"]

trait Routable {
    fun to_path(self): str         // implemented by the app's route enum (usually = href)
}

fun link<R: Routable>(label: str, route: R): View
```

- The path signal is a module-level singleton (the `std::reactive` pattern:
  `turn_scope`, `next_subscriber_id`), lazily wired on first use:
  initialization reads `location.pathname` and subscribes `popstate`, so
  back/forward buttons drive the same signal as `navigate`.
- Both the popstate handler and `navigate` settle like any other reactive
  boundary: popstate dispatches inside a fresh turn (the DOM-event cadence,
  exactly as `View.on` does); `navigate` joins the caller's ambient turn when
  called from a handler.
- `link(label, route)` renders a real `<a href=..>` — the href comes from
  `to_path`, so middle-click / ctrl-click / copy-link keep native anchor
  behavior — and intercepts only PLAIN left-clicks (no modifier keys, main
  button) with `prevent_default` + `navigate`. It returns a `View`, so the
  usual chaining applies (`link(..).styled(nav_item)`).
- The app derives its typed route signal itself: `current_path().map(parse)`.

### 2.2 `View.swap` (in `std::ui`) — the dynamic-subtree primitive

Routing's rendering half is a GENERAL primitive, not a router feature
(decision: general `swap`, routing is just its first customer):

```vilan
fun swap<T: PartialEq>(self, source: Signal<T>, render: (|T| View) context owner_scope): View
```

The value-generalized `when`: whenever `source`'s value CHANGES, the previous
subtree's owner is disposed and its element removed, and `render` runs under a
fresh owner (the same disposal-boundary discipline as a `bind_each` row —
proposal/ambient-owner.md §4). `T: PartialEq` makes an equal value a no-op:
navigating to the current route re-renders nothing. The route match lives in
the render closure:

```vilan
view("main").swap(route, |current| match current {
    Route::Home => home_page(),
    Route::Login => login_page(),
    Route::Workspace(let org, let inner) => workspace_layout(org, inner),
    Route::NotFound => not_found_page(),
})
```

### 2.3 `Event` + `View.on_event` (in `std::dom` / `std::ui`)

`link`'s click interception needs the DOM event — machinery `std::ui` lacked
(handlers were `|| void`). Rather than a router-private helper, the general
form: `external struct Event` with `prevent_default()` and the modifier/button
getters, `Element.on_event` binding the same `addEventListener` with an
event-taking handler, and `View.on_event(name, handler)` wrapping dispatch in
a turn exactly as `View.on` does. Generally useful (keyboard handling is the
obvious next customer).

## 3. Decisions (resolved 2026-07-11)

1. **Enum routes** over pattern strings (no pattern escape hatch in v1).
2. **`link(label, route)`** takes the route value via the `Routable` bound.
3. **General `swap(signal, render)`** rather than a route-specific
   `route_view`.
4. **Query strings and hash: deferred.** `current_path()` is `pathname` only.
   When query support lands it should stay in the typed-value model (a
   `Route` payload, not a stringly side-channel).

## 4. Deferred / recorded

- **`[derive(Route)]`** — generate `parse`/`href` from per-variant path
  attributes once the hand-written pair proves annoying in practice.
- **Query strings + hash** (decision 4).
- **Scroll restoration** — browser-default for now; a `navigate` option
  later.
- **SSR / base-layer lift** — `segments` and an app's `parse`/`href` are pure
  string logic; if server-side rendering arrives, the pure parts move to a
  platform-neutral layer so the server can route too. Until then the router
  is browser-only and a `@process` import of `std::router` is the platform
  error it should be.
- **Route-change effects** (title, analytics) — plain `effect` on the route
  signal already covers this; no API needed.

## 5. The event surface, widened (A27, kolt.local 037) — 2026-08-31

**Why this paper.** §2.3 is where the DOM event surface was designed: `Event`
and `Element.on_event` exist because `link` needed them and the ruling was
"rather than a router-private helper, the general form". The same paper
carries the *other* half of the same decision — `router.vl:29`'s
`window_listen`, which is a router-private helper, the one §2.3 declined to
write for elements and then wrote for the window anyway. A27 names it as one
of three independent hand-rolls of `window.addEventListener`, and `canvas.md`
§4 already asks for it by name ("the same shape `router.vl:29`'s
`window_listen` already is, just not currently exported outside routing").
So the widening belongs beside §2.3, not in `element-syntax.md` (which owns
the *spelling* of attachment — `on:click` lowering to `.on`/`.on_event` — and
gains every new `View` method for free, by its own name-blind rule) and not in
`fullstack-dx.md` (the app/server seam). `std-surface.md` is the base-layer
audit and holds no browser module at all.

The live exhibit is kolt's sidebar-resize drag (`kolt/src/views.vl`,
`View.on_drag`): a working handler that had to hand-roll three things std does
not have. The owner is explicitly **not** asking for a drag surface — the item
is the capabilities, and a drag is simply the case that needs all three at
once, because the pointer leaves the element mid-drag and element-local
`on_event` cannot follow it.

### 5.1 `window` is a listen TARGET, not a suffix

A27 sketched `on_window`. Taken as written it grows a parallel vocabulary —
`on_window`, `on_window_event`, and then a `listen_window` beside `listen` —
where the only difference from the element forms is *which object* is being
listened to. That is a target, and vilan already spells targets as handles:
`Element` is an opaque handle over a real DOM object, and every verb hangs off
it.

So: `external struct Window`, `fun window(): Window`, and the **same three
verbs on both targets** — `on`, `on_event`, `listen`. `window().on_event("resize", ..)`
reads as what it is, and the surface never has to answer "why is it
`on_window_event` but `on_event`".

`window` is a global property with no function form, so it is acquired through
a one-line runtime helper (`__dom_window`) — exactly the precedent
`location.pathname` set at `router.vl:26` and for exactly the stated reason.
(`[extern(get, ..)]` is the property form and needs a receiver, so a zero-arg
free function cannot use it; a new binding form for "a bare global as an
expression" is the alternative, and it is a language change this does not
need.) The visible cost is the emission: `window.addEventListener(..)` becomes
`__dom_window().addEventListener(..)` plus a three-line helper once per bundle.
`router.vl`'s fold onto the new verbs is what makes that concrete — the split
fixture's golden moves by exactly those two things and nothing else, every
chunk byte-identical — and it is the price of the handle, not of the fold: the
same indirection appears wherever `window()` is called.

The handle also gives the *next* asks a place to land. `canvas.md` §4 wants a
window `resize` listener and, for DPR, `innerWidth`/`devicePixelRatio`; those
are `Window` accessors, where the free-function shape would have made them
three more free functions. Nothing beyond the listen verbs ships now — an
accessor with no caller is the dead surface A27's own trap warns about.

**Raw means raw.** `std::dom` handlers do not establish a turn — the docs
already say so of `element.on` ("that's `View.on`'s job"), and the window
verbs are consistent with it: `ensure_wired` keeps its explicit
`turn(FlushPolicy::AtSuspension, ..)` wrapper after folding onto the new
surface, and so must any caller that writes signals from a window event. A
turn-establishing window listener at the `std::ui` layer — the `View.on`
treatment for a target that is not a view — is **recorded, not built** (5.5).

### 5.2 Removal is a `Subscription`, and it is a new verb

`on_event`'s signature does not change. It is the chaining form, it is what
`on:click` lowers to, and it is fire-and-forget by design: the listener dies
with the element, which for an element is the right and free answer.

For the window there is no element to die, so removal has to be expressible,
and the vocabulary already exists: `Source::sub` hands back a `Subscription`
whose `dispose` unhooks it. The registration verb is therefore **`listen`**,
`[must_use]` exactly as `sub` is, on both targets:

```vilan,ignore
fun listen(self, event: str, handler: |Event| void): Subscription
```

Two tiers, one rule: **`on`/`on_event` are fire-and-forget; `listen` is the
removable form.** That is why `listen` is a new verb rather than a changed
return type on `on_event` — `on_event` returning a `[must_use]` handle would
make every existing zero-ceremony call site a warning, and `View.on_event`'s
chaining return (`View`) has no room for it at all.

`Subscription` gains the constructor this needs:
`Subscription::teardown(release)` — a subscription over no signal, whose
`dispose` runs the hook once and nothing else. It is not dom-specific: it is
the registration shape for any source outside the signal graph, and it reuses
the one-shot `release` cell that `RemoteSource::sub`'s lease decrement already
rides, so a double `dispose` (an owner releasing a handle the app already
disposed by hand — precisely the drag's case) cannot unhook twice.

**Ownership stays the caller's, as `sub`'s does.** `listen` does not register
with the ambient owner. `sub` doesn't either — `effect` is the owner-tied
twin — and the asymmetry is deliberate here: a drag arms two window listeners
per `pointerdown`, so auto-registration would push two dead cleanups onto the
enclosing boundary's owner on every drag, forever (the A28 shape, from the
other end). The idiom is explicit and one line:
`get_owner().take(window().listen(..))`. An owner-tied twin is recorded (5.5).

**`removeEventListener` is `listen`'s teardown, and it is identity-matched** —
the handler value passed to remove must be the same object the host was handed.
Probed against the real emitter before building: a closure bound to a `let`,
passed to a std function, used once as an argument and once captured by the
returned teardown closure, emits as a single JS `const` referenced twice. No
clone, no wrapper. The `off_event` twin is bound and documented, but `listen`
exists so that nobody has to hold the pairing right.

**`retains` marks registration only.** `addEventListener` retains (the host
stores a vilan closure and calls it later — the `lifetimes.md` §S4 audit's own
sentence); `removeEventListener` does not keep anything past the call, so it is
left unmarked. kolt's hand-roll marks both; that is over-marking, the same
error the audit's `appendChild` golden caught, and this surface does not
inherit it.

### 5.3 Pointer coordinates: `pointer_x` / `pointer_y`, and nothing else yet

`Event` gains two accessors, over `clientX` / `clientY`.

The mechanical transliteration would be `client_x`/`client_y`, and it would be
a worse name in vilan than it is in the DOM: "client" means *viewport* for
reasons that are pure history, and the surface would be teaching that history
to every reader forever. `pointer_x`/`pointer_y` say where the pointer is.
kolt already spells it that way, which makes the exhibit's `impl Event` block
delete with zero call-site churn.

The family objection is real and answered: if `pageX` lands later its vilan
name is `page_x` — *where the pointer is in the document* — which is
self-explanatory on its own terms rather than as the second row of a
coordinate-space table. Two good names beat four uniform ones.

**page / offset / screen variants wait.** Nothing in std or in the exhibit
reads them, and A27's recorded trap is exactly this: an accessor no delivered
event has a caller for is dead surface. They land with a caller.

`pointerId`, `buttons`, and the rest of `PointerEvent` wait for the same
reason — and `pointerId` in particular waits *with* 5.4.

### 5.4 `setPointerCapture` — designed alongside, not built

037 names it as "the honest alternative to window listeners for drags", and it
is: `element.setPointerCapture(event.pointerId)` retargets every subsequent
pointer event to the capturing element until release, so the pointer leaving
the element stops mattering and a drag needs no window listener at all.

It is recorded rather than built, on three grounds. It is not a substitute for
the window surface — `resize`, `popstate`, `storage`, `message` and `keydown`
still have no element to hang on, and A27's gap is those, not drags. It is a
*pair* of methods plus `pointerId` plus the `lostpointercapture` event, i.e.
its own surface with its own disposal question (what releases capture if the
element is unmounted mid-drag?), which is a proposal, not a slice tail. And
the exhibit does not need it: kolt's drag works today on window listeners, so
building capture now would be building the alternative to the thing that is
actually asked for, before the thing itself has shipped.

The recommendation for when it is taken up: a capture handle that is
`Disposable`, so release rides the same vocabulary `listen` just established,
rather than a bare `release_pointer_capture` twin.

### 5.5 Recorded, not built

- **A turn-establishing window listener at the `std::ui` layer** (5.1) — the
  `View.on` treatment for a non-view target. Every current caller wraps by
  hand; when a second one appears, the wrapper belongs in std.
- **An owner-tied `listen` twin** (5.2), `effect`'s shape for listeners —
  wanted the moment a component registers a window listener for its whole
  lifetime. Blocked on nothing but a caller.
- **`Window` accessors** — `inner_width`/`inner_height`,
  `device_pixel_ratio` (`canvas.md` §4's DPR path). Land with the resize
  consumer.
- **`page_x`/`page_y`, `screen_*`, `offset_*`, `pointerId`, `buttons`** (5.3).
- **`setPointerCapture`** (5.4).
- **A typed `message` event `data`** — A27's stated bindgen-shaped question.
  The window surface delivers the event; giving `Event` an `origin()` or a
  typed `data` is `bindgen.md`'s problem, and A27 is explicit that adding
  `origin()` alone would have been dead surface. It is no longer dead once
  something delivers a `message` — but the typing is still bindgen's call.

### 5.6 Acceptance

The surface is right if the exhibit rewrites onto it *alone*: kolt's
`View.on_drag` keeping its own arithmetic and its own closure triple, with the
`impl Event { pointer_x, pointer_y }` block and both
`window_add_event_listener`/`window_remove_event_listener` externs **deleted**,
and the `mut dispose` closure becoming two `Subscription::dispose` calls. That
rewrite is a probe against the built compiler, and its essence is a pin.
