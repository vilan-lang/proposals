#!/usr/bin/env bash
# I5 S2, PREPARED (Order 41, lane index-41) — the whole migration run over a
# SCRATCH copy of a vilan tree, measured, and diffed. Nothing here touches the
# tree it reads: the worktree is `git archive`d twice (a pristine BASE and the
# TREE the migration runs on) and every build lands under <scratch>.
#
#   run_s2.sh <vilan worktree> <scratch dir>
#   STOP_AFTER=codemod run_s2.sh …   (stop after step 3 — how hand.patch is made:
#                                     edit a copy of <scratch>/codemod/vilan and
#                                     diff it against the snapshot)
#
# Steps (proposal/index-type.md §8.1, §9 S2):
#   1. compiler.patch — S2's compiler half: the subscript's expectation becomes
#      `usize` and S1's two-type admission is deleted.
#   2. signatures   — the 105 std positions of the census verdict table, found by
#      parse and respelled `usize` (i5_s2_codemod.rs).
#   3. fix          — the fixed-point loop over the compiler's own diagnostics:
#      E218's named conversions, and the binary-operator refusals between
#      `usize` and another integer width, over every std module on both
#      platforms and every corpus program.
#   4. hand.patch   — the seven `-1` sentinels and the eight `>= 0` loops (§3.4,
#      §3.5) and whatever residue NOTES.md names, by hand. Then the fix loop
#      once more, since a hand edit can expose a conversion.
#   5. measure      — `vilan fmt`; every corpus golden rebuilt with the scratch
#      binary against the scratch std and byte-compared with the base golden;
#      the split goldens the same way; every example built; the residue.
#   6. s2.diff      — base vs tree, sources only.
set -euo pipefail

WORKTREE="$(cd "${1:?usage: run_s2.sh <vilan worktree> <scratch dir>}" && pwd)"
SCRATCH="${2:?usage: run_s2.sh <vilan worktree> <scratch dir>}"
HERE="$(cd "$(dirname "$0")" && pwd)"
VERDICTS="$HERE/../../order40/papers-40/i5-std-index-sites.tsv"
TREE="$SCRATCH/tree"
BASE="$SCRATCH/base"
TARGET="${S2_TARGET:-$WORKTREE/target/s2}"
OUT="$SCRATCH/out"

rm -rf "$TREE" "$BASE" "$OUT"
mkdir -p "$TREE" "$BASE" "$OUT"
git -C "$WORKTREE" archive "${S2_REV:-HEAD}" | tar -x -C "$TREE"
git -C "$WORKTREE" archive "${S2_REV:-HEAD}" | tar -x -C "$BASE"
echo "base: $(git -C "$WORKTREE" rev-parse --short "${S2_REV:-HEAD}")" | tee "$OUT/summary.txt"

# 1. the compiler half
( cd "$TREE" && patch -p1 --no-backup-if-mismatch < "$HERE/compiler.patch" )
mkdir -p "$TREE/crates/vilan-core/examples"
cp "$HERE/i5_s2_codemod.rs" "$TREE/crates/vilan-core/examples/"
( cd "$TREE" && CARGO_TARGET_DIR="$TARGET" cargo build -q -p vilan-cli --bin vilan \
	&& CARGO_TARGET_DIR="$TARGET" cargo build -q -p vilan-core --example i5_s2_codemod )
VILAN="$TARGET/debug/vilan"
CODEMOD="$TARGET/debug/examples/i5_s2_codemod"

# 2. the signatures
"$CODEMOD" signatures "$VERDICTS" "$TREE/vilan/std/src" > "$OUT/signatures.tsv" 2> "$OUT/signatures.err"
cat "$OUT/signatures.err" | tee -a "$OUT/summary.txt"
# What the signatures pass alone wrote — the tree `pre.patch` is made against.
if [ "${STOP_AFTER:-}" = signatures ]; then
	rm -rf "$SCRATCH/signatures" && mkdir -p "$SCRATCH/signatures" && cp -r "$TREE/vilan" "$SCRATCH/signatures/"
	echo "--- stopped after the signatures (STOP_AFTER=signatures); snapshot in $SCRATCH/signatures" | tee -a "$OUT/summary.txt"
	exit 0
fi

# 2b. pre.patch (index-42, Order 42): the respellings a TYPE decides, made by
#     hand BEFORE the fix loop so the loop writes the conversions their new
#     boundaries need rather than conversions a later hand edit would take back
#     out. S4 — the positions not born `usize`: A112's `// I5` markers in
#     delta.vl and std::ui, `SeqOp`'s payloads, `RowStep`, `Delta::Insert`,
#     macro_std's `Arguments` and `indent` — and the census's misses:
#     `Enumerated`'s trait argument, annotated locals (compare.vl's counter,
#     markdown.vl's three `close`, document.vl's two insertion lists), and the
#     one place a delta SEQUENCE number becomes a POSITION (DeltaLog's
#     `trim`/`since`), converted once at that boundary.
if [ -s "$HERE/pre.patch" ]; then
	( cd "$TREE" && patch -p1 --no-backup-if-mismatch < "$HERE/pre.patch" ) > "$OUT/s4.log"
	echo "--- pre.patch: $(grep -c '^patching' "$OUT/s4.log") files" | tee -a "$OUT/summary.txt"
