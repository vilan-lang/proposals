#!/usr/bin/env bash
# E227 probes: the full type each pipeline node renders as today (via a
# deliberate annotation mismatch), and whether `~` lexes anywhere.
# Usage: run_all.sh <scratch-dir>   (copies the probes there; never builds in place)
set -u
export PATH=$HOME/.cargo/bin:$HOME/.nvm/versions/node/v24.2.0/bin:$PATH
here=$(cd "$(dirname "$0")" && pwd)
scratch=${1:?scratch dir}
mkdir -p "$scratch" && cp "$here"/*.vl "$scratch"/
vilan --version
for f in tilde tilde2 nodes nodes2 nodes3 nodes5; do
  echo "== $f.vl"
  (cd "$scratch" && vilan check "$f.vl" 2>&1 | grep '^Error')
done
