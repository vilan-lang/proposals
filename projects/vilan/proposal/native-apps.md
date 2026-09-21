# Native apps — an emit-Rust backend, a desktop platform, and a third `std::ui`

Tracker **F1** (filed 2026-09-14 as a DISCUSSION with owner questions; RULED to a paper at
Order 36's GO, **R10**: "the paper and its probe ASSUME the emit-Rust backend and desktop
first, present the alternatives as costed rejections, keep the DOM-shaped `View`, and answer
the four owner questions themselves"). Written by lane `paper-native-36` of Order 36 on vilan
`next` @`9b22ec36`; every probe is `vilan 0.40.0 (9b22ec364)` and `rustc/cargo 1.90.0`.
**No compiler change lands from this lane, and none is in scope until this paper is ruled.**

Related: **C14** (`signal-cell-representation.md`, the sibling paper — this paper's second
pillar and its first dependency), **C1**, **C12** (a captured view of a dead local: memory-safe
only because JS boxes and traces it — "under any non-GC backend this is a use-after-free",
`lifetimes.md` §2.2), **A95** (`style-conditions.md` — the condition model the native style
resolver consumes), `platform-model.md`, `platform-coloring.md`, `ssr.md` (the second-layer
precedent), `lifetimes.md` §3/§7, `destruction.md` §10, `capture-clones.md`, `canvas.md` §6,
spec `docs/spec/memory.md` §6.1/§6.9 and `docs/spec/platform.md`.

---

## 0. What the probes changed about the plan

1. **The backend probe is DONE and it built.** §2. A 62-line vilan program with two structs, a
   `List`, a bare-`self` method, a closure capturing a binding, a `SignalCell` and a subscriber
   was hand-translated to Rust twice (once per C14 representation), compiled with the host's
   `cargo 1.90.0`, and run. Both binaries reproduce the vilan program's output. F1's "cheap
   first move" is no longer prospective.

2. **`Target` no longer exists.** F1 says "the build model is `Target` = `Backend` +
   `Platform`". As built, they are two independent values threaded separately
   (`crates/vilan-core/src/target.rs`, 442 lines): `Backend { Js }` and
   `Platform { Node{version}, Deno{version}, Bun{version}, Browser, None }`. `Backend` also has
   no `ecma` field and `Layer` has no `backend` field — `platform-model.md` §11 Q1's
   `backend = ["wasm"]` on a layer was never built. A native *backend* and a native *platform*
   are therefore two separate changes that must land together, and §5-S2 says exactly where.

3. **`target.rs`'s own module doc claims the edit is one file. It is not, any more.** §5-S2
   enumerates **eleven** registration sites across six crates, of which three are structurally
   two-valued and must become N-valued: `lib.rs`'s `infer_platform` (binary: browser or
   not-browser), `std_twin_parity.rs`'s `enum Side { BrowserOnly, ProcessOnly }`, and
   `ssr_differential.rs`'s two-leg byte-equality harness. That is the real size of "a minimal
   `native` platform", and it is bigger than the item implies.

4. **`std::ui` is the ONLY twinned module, and there is no rule for a third layer.**
   `std_twin_parity.rs:74`: `const TWINNED_MODULES: &[&str] = &["ui"]`. The only forward
   reference in the whole proposal corpus is `platform-coloring.md:329` — "wasm as a third
   *color*", not a third *implementation*. The three-layer rule does not exist; §5-S2 and §6.2
   invent it, and §9 Q3 asks for it to be ruled.

5. **Nothing in the crates anticipates a native target.** `grep -ni "native|desktop|wgpu|scene
   tree|retained"` over `target.rs`, `manifest.rs`, `platform_color.rs`: one unrelated false
   positive. The only `native` identifier in std is `native_map.vl`, an internal `Map` building
   block. The proposal corpus has nine mentions and every one is about a *backend*
   (`p6-followups.md:157`, `lifetimes.md:528`, `view-invalidation.md:117`,
   `platform-model.md:270`), never a platform and never a UI layer.

---

## 1. The answer up front, and the owner's four questions

**Emit Rust. Desktop first. Keep the DOM-shaped `View`, as a third `std::ui` twin. Client-only
first, with the rpc runtime in-process as a later slice.** R10 ruled these as assumptions; the
paper's job is to give them reasons, and it does, in §2 (the probe), §4 (the costed rejections)
and §5 (the slice order). The four questions, answered:

**Q-A — which backend?** *Rust.* The probe compiled in 1.5 s of CPU and the translation is
mechanical: vilan's affine moves, loans and `own` map onto Rust's ownership almost
one-for-one, rustc does codegen and LLVM does optimisation, and the render stack the third
pillar needs — wgpu, a vello-class 2D renderer, cosmic-text, taffy, winit — is *already Rust*
and is reachable as a dependency rather than as a port. §4 prices C, wasm-in-a-host and an
interpreter and rejects all three. The probe's honest caveat is §2.4's R-4: the emitted Rust
does not inherit vilan's static guarantees, so interior mutability is `RefCell` and its
failure mode is a runtime panic, not a compile error.

**Q-B — desktop or mobile first?** *Desktop.* One window system to bring up, no store review,
no signing arc, no cross-compilation in the first slice, and the exit test is a binary the
developer runs on the machine they wrote it on. Mobile changes the windowing layer and nothing
above it, so it costs a slice later rather than a redesign.

**Q-C — a new retained-tree API, or the DOM-shaped `View`?** *The `View`.* `ssr.md` is the
precedent and it is a proven one: "A second `ui.vl` in std's process layer, **same public
surface**, over a string tree." The whole application estate — kolt's ~4,060 lines outside the
icon library, every example, every doc fence — is written against `view("div").child(..)
.bind_text(..).styled(..)`, and a new API would fork it. §4.4 prices the alternative honestly:
it is not obviously worse *as a design*, and it is worse *as a migration*, which is the
question actually being asked. The cost of the choice is §6.2's: a third twin, and a twin-parity
gate that is structurally two-valued today.

**Q-D — client-only first, or the full stack?** *Client-only first.* A native app that renders
and takes input is a complete thing; a native app that also *is* a server is two things. The
rpc runtime moving in-process is a real and attractive slice (§5-S6) — a desktop app whose
`[rpc]` handlers run in the same process over a `duplex_pair()` transport, which `rpc.vl`
already has — and it is strictly after a window exists. Nothing in the client-only slices
forecloses it.

---

## 2. The PROBE — done, built, recorded

### 2.1 What was translated

`native-apps-probe/board.vl` (beside this paper), 62 lines, chosen to cover exactly F1's list plus
the two things the list omits (a bare-`self` loan, and a closure capturing a mutable binding):

