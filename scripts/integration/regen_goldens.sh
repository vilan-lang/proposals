#!/usr/bin/env bash
# regen_goldens.sh — regenerate the corpus `.mjs` goldens and the split fixture's artifacts over the
# integration worktree's CURRENT tree, then JUDGE every moved corpus golden by its RUNTIME output
# (node, old golden vs new, stdout+exit status). Prints one verdict line per moved file; exits 9 if
# any moved golden's runtime output differs (stop-and-decide — never commit that). Commits nothing.
set -u
W=${VILAN_INTEGRATION:-$HOME/code/vilan-lang/vilan/.claude/worktrees/integration}
cd "$W" || exit 1
cargo build -q -p vilan-cli || exit 5
bin="$W/target/debug/vilan"
scratch=$(mktemp -d "${TMPDIR:-/tmp}/regen-goldens.XXXXXX")
for source in vilan/test/*.vl; do
  golden="${source%.vl}.mjs"
  [ -f "$golden" ] || continue
  "$bin" build "$source" > "$scratch/build.log" 2>&1 || { echo "BUILD FAILED: $source"; cat "$scratch/build.log"; }
done
bad=0
for golden in $(git diff --name-only -- 'vilan/test/*.mjs'); do
  name=$(basename "$golden")
  git show "HEAD:$golden" > "$scratch/old-$name"
  ( cd "$scratch" && timeout 20 node "old-$name" > "old-$name.out" 2>&1; echo "exit $?" >> "old-$name.out" )
  cp "$golden" "$scratch/new-$name"
  ( cd "$scratch" && timeout 20 node "new-$name" > "new-$name.out" 2>&1; echo "exit $?" >> "new-$name.out" )
  # a stack trace names the file it ran from — normalize the two scratch names before comparing
  sed -i "s/old-$name/GOLDEN/g" "$scratch/old-$name.out"; sed -i "s/new-$name/GOLDEN/g" "$scratch/new-$name.out"
  if cmp -s "$scratch/old-$name.out" "$scratch/new-$name.out"; then
    echo "moved, runtime identical: $golden ($(wc -c < "$scratch/old-$name") -> $(wc -c < "$golden") B)"
  else
    echo "RUNTIME DIFFERS: $golden"; diff "$scratch/old-$name.out" "$scratch/new-$name.out" | head -10; bad=1
  fi
done
# the split fixture
stage="$scratch/split"; mkdir -p "$stage"
find crates/vilan-cli/tests/split/project -maxdepth 1 -type f -exec cp {} "$stage/" \;
"$bin" build "$stage" > "$scratch/split-build.log" 2>&1 || { echo "SPLIT BUILD FAILED"; cat "$scratch/split-build.log"; bad=1; }
for artifact in app.js app.Route_Home.js app.Route_Docs.js app.Route_NotFound.js app.chunks.json; do
  found=$(find "$stage" -name "$artifact" | head -1)
  [ -n "$found" ] || { echo "SPLIT ARTIFACT MISSING: $artifact"; bad=1; continue; }
  if ! cmp -s "$found" "crates/vilan-cli/tests/split/golden/$artifact"; then
    cp "$found" "crates/vilan-cli/tests/split/golden/$artifact"; echo "moved (split): $artifact"
    case "$artifact" in *.js) node --check "crates/vilan-cli/tests/split/golden/$artifact" || { echo "SPLIT SYNTAX: $artifact"; bad=1; } ;; esac
  fi
done
git status --short -- vilan/test crates/vilan-cli/tests/split | grep -v '\.mjs$\|split/golden' | head
[ "$bad" = 0 ] || exit 9
echo "regen done: $(git diff --name-only -- 'vilan/test/*.mjs' | wc -l) corpus golden(s) moved"
