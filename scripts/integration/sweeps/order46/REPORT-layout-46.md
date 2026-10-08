## layout-46: A154 is done; F28's first half stopped on its proof, as the brief required

I couldn't write the REPORT file (the tool refuses report files for subagents), so this message is the report.

- **Branch:** `layout-46`, tip **2f1cb1a09ff6428f2ab732fcc4edfa2a44734248**. It has 6 commits on `origin/next` @18c2a059.
- **Not pushed.** The worktree is `vilan/.claude/worktrees/layout-46`.

**Commits**
1. `0b09e865`: the moves and every reference to them (step 2).
2. `de35a43b`: the refusal of old paths, its fix data and the LSP quick fix (step 3).
3. `102a193a`: F28 stopped. It carries the proof pins and a formatter bug the attempt found, now fixed.
4. `bca29f4b`: docs and the CHANGELOG.
5. `8b8781ae`: the layer contract now checks nested modules. A154 had moved every layered std module out of its reach.
6. `2f1cb1a0`: one clippy fix.

**Step 1 (census)** is in `proposals/…/order46/layout-46/census.md`. It is not committed: it lives in the proposals repo, which is yours.

### Census counts
- **Total:** 1,706 references to an old path in 229 files, excluding CHANGELOG history. On top of that, 52 sites spell `"std::web"` or `WEB_PRELUDE`, and about 180 references name a moved file by its path.
- **By old module:** ui 488, style 438, asset 155, web 102, dom 97, rpc_server 95, store 78, router 65, document 42, dev 37, storage 23, transient 20, delta 18, promise 15, native_map 14, store_core 7, hash_map_cell 6, hash_set_cell 5, null 1.
- **By area:** vilan-core tests 634, vilan-cli tests 358 (including 8 native fixtures, the split project and the ledger), docs 198, std's own files 152, vilan-core src 120, vilan-lsp 97, examples 76, wasm tests 15, templates 12, corpus 11, scripts 8, others small.
- **Sites that name a module as a bare string** (these match no grep for `std::`, so they are listed by hand in the census):
  - element syntax's `StdItem("ui","view")` and css's `StdItem("style",..)`;
  - the always-loaded `null` and `promise`;
  - the lang items found by module name: `asset`, `dev`, `native_map`, `promise`, `dom`;
  - the css-ambient `style::prelude`;
  - `WEB_PRELUDE`, which was looked up by its last segment;
  - the B4 import steer's index, the LSP's add-import candidates, the IDE's auto-import table, `infer_platform` and the layer contract: all five read std's top level only;
  - the chain frame label, which used the file stem;
  - the book theme's `PROCESS_HINT` regex.
- **Checked and not affected:** bindgen output, the `Wire`/`Json` derives, `init_order` (it matches the file name, which did not change).

### The final old → new table (this is the one site-46's table needs)
| Old | New |
|---|---|
| `std::dom` | `std::web::dom` |
| `std::ui` | `std::web::ui` |
| `std::style` (and `std::style::prelude`) | `std::web::style` (and `std::web::style::prelude`) |
| `std::dev` | `std::web::dev` |
| `std::router` | `std::web::router` |
| `std::storage` | `std::web::storage` |
| `std::document` | `std::web::document` |
| `std::asset` | `std::web::asset` |
| `std::web` (the web prelude), and `prelude = "std::web"` | `std::web::prelude`, and `prelude = "std::web::prelude"` |
| `std::hash_map_cell`, `std::hash_set_cell` | `std::reactive::hash_map_cell`, `std::reactive::hash_set_cell` |
| `std::transient`, `std::store`, `std::store_core`, `std::delta` | `std::reactive::transient`, `std::reactive::store`, `std::reactive::store_core`, `std::reactive::delta` |
| `std::null`, `std::promise`, `std::native_map` | `std::js::null`, `std::js::promise`, `std::js::native_map` |
| `std::rpc_server` | `std::rpc::server` |

### Coexistence and the file layout
- **`reactive.vl`, `rpc.vl` and `web/style.vl` each sit beside a directory of the same name**, following the precedent `style.vl` + `style/` already set. None of the three declares an item with a child module's name, so A67's collision rule is not triggered.
- **`web/` and `js/` are directories with no `lib.vl` of their own** (pure namespaces).
- **The layered modules are still layered, under their new paths:**
  - `src/browser/web/{dom,ui,router,storage,dev}.vl`
  - `src/process/web/{ui,document}.vl` and `src/process/rpc/server.vl`
  - `fs`, `http`, `db`, `process`, `watch` and `build` stay at the top of `src/process/`.
- **What still works unchanged:** re-exports through `std::reactive` (`HashMapCell`, …), and `ui::` and `style::` as ambient modules under the web prelude.