```vilan
struct Todo { id: i32, title: str, done: bool }
struct Board { name: str, todos: List<Todo> }
impl Board { fun new(name: str): Board; fun add(&mut self, todo: Todo); fun open(self): i32 }

fun main() {
    mut board = Board::new("inbox");                 // struct, str, List
    …
    mut snapshot = board.todos;                      // rule 1: a copy
    snapshot.push(Todo { … });
    print(board.todos.len()); print(snapshot.len()); // 2, 3

    let count: SignalCell<i32> = SignalCell::new(board.open());
    mut seen: List<i32> = [];
    let owner = Owner::new();
    let _sub = owner.take(count.sub(|value| { seen.push(value); }));   // §6.9 capture
    board.add(…); count.set(board.open());
    print(seen.len());                               // 2
    owner.dispose(); count.set(99);
    print(seen.len()); print(count.get());           // 2, 99
}
```

Ground truth from the shipped toolchain, and the emitted JS for reference:

```
$ vilan run board.vl                     -> 2 3 2 2 99
$ vilan build board.vl                   -> board.mjs, 267 lines / 5,633 bytes
```

### 2.2 The result: BOTH translations BUILT and RAN

| | `probe_rc.rs` (C14 rep. (a)) | `probe_arena.rs` (C14 rep. (b)) |
|---|---|---|
| `cargo build` | **clean** (after one fix, R-1 below) | **clean** |
| output | `2 3 2 2 99` — identical to vilan | `2 3 2` … `after-dispose-get=None` |
| extra measured | `Weak::upgrade() -> None` deterministic; weak count 2→1 at dispose | handle 16 B `Copy`, owner 8 B, root partition survives |
| release binary | 475,232 B | 493,056 B |

Clean `--release` build of both binaries: **1.15 s user + 0.35 s sys** (`time cargo build
--release`, warm toolchain, cold target dir). That is the number that matters for the
developer's inner loop, and it is why §4.1 rejects emitting C: the Rust toolchain is already on
the machine of everyone who builds vilan.

### 2.3 The runtime the emitter needs — enumerated

Read off the emitted `board.mjs` and off the two translations. Nothing here is speculative;
each row is something the probe either used or had to hand-write.

**(1) Value representations.** The emitted JS is the baseline to replace:

