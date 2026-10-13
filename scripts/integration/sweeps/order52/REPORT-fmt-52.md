fmt-52 / E314 is committed as one commit on branch fmt-52, and every gate is green except `scripts/ci-local.sh perf`, which was not run. Nothing is pushed, and none of my processes are still running.

Commit
- Tip: cbab680d, on base e4255f60.
- Subject: "E314: a long call inside an element-body hole breaks its arguments, its list's tuples siblings alike, an element literal whole, and the chain link on its own line". It carries the Sonnet 5.5 trailer.
- Family marker: `tooling`.
- Files: crates/vilan-core/src/formatter.rs and CHANGELOG.md. `fmt-52-STATUS.md` stays untracked.
- No other lane's file is touched.
- analyzer.rs, mono.rs and the emitters are untouched, so the perf gate is not needed.

Gate counts (on cbab680d)
- Full suite, `cargo nextest run --workspace --cargo-profile ci-test -E 'not binary(deep_nesting)' -j 6 --no-fail-fast`: 10564 run, 10564 passed, 32 skipped. This includes `ci_ignored_pins`, `hygiene`, `corpus`, `check_scope_differential` and the native differential in default mode.
- Native differential in sweep mode (`VILAN_NATIVE_DIFFERENTIAL=1`, `--test native_differential`): 278 run, 278 passed, 1 skipped.
- Formatter unit tests: 498/498 (489 existing, including the fixed-point tests over std files, plus the 9 new `hole_call_layout` pins).
- `cargo clippy --workspace --all-targets -- -D warnings`: clean.
- `cargo fmt --check`: clean.
- `vilan fmt --check .` over the repo: rc=0.
- RSS probe (`scripts/rss-probe.py`, 5 runs, kolt copy with lucide and search-dict, debug build of the base formatter vs. the tip):
  - Median peak RSS 279240 KB (base) against 286008 KB (tip), which is +2.4%, inside the 3% bound.
  - The formatter is not on the `check` path; the difference is probe noise (individual runs overlap) between two separately built binaries.
- Canary, vilan-lsp and `scripts/ci-local.sh perf` were not run, as agreed: no walk, record, table, analyzer, mono or emitter is touched.

Pins
- New module `hole_call_layout` in formatter.rs (idempotence and the token round trip run through `assert_construct`):
  - The kolt shape: arguments one per line, the list one tuple per line, `)` at the hole's indent, `.styled(..)` on its own line one level under the hole's indent, and the `css { }` block kept.
  - A hole call that fits stays inline; a link that only just overflows takes its own line and no argument breaks.
  - A plain long call in a hole; sibling tuples that come apart together; a comment between arguments; a lone wide argument left alone; the same call outside markup left alone; no element cut mid-literal, and the output is a fixed point.
- Red on the base binary: the repro, the link-overflow case, the plain call, the siblings case and the comment case. The other four are guards that pass on both.

Moved lines: exactly six holes
- This is from scratch copies of 468 .vl files, run with the base and the tip binaries and diffed. The copies cover kolt src (with lucide and search-dict), the website src, vilan/ (std, examples, test, benchmarks, macro_std), the CLI templates, the native tests and the bindgen fixtures. The tip's output is a fixed point and nothing was declined.
- kolt `src/prefs.vl`, three `select_component(...)` holes (the base's lines 229, 247 and 273, for text_selection_enabled, context_menu_enabled and sidebar_collapsed). Each now has its arguments one per line, the list one tuple per line, and `.styled(..)` on its own line.
- Website `src/page.vl`, three holes: `install_row("macOS / Linux", ...)` at about line 220, `install_row("Windows (PowerShell)", ...)` right below it, and `button_link("https://github.com/vilan-lang/vilan/tree/main/editors/vscode", ...)` at about line 535.
- std, the examples, the templates, the native tests, the benchmarks and test/: 0 lines moved.
- The saved diff is at /home/reed/code/vilan-lang/proposals/scripts/integration/sweeps/order51/fmt-52/finds/e314-estate-moves.diff.
- The repo's own `.vl` files do not move, so `vilan fmt --check .` stays green with no reformat of other lanes' files. The kolt and website moves are the owner's to apply.

Where the item's premise was wrong
- E314 says a call outside markup "already breaks" its arguments one per line. It does not: `print_call_arguments` documents R5 (last-argument layout only), and the existing pin `a_single_link_and_a_plain_long_call_stay_inline` says argument wrapping is out of scope. The argument-list layout is new code, gated to calls inside an element-body hole (`hole_depth > 0`).
- Ungated, the same code moves about 1,813 diff lines in 60 files (std 949, kolt 488, native tests 149, website 147, benchmarks 36, examples 23, test/ 21). The hole-only gate is as you ruled; the generalisation is the owner's call next order.

Finds
- `E?1` is filed in /home/reed/code/vilan-lang/proposals/scripts/integration/sweeps/order52/newitems52-fmt-52.json: the formatter never breaks a call's arguments outside a markup hole. The generalisation is a single slice: drop the three `hole_depth` gates (the Call arm, the call-subject chain door, the split-chain subject) and reformat the estate in the same commit.
- Its repro is at sweeps/order51/fmt-52/finds/calls_outside_markup_never_break_their_arguments.vl.

Owner questions (as filed; your rulings stand)
1. Generalise the argument-per-line layout beyond holes: recommended, as its own slice next order, after the owner reads a sample of the 1,813 lines. Your ruling is hole-only for this order.
2. The split tuple has no trailing comma, because the grammar has none. Accepted.
3. A trailing `// note` after an argument in a split call attaches above the next argument (the existing comment-attachment rule). Left as is.
