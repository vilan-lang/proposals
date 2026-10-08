#!/usr/bin/env bash
# A155 probes: each case on the SSR (node) leg via `vilan run` and on the client
# (browser) leg built with --platform browser and run under stub.mjs.
# Usage: run.sh <vilan-binary> <scratch-dir>
set -u
V=${1:?vilan}; S=${2:?scratch}
here=$(cd "$(dirname "$0")" && pwd)
mkdir -p "$S" && cp "$here"/*.vl "$here"/stub.mjs "$S"/ && cd "$S"
for f in a*.vl; do
  n=${f%.vl}
  echo "== $n"
  out=$("$V" run "$f" 2>&1)
  echo "  warnings: $(grep -c '^Warning: this element' <<<"$out")"
  echo "  ssr: $(grep -E '^<div' <<<"$out" | tail -1)"
  grep -E '^Error' <<<"$out" | head -2 | sed 's/^/  /'
  "$V" build --platform browser "b_$f" >/dev/null 2>"b_$n.err" || { echo "  client: BUILD FAILED"; head -5 "b_$n.err"; continue; }
  echo "  client:"; node stub.mjs "./b_$n.js" 2>&1 | sed 's/^/    /' | head -6
done
