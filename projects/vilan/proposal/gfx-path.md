# Paths and icons in `std::gfx` and `std::ui` (native-ui.md part P5)

Status: RULED 2026-11-12. The owner accepted all thirteen recommendations of section 9 ("Accept all recs"); they are rulings R1 to R13 by question number (tracker F175). First work under them: slices S1 and S2 of section 5. Written 2026-11-12 by lane `path-58`,
with a spike on branch `path-58` @05259d63 (`spike/path/`, not for merge). Nothing here
is built in the shipped crate. Section 9 lists the decisions in the order I
would ask them, each with a recommended answer.

## 0. The answer up front

Draw a path as a coverage mask, rasterised on the CPU by `zeno`, and draw the
mask as a textured quad from the glyph atlas's mask pages, tinted by a colour.
That is how a glyph is drawn today, and `zeno` is the rasteriser `swash`
already uses for glyphs, so the recommendation adds no package, no shader, no
pipeline and no draw call kind. An icon then batches with the text beside it.

The spike measured it against CPU tessellation (`lyon`) drawn with MSAA, and
against a second mask rasteriser (`tiny-skia`):

- **Quality.** At 16 dp a mask is within 0.022 of the true coverage on
  average. Four-sample MSAA is 0.052 off, and with no anti-aliasing 0.161.
- **Cost per frame once cached.** 240 icons cost 83 us of CPU against 72 us
  for 240 rounded rectangles. Nothing else changes in the frame.
- **Cost of a new path.** Parse plus rasterise is 2 to 48 us for a 24 dp icon
  (the gear, the worst of seven, is 48 us; stroking it once and filling the
  outline makes that 34 us, and 10 us at every later size). The upload is one
  small texture write.
- **Weight.** Zero new packages, zero build time. `lyon` would add five
  packages; `vello` twelve, and compute shaders the renderer refuses on
  purpose.

`lyon` stays the documented fallback for large paths whose data changes every
frame, if a real measurement ever asks for it. `vello` stays rejected, as
native-ui.md 3.3 said.

Icons are generated Vilan source from an upstream set (Lucide first), shipped
as a package, and drawn by a typed `icon` element in `std::ui` whose colour is
the inherited text colour.

## 1. What a UI needs from paths

| Need | How common | What it asks of a path |
|---|---|---|
| Icons | Every screen | Small (12 to 48 dp), many, few distinct, drawn every frame, rarely change. Mostly STROKED (Lucide, Tabler, Feather, Heroicons outline), some filled (Material, Heroicons solid) |
| A checkbox mark, a radio dot, a chevron, a dropdown caret | Every form | An icon by another name |
| Simple charts: a line, an area, bars | Some apps | Large (hundreds of dp), one or two paths, data may change every frame |
| Focus rings on shapes that are not rounded rectangles | Rare | A stroke. Rounded rectangles and circles already have one: a border, and a radius of half the side |
| A spinner arc | Common | A stroked arc, rotated or with a moving start (animated) |

Icon sets that matter, and their form:

| Set | Licence | Form |
|---|---|---|
| Lucide (about 1,600) | ISC | 24-unit box, stroke 2, round caps and joins, no fill. SVG elements `path`, `circle`, `rect`, `line`, `polyline`, `ellipse` |
| Tabler, Feather | MIT | The same conventions as Lucide |
| Heroicons | MIT | 24-unit box: outline (stroke 1.5) and solid (fill) |
| Material Symbols | Apache-2.0 | Filled paths in a 24-unit box; also shipped as a variable font |

This project already has a Lucide package on the web side: kolt generates
`src/lucide/lib.vl` (636 KB) from the upstream SVGs with `scripts/lucide.mjs`,
declared as the package's `generated` root (CHANGELOG, E357 and E186). It
emits web elements, so the native side needs its own generator, but the
pattern is proven.

What a UI does NOT need, and this paper leaves out:

- Rendering SVG documents: groups, `transform`, gradients, filters, text, CSS.
  An icon generator flattens what it needs into path data at generation time.
  No `usvg` or `resvg`.
