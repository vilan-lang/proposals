#!/usr/bin/env python3
"""fold_tests_by_name.py <file> <base-rev> <lane-ref> [--allow-edit a,b]
Resolve a conflicted Rust test file as HEAD's copy plus the lane's NEW top-level `fn`s appended
whole (brace-matched, with their preceding `#[…]`/`//` lines). Refuses if the lane changed an
existing fn relative to <base-rev> unless that fn is named in --allow-edit (then the lane's version
replaces HEAD's). Whitespace-insensitive comparison. Test MODULES (`mod x { … }`) are NOT handled —
resolve those as the merged prefix plus each original's tail located by an anchor."""
import re, subprocess, sys
path, base_rev, lane = sys.argv[1:4]
allow = set(sys.argv[sys.argv.index("--allow-edit") + 1].split(",")) if "--allow-edit" in sys.argv else set()
def show(ref): return subprocess.run(["git", "show", f"{ref}:{path}"], capture_output=True, text=True).stdout
def fns(src):
    lines = src.split("\n"); res = {}; n = 0
    while n < len(lines):
        m = re.match(r"^(pub(\(crate\))? )?(async )?fn ([A-Za-z_][A-Za-z0-9_]*)", lines[n])
        if m:
            name, start = m.group(4), n
            while start > 0 and (lines[start-1].startswith("#[") or lines[start-1].startswith("//")): start -= 1
            depth, end, seen = 0, n, False
            while end < len(lines):
                depth += lines[end].count("{") - lines[end].count("}")
                if "{" in lines[end]: seen = True
                if seen and depth == 0: break
                end += 1
            res[name] = (start, end, "\n".join(lines[start:end+1])); n = end + 1
        else: n += 1
    return res
def norm(t): return re.sub(r"\s+", "", t)
head, base, lane_src = show("HEAD"), show(base_rev), show(lane)
hf, bf, lf = fns(head), fns(base), fns(lane_src)
changed = [n for n in lf if n in bf and norm(lf[n][2]) != norm(bf[n][2]) and n not in allow]
if changed: print(f"REFUSED: the lane edited existing fns: {changed} (pass --allow-edit a,b to take the lane's version)"); sys.exit(1)
new = [n for n in lf if n not in hf]
head_text = head
for n in allow:
    if n in hf and n in lf: head_text = head_text.replace(hf[n][2], lf[n][2], 1); print(f"took the lane's {n}")
appended = "\n\n".join(lf[n][2] for n in new)
# the lane's NEW top-level consts/statics (fixtures its fns read) ride along, by item boundary,
# inserted after the last `use`
_start = re.compile(r"^(pub(\(crate\))? )?(const|static|fn|async fn|use|mod|struct|enum|impl|type|macro_rules!|#\[|///|//)")
def top_consts(src):
    ls = src.split("\n"); starts = [i for i, l in enumerate(ls) if _start.match(l)]; out = {}
    for k, i in enumerate(starts):
        m = re.match(r"^(pub(\(crate\))? )?(const|static) ([A-Za-z_][A-Za-z0-9_]*)", ls[i])
        if not m: continue
        end = starts[k + 1] if k + 1 < len(starts) else len(ls); s0 = i
        if 'r#"' in ls[i] and not ls[i].rstrip().endswith('"#;'):
            # a raw-string fixture: its body may hold column-0 lines; end at the terminator
            end = next(j for j in range(i, len(ls)) if ls[j].rstrip().endswith('"#;')) + 1
        while s0 > 0 and (ls[s0-1].startswith("///") or ls[s0-1].startswith("#[")): s0 -= 1
        out[m.group(4)] = "\n".join(ls[s0:end]).rstrip("\n")
    return out
carried = {k: v for k, v in top_consts(lane_src).items() if k not in top_consts(head) and k not in top_consts(base)}
if carried:
    hl = head_text.split("\n"); last_use = max((i for i, l in enumerate(hl) if l.startswith("use ")), default=0)
    hl[last_use+1:last_use+1] = [""] + list(carried.values())
    head_text = "\n".join(hl); print(f"carried top-level consts: {sorted(carried)}")
open(path, "w").write(head_text.rstrip("\n") + ("\n\n" + appended + "\n" if appended else "\n"))
print(f"folded {path}: head_fns={len(hf)} lane_new={len(new)} {new}")
