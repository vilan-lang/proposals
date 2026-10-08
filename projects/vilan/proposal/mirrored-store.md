# The mirrored `Store` — a server's `Store<T>` mirrored by the client, one seed then per-field patches (A153)

> Status: **DRAFT 2026-10-03 — for the owner's ruling** (R-d: a paper this order, nothing
> built). Written by lane papers-46 of Order 46 against `vilan 0.43.0 (fe092e8d1)`, with
> std read at the tag (`v0.43.0`, a408d5db). Nothing in the compiler, std or kolt changed.
> Every claim about today's behaviour is a probe that was run (JS) or a line that was read.
> No probe here ran natively: cargo was off limits this order, so the native rows are
> emitted-source reads (`vilan build --backend rust --stdout`) and nothing native was run.
>
> Probes: `scripts/integration/sweeps/order46/papers-46/probes/store/`, re-run by
> `probes/run_all.sh`, output in `probes/run_all.out`. Cited as `sN`.
>
> Related:
> - A142 / `store.md` (the local `Store`, R1–R37, Q1–Q12 ruled 2026-10-01);
> - A149 (S3, the keyed and sequence nodes, being built this order by store-46);
> - A152 (`zip_some`, `when_all_some`), A150 (`states()` on a mirror, R-c);
> - A144 (the contract hash reads resolved types), A146 (handle identity);
> - A39 (per-key demand on the protocol), A54 (op-log forwards), A79 / A92 / A134 (handle
>   returns, dynamic channels, origin identity), A137 (a sibling seeds the joiner);
> - `transport-rpc.md` §8–§9, `remote-sources.md`, `reactive-maps-sets.md` §7.

## 0. The ask, and the answer up front

The owner's rule (A153). An rpc for a granular field that can be called where the parent
does not exist must answer a maybe type. A field reached THROUGH the parent struct need not:
the struct must exist to be passed, and the field's source is disposed when the parent's
derivation turns `None`. The amendment, already agreed: holding the struct proves the parent
existed only as of the client's last frame, because a delete can cross a field call on the
wire. So the WIRE answer stays a maybe and the client model hides it: inside the parent's
scope, an absent field means the scope is about to be disposed, so the field holds its last
value.

The catch is the first value. A field mirror has nothing until its first frame. A non-optional
`Source<T>` therefore needs either a WAIT (A152's `when_all_some`) or a SEED: the parent's
snapshot carries the field's value, and the handle starts from it and then follows its own
channel.

**The answer.**

1. **Today's id-keyed surface pays a round trip and two frames for every handle** (s1,
   measured). Opening a kolt channel with 50 messages leases 55 handles. That is 55 rpc
   round trips, 55 `Subscribe` frames and 55 seed `Update`s: **220 frames, 9,598 bytes**,
   and six round trips of dependency depth before the authors' names paint. A rename costs
   34 bytes on the push. An edit re-sends the whole message, 92 bytes.
2. **A mirrored store sends a seed once, then patches** (s2: projected bytes, written by
   today's codec). The same open costs **108 frames / 7,483 B** with one frame per
   subscription, and **8 frames / 5,583 B** with the client's subscriptions and the server's
   seeds coalesced per turn. It takes three round trips of depth, not six. The rename push
   is 51 B. The edit push is 65 B, and it carries only `content`. A snapshot-as-unit design
   would re-send the record on a rename: 203 B.
3. **The owner's rule falls out of the local store's own type algebra.** A handle through a
   maybe is a `StoreSome<F>`. `when_live` hands its body `assume()`'s `Store<P>`, whose
   fields are plain `Store<F>`s (s6). The amendment needs one change. `assume()` holds the
   value *at the call*, not the *last* value, so an edit followed by a delete shows the
   pre-edit text for the turn before teardown (s6, find 2).
4. **Seed inside, wait at the boundaries.** The wire's unit is a DEMAND BOUNDARY: the
   granted root, each keyed child (`at(k)`) and each key set (`keys()`). A boundary's seed
   carries its whole subtree, so every field reached through it is seeded and needs no
   maybe. Only a boundary waits, and a boundary is exactly where the owner's rule already
   puts a maybe.
5. **Nothing in 0.43.0 can carry it yet.** An `[rpc]` returning `Store<T>` or `StoreSome<P>`
   is refused as "not Wire" (s5). A map field is a leaf with no `at` (s4), and one key's
   write wakes all 50 of its observers. The contract hash renders type NAMES only: adding
   or reordering a Wire struct's fields leaves it unchanged (s3, find 1). Field-indexed
   patches cannot ship until the hash covers the shape.

**Recommendation.** Build the mirrored store as a fourth handle kind on the existing reactive
protocol (§3–§7, slices S0–S5):

- **One channel per store ROOT per connection**, deduped by the root's identity. An `[rpc]`
  returning a handle into it adds a GRANT (a base path) to that channel.
- **Client-named slots** at demand boundaries. `Subscribe(channel, [(slot, path)])` goes up;
  `Patch(channel, [Seed | Set | Gone | Seq | Keys])` comes down, addressed by slot and
  relative path.
- **Ops at the writer's granularity**, coalesced per root channel per turn (last value per
  path wins).
- **A read-only client face**, `RemoteStore<T>` / `RemoteStoreSome<P>`, whose projections
  the derive writes. Its root is always a maybe until its seed. `when_live` and
  `when_all_some` turn it into plain handles.
- **The contract hash covers the Storable shape** of every type a store return reaches.
- **Reconnect** replays the root rpcs, re-subscribes every live slot in one frame, and
  applies the re-seeds as COMPARING writes. Only what changed during the outage wakes.

