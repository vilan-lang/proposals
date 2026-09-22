# Order 40 — the pipeline paper and its `dyn`, the native server's second slice, and the rulings built (drafted 2026-09-22, off vilan next @49de3915; awaiting GO)

**Base.** Order 39 sealed at 49de3915 on 2026-09-22 (CI 35683785688 green 10/10; local seal green
twice; toolchain `vilan 0.40.0 (49de39157)` in both locations; nothing has landed on `next` since).
Ledger next id **550** (`crates/vilan-cli/tests/diagnostics-ledger.tsv`, max 549). Tracker 124 open.
Kolt is at 9a057c6 (`wip`, the owner's) with `src/channel.vl` modified and `src/lib/reactive2.vl`
untracked — the pipeline sketch this order's paper is about; `vilan check` was 0/0 on 49de39157
before those two edits. Every ruling this order builds was made by the owner on 2026-09-22 and is
stamped on its item (`sweeps/order39/rulings40.json`); nothing below is a record-only default
except where the section at the end says so.

**The shape.** Three kinds of work. **The reactive core's next design** — the owner's push-pull
pipeline (A124, rewritten from the read-tracked `computed`): one lane writes the paper AND its S1
probe in std with no compiler change, and a second builds the one language feature the design
needs, `dyn Trait` over an object-safe core (R3, reopening B4 in that scope) with the bare-trait
FIELD refused and steered. Beside them, A123's two dynamic combinators land on today's `Source` (they
become nodes later, unchanged in meaning), and A125's `K: Hashable` makes reorders linear.
**The native server, slice 2** — `std::json` natively so a `Server` can be built from a builder,
`std::db` as the SEPARATE SQLite crate (Order 39's R1), the rpc server, and the exit "kolt's server
leg runs natively"; a second native lane takes the emitter's latent-wrong classes (F30 is a silent
copy of a module-level aggregate) and the liveness pass. **The rulings and the bugs** — B362's
dispatched half (thunk), F32 (`i128` limit), E215 (`comment_width`; std opts in at 84), A120 S1–S5
(a service as an HTTP API, after its two HIGH bugs B374/B375), A121 (focus scope, after the DOM stub
grows its four reads), the solver's nine (B377 MISCOMPILE first; B378/B379 unblock A112 S3), the
editor's four, the formatter's two, hygiene's eight, and the I5 paper (`usize` everywhere — the
breaking train the v0.41.0 cut waits on).

**Twelve lanes**, two more than Order 39 — the pipeline work (paper+probe, `dyn`) is two lanes that
did not exist, and A121 needs its own because it edits `std::dom`/`std::ui` beside the std lane's
rpc files. Merge order at the end; fmt-40 LAST because E215's std opt-in reflows comments across
every std file the other lanes touched.

## Rulings — all RULED 2026-09-22 (the owner); what each lane BUILDS from them
- **A124 R1–R5 (reactive-40, dyn-40).** R1 `get` stays on the trait. R2 a notification carries NO
  payload; the leaf pulls through `get()`; one subscriber id per leaf chain so door 2's dedup absorbs
  a diamond's duplicate — AND cells are welcome mid-chain: `.cell()` (the owner's name; not `memo()`)
  is one more node, composable anywhere, for an efficient cached value after a complex mapping; cells
  at EVERY step is what is inefficient. R3 `dyn Source<T>` over the object-safe core (`get`,
  `on_change`), explicit keyword, no resources; a bare `Trait` at a struct FIELD is REFUSED for now
  with a steer to `dyn Trait` (B184's hidden generic withdrawn at that position; parameters B186 and
  bindings B161 unchanged). R4 kolt migrates; the cut may come before the migration. R5 the pending
  family is `Pending<T>` or `Resource<T>` (the paper picks — rec `Resource<T>`, since it can go from
  settled BACK to pending when an upstream changes, and the paper states that state machine), with
  BOTH `.or(default)` → `Source<T>` and `.optional()` → `Source<Option<T>>`; sub-question for the
  paper: on re-pend does `.or` reset or hold (rec: reset; a `.latest(default)` holds).
- **A125 (collections-40).** YES — `K: Hashable` on `reconcile` and the `each*` family; BREAKING;
  kolt's two `each_values` over structs derive `Hashable`; pin a 1,000-row reverse linear in Ir.
