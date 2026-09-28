# Closure captures on a native backend — §6.9 priced on Rust (C15)

Tracker C15. Written by lane papers-43 of Order 43 on 2026-09-28, against vilan
`next` @762c6aa5 (content-identical to `main` @1a33340f; `vilan 0.41.1
(1a33340f2)`). Nothing in the compiler tree changed. Every claim about the tree
is a line that was read (cited `file:line`, crate paths under `crates/`) or a
probe that was run.

Probes: `scripts/integration/sweeps/order43/papers-43/probes/c15/` —
`run_probes.sh <scratch>` copies everything to a scratch dir and runs it:

- thirteen probe programs (`probes/p1…p12*.vl`), each run on JS and natively, the
  native run with the boxed-binding count and the leak census;
- the corpus census (`census_corpus.py`, emit-only over a scratch copy of
  `vilan/test`);
- the syntactic class census over std and kolt (`census_syntactic.py` →
  `std_census.tsv`, `kolt_census.tsv`, `corpus_census.tsv`);
- a full native build of kolt's server.

`kolt_server_json_codec_excerpt.rs` holds six lines of that build's emitted Rust.

Related: C14 (SignalCell off `Shared` — the counted cell and the leak gate), F1 /
`native-apps.md` (the backend; R-2 is the probe that first boxed a `let mut`), R3
(RULED 2026-09-17: v1 boxes every mutably-captured binding and counts them),
`lifetimes.md` §4 (the design §6.9 cites), `mut-parameters.md`.

---

## 0. The ask, and the answer up front

Spec §6.9 says a closure captures the BINDING, not the value. On JS that costs
nothing, because the host boxes every place. Natively, the compiler must decide
per binding whether it is copied, shared through a counted cell, or refused. R3
ruled the v1 answer, "box every mutably-captured binding as `Rc<RefCell<_>>`",
and asked for a count before any optimisation. C15 is the paper that prices the
rule.

**The answer.**

1. **Keep §6.9 as written, and keep R3's boxing.** Two findings support it.
   - **The box is exactly the cell the spec's own alternative would use.** The
     emitted `Captured<T>` is a type alias of the runtime's `Shared<T>`
     (`vilan-rt/src/lib.rs:670`). A binding that §6.9 shares costs what a
     hand-written `Shared` costs, and not a byte more. std shows it: the JSON
     codec moved FROM `Shared` cells TO a captured `mut writer`, and says so
     (`vilan/std/src/json.vl:850-851`).
   - **The optimisation the item proposes has nothing to optimise.** "Copy a
     binding never written after capture" applies to zero sites in all three
     bodies of code: the native-accepted corpus, std, and kolt (§3).
2. **Measured cost.**

   | where | boxed bindings |
   |---|---|
   | test corpus (140 programs, 104 emitted natively) | 2 |
   | std | 12 sites |
   | kolt's server, built natively | 6, all std's (JSON/binary codec, RPC socket handshake) |

   kolt's own source contributes 0 boxes to that build.
3. **The pricing found three native defects the rule does not excuse** (§6):
   - **D1, a silent miscompile.** A captured `mut` PARAMETER is never boxed:
     `fun late(mut n: i32): i32 { let show = || n; n = 5; show() }` prints
     `5` on JS and **`0` natively**.
   - **D2.** A reassigned closure-typed `mut` binding is refused by rustc.
   - **D3.** A `&self` method call on a boxed binding deep-copies the whole value.
     The JSON codec pays one extra copy of its writer per encoded frame.
4. **The copy census cannot see what boxing costs.** It sees no capture copy, no
   `Captured::get` copy, and no D3 copy (§4).
5. **A mutably-captured binding can make a real native `Rc` cycle** that JS's GC
   collects (§5). The leak gate catches it where a corpus program runs it.
6. **An explicit `move` is not recommended.** It would re-open `lifetimes.md` §4's
   ruled rejection of copy-at-capture, for a measured payoff of zero.

**Rec: rule kept, R3 kept, D1–D3 filed and fixed (all S), the census gains a
capture column, by-value capture parked with its trigger stated.** C15 then
closes on this paper.

## 1. The rule

