# Order 39 — the native server's first request, the rulings built, and the bugs kolt keeps finding (drafted 2026-09-21; GO 2026-09-21, off vilan next @c3f7d1a3)

**GO (2026-09-21).** The owner: "Go" — answering the integrator's "waiting for R1–R9, or a 'go with
all recs'". R1–R9 are therefore RECORDED AS RECOMMENDED and the record-only defaults stand; any of
them the owner re-rules mid-order is relayed to its lane by SendMessage. TEN lanes. Order 38 sealed at c3f7d1a3 the same day (CI 35642858068 green on
all eleven jobs; the local seal green on its first run; toolchain `vilan 0.40.0 (c3f7d1a38)` in
both locations; nothing has landed on `next` since). Ledger next id 549. Tracker 123 open. Kolt is
migrated to c3f7d1a38 and committed by the owner at 8c3f84f, plus two uncommitted files (B369's
one-line workaround in `lib/conditional_value.vl`; `comp/login.vl` formatted) — `vilan check` 0/0,
`vilan build` clean, runtime unverified on this host.

**The kolt sweep (2026-09-21, kolt 8c3f84f — 28 comment lines outside `src/lucide`).** FIVE items
filed (`newitems39a.json`): B368 (a tuple pattern in a `for` header does not parse, and the refusal
names the `for` keyword — lib/search.vl:26; reproduced in five lines), B369 (an INTERNAL error when
a generic constructor function with an undeclared return type builds a user `Slot` impl — found
because it BROKE kolt's build; minimized to 20 lines; kolt carries the workaround), A119
(`when_some` — kolt's `lib/conditional_value.vl` under three of its own FIXME/BUG comments), A120
(a `[service]` as a plain HTTP API — store.vl:51, server.vl:31, login.vl's hand `fetch`), A121
(focus management for overlays — lib/overlay.vl:536). THREE stamps: A72 (client.vl:39/44 replace
navigation, still owed), A8 (styles.vl:46 declared rules, still owed), I3 (kolt's two `map_filter`
impls retired onto `filter_map`). FOUR comments were STALE and are gone from kolt's tree: the two
`map_filter` impls (I3 — one of them unused) and the two E191 notes in login.vl (closed Order 38).
APP-ONLY, staying in kolt: login.vl:89/193 (show the error to the user), styles.vl:78 (selectable
button states), shared.vl:20 (a uuid for the account id), app_input_system.vl:6 (input-system
design), client.vl:92/93/115 (the reauth/redirect effects — A114's scoped effect is the std half of
that worry), prefs.vl:25/43 (the `StorageKey` boilerplate; a typed storage-key codec is a candidate
std item the day a second app wants it), views.vl:675/684 (export/import configuration),
todo.md:145.

The shape. Order 38 left three kinds of work and this order takes one slice of each. **The native
path** did not reach its exit — `board.vl` stops at the host type `Hash` — and the owner's next
native product is the SERVER: so one lane finishes the emitter's three big refusal classes (F20:
`Hash`, `lazy` parameters, overloaded operators = 29 of 68) and flips `board.vl`, while a second
builds the first host bindings a server needs — HTTP over `std::net`, hand-written, because
`vilan-rt` is dependency-free by ruling — with the exit "a native `vilan` server answers a GET".
SQLite cannot be dependency-free, which is this order's first ruling. **The two papers the owner
ruled mid-Order 38** become code: A110 door 2 (nested-forms ordering, bucketed, on door 1) with
A114's scoped effect beside it, and A112's S1 (the delta log lifted into `std::reactive`) with S3
(the delta-driven `each` — measured 16,040× at 1,000 rows against a pass that is quadratic today).
**The bugs**: five HIGH finds from Order 38's lanes (A116, A118, B360, B362, B365) and the two the
kolt sweep just produced (B368, B369), and the owner's seven editor asks (E202–E207 + E205 in its
own formatter lane, merged last).

## Rulings at GO (owner: "Go") — ALL as recommended; the ones that change what a lane BUILDS
- **R1 — native dependencies (native-b-39).** `vilan-rt` is dependency-free (Order 37 R8). HTTP/1.1
  + the WebSocket upgrade can honour that over `std::net` (SHA-1 for RFC 6455 is ~60 lines by
  hand). SQLite cannot. Rec: `vilan-rt` STAYS dependency-free and gains `http`; `std::db` natively
  is a SEPARATE crate (`vilan-rt-sqlite`, depending on `rusqlite` with the bundled feature), linked
  only when a program reaches `std::db` — Order 40's, after this order's HTTP exit. Alternative:
  let `vilan-rt` take dependencies behind cargo features (simpler layout; AGENTS.md's stop condition
  moves).
- **R2 — A114's surface (reactive-39).** Rec: `Source::scoped_effect(body)` and
  `scoped_effect_on_change(body)` as trait defaults beside `effect`; a free `on_cleanup(|| ..)` =
  `get_owner().defer(..)` — inside a scoped effect it is per RUN, inside a boundary per boundary
  (one name, the ambient owner decides); `swap`/`when`/`each` are NOT rebased onto it this order
  (one mechanism is the goal; door 2 lands first).
- **R3 — A113's first ruling: an OWNERLESS derivation (reactive-39).** `map`/`combine`/`flatten`
  outside every boundary live as long as their source today. Rec: KEEP (refusing is breaking and
  `current_path().map(parse)` at the top of `main` is a documented idiom); the guide's "who cleans
  up what" table says so; pins per row.
- **R4 — three refusals (solver-39).** B360: a user-written `external fun` with no `[extern]`
  binding and no lowering is REFUSED at the declaration (today it emits a call to an undefined
  name). B362: a function with a `lazy` parameter is NOT a closure value — refused at the COERCION
  (today an indirect call throws at runtime). B361: `Self<i32>` is refused with "write the type's
  name". Rec: all three; census first, a `breaking` note for any estate program that fires
  (expected none).
- **R5 — B368: patterns in a `for` header.** Rec: admit the TUPLE pattern (and whatever pattern
  `let` already takes, by sharing its production); anything else is refused BY NAME with "bind the
  element and destructure in the body".
- **R6 — A119's semantics (std-39).** `when_some(source, |value| view)`: on `Some → Some` with a
  changed payload, REBUILD the row (needs `T: PartialEq`, like `swap`) or KEEP the row and hand the
  body a derived `Source<T>`? Rec: keep the row — `when_some(source, |value: Source<T>| ..)` is what
  `each_by`'s row cell already does, needs no `PartialEq`, and answers kolt's own FIXME ("ignore
  recompute on every change"); a by-value twin can follow if asked.
- **R7 — A118: `random::range`.** Rec: the DOC is the contract (`[low, high)`); fix the
  implementation; pin over an exhaustive small range.
- **R8 — E205 (fmt-39).** Rec: opt-in first — `[fmt] wrap_comments = true` in vilan.toml, default
  off for one release; a words-in-order safety net; a "Reflow this comment" code action from the
  same function.
- **R9 — E202/E203 (editor-39).** Rec: `<` is placed by the SERVER in type/generic context
  (`onTypeFormatting`) and joins `surroundingPairs` everywhere; the backtick is a global pair with
  `notIn: ["string"]` and a grep pin that the lexer still has no backtick token.
- Record-only defaults: A120 (a service as an HTTP API), A121 (focus scope) and B363 (a unit
  literal) are PAPERS this order (papers-39), ruled after; M79's S1+S2, C14 S4/S5, F26 (the shared
  monomorphisation-resolution module — it would sit across both native lanes' files), F22 (adapted
  instances), A106 door 2's re-census (after A117), A111, M83's landing (re-measured here, landed
  only if the JIT direction survives a quiet host) are NOT this order's builds unless named in a
  lane below; L23 closes on rehearsal 35645802713's verdict, L22 waits on the owner's secret; K15 is
  the website repo's; the v0.41.0 cut stays HELD (the owner's call).

