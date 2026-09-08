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
# Every `-p <crate> --test <name>` in the gate specs must name a real test binary — a typo
# (corpus_harness, std_surface) stops the chain AFTER the merge otherwise (Order 29's third strike).
for spec in "$@"; do
  crate=$(echo "$spec" | sed -n 's/.*-p \([a-z-]*\).*/\1/p')
  for t in $(echo "$spec" | grep -o -- '--test [A-Za-z0-9_]*' | awk '{print $2}'); do
    # present in HEAD, or ADDED by the lane (a new binary the gate names) — Order 30, hygiene-30
    [ -f "crates/$crate/tests/$t.rs" ] || git cat-file -e "origin/$lane:crates/$crate/tests/$t.rs" 2>/dev/null || { echo "UNKNOWN TEST TARGET: -p $crate --test $t (no crates/$crate/tests/$t.rs in HEAD or on origin/$lane) — fix the spec"; exit 8; }
  done
done
git merge --no-ff --no-commit "origin/$lane" >/dev/null 2>&1; echo "merge exit=$? (non-zero = conflicts to resolve)"
python3 "$S/changelog_union.py" "origin/$lane" || { echo "CHANGELOG needs a hand"; exit 2; }
python3 "$S/renumber_ledger.py" "$lane" || exit 2
python3 "$S/apply_row_mapping.py" "$lane" || { echo "rs mapping needs a hand"; exit 2; }
git add CHANGELOG.md crates/vilan-cli/tests/diagnostics-ledger.tsv crates/vilan-cli/tests/diagnostics_ledger.rs || exit 2
uu=$(git diff --name-only --diff-filter=U)
if [ -n "$uu" ]; then echo "UNRESOLVED:"; echo "$uu"; exit 3; fi
git commit -q --no-edit || exit 4
# The mdBook anchor golden is DERIVED from vilan/docs; a lane that edits docs without regenerating it
# reds `markdown_golden` at the merge (Order 30: dom-30, hygiene-30). Regenerate and fold it in.
if git diff --name-only HEAD~1 HEAD | grep -q '^vilan/docs/'; then
  python3 scripts/regen-markdown-golden.py > /dev/null 2>&1 && git add crates/vilan-core/tests && git commit -q --amend --no-edit && echo "markdown golden regenerated into the merge"
fi
echo "committed $(git rev-parse --short=8 HEAD)"
cargo build -q -p vilan-cli || exit 5
for spec in "$@"; do echo "== gate: $spec"; eval "cargo nextest run $spec" || exit 6; done
echo "== gate: release_scripts"; cargo nextest run -p vilan-cli --test release_scripts || exit 6
# The split emission is a byte golden over std + reachability; two lanes moved it together in Order 29 and no lane gate saw it.
echo "== gate: split"; cargo nextest run -p vilan-cli --test split || exit 6
cargo fmt --all --check || { echo "fmt drift — run cargo fmt --all and amend"; exit 6; }
git push -q origin next || exit 7
echo "pushed $(git rev-parse --short=8 HEAD)"
