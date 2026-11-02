# Kolt under v0.53.0 - the owner's patch notes (Order 55)

The integrator never edits /home/reed/code/kolt; these are the edits the owner applies. Checked on a copy of the
owner's tree (main @3dbc73b) under the seal tip c50a0a58, and again on 2026-10-31 under the INSTALLED `vilan 0.53.0
(a08f8f73b)` after the fold: unpatched, 48 errors (the M171 collision, 24 files x 2 members); with the two REQUIRED
edits the copy checks with 0 errors and exactly the two B677 warnings below (panels.vl:1280 and :2555). `vilan fmt
--check` on the patched copy names four files: `src/task_table.vl` (E338's reflow, fmt-55 - the one line at :429) and
`src/lib/rich_text/clipboard.vl`, `src/lib/rich_text/controller.vl`, `src/store.vl`, which 0.52.0 also wants
reformatted (the owner's pending edits, not this order's). The owner's uncommitted `src/panels.vl` change was not in
the copy (HEAD only).

## REQUIRED (the tip refuses kolt without them)

1. **M171 - std now carries `Event::default_prevented` and `Event::stop_propagation`** (also `stop_immediate_propagation`,
   `propagation_stopped`). kolt's own `impl Event` in `src/lib/std_ext.vl` declares the same two members and the tip
   reports 46 errors over 23 files for the collision. Delete both members (the doc line, the `[extern(..)]` attribute
   and the `external fun`) - the patch is `std-55/kolt-m171-std_ext.patch` (against 3dbc73b; `patch -p1`). Every call
   site keeps working unchanged against std's members.
2. **M164 - std::http caps a request body at 1 MiB by default** (`ServerBuilder::max_body_bytes(n)`,
   `max_body_bytes_under(mount, n)`, `Request::max_body_bytes(n)`; the body is read lazily). kolt's `/api/upload`
   accepts 25 MB legitimately, so without a cap edit uploads over 1 MiB are refused with 413. The one-line edit at
   `src/files.vl:235`: `request.max_body_bytes(max_upload_bytes.as_usize()).bytes()` (the request-level cap wins over
   the mount's and the server's).

## Warnings the tip prints (B677 door 1; door 2 is the closure-owner paper, ruled at the Order 56 draft)

- `src/panels.vl` at the page wrapper closures (two sites, :1280 and :2555 on 3dbc73b; :922 / :2068 on the tree rpc-55
  measured): a closure that answers a `View` through a parameter is created under the CALLER's owner, not the page's.
  The warning names the clause; the spelling that silences it today is an explicit owner on the parameter:
  `sync |str| View context (owner_scope, page_focus)`. Door 2 would make that the default.

## Optional (the tip accepts kolt as it is; these retire workarounds or use the new surface)

- **B652** - the lexer decodes `\{` and `\}` in every string form: the workaround comment in `document_test.vl` can go.
  One-line externs carrying such escapes are refused now (estate 0 in kolt).
- **B654** - triple-quoted externs for the dictionary strings (search-dict) are accepted as written; nothing to change.
- **M170** - `ui::nothing()` and `ui::each_owned(..)` exist on both twins; kolt's `view("")` placeholders can become
  `ui::nothing()`.
- **M166** - `[derive(Json)]` emits `has_field -> None` for `Option<T>` fields: a hand-written absent-field rule can go.
- **M167** - the router's `HistoryEntry` + `set_history_state(..)`: kolt's own history bookkeeping can read std's.
- **M169** - `Iterator::position` / `List::position` in std: kolt's hand loops over `enumerate()` can use them.
- **M165** - an `Option<T>` landing on an `any` parameter is unwrapped on JS as it already was natively (a JS-only bug
  fixed; nothing to edit unless kolt worked around it).
- **M168** - `ServerBuilder::host(addr)` binds one address; `require_build` / `build_of` look beside the running module
  first: a `cd` before `node dist/server.mjs` is no longer needed for the manifest lookup.
- **fmt-55 (E338)** - `vilan fmt` under the tip reflows one line, `src/task_table.vl:429` (a 101-column hole becomes a
  5-line call); run `vilan fmt .` once under 0.53.0 and commit the result.

## Also for the owner

- The LSP latency harness's anchors (`model.vl` `create_channel(name)`, `channel.vl` `channel_name.adopt(..)`) left
  the tree with 38a7ac9; the Order 55 seal measured kolt@46c5b59. N186 (Order 56) re-anchors on the current tree.
- owner-questions55.md holds the lanes' open questions (closure-owner.md held for the Order 56 draft).

## Under v0.53.1 (E352 + E353, 2026-10-31)

- **E352** fixes the `then … else` arm reflow: `store.vl`'s `mark_unseen` stays as written. The evened-out rule
  also breaks every other then/else arm over 100 columns the way its statement form breaks: 18 kolt files move
  once (251 lines; channel, coedit_test, file_page, rich_text/controller, markdown, mcp, mcp_write,
  message_editor, message_view, org_pages, panels, settings, shared, sidebar_sections, spelling, store,
  tracker_import, plus clipboard and task_table which 0.53.0 already moved identically). The whole reflow as one
  patch against the written tree: `fmt-e352/kolt-e352-vs-written.diff` (or just run `vilan fmt .` under 0.53.1 -
  it is the same result). After it, `vilan check` exits 0 (the two B677 warnings) and `fmt --check` is clean.
- **E353**: `// vilan-fmt: skip` alone on the line immediately above a statement or an item keeps that node as
  written; `vilan fmt --check` lists each skip as `path:line: vilan-fmt: skip` without failing. A reason may
  follow after a space (`// vilan-fmt: skip - E352`). Nothing in kolt needs it now that E352 is fixed.

