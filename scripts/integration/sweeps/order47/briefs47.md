# Order 47 — FASTER, FEWER WRONG ANSWERS, EASIER TO DEBUG: incremental analysis (the hot-set world), the two biggest check levers, `dbg` and panics that say where, the bugs Order 46's lanes found, the editor's remaining holes, and the two warnings that become errors (DRAFT 2026-10-04, written while Order 46's last lane runs; base and counts to be stamped at the v0.44.0 fold; every ask RULED as recommended 2026-10-04; GO 2026-10-05, at the fold)

**Theme (the owner, 2026-10-03):** performance, bug fixes and quality of life. New features wait.
Opaque-returns hiding is deferred past this order by ruling. The mirrored `Store` is asked (R-d).

**Base.** Order 46 sealed at 9fab0ff5 on 2026-10-04 (two seals: the first tip's CI went red on one
Windows pin); v0.44.0 was cut at that seal (tag 1a937ac4, release run 37252287752 green 17/17, ten
assets) and FOLDED on 2026-10-05: `origin/main` = `origin/next` = e5e15ca7. Toolchain `vilan 0.44.0
(e5e15ca7b)` in both locations, and the 0.44.0 extension in the local VS Code server. `## Unreleased`
does not exist on next. Ledger max **637** (lanes write `NEW`). Tracker **148 open**: Order 46 filed 94
and closed 91. The reference perf ceilings were re-taken at the seal with one codegen unit; three carry
owner-approved bumps (reactive-ui x1.07, todo x1.02, walkthrough x1.03: M119, M120). v0.44.0 shipped
over an approved performance override on one editor row (importers open: the edited file's own
diagnostics at about 1.4 s, up from 0.35 s; every file settled in 28% of the CPU).

Kolt is on v0.44.0, uncommitted for the owner: the trait imports, the message row on `when_all_some`,
`model.vl` on `states()`, `.autofocus()`, the std paths (by `vilan check --fix`) and the icon
generator's import. `vilan check` 0 errors and 0 warnings, both legs build; its browser runtime is
unverified. The store exhibits patch is HELD on M117. Still owed by the owner: Dependabot's #6, #7
(CI actions) and #8, #9 (the release workflow's artifact actions, R-i) on GitHub - the CLI token has no
`workflow` scope.

**The shape.** Five things set the order of work:

