## store-50 report

**Tip `dd9951eb`, branch `store-50`.** I started from `origin/next` @5fe24f86 and, as you asked, rebased onto 2b3fdf9d (tools-50 + native-50). Worktree: `vilan/.claude/worktrees/store-50`. Nothing is pushed.

The rebase had one conflict, in CHANGELOG: both sides created `## Unreleased`. I kept both sets of entries. After the rebase there are 19 bold heads and 19 family markers.

`LANE-STATUS.md` is current and untracked. No lane process is still running.

| commit | item | family |
|---|---|---|
| 50c8a764 | A153 S2's remainder | feature |
| 06c1265c | A153 S4, reconnect | feature |
| 10961087 | A168, plus a parked-boundary fix | feature + fix |
| 40e2cb56 | A153 S3, collections | feature |
| dd9951eb | A169 | fix |

**Gates on the rebased tip:**
- Full suite: **10,197 / 10,197 passed**, 31 skipped.
- `clippy -D warnings`, `cargo fmt --check`: clean.
- Native differential: pins mode green; sweep mode (`VILAN_NATIVE_DIFFERENTIAL=1`) green.
- Every item also passed its own targeted gate before its commit: reactive_channels, service_layer, rpc_http, transport_robustness, hmr_swap, ui_rows, shared_census, ci_ignored_pins, hygiene, check_scope_differential, docs, corpus, examples, delta_log, std_twin_parity, module_resolution, the native differential, and inference (the full binary at A168, the store subset otherwise).
- No corpus golden moved.

### Per item

**1. A153 S2's remainder: DONE.**
- **`states()`:** `RemoteStoreSome<P>` now implements `TransientSource<P, RpcError>`, so it has `state` (passive), `states`, `latest` and `is_pending`.
  - The states are `Pending`, `Ready`, `Absent`, `Refreshing` (a re-mint or re-subscribe in flight), and `Failed(error, last)`.
  - A failed mint that is asked again reads `Pending` or `Refreshing` while the call is out.
  - The mint tracks, per boundary, whether this binding has heard it. A handle's pipe follows only its own boundary's cell (`MirrorLink::follow`), so one key's seed doesn't wake every `states()`.
- **`when_remote_live`:** the second function, as ruled. It lives in a new module, `std::web::remote`, not in the ui twins: the face is in `std::reactive::store`, which a web program that mirrors nothing never loads.
- **`when_all_some`:** takes remote handles with no change.
- **Where the premise was wrong — a frame was never applied in one turn.** A closure writes in the turn it was created in, and a boundary's appliers are created long before the frame arrives. So every op of a Patch woke its observers separately; an observer reading two fields saw the new first field beside the old second. I fixed it in this commit:
  - `MirrorBoundary.apply` and `.gone` are now `context turn_scope`, so they write in the caller's turn.
  - The view lands each frame inside one `batch`.
  - A reply's seed, status and base land in one turn, and its re-holds go up as one `Subscribe`.
- **Pins:**
  - `reactive_channels::a153_s2_a_remote_handle_tells_pending_ready_absent_and_failed_through_states`
  - `ui_rows::a153_s2_when_remote_live_and_when_all_some_take_remote_handles`
  - `native_differential::a153_s2_a_patch_lands_in_one_client_turn_on_both_backends`
- **Not built natively:** `states()` hits two native-backend gaps, filed as B605 and B606 below, so the native probe leaves it out.

**2. A153 S4, reconnect: DONE.**
- **How the client learns of a drop:**
  - `SocketDuplex` gains `on_drop`, run by `handle_drop` when a live connection drops.
  - `dispose_on_close` registers `ReactiveClient::connection_lost` there. The generated `connect` text is unchanged, so no golden moved.
  - `replay_dynamic` marks the connection up again.
- **What a mint does:** while it holds a grant it enlists its replay and drop hooks on the client (`enlist_store`).
  - On a drop it kills the dead channel's view, so a stale channel id can't reach the fresh session, and its handles read `Refreshing`.
  - A hold taken while down waits for the replay. A key released while down still leaves the replica.
  - The replay re-issues each held root's call **once**, re-subscribes every live boundary in **one** `Subscribe`, and lands the re-seeds as comparing writes.
