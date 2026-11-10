# Native UI: a graphics API, a UI framework on it, and components on that

Status: DRAFT rev 2 for discussion, 2026-11-10. Nothing here is ruled. Rev 2
folds in the spike's measurements (section 11) and corrects what the spike
found wrong in rev 1. It answers the
owner's direction of 2026-11-10 (native-objective.md, "Owner direction") and
replaces chunks 8 and 9 of that plan once ruled. Every recommendation is a
proposal; section 9 lists the decisions in the order I would ask them.

Working names, to be ruled (Q1): `std::gfx` for the graphics API, `std::ui` for
the framework, `std::ui::kit` for the components. The existing web UI
(`View`, the element syntax's HTML tags, `std::web::style`) is called "the web
UI" below and is not changed by this paper.

## 0. The direction this paper is held to

From the owner, 2026-11-10:

1. No HTML and no CSS for native GPU rendering. Not through a translation
   layer either. Distill what they do into an efficient UI system.
2. HTML does two jobs: structure, and default components. The successor does
   structure only. No styled defaults.
3. The model: a graphics API that takes full advantage of the GPU, a standard
   2D UI framework on top, and buttons, inputs and forms built on the framework.
4. GPUI is an inspiration. Vilan's own ideas stay, the display pixel first.
5. It lands in parts. Desktop first. The browser target follows and is not a
   requirement of the first version, but the graphics API must not rule it out.

## 1. The answer up front

Three layers, each usable without the one above it.

| Layer | What it is | Written in | Size |
|---|---|---|---|
| `std::gfx` | A window, a frame, and a small set of GPU primitives: rounded rectangle, shadow, text run, image, path, clip, transform | Rust runtime crate, a thin Vilan surface | L |
| `std::ui` | Elements, layout, style as typed values, hit testing, focus, events, scrolling, bound to Vilan's signals | Vilan, over a Rust layout solver | XL |
| `std::ui::kit` | Button, text input, checkbox, list, scroll area and so on, with behaviour and no look | Vilan only | M, then ongoing |

The four positions I recommend:

- **Our own primitive renderer on `wgpu`, not a general vector renderer.**
  A UI is almost entirely rounded rectangles, text and images. Those draw as
  instanced quads with the shape computed in the fragment shader. That is what
  GPUI does, it is a few hundred lines of shader, and it runs on every backend
  `wgpu` has, WebGPU included. The spike built it: two draw calls per scene.
- **Fine-grained updates from signals, not a re-render per frame.** GPUI
  rebuilds the whole window's element tree on every drawn frame (a view opts
  into caching). Vilan already
  has a fine-grained reactive core. An element's property is bound to a signal;
  a write marks that one element for layout or for paint, and nothing else
  runs. This is Vilan's main advantage over the systems it borrows from.
- **Style is a typed value, with no cascade, no selectors, no inheritance by
  default.** What CSS does with selectors, a Vilan program does with functions
  and values. State conditions (hovered, pressed, focused, window width) stay,
  as typed conditions on the style, resolved by the framework from hit testing
  and window state.
- **One length unit: the display pixel.** Section 5.

## 2. What exists today that this builds on

- **The native backend.** A Vilan program compiles to Rust and links runtime
  crates by use (`vilan-rt-sqlite`, `vilan-rt-poll`, `vilan-rt-webview`). The
  UI framework written in Vilan therefore compiles to Rust and links the
  renderer directly. There is no foreign-function boundary on the hot path and
  no interpreter anywhere in it.
- **M2's window work.** `std::window` (slice 1 landed 2026-11-10) already
  settled the threading question for a window beside the executor, the
  outside-the-workspace crate with its own lockfile and CI job, and the
  graceful stop when the last window closes. The GPU crate reuses the crate
  arrangement. The threading is revisited in Q8.
- **The reactive core.** Signals, cells, derived values, `each` keyed lists and
  the lens are backend-neutral and already run natively.
- **The typed style builder and `dp`.** `std::web::style` already expresses
  style as typed method calls with computed lengths and typed colours. Its
  output is CSS text, so it cannot be reused as is, but its vocabulary and its
  `dp` rule are the starting point for the native style type.
