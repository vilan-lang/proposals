#!/usr/bin/env python3
"""changelog_union.py <lane-ref> [--path CHANGELOG.md]
Resolve CHANGELOG.md after a merge: union every conflict hunk (HEAD side, then the
lane side), restore `<!-- family: … -->` markers a merge boundary ate (looked up by
bold head in the lane's copy, then HEAD's), and assert Unreleased parity (markers ==
bold heads). Run inside the integration worktree with the merge in progress.

Patch-release shape (releases.md §7.3): when HEAD carries a lane's Unreleased entry in a
RELEASED section (a patch fold moved it under `## v0.51.1`), or HEAD has no `## Unreleased`
at all (the fold emptied it), git's own merge conflicts or files the lane's entries under
the released heading. Then the result is computed from `git show HEAD:` and `git show
<lane>:` alone (never the working-tree file): HEAD's file with the lane's Unreleased
entries HEAD does not already carry anywhere (matched by `**headline**`, ignoring a
`<!-- commit: … -->` marker) appended under HEAD's `## Unreleased` (created above the
first `## v…` section when absent), in the lane's order."""
import re, subprocess, sys

def unreleased_bounds(ls):
    """(start, end) of the `## Unreleased` section in a list of lines, or None."""
    start = next((n for n, x in enumerate(ls) if x.startswith("## Unreleased")), None)
    if start is None: return None
    return start, next((n for n in range(start + 1, len(ls)) if ls[n].startswith("## ")), len(ls))

def parse_entries(sec):
    """Entries of a section's lines: family line + `**…**` headline + continuation lines,
    ended by the next family line / heading / `---`. -> [(headline, [lines])]."""
    entries, cur = [], None
    def close():
        nonlocal cur
        if cur is not None:
            while cur and cur[-1].strip() == "": cur.pop()
            head = next((x for x in cur if x.startswith("**")), None)
            if head is not None: entries.append((head.strip(), cur))
        cur = None
    for x in sec:
        if x.startswith("<!-- family:"): close(); cur = [x]
        elif x.startswith("## ") or x.strip() == "---": close()
        elif x.startswith("**") and cur is None: cur = [x]
        elif cur is not None: cur.append(x)
    close()
    return entries

def heads_after_first_heading(ls, skip=None):
    """Every `**…**` headline line below the first `## ` heading (the file header's
    comment block is not an entry), minus the lines inside `skip=(start, end)`."""
    first = next((n for n, x in enumerate(ls) if x.startswith("## ")), len(ls))
    return {x.strip() for n, x in enumerate(ls) if n > first and x.startswith("**")
            and not (skip and skip[0] <= n < skip[1])}

def patch_shape(head_copy, lane_copy):
    """True when the plain path cannot be trusted: HEAD has no `## Unreleased`, or HEAD
    already carries (in a released section) an entry of the lane's Unreleased."""
    hl, ll = head_copy.split("\n"), lane_copy.split("\n")
    hb, lb = unreleased_bounds(hl), unreleased_bounds(ll)
    if hb is None: return lb is not None and bool(parse_entries(ll[lb[0]:lb[1]]))
    if lb is None: return False
    lane_heads = {h for h, _ in parse_entries(ll[lb[0]:lb[1]])}
    return bool(lane_heads & heads_after_first_heading(hl, hb))

def union_from_copies(head_copy, lane_copy):
    """HEAD's CHANGELOG + the lane's Unreleased entries HEAD lacks. -> (text, added)."""
    hl, ll = head_copy.split("\n"), lane_copy.split("\n")
    lb = unreleased_bounds(ll)
    lane_entries = parse_entries(ll[lb[0]:lb[1]]) if lb else []
    have = heads_after_first_heading(hl)
    add = []
    for h, e in lane_entries:
        if h not in have: add.append(e); have.add(h)
    if not add: return head_copy, 0
    flat = []
    for e in add: flat += e + [""]          # entry, one blank line after each
    hb = unreleased_bounds(hl)
    if hb is None:                          # the fold emptied it: open a fresh section
        at = next((n for n, x in enumerate(hl) if x.startswith("## v")), None)
        if at is None: at = next(n for n, x in enumerate(hl) if x.startswith("## "))
        out = hl[:at] + ["## Unreleased", ""] + flat + hl[at:]
    else:
        start, end = hb
        stop = end
        while stop > start + 1 and hl[stop - 1].strip() == "": stop -= 1
        body = hl[start:stop]
        if len(body) > 1: body.append("")   # blank line between HEAD's last entry and ours
        else: body += [""]                  # empty section: heading, blank, entries
        out = hl[:start] + body + flat + hl[end:]
    return "\n".join(out), len(add)

def show(ref, path): return subprocess.run(["git", "show", f"{ref}:{path}"], capture_output=True, text=True).stdout

def report(sec_lines, hunks, restored):
    markers = sum(1 for x in sec_lines if x.startswith("<!-- family:")); heads = sum(1 for x in sec_lines if x.startswith("**"))
    dup = [h for h in set(x for x in sec_lines if x.startswith("**")) if sec_lines.count(h) > 1]
    print(f"changelog: hunks={hunks} restored={restored} parity={markers}/{heads} dupheads={len(dup)}")
    return markers == heads and not dup

def main():
    lane = sys.argv[1]
    path = sys.argv[sys.argv.index("--path") + 1] if "--path" in sys.argv else "CHANGELOG.md"
    lane_copy, head_copy = show(lane, path), show("HEAD", path)
    if patch_shape(head_copy, lane_copy):
        text, added = union_from_copies(head_copy, lane_copy)
        open(path, "w").write(text)
        b = unreleased_bounds(text.split("\n"))
        sec = text.split("\n")[b[0]:b[1]] if b else []
        print(f"changelog: patch-release shape - added={added} from {lane}, rest is HEAD's")
        sys.exit(0 if report(sec, 0, 0) else 1)
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
    open(path, "w").write("\n".join(out))
    sys.exit(0 if report(sec, hunks, restored) else 1)

if __name__ == "__main__": main()
