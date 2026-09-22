#!/usr/bin/env bash
# I5's contract-hash probe (Order 40, lane papers-40). Two questions:
#
#   1. Does respelling an rpc parameter's index type move the SERVICE's
#      contract hash?  (surface = `parameter.type_.render()`, the type AS
#      WRITTEN — rpc.vl's `service_surface`)
#   2. Does changing the width of a position INSIDE a std frame type
#      (`Delta::Insert`'s index) move it?
#
# Usage: i5_contract_hash.sh <worktree> <scratch-dir>
set -euo pipefail

WORKTREE="${1:?usage: i5_contract_hash.sh <worktree> <scratch>}"
SCRATCH="${2:?usage: i5_contract_hash.sh <worktree> <scratch>}"
PROBE="$(cd "$(dirname "$0")" && pwd)/i5_contract_hash.vl"
VILAN="$WORKTREE/target/debug/vilan"

rm -rf "$SCRATCH/hash"
mkdir -p "$SCRATCH/hash/run"
cp "$PROBE" "$SCRATCH/hash/run/"

fresh_std() {
	rm -rf "$SCRATCH/hash/tc"
	mkdir -p "$SCRATCH/hash/tc"
	cp -r "$WORKTREE/vilan/std" "$SCRATCH/hash/tc/std"
	cp -r "$WORKTREE/vilan/macro_std" "$SCRATCH/hash/tc/macro_std"
}

run() {
	( cd "$SCRATCH/hash/run" && VILAN_STD="$SCRATCH/hash/tc/std" "$VILAN" run i5_contract_hash.vl )
}

echo "--- 1. the rpc parameter's written type"
fresh_std
for spelling in i32 u53 i53 u32 i16; do
	sed -i "s/fun page(self, at: [a-z0-9]*)/fun page(self, at: $spelling)/" \
		"$SCRATCH/hash/run/i5_contract_hash.vl"
	printf '%s\t' "$spelling"
	run
done
sed -i "s/fun page(self, at: [a-z0-9]*)/fun page(self, at: i32)/" \
	"$SCRATCH/hash/run/i5_contract_hash.vl"

echo "--- 2. a position INSIDE a std frame type (Delta::Insert's index)"
printf 'std-as-is\t'
run
python3 - "$SCRATCH/hash/tc/std" <<'PY'
import sys, pathlib
root = pathlib.Path(sys.argv[1], "src")
wire = root / "wire.vl"
text = wire.read_text()
text = text.replace("\tInsert(K, T, i32),", "\tInsert(K, T, u53),", 1)
text = text.replace("let index = i32::rebuild(deserializer);",
                    "let index = u53::rebuild(deserializer);", 1)
wire.write_text(text)
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
printf 'delta-index-u53\t'
run
