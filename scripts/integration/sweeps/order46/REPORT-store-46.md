## store-46 report (the REPORT file write was refused, so the full text is below for the integrator to save as `sweeps/order46/REPORT-store-46.md`)

**Branch `store-46` @ `358eba5c`**: one commit on `origin/next` @c3da9fa3, not pushed. Worktree: `vilan/.claude/worktrees/store-46`.

### FIRST: I committed to the real kolt checkout by mistake — the owner needs to undo it
- **What happened:** while copying kolt to scratch, `rsync` was missing and the `&&` chain broke. The commands meant for the scratch copy ran inside `/home/reed/code/kolt`.
- **Result:** commit **`f3171d1` "reactive-46 patches"** (author `lane <x@y>`) now sits on top of `4e7e8d1`.
  - It holds exactly the owner's 8 previously-uncommitted files: channel, command_palette, lib/input_system, login_page, sidebar, store, theme, views (12 insertions).
  - The working-tree contents are unchanged, and no patch was applied there.
- **I could not undo it:** I tried `git reset 4e7e8d1` and the permission layer refused it, so I left it.
- **To undo:** `git -C /home/reed/code/kolt reset 4e7e8d1`. HEAD and the index go back, and the 8 files return as uncommitted edits.
- Every later kolt step used a scratch copy made with `cp` and absolute paths.

### One line per step
1. **A149 S3: DONE (`358eba5c`).** Map, set and list fields are keyed and sequence nodes. The store's core moved to `std::store_core`.
2. **A149 S6: DONE.** The patch is `sweeps/order46/store-46/kolt-a149-s6-store-exhibits.patch`, verified on a scratch copy.
3. **A149 S4: STOPPED.** It does not fit cleanly; reasons below.

### S3 as built
```vilan
global.channels().at(7)                          // Store<Option<Channel>>: wakes for key 7 only
global.channels().at(7).some().name().patch("x")
global.channels().at(7).some().messages().push(70)   // StoreSome<List<_>> has the SequenceCell writes
global.channels().insert(8, c); .remove(8); .len()
global.tags().contains("red")                    // Store<bool>; set(true/false), insert/remove
global.log().by_key(3)                           // Store<Option<Message>>; no at(index) (Q11)
global.log().push(m); .splice(..); .remove_at(i) // in place
global.channels().keys().memo_global(); global.log().map(..); each_by(global.log(), ..)   // ops, not diffs
```
- **Paths:** a path is now `List<StoreStep { Field(usize), Key(Hash) }>`. `StoreNode` gains `keyed` (children by key hash) and `feeds`.
- **Diffs:**
  - `HashMap<K, V: Storable>`: each watched key's child is diffed exactly. Other keys are compared only when an answer is needed: a whole-value slot above (stops at the first difference), or an open feed (every key). Maps are never compared with `==`.
  - `HashSet` works the same way with flags.
  - `List<T>`: `reconcile_to`'s prefix/suffix gives one span. `by_key` children are re-diffed only for keys carried by that span.
- **Write order:** `write_at` now diffs in a read pass (lend), lets touched feeds read, assigns (modify), lets the feeds read again, then wakes. Sequence writes go through `splice_at`, in place; this uses delta.vl's `splice_*` helpers, now exported as `[internal]`.
- **Deviation for the owner — flows instead of `MapSource`/`CollSource`:**
  - store-45's plan said "a lazily made `DeltaLog<MapOp>` per watched field so the handle is a `MapSource`". That can't be built: a `DeltaSource` must answer `since(cursor)` from any copy of the handle, but the uniform, untyped node cannot hold a typed log, and vilan has no type erasure to recover one.
  - So the collection handles implement `MapFlow`, `SetFlow`, `CollFlow` and `RowFeed` directly. Each `open()` makes its own log and stands a feed (`StoreFeed`: touch/before/after closures) on the node until release.
  - The write tells the feed which key or span it touched. The feed reads that part before and after, so each op carries what left and what arrived without copying the collection.
  - A `Whole` touch (variant switch, coarse write), or a list write that touched two places, is recorded as `Reset`.
  - Every map/set/sequence operator and `each_by` takes these handles. Code that bounds on `MapSource`/`CollSource` does not.
- **Extra surface:**
  - `insert`/`remove` on map and set handles (sugar), and `len()` on both.
  - `at`, `contains`, `by_key` and the sequence writes also exist on `StoreSome`, following the patch rule.
  - Flows exist on `Store` only.
