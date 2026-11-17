# Standard library survey (read-only), 2026-11-17

Subject: `vilan/std/src/` on branch `next` in the worktree
`/home/reed/code/vilan-lang/vilan/.claude/worktrees/integration`, tip dated 2026-11-16 (v0.56.1 is the latest release).
Nothing was built or run. Every number below came from `wc`, `grep`, `git log` or reading source; where a claim is an
inference from reading rather than a measurement, it says so.

Note on paths: the worktree root holds `crates/`, `vilan/`, and so on. The std is at `vilan/std/src`, the book at
`vilan/docs`, packages at `vilan/packages`, the test corpus at `vilan/test` (162 `.vl` programs).

## 0. Headline numbers

- 62 top-level entries in `vilan/std/src` (files + directories); **90 `.vl` files**; **65,908 lines** (`cat | wc -l`).
- Std is a layered library (`vilan/std/vilan.toml`): a core root, a `process` layer (`@process`: node and native) and a
  `browser` layer. `std::web::ui` exists twice: `browser/web/ui.vl` (3,056 lines, live DOM) and `process/web/ui.vl`
  (1,097 lines, SSR string tree); the two are twins and are counted separately below.
- `std::term` does not exist. Terminal input lives in `std::process` (`keys()`, `KeyDecoder`, `prompt`) and the native
  runtime crate `vilan-rt-term`. `std::canvas` is listed in the native differential's `PLATFORM_MODULES` but there is no
  such module in std (a stale entry).
- Native backend: `crates/vilan-rust/src/lib.rs` (19,380 lines; plus `dbg.rs`); runtime `crates/vilan-rt` plus `-rt-crypto
  -rt-gfx -rt-image -rt-net -rt-poll -rt-signal -rt-sqlite -rt-term -rt-webview`. Differential suite:
  `native_differential.rs` (19,378 lines, 411 `#[test]`s) plus 210 probe programs in `crates/vilan-cli/tests/native/`,
  over the 162-program corpus.

## 1. How native status was determined

1. Host-bound std members are `external` declarations with `[extern("module","symbol")]`. The Rust emitter maps them in
   `crates/vilan-rust/src/lib.rs` through a chain of `*_host_binding` functions called from `lowered_host_binding_in`
   (about line 13253): `runtime_host_binding` (executor, J6), `http_host_binding`, `ws_host_binding`, `json_host_binding`,
   `scalar_host_binding`, `math_host_binding`, `host_module_binding` (fs, crypto hash, process, url, time, term),
   `db_host_binding`, `image_host_binding`, `window_host_binding`, `gfx_host_binding`, `crypto_host_binding`.
   Receiver-keyed methods are in a separate match near lines 12575-12615 (`RawStat`, `FsOptions`, `RawEntry`,
   `HostDate`, `NodeHash`...).
2. An `external` with no arm falls to `host_gap(..)` (line 17598): a refusal "by name" in a normal build; under
   `VILAN_NATIVE_HOST_CENSUS=1` it records the gap and emits `unimplemented!()`. There is no static table of refusals,
   so "refused" below means "no mapping arm found by grep" plus, where one exists, a test that pins it.
3. A crude script (scratchpad only) matched each std `external` name or symbol against the quoted strings in `lib.rs`.
   It is only a hint: intrinsics with no `[extern]` string (list/string/shared/option operations) show as "misses" but
   are handled by the emitter's intrinsic path, so I did not use it to downgrade a module.
4. Differential programs: `DEFAULT_SUITE` (39 listed programs), `ASYNC_SUITE` (7), `PLATFORM_BOUND_REQUIRED` (9), plus a
   sweep of every other corpus program that reaches no module in `PLATFORM_MODULES` (19 names, incl. the non-existent
   `std::canvas`). Exclusion lists are tiny: `OUTSIDE_THE_DIFFERENTIAL` has ONE entry (`usize-underflow.vl`: unspecified
   result), `PLATFORM_BOUND_OUTSIDE` has ONE (`lens-rope.vl`: prints wall-clock timings). Everything else is "identical,
   or refused by name".