### Step 4 (F28): stopped, with exactly what failed
I wrote three pins, `module_resolution::f28_*`, phrased so they read the same whichever mechanism serves the modules. They pass on the layered tree. I then moved all thirteen modules into the base and gave each a file-level `[platform(..)] mod self;`, and ran the pins again:

- **(a) An off-platform call gives one error at the user's call, and a bare import is legal.** This fails for `std::web::router`.
  - `router` is fenced `browser` and imports the `ui` twin. A node build binds the process twin.
  - The fence walk then reports six of the process twin's functions as violations inside std: `view`, `text`, `attr`, `on_event`, `chunk_pending`, `chunk_failure`.
  - This happens even on a bare `import std::web::router::location_url;`. Under the layer, the same import gives zero errors.
  - The other eleven modules behave like the layer: one error at the call. Only the label changes, from "the `browser` layer of `std`" to "the `browser` platform its file declares".
  - `std::web::document` gives the same resolution errors in a browser build under either mechanism. That is a pre-existing bug, filed below.
- **(b) A file importing only a browser module is inferred browser.** This fails for all four browser modules: `infer_platform` reads browser evidence only off the layer directory.
- **(c) Reachability** was not reached.
- **Outcome:** I reverted the move. The pins stay in place as the gate for when F28 is tried again.

### The refusal of old paths: code and fix-data API
Everything is in `vilan_core::parsing`, beside the existing foreign-spelling and autofocus fixes:
- **The table:** `MOVED_STD_MODULES` (old → new), read through `moved_std_module(old)`. The import refusal, the manifest refusal and the quick fix all read this one table.
- **The message:** `moved_std_module_message(old, new)` gives "`std::dom` moved to `std::web::dom`: std's modules are grouped under namespaces since v0.44.0, and the old path is gone — write `std::web::dom`".
- **The code:** `MOVED_STD_MODULE_CODE = "std-path/moved"`, with `std_path_diagnostic_code(msg)` and `moved_std_module_of_message`.
- **The fix:** `moved_std_module_fix(source, message, span) -> Option<StdPathFix { code, title, span, replacement }>`. It means "replace the old module segment with the new path": `dom` → `web::dom`, `rpc_server` → `rpc::server`.
- **Where the refusal anchors:**
  - at the old segment, on an import and inside brace lists;
  - `std::web` now resolves (it is the namespace), so the old web-prelude path is caught at the next segment, but only for a name the prelude exports (`std::web::Signal`, anchored back at `web`); a typo such as `std::web::dmo` stays an ordinary miss.
  - A path written in an expression or a type (`std::x::y` without an import) is already refused as "`std` is a namespace, not a value", so imports are the real surface.
