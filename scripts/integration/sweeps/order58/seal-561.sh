#!/usr/bin/env bash
# The v0.56.1 patch's seal on b4561bf6 = the tag v0.56.0 (d20bbfd9) + ONE commit, B746 (lane b746-58): the head of
# release/0.56 (the owner: "Yes, cut v0.56.1", 2026-11-16). The integration worktree is DETACHED at that commit for the run
# (next's merge 7df946e3 has the same tree); put it back on `next` afterwards. Base = the installed vilan 0.56.0 (b6bc6b542);
# both sides check ONE source: the exhibit ~/.vilan/perf-exhibit/order58b/kolt @76067e7 (a copy of order58's exhibit with
# db-58's kolt-db58.patch committed = order58's kolt-tip; checks clean under 0.56.0). No VILAN_PERF_ADVANCE: a patch is not
# an order's final seal. Run with no CI job on this machine during the perf leg.
export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$HOME/.nvm/versions/node/v24.2.0/bin:$PATH"
export CARGO_BUILD_JOBS=6
E="$HOME/.vilan/perf-exhibit/order58b"
export VILAN_PERF_KOLT_DIR="$E/kolt"
export VILAN_PERF_KOLT_COMMIT=76067e7
exec bash /home/reed/code/vilan-lang/proposals/scripts/integration/seal.sh