**§6.9** (`vilan/docs/spec/memory.md:922-994`), `:926-930`: "**A closure captures
bindings, not values.** A captured binding is the same binding: a write on either
side is visible on the other, and a later **rebinding** is visible through the
capture." A closure capture "is not a new binding at all, so it copies nothing and
has no moment to copy at" (`:932-936`). The worked example, `mut label =
"before"; let show = || label; label = "after"; print(show())`, prints `after`
(`:938-945`). The one copy a closure takes is the per-call RETURN copy
(`:951-956`). Three things are excluded:

- resources (R9);
- the ambient context, which is snapshotted at creation — "the one true
  capture-time copy in the language";
- views (`:958-982`).

The section closes by saying that two closures sharing state "neither of them
declared" hold a `Shared` cell (`:984-989`).

**§6.1** (`memory.md:82-86`): every binding, assignment, argument pass, field
initialisation and return copies. A closure capture "is a different mechanism
and copies nothing at all" (`memory.md:211-212`). §6.2 allows an elision only
where no conforming program can observe it.

**The design source** is `lifetimes.md` §4 (`proposal/lifetimes.md:233-255`),
which weighed copy-at-capture and rejected it.

**JavaScript pays nothing.** p1 emits `let label = "before"; const show = () => {
return label; }; label = "after";` (`run_probes` output). Two closures assigning
one `let` (p3) are two arrows over one JS binding. No box and no copy are needed
at capture.

**The Rust contrast.** A non-`move` Rust closure BORROWS its captures, and the
borrow checker refuses two writers, or the enclosing scope touching the binding,
while the closure lives. A `move` closure copies or moves the value in, so a later
write outside is invisible, which is the opposite of §6.9. Shared mutation in
Rust is an explicit `Rc<RefCell<_>>` or `Cell`. vilan has no `move` and no
capture-mode syntax (`vilan-core/src/lexing.rs:61-96`).

## 2. What the native backend does today

All of this is in `vilan-rust/src/lib.rs`.

**Which bindings are boxed.** `compute_boxed_bindings` (`:616-653`) walks every
closure the program loaded. A binding is boxed if a closure body references it
as an `Expr::Local`, the closure did not declare it, and it is declared `mut`
(`program.variables … mutable`, `:641-650`). Two things follow:

- **No write is required.** p2 (`mut n = 1; n = n + 1; let f = || n + 1`, where
  the closure only reads) is boxed (`boxed-bindings=1`).
- **Parameters are never boxed.** They are not in `program.variables`. This is
  D1.

**What is emitted for a boxed binding:**

- The declaration: `let x = vilan_rt::Captured::new(v)` (`:4663-4668`), where
  `Captured<T> = Shared<T>` = `Rc<Slot { RefCell<T>, identity }>`
  (`vilan-rt/src/lib.rs:441-443`, `:464-467`, `:670`).
- A read: `x.get()` (`:4361-4362`). `Shared::get` returns a clone of `T`
  (`vilan-rt/src/lib.rs:516-526`).
- A write: `x.set(v)` (`:4129-4131`).
- A mutating use: `x.borrow_mut()` (`mutable_place`, `:9763-9769`).

**What every capture gets, boxed or not.** A handle of its own:
`{ let n = n.clone(); Rc::new(move || …) }` (`:6178-6241`). The comment gives the
reason: a Rust 2021 `move` closure takes the whole binding, so the enclosing
frame would lose it. For a boxed binding that clone is an `Rc` bump. For an
unboxed aggregate it is a deep copy at closure creation: p5 (`let xs = [1, 2, 3];
|| xs.len()`) emits `let xs = xs.clone()`.

**What a closure value is.** Always `Rc<dyn Fn>` (F16, `:6269-6275`), and never
`FnMut` (`:370-378`). A closure that must mutate state therefore needs interior
mutability whether or not anything else shares that state.

**The counter.** `Emitted::boxed_bindings = boxed_emitted.len()` (`:611`). It
counts declarations the walk actually EMITTED (merge fix c3f7d1a3; `mutable_place`
deliberately does not write it, `:9764-9766`). It is printed as
`vilan-native: boxed-bindings=N` on a full build under `VILAN_NATIVE_REPORT_BOXED=1`
(`vilan-cli/src/native.rs:30`, `:509`). The pin is
`the_boxed_binding_count_is_reachable_and_counts_the_right_bindings`
(`vilan-cli/tests/native_differential.rs:4114`). Its read-only case uses
`let n`, so it never exercises a read-only capture of a `mut` binding.

## 3. The measurement

**The classes, per C15's own question:**

- **(i)** captured, and written only BEFORE the capture. A copy suffices.
- **(ii)** after the capture, used by exactly one closure and by nothing else. The
  state could live in the closure.
- **(iii)** genuinely shared: two closures, or a closure and the enclosing scope,
  touch it after the capture.

| body of code | how | sites | (i) | (ii) | (iii) | (iii) that never escape |
|---|---|---|---|---|---|---|
| test corpus, 140 programs (104 emit natively, 36 refused) | `census_corpus.py` (emit-only) + syntactic cross-check | 2 | 0 | 1 | 1 | 0 |
| std (`vilan/std/src`, all `.vl`) | `census_syntactic.py` | 12 | 0 | 1 | 11 | 2 |
| kolt `src/` (client code, `lucide/` excluded) | `census_syntactic.py` | 6 | 0 | 3 | 3 | 0 |
| kolt's server, built natively (`vilan build --backend rust src/server.vl`) | `VILAN_NATIVE_REPORT_BOXED=1` | 6 (all std's) | 0 | 1 | 5 | — |

- The two corpus programs, `iterator.vl:24` `i` (ii) and
  `reactive-selector.vl:57` `hits` (iii), also full-build with
  `boxed-bindings=1` each. The syntactic census finds the same two, which
  validates it.
- std's 12 are listed in `std_census.tsv`. One false positive was dropped:
  `rpc.vl:5229` is inside a string literal. The 12:
  - the JSON and binary codecs' `writer` / `reader` (`json.vl:855`, `:878`;
    `binary.vl:405`, `:426`), each written by 15–18 closures;
  - `rpc_server.vl`'s handshake flags `settled`, `expired`, `closed`, `greeted`
    (`process/rpc_server.vl:832-833`, `:1289`, `:1302`);
  - `rpc.vl`'s `connection` / `refused` / `fault` (`:393`, `:961-962`, `:4831`).
- kolt's six are `command_palette.vl:44` `command_id` (ii) and
  `lib/interact.vl:75/77/78/112` (`dispose` iii, `drag_event` ii,
  `initiated_drag_handler` iii, `last_click` ii), plus `theme.vl:95`
  `initial_theme` (iii). All are browser code. The client leg is refused natively
  today for an unrelated reason, "generic type instantiated at any"
  (`client.vl:15`).

**Class (i) is zero everywhere.** The optimisation the item's text proposes
("a binding never written after capture is copied") has no site to act on. Every
mutably-captured binding in the estate is written after its capture, because
that is why it was declared `mut`.

## 4. The price

### 4.1 Per boxed binding

| operation | emitted | cost |
|---|---|---|
| declaration | `Captured::new(v)` | one `Rc` allocation (`RefCell` + identity) + the leak counter |
| capture, per closure | `x.clone()` | an `Rc` bump |
| read | `x.get()` | a `RefCell` borrow + a clone of `T`, and rule 1's copy may add a second: `(x.get()).clone()` |
| write | `x.set(v)` | a `borrow_mut` + a drop of the old value |
| `&mut self` call | `m(&mut x.borrow_mut(), ..)` | a `borrow_mut` — cheap (the JSON codec's 15 writer closures, `kolt_server_json_codec_excerpt.rs` line 4) |
| `&self` call | `m(&x.get())` | **a clone of the WHOLE value** (D3) |

The JSON codec is the hot site. `json_codec().writer()` runs once per encoded
frame. It mints one `Captured<JsonWriter>` and seventeen `Rc` closures over it,
then its finisher calls `result_5091(&writer_5860.get())`
(`kolt_server_json_codec_excerpt.rs` line 6, emitted from `json.vl:873`). That
finisher copies the writer, output buffer included, to call a `&self` method.
The closures dominate the allocation count, and the box is one allocation among
eighteen. The D3 copy is the only cost here that scales with the payload.

### 4.2 The unboxed capture's copy — native's own cost, not §6.9's

Every capture of an unboxed aggregate is deep-copied at closure creation (§2,
p5). §6.9 says a capture copies nothing. The copy is unobservable, because the
binding is not `mut`, so §6.2 permits it. But it is a cost the native lowering
adds, and the rule does not cause it. kolt's native server emits 114 closure
values with 277 capture-prelude clones. How many of those 277 are deep copies
and how many are handle bumps (a `Shared`, a closure, a `Captured`) depends on
their types, which this paper did not tabulate. A shared `Rc` handle to an
immutable capture, or a borrow for a non-escaping closure, would remove the deep
ones. That is a native-perf item of its own (§8, Q3), not C15.

### 4.3 What the copy census sees

The JS golden `copy-elision-census.tsv` counts `__clone` call sites in the corpus
`.mjs` goldens (`vilan-cli/tests/copy_elision_census.rs:1-28`). JS captures copy
nothing, so a capture is correctly absent from it. The native twin,
`native-copy-census.tsv`, counts CONSUMED place reads through
`copy_a_consumed_place_read` (`vilan-rust/src/lib.rs:8776-8806`). A read inside a
closure is never eligible for last-use elision (`reads_a_captured_binding`,
`:8783`, `:8800`). The census sees none of the capture-prelude clone, the
`Captured::get` clone, or the D3 clone. Under
`VILAN_NATIVE_REPORT_COPIES=1`, p2, p4 and p5 each report `consumed-copies=0`
while their emitted `main` holds one or two `.clone()` and two `.get()`.
**Boxing does not move the census, and it adds copies the census cannot see.**
Rec (S): the native census gains a `capture_copies` column, so §4.2's work has a
number to move.

## 5. The leak gate

With `VILAN_NATIVE_LEAK_CENSUS=1`, `main` runs on a thread of its own. After every
thread-local is dropped, the gate prints `cells minted=M live=L`
(`vilan-rt/src/lib.rs:305-340`). Its counters sit on every `Shared::new`
(`:473-497`). `Captured` IS `Shared`, so boxed bindings are counted. The census
table (`native_differential.rs:3517-3579`, `native-leak-census.tsv`) has two live
rows, `delta-law 2842/14` and `list-cell 2231/92`. Both have zero boxed bindings,
so those rows are reactive `Shared` cells, C14's business.

**A captured-binding cycle is real natively.** p10:

```vilan
mut holder = Holder { n = 1, run = || 0 };
holder = Holder { n = 2, run = || holder.n };
```

This prints `2` and ends with `cells minted=1 live=1`: the cell holds a closure
that holds the cell. JS's GC collects the same cycle. p9 breaks its own cycle by
reassigning `run`, and ends `live=0`. kolt's `lib/interact.vl:75-104` has the
cycle's shape (`mut dispose;` captured by the pointer-up handler, then assigned a
closure over both subscriptions). It is client code, and a binding with no
initializer is refused natively anyway (`vilan-rust/src/lib.rs:4671-4674`).

This is the same honest limit as C14's `Shared` cycles: a counted cell cannot
collect a cycle through itself. The leak gate is the detector, and it only sees
what the corpus runs. **Rec:** state the limit beside §6.9 in the native chapter,
and add p10 as a leak-census row with `live=1` expected. The row is then a pin on
the limit, not a hidden failure.

## 6. Three defects the pricing found

None of these is in the tracker (grepped).

**D1 — a captured `mut` parameter is not boxed: a SILENT MISCOMPILE.**

```vilan
fun late(mut n: i32): i32 {
	let show = || n;
	n = 5;
	show()
}
```

`print(late(0))` prints **JS `5`, native `0`**. This was re-run for this paper:
`vilan run` against `vilan run --backend rust`, `p12_mut_param_read.vl`. The
emitted Rust is `let n = n.clone(); Rc::new(move || { n })` followed by a plain
`n = 5`. The capture took a copy and the write went to the frame's own binding.
It is §6.9's example with a parameter where the local was.
`compute_boxed_bindings` asks only `program.variables`
(`vilan-rust/src/lib.rs:641-650`). The fix (S) extends the test to
`program.parameters` with a `mut` binder, and emits
`let n = vilan_rt::Captured::new(n);` at function entry, so every read and write
below takes the boxed path. Pin: p12 in `native_differential` (stdout `5`), plus
p11 (a closure that WRITES a `mut` parameter, refused by rustc today with
E0594/E0596) as its loud sibling. This belongs in native-43 or Order 44's native
lane as a B-item, flagged UNSOUND, because it prints a wrong answer without a
diagnostic.

**D2 — a reassigned closure-typed `mut` binding is refused by rustc.** p7 is
`mut g: || i32 = || 1; let h = || g(); g = || 2; print(h())`. It prints `2` on JS,
and natively fails with `error[E0308]: mismatched types` ("no two closures … have
the same type"). The same holds unboxed (p7b), self-recursive (p6,
`f = || … f()`), and for a `List<|| i32>` holding two different closures (p8).
The declaration writes an annotation only for an empty list literal
(`vilan-rust/src/lib.rs:4611-4629`), so the binding takes the concrete closure's
type instead of `Rc<dyn Fn>`. Fix (S): annotate a closure-typed binding (and a
closure-typed list literal) with its `rust_type`. It is loud, not silent.

**D3 — a `&self` call on a boxed binding clones the whole value** (§4.1). Emit
`m(&*x.borrow(), ..)` instead of `m(&x.get(), ..)`. The borrow is exactly as
safe: a reentrant access through another handle already panics with
`REENTRANT_READ` (`vilan-rt/src/lib.rs:445-455`). Fix S, with a pin on the
codec's finisher.

## 7. The options

**(a) Keep the rule; box every mutably-captured binding (R3, today).** The price
is §4.1's table on 2 corpus, 12 std and 6 kolt sites, and the box is the `Shared`
the spec would otherwise ask for. **Rec**, with D1–D3 fixed.

**(b) Capture by value unless the binding is written after the capture.** Box
only a binding with a write reachable after its capture, in the closure or in
the enclosing scope. It is precise, sound and cheap to state, and p2 shows the
current rule over-boxes. **It saves zero sites** in the measured estate (§3,
class (i)). Park it. The trigger: a class-(i) site appears in the native census,
which the (b) predicate would itself count.

**(b′) Closure-owned state for class (ii).** A binding that only one closure
touches after capture moves INTO that closure's environment as a `RefCell<T>`
(or a `Cell` for `Copy` types), with no second `Rc`. The saving is one allocation
per closure creation over 1 + 1 + 3 sites, all low-frequency (per connection, per
click, per id minted). It needs a proof of no later use in the enclosing scope
that survives nested closures (`interact.vl:91`'s nested closure reads
`drag_event`). Park it.

**(c) An explicit `move`, meaning capture by value.** This is a language change.
It gives closures two capture meanings, re-opens `lifetimes.md` §4's ruled
rejection of copy-at-capture, and adds a word (contextual per B414 at best). The
measured payoff is nothing (class (i) is zero), and the one case it would
express, "snapshot this now", is already a `let` copy before the closure.
**Not recommended.**

## 8. Sizing and pins

| piece | size | lane |
|---|---|---|
| D1 fix + p11/p12 pins (UNSOUND) | S | native (Order 43 native-43 if it has room; else Order 44 first) |
| D2 fix + p6/p7/p8 pins | S | native |
| D3 fix + codec-finisher pin | S | native |
| p10 as a leak-census row (`live=1`, the limit pinned) + the §6.9 native note | S | native / docs |
| `capture_copies` column in `native-copy-census.tsv` | S | native |
| (b) / (b′) | S–M each | parked |
| (c) | — | not recommended |

## 9. For the owner

- **Q1 — keep §6.9 as written on the native backend (option (a))?** Rec: yes.
  It costs what the spec's own `Shared` alternative costs, and the measured
  by-value payoff is zero.
- **Q2 — file D1 as UNSOUND and fix it first?** Rec: yes. It is a silent wrong
  answer on the spec's own example shape. D2 and D3 follow as S items.
- **Q3 — open a separate native-perf item for §4.2** (the deep copy of an
  immutable aggregate at every closure creation: a shared handle, or a borrow for
  a non-escaping closure)? Rec: yes, once the census column exists to measure it.
  C15 closes without it.
- **Q4 — close C15 on this paper?** Rec: yes. The rule is priced, R3 stands, and
  (b) / (b′) are parked with the trigger stated in §7.