1. **A keystroke should not re-analyse the world.** Since entry-world analysis, every edit outside the
   entry file misses the base cache: the world is evicted, rebuilt cold and stored again (M115), about
   14.3 G instructions on kolt against E121's roughly 5.5 G. `proposal/incremental-analysis.md` is
   ruled (Q1–Q10): firewalls inside today's analyzer, not a rewrite. This order builds S0 (the
   fingerprints and the per-edit counters, so the cost is finally measured), S1 (hot-set worlds: keep
   the entry's world minus the edited module and what imports it) and the edit-replay differential
   that blocks every later slice; S2–S4 follow in the same lane as far as they measure.
2. **Two levers on every `vilan check`.** Implementation selection is about 32% of kolt's check
   because the emitter's member selection misses its memo (M111). And kolt's check costs 9% more once
   it adopts the store, which nobody can yet explain (M117); the store exhibits and the mirrored store
   wait on that answer.
3. **Debugging.** `proposal/debugging.md` is ruled (Q1–Q12). `print` shows the JS representation
   (`Some(5)` prints `[ 0, 5 ]`), panics carry no location, and `Debug` cannot be derived on a struct
   with a `List` field. This order builds S0 (`[track_caller]`: panics, asserts, index errors and
   unwrap report their vilan location), S1 and S1b (`dbg(..)` as an intrinsic, with the printer that
   writes vilan's own literal syntax on both backends), S2 (`dbg_stack()`) and S4 (every type
   debuggable).
4. **The bugs Order 46 found and did not fix.** Its lanes filed more than they were asked to fix,
   which is what the owner wants from them. The wrong-answer and false-refusal residue is one solver
   lane and one native lane here.
5. **Two warnings become errors, as ruled for v0.45.0:** a trait method called without importing its
   trait (B515, via B535), and attributes written out of the canonical order (B536). Each needs its
   quick fix in the editor and the estate migrated first.

**Eight lanes plus papers, in two waves under the cap of five.** Wave 1: incr-47, perf-47, debug-47,
solver-47, native-47. Wave 2, each as a slot frees: editor-47 (rebased onto incr-47), store-47,
docs-47. papers-47 beside. Merge order:

1. solver-47 (sha to LANE-STATUS.md as each wrong-answer fix lands);
2. native-47;
3. perf-47;
4. debug-47 (rebased onto solver-47: both add analyzer passes and emitter arms);
5. incr-47 (rebased; it owns the world, cache and pass-driver layer, so it lands after the pass work);
6. store-47;
7. docs-47;
8. editor-47 (rebased onto incr-47; last).

A cut is proposed at the seal (R-f).

## Asked at GO (the owner)

**RULED 2026-10-04: R-a through R-l as recommended** (R-d door (a): the mirrored store waits for Order 48, behind M117).

- **R-a: how far incremental analysis goes this order.** S0 + S1 + the differential are the floor.
  S2 (prefix tables), S3 (seeded context/async/platform passes) and S4 (the const cache) are built in
  the same lane only while each one's measured win matches the paper's estimate within reason; the
  lane stops and reports at the first that does not. S5–S7 (the interface firewall, one function per
  keystroke) are next order's. Rec: **yes, measure-gated**.
- **R-b: how far debugging goes this order.** S0, S1, S1b, S2, S4. `print` adopting the printer (S3:
  it moves corpus goldens and closes F68), source maps (S5) and `--inspect` (S6) follow in Order 48.
  Rec: **yes**. S3 could ride this order if debug-47 finishes early; say if you want it pulled in.
- **R-c: the two flips ride v0.45.0.** B515's warning becomes a refusal and B536's attribute-order
  warning becomes an error, each only after its quick fix exists and std, the corpus, the docs, the
  examples and kolt are clean under the warning. Rec: **yes, both, at this order's cut**.
- **R-d: the mirrored `Store` (A153, ruled Q1–Q15).** It is a feature, and the theme says features
  wait. It is also the answer to kolt's manual caching on both sides of the wire, and it cuts a
  channel open from 220 frames to 8. Door (a): hold it for Order 48, and settle M117 first, since
  nothing more should be built on the store until its check cost is understood. Door (b): build S1
  (the server half) now behind M117's answer. Rec: **(a)**.
- **R-e: field syntax on store handles (A149 S4)**, ruled to this order with its door chosen:
  `[internal]` fields stop resolving as members outside std, then `app.user.name` reads the handle.
  It is quality of life on a feature that already shipped. Rec: **build**, in store-47.
- **R-f: the cut at the seal.** v0.45.0: R-c's two flips are breaking. Rec: **v0.45.0 at the seal**,
  the perf verdict required by the cut script.
- **R-g: negative zero (N136).** `print(0.0 * -1.0)` prints `-0` on JS and `0` natively. Door (a):
  `print` formats numbers the language's own way on both backends (`0`). Door (b): native prints
  `-0`. Rec: **(a)**; it lands with `dbg`'s printer, which already has to define number printing.
- **R-h: the book takes element syntax (K26's second half)** and the std namespaces' new paths, in
  docs-47. Rec: **yes**.
- **R-i: Dependabot's two release-workflow bumps** (`upload-artifact` to v7, `download-artifact` to
  v8) merge at the START of this order, so a full order of CI sits between them and the next release
  run, and the cut's dry run exercises them. Rec: **yes**.
- **R-j: CI-class perf ceilings (M114).** After ten runs of the `perf` job on `next`, adopt its
  figures as the `ci` class's ceilings, so CI enforces more than the growth row. Rec: **yes**, in
  perf-47.
- **R-k: class writers append? (A155's open half.)** Today the last writer wins and a second writer
  warns. A census of real double-writes decides whether `.styled` + `class(..)` should combine. Rec:
  **census in papers-47, no build**.
- **R-l: carried, not in this order:** the opaque-returns hiding; the mirrored store if R-d is (a);
  incremental S5–S7; debugging S3, S5–S9; store S5; maps S4/S5; F1/F15/F17; F27 R5 (twin structs) and
  the rest of F28 with B548 and E266 (ruled 2026-10-05: Order 48); A87/A111/A131; B521; B183; E62; L15. Rec: **carry**.

## Mechanics (every lane)

briefs46.md's "Mechanics" stands in full (and, through it, 45's to 42's): worktrees
`vilan/.claude/worktrees/<lane>-47` off `origin/next` at the base and never the main checkout; the
item's text is a HYPOTHESIS; pins red first; one commit per item with its CHANGELOG entry and family
marker; ledger rows written `NEW`; `LANE-STATUS.md` untracked; native differential in both modes and
`check_scope_differential` in every std gate; five lanes at once, `CARGO_BUILD_JOBS=6`, nextest
`-j 6`, one cargo at a time; logs under `target/<lane>-scratch/`; kill by PID; the paper is the spec;
measure in instructions; **model Opus, never Fable**. Added to them, Order 46's lessons as RULES:

- **A lane never runs a git command in kolt or the website checkout.** It copies with `cp -r` to its
  scratch directory and changes into the copy by ABSOLUTE path in the same command. In Order 46 a
  broken command chain committed inside the real kolt checkout.
- **A lane PROBES BEYOND ITS ITEMS and files what it meets**, each with a minimal repro. Order 46's
  best finds came this way, and the owner asked for more of it. A find is filed, not fixed, unless
  it blocks the item.
- **Test programs import the traits whose methods they call and write a head's attributes in the
  canonical order.** Both are warnings now and errors at this order's cut.
- **An `#[ignore]` reason LEADS with its tracker id** (`B539: …`); `ci_ignored_pins` reads it that way.
- **std paths are the new ones** (`std::web::…`, `std::reactive::…`, `std::js::…`, `std::rpc::server`);
  an old path is refused with a steer.
- **A lane that changes analyzer.rs, mono.rs or an emitter says which functions it touched**, keeps
  the late-write count at zero (`VILAN_COUNTERS=1`; the inference suite runs with the assert), and
  runs `scripts/ci-local.sh perf`.
- **A lane's report is its final message.** The tool environment refuses report files from a lane;
  the integrator saves the text.
- **A lane whose base has moved in its files rebases before it is merged**, re-runs its FULL gates on
  the rebased tip, and says which base each number is from. The integrator names what changed.
- **Integrator: every merge's gates include `ci_ignored_pins` and `hygiene`**, each gate's crate is
  resolved from the tree, and a push never follows a piped test in one command.
- **Integrator: a push to `next` cancels the CI run before it.** Hold the next push until the running
  verdict is in, or merge two ready lanes back to back and read one run for both.
- **Integrator: reference perf ceilings are re-taken only at a seal**, on a quiet machine (load at or
  under 2), with one codegen unit. A lane reports its delta against its own base, never against a
  ceiling.

## Lane incr-47: M110 S0 + S1 + the edit-replay differential FIRST; then S2, S3, S4 as each measures (R-a); M115, M99, M73/M79, M101, M19 close as they are subsumed

1. **S0.** Per-item interface fingerprints (canonical resolved signature, inferred return, effects)
   and the global-facts fingerprint (impl headers, trait members, resource-ness, generated impls). The
   `[vilan phase] hot-set n/m interface-moved k global-moved b` line, and a scripted kolt session (ten
   keystrokes each in `views.vl`, `theme.vl`, `model.vl` and a css block) that reports, per edit, what
   moved. Per-edit counters join M105's tier 1 (Q9). No behaviour change.
2. **The edit-replay differential** (Q3): the incremental result against a clean analysis, byte for
   byte, over a scripted edit sequence; a planted bug per slice proves it red. `VILAN_INCREMENTAL=
   verify` for dogfooding on kolt. It blocks every slice from S1 on.
3. **S1, hot-set worlds.** Store the entry's world minus the edited module and its reverse import
   closure (import cycles included, Q2); a keystroke walks the hot set over the stored prefix. M19's
   terms are re-pointed. Acceptance on kolt, by `scripts/lsp-latency.py`: a world-mode keystroke in
   `views.vl` at or under 10 G (from 14.3 G), and base-cache hits per keystroke above zero.
4. **S2, S3, S4** in that order, each behind the differential, each reported with its measured win
   against the paper's estimate. STOP at the first that falls well short and say why.
5. Find References stays whole-entry throughout (the owner's condition from Order 46); its pin stays.

Sizing L. Owns the world, base cache and pass-driver layer in vilan-core, the LSP's analysis
scheduling, `scripts/lsp-latency.py`. perf-47 owns impl selection and emission; where they meet, this
lane rebases.

## Lane perf-47: M111 + M118 + M117 FIRST; then M113, M112, M114 (R-j), M60, M90, M109's remainder, F49, M89

1. **M111.** `impl_select::applying_implementations` is about 32% of kolt's check. Make the emitter's
   member selection hit its memo (or give it one keyed the way it asks). Acceptance: kolt's
   `vilan check` instructions down by a double-digit percentage, goldens byte-identical.
1b. **M118.** One kolt function, `Channel::find`, is 8.3% of the browser leg's solver work: 41,860
   type slots, where its siblings mint about 900. Two triggers, NOT additive: a coercion to `dyn Flow<..>` over a
   `match` of two stages, or an inline `match` in a `.derive` closure whose parameter type is not
   written. Either alone costs the full ~28k slots; annotating the parameter AND dropping the coercion
   brings it to 16k. Read the item's stamp. Likely one disease with M111, and the first real case for
   M106's "suggest an annotation" diagnostic. Acceptance: `find` as written costs within a small multiple of
   `messages`. Also make the per-declaration `selections` column count (it reads 0 everywhere).
2. **M117.** Why kolt's check costs 9% more with the store exhibits applied (client `Account` +0.56 G,
   server store +2.11 G). Attribute it with `--explain-cost` and callgrind, then fix what is the
   compiler's (a derive that expands to more than it needs, a blanket chain selected per site) or
   report what is inherent. The store exhibits patch and R-d wait on this answer.
3. **M113.** Above 50k lines the doubling costs x2.33. Find the next superlinear lookup.
4. **M112, M114.** The generated app's emission-walk share is 18.6 points off kolt's: fix the
   generator. Adopt the `ci` class's ceilings from the job's first ten runs (R-j).
5. **The copies.** M60 (`SignalCell::get()`/`set()` deep-copy), M90 (a read-only `let` of a struct
   field deep-copies on JS), M109's remainder (a dead `mut` capture cloned on write-back in the
   multi-payload step), F49 (native: a `&self` call on a boxed binding deep-copies). Each pinned by
   a COUNT of clones, as B509's pin does.
6. **M89** if time: dedupe vtables by slot set at emit.

Sizing L. Owns impl_select.rs, the emitters' selection and copy paths, `scripts/perf_*`,
`perf/budgets.toml`'s `ci` rows.

## Lane debug-47: debugging.md S0, S1 + S1b, S2, S4 (R-b); E258, E260, E259; N136 (R-g). REBASES onto solver-47

1. **S0, `[track_caller]`.** `panic`, `assert`, an index out of bounds and `unwrap` report their
   vilan file, line and column on both backends, in release builds too (Q11). Closes E258.
2. **S1, `dbg(..)`** as a compiler intrinsic: any number of arguments; prints
   `[file:line:col] expr = value` to stderr (`console.log` in the browser, Q3) through a generated
   printer that writes vilan's own literal syntax, identical on both backends (Q1: one line when it
   fits 80 columns, floats keep `.0`, no depth cut, at most 100 entries per container); returns its
   argument, a tuple for several (Q2); reads in place in statement position; refused in release
   builds, with `[build] dbg = "strip"` or `"keep"` (Q4).