kolt's 55-handle open becomes one root rpc per session plus three coalesced exchanges. Its
`model.vl` loses `transient_of`, `map_state` and every per-field stub (§8).

## 1. Ground truth (0.43.0)

### 1.1 Today's traffic on kolt's shapes (s1, measured)

`s1_today_traffic.vl` rebuilds kolt's service (`kolt/src/store.vl`): `GlobalStore` with
`channels: HashMapCell<u53, ChannelRecord>`, `messages: HashMapCell<u53, Message>`, the users
memo, `get_channel`'s memoized view, and the `[rpc]` methods `get_channel`,
`get_channel_name`, `set_channel_name`, `get_messages`, `get_message` and `get_user`. The
only change is that no database is involved. One `edit_message` is added, because kolt has
none yet. The rpc leg is `local_rpc(..).for_connection(7)` wrapped in a counting
`Transport`. The reactive leg is two `duplex_pair`s joined by a counting relay. Bytes are the
JSON envelope plus the socket's lane prefix: `d:` on a reactive frame and `r:<id>:` on an
rpc frame, which is what `route_socket_frame` (`rpc.vl`) reads. One handle, traced:

```
up   rpc  {"method":"get_message","args":[0]}
down rpc  {"Success":0}
up   live {"Subscribe":[0,null]}
down live {"Update":[0,{"id":0,"author":{"uuid":"alice"},"content":"message number 0 says hello"}]}
A0 one message: TOTAL 4 frames / 171 B
```

| Scenario (what kolt leases or writes) | rpc frames / B | live frames / B | **total** |
|---|---|---|---|
| (A) open channel 0 with 50 messages, 2 authors: `get_channel`, `get_channel_name`, `get_messages`, 50 × `get_message`, 2 × `get_user` (55 handles) | 110 / 3,285 | 110 / 6,313 | **220 frames / 9,598 B** |
| (B) rename the channel (`set_channel_name`): the call plus the push `{"Update":[2,"general-renamed"]}` | 2 / 84 | 1 / 34 | **3 / 118 B** |
| (C) edit message 7: the call plus the push, which re-sends the whole `Message` | 2 / 94 | 1 / 92 | **3 / 186 B** |
| (D) write the same name again | 2 / 84 | 1 / 34 | 3 / 118 B; the client's observer **runs once** |

Read from the trace and the code:

- **Every handle is four frames.** The stub mints an unleased mirror. Its first lease runs
  the origin's call (A92). The reply is a channel id. Only then does the mirror send
  `Subscribe`, and the forward sends the seed. Over a socket that is two round trips per
  handle (`rpc.vl` `Origin`, `open_forward`).
- **Six round trips of depth.** The rows cannot be leased before the id list arrives, and
  the authors cannot be leased before their messages arrive. So kolt pays two round trips at
  each of three levels. (This is derived from the frame order. The in-process pair delivers
  inline and cannot time it.)
- **A cell never compares** (R7). (D) re-sends an unchanged name, and the client's observer
  reruns. A reconnect does the same at scale: each re-minted mirror's seed is a
  `SignalCell::set` on its cache, and every observer of every mirror reruns
  (`reattach_mirrors` → `replay`).
- **kolt already splits its records to make (B) cheap.** `Channel` is a bare `{ id }` and the
  name is its own channel (`kolt/src/shared.vl`, `store.vl:231`). The cost of that is the four
  frames per handle and the 184 lines of `model.vl` that wire the handles back together
  (`transient_of`, `map_state`, the `switch<TransientState<..>>` B480 still needs).

### 1.2 The local store, as built (s4, s6, s7)

| Fact | Probe | Consequence for the mirror |
|---|---|---|
| A handle through a maybe is a maybe: `slot.some().content()` is a `StoreSome<str>` | s6 | the owner's "callable where the parent may not exist" half is already the type |
| `assume()` (what `when_live` hands its body, `browser/ui.vl:2419`) types the same field as a plain `Store<str>` | s6 | the "reached through the parent" half is already the type |
| After the parent is deleted, the assumed field reads the value **at the `assume()` call**: patch to `edited`, delete, and it reads `hello` and wakes with `hello` | s6 | the amendment's "hold the LAST value" is not what ships (find 2) |
| Two projections of one path share one identity, and the assumed handle shares it too (A146) | s6 | the dedup key a channel needs exists per path |
| `[derive(Storable, Wire)]` on one struct compiles | s6 | the two derives compose |
| A `HashMap` field of a derived struct is a LEAF: `global.messages().at(7)` → "has no method 'at'"; one key's write wakes all 50 observers of the map | s4 | the keyed node is A149 S3 (this order); the mirror needs it |
| A leaf compares with the type's own `PartialEq`. kolt's `Message` is equal **by id**, so an edit that keeps the id wakes nothing: `observer runs=0 held=edited` | s7 | a mirrored type must derive `Storable` or have structural equality, or its edits never reach the wire (§9) |
| An `[rpc]` returning `Store<Option<Record>>` or `StoreSome<Record>`: "is not Wire" | s5 | `handle_element` recognizes `SignalCell`, `MemoCell`, `KeyedCell`, `HashMapEntry` and `MemoEntry` by spelling (`rpc.vl:6324`); a store is none of them |

### 1.3 The contract hash does not see fields (s3)

