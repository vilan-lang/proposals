# Views in closure types — carry `&`/`&mut` in `Type::Closure`, not in a side table (B495)

> Status: **DRAFT 2026-10-03 — for the owner's ruling.** Written by lane papers-46 of Order 46
> against `vilan 0.43.0 (fe092e8d1)`, reading the compiler at the tag (`v0.43.0`, a408d5db).
> Nothing changed. JS rows were run. Native rows are the emitted Rust
> (`vilan build --backend rust --stdout`), read and not built, because cargo was off limits
> this order. rustc's verdict is stated only where the emitted signature makes it certain.
>
> Probes: `scripts/integration/sweeps/order46/papers-46/probes/views/`, re-run by
> `probes/run_all.sh`, output in `probes/run_all.out`. Cited as `vN`.
>
> Related:
> - B495 (this paper), F69 (the native face of it);
> - B465 / B467 (Order 45: the adoption pass and the field-escape fix, built on the side
>   table);
> - B309 (the `context` clause moved INTO `Type::Closure`, the precedent);
> - B400 (closure-typed callee views), F18 slice 3 (`SignalCell::update`'s `&mut` signature);
> - `store.md` §3.1 (the lend `|(|&T| void)| void` the Store's read path is built on).

## 0. The ask, and the answer up front

A closure type may take views: `|&str| void`, `sync |&mut T| void`. The analyzer erases the
`&` when it walks the type ("a view is tracked beside the type, never in it") and records the
views in `closure_type_parameter_views: HashMap<TypeId, Vec<Option<bool>>>`, keyed by the
WRITTEN annotation's type id. Types are not interned: each walk mints a fresh id
(`type_id_for_type`). So the entry belongs to one written annotation. Any type that was
copied, reconciled or substituted from it is a different id with no entry.

**The answer.**

1. **It miscompiles on JS today, not only natively.** A let-bound literal re-typed by an
   annotation (`let typed: |&str| void = h`) receives the caller's place pair and stores it as
   the value: `out=Oslo,0` (v1). The same happens through a generic identity function (v3),
   through an annotated `let` whose initializer IS the literal (v7b; B465 lists that position
   as adopting), and when a by-value closure is bound where the type takes a view (v2). The
   item named F69 (native) as the face; the JS face is a silent wrong value.
2. **The type cannot tell a view closure from a value closure.** `|str| void` and `|&str| void`
   are the same `Type`, so each binds to the other with no diagnostic (v2).
3. **The native backend loses views in two ways.** At a call through a match capture, a loop
   binding or a generic struct's field (v8, v5), it passes a value to an `Fn(&mut i32)`, so
   rustc must refuse (F69). Through a generic return it erases the view on both sides and
   builds by value (v3).
4. **There is a precedent for the fix.** B309 moved the `context` clause from a side band keyed
   by parameter id into `Type::Closure(params, ret, contexts)`, for the same reason: a side
   band "flowed through no field, generic argument or return".

**Recommendation: door (b).** `Type::Closure` gains a fourth slot, the parameters' MODES
(`Vec<Option<Mode>>`, with `Mode` one of value, view and mutable view; `None` means a literal's
parameter that was never written). Reconciliation keeps a written mode and lets an open one
adopt it, exactly as it keeps a clause today. Two WRITTEN modes that differ are refused, which
closes v2. The side table and the post-inference adoption pass are deleted. The emitters read
the type. The cost is mechanical: about 69 destructuring sites in `analyzer.rs` gain a `_`, one
in `mono.rs`, one in `transformer.rs`, and 14 in `vilan-rust`, of which 4 read the side table
today. One new diagnostic row is added. One behaviour changes: v2's silent rebinding becomes a
refusal. The estate has no annotated shape of it (§6), and S1 counts the rest before landing.

## 1. Ground truth (0.43.0)

### 1.1 Where the views live

- **Recorded:** `walk_type_node`, the `Node::ClosureType` arm (`analyzer.rs:37781`). If any
  parameter is a `Node::Reference`, the type's FRESH id gets an entry. The `Type::Closure` it
  builds carries no views.
- **Read, by the analyzer:**
  - `adopt_closure_parameter_views` (`:28940`, B465). It runs once after inference. A bare
    literal parameter takes the view of the written position it lands in: a callee's declared
    parameter, a struct literal's field, or an annotated binding.
  - `closure_callee_views` (`:29085`, B400). At a call through a closure-typed value, it reads
    the views off `closure_value_type_id`: the parameter's, the local's or the field's
    `type_id`.
- **Read, by the native emitter:**
  - `write_type_key` (`lib.rs:1631`), so a view closure keys apart;
  - the closure SIGNATURE (`:2157`, `&`/`&mut` before each viewed parameter);
  - `closure_call_arguments` (`:9655`), which passes a place for a viewed parameter and reads
    the views off `self.concrete(type_id)`;
  - `reentrant_view_read` (`:9539`).
- **Lost, by construction:** `reconcile_type`'s closure arm (`:43691`) builds a NEW
  `Type::Closure` from the reconciled parameter ids. The comment above it says the arm keeps
  "whichever side has" a clause. Nothing like that exists for views, because they are not in
  the type. A substitution (`concrete`, a generic's instantiation) produces another id. A
  binding whose `type_id` is re-pointed at its initializer's type loses the annotation's id.

### 1.2 What happens, shape by shape

| Probe | Shape | JS (run) | Native (emitted, not built) |
|---|---|---|---|
| v6 | bare literal handed to a `fun` parameter `f: \|&mut i32\| void` | `n=11`, right | — |
| v9 (a) | bare literal handed to a `fun` parameter `f: \|&str\| void` | `Oslo`, right | `fn with_city(.., f: Rc<dyn Fn(&Str)>)` |
| v9 (c) | bare literal in a struct field written `\|&str\| void` | `Oslo`, right | `f: Rc<dyn Fn(&Str)>` |
| v9 (b) | annotated `let`, the view SPELLED on the literal (`\|c: &str\|`) | `Oslo`, right | `Fn(&Str)` |
| **v1** | `let h = \|c\| ..; let typed: \|&str\| void = h; typed(&home.name)` (the item's repro) | **`out=Oslo,0`**: the emit is `typed([ home, 0 ])` into `const h = (c) => { out.v = c; }` | refused: "does not emit a value of type `an unresolved type`" (h's parameter) |
| **v7b** | annotated `let`, BARE literal as the initializer, read view | **`out=Oslo,0`** | — |
| **v7** | the same with `\|&mut i32\| void` and `x += 100` | refused: "cannot mutate immutable 'x'" | — |
| **v3** | `let f: \|&str\| void = hold(\|c\| ..)` with `fun hold<T>(x: T): T` | **`out=Bergen,0`** | the view is erased on both sides: `fn hold_0(x: Rc<dyn Fn(Str)>)`, closure `\|c: Str\|`; builds by value |
| **v2** | `let as_view: \|&str\| void = by_value` with `by_value: \|str\| void`; and the reverse | **`out=Oslo,0`**; the reverse prints `Oslo` | both erased: `Fn(Str)` |
| v4 | BARE literal stored in `Option<\|&mut i32\| void>` / `List<..>` (`x += 10`) | refused: "cannot mutate immutable 'x'" (a nested written position: no adoption) | — |
| v8 | view SPELLED on the literal, stored in `Option<\|&mut i32\| void>` / `List<..>`, called through a match capture / a loop binding | `11`, `111`, right | literal `Fn(&mut i32)`, but the call is `(f)((c.n).clone())`: a value into `&mut i32`, rustc E0308 (F69) |
| v5 | spelled, in a generic struct `Holder<\|&mut i32\| void>`, called `(h.f)(&mut n)` | `n=6`, right | field `Fn(&mut i32)`, call `(h.f)((n).clone())`: E0308 (F69's shape, through a generic field) |

The pattern:

- A written position that is still the annotated id works: v6, v9, v8 on JS, v5 on JS.
- Every path that copies or reconciles the type loses the views: v1, v3, v7, v7b on both
  backends; v4, where the written type is nested in `Option`/`List` and the literal never
  meets it directly; v8 and v5 natively, where the call site reads a substituted id.
- v2 is the hole the type cannot express at all.

v7 also shows an ORDER problem. The mutability check runs during inference, before the
post-inference adoption pass, so an adopted `&mut` is refused before it is adopted.

## 2. What breaks, by cause

1. **Copy.** A binding's type is unified with its initializer's, and the annotation's id is
   not the one the call site reads (v1, v7, v7b). JS: the caller passes the place pair
   (`closure_callee_views` found the annotation's entry), while the literal's parameter
   stayed bare. That is a wrong value. Native: refused, or a value passed to a reference.
2. **Substitution.** A generic parameter instantiated at a view closure type (v3: `T` in
   `hold<T>`) is the reconciled type: fresh parameter ids, no entry. JS miscompiles; native
   erases consistently and happens to build.
3. **Identity.** The view is not part of `Type`, so `Type`'s derived `Eq`/`Hash` and every
   memo keyed on them (`impl_select`'s buckets, the analyzer's structural comparisons,
   `same_type_structure` at `:7128`) treat `|str| void` and `|&str| void` as one type (v2).
   Only the native key adds the views back by hand (`write_type_key`), and only when the id
   it holds is the annotated one.
4. **Order.** Adoption is a pass after inference, and the checks inside inference (mutability)
   have already run (v7).

## 3. The candidate representations

### (a) Keep the side table, and propagate it

Copy the entry wherever a closure type id is copied: reconciliation, substitution, `concrete`,
a binding re-pointed at its initializer, a field's instantiation, the return of a generic.
There are 69 `Type::Closure(` sites in `analyzer.rs` alone. Each new flow path is a new place
to forget, which is how B465, B467 and F69 each happened. It also cannot express v2: two types
equal by `Eq` would still need a side-table comparison wherever equality is asked.
**Declined.**

### (b) Modes in the type (the B309 precedent)

```rust
pub enum Mode { Value, View, MutView }
Closure(Vec<TypeId>, TypeId, Vec<Id>, Vec<Option<Mode>>)
//      parameters,  return, contexts, modes (None = a literal parameter nobody wrote)
```

- **Walked types** get `Some(Value | View | MutView)` for every parameter. A written closure
  type has no open parameter.
- **Closure literals** get `Some(..)` where the parameter is spelled (`|c: &str|`,
  `|x: &mut i32|`, `|c: str|`) and `None` where it is bare (`|c|`).
- **Reconciliation** (`:43691`, and the three structural comparisons at `:7128`, `:10114`,
  `:40313`, `:44007`):
  - `None` against `Some(m)`: the result is `Some(m)`, and the literal's parameter takes
    convention `m`. This is adoption, at inference time. It replaces the B465 pass and fixes
    v7's order.
  - `Some(m)` against `Some(m)`: `Some(m)`.
  - `Some(m)` against `Some(n)` with `m != n`: no match. A new refusal row (§5) says which
    parameter disagrees and how to adapt it (`|c| f(*c)`).
- **Substitution** carries the modes with the type. `hold<T>` at `|&str| void` is `T :=
  Closure(.., [Some(View)])` (v3).
- **`Eq`/`Hash`** see the modes, so memo keys and `same_type_structure` separate the two
  closures with no extra code. The native key reads them off the type.
- **The literal's `Parameter.convention`** stays the emitters' per-parameter truth. It is set
  once, when its mode resolves, and never changes after.

### (c) A `View` type node in parameter position

`|&mut T| void` walks to `Closure([View(T, mut)], ..)`, with `Type::View(TypeId, bool)` a new
type. Views would flow with types everywhere for free. That is the problem: `T` in
`hold<T>(x: T)` could be instantiated at `View(str)`, a `List<View(str)>` would be a type, and
every type match in the solver would meet the node. The language's rule that a view "is
tracked beside the type, never in it" exists to keep views out of generic arguments, fields
and collections (the escape rule). (b) keeps them in the ONE type constructor whose
parameters are positions, not values. **Declined.**

### (d) Native reads the argument's `&` at the call site (F69's alternative)

`closure_call_arguments` would pass a place whenever the argument is spelled `&`/`&mut`,
whatever the type says. This fixes v8 and v5 natively, and nothing else. JS v1, v3, v7b and
the v2 hole remain. It also lets a call site's spelling, not the callee's type, decide the
calling convention. **Declined as the fix.** It is acceptable as a stopgap for F69 if (b) does
not land in the same order.

## 4. What (b) costs

| Where | Today | Under (b) |
|---|---|---|
| `type_.rs` | `Closure(Vec<TypeId>, TypeId, Vec<Id>)` | a fourth field, and `Mode` |
| `analyzer.rs` | 69 `Type::Closure(` sites; 1 insert into the side table; 4 reads; the adoption pass (~90 lines, `:28940`–`:29105`) | the 69 sites gain a `_` or pass the modes along (≈10 do real work: the walk, the 5 reconcile/compare arms, the literal's type, `closure_callee_views`, the context threading at `:21832`/`:44207`); the side table, the pass and `closure_value_type_id`'s view lookup go |
| inference | adoption after the fixpoint | adoption inside reconciliation: one `Option` merge per parameter per closure reconcile, the cost class of the clause merge already there |
| `mono.rs`, `impl_select.rs`, `async_infer.rs`, `context.rs`, `const_eval.rs`, `contract_hash.rs`, `hint_labels.rs`, `vilan-ide` completion | 1 + 3 + 4 + 2 + 1 + 1 + 2 + 1 sites | destructuring arity only. `contract_hash` and `hint_labels` render the `&` (a hover of `\|&str\| void` stops saying `\|str\| void`) |
| JS emitter (`transformer.rs`) | 1 site; reads conventions through the analyzer's tables | unchanged: it reads parameter conventions, which (b) settles earlier |
| native emitter (`vilan-rust`) | 14 sites, 4 side-table reads, `concrete()` loses the id | the 4 reads read the type; `concrete()` preserves the modes because they are in the type; F69 closes |
| module reuse | the side table is whole-program `Program` state, re-derived per analysis | nothing to re-derive: modes live in the type map that reuse already restores |

New diagnostic, one row: "this closure takes `str` by value where the type takes a view
`&str`". It carries a quick fix that rewrites the literal's parameter to the type's mode when
the literal is right there, or wraps the value (`|c| f(*c)`) when it is not.

## 5. Behaviour that changes

- **v2 becomes a refusal** in both directions. A by-value closure bound to a view type
  miscompiles on JS today. A view closure bound to a value type prints the right value on
  JS today, but only because `*c` of a non-view happens to read through. It is still a
  convention mismatch, and natively both were erased. BREAKING for a program that relies on
  either direction.
- **v1, v3, v7, v7b become right on both backends.** v7 starts compiling.
- **v8, v5 build natively** (F69).
- **Hover and inlay hints print the `&`** inside closure types.

## 6. The estate

There is one breaking edge: a WRITTEN by-value closure type meeting a written view type. A
census at the tag (grep, run for this paper):

- **annotated bindings of a view closure type** (`let x: |&..| ..`): **0** in std, **0** in
  kolt, **0** in the corpus's `.vl` fixtures;
- **view closure types in std positions** (`: |&T| ..` / `: sync |&mut T| ..`, parameters and
  fields): **40**. They include `SignalCell::update`'s `sync |&mut T| void` and `Store`'s
  lends and `modify`. They receive literals, which adopt, or values forwarded from a position
  of the same written type, which match;
- **kolt** spells the view on the literal's parameter: three `update(|&mut ..| ..)` sites
  (`account.vl:21`, `store.vl:257`, `store.vl:271`). Written and equal, they are unaffected.

The census cannot prove that no by-value closure value flows into one of the 40 positions.
Only the build's own refusal can. S1 runs the estate (std's gates, kolt's `vilan check`, the
corpus) and reports the count before it lands. If the count is not zero, the refusal ships
as a warning for one release (Q2's fallback).

## 7. Interactions

- **B309's clause** sits beside the modes and merges the same way. A closure type with both
  is legal (`(sync |&mut T| void) context owner_scope`).
- **B467's escape rule**: a closure's own view parameters are not captures. Unchanged, and
  now readable off the type instead of the side table.
- **`store.md` §3.1, the lend.** `Store`'s `lend: |(|&T| void)| void` nests a view closure
  type inside a closure parameter. Today that inner type's views reach the native signature
  only while its id is the annotated one. Under (b) the nesting is a type like any other.
- **A future "readonly by default" flip** for bare parameters (`node.rs` `Convention`'s doc
  anticipates one). Under (b) it would be a change to what `Mode::Value` means in one place.
  Under the side table it would be another set of propagation sites.

## 8. Finds (met while probing, for the integrator to file)

1. **An annotated `let` whose initializer is a bare closure literal does not adopt the
   annotation's views**, although B465 names "an annotated binding" as an adopting position.
   With a read view, `let typed: |&str| void = |c| { out = *c; }; typed(&city);` prints
   `out=Oslo,0` on JS (the place pair). The write-view twin is refused, "cannot mutate
   immutable 'x'". The same literal handed to a `fun` parameter or a struct field adopts
   correctly (v9). Repro: `probes/views/v7b_let_literal_read.vl`, `v7_let_literal_adopt.vl`.
   Root: this paper (the binding's `type_id` is not the annotation's id when the pass reads
   it). The read case is a silent JS miscompile, so it wants a pin whatever door is chosen.
2. **(Noted, B495 itself)** v1 and v3 are silent JS miscompiles, and v2 is accepted in both
   directions. They are B495's own symptoms, listed here so the integrator can widen B495's
   title to "miscompiles on JS, refuses natively".

## 9. Open questions, each with a recommendation

- **Q1. The representation.** Re-key the side table, modes in `Type::Closure`, a `View` type
  node, or native-only call-site reading. **Rec: modes in `Type::Closure`** (§3 (b)).
- **Q2. A written mode against a different written mode.** Refuse, or adapt implicitly (insert
  a `*` thunk for value-into-view; refuse the reverse). **Rec: refuse both, with a quick fix.**
  An implicit adapter hides a copy, and the reverse cannot be adapted soundly (a value closure
  that writes its parameter would write a temporary). Fallback, if S1's estate count is not
  zero: a warning for one release, then the refusal.
- **Q3. Where adoption happens.** Keep the post-inference pass (fed by the type), or adopt
  inside reconciliation. **Rec: inside reconciliation.** It fixes v7's order, and it is where
  the clause already merges.
- **Q4. Do modes take part in `Eq`/`Hash` of `Type`?** **Rec: yes.** They are different
  calling conventions, and the native backend already keys them apart by hand.
- **Q5. F69 before (b)?** If (b) does not land in the same order as a native fix, take door
  (d) as a stopgap for F69 only. **Rec: land (b) and close F69 with it.** The stopgap leaves
  the JS miscompiles.

## 10. Slices

| Slice | Content | Size | Needs |
|---|---|---|---|
| S1 | `Mode`; the fourth field; the walk writes modes; literals write `Some`/`None`; the 5 reconcile/compare arms merge and refuse; the refusal row; delete the side table and the B465 pass; pins v1, v2 (both directions), v3, v7, v7b on JS | M | — |
| S2 | Native: the 4 reads read the type; F69's pins (v8, v5, the B467 depth pin) on both backends | S | S1 |
| S3 | Hover, hints and contract-hash render print the `&`; the quick fix | S | S1 |

S1 is breaking only for v2's shape: no annotated site in the estate, and S1 counts flowed values before landing (§6).
