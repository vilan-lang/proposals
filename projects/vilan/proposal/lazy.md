# `lazy` — defer to first demand

> **Status: RATIFIED 2026-07-21.** The §6 calls (user): **(a) poison** — a
> failed initializer/argument re-panics on later touches; **(b) retrofit** —
> `Option.unwrap_or`/`Result.unwrap_or` become `lazy fallback`, gated on the
> corpus/std/docs sweep (any observable difference is stop-and-decide);
> **(c) `lazy`** — the user offered `lazy` or `late`; `lazy` chosen for the
> Kotlin/Swift precedent, and because Dart's `late` names a different
> contract (assign-before-use, not memoized call-by-need) that would import
> wrong intuitions. Implementation queue: slices in §7, sequenced at the
> user's call (A13 shipped 2026-07-21; F5/F7 hold the next slot in the
> agreed order).
>
> Original status: **DRAFT 2026-07-20 — for review.** Origin: the lazy-database question
> (2026-07-20) — the accessor sketch (`fun db(): &Database` over a `mut
> Option<Database>` global) fights three model walls at once (module writes, view
> returns, payload locking) because it relocates ownership plumbing into user code.
> The resolution moves only the *time* of one event. The user's reframing is the
> design: `lazy` must not be a one-case keyword — it is **one semantic in several
> positions**: *defer evaluation to first demand, evaluate at most once, memoize.* A
> lazy parameter defers an argument; a lazy binding defers an initializer. One
> lowering (a memo thunk) serves both.

## 1. Lazy parameters

```vilan
impl Option<type T> {
    fun expect(self, lazy message: str): T { .. }     // new surface
    fun unwrap_or(self, lazy fallback: T): T { .. }   // retrofit (§6b)
}

option.expect(i"no row for {key} in {table.describe()}");
```

- **Call site**: the argument expression is not evaluated; the compiler packages it
  as a thunk closing over its free variables. Every existing capture rule applies to
  that closure unchanged — a view in the expression is a view capture (rejected), a
  resource local is an R9 capture (rejected; module-level resources pass, per the
  exemption), so nothing new leaks.