5. Docs/code disagreement: `vilan/docs/guide/native.md` still says a `resource` type with a `Drop` impl is refused
   natively ("its own slice"), but tests `a_resource_without_drop_builds_the_same_on_both_backends` and
   `a_resource_enum_with_drop_and_its_struct_twin_build_natively` (native_differential.rs 10553, 10667) show Drop types
   build. The book sentence is stale. `File`/`Watcher` are refused for their handle externals, not for Drop.

## 2. Part 1: the module map

Columns: LOC (`wc -l`), last commit date on `next` in 2026 (MM-DD), hosts (from `[platform(..)] mod self;` or its
absence: "core" = no attribute, so every target), native status, book (a topic page under `vilan/docs/std/` or the
book names the module). Dates: many files carry a date from a bulk reformat or sweep, so a recent date does not prove
active design work. Only three small files are older than 60 days (before 2026-09-18).

### 2.1 Core (all hosts)

| Module | LOC | Last | Purpose | Native | Book |
|---|---|---|---|---|---|
| `std::arena` | 142 | 09-25 | generational arena, `Handle<T>` | works (`option-view.vl` pins `Arena::get`) | cells/collections |
| `std::base64` | 222 | 11-09 | base64url and standard base64, pure vilan | works (`f158` pin) | encoding.md |
| `std::binary` | 456 | 09-25 | compact binary codec for Wire types | works (`f156` f64 DataView pin) | encoding.md |
| `std::boolean` | 13 | 09-14 | `bool` nominal type | works | one mention |
| `std::bytes` | 146 | 10-02 | `Bytes` buffer | works (22/22 externs; aliasing pin) | encoding.md |
| `std::compare` | 338 | 10-16 | `PartialEq`/`Ord`, list sorting | works | traits.md |
| `std::context` | 45 | 09-29 | dynamically scoped value | works (threading pass lowers it to parameters; inferred) | yes |
| `std::crypto` | 59 | 09-29 | SHA-2, HMAC, PBKDF2, random bytes, uuid | works (7/7; `the_crypto_surface_answers_nodes_bytes`) | encoding.md |
| `std::debug` | 424 | 11-02 | `Debug` derive, `dbg`, `dbg_stack` | works (s1/s2/e283 dbg pins) | debug.md |
| `std::default` | 74 | 10-15 | `Default` for scalars | works | traits.md |
| `std::display` | 138 | 10-05 | `Display`, `format` | works | yes |
| `std::drop` | 24 | 09-22 | `Drop` trait | works (see sec. 1 item 5) | yes |
| `std::fetch` | 231 | 09-24 | HTTP client over host `fetch` | **refused** (no mapping for `fetch_with`, `Response`, `RequestInit`, body stream; 4/21 externs matched) | net.md |
| `std::hash` | 183 | 10-10 | `Hashable`, canonical `Hash` | works | collections.md |
| `std::hash_map` | 248 | 11-03 | `HashMap` | works | collections.md |
| `std::hash_set` | 213 | 11-02 | `HashSet` | works | collections.md |
| `std::into` | 5 | 09-14 | a bare `Into<T>` trait, no implementors | n/a (declaration only) | no mention |
| `std::io` | 29 | 10-26 | `print`, `panic`, `assert`; `write` | works | yes |
| `std::iterator` | 394 | 10-26 | `Iterator` protocol and adapters | works | yes |
| `std::json` | 1702 | 11-09 | JSON parse/encode, `derive(Json)` | works (30/36 externs, rest intrinsics; derive + roundtrip in DEFAULT_SUITE) | encoding.md |
| `std::jwt` | 58 | 09-22 | HS512 JWT over Wire claims | not determined (pure over crypto/base64; no native probe; 0 Rust tests mention it) | one mention |
| `std::lib` | 12 | 09-22 | comment only; re-exports nothing | n/a | - |
| `std::list` | 232 | 10-15 | `List<T>` | works | collections.md |
| `std::markdown` | 1052 | 09-25 | markdown parser to AST (docs tooling) | not determined (pure; no native probe) | markdown.md |
| `std::math` | 146 | 09-22 | constants, generic min/max | works | numbers.md |
| `std::memo` | 121 | 09-29 | `Memo<K,V>` per-key cache (`get_or` deprecated) | not determined (pure; 1 Rust test mention) | yes |
| `std::number` | 2146 | 09-29 | numeric types, `Math.*`, conversions | works (97/98; scalar and math host bindings) | numbers.md |
| `std::operators` | 111 | 09-22 | `Add`, `Try` (`!`) | works | traits.md |
| `std::option` | 513 | 11-09 | `Option` | works | option-result.md |
| `std::path` | 386 | 10-09 | path arithmetic, "colour: none" | works (pure) | paths.md |
| `std::prelude` | 31 | 10-09 | base prelude, 8 names | works | one mention |
| `std::random` | 44 | 09-22 | `range(low,high)` | **refused** (no arm for `range_i32/u32/f64`; listed in `PLATFORM_MODULES`) | yes |
| `std::range` | 30 | 09-14 | `Range` | works | yes |
| `std::result` | 237 | 10-13 | `Result` | works | option-result.md |
| `std::shared` | 210 | 10-09 | `Shared<T>` cell | works | yes |
| `std::string` | 129 | 09-25 | `str` impls | works | strings.md |
| `std::task` | 184 | 10-03 | `Task`, `nursery`, cancel | works (J6 executor; `ASYNC_SUITE`) | yes |
| `std::time` | 482 | 11-09 | `Instant`, `Duration`, sleep, debounce | **partly**: clock, `to_iso`, sleep, timers work; `__with_finally_async` (Debounce) refused (9/10 externs) | time.md |
| `std::tuple` | 78 | 09-28 | walkable tuples | works | yes |
| `std::url` | 27 | 11-02 | percent-encode/decode | works (`vilan_rt::url`) | paths.md |
| `std::wire` | 743 | 09-29 | codec-neutral serialization | works | encoding.md |
| `std::ws` | 249 | 10-26 | RFC 6455 frame layer, pure bytes | works (inferred; used by the native rpc server) | one mention |
| `std::js::hash_table` | 37 | 11-02 | raw JS `Map` by `Hash` (internal) | works (emitted as `HashTable`) | internal |
| `std::js::native_map` | 63 | 11-02 | table under `HashMap`/`HashSet` (internal) | works (`vilan_rt::NativeMap`) | internal |
| `std::js::null`, `std::js::promise` | 4, 17 | 10-04 | `null`, `Promise<T>` | works | internal |

