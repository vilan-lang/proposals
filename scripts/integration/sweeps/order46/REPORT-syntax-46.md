## syntax-46: final report

**Branch tip: `be34a97f`** on `syntax-46` (worktree `vilan/.claude/worktrees/syntax-46`, off `origin/next` @fe092e8d). Eight commits, nothing pushed. All the listed gates pass at the tip.

The tool refused to write `REPORT-syntax-46.md`, so the full report is below for you to save as `sweeps/order46/REPORT-syntax-46.md`. The new finds were written to `proposals/scripts/integration/sweeps/order46/newitems46-syntax.json`.

| item | status | sha |
|---|---|---|
| B520 foreign spellings | LANDED | 8212fdd8 |
| B486 marker order (with B485 Q7 and Q8) | LANDED | da452c3e |
| B487 `const` takes labels | LANDED | 20dda773 |
| B493 local-label refusal | LANDED | 9f5497b7 |
| B494 `async x = 1;` | LANDED | 0cd12ef0 |
| K26 grammar half (`only`) | LANDED | 5e319020 |
| N138 `vilan fmt` walking `target/` | LANDED | f5c1f18f |
| B485 Q10 (`[resource]` on its own line) and the keyword rule in the spec | LANDED | be34a97f |
| K24 | report only (below) | — |

Every commit has its CHANGELOG entry under a new `## Unreleased`, each with its `<!-- family: … -->` marker. Commit trailers use `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`, following the session's attribution reminder rather than the brief's plain "Claude Opus".

**Gates at the tip** (machine load was about 7 to 11 from the other lanes):

| gate | result |
|---|---|
| `cargo fmt --check` | pass |
| `cargo clippy --workspace --all-targets -D warnings` | pass |
| vilan-core: lib, inference, parse_differential, marker_census, deep_nesting, module_resolution, markdown_golden, docs, check_scope_differential (one run) | 6307/6307 |
| deep_nesting with `VILAN_CANARY_STACK_KIB=1536` | 18/18 |
| vilan-cli: corpus, diagnostics_ledger, grammar_sync, fmt_declines, native_differential | 217/217 |
| `scripts/ci-local.sh vilan-fmt` | green |

- native_differential ran only in its default mode, not both modes.
- No corpus golden moved.
- Each new pin was planted red first (I disabled the fix and watched the pin fail), except the controls that hold today's behaviour.
- I did not touch the analyzer's expression walk, so no frame re-measure was needed.

## B520: `return`, `fn`/`function`/`func`/`def`, `->`

**On the base:**
- `return 1;` gave "expected `;`" plus a second "body ends without producing a value".
- Every function declared with `fn` led to "cannot find '<name>'".
- `-> i32` gave "found '-' expected '{' or ';'".

**None of the five words is reserved.** `let return = 1;`, a field `fn: i32`, `fun def(fn: i32)`, `fun return()` and `import a::{ fn }` all check clean before and after. A pin holds 18 such programs.

**How it works.** The parser rewrites the token in place, only where no name can stand:
- **`return`** at the head of an expression, followed by a name (other than `then`), a literal, or `if`/`match`/`await`/`const`/`css`/`async`, becomes `ret`. This covers a statement, a match arm, a closure body and a `then` branch.
  - It is also refused as an operand, so `1 + return 5` reports the missing operand and then the steer, as `ret` would.
  - It is a recovery sync point.
- **`fn`/`function`/`func`/`def`** at an item head, followed by a name and `(` or `<`, becomes `fun`.
  - It looks past attributes and `export`/`async`/`external`/`const`/`macro`, in a module, an impl's item list and a trait body.
  - It is also a sync point, so `pub fn f()` gives the `pub` rule and then the `fun` steer, nothing more.
- **`->` written as one arrow** after a `fun`'s or a closure literal's parameter list is read as `:`. In a closure type (`|i32| -> str`) it is read past, because the result follows `|..|` directly there.

Each produces one diagnostic at the foreign token, and the parse then reads exactly as if the right spelling had been written. A pin checks this over 29 shapes, comparing the tree with the respelled source's tree.

**Not steered:** bare `return;`, `return (x)`, `return -x` and a block tail `{ return }`. Each is a valid parse today (a read of a binding named `return`), so only the analyzer can steer them. Filed as B?2.

### The codes and the fix data (for editor-46)

Everything is in `vilan_core::parsing`:
- `pub enum ForeignSpelling { Return, Fn, Function, Func, Def, Arrow, TypeArrow }`, with `ALL`, `written()`, `vilan()` (the replacement text), `code()`, `message()`, `fix_title()` and `of_message(&str) -> Option<ForeignSpelling>`.
- **Stable codes** from `ForeignSpelling::code()`, to publish as the LSP `Diagnostic.code`:
  - `foreign-spelling/return`
  - `foreign-spelling/fn`
  - `foreign-spelling/function`
  - `foreign-spelling/func`
  - `foreign-spelling/def`
  - `foreign-spelling/arrow`
  - `foreign-spelling/type-arrow`
