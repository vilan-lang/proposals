#!/usr/bin/env python3
"""stamp_items.py <spec.json> [--check] [--tracker DIR] — append dated stamps to tracker items, SAFELY.
spec = {"prefix": "- 2026-09-21 (Order 39 sweep): ", "stamps": {"A110": "text…", …}}

Why this exists (Order 39): the integrator stamped items with the one-liner
    open(p, 'w').write(open(p).read().rstrip('\\n') + stamp)
which opens the file for WRITING — truncating it — before Python evaluates the read, so every item
stamped that way kept only its newest stamp (25 files, restored from git history). This helper reads
EVERYTHING first, validates every target (exists, starts with its `# ID — ` heading), and only then
writes; after writing it re-reads each file and asserts the heading and the old body are still there."""
import json, os, sys
args = sys.argv[1:]
check = "--check" in args
tracker = args[args.index("--tracker") + 1] if "--tracker" in args else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "projects", "vilan", "tracker")
spec = json.load(open([a for a in args if a.endswith(".json")][0]))
prefix, stamps = spec["prefix"], spec["stamps"]
bodies, errors = {}, []
for item, text in stamps.items():
    path = os.path.join(tracker, "items", item + ".md")
    if not os.path.exists(path):
        errors.append(f"{item}: no item file"); continue
    body = open(path).read()
    if not body.startswith(f"# {item} — "):
        errors.append(f"{item}: does not start with its heading — is it already damaged?"); continue
    if not text.strip():
        errors.append(f"{item}: empty stamp"); continue
    bodies[item] = (path, body)
if errors:
    print("INVALID:\n  " + "\n  ".join(errors)); sys.exit(1)
print(f"valid: {len(bodies)} stamps")
if check:
    sys.exit(0)
for item, (path, body) in bodies.items():
    new = body.rstrip("\n") + "\n\n" + prefix + stamps[item].strip() + "\n"
    with open(path, "w") as handle:
        handle.write(new)
    after = open(path).read()
    assert after.startswith(f"# {item} — ") and body.rstrip("\n") in after, f"{item}: the write damaged the file"
print(f"stamped {len(bodies)}: {sorted(bodies)}")
