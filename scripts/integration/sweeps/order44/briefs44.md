# Order 44 — THE PIPE TRAIN: A142's reactive layers (sources and move-only pipes, per-run owners, transient sources, per-shape collection operators, tracked reads), the language items the owner's sketch needs (B458–B463), the collections rename that rides the same breaking release (I9), and the mirror bugs in the files the train rewrites (drafted 2026-09-29, off vilan next @07e8db37; GO 2026-09-29)

**GO 2026-09-29.** The owner: "Regarding R-k, I'd be fine constraining it even further by making `.{WHITESPACE}{NAME}` illegal (only `.{NAME}` is legal). Or, at the very least, no new line characters between the `.` and `{NAME}`. Go with all recs." R-a–R-j and R-l–R-m stand as recommended. **R-k is RULED STRICTER**: a member name follows `.` with no whitespace at all, for every member (not only keyword members). syntax-44 first counts the estate's `.`-whitespace-name uses; if it finds a legitimate one, it falls back to the owner's minimum (no newline between `.` and the name) and reports the uses. **Step 0 was run by the integrator at GO**, on `--backend rust` over Appendix A's prototype (0.41.1): the native backend refuses EVERY `[resource]` type ("destruction.md's teardown is a later slice"), so every pipe node fails natively. The move refusal is the analyzer's and reads the same on both backends. That is **F56, filed at GO**: emit a Drop-less resource as an ordinary type. It is native-44's item 0, FIRST, and reactive-44 cherry-picks it for its native gates. reactive-44 therefore starts at GO and does not wait for a message. A second step-0 find is recorded, not filed: a value typed `dyn Up<T>` cannot be sealed (`memo` lives on `Pipe`). That is R34 as ruled: a selector returns `dyn Flow` to be *started*, never sealed.

**Base.** Order 43 sealed at 07e8db37 on 2026-09-28 (CI 36501668642 green 11/11), and nothing has landed
on next since. `origin/main` = 1a33340f (the v0.41.1 fold). `## Unreleased` carries **44 entries, none
breaking**. Toolchain `vilan 0.41.1 (07e8db37)` in both locations, plus the extension from the sealed tip
(E229 door d). Ledger max **590** (next id 591; lanes write `NEW` and the merge helper renumbers). Tracker
**133 open**: 126 after Order 43's sweep, plus seven filed 2026-09-29 (A142, B458–B463). Shared-census
literal 146. `release/0.41` is KEPT until v0.42.0 ships (releases.md §7.3 step 5).

Kolt is RED on the new compiler until the owner applies B419's patch
(`sweeps/order43/solver-43/finds/kolt-b419.patch`) and A122's `divorce` edit (channel.vl:26). Its tree
also carries the owner's uncommitted search system and `lib/reactive2.vl`: the A142 sketch, which is a
design file rather than a build input.

**The design.** `proposal/reactive-layers.md` (A142), RATIFIED 2026-09-29 as R1–R37 with no question
open; proposals @714a652. Every lane in this order reads it first. The model in one paragraph:

- A **`Source`** has state and `get()`.
- A transformation (`derive`, the renamed `map`; `switch`; `switch_some`; `distinct_by`; …) returns a
  **`Pipe`**. A pipe is a move-only description (`[resource]` nodes, `own self` everywhere), consumed
  exactly once:
  - by sealing: `.memo()`, `.cell()`, the `_global` twins, `.sample()`, `.transient()`;
  - or by a consumer: `effect`, a UI binding.
- **`Flow`** is anything a pipeline starts from.
- Because a pipe has exactly one consumer, every body in it runs once per change of its input. So every
  body gets a lazily allocated per-run owner, can start tasks (cancelled with the run), and can call
  `.track()`.
- Collections have one change vocabulary per shape, and their operators follow whatever flow a closure
  returns (`IntoFlow`).
- Tracked reads (`.track()`, `Context::clear` as untrack) and `Store` are sugar layers.

Appendix A of the paper is the 0.41.1 prototype. It is the reference for what the language already
enforces (a second consumer is "use of `p` after it was moved") and what it does not (B463).

**The shape.** A train. It is BREAKING:

