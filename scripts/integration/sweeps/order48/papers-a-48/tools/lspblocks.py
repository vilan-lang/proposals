import re,sys,statistics
blocks=[[]]
for line in open(sys.argv[1]):
    blocks[-1].append(line.rstrip('\n'))
    if line.startswith('[vilan phase] lsp-context'): blocks.append([])
def kind(b):
    t='\n'.join(b)
    if 'hot-world=1' in t and 'base-hits=1' in t: return 'served'
    if 'hot-refusal impl' in t: return 'refused'
    if 'hot-world=1' in t and 'base-misses=1' in t: return 'hotmiss'
    return None
groups={}
for b in blocks:
    k=kind(b)
    if not k: continue
    rows={}
    for line in b:
        m=re.match(r'\[vilan pass\]\s+([\d.]+)cpu.* slots\+\d+ (.*)$',line)
        if m: rows['pass '+m.group(2)]=float(m.group(1))
        for tag in ['load+walk','base','build','checks','post-passes','contexts+graph','async-infer','platform-color','const-pass','lsp-context','lsp-analyze','lsp-index','lsp-landed']:
            m=re.search(r'(?:^|\s)'+re.escape(tag)+r' [\d.]+ms/([\d.]+)cpu',line)
            if m and line.startswith('[vilan phase]') and 'macro-worlds' not in line: rows['phase '+tag]=float(m.group(1))
    groups.setdefault(k,[]).append(rows)
for k,lst in groups.items():
    print('===',k,len(lst))
    keys=[]
    for r in lst:
        for x in r:
            if x not in keys: keys.append(x)
    for x in keys:
        v=[r[x] for r in lst if x in r]
        print(f"{statistics.median(v):8.1f} n={len(v)} {x}")
