debug-52 hand-back (Order 52, Opus 5.5). E257 S6 is built: all five parts of the brief, plus the extension test the paper still owed. Nothing pushed, and none of my processes are still running.

After your restart, two stale `vilan run --watch --inspect` processes were still alive. They came from the old refusal test, which hangs once the watch refusal is gone. I killed them by PID and resumed from the uncommitted tree.

**Tree:** branch `debug-52` in `/home/reed/code/vilan-lang/vilan/.claude/worktrees/debug-52`.
- Base: e4255f60. Tip: **a7adb25b**.
- Untracked: `debug-52-STATUS.md`.
- The temporary base worktree (`debug-52-base`) I made for measuring is removed.

**Commits** (each with its `## Unreleased` CHANGELOG entry and family marker)
1. **b800def3 — E257 S6a, `tooling`.** The runtime helpers' ignore-listed source, and the `sourcesContent` cap.
   - **Runtime source.** The helpers at the top of every script (`__at`, `__panic`, …) now map line for line into a made-up source, `vilan:///runtime.js`. Its text is carried in the map and it is in `ignoreList`. A helper's stack frame now reads `at __at (vilan:///runtime.js:3:1)` where it used to name the temp script.
   - **Cap.** A user file over 256 KB (`SOURCES_CONTENT_CAP`) is named by its relative path, with null content, and the debugger reads it from disk.
   - **kolt acceptance met:** `client.js.map` went from 978 KB to **291 KB**; `src/lucide/lib.vl` is now named by path.
2. **76112b74 — E257 S6b, `feature`.** A `split = true` leg's eager bundle and each route chunk get their own map. Before this, a split leg had no map at all.
   - Each chunk's map sits beside it and is swept with it when a build stops splitting.
   - The four split goldens (`tests/split/golden/app*.js`) each moved by exactly the one comment line.
3. **923c1c0e — E257 S6c, `feature`.** Watch rounds.
   - `--inspect[-brk]` is now accepted with `--watch`: every round's node child starts under the inspector again.
   - Every watched node child also gets `--enable-source-maps` when its map exists. It didn't before, so a watch-round panic printed script lines.
   - The lone package's watch script gets a map, removed with the script on each round and on Ctrl-C.
   - The HMR browser bundle gets a map again:
     - It is shifted down by the shim's line count (`hmr::shim_lines`).
     - The bundle names the map by an absolute URL at the dev channel, `/bundle/<leg>.js.map?token=…`, and the channel serves it there behind the token.
4. **a7adb25b — E257 S6d, `feature`.** The extension's `vilan` debug type and the "Debug" code lens.
   - A plain run resolves to VS Code's JavaScript debugger running `vilan run --inspect-brk=127.0.0.1:<free port>`, attached at that port before the first line runs.
   - `watch: true` runs `vilan run --watch` under the JS debugger's child-process attach, so each restarted server is attached again.
   - The lens sits on every top-level `fun main`.
   - New files: `src/debug.ts` (the resolution logic, no vscode import, tested by `src/test/debug.test.ts`, 12 tests) and `src/debugging.ts` (registration).
   - `extension.ts` changes by 4 lines.
   - `package.json` hunks are limited to the debug contributions: `onDebugResolve:vilan`, `breakpoints`, and `debuggers`. I placed them between `languages` and `grammars`, away from editor-52's settings, so the rebase onto its merge should be clean.

**Where the premises were wrong**
- The paper planned a pre-launch `vilan build` with `outFiles` set to the dist directory. Instead the debug type runs `vilan` itself as the runtime, so the map `vilan run` writes beside its temp script is the one read. That needs `resolveSourceMapLocations: null`, because the temp script is outside the workspace.
- The brief said "`--inspect-brk` under the hood". That holds for a plain run. A watch run can't use it: attaching once at a fixed port ends when the round restarts the process, so watch uses child-process attach instead.
- The brief said the HMR fix was only shifting the mappings by the shim's lines. Shifting alone isn't enough: a relative map URL can't be reached. The page's server (`serve_build`) doesn't route maps, and the swap re-evaluates the bundle text, where a relative URL has nothing to resolve against.
- Watched node children never got `--enable-source-maps` in S5, even when the server leg's map existed.

**Measured** (instructions under callgrind, against the same `profiling` build of the base, 3 runs each)
- `vilan build` of examples/reactive-ui: **+0.015%** (+0.33M of 2.297G, map written). Within the +0.1% limit.
- `vilan check`: −0.003% (noise).
- kolt cold check RSS: tip 268,572 KB against base 278,996 KB.

