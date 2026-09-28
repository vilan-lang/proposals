# Devirtualizing a single-implementor `dyn Trait` — measured first (M88)

Tracker M88 (the owner's item). Written by lane papers-43 of Order 43 on
2026-09-28, against vilan `next` @762c6aa5 (content-identical to `main`
@1a33340f; `vilan 0.41.1 (1a33340f2)`). Nothing in the compiler tree or in kolt
changed. kolt was measured from a scratch copy of its working tree as it stands
today, the owner's uncommitted edits included. Every claim about the tree is a
line that was read (cited `file:line`, crate paths under `crates/`) or a probe
that was run.

Probes: `scripts/integration/sweeps/order43/papers-43/probes/m88/` (see its
`README.txt`):

- `dyn_census.py`: the per-key occupant census from a `vilan build -d` dump,
  cross-checked against the emitted tables;
- `sweep.sh`: vtables over the corpus, the examples and the benchmarks;
- `doors/d*.vl`: every way found for a `dyn` value to exist, each run on both
  backends;
- `bench/`: a `dyn` field against the concrete field, timed by child CPU time.

Related: B4 / `trait-objects.md` (§3.3 the measurement, §6 representation, §8
drop), A124 R3 (`dyn Source<U>` in `combine`, the only `dyn` std has), B398
(element-wise erasure of a tuple literal), B412 (a generic parameter erased),
B430 / B431 (open), `bundle-splitting.md`, `hmr.md`.

---

## 0. The ask, and the answer up front

The owner's idea: when the whole program coerces exactly ONE concrete type into
`dyn Trait<Args>`, the `(value, vtable)` pair is redundant. The pair collapses to
the value, and every dispatch through it becomes the direct call. This is a
build-time optimisation only: `dyn` stays the author's spelling, and the
analyzer, the LSP and the types do not move.

**What the measurement says.**

1. **The premise holds.** 13 of the 15 `(trait, args)` keys in the estate have
   exactly one occupant: kolt's client 9 of 9, the todo example 2 of 2,
   reactive-ui 2 of 2. The only exception is `test/dyn-objects.vl`, 0 of 2 by
   construction (§2).
2. **The optimisation as filed reaches no dispatch site in the estate.** std
   has two `dyn` positions, both `combine`'s (`vilan/std/src/reactive.vl:1613`,
   `:1925`), and every one of kolt's coercions is one of its five
   `combine((a, b))` calls. Every dispatch through those pairs sits inside
   `Combine`'s tuple comprehension. The transformer emits that comprehension
   ONCE and shares it across every instantiation (`push_or_share`,
   `crates/vilan-core/src/transformer.rs:8971`). In kolt's client, one
   `source[1].get(source[0])` site serves all nine tables. Collapsing each key
   still leaves a site that sees nine types. It only pays if `Combine`'s body is
   also unrolled per element and un-shared per instantiation (§3).
3. **The census is not complete, and that must be fixed before anything relies
   on it.**
   - **A `dyn` nested in a container of an existing binding type-checks, then
     crashes on JS.** The shapes are a `List<Root>` variable passed as
     `List<dyn Src>`, an `Option<Root>`, a user generic struct, a closure
     variable, `push`, and index assignment (`x[1].get` is undefined at run time).
     Native refuses the same programs at rustc. Only the tuple case is filed
     (B430). The rest are unfiled, and they are an UNSOUND acceptance on JS
     today, whether or not M88 is ever built (§5.1).
   - **An `external fun` answering a `dyn` hands the program a pair nobody
     recorded.**
4. **A collapse is observable today.** `print` of a `dyn` prints the pair, as
   `[ [ 5 ], {} ]`, and the native backend reproduces that byte for byte on
   purpose (§5.4). A collapsed pair would print `[ 5 ]`.

**Rec: PARK M88 as filed.** File its prerequisites now, because each is a defect
on its own:

- **P1** the nested-`dyn` door family (UNSOUND), with B430;
- **P2** `print` of a `dyn` prints the value;
- **P3** the JS `type_key` gains a `Dyn` arm.

Revisit when a program has a single-occupant `dyn` dispatched on a hot path
OUTSIDE a shared generic body. A124's `dyn Source<T>` at app model fields, the
item's own motivating case, is exactly that. kolt has none today; its one `dyn`
parameter is unreachable (§2.2). If the owner wants `Combine` itself faster
first, §6 (b) is the form that pays there (**L**), and §6 (c) is a cheap
sibling (**S**).

