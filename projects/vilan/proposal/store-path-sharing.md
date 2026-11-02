# A store handle's path is shared, not copied (M186)

- status: DESIGN 2026-11-02 (integrator; lane m186 builds it; rides v0.54.0)
- item: M186 — a read below any store handle copies the handle's path lists on the
  way down (~74 `__clone` calls per read of a five-step path, whatever the payload)
- lineage: `store.md` (A142 S7, the handle types), `hash-map-lend.md` (B689: the
  payload copy), `store-assume-keeper.md` (B693: the fallback copy; this item is
  its §7 find)

## 1. The fault

A handle is a struct holding its `root`, its `path: List<StoreStep>` (and, for
`StoreSome`, its `gate`, a second list), and two closures. Every projection —
`project`, `descend`, `variant`, `tag`, `live`, `assume`, the derive's field
methods that call them, `some()`, `at(key)` — takes `self` by value and builds a
new handle:

```
Store<F> {
    root = self.root,
    path = child_path(self.path, step),   // the parent's list copied, plus one
    ...
}
```

A `List` is a value: binding it copies it, passing it copies it, and
`child_path` copies it again to push. A five-step read
(`live.records().at(1).some().title().get()`) builds five handles, and each copies
its parent's list on the way in (`self` by value), on the way out (the struct
literal) and in `child_path`; a `StoreSome` copies `gate` beside it. Measured with
the harness's `__clone` counter: 74 calls per read, independent of the payload's
size, every one a `List<StoreStep>`. On node a list copy is an array allocation
and a map over its steps; natively a `Vec<StoreStep>` clone with its `Hash`
payloads. B689 and B693 removed the term that grew with the payload; this is the
constant that is left (~10 µs a read on node).

