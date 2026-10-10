#!/usr/bin/env python3
"""save_report.py <agent-id> <lane> [X?n=ID ...] — save a lane's hand-back text as REPORT-<lane>.md and
rewrite placeholder ids in newitems50-<short>.json (short = lane without -50)."""
import json,sys,os
aid,lane,*maps=sys.argv[1:]
here=os.path.dirname(os.path.abspath(__file__))
J=f'/home/reed/.claude/projects/-home-reed-code-vilan-lang/89336be2-ed61-4826-b9ee-21d5898255eb/subagents/agent-{aid}.jsonl'
rep=None
for line in open(J):
    try: d=json.loads(line)
    except Exception: continue
    c=d.get('message',{}).get('content')
    if isinstance(c,list):
        for b in c:
            if b.get('type')=='tool_use' and 'andback' in b.get('name',''): rep=b['input']
txt=max((v for v in rep.values() if isinstance(v,str)),key=len)
open(f'{here}/REPORT-{lane}.md','w').write(txt.rstrip()+'\n'); print('report',len(txt))
if maps:
    p=f'{here}/newitems50-{lane.replace("-50","")}.json'; s=open(p).read()
    m=dict(x.split('=') for x in maps)
    for k in sorted(m,key=len,reverse=True): s=s.replace(k,m[k])
    open(p,'w').write(s)
