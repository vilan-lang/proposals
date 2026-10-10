#!/usr/bin/env python3
"""rss-probe.py <vilan-binary> <kolt-dir> [runs] — peak RSS (KB) of `vilan check .` per run, a FRESH child per run
(forked measurer, so ru_maxrss is that run's alone — the first version read the max over all children)."""
import os, resource, subprocess, sys
binary, kolt = sys.argv[1], sys.argv[2]; runs = int(sys.argv[3]) if len(sys.argv) > 3 else 3
rows = []
for _ in range(runs):
    r, w = os.pipe()
    if os.fork() == 0:
        os.close(r)
        p = subprocess.run([binary, "check", "."], cwd=kolt, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        u = resource.getrusage(resource.RUSAGE_CHILDREN)
        os.write(w, f"{u.ru_maxrss} {u.ru_utime:.2f} {p.returncode}".encode()); os._exit(0)
    os.close(w); data = os.read(r, 256).decode().split(); os.wait()
    rows.append((int(data[0]), float(data[1]), int(data[2])))
rows.sort()
print("runs:", " ".join(f"{k}KB" for k, _, _ in rows), f"| median peakRSS={rows[len(rows)//2][0]} KB user={rows[len(rows)//2][1]}s exit={rows[len(rows)//2][2]}")
