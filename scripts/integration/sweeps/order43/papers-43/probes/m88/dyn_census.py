#!/usr/bin/env python3
"""M88 dyn census over a `vilan build -d` dump (`<entry>.analyze.out`).

Usage: dyn_census.py <file.analyze.out> [--js <emitted.mjs>]

Reads the Program Debug dump's `dyn_coercions` (expr -> (subject TypeId, trait Id,
trait args)), `dyn_method_calls` (dispatch sites), `type_id_to_type_map`,
`structs`/`enums`/`traits` (names), `span_map` + `source_ranges` + `sources`
(site locations), and prints per dyn key (trait + args) the SET of subject
types. A subject that is still `Generic(..)` (B412 erasure inside a generic
body) is resolved per instantiation at emission and is reported as such.
With --js, also counts emitted vtables (`Object.create({ ... })`) by slot set.
"""
import re, sys, collections, os

def sections(path, wanted):
    out = {}
    cur = None
    buf = []
    with open(path, encoding='utf-8', errors='replace') as f:
        for line in f:
            if cur is None:
                m = re.match(r'^    ([a-z_]+): (.*)$', line)
                if m and m.group(1) in wanted:
                    rest = m.group(2)
                    if rest.endswith('{') or rest.endswith('[') or rest.endswith('('):
                        cur = m.group(1); buf = [rest]
                    else:
                        out[m.group(1)] = rest
            else:
                if re.match(r'^    [\]\}\)],?$', line):
                    buf.append(line.strip().rstrip(','))
                    out[cur] = '\n'.join(buf)
                    cur = None
                else:
                    buf.append(line)
    return out

TOK = re.compile(r'\s*(?:(?P<str>"(?:[^"\\]|\\.)*")|(?P<range>-?\d+\.\.-?\d+)|(?P<num>-?\d+(?:\.\d+)?(?:e-?\d+)?)|(?P<id>[A-Za-z_][A-Za-z0-9_]*(?:::[A-Za-z_][A-Za-z0-9_]*)*)|(?P<p>[\[\]\{\}\(\),:]))')

def tokenize(s):
    pos = 0; toks = []
    while True:
        m = TOK.match(s, pos)
        if not m or m.end() == pos:
            break
        pos = m.end()
        for k in ('str', 'range', 'num', 'id', 'p'):
            if m.group(k) is not None:
                toks.append((k, m.group(k)))
                break
    return toks

class P:
    def __init__(self, toks): self.t = toks; self.i = 0
    def peek(self): return self.t[self.i] if self.i < len(self.t) else (None, None)
    def next(self): v = self.t[self.i]; self.i += 1; return v
    def expect(self, v):
        k, x = self.next()
        assert x == v, (x, v, self.i)
    def value(self):
        k, x = self.next()
        if k == 'str': return ('S', x[1:-1])
        if k == 'num': return ('N', x)
        if k == 'range': return ('R', x)
        if k == 'id':
            k2, x2 = self.peek()
            if x2 == '(':
                self.next(); items = self.seq(')'); return ('T', x, items)
            if x2 == '{':
                self.next(); return ('O', x, self.fields())
            return ('I', x)
        if x == '[': return ('L', self.seq(']'))
        if x == '(': return ('U', self.seq(')'))
        if x == '{': return self.mapping()
        raise ValueError((k, x, self.i))
    def seq(self, close):
        items = []
        while self.peek()[1] != close:
            items.append(self.value())
            if self.peek()[1] == ',': self.next()
        self.next(); return items
    def fields(self):
        fs = {}
        while self.peek()[1] != '}':
            k, name = self.next(); self.expect(':'); fs[name] = self.value()
            if self.peek()[1] == ',': self.next()
        self.next(); return fs
    def mapping(self):
        entries = []; is_set = False
        while self.peek()[1] != '}':
            key = self.value()
            if self.peek()[1] == ':':
                self.next(); entries.append((key, self.value()))
            else:
                is_set = True; entries.append((key, None))
            if self.peek()[1] == ',': self.next()
        self.next(); return ('SET', [k for k, _ in entries]) if is_set else ('M', entries)

def parse(s): return P(tokenize(s)).value()

def idnum(v):  # ('T','Id',[('N','5')]) -> 5
    return int(v[2][0][1])

