#!/usr/bin/env python3
"""Classify every changed top-level item across a repo's git history of .vl
files: what would an edit of this kind have to invalidate?

Classes (an item's widest change):
  import      - an import/use line was added, removed or changed
  type-shape  - a struct/enum/trait/type declaration changed
  impl-header - an impl's header line changed, or an impl was added/removed
  signature   - a fun's signature (name, params, written return) changed,
                or a fun was added/removed
  body-annot  - a fun body changed under an unchanged signature WITH a written return type
  body-infer  - a fun body changed under an unchanged signature with an INFERRED return
  binding     - a module-level let/const changed
  other

Read-only: `git show` only. Heuristic splitter: top-level items start at column 0;
impl/trait members start with one tab + `fun`.
Usage: edit_classes.py <repo> [<pathspec-exclude>...]"""
import re, subprocess, sys, collections
repo = sys.argv[1]
excludes = sys.argv[2:]
def git(*args):
    return subprocess.run(['git', '-C', repo, *args], capture_output=True, text=True).stdout
def items(text):
    """-> dict key -> (kind, header, body) ; members of impls flattened as their own items"""
    out = {}
    lines = text.split('\n')
    cur = None
    def flush(block):
        if not block:
            return
        head = block[0]
        h = head.strip()
        body = '\n'.join(block[1:])
        m = re.match(r'(?:export(?:\([^)]*\))?\s+)?(?:const\s+)?(?:async\s+)?(?:external\s+)?fun\s+(\w+)', h)
        if h.startswith('import') or h.startswith('use ') or h.startswith('export *') or re.match(r'export\s+(use|import)', h):
            out[('import', h)] = ('import', h, '')
            return
        if m:
            name = m.group(1)
            # signature = text up to the first '{' across lines
            full = '\n'.join(block)
            sig = full.split('{', 1)[0]
            rest = full[len(sig):]
            out[('fun', name)] = ('fun', ' '.join(sig.split()), rest)
            return
        m = re.match(r'(?:export\s+)?(?:resource\s+)?(struct|enum|trait|type)\s+(\w+)', h)
        if m:
            full = '\n'.join(block)
            out[(m.group(1), m.group(2))] = ('type-shape', h, full)
            if m.group(1) == 'trait':
                members(block, 'trait ' + m.group(2), out)
            return
        m = re.match(r'(?:export\s+)?impl\b(.*?)\{?\s*$', h)
        if m:
            key = ('impl', ' '.join(h.split()))
            out[key] = ('impl-header', ' '.join(h.split()), '')
            members(block, key[1], out)
            return
        m = re.match(r'(?:export\s+)?(?:const\s+)?(?:let|mut)\s+(\w+)', h)
        if m:
            out[('binding', m.group(1))] = ('binding', h, body)
            return
        if h.startswith('//') or h.startswith('[') or h == '':
            return
        out[('other', h)] = ('other', h, body)
    def members(block, owner, out):
        mem = None
        for line in block[1:]:
            if re.match(r'^\t(?:export\s+)?(?:async\s+)?fun\s+\w+', line) or re.match(r'^\t\S', line) and mem is None:
                if mem:
                    emit(mem, owner, out)
                mem = [line]
            elif mem is not None:
                mem.append(line)
        if mem:
            emit(mem, owner, out)
    def emit(mem, owner, out):
        full = '\n'.join(mem)
        m = re.match(r'^\t(?:export\s+)?(?:async\s+)?fun\s+(\w+)', mem[0])
        if not m:
            return
        sig = full.split('{', 1)[0]
        out[('fun', owner + '::' + m.group(1))] = ('fun', ' '.join(sig.split()), full[len(sig):])
    block = []
    for line in lines:
        starts = line and not line[0].isspace() and not line.startswith('}') and not line.startswith(')')
        if starts and not line.startswith('//') and not line.startswith('['):
            flush(block)
            block = [line]
        elif block:
            block.append(line)
    flush(block)
    return out
def classify(old, new):
    res = collections.Counter()
    keys = set(old) | set(new)
    for key in keys:
        a = old.get(key); b = new.get(key)
        if a == b:
            continue
        kind = (a or b)[0]
        if kind == 'import':
            res['import'] += 1
        elif kind == 'type-shape':
            res['type-shape'] += 1
        elif kind == 'impl-header':
            res['impl-header'] += 1
        elif kind == 'fun':
            if a is None or b is None or a[1] != b[1]:
                res['signature'] += 1
            else:
                sig = a[1]
                # written return: ')' followed by ':'
                depth = 0; close = None
                for i, ch in enumerate(sig):
                    if ch == '(':
                        depth += 1
                    elif ch == ')':
                        depth -= 1
                        if depth == 0:
                            close = i
                tail = sig[close+1:] if close is not None else ''
                res['body-annot' if re.match(r'\s*:', tail) else 'body-infer'] += 1
        elif kind == 'binding':
            res['binding'] += 1
        else:
            res['other'] += 1
    return res
ORDER = ['import', 'type-shape', 'impl-header', 'signature', 'binding', 'body-infer', 'body-annot', 'other']
import os
subject = os.environ.get('SUBJECT')
commits = [l.split(' ',1)[0] for l in git('log', '--format=%H %s', '--reverse', '--', '*.vl').splitlines() if not subject or re.match(subject, l.split(' ',1)[1])]
items_total = collections.Counter()
widest_per_file = collections.Counter()
files_seen = 0
for c in commits:
    changed = git('diff-tree', '--no-commit-id', '-r', '--name-status', c + '^', c, '--', '*.vl') if git('rev-parse', '--verify', '-q', c + '^') else ''
    for row in changed.splitlines():
        parts = row.split('\t')
        status, path = parts[0], parts[-1]
        if any(x in path for x in excludes) or status.startswith('D') or status.startswith('A'):
            continue
        old = git('show', f'{c}^:{path}')
        new = git('show', f'{c}:{path}')
        res = classify(items(old), items(new))
        if not res:
            continue
        files_seen += 1
        items_total.update(res)
        widest = next(k for k in ORDER if res.get(k))
        widest_per_file[widest] += 1
print(f"commits touching .vl: {len(commits)}; (commit, modified file) pairs classified: {files_seen}")
tot = sum(items_total.values())
print("\nchanged ITEMS by class:")
for k in ORDER:
    print(f"  {k:12} {items_total[k]:5}  {100*items_total[k]/max(tot,1):5.1f}%")
print("\nWIDEST class per (commit, file):")
for k in ORDER:
    print(f"  {k:12} {widest_per_file[k]:5}  {100*widest_per_file[k]/max(files_seen,1):5.1f}%")