## 1. Ground truth — what a `dyn` is today

### 1.1 Recording

`infer_type_inner` calls `note_dyn_coercion` at every inference exit
(`crates/vilan-core/src/analyzer.rs:35558`). It records a site
(`analyzer.rs:35576-35670`) only when all of these hold:

- the constraint is a TOP-LEVEL `Type::Dyn`;
- the inferred type is a struct, enum, tuple or array, or a rigid generic whose
  bounds provide the trait (B412, `:35598-35607`);
- the expression is one of `Local`, `Field`, `Index`, `TupleIndex`, `Call`,
  `StructInitializer`, `Dereference` (`:35616-35629`);
- the type implements the trait (`:35630`).

A resource is REFUSED at the same point (`:35632-35660`, trait-objects.md §8.3).
The map is `dyn_coercions: HashMap<Id, (TypeId, Id, Vec<TypeId>)>`. Dispatch
sites are recorded in `dyn_method_calls`, and the call graph counts each one as
`Indirect(TraitDispatch)`, which keeps every implementation of the member live
(`crates/vilan-core/src/call_graph.rs:1009-1019`).

### 1.2 JS

The pair is built in `walk_entity`, after the copy seams have run: `[value,
table]` (`transformer.rs:4636-4655`). A subject that is itself a `dyn` passes
through unwrapped (B412, `:4643-4651`).

