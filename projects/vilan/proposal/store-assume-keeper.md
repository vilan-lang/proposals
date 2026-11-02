# The assumed handle's fallback, kept at the variant's end — not copied per read (B693)

- status: DESIGN 2026-11-02 (integrator; lane b693 builds it; rides v0.54.0)
- tracker: B693 (the owner's item, filed 2026-11-02 measuring B689's fix on next f9fcc6ce)
- touches: `std/src/reactive/store_core.vl` (`StoreSome::assume`, `store_switch`), docs `std/store.md`, pins in `crates/vilan-core/tests/inference/store.rs`
- related: B689 / `hash-map-lend.md` (the keyed step), B526 / `mirrored-store.md` Q11 (the last-value rule this must keep), A149 S3 (feeds), `ambient-owner.md` (`defer_to_owner`)

## 1. The fault

`StoreSome::assume()` hands a body a `Store<P>` through a variant. Its lend keeps a
fallback for a reader that runs in the turn that ENDS the variant (B526: a
derivation settles before the effect that tears the body down, and must read the
edit, not the text the body was built over):

```
lend = |f: |&P| void| {
	mut reached = false;
	lend(|payload: &P| {
		reached = true;
		last = Some(*payload);     // <- a deep copy of the WHOLE payload, per read
		f(&payload);
	});
	if !reached { match last { Some(let held) => f(&held), None => {} } }
},
```

and `mut last = self.get()` copies it once more at `assume()`. Every read BELOW the
handle — `live.records().at(1).some().title().get()` — goes through this lend, so
one title read copies the entire payload. Kolt wraps an organization's store in
`when_remote_live`, so each field read copies every task, channel, message and
document; B689's keyed-step fix changed nothing for it. The item's repro, 2,000 title
reads: 13.4 / 271 / 4,264 ms for 10 / 1,000 / 10,000 records on next f9fcc6ce.

The copy is there to serve the fallback, and the fallback is needed in exactly ONE
moment: after the write that ends the variant, before the body is released. Copying
on every read is copying at the wrong time.

## 2. The mechanism: a keeper feed on the variant's flag

The store already has a hook that runs around a write, typed and per subscriber: a
`StoreFeed` (`store_core.vl`, A149 S3) stands on a node, is told what a write touched
(`touch`), reads its part BEFORE the write lands (`before`) and again AFTER
(`after`). Feeds are how a map flow records `Put`/`Delete` around a write without
the slot tree knowing the map's type.

The fix makes the fallback a feed — the **keeper** — standing on the handle's
**gate** (`self.gate`, the innermost variant's flag node, `flag_path(parent, index)`):

- `touch`: nothing.
- `before`: lend the payload through the variant (still live before the write
  lands) and copy it into `last`. If the lend reaches nothing (the variant is
  COMING, not going), nothing is copied.
- `after`: nothing.

and `assume()`'s lend reads in place with no copy, falling back to `last` only when
the lend reaches nothing:

```
fun assume(self): Store<P> {
	let lend = self.lend;
	mut reached = false;
	lend(|_payload: &P| { reached = true; });
	if !reached { panic("`StoreSome::assume` on a variant that is not live"); }
	// The fallback: the payload as it stood when the variant ended, taken by the
	// keeper below in the write that ended it, and never on a read. A binding the
	// two closures capture, not a cell (spec §6.9, M93's rule).
	mut last: Option<P> = None;
	let keeper = StoreFeed {
		id = fresh_identity(),
		touch = |_touch: StoreTouch| {},
		before = || lend(|payload: &P| { last = Some(*payload); }),
		after = || {},
	};
	let root = self.root;
	let gate = self.gate;
	attach_feed(root, gate, keeper);
	defer_to_owner(|| detach_feed(root, gate, keeper.id));
	Store<P> {
		root = self.root,
		path = self.path,
		lend = |f: |&P| void| {
			mut reached = false;
			lend(|payload: &P| { reached = true; f(payload); });
			if !reached {
				match &last { Some(let held) => f(held), None => {} }
			}
		},
		modify = self.modify,
	}
}
```

(The exact closure spellings are the lane's; `match &last` is the B689 form so the
native backend reads the fallback where it is.)

### 2.1 Why the FLAG node and not the payload's

A write INSIDE the payload (`live.records().at(1).some().title().patch(..)`) walks
`spine()` down through the payload node and touches every feed on the way with
`StoreTouch::Whole` — a keeper on the payload node would copy the whole payload on
every inner write, a per-keystroke copy of the organization in kolt's live edit. The
flag node is on no inner write's spine: `[.., Field(1 + i), ..]` passes the enum
node and the payload node, never the discriminant (child 0) or its flags. The flag
node's feeds are told only when the variant comes or goes — which is §2.2.

### 2.2 `store_switch` tells the flags' feeds

Today `store_switch(node, from, to, woken)` wakes the discriminant's slot, the two
flags' slots, and every slot under the two payloads (`store_wake_all`, which also
touches the feeds under the payloads). It does not touch the FLAGS' feeds: nothing
stood on a flag node before this. The change: after `store_wake_me(store_kid(flags,
from), ..)`, `store_touch(store_kid(flags, from), StoreTouch::Whole, woken)`; the
same for `to` when `to != from`. `write_at` then runs the keeper's `before` ahead of
the assignment (`for feed in woken.feeds { (feed.before)(); }`), with the payload
still in place.

