#!/bin/bash
# usage: run.sh <kolt copy dir>  — throwaway server dir, seed, measure
export PATH="$HOME/.nvm/versions/node/v24.2.0/bin:$PATH"
here="$(cd "$(dirname "$0")" && pwd)"
copy="$(cd "$1" && pwd)"
work="$(mktemp -d -p "$here")"
cp -r "$copy/dist" "$work/dist"
cd "$work"
node dist/server.mjs > server.log 2>&1 &
server=$!
trap 'kill $server 2>/dev/null; rm -rf "$work"' EXIT
for i in $(seq 50); do grep -q "kolt:" server.log && break; sleep 0.2; done
node "$here/seed.js" "$work/state.json" || { cat server.log; exit 1; }
node "$here/measure.js" "$work/dist" "$work/state.json"
