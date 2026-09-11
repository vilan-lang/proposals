# Order 33 — the surface order (drafted 2026-09-11; GO 2026-09-11, off vilan next @5a0d0b49)

**GO (2026-09-11).** The owner: "Go with your recommendations on all rulings." Every R below and
every record-only default is therefore RULED as recommended: slots-33 and rpc-33 GO; B299 is the
DESUGAR; B287 is refused (rpc-smalls-33); `Vec2` gains `length_squared` (styles-33); E156 is
documented (editor-33); A90, A91 (A85's Q3) and A92 (P1–P3, rpc-33's item) are filed at GO.
EIGHT lanes.

The owner's focus, read from the day: the UI surface kolt is being written against — styles
(the `new_button_style` exploration: state as data attributes, colour as a custom property,
A89/B308/A84), positional slots (A85's paper, A46's fragment), the solver residue Order 32
left pinned (B300 blocks A86; B304 is kolt's `|event: Event|` workaround; B296 is an internal
error), and the daily loop (B276: kolt's watch reuses nothing; E106: the language server slows
over a session). Six lanes go on no ruling; two (slots-33, rpc-33) go only with one.

## Rulings at GO (owner) — the ones that change what a lane BUILDS
> **RULED 2026-09-11 (owner): all as recommended.** The recommendations below are the rulings.
- **R1 — A85's surface (slots-33 go/no-go).** The paper (`proposal/positional-slots.md` §9)
  asks: ship five value forms `when`/`swap`/`each`/`each_values`/`each_by` as structs with
  concretely-typed closure fields implementing `Slot`, the five parent methods as one-line
  sugar, render closures still returning `View`, no `Group`, B253 unchanged. Q1 `each` beside
  `bind_each` (rec yes); Q2 teach the split recognizer the value form (rec yes — a value-form
  `swap` silently stopping splitting is the worst failure mode); Q3 "a render closure may yield
  a `Slot`" as its own item (rec yes, file it; kolt rows 4 and 6 are the exhibits). Sizing M.
- **R2 — A46's form (slots-33).** Rec: the `List<View>` LITERAL lowering (S–M), as A46's own
  recommendation and the paper's §4 say; the multi-root `Group` stays out.
- **R3 — A88 (slots-33).** Rec: the boundary REMOVES what it placed — `Region::close` removes
  the live content on every form; kolt's overlay `defer(|| remove())` goes.
- **R4 — P1–P3, carried from Order 32 (rpc-33 go/no-go).** The SYNC unleased handle stub
  returning `RemoteSource<T>` with `Status::{Absent, Failed(RpcError)}`; server dedup by source
  identity with lease counting; std `Memo`; A79 in the same shape. Rec as in `briefs32.md`'s
  rpc-32 section, which this order's rpc-33 reuses verbatim. BREAKING for every handle stub.
- **R5 — B299 (solver-33's default is REFUSE).** `impl Source<type I: Source<type U>> { .. }`
  parses and then refuses every `self`. Rec: DESUGAR it to `impl type S: Source<..>` — the
  universal reading every other bare-trait value position already has (B186, B184), and the
  owner's own probe head means exactly that. Unruled → refused with a steer (safe; a desugar
  can follow without breaking anything).
- **R6 — A84 (styles-33 measures, the owner rules at the sweep).** Rec: data-attribute rules
  (A89's presence form) + custom properties, which is what `new_button_style` already spells;
  `Style::when`'s computed merge stays for the local case. No build in this order.
- Record-only defaults (written as built at the sweep unless the owner objects): P4 B287 NOT
  built; B273's binder-exempt boundary kept and B307's under-supply REFUSED (rpc-smalls-33
  builds the refusal — one row); B275's kolt fix is `.map(|on| i"{on}")` (no `Source<bool>`
  `AttrValue` arm); `View::link_to` kept; `Vec2` gains `length_squared`, no `Mul<f64>`;
  `Region` public (no visibility exists); A87 `Owner::release` NOT built; E163's devDependency
  ADDED (editor-33); E154 yes; E156 accept and document; A82's visitor lanes and sticky tag
  kept; A78's wiring refusal kept; B292's abandon-the-wave kept; B298 behind trait-typed-fields
  Q3, not this order.
