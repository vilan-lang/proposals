# Order 46 — THE EDITOR AND THE CLOCK: entry-world analysis and the editor items the owner filed, the memory regression and the remaining superlinear passes, the performance gates built, two JS miscompiles and a native runtime abort, the opaque-returns build, `when_all_some` and the Store's next slices, and steering for foreign spellings (drafted 2026-10-03, off vilan next @fe092e8d; every ask RULED as recommended 2026-10-03; GO 2026-10-03)

**Base.** Order 45 sealed at dcb06444 on 2026-10-02; v0.43.0 was cut at that seal (tag a408d5db, release
run 37081371625 green 17/17) and FOLDED on 2026-10-03: `origin/main` = `origin/next` = fe092e8d. Nothing
has landed since. `## Unreleased` does not exist on next (0 entries). Toolchain `vilan 0.43.0
(fe092e8d1)` in both locations, and the 0.43.0 extension in the local VS Code server. Ledger max **610**
(lanes write `NEW`). Tracker **159 open**: 147 after Order 45's sweep, plus twelve filed since (A150–A153,
B520, B521, E246–E251). The shared census, the copy-elision census and the expr-walk frame are re-read
at the base by the first lane that touches each, and reported.

One thing is owed from the cut: the `release/0.42` branch and its worktree still exist (the owner's
hand; releases.md §7.3 step 5).

Kolt is on 0.43.0: `vilan check` 0 errors and 0 warnings, both legs build. `model.vl` is committed;
the maps patch on `store.vl` and the message row in `channel.vl` are the owner's to commit. Its browser
runtime is unverified since B519's fix.

**The shape.** Order 45 fixed what the pipe train broke. What is left is mostly how the tools FEEL, and
that is what the owner has been filing. Five things set the order of work:

1. **The editor is the complaint.** A `model.vl` keystroke with its importers open settles in about
   5.5 s (M104), a kolt keystroke costs 1.1–1.3 s of CPU to diagnostics against E121's 500 ms (M101),
   and an idle hover costs 6–10 ms (E245). M104's entry-world design is ruled and goes FIRST in the
   editor lane. Beside it, the items the owner filed from daily use: the hover struct hint (E246), the
   status bar menu (E247), stop/start commands (E248), blanket-impl methods missing from completion
   (E249), import quick fixes missing in struct literals and match patterns (E250), duplicate imports
   left by Organize Imports (E251).
2. **Performance is gated, not only measured.** M105 is ruled (Q1–Q12) and only its seal-time script
   exists. This order builds S2–S8: instruction counts in CI, `budgets.toml`, the kolt-shaped
   generator, the cut refusing without a verdict. The same lane pays down M108 (peak memory +27% on
   kolt, shipped in v0.43.0 as a written exception) and the three superlinear passes M107 still names.
3. **Three wrong-answer bugs go first in their lanes.** B511 (a qualified call to a blanket impl's
   member is not monomorphized, JS) and B514 (`*if c { &a } else { &b }` over a scalar prints the
   place pair, JS) in solver-a-46; F83 (a write in an effect run from a turn drain aborts natively) in
   native-46. B441 (a mis-shaped tuple destructure compiles and reads flattened slots) rides with the
   first two.
