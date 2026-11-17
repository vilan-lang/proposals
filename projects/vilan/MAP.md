# The map of Vilan

As of 2026-11-17, at v0.56.1 (main `12b8f86a`, next `6edafda5`).

This is a survey, not a plan. Five read-only surveys produced it (their full notes, with file and
line citations, are in [map/2026-11-17/](map/2026-11-17/)); the integrator verified the claims marked
"verified" and wrote the reading. Nothing here was built or run for the survey except where a
section says so.

**Since this was written** (same day): Homebrew is fixed and serves 0.56.1 (L25 keeps two code
follow-ups). The tracker rows section 11 calls stale were closed after checking each against the
code (B713, C13, N192, N193, E99, F175) or corrected (A185, M110, F1), the broken index row was
removed, and P6b has its own item, M207. The text below is left as found.

**How to read a percentage.** Every percentage has a basis in the same row, and a different basis
gives a different number. "Slices" counts the paper's planned pieces; "outcome" measures the goal
the paper set. Where the two disagree, both are given, and the gap between them is usually the
most useful fact on the page. A number marked *judgement* has no countable basis.

---

## 1. One screen

| Area | State | Complete | Basis | Biggest gap |
|---|---|---|---|---|
| Language on JavaScript | shipping, mature | n/a | 162-program golden corpus, 11,700 tests | 4 open JS miscompiles (B748, B749, B684, B685) |
| Native binaries, language core | works | ~95% | 134 of 142 platform-free corpus programs identical to node (4 refused by name, 4 lost to a full disk in that run) | about 11 shapes rustc refuses |
| Native binaries, servers and CLIs | works on a patched Kolt copy | ~85% | 404 of 421 non-browser std host bindings bound; Kolt's server built and measured | not from Kolt's own tree yet; no `--release`; no user `[extern]` for Rust |
| GPU rendering (`std::gfx`) | built, barely verified | ~70% | 9 of 9 planned primitives; 1 of ~5 targets ever run (Linux X11, software Vulkan) | never run on a real GPU, Windows or macOS |
| Native UI (`std::ui` + kit) | built through part P5 | ~75% | parts P0 to P5 of P0 to P6 | no input method composition, focus scopes, second window |
| Desktop app via the webview shell | slice 1 only | ~15% | 1 of ~10 listed slices; 1 of 15 capabilities Kolt's Electron shell uses | no bridge to the page, menus, storage, installer |
| Desktop app via the GPU UI | framework only | ~25% new apps, ~5% Kolt | *judgement* over the row above | no shell features at all; Kolt's client would be rewritten |
| Reactive lens migration | additive half landed, parked | 44% by slices, ~0% by adoption | 4 of 9 build slices; no std type and no Kolt file uses the lens | S3b refused twice for cost; nothing landed since 2026-11-09 |
| `std::fs` | complete on node | 48% native | 21 of 44 callables build natively | the `File` handle tier, `Reader`, the watcher |
| Incremental analysis | every slice built | 94% by slices, ~45% by outcome | 15 of 16 slices; leaf keystroke 1,090 ms against the 500 ms mandate | derived bodies re-walked every keystroke (M194) |
| Compiler performance | gated, flat | n/a | fixed-subject cost down 24% since v0.44, up 5% since v0.52 | 1% bump rows every order; Kolt check 5.3 s, 594 MB |
| Language server | mature | n/a | 14 capability groups advertised | over its latency budget; no signature help or workspace symbols |
| Debugger | works for JS | 0% native | VS Code adapter over node's inspector | nothing for native binaries |
| Test runner | minimal | n/a | one folder, no recursion, exit code only | unchanged since 2026-06-18 (E368) |
| Packages | path and git | registry 0% | manifest refuses a registry dependency | Lucide is not in any release artifact (F184) |
| Release channels | 5 of 6 work | 83% | npm, GitHub assets, install scripts, Open VSX and Marketplace current | **Homebrew broken since 2026-09-28** (verified) |
| Docs (the book) | current, gated | n/a | 71 pages, 725 compiled examples | README and the paper index are stale |

---

## 2. Repositories

| Repository | What it is | Last commit | Maintained |
|---|---|---|---|
| `vilan-lang/vilan` | compiler, std, docs, VS Code extension | 2026-11-17 | yes, daily |
| `vilan-lang/proposals` | papers, tracker, integration scripts and records | 2026-11-17 | yes, daily; its indexes are stale (section 11) |
| `vilan-lang/website` (local `vilan-website`) | the site and the playground, written in Vilan | 2026-11-03 | idle; still builds and deploys under 0.56.1 |
| `vilan-lang/vilan-lang.github.io` | the published site and book | 2026-11-17 (by the deploy) | automatic; the local clone is 3 commits behind |
| `vilan-lang/homebrew-vilan` | Homebrew tap | 2026-09-27 | **no: formula is v0.41.1, fifteen releases behind** |
| `vilan-lang/branding` (private) | brand masters | 2026-08-20 | dormant by nature |
| `vilan-playground` (local folder) | three scratch files, not a git repository | n/a | dead; the playground lives in `vilan-website` |
| `ReedSyllas/kolt` | the real program written in Vilan | 2026-11-16 | yes; 161 files, 85,048 lines of Vilan |

