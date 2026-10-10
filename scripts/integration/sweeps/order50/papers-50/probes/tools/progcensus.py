import re,sys
f=sys.argv[1]
cur=None;counts={};maxid=0;maxtid=0
idre=re.compile(r'\bId\((\d+)\)');tre=re.compile(r'TypeId\((\d+)\)')
with open(f) as fh:
    for line in fh:
        m=re.match(r'^    ([a-z_0-9]+): (.*)$',line)
        if m:
            cur=m.group(1);counts[cur]=0
            continue
        if cur and re.match(r'^        \S',line) and not line.strip().startswith(('}',']',')')):
            counts[cur]+=1
        for x in idre.findall(line):
            v=int(x); maxid=max(maxid,v)
        for x in tre.findall(line):
            v=int(x); maxtid=max(maxtid,v)
print('maxId',maxid,'maxTypeId',maxtid)
for k,v in sorted(counts.items(),key=lambda x:-x[1])[:int(sys.argv[2]) if len(sys.argv)>2 else 40]: print(f'{v:8} {k}')