3. **S1b.** std's handle types print as themselves (`Shared`, `SignalCell`, `HashMap`, `HashSet`,
   tasks); a `dyn` value shows its value; closures and pipes by type; cycles are cut.
4. **S2, `dbg_stack()`**, expanded statically from the scope (Q5): parameters, locals, captures;
   shadowed bindings marked; moved bindings say where; an invalidated view shows no value; a cell is
   read untracked; a pipe shows its type.
5. **S4.** Every type is debuggable through the printer; a written `Debug` impl overrides; the derive
   is redundant but stays valid (Q7). Closes E260.
6. **E259.** A generic function's instance has a readable name in the debug build, so a stack trace
   does not read `$a`.
7. **N136** per R-g, with the printer's number rule.

Sizing L. Owns the intrinsic's analyzer arm and both emitters' printer generation, `vilan-rt`'s
printing, std's `debug.vl`. New arms in `walk_expr_node_inner` go in their own `#[inline(never)]`
methods and the frame is re-measured.

## Lane solver-47: B533, B539, B540 (+ B530), B541, B542, B543 FIRST as a family (a type argument bound from the wrong place); then B544, B545, B537, B547, B501, B500, B438, B149, B443; the two flips' compiler half (R-c)

1. **The binding family.** A callee's `T` taken from the first of two providers (B533); a
   trait-annotated `let` not carrying the trait's arguments into its initializer (B539); a nullary
   variant binding that never grounds (B540, closing B530); an underdetermined mapped-tuple element
   reported as a mismatch (B541); a method call on another instance inside `impl SignalCell<type T:
   (2..)>` reading the block's `T` (B542); `entries()`/`get(key)` on a mapped tuple typed as the
   template (B543). Look for the shared cause before fixing six times.