Nothing is published to crates.io. There are no GitHub issues; the tracker in `proposals` is the
only record.

---

## 3. The compiler

About 397,000 lines of Rust outside tests, in 19 crates.

| Crate | Lines | Role | Note |
|---|---|---|---|
| `vilan-core` | 232,148 | lexer, parser, analyzer, solver, JS emitter, const interpreter, formatter | `analyzer.rs` alone is 96,573 lines |
| `vilan-lsp` | 66,218 | language server | `document.rs` is 33,445 lines |
| `vilan-rust` | 19,859 | the Rust emitter (native backend) | one file of 19,380 lines |
| `vilan-cli` | 17,333 | the `vilan` binary, dev server, HMR | 112,679 lines of tests |
| `vilan-ide` | 9,910 | completion and quick fixes shared by server and playground | |
| `vilan-rt` | 17,690 | runtime every native program links | no third-party dependencies, no `unsafe` |
| `vilan-rt-gfx` | 27,868 | GPU layer under `std::gfx` and `std::ui` | outside the workspace, own lockfile and CI job |
| `vilan-rt-webview` | 615 | desktop window over the system webview | outside the workspace |
| `vilan-rt-{sqlite,crypto,signal,term,net,poll,image}` | 46 to 1,081 each | optional runtime halves | linked only when a program reaches them |
| `vilan-image`, `vilan-image-wasm` | 1,526 | one image codec for both backends | the wasm blob is committed and byte-checked |
| `vilan-embedded` | 715 | carries std and the runtime sources inside the binary | |
| `vilan-wasm` | 1,143 | the compiler as wasm for the playground | idle since 2026-10-03 |

**The pipeline:** lex and parse, macros, analysis (load, resolve by a constraint fixpoint, then
about 61 checking passes), post-analysis passes (hidden context parameters, async inference,
platform colouring, const evaluation, init order), then emission by one of two backends. There is
no shared lowered form between the two backends: each reads the analyzer's program directly, and
monomorphisation resolution exists twice (F26). That fact matters for section 13.

**Maintainability.** Seven files hold most of the code: `analyzer.rs` 96.6k lines,
`document.rs` 33.4k, `formatter.rs` 21.0k, `vilan-rust/lib.rs` 19.4k, `transformer.rs` 17.9k,
`parsing.rs` 17.4k, `vilan-lsp/main.rs` 12.1k. `analyzer.rs` took 356 commits since October.

### Language health

217 open tracker rows: B type system 55, M performance 43, N hygiene 26, A reactive 24, F native 24,
E tooling 23, the rest 22.

**Open miscompiles and silent wrong behaviour** (the correctness debt):

| Id | Backend | What goes wrong |
|---|---|---|
| B748 | JS | a copy of a plain enum changes when the original is written through `&mut` |
| B749 | JS | `if x` and `!x` over a `&bool` view are always true and always false |
| B684 | JS | a read-only `&` passed at a `&mut` parameter checks clean and writes through |
| B685 | JS | `opt.unwrap_or(&0) + 1` over `None` prints `0,01` |
| B679 | both differ | an `Option` reaching `any` through a generic body (may be fixed by M175; not confirmed) |
| B728 | native | `usize::max` and `min` go through `f64` and lose precision above 2^53 |
| B700 | both | an imported function silently wins over an imported module of the same name |
| B717 | native | lens cells are still alive at exit (a leak) |
| B702, B703, B704, A186 | std | rpc and mirror: a revoke sends no frame, acks never sent, one bad base drops a frame, a write outside a turn can dispose its own owner |

Eleven more items are shapes the Rust backend emits and rustc refuses (B699, B705, B708, B729, B730,
B732, B733, B736, B750, F150, F155). They fail loudly, so nothing wrong runs.

**Language features:** `dyn`, `lazy`, backed enums, typed elements: shipped. Const evaluation and
macros: built, with tails (G2, G9, G12, B614, B678). Concurrency: partial (J4, J5, J8: no public
cancel handle). Struct keys (B711) and the import foundation (A183): papers only.

---

## 4. Incremental analysis and compiler performance

### Incremental analysis: 94% by slices, about 45% by outcome

Every slice of the incremental paper landed (S0 to S7, Orders 47 to 52), and seven of eight of the
std-prefix paper. The missing one is **P6b**: make the saved std prefix the default for
`vilan check`. Nothing blocks it; it was scheduled for Order 56 and is tracked only inside M36.

What an edit costs today:

- One keystroke runs one analysis of the entry's world. The edited module, its importers and their
  import cycles are re-walked over a cached copy of the rest (1 to 14 modules on Kolt).
