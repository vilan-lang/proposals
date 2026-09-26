#!/usr/bin/env bash
# resume_merge.sh <lane> [nextest-spec ...] — the tail of merge_lane.sh, run after a hand fix in a merge
# left in --no-commit state (CHANGELOG folded, conflicts resolved and `git add`ed): renumber the lane's
# NEW ledger rows, map them, add, check unresolved, commit, regenerate the markdown golden if docs moved,
# build, gate, fmt-check, push. Same exit codes as merge_lane.sh.
set -u
S=$(cd "$(dirname "$0")" && pwd)
W=${VILAN_INTEGRATION:-$HOME/code/vilan-lang/vilan/.claude/worktrees/integration}
lane=$1; shift
cd "$W" || exit 1
python3 "$S/renumber_ledger.py" "$lane" || exit 2
python3 "$S/apply_row_mapping.py" "$lane" || { echo "rs mapping needs a hand"; exit 2; }
git add CHANGELOG.md crates/vilan-cli/tests/diagnostics-ledger.tsv crates/vilan-cli/tests/diagnostics_ledger.rs || exit 2
uu=$(git diff --name-only --diff-filter=U)
if [ -n "$uu" ]; then echo "UNRESOLVED:"; echo "$uu"; exit 3; fi
git commit -q --no-edit || exit 4
if git diff --name-only HEAD~1 HEAD | grep -q '^vilan/docs/'; then
  python3 scripts/regen-markdown-golden.py > /dev/null 2>&1 && git add crates/vilan-core/tests && git commit -q --amend --no-edit && echo "markdown golden regenerated into the merge"
fi
echo "committed $(git rev-parse --short=8 HEAD)"
cargo build -q -p vilan-cli || exit 5
for spec in "$@"; do echo "== gate: $spec"; eval "cargo nextest run $spec" || exit 6; done
echo "== gate: release_scripts"; cargo nextest run -p vilan-cli --test release_scripts || exit 6
echo "== gate: split"; cargo nextest run -p vilan-cli --test split || exit 6
cargo fmt --all --check || { echo "fmt drift — run cargo fmt --all and amend"; exit 6; }
git push -q origin next || exit 7
echo "pushed $(git rev-parse --short=8 HEAD)"
