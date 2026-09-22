#!/usr/bin/env bash
# I5's WIRE proof (Order 40, lane papers-40) — three runs of i5_wire_patch.vl
# over three standard libraries, byte-compared.
#
#   A  std as it is                     `Delta::Insert(K, T, i32)`
#   B  the naive migration              `Delta::Insert(K, T, u53)`, natural Wire impl
#   C  the width-pinned migration       `Delta::Insert(K, T, u53)`, `i32_value` wire width
#
# B is the control: it must MOVE the frame, or C proving the frame did not move
# is vacuous.
#
# Usage: i5_wire_flip.sh <worktree> <scratch-dir>
#   <worktree>  a vilan checkout (its vilan/std + vilan/macro_std are copied,
#               never edited) with target/debug/vilan already built
set -euo pipefail

WORKTREE="${1:?usage: i5_wire_flip.sh <worktree> <scratch>}"
SCRATCH="${2:?usage: i5_wire_flip.sh <worktree> <scratch>}"
PROBE="$(cd "$(dirname "$0")" && pwd)/i5_wire_patch.vl"
VILAN="$WORKTREE/target/debug/vilan"

rm -rf "$SCRATCH/wire"
mkdir -p "$SCRATCH/wire/run"
cp "$PROBE" "$SCRATCH/wire/run/"

fresh_std() {
	rm -rf "$SCRATCH/wire/tc"
	mkdir -p "$SCRATCH/wire/tc"
	cp -r "$WORKTREE/vilan/std" "$SCRATCH/wire/tc/std"
	cp -r "$WORKTREE/vilan/macro_std" "$SCRATCH/wire/tc/macro_std"
}

run() {
	( cd "$SCRATCH/wire/run" && VILAN_STD="$SCRATCH/wire/tc/std" "$VILAN" run i5_wire_patch.vl )
}

# --- A: std as it is ---------------------------------------------------------
fresh_std
echo "=== A  Delta::Insert(K, T, i32) — std as it is"
run | tee "$SCRATCH/wire/a.txt"

# --- B: the position becomes u53, its own Wire impl decides the width --------
fresh_std
python3 - "$SCRATCH/wire/tc/std" <<'PY'
import sys, pathlib
root = pathlib.Path(sys.argv[1], "src")
wire = root / "wire.vl"
text = wire.read_text()
text = text.replace("\tInsert(K, T, i32),", "\tInsert(K, T, u53),", 1)
text = text.replace("let index = i32::rebuild(deserializer);",
                    "let index = u53::rebuild(deserializer);", 1)
wire.write_text(text)
# The nine call sites the flip breaks (the cascade this probe also measures).
rpc = root / "rpc.vl"
text = rpc.read_text()
text = text.replace("Delta::Insert(key, element, at)",
                    "Delta::Insert(key, element, at.as_u53())")
text = text.replace("Delta::Insert(key_of(element), element, index)",
                    "Delta::Insert(key_of(element), element, index.as_u53())")
text = text.replace("Delta::Insert(element.key, element.value, at + offset)",
                    "Delta::Insert(element.key, element.value, (at + offset).as_u53())")
text = text.replace("mut bounded = index;", "mut bounded = index.as_i32();")
rpc.write_text(text)
PY
echo "=== B  Delta::Insert(K, T, u53) — the naive migration (CONTROL: must move)"
run | tee "$SCRATCH/wire/b.txt"

# --- C: the same u53 position, wire width pinned at i32 ----------------------
python3 - "$SCRATCH/wire/tc/std" <<'PY'
import sys, pathlib
wire = pathlib.Path(sys.argv[1], "src", "wire.vl")
text = wire.read_text()
text = text.replace("\t\t\t\tindex.describe(serializer);",
                    "\t\t\t\tserializer.i32_value(index.as_i32());", 1)
text = text.replace("let index = u53::rebuild(deserializer);",
                    "let index = deserializer.i32_value().as_u53();", 1)
wire.write_text(text)
PY
echo "=== C  Delta::Insert(K, T, u53) with the i32 wire width"
run | tee "$SCRATCH/wire/c.txt"

echo
echo "=== A vs B (the control — expect a difference)"
diff "$SCRATCH/wire/a.txt" "$SCRATCH/wire/b.txt" && echo "NO DIFFERENCE — the control is vacuous, stop"
echo "=== A vs C (the claim — expect no difference)"
if diff "$SCRATCH/wire/a.txt" "$SCRATCH/wire/c.txt"; then
	echo "BYTE-IDENTICAL: the frame did not move"
else
	echo "MOVED — the claim is false"
	exit 1
fi