### 2.2 Process layer (`[platform("@process")]`: node and native)

| Module | LOC | Last | Purpose | Native | Book |
|---|---|---|---|---|---|
| `std::build` | 428 | 10-26 | what the build emitted | works (`module_dir` mapped to empty) | yes |
| `std::db` | 564 | 11-09 | SQLite (`node:sqlite` / `vilan-rt-sqlite`) | works (19/19; `db.vl` required) | yes |
| `std::fs` | 1022 | 10-26 | filesystem | **partly** (Part 2a, 48%) | paths/process.md |
| `std::gfx` | 1667 | 11-13 | GPU window, frame primitives, `Dp`, paths | native only (37/41 externs; the rest handle structs) | gfx.md |
| `std::http` | 1751 | 11-10 | HTTP server builder | works (42/42; real-socket tests) | net.md |
| `std::image` | 173 | 11-02 | decode/resize/encode images | works (9/10; `m185_image_is_identical`) | image.md |
| `std::io::stdout` | 19 | 10-26 | unbuffered write | works | yes |
| `std::process` | 688 | 11-03 | args, env, exit, stdin, keys, prompt | works (A173 S1/S2 pins) | process.md |
| `std::watch` | 71 | 10-09 | dev-mode flag, `force_refresh` | **refused** (imports `std::fetch::post`) | dev.md |
| `std::window` | 94 | 11-10 | desktop webview window | native only (`vilan-rt-webview`) | window.md |
| `std::web::document` | 980 | 10-16 | HTML shell held against the build | not determined (no native probe) | browser.md |
| `std::rpc::server` | 1535 | 10-26 | rpc server on `std::http` | works | rpc.md |
| `std::ui` | 2719 | 11-13 | native UI element tree | native only | ui.md |
| `std::ui::kit` + buttons, checkboxes, inputs, lists, text_areas, editing, heights | 23 / 223 / 59 / 176 / 958 / 193 / 1027 / 282 | 11-12..13 | controls with behaviour, no look | native only | ui.md |
| `std::web::ui` (process twin) | 1097 | 11-03 | SSR string tree, browser's public surface | works (`element-syntax.vl` is in `PLATFORM_BOUND_REQUIRED` and imports it); the book's "std::web::ui refused" means the browser layer | browser.md |

