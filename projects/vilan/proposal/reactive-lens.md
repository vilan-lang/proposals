# Reactive lens: one reactive wrapper for any structure, with the shape passed in

Tracker A185. Proposed by the owner (2026-11-05), from kolt's reactive-list prototype (`kolt/planning/proposal/live/`, `new_connection.md` §14). Drafted on vilan 0.54.0.

**DRAFT, for ruling.** Q1–Q10 are open (§10). Nothing here is built except the probe in Appendix A.

Related:
- `reactive-layers.md` (A142, ratified). §6 says "a collection *type* joins by declaring its shape; std writes this once per type." This paper reopens that sentence: once per **shape**, not once per type.
- `incremental-collections.md` (A112): `SeqOp`, `MapOp`, `DeltaLog`, the operators.
- `store.md` (A142 S7), especially §2.7 and Q11 (no `at(index)`).
- `reactive-maps-sets.md` (A138): `HashMapCell`, `HashSetCell`.
- `struct-keys.md` (B711): typed field keys, which §4.4 leans on.

---

## 0. Summary

**The problem.** Every structure that wants fine-grained reactivity needs a reactive twin. std has written four (`ListCell`, `HashMapCell`, `HashSetCell`, `KeyedCell`) plus `Store`. An app's own structure (a rope, a gap buffer, a sorted index) gets none, and its author must write one.

**The proposal.** Keep the data plain and put the reactivity in a **lens** that wraps it. The lens holds the structure, the observers, and the slots. What differs between structures is passed in as a **handler**. Every write says what it did in the same three words: insert, replace, delete.

**What ran** (Appendix A, 0.54.0, JS backend). One `Lens` type served a list, a toy rope and a `HashSet`:
- The list and the rope share one handler. The rope's whole reactive cost is one five-method trait impl with no reactive code in it.
- The set uses a second handler under the same lens.
- A slot reads `Option<T>`, follows its item through inserts, and reads `None` after its item is deleted.
- The batched turn the prototype got wrong (insert, then write through a slot, no settle between) lands on the right item.

**What it does to std, if the tests in §9 pass.** The four cells become one lens plus two handlers. `Store` becomes the lens fed by a diff. The operators in `delta.vl` stay as they are. Q11 can be reversed: a positional handle becomes sound.

**What is not known.** Performance against `ListCell` on kolt's exhibit, and how the lens feeds std's value-carrying ops (§5). Both are gated before anything in std moves (§9, §11).

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
| Positional | a position (and a count) | every later position shifts | slot id per position | one splice of the table |
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

These are what the pins of S1 assert. The probe checks L1, L2, L4, L6 and L7 in small.

