#!/usr/bin/env python3
"""A155 census (papers-47): every CLASS WRITER in a set of .vl files, grouped by
the element it writes.

A class writer is any of: an element head's undotted `class(..)` (lowers to
`.attr("class", ..)`), a dotted `.class(..)`, `.styled(..)`, `.bind_class(..)`,
`.bind_styled(..)`, `.attr("class", ..)`, `.bind_attr("class", ..)`,
`.toggle_attr("class", ..)`, and the DOM-level `set_attribute("class", ..)` /
`.set_class(..)`.

Each writer is attributed to a ROOT:
  head:<pos>   it sits in an element head `<tag ...>` (at the head's own depth)
  view:<pos>   a dotted chain whose root is `view("..")`
  elem:<pos>   a dotted chain hung off a closed element (`<div />.styled(..)`)
  call:<name>  a dotted chain whose root is a call of a function of the
               program's own (the callee may already have written a class)
  var:<name>   a dotted chain whose root is a variable or parameter
Two writers with the same head/view/elem root are a STATIC double write (the
A155 warning's domain). call:/var: roots are the cross-boundary candidates,
listed for review by hand.

Usage: census_class_writers.py LABEL ROOTDIR [EXCLUDE_SUBSTR...]  > tsv
"""
import os, re, sys

WRITER = re.compile(
    r'(?P<dotted>\.(?P<m>class|styled|bind_class|bind_styled|set_class)\s*\()'
    r'|(?P<attr>\.(?P<am>attr|bind_attr|toggle_attr|set_attribute)\(\s*"class")'
    r'|(?P<bare>(?<![\w.])class\()'
)

def strip(text):
    """blank out // comments and string contents (keep offsets and quotes)."""
    out = list(text)
    i, n = 0, len(text)
    while i < n:
        c = text[i]
        if c == '/' and i + 1 < n and text[i + 1] == '/':
            while i < n and text[i] != '\n':
                out[i] = ' '
                i += 1
            continue
        if c == '"':
            j = i + 1
            while j < n and text[j] != '"':
                if text[j] == '\\':
                    out[j] = ' '
                    j += 1
                if j < n and text[j] != '\n':
                    out[j] = ' '
                j += 1
            i = j + 1
            continue
        i += 1
    return ''.join(out)

def heads(s):
    """(start, end, tag) spans of element heads `<tag ...>` / `<tag ... />`."""
    spans = []
    for m in re.finditer(r'<([a-z][\w-]*)(?=[\s>/])', s):
        k = m.start() - 1
        if k >= 0 and (s[k].isalnum() or s[k] in '_<'):
            continue  # generic `List<View>` or `<<`
        depth = 0
        j = m.end()
        while j < len(s):
            c = s[j]
            if c in '([{':
                depth += 1
            elif c in ')]}':
                depth -= 1
                if depth < 0:
                    break
            elif c == '>' and depth == 0 and s[j - 1] != '=' and s[j - 1] != '-':
                spans.append((m.start(), j + 1, m.group(1)))
                break
            j += 1
    return spans

def match_back(s, close):
    depth = 0
    j = close
    while j >= 0:
        if s[j] in ')]}':
            depth += 1
        elif s[j] in '([{':
            depth -= 1
            if depth == 0:
                return j
        j -= 1
    return -1