Every way a variant ends reaches `store_switch` or `store_wake_all`:

| the write | the diff's path to the keeper |
|---|---|
| `presence.set(Presence::Offline)` (the enum's own handle) | the derive's enum diff → `store_switch` |
| `slot.set(None)` on a `Store<Option<P>>` | `Option`'s structural diff → `store_switch(node, 1, 1)` |
| the key removed under `records.at(id).some()` (`at(id).set(None)`, `remove(id)`) | the map's diff compares `value_at` old/new (`Option<V>`) → `Option`'s diff → `store_switch` on the keyed node |
| a whole-state write that replaces the enum (`store.set(State { .. })`) | the derive walks down to the enum → as above |
| an OUTER variant ending (`Option<State>` → `None` above the inner handle) | `store_switch` on the outer node → `store_wake_all` of its payload subtree, which touches every node's feeds on the way down, the inner flag's among them |
| a `[reactive(coarse)]` or equality-less leaf above it changing | `store_wake_all` of the leaf's subtree, as above |

A `notify()` compares nothing and lands nothing, so it cannot end a variant. There
is no other writer: `write_at` and `splice_at` are the store's two.

### 2.3 Lifetime: released with the ambient owner

`when_live` / `when_remote_live` call `assume()` inside `when(..)`'s body, which runs
under the body's fresh owner; the keeper's detach is deferred to it
(`defer_to_owner`, the owner-OPTIONAL shape of `register_with_owner`, `ambient-owner.md`),
so the keeper goes with the body. Ordering in the teardown turn: the ending write
runs the keeper's `before` (the copy) → the assignment → the woken derivations read
the fallback → the `when` effect disposes the body → the keeper detaches. Inside a
`scoped_effect` or a derive body the ambient owner is the RUN's, so the keeper is
detached before the next run and re-attached by that run's `assume()`.

Called OUTSIDE any owner (the top of `main`, the existing pins), the keeper stands
for the store's life — the same lifetime as the handle it serves today, and the
leak-as-today rule `register_with_owner` documents. `assume`'s signature does not
change: `owner_scope.get_safe()` needs no `context` clause (as `register_with_owner`
has none), so no caller is affected.

### 2.4 The semantics, restated

Before: "the LAST payload a read through the live variant saw". After: "**the payload
as it stood when the variant ended**". The second is never older than the first (any
read's value was written by some write at or before the end), and it is what B526
asked for: a message edited then deleted repaints its edit. Both existing pins
(`a142_s7_a_payload_store_assumed_reads_the_last_payload_once_the_variant_ends`,
`b526_an_assumed_handle_holds_the_last_value_its_subscribers_read`) stay green
unchanged; the docs sentence in `std/store.md` ("reads the LAST payload a read
through the live variant saw") is reworded to the new rule.

One copy of the payload per variant end, per live `assume()` — the price of the
fallback, paid once where it is needed. Zero copies at `assume()`, zero per read.

## 3. Not done here

- **Not copying at the end either** — a fallback that holds a reference into the
  value the store just dropped is impossible natively (the payload is owned by the
  store's root value and dropped by the assignment), and a JS-only reference-keep
  would be two semantics for one function. The one copy stays. (The owner's B689
  follow-up "the same copies on leaving a page" is this copy, once per leave,
  rather than per read.)
- **A keeper per node shared by every `assume()` on it** — the node is untyped
  (`StoreNode` is one type for every user type, §3.1), so a typed `Option<P>` cannot
  hang off it; the typed half of a feed is its closures, which is why one keeper per
  `assume()` (two bodies over the same handle = two feeds, two copies at the end).
- `M183` / `M184` (the map diff's and `HashMapCell::at`'s copies) are separate items.

## 4. Pins (the lane's)

In `crates/vilan-core/tests/inference/store.rs` unless said:

1. The two existing B526 / A142 S7 pins unchanged and green.
2. **Codegen shape** (the B689 form, `std_surface.rs:916`): the emitted `assume`
   (its lend closure) carries no `__clone`; the keeper's `before` is the only
   `__clone` the function emits. Prove it non-vacuous by planting `last =
   Some(*payload)` back in the lend.
3. **The keeper copies at the end, not on a read**: a payload with an equality-less
   leaf would not do; instead count feeds — `store_feed_census`: `assume()` under
   an owner attaches one feed, the owner's dispose detaches it (census back to the
   figure before); `assume()` twice under one owner = two; outside any owner = one
   for the store's life.
4. **A write inside the payload does not fire the keeper**: pin through a
   `Store<HashMap<i32, Record>>`-shaped state where the keeper's `before` would be
   observable by its cost is not deterministic; pin it structurally instead — a map
   flow's feed on the payload's map node IS touched by a write at a key (the
   existing A149 behaviour), while the keeper on the flag node is not: assert via
   the trace of which feeds a write enlists if the store has an instrument for it,
   else by the design's spine argument plus pin 5. (If no instrument exists, say so
   in the report; do not add a sleep or a timing gate.)
5. **Every row of the §2.2 table**: the enum's own handle, `Option` → `None`, a key
   removed under `at(id).some()`, a whole-state write, an outer variant ending —
   each reads the pre-end payload through the assumed handle after the end, on both
   backends (`assert_compiles_and_runs` is JS; add the enum + map rows to the native
   differential beside `hash_map_lend.vl`).
6. **Dead at `assume()`** still panics; **live again** after an end then a new
   `Some` reads the NEW payload (the keeper's `last` is stale but unused while the
   lend reaches).
7. The item's repro timings before/after on node and native: reported, not a gate.

## 5. Docs

`vilan/docs/std/store.md` `when_live` paragraph: the fallback sentence reworded
("it reads the payload as it stood when the variant ended — a message edited and
then deleted shows its edit, never the text the body was built over — and a write
then lands nowhere"), plus one sentence that the handle keeps nothing on a read and
copies the payload once when the variant ends, released with the body's owner.
`when_remote_live`'s doc comment in `web/remote.vl` says "holds its LAST value" —
consistent, leave or reword to match. CHANGELOG `## Unreleased`: a `fix` entry
(B693) in the A178/B689 form.

## 6. Owner questions

- **Q1.** Outside any owner, the keeper stands for the store's life (the
  `register_with_owner` rule). Alternative: refuse `assume()` outside an owner (a
  COMPILE error, the `on_cleanup` rule). Rec: leak-as-today, as the paper says; the
  stronger law is A130's conversation.
- **Q2.** The reworded semantics ("as it stood when the variant ended") — ratify, or
  keep the old sentence (which the new mechanism also satisfies).
