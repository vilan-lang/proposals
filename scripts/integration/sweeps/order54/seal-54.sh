#!/usr/bin/env bash
# Order 54's seal on next (after fmt-54's merge = the last). Base = the installed vilan 0.51.1 (5ba52b16); base kolt = the
# scratch clone copy of the owner's WORKING tree as copied on 2026-10-17 (dee494ab + the owner's uncommitted edits in sixteen
# files incl. the E314 and E321 patches; committed inside the copy as 66109df; lucide + search-dict present, untracked;
# checks clean under 0.51.1). Same-source: the tip compiler checks the same copy (no breaking entry; E329/E325 move no kolt line).
# Run with NO CI in flight and no lane cargo, after `cargo clean` in the integration worktree (disk) and with the runner
# online; ADVANCE=1 because this is the order's final seal (reset the e121 state from
# sweeps/order54/e121-state-pre-seal.json before ANY re-run). N166: perf_gate judges the T3 kolt row's peak RSS at 1.05.
# N174: the eight LSP rows run by name; the leaf row is lsp-latency's lone open document, now SEEDED (M159) and served by
# M148/M154/M155/R11 door B/M138's records.
export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$HOME/.nvm/versions/node/v24.2.0/bin:$PATH"
export CARGO_BUILD_JOBS=6
SP=/tmp/claude-1000/-home-reed-code-vilan-lang/89336be2-ed61-4826-b9ee-21d5898255eb/scratchpad/seal-54
export VILAN_PERF_KOLT_DIR="$SP/kolt-base"
export VILAN_PERF_KOLT_COMMIT=611d86f
export VILAN_PERF_ADVANCE=1
# VILAN_PERF_THRESHOLD unset = perf_gate's default 1.10; VILAN_SEAL_PERF_ONLY=1 for a re-run of the perf leg alone.
exec bash /home/reed/code/vilan-lang/proposals/scripts/integration/seal.sh