4. **Two ruled designs get built.** Opaque returns (ruled 2026-10-01, reversing Order 44's "checked,
   not hidden"), with B489–B491; and A152, the owner's `zip_some` / `when_all_some` / `unzip`, ruled
   in conversation on 2026-10-03.
5. **The language should meet people where they arrive from.** `return`, `fn`, `function` and `-> T`
   fall into generic parse errors today (B520). syntax-46 steers each one and the editor offers the
   rewrite. B486's marker-order steers and B485's remaining ruled steps land with it.

**Nine lanes plus papers, in two waves under the cap of five.** Wave 1: solver-a-46, native-46,
perf-46, editor-46, syntax-46. Wave 2, each started as a slot frees: solver-b-46, reactive-46,
store-46, site-46; papers-46 runs beside either wave (it builds nothing). Merge order:

1. solver-a-46 (the miscompiles; sha to LANE-STATUS.md as each lands);
2. native-46;
3. syntax-46;
4. perf-46 (rebased onto solver-a-46 if analyzer.rs conflicts);
5. solver-b-46 (rebased onto solver-a-46 and syntax-46);
6. reactive-46 (rebased onto solver-b-46);
7. store-46 (rebased onto reactive-46);
8. layout-46 (A154, added 2026-10-03: starts only after store-46 merges);
9. editor-46 (rebased; last: its printer and completion rows read what the others changed).

site-46 merges to the website repo on a branch; papers-46 to proposals only. A cut is proposed at the
seal (R-f).

## Asked at GO (the owner)

**RULED 2026-10-03: every ask as recommended** (R-c door (b); R-g by the count solver-a-46 reports).

- **R-a: E247, the status bar menu.** The item reads `vilan 0.43.0`; a click opens a quick pick with
  read-only rows (platform and why, the entry the file is analysed under, server version and sha, the
  last analysis' work counts), toggle rows (`vilan.inlayHints.enabled`, `.abbreviate`, the other
  feature switches; each writes the setting, which the extension already pushes live), and action rows
  (restart, stop, start, show status, open the output channel). Cost figures are WORK COUNTS, not
  milliseconds, matching the M106 ruling. Rec: **build as described**.
- **R-b: A151, the autofocus marker.** std writes `data-autofocus` instead of the native attribute;
  `focus_initial` reads `[data-autofocus]` and still honours a hand-written native `[autofocus]`. Rec:
  **yes**. It removes Chromium's once-per-page console message and changes nothing in kolt.
- **R-c: A150, a mirror's `state()`.** Door (a): `state()` on a `RemoteSource` LEASES, as `latest()`
  does. Door (b): `state()` stays a passive report and std gains `states()`, a leased pipe of the
  whole `TransientState`. Rec: **(b)**. R28's read-only face keeps its meaning, and kolt's hand-written
  `transient_of` becomes one std call. `TransientState::map`, `zip` and `and_then` land with it.
- **R-d: A153, the mirrored `Store`, is a PAPER this order.** Nothing built. Rec: **paper**. It needs
  A149 S3's keyed nodes before it can be probed honestly.
- **R-e: the deprecated names are removed.** `Map`/`Set` (deprecated in v0.42.0) and `MapCell`/
  `SetCell` and their entry and memo aliases (renamed by A148 in v0.43.0) go. Rec: **remove both**.
  Each has had its one release.
- **R-f: the cut at the seal.** v0.44.0: R-e, B515 (R-g) and the opaque-returns build are breaking.
  Rec: **v0.44.0 at the seal**, refused by the cut script without M105's verdict once S6 lands.
- **R-g: B515, trait methods that resolve with no import.** Once any loaded std module imports a
  trait, its methods resolve in user code that never imported it. Fixing it is BREAKING for programs
  that lean on the hole. Door (a): fix now; the refusal names the import and carries the quick fix.
  Door (b): warn for one release, refuse in v0.45.0. Rec: **(b)** if kolt or the estate has more than
  a handful of sites (solver-a-46 counts them first and reports), otherwise **(a)**.
- **R-h: B520's scope.** The four the owner named (`return`, `fn`, `function`, `-> T`) plus `func`
  and `def`. Other candidates (`null`/`nil`, `=>` closures, `let mut` order) only where a probe shows
  today's message is misleading. Rec: **the six, the rest on evidence**.
- **R-i: E236 stays a seal-time REPORT** for this order; it becomes a blocking budget when M105 S8
  (E121 rows blocking) lands and holds for one seal. Rec: **report, then gate through M105**.
- **R-j: site-46 pushes a BRANCH.** K26 rewrites the site, the playground examples and the docs to
  element syntax. A push to the website's `main` deploys, so the lane stops at a branch and the owner
  reviews the preview. Rec: **branch, owner merges**.
- **R-k: carried, not in this order:** M60, A87/A111, A131, B183's concrete arm, store S5
  (compiler-generated nodes), maps S4/S5, the on-disk world cache, the parallel-analysis paper, B521
  (after A152's call sites exist), B509, F1/F15/F17. Rec: **carry**.

## Mechanics (every lane)

briefs45.md's "Mechanics" stands in full (and, through it, briefs44's, 43's and 42's): worktrees
`vilan/.claude/worktrees/<lane>-46` off `origin/next` @fe092e8d and never the main checkout; the item's
text is a HYPOTHESIS; pins red first; one commit per item with its CHANGELOG entry and family marker;
ledger rows written `NEW`; `LANE-STATUS.md` untracked; native differential in both modes and
`check_scope_differential` in every std gate; tracker writes through `file_items.py` /
`stamp_items.py` / `close_batch.py`; the PATH export; kill by PID; the paper is the spec; **model Opus,
never Fable**. Added to them, Order 45's lessons as RULES:

- **Five lanes at once, no more.** Every lane exports `CARGO_BUILD_JOBS=6`, runs nextest with `-j 6`,
  and runs ONE cargo at a time. Eight unthrottled lanes took WSL2 down in Order 45.
- **Logs and scratch go under the lane's own `target/<lane>-scratch/`.** Never the shared scratchpad:
  one lane overwrote another's suite log.
- **A lane that adds or edits a `.vl` fixture runs `scripts/ci-local.sh vilan-fmt` before it
  reports.** Eight unformatted fixtures reached next in Order 45 and CI's leg sat red, unread.
- **A gate's crate is resolved from the tree** (`find crates -path '*/tests/<name>.rs'`), never from
  memory. The merge helper stopped twice on a wrong crate.
- **A pin that reads a clock, a debounce window or a path spelling says how it holds on Windows.** Two
  such pins were green locally and red on CI's Windows shard.
- **kolt is READ-ONLY.** A lane that wants a kolt change writes a patch file under
  `sweeps/order46/<lane>/` and says so in its report. The owner applies and commits.
- **A lane touching an analyzer pass reports instructions before and after** on kolt's `vilan check`
  (`scripts/lsp-latency.py` and `perf_compare.py` are the tools), not wall time.
- **The integrator watches CI on next after EVERY merge** and reads each red before the next merge.
- **A CHANGELOG fold moves entries by marker and head**, never by splitting on rules (the v0.42.1
  merge-back lost an entry that way).
- **The seal's perf leg runs on a quiet machine** (load at or under 2), after the lanes are reaped.

## Lane solver-a-46: the wrong answers. B511 + B514 FIRST, then B441, B512, B498, B510, B515 (R-g), B439, B502, B455's `(impl Box with One)`

1. **B511.** A qualified call to a blanket impl's member (`Same::same(a, b)` over
   `impl type T: PartialEq with Same`) is monomorphized like the method form. Both backends; the
   native half is in the item. Sha to LANE-STATUS.md at once.
