import re,sys,collections
src=open(sys.argv[1]).read().split('\n')
start,end=int(sys.argv[2]),int(sys.argv[3])
body=src[start:end-1]
# join multi-line field decls: a field starts with 'pub? name:' at indent 4
fields=[];cur=None
for l in body:
    s=l.strip()
    if s.startswith('//') or s.startswith('#[') or not s: 
        if cur is not None and s.startswith('//'): pass
        continue
    m=re.match(r'^    (pub(\([^)]*\))? )?([a-z_][a-z0-9_]*)\s*:\s*(.*)$',l)
    if m:
        if cur: fields.append(cur)
        cur=[m.group(3),m.group(4)]
    elif cur: cur[1]+=' '+s
if cur: fields.append(cur)
print('fields',len(fields))
cats=collections.Counter()
rows=[]
for n,t in fields:
    t=t.rstrip(',')
    tags=[]
    if re.search(r'\bHash(Map|Set)|BTree(Map|Set)|IndexMap|FxHash',t): tags.append('map/set')
    if re.search(r"'src",t): tags.append("'src")
    if re.search(r"'static",t): tags.append("'static")
    if re.search(r'\bTypeId\b',t): tags.append('TypeId')
    if re.search(r'\bId\b',t): tags.append('Id')
    if re.search(r'\bSourceId\b',t): tags.append('SourceId')
    if re.search(r'\b(Rc|Arc|Weak)\b',t): tags.append('Rc/Arc')
    if re.search(r'\b(RefCell|Cell|Mutex|OnceCell|OnceLock)\b',t): tags.append('cell')
    if re.search(r'Hash(Map|Set)<\s*usize',t) or re.search(r'Hash(Map|Set)<\s*\(\s*usize',t): tags.append('usize-key')
    if re.search(r'\*const|\*mut|NonNull',t): tags.append('rawptr')
    if re.search(r'&',t): tags.append('ref')
    if re.search(r'\bType\b',t): tags.append('Type')
    if re.search(r'\bSpan\b|Spanned',t): tags.append('Span')
    if re.search(r'Node<|NodeList|Spanned<',t): tags.append('AST')
    if re.search(r'dyn |Box<dyn|fn\(',t): tags.append('dyn/fn')
    for g in tags: cats[g]+=1
    rows.append((n,t,tags))
for k,v in sorted(cats.items(),key=lambda x:-x[1]): print(f'{k:10} {v}')
if len(sys.argv)>4:
    for n,t,tags in rows: print(n,'|',t[:160],'|',','.join(tags))
