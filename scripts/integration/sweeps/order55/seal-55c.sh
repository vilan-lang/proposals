#!/usr/bin/env bash
# seal-55c.sh = seal-55b.sh without the e121 advance: pass 3, the perf leg alone again on the same anchored exhibit (2026-10-27).
# Order 55's perf leg RE-RUN alone (pass 2) on the ANCHORED exhibit: pass 1 (seal-c50a0a58.out) was green on every leg and
# RED on the perf verdict for the exhibit's drift, not a regression (T3 CPU x0.989, instr x1.001, RSS x0.991; the four LSP
# rows measured x1.01/x0.98/x0.97/x0.84): N174's anchors for `parse break` (a mandate row) and the two model.vl rows are
# gone from the owner's kolt since 38a7ac9 (organizations), and E121's 500 ms leaf mandate is exceeded by the BASE itself
# (1190 ms) on the 168-commit kolt. Base kolt = kolt-base (the clone) archived at 46c5b59 (2026-10-20, the last owner
# commit carrying every anchor; checks clean under 0.52.0); tip = kolt-anchored-tip (46c5b59 + the M171 member removed +
# nothing else needed; checks clean under the tip). Reset ~/.vilan/perf-verdicts/e121-state.json from e121-state-pre-seal.json
# BEFORE this run (pass 1 advanced shared.vl 6 -> 7 despite its red verdict). Run QUIET, no CI in flight.
export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$HOME/.nvm/versions/node/v24.2.0/bin:$PATH"
export CARGO_BUILD_JOBS=6
# The exhibit lives OUTSIDE the session scratchpad (the first pass-2 attempt refused: a session restart wiped /tmp/claude-*/scratchpad,
# taking both copies with it). Rebuilt 2026-10-27: kolt-base = `git clone --no-hardlinks ~/code/kolt` + src/lucide + src/search-dict;
# kolt-anchored-tip = `git archive 46c5b59` + the two generated dirs + the `default_prevented` member (its doc line and attribute) deleted
# from src/lib/std_ext.vl by hand (std-55's patch is against 3dbc73b and does not apply at 46c5b59; `stop_propagation` is not there yet).
SP=$HOME/.vilan/perf-exhibit/order55
export VILAN_PERF_KOLT_DIR="$SP/kolt-base"
export VILAN_PERF_KOLT_COMMIT=46c5b59
export VILAN_PERF_TIP_KOLT="$SP/kolt-anchored-tip"
# no VILAN_PERF_ADVANCE: pass 3 is a RE-MEASUREMENT of pass 2 (the leaf row read x1.14 CPU on x1.03 instructions; the importers-open row cannot go green on this exhibit), not the final seal; the e121 state is left where pass 2 restored it
export VILAN_SEAL_PERF_ONLY=1
cp /home/reed/code/vilan-lang/proposals/scripts/integration/sweeps/order55/e121-state-pre-seal.json "$HOME/.vilan/perf-verdicts/e121-state.json"
exec bash /home/reed/code/vilan-lang/proposals/scripts/integration/seal.sh