- `Source.map` → `derive`;
- derived values are pipes, so `.get()` on an unsealed derivation is refused;
- `.cell()` exists only on pipes;
- `effect`/`scoped_effect` merge;
- I9's `Map`/`Set` → `HashMap`/`HashSet` rides the same release.

The seal proposes the v0.42.0 cut (R-b). Three things set the order of work:

1. **B463 is the train's soundness floor.** A trait default whose receiver is the loan `self` can move a
   resource `Self` into an aggregate. Every combinator is a trait default over a `[resource]` node, so
   solver-44 lands B463 FIRST. Until it lands, reactive-44 writes every combinator and sealing operation
   `own self`; the prototype confirms that closes the gap.
2. **Native has never run a `[resource]` node, and step 0 at GO confirmed it cannot.** The `rust`
   backend refuses every resource type. native-44 lands **F56** FIRST (emit a Drop-less resource as an
   ordinary type), and every pipe-touching lane cherry-picks it for native gates until native-44
   merges.
3. **The train rewrites the files the open mirror bugs live in.** A141 (`.cell()` on a shared store
   dies with the first connection), A139 and A140 land in transient-44 before S3 rebuilds
   `RemoteSource` on `TransientSource`.

Around the train:

- the language items from the owner's sketch: B458 `Context::clear`, B459 `then`/`else` plus the guard,
  B461 nested bare traits, B462 variants as closures, B460 if ruled;
- the chronicle's openers that live in files these lanes own (B452 and B456 FIRST in solver; E230–E233;
  F53);
- E227's inlay-hint build, now load-bearing, because pipe types are long node chains;
- papers-44: A142 S7 (the `Store` paper) and A138/I10 (reactive maps/sets and ordering).

**Nine lanes, plus papers.** Merge order:

