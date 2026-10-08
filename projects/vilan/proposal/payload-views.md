# Payload views — a pattern that binds a writable view into an enum payload (B509)

> Status: **DRAFT 2026-10-03 — for the owner's ruling** (R-k carried B509's ruling to Order 47.
> This paper is what that ruling reads). Written by lane papers-46 of Order 46 against
> `vilan 0.43.0 (fe092e8d1)`, reading the compiler and std at the tag (`v0.43.0`). Nothing
> changed. JS rows were run. Native rows are the emitted Rust
> (`vilan build --backend rust --stdout`), read and not built, because cargo was off limits
> this order.
>
> Probes: `scripts/integration/sweeps/order46/papers-46/probes/payload/`, re-run by
> `probes/run_all.sh`, output in `probes/run_all.out`. Cited as `bN`.
>
> Related:
> - B509 (this paper; store-45's find, building `StoreSome::patch`);
> - `store.md` §2.6 and Q6 (through-variant writes); A149 (the write-back under a match
>   binder "goes with B509");
> - rule 4 (no invalidating mutation under a live view); the view-escape rule;
> - `for e in &mut list` (the loop's view binding); the wrapped-view captures
>   (`fun get(..): Option<&mut T>`, `wrapped_view_captures`).

## 0. The ask, and the answer up front

Vilan can bind a writable view into a list element (`for e in &mut list`) and into the payload
a `borrows` call returns (`match arena.get(i) { Some(let v) => .. }`). It cannot bind one into
the payload of an enum PLACE. So std writes through a variant by copying the payload out and
writing it back.

**The answer.**

1. **The copy is real, and it is two deep copies on both backends** for the derive's enum
   write step (b7). 2,000 writes of one scalar inside a payload holding a 10,000-element list
   take **420–470 ms** on JS, against **0–1 ms** for the same write through a `&mut` lend. The
   JS emit is `let p0 = __clone($a[1]); f(p0); __replace(held, [ 0, __clone(p0) ])`. The
   native emit is `match (held).clone() { E::A(mut p0) => { f(&mut p0); *held =
   E::A((p0).clone()); } }`.
2. **`Option`'s step is cheaper but not safe.** `store.vl` writes `match held.take() {
   Some(mut payload) => { f(&mut payload); held = Some(payload); } }`, which is moves, not
   clones, on both backends (b1, b6). While `f` runs, the place holds `None`. A panic inside
   `f` loses the payload.
3. **The spelling the language already suggests is accepted, does the wrong thing, and steers
   to a silent no-op.** `match &mut held { Some(let p) => p.x = 2 }` parses. Its capture is a
   COPY, and the refusal says "declare it `mut`". `Some(mut p)` then compiles and the write
   does not land (b2, b1; find 1).
4. **The pieces exist.**
   - The wrapped-view capture already binds a payload as a view, `(mutable, scalar)`, on both
     emitters (b4).
   - Rule 4 already refuses an invalidating write under a loop's view (b8).
   - Rule 4 does NOT guard the wrapped-view capture today. Replacing the list under a live
     capture loses the write silently (b9, find 2).

**Recommendation: the subject carries the mode** (§3, door A).

- `match &mut place { V(let p) => .. }` binds every `let` capture as a WRITABLE view into its
  payload slot, and `match &place` binds read views. The `is` form is the same:
  `&mut held is Some(let p)`.
- This is `for e in &mut list`'s rule, applied to a match.
- A `mut` capture under a reference subject is refused, because it would be a copy that looks
  like a write.
- Rule 4 guards the subject place for the capture's live range, and the wrapped-view capture
  gets the same guard (find 2).
- Today's spelling `match held { .. }` keeps its copy semantics, so nothing that compiles
  changes meaning. A census finds zero `match &`/`match &mut` sites in std, kolt and the
  corpus.
- std's `Option` step and the derive's single-payload enum step then write in place.

## 1. Ground truth (0.43.0)

### 1.1 The spellings, run

| Probe | Spelling | Result |
|---|---|---|
| b1 (1) | `match held { Some(mut p) => p.x = 2 }` | compiles; **the write does not land** (`held.x=1`): `mut p` is a copy (JS `let p = __clone($a[1])`) |
| b1 (2) | `match held.take() { Some(mut p) => { p.x = 3; held = Some(p); } }` | lands (`held.x=3`); moves on both backends (JS `__option_take`, native `.take()`) |
| b2 | `match &mut held { Some(let p) => p.x = 2 }` | **refused**: "cannot mutate immutable 'p'; declare it `mut` to allow mutation." Following the steer gives b1 (1): a silent no-op |
| b12 | `match held { Some(let p) => p.x = 2 }` with `held: &mut Option<P>` (a view subject: `store.vl`'s shape) | refused, the same message |
| b12b | `match &mut held { Some(let p) => read p.x }` with `held` a `&mut` parameter | compiles (`read p.x=1`); the capture is a copy |
| b10 | `match &held { Some(let p) => read p.x }` | compiles; no clone is emitted (a read binding is not copied) |
| b3 | `Some(&mut p) =>` | parse error: "found '&' expected a pattern" |
| b3b | `Some(&mut let p) =>` (the item's sketch) | parse error, the same |
| b4 | `match first(&mut bag) { Some(let p) => p.x = 7 }` with `fun first(bag: &mut Bag): Option<&mut P>` | lands (`7`): the wrapped-view capture |
| b4 | `for e in &mut bag.items { e.x += 1 }` | lands (`8`) |
| b5 | `fun some_mut(o: &mut Option<P>): Option<&mut P> { match o { Some(let p) => Some(&mut p), .. } }` | refused: "a view cannot escape its scope … carried in an enum payload", and "cannot take a writable view of immutable 'p'". The wrapped-view route cannot reach an `Option` PLACE without this paper's pattern |

### 1.2 What the copy costs (b6, b7)

| Write shape (2,000 writes of `x`, payload holding a 10,000-element list) | JS, three runs | what is emitted |
|---|---|---|
| `Option`: `take()`, write, put back (b6) | 0–7 ms (noise; same as the direct arm) | JS `__option_take`, no clone; native `.take()`, moves |
| the derive's enum step: `match held { E::A(mut p0) => { f(&mut p0); held = E::A(p0); } }`, `held: &mut E` (b7) | **420–470 ms** | JS `__clone($a[1])` in, `__clone(p0)` back; native `(held).clone()` in, `(p0).clone()` back |
| the same write through a `&mut` lend, no variant (b7) | 0–1 ms | `f(held)` / `(f)(&mut *held)` |

The second clone of the write-back copies `p0`, which is dead after the assignment. That is a
copy-elision miss whatever this paper decides (find 3). Native timings were not taken.

### 1.3 Where std pays it

- `store.vl:759–806`: `Store<Option<P>>::some()` and `StoreSome<Option<P>>::some()`, the
  `take()`/put-back step. Every A149 S3 keyed child is a `Store<Option<V>>`, so every field
  write under `at(k).some()` passes through it.
- `store_enum_impls` (`store.vl`, the `write` closure the derive emits per payload variant):
  `V(mut p0) => { f(&mut p0); held = V(p0); }`, and for a multi-payload variant
  `mut payload = (p0, p1, ..); f(&mut payload); held = V(..)`. Two deep copies per write
  (§1.2).

### 1.4 The rules a payload view must obey, as they stand

- **Rule 4** (b8): "cannot reassign 'list' while a view into it is live (rule 4: no
  invalidating mutation under a live view)", inside a `for e in &mut list` body.
- **The view-escape rule**: a view "may not be returned, stored in a field, placed in a
  collection, or carried in an enum payload" (b5's refusal text). Wrapped captures are view
  bindings for it (`view_bindings.extend(self.wrapped_view_captures.keys())`,
  `analyzer.rs:24587`).
- **The hole** (b9): a wrapped-view capture is NOT guarded by rule 4. `match first(&mut bag) {
  Some(let p) => { bag.items = [P { x = 50 }]; p.x = 7; } }` compiles and prints
  `items[0].x=50`. The write went to the element the list no longer holds. Natively, the
  emitted `match first(&mut bag) { Some(p) => { bag.items = ..; p.x = 7 } }` holds a live
  `&mut` borrow of `bag` across the assignment, which rustc refuses. vilan should refuse it
  first, on both backends.

## 2. What a payload view needs

1. A **spelling** that says "write through", distinct from today's copy.
2. **Soundness**:
   - the view cannot outlive the payload (escape);
   - the payload cannot be replaced or the variant switched while the view is live (rule 4
     on the subject place and every prefix of it);
   - no other path may write the subject while the view is live (rule 4 against `&mut
     subject` passed to a call).
3. **Both emitters**: an aggregate payload is a reference to its slot; a scalar payload is a
   place pair `(enum value, slot index)`; natively, a `&mut` into the payload.

## 3. Syntax, the doors

### (A) The subject carries the mode

```vilan
match &mut held {
	Some(let p) => {
		p.x = 2;          // writes held's payload in place
		p = P { .. };     // replaces the payload: still Some
	},
	None => {},
}

if &mut presence is Presence::Online(let device) {
	device.since = now();
}

match &held { Some(let p) => total += p.x, None => {} }    // a read view: no copy
```

- **Precedent.** `for e in &mut list` puts the mode on the subject, and `e` is a writable view
  bound with no marker of its own. A match is the same act on one element.
- **Free syntax.** `match &mut place` already parses (b2, b12b), and its captures are copies
  today. Writes through them are refused, so no accepted program's meaning changes. A census
  over std, kolt and the corpus at the tag finds **zero** `match &`/`match &mut` subjects.
- **The trap closes.** A `mut` capture under a reference subject is refused: "`mut p` binds a
  copy; this match writes through `&mut held`, so bind `let p`". The steer that leads to a
  silent no-op (find 1) cannot be followed any more.
- **All or nothing per match.** Every `let` capture of the match is a view of the subject's
  mode. A copy is `*p`, spelled where it is wanted.

### (B) The binding carries the mode: `Some(&mut let p)`

This is the item's sketch. It mixes views and copies in one pattern, and it reads like the
expression `&mut x`. Against it:

- it is a parser change for a pattern form nothing else uses;
- it gives each binding two markers (`&mut` and `let`);
- for anyone arriving from Rust, `&mut p` in a PATTERN means the opposite: it dereferences a
  reference.

The mixing it buys is rare, and `*p` gives a copy under (A).

### (C) `Some(ref mut p)`

Rust's older spelling. It is a new contextual keyword for one position, foreign to vilan's
`&`/`&mut` vocabulary everywhere else. Declined.

### (D) Infer the view from a write in the arm

The match stays `match held { Some(let p) => p.x = 2 }`, and a write through `p` makes it a
view. This is invisible. A reader cannot tell a copy from an alias without reading the whole
arm, and adding a write far down an arm would change what every read above it means. Declined.

**Rec: (A).**

### 3.1 A subject that is already a view

`store.vl`'s steps match `held`, which is a `&mut` PARAMETER. Under (A) the writer spells
`match &mut held`, and it compiles today (b12b). Inside a body, a view is otherwise forwarded
bare (`wire.vl`: "the parameter already IS the view"), so re-spelling `&mut` could read as
re-taking one. The rule is the loop's: `for e in &mut list` is written even where `list` is a
view parameter. **Rec: spell it** (Q2). A bare `match held` keeps copy semantics, so the
choice stays visible at the match, and nothing that compiles today changes.

## 4. Soundness

- **Escape.** A payload view is a view binding. It joins `wrapped_view_captures` in the escape
  check, so it is not returned, stored, placed in a collection or payload, or captured by a
  closure that is stored.
- **Rule 4 on the subject.** While a capture view is live, refuse:
  - an assignment to the subject place or any prefix of it (`held = None`,
    `outer.held = ..`);
  - a `&mut` of the subject or a prefix passed anywhere (`reset(&mut held)`);
  - a method that takes the subject `&mut self`.

  Writes THROUGH the view (`p.x = ..`, `p = ..`) are the point and are allowed. A whole
  assignment `p = v` replaces the payload and keeps the variant.
- **Live range** (Q3). From the arm's start to the capture's last use, so
  `Some(let p) => { let next = f(*p); held = Some(next); }` is legal: `p` is dead at the
  assignment. A loop view is live for the whole body because it is re-bound every iteration.
  A match arm binds once, so last use is the precise and permissive answer.
- **Disjoint captures.** `V(let a, let b)` binds two views into two slots of one payload.
  They are disjoint by construction, as `for` views over distinct elements are.
- **The same guard for wrapped captures** (find 2). The capture of
  `match first(&mut bag) { Some(let p) => .. }` is a view into `bag`. Rule 4 guards `bag` for
  `p`'s live range.

## 5. The emitters

**JS.** An enum value is `[tag, payload0, payload1, ..]` (b1's emit: `[ 0, [ 1, [ "a" ] ] ]`).
For capture `i` of the matched variant:

- an aggregate payload → the reference `$a[1 + i]`, with no clone. Whole-payload assignment
  is `__replace($a[1 + i], value)`, as an aggregate view's whole write already is (b7's emit
  uses `__replace`).
- a scalar payload → the place pair `[$a, 1 + i]`, read and written through `p[0][p[1]]`, the
  existing primitive-view representation.

These are exactly the two shapes `wrapped_view_captures` already records as `(mutable,
scalar)`. `compute_wrapped_view_captures` learns a third subject kind beside "a call
returning a wrapped view" and "an inline transient": a `Reference` expression over an enum
place. The emission paths for both shapes exist.

**Native.** `match &mut <place> { V(p) => .. }`, with Rust's default binding modes giving
`p: &mut P`, and `match &mut *held` for a view subject. Scalar reads and writes go through
`*p`, which the emitter already writes for view parameters (`(*x_9427) = ((*x_9427) +
(10i32))`, `views/v8.rs`). The `.clone()` of the subject and of the write-back disappear. rustc
then enforces rule 4 a second time, as it does for every native view.

## 6. std after it

```vilan
// store.vl, `Store<Option<P>>::some()`'s write step: in place, no take, no window of `None`
|held: &mut Option<P>, f: |&mut P| void| {
	match &mut held {
		Some(let payload) => f(payload),
		None => {},
	}
}

// the derive's single-payload enum step
|held: &mut E, f: |&mut P| void| {
	match &mut held {
		E::A(let p0) => f(p0),
		_ => {},
	}
}
```

A **multi-payload** variant (`Away(str, i32)`) is projected as a tuple, `StoreSome<(str,
i32)>`, and a tuple of views cannot be formed (the escape rule: "placed in a collection"). Its
step keeps the copy until the derive projects each position as its own handle (Q6). That is
`store.md`'s `away()` handle, and it is the rare case.

Projected effect on b7's arm: the derive's write becomes the direct arm's shape, 0–1 ms against
420–470 ms. This is projected from the direct arm, which is the same emitted code. It is not
measured.

## 7. Finds (met while probing, for the integrator to file)

1. **The refusal at a write through a `match &mut place` capture steers to `mut`, which
   compiles and drops the write.** `match &mut held { Some(let p) => p.x = 2 }`: "cannot mutate
   immutable 'p'; declare it `mut` to allow mutation." With `Some(mut p)` the program compiles
   and `held` is unchanged (b2, b1 (1)). The steer should say that the capture is a copy and
   how to write the payload. Today that is `take()`/put back; after this paper it is a `let`
   capture under `&mut`. Repro: `probes/payload/b2_match_ref_mut.vl`,
   `probes/payload/b1_today.vl`.
2. **Rule 4 does not guard a wrapped-view capture.** `match first(&mut bag) { Some(let p) => {
   bag.items = [P { x = 50 }]; p.x = 7; } }` compiles on JS and loses the write
   (`items[0].x=50`). The same mutation under a `for e in &mut list` view is refused (b8). The
   emitted Rust holds a `&mut bag` borrow across the assignment, which rustc refuses (read,
   not built). Repro: `probes/payload/b9_wrapped_subject_write.vl`.
3. **The write-back of a dead `mut` capture clones it.** In the derive's enum step,
   `held = E::A(p0)` emits `__replace(held, [ 0, __clone(p0) ])` on JS and
   `E::A((p0).clone())` natively, although `p0` is dead after the statement. This is half of
   b7's 420–470 ms. It is a copy-elision miss, independent of this paper. Repro:
   `probes/payload/b7_derive_shape_cost.vl` (and `b7.rs`).

## 8. Open questions, each with a recommendation

- **Q1. The spelling.** The subject carries the mode (`match &mut place`, `&mut place is ..`),
  the binding carries it (`Some(&mut let p)`), `ref mut`, or inference from a write. **Rec:
  the subject** (§3 A).
- **Q2. A view subject spelled bare** (`match held` where `held: &mut ..`). Copy, as today, or
  implicitly a view. **Rec: copy; write `match &mut held` for views.** It keeps the choice
  visible and changes nothing that compiles.
- **Q3. The capture's live range for rule 4.** The whole arm, or to the last use. **Rec: the
  last use** (§4).
- **Q4. A `mut` capture under a reference subject.** Allow it as a copy, or refuse it. **Rec:
  refuse, with a steer to `let`.** It is the trap find 1 describes. The census finds no site.
- **Q5. The wrapped-view capture's rule-4 hole** (find 2). **Rec: close it in the same slice,
  with the same check.** It is the same view in a different subject.
- **Q6. Multi-payload variants in the Store derive.** **Rec: keep the copy for now.** Project
  each payload position as its own handle when a customer asks. A tuple of views is not
  formable.
- **Q7. `is`.** **Rec: the same rule** (`&mut held is Some(let p)`). One mechanism, two
  spellings of a match.

## 9. Slices

| Slice | Content | Size | Needs |
|---|---|---|---|
| S1 | Analysis and both emitters: a `&`/`&mut` subject binds `let` captures as views (`compute_wrapped_view_captures`' third subject kind); the escape rule over them; rule 4 on the subject for the capture's live range, for payload AND wrapped captures (find 2); `mut` under a reference subject refused (Q4); find 1's steer rewritten; pins on both backends (aggregate and scalar payloads, multi-payload disjoint captures, `is`, each refusal) | M | — |
| S2 | std: `store.vl`'s two `Option` steps and the derive's single-payload enum step write in place; the store pins byte-identical; b7's shape counted as copies in the census (zero, against two today) | S | S1 |
| — | find 3 (dead write-back clone) is a copy-census item on its own | S | — |

S1 is not breaking: every program it changes was refused before, or is a `mut` capture under a
reference subject (zero sites in the census).
