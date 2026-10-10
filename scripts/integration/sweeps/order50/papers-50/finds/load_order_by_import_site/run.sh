#!/bin/bash
# B603 repro (papers-50): the same reachable module set loads in a different
# order, so the emitted module differs, when the ENTRY names a std module that a
# package module already imports. WO-1b says the load order is "a function only
# of WHICH modules are reachable"; here the set is identical (std::path is
# reached through pkg::a either way) and the order is not.
#   ./run.sh            (uses the `vilan` on PATH; copies itself to a temp dir)
set -e
here=$(cd "$(dirname "$0")" && pwd)
work=$(mktemp -d)
cp -r "$here/vilan.toml" "$here/src" "$work/"
cd "$work"
vilan build . >/dev/null
cp dist/main.mjs plain.mjs
sed -i '1i import std::path;' src/main.vl      # redundant: path is already reachable
vilan build . >/dev/null
cp dist/main.mjs redundant.mjs
if cmp -s plain.mjs redundant.mjs; then echo "IDENTICAL (fixed)"; else
  echo "DIFFER: a redundant std import moved pkg::a's declaration"; diff plain.mjs redundant.mjs || true; fi
node redundant.mjs
rm -rf "$work"