1. solver-44 (B463 first);
2. native-44;
3. reactive-44 (S1+S2);
4. transient-44 (rebased onto reactive-44);
5. collections-44 (rebased);
6. tracking-44 (rebased onto reactive-44 AND solver-44's B458);
7. syntax-44 (rebased; B459's binding rule lands in analyzer rows after solver-44);
8. editor-44 (last: E227's attributes go on the node types reactive-44 names).

papers-44 merges to proposals only. After the seal and CI green: the v0.42.0 cut (R-b); `release/0.41`
deleted at the cut; toolchain in both locations and the vsix.

## Asked at GO (the owner)

- **R-a: B460, a bare trait in return position** (it reopens B253's 2026-09-07 refusal). Door (a) is an
  OPAQUE return for free functions and inherent methods: one callee-chosen type, statically
  dispatched, with the refusal's steer pointing at `dyn` when branches disagree. Trait-method returns
  come later, after a paper.
  - Under R29 this is the pipe model's `impl Iterator`: a model method that builds a pipe
    (`fun open_channel(self): Pipe<Channel>`) otherwise spells its whole node chain, or pays `dyn`.
  - Rec: **(a)**, built in solver-44 after B463. If it is not ruled, pipes return `dyn` and the paper
    stands.
- **R-b: the v0.42.0 cut at the seal.**
  - A142 S1 and I9 are breaking. `## Unreleased` also carries 44 non-breaking entries from Order 43.
  - The cut deletes `release/0.41` (§7.3 step 5).
  - Kolt migrates at the owner's word, from the lanes' patch files (R-l).
  - Rec: **cut**.
- **R-c: I9 rides the train.**
  - `std::hash_map::HashMap` / `std::hash_set::HashSet`, one module per type; the old names stay one
    release as `[deprecated]` aliases; the estate codemod covers std, examples, kolt (as a patch), the
    website and the playground.
  - I9's rec kept the reactive node named `Map`. A142's R1 renames the node (`derive` → a `Derive`
    node), so the collision ends from both sides.
  - Rec: **yes**. I8's maps half (`HashMap::get_or_insert`) rides with it.
- **R-d: E227 builds** with `proposal/inlay-hint-abbreviation.md`'s recommendations:
  - the marker is `~T`;
  - nested nodes abbreviate;
  - admission is per instantiation, at render time;
  - `vilan.inlayHints.abbreviate` is on by default;
  - hover shows both forms.

  The pipe nodes carry `[hint(Pipe<T>)]`, and the sealed faces carry `[hint(Source<T>)]`. Rec: **yes**.
- **R-e: B457, copy policy across a call.** Door (a): copy when the call can REACH an in-place write of
  that cell (a write summary per callee). Rec: **(a)**.
- **R-f: A141.**
  - Door (b): a `Service::new` handler runs under the SERVICE's owner, and a `Service::factory` handler
    under the connection's.
  - Door (a)'s warning also applies: a `.cell()` (now `.memo()`) stored through `get_or_insert` or
    `Shared::write` in a handler.
  - Kolt's `get_user` (store.vl:160) is the customer.
  - Rec: **(b) plus the warning**.
- **R-g: A133.** Door (c): document the in-process seed as inline and close. Door (a) broke 15
  `reactive_channels` pins and the documented contract. Rec: **(c)**.
- **R-h: B401, the admission restructure.** Compute impl admission after the import and type drains,
  before the fixpoint, and filter both the inherited-default and the declared-member candidates. Rec:
  **go**.
- **R-i: B428.** Withdraw the documented `128i8` looseness, now that B407 reads the negation. The fix
  is already written; two looseness pins flip, and numeric-types.md §3 and std/numbers.md change.
  Rec: **withdraw**.
- **R-j: E224.** Door (b): one rule for types and functions — "an import line alone does not warn; the
  USE warns"; deprecation.md's line 87 corrected. Rec: **(b)**.
- **R-k: B414 S4, the member tier.** A keyword used as a member after `.` stays on the dot's own line
  (otherwise a half-typed `foo.` swallows the next statement's keyword). B416 landed in Order 43.
  Rec: **yes**, built in syntax-44.
- **R-l: kolt.**
  - The train breaks kolt twice: the pipe split (`.map` → `.derive`, derived fields → `.memo()`,
    `.get()` on derivations → a seal or `.sample()`) and I9.
  - reactive-44 and collections-44 each deliver a patch
    (`sweeps/order44/<lane>/kolt-<lane>.patch`) built and checked over a scratch copy of kolt at its
    current tip PLUS the owed B419 patch and `divorce` edit. They never write kolt.
  - The owner applies them at their word, after the owed Order 43 patches.
  - Rec: **yes**.
- **R-m: scope.** The chronicle's non-reactive openers ride in the lanes that already own their files:
  B452 and B456 (solver, FIRST, beside B463), E230/E231/E232 (editor), E233 (syntax), F53 (native),
  F27's editor routing (editor). Rec: **yes**. M60, A87/A111, A131, and the builds of A138/I10 carry
  to Order 45.

## Mechanics (every lane)

briefs43.md's "Mechanics" stands in full: briefs42's and Order 41's rules, the item's text is a
HYPOTHESIS, native differential in every std gate, worktrees `vilan/.claude/worktrees/<lane>-44` off
`origin/next` @07e8db37 and never the main checkout, one commit per item with its CHANGELOG entry under
`## Unreleased`, tracker writes through `file_items.py` / `stamp_items.py` / `close_batch.py`, the PATH
export, and **model Opus, never Fable** (the launcher passes `model` explicitly). Added to them, this
week's lessons and the train's rules:

- **Lanes write ledger rows `NEW`** and cite them by message. The merge helper renumbers from the
  head's max and remaps the pins, so per-lane id blocks are pointless (Order 43's lesson).
- **LANE-STATUS.md stays UNTRACKED.** Two lanes' status files at the root collide add/add at merge.
  The integrator keeps them.
- **Every std-touching lane's gate list includes `check_scope_differential`.** Order 43's seal (1) was
  red on an unexported field type under the reach rule. A `#[cfg(unix)]` constant read only by unix
  pins is dead on the Windows cross-check, so run `clippy --target x86_64-pc-windows-gnu` when adding
  one.
- **A test file two lanes APPEND to at the same spot** is rebuilt at merge from each side's WHOLE
  insertion, never from git's hunks (solver-43's merge).
- **The pipe rule, until B463 is on next:** every combinator, consumer and sealing operation takes
  `own self`, including trait defaults. A `self` default over a `[resource]` `Self` is the B463 hole.
  After B463 lands, the refusal proves it.
- **Native gates for pipe code need F56.** The `rust` backend refused every `[resource]` type at GO
  (step 0). Until native-44 merges, a lane whose std change emits a pipe node cherry-picks F56's commit
  (sha in native-44's LANE-STATUS.md) for its native gates only.
- **The paper is the spec.** A lane that finds a ruling unbuildable STOPS that item and messages the
  integrator, citing the ruling's number. It never re-rules in code. A paper edit is the integrator's.

## Lane solver-44: B463 FIRST (the train's floor; sha to LANE-STATUS.md the moment it lands), B452 and B456 FIRST beside it, then B458, B461, B462, B434, B460 (R-a), B457 (R-e), B401 (R-h), B428 (R-i), and the steer for `.get()` on a pipe

1. **B463.** Resource-ness is decided per instantiation (§6.8), so the affine check runs over a trait
   default's body under each resource instantiation of `Self`, or at the impl that admits the default.
   A loaned `self` moved into an aggregate is refused with the concrete impl's message.
   - Red-first pins: the 22-line repro (A142 Appendix A / the item), a generic free function over
     `T` with a resource instantiation, and the prototype's `derive(self)` branch case.
   - The concrete-impl refusal stays byte-identical.
2. **B452.** The JS emitter keeps sibling evaluation order when an argument, list element or struct
   field is a block expression (no hoist ahead of earlier siblings; a temp per earlier sibling where
   the block needs a statement position). The repros are under `sweeps/order43/solver-43/finds/`.
3. **B456.** The same-name concrete/blanket collision is refused in BOTH declaration orders and across
   modules. Pin both orders and the cross-module case. Kolt's `StorageSignal` shape is the customer; the
   kolt patch, if any, goes in the report.
4. **B458.** `Context::clear<U>(self, body: || U): U` as an intrinsic beside `run`/`get`/`get_safe`.
   Inside it, a strict `get` region is the uncovered coverage error, naming the `clear`, and a
   `get_safe` region receives `None`. A nested `run` re-establishes. Closures created inside capture
   the cleared state. tracking-44 cherry-picks this for its gates.
5. **B461.** A bare trait nested in an annotation mints one implicit generic per mention (B186's
   `mint_implicit_generic`) at `let`, parameter and field positions. A mixed literal steers to `dyn`.
6. **B462.** A tuple variant at a closure-typed position coerces to `|A, B| E<..>`, with generics taken
   from the expected type. Unit and named-field variants do not coerce, and neither does a position
   with no expected closure type (B348's rule shape).
7. **B434.** A closure parameter's type reaches a generic constructor in the closure's tail.
   collections-44's `filter_map(|x| x)` over `IntoFlow` is the first customer; pin that shape too.
8. **B460** if R-a is ruled (a): the opaque return for free functions and inherent methods (B184's
   hidden-parameter machinery, callee-bound), with the steer to `dyn` when branches disagree.
   Trait-method returns are refused as today, with a steer. The inlay face comes from editor-44's
   `~T`.
9. **B457** per R-e (a write summary per callee; the 14 notify goldens classified).
10. **B401** per R-h.
11. **B428** per R-i.
12. **The steer for `.get()` on a pipe** (A142 §3.3). A method missing on a type that implements `Pipe`
    but present on `Source` answers "a pipe has no `get`: seal it with `.memo()`, or read it once with
    `.sample()`". Today the message suggests importing `Source`. The analyzer half is this lane's; the
    wording is pinned against reactive-44's names after the rebase.

Sizing L. Owns analyzer.rs, impl_select.rs, mono.rs, transformer.rs (JS emit), the context pass.

## Lane native-44: F56 FIRST (step 0's find), F53, the native parity of the pipe nodes, the censuses after the split

0. **F56, FIRST.** Step 0 ran at GO: the `rust` backend refuses every `[resource]` type (vilan-rust
   lib.rs `ensure_struct` and its enum twin). Lift the refusal for a resource with no `Drop` impl and
   emit it as an ordinary type, with no clone at a move site. A resource WITH `Drop` stays refused
   (teardown is F1's later slice).
   - Pins: Appendix A's five programs print the JS output natively (the fused chain, `switch`, an `own`
     parameter, a branch, a `dyn Up` holder); a `Drop` resource is still refused.
   - Put the sha in LANE-STATUS.md the moment it lands: reactive-44 cherry-picks it.
1. **F53.** A closure body erased to `dyn` is wrapped natively (`roots.map(|r| r)` into a
   `List<dyn Src>`).
2. **Native parity for reactive-44's node layout** as its branch grows. Cherry-pick its commits for
   your gates only. Anything the Rust emitter lacks for `own self` blanket defaults or `dyn Pipe` is
   fixed here, before reactive-44's merge.
3. **After reactive-44's merge:** the native copy census regenerated over the tip, and the native leak
   census re-run. Pipe instances must release their stage owners and subscriptions; the list-cell row
   stays at 0.

Sizing M. Owns vilan-rust, vilan-rt, the native tests and censuses.

## Lane reactive-44: A142 S1 + S2 (THE TRAIN; BREAKING). Starts at GO; F56 cherry-picked from native-44 for native gates; `own self` everywhere until B463

1. **S1, the split** (paper §3). Write the traits:
   - `Flow<T>`: the combinators and consumers, all `own self`, with a blanket impl over every
     `Source<T>`.
   - `Pipe<T>`: `with Flow<T>`; the sealing operations.
   - `Source<T>`: keeps `get` and the node-author member `on_settle`.

   A124's nodes become `[resource]` pipe nodes. Each is its own instance: `switch` keeps its current
   inner and generation, and `distinct`/`distinct_by` keep their last key.

   The surface:
   - `derive`, the renamed `map`; its node is `Derive`, which ends I9's collision from the reactive side;
   - `switch`, `switch_some`, `then_some` (takes a `Source`);
   - `flatten` (over flows of `Source`s), `and_then`;
   - `distinct`, `distinct_by`;
   - `Source::constant(v)`;
   - sealing: `.memo()` (a read-only face over one `SignalCell`), `.cell()`, `.memo_global()`,
     `.cell_global()`, `.sample()`;
   - `sub`, `on_change`, `effect`, `effect_on_change` moved to `Flow`.

   Also in S1:
   - `std::ui`'s bindings accept `Flow`, and a binding is a consumer.
   - `MaybeSignal`'s static arm is unchanged (R26).
   - The examples, the website's snippets and the guide's reactive pages are rewritten, with counts
     declared in the report.
   - A135's warning wording (`.cell()` → `.memo()` where it names the seal) is updated.
   - Pins:
     - a second consumer is refused, both by sealing twice and by branching;
     - a root is copied freely;
     - `cell.memo()` has no method;
     - a five-stage sealed chain puts ONE subscriber on its root and runs once per change;
     - `sample` releases what its bodies created.
2. **S2, per-run owners** (paper §4):
   - every pipe stage's body runs under a lazily allocated per-run owner, created on the first
     registration;
   - `effect` and `scoped_effect` merge, with `scoped_effect` kept as a `[deprecated]` alias;
   - a task started during a run belongs to that run's nursery and is cancelled when the run is
     released.

   Pins:
   - a body that registers nothing allocates no owner (callgrind or a counter);
   - a superseded fetch is cancelled;
   - a `switch` selector's creations are released on re-selection;
   - the prototype's `made=1` shape.
3. **The kolt patch (R-l):** `sweeps/order44/reactive-44/kolt-reactive-44.patch`, over a scratch copy
   at kolt's tip plus the owed Order 43 patches. `vilan check` 0/0 and `vilan build` clean over the
   patched copy; the site count in the report.

Sizing XL (the order's long pole). Owns reactive.vl (all of it this order, until its merge),
delta.vl's `Source` impls, `std::ui`'s binding signatures, memo.vl's doc lines that name `.cell()`, the
guide's reactive pages, the examples.

## Lane transient-44: A141 FIRST (R-f; independent of the split), A139, A140, A133 (R-g), then A142 S3, REBASED onto reactive-44's merge

1. **A141** per R-f. A `Service::new` route runs under the service's owner. The warning covers a
   derivation stored through `get_or_insert`/`Shared::write` in a handler. Pin: N connections open and
   close, and the shared store's cached derivation survives the first close. Kolt store.vl:160 goes in
   the report.
2. **A139.** The sibling seed is extended to the per-key path; pinned in-process AND over a socket.
3. **A140.** Routes and replays are pruned on the mirror's retire hook (A134's `MirrorTable` event).
   Pin: N mints then N releases leave 0 routes and 0 replays.
4. **A133** per R-g: the in-process seed is documented as inline in remote-sources.md and at
   `duplex_pair`; the item closes.
5. **S3, after the rebase** (paper §5):
   - `TransientState<T, E>` (Pending, Ready, Refreshing, `Failed(E, Option<T>)`, Absent);
   - `TransientSource<T, E>` with `Source<Option<T>>`: `state()` is the read-only face, and `latest()`
     and `is_pending()` return fresh pipes;
   - `TaskSource<T, E>` (one-shot);
   - `Pipe<Task<..>>.transient()`: latest task wins; the superseded task is cancelled with its run (S2)
     and a late reply is dropped. R36's error rule: `Task<Result<T, E>>` lifts `Err`, and a bare
     `Task<T>` is `E = str`;
   - `RemoteSource` implements `TransientSource<T, RpcError>`, with rpc.vl's `Status` mapped as the
     paper says.

   Pins:
   - out-of-order replies;
   - a failed refresh keeps the stale value;
   - `Absent` versus `Pending` over a socket;
   - `latest()` across Refreshing.

Sizing M–L. Owns rpc.vl, rpc_server.vl, a new transient.vl (or reactive.vl's transient section AFTER
the rebase), remote-sources.md.

## Lane collections-44: I9 (R-c, BREAKING) and I8's maps half first, then A142 S4 + S5, REBASED onto reactive-44's merge

1. **I9:**
   - `std::hash_map::HashMap<K, V>` / `std::hash_set::HashSet<T>`;
   - `Map`/`Set` kept one release as `[deprecated]` aliases in their old modules;
   - the estate codemod (std, examples, the website, the playground) and the kolt patch
     (`kolt-collections-44.patch`);
   - the prelude, the guide and the spec pages.

   This can start before the rebase: it does not touch reactive.vl beyond imports.
2. **I8's maps half:** `HashMap::get_or_insert(key, || make())`.
3. **S4** (paper §6):
   - collection pipes (`CollPipe<T>`), sealed by `.memo()` into `CollSource<T>` or consumed by
     `each`/`each_by`;
   - `IntoFlow<T>`, the result trait with a plain-value blanket (a constant, no subscription) and a
     `Flow` impl (started per element);
   - flow-following `filter`/`filter_map`/`any`/`all`/`count`;
   - `CollPipe<S: Source<U>>.flatten()`;
   - `map` starting a returned pipe per element (R35) while never flattening a returned `Source`;
   - per-element owners, stable slot ids, and the Fenwick index for `filter`/`filter_map` output
     positions;
   - counter folds using `delta.vl`'s "what left" payload.

   Pins:
   - a plain `filter` allocates nothing per element;
   - `any` over `is_pending()` pipes flips exactly once per element change;
   - a removed element releases its source;
   - `filter_map(|x| x)` over transients (needs B434 — cherry-pick for gates);
   - positions under interleaved splices.
4. **S5:** `.coll_by(key)` over `ReconcilePlan` (it can emit `Move`) and `.coll()`, positional, with
   `T: PartialEq` and prefix/suffix trim. Pins: minimal ops for append / insert-one / remove-one.

Sizing L. Owns delta.vl (the operators), list.vl's cell half, map.vl/set.vl → hash_map.vl/hash_set.vl,
`each`/`each_by`'s input type in `std::ui` (after reactive-44's merge), the collection guide pages.

## Lane tracking-44: A142 S6, REBASED onto reactive-44's merge, with solver-44's B458 cherry-picked for gates until it merges

1. **The context:** `tracking: Context<TrackScope>`. `Source::track(self): T` does `get()` plus a
   registration through the STRICT `get`, so a `track()` outside a scope is a compile error.
2. **Scopes in every pipe body** (paper §7.2): `derive`, the `switch` selector, `effect`, and the free
   `derive(|| body)`, which returns a pipe.
   - After each run, the new dependency list is compared with the old one, reusing edges in order.
   - New dependencies subscribe and dropped ones release.
   - Wakes happen in the derivation phase (`as_derivation`).
   - Collection per-element closures open NO scope (R9).
3. **Callbacks clear:** `on_change`, `effect_on_change` and UI event handlers run their callback under
   `tracking.clear(..)` (B458). `clear` is the documented `untrack`.
4. **Docs:** reactive-batching.md and reactive-pipeline.md each get the pointer paragraph (paper §7.4) —
   that is a proposals edit, so it goes to the integrator in the report. The guide gets a tracked-reads
   page.

Pins:
- a dynamic dependency switches;
- a dependency dropped by a branch stops waking;
- a callback minted in a scope does not register later;
- `clear` inside a free `derive`;
- a glitch-free diamond.

Sizing M. Owns reactive.vl's tracking section (a new tracking.vl if cleaner), the UI handlers' callback
wrapper.

## Lane syntax-44: B459 (then/else and the guard, R15), B414 S4 (R-k), E233

1. **B459.** The expression form `EXP then EXP else EXP` and the statement forms `EXP then STMT;`,
   `EXP else STMT;`, `EXP then STMT else STMT;`, all sugar over `if`. Per the item:
   - `then` is contextual (B414's machinery);
   - precedence above assignment and below `||`;
   - right-associative chaining;
   - no bare `then` in expression position;
   - the statement reading at statement position;
   - `let` refused as the STMT.

   **R15:** when the `else` statement diverges (`never`), the condition's `is` bindings extend to the
   rest of the enclosing block. This is the one non-rewrite rule; its scope rows in analyzer.rs land
   AFTER solver-44's merge (rebase). Formatter line-break rule, EBNF + `grammar_sync`, both editor
   grammars, hover on `then`.
2. **B414 S4** per R-k, RULED STRICTER at GO: a member name follows `.` with NO whitespace, for every
   member. Census the estate first (std, examples, kolt read-only, the website, the playground) for
   `.` followed by whitespace before a name. If the census finds a legitimate use, build the owner's
   minimum instead (no newline between `.` and the name) and list the uses. Either way, any word is
   admitted as a member after `.`, and the diagnostic steers to `.name`.
3. **E233.** The formatter reorders a `borrows`/`context` pair to the canonical order when the return
   type is `&T`.

Sizing M. Owns lexing.rs, parsing.rs, formatter.rs, grammar.md and the EBNF, the editor grammars; the
analyzer scope rows for R15 only, after the rebase.

## Lane editor-44: E227 (R-d) with the pipe hints, E232, E230, E231, E224 (R-j), F27's editor routing. LAST to merge (the hint attributes go on reactive-44's node names)

1. **E227** per R-d:
   - the `[hint(Trait<..>)]` attribute (parser + one analyzer table — coordinate the parser rows with
     syntax-44);
   - the substitution in `inlay_hints`, admitted per instantiation;
   - the marker `~T`; nested nodes abbreviate;
   - `vilan.inlayHints.abbreviate` on by default; hover shows both forms;
   - the attributes: the pipe nodes `[hint(Pipe<T>)]`, the sealed faces and `RemoteSource`
     `[hint(Source<T>)]`, the eight iterator adapters.
2. **E232.** Door (2): hints on the edited line stay in place; the server keeps serving the last
   analysis's hints for a dirty line until the new one lands.
3. **E230.** `vilan upgrade` runs the installers' extension step, preferring the gallery id.
4. **E231.** The server reports `version (sha)`, and the extension compares shas when both carry one
   (the vsix embeds the sha at packaging).
5. **E224** per R-j (type import lines stop warning; the paper's line 87 corrected by the integrator).
6. **F27's editor routing** (R3's remainder: the editor keeps the second platform's analysis for twin
   files).

Sizing M. Owns vilan-lsp, editors/vscode, the installer scripts, labels.rs (E224).

## Lane papers-44: A142 S7 (the `Store` paper), A138 with I10 folded in; NO tree change

1. **A142 S7, the `Store` paper** (reactive-layers.md §8):
   - `Store::new(value)` generates the fine-grained version of a type from its shape: a cell per scalar
     leaf, a lazily allocated slot per field, the enum discriminant plus the live payload, and a
     collection's declared shape;
   - projections are `Source`/`Signal` lenses, cheap copyable handles;
   - a whole-value write diffs;
   - same-variant writes patch.

   Its questions: the slot layout (inline pointer vs side table), `Store::new` vs a `reactive let`
   binding form, and what a private-field type exposes. A prototype on the train's tip if it has
   merged, otherwise on 0.41.1 with Appendix A's style.
2. **A138 + I10:** reactive maps and sets as the Map and Set shapes of paper §6:
   - `KeyedCell` censused against a map face;
   - `SetCell`;
   - `MapOp`/`SetOp` operators and per-key tracking;
   - I10's ordering strategy (doors a/b/c) decided in the same paper, because an ordered map is a
     shape question.

   Recs and sizing; the build queues for Order 45.

Merges to proposals only.

## Ownership map (conflict avoidance)

- **solver-44:** analyzer.rs, impl_select.rs, mono.rs, transformer.rs (JS emit), the context pass.
  syntax-44 takes R15's scope rows and editor-44 the `[hint]` table rows, each AFTER solver-44's
  merge (rebase, never cherry-pick).
- **native-44:** vilan-rust, vilan-rt.
- **reactive-44:** reactive.vl (whole), delta.vl's `Source` impls, `std::ui` binding signatures, the
  guide's reactive pages, the examples.
- **transient-44:** rpc.vl, rpc_server.vl (A141 first, before the rebase), then the transient section.
- **collections-44:** delta.vl's operators, list.vl's cell half, hash_map.vl/hash_set.vl, `each`'s input
  type (after reactive-44).
- **tracking-44:** the tracking section, the handlers' callback wrapper.
- **syntax-44:** lexing.rs, parsing.rs, formatter.rs, grammar.md/EBNF, the editor grammars.
- **editor-44:** vilan-lsp, editors/vscode, the installers, labels.rs.
- **The estate codemods (I9's rename, S1's `.map` → `.derive`) touch every std file.** collections-44's
  I9 codemod runs over reactive-44's MERGED tree (rebase first), so the two sweeps never interleave.
  reactive-44's `.map` → `.derive` over collection files lands first.
- **Merge order:** solver-44, native-44, reactive-44, transient-44 (rebased), collections-44 (rebased),
  tracking-44 (rebased), syntax-44 (rebased), editor-44 (rebased). papers-44 goes to proposals.
- **After every merge that moved goldens:** `regen_goldens.sh`, the copy census, the merge helper's
  BUILD step, `native_differential` and `check_scope_differential` in every gate list.
- **After the seal and CI green:** the v0.42.0 cut (R-b) per releases.md, with `release/0.41` deleted
  at the cut. Then the toolchain in both locations from the tag, the vsix, the playground wasm smoke
  (N134), and the website migrated to the pipe spellings (reactive-44's snippets).

## At the sweep (integrator, proposals)

- **Close per the reports.** A142 stays OPEN with S7's build queued; A133 closes per R-g. B458–B463
  close on their pins.
- **reactive-layers.md:** a "built" note per slice, and §7.4's pointer paragraphs into
  reactive-batching.md and reactive-pipeline.md (tracking-44's text). inlay-hint-abbreviation.md and
  deprecation.md (R-j) are marked built.
- **Kolt at the owner's word, in order:**
  1. the owed Order 43 patches (B419's, the A122 `divorce` edit);
  2. `kolt-reactive-44.patch`;
  3. `kolt-collections-44.patch`;
  4. store.vl:160 per A141;
  5. `lib/reactive2.vl` retires to a note (the paper supersedes it).
- **Order 45's queue:** the `Store` build (A142 S7) if the paper is ruled; A138/I10's build; M60;
  A87/A111 if a caller appears; A131 if an exhibit appears; B460's trait-method returns (paper first);
  B183's concrete arm; the `self::` paths if re-ruled.
