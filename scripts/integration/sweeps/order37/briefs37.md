# Order 37 — the native foundations, the css call surface, and the honest tools (drafted 2026-09-17; GO 2026-09-17, off vilan next @d783fbf4)

**GO (2026-09-17).** The owner: "Provided none of the above requires clarification or blocks
the order, you may begin (go)" — with two steers that AMEND the record. (1) The native path is
"just setting up the Rust backend supporting cli programs for now"; drawing windows "is much
more complicated" and waits for a design conversation the owner wants first — how to write UI
code that works for native and web simultaneously, with named exceptions such as native
close/minimize/maximize buttons (F17 filed as that DISCUSSION; nothing in F1 S3–S5 starts
before it); and native WEB SERVERS are "more easily achievable in the short term" and "a huge
win in and of itself" — so the slice after S1a is native servers, not the render layer (F18
filed; native-apps.md §8 Q2's "`native` does not join `@process`" is REVISITED there — a
server is exactly the `@process` family on the Rust backend; native-b-37 sizes it in its
report). (2) A fresh sweep of kolt's TODO/FIXME/HACK comments (46 lines at kolt 0decf84): 12
items filed at GO (A104–A107, B352, B353, E191–E193, I4, F17, F18), three stamps (A72, I3, A8),
and 14 comments found STALE against std that already shipped (A59, A60, A62, A82, A83, B268,
B340, `std::fetch::post(..).send()`) — kolt's migrations at the owner's word, listed at the
sweep. RULINGS: R1–R13 as recommended, with R2 AMENDED (emit Rust ratified; "desktop first"
replaced by CLI programs → servers → the UI layer after the F17 conversation) and R4 RECORDED
only (the three-layer rule is part of that conversation; S2's sizing moves with it). Lane
additions at GO: solver-37 += B352, B353; diagnostics-37 += E191; editor-37 += E192, E193;
native-b-37's report sizes F18. TEN lanes. Order 36 sealed at d783fbf4 (CI green on all eleven
jobs; toolchain at that sha in both locations; nothing has landed on `next` since). Ledger
next id 500. Tracker 120 open at GO. Kolt committed at 0decf84; the website's seven `export *;`
files are still uncommitted (the owner's).

The shape, read from what Order 36 left and what the owner owes: the two native papers landed
with recommendations, and the rulings that turn them into code are this order's gate — C14's
counted `Shared` (its first three slices land on JS and are proved by the SCC gate that already
ships) and F1's first slice (the emit-Rust backend and its runtime crate, behind C16's refusal,
scoped to what the probe already translated). The owner's own css-block redesign A101 is the
order's one BREAKING surface (138 blocks per the filing; kolt's at the owner's word), merged
LAST as one revertible diff with E183 riding on it. Around them: the A99-reachable solver
family B351/B347 (kolt's FIXME at views.vl:94), the lazy paper's third slice A103 with its two
corners, the two diagnostics kolt's upgrade exposed (E189's 173-error cascade, E190's span-less
refusal) beside E185 and B343, the editor's spec-generated attribute completion E69 with the
fourth consumer E184, the kolt-keystroke perf pair M72/M73, and two hygiene lanes — one for
rot, one for the three tools that lie (`fmt --check`, `vilan check`'s cache, `VILAN_STD`).

## Rulings at GO (owner) — the ones that change what a lane BUILDS
- **R1 — C14's representation (native-a-37).** The paper recommends (a): `Shared<T>` becomes
  the counted resource destruction.md §10 already specifies — retain on clone, release at last
  use on Tier 1's dataflow, `Weak<T>` (C1) at exactly two std sites (`observe`'s captured cell,
  `Subscription`'s alias of the subscriber list); `Arena`/`Handle` unchanged. Rec: (a). The
  census is the argument: NO owner owns a cell today, so (b) would invent an ownership relation
  at 126 sites and turn `Source::get` into `Option<T>` (breaking, estate-wide). This order
  builds S1–S3, all on JS and proved by the SCC gate; S4 (the counted lowering) waits for F1's
  backend; S5 (the JS counted instrument) is optional and queued.
- **R2 — F1's four answers, ratified for the BUILD (native-b-37).** The paper assumed (Order
  36's R10) and then argued: emit Rust; desktop first; the DOM-shaped `View` as a third
  `std::ui` twin; client-only first with rpc in-process later. Rec: ratify all four as the
  build's premises; the costed rejections (C, wasm-in-a-host, the interpreter, a retained-tree
  API) stand as written. **GO AMENDMENT:** "desktop first" is REPLACED — the order of native
  products is CLI programs (S1a, this order) → native web servers (F18, Order 38) → the UI layer
  only after the F17 conversation; "emit Rust", the DOM-shaped `View` twin as the STARTING
  position for that conversation, and client-only-first stand.
- **R3 — rule 4 under rustc (native-b-37).** rustc sees aliasing the vilan checker already
  proved safe. Rec: ship `RefCell` for S1 and MEASURE (the count of boxed bindings over the exit
  corpus, recorded on the item); a violated invariant is a panic with a message, which is
  honest; `unsafe` with a soundness argument is a later optimisation paid for by that
  measurement. C15's capture-mode analysis (by-value copies for bindings never written after
  capture) is the same later item — v1 boxes every mutably-captured binding.
