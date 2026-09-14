#!/usr/bin/env python3
"""merge_items_by_name.py <file> <base-rev> <lane-ref> [--head-rev REV]
Item-level three-way merge of a Rust TEST file: HEAD's top-level items in HEAD's order; an item
the lane CHANGED relative to <base-rev> takes the lane's version where HEAD kept the base's (both
changed = reported, exit 2); the lane's NEW items are appended. Items are `fn`/`const`/`static`/
`mod`/`use`/`struct`/`enum`/`impl`/`type` at column 0 with their preceding `#[..]`/`///`/`//`
lines attached; STRING LITERALS are skipped when finding item starts — raw strings (`r#"…"#`, any
hash depth) and, since N81, ordinary `"…"` ones whose line ends in a backslash continuation —
because vilan program text inside them spells `struct`/`impl` at column 0 too. Round-trips
exactly (asserted). Use it where `fold_tests_by_name.py` refuses or where a lane edited a
program CONST beside its pin (the fold carries new consts only). Order 33, rpc-33's merge.

N81 (Order 36): `const EXPOSURE_MODULE: &str = "\\` + 32 lines of vilan at column 0 was split at
every `struct`/`}` inside it, and the pieces merged as separate "items" — the visibility-a-35
merge shipped a file whose header lines had moved inside a `use { }` block and whose const body
was gone. The line scanner below carries string state across lines, so those lines are not item
starts at all."""
import re, subprocess, sys, collections
args = sys.argv[1:]
head_rev = args[args.index('--head-rev') + 1] if '--head-rev' in args else 'HEAD'
path, base_rev, lane = args[0], args[1], args[2]
ATTR = lambda l: l.startswith('#[') or l.startswith('///') or l.startswith('//')
def show(rev): return subprocess.run(['git', 'show', f'{rev}:{path}'], capture_output=True, text=True, check=True).stdout

def code_line_starts(lines):
    """For each line, whether it BEGINS outside a string literal or a block comment — the only
    lines a column-0 item regex may be trusted on. See fold_tests_by_name.py for the argument;
    the two tools carry one copy each on purpose, so neither depends on the other being landed."""
    out, state, hashes = [], None, 0
    for line in lines:
        out.append(state is None)
        i = 0
        while i < len(line):
            c = line[i]
            if state is None:
                m = re.match(r'r(#*)"', line[i:])
                if m: state, hashes = 'raw', len(m.group(1)); i += m.end(); continue
                if line.startswith('//', i): break
                if line.startswith('/*', i): state = 'block'; i += 2; continue
                if c == '"': state = 'str'; i += 1; continue
                if c == "'" and i + 2 < len(line) and line[i + 2] == "'": i += 3; continue
                i += 1
            elif state == 'str':
                if c == '\\': i += 2; continue
                if c == '"': state = None
                i += 1
            elif state == 'block':
                if line.startswith('*/', i): state = None; i += 2; continue
                i += 1
            else:
                if line.startswith('"' + '#' * hashes, i): state = None; i += 1 + hashes; continue
                i += 1
    return out

def items(src):
    lines = src.split('\n'); code = code_line_starts(lines); starts = []
    for i, l in enumerate(lines):
        if not code[i]: continue
        m = re.match(r'^(?:pub(?:\(crate\))? )?(fn|const|static|mod|use|struct|enum|impl|type) +([\w:]+)', l)
        if m: starts.append((i, m.group(1), m.group(2)))
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
# N81: an item in the BASE but not in HEAD was DELETED or RENAMED on HEAD; appending it as "new"
# resurrects a test head under its old name. Only an item neither HEAD nor the base carries is new.
resurrected = [k for k, _ in lane_items if key(k) and k not in hm and k in bm]
new = [(k, t) for k, t in lane_items if key(k) and k not in hm and k not in bm]
if new: result.append('\n'.join(t for _, t in new))
print(f'{path}: replaced from the lane {[k[1] for k in replaced]}; appended {[k[1] for k, _ in new]}; '
      f'both-changed {[k[1] for k in conflicts]}; not resurrected {[k[1] for k in resurrected]}')
if conflicts: sys.exit(2)
open(path, 'w').write('\n'.join(result))