`emit_vtable` (`transformer.rs:9397-9453`) memoizes on `(trait_id,
type_key(resolved type))`. The trait's ARGUMENTS are not in the key. The type is
resolved at emission (`:9398`), per instance, because the transformer is the
monomorphizer. The table renders as `const $x = Object.create({get: …, …});`,
with its slots on the prototype (`transformer.rs:12139-12156`, "the one
producer"). That comment records the one dispatch measurement the tree has:
"5.3-7.0x a direct call in node 24 at two and three types" for a bare literal
table, and on the prototype "the same site costs 2.0-2.9x (1.4-1.9x monomorphic)".

Dispatch is `x[1].member(x[0], …)` (`object_call_node`, `transformer.rs:9615-9636`).
The JS `type_key` (`transformer.rs:10927`) has no `Dyn` arm. A `dyn` key falls
through to `#{other:?}` (`:11009-11011`), the `Debug` spelling with raw type ids
(P3).

### 1.3 Native

A `dyn` is `vilan_rt::Dyn<dyn ObjectX>`, a counted `Rc` (`crates/vilan-rt/src/lib.rs:725-765`).
The emitter writes one Rust trait per `(trait, args)` (`ensure_object_trait`,
`crates/vilan-rust/src/lib.rs:8970`) and one impl per pair (`ensure_object_impl`,
`:9179`). Erasure is `Dyn::new(Rc::new(v))` (`erase_into_object`, `:3852`).
`rustc` does not, in general, devirtualize an `Rc<dyn Trait>` across a whole
program. That is general knowledge about rustc, not measured here.

### 1.4 What the item's questions dissolve into

- **Drop (item Q3).** A `dyn` is never a resource: "`check_dyn_coercion` refuses
  a resource at the coercion" (`analyzer.rs:10256-10266`). No drop slot exists on
  either backend, and a native `Dyn` drops as its `Rc` releases. The drop plan
  has no decision to share. (B431, a B412 erasure instantiated at a resource, is
  OPEN and is the one hole in that sentence.)
- **HMR.** A `dyn` is never transferred across a swap: "a trait OBJECT carries a
  vtable of emitted functions — the old module's functions"
  (`analyzer.rs:10545-10549`). A census that flips between two builds therefore
  cannot meet a live value from the previous build.

## 2. The measurement

### 2.1 Positions

- **std: two**, both `combine`'s mapped-tuple element: the `combine` parameter
  `(U in T: dyn Source<U>)` (`reactive.vl:1613`) and the `Combine.sources` field
  (`reactive.vl:1925`). Every other `dyn` in std is in a doc comment.
- **kolt: one**, `src/lib/reactive2.vl:42`
  (`fun inspect<T>(label: str, source: dyn Source<T>)`). No module imports that
  sketch, so neither entry reaches it.
- **kolt's `worktrees/connection-v3`: zero.** Its `common/src/lib.vl:41-42`
  `[expose]` fields are bare `Signal<List<..>>`, and an `[expose]` of a `dyn` is
  refused today (`doors/d20`).

### 2.2 Occupants per key, per leg

Method: `vilan build -d` on each program (a scratch copy), then
`dyn_census.py <prog>.analyze.out --js <emitted>`. The script groups
`dyn_coercions` by resolved `(trait, args)`, and resolves `combine`'s element
`U` from the subject's std impl. kolt's client was cross-checked against its
emitted tables (9 = 9). `sweep.sh` builds the 140 `vilan/test` programs, the 11
examples and the benchmarks, and counts `Object.create({`.

| program / leg | key | occupants | sites | where |
|---|---|---|---|---|
| kolt client | `Source<List<Command>>` | `Map<SignalCell<str>, str, List<Command>>` | 1 | `command_palette.vl:210` |
| | `Source<usize>` | `SignalCell<usize>` | 1 | `command_palette.vl:210` |
| | `Source<Option<Command>>` | `Map<Combine<..>, .., Option<Command>>` | 1 | `command_palette.vl:277` |
| | `Source<bool>` | `SignalCell<bool>` | 2 | `command_palette.vl:277`, `theme.vl:224` |
| | `Source<Theme>` | `SignalCell<Theme>` | 1 | `theme.vl:224` |
| | `Source<Option<Message>>` | `SignalCell<Option<Message>>` | 1 | `channel.vl:46` |
| | `Source<Option<User>>` | `Map<FlattenOption<..>, ..>` | 1 | `channel.vl:46` |
| | `Source<str>` | `SignalCell<str>` | 1 | `sidebar.vl:320` |
| | `Source<Option<f64>>` | `Map<SignalCell<str>, str, Option<f64>>` | 1 | `sidebar.vl:320` |
| kolt server | — | — | 0 | |
| `examples/todo` client | `Source<List<Todo>>`, `Source<str>` | one `SignalCell` each | 1 each | |
| `examples/reactive-ui` | the same two | one each | 1 each | |
| `test/dyn-objects.vl` | `Shape` | `Square`, `Rect` | 4 | |
| | `Source<i32>` | `SignalCell<i32>`, `Offset` | 3 | |
| every other test, example, benchmark | — | — | 0 | |

**Headline: 13 of 15 keys have a single occupant.** The owner's premise is
right: in practice a `dyn` has one implementor. All of it is `combine`.

## 3. The catch — where the dispatch actually is

Every dispatch through those 13 keys happens in `Combine`'s two tuple
comprehensions: `get` (`reactive.vl:1929-1931`, `(source in self.sources =>
source.get())`) and `on_settle` (`:1942-1943`). kolt's emitted client has each
comprehension exactly ONCE (from a scratch build, `dist/client.js:5577-5596`):

```js
function $lH(self) {
	return self[0].map((source) => {
		return source[1].get(source[0]);
	});
}
```

`push_or_share` (`transformer.rs:8971`) merges instance bodies that render
identically. Once dispatch goes through a table, every `Combine<T>` body renders
the same, so all five `combine` instantiations share this one function. Its call
site therefore sees all nine tables. Their prototypes are distinct, 7 slot sets
among 9 tables (three `SignalCell` tables share every slot function), so the
site is megamorphic by V8's measure.

Collapsing each key, as filed, changes the pair's construction and nothing at
this site. For the direct call to appear, the emitter must:

1. **Unroll** the comprehension over a heterogeneous tuple into one expression
   per element, so each element's call has one static type;
2. **Un-share** the `Combine` instance bodies, which `push_or_share` exists to
   merge;
3. **Emit, per element, the call its key's single occupant resolves to.**

That is a monomorphization of `Combine` over its element types, which is the
opposite of what A124 R3 chose `dyn` for: the per-element existential, A33.
It is a legitimate design (§6 (b)), and it is L, not the M the item sized.

## 4. What a collapse would buy, measured

- **The tree's own number.** A table call on the prototype costs 1.4–1.9× a
  direct call monomorphic, and 2.0–2.9× at two or three types
  (`transformer.rs:12147-12153`). That is per call, and this is the upper bound
  of the dispatch win.
- **A non-escaping pair.** `bench/bench_dyn.vl` against `bench_direct.vl` (20 M
  iterations, each builds a `Holder { s: dyn Step }` and calls through it). CPU
  time over five alternating runs: 72–88 ms against 70–81 ms. **No difference
  above noise.** V8 removes a pair that does not escape and inlines the
  monomorphic table call.
- **An escaping pair.** `bench_dyn2.vl` against `bench_direct2.vl` (2 M holders
  kept in a list, then dispatched through 10 rounds). Median CPU **672 ms against
  519 ms (≈1.3×)** over five alternating runs, on a loaded machine (the spread
  was 658–1307 against 483–885). This is the allocation and the extra
  indirection of a stored pair.
- **kolt.** Its pairs are built once per `combine` call, when the node is made,
  and dispatched per pull and per attach through the shared megamorphic site. The
  collapse as filed removes nine small allocations per `combine` construction
  and nothing per pull.

The item asked for a callgrind before/after on kolt's client and the A124
exhibit. That run was not done, because there is no build to measure: §3 shows
the filed collapse emits identical code at every site kolt dispatches through.
The method, for the day it matters, is Order 40's per-iteration slope
(`sweeps/order40/reactive-40/a124_measurements.md:9-17`,
`sweeps/order38/reactive-38/measure-ir.sh`).

## 5. The item's questions, answered

### 5.1 Q1 — is the census complete? No.

Each probe prepends `trait Src { fun get(self): i32; }` and `struct Root` with an
impl. Every probe type-checks cleanly with `vilan check`, except the closed
doors marked as refused.

| probe | shape | JS | native |
|---|---|---|---|
| `d1` / `d1b` | a `List<Root>` variable, or a call result, into a `List<dyn Src>` position | **crash**, `x[1].get` undefined (re-run for this paper) | rustc E0308 |
| `d3` | an `Option<Root>` variable into `Option<dyn Src>` | **crash** | E0308 |
| `d12` | a `Box2<Root>` (user generic) into `Box2<dyn Src>` | **crash** | — |
| `d4` (= B430) | a tuple variable into `(dyn A, dyn B)` | **crash** | — |
| `d2` | a closure VARIABLE `\|\| Root` into `\|\| dyn Src` (a closure literal, `d2b`, is fine) | **crash** | refused by name |
| `d24` / `d25` | `List<dyn Src>.push(Root { .. })`, including on a field | **crash** (re-run) | E0308 |
| `d26` | `xs[0] = Root { .. }` on `List<dyn Src>` | **crash** | E0308 |
| `d5` | `external fun make(): dyn Src`, where the HOST mints the pair | runs, invisible to the census | refused by name |

The root cause: `reconcile_type` unifies a nested `Dyn` against a concrete
argument (`analyzer.rs:38643-38700`), while `note_dyn_coercion` records only a
top-level `Dyn` expectation (§1.1). The nested shapes are accepted and never
erased.

**This is P1.** File it now as one UNSOUND item beside B430, in the solver's
family. There are two doors. (a) Erase element-wise by projection (B430's own
fix), which is only possible for a tuple, an `Option` and a struct literal.
(b) REFUSE a nested `dyn` against a non-`dyn` argument, with a steer to map
(`roots.map(|r| r)` into `List<dyn Src>` works today, `d22`). Rec: (b) for
`List` / `Option` / user generics / closures / `push` / index assignment, and
(a) for tuples as B430 says.

The closed doors: an `[rpc]` returning a `dyn` is refused as "not Wire" (`d21`);
an `[expose]` of a `dyn` is refused (`d20`); bindgen never emits `dyn`.
`[derive(Json)]` on a `dyn` field (`d17`) and a `const` `dyn` (`d18`) are
DIAGNOSTIC bugs, not doors: the macro emits invalid vilan, and const-eval reports
"`$a` is not defined".

For M88, the rule is that a key reachable from an extern's `dyn` return (`d5`) is
never collapsed, because the host hands the program a pair.

### 5.2 Q2 — generics: resolved keys, which means a pre-pass

The transformer resolves each table at emission, per instance (`:9398`). One
recorded site with a generic subject emits two tables (`doors/d9_generic`). The
census must run over RESOLVED keys, which means over instances, and it must be
complete before the first coercion site is emitted, because a later instance can
add a second occupant. That makes emission two-phase: a walk over the instance
set that computes the key census, then emission. The walk is the size driver of
the build (M).

### 5.3 Q3 — drop

Dissolved (§1.4).

### 5.4 Q4 — observability: yes, today

- **`print`.** `print(a)` where `a: dyn Src` prints **`[ [ 5 ], {} ]`**
  (`doors/d13`, re-run). `test/dyn-objects.vl`'s golden prints
  `[ [ [ 3 ], {} ] ]`. The native backend reproduces the pair on purpose:
  `impl Js for Dyn` renders `js_tuple(&[object, "{}"])`
  (`crates/vilan-rt/src/lib.rs:777-781`). The native differential byte-compares
  dyn-objects.vl (`crates/vilan-cli/tests/native_differential.rs:98-129`). A
  collapse changes stdout. **P2:** a `dyn` prints as its value on both
  backends. A `{}` is not information, and printing it leaks the representation
  the item wants to be free to change. The golden move is one line, on both
  sides.
- **`impl dyn Src { .. }`** is admitted (`doors/d16`), and its body is emitted
  with the pair as receiver (`self[1].get(self[0])`). A collapse must re-emit
  those bodies for the bare value.
- **Clone.** `__clone` of a pair copies the value and keeps the table, which is
  equivalent to cloning the bare value.
- **`==`** on a `dyn` is refused (`doors/d8`), and a derived `PartialEq` over a
  `dyn` field is refused (`d14`).
- **Identity.** Native `PartialEq for Dyn` is `Rc::ptr_eq`, but no vilan-level
  path reaches it.
- **Not found:** `is`, downcast, reflection.

### 5.5 Q5 — native

The same census applies. The collapse on native is a TYPE change: a
`Dyn<dyn ObjectX>` field or parameter becomes the concrete type, and
`Dyn::new(Rc::new(v))` disappears. The by-name refusals (`&mut self`, async,
view-returning slots) are untouched. Build it on JS first, because the
differential is the proof.

### 5.6 Q6 — the switch

Yes, if the collapse is built: `VILAN_DEVIRT=0`, and `native_differential` runs
the dyn goldens both ways.

### 5.7 What breaks a collapse after it ships

- **A second coercion added later.** Every site of that key flips back to pairs.
  That is a cost cliff and golden churn, and never a change in meaning. The
  owner's framing ("the cliff is the second implementor arriving, which is
  exactly when a vtable is earned") stands.
- **HMR.** Safe, per §1.4.
- **Bundle splitting.** The census is per LEG, over the whole program the leg
  builds, lazily loaded chunks included. A second occupant that lives only in a
  lazy chunk still counts.

## 6. Options

- **(a) M88 as filed** (per-key collapse at coercion and dispatch).
  - Pays for a dispatch site outside a shared generic body with one occupant.
    The estate has none today.
  - Sized M: census pre-pass, two emitter seams, `impl dyn` re-emission, the
    native type swap, the differential.
  - **Park** until the trigger in §0.
- **(b) (a) plus `Combine` specialization.**
  - When every element key of a `Combine<T>` instantiation has a single
    occupant, emit that instance's `get` / `on_settle` with the comprehension
    unrolled per element and direct calls, un-shared from the other instances.
  - The only form that pays in kolt. Sized **L**, with a bundle-size cost
    (`push_or_share`'s merge is given up for those instances), measured under
    Order 40's slope method.
  - The owner's call, if `combine` becomes hot.
- **(c) Table dedup by slot set.**
  - Two tables whose slots are the same functions are one table. kolt's 9 would
    become 7, and the shared site would see fewer classes.
  - Sized **S**, with no census and no observability question.
  - A small, honest win at the one site the estate has. Recommended as a hygiene
    item, independent of M88.
- **(d) Enum dispatch for 2..N occupants.** The item's "beyond one", priced
  separately. Not now.

## 7. Sizing

| piece | size |
|---|---|
| P1 nested-`dyn` doors: refuse, or erase for tuples, with red-first pins (UNSOUND) | S–M, solver |
| P2 `print` of a `dyn` prints its value, both backends, one golden line each | S |
| P3 the JS `type_key` gains a `Dyn` arm | S |
| (c) table dedup by slot set | S |
| (a) M88 as filed | M, after P1–P3 |
| (b) `Combine` specialization | L |

## 8. For the owner

- **Q1 — park M88 as filed, on the measurement?** Rec: yes. 13 of 15 keys are
  single-occupant, but none is dispatched outside `Combine`'s shared body.
- **Q2 — file P1 now as UNSOUND, beside B430?** Rec: yes, whether or not M88 is
  ever built. The nested-`dyn` shapes type-check and crash on JS today. Rec:
  refuse with a steer to `.map(|r| r)`, and erase element-wise for tuples as
  B430 says.
- **Q3 — P2: print a `dyn` as its value?** Rec: yes. It is the prerequisite for
  ANY representation change of `dyn`, this one included.
- **Q4 — (c) table dedup as a hygiene item?** Rec: yes, S.
- **Q5 — (b) `Combine` specialization?** Rec: not until an exhibit shows
  `combine` hot. Recorded here so the day it is wanted it starts sized.