- **The element syntax.** `<div .styled(s)>` lowers to `view("div")` plus a
  chain of method calls. The syntax itself is not HTML. Q6 asks whether the
  native framework reuses it with its own element names.
- **`std::canvas`.** A typed immediate-mode 2D context over the browser canvas.
  It is a different thing (a browser API binding) and stays as it is.

## 3. Layer 1: `std::gfx`

### 3.1 What it offers

A program asks for a window, and on each frame it is handed a scene to fill.

```vilan
// Sketch only. Names and shapes are for discussion.
let window = gfx::Window::builder().title("Demo").size(dp(800), dp(600)).open()?;

window.on_frame(|scene: Scene| {
	scene.rect(Rect::new(dp(16), dp(16), dp(200), dp(48)))
		.fill(Color::gray(100))
		.radius(dp(8))
		.border(dp(1), Color::gray(300));
	scene.text("Hello", font, Point::new(dp(32), dp(28)), Color::gray(900));
});
```

The primitive set, complete for a first version:

| Primitive | Notes |
|---|---|
| Rectangle | Per-corner radius, fill (solid or linear gradient), border with per-side width |
| Shadow | Blurred rounded rectangle, computed in the shader, no offscreen pass |
| Text run | Shaped glyphs from an atlas; subpixel positioning; colour glyphs (emoji) as images |
| Image | A texture with a rounded clip; decoded by the existing `std::image` |
| Path | Filled or stroked vector path. Later slice: icons need it, layout does not |
| Clip | Rectangular, with radius. Scrolling and overflow are built on it |
| Transform | Translate and scale first; rotation later |
| Layer | A subtree drawn with opacity, and the unit of caching for scrolling |

A frame is drawn on demand. Nothing is drawn while nothing changes, so an idle
window costs no CPU and no GPU time. An animation asks for the next frame.

### 3.2 How it draws

The scene is a list of primitives in paint order. The renderer sorts it into
batches by primitive kind while keeping the order where primitives overlap,
uploads one instance buffer per batch and issues one draw call per batch. A
rectangle's corners, border and anti-aliasing come from a signed-distance
function in the fragment shader, so a rounded, bordered rectangle is one quad.
Text is quads sampling a glyph atlas.

This is GPUI's design in outline, checked against the Zed source by the spike
(2026-11-10). One decision is open here (Q14): sorting by kind inside a layer
is wrong when a later rectangle overlaps earlier text in the same layer. GPUI
orders by an overlap test over bounds, then merges by order and kind. The
alternative is strict layers, where the framework opens a layer for every
overlapping subtree. The primitive list also needs an underline.

### 3.3 The recommendation and what I rejected

- **Recommended: `winit` for windows and input, `wgpu` for the GPU, our own
  batch renderer.** `wgpu` gives Vulkan, Metal, DirectX 12, OpenGL as a
  fallback, and WebGPU and WebGL2 in a browser, behind one API. That is the
  cross-system abstraction the owner named as the biggest hurdle, already built
  and maintained by others. We write the part that is specific to a UI.
- **Rejected for the first version: `vello`.** It is a general vector
  renderer that does its work in compute shaders. It is better than a quad
  renderer at large filled paths, which a UI rarely has. It is not yet at 1.0,
  it requires compute shader support (so no WebGL2 fallback), and it is a far
  larger thing to depend on and to debug. If paths turn out to matter more
  than I expect, it can be added behind the Path primitive later without
  changing the API above.
- **Rejected: direct platform APIs.** GPUI writes Metal for macOS and
  Direct3D 11 for Windows by hand, and now uses `wgpu` itself for Linux and
  the web (its earlier Vulkan renderer was removed). That is the strongest
  outside evidence for `wgpu`, and hand-written renderers per system are more
  than we can maintain.
- **Rejected: Skia.** A large C++ dependency with a difficult build. It would
  put a C++ toolchain into every user's desktop build.

### 3.4 Text

Text is the largest single risk in this layer. Shaping, line breaking,
bidirectional text, font fallback and emoji are each deep. We do not write
them. Two candidate stacks, both pure Rust:

