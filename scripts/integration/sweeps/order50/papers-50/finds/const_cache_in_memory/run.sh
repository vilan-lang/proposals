#!/bin/bash
# M135 repro (papers-50): S4's const cache is content-keyed and id-free
# (const_cache.rs: "the program IS the key ... whatever their entity ids") but
# lives in process memory only, so every cold `vilan check` of kolt's client
# re-evaluates every const site: two checks in a row both report the same
# misses and both pay the const pass.
#   ./run.sh <kolt-copy-with-src/lucide-and-src/search-dict>
set -e
cd "$1"
for i in 1 2; do
  VILAN_PHASE_TIMING=passes VILAN_COUNTERS=1 vilan check src/client.vl 2>&1 \
    | grep -oE "const-pass [0-9.]+ms/[0-9.]+cpu|const-interp [0-9.]+ms/[0-9.]+cpu|const-hits=[0-9]+ const-misses=[0-9]+" | tr '\n' ' '
  echo
done
