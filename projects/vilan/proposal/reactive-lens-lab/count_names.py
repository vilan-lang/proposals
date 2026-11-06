#!/usr/bin/env python3
"""usage: count_names.py FILE START END
Public names in a line range: top-level `export` struct/enum/trait/fun/let (T),
trait-declared methods (D), methods in `export impl X {` inherent (I),
methods in `export impl X with Tr {` (M, trait-impl bodies: implement existing names).
public = T + D + I."""
import sys, re
p, a, b = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
T = D = I = M = 0
ctx = None
for i, l in enumerate(open(p, encoding="utf-8"), 1):
    if i < a or i > b: continue
    if re.match(r'^(export )?(impl|trait)\b', l) or re.match(r'^(export )?(struct|enum|fun|let)\b', l) or re.match(r'^\}', l):
        if l.startswith('}'): ctx = None
    m = re.match(r'^export (struct|enum|trait|fun|let)\b', l)
    if m:
        T += 1
        ctx = 'trait' if m.group(1) == 'trait' else None
        continue
    m = re.match(r'^(export )?impl\b', l)
    if m:
        if not m.group(1): ctx = 'private'
        else: ctx = 'trait-impl' if re.search(r'\bwith\b', l) else 'inherent'
        continue
    if re.match(r'^(impl|struct|trait|fun)\b', l): ctx = 'private' if not l.startswith('trait') else 'private'; continue
    if re.match(r'^\t(sync )?fun\b', l):
        if ctx == 'trait': D += 1
        elif ctx == 'inherent': I += 1
        elif ctx == 'trait-impl': M += 1
print(f"toplevel={T} trait_decl_methods={D} inherent_methods={I} trait_impl_methods={M} PUBLIC(T+D+I)={T+D+I}")
