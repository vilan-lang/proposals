# Struct keys: `S.x`, typed paths into a struct

Tracker B711. Filed by kolt (2026-11-05), from its reactive-list prototype (`kolt/planning/proposal/live/`, `new_connection.md` §14). Written on vilan 0.54.0.

Related:
- `TupleKey` (`spec/types.md`, "Walking a family"), which this generalizes from tuples to structs. The spec records `keyof` as future work.
- Labelled tuples (B569).
- `std::reactive::store` (`derive(Storable)`), and the `Json` and `Wire` derives.
- The contract hash (A144).

---

## 1. Why

A value that names a FIELD, checked by the compiler, is missing. Three places spell one today, each its own way:

- **Kolt's reactive list** says which field of an item changed with a string: `slot.edit("status", ...)` emits `Edit(i, ["status"])`, and a binding listens with `slot.field("status", |t| t.status)`. A typo or a stale name compiles, and leaves a binding silently stale. This is the prototype's one open risk, and the reason for this paper.
- **`derive(Storable)`** generates one projection method per field (`user.address().city()`), so a store handle can name a field.
- **`derive(Json)`, `derive(Wire)` and `derive(PartialEq)`** generate a walk over the fields, because there's no way to write one as library code.

A typed key covers all three. A field becomes a value that can be passed, stored, compared and sent, and the compiler knows its type.

## 2. The shape

### 2.1 Typed keys: `Key<S, F>`

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
- **A key always names a real field.** No public constructor exists: `S.x` is checked when the program is built, and erased keys (§2.3) become typed only through a run-time check.
- **Paths are keys.** `Task.meta.owner` is one `Key<Task, str>` with two steps, so a key can name any field below the top level. `k.then(Meta.owner)` composes two keys.
- **Generic structs** take their arguments: `Pair<i32>.left`.

### 2.2 The inferred root: `~`

`~` stands for the expected type, wherever one is known:
- `~.x` is `S.x` when a `Key<S, _>` (or an `AnyKey<S>`) is expected;
- `~::Variant(..)` is `E::Variant(..)` when an `E` is expected.

```
slot.field(~.title)                    // Key<Task, str>
slot.edit(~.status, |s| s = "done")
events.push(~::replace(0))             // LiveResizeEvent::replace(0)
```

`~` is free: it appears nowhere in the lexical spec or the grammar. With no expected type, `~` is an error that names what it couldn't infer.

### 2.3 Erased keys: `AnyKey<S>`

A key known only at run time (from a string, the wire or a URL) can't have a static `F`. `AnyKey<S>` is the erased form:

```
let k: AnyKey<Task> = AnyKey<Task>::parse("meta.owner").unwrap();
match k.typed<str>() {                 // Option<Key<Task, str>>
	Some(let key) => print(task[key]),
	None => {},
}
for field in AnyKey<Task>::all() { print(field.name()); }   // the top-level fields
```

- `Key<S, F>` turns into `AnyKey<S>` with `.erase()`, and back with `typed<F>()`, which checks the field's type at run time.
- `AnyKey<S>` has equality and hashing, `name()` (a dotted path), `index()` (§4), `steps()`, and `starts_with(other)`. The last is what an event matches on: a write at `meta` reaches a watcher of `meta.owner`.

### 2.4 Access in place

- `s[k]` reads the field without copying `s`; only the field's value is copied when it is bound.
- `s[k] = v` writes through a `mut` place, and `&mut s[k]` is a view.
- These are the same rules as field access, because a key is a field access chosen at run time.

### 2.5 Through enums and `Option`

A step into a variant's payload can be dead at run time, so a path through one has type `Key<S, Option<P>>`. Reading it gives `None` while the variant isn't live, and a write lands only while it is, as std's `StoreSome::patch` does.

### 2.6 Steps into collections (later)

`S.tags[i]` would be a step that holds its index as a value, and a `HashMap` step its key. They're out of the first stage. A reactive list already carries positions in its own events.

## 3. Visibility

Every struct has keys. Vilan has no inaccessible items, only hidden ones, so a key is nameable exactly where its field is: `S.x` is hidden wherever `x` is, and `AnyKey<S>::all()` lists only the fields visible at the call site.

## 4. Representation and encoding

**Representation.** A key is a field index (a path is a short list of them).
- On the JS backend a struct is already an array, so `s[k]` is `s[k.index]`.
- A native backend would use an offset table.
- Neither needs a key-per-field function.

**On the wire: by index.** `S.x` is `S[index of x]`, and `AnyKey<S>::parse("x")` returns that index, so a key is sent as its index.
- The client and the server must agree on `S`'s layout anyway. std's binary codec already writes struct fields in schema order.
- **This needs the contract hash to cover struct layouts.** A144's hash appears to fill each slot with its resolved type NAME. If so, reordering or retyping a field of a struct used in a service keeps the hash the same, and index encoding (like the binary codec today) silently pairs values with the wrong fields. The hash should cover each reachable struct's fields, in order, with their types. This should be checked against the compiler before stage 2.

**Stored data: by name.** Data that outlives a build is a different contract from a connection: kolt's SQLite rows, JSON files, `localStorage` and URLs. A reordered or inserted field shifts every index after it. So `Json` and anything persisted write a key by `name()`, and read it back with `parse`. Renaming a field breaks stored names, as it breaks `Json` today.

## 5. What it replaces

- **Kolt's live lists:** `Edit` events carry `AnyKey<T>` paths instead of strings. `slot.field(~.title)` and `slot.edit(~.status, ..)` are checked, and a typo is a build error. Path matching becomes `starts_with`.
- **Store projections without a derive:** `store.at(Task.title)` can be a generic method, so `derive(Storable)` only needs to opt a type in (or nothing at all).
- **Library derives (stage 4):** with a way to walk a struct's fields at their own types (§6), `PartialEq`, `Json` and `Wire` become ordinary generic code over keys.

## 6. Stages

1. **S1:** `S.x` and paths, `Key<S, F>`, `s[k]` and `s[k] = v`, `~.x` and `~::V`. Kolt's live lists switch to it.
2. **S2:** `AnyKey<S>` with `parse`, `all`, `name`, `index`, `typed<F>` and `starts_with`, and wire encoding by index. Includes the contract-hash check of §4.
3. **S3:** steps through enum variants (§2.5).
4. **S4:** a struct's fields as a typed FAMILY, like a tuple's `keys()`: `S::fields()` maps each field to its own `Key<S, F>`, so `(k in S::fields() => ...)` is checked once per field type. With it, `PartialEq`, `Json` and `Wire` move out of the compiler.

## 7. Open questions

1. **`S.x` when `S` names both a type and a value.** Resolve by what `S` is in scope; a local value wins, and `~.x` or a type ascription covers the rest. Or refuse the ambiguity.
2. **Tuples.** Labelled tuples have `p.x` already; should `(x: f64, y: f64).x` be a key too, so `TupleKey` and `Key` meet?
3. **A field holding a closure.** It can't be compared, but its key can. Is that enough, or should keys of such fields be refused somewhere?
