#!/usr/bin/env bash
# Order 51's seal on next (the C3 merge). Base = the installed vilan 0.48.0 (ca407da0); base kolt = the scratch clone copy
# of the owner's tree at dee494ab (the owner committed the Order 50 patches on 2026-10-12; lucide + search-dict present,
# untracked; checks clean under 0.48.0). Same-source: the tip compiler checks the same copy (B607/E291 estate 0).
# Run with NO CI in flight and no lane cargo; ADVANCE=1 because this is the order's final seal (reset the e121 state from
# sweeps/order51/e121-state-pre-seal.json before ANY re-run). N166: perf_gate judges the T3 kolt row's peak RSS at 1.05.
export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$HOME/.nvm/versions/node/v24.2.0/bin:$PATH"
export CARGO_BUILD_JOBS=6
SP=/tmp/claude-1000/-home-reed-code-vilan-lang/89336be2-ed61-4826-b9ee-21d5898255eb/scratchpad/seal-51
export VILAN_PERF_KOLT_DIR="$SP/kolt-base"
export VILAN_PERF_KOLT_COMMIT=dee494ab
# SAME-SOURCE seal (seal.sh REFUSES if either compiler rejects the shared source - tools-50's rule).
export VILAN_PERF_ADVANCE=1
# VILAN_PERF_THRESHOLD unset = perf_gate's default 1.10; VILAN_SEAL_PERF_ONLY=1 for a re-run of the perf leg alone.
exec bash /home/reed/code/vilan-lang/proposals/scripts/integration/seal.sh
