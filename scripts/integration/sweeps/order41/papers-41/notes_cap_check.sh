#!/bin/sh
# Re-runs the cut-plan's §5.3 check: the script's OWN rewrite parser over the
# CHANGELOG, then release.yml's notes-cap step over the resulting section.
# Usage: notes_cap_check.sh <vilan-tree> <version>   (read-only; writes /tmp only)
set -eu
TREE="$1"; VERSION="$2"; WORK="$(mktemp -d)"
python3 - "$TREE/scripts/cut-release.sh" "$WORK/changelog.awk" <<'PY'
import sys
s = open(sys.argv[1]).read()
a = s.index("CHANGELOG_AWK='") + len("CHANGELOG_AWK='")
open(sys.argv[2], "w").write(s[a:s.index("\n'\n", a)])
PY
awk -v mode=rewrite -v heading="## v$VERSION — $(date +%Y-%m-%d)" -f "$WORK/changelog.awk" \
	"$TREE/CHANGELOG.md" > "$WORK/proposed.md"
python3 - "$WORK/proposed.md" "$VERSION" <<'PY'
import sys
from collections import Counter
lines, version = open(sys.argv[1]).read().split("\n"), sys.argv[2]
out, inside = [], False
for line in lines:
    if line.startswith(f"## v{version} "): inside = True; continue
    if inside and line.startswith("## "): break
    if inside: out.append(line)
text = "\n".join(out) + "\n"
CAP = 110_000   # release.yml's margin under GitHub's 125,000
entries = text.split("\n<!-- family:")
kept, size = [entries[0]], len(entries[0])
for entry in entries[1:]:
    size += len(entry) + len("\n<!-- family:")
    if size > CAP: break
    kept.append(entry)
print(f"section {len(text)} chars; kept {len(kept)-1}, dropped {len(entries)-len(kept)}")
print(Counter(k.split("-->")[0].strip() for k in kept[1:]))
PY
