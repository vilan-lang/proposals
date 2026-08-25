# Vilan Backlog — open items (re-baselined 2026-08-18)

**The single planning surface.** Everything open lives here; nothing else
is tracked anywhere else. The chain: `backlog.md` (the alpha capture,
frozen 2026-07-18) → `backlog-2026-07-18.md` (the cycle 15–19 era, frozen
2026-08-18) → this file. `roadmap.md` is superseded the same day — its
ranked-strategy role is the **Now / Next / Later** block below; its Done
chronicle stays where it is as history.

The rules, tightened where the last tracker drifted:

- **Open items only.** When an item ships, its tombstone paragraph moves
  to [`backlog-archive.md`](backlog-archive.md) in the same sweep that
  closes it, and the number is retired. A `STATUS: OPEN` line whose body
  says "COMPLETE" (how E55/E56/I4 read by the end) is the exact failure
  this rule exists to prevent.
- **Item numbers are stable identifiers**, per-section, never reused.
  Numbering continues from the frozen tracker (highest retired: A24,
  B124→125 below, C10, D14, E61, F13, G4, H9, I5, J6).
- **Carried items keep their live remainder only**; full shipped context
  lives in the frozen file, cited as `History:`.
- `STATUS: OPEN` / `OPEN (blocked: <what>)` / `OPEN (proposal-first)` /
  `OPEN (deferred: <demand gate>)` — same legend as before, plus the
  explicit deferred form for demand-gated items.

**Owner questions parked in papers** (the recall surface — each waits on
a ruling, none blocks unrelated work): optimistic-lifecycle.md §9 (the
paint-less action-state cell; caller-less free `optimistic`),
draft-reconnect.md §4 (default debounce for `bind_draft`), bindgen.md §8
(Q1/Q2/Q3/Q6). RULED 2026-08-18, all as recommended: beta.md §4,
design-language.md §3, method-resolution.md §13.6, const-eval.md §10.5
(Option A). RULED 2026-08-19, all as recommended: remote-sources.md §6
(A25 — `sub` keeps `|T|`, no `Stale`, `Waiting`/`Ready` + `or`, deferred
`Unsubscribe`), docs-port.md §4 (K6 — option B; accept the prerequisite
filing as K13; chrome mechanism (i); keep `/docs/` anchors; keep search,
index weight = N14; `header.hbs`; no `&v=` pin).

## Now / Next / Later

