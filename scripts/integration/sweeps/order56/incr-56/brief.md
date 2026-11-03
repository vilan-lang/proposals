# Lane incr-56 — M188 → M189 → the next post-pass as a record → M163 re-weighed (Order 56, wave 1; Opus)

Worktree: vilan/.claude/worktrees/incr-56 (branch `incr-56` off origin/next @5fd01232).
Items: proposals/projects/vilan/tracker/items/M188.md, M189.md, M163.md, M110.md (read its last three entries), E340's close text in archive.md (the pass table on the N186 series), E292.md.
The series: N186's (exhibit ~/.vilan/perf-exhibit/order56/kolt @3fb5d74 — the owner's kolt WITH B688's imports; carries src/lucide + src/search-dict); base = a RELEASE build of 5fd01232's `vilan-lsp` kept at ~/.vilan/perf-exhibit/order56/lsp-base-56 (build it first; the old lsp-base there is 8e8c463c's — keep both, name yours); tip = your tree's. `scripts/lsp-latency.py --runs 5` with the cold first dropped; compare INSTRUCTIONS (the ratio gate now judges them; CPU beside). Load: four other lanes build on this box — read instructions, say the load.
Prior art: the E340 doors in analyzer.rs (`compute_retaining_positions`, the lazy call test, the census counter `retaining-fixpoints`), the three record precedents (`analyzer/move_tables.rs`, `lazy_tables.rs`, `hover_records.rs`), `incremental.rs`, the pass map (proposals/projects/vilan/proposal/analyzer-pass-map.md §3 + §7), the edit-replay differential (crates/vilan-core/tests/edit_replay_differential.rs — a new table MUST be observed by it; a plant must turn it red).
You own the checks-phase records and `incremental.rs`; lane solver-56 owns the solver's rules and lane lang-56 the resolver — a conflict in analyzer.rs is expected to be textual only; the integrator merges you after them and re-runs the differentials.

Shell: every command starts with
`export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$HOME/.nvm/versions/node/v24.2.0/bin:$PATH"; export CARGO_BUILD_JOBS=6`
and runs from the worktree by its absolute path (the shell's cwd resets between calls). Suite: `cargo nextest run --workspace -j 6 > suite.log 2>&1; echo $?` — never pipe a gate through grep/head/tail. Never `git stash`, never `git config`, never `--no-verify`, never touch the owner's kolt checkout (~/code/kolt) or the integration worktree; measure on the exhibit clone only. Commit on `incr-56` only; do not merge or push. Scratch under /tmp/claude-1000/-home-reed-code-vilan-lang/e520b8fd-c1d8-40ac-8d5e-45f93d2477ba/scratchpad/incr-56/ (the old incr-56 scratch there is Order 55's; make a `56/` subdirectory).

## Order of work (commit per door)

1. Base figures: the seven rows base-vs-base on the exhibit with the base binary (the series' figures on 3fb5d74 — N186's were taken on 2684c70; these are the ones the seal compares against) — report the table.
2. **M188** — a per-callee retaining summary: a body-expression index as class D rows (the S7 record form, filed per module, served on a hit; `move_tables.rs` is the model), then `check_view_escape` computes the summary only for the callee a live call asks about. Pin: the census counter (`retaining-fixpoints` → a per-callee counter), the differential observes the index (a plant red), css and parse break no longer pay the sweep.
3. **M189** — the capture scan as a lazy per-closure memo filed on the record (keyed by the closure's entity, invalidated with its item); pin: a served keystroke scans only the hot set's closures (a counter), the differential.
4. The next post-pass by cost on the served leaf (your base table decides: contexts+graph ~180 ms or the const post-pass ~200 ms at load in E340's table) — as a record in the same form, with the differential plant; if neither is M or smaller, the measured sizing in the pass map's §7 instead, and say so.
5. **M163** re-weighed: `plan_resource_drops` on the served leaf on this exhibit (quiet-estimated); decide the const-reach gate question in the item's terms and write the recommendation (the owner rules).
6. Tip figures: the seven rows with your tree; the pass table base vs tip; the T2 gate (`VILAN_PERF_CLASS=ci scripts/ci-local.sh perf`) — a `[[bump]]` only if red, with the reason.

## Gates, in this order

`cargo fmt`; `cargo clippy --workspace --all-targets -- -D warnings`; `cargo test -p vilan-core --test inference`; `cargo test -p vilan-core --test docs`; `cargo test -p vilan-cli --test corpus`; the differentials (`cargo nextest run -p vilan-core -E 'binary(/differential|id_windows|module_resolution/)' -j 6` — byte-identical; the N188 timeout that passes alone is acceptable, say so) and `cargo nextest run -p vilan-lsp -j 6`; `cargo run -q -p vilan-cli -- fmt --check .`; `python3 scripts/regen-markdown-golden.py` if you added or changed a docs HEADING (mdbook v0.5.4 is installed; read the one-line-per-anchor diff; `cargo test -p vilan-core --test markdown_golden`); then the FULL suite ONCE at the end.

## Report (hand back)

Commit sha(s) per door; files touched; every gate's exit code (the suite's from `echo $?` with the count line); the base table (seven rows, instructions + CPU + load); the tip table and the pass table base vs tip; the served leaf's instructions before/after per door; the M163 recommendation; deviations with reasons; finds (id-less). No agent ids. Under 70 lines.