Nothing on a READ needs the path at all. A `get()` runs the handle's lend; the
path is read only when something asks for a SLOT (`on_settle`, `attach_observer`,
a flow's `open`), for an IDENTITY (`identity()`, a tracked read), or WRITES
(`set`, `patch`, `notify`, a splice — the spine walk, the wire log).

## 2. The mechanism: a persistent cons-list

The path becomes a value whose copy is one pointer: a linked list of steps, leaf
first, each node pointing at its parent's. A projection allocates ONE node; a
handle copy copies one `Option<Shared<…>>`.

```
/// A store's path (M186): the steps from the root, shared — a projection
/// allocates one node pointing at its parent's path, and a handle copy copies
/// one pointer. Read as a list (`steps`) only where the slot tree is walked.
export struct StorePath {
    [internal("the innermost step; reach the path through `steps`")]
    end: Option<Shared<StorePathStep>>,   // `None` at the root
}

/// One step of a `StorePath` and the path above it.
export struct StorePathStep {
    step: StoreStep,
    above: StorePath,
    /// How many steps from the root, so `steps` fills its list without a second pass.
    depth: usize,
}

impl StorePath {
    fun root(): StorePath                        // end = None
    fun child(self, step: StoreStep): StorePath  // one `Shared::new`
    fun len(self): usize                         // the end's depth, 0 at the root
    fun steps(self): List<StoreStep>             // root → leaf, one allocation
}
```

`steps()` walks from the end up, filling a list of `len()` entries from the back
(or pushing and reversing in place — the lane picks the cheaper on both backends;
`List::reverse` allocates a second list, so prefer a fill by index).

### 2.1 Who holds what

- `Store.path`, `StoreSome.path`, `StoreSome.gate`, `StoreFlag.path`: `StorePath`.
- `Store::new`: `path = StorePath::root()`.
- `descend`/`project`/`variant`: `path = self.path.child(step)`;
  `flag_path(path, index)` = `path.child(Field(0)).child(Field(index))`.
- `assume`: `root`, `gate`, `path` copied as pointers (unchanged shape).

### 2.2 Who materializes

The tree walkers keep `List<StoreStep>` — they index and iterate it (`spine`,
`node_made`, `node_chain`, `prune`, `prune_empty`, `slot_at`). The ENTRY points a
handle calls take a `StorePath` and materialize once per call:

| entry | today | after |
|---|---|---|
| `identity_at(root, path)` | `canonical_hash(path)` | `canonical_hash(path.steps())` — the same key for the same path, so an identity minted before a projection is remade is the same number (A146 holds) |
| `store_identity_at` | list | `StorePath` (store.vl's mirror seam: `mirror_boundary*`) |
| `watch_at`, `store_watch`, `observe_at` | list | `StorePath`; `slot_at(root, path.steps())` |
| `counted(root, path, slot, handle)` | captures the list for `prune` | captures the `StorePath` (a pointer) and materializes at prune time |
| `attach_feed`, `detach_feed` | list | `StorePath` |
| `write_at`, `notify_at`, `splice_at` (store.vl) | `spine(root, &path)`, `WireWrite { path }` | `let steps = path.steps();` once; `spine(root, &steps)`; `WireWrite { path = steps }` — the wire log keeps a LIST (`mirror.vl` reads it as one); it is recorded only while a mirror stands |
| store.vl flows' `open` (`MapFlow`, `SetFlow`, `CollFlow`, …) | capture `self.path` (list) | capture the `StorePath` |
| `mirror_boundary*` (store.vl ~:1670) | `place = local.path` | `place = local.path.steps()` — `MirrorBoundary.place` stays a list (relative paths are applied under it) |
| `MirrorAt.below` (store.vl ~:1657) | `mut path = self.path` | untouched: `MirrorAt.path` is a `List<MirrorStep>`, the WIRE path, not the store's |

Relative paths — the `Storable` mirror methods' `path: &List<StoreStep>` /
`into: &mut List<StoreStep>`, `MirrorBoundary.apply(rel, …)`, `list_span(path,
from)`, everything in `rpc/mirror.vl` — are lists built from the wire and stay
lists. Only the HANDLE's own path changes type.

### 2.3 Cost accounting

Per projection step: one `Shared::new` (an object on node, an `Rc` natively)
instead of two to three list copies. Per handle copy: pointer copies. Per
subscription / write / identity ask: one `steps()` materialization (one list of
`len()` entries) that today did not exist — the same order as one of the copies a
read used to make, paid only on the operations that walk the tree. A write's
`spine` and the wire log read the materialized list exactly as before.

An identity ask on a TRACKED read (`identity()` per run, A146) hashes the
materialized list where it hashed the handle's list: the same hash of the same
steps, plus the fill. If the lane's measurement shows that fill mattering on a
read-heavy page, the fallback is a lazily cached key on the step node
(`key: Option<Hash>` set on the first ask through `Shared::write`) — not built
unless measured.

### 2.4 Why not views

Making every projection take `&self` would avoid the copies at the receiver but
not in `child_path` or the literal, would change the derive's output and every
user-written projection chain, and would not help the `gate` copy. The cons-list
makes every copy cheap without touching the surface.

## 3. Not done here

- The derive's projection methods and the `Storable` trait: unchanged.
- The wire protocol: `WireWrite.path`, `MirrorBoundary.place`, `apply(rel)` stay
  lists — nothing on the wire changes shape.
- `StoreStep` itself: unchanged (the completion pin that names `List<StoreStep>` in
  its comment, vilan-ide `completion/tests.rs:357`, is about internal fields not
  being offered; re-read it and update the comment if the type it names moved).

## 4. Pins

1. **Copies per read, exact** (the M172 form, `copies_per_print`): the B693
   phases program's hundred-read phase at 10 and 1,000 records — the per-read
   `__clone` count after, pinned as the exact number (74 before; expect ~10–15:
   the handle struct copies remain as O(1) `__clone` calls that copy nothing).
   Plant: revert `child_path` to a list copy in one projection and watch it go red.
2. **Linear in the depth, constant per step**: reads at depth 3 and depth 5 of the
   same program differ by exactly two steps' worth; pin both numbers.
3. **A path's identity survives its sharing**: `identity()` of a projection made
   twice is the same number; made from a copied handle, the same; a different
   path's differs (A146's existing pins must stay green unchanged — run
   `-- identity a146` first).
4. **Subscriptions, feeds, prune**: the slot-lifetime pins (`store_census` Q12),
   the feed-lifetime pins (`store_feed_census`, B693's keeper), the mirror pins
   (`mirrored` / A153) — all unchanged and green: they walk the materialized path.
5. **The wire log**: `WireWrite.path` for a write below a five-step handle lists
   the five steps root-first (an existing A153 pin reads it; if none pins the
   order, add one).
6. **Native differential**: the B693 program (`native/store_assume_keeper.vl`)
   unchanged and green; a new `native/store_path_sharing.vl` that projects to depth
   5 under keys and fields, subscribes, writes, prunes and prints the census and
   the values on both backends.

## 5. Docs and records

- `docs/std/store.md`: no surface change; the "handles are cheap to copy"
  sentence, if the page has one, gains "a projection allocates one step". Mention
  nothing else.
- CHANGELOG `## Unreleased`, family perf, one bold head: M186.
- `store.vl`'s header design notes (the module top): one line on the path.

## 6. Owner questions

- Q1: `StorePath` and `StorePathStep` are exported (the reach rule: a public
  struct's field type) and `[internal]`-marked where the handles' fields are. Rec:
  export, internal.
- Q2: the lazily cached identity key (§2.3) is not built unless measured. Rec:
  measure first.
