## store-49 report

**Branch `store-49`, tip `e11a473d`, base `origin/next` @445c9346.** Six commits, not pushed, no rebase (I saw that next is now at 92429f5a). Worktree: `vilan/.claude/worktrees/store-49`. After the session restart I found the S2 commit staged but not written: the WSL vsock error had failed `git commit`. That staged tree was the one the S2 gate had just passed 1214/1214, so I committed it as is (171a815f).

| commit | item |
|---|---|
| e54d1731 | A153 S1: the server half |
| 31afb43f | C15 option S (family: performance) |
| 73e9373d | A165 |
| 171a815f | A153 S2: the client half |
| e11a473d | A165's split-fixture golden (one byte: a std line number) |

**Full suite on the tip:** 9936 tests, 9935 passed. The one failure was `split::the_split_fixture_emits_its_pinned_artifacts`: A165's insertion moved a `ui.vl` panic location from line 2271 to 2320, and that was the only differing byte. I regenerated the golden by hand and the split binary is now 13/13. The full suite was not re-run after that, and 33 tests were skipped. Clippy (`-D warnings`) and both fmt legs are clean.

Every slice's targeted gate was green:
- **S1:** 777 tests. The one red was the Shared census row, which I classified and updated (now 222 total).
- **Option S:** 327 tests.
- **A165:** 601 tests.
- **S2:** 1214 tests, covering store and macro inference, reactive_channels, service_layer, the rpc binaries, `check_scope_differential`, `native_differential`, the censuses, twin parity, docs, the markdown golden, `ci_ignored_pins`, hygiene, corpus and examples.
- **Native corpus sweep:** run with `VILAN_NATIVE_DIFFERENTIAL=1` after S1, and green.

### Per item
**1. A149 S3: DONE before this order, so the premise was wrong.** store-46 built it (56e5a2ca, Order 46): `StoreStep { Field, Key }` paths, keyed nodes, map/set/list fields, and the flow handles ruled 2026-10-03. Nothing was left to build. The `store_opaque` remainder went in store-47, and B509's write-back is in place.

**2. A153 S1, the server half: DONE (e54d1731).** It lives in `std::rpc::mirror`.
- **Replies:** `reply_store` and `reply_store_some` open one channel per store root per connection (deduped by root identity) and add one grant per handle path (two replies at one path are one grant, held twice). The reply is `[channel, base, seed]`: the base slot is server-named and negative, and the seed is described after the route's turn settles.
- **Subscribe:** each entry is `[slot, base, [steps]]`, and the path is read at the GRANT's type. That makes the grant the capability: a flag step, an unknown base or a malformed key drops the rest of the frame.
- **Slots:** each slot is a counted store subscription at its boundary node.
- **Write log:** every write that changes something records its path in the root's wire log (a `DeltaLog`, made with the first mirror and dropped with the last).
- **Patches:** each settled turn sends ONE `Patch` of `Seed` / `Set` / `Gone` ops. A write at or above a boundary re-seeds it. Writes inside a boundary are `Set`s at their own paths, cut at the first key, with any write that another one covers dropped. A log that outran its ceiling re-seeds.
- **Teardown:** the last grant revokes the channel; teardown and session disposal leave no slot and no log.
- **Derive:** `[derive(Storable)]` now also writes `StoreWire` (describe at a path, apply at a path, read a subscription path, build a fresh value). The format is `Wire`'s own, except that a `HashMap`/`HashSet` inside a described value goes out EMPTY, because its keys are boundaries of their own.
- **std::rpc:** gains controlled channels (`open_controlled`, `ChannelControl`). `spine()` now takes its path as a view, so a store nobody mirrors pays +28 Ir per write natively.
- **Pins:** `inference::store::a153_s1_*` (4), `reactive_channels::a153_s1_*` (3), `native_differential::a153_s1_a_mirrored_store_sends_the_same_frames_on_both_backends`.
- **Where the premise was wrong:**
  - The paper's `Subscribe(channel, [(slot, path)])` cannot work as written. A handle's root type is erased, so a path has to be read relative to a GRANT. That is why entries carry the base.
  - A removed key re-seeds as `Seed(slot, null)`, its value at its own type. `Gone` is kept for a boundary that can no longer be reached at all.
  - A relpath keeps the `Some` step (`[1,2]`); the paper wrote `[2]`.

**One example exchange** (JSON; this is the probe output, pinned):
```
reply {"Success":[0,-1,{"rooms":[],"messages":[],"motd":"welcome"}]}
up    {"Subscribe":[0,[[0,-1,[0,0]],[1,-1,[1,8]]]]}
down  {"Patch":[0,[{"Seed":[0,{"id":0,"name":"general","messages":[7]}]},{"Seed":[1,{"id":8,"author":"amy","content":"ho"}]}]]}
down  {"Patch":[0,[{"Set":[-1,[2],"one turn"]},{"Set":[0,[1,1],"lounge"]},{"Set":[0,[1,2],[7,9]]},{"Set":[1,[1,2],"x"]},{"Set":[1,[1,1],"zed"]}]]}
down  {"Patch":[0,[{"Gone":-2}]]}
```

**3. C15 option S: DONE (31afb43f).** `write_at`'s three out-parameters are now one captured `Lent`. Measured with callgrind on C15's probe (20,000 `user.visits().set(n)`, native release build):

