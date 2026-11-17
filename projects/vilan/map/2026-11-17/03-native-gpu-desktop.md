# Map 03: native binaries, native compile time, the GPU UI, native desktop apps

Survey date 2026-11-17. Code read at `vilan/.claude/worktrees/integration` (branch `next`, HEAD
`6edafda5`, the v0.56.1 fold). Papers and tracker at `proposals/` main. Kolt read at
`/home/reed/code/kolt` (branch `vilan-migration`, HEAD `755da23`). Nothing was built or run;
every count below is from grep/wc/a small Python scan over source, or quoted from a named record.
Paths are relative to the vilan worktree unless they start with `proposals/` or `/`.

Where the tracker and the code disagree, the code wins and the disagreement is named.

---

## Part A. The Rust backend (native binaries)

### A1. Architecture as built

**Pieces and sizes (counted, `wc -l`):**

| Crate | Lines | Role | Third-party deps |
|---|---|---|---|
| `crates/vilan-rust` | 19,859 (`src/lib.rs` 19,380 in ONE file, `src/dbg.rs` 479) | the emitter: analyzer `Program` in, one Rust source file out | `vilan-core` only |
| `crates/vilan-rt` | ~17,690 (lib 3,438, executor 3,470, http 4,576, ws 1,637, fs 859, json 826, ...) | runtime every native program links | **none** (`Cargo.toml` has an empty `[dependencies]`), `#![forbid(unsafe_code)]` (`src/lib.rs:30`) |
| `vilan-rt-sqlite` | 532 | `std::db` | `rusqlite 0.41` (bundled: compiles SQLite's C) |
| `vilan-rt-crypto` | | `std::crypto` (SHA-2/HMAC/PBKDF2 hand-written) | `getrandom 0.3`; forbid unsafe |
| `vilan-rt-signal` | | SIGTERM / graceful stop | `ctrlc 3.5.2` |
| `vilan-rt-net`, `vilan-rt-poll` | 312 / 458 | dual-stack listener; readiness wait (`poll`/`WSAPoll`) | libc / windows-sys FFI (14 and 3 `unsafe` lines) |
| `vilan-rt-term` | 352 | raw terminal | FFI (15 `unsafe` lines) |
| `vilan-rt-image` | | `std::image` | `vilan-image` |
| `vilan-rt-webview` | 615 | `std::window` (M2) | `wry =0.57.2`, `tao =0.37.2`; outside the workspace |
| `vilan-rt-gfx` | 28,161 incl. in-tree tests | `std::gfx` / `std::ui` (M3) | wgpu, winit, parley, swash, zeno, taffy, accesskit, arboard; outside the workspace |

**The command.** `vilan build --backend rust <entry>` and `vilan run --backend rust <entry>`
(`crates/vilan-cli/src/main.rs:156-258`; help text: "a debug build unless you build the cargo
project yourself"). `vilan run --backend rust --watch` is refused (`main.rs:604`). There is **no
`--release` flag**: a release binary means running `cargo build --release` by hand in the project.

**What it writes** (`crates/vilan-cli/src/native.rs`):

- A cargo project at `<package root>/dist/native/<entry-stem>/` (`project_dir`, `native.rs:178`):
  `Cargo.toml`, `src/main.rs` (the whole program, one file), and for window programs a seeded
  `Cargo.lock` (`seed_lock`, `native.rs:321`: the audited lockfile of the webview or gfx stack,
  embedded in the compiler as `vilan_embedded::RT_WEBVIEW_LOCK` / `RT_GFX_LOCK`).
- Size, measured on a real program: kolt's server emits `src/main.rs` of **36,632 lines /
  2,524,831 bytes** (`~/.vilan/native-m1/kolt/dist/native/main/src/main.rs`, counted).
- The manifest (`vilan_rust::cargo_manifest`, `crates/vilan-rust/src/lib.rs:19279`):
  `vilan-rt = { path = .. }` plus each OPTIONAL runtime crate only when the program reached it
  (`OptionalCrates`: sqlite, crypto, signal, term, image, poll, window, gfx); `[profile.release]
  panic = "unwind"`; `opt-level = 3` in the DEV profile for `vilan-rt-crypto` and the image codec
  crates only; an empty `[workspace]` so the project never joins a surrounding workspace.
- **How the runtime is referenced** (`runtime_crate`, `native.rs:137`): path dependencies, never
  crates.io. Three roots in order: `$VILAN_RT` (never falls through); the `crates/vilan-rt` of the
  vilan checkout the entry sits in; else the copy EMBEDDED in the compiler binary
  (`vilan-embedded`), materialized once per content hash under `~/.vilan/rt-cache/<hash>/`
  (`crates/vilan-embedded/src/lib.rs:55-110`), with the optional crates beside it.

**How cargo is invoked** (`cargo_build`, `native.rs:336`): `cargo build` with no flags, in the
project directory, `CARGO` env removed. Consequences, all read off the code:

- Profile: `dev` (debug). Incremental compilation: cargo's dev default (on); nothing sets it.
- Target dir: `dist/native/<stem>/target` **per project**, unless the caller exports
  `CARGO_TARGET_DIR` (the differential test does, to build `vilan-rt` once for its whole sweep:
  `shared_target`, `crates/vilan-cli/tests/native_differential.rs:1236`). Nothing in the CLI
  shares a target between projects or between entries of one package: kolt's M1 copy has 12
  separate `dist/native/<stem>/` projects (one per test file plus `main`).
- No `--offline`, no vendoring, no `rust-toolchain.toml` in the generated project (it builds with
  whatever toolchain rustup resolves there). A program reaching only `vilan-rt` needs no network
  (path deps, zero third-party crates); sqlite/crypto/signal/webview/gfx programs resolve from
  crates.io on first build (window stacks start from the seeded lock).
- No linker configuration, no sccache, no codegen-backend selection.
- A rustc failure is classified (`RustcRefusal`, `native.rs:404`): an `arithmetic_overflow` lint
  is reported as the PROGRAM's overflow; anything else as "a BACKEND defect".

**Memory model in the emitted Rust** (`crates/vilan-rt/src/lib.rs`, `crates/vilan-rust/src/lib.rs`):

- Values are Rust values: a vilan `struct` is a Rust `struct`, emitted ONCE PER INSTANTIATION
  (the emitter monomorphises itself, `vilan-rust/src/lib.rs:33-60`; it does not lean on Rust
  generics). Enums are Rust enums, `List` is `Vec`, `Option`/`Result` are Rust's.
- `str` is `vilan_rt::Str = Rc<str>` (`lib.rs:56`): a copy is a refcount bump.
- Rule-1 copies are explicit clones; a last-use pass elides them (the census
  `VILAN_NATIVE_REPORT_COPIES`, `native.rs:37-77`; `crates/vilan-cli/tests/native-copy-census.tsv`).
- The counted cell `Shared<T>` is `Rc<Slot<T>>` with `RefCell`-style borrow tracking
  (`lib.rs:776`); a reentrant access panics with a named sentence (`REENTRANT_READ`, `lib.rs:796`)
  where JS would answer the in-progress value. `Weak<T>` (`lib.rs:1008`). Closures that capture a
  binding something writes are boxed into a cell (`Captured<T> = Shared<T>`, `lib.rs:1052`;
  count via `VILAN_NATIVE_REPORT_BOXED`).
- Closures are `Rc<dyn Fn(..)>` (28 spellings in the emitter). Trait objects are
  `vilan_rt::Dyn<T: ?Sized> { object: Rc<T> }` over a per-trait Rust trait `Object..`
  (`lib.rs:1215`); `&mut self` slots through a `dyn` are refused by name.
- `any` is `vilan_rt::Any` (`lib.rs:2043`): number, str, bool, NULL, Option, BLOB; a struct at an
  `any` position is a known gap (F150, A176).
- Panics: Rust panics with `panic = "unwind"`; `catch_unwind` at 12 runtime sites implements
  `__guarded` / finally / task failure; a native panic prints node's message shape (`main_guard`).

**Async** (`crates/vilan-rt/src/executor.rs:1-80`): emitted code says `async fn`, `.await`,
`spawn(..)`, `sleep(..)`; rustc builds the state machines. The executor is ONE thread, no work
stealing: a slab of tasks (generational ids, F24), a microtask queue drained to exhaustion, then
the earliest timer, then microtasks again, exactly the JS helpers' semantics (the contract is
`transformer.rs::helper_source`). Wakers are `Waker::noop()`; a leaf future parks by writing the
current task id into what it waits on, so the crate stays `forbid(unsafe_code)`. `Boxed<T> =
Pin<Box<dyn Future>>` (`executor.rs:85`). I/O: external readiness sources (`IoSource`) waited on
through `vilan-rt-poll` (F160: real readiness, not a 1 ms tick). R8 added a HOSTED mode:
`executor::turn()` (`executor.rs:1921`) so a window loop can drive the program on the main thread.

**`unsafe`** (counted):

- `vilan-rt`, `vilan-rt-crypto`, `-image`, `-signal`: `#![forbid(unsafe_code)]`.
- `vilan-rt-net` 14 lines, `vilan-rt-poll` 3, `vilan-rt-term` 15: OS FFI (sockets, `poll`/`WSAPoll`,
  termios), each crate `#![deny(unsafe_op_in_unsafe_fn)]`.
- `vilan-rt-gfx`, `vilan-rt-webview`: zero `unsafe` in their own code (F171 was the ruling "no
  unsafe" for gfx).
- **Emitted code: one site.** `crates/vilan-rust/src/lib.rs:10318` emits
  `let x = unsafe { std::ptr::read(x) };` for the bindings of a `match` leg that consumes a value
  with a `Drop` impl.

### A2. Coverage, quantified

**(i) The native differential** (`crates/vilan-cli/tests/native_differential.rs`, 19,378 lines):

- **411 `#[test]` functions**, 0 ignored; **233** `include_str!("native/…")` probe programs from
  `crates/vilan-cli/tests/native/` (231 `.vl` files there). Each compares stdout (or wire bytes,
  for servers) of `vilan run` on node against the native binary.
- **The whole-set sweep** `every_platform_free_program_is_identical_or_named` (`:2826`) walks the
  corpus `vilan/test/*.vl` (162 programs, counted). It enumerates **142** platform-free programs
  (my reimplementation of `platform_free_programs` over `PLATFORM_MODULES`, `:1199`, gives 142,
  matching the lane log below). It is OPT-IN (`VILAN_NATIVE_DIFFERENTIAL=1`): **CI does not set it**
  (no hit in `.github/`); the integrator's seal script runs it ("native whole-set exit=0" in
  `proposals/scripts/integration/sweeps/order58/seal-58-run2.log:5` and `seal-561-run.log:5`).
  The test asserts only "nothing broken"; refusals pass.
- **Latest counts I could find:** `~/.vilan/gates/f168-58/native_differential.log` (2026-11-12):
  **142 enumerated, 134 identical, 4 refused by name, 4 "broken"**; the 4 broken were the JS leg
  failing on `No space left on device` (an environment failure, not the backend). The 4 refusals:
  `async-await.vl` (host binding `sleep`/`setTimeout`), `lens-loaded.vl` (a generic at `any`),
  `lens-overlay.vl` (an unbound generic parameter), `signal-update.vl` (a closure handed a `&mut`
  view that reads the same place). The seal logs (nextest) do not print the counts for a passing
  test, so the seal-time split is **not determined**; the seals prove only "0 broken".
  The B709 stamp's "whole-set native differential 330/330"
  (`proposals/scripts/integration/sweeps/order57/stamps-merges-1109.json:3`, repeated in
  native-objective.md §1) does not match any enumeration in the code (142 + 13 + 7 = 162 corpus);
  I could not reproduce what 330 counted.
- **Other sets:** `ASYNC_SUITE` 7 programs (`:1151`; `every_async_corpus_program_is_identical_or_named`
  requires `await-postfix.vl`, `nursery.vl`, `adapt.vl` identical; the rest may be refused);
  platform-bound set 13 programs (`:1274`), of which 9 are REQUIRED identical
  (`PLATFORM_BOUND_REQUIRED`, `:1170`: crypto, db, asset_bundle, element-syntax, estate,
  process-env, stdin-lines, key-decoder, stdin-keys); `DEFAULT_SUITE` 37 corpus programs always
  run (`:1037`).
- **Exclusions with reasons:** 2 corpus programs. `usize-underflow.vl` ("a `usize` subtracted past
  zero is unspecified: -1 on JS, a debug panic natively", `:1137`) and `lens-rope.vl` (prints its
  own wall-clock timings, `:1188`). Plus 7 async programs routed to their own gate.
  So: 160 of 162 corpus programs are inside some differential; 2 excluded by construction.
- Native whole-set history: Order 39 119 enumerated / 69 identical / 50 refused
  (`sweeps/order39/notes39.md:150`); Order 47 129 / 102 / 27 (`sweeps/order47/REPORT-native-47.md:74`);
  2026-11-12 142 / 134 / 4.

**(ii) Constructs the emitter refuses.** Every refusal goes through `unsupported(what, span)`
(`crates/vilan-rust/src/lib.rs:401`), whose message still reads "this is F1's slice S1b, whose
scope is ..." (stale wording: S1b long since shipped). **135 call sites** (counted). Categorized
from the extracted strings (list in the session scratchpad, not repeated here):

| Category | Approx. sites | Examples |
|---|---|---|
| Internal "did not resolve" guards (analysis left something open; should be unreachable) | ~45 | "an unresolved struct/enum/parameter/closure/call/function", "a value whose type did not resolve" |
| Generics/`any` | ~6 | "a generic type instantiated at `any`", "a value of an unbound generic type parameter" |
| `const` evaluation shapes | ~14 | a `const` map keyed by a non-scalar, a `const` of a host type, non-plain-data `const` |
| Views / loans / aliasing | ~8 | "a call handed two loans of one place, one `&mut`", "a view binding that ALIASES another view binding", "a closure handed a `&mut` view ... reads the same place again" (F102/B729) |
| Trait objects | ~10 | the async member through `dyn`, a view-returning member through `dyn`, `&mut self` slots |
| `?`/`Lift`/`Try` | ~12 | "a `?` lift over a user `Lift` container", `Try` impls of odd shape |
| Patterns / match | ~6 | a guarded leg consuming a `Drop` value (B736 cousin), a pattern over a fixed array past 1 KiB, a `str` literal nested in a pattern outside `match` |
| Iteration / async | ~6 | "a `for` over anything but a `List`" or a plain `Iterator` impl; an `async` spawn of something but a body |
| Operators / literals | ~5 | `>>>`, an operator over two numeric types, a `BigInt` literal with a fraction |
| Context threading | ~4 | "a recursion whose context parameters do not settle (F168)" |
| Misc (print of a function value, interpolation with its own `render`, a body-less function, module-level binding without initializer, ...) | ~19 | |

Separately, **host bindings** with no native body are refused through `host_gap`
(`lib.rs:17598`) as "the host binding `name` (`symbol`)"; under `VILAN_NATIVE_HOST_CENSUS=1` they
become `unimplemented!()` and the walk continues, which is how censuses are taken.

**(iii) std members bound natively vs refused.** There is no single table; the emitter tries a
chain of matchers (`lowered_host_binding_in`, `lib.rs:13253`: runtime/executor, http, ws, json,
scalar, math, module, db, image, window, gfx, crypto). I counted heuristically: for every
`[extern(..)]` in `vilan/std/src` (**564 sites**), whether its symbol (or function name) appears as
a quoted string in `vilan-rust/src/lib.rs`. This over-counts (a name present is not proof of a
correct arm) and under-counts nothing obvious.

| | extern sites | named in the emitter |
|---|---|---|
| All of std | 564 | 420 (74%) |
| Browser-only modules (`web/*`, `browser/*`, `fetch`) | 143 | 16 |
| **Everything else** | **421** | **404 (96%)** |

The 17 non-browser misses: `fs.vl` 13 (the `File` handle tier and the watcher: tracker **F185**,
open), `number.vl` 1 (`Math.log`), `time.vl` 1 (`__with_finally_async`), `io.vl` 1
(`console.log`, emitted through `print` instead), `http.vl` 1 (a parse artifact). `fetch` (the
HTTP client) is essentially absent natively (4 of 16). Every module of `gfx` (37), `ui` (48),
`ui/kit/editing` (12), `db` (16), `crypto` (7), `json` (29), `rpc` (21), `task` (9), `image` (9),
`window` (2) is fully named.

**User externs:** there is no native arm for a program's own `[extern(..)]`. Ruling S2
(native-objective.md §3) asked for `[extern(js = "..", rust = "..")]`; `ExternBinding`
(`crates/vilan-core/src/node.rs:57`) has no rust arm and no parser path for one. **Not built.** A
program with its own JS binding cannot build natively unless std grows the member.

**(iv) The native census and what has cleared since.**
`proposals/scripts/integration/sweeps/order58/native-census.md` (2026-11-09, vilan 0.55.0): kolt's
server built natively only after 23 workarounds; stops filed as B718-B726, B705, F156, F157,
F158, M199. Tracker state now (INDEX open vs archive):

| Item | State |
|---|---|
| B718, B719, B720, B721, B722, B723, B724, B725, B726 | CLOSED (archive; each a v0.56.0 changelog entry) |
| F156, F157, F158 | CLOSED (v0.56.0) |
| F163 (peer address, the M1 report's "NEW") | CLOSED, `Request::peer_address` on both backends (vilan `46ff5439`) |
| F152 + F151 (keep-alive, timeouts, reason phrases) | CLOSED (v0.56.0) |
| M199 | still OPEN in INDEX, but the v0.56.0 CHANGELOG has an M199 fix entry ("a pattern over a `Shared` read that only VIEWS ... reads the cell in place"). Tracker drift, or a residue (`is Some(let _)` copies too, per the title); not settled here |
| B705 | OPEN in INDEX; v0.56.0 CHANGELOG fixes the census's shape (`insert(position(..))`); the item's own title shape (`let v = &mut xs; xs.len(); v.push(3)`) is a different case and stays open. Partly fixed |
| B727 | OPEN (analyzer: a variant fixing some type params drops all) |
| B733 (the M1 report's NEW-1, `for`-condition move, E0382) | OPEN |
| B750 | OPEN (three scalar-view reads are rustc E0308; filed 2026-11-16, not re-run by the integrator) |
| F185 | OPEN (fs File handle tier + watcher) |

Other open native-backend defects in INDEX where rustc refuses the emitted code: B684, B699,
B705, B708, B732, B733, B750, F150, F155; parity bugs F159 (JSON key order), F161 (db REAL vs
INTEGER), B728 (`usize::max` via f64); leak B717 (lens cells live at exit). 52 open INDEX rows
mention native or rustc.

**(v) Does kolt's server build natively today?** **Not from kolt's own tree.** The M1 report
(`sweeps/order58/native-m1-report.md`, 2026-11-10, vilan `3511caa1`) built it with ONE
behavior-dropping workaround on a patched copy (`~/.vilan/native-m1/kolt-m1.patch`); since then
the std side of that workaround shipped (F163). But kolt at `755da23` still carries four JS-only
`[extern]`s on the server path, each now replaceable by std:
`src/server/account_guard.vl:107` (`peer_address`, replace with `Request::peer_address`),
`src/server/files.vl:187` (`decode_base64`), `src/server/mcp_write.vl:41` (`keys_of`) and `:46`
(`base64_of`) (replace with F158's members). `store.vl`'s `pbkdf2_sync` and `toString` are bound
natively. `kolt-patch-notes58.md:5-8, 50-52` records that the M1 patch no longer applies after
kolt's reorganisation and that the std adoptions are "NOT applied (the owner's code decisions)".
So: about four one-line adoptions away from building, assuming no new stop; not verified.

M1's done-criteria (native-objective.md §2) beyond the build: kolt's e2e against the native
binary (kolt has no e2e suite in the tree any more: M1 report line 21), behind a reverse proxy
(not run: no proxy installed), RSS/request cost measured (DONE in the M1 report: native release
idle RSS 14.2 MB vs node 77.5 MB; CPU per request 0.4x node on a DB read, 0.2x on a static file;
spelling 500 words 0.96 s native vs 5 ms node before the M199 fix).

### A3. Native compile time

**Every recorded measurement found:**

| When / where | What | Number |
|---|---|---|
| native-apps.md §2.2 (Order 36 probe, rustc 1.90) | ~700 lines, `cargo build --release`, warm toolchain, cold target | 1.15 s user + 0.35 s sys; 475 KB binary |
| native-apps.md:805 (Order 38) | per accepted corpus program, debug, loadavg 58-64 | emit 0.353 s mean; cargo + rustc +0.521 s mean |
| `native_differential.rs:2829` | the sweep's own note | "rustc is ~1 s per program" |
| `proposals/scripts/integration/native-b4561bf6.log` (seal 56.1) | the whole differential binary, 411 tests, shared target | 349.9 s; the whole-set test alone 195.2 s |
| native-census.md:21 (0.55.0) | kolt server | emit 1.3 s; rustc 8.8 s debug, 37 s release; release binary 9.8 MB |
| native-m1-report.md:55 (0.55.1) | kolt server | emit + debug cargo ~15 s cold, ~3 s warm; release cargo 71 s; 10.2 MB |
| native-ui.md §11.2 (gfx spike) | clean builds | winit+wgpu 256 pkgs 25.0 s debug / 41.7 s release; +parley+swash 300 pkgs 29.0 / 54.0; +cosmic-text 281 pkgs 28.0 / 53.3; +taffy 257 pkgs 25.6 / 46.1; whole spike 328 pkgs |
| gfx-path.md:267 | adding `lyon` | +4.5 s CPU of 416 s release, +1.9 s of 170 s debug; `naga` alone 41 s; wall 63.5 vs 64.4 s |
| F178 (4) | accessibility (accesskit, +57 packages) | clean debug of the gfx crate 29.4-36.8 s; `ui-todo` native 36-44 s (one run each); owner ruled "always on, the build time stands" |
| F167 (c) | gfx debug vs release | "debug fill is 5-10x slower"; owner decision OPEN on optimizing wgpu/parley/swash in the generated dev profile (not done: `cargo_manifest` optimizes only crypto and image) |
| F184 (2) | the Lucide package | `vilan check` 0.29 s -> 0.35 s, +21% instructions when declared even if unused |

No measurement of: an incremental one-line edit of a large program (beyond the M1 "3 s warm"),
link time alone, sccache, mold/lld for native output, a Cranelift codegen backend, a shared
target across projects, or any native build on Windows/macOS.

**What the design already does for rebuild speed:** debug by default (R8, `native.rs:10-14`);
cargo's dev incremental (default, not configured); `vilan-rt` has zero third-party deps and the
optional crates are linked only when reached (`lib.rs:19280-19295`); the heavy loops of crypto
and image are `opt-level = 3` in dev so debug stays usable without a release build;
`CARGO_TARGET_DIR` is honoured (used by tests); the runtime source is materialized once per
toolchain hash; the window stacks start from a seeded lockfile (no resolution churn); rust-lld is
already rustc's default linker on x86_64 Linux since 1.90 (`proposals/projects/vilan/proposal/suite-speed.md:111-117`,
measured for the compiler's own build, where mold showed no real win).

**What it does not do:** share a target directory between projects or between a package's
entries (each `dist/native/<stem>/target` recompiles `vilan-rt`, and for a GUI program the 300+
package wgpu stack, from cold); ship prebuilt runtime rlibs; use sccache; split the emitted
program into modules or crates (kolt's server is one 2.5 MB `main.rs`, one crate, so every edit
re-typechecks and re-borrowchecks the whole program even with incremental codegen reuse); offer
a `--release` flag, a watch loop, or a native dev profile tuned for the gfx stack; pin a toolchain
in the generated project.

**Prior discussion of LLVM / Cranelift / direct machine code:**

- `proposals/archive/backlog.md:893-910` (old section F item 4, "Native backend — server
  performance", DEFERRED far future): lays out "emit C ▸ Cranelift (Rust-native, fast compiles,
  solid codegen; the natural fit for a Rust project) ▸ LLVM (peak performance, heavy dependency,
  slow builds)", says the memory model (scope-end drops C4, ARC for `Shared`, `Weak`) is the
  bigger challenge than codegen, rules out a tracing GC, and says to gate any third backend
  behind "a stable backend abstraction + a shared lowered IR", proven on one non-JS backend first.
  Same in `proposals/archive/backlog-2026-07-18.md:705`.
- `proposals/projects/vilan/proposal/native-apps.md` §1 Q-A and §4 (F1 paper, RULED, Order 36):
  chose "emit Rust" ("rustc does codegen and LLVM does optimisation"; ownership maps almost
  one-for-one; the render stack is already Rust); costed and rejected emit-C (§4.1), wasm-in-a-host
  as first target (§4.2, kept as a later second backend), shipping the interpreter (§4.3).
  Cranelift and a direct LLVM backend are NOT discussed there.
- Nowhere in proposals or the vilan repo is rustc's own Cranelift codegen backend
  (`-Zcodegen-backend=cranelift`) or a direct-LLVM backend evaluated for native COMPILE TIME.
- Facts that bear on an LLVM backend's viability, from the code: the emitter consumes the
  analyzer's `Program` directly; there is no shared lowered IR (F26: monomorphisation resolution
  exists twice, in `transformer.rs` and `vilan-rust`). The emitted Rust leans on rustc for: async
  state machines (`async fn`), drop glue, unwinding (`catch_unwind` x12, `panic = "unwind"`),
  trait-object vtables, `HashMap`/formatting/UTF-8 strings, and the whole runtime (17.7k lines of
  `vilan-rt`, 28k of `vilan-rt-gfx`) which is Rust. A direct backend would need its own lowering
  for each, or a C ABI to a Rust runtime. On the other side, a sizable share of open native
  defects are rustc borrow-checker or typing frictions with the emitted Rust (B705, B732, B733,
  B750, F155, F150, the E0502/E0382/E0308 family), which a backend owning its own IR would not have.

### A4. "Native binaries" completeness

| Basis | Number |
|---|---|
| Whole-set corpus differential, latest counted run | 134 of 142 identical (94%); 138/142 (97%) if the 4 disk-full failures pass, 4 refused by name |
| Corpus inside any differential | 160 of 162 (2 excluded by construction) |
| std host bindings named natively, non-browser modules | 404 of 421 extern sites (96%, heuristic) |
| std host bindings, all modules incl. browser | 420 of 564 (74%) |
| native-objective.md chunks 0-7 (8, 9 replaced by native-ui.md) | done: 0 census, 1 HTTP hardening, 3 backend defects (census set), 4 db boundary (M175, M195, F149), 6 ws:// client; partial: 2 (std homes yes, two-arm `[extern]` no), 5 (kolt measured on a copy; patch not in kolt; no e2e, no proxy), 7 (webview slice 1 of ~9) |
| M1 | build half proven on a copy; not from kolt's tree; e2e and proxy legs not done |

**Estimate: ~85% for native SERVER/CLI binaries** (the language and the server-side std are
essentially covered; remaining: two-arm user externs, fs handle tier/watcher, an HTTP client,
~10 open rustc-refusal defects, release/packaging ergonomics). **~95% for the platform-free
language core** by the differential.

---

## Part B. GPU rendering and the native UI

### B1. Architecture as built (`crates/vilan-rt-gfx`, `vilan/std/src/{gfx,ui}.vl`, `ui/kit/`)

**Layering.** `std::gfx` (vilan, `vilan/std/src/gfx.vl`, 1,667 lines, 37 `__gfx_*` externs) over
`vilan-rt-gfx` (Rust); `std::ui` (`vilan/std/src/ui.vl`, 2,719 lines, 48 `__ui_*` externs) whose
retained element tree lives in Rust (`crates/vilan-rt-gfx/src/ui/mod.rs`, 3,283 lines);
`std::ui::kit` in pure vilan (`vilan/std/src/ui/kit/*.vl`, 2,941 lines; editing uses 12
`__ui_text_*` externs). A native program calls the crate directly through `vilan_rt_gfx::host::*`
(`gfx_host_function`, `crates/vilan-rust/src/lib.rs:19146`), no FFI on the hot path.

**Graphics API layer** (`src/gpu.rs`, `src/window.rs`): `wgpu =30.0.1` with features `vulkan`,
`metal`, `dx12`, `gles` (`Cargo.toml`). Backends are not hard-coded: the instance is made
`new_with_display_handle_from_env` / `new_without_display_handle_from_env`, so `WGPU_BACKEND`
can override; otherwise wgpu's defaults apply (Vulkan then GL on Linux; DX12/Vulkan/GL on
Windows; Metal on macOS). Adapter: `PowerPreference::HighPerformance`, `compatible_surface` = the
window's surface (`window.rs:63-68`). For goldens, `AdapterPreference::Software` picks a CPU
adapter, Vulkan (lavapipe) before GL (llvmpipe) (`gpu.rs:73-88`). Device limits are
`Limits::downlevel_webgl2_defaults()` raised only to the adapter's texture size (`gpu.rs:97-99`),
deliberately, so nothing needs more than the future browser part. `DEBUG` instance flag off unless
`WGPU_DEBUG=1` (Vulkan loader crash under multi-device tests). Surface: first sRGB format,
`PresentMode::AutoVsync`, `color_space: Auto` (`window.rs:72-95`).

**Windowing:** `winit =0.30.13` with `x11`, `wayland`, `wayland-dlopen`, adwaita decorations.
The window loop owns the main thread and the vilan program runs ON IT, turned by the hosted
executor (R8; `src/host/mod.rs:1-75`): window events are queued on a `WindowSource`, a turn runs,
`Turn::Idle{deadline}` becomes `ControlFlow::WaitUntil`, so an idle window costs no CPU. `open` is
async (windows are made between turns). Sockets are waited on by a helper thread only while any
exist (`vilan_rt_poll::install_hosted`). Closing the last window = SIGTERM-style stop. The emitted
`main` is rewritten for this by text replacement (`hand_main_to_the_gfx_host`, `lib.rs:13443`;
F167 notes it should become structural).

**Frame model:** retained, immutable, nestable `Scene` values (`src/scene.rs`). A `SceneBuilder`
appends primitives in paint order plus `push_clip` / `push_transform` / `push_layer` / `pop`; a
built scene can be appended into another (`SceneBuilder::scene`, `scene_at`). An element repaint
rebuilds its own scene and the chain of parents; siblings are re-appended as shared values.
Nothing in a scene points into the atlas (glyphs resolved by key each frame). Frames are on
demand only (`RedrawRequested`), never on a timer (`lib.rs:49-50`).

**Primitives** (`src/lib.rs:9-19`): Rectangle (per-corner radius, solid or linear-gradient fill,
per-side border inside the bounds), Shadow (analytic blurred rounded rect, no offscreen pass),
Text run, Underline, Image (RGBA, rounded clip), Path (fill or stroke, one colour), Clip (rect
with radii), Transform (translate + uniform scale), Layer (opacity).

**Pipelines and shaders:** ONE WGSL file, `src/shader.wgsl` (293 lines), TWO pipelines
(`src/renderer.rs`, `create_render_pipeline` at `:432`), every primitive one instanced quad, no
MSAA (`sample_count: 1`):

| Pipeline | Entry points | Kinds | Draws |
|---|---|---|---|
| quad | `quad_vertex` / `quad_fragment` | rect (default), `QUAD_KIND_SHADOW` | rounded rects, borders, gradients, underlines via a signed-distance function (`rounded_box_distance`, `rounded_rect_coverage`); shadows via an erf-based Gaussian (`shadow_alpha`); clip corners in the same SDF |
| sprite | `sprite_vertex` / `sprite_fragment` | `SPRITE_KIND_MASK` (0), colour (1), `SPRITE_KIND_IMAGE` (2) | single-channel masks (monochrome glyphs AND path masks) tinted by colour; colour glyphs (straight alpha); images (premultiplied, rounded) |

Blending in linear light (sRGB targets); no gamma/contrast correction for text (a stated limit).

**Paint order and batching** (`src/order.rs`, R14): each primitive's order = 1 + the highest order
of earlier primitives it overlaps (GPUI's overlap test); batches merge by order and kind, one
draw call per batch, one instance buffer per batch (`INITIAL_INSTANCE_CAPACITY` 1024, doubling).
`src/encode.rs` (1,490 lines) scales, snaps and culls each primitive and emits instances.

**Text** (`src/text/`): `parley =0.12.0` shapes and lays out paragraphs in dp behind a small
internal interface (`text/parley_engine.rs`; R15: one Rust stack, platform engines possible
later); `fontique` with `fontconfig-dlopen` for system fonts and fallback; `swash =0.2.10`
rasterises glyphs into a glyph atlas (`src/atlas/`): single-channel pages for mono glyphs, RGBA
pages for colour glyphs (emoji), a shelf packer that frees, LRU eviction, no CPU copy kept;
quarter-pixel subpixel positioning (`SUBPIXEL_BINS`); no LCD subpixel text. Editing geometry
(caret, hit-to-index, grapheme/word steps, selection rects, RTL) in `text/editing.rs` (917 lines).

**Paths** (`src/path/`, gfx-path.md): NOT tessellation. A path is parsed (SVG path data, byte-
precise errors) or built, stroked into an outline by `zeno`'s stroker and rasterised on the CPU
by `zeno =0.3.3` into a COVERAGE MASK stored in the glyph atlas's mask pages (own texture past
256 px), then drawn as a tinted textured quad, i.e. exactly like a glyph: no new pipeline, no new
package (zeno already came with swash). Masks are cached by content hash; stroke outlines kept per
style. Known limits: solid colour only, no clip-to-path, no dashes, no rotation; zeno bevels miter
joins sharper than 90 degrees; overlapping stroke outlines over-cover edge pixels (F183).
`lyon` (tessellation) is the documented fallback; `vello` rejected.

**Layout** (`src/ui/mod.rs`): `taffy =0.15.1` (flexbox + grid features), our vocabulary over it:
`row`/`column` = flexbox (gap, padding, grow, shrink, align, justify, wrap), `stack` = one grid
cell with per-child anchor, `text` measured by the text system, `image`, `icon`, `scroll`. No
margins (R5). The tree lives in taffy so its per-node cache is the incremental layout. Boxes are
snapped to device pixels by the renderer's rule (R16).

**Damage / redraw:** two passes per frame (`ui/mod.rs:31-62`): layout only when the layout
generation moved (re-measuring only the dirty chain); paint rebuilds only elements marked dirty
(a resized box marks itself; a moved box marks its parent, F170), each element keeping its scene in
its own coordinates. A paint-only change (colour, condition look) skips layout; a scroll moves an
offset without repainting the inside. No partial-surface (scissored) presents: the whole frame is
re-encoded from retained scenes each frame (cost linear in primitives; ~1/4 us per primitive).

**DPI:** `src/units.rs`: `dp` x scale factor (x text scale for all but line widths), snapped; a
border under 2 dp is one device pixel at 150% (R16). The user's text-scale setting is NOT read
(text scale fixed at 1, `host/mod.rs:71`). Scale-factor change events are delivered (kind 9).

**Input:** `src/host/input.rs`: winit events become `RawEvent`s in dp with a 12-kind table
(pointer moved/pressed/released/left, scrolled, key pressed/released, text input, resized, scale
changed, close requested, focus changed), read by `gfx.vl` through three externs. Framework
input in `src/ui/input.rs`: hit testing through corners, clips and scroll offsets; bubbling;
`stop_event()`; implicit pointer capture on press; click counts; hover/press/focus conditions;
Tab order with `tab_index`. Ctrl/Super no longer types its letter (F182 host fix). No IME
composition.

**Accessibility:** `src/ui/access.rs` (1,129 lines) + `host/access.rs`: `accesskit =0.25.2`,
`accesskit_winit =0.34.2`; the tree is converted and DIFFED, published after a turn only while an
assistive tool listens; actions (focus, click, set value, selection, scroll) are replayed as
input. Always on (F178 ruling).

**Clipboard:** `src/host/clipboard.rs`: `arboard =3.7.0`, text only, on a host worker; an
in-memory clipboard for tests (`std::gfx::use_memory_clipboard`).

**The vilan side:** typed elements (`[element] fun row(): Row`, native-ui.md §12; lowering in the
analyzer, both backends); attributes are methods taking a value or a signal (`Bindable<T>`);
reactive children `each`/`each_by`/`each_values`/`when`/`swap` sharing std's `reconcile` with the
web UI (R9); element timers (`after`, `every`); window focus. Kit: `button`, `checkbox`,
`text_input`, `text_area` (multi-line, undo/redo, clipboard), `virtual_list`/`virtual_list_by`
(fixed and estimated row extents, rebase past 4,194,304 dp), roles for each. Icons:
`<icon of(..)/>` + the generated Lucide package (1,999 icons) at `vilan/packages/lucide`.

### B2. Status against the papers

**native-ui.md parts** (evidence: tracker F167's landing log, CHANGELOG `## v0.56.0`):

| Part | State | Evidence |
|---|---|---|
| P0 spike | DONE | native-ui.md §11 (branch `gfx-spike` a9c64577, throwaway) |
| R8 executor slice | DONE | F167 (a), exec-58 5a331875; changelog "R8 (native-ui.md)" |
| P1 `std::gfx` | DONE (Rust half gfx-p1 bb1b3022; vilan half gfx-s2 2a233e0a) | 7 crate goldens + 2 example goldens |
| P2 layout + elements | DONE (ui-p2 3ad94a38) | recorded rectangles + goldens at 100/150% |
| §12 typed elements (Q6) | DONE (elem-58 ef5fce0e) | changelog |
| P3 interaction | DONE (ui-p3 7ff2b699; ui-p3b reactive children af70ada8) | `ui_interaction.rs` (9 tests) |
| P4 kit | DONE ("P4's exit test ... is MET", F167 (i)) | `examples/ui-todo`, `ui-virtual-list` |
| P5 paths + icons | DONE (gfx-path S1-S4) | changelog S1/S2, S3, S4 entries |
| P5 text editing | DONE (text_area + undo; F180 perf open) | F167 (o) |
| P5 accessibility publishing | DONE on Linux only (AT-SPI); Windows/macOS not run | F178 |
| P6 browser through wasm | NOT STARTED (its own paper, not written) | F167 "LEFT" |

**gfx-path.md slices:** S1 the primitive DONE, S2 the vilan surface DONE, S3 the `icon` element
DONE, S4 the Lucide generator + package + full-set sweep DONE (all in v0.56.0's changelog; F175
carries the record). Follow-ups F183 (stroke overlap coverage), F184 (package distribution + check
cost) open.

**Rulings R1-R16:** all built as ruled except where the paper itself deferred: R6 typed elements
built; R8 main thread built; R10 roles built and now published; R14 overlap order built; R16 dp
snapping built; R12 "browser-capable by design" holds only as the WebGL2 limits choice (no
browser code exists).

**Explicitly NOT done** (code and tracker agree):

- Input method (IME) composition: none (`host/mod.rs:72`; native-ui.md §8 fence).
- Focus scopes (`focus-scope.md`): not built (F167).
- P6 browser: no paper.
- Multiple windows: "not refused, but built and proven for one" (`host/mod.rs:68-70`).
- The user's text-scale setting: not read.
- Group opacity (per-primitive only), crossing rounded clips approximated, no text gamma, no
  rotation, no clip-to-path, no dashes, no grid layout in the user vocabulary, no RTL anchors
  (physical Left/Right), mixed-style text runs in one `text` (P2 "not done"), no emoji golden.
- Owner decisions open (F167): optimizing wgpu/parley/swash in the dev profile; `Window::size()`
  0x0 when closed; `CloseRequested` cannot be vetoed; `Bindable` vs `MaybeSignal`; the event set
  and `stop_event` naming; condition semantics; test seams in the public surface (F182).
- Open F items on gfx/ui: F166 (webview slices), F167 (the umbrella), F178 (a11y verification),
  F179 (virtual list anchoring, O(n) inserts), F180 (text_area: 42 ms per key at 1,000 lines,
  0.49 s at 10,000), F181 (BSL-1.0 deps revisit), F182 (kit wiring follow-ups), F183, F184; plus
  M204 (perf).

### B3. Verification gaps and performance numbers

**What the tests exercise** (counted): 277 `#[test]` in `vilan-rt-gfx/src` (unit), plus
`vilan-rt-gfx/tests/golden.rs` 6, `paths.rs` 3, `window.rs` 1; compiler-side
`crates/vilan-cli/tests/gfx_window.rs` 2, `ui_screen.rs` 1, `ui_interaction.rs` 9. **13 PNG
goldens** (7 in `crates/vilan-rt-gfx/tests/golden/`: primitives at 100/125/150/200%, paths at
100/125/150%; 2 in `crates/vilan-cli/tests/gfx/` (counter 100/150); 4 in `crates/vilan-cli/tests/ui/`
(screen and icons at 100/150)) plus text listings (`*-check.txt`, `*-rects.txt`, 8 files). All
rendered on **Mesa lavapipe (software Vulkan)**, tolerance 1 per channel (and a pinned allowance,
N201, after CI's newer Mesa moved one pixel). Windows run under **xvfb** with input injected via
XTEST. CI job `gfx` (`.github/workflows/ci.yml:511-560`) runs all of this on GitHub-hosted
ubuntu with `VILAN_REQUIRE_GFX=1` (cannot pass by skipping). Lucide sweep: 1,999 icons against
tiny-skia (F183's numbers).

**Never run:** a real GPU (any vendor); Windows or macOS at run time (Windows is a clippy
cross-lint only, `scripts/ci-local.sh:322-326`; **macOS is not even cross-linted**); Wayland;
live drag-resize; a scale change while running; a real screen reader (Orca/NVDA/VoiceOver); the
AT-SPI test on CI (skips: the job does not install at-spi2-core, F178 (2)); keyboard/scroll/IME on
non-X11; a colour-emoji golden. native-ui.md §11.7 wrote out the Windows run that would settle
the GPU numbers; no record shows it was done.

**Performance numbers recorded** (all software Vulkan unless noted; "release" = optimized build):

- Spike (§11.3): stripped release 12.3 MB (7.5 MB size-optimised); cold start to first offscreen
  frame 115-219 ms (device creation 72-166 ms); first on-screen frame 105-286 ms; CPU per counter
  click: event 2 us, layout+reshape 33 us, scene 13-25 us, encode+submit 73-120 us; 10,000-row
  list 23 visible: scene build 101 us median; RSS ~140 MB (mostly the software driver).
- P1 (`lib.rs:75-79`): 1,000-primitive scene build ~13 us, encode+upload+submit ~225 us; through
  the vilan surface 20-45 us per 1,000 rectangles; idle CPU 0 ticks / 5 s; first frame 84-99 ms;
  example 12.75 MB stripped.
- P2/P3: example screen first layout 0.5-0.9 ms; 10,000 plain rows first frame 0.70 s; scroll step
  1 us layout / 0.87 ms paint / 2.3 ms draw.
- R9: 10,000 rows insert at top 14.1 ms layout / 7.9 ms paint; one-row change 3.5 / 0.8 ms.
- Virtual list (100,000 rows): first frame 0.37 ms layout; scroll step 87 us (125 us through vilan);
  insert at top 43 us (135 us through vilan).
- Paths: 240 cached icons 83 us vs 72 us for 240 rects; new 24 dp icon 2-48 us.
- text_area: 42 ms per key at 1,000 lines, 0.49 s at 10,000 (F180).
- No GPU-side frame times on real hardware; no memory number on real hardware.

### B4. Percentages

- **GPU rendering (the graphics layer): ~70%.** Basis: the v1 primitive set of native-ui.md §3.1
  is 9 of 9 built, with on-demand frames, atlas, paths and goldens (~90% of the features); but
  verification covers 1 of the ~5 targets that matter (Linux X11 on a software driver; not real
  GPUs, Windows, macOS, Wayland), and group opacity, gamma and rotation are open.
- **Native UI framework (std::ui + kit): ~75%.** Basis: parts P0-P5 of P0-P6 landed (6 of 7, P6
  being a separate browser paper); against a desktop app's needs, IME, focus scopes, multiple
  windows, text-scale, grid/RTL and platform verification are missing, and the long-text editor is
  slow (F180).
- **What a real app would hit first:** (1) any non-Latin text input (no IME); (2) running on
  Windows/macOS/a real GPU for the first time (never done); (3) build time: ~36-44 s clean debug
  per GUI project, every project from cold (no shared target), and slow debug rendering until the
  dev-profile ruling; (4) a second window, dialogs, menus, file pickers (none in std::gfx);
  (5) long documents in `text_area` (F180); (6) distributing icons outside a clone (F184).

---

## Part C. Native desktop apps

### C1. The webview shell (`crates/vilan-rt-webview`, `vilan/std/src/window.vl`)

**What works (slice 1, F166):** `Window::builder(url).title(..).size(w, h).open()` and
`Window::close()` (`window.vl`, 94 lines; two externs `__window_open`, `__window_close`). The
emitted `main` becomes `vilan_rt_webview::run(program_main)` (`vilan-rust/src/lib.rs:1087`):
the tao event loop owns the main thread, the vilan program (executor + in-process `std::http`
server) runs on a second thread with an 8 MiB stack (`crates/vilan-rt-webview/src/lib.rs:1-45`);
`open` is one proxy round trip; an open window is an `IoSource` keeping the loop alive; closing
the last window = graceful SIGTERM-style stop. The page reaches the server over the real loopback
socket (D8); there is NO JS-to-native IPC. Linux: wry inside tao's GTK vbox (X11 and Wayland);
macOS/Windows: wry on the native handle (`shell.rs:144-182`). The JS backend refuses
`std::window` by name. CI job `webview` runs `vilan/examples/desktop` in a real window under xvfb
(`crates/vilan-cli/tests/desktop_shell.rs`, 1 test). macOS and Windows: Windows cross-linted only,
never run; macOS not linted.

**Later slices the paper/tracker list (F166), none started:** deep links; menus; notifications;
secure token storage; tray; multiple windows; packaging and installers; porting kolt's Electron
shell; verification on real macOS and Windows; plus the `desktop` entry kind (manifest backend
key + run/build/workspace rules). Not even listed yet but needed by kolt (C3): IPC/bridge,
title-bar overlay, external-link handling, single instance, devtools, zoom, theme, error dialogs,
code signing, auto-update.

### C2. Packaging and distribution

Nothing exists. Grep of `crates/vilan-cli/src`, `crates/vilan-rust/src`, the webview and gfx
crates for installer / msi / dmg / app bundle / Info.plist / codesign / notarize / AppImage /
deb / `windows_subsystem`: no hits (only the toolchain's own installers in `upgrade.rs`). The
output is a cargo debug binary under `dist/native/<stem>/target/debug/`; release is a manual
`cargo build --release`; no app icon; no `#![windows_subsystem = "windows"]`, so a Windows GUI
build would also open a console window (inferred from the absence; not run). The Lucide package
is not shipped in any release artifact (F184).

### C3. Kolt's Electron desktop and what moving it would take

`/home/reed/code/kolt/src/desktop`: `main.mjs` 551 lines, `preload.cjs` 149, `page.vl` 136,
Electron 45.0.0 + electron-builder 26.15.3. Capabilities it uses (from the code):

| Capability | Electron API | Webview shell today | GPU UI today |
|---|---|---|---|
| Embedded server | `utilityProcess.fork(dist/server.mjs)` + port probe + log file | YES, better: in-process native server (M1 pending) | same server; UI would be rewritten |
| A window on the local origin, min size, background colour, app icon | `BrowserWindow` | partial: title + size only | partial: `std::gfx` window |
| Frameless window with title-bar overlay | Electron window options | no | no |
| Application menu driven from the page, accelerators | Electron menus over the bridge | no | no |
| A bridge between the page and native code (13 channels) | Electron context bridge and IPC | no IPC at all | n/a (no JS) |
| Secure token storage | the platform keychain through Electron | no | no |
| Browser sign-in handoff | a local listener plus the system browser | server side possible in vilan; no open-external | same |
| External links open in the system browser | `setWindowOpenHandler`, `will-navigate`, `shell.openExternal` | no | no |
| Single instance, focus on second launch | `requestSingleInstanceLock`, `second-instance` | no | no |
| System colour scheme + live changes | `nativeTheme` | no | no |
| Zoom | `webContents.setZoomFactor` | no | n/a |
| Devtools toggle (F12) | `webContents.toggleDevTools` | no | n/a |
| Device spelling dictionary to the page | over the bridge | needs IPC | n/a |
| Error dialogs | `dialog.showErrorBox` | no | no |
| App identity (AppUserModelID), per-profile data dirs | `app.setAppUserModelId`, `app.getPath/setPath` | no | no |
| Windows installer | electron-builder | no | no |

To move to the webview shell: M1 (the server native from kolt's tree), then at minimum an IPC
bridge (or route everything through the loopback server, which handles secrets/sign-in/spelling
but not menus, title bar, theme, zoom), menus, secure storage, open-external + navigation policy,
single instance, title-bar overlay, theme, error dialog, app identity/data dirs, an installer, and
real Windows/macOS runs. To move to std::ui: all of the above shell features PLUS rewriting kolt's
whole client (native-objective.md §2 already says kolt's client is NOT M3's first exhibit: its
editor uses contenteditable, the DOM Range and clipboard, ~130 browser bindings) and IME.

### C4. Percentages

- **Native desktop via the webview shell: ~15%.** Basis: slice 1 of the 10 F166 lists (window +
  page + in-process server, Linux-proven); against kolt's Electron capability table above, 1 of
  15 rows fully covered (the embedded server) and 1 partly (the window); 0 of 3 OSes verified
  beyond Linux; no packaging.
- **Native desktop via the GPU UI: ~25% as a platform for NEW apps, ~5% for kolt.** Basis: the UI
  framework itself is ~75% (B4), but every desktop-shell capability in the table (menus, dialogs,
  tray, secure storage, single instance, deep links, theme, installers, signing, auto-update,
  multiple windows) is absent, and IME is missing; for kolt the client rewrite dominates.

---

## Sources by claim (quick index)

- CLI native path: `crates/vilan-cli/src/native.rs` (747 lines).
- Manifest: `crates/vilan-rust/src/lib.rs:19279-19343`.
- Runtime materialization: `crates/vilan-embedded/src/lib.rs:46-110`.
- Executor: `crates/vilan-rt/src/executor.rs:1-80, 1921, 2488-2616`.
- Differential: `crates/vilan-cli/tests/native_differential.rs:1037-1290, 2826, 10316, 12407`.
- GPU crate overview: `crates/vilan-rt-gfx/src/lib.rs:1-117`; host: `src/host/mod.rs:1-75`;
  UI tree: `src/ui/mod.rs:1-80`; input table: `src/host/input.rs:1-30`; shader: `src/shader.wgsl`.
- CI: `.github/workflows/ci.yml:471-560`; `scripts/ci-local.sh:206-326`.
- Papers: `proposals/projects/vilan/proposal/native-objective.md`, `native-ui.md`, `gfx-path.md`,
  `native-apps.md`.
- Records: `proposals/scripts/integration/sweeps/order58/native-census.md`, `native-m1-report.md`,
  `kolt-patch-notes58.md`; tracker items F166, F167, F178-F185, B705, B727, B733, B750.