## Mechanics (every lane)
briefs38.md's "Mechanics" stands in full, with Order 38's ten lessons as RULES:
- **NEVER run `git config`, in any form, not even to read.** Signing is configured globally. If a
  commit fails, REPORT the error text; do not reconfigure. (One lane typed a read as a write into
  the shared config and broke `git commit` in every worktree for an hour.) Verify your commits by
  the `gpgsig` HEADER (`git cat-file commit <sha> | grep -c '^gpgsig'`) — `%G?` reads `N` on this
  host for everyone.
- **Your item's text is a HYPOTHESIS. Verify its premise first** and say so in one line of the
  report — five items' premises were wrong last order (a diagnosis, a claimed std feature, a count,
  a reuse the brief promised).
- **A probe that passes must be shown to BUILD something.** A reproducer with wrong manifest keys
  passes vacuously (B369 cost an hour that way): assert the artifact exists, or plant the failure.
- **Merge gates: every lane touching std runs `-p vilan-cli --test native_differential`** (default
  AND `VILAN_NATIVE_DIFFERENTIAL=1`) — `next` was red for an hour when a std change met a native
  pin no gate list named. The golden suites are `corpus`, `split`, `examples` AND
  `copy_elision_census`. A `-p <crate>` spec with ZERO tests exits non-zero under nextest.