- **File at GO (integrator):** A90 — `Color::var`/`Length::var` REFUSE a name without the
  leading `--` at const time (kolt wrote `var("button-color")` and got `var(button-color)`,
  which no browser resolves; the docs spell `var("--w")`) — styles-33's.

## Mechanics (every lane)
- Worktree `vilan/.claude/worktrees/<lane>` branched from `origin/next` (5a0d0b49); NEVER
  touch the main checkout; NEVER `git stash`; kill only PIDs you recorded; kolt
  (`~/code/kolt`) is READ-ONLY — read it for exhibits, copy nothing; the owner edits it live,
  so read it ONCE into your scratch and work from the copy.
- Lanes NEVER PUSH. The integrator pushes each lane branch at merge time (Order 32's rule).
- One commit per item, message = the CHANGELOG entry's first sentence; CHANGELOG entry under
  the right family with its marker (`<!-- family: breaking|miscompile|fix|feature|
  performance|tooling|diagnostics -->`); the parity gate is `--test release_scripts`. A
  refusal that newly fires on std, `examples/`, the corpus, the docs or kolt carries a
  `breaking` note naming the program.
- Diagnostics: a new message is a ledger row written `NEW` in
  `crates/vilan-cli/tests/diagnostics-ledger.tsv` (the integrator numbers; next id 415), an
  edited text is a row edit; every lane that adds or edits a row runs `--test
  diagnostics_ledger`; a message whose FIRING changes means `-p vilan-lsp` too.
- PIN LOCATION: attribute and type refusals in vilan-core `tests/inference/<module>.rs`
  (`main.rs` is `mod` declarations only — `traits.rs`, `bounds.rs`, `generics.rs`,
  `platform.rs`, `std_surface.rs` by subject); wire behaviour in vilan-cli `service_layer.rs`;
  reactive in `reactive_lifetimes.rs`/`reactive_channels.rs`; rows/children in `ui_rows.rs`;
  routing `router.rs`; styling `style_when.rs`/`style_chain_order.rs`/`hmr_css_matrix.rs`;
  editor in `crates/vilan-ide`/`crates/vilan-lsp` unit tests. Nothing in `vilan/test/` uses
  `[service]` — `--test examples` and `-p vilan-core --test docs` exercise the generator.
- Shared test files: ADD whole new `fn`s. An EXISTING fn you must edit is named in the
  report (the fold takes `--allow-edit`); the DOM stubs (`DOM_STUB`/`HARNESS`/`BOOT_HARNESS`/
  `STUB`) are hygiene-33's to consolidate FIRST — another lane that needs a stub change says
  so and edits the minimum.
- The split emission golden (`tests/split/golden`) moves on ANY change to what std::reactive or
  std::ui emits; regenerate it per `split.rs`'s ritual over YOUR tree and say so; the
  integrator regenerates once more over the merged tree.
- Tests: `cargo nextest run -p <crate> --test <name>` targeted; verify names with `ls
  crates/<crate>/tests/`; the whole `-p vilan-core` run is the merge gate, but `-p vilan-core
  -E 'test(every_std_module_is_clean_under_full_scan)'` IS yours (std edits). Lib-only `cargo
  build` while nextest runs. Clippy `--all-targets -D warnings`, `cargo fmt --all --check`,
  `vilan fmt` over any `.vl` touched, before you finish.
- A parser rule statement added anywhere bumps `RULE_STATEMENT_SITES`.
- Scratch: `scratchpad/<lane>/`; the scratchpad is shared — read nothing outside yours.
- Heredocs in their OWN shell call. A hand-composed generated block is brace-counted and
  smoke-compiled (`--test examples`) before the gates.
- No SendMessage: every interaction is in this brief; a question you cannot answer from source
  is an OPEN Q in the report and you build your recommendation.
- Perf claims: CPU time (`getrusage`) or callgrind Ir + loadavg, never wall.
- Report (final message): per item — commit sha, what landed, the pins (names), numbers;
  FINDS as candidate items with evidence; OPEN Qs; anything unfinished and why; corrections
  to this brief. Model: Opus.

## Lane solver-33 — TOP: the residue Order 32 pinned
Items: B300 (A86 rides on it), B304, B296, B305, B306, B299 (R5), B297; B286 droppable.
Build:
1. B300 — impl selection over a bounded subject: (a) the bound's ARGUMENT is not solved from
   the receiver for `impl type S: Source<type I> { fun f(self): SignalCell<I> }` (`outer.f()`
   "never fully determined"; annotated it runs — the annotation is doing the solver's work);
   (b) a NESTED bound `type I: Source<type U>` resolves the receiver to no concrete impl
   ("internal: a call resolved to `Source`'s requirement `get`, which has no body") even for
   a concrete `SignalCell<SignalCell<i32>>`. The two `#[ignore = "A86: …"]` pins in
   `inference/traits.rs` are the exhibits — un-ignore both. Sites: `impl_select.rs`
   (`subject_applies` :174, `subject_applies_at_arguments` :201, `bound_trait_ids` :276,
   `instantiation_agrees` :412) and `satisfies_trait_bound` (analyzer.rs ~4900, B275's threading
   is the model for the argument half). THEN A86: land `impl type S: Source<type I: Source<type
   U>> { fun flatten(self): SignalCell<U> }` and the `Option` form in reactive.vl (:890 is the
   cell-only impl to retire; the A4 pins are the control; ownership story unchanged) — the
   `or` census is NOT yours (rpc.vl is the rpc lanes'). If B300(b) will not fall, land (a),
   keep A86 open and say why.
2. B304 — a closure parameter is not typed from an INHERENT IMPL METHOD's expected closure
   type (`View::link_to` with `|event|` fails a process build; the byte-identical body as a
   free function compiles; `|event: Event|` fixes it). Find the impl-method path that skips
   `infer_closure_args_against_params`' fill (the `Self`-substitution context is the suspect);
   pin the un-annotated `link_to` body green on both platforms (`inference/platform.rs` and
   `modules.rs` pins B304 names are the red faces); kolt's `on:contextmenu(|event: Event|` and
   `remote_signal.vl`'s annotation are the exhibits.
3. B296 — two exposed `KeyedCell<str, Task>` fields both built `KeyedCell::new([])` → the
   internal error (one field compiles; a seeded list compiles). Repro in rpc-smalls-32's
   scratch is gone — rebuild it from the item; suspects: an unsolved `T` from `[]` unifying
   across two sites under `Keyed<K>` (B254/B258's name-keyed candidates) — pin the two-field
   shape green and the internal text as must-not-fire.
4. B305 — the `Expr::List` arm's `if Unknown { Vec::new() }` manufactures an ERASED `List` for a
   non-empty literal whose element is `Unknown` (B288 closed its struct-literal door upstream;
   the erasure is still made). Mint a slot as the empty path does; the infer differential and
   the corpus are the net; pin `[x]` over an unfilled `x` never typing as a bare `List`.
5. B306 — `bind_callee_own_generics` drops a failed reconcile silently. Record it as a
   candidate diagnostic deduped against the later check (B5's rule) or prove a later check
   always fires; pin a contradicting closure argument with NO later consumer.
6. B299 (R5 RULED: DESUGAR) — `impl Trait<..> { .. }` with a bare trait as the SUBJECT means
   `impl type S: Trait<..> { .. }` — the universal reading B186 (parameters) and B184 (fields)
   already give a bare trait; desugar at the impl-subject walk (mint the implicit binder the way
   B186's `implicit_generic_scopes` does), so `self` is the bound `S`. Pins: the owner's probe
   head `impl Source<Option<type _: Source<type U>>> { fun foo(self) .. }` compiles AND `self.get()`
   works in it; a body that needs `S` by name is told the spelling (one steer, no refusal); the
   spec's impl-subject rule (types.md §5.4) gains the sentence.
7. B297 — an unresolved name in an impl subject reports twice (`walk_trait_position_type_node`
   + the per-argument walk each prep a `prepped_type_locals` entry): walk once or dedupe by
   (span, name); pin one error; the `let` form is the control.
8. B286 (droppable) — solve a bound-introduced parameter from the bound's application when the
   argument is itself a parameter with that bound (`S: Source<T>` + `S` known → `T`); pin the
   generic-to-generic call; measure the solver cost (Ir on kolt's `check`).
Gates: `-p vilan-core --test inference --test infer_differential --test docs`; `-p vilan-cli
--test corpus --test service_layer --test examples --test reactive_lifetimes --test
diagnostics_ledger --test ci_ignored_pins`; std full-scan; `-p vilan-lsp` (firing changes).
Family: fix (B300/B304/B296/B305/B306), feature (A86), diagnostics (B299/B297).

## Lane styles-33 — A89, B308, A90, the A84 measurement
Items: A89, B308, A90 (filed at GO), A84 (MEASURE + one-page note, no build).
Build:
1. A89 — `attribute(self, name: str, value: Option<str>, inner: Style)` (style.vl:1470): `Some(v)`
   → `[name="v"]` as today, `None` → `[name]`; sweep every call site in std/docs/examples to
   `Some(..)` (kolt at the owner's word — count its sites in the report); `within` (:1380) takes
   the same `Option` for symmetry (say so if you decline). NEGATION, the owner's form: `fun
   not(self, inner: Style): Style` beside `hover` (:1339) — marks the inner's rules (a `!` in
   the condition slot of each rule key, or a flag on the value) and emits nothing; the
   immediately ENCLOSING condition combinator (`attribute`, `within`, `hover`/`focus`/`active`
   family, `pseudo` :1502) consumes the mark, emits its own selector NEGATED, clears it.
   `attribute("disabled", None, not(hover(S)))` → `.sX:not([disabled]):hover`; `hover(not(S))`
   → `.sX:not(:hover)`. Refused at const time (curated, one row each or one row with a hole):
   an UNWRAPPED `not` reaching application, `not(not(S))`, a `not` directly under a media
   condition (`md`/`dark`) in v1. The `css` block's nested `.not { .. }` lowers to it by the
   name-blind rule (elements.rs's css desugar is name-blind — verify nothing lists combinator
   names; `STYLE_CONDITION_METHODS` in the completion tables gains `not` and `attribute`'s new
   arity). `child_relation`'s message (:1443) gains the steer "for a state on the element
   itself, `attribute(..)`". Pins (`style_when.rs`/`style_chain_order.rs`, new fns): presence,
   `Some` control, the two negation spellings, the three refusals, the css-block spelling,
   specificity `(0,3,0)` over `(0,2,0)`. Docs: guide/styling.md's condition table (+2 rows),
   std/style.md.
2. B308 — `Style::rule` (:935) emits at CONSTRUCTION, so every intermediate style in a condition
   nest puts a dead rule on the sheet (`attribute(.., hover(S))`: the inner `hover` style's
   `.sY:hover{..}` beside the composed `.sX[..]:hover{..}`; measured two of five rules dead on a
   two-level probe). Fix: emit at APPLICATION — `rule` records `(class, rendered)` on the
   `Style` beside `rules`; the sheet receives a style's rendered rules when it is applied
   (`styled`/the element-syntax class path) or when a `Style` is bound at module level / from a
   `const` (the plateau the model already relies on); a combinator does not carry the inner's
   rendered rules forward. The `emit("css", ..)` channel is const_eval.rs's — read how the CLI
   collects it (`hmr_css_matrix.rs`, `ssr_differential.rs` are the gates) before moving it; if
   application-time emission needs the CLI's collector to change, say so and price it. Measure
   kolt's sheet before/after (bytes; rules whose class is absent from the bundle — the probe's
   method) and the split fixture. Pins: a two-level nest emits exactly the composed rule; a
   standalone `hover` style still emits when applied itself (control); `hmr_css_matrix`,
   `ssr_differential`, `split` green (regenerate the split golden per the ritual if the sheet
   bytes move).
3. A90 — `Color::var`/`Length::var` (:200/:128) refuse a name that does not start with `--` at
   const time (curated, one row): "a custom property is written with its dashes —
   `var(\"--button-color\")`"; pin the refusal and the `--` control; `view.style_var` (browser/
   ui.vl:160) takes the same check if it writes the property name verbatim.
4. `Vec2::length_squared` (record-only ruling): the no-sqrt threshold form beside `length` in
   std/math.vl, one pin, one doc row; no `Mul<f64>`.
5. A84 MEASURE — kolt's `button_style` (styles.vl:44) across its flag space under the current
   computed `when` merge (:1591): count classes and rule bytes per distinct combination, then
   the same surface as (a) `data-` attribute rules (A89's form — `new_button_style` is the
   author's own draft) and (b) custom properties; a one-page note in your report with the
   numbers and a recommendation (rec: (a) + (b) as `new_button_style` spells it; `when` stays
   for the local case); NO build.
Gates: `-p vilan-cli --test style_when --test style_chain_order --test hmr_css_matrix --test
ssr_differential --test split --test corpus --test release_scripts --test diagnostics_ledger`;
`-p vilan-core --test inference --test docs`; std full-scan; `-p vilan-lsp` (completion tables).
Family: feature (A89, A90), fix (B308), diagnostics.

## Lane rpc-smalls-33 — B295, B303, B301, B307, N70, B287 (P4 RULED: refuse)
Build:
1. B295 — QUALIFY the free calls in generated stubs (`rpc::call(..)`, `rpc::notify(..)` — the
   import list at rpc.vl ~4993 is where the bare names come from) so an `[rpc]` method named
   `call` or a `[client_service]` method named `notify` builds and round-trips; REFUSE an
   `[rpc]` parameter whose name starts with `__` (one row). Pins in `service_layer`.
2. B303 — the `[rpc]` signature refusal stands the generated stub's `call<T: Wire>` bound
   failures down (B189's mechanism / A56's `expose_refused_key_bounds` shape); pin: one report
   for a non-Wire return.
3. B301 — `[derive(Wire)]` emits the JSON impls beside Wire (`derive_impl_source`, analyzer.rs
   :47774, the `"Json" | "Wire"` arm "additive until the codec re-plumb consumes it"): finish
   the re-plumb — `[derive(Wire)]` emits the Wire visitor impls alone, `[derive(Json)]` the JSON
   pair, `[derive(Json, Wire)]` both; the derive's field check reads B289's predicate. Flip
   wire-32's two current-behaviour pins (`a_derive_wire_field_typed_map_meets_the_same_pre_
   existing_json_residue`, `a_derive_wire_field_may_be_a_hand_implemented_wire_type`) to the
   admit face — those are the two EXISTING fns you may edit; a `[derive(Json, Wire)]` control.
   CENSUS first: every `[derive(Wire)]` in std/examples/docs/kolt that RELIES on the JSON impls
   (a `.to_json()` on a Wire type) — each is a `breaking` note or a `[derive(Json, Wire)]`
   edit in std/examples; kolt's are listed for the owner.
4. B307 — under-supply `impl DogBox with Holder` (a bounded, non-defaulted trait parameter left
   unwritten) is padded by `effective_trait_arguments_of`: REFUSE it as an arity error (B188's
   row, or its sibling naming the elision); a defaulted parameter stays elidable; census std/
   docs/examples/kolt first and report every site the refusal hits before choosing the text.
5. N70 — `analyzer::service_impl_source`, the Rust fallback `[service]` generator, is a stale
   twin: TOMBSTONE it (the fixture stds without rpc.vl are the only reach — make them carry
   rpc.vl or make the fallback refuse with "std without `rpc.vl` cannot expand `[service]`")
   rather than sync it; say which.
6. B287 (P4 RULED refuse) — `async` + `&mut self` on an `[rpc]` method refused at expansion (the
   `service` macro; row 408's `mut self` refusal is the model), one row, must-fail pin; the
   guide caveat becomes "refused".
Gates: `-p vilan-core --test inference --test docs`; `-p vilan-cli --test service_layer --test
rpc_http --test examples --test corpus --test release_scripts --test diagnostics_ledger`; std
full-scan; `-p vilan-lsp`. Family: fix, diagnostics, breaking (B301's census hits).

## Lane dx-33 — the daily loop: B276, E106, M58
Build:
1. B276 — a bundling leg is never `Fresh` under `build --watch`: `asset::bundle` records
   `content_hash_bytes(&bytes)` (const_eval.rs ~487) while `current_source_hash`
   (vilan-cli main.rs:4818) re-hashes with `read_source` + `content_hash`, so `leg_is_current`
   (hmr.rs:745) always fails. ONE hash function for both sides; pin a bundling leg `Fresh` on an
   unchanged round (`watch_leg_reuse.rs` is the binary; kolt's shape — a bundled `lucide` —
   is the exhibit, rebuilt as a fixture). Measure kolt's second watch round before/after (CPU).
2. E106 — the language server slows over a session. MEASURE FIRST, on kolt: drive 2,000
   keystrokes through the LSP harness (`keystroke.rs`'s driver; `session_trace.rs`) and record
   per-100-keystroke medians of the analyze phase and RSS; if the deliberate per-analysis leak
   (`leak_measurement`-bounded: entry text + AST) is the growth, bound it (an arena reused per
   document, or a generation cap that frees the previous world's leaks when the next lands);
   if S5's per-request re-parses are, say so and queue. Pin the growth: the 2,000th keystroke's
   analyze median within 1.5× of the 100th (CPU, not wall — M27's rule); RSS bounded.
3. M58 — profile a WARM re-analysis of kolt's client on the `profiling` profile (the keystroke
   path is the warm shape; every lane profile so far was cold): name the top five warm items
   with Ir, land the largest if it is a day's work (`post_analysis_passes`, lib.rs:750, is
   57–63% of warm), else file it with the profile attached in your scratch and the numbers in
   the report.
Gates: `-p vilan-cli --test watch_leg_reuse --test watch_lifecycle --test hmr --test
perf_baseline --test corpus --test release_scripts`; `-p vilan-core --test phase_timing`;
`-p vilan-lsp`. Family: fix (B276, E106), performance.

## Lane editor-33 — E160, E163 (ruled), E162, E157, E159, E154 (ruled), E158
Build:
1. E160 — completion inside a STRUCT INITIALIZER: a `StructInitializer { struct_id, written }`
   `CursorContext` arm (vilan-ide `completion.rs` ~975) recognised from the token stream
   (`Name {` … cursor at a field position, comma-separated, `=` not yet typed); candidates are
   the struct's fields minus the written ones, inserting `name = ` (bare `name` when a
   same-named binding is in scope — the shorthand), the field's type and doc as detail; nested
   initializers resolve to the inner struct; generic structs through the declaration. Pins
   beside `member_completion_lists_fields_and_methods`; kolt `store.vl`'s `KoltStore { .. }` is
   the exhibit.
2. E163 — `vscode-textmate` + `vscode-oniguruma` as extension devDependencies (lockfile;
   THIRD-PARTY-NOTICES if the notices gate reads devDependencies — check `third_party_notices
   .rs`); a `tokenize.js` under `crates/vilan-cli/tests/support/` loading the grammar with the
   wasm onig; rewrite E161's five regex pins as SCOPE assertions over the exhibit (`<div>` and
   `a < b` as controls). If the notices gate or `npm ci` in CI makes this an L, STOP and report
   the price.
3. E162 — a nested `[`…`]` sub-rule inside `meta.generic.vilan` so `SignalCell<[i32; 4]>` does not
   end the list at `;`; one pin beside E161's (a scope pin once E163 lands, a regex pin else).
4. E157 — a block-like head followed by `::` (`match x {..}::foo`) gets its own arm instead of
   B248's parenthesize steer; pin the message.
5. E159 — a docs parity gate: every std enum fragment the docs show lists every arm std declares
   (the `style_table_sync` idiom); pin on `RpcError` and `Reject`.
6. E154 (ruled yes) — `for x in <iterable>` heads take the split permission `for` conditions and
   `match` subjects have (E150 rule B); formatter pin; `vilan fmt --check vilan/` green.
7. E156 (ruled: accept and document) — one paragraph at E151's attribute-sorting rule in the
   formatter docs: sorting reorders WHEN attribute values run; a side-effecting attribute value
   is the smell, not the sorter's; no code change.
8. E158 — `references.rs`'s `narrow` and every DERIVED-span table: the sweep B264 asked for;
   `is_namespace_module`'s thin discriminator gets a real marker if a third `SourceId(0)`
   entity exists — else document.
Gates: `-p vilan-ide`; `-p vilan-lsp`; `-p vilan-cli --test grammar_sync --test grammar_ebnf
--test vscode_extension --test third_party_notices --test release_scripts --test
diagnostics_ledger`; `-p vilan-core --test docs --test markdown_golden`. Family: tooling,
editor, diagnostics.

## Lane hygiene-33 — DROPPABLE, lands FIRST: N73, N71, N72, M61, N69, N68, N65
Build:
1. N73 — one DOM stub under `crates/vilan-cli/tests/support/` (a Rust const or a `.js` file
   read at test time) with the per-file extras layered on (`byId`, `find`/`findAll`, `page()`);
   `ui_rows.rs`, `reactive_lifetimes.rs`, `source_bindings.rs`, `ssr_differential.rs`,
   `ssr_fullstack.rs`, `router.rs`, `split.rs` and the eighth include it. Behaviour-neutral:
   every gate in those binaries green with no test edited beyond the include.
2. N71 — a harness seam to OBSERVE a free-task failure (an env-gated collector on the runtime's
   free-task failure path, or a test-only `on_task_failure` extern); then pin B277's throwing
   callback shape in `debounce.rs`.
3. N72 — `tuples::nested_nurseries_join_inside_out`: decide whether the join order is promised
   (a runtime race to fix) or not (assert the set + the inner-before-outer-done invariant);
   fix the pin or the runtime, say which.
4. M61 — measure `__with_finally`/`__guarded`'s bundle weight on kolt's browser bundle and the
   split fixture (bytes, minified and gzipped); fold or leave, with the number.
5. N69 — `element_view_import_note` (analyzer.rs ~21871) is unreachable after B270 whenever std
   holds `ui::view`: delete it or make it reachable; pin whichever.
6. N68 — `service_layer.rs:1667`'s 2,500 ms wall bound on a raw handshake: retries or CPU, per
   N61's rule.
7. N65 — the ledger gate enumerates parser CURATED rule statements (`CSS_BLOCK_IS_BRACE_INITIAL`,
   `IMPORTANT_HAS_NO_PLACE`, E153's `:hover` rule) so a "row EDIT" has a row to edit; and the
   `resource_derive_r*` naming the item lists.
Gates: `-p vilan-cli --test ui_rows --test reactive_lifetimes --test source_bindings --test
ssr_differential --test ssr_fullstack --test router --test split --test debounce --test
service_layer --test diagnostics_ledger --test release_scripts`; `-p vilan-core --lib`; std
full-scan. Family: tooling, fix.

## Lane slots-33 — GO (R1–R3 RULED as recommended): the A85 build, A46, A88
Build (per `proposal/positional-slots.md` §3, §4, §8):
1. A85 — `Conditional<S>`, `Swap<T, S>`, `Each<T, K, S>` (+ `EachValues`, `EachBy`) as structs
   with CONCRETELY-TYPED closure fields (§5: PROBE FIRST that a struct field typed as a
   context-carrying closure `(sync || View) context owner_scope` compiles and captures at the
   right site — if not, the value forms take a plain closure and the owner scope is entered in
   `place`; say which), each `impl .. with Slot` whose `place(parent)` opens a `Region` and runs
   the method's existing body; free functions `when`/`swap`/`each`/`each_values`/`each_by` in
   `std::ui`; the five parent methods become `self.child(when(..))` one-liners (signatures
   unchanged, no migration); process twin same names, no anchor; ownership unchanged. THE
   SPLIT GATE (§8.1): `chunks.rs:90` finds `View::swap` by method name and rewrites it to
   `swap_split`; `platform_color.rs:248` reads it — teach both the value form (`Swap` built by
   `swap(route, render)`), pin in `split.rs` that a value-form route swap still splits (RED
   FIRST: the bundle whole = the failure). Docs: guide/ui.md (the child contract and the three
   forms), std/browser.md, guide/routing.md (the page container is the exhibit everyone copies).
   Pins (`ui_rows.rs`): each value form in a middle position (A71's five are the template);
   `ssr_differential`.
2. A46 (R2) — `<>..</>` lowers to a `List<View>` LITERAL: the parser's second gate (`'<'` then an
   adjacent `'>'`), `parse_element_inner`'s nameless arm, `parse_element_children` accepting
   `</>`; `build_chain` emits `Node::List(children)`; runtime nothing (the `List<View>` Slot arm
   and, reactive, the `Source<List<View>>` arm with A71's region keep position). Documented limit:
   the fragment's TYPE is `List<View>` — legal in child position and wherever a list is; not as
   a `fun ..: View` return. Grammar spec (element-syntax S2/§7 reversed), `grammar_ebnf`,
   `grammar_sync` (the `<>` token — a fused pair? check `TWO_CHARACTER_OPERATORS`; if the lexer
   gains one, the three-place rule applies), formatter (E150 rules for the empty head), pins.
3. A88 (R3) — `Region::close` REMOVES the live content on every form (`when`, `swap`,
   `bind_each` ×3, the reactive arms) at boundary disposal; pin: a `when` inside a portal whose
   parent survives leaves nothing behind after the owner disposes; `ssr_differential` unchanged;
   kolt's overlay `defer(|| live_panel.remove())` becomes redundant (report it; no kolt edit).
Gates: `-p vilan-cli --test ui_rows --test router --test ssr_differential --test ssr_fullstack
--test split --test corpus --test grammar_ebnf --test grammar_sync --test release_scripts`;
`-p vilan-core --test docs --test markdown_golden --test parse_expr_regression`; std full-scan.
Family: feature (A85, A46), fix (A88).

## Lane rpc-33 — GO (R4 RULED: P1–P3 as recommended): A92 (the sync unleased handle stub) + A79
The brief is `briefs32.md`'s "Lane rpc-32" section, verbatim, with two updates: RE-ANCHOR the
rpc.vl line numbers (A78 added `Dispatcher.handle_methods`/`RpcProtocol.handle_methods` and
`no_connection_for_handle` in the 1184–1440 region and the generated chain gained `.handles(..)`
— `grep -n` every cited fn before editing), and the `Memo`'s home is `std::collections` unless
you argue otherwise. Gates and pins as written there. Family: feature; BREAKING (every handle
stub's type — the entry names it; kolt's model.vl migrates at the owner's word).

## Ownership map (conflict avoidance)
- analyzer.rs: solver-33 owns the impl-selection and closure sites (impl_select.rs whole;
  `satisfies_trait_bound` ~4900; `infer_closure_args_against_params` ~29119; the `Expr::List`
  arm; `bind_callee_own_generics`; the impl-subject walk); rpc-smalls-33 owns
  `derive_impl_source` (:47774), the `[rpc]` refusal stand-down (~14850–14890) and
  `effective_trait_arguments_of`; hygiene-33 owns `element_view_import_note` (~21871). No two
  lanes in one fn.
- rpc.vl: rpc-smalls-33 (the generator's import list ~4993, the stub's method names, the
  `service` macro's receiver check for B287); rpc-33 (`expose_dynamic`, `Status`/`RemoteSource`,
  `handle_element`, the stub's handle arm) — separate regions; the integrator resolves.
- style.vl, const_eval.rs's css emit channel, the CLI's css collector: styles-33 only.
- reactive.vl: solver-33 for A86's `flatten` only (:890). browser/ui.vl, process/ui.vl,
  elements.rs, parsing.rs's element gate, chunks.rs, platform_color.rs: slots-33 (editor-33's
  E157/E154 are formatter.rs and parsing.rs's OTHER arms — say which lines; no shared fn).
- vilan-cli hmr.rs/main.rs hashing, vilan-lsp's document lifecycle, lib.rs profiling: dx-33.
- vilan-ide completion.rs/references.rs, formatter.rs (E157/E154), editors/, docs tests:
  editor-33.
- `crates/vilan-cli/tests/support/` and the eight stub consts: hygiene-33 FIRST.
- Landing order (integrator): hygiene-33 → editor-33 → styles-33 → rpc-smalls-33 → dx-33 →
  solver-33 → slots-33 → rpc-33 (the conditional two last; the largest last). After the
  merges: regenerate the split golden once over the merged tree; grep every `Name {` a lane
  added a field to.

## At the sweep (integrator, proposals)
- Close: B300 B304 B296 B305 B306 B299 B297 (B286 if built) A86 (if landed) · A89 B308 A90 ·
  B295 B303 B301 B307 N70 B287 · B276 E106 M58 (or filed residue) · E160 E163 E162 E157 E159
  E154 E156 E158 · N73 N71 N72 M61 N69 N68 N65 · A85 A46 A88 · A92 A79. A91 stays open (after
  A85); A87 stays open, declined until a caller appears.
- A84's ruling from styles-33's numbers; css-block.md/ui-styling.md as-built notes for A89/
  B308 (the `not` marker, the application-time sheet); positional-slots.md §10 as-built;
  transport-rpc §9.6 if rpc-33 went.
- Kolt follow-ups at the owner's word: views.vl:57 (`.map`), the three `remote_signal`
  annotations, `store.vl:27`'s impl, `var("--button-color")`, `child_relation` → `attribute`
  + `not`, overlay's manual remove (A88), `on:contextmenu`'s annotation (B304), the migration
  to A59/A60/B268/A62 still owed.
- The cut (HELD since Order 29): the owner tests kolt on the seal — reinstall BOTH `vilan`
  and `vilan-lsp` — then the changelog train ships (303 entries at Order 32's seal).
