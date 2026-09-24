#!/bin/sh
# Re-runs every papers-41 probe over a SCRATCH copy (a `vilan build` writes
# beside its source). Usage: run_probes.sh [scratch-dir]  — prints one block per
# probe: the command, then the compiler's or the program's output.
# Toolchain on record: vilan 0.40.0 (1265ea5d3).
set -u
export PATH="$HOME/.cargo/bin:$HOME/.nvm/versions/node/v24.2.0/bin:$PATH"
HERE="$(cd "$(dirname "$0")" && pwd)"
SCRATCH="${1:-$(mktemp -d)}"
mkdir -p "$SCRATCH"
cp "$HERE"/*.vl "$SCRATCH"/
cd "$SCRATCH" || exit 1
vilan --version
for f in a122_*.vl; do
	echo "=== vilan run $f"
	vilan run "$f" 2>&1 | grep -v '^ *│ *$' | head -12
done
# Native: the mapped tuple and the 2-arity hand form on the rust backend.
for f in a122_01_hand_divorce2.vl a122_06_comprehension_mapped_to_mapped.vl; do
	echo "=== vilan run --backend rust $f"
	vilan run --backend rust "$f" 2>&1 | grep -v '^ *│ *$' | head -4
done
# F27 R3: every probe checked under both platform legs.
for f in f27_*.vl; do
	for p in node browser; do
		echo "=== vilan check --platform $p $f"
		vilan check --platform "$p" "$f" 2>&1 | grep -v '^ *│ *$' | head -12
	done
done
