# F99, the aliasing-views half — a model of aliasing loans for the native backend

native-49, Order 49. Base next @445c9346. This note is the brief's item 4: write the
model, build it if it is S, else file the design as the item's next step. **Conclusion:
it is not S (M, possibly L at the call seam); the design below is filed as F99's next
step, and the native refusal stays as it is.** Nothing in the tree changed for it.

## 1. The shape, and what refuses it today

```vilan
mut a: i32 = 10;
let b: &mut i32 = &mut a;   // a view binding
let c: &mut i32 = b;        // a second view of the SAME place
b = 20;                     // write through b
print(i"{a} {*b} {*c}");    // read the owner and both views: 20 20 20
add_ten(&mut a);            // a fresh loan of the owner while b and c live
add_ten(b);                 // b handed on
same(c) /= 10;              // a compound write through a `borrows` call of c
```

`vilan/test/transparent-references.vl` lines 34–47. Natively the second `let` is refused
by name in `vilan-rust` (`Emitter::declaration`, F21's refusal: "a view binding that ALIASES
another view binding … needs a model of aliasing views"). It is the one platform-free
corpus program refused for this reason (the whole-set triple's fourth refused program
besides async-await, signal-update and capture-clones).

The language PERMITS this: rule 3 makes a view an alias of a place, and rule 4 forbids
only INVALIDATING mutation under a live view (a reassignment, a resize, a variant
switch). Two writable aliases of one scalar, and a read or a fresh loan of the owner
between them, are all legal vilan. JS models every view as a `(base, key)` pair or an
object reference, so aliases are free there.

Rust's model is the opposite: at most one `&mut` to a place is usable at a time, and the
owner is frozen while it lives. `b`, `c` and `a` interleave above, so no assignment of
Rust lifetimes (NLL, two-phase borrows, reborrows) accepts the program as written.

## 2. The model: a loan GROUP per root, two lowerings

The analyzer already knows every view's ORIGIN ROOTS (`compute_view_origins`, the
fixpoint `liveness.rs` reads for §6.1's loan extension). Group the view bindings by
root: a root plus every view binding whose origin set contains it is one **loan group**.
A group is lowered one of two ways, decided per group by the emitter.

### 2.1 Disjoint use: Rust reborrows (no runtime cost)

If, walking the group's accesses in evaluation order, every access through member X
happens when no OTHER member (or the owner) is accessed until X is dead, the group is a
chain of reborrows: `let c = &mut *b;` and Rust's own borrow checker accepts it. This is
the common shape (forwarding a view, `let v = cell.slot(); v += 1;`) and costs nothing.
The question is a liveness interval test over the group's accesses: the analyzer's
last-use dataflow (S2) answers "last use of X" per binding, and the emitter checks that
the intervals are NESTED (stack discipline). transparent-references.vl's group is NOT
nested (`b`, `a`, `c`, `b`, `a`, `c` interleave), so it needs 2.2.

### 2.2 Interleaved use: the root lives in a cell, views are LENS handles

The root binding is promoted into the counted cell a captured `mut` binding already
lives in (`compute_boxed_bindings`, R3: `Shared<T>`), and each view of the group becomes
a handle — the cell plus a PATH (fields, tuple slots, settled subscripts) — copied, not
borrowed, when aliased (`let c = b;` is a handle copy). Every access is momentary:

| access | lowering |
|---|---|
| read `*b`, `a` | `cell.read_with(\|v\| path(v).clone())` (or the F49 scoped view for a `&` callee) |
| write `b = x` | `{ let x = ..; cell.update(\|v\| *path_mut(v) = x) }` — the value first |
| compound `same(c) /= 10` | settle the PLACE once (`let h = same(c);` — a handle), then read and write in two borrows: `{ let h = ..; let old = h.get(); h.set(old / 10) }` |
| `&mut a` / `b` to a `&mut` callee | `cell.with_mut(\|v\| callee(path_mut(v)))` — one `borrow_mut` for the callee's length |

The compound row is the double evaluation native-48 met (`same(c) /= 10` emitted the
place twice and took two live borrows in one statement): the fix is that a handle is a
VALUE, so the place expression runs once and the two borrows are sequential.

The last row is the one hazard. A callee holding the cell's `borrow_mut` may reach the
same root through ANOTHER handle — an argument, a closure argument, or (through a
`Shared`) a field — and the runtime would abort with `REENTRANT_READ`. That is F39's
runtime half and F102's compile-time half again: the call is refused at compile time
when another argument carries a member of the same loan group, or a closure that reaches
the root (F102's `carried_closure_touch` already finds closures that touch a binding),
and stays a runtime abort only where the compiler cannot see the reach (a handle hidden
in a value). JS answers that program; natively it is refused by name, which the
differential accepts.

A borrows CALL returning a view of a promoted root returns a handle; its signature
changes for that instance only (`fn same(x: Place<i32>) -> Place<i32>` beside the
plain `&mut i32` instance), so the call seam is per-instance, keyed like the async
adapted instances (F22).

### 2.3 What stays refused

- A group whose root is a PARAMETER received by reference (`&mut` from the caller):
  promoting it would need the caller's cooperation; the reborrow lowering (2.1) is the
  only one available, and an interleaved group over a borrowed root stays refused.
- A loan group crossing an `await` (§6.6 forbids it already).
- An aliased view into an enum PAYLOAD (payload-views.md's door A): the path through a
  variant is not a field path; refused until payload views get a lens of their own.

## 3. Why it is not S

1. The interval test (2.1) needs the group's ordered access list, which no record holds
   today: `view_origins` gives membership, liveness gives last uses, but "interleaved"
   needs first and last use per member in one order — a new walk in the emitter (or a
   new analyzer record, which is incr-49's core this wave).
2. The lens handle (2.2) is a new runtime type (`vilan_rt::Place<T>`, a cell plus a
   projection), and every view-binding read and write path of the emitter — the value
   read, the `*v` copy, write-through, compound assignment, the call seam with its
   per-instance signatures, `for e in &mut` — has to ask "is this view a handle?". The
   boxed-binding machinery (F49/F103) covers the ROOT's side; the view side is new.
3. The refusal of 2.2's last row reuses F102's closure reach, but the "another argument
   carries a member of the group" half is new.

Estimated M (the emitter seam), with the runtime type S. One corpus program flips
(transparent-references.vl); no std or kolt site writes the shape that I could find in
std (`grep` over `vilan/std` for a view binding initialized from a view binding: none).

## 4. Filed

The design above as F99's next step: `newitems49-native.json`, the item titled "native:
a model of aliasing loans …". Recommendation: build 2.1 (reborrows for a nested group)
first — it costs nothing at run time, needs only the interval test, and covers the
common forwarding shapes; then 2.2 for transparent-references.vl, with its call-seam
refusal, as its own slice.