`s3_hash_v{1,2,3}.vl` declare one service whose `[rpc]` returns `SignalCell<Option<Message>>`.
v2 adds a field to `Message` and v3 reorders its two fields. All three print
`contract_hash=b8fcf645`. `contract_hash.rs` `render` writes each nominal type by its
declared NAME and its arguments, never its fields. Two consequences follow:

- **Today:** the binary codec is positional ("the shared Wire type IS the schema",
  `wire.vl`). A redeployed server that reordered a Wire struct's fields passes the
  connect-time check, and its clients then decode garbage (find 1).
- **For this paper:** a patch addressed by field index (§3.4) is wrong the moment the shape
  drifts, so the hash must cover the shape before S1 ships.

### 1.4 What the protocol already has

- **A39's optional key on the control frames.** `Subscribe(channel, key?)` already makes
  demand finer than a channel. Here the key slot carries a list of `(slot, path)` pairs.
- **A54's op-log forward.** `keyed_cell_forward` holds a cursor and sends only the ops since
  it. That is the store's forward shape.
- **The wire turn.** Inbound frames are handled in one `batch`, so "a handler that mutates
  subscribed state produces ONE coalesced Update per source" (`rpc.vl` header). It is per
  source today; §5 makes it per root.
- **Origins (A92, A134)** make a dynamic handle re-mintable after a reconnect.
- **No back-pressure exists.** A grep of `rpc.vl`, `rpc_server.vl` and `ws.vl` finds no
  buffered-amount read and no high-water mark.

## 2. The model

### 2.1 Three roles

- **The server** holds an ordinary `Store<T>` (`store.md`): one root and its slot tree. It
  writes it with ordinary handle writes. Nothing about the store changes because a client
  watches it, except that a write is also recorded for the wire while a wire forward stands
  on it (§4).
- **The wire** carries one CHANNEL per (connection, store root). The channel carries GRANTS
  (the base paths the client was handed) and SLOTS (the boundaries the client is watching).
- **The client** holds a REPLICA: a local `Store<T>` whose value is the union of the subtrees
  it has been seeded with. Its handles are a read-only face over that replica
  (`RemoteStore<T>`, §6). A patch is applied to the replica by an internal comparing write,
  so the client's wakes are the store's own diff (Q7 of `store.md`): exactly the live local
  slots whose value changed.

### 2.2 The demand boundary

A node is a **demand boundary** when it is one of:

1. the base of a grant (what an `[rpc]` returned);
2. a keyed child of a map field (`at(k)`), or a set's membership flag (`contains(x)`);
3. a map's or set's KEY SET (`keys()`);
4. a whole map, set or keyed-list field leased as a collection (`each_by(g.channels(), ..)`).

Everything else is INSIDE the nearest boundary above it. That covers struct fields, enum
payloads, `Option`s, tuples and `List` fields. A `List` field is a sequence node (A149 S3),
seeded with its record and patched with `Seq` ops. It is not a boundary unless it is leased
as a collection.

**A lease subscribes at its nearest boundary.** A client lease of
`g.messages().at(7).some().content()` sends `Subscribe` for `[messages, 7]`, the message, not
for `content`. A second local lease anywhere inside an already-subscribed boundary sends
nothing. So the wire never carries a per-field subscription. Its slots are boundaries, and a
boundary slot stays subscribed while any local slot under it is live.

That is how the owner's rule and its catch are met together:

| | where it lives | type at the client | first value |
|---|---|---|---|
| a granular thing callable where its parent may not exist | a boundary (a grant base, a keyed child) | a MAYBE (`RemoteStoreSome<V>`) | **waits** for the boundary's `Seed` |
| a field reached through the parent | inside a boundary | plain (`RemoteStore<F>`), inside `when_live` | **seeded** with the boundary |
| the amendment: a delete crosses a field read | the wire | the boundary's `Seed(slot, null)` or `Gone(slot)` | the scope disposes; until it does, the inner handle holds its LAST value (Q11) |

### 2.3 Why not the other two units

- **Per-field slots** (every leased field is its own subscription). Every field waits for its
  own first frame, so every field handle is a maybe, or sits behind a `when_some`. That is
  today's kolt with a different spelling. It is also the most frames: one `Subscribe` and one
  seed per field.
- **The whole root as one replica** (one subscription, everything seeded). No field ever
  waits. But a root holding `messages: HashMap<u53, Message>` would ship every message the
  server knows to every client on connect, and every write to any of them after. kolt's
  database would be the seed.

**Rec (Q1): boundaries.** Seed inside, wait at the boundaries. A boundary is where the type
already has a maybe (a keyed child is `Store<Option<V>>` on the server, A149 S3), so the wait
costs no new type. The subtree seed means a field never waits.

## 3. The wire

### 3.1 The reply

An `[rpc]` whose return type is written `Store<T>` or `StoreSome<P>` is a handle return. The
`service` macro's `handle_element` learns both spellings, as it learned `HashMapEntry`
(A138). The route's replier is `reply_store` (S1):

1. find, or open, this connection's channel for the handle's ROOT, keyed by the root's
   identity (`identity_at(root, [])`, A146): the A92 dedup, one level up;
2. add a GRANT for the handle's path;
3. answer `(channel, base_slot, seed)`. The base slot is numbered by the server from a
   namespace disjoint from the client's (negatives), so neither side waits for the other to
   name it. The seed is the base boundary's subtree, `Option`-wrapped for a `StoreSome`.

**The seed rides in the reply** (Q5). A dynamic handle is minted only by its first lease
(A92), so the call that mints it is already the subscription. Today the reply names a channel
and the client then asks for it. That ask is one frame and half a round trip per handle,
saved here. The base slot is subscribed from the reply on.

