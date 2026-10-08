# reactive-46 — final report

I couldn't write `REPORT-reactive-46.md` (the tool refused report files), so the full report is below for you to save.

**Branch `reactive-46` @ b580d696**: 12 commits on `origin/next` @38314319. I started off baccee32 and rebased once at the end, after syntax-b-46 merged. Nothing is pushed. Worktree: `vilan/.claude/worktrees/reactive-46`. All gates below are on the rebased tip unless a line says otherwise.

## One line per item
1. **A152: DONE** (699a140f; anchor golden in b580d696). `zip_some`, `when_all_some` on both ui twins, `SignalCell<(..)>::unzip`.
2. **A150: DONE** (bf53a4f4). `states()` leases the mirror; `state()` stays passive and its doc says so first. `TransientState` gains `map`, `and_then`, `zip`.
3. **B525 + B526: DONE** (ace0d396). The contract hash covers Wire shapes (**BREAKING**); `assume()` holds the last value read.
4. **A151: DONE** (1735e15e, goldens 7ed8addb). std's focus marker is `data-autofocus`.
5. **A155: DONE** (f6bfceb6). A warning names both writers when one element writes its class twice.
6. **B535: DONE** (8116f661). `Iterator` is in the base prelude; `CollPipe` and `SetPipe` are in the web prelude.
7. **R-e: DONE** (63a0b6f1, ledger 6160050e). `Map`/`Set` and the old short cell names are removed (**BREAKING**); the old names are refused with a steer.
8. **B480: NOT REPRODUCED** (12cff69a, a control pin). The kolt patch drops the explicit type arguments.
9. **F78: DONE** (0df43a2d; a pin re-aimed in b580d696). `Flow::on_change`/`sub` are defaults now, and the 26 per-stage copies are gone. Only one golden moved, so it was cheap.
10. **M60: NOT REACHED** (R-k carries it).

Every CHANGELOG entry is under `## Unreleased` with a family marker. B525 and R-e are marked `breaking`, A155 `diagnostics`, the rest `feature`.

## Item details

### 1. A152
- **`zip_some((a, b, ..))`** takes `(U in T: dyn Flow<Option<U>>)` and returns `ZipSome<T>`, a `Pipe<Option<T>>`. It holds no state and needs no owner.
  - It uses `combine`'s mapped-tuple mechanism.
  - Unlike `combine`, its inputs are flows rather than sources, so a mirror's `.latest()` pipe goes in directly.
- **`when_all_some`** is `when_some(zip_some(flows), |whole| render(whole.unzip()))` on both twins.
  - The cells are created under the body's owner.
  - They are written in place while every input stays `Some`.
  - They are released when any input goes `None`.
- **`unzip`** works like `.cell()`: it registers with the owner and refreshes as a derivation. Its body lives in a free function (`unzip_cell`) because of solver find B?1.
- **Pins:**
  - `tuples::a152_*` ×4.
  - `ui_rows::a152_when_all_some_updates_its_cells_in_place_and_releases_on_none`: same row node across payload changes, 2 builds and 2 releases over 5 transitions.
  - `ui_rows::a152_the_ssr_twin_renders_an_all_some_body_once_and_omits_a_none`.
  - `native_differential::zip_some_and_unzip_are_never_a_different_answer_natively`. The native backend refuses any mapped tuple by name, as it already does for `combine`.
- **Docs:** reactive, browser and ui pages.

### 2. A150
- `states()` is now a requirement on `TransientSource`. A hand-written implementor must add it; std has none outside its own three.
  - On a mirror it has the same shape as `latest()` but keeps every arm.
- `and_then` on a `Refreshing(v)`: a `Ready` or `Refreshing` from `next(v)` reads `Refreshing`, a `Pending` or `Absent` reads `Pending`, and a `Failed` stands.
- `zip` precedence when the two states differ: `Failed` > `Absent` > `Pending` > `Refreshing`.
- **Pins:**
  - `reactive_channels::a150_states_leases_a_mirror_and_state_stays_a_passive_report`, over a real socket: the passive report stays `Pending`, while `states()` alone reads `Ready` and `Absent`.
  - `std_surface::a150_*` ×3, every arm.