- The pipeline's `Error` has no code field. The diagnostic is recognized by its message instead: it is rendered with no context and no hint, so `of_message` is an exact match.
- **The fix:** `pub fn foreign_spelling_fix(source: &str, message: &str, span: Span) -> Option<SpellingFix>`, where `SpellingFix { code, title, span, replacement }` means "replace `span` with `replacement`".
  - A word's span is the diagnostic's own (`return` becomes `ret`, `fn` becomes `fun`).
  - The arrow's span widens left over the blanks before `->` and writes `:`, so `fun f() -> i32` and `fun f()\n  -> i32` both become `fun f(): i32`.
  - A closure type's arrow widens right over the blanks after it and writes nothing, so `|i32| -> str` becomes `|i32| str`.
  - Titles: "Write `ret`", "Write `fun`", "Write `:` for the return type", "Remove the `->`".
  - A pin applies ten fixes and re-parses each one clean.

**Ledger:** four `NEW` rows. The messages:
- "`return` is not a vilan keyword: vilan spells this `ret` — `ret value;` returns a value, and a bare `ret;` leaves a function that returns nothing"
- "`fn` is not a vilan keyword: vilan spells this `fun` — `fun name(parameter: Type): Result { … }`" (the same for `function`, `func` and `def`)
- "`->` is not how vilan writes a return type: vilan spells this `:` — `fun name(parameter: Type): Result`, and `|parameter: Type|: Result` on a closure"
- "`->` is not how vilan writes a closure type: its result follows the `|..|` directly — `|Type| Result`, and `|| Result` with no parameters"

I did not build R-h's other candidates. `null` is already a reserved literal, and no probe showed a misleading message for the rest.

**Docs:** the tour's functions page and the JavaScript phrasebook. `lexical.md` gets a line in be34a97f.

## B486 with B485 Q7 and Q8

**What B485 still needed.** I read the paper against the tree first. Order 45 had already landed B445 (attributes on either side of `export`) and the formatter flip. Left were:
- Q7: attributes in any order.
- Q8: one keyword order, with a steer.
- Q10: `[resource]` on its own line.
- S3: the v0.44 refusal of the old order.

**How it works.** At every item head (a statement head or a trait member), the run of attributes and marker keywords that ends at a declaration word is put, once, into the order the parser's productions read:
- Attributes are sorted by the new `pub fn parsing::attribute_rank`, which is today's production order, so no attribute moved.
- `export`, `const` and `macro` go ahead of the attributes; `lazy`, `async` and `external` after.

Diagnostics:
- **No diagnostic** for attribute order, or for `export` on either side of the attributes. The same goes for `macro`, because `macro [attr] fun` already parsed before this change.
- **One refusal, spanning the run, when a keyword stands ahead of an attribute or two keywords are inverted.** The text is "a declaration's markers are written in one order — its attributes, then the keywords `export`, `const` or `lazy`, `async`, `external` or `macro`, then the declaration word: write `[platform(..)] async fun`". The head is then read as if written in that order.
- **Left alone:**
  - A run that does not end at a declaration word (`[a][b];`, `async { }`).
  - A keyword set that no order makes legal; its own production refuses it.
  - A repeated `export`, which stays B492's refusal.

Nodes keep their written start position. The formatter's safety net sorts attribute runs, and moves a trailing `macro`, the same way in both streams, so a reordered head formats instead of being declined.

**The 29 swaps** from papers-45's matrix:
- 24 now parse and format exactly like the canonical stack.
- The other 5 carry the steer: `async`↔`[platform]` (twice), `external`↔`async`, `external`↔`[resource]`, and `lazy`↔`[internal]`.
- `[derive(..)] export struct` no longer steers to an import (B445 fixed it; now pinned).

Three old parser pins that asserted out-of-order attributes are refused now assert the ruled acceptance. The marker census was regenerated. One `NEW` ledger row. Docs: `grammar.md` §3.2 and §3.3.

## B487