- `parley` (shaping and paragraph layout) with `swash` for rasterising.
- `cosmic-text` (shaping, layout, fallback, and an editor model).

The spike measured both (section 11). Recommendation: `parley`. It shaped
ordinary text about twice as fast and text needing a fallback font 30 to 170
times as fast, it avoids an unmaintained dependency, and it ships an editing
model. Against it: 19 more packages, a build-time link to libfontconfig on
Linux unless a feature is switched, and an API still changing shape.

A third option the spike raised (Q15): use each system's own text engine, as
GPUI does on macOS (CoreText) and Windows (DirectWrite). That gives native
font fallback and rendering, at the price of three text back ends. I
recommend one Rust stack first, with the interface kept small enough to put a
platform engine behind it later.

Text decisions still to make, none urgent: subpixel positioning bins, gamma
correction, and LCD subpixel text. I recommend no LCD subpixel text: it needs
a blending mode WebGL2 lacks.

## 4. Layer 2: `std::ui`

### 4.1 Structure without default components

Five element kinds carry every layout. None of them has a look.

| Element | Role |
|---|---|
| `row`, `column` | Children in a line, with gap, alignment, wrap |
| `stack` | Children on top of one another, each anchored to an edge or centre |
| `text` | A paragraph of styled runs |
| `image` | A picture with a fit rule |
| `scroll` | A clipped viewport over a larger child |

Everything else, a button included, is a function that returns these.

```vilan
// Sketch only.
fun counter(): Element {
	let count = Signal::new(0);
	<column gap(dp(8)) padding(dp(16))>
		<text>{count.derive(|n| "Count: " + format(n))}</text>
		{kit::button("Add one", || count.update(|n| n + 1))}
	</column>
}
```

### 4.2 Layout

Recommended: flexbox semantics for `row` and `column`, solved by `taffy`
(the Rust solver GPUI and Dioxus use), under our own vocabulary. The user
writes `gap`, `padding`, `grow`, `align`, `min_width`; they never write a CSS
property name and `taffy` is not visible in the surface. Grid is a later slice
on the same solver.

One opinion to rule on (Q5): no margins. Space between siblings is the
parent's `gap`; space inside is `padding`. Margins are the main source of
layout surprises in CSS (collapsing, negative values, auto), and gap plus
padding covers what they are used for.

### 4.3 Style

A style is a struct of typed, optional fields: background, border, radius,
shadow, opacity, text style, cursor. It is a value. Composition is `+`, as in
the web style builder today. There are no selectors and no cascade.

Inheritance exists for text style only (font, size, colour, line height),
because setting a font on every `text` is not reasonable. It flows down the
element tree as a context value, the way GPUI does it.

Conditions are typed and closed, carried over from the web builder's condition
sets (A95) in vocabulary but not in mechanism:

```vilan
let button_look = style()
	.background(Color::blue(600))
	.radius(dp(6))
	.when(hovered(), |s| s.background(Color::blue(700)))
	.when(pressed(), |s| s.background(Color::blue(800)))
	.when(focused(), |s| s.outline(dp(2), Color::blue(300)));
```

`hovered` and `pressed` come from hit testing, `focused` from the focus
system, width conditions from the window. A condition change repaints the one
element.

### 4.4 Updates

The element tree is retained. Each element property is either a constant or
bound to a signal. A signal write marks the bound element dirty for layout or
for paint only. A frame then:

1. Re-solves layout for dirty subtrees.
2. Rebuilds the scene for layers containing a dirty element.
3. Draws.

Keyed lists reuse `each`. A list of 10,000 rows that changes one row touches
one element. List virtualisation (only laying out visible rows) is a `kit`
component on `scroll`, not a framework feature.

### 4.5 Input, focus, events

Hit testing walks the laid-out tree back to front. Events (pointer, key, text,
scroll) are delivered to the hit element and bubble to ancestors that listen.
Focus is a framework concept with tab order from tree order and an explicit
override. The existing `focus-scope.md` proposal is an input here.

### 4.6 Accessibility

HTML gives semantics for free and we are giving that up, so it has to be
designed in rather than added. Each element carries an optional role and label
from the first version (button, text field, list, heading). The first version
does not publish them to the operating system. A later slice does, through
`accesskit`, without changing component code. I recommend ruling the role
field into the first version even though nothing reads it yet.

