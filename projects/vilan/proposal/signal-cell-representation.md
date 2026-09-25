# The signal cell's representation — `Shared` boxes, counted handles, or owner arenas

Tracker **C14** (filed 2026-09-14; RULED to a paper at Order 36's GO). Written by lane
`paper-native-36` of Order 36 on vilan `next` @`9b22ec36`; every probe is
`vilan 0.40.0 (9b22ec364)`, the toolchain at that sha in **both** install locations.
**No compiler change and no std change lands from this lane.** The build is Order 37's, on
§10's slices.

Related: **C1** (`Weak<T>`, OPEN, blocked on counting), **M66** (the lazily-stamped identity
intrinsic — perf-36 builds it this order), **A92** (the `.id` dedup key M66 replaces),
**M60** (`get`/`set` deep-copy), **A87** (`Owner::release`, declined 2026-09-11), **F1**
(native apps — the sibling paper, `native-apps.md`), `destruction.md` §10 (Tier 2, which
already specifies both candidates), `lifetimes.md` §3/§5/§7/§9, `leak-soak.md` §7.7/§7.8,
`ambient-owner.md`, `affine-moves.md` §9.1/§9.3/§9.4, `capture-clones.md` §9.4,
`claims-and-epochs.md` §5a/§5b, spec `docs/spec/memory.md` §6.1/§6.8/§6.9.

---

## 0. What the probes changed about the question

Five of C14's premises need amending before the design starts. Each is answered in place
below; they are collected here because they are what a build would hit first.

1. **The ghost is not a stale read — it is a live cell.** C14 says "a disposed owner's cells
   stay readable forever". Measured (§5.1, probe P1): after `owner.dispose()`, a `set` on the
   cell still *commits and notifies*, and the following `get` reads the NEW value. Disposal
   detaches subscribers; it does nothing whatever to the cell. So the behaviour change either
   candidate makes is larger than the item states.

2. **No cell in the program has an owner today.** `Owner::take<T: Disposable>` takes a
   `Disposable`, and exactly four types implement `Disposable` in the whole estate —
   `Subscription`, `Owner`, `ReactiveServer`, `ReactiveClient` (`reactive.vl:390,504`,
   `rpc.vl:2708,3073`). `SignalCell` is not one, and neither is `View` (ambient-owner's ship
   note removed its owner field and its `Disposable` impl). Representation (b) therefore does
   not *change a representation*: it **invents an ownership relation that does not exist**, at
   126 of the 154 std sites. That is the single biggest fact in this paper, and §4.2 prices it.

3. **The leak-soak harness cannot see a `Shared` cell, and is the wrong exit test.**
   `leak-soak.md`'s instrument is `leak_tally` + `mallinfo2` over the **Rust** process
   (`vilan-lsp`/`vilan-core`); §4.4 says so outright — "nothing here is inside Rust's memory
   model, and no counter in this repository can see it". The exit test C14 wants is the SCC
   gate: `a_disposed_exemplar_holds_no_reactive_cycle`
   (`crates/vilan-cli/tests/reactive_lifetimes.rs:287`) driving
   `crates/vilan-cli/tests/support/heap_cycles.js`, plus
   `derivations_detach_from_their_source_with_their_boundary` (`:148`, the A28 25→0 pin) and
   the three `b291`/`b292` owner pins (`:377`, `:450`, `:541`). §10 uses those.

4. **`lifetimes.md` §9 lists "Changing `Shared`'s JS representation" as a NON-GOAL**, ratified.
   C14 reopens it. This paper says so explicitly and gives the reason (§1): the item's premise
   is that the JS backend is where a native representation gets *verified*, which is a
   different claim from the one §9 refused (that the JS backend should pay for counting).
   §9's sentence should be amended to "changing `Shared`'s JS representation **for its own
   sake**" when this paper's recommendation is ruled.

5. **`destruction.md` §10 already decided most of this, and already says the two candidates
   are one object.** Verbatim: "`Shared`/`Weak` is a one-slot counted arena: `clone` = retain,
   `Weak` = the handle". Tier 2 specifies counted `Shared`, `Weak::upgrade`/`Weak::get`, the
   reconciled trap law, and counted closure environments. C14 is therefore not an open fork
   between two philosophies; it is a **granularity and build-order** decision inside a
   ratified design. §4.4 and §9 read it that way.

One more correction, to the brief rather than to the item: `Task<T>` is an `external struct`
over the host promise (`task.vl:18`) and holds **no `Shared` at all**. "Task results" are not
an escaping-cell class; the escaping classes are `std::memo` caches, rpc mirrors, and
`Draft`/`Optimistic` store values (§2.4).

---

## 1. The question, and the answer up front

`Shared<T>` is an `external struct` (`shared.vl:18`) whose JS backing is
`function __shared_new(value) { return { v: value }; }` (`transformer.rs:1273`), whose
`clone()` is the identity (`transformer.rs:7256`), and whose `read`/`write` are both
`cell.v` (`transformer.rs:7264`). Its own doc-comment opens "reference-counted shared mutable
state". **Nothing counts.** The host GC reclaims it; a cycle through it is the GC's problem;
and a cell whose owner is disposed is not merely readable but writable.

Neither property survives a backend with no tracing collector, which is F1's whole premise.
The question is what replaces it:

- **(a) a real counted box** — `Rc<T>`, retain on `clone`, release at handle death riding the
  Tier-1 last-use machinery, `Weak<T>` (C1) for the one back edge the graph genuinely needs;
- **(b) owner-attached generational storage** — the owner holds the slab, a cell is a handle
  plus its owner, disposal frees the partition wholesale, and a stale handle reads `None`.

**The answer: (a), built as `destruction.md` §10 already specifies it, with (b)'s generational
check kept for exactly the tier it already serves — `Arena`/`Handle`, shipped, unchanged.**
The census is why: 63 % of std's cells are owner-scoped, which sounds like (b)'s case until
you ask *which* owner, and find (finding 2 above) that no owner owns a cell today and that
inventing the relation costs an argument at 126 construction sites and a new refusal class
at every one of them. (a) costs a retain/release pair the last-use dataflow already computes
the schedule for, and one `Weak` at one place in std that is already the place the code's own
comment names. §9 gives the three sentences; §4 gives the reasoning; §10 gives the slices.

---

## 2. The census

### 2.1 The unit, and the classes

The unit is a **declaration site** of a `Shared<..>` cell: a struct field declaration, a
module-level `let`, or a local `let`. A construction slot (`pending = Shared::new([])`)
re-states a field declaration and is not counted twice; three `Shared`-typed *parameters*
(`process/ui.vl:93,113`, `rpc.vl:572`) pass a cell rather than declaring one and are excluded.
Raw totals, reproducible:

```sh
W=vilan/std/src
grep -rn "Shared" $W | wc -l              # 262 lines, 324 tokens
grep -rln "Shared" $W | wc -l             # 15 files
grep -rno "Shared::new" $W | wc -l        # 131 construction calls
```

Fifteen files mention `Shared`. **Twelve use it**; `shared.vl` declares it; `browser/dom.vl:5`
and `markdown.vl:18` mention it only in prose ("like `Shared`, it is an opaque handle";
"No `Shared`, no `View`, no closure anywhere"). C14's "13 std files" is right if `shared.vl`
counts and the two prose files do not — worth writing down because the two prose files are
the ones a mechanical sweep will keep tripping over.

Four classes, one per cell:

| class | definition | what a representation owes it |
|---|---|---|
| **R** root-scoped | a module-level binding; program lifetime | nothing — it never dies |
| **O** owner-scoped | dies with a disposal boundary: a view, a `bind_each` row, a turn's extent, an SSR request, a socket | a release at that boundary |
| **E** escaping | minted under one owner and read by another, or outliving the frame that made it | a *liveness answer*, not a lifetime |
| **F** frame-scoped | never outlives the call or builder that made it, and nothing subscribes to it | **nothing at all** — it wants a `&mut` local, not a cell |

### 2.2 std — 154 sites

| file | R | O | E | F | total |
|---|---:|---:|---:|---:|---:|
| `rpc.vl` | 3 | 47 | 19 | 3 | **72** |
| `reactive.vl` | 3 | 15 | 9 | 0 | **27** |
| `browser/ui.vl` | 0 | 22 | 0 | 0 | **22** |
| `process/rpc_server.vl` | 2 | 2 | 0 | 4 | **8** |
| `json.vl` | 0 | 0 | 0 | 7 | **7** |
| `binary.vl` | 0 | 0 | 0 | 4 | **4** |
| `process/ui.vl` | 0 | 4 | 0 | 0 | **4** |
| `ws.vl` | 0 | 4 | 0 | 0 | **4** |
| `time.vl` | 0 | 3 | 0 | 0 | **3** |
| `browser/router.vl` | 1 | 0 | 0 | 0 | **1** |
| `memo.vl` | 0 | 0 | 1 | 0 | **1** |
| `process/fs.vl` | 0 | 0 | 0 | 1 | **1** |
| **total** | **9** | **97** | **29** | **19** | **154** |
| | 5.8 % | 63.0 % | 18.8 % | 12.3 % | |

The nine **R** cells, in full, because a root-scoped cell is the one shape both candidates
leave completely alone: `reactive.vl:25` `next_subscriber_id`, `:120` `draining_turns`,
`:142` `releasing_turns`; `rpc.vl:1658` `reactive_sessions`, `:1709` `client_channels`,
`:1768` `next_channel`; `process/rpc_server.vl:840` `connections`, `:843` `next_connection`;
`browser/router.vl:55` `wired`.

The twenty-nine **E** cells, the ones that decide the semantics question of §5:
`reactive.vl` `SignalCell.value`/`.subscribers` (2 — the general case: a cell handed out of
the boundary that made it), `Draft` (4), `Optimistic` (3); `memo.vl` `Memo.entries` (1);
`rpc.vl` `LiveForward.holds` (1), `RemoteSource` (6), `KeyedRemoteSource` (7), `KeyLease` (3),
the two `channel_cell` locals (2).

`reactive.vl`'s 47 mentions resolve to **27** declaration sites — the difference is imports,
doc prose, and construction slots. C14's "47" is the mention count, and both numbers are
worth carrying: 47 is the size of the diff, 27 is the size of the design.

### 2.3 kolt — 13 sites, read-only at `~/code/kolt`

| file | R | O | E | entity |
|---|---:|---:|---:|---|
| `src/store.vl` | 4 | 0 | 0 | module `next_channel_id`/`next_message_id`, and the two `KoltStore` fields that **alias** them ("the module-level cells every instance shares, so a write through one connection's store is the broadcast to all") |
| `src/lib/overlay.vl` | 2 | 2 | 1 | `OverlayDriver.layers`/`.next_id` (app-level); `attach`'s `live_panel` and `relayout`'s `focused` (per-boundary); **`Overlay.driver`** — "An overlay is a handle, so the cell is shared by every copy of it" |
| `src/lib/input_system.vl` | 2 | 0 | 0 | `InputSystem.layers`/`.next_id` — one per app, held in the app context |
| `src/lib/rotary.vl` | 0 | 2 | 0 | `Rotary.next_key`/`.nodes` — per-component |
| **total** | **8** | **4** | **1** | **13** |

kolt's distribution is the inverse of std's: **8 of 13 are root-scoped**. An application uses
`Shared` for app-level singletons and for the handle idiom; the framework uses it for
everything. Neither candidate is visible to kolt at the surface, and §10's slices keep it so.

### 2.4 What the census says — four findings

**Finding 1 — the dominant use of `Shared` is not ownership. It is rule 1.**
Spec §6.1: "Every binding, assignment, argument pass, field initialization, and return
**copies** the value." A struct handed around by value therefore cannot carry mutable state in
a plain field, and every one of the 96 field sites is a cell for exactly that reason. The code
says so in its own words, repeatedly — `rpc.vl:1855`: "A `Shared` because the list is iterated
by VALUE: a copied `LiveForward` must still count into the one hold"; `reactive.vl:1252`:
"A CELL, like every other field, so copying a draft can never produce two values that disagree
about their own window"; `time.vl:329`: "The `Shared` cell IS required, and both directions of
the rule are…"; `process/fs.vl:722`: "A `Shared` cell is the shape the language leaves".
`shared.vl`'s own headnote says to "prefer an `Arena` + `Handle` whenever an owner exists" —
and the estate does the opposite, 154 times, because the thing it needs is not an arena. It is
**interior mutability behind a value-copied handle**. That is `Rc<RefCell<T>>`, not a slab.

**Finding 2 — 12.3 % of the cells want no cell at all.** The 19 **F** sites
(`json.vl`'s writer/reader, `binary.vl`'s two, `process/fs.vl`'s cursor, the four handshake
flags in `process/rpc_server.vl`, three locals in `rpc.vl`) are mutable state inside one call
or one builder that never escapes and that nothing observes. On a native backend they are a
`&mut` local and a struct field; they cost a heap allocation and an indirection today for no
reason but rule 1. Whichever representation is chosen, these 19 are a separate, cheaper item
(**FIND-1**, §11).

**Finding 3 — the escaping tier is small, named, and every member of it is a *handle*.**
Twenty-nine sites, and 19 of them are one shape: an rpc mirror (`RemoteSource`,
`KeyedRemoteSource`, `KeyLease`, `LiveForward`) whose whole point is that copies of the handle
count into one demand. The remaining ten are `Memo.entries` (a cache deliberately outliving
every maker's scope — "Nothing is evicted by itself, and for a remote handle nothing needs to
be"), `Draft`, `Optimistic`, and the general `SignalCell`. **Not one of them wants to die with
a boundary.** Representation (b)'s central promise — a stale handle reads `None` — is a
promise these 29 sites would have to be redesigned to survive.

**Finding 4 — the cycle is one edge, in one function, and its own comment names it.**
`observe` (`reactive.vl:817`, its doc comment at `:805`) already carries the repair: "The notify closure captures the
VALUE CELL, never the signal… Capturing `self` closed a back edge — signal → subscribers cell
→ list → subscriber → closure → scope → signal — so every subscription in the program minted
its own 6-node cycle." That is `lifetimes.md` §5's V1, fixed. What remains under counting is
the *shortened* edge: the value cell is reached from the subscriber closure, and the
subscriber list is reached from the cell, so `cell → subscribers → Subscriber → notify →
(captured) cell` is a 4-node cycle a refcount cannot collect. **One `Weak` at one line**
(`observe`'s `let cell = signal.value;`, `reactive.vl:819`) breaks it. `lifetimes.md` §5 measured the same thing
from the other side: "zero `Owner`s observed inside any cycle in any probe" — the spine is
acyclic; the cycles are all one layer down, at the cell.

---

## 3. What `Shared` is today, exactly

Eight analyzer sites key on the primitive (`analyzer.rs:9822` registers it in
`primitive_struct_ids` beside `List`, `Map`, `Set`, `NativeMap`, `Context`):

| site | what it decides |
|---|---|
| `hmr_transfer_form` `:9227` | a `Shared<T>` binding carries its payload across an HMR swap (`TransferForm::SharedPayload`) |
| `compute_transferable` `:9308` | a bare `Shared` **component** is not transferable-as-value |
| `is_shared_cell` `:19448` | `__clone` returns the object unchanged; `Shared::clone` is the identity |
| `shared_read_value_type_id` `:19887` | the concrete `T` of a `read()` in a storing position, for the clone pass |
| `shared_members` `:24560` | the four declarations (`new`/`read`/`write`/`clone`) B267's cell analysis keys on |
| `is_shared_handle` / `type_is_shared_handle` `:24596` | the type test the B267 slot walk filters with |
| the B267 union walk `:24685` | which slots can hold ONE cell (binding initializer, construction slot, assignment, `clone()`) |
| the intrinsic table `:56206` | `SharedNew`/`SharedClone`/`SharedValue`/`SharedWrite` |

Two of those eight are already a *static approximation of reference identity*: B267's union
walk exists because "`place_root` answers 'which binding is this path rooted at', which is not
cell identity" (`analyzer.rs:24614`). The compiler already reasons about which slots alias one
cell. A counted representation makes that reasoning *load-bearing at runtime* rather than only
at elision time; an arena representation makes it *unnecessary* (a handle is compared, not
inferred) — which is the one genuine argument for (b), and §4.2 weighs it.

What `Shared` guarantees today, and what it does not:

- **Guaranteed:** aliasing survives every copy rule 1 takes; `read()` is a value return, so
  storing one copies (M60's subject); `write()` is a `borrows self` projection, so a write
  through it is visible through every handle.
- **Not guaranteed, though the doc says otherwise:** counting. There is no count.
- **Not guaranteed, and nothing says otherwise:** that a cell dies. Nothing releases one.

---

## 4. The two representations

### 4.1 (a) A counted box — `Rc<T>` with deterministic drop, `Weak` for the back edge

`destruction.md` §10 specifies this already: "`clone()` = retain; a handle's death = release;
zero → the cell's value drops. Handle death is deterministic **because handles ride the Tier-1
machinery** (scope-end, moves) — the counting itself is what JS never needed and native
requires." Plus `Weak<T>` with a deterministic `upgrade() → None`, and its scoped twin
`Weak.get(&self): Option<&T> borrows self` from `claims-and-epochs.md` §5a.

**On JS, an `Rc` is the box that already ships.** `{ v: value }` gains a second field
(`{ v, n }`) only if a *counted mode* is built, and `destruction.md` §10 already classifies
that as "a verification tool, not a semantic". The zero-cost landing is: **the surface and
the graph shape change; the JS emission does not.** `downgrade()`/`upgrade()` lower to the
same object and a `!== undefined` test; the count is a no-op. That is what lets (a) ship and
be verified on JS before a native backend exists — the SCC gate (§0 finding 3) proves the
graph is acyclic, which is the property counting needs, and it proves it on the representation
that ships.

**What it costs the language.** Two ratified sentences have to move, and both are in
`affine-moves.md`:

- §9.3: "**R7: no conditional moves.** … This keeps end-of-scope ownership static: there are
  no runtime drop flags in v1." A refcount is not a drop flag — it is a *shared* count, not a
  per-binding per-path boolean, and R7's own reason (the compiler must know statically where a
  drop is emitted) survives: a release is emitted at the handle's last use, unconditionally, on
  every path. What does *not* survive is the implication people read off it, that no runtime
  value decides whether storage is freed. The sentence needs one clause: "no runtime drop
  flags **for bindings**; a counted handle's release is still statically placed, and only the
  *last* release frees."
- §9.4: "'A generic body cannot destroy a `T`' is now asked at every place the drop planner
  can schedule a destruction, which is an exhaustive list of three… **There is no fourth.**"
  Counting adds no fourth site (a release *is* a scope-end/last-use drop of the handle), so
  this one stands. It is (b) that breaks it — see §4.2.

**What it costs the graph.** Exactly one edge, at one line. `observe` captures
`let cell = signal.value;`; under counting that capture must be a `Weak`, because the closure
is stored in the cell's own subscriber list. Everything else `lifetimes.md` §5 named is
already repaired: V1 (fixed, the comment above), V2 (A28, fixed), V3 (`write_back_value`/
`write_back_draft`, fixed), V5 (`DuplexEnd.me` cleared, fixed). V4 is the semantic loop that
disposal dissolves.

**The repo has already run this experiment, and it is the strongest evidence on both sides.**
`leak-soak.md` §7.7: the const-pass interpreter is `Rc<RefCell<Scope>>` for environments and
`Rc<ClosureData>` for closures, whose `env` *is* the scope that declares it — structurally
identical to cell → subscriber → closure → cell. It leaked **+1,523.9 KiB per analysis** on
`page.vl` and **+45.8 KiB** on `views.vl`, invisible to `leak_tally` (every site nets zero),
visible only in glibc `uordblks`. The fix (§7.8, M8) is not a cycle collector: it is a
**`Vec<Weak<RefCell<Scope>>>` registry** forcing all eight scope-creation sites through two
constructors, plus a teardown that severs edges leaf-first — after which in-use growth is
**+0.3 B/analysis** on `page.vl`. Read forward: an `Rc` graph in this codebase leaks exactly
where a back edge is left strong, and is fixed by making that one edge weak, under a pin
(`const_evaluations_in_use_bytes_plateau`, `document.rs:19034`) that was planted red first.

### 4.2 (b) Owner-attached generational storage — arena + handle

The shape: the owner holds the slab; a cell is `Handle<Slot<T>>` plus the owner it was minted
in; disposal frees the partition wholesale and bumps its generation, so every outstanding
handle reads `None`. `std::arena` already ships exactly this at one level
(`Arena<T>`/`Handle<T>`, generational, branded, `get` → `Option<&T>`), and it is a good design.
Five things break when it is made the cell representation.

**(b1) No cell has an owner, so every construction site grows an argument.** §0 finding 2.
`SignalCell::new(value)` becomes `SignalCell::new_in(owner, value)` or reads an ambient one.
The ambient reading is not available: `ambient-owner.md` §2.1 is "**Strict-only — no absence
semantics**", and its coverage check is a whole-call-graph compile error, so making
`SignalCell::new` read `owner_scope` strictly turns **every module-level `Signal::new`** into a
compile error — including kolt's two (`store.vl:238`, `:240`) and the `selector`/`flatten`/`map`
idioms the ambient-owner paper itself documents as callable at module level. Reading it safely
(`get_safe`) puts the cells back in a root partition, which is a global slab that is never
freed — i.e. the status quo, with a downcast.

**(b2) `Arena<T>` is monomorphic and an owner holds many types.** An owner scoping cells of
`i32`, `str`, `List<Todo>` and `SignalCell<bool>` needs either one arena per `(owner, T)` pair
— a type-indexed map, which vilan has no spelling for and which on native is a `TypeId`-keyed
`Box<dyn Any>` — or a type-erased slot with a downcast per read. The probe (§4.3) took the
second and it works; the cost is that **every cell read is a downcast**, which is the one
operation the census says is hottest (`lifetimes.md` §3: ~1,140 non-owning dereferences per
render, of which the `Shared` `.v` reads are the bulk).

**(b3) A handle is data, so it needs a root to look up through.** Two integers are storable and
wire-sendable — that is `Handle`'s whole virtue — but they name nothing without the arena.
Either the cell carries a reference to the owner's arena (which is a counted box again, one
per owner instead of one per cell field: a real reduction, and not an elimination), or the
slab is a program-wide thread-local partitioned by owner (the probe's choice). The second
keeps handles pure data and moves the count to zero; it also makes every read a
thread-local access plus three generation comparisons, and it makes the slab a root that no
teardown ever shrinks below its high-water mark.

**(b4) It adds the fourth destruction site `affine-moves.md` §9.4 says does not exist.** A
wholesale partition free is a destruction the drop planner never scheduled, of values it never
saw. For data that is only a policy question; for a `resource` it is a soundness one, and
§9.4's completeness claim ("`plan_scope` writes `dropped` and `overwrites` and nothing else")
has to be amended rather than merely re-read. (a) needs no such amendment.

**(b5) The 29 escaping cells are the design's counter-examples, not its edge cases.** §2.4
finding 3. A `std::memo` cache whose entries go stale when the boundary that first asked for
them is disposed is not a cache; `memo.vl`'s headnote is explicit that "a released mirror
re-mints itself on the next lease while painting its cached value meanwhile", and a `None`
read deletes the "meanwhile". An rpc mirror whose `count`/`released`/`leased` cells go stale
under one holder's disposal loses the lease arithmetic A92 built. `Draft`/`Optimistic` hold the
rollback target across the very boundary a route switch disposes.

**What (b) genuinely buys, and it is not nothing.** Cell identity becomes *data*, not an
inference — which retires B267's union walk, gives M66's identity for free (§7), makes a cell
wire-sendable the way `claims-and-epochs.md` §6 makes an arena handle one, and removes every
cycle by construction because a handle is not a pointer. Disposal becomes O(1) in the cells.
And the probe shows the handle is **16 bytes, `Copy`**, so rule 1's copy of a cell becomes
free rather than a refcount bump.

### 4.3 The probe — both representations, built and run

Reproduction: `native-apps-probe/` (beside this paper), `cargo 1.90.0`, `rustc 1.90.0`. The vilan
source is `probe/board.vl` (62 lines: two structs, a `List`, a bare-`self` method, a closure
capturing a binding, a `SignalCell` with a subscriber, an `Owner`). Both Rust translations are
hand-written from it with no optimisation the shipped last-use pass does not already compute.

```
$ vilan run probe/board.vl                    # vilan 0.40.0 (9b22ec364)
2 3 2 2 99
$ ./target/debug/probe_rc                     # representation (a)
2 3 2 2 99 · identity=1 · strong=1 weak=1 · after-drop-upgrade-is-none=true
$ ./target/debug/probe_arena                  # representation (b)
2 3 2 · identity=Some(1) · 2 · after-dispose-get=None
  cell-live=false owner-live=false · root-cell-live=true
  handle-size=16 owner-size=8
```

Both compile clean and both reproduce vilan's five printed lines up to the last one. What
separates them is the last line, and it is §5's whole question: **(a) prints `99`, matching
vilan today; (b) prints `None`.**

Three findings the probe produced that paper alone would not have:

- **R-1 — a closure crossing a parameter boundary must be boxed at the boundary.** `sub` uses
  its observer twice (stored in the subscriber list, then called once immediately). Taking it
  as `impl Fn(T)` moves it on the first use and fails to compile (`E0382`, reproduced). Every
  vilan closure parameter that is both stored and called lowers to `Rc<dyn Fn(..)>`, not
  `Box<dyn Fn>` and not a generic. This is `destruction.md` §10's "counted closure
  environments" bullet arriving from the other direction, and it is a *fact about the emitter*,
  not about the cell.
- **R-2 — spec §6.9 forces a shared cell per mutably-captured binding.** "A closure captures
  bindings, not values… a write on either side is visible on the other." `seen` in `board.vl`
  is pushed to inside the closure and read outside it, so both translations need
  `Rc<RefCell<Vec<i32>>>` for it. **The cell representation question is therefore larger than
  `SignalCell`**: it is the representation of every captured mutable binding in the language,
  and `Shared` is only the part of it that has a name.
- **R-3 — (a)'s `Weak` is measurable, (b)'s staleness is measurable, and both work.** After
  `owner.dispose()` the probe's weak count falls from 2 to 1 (the subscriber closure holding
  the weak edge is genuinely freed), and after dropping the last strong handle
  `upgrade()` is `None` deterministically. Under (b) `is_live()` is `false` for the
  owner-scoped cell and `true` for the root-partition one, which is the "root-scoped cells
  survive" rule §2.2's nine R sites need.

Cost datum for F1 as well: a clean `--release` build of the two-binary, ~700-line crate is
**1.15 s user + 0.35 s sys**; the binaries are 475 KB and 493 KB.

### 4.4 They are the same object at two granularities

`destruction.md` §10, verbatim: "`Shared`/`Weak` is a one-slot counted arena: `clone` =
retain, `Weak` = the handle". The choice is not counting-versus-generations. It is:

| | (a) | (b) |
|---|---|---|
| granularity of the reclaimed unit | one cell | one owner's partition |
| what says "is this alive?" | a count reaching zero | a generation mismatch |
| what the cell's value is | a pointer (1 word) | a handle (16 bytes, `Copy`) |
| who decides the lifetime | the last holder | the owner |
| what breaks a cycle | `Weak`, at one line | nothing — there is no pointer |
| ownership relation required | the one that exists (last use) | **a new one, at 126 sites** |
| destruction sites in the planner | 3 (unchanged) | **4** |
| read cost | a deref | a thread-local + 3 compares + a downcast |

vilan already ships (b) where (b) is right: `std::arena`, for "stable, deletion-safe identities
for values of any type `T`" — a graph's nodes, a server's entities, anything whose identity
must cross a wire. It ships (a)'s *surface* already too, in `Shared::clone`, which
`affine-moves.md` §9.1 calls "a refcount handle — the opposite of a payload copy". The
recommendation is to finish the one the estate is written in.

---

## 5. A read after the owner's disposal

### 5.1 Today — measured, and worse than the item says

Probe P1, `probe/board.vl` lines 55–61, run above:

```vilan
owner.dispose();
count.set(99);          // commits, and notifies (nobody is listening)
print(seen.len());      // 2 — the subscriber is detached
print(count.get());     // 99 — the NEW value
```

Disposal runs the owner's cleanups; each cleanup disposes a `Subscription`, which removes an
entry from a subscriber list. The cell is untouched. So today's answer is not "a ghost value"
but "**the cell is a fully live, writable object that has merely lost its audience**". Two
consequences the estate depends on: an escaping cell keeps working (§2.4 finding 3), and a
`set` after disposal is silent rather than an error — B291's pin
(`reactive_lifetimes.rs:377`) records exactly this shape, expecting
`["at-registration=1", "after-disposal=0", "subscribers=0", "after-second-dispose=0"]`.

### 5.2 Under (a)

**A read succeeds while any holder lives, and the holder is the reader.** That is the
definition of a count. A disposed owner drops its cleanup closures, releasing whatever handles
they held; if that was the last one, the cell drops then, deterministically, and nothing can
read it because nothing names it. If the app still holds the cell — the `Memo` entry, the
mirror, the module-level binding — it reads the value, exactly as today.

So (a)'s answer to §5.1 is **"unchanged"**, and that is its main behavioural virtue: the 154
sites keep their semantics and the migration is a representation change, not a redesign. The
one new observable is `Weak::upgrade() → None`, and it is new *surface*, reached only by code
that asked for a weak reference.

### 5.3 Under (b)

**A read after disposal is `None`.** That is the design's point and its bill:

- `Source::get(self): T` cannot keep its signature. It becomes `Option<T>`, or it panics, or
  it answers a stale-but-remembered value (which is the ghost, i.e. (b) buying nothing). An
  `Option<T>` return propagates into `Source`, `Signal`, `MaybeSignal`, every `bind_*` in both
  `ui` twins, `map`/`combine`/`flatten`/`selector`, and every user call site: kolt reads a
  signal in ~200 places.
- A `set` after disposal is silently dropped (the probe's behaviour) or refuses. Both are
  changes to B291's documented "a late registration is not an error — it is the async shape".
- The 29 **E** sites need redesign, not migration (§2.4 finding 3).

(b)'s semantics are *better* in the abstract — a stale read is a bug caught rather than a
ghost propagated — and the estate is not written for them.

### 5.4 The one thing both must keep

`ambient-owner.md` §1 proves the owner reference "outlives the syntactic extent by design,
carried in ordinary closure state" (stored callbacks, post-`await` registrations). Its static
fence answers *"is an owner syntactically reachable"*, never *"is this owner still alive"* —
§2.1 says "Nothing ever observes 'no owner', so nothing needs `Option` semantics", which is
about **absence**, not about **disposal**. B291's `disposed` flag is the shipped answer to the
second question and it is a runtime one. Under (a) that flag stays what it is; under (b) it is
subsumed by the partition generation. Either way the paper's law is: **a disposed owner is a
different condition from an absent one, and only the second is a compile error.**

---

## 6. `Owner`, `Signal`, `Memo`, `RemoteSource`, and the rest, in one pass

| type | cells | under (a) | under (b) |
|---|---|---|---|
| `Owner` (`reactive.vl:455`) | `cleanups: Shared<List<|| void>>`, `disposed: Shared<bool>` | one `Rc<RefCell<OwnerBody>>`: two allocations become one, and `dispose` drops the cleanup closures, which is what releases the handles they hold | the owner IS the partition; both cells become partition fields, 8 bytes of handle |
| `SignalCell` (`:758`) | `value`, `subscribers`, `id` | one `Rc<RefCell<CellBody>>`; `id` per §7 | a 16-byte handle; slot holds value + subscribers + identity |
| `Subscription` (`:361`) | `subscribers` (an alias of the cell's), `release` | the alias is a second strong handle to the *subscriber list*, which must not keep the cell alive → **`Weak`, the second one** | a handle + an id, plain data |
| `Turn` (`:81`) | 5 | one body; the turn is extent-scoped so the drop is at the extent's end | a partition per turn — plausible, and the one place (b) is genuinely attractive |
| `Selector` (`:999`) | `cells`, `current` | one body; entries removed by `defer_to_owner` as today | the map's *values* are cells in other partitions — a stale entry is exactly the row-died case, and reads `None` correctly |
| `Draft` (`:1240`) / `Optimistic` (`:1483`) | 4 / 3 | one body each | **E** — needs an owner it does not have |
| `Memo` (`memo.vl:44`) | 1 | one body, held by whoever holds the memo | **E** — a cache scoped to a boundary is not a cache |
| `RemoteSource` (`rpc.vl:3188`) / `KeyedRemoteSource` | 6 / 7 | one body per mirror; `LiveForward.holds` becomes an honest count | **E** ×19 — the lease arithmetic is the counter-example |
| `Task<T>` (`task.vl:18`) | **none** | unchanged — an `external struct` over the host promise | unchanged |
| `View` | browser: none (an `Element` handle); process: 3 | process twin's three become one body; a request-scoped tree | the SSR `View` is the one shape a per-request partition fits perfectly |

Read down the (a) column: every row is "one allocation instead of N, same semantics". Read
down the (b) column: four rows are a redesign and two are an improvement.

---

## 7. The identity stamp (A92, M66)

`SignalCell.id` exists because "vilan has no reference equality, and a cell is exactly the kind
of thing two holders need to recognise as the SAME one" (`reactive.vl:761`). Its consumer is
A92's dynamic exposure: a reply carrying a source the connection already exported answers the
channel it already minted. M66 (R8, built by perf-36 this order) replaces the eager
`fresh_id()` with a lazily-stamped intrinsic, `Shared::identity` — `o.__id ??= next++` — which
returns twelve corpus goldens to their pre-A92 shape.

**Under (a): M66 is the right answer and survives untouched.** The intrinsic stamps the box on
first read; a counted box has a stable address for its whole life, and stamping is a lazy
memoised property of it. The probe's `identity()` prints `1` and costs nothing until asked.
M66 is, in fact, the *first slice of (a)* arriving early: an intrinsic that gives reference
identity on the `Shared` box is exactly the operation a counted box needs and the plain-object
box does not deserve. C14's paper should say so, and Order 37 should build on it rather than
around it.

**Under (b): the stamp is redundant — the handle *is* the identity.** Two handles are equal iff
they name one cell, by construction, and a `[derive(Wire)]` handle crosses the wire as a name
(`arena.vl`'s headnote, `claims-and-epochs.md` §6). A92's dedup key becomes
`(partition, partition_generation, index, generation)` compared structurally, `LiveForward.key`
becomes the handle, and M66 is deleted rather than built. That is (b)'s cleanest win and it is
worth saying out loud in the recommendation: **choosing (a) means keeping an identity stamp
forever; choosing (b) means never needing one.** It does not outweigh §4.2, but it is the
argument (b) has.

---

## 8. Prior art, briefly

- **Solid (JS) and Leptos (Rust) — ownership arenas.** Solid's `createRoot`/`getOwner` is the
  design `ambient-owner.md` already took: an owner tree, cleanups per owner, signals *not*
  owned by it. Leptos moved the other way across its 0.x line — from an arena of typed slots
  keyed by `(runtime, index)`, where a disposed scope's signal id read as a panic or `None`, to
  `ArcRwSignal`/`RwSignal` with real `Arc` and a separate arena only for the `Copy` convenience
  handle. The migration's public reason is the one §4.2 (b5) reaches independently: arena
  handles make *escaping* state (a resource, a cached fetch, a store handed to a route) a
  lifetime bug that the type system cannot see. It is the strongest external evidence available
  and it points at (a).
- **Rust `Rc`/`Weak` reactive graphs** (futures-signals, druid's `Env`/`Widget` tree, and this
  repo's own interpreter, §4.1): the pattern is universal and so is its failure mode —
  whichever back edge is left strong is the leak. The discipline that works is not a collector;
  it is naming the back edge once and making it weak, with a gate that proves it.
- **Slint's property system**: properties are `Rc`-boxed values with a dependency list of
  `Weak` back-pointers, and dirty propagation walks the weak list dropping dead entries.
  Slint's C++/Rust dual backend is the closest live analogue to vilan's two-backend problem,
  and it chose counting.
- **Swift**: `destruction.md` §10's "counted closure environments (Swift's model)" is cited
  already; the probe's R-1 finding is the same constraint arriving from rustc.

Nobody in this list runs an owner-scoped arena as the *general* cell representation. The ones
that tried moved off it.

---

## 9. Recommendation

**Build (a): `Shared<T>` becomes the counted resource `destruction.md` §10 already specifies —
retain on `clone`, release at the handle's last use riding Tier 1's shipped dataflow, `Weak<T>`
(C1) unblocked and used at exactly two places in std (`observe`'s captured cell, and
`Subscription`'s alias of the subscriber list). Keep `Arena`/`Handle` exactly as they ship, for
the tier they already serve.** The census is the argument: 63 % of std's cells are owner-scoped
but **no owner owns a cell**, so (b) does not change a representation, it invents an ownership
relation at 126 sites, grows an argument on every construction, turns `Source::get` into
`Option<T>`, and makes the 29 escaping cells — memo caches, rpc mirrors, drafts — into
counter-examples rather than edge cases. **(a) is a representation change with no surface
change: the estate's semantics are unchanged (§5.2), the one back edge that forces `Weak` is
named in `observe`'s own comment, and the repo has already run this exact experiment in its
own interpreter and fixed it with one weak edge under a planted-red pin.** The JS backend
verifies it for free — an `Rc` there is the `{ v }` box that already ships with a no-op count,
so the SCC gate `a_disposed_exemplar_holds_no_reactive_cycle` proves the property counting
needs on the representation that ships, before any native backend exists.

---

## 10. Slices

Each slice is buildable, suite-gated, and lands its docs in the same commit. Sizing is against
this lane's measurements; the exit test is named, and each new pin is planted red first
(vilan's CLAUDE.md rule).

**S1 — the frame-scoped subtraction (FIND-1). Size: S.**
Retire the 19 **F** cells: `json.vl`'s writer/reader, `binary.vl`'s two, `process/fs.vl`'s
cursor, `process/rpc_server.vl`'s four handshake flags, `rpc.vl`'s three locals. Each becomes a
`mut` local or a `&mut self` field. Independent of the representation decision, and it is the
cheapest 12 % of the census.
*Exit test:* `-p vilan-core` green; `-p vilan-cli --test service_layer`; no golden moves
outside the emitted `__shared_new` count, which drops by 19 construction sites.

**S2 — `Weak<T>`: the surface, JS-lowered, C1 unblocked. Size: M.**
`Shared::downgrade(&self): Weak<T>`; `Weak::upgrade(): Option<Shared<T>>`;
`Weak::get(&self): Option<&T> borrows self` (`claims-and-epochs.md` §5a). On JS, `downgrade`
is the identity and `upgrade` is `Some(cell)` — the *shape* lands and the *deterministic
`None`* waits for counting, documented as such at the type, exactly as `destruction.md` §10
says ("Ships with counting"). This is the slice that makes the graph change expressible.
*Exit test:* new pins in `crates/vilan-core/tests/inference/` for the three signatures and for
the second-class `get` view; `-p vilan-cli --test reactive_lifetimes` unchanged.

**S3 — std's two back edges become weak. Size: S. BREAKING to nothing.**
`observe`'s `let cell = signal.value;` → a weak capture; `Subscription.subscribers` → a weak
alias. Two lines and their comments.
*Exit test:* `a_disposed_exemplar_holds_no_reactive_cycle` still `cycles=0` **and the mounted
SCC count drops** (recorded, not asserted, per its own contract);
`derivations_detach_from_their_source_with_their_boundary` still 25→0; the three `b291`/`b292`
pins unchanged. Plant: restore the strong capture, watch the mounted count rise.

**S4 — the counted representation, native only; JS keeps the no-op count. Size: L.**
`Shared`'s four intrinsics gain a counted lowering behind the backend; the JS lowering is
byte-identical to today. `Owner`'s two cells become one body. This is the slice that cannot
land before F1's backend probe has a backend to land in — it is listed here because it is what
S1–S3 are for, and because its size is the number Order 37 needs.
*Exit test:* a native leg of the reactive suite (F1 §S1's exit test is its precondition); on
JS, zero golden movement.

**S5 — the JS counted mode, as an instrument. Size: M. Optional.**
`destruction.md` §10's "optional JS counted mode (debug builds)… a verification tool, not a
semantic": `{ v, n }` under a debug flag, with a leak report at teardown naming the cells whose
count never reached zero. This is what turns the SCC gate from "no cycle among what the test
kept rooted" (its honest, narrow claim — `heap_cycles.js` cannot see what GC already took) into
a positive statement about release.
*Exit test:* the counted mode run over the SCC exemplar reports zero non-zero counts after
`dispose`; planted red by restoring S3's strong capture.

**Not a slice: deleting `Shared`.** C14 is right — "`Shared` stays for genuinely diffuse
ownership (its own doc's case) and gains real counting under a native backend". §2.4 finding 1
says the doc's case is 0 of 154 sites in std today, which is worth recording at the type, but
the type stays.

---

## 11. Open questions, each with a recommendation

**Q1 — does `Source::get` ever return `Option<T>`?** *Rec: no, and this paper's
recommendation is what avoids it.* Under (a) it never needs to. If (b) is ever ruled, this is
the question that must be answered first, and the answer is an estate-wide breaking change
(§5.3).

**Q2 — is the `Rc` count observable to vilan code?** *Rec: no.* `Shared` gains no `count()`
member. A count is an implementation of lifetime, not a value; exposing it would make a
program's correctness depend on elision, which spec §6.2 forbids ("elision is an optimization,
never observable"). The debug counted mode (S5) reports counts to the *developer*, not to the
program.

**Q3 — do closure environments become counted objects, and when?** *Rec: yes, with S4, per
`destruction.md` §10's fourth bullet, and the probe's R-1 finding is the reason it cannot be
deferred.* A closure parameter that is both stored and called must be `Rc<dyn Fn>` at the
boundary; a closure capturing a counted handle holds a retain. This is the "single reason
`Shared` cannot join Tier 1" and it is unchanged by this paper.

**Q4 — `Owner::release` (A87), reopened?** *Rec: still no.* A87 was declined 2026-09-11
"until a caller appears". Counting does not produce one: releasing without raising `disposed`
is orthogonal to how the cells are represented. Recorded so the next reader does not have to
re-derive it.

**Q5 — M60's deep copy, under counting?** *Rec: unchanged, and re-measure after S4.*
`get()`/`set()` deep-copy the value (`__clone` over the whole container) and that is spec
§6.1's value return, not a representation artefact. Counting makes the *cell* cheap to copy and
leaves the *value* exactly as expensive. M60 stays its own item; the census note it wants is
§2.4 finding 1's sentence.

**Q6 — does M66 land as written, given §7?** *Rec: yes, unchanged, and perf-36 should not
wait for this paper.* Under the recommendation the intrinsic is permanent and correct; under
(b) it would be deleted later. Building it now costs nothing in the (b) world and is required
in the (a) one.

**Q7 — what happens to B267's cell-union walk under counting?** *Rec: it stays, and gets
cheaper to justify.* The walk approximates cell identity statically for elision. Under counting
the runtime answer exists, so a wrong approximation becomes a performance bug rather than a
correctness one — which is a strictly better failure mode, and worth a sentence at
`analyzer.rs:24614`.

**Q8 — a `Store<T>` trait, per `destruction.md` §10's last bullet?** *Rec: not yet.* §10 says
"extract the trait when Tier 2 builds, not before". S4 is Tier 2 building; the trait is S4's
question, not this paper's.

---

## 12. What this closes, and what stays

**Closes.** C14's design question, with a recommendation and slices. C1's blocker is refined
from "Tier 2 refcounting, the native arc" to "S2 lands the surface; S4 lands the determinism" —
`Weak` becomes buildable this coming order rather than waiting on a backend. F1's second pillar
("memory without a GC") gets its answer, so `native-apps.md` §2 can cite a decision instead of
a fork. M66's shape is confirmed as permanent rather than provisional.

**Stays open.** The 29 escaping cells keep the semantics they have; nothing in the
recommendation changes what an rpc mirror or a memo entry does. `Arena`/`Handle` ship unchanged
and gain a paragraph in `shared.vl`'s headnote saying which of the two to reach for (§2.4
finding 1 says the headnote's current advice is backwards for 154 of 154 sites).
`affine-moves.md` §9.3's "no runtime drop flags in v1" needs the one-clause amendment in §4.1
when S4 is ruled; §9.4's three-destruction-sites claim survives. `lifetimes.md` §9's non-goal
sentence needs the words "for its own sake". The B267 walk, M60, and the identity stamp all
stay where they are.

**New items this paper proposes** (evidence in §2.4 and §4.3):

- **FIND-1** — the 19 frame-scoped `Shared` cells that want a `mut` local. S1 above. `perf`.
- **FIND-2** — `shared.vl`'s headnote advises "prefer an `Arena` + `Handle` whenever an owner
  exists"; measured, 0 of 154 std sites and 0 of 13 kolt sites follow it, because the thing
  they need is interior mutability behind a value-copied handle, not an arena. Re-word.
  `documentation`.
- **FIND-3** — a closure parameter that is both **stored and called** must lower to a counted
  boxed `Fn` on any non-JS backend (probe R-1, `E0382` reproduced). Record it against the
  emitter design before F1's backend slice, not after. `design`.
- **FIND-4** — spec §6.9's "a closure captures bindings, not values" means every mutably
  captured binding is a shared cell on a native backend (probe R-2). This is a larger surface
  than `Shared` and it has no item. `design`.

---

## 13. As built (Order 37, lane native-a-37, 2026-09-17)

**R1 ruled (a)** — the counted `Shared` with `Weak` at two std sites, `Arena`/`Handle`
unchanged. S1–S3 landed on JS; S4 waits for F1's backend (S1a shipped the same order,
native-b-37); S5 is queued as the instrument §10 S3's exit test turns out to need.

**S1 — eight of nineteen** (`c5b98491`). `process/rpc_server.vl`'s `settled`/`expired`
(the authorize bound) and `closed`/`greeted` (the connection latches); `rpc.vl`'s
`connection`/`refused` (the dial handshake), the keyed mirror's per-patch `fault`, and
`connect_split`'s own `connection` — a closure captures the *binding* (spec §6.9), so
sibling closures in one frame already share a `mut` local. std `Shared::new(` sites
136 → 128 (§2.2's 131 was counted at `9b22ec36`); the corpus goldens' `__shared_new`
stayed at 127 (no corpus program reaches `std::rpc`); ≈587 Ir per retired cell per round
under `node --jitless`, indistinguishable under the JIT (V8 escape-analyses the box).
**The other eleven are blocked by the language, not by effort**: `json.vl`'s six and
`binary.vl`'s four are the Wire visitor's state, and `Serialize`/`Deserialize` declare
every method on a by-value `self` — moving the receivers to `&mut self` and
`Wire::describe`/`rebuild` to `&mut S`/`&mut D` is a breaking public-surface change,
proven to compile in a probe with zero `__shared_new`, filed as **A108** for Order 38;
`process/fs.vl`'s `Reader.cursor` is forced because `next` awaits and a `&mut` view may
not cross a suspension. Two census corrections: `connect_split`'s `connection`
(`rpc.vl:260`) is F, filed here inside an O group — the F class was **20** on this
paper's declaration-site unit; and `census.py` is a hand-curated table, not a
classifier, so the pin that holds the line is a committed per-file `Shared::new(`
count with the class each file's cells belong to (`crates/vilan-cli/tests/shared_census.rs`).
D8 landed with S1: `shared.vl`'s headnote and the memory-model tour say what §2.4
found.

**S2 — `Weak<T>`** (`1379ccdd`, `f7fa4542`). `Shared::downgrade(&self): Weak<T>`
(`&self`, as §10 and destruction.md §10 spell it — it says "adds no holder" in the
signature), `Weak::upgrade(self): Option<Shared<T>>`, `Weak::get(&self): Option<&T>
borrows self`. The lowering allocates **no wrapper**, so a native representation stays
free to be a second word on the cell rather than a box around it: `downgrade` is the
receiver, `upgrade` is `[0, cell]`, `get` is `[0, cell.v]` (the shape `Arena::get`
already emits). The one analyzer seam that was genuinely missing: a view is a property
of an *expression*, not of a `Type`, so a bodiless declaration could not say
`Option<&T>` where any checker could see it — `Some(let view)` over `weak.get()` bound
a value wearing an ampersand and `out.push(view)` into a `List<&i32>` was allowed where
the identical `Arena::get` program is refused; `Weak::get` is the one extern with that
return and gets the one exception, found by the primitive's identity. Eighteen pins in
`inference/weak.rs`. No HMR arm (a bodiless `external struct` is already excluded
conservatively — an arm was tried, measured redundant, removed), no interpreter arm
(`[0, cell]` and `cell.v` are shapes it already evaluates), no hover site.

**A miscompile found on the way** (`7d9427dc`): a `Shared` handle bound by a **match
capture** aliased the cell it read from. B267's walk follows a handle between four slot
forms and joins what it cannot follow to `Unknown`; a pattern capture has no
initializer to follow, and `Weak::upgrade` is the first API in the language that binds
a `Shared` handle through one — the gap had been unreachable. Measured: `mut copy =
strong.read(); cell.write().push(9); print(copy.len())` printed 2 where the direct
form printed 1. An initializer-less capture typed as a `Shared` handle now joins
`Unknown`, as a `Shared`-typed parameter already did; pinned; no golden moved.

**S3 — the two back edges weak** (`7d9427dc`). `observe` captures
`signal.value.downgrade()` and upgrades on each notify (`upgrade`, not `get`: the
observer takes a value and `read()` is the spelling that copies one out);
`Subscription.subscribers` is a `Weak<List<Subscriber>>` that `dispose` upgrades before
detaching; `Subscription::teardown`'s signal-less shape mints a cell that dies with the
call, whose weak answers `None` once anything counts. **§10 S3's exit test is
unachievable on JS, by construction, and this section corrects it**: `downgrade` lowers
to the identity, so the emitted heap graph is unchanged — the SCC gate reads mounted
`reachable=243 cycles=2` and unmounted `reachable=122 cycles=0` on both sides, and the
brief's plant (restore the strong capture, watch the mounted count rise) cannot move
either. §4.1 ("the surface and the graph shape change; the JS emission does not")
already said so. **C14 S5's counted JS mode is the first instrument that can see the
difference**, and its exit test is the one §10 S3 wanted. Cost, measured: +590.6 Ir per
notification (+11.7 %) on the interpreter tier for the `[0, cell]` array and its branch,
indistinguishable under the JIT — a JS cost that buys a native property, which S5 should
re-measure and decide whether the weak edges want a counted-mode-only spelling. Nine
corpus goldens moved (reactive's body), `__shared_new` in the goldens 127 → 129 —
`observe` is now emitted twice in two goldens because the body-sharing key does not
normalize local gensyms (**M80**). Three S3 pins, one of them §5.2's "a `set` after
`owner.dispose()` still commits" (`after-dispose=99`), which had been unpinned.

**Q7 answered in the tree** — `compute_shared_cells`'s headnote (`baefa933`) now says
what a counted `Shared` does to B267's walk: today the approximation is load-bearing for
*correctness* (nothing counts, so nothing at runtime knows which handles name one cell,
and every hole in the `Unknown` sink is a copy that should have been taken — the
match-capture hole above was exactly one); under counting the walk becomes an *elision*
heuristic over a fact the runtime also holds. The headnote's stale worked example
(`Subscription`'s `subscribers` initialized from `SignalCell`'s — a union S3 removed) is
fixed in the same commit. lifetimes.md §9's non-goal carries the clause §12 asked for.

**Numbers at a glance.** std `Shared::new(` 136 → 128 · goldens' `__shared_new`
127 → 129 · SCC gate 243/2 mounted, 122/0 unmounted, unchanged · `derivations_detach…`
25 → 0 unchanged · `-p vilan-core` 5,914 passed on the lane's tree.

## 14. As built (Order 38, 2026-09-21) — the ten blocked cells retired, and three added on purpose

**A108 (lane wire-38, 141bea80) retired the ten cells §13 filed as blocked** — json.vl's six and
binary.vl's four — by moving `Serialize`/`Deserialize` to `&mut self` and `Wire::describe`/`rebuild` to
`&mut S`/`&mut D` (BREAKING; the value stays by-value `self`, and inside a `describe`/`rebuild` body the
parameter already IS the view, so nested forwarding is bare — seventeen std impls and both derive
emitters at one line each). std `Shared::new(` 128 → 118; the F class is one file, `process/fs.vl`'s
`Reader.cursor`, and §13's reason for it holds unchanged (`next` awaits; a `&mut` view may not cross a
suspension) — which is why the receiver change reached the other ten and not that one. The census pin
asserts the ABSENCE in both codec files and the ten plain field declarations by spelling
(`VISITOR_STATE_UNBOXED`). **The wire did not move**: the handle-free service hash `78bdada7` is
byte-identical and every frame-level pin is green. Two corpus goldens moved (crypto.vl −227 B, time.vl
−310 B) and both print byte-identically; `__shared_new` in the goldens 129 → 111. Kolt migrates by
REBUILDING — zero hand-written visitor impls, two `[derive(Wire)]`.

**The one surface casualty:** `JsonWriter::serializer()`, `JsonReader::deserializer()` and their two
binary siblings are deleted. A record's closures may capture a `mut` local of their own frame but not a
`&mut self` view (`a view cannot escape its scope`), so the records are built in `json_codec` /
`binary_codec` over the `mut` local of the frame that mints them — §6.9's binding capture is the relation
the cells were buying (tracker B364 records the limit).

**Three cells were ADDED the same order, deliberately** (A110 door 1, lane reactive-38, 2f93d7a2): one
liveness `Shared<bool>` per `observe` subscription, shared between the `Subscriber` and its
`Subscription` and lowered by `dispose` before any removal, so a disposed observer never fires from an
inline notify's snapshot or from a wave the drain already took out. Deferrals share one module-level
`always_live`. reactive.vl 26 → 29; **the merged tree's census reads 121** (128 − 10 + 3). Cost
+9.1 % Ir per 12-notification wave (≈1,162 Ir per notification — the order of S3's +590 for its weak
upgrade). S4 (the counted lowering on the Rust backend) is unblocked by F1 S1b; S5 rides with it.

## 15. Re-scoped (Order 42, 2026-09-25) — the representation half is closed, S4 becomes the native leak gate, S5 recommended dropped

Written by lane papers-42 against vilan `next` @d65d4e75, from native-41's
report (C14's 2026-09-24 stamp) and the Order 42 brief; the re-scope itself is
native-42's to stamp at the sweep.

**The representation half is CLOSED — built by F1 S1a, by construction.**
§9's recommendation (a) asked for `Shared<T>` to be the counted resource
destruction.md §10 specifies: retain on clone, release at last use, `Weak` at
the back edges. On the native backend that is what `Shared` already IS.
`vilan-rt::Shared<T>` wraps an `Rc<RefCell<T>>` (`crates/vilan-rt/src/lib.rs:406`):
`Clone` is `Rc::clone` (a retain), dropping the last handle is `Rc`'s drop (the
release), `downgrade` is `Rc::downgrade`, and `Weak::upgrade` answers `None`
once the last strong handle is gone — so C1's "deterministic `None`", which §10
S2 said "waits for counting", holds natively today. Probe
(`sweeps/order42/papers-42/probes/c14/weak_release.vl`): a cell made and
downgraded inside a function, upgraded after it returns — JS `orphan=7` (no count,
`upgrade` is always `Some`, as §10 S2 documents), native `orphan=None`. Nothing
about this needed S4: the native lowering never had a no-op count to replace.
Stale sentence to correct with the stamp: `Shared`'s own doc in `vilan-rt` still
says "with C14 S4's real counting a later slice".

**What §10 S4 named, item by item:**

| §10 S4 said | now |
|---|---|
| `Shared`'s intrinsics gain a counted lowering, native only | DONE by F1 S1a (above) |
| the JS lowering stays byte-identical | holds — nothing on JS moved |
| `Owner`'s two cells become one body | NOT done (`reactive.vl:943`, `cleanups` + `disposed`); an allocation saving, not a correctness property — **dropped from C14**; file it only if a native profile asks |
| exit test: a native leg of the reactive suite | the native differential runs reactive programs, but nothing ASSERTS release — the gap the leak gate fills |

**S4 is REPLACED by the native leak gate** (native-42, this order). What it has
to be to count as the exit this paper never had: a census of live counted cells
over the exit program at process end, asserting every owner-scoped cell was
released. Three things decide whether it is a gate or a number:

1. **The instrument** is in `vilan-rt`: a live-cell counter raised at
   `Shared::new` and lowered when the last strong handle drops (a `Drop` on the
   allocation, not on the handle); `strong_count` is already there "for the
   measurement C14 S4 will want".
2. **What "released" means at process end.** Root-scoped cells (§2's 5.8 %: module
   bindings, and from this order `.cell_global()`, A130) are alive by design at
   exit. The gate asserts the OWNER-scoped class — cells minted under an owner that
   has been disposed — and REPORTS the root-scoped count, which is §2.4's
   finding stated as a number, not a failure.
3. **It must be shown red.** Plant §10 S3's strong back edge (the `observe`
   capture made strong again): under `Rc` a strong cycle is exactly what never
   releases, so the counter stays above zero where JS's SCC gate can only see the
   cycle in a heap snapshot. That is the property §13 found S3's exit test could
   not show on JS "by construction".

⟦INTEGRATOR: native-42 had not reported when papers-42 closed. Fill from its
report: the commit; the counter's mechanism; the exit program it runs over; the
owner-scoped live count at exit (expected 0) and the root-scoped count reported;
the planted-red run.⟧

**S5 — the JS counted mode as an instrument: recommended DROPPED (Q below).** It was
queued as the one tool that could turn the SCC gate's narrow claim into "every
cell is released" (§10, §13). Two things changed. The platform-free reactive
core — `reactive.vl`, `rpc.vl`, `delta.vl`, `process/ui.vl`, `rpc_server.vl`,
`ws.vl`, `time.vl`, `memo.vl`, `fs.vl`: **117 of std's 143** `Shared::new(`
sites (the `shared_census` literal) — builds natively and falls under the
native gate, where the count is real rather than simulated. And the remaining
**26** (`browser/ui.vl` 25, `browser/router.vl` 1) run ONLY on JS, under a
garbage collector, where an unreleased-but-unreachable cell is simply
collected: the only leak that matters there is a REACHABLE one, and the two
instruments that see reachable leaks already exist — the SCC gate
(`a_disposed_exemplar_holds_no_reactive_cycle`, cycles among what the test
keeps rooted) and the subscriber-list pins
(`derivations_detach_from_their_source_with_their_boundary`, 25 → 0). A counted
mode would measure, on JS, a property JS never relies on. **Re-file condition:**
a browser leak reported that neither gate sees. A native UI twin (F1's GPU apps)
would be under the native gate by construction and needs no S5.

**Q — confirm S5 dropped?** *Rec: yes*, with the browser twin's 26 sites
recorded as the native gate's documented blind spot and the re-file condition
above. If the owner keeps it, it is optional and M, and it belongs after the
native gate, whose output tells it what to look for.

**C14 at the sweep:** the representation half closes as built by F1 S1a; the
item stays open on the native leak gate alone until native-42's gate lands, and
closes with it.