`const fun` and `const let` now take `[deprecated]`, `[internal]` and `[must_use]` (and a `let`'s labels), written ahead of the keyword:
- The canonicalizer moves `const` ahead of the attributes, and `parse_const_declaration` then reads the declaration's own prefix.
- A deprecated `export const let` or `const fun` warns at its uses in another module (probed).
- The formatter prints the labels above and `const` on the signature line, with `export` ahead of it.
- `const [x] fun` gets B486's steer.
- Docs: `const.md` §9.6.

## B493 and B494

**B493.** The refusal of a label on a local `let` now names the labels actually written (in `labels.rs`). Ledger row 567 is re-keyed. I left the impl-label refusal alone: it states the rule for both labels and is not wrong when only one is written.

**B494.** `async x = 1;`, `async x: T = 1;`, `async let x = 1;` and `async mut x = 1;` now get one refusal at `async` and are read as the plain binding. It is a new curated rule, `ASYNC_MARKS_NO_BINDING`; the ledger's rule-site count goes from 60 to 61.

**Found along the way:** before this change, `async x = 1;` with `x` already bound passed `vilan check` and emitted invalid JavaScript, because it parsed as an assignment to the place `async x`. The general hole is filed as B?1, rated HIGH.

## What B485 still leaves

- Q7, Q8 and Q10 are built.
  - Q10 reformatted 37 `[resource]` heads in std: 21 in `delta.vl`, 11 in `reactive.vl`, 3 in `process/fs.vl`, and one each in `task.vl` and `process/db.vl`.
  - It also reformatted three corpus programs and one native fixture. No golden moved.
  - Field and variant attributes stay inline.
- Q1's keyword-vs-attribute rule is now written into `lexical.md` §2.2.
- **S3 is not built: the refusal of `export` (or `macro`) ahead of the attributes, with a quick fix, which Q9 schedules for v0.44.0.** It is a small change: the canonicalizer already isolates that case.
- The book still has 20 fence lines with `[resource]` on the declaration line (filed as K?1).

## K26 grammar half, and K24

Both toolchain grammars now paint `only` as a keyword after a path's end (a name or `}`) and before `;`: the VS Code TextMate grammar and the book's `vilan/docs/theme/vilan.js`.
- `ret`, `else`, `then`, `await`, `const` and `async` before it are ruled out by name, so `ret only;` stays plain.
- `grammar_sync`'s `UNPAINTED_CONTEXTUAL_WORDS` list is now empty.
- Its word reader now skips the words inside a negative lookbehind, as it already did for a negative lookahead.
- A new pin checks four modifiers and twelve plain uses of the name, running both rules in node.

**What the website needs (I did not touch it):**
- Nothing functional. `playground/editor-src/editor.mjs` already paints `only`, with its own import-line guard.
- Its comment near line 70, "Neither toolchain grammar paints it yet", is now stale.

**K24.** Its original ask is already met: the keyword lists come from one source. Since K27, `playground/keywords.js` is generated from `vilan --print-keywords` and gated by `tests/keywords.test.mjs`.
- What is still copied by hand is the positional rules (the site's `CONTEXTUAL_RULES` before/after regexes).
- Those could come from one source if the compiler exported a position per contextual word, for example `{word, before, after}` JS-regex pairs.
- The catch: TextMate's engine needs fixed-length lookbehind and JavaScript does not. So the TextMate rule would be held to the exported rule by probe strings rather than generated from it.
- Recommendation: a small item only if the three copies start to drift. Today they agree.

## N138

N133 made `vilan fmt` skip a directory carrying cargo's `CACHEDIR.TAG`. But cargo only writes that tag into a `target/` it creates itself, so a `target/` made first by hand has none. A lane's `target/<lane>-scratch/`, made before the first build, is exactly that case.
- `vilan fmt` now also skips a directory named `target` that sits beside a `Cargo.toml`.
- A vilan module directory named `target`, with no `Cargo.toml` beside it, is still formatted.
- I chose this over listing files with `git ls-files` in the leg: that would lose the formatter's three distinct exit codes (piped through xargs) and miss untracked new fixtures.

## New finds (`newitems46-syntax.json`)

- **B?1 (HIGH, JS miscompile):** an assignment to something that is not a place (`-x = 1`, `!b = true`, `(x + 1) = 2`, `await x = 1`) passes `vilan check`, and the JS backend emits invalid code that throws at load.
- B?2: a bare `return;` still says "cannot find 'return'". The steer belongs in the analyzer's unresolved-name path; `ForeignSpelling` is public for it.
- B?3: `macro async fun` parses and `async macro fun` does not. Small, for the owner to rule on.
- K?1: the book's one-line `[resource]` heads.
- N?1: `diagnostics-ledger.tsv` has a stale `NEW` row in the middle of the file (line 598), inherited from next.

## Needs the owner or the integrator

1. **B485 S3:** should the refusal of `export`/`macro` ahead of the attributes ride v0.44.0 at this order's seal, as Q9 schedules it? R-f's breaking list does not name it, so I did not build it.
2. **Q10 moves std:** 37 `[resource]` heads across five files, including `reactive.vl`. reactive-46 and store-46 will hit conflicts on those head lines only. If that is unwelcome, be34a97f stands alone and can be dropped or deferred.
3. **Merge notes:**
   - This lane creates `## Unreleased`.
   - It adds five `NEW` ledger rows (four for B520, one for B486) and re-keys row 567.
   - The rule-site count is now 61.
   - The marker census golden moved in four commits.
   - editor-46 rebases onto this branch for `ForeignSpelling` and `foreign_spelling_fix`.
