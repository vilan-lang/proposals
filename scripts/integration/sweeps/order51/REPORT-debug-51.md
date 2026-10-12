debug-51 hand-back (Order 51, Opus 5.5). E257 S5 is built: S5a (marks and the v3 map), S5b (`vilan run --inspect`), and the paper's S5/S6 rows are updated. E257 gets a stamp, not a close. Nothing was pushed, and no process of mine is still running.

**Tree:** branch `debug-51` in `/home/reed/code/vilan-lang/vilan/.claude/worktrees/debug-51`.
- Base: ca407da0. Tip: **8ae0afc2**.

**Commits**
1. **c8866c46** — E257 S5a, family `feature`. Source maps for the JS backend.
   - **Marks.** The transformer leaves marks in the JS tree, but only on the new entry `transform_with_source_map`:
     - `js::Node::Mark(id)` sits before each statement or body tail.
     - `js::Node::At(id, call)` wraps each lowered `Expr::Call`.
     - Function and closure heads are marked through `origin` (a new `js::Function.origin` sits beside `Closure`'s; it is packed as `Option<NonZeroU32>` so `js::Node` stays 80 bytes).
     - The printer writes U+FDD0 at each mark and records it in textual order. `source_map.rs` strips the characters and computes the VLQ `mappings`.
   - **Where marks point.** A call points at its callee's name and a derive at its attribute. `sourcesContent` carries user files only; std is named by its cache path and listed in `ignoreList`. Function heads carry their source names in `names`.
   - **CLI.**
     - The debug preset writes `<script>.map` plus a `//# sourceMappingURL` line.
     - Elsewhere, `[build] source-maps` (new key, plus LSP completion and schema) or `vilan build --source-maps` turns it on.
     - A build without a map removes a stale one, and `--explain` names the map.
     - `vilan run` passes `--enable-source-maps`, and an HMR watch round now writes the server leg's map.
   - **Goldens.** All 145 corpus goldens moved by exactly one line (the comment), as did infer_preset's debug golden. I added gitignore entries for maps and regenerated the markdown anchor golden.
2. **8ae0afc2** — E257 S5b, family `feature`. `vilan run --inspect[-brk][=[host:]port]`, refused under `--watch` and `--backend rust`.

**Pins**
- `vilan-core` `tests/source_maps.rs`:
  - Each corpus program is built with and without a map, and the JS must be byte-identical.
  - Map validity: the test's own decoder, every segment inside its source's text, and a decode/encode round trip.
  - Per-construct pins: function head and name, statement and tail, call, closure, both instances of a generic, derive, std frame, release off, relative paths, and `js::Node` width = 80.
  - `source_map` unit tests.
- `vilan-cli` `tests/source_maps.rs`:
  - Files and comment, `--stdout` unchanged, release and stale-map removal, the manifest switch, and a panic's `.vl` stack.
  - The inspector smoke test: `--inspect-brk` on port 0, one breakpoint placed through the map, read back via node's `module.SourceMap`, then `Debugger.evaluateOnCallFrame` reads `product`. I used that rather than `Runtime.evaluate`, because a paused frame's local isn't global. It skips with an E257-led reason where node lacks the inspector.
- Shown non-vacuous by planting bugs: a lowering divergence went red on 3 corpus programs, and an off-by-one line went red on 154.

**Measured** (instructions:u, against the same `profiling` build of the base, median of 5)
- `vilan build` reactive-ui: **+0.27%** with the map (+4.9M of 1.80G); +0.03% with `source-maps = false`.
- `vilan check`: within ±0.06% on all perf subjects, both signs (reactive-ui +0.005%). `scripts/ci-local.sh perf` T2 is green, growth x1.929.
- kolt build: +0.36% with maps.
- My first cut was +0.60%. The cost came from building line tables over 600 KB of std text, plus the `Option<Id>` field widening every JS node from 80 to 88 bytes. I fixed both with a word-at-a-time newline count and a packed origin.

**Gates**
- Full suite `--cargo-profile ci-test -E 'not binary(deep_nesting)' -j 6`: 10439 passed, 0 failed, 31 skipped.
  - Within it: ci_ignored_pins 12/12, hygiene 3/3, corpus 13/13, check_scope_differential 15/15, native_differential 259/259, source_maps 162/162.
- `VILAN_NATIVE_DIFFERENTIAL=1`: 259/259.
- clippy, `cargo fmt --check` and `vilan fmt --check`: clean.
- kolt cold check RSS: 263,980 KB against the base's 266,916 KB (−1.1%), exit 0.
- **Canary: 17/18.** `a_thirty_level_chain_still_fits_libtests_own_two_mib_thread` aborts with SIGABRT. It aborts identically on base ca407da0 (N169, incr-51a's item); the test runs analysis only, which I didn't touch.

**Functions changed**
- analyzer.rs and mono.rs: none. Late writes are untouched.
- `track_caller.rs`: `site_offset` made `pub(crate)`.
- `vilan-cli`: run and build writers, the HMR round, `explain` (a new "source map" role), and test fixes in corpus, split, print_chunks and infer_preset.
- Emitter, in transformer.rs (fix-51's file; listed arms):
  - Entry points: `transform`, `transform_with_source_map` (new), `Transformer::transform_entry`.
  - Mark placement: `emit_statement` and the new `mark_statement` / `drop_bare_mark` / `mark_tail` / `mark_call`, `walk_entity_seams`.
  - Tail sites: `walk_function_body_nodes`, the closure arm, `walk_loop_body_nodes`, `walk_branch_body`, `emit_scope_tail_node`. `function_with_name` sets the origin.
  - `Formatter`: `with_marks`, `take_marks`, `mark`, `marked_items`, `between`, `sequence`, `operand`, `postfix_subject`, `call`, `node`.
  - Walker arms: `rewrite_sibling_node`, `descend_for_preload`, `gate_source_name`, `collect_reference`, `node_is_expressible`, `collect_node`, `rename_node`.
  - `js::Node` and `js::Function`; `origin: None` added at the `chunk_forwarder`, drop-helper and test constructors.
  - `dbg.rs` (`push_printer`).

**Where the premises were wrong**
- "printer.rs's mark emission": `printer.rs` holds the dbg printer's shapes. The JS printer is `Formatter` inside transformer.rs, so the marks live there.
- debug-50's +0.2–0.3% estimate faked the original positions. Resolving real ones is most of the cost.
- Turning maps on for the debug preset changes every debug build's script by one comment line. Every corpus golden had to move, and five tests assumed the old file set: corpus leftovers, the split namespace, print_chunks' denominator, the HMR server-bundle equality, and the watch-session detector.
  - For the detector I put `--watch` in a constant, `WATCH_REFUSED`, because the refusal test never opens a session. That avoids editing `.config/nextest.toml`, which is tools-51's.

**Finds** — `sweeps/order51/newitems51-debug-51.json`, repros under `sweeps/order51/debug-51/finds/`:
- **N?1:** `[build] dbg` is missing from the editor schema (which has `additionalProperties: false`) and from LSP completion, so VS Code flags a valid key.
- **N?2:** a failing `vilan test` prints the temp script's lines because it writes no map.

The paper (`debugging.md`) has an "As built" note under §5.1, the S5 row marked BUILT, and the S6 row listing what's next: the extension's debug type and code lens, maps for HMR browser bundles, split chunks and the lone-package watch script, `--inspect` under `--watch`, and an ignore-listed source for runtime helpers. The integrator commits it.

**Questions for the owner**
1. kolt's `client.js.map` is 978 KB against a 590 KB script, because `sourcesContent` embeds the generated `src/lucide/lib.vl` (636 KB). Should large or generated user files be named by path instead of embedded? I recommend a size cap of about 256 KB: past it the file goes by its relative path, which a local debugger reads from disk.
2. Every debug-build script, the corpus goldens included, now ends with the `sourceMappingURL` line. Do you accept that? I recommend yes; it is the standard spelling and node and debuggers need it.
3. Should `vilan test` get maps (N?2)? I recommend yes; it's small.
4. Should the HMR browser bundle get its map in S6, by shifting the mappings by the shim's line count? I recommend yes, in S6 with the extension's debug type.