- Unchanged items are served from records. But every checking pass still sweeps about **126,000
  derived-body entities** per keystroke (M194). That is the named next lever, and the same item
  parks the lens migration.
- Hover, completion and colouring are answered from the last analysis without type checking.
- On the command line, two small caches persist by default (macro expansions, const sites). The
  saved std prefix is opt-in. No analysis of package code persists between runs.

The paper's goal that a keystroke in a body re-checks one function is **not met in effect**. No
incremental work has landed since 2026-11-04.

### Performance, measured at v0.56.1

| Measure | Value | Target |
|---|---|---|
| Kolt `vilan check` | 5.27 s CPU, 46.2 G instructions, 594 MB | no absolute target; x1.10 against the last release |
| Leaf keystroke to diagnostics | 1,090 ms | 1,500 interim; **500 is the mandate** |
| css keystroke | 1,220 ms | 1,300 |
| `model.vl` keystroke | 590 ms | 600 |
| Parse break | 1,930 ms | 2,500 |

**Trend.**

- On a fixed generated program the compiler's cost fell from 9.87 G instructions (v0.44) to 7.14 G
  (v0.52), then rose to 7.52 G: about 1% per order, through bump rows for std growth and features.
- Scaling with program size is linear (x2.00 per doubling; it was x2.99 at v0.43).
- The leaf keystroke was under 500 ms from v0.50 to v0.53 on a Kolt a third of today's size. Kolt
  tripled at v0.54 and the row has sat at about 1.1 s since.
- The checking phase is the most expensive phase in 12 of 14 release reports (31% now).

**Known cliffs in std at run time:** M197 (unsubscribe is quadratic: leaving Kolt's table page takes
69 to 102 s), M200 (a keyed store write is linear in the list: 5.3 s for one batch over 32,000
rows), M173, F180 (text area: 42 ms per key at 1,000 lines), F179.

**Two caveats on the perf exhibit**, both filed as N208.

- The perf harness still expects Kolt's old folder layout, so it measures a frozen copy of Kolt
  from before the reorganisation. Its editor-latency scenarios do not follow today's Kolt.
- The Kolt check row is not comparable between seals of different kinds. The same Kolt source
  reads about 33.7 G instructions at a seal across a breaking change (v0.54.0, v0.56.0) and about
  46.1 G at an ordinary one (v0.55.0, v0.56.1), under the same compiler. Within one seal both
  sides are measured the same way, so each seal's ratio stands; the absolute trend does not.
  I verified the sources are identical and have not found the cause.

---

## 5. Tooling

| Tool | State | Note |
|---|---|---|
| Language server | mature | advertises hover, definition, references, rename, symbols, formatting, completion, inlay hints, semantic tokens, code actions. Missing: signature help, workspace symbols, document highlight, go to implementation or type, call hierarchy, folding |
| Formatter | working | six open layout-edge items |
| Debugger | working, JS only | lives inside the VS Code extension; nothing for native |
| Test runner | minimal | one folder, no recursion, pass means exit 0, no filtering or per-test report |
| Dependencies | partial | path and git (pinned); no registry, no lockfile |
| Build hooks | working, gaps | a workspace member's own hook never runs, silently (G9) |
| Dev server and HMR | working, idle | last change 2026-10-13 |
| Wasm playground | working, idle | last change 2026-10-03 |
| VS Code extension | current | 13 old `.vsix` files sit in the folder |

---

## 6. The standard library

62 modules, 90 files, 65,908 lines, in three layers: a core for every host, a process layer (node
and native), and a browser layer. The full per-module table is in
[map/2026-11-17/02-std.md](map/2026-11-17/02-std.md).

| Group | Modules | JS | Native |
|---|---|---|---|
| Core types and collections | list, option, result, hash map and set, string, number, iterator, tuple, range, arena | works | works |
| Encoding | json, wire, binary, bytes, base64, url | works | works |
| Crypto and time | crypto, time, task | works | works, except `Debounce` |
| Servers | http, db, rpc server, ws, process, image, build | works | works |
| `std::fs` | 44 callables | works | **21 of 44**: reads, writes, directories work; the handle tier, `Reader` and the watcher are refused (F185) |
| Reactive | signals, cells, delta, store, transient, trace | works | works |
| Reactive lens | lens, lens::loaded | works | builds, leaks (B717); `loaded` refused |
| rpc and mirrors | rpc, rpc::mirror | works, three open protocol bugs | works |
| Browser UI | web::ui, dom, router, storage, style, dev | works | refused by design; the server-rendering twin works |
| Native UI | gfx, ui, ui::kit, window | refused by design | native only |
| `std::fetch`, `std::random` | HTTP client, random range | works | **refused, and nothing marks them as host-bound** |
| Leaves with thin coverage | jwt, markdown, memo, into | work | not determined; `std::into` is a 5-line trait nobody implements |

### The reactive lens migration: 44% by slices, about 0% by adoption

The paper (A185, ruled 2026-11-08) made the lens std's reactive core, to land in slices.

