import re, sys
src = open(sys.argv[1]).read().split('\n')
# map fn name -> (start,end) for methods (4-space indent "    fn" / "    pub fn")
fns = {}
starts = []
for i, l in enumerate(src):
    m = re.match(r'^    (?:pub(?:\(crate\))? )?fn ([a-z_0-9]+)', l)
    if m: starts.append((i, m.group(1)))
    m2 = re.match(r'^(?:pub(?:\(crate\))? )?fn ([a-z_0-9]+)', l)
    if m2: starts.append((i, m2.group(1)))
starts.sort()
for k, (i, n) in enumerate(starts):
    end = starts[k+1][0] if k+1 < len(starts) else len(src)
    fns.setdefault(n, []).append((i, end))
calls_re = re.compile(r'self\.([a-z_0-9]+)\(')
write_re = re.compile(r'self\.([a-z_0-9]+)\s*(?:=[^=]|\.(?:insert|push|extend|entry|get_mut|remove|retain|clear|append|drain|values_mut|iter_mut|truncate|swap_remove|sort|dedup)\b)')
IGN = {'diagnostics','warnings','diagnostic_sources','warning_sources'}
def direct(n):
    w=set(); c=set()
    for (a,b) in fns.get(n,[]):
        for l in src[a:b]:
            s=l.strip()
            if s.startswith('//'): continue
            for m in write_re.finditer(l): w.add(m.group(1))
            for m in calls_re.finditer(l): c.add(m.group(1))
    return w, c
def closure(n, depth=5):
    seen=set(); allw=set(); frontier=[n]
    for d in range(depth):
        nxt=[]
        for f in frontier:
            if f in seen: continue
            seen.add(f)
            w,c=direct(f); allw|=w
            nxt += [x for x in c if x in fns]
        frontier=nxt
    return allw
for n in sys.argv[2:]:
    w,_=direct(n)
    cw=closure(n)
    print(f"{n}: direct={sorted(w-IGN)} | via-callees(3)={sorted((cw-w)-IGN)[:25]}")
