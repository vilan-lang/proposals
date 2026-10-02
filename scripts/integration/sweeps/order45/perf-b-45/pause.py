"""M102 probe: one keystroke, then a REAL pause (no follow-up edit), counting
the analyses the server runs and the CPU it spends until it is idle for 2 s."""
import importlib.util, os, sys, time, json
from pathlib import Path
S = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("lat", S / "lsp-latency.py")
lat = importlib.util.module_from_spec(spec); spec.loader.exec_module(lat)
name = sys.argv[1]; scenario_name = sys.argv[2]; pause = float(sys.argv[3]) if len(sys.argv) > 3 else 3.0
scratch = S / f"lsp-scratch-pause-{name}"
root, sha = lat.prepare_copy("/home/reed/code/kolt", "984a1dfb", scratch)
env = dict(os.environ, VILAN_STD=str(S / "bins" / name / "src/vilan/std"), VILAN_PHASE_TIMING="1")
server = lat.Server([str(S / "bins" / name / "vilan-lsp")], root, env, scratch / "vilan-lsp.stderr")
try:
    server.request("initialize", {"processId": os.getpid(), "rootUri": root.resolve().as_uri(), "capabilities": {}})
    server.notify("initialized", {})
    scenario = next(s for s in lat.SCENARIOS if s["name"] == scenario_name)
    for rel in scenario.get("also_open", []):
        d = lat.Document(server, root / rel); t = time.perf_counter(); d.open(); server.wait_publish(d.uri, t); server.settle()
    doc = lat.Document(server, root / scenario["file"]); t = time.perf_counter(); doc.open(); server.wait_publish(doc.uri, t)
    server.settle(quiet_polls=30)  # 3 s quiet: any union after the open is done
    stderr = scratch / "vilan-lsp.stderr"
    before_lines = stderr.read_text().count("lsp-context")
    cpu0 = lat.cpu_ms(server.pid)
    at = lat.anchor_offset(doc.text, scenario["edit"], scenario, "edit")
    doc.insert(at, scenario["text"])
    server.settle(quiet_polls=int(pause * 10))
    cpu1 = lat.cpu_ms(server.pid)
    lines = stderr.read_text().split("\n")
    analyses = [l for l in lines if "lsp-context" in l][before_lines:]
    print(f"{name} {scenario_name}: {len(analyses)} analyses after one keystroke and a {pause}s pause; CPU {cpu1-cpu0:.0f} ms")
    for l in analyses:
        print("   ", l.split("lsp-analyze ")[1].split(" lsp-index")[0])
finally:
    server.stop()
