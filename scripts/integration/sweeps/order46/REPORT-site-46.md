## site-46: K14, K15 and the website half of K26 are on branch `site-46`; merging it to `main` is yours

**Branch tip:** `7016f2b2eca0cd1ea5de8a63a18f6839995c2a80`, pushed to vilan-lang/website as the branch `site-46` only. `main` was not pushed or merged.

CI on the branch is green (runs 37146024821 and 37146044566): the site's test harness passes 6/6 files and the playground smoke gate passes 7/7 checks against the v0.43.0 playground compiler.

The report file was refused (subagents can't write report files), so the full `REPORT-site-46.md` text is below. The new-items file is written: `proposals/scripts/integration/sweeps/order46/newitems46-site.json`.

- **K14: done.** The old unmerged `k14` branch is rebased onto main. It was held for "the cut that carries `compile_with`", and every release since v0.41.0 has it. I added the missing "Prelude: web" option to the playground's prelude selector. No example or page panel uses `.map` on a cell, `Map`, `Set`, `MapCell` or `SetCell`.
- **K15: done.** When the formatter declines, the playground now shows "Format left the buffer unchanged — <the formatter's own sentence>" instead of "Format made no changes."
- **Stale comment: fixed.** The `only` comment in `playground/editor-src/editor.mjs` now says both toolchain grammars paint the word.
- **K26: website half done.** All ~200 `view("tag")` chains in the site's source, the four playground examples and both landing-page code panels are element syntax. The site now sets `prelude = "std::web"`, so the examples need no imports. The server-rendered pages are byte-identical apart from two attribute pairs that `vilan fmt` reorders (E151). The client DOM is identical apart from the content changed on purpose. The book's half is left (vilan repo).

**What needs you:**
1. **Merge `site-46` into the website's `main`.** That push deploys. It closes K14 and K15. The old `k14` branch and its worktree become obsolete; I left both alone.
2. **K26 stays open for the vilan repo:** the book's UI snippets, `vilan/examples/`, and the style note in the docs.
3. **The website must be rewritten before the first deploy after v0.44.0.** Once A154 ships, nine site import lines and `prelude = "std::web"` stop resolving. The table below lists every one.

---

# REPORT-site-46 (full text, for `sweeps/order46/REPORT-site-46.md`)

**Repo:** vilan-lang/website.
**Branch:** `site-46`, pushed. `main` was not pushed or merged (R-j).
**Tip:** `7016f2b2eca0cd1ea5de8a63a18f6839995c2a80`, based on `origin/main` @06efc1f.
**Worktree:** `vilan-website/.claude/worktrees/site-46`. The main checkout was clean and was not touched.
**CI on the branch:** green. Harness PASS 6/6 files, smoke 7/7 checks in the v0.43.0 playground wasm.
**Toolchain:** `vilan 0.43.0 (fe092e8d1)`, plus the v0.43.0 wasm fetched with `scripts/fetch-wasm.sh`. No cargo was run; the vilan repo and kolt were not touched.

| Item | State | Commit |
|---|---|---|
| K14: the playground's buffers carry the prelude; examples in the ambient idiom | DONE (the `k14` branch rebased, plus its open gap) | 766d646, d927db6 |
| K15: the playground says when the formatter declined | DONE | d927db6 |
| syntax-46's stale comment (`editor.mjs`, `only`) | DONE | d927db6 |
| K26: element syntax, website half | DONE; the vilan-repo half is left | 0be580d, cf7db54 |
| A ci.yml comment said the playground "carries no prelude" | fixed | 7016f2b |

## Commits

**766d646: the owner's `k14` commit (764442d), rebased.**
- It was held for "the cut that carries `compile_with`". Every release since v0.41.0 carries it, so the hold no longer applies.
- Conflicts in generated files were resolved by regenerating them with their own scripts: `examples.js` (which also retires the shipped example texts) and the editor bundle.
- The smoke gate conflict kept K25's landing-page check as claim 5 and made the toggle's check claim 6.
- Two harness changes were needed:
  - `tests/examples.test.mjs` now checks and builds each buffer under the playground's mode prelude, through a one-line `vilan.toml` (`std::web` for browser, `std::prelude` for node). A native check of a file with no manifest gets the base set on every platform.
  - The restore test now spells out the v0.42 counter literally instead of deriving it from the current example.

**d927db6: K15, the rest of K14, and the stale comment.**
- **K15.**
  - The worker calls `format_checked` when the loaded wasm exports it. It falls back to `format`, then to the unchanged source.
  - The worker carries `declined` on the "formatted" event (`""` when the format went through).
  - The page shows "Format left the buffer unchanged — <sentence>". That is the same sentence `vilan fmt` and the language server use.
  - Pinned by a new `tests/playground-format.test.mjs` (three outcomes) and a new smoke claim 7. The wasm declines an unparseable buffer with a sentence and returns its bytes unchanged; it does not decline the counter example.
- **K14's gap.**
  - The prelude selector gains a third position, "Prelude: web", which pins the web set on either leg.
  - The page sends the words on/web/off, and only the worker maps them to `compile_with`'s argument: `undefined`, `"std::web"` or `"off"`.
  - Share links spell it `&prelude=web`.
  - Smoke claim 6 gains a web half: on the node leg, "on" has no `Signal` and "web" does.
- **The `only` comment** in `editor.mjs` now says both toolchain grammars paint the word, and how its own guard is narrower.

**0be580d: K26** (details below).

**cf7db54: README correction.** `.styled`, `.class` and `class(..)` each set the class attribute, so the last one wins.

**7016f2b: ci.yml comment.** The playground compiler uses its mode's prelude, not none.

## K26 by surface

- **The site's own source (`src/*.vl`).**
  - All ~200 chains are now element syntax. None is left, since the site never picks a tag at run time.
  - A scratch converter (not committed) did most of the work and kept the same desugar wherever possible:
    - attributes undotted (`href(..)`);
    - other links as dotted head items, verbatim (`.styled`, `.show`, `.bind_attr`, `.style_var`, `.toggle_attr`);
    - closure handlers as `on:event(..)`;
    - components and lists in holes.
  - Two spellings change the desugar but not the DOM of a fresh element: `.text(s)` became a quoted child, and `.bind_text(src)` became a `{src}` hole.
  - `toolchain_art` had comments between its chain links, so I converted it by hand.
  - Three showcases now build their prose and code in `let`s instead of passing an element inside a call argument.
  - `vilan fmt` laid everything out.
- **The prelude.** `vilan.toml` sets `prelude = "std::web"`, which is what `vilan init` gives a web package and what the playground's browser mode uses.
  - Removed as redundant: imports of `view`, `View`, `each_by`, `Signal`, `SignalCell`, `Option`, `Some` and `None`.
  - `std::ui::{ mount_root, render }` became `ui::mount_root` and `ui::render`.
  - The `std::style` import lists stay: bare builder names read better, and explicit imports win.
- **The four playground examples.**
  - All are element syntax with no imports; `counter` and `hello` call `ui::mount_root` and `ui::mount`.
  - `styles` now writes its two styles as `css { }` blocks. Their vocabulary is ambient, so the `import std::style::{..}` line is gone and the example does not depend on A154.
  - A grep finds none of the removed spellings in any example or panel.
- **The landing-page panels.**
  - The reactive snippet is the counter in element syntax with no imports. Its prose said `bind_text` and now says "a `{signal}` hole".
  - The diagnostic demo dropped two redundant import lines. Its terminal now quotes `demo.vl:8:14`, re-read from `vilan check` and still held line for line by the test.
  - The test finders now look for `clicked {n} times` instead of `bind_text(`.
- **The style rule** K26 asks for is written once, in README's new "Writing views" section.
- **Harness.** The DOM stub's `textContent` getter now reads all descendant text, as the real getter does. Before, a quoted-child "+1" button was invisible to `click()`.

## Verification

**No behaviour change.** I captured every rendered surface at d927db6 and at 0be580d with v0.43.0: ran the server and the chrome leg, and booted both browser bundles under the test stub.
- Server-rendered `/` and `/playground`: byte-identical except two attribute pairs reordered by `vilan fmt`'s E151 head sort (`aria-label`/`role`, and `value` after `disabled`/`hidden`).
- Chrome export (`header.html`, `header.css`, `tokens.css`) and all four stylesheets: byte-identical.
- Client DOM of both pages: identical, comparing a text node and `textContent` as equal, except the intended snippet, prose and demo changes.

**Every changed example and snippet compiles:**
- with native `vilan check` (clean, no warnings) and `vilan build` + run under the stub, in `tests/examples.test.mjs`. The counter counts, hello prints and mounts, every class on the styles card is a rule in its stylesheet, and the snippet's button moves its label;
- in the v0.43.0 playground wasm (`scripts/smoke-playground.mjs`).

**Site gates:**
- `vilan check .` and `vilan fmt --check .` are clean.
- `node scripts/test.mjs` passes 6/6 files.
- The editor bundle was rebuilt after `npm ci`. Rebuilding the untouched tree first reproduced the committed bundle byte for byte.

## Explicit imports and paths A154 will move (complete, at the tip)

| File:line | Today |
|---|---|
| src/art.vl:22 | `import std::style::{ ... };` |
| src/code.vl:5 | `import std::style::{ Length, Overflow, WhiteSpace, space, style };` |
| src/masthead.vl:4 | `import std::style::{ ... };` |
| src/page.vl:23 | `import std::style::{ ... };` |
| src/playground_page.vl:12 | `import std::style::{ ... };` |
| src/theme.vl:6 | `import std::style::{ ... };` |
| src/topbar.vl:6 | `import std::style::{ ... };` |
| src/server.vl:24 | `import std::document::Document;` |
| src/playground.vl:12 | `import std::asset::bundle;` |
| vilan.toml:23 | `prelude = "std::web"` |
| src/playground/worker.js:87 | `"std::web"` (the "Prelude: web" module path) |
| scripts/smoke-playground.mjs:185 | `"std::web"` (claim 6's web half) |
| tests/examples.test.mjs:55 | `"std::web"` (the playground-mode manifest) |
| src/page.vl:672 | the prose `leaf("std::ui")` in the "Rendered before it ships" card |

- No `std::ui`, `std::dom`, `std::router`, `std::storage` or `std::dev` import is left on the site.
- The examples use only ambient names, plus `std::http` in `server.vl`, which does not move.
- The worker's `"std::web"` is not a purely mechanical rename: `?v=` can pin an older compiler that only knows the old path. Filed as K?1.

## How the owner previews

Nothing deploys a branch, so the preview is local. The lane worktree is ready: the wasm is fetched and the editor's node_modules are installed.

```sh
cd /home/reed/code/vilan-lang/vilan-website/.claude/worktrees/site-46
vilan run .     # http://localhost:3000/ and /playground
```

From a fresh checkout: `git worktree add <dir> origin/site-46`, then `sh scripts/fetch-wasm.sh` and `vilan run .`.

As a PR: https://github.com/vilan-lang/website/pull/new/site-46 (CI runs on PRs).

Worth a look in the browser:
- the three-position prelude selector and a `&prelude=web` share link;
- Format on a broken buffer;
- the four examples;
- the landing page's two code panels.

## Left, and what needs the owner

1. **Merge `site-46` to the website's `main`.** It deploys, and it is the owner's step.
   - It closes K14 (per its own text) and K15.
   - The `k14` branch and the `vilan-website/.claude/worktrees/k14` worktree are then obsolete. I left both untouched.
2. **K26's vilan-repo half stays open.** That is the book's UI snippets, the `vilan/examples/` UI programs, and the book's copy of the style note.
   - Pages: `docs/guide/ui.md`, `guide/styling.md`, `std/browser.md`, `std/reactive.md`, `tour/coming-from-javascript.md`, `guide/routing.md`, `guide/dev-loop.md`, and others.
   - README's "Writing views" can serve as the source for the style note.
   - It is best done in a vilan-repo lane, under the docs gate, after A154.
3. **K28** (the book's one-line `[resource]` heads) is vilan-repo docs and was not touched.
4. **At the v0.44.0 cut.** The deploy installs the latest release. Once A154 ships, the site needs the table's rewrite before its next deploy (the seal's "website re-checked" step).
5. **Not changed:**
   - The editor-band art (`editor_art`) still draws the old 11-line demo with its two import lines and "Ln 10, Col 17". It is decoration, laid out for 11 lines.
   - The card icons could become inline `<svg>` now that `std::ui` creates SVG-namespace elements. I updated the stale comment to say so.

## New finds (newitems46-site.json)

- **K?1.** "Prelude: web" sends the std path `"std::web"`. A154 renames that path, while `?v=` can still pin an older compiler that only knows the old one.
  - Rec: vilan-wasm accepts a reserved word `"web"` beside `"off"` (mapped to `manifest::WEB_PRELUDE`), so the page never spells a std path.
- **E?1.** An element that writes its class twice silently keeps only the last write. This covers `.styled`, `.class`, an undotted `class(..)`, or a second `.styled`; both ui twins `set_attribute("class", ..)`.
  - Probed on v0.43.0: `<div class("x") .styled(card) />` renders card's classes, and the reverse order renders `class="x"`.
  - Element syntax makes `class("x")` the natural spelling for anyone coming from HTML.
  - Rec: (a) a warning naming both writers; (b) making the writers append instead is a question for the owner, after a census.