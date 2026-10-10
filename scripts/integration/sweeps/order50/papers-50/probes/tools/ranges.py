import re,sys,collections
f=sys.argv[1]
lines=open(f).read().split('\n')
# sources
i=next(k for k,l in enumerate(lines) if l=='    sources: [')
srcs=[]
k=i+1
while lines[k].startswith('        "'):
    srcs.append(lines[k].strip().strip(',').strip('"')); k+=1
def kind(p):
    if '/std/src/' in p: return 'std'
    if '/macro_std/' in p: return 'mstd'
    return 'pkg'
def short(p):
    if '/std/src/' in p: return 'std::'+p.split('/std/src/')[1]
    return p.split('/')[-1] if 'lucide' not in p else 'lucide/'+p.split('/')[-1]
# source ranges
i=next(k for k,l in enumerate(lines) if l=='    source_ranges: [')
k=i+1; rows=[]
while not lines[k].startswith('    ]'):
    if lines[k].strip()=='SourceRange {':
        s=int(lines[k+1].split(':')[1].strip(' ,')); e=int(lines[k+2].split(':')[1].strip(' ,'))
        sid=int(lines[k+4].strip(' ,')); rows.append((s,e,sid)); k+=7; continue
    k+=1
rows.sort()
per=collections.defaultdict(int); runs=[]
for s,e,sid in rows:
    per[sid]+=e-s
    kd=kind(srcs[sid]) if sid<len(srcs) else '?'
    if runs and runs[-1][0]==kd: runs[-1][2]=e; runs[-1][3]+=e-s
    else: runs.append([kd,s,e,e-s])
tot=collections.Counter()
for sid,n in per.items(): tot[kind(srcs[sid]) if sid<len(srcs) else '?']+=n
print('sources',len(srcs),'by kind',collections.Counter(kind(p) for p in srcs))
print('entity ids by kind',dict(tot),'max',rows[-1][1])
print('runs (kind,start,end,ids):',len(runs))
for r in runs[:60]: print('  ',r)
if len(sys.argv)>2:
    for sid,p in enumerate(srcs): print(sid,short(p),per.get(sid,0))