### 3.2 The frames

Up (client → server), on the existing control-frame shape (`encode_control`: a channel plus
the optional A39 key, which here carries a list):

```
{"Subscribe":[channel, [[slot, path], ..]]}     // one frame per turn, every new slot in it
{"Unsubscribe":[channel, [slot, ..]]}
```

Down (server → client), one `Patch` per root channel per turn (§5):

```
{"Patch":[channel, [op, ..]]}

op := {"Seed":[slot, value | null]}             // the boundary's subtree; null = absent
    | {"Set":[slot, relpath, value]}            // a write inside the boundary
    | {"Gone":[slot]}                           // the boundary became absent (key removed)
    | {"Seq":[slot, relpath, seqop]}            // a sequence field's op (A149 S3)
    | {"Keys":[slot, keyop]}                    // a key-set slot's op
seqop := Splice(at, removed_count, inserted) | SetAt(at, value) | Reset(list)
keyop := Put(key) | Delete(key) | Reset([key])
```

`SeqOp::Splice` carries the removed ELEMENTS in std (`delta.vl:108`). The wire carries only
their count, because the client holds them.

### 3.3 Paths

A path is a list of steps, and each step describes itself as the walker reads it:

- a **field** step is the field's declaration index, which is the store's own child index
  (`store.md` §3.1);
- a **variant** step is the payload's child index (`1 + i`, as `StoreNode` numbers them);
- a **key** step is the key described at its own type, as A39 describes a key (`K::rebuild`
  at the walk).

A `Subscribe` path runs from the grant base to the boundary, so it may hold key steps. A
`relpath` inside an op never holds one: keyed children are boundaries, so a boundary's
subtree contains no key step. That is why ops are addressed by SLOT. The server never has to
describe a key outward. S3's `StoreStep::Key(Hash)` keeps only the key's hash, so it could
not.

### 3.4 Indices, names and the hash

A field step is an index, not a name. Measured in s2: 51 B for the rename with an index path
and the slot address, against 53 B with an absolute index path. A name per step would add a
quoted string per level. An index is only correct while both sides agree on the shape, so
**the contract hash must render the shape** (Q3, Q14):

- for every type a `Store<..>` / `StoreSome<..>` return reaches, the template's slot is
  filled with the type's fields in declaration order (name and resolved type), recursively,
  and with an enum's variants in order;
- leaves stop the walk: scalars, `str`, and any type that is not `Storable`-derived. Such a
  type is a leaf on the wire too, sent whole.

A drifted server is then refused at connect and on reconnect (`reattach_mirrors`' drift arm
closes for good), as a renamed method is today.

### 3.5 Measured: what the frames cost (s2)

`s2_store_wire_bytes.vl` builds each frame of §3.2 with today's JSON `Serializer` and real
values, so each length is what the codec would write. The paths use kolt's field order:
`Global { channels 0, messages 1, users 2 }`, `ChannelRecord { id 0, name 1, messages 2 }`,
`Message { id 0, author 1, content 2 }`. Socket prefixes are added as in s1.

```
rpc global:            {"method":"global","args":[]} | {"Success":[0,[]]}      (once per session)
subscribe the channel: {"Subscribe":[0,[[0,[0,0]]]]}
seed one message:      {"Patch":[0,[{"Seed":[8,{"id":7,"author":{"uuid":"bob"},"content":"message number 7 says hello"}]}]]}
rename push:           {"Patch":[0,[{"Set":[0,[1],"general-renamed"]}]]}
edit push:             {"Patch":[0,[{"Set":[8,[2],"message number 7 says goodbye"]}]]}
```

| Scenario | today, id-keyed rpcs (s1, measured) | mirrored store, a frame per slot | mirrored store, coalesced per turn |
|---|---|---|---|
| open channel 0, 50 messages, 2 authors | 220 frames / 9,598 B; 6 round trips deep | 108 frames / 7,483 B | **8 frames / 5,583 B**; 3 round trips deep |
| rename the channel (call + push) | 3 / 118 B (push 34 B) | 3 / 135 B (push 51 B) | same |
| edit one message (call + push) | 3 / 186 B (push 92 B: the whole message) | 3 / 159 B (push 65 B: `content` only) | same |
| same-value write | 3 / 118 B, and the observer reruns | 2 / 84 B: the call only; nothing changed, so nothing is pushed or woken | same |
| (the snapshot as the unit, for contrast) rename push | — | 203 B: the record again, 50 ids included | — |

- **The store's frames include its once-per-session root rpc** (2 frames / 55 B). Every
  later channel opened in the session costs 6 frames, not 8.
- **The rename push is 17 B MORE than today's.** That is the slot and the one-step path.
  kolt made the rename cheap by giving the name a channel of its own, and paid four frames
  per handle for it. The store keeps the rename at one string without that.
- **What remains of the open's bytes is the content.** A message's JSON is about 72 B and
  its `Seed` op about 85 B, so the 50 row seeds are about 4,300 of the coalesced 5,583 B, and
  the messages themselves about 3,600. A binary codec would shrink the envelope, not the
  text.

## 4. The server

### 4.1 What a write records

A write through a server handle does what it does today (`write_at`: diff, assign in place,
wake the live slots). When a wire forward stands on a boundary above the written path, the
write also appends `(path)` to the root's OP LOG. One log per root, created when the first
wire forward attaches and dropped with the last, so a store nobody mirrors records nothing.

**The op's granularity is the writer's** (Q6). Each write records an op at its own path:

