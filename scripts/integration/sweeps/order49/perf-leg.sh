#!/usr/bin/env bash
# perf-leg.sh — seal.sh's perf leg alone (Order 49): the base kolt comes from $VILAN_PERF_KOLT_DIR at $VILAN_PERF_KOLT_COMMIT
# (a scratch CLONE COPY where the integrator committed the owner's working tree), the tip from $VILAN_PERF_TIP_KOLT.
set -u
S=$(cd "$(dirname "$0")/../.." && pwd)
W=${VILAN_INTEGRATION:-$HOME/code/vilan-lang/vilan/.claude/worktrees/integration}
cd "$W" || exit 1
export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$HOME/.nvm/versions/node/v24.2.0/bin:$PATH"
tip=$(git rev-parse --short=8 HEAD); echo "tip=$tip loadavg=$(cut -d' ' -f1-3 /proc/loadavg)"
cargo build -q --release -p vilan-cli -p vilan-lsp > "$S/perf-build-$tip.log" 2>&1; pb=$?
commit="${VILAN_PERF_KOLT_COMMIT:?}"; kolt="${VILAN_PERF_KOLT_DIR:?}"
for _ in $(seq 1 90); do awk '{exit !($1 < 1.5)}' /proc/loadavg && break; sleep 10; done; echo "perf leg starts at loadavg=$(cut -d' ' -f1-3 /proc/loadavg)"
scen=(--scenario "leaf keystroke" --scenario "leaf keystroke + pause" --scenario "shared.vl keystroke" --scenario "model.vl keystroke" --scenario "model.vl keystroke, importers open" --scenario "css keystroke" --scenario "parse break")
tip_kolt=(--tip-kolt "${VILAN_PERF_TIP_KOLT:?}"); tip_src=(--source "$VILAN_PERF_TIP_KOLT")
lsp_json=()
python3 scripts/lsp-latency.py --kolt "$kolt" --commit "$commit" --runs 5 --lsp "${VILAN_PERF_LSP_BASE:-$HOME/.vilan/bin/vilan-lsp}" "${scen[@]}" --json "$S/lsp-base-$tip.json" > "$S/lsp-base-$tip.log" 2>&1 &&
python3 scripts/lsp-latency.py "${tip_src[@]}" --runs 5 --lsp "$W/target/release/vilan-lsp" "${scen[@]}" --json "$S/lsp-tip-$tip.json" > "$S/lsp-tip-$tip.log" 2>&1 &&
lsp_json=(--lsp-json "$S/lsp-base-$tip.json" "$S/lsp-tip-$tip.json")
adv=(); [ -n "${VILAN_PERF_ADVANCE:-}" ] && adv=(--advance)
python3 scripts/perf_gate.py seal --class reference --tip "$W/target/release/vilan" --tip-std "$W/vilan/std" \
    --base "${VILAN_PERF_BASE:-$HOME/.vilan/bin/vilan}" --kolt "$kolt" --commit "$commit" "${tip_kolt[@]}" --runs 5 \
    --sha "$(git rev-parse HEAD)" "${lsp_json[@]}" "${adv[@]}" > "$S/perf-$tip.log" 2>&1; pf=$?
[ $pb -ne 0 ] && pf=$pb; grep -E "T3 kolt|T2 VERDICT|PERF VERDICT|REFUSED|OWNER|RED|different sources|wrote" "$S/perf-$tip.log"; echo "perf exit=$pf"
