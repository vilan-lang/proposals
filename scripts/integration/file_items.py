#!/usr/bin/env python3
r"""file_items.py <spec.json> [--check] [--tracker DIR] — validate-all-then-mutate tracker filing.
spec = {"new_sections": {"F": {"heading": "## F. …", "before": "## G."}}, "items": [{"id","section","title","kind","discussion","status","area","body"}]}
A `|` in a title/discussion must be written `\|` (unescaped for the item's H1)."""
import json, os, re, sys
args = sys.argv[1:]
check = "--check" in args
tracker = args[args.index("--tracker") + 1] if "--tracker" in args else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "projects", "vilan", "tracker")
spec = json.load(open([a for a in args if a.endswith(".json")][0]))
items, new_sections = spec["items"], spec.get("new_sections", {})
index_path = os.path.join(tracker, "INDEX.md")
index = open(index_path).read().split("\n")
archive = open(os.path.join(tracker, "archive.md")).read()
errors, seen = [], set()
for it in items:
    for k in ("id", "section", "title", "kind", "status", "area", "body"):
        if not it.get(k): errors.append(f"{it.get('id','?')}: missing {k}")
    i = it["id"]
    if i in seen: errors.append(f"{i}: duplicate in spec")
    seen.add(i)
    if not re.fullmatch(r"[A-Z]+\d+", i): errors.append(f"{i}: bad id")
    if not i.startswith(it["section"]): errors.append(f"{i}: section mismatch")
    if os.path.exists(os.path.join(tracker, "items", i + ".md")): errors.append(f"{i}: items/{i}.md exists")
    if any(f"[{i}]" in l for l in index): errors.append(f"{i}: already in INDEX")
    if re.search(rf"\*\*{i}\.", archive): errors.append(f"{i}: has a tombstone")
    if re.search(r"(?<!\\)\|", it["title"] + it.get("discussion", "")): errors.append(f"{i}: unescaped pipe (write \\|)")
    if not any(l.startswith(f"## {it['section']}.") for l in index) and it["section"] not in new_sections:
        errors.append(f"{i}: no section heading for {it['section']}")
if errors:
    print("INVALID:\n  " + "\n  ".join(errors)); sys.exit(1)
print(f"valid: {len(items)} items")
if check: sys.exit(0)
for sec, ns in new_sections.items():
    at = next(n for n, l in enumerate(index) if l.startswith(ns["before"]))
    index[at:at] = [ns["heading"], "", "| ID | Title | Kind | Discussion |", "|----|-------|------|------------|", ""]
def insert_row(sec, row):
    start = next(n for n, l in enumerate(index) if l.startswith(f"## {sec}."))
    end = next((n for n in range(start + 1, len(index)) if index[n].startswith("## ")), len(index))
    last = max(n for n in range(start, end) if index[n].startswith("|"))
    index.insert(last + 1, row)
for it in items:
    i = it["id"]
    insert_row(it["section"], f"| [{i}](items/{i}.md) | {it['title']} | {it['kind']} | {it.get('discussion','')} |")
    heading = it["title"].replace("NEW — ", "", 1).replace("\\|", "|")
    open(os.path.join(tracker, "items", i + ".md"), "w").write(
        f"# {i} — {heading}\n\n- status: {it['status']}\n- kind: {it['kind']}\n- area: {it['area']}\n\n{it['body'].rstrip()}\n")
open(index_path, "w").write("\n".join(index))
print(f"filed {len(items)} items")
