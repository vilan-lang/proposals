#!/usr/bin/env python3
"""C15 census over the vilan/test corpus with the INSTALLED vilan.

For every *.vl program: emit Rust (`vilan build --backend rust --stdout`),
classify emit OK / refused, and count DISTINCT boxed bindings (distinct
`let NAME = vilan_rt::Captured::new(` declarations — the emitter's
`boxed_emitted` set, keyed by the id-suffixed name). Also counts the
native consumed-copy census line. Usage: census_corpus.py <corpus dir>
"""
import os, re, subprocess, sys, pathlib, json
corpus = pathlib.Path(sys.argv[1])
env = dict(os.environ, VILAN_NATIVE_REPORT_COPIES="1")
decl = re.compile(r"let (\w+) = vilan_rt::Captured::new\(")
rows = []
for program in sorted(corpus.glob("*.vl")):
    try:
        out = subprocess.run(["vilan", "build", "--backend", "rust", "--stdout", program.name],
                             cwd=corpus, env=env, capture_output=True, text=True, timeout=120)
    except subprocess.TimeoutExpired:
        rows.append((program.stem, "timeout", 0, [])); continue
    if out.returncode != 0:
        rows.append((program.stem, "refused", 0, [])); continue
    names = sorted(set(decl.findall(out.stdout)))
    rows.append((program.stem, "emitted", len(names), names))
emitted = [r for r in rows if r[1] == "emitted"]
print(f"programs {len(rows)}  emitted {len(emitted)}  refused {sum(r[1]=='refused' for r in rows)}")
print(f"boxed TOTAL over emitted: {sum(r[2] for r in emitted)}")
for r in emitted:
    if r[2]:
        print(f"  {r[0]}: {r[2]} {r[3]}")
json.dump(rows, open(pathlib.Path(sys.argv[0]).parent / "census_corpus.json", "w"), indent=1)
