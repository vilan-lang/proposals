After B586, `vilan check <file>` on std's own files (the ones the item named) no longer
fails on `pkg::` paths, but 11 of std's 70 `.vl` files still report errors in file mode,
in three shapes (each a std-AS-ENTRY artifact; `vilan check` of a program that imports
std is clean):

- `external fun` with no `[extern(..)]` that the transformer lowers itself (an intrinsic):
  `vilan check vilan/std/src/web/dom.vl` -> "`external fun query_selector_all` names no
  body"; likewise context.vl (`Context::new`), process.vl (`scan`), random.vl, shared.vl
  (`Shared::new`). The rule that wants a binding does not know std's intrinsics when std
  is the entry.
- a file in a platform LAYER importing a BASE-layer module by `pkg::`
  (`vilan/std/src/browser/web/ui.vl:63` `pkg::web::dev`; `process/web/ui.vl`;
  web/document.vl, web/prelude.vl, web/router.vl `pkg::ui`): `pkg::` has one root in file
  mode (the layer's), the deferral the editor records
  (`a_layered_library_module_is_rooted_at_its_own_layer`). Not new, and now visible.
- `vilan/std/src/reactive/store.vl:726`: "`lend` is an `[internal]` field of std's `Store`"
  - the B568 rule treats the entry file as outside std.

Rec: `vilan check` of a file under a `[library]` that IS std (the toolchain's own std
directory) analyzes it as std (`analyze` already recognizes std's layer roots as "compiling
std" once reached through an import), or the item closes as "std is not checked as an entry"
and its doc says so. Owner's call; sizing S-M. Repro: loop `vilan check` over
`vilan/std/src/**/*.vl`.
