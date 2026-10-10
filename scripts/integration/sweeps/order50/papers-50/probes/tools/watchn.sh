#!/bin/bash
# usage: watchn.sh <projdir> <file-to-touch> <n-touches> [check-arg]
dir=$1; f=$2; n=$3; arg=${4:-.}
cd $dir
python3 /home/reed/code/vilan-lang/vilan/.claude/worktrees/integration/scripts/perf_count.py --json -- timeout -s INT $((8 + 6*n)) vilan check --watch $arg > /tmp/claude-1000/-home-reed-code-vilan-lang/89336be2-ed61-4826-b9ee-21d5898255eb/scratchpad/papers-50/runs/watch-last.json 2>/dev/null &
sleep 6
for i in $(seq 1 $n); do echo "// t$i" >> $f; sleep 6; done
wait
tail -1 /tmp/claude-1000/-home-reed-code-vilan-lang/89336be2-ed61-4826-b9ee-21d5898255eb/scratchpad/papers-50/runs/watch-last.json
