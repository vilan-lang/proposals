#!/usr/bin/env bash
# C15 probes: JS (the reference) against native, with the boxed count and the
# leak census. Usage: run.sh <vilan-binary> <scratch-dir>
set -u
V=${1:?vilan}; S=${2:?scratch}
here=$(cd "$(dirname "$0")" && pwd)
mkdir -p "$S" && cp "$here"/c*.vl "$S"/ && cd "$S"
for f in c*.vl; do
  n=${f%.vl}
  js=$("$V" run "$f" 2>&1 | grep -v '^Warning' | tr '\n' ' ')
  boxed=$(VILAN_NATIVE_REPORT_BOXED=1 "$V" build --backend rust "$f" 2>&1 | grep -oE 'boxed-bindings=[0-9]+|^error\[E[0-9]+\]|^Error: .{0,120}' | head -2 | tr '\n' ' ')
  nat=$(VILAN_NATIVE_LEAK_CENSUS=1 "$V" run --backend rust "$f" 2>&1 | grep -vE 'Compiling|Finished|Running|^warning|^ *\||^ *-->|^ *= |^$' | tail -4 | tr '\n' ' ')
  echo "$n | js: $js | $boxed | native: $nat"
done