### 2.3 Browser layer and shared web

| Module | LOC | Last | Purpose | Hosts | Native | Book |
|---|---|---|---|---|---|---|
| `std::web::ui` (browser twin) | 3056 | 11-12 | declarative fine-grained DOM views | browser | refused | browser.md |
| `std::web::dom` | 865 | 11-03 | DOM bindings (3/82 externs matched) | browser | refused | browser.md |
| `std::web::router` | 449 | 11-02 | history-API routing, enum routes | browser | refused (0/5) | guide/routing.md |
| `std::web::storage` | 191 | 10-09 | local/session storage | browser | refused | browser.md |
| `std::web::dev` | 66 | 10-09 | HMR app surface | browser | refused | dev.md |
| `std::web::remote` | 34 | 10-10 | mirrored-store handles as content | core (no attr) | not determined (rides `std::web::ui`) | no page |
| `std::web::style` | 3256 | 11-02 | typed atomic styles, compiled CSS | core | not determined (const-time asset channel; no native probe) | style.md |
| `std::web::style::prelude` | 287 | 10-31 | css-block hole aliases | core | not determined | style.md |
| `std::web::asset` | 251 | 10-04 | compile-time asset channel | core, const-only | works for compile-time use (`estate.vl`) | yes |
| `std::web::prelude` | 65 | 10-04 | web prelude | core | n/a | yes |

### 2.4 Reactive and rpc (core)

| Module | LOC | Last | Purpose | Native | Book |
|---|---|---|---|---|---|
| `std::reactive` | 4393 | 11-08 | signals, cells, effects, batch, owners | works (list-cell, flatten, selector, a138, a142 pins) | reactive.md, cells.md |
| `reactive::delta` | 3884 | 11-12 | change structure, `DeltaLog` | works | cells.md |
| `reactive::hash_map_cell` | 717 | 11-02 | `HashMapCell` | works (a138 pin) | collections |
| `reactive::hash_set_cell` | 368 | 11-02 | `HashSetCell` | works | collections |
| `reactive::store`, `store_core` | 3030 + 1434 | 11-02, 11-03 | `Store<T>` per-field handles | works (a142_s7, a149_s3 pins) | store.md |
| `reactive::transient` | 492 | 10-16 | values that come and go | works | transient.md |
| `reactive::trace` | 324 | 11-03 | wake tracer | works | debug.md |
| `reactive::lens` | 3026 | 11-09 | one wrapper for any structure (A185) | builds natively since B709; leaks cells (B717) | lens.md |
| `reactive::lens::loaded` | 1290 | 11-09 | loaded collections, optimistic overlay | refused on "other native gaps" per tracker (lens-loaded/-tasks/-overlay) | loaded.md |
| `std::rpc` | 7973 | 11-09 | rpc client/service, mirrors, transports | works (client over `ws://`, server; pins) | rpc.md |
| `rpc::mirror` | 2280 | 11-02 | mirrored store protocol | works (a153 pins) | rpc.md |