### 3. B525 + B526
- **B525:** a struct or enum declared outside std is now written into the hash as its shape the first time a surface reaches it: fields in order with resolved types, recursively, plus enum variants with payloads and backing values. After that it is written by name, which also ends recursion.
  - std types stand for themselves.
  - The papers-46 probes now give three different hashes; on 0.43.0 all three were `b8fcf645`.
- **B526:** the `assume()` fallback is refreshed on every read through the live variant.
  - The browser pin was planted back on the old `store.vl` and went red: it read `laptop` in the turn that ended the variant.
- **Pins:** `traits::b525_*` ×2, `store::b526_*` ×2, and `source_bindings::b526_a_when_live_body_reads_the_last_payload_as_its_variant_ends`.
- **One shipped pin changed with the rule:** `a142_s7_a_payload_store_assumed_reads_the_last_payload_once_the_variant_ends` now expects `phone`.
- **How far the hash change reaches:**
  - Every service whose surface reaches one of its own structs or enums moves once.
  - Services over scalars and std types keep their hash (A144's `7edcd9bc`, the factory's `d1d5fba0`). No corpus golden carries a hash.
  - Three frozen values in `service_layer` were updated with a note, each checked against djb2 of the expected surface:
    - `78bdada7` → `ddcd4de6`
    - `43077e29` → `b034cc03`
    - `d093c571` → `9f8b135b`
  - kolt's hash moves too. Both legs rebuild together, so no patch is needed.

### 4. A151
- `View::autofocus` writes `data-autofocus`.
- `focus_initial` focuses the first descendant carrying either `[data-autofocus]` or a native `[autofocus]`.
- Element syntax stays name-blind: the browser `View::attr` writes the one name `autofocus` as `data-autofocus`. So kolt's six element-syntax sites get the fix with no source change.
- **The server `attr` now DROPS `autofocus`**, the same as server `View::autofocus`. This is a behaviour change: `<input autofocus />` used to serve the native attribute. See owner question 2.
- The A121 §6.1 comment in std is corrected. I did not edit the proposal paper.
- **Goldens moved:** `element-syntax.mjs` and `ssr-render.mjs` (both runtime-identical), plus the split fixture's 4 artifacts (temporaries renumbered).
- **Pins:** `ui_rows::a151_autofocus_writes_data_autofocus_and_a_scope_honours_a_native_one`; the two A121 pins were updated.

### 5. A155
- A post-build pass, `check_class_written_twice`, walks each element's chain of dotted std `View` calls.
  - Writers: `class`, `styled`, `bind_class`, `bind_styled`, `attr("class", ..)`.
  - It warns at the writer that wins and names both writers.
  - It skips std, dependencies and generated code.
- Zero sites warn in std, the corpus, the examples or kolt.
- **Pins:** `styling::a155_*` ×2.
- One `NEW` ledger row.

### 6. B535
- **B515 sites in the docs, re-counted on my base:** 27 sites in 10 fences before; 12 sites in 6 fences after.
  - None of the 12 is an iterator chain: `Debug`, `Display` ×4, `Ord`, `Flow`/`Disposable`, and the sealers ×3. The sealers still count because the book compiles under the base prelude.
- **Corpus:** 5 sites, all `PartialEq`/`Ord`/`PartialOrd`.
- All 17 sites now import their traits. No corpus golden moved.
- The docs gate now fails on this warning.
- **Pins:** `module_resolution::b535_*` ×2, plus the web-surface pin.

### 7. R-e
- `map.vl` and `set.vl` are deleted.
- Removed with them:
  - the `macro_std` re-exports
  - the `Map` cases in `is_hash_map_head` and in rpc.vl's expose expansion
  - bindgen's reserved `Map` and `Set` names
- The formatter fixed-point test now reads `hash_set.vl`.
- **std never had a `MapCell`/`SetCell` alias.** A148 renamed them before release. The refusals cover them anyway, from one table: nine renamed names and four removed modules. The steer appears both on an import-segment miss and on a bare-name miss.
- **Pins:** `std_surface::r_e_*` ×3, replacing I9's alias pins. `a144` drops its `Map` spelling; `modules::b472` now reads R-e's steer.
- Five `NEW` ledger rows.

### 9. F78
- One golden moved: `dyn-objects.mjs`, 23,317 → 23,994 B, runtime-identical.
- Native copy census: 35/67 → 33/57. Native leak census: 12 → 10 minted, 0 live.
- `platform::b249` now names `start` (`Instance<i32>`). The closure case moved to a trait of its own, which exposed E?5.

