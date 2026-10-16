#!/usr/bin/env bash
# Order 53's seal on next (after fmt-53's merge = the last). Base = the installed vilan 0.50.0 (b923bfc6); base kolt = the
# scratch clone copy of the owner's WORKING tree as copied on 2026-10-16 (dee494ab + the owner's uncommitted edits in eleven
# files + the E314 prefs.vl patch; committed inside the copy as d48ab61; lucide + search-dict present, untracked; checks
# clean under 0.50.0). Same-source: the tip compiler checks the same copy (no breaking entry; E321 is layout only).
# Run with NO CI in flight and no lane cargo; ADVANCE=1 because this is the order's final seal (reset the e121 state from
# sweeps/order53/e121-state-pre-seal.json before ANY re-run). N166: perf_gate judges the T3 kolt row's peak RSS at 1.05.
# N174: the seven LSP rows run by name; P3's cold-open effect shows on the open rows.
export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$HOME/.nvm/versions/node/v24.2.0/bin:$PATH"
export CARGO_BUILD_JOBS=6
SP=/tmp/claude-1000/-home-reed-code-vilan-lang/89336be2-ed61-4826-b9ee-21d5898255eb/scratchpad/seal-53
export VILAN_PERF_KOLT_DIR="$SP/kolt-base"
export VILAN_PERF_KOLT_COMMIT=d48ab61
export VILAN_PERF_ADVANCE=1
# VILAN_PERF_THRESHOLD unset = perf_gate's default 1.10; VILAN_SEAL_PERF_ONLY=1 for a re-run of the perf leg alone.
exec bash /home/reed/code/vilan-lang/proposals/scripts/integration/seal.sh