| Slice | What | State |
|---|---|---|
| S1 | the module, laws, pins | shipped v0.55.0 |
| S2 | read-only shape, set lens, a real rope | shipped v0.55.0 |
| S3 | the slim write path | shipped v0.55.0 |
| S5 | `lens::loaded`: loaded collections, optimistic overlay | shipped v0.55.0 |
| S3b | re-found `ListCell`, `HashMapCell`, `HashSetCell` on the lens | **refused twice for cost**: writes x1.48, heap x3.3, compile +21 to 29%. Parked on M194 |
| S4 | struct keys | waits on B711 (a paper) |
| S6 | the wire | not started |
| S7 | `Store` on the lens | not started |
| S8 | Kolt exhibits | not started |

The four slices that landed are the ones the paper calls additive: they add the lens beside the old
types. None of the six old reactive types sits on it. No other std file imports it. Kolt has 0 uses,
against 206 of `Store` and 451 of signals. The module is 4,316 lines that only its own tests and
docs use. The tracker row for A185 still reads "DRAFT, Q1-Q10 open".

This is the clearest case in the project of slices done and outcome not moved. It needs a decision:
pay for M194 and push S3b through, or say plainly that the lens stays an optional second system.

---

## 7. Native binaries (the Rust backend)

**How it works.** `vilan build --backend rust` writes a cargo project under `dist/native/<entry>/`
with the whole program in one `main.rs`, and runs plain `cargo build`. It is always a debug build;
there is no `--release` flag. Each project has its own `target` folder. The runtime crates are path
dependencies, from the checkout or from a copy unpacked out of the compiler binary.

**What the emitted Rust looks like.** A Vilan struct is a Rust struct, emitted once per
instantiation (the emitter monomorphises itself). Strings are `Rc<str>`. The shared cell is an `Rc`
with a borrow flag. Closures are `Rc<dyn Fn>`. Async is `async fn` on a single-threaded executor
with node's ordering. Panics unwind. The emitted code has one `unsafe` site.

**Coverage.**

- Language core: ~95%. The latest counted corpus sweep (2026-11-12) had 134 of 142 programs
  identical to node, 4 refused by name, 4 lost to a full disk.
- Server-side std: 404 of 421 host bindings outside the browser modules are bound (96%).
- That sweep is **not in CI**. Only the seal script runs it, and it asserts only that nothing is
  broken; a refusal passes.
- Kolt's server built natively on a patched copy on 2026-11-10: 14 MB idle against node's 78 MB,
  0.2x to 0.4x node's CPU per request. From Kolt's own tree it does not build yet: four JS-only
  bindings remain, and each now has a std replacement Kolt has not adopted.

**Missing.** A `--release` flag and a watch loop. User-written bindings for Rust (the ruled two-arm
`[extern(js = .., rust = ..)]` is not built, so any program with its own JS binding is refused). An
HTTP client (`std::fetch`). The `fs` handle tier. Packaging of any kind. A native debugger.

Build times are in section 13.

---

## 8. GPU rendering and the native UI

**What is built.** `std::gfx` over `vilan-rt-gfx`: wgpu 30 for the graphics API, winit for windows,
parley and swash for text, zeno for paths, taffy for layout, accesskit for accessibility, arboard
for the clipboard. On top, `std::ui`: typed elements, layout, hit testing, bubbling events, focus,
scroll, reactive children, timers. On top of that, `std::ui::kit`: button, checkbox, text input,
text area with undo, virtual list. Plus an `icon` element and Lucide's 1,999 icons as a package.

**Against the paper** (native-ui.md, parts P0 to P6): P0 to P5 are done. P6, the browser through
wasm, has no paper yet. The paths paper (gfx-path.md) is fully built.

**Not built:** input method composition (so no Chinese, Japanese or Korean input), focus scopes,
more than one window, the user's text-scale setting, group opacity, rotation, clip to a path,
right-to-left anchors, mixed styles inside one text run, dialogs, menus, file pickers.

**Verified on:** Linux, X11, Mesa's software Vulkan, under a virtual display. 277 unit tests and 13
image goldens.

**Never run:** a real GPU of any vendor. Windows or macOS at run time (Windows is linted only;
macOS is not even linted). Wayland. A real screen reader. The accessibility test on CI (it skips
there).

**Recorded numbers** (software rendering): first frame 84 to 99 ms; a 100,000-row virtual list
scrolls in 87 microseconds per step; the idle window uses no CPU; a stripped release binary is
about 12.8 MB.

The 70% and 75% in section 1 are mostly a verification discount. The features exist; almost none
of the platforms have seen them.

---

## 9. Native desktop apps

**The webview shell, ~15%.** One slice: a native program opens a window on its own in-process HTTP
server. That is all. There is no bridge between the page and native code. Nothing else the tracker
lists has started: menus, notifications, secure storage, tray, more windows, deep links, packaging.