### 2.5 Stale or unowned candidates (judgement, with evidence)

- `std::into` (5 lines): a trait with no implementor in std and no mention in test or docs. Looks orphaned.
- `std::watch` (71): refused natively because it imports `std::fetch`; the book folds it into dev.md. The book says
  `--watch` is not native by design, so this is one-sided by design.
- `std::fetch` (231) and `std::random` (44): core-labelled modules with no native binding, the only two. They break the
  "core means every target" promise, and nothing in the platform check can say so (no attribute).
- Zero importers inside std: `jwt`, `markdown`, `memo`, `arena`, `binary`. Corpus programs naming them: jwt 1, arena 1,
  binary 1, memo 0, markdown 0. They are user-facing leaves, not dead; `markdown` serves the docs site.
- `std::web::remote` (34 lines, no page of its own), `std::ws` (no page of its own, 0 corpus programs).
- Deprecated markers inside std: `memo.vl:95` (`get_or`), `web/style.vl:2726` and `:2794` (attribute conditions),
  `reactive.vl:2245` and `:2251` (`scoped_effect`, `scoped_effect_on_change`). No whole-module deprecation.
- Oldest files: `boolean.vl`, `into.vl`, `range.vl` (2026-09-14, 64 days), all trivial. Nothing is older than that.
- Superseded or half-migrated: `ListCell`/`HashMapCell`/`HashSetCell`/`Store` are meant to be re-founded on
  `std::reactive::lens` (R1) but are not; the lens sits beside them. `std::web::ui` (browser) is the older UI stack,
  `std::ui` + `std::gfx` the native one.
- Book coverage: `docs/std/` is 27 topic pages (13,228 lines), not per-module; "no page" means not named in
  `docs/std/*.md` by `grep std::<name>`.

## 3. Part 2: deep dives

### (a) `std::fs`: 48% native (21 of 44 callables); 45% counting types

Source `vilan/std/src/fs.vl`, 1,022 lines, `[platform("@process")]`. JS = node `node:fs/promises`; tests exist
(`vilan/test/file.vl`, `watch.vl`; 128 Rust test files mention fs) but I ran nothing, so the JS column is "implemented
over node", not a measurement.

Native evidence: arms in `host_module_binding` (lib.rs ~13760-13835) for `readFile`, `writeFile`, `appendFile`, `copyFile`,
`rename`, `unlink`, `readdir`, `mkdir`, `rmdir`, `rm`, `cp`, `__fs_stat`, `__fs_read_dir_all`, `new_fs_options`; receiver
arms for `RawStat`, `FsOptions`, `RawEntry` (lines 12590-12615); runtime `crates/vilan-rt/src/fs.rs`. No arm for
`open_with_flags`, `raw_read`, `raw_write`, `raw_handle_stat`, `truncate`, `sync`, `data_sync`, `__fs_close`,
`__fs_close_awaited`, `__fs_watch`, `next_change`, `__fs_watch_stop`, `RawChange.kind`. The refusal is pinned in
`native_differential.rs:11599` (`std::fs::with_file` refused at the user's call, naming `with_file`'s body in `fs.vl`).
Pin for the working half: `f156_fs_options_calls_are_identical_on_both_backends`. F185 says the same; code and
`guide/native.md` agree with it.