- **I5 (papers-40).** The last question: a length or position crossing rpc KEEPS its wire width —
  frames byte-identical, the contract hash does not move; the paper proves it with a `Patch`/`Delta`
  frame byte-compared before and after. Everything else was ruled 2026-09-21 (distinct type; underflow
  unspecified but never memory-unsafe; literal inference a general law — B370 landed; no `isize`;
  in the breaking train BEFORE the cut).
- **F32 (native-a-40).** (b) an `i128` LIMIT: a literal past it refused at compile time, an overflow
  traps at runtime, the book states the limit; the two BigInt programs flip or their refusal names
  the rule.
- **E215 (fmt-40).** R1 a `[fmt] comment_width` key, default = the code width; R2 std opts in at the
  measured 84; R3 no default flip before std has run under it for one order.
- **B362 (solver-40).** The dispatched half: THUNK at the dispatched call site through the callee's
  recorded convention; the direct-call pins stay true; un-ignore the red pin first.
- **A120 Q1–Q5 (std-40).** As §9.7.12 recommends: an opt-in `[service(http)]` MARKER; a second
  `authorize_request` hook; no CORS in std (the content-type check stays); `over_http` (no call
  made); an application `Err` is ALWAYS 200; envelope and status never disagree.
- **A121 Q1–Q6 (ui-40).** As focus-scope.md §10 recommends: a WALK; `Contain` + `Wrap`; the SHOW
  calls `focus_initial`; `View::autofocus()` sets the attribute; no `inert` arm; the stack in std;
  trap at mount and focus at show as two acts. The DOM stub grows FIRST.
