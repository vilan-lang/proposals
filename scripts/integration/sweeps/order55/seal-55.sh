#!/usr/bin/env bash
# Order 55's seal on next (after fmt-55's merge = the last). Base = the installed vilan 0.52.0 (d18f50d8); base kolt = the
# scratch clone copy of the owner's tree at 3dbc73b (clean on 2026-10-27: the owner had committed everything, the three
# Order 55 comment lines included; lucide + search-dict carried, untracked; checks clean under 0.52.0). ACROSS A BREAKING
# RELEASE (M171's Event members, M168's Server literal, M164's default body cap): the tip checks its own MIGRATED copy
# (VILAN_PERF_TIP_KOLT = kolt-tip: the same tree + the owner's two required patches, std-55's kolt-m171-std_ext.patch and
# http-55's files.vl:235 max_body_bytes line; a plain directory, no git; checks clean under the tip with B677's two warnings).
# Run with NO CI in flight and no lane cargo, after `cargo clean` in the integration worktree (disk) and with the runner
# online; ADVANCE=1 because this is the order's final seal (reset perf/budgets.toml from
# sweeps/order55/budgets-pre-seal.toml before ANY re-run). N166: perf_gate judges the T3 kolt row's peak RSS at 1.05.
export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$HOME/.nvm/versions/node/v24.2.0/bin:$PATH"
export CARGO_BUILD_JOBS=6
SP=/tmp/claude-1000/-home-reed-code-vilan-lang/e520b8fd-c1d8-40ac-8d5e-45f93d2477ba/scratchpad/seal-55
export VILAN_PERF_KOLT_DIR="$SP/kolt-base"
export VILAN_PERF_KOLT_COMMIT=3dbc73b
export VILAN_PERF_TIP_KOLT="$SP/kolt-tip"
export VILAN_PERF_ADVANCE=1
# VILAN_PERF_THRESHOLD unset = perf_gate's default 1.10; VILAN_SEAL_PERF_ONLY=1 for a re-run of the perf leg alone.
exec bash /home/reed/code/vilan-lang/proposals/scripts/integration/seal.sh
