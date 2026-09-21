# Order 38 — generics on the native backend, the scheduler's dead observers, and the breaking Wire receivers (drafted 2026-09-21; GO 2026-09-21, off vilan next @0fa109eb)

**GO (2026-09-21).** The owner: "Go with all recs (including the before go points)." R1–R8 are
RULED as recommended and the record-only defaults stand; 0fa109eb was pushed to `origin/next` at GO
and the worktrees are cut only after its CI run reads green. A110, A111, A112 and B359 are committed
with this file (the integrator's, under the owner's "go"). TEN lanes.
Order 37 sealed at 31c13567 (CI green on all eleven jobs); since then `next` carries 9e4ab461
(Dependabot opens against `next`) and 0fa109eb (the N21 toolchain bump, 1.90.0 → 1.98.1 — every
lane compiles under the new pin). The installed toolchain is `vilan 0.40.0 (0fa109eb7)` in both
locations. Ledger next id 546. Tracker 115 open at GO. Kolt:
`views.vl` + `routes.vl` carry the shell-key migration and the `page_content` latch (A110's
workaround), uncommitted, runtime unverified (no browser on this host; the e2e harness is
obsolete) — the owner's review.

The shape, read from Order 37's queue and the four items filed since. The owner's native order is
CLI programs → SERVERS → a UI layer after the F17 conversation, and the sizing says "S1b must not
be under-scoped": 51 of the backend's 98 refusals are monomorphisation, and ~2,240 lines of the
rpc server compile natively "the day generics work". So this order's native half is S1b whole
(F19 first) with J6's executor built BESIDE it in `vilan-rt` — and F18's http/db/rpc bindings are
Order 39's, on a backend that can already compile them. The order's one BREAKING surface is A108
(the Wire visitor's by-value receivers, which force ten of the eleven frame-scoped cells Order
37 could not retire), merged LAST. Two miscompile-class bugs lead their lanes: B359 (a trait
default's `self.member` hijacked by an implementor's inherent member; a `ReferenceError` when that member is `external`) and
A110's second face (outside a turn a DISPOSED observer still fires — a `swap` builds a subtree
under an owner nothing will ever dispose). Around them: the solver residue Order 37 filed
(B354 HIGH, B355–B357), the kolt sweep's std gaps (A104–A107, A109, I3, I4), kolt's keystroke
(M76 is the largest cost left; M78 makes the instrument honest first), the editor's eight, a
hygiene lane for N98–N107, and two PAPERS — A112 (incremental collections; the receiver question
is already probed) and A110's ordering rule as a `reactive-turns.md` section.

## Rulings at GO (owner) — ALL as recommended; the ones that change what a lane BUILDS
- **R1 — B359: what `self.name(..)` means inside a trait DEFAULT body (solver-38).** Rec: (a) the
  TRAIT's member, always — `Self` is opaque there; an implementor's inherent members are not in
  scope (Rust's rule, and what the generic-bound route already does). Both faces close in one
  fix. Under (b) (inherent wins) Face 1 is as designed, defaults become implementor-dependent,
  and only the `external` emit is a bug. Inherent-wins OUTSIDE default bodies is unchanged
  either way.
- **R2 — A108: the Wire receivers, BREAKING (wire-38).** `Serialize`/`Deserialize` methods take
  `&mut self`; `Wire::describe`/`rebuild` take `&mut S`/`&mut D`; every std impl and both derive
  emitters move in one commit; the `shared_census` json/binary rows drop to zero. Rec: YES, its
  own lane, merged last. Blast radius per native-a-37: 17 std Wire impls, the derive emitters, 3
  fixtures, kolt's derives (re-expanded, no source change) plus any HAND-written impl in kolt
  (re-census read-only). `fs.vl`'s `Reader.cursor` is NOT in scope (its `next` awaits).
- **R3 — B355: E189's broad gate (solver-38).** Rec: the third option — give B279's fence a
  NON-diagnostic face (the dispatch fallback's candidate set exposed on `Program` or a test-only
  accessor), re-pin B279 on it, THEN land the broad gate; E191 closes with it (kolt copy: 184 →
  9 → expect 1).
- **R4 — A110: door 1 now, door 2 as a paper (reactive-38, papers-38).** Door 1 (a subscriber
  liveness flag lowered by `Subscription::dispose`; the inline loop and `drain`'s wave loop skip a
  lowered one) is a LEAK fix and changes no ordering — rec: build. Door 2 (derivations to a
  fixpoint, then effects in ascending subscriber id = parent-before-child) changes observable
  effect order for every app — rec: a `reactive-turns.md` section this order, the ruling on the
  paper ("is effect order within one wave part of the contract?"), the build in Order 39; kolt's
  latch stays until then.
- **R5 — the native split (native-a-38, native-b-38).** Rec: S1b and J6 run in PARALLEL — the
  executor is a `vilan-rt` module with Rust-side pins and owns only the emitter's `async`/`await`
  arms; S1b owns instances, module-level bindings, operators, `?` and the intrinsics; J6 merges
  AFTER S1b. F18's http → db → rpc is Order 39. Alternative: one serial lane (safer merges, a
  lane-order slower). The order's native exit: `board.vl` flips from a named gap to a byte-identical
  comparison, and the async corpus programs print byte-identically.
