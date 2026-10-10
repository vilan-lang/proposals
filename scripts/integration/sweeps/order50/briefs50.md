# Order 50 — the incremental order, part three: the seeded fixpoints by mutation log, windowed ids, and the true editor numbers (base: next @5fe24f86 = the v0.47.0 fold)

Drafted 2026-10-10 from `go-items49.json`'s `order50`, the owner's rulings of 2026-10-10 (recs accepted: R-l's S3 re-plan, the E121 reset → E292, the spike's three answers) and the pass map's §7.2 design note. The theme stays: performance, bug fixes, quality of life; lanes probe beyond their items and file what they meet. The two measured truths this order answers: a kolt keystroke is 570–810 ms CPU on the reference box (E292), and the fixpoints are ~183 ms of a ~480 ms served analysis.

## Asked at GO (the owner; each with its recommendation — the order proceeds on the recommendations unless overruled)

- **R-a. The core-alone rule, as in Order 49.** incr-50 is the ONLY lane in the analyzer core in wave 1; it hands back at checkpoints (C1 = S3 by mutation log, C2 = S6's windowed ids, C3 = M134's anchors if time). solver-50 and debug-50 launch at C1 and rebase onto C2/C3; lang-50 (the array-lengths slices, which change `Type::Array`) launches at C2. Rec: yes.
- **R-b. S6's scope this order:** windows for all three id lanes laid out by the walk, TYPE windows sized from the item's previous demand (×1.5; first analysis ×8 + spill; an overflowing re-walked item re-laid out at the end), the run-length `type_id_sources`, anchors for the resolve's prepped drains, the two new differential classes (`frozen_entity` over a relocated resolve-time entity in a std item; a B217 re-anchor through a generated-expansion window), the "body edit re-walks one module" pin, `writes_other == 0` and `relocated_outside_anchor == 0` as standing counter pins. S7 (per-item records, the edited item's diagnostics first) is Order 51's unless M134's anchors land at C3. Rec: yes.
- **R-c. B602, B579's float scope:** `f64 * i32` (a float and an integer) refused like the integer pairs, breaking at v0.48.0 after the estate is counted. Rec: yes.
- **R-d. B599, fill-from-use:** a binding's hole filled from the argument and receiver channels (kolt's B580 annotation becomes unnecessary; not breaking). Rec: yes.
- **R-e. F122:** large fixed arrays boxed natively per array-lengths.md Q12 (keep `[T; N]`, box past a size). Rec: yes.
- **R-f. The std-prefix paper** (M120 door (b), M36 §6.15, N157, E292 door (c)): a deterministic, persisted std prefix so a cold check, every test process and kolt's server leg stop re-analyzing std — what S6's windows give it, what blocks it, sizes. Rec: yes, papers-50.
- **R-g. E292's gate:** the seal's seven LSP rows report CPU ms AND instructions; the e121 state advances only on a true green on a quiet box with a lucide-carrying copy; the mandate stays 500 ms CPU. Rec: yes.
- **R-h. The cut:** v0.48.0 at the seal (breaking: B602, B579's float scope; everything else additive). Rec: yes.
- **R-i. A153 S5, the kolt exhibit:** store-50 builds it as a PATCH on a scratch copy of kolt (verified under the tip); the owner applies and commits. Rec: yes.
- **R-j. L24:** the Windows runner's routing lands when the owner registers the runner (standing).

## Mechanics (every lane)

briefs49.md's "Mechanics" stands in full (and through it 48's to 42's): worktrees `vilan/.claude/worktrees/<lane>` off `origin/next` at the base, never the main checkout; an item's text is a HYPOTHESIS; pins red first; one commit per item/slice with its `## Unreleased` CHANGELOG entry and a family marker the cut classifies (`breaking`, `miscompile`, `fix`, `feature`, `performance`, `diagnostics`, `tooling` — never `perf`); ledger rows `NEW`; `LANE-STATUS.md` untracked; the native differential in both modes and `check_scope_differential` in every std gate; five lanes at once, `CARGO_BUILD_JOBS=6`, nextest `-j 6`, one cargo at a time; logs under `target/<lane>-scratch/`; kill by PID; measure in instructions; a lane never runs a git command in kolt or the website checkout (a `cp -r` copy carries `src/lucide` + `src/search-dict`); a lane probes beyond its items and files what it meets; test programs import the traits they call, write attributes canonically and use v0.47.0's std paths; an `#[ignore]` reason leads with its tracker id; a lane that changes analyzer.rs, mono.rs or an emitter names the functions, keeps late writes at zero and runs `scripts/ci-local.sh perf`; a native test builds its OWN program name; never leave a load generator running; a rebase re-runs the FULL gates; models per lane as the brief names (the trailer names the model). Added from Order 49:

- **A rebase keeps every CHANGELOG entry's family marker** (debug-49's E283 lost its marker in a rebase; run the changelog parity check after every rebase).
- **An ownership exception is a listed arm:** a new `Expr`/`Type` variant may add the mechanical arm an exhaustive match needs in another lane's file, listed in the commit and the report; nothing else there.
- **A record or table that reuse restores needs the reuse pin:** anything built per module and skipped on a hit is pinned on a reused module in an UNSEEDED session (the C3 hover red), and the merge gate runs the vilan-lsp binary whenever records or tables move.
- **Editor-only tables never run on a CLI check** (lang-b-49's Q10): gate them on the front end's flag (`Workspace::reading_aids`), and measure the cold rows.
- **Peak RSS is a gate too:** kolt's cold check within 3% of the base in RSS (the TypeTable lesson: a hash table's doubling is a cliff); measure with `sweeps/order49/rss-probe.py` (a fresh process per run).
- **The seal's base kolt is a copy that checks clean under the BASE compiler, carrying `src/lucide` and `src/search-dict`;** the base LSP rows' `errors` column must read 0 before any ratio is believed; the e121 state is reset from the saved pre-seal copy before every perf re-run; every lane's processes stop by PID before the perf leg.
- **Integrator:** every merge gates `ci_ignored_pins` + `hygiene` with crates resolved from the tree; read the gate, THEN push; a push to `next` cancels the running CI; the seal's perf leg never overlaps a CI run; the cut keys the perf verdict by the TARGET sha; absolute paths in every chained command (three cwd slips in Order 49); after a host reboot the runner container is started by hand.

