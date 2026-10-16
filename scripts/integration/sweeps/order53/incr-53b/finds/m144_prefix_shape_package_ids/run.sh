#!/bin/bash
# incr-53b find (Order 53): after M144 std's ids are a function of the std set in BOTH
# shapes, but a PACKAGE item's id still differs between the canonical world and the
# std-prefix world: the std-only prefix world resolves std (which mints entities)
# before the package's nodes mint, and the canonical path mints the package's nodes
# before its one resolve. The native backend names items `name_<id>`, so the same
# program emits different Rust under VILAN_STD_PREFIX=on and =off while the JS is
# byte-identical.
#   ./run.sh            (uses the `vilan` on PATH; copies itself to a temp dir)
set -e
here=$(cd "$(dirname "$0")" && pwd)
work=$(mktemp -d)
cp -r "$here/pkg" "$work/"
cd "$work/pkg"
VILAN_STD_PREFIX=off VILAN_WORLD_CACHE=off vilan build --stdout --backend rust src/main.vl > off.rs
VILAN_STD_PREFIX=on VILAN_WORLD_CACHE=off vilan build --stdout --backend rust src/main.vl > on.rs
echo "std item (basename), off vs on:"
grep -o 'fn basename_[0-9]*' off.rs on.rs
echo "package item (two), off vs on:"
grep -o 'fn two_[0-9]*' off.rs on.rs
rm -rf "$work"