Kolt's desktop today is Electron. It uses 15 capabilities. The shell covers one fully (the embedded
server) and one partly (the window). The other thirteen: a frameless window with a title-bar
overlay, an application menu, a 13-channel bridge, secure token storage, the browser sign-in
handoff, external links, single instance, the system colour scheme, zoom, devtools, the spelling
dictionary, error dialogs, app identity, and a Windows installer.

**The GPU UI, ~25% for a new app, ~5% for Kolt.** The framework is there. Every shell capability
above is absent from it too, and Kolt's client would be rewritten (its editor leans on
`contenteditable`, the DOM range and about 130 browser bindings).

**Packaging: nothing exists.** No installers, bundles, icons, signing or auto-update. A Windows GUI
build would also open a console window.

---

## 10. Infrastructure and CI

### Release channels

| Channel | State |
|---|---|
| GitHub release assets, install scripts | current (0.56.1) |
| npm | current |
| Open VSX and the VS Code Marketplace | current (Marketplace not independently queried) |
| Playground | current |
| **Homebrew** | **was broken; fixed later on 2026-11-17** (the secret was added and the tap now serves 0.56.1; the two code follow-ups in L25 remain). As found: the publish job reads a secret named `TAP_APP_CLIENT_ID`. The repository has `TAP_APP_ID`. The job skips its steps and reports green. The website advertises `brew install`. Fix: add the App's client id as that secret, then re-run the job for v0.56.1 (L25) |

Also: the nightly perf workflow's macOS job has been cancelled within two seconds on eight straight
nights (N209).

### CI today, measured over the last seven green runs on `next`

- A full run takes **23 to 24 minutes** when the runner is free. The median was 30; one run took
  112 minutes, 100 of them queued.
- The floor is the four Windows test shards: 19 to 23 minutes each.
- The two Linux shards take 8 minutes each but run **one after the other** on the single
  self-hosted runner, the only place they run. When it is down, runs hang: 14.5 hours on
  2026-11-17.
- The perf job takes 14 minutes and is not on the critical path.
- A release run takes 45 minutes, 30 of them re-running the test matrix CI just passed on the same
  commit.

Yesterday's two releases cost twelve full runs: five for v0.56.0 (the tip, the release commit, the
release workflow's gate, then main and next after the fold) and seven for v0.56.1.

### Ways to shorten it

Ordered by what they save against what they cost. None of these is built.

| # | Change | Saves | Cost and risk |
|---|---|---|---|
| 1 | **Skip a tree CI has already passed.** Key on the git tree hash, not the commit. A fold produces main and next with the tag's exact tree; a merge commit with no content change is the same case | 2 of 5 runs per release, and every such push | small: the existing `changes` job looks up a green run for the tree. The required `check` status still reports |
| 2 | **Let the release workflow trust CI on the same commit** instead of re-running the matrix | 30 minutes per release | this reverses a deliberate rule made after v0.32.0. The cut script already refuses a tag without green CI on that commit, so the gate would be checked, not skipped. Your call |
| 3 | **Remove the single runner as a failure point.** Fall back to GitHub's Linux runners when the self-hosted one is offline, and register a second runner instance so the two Linux shards run together | hours on a bad day; 8 minutes on a good one | hosted Linux is slower than your machine; the fallback needs a probe step |
| 4 | **Attack the Windows floor.** First measure how much of the 23 minutes is compiling and how much is tests. If compiling: build once and hand the test archive to four shards. If tests: more shards. L24 (a Windows runner on your machine) is open since October | up to 10 minutes per run | needs the measurement first |
| 5 | **One pre-push command for the cheap legs** (fmt, vilan-fmt, clippy, notices): about three minutes locally | a full cycle each time one of them would have failed. One of yesterday's red runs and two earlier in the order were exactly these | none; `scripts/ci-local.sh` has the legs |
| 6 | **Batch landings.** I wait for each run to finish before the next push. Merging several lanes locally and pushing once removes most of that waiting | most of my idle time on a busy day | a red run then names several merges; bisecting is local |
| 7 | Run the perf job only when the compiler or std changed | runner minutes, not wall time | low value: it is not on the critical path |

My recommendation: 1, 5 and 6 now (they are cheap and need no ruling), 3 next (the outage cost a
night), then measure for 4. Option 2 is yours to rule.

---

## 11. What is out of date

**Broken or silently wrong**

- Homebrew (section 10).
- The nightly macOS perf job (section 10).
- `std::fetch` and `std::random` look universal and are refused natively with no marker.
- `docs/guide/native.md` says a `Drop` resource is refused natively; two tests show it builds.
- The differential's platform list names `std::canvas`, which does not exist.
- The Rust emitter's refusal message still says "this is F1's slice S1b", shipped long ago.

**Tracker rows that contradict the code**

- Open but fixed: B713 (shipped v0.55.0), C13 (fixed 2026-09-17), N192, N193, E99. B715 and B737
  are fixed and wait on one decision each from you.
- M110 is open with every slice built. A185 reads "DRAFT" though ruled. F175 reads "open" though
  built. F1 says there is one backend.
