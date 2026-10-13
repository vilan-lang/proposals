debug-52 rebase hand-back (Order 52, Opus 5.5). The branch is rebased onto `origin/next` at 96487112 and every gate you listed passes. Nothing pushed, and none of my processes are still running.

**Tree:** branch `debug-52` in `/home/reed/code/vilan-lang/vilan/.claude/worktrees/debug-52`.
- Base: **96487112**. New tip: **c6c19da7**. The pre-rebase tip was a7adb25b.

**Commits** (same content and families as the first hand-back)
1. **bf5fa525 — E257 S6a, `tooling`.** The runtime helpers map into an ignore-listed source, `vilan:///runtime.js`, and a user file over 256 KB goes by its path instead of being carried in `sourcesContent`.
2. **3e53cd2f — E257 S6b, `feature`.** A split leg's eager bundle and each route chunk get their own map; the four split goldens moved by one comment line each.
3. **52717f4c — E257 S6c, `feature`.** Watch rounds map their scripts and take `--inspect[-brk]`, and the HMR browser bundle's map is shifted past the shim and served by the dev channel.
4. **c6c19da7 — E257 S6d, `feature`.** The extension's `vilan` debug type and the "Debug" code lens on `fun main`.

**Rebase**
- The only conflict was CHANGELOG ordering. My four entries now sit after upstream's B617, E309, B620 and E314, and every entry is kept.
- Parity check: `origin/next` has 1556 family markers and the tip has 1560, my four entries; nothing upstream was removed or changed.
- The extension's `package.json` merged cleanly; my hunks stay between `languages` and `grammars`.
- `transformer.rs` merged with no conflict. My changes there are only the entry points (`Printed`, `with_prelude`) and the split mapping; native-52's argument-copy change is untouched. The suite, the corpus and both native differential modes are green over the merged result.

**Gates on c6c19da7**
- Full suite (`--cargo-profile ci-test -E 'not binary(deep_nesting)' -j 6`): **10609 passed, 0 failed, 38 skipped.** Within it:
  - ci_ignored_pins 12/12
  - hygiene 3/3
  - corpus 14/14
  - check_scope_differential 16/16
  - native_differential 279/279
  - source_maps: vilan-core 158/158, vilan-cli 8/8
  - split 13/13
  - hmr 15/15
  - watch_lifecycle 3/3
  - vscode_extension 26/26
- `VILAN_NATIVE_DIFFERENTIAL=1` (sweep mode): 279 passed, 1 skipped.
- `scripts/ci-local.sh perf`: T2 green, growth x1.929.
- kolt cold check RSS, 5 runs each against a release build of 96487112: base 276,400 KB, tip 276,488 KB (+0.03%).
- kolt `client.js.map` is still 291,166 bytes (978 KB before S6a).
- `cargo fmt --check`, `cargo clippy --workspace --all-targets -- -D warnings`, and `vilan fmt --check .`: clean.
- Extension: `tsc` clean, `npm test` 40/40.
- The deep-nesting canary and the vilan-lsp binary were not run; I touched no walk, checks, records or tables.
- The build/check cost was measured before the rebase, not re-measured after it: `vilan build` of reactive-ui +0.015%, `vilan check` −0.003%.

Nothing else changed since the first hand-back:
- Functions changed: none in analyzer.rs or mono.rs; in the emitter, only the transformer's entry and split functions.
- Finds: B?1, `serve_build` serves no source map (in `newitems52-debug-52.json`).
- Paper: the `debugging.md` S6 row and the §5.2 "As built" note are still uncommitted in the proposals checkout, for you to commit.
- The four owner questions stand as filed.

The temporary base worktree I built for the RSS comparison is removed.
