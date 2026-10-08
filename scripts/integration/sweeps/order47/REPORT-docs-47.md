# docs-47 report

**Tip `f8a0b35a`** on base `origin/next` @`b94cb47f`. I created the worktree at c43d6ab9 and fast-forwarded it to b94cb47f, which includes the native-47 merge (and its memory.md §6.9 paragraph), before making any edit. `origin/next` had not moved when I re-checked at report time, so no rebase was needed. Five commits, not pushed. Worktree: `vilan/.claude/worktrees/docs-47`. `LANE-STATUS.md` is untracked there.

## Per item

| item | verdict | sha | what was really the case |
|---|---|---|---|
| K26 (book half, R-h) | DONE | 1d35c5b3 | The UI snippets in 13 book pages are now element syntax. Building UI opens on markup and gains a style note, "Markup or chain", taken from the website README's rules. The chain stays where it is the subject: the `bind_attr` contrast, placing a run at the end with `child`, and the `View` reference. The five UI examples are converted: reactive-ui, router, ssr, todo, walkthrough. Their READMEs are fixed too; they still said `count.map(..)` and the retired `View.swap`. Corrected on the way: (1) ui.md's Fragments section claimed a `when` body, `swap` render or `each` row refuses a fragment. That is false; they take any `Slot`, and I verified it. (2) transient.md called the retired `View::each`. (3) The todo and walkthrough `client.vl` were missing `import std::debug::Debug` (B515 warnings). Every example builds with 0 warnings, and its CSS is byte-identical to the base build. The JS differs where `.text` became a child text node. Std paths in the book were already the new ones (the docs gate compiles them). |
| | | | **The premise missed one thing.** The SSR example's client-boot test went red because the shared DOM stub's `textContent` read only the element's own text, so `<li>{task}</li>` read empty. I fixed `crates/vilan-cli/tests/support/dom/stub.js` to read the way the DOM does (every descendant text node in order). The two serializers that wanted only the element's own text now read `_text` explicitly. All 10 stub suites pass: 116/116. |
| | | | **Perf.** `vilan check` instructions, base → after: router +1.15%, reactive-ui +1.13%, ssr +0.44%, walkthrough +0.43%, todo +0.18%. I measured the cause on router: the quoted text children cost it (three alone are +0.47%); the reactive hole costs nothing over `bind_text`. I added `[[bump]]` rows ×1.012 for reactive-ui and router (item K26). All five examples stay under their ceilings. |
| L16 | DONE | 163449ca | There are 19 ParseError sites, not "~20". I added 19 `NEW` rows to `diagnostics-ledger.tsv`, keyed on each message as printed; the two composed messages (backslash escape, raw HTML tag) use slots. Each message already had a pin (`inference::markdown::markdown_refuses_*`), so the C2 pins existed. I proved the rows hold by rewording two messages in markdown.vl: the gate went red, then I restored the file. No wording changed; the em-dash style stays parked on the REWORD ruling. |
| N140 | DONE | f4bed6ae | **The premise was wrong.** The row was not an unnumbered row. It was a duplicate of row 570 (B407): the integrator numbered 570 in Order 42, and transient-44's rebase fold (024e890c) "restored" the lane's `NEW` copy. I deleted it. `the_index_is_well_formed` now refuses a numbered row after a `NEW` row, as the index's header always promised; proven red on a planted row. |
| N142 | PARTIAL (by ownership) | b85811cc | Respelled the comments in node.rs and inference/modules.rs. `native/reassigned_closures.vl` now calls `adders[2](30)` directly; the native differential pin passes. I left the 7 analyzer.rs comments alone because the brief keeps me out of that file. A ready patch for the next lane that touches it: `sweeps/order47/docs-47/finds/n142-analyzer-comments.patch` (`git apply --check` passes). |
| N143 | DONE | f8a0b35a | The tree actually has 1,149 declarations, 70 files and 34 bare-marker modules (the comment said 741/63/33). The 856/548/308/152 figures were stale too. I dropped all the figures, kept the recipes, said why there are no numbers, and respelled `resource struct` as `[resource] struct`. |
| K24's remainder | NO-OP | — | Nothing is owed in this repo. The book's keyword list is already generated and gated by `grammar_sync`. I compared the book's contextual-keyword regexes with the site's `CONTEXTUAL_RULES` on 35 probe lines: they agree on every one. The stale site comment syndicated in syntax-46's report ("Neither toolchain grammar paints it yet") is already gone from the website. |

Each commit carries a `## Unreleased` CHANGELOG entry: K26 tooling, N140 tooling, L16 diagnostics, N142 tooling, N143 tooling. The markdown anchor golden was regenerated; the only change is one new anchor, `guide/ui.md h3 markup-or-chain`.

## For the integrator / rulings
- **No ruling is needed.** For the record: the K26 bumps are +1.2%, under the 3% approval line.
- The L16 verdicts for the ledger prose:
  - 14 rows QUALIFY: each names the construct and its line, plus the in-grammar alternative.
  - 5 rows have no steer beyond removing the construct: image, footnote, strikethrough, hard line break, backslash line break. Acceptable for a strict docs grammar.
  - All 19 have the em-dash style that is parked under REWORD.
- Expect a textual conflict at the ledger TSV tail and in `## Unreleased` with the other lanes.
- **solver-47:** the examples' B515 sites (the two `client.vl`) are fixed here. I scanned every compiled docs fence with `vilan check`: 0 errors and 0 warnings, so the book is clean under both coming flips.

## Finds filed
`sweeps/order47/newitems47-docs.json`, with repros in `sweeps/order47/docs-47/finds/`:
- **K?1:** the `vilan init` templates (`templates/browser/counter.vl`, `templates/fullstack/src/client.vl`) are still `view(..)` chains. K26's scope never named them.
- **E?1:** a non-text hole such as `<p>{count}</p>` or `<p>{5}</p>` gets "does not implement trait 'Slot'". It is spanned on the element's `<` rather than the hole, names std's `child`, and does not suggest the i-string or `.derive` fix.
- **E?2:** a fragment returned where a `View` is wanted gets a bare "Expected View, but got List<View>". The book promises "a type error that says so".

## Gates (on f8a0b35a, base b94cb47f)
- `cargo fmt --all --check`: 0
- `scripts/ci-local.sh vilan-fmt`: green
- clippy `--workspace --all-targets -D warnings`: 0
- `cargo nextest run --workspace -j 6`: **9643/9643 passed**, 33 skipped
- Docs gates by name, all passing in the full run: `docs::every_doc_example_compiles`, `markdown_golden`, `book_mirrors` (both tests). Also targeted before commit: diagnostics_ledger 25/25, examples, ssr_fullstack, ssr_differential, chunks, style_chain_order.
