#!/usr/bin/env python3
"""close_batch.py <spec.json> [--check] [--tracker DIR]
spec = {"date": "YYYY-MM-DD", "order": "Order N", "closes": [{"id","lane","commit","text"}]}
Validate every close (item file, INDEX row, no tombstone yet), then delete items/<ID>.md, drop the
INDEX row, append the tombstone to archive.md:
  - **ID. <title> — CLOSED <date>** (<order>, lane <lane>, vilan <commit>: <text>)"""
import json, os, re, sys
args = sys.argv[1:]
check = "--check" in args
tracker = args[args.index("--tracker") + 1] if "--tracker" in args else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "projects", "vilan", "tracker")
spec = json.load(open([a for a in args if a.endswith(".json")][0]))
date, order, closes = spec["date"], spec["order"], spec["closes"]
index_path, archive_path = os.path.join(tracker, "INDEX.md"), os.path.join(tracker, "archive.md")
index = open(index_path).read().split("\n"); archive = open(archive_path).read()
errors, seen, titles = [], set(), {}
for c in closes:
    i = c["id"]
    if i in seen: errors.append(f"{i}: duplicate")
    seen.add(i)
    p = os.path.join(tracker, "items", i + ".md")
    if not os.path.exists(p): errors.append(f"{i}: no item file"); continue
    m = re.match(rf"# {re.escape(i)} — (.*)$", open(p).readline().rstrip("\n"))
    if not m: errors.append(f"{i}: H1 not parseable"); continue
    titles[i] = re.sub(r"^NEW — ", "", m.group(1))
    if sum(1 for l in index if l.startswith(f"| [{i}](")) != 1: errors.append(f"{i}: INDEX row count != 1")
    if re.search(rf"^- \*\*{i}\. ", archive, re.M): errors.append(f"{i}: already has a tombstone")
    for k in ("lane", "commit", "text"):
        if not c.get(k): errors.append(f"{i}: missing {k}")
if errors: print("INVALID:\n  " + "\n  ".join(errors)); sys.exit(1)
print(f"valid: {len(closes)} closes")
if check: sys.exit(0)
tomb = []
for c in closes:
    i = c["id"]
    tomb.append(f"- **{i}. {titles[i]} — CLOSED {date}** ({order}, lane {c['lane']}, vilan {c['commit']}: {' '.join(c['text'].split())})")
    os.remove(os.path.join(tracker, "items", i + ".md"))
    index = [l for l in index if not l.startswith(f"| [{i}](")]
open(index_path, "w").write("\n".join(index))
open(archive_path, "w").write(archive.rstrip("\n") + "\n\n" + "\n\n".join(tomb) + "\n")
print(f"closed {len(closes)}: {[c['id'] for c in closes]}")
