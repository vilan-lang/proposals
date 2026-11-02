# Lane m186 — M186 (a read below any store handle copies its path lists)

Worktree: vilan/.claude/worktrees/m186 (branch `m186` off origin/next @8e8c463c).
Design: proposals/projects/vilan/proposal/store-path-sharing.md — READ IT FIRST and build what it says; a deviation goes in the report with its reason.
Item: proposals/projects/vilan/tracker/items/M186.md (the lane b693 find; its measurement is the B693 phases program in crates/vilan-core/tests/inference/store.rs, `B693_PHASES` + `copies_per_print`).
Prior art to read: `store-assume-keeper.md` §7 (B693 as built, the lane before you), store_core.vl top to bottom (1,367 lines: the handles ~:838–1100, the walkers ~:320–720), store.vl's `splice_at` (~:405), the flows' `open` (~:930–1000), `mirror_boundary*` (~:1670), `RemoteStore*::at` (~:1800); `shared.vl` (`Shared::new/read/write`).

Shell: every command starts with
`export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$HOME/.nvm/versions/node/v24.2.0/bin:$PATH"; export CARGO_BUILD_JOBS=6`
and runs from the worktree by its absolute path (the shell's cwd resets between calls). Suite: `cargo nextest run --workspace -j 6 > suite.log 2>&1; echo $?` — never pipe a gate through grep/head/tail. Never `git stash`, never `git config`, never `--no-verify`, never touch the owner's kolt checkout (~/code/kolt) or the integration worktree. Commit on `m186` only; do not merge or push. Scratch files go under /tmp/claude-1000/-home-reed-code-vilan-lang/e520b8fd-c1d8-40ac-8d5e-45f93d2477ba/scratchpad/m186/ (make it).

## Order of work

1. Measure BEFORE on the lane's own tree before touching it: build the debug binary, run `cargo test -p vilan-core --test inference -- b693_an_assumed_handle_copies_its_payload_once -- --nocapture` and note the per-phase copy counts at 10 and 1,000 records (phase 2 = the hundred reads; expect ~7,400 = 74 per read). Also time the B693 repro on node (sweeps/order55/b693/repros/assume-main.vl; vilan.toml `[package] name = "m186" version = "0.1.0" entry = "main.vl"`): the per-read ms at 10 / 1,000 / 10,000 records (the item's baseline after B693: 10.4 / 4.3 / 4.5 ms for 2,000 reads).
2. `StorePath` + `StorePathStep` in store_core.vl (design §2), `root`/`child`/`len`/`steps`; the handles' fields and `Store::new`, `descend`, `variant`, `tag`, `live`, `assume`, `flag_path` (§2.1). Export both; re-export from store.vl's list (~:95) as the other core names are.
3. The entry points (§2.2 table): `identity_at`, `store_identity_at`, `watch_at`, `store_watch`, `observe_at`, `counted`, `attach_feed`, `detach_feed`, `write_at`, `notify_at`; store.vl's `splice_at`, the flows' `open`, `mirror_boundary` + `mirror_boundary_some`. The walkers stay on `List<StoreStep>`. `grep -n "List<StoreStep>\|\.path\b\|\.gate\b" vilan/std/src/reactive/*.vl vilan/std/src/web/*.vl vilan/std/src/rpc/*.vl` and account for every hit: handle-path or relative/wire path.
4. `cargo build`, then the cheap pins first: `cargo test -p vilan-core --test inference -- identity a146 a142 a149 a153 b526 b693 mirrored store_census` — all green unchanged before any new pin.
5. Pins per design §4 (1–6): exact copy counts in the M172/B693 form (plant-proven red), depth 3 vs 5, identity stability, the wire-log order, the native differential `native/store_path_sharing.vl` beside `store_assume_keeper.vl`. No sleeps, no timing gates.
6. Docs per design §5; CHANGELOG `## Unreleased` perf entry (M186) in the B693 entry's form, ONE bold head; store.vl's header note.
7. Corpus goldens (`cargo test -p vilan-cli --test corpus`): the handles' emitted JS changes, so goldens that project a store move. Rebuild the debug binary first, READ the diff of one moved golden to confirm the shape (a `child(step)` call where a list copy was), then regenerate; say which moved and why. Copy censuses may move (read them).
8. Measure AFTER: the same phase counts and the same repro timings on node, and `vilan build --target native` + run for the native timings (release). Report before/after side by side. If the identity ask's fill shows on a tracked-read loop (design §2.3), say so with the number — do NOT build the cached key; it is the owner's call.
9. Gates, in this order: `cargo fmt`; `cargo clippy --workspace --all-targets -- -D warnings`; `cargo test -p vilan-core --test inference`; `cargo test -p vilan-core --test docs`; `cargo test -p vilan-cli --test corpus`; `cargo test -p vilan-cli --test native_differential`; then the full nextest suite ONCE at the end, after every edit. perf/budgets.toml only if a budget goes red (`scripts/ci-local.sh perf`; follow the B693 `[[bump]]` row at the bottom of the file — std grew, so a reference-class row may need x1.00x; say which).

## Report (hand back)

Commit sha(s) on `m186`; files touched; every gate's exit code (the suite's from `echo $?`, with the count line from suite.log); the goldens moved and why; the copy counts and the repro timings before/after on node and native; deviations from the design with reasons; the §2.3 identity-fill answer; anything out of scope you found, as a find (id-less: title, repro, where). Do not quote agent ids. Under 60 lines.
