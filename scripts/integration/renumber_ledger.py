#!/usr/bin/env python3
"""renumber_ledger.py <lane>
Resolve crates/vilan-cli/tests/diagnostics-ledger.tsv after a merge (conflicted or
clean): union hunks (HEAD side then lane side); HEAD's rows pass UNTOUCHED (duplicate
message keys under different ids are legitimate); a row whose KEY (the line after the
id column) is not in HEAD's copy is a lane row — renumbered from HEAD's max id + 1 in
file order whatever id it carries (NEW or a local number) — EXCEPT a row whose numeric id
HEAD also carries: that is an EDIT of an existing row, decided against the merge base (the
lane's text wins in place when HEAD's is the base's; HEAD's wins when the lane's is the
base's; both changed = stop). Order 29, rpc-29: an edited row 399 was renumbered to 403 and
HEAD's stale 399 orphaned, which the `every_indexed_row_still_lives_in_the_tree` gate caught.
Env: LEDGER_HEAD_REV (default HEAD), LEDGER_BASE_REV (default merge-base HEAD MERGE_HEAD),
LEDGER_PATH (default the tsv) — for dry runs. Writes row-mapping-<lane>.json beside this
script: {"by_key": {key: new}, "by_old_id": {old: [new…]}, "edited": [id…]}."""
import json, os, subprocess, sys
lane = sys.argv[1]
repo_path = "crates/vilan-cli/tests/diagnostics-ledger.tsv"
path = os.environ.get("LEDGER_PATH", repo_path)  # read and written; git lookups use repo_path
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
head_rev = os.environ.get("LEDGER_HEAD_REV", "HEAD")
def show(rev): return subprocess.run(["git", "show", f"{rev}:{repo_path}"], capture_output=True, text=True).stdout.split("\n")
base_rev = os.environ.get("LEDGER_BASE_REV") or subprocess.run(["git", "merge-base", head_rev, "MERGE_HEAD"], capture_output=True, text=True).stdout.strip()
head_copy, base_copy = show(head_rev), (show(base_rev) if base_rev else [])
def split(row):
    idx = row.find("\t"); return (row[:idx], row[idx:]) if idx > 0 else (None, None)
def by_id(copy):
    d = {}
    for r in copy:
        if r.startswith("#") or not r.strip(): continue
        rid, key = split(r)
        if rid is not None and rid.isdigit(): d[rid] = key
    return d
head_by_id, base_by_id = by_id(head_copy), by_id(base_copy)
head_keys = {split(r)[1] for r in head_copy if r.strip() and not r.startswith("#") and split(r)[0] is not None}  # every HEAD row, the header included
head_max = max((int(i) for i in head_by_id), default=0)
next_id, by_key, by_old, seen, result, id_at, edited = head_max + 1, {}, {}, set(), [], {}, []
for r in out:
    if r.startswith("#") or not r.strip(): result.append(r); continue
    rid, key = split(r)
    if rid is None: result.append(r); continue
    if rid.isdigit() and rid in head_by_id:
        hk, bk = head_by_id[rid], base_by_id.get(rid)
        if key == hk:
            if rid not in id_at: id_at[rid] = len(result); result.append(r)
            continue
        if key == bk:  # the lane left it alone; HEAD changed it — HEAD's stands
            if rid not in id_at: id_at[rid] = len(result); result.append(rid + hk)
            continue
        if hk != bk: print(f"CONFLICT: row {rid} edited by HEAD and the lane — resolve by hand"); sys.exit(2)
        if rid in id_at: result[id_at[rid]] = rid + key
        else: id_at[rid] = len(result); result.append(rid + key)
        edited.append(rid); continue
    if key in head_keys: result.append(r); continue
    if key in seen: print(f"duplicate LANE row dropped: {r[:90]}"); continue
    seen.add(key)
    new = str(next_id); next_id += 1
    by_key[key] = new; by_old.setdefault(rid, []).append(new); result.append(new + key)
open(path, "w").write("\n".join(result))
here = os.path.dirname(os.path.abspath(__file__))
json.dump({"by_key": by_key, "by_old_id": by_old, "edited": edited}, open(os.path.join(here, f"row-mapping-{lane}.json"), "w"), indent=1)
print(f"ledger: head_max={head_max} lane_rows={len(by_key)} assigned={head_max+1}..{next_id-1} old_ids={by_old} edited_in_place={edited}")
