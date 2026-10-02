#!/usr/bin/env python3
"""perf_compare.py --base VILAN --tip VILAN [--tip-std DIR] [--kolt DIR] [--commit SHA] [--runs N]
                   [--threshold 1.10] [--lsp-base BIN --lsp-tip BIN --harness scripts/lsp-latency.py]

The seal's performance verdict (Order 45; tracker M105): the TIP compiler against the PREVIOUS RELEASE on
the owner's app, by CPU time (user+sys of the child, never wall — wall is a claim about the machine's load).
`vilan check` on a scratch copy of kolt (git archive of --commit, plus the untracked search-dict), N cold
runs each, interleaved base/tip so load drifts hit both; medians. Exit 1 if tip > base * threshold on CPU
or on peak RSS. With the LSP arguments it also runs the edit-latency harness for both servers and compares
each row's CPU-to-diagnostics. v0.42.0 shipped a 3x regression with every gate green; this is the gate.

A binary run outside its checkout uses its EMBEDDED std; a tip built in a worktree needs --tip-std pointing
at that worktree's vilan/std when the copy is outside it (std and compiler must match)."""
import argparse, json, os, resource, shutil, statistics, subprocess, sys, tempfile

def run(cmd, cwd, env):
    # One child's OWN usage (os.wait4), never RUSAGE_CHILDREN: that is the maximum over every child
    # so far, which made the peak-RSS ratio x1.00 by construction (papers-b-45's find).
    p = subprocess.Popen(cmd, cwd=cwd, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    err = p.stderr.read()
    _, status, usage = os.wait4(p.pid, 0)
    p.returncode = os.waitstatus_to_exitcode(status)
    return usage.ru_utime + usage.ru_stime, usage.ru_maxrss / 1024.0, p.returncode, err

def main():
    a = argparse.ArgumentParser()
    a.add_argument("--base", required=True); a.add_argument("--tip", required=True)
    a.add_argument("--tip-std"); a.add_argument("--kolt", default=os.path.expanduser("~/code/kolt"))
    a.add_argument("--commit", default="HEAD"); a.add_argument("--runs", type=int, default=5)
    a.add_argument("--threshold", type=float, default=1.10)
    a.add_argument("--max-load", type=float, default=2.0, help="refuse a CPU verdict above this 1-minute loadavg (CPU time rose 3.19 -> 5.80 s as load went 10 -> 20)")
    a.add_argument("--lsp-base"); a.add_argument("--lsp-tip"); a.add_argument("--harness")
    o = a.parse_args()
    scratch = tempfile.mkdtemp(prefix="perf-compare-")
    try:
        copy = os.path.join(scratch, "kolt"); os.makedirs(copy)
        tar = subprocess.run(["git", "-C", o.kolt, "archive", o.commit], stdout=subprocess.PIPE, check=True)
        subprocess.run(["tar", "-x", "-C", copy], input=tar.stdout, check=True)
        for extra in ("search-dict", "src/search-dict"):  # untracked inputs the const pass reads
            src = os.path.join(o.kolt, extra)
            if os.path.isdir(src) and not os.path.exists(os.path.join(copy, extra)):
                shutil.copytree(src, os.path.join(copy, extra))
        sha = subprocess.run(["git", "-C", o.kolt, "rev-parse", "--short=8", o.commit], capture_output=True, text=True).stdout.strip()
        env_base = dict(os.environ); env_tip = dict(os.environ)
        if o.tip_std: env_tip["VILAN_STD"] = o.tip_std
        ver = lambda b: subprocess.run([b, "--version"], capture_output=True, text=True).stdout.strip()
        print(f"kolt @{sha}  load {open('/proc/loadavg').read().split()[0]}  runs {o.runs}")
        print(f"base: {ver(o.base)}\ntip:  {ver(o.tip)}")
        rows = {"base": [], "tip": []}; codes = {}
        for binary, env in ((o.base, env_base), (o.tip, env_tip)):  # one discarded warm-up each: the first run fills the std cache
            run([binary, "check", "."], copy, env)
        for _ in range(o.runs):
            for name, binary, env in (("base", o.base, env_base), ("tip", o.tip, env_tip)):
                cpu, rss, code, err = run([binary, "check", "."], copy, env)
                rows[name].append((cpu, rss)); codes[name] = (code, err.count("\nError") + err.startswith("Error"))
        med = {n: (statistics.median(c for c, _ in v), max(r for _, r in v)) for n, v in rows.items()}
        for n in ("base", "tip"):
            print(f"  {n:4}  check CPU {med[n][0]*1000:7.0f} ms   peak RSS {med[n][1]:6.0f} MB   exit {codes[n][0]} errors {codes[n][1]}")
        failed = []
        if codes["base"] != codes["tip"]:
            print(f"  NOTE  the two compilers disagree on the program (exit/errors {codes['base']} vs {codes['tip']}): the comparison is over different work")
        ratio_cpu = med["tip"][0] / med["base"][0]; ratio_rss = med["tip"][1] / med["base"][1]
        print(f"  tip/base  CPU x{ratio_cpu:.2f}   RSS x{ratio_rss:.2f}   (threshold x{o.threshold:.2f})")
        load = float(open('/proc/loadavg').read().split()[0])
        if load > o.max_load:
            print(f"  NOTE  loadavg {load:.1f} > {o.max_load}: the CPU verdict is NOT TRUSTED at this load — re-run quiet (interleaving keeps the RATIO fairer than either number)")
            failed.append(f"load {load:.1f} too high for a CPU verdict")
        if ratio_cpu > o.threshold: failed.append(f"check CPU x{ratio_cpu:.2f}")
        if ratio_rss > o.threshold: failed.append(f"check peak RSS x{ratio_rss:.2f}")
        if o.harness and o.lsp_base and o.lsp_tip:
            tables = {}
            for name, lsp, std in (("base", o.lsp_base, None), ("tip", o.lsp_tip, o.tip_std)):
                out = os.path.join(scratch, f"lsp-{name}.json")
                cmd = [sys.executable, o.harness, "--kolt", o.kolt, "--commit", o.commit, "--lsp", lsp, "--runs", str(o.runs), "--json", out]
                if std: cmd += ["--std", std]
                r = subprocess.run(cmd, capture_output=True, text=True)
                if r.returncode != 0 or not os.path.exists(out):
                    print(f"  LSP harness failed for {name}: {r.stderr[-400:]}"); failed.append(f"lsp harness ({name})"); continue
                tables[name] = json.load(open(out)); print(f"--- LSP {name} ---\n{r.stdout.strip()}")
            if len(tables) == 2:
                print("  (compare the two LSP tables row by row; the harness's JSON shape decides the automatic check — see M105)")
        if failed:
            print("PERF VERDICT: RED — " + "; ".join(failed)); return 1
        print("PERF VERDICT: green"); return 0
    finally:
        shutil.rmtree(scratch, ignore_errors=True)

sys.exit(main())
