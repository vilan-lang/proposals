# `std::image` — decode, resize, crop and encode pictures on both backends (M185)

- status: DESIGN 2026-11-02 (integrator; lane m185 builds it; rides v0.54.0)
- tracker: M185 (the owner's item, filed 2026-11-02; kolt's custom avatars, task #9)
- touches: NEW `std/src/image.vl` (`@process`), NEW crates `vilan-image` (the codec core), `vilan-rt-image` (native glue, a satellite of `vilan-rt`), `vilan-image-wasm` (the same core as a wasm module for node); `vilan-rust` (`OptionalCrates`, the extern table), the JS emitter's helpers (`transformer.rs`), `vilan-core`'s `build.rs` (the wasm blob as base64), CI's `wasm` leg, `THIRD-PARTY-NOTICES.txt`, docs `std/image.md`
- related: `native-apps.md` §8 Q7 / Order 37 R8 (`vilan-rt` is dependency-free; the SEPARATE-crate shape `vilan-rt-sqlite` / `-crypto` / `-signal` / `-term` already follow), F19 (the materialized runtime cache), N134 (the wasm leg runs its artifact under node)

## 1. The gap

Kolt stores uploads and wants a few smaller copies of an avatar (32, 64, 256 px
square) and thumbnails of pictures in messages. std decodes nothing: no PNG, JPEG,
WebP or GIF to pixels, no scaling, no encoding. An app's only routes today are a
native npm dependency wrapped by hand (`sharp`: prebuilt binaries per OS, nothing on
the native backend) or sending the full picture and letting the browser scale it.

## 2. The shape: ONE implementation, two hosts

The decision that settles "keeping both backends' output close" is to not have two
implementations. The codec core is one Rust crate on the `image` crate
(`image = "0.25"`, pure Rust: `png`, `zune-jpeg`, `gif`, `image-webp`), and it
reaches both backends:

- **natively** as `vilan-rt-image`, a satellite of `vilan-rt` exactly as
  `vilan-rt-sqlite` is: its own crate, a crates.io dependency `vilan-rt` must not
  take (R8), named by the generated manifest ONLY when the program reaches
  `std::image` (`OptionalCrates.image`), with `opt-level = 3` in the dev profile as
  `vilan-rt-crypto` has (an unoptimized decoder is ten to fifty times slower, and
  the program's own code keeps the fast-to-build profile);
- **on node** as the SAME core built for `wasm32-unknown-unknown` (`vilan-image-wasm`,
  a `cdylib` over a C ABI — no wasm-bindgen, so no CLI version to pin), carried by
  the compiler as a base64 string and emitted into the program's bundle as one JS
  helper when `std::image` is reached. Node's `WebAssembly` instantiates it on
  first use. A program that never reaches the module pays nothing: not a byte in
  its bundle, not a crate in its native build.

The module is `[platform("@process")]` like `std::db`: a server concern. The browser
has `createImageBitmap` and a canvas for the client side, and nothing here is
emitted into a browser leg.

### 2.1 Why not the alternatives

| route | why not |
|---|---|
| `sharp` on node | prebuilt native binaries per OS/arch, a peer install the app must manage, a different implementation from the native backend's (two outputs to keep close), nothing for `--backend rust` |
| pure-JS codecs (`pngjs`, `jpeg-js`, a wasm WebP) | three dependencies of three qualities, a second resampler to write, and WebP decode is wasm anyway |
| a worker pool so decoding never blocks the event loop | real, but a second feature; §6 Q3 |
| `fast_image_resize` (SIMD resampling) | a second dependency for speed the avatar case does not need yet; measured in the lane, a follow-up if Lanczos is slow |

### 2.2 The crates

```
crates/vilan-image/        the core: decode / resize / crop / encode over `image`, no vilan types
crates/vilan-rt-image/     native glue: vilan-rt `Bytes` <-> Vec<u8>, the externs' Rust renderings
crates/vilan-image-wasm/   the core as a wasm cdylib over a C ABI; vilan_image.wasm COMMITTED beside it
```

`vilan-image` is pure (`#![forbid(unsafe_code)]`, like the runtime) and unit-tested
natively: every pin on codec behaviour runs on the host, as `vilan-wasm`'s compile
logic does. The wasm crate is a thin export layer: `alloc(len)`, `free(ptr, len)`,
`decode(ptr, len, max_pixels) -> status`, `width()`, `height()`, `pixels_ptr()`,
`resize(..)`, `crop(..)`, `encode(format, quality) -> (ptr, len)` over one scratch
image slot; pixels are COPIED out to the JS side after every call (`Uint8Array`),
so wasm memory holds nothing between calls and nothing leaks — no handles, no
`FinalizationRegistry`.

### 2.3 Carrying the wasm

`crates/vilan-image-wasm/vilan_image.wasm` is a committed artifact (~1 MB; it moves
only when the core moves). `scripts/build-image-wasm.sh` rebuilds it with the pinned
toolchain's wasm32 target (`rustup target add wasm32-unknown-unknown`, release,
`opt-level = "s"`, `lto`, `panic = "abort"`). `vilan-core`'s `build.rs` base64-encodes
it into `$OUT_DIR` as a JS fragment (`const __image_wasm = "…";`) that
`helper_source` includes (`include_str!`), with `rerun-if-changed` on the blob alone
— so a std edit still relinks without recompiling the compiler (F19's bargain), and
a blob edit recompiles only the emitter. CI's `wasm` leg builds the crate fresh for
wasm32 and runs the decode smoke under node (N134's rule); it also byte-compares
its build against the committed blob when built with the PINNED toolchain — a
stale blob after a core change goes red. (If wasm builds prove non-reproducible
across machines, the compare is dropped and the leg keeps the fresh build + smoke;
the lane records which.)

## 3. The surface (`std::image`)

```vilan
[platform("@process")] mod self;

/// A decoded picture: `width` x `height` pixels, RGBA, 8 bits each. A VALUE —
/// copies copy the pixels (rule 1); nothing to close.
export external struct Image;

export enum Format { Png, Jpeg, Webp, Gif }
export enum Fit { Contain, Cover, Fill }

export impl Image {
	/// Decode PNG, JPEG, WebP or GIF (its first frame), the format sniffed from the
	/// bytes, JPEG's EXIF orientation applied. Refuses a picture that would decode to
	/// more than `max_pixels` BEFORE allocating it (an upload can claim 60,000 x
	/// 60,000). `decode` is `decode_within(bytes, 50_000_000)`.
	fun decode(bytes: Bytes): Result<Image, str>;
	fun decode_within(bytes: Bytes, max_pixels: usize): Result<Image, str>;
	/// The format `decode` would read `bytes` as, from their first bytes.
	fun sniff(bytes: Bytes): Option<Format>;
	/// A picture from raw RGBA pixels (`width * height * 4` bytes); refuses a
	/// mismatch.
	fun from_rgba(width: usize, height: usize, pixels: Bytes): Result<Image, str>;

	fun width(self): usize;
	fun height(self): usize;
	/// The pixels, RGBA row-major — a copy.
	fun rgba(self): Bytes;

	/// Scaled to fit `width` x `height`: `Contain` keeps the aspect inside the box
	/// (the result may be smaller on one side), `Cover` fills the box and crops the
	/// overflow centred, `Fill` stretches. Lanczos3; upscaling allowed.
	fun resized(self, width: usize, height: usize, fit: Fit): Image;
	/// The `width` x `height` window at (`x`, `y`), clamped to the picture.
	fun cropped(self, x: usize, y: usize, width: usize, height: usize): Image;

	/// Encode: `quality` 1-100 for JPEG (WebP is lossless in this slice, `quality`
	/// ignored — §6 Q2), ignored for PNG. `Gif` is decode-only and refused here.
	fun encode(self, format: Format, quality: i32): Result<Bytes, str>;
}
```

Kolt's avatar:

```vilan
let picture = Image::decode(upload)?;
for size in [32usize, 64, 256] {
	let copy = picture.resized(size, size, Fit::Cover).encode(Format::Webp, 80)?;
	write_bytes(i"avatars/{id}-{size}.webp", copy).await;
}
```

Semantics to pin (§4): sniffing by magic bytes (PNG `\x89PNG`, JPEG `\xFF\xD8`,
WebP `RIFF….WEBP`, GIF `GIF8`); EXIF orientation 1-8 applied so a phone photo
comes out upright with `width`/`height` reporting the UPRIGHT size; the pixel limit
checked from the header (`image`'s `Limits` / `ImageReader::with_limits`) before
decoding; `Cover` centres the crop; `Contain` rounds to at least 1 px a side;
alpha kept through PNG and WebP, flattened onto black for JPEG (no alpha channel
there — §6 Q4 asks white); `cropped` clamps rather than refuses; `rgba` round-trips
through `from_rgba` exactly on both backends; the two backends decode the same
PNG to the same pixels, and encode the same pixels to bytes that decode back to the
same pixels (JPEG is lossy: equal after a decode, not byte-equal — the pin compares
pixels within a tolerance).

Errors are `str`s like the rest of std's host seams (`"not a PNG, JPEG, WebP or GIF"`,
`"4000 x 4000 exceeds the 1,000,000-pixel limit"`, `"GIF cannot be encoded"`).

Synchronous: decoding a 12-megapixel JPEG costs ~100-200 ms of the event loop on
node (wasm, no SIMD) and a tenth of that natively. The avatar case is one upload at a
time; a server doing many should run them through `std::task`'s executor (§6 Q3 for
a worker-backed `decode_async`).

## 4. Pins

- `crates/vilan-image` unit tests (host): sniff for the four formats and a
  non-picture; decode of a synthesized PNG/JPEG/WebP/GIF (encoded by the crate in
  the test, so no binary fixtures); EXIF orientation 6 (a 2x3 picture with one
  marked pixel lands where orientation says); the pixel limit refuses from the
  header without decoding; `Contain`/`Cover`/`Fill` sizes and `Cover`'s centring;
  crop clamping; encode -> decode round trip per format; `from_rgba` length check.
- `crates/vilan-core/tests/inference/std_surface.rs`: the vilan surface compiles
  and runs on node through the embedded wasm — a 2x2 PNG as a base64 literal
  decoded, resized to 1x1 (`Fill`), `rgba()` read back; `sniff`; the limit's error
  text; `encode(Gif, ..)` refused; the browser leg REFUSES the module (`@process`,
  the `std::db` pin's form); the helper is emitted only when reached (a program
  without `std::image` carries no `__image_wasm`).
- The native differential (`crates/vilan-cli/tests/native/image.vl`): the same
  program, same printed pixels on both backends.
- `cargo test -p vilan-cli --test third_party_notices` with the regenerated
  notices; `cargo audit --deny unsound` clean.
- CI's `wasm` leg: the wasm crate builds and its node smoke decodes the 2x2 PNG.
- Timings reported, not gated: decode + `Cover` 256 + WebP encode of a 4000x3000
  JPEG on node (wasm) and native.

## 5. Docs

NEW `vilan/docs/std/image.md` ("Images": the surface, the avatar example, the
limit, orientation, the sync note, what each backend runs on), rows in
`docs/SUMMARY.md` and `docs/README.md`'s std table; `docs/std/process.md`'s list of
`@process` modules if it keeps one. CHANGELOG `## Unreleased`: a `feature` entry
(M185) in the M182 entry's form.

## 6. Owner questions

- **Q1. The committed wasm blob** (`crates/vilan-image-wasm/vilan_image.wasm`, ~1 MB,
  regenerated by script, byte-checked by the wasm leg). The alternative — build it in
  `vilan-core`'s `build.rs` — puts a nested cargo wasm32 build inside every
  `cargo build` on every machine and CI leg. Rec: commit the blob.
- **Q2. WebP lossy encoding.** `image` encodes WebP LOSSLESS only (its pure-Rust
  encoder); lossy WebP means `libwebp` (C) on both hosts. Rec: lossless now,
  `quality` ignored for WebP and documented; kolt's avatars can take JPEG for photos
  and WebP/PNG for graphics; revisit if sizes bite.
- **Q3. Async decoding** (a worker thread on node, `spawn_blocking` natively) as
  `decode_async`. Rec: not in this slice; a follow-up item.
- **Q4. JPEG's alpha flattening colour**: black (the `image` crate's `to_rgb8`
  drops alpha, which is black-backed for premultiplied-free data) or white. Rec:
  white — a transparent avatar on a white page.
- **Q5. The default pixel limit**: 50 MP (a 12 MP phone photo decodes; a 60,000²
  bomb does not). Rec: 50,000,000.