| build | Ir |
|---|---:|
| v0.46.0 base | 76,452,679 |
| with S1's write log | 77,010,288 |
| with option S | 71,007,268 |

That is −300 Ir per write (−7.8%) against S1, and −7.1% against the base. C15 predicted about 7%.

**4. A165: DONE (73e9373d + e11a473d).** `impl Option<type V: Slot> with Slot` is in both ui twins.
- **Premise wrong:** a `Source<Option<View>>` does NOT follow from any blanket. I added its own reactive arm, `impl type S: Flow<Option<View>> with Slot`. On the browser it uses a Region; the process twin reads it once.
- **Docs:** `guide/ui.md` and `std/browser.md` updated.
- **Parity:** `std_twin_parity` and `ssr_differential` are green.
- **Pins:** `ui_rows::a165_an_optional_child_places_its_view_or_nothing_and_its_source_follows`, `ui_rows::a165_the_process_twin_renders_an_optional_child_once`.

**5. A153 S2, the client half: PARTIAL (171a815f).** Built:
- **Replica and faces:** a replica (`Store<Option<T>>`) that frames land in as comparing writes, read through faces `RemoteStore<T>` / `RemoteStoreSome<P>` / `RemoteStoreFlag`. The derive writes their projections via `narrow`.
- **Boundaries:** a remote map's `at(k)` is a boundary. Its first hold sends the turn's one `Subscribe` (two handles share a slot); its last hold sends `Unsubscribe` and takes the key out of the replica.
- **Minting:** `mint_store` mints UNLEASED, as A92 does: the first hold issues the call, the last lets the grant go, and the replica keeps its last value and re-seeds by comparison. `origin_store` dedups per origin (A134).
- **Expansion and rpc:** the `[service]` expansion reads `Store<T>`/`StoreSome<P>` returns as handles (route replier, sync stub returning `RemoteStoreSome<T>`, contract surface with a `?` for the `StoreSome` form). `std::rpc` gains `call_reading`.
- **Pins:** `reactive_channels::a153_s2_a_store_mirror_mints_on_its_first_hold_and_patches_its_replica`, `native_differential::a153_s2_a_store_mirror_behaves_the_same_on_both_backends`, and `reactive_channels::a153_s2_a_generated_store_stub_mints_on_its_first_hold_and_lets_go_with_its_last` (ignored on A153).
- **Blocked on the analyzer (filed, did not touch the core):** the `[rpc]` spelling is still refused for two reasons:
  - The analyzer's element rule does not read the store's two spellings.
  - The loader never loads `std::rpc::mirror`; a macro's output cannot seed a module.
- **The patch:** `proposals/scripts/integration/sweeps/order49/store-49/a153-analyzer-admission.patch` (176 lines, rustfmt-clean, `git apply --check` clean). It touches two match arms, adds a `service_seeds` helper used at the five `contains_service` sites (the world key among them), and adds macros.rs's http rows. I verified it on a scratch build: the generated-stub program is green on both backends.
- **Not built:** `when_live` / `when_all_some` over remote handles, `states()`, reconnect (S4), key sets and `Seq` ops (S3).
- **What S3 starts from:**
  - Map/set fields are elided in seeds and become `Keys` ops on key-set slots.
  - Lists are sent whole as a `Set` today; that is where `Seq` slots in.
  - `HashSet` needs a `Wire` impl first.

**6. Kolt exhibit: NOT BUILT.** The `[rpc]` spelling does not compile on next until the patch lands, so a kolt patch could not be verified.

**Check-cost measurements** (debug binary, warm cache):

| program | change |
|---|---:|
| rpc example | +0.18% |
| browser example | −0.15% (noise) |
| C15 store probe (cold) | +0.5% |

### Finds
All are in `sweeps/order49/newitems49-store.json`, with repros under `store-49/finds/`.
- **A?1:** the analyzer half of A153 (the element rule and the loader seed), with the patch above. This lands in incr-49's world-key area.
- **B?2:** a static call on a concrete type that only a blanket answers (`str::tag(1)`) is refused with "cannot infer 'T'". The derive works around it with helper functions.
- **E?3:** E271's message does not mention `Option` now that A165 made it a child.
- **A?4:** `HashSet` has no `Wire` impl, so a struct with a set field cannot be mirrored (S3 needs it).
- **A?5:** the client keeps a released slot's reader until its channel view closes, because the codec cannot skip a value and there is no unsubscribe acknowledgement.

### Questions for the owner
1. **Who lands the A?1 patch?** Rec: the integrator applies it at an incr-49 checkpoint with incr-49 reviewing, since it touches the loader seeds and the world key. Then un-ignore the stub pin.
2. **Subscribe entries carry the base: `[slot, base, path]`.** Rec: accept this deviation from the paper; it is forced by the root type being erased at the handle.
3. **`Seed(slot, null)` for a removed key, `Gone` only for an unreachable boundary.** Rec: keep it.
4. **`when_live` over a remote handle.** Either give the current `when_live` a trait (its body's type then cannot be inferred without an annotation) or add a second function. Rec: a second function, `when_remote_live`, in S3's slice; until then users write `when(m.live(), || body(m.assume()))`.
5. **A?5's fix.** Rec: door (a), the server answers an `Unsubscribe` with `Gone(slot)`.
6. **Option S for `splice_at` (seven captured `mut`s).** Rec: take it next time a sequence write is on a hot path; measure first.

`LANE-STATUS.md` is current; no lane process is still running.