- **Callee side**: the parameter reads as a plain `T` — fully transparent. The thunk
  forces on the parameter's **first read** and memoizes; later reads reuse the value
  (call-by-need, not call-by-name — an argument never runs twice, so a side effect
  can at most happen once, late). A parameter never read never runs — that is the
  point (`expect`'s happy path).
- **Forwarding**: passing a lazy parameter onward to another lazy position forwards
  the thunk (one memo, however deep the chain); passing it to an eager position
  forces it there.
- **v1 restrictions**, each the conservative direction:
  - **Data only.** A lazy *resource* argument would make the thunk own a resource —
    a closure owning a resource is exactly what R9 forbids. Resources stay eager.
  - **Sync only.** An awaiting argument would smuggle asyncness into the callee at
    an invisible forcing point; deferred async already has a spelling (`async
    expr` → pass the `Task`).
  - **Context-free.** The thunk forces inside the callee, where the call site's
    ambient contexts may be gone — the same self-containment rule `drop` bodies and
    (§2) lazy initializers obey. A context-reading expression in lazy position is
    rejected with the steer to pass a closure explicitly.
- **Traits**: a `lazy` parameter is part of the signature; impls must match. (B29 —
  name-only conformance — means the mismatch is not caught today; the `lazy` check
  should not wait for B29: laziness changes call-site *codegen*, so the S1 slice
  carries a targeted arity/laziness agreement check for impls of lazy-parameter
  signatures.)

## 2. Lazy module bindings

```vilan
lazy let database: Database = Database::open("kolt.db");
```

The initializer runs at the binding's **first use** instead of module load, then
memoizes. *Everything else is identical to today's eager module global*: the module
owns the value, process lifetime, resources are loan-only and write-frozen (the
2026-07-20 rule), closures may reference it (the R9 exemption), platform coloring
flows from the initializer exactly as global init colors today, and it never drops.
The lazy-database answer is this one line — no accessor, no `Option`, no view
returns.

- **The initializer is sync and context-free** — first touch can happen anywhere, so
  the deferred code must be self-contained. Pleasing symmetry: birth and death
  (`drop`) obey the same law, for the same reason (their call sites don't thread
  contexts).
- **Reentrancy**: an initializer that (transitively) touches its own binding traps
  with a clear message ("lazy initialization cycle: `database`") via an
  in-progress flag — not a silent hang.
- **A failed initializer poisons the binding** (recommendation, §6a): the panic
  propagates at the touching site, and later touches re-panic with the poisoned
  message. Retry-on-next-touch would re-run side effects and turn "at most once"
  into "at least once per attempt".
- **Turns**: initialization is atomic within a turn by construction (the
  initializer is sync; nothing interleaves mid-init on one turn).

## 3. What v1 excludes, and why

- **Lazy local `let`** for resources: an end-of-scope drop would need a runtime
  was-it-initialized flag — drop flags are ratified out (C4 (c)). Lazy *data*
  locals are harmless but weakly motivated; excluded for symmetry, recorded as the
  relaxation if demand appears.
- **Lazy resource parameters, async/context-carrying thunks**: above.
- **`lazy` fields**: a struct field's forcing point is any read anywhere — that is
  interior mutability through a copyable value, a different feature (`Shared`'s
  territory). Out.

## 4. Classification under the closure rule

`claims-and-epochs.md` §4: **surface, not a model change.** No new alias kind — a
lazy binding is loaned exactly like an eager one, a lazy parameter is a compiler-
managed closure. No new epoch event — the initialization event exists either way;
only its time moves, and no claim can precede the birth it waits on (a loan of a
lazy binding forces it first). The law is untouched.

## 5. Lowering

One shape serves both positions: a memo cell `{ state, value, thunk }` with a
`__force` helper (state: pending → running → done | poisoned; `running` is the cycle
trap). Parameters pass the cell; bindings store it module-level. **The helper needs
its interpreter arm in the same commit** (the equivalence gate). Hover renders
`lazy` in signatures like the other effect surface. `lazy` is a hard keyword
(grep-verified free of identifier uses) — and per the AGENTS.md invariant it lands
in **three homes**: lexer, TextMate grammar, book theme, same commit.

## 6. Open questions — SETTLED 2026-07-21 (calls in the status block)

- **(a) Poison vs retry** on a panicking initializer/argument. Recommendation:
  poison (at-most-once stays true; retry re-runs side effects). **CALL: poison.**
- **(b) Retrofitting `Option.unwrap_or` / `Result.unwrap_or`** to `lazy fallback`.
  This *changes observable behavior* of existing call sites whose fallback has side
  effects (they stop running eagerly on the `Some` path). Recommendation: retrofit —
  deferred-fallback is what callers nearly always mean, `unwrap_or_else` remains the
  explicit form, and the corpus/std/docs sweep is the gate (any observable
  difference is a stop-and-decide, per the E2/E3 precedent). New `expect(self, lazy
  message: str)` lands alongside either way. **CALL: retrofit, sweep-gated.**
- **(c) Keyword spelling**: `lazy` (recommendation; Kotlin/Swift precedent) vs
  `defer` (collides with Go/Zig's unrelated meaning) vs annotation-style.
  **CALL: `lazy`** (user offered `lazy`/`late`; `late` rejected as Dart's
  different contract).

## 7. Slices (suite-gated, docs same commit, per-case pins)

1. **S1 — lazy parameters** (the pure-sugar half; derisks the memo lowering):
   keyword through lexer/parser/formatter (+ the three grammar homes), thunking at
   call sites, forcing on first read, forwarding, the v1 rejections (resource /
   async / context arguments, each with its steer), the impl-signature agreement
   check, `__force` + interpreter arm. Pins: forced-once (memo observable via a
   counting side effect), never-forced-never-runs, forwarding chains, each
   rejection, trait mismatch, hover.
2. **S2 — lazy module bindings**: the memo cell at module scope, first-use init
   order (observable via prints), cycle trap, poison, loan-only/write-frozen
   inheritance for resources (pins with a real `Database`), platform coloring of
   the initializer, docs (spec §6.x sentence for bindings + the std pages for
   `expect`/`unwrap_or`, tour "lazy resources" section replacing nothing — the
   eager idiom stays primary).
3. **S3 — std adoption + the retrofit sweep** per (b).

## 8. As built (Order 36, 2026-09-14, lane lang-c-36)

**S1 — lazy parameters** (`177be8de`). `lazy` is a hard keyword in all three
homes, landed in one commit: `KEYWORDS` + `Token::Lazy`, the TextMate grammar
and the book theme, the last two GENERATED from `grammar_sync.rs`'s
`KEYWORD_ROLES` (one row, `Modifier`). The modifier is accepted on a free
`fun`, an `impl` method and a `trait` signature — one parse path serves all
three — and refused on a closure and an `external fun`, and beside `own`, a
view, `mut` and `...`. A `lazy` written after the prefix it belongs in front
of is CONSUMED and reported rather than declined, because `Parser::attempt`
truncates a declining branch's errors.

The lowering is §5's, with one slot added: the memo cell is
`{ name, state, value, thunk }` — `name` because the cycle and poison messages
must say WHICH binding and the forcing site has no other way to know — built by
`__lazy(name, thunk)` and read through `__force(cell)`, states 0 pending,
1 running, 2 done, 3 poisoned. Both helpers carry their interpreter arms in
the same commit.

Two analyzer tables decide the call sites and the transformer reads them:
`lazy_argument_thunks` (the arguments packaged, mapped to the parameter's
name) and `lazy_argument_forwards` (a bare reference to a binding that already
holds a cell, standing in another lazy position). They partition the lazy
positions, so forwarding is one memo however deep the chain and an eager
position forces, without either being re-derived at emission. A method and a
free call share the path: `wire_method_call` normalizes a method into a
`subject -> Expr::Local(member)` call with the receiver prepended, so one
positional zip serves both. The thunk's expression is walked into the
CLOSURE's own block, so every statement its lowering needs (temporaries,
short-circuit slots, scope-end teardown) lands inside the thunk rather than at
the call site.

§1's three v1 restrictions are refused as written, with two corrections to the
paper:

- **Data only** is enforced at BOTH ends: at the declaration when the declared
  type is concretely a resource (a signature nobody calls is still wrong), and
  at the argument when the value standing there resolves to one. A resource
  LOCAL named inside a lazy argument is refused by R9 itself, and a view
  binding by rule 3, in each rule's own words: the thunk is a closure, so the
  existing scans run over the argument expression with the existing sets and
  produce the existing violation. Neither needed a new refusal.
- **Sync only** counts both spellings of the suspension, exactly as E3 counts
  them — the `await` the author wrote, and the implicit one a call to an async
  callee performs — and steers to `async <expr>` → pass the `Task`.
- **Context-free** refuses an expression that calls a context-dependent
  function and steers to passing a closure. Both of these run in
  `post_analysis_passes` (`check_lazy_argument_effects`), because
  `async_functions` and `context_dependent_functions` are only settled there.

**The trait rule is no longer targeted.** §1 asked for a standalone
arity/laziness check because B29 — name-only conformance — had not landed.
B29 HAS landed: `check_one_conformance` compares receiver convention, arity,
per-position conventions and types. Laziness is one more position-wise
comparison beside the conventions, in both directions, with the trait's
declaration as the note.

**§5's "grep-verified free of identifier uses" was stale by the time it was
built.** Three programs in the tree used `lazy` as an identifier — the corpus's
`reactive-on-change.vl` and two Rust test programs — each a local binding,
each renamed to `quiet`. That is the whole migration: std, `examples/`, the
templates, the benchmarks, the docs' fences and kolt spell it nowhere.

**S2 — lazy module bindings** (`4454df49`). `lazy let name: T = init;`, module
level only. `Node::Let` carries the flag; `record_lazy_bindings` partitions the
declarations once every scope exists (which scopes are module bodies is not an
answer the walk has), module-level ones becoming cells and locals being
refused per §3. The declaration emits `__lazy("name", () => …)` with the
initializer walked into the thunk's own block; every read emits `__force`,
through the same arm a lazy parameter's reads take. A binding nothing reads
emits nothing and runs nothing — which is also why the unused-binding path may
not fall back to emitting the initializer for its effects.

Everything else about the binding is unchanged, and each was pinned rather than
assumed: loan-only and write-frozen for a resource (the module-level move
refusal fires on the lazy form exactly as on the eager one), platform coloring
flowing from the initializer (the reachability path still reads
`main → config → read_file_to_str`), process lifetime with no drop, and R9's
module-level exemption for closures.

**The relation, not the trap.** `init_order`'s load-time relation gives a lazy
binding NO out-edges: its declaration builds a closure, and creating a closure
is inert — the same rule that keeps the mutually-recursive module-closure idiom
legal. That is what leaves §2's reentrancy trap to the runtime, where the paper
put it: two lazy bindings that reach each other are legal as long as neither is
forced into its own initialization, and the one that is meets the cell's
`running` flag and panics ``lazy initialization cycle: `database` ``. A lazy
binding stays an ordinary TARGET, so its cell is still declared before anything
reads it.

**Poison** (§6a) is `` lazy `database` is poisoned: its initializer panicked:
<the original message> `` on every touch after the first, which propagates the
author's own panic. Only a vilan `panic` poisons, in the interpreter as in the
emitted JS: fuel, depth, an unsupported capability and an internal bug are the
expansion environment failing rather than the program throwing.

**Sync and context-free, with one diagnostic each.** The sync half is ALREADY
the rule every module-level initializer obeys, lazy or not, so `lazy` adds no
second sentence about the same mistake (B5) — the paper's §2 sentence is
enforced by the rule that was already there. Only the context half is new on
the binding side.

§3's exclusions are refused where they are written: a lazy local (an
end-of-scope drop would need the was-it-initialized flag drop flags were
ratified out to avoid), `lazy mut`, a lazy destructure, a lazy binding with no
initializer, and a bare `lazy name = …`. `lazy` fields were never parsed.

