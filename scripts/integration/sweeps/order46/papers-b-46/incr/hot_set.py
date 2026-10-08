#!/usr/bin/env python3
"""For each module of a package, the HOT SET a keystroke in it would re-walk if
the world were split at the edit: the module plus every module that imports it,
transitively, up to the entry. Prints the hot set's share of the entry world's
source lines. Static, from `import pkg::a::b` lines (module = longest existing file).
Usage: hot_set.py <src-dir> <entry-module>"""
import re, sys, pathlib, collections
root = pathlib.Path(sys.argv[1]); entry = sys.argv[2]
mods = {}
for p in root.rglob('*.vl'):
    rel = p.relative_to(root).with_suffix('')
    name = '::'.join(rel.parts)
    if name.endswith('::lib'):
        name = name[:-5]
    mods[name] = p
imports = collections.defaultdict(set)
for name, p in mods.items():
    for m in re.finditer(r'pkg::([\w:]+)', p.read_text()):
        parts = m.group(1).split('::')
        for k in range(len(parts), 0, -1):
            cand = '::'.join(parts[:k])
            if cand in mods and cand != name:
                imports[name].add(cand); break
# entry world = forward closure of entry
world = set(); stack = [entry]
while stack:
    m = stack.pop()
    if m in world: continue
    world.add(m); stack.extend(imports[m])
lines = {m: len(mods[m].read_text().split('\n')) for m in mods}
total = sum(lines[m] for m in world)
rev = collections.defaultdict(set)
for a, bs in imports.items():
    for b in bs:
        rev[b].add(a)
print(f"entry {entry}: world {len(world)} modules, {total} lines")
rows = []
for m in sorted(world):
    hot = set(); stack = [m]
    while stack:
        x = stack.pop()
        if x in hot or x not in world: continue
        hot.add(x); stack.extend(rev[x])
    hl = sum(lines[x] for x in hot)
    rows.append((m, lines[m], len(hot), hl, 100*hl/total))
for r in sorted(rows, key=lambda r: -r[4]):
    print("  %-26s %6d lines  hot set %2d modules %6d lines  %5.1f%% of the world" % r)
