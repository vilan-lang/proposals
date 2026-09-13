# Order 35 — the papers' first slices (drafted 2026-09-13; GO 2026-09-13, off vilan next @36fb64ed)

**GO (2026-09-13).** The owner: "Go with your recommendations on all rulings." Every R below is
therefore RULED as recommended: R1 the plain-import WARNING (rollout warning-only for release N);
R2 a type segment REPLACES the namespace after a zero-hit census; R3 `lib` refused as a segment;
R4 B326 declines to descend; R5 B330 documented now, refused at the call under S4; R6 M67's
default set after measuring; R7 N79 built; R8 E173 built; the record-only defaults stand. NINE
lanes. Order 34 sealed at 36fb64ed (CI green on all eleven jobs; toolchain at that
sha in both locations). Ledger next id 434. Tracker 96 open.

The shape, read from Order 34's two papers and their rulings: both designs are RULED down to
their surfaces and both say their first slice ships alone — visibility.md's S1 (the bit and the
two warnings; release N's additive half, the flip's warning period is the long pole) and
style-conditions.md's S1 (the condition values behind the existing surface; byte-identical
stylesheets are the gate) with G23, the const-eval end-of-evaluation hook the owner ruled for
B308, laid FIRST because every later emission behaviour is simpler once emission is late.
Beside them: A85/A91 on the clause B309 landed; the three silent corners of that clause; the
tooling finds Order 34 filed; the base cache's ruled budget; the std cache that never prunes.
Nine lanes; seven go on no ruling, two (visibility-b-35, lang-35's B332) carry one.

## Rulings at GO (owner) — the ones that change what a lane BUILDS
- **R1 — the plain import of a PRIVATE item (visibility-a-35).** visibility.md §5 recommends a
  WARNING with two fixes ("Export `hidden`", "Import as `#hidden`") — the flip breaks nothing;
  the alternative is an error and a codemod day one. Rec: the warning; the rollout is
  warning-only for release N (§8), the error is a later order's.
- **R2 — B332 (lang-35).** After a STRUCT segment the import walk keeps the module scope; an
  enum segment replaces it. Rec: a type segment REPLACES the namespace (one rule), gated on a
  census first — if any resolving path in the estate reaches a module member through a
  type-named prefix, the lane reports and keeps today's order.
- **R3 — B331 (lang-35).** `import pkg::a::lib` resolves `a/lib.vl` a second time as `a::lib`.
  Rec: REFUSE `lib` as a segment when the directory is a module's body (one row, a steer to
  `pkg::a`), not a silent alias.
- **R4 — B326 (solver-35).** `Option<KeyedCell<K, T>>` as an `[rpc]` return. Rec: decline to
  descend through `Option` into a KEYED handle so the form falls to the Wire refusal in the
  method's vocabulary; supporting the form (per-key `Absent`) is a design item, not this.
- **R5 — B330 (solver-35).** Two blankets bounded DIFFERENTLY declaring one member stay
  admitted. Rec: DOCUMENT the admission and pin it this order; the call-site refusal belongs to
  B318's S4 (the per-importer namespace, Order 36), where such a check lives.