- Clipping to a path, boolean operations on paths, blend modes.
- Path hit testing. A button is hit by its rectangle. (`zeno` has a hit
  tester if it is ever wanted.)
- Huge or zoomable vector art (maps, drawing apps). That is `vello`'s case.

## 2. The surface

### 2.1 In `std::gfx`

```vilan
// Sketch only. Names are for discussion.
export external struct Path;        // a host value: immutable, cheap to copy

export impl Path {
	/// SVG path data (`M20 6 9 17l-5-5`): every command, arcs included.
	/// Err names the byte where the data stops making sense.
	fun from_svg(data: str): Result<Path, str> { .. }

	fun builder(): PathBuilder { .. }

	/// The smallest rectangle holding every point (control points included),
	/// in the path's own units.
	fun bounds(self): Rect { .. }
}

export external struct PathBuilder;  // a host value

export impl PathBuilder {
	fun move_to(self, x: f64, y: f64): PathBuilder { .. }
	fun line_to(self, x: f64, y: f64): PathBuilder { .. }
	fun quad_to(self, cx: f64, cy: f64, x: f64, y: f64): PathBuilder { .. }
	fun cubic_to(self, c1x: f64, c1y: f64, c2x: f64, c2y: f64, x: f64, y: f64): PathBuilder { .. }
	/// SVG's arc: radii, rotation in degrees, the two flags, the end point.
	fun arc_to(self, rx: f64, ry: f64, rotation: f64, large: bool, sweep: bool, x: f64, y: f64): PathBuilder { .. }
	fun close(self): PathBuilder { .. }
	fun finish(self): Path { .. }
}

export enum FillRule { NonZero, EvenOdd }
export enum Join { Miter, Round, Bevel }
export enum Cap { Butt, Round, Square }

/// A stroke, in the PATH's units: it scales with the path, as SVG's does.
export struct Stroke {
	width: f64,
	join: Join,     // Round
	cap: Cap,       // Round
	miter_limit: f64, // 4
}

export enum PathPaint { Fill(FillRule), Stroke(Stroke) }

impl Frame {
	/// Draws `path` with its origin at `at`, `scale` dp to one path unit,
	/// painted solid `color`.
	fun path(self, path: Path, at: Point, scale: f64, paint: PathPaint, color: Color) { .. }
}
```

Units. A path's coordinates are its own units. For an icon they are the
icon's box (24 units for Lucide); for a chart they are dp, drawn at scale 1.
`scale` is a plain ratio, so `Dp` never appears inside a path, and drawing a
24-unit icon at 16 dp is `scale` 16 / 24. A stroke's width is in path units
and scales with the path, as SVG's does by default. The hairline rule of
section 5 does not apply to paths: a stroke at an angle has no pixel grid to
snap to.

Placement. The renderer turns `at` and `scale` into device pixels and snaps
the path's origin to a whole device pixel on both axes, as it snaps a text
baseline. No subpixel bins for paths: icon sets are drawn to a whole-unit
grid, and a bin per quarter pixel would multiply atlas entries for a
difference nobody sees. A path moved by an animation moves by whole pixels.

Transforms. The crate's transform is a translation and a uniform scale
(rotation is a later part). Both fold into the mask's size and position: the mask is
rasterised at the device size it is drawn at, so a path is sharp at every
scale and every transform scale. Rotation, when the crate gets it, means a
mask per angle; section 3 has what that costs.

