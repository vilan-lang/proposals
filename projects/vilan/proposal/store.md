# `Store` — the fine-grained version of a type, generated from its shape (A142 S7)

> Status: **RULED 2026-10-01** — Q1–Q12 as recommended (the owner, at Order 45's GO); the build is Order 45's. Drafted 2026-09-29. Tracker A142, slice S7: the paper
> `reactive-layers.md` §8 deferred ("This gets its own paper when the base has
> shipped"). Written by lane papers-44 of Order 44 against `vilan 0.41.1
> (07e8db372)`, before the train's A142 S1 lands. Nothing in the compiler or std
> changed. Every claim about today's behaviour is a probe that was run or a line
> that was read (std paths under `vilan/std/src/`, kolt paths under `kolt/src/`).
>
> Probes: `scripts/integration/sweeps/order44/papers-44/probes/store/`, re-run by
> `probes/run_all.sh`, output in `probes/run_all.out`. The two prototypes are
> `store_lens.vl` (two slot layouts and the coarse model, Appendix A) and
> `store_derive.vl` (the macro door, §3.1). Both run on the JS backend only: the
> native backend does not yet emit a field read of an unresolved subject (F1
> S1b).
>
> Related: A142 (`reactive-layers.md`, R1–R37, especially §1, §6 and §8), A138
> and I10 (`reactive-maps-sets.md`, this order's sibling paper: the Map and Set
> shapes a store's collection fields use), A112 (`incremental-collections.md`:
> `SeqOp`, `DeltaLog`, `reconcile_to`), A119 (`when_some`), B158 (specificity
> tiers), I1 (`hashable-keys.md`), B460 (a bare trait in return position).

## 0. The ask, and the answer up front

`reactive-layers.md` §1 asked whether per-struct "signal colouring" is a
principle of reactivity. It answered no. For *algebraic* data the fine-grained
version can be generated from the type's definition, because the fields and
variants are the places that can change. Its §8 sketched the generated thing:

- a cell per scalar leaf;
- a lazily allocated slot per struct field;
- for an enum, the discriminant plus the live variant's payload;
- a collection's declared shape (its §6).

Projections such as `app.channels.at(id).name` are copyable `Source`/`Signal`
handles: a root plus a static path. A whole-value write diffs and wakes only the
leaves that changed. A same-variant write patches its payload, so subscriptions
into the payload survive.

**The answer, measured on a toy root (Appendix A):**

1. **The mechanics hold.** Two independent slot layouts and a third, macro-shaped
   one wake the same slots in every scenario each of them ran (§2, Appendix A). A write
   that changes `address.zip` wakes exactly `address.zip`, `address` and the
   root. A same-variant write that changes only `since` builds nothing
   (`built+=0`) and never wakes `name`. The coarse model runs the name binding 100
   times in 100 such writes.
2. **Nothing in the base blocks a lens.** A handle over a `Shared` root, with a
   notification-only `SignalCell` per path, implements std's `Source` and `Signal`
   today. `map(..).cell()`, `effect`, `set_with` and `batch` run over it unchanged
   (`std_lens.vl`). The one constraint the base paper put on the base is met.
3. **A whole-value write is not the fast path.** It costs one comparison per
   *live* slot: the same order as the coarse model with `.distinct()` on every
   projection, and 1.2–1.7× its time in the toy. The fast path is a write through a
   handle. The path is static, so only the handle's subtree and its ancestors'
   whole-value slots are looked at: 200 writes to one key of a 1,000-key map cost
   200 comparisons, against 200,000 for the whole write and 200,000 projection
   runs for the coarse model.
4. **It is buildable without the compiler.** A `[derive(Storable)]` macro can emit
   everything per type (the macro door, §3.1): a macro sees one item at a time,
   the specificity tiers make every non-derived type a leaf, and a projection
   composes one field step onto its parent's handle. The prototype of that door
   reproduces the inline layout's wake lists and comparison counts exactly.
5. **One thing the macro door must get right is how it reads.** A handle that
   hands the *value* up through every level copies the whole root for every leaf
   read: 1,143 ms for 2,000 reads on a 1,000-key root, against 1 ms through an
   in-place lend. The in-place spelling is blocked today by two emit defects,
   found here (§8).

**Recommendation.** Build the macro door first (§10, S1–S3):

- `Store<T>` is the one handle type, root and projection alike;
- `[derive(Storable)]` is the opt-in, and it is the encapsulation boundary,
  because vilan has no private fields (§4);
- the node is a uniform tree, allocated on the first subscription below it;
- every write compares, since the store is the layer that owns equality (§2.3);
- handle writes commit along the spine.

Field syntax (`app.user.name` for `app.user().name()`) is a small later compiler
sugar (S4). The compiler-generated static layout (S5) waits for a measured need.

## 1. Ground truth

### 1.1 What a lens needs from the base, checked against std

`reactive-layers.md` §8 said: "`Signal` must allow a *lens* implementation, where
`set` on a projection writes back through the root. Nothing in §3 blocks that."

`std_lens.vl` checks this against today's traits. The lens holds three things:

- a read closure over a `Shared` root;
- a write closure that assigns in place at the path;
- a `SignalCell<i32>` that carries only the notification.

That split is `ListCell`'s discipline: the items live in a `Shared` and the
notification in a `SignalCell` (`delta.vl` `ListCell`, `publish`). The lens
implements `Source<T>` (`get`, `on_change`, `on_settle` forwarded to the
notification cell) and `Signal<T>` (`set`, `notify`). Then:

```
effect sees Oslo
effect sees Bergen
root.city=Bergen shout=Bergen!
effect sees Trondheim S
after batch: root.city=Trondheim S shout=Trondheim S! effect runs=3
```

The observations:

- A copy of the handle writes through the same root.
- `city.map(|c| c + "!").cell()` follows it.
- The trait default `set_with` works over it.
- Two writes in one `batch` are one effect run.

Under A142 S1 the same handle is a `Source`, and so a `Flow` by the blanket
(R30). It is not a pipe, because it has state to read (§8 of the base paper).

### 1.2 The estate's hand-written twins

kolt carries the heft this layer removes. It writes reactive twins by hand, and
its maps are coarse cells.

| Site | Shape today | What it costs |
|---|---|---|
| `kolt/src/account.vl:3` `Account` | four `SignalCell` fields, the whole struct inside another `SignalCell<Account>` (`account.vl:12`) | a twin type; a write to one field goes through two layers of cells |
| `kolt/src/store.vl:97` `ChannelRecord` | `name: SignalCell<str>`, `messages: SignalCell<List<u53>>`, as a VALUE in a `Map` held by a `SignalCell` | a coarse map of hand-coloured records |
| `kolt/src/store.vl:106` `GlobalStore` | `channels: SignalCell<Map<u53, ChannelRecord>>`, `messages: SignalCell<Map<u53, Message>>` | every per-key read is a projection of the whole map |
| `kolt/src/store.vl:257` `get_message` | `messages.map(\|x\| x.get(message)).cell()` | one projection per asked key, all rerun on every write to any key |
| `kolt/src/prefs.vl:11` `Prefs` | nine `StorageSignalCell` fields | a twin per preference |

The per-key row is measured in the sibling paper. 1,000 keys each observed that
way, then 1,000 single-key writes, run 1,000,000 projections in 30.5 s. The same
writes against a per-key cell run 1,000 observers in 1 ms
(`reactive-maps-sets.md` §1.3).

### 1.3 Language facts the design leans on

| Fact | Probe | Consequence |
|---|---|---|
| A field is readable from any module. `m.table.len()` on std's `Map` compiles with no diagnostic. Visibility is per item and "never blocks access" (spec `names.md` §4.8). | `field_reach.vl` | vilan has **no private fields**, so "the encapsulation boundary" (§1 of the base paper) has no language form to lean on (§4) |
| `Map` and `Set` have no `PartialEq`. `[derive(PartialEq)]` on a struct holding a `Map` is refused. | `map_eq.vl`, `set_eq.vl` | a store cannot compare a map-valued field wholesale; it diffs by key (§2.7, and the sibling paper's Q8) |
| The specificity tiers choose by bound through generic code. A concrete impl beats `impl type T: PartialEq`, which beats `impl type T`. | `derive_tiers.vl`, `leaf_tier.vl` | a derived type diffs per field. A comparable leaf compares. Anything else counts as changed on every covering write. |
| An inherent impl on one instantiation of a foreign generic type is accepted (`impl SignalCell<Address> { .. }`, `impl List<Address> { .. }`). | `extend_instantiation.vl` | the derive on `Address` can put `.city()` on `Store<Address>` without seeing `User` |
| A macro sees one item at a time (spec `macros.md` §10.2). | (spec) | the derive cannot name another type's generated node type, so the node is uniform (§3.1) |
| An inherent method beats a trait method of the same name (spec `names.md` §4.6). `i32` has an inherent `diff` (`number.vl:29`). | `store_derive.vl` (first compile) | the derive's trait method cannot be named `diff`. Generated projection names can collide the same way (§9 Q9). |
| A `&mut` lend composes through closures and writes in place at the root. | `compose_modify.vl` | a handle's write is one in-place assignment, however deep the path |

## 2. The model

### 2.1 The handle

`Store<T>` is a copyable handle: a root plus a path. `Store::new(value)` makes a
root and hands back the handle to it. Every projection is another `Store<F>`,
cut from its parent:

```vilan
let app = Store::new(App { user = alice(), channels = HashMap::new() });
let name: Store<str> = app.user().name();          // a handle, not a value
let name_now: str = name.get();                    // a read
name.set("Alice B.");                              // a write, back through the root
let ch: Store<Option<str>> = app.channels().at(id).name();
```

It implements `Source<T>` and `Signal<T>`, so under A142 S1 it is a `Flow` too,
and `name.derive(..)` starts a pipe from it. It is not a pipe: it has state, and
copying it copies a handle (R29's split). One type serves root and projection
alike, because a projection *is* a store rooted elsewhere: it reads, writes,
subscribes and projects further.

### 2.2 Slots

A **slot** is one path's subscriber list: a notification-only `SignalCell`, as in
§1.1. The base paper's "a cell per scalar leaf" becomes a slot per *watched*
path. The value itself stays in the root, in place, so a read never goes through
a cell, and a leaf nobody watches costs nothing. Slots hang off a tree of **nodes**, one node per struct or enum level that
has a live slot somewhere below it. Four rules govern them:

- **Allocated lazily.** Constructing a store allocates the root node and nothing
  else. A read allocates nothing: `new + one read` is `slots=0 nodes=0` in both
  layouts (`store_lens.vl`). A subscription allocates its slot, and the nodes on
  the way down to it.
- **Freed when unwatched.** A slot counts its subscriptions. When the last one
  releases, the slot goes, and so does a node left empty. The store's memory then
  tracks what is watched, not what is held. The toy never frees; this is S1's to
  pin.
- **Keyed children.** A map field's node has keyed children, one per asked key.
  That is `Selector`'s shape (`reactive.vl` `Selector::of`, one cell per asked
  key), and it is how `at(key)` depends on that key only (§2.7).
- **Owners are not involved.** A handle is data: it has no owner, and copying it
  allocates nothing. Only a *subscription* ties a slot to an owner, the way every
  `on_change` does.

### 2.3 The one write rule

> A write wakes exactly the live slots whose value changed.

Two cases follow:

- **A whole-value write** (`store.set(v)` at any level) compares old against
  new, but only where a slot is live. An unwatched field is never compared unless
  a whole-value slot above it needs to know whether anything changed. The
  prototype threads that as a `need` flag down the diff. With no live slots a
  whole write costs no comparisons at all (`I, 0 slots: compares=0`).
- **A write that changes nothing wakes nothing.** In `store_lens.vl`, a handle
  set to the value already held logs `woke [-]`.

This is deliberately not `SignalCell::set`, which never compares (R7). A store
cannot localize a write without comparing, and §1 of the base paper lists
equality as part of what is irreducible. The store is the layer that owns it.

A leaf with no `PartialEq` (a closure, an opaque handle) falls to the bare tier
(`leaf_tier.vl`). It reports "changed" on every write that covers it. `notify()`
on any handle wakes that slot and its ancestors without comparing, which is the
escape hatch.

### 2.4 What a whole-value write costs

The cost is one comparison per live slot, plus one equality per whole-value slot
whose children did not already report a change. Measured, 20,000 whole writes
that each change `age`, with 11 slots live (`store_lens.vl`, three runs):

| Arm | ms | comparisons | wakes |
|---|---|---|---|
| inline layout, 0 slots (the floor: the write and its copies) | 25–30 | 0 | 0 |
| inline layout, 11 slots | 36–45 | 160,000 | 40,000 |
| side-table layout, 11 slots | 52–63 | 220,000 | 40,000 |
| coarse cell, 11 projections each with `.distinct()` | 27–29 | 220,000 (plus 220,000 runs) | 40,000 |

The wakes are the same everywhere (`age` and the root). The coarse model with a
`.distinct()` on every projection is the fair comparison, and its toy cost is
just above the floor: its projections are one-line closures. A whole write in a
store is therefore the **compat path**, like `ListCell::set` and `reconcile_to`.
It is what a fetch result or a wire snapshot does at a boundary. What the store
buys over the coarse model is:

- no hand-written projection and no `.distinct()` per leaf (the heft);
- the spine commit (§2.5);
- the same-variant patch (§2.6);
- per-key collections (§2.7).

### 2.5 Handle writes: in place at the root, then the spine

`name.set(v)` does three things:

1. It assigns `v` in place at the path. A `&mut` lend composes through the path
   (`compose_modify.vl`), so the assignment is one write into the root's storage,
   not a copy per level.
2. It diffs the handle's own subtree: old value against what the path now holds.
3. If that changed, it wakes each ancestor's whole-value slot on the way up.

Siblings are never looked at, because the path is static and a write at
`address.city` cannot change `name`. The **spine commit** is what makes a handle
write cheap. Measured on a 1,000-key map field, every key observed, 200 writes
to one key:

| Arm | ms | comparisons |
|---|---|---|
| whole write (`store.set(with_score(..))`) | 94–106 | 200,000 |
| handle write, full diff from the root | 54–56 | 200,000 |
| handle write, spine commit | 0–1 | 200 |
| coarse cell, 1,000 projections each with `.distinct()` | 38–40 | 200,000 |

The diff runs against what the path holds *after* the write, not against the
argument. That matters for a write through a variant that is not live (§2.6),
which never lands. The first macro-door prototype diffed against the argument
and woke three slots for a write that did nothing. It now reads the path back
and wakes nothing.

### 2.6 Enums: the discriminant, and the payload patch

An enum's node has one slot for the **discriminant** and one child node per
variant payload. A payload's leaves read `Option`s. `presence.online().name()`
is a `Store<Option<str>>`: `None` while the variant is not live. The diff
compares the discriminant, then diffs the payload against the payload:

- **Same variant.** The payloads diff field by field, so only the changed leaf
  wakes. `Online(d1)` to `Online(d2)` with only `since` changed wakes `since`,
  `presence` and the root. It does not wake `name` or the discriminant.
- **Different variant.** Every live slot under the payload goes between `Some`
  and `None`, so all of them wake, and the discriminant slot wakes.

**Subscriptions into the payload survive** because slots hang off the type's
paths, not off the value. A consumer that should be rebuilt only when the
variant changes subscribes to the discriminant, and hands its body the payload's
handles. Measured over 100 same-variant writes (`store_lens.vl`
`scenario_payload`):

```
store:  built=1 name_wakes=0 wakes=100
coarse: runs=300 name_wakes=100
```

The coarse arm is today's `when_some`, which already keeps its row across
`Some -> Some` (A119, `browser/ui.vl` `place_when_some`). It hands the body a
`SignalCell<T>` of the whole payload, so each payload binding is a projection of
that cell, and every one of them reruns on every write. The store's version of
`when_some` hands the body a `Store<P>` instead. That is S2's UI helper.

A handle *through* a variant writes only while the variant is live. Otherwise the
write is a no-op: `handle set through a dead variant: woke [-] online=false`. A
write cannot choose which variant to become, so a through-variant handle is a
`Source<Option<P>>` with a `patch(value: P): bool`, not a `Signal` (Q6). Switching
the variant is a write to the enum's own handle.

### 2.7 Collections inside a store

A collection field takes its **declared shape** (`reactive-layers.md` §6):

- **`HashMap<K, V>`** is a keyed node. `at(key)` is a `Store<Option<V>>` whose
  slot is keyed by `key.hash()`, allocated on first subscription (§2.2). A write
  to one key wakes that key's slot only. A whole write of the map compares by key
  over the live keyed slots, then settles the map's own whole-value slot with one
  equality if nothing below reported a change. It never compares the map with
  `==`, because there is no `==` on maps (§1.3). `at(key).set(None)` removes the
  key. Its ops are the sibling paper's `MapOp`, so `app.channels()` is a map
  source that the map operators take directly.
- **`HashSet<T>`** is the same with `contains(x): Store<bool>`, and `SetOp`.
- **`List<T>`** is a sequence node. A handle write through it (`push`, `splice`)
  records a `SeqOp`, so `each_by(app.messages(), ..)` gets ops, not a diff. A
  whole write of the list field is `reconcile_to` (prefix and suffix, then one
  splice; `delta.vl` `ListCell::reconcile_to`), or the keyed reconcile when
  `T: Keyed<K>`. `at(index)` is **not** offered, because a position shifts under
  splices and the handle would silently change which element it names. A keyed
  list offers `by_key(k)` instead.

A value inside a collection is itself a store: `app.channels().at(id).name()` is
a keyed child's field. That is the summary's `app.channels.at(id).name`.

### 2.8 Wakes go through the turn

The toy wakes inline, during the diff, and that shows a real hazard. In the
variant-switch scenario the gate builds its body *while the diff is running*.
The body subscribes to the payload's slots, and the rest of the same diff then
wakes those fresh subscriptions for the write that created them (`wakes=7`
against five logged slots). In std the diff only **collects** what changed; the
turn delivers it. Each slot is a `SignalCell`, so `notify` already enqueues into
the ambient turn, and the push-pull settle keeps it free of glitches
(`reactive-turns.md`). The gate is a derivation (`as_derivation`) that seeds from
the value it reads when it runs, as every derivation does.

## 3. Two doors

### 3.1 The macro door: `[derive(Storable)]`

Everything per type can be emitted by a derive. `store_derive.vl` is what it
would emit for `User`, `Address`, `Presence` and `Device`, written by hand, over
two pieces std writes once.

**What std writes once:**

- `trait Storable { fun store_diff(self, b: Self, node: Option<Shared<Node>>, need: bool): bool; }`,
  with the two blanket leaf tiers (§2.3);
- `struct Node { me: Option<Slot>, kids: List<Option<Shared<Node>>>, keyed: Map<Hash, Shared<Node>> }`,
  the uniform tree;
- `Store<T>`, whose projection helper `project(parent, index, read, step)` builds a
  child handle from its parent and one field step;
- `impl HashMap<K, V> with Storable` (keyed by key), and the same for the other
  declared shapes.

**What the derive emits per type:**

- `impl T with Storable`: one `store_diff` line per field, in declaration order,
  each passing the field's child node and the `need` flag;
- `impl Store<T> { fun field(self): Store<F> }`: one projection per field, each a
  `project(..)` call with the field's index, a read and a `&mut` step
  `|up, f| up(|&mut t| f(&mut t.field))`;
- for an enum, the discriminant projection (`is_online()`), and per payload
  variant a through-variant projection whose step reaches only a live payload.

The derive never names another type's node type, because there is only one.
It reaches a field's type only through the `Storable` bound, so a field whose
type is not derived is a leaf, by the tiers.

**Measured.** The derived surface reproduces the inline layout exactly: the same
woken lists in all nine scenarios, and the same comparison counts (8, 8, 6, 6, 9,
9 per write; 160,000 over 20,000 whole writes). Its handle writes commit along
the spine: 1 comparison for `address.city`, against 8 for a full diff.

**The read must be a lend, not a value.** A projection built as
`read = || parent.read().field` hands the *whole parent value* up through every
level, so every leaf read copies the root:

| Read | ms for 2,000 leaf reads on a 1,000-key root |
|---|---|
| inline layout (`self.value.read().address.city`, direct) | 1 |
| macro door, composed value read | 1,124–1,491 |
| macro door, composed in-place lend | 1 |

The lend is `modify`'s shape, `|(|&T| void)| void`, with only the leaf copied at
the end. Its honest spelling is a *shared* view. On 0.41.1 that miscompiles on
both backends (§8, find 2), so the prototype borrows `modify`'s `&mut` lend
instead. Taking a snapshot out of the lend (`Some(*v)`) meets a second defect:
`*v` on an aggregate does not copy on the JS emit, so the "old" value aliases the
storage and follows the write (§8, find 3). The prototype routes the copy
through a list. With both fixed, the macro door's reads cost what the inline
layout's do.

### 3.2 The compiler door

The compiler can generate what the macro cannot:

- a node *type* per user type, with inline `Option` fields (`store_lens.vl`
  layout I);
- static paths, so a handle is a root pointer plus a path the compiler knows,
  and no closures;
- field syntax on handles.

It costs a new member-resolution tier and codegen for both backends. On the
evidence, its only win over a fixed macro door is constant factors. The macro
door's comparison counts already equal layout I's, and the lend reads match its
read time.

**Field syntax needs neither door.** Once the derive has put `name()` on
`Store<User>`, a single member-resolution rule gives `app.user.name`: "on a
`Store<T>` value, a member that names a field of `T` resolves to the projection
method of that name". It sits after fields and methods (spec `names.md` §4.6),
so it can shadow nothing. That rule is S4, and it is small.

### 3.3 The slot layout (inline pointers against a side table)

The brief asked which layout. Both were built (`store_lens.vl`):

| | Inline (layout I) | Side table (layout T) |
|---|---|---|
| Shape | a node per struct level; an `Option` per field | one `Map<path, (slot, comparator)>` per root |
| Whole-write comparisons, 11 live slots | 8 per `zip` write; 160,000 per 20,000 writes | 11 per write; 220,000 per 20,000 writes |
| Why | prunes by path; a parent's change is its children's | every live entry runs its comparator from the root, and an ancestor's comparator repeats its descendants' |
| Spine commit | natural (walk up the nodes) | needs a prefix index over the paths |
| Generated code | a node type per user type (compiler door) or one uniform node (macro door) | one closure per path |
| Wake order | leaves, then ancestors | the table's insertion order (`user presence online.since`) |

Wake order is not a contract: the turn orders delivery (§2.8).

**Rec: the tree.** It prunes, it commits along the spine, and it has the macro
door's uniform form. The side table's one advantage, less generated code, does
not survive the comparison count.

## 4. Encapsulation and granularity

**Vilan has no private fields** (§1.3), so "a type's private fields are opaque
unless its author opts in" (§1 of the base paper) needs a boundary the language
does not draw. There are three candidates:

- **(a) Structural everywhere.** Every struct projects its fields. Then std's
  `HashMap` would project its `table: NativeMap`, and an app's `Money` its raw
  cents. That breaks every abstraction whose representation is not its meaning.
- **(b) Opt-in per type, by derive.** A type projects its fields only if its
  author wrote `[derive(Storable)]`. Every other type is a **leaf**: one slot
  holding the whole value, compared by `PartialEq` when it has one, and changed on
  every covering write when it has not. This is how `Hashable`, `PartialEq`,
  `Wire` and `Debug` already work.
- **(c) Structural within the package, opt-in across it.** This needs the
  compiler door, because a macro cannot tell which package declared a field's
  type.

**What an encapsulated type exposes**, under (b):

- the whole value as a leaf `Store<T>`: read, write, subscribe;
- its **declared shape**, if its author declared one. std's collections are the
  case (§2.7): a `HashMap` is not projected field by field, it is a keyed node
  with the Map shape's vocabulary. An author who writes a collection-like type
  wraps a std one and inherits its shape (§6 of the base paper).

Algebraic std types are structural built-ins, with no derive to write: `Option`
(through-`Option` projections, as in §2.6), `Result` (`ok()`/`err()` like two
variants) and tuples (`.0`, `.1`).

**The granularity knob.** With (b), a type that is not derived is already
coarse. What remains is the per-*field* override, for a derived type used where
one slot is wanted (an `Address` that is always edited as a whole):

```vilan
[derive(Storable)]
struct User {
	name: str,
	[reactive(coarse)]
	address: Address,     // one slot, compared with ==, even though Address derives Storable
}
```

Field attributes already exist (`[expose]`, `[expose(keyed)]`, read by the
`service` macro through `macro_std::meta::Field`). `[reactive(coarse)]` is the
spelling the brief used; the derive reads it the same way.

**Rec: (b)** with the field knob. It is the only boundary the language can
support, it matches every other derive, and it is what the macro door needs.
The cost is one attribute line per type, against a hand-written twin type today.

## 5. `Store::new` against `reactive let`

A binding form would read `reactive let app = App { .. };`, after which
`app.user.name` is a handle. `lazy let` is the precedent (A100): a binding
modifier that changes how reads behave. But `lazy let x` still reads as the
declared type, and forcing is invisible. A reactive binding changes the type of
every member read: `app.user.name` is a `Store<str>`, not a `str`. The type
change is what a reader must see, and `Store::new(..)` puts it in the one place
a reader looks. The binding form also has no spelling for a store built inside
an expression or returned from a function.

**Rec: `Store::new` only.** Revisit `reactive let` if kolt's migration (S6)
shows the call to be noise. The field-syntax rule (S4) removes most of that
noise anyway.

## 6. kolt, rewritten (the exhibits S6 would land)

`Account` (`kolt/src/account.vl`) drops its twin type:

```vilan
[derive(Storable)]
struct Account {
	fullname: str,
	username: str,
	nickname: str,
	channels: List<u53>,
}

fun stub(): Store<Account> {
	Store::new(Account { fullname = "Reed Syllas", username = "reedsyllas", nickname = "Reed", channels = [] })
}

fun join_channel(account: Store<Account>, channel_id: u53) {
	account.channels().push(channel_id);      // a SeqOp; one slot wakes
}
```

`GlobalStore`'s two maps become one keyed store, and `get_message`
(`store.vl:257`) becomes a keyed handle:

```vilan
[derive(Storable)]
struct ChannelRecord {
	id: u53,
	name: str,
	messages: List<u53>,
}

[derive(Storable)]
struct Global {
	channels: HashMap<u53, ChannelRecord>,
	messages: HashMap<u53, Message>,
}

// was: self.global_store.messages.map(|x| x.get(message)).cell()
fun get_message(self, message: u53): Store<Option<Message>> {
	self.global.messages().at(message)
}
```

`Message` is not derived, so it is a leaf: `at(id)` wakes when that message is
replaced, and never when another one is. Whether a `Store` crosses the wire as
an `[rpc]` return (today a `SignalCell` does, A79) is a transport question this
paper leaves to the transient slice. A store handle is a `Source`, so the
generic `Source` exposure applies unchanged.

## 7. What it costs, stated plainly

1. **A derive line per type**, and a knob per coarse field.
2. **Every write compares.** A whole write costs one comparison per live slot. It
   is the compat path; the handle write is the fast one.
3. **A handle is six closures and a name** in the macro door. It is copyable,
   and it allocates nothing until something subscribes.
4. **Projections are methods until S4**: `app.user().name()`.
5. **A handle through a variant or an `Option` is read-plus-patch**, not a
   `Signal` (Q6).
6. **Two emit defects block the cheap read** (§8, finds 2 and 3). The macro door
   cannot ship its read path until they are fixed.

Against those costs:

- the twin types go;
- per-key collections cost O(1) per write instead of O(keys);
- same-variant writes rebuild nothing;
- `when_some`'s payload bindings stop rerunning on every write.

## 8. Finds (bugs met while probing, for the integrator to file)

1. **A closure-typed `&mut` parameter accepts a bare place, and the JS emit
   crashes.** `fun apply(f: |&mut str| void)` whose body calls `f(a.s)` is
   accepted. A `fun` with a `&mut` parameter refuses the same call ("pass
   `&mut <place>`"). The JS emit then passes the value while the closure assigns
   through a place pair: `TypeError: Cannot create property 'l' on string 'o'`.
   `--backend rust` prints the expected `sync local list`. Repro:
   `probes/store/find_bare_place_call.vl`.
2. **A shared view handed to a closure's `&T` parameter arrives as the emitter's
   place pair.** `f(&a.city)` into `|c| { out = *c; }` stores
   `[ [ 'Oslo', '1' ], 0 ]` instead of `Oslo`. `out = c`, without the `*`, is
   also accepted, where the `&mut` twin refuses and asks for `*`. Annotating
   the parameter changes nothing. `--backend rust` refuses the emitted Rust
   (`expected Rc<dyn Fn(&Rc<str>)>, found Rc<dyn Fn(Rc<str>) -> _>`). This blocks
   the macro door's read path (§3.1). Repro:
   `probes/store/find_view_closure_read.vl`.
3. **`*view` on an aggregate does not copy on the JS emit (value semantics).**
   `mut c: P = *v; c.x = 99;` inside `fun touch(v: &mut P)` writes 99 into the
   caller's value. The emit is `let c = v;` where a `__clone` is owed. A snapshot
   taken through a lend (`Some(*v)`) likewise follows the next in-place write.
   `--backend rust` refuses the emitted Rust. Repro:
   `probes/store/find_deref_copy_aliases.vl`.
4. **(Minor) A closure type with a `&mut` parameter is refused as a struct field
   but accepted nested one level down.** `struct Holder { f: |&mut str| void }`
   is refused ("a view cannot escape its scope"). `struct Nested { g:
   |(|&mut str| void)| void }` is accepted, and so is a `|&mut T| void` captured
   by a stored closure. A function that *takes* a view is not a view, so either
   the refusal is too strict or the nested acceptance is a hole. Repro:
   `probes/store/find_view_field.vl`.

## 9. Open questions, each with a recommendation

- **Q1. The build door.** Macro (`[derive(Storable)]`, std only) or compiler
  (generated node types, static paths). **Rec: macro first** (S1–S3). The
  compiler door (S5) only if a measured need appears after the finds are fixed.
- **Q2. The slot layout.** A tree of nodes with an `Option` per field, or a side
  table per root keyed by path. **Rec: the tree** (§3.3). It prunes by path, it
  commits along the spine, and its uniform form is what the macro door can emit.
- **Q3. The encapsulation boundary.** Structural everywhere, opt-in by derive, or
  structural within the package. **Rec: opt-in by `[derive(Storable)]`** (§4).
  vilan has no private fields, and every other derive already works this way.
  Non-derived types are leaves; declared shapes are keyed or sequence nodes.
- **Q4. The granularity knob.** **Rec: a field attribute `[reactive(coarse)]`**,
  read by the derive. Coarse *types* need no knob under Q3's rec.
- **Q5. `Store::new` or `reactive let`.** **Rec: `Store::new` only** (§5).
- **Q6. What `set` means through a variant or an `Option`.** **Rec: such a handle
  is `Source<Option<P>>` plus `patch(value: P): bool`**. The write lands only
  while the variant is live, and the bool says whether it did. It does not
  implement `Signal`, because `set(None)` has no meaning there. Switching the
  variant is a write to the enum's own handle.
- **Q7. Does a store write compare?** **Rec: yes, always** (§2.3). "A write wakes
  exactly the live slots whose value changed" is the store's contract. It
  deliberately differs from `SignalCell::set` (R7). `notify()` is the
  non-comparing escape.
- **Q8. The handle's name.** `Store<T>` for root and projection alike, or a
  separate `Lens<T>`/`Focus<T>` for projections. **Rec: `Store<T>` for both.**
  A projection reads, writes, subscribes and projects exactly as a root does, and
  one name keeps hover and diagnostics short (E227's `[hint]` applies unchanged).
- **Q9. Name collisions in generated projections.** A field named `get`, `set`,
  `on_change`, `derive` or `patch` collides with the handle's own members, and an
  inherent member wins (§1.3). **Rec: the derive refuses such a field** with a
  steer to `[reactive(name = "..")]`, which renames the projection. That leaves a
  field-syntax use (S4) unambiguous.
- **Q10. The trait and derive name.** **Rec: `Storable`**, so that the derive is
  named after the trait it implements, like `Hashable` and `PartialEq`, and
  `Store` stays the handle.
- **Q11. `at(index)` on a list field.** **Rec: not offered** (§2.7). A keyed list
  offers `by_key(k)`.
- **Q12. Slot lifetime.** **Rec: counted per slot**, freed at the last
  unsubscription, with empty nodes pruned (§2.2). A handle has no owner.

## 10. Slices

| Slice | Content | Size | Needs |
|---|---|---|---|
| S1 | `Storable` with the two leaf tiers; `Node`; `Store<T>` (`Source` + `Signal`, notification-only slots delivered through the turn, the spine commit, counted slot lifetime); `Store::new`; `[derive(Storable)]` for structs; through-`Option` projections; the Q9 refusal | M | A142 S1 (the handle is a `Source`/`Flow`); finds 2 and 3 fixed (or the list-copy workaround kept internal) |
| S2 | Enums: the discriminant projection, through-variant handles with `patch`, and the UI helper that rebuilds only on the discriminant and hands the body the payload's `Store<P>` | S–M | S1 |
| S3 | Declared shapes as nodes: `HashMap`/`HashSet` keyed nodes (`at`, `contains`, `MapOp`/`SetOp` out), `List` sequence nodes (`SeqOp` out, `reconcile_to` on whole writes, `by_key` for keyed lists) | M | S1; `reactive-maps-sets.md` S1 (the Map/Set cells whose bodies these nodes reuse); I9's names |
| S4 | Field syntax on handles: the member-resolution tier (§3.2), completion and hover in the LSP | S | S1 |
| S5 | Compiler-generated static node types and paths | L | only on a measured need after S1–S3 |
| S6 | kolt exhibits: `Account`, `ChannelRecord`/`GlobalStore`, `get_message` (§6), as a patch the owner applies | S | S3 |

S1–S3 are std and macro work. S4 and S5 are compiler work. None of it is
breaking: `Store` is new surface.

## Appendix A. The prototype (0.41.1)

`store_lens.vl` follows `reactive-layers.md` Appendix A's style. Its toy root is
a `Shared<User>`, and a `Slot` is a list of wake-up closures, so the layout and
diff mechanics are isolated from the turn machinery. The user type exercises
every shape: scalar leaves, a nested struct, an enum with a payload, and a map:

```vilan
struct User { name: str, age: i32, address: Address, presence: Presence, scores: Map<str, i32> }
enum Presence { Offline, Online(Device) }
```

Layout I (the tree), as the compiler door would generate it:

```vilan
struct UserNode {
	me: Option<Slot>,                       // whole-value subscribers
	name: Option<Slot>,
	age: Option<Slot>,
	address: Option<Shared<AddressNode>>,
	presence: Option<Shared<PresenceNode>>, // tag slot + Online's payload node
	scores: Option<Shared<ScoresNode>>,     // keyed slots
}

/// A leaf: compare only when someone below or above needs the answer.
fun leaf<T: PartialEq>(slot: Option<Slot>, a: T, b: T, need: bool): bool { .. }
```

Layout D (the macro door, `store_derive.vl`) replaces the node types with one
`Node` and puts the dispatch in the `Storable` tiers. A projection is one step
composed onto its parent:

```vilan
impl Store<User> {
	fun address(self): Store<Address> {
		project(self, 2, 2, "address", |u| u.address, |up, f| up(|&mut u| f(&mut u.address)))
	}
}
```

The scenarios, with 8 leaves and 3 whole values subscribed and a variant gate
over `presence`. I and D agree line for line; T agrees on every woken set, in
its own order.

| Scenario | Woken (I and D) | Comparisons I / T / D |
|---|---|---|
| new, then one read | nothing; `slots=0 nodes=0` | 0 / 0 / 0 |
| whole write, `zip` changed | `address.zip address user` | 8 / 11 / 8 |
| same-variant write, `since` changed | `online.since presence user`; `built+=0` | 8 / 11 / 8 |
| variant switch to `Offline` | `presence.tag online.name online.since presence user` | 6 / 11 / 6 |
| variant switch back to `Online` | the same five; `built+=1` (and `wakes=7`, §2.8) | 6 / 11 / 6 |
| whole write, `scores[b]` changed (only `scores[a]` observed) | `user` | 9 / 11 / 9 |
| whole write, nothing changed | nothing | 9 / 11 / 9 |
| handle set `address.city` | `address.city address user`; the root holds `Bergen` | 8 (full) / 11 / 1 (spine) |
| handle set, same value | nothing | 9 / — / 1 |
| handle set through the live variant | `online.name presence user` | 8 / — / 1 |
| handle set through a dead variant | nothing; the variant stays `Offline` | — |
| handle set `scores[a] = None` | `scores[a] user` | 6 / — / 1 |

The coarse model, the same 8 projections over one cell, after a `zip` write:

- without `.distinct()`: 8 runs and 8 wakes;
- with `.distinct()`: 8 runs, 3 wakes and 8 comparisons.

The toy lacks per-run owners, so a gate that builds twice keeps its first body's
subscriptions. That is why the through-variant write reports `wakes=4` against
three logged slots; S2's owners release them.

Timings are CPU-bound loops on node 24 under the JS emit, three runs each, with
the counters in every arm. They are wall time inside one process, and they
compare arms within one program. `probes/run_all.out` was captured while other
lanes were building, with a load average near 60. Its counts are identical. Its
times are noisier: there the inline layout's whole write ran at 0.8× the coarse
arm for 11 slots and 3.9× for the 1,000-key map, so the ms columns above are the
quiet runs'. The spine commits (0–2 ms) and the lend read (1 ms) hold in both.
The macro-door prototype's whole-write times are dominated by its list-copy workaround for
find 3, so the table quotes its comparison counts, which are exact, instead.