- **Where the premise was wrong — a reply's seed replaced the replica.** A seed carries its maps empty, so a rebind with live key slots would have wiped the held keys and woken everything. The seed now lands over the replica through `store_apply_at`, which keeps those keys (`landed_over`).
- **Deviation:** slot numbers restart on the fresh channel. The paper kept them, but nothing on either side depends on them.
- **The pin's shape** (`a153_s4_a_reconnect_replays_the_root_once_resubscribes_in_one_frame_and_reseeds_by_comparison`):
  - Connect and seed keys 7 and 8.
  - `client.connection_lost()`, then `drop_session(7)`: the root's and key 7's states read `Refreshing`.
  - While down, write the motd and key 7; leave key 8 alone; take a new hold on key 8.
  - `register_session(7, ..)` on the same wire, then `client.replay_dynamic()`. Exactly one `rpc global`, then one `Subscribe` on fresh channel 1 carrying both slots, then one Patch of Seeds.
  - Only "motd while down" and "seven edited" wake. Eight and the hold taken while down do not.
  - The fresh channel then follows a write, and the page's release lets it go.
- **Proved non-vacuous:** making the rebind set the seed whole turns the pin red (keys wiped, eight wakes).
- **Native pin:** `native_differential::a153_s4_a_mirrored_store_reconnects_the_same_on_both_backends`.

**3a. A168: DONE.**
- `impl HashSet<T: Hashable + Wire> with Wire`: a set crosses as the list of its members, in insertion order.
- It lives in `std::hash_set`, not beside the map's impl in `std::wire`: every program loads `std::wire`, and one that never names a set shouldn't load `std::hash_set` for it.
- `contains(member)` on a remote set is a boundary, on both `RemoteStore` and `RemoteStoreSome`.
- `StoreSome<HashSet<T>>` gains `insert` and `remove`.
- **Fix in the same commit:** a released boundary dropped its key from the replica even while a boundary inside it was still held. Releasing `rooms().at(1)` killed a still-watched `members().contains("amy")`. A released boundary is now parked while anything below it is held (`MirrorBoundary::place`).
- **Pins:** `reactive_channels::a168_a_set_field_crosses_the_wire_and_each_watched_member_is_a_boundary` and `native_differential::a168_a_mirrored_set_behaves_the_same_on_both_backends`.

**3b. A153 S3, collections: DONE, with two deviations.**
- **Lists:** the wire log now records a sequence write's splice beside its path (`WireWrite`). A forward composes one turn's splices on a list into one `Splice` in the list's pre-turn positions; the inserted elements are read at the flush. Any other write to that list still sends it whole as a `Set`.
- **Key sets:** any subscription that reaches a map or a set is a key-set slot. `keys()` answers a `RemoteStoreKeys<K>`, which is a `Source<List<K>>`.
- **Collections:** `each` over a remote map's keys, with each row on its own `at(k)` boundary, is how the map is leased as a collection.
- **Derive unchanged:** the list span and the key set ride the existing walkers as two internal wire steps that no subscription path can name.
- **Deviation 1:** key sets send only `Reset`. A `Delete` would need the key, and the server no longer has it.
- **Deviation 2:** no single whole-map boundary seeding every entry at once. Composing keys plus per-key rows costs one more round trip on the first paint.
- **Where the premise was wrong:** the S1 pin's `push` changes from a whole `Set` of the list to a `Seq`.
- **Pins:**
  - `reactive_channels::a153_s3_a_list_crosses_by_splices_and_a_key_set_by_keys`
  - `ui_rows::a153_s3_each_over_a_remote_maps_keys_builds_one_row_per_key_and_keeps_them`
  - `native_differential::a153_s3_mirrored_collections_cross_the_same_on_both_backends`

**4. A169: DONE (door (a)).**
- When a client slot's last hold is released, the server sends `Gone(slot)` in its next patch, after every op it sent for that slot. The client then forgets the reader.
- A `Gone` for a live slot still means the boundary is unreachable; the client tells the two apart by its own state.
- New census for pins: `mirror_retired_census`.
- Every existing mirror pin gained its acknowledgement lines. I reviewed each one; they are additions only.
- **Pins:** `reactive_channels::a169_the_server_acknowledges_an_unsubscribe_with_gone_and_the_client_forgets_the_reader` (1 retired reader while the `Gone` is in flight, 0 after) and `native_differential::a169_an_acknowledged_unsubscribe_is_the_same_on_both_backends`.

**5. A153 S5 + A149 S6, the kolt exhibit: DONE as a patch.**
- **Patch:** `sweeps/order50/store-50/kolt-mirror-v0.48.0.patch` (744 lines, `a/`/`b/` paths against `/home/reed/code/kolt`, dry-run applies clean). Kolt comments use plain hyphens, ASCII only; the changed files are `vilan fmt`-clean.
- **Files:**
  - `store.vl`: `ChannelRecord` and `Global` (now with `users`) derive Storable + Wire. The live surface is one `[rpc] global(): Store<Global>`, plus `account(): UserId`. The write rpcs are kept; the `get_*` stubs and memos are deleted.
  - `shared.vl`: `User` gains `Storable`.
  - `model.vl` follows §8.2: `Channel::find`/`ids`, `Message::find`, `User::find`, all over the mirror.
  - `channel.vl` follows §8.3: `when_remote_live` rows, the author through `switch`.
  - `views.vl`, `sidebar.vl`, `command_palette.vl` are moved off the old model API.
