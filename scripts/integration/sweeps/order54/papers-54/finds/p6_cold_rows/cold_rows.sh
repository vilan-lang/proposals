#!/bin/bash
# M157 / P6: cold `vilan check` in instructions, three shapes per subject:
#   off        - the canonical path (VILAN_STD_PREFIX=off)
#   on-nofile  - the prefix shape built in-process (no file): pays the closure parse (no index)
#                and the guard's 'everything' reach log - an UPPER bound on door A's cold cost
#   on-file    - the prefix shape over a loaded world file (warm cache dir)
export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$HOME/.nvm/versions/node/v24.2.0/bin:$PATH"
S=${SCRATCH:?set SCRATCH to a dir holding copies of the subjects (m157 = order53 incr-53b repro pkg, todo = vilan/examples/todo, kolt = a cp -r of kolt with src/lucide + src/search-dict)}
P=/home/reed/code/vilan-lang/vilan/.claude/worktrees/papers-54/scripts/perf_count.py
V=/home/reed/.cargo/bin/vilan
rm -rf $S/wc; mkdir -p $S/wc
out=$S/m157-cold-rows.txt; : > $out
for subj in "$@"; do
  for shape in off on-nofile on-file; do
    case $shape in
      off) envs=(--env VILAN_STD_PREFIX=off --env VILAN_WORLD_CACHE=off);;
      on-nofile) envs=(--env VILAN_STD_PREFIX=on --env VILAN_WORLD_CACHE=off);;
      on-file) envs=(--env VILAN_STD_PREFIX=on --env VILAN_WORLD_CACHE=$S/wc)
         (cd $S/$subj && VILAN_STD_PREFIX=on VILAN_WORLD_CACHE=$S/wc $V check . >/dev/null 2>&1);;
    esac
    for run in 1 2 3; do
      r=$(cd $S/$subj && python3 $P --json "${envs[@]}" -- $V check . 2>&1 | tail -1)
      echo "$subj $shape $run $r" >> $out
    done
  done
done
cat /proc/loadavg >> $out