| the server writes | the op |
|---|---|
| `global.messages().at(7).some().content().patch(c)` | `Set(slot of [messages, 7], [2], c)` |
| `global.messages().at(7).set(Some(m))` on a present key | `Set(slot, [], m)`: the message whole |
| `global.messages().at(7).set(None)` | `Gone(slot)` |
| `global.channels().at(0).some().messages().push(id)` | `Seq(slot of [channels, 0], [2], Splice(50, 0, [id]))` |

The log records only the PATH. The forward reads the value at that path when it flushes
(§5), so ten writes to one path in a turn send the settled value once. Reading a value at a
path needs one generated walker per derived type: `store_describe_at(&self, steps, serializer)`.
The client applies a value at a path with its twin, `store_apply_at`. The derive writes both
beside `store_diff`, from the same field list. A type that is not derived is a leaf, and its
walker describes it whole.

The **diff-split** alternative uses the diff's own walk to split a whole-value write into
per-leaf ops. It sends less for a coarse writer, but it changes `store_diff`'s signature (a
path collector) and costs a push per changed leaf on every logged write. It waits for a
measured need (S6).

### 4.2 Per connection

| | today (55 handles of s1) | mirrored store (the same open) |
|---|---|---|
| capability entries | 55, each a starter closure capturing its source | 1, the root channel, plus its grants (one path each) |
| live forwards | 55, each a subscription on a server cell | 53 slot forwards, each a counted store slot at its boundary node plus a cursor into the root's log |
| client mirrors | 55 `RemoteSource`s (ten fields each, a cache `SignalCell` among them) and 55 `MirrorTable` entries | one replica (the seeded subtrees) and one slot table |

A slot forward IS a store subscription (`watch_at` on the boundary's node), so the server's
slot tree grows and prunes with client demand exactly as it does with local demand
(`store.md` Q12). A slot whose `Unsubscribe` arrives releases its store slot and its cursor.
Disposing the connection releases all of them (`ReactiveServer::dispose`).

### 4.3 Authorization

**The capability is the grant** (Q12). A channel's grants are the base paths its `[rpc]`s
handed out on this connection. A `Subscribe` whose path does not start with a grant is
dropped, as a keyed `Subscribe` on a plain channel is dropped today (`Capability::resolve`).
So:

- `[rpc] fun message(self, id): Store<Option<Message>>` that checks the caller may read `id`
  grants `[messages, id]`. A crafted `Subscribe` for `[messages, 8]` is dropped.
- `[rpc] fun global(self): Store<Global>` grants the root, and every path below it.

**No per-field redaction** in S1. A field that a client must not see does not belong to a
type that crosses whole. Split the type (`Account { public: Profile, secret: Credentials }`)
and grant `account.public()`. A `[wire(skip)]`-style attribute would leave the client's
replica holding a value it was never sent. Every field of a client-side `T` must have one.

### 4.4 Identity and dedup

Two `[rpc]`s that return handles into one root share one channel and one client replica.
`channel(0)` and `message(7)` are two grants on one channel, so a message reachable by two
routes is stored once and patched once. Two calls returning the SAME path are one grant: the
A92 dedup, by path identity (A146).

## 5. Turns, coalescing and back-pressure

- **Per root channel, per turn, one `Patch` frame.** The forward flushes at the turn's settle
  (as `keyed_cell_forward` flushes on `on_change` today), reads each logged path's value
  once, and drops an op whose path lies under another op's path in the same turn (a whole
  write supersedes the field writes inside it).
- **Up, per turn, one `Subscribe` frame.** The client's lease transitions in one turn (a list
  of 50 rows mounting) are collected and sent together, as `RemoteSource` already defers
  its `Unsubscribe` to the settle (`closing`, `settle_id`). That is the "coalesced" column of
  §3.5.
- **Ordering.** A frame's ops apply to the replica in one client `batch`, so the push-pull
  settle sees one consistent state (`reactive-turns.md`). Across two roots, frames
  interleave as two channels' do today.
- **Back-pressure** (Q13). None in S1, as today. A store makes the later fix cheap, because
  its state is addressable. A forward over its high-water mark stops sending, marks its slots
  dirty, and on drain sends each dirty slot's CURRENT value once. "Latest value wins" is the
  store's semantics anyway. It needs a buffered-amount read on `std::ws`, which does not
  exist (§1.4).

## 6. The client

### 6.1 The face: `RemoteStore<T>` and `RemoteStoreSome<P>`

