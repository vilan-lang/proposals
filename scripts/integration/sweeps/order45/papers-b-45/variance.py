#!/usr/bin/env python3
"""variance.py --vilan BIN --runs N [--spin K] SUBJECT_DIR...

performance-gates.md §1's probe: run `vilan check .` in each subject directory N times,
interleaved (subject A, B, C, A, B, C, ...) so load drift hits every subject alike, and
record per run: wall, CPU (user+sys of the child, from rusage), peak RSS, the 1-minute
loadavg. With --spin K, K busy-loop processes run for the whole probe (a controlled
"loaded box"); they are started and killed by PID here.

Prints one CSV row per run and, per subject and metric: median, min, max, the spread
(max-min)/median and the coefficient of variation (stdev/mean)."""
import argparse, os, resource, signal, statistics, subprocess, sys, time

def one(binary, cwd):
    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    start = time.perf_counter()
    p = subprocess.run([binary, "check", "."], cwd=cwd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    wall = time.perf_counter() - start
    after = resource.getrusage(resource.RUSAGE_CHILDREN)
    cpu = (after.ru_utime - before.ru_utime) + (after.ru_stime - before.ru_stime)
    return wall, cpu, after.ru_maxrss / 1024.0, p.returncode

def main():
    a = argparse.ArgumentParser()
    a.add_argument("--vilan", required=True); a.add_argument("--runs", type=int, default=10)
    a.add_argument("--spin", type=int, default=0); a.add_argument("subjects", nargs="+")
    o = a.parse_args()
    spinners = [subprocess.Popen([sys.executable, "-c", "while True: pass"]) for _ in range(o.spin)]
    try:
        time.sleep(1 if spinners else 0)
        rows = {s: [] for s in o.subjects}
        print("subject,run,wall_s,cpu_s,maxrss_mb_cumulative,exit,load1")
        # one throwaway run each: the on-disk macro cache (~/.vilan/check-cache) is filled by the first check
        for s in o.subjects:
            one(o.vilan, s)
        for r in range(o.runs):
            for s in o.subjects:
                wall, cpu, rss, code = one(o.vilan, s)
                load = open("/proc/loadavg").read().split()[0]
                rows[s].append((wall, cpu))
                print(f"{os.path.basename(s.rstrip('/'))},{r},{wall:.4f},{cpu:.4f},{rss:.0f},{code},{load}", flush=True)
        print()
        print("subject,metric,median,min,max,spread_pct,cv_pct")
        for s, v in rows.items():
            for i, name in ((0, "wall"), (1, "cpu")):
                xs = [x[i] for x in v]
                med = statistics.median(xs); mean = statistics.mean(xs); sd = statistics.stdev(xs)
                print(f"{os.path.basename(s.rstrip('/'))},{name},{med:.4f},{min(xs):.4f},{max(xs):.4f},"
                      f"{100*(max(xs)-min(xs))/med:.1f},{100*sd/mean:.1f}")
    finally:
        for p in spinners:
            os.kill(p.pid, signal.SIGTERM)
        for p in spinners:
            p.wait()

main()
