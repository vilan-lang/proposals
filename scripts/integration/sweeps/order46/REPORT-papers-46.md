# papers-46: A153, B495 and B509 papers written, six new finds

I wrote the three papers to proposals and changed no tree (vilan, kolt and the website are untouched). I ran no cargo, so no native program was built or run. The native rows are the emitted Rust (`vilan build --backend rust --stdout`), read only. My write of `sweeps/order46/REPORT-papers-46.md` was refused ("subagents return findings as text"), so the report is this message.

**Papers:**
- `/home/reed/code/vilan-lang/proposals/projects/vilan/proposal/mirrored-store.md` (A153, 768 lines)
- `/home/reed/code/vilan-lang/proposals/projects/vilan/proposal/closure-type-views.md` (B495, 283 lines)
- `/home/reed/code/vilan-lang/proposals/projects/vilan/proposal/payload-views.md` (B509, 320 lines)

**Also written:**
- Probes: `/home/reed/code/vilan-lang/proposals/scripts/integration/sweeps/order46/papers-46/probes/{store,views,payload}/`.
- `probes/run_all.sh` regenerates `probes/run_all.out` (45 sections, captured on 0.43.0).
- New items: `/home/reed/code/vilan-lang/proposals/scripts/integration/sweeps/order46/newitems46-papers.json`, six items in `file_items.py` shape (B?1–B?5, M?1). Nothing was written to the tracker.

## A153: the mirrored `Store`

**Today, measured (s1).** I rebuilt kolt's service in a probe and counted both legs.
- Opening a channel with 50 messages leases 55 handles. Each costs 4 frames: rpc request, rpc reply with a channel id, `Subscribe`, then the seed `Update`.
- Total: **220 frames / 9,598 B**, six round trips deep before the authors' names paint.
- A rename push is 34 B. An edit re-sends the whole message, 92 B.
- Writing the same value again re-sends it and reruns the client's observer.

**Projected for the store (s2).** The bytes are real: each proposed frame was built with today's JSON codec.
- The same open is **108 frames / 7,483 B** at one frame per slot, or **8 frames / 5,583 B** coalesced per turn, three round trips deep.
- The rename push is 51 B, which is 17 B more than today's split surface.
- The edit push is 65 B and carries only `content`.
- A same-value write pushes nothing.

**Headline recommendation:**
- One channel per store root per connection, with grants for the paths the rpcs handed out.
- The first value (the seed) rides in the rpc reply.
- Subscriptions happen only at demand boundaries: the root you were handed, each `at(k)` keyed child, and each key set. A boundary's seed carries everything beneath it, so a field reached through its parent is seeded and needs no maybe; only boundaries wait. That is the owner's rule plus the amendment, and it falls out of the local store's existing `StoreSome`/`assume()` types.
- Patches are addressed by client-named slot plus a field-index path, at the granularity the server wrote, and coalesced per root per turn.
- The client sees a read-only `RemoteStore`/`RemoteStoreSome`, whose root is always a maybe.
- The contract hash covers type shapes.
- Reconnect re-subscribes in one frame, and re-seeds compare, so only what changed during the outage wakes.
- The kolt exhibit (§8): `model.vl` loses `transient_of`, `map_state` and the per-field stubs.

**Questions for the owner (Q1–Q15), each with my recommendation:**
1. Unit of demand: boundaries.
2. Addressing: client-named slots with relative paths.
3. Field steps: declaration index, with the shape in the hash.
4. Channels: one per root, with grants.
5. Seed in the reply: yes.
6. Op granularity: the writer's path; per-leaf splitting only on a measured need; no per-connection shadow diff.
7. Coalescing: one `Patch` down and one `Subscribe` up per turn.
8. Client face: read-only `RemoteStore`/`RemoteStoreSome`, with projections written by the derive.
9. Client writes through the mirror: none; mutation stays rpcs.
10. Root type at the client: always a maybe.
11. A field inside a scope being disposed reads its LAST value (fixes B?2).
12. Authorization: the grant is the capability; no per-field redaction; split the type instead.
13. Back-pressure: none in S1.
14. The hash covers every Wire type's shape, not just stores. Breaking once (B?1).
15. Keep the existing handle returns; the store is additive.

**Slices:**
- **S0:** the hash and the `assume()` fix. Breaking.
- **S1:** the server half. Needs A149 S3.
- **S2:** the client half.
- **S3:** collections over the wire.
- **S4:** reconnect.
- **S5:** the kolt patch.
- **S6:** later, on measured need.

## B495: views in closure types

The views live in a side table keyed by the type id of the annotation as written. Types are not interned, and unification builds a fresh closure type, so any copy, unification or generic substitution loses them. The item framed the damage as native (F69). The probes show **silent JS miscompiles** too: the caller's internal place pair is stored as the value (`out=Oslo,0`) when:
- a let-bound closure is re-typed by an annotation (v1);
- it passes through a generic `hold<T>` (v3);
- an annotated `let` has a bare closure literal as its initializer (v7b), a position B465 says should work;
- a by-value closure is bound where the type takes a view (v2).

