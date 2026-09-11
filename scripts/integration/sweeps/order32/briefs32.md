# Order 32 — the kolt-findings order (drafted 2026-09-11; GO 2026-09-11, off vilan next @65af4be0)

**GO as adjusted (2026-09-11).** The owner filed three more items (B294, A86, E161) and said
"adjust order or go" without ruling P1–P5. Defaults taken: rpc-32 is DROPPED from this
order (P1–P3 are a BREAKING change to every handle stub and get an explicit ruling, not a
default); B287 is NOT built (P4 unruled — stays stated-unenforced, record-only); A71 IS
built (P5 — the owner's positional-slots ask is 'keep position' in substance). The
record-only list below is written as built at the sweep unless the owner objects. Six
lanes: solver-32, reactive-32 (+A86), wire-32, rpc-smalls-32, ui-32, smalls-32 (new: B294,
E161).

The owner's focus: kolt, dogfooding Order 31's seal, exposed three SOUNDNESS holes (B288,
B290, B273 — programs that must refuse compile), two reactive-core ROBUSTNESS defects (B291,
B292 — one late continuation or one throwing observer breaks the session), the Wire
predicate's syntactic gap (B289/A82), a Chrome per-tab trap std's `link` arms (B293), and
the remote-source paradigm question (kolt's `Task::remote_signal` hack, model.vl's `Memo`).
This order fixes everything that needs no ruling, and carries the ruled half if the owner
rules at GO.

## Rulings at GO (owner) — the ones that change what a lane BUILDS
- **P1 — the handle stub's shape (rpc-32 go/no-go).** Today `[rpc] fun get(id): SignalCell<T>`
  becomes an ASYNC stub `Result<RemoteSource<T>, RpcError>` (A74), so `.or()`/`.map()` are
  unreachable until the reply and every app writes the `remote_signal` bridge. Rec: the stub
  is SYNC and returns `RemoteSource<T>` directly, minted from `Origin` UNLEASED (the shipped
  re-mint path is the first mint); `Status` gains `Absent` (the `Option<SignalCell<T>>` form's
  `None` reply) and `Failed(RpcError)` (the next 0→1 lease retries). `.or(seed)` at the call
  site, no bridge. BREAKING for every handle stub (kolt migrates at the owner's word).
- **P2 — dedup.** Rec: (i) the SERVER dedups dynamic channels by source IDENTITY (two replies
  carrying one cell share one channel; the capability counts client leases and revokes at
  zero); (ii) the CLIENT does not auto-memo — a std `Memo<K: Hashable, V>` (kolt's
  `lib/memo.vl` is the exhibit) is the app's composition tool, one line per handle. Not (a)
  'pure/deduped stubs' — the owner did not love it, and a stub that silently returns a
  previous call's mirror is a cache the reader cannot see.
- **P3 — A79** (keyed RETURN `KeyedCell<K, T>` → `KeyedSource<K, T>`) in the SAME shape as P1,
  same lane. Rec: yes, it is the per-workspace tasks exhibit and the machinery exists.
- **P4 — B287.** Rec: REFUSE `async fun f(&mut self)` on an `[rpc]` method at expansion (one
  row) until the no-view-across-await rule lands. rpc-smalls-32 builds it if ruled.
- **P5 — A71.** Rec: KEEP POSITION (anchor + `insert_before`); ui-32 builds it as A85's brick.
- Record-only (the sweep writes these as ruled unless the owner objects): hop scope stays
  DYNAMIC-ONLY as built; the keyed per-key lease gets no hop; `client = H` same-module in v1;
  a void forward stub stays sync void; `__contract` on a client-only struct kept; bare
  `[expose]` over a `KeyedCell` IS the keyed channel; `reattach_mirrors`' `replay` parameter
  kept; `keyed_log_limit` fixed at 1024. B274 (copy at a `&mut self` receiver on a temporary
  read) stays queued — not this order.

## Mechanics (every lane)
- Worktree `vilan/.claude/worktrees/<lane>` branched from `origin/next` (65af4be0); push the
  branch; NEVER touch the main checkout; NEVER `git stash`; kill only PIDs you recorded,
  never by pattern; kolt (`~/code/kolt`) is READ-ONLY — read it for exhibits, copy nothing.
- One commit per item, message = the CHANGELOG entry's first sentence; CHANGELOG entry under
  the right family with its marker (`<!-- family: breaking|miscompile|fix|feature|
  performance|tooling|diagnostics -->`); the parity gate is `--test release_scripts`. A
  refusal that newly fires on a program std, `examples/` or kolt compiled yesterday carries
  a `breaking` note in the entry — say which program.
- Diagnostics: a new message is a ledger row written `NEW` in
  `crates/vilan-cli/tests/diagnostics-ledger.tsv` (the integrator numbers; next id 412) and
  a prose row is NOT yours; an EDITED message text is an edit to its row. Every lane that
  adds or edits a row runs `--test diagnostics_ledger`. A message whose FIRING changes means
  `-p vilan-lsp` too (quickfix/steer pins).
- PIN LOCATION (Order 31's rule): attribute and type refusals pin in vilan-core
  `tests/inference/main.rs`; wire behaviour in vilan-cli `service_layer.rs`; reactive
  lifetimes in `reactive_lifetimes.rs`, channels in `reactive_channels.rs`, rows/children in
  `ui_rows.rs`, routing in `router.rs`, timers in `debounce.rs`/`cancellation.rs`. Nothing in
  `vilan/test/` uses `[service]`, so `--test corpus` cannot catch a generator change —
  `--test examples` + `-p vilan-core --test docs` do.
- Shared test files: ADD whole new `fn`s only; never edit an existing fn or a shared const —
  if you must, say so in the report with the exact fn name.
- Tests: `cargo nextest run -p vilan-cli --test <name>` targeted, never plain `cargo test`;
  verify binary names with `ls crates/vilan-cli/tests/`. The whole `-p vilan-core` run is the
  merge gate, not yours, but `-p vilan-core -E 'test(every_std_module_is_clean_under_full_scan)'`
  IS yours (std edits). Building while nextest runs overwrites live test binaries — iterate
  with lib-only `cargo build`. Clippy `--all-targets -D warnings` and `cargo fmt --all
  --check` before every push; `vilan fmt` over any std file you touched.
- A parser rule statement added anywhere bumps `RULE_STATEMENT_SITES`.
- Scratch: `scratchpad/<lane>/` — the scratchpad is SHARED across sibling lanes; namespace
  by lane name and read nothing outside yours.
- Heredocs in their OWN shell call (a heredoc ends an `&&` chain). A hand-composed block of
  generated code is brace-counted and smoke-compiled (`--test examples`, 15 s) before the
  gates.
- No SendMessage in this build: a running lane cannot be steered, so every interaction is
  in this brief; a question you cannot answer from source becomes an OPEN Q in the report,
  and you build your recommendation.
- Perf claims: CPU time (`getrusage`) or callgrind Ir + loadavg, never wall.
- Report (final message): per item — commit sha, what landed, the pins (names), numbers;
  FINDS (pre-existing bugs, design gaps) as candidate items with evidence; OPEN Qs for the
  owner; anything you could not finish and why. Corrections to this brief are welcome and
  expected — say what was wrong.
- Model: Opus. The lane's own gate list is per lane below.

## Lane solver-32 — TOP: three soundness holes and two census items
Items: B288, B290 (probably one root — verify FIRST and say), B273, B275, B280.
Build:
1. B288 — a closure's declared/inferred return reaching a callee generic THROUGH A USER
   GENERIC STRUCT (`g: |T| Remote<U>`, `|T| Option<Remote<U>>`) neither binds `U` nor is
   checked. Sites: `resolve_closure_returns` (analyzer.rs:37075, `Constraint::ClosureReturns`
   pushed at :27012/:27052), `check_closure_rets_against_target` (:37168),
   `infer_closure_args_against_params` (:29119), `reconcile_type` (:31447). The descent that
   binds through `Option`/`List` must descend a user struct application the same way (the
   walk `reconcile_type` does for arguments). Pins (vilan-core `inference`): the infer face
   (`wrap([], |x| Remote { seed = [x] })` then `f[0] + 1` compiles), the refuse face
   (`let f: List<str> = wrap(..)` refused naming `Remote<List<i32>>`), and the generated-
   client shape in `service_layer` (a `[service]` with `get(id): Option<SignalCell<List<i53>>>`,
   a generic `remote_signal<U>(fallback, |T| Option<RemoteSource<U>>)` on `Task`, the wrong
   annotation `SignalCell<List<str>>` REFUSED — kolt's `channel.vl:13` shape at the sweep
   before this order). Probes: proposals scratch `kolt-markers/pa2`, `pa4` (nine variants).
2. B290 — `is Some(let x)` (and `match`) on an UNANNOTATED closure parameter types the
   payload as `Option`'s declared `T`, a free generic that then reconciles with ANYTHING.
   Sites: `Node::Is` walk (:25326) → `Constraint::Is` → `resolve_is` (:38683); the parameter's
   FILL lands through `infer_closure_args_against_params`. Type the pattern against the
   filled parameter type (defer the `Is` resolution while the parameter is unresolved, the
   way a closure return defers), for `is`, `match` legs and `for .. is`. Pins (`inference`):
   the refuse face (`inner.len()` over `SignalCell<Option<List<i32>>>::sub(|inner| ..)`
   compiles), the UNSOUND face (`cell.set(inner)` on a `SignalCell<str>` over a `List<i53>`
   payload REFUSED), a non-generic user callee typed `|Option<i32>| void`, `Ok(let v)`, a
   user enum, and a nested `SignalCell` payload. Probes: `kolt-markers/pa5` (thirteen
   variants). Annotating the parameter is the shipped workaround — the pin for the annotated
   form stays green (control).
3. B273 — an impl's `with` clause arguments are bound-checked and arity-checked by NOTHING
   (`impl CatBox with Holder<Cat>` with `Cat` lacking `Label`; `Holder<Cat, i32>` too).
   `check_written_nominal_bounds` (:5937, B251's shape) is the model — a third site at the
   impl clause; B188's arity check misses the position. Un-ignore
   `b262_an_impl_with_clauses_trait_argument_is_still_unchecked`. CENSUS: run the new check
   over std, `examples/`, `vilan/test/` and kolt (read-only) and report every impl it
   refuses BEFORE deciding the message — a std impl that fails is a std fix in the same lane.
   The tour page (data-and-traits.md) already asserts the check; leave it.
4. B275 — `satisfies_trait_bound` (:4900) drops trait ARGUMENTS on a SUPERTRAIT match:
   thread them (`instantiation_agrees`, impl_select.rs:412, B268's machinery); pin the
   refusal at the call site (`slot(signal_of_panel)` with only `Source<str> with Place`);
   the emission filter's never-empty fallback stays as an internal guard.
5. B280 — `freshen_list_element_slots` (:28704): guard the EXTERNAL-function path with
   `generic_is_enclosing_binder` (:4865) as B263 guarded the declared one; exhibit red
   first (an external `fun items(self): List<T>` on a bounded receiver erasing the caller's
   rigid `T`).
Ledger: a new refusal at the impl clause (B273) is probably a NEW row unless B251's row
reads right there — say which; B275's refusal reuses the bound-refusal row if the text
fits. Gates: `-p vilan-core --test inference --test infer_differential --test docs`;
`-p vilan-cli --test corpus --test service_layer --test examples --test release_scripts
--test diagnostics_ledger`; `-p vilan-lsp` (firing changes). Family: fix (with `breaking`
notes for any census hit).

## Lane reactive-32 — ambient capture outliving its extent, and exception safety
Items: B291, B292, B283, B277, and A86 (the owner's flatten ask — last, droppable). One
family for the four: something captured at creation (an owner, a turn, a nursery) is
resolved after its extent ended.
Build:
1. B291 — `Owner` (reactive.vl:347–380) has no disposed state. Add `disposed: Shared<bool>`;
   `take`/`defer` on a disposed owner run the cleanup NOW (the item is disposed on the spot);
   `dispose` idempotent. Then the mirror case: a `RemoteSource` lease taken from a
   continuation after its owner died (kolt's channel switch before the first reply) must
   not stay subscribed — measure both shapes (Subscribe+Unsubscribe in one segment vs
   `acquire` on a disposed ambient owner minting nothing) and build the cheaper one that
   keeps `get()` honest. `register_with_owner` (:427) and the boundaries (`bind_each`,
   `swap`, `when`) are unchanged — their pins are the control. Pins (`reactive_lifetimes.rs`):
   an `effect` registered from a continuation after `owner.dispose()` never fires; a second
   `dispose` is a no-op; (`reactive_channels.rs`) the late mirror lease leaves the server's
   `live` at 0. Probe: `kolt-markers/pa7`. Optional: a dev-build assertion naming the late
   registration site.
2. B292 — `drain` (reactive.vl:138–157) is not exception-safe: a throw inside
   `(subscriber.notify)()` unwinds past `draining_turns.pop()` and `draining = false`, and
   the turn stays draining forever (every later `set`/`at_settle` that resolves to it
   enqueues and never flushes). vilan has no exception syntax, so find the runtime's catch
   seam — grep std for an `external fun` over a JS `try`/`finally` (the `queue_microtask`
   extern at :59 is the model for adding one: `external fun with_finally(body: || void,
   after: || void)` or a `guarded(body): Option<str>` that returns the error text). The wave
   loop restores `draining`/`draining_turns` on ANY exit and RETHROWS after the restore (or
   reports through the host console with the subscriber's origin and continues — say which
   and why; rethrow is the honest default). Same guard around `Owner::dispose`'s cleanup
   loop (a throwing cleanup leaves the rest undisposed). Pins (`reactive_lifetimes.rs`): an
   observer that panics once; a later `set` on another signal captured under the same turn
   still reaches its observers; the panic surfaced to the test. Budget: measure the guard's
   cost on the drain hot path (Ir on the reactive benchmark) — sub-1% or a profile diff.
3. B283 — `RemoteSource::release` (rpc.vl:3081) reaches `at_settle` (reactive.vl:184) from
   the subscription's RELEASE HOOK, which resolves the turn captured AT CREATION: a lease
   taken outside a turn and disposed-and-rebuilt INSIDE one gets no same-turn cancellation
   (`same-turn:up=2 down=1`). Two shapes: change `at_settle`'s resolution for everyone
   (ambient-at-release: the draining turn, else the ambient one — a turn-model change, spec
   §8.4's context rule says captured-at-creation), or make the mirror's release hook read
   the turn at release. Build the mirror's (the narrow one) unless the spec argument for the
   wide one is clean — write it either way. Pin (`reactive_channels.rs`): outside-in lease,
   dispose+rebuild in one turn → 0 frames; the four A25 markdown pins (vilan-core `inference
   markdown::a25_*`) and the same-turn hop pin are the control.
4. B277 — `Debounce::run` (time.vl:363–396) drives its loop in an `async` block under the
   ambient nursery; a nursery cancellation unwinds it with `running` still true and the
   value is INERT after. Find how a cancelled task unwinds (`cancellation.rs`,
   `owned_nursery.rs` pins; `Timer::wait` returns false on `cancel`) and reset `running` on
   the cancellation path — or state the scope rule (a debounce lives in the nursery that
   made it) and make `run` after cancellation refuse loudly. Pin (`debounce.rs`): cancel the
   nursery mid-window, then `run` — fires.
5. A86 — `flatten` (reactive.vl:890) is inherent on `SignalCell<SignalCell<U>>`; make it a
   BLANKET over the trait: `impl Source<type I: Source<type U>> { fun flatten(self):
   SignalCell<U> }` (the bare-trait impl subject compiles at 65af4be0 — the owner's probe
   `impl Source<Option<type _: Source<type U>>>` is the head) with the shipped body, plus
   the `Option` form `impl Source<Option<type I: Source<type U>>> { fun flatten(self):
   SignalCell<Option<U>> }`; the cell-only impl goes (the A4 pins are the control). PROBE
   FIRST against `SignalCell<SignalCell<i32>>`, a `map` result and
   `SignalCell<Option<SignalCell<i32>>>` — if impl selection cannot see through the nested
   bound (B268's machinery, B275's gap), report it as an OPEN Q for solver-32 and leave the
   inherent impl. Census: `RemoteSource::or` (rpc.vl:2943) and `KeyedSource::or` (:3636)
   are one `impl Source<Option<type T>> { fun or(self, initial: T): SignalCell<T> }` in
   reactive.vl — build it ONLY if the two mirrors' `Source<Option<..>>` impls select it
   cleanly (their channel pins are the control; rpc.vl lines 2937–2960 and 3630–3650 are
   yours for the deletion, nothing else in rpc.vl); `status()`, `of(key)`, `update` (A32),
   `Draft`, `Selector`, `Optimistic` stay — say why for each you judged. Pins beside the A4
   pins; docs: std/reactive.md's `flatten` paragraph.
Gates: `-p vilan-cli --test reactive_lifetimes --test reactive_channels --test debounce
--test cancellation --test owned_nursery --test corpus --test release_scripts`; the std
full-scan; `-p vilan-core --test inference --test docs` (the A25 markdown pins). Family:
fix; feature (A86).

## Lane wire-32 — B289 then A82, two commits, one lane (they must move together)
Build:
1. B289 — the Wire predicate is a SYNTACTIC ALLOWLIST. Sites: `is_wire_type` (analyzer.rs:6338,
   over a `&Node`, pre-resolution), `resolved_type_is_wire` (:15170), the derive all-fields
   check (:6364–6410), the `[rpc]` signature refusal (:14865/:14886), the `[expose]` element
   check inside `check_expose_fields` (:14928, text at :14970), the handle element-Wire
   refusal (row 411). One predicate: a resolved type is Wire when an `impl .. with Wire`
   applies to it (`impl_select::subject_applies`, :174), recursing into arguments only where
   the impl's own bounds demand it (`impl Result<type T: Wire, type E: Wire>` binds both;
   `impl Handle<type T>` binds none — C7's phantom rule expressed by the impl); the allowlist
   stays as the fast path for the primitives. For the PRE-RESOLUTION sites say which can be
   moved to resolution time and which cannot; a site that must stay syntactic admits a NAME
   that has an `impl .. with Wire` anywhere in the program — a name-keyed scan, refusal-only
   in direction (B254/B258's hazard: never promote by name). The refusal texts name `Map`
   (A39 admitted it) — row EDITS, not new rows. Pins (`inference`): a user
   `impl Result<T, E> with Wire` admits `[rpc] fun f(self): Result<i53, str>`; refuses
   `Result<Opaque, str>` naming the argument; the derive-field and expose faces; the text
   names `Map`. Probe: `kolt-markers/probe_b.vl`.
2. A82 — wire.vl: `impl Result<type T: Wire, type E: Wire> with Wire` beside `Option`'s
   (:362; variant-tagged `Ok`/`Err`, hash-stable — kolt's `store.vl:27` is the exhibit, read
   it, retype it); `impl u53 with Wire` in the scalar row (:277–327) and the small scalars
   the language actually has (check numeric-types.md — do not invent a type); the analyzer's
   allowlist and the refusal text in the SAME commit as the impl. Pins: a `[rpc] fun
   f(self): Result<i53, str>` round trip in `service_layer`; the contract hash of a
   handle-free service is UNMOVED by a new impl (78bdada7, frozen in handles-31's pin —
   it is the control). Docs: the Wire table (find it: `docs/std/rpc.md` or wherever
   `std::wire` is documented — `git grep 'derive(Wire)' vilan/docs`).
Gates: `-p vilan-core --test inference --test docs`; `-p vilan-cli --test service_layer
--test rpc_http --test corpus --test examples --test release_scripts --test
diagnostics_ledger`; the std full-scan; `-p vilan-lsp`. Family: fix (B289), feature (A82),
diagnostics (the text edits).

## Lane rpc-smalls-32 — four smalls, a fifth if P4 rules refuse
Items: B282, B284, B285, A78, (B287).
Build:
1. B282 — `route_block` (rpc.vl:4214) emits `|request| { .. let request: str = arg(request,
   0); .. }` (the statement at :4560), so an `[rpc]` parameter named `request` shadows the
   closure's. Gensym the closure parameter (`__request`) and thread it into `arg(..)` and
   `decode_failed(..)`; pin a `request`-named parameter in `service_layer`. `route_block` is
   rpc-32's territory too if that lane goes — touch only the parameter name.
2. B284 — `[expose]` on a `[client_service]`-ONLY struct is a silent no-op (compiles, hashes,
   never mints; the comment region at rpc.vl:4645 says as much). Refuse at the attribute in
   the field's vocabulary — the analyzer knows the struct's `ServiceAttr { server_side,
   client_side }`; put the arm at the TOP of `check_expose_fields` (:14928) as its own early
   `if` (wire-32 edits strings inside the same fn — stay out of its lines). Ledger NEW row;
   must-fail pin in `inference`; the peer struct (both attributes) with an `[expose]` stays
   admitted (control).
3. B285 — `[expose(keyed = K2)]` over a `KeyedCell<K, T>` with `K2 ≠ K` is silently ignored
   (the `service` macro's exposed-field loop, rpc.vl:4312–4390, prefers the type). Refuse at
   the attribute, span on the argument, row 407's shape (`Exposure::Keyed` carries the
   spanned key) — its row with a `KeyedCell` label or a sibling row; control pin for the
   agreeing form.
4. A78 — a handle-returning service on the CONNECTIONLESS leg fails at RUNTIME
   (`RpcError::Remote("..arrived on none..")`). Rec: refuse at mount — `Service::at`
   (process/rpc_server.vl:555) / `Service::new` (:479) sees the surface string, which
   carries `->RemoteSource<` for a handle method; a mount with no socket leg panics with a
   curated message naming the method (a RUNTIME message: no ledger row, but the text follows
   diagnostics-standard.md); plus one line in the guide's status table. Pin in `rpc_http`:
   the POST-only mount of a handle service refuses at startup, not at the first call.
5. B287 (if P4 = refuse) — `async` + `&mut self` on an `[rpc]` method REFUSED at expansion
   (the `service` macro :4262 sees receiver and asyncness; row 408's `mut self` refusal is
   the model), ledger NEW row, must-fail pin; the guide caveat in guide/services.md ("What
   the turn model owes you here") becomes "refused, until the no-view-across-await rule".
Gates: `-p vilan-core --test inference --test docs`; `-p vilan-cli --test service_layer
--test rpc_http --test examples --test corpus --test release_scripts --test
diagnostics_ledger`; the std full-scan; `-p vilan-lsp`. Family: fix, diagnostics.

## Lane ui-32 — B293, A83, A71 (as A85's brick), and the A85 paper
Build:
1. B293 — `link` (browser/router.vl:261) sets `draggable="false"` on the anchor it builds
   (the href stays: middle-click, ctrl-click, copy-link keep native behaviour; only the drag
   arming goes). guide/routing.md's `link` paragraph (:205) gains one sentence; the
   hand-written `<a href on:click>` idiom wherever the guide shows it gains the attribute;
   appendix/gotchas.md gets the browser note (the mechanism: a link drag that starts while a
   quick click's in-app navigation is settling wedges the TAB's drag-and-drop in Chrome —
   per tab, survives a hard refresh; kolt's `views.vl` comment is the record). Pin
   (`router.rs`): the built anchor carries the attribute. `View::link_to(route)` only if it
   is a three-line chain; otherwise say so and skip.
2. A83 — `Vec2 { x: f64, y: f64 }` in `std/math.vl` with `add`/`sub`/`scale`/`length`/
   `distance`/`dot` and `Add`/`Sub` operator impls (a named type reads at a call site where a
   tuple does not); a `vilan/test/` corpus program; the docs row. kolt's `interact.vl:127`
   (`magnitude`) is the exhibit — read-only, no migration.
3. A71 (P5 = keep position) — THE ANCHOR PRIMITIVE, built as A85's brick: `dom.vl` gains
   `create_comment(text)` (or reuses `create_text_node("")`, :34 — say which and why) and
   `Element::insert_before(child, anchor)` (`append` at :158 is the model); a `Region`
   helper in `browser/ui.vl` (an anchor node placed at `place`/call time, `live` content
   inserted BEFORE it, cleared on dispose via the ambient owner's `defer` — `bind_each`'s
   own shape at :342). The `Source<View>` (:1007) and `Source<List<View>>` (:1032) arms take
   a region; `when` (:540), `swap` (:592) and `bind_each` (:342, with `_values` :421 and
   `_by` :452) create their region at CALL time (the call sits at the child's position in
   the chain, so 'append the anchor now, insert before it later' keeps position) — their
   method form and signatures are UNCHANGED this order. Process twin (`process/ui.vl`
   :379–430): the region renders its content in place, the anchor renders as nothing.
   Remove the 'put it last' sentences. Pins (`ui_rows.rs`): a middle `{signal}` child
   replaced twice keeps its position; `when` between two static siblings toggled off/on
   lands between them; `bind_each` rows between a header and a footer stay between them
   after insert/remove/reorder; `ssr_differential` green. Measure: the `bind_each` 1,000-row
   benchmark before/after (Ir) — an anchor per region must not move it.
4. A85 PAPER (no build): deliver `scratchpad/ui-32/positional-slots.md` (the integrator
   commits it to proposals as `proposal/positional-slots.md`): the value forms
   (`when(..): Conditional<S>`, `swap(..): Swap<T, S>`, `each(..): Each<T, K, S>` + the A42
   siblings) as structs with `impl .. with Slot` whose `place` creates the region and runs
   the method's body; the parent methods as one-line sugar (no breaking change); the
   fragment interplay (A46's literal is `List<View>`; a `Source<List<View>>` of fragments
   keeps position via the region; the 'component returns multiple roots' form IS a region
   value — price it); the SSR twin; ownership (unchanged); B253's spelling cost — a helper
   returning a positional slot names the concrete type (`fun account(): Conditional<
   SignalCell<bool>>`) because a bare trait in return position is refused by ruling — with
   a read-only CENSUS of kolt: every helper that would return one, and every wrapper element
   whose only job is to hold a position (count both). End with the ruling the owner is asked
   for (the surface) and the sizing (S/M/L) of the build.
Gates: `-p vilan-cli --test ui_rows --test router --test ssr_differential --test
ssr_fullstack --test benchmarks --test corpus --test release_scripts`; `-p vilan-core
--test docs --test markdown_golden`; the std full-scan. Family: fix (B293, A71), feature
(A83).

## Lane rpc-32 — NOT IN THIS ORDER (P1–P3 unruled at GO; kept here as the brief for the next order)
Items: A-sync-handles (the integrator files it at GO from P1/P2), A79 (P3).
Build, under the recommended shape:
1. `Status` (rpc.vl:2748) gains `Absent` and `Failed(RpcError)`; `status()` (:2959) reports
   them; `RemoteSource`'s `Source<Option<T>>` impl (:2856) is unchanged (`None` while
   Waiting/Absent/Failed — `or(seed)` :2943 is the app's fallback, reachable at the call
   site now).
2. A NEVER-MINTED mirror: built from `Origin` (:2784) with `released = true` (:2833) and no
   channel — the shipped re-mint path (`acquire` :3016 → `remint` :3035 → `rebind` :3148)
   IS the first mint, so an unleased handle costs nothing (R3's demand-decides, kept). The
   `Option<SignalCell<T>>` written form maps to `RemoteSource<T>` whose `None` reply sets
   `Absent` (no channel; `get()` stays `None`); an `Err` reply sets `Failed(e)` and the next
   0→1 lease retries. Say what a lease during an in-flight mint does (it joins; one call).
3. Generator: the stub's handle arm (`service` macro :4262; `handle_element` :4247; the
   `else` arm handles-31 built) renders SYNC — `fun get(self, id: i53): RemoteSource<T>` —
   and constructs the unleased mirror with its `Origin`; the surface renders the mapped type
   (`Option<RemoteSource<T>>` → `RemoteSource<T>` MOVES the Option form's hash; the plain
   form's 78bdada7/da79e00b pins say whether the plain form moved — it must not). The
   `reactive: ReactiveClient` field rule is unchanged.
4. Server dedup by source identity (P2 i): `expose_dynamic` (:1764) keys the capability by
   the cell's identity (`SignalCell` :600 — verify it carries an `id`; else stamp one with
   `fresh_id` at construction, reactive.vl:26); a second reply carrying the same cell reuses
   the channel; `Capability` counts client leases (Subscribe +1, Unsubscribe −1) and
   `release_demand` revokes at ZERO, never under another mirror. Pin: two replies of one
   cell → one channel; the first mirror's release past the hop leaves the channel live for
   the second; the last release revokes.
5. std `Memo<K: Hashable, V>` (P2 ii): `new()`, `get_or(key, make: || V): V`, `forget(key)`;
   the maker runs at the CALL SITE (context reads stay covered — kolt's `lib/memo.vl` is the
   exhibit, read-only); home `std::collections` (or beside `Shared` — pick, justify); docs.
6. A79 — `handle_element` grows the `KeyedCell<K, T>` spelling; `reply_source_keyed` over
   `expose_keyed_cell` (:1859) marked dynamic; the keyed mirror gets the same unleased
   `Origin` path (keyed-31's `acquire` :3697 / `rebind` :3920); no per-key hop (record
   ruling). Pin: the per-workspace tasks shape (`tasks_in(workspace): KeyedCell<i32, Task>`)
   round trip, element-grained.
7. Docs: the rpc guide's handle section rewritten for the sync stub (`.or()` at the call
   site; `status()`'s four arms; the Memo idiom); `vilan/examples/rpc`'s `Session::note`
   updated. Paper corrections for transport-rpc.md §9.2/§9.6 and remote-sources.md §2d in
   the report (the integrator applies them).
Pins (`reactive_channels.rs`/`service_layer.rs`): sync stub + `.or()`; Waiting→Ready on the
first lease; Absent; Failed then retry on the next lease; the in-flight join; dedup (4);
Memo; A79; the hash pins. Gates: handles-31's list + `--test examples` + `-p vilan-core
--test docs`. Family: feature; BREAKING (every handle stub's type — the entry names it).

## Lane smalls-32 — B294 (`_` as the anonymous type binder) + E161 (the generic-head highlighting)
Build:
1. B294 — `parse_type_atom` (parsing.rs:4430) routes only the `type` keyword to
   `parse_type_binder` (:4495, `type NAME (: A + B)?` → `Node::TypeBinder`). Add the arm: an
   `_` identifier in type position, optionally `: bounds`, produces the SAME node — one
   analyzer path, no new semantics (`impl Source<Option<_: Source<type U>>>` is the owner's
   exhibit; `impl Source<Option<type _: Source<type U>>>` compiles today, `_:` is a parse
   error at the `:`). CHECK FIRST and pin either way: `impl Pair<type _, type _>` — are two
   anonymous binders ONE parameter named `_` today (an aliasing bug the wildcard must not
   inherit) or fresh each? The wildcard must be fresh each time. A named binder keeps its
   keyword; `type _` stays accepted and `vilan fmt` canonicalises to `_` (formatter pin;
   E150's rules apply). A bare `_` outside an impl head (`let x: List<_>`, an inference
   placeholder) is OUT OF SCOPE — its refusal text should now say what `_` is for (one
   curated row, `diagnostics_ledger`). Estate: spec/grammar.md:249 and spec/types.md:318
   gain the spelling; `grammar_ebnf` and `grammar_sync` green (no new keyword — `_` is an
   identifier; if the EBNF grows a production, the sync test tells you). Pins (vilan-core
   `inference` for the type faces, `parse_expr_regression`/the parser tests for the
   grammar): the exhibit; two-wildcards-fresh; `type _` still accepted; the placeholder
   refusal text.
2. E161 — the TextMate grammar (`editors/vscode/syntaxes/vilan.tmLanguage.json`) mis-scopes
   a nested generic head: `type` is in the declaration-keyword list (`storage.type.vilan`,
   :303), `<type` matches the ELEMENT rule (:388 — a lowercase word glued to `<` is a tag),
   the other brackets are the operator fallback (:380), a line-leading `>` is E115's
   terminator rule. Fix: (a) a begin/end generic-argument-list rule (`(?<=[A-Za-z0-9_])<` …
   `>`, `meta.generic.vilan`, delimiters `punctuation.definition.generic.begin/end.vilan`,
   nesting by including itself — `>>>` closes three); (b) the binder rule inside it
   (`\b(type)\b(?=\s+[A-Za-z_])` → `keyword.other.type-binder.vilan` or
   `storage.modifier.vilan` — pick what the shipped themes colour as a KEYWORD, name the
   themes checked); (c) the element rule requires the `<` not to follow an identifier
   character (`(?<![A-Za-z0-9_])`) — element-syntax S2's atom-position rule, the grammar
   catching up; (d) the E115 terminator scoped only where a generic did not consume the
   `>` (the begin/end from (a) spans lines). Third place: `vilan/docs/theme/vilan.js` —
   check the book's highlighter on the same head. SEMANTIC LAYER: vilan-lsp emits semantic
   tokens (main.rs:251 `encode_semantic_tokens`, E2's classes) and in VS Code they override
   TextMate where they classify — establish which layer painted each of the owner's three
   observations (`vilan.semanticTokens.enabled` off in a scratch VS Code settings file is
   not available to you headlessly, so read the classifier: if it classifies `type`
   binders or brackets, fix it there or leave the spans unclassified). Pins: `grammar_sync`
   green (regenerate ONLY if a generated fragment moved, and say so); a NEW node-driven
   scope test beside it that tokenises the exhibit with `vscode-textmate` (grammar_sync
   already reads the grammar under node — copy its harness; if `vscode-textmate` is not in
   the extension's `package-lock.json`, that is a new dependency: STOP and report, and
   assert on the regexes instead) — every bracket in the head carries the generic
   delimiter scope and none the tag or operator scope; `type` the binder scope; `<div>`
   still a tag and `a < b` still an operator (controls).
Gates: `-p vilan-core --test inference --test parse_expr_regression --test docs`;
`-p vilan-cli --test grammar_ebnf --test grammar_sync --test vscode_extension --test
corpus --test release_scripts --test diagnostics_ledger`; `-p vilan-lsp` if the
classifier moved; `cargo fmt`/clippy; `vilan fmt --check` over `vilan/test/`. Family:
feature (B294), tooling (E161), diagnostics (the placeholder row).

## Ownership map (conflict avoidance)
- analyzer.rs: solver-32 owns the closure/pattern/impl-bound sites (:4865–5937, :25326,
  :28704, :29119, :31447, :37075–37260, :38683); wire-32 owns :6300–6410, :14865–14890,
  :15170–15200 and the STRINGS inside `check_expose_fields` (:14928–14970); rpc-smalls-32
  adds one early arm at the top of `check_expose_fields` (B284) and the keyed arm (B285) —
  nothing else in that fn.
- rpc.vl: rpc-smalls-32 owns `route_block` (:4214, the parameter name only), the exposed-
  field loop (:4312–4390) and the client-only region (:4645); rpc-32 owns `expose_dynamic`
  (:1764), `Status`/`RemoteSource` (:2748–3160), `handle_element` (:4247) and the stub's
  handle arm. Separate regions; the integrator resolves.
- reactive.vl, time.vl: reactive-32 only (rpc-32 touches no `at_settle`; B283's mirror-side
  fix lives in rpc.vl:3081–3095 — reactive-32 owns those lines, rpc-32 stays out).
- wire.vl: wire-32. browser/ui.vl, process/ui.vl, browser/dom.vl, browser/router.vl,
  math.vl: ui-32. process/rpc_server.vl: rpc-smalls-32 (A78). rpc.vl:2937–2960 and
  3630–3650 (the two `or` bodies) are reactive-32's for A86's deletion only.
- parsing.rs (`parse_type_atom`/`parse_type_binder`), formatter.rs, spec/grammar.md,
  spec/types.md, `editors/vscode/syntaxes/`, `vilan/docs/theme/vilan.js`: smalls-32.
  solver-32 touches no parser file; smalls-32 touches no analyzer type-check site (the
  placeholder refusal text lives where 'cannot find type' is raised — one string).
- Landing order (integrator): smalls-32 → ui-32 → reactive-32 → wire-32 → rpc-smalls-32 →
  solver-32 (the largest, last). Docs-touching merges
  regenerate the mdBook golden (merge_lane does it). After any two lanes add a FIELD and a
  CONSTRUCTION SITE to one std struct, grep every `Name {` post-merge (keyed-31's lesson).

## At the sweep (integrator, proposals)
- Close: B288 B290 B273 B275 B280 · B291 B292 B283 B277 A86 · B289 A82 · B282 B284 B285
  A78 · B293 A83 A71 · B294 E161. Not this order: B287 (P4 unruled), the sync-handles item
  and A79 (P1–P3 unruled — rpc-32's brief stands for the next order). A85: the paper
  committed to proposals (`proposal/positional-slots.md`), the ruling requested.
- Paper: transport-rpc.md §9.6 as-built amendment and remote-sources.md §2d (if rpc-32);
  the Order 31 record-only rulings written down; B253's ruling cited from A85.
- Kolt follow-ups AT THE OWNER'S WORD (nothing in this order touches kolt): delete
  `store.vl:27`'s Result impl and its FIXME (A82); `lib/remote_signal.vl` and model.vl's
  memos go if rpc-32 went (`Memo` → std's); the B288/B290 annotations and their FIXMEs go;
  `views.vl`'s draggable comment shortens to 'see std' (B293); `interact.vl`'s `magnitude`
  → `Vec2` (A83). The migration to A59/A60/B268/A62 is still owed.
- The cut (HELD since Order 29): the owner tests kolt on the seal — reinstall BOTH `vilan`
  and `vilan-lsp` from the integration tip — then the changelog train ships.
