# Closure captures — what §6.9's shared binding costs, and which narrower rule is sound (C15)

> Status: **DRAFT 2026-10-05 — for the owner's ruling.** Written by lane papers-47 of Order 47
> against vilan `next` @b94cb47f (`vilan 0.44.0 (b94cb47fc)`, built in the lane's worktree).
> Nothing in the compiler tree changed. kolt and the website were read in place and built only
> as copies in the lane's scratch directory.
>
> This is the second C15 paper. The first, `closure-captures-on-native.md` (papers-43,
> 2026-09-28), priced R3's rule ("box every mutably-captured binding") at @762c6aa5. It
> recommended keeping the rule and parking the by-value optimisation until a site appeared.
> This paper re-measures at the Order 47 base, measures the cost in instructions, and gives the
> soundness argument or a counterexample for each narrower rule.
>
> Probes, censuses and benchmarks: `scripts/integration/sweeps/order47/papers-47/c15/`.
> - `probes/run.sh <vilan> <scratch>` runs nine probe programs (`cN`), on JS and natively, the
>   native run with the boxed count and the leak census. The output is in `probes_out.txt`.
> - `handlowered/` holds emitted Rust with a candidate rule's lowering applied by hand, run
>   against the same `vilan-rt`.
> - `bench/` holds the out-parameter microbenchmark's four lowerings and their callgrind counts
>   (`bench/README.txt`).
> - `census_emit.py` is an emit-only native census: distinct `Captured::new` declarations, the
>   function each sits in, closures, and the copy-census line. Outputs: `corpus_census.txt`,
>   `estate_census.txt`, `store_probe_census.json`.
> - `census_syntactic.py` is papers-43's syntactic census, re-run here (`*_census.tsv`).
>
> Related: R3 (RULED 2026-09-17); F47 (CLOSED: a captured `mut` parameter is boxed); F48
> (CLOSED); F49 (OPEN: a `&self` call on a boxed binding copies the value); F50 (its column and
> its row are both present at this base, §1); C16 (the retention summary, §4.3); F16 (every
> closure value is `Rc<dyn Fn>`); F39 (the reentrant read through an alias, DECIDED as a
> compile-time refusal).

## 0. The ask, and the answer up front

Spec §6.9 (`vilan/docs/spec/memory.md:979-1063`) says a closure captures the BINDING. On JS that
costs nothing. Natively, R3 boxes every mutably-captured binding in a `Captured<T>`, which is
`Shared<T>` (`crates/vilan-rt/src/lib.rs:750`). C15 asks what that costs, and whether a narrower
rule is sound. The narrower rule the brief names is "a binding captured by exactly one
non-escaping closure stays unboxed".

**The answer.**

1. **What it costs** (§2, §3):
   - **JS:** zero cells. A captured `mut` is a plain `let`, the store's out-parameters included.
   - **Natively, per boxed binding:** one 40-byte allocation, about **152 instructions** for a
     scalar (allocate, initialise, free). Of those, **17** are the cell's identity and the leak
     counter.
   - **Not this rule's cost:** the closure's own `Rc` (about **178 Ir**). Every closure value
     pays it (F16).
   - **The site that matters is the store.** A `Store` write costs about **4,150 Ir and 15
     allocations**, of which **3 are capture boxes (about 11 %)**. F49's copies of the boxed
     value come on top: six whole-`StoreWoken` copies per write, all from field reads.
2. **Where boxes are emitted.** The measured estate has **16 distinct boxed sites**, against 2
   corpus sites in Order 43:
   - the corpus: 145 programs, 113 emitted natively, 5 boxes;
   - kolt's native server: 7, all std's or generated;
   - the one example that emits natively, `rpc`: 4;
   - a `Store` probe: 5.

   std's mutably-captured sites grew from 12 to **43**, nearly all of them the store's
   `lend(|place| { out = .. })` out-parameters.
3. **Soundness of the candidates** (§4):
   - **The brief's rule as stated is unsound.** Lowered as a copy, it breaks §6.9's own example:
     one closure, never escaping. Hand-lowered, it prints `before`, where the rule says `after`.
   - It is sound only as **R2a**: one closure, which no callee keeps, and which the enclosing
     frame does not touch between creating the closure and its last use. The lowering is a
     BORROW, and rustc re-checks it, so a misclassification is refused rather than miscompiled.
   - **R1** ("written only before capture") is sound only by control-flow reachability. Read
     textually, a loop breaks it.
   - **R2b** (closure-owned state) is sound only if the closure expression runs once per
     instance of the binding. Hand-lowered without that condition, it prints `1 1 1` for
     `1 2 3`.
4. **What the narrower rules would save** (§5):
   - R1 applies to **1** emitted site, and R2b to **2**. All three are cold.
   - R2a applies to 1 corpus site.
   - R2a's shape covers the store's **4** hot sites, but they are out of its reach. Their callee
     is a closure VALUE (`lend`), and C16's retention summary answers "keeps everything" for an
     opaque callee.
   - Every narrower rule also needs a second closure representation, because F16 makes every
     closure `'static`.
5. **Two finds** (§6):
   - **c5/c9:** a JS-valid program aborts natively when a closure writes a captured binding
     while a `&mut` view of that binding is live. The program declares no `Shared` at all.
   - **F49 is wider than filed:** a FIELD read on a boxed binding also copies the whole value.

**Rec: keep §6.9 and R3. Build no narrower capture rule now** (R1, R2a and R2b parked, each with
its soundness condition written down). Fix F49 together with its field-read sibling before the
mirrored store's server half runs natively. Settle c5/c9 as F39 was settled, by refusing at
compile time. If the store's write path needs its three boxes back before any language change,
the lever is in std (§7, option S).

## 1. Since the first paper

- **F47 is fixed.** `compute_boxed_bindings` (`crates/vilan-rust/src/lib.rs:738-780`) now boxes a
  by-value `mut` parameter too (`:766-774`). kolt's server shows it: the generated `[service]`
  dispatcher boxes `this`.
- **F50 is done, although the tracker still lists it OPEN.**
  - The copy census has its `capture_copies` column: 144 over the 37 rows of
    `native-copy-census.tsv`. kolt's server has 145.
  - The leak census pins the cycle as `native_probe_captured_cycle 1 1`.
  - §6.9 carries the "Native limit: a captured binding can close a cycle" note
    (`memory.md:1053-1062`).
- **F49 is still open.** kolt's native server makes **13** `&this.get()` calls, one per RPC
  route. Each copies the connection's `KoltStore`, which is two handles, per request. The JSON
  codec's `&writer.get()` is still there.
- **The store emits natively** (probe s1). Its out-parameter closures are where std's capture
  count went: 12 sites became 43 (`std_census.tsv`).

## 2. The measurement

### 2.1 JavaScript

There are zero cells. c1 emits `let label = "before"; const show = () => { return label; };
label = "after";`. The store's `write_at` emits `let reached = false;` and assigns it inside an
arrow. The host's closure environment is the shared binding.

### 2.2 Native, emitted

`census_emit.py` counts distinct `let NAME = vilan_rt::Captured::new(` declarations in
`vilan build --backend rust --stdout`.

| body | targets | emitted | boxed sites | closures | capture-copies |
|---|---|---|---|---|---|
| test corpus (`vilan/test/*.vl`) | 145 | 113 (32 refused) | 5 in 5 programs: `iterator.vl` `i`; `reactive-selector.vl` `hits`; `shared-compound-write.vl` `captured`; std's `effect` `latest` (in `dyn-objects`, `reactive-owner`) | 358 | 202 |
| `vilan/examples/` (every `.vl`) | 29 | 3 (`math` ×2, `rpc`) | 4, all in `rpc`: std `json_codec` `writer` and `reader`, the `[service]` dispatcher's `this`, std `rpc.vl` `enlist`'s `found` | 139 | 70 |
| kolt `src/server.vl` (from the package root) | 1 | 1 | 7, all std's or generated: `settled`, `expired`, `closed`, `greeted` (`process/rpc/server.vl`), `this`, `writer`, `reader` | 145 | 145 (consumed 265, elided 680) |
| kolt `src/client.vl`, website server and client | 3 | 0 | refused: F1 S1b's scope ("generic type instantiated at `any`", an unresolved type) | — | — |
| probe s1 (a `Store`, 20,000 writes) | 1 | 1 | 5: `latest`; `lent_value`'s `out`; `write_at`'s `woken`, `reached`, `changed` | 52 | 19 |

kolt's own source contributes no box to its server build, which matches Order 43. The example
refusals that are not F1 S1b are modules with no `main`, and package entries compiled from
inside their package's `src/`, which hits find B?1 (§6.3).

### 2.3 The syntactic estate

This is papers-43's script, re-run over code the native backend cannot emit yet.

| body | sites | (i) written only before | (ii) one closure, nothing after | (iii) shared |
|---|---|---|---|---|
| std | 43 (12 in Order 43) | 2 after review: `rpc.vl:3726` `found`, `rpc.vl:3927` `ops` | 3 (`closed`, `store_core.vl:944` `last`, `ops` as scored) | 38, of which **26 are the store's `lend` out-parameters**: 17 with one closure, 9 shared by two sequential `lend` calls |
| kolt `src/` | 6 (unchanged) | 0 | 3 (`command_id`, `drag_event`, `last_click`) | 3 |
| website `src/` | 3 | **2** (`server.vl:217-218` `wasm_manifest`, `wasm_pairs`) | 0 | 1 (`chrome.vl:110` `markup`, read after `run_with_owner`) |
| `vilan/examples/` | 0 | — | — | — |

`rpc.vl:6314` (`mut closure = i".."`) is a string the script misreads, and it is dropped. The
script also undercounts. `write_at`'s `woken` is captured only as `&mut woken`, which it does
not see, and the native emitter does box it.

**Order 43's trigger has fired.** Order 43 parked R1 until "a class-(i) site appears in the
native census". `found` in `enlist` (`rpc.vl:3726-3765`) is written in a loop that ends before
the `revive` closure, which only reads it, and the `rpc` example emits it boxed. It runs once per
mirror enlistment.

## 3. The price, in instructions

### 3.1 One boxed scalar

The benchmark is `bench/` and `probes/m1_out_param.vl`: the store's out-parameter shape, a
binding written by one closure handed to a function that calls it and does not keep it, then
read. It runs 200,000 iterations, built `--release`, and is counted with callgrind. `with_value`
is `#[inline(never)]` in every variant.

| lowering | Ir | allocations | per iteration over the floor |
|---|---|---|---|
| v0: as emitted, a `Captured<i32>` and an `Rc<dyn Fn>` closure | 70,528,461 | 400,012 | 330 |
| v1: `Rc<Cell<i32>>` and an `Rc<dyn Fn>` closure | 67,128,467 | 400,012 | 313 |
| v3: a `Captured<i32>` and a borrowed `&dyn Fn` closure | 34,926,860 | 200,012 | 152 |
| v2: a `Cell<i32>` on the stack and a borrowed `&dyn Fn` closure (R2a's lowering) | 4,528,265 | 12 | — |

Reading the table:

- The **box** costs v3 − v2 = **152 Ir** and one 40-byte allocation per instance.
- The `Captured` representation's own share of that, the identity and the leak gate's counter
  (`crates/vilan-rt/src/lib.rs:501-590`, `Slot`'s identity cell and the minted counter), is v0 − v1 = **17 Ir**.
- The closure's `Rc` costs v0 − v3 = **178 Ir**. It is not §6.9's cost: every closure value pays
  it (F16). A narrower rule nevertheless saves it too, because the only lowering that drops the
  box also drops the `Rc` (§4.3).

### 3.2 A store write

Probe s1 makes 20,000 `user.visits().set(n)` calls: **83,052,896 Ir** and **300,181
allocations**, so about **4,150 Ir and 15 allocations per write**. Three of the allocations are
`write_at`'s boxes, `woken`, `reached` and `changed` (`std/src/reactive/store_core.vl:552-554`).
At 152 Ir each, the boxes are about **456 Ir, 11 %** of a write.

The leak census reports `cells minted=60036 live=0`. Every minted cell in that run is a capture
box, and the census's `minted` column cannot tell one from a `Shared` the program wrote. On top
of the boxes, F49 adds the field-read copies (§6.2): `(woken.get().feeds).clone()` appears
twice per write and `woken.get().slots` once, and each `get()` copies the whole `StoreWoken`.

A store READ goes through `lent_value` (`:1053-1062`), one box per read.

### 3.3 What the censuses see

The copy census's `capture_copies` column (F50) counts the capture-prelude copies of UNBOXED
values. A box's prelude clone is a handle bump, and is correctly not counted. The `get()` copies
of §3.2 are counted nowhere: they are neither a consumed place read nor a capture. The leak
census counts every box as minted. Neither census has a column that isolates §6.9's cost. A
`boxed` column beside `capture_copies` is cheap: `Emitted::boxed_bindings` already exists
(`crates/vilan-rust/src/lib.rs:105`).

## 4. The candidate rules, and their soundness

Each candidate keeps §6.9's meaning and changes only the lowering, so each is an elision under
§6.2 and must be unobservable. "Access" below means any read, write, `&`/`&mut` view, or method
call on the binding.

### 4.1 R1 — copy a binding no write reaches after the capture

**Rule.** A binding is captured by value (copied when the closure is created) if no write to it
is REACHABLE from any closure-creation point that captures it. Reachability is over the enclosing
function's control-flow graph, back edges included. A write here means an assignment, a compound
assignment, a `&mut` view, a `&mut self` call, or any closure that writes it.

**Soundness.** On every path from the creation point the binding holds the value it held at
creation, so the copy and the binding agree at every read through the capture. §6.9's per-call
return copy is taken either way. This is sound.

**Counterexample to the TEXTUAL reading** (c2): "every write is above the closure in the text".

```vilan
mut x = 0;
mut fs: List<|| i32> = [];
for k in [0, 1, 2] {
	x = k;            // above the closure, but the back edge reaches it after
	fs.push(|| x);
}
for f in fs { print(f()) }   // 2 2 2 (JS and native today); a copy prints 0 1 2
```

**Sites:** `rpc.vl` `found` among the emitted boxes, plus `ops` and the website's two in the
syntactic estate. All four are cold: once per enlistment, per mirror patch, or per server start.
For an aggregate, R1's copy is a deep copy at creation (§4.2 of the first paper). The cheaper
lowering for those is an immutable shared handle, which is the parked capture-copies item, not
C15.

### 4.2 The brief's rule as stated — UNSOUND

"A binding captured by exactly one non-escaping closure stays unboxed." Unboxed means the closure
gets a copy, and §6.9's own worked example (c1) is the counterexample. It has one closure, which
never leaves `main`:

```vilan
mut label = "before";
let show = || label;
label = "after";
print(show());     // after
```

`handlowered/c1_copy.rs` is the emitted Rust with the `Captured` replaced by a plain binding
moved into the closure. It prints **`before`**, and rustc warns that the later write is never
read. "Exactly one" and "non-escaping" are both true here. What the rule misses is the ENCLOSING
frame's write between the closure's creation and its call.

### 4.3 R2a — one non-retained closure, no interleaved access, lowered as a borrow

**Rule.** The binding stays an ordinary stack local, wrapped in `Cell`/`RefCell` because F16
closures are `Fn`, never `FnMut` (`vilan-rust/src/lib.rs:449`). The closure BORROWS it, when all
of the following hold:

- (a) exactly one closure expression references it. With R2a′, several are allowed provided
  their live ranges are disjoint.
- (b) that closure's value is never retained. It is not stored, returned, or put in a field,
  collection or payload, and every callee it is passed to keeps nothing (C16's
  `compute_retaining_positions`, `crates/vilan-core/src/analyzer.rs:26298-26376`).
- (c) the enclosing frame does not access the binding from the closure's creation to the
  closure value's last use.

**Soundness.** During the closure's live range, the closure body is the only code that can reach
the binding:

- (c) excludes the frame.
- (a) excludes any other closure.
- (b) excludes any later caller.

After the live range the frame reads the binding directly, and it holds every write the closure
made. A recursive call into the closure is impossible, because it cannot name itself without
capturing a binding that holds it, and that assignment retains it under (b). The `RefCell`
borrow is therefore never contended.

The lowering also checks itself. It is an ordinary Rust borrow, so if a classification were
wrong (a missed access, a missed retention), rustc would refuse the crate instead of the program
printing a wrong answer. That is the property the copy lowering in §4.2 lacks.

Two obligations remain for (b):

- an `async` callee's future keeps its arguments until it completes, so a callee returning a
  future that is not awaited at once is retaining;
- the C16 summary has to be computed for every program, not only those with a view-capturing
  closure as today (`analyzer.rs:26053-26057`).

**Cost to build.** F16 makes every closure parameter `Rc<dyn Fn>`, which is `'static`, so a
borrowing closure has nowhere to go. R2a needs a second closure ABI: a non-retained closure
PARAMETER received as `&dyn Fn`. That is a change to signatures, call sites and
monomorphization, sized M–L.

**The obstacle that matters.** The store's out-parameters pass their closure to `lend`, which is
itself a closure-typed parameter (`write_at`'s `lend: |(|&T| void)| void`, `store_core.vl:545`).
A call through a closure value has no body for C16 to read, and C16 answers such a callee by
"keeps everything" (`analyzer.rs:26285-26295`; the doc comment at `:26310-26314`: "a callee with
no readable body keeps everything"). So R2a as stated covers `shared-compound-write.vl`'s `captured` and **none of the
store's sites**. Reaching them needs a closure TYPE that promises not to keep its argument,
which is a language change. Or it needs std to stop writing out-parameters through closures
(§7, option S).

### 4.4 R2b — closure-owned state

**Rule.** The binding moves INTO the closure's environment as a `Cell`/`RefCell`, and the
closure's own `Rc` becomes the box, when all of the following hold:

- (a) exactly one closure expression references it, counting a nested closure inside it as a
  second reference unless that nested closure is itself non-retained;
- (b) the enclosing frame never accesses it after the closure's creation;
- (c) the closure expression is evaluated **at most once per instance of the binding**: no loop
  and no closure body encloses the creation without also enclosing the declaration;
- (d) copies of a closure value share one environment. They do under F16's `Rc`, and c4 prints
  `1 2` on both backends.

Escaping is allowed. That makes R2b the rule for the counter-factory shape (c6) and for
`iterator.vl`'s `Iterator::from_fn(|| { i += 1; i })`.

**Soundness.** After creation, the binding is reachable only through the closure's environment.
By (d) every copy of the closure value reaches the same environment. By (c) there is exactly one
environment per binding instance. So the environment's cell IS the binding.

**Counterexample without (c)** (c3):

```vilan
mut n = 0;
mut fs: List<|| i32> = [];
for _i in [0, 1, 2] {
	fs.push(|| { n += 1; n });
}
for f in fs { print(f()) }    // 1 2 3 (JS and native today)
```

`handlowered/c3_closure_owned.rs` moves `n` into each closure as a `Cell`. It prints
**`1 1 1`**: three environments for one binding.

**Saving:** one allocation per binding instance (about 150 Ir) and one `Rc` bump per capture.
**Sites:** `iterator.vl` `i` and std's `closed` (`process/rpc/server.vl:1299-1310`, once per
connection) among the emitted boxes. kolt's `command_id` and `last_click` qualify in the
syntactic estate. `drag_event` qualifies only if `turn`'s closure is non-retained. All of these
are cold.

### 4.5 R4 — keep the box, change its representation

A `Copy`-typed box as `Rc<Cell<T>>` instead of `Rc<RefCell<T>>` with an identity is always
sound. It is not an elision. It saves **17 Ir** per instance (v0 − v1) and a borrow-flag check
per access. It is not worth a second cell type in `vilan-rt` on its own.

## 5. Who each rule reaches

| boxed site (emitted) | where it runs | shape | R1 | R2a | R2b |
|---|---|---|---|---|---|
| `write_at` `woken`, `reached`, `changed` | every store write | one closure to `lend`, read after | — | shape fits; **callee opaque** | — |
| `lent_value` `out` | every store read | same | — | shape fits; **callee opaque** | — |
| `json_codec` `writer`, `reader` | every encoded/decoded frame | 15–18 closures | — | — | — |
| dispatcher `this` (generated by `[service]`) | per connection, read per request | 14 route closures | — | — | — |
| `effect` `latest` | per effect | two closures, read after | — | — | — |
| `settled`, `expired`, `greeted` | per connection | retained handler, frame reads after / two closures | — | — | — |
| `closed` | per connection | one retained closure, frame never touches it | — | — | **yes** |
| `rpc.vl` `found` | per mirror enlistment | written before, read by one closure | **yes** | — | — |
| corpus `iterator.vl` `i` | per program | `Iterator::from_fn`, retained | — | — | **yes** |
| corpus `shared-compound-write.vl` `captured` | per program | one local closure, called, read after | — | **yes** | — |
| corpus `reactive-selector.vl` `hits` | per program | retained `on_change`, read after | — | — | — |

Of 16 sites, one is reachable by R1 and two by R2b, all cold, and one corpus program by R2a. The
hot paths are the store, where R2a's shape fits but the callee is opaque, and the codec, which
is genuinely shared. Neither yields to any narrower rule that can be built today.

## 6. Finds

### 6.1 A view and a capturing closure on one binding abort natively (c5, c9)

```vilan
fun apply(x: &mut i32, f: || void) { f(); x += 10; }
mut n = 0;
apply(&mut n, || { n += 1; });
print(n);                       // JS 11; native: "a cell was read while it is being updated" (exit 1)
```

The same happens through a `&mut self` receiver (c9: `c.bump_then(poke)`, where `poke` writes
`c.n`). JS gives 102, and native aborts. Here is why. `n` is boxed because a closure writes it.
The `&mut n` argument holds the cell's `borrow_mut` for the length of the call, and the closure's
write reaches the same cell. The program declares no `Shared`, so the cell is purely §6.9's
lowering. F39 settled the explicit-`Shared` twin by refusing at compile time, following aliases.
The capture form is the same aliasing, a `&mut` view live while another path writes its place,
and it is the shape rule 4 (§6.4) exists to refuse. Filed as F?1 with a repro
(`finds/native_view_beside_capturing_closure.vl`), recommendation: refuse at compile time.

### 6.2 F49 is wider: a FIELD read copies the whole boxed value

`log.lines.len()` on a boxed `log` emits `log.get().lines.len()`, which copies the whole struct,
every list included, to read one field. In std it is `write_at`'s `woken.get().feeds` and
`.slots`, six whole-`StoreWoken` copies per store write. F49 was filed for `&self` calls, and the
same fix (borrow through the cell rather than `get()`) covers field reads. Filed as F?2, F49's sibling,
with a repro (`finds/native_boxed_field_read_copies.vl`).

### 6.3 Not C15's, met on the way

`vilan check main.vl` run from inside a package's `src/` ignores the package. `owning_package`
asks `Path::new("main.vl").parent()`, which is `""`, and finds no manifest
(`crates/vilan-cli/src/main.rs:3826-3832`). So the package's prelude and std are not applied: kolt
fails with a `[service]` expansion error, and a web-prelude package is told to set the prelude it
already sets. An absolute path, or a relative path from the package root, works. Filed (B?1)
with a three-file repro.

## 7. Options

- **(a) Keep §6.9 and R3, and build no narrower rule.** The cost is §3's: 152 Ir and one
  allocation per instance, about 11 % of a store write, and nothing on JS. **Rec**, together
  with F49 and its sibling fixed (they scale with the payload, as the box does not) and §6.1
  settled.
- **(b) R1.** Sound with reachability. It needs the analysis plus one capture form in the
  emitter, sized S–M, and reaches 1 emitted site and 3 more estate sites, all cold. **Park**,
  trigger: an R1 site on a per-request or per-frame path.
- **(c) R2b.** Sound with the once-per-instance condition. It needs a per-binding check and an
  environment-owned cell, sized M, and reaches 2 emitted sites, all cold. **Park**, same trigger.
- **(d) R2a.** Sound, and self-checked by rustc. It needs C16 always on plus a second closure ABI
  (sized M–L), and still misses the store unless closure types carry non-retention. **Park as the
  candidate of record**: it is the only rule whose shape covers a hot path.
- **(S) std, not the compiler.** `write_at`'s three out-parameters can be ONE captured struct
  (`mut lent = Lent { reached = false, changed = false, woken = .. }`). That is one box instead
  of three per write: about 300 Ir, roughly 7 %. It needs no language change, and the store pins
  hold byte-identical output. **Offer** to the lane that builds A153's server half, which is
  when a store first runs per request natively.
- **(e) Change §6.9** so that a closure copies at capture. Not recommended, for the first paper's
  reasons: `lifetimes.md` §4's ruled rejection, and the explicit `let` copy already spells a
  snapshot.

## 8. Sizing

| piece | size | lane |
|---|---|---|
| §6.1: refuse a write through a capture while a `&mut` view of the binding is live; pins c5/c9 | S–M | analyzer (rule 4's walk) |
| F49 + §6.2: borrow through the cell for `&self` calls and field reads; a pin on `write_at`'s copy count | S | native |
| a `boxed` column in `native-copy-census.tsv` (§3.3) | S | native |
| F50: close (both halves present) | — | sweep |
| option S: `write_at`'s one-struct out-parameter | S | store / A153 S1 |
| R1 / R2b / R2a | S–M / M / M–L | parked |

## 9. For the owner

- **Q1. Keep §6.9 and R3 unchanged, and build no narrower capture rule now?** Rec: **yes.** The
  narrower rules that are sound reach 3 cold sites (R1, R2b). The one that fits the hot path
  (R2a) cannot reach it without a closure ABI change and a closure type that promises
  non-retention.
- **Q2. The brief's candidate ("exactly one non-escaping closure stays unboxed"): record it as
  unsound as a copy, and adopt R2a's three conditions and borrow lowering as the parked candidate
  of record?** Rec: **yes.** c1 is the counterexample, and R2a's conditions are the repair.
- **Q3. c5/c9, the native abort when a closure writes a binding under a live `&mut` view: refuse
  at compile time, as F39 decided for `Shared`?** Rec: **yes**, under rule 4. The alternative,
  native answering JS's in-progress value, is unavailable in safe Rust for the reason F39 gives.
- **Q4. F49 widened to field reads, and fixed before A153's server half runs natively?** Rec:
  **yes.** It is the cost here that scales with the payload.
- **Q5. Option S (one boxed out-parameter struct in `write_at`): offer it to A153 S1's lane?**
  Rec: **yes, as an offer, measured there.**
- **Q6. Close C15 on the two papers, and F50 as done?** Rec: **yes.** R1, R2a and R2b are parked
  with their conditions and the trigger: a site on a per-request or per-frame path that one of
  them reaches.
