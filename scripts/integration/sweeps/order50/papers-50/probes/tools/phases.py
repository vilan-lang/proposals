import re,sys,statistics,collections
# args: label=file1,file2,file3 ...
def parse(path):
    d=collections.OrderedDict()
    for line in open(path):
        if line.startswith('[vilan phase] load+walk'):
            for name,ms,cpu in re.findall(r'([a-z+\-]+) ([\d.]+)ms/([\d.]+)cpu',line):
                d[name]=d.get(name,0)+float(cpu)
        elif line.startswith('[vilan phase] post-passes'):
            for name,ms,cpu in re.findall(r'([a-z+\-]+) ([\d.]+)ms/([\d.]+)cpu',line):
                d['pp:'+name]=d.get('pp:'+name,0)+float(cpu)
        elif line.startswith('[vilan phase] resolve_world') and 'fixpoint' in line:
            m=re.search(r'fixpoint ([\d.]+)ms/([\d.]+)cpu',line)
            d['rw-fixpoint(sum)']=d.get('rw-fixpoint(sum)',0)+float(m.group(2))
        elif line.startswith('[vilan pass]') and '(macro world)' not in line:
            m=re.match(r'\[vilan pass\] ([\d.]+)cpu .*slots\+\d+ (.*)$',line.strip())
            if m: d['chk:'+m.group(2)]=d.get('chk:'+m.group(2),0)+float(m.group(1))
        elif line.startswith('[vilan phase] emission-walk'):
            for name,ms,cpu in re.findall(r'([a-z+\-]+) ([\d.]+)ms/([\d.]+)cpu',line):
                d['tail:'+name]=d.get('tail:'+name,0)+float(cpu)
    return d
cols=[];data={}
for arg in sys.argv[1:]:
    label,files=arg.split('=',1)
    runs=[parse(f) for f in files.split(',')]
    keys=[]
    for r in runs:
        for k in r:
            if k not in keys: keys.append(k)
    data[label]={k:statistics.median([r.get(k,0) for r in runs]) for k in keys}
    cols.append(label)
allkeys=[]
for l in cols:
    for k in data[l]:
        if k not in allkeys: allkeys.append(k)
print('| phase | '+' | '.join(cols)+' |')
for k in allkeys:
    print('| '+k+' | '+' | '.join(f"{data[l].get(k,0):.1f}" for l in cols)+' |')