- **`vilan build vilan/test/<x>.vl` OVERWRITES the corpus golden in place** — census and probe
  over a scratch copy.
- **A BREAKING or refusing lane re-runs its estate sweep over the MERGED tree at its merge** — and
  the estate list includes the `.vl` program CONSTS inside Rust test files (`module_resolution.rs`,
  `check_scope_differential.rs`, the inference modules), which a `.vl`-file sweep cannot see. The
  estate also names `vilan-website` (30 `.vl`) and `vilan-playground` (6), read-only.
- SendMessage WORKS in this build: the integrator relays cross-lane finds to running lanes and
  RESUMES a finished lane's agent for its own rebase. A lane still answers no question itself —
  an OPEN Q plus the recommendation it built.
- Worktrees off `origin/next` (c3f7d1a3); never the main checkout; never `git stash`; never push;
  `kill <pid>` of PIDs you recorded, never by pattern; one commit per item with its CHANGELOG entry
  and family marker; ledger rows written `NEW` (next id 549), a rowed message is ONE `\`-continued
  literal and N98's prose-literal gate now walks all eight crates; new test files use the support
  scratch root and a staging directory carries the process id; long runs in the FOREGROUND with a
  timeout; perf in thread CPU or callgrind Ir + loadavg, never wall — and thread CPU is itself
  ~2× under loadavg 30+, so a claim names its loadavg. Kolt and proposals are READ-ONLY; kolt is
  never copied into the vilan tree. Model: Opus — never Fable; the integrator passes `model`.

## Lane solver-39 — B369 (kolt's build-breaker), B360, B362, B365, B368 (R5), B361, B367, E199, E208
1. **B369** — `sweeps/order39/probes/b369_min.vl` red first; the inferred return type of a generic
   function whose tail is a struct literal of a generic type must carry the function's own
   parameters; the four pins the item owes, incl. the non-`Slot` twin and B55's guard anchoring at
   the USER's call. 2. **B360 / B362 / B361 (R4)** — three refusals, census first. **B365** — the
   vacuous drop-planner arm (analyzer.rs ~11946) through `struct_initializer_to_def`, with a pin
   that REACHES the arm. 3. **B368 (R5)** — share `let`'s pattern production with the `for` header;
   EBNF, grammar_sync, formatter, the named refusal. 4. **B367** — is B318 S4's admission miss
   reachable? Re-derive editor-38's four-module reproducer against B354's three-file fixture; if a
   hole, it is a soundness item with a red pin; if reachable only through derives, visibility.md
   §3.5 says so (text handed back). **E199** — WRITE THE REPRO FIRST (solver-38 located the seam:
   the `constructions` loop's `declared_bindings`, analyzer.rs ~6785–6860); no repro in two hours =
   stop and report. **E208** — settle a refused written type argument's expression type from the
   WRITTEN arguments. Sizing L. Owns the analyzer's return-type inference, the three refusal sites,
   the drop planner's gate, `for`'s parser production.

## Lane std-39 — A116 (HIGH), A118 (R7), A117, A115, A119 (R6), A72
1. **A116** — `__json_tag` answers `""` for a non-string non-object (transformer.rs's helper table
   + interpreter.rs's twin); pins `null` / number / array / `{}`; every derive-using golden moves —
   regenerate, judge by RUNTIME output, run `copy_elision_census`. **A118 (R7)**. 2. **A117** — hide
   the prelude's 21 alias spellings; a pin that the export set is the designed 46; re-run std-38's
   census script and REPORT door 2's numbers (do not take door 2). **A115** — `AttrValue` arms for
   `Option<str>` / `Source<Option<str>>`, both twins. 3. **A119 (R6)** — `when_some` in both twins on
   `place_swap`'s machinery; FIRST reproduce kolt's "breaks on HMR" on a user-written `Slot` impl —
   if a user `Slot` impl cannot survive an HMR round, that is a FIND with its repro, not this item.
   **A72** — replace-state navigation (`navigate_replace`, or `navigate(path, replace)` — pick after
   reading `std::router`'s surface; kolt client.vl:39/44 is the customer). Sizing M–L. Owns json's
   helper, `random`, style/prelude.vl, the `AttrValue` impls, the new form, `std::router`.

## Lane reactive-39 — A110 door 2 (RULED), A114 (R2), A113 (R3), M83 (re-measure)
Read reactive-turns.md §7 whole (both measurements, the ruling, §7.4's two findings — both landed),
reactive-38's `door2-variant*.patch` (kept at `sweeps/order38/reactive-38/`), A114's probe
(`sweeps/order38/probes/scoped_effect.vl`). 1. **Door 2**, BUCKETED: derivations to a fixpoint, then
effects in ascending subscriber id; the contract is about NESTED forms only and the docs say order
among independent observers is NOT promised; the nested-`swap` pin goes 3/3 → 2/2; the no-cycle
gate is RE-MEASURED on the real build (the instrument read `unmounted cycles 0 → 1` from its own
wrapper closure — the build must read 0); cost against reactive-38's +23.5 % Ir. Goldens move —
runtime-identical or stop. 2. **A114 (R2)** — `scoped_effect` + `on_cleanup`; the probe's exact
sequence as a `reactive_lifetimes` case, inline and in a turn; disposal count = creation count; the
throwing-body case; a `RemoteSource` lease released at the run's end. 3. **A113 (R3)** — one
subscriber-count pin per row of the item's table; `guide/reactivity.md` "Who cleans up what".
4. **M83** — per-id `remove` vs a fresh map per wave, on a QUIET host, both `--jitless` Ir and thread
CPU; land only if both directions agree. Sizing L. Owns reactive.vl's scheduler + the `Source` trait's
new defaults. Tells the integrator when kolt's `page_content` latch can go (views.vl).

## Lane collections-39 — A112 S1 then S3 (RULED), M82
Read `proposal/incremental-collections.md` whole (§13 is ruled: `map_each`/`filter_each`; two hand
lists; `Move` an op from S1; `DeltaCursor` with a deprecated `KeyedCursor` re-export; `Splice`
carries removed VALUES; `set(whole)` records `Reset`, the diff door is `reconcile_to`), the eleven
probes at `sweeps/order38/papers-38/probes/`. 1. **S1** — `DeltaLog<O>` + the `DeltaSource<C, O>`
trait in `std::reactive` (a NEW file beside reactive.vl — reactive-39 owns reactive.vl itself);
`KeyedCell` re-based on it with its public surface and the `Patch` frame UNMOVED (the wire's
byte-identity pins are the gate; `std::reactive` imports nothing from `std::wire`). 2. **S3** — `each`
consumes ops where its source is a delta source; a plain `Source<List<T>>` keeps today's path —
and **M82**: a position index inside `reconcile` so that path stops being quadratic (95 M / 358 M /
1,370 M Ir at 500 / 1,000 / 2,000 rows is the before). 3. THE LAW as a property test in the suite
(the paper's randomized probe, ported); one push into 1,000 rows builds one row and runs no
reconcile pass, measured in Ir. `ListCell`/`map_each` (S2) is Order 40's. Sizing L. Owns the new
delta file, rpc.vl's `KeyedCell`, browser/ui.vl + process/ui.vl `each`/`reconcile`.

## Lane native-a-39 — F20: `Hash`, `lazy` parameters, overloaded operators; then backed enums, `for` over an `Iterator`, F21, N106
Read native-apps.md §11. In refusal-count order, each its own commit: the host type `Hash`
(`CanonicalHash`/`HashEq` — 10 programs, `board.vl`'s wall); `lazy` parameters (12 — a thunk at the
call, an `Rc<OnceCell>`-shaped force in the callee; M81's eager set shrinks it; B362's refusal is
solver-39's); overloaded operators (7 — `binary_op_dispatch`); backed enums (5); `for` over an
`Iterator` impl (5; B368's pattern arm when it merges); F21 (`Option<&mut T>` in a payload); `Map` /
`Set` `impl Js`; N106's two remaining halves. EXIT: `board.vl` byte-identical on both backends; THE
TABLE before/after; 0 differing / 0 rustc-refused / 0 broken under the whole set. Sizing L. Owns
`vilan-rust` lowering; `vilan-rt` value types. NOT yours: host modules, `runtime_host_binding`,
`native.rs`, `context.rs` (native-b-39).

## Lane native-b-39 — F18 slice 1: HTTP natively (R1), F23, F24, F25; merged AFTER native-a-39
Read kolt's server-leg census (`sweeps/order38/native-a-38/kolt-server-census.txt`: 55 host bindings
— this lane takes the HTTP/socket/header/url accessors, `queueMicrotask`, `Date.now`, `setTimeout`
(`sleep`), the `Number`/`String`/`Boolean` coercions; NOT `__db_*`, NOT fs, NOT JSON — those are
Order 40's). 1. **F23** FIRST — `context.rs` records the hidden parameter's flavour where it mints
it; delete `compute_context_flavours`' inference. **F24** — the executor's slab free list with a
generation counter, before any per-request spawn. 2. **`vilan-rt::http`** over `std::net`, no
dependencies: an HTTP/1.1 server (request line, headers, `Content-Length` bodies, keep-alive off in
v1), `Response::builder`'s native twin, driven by J6's executor (non-blocking accept registered with
the loop — design it in the report before building if it needs more than a poll per turn).
WebSocket upgrade is Order 40's unless the slice is small once HTTP stands. 3. **F25** — native exit
code 1 without Rust's banner; printing a host handle or a function-holding value is a COMPILE-TIME
refusal. EXIT: a corpus-style program — `std::http` server answering `GET /` with a fixed body —
runs natively and a test fetches it; the JS twin's output is byte-identical. Sizing L. Owns
`vilan-rt` host modules + `executor.rs`, `runtime_host_binding`, `native.rs`, `context.rs`'s one
record. The integrator resumes you once for the rebase onto native-a-39.

## Lane editor-39 — E207 FIRST, E206, E204, E202 + E203 (R9), E211, E212
**E207** — delete the stale per-parameter clause append (analyzer.rs ~19137; B309 made the clause
part of the closure TYPE's printed form); pins that COUNT the substring (the existing pins assert
`contains`, which a doubled clause satisfies); check bindings, fields, the trait/impl pair renderer,
completion detail, signature help. **E206** — a generic function's hover shows the declaration AND
the signature under the call's substitution, one fenced block, blank line between; one line when
nothing is substituted; signature help too. **E204** — census every consumer of a field's `///`
(hover on a read, on the declaration, on an initializer field, member completion, the struct hover
block, the docs generator, the playground), then make each carry it. **E202/E203 (R9)**. **E211** —
`filter_text` + an edit range on `Completion`. **E212** — a `$VILAN_STD` with no `macro_std` sibling
is refused naming both paths. Sizing M–L. Owns vilan-lsp hover/completion, the signature label's
parameter arm, the language configuration, toolchain resolution's refusal.