2. **Payload views' residue.** `if held is Some(let v) { v += 1 }` still steers to `mut` (B544); a
   capture inside a tuple sub-pattern under `match &mut` is still a copy (B545).
3. **B537, B547, B501, B500, B438, B149, B443, B549** (B549 added 2026-10-05: `std::web::document`
   fails inside std in a browser build), each a pin and a fix; B367 reproduced or closed.
4. **The flips (R-c), LAST and only when the estate is clean:** B515's warning becomes a refusal
   (B535) and B536's attribute-order warning becomes an error. Count what still warns in std, the
   corpus, the docs, the examples and a scratch copy of kolt; fix the vilan repo's sites; write the
   kolt patch; then flip. Both carry their existing fix data.

Sizing L. Owns analyzer.rs, mono.rs, impl_select.rs's solver side, parsing.rs for B536's flip.

## Lane native-47: F90 FIRST (a runtime abort), then F89, F85, F86, F88, F50; the differential's refused list re-read

1. **F90.** `counts.write()[0] += 1` on a `Shared<List<i32>>` aborts natively: F83's indexed twin.
2. **F89.** A `match` on an indexed element whose payload is not `Copy` moves out of the list
   (rustc E0507); std carries three workarounds, removed with the fix.
3. **F85, F86, F88.** A closure handed to a generic callee without a written return; a variant
   constructor as a method receiver with a literal payload; `*{ &m }`.
