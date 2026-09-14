#!/usr/bin/env python3
"""apply_row_mapping.py <lane>
Apply row-mapping-<lane>.json to diagnostics_ledger.rs's `const ROWS_THE_ENUMERATION_CANNOT_REACH`
block via temp tokens (386→387 and 387→388 cannot chain); a "NEW" old id with several targets is
reported for hand-resolution. Also unions a conflicted .rs block (HEAD then lane).

N81 (Order 36): the union is not a union for a SCALAR CONSTANT. Two lanes that each add parser
rules both edit `const RULE_STATEMENT_SITES: usize = N;`, and "HEAD's lines then the lane's" left
BOTH lines in the file — `28` and `29` off a base of `23` — so the diagnostics_ledger test binary
would not compile at all (Order 35, visibility-b-35; set to 34 by hand). A same-named single-line
`const`/`static` on both sides is now resolved rather than duplicated: an integer one is summed
through the merge BASE (23 + 5 + 6 = 34, the answer that was written by hand), anything else keeps
HEAD's line and is REPORTED with a non-zero exit so the chain stops at a decision instead of at a
build error three steps later. Ordinary conflict lines — a LIST constant's entries, the case the
union exists for — union exactly as before.
"""
import json, os, re, subprocess, sys
lane = sys.argv[1]
path = "crates/vilan-cli/tests/diagnostics_ledger.rs"
here = os.path.dirname(os.path.abspath(__file__))
mapping = json.load(open(os.path.join(here, f"row-mapping-{lane}.json")))["by_old_id"]
s = open(path).read()

SCALAR = re.compile(r"^(\s*)((?:pub(?:\(crate\))? )?(?:const|static) ([A-Za-z_][A-Za-z0-9_]*)\s*:[^=]*=\s*)(.+?)(;\s*)$")

def base_text():
    """The merge base's copy of the file, for resolving a constant both sides moved. Read through
    git rather than from the `|||||||` conflict side, so it is there whatever `merge.conflictStyle`
    the integrator's checkout is set to."""
    base = subprocess.run(["git", "merge-base", "HEAD", "MERGE_HEAD"], capture_output=True,
                          text=True).stdout.strip()
    if not base: return ""
    return subprocess.run(["git", "show", f"{base}:{path}"], capture_output=True, text=True).stdout

def union(head, lane_side, base_src, problems):
    """HEAD's lines then the lane's, with a same-named scalar constant resolved instead of
    duplicated."""
    head_scalars = {}
    for index, line in enumerate(head):
        m = SCALAR.match(line)
        if m: head_scalars[m.group(3)] = (index, m)
    out, tail = list(head), []
    for line in lane_side:
        m = SCALAR.match(line)
        if not m or m.group(3) not in head_scalars:
            tail.append(line); continue
        name = m.group(3)
        index, hm = head_scalars[name]
        if hm.group(0).strip() == m.group(0).strip():
            continue  # both sides wrote the same line: one is the union
        bm = None
        for base_line in base_src.split("\n"):
            candidate = SCALAR.match(base_line)
            if candidate and candidate.group(3) == name: bm = candidate; break
        if bm and hm.group(4).strip().isdigit() and m.group(4).strip().isdigit() \
                and bm.group(4).strip().isdigit():
            base_value = int(bm.group(4)); merged = base_value + (int(hm.group(4)) - base_value) \
                + (int(m.group(4)) - base_value)
            out[index] = f"{hm.group(1)}{hm.group(2)}{merged}{hm.group(5)}"
            print(f"rs: {name} summed through the base: {bm.group(4)} + "
                  f"{int(hm.group(4)) - base_value} + {int(m.group(4)) - base_value} = {merged}")
        else:
            problems.append(name)
            print(f"rs: BOTH SIDES changed `{name}` and it is not an integer off a base "
                  f"({hm.group(4).strip()!r} / {m.group(4).strip()!r}) — HEAD's line kept, resolve by hand")
    return out + tail

problems = []
if "<<<<<<< " in s:
    base_src = base_text()
    lines, out, i = s.split("\n"), [], 0
    while i < len(lines):
        if lines[i].startswith("<<<<<<< "):
            head, ls, side = [], [], "head"; i += 1
            while not lines[i].startswith(">>>>>>> "):
                if lines[i].startswith("=======") and side == "head": side = "lane"
                elif lines[i].startswith("|||||||") and side == "head": side = "base"
                elif side == "head": head.append(lines[i])
                elif side == "lane": ls.append(lines[i])
                i += 1
            out += union(head, ls, base_src, problems)
        else:
            out.append(lines[i])
        i += 1
    s = "\n".join(out); print("rs: conflict hunks unioned")
anchor = "const ROWS_THE_ENUMERATION_CANNOT_REACH"
a = s.find(anchor)
if a < 0:
    print("rs: no const block")
    open(path, "w").write(s)
    sys.exit(1 if problems else 0)
b = s.find("];", a); block = s[a:b]
changed, ambiguous = 0, []
for old, news in mapping.items():
    if old == "NEW" or len(news) != 1:
        if re.search(rf'\(\s*"{re.escape(old)}"\s*,', block): ambiguous.append((old, news))
        continue
    block, n = re.subn(rf'(\(\s*)"{re.escape(old)}"(\s*,)', rf'\1"@@{news[0]}@@"\2', block); changed += n
block = block.replace("@@", "")
open(path, "w").write(s[:a] + block + s[b:])
print(f"rs: tuples renumbered={changed} ambiguous={ambiguous} unresolved_constants={problems}")
sys.exit(1 if (ambiguous or problems) else 0)