| Member | JS | Native |
|---|---|---|
| read_file_encoded, read_bytes, write_file, write_bytes, read_file_to_str | yes | works |
| rename, write_atomic, write_bytes_atomic, append, copy, remove, update | yes | works (atomic ones use `random_uuid`) |
| read_dir, read_dir_all, scan_dir (+ `Entry`), stat (+ `Stat`) | yes | works |
| create_dir, create_dir_all, remove_dir, remove_dir_all, copy_dir | yes | works (F156) |
| `File::open/create/create_new/append_to/modify` (5) | yes | refused |
| `File::read_at/write_at/stat/truncate/sync/data_sync` (6) | yes | refused |
| `with_file`, `with_file_create/_create_new/_append/_modify` (5) | yes | refused |
| `Reader::of/next/position/seek` (4) | yes | refused |
| `Watcher::watch/watch_all/next` (3) | yes | refused |
| types: `Entry`, `Stat` work; `File`, `Reader`, `Watcher` refused; `Change`, `ChangeKind` are plain data unusable without a watcher | | |

Count: callables 21 + 11 + 5 + 4 + 3 = 44; native 21 = **47.7%**. With the 7 public types (2 work): 23 of 51 = **45%**.
The `Drop` impls of `File`/`Watcher`/`Reader` are not counted.

### (b) The reactive stack and the lens migration

Sources: `proposal/reactive-lens.md` (863 lines; rulings 10a, slices 11, status 21.4-21.7), tracker A185 (stamps through
2026-11-09), `git log` on the lens files. Nothing about A185 landed on `next` after 2026-11-09.

| Slice | What | State |
|---|---|---|
| S0 | paper + rulings R1-R17 | done (2026-11-08) |
| S1 | `std::reactive::lens` | landed (c56ae837), shipped v0.55.0 |
| S2 | keyed side, `Indexed`/`Membership`, sorted/set/rope shapes, B715 fixed | landed (98b7334f), v0.55.0 |
| S3 | slim write path, `settle_together` | landed (b7a6b62e), v0.55.0 |
| S3b | `ListCell` then `HashMapCell`/`HashSetCell` re-founded on the lens | **parked** on M194 (analyzer cost per std module) and the lens's resting heap; T4 tried twice and refused (x1.48 bare writes, x3.3 heap, +21-29% compile cost) |
| S4 | fields and nested lenses | **waiting** on B711 S1 (struct keys; open) |
| S5 | `lens::loaded`, overlay | landed (54f14a47), v0.55.0 |
| S6 | the wire: patch vocabulary, `KeyedCell`/mirror onto it | not started (needs versions on frames) |
| S7 | `Store` on the lens | not started |
| S8 | kolt exhibits | not started |

**Percentage 1, slices landed / planned: 5 of 10 listed slices (S0, S1, S2, S3, S5) = 50%; excluding paper-only S0,
4 of the 9 implementation slices (S1, S2, S3, S3b, S4, S5, S6, S7, S8) = 44%.** The four that landed are exactly the
ones the paper marks additive ("S1, S2, S3 and S5 are additive"); none of the slices that can break something (S3b, S6,
S7) has landed.

Old types and whether they sit on the lens:
- `SignalCell`, `Source`, `batch`, turns: the base. The lens is built ON `SignalCell` (one notification cell per lens).
- `ListCell`, `HashMapCell`, `HashSetCell`: own `DeltaLog` machinery; unchanged (R17: "ListCell stays off it").
- `KeyedCell`, `Store`/`store_core` (4,464 lines), the rpc mirror and `std::web::remote`: own machinery; S6/S7 unstarted.
- Re-founded on the lens: **0 of 6** (ListCell, HashMapCell, HashSetCell, KeyedCell, Store, mirror).

Consumers using the lens (grep for `reactive::lens`, `std/src` and `/home/reed/code/kolt/{src,lib}`):
- std: only `reactive/lens.vl` (3,026) and `reactive/lens/loaded.vl` (1,290); `reactive.vl:4382` has an `[internal]` hook
  for it. **0 of the other 88 std files import it**: `std::web`, `std::ui`, `std::rpc` all 0.