## 5. The display pixel

Today `dp(8)` is "the 8 of a design measured in pixels", and the property
decides what it becomes: spacing and sizing scale with the reader's text size,
border widths do not. That rule carries over unchanged and becomes simpler,
because there is no rem or px underneath it:

- `dp` is the only length unit in `std::gfx` and `std::ui`.
- One `dp` is one logical pixel times the display's scale factor, and for
  spacing, sizing and text also times the user's text scale setting.
- A border or hairline of `dp(1)` is never thinner than one device pixel and
  is snapped to the device pixel grid, so it stays sharp at 125% and 150%.
  The spike confirmed one opaque device pixel at 100% and 125%. At 150% the
  rule must choose between 1 and 2 device pixels (Q16). I recommend rounding
  down for widths under 2 dp, so a hairline stays a hairline.
- Fractions (`fraction(1, 2)`, percent of parent) and `auto` remain. `em`,
  `vh` and the rest do not exist.

## 6. Where the code lives

| Piece | Location | Language |
|---|---|---|
| Window, events, GPU device, renderer, shaders, glyph atlas | `crates/vilan-rt-gfx`, outside the workspace like the webview crate, own lockfile and CI job | Rust |
| Text shaping and layout | Same crate, behind a small interface | Rust (dependency) |
| Layout solver | Same crate | Rust (`taffy`) |
| `std::gfx` surface | `vilan/std/src/gfx.vl` | Vilan externs |
| Element tree, style, conditions, focus, events, reactive binding | `vilan/std/src/ui/` | Vilan |
| Components | `vilan/std/src/ui/kit/` | Vilan |

