#!/usr/bin/env python3
"""changelog_union.py <lane-ref> [--path CHANGELOG.md]
Resolve CHANGELOG.md after a merge: union every conflict hunk (HEAD side, then the
lane side), restore `<!-- family: … -->` markers a merge boundary ate (looked up by
bold head in the lane's copy, then HEAD's), and assert Unreleased parity (markers ==
bold heads). Run inside the integration worktree with the merge in progress."""
import re, subprocess, sys
lane = sys.argv[1]
path = sys.argv[sys.argv.index("--path") + 1] if "--path" in sys.argv else "CHANGELOG.md"
lines = open(path).read().split("\n")
out, i, hunks = [], 0, 0
while i < len(lines):
    l = lines[i]
    if l.startswith("<<<<<<< "):
        head, lane_side, side = [], [], "head"
        i += 1
        while not lines[i].startswith(">>>>>>> "):
            if lines[i].startswith("=======") and side == "head": side = "lane"
            elif lines[i].startswith("|||||||") and side == "head": side = "base"
            elif side == "head": head.append(lines[i])
            elif side == "lane": lane_side.append(lines[i])
            i += 1
        out += head
        if head and lane_side and head[-1].strip() != "" and lane_side[0].strip() != "": out.append("")
        out += lane_side
        hunks += 1
    else:
        out.append(l)
    i += 1
def marker_before(copy, headline):
    ls = copy.split("\n")
    for n, x in enumerate(ls):
        if x == headline:
            j = n - 1
            while j >= 0 and ls[j].strip() == "": j -= 1
            if j >= 0 and ls[j].startswith("<!-- family:"): return ls[j]
    return None
def show(ref): return subprocess.run(["git", "show", f"{ref}:{path}"], capture_output=True, text=True).stdout
lane_copy, head_copy = show(lane), show("HEAD")
start = next(n for n, x in enumerate(out) if x.startswith("## Unreleased"))
end = next((n for n in range(start + 1, len(out)) if out[n].startswith("## ")), len(out))
restored, n = 0, start + 1
while n < end:
    if out[n].startswith("**"):
        j = n - 1
        while j > start and out[j].strip() == "": j -= 1
        if not out[j].startswith("<!-- family:"):
            m = marker_before(lane_copy, out[n]) or marker_before(head_copy, out[n])
            if m is None: print(f"NO MARKER FOUND for head: {out[n][:80]}"); sys.exit(2)
            out.insert(n, m); restored += 1; n += 1; end += 1
    n += 1
sec = out[start:end]
markers = sum(1 for x in sec if x.startswith("<!-- family:")); heads = sum(1 for x in sec if x.startswith("**"))
dup = [h for h in set(x for x in sec if x.startswith("**")) if sec.count(h) > 1]
open(path, "w").write("\n".join(out))
print(f"changelog: hunks={hunks} restored={restored} parity={markers}/{heads} dupheads={len(dup)}")
sys.exit(0 if markers == heads and not dup else 1)