**HMR excludes lazy bindings** (`TransferForm::Excluded`). What a swap carries
is a VALUE, and a lazy binding may not have one yet; adopting the cell would
hand the new bundle the old bundle's thunk, closed over the old bundle's
functions. Fresh init on each swap is the honest v1 answer.

**Pins.** 37 in a new `crates/vilan-core/tests/inference/lazy.rs` (22 for S1,
15 for S2), behaviour-first — a counting side effect proves the memo, its
absence proves that a parameter never read never runs, print order proves the
force is the first READ and not the call, a three-hop chain proves the single
memo — plus two formatter round trips (`formatter.rs`), one hover
(`vilan-lsp`), and two against the real host database in
`vilan-cli/tests/database.rs`: a `lazy let database: Database` that opens at
the first read and stays one handle across three reads through two functions,
and the loan-only refusal firing on it as on the eager form. Seven ledger rows;
eight new parser rule statements (`RULE_STATEMENT_SITES` 34 → 42). Docs: spec
§6.10 and §3.4's production, appendix A.2, the tour's "Lazy parameters" and
"Lazy resources" sections, and the `Option`/`Result` page's note that the
retrofit has NOT happened.

**S3 — the std retrofit** (§6b) is not in this order: ruled Order 37's at
Order 36's GO.