## Lane fmt-39 — E209, E210, then E205 (R8); merged LAST
**E209** — `reprint` re-parses its own output and declines on failure (a planted printer bug that
keeps the token count is the pin). **E210** — `WouldChangeTheCode` reports the first DIVERGING
token's span, not the file's first item. **E205** — comment reflow behind `[fmt] wrap_comments`:
paragraphs of consecutive `//`/`///` lines at one indentation re-filled to the width; NEVER
reflowed: fences, lists (hanging indent per item), tables, headings, URLs and code spans longer
than the width, lines with interior runs of 2+ spaces, toolchain directives (`// witness:`, …),
commented-out code, trailing comments; a words-in-order net that DECLINES (N90's exit 2) if the
words differ; idempotent; no character is ever substituted. REPORT how many lines a run over std
would touch (do not run it over std in the lane's commits). Sizing M–L. Owns formatter.rs.

## Lane hygiene-39 — DROPPABLE, lands FIRST: N109, N110, N111, N112, B366, D9
N109 (`List::new`/`push` become `Intrinsic` rows — coordinate: it touches two lines of vilan-rust;
land BEFORE the native lanes branch… they branch at GO, so this lane edits ONLY the vilan-core half
and hands the two vilan-rust lines to native-a-39 in its report); N110 (the witness gate normalizes
gensyms); N111's five one-liners; N112 (decide `Error.footnotes` against B355's landed warning —
rec keep the warning; write it down); B366 (one spelling for a nominal's generic parameter — the
Rust emitter's double handling is native-a-39's to delete after); D9 (three paragraphs into
editing-dx.md, handed back). Sizing M.

## Lane papers-39 — A120, A121, B363; NO tree change
`transport-rpc.md` § "a service as a plain HTTP API" (A120: a generated stub over the existing
connectionless POST leg; what a handle- or notification-bearing service is refused for; how
`authorize` composes with a login that mints the socket's token; status codes; kolt's three sites
rewritten as the worked example); a `focus-scope.md` (A121: tabbable query, `focus_first`, a scope
that cycles Tab within a subtree and restores focus on disposal without `inert`; nested overlays;
`autofocus`); `unit-literal.md` (B363: `()` vs `void` as an expression vs documenting the limit;
what A107's stub becomes; the breaking surface). Each with probes and a rulings section. Handed back
as markdown.

## Ownership map (conflict avoidance)
- reactive.vl: reactive-39. The NEW delta file + rpc.vl `KeyedCell` + `each`/`reconcile` in both
  ui twins: collections-39. std-39: json helper, random, style/prelude, `AttrValue`, `when_some`
  (a NEW block at the end of each ui twin — collections-39 edits `each` above it), router.
- analyzer.rs: solver-39 (return-type inference, refusals, drop planner); editor-39 (the signature
  label's parameter arm ONLY); native-b-39 touches `context.rs` only. parsing.rs: solver-39 (`for`).
  formatter.rs: fmt-39 (solver-39 hands B368's printing to it if the production changes shape —
  say so in the report). transformer.rs: std-39 (`__json_tag`'s row only).
- vilan-rust: native-a-39 (lowering) / native-b-39 (`runtime_host_binding`, the async arms' host
  calls). vilan-rt: native-a-39 value types / native-b-39 host modules + executor.
- Merge order: hygiene-39, editor-39, std-39 (goldens), solver-39, reactive-39 (goldens),
  collections-39 (goldens), native-a-39, native-b-39 (one rebase, by its resumed agent), fmt-39
  LAST. After EVERY merge that moved goldens: `scripts/integration/regen_goldens.sh` over the
  merged tree (runtime-judged). Every merge gate list includes `native_differential`.

## At the sweep (integrator, proposals)
- Close per the reports; A110 closes if door 2 lands; A112 stays OPEN (S2); F1/F18 stamped with the
  table and the HTTP exit; papers-39's three documents committed and their rulings asked.
- Kolt at the owner's word: the `page_content` latch retired (door 2); `lib/conditional_value.vl`
  → std's `when_some` (A119) and its B369 workaround comment dropped; client.vl:39/44 →
  `navigate_replace` (A72); lib/search.vl:26's manual counter → `for (i, item) in …` (B368).
- Order 40's queue: `std::db` natively (R1's crate) → the rpc server → kolt's server leg; A112 S2
  (`ListCell`, `map_each`); C14 S4/S5; F26; F22; M79 S1+S2; the v0.41.0 cut (HELD).
