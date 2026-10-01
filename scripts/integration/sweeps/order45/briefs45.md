# Order 45 — AFTER THE PIPE TRAIN: three miscompiles and the value-semantics holes the train exposed, the pipe model's solver and native debts, the model's follow-ups (static `untrack`, lazy nursery and tracker, `identity()`), reactive maps and sets and the `Store` if ruled, the hover arc, and an LSP latency baseline on kolt (drafted 2026-10-01, off vilan next @6e6830df; GO 2026-10-01, every ask as recommended)

**Base.** Order 44 sealed at 3ca733f3 on 2026-09-30; v0.42.0 was cut at that seal (tag 61d15612, release
run 36760569845 green 17/17) and FOLDED: `origin/main` = `origin/next` = 6e6830df. Nothing has landed
since. `## Unreleased` does not exist on next (0 entries). Toolchain `vilan 0.42.0 (6e6830dfc)` in both
locations, and the 0.42.0 extension in the local VS Code server. Ledger max **603** (lanes write `NEW`).
Tracker **144 open**: 139 after Order 44's sweep, plus five filed 2026-10-01 (E236–E239, B485). Shared
census 180. Copy-elision census 578.

Kolt is on 0.42.0 as of 2026-10-01 (the owner's commit, plus the store's three sealed views, uncommitted):
`vilan check` 0 errors and 0 warnings, build clean, server smoke 200. Its browser runtime is unverified.

**The shape.** Not a train. Order 44 changed the reactive model and found more than it fixed: 40 items
were filed against 34 closed. This order pays that down. Four things set the order of work:

