#!/usr/bin/env bash
# I5 S2 (index-42): steps 5 and 6 of run_s2.sh on their own, over the TREE a
# previous run left in <scratch>, the corpus goldens built IN PARALLEL (a
# loaded box timed the serial loop out). Same outputs as run_s2.sh's tail.
#
#   measure_s2.sh <vilan worktree> <scratch dir>
set -euo pipefail
WORKTREE="$(cd "${1:?usage: measure_s2.sh <vilan worktree> <scratch dir>}" && pwd)"
SCRATCH="${2:?usage: measure_s2.sh <vilan worktree> <scratch dir>}"
TREE="$SCRATCH/tree"
BASE="$SCRATCH/base"
OUT="$SCRATCH/out"
VILAN="${S2_TARGET:-$WORKTREE/target/s2}/debug/vilan"
JOBS="${JOBS:-6}"

for formatted in vilan/std vilan/test vilan/macro_std; do
	VILAN_STD="$TREE/vilan/std" "$VILAN" fmt "$TREE/$formatted" > "$OUT/fmt.log" 2>&1 \
		|| { echo "--- fmt declined in $formatted:"; grep declined "$OUT/fmt.log"; } | tee -a "$OUT/summary.txt"
done
GOLDENS="$SCRATCH/goldens"
rm -rf "$GOLDENS" && mkdir -p "$GOLDENS"
cp -r "$TREE/vilan/test/." "$GOLDENS/"
rm -f "$OUT"/golden-*.diff
build_one() {
	local source="$1" name
	name="$(basename "$source" .vl)"
	[ -f "$BASE/vilan/test/$name.mjs" ] || return 0
	if VILAN_STD="$TREE/vilan/std" "$VILAN" build "$source" > /dev/null 2> "$GOLDENS/$name.err"; then
		if cmp -s "$GOLDENS/$name.mjs" "$BASE/vilan/test/$name.mjs"; then
			printf 'SAME\t%s\n' "$name"
		else
			printf 'MOVED\t%s\n' "$name"
			diff "$BASE/vilan/test/$name.mjs" "$GOLDENS/$name.mjs" > "$OUT/golden-$name.diff" || true
		fi
	else
		printf 'FAILED\t%s\t%s\n' "$name" "$(grep -m1 '^Error' "$GOLDENS/$name.err" | cut -c1-160)"
	fi
}
export -f build_one
export GOLDENS BASE TREE VILAN OUT
ls "$GOLDENS"/*.vl | xargs -P "$JOBS" -I{} bash -c 'build_one "$@"' _ {} | sort > "$OUT/goldens-all.tsv"
grep -v '^SAME' "$OUT/goldens-all.tsv" > "$OUT/goldens.tsv" || true
echo "--- corpus goldens: $(grep -c '^SAME' "$OUT/goldens-all.tsv") byte-identical, $(grep -c '^MOVED' "$OUT/goldens-all.tsv") moved, $(grep -c '^FAILED' "$OUT/goldens-all.tsv") failed to build" | tee -a "$OUT/summary.txt"
# A moved golden must still PRINT what it printed: each one run under node,
# base and migrated, stdout compared (a program that does not run under node —
# a browser leg — is reported as such, not as a pass).
: > "$OUT/golden-outputs.tsv"
for name in $(grep '^MOVED' "$OUT/goldens-all.tsv" | cut -f2); do
	base_out="$(cd "$BASE/vilan/test" && timeout 60 node "$name.mjs" 2>&1)" && base_ok=1 || base_ok=0
	tree_out="$(cd "$GOLDENS" && timeout 60 node "$name.mjs" 2>&1)" && tree_ok=1 || tree_ok=0
	if [ "$base_ok$tree_ok" != 11 ]; then
		printf 'DID-NOT-RUN\t%s\t%s%s\n' "$name" "$base_ok" "$tree_ok" >> "$OUT/golden-outputs.tsv"
	elif [ "$base_out" = "$tree_out" ]; then
		printf 'SAME-OUTPUT\t%s\n' "$name" >> "$OUT/golden-outputs.tsv"
	else
		printf 'OUTPUT-DIFFERS\t%s\n' "$name" >> "$OUT/golden-outputs.tsv"
		diff <(echo "$base_out") <(echo "$tree_out") > "$OUT/output-$name.diff" || true
	fi
done
echo "--- moved goldens' output under node: $(grep -c '^SAME-OUTPUT' "$OUT/golden-outputs.tsv") same, $(grep -c '^OUTPUT-DIFFERS' "$OUT/golden-outputs.tsv") differ, $(grep -c '^DID-NOT-RUN' "$OUT/golden-outputs.tsv") did not run" | tee -a "$OUT/summary.txt"
examples_ok=0
examples_failed=0
: > "$OUT/examples.tsv"
for example in "$TREE"/vilan/examples/*/; do
	name="$(basename "$example")"
	if ( cd "$example" && VILAN_STD="$TREE/vilan/std" "$VILAN" check > "$OUT/example-$name.log" 2>&1 ); then
		examples_ok=$((examples_ok + 1))
	else
		examples_failed=$((examples_failed + 1))
		printf 'FAILED\t%s\t%s\n' "$name" "$(grep -c '^Error' "$OUT/example-$name.log")" >> "$OUT/examples.tsv"
	fi
done
echo "--- examples: $examples_ok check clean, $examples_failed refused (examples.tsv)" | tee -a "$OUT/summary.txt"
( cd "$SCRATCH" && git diff --no-index --stat=200 base/vilan tree/vilan > "$OUT/s2.stat" || true )
( cd "$SCRATCH" && git diff --no-index base/vilan tree/vilan > "$OUT/s2.diff" || true )
( cd "$SCRATCH" && diff -ru -x examples -x target base/crates tree/crates > "$OUT/s2-compiler.diff" || true )
tail -1 "$OUT/s2.stat" | tee -a "$OUT/summary.txt"
