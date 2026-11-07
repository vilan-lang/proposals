# Reactive lens: one reactive wrapper for any structure, with the shape passed in

Tracker A185. Proposed by the owner (2026-11-05), from kolt's reactive-list prototype (`kolt/planning/proposal/live/`, `new_connection.md` §14). Drafted on vilan 0.54.0.

**DRAFT rev 2.2 (2026-11-06), for ruling.** Q1–Q17 are open (§10). Rev 2.1 filled four of rev 2's gaps (the planned write, the truth check, owner-tied slots, the keyed side) and isolated the trait-admission find (B712); rev 2.2 adds T4's result (§21: `ListCell` on the lens inside std keeps every semantic and is slower) and the lane's library fixes.

- **Part I** is the design. Rev 2 changes law L7, adds law L8, and updates §5, §8, §9, §10 and §11 from what the lab found.
- **Part II** is the lab: a working library on std's own signals and turns, measured against std's cells and kolt's prototype, with more structures, kolt's situations, async data, a wire and nesting.

Related:
- `reactive-layers.md` (A142, ratified). §6 says "a collection *type* joins by declaring its shape; std writes this once per type." This paper reopens that sentence: once per **shape**, not once per type.
- `incremental-collections.md` (A112): `SeqOp`, `MapOp`, `DeltaLog`, the operators.
- `store.md` (A142 S7), especially §2.7 and Q11 (no `at(index)`).
- `reactive-maps-sets.md` (A138): `HashMapCell`, `HashSetCell`.
- `struct-keys.md` (B711): typed field keys, which §4.4 leans on.

---

## 0. Summary

**The problem.** Every structure that wants fine-grained reactivity needs a reactive twin. std has written four (`ListCell`, `HashMapCell`, `HashSetCell`, `KeyedCell`) plus `Store`. An app's own structure (a rope, a gap buffer, a sorted index) gets none, and its author must write one.

**The proposal.** Keep the data plain and put the reactivity in a **lens** that wraps it. The lens holds the structure, the observers, and the slots. What differs between structures is passed in as a **handler**. Every write says what it did in the same few words: insert, replace, delete, edit, move.

**What the lab shows** (Part II; vilan 0.54.0, JS backend):