- **Verified** on a scratch copy (`target/store-50-scratch/kolt/work`, carrying lucide and search-dict) under the tip: `vilan check .` gives 0 diagnostics, and `vilan build .` builds both legs.
- **Run, both legs:** a harness (`sweeps/order50/store-50/kolt-traffic-harness/`) starts the built server, seeds two users, one channel and 50 messages over the raw protocol, then loads the real `client.js` under the shared DOM stub, deep-linked to the channel. It counts every WebSocket frame. Results were identical across repeated runs:

| scenario | before (kolt today) | after (mirror) |
|---|---|---|
| open the channel (50 messages, 2 authors), until the 50th row paints | 229 frames, 10,110 B | **13 frames, 6,228 B** |
| rename push | 1 frame, 34 B | 1 frame, 53 B (the paper predicted 51) |
| add a message (push + row) | 5 frames, 332 B | 3 frames, 194 B |

- **The open after the exhibit has the paper's shape:**
  - `global` reply `{"channels":[],"messages":[],"users":[]}`
  - one `Subscribe` for the key set and the channel, answered with `Keys(Reset([0]))` and the record's `Seed`
  - one `Subscribe` for the 50 message slots and its Patch of 50 Seeds
  - one `Subscribe` for the 2 users and their Seeds
  - the push afterwards is `{"Seq":[1,[1,2],{"Splice":[50,0,[50]]}]}`
- **A149 S5 (compiler-generated nodes): not built, no measured need.**
  - Kolt's own declarations get cheaper with the exhibit: server leg 24,357 → 21,495 work units, client leg 524,124 → 504,981.
  - The derive-written walkers are about 2,900 units of the server leg's 21,495.
  - Total inferences rise **+7.0%** (134,799 → 144,180) because std's `rpc::mirror` loads again once a service returns a `Store`. Filed as M136.

### Perf rows

`perf_gate measure`, instructions:u. Base is the 5fe24f86 release binary; tip is `dd9951eb`, which also contains the tools-50 and native-50 merges. All 14 rows are within −0.07% to +0.05%:
- browser +0.04%
- reactive-ui +0.05%
- ssr +0.04%
- walkthrough +0.04%
- rpc −0.07%
- the others ±0.03%

The web examples don't load the new code: the face and keys stay in `store.vl`, `when_remote_live` is in its own module, and the sets impl is in `hash_set`.

### Finds

In `sweeps/order50/newitems50-store.json` (it validates apart from the placeholder ids); repros under `sweeps/order50/store-50/finds/`:
- **B605:** a generic function that returns a `dyn Pipe<Option<P>>` built with `value.derive(..)` is refused natively ("unbound generic type parameter"). This is why `states()` doesn't build natively.
- **B606:** a `RemoteStoreSome` used as a `dyn Source` is refused natively (the `attach_observer` implementation takes 3 parameters, the declaration 5). This was already present at 5fe24f86.
- **M136:** the exhibit's +7% inference cost comes from std's mirror module, not kolt's code. Rec: answered by the std-prefix paper (R-f).

Shared census: the `rpc.vl` row goes 56→58, `rpc/mirror.vl` 25→31, total 223→231, each site classified in the table.

### Questions for the owner
1. **Where should `when_remote_live` live?** Rec: keep it in `std::web::remote`, so web programs that mirror nothing don't load the face. The alternative, beside `when_live` in the ui twins, puts the face in `store_core` for every web program.
2. **Key sets send only `Reset`.** Rec: accept, and add `Put`/`Delete` only on a measured need (a large key set leased by many clients).
3. **No single whole-map boundary;** `each` over `keys()` with per-key rows instead. Rec: accept; it costs one more round trip on the first paint.
4. **Slot numbers restart on the fresh channel after a reconnect.** Rec: accept.
5. **The kolt exhibit costs +7% inferences on kolt's check, all in std.** Rec: apply the patch at the seal, re-take E121's seven rows with it applied, and let R-f's persisted std prefix absorb the cost; don't build A149 S5.
6. **A turn's splices compose into one `Splice` that covers every edited span.** It is exact but not minimal: insert at 0, remove at 2 and push in one turn send the whole tail. Rec: leave it until measured.