| vilan | JS today | native |
|---|---|---|
| `struct` / tuple | a positional JS **array** — `add(board, [ 1, "write the paper", false ])` | a Rust struct, `#[derive(Clone)]` |
| `enum` | a tagged positional array — `Option` is `[0, v]` / `[1]` | a Rust enum; `Option`/`Result` map onto Rust's |
| `bool` | a numeric enum (`analyzer.rs`'s `bool_enum_id`) | `bool` |
| `str` | a JS string, value-copied | **`Rc<str>`** — rule 1 copies at every binding; a `String` clone per binding is the single largest avoidable cost |
| `List<T>` | a JS array; copy = `__clone` | `Vec<T>`; copy = `.clone()`, elided at last use |
| `Map`/`Set` | JS `Map`/`Set` keyed by `__hash` (`JSON.stringify` for objects) | `HashMap`/`HashSet` over the `CanonicalHash`/`HashEq` intrinsics — the canonicalisation already exists |
| `NativeMap<V>` | a JS `Map` keyed by hash | the same |
| `Shared<T>` | `{ v: value }` | **C14's answer** — this paper's first dependency |
| `i32`/`u8`/`f64` | one JS number | real widths (a gain) |
| `i53`/`u53` | one JS number | 53-bit types are a *JS* shape; native needs a ruling (§9 Q5) |

**(2) The 52 intrinsics** (`analyzer.rs:47073`), each needing a native body: 12 `Str*`, 6
`List*`, 8 `Map*`, 4 `Set*`, 4 `Shared*`, 5 `Json*`, `CanonicalHash`/`HashEq`, `Scan`,
`ParseI32`/`ParseF64`/`TryParseJson`, `RandomInt`/`RandomFloat`, `Args`, `Env`,
`OptionTake`/`OptionReplace`. One is browser-only and excluded: `QuerySelectorAll`.

**(3) ~35 runtime helpers** (`transformer.rs`'s `RESERVED_NAMES`, `:10776`+): `__clone`, `__hash`, `__guarded`,
`__with_finally`, `__scan`, `__list_get`/`__list_pop`/`__list_sort_by`,
`__option_take`/`__option_replace`, `__map_get`/`__map_keys`/`__map_values`, `__shared_new`,
`__parse_i32`/`__parse_f64`, `__random_int`/`__random_float`, `__args`, `__env`, `__sleep`,
`__timer`/`__Timer`, `__task`/`__Task`, `__nursery_new`/`__nursery_new_detached`/
`__nursery_run`/`__nursery_of`/`__nursery_is_cancel`/`__Nursery`. Browser-only and excluded:
`__hmr_active` and the five `__chunk_*`.

**(4) Closures.** Boxed and counted: **`Rc<dyn Fn(..)>`**, not `Box<dyn Fn>` and not a generic
— finding R-1. And per spec §6.9 a closure captures **bindings**, so every mutably-captured
binding is a shared cell — finding R-2, and the reason C14 is larger than `SignalCell`.

**(5) Panics and unwinding.** `panic(msg)` → `panic!`; `__guarded` → `catch_unwind` +
payload downcast (both probes implement it); `__with_finally` → a drop guard.
`destruction.md:379` already anticipates the semantics ("a native backend would abort, also").

**(6) Rule 1's copies.** The emitter already knows exactly where: `let snapshot =
__clone(board[1]);` in the emitted JS is the one copy in the probe the last-use pass cannot
elide, and the Rust translation puts `.clone()` at precisely that line and nowhere else.
`lifetimes.md` §3 measures the workload this decides: **12,292 compiler-inserted deep copies
per render of the website's `/`, 50.1 % of 24,555 allocations**, and §7 makes the whole
Perceus/reuse question turn on it.

**(7) Async — the largest unlisted item.** `Task<T>` is `[extern("Promise.all")]`; `Nursery`
is five host helpers; `sleep`/`fetch` bridge `AbortSignal`. Native needs an executor and a
cancellation primitive, and nothing in std names one. **This is the biggest single piece of
runtime the emitter needs and F1's item does not list it.** §9 Q4.

**(8) Free.** Context threading compiles away to hidden parameters (`contexts.md`); generics
are monomorphised before emission; `const` is evaluated by the interpreter. Nothing of the
three costs a runtime.

### 2.4 Four findings from the probe

- **R-1 — a closure parameter that is both stored and called must be boxed at the boundary.**
  `sub` stores its observer in the subscriber list and calls it once immediately; `impl Fn(T)`
  is moved by the first use and fails with `E0382` (reproduced, then fixed by
  `Rc<dyn Fn(T)>`). This is `destruction.md` §10's "counted closure environments" bullet
  arriving from rustc.
- **R-2 — spec §6.9 forces a shared cell per mutably-captured binding.** `seen` is pushed to
  inside the closure and read outside; both translations need `Rc<RefCell<Vec<i32>>>`. The
  emitted JS shows the same thing from the other side: `seen.push(value)` inside the arrow is a
  plain lexical capture of the array. The cell-representation question is the representation of
  **every captured mutable binding**, not only of `Shared`.
- **R-3 — the reactive back edge is real in Rust and one `Weak` fixes it.** Under (a), the
  notify closure must capture a weak cell or the cell's own subscriber list keeps it alive.
  Measured: the weak count falls 2→1 at `dispose`, and `upgrade()` is `None` after the last
  strong handle drops.
- **R-4 — emitted Rust does not inherit vilan's static guarantees, and the residue is
  `RefCell`.** vilan's rule 4 is checked by *vilan*; rustc sees only the emitted code, which
  aliases freely by design. So every cell access is a `RefCell` borrow, and `notify` had to
  clone the subscriber list out before walking it — holding a borrow across an arbitrary
  observer closure would panic. **The honest statement: a native backend converts a class of
  vilan-checked property into a runtime check whose failure is a panic.** The alternatives are
  `unsafe` with a soundness argument, or an IR that is not Rust source. §9 Q1.

---

## 3. What exists today, precisely

**The build model.** `Backend` (`target.rs:26`) is `enum { Js }`. `Platform` (`:52`) is
`Node{version} | Deno{version} | Bun{version} | Browser | None`, with fixed supported
versions (`NODE_LTS = 24`, `DENO_CURRENT = 2`, `BUN_CURRENT = 1`) and a hard error on any
other. `PlatformPattern` (`:239`) is the manifest-side wildcard; the one family, `@process`,
is hardcoded in `PlatformPattern::parse` (`:255`) to the three process runtimes.

**The layers.** `[library.layer.<name>]` takes exactly two keys, `root` (default
`src/<name>`) and `platform` (required). std's entire declaration is five lines:

```toml
[library.layer.process]
platform = ["@process"]    # fs, http, process

[library.layer.browser]
platform = ["browser"]     # dom, ui, storage
```

`browser/ui.vl` and `process/ui.vl` are twins *purely by co-name*. `Library::layer` is a
`BTreeMap`, so layer order is alphabetical — a layer named `native` sorts first, ahead of
both, which matters for specificity ties (`matching_layers` stable-sorts by descending
specificity and keeps declaration order on a tie).

**The coloring.** `platform_color.rs::check(program, platform, graph)` colors from the
*definition site*, not the import: a source in a layer seeds a requirement labelled
``the `process` layer of `std` ``, and the requirement propagates along the same call-graph
edges emission uses, so *emitted ⊆ admitted* by construction. The refusal, pinned verbatim:

```
`env` requires the `process` layer of `std` and cannot run on `browser`
  reachable from the entry: main → cache → env (std::process)
```

**What a native entry would be forbidden from reaching falls out of file placement alone** —
`canvas.md` §6 states the principle: "there is no process twin, and none is proposed. This is
not a special case — it's the existing pattern for every module under `std/src/browser/` that
has no counterpart under `std/src/process/`." So `std::dom`, `std::canvas`, `std::router`,
`std::storage`, `std::dev` refuse on native by having no native file; `std::fetch`,
`std::rpc`, `std::reactive`, `std::style`, `std::json`, `std::time` are base-layer and are
reachable; `std::fs`/`std::http`/`std::db` are reachable iff `native` joins `@process`.

**The second-layer precedent, and its price.** `ssr.md` §2: "A second `ui.vl` in std's process
layer, **same public surface**, over a string tree." §5 names the standing risk: "**any new
`bind_*` must land in both layers or the pin fails**." Two gates hold it —
`std_twin_parity.rs` (names, with a 25-entry `ALLOWED_DIVERGENCES` honest in both directions)
and `ssr_differential.rs` (bytes: one `component.vl` compiled twice, the DOM stub serialised
with the process twin's escaping rules, so "structural equality is byte equality").

---

## 4. The alternatives, costed and rejected

### 4.1 Emit C — rejected
*What it buys:* the smallest possible runtime dependency, every platform's system compiler,
trivially embeddable.
*What it costs:* every guarantee is hand-rolled. No ownership model to map onto (§2.3's rule-1
copies become explicit `memcpy` and explicit frees with no checker behind them), no `Option`,
no tagged unions with exhaustiveness, no `Rc`/`Weak`, no `catch_unwind` for `__guarded`, no
`Drop` for `__with_finally`, no `HashMap`, no UTF-8 string type. And the render stack does not
exist: wgpu, vello, cosmic-text, taffy and winit are Rust, so emitting C means either
re-implementing them or writing and maintaining an FFI surface for all five.
*Verdict:* strictly more work than Rust for strictly fewer guarantees. Rejected.

### 4.2 wasm in a host — rejected as the FIRST target, kept as a later one
*What it buys:* one artefact, a sandbox, an existing story for the browser.
*What it costs:* it does not answer the question F1 asks. A wasm module in a host still needs
that host to own the window, the GPU and the event loop; "a native app" then means "a native
*host* plus a wasm payload", and the host is the part that is not written. Component-model
interop for a DOM-shaped `View` is a large surface of its own. `platform-model.md:270` lists
the wasm *backend* as deferred and `platform-coloring.md:329` lists wasm as a future third
*color*; neither is this.
*Verdict:* a legitimate second backend, after Rust, reusing everything §5-S1 builds. Rejected
as first.

### 4.3 Ship the interpreter — rejected
vilan already has an interpreter (`crates/vilan-core/src/interpreter.rs`) — for the const pass,
over the *emitted JS AST*, with `Value::{Str(Rc<str>), Array(Rc<RefCell<Vec>>), Object, Closure}`
and an `Env = Rc<RefCell<Scope>>`. Shipping it as a runtime means shipping an
`Rc<RefCell<..>>`-per-value tree walker whose own leak history is `leak-soak.md` §7.7's
**+1,523.9 KiB per analysis**, at an order of magnitude below JIT'd V8 on the workload
`lifetimes.md` §3 measured (24,555 allocations per render). It also fixes nothing: the GPU,
the window and the event loop still have to be written in Rust underneath it.
*Verdict:* rejected. It is a compiler component and should stay one.

### 4.4 A new retained-tree API instead of the DOM-shaped `View` — rejected, with respect
*What it buys:* a surface designed for a scene graph rather than adapted to one — no
`innerHTML`-shaped operations, no attribute strings, no CSS cascade to emulate, and a chance to
make the tree diff-free by construction.
*What it costs:* the entire application estate. kolt is ~4,060 lines outside its icon library
and essentially all of its UI is `view(tag)` chains; every doc fence, every example and both
existing `ui` twins are written against that surface, and `std_twin_parity` exists precisely to
keep one surface true across implementations. A second surface forks the ecosystem at the point
where it has one application.
*Verdict:* rejected for v1, **recorded as genuinely open for v2.** The DOM shape is a
*syntax* (`view("div").child(..).styled(..)`), not a commitment to a DOM; §5-S3 maps it onto a
retained scene tree with no HTML anywhere. If that mapping proves to be where the cost is, this
is the fallback and it should be re-priced then rather than now.

---

## 5. The slices, in dependency order

Dependency order, as ruled: **C14 → the backend probe → a minimal `native` platform → the
render layer → the style mapping → input/windowing**, with the rpc runtime last. Sizes are
`S` (part of a lane), `M` (one lane-order), `L` (two to three lane-orders), `XL` (a dedicated
arc of several orders). Each slice names its exit test and its risks.

### S0 — C14's representation (precondition, not part of F1)
`signal-cell-representation.md` §10's S1–S3 land on JS and are verified by the SCC gate before
any native code exists. **F1's S1 cannot start until S0 has a decision**, because the probe's
R-2 finding makes the cell representation part of the *value* representation.
*Size:* see C14 §10. *Exit test:* `a_disposed_exemplar_holds_no_reactive_cycle` still
`cycles=0` with a lower mounted SCC count.

### S1 — the backend: `fun main()` printing to stdout as a native binary. **Size: L.**
A `Backend::Rust` arm and a `crates/vilan-rust` emitter beside `transformer.rs`, plus the
runtime crate §2.3 enumerates. Scope it hard: **no async, no UI, no rpc, no `std::fs`** — the
subset the probe used, which is structs, enums, `Option`/`Result`, `str`, `List`, `Map`/`Set`,
closures, `impl`s, traits (monomorphised), `print`, `panic`, and C14's cell.
*Exit test:* a corpus of the existing `crates/vilan-cli/tests/` programs that use no platform
surface, each compiled by both backends, **producing byte-identical stdout**. That is the
`ssr_differential` shape applied to a backend rather than to a platform, and it is the right
gate because it needs no new oracle.
*Risks:* (i) R-4 — the `RefCell` residue and its panic failure mode, which needs a ruling
(§9 Q1) before the emitter's shape is fixed; (ii) rule 1's copies are 50.1 % of allocations and
whether Rust's move semantics let the emitter elide *more* of them than JS does is unmeasured —
`lifetimes.md` §7 calls the reuse analysis "the tier's one open engineering question, and it is
not resolvable on paper"; (iii) C12 (a captured view of a dead local) is a filed, unfixed
use-after-free the moment the host stops boxing places — **it must be fixed before S1 ships**,
not after.
*Cost note:* the probe's clean release build was 1.15 s user for ~700 lines. rustc is the
inner loop from here on, and it is slower than emitting JS by roughly two orders of magnitude
on small programs. `vilan run` on a native target needs a debug profile and incremental builds
by default.

### S2 — a minimal `native` platform in the build model. **Size: M.**
Eleven registration sites, named so the estimate is checkable:

1. `target.rs` — `Platform::Native`, `PlatformPattern::Native`, and the eight methods that
   match on `Platform`: `parse` (and its "unknown platform" message), `name`, `runtime_name`,
   `all_hosts`, `has_process_exit`, `script_extension`, `matches`, `representative`.
2. `platform_color.rs:125` — `known_hosts() -> [Platform; 4]`, a hardcoded duplicate of
   `all_hosts()` whose *type* changes.
3. **`lib.rs:93` `infer_platform` — the sharpest break.** It is binary: find the layer holding
   `Pattern::Browser`, lump everything else into `other_roots`, answer `Browser` or the
   default (node). With a third `ui` twin, a scratch file importing a native-only name analyzes
   as **node** and the editor reports the process twin's `View` against native source — exactly
   the E113 failure its own doc comment at `:80` describes.
4. `crates/vilan-wasm/src/lib.rs:291` `embedded_std_spec()` — a hand-built `PackageSpec`
   duplicating std's manifest, guarded by `the_hand_built_std_spec_matches_the_manifest`.
5. `manifest.rs` — validation and the two user-facing messages that enumerate platforms.
6. `crates/vilan-cli/src/main.rs` — `no_host_platform()`, `validate_backend`, `NODE_LEG`,
   `select_node_entry` (`vilan run` filters to `Platform::Node`; a native leg is unrunnable
   without an arm), the two `Project::Single` run guards, the two `Command::new("node")` sites,
   and the browser-first build ordering.
7. `transformer.rs` — the four `has_process_exit()` branches.
8. `std_twin_parity.rs` — `enum Side { BrowserOnly, ProcessOnly }` becomes N-way; every
   `ALLOWED_DIVERGENCES` entry grows a column.
9. `ssr_differential.rs` — a native leg has no serialisation to compare against; §6.2 proposes
   what it compares instead.
10. std's manifest — three lines: `[library.layer.native] platform = ["native"]`.
11. Docs gated by `cargo test --test docs`: `tour/platforms.md`, `appendix/cli.md`,
    `guide/ssr.md`, `guide/ui.md`.

*Exit test:* `vilan build --platform native` on a program importing `std::dom` produces
``requires the `browser` layer of `std` and cannot run on `native` ``, pinned in
`crates/vilan-core/tests/inference/platform.rs` beside the two existing direction pins; and
`check_library_contract` stays green over std.
*Decision this slice forces:* **does `native` join `@process`?** §9 Q2. Recommendation there:
**no**, initially — joining makes `std::fs`/`std::http`/`std::db` free and simultaneously
obligates every base-layer module to resolve for native (`check_library_contract` seeds the
base layer with `Platform::all_hosts()`), which is a much larger S1.

### S3 — the render layer: a third `std::ui` twin over a retained scene tree. **Size: XL.**
`vilan/std/src/native/ui.vl` with the same public surface, over:

- **a retained scene tree** — one node per `View`, holding tag, attributes, children, text, and
  the live subscriptions that write them. `bind_text`/`bind_attr`/`bind_styled`/`bind_each`
  become writes into the node rather than into a DOM element; `Region`/`Row` already exist in
  the browser twin as the reconciliation unit and port directly.
- **layout** — a flexbox-class engine (taffy). The `View` surface is already flex-shaped
  because CSS is; A95's `style()` builder is where the box model is spelled.
- **text** — shaping and rasterisation (cosmic-text / swash). Text is the part that is never
  cheap and never optional.
- **paint** — wgpu plus a vello-class 2D renderer for the fills, strokes, rounded rects,
  shadows and clips that a `Style` can ask for.

*Exit tests, in order:* (1) a window showing one `<div>` with a background colour and a fixed
size; (2) the same `<div>` with text, wrapped, at the right font; (3) a `bind_each` list of 100
rows that adds, removes and reorders; (4) **kolt's sidebar rendered natively** —
`src/sidebar.vl` + `views.vl:197` `fun sidebar(..)`, ~130 lines, which exercises nested flex,
a styled scroll region, icons, hover state, and a `show(..)` toggle.
*Risks:* this is the slice that is a project rather than a change. Text shaping and the style
resolver (S4) are each larger than S1. The honest sequencing is that S3 ships *incapable* —
a small subset of `Style`, a subset of the layout algorithm — and grows, with the exit tests
above as its ladder.

### S4 — the style mapping: A95's conditions onto native state. **Size: L.**
`style-conditions.md` §1's four condition kinds each get a native meaning, and the mapping is
clean because A95 made a condition a *value* rather than a selector string:

| kind | constructors | native meaning |
|---|---|---|
| `Pseudo` | `hover()`, `focus()`, `active()`, `disabled()`, `first()`, `last()` | per-node **hit-test / focus / interaction state** on the scene node; `first()`/`last()` are sibling-index facts the tree already has |
| `Element` | `element("selection")`, `element("before")` | a generated sub-node the renderer owns |
| `Attribute` | `attribute(n)`, `attribute(n).eq(v)` | a lookup in the node's own attribute list — **cheaper natively than in a browser**, because there is no selector engine |
| `Relation` | `within(c)`, `children()`, `divide()` | an ancestor/sibling query up the retained tree |
| `Media` | `sm()`…`xl()`, `media(min_width)` | **window queries** — the window's logical width, re-evaluated on resize |

The `css` block becomes a native **style resolver**: A95's canonicaliser already produces a
structured condition set with a total order (§2.1) and a stable key, so the resolver is a
match over sets rather than a CSS cascade. `.not()` and `+` are set algebra, already defined.
*Exit test:* `hmr_css_matrix`'s and `style_when.rs`'s condition programs, evaluated by the
native resolver, produce the same *declaration set per node state* the browser produces per
selector — a differential of resolved declarations rather than of CSS text.
*Note:* this is why A95 was worth building before this paper existed. A condition-as-string
model would have made this slice a CSS-parser port.

### S5 — input and windowing. **Size: M.**
A winit-class layer: window creation, the event loop, pointer/keyboard/IME/scroll, DPI and
resize, and the mapping from a pointer position to a scene node (the hit test S4's `hover()`
consumes). `std::dom`'s `Event` does not port — the browser twin's `on_event` takes
`|Event| void` and the process twin already takes a generic `|E| void` precisely because "a
server layer cannot name browser-only `std::dom::Event`". The native twin takes a native
event type, and §6.2 says what the twin-parity gate does about that.
*Exit test:* a `<div>` whose `hover()` style applies under the pointer and whose `on("click")`
fires; kolt's sidebar collapse toggle works.

### S6 — the rpc runtime in-process. **Size: M. Later.**
`rpc.vl` already has `duplex_pair()` (`:164`) — two `Shared<Option<|Frame| void>>` slots making
each end's send the other's receive. A desktop app's `[rpc]` handlers run over that transport
with no socket, which makes a native kolt a single process with the same source as the
fullstack one. Needs S1's async answer (§9 Q4) and nothing else.
*Exit test:* an `[rpc]` call from a native `main` reaching a handler in the same binary,
with a `RemoteSource` mirror updating a `bind_text`.

---

## 6. Prior art, measured against this plan

### 6.1 The five
- **Dioxus / Blitz.** The closest analogue by design: HTML+CSS *semantics* over a
  Rust-native renderer (vello, taffy, parley), with the app written against a DOM-shaped API.
  Blitz exists precisely because "keep the web's layout model, drop the browser" is a coherent
  target. It validates §5-S3's premise and it also shows the bill: Blitz's hard parts are
  text and CSS, which are S3 and S4 here, in that order.
- **Makepad.** A shader-first, GPU-native UI with its own DSL and its own layout model.
  Fast, and a different language — it is the retained-tree-API alternative §4.4 rejects,
  built by people who accepted the migration cost because they had no estate to migrate.
- **Slint.** The closest to vilan's *shape*: a declarative UI language with a property system
  that is `Rc`-boxed values plus `Weak` dependency back-pointers, compiled ahead of time,
  running on both a native and an embedded backend. Slint chose **counting**, which is C14's
  recommendation, and its dual-backend structure is the third-twin problem solved once.
- **GPUI (Zed).** A Rust-native, GPU-rendered UI whose central design decision is an
  **entity/handle model over a central app context** — `Entity<T>` is a handle into an
  app-owned slab, cloned freely, upgraded to read. It is C14's representation (b), shipped and
  successful, in a codebase that controls both the framework and the application. The thing it
  does that vilan cannot is make the handle's context an explicit parameter everywhere; vilan's
  `ambient-owner.md` §2.1 deliberately refuses that ("strict-only, no absence semantics"),
  which is exactly why C14 §4.2 (b1) prices (b) as it does.
- **Flutter (Impeller).** The long view: Impeller exists because runtime shader compilation
  caused jank, and the fix was precompiling every shader the renderer can need. The lesson
  transfers whole — S3's renderer should have a *closed* set of shaders, which a vello-class
  design gives, rather than generating them per style.

### 6.2 The third-twin problem, which none of them has
Every project above has one UI implementation, or two written by one team with no parity gate.
vilan has two implementations behind one surface **and two gates that are structurally
two-valued** (§3). A third twin needs:

1. `std_twin_parity.rs`'s `Side` to become "which layers declare this name", with
   `ALLOWED_DIVERGENCES` gaining a column — and the existing divergences re-checked, because
   the allowlist is honest in both directions and a stale entry fails.
2. A rule for a name that exists in two of three layers. `bundle-boundaries.md`'s
   `View.swap_split` is the only sanctioned precedent ("its absence degrades the chunk gate
   away instead of breaking a build") and it works only for emitter-selected names no user
   writes. `mount`/`mount_root` are browser-only today and native needs *its own* entry verb.
   **Recommendation: the native twin declares `mount` too, and the rule becomes "a name in the
   `ui` surface is declared by every layer that can host an app" — process/SSR being the
   exception that renders rather than mounts.**
3. `std::web`'s prelude premise. `web.vl:32` re-exports `ui::{ View, view }` and works only
   because `ui` is declared by *both* platform layers; the rule becomes "all three".
4. An answer for `ssr_differential`: there is no native serialisation to compare bytes with.
   **Recommendation: compare the resolved scene tree's structure — tag, ordered attributes,
   text — against the process twin's `render` output parsed back, which is the same
   equivalence the DOM stub already computes on the browser side.**

---

## 7. What is explicitly NOT in scope

No compiler work of any kind lands from this paper. No `Backend` variant, no `Platform`
variant, no std file, no manifest key. F1 stays open with the paper landed and its slices
filed as items; S1's first move (the emitter skeleton and the runtime crate) is Order 37's
earliest candidate, and only after C14's S0 has a ruling.

Also out of scope, deliberately: mobile (a later S5 variant), wasm (§4.2, a second backend),
hot reload on native (`__hmr_active` is browser-only and stays so), bundle splitting
(the five `__chunk_*` helpers are browser-only), and `std::canvas` (browser-only by file
placement, `canvas.md` §6 — a native equivalent draws into the same scene tree S3 builds and
is a separate item).

---

## 8. Open questions, each with a recommendation

**Q1 — what does emitted Rust do about rule 4?** Probe finding R-4: rustc sees aliasing the
vilan checker already proved safe, so interior mutability becomes `RefCell` and a violated
invariant becomes a runtime panic instead of a compile error. *Rec: ship `RefCell` for S1 and
measure.* The failure mode is a panic with a message, which is honest; `unsafe` with a
soundness argument is the optimisation, and it should be paid for with a measurement rather
than in advance. This must be ruled before S1's emitter shape is fixed.

**Q2 — does `native` join the `@process` family?** *Rec: no, initially.* Joining gives
`std::fs`/`std::http`/`std::db`/`std::process` for free and simultaneously makes
`check_library_contract` demand that **every base-layer std module resolve for native**,
because the base layer serves `Platform::all_hosts()`. That is a much larger S1 than "a window
and a `<div>`". Revisit at S6, when the in-process rpc runtime wants a server-shaped std.

**Q3 — the three-layer rule.** §6.2 proposes it: a `ui` name is declared by every layer that
can host an app; the parity gate becomes N-way; `ssr_differential` compares resolved structure
rather than bytes. *Rec: rule it with this paper*, because S2 cannot be sized without it and
because `std_twin_parity`'s type signature changes either way.

**Q4 — async on native: which executor, and does `Task` stay `external`?** Unlisted in F1 and
the largest single runtime item (§2.3 (7)). *Rec: keep `Task<T>` `external` and bind it to a
single-threaded executor in the runtime crate*, because vilan's concurrency model is
structured-and-single-threaded by construction (nurseries, `ambient_nursery`, a synchronous
drain) and a work-stealing multi-threaded executor would import a `Send`/`Sync` obligation the
language does not express. File as its own item before S1.

**Q5 — `i53`/`u53` on native.** They are a JS shape (`f64`'s exact-integer range).
*Rec: keep them as distinct types with native widths `i64`/`u64` and a documented note that
their *range guarantee* is the JS one*, so a program that round-trips through both backends
behaves the same. kolt already uses `i53` for ids with a `FIXME` about missing `u53` wire
support (`store.vl:104`), so this is not hypothetical.

**Q6 — is C12 a native blocker?** `lifetimes.md` §2.2: a closure capturing a view of a dead
local is "memory-safe today only because JS boxes the place and traces it… under any non-GC
backend this is a use-after-free." *Rec: yes — C12 is promoted to an S1 precondition*, not a
deferral. It is the one filed item that turns into memory unsafety rather than into a
behaviour change.

**Q7 — where does the native runtime crate live, and does it vendor wgpu?** *Rec: a new
workspace crate `vilan-rt` for §2.3's items (1)–(6), with the render stack as a **separate**
crate S3 introduces*, so S1's dependency footprint is `std` plus nothing and the probe's 1.5 s
build stays representative. AGENTS.md makes a new dependency a stop condition; S3's five
(wgpu, a 2D renderer, cosmic-text, taffy, winit) are a deliberate, ruled decision, and S1 must
not smuggle them in early.

**Q8 — does `vilan run` build native in debug by default?** *Rec: yes, and say so in the CLI
help.* rustc is the inner loop from S1 onward; the probe's release build was 1.15 s user for
700 lines, and a real app is three orders larger.

---

## 9. What this closes, and what stays

**Closes.** F1's DISCUSSION status: the four owner questions are answered with reasons (§1),
the backend probe is done and recorded (§2), the alternatives are costed rather than left as
a fork (§4), and the four pillars are slices with a dependency order, exit tests and sizes
(§5). The runtime the emitter needs is enumerated (§2.3) rather than gestured at.

**Stays open.** Everything in §8, of which Q1 (rule 4 under rustc), Q3 (the three-layer rule)
and Q6 (C12) block S1 or S2 and should be ruled before Order 37's queue is written. The render
layer (S3) stays an XL that nobody should start before S1 and S2 are green.

**New items this paper proposes** (evidence in §2.3, §2.4, §5):

- **F1-S1** — the emit-Rust backend and `vilan-rt`: a `fun main()` printing to stdout as a
  native binary, gated by byte-identical stdout against the JS backend over the
  platform-free test corpus. `design`/`feature`, size L.
- **F1-S2** — the `native` platform in the build model: eleven registration sites, named in
  §5-S2. `feature`, size M.
- **NEW-1** — async on native (§8 Q4): an executor and a cancellation primitive for `Task`
  and `Nursery`. Unlisted in F1; blocks S6 and probably S3. `design`.
- **NEW-2** — C12 promoted from a recorded deferral to an S1 precondition (§8 Q6): a captured
  view of a dead local is a use-after-free the moment the host stops boxing places. `bug`.
- **NEW-3** — the three-layer `std::ui` rule and the N-way twin-parity gate (§6.2). `design`.
- **NEW-4** — `infer_platform` is binary (browser / not-browser) and a third UI twin makes the
  editor report the wrong twin's `View` against native source — the E113 shape its own doc
  comment describes. `bug`, latent until S2. `crates/vilan-core/src/lib.rs:93`.

---

## 10. As built (Order 37, lane native-b-37, 2026-09-17) — S1a, and what the owner changed

**The owner's steer at GO, verbatim:** "For the native path, I assume we're just setting up
the Rust backend supporting cli programs for now. Drawing windows is much more complicated
and I want to have a conversation about how to write UI code such that it works for native
and web simultaneously (with some exceptions; native close, minimize, maximize buttons, for
example). Being able to run native web servers (which should be more easily achievable in
the short term) is a huge win in and of itself." So §1's four answers stand for the *build*
with one replaced: **"desktop first" is gone.** The order of native products is CLI programs
(S1, this order) → web servers (**F18**, Order 38's first native slice) → a UI layer only
after that conversation (**F17**, a discussion, not queued). §8 Q3's three-layer rule (F15)
is *recorded*, not ruled — it belongs to that conversation, and S2's sizing waits with it.

**C16 first** (`e56b1227`). The precondition §8 Q6 named: a closure that captures a view
and is handed to a callee that KEEPS it (stores it in a field, puts it in a collection or
an enum payload, assigns it, returns it, or passes it on to a callee that keeps it) is
refused, with the callee named — an interprocedural summary of *retaining parameter
positions*, a monotone fixpoint in `infer_bumps`'s shape, asked only of call arguments
that are view-capturing closures (a bodiless callee keeps everything). C13's
pinned-ignored case is the first exhibit and is no longer ignored. Both *direct* shapes
were already refused at `d783fbf4`; the whole remainder was the storing-callee shape, and it
landed whole. Nothing in the estate fires (131 corpus programs, the examples, the docs,
kolt), so the family is `fix`.

**S1a** (`7e245e39`). `Backend::Rust` (`--backend rust` on `build` and `run`; the
help says the build is debug — §8 Q8). Two new workspace crates with **zero crates.io
dependencies** (§8 Q7): `vilan-rt` (~700 lines: `Rc<str>`, `Vec`, insertion-ordered
`Map`/`Set`, `Shared`/`Captured` as `Rc<RefCell<_>>`, `guarded` over `catch_unwind`,
`with_finally`, the `List`/`str` intrinsic bodies, and `Js` — the `console.log` rendering,
which is where the differential actually lives: `Infinity` not `inf`, `0` not `-0`, the
`1e-6..1e21` exponential switch, node's `[ a, b ]` spacing, a top-level string bare and a
nested one quoted, an enum as `[ index, …data ]`) and `vilan-rust` (~1,950 lines: the same
`Program` in, one `main.rs` out — real structs and enums, `Option`/`Result` onto Rust's,
`impl` methods, closures, `match`, loops, views, rule-1 copies read off `clone_sites`).
`vilan-cli/src/native.rs` writes `dist/native/<entry>/{Cargo.toml,src/main.rs}`, runs
`cargo build`, runs the binary; `--stdout` prints the Rust; `--watch` and a workspace are
refused by name. **A finding worth recording against §5-S1's sizing:** the analyzer has
already resolved `p.bump(2)` into a call whose subject is the member and whose first
argument is the receiver, so a concrete-case backend needs **no impl-selection
machinery** — that is why S1a was reachable in one lane-order.

**The exit test** — `crates/vilan-cli/tests/native_differential.rs`: every platform-free
program compiled by both backends, stdout byte-identical. The enumeration
(`platform_free_programs()` + `PLATFORM_MODULES`) is a support fn, so S1b widens the
corpus by deleting rows. The default suite runs ten programs (rustc is ~1 s each); the
whole set runs under `VILAN_NATIVE_DIFFERENTIAL=1`.

| | |
|---|---|
| corpus `.vl` | 131 |
| platform-free | 117 |
| emitted (accepted by the backend) | 33 |
| refused by name | 98 |
| byte-identical (verified) | 17 |
| differing stdout | **0** |
| rustc-refused emitted Rust | **0** |

Refusals by construct: generic type parameter 29, named generic fn 17, generic-parameter
dispatch 5 — **51 of 98 are monomorphisation, which is S1b exactly as §5-S1 predicted**;
module-level binding 6, overloaded operator 6, intrinsics 3, `resource` 2,
`JSON.stringify` 2, `?` 2, `async fn main` 2, and singles. Two *differing* outputs were
found during the lane and closed before it ended (`List::remove` answered an `Option`
where its signature is `T`; `resource` teardown produced wrong output → refused by name):
a wrong answer is never left standing, it becomes a refusal or a fix. **`board.vl` cannot
be S1a's headline** — its first wall is `SignalCell<i32>`, a generic type, so it is pinned
as a named gap that flips to a comparison when S1b lands.

**§8 Q1 as measured.** `RefCell` shipped; the boxed-binding count over the accepted
corpus is **0** (sixteen programs measured; no corpus program has a mutably-captured
binding — the mechanism is proved on a probe, `boxed-bindings=1`, and
`VILAN_NATIVE_REPORT_BOXED=1` prints it). The by-value capture optimisation (C15) has
nothing to optimise until S1b's corpus compiles; it should wait. **F16 as built:** every
closure *type* is `Rc<dyn Fn>` and a closure value read from a binding is retained per use
(the probe's R-1 reproduced and closed); the `impl Fn` half for only-called closures is
not built until a measurement says the retain costs something — C16's
`compute_retaining_positions` is the discriminator if wanted.

**§8 Q4 — the executor, designed (J6).** Read off `transformer.rs::helper_source`, which
*is* the contract, seven primitives: (1) `Task<T>` stays `external` — a handle into the
executor's slab (`Pending | Done(T) | Failed(payload)`, a continuation list
`Vec<Rc<dyn Fn()>>`, an `observed` flag, the spawn origin; eager spawn; a failure latches at
settle time; an unowned, unobserved failure reports once with its origin, as `__task`
does); (2) a single-threaded loop with a **microtask queue drained to exhaustion** before
a deadline-ordered timer heap — observable, `reactive-turns` is the pin — and exit when
both are empty; no threads, no work stealing; (3) `Nursery` as `Rc<NurseryBody>` with
`children`, `cancelled`, a fail latch, a wake list and `parent: Option<Weak<…>>`,
`CancelSignal` the `Weak`; `OwnedNursery`'s `Drop` is already pure vilan, so
cancellation-on-drop is destruction.md's mechanism and needs no second one; (4) the join
reproduced exactly — the child list grows mid-drain, each child raced against the
fail-wake; on failure cancel, absorb every remaining child, then propagate the body's
error first or the latched winner's with `" (in task spawned in …)"`; (5) detached
nurseries override `__fail`; (6) `sleep` as an abortable timer registration; (7) `Timer` as
a memoized verdict plus a waiter list. Emitter side: **emit Rust `async fn` over a
hand-written single-threaded executor** in `vilan-rt` (`await` → `.await`; the `Waker`
from a `RawWakerVTable` over an `Rc<Cell<bool>>`; `Pin`/`Send` never surface) — CPS
rejected. Size M; the precondition for F18.

**§8 Q2 is wrong on its own evidence, and reversed (F18).** "Joining `@process` obligates
every base-layer module to resolve for native, which is a much larger S1" —
`check_library_contract` (`analyzer.rs` ~52616) never inspects `[extern]`; it is
structural. Measured: joining `@process` alone costs **zero** violations (no process
module imports a browser-only module); joining `all_hosts()` alone costs exactly **one**
(`web.vl:41`/`:57` re-export `pkg::ui`, which exists only in the platform layers); joining
**both** costs zero, because `process/ui.vl` then covers `native`. The real gate is
*emission*: fifteen base modules with JS-only bindings (12,500 lines, `number.vl`'s 81
`Math.*` and `json.vl`'s 26 dominate) plus eight intrinsic-only modules that already
have native bodies in `vilan-rt`. **Native servers, sized:** S1b (monomorphisation +
module-level bindings via `thread_local!` + the remaining intrinsics — 51 of the 98
refusals; L) → J6 (M) → http (`node:http`'s `createServer` + `node:stream/consumers`, 3
imports + 22 accessors, plus `node:crypto`'s `createHash` for the RFC 6455 key; M) → db
(`node:sqlite`'s `DatabaseSync` + the eleven `__db_*` helpers; M) → rpc (**S — nothing
new**: `process/rpc_server.vl` is 1,306 lines of which 1,303 carry no extern; `ws.vl` (229)
and `wire.vl` (708) carry none — ~2,240 lines of the server compile natively the day
generics work, on 28 host bindings) → fs (`node:fs/promises`, 16 imports + 21 accessors;
M, and **not on the exit test's path**). Of the nine `process/` files four carry zero
externs (`build`, `watch`, `document`, `ui` — 2,142 lines, no twin needed). **The exit test
is small**: kolt's server leg is three files, 564 lines, reaching five of the nine process
modules and no `fs` at all. Total to kolt's server serving its client ≈ two to three
lane-orders, of which S1b must not be under-scoped.

**Corrections to this paper.** §2.3 (2): 53 intrinsics, not 52 (`analyzer.rs:48629`).
§2.3 (3): `RESERVED_NAMES` is at `transformer.rs:11291`; the extern-helper registry has 47
entries, 25 on the server path. §5-S1: no impl selection is needed for the concrete case
(above). §8 Q2: reversed (above). **F19** (`vilan-rt` is not reachable from a released
binary — `native.rs` resolves `$VILAN_RT`, else the crate's source sibling) blocks any
non-from-source use of the backend and is S1b's first item. **What stays out until F17:**
S2's UI-shaped registration sites, F15's N-way parity gate, E182.

## 11. As built (Order 38, lanes native-a-38 + native-b-38, 2026-09-21) — generics, the executor, and an exit not reached

**The base was red, and §10's table did not say so.** §10 reports "17 byte-identical, 0 differing, 0
rustc-refused". That was the DEFAULT suite's view — ten programs. Under `VILAN_NATIVE_DIFFERENTIAL=1` the
whole set at Order 37's sealed tip read 117 enumerated / 29 identical / 84 refused by name / **4 broken**: a
native MISCOMPILE (`side-effect-let.vl` printed `0 0` where JS prints `1 2` — rule 1's copy applied to a
loaned parameter in argument position, including the receiver of a mutating intrinsic: `(xs).clone().push(..)`),
two rustc refusals (`mut-parameters.vl` — no `mut` on the binder; `option-view.vl` — a view inside an enum
payload) and a harness defect (`stage()` copied files only, so `module-dirs.vl` could not resolve). All four are
closed, and **the seal now runs the whole set** (`scripts/integration/seal.sh`).

**F19** — `vilan-rt` is reachable from an installed toolchain: `vilan-embedded-std` carries a second table
(own hash, `~/.vilan/rt-cache/<hash>/vilan-rt/`, a GENERATED manifest — the crate's own is a workspace
member); `runtime_crate` is three roots in B346's order and `$VILAN_RT` never falls through; pinned in
`install`.

**S1b** (835c29d2) — monomorphisation by reproducing the JS emitter's MECHANISM: substitution threaded through
the walk, a structural instance key, reservation before the body so recursion works. §5-S1's hope that the
Rust emitter could CONSUME the JS instance set is wrong: `Transformer::instances` is minted during the JS walk
with `js::Node` values. What is shared is `impl_select::*` and the dispatch helpers; the resolution half now
exists twice and tracker F26 lifts it. Also built: generic structs/enums as one Rust item per instantiation
with their own `impl Js`; generic-parameter dispatch and trait-default specialization; module-level bindings as
`thread_local!` `RefCell`s; `Weak<T>` and six `Shared`/`Option` intrinsics; `if x is P(let y)` → `if let`; a
return type inferred where none was written; a string-literal ESCAPE miscompile found and fixed.

| whole set (117 platform-free) | Order 37's tip | after S1b | after J6's rebase |
|---|---|---|---|
| byte-identical | 29 | 47 | **49** |
| refused by name | 84 | 70 | 68 |
| differing stdout | 1 | 0 | **0** |
| rustc-refused | 2 | 0 | **0** |
| broken (incl. harness) | 4 | 0 | **0** |

**J6, as built** (native-b-38; 5b810d06, 3bcaa083) — `vilan-rt/src/executor.rs`, dependency-free,
`#![forbid(unsafe_code)]` intact. Four corrections to §10's design: (2) it is ONE timer per turn — the single
earliest entry — then the microtask queue again; firing every DUE timer in one pass puts a second
`setTimeout(_, 0)` callback ahead of the first's continuations, a different program (proven red); (3) a `Weak`
cannot WAKE a parked `sleep`, so a nursery body also carries a cancel-waiter list and a descendant list; the
`RawWakerVTable` over an `Rc<Cell<bool>>` is reversed — it would cost `unsafe` and buys nothing, since every
waitable object already owns a wake list: `Waker::noop()` plus the current task's id is the whole mechanism;
(4) the body's own failure CANCELS the nursery before the drain. A panic is caught at the poll boundary
(`catch_unwind` over `Future::poll`), which latches a task's failure and gives the nursery join and
`with_finally_async` their catch-across-an-await; a cancellation is its own payload TYPE. 25 `vilan-rt` pins,
one per ordering rule, four proven red against the rule removed. Emitted Rust never spells `Pin`, `Send` or
`Box::pin`. After the rebase onto S1b: `nursery.vl` and `await-postfix.vl` are byte-identical, `Promise.all` /
`Promise.race` are wired and pinned, and five async programs are refused BY NAME — three for node host
bindings (F18's), `reactive-turns.vl` for the host type `Hash`, `adapt.vl` for an async closure as a VALUE
(adapted instances are unmodelled natively — F22).

**The exit was not reached.** The order's native exit was "`board.vl` flips to a byte-identical comparison".
S1b removed every wall S1a named, and the one it then recorded — "an `is`-test capture outside an `if`" —
was a FALSE POSITIVE: "a binding in neither `variables` nor `parameters`" also describes a context-threaded
hidden parameter, which `context.rs` keeps out of `parameters` deliberately. With that fixed, `board.vl` stops
at a real wall, the host type `Hash` (`std::reactive`'s `CanonicalHash`). Three constructs are 29 of the 68
remaining refusals — `Hash` (10), `lazy` parameters (12), overloaded operators (7) — and they are F20,
Order 39's, beside F18.

**Measurements.** C15: ONE boxed binding over the 47-program accepted corpus (iterator.vl) — keep waiting; and
the count measures what the walk EMITTED (it had scanned every closure the program loads, and A108's two
mutably-captured codec locals made a two-line probe read 2 — a merge fix). Compile CPU per accepted program,
debug, loadavg 58–64: emit 0.353 s mean, cargo+rustc +0.521 s mean. **F18's brief is measured**: kolt's server
leg has 85 gaps (`VILAN_NATIVE_HOST_CENSUS=1 vilan build --backend rust --stdout src/server.vl` — a refusal in
expression or type position becomes a recorded `unimplemented!()` and the walk continues): 55 host bindings, 11
host types, 10 intrinsics, 9 language constructs. The list is kept at
`scripts/integration/sweeps/order38/native-a-38/kolt-server-census.txt`.

**Open from this order:** F20 (the three constructs), F21 (`Option<&mut T>` in a payload — refused by name
today), F22 (adapted instances), F23 (`context.rs` records the hidden parameter's flavour; the emitter infers it
today), F24 (the executor's slab never reuses a slot — before F18's per-request spawns), F25 (exit codes, panic
rendering, printing a host handle), F26 (the shared resolution module), N106 (the f64-boundary and non-BMP
halves).