- **R4 — the three-layer `std::ui` rule (F15) — record now, build with S2.** Rec: rule it as
  native-apps.md §6.2 states it — one surface, N twins; a member added to one twin is added to
  all in the same commit or refused by the gate; the parity gate becomes N-way;
  `ssr_differential` compares resolved structure for a native leg. NOT built this order (S2 is
  Order 38's); the ruling is what lets S2 be sized. **GO: RECORDED, not ruled** — the
  three-layer rule is part of the F17 conversation, and S2's sizing waits with it.
- **R5 — async on native (J6).** Rec: `Task<T>` stays `external`, bound to a single-threaded
  executor in `vilan-rt` matching the JS turn model (reactive-turns.md); cancellation via the
  Nursery's drop. S1a builds NO async (its scope excludes it); the lane writes the executor's
  design as a section of its report for native-apps.md.
- **R6 — `i53`/`u53` on native.** Rec: distinct types with native widths `i64`/`u64` and the
  documented note that the RANGE guarantee is the JS one, so a program round-tripping both
  backends behaves the same (kolt's ids are `i53`).
- **R7 — C16 blocks S1.** Rec: yes — the captured view of a dead local is the one filed item
  that turns into memory unsafety rather than a behaviour change under a non-GC backend;
  native-b-37 lands the refusal FIRST; the exit corpus contains no such program.
- **R8 — `vilan-rt` and the debug default.** Rec: a new workspace crate `vilan-rt` with NO
  dependencies beyond Rust's std (AGENTS.md's stop condition holds; the render stack is S3's
  separate crate, later); `vilan run --backend rust` builds debug by default and the CLI help
  says so.
- **R9 — B343: where the `context` clause sits (diagnostics-37).** Rec: KEEP it after the
  return type (contexts.md §3's choice; 0 std / 1 kolt / 2 docs declaration sites either way);
  REFUSE the one ambiguous form — an un-parenthesized closure-typed return carrying a clause
  (`fun f(): || void context c`) — with the steer "parenthesize the closure type to give it its
  own clause: `fun f(): (|| void context d) context c`" (one row; a quick fix); fix the
  TextMate lookbehind (today `context` paints as an identifier after a return type) and the
  book theme's copy; grammar_sync scope pins for both shapes. Alternative: move it before the
  `:` — cheap today, never cheaper, but the declaration then reads unlike the type it declares.
- **R10 — A101 Q1: N arguments (css-37).** `margin(px(4), px(8))` — how N arguments become ONE
  raw value. Rec: joined by a single SPACE (CSS's own list separator); a comma-separated CSS
  value is ONE argument (a string today; a `list(..)` helper is a later item); the desugar stays
  "exactly one `.raw(name, value)` per declaration" — `raw`'s arity does not change.
- **R11 — A101 Q2: what the codemod writes (css-37).** Rec: the TYPED constructor where
  E167's converter already types the value (`width: 100%;` → `width(pct(100));`), the string
  literal where it does not (`font-family: "Inter", sans-serif;` →
  `font-family("\"Inter\", sans-serif");`); the lowering-identity gate makes the two
  byte-identical, so the choice is readability only; kolt's blocks (28 per the filing;
  re-census read-only) at the owner's word, the integrator at the sweep.
- **R12 — A101 Q3: custom properties (css-37).** Rec: `--name(value);` is admitted on the
  property side (the `property` production already admits leading hyphens, as element
  attributes do); on the VALUE side CSS's `var(--x)` is spelled `var("--x")` — a `std::style`
  value function (add it if missing, S) — because `--x` is not an expression.
- **R13 — A102: `lazy let` under HMR (lazy-37).** Rec: transfer the cell only when
  `state == done` (the value survives, the thunk is dropped); a pending or poisoned binding stays
  `Excluded`; pinned under the HMR round harness.
- Record-only defaults (written as built at the sweep unless the owner objects): F1 S2 (the
  `native` platform's eleven registration sites, E182, F15's N-way gate) and S3–S6 are NOT this
  order; C14 S4/S5 queued; N97 MEASURES the walk's frame and plants the canary — the walk's
  SPLIT is a separate item if the measurement says so (five lanes share analyzer.rs this
  order); E69's generator reads a VENDORED spec extract (no network inside a gate); B348 and
  B298 stay behind their questions; A87 stays declined (C14 §11 Q4 re-affirms it); A94, M60,
  M56/M57/M54 and E121's remaining path are not this order; K14's website branch and its
  `Prelude: web` option merge at the v0.41.0 cut, which stays HELD (the owner's call); L20 is
  the owner's own; kolt is READ-ONLY to lanes — its css blocks, the B351 FIXME (views.vl:94)
  and any B347 annotation are the integrator's at the sweep at the owner's word.

## Mechanics (every lane)
- Worktree `vilan/.claude/worktrees/<lane>` branched from `origin/next` (d783fbf4); NEVER
  touch the main checkout; NEVER `git stash`; kill only PIDs you recorded; kolt
  (`~/code/kolt`, committed at 0decf84) is READ-ONLY — read it ONCE into your scratch and work
  from the copy. The proposals repo (`~/code/vilan-lang/proposals`) is READ-ONLY too: papers
  and the probe crate (`projects/vilan/proposal/native-apps-probe/`) are read there; anything
  you would write there is handed back in the report.
- Lanes NEVER PUSH. The integrator pushes each lane branch at merge time. Commit as the
  worktree's configured identity (the push hook refuses a `Claude` author; never pass
  `--author` or set `GIT_AUTHOR_*`).
- One commit per item (a slice may take several, each buildable), message = the CHANGELOG
  entry's first sentence; CHANGELOG entry under the right family with its marker
  (`<!-- family: breaking|miscompile|fix|feature|performance|tooling|diagnostics -->`); the
  parity gate is `--test release_scripts`. A refusal that newly fires on std, `examples/`, the
  corpus, the docs or kolt carries a `breaking` note naming the program. Breaking items this
  order: A101 (the codemod), C16's refusal (if an estate program fires — expected none), B345's
  widened scan (if it fires), A103's retrofit (a behaviour change, gated by the differential —
  any observable difference is stop-and-decide, not a note); each carries its migration note.
- Diagnostics: a new message is a ledger row written `NEW` in
  `crates/vilan-cli/tests/diagnostics-ledger.tsv` (the integrator numbers; next id 500 —
  NEVER write a literal id), an edited text is a row edit, a RETIRED row is a deletion named in
  the report; every lane that touches a row runs `--test diagnostics_ledger`; a message whose
  FIRING changes means `-p vilan-lsp` too. The proposals `diagnostics-ledger.md` is the audit
  paper — the integrator re-keys it at the sweep from your report. N94's three-space gate
  (hygiene-37) will fire on any new literal carrying a swallowed continuation — write
  concatenated lines.
- A named parser rule constant needs TWO edits: `RULE_STATEMENT_SITES` AND
  `CURATED_RULE_STATEMENTS`. Two lanes touch parser rules this order (css-37 deletes the css
  value productions and adds two; diagnostics-37 may add B343's refusal): report the DELTA
  (+n/−n) — the merge tools (N81) SUM a same-named integer const through the merge base and
  REFUSE any other edited const not named in `--allow-edit`, so name every const you edit.
- No keyword lands this order. The TextMate grammar is edited by css-37 (the css-block rules)
  and diagnostics-37 (the `context` lookbehind) — different rules, named in both reports.
- PIN LOCATION: attribute and type refusals in vilan-core `tests/inference/<module>.rs`
  (`lazy.rs`, `callable.rs`, `const_eval.rs`, `styling.rs`, `platform.rs`, `borrows.rs`,
  `lifetimes.rs`, `modules.rs`, …); module resolution in `tests/module_resolution.rs`; wire
  behaviour in vilan-cli `service_layer.rs`; reactive in `reactive_lifetimes.rs`/
  `reactive_channels.rs`; rows/children in `ui_rows.rs`; styling `style_when.rs`/
  `style_chain_order.rs`/`hmr_css_matrix.rs`/`ssr_differential.rs` + vilan-core
  `inference/styling.rs`; HMR transfer in `hmr.rs`/`hmr_swap.rs`; the TextMate scope pins in
  `grammar_sync.rs` (they need `npm ci --prefix editors/vscode` in YOUR worktree; `CI=true`
  makes a skip a failure); vilan-lsp/vilan-ide pins are `mod tests` inside `src/*.rs`
  (formatter pins run as `-p vilan-core --lib`); the deep-fixture harness is
  `tests/deep_nesting.rs`.
- Shared test files: ADD whole new `fn`s. An EXISTING fn you must edit is named in the report;
  a program CONST edited beside its pin is named too (the merge tool refuses an unnamed const
  edit); a multi-line string const whose first line ends in `"\` must be REWRITTEN as
  concatenated lines. Report every `--test` name WITH its crate (Order 36 lost two merges to
  `book_sync`/`docs` named without one).
- Goldens (split/corpus/markdown/`.css`) move on ANY change to what std::reactive/std::ui/
  std::style emit; regenerate per the ritual over YOUR tree and say so; the integrator
  regenerates once more over the merged tree. Lanes expected to move goldens: native-a-37
  (`__shared_new` count −19 in S1; S2/S3 change reactive.vl's emitted body), css-37 (none if the
  lowering identity holds — a moved `.css` golden is a FINDING, not a regeneration); no other
  lane may move one without saying why.
- An estate sweep names EVERY crate with `.vl` fixtures — vilan-core, vilan-cli, vilan-lsp
  (`mod tests`), vilan-ide, vilan-wasm (Order 36 missed it), `vilan/test`, `vilan/docs`,
  `vilan/examples`, `vilan/benchmarks`, the `vilan init` templates.
- Tests: `cargo nextest run -p <crate> --test <name>` targeted (`-p A -p B --test X` applies
  `--test X` to EVERY package — run packages separately); the whole `-p vilan-core` run is the
  merge gate; `-p vilan-core -E 'test(every_std_module_is_clean_under_full_scan)'` IS yours
  (std edits). Clippy `--all-targets -D warnings`, `cargo fmt --all --check`, `vilan fmt` over
  any `.vl` touched. The suite runs on 8 MiB test threads (`.cargo/config.toml`, N97) — do not
  raise it further; a deeper frame is a finding. The inference harness writes under `target/`
  (N82); the other binaries still write to the tmpfs until hygiene-37 lands N86 — an ENOSPC red
  is re-run once before it is believed. The ci-local console prints NO `FAIL` line for an
  ABORT — grep nextest's `ABORT` marker. `cargo build --release` is allowlisted for lanes.
- Scratch: `scratchpad/<lane>/`; the scratchpad is shared — read nothing outside yours.
- Heredocs in their OWN shell call. No SendMessage — a question you cannot answer from source
  is an OPEN Q in the report and you build your recommendation. Perf claims: CPU time or
  callgrind Ir + loadavg, never wall.
- Report (final message): per item/slice — commit sha, what landed, the pins (crate + test
  name), numbers; FINDS as candidate items with evidence; OPEN Qs; anything unfinished and why;
  corrections to this brief. Model: Opus.

## Lane hygiene-37 — DROPPABLE, lands FIRST: N94, N95, N96, N87, N88, N89, N86, N97 (measure + canary)
Read each item; `diagnostics_ledger.rs` (its check (3), the vacuity pins), `docs.rs` (the
tour's reserved-word gate), `build_impl_admission` (analyzer.rs ~58999), `deep_nesting.rs`,
`walk_expr_node_inner` (analyzer.rs ~27721), N82's three helpers in the inference harness
(`scratch_root`/`scratch_dir`/`ScratchFile`).
1. **N94** — fix the two swallowed continuations (`const_eval.rs` ~723 user-facing;
   `analyzer.rs` ~58192 an assertion — re-find both by grep); the gate: no rowed diagnostic
   literal contains three consecutive spaces (in `diagnostics_ledger.rs`, over every literal
   the ledger walk reaches). **N95** — rename `Program::hidden_impls` → `hidden_impls_pending`
   + a `debug_assert` at the drain; every reader updated (name them). **N96** — widen the
   ledger's check (3) to `Failure::new`/`Failure::unsupported`; ROW what it finds (the staging
   registry, the project files, the macro-engine limits, M66's identity message) with the
   vacuity pin each; a limit that is genuinely internal is fenced with a comment naming why.
2. **N87** — gate spec appendix A.2's reserved-word list to the lexer's keywords the way
   `docs.rs` gates the tour's; one pin. **N88** — the doc sweep: `reactive.vl` (7 `bind_each`
   lines), `rpc.vl` (7), `math.vl` (1), `browser/ui.vl:537`'s `child_relation`, `ui.vl:1187`'s
   redundant `context owner_scope` annotation (B333 adopts it — remove it and prove the
   check is unchanged), formatter.rs's two element-head layout pins spelling `.bind_each(`
   (rename the method to one that exists); the wasm playground's bare `View has no method
   'swap'` (no A99 steer suffix — find whether K14's no-prelude buffer or the steer's keying
   on std's `View` is the cause; fix if one line, else a FIND); a grep pin that std's comments
   name no retired method. COMMENT lines only in reactive.vl/rpc.vl — native-a-37 edits the
   same files and merges after you. **N89** — audit the ~24 `Node::Export(..)` match sites for
   a `Const` wrapper (formatter, macros.rs, lib.rs, css.rs, elements.rs, lift.rs, parsing.rs);
   either peel everywhere or refuse `export const` with a row — rec: peel (the form is
   legal since G24); pin `export const let` / `export const fun` through import, format, docs.
3. **N86** — port N82's three helpers into each binary that still names
   `std::env::temp_dir()` (`module_resolution.rs` 21 sites, `base_cache.rs` 9,
   `embedded_std.rs` 6, vilan-cli `corpus.rs` 4, `interpreter.rs` 2, `intrinsic_binding.rs` 2,
   `check_scope_differential.rs` 2, `corpus_harness/mod.rs` 2, `watch_lifecycle.rs` 2,
   `chunks.rs`, `markdown_golden.rs`, `diagnostic_determinism.rs`) — or lift them into a
   per-crate `tests/support` module; the ENOSPC guard with them; a grep pin that no test file
   names `temp_dir()` directly.
4. **N97** — MEASURE `walk_expr_node` + `_inner`'s frame per level (gdb frame deltas, debug
   and release; the integrator's method read ~110 KB per level on Linux debug); record the
   numbers on the item; plant the CANARY in `deep_nesting.rs`: a 30-level nested fixture
   analyzed on a 2 MiB thread (planted red first by running it at 1 MiB); a note in
   AGENTS.md's test section on `RUST_MIN_STACK`. Do NOT split the walk this order — if the
   frame is the cause, the split is a FIND with the per-arm sizes that justify it.
Sizing: S ×8 = M. Model: Opus. Owns `diagnostics_ledger.rs`, `docs.rs`'s keyword gate, the
test-harness plumbing, `deep_nesting.rs`, the two `Node::Export` audits' sites (peel only), the
comment lines it names. Nothing else in analyzer.rs beyond N95's rename and N94's literal.

## Lane dx-37 — the tools that lie: B346 (HIGH), N90 (HIGH), N91, N92, B342
Read B346, N90, N91, N92, B342; vilan-core `lib.rs` (std discovery), the `vilan-embedded-std`
crate, `base_cache.rs`'s relocated-checkout pin (`base_cache_miss_cost_across_a_sibling_
checkout`), vilan-cli `main.rs`'s `fmt` and `check` arms, formatter.rs's bail path and the
`formatter_never_silently_bails` pin (vilan-core `tests/parse_differential.rs`), `split.rs:63`, the
`refuse_shadowed_submodules`/A67 section in `module_resolution.rs`.
1. **B346 (HIGH).** Find the second std discovery path that ignores `VILAN_STD` (the
   embedded/materialized std? the workspace-relative probe? two std worlds mixed — the item's
   two symptoms are `Each<..> does not implement trait 'Slot'` and the derive load-ordering
   refusal); make ONE root win and REFUSE two (a row naming both paths); pin with a
   byte-identical relocated copy under `CARGO_TARGET_TMPDIR` — plant red on d783fbf4 first.
2. **N90 (HIGH).** `vilan fmt --check` reports a BAIL as a distinct non-zero outcome naming the
   file and the construct the printer declined (today it says "clean"); the CI fmt job reads
   it; pin with a construct the printer declines (N91's `macro` until N91 lands, then another).
   **N91** — a `print_macro` arm (and the `export macro` wrapper — 15 of std's after the
   curation); idempotency pins over `hash.vl`, `json.vl` (6 macros), `rpc.vl` (8); `vilan fmt
   --check vilan/std` green AND honest after N90.
3. **N92** — `vilan check` keeps its cache OUT of the checked package (the user cache dir
   beside `~/.vilan/std-cache`, or `target/` — pick after reading how `build` keys `dist/.cache`;
   say which); the split loader (`split.rs:63`) skips directories with a readable message; pins
   for both. **B342** — measure a `read_dir` per loaded module on a kolt copy (24 modules, the
   lucide directory excluded by the generated root); build the listing if the cost is under
   1 ms per analysis on kolt, else correct the heading in `module_resolution.rs` to the rule as
   it is; pin whichever.
Sizing: M + S + M + S + S = M–L. Model: Opus. Owns std discovery in `lib.rs` + the embedded-std
crate's materialization, vilan-cli's `fmt`/`check` arms, formatter.rs's `print_macro` (NEW fn;
css-37 owns the css-block printing — disjoint), `split.rs`'s loader, the A67 listing.

## Lane lazy-37 — A103 (S3, READY), B344, B345, A102 (R13)
Read A103, lazy.md §6b + §7 S3 + §8 (as built: `RULE_STATEMENT_SITES` 43 on the merged tree, the memo cell, the
thunk closures' `origin: None`), `option.vl`, `result.vl`, the std page for `Option`/`Result` (find its note that
the retrofit has NOT happened — lazy.md §8 says it is there), B344, B345, A102, the lazy analyzer fns lang-c-36 named
(parameter binding, the argument check on `expr_id_to_type_id_map`,
`check_resource_generic_instantiations` ~15232, `scan_closure_view_captures` ~23321), the HMR
transfer classification (`TransferForm`, `hmr.rs`/`hmr_swap.rs`).
1. **A103 — the retrofit.** `Option::expect(self, lazy message: str)`, `Option::unwrap_or(self,
   lazy fallback: T)` and `Result`'s twins become lazy; `unwrap_or_else` stays the explicit
   form. THE GATE: the corpus/std/docs/examples differential run BEFORE and AFTER over every
   program calling the four — any observable difference (a side-effecting fallback that stops
   running on the `Some` path, a changed golden, a changed print) is STOP-AND-DECIDE: record it
   on the item and do not land the retrofit for that program's shape until the owner rules.
   Expected: zero differences (record the count of call sites examined). Docs: the page's note
   retired, the tour's "Lazy parameters" section names the four; CHANGELOG `breaking` (a
   behaviour change) with the note.
2. **B344** — the argument check resolves a bare binding's type through
   `variables`/`parameters` (not only `expr_id_to_type_id_map`); a generic lazy parameter
   instantiated at a resource is caught through `check_resource_generic_instantiations`'s
   family; pin both (a resource reached through a field, not a local). **B345** —
   `scan_closure_view_captures`'s `Expr::Call` arm walks the SUBJECT; pin the nested-subject
   shape in a closure and in a lazy argument; run the estate (std, examples, corpus, docs,
   kolt copy) — a newly-firing program is a `breaking` note naming it.
3. **A102 (R13)** — transfer the lazy cell only when `state == done`; pending/poisoned stay
   `Excluded`; pin under the HMR round harness (a `lazy let` forced before the swap survives
   it; one never forced is re-minted).
Sizing: M + S + S + S = M. Model: Opus. Owns `option.vl`, `result.vl`, the four lazy analyzer
fns (named in the report), `inference/lazy.rs`, the HMR transfer classification, the lazy docs
pages.

## Lane solver-37 — B351 (kolt's FIXME), B347, B349, B350 (+ at GO: B352, B353)
Read B351 (the twenty-line description and the FIVE passing variants; the bisect note: not an
Order 36 regression — the VALUE forms' closure typing, A85-era, newly reachable via A99), B347,
B349, B350, positional-slots.md §10–§12, the closure-argument typing in `infer_type_inner`
(`note_callable_coercion` ~32794 is B340's gate beside it), context.rs's `adoptable_closure`
(:412) and `call_return_clause` (:398) — READ them; diagnostics-37 owns context.rs's walk —
if the fix lands there, name the fn and the two lanes' edits are disjoint), the transformer's
`current_admitting_file` (`enter_instance` seam), the S2 `#`-redundancy warning site.
1. **B351.** Rebuild the reproduction from the item (the integrator's scratch is gone): a
   block hole whose tail is `context.run(v, || { <el .child(swap(s, |x| match x { .. => <e/>,
   .. => <div .child(swap(t, |y| match y { .. })) /> })) /> })` under the EXTERNAL generic
   `run<U>`; find where the closure's return type is seeded for an external generic's
   block-bodied closure parameter and why a nested `swap` whose `C` is decided by `match` arms
   leaves `U` unresolved; fix at the seam; pin the reproduction AND the five passing variants
   (user generic, expression-bodied, single swap, outside a block hole, both annotated) so the
   fix cannot regress one into another. Kolt's FIXME (views.vl:94) is the integrator's.
2. **B347.** Bind `each_by`'s `T` from the source argument BEFORE the closure parameters are
   typed (the retired method did it through the receiver path); pin the unannotated form with
   `h.map(|c| c.title)` in the render closure and the `owner_scope` cascade GONE (one error at
   most, none after the fix); drop the four annotations the estate carries (name them).
3. **B349** — set `current_admitting_file` at the module-body seam too; pin a module-level call
   through a selector-restricted import (refused, as §3.5 says). **B350** — the `#`-on-an-
   exported-impl redundancy WARNING (one row; the delete-the-`#` quick fix widened to the
   selector); pin.
4. **B352 (GO).** Three kolt exhibits of the same family, rebuilt as std-only programs and
   pinned un-annotated: (1) `swap(cell, |enabled| …)` over a `StorageSignalCell<bool>` leaves
   `enabled: T` (B347's fix is the first thing to try); (2) `Signal<Option<str>>::map(|x|
   x.unwrap_or_default())` needs the annotation although it is the RECEIVER path — diagnose
   whether `map`'s `U` is solved before the body is checked or the `Default` bound is resolved
   against an abstract `T`; (3) `SignalCell<User>::map(|x| x.channels).flatten()` cannot
   produce `SignalCell<List<i53>>`. Kolt's three annotations are the integrator's.
5. **B353 (GO; HIGH until probed).** `Signal<List<i53>>::new([]).set(Some([1i53]))` must be
   refused — probe it, then the exhibit's shape (a `RemoteSource<Option<List<i53>>>`'s
   `effect(|incoming| channels.set(incoming))`); if the second passes, the closure's parameter
   is abstract and every call inside it is unchecked — plant that pin red and make B352's fix
   turn it green; if neither reproduces, record the probe on the item (close at the sweep).
Sizing: M + S + S + S + M + S = M–L. Model: Opus. Owns the closure-argument typing seam in analyzer.rs
(name every fn), `each_by`'s binding, the transformer's module-body seam, the B350 row + fix
arm (vilan-lsp: one arm, named), `inference/lifetimes.rs` or the module the lane finds for the
value-form pins, `ui_rows.rs` for B347.

## Lane diagnostics-37 — E189, E190, E185, B343 (R9) (+ at GO: E191)
Read E189 (the mechanism: a closure handed to a call that failed to resolve never attaches to
the clause-carrying parameter, so everything it reaches looks unenclosed — 173 of kolt's 180
errors), E190, E185, B343 + R9, context.rs (`analyze`'s reach edges), transformer.rs
`ensure_function_emitted` (~8386) and the B55 refusal site (`function_with_name` records the
bodyless id at EMISSION, after the call that asked), the S4 monomorphization refusal
(visibility-36's fn; `current_admitting_file` is in hand), parsing.rs `parse_function` (~5503),
the TextMate `context` rule (`(?<=\))\s+(context)\b`), `grammar_sync.rs`, contexts.md §3.
1. **E189.** The NARROW rule first: the reachability walk skips edges whose call failed to
   resolve and closures that are arguments of such calls (one primary error, no fan-out); then
   the BROAD gate as backstop: `context`-family diagnostics are dropped when the list already
   carries a resolution/type error, with a NOTE on the first primary error saying context
   checks were skipped (one row). Pins: the kolt shape (a retired method taking a closure whose
   body reaches a context read → ONE error); the pure missing-`run` program still errors; the
   broad gate's pin (a type error elsewhere + a genuine missing `run` → the run error deferred,
   the note says so). Verify over a kolt COPY at d783fbf4 with the seven A99 sites RESTORED to
   the retired spelling: 180 → 8 (seven steers + E190's, until solver-37 lands B351).
2. **E190.** Record, with the bodyless id, the function being emitted when the requirement was
   first requested (`self.emitting`'s innermost + its file) and the call expression id when
   the resolver has it; the message names the function and its file; the span is the CALL's
   when known, the enclosing function's name otherwise; row edit. The pin over B351's
   reproduction is planted on the BASE (before solver-37's fix); if the merged tree no longer
   reaches the refusal there, land a second trigger (any body-less requirement reached through
   an unresolved generic) or unit-test the message construction — say which in the report.
3. **E185** — thread the declaring module's spelled name into the S4 refusal and its steer
   (no more `that module`); re-key the row; the §3.5 pin asserts the name. **B343 (R9)** — the
   refusal for the un-parenthesized closure-typed return carrying a clause (one row NEW; the
   quick fix parenthesizes); the TextMate lookbehind fixed so `fun f(): i32 context settings`
   paints the keyword; the book theme's copy; grammar_sync scope pins for both shapes;
   contexts.md's §3 sentence is the integrator's (hand back the text).
4. **E191 (GO).** One arity error inside an element head (`<a href(href()) on:click(..)
   .styled(..)>` — `href()` missing its `Route`) "caused a ton of error noise" in kolt: count
   the errors on the twenty-line shape; if E189's broad gate covers it, record that and pin the
   count; else fix the head's recovery so a failed attribute argument leaves the element typed
   (`View`) and the chain continues — ONE error, pinned.
Sizing: M + M + S + S + S = M. Model: Opus. Owns context.rs's reach walk (`analyze` and the fns it
calls — solver-37 may edit `adoptable_closure`/`call_return_clause`, disjoint, both named),
transformer.rs's `ensure_function_emitted` + the B55 message site, the E185 row's site,
parsing.rs's B343 refusal (ONE new check in `parse_function`'s head — css-37 owns
`parse_css_block`), the TextMate `context` rule, the two quick-fix arms in vilan-lsp (named).

## Lane editor-37 — E69 (ruled), E184, E186, E187, E188 (+ at GO: E192, E193)
Read E69 (the ruling: GENERATED from the WHATWG HTML attribute index + the SVG index; completion
only; the desugar stays name-blind), the repo's precedent for a generated-and-gated table —
`scripts/regen-mime-table.py` + `crates/vilan-core/tests/mime-table.tsv` +
`mime_table_sync.rs` — and `css_properties.rs` (E153's closed vocabulary, the same shape for
properties); E67's head-position machinery in vilan-ide `completion.rs`; E184 +
`AutoImportOrder::build` (~3872) + `Program::exported_entities`/`curated_modules`; E186–E188 +
document.rs's organizer deletion, E177's Export fixes and E175's sibling reads, the exposure
warning site.
1. **E69.** A generator `scripts/regen-html-attributes.py` with two modes: `--fetch` (network;
   rewrites the VENDORED extract `crates/vilan-ide/src/html-attributes.tsv` — element-or-`*`,
   attribute, source index, with the fetch date, the source URLs and a content hash in its
   header) and the default (TSV → the checked-in Rust table `html_attributes.rs`: per-element
   + global attributes, and the `on:` event names from GlobalEventHandlers as a second table);
   the sync test regenerates from the TSV and diffs (offline — a gate never touches the
   network; refreshing the extract is a deliberate commit). Completion at `<tag |>` offers the
   tag's attributes plus the globals (E67's machinery), `on:` from the event table; a `data-*`
   name is never refused; the desugar untouched. Pins: `<input |>` offers `type`, `disabled`,
   `value` + globals; `<svg |>` offers `viewBox`; the sync test fails on a stale table; the
   playground (vilan-wasm) reaches it unchanged.
2. **E184** — one filter in `AutoImportOrder::build` on the two `Program` fields (a curated
   module's private item is not offered; an uncurated module's is); the four
   `overlay_module_reclaim` pins stay green (it runs outside `owned_modules::collecting()` —
   do not call `module_importables` per keystroke).
3. **E186** — delete the run's trailing separator when the run was a whole paragraph; pin over
   the lucide shape. **E187** — both readers consult the server's open-document map before the
   filesystem; pin: an unsaved sibling edit still lands the `export` at the right line.
   **E188** — record the exposed entity on the exposure warning; the fix reads it; pin the
   two-`S` file.
4. **E192 (GO).** `import std::map::Map;` fades as unused while `import std::map::{ (impl
   Map<_, _>) };` names `Map` (kolt views.vl:2–4). Delete the type import in a copy and
   `vilan check`: if the selector needed it, the fade's use-count gains the selector subject
   (pin); if not, the fade is right — record the answer on the item for the owner.
5. **E193 (GO).** Completion inside a STRUCT INITIALIZER body: at `S { | }` and after a comma
   offer the REMAINING fields (type as detail, `name = ` inserted) and the shorthand where a
   local of that name is in scope; the head resolves through B190's `type-path`. Pins: at the
   brace, after a comma, written fields excluded, a generic struct, a qualified head; the
   playground reaches it.
Sizing: M + S + S + S + S + S + M = L. Model: Opus. Owns vilan-ide `completion.rs`'s head-position
completion + `AutoImportOrder` (css-37 owns `css_block_completions` + `CssPosition` in the same
file — disjoint fns, named), the new table + generator + sync test, vilan-lsp document.rs's
organizer deletion + the two readers + the exposure-warning record (one analyzer field, named).

## Lane perf-37 — M72, M73, M74, M75 (E121's lanes for kolt's keystroke)
Read M72 (`base_cacheable` at analyzer.rs ~55215 requires `!contains_service`; kolt's `store.vl`
290–605 ms CPU per keystroke, 0 hits 0 misses), M73 (`resolve_world` ~43872; theme.vl's build
161 ms vs views.vl's 11 ms with the same checks phase; the naive import-fixpoint split moved
0.4 ms), M74 (`world_cache_spike.rs`; M67's weights in vilan-lsp `memory.rs`), M75
(`refuse_imported_member_collisions` ~59192, `statement_for`'s linear scan), M70's as-built
(the entry-aliased key), dx-33's instrument, the paired harness perf-36 used.
1. **M72.** Store the world BEFORE the service expansion (the expansion runs inside the
   world-building loop — split it) or key the service's expanded form; pick after reading;
   measure `store.vl` with the paired harness over a READ-ONLY kolt copy (before/after CPU per
   keystroke, loadavg beside); pin: a service entry served from the cache on the second
   analysis (a fixture with one `[service]`).
2. **M73.** Split `resolve_world` at the alias boundary — preludes/use-drain/conformance/
   constraint fixpoint for non-alias scopes first, the ALIAS-reaching work deferred; measure the
   six M70 files; the fix must not re-open M70 (its pin stays green).
3. **M74** — measure the two shapes (resolved vs entry-shaped world) with the spike harness; a
   per-world weight or a second factor; M67's budget pin re-read with the numbers. **M75** —
   the `(importer) → [(span, sources)]` index built once per program; pin a 500-statement
   two-package collision under a CPU bound.
Sizing: M + M + S + S = M–L. Model: Opus. Owns the base cache fns in analyzer.rs (named),
`resolve_world` and its callees, vilan-lsp `memory.rs`'s weights,
`refuse_imported_member_collisions`. Nobody else touches the base cache.

## Lane native-a-37 — C14 S1–S3 (R1) + D8: the counted cell's JS-provable half
Read C14 + signal-cell-representation.md whole (§2.2's table of the 19 frame-scoped cells, §4.1
(a), §5.2, §7 the identity stamp, §9, §10 S1–S3 with their exit tests, §11 Q2/Q3/Q7, §12's
"stays open" edits), C1, D8, M71, `shared.vl` (the headnote at :5), `reactive.vl` (`subscribers:
Shared<List<Subscriber>>` :362/:760; `observe` :826 — its own comment names the back edge),
`arena.vl`, destruction.md §10, claims-and-epochs.md §5a, the `Shared` primitive in the
analyzer (`primitive_struct_ids` 'Shared', 8 sites) and its four intrinsics in the transformer
(`__shared_new` …), `reactive_lifetimes.rs` (the SCC gate `a_disposed_exemplar_holds_no_
reactive_cycle` + `support/heap_cycles.js`; `derivations_detach_from_their_source_with_their_
boundary`; the `b291`/`b292` pins).
1. **S1 — the frame-scoped subtraction (M71).** The 19 cells of §2.2 (`json.vl`'s writer/
   reader, `binary.vl`'s two, `process/fs.vl`'s cursor, `process/rpc_server.vl`'s four
   handshake flags, `rpc.vl`'s three locals, …) become `mut` locals or `&mut self` fields;
   `-p vilan-core` green, `-p vilan-cli --test service_layer`; the emitted `__shared_new` count
   drops by 19 (say the number); Ir on the rpc codec paths before/after; a census pin that
   the frame-scoped class stays at zero (port the probe's `census.py` classifier to a Rust
   test, or hand the script back — say which). **D8** — the `shared.vl` headnote rewritten to
   what the paper found (`Shared` is the counted box for diffuse ownership; `Arena`/`Handle`
   the tier for graphs and stable identities; today 0 of 154 sites match the old advice) + the
   memory-model tour's sentence.
2. **S2 — `Weak<T>` (C1).** `Shared::downgrade(&self): Weak<T>`; `Weak::upgrade(): Option<
   Shared<T>>`; `Weak::get(&self): Option<&T> borrows self` (§5a's second-class view); on JS
   `downgrade` is the identity and `upgrade` is `Some(cell)` — the SHAPE lands, the
   deterministic `None` waits for counting (S4), documented at the type exactly as
   destruction.md §10 says; `Weak` a primitive beside `Shared` (the analyzer sites, the
   transformer's lowering, the interpreter arm, hover). Pins in `inference/` (a new
   `weak.rs` or `lifetimes.rs`) for the three signatures and the second-class `get`;
   `reactive_lifetimes` unchanged.
3. **S3 — std's two back edges weak.** `observe`'s captured cell → a weak capture;
   `Subscription`'s alias of the subscriber list → a weak alias; two lines and their comments.
   Exit: the SCC gate still `cycles=0` AND the mounted SCC count DROPS (recorded, per its
   contract — report before/after); `derivations_detach…` still 25→0; the three `b291`/`b292`
   pins unchanged. Plant red: restore the strong capture, watch the mounted count rise. A
   `set` after `owner.dispose()` still commits and notifies (§5.2 — pin it if unpinned).
4. The paper's small edits, handed back: lifetimes.md §9's non-goal gains "for its own sake";
   a sentence at `analyzer.rs:24614` (B267's walk under counting, Q7 — that one you write).
Sizing: S + S + M + S = M. Model: Opus. Owns `shared.vl`, `reactive.vl` (S2/S3 — hygiene-37's
N88 touches its comments and merges first), the 19 sites' files (those lines only), the
`Shared`/`Weak` primitive sites in analyzer/transformer/interpreter (named), the new
inference module, `reactive_lifetimes.rs` (new fns). Goldens move (S1's construction count;
S2/S3's reactive body) — regenerate and say which.

## Lane native-b-37 — C16 (R7) then F1 S1a (R2, R3, R5, R6, R8): the emit-Rust backend's first cut
Read F1 + native-apps.md whole (§0 the probe's five findings — `Target` no longer exists, the
eleven S2 sites are NOT yours; §2 the probe: `board.vl` 62 lines and its two Rust
translations under `projects/vilan/proposal/native-apps-probe/`, §2.3 the 52 intrinsics /
~35 helpers the emitter needs, §2.4 R-1 (stored-and-called closures → `Rc<dyn Fn>`, F16) and
R-2 (mutably-captured bindings → `Rc<RefCell<_>>`, C15/R3); §5 S1's scope and exit test; §7;
§8 Q1–Q8 with R2–R8 above), C16 + C13's ignored pin (`inference/borrows.rs:7171`: "the escape
rule does not follow a closure through an ordinary call") + `ci_ignored_pins.rs` (un-ignoring
a pin means updating the gate), lifetimes.md §2.2, `target.rs` (`Backend { Js }` :27, `parse`,
`name`), vilan-cli `main.rs` (`validate_backend`, the run arms), `transformer.rs` as the JS
emitter's shape (NOT edited), the interpreter's intrinsic table (the enumeration of what a
backend must provide), AGENTS.md's dependency stop condition.
1. **C16 first.** A closure capturing a VIEW of a dead local is a REFUSAL: build the escape
   rule's remainder for views (un-ignore C13's pin as its first exhibit; the direct shape —
   the capture outlives its frame through a return or a store in the same body — and the
   storing-callee shape); plant the probe's shape red first; row NEW; run the estate — a
   newly-firing program is a `breaking` note (expected none; C12 closed as a limit with its
   shape pinned). If the storing-callee remainder is larger than M, land the DIRECT shape's
   refusal, keep C13's pin ignored with its text re-pointed at what is left, and say so — S1a's
   exit corpus must contain no such program either way.
2. **F1 S1a — the emitter and the runtime.** `Backend::Rust` (`--backend rust`) in target.rs;
   a NEW crate `crates/vilan-rust` (the emitter, beside transformer.rs — same `Program` in, a
   cargo project out under `dist/native/`) and a NEW workspace crate `crates/vilan-rt` (the
   runtime §2.3 enumerates, items (1)–(6): `str` → `Rc<str>`, `List` → `Vec`, `Map`/`Set`,
   `Option`/`Result`, closures — `Rc<dyn Fn>` wherever a closure value reaches a storing
   position (F16's rule, pinned on `board.vl`), `impl Fn` where only called; mutably-captured
   bindings boxed `Rc<RefCell<_>>` (R3), COUNTED over the exit corpus; panics via
   `catch_unwind`; `print`; C14's cell as the counted box — S4's real counting is later, S1a's
   cell is `Rc<RefCell<{ value, subscribers }>>`); `i53`/`u53` → `i64`/`u64` with R6's note;
   NO dependencies in `vilan-rt` (R8). SCOPE, hard: structs, enums, `Option`/`Result`, `str`,
   `List`, `Map`/`Set`, closures, `impl`s, traits (monomorphised), `print`, `panic`, the cell —
   NO async (R5: the executor's DESIGN is a section of your report), no UI, no rpc, no `std::fs`,
   no platform surface. `vilan build --backend rust` writes the project and runs `cargo build`
   (debug by default, R8; the help says so); `vilan run --backend rust` runs the binary.
3. **The exit test.** A differential `crates/vilan-cli/tests/native_differential.rs`: each
   program compiled by BOTH backends, stdout byte-identical. The corpus: `board.vl` first, then
   every platform-free program you can enumerate from `crates/vilan-cli/tests/` and
   `vilan/test/` (no `std::dom`/fetch/fs/rpc/ui/async — write the enumeration as a test
   support fn so Order 38 widens it). Report compiled / identical / failing with the reason
   per failure. The default suite runs `board.vl` + a handful (rustc is ~1 s per program);
   the full set runs under `VILAN_NATIVE_DIFFERENTIAL=1` and in the seal — the shared
   `vilan-rt` build is cached under `CARGO_TARGET_TMPDIR`. Docs: `appendix/cli.md`'s
   `--backend` row; a `guide/native.md` stub stating scope and what is not there.
4. **F18 sizing (GO; report only, no build).** The owner's next native product is a WEB
   SERVER, before any UI. Your report carries a sizing section for it: what `vilan-rt` needs
   beyond S1a (J6's executor — write its design here, R5; sockets/HTTP; SQLite or the `std::db`
   shape; the file system; the rpc server's wire path), which `@process` std modules would
   resolve for `native` unchanged and which need a native twin (`native` MUST join
   `@process` for a server — F1 §8 Q2 revisited; name `check_library_contract`'s cost), and the
   order S1b → executor → http → db → rpc with a size per step. The UI twin (S3–S5) and the
   `native` PLATFORM's UI-shaped sites (S2, F15, E182) are NOT sized — they wait for F17.
Sizing: M + L (S1a = the first of S1's two to three lane-orders; S1b + F18 are Order 38's). Model: Opus. Owns `target.rs`'s `Backend`, the two NEW crates, vilan-cli's backend
validation and run arms (named), the escape rule's fns in analyzer.rs (named; C16), the new
differential test, `guide/native.md`. Touches NOTHING in transformer.rs, `std`, the platform
model (S2 is not yours; `infer_platform` stays binary until then).

## Lane css-37 — A101 (BREAKING; R10–R12) + E183; merged LAST
Read A101 whole (the grammar: `css-item = declaration | method-item | nested-rule`;
`declaration = property "(" [ expression { "," expression } [ "," ] ] ")" ";"`; `property =
{ "-" } NAME { "-" NAME }` span-adjacent; `method-item = "." IDENT [ "(" args ")" ] ";"`; the
`value`/`value-piece`/`hole` productions DELETED; the lowering unchanged — one `.raw(name,
value)` per declaration), R10–R12, css-block.md §4.1 (the value lexing that goes), §4.3, §5.2,
§6 (`raw`'s typed values, `IntoRawValue`), §7.1 (the completion tables), §8 (the formatter's
value pass), §15–§16, E167's converter (vilan-lsp document.rs ~6166–6800: it TYPES declarations
— the codemod rides it), `parse_css_block` (parsing.rs ~3594), `css.rs` (the desugar),
`lexing.rs`'s css value tokens, `css_properties.rs`, `css_block_completions` +
`CssPosition` (vilan-ide completion.rs ~724), `STYLE_CONDITION_METHODS` (formatter.rs ~1195),
`StyleSurface` (E172/E175), E183, the `var(..)` question (R12).
1. **A101 — the grammar and the lowering.** Declarations as calls; the method item; nested
   rules unchanged; the css value tokens gone from the lexer (`100%`, `1rem`, `#333` never
   lexed — the `#333` refusal row RETIRED, named); N arguments space-joined (R10); a
   declaration argument whose type is not a raw value is the ordinary type error at the
   argument; `--name(..)` admitted (R12) and `var(name: str)` in `std::style` if missing.
   Pins: each production; the LOWERING IDENTITY — a block and its chain twin produce the same
   `class_list` and stylesheet (every existing css-block pin re-spelled; a `.css` golden that
   MOVES is a finding, not a regeneration); the `;` rule; the retired row's absence.
2. **The tooling, same order.** Formatter §8: items print as calls with expression formatting
   inside (idempotency pins); the TextMate css-block rules (property-call heads; scope pins);
   `css_block_completions`: property position offers `name(` with the paren, value position
   falls through to EXPRESSION completion (`pct(`, `Color::`), a method item `();`; E167's
   converter both ways (CSS text → the call form; the call form → CSS) — round-trip pins;
   `StyleSurface` unchanged.
3. **E183 — the dotted head.** `CssPosition::Condition` → `DottedHead`, merging
   `STYLE_CONDITION_METHODS` (first), std's other `impl Style` methods from the program, and
   the program's user `impl Style` blocks (same file and siblings — `StyleSurface::extend`
   after E175 feeds from the impl table), filtered by the B318 bit under the uncurated
   exemption; each entry carries the signature as detail; a nested-rule entry inserts
   `() { }`, a plain method `();`. Pins: a user method in the same file; one in a sibling; std's
   `on`; the combinators still first; the filtered case; the playground reaches it.
4. **The codemod (R11).** Over EVERY css block in the tree (re-census: the filing said 138 —
   docs 14, corpus 4, vilan-core tests 80, vilan-cli tests 12; the integrator's grep on
   d783fbf4 reads `inference/styling.rs` 43, `parse_expr_regression/fixtures.rs` 33,
   `style_chain_order.rs` 10, `guide/styling.md` 9, `vilan/test/css-block.vl` 4, plus the
   pins INSIDE vilan-lsp document.rs (57 mentions), formatter.rs (40), css.rs (31), vilan-ide
   completion.rs (4) and vilan-wasm — count them all; CHANGELOG's historical entries are NOT
   rewritten), typed where the converter types, string otherwise; one commit, nothing else in
   the diff; kolt NOT touched (the integrator's at the sweep at the owner's word — hand back
   the codemod as a runnable script over a directory). CHANGELOG `breaking` entry with the
   three rewrites (declaration → call; `{expr}` hole → the expression; `.method { }` head
   without a block → `.method();`). Docs: css-block.md §16 (the spelling change and why — hand
   back the text), the styling guide and reference rewritten.
Sizing: L + M + M + M = L. Model: Opus. Owns `parse_css_block` and its helpers, the css
value-token rows in lexing.rs, `css.rs`, `css_properties.rs`, the formatter's css-block printing
(dx-37 owns `print_macro` — disjoint), the TextMate css-block rules (diagnostics-37 owns the
`context` rule), `css_block_completions` + `CssPosition` (editor-37 owns the head-position
completion + `AutoImportOrder`), E167's converter, the styling docs, every css block it
rewrites. MERGED LAST, rebased by the integrator if a pin file conflicts.

## Ownership map (conflict avoidance)
- analyzer.rs: solver-37 (the closure-argument typing seam, `each_by`'s binding, B350's
  warning); lazy-37 (the lazy argument check, `check_resource_generic_instantiations`'s
  family, `scan_closure_view_captures`); perf-37 (the base cache fns, `resolve_world`,
  `refuse_imported_member_collisions`); native-a-37 (the `Shared`/`Weak` primitive sites);
  native-b-37 (the escape rule's fns — C16); diagnostics-37 (the E185 row's site); hygiene-37
  (N95's rename, N94's literal); dx-37 nothing. Name every edited fn in the report; the
  integrator hand-folds adjacent edits.
- context.rs: diagnostics-37 (the reach walk); solver-37 only if B351's seam is
  `adoptable_closure`/`call_return_clause` (named) — disjoint fns.
- transformer.rs: diagnostics-37 (`ensure_function_emitted` + the B55 site); solver-37 (the
  module-body seam, B349); native-a-37 (the `Shared`/`Weak` lowering); native-b-37 NOTHING
  (the Rust emitter is its own crate).
- parsing.rs: css-37 (`parse_css_block` + helpers, the deleted value productions);
  diagnostics-37 (B343's one check in `parse_function`). lexing.rs: css-37 only.
- formatter.rs: css-37 (the css-block printing), dx-37 (`print_macro`, NEW fn), hygiene-37
  (two pin renames in `mod tests`) — disjoint.
- vilan-ide completion.rs: css-37 (`css_block_completions`, `CssPosition`), editor-37
  (head-position completion, `AutoImportOrder`, the new table) — disjoint fns.
- vilan-lsp document.rs: editor-37 (the organizer deletion, the two readers, E188's record);
  css-37 (E167's converter fns); the quick-fix arms: diagnostics-37 (B343's, E189's note),
  solver-37 (B350's) — one arm each, named.
- editors/vscode grammar: css-37 (css-block rules), diagnostics-37 (`context`) — disjoint.
- std: `shared.vl`, `reactive.vl`, the 19 M71 sites — native-a-37; `option.vl`, `result.vl` —
  lazy-37; `style.vl` (`var(..)` only) — css-37; comment lines in reactive.vl/rpc.vl/math.vl/
  browser/ui.vl — hygiene-37 (merged first). Nobody else edits std.
- New crates: `vilan-rust`, `vilan-rt` — native-b-37 only. target.rs — native-b-37 only.
- Tests: `deep_nesting.rs`, `diagnostics_ledger.rs`, `docs.rs` — hygiene-37; `reactive_
  lifetimes.rs` (new fns) — native-a-37; `native_differential.rs` (new) — native-b-37;
  `ui_rows.rs` (new fns) — solver-37; `hmr.rs`/`hmr_swap.rs` (new fns) — lazy-37; the css-block
  pins everywhere — css-37 (the codemod), merged last.
- Docs: lazy-37 (the lazy pages), native-b-37 (`guide/native.md`, `appendix/cli.md`'s row),
  css-37 (styling guide/reference), native-a-37 (the memory-model tour sentence), hygiene-37
  (appendix A.2's gate), diagnostics-37 (contexts §3 text handed back) — disjoint pages.
- Merge order: hygiene-37, dx-37, lazy-37, solver-37, diagnostics-37, editor-37, perf-37,
  native-a-37 (goldens), native-b-37 (new crates; `Cargo.lock` union), css-37 LAST (the
  codemod over the pin files; the lowering-identity harness re-run over the merged tree is its
  gate). Merges DETACHED (merge_fold under setsid nohup + an until-grep waiter); goldens
  regenerated once over the merged tree; hand-folded merges use `gates_push.sh`.

## At the sweep (integrator, proposals)
- Close: M71 D8 C1 (S2 landed; the determinism note points at C14 S4) · C16 · B351 B347 B349
  B350 B352 B353 (or record the probe) · E191 E192 E193 · A103 A102 B344 B345 · E189 E190 E185 B343 · E69 E184 E186 E187 E188 · M72 M73 M74
  M75 · N94 N95 N96 N87 N88 N89 N86 N97 · B346 N90 N91 N92 B342 · A101 E183 · F16 and C15 as
  DECIDED (their rules built in S1a — close or re-point per the lane's report) · J6 stays
  OPEN with its design section landed · C14 stays OPEN (S1–S3 landed; S4/S5 queued) · F1 stays
  OPEN (S1a landed; S1b + S2 queued) · F15 and E182 stay OPEN (ruled, S2's).
- Papers: signal-cell-representation.md §13 as-built (S1–S3; the SCC counts before/after; the
  `__shared_new` count); native-apps.md §10 as-built (S1a: the crates, the corpus numbers, the
  boxed-binding count, the executor design section from the lane's report); css-block.md §16;
  lazy.md §9 (S3 as built; the differential's count); contexts.md §3 (R9's sentence);
  visibility.md (E185/B349/B350 notes); lifetimes.md §9's clause; editor-latency.md's ledger
  (M72/M73 numbers).
- Kolt at the owner's word: the css codemod over its blocks (the lane's script; re-census
  first); the B351 FIXME at views.vl:94 dropped (`let shell: View = …` → the direct form);
  any B347/B352 annotation; `vilan check` 0/0 and `vilan build` clean after. The kolt sweep's
  STALE comments, migrated at the owner's word (go-items37.json lists them): overlay.vl:67–87
  → `std::dom`'s `query_selector_all`/`observe_resize` (A59); views.vl:200's `[hidden]` HACK →
  `View::show()` (A60); routes.vl:25 → `impl Route with FromPath` (A62); interact.vl:129 →
  `std::math::Vec2` (A83); theme.vl:268's swap HACK → `{signal}` (B268); store.vl:97's `u53`
  and :166's `Result<i53, str>` (A82; A107 verifies); scale_step.vl:12 → `Callable` (B340);
  login.vl:71's fetch HACK → `std::fetch::post(url, body).send()`; login.vl:1's stale FIXME.
- Goldens: regenerated once over the merged tree (native-a-37 moves them; css-37 must not);
  the lowering-identity harness and the S1 stylesheet-identity harness re-run there.
- The ledger paper re-keyed from the lanes' `NEW` rows (next id 500 →); N94's gate runs over
  the merged tree.
- Chronicle: Order 37 — cycle 55 entry at GO; MERGED and SEALED paragraphs; toolchain refresh
  both locations; reap ten worktrees.
- Order 38's queue, written at the sweep: F1 S1b (the widened platform-free corpus); F18
  native SERVERS (the owner's priority, sized by native-b-37) BEFORE S2 (the `native`
  platform's UI-shaped sites, F15's N-way gate and E182 wait for the F17 conversation); J6's
  executor (built); A104/A105/A106/A107/I4/I3 from the kolt sweep; C14 S4
  (the counted lowering on the Rust backend) + S5 (optional); C15's by-value capture
  optimisation with R3's measurement; N97's split if measured; M56/M57/M54; E121's remaining
  path; K14 at the cut; B348 (behind fn-coercion rule 2's instantiation); B298 (Q3); A94;
  M60 (re-measure after S4); L20 (owner); the v0.41.0 cut (HELD — the owner's call; thirteen
  orders since v0.40.0).
