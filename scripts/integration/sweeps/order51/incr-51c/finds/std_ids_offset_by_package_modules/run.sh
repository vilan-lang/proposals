#!/bin/bash
# incr-51c find (Order 51): after B603's std-first order (P0), std's MODULE NODES
# mint before any package module's, but std's WALK ids still follow EVERY module
# node of the program - the drain registers all modules (std, dependencies,
# package) before any walk - so a std item's entity id moves with the number of
# package modules. Here the same std set (std::path) gives `basename` Id(N) in a
# single-file program and Id(N+2) in a package with two sibling modules.
#   ./run.sh            (uses the `vilan` on PATH; copies itself to a temp dir)
set -e
here=$(cd "$(dirname "$0")" && pwd)
work=$(mktemp -d)
cp -r "$here/single" "$here/pkg" "$work/"
cd "$work"
vilan check -d single/prog.vl >/dev/null
(cd pkg && vilan check -d . >/dev/null)
echo "single: $(grep -o 'basename": Id([0-9]*)' single/prog.analyze.out | head -1)"
echo "pkg:    $(grep -o 'basename": Id([0-9]*)' pkg/src/main.analyze.out | head -1)"
rm -rf "$work"
