# Struct keys: `S.x`, typed paths into a struct

Tracker B711. Filed by kolt (2026-11-05), from its reactive-list prototype. Rev 1 was written on vilan 0.54.0.

**Rev 2 (2026-11-25, vilan 0.56.1 and `next` @30247c7e).** A second consumer arrived: the optic spike (field optics over plain state, the owner's port of his Solid lens sketch), which wrote every field as two closures and a string and listed keys as its first prerequisite. Rev 2 checks rev 1 against the compiler, adds what the optic and std's own store need, and re-cuts the stages. Probes are in `proposal/struct-keys-lab/`.

Related:
- `TupleKey` (`spec/types.md`, "Walking a family"), which this generalizes from tuples to structs. The spec records `keyof` as future work.
- `std::reactive::store` (`derive(Storable)`), whose `project(index, read, write)` and `StoreStep` are a hand-rolled key (§1).
- `std::reactive::lens` (A185), whose parts are named by strings and whose nested call site passes two closures (reactive-lens.md §18, Q9).
- Labelled tuples (B569, in the spec).
- The contract hash (A144, B525).

---

## 0. Summary

**The gap.** A value that names a FIELD, checked by the compiler, is missing. Four places spell one today, each its own way, and three of them spell it as an index or a string plus two closures (§1).

**The proposal.** `S.x` is a value of type `Key<S, F>`. A key can be passed, stored, compared, hashed and composed, and `s[k]` reaches the field in place.

**What rev 2 changes.**

| # | Change | Why |
|---|---|---|
| 1 | Identity moves into the first stage: a key has equality, a hash, a name and a prefix test from the start | Every consumer keeps a table by key: the lens's parts, the store's child slots, the optic's nodes |
| 2 | In-place access is a compiler intrinsic, with a representation chosen per backend | A closure cannot return a view (§2.3), so no library value can hold an accessor |
| 3 | Partial places get their own type, `MaybeKey<S, F>`, and collection steps move from "later" into a stage | The store already has them (`StoreSome`, `StoreStep::Key`), and the optic needs `some`, `entry` and `at` |
| 4 | Field syntax on a handle (`store.user.name`) opens to library types | It is hard-wired to std's `Store` today; the optic and the lens's slots want the same thing |
| 5 | The inferred root `~` is deferred | With (4) most of its uses go away, and `~` is already the editor's spelling for a hinted type |
| 6 | Four statements of rev 1 are corrected against the code (§9) | The contract hash already covers layouts; fields have no visibility; the derives are already std macros; a native key needs generated access |

**What is asked of the owner.** Fourteen questions, each with a recommendation (§8). The ones that shape everything else are Q1 (identity in S1), Q2 (two key types), Q3 (how a partial place is reached) and Q6 (the handle door).

---

## 1. Why

Four places name a field today:

| Who | How a field is named today | What goes wrong |
|---|---|---|
| std's lens (`slot.edit("status", ..)`, `slot.part("title", \|t\| t.title)`, `slot.sequence("items", [], lend, borrow)`) | a string, plus one or two closures | a typo compiles and leaves a binding stale; the string and the closure can disagree |
| std's store (`derive(Storable)`) | generated per field, on each of four handle types: `self.project(i, \|held, f\| f(&held.x), \|held, f\| f(&mut held.x))` | nothing goes wrong, but it is a field key written out by a macro: an index for identity and two closures for access |
| The optic spike (`user.field("name", \|u, read\| read(&u.name), \|u, change\| change(&mut u.name))`) | a string and two closures, or a derive that generates them | as the lens; and the result type is not inferred, so each binding needs an annotation |
| `derive(PartialEq)`, `Json`, `Wire`, `Hashable`, `Debug` | a generated walk over the fields | each is a macro over source text; none can be an ordinary generic function |

Three of the four hold the same three things: an identity for the field, a way to read it in place, and a way to write it in place. A typed key is those three things as one value the compiler checks.

## 2. What the consumers need, and what the language has

### 2.1 Requirements

| Need | Lens parts | Store | Optic | Derives |
|---|---|---|---|---|
| Name a field, checked at build time | yes | yes | yes | yes |
| Read the field in place (`&F`) | yes | yes | yes | yes |
| Write the field in place (`&mut F`) | yes (`edit`) | yes | yes | no |
| Equality and a hash (one table entry per key) | yes | yes | yes | no |
| A prefix test (a write at `address` reaches a watcher of `address.city`) | yes | yes (the slot tree) | yes | no |
| Composition (`a.then(b)`, paths) | yes (nested lenses) | yes | yes | no |
| An identity with the types erased (one table for every field type) | yes (`Edit(at, part)`) | yes (`StoreStep`) | yes (one node tree) | no |
| A place that may not be there (an `Option`'s payload, a variant, a list index, a map entry) | yes (a slot reads `Option<T>`) | yes (`StoreSome`, `at(key)`) | yes (`some`, `entry`, `at`) | no |
| A key from run-time data (a string, the wire) | later (the wire) | later (a mirror's slot paths) | no | `Json` by name |
| Every field of a struct, each at its own type | no | the diff | a covering write's diff | yes |

Rev 1 put identity and erasure in its second stage. The table says every reactive consumer needs them on day one, so they are in S1 here.

### 2.2 What exists

- **`TupleKey<T, U>`** names a tuple position. It is minted only by `keys()` and `entries()`, read by `get(key)`, which copies. It has no write, no in-place access, and no equality, hash, name or index a program can read. On JS it is `[at]`; natively it is `TupleKey(usize)` and a read goes through a generated per-arity match and an `Any` downcast.
- **`x[i]`** accepts a `List` or a `[T; n]` and a `usize`, and nothing else. There is no index trait. `&mut list[i]` panics out of range when the view is made, on both backends.
- **`Task.title`** parses, and fails at name resolution: "`Task` is a type, not a value". `Type.member` is never valid today, so the spelling is free.
- **A struct** is an array in field order on JS, and a named Rust struct natively. A native field cannot be reached by a run-time index without generated code.

### 2.3 Views decide the design

The memory spec's rule 3: a view may be a parameter, a short-lived local, or a return that projects a parameter (`borrows`). It may not be stored, captured, or returned any other way. Three consequences, each checked by a probe:

- **A closure cannot return a view.** The grammar gives a closure type no `borrows`, and the analyzer says "nothing sanctions a view leaving through one". `pick(&mut t).owner = "y"` over a `|&mut Task| &mut Meta` is refused as a write to a temporary (`lab/b3.vl`). So a key cannot be a library struct of accessor closures.
- **A function can** (`fun meta_of(t: &mut Task): &mut Meta borrows t`), so `s[k]` as a compiler-known place expression fits the existing rules: it is a field access whose field is chosen at run time.
- **Where a view cannot go, std passes a continuation.** The store, the lens's `Port` and the optic all use `|&S, (|&F| void)| void` and `|&mut S, (|&mut F| void)| void`. That shape works for any place, including one that may not be there.

A view of a variant's payload already exists: `match &mut place { V(let p) => .. }` binds `p` as a writable view, on both backends (`lab/c1.vl`). A payload of several fields is viewable one slot at a time; a binding of the whole sub-tuple is a copy.

---

## 3. The shape

### 3.1 Typed keys: `Key<S, F>`

`S.x`, where `S` is a struct TYPE and `x` one of its fields, is a value of type `Key<S, F>`. `F` is the field's type.

```
struct Task { title: str, status: str, meta: Meta }
struct Meta { owner: str }

let k: Key<Task, str> = Task.title;
let p: Key<Task, str> = Task.meta.owner;       // a path: two steps, one key type

fun read<F>(t: Task, k: Key<Task, F>): F { t[k] }
fun write<F>(t: &mut Task, k: Key<Task, F>, v: F) { t[k] = v; }
```

- **The field's type is in the key's type**, as `TupleKey<T, U>` carries its element type. There are no indexed-access types (`S[K]`) and no key-per-field types. A generic over keys monomorphizes per field TYPE `F`, never per key.
- **A key always names a real field.** No public constructor exists: `S.x` is checked when the program is built.
- **A key is total.** The field is always there, so `s[k]` is a place like `s.x` (§3.2). A place that may not be there is a `MaybeKey` (§3.4).
- **Paths are keys.** `Task.meta.owner` is one `Key<Task, str>` with two steps. `k.then(Meta.owner)` composes a `Key<S, Meta>` with a `Key<Meta, str>`.
- **Generic structs** infer their arguments from the expected type, as a struct literal does: `Pair.left` where a `Key<Pair<i32>, i32>` is expected. `Pair<i32>.left` does not parse today (`<` after a name is a comparison unless `::` follows), and this paper does not ask for it to (Q8).

### 3.2 Access in place

For a total key, on a struct `s: S` and `k: Key<S, F>`:

- `s[k]` is a place of type `F`. Reading it copies only the field. `s[k] = v` writes it. `&s[k]` and `&mut s[k]` are views, under the rules of `&s.x` and `&mut s.x`.
- A function may return it: `fun at<F>(s: &mut S, k: Key<S, F>): &mut F borrows s { s[k] }`.

This is `resolve_subscript` gaining one arm: a struct subject and a `Key` over that struct. It never panics, because a total key cannot miss.

### 3.3 Identity

A key is a value like any other:

- `Key<S, F>` implements `PartialEq` and `Hashable`. Two keys are equal when their paths are equal, however each was written: `Task.meta.owner == Task.meta.then(Meta.owner)`.
- `k.path(): KeyPath` is the key with its types erased: the steps and nothing else. `KeyPath` has equality, a hash, `name()` (`"meta.owner"`), `steps()`, `starts_with(other)` and `then(other)`. It cannot reach anything. It is what a table is keyed by and what an event carries: the lens's `Change::Edit(at, KeyPath)`, the optic's node table, the store's slot path.
- `k.name()` and `k.starts_with(other)` forward to the path.

The laws a consumer may rely on:

- **K1.** `s[k] = v; s[k] == v`.
- **K2.** `s[k] = s[k]` changes nothing.
- **K3.** Keys with equal paths reach the same place.
- **K4.** Keys where neither path starts with the other reach disjoint places: a write through one cannot change what the other reads.
- **K5.** `a.then(b).path() == a.path().then(b.path())`.

K4 is the wake rule of every consumer. A write at path `p` wakes a watcher at path `q` exactly when one starts with the other, and whether a watcher BELOW the write changed is a comparison of its value (the optic) or a diff (the store).

### 3.4 Places that may not be there: `MaybeKey<S, F>`

A step into an `Option`'s payload, an enum variant's payload, a list position or a map entry can miss at run time. A path with one such step is a `MaybeKey<S, F>`.

```
struct Doc { title: Option<str>, tags: List<str>, scores: HashMap<str, i32>, shape: Shape }
enum Shape { Circle(f64), Rect(f64, f64) }

Doc.title::Some           // MaybeKey<Doc, str>
Doc.shape::Rect.0         // MaybeKey<Doc, f64>: the first payload slot
Doc.tags[2]               // MaybeKey<Doc, str>: holds the index
Doc.scores["ada"]         // MaybeKey<Doc, i32>: holds the key
```

- **Why a second type and not `Key<S, Option<P>>`** (rev 1 §2.5). There is no `Option<P>` stored at a variant's payload for `&mut s[k]` to view, and a path that continues past the step (`Doc.shape::Rect.0`, or a field of a payload struct) would nest an `Option` per step. One bit in the type, "may miss", composes: total then total is total, and anything with a partial step is partial. A total key converts to a `MaybeKey` implicitly where one is expected.
- **Access is by continuation**, the form §2.3 says every consumer already uses:
  - `k.get(&s): Option<F>` copies the place out;
  - `k.view(&s, |place: &F| ..): bool` lends it, and answers whether it was there;
  - `k.change(&mut s, |place: &mut F| ..): bool` lends it for writing;
  - `k.put(&mut s, v): bool` is `change` with an assignment, std's `StoreSome::patch`.
  A `MaybeKey` has no `s[k]`. A view form (`if &mut s[k] is Some(let place) { .. }`) is possible later as sugar (Q3).
- **Steps that hold a value** (`[2]`, `["ada"]`) are built at run time from any expression: `Doc.tags[i]`. In generic code the same steps are methods on a key: `k.at(i)` where `F` is a `List<E>`, `k.entry(key)` where `F` is a `HashMap<K, V>`, `k.some()` where `F` is an `Option<T>`.
- **A value step's identity is the value's `Hash`**, as `StoreStep::Key(Hash)` already does. `Hash` is std's erased "hashable and comparable" value. It carries no type tag (`Id { n = 1 }` and `[1]` hash equal), which is sound here because one map has one key type and the step's KIND (field, variant, index, entry) is part of the step.
- **A list index is a position**, not an item. `Doc.tags[2]` names whatever sits at 2. A row that follows its item across an insert is the lens's slot, which is a different thing and stays the lens's.

### 3.5 Field syntax on a handle

A store handle already reads `app.user.name`: on `Store<T>` and `StoreSome<T>`, a member that names a field of `T` resolves to the projection method the derive generated. The rule is keyed on std's own two structs (`field_syntax_handles = ["Store", "StoreSome"]`), and each projection is generated four times (`Store`, `StoreSome`, `RemoteStore`, `RemoteStoreSome`).

With keys, the door is one attribute on one method:

```
export impl Optic<type S, type T> {
	[field_syntax]
	fun at<U>(self, key: Key<T, U>): Optic<S, U> { .. }
}

let city = user.address.city;     // user.at(User.address).at(Address.city)
```

- On a receiver whose type has a `[field_syntax]` method taking a `Key<T, _>`, a member name that is not a member of the receiver and names a field of `T` resolves to `receiver.at(T.name)`.
- The receiver's own members win, as today. A field the handle shadows (`get`) is reached with `handle.at(T.get)`; the derive's reserved-name list goes away.
- `derive(Storable)`'s projections become one generic method per handle type, and the derive is left with the diff (and with S5, with nothing).
- The lens's `slot.part(name, read)` and `slot.sequence(part, empty, lend, borrow)` become `slot.title` and `slot.items`.

This is what removes the closures and the annotation from the optic's call site, and it is why the inferred root can wait (§3.7).

### 3.6 Erased keys from run-time data: `AnyKey<S>`

Unchanged from rev 1 §2.3, and later than everything above. A key from a string, the wire or a URL has no static `F`:

```
let k: AnyKey<Task> = AnyKey<Task>::parse("meta.owner").unwrap();
match k.typed<str>() {                 // Option<Key<Task, str>>
	Some(let key) => print(task[key]),
	None => {},
}
for field in AnyKey<Task>::all() { print(field.name()); }   // the top-level fields
```

`AnyKey<S>` is a `KeyPath` that is known to be valid for `S`. `KeyPath` is the part of it the first stage needs.

### 3.7 The inferred root (`~`), deferred

Rev 1 proposed `~.x` for `S.x` and `~::Variant` for `E::Variant` where the type is expected. The integrator asked to weigh a new sigil with two meanings against inferring the root with no sigil. Three findings:

- `~` is not a token, but it is already something a user sees: the editor shows a hinted type as `: ~Pipe<..>` (E227).
- The language has no syntax today that takes a name from the expected type. Variants are `E::V` or imported.
- With §3.5, the call sites that motivated it stop needing a key expression at all: `slot.field(~.title)` is `slot.title`, and `slot.edit(~.status, ..)` is `slot.status.set(..)`.

Recommendation: no inferred root in this paper's stages. If key expressions turn out to be written often in argument position, it comes back as its own item, together with the variant half, which has nothing to do with keys (Q7).

---

## 4. Representation and encoding

**JS.** A struct is an array in field order, and a scalar view is already a `(base, key)` pair.
- A key is its steps. A total key of field steps reads `s[i0][i1]..`, and `&mut s[k]` is the pair of the parent array and the last index: the existing view shape.
- A partial step tests before it descends: a variant's tag, a list's length, a map's `has`.

**Native.** A struct is a named Rust struct: no offsets, no reflection. Two ways to reach a field by a run-time key:
- **(a) The key carries its access.** `Key<S, F>` is the path (for identity) and two projections, `for<'a> Fn(&'a S) -> &'a F` and its `&mut` twin. Views are Rust references natively, so this is exactly a view projection. A literal `Task.meta.owner` is two non-capturing functions and a static path: no allocation. `then` allocates one `Rc` per composition. A `MaybeKey`'s projections answer `Option<&F>`.
- **(b) Generated per-struct matches**, `TupleKey`'s way: field index to `&dyn Any`, then a downcast. It clones on read, cannot give `&mut`, and is slower.

Recommendation: (a) (Q11). Rev 1's "an offset table; neither backend needs a key-per-field function" does not hold natively.

**On the wire: by index.** As rev 1. Its precondition is already met: since B525 the contract hash writes every struct and enum declared outside std as its name followed by its fields in order, each with its resolved type, recursively. A reordered or retyped field changes the hash. What stays name-only is std's own types and `external` structs.

**Stored data: by name.** As rev 1. Data that outlives a build (SQLite rows, JSON files, `localStorage`, URLs) writes a key by `name()` and reads it back with `parse`.

## 5. What each consumer gets

- **The lens.** `Change::Edit(at, part: str)` carries a `KeyPath`. `slot.edit<F>(key: Key<T, F>, change: |&mut F| void)` hands the closure the FIELD, not the item, so a body cannot change a field it did not name (the integrator's note (b) on B711). `part` and the nested `sequence` take a key, or go through field syntax.
- **The store.** `project(index, read, write)` becomes `at(key)`. `StoreStep { Field(usize), Key(Hash) }` is `KeyPath`'s step. Four generated projections per field become one generic method per handle type.
- **The optic.** `field(name, lend, borrow)` becomes `at(key)`, and `user.address.city` through §3.5. The node table is keyed by `KeyPath`. `some`, `entry` and `at(i)` are `MaybeKey` steps. The spike measured what the hand-written form costs: building a handle is 140 ns at depth 1 and 600 ns at depth 6 on JS, most of it closure allocation that a key literal does not do.
- **The derives.** All six are std macros today, not compiler built-ins (rev 1 said otherwise). With S5 they become generic functions over a struct's fields. The gain is real (one walk, written once, type-checked as code and not as text) and smaller than rev 1 put it, so it is last.

## 6. Stages

| Stage | What | Who can switch |
|---|---|---|
| **S1** | `S.x` and paths; `Key<S, F>`; `s[k]`, `s[k] = v`, `&s[k]`, `&mut s[k]`; `then`; `PartialEq`, `Hashable`, `name`, `starts_with`; `KeyPath`. Both backends | The lens's parts and `Edit`. The optic's fields, written `user.at(User.name)` |
| **S2** | `[field_syntax]` on a library method (§3.5) | The optic and the lens's slots read `user.name`. The store's projections become one method |
| **S3** | `MaybeKey<S, F>`: `Option` and variant steps, list and map steps, `get`/`view`/`change`/`put` | The optic's `some`/`entry`/`at`. The store's `StoreSome` and keyed `at` |
| **S4** | `AnyKey<S>`: `parse`, `all`, `typed<F>`; a key on the wire by index | Mirrors, the lens over the wire |
| **S5** | A struct's fields as a typed family: `S::fields()` maps each field to its own `Key<S, F>` | `PartialEq`, `Json`, `Wire`, `Hashable`, `Debug` and the store's diff as generic code |

S1 is the compiler work: a new expression form, one arm in subscript resolution, and a key representation in each emitter. S2 is a generalization of an existing analyzer rule. S3 is mostly S1's machinery again with a test before each descent.

## 7. The lab

`proposal/struct-keys-lab/` holds the probes this revision rests on. All were run on 0.56.1, and `b1.vl` again on `next`.

| File | What it shows |
|---|---|
| `a.vl` | `Task.title` today: "`Task` is a type, not a value" |
| `b1.vl` | A function returning a view of a struct-typed field works. One returning a view of a SCALAR field (`&mut str borrows t`) checks clean, then fails: a `TypeError` on JS, rustc E0308 natively. A defect on both backends, filed as B753 |
| `b3.vl` | A closure cannot return a view that is written through; and a closure in a generic struct literal is typed against the unsubstituted parameter ("cannot access field 'meta' on type S", B754) |
| `c1.vl` | `match &mut` gives writable views of a variant's payload slots and an `Option`'s payload, on both backends |

A library stand-in for `Key` and `MaybeKey`, with the optic ported onto it and a key-based diff measured against the spike's copy-and-compare, is being built; its results will be added here as §7.1.

## 8. Questions

Each has a recommendation. Q1, Q2, Q3 and Q6 shape the rest.

1. **Identity in S1.** Equality, hash, `name`, `starts_with` and `KeyPath` in the first stage, not with `AnyKey`? **Rec: yes.** No reactive consumer can switch without them (§2.1).
2. **Two key types.** `Key<S, F>` for a place that is always there and `MaybeKey<S, F>` for one that may not be, in place of rev 1's `Key<S, Option<P>>`? **Rec: yes** (§3.4). The name follows std's `MaybeSignal`; `PartialKey` is the alternative.
3. **Reaching a partial place.** Continuation methods only (`get`, `view`, `change`, `put`) in S3, with a view form (`&mut s[k] is Some(let place)`) left as later sugar? **Rec: yes.** The continuation form is what the store, the lens and the optic already hold, and it needs no new view rule.
4. **Variant steps.** `Doc.title::Some`, `Doc.shape::Rect.0`: `::Variant` then a payload position, with the position optional when the payload is one slot? **Rec: yes.** A payload of several slots is reached one slot at a time, which is what views already allow.
5. **Collection steps in S3.** `Doc.tags[i]` and `Doc.scores[key]` as `MaybeKey` steps, identified by `Hash`? **Rec: yes.** Rev 1 left them for later; the store already has them and the optic needs them. A list step is a position, never an item.
6. **The handle door.** `[field_syntax]` on a method taking a `Key<T, _>` (§3.5), replacing the rule keyed on `Store` and `StoreSome`? **Rec: yes.** The alternative, a trait, needs a result type that varies with `F`, which the language cannot write.
7. **The inferred root.** Leave `~.x` and `~::Variant` out of these stages? **Rec: yes** (§3.7).
8. **Generic structs.** `Pair.left` with the arguments inferred from the expected type, and no `Pair<i32>.left`? **Rec: yes.** An ascription covers the case inference cannot.
9. **`S.x` when `S` names both a type and a value** (rev 1 Q1). **Rec: the value wins**, as it does today; no existing program changes meaning, because `Type.x` is an error today.
10. **Tuples** (rev 1 Q2). Should `TupleKey` gain what `Key` has (identity, `t[k]` in place), and should a labelled tuple's `(x: f64, y: f64).x` be a key? **Rec: give `TupleKey` identity and in-place access in S1, since it is the same machinery; leave unifying the two types open.**
11. **Native representation.** The key carries its access (§4 (a)) or generated per-struct matches (b)? **Rec: (a).**
12. **A field holding a closure** (rev 1 Q3). Its key is comparable though its value is not. **Rec: nothing to refuse.**
13. **Steps of a library's own** (a rope's line, a grid's cell) as `MaybeKey` steps built from two continuations and a `Hash`? **Rec: no.** A structure's own addressing is the lens's job, and an open step would put closures back into keys.
14. **Names.** `KeyPath` for the erased identity (Swift uses the word for the typed thing), `MaybeKey`, `[field_syntax]`. **Rec: as written; the owner's to change.**

## 9. Rev 1 against the code

| Rev 1 said | The code says |
|---|---|
| §4: the contract hash "appears to fill each slot with its resolved type NAME", so an index encoding could pair values with the wrong fields | Since B525 the hash covers each non-std struct's fields, in order, with their types, recursively. Only std's types and `external` structs are name-only |
| §3: "`S.x` is hidden wherever `x` is", and `all()` lists only the visible fields | There is no per-field visibility. The one exception is a field std labels `[internal]`, which is not a member outside std; a key to it is refused there the same way |
| §1, §6: keys let `PartialEq`, `Json` and `Wire` "move out of the compiler" | All six derives are std macros already. Keys turn generated text into generic code |
| §4: natively "an offset table"; "neither needs a key-per-field function" | A native struct is a named Rust struct. A key needs to carry its access or the compiler must generate a match per struct |
| §2.2: "`~` is free" | True of the lexer and grammar. The editor already shows `~Type` for a hinted type |
| §2.4: `&mut s[k]` follows "the same rules as field access" | True for a compiler-known place. No library value can do it: closures cannot return views |
| §2.1: `Pair<i32>.left` | `<` after a name is a comparison unless `::` follows |
| §2.5: a path through a variant is `Key<S, Option<P>>` | There is no `Option<P>` at that place to view, and a payload of several fields has no view as a whole |
