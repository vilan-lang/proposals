# layout-46 census: every std path the tree names (A154 + F28's first half)

Taken on `origin/next` @18c2a059 before any change. The checklist for step 2.
Pattern for the textual counts: `\b(std|pkg)::(dom|ui|style|dev|router|storage|document|asset|web|hash_map_cell|hash_set_cell|transient|store|store_core|delta|null|promise|native_map|rpc_server)\b`,
over `git grep`, excluding `CHANGELOG.md` (history is not rewritten) and the stray root
`REPORT-*.md` files. `macro_std::` names none of the moved modules (0).

**Total: 1,706 references in 229 files**, plus 52 `"std::web"` / `WEB_PRELUDE` string sites
(next table) and the special resolutions below, which spell a module as a bare string and
match no pattern.

## Per old module

| Old | Refs | | Old | Refs |
|---|---|---|---|---|
| `dom` | 97 | | `hash_map_cell` | 6 |
| `ui` | 488 | | `hash_set_cell` | 5 |
| `style` (incl. `style::prelude`) | 438 | | `transient` | 20 |
| `dev` | 37 | | `store` | 78 |
| `router` | 65 | | `store_core` | 7 |
| `storage` | 23 | | `delta` | 18 |
| `document` | 42 | | `null` | 1 |
| `asset` | 155 | | `promise` | 15 |
| `web` (the prelude) | 102 | | `native_map` | 14 |
| | | | `rpc_server` | 95 |

## Per category (refs / files)

| Category | Refs | Files |
|---|---|---|
| std's own sources (`pkg::` imports, doc comments, macro bodies that emit `std::…`) | 152 | 28 |
| vilan-core `src` (incl. inline unit tests) | 120 | 15 |
| vilan-cli `src` | 5 | 2 |
| `vilan init` templates (`crates/vilan-cli/templates`) | 12 | 7 |
| vilan-lsp `src` (mostly inline tests in `document.rs`) | 97 | 6 |
| vilan-ide `src` (completion tests) | 5 | 2 |
| vilan-wasm (tests) | 15 | 1 |
| vilan-rust / vilan-rt `src` (comments) | 10 | 4 |
| vilan-core `tests` (inference pins, module_resolution, std_twin_parity, …) | 634 | 30 |
| vilan-cli `tests` (incl. 8 native fixtures, the split project, the ledger TSV) | 358 | 46 |
| docs (`vilan/docs`: std pages, guide, spec, tour, appendix, README) | 198 | 38 |
| examples (`vilan/examples`) | 76 | 33 |
| corpus (`vilan/test/*.vl`) | 11 | 9 |
| benchmarks | 2 | 2 |
| scripts (`soak.sh`, `wasm-smoke.mjs`, `perf_genapp.py`, `cut-release.sh`) | 8 | 4 |
| editors/vscode | 2 | 1 |

## `prelude = "std::web"` / `WEB_PRELUDE` (52 sites in 50 files)

- `manifest.rs` `WEB_PRELUDE` (the constant) + 3 manifest unit tests; analyzer.rs ×3 (the web-set
  steer reads it; `build_web_prelude_index_if_needed` takes its LAST SEGMENT as the module file
  name — must become the full nested path); css.rs doc ×1.
- vilan-wasm `PlaygroundPrelude::recommended_for` (browser mode) + its test.
- `vilan init`: browser + fullstack `vilan.toml`, node's comment, three template `.vl` comments.
- vilan-cli `main.rs` (a steer comment), tests: native_differential, workspace; vilan-core tests:
  chunks ×3, modules, styling, module_resolution; vilan-lsp `document.rs` ×7.
- docs ×9 (errors appendix, glossary, walkthrough ×2, names spec, hello-vilan, projects ×3).
- examples: 10 `vilan.toml` + 12 source comments; `scripts/perf_genapp.py`.
- `std/src/web.vl` (its own header).

## Special resolutions (a module named as a bare string or by file path)

The compiler finds these modules by NAME, not by an import. Each is a site step 2 must move.

