import re, sys
src = open(sys.argv[1]).read().split('\n')
starts=[]
for i,l in enumerate(src):
    m = re.match(r'^    (?:pub(?:\(crate\))? )?fn ([a-z_0-9]+)', l)
    if m: starts.append((i,m.group(1)))
starts.append((len(src),'<end>'))
pat = re.compile(r'self\.(try_get_expr_id_by_name|get_expr_id_by_name|lookup_[a-z_]+|resolve_name[a-z_]*|find_in_scope[a-z_]*)\(')
for k,(i,n) in enumerate(starts[:-1]):
    if not n.startswith('walk'): continue
    end=starts[k+1][0]
    hits=[]
    for j in range(i,end):
        s=src[j].strip()
        if s.startswith('//'): continue
        for m in pat.finditer(src[j]): hits.append((j+1,m.group(1)))
    if hits: print(n, i+1, hits[:6])
