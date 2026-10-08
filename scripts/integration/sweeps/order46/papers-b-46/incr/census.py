#!/usr/bin/env python3
"""Static census of a vilan package: how often can a BODY edit cross a
function boundary (inferred returns), how many impls/blankets/consts/derives
/contexts exist. Heuristic (line regexes over the source), read-only.
Usage: census.py <src-dir> [--exclude <subdir>]"""
import re, sys, pathlib
root = pathlib.Path(sys.argv[1])
exclude = sys.argv[3] if len(sys.argv) > 3 and sys.argv[2] == "--exclude" else None
fun_re = re.compile(r'^\s*(?:export(?:\([^)]*\))?\s+)?(?:const\s+)?(?:async\s+)?fun\s+(\w+)')
impl_re = re.compile(r'^\s*(?:export\s+)?impl\b(.*)')
tot = dict(files=0, lines=0, fun=0, fun_inferred=0, fun_annotated=0, impl=0, impl_trait=0, impl_blanket=0,
           const=0, derive=0, context_clause=0, macro_attr=0, closures=0, opaque_ret=0)
per = []
for path in sorted(root.rglob('*.vl')):
    if exclude and exclude in str(path):
        continue
    text = path.read_text()
    lines = text.split('\n')
    tot['files'] += 1; tot['lines'] += len(lines)
    f = dict(fun=0, inferred=0)
    # join signature lines up to the opening brace to see the return annotation
    i = 0
    while i < len(lines):
        m = fun_re.match(lines[i])
        if m:
            sig = lines[i]; j = i
            depth = sig.count('(') - sig.count(')')
            while (depth > 0 or '{' not in sig and ';' not in sig) and j + 1 < len(lines) and j - i < 40:
                j += 1; sig += ' ' + lines[j].strip(); depth = sig.count('(') - sig.count(')')
            # signature text between the matching ')' and '{'
            k = 0; d = 0; close = None
            start = sig.index('(') if '(' in sig else None
            if start is not None:
                for idx in range(start, len(sig)):
                    if sig[idx] == '(':
                        d += 1
                    elif sig[idx] == ')':
                        d -= 1
                        if d == 0:
                            close = idx; break
            tail = sig[close+1:] if close is not None else ''
            tail = tail.split('{')[0]
            annotated = bool(re.match(r'\s*:', tail))
            tot['fun'] += 1; f['fun'] += 1
            if annotated:
                tot['fun_annotated'] += 1
                if re.match(r'\s*:\s*(?!dyn)[A-Z]\w*<', tail) and False:
                    pass
            else:
                tot['fun_inferred'] += 1; f['inferred'] += 1
            if 'context' in tail:
                tot['context_clause'] += 1
        mi = impl_re.match(lines[i])
        if mi:
            tot['impl'] += 1
            rest = mi.group(1)
            if ' with ' in rest or rest.strip().startswith('type') and 'with' in rest:
                tot['impl_trait'] += 1
            if re.match(r'\s*(<[^>]*>\s*)?type\s+\w+', rest):
                tot['impl_blanket'] += 1
        if re.match(r'^\s*(?:export\s+)?const\s+(?!fun)', lines[i]):
            tot['const'] += 1
        if '[derive(' in lines[i]:
            tot['derive'] += 1
        tot['closures'] += len(re.findall(r'\|[^|]*\|\s*[{\w(]', lines[i]))
        i += 1
    per.append((str(path.relative_to(root)), len(lines), f['fun'], f['inferred']))
for k, v in tot.items():
    print(f"{k:16} {v}")
print()
print("per file (path, lines, fun, inferred-return):")
for row in per:
    print("  %-40s %6d %5d %5d" % row)