2. **B514.** `*if c { &a } else { &b }` over a scalar or `str` reads the value on JS. This is B466's
   family at a conditional; check `match` and block-tail forms in the same pass, and B512 (an
   unannotated `let x = if c { &a } else { &b }` is not seen as a view binding) with it.
3. **B441.** `let (a, b, c, d, e, f) = ((1, 2), (3, 4), (5, 6));` is REFUSED: a destructuring pattern
   matches the value's shape, not its flattened slot count. Pin the nested forms that must keep
   working.
4. **B498, B510.** Two internal errors: a static trait call on a type bound only through an impl
   subject's nested binder; a trait default passing `self` to a generic over the same trait. Each
   becomes a working program or a real diagnostic.
5. **B515** per R-g. COUNT FIRST: the sites in kolt, the estate, the examples and the docs that
   resolve a trait method with no import. Report the count before building either door.
6. **B439.** The false "a view cannot escape its scope" for a `&mut` PARAMETER of a closure type.
7. **B502.** `measure<T, S: Shape<T>>` called with `dyn Shape<i32>` and then `dyn Shape<str>`.
   Observed once: reproduce it, or close it as not reproducible with the probe recorded.
8. **B455** as ruled (B): a selector spelled `(impl Box with One)` admits an impl block with no
   declarations, and the refusal's empty slot is filled.