- `INDEX.md` lines 133 to 138 hold a broken row with no id.
- Probably done: A138, I10, M199 (the remainder is M201).

**Papers that would mislead a reader**

- 11 papers say DRAFT or PROPOSED and shipped: auto-annotations, type-ascription,
  named-tuple-fields, payload-views, mirrored-store, r11-instantiations, std-prefix,
  reactive-pipeline, reactive-traits, build-hooks, filesystem.
- `reactive-layers` and `sql-value` say unbuilt; both shipped. `incremental-analysis` says draft;
  it is ruled and built.
- The paper index (`proposal/README.md`) is dated 2026-08-18 and omits 38 later papers. 55 papers
  have no status line at all.

**Documents**

- The vilan `README.md` says about 3,700 tests (there are about 11,700) and lists 5 crates
  (there are 19).
- The chronicle's "Now / Next / Later" section dates from 2026-09-01 and v0.40.0. The chronicle has
  no entries for Orders 56 and 57.
- `projects/README.md` says a restructure is pending that ran on 2026-08-28.

**Leftovers on disk**

- 56 worktrees in the vilan repository (187 GB). 55 of 58 local branches are merged into next; the
  three that are not are `e361`, `gfx-spike` and `path-58`.
- 8 branches in proposals are fully merged and can go. The six `kolt-*` branches hold nothing that
  is not on main, under other numbers; they must not be merged as they stand.
- Tracked clutter: 9 `REPORT-*` files at the vilan root, 12 `fold-*` files at the proposals root,
  about 100 seal logs, 13 old `.vsix` files.
- Two Dependabot pull requests, one open since 2026-10-06.

---

## 12. Your decision queue

28 items wait on you; 14 carry a recommendation. The full list with the question each asks is in
[map/2026-11-17/05-papers-tracker.md](map/2026-11-17/05-papers-tracker.md). The ones that block
work or have aged most:

| Id | Age | The question |
|---|---|---|
| B737 | 6 d | `std::ui` attributes on `MaybeSignal` or `Bindable` (rec: keep `Bindable`) |
| B715 | 8 d | review one caveat of a shipped fix |
| N207 | 1 d | where Kolt-side sessions file tracker items (rec: on main) |
| F167 | | optimise the GPU stack in the debug profile; veto of a window close; the event names |
| A175 | 22 d | rpc revoke: five questions |
| M174 | 22 d | JSON field defaults: five questions (rec: build) |
| F115 | 40 d | a closure capturing a binding under a `&mut` view: language rule or backend fix |
| F27 | 57 d | platform-specific code in user land: six questions |
| A106 | 61 d | widen the style prelude |
| A97 | 65 d | the wire's unsubscribe contract |
| M18, B183 | 77 d | bundle boundaries; the tuple comprehension's concrete arm |
| L20, L24 | 73 d, 39 d | the Windows test leg on your machine |
| A14, D5 | 122 d | the optimistic lifecycle question; the public traction plan |
| Order 56 | | six of its eleven owner questions are still open |

---

## 13. Primers

Three subjects you asked to get up to speed on, each tied to our code.

### 13.1 GPU rendering and graphics APIs, as we use them

**The layers, bottom up.**

1. **The GPU and its driver.** The driver speaks one or more native graphics APIs: Vulkan (Linux,
   Windows, Android), Direct3D 12 (Windows), Metal (Apple). OpenGL is the old fallback.
2. **wgpu.** A Rust library that offers one API, modelled on the WebGPU standard, and translates it
   to whichever native API the machine has. We program against wgpu only. This is why the same code
   is expected to run on all three systems, and also why "expected" is all we can say: each native
   API and driver has its own behaviour.
3. **winit.** Opens the operating system's window and delivers its events. wgpu draws into a
   *surface* tied to that window.

**The objects you meet in the code** (`crates/vilan-rt-gfx/src/gpu.rs`, `window.rs`):

- *Instance*: the entry point. *Adapter*: one physical or software GPU. *Device*: our session with
  it. *Queue*: where commands and data are submitted.
- *Surface*: the window's drawable. It has a pixel format and a present mode (we use vsync).
- *Texture*: an image on the GPU. *Buffer*: an array of bytes on the GPU.
- *Shader*: a small program the GPU runs, written in WGSL. A *vertex* shader places geometry; a
  *fragment* shader computes each pixel's colour.
- *Render pipeline*: a compiled pair of shaders plus blending and layout rules.
- *Render pass*: one drawing session into a texture, made of *draw calls*.

**How a 2D interface is drawn with this.** Almost every UI renderer of this kind, ours included,
draws everything as rectangles and lets the fragment shader do the shaping:

- **Instanced quads.** One unit rectangle is drawn N times in a single draw call, with a row of
  per-instance data each: position, size, colours, corner radii. Our renderer has two pipelines,
  both of this kind (`renderer.rs`, `shader.wgsl`, 293 lines).