4. **F50.** The two census gaps from the closure-captures paper.
5. **The refused list.** The whole-set differential still refuses 27 programs. Classify each (by
   design, a known item, a new find) and file what is new.

Sizing M–L. Owns vilan-rust, vilan-rt, the native fixtures.

## Lane editor-47 (wave 2): the quick fixes the flips need FIRST (B536's, B515's), then E253, E263, E264, E261, E262, E254, E265, N141. REBASES onto incr-47. LAST to merge

1. **The two quick fixes R-c depends on:** "reorder these attributes" over
   `parsing::marker_order_fix`, and "import this trait" on B515's warning. Each pinned; each offered
   as a fix-all for the file.
2. **E253.** Hover and go-to-definition on a call that takes a context closure (`switch_some(|v| ..)`).
3. **E263, E264.** The quick fix for B495's mode-mismatch refusal; element-head completion offers
   `.autofocus()` and not the bare attribute.
4. **E261, E262.** A `match` of two pipe stages steers to the `dyn Flow` annotation; the "declare
   `fun ..`" steer keeps a callback's `context` clause.
5. **E254.** A file holding platform-fenced twins is served from its entry's world.
6. **E265, N141.** `vilan fmt` formats `a + match {..}`; `assert_formats` asserts the reprint
   succeeded, so an identity pin can no longer pass on a decline. Re-run the ten identity pins and
   file what turns red.
