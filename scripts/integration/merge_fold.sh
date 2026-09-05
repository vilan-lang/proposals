#!/usr/bin/env bash
# merge_fold.sh <lane> <allow-edit list or -> <nextest-spec>... — merge_lane, then fold conflicted
# TEST files by function name, commit, gate, push. Stops (exit 3) on any non-test conflict or a
# test module conflict; stops (exit 6) on a red gate WITHOUT pushing — chain the next merge with &&.
set -u
S=$(cd "$(dirname "$0")" && pwd)
W=${VILAN_INTEGRATION:-$HOME/code/vilan-lang/vilan/.claude/worktrees/integration}
lane=$1; allow=$2; shift 2
cd "$W" || exit 1
bash "$S/merge_lane.sh" "$lane" "$@" > "$S/merge-$lane.log" 2>&1; m=$?
grep -E 'merge exit|changelog:|ledger:|rs:|committed|pushed|UNRESOLVED|Summary|FAIL|drift' "$S/merge-$lane.log" | head -14
if [ $m = 0 ]; then echo "$lane: merged, gated and pushed"; exit 0; fi
if [ $m != 3 ]; then echo "$lane: merge_lane exit $m — STOP"; exit $m; fi
uu=$(git diff --name-only --diff-filter=U); echo "UU: $uu"
base=$(git merge-base HEAD "origin/$lane"); ok=1
for f in $uu; do
  case "$f" in
    crates/*/tests/*) if [ "$allow" = "-" ]; then python3 "$S/fold_tests_by_name.py" "$f" "$base" "origin/$lane" || ok=0; else python3 "$S/fold_tests_by_name.py" "$f" "$base" "origin/$lane" --allow-edit "$allow" || ok=0; fi ;;
    *) echo "NON-TEST CONFLICT: $f"; ok=0 ;;
  esac
done
[ $ok = 1 ] || { echo "$lane: hand fold needed — STOP"; exit 3; }
git add $uu && test -z "$(git diff --name-only --diff-filter=U)" && git commit -q --no-edit && echo "committed $(git rev-parse --short=8 HEAD)" || exit 4
cargo build -q -p vilan-cli || exit 5
for spec in "$@"; do log="$S/gate-$lane-$(echo "$spec" | tr -c 'a-z0-9' '_' | cut -c1-40).log"; echo "== gate: $spec"; eval "cargo nextest run $spec" > "$log" 2>&1; r=$?; tail -1 "$log"; [ $r = 0 ] || { echo "$lane: gate failed ($spec) — NOT pushed"; exit 6; }; done
cargo nextest run -p vilan-cli --test release_scripts > "$S/gate-$lane-release.log" 2>&1 || { echo "$lane: release_scripts failed — NOT pushed"; exit 6; }
cargo fmt --all --check || { echo "$lane: fmt drift — NOT pushed"; exit 6; }
git push -q origin next && echo "$lane: pushed $(git rev-parse --short=8 HEAD)"