- **N119 (hygiene-40).** Wanted: the language server survives an analyzer abort.
- **Asked at GO (rec in each):** R-a `dyn` this order in parallel with the paper (rec YES — the
  object's core is fixed by R3, independent of how nodes look; the alternative waits an order).
  R-b the v0.41.0 cut: I5's S2 is the breaking train and is Order 41 at the earliest (paper first),
  so the cut waits for it unless the owner cuts before (R4's leave) — rec HOLD through Order 40.
  R-c B382 (no type alias): papers-40 writes the one-page recommendation; no build this order.

## Mechanics (every lane)
briefs39.md's "Mechanics" stands in full (never `git config`; the item's text is a HYPOTHESIS —
verify the premise and say so; a passing probe must be shown to BUILD something; every std-touching
lane gates `-p vilan-cli --test native_differential` default AND `VILAN_NATIVE_DIFFERENTIAL=1`; the
golden suites are `corpus`, `split`, `examples`, `copy_elision_census`; a `-p <crate>` spec with zero
tests exits non-zero; `vilan build vilan/test/<x>.vl` overwrites the golden — probe over a scratch
copy; a BREAKING lane re-sweeps the estate INCLUDING the `.vl` consts inside Rust tests,
vilan-website (30) and vilan-playground (6); SendMessage works — a lane answers no question itself;
worktrees off `origin/next` @49de3915, never the main checkout, never `git stash`, never push,
`kill <pid>` of recorded PIDs only; one commit per item with its CHANGELOG entry and family marker;
ledger rows written `NEW` (next id 550), a rowed message is ONE `\`-continued literal; long runs in
the FOREGROUND with a timeout; perf in thread CPU or callgrind Ir + loadavg, never wall; kolt and
proposals READ-ONLY, kolt never copied into the vilan tree; model Opus, never Fable), PLUS Order 39's
six lessons as RULES:
- **Never rebuild while your own whole-crate run is in flight** — the run reads a binary you are
  replacing; the result is a red you cannot reproduce.
- **Any lane touching `node.rs` runs `-p vilan-core --test node_size`** in its gate list.
- **Any lane touching `vilan/docs` gates `markdown_golden` and the LSP's `book_sync`.**
- **A wall claimed on the native path is measured on the EXIT program** with the host census
  (`VILAN_NATIVE_HOST_CENSUS=1`) — and note F29: the census under-reports refused calls' arguments
  until native-b-40 fixes it; say which census you ran.
- **The integrator makes no edit in the integration worktree while a merge helper runs**; a lane's
  equivalent: no edit to a file a foreground gate is reading.
- **`pgrep -f "<pattern>"` in a wait loop matches the loop itself** — poll a log line, not a process.

## Lane hygiene-40 — DROPPABLE, lands FIRST: N119, N113, N114, N115, N116, N118, B376, B384, M85
1. **N119** — the check runs on a stack-sized worker thread with `catch_unwind`; a planted
   `unreachable!()` answers a diagnostic and the NEXT request still works; the B385 shape with the
   guard removed under a test flag does the same via the thread's `join` `Err`; vilan-ide's twin.
   2. **N113** — `()` refused by name pointing at `void`; `void` in the EBNF's literal production
   (grammar_sync); `let void = 3;` refused; the fourth edge (`[extern("document.activeElement")]`
   emits a call) goes to ui-40 as `__dom_active_element` — hygiene-40 pins the REFUSAL of a global
   property spelled as a call only if ui-40's helper has landed; otherwise stamp. 3. **N114** —
   retire `hover_at_cursor` (or make it refuse a fixture with `|`), re-derive E9's pin over
   `hover_at_marker`. **N115** — in-crate tests for vilan-ide's completion engine: ranking,
   filter-text, replace-span (E211's three). **N116** — the two wall-clock pins lose their wall half;
   the rule 'no assertion reads a clock' written at the suite's head. **N118** — `std_twin_parity`'s
   contract written at its head; private declarations excluded or the contract says why not.
   4. **B376** — a derive name std declares no macro for is refused BY NAME at the attribute
   (`STD_DERIVE_MACROS` vs the declared macros); one ledger row. **B384** — make B365's pin reach the
   arm from cold or delete the counter and say the arm is warm-path only. **M85** — MEASURE first
   (callgrind Ir per hover on a 20k-line workspace); build the offset→field index only if the scan
   shows. Sizing M. Owns vilan-lsp's server main + tests, vilan-ide tests, the two named test
   files, `std_twin_parity`, the derive-attribute check (one function — tell solver-40 which).

## Lane solver-40 — B377 (MISCOMPILE) first, B378 + B379 (A112 S3's blockers), B362 (thunk), B371, B372, B380, B381
1. **B377** — `(value in values => { note(1); value })` emits NOTHING: red pin from the item's repro
   (`sweeps/order39/probes/tuple_comprehension_block_dropped.vl`), then the block-element arm in the
   comprehension's emit; a golden if any moves. 2. **B378** — impl-selection ranks a SUBTRAIT bound
   above its supertrait bound (`impl type S: Narrow<T>` over `impl type S: Base<T>` when `trait
   Narrow<T> with Base<T>`); pins both spellings collections-39 was refused. **B379** — a generic
   parameter reachable only through a blanket impl's trait argument binds through a struct-returning
   constructor call; the item's control. REPORT when both land — collections-40 rebases A112's HELD
   S3 patch on your merge. 3. **B362 (RULED)** — thunk at the dispatched call site through the
   callee's recorded convention; un-ignore
   `b362_a_lazy_parameter_reached_through_a_bound_is_still_unsound` red-first; the mixed case.
   4. **B371** — the generic `switch` body's `internal: a call resolved to Source's requirement get`
   at emit: a trait requirement reached through an abstract `I: Source<U>` inside a blanket must
   dispatch, not inline; reactive-40 writes `switch` directly over `on_change` meanwhile and does
   NOT wait on you. **B372** — `Signal::new(m * 2)` in closure-return position keeps its callee's
   parameters; B162's receiverless resolution must still fix `T` from the argument. **B380** —
   indexing a `read()` temporary at a generic element type. **B381** — `T: PartialEq` lost inside a
   nested `match` arm within a closure. Sizing L. Owns analyzer.rs (impl selection, generic binding,
   lazy dispatch, bound tracking), transformer.rs (the comprehension emit), the B362 tests.

## Lane reactive-40 — A124 PAPER + S1 PROBE (no compiler change), A123 first
1. **A123** — `and_then` on `Source<Option<T>>` and `switch` on `Source<T>` as blankets over today's
   `Source`, written DIRECTLY over `on_change` (one derived cell each; the generic `map(f).flatten()`
   body hits B371); the item's pins (switch of inner, inner update, outer `None` detaches, re-follow,
   derivation-class under door 2 with a diamond, release at the owner's disposal); the `Option`
   `flatten`'s doc comment says what it is and points at `and_then`; the guide's derivations section.
   REPORT the two kolt sites' spellings (channel.vl:41 → `message.and_then(|m| m.author.user())`;
   model.vl `map_safe` retires) — kolt is the owner's. 2. **A124 the paper** —
   `proposal/reactive-pipeline.md` per the item's Deliverables (1): the five parts with the node
   structs written in vilan (`Map<S, U>`, `Switch<S, I>`, `Combine` over a tuple bound, `.cell()`),
   the push-pull protocol re-derived against reactive-turns.md §7 and door 2 (the diamond pin at
   `reactive_lifetimes.rs:1036` under no-payload notify + one id per leaf chain), the `Resource<T>`
   family (R5: pending → settled → pending again; `.or` and `.optional`; the reset-or-hold
   sub-question with a rec), the `dyn` scope as a DELTA to trait-objects.md (§4's census re-run for
   `Source` only; drop glue for a resource-free object) — coordinate with dyn-40 by SendMessage
   through the integrator so the two documents agree on the core, kolt's classification (the 74 maps
   into single-consumer / shared / stored; which of the 19 fields need `dyn`), the R4 migration, a
   cost table (per-read work of a cold chain vs today's eager cell; allocation per node; a `dyn` on
   the native backend = a fat pointer with a two-slot vtable in vilan-rt). The owner's sketch now
   names the root `Initial<T>` and keeps `Signal<T>` as the WRITABLE trait — the same split as
   today's `Signal`/`SignalCell`; the paper keeps those names unless it argues otherwise. 3. **S1
   the probe** — in std, over today's `Source`, no compiler change: the nodes as blankets (probe
   `sweeps/order39/probes/a124_h_blanket_adapter.vl` at std scale), `.cell()`, the no-payload
   `on_change` as a feature-flagged twin, run under the existing turn pins; MEASURE a 5-deep map chain
   read-per-frame against today's five cells (Ir); the item's pins (zero evaluations with no
   subscriber; twice for two leaf subs and once with a `.cell()` between; the diamond once with the
   settled pair). Nothing in S1 ships as the public surface — it is the paper's evidence, kept under
   `std/src/reactive_pipeline.vl` behind no export, or deleted at the report with its numbers kept.
   Sizing L. Owns reactive.vl (A123's two blanks at the END of the `Source` blankets), the new probe
   file, `proposal/reactive-pipeline.md`, reactive-turns.md's §7 cross-reference.

## Lane collections-40 — A125 (RULED, breaking), A112 S3 (after solver-40), A112 S2, the turns text
1. **A125** — `K: Hashable` on `reconcile` and `each`/`each_by`/`each_values` in BOTH ui twins;
   the reorder path uses the hash index; the 1,000-row reverse pinned linear in Ir; estate sweep
   (every `each` caller whose key is a struct without `Hashable` — kolt's two are the owner's to
   derive; say so in the report); BREAKING entry. 2. **A112 S3** — the HELD delta-driven `each`
   patch, rebased UNCHANGED on solver-40's B378/B379 merge (the integrator tells you when); if a third
   gap appears, file it and stop S3 — do not work around the solver. 3. **A112 S2** — `ListCell` and
   `map_each` per incremental-collections.md §13 (RULED), born with `usize` positions NOT yet (I5's
   S1 is Order 41's — write `i32` and a `// I5` marker at each position; the paper's census counts
   them). 4. **reactive-turns.md** gets FIND-3 + Q3 (inline cadence is order + door 1, not a
   contract; `at_settle` deferrals are effect-class by a held id) — text only. Sizing L. Owns
   delta.vl, `each*`/`reconcile` in both ui twins, rpc.vl's `KeyedCell`, reactive-turns.md.

## Lane dyn-40 — `dyn Trait` over an object-safe core (A124 R3, B4 reopened in scope); the bare-trait FIELD refused
1. **Census first** — every bare-trait struct field in the estate (B184's kolt census named
   `Searchable<T>` and `InputLayer<T>`; std's own; the `.vl` consts in Rust tests) — they are the
   BREAKING surface of the refusal; list them in the report with the `dyn` spelling each takes.
   2. **The token and the type** — `dyn Trait<..>` parses in type position (EBNF + grammar_sync;
   formatter prints it; the LSP paints it); object-safety is CHECKED at the spelling per
   trait-objects.md §4's three disqualifiers (no receiver, `Self` in a return, a generic member) —
   a non-object-safe trait is refused BY NAME with the disqualifying member named; a `dyn` may hold
   no resource (Q5: refused at the coercion with R10's wording). 3. **Coercion is EXPLICIT** — a
   value becomes a `dyn` only at a `dyn`-typed position (field, binding annotation, parameter,
   list element type); never implicitly between two concrete types (Q4, P15). 4. **Dispatch** — the
   vtable carries the trait's members as resolved by B57's winners (Q6, §9.1); JS: a two-field
   record `{ value, vtable }` or the value itself with a prototype — pick by measuring
   trait-objects.md §3.3's benchmark (erasure was 14–18 % slower for ALL dispatch; here only `dyn`
   values pay); native (vilan-rust/vilan-rt): a fat pointer with the vtable, F1's shape. 5. **The
   blanket** — `impl dyn Trait with Trait` so blankets over `S: Trait` (`map`, `flatten`, A123's
   two) apply to the object. 6. **The field refusal** — a bare `Trait` at a struct field is refused
   with a steer naming `dyn Trait` (one ledger row; B184's pins that admitted it flip to the
   refusal; its `resolve_hidden_struct_parameters` pre-pass stays for the OTHER positions or is
   retired if fields were its only customer — say which). 7. **Pins** — `dyn Source<i32>` field
   holding a root, a mapped cell and a `.cell()` in one `List<Holder>` (probe
   `a124_g_mixed_field.vl`'s refusal becomes a pass); `dyn` in a parameter and a binding; the
   non-object-safe refusal; the resource refusal; the explicit-only coercion; both backends
   byte-compared on a `dyn` program in the native differential. Sizing L; the riskiest lane —
   STOP-AND-REPORT if the dispatch design needs a choice the paper did not price. Owns the parser's
   type production, analyzer.rs's type-annotation admission + object-safety check + coercion, the
   emitters' `dyn` arms in transformer.rs and vilan-rust, vilan-rt's vtable type, the B184 pins.

## Lane native-a-40 — F18 slice 2: `std::json` natively → `Server::builder()`, `std::db` (the SEPARATE SQLite crate), the rpc server, kolt's server leg; F32
1. **`std::json` natively** — the reader/writer over `vilan-rt` (dependency-free; its own
   parser), the derive emitters' output reaching the Rust backend; exit: `Server::builder()` builds
   natively. 2. **`std::db`** — the crate `vilan-rt-sqlite` (rusqlite, bundled feature), linked
   ONLY when a program reaches `std::db` (R1 Order 39; AGENTS.md's stop condition on vilan-rt
   unchanged); the workspace's audit/clippy/windows gates cover it. 3. **The rpc server** — `std::rpc_server`
   natively over vilan-rt::http's upgrade handover (F18 slice 1's `IoSource`); the wire byte-identical
   to node (the keyed rpc pins run against a native server). 4. **THE EXIT** — kolt's server leg
   (`server.vl`, read-only; a copy of its SHAPE as a corpus program, never kolt itself) runs natively
   and answers a login over the socket; the whole-set table in native-apps.md §12 updated; the host
   census on the exit program. 5. **F32 (RULED b)** — `i128` natively; a literal past it refused
   at compile time (ledger row), overflow traps; the book's limit; the two programs flip or their
   refusal names the rule. Sizing L. Owns vilan-rust's json/db/rpc_server lowering, the new crate,
   vilan-rt's json module, native-apps.md §12's table.

## Lane native-b-40 — F30 (HIGH latent), F29, F31, F21, F22, F26 LAST; merged AFTER native-a-40
1. **F30** — a module-level `mut` aggregate mutated in place is a COPY natively: box the binding
   (the class native-a-39 fixed for locals) — pin `counts.push(x)` on a module-level `let mut`;
   estate census of mutated module bindings (all `Shared` today — the pin is the point). 2. **F29**
   — the host census walks a refused call's arguments and closure bodies; re-run on Order 39's exit
   program and report the corrected count against '55'. 3. **F31** — native liveness: last-use per
   binding, `move` instead of `clone` there; the four copies in Order 39's exit program go; Ir
   before/after. 4. **F21** — `returns_mut_view` through an enum payload (`Option<&mut T>`); the two
   programs refused by name flip. **F22** — adapted instances: monomorphise on asyncness as well as
   types for a closure-taking generic (async-polymorphism.md A.1); `adapt.vl` flips. 5. **F26 LAST**
   — the monomorphisation-resolution half shared between transformer.rs and vilan-rust as ONE module
   (it sits across both native lanes' files — which is why it is last and why you rebase on
   native-a-40's merge, by your resumed agent). Sizing L. Owns vilan-rust's binding/liveness/view
   lowering, the census, the shared module (after the rebase).

## Lane std-40 — B374 (HIGH), B375 (HIGH), B373, B383, N117, then A120 S1–S5 (RULED)
1. **B374** — `HttpTransport` answers `Err(reason)` on an unreachable host (the rejection is
   caught at the fetch); a pin against a closed port. **B375** — `[service]` over an `export impl`
   finds its members (the exported node shape); the empty contract hash `00001505` becomes a
   REFUSAL (a service with zero routes is an error) — ledger row. 2. **B373** — the scalar `from_json`
   entry points go through the poisoning reader (`i32::from_json("1.5")` → `Err`); **B383** —
   `open_request` closes the list and `RpcRequest.arity` is checked (the LONG list poisons like the
   short one); **N117** — the binary reader's kind-mismatch audit, the ten pin shapes. 3. **A120
   S1–S5** per transport-rpc.md §9.7 (S1 the decode/refusals; S2 `over_http(mount, codec)`; S3 the
   status table — 200 for everything the protocol decides, 401 typed envelope, 501 plain text; S4
   `authorize_request`; S5 the `[service(http)]` marker); the four refusals (`client = H` compiles
   clean today — the hole); the guide's CORS recipe. S4/S5 may slip to Order 41 — say so. Sizing L.
   Owns rpc.vl's transports + server, json.vl's scalar impls, binary.vl's reader, the service macro,
   transport-rpc.md's §9.7 'as built' note.

## Lane ui-40 — A121 (RULED): the DOM stub's four reads FIRST, then S1–S3
1. **The stub** — `Element::tab_index` (`[extern(get, "tabIndex")]`), `Element::parent`
   (`parentElement`), `Event::related_target`, and the two runtime helpers `__dom_active_element`
   + `__dom_computed_style` in transformer.rs's `EXTERN_HELPERS` + the interpreter's twin — and the
   DOM STUB (the test harness) grows `tabIndex`, `parentElement`, `getComputedStyle` so S1 is
   pinnable; N113's fourth edge (a global property spelled as a call) is the refusal you add
   beside the helper. 2. **S1** — the tabbable WALK + `FocusScope` with `Contain`/`Wrap` and the
   scope STACK in std (§3–§5); **S2** — `focus_initial` (the show calls it; `View::focus_scope`
   sugar on `autofocus`'s bounded clock) and `View::autofocus()` setting the attribute (a pin that
   markup moved); **S3** — `related_target` + the `focusout` path (deferred by the paper — build if
   S1/S2 land early). Kolt's `[x-autofocus]` and `panel_element.focus()` are the owner's to retire —
   the report names the lines. Sizing M. Owns std::dom (the three reads + helpers), std::ui's new
   focus module in both twins, the DOM stub.

## Lane editor-40 — F27 (R6 + R2), E213, E214, E216
1. **F27** — a user file that imports names existing in BOTH ui twins (kolt's
   `lib/conditional_value.vl` case): the diagnostic SAYS WHY the file was analysed as `process`
   (R6) and import-name inference (B36) uses member-name evidence — a `region.anchor` read picks the
   browser twin (R2); pins from the item. 2. **E213** — `[doc(internal)]`: hidden from completion,
   grayed (a `deprecated`-style tag) where it appears, hover says 'internal'; distinct from
   visibility; the attribute's grammar row; std applies it to its runtime seams as the paper names
   them (a first list in the report, not a sweep). 3. **E214** — grammar-scoped `<` auto-close
   (`autoClosingPairs` with `notIn` the operator scope) so VS Code's native overtype engages;
   E202's server placement retires where the grammar covers it; the fallback `type` command
   override only if the grammar scope cannot distinguish. 4. **E216** — the LSP and the playground
   read `[fmt] wrap_comments` + fmt-40's `comment_width` (the four-file `TABLES` set); the 'Reflow
   this comment' code action from the formatter's function (fmt-40 owns the function — you call
   it). Sizing M–L. Owns vilan-lsp (diagnostics wording, completion, code actions, manifest read),
   the VS Code grammar/package.json, vilan-playground's manifest read.

## Lane fmt-40 — E215 (RULED), E217; merged LAST
1. **E215** — the `comment_width` key (manifest schema, LSP `TABLES`, completion — the four
   files), default = the code width; a width other than 100 respected; std's `vilan.toml` opts in at
   84 (`wrap_comments = true`, `comment_width = 84`) and the reflow runs over std ONCE — the diff is
   the pin's size: report lines moved; the book's `[fmt]` section states the ten never-reflow
   classes and 'over-budget comments can remain'. 2. **E217** — a hand-wrapped generic `impl`
   header is PRINTED, not declined (one line if it fits, else one bound per line). Sizing S–M.
   Owns formatter.rs, the manifest schema, std's `vilan.toml`, the book's `[fmt]` section.

## Lane papers-40 — I5 (the `usize` paper), B382 (a recommendation), NO tree change
1. **I5** — `proposal/index-type.md`: the census the item owes (exact, by parse: every std
   signature position of index kind by module; every estate program naming an index type; every
   `-1` sentinel; every downward loop), the type's family in number.vl, literal inference under
   B370, the underflow rule as ruled (unspecified, never memory-unsafe; native differential cannot
   cover an underflowing program), the WIRE proof (a `Patch`/`Delta` frame byte-compared: width
   kept), the codemod + naming diagnostic + quick fix, slices S1–S4 sized, and the cut's dependency
   on S2. 2. **B382** — one page: a type alias (`type X = Y;`) — worth having or not; what
   `[deprecated]` on a re-export needs; rec for the owner. 3. Read-only otherwise; the probes under
   `sweeps/order40/papers-40/probes/`. Sizing M.

## Ownership map (conflict avoidance)
- reactive.vl: reactive-40 (A123's two blankets at the END of the `Source` blankets; the probe in a
  NEW file). delta.vl, `each*`/`reconcile` in both ui twins, rpc.vl `KeyedCell`: collections-40.
  rpc.vl transports/server, json.vl scalars, binary.vl reader, the service macro: std-40. std::dom +
  the new focus module in both ui twins + the DOM stub: ui-40. std's `vilan.toml`: fmt-40.
- analyzer.rs: solver-40 (impl selection, generic binding, lazy dispatch, bounds); dyn-40 (type
  annotation admission, object safety, coercion — a NEW module if it can be); hygiene-40 (the
  derive-name check, one function). parsing.rs: dyn-40 (`dyn`). transformer.rs: solver-40 (the
  comprehension emit); dyn-40 (the `dyn` arms); ui-40 (`EXTERN_HELPERS` rows only). formatter.rs:
  fmt-40 (dyn-40 hands `dyn`'s printing to it — say so in the report).
- vilan-rust: native-a-40 (json/db/rpc_server lowering, i128) / native-b-40 (bindings, liveness,
  views, F26 last) / dyn-40 (the `dyn` arm — one file, named in the report). vilan-rt: native-a-40
  json + the new sqlite crate / native-b-40 nothing / dyn-40 the vtable type.
- vilan-lsp: editor-40; hygiene-40 (server main's worker thread + tests only). vilan-ide: hygiene-40.
- Merge order: hygiene-40, editor-40, ui-40 (goldens), std-40 (goldens), solver-40, reactive-40,
  collections-40 (goldens; its S3 rebased after solver-40), dyn-40 (goldens; the BREAKING field
  refusal — estate re-sweep at the merge), native-a-40, native-b-40 (one rebase, by its resumed
  agent), fmt-40 LAST (the std reflow). papers-40 merges to proposals only. After EVERY merge that
  moved goldens: `scripts/integration/regen_goldens.sh` over the merged tree. Every gate list
  includes `native_differential`; `node_size` for node.rs lanes; `markdown_golden` + `book_sync` for
  docs lanes.

## At the sweep (integrator, proposals)
- Close per the reports; A124 stays OPEN (the paper's rulings → S2 the surface); A112 closes S3
  (S2 if landed); F18 stamped with the exit; B4's paper gets an 'as reopened' note; B184 a
  'withdrawn at fields' stamp.
- Kolt at the owner's word: A123's two sites; A125's two derives; A121's `[x-autofocus]` and the
  focus fallback; the bare-trait fields (`Searchable<T>`, `InputLayer<T>`) → `dyn`; nothing else.
- Order 41's queue: A124 S2 (the surface, per the paper's rulings) + R4's migration; I5 S1–S2 (the
  breaking train) → the v0.41.0 cut; A122 (std::tuple) after I5; A112 S2 if not landed; C14 S4/S5;
  A120 S4/S5 if slipped; B382 per its recommendation.