Sizing L. Owns analyzer.rs, mono.rs, impl_select.rs and transformer.rs for these items.

## Lane native-46: F83 FIRST, then F66, F82, F70, F67, F69, F77, F48, F51, F78; output parity F68 + B503; E243

1. **F83.** `fired.write() += 1` in an effect run from a turn drain aborts "a cell was read while".
   Find which borrow is held across the drain; the fix is in vilan-rt or the emitted drain, not in the
   program. Add it to the native leak and differential gates.
2. **F66.** The variant-constructor type arguments derived inside generic instances. It is marked
   latent: build the program that makes it wrong, then fix it.
3. **The rustc refusals**, each with a native fixture: F82 (a swapped struct literal inside its own
   impl), F70 (a nested tuple index), F67 (a call of a local closure binding, then a member read), F69
   (a closure reaching its call through a match capture, a loop binding or a nested closure), F77 (an
   unannotated closure parameter in a closure-typed field), F48 (a reassigned closure-typed `mut`
   binding; a `List` of two closures), F51 (a captured value returned from a closure).
4. **F78.** A trait default calling an overridable hook reached through a blanket. Not live: pin it.
5. **Output parity.** F68 (`print` of a long `List` wraps on node and not natively) and B503
   (`List<dyn T>` prints `[value, {}]` pairs). One printer rule, both backends.
6. **E243.** The JS `vilan run` prints its asset report on stderr, so the two backends' stdout agree.

Sizing L. Owns vilan-rust, vilan-rt, the native fixtures; the JS printer rows for item 5 (coordinate
with solver-a-46 on transformer.rs).

## Lane perf-46: M108 + M107 FIRST, then M105 S2–S8, M106's first slice, M100, N137

1. **M108.** Peak memory on kolt is 1,030–1,079 MB against v0.42.1's 831–876. Attribute it (heap
   profile by pass and by table), then bring it back to v0.42.1's figure or report exactly what the
   remainder buys. The exception in v0.43.0's notes is closed or restated at the seal.
2. **M107's remaining three sites.** `vilan check` is close to quadratic in package size on generated
   plain code. Two passes were fixed in Order 45; the item names the rest. The acceptance is the
   doubling test: 24k to 49k lines costs about 2x, not 4x.
3. **M105 S2–S8**, per `proposal/performance-gates.md` as ruled:
   - S2 the CI perf job (instruction counts under callgrind or `perf stat`, not wall);
   - S3 `budgets.toml` with a tolerance per row;
   - S4 the kolt-shaped generator, so the gate does not depend on a private repository;
   - S5 `VILAN_COUNTERS`, the solver's own work counts;
   - S6 `cut-release.sh` refuses without a verdict;
   - S7 the nightly and per-release report;
   - S8 E121's rows blocking.
4. **M106's first slice**, with S5: per-item cost attribution. The compiler can say which declaration
   cost the most solver work. By the owner's ruling the measure is computational complexity (work
   counts), never elapsed time. The diagnostic itself (the suggestion to annotate) is a later slice;
   this one produces the numbers and a `--explain-cost` report.
5. **M100.** `check_workspace` starts every entry together instead of the first alone.
6. **N137.** `~/.vilan/check-cache` gets a bound (size or age) and a `vilan cache clean`.

Sizing L. Owns the pass drivers and tables in vilan-core for items 1–2, `scripts/` and `.github/` for
item 3, the counters. editor-46 owns the session and world layer: where M104 and M107 meet (the
per-entry world), editor-46 leads and this lane rebases.

## Lane editor-46: M104 FIRST, then M101, E245; the owner's items E246, E247 (R-a), E248, E249, E250, E251; B520's quick fixes; E214. LAST to merge

1. **M104, entry-world analysis**, as ruled. A file is analysed in the world of its ENTRY, once; an
   edit to `model.vl` with `client.vl`, `channel.vl` and `views.vl` open republishes all four from one
   analysis instead of one per document. Acceptance, by `scripts/lsp-latency.py` on kolt: the
   multi-document settle goes from about 5.5 s to within 1.5x of the single-document figure, and no
   document shows diagnostics from a stale world.
