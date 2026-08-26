# The markdown story — std::markdown, the anchor pin, and the docs-port gate (K13)

> Status: DRAFT 2026-08-24 (cycle 28, work order 10, lane
> `k13-markdown-design`), for owner review. Design-first with a spike;
> the spike's numbers are §5 and the spike itself is deliberately
> uncommitted (§8 says why). Tracker: backlog-2026-08-18.md §K13.
>
> What this paper is for: docs-port.md §3.3 (RATIFIED 2026-08-19)
> filed the port's honest order — (1) a markdown story, (2) a const
> input channel only if the parser runs at compile time (fuel question
> first), (3) router + rung-2 adoption on the site. This paper is
> step 1's design: the grammar scope (from a census, not from
> CommonMark), the AST as plain data, the anchor algorithm as a
> required behavior, parser-in-vilan vs a `[build] run` pre-step
> argued with measured numbers, and the first package-shaped-module
> convention.
>
> Governing records: docs-port.md §2.1 (the port is unavailable today:
> no const input path, no `View` from const, the 1M fuel budget
> exhausted by a char-scan of the largest page) and §4 Q3 (RULED: the
> book keeps `/docs/` and mdBook's `page.html#slug` anchors as a
> compatibility surface); std-shape.md §6 (RULED 2026-08-22, Q4: the
> markdown story is built PACKAGE-SHAPED — own directory-shape
> discipline, no compiler-known names — as the first candidate
> official package under the namespace model, with zero
> registry/loader construction now); documentation.md §4 (the fence
> gate); const-eval.md (the fuel budget and the determinism stance).
>
> Everything measured here was measured on this lane's worktree
> (`next` @ eac75127) with the branch's own debug binary
> (`vilan 0.35.0 (eac75127f)`), the process leg's node runtime, and
> the pinned renderer, mdBook v0.5.4, built locally on a scratch copy
> of `vilan/docs/`.

## 0. Thesis

Four sentences carry the paper.

**The book is small as a grammar.** The census (§1) finds eleven
constructs in real use and eleven measured zeros — no images, no
footnotes, no nested lists, no thematic breaks, no HTML beyond one
`<a id>` shape in one file. A markdown story scoped to the census is
a parser a fraction of CommonMark's size, and the docs gate already
guarantees the scope cannot rot silently.

**Parser-in-vilan is not a bet any more; it is measured.** A 522-line
pure-vilan spike covering the census grammar parses the book's
largest page (`spec/memory.md`, 40,758 bytes) in **1.1 ms** and the
entire 56-file, 585 KB book in **77 ms** as a plain runtime program
under `vilan run` — and reproduces mdBook v0.5.4's heading ids
**449/449, in order, on every rendered page of the book** (§5). The
performance question the fuel budget poses at compile time simply
does not exist at runtime.

**So the recommendation is a runtime parser, not a pre-step and not
const.** `std::markdown` parses `.md` to a plain-data AST on the
process leg; the docs app walks the AST to Views at serve/deploy
time. The `[build] run` pre-step shape is declined (§4): it needs the
same parser anyway and only changes where the output lands — in the
bundle's eager module bindings, the one place it hurts. The const
channel stays deferred (§7): the same AST is const-eligible by
construction whenever step 2 lands, and nothing about the runtime
path has to be undone.

**This lane ships the paper; the package is the next order's build.**
The spike is clean and the build is M-sized, but three rulings below
set precedents bigger than this lane — the scope cut's failure policy
(Q1), the first package-layout convention in the tree (Q2), and the
anchor-compat bar (Q3). Building ahead of those rulings would be
building ahead of the design. §8 gives the judgement in full.

## 1. The census — what the book actually writes

The scope question comes before the design question: a markdown story
for the docs port does not need CommonMark, it needs the book. So the
first act of this lane was a construct census over the book as it
exists on this branch — 56 files under `vilan/docs/**/*.md` (the
`book/` build dir excluded), 599,020 bytes, largest page
`spec/memory.md` at 40,758 bytes. Counts are from a fence-aware sweep
(constructs inside fenced code are not counted; inline-code spans are
stripped before inline constructs are counted). The spike's own block
census (§5) independently reproduces the block-level rows exactly —
455 headings, 385 fences, 31 tables, 27 quotes — so the numbers are
cross-checked by two implementations.

### 1.1 What is in