- **Now** — cycles 19–26 closed. Cycle 26 (2026-08-20) shipped E78
  (the unprovided-context error underlines every uncovered call on the
  path — the owner's ask, example-as-contract), E76 (one index space at
  the ariadne boundary), E77 (hatches compose onto supplied shells,
  checked), K11 (wasm pruned to 6 + the stale-pin fallback), K13 step 3
  (the site itself on rung 2, pixel-identical), N7 (branding manifest +
  byte-equal shadow recipes), and three papers awaiting rulings: B127
  (delete the blanket — census says zero serving sites), L10 (the
  namespace model), N15 (the proposals-repo migration plan). What is
  active: nothing — **v0.35.0 SHIPPED 2026-08-21** (the owner's call, a
  day before the scheduled Saturday): the first train on the scripts
  (cut refused nothing; release 773da400, 33 entries) and the first fold
  under the ruleset (8d7fe41b, all ten steps clean, the bypass notice on
  `main` as expected), the re-themed book + masthead live, the toolchain
  at 0.35.0 in both locations. The playground-todo A25 diff turned out
  already applied by the owner; the kolt patches remain theirs. Beta
  (b): v0.35.0 is the first counted train — earliest (b) 2026-08-29.
  Wave 2 (2026-08-22, the owner's ruling batch): b126 MERGED on the nod
  (3b83d7e5 + repair aaaf4d2a); website main @f3ede99 DEPLOYED (E80 pane +
  K9 completion; live once v0.36.0's wasm ships). RULED: C3a (widened to
  any external package → E84), E79 ×7 (→ E85/E86/K17), K9 ×4, B127 DELETE,
  M9 nod, L4 ×4, N15 ×6, E69 deferred (generated vocabulary direction),
  L10 ×5 (→ L12), E87 probed and filed. Wave 2 CLOSED 2026-08-23:
  b127 SHIPPED (blanket deleted; B128 + B130 closed with it), l4 SHIPPED
  (the deprecation mechanism whole), m9 SHIPPED (overlay-owned loads,
  ASan-proven, the soak reads zero), n15 PREPARED (extraction verified,
  runbook persisted — the cutover waits on the owner creating
  `vilan-lang/proposals`). Archive 75. **Order 10 (cycle 28) CLOSED 2026-08-24** — seven lanes, all
  SHIPPED (l12 reserved names + the std-shadowing hole; e83 completion
  parse-once 60.8→5.8 ms; k13 markdown.md PROPOSED, spike-proven, build
  behind §9's rulings; e84 package demotion widened; diag-anchors E82's
  finalize_build class + B131; std-doc-smalls E85/E86/E87/I4 + K17
  deployed; closure-ret-family B132/B133/B134 incl. a RELEASED
  miscompile — the unannotated loaned-tail alias). Archive 92. next
  @12dfa484 (suite 4061); proposals main @f1890b6; website main
  @e18eb0c + one HELD commit (a359612, lands after v0.36.0).
  **v0.36.0 SHIPPED 2026-08-24/25** (the owner's call,
  early again): release 0fb5e5f0 after ONE gate incident — the wasm
  tests' stack margin (SIGABRT on CI, fixed + plant-proven before any
  publish leg ran; the tag moved cleanly; B138 files the depth) — then
  13/13 green; fold 1a4444b0 carried the N15 freeze to vilan main; the
  playground's trace pane + completion are LIVE; the held website
  commit deployed (ed7cc20). Beta accounting: v0.35.0 → v0.36.0 = two
  consecutive trains, no patch between — trigger (b)'s letter may now
  be satisfied (early cuts vs "weekly rhythm" is the owner's Q1-style
  call), and B73's fix shipped, unblocking (c); (a) kolt migration and
  (d) D5 remain. **Kolt refactored current with 0.36.0** (2026-08-25,
  the owner's ask; kolt@4289594 on its vilan-migration branch: the
  builder chain, the generated shell, the counted mirrors; build +
  10/10 probe + 16/16 e2e green — whether this satisfies (a)'s letter
  is the owner's call; E92 filed from its one dogfood finding). What
  is active: nothing — Order 11 on the owner's ask.
- **Next** — the owner's parked rulings (B127 §14.1; L10 §6 ×5; N15 §8
  ×6; L4's four; M9's nod; E79's §10.1 review; N8's sunset; beta.md
  §5.1 at the switch; the REWORD candidates), then the build lanes they
  unlock (B127's deletion, M9's overlay loads, N15's cutover), K9
  (design-first: the completion core's seam for wasm), E69/E80, B125,
  B126, B130, D5's session. The Zed extension (E62) is DEFERRED by
  ruling.
- **Later** — the long-gated compiler tails (A7/A8, B3/B11, C1/C2, I2,
  J4 — each blocked on a named design or the native arc), D5's traction
  plan (needs its dedicated session), and the beta switch itself
  (trigger-gated: earliest 2026-08-29 for condition (b); (d) rides D5).

---

## A. Reactive core & UI (`std::reactive`, `std::ui`)

7. **SSR tail** (S3 demand-gated; factoring undesigned)
   STATUS: OPEN (blocked: kolt/walkthrough SSR factoring undesigned; S3 demand-gated on real usage)
   v1 (render + replace) SHIPPED 2026-07-23. Live remainder: **S3, the
   Wire initial-state blob**, stays unbuilt by decision (demand-gated per
   ssr.md §6c — the double-fetch stands); and the S2 amendment's real
   open scope — **kolt and the walkthrough cannot SSR under v1** (views
   read the live rpc client at build time, handlers capture it,
   browser-layer imports), an applicability factoring question recorded
   only in ssr.md's amendment. Resumability = A7b, ssr.md §7.
   History: backlog-2026-07-18.md §A item 7.

8. **UI styling — the tail** (entangled pieces only)
   STATUS: OPEN (blocked: A7/G2 — liveness-tied emission)
   The 2026-08-04 slices closed everything unentangled. Remainder:
   critical CSS and liveness-tied dead-style elimination, riding A7/G2's
   liveness-tied emission — nothing else. Adjacent open find: A22
   (same-family rule ordering). History: backlog-2026-07-18.md §A item 8.

14. **Reactive residuals** (S–M)
    STATUS: OPEN (narrowed — one mechanism + two parked owner questions)
    Live remainder: `batch` async-join drain affinity — `batch` kept its
    `sync` fence at the turn merge; joining an ambient turn from an
    awaiting body is unresolved. The optimistic lifecycle and `Draft`
    auto re-push both SHIPPED 2026-08-04; their parked owner questions
    are indexed in this file's header. History: backlog-2026-07-18.md §A
    item 14.

## B. Type system & the type solver

3. **Variadic-generics tail** (M–L)
   STATUS: OPEN (remainder: keyof + symbolic pack concatenation, flat-tuple elision, B4-linked dispatch)
   B3a (spread parameters) SHIPPED 2026-08-04; tuple-value spread's
   circle closed. Remainder: `keyof`; symbolic pack concatenation;
   eliding the flat-tuple construction copy; trait-typed-value dispatch
   (→ B4). Record: variadic-generics.md §S/§T. History:
   backlog-2026-07-18.md §B item 3.

11. **`!` / `?.` tail** (M)
    STATUS: OPEN (design-gated only — try-and-lift.md §12.1/§12.2)
    The bare-`?` trait path shipped. Remainder, both genuinely
    undesigned: §12.1 closure `!` (arg-becomes-Result, RpcOutcome×Try
    collision, which closures may host a `!`) and §12.2 Signal/Promise
    Lift opt-ins (Signal::map SUBSCRIBES — `signal?` would mint an
    unowned subscription per render, the A21 leak shape). Recorded §11:
    B29 does not cover a wrong-shaped Lift impl. History:
    backlog-2026-07-18.md §B item 11.

135. **NEW — the operator path skips monomorphization for all-native bindings and hits the no-body guard** (S–M; found by std-doc-smalls 2026-08-24; B127's family, the OPERATOR half)
    STATUS: OPEN
    A conditional trait impl whose body calls the trait method explicitly
    (`fun eq(self, other) { ... self.get(i).eq(other.get(i)) ... }`) ICEs
    through the OPERATOR path at an all-native binding — `List<i32> ==
    List<i32>` reported "internal: a call resolved to `PartialEq`'s
    requirement `eq`, which has no body…" while `List<List<i32>> ==` and
    explicit `.eq()` calls worked: the operator lowering skips
    monomorphization for all-native bindings, assuming the body uses only
    operators on `T`. Std works around it (compare.vl's body uses `==`, the
    Option/Result idiom, recorded in its doc comment) but a USER impl can
    still trip it. Same transformer territory D3/§14 mapped; probe, pin
    #[ignore]d if not fixed, fix the general path. Record: std-doc-smalls'
    report Q1.

136. **NEW — an `is` test in a loop CONDITION compiles against a hoisted copy of its subject** (M; found by markdown-build 2026-08-25; MISCOMPILE, live in releases)
    STATUS: OPEN
    The transformer hoists `const $a = subject;` before the `while`, so body
    reassignments never reach the condition's `is` test: the minimal repro
    (markdown.md §10.7, verbatim) prints 3 where 1 is correct, and the
    unbounded form LOOPS FOREVER — which is how it surfaced (the spike port
    hung). `vilan check` is clean; the defect is codegen. One commented
    workaround site in std/src/markdown.vl (a bool flag) comes out with the
    fix. Probe per loop form (`for cond`, infinite+break, nested), pin
    red-first, fix the general hoist rule. Record: markdown.md §10.7.

137. **NEW — book_sync's `normalize_id` diverges latently from std::markdown's anchor rule** (S; found by markdown-build 2026-08-25)
    STATUS: OPEN
    The LSP twin lowercases ASCII-only and skips the post-tag-drop trim —
    both empirically wrong against mdBook v0.5.4 (`École Été` → `école-été`;
    tag-dropped headings trim). No book heading exercises them TODAY, which
    is why the deep links still land. Align the twin with the package's
    `heading_id` and add a DIFFERENTIAL pin (the twin against std::markdown
    over the golden's 456 ids) so they can never drift apart again.
    Record: markdown.md §10.

138. **NEW — the analyzer's recursion depth needs 64 MiB of headroom** (M; surfaced by the v0.36.0 gate's SIGABRT 2026-08-24)
    STATUS: OPEN
    A modest server program's analysis overflows a 1–2 MiB stack (the
    release gate aborted; local passed one margin over — the wasm tests now
    ride the 256 MiB harness thread like every vilan-core binary, and the
    shipped wasm links 64 MiB). The depth itself is the smell: measure
    WHICH path recurses (likely `infer_type_inner`/the constraint walks —
    instrument max depth per phase the VILAN_PHASE_TIMING way), then make
    the deepest path iterative (the E73 hover precedent: iterative with a
    seen-list) or explicitly bounded with a clean refusal. The 256 MiB
    spawns and the 64 MiB link flag shrink to documented safety once the
    depth is understood. Record: the stack-fix commit on next (0fb5e5f0's
    parent message has the incident).

## C. Memory model

1. **`Weak<T>`** (M)
   STATUS: OPEN (blocked: Tier 2 refcounting, the native arc)
   Fully specified in destruction.md §10 (incl. the scoped
   `get(&self): Option<&T> borrows self` twin from claims-and-epochs.md
   §5a). Deterministic `upgrade() → None` needs a release event, which
   only exists once handles are refcounted; GC-timing `WeakRef` rejected
   2026-07-07. History: backlog-2026-07-18.md §C item 1.

2. **Dynamic rule-4 remainder** (M)
   STATUS: OPEN (blocked: F4's native memory story)
   Cross-handle aliased writes (two `Shared` handles, one cell) need
   runtime generations / poisoned views; semantically empty on JS. Build
   with the native memory story, likely debug-mode-only. History:
   backlog-2026-07-18.md §C item 2.

## D. Documentation

5. **Public traction plan** (M; a PLAN first, not execution)
   STATUS: OPEN (blocked: needs a dedicated session with the owner)
   Blogs, website, and other resources for public traction. Candidate
   skeleton in the frozen entry (landing page, "why vilan" essay, deep
   dives, demos, distribution as on-ramp). Public-exposure choices
   interact with the pseudonym discipline; voice/positioning are the
   owner's calls. Overlaps §K's web arc — coordinate, don't duplicate.
   History: backlog-2026-07-18.md §D item 5.

## E. LSP & tooling

37. **bindgen v2 — the remainder** (M–L)
    STATUS: OPEN (remaining: (c) the oxc swap-in seam and (d) the override-table direction, both unscheduled; the 183-globals "read a global" language question; §11.6's shallow `--only` mode; §8 Q1/Q2/Q3/Q6 remain the owner's)
    (a)(b)(e) SHIPPED 2026-08-06 (92.3% of lib.dom declarations). Record:
    bindgen.md §11. History: backlog-2026-07-18.md §E item 37.

62. **NEW — Zed language extension** (M–L; owner's 2026-08-18 list, item 4)
    STATUS: DEFERRED (owner ruling 2026-08-18: a tree-sitter grammar is one more thing to maintain after every syntax change — revisit when the syntax settles, i.e. at or after the beta switch) Strategy ratified 2026-08-25: skeleton-grade static grammars + semantic tokens as truth; E91 makes the tables generated so this grammar is born gated.
    Zed extensions are Rust→WASM: a tree-sitter grammar plus glue
    launching `vilan-lsp` (which already ships per-release). The grammar
    is the bulk of the work and pays twice — GitHub's syntax
    highlighting consumes tree-sitter grammars too. Survey question for
    the order: what the existing `editors/` assets (TextMate grammar?)
    can seed.

69. **NEW — attribute-NAME completion in an element head is a semantics decision** (S–M; deferred by the E67 lane 2026-08-18)
    STATUS: DEFERRED (owner ruling 2026-08-22: if offered at all, the vocabulary should be GENERATED — not handcrafted or hand-maintained; decide later. The generation source is the open question when revisited — §9.3's objection was a second source of truth, which a generated, gated table answers)
    `<div .|>` now completes the View's methods and `<div |>` the dotted
    links + `on:` — but attribute NAMES (`name(..)`, `type(..)`, …) are
    not offered, because the desugar has no table of them to consume
    ("no special-cased names in the lowering table, ever"), and a list in
    the LSP would be a second source of truth with nothing to gate it;
    deriving one from DOM bindings was rejected (IDL property names ≠
    attribute names). Offering them means amending §9.3 (a curated
    vocabulary the desugar validates AND completion reads) — the owner's
    call. Also not attempted: tag-name completion and the child position.
    Record: editing-dx.md §18.

88. **NEW — a dependency named `std` resolves opposite ways in the compiler and the IDE** (S; found by L12's probe 2026-08-24)
    STATUS: OPEN (defensive — unreachable through manifests since L12)
    Pre-L12, the analyzer bound a dependency named `std` OVER the standard
    library (resolve_import_root checks dependencies first) while vilan-ide's
    completion (completion.rs:525) answers the stdlib — two answers for one
    name. L12's manifest refusal makes the shape unreachable through
    manifests, but a programmatically built Workspace can still stage it.
    Either align the two resolvers or refuse at the Workspace layer too;
    pin whichever. Record: L12's report, Q3.

91. **NEW — grammar_sync generates the token tables, so the tree-sitter grammar is born gated** (S–M; the owner's grammar-strategy ask, filed 2026-08-25)
    STATUS: OPEN
    The strategy (owner + orchestrator, 2026-08-25): the compiler stays the
    one grammar truth, delivered as SEMANTIC TOKENS wherever LSP runs
    (already shipped in the VS Code extension; TextMate is the documented
    fallback); every static grammar is deliberately SKELETON-grade
    (keywords, comments, strings, numbers, attributes, element tags); the
    tree-sitter grammar for Zed is written ONCE at/after the beta switch
    per E62's standing deferral — ideally after I2 (const generics) and
    B3's keyof land or park, the only foreseeable medium syntax changes.
    This item is the enabling work: extend grammar_sync.rs from GATING the
    word lists (TextMate + highlight.js today) to GENERATING the token-table
    halves from the lexer's exported tables (`lexing.rs` KEYWORDS et al.) —
    emit the keyword/operator/literal fragments the grammars consume
    (including, when it exists, tree-sitter's `grammar.js` tables and its
    query files under the same gate), leaving only the structural rules
    hand-written. Pins: the generated fragments byte-match what each
    grammar registers; a lexer keyword added without regeneration goes red.
    Notes for the eventual E62 lane: VS Code has NO tree-sitter support and
    none announced (TextMate + semantic tokens indefinitely); Zed is
    tree-sitter-ONLY for highlighting (weak semantic-token support), so the
    grammar carries real weight there; GitHub consumes tree-sitter for code
    navigation, TextMate (linguist) for highlighting — both grammars have a
    second customer. Record: this entry is the strategy record until the
    E62 lane opens its paper.

92. **NEW — `vilan build` leaves a superseded process artifact in place after a rename** (S; found refactoring kolt to 0.36.0, 2026-08-25)
    STATUS: OPEN
    A project last built before v0.33.0's artifact rename (process legs
    `.js` → `.mjs`) rebuilds clean on the current toolchain — and leaves
    the OLD `dist/server.js` sitting beside the new `dist/server.mjs`.
    Nothing removes or flags it, so a script, Dockerfile or process
    manager still saying `node dist/server.js` keeps launching the
    superseded application silently — exactly the drift the gotchas page
    warns about, with nothing in the toolchain to catch it (kolt's
    2026-08-01 `dist/` reproduced this live: both generations present
    after one 0.36.0 build). The shape generalizes: any output-name
    change — a renamed leg, a leg dropped from the manifest, `split`
    toggled — strands the previous generation in `dist/`, chunks and
    manifest included. Candidate answers, for the lane to weigh: sweep
    what the build itself once wrote (scoped by a recorded emission
    manifest, so user files in `dist/` are never touched), or warn when
    an emission's sibling with a retired name or extension survives.
    Record: this entry.

## G. Macros & const

2. **Const-eval tail** (S–M)
   STATUS: OPEN (remainder is deferred-with-question, const-eval.md §8)
   Remainder, each deferred-with-question in §8: expression-level const
   spans (needs per-node provenance or a spanned IR), cross-analysis
   memoization (cache-key question; measured 7–9% of warm analysis — of
   direct interest to §M's perf arc), a const budget knob. Liveness-tied
   emission stays A7-entangled. History: backlog-2026-07-18.md §G item 2.

## I. Collections

2. **Fixed-arrays tail** (M; fixed-arrays.md §7)
   STATUS: OPEN (blocked: const-generics design — what `const N` means)
   Const-named / const-generic lengths (`[u8; SIZE]`, `<const N>`):
   proposal first (the constraint form, the staging fork — const-eval is
   post-analysis, lengths are needed mid-fixpoint). Then `List` ↔
   `[T; n]` conversions, slicing (wants a range type), generic
   `[T; N].len() → N`. History: backlog-2026-07-18.md §I item 2.

3. **Iterator adapters — the remainder** (S–M)
   STATUS: OPEN (remaining: S6/Iterable under B4)
   The arc SHIPPED 2026-08-06; §4 option (ii) REFUSED by owner ruling.
   Live remainder: S6/`Iterable` waits on B4 (trait-typed-value
   dispatch). Record: iterator-adapters.md §11. History:
   backlog-2026-07-18.md §I item 3.

## J. Concurrency

4. **Free-spawn lint** (S once unblocked)
   STATUS: OPEN (blocked: Tier 2 counted closure environments)
   The rule ("a spawn happens inside a `nursery` extent or an
   `OwnedNursery.enter` — anything else is a lint") cannot ship while
   std's three legitimate free spawns remain (Draft.commit, the RPC SSE
   pump, streaming `on_open`); they become ownable with §10's counted
   captures. The lint ships the same day they migrate, zero baked-in
   exceptions. History: backlog-2026-07-18.md §J item 4.

5. **Async recorded opens — the deferred pair** (S each)
   STATUS: OPEN (deferred: demand-gated)
   Live remainder: per-task cancel handles (resolved-for-delays by
   `std::time::Timer` 2026-07-28; handles stay deferred — no field case
   has asked for cancelling a computation, only a delay); the free-spawn
   lint rides J4. Everything else in the entry shipped. History:
   backlog-2026-07-18.md §J item 5.

## K. Web presence (site, playground, docs delivery) — NEW SECTION

The website, playground, and docs repos had no tracker home; that gap is
part of why planning fragmented. Spans `vilan-website` and
`vilan-lang.github.io`; compiler-repo work stays in §A–§J.

5. **The design language — adopt** (M–L; owner's items 3 + 11)
   STATUS: OPEN (RATIFIED 2026-08-18; SLICE 1 SHIPPED 2026-08-18 — web-tokens → website@561dcff; SLICE 2 SHIPPED 2026-08-18 — web-slice2 8c98bbc → website@6e549d2, deployed, with K9 (dropped on evidence) and K10 (editor theme reads tokens via CSS vars); owner on merge: "could use some refinement, but definitely moving in the right direction" — a refinement pass rides slice 3 or its own item once the owner names the specifics; slice 3 = the docs, with K6 — its design now lands in docs-port.md
   §3.1 S2–S3 (mdBook is token-driven: 42 CSS custom properties per theme
   in one `variables.css` override, and it already ships a light/dark
   picker); K6 RULED 2026-08-19 — SLICE 3 SHIPPED 2026-08-19, both halves: the book (k6-book → next 0eaa38c0: `variables.css` role tokens on `html.light`/`html.navy`, design-language.md §2.5 the light palette; live at the v0.35.0 fold) and the site (web-chrome + web-art-light → website@cb3752a, deployed: every token carries both values behind `prefers-color-scheme`, the art re-lit onto the roles, `shadow`/`art-error` tokens; owner: "Approved"). What stays open under K5: the refinement pass the owner named at slice 2 (specifics pending), and K10's one-token-source generation now that three mirrors exist)
   design-language.md is ratified: kolt's `visual-overhaul-2` role
   tokens (`up`/`down`/`stroke`/`primary`, verbatim) carrying the brand
   palette, tool surfaces fully utilitarian, the hero fenced as the one
   indulgence, CommitMono V143 with the owner's feature settings (§2.3),
   light theme with K6, editor stays CodeMirror 6. Slices: **(1)** the
   token system in `theme.vl` + site chrome (masthead, page, footer)
   restyled onto it + CommitMono self-hosted for code blocks + K1's nav
   link; **(2)** the playground page + editor onto the tool register,
   with K10 (generated editor theme) and K9; **(3)** the docs, riding
   K6. Every slice: before/after screenshots for the owner's review
   BEFORE merge — the website deploys on every push to `main`.

8. **Website features & small visual upgrades** (S–M each; owner's item 11)
   STATUS: OPEN (umbrella — refine into concrete items under K5's ratified language)

13. **NEW — the docs on the vilan framework, the port proper — behind its markdown prerequisite** (L; filed by the K6 ruling 2026-08-19)
    STATUS: OPEN (STEP 1 SHIPPED 2026-08-25 — std::markdown built strict per the ruled markdown.md (fa742f146 merged 7b9b55ce): 456/456 mdBook-exact anchors with a real-build golden, 0.9 ms/page, `Items` carries BLOCK bodies (the build's correction, OWNER NOD 2026-08-25; golden regen rule also nodded); NEXT: the const input channel + fuel, then the router/docs-app rung; STEP 3 DONE 2026-08-20 — the site took rung 2 whole, website@6036e21, record fullstack-dx.md §16.11: pixel-identical both pages both schemes, the shells deleted, the hatch census is the ladder's fit report, §15.2's declined helpers all found customers → E79)
    The owner's literal item 10 ("transitioning the docs to the vilan
    framework"), filed as its own item so it stays reachable while K6
    ships option B. docs-port.md §2.1 proved the port is *unavailable*
    today, not merely expensive: a `const` cannot read a file nor return a
    `View`, and the 1M fuel budget is exhausted by a char-scan of a page
    the size of the book's largest. §3.3 gives the honest order: (1) a
    markdown story — a `std::markdown` (or package) parser producing a
    plain-data AST, or a `[build] run` pre-step emitting generated `.vl`
    from `.md` (no compiler change; the cheaper proof); (2) a const input
    channel, only if the parser is to run at compile time, with the fuel
    question answered first; (3) a router and rung-2 adoption on the site
    (`Document::of` + `serve_build` + `split = true`), which fullstack-dx.md
    §16.2 notes the compiler repo cannot yet demonstrate either (E65).
    Each step is independently valuable — the test of a real prerequisite.
    **L10's paper (std-shape.md, 2026-08-20) names `std::markdown` as the
    first candidate official package — its §6 Q4 asks whether the markdown
    story should be built package-shaped from day one.**
    The 32 LSP deep links and 417 in-book links pin mdBook's anchor
    algorithm as a compatibility surface (§4 Q3) that any renderer must
    reproduce. Record: docs-port.md §2.1, §3.3, §4 Q1.

## L. Release engineering & beta — NEW SECTION

The alpha→beta transition. The *contract* is RATIFIED (process.md §5,
2026-08-07: three promises, no spec freeze, the four-condition trigger,
the v0.40.0 jump); beta.md (RATIFIED 2026-08-18) is the execution
charter — its status block also records the owner's "should we defer
beta?" and the answer: **the trigger already defers the declaration**
(none of the four conditions hold today; (b) earliest 2026-08-29; (c)
waits on B73; (d) on D5), so the pre-switch items below proceed at
ordinary priority as low-regret hygiene, and nothing beta-branded ships
publicly until the trigger fires. The alpha framing in README/CHANGELOG
is **correct until the switch commit** — do not "fix" it as rot.
(L1 — ratify beta.md — CLOSED 2026-08-18; the archive's first entry.)

3. **std tier sweep** (M)
   STATUS: OPEN (table DRAFTED 2026-08-20, beta.md §5; ruling DEFERRED 2026-08-20 by the owner — "the answers to those questions might change from now until we officially enter beta" — re-present §5.1 with the beta switch's pre-work, not before; the docs page lands at ratification)
   The census: 56 public modules (54 std + 2 macro_std; canvas has no
   module yet — §4 Q4's Tier 3 binds when it lands). Proposed: 32 Tier 1,
   23 Tier 2 (with promote-on-quiet clocks and holds where an open item
   gates), 1 Tier 3 (`into`, B127's deletion question). §5.1's arguable
   rows: iterator straight to Tier 1; operators under B11's open item vs
   an item-level carve; into at Tier 3; process/dom at Tier 1 against
   their Tier-2 directories; wire's tier vs §5.2(3)'s unconditional
   Breaking pricing.
   Enumerate the public std surface, propose the Tier 1/2/3 table
   (beta.md §3.2), owner rules, docs publish it.

8. **Contribution scaffolding** (M)
   STATUS: OPEN (blocked: D5 — deferred with it, process.md §9.2)
   CONTRIBUTING.md, SECURITY.md, CODEOWNERS, issue/PR templates,
   private vulnerability reporting. Revisit when D5's session happens;
   scaffolding for an audience arrives with the audience.

13. **NEW — a mechanical re-key scan over the whole ledger** (S; diag-anchors Q4, RULED file 2026-08-24)
    STATUS: OPEN — RULED, ready to build
    Row 135's key had drifted outside batch 8's re-key list (caught by hand).
    Re-run batch 8's mechanical scan over every row: site/head columns against
    the live source; drifted keys re-keyed in place, dead rows flagged. Also
    parks the held-target closure head as a REWORD candidate with the
    process-layer batch (closure-ret-family Q1, RULED park 2026-08-24).
    Record: the ledger's conventions paragraph.

## M. Performance & footprint — NEW SECTION

Owner's items 7 (perf) and 8 (leaks). The 2026-08-18 survey found the
seams already cut: the four pipeline phases are independently callable
library entry points (`parsing::parse` → `analyzer::analyze` →
`post_analysis_passes` → `transformer::transform`, the same seam
`VILAN_PHASE_TIMING` marks), a purpose-built per-site leak harness
exists (`leak_tally` + vilan-lsp's `leak_measurement` module), and the
suite's liveness bounds already use measured-reference thresholds
(`support/mod.rs`'s `reference_compile()`), never fixed seconds.
Corpora measured: todo 119 lines (smoke only), kolt 943, website 2,996,
std 15,024 (the cold-compile stand-in).

## N. Hygiene & rot — NEW SECTION

Owner's items 1–2 (repo refactoring, rot, consolidation, README;
rotted/poorly-written code). Seeded by the 2026-08-18 rot survey (all
four repos, read-only). What the survey found and this order already
fixed in the same sweep: the proposal index's stale/missing rows,
AGENTS.md's dead arc pointer, roadmap.md routing readers to the dead
backlog (banners landed with the re-baseline). What it cleared as
NOT rot: `about.hbs`/`about.toml` (live, `cargo about` consumers),
npm's `0.0.0-placeholder` and the homebrew formula's 0.14.0 seed pin
(both deliberate and test-documented), the bindgen module's 63
`TODO(bindgen)` hits (an emission vocabulary, not debt), and the
README/CHANGELOG alpha framing (correct until the beta switch — §L).

8. **Pages repo housekeeping** (S–M umbrella)
   STATUS: OPEN (narrowed 2026-08-20 — the three orphaned brand files are deleted and the 404 shim's sunset is PROPOSED in the pages README ("at the beta switch", proposed-not-ruled — the one open half); N12's README shipped 2026-08-19; K12/N13 closed 2026-08-20)
   The local checkout is 41 commits behind its origin (refresh before
   trusting any file-presence claim there — the survey's "no sitemap"
   class of findings were checkout staleness, not site defects). Then:
   no README distinguishing bot-generated files (`docs/`, `index.html`,
   `client.*`, `playground/` — pushed by two different workflows) from
   hand-owned (`assets/`); three orphaned brand files nothing
   references (`icon-512.png`, `light_lockup.png`,
   `dark_wordmark_flat.svg` — delete); the pre-v0.15 `404.html`
   deep-link shim deserves a recorded sunset condition. (The
   `book.toml` leak and mdBook fonts rode K6 — both closed 2026-08-19;
   the README is N12, shipped the same day, and names `chrome/` as the
   new bot-owned prefix; the stale-checkout note is moot — pulled
   2026-08-19; wasm retention is K11.)

16. **NEW — the recurring codebase audit** (RECURRING; the owner's standing ask, filed 2026-08-25)
    STATUS: RECURRING — one audit lane every other work order, rotating
    focus; first run due Order 11. Track here: last run NONE / next due
    Order 11 (update this line each run).
    A standing audit over all four repos (vilan primary; website,
    proposals, pages secondary), SURVEY-FIRST like the 2026-08-18 rot
    survey: findings are FILED as tracker items with evidence, never fixed
    inline — except S-sized tidies the lane can land with pins. Each run
    picks 2–3 dimensions from the rotation and states which; the report
    grades what it swept so coverage is honest across runs. The rotation:
    - **Security**: `cargo audit`/dependency advisories; the `unsafe`
      inventory (each block's SAFETY comment against reality — the
      BASE_CACHE transmute class); injection/escaping surfaces (the
      website's served HTML, the playground share codec, the HMR
      endpoints); secrets/tokens in tracked files; the release pipeline's
      supply chain (pinned actions, checksum gates).
    - **Tidy & structure**: directory/module layout drift, files that
      outgrew their name, orphaned assets/fixtures, stale scratch or
      generated files tracked by mistake.
    - **Dead code**: unreferenced items the compiler cannot see (feature-
      gated, test-only helpers gone stale, cfg'd-out paths), dead exports,
      the `#[cfg_attr(not(test), allow(dead_code))]` inventory re-argued.
    - **Error handling**: `unwrap`/`expect`/`panic!` in non-test code
      audited against the panic-fence and Result discipline; swallowed
      errors; error messages that lost their context.
    - **Diagnostics**: a ledger sweep (with L13's mechanical re-key),
      heads that drifted from house rules, missing C3 notes/steers on
      newer refusals.
    - **Debugging**: VILAN_PHASE_TIMING/debug-dump coverage of newer
      passes; leak_tally site coverage; whether the perf baseline still
      reproduces.
    - **Tests**: vacuous pins (plant-audit a sample), #[ignore]d pins
      whose reason expired, per-case gaps on newer features, goldens
      whose regeneration story rotted, suite wall-time creep.
    Each run ends by updating this item's last-run/next-due line and
    filing its findings; a dimension with zero findings says so
    explicitly (absence of evidence recorded, not implied).