- **Signature change:** `Storable::store_diff`'s last parameter is now `&mut StoreWoken` instead of `&mut List<StoreSlot>`. The derive writes it; a hand-written impl must change. The CHANGELOG family is `feature`; `breaking` is the owner's call.
- **`std::store_core`** (new file) holds the handle types, slot tree, write engine, leaf tiers and `Option`. `std::store` re-exports it and adds the collections and the derive.
  - Both `ui.vl` twins now import `store_core` (one line each).
  - Why: `when_live` made every web program load `store.vl`. With the collection layer inside it, that cost +134 M instructions (+9%) on example:browser. After the split it costs +14 M (+1.0%).
- **Derive output now imports from `std::store_core`:**
  - Through `std::store`, a non-entry module that is the first to load it resolved the module's own `Storable` macro and was refused with "'Storable' is not a trait". kolt's `account.vl` hit this.
  - This case is pinned. The general hole for hand-written impls is filed as B?4.
- **Known cost:** a `by_key` read scans the list.

### Pins
- **`inference::store::a149_s3_*` (8),** red on base except the refusal pin.
- **Wake counts for one key's write:**

  | Write | Who wakes |
  |---|---|
  | `at(3).some().name().patch` | k3=1 map=1 name3=1 (k1, k2, k4–k6 and tags: 0) |
  | `at(3).some().messages().push` | k3=1 map=1 |
  | `at(3).set` to the value already held | nothing |
  | `insert(4)` | k4=1 map=1 |
  | `insert(9)`, an unwatched key | map=1 |
  | `remove(5)` | k5=1 map=1; a second `remove(5)` wakes nothing |
  | whole map with only key 2 changed | k2=1 map=1 |
  | whole map unchanged | nothing |
  | root write changing only the set | tags=1 |

- **The other S3 pins cover:**
  - keyed-slot lifetime;
  - map-flow ops (handle writes, whole write, root write, unchanged, release, `keys()` memo);
  - set wakes and ops;
  - `by_key` wakes only its element, and a same-elements splice wakes nothing;
  - list-flow Splice/SetAt, with an operator mapping one element per push;
  - no `at(index)`;
  - collections through an `Option`.
- **`module_resolution::a149_s3_a_storable_derive_in_an_imported_module_resolves_and_keys_its_map`** (proven red with the old header).
- **`native_differential::a149_s3_collection_fields_build_and_wake_the_same_on_both_backends`** (`tests/native/store_collections.vl`).

### Native backend
- Takes every S3 shape with identical output, in both modes.
- Three std sites bind before a `match` to work around F?1, each with a comment.