Colour. Solid only in the first version. A gradient on a path is the mask
times the gradient the rectangle shader already computes, which a later slice
can add without changing this surface (`color` becomes a `Fill`, as a
rectangle's is).

Clipping. Paths are clipped by the clip in force (a rounded rectangle), like
every primitive. Clipping TO a path is out: it needs a stencil or an offscreen
mask pass, which breaks batching, and a circular avatar is already a rounded
clip with a radius of half the side.

Dashes. Out of the first version. `zeno` strokes dashes, so adding them later
is one more field on `Stroke`. A UI rarely needs them (a dashed focus ring is
a style choice; a chart grid can be solid hairlines).

### 2.2 What crosses the host boundary

The crossing rule allows numbers, strings, `Bytes`, host values and `|| void`
closures. The surface follows the precedent of `TextLayout` and `Texture`:
heavy things are host values the program holds, and a draw is one call of
numbers.

| Extern | Crosses |
|---|---|
| `gfx_path_parse(data: str): Result<Path, str>` | a string in; a host value or an error string out |
| `gfx_path_builder(): PathBuilder` | a host value out |
| `gfx_path_segment(builder, verb: i32, a..g: f64)` | numbers: one call per segment, nothing allocated per call |
| `gfx_path_finish(builder): Path` | a host value in, a host value out |
| `gfx_path_number(path, which: i32): f64` | the bounds, one number at a time, as `gfx_layout_number` |
| `gfx_path(frame, path, x, y, scale, paint: i32, rule_or_width, join, cap, miter_limit, r, g, b, a)` | one call of numbers per draw, as `gfx_text` |

Parsing. `zeno` parses SVG path data, arcs included, and its validator gives
the byte where data goes wrong (`zeno::validate_svg`). The host wraps that in
an error that names the byte and shows the data around it. Parsing the gear
(600 bytes, 62 commands) takes 11 us, the check mark 0.2 us.

Identity and caching. A `Path` keeps its commands and a hash of them, made
once. The renderer's mask key is the hash, the paint, and the device scale,
with the commands compared on a hit, so two `Path` values parsed from the same
data share one mask. A path that is STROKED also keeps its stroke outline per
stroke style, made the first time it is drawn with that style: a stroke's
outline does not depend on the size it is drawn at (its width scales with the
path), so every later size only fills the outline. The spike measured that
filling the kept outline gives byte-identical masks and cuts the gear's
rasterise at 16 dp from 35 us to 7 us.

Name. `std::path` is filesystem path arithmetic over `str` and says a `Path`
type may come there later (filesystem.md 9). `gfx::Path` lives in its own
module and a program that wants both qualifies one. Q4 asks.

## 3. How to draw it

Four candidates. The spike built (a) and (b); (c) and (d) are argued from
their design and dependency trees.

### 3.1 The numbers

All on this machine: no GPU, Mesa 25.0.7's lavapipe (Vulkan on llvmpipe),
16 cores shared with other lanes (load 7 to 15 during the runs). CPU times are
real and are medians of three runs; GPU and wall times are a software
rasteriser's and say nothing about a real GPU.

Quality: mean absolute error of each pixel's coverage against the true area
coverage (the icon rasterised at 16 times the size and averaged), over the
pixels either one inks; and the worst pixel. Seven icons per size.

| dp | mask (`zeno`) | mask (`tiny-skia`) | `lyon`, 4x MSAA | `lyon`, no AA |
|---|---|---|---|---|
| 16 | 0.022 (worst 0.18) | 0.023 (0.12) | 0.052 (0.31) | 0.161 (0.78) |
| 24 | 0.019 (0.19) | 0.019 (0.13) | 0.048 (0.32) | 0.104 (0.55) |
| 48 | 0.009 (0.35) | 0.014 (0.19) | 0.028 (0.33) | 0.067 (0.60) |
| 256 | 0.002 (0.50) | 0.004 (0.42) | 0.006 (0.42) | 0.016 (0.76) |

(The reference is `zeno` itself at 16 times the size, which flatters `zeno`
slightly; `tiny-skia`, an independent rasteriser, scores the same to within
0.001 at 16 and 24 dp. Eight samples per pixel were not available: lavapipe offers 1
and 4, and WebGL2 guarantees only 4.)

Time to prepare a path the first time (CPU, microseconds, after parsing):

| Icon | dp | `zeno` mask | `zeno`, outline kept | `tiny-skia` mask | `lyon` tessellate (triangles) |
|---|---|---|---|---|---|
| check (stroke) | 16 / 24 / 48 / 256 | 1.5 / 1.7 / 3.0 / 7.1 | 0.6 / 1.3 / 1.5 / 6.1 | 3.6 / 4.8 / 6.6 / 46.5 | 0.4 to 0.7 (12 to 42) |
| circle-check (stroke) | same | 5.4 / 6.0 / 8.1 / 23.5 | 2.0 / 2.5 / 4.5 / 19.9 | 7.9 / 10.6 / 18.2 / 98.5 | 1.9 to 4.5 (66 to 204) |
| star (stroke) | same | 16.3 / 17.0 / 20.0 / 51.4 | 3.8 / 4.4 / 7.3 / 37.9 | 9.2 / 11.9 / 18.2 / 93.8 | 2.9 to 4.8 (100 to 190) |
| settings, the gear (stroke) | same | 35.4 / 37.5 / 42.9 / 103 | 7.3 / 9.5 / 14.7 / 76.8 | 19.2 / 23.0 / 33.6 / 141 | 7.0 to 13.4 (258 to 558) |
| chevron-down (stroke) | same | 1.3 / 1.5 / 2.0 / 5.7 | 0.6 / 0.7 / 1.2 / 4.9 | 2.8 / 4.0 / 5.6 / 36.1 | 0.5 to 0.8 (12 to 42) |
| heart (fill) | same | 0.7 / 0.9 / 1.5 / 6.3 | | 2.9 / 3.9 / 7.4 / 48.4 | 2.0 to 4.3 (20 to 72) |
| ring with a hole (even-odd fill) | same | 1.1 / 1.4 / 2.4 / 10.3 | | 4.4 / 5.3 / 10.5 / 68.0 | 3.1 to 7.7 (42 to 132) |

"Outline kept" is the stroke outline made once per path and style (0.4 us for
the check, 6 us for the star, 13 us for the gear) and then only filled per
size; its masks are byte-identical to stroking directly.

Per frame and per new path:

| Measure | Result |
|---|---|
| 240 icons at 24 dp, masks cached, through the shipped renderer | 83 us CPU (encode, upload, record, submit) |
| 240 rounded rectangles, same renderer | 72 us CPU |
| Draw calls for the 240 icons | 7 in the spike (each mask is its own texture there); 1 when the masks share an atlas page |
| The same 240 icons as `lyon` triangles at 4x MSAA | 250 us CPU (copying cached triangles to each position, a new vertex buffer per frame), and a 4-sample target |
| A frame that adds one new 24 to 53 dp gear mask (rasterise, a new texture, upload) | about 1.5 ms wall against 1.39 ms without, on lavapipe: about 0.1 ms for the new path |
| A chart: a 200-point line, 2 dp wide, over 800 x 300 dp | `zeno` mask 93 us; `lyon` 17 us, 602 triangles |
| The area under it, filled | `zeno` mask 21 us; `lyon` 13 us, 200 triangles |
| Target memory, the spike's 400 x 1906 sheet | 3.05 MB single-sampled; 15.3 MB at 4x MSAA with its resolve |

Determinism. The same scene rendered by Mesa's Vulkan and GL software drivers:
the masks differ by at most 1 in a channel (13 of 762,752 pixels), the MSAA
and aliased triangles not at all. Three runs on Vulkan were byte-identical.
Both drivers are llvmpipe underneath, so this says little about two real
GPUs; see 3.3.

Dependencies:

| Candidate | New packages in the crate's lockfile | Licences | Clean build of `vilan-rt-gfx` |
|---|---|---|---|
| (b) `zeno =0.3.3` | 0: already there through `swash` | Apache-2.0 OR MIT | unchanged: already compiled |
| (b) `tiny-skia =0.11.4` | 0: already there on Linux through winit's Adwaita decorations (its `png` feature off) | BSD-3-Clause | newly compiled on Windows and macOS; not measured |
| (a) `lyon_tessellation =1.0.23` | 5: `lyon_tessellation`, `lyon_path 1.0.19`, `lyon_geom 1.0.20`, `euclid 0.22.14`, `float_next_after 1.0.0` | MIT OR Apache-2.0; `float_next_after` MIT | +4.5 s of CPU in release (of 416 s), +1.9 s in debug (of 170 s), off the critical path (`naga` takes 41 s); wall 63.5 s against 64.4 s base, inside the load noise |
| (d) `vello =0.12.0` | 12: `color`, `euclid`, `futures-intrusive`, `guillotiere`, `kurbo`, `peniko`, `polycool`, `svg_fmt`, `termcolor`, `vello`, `vello_encoding`, `vello_shaders`; on `wgpu ^30` | Apache-2.0 OR MIT | not built |
| (d') `vello_hybrid =0.2.0` | about 60, and a second `wgpu` (29.0.4) | | not built |

Every licence above is on the accepted list. None of the candidates was run
through `cargo audit` in the crate (none was added to it).

### 3.2 The candidates

**(a) CPU tessellation with `lyon`, drawn as triangles.** Fast to prepare
(the gear in 7 to 13 us at any size) and the cheapest at large sizes. Its
geometry is size-independent if tessellated at the largest size, so a scale
animation re-tessellates nothing. Against it:

- Anti-aliasing. Triangles have none. MSAA at 4 samples gives five levels of
  coverage, and it shows: the gear at 16 dp is speckled grey, 2.4 times the
  mask's error. 8 samples is not portable (WebGL2 guarantees 4; lavapipe
  offers 4). Feathered edges (an extra ring of triangles with alpha fading out,
  as `lyon` users do by hand) fixes the edge but not thin strokes, and costs a
  second tessellation pass of our own.
- It does not fit the renderer. Today every primitive is an instanced quad,
  single-sampled, with its own anti-aliasing in the shader. MSAA means either
  the whole pass at 4 samples (four times the target's memory, 133 MB more at
  3840 x 2160, for shapes that do not need it), or paths drawn into a separate
  multisampled texture and composited, which breaks the paint-order batching
  of R14 (a path between two rectangles needs a pass break or a path atlas).
- A new pipeline, vertex and index buffers that change per frame, and a third
  primitive kind for the order test.
- Five new packages.

What it keeps open: large paths whose data changes every frame (a live chart),
and rotation (rotating triangles costs nothing). Those are the cases to watch.

**(b) CPU coverage mask, in the atlas, as a textured quad.** Recommended.

- Quality: exact area coverage (`zeno` accumulates signed areas, as font
  rasterisers do), 256 levels. The same look as the glyphs beside it, from the
  same rasteriser, blended the same way (linear light, as section 3.4 of
  native-ui.md settled for text).
- Fit: none of the renderer changes. A mask is a glyph with another key: the
  mask pages, the shelf allocator, LRU eviction that never evicts the current
  frame's entries, the sprite pipeline and its `MASK` kind, the paint-order
  test. The atlas key gains a variant (`Path { hash, paint, device scale }`
  beside today's glyph key).
- Cost: a cached icon costs what a glyph costs to draw. A new icon costs its
  rasterise (table above) and a small texture write. Memory: a 24 dp icon at
  100% is under 600 bytes of a mask page; at 256 dp it is 64 KB.
- Under scale and animation. A new device size is a new mask. Animating an
  icon's scale rasterises once per frame: 1 to 15 us for the seven icons at
  48 dp with the outline kept, affordable. Rotation (not in the crate yet)
  would be a mask per angle; for icons the same cost, for a large path it
  argues for (a).
- Large paths. A mask over 256 device pixels a side does not go in the atlas
  (a 1024 page holds sixteen of them): it gets a texture of its own, as an
  `Image` does today, freed when it is not drawn. A chart line 800 x 300
  rasterises in 93 us; redrawn every frame that is affordable but it is where
  (a) would win (17 us).
- Determinism. The mask is made on the CPU, so it is the same bytes on every
  machine with the same `zeno` and the same float behaviour; the GPU only
  samples it texel for texel and blends. Golden tests hold to the same
  tolerance of 1 the text goldens use.
- Weight: nothing new.
- What it rules out: nothing above the primitive. A later switch to (a) for
  some paths is a renderer decision behind the same `Frame::path`.

`zeno` or `tiny-skia`? Same quality to within 0.001 at icon sizes. `zeno` is
two to eight times faster on fills and simple strokes and at large sizes;
`tiny-skia` was faster on the curved strokes (star, gear) at small sizes until
the outline is kept, after which `zeno` is faster at every later size. `zeno` is already compiled into
every program that uses the crate. The two placed a curved inner stroke edge up
to half a pixel apart at 256 dp, with no visible artefact in either (I looked
at both, magnified). Recommendation: `zeno`; `tiny-skia` is the fallback if a
sweep of a whole icon set finds a stroker defect.

Outside evidence: GPUI draws SVG icons the same way (rendered to an alpha mask
with `resvg`/`tiny-skia`, stored in its sprite atlas as monochrome sprites,
tinted by a colour). That is from memory of the Zed source; I did not re-check
it in this lane.

**(c) Analytic coverage or signed distance in the shader.** Three families:
curve triangles with an implicit test in the fragment shader (Loop-Blinn),
per-pixel winding from a texture of curves (the Slug approach), and
multi-channel distance fields made per path. All three give resolution
independence, which is their reason to exist: huge sizes and smooth zoom. A UI
draws icons at three or four sizes. Against them: the most work of the four
(a new pipeline, curve encoding in data textures because WebGL2 has no storage
buffers), thin-stroke quality at 16 dp that is worse than exact coverage
(distance fields round corners; Loop-Blinn needs extra work for strokes), and
Slug's method is patented by its author (not checked in this lane). Not
spiked. Rejected for the first version.

**(d) `vello` behind the primitive.** native-ui.md 3.3 rejected it for the
renderer and named this as the door to use if paths mattered more than
expected. They do not: every case in section 1 is small or rare. It needs
compute shaders and storage buffers, outside the WebGL2 limits `gpu.rs` holds
on purpose (P6, the browser). It is 12 more packages, a second renderer to
composite with ours, and pre-1.0. `vello_hybrid` (CPU stripping, GPU fill,
meant to run on WebGL2) resolves to about 60 new package names and pulls `wgpu` 29
beside our 30. `vello_cpu` is 11 packages for what `zeno` already does.
Rejected again.

### 3.3 What the numbers do not say

- Nothing here ran on a real GPU. The GPU half of (b) is the glyph path, so a
  real GPU should only make it cheaper; MSAA cost on a real GPU is mostly
  memory bandwidth, which the software driver does not model.
- Texture writes on a real driver. The spike made a texture per mask; the real
  slice writes into an atlas page.
- Cross-GPU determinism of MSAA: Vulkan, D3D12 and Metal specify the 4-sample
  positions, but resolve and edge rules differ by driver. Only (a) is exposed
  to that.
- The whole Lucide set. Seven icons were drawn, not 1,600.

## 4. Icons

### 4.1 How an icon set ships

Generated Vilan source, as kolt's web Lucide package is:

```vilan
// Generated by scripts/lucide-native.mjs from lucide-static 0.x (ISC). Do not edit.
export fun check(): Icon {
	Icon::stroked("M20 6 9 17l-5-5", 24.0, 2.0)
}

export fun circle_check(): Icon {
	Icon::stroked("M22 12a10 10 0 1 1-20 0a10 10 0 1 1 20 0ZM9 12l2 2 4-4", 24.0, 2.0)
}
```

- The generator flattens every SVG element of an icon (`circle`, `rect`,
  `line`, `polyline`, `ellipse`, `path`) into one path-data string, and reads
  the set's box and stroke conventions from the SVG root.
- `Icon` holds the data string, the box, and the paint. It parses on first
  draw and keeps the parsed `Path` (the host caches by content, so two copies
  of `check()` share one parse and one mask).
- Unused icons cost nothing in a native binary: each is a function, and the
  linker drops what nothing calls. Lucide's path data is a few hundred
  kilobytes of source in all.
- A package, not std (Q11): icon sets change on their own schedule and have
  their own licences, and std ships no look. The `generated` root keeps
  `vilan fmt` and the editor's reading aids off it, as kolt's already does.

Icon fonts (Material Symbols, Font Awesome) already work today through
`register_font` and a text run, with no work here. I would document them and
not recommend them: a code point or ligature name instead of a name in code,
alignment by font metrics, one colour, and nothing for accessibility.

### 4.2 The element

```vilan
// Sketch only.
<row gap(dp(8)) align(Align::Center)>
	<icon of(lucide::check()) size(dp(16))/>
	<text>"Saved"</text>
</row>

<icon of(lucide::trash()) label("Delete")/>
```

- A seventh typed element, `icon`, by the `[element]` contract of native-ui.md
  section 12. Attributes: `of(Icon)`, `size(Dp)`, `color(Color)`, `label(str)`.
- Colour: the inherited TEXT colour unless `color` sets one, as SVG's
  `currentColor` does. Text style is already the one inherited thing in
  `std::ui`, so an icon in a red button is red with no extra code.
- Size: square, `size` on a side. Unset, it is the inherited text size, so an
  icon beside a label matches it. That is a default, not a unit: `dp` stays
  the only length (section 5). Q9 asks.
- Accessibility: an icon is decorative unless it has a `label`, and a
  decorative element publishes nothing. With a label it takes `Role::Image`
  and that label. An icon inside a labelled button stays decorative, which is
  what a screen reader wants.
- Not a general `path` element. A chart in a layout needs a paint callback
  sized by layout, which is its own question (a "custom paint" element), not
  this part.

## 5. Slices and exit tests

| Slice | Delivers | Exit test |
|---|---|---|
| S1 the primitive | `vilan-rt-gfx`: `Path` (parse with byte-precise errors, builder, content hash, kept stroke outlines), `SceneBuilder::path`, masks by `zeno` in the atlas's mask pages under a new key variant, own textures over 256 px, origins snapped | Golden images: the seven spike icons at 16, 24, 48 and 256 dp, at 100%, 125% and 150%, tolerance 1. Unit pins: parse errors (the byte), both fill rules, a stroke's outline kept per style and reused, two equal paths sharing one mask, eviction never taking the current frame's mask, a large mask off the atlas. 240 cached icons within 25% of 240 rectangles' CPU time (`examples/measure.rs`) |
| S2 the Vilan surface | `std::gfx`'s `Path`, `PathBuilder`, `Stroke`, `PathPaint`, `Frame::path`; `docs/std/gfx.md` | Docs gate; the `vilan/examples/gfx` end-to-end test draws a path and holds it to a golden; a malformed `from_svg` is an `Err` naming the byte |
| S3 the element | `std::ui`'s `icon` and `Icon`; inherited colour and size; label and role | `ui_screen`'s recorded rectangles and goldens with icons in a row beside text; the outline listing shows a labelled icon's role and none for a decorative one; the todo app (P4) uses a check icon in its checkbox |
| S4 an icon set | A generator and a Lucide package, outside std | Every Lucide icon parses, and renders at 24 dp within a set error of a reference rasteriser (`tiny-skia` is enough); the package checks clean |

Later, each its own slice when asked for: dashes; gradient fills on paths;
rotation (and a mask per angle, or (a) for large paths); a custom-paint element
for charts; (a) for large paths that change every frame, if a real measurement
asks.

## 6. What I am least sure of

- **Thin strokes in linear light.** Lucide at 16 dp is a 1.33 px stroke. Masks
  blend in linear light, as text does, so a dark stroke on white reads lighter
  than a browser draws it (browsers blend in sRGB). The zoomed images show it.
  If it bothers, the fix is the text's (a contrast or gamma adjustment on mask
  coverage), shared by both, and belongs with section 3.4's open text
  decisions.
- **`zeno`'s stroker over a whole set.** Seven icons are a sample. S4's sweep
  is the real test, with `tiny-skia` as the fallback.
- **`zeno`'s upkeep.** It is the `swash` author's, at 0.3.3, and already a
  dependency through `swash`, so the risk is not new, but this adds a direct
  use.
- **The default icon size.** Following the text size is convenient and is the
  web's habit (`1em` icons); it is also a second thing a text size changes.
- **Real GPUs, Windows and macOS.** Not run. Section 3.3.

## 7. The spike

Branch `path-58`, directory `spike/path/`: a package and workspace of its own
with its own lockfile (seeded from the GPU crate's). It depends on the
shipped `vilan-rt-gfx` by path and draws masks through its PUBLIC API (a mask
becomes an `Image`, drawn by the sprite pipeline glyphs use), and has a
triangle pipeline of its own for `lyon`. The shipped crate's manifest,
lockfile, notices and CI job are untouched. Run it with
`cd spike/path && cargo run --release -- <out-dir>`; it writes the sheets and
close-ups and prints every number above as `key=value` lines. Its images from
this run are beside this paper in `gfx-path-images/`: `sheet-*.png` per
candidate, `zoom-16.png` and `zoom-24.png` (columns: `zeno` mask, `tiny-skia`
mask, `lyon` with no AA, `lyon` at 4x MSAA; rows: check, circle-check, star,
gear, chevron, heart, ring), and `large-256.png` (star and gear at 1:1).

What I saw in them: at 16 and 24 dp the two masks are indistinguishable and
clean; MSAA is close at a glance but the gear and the circle-check's inner mark
are speckled and greyer; no AA is visibly jagged on every diagonal, and the
chevron at 16 dp breaks into stair steps. At 256 dp all four look the same at
1:1; magnified, no AA shows its stairs and the two masks differ by half a
pixel on curved inner edges.

## 8. Not decided here

- Rotation in `std::gfx` (native-ui.md lists it as later).
- A custom-paint element in `std::ui` for charts.
- Where a first-party Lucide package lives (this repo, its own, the registry).

## 9. Decisions (ALL RULED as recommended, 2026-11-12)

Each recommendation below is a ruling, R1 to R13 by its question number.

| # | Question | Recommendation |
|---|---|---|
| Q1 | How paths are drawn: CPU coverage masks in the glyph atlas; CPU tessellation with MSAA; shader-analytic; `vello` | Masks in the glyph atlas (3.2 b) |
| Q2 | The rasteriser | `zeno`, already in the tree through `swash`; `tiny-skia` the fallback |
| Q3 | The surface: a `Path` host value from SVG path data or a builder, drawn with `Frame::path(path, at, scale, paint, color)`; path units scaled by a ratio | Yes, as in 2.1 |
| Q4 | The name `gfx::Path`, given that `std::path` may grow a filesystem `Path` | `gfx::Path`; qualify when both are used |
| Q5 | Stroke options in the first version: width, join, cap, miter limit; no dashes | Yes; dashes later |
| Q6 | Solid colour only on paths at first; no clip to a path | Yes to both |
| Q7 | Path origins snap to whole device pixels, with no subpixel bins | Yes |
| Q8 | Masks over 256 device pixels a side go to a texture of their own, outside the atlas | Yes |
| Q9 | An `icon` element in `std::ui` (not a general `path` element); colour from the inherited text colour; size defaulting to the inherited text size | Yes; if the size default is unwanted, require `size` |
| Q10 | An icon is decorative unless labelled; labelled, it is `Role::Image` | Yes |
| Q11 | Icon sets ship as generated packages outside std, Lucide first | Yes |
| Q12 | Icon fonts: documented as working, not the recommended route | Yes |
| Q13 | The spike: merge `spike/path/` or keep it on its branch | Keep it on the branch, as `gfx-spike` was |