2. **M101, E245.** After M104, re-measure. 57% of a keystroke's CPU was post-analysis work (the
   editor tables, M27); the idle hover cost 6–10 ms with importers open. Fix what M104 did not.
3. **E249.** Completion asks the SOLVER which blanket impls admit the receiver, instead of keeping its
   own applicability rule. First establish which receivers miss (`MemoCell` against `SignalCell`
   against a pipe node) and whether hover and signature help miss too.
4. **E250.** Census every position an unresolved name can stand in (struct literal head, pattern head
   in `match`/`is`/`let`, impl subject and `with` trait, generic argument, bound, `[derive(X)]`, a
   static call's receiver, an element tag) and pin the import action at each.
5. **E251.** Organize Imports removes duplicates: identical lines collapse, a repeated name in one
   group is dropped, two lines over one module merge; a module import beside a member import merges into the `self`
   form (`import std::reactive::{ self, draft };`, `self` first); an alias is not a duplicate. The code action only (`vilan fmt` does not delete code). Idempotent.
6. **E246.** The struct hint gets a gap under the `name: Type` line and moves BELOW the doc comment.
7. **E247** per R-a, and **E248**: `vilan.stopServer` / `vilan.startServer`; stop does not
   auto-restart, clears stale diagnostics, and the status item says `vilan (stopped)`.
8. **B520's quick fixes**: the code actions over syntax-46's diagnostics (`return` to `ret`, `fn` to
   `fun`, `->` to `:`). Rebase onto syntax-46 for the codes.
9. **E214.** The auto-closed `>` no longer doubles when typed over.

Sizing L. Owns vilan-lsp, vilan-ide, editors/vscode, `scripts/lsp-latency.py`, and the session and
world layer in vilan-core.

## Lane syntax-46: B520, B486, B487, B493, B494, B485's remaining ruled steps, K26's grammar half, N138

1. **B520** per R-h. In the parser's recovery: `return` at statement head; `fn`/`function`/`func`/
   `def` at item head followed by a name and `(`; `->` after a parameter list. Each reports ONE
   diagnostic at the foreign token ("vilan spells this `ret`"), parses on as if the right spelling had
   been written so nothing cascades, and carries the data the quick fix needs. Ledger rows.
2. **B486.** Out-of-order markers get a steer that names the right order; all 29 adjacent swaps
   pinned. `[derive(..)] export struct` no longer steers to an import.
3. **B487.** `const fun` / `const let` carry `[deprecated]`, `[internal]` and `[must_use]`.
4. **B493, B494.** A label on a local `let` is refused in words that fit a local; `async x = 1;` gets
   a real message.
5. **B485's remaining ruled steps** (keywords-vs-attributes.md Q7, Q8, Q10 with the 2026-10-02
   amendment: field and variant attributes stay inline): whatever the formatter and the parser do not
   yet do. Read the paper against the tree first and list what is left.
6. **K26's grammar half:** `only` in the two toolchain grammars (TextMate and the playground's),
   and K24 if the playground's keyword list can be generated from the same source.
7. **N138.** CI's `vilan-fmt` leg stops scanning `target/`.

Sizing M. Owns lexing.rs, parsing.rs, formatter.rs, the grammars.

## Lane solver-b-46 (wave 2): the opaque-returns build, B489 + B490 + B491, then inference B499, B501, B513, B516, B440, B442, B447, B508, B518, B497. REBASES onto solver-a-46 and syntax-46

1. **Opaque returns**, per `proposal/opaque-returns.md` as ruled: `fun f(): Trait` hides the callee's
   type from the caller. The paper's slices in order; both emitters.
   - **B489** with it: a bare-trait return's type arguments reach the body.
   - **B490, B491**: the `[rpc]` refusal points at the method, and the steer prints `dyn Source<i32>`
     with its arguments.
   - Count what moves in kolt and the estate, and write the kolt patch.
