#!/usr/bin/env bash
# gates_push.sh <lane> [nextest-spec ...] — the second half of merge_lane.sh, for a merge that was
# folded BY HAND after merge_lane.sh stopped at exit 3: every conflicted file is already resolved
# and `git add`ed is NOT required — this adds the named-resolved files itself only if they carry no
# markers. Commits the in-progress merge (MERGE_HEAD present) or gates an already-committed HEAD,
# then builds, gates and pushes exactly as merge_lane.sh does. Exit 3 = markers remain, 6 = a gate
# failed (NOT pushed).
set -u
W=${VILAN_INTEGRATION:-$HOME/code/vilan-lang/vilan/.claude/worktrees/integration}
lane=$1; shift
cd "$W" || exit 1
if [ -f "$(git rev-parse --git-dir)/MERGE_HEAD" ]; then
  for f in $(git diff --name-only --diff-filter=U); do
    if grep -q '^<<<<<<< \|^>>>>>>> ' "$f"; then echo "MARKERS REMAIN: $f"; exit 3; fi
    git add "$f" || exit 2
  done
  cargo fmt --all || exit 2
  git add -u || exit 2
  git commit -q --no-edit || exit 4
  if git diff --name-only HEAD~1 HEAD | grep -q '^vilan/docs/'; then
    python3 scripts/regen-markdown-golden.py > /dev/null 2>&1 && git add crates/vilan-core/tests && git commit -q --amend --no-edit && echo "markdown golden regenerated into the merge"
  fi
fi
echo "committed $(git rev-parse --short=8 HEAD) ($lane, hand-folded)"
cargo build -q -p vilan-cli || exit 5
for spec in "$@"; do echo "== gate: $spec"; eval "cargo nextest run $spec" || exit 6; done
echo "== gate: release_scripts"; cargo nextest run -p vilan-cli --test release_scripts || exit 6
echo "== gate: split"; cargo nextest run -p vilan-cli --test split || exit 6
cargo fmt --all --check || { echo "fmt drift — run cargo fmt --all and amend"; exit 6; }
git push -q origin next || exit 7
echo "pushed $(git rev-parse --short=8 HEAD)"