1. **Three miscompiles go first, and two more beside them.**
   - **B473**: through a subtrait bound, a supertrait's default runs even when the type overrides it
     (both backends; predates A142; re-created A132's leak until reactive-44 routed around it).
   - **B483**: `Shared::new(x)` aliases the caller's value on JS; `ListCell::of(xs)` then `push`
     mutates `xs`.
   - **B466**: `*view` of an aggregate does not copy on JS.
   - Beside them: **B465** (a shared view into a closure reads the place pair) and **B474** (`sub`
     through a bound emits `RemoteSource`'s inherent `sub`).

   B483, B466 and B465 are one family: a value position that should copy and does not.
2. **The pipe model's debts are what make it awkward today.** `count.derive(Some)` does not compile
   (B478); a mixed-arm selector needs its type arguments written (B480); a pipe over a `dyn Source`
   throws at run time (B475); `std::ui` keeps a duplicate `Source` arm beside every `Flow` arm because a
   blanket's bound goes unchecked (B476, B477). These land in solver-b-45 so reactive-45 can remove the
   workarounds.
3. **Native has refused the same shape three times.** Reading or writing a field through a `Shared`
   view (F62) made A142's `OwnerCell` and S6's `TrackRuns` whole-value writes. native-45 fixes it,
   with the rest of the order's native finds.
4. **Two builds wait on rulings** (R-a, R-b): reactive maps and sets
   (`proposal/reactive-maps-sets.md`), where kolt's per-key shape ran 1,000,000 projections in 30.5 s
   against a toy `MapCell`'s 1,000 in 1 ms, and the `Store` (`proposal/store.md`). Each is a lane only
   if its paper is ruled at GO.

Around those: the hover arc the owner ruled on 2026-10-01 (E235, E237, E238, E239 as one change), the
LSP latency baseline on kolt (E236), and two papers (B485 keywords vs attributes; B460's opaque
returns).

**Seven lanes plus papers; nine if both papers are ruled.** Merge order:

1. solver-a-45 (the miscompiles; sha to LANE-STATUS.md as each lands);
2. solver-b-45 (rebased onto solver-a-45);
3. native-45;
4. reactive-45 (rebased onto solver-b-45: it removes workarounds those fixes make unnecessary);
5. maps-45, if R-b is ruled (rebased onto reactive-45);
6. store-45, if R-a is ruled (rebased onto maps-45: store S3 needs the keyed nodes);
7. syntax-45;
8. editor-45 (last).

papers-45 merges to proposals only. A cut is proposed at the seal (R-h).

## Asked at GO (the owner)

- **R-a: `proposal/store.md`, Q1–Q12.** All as recommended:
  - Q1 the macro door first (`[derive(Storable)]`); compiler generation only on a measured need;
  - Q2 the tree layout;
  - Q3 opt-in by derive (vilan has no private fields);
  - Q4 `[reactive(coarse)]` as a field attribute;
  - Q5 `Store::new` only;
  - Q6 a handle through a variant or `Option` is `Source<Option<P>>` plus `patch`;
  - Q7 a store write always compares;
  - Q8 `Store<T>` for the root and every projection;
  - Q9 the derive refuses a field named like a handle member;
  - Q10 the name `Storable`;
  - Q11 no `at(index)` on a list field (`by_key` instead);
  - Q12 slots counted per subscription.

  If ruled, store-45 builds S1 + S2 (S3 needs maps-45's keyed nodes and follows in the same lane if
  maps-45 merges in time). Rec: **rule and build S1 + S2**. B465 and B466 are its prerequisites and
  land first.
- **R-b: `proposal/reactive-maps-sets.md`, Q1–Q7 and Q9** (Q8 is ruled and built). All as
  recommended:
  - Q1 `MapCell`/`SetCell`;
  - Q2 `KeyedCell` re-founded on `MapCell`, its surface and wire bytes kept;
  - Q3 `SetCell` its own type;
  - Q4 key slots counted per subscription;
  - Q5 `at(k)` is a `MapEntry<K, V>` handle;
  - Q6 `Reset` wakes every live key slot;
  - Q7 insertion order is the `HashMap`/`HashSet` contract, `SortedMap`/`SortedSet` take a comparator
    value, door (a) declined;
  - Q9 `clear()` records one `Reset`.

  If ruled, maps-45 builds S0 + S1 + S2 (S3, the `KeyedCell` re-founding, if time). Rec: **rule and
  build**. Kolt's `GlobalStore` is the customer.
- **R-c: the copy family (B483, B466, B465).** One rule: a value taken out of a place the binding does
  not own is copied. That covers `*view`, a view passed where a value is read, and an argument a
  constructor stores.
  - `Shared::new`, `ListCell::of` and every std constructor that STORES its argument take `own`.
  - The JS emitter copies an `own` argument at a non-last use, as native does.
  - A closure's view parameter is a view: reading it into a `T` place without `*` is refused, as for
    a `fun`.

  Rec: **yes**.
- **R-d: F60, an unconsumed pipe.** `outer.flatten();` as a statement runs on JS and is refused
  natively. Door (a): the pipe node types are `[must_use]`, so a dropped pipe WARNS on both backends,
  and native binds the dropped node's parameters so it still builds. Door (b): refuse it on both
  backends. Rec: **(a)**. A dropped value is not an error anywhere else in the language.
- **R-e: B468, a defaulted struct type parameter.** Door (a): apply the default wherever the argument
  is omitted. Door (b): refuse a default on a struct parameter until (a) is built. Rec: **(a)**.
- **R-f: A144, the contract hash.** Hash the RESOLVED type (aliases expanded), so `Map<..>` and
  `HashMap<..>` hash the same. This moves every service's hash once. Rec: **yes**, in this order,
  before the deprecated aliases are removed.
- **R-g: B482 builds** (ruled 2026-09-30, door (a)): an injected closure called inside `clear` of its
  own context gets the cleared state, and the base callback positions take `context tracking`. It is
  BREAKING for a callback VALUE typed without the clause. Rec: **build now**, in solver-b-45 and
  reactive-45.
- **R-h: the cut at the seal.** v0.43.0 if any entry is breaking (B482 and A144 are), otherwise
  v0.42.1 from a `release/0.42` branch. Rec: **v0.43.0 at the seal**.
- **R-i: E236 is a seal-time REPORT first**, and a gate with a budget once the numbers hold steady
  over two orders. Rec: **report**.
- **R-j: B485 (keywords vs attributes) and B460's opaque returns are PAPERS** this order, with nothing
  built. Rec: **papers**.
- **R-k: `.transient()` joins A130's module-binding refusal**, with a `transient_global()` twin for a
  program-lifetime transient. Rec: **yes**, in reactive-45.
- **R-l: the old names.** `Map`/`Set` stay deprecated for this release as ruled (one release). They
  are removed in v0.44.0, not now. Rec: **hold**.
- **R-m: carried, not in this order:** M60, A87/A111, A131, B183's concrete arm, the `self::` paths,
  store S5 (compiler-generated nodes), maps S4/S5. Rec: **carry**.

## Mechanics (every lane)

briefs44.md's "Mechanics" stands in full (and, through it, briefs43's and briefs42's): worktrees
`vilan/.claude/worktrees/<lane>-45` off `origin/next` @6e6830df and never the main checkout; the item's
text is a HYPOTHESIS; pins red first; one commit per item with its CHANGELOG entry; ledger rows written
`NEW`; `LANE-STATUS.md` untracked; native differential in both modes and `check_scope_differential` in
every std gate; tracker writes through `file_items.py` / `stamp_items.py` / `close_batch.py`; the PATH
export; **model Opus, never Fable**. Added to them, Order 44's lessons as RULES:

- **Kill by PID, never by pattern.** Two lanes ran `pkill -f` in Order 44 and each took another
  lane's test run. Record the PID when you start a long run.
- **A lane that adds an arm, or locals, to `walk_expr_node_inner` re-measures the walk** and reports
  it: `VILAN_DEPTH_STATS=1 vilan check` over the 13/33/103-level `.trim()` chains; expr-walk is
  **26,376 B/level** at the base. An arm with real locals goes in its own `#[inline(never)]` method
  (the doc comment on `walk_expr_node_inner` says so). Order 44 grew the frame past Windows's 2 MiB
  canary and found out at the seal.
- **Every CHANGELOG entry carries its `<!-- family: … -->` marker.** The merge helper stops on a
  missing one.
- **A lane that cannot write its REPORT file sends the text as its final message.** The tool
  environment refused report files for five lanes; the integrator saves them under
  `sweeps/order45/`.
- **A lane that rebases re-runs its FULL gates on the rebased tip**, and says which base its numbers
  are from.
- **Pins written against today's std spellings are re-read after a rebase onto a lane that renames
  them.** Four pins from one lane broke at another's merge in Order 44.
- **The seal runs CI's wasm leg and the stack canary's margin.** `ci-local.sh wasm` joins `seal.sh`,
  and `deep_nesting` is also run on a 1.5 MiB thread. Both were CI-only finds in Order 44. This is the
  integrator's step, written into `seal.sh` before the seal.
- **The paper is the spec.** A lane that finds a ruling unbuildable STOPS that item and messages the
  integrator with the ruling's number.

## Lane solver-a-45: the miscompiles and the copy family. B473 FIRST, then B483 + B466 + B465 (R-c), B474, B453, B444, B464, B467

1. **B473.** Dispatch through a subtrait bound resolves a supertrait's member against the receiver's
   IMPL: the override first, the default second.
   - Un-ignore `traits::a_supertrait_defaults_override_is_dispatched_through_a_subtrait_bound`.
   - Both backends.
   - Put the sha in LANE-STATUS.md at once: reactive-45 removes `map_each`'s routing-around.
2. **B483 + B466 + B465** per R-c, as one rule with three sites.
   - Pins: mutate through the cell and read the original; mutate a `*view` copy and read the caller's
     value; a snapshot taken with `Some(*v)` survives an in-place write; a shared view into a `|c|`
     closure reads the element. Both backends.
   - The std half (`own` on the storing constructors) is yours in shared.vl and delta.vl.
   - The `copy_elision_census` moves are classified.
3. **B474.** The emitter's mono dispatch honours "through a bound, the trait answers" (B408's rule at
   emission). Un-ignore the `markdown.rs` pin. Natively it surfaces as rustc E0308.
4. **B453.** A `&mut` view of a tuple position writes through on JS.
5. **B444.** Interpolating a `&T` view prints the element.
6. **B464.** A closure's `&mut` parameter called with a bare place takes the `fun` path's rule
   (refused, with the steer to `&mut place`).
7. **B467.** The view-escape rule answers the same at every nesting depth (with B439: a `&mut`
   PARAMETER of a closure type is not a capture).

Sizing L. Owns analyzer.rs, mono.rs, transformer.rs (JS emit) for these items; shared.vl and
delta.vl's constructor signatures.

## Lane solver-b-45: the pipe model's solver debts. REBASES onto solver-a-45's merge. B475, B476 + B477, B478, B480 + B484, B479, B482 (R-g), B468 (R-e), B481, B455's remainder, B472, B454, B471's control pin

1. **B475.** A `dyn Source<T>`'s method table carries its supertrait's members (`Flow::start` and the
   rest), so a pipe over a source object runs. Un-ignore the three `dyn_objects` pins and
   collections-44's per-element `dyn Source` pin. Both backends; the native table is native-45's if it
   differs.
2. **B476 + B477.** A blanket impl's element bound is checked at candidate selection.
   - A bare total-join `flatten()` is refused, with the steer to `switch(|inner| inner)`.
   - The two `flatten`s resolve by which bound holds, in both declaration orders. If both hold,
     refuse as ambiguous.
   - transient-44's two `.transient()` arms must keep working: specificity, not refusal, picks
     between `Task<Result<T, E>>` and `Task<T>`.
3. **B478.** A named function AND an enum variant coerce at a `context`-typed closure parameter.
   Un-ignore `callable::b462_a_source_derivation_takes_the_variant` (`count.derive(Some)`).
4. **B480 + B484.** A generic bound through a trait argument binds from the argument: `switch`'s `U`
   through a `dyn Flow<i32>`, and `IntoFlow<Option<U>>` through a flow. Pin the mixed-arm selector
   WITHOUT written type arguments.
5. **B479.** A pipe stage's closure parameter in a generic body is typed with the impl's binders
   substituted. Un-ignore the `traits.rs` pin.
6. **B482** per R-g, the context pass's half: a call inside `clear` of context C reads C as cleared
   (a strict `get` in the callee's literal is refused; `get_safe` answers `None`). reactive-45 changes
   the std callback signatures on top of it.
7. **B468** per R-e.
8. **B481.** Reproduce first (a `for` whose `next` is an inherited default behind a declined block),
   then route the loop's `next` through the admission refusal.
9. **B455's remainder:** the "admissible by its trait name" spelling.
10. **B472.** The import steer indexes an exported alias import (`Map` → "did you mean `HashMap`").
11. **B454.** The argument constructor's own error parameter in `ok.and(Ok(5))`.
12. **B471's control pin:** a user type's `.css` miss stays the ordinary error.

Sizing L. Owns analyzer.rs, impl_select.rs, mono.rs, the context pass, AFTER solver-a-45's merge
(rebase, never cherry-pick).

## Lane native-45: F62 FIRST, then F57, F60 (R-d), F61, F63, F64, F52, F54, F55, M91; the censuses

1. **F62.** A field read or write through a `Shared` view emits as a scoped borrow, with the
   right-hand side hoisted into a temporary when it reads the same cell.
   - Pins: read, write, and the read-modify-write line of `vilan/test/shared.vl`. Both backends.
   - Tell reactive-45 when it lands: `OwnerCell` and `TrackRuns` may go back to field writes.
2. **F57.** `crypto.vl`'s moved `salt` (rustc E0382 at the base). Add a native pin set for the
   platform-bound programs the sweep can build.
3. **F60** per R-d: the native half binds a dropped pipe's parameters. The `[must_use]` attributes
   are reactive-45's.
4. **F61.** One order for an injected closure's hidden parameters, at the literal and at the closure
   type. Drop std's ordering comment.
5. **F63.** An indexed read of a non-Copy element clones.
6. **F64.** An `Option<|| V>` field in a generic struct.
7. **F52, F54, F55:** the three carried from Order 43.
8. **M91.** The native `HashMap`/`HashSet` compact tombstones past half-full, preserving insertion
   order. Pin: churn, then walk, in bounded time, with the order equal to JS's. If maps-45 runs, this
   is its S0 and moves there; say which lane took it.
9. The native copy census regenerated over the tip, and the leak census re-run at 0 live everywhere.

Sizing M–L. Owns vilan-rust, vilan-rt, the native tests and censuses.

## Lane reactive-45: the model's follow-ups. REBASES onto solver-b-45's merge. J7 + M92, M93, A146, B482's std half (R-g), F60's `[must_use]` (R-d), A144 (R-f), R-k, and the workarounds removed

1. **J7 + M92.** A spawn under a `context ambient_nursery` closure registers with the injected
   nursery; a run's nursery is created on its first spawn.
   - Un-ignore `a142_s2_a_cancelled_runs_task_is_owned_and_reports_nothing`.
   - Extend the `quiet`/`busy` pin: a task-free run allocates nothing.
   - The JS "unhandled task error … AbortError" on cancelling a detached nursery goes away
     (native-44's divergence).
2. **M93.** The `Tracker` is allocated on the first `track()`. Pin: an untracked body allocates
   nothing.
3. **A146.** `Source::identity()` for `RemoteSource`, `KeyedSource`, `KeyedCell` and `ListCell`. Pin:
   a tracked mirror read attaches once across runs.
4. **B482's std half**, after solver-b-45's context-pass change: `on_change`, `effect_on_change` and
   the UI event handlers take `context tracking` and call under `tracking.clear(..)`. Pins: a
   `track()` in a callback literal is a compile error; a callback's `get_safe` sees `None`. BREAKING
   for a callback value typed without the clause; the kolt patch, if any site exists, goes in the
   report.
5. **F60's `[must_use]`** per R-d on every pipe node, on `TrackedDerive` and on the collection pipes.
   Pin the warning.
6. **A144** per R-f: the contract hash reads the resolved type. Every `[service]` hash pin moves
   once; classify them.
7. **R-k:** `.transient()` in A130's module-binding refusal (row 575), and `transient_global()`.
8. **Workarounds removed as their fixes merge:**
   - `std::ui`'s duplicate `Source` arms beside the `Flow` arms (B476);
   - any `map_each` routing left after native-44's F58 (B473);
   - `OwnerCell`/`TrackRuns` back to field writes if F62 has merged (optional; say what you did).
9. **A135's tail warning** names the seal it found (`.memo()` or `.cell()`); it is hard-coded to
   `.cell()` today (transient-44's cosmetic find).

Sizing M. Owns reactive.vl, transient.vl, tracking's section, `std::ui`'s binding arms, rpc.vl's
contract hash and `identity()` lines, task.vl's nursery registration.

## Lane maps-45 (if R-b is ruled): `proposal/reactive-maps-sets.md` S0 + S1 + S2. REBASES onto reactive-45

1. **S0.** A differential pin for remove-then-re-insert; M91's compaction if native-45 did not take
   it.
2. **S1.** `MapCell`/`SetCell` with the writes and reads of §3; the `MapSource`/`MapSignal`/
   `SetSource`/`SetSignal` faces; the `DeltaSource` impls over `DeltaLog<MapOp>`/`DeltaLog<SetOp>`;
   `at(k)` (a `MapEntry<K, V>` that depends on that key only) and `contains`; per-key slots counted
   per subscription; `Reset` waking every live key slot; `reconcile_to` waking only changed keys;
   `clear()` as one `Reset`.
3. **S2.** The operators of §5 except `group_by`, as collection pipes (A142 §6): `keys`,
   `values`/`entries` with the Fenwick rank, `map_values`, `filter`, the counter folds.
4. **S3 if time:** `KeyedCell` re-founded on `MapCell`, A54's pins byte-identical.
5. **The kolt exhibit** as a patch the owner applies: `GlobalStore.channels` and `.messages` as
   `MapCell`s, with `get_channel`/`get_message` returning `at(id)` in place of the three sealed views
   kolt keeps today.

Pins per the paper, both backends. Sizing L. Owns a new `map_cell.vl`/`set_cell.vl`, delta.vl's map
and set operators, hash_map.vl/hash_set.vl's reads.

## Lane store-45 (if R-a is ruled): `proposal/store.md` S1 + S2. REBASES onto maps-45 (or reactive-45 if maps-45 is not ruled)

1. **S1.** `Storable` with the two leaf tiers; `Node`; `Store<T>` as `Source` + `Signal` (a lens: a
   root plus a path; a projection's `set` writes back through the root); the struct derive
   `[derive(Storable)]`; whole-value writes that diff and wake only the changed spine; lazily
   allocated slots counted per subscription; `[reactive(coarse)]`; the derive's refusal of a field
   named like a handle member. The read path lends in place: the paper measured 1,124–1,491 ms for
   2,000 leaf reads on a 1,000-key root when a read copies up through each level, against 1 ms lent.
   It needs B465 and B466 from solver-a-45.
2. **S2.** Enums: the discriminant projection; through-variant handles as `Source<Option<P>>` plus
   `patch`; same-variant writes patching the payload; the UI helper that rebuilds only on the
   discriminant.
3. **S3 if maps-45 has merged:** map, set and list fields as keyed and sequence nodes.

Pins per the paper's prototype, both backends where native allows; say where it does not. Sizing L.
Owns a new `store.vl` and the derive in macro_std.

## Lane syntax-45: B445, B446, the B485 census support

1. **B445.** `[platform("browser")]` before `export impl` parses, or is refused with the steer to
   the working order. Pick per papers-45's B485 draft if it has landed its ordering section;
   otherwise accept both orders.
2. **B446.** A parameter named `own` after a generic-typed one reports at the right token.
3. The marker census B485's paper needs: every keyword and attribute, the positions each is accepted
   at, generated from the parser's tables rather than hand-listed. Hand it to papers-45.

Sizing S. Owns lexing.rs, parsing.rs, formatter.rs, grammar.md and the EBNF.

## Lane editor-45: the hover arc (E235 + E237 + E238 + E239, RULED), E236 (R-i), E234, B436 + B437. LAST to merge

1. **The hover arc, one change:**
   - **E238** (ruled door (b)): a method's hover shows the `impl` header on its own line above the
     `fun` line — `impl Memo<K: Hashable, V>`, `impl Memo<K, V> with Source<V>`,
     `impl type S: Source<type T>`, or `trait Flow<T>` for a default. Completion's detail line takes
     the same header.
   - **E235:** the signature printer prints the receiver's `own`.
   - **E239:** `self` hovers as a binding: `self: <subject>` with the receiver convention; the bound
     inside a blanket or a trait default.
   - **E237** (ruled): under a variable's or field's `name: Type` line, the type's definition — one
     level deep, about 12 members then `…`, generic arguments substituted, std types by the same
     rule, a trait-typed or `dyn` value showing the trait's required members.
2. **E236** per R-i: a harness that speaks LSP over stdio to the installed `vilan-lsp` and replays a
   fixed edit script over a scratch COPY of kolt at a pinned commit.
   - The edits: a keystroke in a leaf file; one in `shared.vl`; one in a file holding css; an edit
     that breaks and then repairs the parse.
   - The table: per edit, time-to-diagnostics, hover/completion/inlay latency, CPU time and peak
     memory, against E121's <10 ms and <500 ms. CPU time, not wall.
   - Also: callgrind's top offenders for the slowest edit, and the script committed under `scripts/`
     so the seal can run it.
3. **E234.** bindgen emits a reserved word unescaped at a member position; `examples/canvas`'s
   bindings regenerated and classified.
4. **B436 + B437:** `print` of a `dyn` value prints the value; the JS `type_key` gains a `Dyn` arm.
   These are emitter rows next to the printer the hover arc touches; coordinate with solver-a-45 if
   transformer.rs conflicts.

Sizing M. Owns vilan-lsp, vilan-ide, editors/vscode, bindgen, `scripts/` (the harness).

## Lane papers-45: B485, B460's opaque returns; NO tree change

1. **B485, keywords vs attributes.** From syntax-45's census: what each marker changes (typing,
   ownership class, visibility and linkage, tooling only, code generation); a candidate RULE; the
   misfits in each direction with the migration cost of each move; one ORDER for stacked markers
   (B445). Doors and recs per misfit.
2. **B460's opacity.** The opaque type kind for `fun f(): Trait`: what hiding the callee's type costs
   in inference, dispatch and both emitters; trait-method returns as associated opaque types; whether
   door (i)'s "checked, not hidden" should stay the default with opacity opt-in. Probes on 0.42.0.

Merges to proposals only.

## Ownership map (conflict avoidance)

- **analyzer.rs, mono.rs, transformer.rs, impl_select.rs, the context pass:** solver-a-45, then
  solver-b-45 rebased onto it. editor-45's printer rows and syntax-45's parser rows land after both.
- **vilan-rust, vilan-rt:** native-45.
- **reactive.vl, transient.vl, the tracking section, `std::ui` arms, task.vl, rpc.vl's hash and
  identity lines:** reactive-45. shared.vl's and delta.vl's constructor signatures are solver-a-45's
  (R-c), merged first.
- **delta.vl's map and set operators, the new cell files:** maps-45. **store.vl, the derive:**
  store-45.
- **lexing.rs, parsing.rs, formatter.rs, grammar:** syntax-45.
- **vilan-lsp, vilan-ide, editors/vscode, bindgen, the harness script:** editor-45.
- **Merge order:** solver-a-45, solver-b-45 (rebased), native-45, reactive-45 (rebased), maps-45
  (rebased), store-45 (rebased), syntax-45, editor-45 (rebased). papers-45 to proposals.
- **After every merge that moved goldens:** `regen_goldens.sh`, the copy census regenerated over the
  merged tree, the merge helper's BUILD step.
- **After the seal and CI green:** the cut (R-h), the fold, the toolchain in both locations and the
  vsix, the website re-checked against the new compiler.

## At the sweep (integrator, proposals)

- Close per the reports. A142 closes when store-45 lands S1 (S7's build), or stays open with it
  queued.
- `seal.sh` gains the wasm leg and the 1.5 MiB canary BEFORE the seal (the Mechanics rule).
- `diagnostics-ledger.md` prose for every `NEW` row and re-key, at each merge, not at the end.
- Kolt at the owner's word: the store's three sealed views (uncommitted since 2026-10-01); B482's
  callback clause if any site exists; maps-45's `GlobalStore` patch; `count.derive(Some)` works after
  B478.
- Order 46's queue: maps S3–S5 and store S3–S6 as their lanes leave them; B485's and B460's rulings
  and builds; E236 as a gate if the numbers hold; removing the deprecated `Map`/`Set` aliases at
  v0.44.0; M60, A87/A111, A131.
