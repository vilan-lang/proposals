# Kolt under v0.53.0 - the owner's patch notes (Order 55)

The integrator never edits /home/reed/code/kolt; these are the edits the owner applies. Checked on a copy of the
owner's tree (main @3dbc73b) under the seal tip c50a0a58: with the two REQUIRED edits the copy checks with 0 errors
and the B677 warnings below.

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
