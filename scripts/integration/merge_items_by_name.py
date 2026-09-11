#!/usr/bin/env python3
"""merge_items_by_name.py <file> <base-rev> <lane-ref> [--head-rev REV]
Item-level three-way merge of a Rust TEST file: HEAD's top-level items in HEAD's order; an item
the lane CHANGED relative to <base-rev> takes the lane's version where HEAD kept the base's (both
changed = reported, exit 2); the lane's NEW items are appended. Items are `fn`/`const`/`static`/
`mod`/`use`/`struct`/`enum`/`impl`/`type` at column 0 with their preceding `#[..]`/`///`/`//`
lines attached; raw strings (`r#"…"#`, any hash depth) are skipped when finding item starts,
because vilan program text inside them spells `struct`/`impl` at column 0 too. Round-trips
exactly (asserted). Use it where `fold_tests_by_name.py` refuses or where a lane edited a
program CONST beside its pin (the fold carries new consts only). Order 33, rpc-33's merge."""
import re, subprocess, sys, collections
args = sys.argv[1:]
head_rev = args[args.index('--head-rev') + 1] if '--head-rev' in args else 'HEAD'
path, base_rev, lane = args[0], args[1], args[2]
ATTR = lambda l: l.startswith('#[') or l.startswith('///') or l.startswith('//')
def show(rev): return subprocess.run(['git', 'show', f'{rev}:{path}'], capture_output=True, text=True, check=True).stdout
def items(src):
    lines = src.split('\n'); starts, depth = [], None
    for i, l in enumerate(lines):
        if depth is None:
            m = re.match(r'^(?:pub(?:\(crate\))? )?(fn|const|static|mod|use|struct|enum|impl|type) +([\w:]+)', l)
            if m: starts.append((i, m.group(1), m.group(2)))
        pos = 0
        while True:
            if depth is None:
                o = re.search(r'\br(#*)"', l[pos:])
                if not o: break
                depth = len(o.group(1)); pos += o.end()
            else:
                c = l.find('"' + '#' * depth, pos)
                if c < 0: break
                pos = c + 1 + depth; depth = None
    out, prev_end = [], 0
    for idx, (i, kind, name) in enumerate(starts):
        j = i
        while j > prev_end and ATTR(lines[j-1]): j -= 1
        if j > prev_end: out.append((('prelude', len(out)), '\n'.join(lines[prev_end:j])))
        end = starts[idx+1][0] if idx + 1 < len(starts) else len(lines)
        k = end
        while k > i + 1 and ATTR(lines[k-1]): k -= 1
        out.append(((kind, name), '\n'.join(lines[j:k]))); prev_end = k
    if prev_end < len(lines): out.append((('tail', len(out)), '\n'.join(lines[prev_end:])))
    assert '\n'.join(t for _, t in out) == src, 'round-trip failed'
    return out
base, head, lane_items = items(show(base_rev)), items(show(head_rev)), items(show(lane))
key = lambda k: k[0] not in ('prelude', 'tail')
bm = {k: t for k, t in base if key(k)}; lm = {k: t for k, t in lane_items if key(k)}; hm = {k: t for k, t in head if key(k)}
dups = [k for k, v in collections.Counter(k for k, _ in head if key(k)).items() if v > 1]
if dups: print('duplicate item keys in HEAD, cannot merge by name:', dups); sys.exit(3)
conflicts, replaced, result = [], [], []
for k, t in head:
    if not key(k): result.append(t); continue
    if k in lm and lm[k] != bm.get(k):
        if t != bm.get(k): conflicts.append(k)
        else: replaced.append(k); t = lm[k]
    result.append(t)
new = [(k, t) for k, t in lane_items if key(k) and k not in hm]
if new: result.append('\n'.join(t for _, t in new))
print(f'{path}: replaced from the lane {[k[1] for k in replaced]}; appended {[k[1] for k, _ in new]}; both-changed {[k[1] for k in conflicts]}')
if conflicts: sys.exit(2)
open(path, 'w').write('\n'.join(result))
