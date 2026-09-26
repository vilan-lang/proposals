#!/usr/bin/env bash
# Usage: slope.sh <variant> [low] [high]  -> per-call Ir slope under node --jitless
set -euo pipefail
export PATH="$HOME/.cargo/bin:$HOME/.nvm/versions/node/v24.2.0/bin:$PATH"
cd "$(dirname "$0")"
variant=$1; low=${2:-20}; high=${3:-220}
ir() {
  local out=cg.$variant.$1.out
  M87_VARIANT=$variant M87_CALLS=$1 valgrind --tool=callgrind --callgrind-out-file=$out node --jitless harness.mjs >/dev/null 2>cg.$variant.$1.err
  grep -E '^(summary|totals):' $out | head -1 | awk '{print $2}'
}
a=$(ir $low); b=$(ir $high)
echo "variant=$variant low=$low Ir=$a high=$high Ir=$b slope=$(( (b - a) / (high - low) )) loadavg=$(cut -d' ' -f1-3 /proc/loadavg)"
