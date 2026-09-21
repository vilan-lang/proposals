#!/bin/bash
# Per-wave Ir by SLOPE: build the bench at two wave counts and take the
# difference, so node's startup cancels out. usage: measure-ir.sh <label>
set -u
W=/home/reed/code/vilan-lang/vilan/.claude/worktrees/reactive-38
S=/tmp/claude-1000/-home-reed-code-vilan-lang/ae2b0352-743d-4446-aedf-1f52ad55831a/scratchpad/reactive-38
LABEL="$1"
for n in 5000 25000; do
    d="$S/bench-$LABEL-$n"
    rm -rf "$d"; cp -r "$S/bench" "$d"; rm -f "$d"/app.mjs
    sed -i "s/round <= 20000/round <= $n/; s/waves=20000/waves=$n/" "$d/app.vl"
    "$W/target/debug/vilan" build "$d" > /dev/null 2>&1 || { echo "build failed $n"; exit 1; }
done
echo "loadavg: $(cat /proc/loadavg)"
for mode in jitless jit; do
    for n in 5000 25000; do
        d="$S/bench-$LABEL-$n"
        flags=""
        [ "$mode" = jitless ] && flags="--jitless"
        out="$S/cg-$LABEL-$mode-$n.out"
        ir=$( (cd "$d" && valgrind --tool=callgrind --callgrind-out-file="$out" node $flags app.mjs > "$S/run-$LABEL-$mode-$n.stdout" 2> "$S/run-$LABEL-$mode-$n.stderr"); grep -o 'I *refs: *[0-9,]*' "$S/run-$LABEL-$mode-$n.stderr" | tr -d ' ,' | sed 's/Irefs://')
        echo "$LABEL $mode n=$n Ir=$ir stdout=$(cat "$S/run-$LABEL-$mode-$n.stdout")"
    done
done
