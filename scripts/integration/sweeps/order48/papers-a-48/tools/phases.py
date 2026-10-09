import re, sys, statistics, json
runs = []
for path in sys.argv[1:]:
    legs = [[]]
    for line in open(path):
        legs[-1].append(line.rstrip('\n'))
        if 'emission-walk' in line: legs.append([])
    legs = [l for l in legs if l]
    runs.append(legs)
def cpu(tok):  # "12.3ms/11.9cpu" -> cpu ms
    m = re.match(r'([\d.]+)ms/([\d.]+)cpu', tok); return float(m.group(2)) if m else None
out = {}
for li in range(len(runs[0])):
    rows = {}
    for r in runs:
        leg = r[li]; seen_rw = 0
        for line in leg:
            if line.startswith('[vilan pass]'):
                m = re.match(r'\[vilan pass\]\s+([\d.]+)cpu.*?slots\+(\d+) (.*)$', line)
                name = 'pass: ' + m.group(3)
                rows.setdefault(name, []).append(float(m.group(1)))
                rows.setdefault('slots: ' + m.group(3), []).append(int(m.group(2)))
            elif line.startswith('[vilan phase] resolve_world'):
                toks = line.split()[3:]
                tag = 'base' if seen_rw == 0 else 'build'; seen_rw += 1
                for k in range(0, len(toks), 2):
                    rows.setdefault(f'resolve_world[{tag}] {toks[k]}', []).append(cpu(toks[k+1]))
            elif line.startswith('[vilan phase] load+walk') or line.startswith('[vilan phase] post-passes') or line.startswith('[vilan phase] emission-walk'):
                toks = line.split()[2:]
                for k in range(0, len(toks)-1, 2):
                    v = cpu(toks[k+1])
                    if v is None:
                        try: v = float(toks[k+1])
                        except: continue
                    rows.setdefault('phase ' + toks[k], []).append(v)
    print(f"=== leg {li}")
    for k, v in rows.items():
        print(f"{statistics.median(v):10.1f}  min {min(v):8.1f}  n={len(v)}  {k}")