- Kolt (161 `.vl` files, 85,048 lines): **0 lens hits**. For comparison: `Store`-related hits 206 across 41 files,
  `SignalCell`/`Signal<` 451, `ListCell` 11 in 4 files, `HashMapCell`/`HashSetCell` 0.
- Its users are its own pins: 11 `vilan/test/lens-*.vl`, `crates/vilan-cli/tests/reactive_lens.rs`, `docs/std/lens.md`,
  `docs/std/loaded.md`.

**Percentage 2, adoption: about 0% of consumer code (0 of 6 types re-founded; 0 of 88 other std files; 0 of 161 Kolt
files).** The lens module itself is 4,316 lines = 6.5% of std's 65,908, shipped and fuzz-tested but with no dependants.
Related open: B717 (lens cells stay live at exit natively), B711, M194, B712.

### (c) `std::rpc` and mirrored stores

Size: `rpc.vl` 7,973 + `rpc/mirror.vl` 2,280 + `rpc/server.vl` 1,535 = 11,788 lines.

Open bugs in INDEX.md (line references still match the code, so not stale): B702 (`ReactiveServer::revoke`,
rpc.vl:3167, sends the client no frame), B703 (`release_grant`, mirror.vl:669, never acks a released base slot: client
leak), B704 (a Subscribe naming an unknown base drops the rest of its frame, mirror.vl:566), B614 (non-Wire derive
diagnostic restated at the attribute). Design/feature: A76 (SSE leg has no reverse lane), A81 (awaited server to client
calls), A97 (raw double-subscribe holds a channel), A175 (revoke by value, depends on B702). Perf: M136, M173, M120, M178.
N196: the std full-scan check does not reach nested std modules (rpc, lens).

Native: yes, substantially. Native rpc server (`Service::new`/`factory`, WebSocket upgrade, `[expose]`/keyed mirrors)
and client (`ws://` only, no TLS) are pinned against node (`the_keyed_rpc_service_answers_a_node_client...`,
`f1_s1b_a_native_rpc_client...`, `an_in_process_mirror_program...`, `a153_s1..s4`, `a168`, `b606`, `b746`, `m165`).
`wss://` is refused at dial time.

### (d) `std::web`

Size: browser layer ui 3,056 + dom 865 + router 449 + storage 191 + dev 66 = 4,627; shared style 3,256 + style/prelude 287
+ asset 251 + document 980 + remote 34 + prelude 65 = 4,873; SSR twin 1,097. Total 10,597 lines (16% of std).
Test signals (files mentioning the module name): Rust tests `std::web::ui` 25, `style` 13, `dom` 9, `router` 7, `document`
4, `storage` 3 (`router.rs`, `ssr_differential.rs`, `ssr_fullstack.rs`, `ui_*.rs`, `dom_events.rs`, `hmr*.rs`,
`style_*.rs`, `document.rs`, `mount_missing_id.rs`, `element_head_order.rs`); corpus programs (including examples) `ui` 3,
`style` 7, `router` 4. No test files live inside the std tree (`find std -name '*test*'` is empty). Open items touching it:
A7, A72, A106, B734, B737, E182, E292, F15, M59, M101, M163, M174, M192, M202 (typed elements cost every web element a
head, x1.0054 on genapp). Deprecated markers in `style.vl`: 2.

### (e) One line each

- `std::db`: SQLite, 564 lines, works on both (node:sqlite, `vilan-rt-sqlite` natively); untyped-column affinity differs.
- `std::http`: server builder, 1,751 lines, native 42/42 externs, node-identical heads except `Date`; no TLS/HTTP2 natively.
- `std::crypto`: 59 lines, SHA-256/384/512, HMAC-SHA-512, PBKDF2, random, uuid; native yes.
- `std::image`: 173 lines over the `vilan-image` crate (wasm on JS, native on Rust); identical on both.
- `std::time`: 482 lines; native except Debounce's `with_finally_async`.
- `std::json`: 1,702 lines; native yes.
- `std::process`: 688 lines; args, env, cwd, exit, stdin lines/bytes, raw keys, prompt; native yes (A173).
- `std::term`: does not exist; its job is `std::process::keys` plus `vilan-rt-term`.