7. **E269, E267** (added 2026-10-05): a bare `import std::web;` (v0.43.0's prelude-as-module import)
   gets the moved-path refusal and a fix (`import std::web::prelude as web;`); auto-import and the
   add-import fix read a package's NESTED modules, not only its top level.
8. **E270** (added 2026-10-05, the owner's item): `then` leading a line is highlighted (and `else`, if it has the same gap).
9. **B560** (added 2026-10-05, the owner's item): the "import it first" steer spells a nested module's full path (same root as E267; the one analyzer.rs function is editor-47's for this).
10. E121's six rows re-measured on the merged tree, for the seal.

Sizing M–L. Owns vilan-lsp, vilan-ide, editors/vscode, formatter.rs for item 6.

## Lane store-47 (wave 2): A149 S4 (R-e), B547's std side, `store_opaque`'s removal, B546. After perf-47 reports M117

1. **S4.** `[internal]` fields stop resolving as members outside std; then the field-syntax tier
   (`app.user.name` for `app.user().name()`), with completion and hover.
2. **`store_opaque` goes** once a blanket reaches a closure through the two-tier
   `StoreLeaf` → `Storable` chain (B508's remainder; coordinate with solver-47).
3. **B546.** A focus scope installed after its content took focus remembers the wrong restore target.
4. If R-d is (b): the mirrored store's S1, only after M117's answer.

Sizing M. Owns `std::reactive::store`, `store_core`, the derive, the ui twins for item 3.

Added 2026-10-05 (the owner's item): **A158**, `List::push_many(iterable)`, as a std small on both backends.

## Lane docs-47 (wave 2): K26's book half (R-h), L16, N140, N142, N143, K24's remainder

1. **K26.** The book's UI snippets and `vilan/examples/` in element syntax; the style note from the
   website's README. Every fence still compiles under the docs gate.
2. **L16.** `std::markdown`'s strict-parse refusals enter the diagnostics ledger.
3. **Hygiene:** the stale ledger row (N140), the stale comments and the fixture workaround (N142), the
   std manifest's census comment (N143).

Sizing M. Owns `vilan/docs/`, `vilan/examples/`.

## Lane papers-47: A155's census (R-k), C15, the const-cache key if incr-47 asks; NO tree change

1. **A155.** A census of elements that write their class more than once in kolt, the site and the
   examples, and what each author meant. Doors: append, last wins with the warning, refuse. A rec.
2. **C15.** Spec §6.9's closure rule makes every mutably-captured binding shared: what it costs
   (probes, counts) and whether a narrower rule is sound.

Merges to proposals only.

## Ownership map (conflict avoidance)

- **analyzer.rs's inference and checks, mono.rs:** solver-47, then debug-47 rebased onto it.
- **impl_select.rs's selection memo, the emitters' selection and copy paths:** perf-47.
- **The world, base cache and pass drivers; the LSP's scheduling:** incr-47, merged after the three
  above and rebased onto them.
- **vilan-rust, vilan-rt:** native-47; debug-47 for the printer (coordinate on `inspect.rs`).
- **vilan-lsp, vilan-ide, editors/vscode, formatter.rs:** editor-47, after incr-47.
- **`std::reactive::store`, the derive:** store-47. **`vilan/docs/`, examples:** docs-47.
- **Merge order:** solver-47, native-47, perf-47, debug-47 (rebased), incr-47 (rebased), store-47,
  docs-47, editor-47 (rebased). papers-47 to proposals.
- **After every merge that moved goldens:** `regen_goldens.sh`, both native censuses, the copy census,
  the merge helper's BUILD step; CI on next read before the next push.
- **After the seal and CI green:** the cut (R-f), the fold, the toolchain in both locations and the
  vsix, kolt's patches, the website re-checked.

## At the sweep (integrator, proposals)

- Close per the reports. M110 stays open with its remaining slices named. E257 likewise.
- The seal runs `perf_gate.py seal` against v0.44.0 with `--advance`; E121's rows count their first
  green toward blocking.
- `diagnostics-ledger.md` prose for every `NEW` row, at each merge.
- Kolt at the owner's word: the flips' imports and attribute orders; the store exhibits if M117
  clears them.
- Order 48's queue: incremental S5–S7; debugging S3, S5, S6; the mirrored store; M106's diagnostic
  slice; whatever R-l carried.