- **Signed-distance functions.** For a rounded rectangle the shader computes, per pixel, the
  distance to the shape's edge, and turns it into coverage. Corners, borders and clipping come from
  the same formula with no extra geometry. A shadow is the same shape blurred analytically.
- **Text.** Three steps. *Shaping* turns a string into positioned glyphs (parley). *Rasterising*
  turns each glyph's outline into a small bitmap on the CPU (swash). The bitmaps are packed into
  one large texture, the *glyph atlas*; drawing text is then drawing textured rectangles that
  sample it (`text/`, `atlas/`).
- **Paths and icons.** There are three known ways: cut the shape into triangles (the `lyon`
  library), compute coverage on the GPU with compute shaders (`vello`), or rasterise a coverage
  mask on the CPU and draw it like a glyph. We do the third (zeno), so paths needed no new
  pipeline. Its limits follow from that choice: one colour per path, no rotation, masks cost memory
  at large sizes.
- **Order and blending.** Later shapes blend over earlier ones. Draw calls are expensive, so shapes
  are batched; ours batches by an overlap order (the approach the Zed editor's GPUI uses).
- **Frames on demand.** Nothing is drawn until something changed. An event runs the program, dirty
  elements are laid out (taffy) and repainted into retained *scenes*, the scenes are encoded into
  instance buffers, and one render pass presents the frame (`scene.rs`, `encode.rs`, `ui/mod.rs`).

**What a real GPU would test that our tests do not.** Driver and format differences, high-DPI
surfaces and scale changes at run time, present modes and tearing, device loss (sleep, driver
reset), memory on integrated graphics, and frame time on hardware. Our numbers all come from a
software renderer.

**Reading order in our code:** `gpu.rs`, `window.rs`, `scene.rs`, `encode.rs`, `renderer.rs`,
`shader.wgsl`, `atlas/`, `text/`, `path/`, then `ui/mod.rs`.

**Outside reading**, from my own knowledge rather than a search today: the "Learn Wgpu" tutorial
for the objects above; the WebGPU specification's overview for the model; Zed's write-up on
rendering interfaces with the GPU for the quad-and-SDF approach we follow; Raph Levien's writing on
2D rendering for the path question; Inigo Quilez's articles for distance functions.

### 13.2 rustc caching and native compile times

**Where the time goes today.** All recorded, none recent:

| Build | Time |
|---|---|
| Small program | 0.35 s to emit, about 0.5 to 1 s in cargo |
| Kolt's server (one `main.rs`, 36,632 lines) | about 15 s cold and 3 s warm in debug; 37 to 71 s in release |
| The GPU stack (300 packages) | 25 to 37 s clean debug, 42 to 54 s clean release |
| A small GUI app from cold | 36 to 44 s, **and every project pays it again** |

Never measured: a one-line edit of a large program, link time alone, any build on Windows or macOS,
and how the program crate's time splits between rustc's front end and code generation.

**How rustc and cargo cache.**

- Cargo compiles one *crate* at a time and keeps the results in a `target` folder. An unchanged
  dependency is not rebuilt, **within that folder**.
- Inside one crate, rustc's *incremental* mode reuses work between builds, but it still re-runs type
  checking and borrow checking for the whole crate. So one huge crate is the worst shape for it.
- Nothing is shared between `target` folders unless you arrange it.

**The levers, cheapest first.** None is built or measured here.

1. **One shared `target` folder for all native builds.** Today each project compiles the runtime,
   and for a GUI app the 300-package GPU stack, from cold. Pointing every build at one folder under
   `~/.vilan` makes that a once-per-machine cost. Our own differential tests already do this.
   Risks: cargo locks the folder, so two builds queue; binaries need distinct names.
2. **Tune the generated debug profile.** Compile the GPU dependencies optimised even in debug (your
   open ruling in F167: debug rendering is 5 to 10 times slower without it), and turn debug
   information down or off for dependencies, which shortens both compiling and linking.
3. **Add `--release` and pin the Rust toolchain in the generated project.** Not a speed lever, but
   today's builds use whatever toolchain is installed, which silently discards every cache when it
   changes.
4. **Split the program into several crates.** Kolt's server is one crate, so any edit re-checks all
   36,632 lines. Emitting std's instantiations as one crate and the program as another, or one
   crate per Vilan package, lets cargo skip the unchanged parts. Harder than it sounds: Vilan
   modules may import each other in cycles, and crates may not.
5. **Ship the GPU stack prebuilt.** Rust has no stable binary interface, so a prebuilt Rust library
   only works with the exact compiler that made it. The workable form is a C-interface dynamic
   library. Our program already talks to the GPU crate through a narrow set of about 85 host
   functions, so the boundary is plausible. This would cut a GUI app's cold build to that of a
   plain program. It is a real design job and adds a library to ship per platform.
6. **sccache.** Caches compiler invocations across folders and machines. Helps CI and first builds;
   does nothing for incremental rebuilds or linking.
7. **A faster linker.** rustc already uses lld by default on Linux x86_64 since 1.90. `mold` and
   `wild` are faster still. Measure the link share before spending on this; Windows is the likely
   place it matters.
8. **Cranelift as rustc's code generator for debug builds.** As of what I found today it is still a
   nightly-only preview, with reported gains from about 5% to 20% of total build time. It would
   mean asking users for a nightly toolchain. Worth one measurement, not a plan.

Also on the Rust project's 2026 list and not stable: a parallel front end, and a cache shared
across workspaces in cargo itself. Neither can be relied on yet.

**The first thing to do is measure.** `cargo build --timings` on Kolt's server and on a GUI example
shows which crates and which phases cost what. That one afternoon decides between levers 1, 4
and 5.

### 13.3 Is an LLVM backend viable?

Viable in principle. I think it is the wrong next step, and that a smaller step toward it is
worth taking anyway.

**What rustc gives us today for free.** A direct backend would have to replace each of these:

- async state machines (we emit `async fn` and rustc builds them; the JS backend leans on
  JavaScript's own async the same way, so we have never written this transform);
- drop glue and unwinding (the runtime uses `catch_unwind` at 12 sites);
- trait-object tables, hash maps, string formatting, UTF-8;
- the runtime itself: 17,690 lines of `vilan-rt` and 27,868 of `vilan-rt-gfx`, in Rust, called
  through generic Rust types. Generics cannot cross a C interface, so reference counting, lists,
  options and strings would need our own layout and our own code.

**What we would gain.**

- No rustc front end over a 36,632-line file. This is probably where most of the debug build time
  goes, but that is the unmeasured split from 13.2.
- No borrow-checker friction. Eleven open defects are exactly "rustc refuses what we emitted".
- Control over debug information, which a native debugger needs.

**Why LLVM in particular is a poor fit now.**

- LLVM's strength is optimised code. Release builds already get it, through rustc. Its unoptimised
  mode is not fast, and compile time is the complaint.
- It is a heavy dependency to ship and to pin across three systems.
- If we want fast debug builds from our own backend, Cranelift is the natural choice: written in
  Rust, built for compile speed, code about as good as unoptimised LLVM. The project's own old
  ranking (2026-07) said the same: Cranelift for fast builds, LLVM for peak speed, both far off.

**The prerequisite either way.** Neither backend shares a lowered form with the other; each reads
the analyzer's output directly (F26). That old ruling still looks right: a third backend should
wait for a shared lowered form with explicit copies, drops and reference counts. That form pays
back before any new backend exists. It removes the duplicated monomorphisation, and it lets us
emit simpler Rust, which is where the rustc refusals come from.

**My reading, in order:**

1. Measure where native build time goes (13.2).
2. Pull the cheap levers: shared target, debug profile, crate split.
3. Build the shared lowered form when the Rust emitter next needs deep work.
4. Only then weigh a Cranelift backend for debug builds, keeping rustc for release.

An LLVM backend comes after all four, if ever.

---

## 14. A suggested order of attention

This is my recommendation; the priorities are yours.

1. **Correctness.** Four open JS miscompiles (B748, B749, B684, B685) and the three mirror protocol
   bugs. Small items, and each one is a program doing the wrong thing silently.
2. **Clean the records.** One clerk pass closes the stale rows and marks the misleading papers.
   Until then the tracker overstates what is open and understates what is decided.
3. **Fix what is silently broken.** Homebrew, the macOS perf job, the CI changes numbered 1, 5 and 6
   in section 10.
4. **Decide the desktop route.** The webview shell is 15% and the short road for Kolt; the GPU UI
   is the long one. They share almost no remaining work. Finishing the native server from Kolt's
   own tree (four adoptions in Kolt) serves both.
5. **Run the GPU UI on real hardware once**, on Windows and macOS, before building more on it.
6. **Measure native build time**, then pull the cheap levers.
7. **Decide the lens.** Fund M194 (it also moves the keystroke row) and push S3b through, or stop.
8. **Incremental analysis:** M194, then P6b, which is unblocked and unscheduled.

---

## Sources

The five survey files in [map/2026-11-17/](map/2026-11-17/) carry the evidence: file paths, line
numbers and the commands behind each count. Known corrections to them are listed in that folder's
README. External facts in section 13.2 (Cranelift's status, lld as the default linker, cargo's
cross-workspace cache, the parallel front end) come from a web search on 2026-11-17 of the Rust
project's 2026 goals pages and blog; they are roadmap statements, not release notes, and should be
rechecked before a decision rests on them:

- <https://rust-lang.github.io/rust-project-goals/2026/roadmap-fast-builds.html>
- <https://rust-lang.github.io/rust-project-goals/2026/improve-cg_clif-performance.html>
- <https://rust-lang.github.io/rust-project-goals/2026/cargo-cross-workspace-cache.html>
- <https://doc.rust-lang.org/cargo/guide/build-performance.html>
- <https://blog.rust-lang.org/2025/09/10/rust-compiler-performance-survey-2025-results>