- **The manifest:** `prelude = "std::web"` (or any moved module named as a prelude) is refused with "write `prelude = \"std::web::prelude\"`".
- **The LSP:** it publishes the code and offers "Write `std::web::dom`", pinned in `moved_std_path_tests.rs`.
- **Ledger:** two `NEW` rows. Rows 628 and 629 (R-e's `map_cell`/`set_cell` steers) now name `std::reactive::hash_*_cell`, so their prose in the proposals ledger needs updating.
- **Non-vacuity:** with the steer disabled, 8 of the 9 new pins went red.

### Latent bugs fixed along the way
- **A prelude in a module directory was never loaded or resolved.** The seed took exactly two path segments, and `prelude_module_scope` did not descend into a module's children. This is how it showed up: every web example lost `view` and `Signal`.
- **The four std inventories (B4 index, add-import candidates, auto-import table, contract) were top-level only.** A new `analyzer::modules_under_root(root, other_roots)` lists nested modules and skips a layer root nested inside the base. Nested modules named `prelude` are left out of the steer and candidate indexes, which keeps their answers exactly as before.
- **`infer_platform` now walks namespace segments.**
- **Chain frames name a module by its path** (`std::web::dom`), not its file stem.
- **The formatter declined any file with `[platform(..)] mod self;` plus `export *;`** (E181 put the marker above `mod self;`). Fixed and pinned.
- **The layer contract skipped nested modules,** so after the move `vilan check std` covered nothing in a layer. Fixed and pinned.

### Goldens and censuses that moved, and why
- **Corpus `.mjs`:** none moved.
- **Split fixture `app.js`:** two hoisted function declarations (`has_spawned`, `detached_nursery`) now come before `ensure_wired`. The canonical load drain orders modules by path, and `web::router` now sorts after `task`. The file has the same multiset of lines, so it is runtime-identical.
- **mdBook anchor golden:** regenerated with mdbook v0.5.4, because the std headings were renamed. The cross-page links (`#stdwebdocument`, `#stdrpcserver`, `#stdwebasset`) were updated to match.
- **Shared census:** the path keys changed and the table was re-sorted. Every count is the same, total 197.
- **Built examples, base vs tip:**
  - All other bundles are byte-identical or the same lines reordered.
  - `todo`'s `server.mjs` renames colliding helpers consistently (`body2` ↔ `body3`). That comes from the same load-order change.
- **Contract hashes do not move.** The hash spells a declaration by its declared name only, with no module path. Checked by building against both binaries: todo `e755843c`, walkthrough `4d7dcaad`, identical on base and tip.

### Gates on the final tip
All green:
- `cargo nextest run --workspace -j 6`: 9,620 passed, 33 skipped.
- `native_differential` with `VILAN_NATIVE_DIFFERENTIAL=1`: 161 passed.
- `deep_nesting` with `VILAN_CANARY_STACK_KIB=1536`: 18 passed.
- clippy `-D warnings`, `cargo fmt --check`, `ci-local.sh vilan-fmt`, `ci-local.sh wasm`.
- `ci-local.sh perf`: T2 verdict green, growth ×1.939.
- `ci-local.sh windows`: green.

**Windows and path separators:** module names are built from path components and joined with `::`. Overlay paths go through `components()`. The manifest only ever holds `::` paths. The shared census normalises `\` to `/`. No pin I added reads a separator. This is verified only by the cross-compile leg.

### Instructions on kolt's `vilan check`
Release builds, warm, `VILAN_SEQUENTIAL_CHECK=1`, `perf_count.py`:

| | Instructions |
|---|---|
| Base: origin/next binary and std, kolt plus the 3 pending patches | 25,664.6M (RSS 215 MB) |
| Tip: this branch's binary and std, the same kolt plus my patch | 25,747.2M (+0.32%, RSS 215 MB) |

- `--explain-cost` work units are identical on both.
- The fixed cost is flat: a trivial program is 0.3M cheaper on the tip.
- The examples are +0.03–0.24% (router highest).
- My best explanation is the reordered module loads and shifted entity ids (the same cause as the `body2`/`body3` renames), well within M116's ±2% item-placement band. I did not chase it further.

### The two patches
- **`layout-46/kolt-a154-std-paths.patch`:** 21 files.
  - It includes `scripts/lucide.mjs`: kolt's generated `src/lucide/lib.vl` spells `std::ui`, so the generator has to change.
  - It applies on kolt's working tree plus the three pending patches (`kolt-a152-message-row`, `kolt-a150-model-states`, `kolt-autofocus`). I applied all four to a fresh `cp` of kolt; no git command was run in kolt.
  - With the tip compiler: `vilan check` gives 0 errors and 0 warnings (once a build has regenerated lucide), `vilan build .` builds both legs, `fmt --check` is clean.
- **`layout-46/website-a154-std-paths.patch`:** 17 files. It covers site-46's table, plus `prelude = "std::web"` in `vilan.toml`, `worker.js`, the smoke script, `examples.test.mjs`, and the prose in the README, `dom.mjs` and `page.vl`.
  - I deliberately left the historical counter in `playground-restore.test.mjs` and `retired-examples.json` alone.
  - Verified on a scratch copy with the tip compiler: `vilan check` clean, `fmt --check` clean, build clean, and `node scripts/test.mjs` PASS on 6/6 files (the examples test uses the new manifest).
  - **Not verified:** the playground wasm smoke, which needs the v0.44.0 wasm. Per K29 ("just break"), a `?v=` link pinned to an older compiler will send a path that compiler doesn't know.

### Finds
They are in `newitems46-layout.json` with placeholder ids. Repros are in `layout-46/finds/`.
- **B?1** (blocks F28 for `router`): a file that declares `[platform("browser")] mod self;` and imports a twin module gets the other twin's functions reported as fence violations in a build for the other platform, even when nothing reaches them. It reproduces in user code too.
- **B?2** (pre-existing): importing `std::web::document` in a browser build fails inside std, because `escape_attribute` and `escape_text` exist only in the process twin.
- **E?3:** `infer_platform` should treat a browser-only file declaration as browser evidence. F28 needs this first.
- **E?4:** the auto-import table and the add-import fix still read a package's own nested modules at the top level only.
- **E?5:** the moved-path fix on `std::web::{ Signal, dom::x }` breaks the sibling `dom::x` (a rare shape).
- **Filed as fixed:** B?6 (prelude in a module directory), B?7 (formatter), N?8 (contract coverage).

### Needs the owner's ruling
1. **F28's first half needs a decision.** It needs B?1 (the fence walk should skip a fenced body this build's platform doesn't admit) and E?3 before it can move. Also: is the label change from "layer of `std`" to "platform its file declares" acceptable once it does?
2. **`vilan check --fix` covers numeric fixes only.** Do you want it to apply the moved-path fix too? It's a small addition, but it changes that command's report wording.
3. **The website must take its patch before its first deploy after v0.44.0.**
4. **`std::null` and `std::js::null` cannot appear in an import path at all,** because `null` is a keyword. The old path therefore has no refusal pin; it was never importable in the first place.
