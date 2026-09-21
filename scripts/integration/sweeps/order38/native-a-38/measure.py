#!/usr/bin/env python3
"""C15's boxed-binding count and the compile CPU per program, over the accepted corpus."""
import os, resource, subprocess, sys, shutil, pathlib

WT = "/home/reed/code/vilan-lang/vilan/.claude/worktrees/native-a-38"
SCRATCH = pathlib.Path("/tmp/claude-1000/-home-reed-code-vilan-lang/ae2b0352-743d-4446-aedf-1f52ad55831a/scratchpad/native-a-38/measure")
if SCRATCH.exists():
    shutil.rmtree(SCRATCH)
SCRATCH.mkdir(parents=True)
corpus = pathlib.Path(WT) / "vilan/test"
for entry in corpus.iterdir():
    if entry.is_file():
        shutil.copy(entry, SCRATCH / entry.name)
    elif entry.is_dir() and entry.name not in ("dist", "target"):
        shutil.copytree(entry, SCRATCH / entry.name)

env = dict(os.environ)
env["VILAN_STD"] = f"{WT}/vilan/std"
env["VILAN_RT"] = f"{WT}/crates/vilan-rt"
env["CARGO_TARGET_DIR"] = str(SCRATCH / "target")
env["VILAN_NATIVE_REPORT_BOXED"] = "1"
vilan = f"{WT}/target/debug/vilan"

programs = sys.argv[1:]
rows = []
for program in programs:
    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    emit = subprocess.run([vilan, "build", "--backend", "rust", "--stdout", program],
                          cwd=SCRATCH, env=env, capture_output=True, text=True)
    mid = resource.getrusage(resource.RUSAGE_CHILDREN)
    full = subprocess.run([vilan, "build", "--backend", "rust", program],
                          cwd=SCRATCH, env=env, capture_output=True, text=True)
    after = resource.getrusage(resource.RUSAGE_CHILDREN)
    if emit.returncode != 0 or full.returncode != 0:
        continue
    emit_cpu = (mid.ru_utime - before.ru_utime) + (mid.ru_stime - before.ru_stime)
    full_cpu = (after.ru_utime - mid.ru_utime) + (after.ru_stime - mid.ru_stime)
    boxed = None
    for line in full.stdout.splitlines():
        if line.startswith("vilan-native: boxed-bindings="):
            boxed = int(line.split("=", 1)[1])
    lines = len(emit.stdout.splitlines())
    rows.append((program, boxed, emit_cpu, full_cpu, lines))

print(f"{'program':38} {'boxed':>5} {'emit CPU s':>10} {'rustc CPU s':>11} {'rust lines':>10}")
total_boxed = 0
for program, boxed, emit_cpu, full_cpu, lines in rows:
    total_boxed += boxed or 0
    print(f"{program:38} {boxed if boxed is not None else -1:5} {emit_cpu:10.3f} {full_cpu:11.3f} {lines:10}")
n = len(rows)
if n:
    print(f"\n{n} programs measured; boxed bindings TOTAL {total_boxed}")
    print(f"emit CPU  mean {sum(r[2] for r in rows)/n:.3f}s  max {max(r[2] for r in rows):.3f}s")
    print(f"rustc CPU mean {sum(r[3] for r in rows)/n:.3f}s  max {max(r[3] for r in rows):.3f}s")