## Kolt patches
Both are in `sweeps/order46/reactive-46/`; kolt itself is untouched.
- **`kolt-a152-message-row.patch`** (`channel.vl`): the row is `when_all_some((message, author), |(message, author)| ..)`, with `author = message.derive(..author).distinct().and_then(..user())`.
  - The row now waits for its author instead of showing an empty name first. That is the ruled design, but users will see it.
- **`kolt-a150-model-states.patch`** (`model.vl`): `transient_of` and `map_state` are gone, replaced by `.states()`, `TransientState::map` and `and_then`. `switch` loses its type arguments and the B480 FIXME.

**How I verified them:**
- `git apply --check` passes against kolt's working tree (including your uncommitted edits).
- On a scratch copy with both applied, the tip release binary gives: `vilan check` 0 errors and 0 warnings, `vilan build .` builds both legs, and `vilan fmt --check` is clean.
- I did not verify the browser runtime. kolt's `e2e/run.sh` fails on a `history.replaceState` gap in its own DOM stub, which predates this order.

## Instructions on kolt `vilan check`
Scratch copy, release build, `VILAN_SEQUENTIAL_CHECK=1`, warm cache per binary, runs 2 and 3:

| Binary | Instructions | Peak RSS |
|---|---|---|
| Base (next @38314319) | 26,753,583,361 / 26,753,574,323 | 230 MB |
| Tip | 26,671,584,578 / 26,671,589,857 | 230 MB |

That is **−0.31%** on the tip despite the std growth, because F78 removed the per-stage copies. `scripts/ci-local.sh perf` is green: T2 verdict green, growth ×1.940, and no ceiling went red.

## Gates on the tip
- **Full workspace** (`cargo nextest run --workspace -j 6`, at 0df43a2d): 9556 run, 9551 passed, 5 failed.
  - Four were mine: two A152 anchor goldens, `b472`, `b249`. All fixed in b580d696, and inference, markdown_golden and vilan-lsp re-ran green.
  - The fifth is `hygiene::no_tracked_file_contains_an_absolute_home_path`, failing on `editors/vscode/src/test/menu.test.ts:27`. It came in with fa3aa10f and is **already red on next — not this lane's.**
  - I did not re-run the full workspace after b580d696, which changed only tests and one golden.
- `native_differential` with `VILAN_NATIVE_DIFFERENTIAL=1`: 155/155.
- check_scope_differential, docs, corpus, diagnostics_ledger, std_twin_parity: green.
- clippy, `cargo fmt --check`, `ci-local.sh vilan-fmt`, `ci-local.sh wasm`, `ci-local.sh perf`: all green.

## Goldens and censuses moved
- Corpus `.mjs`, all runtime-identical: `element-syntax` and `ssr-render` (A151), `dyn-objects` (F78).
- Split fixture: 4 artifacts (A151).
- Native copy and leak censuses: the `dyn-objects` row (F78).
- mdBook anchor golden (A152).
- 3 frozen hashes in `service_layer` (B525).
- The JS copy census and the shared census did not move.

## New finds
In `newitems46-reactive.json`:
- **B?1:** inside `impl SignalCell<type T: (2..)>`, `SignalCell::new` and `.set` on another instance read the block's `T`.
- **B?2:** `entries()` and `get(key)` on a mapped tuple give the template `U`, not the mapped element type.
- **E?3:** a `match` whose arms are two pipe stage types gives no steer toward the `dyn Flow` annotation (what remains of B480).
- **N?4:** the census comment in `std/vilan.toml` is stale.
- **E?5:** the "declare `fun ..`" steer drops a callback parameter's `context` clause when the trait is the program's own.

## Needs your ruling
1. **R-f:** B525 and R-e are breaking, as ruled. Adding `TransientSource::states()` as a requirement is also breaking for any hand-written implementor.
2. **A151, server half:** I made the server `attr` drop `autofocus` so element syntax means the same thing on both twins. The alternative is to keep serving the native attribute on the server, which some server-rendered pages may be relying on to focus at initial parse.
3. **A155:** whether the class writers should APPEND instead stays open (census first).
4. **kolt:** the `Iterator` imports added by the B515 patch are now redundant and can be dropped.