## Lane incr-50 (wave 1; Fable 5.1): M110 S3 by MUTATION LOG → C1; S6 windowed ids → C2; M134's anchors → C3 if time. ALONE in the analyzer core

1. **S3a + S3b, the mutation-log form** (analyzer-pass-map.md §7.2, R-l): the context rewrite's and `[track_caller]`'s edits (hidden parameters, threaded arguments, `get()` → `Expr::Local`, lowered `run(v, f)`, the ids they mint) RECORDED per prefix function with the world and REPLAYED on a hit, recomputed for the hot set; the emitters untouched (the native differential trivially green); then the five fixpoints — contexts (+ the graph built once), async, platform colour, `infer_borrows`, `infer_bumps` (M127) — seeded from the stored prefix results (hot callees as unknowns) and iterated from the hot set's nodes and their callers, never from last keystroke's settled sets (a deletion must shrink). Gates: the four differentials with EFFECT edits (a removal of a `get()`, a `sleep`, a node call), the contexts and track_caller corpora byte-identical, a "one seeded pass" counter and a planted "replayed a stale log" red; `scripts/ci-local.sh perf` (cold rows within 0.1%: the log is filed only for reusable analyses, as S2b); the session table and E121's seven rows (instructions AND CPU, quiet, the lucide-carrying copy under `target/incr-50-scratch/`). **→ C1.** Expected: the fixpoints' ~183 ms of a served keystroke mostly gone.
2. **S6, the interface firewall over windowed ids** (R-b; the spike's hooks on branch `spike-49` @c761e214 are the skeleton: `walk_module_items`, the per-constraint anchor, the modes, the census, `tests/id_windows_spike.rs`): windows for all three lanes; demand-sized type windows; run-length `type_id_sources`; anchors for the prepped drains (5,486 + 2,634 mints per client leg); the two new differential classes; the "body edit re-walks one module" pin; the standing counter pins. Gates: the six legs the spike ran, byte-identical under `all` (the four differentials, the corpus goldens, the native differential), cold rows within 0.1%, the session table and E121 rows. **→ C2.** Then the spike branch is deleted (its evidence is the report).
3. **M134** if time: one `set_anchor` per body in the six post-settle passes; the census reads 0 unanchored; **→ C3.** S7 is Order 51's.
4. **E292** is measured by this lane at each checkpoint (the seven rows, both metrics); it closes when leaf, css and parse break read under 500 ms CPU on the reference box on a quiet run, else the report says the remaining ms per pass.

Sizing XL. Owns the analyzer core (analyzer.rs, analyzer/, incremental.rs, const_cache.rs, impl_select.rs, mono.rs, type_.rs's ids, id.rs, lib.rs's drivers, track_caller.rs, context.rs, vilan-lsp's scheduling).

## Lane store-50 (wave 1; Opus 5.5): A153 S2's remainder → S4 reconnect → S3 collections (A168) → S5 the kolt exhibit (R-i); A169; A149 S5/S6

1. **A153 S2's remainder:** `when_remote_live` (the second function, as ruled), `states()`, `when_all_some` over remote handles; the stub pins un-ignored stay green.
2. **S4, reconnect** (mirrored-store.md §7): root replay, one coalesced re-subscribe, comparing re-seed, `Refreshing` while down.
3. **S3, collections over the wire:** `Seq` (Splice with counts), key-set slots and `Keys`, whole-collection leases (`each_by` over a remote map); **A168** (`HashSet` gains `Wire`) first.
4. **A169** (door (a): the server answers an `Unsubscribe` with `Gone(slot)` so the client forgets the reader).
5. **S5, the kolt exhibit** (R-i): kolt's `store.vl`/`model.vl`/`channel.vl` as §8 writes them, built and verified on a scratch copy under the tip, delivered as `sweeps/order50/store-50/kolt-mirror-v0.48.0.patch` (plain hyphens in kolt comments); **A149 S6** rides with it; **A149 S5** (compiler-generated nodes) only on a measured need — say the number.

Sizing L. Owns `std/src/reactive/store*.vl`, `delta.vl`, `std/src/rpc/*.vl`, `rpc.vl`, `wire.vl`'s store frames, the `Storable`/`StoreWire` derive code, `hash_set.vl`. Not the analyzer core (file with a repro).

## Lane native-50 (wave 1; Opus 5.5): F122 (R-e), F123, F125, F126, F127, F128; then F124 (M)

1. **F122** (box past a size; array-lengths.md Q12), **F123** (a std METHOD over a `Shared` view's field reads through the view — the F114 seam, methods not intrinsics), **F125** (`BigInt` as text: interpolation, `+ ""`, `to_string`), **F126** (`print(caller())` refused by name or rendered), **F127** (a spread of a tuple LITERAL), **F128** (a by-value closure parameter over `List<usize>` not dereferenced).
2. **F124, the aliasing-loans model** (your own note under `sweeps/order49/native-49/F99-aliasing-loans.md`): the reborrow lowering first (nested groups), then the cell-and-handle lowering for interleaved groups; transparent-references.vl is the acceptance (the whole-set triple 130/127/3/0 → 130/128/2/0).
3. The triple after each flip; both native modes; the copy and leak censuses.

Sizing L. Owns vilan-rust, vilan-rt, the native tests. Stays out of the context/track_caller emission (incr-50's S3 keeps the emitters untouched by design — if S3 needs an emitter read of the log, incr-50 asks through the integrator) and of `dbg.rs`'s printers until debug-50 merges.

## Lane tools-50 (wave 1; Sonnet 5.5): N164, N165's pin, N163, N162, B594, the seal's base-copy tooling

1. **N164:** the M26 burst pin driven by the server's own counters between keystrokes (door (a)), green under load.
2. **N165's structural pin:** the harness's copy checks clean under the base compiler before the first edit, else the run refuses with the errors; `seal.sh` gains `VILAN_PERF_KOLT_DIR` (a clone COPY the integrator commits the working tree into) and `VILAN_PERF_THRESHOLD`, folding `sweeps/order49/perf-leg.sh`'s two options in; `sweeps/order49/rss-probe.py` moves to `scripts/rss-probe.py` and the seal's T3 kolt row reports peak RSS from a fresh process per run.
3. **N163** (the nextest priority tiers re-measured under `ci-test`), **N162** (`vilan check <std file>`: close with the doc note, as ruled, or the three fixes if S), **B594** (`[library.dependencies]` resolved in file mode).

Sizing M. Owns `scripts/`, `.config/nextest.toml`, `perf_gate.py`, `lsp-latency.py`, the release scripts and their pins, vilan-cli's `file_project`, vilan-lsp's cancellation tests.

## Lane papers-50 (wave 1; Opus 5.5): the std-prefix paper (R-f). NO tree change

To `proposals/projects/vilan/proposal/std-prefix.md`: a deterministic, PERSISTED std prefix — the std world analyzed once per toolchain build and loaded by every process (a cold `vilan check` pays 1.23 G of its 1.48 G floor to std; every nextest process re-analyzes it, N157; kolt's server leg re-analyzes std's rpc/store growth on every pause, M120's +17%). Ground truth measured on next: what a cold check spends in std by pass; what the base cache's key carries (`std_seeds`, the hot set); M36 §6.15's leaked-AST-keyed structures and every other process-bound thing (ids, interned types, arenas); what S6's windows give it (a std window stable across processes once ids are windowed per item); the serialization form and its size; the invalidation rule (std's content hash + the compiler's build id); the doors (a cache file beside the toolchain; a fork-server for the suite, N157 (b); the server leg sharing the client's std prefix); the estate of readers that would need a cross-process id. Numbered questions with recommendations; slices sized with gates. The type-ascription paper is the measure of length.

## Lane solver-50 (wave 2, at C1; Opus 5.5): B596 (miscompile) FIRST; B599 (R-d); B579's float scope (R-c); B598, B600, B601, B592, B593, B595; M133; E287, E289, E290

1. **B596** (a struct literal evaluates its fields in WRITTEN order on JS as natively — the transformer spills to temporaries as lang-a-49 did for by-name tuple literals; family miscompile; both backends pinned).
2. **B599** (fill-from-use: the argument and receiver channels carry a use's type back into a binding's hole; kolt's sidebar annotation becomes optional — estate counted; not breaking), **B602** (R-c, B579's float scope; breaking; the estate on kolt's copy, the website's `src`, the examples, std's corpus).
3. **B598** (a std trait a user file never imports competes at its call: the import-surface rule), **B600** (an expression hole no binding holds refused), **B601** (the double narrowing message), **B592** (a list literal of array literals under `List<[i32; 2]>`), **B593** (a list of function items callable), **B595** (a static trait method on a concrete type that only a blanket answers).
4. **M133** (the hole's `Slot` question answered once per hole type, keyed against B401 admission and M121's reach record; `ci-local.sh perf` says what it bought; no bump).
5. **E287**, **E289**, **E290** (diagnostics).

Sizing L. Owns inference and the checks, `impl_select.rs`, `mono.rs`, the JS transformer's struct-literal arm (B596), the diagnostics named. Rebases onto C2 (and C3) when the integrator says.

## Lane lang-50 (wave 2, at C2; Opus 5.5): array-lengths.md S1 → S2 → S3 → S5 → S6; E291's census

S1 (R2: `Type::Array(TypeId, TypeId)` with `Type::Length(n)`, byte-identical output — the one slice that touches the core, hence at C2), S2 (`[type T; _]` and `[type T; const N]` impl heads; A163 closes, A161 builds in S5), S3 (`<const N>` in generic lists; a number as a generic argument), S5 (std's first wave: `Items` (A161), `PartialEq`/`Eq` (A166), `Hashable`, `Debug` (E283's array half, with debug-50), `to_list`, `iter`), S6 (the book and spec; D15). S4 (named lengths) if room. **E291:** the census of spaced `<` after a name in expression position across the estate; the rule is decided on the numbers (file them; build nothing). A170 stays declined. Sizing L. Owns the parser's array grammar, `Type::Array`'s representation (after C2), the comparators' array arms, mono's array keying, std's array impls, the array grammar in the spec.

## Lane debug-50 (wave 2, at C2; Sonnet 5.5): a bare closure under `print` (E293); E283's array half (with lang-50's S5); E257 S5 if room

1. **E293** (filed at GO): a bare closure under `print` prints `<closure |i32| i32>` on both backends, retiring F25's function half; the host/opaque values keep console.log.
2. **E283's array half:** `T: Debug` over `[T; n]` once lang-50's S2 is on next (the any-length head).
3. **E257 S5** (source maps for the JS backend; `--inspect` through them) if room — measure first.

Sizing S–M. Owns `printer.rs`, `transformer/dbg.rs`, `vilan-rust/src/dbg.rs`'s printers, `show.rs`, std's `debug.vl`, the `Debug` derive.

## Ownership map (conflict avoidance)

- **The analyzer core:** incr-50 ALONE in wave 1 (R-a); solver-50 from C1 (inference/checks/impl_select/mono + the transformer's struct-literal arm); lang-50 and debug-50 from C2.
- **std's store, rpc, wire, hash_set:** store-50. **vilan-rust, vilan-rt, native tests:** native-50. **scripts, profiles, harnesses, file_project, the cancellation tests:** tools-50. **Papers:** papers-50.
- **Merge order:** wave 1 as they come (tools-50, papers-50 to proposals, native-50, store-50; incr-50 at C1, C2, C3); wave 2: solver-50 (rebased onto C2/C3), debug-50, lang-50 (rebased last).
- **Waves:** wave 1 = incr-50, store-50, native-50, tools-50, papers-50. Wave 2 = solver-50 at C1; lang-50 and debug-50 at C2, as slots free.
- **After every merge that moved goldens:** `regen_goldens.sh`, both native censuses, the copy census; CI on next read before the next push.
- **At the seal:** `seal.sh` with the base kolt = a clone COPY of the owner's working tree committed inside the copy (never the owner's checkout), lucide carried, checked clean under 0.47.0; the tip = the same tree (+ any patch the order owes); E121's seven rows quiet, CPU and instructions; the e121 state reset only if a seal is re-run; then the v0.48.0 cut (R-h), the fold, toolchain both locations + vsix, kolt's patches (the mirror exhibit, R-i), the website re-checked, L24's routing when the Windows runner is online.
