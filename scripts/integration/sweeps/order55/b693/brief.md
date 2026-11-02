# Lane b693 — B693 (`StoreSome::assume` copies the whole payload per read)

Worktree: vilan/.claude/worktrees/b693 (branch `b693` off origin/next @f9fcc6ce).
Design: proposals/projects/vilan/proposal/store-assume-keeper.md — READ IT FIRST and build what it says; a deviation goes in the report with its reason.
Item: proposals/projects/vilan/tracker/items/B693.md (the owner's text; its repro is sweeps/order55/b693/repros/assume-main.vl).
Prior art to read: `hash-map-lend.md` §8 (B689 as built, the lane before you), store_core.vl's `StoreFeed` / `attach_feed` / `detach_feed` / `store_switch` / `write_at`, store.vl's `map_feed` + `MapFlow::open` (a feed's life), reactive.vl `defer_to_owner` (~:1360).

Shell: every command starts with
`export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$HOME/.nvm/versions/node/v24.2.0/bin:$PATH"; export CARGO_BUILD_JOBS=6`
and runs from the worktree by its absolute path (the shell's cwd resets between calls). Suite: `cargo nextest run --workspace -j 6 > suite.log 2>&1; echo $?` — never pipe a gate through grep/head/tail. Never `git stash`, never `git config`, never `--no-verify`, never touch the owner's kolt checkout (~/code/kolt) or the integration worktree. Commit on `b693` only; do not merge or push.

## Order of work

1. `store_switch` (store_core.vl ~:290): touch the two flags' feeds (design §2.2). `store_touch` is right there.
2. `StoreSome::assume` (store_core.vl ~:1040): the keeper feed on `self.gate`, the lend without a copy, `defer_to_owner` for the detach (design §2). `fresh_identity`, `attach_feed`, `detach_feed`, `StoreTouch` are in the file; `defer_to_owner` is `std::reactive`'s — check how store_core.vl imports from reactive.vl today and follow it. Note `RemoteStoreSome::assume` (store.vl ~:1773) delegates and needs nothing.
3. `cargo build`, then the two existing pins first: `cargo test -p vilan-core --test inference -- assumed b526` — both must stay green unchanged.
4. Pins per design §4 (1–6) in crates/vilan-core/tests/inference/store.rs (the codegen-shape pin in the B689 form at std_surface.rs:916 — `emitted_function`, no `__clone` in the lend; plant the old `last = Some(*payload)` to prove it red, then restore). Native differential: a program beside crates/vilan-cli/tests/native/hash_map_lend.vl for the §2.2 rows (enum handle, Option → None, key removed under `at(id).some()`, outer variant). If the store has no instrument for "which feeds a write enlisted", say so and pin §4.4 structurally as the design allows — no sleeps, no timing gates.
5. Docs per design §5 (docs/std/store.md `when_live` paragraph; `web/remote.vl`'s comment if you reword), CHANGELOG `## Unreleased` fix entry (B693) in the B689 entry's form, ONE bold head.
6. Corpus goldens (`cargo test -p vilan-cli --test corpus`): `assume`'s emitted JS changes, so goldens using `when_live`/`assume` move. Rebuild the debug binary first, READ the diff of one moved golden to confirm it is only the expected shape, then regenerate. Say which moved and why. Copy censuses may move too (read them).
7. Measure: the repro (vilan.toml `[package] name = "b693" version = "0.1.0" entry = "main.vl"`, source at src/main.vl) with the lane's built `vilan` on node, before (baseline from the item on next: 13.4 / 271 / 4,264 ms) and after; and `vilan build --target native` after. Also re-run the B689 repro (sweeps/order55/b689/repros/b689-main.vl) to show it unchanged. Numbers are reported, not a gate.
8. Gates, in this order: `cargo fmt`; `cargo clippy --workspace --all-targets -- -D warnings`; `cargo test -p vilan-core --test inference`; `cargo test -p vilan-core --test docs`; `cargo test -p vilan-cli --test corpus`; then the full nextest suite ONCE at the end, after every edit. perf/budgets.toml only if a budget goes red (follow B689's rows at the bottom of the file; the B689 lane found std-growth bumps of ~1 %).

## Report (hand back)

Commit sha(s) on `b693`; files touched; every gate's exit code (the suite's from `echo $?`, with the count line from suite.log); the goldens moved and why; the repro timings before/after on node and native; deviations from the design with reasons; the answer to design §4.4 (instrument or structural); anything out of scope you found, as a find (id-less: title, repro, where). Do not quote agent ids. Under 60 lines.