fi

# 3. the fixed-point loop. Entries: every std module on each platform (so no
#    std body is left unanalyzed), and every corpus program.
ENTRIES="$SCRATCH/entries"
rm -rf "$ENTRIES" && mkdir -p "$ENTRIES"
module_imports() {
	for file in "$@"; do
		local module
		module="$(basename "$file" .vl)"
		case "$module" in lib | prelude | web | null) continue ;; esac
		echo "import std::$module;"
	done
}
(
	cd "$TREE/vilan/std/src"
	{ module_imports ./*.vl process/*.vl; printf '\nfun main() {}\n'; } > "$ENTRIES/all_node.vl"
	{ module_imports ./*.vl browser/*.vl; printf '\nfun main() {}\n'; } > "$ENTRIES/all_browser.vl"
)
fix_round() {
	local label="$1"
	# std first, over the two all-module entries alone, to its fixed point;
	# then the corpus programs (their own code, and anything of std's only
	# they reach).
	"$CODEMOD" fix "$TREE/vilan/std" node "$ENTRIES/all_node.vl" \
		> "$OUT/fix-$label-std-node.tsv" 2> "$OUT/fix-$label-std-node.err"
	"$CODEMOD" fix "$TREE/vilan/std" browser "$ENTRIES/all_browser.vl" \
		> "$OUT/fix-$label-std-browser.tsv" 2> "$OUT/fix-$label-std-browser.err"
	# macro_std: the package every macro world compiles against, which no
	# program world ever walks — each of its files is its own entry.
	"$CODEMOD" fix "$TREE/vilan/std" node "$TREE"/vilan/macro_std/src/*.vl \
		> "$OUT/fix-$label-macro_std.tsv" 2> "$OUT/fix-$label-macro_std.err"
	"$CODEMOD" fix "$TREE/vilan/std" node "$TREE"/vilan/test/*.vl \
		> "$OUT/fix-$label-corpus.tsv" 2> "$OUT/fix-$label-corpus.err"
	echo "--- fix ($label)" | tee -a "$OUT/summary.txt"
	for leg in std-node std-browser macro_std corpus; do
		tail -1 "$OUT/fix-$label-$leg.err" | sed "s/^/$leg: /" | tee -a "$OUT/summary.txt"
	done
}
fix_round codemod
# What the codemod alone wrote — the tree `hand.patch` is made against.
rm -rf "$SCRATCH/codemod" && mkdir -p "$SCRATCH/codemod" && cp -r "$TREE/vilan" "$SCRATCH/codemod/"
if [ "${STOP_AFTER:-}" = codemod ]; then
	echo "--- stopped after the codemod (STOP_AFTER=codemod); snapshot in $SCRATCH/codemod" | tee -a "$OUT/summary.txt"
	exit 0
fi

# 4. by hand — against the codemod's output FORMATTED (index-42: hand.patch is
#    a diff from `vilan fmt`'s reprint, so the loop's layout is not in it).
for formatted in vilan/std vilan/macro_std vilan/test; do
	VILAN_STD="$TREE/vilan/std" "$VILAN" fmt "$TREE/$formatted" > /dev/null 2>&1 || true
done
if [ -s "$HERE/hand.patch" ]; then
	( cd "$TREE" && patch -p1 --no-backup-if-mismatch < "$HERE/hand.patch" ) > "$OUT/hand.log"
	echo "--- hand.patch: $(grep -c '^patching' "$OUT/hand.log") files" | tee -a "$OUT/summary.txt"
	# Two literals B389's law does not reach yet: a generic CONSTRUCTOR call's
	# literal argument inside a struct literal's field (`count =
	# Shared::new(0)` for a `Shared<usize>` field — refused as `Shared<i32>`).
	# The suffix is a bug report against §4 (Q5), filed; with that gap closed
	# this patch is dropped. LITERAL_GAPS=0 measures the tree without it.
	if [ "${LITERAL_GAPS:-1}" = 1 ]; then
		( cd "$TREE" && patch -p1 --no-backup-if-mismatch < "$HERE/b389-gap-literals.patch" ) > /dev/null
		echo "--- b389-gap-literals.patch applied (2 suffixes, the struct-field generic-call gap)" | tee -a "$OUT/summary.txt"
	fi
	fix_round after-hand
fi

# 5–6. measure — the corpus goldens in parallel, the examples, the diff
#      (measure_s2.sh; a loaded box timed the serial loop out).
if [ "${STOP_AFTER:-}" = fix ]; then
	echo "--- stopped after the fix rounds (STOP_AFTER=fix); measure with measure_s2.sh" | tee -a "$OUT/summary.txt"
	exit 0
fi
bash "$HERE/measure_s2.sh" "$WORKTREE" "$SCRATCH"