The client must not write a server store ("client code can't write a server signal",
`RemoteSource`'s doc). So the client's handles are a READ-ONLY face over the replica:

- `RemoteStore<T>`: `Source<T>`, with the derive's projections;
- `RemoteStoreSome<P>`: `Source<Option<P>>`, with the projections, `live()`, `assume()`,
  and `states()` (A150's leased pipe of `TransientState`, which separates `Pending` from
  `Absent`);
- `RemoteStoreKeys<K>`: a map's or set's key set (`keys()`), a `Source<List<K>>` fed by
  `Keys` ops, which `each_by` takes as it takes a map's key pipe today.

The derive writes the projections for these two subjects as it writes them for `Store<T>`
and `StoreSome<P>` (`store_struct_impls`, `store_enum_impls`). That doubles the projection
text, not the diff. A single generic `impl` over a handle trait would avoid the doubling, but
vilan has no inherent impl over a trait-bounded subject today (Q8).

**The root is always a maybe** (Q10). An `[rpc]` returning `Store<T>` mints, at the client,
a `RemoteStoreSome<T>`: until the reply's seed lands it has no value, whatever `T` is. Its
first value WAITS, and it is the only boundary every client always waits on.

### 6.2 Leases and slots

A local subscription on any handle allocates a local store slot, as on the server (`watch_at`
on the replica). It also takes a COUNTED hold on its nearest boundary (§2.2). The boundary's
0→1 queues a `Subscribe` for the turn. Its flushed 1→0 queues an `Unsubscribe`, cancelled by
a 0→1 in the same turn (`RemoteSource`'s `closing` discipline). `get()` is passive, as
`RemoteSource::get` is. A boundary nobody holds reads what the replica last held, or
`None`.

When a keyed boundary is released, the replica removes the key, so its memory follows
demand. When the base's last hold goes, the channel's base grant is released and the server
drops the grant (A92's revoke).

### 6.3 The owner's rule, written

```vilan
// a granular rpc callable where the parent may not exist: a maybe
let message: RemoteStoreSome<Message> = g.messages().at(id).some();

// reached through the parent: plain, seeded with the message
when_live(message, |m: RemoteStore<Message>| {
	<span>{m.content()}</span>          // RemoteStore<str>: no maybe, no wait
})

// several boundaries at once (A152)
when_all_some((message, author), |(m, a)| ..)
```

Inside `when_live`'s body, a `Gone` for the message means the body is about to be disposed.
Until it is, `m.content()` must read the LAST value it held. Today's `assume()` reads the
value at the call (s6), so S0 changes `assume()` to refresh its fallback on every successful
read through the live variant (find 2, Q11).

## 7. Reconnect

Today (`reattach_mirrors`): `__contract`, `__attach`, the positional rebinds, then `replay()`,
which re-issues every dynamic mirror's minting call. For s1's open that is 55 calls, 55
`Subscribe`s and 55 seeds, and each seed is a non-comparing set that reruns its observers.

The mirrored store does this instead:

1. re-verify the contract, whose hash now covers the shape (§3.4);
2. replay each ROOT's grants: one call per origin, usually one;
3. re-subscribe every live slot in ONE `Subscribe` frame. The client keeps its slot numbers,
   and only the channel is new;
4. the server answers with one `Patch` of `Seed`s;
5. the client applies each seed as a **comparing** write on the replica. A message that did
   not change while the socket was down wakes nothing. One that did wakes exactly its changed
   fields.

While disconnected, every handle keeps its last value. `states()` reports `Refreshing` (the
stale value with a refresh owed), so a view can show it without blanking.

## 8. kolt, rewritten (the exhibit)

### 8.1 The server (`store.vl`)

```vilan
[derive(Storable, Wire)]
struct ChannelRecord {
	id: u53,
	name: str,
	messages: List<u53>,           // a sequence node inside the record: seeded with it, patched with `Seq`
}

// `Message` and `User` (shared.vl) gain `Storable`. Their identity `PartialEq`
// stays for keyed lists, but the store diffs them FIELD BY FIELD (s7: a leaf
// compared by id would never see an edit).

[derive(Storable, Wire)]
struct Global {
	channels: HashMap<u53, ChannelRecord>,    // keyed: each `at(id)` is a boundary
	messages: HashMap<u53, Message>,
	users: HashMap<UserId, User>,
}

lazy let global: Store<Global> = Store::new(load_global(db));

[service(KoltClient)]
struct KoltStore {
	user_id: UserId,
}

impl KoltStore {
	// The one live surface. Read-only at the client, seeded in the reply
	// (every field is keyed, so the seed is three empty key sets).
	[rpc]
	fun global(self): Store<Global> {
		global
	}

	[rpc]
	fun create_channel(self, name: str): u53 {
		let id = next_channel_id();
		global.channels().at(id).set(Some(ChannelRecord { id, name, messages = [] }));   // `Keys(Put(id))` to key-set slots
		id
	}

	[rpc]
	fun delete_channel(self, channel_id: u53): bool {
		global.channels().at(channel_id).set(None);       // `Gone` to that channel's slot
		true
	}

	[rpc]
	fun set_channel_name(self, channel: u53, name: str): bool {
		global.channels().at(channel).some().name().patch(name)      // `Set(slot, [1], name)`
	}

	[rpc]
	fun add_message(self, channel: u53, content: str): Result<u53, str> {
		let record = global.channels().at(channel).some();
		record.live().get() else ret Err(i"no such channel: {channel}");
		let id = next_message_id();
		global.messages().at(id).set(Some(Message { id, author = self.user_id, content }));
		record.messages().push(id);                        // `Seq(slot, [2], Splice(n, 0, [id]))`
		Ok(id)
	}

	[rpc]
	fun edit_message(self, id: u53, content: str): bool {
		global.messages().at(id).some().content().patch(content)    // `Set(slot, [2], content)`
	}

	[rpc]
	fun remove_message(self, channel_id: u53, message_id: u53) {
		// S3's sequence-node vocabulary; the method name is illustrative
		global.channels().at(channel_id).some().messages().remove_value(message_id);
	}
}
```

`ChannelRecord` stops being a hand-coloured twin (`name: SignalCell<str>`, `messages:
SignalCell<List<u53>>`). `GlobalStore`'s two `HashMapCell`s, its users memo, its
`channel_ids` and `channel_views` memos and their `.memo_global()` derivations all go. So do
`get_channel`, `get_channel_name`, `get_channels`, `get_messages`, `get_message`,
`get_account_user` and `get_user`.

`users` is a keyed field the server must fill. `load_global` loads the authors of the loaded
messages. A user loaded on demand would keep a granular rpc, `[rpc] fun user(self, id:
UserId): Store<Option<User>>`, which fills `global.users().at(id)` and returns it: a maybe,
by the owner's rule.

### 8.2 The client (`model.vl`)

```vilan
import std::rpc::RemoteStore;
import pkg::store::{ ChannelRecord, Global, KoltClient };

// The one mirror, a maybe until the reply's seed lands. A reconnect replays it
// and keeps the replica (§7), so nothing here re-switches on the client.
fun global(client: KoltClient<SocketTransport>): RemoteStoreSome<Global> {
	client.global()
}

impl Channel {
	// was: `find` (a `switch<TransientState<..>>` over `transient_of`, B480's
	// explicit binding), `name`, `messages`, `get_channel_ids` and `get_channels`:
	// five stubs, three state-mappers
	fun find(g: RemoteStore<Global>, id: u53): RemoteStoreSome<ChannelRecord> {
		g.channels().at(id).some()
	}

	fun ids(g: RemoteStore<Global>): RemoteStoreKeys<u53> {
		g.channels().keys()
	}
}
```

`transient_of`, `map_state`, `Account::user`, `User::find`, `Message::find` and the
`impl Source<Option<KoltClient<..>>>` helper all go. A view that needs `Pending` apart from
`Absent` asks the handle: `Channel::find(g, id).states()` (A150's pipe).

### 8.3 The message row (`channel.vl`)

```vilan
fun channel_component(g: RemoteStore<Global>, channel_id: u53) {
	<div .styled(css { padding(rem(8 / 16)); })>
		{when_live(Channel::find(g, channel_id), |channel| {
			// `channel.messages()`: a RemoteStore<List<u53>>, seeded with the record
			ui::each_by(channel.messages(), |id| id, |message_id| {
				when_live(g.messages().at(message_id).some(), |message| {
					let author_name = message
						.author()
						.switch(|author| g.users().at(author).some().username())
						.derive(|name| name.unwrap_or_default());
					<div .styled(css { gap(rem(4 / 16)); .flex_row(); })>
						<span .styled(css { font-weight("600"); })>{author_name}</span>
						<span>{message.content()}</span>
					</div>
				})
			})
		})}
	</div>
}
```

Wire cost of mounting it: one `Subscribe` and one `Seed` for the record, one coalesced pair
for the 50 rows, and one for the authors (§3.5). An edit wakes one `<span>`.

## 9. What it costs, stated plainly

1. **New protocol surface.** Two control-frame payloads and one `Patch` vocabulary of five
   ops. Old clients are fenced by the contract hash, as for any surface change.
2. **Two generated walkers per derived type** (`store_describe_at`, `store_apply_at`) and
   doubled projection text (the read-only face).
3. **The root is a maybe at the client**, always. One `when_live` per root, typically once at
   the app's top.
4. **A mirrored type must diff structurally.** A leaf compared by an identity `PartialEq`
   swallows its edits on the server, so they never reach the wire (s7). kolt's `Message` and
   `User` must derive `Storable`.
5. **The contract hash moves for every service once**, when it learns shapes (find 1, Q14).
6. **The rename push grows** from 34 to 51 B. It is the one row where today's split surface
   is cheaper on the push.

Against those costs:

- the open drops from 220 frames to 8, and from 6 round trips deep to 3;
- an edit sends the field and not the record;
- a same-value write sends nothing and wakes nothing;
- a reconnect re-seeds in one exchange and wakes only what changed;
- kolt's `model.vl` loses its state plumbing.

## 10. Finds (met while probing, for the integrator to file)

1. **The contract hash does not see a Wire struct's fields.** Adding a field or reordering two
   leaves `contract_hash()` unchanged (`b8fcf645` for all three of s3's versions).
   `contract_hash.rs` `render` writes nominal types by name and arguments only. Under the
   binary codec, which is positional, a redeployed server with a reordered struct passes
   `__contract` and its clients mis-decode. Repro: `probes/store/s3_hash_v{1,2,3}.vl`.
2. **`StoreSome::assume()` falls back to the value at the call, not the last value.** Patch a
   payload field through the live variant, then end the variant. The assumed handle reads
   (and its observer wakes with) the PRE-patch value: `after delete: held=hello` after
   `held=edited`. `when_live` hands its body exactly this handle (`browser/ui.vl:2419`), so a
   row whose message was edited and then deleted repaints the pre-edit text in the turn
   before it is torn down. The doc comment says "as it was when this was called", so this is
   to spec. It is the wrong spec for A153's amendment ("hold the last value"). Repro:
   `probes/store/s6_owner_rule_today.vl`.

(Noted, not defects: s7's identity-equality leaf, §9 item 4; s4's map field as a leaf, which
is A149 S3.)

## 11. Open questions, each with a recommendation

- **Q1. The wire's unit of demand.** Per-field slots, the whole root as one replica, or demand
  boundaries (grant bases, keyed children, key sets, collections leased whole) with subtree
  seeds. **Rec: boundaries** (§2.2–§2.3). Fields inside are seeded and never wait. Only
  boundaries wait, and a boundary is already a maybe in the type.
- **Q2. Addressing.** Absolute paths on every op, or client-named SLOTS with paths relative
  to the slot. **Rec: slots** (§3.3). Ops never carry key steps, so the server never
  describes a key outward. S3's `Key(Hash)` path could not, and the bytes are within 2 B.
- **Q3. Field steps.** Declaration index, or field name. **Rec: index**, with the shape in the
  contract hash (§3.4).
- **Q4. Channels.** One per `[rpc]` call (today's dynamic channel), or one per store root per
  connection with GRANTS. **Rec: per root with grants** (§3.1, §4.4). One replica per root at
  the client; dedup by root identity.
- **Q5. The seed in the reply.** **Rec: yes.** The minting call is the first lease (A92), so
  the reply is the subscription. It saves a frame and half a round trip per root.
- **Q6. Op granularity.** The writer's path, a diff-split into per-leaf ops, or a
  per-connection shadow diff. **Rec: the writer's path** (§4.1), with the value read at flush.
  Diff-split is S6, on a measured need. The shadow diff is declined: it holds a copy of every
  subtree per connection.
- **Q7. Coalescing.** **Rec: one `Patch` per root channel per turn**, last value per path, an
  ancestor's op superseding its descendants'. One `Subscribe` per turn upward (§5).
- **Q8. The client face.** `Store<T>` with writes refused at run time, a writable replica
  whose writes are overwritten by the next patch, or a read-only `RemoteStore<T>` /
  `RemoteStoreSome<P>` with derive-written projections. **Rec: the read-only face** (§6.1).
- **Q9. Client writes through the mirror.** **Rec: none.** Mutation stays an explicit
  `[rpc]`, authorized as any call is. Optimistic local writes would be a later paper
  (`optimistic-lifecycle.md`'s territory).
- **Q10. The root's type at the client.** **Rec: always a maybe** (`RemoteStoreSome<T>`), even
  for a `Store<T>` return. It has nothing until its seed (§6.1).
- **Q11. What a field inside a disposed scope reads.** **Rec: its LAST value.** `assume()`
  refreshes its fallback on every read through the live variant (find 2), on the local store
  too.
- **Q12. Authorization.** **Rec: the capability is the grant.** A `Subscribe` outside every
  grant is dropped; there is no per-field redaction attribute; a secret field means a split
  type (§4.3).
- **Q13. Back-pressure.** **Rec: none in S1.** Dirty-slot coalescing under a high-water mark
  is a later slice (§5), after `std::ws` can read its buffered amount.
- **Q14. The contract hash and fields, beyond stores** (find 1). **Rec: render every Wire
  struct's and enum's shape** into the template, not only a store's. It is BREAKING once:
  every service's hash moves, and client and server must be rebuilt together, which a
  deploy already does.
- **Q15. The existing handle returns.** **Rec: keep them.** `SignalCell`, `MemoCell`,
  `HashMapEntry` and `KeyedCell` returns stay as they are, and the store is additive. kolt
  moves at its owner's pace.

## 12. Slices

| Slice | Content | Size | Needs |
|---|---|---|---|
| S0 | The contract hash renders Wire and Storable shapes (find 1, Q14; BREAKING: every hash moves once). `assume()` holds the last value (find 2, Q11). Pins for both | S | — |
| S1 | Server half: `handle_element` learns `Store`/`StoreSome`; `reply_store` (root channel, grants, seed in the reply, base slot); `Subscribe`/`Unsubscribe` with `(slot, path)` lists and the grant check; boundary slot forwards over the root's op log at the writer's granularity; per-turn coalescing; `Seed`/`Set`/`Gone`; the derive's `store_describe_at`/`store_apply_at` | L | A149 S3 (keyed children, `StoreStep`); S0 |
| S2 | Client half: `RemoteStore<T>`/`RemoteStoreSome<P>` and their derive-written projections; the replica; leases aggregated to boundary slots; per-turn `Subscribe`; `states()`; `when_live` and `when_all_some` over remote handles | M–L | S1; A150 (`states()`); A152 |
| S3 | Collections over the wire: `Seq` (Splice with counts), key-set slots and `Keys`, whole-collection leases (`each_by` over a remote map) | M | S1, S2; A149 S3's `SeqOp`/`MapOp` on the store |
| S4 | Reconnect: root replay, one coalesced re-subscribe, comparing re-seed, `Refreshing` while down | S–M | S2 |
| S5 | kolt exhibit (§8) as a patch the owner applies | S | S2, S3 |
| S6 | On a measured need: diff-split ops for whole writes; back-pressure by dirty slots | M | S1; `std::ws` buffered amount |

Only S0 is breaking. The rest is new surface beside the existing handle returns (Q15).

## Appendix A. Probes

| Probe | What it shows |
|---|---|
| `s1_today_traffic.vl` | today's frames and bytes for kolt's open, rename, edit and same-value write (§1.1) |
| `s2_store_wire_bytes.vl` | the proposed frames' lengths under today's JSON codec, absolute and slot-addressed, per-slot and coalesced (§3.5) |
| `s3_hash_v1.vl`, `s3_hash_v2.vl`, `s3_hash_v3.vl` | the contract hash ignores fields (find 1) |
| `s4_map_field_is_a_leaf.vl`, `s4b_no_at.vl` | a map field is a leaf on 0.43.0; one key's write wakes all 50 observers |
| `s5_rpc_store_return.vl` | an `[rpc]` returning `Store`/`StoreSome` is refused as not Wire |
| `s6_owner_rule_today.vl` | the owner's rule in the local store's types; `assume()`'s fallback (find 2); shared identities |
| `s7_identity_eq_leaf.vl` | an identity `PartialEq` leaf swallows an edit |

The in-process pair delivers inline (A133), so s1 counts frames and bytes exactly but cannot
time a round trip. The round-trip depths in §1.1 and §3.5 are read off the frame order.
