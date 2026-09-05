#!/usr/bin/env python3
"""renumber_ledger.py <lane>
Resolve crates/vilan-cli/tests/diagnostics-ledger.tsv after a merge (conflicted or
clean): union hunks (HEAD side then lane side); HEAD's rows pass UNTOUCHED (duplicate
message keys under different ids are legitimate); a row whose KEY (the line after the
id column) is not in HEAD's copy is a lane row — renumbered from HEAD's max id + 1 in
file order whatever id it carries (NEW or a local number). Writes
row-mapping-<lane>.json beside this script: {"by_key": {key: new}, "by_old_id": {old: [new…]}}."""
import json, os, subprocess, sys
lane = sys.argv[1]
path = "crates/vilan-cli/tests/diagnostics-ledger.tsv"
lines = open(path).read().split("\n")
out, i = [], 0
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
head_copy = subprocess.run(["git", "show", f"HEAD:{path}"], capture_output=True, text=True).stdout.split("\n")
def split(row):
    idx = row.find("\t"); return (row[:idx], row[idx:]) if idx > 0 else (None, None)
head_keys, head_max = set(), 0
for r in head_copy:
    if r.startswith("#") or not r.strip(): continue
    rid, key = split(r)
    if rid is None: continue
    head_keys.add(key)
    if rid.isdigit(): head_max = max(head_max, int(rid))
next_id, by_key, by_old, seen, result = head_max + 1, {}, {}, set(), []
for r in out:
    if r.startswith("#") or not r.strip(): result.append(r); continue
    rid, key = split(r)
    if rid is None: result.append(r); continue
    if key in head_keys: result.append(r); continue
    if key in seen: print(f"duplicate LANE row dropped: {r[:90]}"); continue
    seen.add(key)
    new = str(next_id); next_id += 1
    by_key[key] = new; by_old.setdefault(rid, []).append(new); result.append(new + key)
open(path, "w").write("\n".join(result))
here = os.path.dirname(os.path.abspath(__file__))
json.dump({"by_key": by_key, "by_old_id": by_old}, open(os.path.join(here, f"row-mapping-{lane}.json"), "w"), indent=1)
print(f"ledger: head_max={head_max} lane_rows={len(by_key)} assigned={head_max+1}..{next_id-1} old_ids={by_old}")
