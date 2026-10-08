#!/usr/bin/env python3
"""A155: the ARGUMENT of every class writer — composed with `+`, conditional
(`if`/`match` inside the argument, or a reactive writer), `Style::when` / `.on(..)`
condition sets. Usage: args_census.py LABEL ROOT [EXCLUDE...]"""
import os, re, sys
from collections import Counter
W = re.compile(r'(?:\.(class|styled|bind_class|bind_styled)|(?<![\w.])(class))\s*\(')
label, root, ex = sys.argv[1], sys.argv[2], sys.argv[3:]
c = Counter(); rows = []
for d, _, fs in os.walk(root):
    if any(x in d for x in ('node_modules', '/dist', '/target', '/export')): continue
    for f in fs:
        p = os.path.join(d, f)
        if not f.endswith('.vl') or any(x in p for x in ex): continue
        t = re.sub(r'//[^\n]*', lambda m: ' ' * len(m.group(0)), open(p).read())
        for m in W.finditer(t):
            if m.group(2):
                # bare class( only in a head: previous non-space char sequence
                pre = t[max(0, m.start()-200):m.start()]
                if '<' not in pre.split('\n')[-1] and not re.search(r'<\w[^<>]*$', pre): continue
            j, depth = m.end() - 1, 0
            while j < len(t):
                if t[j] in '([{': depth += 1
                elif t[j] in ')]}':
                    depth -= 1
                    if depth == 0: break
                j += 1
            arg = t[m.end():j]
            kind = m.group(1) or 'class(attr)'
            flags = []
            if re.search(r'(?<![+\w"])\+(?![+=])', re.sub(r'"[^"]*"', '""', arg)) and kind in ('styled', 'bind_styled'): flags.append('plus')
            if re.search(r'\bif\b|\bmatch\b', arg): flags.append('cond')
            if kind.startswith('bind_'): flags.append('reactive')
            if re.search(r'\.on\(|\.when\(|Style::when', arg): flags.append('condset')
            if re.match(r'\s*const\b', arg) or re.match(r'\s*css\s*\{', arg): flags.append('inline')
            for fl in flags: c[fl] += 1
            c['all'] += 1
            rows.append((os.path.relpath(p, root), t.count('\n', 0, m.start()) + 1, kind, ','.join(flags)))
for r in rows:
    if r[3] and r[3] != 'inline': print(f'{label}\t{r[0]}:{r[1]}\t{r[2]}\t{r[3]}')
print(f'# {label}: {dict(c)}', file=sys.stderr)
