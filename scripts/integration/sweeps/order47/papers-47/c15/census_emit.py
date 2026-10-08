#!/usr/bin/env python3
"""C15 (papers-47): emit-only native census.

For each target (a .vl file, or a package dir + entry file), run
`vilan build --backend rust --stdout` with VILAN_NATIVE_REPORT_COPIES=1 and read
off the emitted Rust:
  boxed      distinct `let NAME = vilan_rt::Captured::new(` declarations (and
             boxed parameters, `let NAME = vilan_rt::Captured::new(NAME)`)
  owner      the emitted `fn` each boxed declaration sits in
  closures   `Rc::new(move |` closure values
  copies     the census line (consumed-copies, elided, capture-copies)
Usage: census_emit.py VILAN OUT.json TARGET...   (TARGET = path/to/file.vl)
"""
import json, os, re, subprocess, sys
vilan, out_path, targets = sys.argv[1], sys.argv[2], sys.argv[3:]
env = dict(os.environ, VILAN_NATIVE_REPORT_COPIES="1")
decl = re.compile(r"let (?:mut )?(\w+)\s*(?::[^=]*)?=\s*vilan_rt::Captured::new\(")
fn_re = re.compile(r"^\s*(?:pub(?:\([^)]*\))? )?fn (\w+)", re.M)
census = re.compile(r"vilan-native: consumed-copies=(\d+) elided=(\d+) capture-copies=(\d+)")
rows = []
for t in targets:
    d, f = os.path.dirname(os.path.abspath(t)), os.path.basename(t)
    try:
        p = subprocess.run([vilan, "build", "--backend", "rust", "--stdout", f], cwd=d, env=env,
                           capture_output=True, text=True, timeout=300)
    except subprocess.TimeoutExpired:
        rows.append({"target": t, "status": "timeout"}); continue
    if p.returncode != 0:
        err = next((l for l in (p.stderr + p.stdout).splitlines() if l.startswith("Error")), "")
        rows.append({"target": t, "status": "refused", "why": err[:200]}); continue
    src = p.stdout
    m = census.search(src) or census.search(p.stderr)
    fns = [(m2.start(), m2.group(1)) for m2 in fn_re.finditer(src)]
    boxed = {}
    for m3 in decl.finditer(src):
        owner = max((fn for fn in fns if fn[0] < m3.start()), default=(0, "?"))[1]
        boxed.setdefault(m3.group(1), owner)
    rows.append({"target": t, "status": "emitted", "boxed": len(boxed),
                 "boxed_sites": boxed, "closures": len(re.findall(r"Rc::new\(move \|", src)),
                 "captured_get": src.count(".get()"),
                 "copies": [int(x) for x in m.groups()] if m else None,
                 "rust_lines": src.count("\n")})
json.dump(rows, open(out_path, "w"), indent=1)
em = [r for r in rows if r["status"] == "emitted"]
print(f"targets {len(rows)} emitted {len(em)} refused {sum(r['status']=='refused' for r in rows)}")
print(f"boxed total {sum(r['boxed'] for r in em)}  closures total {sum(r['closures'] for r in em)}  "
      f"capture-copies total {sum((r['copies'] or [0,0,0])[2] for r in em)}")
for r in em:
    if r["boxed"]:
        print(f"  {r['target']}: boxed={r['boxed']} {r['boxed_sites']} closures={r['closures']} copies={r['copies']}")
