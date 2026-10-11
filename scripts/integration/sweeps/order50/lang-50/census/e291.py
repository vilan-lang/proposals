#!/usr/bin/env python3
"""E291's census: a SPACED `<` after a name, closing to a `>` followed by `(`
or `::` -- the shape the expression parser can read as a generic list
(`List <i32>::new()`, `a < b > (c)`). Also counts the TIGHT shape
(`name<..>(` / `name<..>::`) for scale.

Regex over source text with string literals and `//` comments blanked; every
hit is printed for hand classification. Trees are `label=path` arguments; a
`.rs` file contributes only the text inside its raw strings (`r#"..."#`), which
is where the compiler's tests keep vilan programs. `.md` contributes its
```vilan fences.
"""
import os, re, sys, collections

NAME = r'[A-Za-z_][A-Za-z0-9_]*'
KEYWORDS = {'if', 'while', 'for', 'return', 'ret', 'let', 'mut', 'match', 'in', 'is', 'and', 'or', 'not'}

def blank_strings_and_comments(text):
    out = []
    i = 0
    n = len(text)
    while i < n:
        c = text[i]
        if c == '"':
            j = i + 1
            while j < n and text[j] != '"':
                if text[j] == '\\':
                    j += 1
                j += 1
            out.append('"' + ' ' * max(0, j - i - 1) + '"')
            i = j + 1
            continue
        if text.startswith('//', i):
            j = text.find('\n', i)
            j = n if j < 0 else j
            out.append(' ' * (j - i))
            i = j
            continue
        out.append(c)
        i += 1
    return ''.join(out)

def scan_generic(text, start):
    """From the `<` at `start`, the index after its balanced `>`, or None.
    Admits only type-ish characters inside, like the parser's generic list."""
    depth = 0
    i = start
    while i < len(text):
        c = text[i]
        if c == '<':
            depth += 1
        elif c == '>':
            depth -= 1
            if depth == 0:
                return i + 1
        elif c in ';{}=\n' or (c == '|' and False):
            return None
        i += 1
    return None

PAT = re.compile(r'(?:(?<=\.)|(?<![A-Za-z0-9_.]))(' + NAME + r')(\s*)<')

def hits_in(code):
    found = []
    for m in PAT.finditer(code):
        name, space = m.group(1), m.group(2)
        if name in KEYWORDS:
            continue
        lt = m.end() - 1
        end = scan_generic(code, lt)
        if end is None:
            continue
        rest = code[end:end + 3].lstrip()
        if not (rest.startswith('(') or rest.startswith('::')):
            continue
        found.append((m.start(), bool(space), code[m.start():end + 1].replace('\n', ' ')))
    return found

def sources(root):
    for d, dirs, fs in os.walk(root):
        dirs[:] = [x for x in dirs if x not in ('node_modules', 'target', 'dist', 'worktrees', '.git')]
        for f in sorted(fs):
            p = os.path.join(d, f)
            if f.endswith('.vl'):
                yield p, [(0, open(p, encoding='utf-8', errors='replace').read())]
            elif f.endswith('.md'):
                text = open(p, encoding='utf-8', errors='replace').read()
                chunks, inside, buf, base = [], False, [], 0
                offset = 0
                for line in text.splitlines(keepends=True):
                    if line.startswith('```'):
                        if inside:
                            chunks.append((base, ''.join(buf)))
                            inside, buf = False, []
                        elif line.strip().startswith('```vilan'):
                            inside, base = True, offset + len(line)
                    elif inside:
                        buf.append(line)
                    offset += len(line)
                yield p, chunks
            elif f.endswith('.rs'):
                text = open(p, encoding='utf-8', errors='replace').read()
                yield p, [(m.start(1), m.group(1)) for m in re.finditer(r'r#+"(.*?)"#+', text, re.S)]

def main():
    total = collections.Counter()
    for label, root in (a.split('=', 1) for a in sys.argv[1:]):
        files, spaced, tight = 0, [], 0
        for path, chunks in sources(root):
            files += 1
            for base, chunk in chunks:
                code = blank_strings_and_comments(chunk)
                for offset, is_spaced, text in hits_in(code):
                    if is_spaced:
                        line = chunk.count('\n', 0, offset) + 1
                        spaced.append((os.path.relpath(path, root), base, line, text))
                    else:
                        tight += 1
        print(f'== {label}: {files} files; tight generic heads {tight}; SPACED {len(spaced)}')
        for rel, base, line, text in spaced:
            print(f'   {rel} (+{line}): {text}')
        total['tight'] += tight
        total['spaced'] += len(spaced)
    print(f'== total: tight {total["tight"]}, spaced {total["spaced"]}')

main()