## Under v0.54.0 (A178 - lengths as data; lands at Order 56's cut)

- The codemod: `a178/dp_codemod.py` (`--check` prints the diff, `--apply` rewrites): 599 `rem(n / 16)` -> `dp(n)`, 5 `rem(0)` -> `dp(0)`,
  59 `size(n)` -> `dp(4n)`, 22 constant uses -> the constant; nine constants become `const let .. = dp(..)` (styles.vl's eight +
  channel.vl's content_width); `const let size = Scale::new(0.25)` and its import go, `src/lib/scale_step.vl` is deleted. Proven on a copy of
  3dbc73b: `vilan check` clean (the same two warnings), the built client.css BYTE-IDENTICAL, 38 files -605/+601 lines; `vilan fmt .` then
  rejoins 3 shorter lines (message_actions, settings, views). Left for you (printed by the tool): `avatar_gap` (inside a sum), `views.vl:323`,
  and `sidebar.vl:127-128` (`.border_left/right(rem(2 / 16))` - `dp(2)` renders `2px` there, a px-role hairline; the rec is to take it).

## Under v0.54.0 (B689 + M182 - the map lends; lands at Order 56's cut)

- **B689** needs nothing from you: `g.tasks().at(id).some()` and every keyed read now lends the slot in place and copies only the
  leaf a `get()` returns. The item's repro went 10.7 / 30 / 240 ms -> 7 / 3 / 3 ms on node; the Board's 4.5 s of `__clone` should go
  with it - measure the 2,072-task organization again under 0.54.0 and say what it reads. A copy of your tree (3dbc73b + M171 +
  M164 + the E352 reflow) checks clean under the lane's binary: exit 0, the same two B677 warnings.
- **M182**: `HashMap::update(key, lazy missing: V, change: |&mut V| void)` is the grouping idiom - `groups.update(key, [], |list|
  list.push(row))`, O(1) per push (the repro's 16k pushes: 2,274 ms -> 5 ms). `peek(key, |&Option<V>| U)` reads a slot in place,
  `modify(key, |&mut Option<V>| U)` writes it (leave `None` = removed; `Some` under a new key = inserted last). The take-copy /
  push / put-back sites to rewrite when you like: `sidebar_rows.vl` (2), `task_sections.vl` (2), `command_palette.vl`, `live_edit.vl`,
  `panels.vl` (the `get(..).unwrap_or([])` + `get_or_insert` shapes). `missing` is `lazy`, not `|| V` (hash-map-lend.md Q2).
- A `HashMap`'s debug/DAP layout is now `keys`/`values`; the vscode extension's printer moved with it and the vsix is refreshed at
  the fold - debug a 0.54.0 build with the 0.54.0 extension.

## Under v0.54.0 (B693 - the assumed handle's keeper; lands at Order 56's cut)

Nothing to change: kolt's 28 `when_live` / `when_remote_live` sites get the fix as they are. What to expect: a field read below a body handle costs the field (the item's repro 4,264 ms -> 4.5 ms at 10,000 records on node); the organization is copied ONCE per page leave (the write that ends the variant), not per read. Re-measure Tasks / Board / Table of the 2,089-task organization under the 0.54.0 toolchain; the remaining per-read constant is the path-list copies (M186, ~74 `__clone` per read, size-independent).

## Under v0.54.0 (M185 - std::image; lands at Order 56's cut)

Custom avatars (kolt task #9): `import std::image::{ Image, Fit, Format };` on a server (`@process`) module, then per size

    let picture = Image::decode(upload)!;                      // Result<Image, str>: "not a PNG, JPEG, WebP or GIF" / the 50 MP limit
    let avatar = picture.resized(size, size, Fit::Cover)       // the centre square, scaled; sizes 32 / 64 / 256
        .encode(Format::Webp, 80)!;                            // Bytes; WebP is lossless (quality ignored) - use Format::Jpeg for photos

`Image::sniff(upload)` answers the format without decoding (refuse anything but `Some(..)` at the upload). Thumbnails of pictures in
messages: `picture.resized(300, 300, Fit::Contain)` keeps the aspect inside the box. Costs on node: ~1.4 s for the FIRST call in a
process (the codec module compiles), then ~350 ms for a 12 MP JPEG decode + Cover 256 + WebP encode; the call is synchronous, so put it
on the upload handler, not a page render. The bundle of a server that reaches the codec grows ~783 KB (nothing in the client bundle:
the module is `@process` and refused on a browser leg). A `resized` whose result would exceed 50,000,000 pixels panics at your call -
sizes are yours to pick, so keep them small. Nothing in kolt changes until you write the feature.

## Under v0.54.0 (parser-56: E355, B657 part 1, E354; lands at Order 56's cut)

- **E354** (fmt): `vilan fmt .` reflows SIX sites in four files - `src/accounts.vl:177`, `src/lib/search.vl:144/176/188`, `src/login_page.vl:212`, `src/mcp.vl:665` - a struct or list literal receiver of a call now breaks one element per line with `].to_json()` after the bracket. Idempotent; nothing else in kolt moves. (The item's own `file_page.vl` line no longer moves in the lane's copy of your tree.)
- **E355**: a repeated `[derive]` over one item is one error at the second copy ("merge them, `[derive(PartialEq, Json)]`" when the lists differ; "keep one" when they match) and the item still reads - no more "cannot find 'derive'" steers.
- **B657**: `..base` in a struct literal is one error at the `..` naming the `mut p = base; p.x = ..` form; the `..base` feature itself is not built (your 2026-10-19 note stands).

## Under v0.54.0 (std-56: M181 std::url + A179 the cancellable dial; lands at Order 56's cut)

- **M181**: `import std::url::{ percent_encode, percent_decode };` on both backends. `src/lib/std_ext.vl`'s `decode_uri_component` / `encode_uri_component` externs and their imports (code_links.vl, files.vl's `X-Kolt-Filename`, the `Content-Disposition` writer) can go. One visible difference from your extern: a text mixing a malformed escape with a good one (`%zz%20`) now decodes the good one (`%zz `); a lone `%zz` still reads as written.
- **A179**: in `src/client.vl`'s connect loop, wrap the dial - `dial_within(4000, || KoltClient::connect_with(url, codec, protocols))` - and match `Err(RpcError::Timeout)` as the "Can't reach Kolt" case; a hung first attempt no longer holds the retries back, and the abandoned socket is closed (nothing it opens later is left running). Inside a nursery you cancel, the dial now answers `Err(RpcError::Cancelled)`. Your `client.vl:151` match has a fallthrough, so nothing breaks before you add the arm.

## Under v0.54.0 (M186 - the shared store path; lands at Order 56's cut)

Nothing to change. A read below any handle (`g.tasks().at(id).some().title().get()`, every `when_live` body's reads) now copies only the value it returns - the per-read path copies (74 `__clone` calls a five-step read, size-independent) are gone; a projection allocates one small step node. Measured 200k reads at 1,000 records on node: 279 -> 102 ms. With B689 + B693 + M186 together, re-measure Tasks / Board / Table of the 2,089-task organization under 0.54.0; what is left per read is the handle's closures.

## Under v0.54.0 (solver-56: B688 BREAKING, E356, B677 door 2 BREAKING; lands at Order 56's cut)

- **B688** (86 sites in 34 files - the one patch 0.54.0 asks of kolt): a method an `impl` block adds to a type declared in ANOTHER module (std's `impl List<T: Display> { fun join }`, your `app_overlay`'s `menu`/`modal` on `Overlay`, `styles.vl`'s `ghost`/`select_off`/`flex_col` on `Style`, `to_set`) now resolves only in a file that imports from the block's module - the rule the "import std::display::Display to use it" message always claimed; a build no longer hides what `vilan test` of one file refuses. Each site's error names the import; add it per file. By kind: app_overlay menu/modal 64, join 11 (`import std::display::Display;`), styles 10, to_set 1. Sites (src/ file:line): accounts 109, 162; backlinks 172; board 425, 535, 688; channel_ui 358, 540, 575, 682, 775, 864; channel 376, 1520; command_palette 122, 250, 253; desktop 106, 117, 119; documents 193, 233, 273, 383, 725; hover_card 50; lib/keymap 133; lib/rich_text/controller 1429, 1430, 1778, 1799, 1830, 1865, 1951, 1966, 1990, 2002, 2045; line_editor 96; link_menu 59; live_edit 743, 874, 876, 878; message_actions 193, 321; message_editor 1074, 1172, 1358, 1497, 1628, 2031; notification_center 40; org_pages 333; panels 271, 1170, 1452, 1915, 2036, 2406; reactions 129; settings 136; sidebar_rows 120; sidebar_sections 411; sidebar 216, 249, 273; spelling 536, 543; store 1764; styles 57; task_assignees 166; task_fields 76, 355, 613; task_filter 62, 162, 223; task_menu 78, 182, 233; task_sections 107, 221, 1017; tasks 186; task_table 508. With the imports added, a copy of your tree checks clean. (The quick-fix names the module's FIRST export - `import pkg::styles::search_mark_style;` - which reads oddly; any name from the module serves; E359 improves the steer.)
- **E356**: an `own self` builder called as a statement (`modal.on_close(|| ..);`) now warns at the call; your three sites are already fixed by hand.
- **B677 door 2**: a closure parameter answering `View` takes the owner AT THE CALL by default - your seven written `context owner_scope` clauses stay accepted (now redundant), the two door-1 warnings on `panels.vl`'s `page` are gone, and every page kolt navigates to builds under the owner at the call without a clause. Your copy checks clean with 0 warnings.

