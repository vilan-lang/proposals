#!/usr/bin/env python3
"""apply_row_mapping.py <lane>
Apply row-mapping-<lane>.json to diagnostics_ledger.rs's `const ROWS_THE_ENUMERATION_CANNOT_REACH`
block via temp tokens (386→387 and 387→388 cannot chain); a "NEW" old id with several targets is
reported for hand-resolution. Also unions a conflicted .rs block (HEAD then lane)."""
import json, os, re, sys
lane = sys.argv[1]
path = "crates/vilan-cli/tests/diagnostics_ledger.rs"
here = os.path.dirname(os.path.abspath(__file__))
mapping = json.load(open(os.path.join(here, f"row-mapping-{lane}.json")))["by_old_id"]
s = open(path).read()
if "<<<<<<< " in s:
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
            out += head + ls
        else:
            out.append(lines[i])
        i += 1
    s = "\n".join(out); print("rs: conflict hunks unioned")
anchor = "const ROWS_THE_ENUMERATION_CANNOT_REACH"
a = s.find(anchor)
if a < 0: print("rs: no const block"); sys.exit(0)
b = s.find("];", a); block = s[a:b]
changed, ambiguous = 0, []
for old, news in mapping.items():
    if old == "NEW" or len(news) != 1:
        if re.search(rf'\(\s*"{re.escape(old)}"\s*,', block): ambiguous.append((old, news))
        continue
    block, n = re.subn(rf'(\(\s*)"{re.escape(old)}"(\s*,)', rf'\1"@@{news[0]}@@"\2', block); changed += n
block = block.replace("@@", "")
open(path, "w").write(s[:a] + block + s[b:])
print(f"rs: tuples renumbered={changed} ambiguous={ambiguous}")
sys.exit(1 if ambiguous else 0)