2. **The inference holes**, each a pin and a fix: B499 (`Source::get(cell)` infers the trait's `T`
   from the receiver), B501 (expected-type inference through a generic argument), B513 and B516 (a
   closure's parameters typed from an annotated result, and from a closure-of-closure annotation),
   B440 and B442 (mapped parameters), B447 (integer literals in tuples in a list literal).
3. **B508.** A blanket `impl type T with Trait` reaches a closure type.
4. **B518, B497.** The printer parenthesises a closure parameter that is itself a closure; the "never
   fully determined" steer says `HashMap`.

Sizing L. Owns analyzer.rs, mono.rs and impl_select.rs after solver-a-46's merge.

## Lane reactive-46 (wave 2): A152, A150 (R-c), A151 (R-b), R-e's removals, B480's re-check, M60 if time. REBASES onto solver-b-46

1. **A152**, as ruled 2026-10-03:
   - `reactive::zip_some((a, b, ..))`: a tuple of `Flow<Option<T>>` to `Flow<Option<(A, B, ..)>>`.
     Value level, stateless, on `combine`'s per-arity mechanism.
   - `ui::when_all_some((a, b, ..), |(a, b, ..)| ..)` on BOTH ui twins: the body takes ONE parameter,
     a tuple of `SignalCell`s. The cells are created under the body's owner when everything turns
     `Some`, updated in place while it stays `Some`, released when any part goes `None`.
   - `SignalCell<(A, B)>::unzip()`.
   - NOT built: a `zip` answering a flow of flows.
   - The kolt patch: the message row written with it.
2. **A150** per R-c: `states()` on a mirror, `TransientState::map` / `zip` / `and_then`; `state()`'s
   doc says in its first line that it does not lease. The kolt patch removes `transient_of` and
   `map_state`.
3. **A151** per R-b: `data-autofocus`. A121 §6.1's comment is corrected.
4. **R-e:** remove `Map`/`Set` and the `MapCell`/`SetCell` family of aliases; the refusal for the old
   name steers to the new one for one more release.
5. **B480's shape in kolt:** `Channel::find` still writes `switch<TransientState<Channel, RpcError>>`
   with a `match` of two `dyn Flow` arms. Reproduce on the base; fix or file what remains.
6. **M60**, only if the first five are merged: `SignalCell::get()` and `set()` deep-copy.

Sizing M–L. Owns reactive.vl, transient.vl, rpc.vl's mirror, both `ui.vl` twins.

## Lane store-46 (wave 2): A149 S3, then S6; S4 if solver-b-46 has merged. REBASES onto reactive-46

1. **S3**, per REPORT-store-45.md's plan: map, set and list FIELDS as keyed and sequence nodes (`at`,
   `contains`, `MapOp`/`SetOp`/`SeqOp` out; `reconcile_to` on whole writes; `by_key` for keyed
   lists).
2. **S6:** the kolt exhibits as a patch (`Account`, `ChannelRecord`/`GlobalStore`), on top of the maps
   patch already applied.
3. **S4**, if time: field syntax on handles (`app.user.name` for `app.user().name()`), with
   completion and hover. It is a member-resolution rule: it lands only after solver-b-46.

Sizing M–L. Owns store.vl, the derive, hash_map_cell.vl and hash_set_cell.vl for the node forms.

## Lane layout-46 (wave 2, LATE): A154 + F28's first half. Starts after store-46 merges; editor-46 rebases onto it

Mechanical, and BREAKING by ruling (2026-10-03): no forwarding modules.

1. **Census first:** every std path the compiler names as a string (lang items, the `[rpc]` /
   `[service]` / `[derive(..)]` expansions, element syntax and `css`, the prelude tables,
   `infer_platform`, every steer that prints an import), in the LSP's import action, in the docs.
2. **A154's map:**
   - `std::web::{ dom, ui, style, dev, router, storage, document, asset }`; `web.vl` becomes
     `std::web::prelude`, and `vilan.toml` reads `prelude = "std::web::prelude"` (the old value gets
     the steer). `ui::` and `style::` stay ambient under the web prelude.
   - `std::reactive::{ hash_map_cell, hash_set_cell, transient, store, delta }`.
   - `std::js::{ null, promise, native_map }`.
   - `std::rpc::server` (was `rpc_server`).
   - Everything else stays where it is.