- **It works as one library on std's own turns.** One lens type, two handlers, slots and parts as ordinary sources, nesting, std's `each` and `map`/`filter`/`memo` unchanged over it, tracked reads unchanged. A randomized test holds slot identity and the operators' law through 9,000 random writes.
- **It is fast.** At or ahead of `Store` on every workload but insert-at-top, where it is a few milliseconds per 200 writes behind. Level with kolt's prototype. Linear on a 32,000-row turn, where `Store` takes 5.2 s and the prototype 0.9 s. With real DOM rows it mounts in half `Store`'s time and is within 0.04 ms of a hand-written twin on every write. It holds 60% of the heap `Store` does.
- **A new structure costs its author about 20 lines** (a rope: 20 against at least 102 for a cell written std's way), and a third handler was written outside the library for a 2D grid without touching the lens.
- **It is not smaller than the four cells it would replace** (1,296 lines against 1,293). The gain is the fifth structure and what comes with every one of them, not line count.
- **The wire gets simpler downstream and no easier elsewhere.** One patch vocabulary replaces three, client slots follow server writes exactly, and a reorder is one patch. Grants, demand, reconnect and the codec, about three quarters of `rpc`, are untouched.
- **Async fits, with one exception.** Phases, latest-wins, refresh that keeps rows, and pagination are all simpler than what std or kolt has today. An optimistic delete on a positional lens does not fit as a write (§16.4).

**What it does to std, if the tests in §9 pass.** The four cells become one lens plus two handlers. `Store` becomes the lens fed by a diff. The operators in `delta.vl` stay as they are. Q11 can be reversed: a positional handle becomes sound.

**T4, done (§21).** `ListCell` re-founded on the lens inside std keeps every semantic and passes the whole suite, and is **slower**: 2× on bare writes, 3.4× heap per cell, and 13–18% more compile cost on every reactive program because the module is analyzed with std's reactive closure. Not passed as built; what it takes is listed. Until then the lens ships beside the cells, for bespoke structures and rows with slots.

**What is still open.** The slim write path and the module's analysis cost (§21.3); one inner lens per slot and part; a write of several changes; the native backend (§20).

---

## 1. The problem: one reactive twin per structure

### 1.1 The census

| Twin | Where | Lines |
|---|---|---|
| `ListCell<T>`, its recorder and the sequence traits | `std/src/reactive/delta.vl` (with the operators) | 3,770 in the file |
| `HashMapCell<K, V>` | `reactive/hash_map_cell.vl` | 717 |
| `HashSetCell<T>` | `reactive/hash_set_cell.vl` | 368 |
| `Store<T>` | `reactive/store.vl`, `store_core.vl` | 3,030 + 1,434 |
| `KeyedCell<K, T>` | `std/src/rpc.vl` | (inside rpc) |

Each one is the same three parts fused to one structure's methods. `ListCell` says so itself:

```
export struct ListCell<T> {
	items: Shared<List<T>>,          // the structure
	published: SignalCell<i32>,      // the notification
	log: DeltaLog<SeqOp<T>>,         // what each write did
}
```

Nothing in those three fields is about `List`. The `List` knowledge is in the methods: `splice`, `set_at`, `move_range`, `reconcile_to`.

### 1.2 What a rope's author can do today

- **`SignalCell<Rope>`.** Every write wakes every reader, and a read copies the rope.
- **Write a `RopeCell`.** `DeltaSource`'s own comment says an app's cell should implement it. That means a log, cursors, a notification, a recorder, and the reader that avoids the reference loop (A132). It is `ListCell` again.
- **Put it in a `Store`.** The rope is an opaque field. A write compares the whole value.

So yes: with the system as built, a `Rope` needs a `SignalRope`.

### 1.3 Why this is not intrinsic

An observer needs two things from a structure:

1. how to **read** at an address, and
2. which addresses a write **changed**.

Neither is storage. A list, a rope and a gap buffer answer both questions the same way (by position). A map and a set answer them the same way (by key). The count of reactive implementations should follow the count of ways to address, not the count of structures.

---

## 2. The model

### 2.1 Terms

- **Structure.** Plain data: `List<T>`, `HashSet<T>`, a `Rope`. It holds no reactive code.
- **Address.** How one item is named: a position, a key.
- **Change.** What one write did, by address: `Insert`, `Replace`, `Delete`. Also `Edit` (part of an item changed, §2.5) and `Reset` (anything may have changed).
- **Handler.** The logic for one kind of address. It owns the slots: which slot follows which address, and what a change does to the other addresses.
- **Lens.** The structure, a handler, a way to read at an address, and the notification. The only way to write the structure.
- **Slot.** A handle that follows one item. `get()` answers `Option<T>`.

### 2.2 The owner's sketch

```
mut base_list = ["foo", "bar", "baz"];
let list = Signal::list(base_list);
let bar = list.slot(1).value();
print(bar.get());        // Some("bar")
print(list.get()[1]);    // "bar"
list.update(|list| {
    list.insert(0, "qux");
    (void, ResizeEvent::insert(0))
});
print(bar.get());        // Some("bar")
print(list.get()[1]);    // "foo"
```

`bar.get()` is `Option<str>`: the item a slot follows can be deleted (owner, 2026-11-05).

`base_list` after the second line is a separate value. vilan's values don't alias, so a later `base_list.push(..)` does not reach the lens (checked: `base=["foo", "bar", "outside"] held=["foo", "bar"]`). No write can go around the lens, and that needs no proxy. This is the one thing MobX and Solid's store need a proxy for.

### 2.3 The same three operations; the handler is the parameter

A list and a set have the same operations: insert, replace, delete (owner, 2026-11-05). What differs is what an insert does to the **other** addresses. That is the handler's logic, and the lens takes the handler as a parameter.

| Handler | Address | An insert or delete does this to other addresses | Slot table | Cost per change |
|---|---|---|---|---|
| Positional | a position (and a count) | every later position shifts | slot id per position, in blocks of 128 | one block renumbered, plus one step per block (§13.1) |
| Keyed | a key | nothing | key → slot id | one lookup |

The probe's handler trait is three methods:

```
trait Handler<A> {
	fun follow(&mut self, at: A): i32;                    // the slot for what is at `at` now
	fun apply(&mut self, change: Change<A>): List<i32>;   // move the slots NOW; answer who wakes
	fun locate(self, slot: i32): Option<A>;               // where the slot's item is now
}
```

Other addressing rules fit the same trait without touching the lens: a sorted structure (the structure decides the position), a tree path, a grid with row and column inserts. They are not designed here.

One difference between the two handlers reaches the user (Q4). A positional slot follows an **item**: once deleted it stays `None`. A keyed slot follows a **key**: it exists before the key does and reads the key again if it returns. In the probe, a set's slot for `"urgent"` reads `Some(false)`, then `Some(true)` after the insert.

### 2.4 Granularity is asked for, never taken

The lens is not transparent and does not spread through the structure on its own.

- `list.get()` is the whole value. A reader of it wakes on every change.
- `list.slot(1).value()` is one item, with nothing finer below it.
- `list.slot(1).field(Task.title)` is one field of one item (needs B711 S1).
- `list.slot(1).list()` is a lens over a sequence inside the item. The spelling is open (Q6).

A reader pays for exactly what it asked for. The cost of this choice is that `list.get()[1]` inside a view compiles and is coarse. A lint can steer it toward `slot` (§8).

### 2.5 Nested changes

A write inside an item is `Edit(address, part)`. The part is a field key, and when that field is itself a sequence or a map, the changes inside it. A slot's field watcher wakes only when its part is named. The prototype spells the part as a string path; this paper requires a typed key (B711 S1), because a misspelt string compiles and leaves a binding silently stale.

---

## 3. The laws

These are what the pins of S1 assert. The lab's tests assert all of them on std's turns except L5, whose check is not built (Q7).

- **L1. A slot never reads another item.** A slot made at address `a` reads the item that was at `a`, wherever it is now, or `None`.
- **L2. Slots move at the write.** When `update` returns, every slot's address is current. A write through a slot later in the same turn lands on the slot's item.
- **L3. Wakes wait for the settle.** Observers run once per turn, after every write in it, in the order `reactive-turns.md` gives.
- **L4. The wake set is exact.** A slot wakes when its item is replaced, edited in a part it watches, or deleted. A change elsewhere wakes no slot. It does wake readers of the whole value, and readers of a slot's position.
- **L5. Changes are truthful.** Replaying a write's changes over the old contents gives the new contents, by length and by a read at every address. A debug build checks this (Q7).
- **L6. A deleted item's slot reads `None`** and wakes once to say so.
- **L7. `Reset` is always allowed, and lands by diff when the items have a key.** A keyed slot survives a `Reset` (keys don't move). A positional slot survives it when the items have a key to match by (`reconcile_by_key`: what both lists hold keeps its slot), and dies only when there is none. Rev 1 said every positional slot dies; the wire showed that turns every reconnect into a teardown of every row (§17.3). Q5.
- **L8. A turn's changes replay in order.** Applying a turn's changes, in the order they were made, to a copy of the structure as it stood before the turn gives the structure after it. A tap, a log and a wire all rely on this; a change is never reordered or dropped within its turn.

L2 is the law the prototype breaks. There, slot positions update when the turn settles, so `insert(0, "z"); c.set("C!")` in one turn overwrote `"b"`. The probe runs the same two writes and reads `["z", "a", "b", "C!"]`.

---

## 4. Where changes come from

This is the roughest edge. A wrong change does not crash: it points slots at the wrong items. There are three sources, and they feed the same lens.

### 4.1 The structure's shape (the default)

A structure implements one small trait for its shape. The lens then offers the shape's mutations and writes the changes itself. Nothing is annotated at any call site.

```
trait Resizable<T> {
	fun count(self): usize;
	fun item(self, at: usize): Option<T>;
	fun put(&mut self, at: usize, value: T);
	fun add(&mut self, at: usize, value: T);
	fun take(&mut self, at: usize);
}

fun insert_at<S: Resizable<T>, T>(lens: Lens<S, usize, T, Positional>, at: usize, value: T) {
	lens.update(|held| {
		held.add(at, value);
		(void, [Change::Insert(at)])
	})
}
```

In the probe the rope implements `Resizable<str>` and nothing else. `insert_at(text, 1, "new")` splits a chunk inside the rope, and the slot on line 5 follows its line.

std already has most of this for lists. `Sequence<T>` has one primitive, `splice`, and a dozen defaults over it; `Tracked<T>` is the recorder `ListCell::edit` hands a body. The real trait should be `Sequence<T>` with a read added, not the probe's five methods. One thing improves: `ListCell::edit` copies the whole list into its recorder ("the one copy a batch pays"); the lens lends the structure in place.

### 4.2 The call site (the escape hatch)

The owner's sketch: `update` takes the structure and answers the result and the changes. It is for a structure's own fast paths that no shape trait has (a rope's concat, a sort). Every call site can get it wrong, so:

- a debug build replays the changes and panics on a mismatch (L5; the prototype's `resizable_checked` is this idea);
- the convention is that a **mutator returns its change**, so the truth is written once, beside the code that makes it true:

```
impl Rope {
	fun concat(&mut self, other: Rope): Change<Span> { .. }
}
text.update(|rope| (void, [rope.concat(tail)]));
```

A sorted structure shows why the mutator must be the one to say it: the caller of `index.insert(x)` does not know where `x` landed.

### 4.3 A diff (always truthful)

`reconcile_to(new)` compares and writes the changes it finds. It costs a pass over the structure and cannot lie. This is how `Store` finds changes today, and it is the door for data that arrives whole (a server response).

### 4.4 What the compiler contributes

- **Already there:** value semantics and `&mut` (§2.2). No write escapes the lens.
- **B711 S1:** a typed `Key<S, F>` for `Edit`, replacing string paths.
- **The debug check** (L5) is library code, not compiler work.
- **Later, if wanted:** generate the lens's forwarding methods from a structure's change-returning mutators, so `text.concat(tail)` works on the lens directly. That is a derive, like `derive(Storable)`. Not proposed now.

With §4.1 as the default, the annotation burden the owner named mostly disappears without compiler work. It remains only for §4.2.

---

## 5. Changes and std's ops

std's ops carry **values**: `SeqOp::Splice(at, removed, inserted)`, `MapOp::Put(key, before, after)`. That is a requirement there. A fold's O(1) update is "add what arrived, subtract what left", and the wire translation needs the key of the element that went.

The lens's changes carry **addresses** only. A slot never needs the value: it reads the structure in place.

The two meet at a bridge. When a delta consumer attaches (`each`, `map_each`, a fold, `memo`), the lens turns each change into an op:

- arrived values are read after the write;
- departed values must be read **before** it. On the shape path (§4.1) the lens does this itself, and only while a consumer is attached. On the call-site path (§4.2) the lens cannot, so either the change carries what left or the consumer gets a `Reset` (Q2).

With the bridge the lens is a `DeltaFeed<T>` and a `RowFeed<T>`, and every operator in `delta.vl` runs over a rope unchanged. Rev 1 called this the largest unproven claim. **The lab built it** (§12), as two feeds:

- **`items()`** is the feed of values, as above. std's `map`, `filter` and `memo` follow a lens through it in the laws test, with no operator edited.
- **`rows()`** is a feed of SLOTS. `each` renders one row per slot, and the op that says a row left carries the slot, which the lens already has. Nothing is read before the write and no item is copied. This is the feed a view wants, and it sidesteps the departed-value problem entirely.

The prototype has no derived collections at all: a filtered or sorted view there re-reads the whole list.

Two details the vocabulary needs from the start, both in the lab's library:
- **Spans.** A positional `Insert` or `Delete` carries a count, so a 10,000-line paste is one change.
- **`Move`.** The item's slot goes with it and its value watchers do not wake. On the wire a drag is one patch (§17.2).

---

## 6. What happens to std

If §9 passes:

| Today | Under the lens |
|---|---|
| `SignalCell<T>` | Unchanged. A scalar has no addresses. |
| `ListCell<T>` | The lens with the positional handler over `List<T>`. Gains slots. |
| `HashMapCell`, `HashSetCell` | The lens with the keyed handler. Their per-key slots are the handler's. |
| `KeyedCell` (rpc) | The lens over its insertion-ordered map; the wire translation reads the bridge's ops. |
| `Store<T>` | The lens whose changes come from the diff (§4.3) and from handle writes, with field keys. |
| Store Q11 (no `at(index)`) | Reversible. The reason given was that "a position shifts under splices and the handle would silently change which element it names". A slot does not. |
| `delta.vl` operators | Unchanged. They are bounded on the feed, not on a cell. |
| `each` / `each_by` | `each` over a lens can key its rows by slot id. No `Keyed` impl and no key function. |
| Turns, owners, `transient` | Unchanged. |

The names can stay (`ListCell<T>` as an alias), so this need not be a breaking change for apps. That is Q1.

---

## 7. The prototype: what carries over and what changes

**Carried over.** A root over a bespoke structure through three closures (`Live::sequence`). Slots that follow items. Changes as data. Rows for std's `each`. A checked root.

**Changed.**

| In the prototype | Here |
|---|---|
| Slot positions update at the settle; a batched turn writes the wrong row | L2: slots move at the write |
| Separate `LiveList` / `LiveMap`, `LiveResizeEvent` / `KeyEvent` | One lens, the handler as a parameter (§2.3) |
| `slot.get()` documented as `Option`, the sketch showed a bare value | `Option<T>` (ruled) |
| Every `update` names its event at the call site | The shape trait is the default (§4.1); the call site is the escape hatch |
| Field paths are strings | Typed keys (B711 S1) |
| No derived collections | The bridge to `delta.vl` (§5) |
| Its own turn scheduler, with a linear dedup (32,000 rows in one turn took about 1 s) | std's turns |
| Bridges to std through a `SignalCell<i32>` | Is a `Source` and a feed directly |

Not addressed by either: a derived value that changes which roots it depends on. std's tracked reads handle this today; the lens must keep working under them.

---

## 8. What it costs

- **A new way to be wrong.** `ListCell` cannot record a false op. A call-site change can. §4 narrows this to the escape hatch and checks it in debug builds, but it does not remove it.
- **Four type parameters.** vilan has no associated types, so the probe's type is `Lens<S, A, T, H>`, and the set needed the annotation `Lens<HashSet<str>, str, bool, ByKey>`. The surface needs aliases or constructors that hide this (Q10).
- **Two ways to read.** `get()` is coarse and slots are fine. A view that indexes `get()` works and is slow. This needs a lint and a docs page.
- **The positional table.** Measured (§13.1). A flat table made insert-at-top 13 to 47 times slower than `Store`. A table in blocks of 128 positions closed the gap to within a few milliseconds per 200 writes at 32,000 rows. It is about 230 lines and the most intricate part of the library; a randomized test covers it.
- **The native backend.** The in-place read uses `Weak::get`, which the rust backend does not emit yet (F1 S1b). The probe and the prototype both stop there. `ListCell::peek` uses the same call.
- **A reopened ruling.** A142 §6 is ratified. This changes its sentence about types to one about shapes, in a direction A142's own layering allows.
- **Speed is measured in the lab, not in std.** The lens is at or ahead of `Store` and the prototype on every workload but one (§13). T4 (std's `ListCell` re-founded, on kolt's exhibit) is still the gate.
- **Handle copies.** A slot holds a copy of its lens handle, and the profile and the heap show it (§13.4, §13.5). Same family as M193 and M199.

---

## 9. Acceptance tests

All five before anything in std is re-founded (S4 on). The lens is built beside the cells until then. The last column is where the lab leaves each.

| Test | What it asks | After the lab |
|---|---|---|
| **T1. The laws** | L1–L8 pinned per handler, each proven non-vacuous by planting the bug | All but L5 asserted in the lab on std's turns, with a randomized test of the slot table and planted bugs for the table and the wire. Not yet pins in std's suite. |
| **T2. A rope with no reactive code** | A rope under the lens by one trait impl: slots, a paste as one change, rows through `each` | Done in the lab (§14). |
| **T3. The operators, unchanged** | `map`, `filter`, a fold and `memo` over a lens, std's own `delta-law` suite green, no operator edited | `map`, `filter`, `count` and `memo` follow a lens in the lab with no operator edited. `delta-law` itself has not been run over a lens. |
| **T4. `ListCell` on the lens, no slower** | kolt's perf exhibit and the perf gate's rows, judged by the seal's ceilings | **Done, and failed** (§21): semantics kept, 11,278 tests green, but 2× on bare writes, 3.4× heap per cell, ten compile-cost rows over their ceiling. |
| **T5. The batched turn** | The review's repro and its sibling, in one turn | Done (laws test; the wire and nesting tests repeat it). |

If T4 fails and cannot be fixed, the lens still ships as the answer for bespoke structures, and the cells stay. That outcome answers §1.2 without touching std's own collections.

---

## 10. Questions

Rev 2 marks what the lab settled, changed or added.

- **Q1. One core, or a second system?** Rec: **one core**. Re-found the cells on the lens and keep their names. The lab is the case for it (§13, §15); T4 is the condition.
- **Q2. Do changes carry values?** Rev 1's rec was addresses only; rev 2 wanted values on `update`'s changes. **Rev 2.1 answers it without values:** a planned write (`plan(change, write)`) names its one change BEFORE the write, so the taps read what is about to leave exactly as on the shape path. Rec: addresses only, `plan` for a structure's own fast path, `update` kept for a write that cannot say in advance (coarse but correct). What is still open is a write of several changes (§20).
- **Q3. The default source of changes.** Rec: **the shape trait** (§4.1). Built; no write in the lab's app code names a change.
- **Q4. What a keyed slot follows.** Rec: **the key**. Built so. It is what lets a rejected optimistic delete return in the same slot (§16.2).
- **Q5. Positional slots at a `Reset`.** **Changed** (L7): a `Reset` lands by diff when the items have a key, and slots die only when there is none.
- **Q6. Spellings.** The lab's are `sequence(x)`, `keyed(x)`, `.slot(a)`, `.part(name, read)`, `.slot(a).sequence(..)`. A slot IS the source of its item, so the sketch's `.value()` step is not needed. The constructor's name is the owner's call.
- **Q7. The truth check for `update`.** Rec: on in debug builds and tests. **Built in rev 2.1** (`sequence_checked`): the lengths must add up and nothing outside the window the changes name may differ. It catches a wrong position, a wrong count and an unnamed change, and it copies the structure once per checked write. Conservative inside the window.
- **Q8. The positional table.** **Answered:** blocks of 128 positions (§13.1). A flat table is 13 to 47 times too slow; a tree was not needed.
- **Q9. Fields before B711?** Rec: **no**. The lab names parts by strings as a stand-in and never ships that.
- **Q10. The four type parameters.** Quantified (§15.5): invisible inside a function, 45 to 51 characters at every boundary. Rec: wrapper types per handler (`SequenceLens<S, T>`, `KeyedLens<S, K, V>`), not aliases, and constructors that infer.
- **Q11 (new). The wire.** Rec: one patch vocabulary; frames carry versions; a `Reset` lands by key; the replica stays read-only (§17.3).
- **Q12 (new). Optimistic writes.** Rec: an overlay beside the lens, never a write to it. An optimistic edit shows through the overlay; an optimistic delete HIDES the row until the server answers (§16.4).
- **Q13 (new). Nested lenses.** Rec: one inner table per slot and part, kept with the slot, so two handles to the same inner lens are the same lens (§18).
- **Q14 (new). A list that is also looked up by id.** Rec: **an index over a sequence lens** (`index_by`, a tap), not a third handler. It is kolt's most common shape (§15.4).
- **Q16 (new). One `Splice` change, or the `Delete`+`Insert` pair?** T4 showed a consumer is owed one op for a replacing splice, and the lab now pairs them in the feed from `before`. Rec: keep the owner's three words at the surface and add `Splice(A, removed, inserted)` as the one change a sequence write records, with `Insert` and `Delete` as its two degenerate forms, so no tap has to pair anything.
- **Q17 (new). Where the module lives.** Rec: `std::reactive::lens`, imported by name, NOT re-exported from `std::reactive`, until its analysis cost is paid down; `ListCell` stays off it until the slim path exists (§21.3).
- **Q15 (new). Lifetime.** Rec: slots counted and freed at the last release, as store.md Q12 rules for store slots, and a slot or feed made inside an owner scope released with that owner. **Both built in rev 2.1** through std's `defer_to_owner`, which is a no-op outside an owner, so the same `slot()` serves a view and a plain program.

---

## 11. Slices

Rev 2 moves the lab's lessons into the order.

- **S0.** This paper and its rulings.
- **S1.** `std::reactive::lens`: the lab's library made std's, with what the lab lacks: counted slots and owner-tied taps (Q15), the truth check for `update` (Q7), values on changes (Q2), the laws and the randomized test as pins. A minimal repro of the trait-admission find (§19) comes first. Nothing existing moves.
- **S2.** The keyed side filled in: a `MapOp` bridge, length, the diff door, and the index (Q14). A real rope as the exhibit.
- **S3.** The slim write path and `settle_together` (§21.3 items 1 and 3), measured on the T4 lane's microbenchmark. Nothing existing moves.
- **S3b.** `ListCell` re-founded on the lens (T4 again), then `HashMapCell` and `HashSetCell`, only once S3 brings bare writes level and the compile-cost rows under their ceilings. **The first slice that can break anything.**
- **S4.** Fields and nested lenses, after B711 S1 (Q13).
- **S5.** The loaded collection and the optimistic overlay (§16), replacing nothing: std has neither for collections today.
- **S6.** The wire: the patch vocabulary for lens sources beside today's three, then `KeyedCell` and the mirror's landing moved onto it (§17).
- **S7.** `Store` on the lens; Q11 reopened.
- **S8.** kolt: its chat history and its board as the exhibits.

S1, S2, S3 and S5 are additive. T4 failed once (§21); if it fails again at S3b, they still ship, and the cells stay.

---

# Part II. The lab (rev 2)

Rev 1 rested on a 386-line probe. Rev 2 rests on a working library and its experiments, in `reactive-lens-lab/` (run `vilan test` there). Everything in this part was run on vilan 0.54.0, JS backend, on 2026-11-05.

## 12. What was built

`reactive-lens-lab/src/lens.vl` is the design of Part I as a library over std's own signals and turns. It imports `SignalCell`, `batch`, `DeltaLog`, `SeqOp` and the feed traits from std and changes nothing in std.

- **One lens type**, `Lens<S, A, T, H>`, with the handler as a parameter. Two handlers: `Positional` and `Keyed<K>`.
- **Changes:** `Insert(A, count)`, `Replace(A)`, `Delete(A, count)`, `Edit(A, part)`, `Move(A, A)`, `Reset`. Spans and `Move` are in from the start (§5).
- **Slots** are `Source<Option<T>>`; **parts** of a slot are `Source<Option<U>>`. Each rides one `SignalCell<i32>`, so turns, owners and `on_change` are std's.
- **Shape traits:** `Resizable<T>` (three required members) and `Lookup<K, V>`. `List<T>` and `HashMap<K, V>` implement them in the library. A sequence lens implements std's `SequenceCell<T>`, so it inherits `push`, `insert_at`, `remove_at`, `clear` and the rest.
- **Three sources of changes**, as §4: the shape path (no annotation), `update` (the call site names its changes), and `reconcile_by_key` (the diff).
- **Two bridges to std's ops** (§5): `items()` is the op feed of values, for `map`, `filter`, `count`, `memo`. `rows()` is the op feed of SLOTS, for `each`: a row is handed its item's slot and nothing is copied.
- **Taps:** a listener for the changes themselves, called before a write (while what leaves can still be read) and again for each change right after the slots moved for it. The op bridges, the index and the wire are taps. A tap is told the STAGE of each change, because a write that names several changes at once (`update`) cannot be read change by change: the structure is already final. Value feeds answer that with one `Reset`; the slot feed needs no values and stays exact.
- **Nesting** (§18) and **a wire** (§17).
- **Rev 2.1 (2026-11-06), after the ports:** a **planned write** (`plan(change, write)`) names its one change BEFORE writing, so a structure's own fast path is as exact as the shape path with no value carried (Q2 answered without values); a **truth check** (`sequence_checked`: lengths must add up, and nothing outside the window the changes name may differ) that catches a wrong position, a wrong count and an unnamed change (Q7, built); **counted slots** released with their last handle, feeds that release their tap and their slots, and both tied to the ambient owner when made inside one, so a view's row lets its slot go when the row unmounts and an explicit `release()` is only for code outside any owner (Q15); and the **keyed side**: std's `MapOp` feed (`entries()`, so `filter`, `map_values` and `memo` follow a keyed lens), a length, and `reconcile_keyed` that leaves equal values alone. `keyed_test.vl` covers them; ten test files are green.
- **Tracked reads work unchanged** (`tracked_test.vl`): a `derive(|| ..)` body that tracks two parts of one slot re-runs once for an edit of either, once for the row's deletion, and not at all for another row's edit or an insert above it.
- **An index is a tap:** `index_by(key)` keeps a map from a key of the items to their slots, so a list that is also looked up by id (§15.4) answers in one lookup; `slot.index()` is a slot's position as a source.

What the laws test asserts, on std's turns: L1, L2, L3, L4 (for slots and for parts), L6, L7, a move that keeps its slot silently, the diff door keeping slots, std's `map` and `filter` following a lens, and the keyed handler. A randomized test (`fuzz_test.vl`) runs 9,000 random inserts, deletes, bulk splices, moves and replaces against a plain model with about 400 live slots per run and checks every slot after every write; planting a bug in the slot table fails it at step 23.

## 13. Performance

### 13.1 The reactive layer alone (node, no DOM)

kolt's prototype bench, extended: 2,089 task rows, each watched by two observers (title, status). "Heavy" rows carry 300 strings each. Times are the best of five runs, in whole milliseconds (the clock's resolution).

| Workload | lens | std `Store` | kolt prototype |
|---|---|---|---|
| **2,089 light rows:** build | 14 | 13 | 14 |
| rename one row, x200 | 2 | 9 | 1 |
| insert + delete at the top, x200 | 6 | 1 | 2 |
| one turn closing every row | 7 | 27 | 11 |
| **2,089 heavy rows:** build | 23 | 29 | 29 |
| rename one row, x200 | 1 | 4 | 1 |
| insert + delete at the top, x200 | 2 | 3 | 3 |
| one turn closing every row | 3 | 49 | 8 |
| **32,000 light rows:** build | 80 | 107 | 95 |
| rename one row, x200 | 0 | 25 | 0 |
| insert + delete at the top, x200 | 10 | 7 | 11 |
| one turn closing every row | 57 | 5,225 | 890 |

Plain signals (`SignalCell<List<Task>>` with a derived value per row and column) are not in the table: one rename costs 270 ms and one insert-and-delete 526 ms at 2,089 rows.

Three things the table shows:

- **The lens is at or ahead of `Store` on every workload but insert-at-top on light rows** (6 ms against 1 ms at 2,089 rows; 10 against 7 at 32,000). `Store` tracks no positions; the lens renumbers one block of its table per insert. Against the prototype it is level, a millisecond or two either way, except on the wide turn.
- **The wide turn is linear only on the lens.** `Store` takes 5.2 s at 32,000 rows because a keyed list handle scans the list on every write (§19). The prototype takes 0.9 s because of its scheduler's linear dedup.
- **Q8 is answered by measurement.** With the prototype's flat table, insert-at-top cost 26 ms at 2,089 rows and 377 ms at 32,000. The blocked table (blocks of 128 positions) brought that to 6 ms and 10 ms. No tree was needed.

### 13.2 With real DOM rows

The same seven contenders kolt's prototype measured, plus the lens, through kolt's own harness: 2,089 heavy rows mounted, then a click per write. Script time per click in milliseconds, best of three runs, headless Chrome 151.

| | mount | rename | insert at top | delete at top |
|---|---|---|---|---|
| hand-written twin (the floor) | 62 | 0.033 | 0.081 | 0.076 |
| kolt prototype | 56 | 0.041 | 0.090 | 0.086 |
| **lens** | 67 | 0.042 | 0.108 | 0.118 |
| `each_by` over a `SignalCell` | 84 | 0.077 | 0.095 | 0.111 |
| `ListCell` + `each` | 52 | 0.104 | 0.075 | 0.057 |
| `Store` | 147 | 0.128 | 0.118 | 0.150 |
| plain signals | 51 | 16.4 | 17.5 | 17.8 |

- The lens mounts in half `Store`'s time and renames in a third of it.
- It is within 0.01 to 0.04 ms of the hand-written twin on every write.
- `ListCell` + `each` wins the two structural rows and loses the rename, because a rename there rebuilds the row (4 DOM mutations against 1).
- Layout after each click costs 0.3 to 0.7 ms for every contender. All but plain signals are already under it.
- Bundle size: lens 72 KB, prototype 68, `Store` 82, `each_by` 58, twin 44, `ListCell` 42, signals 37.

### 13.3 Derived views

Two views over the list (`map` to titles, `filter` to open tasks), each sealed with `memo`, then 200 rounds of an insert, a replace and a delete. The lens goes through its op bridge (§5); `ListCell`'s writes are its ops natively.

| Rows | | lens | `ListCell` |
|---|---|---|---|
| 2,089 | build two views | 9 | 2 |
| | 600 writes | 28 | 15 |
| 32,000 | build two views | 35 | 21 |
| | 600 writes | 231 | 234 |

The bridge costs about twice `ListCell` on a small list and nothing on a large one, where the operators themselves dominate. Each `items()` call is its own tap and its own log; sharing one per lens would close most of the small-list gap. The randomized test checks both views against a plain `map` and `filter` of the model after each of 9,000 writes.

### 13.4 Memory

Heap held by 32,000 rows with two observers each (64,000 observers), after a forced collection, less the 7 MB the list itself takes.

| | Heap held | Per observer |
|---|---|---|
| hand-written floor (a `SignalCell` per field) | 53 MB | 0.8 KB |
| kolt prototype | 106 MB | 1.7 KB |
| **lens** | 121 MB | 1.9 KB |
| `Store` | 203 MB | 3.2 KB |

std's own subscription is 0.8 KB of every row here. The lens adds about 1 KB per observer on top; the copied handles of §13.5 are the likely bulk of it, though that is not separated here. `Store` adds 2.4 KB.

### 13.5 Where the lens's own time goes

A profile of the 32,000-row build shows 14% in struct copies and 28% in the collector. A slot holds a copy of its lens handle, and a lens handle is eight fields, so every `slot()` and `part()` copies it. That is the same cost M193 and M199 describe for store handles, and the same fix applies. It is not the design's cost.

Not measured: anything on the native backend.

## 14. More structures, and kolt's situations

`structures_test.vl` and `kolt_test.vl`. Every structure below holds no reactive code: only its shape's trait impl. The ports found ten defects and surprises in the first build of the library; the correctness ones are fixed (§19) and the tests now assert the fixed behaviour.

### 14.1 Structures

| Structure | What its author wrote | What happened |
|---|---|---|
| A rope of lines in chunks, with a real bulk splice | `Resizable`, about 75 lines, nearly all the rope's own splice | Slots survive chunk splits and merges. A 5,000-line paste is ONE change. `rows()` over 20,000 lines builds in 26 ms. |
| A gap buffer | `Resizable`, about 35 lines | Passes. Moving the gap changes no item: an `update` with no changes, which is silent. |
| A sorted index (the structure decides where an insert lands) | Each mutator returns its change: 3 lines each | Passes through `update`. Two costs: the op bridge wants `Resizable`, so the index must expose a `splice` that could break its order; and `update`'s changes carry no values, so a delete reaches value consumers as a `Reset`. |
| A `HashSet` and an insertion-ordered map | `Lookup`, 12 to 15 lines | Passes. A set has to pretend its value is a `bool`. The keyed side has no op bridge, no length and no diff door. |
| A tree stored flat by node id (kolt's panel layout) | `Lookup`, about 15 lines, plus a 30-line keyed diff the test had to write | The keyed handler fits. A re-parented node's slot survives and does not wake; only the two parents hear an edit of their children. |
| A 2D grid | Either nothing, or a 150-line handler of its own | With rows of cells under the positional handler, a column insert is an edit of every row. With a **third handler written outside the library**, whose address carries the axis, a cell's slot followed a row insert, a column insert, a column delete and a row delete. The lens needed no change. |

The grid is the strongest evidence for the handler as a parameter (§2.3): a new addressing rule was added by a user of the library, not by its author.

### 14.2 kolt's situations

Each is the data shape and update pattern of a real kolt site, with asserts on which observers woke.

| Situation (kolt site) | Under the lens | What stayed awkward |
|---|---|---|
| **Rich-text rows** (`controller.vl:256-285`) | An insert above a line wakes that line's marker part and not its text part. Today `set_at` re-renders the row. | The edit arrives as kolt's own `LineEdit`, translated to changes through `update`. Several changes at once reach a value consumer as one `Reset`: every line re-measured once. |
| **Chat: live window plus paged history** (`channel.vl:1122-1345`) | One list replaces two sources and a hand-made twin of the message record. Prepending a page of 50 maps only the 50 new messages; existing rows stay silent. | Finding a message by id was a scan. `index_by` (§12) was added for this. |
| **Board with drag-reorder** (`board.vl:111-200`) | A move within a column keeps the card's row, and the column's count header sleeps through it. | A card crossing columns loses its slot: there is no move between two lenses. |
| **Filtered task table** (`task_table.vl:105-135`: a manual map plus a version counter today) | `filter`, `map` and `count` follow the lens, including a filter whose test reads a signal (a search box). | A SORTED view is not an operator. std has none, so it is a whole `derive` that re-sorts on unrelated edits. |
| **Sidebar index rebuilt whole** (`store.vl:4958-4981`) | `reconcile_by_key` is one turn; a rebuild that changed nothing wakes nobody. | The diff writes `Replace`, never `Edit`, so a rename also wakes the row's other parts. A field-level diff needs to know the fields (a derive). |
| **Select options** (`select.vl:9-33`, with a FIXME asking for granular deltas) | Passes. | A slot's position was not a source. `slot.index()` (§12) was added for this. |

### 14.3 What the ports say

The model held in every case: no scenario needed reactive code in a structure, and none needed a change to the lens type. The gaps are in what surrounds it, in this order:

1. **`update`'s changes carry no values.** Every write that names its own changes degrades to a `Reset` for value consumers (derived views, a wire). It is correct and it is coarse. **Rev 2.1:** the planned write (`plan`) names its one change first and is exact; `update` stays for a write that cannot say in advance (Q2).
2. **Nothing is released.** **Rev 2.1:** slots are counted and released with their last handle; feeds release their tap and slots. The owner tie is still by hand (§20).
3. **The keyed side is thin.** **Rev 2.1:** it has the `MapOp` feed, a length and a diff door. It still has no order.
4. **The diff door cannot emit field edits.**
5. **No move between lenses.**
6. **std has no sort operator.** Not the lens's gap, but every table in kolt meets it.


## 15. Boilerplate

Every count is non-blank, non-comment lines, by one script (`reactive-lens-lab/count_lines.py`).

### 15.1 The library

| The lens (`lens.vl`) | Lines | Public names | std's twins | Lines | Public names |
|---|---|---|---|---|---|
| changes, both handlers, the lens, slots, nesting, the truth check | 789 | | | | |
| the sequence shape: both op bridges, the index, moves, the diff door, the sequence check | 603 | | `ListCell`, its traits and recorder | 345 | 47 |
| the keyed shape: the `MapOp` feed, length, the diff door | 191 | | `HashMapCell` | 452 | 40 |
| | | | `HashSetCell` | 268 | 18 |
| | | | `KeyedCell` (rpc) | 228 | 12 |
| | | | `Store` | 3,433 | 120 |
| **Total (rev 2.2)** | **1,650** | **90** | **Total** | **4,726** | **237** |

- Without `Store`, std's four cells are 1,293 lines and 117 names against the lens's 1,650 and 90. **Line for line the lens is larger than the four cells it would replace**, and grew by 354 lines in rev 2.1 and 2.2 as the ports' and T4's gaps were filled. What it buys is that the fifth structure costs 20 lines (§15.2), and that slots, parts, nesting, the index, the truth check and the diff doors come with every one of them.
- **The sequence shape is larger than `ListCell`** (603 against 345). The keyed shape is 191 lines where `HashMapCell` and `HashSetCell` are 720.
- The comparison flatters the lens in two ways. It reuses std's `DeltaLog`, `SeqOp`, `SignalCell`, `SequenceCell` and `each`, which the twins carry or re-implement. And `Store`'s 3,433 lines include the derive, static paths and remote handling, none of which the lab attempts.
- The lab also lacks things the cells have: log trimming for its own taps, a `Signal`-style whole `set`, the batch recorder, a set shape of its own.

### 15.2 What a structure's author writes

A rope of lines in chunks, made reactive both ways. The rope itself is 56 lines either way.

| | Lines | What it gives |
|---|---|---|
| Under the lens: `impl Rope with Resizable<str>` | **20** | Slots that follow lines, parts, rows for `each`, std's operators, moves, the diff door |
| Under std today: a `RopeCell`, written the way `ListCell` is | **102** | The op feed and std's operators. No slots, no parts, no move that keeps identity. |

The `RopeCell` compiles and keeps a `.map(..).memo()` list correct. It is a floor: it leaves out the whole-value `set`, the batch recorder, `move_range`, `reconcile_to` and the constructors that `ListCell`'s own 185 lines include.

### 15.3 What an app's author writes

The same screen seven ways (2,089 task rows; rename, close, insert and delete buttons).

| Version | File | Row | The four writes | Reactive names used | What the data type must declare |
|---|---|---|---|---|---|
| **lens** | 62 | 9 | 9 | 10 | `derive(PartialEq)`. No id field. |
| kolt prototype | 71 | 9 | 19 | 14 | `derive(PartialEq)`. No id field. |
| `Store` | 74 | 8 | 16 | 12 | `derive(PartialEq, Storable)`, an id field, `impl Keyed` |
| `ListCell` + `each` | 70 | 7 | 20 | 6 | An id field. A rename replaces the whole task. |
| `each_by` | 71 | 7 | 20 | 9 | An id field |
| hand-written twin | 82 | 7 | 14 | 9 | An id field, a twin struct, a `PartialEq` impl, two converters |
| plain signals | 66 | 7 | 16 | 4 | An id field |

The lens version is the shortest, and its four writes are half the next shortest, because no write names an event or copies a task out and back. The prototype's writes are 19 lines because each names its event at the call site (§4.2).

### 15.4 Three kolt sites, before and after

| Site | Before | After | What happened |
|---|---|---|---|
| `select.vl:9-33` (has a FIXME asking for granular deltas) | 35 | 27 | The enumerate-and-copy memo goes. **But** an option's value becomes a slot id, and finding the selected option is still a scan: the lab has no reactive position and no index by value. |
| `panels.vl` lookups, `tabs.get().find(\|t\| t.id == id)` | 21 | 21 or 40 | On a sequence lens the site is the same length and only saves the list copy. On a keyed lens the call is `tabs.slot(id).get()`, but the keyed lens has no order, so the tab bar needs a second structure (40 lines). |
| `x.derive(\|l\| l.unwrap_or([])).cell()` then `each_values` | 14 | 13 | The idiom disappears. **But** kolt's handles are mirrored store handles, not lenses: each server push would have to become a `reconcile_by_key`. |

The middle row is a real gap: **a list that is also looked up by id** is kolt's most common shape (tabs, statuses, channels, authors), and neither handler alone serves it. §14 returns to it.

### 15.5 Type noise

vilan has no associated types, so a lens type is four parameters. Inference hides it inside a function: the laws test spells no lens type at all. It surfaces at every function or struct boundary:

| Spelled | Characters |
|---|---|
| `ItemSlot<List<Task>, usize, Task, Positional>` | 45 |
| `Lens<List<TabRecord>, usize, TabRecord, Positional>` | 51 |
| `Store<List<Task>>` | 17 |
| `ListCell<TabRecord>` | 19 |
| the prototype's `Slot<Task>` | 10 |

The redundancy is plain: the item type appears twice and the address type is implied by the handler. Q10 stands, and aliases alone do not remove it.


## 16. Async and transient data

`loaded.vl` (640 code lines) and two test files: one that drives "the server" by hand so every ordering is exact, and one on real tasks.

### 16.1 The design

1. **The phase sits beside the data, not around it.** A loaded collection is a lens plus a separate phase signal, in std's own `TransientState` arms. The rows stay readable in every phase but `Pending`, so a refresh or a failure never blanks them. The phase carries the token of the load whose rows are held.
2. **Latest wins by token.** A reply with a stale token is dropped. A refresh lands through `reconcile_by_key`, so rows both lists hold keep their slots.
3. **Pagination is a splice** at one end, under the same token rule, with a state per direction (idle, loading, end, failed).
4. **An optimistic write is an overlay addressed by slot.** It shows at once, remembers the confirmed value, and is confirmed or rejected by id.

### 16.2 The eight scenarios

| Scenario | Result | Under the lens |
|---|---|---|
| Page 2 arrives while a row of page 1 is edited optimistically | Passes | One splice puts the page above the row. The row's slot does not wake. Confirming a value already shown wakes only the pending flag. |
| A refresh superseded mid-flight | Passes | The token drops the late reply. An unchanged row wakes 0 times, a changed one once. |
| A refresh fails; a retry succeeds | Passes | Trivial, because the phase is beside the data. |
| An optimistic delete is rejected during a reload | Passes, **badly** | The slot died with the delete. The row is rebuilt from the saved item and its neighbours' keys, and comes back under a NEW slot: a view would rebuild that row. |
| Two edits to one row, the second confirmed first | Passes | The overlay's rule; the lens plays no part. No extra wake. |
| A load-more fails, then is retried | Passes | No duplicate rows, by a key map built per page. |
| A keyed item goes `Absent`, then `Ready`; a server value arrives during a pending edit | Passes | The keyed slot follows the key, so a rejected delete returns in the SAME slot. |
| A connection drop and resync with an edit pending | Passes | std has no "stale" arm; the test uses `Failed(error, Some(token))`. |

On real tasks: a superseded fetch is cancelled (its sleep never finishes), disposing the owner drops the reply, and the library composes with std's `.transient()` and `TaskSource`.

### 16.3 Against what exists

- **std's `Transient<List<T>>`** reads `None` during a refresh and replaces the whole list when it lands. Here the rows stay and keep their identity. std has no pagination at all; kolt hand-writes about 60 lines per paged view, with no cancellation and no stale-page guard.
- **std's `Optimistic` and `Draft`** cover one cell. Here the overlay is per row and survives out-of-order acknowledgements.
- **The prototype's `Loaded` and `Optimistic`** have no pagination and no ordering of acknowledgements.

### 16.4 What does not fit

- **An optimistic delete on a positional lens.** Deleting ends the slot (L6), so a rollback cannot give the row back its slot. The honest reading: an optimistic delete should not write the lens at all. It should hide the row in the overlay until the server confirms, which needs no new lens feature. The lab's overlay writes through and pays for it; Q12 asks for the ruling.
- **An optimistic insert** has no confirmed value behind it, and a confirm cannot swap a temporary key for the server's.
- **A stale snapshot can revert a confirmed write** once nothing is pending. The fix is a version on what the server sends, the same one the wire needs (§17.3).
- **A refresh replaces the window**, so pages loaded earlier vanish unless the server sends them again.
- **std gaps met:** `TransientState` has no `PartialEq` and no stale arm, and there is no public way to hold a cancellable task (the lab uses std's internal `detached_nursery`, as the prototype did).


## 17. The wire

`reactive-lens-lab/src/wire.vl` joins a server lens to a client lens with frames the test carries by hand, so order, lag and loss are exact. It models the part of `std::rpc` the lens would change and nothing else: no codec, no sockets, no grants.

### 17.1 What std's wire does today

From a read of `rpc.vl`, `rpc/mirror.vl` and the papers:

- There are **three downstream vocabularies**: `Update(channel, value)` for a plain source, `Patch` of `Delta` (`Reset`, `Insert`, `Update`, `Remove`) for a keyed list, and the mirror's `Patch` (`Seed`, `Set`, `Gone`, `Seq`, `Keys`) for a store.
- `KeyedCell`'s log stores every element with its key, because a wire `Remove` needs the key of what left. A reorder is a whole `Reset`: `Delta` has no move.
- The client's keyed list is one cell: any patch wakes every reader of the list. The mirrored store lands each op by copying the boundary's value, applying the op, and writing it back through the comparing write, which is fine-grained but costs the boundary per op.
- **The mirrored store's own log is already address-only**, with values read at flush. That is the lens's model.
- `ListCell` and `HashSetCell` cannot be exposed at all.

### 17.2 What the lab built

One vocabulary: a patch is a lens change plus the values the other end cannot know.

```
enum Patch<T> {
	Insert(usize, List<T>),   Replace(usize, T),   Delete(usize, usize),
	Edit(usize, str, T),      Move(usize, usize),  Reset(List<T>),
}
```

- **The server's outbox is a tap.** It records a patch as each change happens, so a value is the value at that moment and a turn's patches replay in order. An insert followed by a delete of the same row in one turn is two patches; the replica ends equal and no client row wakes.
- **The client's replica is a lens.** It applies patches through the ordinary write surface, so client slots and parts move and wake exactly as the server's do. A server edit of one field wakes one part watcher on the client.
- **Frames carry versions.** A frame that does not start where the replica is gets refused whole; the replica marks itself stale and asks again from its own version.
- **A lagging reader** (behind the bounded log) is told the whole list, and lands it with `reconcile_by_key`. Rows both lists hold keep their slots and do not wake.
- **Keyed collections are served by subscription.** A change to a key no reader asked for is recorded nowhere.
- **kolt's shape works as is:** records in a map by id, plus an order list of ids. The reader subscribes to the order whole and to records by key, on demand. A drag on the board is ONE `Move` patch, where today's wire sends the whole column.

Planting two bugs (a reset without the reconcile; no version check) fails the test at the assertion written for each.

### 17.3 What the wire forces on the design

1. **A `Reset` must land by diff when the items have a key** (changes L7). Otherwise every reconnect and every lagging log tears down every row on the client, which is worse than today.
2. **A turn's changes must replay in order** (new law L8). The lab captures values at the change. Composing a turn into one span, as the mirror does today, is an optimisation on top.
3. **Identity on the wire is a key or a server-minted slot id, never a bare position across versions.** Positions are safe downstream only because the stream is ordered and the replica is read-only.
4. **The replica stays read-only** (as mirrored-store.md Q8 and Q9 rule today). A client write travels as an `[rpc]` call; what the user sees meanwhile is an overlay (§16), not a write to the replica.

### 17.4 What the lens does not fix

About three quarters of `rpc` is untouched by any of this: grants and authorization, demand counting, dedup, reconnect and replay, the contract hash, the codec. The lens replaces the vocabularies, the keyed translation layer and the client's copy-and-diff landing. It does not make the rest easier.

Not built, and each is real work:

- **A window onto a large list** (the client holds rows 200 to 260 of 50,000). It needs server slot ids on the wire and a per-connection slot table. Today's mirror seeds lists whole, so this is new ground either way.
- **Nested patches.** A write inside a nested lens reaches the outer lens's taps as `Edit(address, part)`, and the lab's wire then sends the whole outer item.
- **Field values on the wire.** `Edit` sends the whole item until B711 gives a field an index.
- **Back-pressure.** std has none today either.

## 18. Nesting

`list.slot(1).sequence(..)` is a lens over a sequence inside the item a slot follows (`nested_test.vl`).

- The inner lens is an ordinary `Lens`, with slots, parts, rows and std's sequence surface.
- A lens's structure lives either in a cell of its own or **inside an item of another lens**; the library has one `match` for the two.
- A write through the inner lens is an `Edit` of that part on the outer item. In the test, an inner insert wakes the section's `items` watcher and nothing else: not its title, not the other section.
- When the outer list shifts, the inner lens follows its section, because it reaches it through the slot.
- One turn can span both levels.
- When the outer item is deleted, the inner lens reads empty and its slots read `None`.

Two rough edges:

- **The call site is clumsy without B711.** It passes two closures to say where the inner structure is: `doing.sequence("items", [], |s, read| read(&s.items), |s, change| change(&mut s.items))`. A typed key makes that `doing.sequence(Section.items)`.
- **One inner lens per slot and part.** Two inner lenses made over the same part do not see each other's writes, so the handle must be made once and shared. std's build has to keep the inner table with the slot. This is the main open design point in nesting (Q13).

Cost of the storage `match`: none measurable (§13 was re-run with it; the DOM numbers are unchanged).

## 19. Finds

Met while building and measuring. The first is filed; the others are for the integrator to file or fold in.

- **M200 (filed). `Store<List<T: Keyed>>::by_key` scans the list on every read and write.** A field patch costs the list's length: 25 ms for 200 renames at 32,000 rows, and 5.3 s for one turn patching every row (§13.1). kolt is not exposed, because its records live in maps by id.
- **The prototype's wide turn is quadratic** (0.9 s at 32,000 rows). Already in the review; measured again here on the same workload.
- **A type argument that appears only in a return type is not inferred from the expected type**, and the error blames a missing bound: `generic parameter 'S' is missing the bound ': Resizable<T>' required by this call`, for `fun make<S: Resizable<T>, T>(): Access<S, usize, T>` called where an `Access<S, usize, T>` is expected. The lab inlines the constructor twice instead.
- **Handle copies show in the profile** (§13.5): a struct of eight fields copied per slot. Evidence for M193 and M199 from a second direction.
- **Defects in the lab's own first build**, found by the ports of §14 and §16 and fixed before the final measurements:
  - An `update` naming several changes fed the value bridge the final structure for each of them: a derived list lost one item and doubled another. Fixed by the tap stages of §12.
  - A slot asked for past the end claimed a phantom position that later pushes moved. It now follows nothing.
  - A move woke readers of the length; an `update` with no changes woke readers of the whole value. Both now sleep.
  - A write through a dead slot did nothing, silently. `set` and `edit` now answer whether they wrote.
  - A keyed slot's `set` on an absent key reported a replace of a key that never existed. It is an insert now.
- **Found by the T4 lane in the library and fixed in rev 2.2** (§21.1): a tap captured the lens handle (a cycle under counting, 213 leaked cells); a replacing splice was two ops; a run of moves was one op each; the in-place read used `Weak::get`. **Found and not fixable in the lab:** `batch` inside an observer opens a turn instead of joining the draining one (std needs `settle_together`).
- **The rust backend drops a guard's binding:** `x.at() is Some(let at) else ret;` emits Rust whose later use of `at` is `E0425 cannot find value`. B709's family (filed for `jump break`), met here with `ret`; stamped on B709 with this repro.
- **Left as found:** the diff door moves more than it must (one item from top to bottom of five is four moves); slots and taps are not released automatically (§20).
- **A trait impl in the caller's module was not admitted to the library's generic body:** `'find' is provided by an impl in module boiler_kolt, and module lens does not admit it: a generic body resolves under the file it was DECLARED in`. **Isolated (rev 2):** it is B318's explicit export surface, not a name clash. A module that exports anything exports its impls only when they are written `export impl`, and a library's generic body reaching the impl through a bound is subject to that. Marking the impl `export impl Tabs with Lookup<..>` fixes it; a module with `export *;` (70 of kolt's 92 files) never meets it. The defect is the diagnostic, which tells the user to widen the LIBRARY's import of the caller's module, advice a library cannot follow; filed as B712. Not a design blocker, but every shape impl in a module with an explicit surface must be exported, and the docs for the shape traits must say so.
- **Integer literals are not inferred through a generic return:** `(void, [Change::Insert(1, 1)])` is read as `Change<i32>` where `Change<usize>` is expected; the lab writes `1usize`.
- **A bound must be repeated on every struct that holds a `HashMap<K, _>`**, and `TransientState` cannot be compared with `==`.

## 20. What is still unproven

In order of how much each could change the design:

1. **A slim write path, and the module's analysis cost.** T4 measured both (§21). Neither is designed yet; both are engineering, not semantics.
2. **Lifetime, the last corner.** Slots are counted, released with their last handle, and tied to the ambient owner when made inside one, as are the feeds and the index (rev 2.1; `laws_test.vl` disposes an owner and watches both go). What remains: slot ids and their cells are not reused, and a slot a feed makes from inside a tap is deliberately tied to no owner, so it lives until the feed does.
3. **`update` for a write of several changes.** A planned write of ONE change is exact and checked (rev 2.1). A write that names several (a rich-text edit with its renumbered markers) still reaches value consumers as one `Reset`, and the check for it is conservative. Composition of a change list, as the mirror does for a turn, is the missing piece (Q2).
4. **One inner lens per slot and part** (§18, Q13).
5. **A window onto a large list across the wire** (§17.4).
6. **The native backend.** The in-place read no longer uses `Weak::get` (rev 2.2), and std's `ListCell::peek` builds natively through it. The lab's own tests still do not: the next stop is B709's family, a `.. is Some(let at) else ret;` guard whose binding the emitted Rust drops.
7. **Field keys.** Parts are named by strings in the lab. Nothing is final until B711 S1 exists.


## 21. T4: std's `ListCell` re-founded on the lens

A lane did it, in a throwaway worktree (`vilan/.claude/worktrees/lens-t4`, branch `lens-t4`, off `next` @56008e46; nothing merged). The lens went into std as `std/src/reactive/lens.vl`, re-exported from `reactive.vl`, and `ListCell<T>` became `{ lens: Lens<List<T>, usize, T, Positional>, feed: LensItems<..> }` with its whole API kept and `slot(at)` added.

### 21.1 Semantics: kept

Every gate green, each exit code read directly: `cargo build`; the docs gate (no fence changed); the corpus (ONE golden moved, `list-cell.mjs`, 39.9 → 75.2 KB, because it now bundles the lens; `delta-law.vl` and `list-cell.vl` print byte-identical output; all 149 corpus programs run identically); the lab's own tests against std's copy; `cargo fmt`; **`cargo nextest run --workspace`: 11,278 passed**; clippy. Three semantics could not be kept exactly: `move_range` past the end clamps where it panicked; `edit` copies the list once instead of twice (a pin updated as an improvement); `identity()` is the notification cell's.

The port needed six changes to the library, all now folded back into the lab (rev 2.2):

1. The in-place read lends through the cell's write view narrowed to a read, not `Weak::get`, which the rust backend does not emit. `ListCell::peek` builds natively now, which it did not before.
2. **A tap captures the storage, never the lens handle.** The handle carries the tap list the tap is on; under counting that is a cycle no count collects (A132's rule). The native leak census read **213 live cells** before the fix. `rows()` and `index_by` still capture the handle in the lab.
3. **A replacing splice is ONE `SeqOp::Splice`**, not a `Delete` op and an `Insert` op. `each` matches the rows of one splice's span by key, and two ops tore down a row the second brought back. The feed pairs them from `before`. Pinned in `laws_test.vl`.
4. **A run of single moves is one `SeqOp::Move(from, count, to)`**; otherwise `move_range(0, 2, 5)` cost `each` thirty whole-list copies instead of fifteen.
5. **`landed`'s `batch` must join a draining turn.** Called from inside an observer, `batch` opened and drained a fresh turn on the spot, where `SignalCell::notify` joins the one draining, so `map_each`'s writes into its output drained once per op instead of once per turn (a pin read 2,071 renders against 2,061). std's copy gained a `settle_together` for it; the lab cannot (the draining turn is std-private), so the lab still over-notifies in that one situation.
6. A feed can be made over a caller's log, for `with_limit`.

### 21.2 Performance: not kept

Release build; best of five; two runs where they differed.

| `ListCell` alone (ms) | 0.54.0 | on the lens |
|---|---|---|
| 2,089 rows: 10,000 bare writes (push, insert, set_at, remove, pop) | 12 | **25** |
| 2,089 rows: 4,000 single-element `move_range` | 8 | **12–13** |
| 2,089 rows: 200 `edit`s | 24 | 13–14 |
| 2,089 rows: 6,000 writes under two memo views | 114 | **140** |
| 32,000 rows: 1,200 writes under two memo views | 459–466 | 439 |
| §13.3's 2,089-row derived views, 600 writes | 14 | 17–18 |
| §13.3's 32,000-row derived views, 600 writes | 228–242 | 248–251 |

| Heap | 0.54.0 | on the lens |
|---|---|---|
| 20,000 small cells | 21 MB (1.07 KB each) | **74 MB (3.7 KB each)** |
| one 200,000-row cell plus two memo views | +20.7 MB | +20.6 MB |

| Browser, script ms per click (kolt's harness) | mount | rename | insert | delete |
|---|---|---|---|---|
| `ListCell` + `each`, 0.54.0 | 61 | 0.124 | 0.083 | 0.064 |
| `ListCell` + `each`, on the lens | 57 | 0.134 | 0.089 | 0.066 |
| `each_by` over `ListCell`, 0.54.0 | 82 | 0.080 | 0.106 | 0.117 |
| `each_by` over `ListCell`, on the lens | 81 | 0.095 | 0.117 | 0.133 |

DOM mutation counts and row contents are identical. Bundles grew by 21 KB each.

**Compile cost** (`perf_gate.py measure`, instructions): the base binary reproduces every ceiling within 0.1%. With the lens in std, **ten rows are over their ceiling**: every example that imports `std::reactive` costs 13–18% more to check (`browser` ×1.184, `canvas` ×1.184, `router` ×1.181, `reactive-ui` ×1.174, `rpc` ×1.167, ..), and the kolt-shaped `genapp:46` ×1.073. A split says where it goes: with the module merely present and `ListCell` untouched, `browser` is 1,378M → 1,600M instructions; re-founding `ListCell` adds 25M more. **About 90% is the lens module being analyzed with std's reactive closure**, whether or not a program uses it.

### 21.3 The verdict on T4

**Not passed, as built.** The design holds (every semantic, every gate, one golden), but the implementation is 2× on bare writes, 3.4× in heap per cell, and 7–18% in compile cost on every reactive program. The browser rows barely move because layout dominates them, which is also why the lab's own numbers (§13) looked so good: they measured the lens where it is strong, with slots and parts, against `Store`, and not `ListCell`'s bare-write path, where the lens pays for machinery a plain cell never asks for (three notification cells, a tap list, a slot table, per-item in-place reads).

What landing it for real takes, in order:

1. **A slim write path when nothing is watched:** one notification cell until a slot or the shape is asked for; no `Shared` out-cells and no `has()` on the hot path; a handle of one field (§13.5).
2. **The module out of the default reactive closure, or cheaper to analyze.** A program that never names the lens must not pay 220M instructions for it. Either `std::reactive::lens` is imported by name (and `ListCell` then drags it in: the cost returns for every list user), or the analyzer's cost per std module falls (M194's arc).
3. **`settle_together` in std** (21.1 item 5), and the tap-capture rule applied to `rows()` and `index_by`.
4. Then T4 again.

Until then the first outcome in §9 stands: the lens ships as the answer for bespoke structures and for rows with slots, beside the cells, and `ListCell` stays as it is.

## Appendix A. The probe (0.54.0)

`proposal/reactive-lens-probe/src/probe.vl`, 386 lines, run with `vilan run` in that directory. It prints `lens probe: all passed`. Planting the prototype's wrong answer in scenario 2 makes it fail.

It defines `Change<A>`, `Handler<A>`, two handlers (`Positional`, `ByKey`), one `Lens<S, A, T, H>` and one `Slot`. Then:

1. **The sketch on a list.** A slot on `"bar"` still reads `Some("bar")` after `insert_at(list, 0, "qux")`. Position 1 is `"foo"`. The slot did not wake.
2. **The batched turn.** `insert_at(rows, 0, "z"); set(c, "C!")` with no settle between gives `["z", "a", "b", "C!"]` and one wake.
3. **A deleted item.** The slot reads `None` and wakes once.
4. **A rope.** The same lens and handler, by one `Resizable<str>` impl. A slot follows its line through a chunk split, and a write through the slot lands in the rope.
5. **A set.** The same lens with the keyed handler over a `HashSet<str>`. Only the written key's slot wakes.

What the probe does not show:
- **Notification.** Wakes are a list drained by `settle()`. There are no observers, turns or owners.
- **Spans, `Move`, `Reset`, `Edit`.** Single positions and the three basic changes only.
- **The bridge to `delta.vl`** (§5).
- **Speed.** `locate` is a linear search.
- **The native backend.** `--backend rust` refuses the in-place read (`WeakGet`, F1 S1b).