def root_of(s, pos, head_spans):
    """walk back from a dotted writer at `pos` (the dot) to its chain root."""
    j = pos - 1
    while True:
        while j >= 0 and s[j] in ' \t\r\n':
            j -= 1
        if j < 0:
            return ('?', 0)
        if s[j] == ')':
            o = match_back(s, j)
            k = o - 1
            m = re.search(r'([A-Za-z_][\w:]*)\s*$', s[:o])
            if not m:
                return ('?', o)
            name = m.group(1)
            b = m.start(1) - 1
            if b >= 0 and s[b] == '.':
                j = b - 1
                continue
            if name.split('::')[-1] == 'view':
                return ('view', m.start(1))
            return ('call:' + name, m.start(1))
        if s[j] == '>':
            # a closed element; find the head that owns it (closing tag or
            # self-closing head) — approximate: the nearest head ending here
            for (a, e, tag) in head_spans:
                if e - 1 == j:
                    return ('elem', a)
            # `</tag>` closing: find its opener by tag balance
            m = re.search(r'</([a-z][\w-]*)\s*$', s[:j])
            if m:
                tag = m.group(1)
                depth = 0
                for (a, e, t) in sorted(head_spans, key=lambda h: -h[0]):
                    if a > m.start() or t != tag:
                        continue
                    if s[e - 2] == '/':
                        continue
                    return ('elem', a)
            return ('elem?', j)
        m = re.search(r'([A-Za-z_][\w]*)$', s[:j + 1])
        if m:
            b = m.start(1) - 1
            if b >= 0 and s[b] == '.':
                # field access `a.b` — treat the whole path as the variable
                mm = re.search(r'([A-Za-z_][\w.]*)$', s[:j + 1])
                return ('var:' + mm.group(1), mm.start(1))
            return ('var:' + m.group(1), m.start(1))
        return ('?', j)

def scan(path, label):
    text = open(path).read()
    s = strip(text)
    hs = heads(s)
    rows = []
    for m in WRITER.finditer(s):
        pos = m.start()
        kind = m.group('m') or m.group('am') or 'class(attr)'
        if m.group('am'):
            kind = m.group('am') + '("class")'
        # inside a head at the head's own depth?
        owner = None
        for (a, e, tag) in hs:
            if a < pos < e:
                # depth of pos inside the head
                depth = 0
                for c in s[a:pos]:
                    if c in '([{': depth += 1
                    elif c in ')]}': depth -= 1
                if depth == 0:
                    owner = ('head', a, tag)
        if m.group('bare'):
            if not owner:
                # a bare `class(` outside a head: a function named class? skip
                # unless it's a fun decl
                continue
            kind = 'class(attr)'
        if owner:
            root = ('head', owner[1])
        else:
            root = root_of(s, pos, hs)
        line = text.count('\n', 0, pos) + 1
        arg = text[m.end():m.end() + 60].split('\n')[0]
        rows.append((label, path, line, kind, root[0], root[1], arg.strip()))
    return rows

def main():
    label, rootdir = sys.argv[1], sys.argv[2]
    excludes = sys.argv[3:]
    all_rows = []
    for dirpath, dirs, files in os.walk(rootdir):
        if any(x in dirpath for x in ('node_modules', '/dist', '/target', '/export')):
            continue
        for f in sorted(files):
            p = os.path.join(dirpath, f)
            if f.endswith('.vl') and not any(x in p for x in excludes):
                all_rows.extend(scan(p, label))
    from collections import defaultdict
    groups = defaultdict(list)
    for r in all_rows:
        if r[4] in ('head', 'view', 'elem'):
            groups[(r[1], r[4], r[5])].append(r)
    static_doubles = {k: v for k, v in groups.items() if len(v) > 1}
    print('label\tfile:line\twriter\troot\targ')
    for r in all_rows:
        rel = os.path.relpath(r[1], rootdir)
        root = r[4] if r[4].startswith(('call:', 'var:')) else f'{r[4]}@{r[5]}'
        flag = ' DOUBLE' if (r[1], r[4], r[5]) in static_doubles else ''
        print(f'{r[0]}\t{rel}:{r[2]}\t{r[3]}\t{root}{flag}\t{r[6]}')
    from collections import Counter
    kinds = Counter(r[3] for r in all_rows)
    roots = Counter(('cross' if r[4].startswith(('call:', 'var:')) else r[4]) for r in all_rows)
    print(f'# {label}: writers={len(all_rows)} elements(head/view/elem)={len(groups)} '
          f'static-doubles={len(static_doubles)} kinds={dict(kinds)} roots={dict(roots)}',
          file=sys.stderr)

main()
