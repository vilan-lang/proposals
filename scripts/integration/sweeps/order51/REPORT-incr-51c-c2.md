## incr-51c: hand-back at C2 (P0 / B603 done)

**Branch `incr-51c`.** Worktree `/home/reed/code/vilan-lang/vilan/.claude/worktrees/incr-51c`. Base `5e17cb59` (C1), tip **`56b36ee8`**. Nothing pushed, and none of my processes are still running. P1 is not started; it is ready to begin if you resume me.

### The commit
- `56b36ee8` **B603 (std-prefix P0): std-first canonical load order**. Family `fix`, with its `## Unreleased` CHANGELOG entry.
  - **What it does:** the drain in `analyze_inner` now runs two phases per round.
    - Discovery resolves each request, parses the module (parsing mints nothing) and follows the requests that module writes. It also requests the module's ancestor modules, so a parent mints before its children.
    - Minting then registers the discovered set in `load_order_key` order: std, then dependencies, then the package.
  - **Code changes:**
    - M107's heap is now one sort per round.
    - The new enum `DiscoveredModule` (Namespace / EntryAlias / Body) replaces `load_order_entry`, which became dead and was removed.
    - `load_order_key`'s doc comment is updated.
    - There are no other functions changed in analyzer.rs, and nothing changed in mono.rs or any emitter.
  - **Goldens:** four moved, all reorder-only (sorted lines identical, and regen_goldens judged the runtime output identical):
    - `vilan/test/adapt.mjs`, `await-postfix.mjs`, `time.mjs`: 11/11 lines each
    - the split fixture's `app.js`: 5/5 lines
    - Neither native census moved.
  - **New pin:** `corpus::emitted_js_is_independent_of_which_module_asks_first` covers two shapes, and I checked both red with the base binary by hand:
    - the papers-50 package repro;
    - a single-file twin where `std::time` reaches `std::task`.

### Where the premises were wrong
1. **Single-file programs do move.** The paper says they are unmoved, but std's own `pkg::` imports were discovered in ask order too (`time` → `task`). That is why three corpus goldens moved.
2. **std's ids are not yet "a function of the std module set alone"** (§3 of the paper). After P0, std's module nodes and walk order come first. But std's walk ids still come after every module node of the program, because all modules register before any walk. Measured: `basename` is Id(7994) in a single-file program and Id(7996) beside two sibling modules, with the same std set. This does not affect P1; P3 needs it fixed.
3. **The kolt server output is not strictly reorder-only.** The 18-line diff from a redundant `import std::db;` is now 0 (base: 18). But base vs tip on the plain server build differs in 16 line pairs: collision suffixes are renumbered by mint order (`composed` and `composed2` swap). With suffixes and `$` temporaries normalised, the two outputs are equal.

### Gates (tip `56b36ee8`)
- **Full suite** (`--cargo-profile ci-test -E 'not binary(deep_nesting)' -j 6`): 10,491/10,491 passed, 32 skipped. Within it:
  - ci_ignored_pins 12
  - hygiene 3
  - corpus 14
  - check_scope_differential 15
  - native_differential (default mode) 270
  - permutation_differential 6
  - edit_replay_differential 20
  - id_windows 10
  - vilan-lsp 1,103
- **Native differential, sweep mode** (`VILAN_NATIVE_DIFFERENTIAL=1`): 270/270.
- **Deep-nesting canary at 1536 KiB:** 18/18.
- **Lint and format:** `cargo clippy --workspace --all-targets -D warnings`, `cargo fmt --check` and `vilan fmt --check .` are all clean.
- **`ci-local.sh perf`:** T2 green on both release binaries, run in the same session. Cold rows tip vs base range from −0.085% to +0.061% (mixed signs; worst `example:walkthrough` −0.085%, `example:reactive-ui` +0.061%). No bump row. Late writes 0 on kolt.
- **RSS** (`rss-probe.py`, kolt cold check): 15-run medians base 278,740 KB, tip 281,428 KB (+1.0%). The tip shows a second mode around 295 MB in 5 of 15 runs; the counted heap peak is 291.3 → 291.6 MB (+0.1%), so I read this as allocator placement (all parses now happen before any minting).
- **E292's six rows** on today's kolt (`--source` copy, release, `--runs 5`, load about 1–2.4, errors 0). The harness refuses "model.vl keystroke" and "parse break" because their anchors are gone. Base → tip, CPU ms / instructions G:

| row | base | tip |
|---|---|---|
| leaf | 640 / 4.30 | 650 / 4.30 |
| leaf + pause | 2200 / 10.49 | 1600 / 10.47 |
| world | 850 / 4.65 | 670 / 4.64 |
| shared | 260 / 1.66 | 240 / 1.66 |
| model importers open | 770 / 5.47 | 750 / 5.45 |
| css | 850 / 6.53 | 840 / 6.53 |

  - Instructions agree within 0.4%; the CPU differences are noise.
  - VmHWM is about 1029 → 1034 MB.
  - E292 stays open.
- **Late-round probe:** a temporary counter, since removed, found zero modules minted in a later expansion round across kolt, the 11 examples and all 298 corpus files.

### Finds
Filed in `sweeps/order51/newitems51-incr-51c.json`:
- **M?1:** std's walk ids are offset by the package's module count (premise 2 above). Repro: `sweeps/order51/incr-51c/finds/std_ids_offset_by_package_modules/run.sh`.
- **B?1:** B603's leftover case. A module that only macro-generated code reaches mints in the next round, after everything in the first. There is no instance anywhere in the estate.

I also added an "As built (P0)" note to `std-prefix.md` §4.1 in the proposals checkout. It is uncommitted, for you to commit.

### Questions for the owner
1. **M?1:** should P3 mint the non-std module nodes after std's walk, rather than relocating std's ids when the prefix loads? My recommendation is to mint them after std's walk, as P3's first step: std never names a package module, and macro expansion has already run by then.
2. **B?1:** should the generated-only-module case be accepted as a known leftover for now? My recommendation is yes, with P3's key check (the closure computed from written imports) refusing a world that grew in a later round.
3. **Kolt's naming churn:** collision suffixes such as `composed` and `composed2` are numbered by mint order, so any ordering change renames them in output. My recommendation is to accept it, since it changes no behaviour.