3. **The old path is refused with a steer** ("`std::dom` moved to `std::web::dom`") carrying the
   quick-fix data, from one table of old-to-new paths.
4. **F28's first half:** the thirteen single-platform modules leave `src/browser/` and `src/process/`
   for a file-level `[platform(..)] mod self;`. Prove first that the file-level fence gives the same
   cross-platform import error and the same editor platform inference as the layer did. The `ui` twin
   pair STAYS layered (its structs differ; one file needs F27 R5, not built).
5. The docs' std pages, the book, the examples and the corpus move with it; a kolt patch and a note
   for site-46's branch.

Sizing L, mechanical. Owns std's file layout and the path table; touches every std importer.

## Lane site-46 (wave 2): K26, K14, K15; the website repo, a BRANCH (R-j)

1. **K26.** Element syntax (`<div class(..)> … </div>`) wherever it applies on the site, in the
   playground examples and in the docs. Every changed example is compiled by the v0.43.0 playground
   wasm before it is committed.
2. **K14.** The playground's buffers carry the prelude; no example teaches a removed spelling
   (`.map` on a cell, `Map`, `MapCell`).
3. **K15.** The playground says when the formatter declined.

Sizing M. Owns the website repo. Does not push `main`.

## Lane papers-46: A153 (R-d), B495, B509; NO tree change

1. **A153, the mirrored `Store`.** What a `[rpc]` returning `Store<T>` or `StoreSome<P>` puts on the
   wire (the seed frame, then slot-addressed patches); leases mapped to slots; keyed and sequence
   nodes; identity and the contract hash; reconnect; what kolt's `GlobalStore` and `model.vl` become.
   The owner's rule and its amendment are in the item. Doors and recs; probes on v0.43.0.
2. **B495.** Views in closure types: the side table keyed by the written annotation's type id.
3. **B509.** A pattern that binds a writable view into an enum payload.

Merges to proposals only.

## Ownership map (conflict avoidance)

- **analyzer.rs, mono.rs, impl_select.rs, transformer.rs:** solver-a-46, then solver-b-46 rebased
  onto it. perf-46's pass work lands between them and rebases if it conflicts.
- **vilan-rust, vilan-rt, native fixtures:** native-46.
- **lexing.rs, parsing.rs, formatter.rs, the grammars:** syntax-46.
- **The pass drivers, tables and counters; `scripts/perf_*`, `budgets.toml`, `.github/`:** perf-46.
- **vilan-lsp, vilan-ide, editors/vscode, the session and world layer, `scripts/lsp-latency.py`:**
  editor-46.
- **reactive.vl, transient.vl, the rpc mirror, both `ui.vl` twins:** reactive-46. **store.vl, the
  derive, the cell files:** store-46.
- **The website repo:** site-46.
- **Merge order:** solver-a-46, native-46, syntax-46, perf-46, solver-b-46 (rebased), reactive-46
  (rebased), store-46 (rebased), layout-46, editor-46 (rebased). papers-46 to proposals; site-46 to a branch.
- **After every merge that moved goldens:** `regen_goldens.sh`, the copy census regenerated over the
  merged tree, the merge helper's BUILD step, and CI on next read before the next merge.
- **After the seal and CI green:** the cut (R-f), the fold, the toolchain in both locations and the
  vsix, the website re-checked against the new compiler.

## At the sweep (integrator, proposals)

- Close per the reports. M105 closes when S8 lands, or stays open with what is left named. M108
  closes only on a measured figure.
- `seal.sh` runs M105's verdict once S6 exists; until then `perf_compare.py` against v0.43.0.
- `diagnostics-ledger.md` prose for every `NEW` row and re-key, at each merge.
- Kolt at the owner's word: A152's message row, A150's removal of `transient_of` / `map_state`, the
  opaque-returns moves, store S6's exhibits, B515's imports if door (a) or (b) flags any.
- Delete `release/0.42` if it still exists (the owner).
- Order 47's queue: A153's ruling and build; store S4/S5 as store-46 leaves them; M106's diagnostic
  slice; the on-disk world cache and the parallel-analysis paper; M60, A87/A111, A131; B521; B509's
  ruling.
