#!/usr/bin/env bash
# merge_lane.sh <lane> [nextest-spec ...] — merge origin/<lane> into the integration worktree with
# --no-commit, resolve CHANGELOG/ledger/rs mechanically, commit, build, gate, push. Exit 3 = files
# left unresolved (fold by hand or with merge_fold.sh), 6 = a gate failed (NOT pushed).
set -u
S=$(cd "$(dirname "$0")" && pwd)
W=${VILAN_INTEGRATION:-$HOME/code/vilan-lang/vilan/.claude/worktrees/integration}
lane=$1; shift
cd "$W" || exit 1
git fetch -q origin || exit 1
git merge --no-ff --no-commit "origin/$lane" >/dev/null 2>&1; echo "merge exit=$? (non-zero = conflicts to resolve)"
python3 "$S/changelog_union.py" "origin/$lane" || { echo "CHANGELOG needs a hand"; exit 2; }
python3 "$S/renumber_ledger.py" "$lane" || exit 2
python3 "$S/apply_row_mapping.py" "$lane" || { echo "rs mapping needs a hand"; exit 2; }
git add CHANGELOG.md crates/vilan-cli/tests/diagnostics-ledger.tsv crates/vilan-cli/tests/diagnostics_ledger.rs || exit 2
uu=$(git diff --name-only --diff-filter=U)
if [ -n "$uu" ]; then echo "UNRESOLVED:"; echo "$uu"; exit 3; fi
git commit -q --no-edit || exit 4
echo "committed $(git rev-parse --short=8 HEAD)"
cargo build -q -p vilan-cli || exit 5
for spec in "$@"; do echo "== gate: $spec"; eval "cargo nextest run $spec" || exit 6; done
echo "== gate: release_scripts"; cargo nextest run -p vilan-cli --test release_scripts || exit 6
cargo fmt --all --check || { echo "fmt drift — run cargo fmt --all and amend"; exit 6; }
git push -q origin next || exit 7
echo "pushed $(git rev-parse --short=8 HEAD)"
