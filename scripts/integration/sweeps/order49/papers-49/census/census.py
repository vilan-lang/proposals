import re, sys, os, collections
# finds `[ELEM; LEN]` (types and repeat literals) in .vl files, comments stripped (line comments only)
pat = re.compile(r'\[([^\[\];\n]*(?:\[[^\[\]\n]*\][^\[\];\n]*)*);\s*([^\]\n]+?)\s*\]')
STR=re.compile(r'"(?:\\.|[^"\\])*"')
def strip(line):
    line=STR.sub('""',line)
    # crude: drop // comments not inside strings
    out=[];instr=False;i=0
    while i<len(line):
        c=line[i]
        if c=='"' and (i==0 or line[i-1]!='\\'): instr=not instr
        if not instr and line.startswith('//',i): break
        out.append(c);i+=1
    return ''.join(out)
for label, root in [a.split('=',1) for a in sys.argv[1:]]:
    files=0; hits=[]
    for d,dirs,fs in os.walk(root):
        dirs[:] = [x for x in dirs if x not in ('node_modules','target','dist','worktrees','.git')]
        for f in fs:
            if not (f.endswith('.vl') or f.endswith('.md')): continue
            files+=1
            p=os.path.join(d,f)
            infence = p.endswith('.vl')
            for n,line in enumerate(open(p,encoding='utf-8',errors='replace'),1):
                if p.endswith('.md'):
                    if line.startswith('```'):
                        infence = line.strip().startswith('```vilan') and not infence
                        continue
                    if not infence: continue
                s=strip(line)
                for m in pat.finditer(s):
                    hits.append((os.path.relpath(p,root),n,m.group(0),m.group(2),s.strip()))
    print(f"== {label}: {files} .vl files, {len(hits)} `[X; n]` sites")
    lens=collections.Counter(h[3] for h in hits)
    print("   lengths:", dict(lens))
    for h in hits: print(f"   {h[0]}:{h[1]}: {h[2]}    | {h[4][:110]}")