## 9. As built (Order 37, 2026-09-17, lane lazy-37) — S3, the std retrofit

**Landed** (`e493ffb1`): `Option::expect(own self, lazy message: str)` — **new**, `Option`
had no `expect` at `d783fbf4` — `Option::unwrap_or(own self, lazy fallback: T)`,
`Result::expect(self, lazy message: str)`, `Result::unwrap_or(self, lazy fallback: T)`.
`unwrap_or_else` is untouched and stays the explicit form. The clone stays in the callee
(`__clone(__force(fallback))`), so a `List` fallback is still copied out of the caller's
binding — pinned, because the differential's prints cannot see an aliasing regression.
§8's "S3 is not in this order" line is retired by this section.

**The gate, as run.** A before/after differential over **304 programs** — 131 corpus
programs run under node, 155 complete docs fences built and run, 18 packaged
example/template/benchmark trees built — and kolt built both ways (std reverted in-tree,
never `git stash`, never `VILAN_STD`): **0 observable differences**; the eight non-zero
exits are identical on both sides and structural by design; kolt's client e2e output is
byte-identical. **211 call sites examined** (73 in `.vl`, 27 in docs, 97 inside Rust test
program consts, 14 in kolt): every non-literal fallback in the estate is a **bare name**
(`missing`, `empty`, `initial_theme`, `default_theme`), not one a call, so there was no
side effect to lose. Emitted JS moved at 36 of the 304 (the mechanical `__lazy` thunk
wrap; 114 thunk emissions) → sixteen corpus goldens regenerated. **A correction to §6b's
gate as the Order 37 brief spelled it:** "a changed golden" cannot be a stop-and-decide
difference — the retrofit necessarily rewrites every call site's argument into a thunk;
the gate is about observable *runtime* behaviour (prints, exit codes, side effects), and
that is what was held at zero.