| Site | What | Old → new |
|---|---|---|
| `elements.rs:129` | element syntax's hygienic callee `Node::StdItem("ui", "view")` | `"web::ui"` |
| `css.rs:142, 248` | `css { }`'s `StdItem("style", "style")`, `StdItem("style", "piece")` | `"web::style"` |
| `analyzer.rs` `resolve_prepped_std_item` | `std_item_id(&[module], item)` takes ONE segment | split the module path on `::` |
| `analyzer.rs` `collect_std_item_modules` | seeds the loader with the StdItem's module | carries the nested path |
| `analyzer.rs:57029` | the css-ambient style prelude `std_item_id(&["style", "prelude"], ..)` | `["web", "style", "prelude"]` |
| `analyzer.rs:70482` | always-loaded core modules `"null"`, `"promise"` | `"js::null"`, `"js::promise"` |
| `analyzer.rs:71847` | `module_scopes.get("asset")` (the const channel) | `"web::asset"` |
| `analyzer.rs:71919/71925` | `module_scopes.get("dev")` (HMR stash/take) | `"web::dev"` |
| `analyzer.rs:71959` | primitive `null`'s module `("null", "null")` | `"js::null"` |
| `analyzer.rs:72043` | `module_scopes.get("native_map")` (`NativeMap`) | `"js::native_map"` |
| `analyzer.rs:72143` | `module_scopes.get("promise")` (`Promise`) | `"js::promise"` |
| `analyzer.rs:73227` | `module_member("dom", "query_selector_all")` | `"web::dom"` |
| `analyzer.rs:5866–5893` | R-e's steer tables (`std::hash_map_cell now`) | prose to `std::reactive::hash_map_cell` |
| `analyzer.rs` `std_module_files` (via `modules_in_root`) | the B4 import steer's std index: TOP-LEVEL modules only | must list nested modules or every steer into a moved module goes silent |
| `analyzer.rs` `build_web_prelude_index_if_needed` | finds the web prelude's file by `WEB_PRELUDE`'s last segment (`web`) | the full nested path |
| `analyzer.rs` `check_library_contract` / `modules_in_root` | the layer contract walks TOP-LEVEL modules only, by directory | nested modules + the file fence (F28) |
| `lib.rs` `infer_platform` | `std::<module>` single segment; "served only by the browser layer" by directory | nested path; the file fence (F28) |
| `platform_color.rs` `frame_label` | a chain frame's module is `library::file_stem` | the path under the root (`std::web::dom`) |
| `init_order.rs:251` | `transient` seal matched by file name `transient.vl` | unchanged (file name kept) |
| `vilan-lsp` `import_candidates` | add-import candidates from `modules_in_root` (top level) | nested listing |
| `vilan-ide` completion auto-import index | `modules_in_root` per origin root | nested listing |
| `vilan-wasm` | `recommended_for(Browser)` = `WEB_PRELUDE` | follows the constant |
| std `rpc.vl` macros (`[rpc]`, `[service]`, `[client_service]`) | expansions that spell `std::rpc_server::…`, `std::transient`, `std::store…` as strings | rewritten |
| std `store.vl` derive (`Storable`) | expansion imports `std::store_core` | `std::reactive::store_core` |
| std `wire.vl` / `json.vl` derives | checked: no moved path | — |
| bindgen output | checked: emits no std import | — |

## File-path references (a moved FILE named by its path)

~180 references in ~70 files: `std_twin_parity.rs` (`browser/ui.vl`, `process/ui.vl`),
`shared_census.rs` (19: per-file `Shared::new` counts keyed by path), `style_table_sync.rs`
(`style.vl`), `mime_table_sync.rs` + `regen-mime-table.py` + `mime-table.tsv` +
`AGENTS.md` (`process/build.vl`), `docs.rs`, `module_resolution.rs` (21), `workspace.rs`,
`diagnostics.rs`, `document.rs` (37), `formatter.rs` (17, the std fixed-point list),
`diagnostic_determinism.rs`, `embedded_std.rs`, `vilan-rust`/`vilan-rt*` comments, std's own
comments, the docs (walkthrough, platforms, services), examples' READMEs/manifests.

## Tests that spell std paths and must be re-read (editor-46's note)

E250 pins `std::fetch`, `std::json`, `std::hash`, `std::hash_map` (none move); E251 `std::json`
(no move); E249 `std::reactive` (no move).