| construct | count | notes |
|---|---|---|
| inline code spans | 5,247 | the single dominant construct |
| strong `**…**` | 805 | plus ~330 emphasis `*…*` / `_…_` |
| ATX headings | 455 | h1 61 · h2 333 · h3 60 · h4 1; **zero** setext |
| unordered list items | 423 | `-` marker; **zero nested items** in the whole book |
| fenced code blocks | 385 | info strings: `vilan,fragment` 165 · `vilan` 112 · `text` 31 · `vilan,norun` 24 · `vilan,browser` 21 · `toml` 14 · `sh` 8 · bare 5 · `ts` 2 · `json`/`html`/`powershell` 1 each |
| inline links | 476 | cross-page `.md` 408 (33 with `#anchor`) · same-page `#anchor` 35 · external http(s) 25 · section-index dirs (`tour/`, `../std/`, …) 8 |
| tables | 31 | 288 rows incl. headers; pipe tables, delimiter row, **no alignment colons anywhere**; `\|` escapes inside cells on 12 lines (vilan's closure syntax) |
| ordered list items | 35 | flat, sequential `1.` `2.` `3.` |
| blockquotes | 27 blocks | 175 `>` lines |
| HTML passthrough | 49 tags | **one shape in one file**: `<a id="…"></a>` glossary anchors in `appendix/glossary.md`, nothing else |
| autolinks `<http…>` | 1 | `README.md:30` |

### 1.2 What is out — measured zeros, cut deliberately

Zero occurrences in the book, and therefore out of the v1 grammar by
decision, not omission: **images**, **footnotes**, **strikethrough**,
**reference-style links** (`[t][r]` and `[ref]:` definitions),
**setext headings**, **indented code blocks**, **thematic breaks**
(no `---` rule anywhere in 56 files), **nested lists**, **hard line
breaks**, **general backslash escapes** (only `\|` inside table cells
occurs), and **mdBook `{{#…}}` helpers** (`book.toml` declares no
preprocessor). HTML passthrough is scoped to exactly the `<a>` tag
pair; arbitrary HTML is out.

Two constructs stay in despite thin use: tables (31 real uses,
structurally distinct, no cheaper encoding — and the `\|` cell escape
rides with them) and the `<a id>` passthrough (49 uses, and 25 of the
book's 35 same-page `#anchor` links are glossary cross-references
resolving to those targets — dropping it breaks real links).

The census is enforceable, not aspirational: the docs gate walks the
same files on every suite run, and §9 Q1 proposes the parser be
**strict** — a construct outside the grammar is a loud parse error,
so the first page to write a footnote fails the gate instead of
rendering wrong. That converts this census from a snapshot into a
contract, the same move `documentation.md` §4 made for fences.

## 2. The AST — plain data by construction

The one shape docs-port.md §2.1/A4 proved viable is a const-evaluated
**plain-data** tree: structs, enums, tuples and `List` survive const
evaluation and lower to plain JS arrays; `Shared` cells, `View`s and
closures do not. So the AST is designed to that bar from day one —
not because v1 runs at compile time (it does not), but because
keeping the parser's output plain data is free now and is precisely
what makes the module const-eligible later with zero rework.

```vilan,fragment
// std::markdown — the whole public surface is plain data:
// str, i32, bool, List, and these two enums. No Shared, no View,
// no closure anywhere in or under a parse result.

enum Inline {
    Text(str),
    Code(str),                    // content, span-trimmed
    Strong(List<Inline>),
    Emph(List<Inline>),
    Link(str, List<Inline>),      // destination, label
    Html(str),                    // one raw tag, verbatim: <a id="…">, </a>
}

enum Block {
    Heading(i32, List<Inline>, str),  // level 1–6, content, id (§3)
    Paragraph(List<Inline>),
    CodeFence(str, str),              // info string, verbatim body
    Quote(List<Block>),               // recursive, probed to work
    Items(bool, List<List<Inline>>),  // ordered?, flat items (census: no nesting)
    Table(List<List<Inline>>, List<List<List<Inline>>>),  // header, rows
}

struct Doc {
    blocks: List<Block>,
}

fun parse(source: str): Doc
fun heading_id(content: List<Inline>): str   // §3's base algorithm, dedupe-free
```

Design notes, each load-bearing:

- **Tuple-payload variants, house style** (`option.vl`, `json.vl`'s
  `JsonKind`). Recursive payloads through `List` (`Quote`,
  `Strong`) compile and run today — probed on this branch.
- **The renderer is not in the package.** `std::markdown` produces
  `Doc`; walking `Doc` into `View`s (or into HTML strings, or into
  anchors for an LSP gate) is the consumer's code. That split is what
  keeps the package platform-neutral, const-eligible, and out of the
  `View` problem entirely — the parser never touches `std::ui`.
- **Heading ids are computed by the parser**, not the walker, because
  they are a compatibility surface (§3), not a rendering choice: every
  consumer must see the same id for the same heading, including a
  consumer that renders nothing (a link checker, the D17/D19 LSP
  deep-link gate).
- **The info string is carried verbatim** (`vilan,browser` stays one
  string). Interpreting harness tags is `documentation.md` §4's
  business; the parser does not own that vocabulary.
- **`CodeFence` bodies are verbatim** — byte-fidelity here is what
  lets a future docs app hand fences to the highlighter and the
  playground-link pass unchanged, and what a §3-style differential
  gate against the docs-gate extractor needs (§8).
- **Census scope shows in the types**: no image/footnote/hr variants,
  `Items` is flat, `Table` has no alignment field (zero alignment
  colons in the book). Widening any of these later is an additive
  enum-variant/field change behind a ruled scope change (Q1).

## 3. The anchor algorithm — a required behavior

Q3 of docs-port.md pinned the URL space: the book keeps mdBook's
`page.html#slug` anchors as a compatibility surface. The consumers
are concrete: 32 LSP keyword-hover deep links into
`https://vilan-lang.org/docs/` (`crates/vilan-lsp/src/document.rs`),
the VS Code extension and brew formula pinning that base, 33
cross-page anchored links and 35 same-page anchors inside the book
itself, riding 455 headings. Any renderer that ever replaces mdBook
must reproduce its id algorithm exactly — so the algorithm is a
**required behavior of `std::markdown`**, specified here and pinned
by test, not an emergent property of whatever the parser happens to
do.

**The algorithm** (mdBook v0.5.4, established by probe against the
built book, all 449 rendered heading ids):

1. Take the heading's inline content as text: code-span content kept
   (backticks gone), emphasis/strong markers gone (their text kept),
   link labels kept (destinations dropped), raw HTML tags dropped
   entirely, and the HTML-encoded forms of `& < > ' "` dropped.
2. Map per character: ASCII letters lowercased and kept, digits kept,
   `-` and `_` kept, **each** whitespace character becomes its own
   `-`, everything else is dropped. (mdBook keeps non-ASCII
   alphanumerics too; the book has none today — the vilan
   implementation should match mdBook, and the golden corpus carries
   a non-ASCII case so divergence is loud, not latent.)
3. Dedupe per page: the second occurrence of a base id `b` becomes
   `b-1`, the third `b-2`. Unexercised in the book today (zero
   within-page collisions — probed across every built page) but
   pinned anyway; it is exactly the kind of silent tiebreak that
   D19-class bugs are made of.

The consequences are unintuitive enough to need pinning — measured,
not derived:

| heading (source) | mdBook id |
|---|---|
| `# Spec §1 — Introduction & conformance` | `spec-1--introduction--conformance` |
| `## 6.0 The law — owners, epochs, and claims` | `60-the-law--owners-epochs-and-claims` |
| ``## `Shared<T>`: one cell, many holders`` | `sharedt-one-cell-many-holders` |
| `# Macros & const` | `macros--const` |
| ``### Option::take and Option::replace`` | `optiontake-and-optionreplace` |
| ``## Conversions: `as_*` `` | `conversions-as_` |
| ``## `macro { … }` blocks`` | `macro----blocks` |

(Each dropped character between two spaces yields consecutive
hyphens; `§`, `.`, `:`, `&`, `<`, `>`, `*`, `{`, `}`, `…`, and the
em-dash all drop. D19 — the one broken LSP deep link — was exactly a
hand-guess of this algorithm: `impl:` guessed as `impl--`, mdBook
emits `impl-`.)

**The pin strategy.** The suite deliberately excludes the site build
(`docs-site.md`: no external binary in the test run), so the pin
cannot be "run mdbook and diff" in CI. Instead, two artifacts ship
with the package:

1. **A unit corpus** of heading → id pairs covering every dropped-char
   class in the table above, plus the dedupe suffixes and a non-ASCII
   case — compiled into the package's tests, red if the algorithm
   drifts.
2. **A book-wide golden**: the full `page → [ids]` listing for all
   449 rendered headings, generated from a local `mdbook build`
   (regeneration documented, needed only when the mdBook pin moves),
   checked against `std::markdown`'s output for every page by a test
   that walks `vilan/docs/**/*.md` exactly as the docs gate does.
   The spike already ran precisely this comparison once by hand —
   449/449 — so the golden starts life verified, and the D17-family
   LSP-link gate gains the shared source of truth it wanted.

## 4. Parser-in-vilan vs the `[build] run` pre-step — with numbers

§3.3 named two candidate shapes. Spelled out, they are not really
parser-vs-pre-step — **both need the same parser**; a pre-step that
converts `.md` to generated `.vl` still has to parse markdown, in
vilan or in something else, and "something else" abandons the
dogfooding that motivates the port. The real axes are *where the
parse runs* and *what ships*:

| shape | parse runs | what ships | viable today? |
|---|---|---|---|
| A. runtime library | process leg, at serve/deploy | `.md` + parser | **yes — measured** |
| B. `[build] run` pre-step | before each build, emitting generated `.vl` | AST literals in the bundle | yes, but see below |
| C. const | compile time | AST literals in the bundle | no — input channel + fuel (§7) |

**A is sufficient, and the numbers say so.** The spike parses the
largest page in 1.1 ms and the whole book in 77 ms including file
reads (§5) — on the process leg, where the docs app actually runs.
The site's production is static: the deploy renders by curl and
commits HTML (`docs-port.md` §1.4), so the parse cost is paid at
deploy time, a handful of milliseconds against a CI job measured in
minutes. Even a live server re-parsing every page on every request
would be comfortably inside interactive budgets. There is no
performance case for moving the parse earlier.

**B pays real costs to buy nothing A lacks.** The hook exists
(`manifest.rs:378` — `[build] run`, shipped, re-run before each build
and each watch round), but the emitted `.vl` would be 585 KB of AST
literals in **module-level bindings, which never split**
(`bundle-splitting.md`; docs-port.md §2.1/A7) — the entire book eager
in whatever bundle imports it, against a browser leg that never needs
the parser at all under A. It also creates a generated-file hygiene
problem (commit them and they drift; ignore them and every fresh
checkout builds differently before the first `vilan build`), and it
puts generated code where the docs gate reads sources. The pre-step
remains the right tool for *external* generators (Tailwind is the
manifest's own example); for markdown it is a worse delivery of the
same parser.

**C is step 2, not step 1** — deferred, with its price list in §7.
The decision that matters here is that A does not foreclose C: the
AST is const-eligible by construction (§2), so if the input channel
and fuel story ever land, `const parse(...)` is the same call in a
different position.

**Recommendation: A.** Build `std::markdown` as a runtime library;
no pre-step, no compiler change, no new capability. The docs port's
step 1 is then done the moment the package ships.

## 5. The spike — evidence

Scratch program `spike/md.vl` in the code worktree (522 lines, 467
non-blank/non-comment), **deliberately uncommitted** per the lane's
stop condition — §8 records the decision; the numbers survive here.

**What it covers**: the census grammar — ATX headings, fenced code
with info strings, paragraphs, flat ordered/unordered lists with
continuation lines, recursive blockquotes, pipe tables, inline
code-span runs (multi-backtick, CommonMark space-trim), strong,
emphasis with word-boundary `_` handling, links, autolinks, the
`<a id>` passthrough — plus §3's id algorithm with per-page dedupe.
**Known simplifications**: no `\|` table-cell unescape, fence
close is trim-based rather than the docs gate's indent-tracked rule,
paragraph-level backslash escapes ignored — none exercised by the
anchors gate, all owed by the real package (§8).

**Environment**: this branch's debug compiler
(`vilan 0.35.0 (eac75127f)`), `vilan run` on the process leg (node),
WSL2. Timing via `std::time::now_millis` around the parse loop only;
file reads excluded in phase A, included in phase B.

**The numbers**:

| probe | result |
|---|---|
| largest page, `spec/memory.md` | 40,758 bytes (40,582 UTF-16 units), 777 lines |
| parse result | 98 blocks: 19 headings, 13 fences, 3 tables, 10 lists, 53 paragraphs |
| parse time, 100 iterations | 114 ms total → **1.14 ms/parse** |
| whole book, 56 files, one pass | 595,974 chars → 2,192 blocks in **77 ms** incl. reads |
| completes as a plain runtime program? | yes — exit 0, no fuel, no budget, no capability wall |
| anchors vs mdBook v0.5.4 (built locally) | **449/449 identical, in order, all 55 rendered pages; 0 divergences** |
| construct cross-check vs the independent census | headings 455/455 · fences 385/385 · tables 31/31 · quotes 27/27 |

Two readings worth making explicit. First, the anchor row is the
strong one: it is not "the slugs look right", it is byte-identical
agreement with the real renderer over the entire compatibility
surface §3 pins, including every adversarial heading in the book.
Second, the runtime numbers convert §2.1's fuel wall into a
*located* problem: the same workload that exhausts a 1M-fuel const
budget somewhere under 60K characters runs in about a millisecond
per 40K-character page at runtime. The wall belongs to the const
evaluator's pricing, not to vilan-the-language or the parser design.

## 6. The package shape — the first convention

std-shape.md §6 Q4 (RULED): build the markdown story as if published
— the first candidate `std::` package under the namespace model —
with zero registry or loader construction now. This paper must
therefore propose what "package-shaped" physically means in-tree
today, and the proposal becomes the convention for every official
package that follows.

**The constraint that shapes it**: the analyzer populates `std` by a
non-recursive `read_dir` of the layer roots — a std module *is* a
file stem, std paths are exactly two segments (`std::markdown::parse`),
and nothing nests (std-shape.md §1). A literal package directory
inside `std/src/` needs loader work that the ruling explicitly
declines to build now.

**The convention, proposed** — a package-shaped std module is:

1. **One base-root module file**: `vilan/std/src/markdown.vl`.
   Base root, not a platform layer — the parser is pure computation,
   platform-neutral by placement. Precedent for a parser as one file:
   `json.vl`, 1,258 lines. Spelling: `std::markdown`, final under
   the namespace model — the file *moves* when std-shape §4's
   manifest-of-entries exists; the spelling never does.
2. **Leaf imports only**: nothing beyond Tier-1 core
   (`list`/`string`/`option`/`result`/`display`/`compare`). No
   `reactive`, no `ui`, no `rpc`, no `[extern]`, no host binding of
   any kind. Greppable, and cheap to assert in a test.
3. **No compiler-known names**: the analyzer and transformer must
   never capture a `markdown` identifier (std-shape §4 documents the
   existing captures the package must not join). This is the one
   rule that keeps a future package rev free to move between trains.
4. **Plain-data public surface**: every public type reachable from a
   parse result is `str`/`i32`/`bool`/`List`/struct/enum — the
   const-eligibility invariant, stated in the module header and
   pinned by a test that const-evaluates a small parse the day the
   input channel exists (until then, by review).
5. **A header contract block**: the module opens with the
   package-shaped declaration — its scope (the census), its
   compatibility surface (§3), and the rules above — so the
   convention travels with the file, not just with this paper.
6. **Its own docs page and test surface**: `docs/std/markdown.md`
   (fence-gated like every page), a corpus program exercising the
   parser end-to-end, unit pins per construct **including every §3
   corpus case**, and the book-wide anchor golden.

**Considered and declined**: a real sibling package
(`vilan/packages/markdown/` with its own `vilan.toml`, consumed as a
path dependency). It is more literally "package-shaped", but its
spelling today would be `markdown::…`, not `std::markdown::…` — the
graft-under-`std` machinery is exactly what std-shape ruled *not* to
build yet — and a spelling that changes later is the one cost the
namespace model exists to avoid. The convention above gets every
discipline benefit at zero loader cost and keeps the proof case
(re-home the file, keep the spelling) available.

## 7. Step 2, deferred: the const input channel and the fuel budget

Recorded so the deferral is a decision with a price list, not a
shrug. For `const parse(read_file("page.md"))` to be real:

1. **An input channel.** A new host builtin with a carve-out in the
   capability gate (`interpreter.rs:359-372` refuses every `[extern]`
   at expansion time today), a build-invalidation story (a const
   result now depends on a file the compiler must watch), and a
   ruling against const-eval.md's determinism invariant — its asset
   channel is deliberately emission-only. A proposal of its own.
2. **A fuel answer.** The budget is 1,000,000 per const expression, a
   compiler constant, no memoization, evaluated every compile
   (const-eval.md). docs-port.md measured ≈17–24 fuel per character
   for a do-nothing scan. The spike's parser touches most characters
   several times (delimiter rescans, inline recursion, the slug
   pass); calling it 3–10× the minimal loop prices one parse of
   `spec/memory.md` at roughly **2.5–10M fuel — already 2.5–10× the
   entire budget** — and the whole book at tens of millions,
   *estimated from those measured constants, not measured directly*.
   So step 2 is not "raise the constant": it is budget-as-knob plus
   memoization, on a const pass that is already the measured hot spot
   (const-eval.md §10.5).
3. **A reason.** This is the part that is missing. Under §4's
   recommendation the runtime parse costs ~77 ms per whole-book
   deploy. The const win would be deleting a 77 ms step by adding an
   input channel, a cache, and a fuel redesign — and pushing 585 KB
   of AST literals into never-split module bindings. Nothing on the
   docs port's critical path wants that trade.

Deferred, then, with the exit open: the AST is const-eligible by
construction (§2), so step 2, if something ever demands it, is
purely additive.

## 8. The unblocking path, and the stop-condition judgement

**The path** (docs-port.md §3.3's order, now with step 1 designed):

1. **Next order: build `std::markdown`** to this paper, behind §9's
   rulings. Size: M — the spike's 522 lines grow to an estimated
   900–1,400 with the `\|` cells, gate-grade fence rules, strict-mode
   diagnostics, doc comments, and the §3 corpus; plus the docs page
   and tests. One lane. Two build items beyond the spike deserve
   naming: fence-extraction **agreement with the docs gate** —
   `docs.rs` and `parse_differential.rs` already carry two copies of
   the fence rules that must agree, and the package makes a third, so
   the package's fences should be differential-tested against the
   gate's unit-pinned cases — and the **strict-mode diagnostics** Q1
   proposes, which are what turn the census into a contract.
2. **Then the port lane** (K6's declined literal ask, docs-port §3.3
   step 3): router + rung-2 adoption on the site, and a docs app that
   walks `Doc` to Views under the site's chrome. Step 2 (const) is
   explicitly **not** on this path (§7).

**The stop condition, judged.** The lane brief allows building now if
the design is unambiguous, the spike is clean, and the build stays
S–M. The spike is clean (§5) and the build is M — but the design is
not unambiguous in the one way that matters: Q1's strictness policy
decides the parser's error surface, Q2 sets the first package-layout
precedent in the tree (a convention every later official package
inherits), and Q3 fixes a compatibility bar this project will carry
for years. All three are owner-shaped calls, the owner's review queue
is where they are headed, and building against guessed rulings is how
a "package-shaped" module ships needing rework the moment the ruling
lands differently. **So: paper now, package next order; the spike
stays uncommitted** — its value is its numbers, which this paper
carries, and committing scratch code with known simplifications would
only invite someone to grow it into the package without the rulings.

## 9. Owner questions

> **RULED 2026-08-24 — all as recommended.** Strict parsing (an unknown
> construct is a loud parse error the docs gate catches); the one-file
> package layout + six-rule discipline is the tree's convention; the
> anchor bar is bit-exact mdBook v0.5.4 id parity (unit corpus + the
> 449-id golden). **The build is AUTHORIZED** — rulings 1–3 landed as
> recommended; the build lane seeds from the preserved spike.

1. **The scope cut, and its failure mode.** Ratify the census grammar
   (§1.1 in, §1.2 out) as `std::markdown` v1, with **strict** parsing:
   a construct outside the grammar is a parse error naming the
   construct, so the docs gate catches the first page that writes a
   footnote. The lenient alternative (pass unknown text through)
   renders wrong quietly. Recommend: strict.
2. **The package-layout convention** (the first one, precedent for
   every official package): §6's shape — one base-root module file
   plus the six-rule discipline, `vilan/packages/` declined until
   std-shape §4's machinery exists. Accept?
3. **The anchor-compat bar.** Bit-exact id parity with mdBook v0.5.4
   — algorithm, per-whitespace hyphens, dedupe suffixes and all —
   pinned by the §3 unit corpus plus the 449-heading book-wide
   golden, regenerated only when the mdBook pin moves. This is the
   strongest form of docs-port Q3's ruling; anything weaker re-opens
   the 417-link surface page by page. Accept?
4. **Build timing.** §8 recommends the package builds next order
   behind rulings 1–3 rather than in this lane. Accept — or, if the
   rulings all land as recommended, authorize the build as the next
   lane's first item without a further review round?

## 10. Ship record — the build (2026-08-24, cycle 28, Order 10 extension, lane `markdown-build`)

> **OWNER NODS 2026-08-25**: `Items` carries BLOCK bodies (`List<List<Block>>`)
> — the build's correction of §2's sketch stands, and the docs-app lane
> inherits the shape; the golden's regeneration rule is the STANDING
> rule (regenerate only from a real local mdBook v0.5.4 build, CI only
> diffs — revisit when the docs app lands).

Shipped to the paper and the §9 rulings: `vilan/std/src/markdown.vl`
(the one-file package, 1,017 lines), its docs page
`vilan/docs/std/markdown.md` (+ SUMMARY entry), the book-wide anchor
golden with its regeneration script, 35 pins in `inference.rs`, and the
golden/discipline gate `markdown_golden.rs`. Vilan commit: fa742f146 (branch `markdown-build`).
Seeded from the preserved k13 spike; every simplification §5 named as
owed (the `\|` cell escape, gate-grade fence rules, strict diagnostics)
is paid below.

### 10.1 The anchor bar, verified harder than §3 asked

**456/456 rendered heading ids, bit-exact and in order, against a local
mdBook v0.5.4 build of the book as it now stands** — the census's 449
had drifted to 450 on this branch (the l12/i4 doc edits added
`## Reserved names` and `### Searching & equality`, net +1), and the new
docs page adds 6 more. Verified order-preserving per page, not sorted.

The empirical corpus run (a scratch mdBook book of the §3 table plus
non-ASCII, closing-run, tag, and dedupe cases) caught **two facts the §3
spec and the LSP twin's comments understate**, both fixed before ship:

1. **mdBook lowercases with full Unicode**, not ASCII: `## École Été`
   renders as `école-été`. `book_sync.rs`'s `normalize_id` twin
   (`to_ascii_lowercase`, comment "lowercased") matches the book only
   because the book has no non-ASCII heading today. The package folds
   kept units through the host's Unicode `toLowerCase`.
2. **mdBook trims the heading text after tag-dropping**:
   `## <a id="x"></a> anchored` is `anchored`, not `-anchored`. The twin
   does not trim and would emit the latter.

The twin divergences are latent (zero exercised headings) but D19-class;
flagged as an owner question (§10.9 Q2). Non-ASCII beyond the pinned
classes is a documented approximation in the module header: keep/drop is
a curated range table (all punctuation planes the book could plausibly
write), and non-BMP units (surrogate pairs) drop. The corpus pins
`café-naïveté`/`école-été` so any real divergence is loud.

### 10.2 Deviations from §2, recorded

1. **`Items` is `(bool, List<List<Block>>)`, not
   `(bool, List<List<Inline>>)`.** The build found §2's sketch wrong
   about the book itself: bullets in `tour/async.md` ("No top-level
   await"), `guide/reactive.md` (derived state), and `spec/memory.md`
   (R2/R10/R11) carry multi-paragraph bodies and 2-space-indented
   fences *inside* items — six fences and their blank-line-separated
   paragraphs, none of which an inline-only item can hold. The spike flattened them into sibling
   top-level blocks (which is why its census cross-check still matched);
   a docs app walking that AST would render them outside their `<li>` —
   exactly Q1's "renders wrong quietly" failure mode. Items are block
   lists; a simple item is one `Paragraph`. Pinned by
   `markdown_a_list_item_carries_blocks` on the async.md shape.
2. **`parse` returns `Result<Doc, ParseError>`**, not bare `Doc` — the
   §9 Q1 ruling's strict failure mode made concrete.
   `struct ParseError { line: i32, message: str }` (1-based line; exact
   for block constructs, the enclosing block's opening line for inline
   ones) with a `Display` impl rendering `line N: message`.
3. **`CodeFence` bodies carry one trailing newline per line** — the docs
   gate's extraction shape, so the package's fences byte-agree with
   `docs.rs`/`parse_differential.rs` extraction (§8's differential
   debt). The gate's D3 fence rules ship exactly: indent-tracked close
   (same indent, `` ``` `` alone), CommonMark up-to-indent dedent —
   pinned by four mirrors of `docs.rs`'s `extract_pins` cases.

### 10.3 The parse-error shape: a library `Result`, no ledger row

The `fs`-throws / `decode`-returns-Result fork resolves as the paper
guided: callers are programs, so strict refusals are values —
`Result<Doc, ParseError>`, the `from_json` precedent. **The message
surfaces nowhere as a compiler diagnostic head** (no `diagnostics.push`
site exists or is planned), so no diagnostics-ledger row is claimed;
row 255 remains free. If a future docs-gate integration ever prints
these through the CLI as diagnostics, that lane owes the row.

### 10.4 Strictness as shipped

Every §1.2 construct has its own refusal pin (20 strict pins), each a
loud `ParseError` naming the construct and its line: setext underlines,
thematic breaks, nested and indented list items, indented code blocks,
footnotes, reference links and definitions, images, strikethrough, raw
HTML beyond `<a id="…">`/`</a>` (with a backtick steer for bare
generics like `List<T>`), backslash escapes outside `\|`-in-cells, hard
and backslash line breaks, tilde fences, unclosed fences, table
alignment colons, custom heading ids (`{#…}` — mdBook supports them,
census zero, and one would silently change an id), and **lazy
continuations** of blockquotes and list items (CommonMark folds those
into the block; treating them as siblings would render wrong quietly,
so both are refusals — book count: zero). The whole book strict-parses
with zero refusals; the sweep that calibrated this (fence- and
code-span-aware, all 56 files) found the book clean on every rule, the
only near-misses being multi-line code spans (`Holder<Dog>` on a
wrapped line), which paragraph-joining closes before inline scanning.

Plants (targeted binary, restored): dedupe suffix removed → dedupe pin
red; footnote check removed → its pin red printing `parsed`; the
general-punctuation drop range removed → corpus pin AND the book golden
red (first hit `appendix/cli.md h2 vilan-run-file-args`); fence close
reverted to the spike's trim-based rule → the different-indent mirror
pin red.

### 10.5 The golden, and its regeneration story

`crates/vilan-core/tests/markdown_anchors.golden` — 456 `page hN id`
lines over 56 rendered pages — is **generated from a real mdBook build,
never from the parser under test**: `scripts/regen-markdown-golden.py`
(committed) refuses to run unless `mdbook --version` is exactly the
pinned v0.5.4, builds `vilan/docs` to a temp dir, and extracts every
`<hN id>` in document order. `markdown_golden.rs` needs no renderer in
CI: it compiles a walker program against the real std, runs it under
node, and diffs — so it doubles as the strict gate (a page stepping
outside the grammar fails the suite with the refusal line). Regenerate
when a page's headings change or the mdBook pin moves; the diff is
reviewed as a URL-surface change. The same file also carries the
six-rule discipline pin: markdown.vl's imports must stay Tier-1 core
and the file must declare no `[extern]`/`external`.

### 10.6 Perf: the shipped parser beats the spike

Same machine, same debug-binary-compiled program shape, process leg
(node), medians of three: **whole book 64–66 ms including file reads**
— now 57 files / 604,321 chars with the new page (spike: 77 ms, 56
files / 595,974 chars) — and **0.87–0.93 ms per parse of
`spec/memory.md`** over 100 iterations (spike: 1.14 ms). Strictness,
the `\|` unescape, gate-grade fences, and block-bodied items cost less
than the spike's substring-heavy close-search; §4's "no performance
case for moving the parse earlier" stands stronger than written.

### 10.7 A transformer finding: `is` in a loop condition reads a stale subject

Found the moment the spike was ported to house style: an `is` pattern
test in a `for` (while) **condition** compiles to a subject binding
hoisted *before* the loop (`const $a = found;`), so a reassignment in
the body never reaches the condition. Minimal repro (no std beyond
print/Option):

```vilan,norun
import std::print;
import std::option::Option::{ None, Some, self };

fun main() {
	mut found: Option<i32> = None;
	mut cursor = 0;
	for (found is None) && cursor < 3 {
		found = Some(cursor);
		cursor += 1;
	}
	print(cursor);   // expected 1; prints 3 (with no bounding conjunct: infinite loop)
}
```

`vilan check` is clean; the emitted JS is wrong. The same expression in
an `if` is fine (fresh per evaluation); the hazard is specifically the
re-evaluated condition position. The package works around it with a
bool flag (one commented site in `parse_inline`). Not fixed in this
lane — a transformer miscompile wants its own pinned fix on the
analyzer/corpus gates, and the lane's ruling scope was the package.
Filed as Q1 below; the repro is reproduced verbatim above so the fix
lane needs nothing from this worktree.

### 10.8 Files touched

vilan (branch `markdown-build`): `vilan/std/src/markdown.vl` (new),
`vilan/docs/std/markdown.md` (new), `vilan/docs/SUMMARY.md`,
`crates/vilan-core/tests/markdown_golden.rs` (new),
`crates/vilan-core/tests/markdown_anchors.golden` (new),
`crates/vilan-core/tests/inference.rs` (+35 pins),
`scripts/regen-markdown-golden.py` (new), `CHANGELOG.md` (feature
entry). Suite: green — `cargo nextest run --workspace` 4098 passed, 6 skipped, exit 0. proposals (branch `markdown-build`): this
section.

### 10.9 Owner questions

> Status: OPEN 2026-08-24 — for review with the build.

1. **The `is`-in-loop-condition miscompile (§10.7).** Wrong values (or
   hangs) from clean-checking source; the repro above is minimal. File
   as its own backlog item for a transformer lane? The corpus has no
   program in this shape, which is why it built clean; the fix lane
   should pin exactly the repro plus a `Result` variant.
2. **The LSP twin's two latent divergences (§10.1).** `book_sync.rs`'s
   `mdbook_heading_ids` lowercases ASCII-only and skips the post-tag
   trim; both diverge from measured mdBook v0.5.4 on headings the book
   does not yet write. Align the twin with the package (and consider a
   differential test between them), or leave until a heading exercises
   it?
3. **`Items` as block lists** is a §2 deviation taken on build authority
   (the paper's "unless the build finds a flaw" clause) — the evidence
   is §10.2. Nod wanted since every future consumer (the docs app lane
   next) inherits the shape.
4. **The census drift rule.** The golden regenerates from mdBook when
   docs change; regeneration requires mdbook v0.5.4 locally (CI never
   runs it). Acceptable as the standing workflow, or should the docs
   gate grow a CI-side rebuild once the docs app lands?

## 11. Ship record — step 2: the const input channel and the fuel answer (2026-08-26, cycle 29, Order 11, lane `k13-step-2`)

SHIPPED (vilan 5d434d29, merged 37787a39). `std::asset::read(path)` is
the channel's input direction — §7's deferral built: package-root-
relative (absolute and root-escaping paths refused lexically, before
any filesystem look, so the refusal is deterministic), const-only under
exactly `emit`'s machinery (the const-only fixpoint generalized from
one anchor to the set, diagnostics naming which builtin a value
reaches), every read a tracked build input (`Program::const_input_files`,
misses included so an appearing file invalidates too) with all three
invalidation legs proven — the watch trigger re-runs on a read-input
change, an unchanged-source round still recompiles a leg whose inputs
changed, and the in-process pin guards future caches — and reads charge
fuel per byte, so the budget bounds input size as it bounds
computation. Determinism (const-eval.md §9.5) is restated per
build-input closure in spec §9.2.

The fuel answer is a measured raise, not the knob: parsing the book's
largest page (docs/spec/memory.md, 40,758 B) under const eval costs
2,001,457 fuel — §7's 2.5–10M estimate, honestly labeled an estimate,
was high — so the explicit budget rises 1M → **16M** (8× the heaviest
real workload; a runaway `const` still misses its budget in ~1 s on the
release binary), inferred and macro budgets deliberately unmoved,
`VILAN_PHASE_TIMING` printing `const-fuel-max` as the permanent
instrument. §8's `[const]` knob and §4's memoization stay the owner's
open questions, untouched. The centerpiece pin reads the real golden
book page and parses it with `std::markdown` inside const eval, within
budget — step 2's whole point, held red if page or parser outgrow the
budget.

PARKED for the owner: the LSP re-analyzes only on `.vl` events (the
VS Code watcher glob is `**/*.vl`), so an `.md`-only edit shows stale
const diagnostics until the next `.vl` event — every build/check/watch
path is fresh. Widen the watcher (all files, or a recorded-inputs
mechanism), or accept next-edit freshness for v1 the way module-text
staleness once was?

**RECOMMENDATION 2026-08-26 (the owner asked which is better): the
recorded-inputs mechanism, not `**/*`.** Three reasons, and the first
is decisive. (1) `**/*` breaks the load-bearing invariant
`watch-mode.md` states in so many words — only `.vl` files are tracked,
so *"a build can never trigger its own rebuild"*; a glob that also
matches `dist/`, `.parse.out` and every generated artifact re-opens
exactly the self-triggering loop that invariant exists to forbid, and
would have to positively exclude output paths to be safe (the same
objection `dev-refresh.md` §2(iii) raised when it deferred widening the
compiler's watched set). (2) The precise set already exists and cost
nothing to obtain: this step records `Program::const_input_files` per
analysis, misses included, which is *by construction* the exact list of
files whose change can alter a diagnostic. (3) LSP has the mechanism —
dynamic `workspace/didChangeWatchedFiles` registration, re-registered
when the recorded set changes; the fallback when a client refuses
dynamic registration is today's behaviour, which is the status quo, not
a regression. The shape: after each analysis, diff the recorded input
set against the registered one and re-register on change. Cost is one
LSP capability plus a set diff, and it stays correct as the channel's
customers grow (the docs app will read hundreds of `.md` files — the
rung where `**/*` would be at its worst and a recorded set at its
best). Accepting next-edit freshness is defensible for v1 and costs
nothing today; the recommendation is to build the recorded-inputs
watcher when the docs-app rung lands, and not to widen the glob at any
point.

NEXT on the ladder: the router/docs-app rung (§8's stop-condition
judgement governs).