**Two residues filed.** `Result::expect_err` is not retrofitted and is now asymmetric with
`expect` (A109, one line). Every `unwrap_or(<literal>)` now allocates a memo cell — 111
of the 114 thunk emissions carry an inert argument — and an "inert argument stays eager"
elision in `record_lazy_arguments` would keep most of the sixteen goldens byte-identical
and remove the `__force` on the hot path (M81).

**B344 and B345, the corners** (`bc7aaf7a`, `6191ccfa`). Three shapes compiled clean and
should not have: a resource the caller *produces* in the lazy position (`hold(flag,
make())` — no binding named, so R9 saw nothing), the indirect hop (a generic handing its
own `T` to another generic's lazy parameter), and a module-level resource named bare (R9
exempts it for process lifetime). The argument check reads a bare binding's type through
`variables`/`parameters` (`lazy_argument_type_id`, the analyzer's twin of B328's transformer
fix), and §1's data-only rule is asked again at every resource instantiation from
`check_resource_generic_instantiations`'s worklist, which reaches the indirect case by R11's
own propagation. Two stand-downs keep B5: a resource LOCAL named bare stays R9's, in R9's
words (§8), and the instantiation check is silent when the call-site value is concretely a
resource or when the instantiation already produced a diagnostic (`b63_unwrap_or_at_a_
resource_rejects_the_discarded_fallback` asserts exactly one). B345: the view-capture scan
walks a call's *subject* before its arguments — a computed callee (`(build(seen.label))()`)
carries the whole inner expression there. Neither fires on the estate.

**A102 (R13), the HMR question §3 left open** (`95058794`): a `lazy let` of a
value-transferable type crosses a hot swap only once something has forced it — a fourth
`TransferForm::LazyValue`; the new bundle's cell (its thunk closes over the new bundle's
functions) is wrapped in `__hmr_adopt_lazy(key, fp, __lazy(..))`, which writes the carried
value in and marks the cell done on a fingerprint-matching seed hit, and the exposing
getter `__hmr_lazy_value` **throws** when the cell is not done — the swap's capture already
skips a throwing getter, which is how the protocol has always spelled "this key carries
nothing", so pending and poisoned stay excluded with no fourth answer added. A lazy
`SignalCell`/`Shared` stays excluded. The round harness shows a forced `lazy let motto`
reading 41 after the swap while bundle B's initializer never runs, and a never-forced
`lazy let dormant` running B's initializer for the first time on the other side.
