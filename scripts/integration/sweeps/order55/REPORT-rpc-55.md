# REPORT rpc-55 — Order 55 (Fable 5.1)

**Tip** `def08264` on branch `rpc-55` (worktree `vilan/.claude/worktrees/rpc-55`), **base** `d18f50d8` (`origin/next` = the v0.52.0 fold). Six commits, nothing pushed, nothing rebased. `rpc-55-STATUS.md` untracked at the worktree root.

## Commits (item / family)

| sha | item | family | what |
| --- | --- | --- | --- |
| a5be10ce | M172 | performance | the store mirror's holds and slots keyed by what they are looked up by (four lists → maps, in place under `write()`); `StoreNode.ids` a `Shared` cell; counting pin |
| a7045554 | B677 | diagnostics | the refusal names the closure parameter and its clause fix (literal wrap listed last, at the parameter's arity); door 1's warning (user code only); ledger rows 745/746; spec §8.5 paragraph; two older pins retargeted |
| c5dde978 | M165 (rpc half) | fix | `respond_with_status` runs the dispatch under `guarded_async`: a thrown `[rpc]` answers `Remote("`m` threw: …")`, the log keeps a stderr line; native `__guarded_async` binding (vilan-rt executor + vilan-rust arm); three pins |
| 70ce7711 | A174 door 2 | feature | `Connection::close(reason)` + `close_connection(id, reason)` (closers registry at accept, close frame with reason, next-tick close, SSE stream ended); `ws::close_frame_with`; docs; pin |
| bbd4efc3 | B677 door 1 | diagnostics | a `View` parameter called in a literal NESTED in an owner body is warned (kolt's `page` found); the `Shared` census rows (mirror 31→37, store_core 4→5, server 6→7, total 239→247) |
| def08264 | perf | — | `[[bump]]` rows for `example:todo` (reference, ci) at 1.005 |

Paper: `proposals/projects/vilan/proposal/closure-owner.md` (B677 door 2, for the owner's Order 56 ruling — **hand to the owner**; rec: door 2 narrowed to `View`, behind the Order 55 warning). Finds: `sweeps/order55/newitems55-rpc-55.json` (A?1 revoke-by-value as A174's follow-up, M?1 the store's per-key diff); repros under `sweeps/order55/rpc-55/finds/` (`m172_holds.vl`, `b677_mixed_clause.vl`). Ledger: `proposal/diagnostics-ledger.md` two NEW rows + the tsv rows 745/746.

## Where the premises were wrong

- **M172**: the four lists are exactly as filed, but two MORE quadratic walks sat under every mount/unmount the item did not name: `MirrorView::leave_replica` walked every slot per parked boundary (now a `covered` count map), and `store_core::identity_at` BOUND the root's identity `NativeMap` (a deep copy of every identity minted) once per boundary named (`mirror_boundary_some → store_identity_at`) — 1.05M nodes copied at 1024 keys. `StoreNode.ids` is now `Option<Shared<NativeMap<i32>>>`, the shape `keyed` already had (store_core.vl is nobody's this order; the one function changed, listed below). A third residue is the store's own and filed (M?1): a keyed replica's per-key `gone` diffs every watched key (`keyed_hashes` snapshot per write).
- **B677**: kolt at b04095a had already typed the six wrappers the item named — the estate count for the warning was **0** until the nested rule — and a SEVENTH is still plain: `panels.vl:781` `page: (|str| View) context page_focus`, called at `:922` and `:2068` inside `focused_page`'s body inside a `swap`. A clause for another context injects that one and still captures the owner (probed, `b677_mixed_clause.vl`: the cleanups run only at the root's dispose). Every page kolt navigates to is built under the app root. Also: a `void`-returning parameter cannot be told "builds effects" from its type, so the warning splits — `View` anywhere inside the body (nested literals included), `void` only at the body's direct call (the item's `|| provide()`); a nested `|K| void` handler callback is not flagged. One std site fires by design (`MaybeSignal::bind(react: |T| void)`), gated out as library code (C3a's domain).
- **M165**: on the base, in-process (`local_rpc`) the throw took the whole program down (exit 1 with the panic); over a socket the task died and the client hung, as filed. The native backend had NO `__guarded_async` binding (`HttpTransport` reached it as a refusal) — using `guarded_async` in `respond_with_status` would have refused every native rpc program, so the binding was added (`vilan_rt::executor::guarded_async` over the executor's own `Catch`; the emitter arm beside `__nursery_run`). The log line is the lane's own (`rpc `m` threw, and the call was answered with the error: …`, through the reactive trace's `__trace_line` seam, stderr); the runtime's `unhandled task error (spawned in accept_socket)` line cannot stay because the task no longer dies — the pins assert the new line is present and the old one absent.
- **A174**: the brief's "the client's mirror sees its closed/`Absent` status" — it sees `Refreshing(last)` from the drop (connection down) and the socket goes `Closed` when the redial's `authorize` refuses; `Absent` is a boundary the server says is not there, which a closed wire never says. `Connection::close` lands on the NEXT tick so the closing rpc's reply reaches the client first (otherwise `kick` rejects with "connection lost"); kolt keeps `connection.id`, so the id form exists too.

## Gates (final tree def08264 unless noted)

- Full suite, `--cargo-profile ci-test -E 'not binary(deep_nesting)' -j 6`: run 2 on bbd4efc3 **10819/10819 passed, 37 skipped** (944 s). Run 1 (on the first four commits, with the nested-rule edit landing mid-run) was 10815/10819: two stale-binary reds (`build_id`, the new nested pin), the census rows, and `hmr::force_refresh_reloads_a_connected_browser_once` (307 s under the full suite; passed alone in the rerun). The bump-row commit touches only `perf/budgets.toml`.
- `ci_ignored_pins`, `hygiene`, `corpus`, `check_scope_differential`: in the suite, green.
- The four differentials, named run (`permutation_differential`, `edit_replay_differential`, `replay_differential`, `check_scope_differential`, vilan-core): **69/69**.
- Native differential: default **298/298** (after M172) and the `VILAN_NATIVE_DIFFERENTIAL=1` sweep **299/299** (with `native/rpc_body_throws.vl`); both modes byte-identical.
- `cargo clippy --workspace --all-targets -- -D warnings`: green. `cargo fmt --check`: green. `cargo run -p vilan-cli -- fmt --check .`: green.
- Deep-nesting canary: not run — no recursive pass, module walk or check structure changed (context.rs gained a flat pass over the call graph's nodes).
- vilan-lsp binary: not run separately (in the suite, green); no table/record changed.
- `scripts/ci-local.sh perf` (release): **green** (local class reports; growth x1.930 ≤ 2.3). Against v0.52.0's release binary on this box: math x0.9999, watch x1.0002, plain:160 x1.0001, plain:320 x1.0000, genapp:46 x1.0001 (the cold rows within 0.1 %); todo x1.0024, fullstack x1.0024, ssr x1.0024, walkthrough x1.0028, rpc x1.0007, browser/canvas x1.0002/1.0005 — std growth (mirror.vl +~130 lines, rpc.vl, server.vl, the B677 pass); `[[bump]]` rows for `example:todo` (1.005, reference + ci). Functions changed in no emitter, no analyzer.rs, no mono.rs, no lexer/parser.
- kolt cold check RSS (`rss-probe.py`, `MALLOC_ARENA_MAX=1` both sides, release vs installed 0.52.0): base median 454,636 KB, lane 446,960 KB (**x0.983**).
- `vilan check` on the kolt copy under the lane's std: 0 errors (the keyed mirror is API-identical).

## Estate counts (B677's warning, user code)

kolt **2** (`panels.vl:922`, `:2068` — the `page` wrapper; printed twice, once per leg), website 0, the eleven examples 0, the corpus 0, the native tests 0, std 0 (the `bind` site gated). A warning, not a refusal — `diagnostics`, not `breaking`. Breaking entries: **none**.

## Measurements (M172)

Copies (`__clone` calls) per phase of the four-phase program, 48 → 192 keys: page unmount 307k→4.9M (**16×**) before, 5.6k→22.3k (**4.0×**) after; page mount 13× → 4.0×; table mount 10× → 4.0×; table unmount 15× → 4.9× (the residual is the store's per-key diff, M?1). Wall on this loaded box at 256 keys: mount 88→36 ms, unmount 94→6 ms. The kolt sidebar click (550 ms) was NOT reproduced in a browser — the DOM-stub harness in kolt/e2e does not mount the sidebar, and I did not script a browser; the pin's program is kolt's shape (one org store, a table view holding every key, a page view beside it). The counting pin is the gate: `store::m172_a_mirrors_holds_and_releases_cost_their_own_entries_not_the_table` (red on the base std via `VILAN_STD=`: 9.6–16×).

## Functions changed outside my ownership (mechanical, listed)

- `crates/vilan-rt/src/executor.rs`: `guarded_async` added (M165). `crates/vilan-rust/src/lib.rs`: the `__guarded_async` extern arm (M165). No lane holds vilan-rt/vilan-rust this order.
- `crates/vilan-core/src/context.rs` (the checks — solver-55's area is `track_caller.rs`/inference; context.rs was untouched by them per the ownership map): `closure_parameter_refusal`, `literal_wrap_of`, `warn_plain_closure_parameters_under_owner_bodies`, `Builds`, `builds_under_the_owner`; the refusal arm in `analyze`'s parameter-landing loop gained one `else if`. **Rebase note for the integrator:** if solver-55 touched `context.rs`, the conflict is local to that arm.
- `vilan/std/src/reactive/store_core.vl`: `StoreNode.ids` type + `identity_at` (M172). `vilan/std/src/ws.vl`: `close_frame_with` (A174).
- `crates/vilan-cli/tests/shared_census.rs`: the census rows. `crates/vilan-cli/tests/service_layer.rs`: `vilan_run_with_liveness_bound_capturing`.

## Patch notes for kolt (the owner; plain hyphens)

1. **B677 - `src/panels.vl:781` (also `:824`, `:945`, `:1834`)**: `page: (|str| View) context page_focus` builds every page under the app root (the literal at `views.vl:202`), released only with the root. Type it `page: (sync |str| View) context (owner_scope, page_focus)`; the 0.53.0 checker warns at `:922` and `:2068` until then.
2. **M172**: nothing to change; the 12 s / 550 ms go with 0.53.0. The six typed wrappers stay right.
3. **M165**: a thrown `[rpc]` now answers `Err(RpcError::Remote("`create_task` threw: TypeError: Provided value cannot be bound to SQLite parameter 8"))` - the form can show it; the server log line is `rpc `create_task` threw, and the call was answered with the error: …` on stderr.
4. **A174**: sign-out: `self.connection` is an id in `KoltStore`, so `close_connection(self.connection, "signed out")` after `end_session(token)` (the reply reaches the client first); member removal: close every connection of the removed user (kolt's own user→connection map; `on_connect`/`on_disconnect` carry the ids) and the redial's `authorize`/`organization` re-check does the rest.

## Questions for the owner (numbered, with recommendations)

1. **B677 door 2** (`closure-owner.md`): make a closure parameter answering `View` carry `context owner_scope` by default? Rec: yes, narrowed to `View`/`impl Slot`, `sync` implied, in Order 56 behind this order's warning; no opt-out spelling until a caller wants the creation owner.
2. **`MaybeSignal::bind(react: |T| void)`** is the one std site the warning would flag (gated as library code): should `react` carry the clause so a reaction's registrations die with the run? Rec: no - a reaction is a DOM write; leave it, note it in the paper's §3 (done).
3. **M165's log line wording** - the brief asked to keep the runtime's `unhandled task error (spawned in accept_socket)` line; the task no longer dies, so the lane's line replaced it. Rec: accept the lane's line (it names the method and says the call was answered).
4. **A174 door 1** (A?1, revoke by value): Order 56? Rec: yes, S-M with what door 2 taught (channel by root identity, grant by path identity, `session.revoke(channel)` or `release_grant(base)`).
5. **M?1** (the store's per-key diff, K² hash copies at K keys released one turn each): a std lane in Order 56? Rec: yes - a key-touch write diffs that key alone; `node_empty` asks `len()`.

## Housekeeping

- Scratch: `target/rpc-55-scratch/` (694 MB: the kolt copy with `src/lucide` + `src/search-dict` carried, the website copy, the m172/m165/b677 repros, every log). Nothing removed; no cache root written outside the worktree's target (`~/.vilan/std-cache` holds the lane std's hashed copies, 43 MB, the toolchain's own). The worktree's `target/` is 59 GB (ci-test 39 GB, debug 6.5 GB, release 0.2 GB); `df` went 635 → 323 GB free over the order (other lanes' targets included) - the integrator may `cargo clean` this worktree after the merge.
- No process of mine is running (checked by name under the scratch and target paths).
- CHANGELOG: five `## Unreleased` entries (performance, diagnostics, fix, feature), markers in place, the B677 entry carrying the nested rule.