### Goldens and censuses
- **Corpus:** no golden moved.
- **Shared census:** `store.vl` 3 → `store_core.vl` 4 (+1 for a keyed node's table). Feeds use captured `mut` bindings, so `store.vl` mints no cells. Total 196 → 197.
- **mdBook anchor golden:** +1 for the store.md "Collections" heading.
- **Ledger:** no new rows.

### Instructions and RSS: kolt `vilan check`
Scratch copy of kolt plus reactive-46's two patches; release build; `VILAN_SEQUENTIAL_CHECK=1`; warm. "Base" is the same binary over origin/next's std files (no Rust changed in this lane).

| Run | Instructions | Peak RSS |
|---|---|---|
| Base | 25,597,743,851 | 203.9 MB |
| Tip, kolt unchanged | 25,637,535,074 (+0.15%) | 203.6 MB |
| Tip, kolt with the S6 patch | 27,942,904,690 (+9.2%) | 203.1 MB |

- Of the adoption cost, the client's `Account` is +0.56 G and the server store is +2.11 G.
- `--explain-cost` work units don't explain it, so I filed it as M?5.

### Perf gate, reference class (this machine), tip vs base
- **Instructions, base → tip (M):**

  | Example | Base | Tip | Change |
  |---|---|---|---|
  | browser | 1475 | 1489 | +1.0% |
  | router | 1890 | 1907 | +0.9% |
  | ssr | 4145 | 4182 | +0.9% |
  | genapp | 9891 | 9928 | +0.4% |

  The other examples moved by a similar or smaller amount.
- **RED:** reactive-ui ×1.077, todo ×1.028, walkthrough ×1.032. All three were already red on the base (×1.068, ×1.021, ×1.026); they are not this lane's.
- Before the split, five more rows had gone red.
- No ceiling was edited. `ci-local.sh perf` (class `local`) is green; growth ×1.938.

### The kolt patch (S6)
It applies after reactive-46's message-row and model-states patches.
- **`account.vl`:** `[derive(Storable)] struct Account { fullname, username, nickname, channels: List<u53> }`, with `stub(): Store<Account>` and `impl Store<Account> { fun join_channel }` doing a push.
- **Callers:** `app_context.vl` uses `Context<Store<Account>>`; `channel.vl` calls `get_user().join_channel(id)`.
- **`store.vl`:** derived `ChannelRecord { id, name, messages }` and `Global { channels, messages }` live in one `Store<Global>`, and every rpc body writes through handles.
- **Rpc return types:** these stay wire handles, because a `Store` cannot cross the wire until A153.
  - `get_message` returns `MemoCell<Option<Message>>`, which keeps HashMapEntry's contract.
  - `get_channel_name` and `get_messages` return `Option<MemoCell<..>>` (they were `Option<SignalCell<..>>`).
  - Each is sealed once per key in a `Memo`; A153 removes these caches.
- **`shared.vl`:** `Message` derives `Storable, Wire`, so its identity `PartialEq` cannot swallow a content edit.
- **Verified with the tip compiler:** `vilan check` gives 0 errors and 0 warnings, both legs build, `fmt --check` is clean, and the server answers 200.
  - The rpc store expressions also ran on both backends in a standalone probe.
  - The browser runtime is not verified; kolt's e2e stub problem predates this order.

### S4: stopped
1. **Design conflict.** `Store`, `StoreSome` and `StoreFlag` have real fields (`root`, `path`, `lend`, `modify`, `gate`, `read`). A tier placed "after fields and methods" would make `app.path` silently read the handle's internal path whenever a struct has a `path` field. This needs a ruling: either Q9 also reserves these names, or `[internal]` fields stop resolving as members outside std.
2. **Placement.** The rule belongs in `analyzer.rs` `resolve_field_accessor`'s `None` arm. It would rewrite a field accessor into a method call mid-solve, but field accessors resolve before method calls. That is new constraint plumbing in the member-resolution code solver-c-46 is changing, plus completion and hover in vilan-ide.

### What comes next
- **S4:** the ruling above, then the tier, hover and completion.
- **Mirror (A153):**
  - Paths are already step lists by field index and key hash, with slots per path and feeds per open flow.
  - A wire forward can therefore be a feed, which matches mirrored-store §4.1.
  - `store_describe_at` and `store_apply_at` would sit beside `store_diff` in the derive.
- **S5:** unchanged.
- **Still owed from A149:** `store_opaque` can go (B508 is fixed on next), and the B509 write-back.

### Gates on tip 358eba5c (base c3da9fa3)

| Gate | Result |
|---|---|
| `cargo nextest run --workspace -j 6` | 9586 run, 9584 passed, 2 failed |
| The 2 failures | Both the mdBook anchor golden (my new heading); regenerated, both re-run green |
| `native_differential`, `VILAN_NATIVE_DIFFERENTIAL=1` | 158/158 |
| clippy `-D warnings` | clean |
| `cargo fmt --check` | clean |
| `ci-local.sh vilan-fmt` | green |
| `ci-local.sh wasm` | green |
| `ci-local.sh perf` | green |

### New finds
Filed in `newitems46-store.json`; repros are in `sweeps/order46/store-46/finds/`.
- **F?1:** natively, a `match` on an indexed non-Copy element moves out of the list (rustc E0507).
- **F?2:** natively, `shared.write()[i] += 1` aborts. It is F83's indexed twin.
- **E?3:** the formatter declines `a + match {..}`, and names the wrong line in a larger file.
- **B?4:** a hand-written `impl X with Storable` in a non-entry module, reached through the re-exporting `std::store`, is refused with "'Storable' is not a trait".
- **M?5:** kolt's check costs +9% once it adopts the store (S6).

### Needs the owner's ruling
1. kolt's accidental commit `f3171d1` (see the top of this report).
2. S4's internal-field shadowing: reserve the names, or hide internal fields.
3. Whether the `store_diff` parameter change is `feature` or `breaking` for R-f.
4. Flows instead of `MapSource`/`CollSource` on the collection handles.
5. Whether kolt takes the S6 patch at +9% check instructions.
