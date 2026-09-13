# Order 34 — the foundations order (drafted 2026-09-13; NOT GO), off vilan next @e4d192e3

**Status: DRAFT.** Nothing has landed on `next` since Order 33 sealed (e4d192e3 is the tip;
toolchain at that sha in both locations). Ledger next id 426. Tracker 103 open.

The owner's focus, read from 2026-09-12: two DESIGNS filed after a day of writing kolt against
the shipped surface — B318 (visibility and the import surface: default-private, `export *;`,
`export(PATH)`, the `#` reach, the exposure warning, `export mod` + `::*`, the impl selectors
`(impl T)`/`_`/`only`) and A95 (`Style`'s condition model: conditions as typed values, rules
composed by `.add`/`.on`, canonicalised by the compiler) — both RULED to the paper before any
lane ("We'll begin actual work tomorrow"); the tooling that bit while writing kolt (E167 the
css-block converter never fires; E168/E169 Organize Imports over-prunes and over-keeps; A96 HMR
throws a websocket error per remote source); one spec bug the prelude sketch exposed (B317);
two miscompiles from Order 33's finds (B310, B311); the language server's memory (M63/M64,
the 4.13 GB field reading); and the re-ruling A85 waits on (B309). Seven lanes go on no
ruling; two (paper lanes) go on the rulings already given; one (slots-34) goes only with R3.

## Rulings at GO (owner) — the ones that change what a lane BUILDS
- **R1 — B318's paper scope (paper-visibility-34).** Rec: PAPER ONLY this order; B317 (the
  associated-function import, a spec-conformance bug independent of the design) BUILDS now in
  lang-34. The paper answers B318's open (a)–(i) with recommendations and lays the slices; the
  build is Order 35's.
- **R2 — A95's paper scope, and the two fences beside it (paper-style-34).** Rec: paper only
  for the redesign; B311's MISCOMPILE gets its fence NOW (a `pseudo` name containing `:` is
  refused at const time when the call is WRAPPED by another condition — the miscompiling case;
  the unwrapped raw token kolt writes at styles.vl:48–49/:62–86 survives, one ledger row);
  B308 is NOT built separately (A95 closes it structurally — the retraction design is
  recorded, not built); styles-33's open Q (4) — std const-time `panic` refusals carry ledger
  rows — rec KEEP (they are user-facing texts to hold). A93's fence is built by this lane
  (rec) and is BREAKING for kolt views.vl:165 — see "Owner actions at GO".
- **R3 — A85's re-ruling (slots-34 go/no-go).** positional-slots.md §10 asks: (a) build B309
  first, then A85 as ruled (rec); (b) ship with the ownership divergence documented (rec
  against); (c) a `Render` trait per body (works, verbose). B309's shape: (1) the `context`
  clause IN `Type::Closure` (rec — the clause IS part of the closure's type; every `_ =>` over
  `Type` audited per AGENTS.md) or (2) a parallel `field_contexts` side-band (recreates the
  parameter side-band). Rec: RULE (a)+(1) now; slots-34 builds B309 this order (L), A85 + A91
  follow in Order 35 on the landed clause. Without R3, slots-34 does not open.
