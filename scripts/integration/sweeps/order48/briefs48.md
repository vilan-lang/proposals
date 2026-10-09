# Order 48 — the incremental order, part one (base: next @e75bc57c = the v0.45.0 fold)

Drafted 2026-10-08 from `go-items47.json`'s `order48_queue`, which the owner RULED 2026-10-05: Order 48 = M121 door (b) + B553, M110 S4, E279 sticky spans, N151 std-once-per-test, the analyzer pass-map paper — with other lanes on DISJOINT areas; Order 49 = M110 S2 + S3 ALONE in the analyzer core; then the S5 spike decides S6/S7. Theme stays: performance, bug fixes, quality of life; lanes probe beyond their items and file what they meet.

## Asked at GO (the owner; each with its recommendation — the order proceeds on the recommendations unless overruled)

- **R-a.** A162's flip (a visible double class write is an ERROR) lands at THIS order's cut, v0.46.0, once A159/A160 close the warning's gaps (0 sites). Rec: yes.
- **R-b.** B568 (a struct literal writing a std-`[internal]` field is refused outside std) is breaking at v0.46.0. Rec: yes (estate to count first).
- **R-c.** A153, the mirrored store's S1 (with C15's one-struct option): NOT this order (the analyzer core is incr-48's and S2/S3 follow); rec: Order 49 beside S2/S3, on std's side of the ownership map.
- **R-d.** debugging.md S2 `dbg_stack()`: debug-48 attempts it after E275–E277 only if its four prerequisites (the scope's bindings with shadowed ones as `Ref` uses, the move checker's and view-invalidation verdicts before expansion, the capture plan) are met by what the tree has; otherwise it files what is missing and stops. Rec: attempt.
- **R-e.** M123 (the bound audit is 10.6% of kolt's check): solver-48 measures first and builds the memo only if the profile confirms. Rec: yes.
- **R-f.** The cut: v0.46.0 at the seal (breaking: A162, B568). Rec: yes.
- **R-g.** native-48 takes native-47's refused list in estate order (F92, F99, F97, F95, then the rest) after the ruled F49/F103/F102. Rec: yes.

## Mechanics (every lane)

briefs47.md's "Mechanics" stands in full (and through it 46's to 42's): worktrees `vilan/.claude/worktrees/<lane>` off `origin/next` at the base, never the main checkout; an item's text is a HYPOTHESIS; pins red first; one commit per item with its `## Unreleased` CHANGELOG entry and a family marker the cut classifies (`breaking`, `miscompile`, `fix`, `feature`, `performance`, `diagnostics`, `tooling` — never `perf`); ledger rows `NEW`; `LANE-STATUS.md` untracked; the native differential in both modes and `check_scope_differential` in every std gate; five lanes at once, `CARGO_BUILD_JOBS=6`, nextest `-j 6`, one cargo at a time; logs under `target/<lane>-scratch/`; kill by PID; measure in instructions; **model Opus, never Fable**; a lane never runs a git command in kolt or the website checkout; a lane probes beyond its items and files what it meets with a minimal repro; test programs import the traits they call and write attributes in canonical order (both are ERRORS since v0.45.0) and use the new std paths; an `#[ignore]` reason leads with its tracker id; a lane that changes analyzer.rs, mono.rs or an emitter names the functions, keeps late writes at zero and runs `scripts/ci-local.sh perf`; the report is the final message. Added from Order 47:

- **A native test builds its OWN program name.** The suite's shared target keys binaries by name; two tests building one name at once run each other's binary (the seal's one red, `s0_caller_and_a_caught_panic`).
- **Never leave a load generator running** (`yes`, `stress`, a loop): the seal's perf leg trusts load < 2 and the self-hosted CI runner shares the machine. Kill by PID and confirm.
- **A rebase re-runs the FULL gates** and regenerates goldens on the rebased tree rather than carrying them through (debug-47's 123). The integrator sends the rebase order; a lane does not rebase onto another lane's branch unless told.
- **Scripts the tree ships must say what they need**: Python ≥ 3.11 (`tomllib`) and gawk-or-portable awk were the two faults the self-hosted runner found (N152).
- **kolt's generated inputs (`src/lucide`, `src/search-dict`) are gitignored**: any copy of kolt must carry them (`perf_gate.py prepare_kolt` does).
- **Integrator:** every merge gates `ci_ignored_pins` + `hygiene` with crates resolved from the tree; a push never follows a check in one command (read, THEN push); a push to `next` cancels the running CI; reference ceilings only at a seal; the cut keys the perf verdict by the TARGET sha; after a host reboot the runner container is started by hand (runner/README.md).

## Lane incr-48 (wave 1): M121 door (b) + B553 FIRST; then M110 S4; M122, B554 as it meets them. ALONE in the world, the base cache and the pass drivers

1. **M121 door (b), with B553.** Before the stored prefix RESOLVES, pre-walk the hot set's — and the ENTRY's — impl headers and member signatures into it (bodies stay post-store), so an impl the prefix can reach is visible; the impl guard stands down for that case; the use-inferred-binding guard stays. B553's impl half closes with it (an entry's impl is visible to every module); say what B553's context half (`Context::new()` grounded only by an entry `run`) needs and build it if the same pre-walk carries it. Acceptance: kolt's `theme.vl`, `model.vl` and `styles.vl` keystrokes SERVED (the S0 session table re-taken: hot-refusal 0 on all four files), every planted bug still red, the differential green on both legs.
2. **M110 S4, the const cache:** a const result keyed by its site's content, the content hashes of its callee closure, its tracked input files and std's stamp (`M33`'s content-keyed expansion table is the model); the differential with const edits (a callee edit, an input-file edit, a std bump); a hit counter under `VILAN_COUNTERS`; `vilan check` and the LSP both. Expected: −16% of a keystroke (the paper), the const pass's ~600 ms CPU per `views.vl` keystroke gone on a hit.
3. **M122** (a broken-body keystroke is ~25% cheaper: find what stops downstream and whether a CLEAN keystroke could skip it) and **B554** (blame by file name = order dependence; the differential's class) as the work meets them: measure, file or fix.
4. Re-take the kolt session table (S0's `--session`) and E121's six rows on a quiet box against base e75bc57c.

Sizing L. Owns `analyzer.rs`'s world, base cache, pass drivers and `analyze_inner`/`analyze_over_world`; `incremental.rs`; the const pass; vilan-lsp's scheduling. Nobody else touches these this order.

## Lane solver-48 (wave 1): B566 + B567 (two ICEs) FIRST; then B557 → B443, B562, B501's remainder, B545's view half, B558, B559, B563, B564, B565; M124's rule; M123 measured

1. **B566, B567:** internal compiler errors (a trait default with its own generic calling its bound's member; a blanket whose subject is a trait). A refusal with a span, or the feature; never a panic.
2. **B557, then B443:** a tuple-family blanket is admitted for non-tuples at the bound check; fix the admission, then land solver-47's two std blankets (`compare.vl`'s position-by-position `eq`, `hash.vl`'s `canonical_hash`, kept in `sweeps/order47/solver-47/finds/`) so tuple `==` and tuple keys work; E260's tuple `Debug` case un-ignores (debug-48 reads it).
3. **B562** (a method on a scalar view auto-derefs, transparent-references R4; RULED a bug), **B501**'s nested-call remainder (the ignored pin), **B545**'s view half (the paper's one-slot tuple leaf as a view), **B558**, **B559**, **B563** (conformance compares a callback's `context` clause), **B564**, **B565**.
4. **M124:** write the rule for what an object provides a blanket trait at (B533's ambiguity rule touches it), then the cheap fix; the one answer that moves (`a142_s4_filter_map_and_any_over_transients`: `bool` → `T`) is accepted only if the rule says so.
5. **M123** (R-e): profile `check_generic_bound_satisfaction` on kolt at the base; memoize only what the profile names.

Sizing L. Owns `analyzer.rs`'s inference and checks (not the world/drivers — incr-48's), `impl_select.rs`, `mono.rs`. The two lanes meet at `resolve_world` and `analyze_over_world`: solver-48 adds nothing there without telling the integrator.

## Lane native-48 (wave 1): F49 + F103 + F102 FIRST (RULED); then F107, F104, F105, F106, F108; then the refused list (R-g)

1. **F49 + F103:** a `&self` method call or a FIELD read on a boxed binding deep-copies the whole value natively; read through the borrow (`read_with`) with the evaluation-order question answered in the spec note (closure-captures.md Q4 ruled: fix before the store's server half runs natively). **F102:** the reentrancy abort (a closure writes a captured binding while a `&mut` view is live) becomes a compile-time refusal, the way F39 was answered.
2. **F107** (B149's native half: an `async fun`'s call assimilated), **F104**, **F105**, **F106**, **F108**.
3. **The refused list** in estate order: F92 (a generic call's type read unsubstituted; 3 programs), F99 (non-plain `const`; 4 programs), F97 (`for` over a user iterator / `HashSet`), F95 (guarded match legs), then F100, F98, F96, F101, F93, F94 as time allows. The whole-set counts (129/102/27/0 at the base) move with each; report the new triple.

Sizing L. Owns vilan-rust, vilan-rt. debug-48 owns `vilan-rust/src/dbg.rs` and the printers: coordinate on `inspect.rs` and `show.rs`.

## Lane debug-48 (wave 1): E275, E276, E277, N149 FIRST (RULED); S1b's `dyn` show slot; E260's tuple case after solver-48's B557; S2 `dbg_stack()` (R-d); S3 as its reuse allows

1. **E275:** a written or derived `Debug` impl decides how `dbg` prints that type; `[derive(Debug)]` spells variants qualified (`Shape::Circle(1.5)`); `.debug()` stays opt-in. **E276:** `dbg(-0.0)` prints `-0.0` (`print` keeps `0`). **E277:** scalar lists fill lines to 80 columns. **N149:** `print(x)` with `x: T` at a float instance is wrapped per instance. Both backends byte-identical; the committed stderr goldens move once.
2. **S1b's `dyn`:** a `show` slot in the dyn tables of both emitters, so a `dyn` value prints its contents.
3. **E260's tuple case** once B557 is on next (the ignored pin un-ignores; rebase onto solver-48 when the integrator says).
4. **S2 `dbg_stack()`** per R-d; **S3** (`print` of non-scalars through `printer.rs` / `__dbg_layout` / `vilan_rt::show`) if S2 leaves room.

Sizing M–L. Owns `printer.rs`, `transformer/dbg.rs`, `vilan-rust/src/dbg.rs`, `vilan-rt/src/show.rs`, `track_caller.rs`, std's `debug.vl` and the `Debug` derive. REBASES onto solver-48.

## Lane editor-48 (wave 1): E279 FIRST; E254; E273, E274, B561, B572; E121 at the seal. REBASES onto incr-48; LAST to merge

1. **E279, sticky spans:** on every `didChange` the server shifts its cached diagnostics, inlay hints, semantic tokens (delta protocol), references and quick-fix spans by the edit's delta BEFORE the re-analysis lands; republishes diagnostics at once; answers requests from the shifted set until the new analysis replaces it. Pin: a scripted edit above a diagnostic moves its published range before any analysis runs (the counters prove none ran).
2. **E254:** a file holding platform-fenced twins is served from the world of the entry whose platform admits each leg (incr-48 owns the world: E254 reads it through `hot_seeds`/`analyze_world`'s existing seam; name the seam, add nothing to the drivers).
3. **E273** (a named function with a mismatched mode gets B495's steer and the adapter fix), **E274** (completion on a generic struct offers only the impls at ITS arguments), **B561** (B535's message spells a nested package module's path; reuse B560's walk), **B572** (the steer prefers the shortest PUBLIC path over the declaring internal module: `std::reactive::store::Store`, not `store_core`).
4. E121's six rows on the merged tree at the seal (the integrator runs them; the lane re-checks the `shared.vl` row once N150 lands).

Sizing M. Owns vilan-lsp, vilan-ide, editors/vscode, formatter.rs. The `then`-grammar, quick-fix and auto-import code from editor-47 is its own now.

## Lane std-48 (wave 2): A159 + A160 then A162's flip (R-a); B568 (R-b); A161; E271, E272; K30; B555

1. **A159, A160:** the class-written-twice warning covers `.bind_attr("class", ..)` and `.toggle_attr("class", ..)`, and says the truth when the earlier writer is reactive. Then **A162:** the visible double write is an ERROR (family breaking; estate counted across kolt, the website and the examples: 0 expected).
2. **B568:** a struct literal writing a std-`[internal]` field is refused outside std (and say what a destructuring pattern naming one does); breaking; estate counted.
3. **A161:** `[T; n]` implements `Items<T>`. **E271, E272:** the element-hole and fragment-where-a-View diagnostics (span on the hole, the i-string / `.derive` steer; "a fragment is not a View, wrap it" — the book promised it). **K30:** `vilan init`'s two UI templates in element syntax. **B555:** `import std::js::null;` (a keyword-named module) is importable or refused with a steer.

Sizing M. Owns std (`web::ui` twins, `iterator.vl`, `list.vl`, `js`), the templates, the element-syntax diagnostics in `analyzer.rs`'s UI checks (name the functions; not the world, not inference).

## Lane layout-48 (wave 2): F28's retry; B548; E266; B549; B556. REBASES onto incr-48

1. **F28 (the retry) + E266 + B548:** std's layer DIRECTORIES dissolve into `[platform(..)] mod self;` fences (F27's); `infer_platform` reads the fences, not the directories; a twin import binds the IMPORTING FILE's platform side, not the build's. **B549** closes with B548 (`std::web::document` in a browser build).
2. **B556:** `cd src && vilan check main.vl` finds the package (the manifest walk from the file's canonical path, not the bare argument).

Sizing M–L. Owns module resolution (`resolve_import`, the loader, `infer_platform`), std's directory layout. It meets incr-48 in the loader: it rebases onto incr-48 and re-runs the differential.

## Lane suite-48 (wave 2, LAST): N151 (RULED, measure-first); N150; N152; N142's patch; N147, N148; M125's re-calibrate

1. **N151:** where the suite's time goes (measure the std share per test binary first), then one std world per test binary extended per test through S1's `load_hot_modules` (the harness's `Workspace` takes it), the differential green with the shared prefix on; wall time of `cargo nextest run --workspace -j 6` at load < 2 before and after. nextest partitions and the slow tests' own fixes as doors (b) and (c).
2. **N150** (`lsp-latency.py`'s `shared.vl` scenario anchor), **N152** (the cut's awk rewrite runs the same under every awk, or `cut-release.sh` requires gawk loudly, and the Python floor is stated the same way), **N142** (apply `sweeps/order47/docs-47/finds/n142-analyzer-comments.patch`), **N147**, **N148**, and **M125** re-run at the end (`perf_gate.py calibrate --kolt-tree`) with S4 on next.

Sizing M. Owns the test harness, `scripts/`, `.config/nextest.toml`. Rebases last.

## Lane papers-a-48: the analyzer PASS MAP (the prerequisite for Order 49's S2/S3 and the S5 spike). NO tree change

Every pass the analyzer runs (`analyze_inner`, `analyze_over_world`, `post_analysis_passes`, the world's resolve, the checks, the const pass, the emitters' pre-passes): its inputs, its outputs, what it mutates, its ORDER DEPENDENCE (what breaks if it runs earlier/later; which fixpoints), its cost on kolt (instructions, from `VILAN_PHASE_TIMING`/`--explain-cost`), and which of S2/S3's tables it becomes. A section listing the order-dependent special cases to DELETE (B553, B554, the top-level-only walks B560/B561/E267, the macro-reference order incr-47 found) and the invariants the differential proves. Ends with numbered questions and recommendations for Order 49. To `proposals/projects/vilan/proposal/analyzer-pass-map.md`. Sizing L.

## Lane papers-b-48: B569 (named tuple fields), B570 (`auto` annotations), B571 (`EXP as T`, with E278). NO tree change

Three papers to `proposals/projects/vilan/proposal/` (`named-tuple-fields.md`, `auto-annotations.md`, `type-ascription.md`), each from its item's stamped rulings (B569: by-name literal matching, same-label-set-reordered refused/warned; B571: `as` is a constraint never a cast, the whitespace rule, `as (T)` escape; B570: the six accepted points), each with the grammar, the estate counts (assignment-as-expression for B569; `as` in expression position for B571: 0), the interaction with the other two, and numbered questions with recommendations. Sizing L.

## Ownership map (conflict avoidance)

- **The world, base cache, pass drivers, const pass, LSP scheduling:** incr-48 — nobody else.
- **Inference and checks, impl_select, mono:** solver-48. **UI checks (element holes), std:** std-48.
- **vilan-rust, vilan-rt:** native-48; **printers, dbg, track_caller, Debug derive:** debug-48.
- **vilan-lsp (not scheduling), vilan-ide, vscode, formatter:** editor-48.
- **Module resolution, loader, infer_platform, std layout:** layout-48. **Harness, scripts:** suite-48.
- **Merge order:** solver-48, native-48, debug-48 (rebased onto solver), incr-48 (rebased onto solver), editor-48 (rebased onto incr), std-48, layout-48 (rebased onto incr), suite-48 (rebased last). Papers to proposals.
- **Waves:** wave 1 = incr-48, solver-48, native-48, debug-48, editor-48 (five). papers-a-48 takes the first freed slot, then std-48, layout-48, papers-b-48, suite-48 as slots free.
- **After every merge that moved goldens:** `regen_goldens.sh`, both native censuses, the copy census; CI on next read before the next push.
- **At the seal:** `seal.sh` with `VILAN_PERF_KOLT_COMMIT` = the owner's current kolt commit that checks under both 0.45.0 and the tip (or a prepared tip copy if A162/B568 touch kolt), E121's six rows quiet, the e121 state reset only if a seal is re-run; then the v0.46.0 cut (R-f), the fold, toolchain both locations + vsix, kolt's patches, the website re-checked.
