# Order 42 — THE TRAIN: the solver's four blockers, `usize` S2 and the combinator flip merged last, and the v0.41.0 cut at the seal (drafted 2026-09-25, off vilan next @d65d4e75; GO 2026-09-25)

**GO 2026-09-25.** The owner: "Go with all recs." R-a–R-e stand as recommended: the cut plan's Q1–Q5 yes and the cut by the integrator after CI green; `isize` unbuilt; B413 in this train only if ready by index-42's merge, else v0.42.0 with its deprecation announced; `export self::*` deferred; A130's refusal static-only.

**Base.** Order 41 sealed at d65d4e75 on 2026-09-25 (CI 36137702888 green 11/11; seal green start to
finish; toolchain `vilan 0.40.0 (d65d4e759)` in both locations; `origin/next` IS d65d4e75 — nothing
has landed since). Ledger next id **570** (`crates/vilan-cli/tests/diagnostics-ledger.tsv`, max
569). Tracker 121 open. Shared-census literal 143. The CHANGELOG's `## Unreleased` carries **35**
`breaking` entries since v0.40.0 (2026-09-01). Every ruling this order builds was made by the owner
on 2026-09-25 after the seal and is stamped on its item (`sweeps/order41/stamps41-rulings.json`,
`stamps41-f27r3.json`): the ten train decisions, A122 Q1–Q7, F27 R3's six; and four design items
were filed from the owner's side questions with recommendations (A130, B413, B414, B415). Kolt is at
9a057c6 (`wip`, the owner's, eight uncommitted files) and RED 4/4 on the new compiler until the
owner adds A125's two hand `Hashable` impls; kolt's I5 and A124 sites move only WITH this order's
train (R4). vilan-website carries 7 uncommitted files (the owner's). vilan-playground's todo exhibit
checks clean on d65d4e759; its `client.vl:22` breaks under the flip (a derivation handed to a
writable `Signal<Route>` bound — reactive-42 names the line, the integrator applies it at the merge,
the playground is not a git repository).

**The shape.** This is the order the last three were building toward. **The solver's four blockers
land first** — B408 (a blanket method unreachable through an abstract bound: every generic
`s.map(..)` breaks the moment `map` is a blanket), B398 (a mapped tuple over `dyn` does not coerce
its elements: `combine` under the flip throws), B406 and B407 (a literal into a generic constructor
inside a struct-literal field is not typed from the field; NEGATIVE literals are accepted at
unsigned types — under `usize` every `-1` sentinel would compile silently). solver-42 reports each
of those four the moment it lands (its `LANE-STATUS.md`), and the two train lanes REBASE onto its
merge — never cherry-pick (Order 41's lesson). **The train is two lanes merged LAST**, each ONE
breaking commit over a rebased base with a full estate re-sweep: index-42 applies I5 S2 from the
prepared codemod (`sweeps/order41/index-41/run_s2.sh`: 105 signatures, 214 edits, 7 sentinels and 8
loops by hand, the naming diagnostic and quick fix, the subscript flips to `usize`; 17 goldens move,
each classified), and reactive-42 applies A124 S2c from the saved patch
(`sweeps/order41/reactive-41/s2c-flip.patch` + `s2c-combine.patch`: the five combinators return
nodes, `map` a blanket, A25's law at the subscribing leaf, `.cell_global()` and the module-level
refusal, `Resource<T>` keeps its type name and respells its constructor). A third breaking lane
rides beside them if its codemod is ready: syntax-42 dissolves the `resource` keyword into
`[resource]` (B413) and gives file-level attributes a host, `[platform("browser")] mod self;`
(B415), before anything uses the bare form R1 shipped. **The v0.41.0 cut at the seal** per
papers-41's cut plan (Q1–Q5 asked at GO) — I5 S2 first, the flip second, the release-notes breaking
summary written into the release commit, `THIRD-PARTY-NOTICES.txt` regenerated, the `release.yml`
rehearsal re-run. Around the train: native-42 takes F40 (the ruled `vilan-rt-crypto` crate — the
last wall before kolt's `server.vl` builds natively AS WRITTEN) and the five native finds Order 41
left; collections-42 takes A129 (the keyed span, RULED) and M87; std-42 takes A128 (`on_leave`,
RULED) and the hygiene tail incl. the two plain-`cargo test` races; papers-42 writes B414
(contextual keywords), the two as-built notes Order 41 owes the papers, and the cut's release-notes
summary.

**Eight lanes.** Merge order: std-42 (droppable, first), solver-42, collections-42, native-42, then
the breaking train — syntax-42, index-42, reactive-42 LAST — each train lane rebased onto the tip
before it by its own agent. papers-42 merges to proposals only. The cut runs after the seal and CI
are green, by the integrator.

## Rulings — all RULED 2026-09-25 (the owner); what each lane BUILDS from them
- **A25 under the flip (reactive-42).** The mirrors lose their owner-strict `map`; the owner is
  asked at the SUBSCRIBING LEAF. The eight A25 pins re-derive to say so.
- **The no-cycle gate + A130 (reactive-42).** The gate's exemplar builds its `.cell()` under an
  owner; reactive-pipeline.md §2.4 states a module-level cell is a leak by design unless released;
  AND `.cell_global()` carries that intention explicitly while `.cell()` in a module binding's
  initializer is REFUSED with a steer (static — a cell reached from module init through a call is
  not caught; one ledger row). Rec accepted at filing; confirm at GO (R-e).
- **`Resource<T>` (reactive-42).** Keeps the TYPE name; only the constructor respells (`resource` is
  a keyword — until B413 lands, after which the collision is gone; do not wait for it).
- **I6 (index-42).** `as_usize()`/`as_u53()`/… of a negative SATURATES to 0 on every backend.
- **A129 (collections-42).** A `Splice`'s span gets a KEYED match bounded to the span; `set_all`'s
  doc corrected.
- **F40 (native-42).** A second optional crate `vilan-rt-crypto` (OS randomness via `getrandom`;
  SHA-512 + PBKDF2), linked only when reached; `vilan-rt` stays dependency-free and
  `forbid(unsafe_code)`.
- **A128 (std-42).** `FocusScope::on_leave(|to: Element|)` from a capture-phase `focusout` when
  `relatedTarget` is outside the scope and every scope above it; a null target does nothing; Q2
  confirmed.
- **`peek` keeps its name** (M86 closed); B414 (contextual keywords) is papers-42's.
- **editor-41's five spellings CONFIRMED** — and B415 replaces the bare `[platform("browser")];`
  with `[platform("browser")] mod self;` as the host (syntax-42); `export self::*` DEFERRED (R-d).
- **B405 (solver-42).** REFUSE a fractional literal at an integer-typed position, with an `as_f64()`
  steer.
- **A122 Q1–Q7** as recommended — the BUILD waits for this train and the impl-binder grammar
  alternative (syntax-42 adds the alternative; the build is Order 43's).
- **F27 R3's six** as recommended — a build after B415; Order 43 candidate, NOT in this train.
- **Asked at GO (rec in each):**
  - **R-a — the cut plan's Q1–Q5** (`sweeps/order41/papers-41/cut-plan.md` §8): Q1 the trains merge
    I5 S2 first, the flip second (rec yes); Q2 the four no-impact breaking entries stay as written
    (rec yes); Q3 a breaking-changes SUMMARY at the top of the release section, written into the
    release commit (rec yes — papers-42 drafts it); Q4 the `release.yml` rehearsal re-run at this
    order's seal before the cut (rec yes); Q5 deprecation markers keyed by method path (rec yes).
    And the cut itself: the integrator runs `cut-release.sh 0.41.0` after CI is green on the sealed
    tip, `THIRD-PARTY-NOTICES.txt` regenerated in the release commit if `cargo about` is available
    (F2), and the 12,656-character headroom (F3) re-measured — a breaking entry must never drop from
    the body.
  - **R-b — `isize`.** Stays unbuilt (rec: not free — its own wire-width and range rulings; nothing
    in the estate asks).
  - **R-c — B413 in THIS train or v0.42.0.** Rec: in this train IF syntax-42's codemod and estate
    sweep are green by the time index-42 is ready to merge; otherwise syntax-42 lands `mod self;`
    alone and B413 waits for v0.42.0 with its `deprecates:` marker (the cut refuses a `removes:`
    whose deprecation never shipped — so the keyword's removal must be announced in v0.41.0 either
    way).
  - **R-d — `export self::*`.** Rec: DEFER; `export *;` stays; `self::` as a path prefix is its own
    question (B415's stamp).
  - **R-e — A130's refusal is static-only.** Rec: yes (the direct spelling is the mistake; a cell
    built under a call from module init is the documented remainder).

## Mechanics (every lane)
briefs41.md's "Mechanics" stands in full (briefs40's + Order 40's rules: never `git config`; the
item's text is a HYPOTHESIS — verify the premise and say so; a passing probe must be shown to BUILD
something; every std-touching lane gates `-p vilan-cli --test native_differential` default AND
`VILAN_NATIVE_DIFFERENTIAL=1`; the golden suites are `corpus`, `split`, `examples`,
`copy_elision_census`; a `-p <crate>` spec with zero tests exits non-zero; `vilan build
vilan/test/<x>.vl` overwrites the golden — probe over a scratch copy; a BREAKING lane re-sweeps the
estate INCLUDING the `.vl` consts inside Rust tests, vilan-website and vilan-playground; SendMessage
works — a lane answers no question itself; worktrees off `origin/next` @d65d4e75, never the main
checkout, never `git stash`, never push, `kill <pid>` of recorded PIDs only; one commit per item
with its CHANGELOG entry and family marker; ledger rows written `NEW` (next id 570), a rowed message
is ONE `\`-continued literal and `cargo fmt` JOINS a `\`-continued string — multi-line `.vl`
fixtures are `concat!` or one line; long runs in the FOREGROUND with a timeout; perf in thread CPU
or callgrind Ir + loadavg, never wall; kolt and proposals READ-ONLY, kolt never copied into the
vilan tree; model Opus, never Fable; never rebuild while your own whole-crate run is in flight;
`node_size` for node.rs lanes; `markdown_golden` + `book_sync` for docs lanes; `grammar_ebnf` +
`grammar_sync` for grammar.md; `shared_census` in every std gate list and `vilan fmt vilan/std`
before every std commit; a depth cap answers NO when it gives up; doc comments compile under `cargo
test --doc` — a sketch in `///` is a ```text fence; a new corpus program needs its
`corpus_manifest!` row and the interpreter excludes by name what the macro world refuses; the PATH
export `export PATH="$HOME/.cargo/bin:$HOME/.nvm/versions/node/v24.2.0/bin:$PATH"`; `touch build.rs`
when the sha goes stale), PLUS Order 41's lessons as RULES:
- **Scratch files live under `scratchpad/<lane>/`, never at the scratchpad root** — two lanes'
  `changelog.py` helpers collided and one lane's entries landed in another's CHANGELOG. A helper
  takes its repo path from `git rev-parse --show-toplevel`, never a literal.
- **A lane that needs another lane's fix cherry-picks it for its OWN gates only, and REBASES onto
  next (dropping the pick) before it reports, once the source lane is merged** — the integrator
  never hand-folds a cherry-pick; the one that was tried conflicted in five analyzer hunks and was
  aborted. solver-42 writes each blocker's sha to `LANE-STATUS.md` in its worktree the moment it
  lands; the train lanes poll that file between their own steps.
- **Two lanes bumping one COUNT WORD in a docs page merge textually clean and fail at `book_sync`**
  — a lane that adds a quick fix or a code action says so in its report, and the integrator budgets
  the fold.
- **Scratch build targets stay under the worktree's own `target/`, never `/tmp`** (a lane filled the
  shared tmpfs).
- **A 1Password outage is waited out, never signed around** — retry the same commit; report
  uncommitted state precisely if it is still down at report time.
- **The seal runs `cargo test --doc` and the WHOLE-SET native differential; CI is the last word** —
  CI's Windows leg reads paths with backslashes (a pin that names `src/main.rs` reds there), and its
  runner images sometimes fail at setup (re-run, not a defect).
- **A merged tip that moves a golden two lanes touched is REGENERATED over the merged tree
  (`regen_goldens.sh`), never folded by hand**; the native copy census likewise
  (`VILAN_REGENERATE_NATIVE_COPY_CENSUS=1`).
- **Tracker writes go through `file_items.py` / `stamp_items.py` / `close_batch.py`** — never ad-hoc
  (the integrator's own helper truncated 22 items; restored).

## Lane std-42 — DROPPABLE, lands FIRST: A128 (RULED), N130, N129, N131, N128, N127, N132, E224
1. **A128** — `FocusScope::on_leave(|to: Element|)` in both ui twins per the ruling; a pin that a
   Tab inside `Wrap` never fires it, a click outside `Contain` fires it with the target, a null
   target is silent. 2. **N130** — `split.rs`'s unused `Instant` under the Windows cfg (one line);
   decide whether the seal's Windows leg adds `--tests` and say so. 3. **N129** —
   `native_differential` stages per TEST (a tempdir per test) so plain `cargo test` stops racing;
   CLAUDE.md's equivalence sentence corrected or the exception named. **N131** — the lsp suite's M19
   `references::` set under plain `cargo test` at load: find the shared state (a per-process runner
   hides it); `overlay_module_reclaim`/`session_growth` likewise or their load-sensitivity named. 4.
   **N128** — the `for_each_child` probe (node.rs; gates `node_size`), the CLI's three compiler
   threads + the wasm entry DECLARE their stacks, the stale 11.3 KiB figure corrected. **N127** —
   the estate sweep script checks the playground's programs (`vilan check` per exhibit). **N132** —
   the honest replay pin if the served-from-cache signal is cheap (exact reuse only for pairs that
   HIT + a ≥ 90 % floor), else the file header fixed and the budget lift kept — say which. 5.
   **E224** — a `[deprecated]` FUNCTION warns at its import leaf as types do (one rule for labelled
   items). Sizing M. Owns std::ui's focus module (both twins), the three test binaries named,
   node.rs's one probe line + `node_size`, the CLI/wasm thread declarations, the sweep script, the
   label reader's import-leaf rule.

## Lane solver-42 — THE TRAIN'S FOUR FIRST: B408, B398, B406, B407 (each sha to LANE-STATUS.md the moment it lands); then B405 (RULED), B410 (MISCOMPILE), B409, B411, B412, B403, B401, B404, B400, E223
1. **B408** — a blanket method over `S: Trait<T>` reachable through an abstract bound `S:
   Trait<i32>` (`fun f<S: Src<i32>>(s: S) { s.twice() }` — 'S has no method' today); the repro in
   `sweeps/order41/reactive-41/finds/`; pins in both spellings; `.cell()`/`.distinct()` in generic
   code as the std-shaped pin. REPORT the sha at once — reactive-42 rebases on your merge. 2.
   **B398** — `(U in T: dyn Source<U>)` coerces its ELEMENTS at the mapped-tuple position (dyn-40's
   explicit-coercion rule gains the comprehension's element arm); the runtime `s[1].get is not a
   function` becomes a pass; papers-41's probe `a122_09` and reactive-41's `combine` repro. 3.
   **B406** — a literal passed to a generic constructor inside a struct-literal FIELD types from the
   field (`S { count = Shared::new(0) }` with `count: Shared<u53>`); std's rpc.vl drops index-41's
   two suffixes (`b389-gap-literals.patch` reversed). **B407** — a NEGATIVE literal at an UNSIGNED
   type is REFUSED naming the type's range (`let n: usize = -1;`, `u53`, `u8`); index-type.md §3.4's
   seven sentinels are the pin; one ledger row. REPORT — index-42 rebases on your merge. 4. **B405
   (RULED)** — a fractional literal at an integer-typed position refused with an `as_f64()` steer
   (`let y: i32 = 3; y / 2.0`); ledger row; B402's literal-only case stays green. 5. **B410
   (MISCOMPILE)** — an override is selected through a bound when the trait's argument is a TUPLE (JS
   printed 'default'); reactive-41's workaround (each node calling its own `on_settle`) can then
   retire — tell reactive-42 in your report. **B409** — a same-trait bound checked at the upstream's
   arguments (`impl M<type S: Src<type X>, X, type U> with Src<U>`); the private `Upstream` blanket
   in reactive.vl can retire — likewise. **B411** — a default's closure parameter typed from a
   nested binder (the nodes can drop their phantom parameters — reactive-42's call). **B412** — a
   generic `S: Source<X>` value erases to `dyn Source<X>` at a `dyn` position. 6. **B403** — the
   analyzer's cannot-infer check refuses a bare `Holder::tag()` whose bounded impl generic nothing
   binds (native's silent `A A` becomes a refusal on both backends; the first attempt tripped std's
   `FromJson` statics — `Self::` and `Holder<T>::` bind through a channel the check must read).
   **B401** — the inherited-default lookup consults B318's `only`/`(impl …)` admission. **B404** —
   an unsuffixed literal typed `BigInt` emits `3n`. **B400** — copy elision under a live `read()`
   temporary: a closure's `&List<T>` parameter no longer admits `cell.read()` where a `fun`'s
   refuses it (then collections-42 re-spells `peek` — tell them; the native `WeakGet` emission is
   native-42's if needed). 7. **E223** — the mapped-tuple refusal names the `(2..)` bound instead of
   'unbounded'. Sizing L. Owns analyzer.rs, impl_select.rs, mono.rs, transformer.rs's comprehension
   and coercion emit. STOP-AND-REPORT past the four if any needs a design choice — the four are the
   order.

## Lane collections-42 — A129 (RULED), M87, `peek` after B400
1. **A129** — a `Splice`'s span gets a KEYED match bounded to the span in
   `place_each`/`place_each_by`: `set_all` over the same three keys reads `cut=0 built=0`;
   `reconcile_to` with one edit + an append keeps the tail; the 300-turn walk's `each_by` row count
   on the op path ≤ the pass's (1,078 vs 557 today — report the new number); `set_all`'s doc
   corrected. 2. **M87** — `KeyedCell::locate` (rpc.vl) reads one element without copying the list
   (`peek`-shaped or the list in its own `Shared`), Ir before/after; the keyed rpc pins unchanged.
   3. **`peek` after B400** — once solver-42's B400 lands (poll its LANE-STATUS.md), `peek`
   re-spells through `Weak::get` if the closure spelling is refused; if the native backend cannot
   emit `WeakGet`, say so and keep the JS spelling with the native differential excluding by name.
   Sizing S–M. Owns delta.vl, `ListCell`, `each*`/`reconcile` in both ui twins, rpc.vl's `KeyedCell`
   (M87 only).

## Lane native-42 — F40 (RULED) → kolt's `server.vl` natively AS WRITTEN; F35, F36, F37, F38, F39; the conservative copies; C14 re-scoped
1. **F40** — the crate `vilan-rt-crypto` (like `vilan-rt-sqlite`: linked only when a program reaches
   `random_bytes`/PBKDF2/SHA-512; `getrandom` + hand-written or crate SHA-512/PBKDF2 — say which and
   why; the workspace's audit/clippy/windows gates cover it); `vilan-rt` unchanged. THE EXIT: kolt's
   real `server.vl` (read-only; a scratch copy) builds natively with ZERO host gaps and its login
   exchange is byte-identical with node — F18's original exit, finally; the host census saved under
   `sweeps/order42/native-42/`. 2. **F35** — `ListCell` and `map_each` build natively ('generic type
   instantiated at `any`'); `list-cell.vl` and `delta-law.vl`'s consumers flip. **F36** —
   interpolating a generic call's result (`i"{cell.get()}"`); `encode_json` on a `List<i32>`
   (E0596); `blanket-impl.vl`, `reactive-selector.vl`, `resource_take.vl` flip. **F37** — the
   partial move (`let h = r.live; push(copy_of(r))`); the attach path's extra copy goes; the copy
   census re-measured (dyn-objects 9/21, board 5/15 today — the conservative copies from the
   consuming-position rule meeting S2b's reactive.vl; bring them down and say by what). **F38** —
   `Result::and_then`'s `U` recorded for native. **F39** — the reentrant read through an ALIAS: the
   compile-time check follows aliases, or the runtime answers JS's in-progress value — say which and
   why. 3. **C14** — re-scoped: the NATIVE LEAK GATE (a counted-`Shared` census over the exit
   program at process end: every cell released) replaces S4; stamp the representation half as built
   by F1 S1a. 4. You merge BEFORE the train; reactive-42's flip must keep your differential pins
   green (its gates include the whole set) — write your reactive-shaped pins over `Source` bounds,
   not over `SignalCell` return types. Sizing L. Owns vilan-rust's lowering, vilan-rt, the new
   crate, native-apps.md §12's numbers (reported).

## Lane syntax-42 — BREAKING, in the train (third-to-last): B415 (`mod self;`), B413 (`[resource]`), A122's grammar alternative
1. **B415** — `[platform("browser")] mod self;` as the file's first statement is the host for
   file-level attributes; the bare `[platform("browser")];` R1 shipped is REMOVED (nothing uses it —
   verify by grep over std, the estate, the docs, kolt read-only); `self` a reserved module name
   (refused as a module's declared name elsewhere); the EBNF row, formatter, LSP painting +
   completion, the R1 quick fix inserts the new spelling, the book. `export self::*` NOT built
   (R-d). 2. **B413** — the `resource` keyword dissolves into `[resource]` on a struct (the word
   stays): parser (the attribute admitted on `struct` only; a `resource struct` refused with the
   steer, one ledger row), analyzer (the kind read from the label), formatter, EBNF, LSP,
   destruction.md; the CODEMOD over std and the estate (every `resource struct` → `[resource]
   struct`), the `.vl` consts in Rust tests, docs fences; BREAKING entry; a `deprecates:`-style
   announcement in the CHANGELOG so v0.42.0 may refuse the old spelling if R-c keeps it out of this
   train. R-c decides whether your B413 commit merges in this train or is HELD on your branch for
   v0.42.0 — build it either way; the integrator merges per the ruling. 3. **A122's grammar
   alternative** — an impl binder admits a tuple-family bound (`impl type T: (2..) with Tuple`
   parses and type-checks as a blanket over every tuple of arity ≥ 2); a pin; the `for` over a
   mapped tuple (body checked once, element abstract) is solver work — name it for Order 43, do not
   build it. Sizing M–L. Owns parsing.rs, the EBNF, formatter.rs, the LSP's syntax tables,
   destruction.md's spelling. Rebase onto native-42's merge by your resumed agent before you merge.

## Lane index-42 — THE TRAIN, part 1: I5 S2 (+ S3, S4), I6 (RULED); ONE breaking commit, merged second-to-last
1. **Rebase first** onto solver-42's merge (B406 + B407 in; drop nothing — you carry no picks) —
   then `sweeps/order41/index-41/run_s2.sh` on that base: the codemod (105 signatures by parse, none
   unmatched; 214 edits — 169 E218 conversions, 41 operand conversions, 4 counters), `hand.patch`
   regenerated (`STOP_AFTER=codemod`; the 7 sentinels and 8 loops by hand, each named in the commit
   message; `Enumerated`'s trait argument, annotated locals, the dead `from < 0` clamps,
   document.vl's `index_of` underflow), `compiler.patch` (the subscript flips to `usize`, the
   two-type admission deleted, ledger row 558 re-keyed); the naming diagnostic (§8.2) and the quick
   fix (§8.3), the fix-producing function shared with the CLI; residue ZERO in std (both platforms),
   macro_std, every corpus program. 2. **I6** — `as_usize()`/`as_u53()`/… of a negative saturates to
   0 on both backends (JS emits the clamp); a pin per width; the differential covers it. 3. **The
   goldens** — 17 move (index-41's classification: each a conversion the codemod wrote or a
   hand-rewritten std loop) — re-classify on the rebased base; any OTHER movement stops the lane. 4.
   **S3** — vilan-rust drops its `as i32` casts at `len()`; the copy-elision census's emitted
   `main.rs` before/after. **S4** — A112's `// I5` markers cleared (`ListCell`/`map_each`
   positions), `Splice(at, ..)` born `usize`, std::ui's row positions, `KeyedCell.positions` (the
   WIRE width stays `i32` — the frame byte-compared), macro_std's `Arguments::len`/`get`,
   `RowStep`/`Delta` payloads; the markers' census reads zero. 5. **The estate re-sweep** — std,
   corpus, docs fences, examples, benchmarks, templates, the `.vl` consts in Rust tests,
   vilan-website (read-only: report the lines), vilan-playground (report), kolt (read-only: the FIVE
   files — `rotary.vl` first, `command_palette.vl` + `theme.vl`'s `len() - 1` underflow on an empty
   list, `search.vl`, `server.vl` — the exact edits written out for the owner). 6. ONE breaking
   commit (S2 + I6 + S3 + S4 may be one or four — the ESTATE move is one), `<!-- family: breaking
   -->`, the migration line for the release notes in the entry. Gates: everything, plus
   `grammar_sync`, `markdown_golden`, `book_sync`, the whole native set, `shared_census`. Sizing L.
   Owns number.vl, every std signature of index kind, the subscript, the naming diagnostic + quick
   fix, the book's numbers pages.

## Lane reactive-42 — THE TRAIN, part 2: A124 S2c (the flip) + A130, A25 at the leaf, `Resource` respelled; ONE breaking commit, merged LAST
1. **Rebase first** onto solver-42's merge (B408 + B398 in; B409/B410/B411 if landed — then the
   private `Upstream` blanket, the per-node `on_settle` calls and the phantom parameters can retire;
   do it only if solver-42's report says the defect is closed, and pin it). 2. **The flip** —
   `s2c-flip.patch` then `s2c-combine.patch` from `sweeps/order41/reactive-41/`: `map`, `switch`,
   both `flatten`s, `and_then` and `combine` return NODES; `map` is a blanket, so dyn-40's
   `map`-through-`dyn` refusal pin becomes a pass; `FlattenOption`/`AndThen` public; the node
   constructors lose `[internal]`. 3. **A25 at the leaf (RULED)** — the mirrors' own `map` goes; the
   owner is asked at the subscribing leaf; the eight A25 pins re-derive; remote-sources.md's
   sentence. 4. **The no-cycle gate + A130 (RULED)** — the exemplar's `.cell()` under an owner;
   `.cell_global()` (documented lifetime; the gate excludes it by name); `.cell()` in a module
   binding's initializer REFUSED with the steer (one ledger row; static-only per R-e); §2.4's
   sentence. 5. **`Resource<T>`** keeps its type name; the constructor respells (say the spelling;
   if syntax-42's B413 is in the train, the collision is gone — do not depend on it). 6. **The 19
   reds re-derived** — 5 on B408 (green after the rebase), 8 A25, 4 behaviour pins, 1 diagnostic,
   the gate. 7. **The estate** — std rpc's 4 (the mirrors), examples 9, split 1, the 30 Rust-test
   `.vl` consts (11 by `.cell()`), docs fences, the guide's derivations section for the PUBLIC flip,
   playground `client.vl:22` (report the edit), kolt's 17 + 6 cascades written out for the owner
   (R4); the S1 numbers stay in the CHANGELOG. 8. ONE breaking commit, `<!-- family: breaking -->`,
   the migration line; every gate incl. the whole native set (native-42's reactive pins must stay
   green — coordinate through the integrator if a pin's shape must move), `shared_census` (say the
   number), the reactive suites, door 2's pins. Sizing L. Owns reactive.vl, the mirrors' `map` in
   rpc.vl, the guide's derivations section, reactive-pipeline.md's "as built" (reported for
   papers-42).

## Lane papers-42 — B414, the two as-built notes, the release-notes summary, C14's re-scope; NO tree change
1. **B414** — `proposal/contextual-keywords.md`: the reserved list classified into HARD
   (declaration/structural: `let`, `mut`, `fun`, `struct`, `enum`, `trait`, `impl`, `import`,
   `export`, `type`, `mod`, `if`/`for`/`match`…) and CONTEXTUAL (`with`, `as`, `in`, `layer`,
   `sync`, `lazy`?, `resource` after B413…), with the parser lookahead each contextual word needs at
   binding/field/parameter/method positions, the editor's painting rule, the estate's uses that
   would become legal, and a rec + slices. 2. **The as-built notes** — reactive-pipeline.md gets
   reactive-41's "As built (Order 41)" paragraph (its text is in A124's 2026-09-24 stamp and
   notes41; the integrator never added it), and after reactive-42 reports, the S2c line;
   incremental-collections.md §13 gets A129's ruling; index-type.md §9 gets S1's as-built + the
   17-golden correction to §5.4. 3. **The release-notes summary** (cut plan Q3) — the
   breaking-changes digest at the top of the v0.41.0 section, grouped as the cut plan groups them,
   one migration line each, INCLUDING this order's train entries once they land (write it against
   the plan first, patch it at the sweep); the integrator writes it into the release commit. 4.
   **C14's re-scope** — one page: the representation half closed by F1 S1a; the native leak gate as
   S4's replacement; S5 (a JS counted mode) kept or dropped. Sizing M.

## Ownership map (conflict avoidance)
- reactive.vl + the mirrors' `map` + the guide's derivations: reactive-42. delta.vl, `ListCell`,
  `each*`/`reconcile`, rpc.vl's `KeyedCell::locate`: collections-42. number.vl + every index-kind
  std signature + the subscript + the naming diagnostic: index-42. std::ui's focus module: std-42.
  rpc_server.vl: nobody.
- analyzer.rs: solver-42 (everything named above); index-42 (the numeric rows and the subscript
  ONLY, after solver-42); syntax-42 (the `[resource]` kind read + the `mod self` platform seam
  ONLY); native-42 nothing. impl_select.rs, mono.rs: solver-42. parsing.rs + the EBNF + formatter.rs
  + the LSP's syntax tables: syntax-42. transformer.rs: solver-42 (comprehension/coercion emit);
  index-42 (`usize` rows). vilan-rust + vilan-rt + the new crate: native-42; index-42 (S3's casts —
  one function, named in the report; merged after native-42).
- Merge order: std-42, solver-42, collections-42, native-42, syntax-42 (rebased; B413 per R-c),
  index-42 (rebased; goldens regenerated at the merge — 17 expected, classified), reactive-42 LAST
  (rebased; goldens; `shared_census`). papers-42 to proposals only. After EVERY merge that moved
  goldens: `regen_goldens.sh`; the native copy census regenerated; the merge helper's BUILD step
  every time; every gate list includes `native_differential` (whole set for the train lanes).
- After the seal + CI green: THE CUT (integrator): the release-notes summary into the section,
  `cut-release.sh 0.41.0` per the cut plan (its dry run first), the rehearsal (Q4), the notices
  (F2), the headroom (F3); toolchain both locations from the tagged tip.

## At the sweep (integrator, proposals)
- Close per the reports; I5 CLOSES at S2 (S3/S4 landed or stamped); A124 closes at S2c with S3
  (kolt) as the owner's; A25 re-stamped; B4's paper gets the 'as reopened, now the common case'
  note; C14 re-scoped or closed; F18's tombstone gains F40's exit line.
- Kolt at the owner's word: A125's two hand `Hashable` impls (still red 4/4); A123's eight sites;
  A121's overlay lines + six `autofocus` attributes; the connection-v3 worktree's two `dyn Signal`
  fields; A120's §9.7.10 rewrite; A127's header token; I5's FIVE files (index-42's exact edits);
  A124's 17 + 6 sites (reactive-42's exact edits); B413's `resource struct`s if in the train.
- The integrator at the merge: playground `client.vl:22` (reactive-42's edit), `resource struct`
  spellings in the playground if B413 rides.
- Order 43's queue: A122's build (after this train + the grammar alternative; the `for` over a
  mapped tuple rule); F27 R3 (fenced twin items, after B415); the contextual keywords per B414's
  paper; the deferred `self::` paths (`export self::*`); native's remainder (F39 if not settled, the
  copy census); A124 S3 (kolt) at the owner's word; C14 S5 if kept; N132's honest pin if not built;
  E215's width if re-ruled.