- **R4 — the language server's memory (dx-34).** M63 retention policy — rec: keep the
  `Program` for the focused document and the N=2 most recently focused, the rest drop to their
  editor tables and re-analyse on refocus (M58's warm path, sub-second); M64 — rec: `libc`
  promoted to a normal dependency of vilan-lsp, `malloc_trim(0)` after a document close and an
  analysis drop, Linux-gated, no-op elsewhere. Both are one-word rulings; the lane builds
  whichever are ruled and measures the other.
- **R5 — B316's arm (solver-34).** `reconcile_type(Trait, Concrete)`: rec (1) the universal
  reading — accept when the concrete implements the trait — which makes B306's backstop
  buildable later and turns the 18 measured programs into the pin set. Unruled → solver-34
  skips B316 and builds the rest.
- **R6 — two module/memory rulings (lang-34).** A67: rec the AMBIGUITY ERROR when `a.vl`
  declares `b` and `a/b.vl` exists (one rule for both collisions). B274: rec the COPY at a
  `&mut self` receiver on a temporary `read()` (what the five doc sites already promise).
- **R7 — E163's CI half (tm-34).** The devDependencies are RULED added (Order 33); nothing in
  ci.yml's test job creates `editors/vscode/node_modules`, so the scope pins cannot run in CI.
  Rec: add `npm ci --prefix editors/vscode` to the test job (~1 s warm, +1 MB, 0 advisories)
  and land the scope pins; E164's two fixes ride the same pins.
- **R8 — A92/A79 CLOSE at GO (integrator).** Both landed in rpc-33 (d868feb8, 74018c52) and
  the sweep left them open for rpc-33's Qs: (1) the `?` surface marker for the `Option` form —
  rec keep (built); (2) `Absent` retries at the next 0→1 lease like `Failed` — rec keep
  (built); (3) `Memo`'s home `std::memo` — rec keep. Close both with as-built lines.
- **R9 — rpc-33's three unfiled finds (file at GO).** F1 (B): a keyed handle's KEY is not
  Wire-checked in the method's own vocabulary (`KeyedCell<NotWire, T>` passes the `[rpc]`
  return check and fails inside generated code) — rpc-34 builds it (one row). F2 (M): every
  `SignalCell` pays `fresh_id()` for `.id` — a lazily-stamped identity intrinsic; filed, not
  built. F3 (A, design): hold-counting vs remote-sources §3 (a raw client asking twice and
  releasing once holds its channel open) — filed, not built.
- **R10 — N67's two one-liners (hygiene-34).** `dist/.build-hooks.json` — rec: NOT a cache (a
  note in build-hooks §3.3, no move); build-hooks Q5 — rec: rewritten as overtaken by A65.
- Record-only defaults (written as built at the sweep unless the owner objects): M62's six
  narrow-width methods NOT built (measure a frame-heavy exhibit first); K14 (playground
  prelude) not this order (web presence); B298 stays behind trait-typed-fields Q3; A87
  `Owner::release` not built; the M19 tranche (M55/M56/M57), M36, M54 and E121 not this order
  — the memory that bites today is M63/M64; A94 (fragment flatten) not built; B149 not this
  order; A76/A77/A81 (the reverse direction v2) not this order.

## Owner actions at GO
- **kolt views.vl:165** — `child_relation("not([hidden])", ..)` → `attribute("hidden", None,
  not(style().flex_col()))` (A93's fence is breaking for that one site; the fence lands only
  after the site moves — the owner's edit, or mine at the owner's word).
- kolt's uncommitted model.vl/styles.vl state is the owner's to commit; lanes read kolt
  READ-ONLY as always.

## Mechanics (every lane)
- Worktree `vilan/.claude/worktrees/<lane>` branched from `origin/next` (e4d192e3); NEVER
  touch the main checkout; NEVER `git stash`; kill only PIDs you recorded; kolt
  (`~/code/kolt`) is READ-ONLY — read it ONCE into your scratch and work from the copy.
- Lanes NEVER PUSH. The integrator pushes each lane branch at merge time.
- One commit per item, message = the CHANGELOG entry's first sentence; CHANGELOG entry under
  the right family with its marker (`<!-- family: breaking|miscompile|fix|feature|
  performance|tooling|diagnostics -->`); the parity gate is `--test release_scripts`. A
  refusal that newly fires on std, `examples/`, the corpus, the docs or kolt carries a
  `breaking` note naming the program.
- Diagnostics: a new message is a ledger row written `NEW` in
  `crates/vilan-cli/tests/diagnostics-ledger.tsv` (the integrator numbers; next id 426 —
  NEVER write a literal id), an edited text is a row edit; every lane that adds or edits a row
  runs `--test diagnostics_ledger`; a message whose FIRING changes means `-p vilan-lsp` too.
