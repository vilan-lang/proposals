#!/usr/bin/env bash
# Order 56's seal on next (after ui-56's and http-56's merges = the last). Base = the installed vilan 0.53.1; base kolt = the
# Order 56 EXHIBIT ~/.vilan/perf-exhibit/order56/kolt @3fb5d74 (the owner's vilan-migration tree + the integrator's B688 import
# commit on the owner's word; src/lucide + src/search-dict carried; checks clean under 0.53.1 - B688's imports are plain module
# imports). ACROSS A BREAKING RELEASE (A181's `(impl _)` read with an error, A182, B688, M191's `update` removal - kolt has 0
# users, B695 on JS): the tip checks its own MIGRATED copy, VILAN_PERF_TIP_KOLT = kolt-tip (the exhibit + lang-56b's
# kolt-a181-impl-star.patch, a plain directory, no git; both entries check clean under the tip, 0 errors 0 warnings, 2026-11-04).
# Run with NO CI in flight and no lane cargo, after `cargo clean` in the integration worktree (disk) and with the runner
# online; ADVANCE=1 because this is the order's final seal (the e121 rows' interim targets re-taken on a quiet box; the
# advance is conditional on a green verdict since incr-56's patch); reset perf/budgets.toml from
# sweeps/order57/budgets-pre-seal.toml before ANY re-run. N166: perf_gate judges the T3 kolt row's peak RSS at 1.05.
export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$HOME/.nvm/versions/node/v24.2.0/bin:$PATH"
export CARGO_BUILD_JOBS=6
E="$HOME/.vilan/perf-exhibit/order56"
export VILAN_PERF_KOLT_DIR="$E/kolt"
export VILAN_PERF_KOLT_COMMIT=3fb5d74
export VILAN_PERF_TIP_KOLT="$E/kolt-tip"
export VILAN_PERF_ADVANCE=1
# VILAN_PERF_THRESHOLD unset = perf_gate's default 1.10; VILAN_SEAL_PERF_ONLY=1 for a re-run of the perf leg alone.
exec bash /home/reed/code/vilan-lang/proposals/scripts/integration/seal.sh