### (f) gfx, ui, kit, window (native only; counts are grep-approximate: indented-or-not `fun` definitions, and top-level `export` declarations)

| Module | LOC | fun defs | exported decls |
|---|---|---|---|
| `std::gfx` | 1667 | 145 | 68 |
| `std::ui` | 2719 | 213 | 110 |
| `std::ui::kit` (root) | 23 | - | re-exports |
| `kit::buttons` | 223 | 26 | 16 |
| `kit::checkboxes` | 59 | 5 | 7 |
| `kit::inputs` | 176 | 13 | 5 |
| `kit::lists` | 958 | 39 | 11 |
| `kit::text_areas` | 193 | 14 | 5 |
| `kit::editing` (internal) | 1027 | 56 | 1 |
| `kit::heights` (internal) | 282 | 15 | 0 |
| `std::window` | 94 | 7 | 4 |

All are `@process`; `docs/std/gfx.md`, `ui.md`, `window.md` say "Native only": the JS build refuses a program reaching them
by name, `vilan check` accepts them.

## 4. Part 3: packages

`vilan/packages/` holds one package: `lucide` (6 files, about 8,009 lines of `.vl`, last commit 2026-11-13).
- Contents: `vilan.toml` (a `[library]` named `lucide`, `generated = "src/icons"`), `src/lib.vl` (hand-written re-export),
  `src/icons/lib.vl` (generated, one `export fun <name>(): Icon` per icon), `icons.tsv` (2,004 lines of generated data
  read by the GPU crate's sweep), `LICENSE`, `README.md`.
- Generated by `scripts/lucide-native.mjs` (Node, no packages) from `lucide-static` 1.64.0, pinned by sha512 in the README:
  1,999 icons; `node scripts/lucide-native.mjs generate ~/lucide/package vilan/packages/lucide`. It refuses any icon it
  cannot flatten. Test: `crates/vilan-cli/tests/lucide_package.rs`.
- Use: path dependency, `lucide = { path = "../../packages/lucide" }` under `[package.dependencies]`, then `import lucide;`
  and `lucide::check()`. Drawing is native only (a `std::ui` value); the data reads on JS too. Kolt keeps its own generated
  lucide under `kolt/lib/` (not examined).
- Registry: none. `docs/spec/platform.md` 11.4: a dependency is `{ path = "..." }` or `{ git = "...", tag | rev = "..." }`
  (checked out under `~/.vilan/git-deps/`); workspaces share with `{ project = true }` (`tour/projects.md`); "registry
  dependencies are future work". `docs/std/markdown.md` says std is versioned with the toolchain "until a package registry
  exists". Paper `proposal/library-packages.md` exists (not read in depth).

## 5. Other disagreements and gaps found

- `guide/native.md`'s Drop sentence is stale (sec. 1 item 5).
- `PLATFORM_MODULES` in `native_differential.rs` lists `std::canvas`, which no longer exists in std.
- The book's "refused natively: `std::web::ui`" is true for the browser layer only; the SSR twin builds natively.
- Core-labelled `std::fetch` and `std::random` are refused natively with no platform attribute to say so.
- The tracker's A185 INDEX row still reads "DRAFT, Q1-Q10 open"; the stamps in the item and the paper (R1-R17, four
  slices shipped in v0.55.0) say otherwise.
- Not determined: JS test status of any std module (nothing run); native status of `jwt`, `markdown`, `memo`,
  `web::style`, `web::document`, `web::remote`; Kolt's own lucide contents; which "other native gaps" still refuse the
  `lens::loaded` programs.
