#!/usr/bin/env bash
# Order 58's seal on next @eca174d4 = ceb5b6ff (pass 1: every non-perf leg green, seal-58-run.log) + one reference bump row on genapp:46 (531ad140) + E362 (the empty import set panic the owner hit; the full seal reruns here, seal-58-run2.log) (the owner: "Seal it", then "Cut v0.56.0 once the seal is green", 2026-11-16). Base = the installed vilan 0.55.1 (ad0add35f); base
# kolt = the Order 58 EXHIBIT ~/.vilan/perf-exhibit/order58/kolt @c745405 (a copy of order57's exhibit: the owner's
# vilan-migration tree + the integrator's B688 and A181 commits; src/lucide carried; checks clean under 0.55.1).
# ACROSS A BREAKING CHANGE FOR KOLT (Order 58's std::db: query parameters are `List<dyn SqlValue>`): the tip checks its own
# MIGRATED copy, VILAN_PERF_TIP_KOLT = order58/kolt-tip (git archive c745405 + src/lucide + db-58's kolt-db58.patch, a plain
# directory, no git; checks clean under the tip, 0 errors, 2026-11-16). The owner's checkout is never touched.
# Run with NO CI in flight and no lane cargo, on a quiet box; ADVANCE=1 because this is the order's final seal (conditional on
# a green verdict); reset perf/budgets.toml from sweeps/order58/budgets-pre-seal.toml before ANY re-run.
export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$HOME/.nvm/versions/node/v24.2.0/bin:$PATH"
export CARGO_BUILD_JOBS=6
E="$HOME/.vilan/perf-exhibit/order58"
export VILAN_PERF_KOLT_DIR="$E/kolt"
export VILAN_PERF_KOLT_COMMIT=c745405
export VILAN_PERF_TIP_KOLT="$E/kolt-tip"
export VILAN_PERF_ADVANCE=1
# VILAN_PERF_THRESHOLD unset = perf_gate's default 1.10; VILAN_SEAL_PERF_ONLY=1 for a re-run of the perf leg alone.
exec bash /home/reed/code/vilan-lang/proposals/scripts/integration/seal.sh
