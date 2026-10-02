#!/usr/bin/env bash
# performance-gates.md §1's probe: callgrind instruction counts (Ir) for `vilan check .`,
# repeated, to measure the run-to-run spread of the deterministic metric and what one
# callgrind run costs in wall time (the gate's price).
#   callgrind_runs.sh VILAN OUTDIR RUNS SUBJECT_DIR...
# Prints: subject, run, Ir, wall seconds of the callgrind run, the loadavg.
set -u
vilan=$1; out=$2; runs=$3; shift 3
mkdir -p "$out"
for ((r = 0; r < runs; r++)); do
  for s in "$@"; do
    name=$(basename "$s")
    start=$(date +%s.%N)
    (cd "$s" && valgrind --tool=callgrind --callgrind-out-file="$out/cg.$name.$r" "$vilan" check . \
        > /dev/null 2> "$out/cg.$name.$r.stderr")
    end=$(date +%s.%N)
    ir=$(grep -E "^summary:|^totals:" "$out/cg.$name.$r" | head -1 | awk '{print $2}')
    echo "$name,$r,$ir,$(awk -v a="$start" -v b="$end" 'BEGIN{printf "%.1f", b-a}'),$(cut -d' ' -f1 /proc/loadavg)"
  done
done