The spike's probe found the webview crate's reasons do not apply here: every
licence is on the compiler's accepted list and the audit passes. The remaining
reasons to keep it outside are weight (about 330 packages against the
compiler's 191) and `parley`'s libfontconfig build dependency. Q11 is
therefore a real choice now, not a forced one.

Platform fencing follows D4: these modules are native-only until the browser
part lands, and the JavaScript build refuses them by name, as `std::window`
does today.

## 7. The browser, later

Not in the first version. The design keeps three doors open:

- `wgpu` runs on WebGPU and WebGL2, so the renderer is the same code.
- The native backend emits Rust. Compiling that Rust to `wasm32` puts the
  framework and the app in WebAssembly, drawing to a canvas. That answers the
  worry about JavaScript on the hot path: there would be none. It needs a
  wasm variant of the runtime (executor, timers, fetch), which is real work
  and its own paper.
- The cost of a canvas-only page is known and not small: text selection, find
  in page, input methods, screen readers and browser extensions all stop
  working unless rebuilt. The web UI that exists today remains the right tool
  for document-like pages. I would not plan to retire it.

So "one source for native and web" (the old D3) becomes, under this paper: the
native UI can also run in a browser through wasm, and the web UI stays for
pages. Whether a single component source should target both systems is a
question I recommend leaving open until the native one exists.

## 8. The parts, and the spike

Out of the first version, by name (D7 carried over): text editing beyond a
single-line input, input methods, publishing accessibility to the system,
multiple windows, rotation, grid layout, the browser.

| Part | Delivers | Exit test |
|---|---|---|
| P0 spike | Dependency probe; a window; rectangles, text; a hand-laid-out counter | Below |
| P1 `std::gfx` | The primitive set less Path; on-demand frames; image golden tests | A scene renders identically to its golden image offscreen |
| P2 layout and elements | `row`, `column`, `stack`, `text`, `image`; style values | A fixed screen lays out to recorded rectangles |
| P3 interaction | Hit testing, conditions, focus, events, `scroll`; signal binding | The counter and a 10,000-row list, with frame times recorded |
| P4 `kit` | Button, single-line input, checkbox, virtual list | A todo app with the look supplied by the app |
| P5 | Path and icons; text editing; accessibility publishing | Each its own slice |
| P6 | The browser through wasm | Its own paper |

The spike is throwaway code in a lane worktree, the way the lens lab was. It
answers measured questions and nothing else:

1. Dependency probe of `winit` + `wgpu` + each text stack: package count,
   advisories, licences, clean build time.
2. A window with rounded rectangles and text, drawn on demand. Idle CPU.
3. A counter bound to a signal, laid out by `taffy`. Release binary size, cold
   start time, resident memory.
4. A scrolling list of 10,000 rows. Frame time while scrolling.

On this machine there is no display, but a software Vulkan driver (lavapipe)
is installed, so the spike can render offscreen to an image and under xvfb.
Frame times from a software driver are not meaningful. Real numbers need a
run on Windows with the GPU, which I would ask the owner to do with a built
binary.

## 9. Decisions, in the order I would ask them

| # | Question | Recommendation |
|---|---|---|
| Q1 | Names: `std::gfx`, `std::ui`, `std::ui::kit` | As written; the web UI keeps its names |
| Q2 | Renderer: own batch renderer on `wgpu`, or `vello`, or platform APIs | Own renderer on `wgpu` |
| Q3 | Text stack: `parley` or `cosmic-text` | `parley` (measured, section 11) |
| Q4 | Layout: `taffy` under our own vocabulary, flex first, grid later | Yes |
| Q5 | No margins: gap and padding only | Yes |
| Q6 | Reuse the element syntax (`<row gap(..)>`) with framework element names | Yes. It needs a compiler change of roughly 80 to 200 lines: the lowering hard-codes `std::web::ui::view(tag)`, four method names, and string-keyed attributes |
| Q7 | Style: typed values, no cascade, text style inherited by context only | Yes |
| Q8 | Threading: does the Vilan program run on the main thread driven by the window loop, or on a second thread as in M2 | Main thread. It needs an executor slice first (section 11.4); the second-thread arrangement works today and is the fallback |
| Q9 | Updates: retained tree with signal-bound properties, not a per-frame rebuild | Yes |
| Q10 | Accessibility role and label fields in the first version, published later | Yes |
| Q11 | The crate outside the workspace with its own lockfile and CI job | Outside, for weight and the fontconfig build dependency; no longer forced by licences or audit |
| Q12 | The web UI stays; one-source-for-both is left open | Yes |
| Q13 | Start the spike now, before the rest is ruled | DONE 2026-11-10 (owner: "Start the spike"); section 11 |
| Q14 | Paint order: strict layers, or an overlap test over bounds as GPUI does | Overlap test; it keeps batches large without making the user think about layers |
| Q15 | One Rust text stack, or each system's own text engine | One Rust stack first, behind a small interface |
| Q16 | `dp(1)` at 150%: one device pixel or two | One, for widths under 2 dp |

## 10. What I am least sure of

- **Text.** Both stacks are young. Complex scripts and font fallback on three
  operating systems may be where most of the time goes.
- **Q8.** Driving the executor from the window loop touches the readiness loop
  that F160 just rebuilt. The second-thread arrangement is proven by M2 and is
  the fallback.
- **The element syntax (Q6).** I have read that it lowers to `view("div")` and
  method chains. I have not checked how much of the analyzer assumes `View`.
- **Software rendering in CI.** The spike found Vulkan and GL software
  drivers differ by 1 in a handful of channel values. A tolerance of 1 covers
  it.
- **Everything not run on a real GPU or on Windows and macOS.** Section 11.6.

## 11. Spike results (lane gfx-spike, 2026-11-10)

Throwaway code on branch `gfx-spike` (a9c64577, not pushed, not for merge), in
`spike/gfx/` of that worktree with its images and logs under `out/`. Every GPU
time below is from a software driver and says nothing about a real GPU.

### 11.1 What ran

- `wgpu` found an adapter on this machine through software Vulkan and GL.
- Rounded rectangles with per-corner radii and borders, an analytic blurred
  shadow, and atlas text render correctly offscreen at 100%, 125% and 150%. I
  looked at the images.
- A real window ran under xvfb, driven by clicks injected through the X
  server. It drew one frame at start, one per click that changed the counter,
  and none for a click that missed. Idle CPU over 10 s was zero.
- The Windows binary type-checks here but cannot be linked here.

### 11.2 Dependencies

Pinned: `winit =0.30.13`, `wgpu =30.0.1`, `taffy =0.15.1`, `parley =0.12.0`,
`swash =0.2.10`, `cosmic-text =0.19.0`.

| Set | Packages | Clean debug | Clean release |
|---|---|---|---|
| `winit` + `wgpu` | 256 | 25.0 s | 41.7 s |
| with `parley` + `swash` | 300 | 29.0 s | 54.0 s |
| with `cosmic-text` | 281 | 28.0 s | 53.3 s |
| with `taffy` | 257 | 25.6 s | 46.1 s |
| The whole spike | 328 | | |

Audit: one `unmaintained` warning (`ttf-parser`), which the compiler's audit
leg does not deny. Licences: all on the compiler's accepted list.

### 11.3 Measurements

| Measure | Result |
|---|---|
| Release binary, stripped | 12.3 MB; 7.5 MB size-optimised |
| Cold start to first offscreen frame | 115 to 219 ms, of which device creation 72 to 166 ms |
| First frame on screen in the window | 105 to 286 ms |
| CPU per counter click | event 2 us, layout with reshape 33 us, scene 13 to 25 us, encode and submit 73 to 120 us |
| Work per click | one text reshaped, one element repainted; a miss does nothing |
| 10,000-row list, 23 rows visible | scene build 101 us median, 153 us at the 95th percentile; two draw calls |
| Same, a full page per frame | 357 us median |
| Resident memory | about 140 MB, mostly the software driver; the spike's atlas wastes 32 MB that a real one would not |

Text shaping, best CPU time per paragraph in microseconds:

| Paragraph | `parley` | `cosmic-text` |
|---|---|---|
| Latin | 11.9 | 25.7 |
| Latin, Arabic, Hebrew mixed | 16.8 | 24.9 |
| Long, eight lines | 45.5 | 98.1 |
| Emoji | 17.5 | 21.2 |
| CJK through a fallback font | 11.4 | 585 |

Both rendered Arabic joining, bidirectional order, Hebrew, CJK and colour
emoji correctly by eye. `cosmic-text` has an optional cache that might close
the fallback gap; it was not tried.

### 11.4 Q8: the executor and the window loop

The executor cannot be driven from the window loop today. It owns its loop and
blocks inside the readiness wait; a turn is private; and its waker rings a
loopback bell that cannot wake `winit`.

Main thread, as recommended, needs a small executor slice: a public
non-blocking turn that returns the next deadline and the sockets to watch, and
a pluggable waker that calls the window loop's proxy. Timers then cost
nothing. Sockets need a helper thread that waits and signals the loop, only
while sockets are registered, so an app with no network pays nothing. Resize
is in step for free.

Second thread, as M2 does, needs no executor change. Signals cannot cross
threads, so the element tree, layout and rendering all live on the program
thread. Live resize then needs the main thread to wait for each new frame, and
on macOS window calls must be forwarded.

### 11.5 Q6: the element syntax

Tag names are unrestricted, so `<row>` parses. The lowering in
`crates/vilan-core/src/elements.rs` hard-codes the constructor
`std::web::ui::view(tag)`, the method names `attr`, `on`, `on_event` and
`child`, and turns an undotted `gap(x)` into `.attr("gap", x)`. Lowering onto
another element type means resolving the constructor in the analyzer and
lowering undotted attributes to typed method calls. Also touched: IDE
completion, and the formatter, which reorders attributes as an HTML set.

### 11.6 Not verified

Any real GPU. Windows and macOS at run time. Wayland. Live window resize. A
scale change while running. Animation. Either editing model. Input methods.
Thai and Indic line breaking. Whether Windows' emoji font draws in colour.

### 11.7 The run that would settle the GPU numbers

On the owner's Windows machine, with rustup's MSVC toolchain, from the
`gfx-spike` branch: `cargo build --release` in `spike\gfx`, then the `demo`,
`counter`, `list`, `coldstart` and `window` subcommands of `gfx-spike.exe`,
once per `WGPU_BACKEND` of `dx12` and `vulkan`. To look at: frame times, a
live drag-resize, idle CPU and GPU, device creation time, memory, and real
125% and 150% scaling.