- **R6 — M67's default budget (dx-35).** Rec: the lane measures miss COUNT and miss COST over a
  kolt session with dx-33's instrument first, then sets the default (expected ~192 MiB); the
  ruling is the SHAPE (LRU by key, never a focused/retained document's key), already given.
- **R7 — N79 (hygiene-35).** Delete the derive fallback and refuse a std lacking `json.vl`'s
  macros with a curated message (one row) — a lang change with a row in the droppable lane.
  Rec: build it; it is one row and it removes N70's unpinned twin.
- **R8 — E173 (editor-35).** Per-leaf fade text needs `unused_import_spans` → `Vec<(Span,
  String)>` and publish.rs's group API to carry a message per span. Rec: build.
- Record-only defaults (written as built at the sweep unless the owner objects): A95's (v) `+`
  and (vii) `element(name)` recs STAND (unaddressed); B318's S4 (per-importer namespace) and S6
  (the estate sweep) are Order 36's, as are A95's S2 (the new surface, BREAKING for 37 sites),
  S3 (tooling) and S5; M55 (per-module sharing) on the next perf order; A94, A87, K14, B298 (behind
  Q3), A76/A77/A81 not this order; M62 not built; E121 untouched.

## Mechanics (every lane)
- Worktree `vilan/.claude/worktrees/<lane>` branched from `origin/next` (36fb64ed); NEVER
  touch the main checkout; NEVER `git stash`; kill only PIDs you recorded; kolt
  (`~/code/kolt`) is READ-ONLY — read it ONCE into your scratch and work from the copy.
- Lanes NEVER PUSH. The integrator pushes each lane branch at merge time.
- One commit per item (a slice may take several, each buildable), message = the CHANGELOG
  entry's first sentence; CHANGELOG entry under the right family with its marker
  (`<!-- family: breaking|miscompile|fix|feature|performance|tooling|diagnostics -->`); the
  parity gate is `--test release_scripts`. A refusal that newly fires on std, `examples/`, the
  corpus, the docs or kolt carries a `breaking` note naming the program.
- Diagnostics: a new message is a ledger row written `NEW` in
  `crates/vilan-cli/tests/diagnostics-ledger.tsv` (the integrator numbers; next id 434 —
  NEVER write a literal id), an edited text is a row edit, a RETIRED row is a deletion named in
  the report; every lane that touches a row runs `--test diagnostics_ledger`; a message whose
  FIRING changes means `-p vilan-lsp` too. N76 made `ROWS_THE_ENUMERATION_CANNOT_REACH` keyed
  by text, so a `NEW` row CAN be listed there now.
- A named parser rule constant needs TWO edits: `RULE_STATEMENT_SITES` AND
  `CURATED_RULE_STATEMENTS`.
- PIN LOCATION: attribute and type refusals in vilan-core `tests/inference/<module>.rs`;
  module resolution in `tests/module_resolution.rs`; wire behaviour in vilan-cli
  `service_layer.rs`; reactive in `reactive_lifetimes.rs`/`reactive_channels.rs`; rows/children
  in `ui_rows.rs`; styling `style_when.rs`/`style_chain_order.rs`/`hmr_css_matrix.rs`/
  `ssr_differential.rs` + vilan-core `inference/styling.rs`; the TextMate scope pins in
  `grammar_sync.rs` (they need `npm ci --prefix editors/vscode` in YOUR worktree; `CI=true`
  makes a skip a failure); vilan-lsp/vilan-ide pins are `mod tests` inside `src/*.rs`
  (formatter pins run as `-p vilan-core --lib`).
- Shared test files: ADD whole new `fn`s. An EXISTING fn you must edit is named in the report;
  a program CONST edited beside its pin is named too.
- Goldens (split/corpus/markdown) move on ANY change to what std::reactive/std::ui emit;
  regenerate per the ritual over YOUR tree and say so; the integrator regenerates once more.
  style-35's S1 gate is the OPPOSITE: the stylesheets must NOT move (byte identity).
- Tests: `cargo nextest run -p <crate> --test <name>` targeted (`-p A -p B --test X` applies
  `--test X` to EVERY package — run packages separately); the whole `-p vilan-core` run is the
  merge gate; `-p vilan-core -E 'test(every_std_module_is_clean_under_full_scan)'` IS yours
  (std edits). Clippy `--all-targets -D warnings`, `cargo fmt --all --check`, `vilan fmt` over
  any `.vl` touched.
- Scratch: `scratchpad/<lane>/`; the scratchpad is shared — read nothing outside yours.
- Heredocs in their OWN shell call. No SendMessage — a question you cannot answer from source
  is an OPEN Q in the report and you build your recommendation. Perf claims: CPU time or
  callgrind Ir + loadavg, never wall.
- Report (final message): per item/slice — commit sha, what landed, the pins (names), numbers;
  FINDS as candidate items with evidence; OPEN Qs; anything unfinished and why; corrections to
  this brief. Model: Opus.

## Lane style-35 — G23 FIRST, then B308 on it, then A95's S1
Read G23, B308 (its ruled line), A95 and style-conditions.md (§1–§3, §5.4, §9 S1, §12 the
rulings: `.on(CONDITION, STYLE)`, `within(condition)`, (i) admit, (ii) refuse, `+`,
`element(name)`), css-block.md §15.3 (the numbers to re-measure), the const evaluator
(`const_eval.rs`), `style.vl`'s `rule`/`emit`/`class_list`.
1. **G23 — the end-of-evaluation hook.** An intrinsic (name to settle — `schedule_at_end(f)`
   is the item's) that records a const-time function by identity (a set: a repeat request is a
   no-op) and runs the list once, in registration order, in a const context after the LAST
   const evaluation of the build. Settle and document: what "the end" is under an HMR round (the
   round's finalisers run at its end; an un-re-evaluated module does not re-schedule and its
   emitted asset is retained by the round's record — B276/M59's machinery); a finaliser that
   panics fails the build naming the function. Pins: idempotent scheduling (three requests, one
   run); run-once-at-end (the finaliser sees every rule pushed after its scheduling); the HMR
   round (re-evaluated re-emits, untouched retained); the panic.
2. **B308 on G23.** `Style::rule` stops emitting at construction and appends to a registry;
   `class_list`/application marks a class LIVE; the scheduled finaliser emits the rules of live
   classes in the band order and drops the rest. Gates: `hmr_css_matrix`, `ssr_differential`,
   the corpus's `.css` goldens (they may LOSE dead rules — say which; that is the point), the
   compact-styling re-measure (css-block §15.3's method) before/after — the dead share should
   go to zero. The retraction design (§5.4) is NOT built.
3. **A95 S1 — the condition values behind the existing surface.** `Pseudo`/`Element`/
   `Attribute`/`Relation`/`Media`, `.not()`, `.eq()`, `Condition + Condition`,
   `IntoConditions`, the canonicaliser (§2: slot order, duplicate merge, the contradiction
   refusal, one media, one guard, pseudo-element placement), `Style::on(conditions, inner)`;
   EVERY existing combinator re-expressed as sugar over `on` in the same change; `within(..)`
   takes a CONDITION. Gate: BYTE IDENTITY of every stylesheet in std, the corpus, examples,
   docs and kolt (`class_list` and the `.css` outputs equal before/after — build the twin-run
   harness and report the counts). No new surface documented yet (S2 is Order 36's). Ledger
   rows `NEW` for the canonicaliser's refusals.
Sizing: M + S + M = L, sequential. Model: Opus. std edits: style.vl (+ the const evaluator for
G23). Nobody else touches style.vl or const_eval.rs.

## Lane visibility-a-35 — B318 S1 + S2 (+ B320, B321)
Read B318 (all, incl. the 2026-09-13 rulings), visibility.md §1, §2, §4, §5, §7, §8, §9 S1–S2,
§10, §13 (pay for `#`; `export impl` = any declaration — no ambient impls; `[doc(hidden)]`
retired), prelude.md §8/§11, `collect_importables`/`resolve_import`/the warnings family.
1. **S1.** `Importable.exported`; `collect_importables` stops discarding `Node::Export`;
   `export *;` (a node, a parser lookahead, both rule-constant lists); `export(in PATH)` with
   `mod`/`pkg` as reserved heads; the `export <expression>;` refusal (**B321**); `export` on an
   `impl` block (RULED: the impl's methods are unavailable to a consumer who cannot see it;
   ambient impls do not come through); the exposure warning in the post-build family
   (signature positions: value type, params, returns, exported struct fields, enum payloads,
   trait bounds, generic arguments) with the RULED wording ("`S` is returned here. `my_fun` is
   exported, but `S` is not. A consumer can call `my_fun` but cannot name the return type.")
   and the fix "Export `S`" (workspace edit; a dependency's `S` gets no fix and a sentence);
   the plain-reach warning (R1) at the import leaf and at a qualified path with its two fixes;
   completion, the add-import quickfix candidates and the "import it first" steer filtered on
   the bit; `[doc(hidden)]` RETIRED (parser refusal at top level with a steer to `export`;
   members keep it if anything reads it — nothing does: delete). Rows: 4 `NEW` + 1 edit (the
   `pub` rule's text) per the paper. Pins per §9 S1.
2. **S2.** `Token::Hash`; row 335 retired (a deletion named in the report); the css block's
   `#333` refusal re-homed to the css parser with its quickfix re-keyed; `#` on an import leaf
   (`import a::{ #hidden }`, `a::#hidden`); `lexical.md` §2.4. Pins: `#hidden` imports and does
   not warn; `#` on an exported item warns (redundant marker); `#333` in a css block still
   reports the colour rule with its fix; `#` elsewhere still refuses.
3. **B320.** A malformed import reports at the token it stopped on with a curated rule naming
   the import grammar, not `found 'import' expected an expression` at column 1; pin the six
   probe shapes (visibility.md §2.7).
Sizing: M + S + S. Model: Opus. Regions: lexing.rs (`#`), parsing.rs `parse_export` + the
import LEAF arm + the failure report, analyzer importables/`resolve_import`/warnings, lsp
document.rs filters, docs. visibility-b-35 owns `parse_import_statement`'s MODIFIER/SELECTOR
arms as NEW helper fns — do not edit those.

## Lane visibility-b-35 — B318 S3: `only` and the selectors
Read B318, visibility.md §1, §2.4–§2.6, §3 (read only — S4 is Order 36's), §7, §9 S3, §13
(no ambient impls; `#(impl T)` is the reach), E168/E169's tombstones (the predicate you
re-point), the formatter's organize section, `import_leaf_is_used`.
1. `only` as a trailing modifier in `parse_import_statement` (a NEW helper `parse_import_
   modifier`); the selector production `{ (impl TYPE) }`, `(impl TYPE)::name`,
   `(impl TYPE)::{ a, b }`, `_` as the placeholder, no binders (a NEW helper
   `parse_impl_selector`); a method selector refuses `as`.
2. `file_impls`: selector resolution as a SECOND pass over a file's import list in the
   importer's scope (`impl S` through an alias, `impl item::Struct` qualified); a brace set
   naming a selector implies 'these impls only'; `(impl _)` = every impl of the module;
   `#(impl T)` reaches a private impl. A method call in a file whose selector set does not
   admit the impl is refused with the selector named (one row) — this is the FILE-LEVEL
   admission only; the per-importer collision rule (S4) is NOT this lane's.
3. E168/E169's predicate re-pointed at selectors (E168's rewrite becomes `import a::{ (impl
   Style) };` when the file's impl uses come from one subject; the module form when they do
   not); the formatter's selector key (`BranchKey` variant, sorted AFTER names by rendered
   type text) and renderer; Organize Imports keeps a selector whose impl is used and prunes one
   whose impl is not; completion after `impl ` (the module's impl subjects) and after `)::`
   (the block's methods). Pins per §9 S3 + fmt/organize agreement extended.
Sizing: L. Model: Opus. Regions: parsing.rs (the two NEW helpers only — visibility-a-35 owns
`parse_export` and the leaf arm), analyzer selector resolution + `file_impls` (new fns; the
`candidates_of` family is S4's — read, do not edit), formatter organize/selector key, lsp
document.rs `import_leaf_is_used`/organizer, vilan-ide completion. Merges AFTER visibility-a.

## Lane slots-35 — A85 + A91 on B309
Read A85, A91, positional-slots.md (§3–§9 and §10.1: the field is `body: (|| View) context
owner_scope` with NO `sync`; the constructor takes its body as a clause-carrying PARAMETER —
an annotation-only generic argument is inert, B323; `(self.body)()` inside `impl .. with Slot
{ fun place }` is an injected call, so `place` becomes a needs-context node and `View::child<C:
Slot>` inherits an `owner_scope` requirement — CHECK THAT PROPAGATION FIRST), B309's tombstone,
the four `b309_*` pins in `inference/bounds.rs`, `Region` (A71/A88), the split recognizer
(§8.1).
1. **A85 as ruled (Order 33 R1):** five value forms `when`/`swap`/`each`/`each_values`/
   `each_by` as structs with concretely-typed closure fields implementing `Slot`, placed at an
   anchor (`Region`), the five parent methods as one-line sugar; `each` beside `bind_each`; the
   split recognizer learns the value form (a value-form `swap` silently not splitting is the
   worst failure); B253 unchanged; no `Group`. Pins per the paper §9 + the ownership property
   (a toggled-off `when`'s owner disposed → the body's effect does not fire) against the
   plain-closure control.
2. **A91:** render closures may yield a `Slot` (`|T| C` with `C: Slot`) on `swap`/`swap_split`,
   `bind_each` ×3, `when`'s body and the value forms; the region owns whatever the child placed;
   the process twin renders what the Slot renders. Pins: a fragment row, a text row, a value-form
   row, reorder/remove of fragment rows; `ssr_differential`.
Sizing: M + M = L. Model: Opus. Regions: std ui.vl/reactive.vl (+ dom.vl if `insert_before`
needs a twin), ui_rows.rs/reactive_lifetimes.rs/split tests; the split golden WILL move —
regenerate over your tree and say so. context.rs is solver-35's — if a corner blocks you, it
is an OPEN Q with the probe, not an edit.

## Lane solver-35 — the clause's corners, two rpc checks, three solver residues
1. **B323** — the struct-literal field landing consults the annotated EXPECTED type
   (`seed_tail_expectations` carries it for an annotated `let`); pin the probe (`saw 9` → the
   clause holds); the constructor shape stays the control.
2. **B324** — a literal-side check in the context pass: a closure literal born under a clause
   the threading cannot follow (`List<(|| i32) context c>`) is refused (one row); the landing
   positions are the controls.
3. **B325** — `let x = injected;` (unannotated) admitted as a forward (the clause comes from
   the initializer's type); the mismatched-clause refusal unchanged.
4. **B326 (R4)** — decline to descend through `Option` into a keyed handle; the form falls to
   the Wire refusal in the method's vocabulary; pin + the plain `Option<SignalCell<T>>` control.
5. **B327** — `check_hashable_boundary` asks the impl table through `resolved_type_is_hashable`;
   pin the hand-written impl inside a derive + the missing-impl control.
6. **B328** — `transformer::expr_type_id` resolves a parameter spelled `Expr::Local` through
   the parameter table; pin a consumer without the fallback.
7. **B329** — the `[expose]` refusal (and any sibling printing a user annotation) through
   `render_type`; sweep `pretty_print_type` callers that print an annotation; a pin per moved
   message.
8. **B330 (R5)** — document the admission at `generic_bounds_overlap`, pin the pair and a
   receiver satisfying both (the call-site refusal is S4's).
Sizing: M–L. Model: Opus. Regions: context.rs (1–3), analyzer rpc return checks (4–5),
transformer (6), render paths (7), the duplicate family (8). lang-35 owns the module loader;
visibility-a owns importables/`resolve_import`; do not cross.

## Lane lang-35 — B331 (R3), B332 (R2), D7
- **B331**: `lib` refused as a segment when the directory is a module's body (one row, steer to
  the parent path); pin `import pkg::a::lib::x` refused and `pkg::a::x` resolving.
- **B332**: CENSUS first (every resolving path in std, kolt, the website, examples, templates,
  docs that reaches a module member through a type-named prefix); if zero, a type segment
  REPLACES the walk's namespace (enum and struct alike); if not, report the hits and keep
  today's order (an OPEN Q with the count). Pin the shadowing pair either way.
- **D7**: one doc sentence at `SignalCell::update` naming the write-back; A80's refusal steer
  names it too; `-p vilan-core --test docs`.
Sizing: S–M. Model: Opus. Regions: the module loader (`resolve_module_file`,
`longest_module_prefix`, `member_or_submodule`), `module_resolution.rs`, docs.

## Lane editor-35 — E170, E171, E172, E173 (R8), E174
- **E170**: one rule inside `#element-head` — a plain attribute name is
  `entity.other.attribute-name`, a keyword-named one too; scope pins (`class(..)`, `type(..)`,
  `for(..)`, an `on:` control, a real call outside a head). `npm ci --prefix editors/vscode`
  in your worktree; `CI=true` on the pins.
- **E171**: the book's highlight.js tag regex (`vilan/docs/theme/vilan.js:123`) fixed; a note
  or pin per the theme's own testing.
- **E172**: `StyleSurface::build` fed the current file's `impl Style` self-less-chain bodies;
  pin kolt's `button_style` shape converting (copy styles.vl once).
- **E173**: `unused_import_spans` → `Vec<(Span, String)>`; `publish::diagnostic_groups` carries
  a message per span; the leaf text for E168's rewrite case; one pin on the text.
- **E174**: a `workspace/executeCommand` (both sides) that makes the server log its session
  summary now — E166's line is the payload; a unit pin on the handler.
Sizing: M. Model: Opus. Regions: editors/vscode (grammar + the command), docs theme, lsp
document.rs css conversion (E172 — visibility-a edits the FILTER fns in the same file; name
every fn), publish.rs, main.rs (the command). Merges BEFORE visibility-a.

## Lane dx-35 — M67 (ruled), M68, M69
- **M67**: the base cache's LRU byte budget — evict least-recently-used import-set key first,
  never a key an open focused/retained document names; MEASURE FIRST with dx-33's instrument
  over a kolt session (all 19 open, then a realistic focus walk): miss count, miss cost (CPU),
  worlds live; then set the default (R6; ~192 MiB expected) and pin the bound; the numbers
  table before/after (RSS, heap in use, worlds).
- **M68**: `malloc_trim` at the landing seam conditional on released bytes; the per-landing
  cost in CPU time before/after.
- **M69**: `impl_namespaces` by reference/`Rc`; measure on the base-cache clone path.
Sizing: M. Model: Opus. Regions: the analyzer's base cache (`BASE_CACHE`), vilan-lsp memory.rs/
document lifecycle, analyzer `impl_namespaces`.

## Lane hygiene-35 — DROPPABLE, lands FIRST: N77, N79 (R7), N80, L21
- **N77**: std's vilan.toml prelude comment → the measured numbers (664/63, 118) and the
  command; prelude.md §10.1's figure too (proposals; the integrator commits).
- **N79 (R7)**: delete `derive_impl_source`'s Rust fallback; a std lacking `json.vl`'s macros
  is refused with a curated message (one row); pin the refusal and the std control.
- **N80**: `reused_source`/`container_site_visited` folded into one predicate.
- **L21**: `materialize_into` runs `prune_stale(root, 7 days)` after a NEW hash lands (the
  current hash survives); `vilan cache prune [--all] [--dry-run]`; pins per the item; releases.md
  §3's sentence.
Sizing: S. Model: Opus.

## Ownership map (conflict avoidance)
- const_eval.rs + style.vl + style tests + hmr_css_matrix/ssr_differential: style-35 only.
- lexing.rs: visibility-a (`#`). parsing.rs: visibility-a (`parse_export`, the import LEAF arm,
  the import failure report — B320); visibility-b (NEW helpers `parse_import_modifier`,
  `parse_impl_selector` only). Both rule-constant lists: whoever adds a rule (name it).
- analyzer.rs: visibility-a (importables, `resolve_import`'s bit/reach, the two warnings, the
  `[doc(hidden)]` removal); visibility-b (selector resolution + `file_impls`, NEW fns);
  solver-35 (context pass, rpc return checks, render paths, duplicate family); lang-35 (the
  module loader); dx-35 (base cache, `impl_namespaces`); hygiene-35 (`derive_impl_source`).
  Name every edited fn.
- transformer.rs: solver-35 (B328) only. context.rs: solver-35 only.
- std ui.vl/reactive.vl/dom.vl + ui_rows/reactive tests + the split golden: slots-35 only.
- vilan-lsp document.rs: visibility-a (completion/add-import/steer filters), visibility-b
  (`import_leaf_is_used`/organizer), editor-35 (css conversion). publish.rs + main.rs command:
  editor-35. memory.rs + document lifecycle: dx-35.
- formatter.rs: visibility-b (organize/selector key). vilan-ide completion.rs: visibility-b
  (after `impl `/`)::`) — no one else.
- editors/vscode + docs theme: editor-35. vilan-embedded-std + upgrade.rs: hygiene-35.
- Merge order: hygiene-35, lang-35, dx-35, editor-35, solver-35, visibility-a-35,
  visibility-b-35, style-35, slots-35 (the split golden last).

## At the sweep (integrator, proposals)
- Close: G23 B308 (A95 stays OPEN: S1 landed, S2/S3/S5 Order 36) · B320 B321 (B318 stays OPEN:
  S1+S2+S3 landed, S4/S5/S6 Order 36) · A85 A91 · B323 B324 B325 B326 B327 B328 B329 B330 ·
  B331 B332 D7 · E170 E171 E172 E173 E174 · M67 M68 M69 · N77 N79 N80 L21.
- Papers: visibility.md §14 as-built (S1–S3); style-conditions.md §13 as-built (G23, B308, S1;
  the byte-identity counts; the dead-share number); positional-slots.md §11 as-built (A85/A91).
- Goldens: the split golden moves (slots-35); the `.css` goldens may LOSE dead rules (style-35):
  regenerated once over the merged tree when the gate says, and the stylesheet identity gate
  re-run there.
- Chronicle: Order 35 — cycle 53 entry at GO; MERGED and SEALED paragraphs; toolchain refresh
  both locations; reap.
- Order 36's queue, written at the sweep: B318 S4 (per-importer namespace, the solver's
  largest cost), S6 (the `export *;` estate sweep), A95 S2 (BREAKING, the 37-site codemod + kolt
  at the owner's word), S3, S5; M55.
