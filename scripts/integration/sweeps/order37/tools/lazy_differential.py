#!/usr/bin/env python3
"""A103's gate: compile + run every estate program, record stdout/exit/emitted JS.

Run once BEFORE the retrofit and once AFTER; the two output directories are
diffed. Legs: the corpus (vilan/test, 131 programs), the docs' complete
`vilan` fences (node platform), and the packaged examples/templates that a
bare `vilan build` can reach.
"""
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path("/home/reed/code/vilan-lang/vilan/.claude/worktrees/lazy-37")
VILAN = ROOT / "target/debug/vilan"
SCRATCH = Path("/tmp/claude-1000/-home-reed-code-vilan-lang/f41a16b6-e17d-40c2-9495-5f53f0d51dc1/scratchpad/lazy-37")

# Nondeterministic under a second run — corpus_harness::NOT_RUN, verbatim.
NOT_RUN = {
    "time.vl", "crypto.vl", "db.vl", "process-env.vl", "nursery.vl",
}

def sh(args, cwd=None, timeout=300, env=None):
    try:
        p = subprocess.run(args, cwd=cwd, capture_output=True, text=True,
                           timeout=timeout, env=env)
        return p.stdout, p.stderr, p.returncode
    except subprocess.TimeoutExpired:
        return "", "TIMEOUT", -99

def record(out, name, stdout, stderr, code, js):
    out[name] = {
        "stdout": stdout,
        "stderr_tail": stderr[-2000:] if code != 0 else "",
        "code": code,
        "js_sha": hashlib.sha256(js.encode()).hexdigest() if js is not None else None,
        "js_len": len(js) if js is not None else None,
    }

def corpus_leg(stage, out):
    src = ROOT / "vilan/test"
    dst = stage / "corpus"
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    for mjs in dst.rglob("*.mjs"):
        mjs.unlink()
    programs = sorted(p for p in dst.glob("*.vl"))
    for prog in programs:
        name = "corpus/" + prog.name
        so, se, rc = sh([str(VILAN), "build", str(prog)], cwd=str(dst))
        built = prog.with_suffix(".mjs")
        js = built.read_text() if built.exists() else None
        if rc != 0 or js is None:
            record(out, name, "", f"BUILD FAILED\n{so}\n{se}", rc if rc else 1, js)
            continue
        if prog.name in NOT_RUN:
            record(out, name, "<not run: nondeterministic>", "", 0, js)
            continue
        cwd = stage / "run" / prog.stem
        cwd.mkdir(parents=True, exist_ok=True)
        so, se, rc = sh(["node", str(built)], cwd=str(cwd))
        record(out, name, so, se, rc, js)

FENCE = re.compile(r"^(\s*)```vilan(,[a-z]+)?\s*$")

def docs_examples():
    """Every complete node-platform `vilan` fence in vilan/docs, in file order."""
    found = []
    for md in sorted((ROOT / "vilan/docs").rglob("*.md")):
        if "book" in md.parts:
            continue
        lines = md.read_text().splitlines()
        index = 0
        while index < len(lines):
            m = FENCE.match(lines[index])
            if not m:
                index += 1
                continue
            indent, tag = m.group(1), (m.group(2) or "")
            start = index
            index += 1
            body = []
            while index < len(lines) and lines[index].strip() != "```":
                body.append(lines[index][len(indent):] if lines[index].startswith(indent) else lines[index])
                body.append("\n")
                index += 1
            index += 1
            if tag == "":  # complete program, node target
                found.append((md.relative_to(ROOT), start + 1, "".join(body)))
    return found

def docs_leg(stage, out):
    dst = stage / "docs"
    dst.mkdir(parents=True, exist_ok=True)
    for (md, line, source) in docs_examples():
        name = f"docs/{md}#{line}"
        slug = re.sub(r"[^a-zA-Z0-9]+", "_", f"{md}_{line}")
        prog = dst / f"{slug}.vl"
        prog.write_text(source)
        so, se, rc = sh([str(VILAN), "build", str(prog)], cwd=str(dst))
        built = prog.with_suffix(".mjs")
        js = built.read_text() if built.exists() else None
        if rc != 0 or js is None:
            record(out, name, "", f"BUILD FAILED\n{so}\n{se}", rc if rc else 1, js)
            continue
        cwd = stage / "run_docs" / slug
        cwd.mkdir(parents=True, exist_ok=True)
        so, se, rc = sh(["node", str(built)], cwd=str(cwd), timeout=60)
        record(out, name, so, se, rc, js)

def package_leg(stage, out):
    """Packaged trees a bare `vilan build` reaches: examples, templates, benchmarks."""
    roots = []
    for base in ["vilan/examples", "crates/vilan-cli/templates", "vilan/benchmarks"]:
        for toml in sorted((ROOT / base).rglob("vilan.toml")):
            roots.append(toml.parent)
    dst = stage / "packages"
    if dst.exists():
        shutil.rmtree(dst)
    for pkg in roots:
        rel = pkg.relative_to(ROOT)
        target = dst / str(rel).replace("/", "__")
        shutil.copytree(pkg, target)
        so, se, rc = sh([str(VILAN), "build"], cwd=str(target), timeout=300)
        js = ""
        for built in sorted(target.rglob("*.js")) + sorted(target.rglob("*.mjs")):
            js += f"\n// ==== {built.relative_to(target)}\n" + built.read_text()
        record(out, f"pkg/{rel}", so, se, rc, js if js else None)

def main():
    which = sys.argv[1]
    stage = SCRATCH / f"stage-{which}"
    if stage.exists():
        shutil.rmtree(stage)
    stage.mkdir(parents=True)
    out = {}
    corpus_leg(stage, out)
    docs_leg(stage, out)
    package_leg(stage, out)
    dest = SCRATCH / f"diff-{which}.json"
    dest.write_text(json.dumps(out, indent=1, sort_keys=True))
    print(f"{which}: {len(out)} programs -> {dest}")

main()
