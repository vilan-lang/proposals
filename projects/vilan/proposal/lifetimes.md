# The lifetime model — one liveness notion, two backends, and a measured escape hatch

> Status: **S1, S2, S3 AND S4 SHIPPED 2026-08-29** (cycle 37, order 19;
> S3/S4 on branch `lastuse-s3`) — §10 carries each slice's record, and
> §6's ship note below carries what the building corrected. S5 and S6+
> remain open. **The building's three lane rulings were RATIFIED
> 2026-08-29**: drop-at-declaration for a binding nothing reads (the
> owner's words: last-use destruction includes the declaration — unused
> declarations drop), the branch drop at the JOIN and only the join, and
> `retains` marking the place ROOT. Two S1 leftovers were ruled the same
> day: `ReactiveClient` gains an AUTO-dispose at terminal `Closed`
> (A30, the wiring over the bare seam), and the ownerless-derivation
> refusal is DEFERRED — leak-as-today stands, refused later only if the
> footguns become common or hard to diagnose (A28's tombstone carries
> the trigger). Prior status: DRAFT 2026-08-28 (the lifetime-model
> session), for owner review.
> Design-only: this session wrote no production code. Every load-bearing
> claim below is **measured** — three probe legs ran against `vilan 0.38.0
> (6186824b9)` on 2026-08-28: the semantics verification (34 compiled
> probes against the shipped checker), the reactive-graph analysis (V8
> heap snapshots + Tarjan SCC over running programs, `examples/todo`
> against its real server included), and the reclamation census (a
> lexer-verified static census + a 4,394-site dynamic instrument over the
> website server, cross-checked to exact agreement). The numbers are
> carried inline; the probe sources were session-scratch and the numbers
> here are the durable record.
>
> **The owner's reopening, verbatim (2026-08-28):** *"This is reopening
> old wounds. I'd like to revisit the lifetime model. I know we've
> discussed it before, but I'd like to take a detour to truly explore
> every avenue."* — and, framing the landscape: explicit destructors
> (C/Zig) vs garbage collection (JS) vs lifetime annotations (Rust),
> each with "disappointing downsides"; vilan's GC reliance blocks
> (1) dropping/disposal, (2) an efficient WASM target, (3) native
> binaries; *"Referenced data is the particularly difficult problem …
> None can address the root problem."*
>
> **Directions the owner has already ruled in this session** (recorded
> here as the paper's premises, not its questions): **last-use disposal**
> ("seems most appropriate"); **RC or Vale-style generational references
> as the easy escape hatch at a small runtime cost** ("Vilan isn't
> targeting absolute maximum performance"); **Tier C's storable
> references stay 'possibly never'** ("Good to know that it's still
> possible if useful down the road"); and the reactive graph **should be
> top-down unidirectional** ("Ownership is supposed to be a top-down
> unidirectional model" — §5 measures where it is and isn't).
>
> **This paper formally reopens a ratified sentence.** claims-and-epochs.md
> recorded *"C4 is the last major change"* to the memory model
> (2026-07-18). The owner's detour is that reopening, named rather than
> sidled past. What survives untouched: the epoch law itself, rules 1–4,
> the second-class view discipline, the affine resource class (R1–R12),
> and `Drop`'s shape. What this paper amends is *when* an owner's
> obligation discharges (§6), what the spec says closures do (§4), and
> what a non-JS backend uses in place of the host collector (§7).
>
> Governing records built on, not re-decided: `memory-management-rev-1.md`
> (the four rules; archived by relocation, not rejection),
> `claims-and-epochs.md` (static discharge vs dynamic carry),
> `destruction.md` (Tier 1 shipped; Tier 2's four-bullet sketch is this
> paper's §7 seed), `temporary-drop.md` (its statement-end measurements
> carry forward as the special case of last-use), `filesystem.md` §5.1
> (the `File`-only async-close exception, untouched).

---

## 0. The question, and the answer up front

The owner's question, verbatim: *"In a simplified language (no closures
being a major component), it's possible to solve lifetimes implicitly.
Does it actually break/expand exponentially as the language gains
complexity or is there a ceiling or way to solve it still without
imposing too many restrictions (or with escape hatches like occasional
explicit annotations)?"*

**It does not break exponentially. It breaks at cliffs — and vilan
already stands on the safe side of every one.** Region and lifetime
inference are decidable and polynomial in every fragment that matters
(the undecidable edge — region polymorphism with polymorphic recursion —
is exactly what MLKit restricted away; modern borrow checking à la
Polonius is Datalog). The one industrial-scale attempt at whole-program
implicit lifetimes for a rich language — MLKit's region inference for
Standard ML, closures included — failed on **predictability**, not
decidability: lifetimes became emergent whole-program properties, a
one-line edit could silently flip allocation behavior program-wide, and
errors had no local anchor. The true ceiling of pure implicitness is not
"can the compiler figure it out" but "can a human predict what it
figured out, and can an error message point somewhere."

The cliffs are five, each individually forcing annotation, restriction,
or runtime help: a reference **returned** (which input does the output
borrow from?), a reference **stored in a struct** (lifetimes infect the
type system — where Rust's annotation burden actually lives), a
reference **captured by a closure** (the first two in disguise),
**separate compilation / dynamic dispatch** (erase what inference
needs), and **concurrency**. Vilan's shipped rules refuse all five:
views are second-class (returnable only via `borrows` projections, never
storable — rev-1's permanent line), loans end at auditable lexical
intervals, R9 keeps resources out of closures, and the R10/R12 fences
keep ownership out of type-erased sinks. **That restriction set — chosen
for other reasons — is the ceiling-avoidance mechanism.** Vilan gets to
stay implicit because its boundaries are closed; the "occasional
explicit annotation" hatch (Rust's cliff 2) remains available and, per
the owner's ruling, possibly never needed.

The reframe the measurements then force: **"referenced data" is not what
ties vilan to the JS collector.** The aliased tier is 7.1% of a real
workload's allocations (§3), the affine tier is near zero (one dropped
binding in the whole website server), and ~93% of allocations are
uniquely owned *by construction* — the language already enforces what
other compilers must infer. What the collector actually carries is
(a) the reactive graph's closures and cells, and (b) the deep copies the
compiler inserts to keep ownership unique. Both have measured, targeted
answers that need no lifetime annotations: §5 and §7.

---

## 1. The landscape, honestly priced

The owner's three corners, plus the family between them that the three
corners hide:

| model | write for | safety | runtime | the disappointment |
|---|---|---|---|---|
| explicit destructors (C, Zig) | hard | poor | excellent | the human is the checker |
| tracing GC (JS) | easy | good | poor/unpredictable | no disposal points; no lean WASM/native |
| lifetime annotations (Rust) | hard | good | excellent | annotations infect types and users |
| **ownership + compiled RC** (Koka/Perceus, Lean 4, Lobster) | easy | good | very good | cycles leak; copy-on-write unless reuse analysis lands |
| **generational references** (Vale) | easy | good | good | a check per non-owning deref |
| **mutable value semantics** (Hylo; vilan rules 1–4) | easy | good | very good | sharing needs an explicit cell |

Vilan is already the sixth row. The fourth and fifth rows are not
alternatives to it — they are **backend reclamation strategies for the
sixth row's two leaky corners** (the aliased cells, the compiler's
copies), and §3's census assigns each to the corner it actually fits.
The prior record's two rejections stand undisturbed: destruction.md
rejected RC *as the general model* ("pays a global cost for a corner
problem") and claims-and-epochs rejected generational references *as the
general model* ("every dereference pays a check — Vale ran this
experiment so vilan doesn't have to"). This paper rules both **in** only
as targeted mechanisms for the corners the census sizes — which is the
distinction the earlier rejections themselves drew.

---

## 2. The model as shipped — verified, with two spec-vs-shipped gaps

The semantics leg probed every rule in `spec/memory.md` §6 against the
0.38.0 checker. The affine tier (R1–R12), the view discipline (bindable,
never storable/escapable, lexically live, loan-per-call), rule 4's
invalidation fence, `Drop`'s shape (synchronous, context-free, `&mut
self`, reverse declaration order via nested `try`/`finally`), and the
`Arena`/`Shared` hatches all hold exactly as written. Three findings
matter to this paper; the first two are gaps between the spec and the
tree, filed as items alongside this draft:

**2.1 Closure capture semantics were never specified — and the tour
documents the opposite of what ships.** The tour says *"Closures capture
their surroundings by value at the moment they are created. Vilan
copies, remember."* Measured: **false in both halves.** A closure
captures the outer *binding* by reference — a plain JS lexical closure.
Mutations flow in, writes flow out, whole-binding rebinding is visible
inside. The one copy is B64's per-call return copy, taken at each call,
not at creation. `capture-clones.md` governs *pattern* captures only
(the word "closure" does not appear in it); no rule in spec §6 covers
data capture at all. §4 specifies the rule.

**2.2 The documented ban on closures capturing views is not enforced.**
`memory.md` says a view "may not be captured by a closure that outlives
the place"; a probe returned a closure capturing a view of a dead local
and read through it — memory-safe today only because JS boxes the place
and traces it. Recorded in the impl plan as a deferral; under any non-GC
backend this is a use-after-free. Filed (C12); §6.4's liveness rule is
the fix's natural home.

**2.3 A naming hazard for every future memory discussion:** there are
two disjoint R-namespaces — `memory.md`'s R1–R12 (the affine rules) and
`transparent-references.md`'s R1–R8 (the view surface). R7 means "no
conditional moves" in one and "no `mut` view binding" in the other. This
paper writes **mR7** / **tR7** where ambiguity is possible.

---

## 3. The census — what a real vilan program actually allocates

The website server, instrumented at all 4,394 literal-allocation sites,
serving its real page; cross-checked by two independent counters to
exact agreement. Per render of `/` (40 KB of HTML):

```
allocations                                   ~24,555
  compiler-inserted deep copies (__clone)      12,292   50.1%
  constructions and accumulators               ~8,550   34.8%
  Option/Result/enum tuples                     1,887    7.7%   (registers on native)
  Shared cells — THE ALIASED TIER               1,740    7.1%
  escapes-to-closure                               ~86   <0.5%
dup candidates (__clone calls)                 36,033
non-owning dereferences (Shared .v + views)    ~1,140
dereferences, all forms                        23,834
retained after full GC, steady state          ~1.8 KB
```

Five facts fall out, and each one decides a design question:

1. **Copy-heavy, 30:1.** 36,033 dup sites against ~1,140 non-owning
   derefs. Whatever attacks the copy term attacks vilan's actual cost;
   whatever taxes dereferences taxes almost nothing.
2. **The aliased tier — the escape hatch — is 7.1%, measured.** And on
   the SSR leg it is almost entirely the `View` builder's interior
   cells, not user signals: `view(tag)` allocates three `Shared` cells,
   575 times per render, and every builder step's `return __clone(self)`
   produces sibling element arrays **sharing those same cells**. This is
   the one place scope- or last-use reasoning about the *value* is
   wrong about its *cells* — the case that forces a count or a check,
   and it is 7.1% big.
3. **Half of all allocations exist only because the compiler's
   copy-elision test is syntactic.** `is_elidable_copy` elides only a
   plain local with `reference_count == 1` outside loops/closures.
   25.4% of entities fail it — half with exactly two uses, the classic
   read-then-move shape a real last-use dataflow wins immediately.
4. **The affine tier is tiny.** One enrolled drop binding in the entire
   website server; eleven in the destruction stress test. Disposal
   policy is a correctness question, not a throughput one.
5. **2.6% of static sites carry 100% of request-path allocation** (115
   sites, 50 source lines; 92.9% of sites are the boot-time style
   tables). A reclamation pass has a small hot surface to be good at.
   Named hot spots for later engineering: `set_attribute` rebuilds the
   whole attribute list per write (1,171 allocs/render from one
   function); `index_of` heap-allocates `[0, index]` 1,192×/render.

---

## 4. The capture rule — specified

The rule this paper proposes spec §6 adopt, matching what ships:

> **A closure captures bindings, not values.** A captured binding is the
> same binding: mutation on either side is visible on the other, and a
> later rebinding is visible through the capture. A place a closure
> *returns*, rooted at a binding it did not declare, copies per call
> (B64). Resources cannot be captured (mR9); ambient context values are
> snapshotted at creation (the one true capture-time copy); and a view
> capture is governed by §6.4's liveness rule.

The alternative — making the tour's "vilan copies" true — was
considered and is **recommended against**: it would break every program
observing updates through a captured binding (probe c04's shape), it
buys no reclamation simplicity (the aliasing that matters rides `Shared`
cells, which survive any copy by design), and it costs a clone per
capture on the hot mount path. The by-reference rule is JS-native,
zero-cost today, and its native-backend consequence is already in the
record: **destruction.md Tier 2's fourth bullet** — closure environments
become counted objects (Swift's model), "the single reason `Shared`
cannot join Tier 1." The tour's paragraph is corrected under this
paper's amendments.

---

## 5. The reactive graph — the owner's claim, measured

**The claim is refuted as shipped and vindicated in design.** The owner
spine is genuinely acyclic — zero `Owner`s observed inside any cycle in
any probe. Every cycle lives one layer down, in five named places, each
measured by SCC analysis of live heap snapshots (todo app, real server,
real WebSocket — where the mounted app forms one 250-node
strongly-connected component with a 43-edge shortest cycle):

| # | back edge | class | smallest fix |
|---|---|---|---|
| V1 | `Signal::sub`/`map`'s notify closure captures `self` | incidental, universal (one 6-node cycle per subscription) | capture the value cell instead — **fix proven by probe**: cycle → no cycle, two lines |
| V2 | `map`/`combine`/`flatten` return no `Subscription` | **a live std leak today, GC or not**: the documented router idiom leaks 256 objects permanently per mount/dispose round, plus a time leak (every navigation notifies every dead derivation ever made) | return/register the subscription the way `effect` already does — filed as A28, fix-now |
| V3 | `bind_value`/`bind_draft` listeners capture their own element | incidental (the Add button, whose handler ignores its element, measured cycle-free) | `Event::target_value()` in `std::dom`; the listener then captures no element |
| V4 | a handler writes a signal a binding on the same element reads | the one *semantic* loop | broken by disposal already, provided V2 is fixed |
| V5 | `DuplexEnd.me` is never cleared | leaks a session's server+wire per disconnect under any RC | clear it in `dispose`/`drop_session`, one line |

Extent is friendly: 19 signals and 24 subscribers in the todo app
regardless of row count, ~54 graph nodes per list row, and zero drift
over 60 mutation round-trips. The unsubscribe machinery (`Subscription`
ids, owner scopes, `when`/`bind_each` disposal) works exactly as
designed where it is *reachable* — V2 is the API gap, not a mechanism
gap.

**AMENDMENT (2026-08-29, from the S1 build): V3's "smallest fix" line
understated it.** The accessor is necessary but not sufficient — V8
allocates one scope per invocation, so an inline listener reaches the
element its sibling effect closure captured however carefully its body
avoids naming it. The real repair is where the listener is BORN: a
function of its own whose scope holds only the signal (`write_back_value`
/`write_back_draft`). This is a §4 capture-rule consequence, not a DOM
one, and it is the standing rule for any future listener that must not
retain its element.

**Consequence:** "choose an acyclic design" was the wrong tense. The
acyclic design exists at the spine; **five mechanical repairs extend it
to the whole graph**, one of which (V2) is a standing bug worth a lane
this week independent of everything else in this paper. With V1–V3 and
V5 applied, the measured residual is V4 alone, which unmount dissolves.
One boundary caveat carried honestly: V3's element↔listener cycles
straddle the language/host boundary — no vilan-side scheme can see both
halves, so a non-JS backend needs V3 fixed *by construction*, not
collected.

---

## 6. Tier A — last-use disposal (the owner's ruling, priced)

**The ruling:** disposal moves from scope-end to **last use**. The
temporary-drop paper's statement-end recommendation becomes the special
case (a temporary's last use is its statement), so its measurements
carry forward unchanged; its two premise corrections stand (no "B141
lift" exists — the lowering invents it; the loop was never the decisive
case).

**What last-use buys, measured by the probe battery:**
- The §6.2 distinguishability objection **dissolves** — `let f = open(p);
  use(f)` and `use(open(p))` now have the same lifetime, extract/inline
  is behavior-preserving, and the Windows rename-race asymmetry is gone.
  Statement-end's main cost simply does not exist under last-use.
- The serve-forever `main` is fixed for every local, not just
  temporaries — under scope-end, a handle in a never-returning `main` is
  released **never** (fd probes: held forever today, freed at last use
  under the new lowering). This is the shape of every vilan server.
- `drop(x)` already emits a bare, positionally-placed `$a(r)` — **today's
  `drop(x)` is a hand-written last-use drop, byte-identical to what the
  pass would infer.** The feature exists; the pass stops requiring the
  human.
- Two live bugs found by the error-path probes are fixed structurally,
  because a last-use drop always rides `finally`: **`drop(x)` is not
  exception-safe today** (the explicit drop removes the scope `finally`,
  so a panic before it leaks — reproduced on 0.38.0; filed B150) and
  **mR2's overwrite double-drops when the RHS throws** (old value
  dropped, RHS panics, scope `finally` drops it again — a double close
  today, a double free on native; the fix is RHS-into-temp-first
  ordering, proven in-probe; filed B151, fix-now).

**What last-use costs, priced precisely:**

1. **Loans get the extension rule.** A loan is a use; a `borrows`
   projection extends the owner's last use to the last use of any view
   rooted at it. The analyzer already computes exactly this relation —
   `compute_view_origins` is the fixpoint a last-use pass consumes
   unchanged. Rule 4's *own* interval stays lexical (the surveyable
   interval remains what the compiler audits); ownership liveness and
   view validity become two stated notions with the extension rule as
   the bridge. The probe battery confirmed the bridge is load-bearing:
   dropping an owner at its own last use while a projected view was
   still live is the one unsoundness shape, and the extension rule
   removes it.
2. **The ordering sentence is amended.** `memory.md`'s "reverse
   declaration order at scope end" becomes "at each binding's last use;
   simultaneous discharge in reverse declaration order." A ratified
   sentence moves; every drop golden moves; the CHANGELOG entry is
   family breaking.
3. **Branch joins get drop specialization, not runtime flags.** A use
   inside one arm means the other arm owes the drop at the join — the
   compiler places a drop in each path (Perceus's drop specialization).
   This keeps mR7's no-runtime-flags doctrine fully intact for
   *bindings*. The **conditional temporary** (`cond &&
   open(p).stat()…`) remains the one shape with no static drop point
   and keeps temporary-drop's recommendation: **refusal** — the one
   place this arc makes a compiling program an error.
4. **Externs need a retention contract.** The probes demonstrated the
   case where last-use is *wrong*: an `[extern]` that stashes a loaned
   value host-side, read later — under last-use that is an immediate
   use-after-free (`tag=["<FREED>"]`, reproduced). The rule: **an extern
   loan is call-bounded unless the declaration says otherwise** — a
   declared retention (spelling to be settled, e.g. an `[extern(retains)]`
   attribute or `own` instead of a loan) extends the argument's liveness
   to the binding's scope. The HMR channel's synthesized getters (252
   invisible uses in the website server) and module-level bindings
   (never dropped, by design) are exempt by construction and stay so.

**Slice note:** the same dataflow, pointed at the value tier, replaces
`reference_count == 1` in copy elision — the census's single
highest-leverage change (§3 fact 3), a JS-backend win **today** with no
semantic change at all. It ships first, as the dataflow's proving
ground, before any drop timing moves.

### 6.5 Ship note — S3 and S4, 2026-08-29

**SHIPPED** on branch `lastuse-s3` (cycle 37, order 19). Everything §6
ruled is built: the lowering, the loan extension rule, branch-join
specialization, the conditional-temporary refusal, the ordering
amendment into `memory.md` §6.8, and — because a temporary's last use
*is* its statement — C11 in the same change-set. S4's retention contract
rides with it. What follows is what the building CORRECTED, because the
plan was right about the direction and wrong about several mechanics.

**The dataflow answers a second question, and it had to.** S2's answer is
per USE SITE ("is this read the last one?"), which is what elision needs.
Disposal cannot use it directly: a `finally` region can only be cut at a
statement boundary, so the pass also records, per binding, the CHAIN of
enclosing statements around its last read (outermost first). The consumer
picks the chain element that is a direct statement of the scope it is
emitting. Three answers, and the refusals fall back to the law that
shipped: drop at the declaration (nothing reads it), drop after the
statement holding the last read, or scope end.

**"Nothing reads it" is a ruling the paper did not make.** §6 said
"disposal moves from scope-end to last use" and left the no-use case
open. It is ruled here as **drop at the declaration**, because the
alternative — keep the old scope-end rule for unread bindings — makes
adding a use RELEASE THE VALUE EARLIER, which is not a rule anyone can
hold in their head. It is also what makes the never-ending `main` fix
total. It is the single largest source of estate churn: fifteen shipped
pins had programs adjusted, because "drop runs on early `ret`" and its
neighbours were all written with a binding nothing reads, and became
vacuous overnight.

**Branch-join specialization is the join, and only the join.** §6.3 said
"the compiler places a drop in each path". Building it showed that a
per-arm drop cannot be made exception-safe without a runtime flag: the
outer `finally` covering the acquisition would fire again on the arm that
already dropped, and distinguishing them is exactly the flag mR7 bans. So
the drop lands at the JOIN — which every path reaches, taken, not-taken,
`ret` and `jump` alike — and the specialization's observable content is
what P5 asked for: both paths release exactly once, flaglessly. The
residue is honest and recorded: a using arm with a long tail after its
last read holds the resource to the join rather than releasing inside the
arm. Statement granularity is the floor `temporary-drop.md` §6.1 named,
and this is where the floor shows.

**Two emission laws the plan did not name, both found by probe.**
*Regions nest.* A teardown region lowers to a JS block, so every `const`
a statement inside it declares dies at that block's brace — the region
must be widened until it covers the last read of every name declared
within it, or the emitted program reads a name out of scope. Found on
`owner.enter(…)`'s result, read after the owner's drop point. The
widening question is deliberately SYNTACTIC, not the dataflow's: block
scope is about where a name may be written down, not when a value may be
destroyed, so opacity does not apply to it and only the completeness net
(a read the walk never saw) can make it wrong. *And order matters:* the
`finally` must be built AFTER its region is walked, because the capture
drop path reads an alias table the walk fills and every minted name comes
from one generator — building the drop first renamed every helper after
it and moved two goldens for no reason.

**`drop(x)` needed no exception.** The plan reserved one, on the theory
that B150's guarded `finally` is a net over the whole scope. It is not:
moving into the sink is a USE, and R7 rejects a conditional one, so the
sink's statement *is* the binding's last use and the net closes there
instead. P6's identity holds as stated — the point the pass infers is the
point the human wrote.

**C11 came with S3 rather than after it**, and its predicate is P5's read
off the drop scan's own ownership walk rather than re-derived. Three
narrowings, each because the alternative is a double free rather than a
leak: an `await`/`try` wrapper takes the record over from the call
beneath it (capturing the inner call captures a PROMISE and hands the
destructor one); only a `&`/`&mut` view or a bare `self` receiver leaves
ownership with the caller; and an unresolved callee's conventions are a
signature nobody has read. The second is a **finding against std**, not a
choice: R3 says bare parameters are loans generally, but
`Option::replace`'s intrinsic surface declares `value: T` bare and then
KEEPS the value. Recording a temporary there destroys something the
callee stored, so the predicate stops at receivers and explicit views.
**The declaration is the real defect** — it should read `own value: T` —
and widening the predicate is what should follow it being fixed.

The refusal is also **narrower than `temporary-drop.md` §7.3's stated
set**. §7.3 named ternary and non-block `match`-arm expressions alongside
`&&`/`||`, correctly for the lowering it was pricing. Under S3's, an
`if`/`match` arm emits as a JS block with its own statement list, so a
temporary there has a statement position of its own and needs no
refusal. Only `&&`/`||` evaluate an operand inline with no block to hold
it, and only they are refused.

**The extern audit (S4).** Asked of every `[extern]` in std. The question
started as "does the host read this after the call returns" and the suite
sharpened it into two halves — **and is what it keeps a VILAN-owned
value**. 23 marked, across nine files:

| Surface | Declarations | Why it retains |
| --- | --- | --- |
| `browser/dom.vl` | `addEventListener` × 4 | the listener is a vilan closure, stored and called later — twice on `Element`, twice on `Window` |
| `reactive.vl` | `queueMicrotask` | the callback runs after the call returns |
| `browser/dev.vl` | `__hmr_register_teardown`, `__hmr_stash` | held to the next bundle; `__hmr_stash` holds ACROSS it and `hmr_take` reads it back |
| `browser/ui.vl` | `__chunk_arm`, `__chunk_load` | a value and two closures, held until the chunk resolves |
| `rpc.vl` | `__hmr_register_teardown`, `onmessage` / `onclose` / `onerror` | handler properties the socket keeps |
| `process/http.vl` | `createServer`, `listen`, `on` × 4, `close` | every node `EventEmitter` registration |
| `fetch.vl` | `body` × 2, `headers`, `signal` | request-init: a string, a `Bytes`, a header list, a signal, each kept until the fetch runs |

Left unmarked deliberately, and the reasoning is the audit's other half:
every read-through accessor and pure computation (`json`, `debug`,
`bytes`, `crypto`, `time`'s formatters) reads within the call; the
`File` / `Database` / `Watcher` method surfaces take `self` and the host
is done with it when they return; `Timer`'s `wait`/`cancel` settle within
their own suspension; and the HMR synthesized getters — §6.4's named
exemption, the 252 invisible uses in the website server — are excluded by
`TransferForm` already and need nothing here.

*Amended 2026-08-31 (A27 / kolt.local 037, `router.md` §5).* `std::dom`
grew the window listen target and the removable `listen` verb, which moves
two rows into one: `browser/router.vl`'s `window.addEventListener` hand-roll
is deleted — `ensure_wired` calls `window().on` — and `browser/dom.vl`'s
registrations go from two to four, one `on` and one `on_event` per target.
The count is 25, still across nine files. The two new
`removeEventListener` bindings that `listen`'s teardown rides are
deliberately **unmarked**, by the second half of the question: removal
hands the host a value it does not keep. `appendChild`'s lesson below is
the one that governs there, and the exhibit that drove this surface marks
both halves — the over-marking this audit exists to catch.

**`appendChild` is the case that taught the second half**, and it is
worth stating because it is the shape a future audit will reach for
first. The DOM genuinely keeps the child, so the first half of the
question says yes. But the child is an `Element` — a host handle vilan
neither allocates nor destroys, with no vilan-side lifetime for retention
to extend — so marking it bought no safety and cost real elisions: it
made a SIBLING aggregate opaque (the argument is `built[0]`, whose place
root is `built`) and put a deep copy back into the split fixture's
golden, caught by that gate. Retention extends the liveness of values
whose lifetime this compiler manages. A host handle has none, and marking
one only spends precision.

**Measured, after:** the copy-elision census is unmoved (parameters
joining the liveness walk cannot reach elision's answers — it gates on
`variables`, and `compute_view_origins` never keys a parameter), five
corpus goldens moved with runtime output proven identical line-multiset
and exit-code, and the fd staircase reads 0 / 0 / 0 where the leak read
1 / 2 / 7.

## 7. Tier B — reclamation without the host collector

**Stated out loud: on the JS backend the host GC stays.** Per-value RC
in emitted JS is a non-starter (no spare header word; boxing every
aggregate doubles allocation and de-optimizes V8's element kinds).
Everything in this tier is the WASM/native backend's design, using the
JS-measured operation counts as the workload model. Nothing here
touches user-facing semantics; a vilan program cannot tell which
reclaimer runs beneath it (drop timing is Tier A's, identical on both).

The census assigns the two ruled mechanisms to the corners they fit:

- **The owned tier (~93%): last-use + Perceus-class compiled RC, with
  the reuse analysis as the explicit make-or-break.** RC's inc/dec
  traffic prices ~4× *below* the deep copies it replaces on this
  workload (order-of-magnitude arithmetic, marked as such: ~410k cycles
  of copy per render today vs ~110k of count traffic) — **conditional on
  reuse/FBIP**, because vilan mutates in place and a write at `rc > 1`
  is a copy-on-write that puts the copies back. If reuse lands
  (`set_attribute`'s 1,171 allocs/render collapse to zero), RC is a
  large win; if it does not, RC is a wash. That risk is the tier's one
  open engineering question, and it is not resolvable on paper.
- **The non-owning tier (views + `Shared`, ~5% of derefs): generational
  references, essentially free.** ~1,140 checked derefs per render at a
  few cycles each — noise. This reconciles the claims-and-epochs
  rejection rather than overturning it: *all-dynamic* was rejected as
  the general model; here the check applies only where a claim is
  genuinely non-owning, which is also exactly `Arena`'s shipped regime
  (the "dynamic carry" the epoch paper ratified). `Shared` becomes the
  counted resource destruction.md Tier 2 already sketches — retain on
  clone, release on handle death riding Tier 1 machinery, `Weak` (C1)
  for liveness queries — and **closure environments become counted
  objects** per that sketch's fourth bullet, which §4's capture rule
  makes load-bearing.
- **Cycles: unidirectional by construction, verified by gate.** §5's
  five repairs make the reactive graph acyclic in measurement; the
  policy is to *keep* it so — an SCC-walk probe in the suite over a
  mounted exemplar app (the tooling exists from this session) rather
  than a cycle collector. `Weak` covers the deliberate back-reference;
  an accidental cycle under counted `Shared` is a leak with a
  diagnosis, not a crash — and the escape-hatch tier it can occur in is
  7.1% of allocations, measured.

### 7.1 Ship note (2026-08-29, Order 19 close): S1, S2 and S5 are BUILT

S1 (lane graph-repairs): all four repairs + the standing SCC gate
(`unmounted cycles=0` is the law; the mounted count recorded); A28's
leak pinned 25 → 0; the client half was symmetric and also leaking —
`ReactiveClient` gained `Disposable`, caller-less in std pending the
owner. The ownerless derivation is leak-as-today by deliberate choice
(strictness breaks two documented idioms); refusal recommended as a
future ruled breaking change. S2 (lane liveness-dataflow): the last-use
dataflow at copy elision — +69% elisions, 15 goldens moved as pure
`__clone` removals, the old syntactic guards deleted; spec §6.2 needed
no edit (it was already written to last-use). S5 (lane capture-spec):
§4's rule is spec §6.9, the tour corrected, C12 ENFORCED on a zero
census — and the build found C13, the view-parameter-through-storing-
callee escape, pinned ignored as §6.9's honesty limit. S3+S4 shipped in
wave 2 (§6.5's note). Remaining in this paper: S6+ (the native tier,
gated on a backend arc; the reuse spike first, as ruled).

## 8. Tier C — recorded, possibly never

Storable/returned first-class references — cliff 2, Rust's territory —
remain expressible later as an opt-in with annotations at exactly the
declaring boundary, and rev-1's permanent line ("storage in aggregates:
still no") stands until a feature demands otherwise. **Ruled "possibly
never" this session; recorded so the door's location is known.** Nothing
in Tiers A/B forecloses it.

---

## 9. Non-goals

Tracing GC on any backend (never argued in the record; now argued: it
forfeits (1)–(3), the reasons this session exists). Async drop (out,
not deferred — claims-and-epochs). Aliasing-XOR-mutability (rejected
knowingly, stands). Rust-style lifetime annotations as a general surface
(Tier C's door, closed). Linear (exactly-once) types. Changing `Shared`'s
JS representation. Any change to mR1–mR12's *rules* — this paper moves
*when*, never *whether*.

## 10. Slices

- **S1 — the graph repairs + the std leak** (V1–V3, V5; A28 fix-now).
  Buildable immediately, JS-visible win (the leak), prerequisite for
  Tier B's no-cycle gate. Includes `Event::target_value()`.
- **S2 — the liveness dataflow, pointed at copy elision.** Replaces
  `reference_count == 1`; no semantic change; the census sizes the
  prize. The dataflow's proving ground.
- **S3 — last-use disposal for the affine tier. SHIPPED 2026-08-29**
  (branch `lastuse-s3`) — the lowering, the loan extension rule,
  branch-join specialization, the conditional-temporary refusal, the
  ordering amendment, `memory.md` §6.8's edits, corpus goldens
  regenerated deliberately. Closes C11. §6's ship note carries the
  record. *Original scope: as written.*
- **S4 — the extern retention contract. SHIPPED 2026-08-29**
  (branch `lastuse-s3`, with S3) — spelling settled as a TRAILING FLAG
  on `[extern(..)]` rather than a form word (the attribute's arguments
  are matched positionally, so a form word needs an arm per
  combination; trailing position is also what makes the formatter's
  round trip byte-exact). 25 of std's externs marked; the audit table
  is in §6's ship note. *Original scope: as written.*
- **S5 — the capture rule into spec §6** (§4) + the tour correction +
  C12's view-capture enforcement decision.
- **S6+ — the native tier** (§7): gated on a backend arc existing;
  the reuse-analysis spike is its first, riskiest slice and should run
  before any commitment.

## 11. Test plan (per case, as always)

S1: the SCC-walk gate over a mounted exemplar (cycle count = 0 with
V1–V3/V5; planted back-edge reddens); A28's leak pinned by subscriber
count across 25 mount/dispose rounds (25 → 0). S2: elision count
golden over the corpus; byte-identical emitted semantics proven by the
suite. S3: the probe battery of this session becomes pins — the fd
staircases (straight-line, loop, serve-forever), P5's both-paths drop,
P6's `drop(x)` identity, E2/E3 red-first, the loan-extension unsoundness
plant (owner dropped under live projection must refuse), goldens moved
deliberately and listed. S4: the retaining-extern probe as the red-first
pin. S5: c01–c05 as capture-semantics pins; the tour fence recompiled.

## 12. Open questions for the owner

> **RULED 2026-08-28 (the owner): "All recs accepted."** (1) The capture
> rule specifies aliasing-as-shipped — §4's text enters spec §6, the tour
> is corrected. (2) Branch-join drop specialization; the conditional
> temporary is refused. (3) The extern retention contract is the
> attribute spelling (`[extern(retains)]`-shaped; the lane settles the
> exact token). (4) The ordering amendment is confirmed — reverse
> declaration order at scope end yields to last-use order, breaking,
> once. (5) Tier B's opening move is the reuse-analysis spike, and
> nothing else native is built before it proves out. S1–S5 are all
> unblocked; S6+ stays gated on a native arc existing.

Few, because the session already ruled the direction. Each with a
recommendation:

1. **The capture rule (§4): specify aliasing-as-shipped, or migrate to
   the documented copy?** Rec: **specify aliasing** — zero cost, no
   estate breaks, and the native consequence (counted environments) is
   already Tier 2's sketch. This is the largest single ruling left.
2. **Branch-join drop specialization vs tightening mR7** (§6.3). Rec:
   **specialization** — static, flagless, and it is what makes last-use
   total; tightening mR7 instead would refuse ordinary programs.
3. **The extern retention spelling** (§6.4): attribute
   (`[extern(retains)]`) vs convention (`own` parameter). Rec: the
   attribute — an extern's loan staying a loan preserves the caller's
   spelling, and the attribute is auditable.
4. **The ordering amendment** (§6.2) — confirm breaking the ratified
   reverse-declaration-order sentence. Rec: yes; last-use order is the
   truthful order, and the goldens move once.
5. **Tier B's sequencing**: accept the reuse-analysis risk as S6's
   opening spike (build nothing else native until it proves out)? Rec:
   yes — it is the one unknown the census could not price.