- A named parser rule constant needs TWO edits: `RULE_STATEMENT_SITES` AND N65's
  `CURATED_RULE_STATEMENTS` (editor-33's fix at merge was this omission).
- PIN LOCATION: attribute and type refusals in vilan-core `tests/inference/<module>.rs`
  (`main.rs` is `mod` declarations only); wire behaviour in vilan-cli `service_layer.rs`;
  reactive in `reactive_lifetimes.rs`/`reactive_channels.rs`; rows/children in `ui_rows.rs`;
  styling `style_when.rs`/`style_chain_order.rs`/`hmr_css_matrix.rs`; editor in
  `crates/vilan-ide`/`crates/vilan-lsp` unit tests; the HMR e2e per hmr.md's real-event path.
- Shared test files: ADD whole new `fn`s. An EXISTING fn you must edit is named in the report
  (the fold takes `--allow-edit`). A program CONST edited beside its pin is named too — the
  fold-by-name carries NEW consts only; the integrator runs `merge_items_by_name.py` for an
  edited one.
- The split emission golden (`tests/split/golden`), the corpus `.mjs` goldens and the markdown
  golden move on ANY change to what std::reactive/std::ui emit; regenerate per the ritual over
  YOUR tree and say so; the integrator regenerates once more over the merged tree.
- Tests: `cargo nextest run -p <crate> --test <name>` targeted — and `-p A -p B --test X`
  applies `--test X` to EVERY package (run the packages separately or one silently runs
  nothing); verify names with `ls crates/<crate>/tests/`; the whole `-p vilan-core` run is the
  merge gate, but `-p vilan-core -E 'test(every_std_module_is_clean_under_full_scan)'` IS
  yours (std edits). Lib-only `cargo build` while nextest runs. Clippy `--all-targets -D
  warnings`, `cargo fmt --all --check`, `vilan fmt` over any `.vl` touched, before you finish.
- Scratch: `scratchpad/<lane>/`; the scratchpad is shared — read nothing outside yours.
- Heredocs in their OWN shell call. A hand-composed generated block is brace-counted and
  smoke-compiled (`--test examples`) before the gates.
- No SendMessage: every interaction is in this brief; a question you cannot answer from source
  is an OPEN Q in the report and you build your recommendation.
- Perf claims: CPU time (`getrusage`) or callgrind Ir + loadavg, never wall.
- Paper lanes write into the proposals checkout (`~/code/vilan-lang/proposals/projects/vilan/
  proposal/<name>.md`) — the integrator commits; they never touch a vilan worktree except to
  PROBE (a scratch package under `scratchpad/<lane>/`, the installed `vilan`).
- Report (final message): per item — commit sha, what landed, the pins (names), numbers;
  FINDS as candidate items with evidence; OPEN Qs; anything unfinished and why; corrections
  to this brief. Model: Opus.

## Lane paper-visibility-34 — B318's paper (`proposal/visibility.md`), no build
The design is the owner's, RULED in the item; the paper's job is to make it buildable and to
find what the rulings did not decide. Read B318 (all of it), B317, E168/E169, prelude.md (§7–
§9, §11, §14), names.md §4 (the spec's one-namespace rule at §4.6), the analyzer's
`collect_importables`/`resolve_import`/`import_leaf_is_used` (document.rs) and `candidates_of`/
`impl_members_for_bound` (B254/B258's region), the parser's `parse_export`/`pub` curated
rule (parsing.rs:246–260).
1. **The model, stated once.** Visibility = a bit on an importable; `export` sets it, `export
   *;` sets every item of the module, `export(in PATH)` narrows to a scope subtree (`mod`,
   `pkg`, a path); access is never gated — the `#` reach binds a private item; visibility
   gates COMPLETION, the add-import quickfix candidates and the "import it first" steer.
2. **Grammar, PROBED.** Each new form written into a scratch package and tried against the
   installed parser to find what collides: `export *;` (today `*` after `export` is what?),
   `export(in pkg) fun`, `import a::{ #hidden }`, `import a::b only;` (`only` as a contextual
   keyword — does an item named `only` exist anywhere in std/kolt?), `{ (impl List<i32>) }`,
   `{ (impl List<_>)::{ first, last } }`, `export mod m { }` + `import pkg::a::m::*`. Record
   each as parses/collides/needs a rule. `#` is free lexically (the css lexer refuses `#333`
   inside a block only) — confirm.
3. **The per-importer method namespace (the crux).** Today names.md §4.6: one namespace per
   type, two impls declaring one name refused at DECLARATION, globally. Under selectors the
   check moves to the importer: define it (refused at the import? at the call? both with one
   message), say what `candidates_of`/`impl_members_for_bound` (name-keyed, global — the
   B254/B258 silence class) become (scope-filtered by the file's selector set), how method
   lookup consults the selector set at a call (unify the receiver's type against each
   selector; `(impl List<i32>)` never serves a `List<str>` in that file), what the reference
   index and the `impl` steers do, and B318's open (i): the same-module pair.
4. **The exposure warning.** Reach = signature positions (value type, params, returns,
   exported struct fields, enum payloads, trait bounds, generic arguments); the wording is
   RULED — fix the agreement ("is unable"/"cannot"); the fix edits `S` wherever it lives; a
   dependency's `S` gets no fix and a sentence. Where it lives in the analyzer (after
   declaration hoisting, before bodies), one row.
5. **The plain-import-of-a-private-item warning** (recommended, not ruled): two fixes; this is
   what makes the default flip non-breaking. State the alternative (an error) and its cost.
6. **Migration census.** Count, per package, the cross-file imports whose target is unexported
   today: std (364 unexported top-level items; how many are imported by another std file?),
   kolt, the website, `examples/`, the templates, the docs' snippets. The `export *;` codemod
   for apps; std curates. Numbers in a table.
7. **Tooling.** Completion (after `impl ` in an import: the module's impl subjects; after
   `)::`: the block's methods), Organize Imports under selectors (prune per selector; E168's
   rewrite becomes `import a::{ (impl Style) };`), the formatter's canonical spelling and
   sort position of selectors in a brace set (rec: after the names, by type text), `#`
   kept as written.
8. **Rollout.** Rec: one release warning-only (the flip is a warning; `export *;` silences a
   module), then the error; std's own posture (prelude.md §10's precedent).
9. **Slices** for Order 35: visibility bit + `export` forms + warnings; `#` + `only` +
   selectors; per-importer namespace; tooling; docs (names.md visibility section, §4.6
   rewrite, tour/projects.md, prelude.md, the editor page); the estate sweep.
10. **Open questions** — every one of B318's (a)–(i) answered with a recommendation, plus what
    the probes found. Sizing per slice. Model: Opus. No vilan edits.

## Lane paper-style-34 — A95's paper (`proposal/style-conditions.md`) + B311's fence + A93's fence
Read A95 (all), A89's as-built (ui-styling §0bis.6, css-block §5.3), B308, B311, A93, A36,
style.vl's condition machinery (`rule`, `pseudo`, `attribute`, `within`, `not`, the slot key
`media:condition:property`, `class_list`), the formatter's `STYLE_CONDITION_METHODS`/
`ConditionAxis` sort, css-block §7.1's completion tables, and kolt's `new_button_style`
(styles.vl:62–86) — the exhibit.
1. **The paper.** (a) The model: a `Style` = base declarations + rules; a rule = a condition
   SET + declarations; conditions are typed values (`Pseudo`, `Attribute`, `Relation`,
   `Media`) with `.not()`, `attribute(name)` presence and `.eq(value)`; `style().on(..)`
   attaches a set; `.add(rule)` nests (conditions intersect). (b) Canonicalisation: the slot
   order (media, relation, attributes, pseudos), duplicate merge, the one refusal
   (contradiction), pseudo order within the slot (written vs a table — decide). (c) The band:
   ui-styling §0bis's specificity story with the outermost kind as the band — show it survives.
   (d) The block spelling: `.on(hover(), active().not()) { … }`, `.hover { }` as sugar,
   `.add {}` with no head = flatten; no bare selectors. (e) What closes: B308 (rules are
   values until application — no intermediate emission), B311 (no condition is a string),
   A89's marker, A93 (`children()`/`divide()` values; `child_relation` deleted). (f) What
   stays: `hover(inner)` sugar (kept or deleted at migration — decide), `when(condition,
   delta)` for runtime, `Declarations`/`rule`/`declare`, `raw`, the split gate. (g) Migration
   census — the combinator call sites as of e4d192e3: std 27 in 6 files, kolt 47 in 7, docs 60
   in 7, the test corpus 42 in 5, cli tests 10, core tests 157 in 11; refine per method and
   say what E167's converter can rewrite mechanically. (h) Re-measure plan: css-block §15.3's
   compact-styling numbers after. (i) Slices for Order 35 and sizing. Owner's sketch
   divergences (`.pseudo(pseudo(..))` → `.on(..)`; `.set(prop, Length)` = S1's typed raw)
   recorded.
2. **B311 fence (BUILD).** `pseudo`'s name check gains: a `:` in the name when the call is
   WRAPPED by another condition is a const-time refusal (curated, one row `NEW`) naming the
   unwrapped raw form as the working spelling and A95's paper as the real fix; the unwrapped
   raw token keeps emitting verbatim (kolt's styles.vl uses it four times — a breaking note if
   any std/docs/corpus program trips). Pins: the wrapped refusal, the unwrapped control, the
   miscompile's own exhibit now refused.
3. **A93 fence (BUILD, lands only after the owner's kolt edit).** `child_relation`'s token
   checked against `>*`/`>*+*` at const time (one row); pins: the refusal and the two
   controls. The report says whether kolt's site still uses the hatch at your read.
Sizing: paper L, fences S+S. Model: Opus. std edits: style.vl only.

## Lane solver-34 — TOP: B310 (miscompile), B315, B302, B279; B316 with R5
1. **B310 — `Map::entries()` generic tuple layout (MISCOMPILE).** The flattening decision is
   made at the site that builds the tuple from the static types it sees; inside a generic
   body the element types are parameters so the tuple keeps its boxed layout, and the
   instantiated caller assumes the flat one. Build the item's first option: re-lay out by the
   INSTANTIATED layout at the call boundary (a generic function's tuple-of-parameters return is
   re-shaped when the argument is known — `freshen_list_element_slots`'s neighbourhood is the
   model); pins: the `Map<K, (A, B)>` exhibit through `entries()`, a nested tuple, a tuple of
   a parameter and a concrete, and the `.mjs` corpus golden if it moves. `miscompile` family.
2. **B315 — overlapping blankets unranked.** Rec (the item's): REFUSE two blankets whose bounds
   overlap (`instantiation_agrees` both ways = overlap), one row; pin the hypothetical pair with
   a local trait and a non-overlapping control.
3. **B302 — `render_type` path arm.** `a::b::C<..>` rendered as written; sweep callers for a
   message showing `_` for a path; one pin (the `[rpc]` return exhibit).
4. **B279 — the structural guard for B258's class.** Assert every strict node has a refined
   coverage caller (or is run-closure/declared) and REFUSE rather than emit; enumerate
   `candidates_of` consumers, narrow or justify each in a doc comment; a pin per consumer.
   (paper-visibility-34 will READ this region — leave doc comments that say what each list
   is keyed by.)
5. **B316 (only with R5).** The arm accepts when the concrete implements the trait; the 18
   programs solver-33 measured become pins (`inference/traits.rs`); the B306 backstop stays
   unbuilt (its own item later).
Sizing M. Model: Opus.

## Lane lang-34 — B317, A80, B278, A67 (R6), B274 (R6)
1. **B317 — associated functions importable/usable under a bare name.** The importable row
   for a struct/enum gains the self-less functions of its `impl` blocks keyed by the impl's
   declaring module; `use` lifts its fence from "module or enum" to "module, enum or struct";
   the free name binds the function's own entity (rename/go-to-definition through the alias);
   a `self` method under either form: one curated row ("`Length::text` takes `self` — a method
   is called on a value, not imported"). Pins per the item (direct, brace set with `as`,
   `use`, a re-export consumed by a second file — the prelude shape, an extension impl's
   static, the `self` refusal, enum variants unchanged, one LSP rename pin). Docs: names.md
   :98–99 gains `import` beside `use`; prelude.md's custom-prelude example gains one line.
2. **A80 — mutable pattern binding.** The sugar `Some(let mut x)` (rec) — one grammar rule
   (+ `RULE_STATEMENT_SITES` + `CURATED_RULE_STATEMENTS`), the binder is `mut` in the arm's
   scope; pins: the `cell.update(|&mut held| match held { Some(let mut list) => list.push(..)
   })` exhibit, `mut let` still refused with the steer naming the form.
3. **B278 — an i-string hole cannot contain an escaped quote.** `i"{x.get(\"k\")}"` lexes;
   pin it and the nested-brace control.
4. **A67 (R6) — the ambiguity error** when `a.vl` declares `b` and `a/b.vl` exists; one row;
   `longest_module_prefix`'s doc and names.md §4.2 updated; pin the pair and the `lib.vl`
   control.
5. **B274 (R6) — copy at a `&mut self` receiver on a temporary read.** Add the receiver to
   `consider`'s positions; pin the probe (`log.read().push(9)` leaves the cell at 1); the five
   doc sites stay as written (they were right).
Sizing M. Model: Opus. Regions: parsing.rs (A80, B278), analyzer import resolution (B317,
A67), rule 1 (B274) — solver-34 owns method resolution; do not cross.

## Lane editor-34 — E168+E169 (one predicate), E167, E165, M65, B314, E155
1. **E168 + E169 — Organize Imports.** In `Document::import_leaf_is_used` (document.rs): (a)
   E169 — for a MODULE leaf, skip occurrences whose definition is bound by another import leaf
   of this file (build the set from `type_references` at each leaf span, aliases included);
   what remains is what the module import alone brings. (b) E168 — in the organizer, a
   statement whose every leaf is unused but whose module's file declares something this file
   resolves (rule (2)'s test applied to the statement's module) is REWRITTEN to `import
   <module>;` instead of deleted; the fade stays on the leaf. Pins per both items (the s1c/s2/
   s3/s4 shapes: `import pkg::a::b;` + `const { style().select_off() }` → rewrite; module +
   named leaf with only the leaf used → the module import prunes; module alone unused →
   prunes; module + impl use → kept); the fmt/organize agreement pin extended.
2. **E167 — the css-block converter fires on real chains.** Seed: any path whose last segment
   is `style` called with no arguments; typed links: the INLINER over std's parsed style.vl
   (a shorthand body is a `with_length`/`with_color`/`raw` chain — substitute the argument
   text into holes; a body that is not such a chain has no spelling); values through
   `render_block_value`'s rule; the FIRST unconvertible link splits the chain — everything
   before becomes the block, the rest a postfix chain on it (`css { … }.select_off()` parses
   today). Pins: the `style::style()` seed; kolt's `new_button_style` shape converts and the
   block's `class_list()` equals the chain's; a user extension splits; all-unconvertible
   offers nothing; comments still refuse. Docs: the editor page's refactor row.
3. **E165 — blank-line completion.** `scope_at` (vilan-ide) lands on the nearest enclosing
   BODY scope for an empty line, not the nearest entity before the offset; pin `fun main() {
   let start = 1; ▮ }` offers `start`.
4. **M65 — `CompletionIndex::build`'s `source_of` hoist** (same file as 3): the M27/M58 hoist;
   pin answer-identity; the warm profile before/after (Ir).
5. **B314 — `pkg`/`Self` index rows.** `pkg` is not a reference to the package root, `Self`
   not to the impl subject's declaration — drop or retarget the rows; E158's invariant pin
   widened.
6. **E155 — an element argument is atomic to the chain-break rule** (formatter.rs): break
   one link per line before breaking inside an element; pin the lucide shape.
Sizing M–L. Model: Opus. dx-34 shares document.rs — you own the quickfix/organizer/css
regions; dx-34 owns the document lifecycle; name every edited fn.

## Lane tm-34 — E163's CI half (R7) + E164
1. **E163.** `npm ci --prefix editors/vscode` in ci.yml's test job (and wherever the scope
   pins run); the `tokenize.js` helper under `crates/vilan-cli/tests/support/` loading the
   grammar with the wasm onig; E161's five regex pins rewritten as SCOPE assertions over the
   exhibit (`<div>` and `a < b` as controls); THIRD-PARTY-NOTICES if the notices gate reads
   devDependencies (check). Cost line in the report (warm `npm ci` seconds, lockfile delta).
2. **E164.** (1) the generics begin does not fire when `<` is followed by `/`; (2) an
   element-head begin/end (from `<tag` to `>`/`/>`, spanning lines) replaces E115's line-start
   terminator. Scope pins: `</span>` after text is a tag; `<div class="row">`'s `>` is a tag
   delimiter; `a < b` stays an operator; `List<i32>` stays generic; `grammar_sync` green.
Sizing S–M. Model: Opus. Regions: editors/vscode, ci.yml, cli grammar pins.

## Lane dx-34 — M63 (R4), M64 (R4), E166
1. **M63.** The retention policy as ruled (rec N=2): `Document` keeps its `Program` only while
   focused or among the N most recent; the others keep their editor tables (diagnostics,
   symbols, references served from the tables) and re-analyse on refocus. Pin: dx-33's
   `open_documents` instrument bounded at N × the largest document; kolt's 18 files under
   300 MB (measure with dx-33's harness; report before/after RSS and heap in-use).
2. **M64.** `libc` as a normal dependency (Linux-gated `malloc_trim(0)` after a document close
   and an analysis drop; no-op elsewhere); pin RSS after close within 1.2× of before open.
   Unruled: measure the free-list retention once more and report.
3. **E166.** The status page gains RSS, heap in-use and retained-free (`mallinfo2`, Linux) —
   the numbers E106/M63 were found with; a unit pin on the formatting.
Sizing M. Model: Opus. Regions: vilan-lsp main.rs/document.rs lifecycle, Cargo.toml.

## Lane rpc-34 — A96 (TOP), B312, B313, F1 (R9)
1. **A96 — HMR websocket errors, one per remote source.** rpc.vl:1054's teardown becomes
   `close_for_good(duplex)` (state `Closed` first, socket close, `on_terminal`); pins on the
   HMR e2e: no `transmit` on a non-OPEN socket across a swap (spy), the old duplex `Closed`
   and `dial_with_backoff` not re-entered (counter), ONE server connection after the swap, a
   `RemoteSource` minted by the new bundle resyncs (K6's pin). The mechanism was read from
   source, not driven in a browser — your pin is the confirmation; if the browser shows a
   different error, say so with the text.
2. **B312 — generated method-name collisions.** The generator refuses an `[rpc]`/
   `[client_service]` method whose name is in its own generated-member set, at the attribute,
   spanned on the method (one row); a pin per reserved name and a control.
3. **B313 — the double refusal for a suspending `async fun f(&mut self)`.** Rec: E3's check
   stands down for a method the `[rpc]` attribute already refused (the B189 stand-down set,
   fed from macros.rs); pin one report for the suspending shape, B287's alone for the
   non-suspending.
4. **F1 (filed at GO) — a keyed handle's KEY is Wire-checked in the method's vocabulary**
   (`KeyedCell<NotWire, T>` refused at the `[rpc]` return, one row, analyzer.rs ~14930).
Sizing M. Model: Opus. Regions: rpc.vl, macros.rs service expansion, service_layer.rs, the HMR
e2e.

## Lane hygiene-34 — DROPPABLE, lands FIRST: N74, N75, N76, N66, N67 (R10), N35
- N74: `css_style_import_note` deleted as N69 was (same seed change, one pin).
- N75: `mount_missing_id.rs` and `hmr_swap.rs` stubs folded into N73's consolidation.
- N76: `ROWS_THE_ENUMERATION_CANNOT_REACH` keyed by TEXT (or a stable key), so a lane's `NEW`
  row can be listed; `diagnostics_ledger` green.
- N66: the harness notes (pkg_root = the manifest's `root`) into the replay harness's doc and
  a guard that says so when the repo root is passed.
- N67 (R10): the §3.3 note and the Q5 rewrite (proposals `build-hooks.md`; the integrator
  commits).
- N35: `hmr_css_matrix` waits for the round's completion signal (the watcher narrates) or
  reads-until-parse; never contains-and-hope.
Sizing S. Model: Opus.

## Lane slots-34 — GO only with R3: B309 shape (1)
`Type::Closure` gains the context list; every `_ =>` over `Type` audited (AGENTS.md's rule);
a field, a generic argument and a return can carry `context owner_scope`; the coverage check
follows the value; a closure LITERAL written where a context-typed field is initialised is born
under the clause's extent; the four `inference/bounds.rs` wall pins (`a85_a_context_clause_*`)
flip to positive with the control that goes red. A85/A91 are NOT this lane's — Order 35's, on
the landed clause. Pins: field, generic argument, return; forward/`run`/call at a field read;
the capture-at-creation leak measured in slots-33 (positional-slots §10) now impossible by
construction. Sizing L. Model: Opus. Regions: `Type` (types.rs), context.rs, the coverage
check — solver-34 and lang-34 do not touch these.

## Ownership map (conflict avoidance)
- proposals only: paper-visibility-34 (visibility.md), paper-style-34's paper
  (style-conditions.md), hygiene-34's N67 (build-hooks.md).
- style.vl + style tests: paper-style-34 (B311, A93). No other lane edits style.vl.
- analyzer.rs: solver-34 (method resolution, `reconcile_type`, `candidates_of` consumers,
  `render_type`); lang-34 (import resolution, `collect_importables`, `use`, rule 1's
  `consider`); hygiene-34 (N74's `css_style_import_note` deletion — one site); rpc-34's F1
  (~14930, the `[rpc]` return check). Name every edited fn.
- parsing.rs: lang-34 only (A80, B278). Both rule-constant lists.
- types.rs/context.rs/coverage: slots-34 only.
- vilan-lsp: editor-34 (document.rs quickfix/organizer/css regions, references index for
  B314); dx-34 (document lifecycle, main.rs status, Cargo.toml). Merge editor-34 BEFORE dx-34.
- vilan-ide completion.rs: editor-34 (E165, M65).
- formatter.rs: editor-34 (E155's chain-break) — paper-style-34 reads `STYLE_CONDITION_METHODS`
  and edits nothing there.
- macros.rs service expansion + service_layer.rs + rpc.vl + HMR e2e: rpc-34.
- editors/vscode + ci.yml + cli grammar pins: tm-34.
- test stubs / diagnostics_ledger.rs / replay harness: hygiene-34 (lands first).
- Merge order: hygiene-34, tm-34, lang-34, solver-34, editor-34, dx-34, rpc-34, paper-style-34
  (the fences), slots-34 last; the papers are proposals commits at any time.

## At the sweep (integrator, proposals)
- Close: B310 B315 B302 B279 (+B316 if R5) · B317 A80 B278 A67 B274 · E168 E169 E167 E165
  M65 B314 E155 · E163 E164 · M63 M64 E166 · A96 B312 B313 F1 · N74 N75 N76 N66 N67 N35 ·
  B311 (the fence — the item stays open as A95's if the owner prefers the miscompile row to
  stay visible: rec CLOSE, A95 carries the design) · A93 (after kolt) · B309 (with R3).
  A92/A79 close at GO (R8). B318 and A95 stay OPEN with "PAPER LANDED — slices for Order 35"
  status lines.
- File: rpc-33's F1/F2/F3 at GO (R9); each lane's FINDS after the reports.
- Papers: visibility.md and style-conditions.md committed as the lanes land them; positional-
  slots.md §10 gains the R3 ruling; transport-rpc §9.6 the A92/A79 close.
- Goldens: split/corpus/markdown regenerated once over the merged tree when the gate says.
- Chronicle: Order 34 — cycle 52 entry at GO; MERGED and SEALED paragraphs as before.
- Toolchain: refresh BOTH locations after the seal; kolt's A93 site must have moved first.
