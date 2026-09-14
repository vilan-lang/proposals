# Order 36 — the papers' second slices, the breaking surface, and the callable bridge (drafted 2026-09-14; NOT GO; off vilan next @9b22ec36)

**Status: DRAFT.** Ten rulings below (R1–R10) each carry a recommendation; "go with the
recommendations" stamps them all. Order 35 sealed at 9b22ec36 (CI green on all eleven jobs;
toolchain at that sha in both locations; nothing has landed on `next` since). Ledger next id
464. Tracker 94 open.

The shape, read from what Order 35 left and what the owner filed since: B318's S1–S3 and A95's S1
landed with their surfaces hidden; this order turns both papers' remaining slices into the
user-visible half — the per-importer method namespace (S4, the solver's largest cost), the
condition surface (A95 S2, BREAKING for the paper's 37 sites) with its tooling and estate, and
the `export *;` estate sweep with std's curation (S6, merged LAST so it is one diff anybody can
revert). Beside them, the owner's three rulings of 2026-09-14 become code: A99 retires the six
`View` parent methods for the free slot functions; B340 makes a struct value callable and, in the
owner's framing, makes closures formally callable structs; G24 (`const let`/`const fun`) takes
its snapshot shape from that framing; A100 (`lazy`) is the ratified paper that never entered the
tracker. Two design papers are commissioned (C14 the cell representation, F1 native apps), the
editor gets the Organize Imports repair E180 that broke kolt's lucide file, and perf takes M70
(seven kolt files never cached — the largest per-keystroke cost on the owner's machine). Ten
lanes; eight go on no ruling, two (style-36, sweep-36) carry one each that changes what they build.

## Rulings at GO (owner) — the ones that change what a lane BUILDS
- **R1 — A95 S2: the sugar's six nesting refusals (style-36).** S1 kept them verbatim; S2 could
  delete them (the `.on(..)` set spells every nesting) or keep them as refusals. Rec: KEEP them
  as refusals whose text steers to the `.on(<set>)` form ("write `.on(hover() + active().not(),
  ..)`"), because deleting a refusal makes a formerly-refused program compile with nothing to
  steer to; the codemod (§7) rewrites the 27 `not` sites and the `child_relation` sites to `.on`.
- **R2 — A95 S2: `Condition::eq` (style-36).** `.eq(value)` on an attribute condition would
  collide with a future `PartialEq::eq`. Rec: KEEP `.eq()` and never derive `PartialEq` on
  `Condition` (the canonicaliser compares tokens internally; a condition value is never compared
  by user code); document that at the type. Alternative: rename to `.value(..)` now, before S2
  is the surface anyone learned.
- **R3 — A95 S2: `within(hover())` needs the slot-KEY change (style-36).** S1 refuses a
  non-attribute guard because the guard's selector travels inside `media:condition:property`.
  Rec: change the key to a structured record in S2 (the breaking order is the time) so
  `within(hover())` and `within(attribute("open"))` land with the surface; the stylesheet-identity
  harness from S1 is the gate for programs that write no guard.
- **R4 — B334 (lang-a-36).** A method name shadows a same-named free function inside its own
  `impl` block. Rec: the FREE function wins when the call has NO receiver (a method needs one;
  `self.when(..)` is the method) — one resolver rule, pinned; A99 deletes the std exhibit either
  way, so this is a language rule, not a std fix.
- **R5 — B318 S6: std's curation policy (sweep-36).** Which std items carry `export`. Rec: an
  item is exported when any OTHER file imports it today (the 118 cross-file imports), when the
  reference documents it, or when the docs/examples/corpus/kolt import it; a module whose every
  item qualifies gets `export *;`; everything else stays private; the `std_sources` warning
  suppression is then DROPPED and the plain-reach warning must fire 0 times on std. User packages
  keep the uncurated-module exemption.
- **R6 — M55's shape (perf-36).** Cross-leg module sharing was refused once (M52). Rec: MEASURE
  first (per-module overlap of kolt's three legs with dx-33's instrument), then build the key
  (module + platform + seed closure) only if the second node leg's `base` phase drops by half or
  more on kolt's shape; otherwise record the numbers on the item and stop.
- **R7 — A99's estate (lang-a-36 + the sweep).** The retirement rewrites docs (17 sites),
  examples (4), vilan-core tests (14), vilan-cli tests (20) in the lane; kolt's NINE sites
  (views.vl:86/114/158/162/394, theme.vl:270, overlay.vl:502, views.vl:731, theme.vl:216) are the
  owner's — rec: the integrator rewrites them at the sweep at the owner's word, as the Order 35
  migration was done.
- **R8 — M66 (perf-36).** The lazily-stamped identity intrinsic returns twelve corpus goldens to
  their pre-A92 shape. Rec: build — it is small, it removes golden churn from every future
  reactive change, and C14's paper will want reference identity to be an intrinsic anyway.
- **R9 — E180's third subtraction (editor-36).** Rule (2) must subtract prelude bindings and
  path-qualified reaches (the fix); the OPTIONAL third subtraction treats a module the prelude
  module itself `export import`s as ambient. Rec: TAKE it — it is what removes the redundant
  `import std::ui::{ (impl View) };` rescue in every kolt file, not only the collision.
- **R10 — F1's paper assumptions (paper-native-36).** Rec: the paper and its probe ASSUME the
  emit-Rust backend (rustc does codegen; wgpu/winit/taffy/cosmic-text reusable) and desktop first,
  and present the alternatives as costed rejections rather than open forks; the UI surface stays
  the DOM-shaped `View` (the SSR twin is the precedent). The owner's four questions on F1 are
  answered by the paper, not before it.
- Record-only defaults (written as built at the sweep unless the owner objects): G24 R1–R3, B340
  Q1–Q2 and A99 stand as ruled 2026-09-14; A100 builds S1 then S2, S3 (the std `unwrap_or`/
  `expect` retrofit) is Order 37's; C14's paper RECOMMENDS a representation and builds nothing;
  L20 stays the owner's own machine's; A87, A94, B298 (behind Q3), K14, M60, M56/M57 not this
  order; E121 untouched; the `bind_each` trio's retirement rides A99 (ruled).

## Mechanics (every lane)
- Worktree `vilan/.claude/worktrees/<lane>` branched from `origin/next` (9b22ec36); NEVER
  touch the main checkout; NEVER `git stash`; kill only PIDs you recorded; kolt
  (`~/code/kolt`) is READ-ONLY — read it ONCE into your scratch and work from the copy.
- Lanes NEVER PUSH. The integrator pushes each lane branch at merge time. Commit as the
  worktree's configured identity (the push hook refuses a `Claude` author).
- One commit per item (a slice may take several, each buildable), message = the CHANGELOG
  entry's first sentence; CHANGELOG entry under the right family with its marker
  (`<!-- family: breaking|miscompile|fix|feature|performance|tooling|diagnostics -->`); the
  parity gate is `--test release_scripts`. A refusal that newly fires on std, `examples/`, the
  corpus, the docs or kolt carries a `breaking` note naming the program. This order has FOUR
  breaking items (A95 S2, A99, B318 S6's std curation, and any lane whose refusal newly fires);
  each carries its migration note in the CHANGELOG.
- Diagnostics: a new message is a ledger row written `NEW` in
  `crates/vilan-cli/tests/diagnostics-ledger.tsv` (the integrator numbers; next id 464 —
  NEVER write a literal id), an edited text is a row edit, a RETIRED row is a deletion named in
  the report; every lane that touches a row runs `--test diagnostics_ledger`; a message whose
  FIRING changes means `-p vilan-lsp` too. The proposals `diagnostics-ledger.md` is the audit
  paper — the integrator re-keys it at the sweep from your report.
- A named parser rule constant needs TWO edits: `RULE_STATEMENT_SITES` AND
  `CURATED_RULE_STATEMENTS`. Two lanes add rules this order (lang-b-36, lang-c-36): both lists
  are unioned at merge — write ONE line per constant.
- A keyword lands in THREE homes (lexer, TextMate grammar, book theme) in the same commit
  (lang-c-36's `lazy`). The TextMate grammar is also edited by editor-36 (E176): different rules,
  named in both reports.
- PIN LOCATION: attribute and type refusals in vilan-core `tests/inference/<module>.rs`;
  module resolution in `tests/module_resolution.rs`; wire behaviour in vilan-cli
  `service_layer.rs`; reactive in `reactive_lifetimes.rs`/`reactive_channels.rs`; rows/children
  in `ui_rows.rs`; styling `style_when.rs`/`style_chain_order.rs`/`hmr_css_matrix.rs`/
  `ssr_differential.rs` + vilan-core `inference/styling.rs`; const in `inference/const_eval.rs`
  (or the module the lane finds); the TextMate scope pins in `grammar_sync.rs` (they need
  `npm ci --prefix editors/vscode` in YOUR worktree; `CI=true` makes a skip a failure);
  vilan-lsp/vilan-ide pins are `mod tests` inside `src/*.rs` (formatter pins run as
  `-p vilan-core --lib`).
- Shared test files: ADD whole new `fn`s. An EXISTING fn you must edit is named in the report;
  a program CONST edited beside its pin is named too; a multi-line string const whose first line
  ends in `"\` must be REWRITTEN as concatenated lines (N81: the merge tools mis-split it).
- Goldens (split/corpus/markdown/`.css`) move on ANY change to what std::reactive/std::ui/
  std::style emit; regenerate per the ritual over YOUR tree and say so; the integrator
  regenerates once more over the merged tree. Three lanes move goldens (lang-a-36, perf-36's
  M66 moves twelve BACK, style-36's S2); sweep-36 must NOT move any.
- Tests: `cargo nextest run -p <crate> --test <name>` targeted (`-p A -p B --test X` applies
  `--test X` to EVERY package — run packages separately); the whole `-p vilan-core` run is the
  merge gate; `-p vilan-core -E 'test(every_std_module_is_clean_under_full_scan)'` IS yours
  (std edits). Clippy `--all-targets -D warnings`, `cargo fmt --all --check`, `vilan fmt` over
  any `.vl` touched. The inference harness writes to `/tmp` (N82, this order's hygiene lane
  fixes it): an ENOSPC red is re-run once before it is believed.
- Scratch: `scratchpad/<lane>/`; the scratchpad is shared — read nothing outside yours.
- Heredocs in their OWN shell call. No SendMessage — a question you cannot answer from source
  is an OPEN Q in the report and you build your recommendation. Perf claims: CPU time or
  callgrind Ir + loadavg, never wall.
- Report (final message): per item/slice — commit sha, what landed, the pins (names), numbers;
  FINDS as candidate items with evidence; OPEN Qs; anything unfinished and why; corrections to
  this brief. Model: Opus.

## Lane visibility-36 — B318 S4: the per-importer method namespace (+ B335, B336, B338)
Read B318 (its 2026-09-13 rulings: `export` on an impl means what it means everywhere — an
invisible impl contributes NO methods, no ambient impls, the only reach is `#`), visibility.md
§3 whole (§3.2 the rule, §3.3 what `candidates_of`/`impl_members_for_bound` become, §3.4 how a
call consults it, §3.5 monomorphization — the pin that fails if anyone implements "the
instantiating file's set", §3.6 the steers), §9 S4, §14 "What S4 receives" (`Implementation.
source`, `Program::import_impl_restrictions`, `impl_selector_members`; `check_impl_selector_
admission`'s `restricted` map IS `file_impls` inverted — lift it into a `Program` field), B330's
documented admission (R5 of Order 35: the call-site refusal lives here), `impl_select.rs`,
`transformer.rs`'s two `select_member` sites.
1. **S4.** The import-site refusal replacing the cross-module half of
   `check_duplicate_inherent_members`; `candidates_of` / `impl_members_for_bound` /
   `impl_members_for` / `known_receiver_candidates` / `applying_implementations` FILE-SCOPED on
   the lifted admission map; the transformer's two `select_member` sites threaded with the
   ENCLOSING function's file (`source_of(enclosing_fn)`); `resolve_import` gains `bind: bool`
   so a selector-only statement walks the path (retire `module_source_by_name`'s file-name
   lookup — the Windows seal fix 9b22ec36 is the exhibit of why); `export impl` ENFORCED (an
   unexported impl in a curated module contributes nothing to an importer that did not reach it;
   `#(impl T)` built on `Token::Hash` at `at_impl_selector`); B330's pair refused at the call
   under the filter, with the selector named as the fix. Pins: P8's pair refused at the second
   import with the selector fix; each module imported alone is clean; a selector resolves the
   pair; §3.5's monomorphization pin (declaring file's set); B279's consumer list re-asserted;
   `export impl` hidden from a consumer that did not `#`-reach it; `#(impl T)` admits it; B330's
   refusal; the uncurated-module exemption (everything offered) unchanged.
2. **B335** — resolve a module segment whose module owns both `x.vl` and `x/` to the BODY entity
   (or record the file on the namespace entity); pin `import pkg::x;` through `source_of` and
   Organize Imports. **B336** — enforce `export(in <general PATH>)` in the post-build family
   where `Program`'s paths are in hand; pins from `pkg::b` (warns) and `pkg::a::c` (silent).
   **B338** — one row at the import when a selector admits no impl; pin it and the `(impl _)`
   control.
Sizing: L + S + S + S. Model: Opus. Owns analyzer.rs's import/impl resolution (name every fn),
impl_select.rs, the transformer's `select_member` sites, `tests/module_resolution.rs` +
`inference/impls.rs` (or the module the lane finds). Nobody else touches impl_select.rs.

## Lane sweep-36 — B318 S6: the `export *;` estate sweep + std's curation (R5) + S5's docs; merged LAST
Read B318, visibility.md §6 (the census: std 664 items / 118 cross-file imports; kolt 272
plain-reach warnings / website 130 / benchmarks 34 / examples 56 — kolt is ALREADY curated: its
19 modules, the lucide file and `scripts/lucide.mjs`'s template carry `export *;` since the
Order 35 migration, so kolt is a READ-ONLY verification target here), §8 rollout, §9 S5/S6, §14
(the `std_sources` suppression, the uncurated-module exemption), E181 (the marker's canonical
place: module comment / blank / the leading import run / blank / `export *;` / blank — PLACE it
there by hand; editor-36 builds the formatter rule and the merged tree's `vilan fmt --check` is
the proof), `names.md`, `grammar.md`, `tour/projects.md`, `appendix/editor.md`,
`appendix/errors.md`.
1. **The codemod (non-std).** `export *;` into every module of the website, the examples, the
   templates (`vilan init`'s scaffolds), the benchmarks and the corpus/test fixtures that a
   plain-reach warning names today (visibility.md §6's 73 files minus kolt's) — one commit, one
   line per file at E181's place, nothing else in the diff. Gate: every package compiles with
   the plain-reach warning at 0.
2. **std's curation (R5).** Per R5: `export` on every item another file imports, the reference
   documents, or the docs/examples/corpus/kolt import; `export *;` where every item qualifies;
   the rest private; then DROP the `std_sources` suppression. Gate: `every_std_module_is_clean_
   under_full_scan` green, the plain-reach warning 0 on std, the exposure warning 0 on std (an
   exported signature naming a private type is a curation error — fix the curation, not the
   warning), the seal union unchanged in count. Record the numbers: items exported / `export *;`
   modules / private items; the diff is reviewed by the owner as ONE commit.
3. **S5 — the docs.** `names.md` §4.8 Visibility (the bit, the four forms, the reach, the two
   warnings), §4.6 rewritten (one namespace per type per importing file; the selector as the
   disambiguator), §4.3 (`only`, the selector, `::*`), §4.1's impl consequence; `grammar.md` §3.2
   the four productions; `tour/projects.md` a visibility section beside the prelude key;
   `appendix/editor.md` the completion filter + the Organize Imports row; `appendix/errors.md` the
   two warnings and the rewritten `pub` rule. The docs describe S4's namespace as visibility-36
   builds it — read its brief; where the two disagree, the docs say what visibility.md §3 says.
Sizing: S + M + M. Model: Opus. Owns every `.vl` file it touches (list them), the docs pages
above, the `std_sources` suppression site in analyzer.rs (one fn, named). MERGED LAST, after
every other lane, and rebased by the integrator if a `.vl` conflict appears.

## Lane style-36 — A95 S2 (BREAKING), S3, S5 (+ R1, R2, R3; B322 verified)
Read A95, style-conditions.md §1–§2, §4 (the block spelling), §6 (what stays: the single-
condition sugar STAYS), §7 (the migration census: 27 `not` sites, kolt's `pseudo` sites — kolt is
already migrated to `.on(..)` conditions, re-census it read-only), §9 S2/S3/S5, §12 (`within`
takes a condition; (iv) `Option<str>` for one release then `[deprecated]`), §13 as-built (the
one-type `Condition`; `IntoConditions` has one implementor — S2's seam; the slot-key limit
behind `within(hover())`; "still to decide before S2" = R1/R2), B322, css-block.md §7.1 (the
completion tables), `style.vl`, `STYLE_CONDITION_METHODS` (formatter.rs), `style_table_sync`.
1. **S2 — the new surface.** `on` in the reference and the guide; the free constructors in
   `std::style::prelude`; the `css` block head `.on(<set>) { … }` (no lowering change, §4);
   `pseudo`'s `:` refusal; `element(name)`; `child_relation` DELETED; the guard+child-relation set
   admitted and layered; the slot KEY becomes a structured record (R3) so `within(hover())` and
   `within(attribute("open"))` land; the `not` MARKER retired for `.not()` (A89's marker); the six
   nesting refusals kept with `.on` steers (R1); `.eq()` kept (R2). The CODEMOD: every `not`
   site (std 27 per §7 — re-census), every `child_relation` site (std 7, vilan-core tests 4), and
   every doc/example/corpus site, rewritten to the set form; the CHANGELOG `breaking` entry
   lists the four rewrites. Gate: the S1 stylesheet-identity harness over every program that
   writes no guard (report the count), the `.css` goldens regenerated for the rest and each
   difference explained; ledger rows `NEW` for the new refusals; `hmr_css_matrix`,
   `ssr_differential`, `style_when`, `style_chain_order`.
2. **S3 — the tooling.** `STYLE_CONDITION_METHODS` becomes the canonical order over condition
   VALUES (§2.6); `vilan fmt` sorts an `on` head (formatter.rs — the ONE fn you own there, named);
   css-block §7.1's completion tables gain the constructors after `.on(` and after `+`
   (vilan-ide's style completion table — the one file you own there); `style_table_sync`
   extended to hold the value constructors to the canonicaliser.
3. **S5 — the estate.** The `attribute`/`within` `Option<str>` forms deprecated (one release,
   `[deprecated]` with the `.eq()` steer — not removed); the guide and reference rewrites; kolt
   re-censused read-only (expected: zero S2-breaking sites after the Order 35 migration; report
   any). **B322**: verify the `:` refusal closes both halves (`Style::add`'s split, `media`/`raw`);
   if a half survives, fence it (one row) and say so.
Sizing: L + M + S. Model: Opus. Owns style.vl, style/prelude.vl, the style tests, the css
goldens, `STYLE_CONDITION_METHODS` + `sort_on_head` (or whatever it is named) in formatter.rs,
vilan-ide's style completion table, the styling docs. Nobody else touches style.vl.

## Lane lang-a-36 — A99 (ruled: hard removal, six methods), A98, B334 (R4)
Read A99 (the ruling: `View::when`/`swap`/`swap_split`/`bind_each`/`bind_each_values`/
`bind_each_by` deleted, no deprecation window, the editor steer rewrites), positional-slots.md
§10.1/§11, browser/ui.vl 345–600 + 1118–1250, process/ui.vl 261–320 + 559–600, `chunks.rs`
(102/105, 243/247 — both spellings recognized today), web.vl's prelude, ui.vl:965 (B268's
note), A98 (the 1,000-row harness numbers), B334.
1. **A99.** Delete the six methods in BOTH layers; fold `split_route` back into the free
   `swap_split` (nothing shadows it once the method is gone); `chunks.rs` recognizes the free
   `swap` only (the `view_method` arms go); the `std::web` prelude gains `when`, `swap`, `each`,
   `each_values`, `each_by` (E145's rule 0 then fades an explicit import — expected); the curated
   steer on the vanished method ("no method `swap` on `View` — write `child(swap(..))` or
   `{swap(..)}` in a child hole") with the quick fix rewriting in place (the vilan-lsp side of
   that fix is ONE new arm in the steer table — name it; editor-36 does not touch it); the
   estate: docs 17, examples 4, vilan-core tests 14, vilan-cli tests 20 rewritten (R7); kolt
   NOT touched (the integrator's, at the sweep). Pins: the six refusals with the steer; the free
   forms place at the anchor (A85's pins stay); the split recognizer retargets a recognized
   `swap` VALUE; the goldens regenerated over your tree (say which).
2. **A98.** Track the previous index in the region plan; cut/re-insert only rows whose position
   changed; measure with the same 1,000-row harness (nodes, insertions, Ir under `--jitless`)
   before/after — the item's numbers are the baseline (1,005 → 2,005 nodes; ~4,000 → ~8,000
   insertions).
3. **B334 (R4).** The free function wins when the call has no receiver; one resolver rule in
   the analyzer's call-subject lookup inside `impl` bodies (name the fn); pin the shape with a
   user impl (the std exhibit is gone after A99).
Sizing: M + S + S. Model: Opus. Owns browser/ui.vl, process/ui.vl, web.vl (the one prelude
line), chunks.rs, `ui_rows.rs`, the split golden, the slot docs, the one steer arm. Nobody
else touches ui.vl.

## Lane lang-b-36 — B340 (ruled) → G24 (ruled) → B333
Read B340 (Q1: a `Callable` coerces like a function declaration; Q2: the closure-field rule
verbatim — `(a.b)(c)`, the existing steer's text widens; the owner's framing: closures are
formally callable structs, `Callable` the primitive), G24 (R1: folds only in const contexts;
R2: explicit `const let` required + the STEER "declare it `const let`" with a quick fix on the
two refusals; R3: local `const let`; the snapshot = a `Callable` struct of the captures), B333,
const-eval.md §1 ("result must be plain data" — amend), §8.1 (`check_value_escapes` still
refuses an R closure), §9.1, §10.7 (`Value::Closure` = body + env scope), `not_callable_message`
(analyzer.rs ~36289), the struct-called refusal (~37211), fn-coercion.md §1, operators.vl.
1. **B340.** `trait Callable {}` in std::operators (doc: a `call` method of the impl's own
   arity); the call-subject arm resolves `x(args)` on a receiver whose type implements
   `Callable` as the method `call` (the ordinary method path — generics, context clauses,
   argument checking); `impl T with Callable` without `call` refused (row); a type with `call`
   but no `Callable` keeps today's refusal + the steer "implement `Callable`"; the struct-TYPE-
   name refusal unchanged; transformer `x(args)` → `x.call(args)`; interpreter arm; Q1: the
   coercible set gains "a value whose type implements `Callable`", lowered as `|..| x.call(..)`;
   Q2: the closure-field steer's text widens ("a closure or a `Callable`"). Pins: call resolves
   and type-checks like the method; a context clause on `call` inherited at the call; const
   parity; Q1/Q2; kolt's `src/lib/scale_step.vl` shape as a fixture (read-only source).
2. **G24.** `const let NAME[: T] = EXPR;` (module level AND local, R3) and `const fun`;
   `const mut` refused (row); `ConstValue` gains the closure snapshot = a `Callable`-shaped
   record (the closure's body id + its captured values); `Program::const_results` folds a
   `const let` as it folds `let x = const e`; the transformer lowers the snapshot as a struct
   literal over the closure's emitted body (no IIFE); `check_value_escapes` still refuses an R
   closure; `const fun`'s body run through the const capability check at the declaration,
   spanned, naming the capability; the two existing refusals ("reads only compile-time-known
   bindings", "result must be plain data") gain the R2 steer + quick fix (vilan-lsp: one arm,
   named); the raw `ConstVariable` leak retired (row). Pins: `const let add = |a, b| a + b;`
   folds `const add(1f, 2f)` to `3` and calls the snapshot at runtime; `const fun scale_step` +
   `const let space = scale_step(0.25)` + `let s = const style().padding(space(2f))` folds to
   `0.5rem`; `const fun` reaching `fetch` errors at the declaration; a captured runtime `let`
   errors at the capture; §8.1's pins stay red; the corpus differential reports no change for
   programs writing neither keyword. Docs: const-eval.md §11; the const reference page.
3. **B333.** Record the clause on a call's own type (from the callee's declared return) and on
   a literal's type from its landing; pin both shapes; the std value forms' `wire` closure is the
   exhibit.
Sizing: M + M + S. Model: Opus. Owns const_eval.rs, the analyzer's call-subject arm +
`not_callable_message` + the const capability check + B333's `clause_carried_by` (name every
fn), `inference/const_eval.rs` (or the lane's module), operators.vl, the two steer arms in
vilan-lsp (named), parsing.rs's `const` prefix rows (`parse_const_declaration`, one new fn — lang-c
owns `lazy`'s rows; name yours).

## Lane lang-c-36 — A100: `lazy` parameters (S1) then `lazy` module bindings (S2)
Read A100, lazy.md whole (§1 parameters, §2 bindings, §3 exclusions, §5 lowering: one memo
cell `{ state, value, thunk }` + `__force`, `lazy` a hard keyword in THREE homes, §6 calls:
poison, `lazy`, retrofit gated, §7 slices), the capture rules (R9, the view-capture refusal),
`claims-and-epochs.md` §4 (surface, not a model change), the interpreter's closure arm.
1. **S1 — lazy parameters.** Keyword through lexing.rs/parsing.rs/formatter + TextMate + book
   theme (same commit); the modifier in the three grammar homes (free fn, method, trait
   signature); call-site thunking (a closure over the free variables — every capture rule
   applies); forcing on first read inside the callee, memoized; forwarding to a lazy position
   passes the cell, to an eager one forces; rejections with steers: resource argument, awaiting
   argument (→ `async expr`, pass the `Task`), context-reading argument (→ pass a closure); the
   laziness agreement check for impls of a lazy-parameter signature; hover renders `lazy`;
   `__force` + its interpreter arm in the same commit. Pins: forced-once (counting side
   effect), never-forced-never-runs, forwarding chains, each rejection, trait mismatch, hover,
   interpreter parity.
2. **S2 — lazy module bindings.** `lazy let name: T = init;` — the memo cell at module scope;
   first-use init order observable via prints; the cycle trap ("lazy initialization cycle:
   `database`"); poison (re-panic with the poisoned message); loan-only/write-frozen inheritance
   for a resource (a real `Database` pin); platform coloring of the initializer; sync +
   context-free enforced. Docs: spec §6.x sentence, the std pages for `expect`/`unwrap_or`
   (describe, do NOT retrofit — S3 is Order 37's), tour "lazy resources".
Sizing: L. Model: Opus. Owns lexing.rs + token.rs (`lazy`), parsing.rs's parameter/`let`
modifier arms (named), the formatter's signature printing (named fn), the analyzer's parameter
binding + module init (named), the transformer's `__force` lowering, the interpreter arm, the
TextMate `lazy` keyword rule + book theme, `inference/lazy.rs` (new). Ledger rows `NEW`.

## Lane editor-36 — E180 (R9), E181, E175, E176, E177, E178, E179
Read E180 (the whole analysis: rule (0) is right, rule (2) counts prelude-bound path-qualified
reaches, a rescue binds a taken name — kolt lucide's `fun option()`; the LSP driver at the
integrator's scratchpad is described in the item), E181 (the canonical place; the add-import
and Organize Imports insertion points), E175, E176, E177, E178, E179, document.rs
`import_leaf_is_used` (~4972) / `module_import_brings_a_use` (~5140) / `rescuing_subject`
(~5215) / `rewritten_import_statements` (~4580), formatter.rs `module_only_import_branch`
(1792) + `ModuleRescue` (1771), `Document::QuickFix`, vilan-ide `OriginListing::completions` /
`auto_import_completions`, the TextMate head-region rules (E170's), `StyleSurface::extend`,
session_trace.
1. **E180.** Rule (2) subtracts `program.prelude_bindings` and counts only what a module
   import ALONE carries — impl members resolved by receiver syntax, never a definition spelled
   as a path segment behind a head (find the analyzer's method-call resolution record; a text
   check for a preceding `::` is the fallback); R9's third subtraction (a module the prelude
   module `export import`s is ambient); the collision guard: the module segment's name must be
   free in the file (no top-level declaration, no other leaf or alias) → a new
   `ModuleRescue::Keep` arm printing the statement verbatim with its leaves UNFADED; the rule-(0)
   fade says "redundant: the prelude already binds `Option`". Pins: (a)–(e) of the item;
   verify over a COPY of kolt: organize `src/lucide/lib.vl` and `vilan check` it (the copy's
   manifest with the build hook removed).
2. **E181.** The bare `export *;` moves to the slot after the leading import run (paragraph
   gaps both sides; a comment above it travels; no imports → after the module comment; a
   duplicate marker left in place; idempotent); the add-import quick fix and Organize Imports
   insert a new leading import ABOVE the marker. Pins as the item lists. sweep-36 places its
   markers by hand at this slot; the merged tree's `vilan fmt --check` proves the two agree.
3. **E175** — feed `StyleSurface::extend` from the program's impl table; pin the sibling-file
   case. **E176** — one TextMate rule for a parenless head item (declines the tag name and a
   `{hole}`); scope pins. **E177** — widen `QuickFix` with a target document; the Export fixes
   edit `S`'s declaration wherever it lives; pin through the code-action handler. **E178** —
   the two vilan-ide filters on `Importable.exported` under the uncurated-module exemption;
   `module_impl_blocks` filters unexported subjects once visibility-36 enforces `export impl`
   (read its brief; if S4 is not merged when you build, filter on the bit and say so). **E179**
   — three fields on the session summary's retained-state line; E166/E174 pins extended.
Sizing: M + M + M + S + M + S + S = L. Model: Opus. Owns vilan-lsp document.rs (the organizer
fns above + `QuickFix`), publish.rs, session_trace, formatter.rs's `module_only_import_branch`
+ `ModuleRescue` + the NEW export-placement fn (name it; style-36 owns `STYLE_CONDITION_METHODS`
+ its `on`-head sort — two lanes in one file, disjoint fns), vilan-ide completion.rs's two
filters, the TextMate head rules (lang-c owns the `lazy` keyword rule), the css converter.

## Lane perf-36 — M70 (HIGH), M55 (R6), M66 (R8)
Read M70 (seven kolt files never cached: `entry_alias_module` + `entry_is_open_module`
suppress the pre-entry resolve AND the store; 0.42–1.43 s CPU per keystroke each), M55, M66,
M67's as-built (dx-35: the LRU budget, `base_cache_worlds/weight/budget`), dx-33's instrument,
`base_cache_miss_cost_across_a_sibling_checkout`, the base cache's key and store paths in
analyzer.rs (M9/M23/M24 history on the items), reactive.vl's `id` field + `fresh_id()`, the
server's dedup (`LiveForward.holds`).
1. **M70.** Store the world for an entry-aliased open module under a key that excludes the
   entry's own module (the world minus the alias), or resolve the cycle at store time — pick
   after reading; measure the seven files' per-keystroke CPU before/after with the paired
   harness over a READ-ONLY kolt copy; pin the cycle shape (a fixture of three modules with a
   cycle through the entry) served from the cache on the second analysis.
2. **M55 (R6).** Measure the per-module overlap of kolt's three legs; design the key (module +
   platform + seed closure) against M19's record; BUILD only if the second node leg's `base`
   phase drops ≥ 50 % on kolt's shape; otherwise the numbers go on the item and the lane stops.
3. **M66 (R8).** Replace the eager `id` field with a lazily-stamped identity intrinsic
   (`Shared::identity`, `o.__id ??= next++`); the server's dedup and `LiveForward.holds` read
   it; the `.mjs` goldens return to their pre-A92 shape except where an export asks; measure Ir
   per `SignalCell::new` before/after on kolt's client warm.
Sizing: M + L(measure)/S(stop) + S. Model: Opus. Owns the base cache (analyzer.rs's cache fns,
named; memory.rs), reactive.vl (M66 only — lang-a owns ui.vl), the transformer's one intrinsic,
the twelve goldens that move back.

## Lane hygiene-36 — DROPPABLE, lands FIRST: N81, N82, N83, N84, N85, B337, B339
Read each item. N81's tools live in the PROPOSALS repo (`scripts/integration/{fold_tests_by_
name,merge_items_by_name}.py`) — you cannot commit there: copy them into your scratch, fix,
add pins (a pytest or a shell harness over the three shapes: the `"\` continuation, the
renamed-on-HEAD test, the edited const), and hand the fixed files + harness back in your
report at `scratchpad/hygiene-36/tools/`; the integrator lands them.
1. **N81** — the three shapes above + the `union` step's duplicate-constant lines
   (`RULE_STATEMENT_SITES` unioned twice in Order 35). **N82** — the inference harness writes
   under `target/` (or `CARGO_TARGET_TMPDIR`) and cleans eagerly; an ENOSPC guard naming the free
   space. **N83** — gitignore the corpus build's asset artifacts under `vilan/test/`; a hygiene
   pin. **N84** — a load-aware bound for the cost gate; a settle wait in the rpc pin; find the
   shared state behind the two `modules::` tests under `cargo test`. **N85** — re-run the prelude
   census (prelude.md §10.1) or drop the figure (report which, with the number); re-anchor
   css-block.md §15.3 on the sheet number (−8.1 % → the B308 numbers in style-conditions.md
   §13); ROW the interpreter's unrowed `Failure` messages (the ruling: row them — they are user-
   visible). **B337** — one row edit (the directory form) + the namespace arm of
   `refuse_shadowed_submodules`; pins for both. **B339** — the `!in_macro_world()` guard with a
   pin that plants a derive into a force-loaded module fixture.
Sizing: S ×7 = M. Model: Opus. Owns the test harness plumbing, `.gitignore`, the two flaky
pins, `refuse_shadowed_submodules`, `derive_impl_source`'s macro-world guard; the paper edits
(prelude.md §10.1, css-block.md §15.3) are handed back in the report for the integrator.

## Lane paper-native-36 — C14's paper, then F1's paper (R10); NO build
Read C14, F1, C1, A97, M66 (identity), shared.vl, arena.vl, reactive.vl (`SignalCell`, `Owner`,
`Signal`, `Memo`, `RemoteSource`, `Task`), destruction.md, memory-management.md, lifetimes.md
§6.1, ambient-owner.md, affine-moves.md, capture-clones.md, leak-soak.md, platform-model.md,
platform-coloring.md, ssr.md/process.md (the second-layer precedent), style-conditions.md
(conditions → hit-test state), the analyzer's `primitive_struct_ids` (`Shared` is a primitive).
1. **`proposal/signal-cell-representation.md` (C14).** (1) The census: every `Shared` use in
   std (13 files, reactive.vl's 47 mentions) and kolt (4 files, read-only), each classified
   owner-scoped / root-scoped / escaping; (2) the two representations against it — a real
   `Rc<T>` with deterministic drop and `Weak` (C1) for the cell→subscriber→closure cycle, vs
   owner-attached `Arena` + `Handle` (disposal frees wholesale; a stale handle reads `None`) —
   with the JS backend as the first target (an `Rc` on JS is a box with no-op counts; a handle is
   two integers + a lookup); (3) the semantics of a read after the owner's disposal under each;
   (4) `Owner` itself, `Signal`/`Memo`/`RemoteSource`/`Task` in the same pass; (5) the identity
   stamp (A92/M66) under each; (6) a RECOMMENDATION and slices with exit tests (the leak-soak
   harness and `heap_cycles.js` green on JS before any native backend exists).
2. **`proposal/native-apps.md` (F1, R10).** The four pillars as slices with a dependency order
   (C14 → the backend probe → a minimal `native` platform in the build model → the render layer
   over a scene tree → the style mapping → input/windowing), each slice's exit test (a `fun
   main()` printing to stdout as a native binary; a window with one styled `<div>`; kolt's
   sidebar rendered natively), a cost per slice, the prior art measured (Dioxus/Blitz, Makepad,
   Slint, GPUI, Flutter), and the owner's four questions ANSWERED with the paper's reasons
   (emit Rust; desktop first; the DOM-shaped `View`; client-only first with the rpc runtime
   in-process as a later slice). The PROBE, done and recorded in the paper: translate a 50-line
   vilan program (structs, a closure, a `List`, a `Signal`) to Rust by hand and enumerate the
   runtime the emitter needs. What is NOT in scope: any compiler work.
Sizing: L (two papers). Model: Opus. Owns nothing in vilan; writes into its scratch and hands
both papers back in the report for the integrator to land in the proposals repo (as
paper-visibility-34 and paper-style-34 did).

## Ownership map (conflict avoidance)
- analyzer.rs: visibility-36 (import/impl resolution, `resolve_import`'s `bind`, the admission
  map, `check_duplicate_inherent_members`, the `export impl` gate); lang-b-36 (the call-subject
  arm, `not_callable_message`, the const capability check, `clause_carried_by`); lang-c-36
  (parameter binding, module init); lang-a-36 (the receiverless-call rule, ONE fn); perf-36
  (the base cache fns); hygiene-36 (`refuse_shadowed_submodules`, `derive_impl_source`);
  sweep-36 (the `std_sources` suppression, ONE fn). Name every edited fn in the report.
- impl_select.rs + the transformer's `select_member` sites: visibility-36 only. transformer.rs
  otherwise: lang-b-36 (the snapshot lowering + `x.call`), lang-c-36 (`__force`), perf-36 (the
  identity intrinsic) — disjoint fns, named.
- const_eval.rs + the interpreter: lang-b-36 (const), lang-c-36 (the `__force` arm), lang-a-36
  nothing. parsing.rs: lang-b-36 (`const let`/`const fun`), lang-c-36 (`lazy`), style-36
  nothing; both rule-constant lists unioned at merge — one line per constant.
- lexing.rs + token.rs: lang-c-36 only (`lazy`).
- std: style.vl + style/prelude.vl — style-36; browser/ui.vl + process/ui.vl + web.vl —
  lang-a-36; reactive.vl — perf-36 (M66); operators.vl — lang-b-36; every OTHER std `.vl` —
  sweep-36 (markers only, merged last).
- formatter.rs: editor-36 (`module_only_import_branch`, `ModuleRescue`, the export-placement
  fn), style-36 (`STYLE_CONDITION_METHODS`, the `on`-head sort) — disjoint, named.
- vilan-lsp document.rs/publish.rs/session_trace: editor-36; the two steer arms (A99's, G24's)
  are lang-a/lang-b's ONE arm each, named. vilan-ide completion.rs: editor-36 (the two filters),
  style-36 (the style completion table) — disjoint.
- editors/vscode grammar: lang-c-36 (the `lazy` keyword rule), editor-36 (the head-region
  rule) — disjoint rules; book theme: lang-c-36.
- chunks.rs + the split golden + ui_rows: lang-a-36. Corpus/`.css` goldens: style-36 (S2) and
  lang-a-36 (A99/A98) and perf-36 (M66 back) — each regenerates over its tree; the integrator
  regenerates once over the merged tree.
- Docs: sweep-36 (visibility S5), style-36 (styling), lang-a-36 (slots), lang-b-36 (const),
  lang-c-36 (lazy) — disjoint pages.
- Merge order: hygiene-36, lang-a-36, perf-36, lang-b-36, lang-c-36, editor-36, visibility-36,
  style-36 (css goldens), sweep-36 LAST (markers; `vilan fmt --check` over the merged tree is
  its gate together with E181). Papers land in proposals at the sweep.

## At the sweep (integrator, proposals)
- Close: B318 (S4+S5+S6 landed — the paper's arc complete) · B335 B336 B338 · A95 (S2+S3+S5;
  S4 withdrawn under G23) · B322 (if verified) · A99 A98 B334 · B340 G24 B333 · A100 (S3 → a
  new item) · E180 E181 E175 E176 E177 E178 E179 · M70 M66 (M55 per R6's outcome) · N81 N82
  N83 N84 N85 B337 B339 · C14 and F1 stay OPEN with their papers landed (`signal-cell-
  representation.md`, `native-apps.md`) and their slices filed as items.
- Papers: visibility.md §15 as-built (S4–S6; the curation numbers); style-conditions.md §14
  as-built (S2/S3/S5; the codemod counts; the key change); const-eval.md §11; lazy.md §8
  as-built; positional-slots.md §12 (A99); fn-coercion.md (B340's line); the two new papers.
- Kolt at the owner's word (R7): the nine A99 sites; anything style-36's re-census names.
- Goldens: regenerated once over the merged tree (lang-a, perf, style moved them); the
  stylesheet-identity harness re-run there for guard-free programs.
- N81's fixed tools landed in `scripts/integration/` with their harness; the diagnostics-ledger
  paper re-keyed from the lanes' `NEW` rows (next id 464 →).
- Chronicle: Order 36 — cycle 54 entry at GO; MERGED and SEALED paragraphs; toolchain refresh
  both locations; reap.
- Order 37's queue, written at the sweep: C14's build slices (from its paper); F1's first slice
  (the backend probe's result → a `native` platform stub); A100 S3 (the std retrofit sweep);
  M55 if R6 stopped it; M56/M57/M54; E121's arc; K14; B298 (Q3); A87/A94; L20 (owner).
