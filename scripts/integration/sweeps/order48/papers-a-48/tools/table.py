import re,sys
legs={}
cur=None
for line in open(sys.argv[1]):
    if line.startswith('=== leg'): cur=int(line.split()[2]); legs[cur]={}; continue
    m=re.match(r'\s*([\d.]+)\s+min\s+[\d.]+\s+n=(\d+)\s+(.*)$',line.rstrip())
    if m: legs[cur][m.group(3)]=float(m.group(1))
tot = sum(legs[l].get('phase '+p,0) for l in legs for p in ['load+walk','base','build','checks','post-passes','emission-walk','program-drop'])
G=18.93
print('total cpu', tot)
keys=[k for k in legs[1] if k.startswith('pass: ') or k.startswith('phase ') or k.startswith('resolve_world[base] fixpoint')]
for k in keys:
    a=legs[0].get(k,0); b=legs[1].get(k,0)
    if 'fuel' in k: continue
    print(f"{k:70s} {a:7.1f} {b:7.1f} {a+b:7.1f} {100*(a+b)/tot:5.1f}% {G*(a+b)/tot:5.2f}G")
