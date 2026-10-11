#!/usr/bin/env bash
# Order 50's seal on next @68f25eb1. Base = the installed vilan 0.47.0 (5fe24f86); base kolt = the scratch clone copy
# committed at e01e59a8 (lucide + search-dict present, untracked); tip kolt = the same copy + the mirror exhibit (153c4595).
# Run with NO CI in flight and no lane cargo; ADVANCE=1 because this is the order's final seal (reset the e121 state from
# sweeps/order50/e121-state-pre-seal.json before ANY re-run).
export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$HOME/.nvm/versions/node/v24.2.0/bin:$PATH"
export CARGO_BUILD_JOBS=6
SP=/tmp/claude-1000/-home-reed-code-vilan-lang/89336be2-ed61-4826-b9ee-21d5898255eb/scratchpad/seal-50
export VILAN_PERF_KOLT_DIR="$SP/kolt-base"
export VILAN_PERF_KOLT_COMMIT=e01e59a8
# SAME-SOURCE seal: the base kolt copy checks clean under the tip compiler too (verified under 68f25eb1), so the verdict
# measures the COMPILER on one source. The mirror exhibit (kolt-tip @153c4595, +7% inferences by M136) is measured
# separately with lsp-latency.py for information - it must not enter the perf verdict keyed by the tip sha.
export VILAN_PERF_ADVANCE=1
# VILAN_PERF_THRESHOLD unset = perf_gate's default 1.10; VILAN_SEAL_PERF_ONLY=1 for a re-run of the perf leg alone.
exec bash /home/reed/code/vilan-lang/proposals/scripts/integration/seal.sh
