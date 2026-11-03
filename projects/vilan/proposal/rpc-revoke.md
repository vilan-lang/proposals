# Revoke by value: one connection's mirror of one store (A175, A174 door 1)

- status: PAPER 2026-11-03 (lane papers-56, Order 56; owner questions open; not built)
- item: A175 — `connection.revoke(store)` ends ONE connection's subscription to a
  store the service handed out, the client's mirror reading `Absent`, the wire open
- lineage: A174 door 2 (`Connection::close`, archive.md:2674), `mirrored-store.md`
  (A153: channels, grants, slots — §4.2-4.4, §6.2, §7), `transport-rpc.md` §9
  (sessions and channels). A page of its own: what is revoked is a mirrored-store
  channel (A153's), on transport-rpc.md's session, and neither paper owns both
  halves; the sweep may splice it as A120's §9.7 was.
- evidence: vilan `next` @ed9f0db9 (the integration worktree), kolt copy @0de9e2e

## 1. The problem

The only way an app takes back what it handed out is door 2: `Connection::close` /
`close_connection` (`vilan/std/src/rpc/server.vl:136-171`), which drops the whole
session. kolt calls it from three places, all through two helpers
(`close_connections_of`, `src/store.vl:5786-5790`; `close_session_connections`,
`:5794-5800`):

| site | why | door 1 instead? |
|---|---|---|
| `remove_member`, `store.vl:2118` | the removed user loses ONE organization | **yes** |
| `leave_organization`, `store.vl:2132` | the user leaves one; "its other devices too" | **yes** |
| `end_session`, `store.vl:5830` | signed out: the credential is dead | no — the close is right |

At the first two the client still holds its account store and every other
organization's; door 2 makes it reconnect, re-attach and re-seed all of them
(`mirrored-store.md` §7) for one store it lost.

## 2. What exists today

- **One channel per store root per connection, one grant per path.**
  `reply_store` (`vilan/std/src/rpc/mirror.vl:331-355`) finds the session
  (`session_of`, `vilan/std/src/rpc.vl:2324-2332`) and the channel
  (`mirror_channel`, `mirror.vl:223-268`: `store_identity_at(root, [])`,
  `store_core.vl:215-217`, then `session.controlled_channel_for(identity)`,
  `rpc.vl:2794-2802`, then `mirror_of`, `mirror.vl:213-220`), and adds a grant
  (`MirrorChannel::grant`, `mirror.vl:473-500`; `bases: HashMap<identity, base>`,
  `:191-192`, since M172).
- **Every release is client-driven.** An `Unsubscribe` releases slots and grants
  (`unsubscribe`, `mirror.vl:609-635`; `release_grant`, `:669-690`); the
  channel's last grant runs `session.revoke(channel)` (`rpc.vl:3165-3190`), whose
  control teardown is `MirrorChannel::teardown` (`mirror.vl:692-711`).
- **Premise correction: `ReactiveServer::revoke` tells the client nothing.** It
  disposes the forwards, drops the capability and runs the teardown
  (`rpc.vl:3165-3190`) — no frame. Called from app code today, the client's view
  would keep reading `Ready` with its last value, and its later `Subscribe`s on
  that channel would be dropped. Door 1 must SEND something.
- **The wire already has the word.** `Gone(slot)` — "the boundary is not
  reachable any more" (`mirror.vl:37`). A base slot is named on the client by its
  negative number (`adopt_base`, `mirror.vl:1181-1190`), so a `Gone` on a base
  lands at the base boundary's `gone` (`mirror.vl:1551-1563`), which is
  `replica.set(None)` (`:2038`), which `states()` reads as `Absent`
  (`mirror.vl:2132-2133`, `transient_of` `:2193-2202`). No new op, no client change for the read.
- **Premise correction 2:** kolt's `[rpc]`s do not refuse a non-member; they
  answer a shared empty store (`organization`, `store.vl:1830-1836` →
  `live.nowhere`; `private_channel`, `:4100-4108` → `live.nowhere_talk`;
  `edit_session`, `:2898-2901` → `live.no_session`). A re-ask after a revoke
  reads `Ready(empty)`, not a refusal — the app's choice, and fine.

## 3. The design

```vilan
export impl Connection {
	/// Stop mirroring `store`'s root to this connection: the client's handles on
	/// it read `Absent`, every other mirror keeps streaming, the wire stays open.
	/// Answers whether this connection had it.
	fun revoke<T>(self, store: Store<T>): bool { revoke_connection_store(self.id, store) }
}
export fun revoke_connection_store<T>(connection: i32, store: Store<T>): bool
// and the twin for StoreSome<P>
```

**The whole root (door 1a).** `session_of(connection)` (none: `false`); the
channel by `store_identity_at(store.root, [])` (none: `false`); then
`MirrorChannel::revoke_all`: a `Gone` for every slot in the channel's table —
bases and key slots, in stamp order — sent as ONE `Patch` through the flush path
(`flush`, `mirror.vl:714`, which already writes `Gone`, `:784-815`), then
`session.revoke(channel)`. A projected handle (`store.members()`) revokes the root
it stands on.

**When it lands.** On the next tick, as `close` does (`server.vl:157-171`): an
`[rpc]` that revokes and also returns the store answers first, so a reply
already written (after its route's turn, `mirror.vl:327-329`) reaches the client
before its `Gone`. The channel is resolved at landing: a grant made in the same
turn goes with it.

**The client.** Reads `Absent` with no change. One small change: a view whose base
was told `Gone` without releasing it marks its channel finished, so slots it
later releases do not wait in `retired` for the A169 acknowledgement
(`mirror.vl:1064-1068`) that a torn channel never sends.

**A later re-grant.** The next `[rpc]` that hands this store to this connection
finds no channel and opens a fresh one (`mirror.vl:225-268`) — a first grant,
fresh bases. The client re-asks when its holds return from zero (A92's re-mint)
or at a reconnect (`mirrored-store.md` §7), and the `[rpc]`'s own check decides
each time.

**The races.**

- *A revoke during a seed:* the next-tick landing orders it after the reply.
- *A store the connection never got:* a no-op answering `false`, as
  `close_connection` answers for no live connection (`server.vl:159-171`) — not a
  refusal: kolt's loop over a user's connections (`store.vl:5786-5790`) cannot
  know which of them got it.
- *A `Subscribe` in flight:* one frame names one channel (`mirror.vl:17`), so it is
  dropped whole with the capability; the client already has its `Gone`.
- *A revoke then a disconnect:* `drop_session` disposes the rest; idempotent.

**Per grant (door 1b), not recommended now.** Revoking one handle path (its base
from `bases`, a `Gone` for the base and its `under` slots, the channel kept)
meets a frame it cannot read: a `Subscribe` naming a base no grant has "drops the
rest of the frame" (`mirror.vl:550-556`, `:566-571`), because the steps are read
at the grant's type — so slots under OTHER grants later in that frame would never
be seeded. It needs a tombstone grant (walkers kept, answered `Gone`, forgotten at
the client's `Unsubscribe`). That is the M half.

**kolt, rewritten.** `remove_member` (`store.vl:2118`) and `leave_organization`
(`:2132`) revoke on each of the user's connections every root scoped to the
organization: its `OrgLive` store, each private channel's `Conversation`
(`private_live`; `publish_membership` already enumerates them, `store.vl:1693-1697`),
and each `CoSession` of it (`live.sessions`, `store.vl:826-827`). The price,
stated: a root it forgets keeps streaming, where door 2 could forget nothing.

## 4. The alternatives, and why not

- **Door 2 only** (today): correct and simple; the cost is the reconnect and
  re-seed of every other mirror, which is what A175 is for.
- **`ReactiveServer::revoke` exposed as-is:** silent to the client (§2); a handle
  would read stale `Ready` forever.
- **A new `Revoked(channel)` op:** the client would need a new arm; `Gone` per slot
  says the same with the arm that exists.
- **Plain `Source` channels too** (`expose_dynamic`, `rpc.vl:2675`): a plain
  channel has no `Gone` and a `RemoteSource` no `Absent` to land in; out of scope.

## 5. Recommendation and sizing

Build door 1a, **S–M**, not breaking (additive surface).

| file | what |
|---|---|
| `vilan/std/src/rpc/mirror.vl` | `revoke_all` (the `Gone` frame, then `session.revoke`); the client's finished-channel mark |
| `vilan/std/src/rpc/server.vl` | `Connection::revoke`, `revoke_connection_store` and the `StoreSome` twin, landing next tick |
| docs | `vilan/docs/std/rpc.md:584-586` (the surface) and `:614-625` (beside "Closing a connection") |
| pins (`service_layer`, beside `a174_*` at `service_layer.rs:1646`) | two stores on one connection, one revoked: it reads `Absent`, the other keeps patching; a re-hold re-asks and gets what the `[rpc]` answers; a never-handed store answers `false`; an `[rpc]` that revokes and returns the store: reply, then `Gone` |

## Questions for the owner

1. The whole root now, per grant (with its tombstone) on a shown need? Rec: yes —
   kolt's organization is a root.
2. A projected handle revokes the root it stands on (documented), rather than
   being refused? Rec: revoke the root.
3. A store the connection never got: `false`, a no-op? Rec: yes.
4. Land on the next tick, as `close` does? Rec: yes.
5. `Store`/`StoreSome` only, plain `Source` channels out? Rec: yes.