**Gates**
- Full suite (`--cargo-profile ci-test -E 'not binary(deep_nesting)' -j 6`): 10563 run, 10561 passed, 32 skipped. The 2 red were both in my new extension test:
  - `hygiene::no_tracked_file_contains_an_absolute_home_path`: fake `/home/user` paths.
  - `vscode_extension::the_extensions_own_tests_pass`: a `__dirname` read of package.json that fails once the test is bundled elsewhere.
  - Both were fixed in the S6d amend and those two binaries re-run green (29/29). I did not re-run the whole suite after the amend; nothing outside the extension test file changed.
- Within the suite: ci_ignored_pins 12/12, hygiene 3/3 (after the fix), corpus 14/14, check_scope_differential 16/16, native_differential 278/278, source_maps 166/166, split 13/13, watch_lifecycle 3/3, hmr 15/15.
- `VILAN_NATIVE_DIFFERENTIAL=1` (sweep mode): 278 passed, 1 skipped.
- `scripts/ci-local.sh perf`: T2 green, growth x1.930.
- `cargo fmt --check`, `cargo clippy --workspace --all-targets -- -D warnings`, `vilan fmt --check .`: clean.
- Extension: `tsc` clean, `npm test` 40/40.
- Not run, because I didn't touch the walk, checks, records or tables: the deep-nesting canary and the vilan-lsp binary.

**Planted-bug checks**
- Removing the runtime range or the cap turned both core pins red.
- Removing the HMR shift turned the HMR map pin red. My first version of that pin passed by coincidence, because the marked call was the last statement, so I hardened it.
- The `--inspect`-under-watch pin is red on the base by construction, since the base refused that combination.

**Functions changed**
- analyzer.rs, mono.rs: none.
- Emitter (`transformer.rs`):
  - `transform` and `transform_with_source_map`.
  - `Transformer::transform_entry`, which now returns a new `Printed` struct.
  - New `with_prelude`, which assembles the imports and helpers at the top of the script.
  - `transform_split_with_plan`, plus new `map` fields on `SplitProgram` and `EmittedChunk`.
  - No lowering touched.
- `source_map.rs`: `strip_marks` takes a runtime range; new `MapWriter::runtime` and `MapWriter::write`; `MapSource.url`; `SourceMap::shift_lines`; `to_json`.
- vilan-cli: `run_watch`, `hmr_round`, `build_and_spawn_run`, `spawn_watched_node`, `compile_unit`, `remove_watch_script`, `install_watch_interrupt_hook`, `with_mapping_comment` (plus new `with_mapping_url` and `with_comment_line`), `write_chunks`, `sweep_stale_chunks`, `compile_to_js`.
- `hmr.rs`: new `shim_lines`, new `DevChannel::map_url`, the `/bundle/<leg>.js.map` route in `serve_asset`.
- Test support: `kill_watcher` now also removes the map.

**Paper:** `debugging.md` has an "As built (Order 52)" note under §5.2, and the S6 row is marked BUILT with what remains. It is uncommitted in the proposals checkout, for you to commit.

**E257 stamp:** S6 is complete against the paper's list. E257 stays open for S7–S9.

**Finds** — `sweeps/order52/newitems52-debug-52.json`, repro at `sweeps/order51/debug-52/finds/serve_build_serves_no_source_map.md` (the order51 path, as the brief literally says):
- **B?1:** `serve_build` serves no source map. `LegBuild::artifacts` in std's `build.vl` routes only the bundle, styles, chunks and assets. So a built or `--no-hmr` browser page can't load `client.js.map`, and a SPA catch-all answers with HTML instead.

**Questions for the owner**
1. Should B?1 be fixed by listing the maps in the build manifest so `serve_build` routes them, or by `serve_build` routing `<artifact>.map` whenever the file exists? I recommend the manifest: it stays the one description of what a build wrote. It's std's work, sized S.
2. Is an absolute dev-channel URL acceptable for the HMR browser map? It means the session token appears in the bundle's last line, though the shim in the same bundle already carries it. I recommend yes; a relative URL can't be reached either from the page's server or from a swap.
3. The debug type has only been tested at the resolved-configuration level; I couldn't run a live VS Code session in the lane. Should someone do a manual F5 check before v0.50.0, covering both the plain and the watch shapes? I recommend yes. The one assumption I couldn't verify is how `attachSimplePort` behaves with `vilan` as the runtime.
4. Is a line-level mapping enough for the runtime source? A helper frame shows `:line:1`, not the exact column. I recommend yes, since the helpers are ignore-listed and skipped when stepping.