- **L1. A slot never reads another item.** A slot made at address `a` reads the item that was at `a`, wherever it is now, or `None`.
- **L2. Slots move at the write.** When `update` returns, every slot's address is current. A write through a slot later in the same turn lands on the slot's item.
- **L3. Wakes wait for the settle.** Observers run once per turn, after every write in it, in the order `reactive-turns.md` gives.
- **L4. The wake set is exact.** A slot wakes when its item is replaced, edited in a part it watches, or deleted. A change elsewhere wakes no slot. It does wake readers of the whole value, and readers of a slot's position.
- **L5. Changes are truthful.** Replaying a write's changes over the old contents gives the new contents, by length and by a read at every address. A debug build checks this (Q7).
- **L6. A deleted item's slot reads `None`** and wakes once to say so.
- **L7. `Reset` is always allowed.** A positional slot dies at a `Reset` (the structure cannot say where items went). A keyed slot survives (keys don't move). Q5.

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

With the bridge the lens is a `DeltaFeed<T>` and a `RowFeed<T>`, and every operator in `delta.vl` runs over a rope unchanged. This is the largest unproven claim in the paper, and it is S2's whole job. The prototype has no derived collections at all: a filtered or sorted view there re-reads the whole list.

Two details the vocabulary needs from the start:
- **Spans.** A positional `Insert` or `Delete` carries a count, so a 10,000-line paste is one change. The probe uses single positions.
- **`Move`.** `SeqOp` has it so a reordered row keeps its owner. The lens needs the same, or a sort is a `Reset`.

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
- **The positional table.** The prototype's table is one id per position once any slot exists, and a search to find a slot. The probe's `locate` is linear. A structure with many slots and frequent inserts near the front needs a tree (Q8). Not measured.
- **The native backend.** The in-place read uses `Weak::get`, which the rust backend does not emit yet (F1 S1b). The probe and the prototype both stop there. `ListCell::peek` uses the same call.
- **A reopened ruling.** A142 §6 is ratified. This changes its sentence about types to one about shapes, in a direction A142's own layering allows.
- **Unknown speed.** Nothing here is measured against `ListCell`. kolt's exhibit and the leaf-keystroke mandate are the gate (§9).

---

## 9. Acceptance tests

All five before anything in std is re-founded (S4 on). The lens is built beside the cells until then.

- **T1. The laws.** L1–L7 pinned per handler, each proven non-vacuous by planting the bug.
- **T2. A rope with no reactive code.** A real rope (not the toy) under the lens by one trait impl: slots, a paste as one change, rows through `each`.
- **T3. The operators, unchanged.** `map_each`, `filter`, a fold and `memo` over a lens, with `delta.vl`'s own law suite (`delta-law`) green and no operator edited.
- **T4. `ListCell` on the lens, no slower.** kolt's perf exhibit and the perf gate's rows, judged by the seal's ceilings.
- **T5. The batched turn.** The review's repro, and its sibling (edit, then insert before), in one turn.

If T4 fails and cannot be fixed, the lens still ships as the answer for bespoke structures, and the cells stay. That outcome answers §1.2 without touching std's own collections.

---

## 10. Questions

- **Q1. One core, or a second system?** Rec: **one core**. Re-found the cells on the lens and keep their names. A second system beside the first doubles what an app author must learn.
- **Q2. Do changes carry values?** Rec: **addresses only**, with the bridge of §5. A call-site `Delete` with a value consumer attached sends that consumer a `Reset` unless the change carries what left.
- **Q3. The default source of changes.** Rec: **the shape trait** (§4.1). `update` with explicit changes stays, checked in debug builds.
- **Q4. What a keyed slot follows.** Rec: **the key**. It reads `None` while the key is absent and the value when it returns. A positional slot follows the item and stays dead.
- **Q5. Positional slots at a `Reset`.** Rec: **they die**, unless `T: Keyed`, where the handler can find them again by key.
- **Q6. Spellings.** `Signal::list(..)`, `.slot(a).value()`, `.slot(a).list()`. Rec: name the nested step after its handler (`.sequence()`, `.keyed()`), since "list" also has to mean a rope. The constructor is the owner's call.
- **Q7. The truth check.** Rec: **on in debug builds and tests, off in release**, for `update` only. The shape path needs none.
- **Q8. The positional table.** Rec: **start with the prototype's flat table**, measure at T4, and move to a tree only on a measured need.
- **Q9. Fields before B711?** Rec: **no**. S1–S4 have no field edits. Fields wait for B711 S1 and never ship with string paths.
- **Q10. The four type parameters.** Rec: **aliases per handler** (`SequenceLens<S, T>`, `KeyedLens<S, K, V>`) and inference-friendly constructors. Revisit if associated types are ever ruled in.

---

## 11. Slices

- **S0.** This paper and its rulings.
- **S1.** `std::reactive::lens`: the lens, the positional handler, slots, `update`, the debug check, on std's turns. Laws pinned (T1, T5). Nothing existing moves.
- **S2.** The bridge: a lens is a `DeltaFeed` and a `RowFeed`. T3. A real rope: T2. **Stop and measure here.**
- **S3.** The keyed handler. T1 for it.
- **S4.** `ListCell` re-founded on the lens (T4), then `HashMapCell` and `HashSetCell`.
- **S5.** Fields and nested lenses (after B711 S1).
- **S6.** `Store` on the lens; Q11 reopened.
- **S7.** kolt: its message list or editor as the exhibit.

S1 and S2 are additive. The first slice that can break anything is S4.

---

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