Also:
- `|str| void` and `|&str| void` are the same type.
- The `&mut` twin of v7 is falsely refused, and so is a bare literal stored in an `Option` (v4).
- Natively, a call through a match capture, a loop binding, or a generic struct's field passes a value where `Fn(&mut i32)` is expected, so rustc must refuse it (F69; the generic-struct-field case is new).

**Headline recommendation:** follow the B309 precedent. `Type::Closure` gains a fourth slot for parameter modes. An unwritten literal parameter adopts the mode during unification, which replaces the B465 pass and fixes v7's check-order problem. Two different written modes are refused (one new diagnostic row). The side table goes and F69 closes. The cost is mostly mechanical: about 69 match sites in the analyzer, about 10 doing real work, and 4 native reads that move to the type. Census: no annotated view-closure binding anywhere in std, kolt or the corpus; std has 40 view closure types, all receiving literals or same-typed values.

**Questions for the owner (Q1–Q5):**
1. Representation: modes in the type.
2. A written-mode mismatch: refuse with a quick fix; if S1's estate count isn't zero, warn for one release first.
3. Where adoption happens: inside unification.
4. Modes take part in type equality and hashing: yes.
5. A separate F69 stopgap: no; land the fix and close F69 with it.

## B509: payload views

The copy is real.
- The store derive's enum write step deep-clones the payload twice on both backends: once on the way out, once writing back a binding that is already dead.
- 2,000 writes on a 10,000-element payload take **420–470 ms** on JS, against 0–1 ms through a `&mut` lend.
- `Option`'s take-and-put-back step only moves, but the place holds `None` while the write runs, so a panic loses the payload.
- `match &mut held { Some(let p) => p.x = 2 }` already parses, but its capture is a copy, and the error tells you to add `mut`, which then compiles and silently drops the write (B?4).
- `Some(&mut let p)` is a parse error.

**Headline recommendation:** the match subject carries the mode, the same rule as `for e in &mut list`.
- `match &mut place` and `&mut place is V(let p)` bind `let` captures as writable views; `match &place` binds read views.
- A `mut` capture under a reference subject is refused.
- Rule 4 (no invalidating mutation under a live view) guards the subject until the capture's last use, and the same check closes the B?5 hole.
- Emission reuses the existing wrapped-view shapes on JS and Rust's binding modes natively.
- A bare `match held` keeps its copy semantics. There are zero `match &`/`match &mut` sites in std, kolt and the corpus, so nothing that compiles changes meaning.
- std's two `Option` write steps and the derive's single-payload enum step then write in place.

**Questions for the owner (Q1–Q7):**
1. Spelling: on the subject.
2. A subject that is already a view, written bare: stays a copy, as today.
3. Live range: to the last use.
4. `mut` capture under a reference subject: refuse.
5. Close the wrapped-capture hole in the same slice: yes.
6. Multi-payload variants in the derive: keep the copy for now.
7. `is`: same rule.

## Finds, in `newitems46-papers.json`

| Id | Find | Repro |
|---|---|---|
| B?1 | The contract hash ignores Wire struct fields: adding a field or reordering two leaves it at `b8fcf645`. Under the positional binary codec, a redeployed server passes the connect check and its clients mis-decode. The fix is breaking once. | `store/s3_hash_v{1,2,3}.vl` |
| B?2 | `StoreSome::assume()` (what `when_live` hands its body) falls back to the value at the call, not the last value. An edit then a delete repaints the pre-edit text. | `store/s6_owner_rule_today.vl` |
| B?3 | An annotated `let` with a bare closure literal doesn't pick up the annotation's views: a JS miscompile, and a false refusal for `&mut`. Root cause is B495. | `views/v7b_let_literal_read.vl`, `views/v7_let_literal_adopt.vl` |
| B?4 | The `match &mut` capture-write error steers to `mut`, which silently drops the write. | `payload/b2_match_ref_mut.vl`, `payload/b1_today.vl` |
| B?5 | **Unsound:** rule 4 doesn't guard a wrapped-view capture. The write is lost on JS; natively, rustc would refuse a program vilan accepted. | `payload/b9_wrapped_subject_write.vl` |
| M?1 | Writing back a dead `mut` capture deep-clones it on both backends. That is half of B509's cost. | `payload/b7_derive_shape_cost.vl` |

Noted but not filed:
- kolt's id-only `PartialEq` on `Message`/`User` makes a store leaf swallow edits (s7), so the exhibit derives `Storable` for them.
- B495's title should widen to "miscompiles on JS, refuses natively".
- F69 has a new shape: a call through a generic struct's closure field (v5).
