# Lane tooling-56 — B687 FIRST → N188 → E357 → E358 → E341 → E342 → N183 → E346 → E347 (Order 56, wave 1; Opus)

Worktree: vilan/.claude/worktrees/tooling-56 (branch `tooling-56` off origin/next @5fd01232).
Items (read each whole): proposals/projects/vilan/tracker/items/B687.md (three recurrences — the figures are in it), N188.md, E357.md, E358.md, E341.md, E342.md, N183.md, E346.md, E347.md.
Prior art: crates/vilan-cli/tests/request_body.rs (M164's harness; the `the writer of a refused body stalls` case ~:376–408), the http runtime's body cap (`grep -n "max_body_bytes\|_dumped\|destroySoon" vilan/std/src/http.vl crates/vilan-core/src/transformer.rs | head`), .config/nextest.toml (slow-timeout), crates/vilan-core/tests/edit_replay_differential.rs (the corpus-as-modules test), the formatter's comment reflow (formatter.rs; E352's rule) and its project lookup (E357), scripts/lsp-latency.py (E358), the `--watch` loop in vilan-cli (E341; the pid registry E335 built), the macro gate `entry_source.contains("macro")` (N183), debug rendering of control characters (E346; B652 settled the literal spelling), the chain printer (E347; E354's commit f0e7f591 is the newest precedent).
Lane std-56 may add ONE row to formatter.rs's `STYLE_BARRIER_METHODS` (A178's `with_length_as`); you own the formatter otherwise this order.

Shell: every command starts with
`export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$HOME/.nvm/versions/node/v24.2.0/bin:$PATH"; export CARGO_BUILD_JOBS=6`
and runs from the worktree by its absolute path (the shell's cwd resets between calls). Suite: `cargo nextest run --workspace -j 6 > suite.log 2>&1; echo $?` — never pipe a gate through grep/head/tail. Never `git stash`, never `git config`, never `--no-verify`, never touch the owner's kolt checkout (~/code/kolt) or the integration worktree; a kolt COPY for fmt censuses is at /tmp/claude-1000/-home-reed-code-vilan-lang/e520b8fd-c1d8-40ac-8d5e-45f93d2477ba/scratchpad/kolt-0de9e2e (copy the WHOLE tree under your scratch before running fmt on it — E357 is about why a lone file lies; never edit the original). Commit on `tooling-56` only; do not merge or push. Scratch under /tmp/claude-1000/-home-reed-code-vilan-lang/e520b8fd-c1d8-40ac-8d5e-45f93d2477ba/scratchpad/tooling-56/. Four other lanes share the box.

## Order of work (commit per item)

1. **B687** — the case asserts on the SERVER's byte count (the runtime exposes how many body bytes it read after a refusal; zero is the contract), and the client-side write failure becomes a secondary check with no tolerance figure; if the runtime has no such count, add it (an instrument, like `store_census`: it counts, it decides nothing) — pin on both backends; the Windows+Node leg stays strict. Reproduce the flake's shape locally if you can (a held socket on loopback); if not, say the pin is proven by construction and name the CI job that will show it.
2. **N188** — split `the_corpus_as_modules_answers_what_a_clean_analysis_answers` per corpus program (one test per fixture, as `native_differential` is), so nextest spreads it and a timeout names a program; or, if the split is not S, a `slow-timeout` override for that binary in .config/nextest.toml with the reason — say which and why.
3. **E357** — why a lone .vl file outside a project reflows no comments while the same file inside its tree does: find the project setting or the skipped pass; a lone file formats exactly as it does in its tree; pin; docs/appendix/cli.md says what a project changes about fmt, if anything.
4. **E358** — lsp-latency.py records the phase line (`VILAN_PHASE_TIMING`) and the analysis count per sample so an outlier names its cause; then, if the 50.2 G repair sample's cause is the server's (a doubled analysis), fix it and pin it.
5. **E341** — a `--watch` session forwards SIGTERM/SIGHUP to its current child through the pid registry, waits briefly, exits 130; pin by the harness's own sequencing (no sleeps).
6. **E342** — the small open end of E333 (the item says what); fold.
7. **N183** — the text-based macro gate replaced by a real one; count the estate first (which programs' cache keys move) and say so.
8. **E346** — debug rendering escapes control characters (a `Paste` no longer prints a live ESC); count the goldens it moves first, read one, regenerate.
9. **E347** — `return f(..)` breaks under the budget the way E354's receiver does; pins; the fmt estate (std / website read-only / corpus / kolt copy) listed.

## Gates, in this order

`cargo fmt`; `cargo clippy --workspace --all-targets -- -D warnings`; `cargo test -p vilan-cli --test request_body`; `cargo test -p vilan-core --test edit_replay_differential` (after N188); `cargo test -p vilan-core --lib formatter`; `cargo test -p vilan-cli --test fmt_declines`; `cargo test -p vilan-core --test docs`; `cargo test -p vilan-cli --test corpus`; `cargo test -p vilan-cli --test perf_gate_script`; `cargo run -q -p vilan-cli -- fmt --check .`; `scripts/ci-local.sh windows` if a `#[cfg(windows)]` pin changed (say so by name); then the FULL suite ONCE at the end.

## Report (hand back)

Commit sha(s) per item; files touched; every gate's exit code (the suite's from `echo $?` with the count line); B687's mechanism (the count, or the instrument you added) and whether the flake was reproduced; N188's choice; goldens moved and why; the fmt estate for E347; deviations with reasons; finds (id-less). No agent ids. Under 70 lines.