- **R6 — A107: a `void` rpc return (wire-38).** Rec: ADMIT it — `Task<void>` awaiting the ack, an
  empty `Ok` on the wire; A75's notifications already cover fire-and-forget, so an awaited void is
  the honest shape for kolt's `remove_message`. Alternative: refuse with the steer "return `bool`,
  or `notify`". Whichever: `Result<i53, str>` is VERIFIED on the sealed toolchain first (store.vl:166
  predates A82).
- **R7 — A106: the style vocabulary outside a css hole (std-38).** Rec as filed: widen
  `std::style::prelude` with the four TYPES (`Length`, `Cursor`, `TextAlign`, `AlignItems`) and
  document the file-level `import std::style::prelude::*;` idiom NOW; door 2 (the `std::web`
  prelude re-exports it, ambient in every web file) only after a name-collision census over std,
  examples, docs, the website and kolt reads ZERO — the lane runs the census and reports; it
  does not take door 2 on a non-zero count.
- **R8 — the A103 gate's wording.** "A changed golden whose RUNTIME output differs is
  stop-and-decide" (Order 37 wrote "a changed golden"). Rec: adopt; it is in Mechanics below.
- Record-only defaults (written as built at the sweep unless the owner objects): C14 S5 (the
  counted JS instrument) is built WITH S4, not this order; C15 waits for S1b's corpus and is
  MEASURED by native-a-38 (`VILAN_NATIVE_REPORT_BOXED=1` over the widened corpus), not built;
  F1 S2, F15, E182 wait for F17 (the owner's conversation — nothing in this order waits on it);
  A111 (keep-alive `swap`) stays a paper-not-queued; A112's naming (`map_each`/`filter_each`) and
  its two-trait answer are the PAPER's to argue, ruled after it lands; L22 waits on the App's
  client-ID secret (the owner's); L20 is the owner's own; B348, B298, A94, M60, M56/M57/M54 and
  E121's remaining path are not this order; K14 merges at the v0.41.0 cut, which stays HELD (the
  owner's call — this train now carries A101's breaking codemod and, if R2 is yes, A108's).

## Mechanics (every lane)
Order 37's section stands (briefs37.md "Mechanics") — restated here in full where a rule changed.
- Worktree `vilan/.claude/worktrees/<lane>` branched from `origin/next` (the pushed 0fa109eb);
  NEVER the main checkout; NEVER `git stash`. Kolt (`~/code/kolt`) and the proposals repo are
  READ-ONLY: read kolt ONCE into your scratch and work from the copy; anything you would write in
  proposals (papers, item stamps) is handed back in the report.
- **Kills: `kill <pid>` of a PID YOU recorded — never `pkill`/`killall`/`pgrep | xargs kill` by
  name or pattern** (three lanes did in Order 37 and killed two integrator gate runs). Find a
  runaway of yours with `pgrep -f '/worktrees/<lane>/'`.
- Lanes NEVER PUSH. Commit as the worktree's configured identity, SIGNED — **a lane that cannot
  sign says so at its FIRST commit** (seven were re-signed by rebase last order). Never pass
  `--author`.
- One commit per item (a slice may take several, each buildable); message = the CHANGELOG
  entry's first sentence; the entry under its family marker; parity gate `-p vilan-cli --test
  release_scripts`. Breaking this order: A108 (R2), B359 if a std/estate default body changes
  meaning under R1 (census first — expected none), A110 door 1 only if a pin observed the dead
  call (a finding, not a note). Each carries its migration note.
- Diagnostics: a new message is a ledger row written `NEW` (the integrator numbers; next id 546
  — NEVER a literal id). **A rowed message is ONE literal, `\`-continued with the space BEFORE
  the backslash; `+`-concatenation fails the ledger's search; `concat!` only for non-rowed
  literals.** A message whose FIRING changes means `-p vilan-lsp` too.
- Parser rule constants need TWO edits (`RULE_STATEMENT_SITES`, `CURATED_RULE_STATEMENTS`);
  report the DELTA. **A DELETED entry of a list const is named in the report like an edited
  one** — the merge's union resurrects it otherwise (Order 37's `HASH_IS_NOT_A_CSS_VALUE`).
- Pin locations as briefs37 lists them. New this order: native pins in vilan-cli
  `native_differential.rs` and Rust-side `vilan-rt` unit tests; the census pin
  `shared_census.rs`. **Every new test file uses the support scratch root (N86's gate reds a
  `temp_dir()` at the merge); a test binary's staging directory carries the process id; a lane
  adding or renaming a crate runs `--test agents_map` and `--test third_party_notices`.**
- Shared test files: ADD whole new `fn`s; an existing fn or program const you edit is NAMED in
  the report, with its crate. Report every `--test` name WITH its crate.
- Goldens move on ANY change to what std::reactive/std::ui/std::style emit; regenerate over YOUR
  tree and say so; the integrator regenerates once over the merged tree and judges with the
  gensym-normalized diff. **A changed golden whose RUNTIME output differs is stop-and-decide,
  never a regeneration.** Expected movers: reactive-38 (door 1 changes `notify`/`drain`), perf-38
  (M80 and M81 move goldens BACK — say how many), wire-38 (json/binary bodies). Nobody else.
- Estate sweeps name EVERY crate with `.vl` fixtures — vilan-core, vilan-cli, vilan-lsp,
  vilan-ide, vilan-wasm, `vilan/test`, `vilan/docs`, `vilan/examples`, `vilan/benchmarks`, the
  `vilan init` templates.
- Tests: `cargo nextest run -p <crate> --test <name>` targeted, packages run separately; the
  whole `-p vilan-core` run is the merge gate; clippy `--all-targets -D warnings` UNDER 1.98.1
  (eight releases of new lints landed with the bump — a new lint in your diff is yours);
  `cargo fmt --all --check`; `vilan fmt` over any `.vl` touched — exit 2 is a DECLINE (N90),
  report the file. **Long runs in the FOREGROUND with a timeout** — a lane's background task dies
  with the lane's own task lifetime. Heredocs in their OWN shell call.
- Perf claims: CPU time or callgrind Ir + loadavg, never wall; a sub-1 % Ir claim needs a profile
  diff. Counts: count BLOCKS/SITES by parse, not mentions by grep.
- Scratch: `scratchpad/<lane>/`, shared — read nothing outside yours. No SendMessage: a question
  you cannot answer from source is an OPEN Q and you build your recommendation.
- Report (final message): per item/slice — commit sha, what landed, pins (crate + test name),
  numbers; FINDS as candidate items with evidence; OPEN Qs; unfinished work and why; corrections
  to this brief. Model: Opus — never Fable; the integrator passes `model` explicitly.

## Lane hygiene-38 — DROPPABLE, lands FIRST: N98, N99, N100, N101, N102 (a slice), N103, N104, N105, N107, L23
Read each item. 1. **N100 then N99, N98** — fix rows 494/499 (`{{`/`}}` keys), then widen the
ledger's check (2) to EVERY fragment; hand-row `asset::staged`'s registry refusal through
`ROWS_THE_ENUMERATION_CANNOT_REACH` (and the second message N99 names); a second gate over PROSE
literals (the swallowed-continuation class at macros.rs ~1535, document.rs ~18661, formatter.rs
~13388, the ~15 `.vl` program consts) with an aligned-table exemption. 2. **N101** — re-key
`deep_nesting.rs`'s parse-frame figure to the measured 32.8 KiB/level and the doc claim beside
it; **N104** — the three AST doc-comment traps, fixed at the declarations; **N105** —
`manifest::toolchain_root` for a `[library]` with `root = "."` (pin a source-root-less std);
**N103** — `vilan run` stops creating a `dist/` that holds only the macro table (N92's root).
3. **N102** — move the suites that need one line each off the shared tmpfs; shrink
`BINARIES_STILL_ON_THE_SHARED_TMPFS` and report the remainder by file. **N107** — one
implementation of E69's arrow (keep the Rust sync gate; the python generator's default mode
calls it or is deleted — say which). 4. **L23** — a `workflow_dispatch` dry-run lane in
`release.yml`: build → upload → download → checksum, NO publishing step; it cannot be run from a
lane — hand the YAML back reviewed against `actionlint` if present, and say what the integrator
must trigger. Sizing: S ×10 = M. Owns `diagnostics_ledger.rs`, the test-support plumbing,
`release.yml`. Nothing in analyzer.rs beyond the literals N98 names.

## Lane solver-38 — B359 (R1; MISCOMPILE, TOP), B354 (HIGH), B356, B357, B355 (R3), E199
Read B359 (both repros are inlined in the item), B205/B216/B243/B254's pins (default-body `Self`
specialization; dispatch candidates by name), E185's `AdmissionMiss` plumbing, B279's fence pin,
B352's three pins, `binding_is_weaker`.
1. **B359.** Plant both faces red on 0fa109eb. Under R1 = (a): a default body's receiver call
   resolves against the TRAIT's member set before specialization looks at the concrete type; the
   four pins the item owes (Face 1 prints `trait push` ×2; Face 2 runs and does NOT reach `List`'s
   own `push`; the direct and generic-bound routes print the same thing; an ordinary call site
   still reaches the inherent member). CENSUS before landing: every std/examples/docs default
   body whose `self.name(..)` names a member some implementor also declares inherently — each is
   a behaviour change to report (expected none; any hit is a `breaking` note naming the program).
   Whatever R1 says, the `external` emit hole is closed: a call that lands on an `external`
   member emits the external's call form, never a mangled name nothing defines.
2. **B354 (HIGH).** A derived body's admitting file is the file carrying the `[derive(..)]`; pin
   the three-file shape; THEN re-run Order 36's curation over the codec blocks exported for the
   sentinel rule and re-privatize what only it needed — list every re-privatized name.
3. **B356** — enumerate the six path shapes carrying written type arguments, pin each against a
   contradicting argument, fix the inert ones at their seed. **B357** — a nullary variant of a
   generic enum mints fresh holes at the use site; retire `binding_is_weaker`'s special case iff
   B352's three pins stay green without it.
4. **B355 (R3)** — the fence's non-diagnostic face first, B279 re-pinned on it, then the broad
   gate with `b229_only_…`/`b241_…` restated as deferrals; re-run the kolt copy (expect 1) and
   close E191 on the number. **E199** — the refused-bound message takes `T` from the declared
   position, not the closure body.
Sizing: M + M + S + S + M + S = L. Owns the default-body resolution seam, derive admission, the
context-family gate. Runs `-p vilan-lsp` (B355 changes what fires).

## Lane reactive-38 — A110 door 1 (R4; a LEAK), A105, A73, the door-2 MEASUREMENT
Read A110 (the probe and its output are in the item), reactive.vl's `enqueue`/`drain`,
`Subscription::dispose` and its pending-queue scrub, `SignalCell::notify`'s inline arm,
browser/ui.vl `place_swap`/`Conditional::place`/`Each`, C14 S3's `Weak` subscriber list.
1. **Door 1.** The item's probe as two `reactive_lifetimes` cases, planted red: after the outer
   disposes, the inner observer fires ZERO times — inline AND in a turn's later wave. The flag:
   one liveness bit per subscriber that `dispose` lowers (or the `release` cell's one-shot —
   pick after reading S3's representation; say which and the per-subscriber cost in `Shared`
   boxes against `shared_census`). The DOM pin: nested `swap`s on one source, the outer keyed on
   a projection — sign-out builds the inner render closure zero times and owner disposals equal
   creations. The process twin (`process/ui.vl`) gets the same pin or a sentence saying why not.
2. **Door 2 — measure, do not build.** Instrument a scratch build: tag derivation subscribers,
   drain derivations to a fixpoint, run effects in ascending id; report which corpus/reactive
   pins CHANGE OUTPUT ORDER (the list is the paper's evidence) and the per-wave cost in Ir.
   Hand the numbers to papers-38's section; nothing of door 2 lands.
3. **A105** — `bind_attr` over `Source<Option<str>>` (`None` removes the attribute), both twins,
   a `ui_rows`/`ssr_differential` pin. **A73** — `Storage::keys()` and `Debounce::flush()`.
Sizing: M + S + S + S = M. Owns reactive.vl's scheduler and subscriber record; browser/ui.vl and
process/ui.vl `bind_attr` only. Moves goldens (say which).

## Lane std-38 — the kolt sweep's std gaps: A104, A109, I4, I3, A106 (R7)
1. **A104** — `Json`/`FromJson` for `Result<T, E>` in the `[kind, value]` shape kolt hand-writes
   (shared.vl:65/80: 0 = Ok, 1 = Err) — READ wire-38's ownership note: json.vl's visitor
   receivers move under A108, so you add the two impls in a NEW block at the end of the file and
   wire-38 re-spells them at its merge. **A109** — `Result::expect_err` joins the lazy retrofit
   (lazy-37's 304-program differential is kept: `sweeps/order37/tools/lazy_differential.py` — re-run it).
2. **I4** — `Default` for `List`, `Map`, `Set`, `str`, `bool`, `Option<T>` (verify each is
   missing first). **I3** — the iterator-adapter remainder the item lists (`filter_map` first —
   kolt's stamp).
3. **A106 (R7)** — the four types join `std::style::prelude`; the styling tour names the
   file-level idiom; the door-2 census as a script + a table in the report.
Sizing: S ×5 = M. Owns option.vl/result.vl/number.vl's `Default` block/iter.vl/style.vl's
prelude; json.vl's new block only.

## Lane perf-38 — M78 FIRST, then M76, M77, M80, M81; M79 as a PAPER section
1. **M78** — `[vilan phase]` marks on a CPU clock (thread CPU where the host has it; the pin
   DECLINES where it does not); every later number in this lane reads it.
2. **M76** — which checks an entry-shaped world can REUSE (those not reaching the alias); store
   that record; the six kolt files (M70's) measured paired, before/after, CPU + loadavg.
   **M77** — `statement_sources` only for the colliding names once a collision is banked.
3. **M80** — `canonical_instance_body`'s key normalizes local gensyms (`observe` is emitted twice
   in two goldens: −2,857 B over the corpus expected). **M81** — `record_lazy_arguments` keeps an
   INERT argument eager (literal, enum constant, `[]`): 111 of 114 thunks; report how many of
   A103's 16 moved goldens return byte-identical; unobservable by construction — the differential
   harness proves it.
4. **M79** — the paper section (analysis-reuse.md: the eleven queues, the deferral rule),
   handed back; NO build.
Sizing: S + M + S + S + S + paper = M–L. Owns the phase clock, the checks-reuse record, the two
transformer seams it names. Moves goldens BACK.

## Lane editor-38 — E194, E195, E196, E197, E198, E200, E201, N108
**E198** first (the playground's `std_sources` conflates "is std" with "definition-site
diagnostics frozen" — split the two sets; vilan-wasm compile.rs:168 records why a naive fill
breaks split-wired chunks; the pin is the A99 steer suffix appearing in the playground).
**N108** — `vilan fmt` declines a braced import list (kolt client.vl:7's shape, minimized) — a
round-trip bug N90 made visible. **E197** — format-on-save SAYS it declined (LSP
`window/showMessage` once per file per cause; the wasm `format_program` returns the verdict).
**E201** — A101's quick fix for the two mechanical cases, sharing the codemod's rules (E167's
converter). **E194** — `wordPattern` admits `-` in attribute position (pin the completion at
`<svg stroke-w|`). **E195** — `nominal_id_by_name` resolves through the scope chain (E193's
shape). **E196** — the HMR overlay reads the `SourceId` an `Error`'s note carries. **E200** —
one report for a lazy argument reaching a resource through a field.
Sizing: S ×8 = M. Owns vilan-ide completion.rs, vilan-lsp document.rs quick-fix arms (one each,
named), the formatter's import printing, the language-configuration.

## Lane native-a-38 — F19 then F1 S1b: generics, module-level bindings, operators, `?`, intrinsics
Read native-apps.md §5-S1 and §10 whole, `vilan-rust` (~1,950 lines), `vilan-rt`, vilan-cli
`native.rs`, `native_differential.rs` (`platform_free_programs()`, `PLATFORM_MODULES`), and HOW
THE JS BACKEND INSTANTIATES generics (`push_or_share`, `canonical_instance_body`) — the instance
set already exists; the Rust emitter should consume it rather than re-derive it (if it cannot,
that is your first OPEN Q, with the reason).
1. **F19.** `vilan-rt` reachable from an INSTALLED toolchain: embedded and materialized under
   `~/.vilan/` keyed by toolchain version (the `vilan-embedded-std` pattern; B346's one-root rule
   applies — `$VILAN_RT` wins, two roots are refused); a release-gate pin building `board.vl`
   from an installed layout. `agents_map` + `third_party_notices` if a crate is added.
2. **S1b.** In refusal-count order: generic type parameters (29), named generic fns (17),
   generic-parameter dispatch (5); module-level bindings via `thread_local!` (6; `lazy`
   bindings per A100's semantics); overloaded operators (6); `?` (2); the remaining intrinsics
   (3); `JSON.stringify` (2) only if `vilan-rt`'s `Js` renderer already covers it. `resource`
   teardown stays refused unless its output is RIGHT (a wrong answer is never left standing).
   **N106** rides here: `f64` printing pinned on the JS side against `vilan_rt::js_number`.
3. **Exit.** `board.vl` flips from a named gap to a byte-identical comparison; the table in the
   report — corpus / platform-free / emitted / refused-by-name (by construct) / byte-identical /
   differing (MUST be 0) / rustc-refused (MUST be 0); the boxed-binding count over the widened
   corpus (C15's measurement); compile CPU per program. Then, READ-ONLY, try kolt's server leg
   (3 files, 564 lines) and list what still refuses — that list is Order 39's brief.
Sizing: S + L. Owns `vilan-rust` (everything but the async arms), `vilan-rt` (everything but
`executor.rs`), `native.rs`, the differential's enumeration. `async`/`await`: NOT yours.

## Lane native-b-38 — J6: the single-threaded executor (R5), merged AFTER native-a-38
Read native-apps.md §10 "the executor, designed", `transformer.rs::helper_source` (the contract:
`__task`, the nursery join, `sleep`, `Timer`), reactive-turns.md, the async corpus programs.
1. `vilan-rt/src/executor.rs`: the seven primitives as designed — `Task` a slab handle (eager
   spawn; failure latched at settle; an unowned unobserved failure reported once with its
   origin), microtasks drained to exhaustion before the deadline heap, `Nursery` with a `Weak`
   parent and the join reproduced EXACTLY (the child list grows mid-drain; cancel, absorb,
   propagate with `" (in task spawned in …)"`), detached nurseries, abortable `sleep`, memoized
   `Timer`. Rust unit tests for each ordering rule — `vilan-rt` stays dependency-free.
2. The emitter's async arms: `async fun` → Rust `async fn`, `await` → `.await`, `async fun main`
   (2 refusals) — `Pin`/`Send` never surface. Work against NON-generic async programs until
   native-a-38 merges; the integrator rebases you once.
3. Exit: every async corpus program the backend accepts prints byte-identically (`reactive-turns`
   is the ordering pin); the ones still refused are named with their construct.
Sizing: M. Owns `executor.rs` and the emitter's async arms ONLY.

## Lane wire-38 — A108 (R2; BREAKING), A107 (R6); merged LAST
Read A108, native-a-37's FIND-1 (notes37.md: the probe that compiled with zero `__shared_new`),
wire.vl, json.vl, binary.vl, both derive emitters, `shared_census.rs`, rpc.vl's return
rendering and the analyzer's rpc return allowlist.
1. **A108.** One commit: the two visitor traits on `&mut self`; `describe`/`rebuild` on
   `&mut S`/`&mut D`; all 17 std impls; both derive emitters; the 3 fixtures; json/binary's ten
   cells become locals (`shared_census` rows → 0, `Shared::new(` 128 → 118 or the number you
   measure). The service hash of a handle-free service stays byte-identical (78bdada7's pin) —
   the WIRE does not move; a moved frame is stop-and-decide. Re-spell std-38's A104 block if it
   merged before you. Kolt: count hand-written `Serialize`/`Deserialize`/`Wire` impls on your
   copy and write the migration note with the exact before/after.
2. **A107.** Verify `Result<i53, str>` returns on 0fa109eb (pin it if it works; fix it if not);
   `void` per R6 — the allowlist, the generated client's `Task<void>`, the empty-`Ok` ack; pins
   in `service_layer.rs` (round-trip) and `rpc_http.rs` (the connectionless leg).
Sizing: M–L + S. Owns wire.vl, json.vl, binary.vl, the derive emitters, rpc.vl's return path.

## Lane papers-38 — A112 (incremental collections) and A110 door 2's section; NO std change
Both are handed back as markdown in `scratchpad/papers-38/`; probes are yours to write and run.
1. **`incremental-collections.md`.** A112 carries the theory, the three layers, the cost table,
   and the receiver probes A/B/C with their results (re-run them on 0fa109eb; B is B359 and must
   be read as such). The paper owes: the op vocabulary per shape with the LAW stated as a
   property test (and a working probe of it over random op sequences, several ops per turn,
   `Reset`, a cursor past `keyed_log_limit`); the delta-source trait lifted from `KeyedCell`
   with `std::reactive` still importing nothing from `std::wire`; purity and the per-element
   owner (A110's ordering applies); the `set(whole_list)` compat path; cursor lifetime; a
   delta-driven `each` measured against A98's settled-run scan at 1,000 rows (Ir); what
   `KeyedCell` is after the lift with its surface and the `Patch` frame unmoved; the slices
   S1–S4 sized; the ruling questions with recommendations (naming; one macro stamping both
   traits' defaults or two hand lists; `Move` as an op or a `Reset`).
2. **`reactive-turns.md` § "order within a wave".** From reactive-38's measurement: the rule
   (derivations to a fixpoint, effects ascending by id), why id order IS parent-before-child,
   which pins change, the cost, Solid's precedent, what `resume` order A111 would inherit, and
   the one ruling question. A111 is NOT in scope beyond that sentence.
Sizing: L (paper) + S. Owns nothing in the tree.

## Ownership map (conflict avoidance)
- reactive.vl: reactive-38 (scheduler, subscriber record). wire.vl/json.vl/binary.vl: wire-38;
  std-38 adds ONE new block at json.vl's end. rpc.vl: wire-38 (return path) only.
  browser/ui.vl + process/ui.vl: reactive-38 (`bind_attr`). style.vl: std-38 (prelude).
  option/result/number/iter: std-38. Nobody else edits std.
- analyzer.rs: solver-38 (default-body resolution, derive admission, the context gate, B356's
  seeds, B357); perf-38 (the checks-reuse record, `record_lazy_arguments`, `statement_sources`);
  wire-38 (the rpc return allowlist — one fn); hygiene-38 (the literals N98 names).
- transformer.rs: solver-38 (the `external` call form); perf-38 (`canonical_instance_body`).
  `helper_source` is READ by native-b-38, edited by nobody.
- `vilan-rust`/`vilan-rt`/`native.rs`: native-a-38, except `executor.rs` + the async arms
  (native-b-38). `Cargo.lock` unions at the merge.
- vilan-ide/vilan-lsp/vilan-wasm/formatter: editor-38; solver-38 adds no quick fix this order.
- Tests: `reactive_lifetimes.rs`, `ui_rows.rs` (new fns) — reactive-38; `native_differential.rs`
  — native-a-38 (native-b-38 adds fns); `shared_census.rs`, `service_layer.rs`, `rpc_http.rs` —
  wire-38; `diagnostics_ledger.rs`, `deep_nesting.rs` — hygiene-38.
- Merge order: hygiene-38, editor-38, std-38, perf-38, solver-38, reactive-38 (goldens),
  native-a-38, native-b-38 (rebased once), wire-38 LAST. Merges DETACHED (merge_fold under
  `setsid nohup` + an until-grep waiter); never chain a merge behind another's outcome check;
  the split golden regenerated ONCE over the merged tree after the last reactive-emitting merge.

## At the sweep (integrator, proposals)
- Close per the lanes' reports: B359 B354 B355 B356 B357 E191 E199 · A105 A73 · A104 A109 I4
  A106 (or re-point at door 2) · M76 M77 M78 M80 M81 · E194–E198 E200 E201 N108 · N98–N105 N107
  L23 · F19 N106 · J6 · A108 A107. STAY OPEN with stamps: A110 (door 1 landed; door 2 behind its
  ruling), A112 (paper landed; rulings asked), A111, M79 (paper), F1 (S1b), F18 (Order 39), C14
  (S4 unblocked), C15 (measured), I3 if a remainder remains, D9 (the integrator writes the one
  sentence into editing-dx.md).
- Papers: `incremental-collections.md` and the reactive-turns section committed from
  papers-38; native-apps.md §11 as-built (S1b's table, the executor as built, kolt's server-leg
  refusal list); signal-cell-representation.md (A108's census); analysis-reuse.md (M79);
  transport-rpc (A107's `void`); the ledger paper re-keyed from `NEW` rows (546 →).
- Kolt at the owner's word: A108's hand-impl migration (if any); `remove_message` → `void`
  (A107); shared.vl:65/80's hand `Json` pair dropped (A104); styles.vl:54/103's nine-name imports
  → the prelude (A106); `bind_attr_proper` dropped (A105); Order 37's owed list if still owed.
  The `page_content` latch STAYS (door 2 is Order 39's).
- Chronicle: cycle 56 entry at GO; MERGED and SEALED paragraphs; toolchain refresh both
  locations; reap ten worktrees.
- Order 39's queue, written at the sweep: F18 http → db → rpc against kolt's server leg (the
  refusal list native-a-38 hands back is its brief); C14 S4 + S5; C15 if the measurement asks;
  A110 door 2 (if ruled); A112 S1 (the lift) → S2 (`ListCell`, `map_each`, the law pin) if
  ruled; M79's build; F17 when the owner opens it; the v0.41.0 cut (HELD).