def main():
    path = sys.argv[1]
    js = sys.argv[sys.argv.index('--js') + 1] if '--js' in sys.argv else None
    want = {'dyn_coercions', 'dyn_method_calls', 'type_id_to_type_map', 'structs', 'enums',
            'traits', 'span_map', 'source_ranges', 'sources', 'expr_type_ids'}
    sec = sections(path, want)
    types = {idnum(k): v for k, v in parse(sec['type_id_to_type_map'])[1]}
    names = {}
    for key in ('structs', 'enums', 'traits'):
        for k, v in parse(sec[key])[1]:
            names[idnum(k)] = v[2]['name'][1]
    sources = [x[1] for x in parse(sec['sources'])[1]]
    ranges = []
    for r in parse(sec['source_ranges'])[1]:
        f = r[2]; ranges.append((int(f['start'][1]), int(f['end'][1]), int(f['source'][2][0][1])))
    spans = {}
    for k, v in parse(sec['span_map'])[1]:
        if v[0] == 'R': spans[idnum(k)] = int(v[1].split('..')[0])
    def locate(eid):
        src = None
        for a, b, s in ranges:
            if a <= eid < b: src = s; break
        if src is None or eid not in spans: return '?'
        p = sources[src]
        try:
            cands = [p] if os.path.isabs(p) else [os.path.join(os.path.dirname(path), p), p]
            text = next(open(c, 'rb').read() for c in cands if os.path.exists(c))
            line = text[:spans[eid]].count(b'\n') + 1
        except (OSError, StopIteration):
            line = '?'
        short = re.sub(r'.*/std/src/', 'std/', p)
        return f'{short}:{line}'
    def render(tid, depth=0):
        t = types.get(tid)
        if t is None: return f'?{tid}'
        if depth > 6: return '..'
        if t[0] == 'I': return t[1].lower()
        tag = t[1]; a = t[2]
        def args(lst): return ', '.join(render(idnum(x), depth + 1) for x in lst[1]) if lst[0] == 'L' else ''
        if tag in ('Struct', 'Enum', 'Trait', 'Dyn'):
            n = names.get(idnum(a[0]), f'#{idnum(a[0])}')
            s = args(a[1])
            pre = 'dyn ' if tag == 'Dyn' else ''
            return f'{pre}{n}<{s}>' if s else f'{pre}{n}'
        if tag == 'Tuple': return f'({args(a[0])})'
        if tag == 'Generic': return f'GENERIC#{idnum(a[0])}'
        if tag == 'Array': return f'[{render(idnum(a[0]), depth + 1)}; ..]'
        return tag
    co = parse(sec['dyn_coercions'])[1] if 'dyn_coercions' in sec and sec['dyn_coercions'] != '{}' else []
    census = collections.defaultdict(lambda: collections.defaultdict(list))
    for k, v in co:
        eid = idnum(k); subj, trait, targs = v[1]
        key = names.get(idnum(trait), '?')
        if targs[1]:
            rendered = [render(idnum(x)) for x in targs[1]]
            # A mapped-tuple element (`(U in T: dyn Source<U>)`) records the
            # template's U; the emitter resolves it per instance. Recover it
            # from the subject's own `impl .. with Source<X>` for std's
            # nodes (reactive.vl:1379/1835/1877/1928/2071, delta.vl:900).
            if key == 'Source' and len(rendered) == 1 and rendered[0].startswith('GENERIC'):
                st = types.get(idnum(subj))
                if st and st[0] == 'T' and st[1] == 'Struct':
                    n = names.get(idnum(st[2][0])); a = [idnum(x) for x in st[2][1][1]]
                    pick = {'SignalCell': 0, 'Map': 2, 'Switch': 3, 'Combine': 0, 'Distinct': 0}.get(n)
                    if pick is not None and pick < len(a):
                        rendered = [render(a[pick]) + ' (resolved)']
                    elif n == 'FlattenOption' and len(a) == 3:
                        rendered = ['Option<' + render(a[2]) + '> (resolved)']
            key += '<' + ', '.join(rendered) + '>'
        census['dyn ' + key][render(idnum(subj))].append(locate(eid))
    calls = parse(sec['dyn_method_calls'])[1] if sec.get('dyn_method_calls', '{}') != '{}' else []
    by_member = collections.Counter(v[1] for _, v in calls)
    print(f'# {path}')
    print(f'coercion sites: {len(co)}; dyn keys: {len(census)}; dispatch sites (dyn_method_calls): {len(calls)} {dict(by_member)}')
    one = sum(1 for k in census if len(census[k]) == 1)
    print(f'keys with exactly one occupant: {one}; with more: {len(census) - one}')
    for key in sorted(census):
        occ = census[key]
        print(f'  {key}: {len(occ)} occupant(s)')
        for subj in sorted(occ):
            sites = occ[subj]
            print(f'      {subj}  x{len(sites)}  @ {", ".join(sorted(set(sites)))}')
    if js:
        text = open(js, encoding='utf-8').read()
        vts = re.findall(r'(?:const|let|var)\s+(\$?\w+)\s*=\s*Object\.create\(\{([^}]*)\}\)', text)
        slots = collections.Counter(tuple(sorted(re.findall(r'(\w+)\s*:', body))) for _, body in vts)
        print(f'emitted vtables in {js}: {len(vts)}')
        for s, n in slots.most_common():
            print(f'  slots {list(s)}: {n} table(s)')
        pairs = len(re.findall(r'\[1\]\.\w+\(', text))
        print(f'  JS dispatch sites `x[1].member(`: {pairs}')

main()
