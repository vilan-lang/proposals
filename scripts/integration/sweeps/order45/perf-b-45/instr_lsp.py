"""instructions:u spent by a vilan-lsp server per measured edit: attach a hardware
counter (inherit=1) to every thread of the server once it is initialized, so every
thread it spawns later is counted too; read it before the edit and at idle."""
import ctypes, ctypes.util, importlib.util, os, struct, sys, time, statistics
from pathlib import Path
S = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("lat", S / "lsp-latency.py")
lat = importlib.util.module_from_spec(spec); spec.loader.exec_module(lat)
libc = ctypes.CDLL(ctypes.util.find_library("c"), use_errno=True)
class Attr(ctypes.Structure):
    _fields_ = [("type", ctypes.c_uint32), ("size", ctypes.c_uint32), ("config", ctypes.c_uint64),
                ("sample_period", ctypes.c_uint64), ("sample_type", ctypes.c_uint64),
                ("read_format", ctypes.c_uint64), ("flags", ctypes.c_uint64),
                ("wakeup_events", ctypes.c_uint32), ("bp_type", ctypes.c_uint32),
                ("config1", ctypes.c_uint64), ("config2", ctypes.c_uint64),
                ("branch_sample_type", ctypes.c_uint64), ("sample_regs_user", ctypes.c_uint64),
                ("sample_stack_user", ctypes.c_uint32), ("clockid", ctypes.c_int32),
                ("sample_regs_intr", ctypes.c_uint64), ("aux_watermark", ctypes.c_uint32),
                ("sample_max_stack", ctypes.c_uint16), ("reserved", ctypes.c_uint16)]
def attach(tid):
    a = Attr(); a.type = 0; a.size = ctypes.sizeof(Attr); a.config = 1  # HW_INSTRUCTIONS
    # flags: disabled=0, inherit bit1, exclude_kernel bit5, exclude_hv bit6
    a.flags = (1 << 1) | (1 << 5) | (1 << 6)
    fd = libc.syscall(298, ctypes.byref(a), tid, -1, -1, 0)
    if fd < 0: raise OSError(ctypes.get_errno(), "perf_event_open")
    return fd
def total(fds):
    return sum(struct.unpack("q", os.read(fd, 8))[0] for fd in fds)
name = sys.argv[1]; scenarios = sys.argv[2].split("|"); runs = int(sys.argv[3])
scratch = S / f"lsp-scratch-instr-{name}"
root, sha = lat.prepare_copy("/home/reed/code/kolt", "984a1dfb", scratch)
env = dict(os.environ, VILAN_STD=str(S / "bins" / name / "src/vilan/std"))
server = lat.Server([str(S / "bins" / name / "vilan-lsp")], root, env, scratch / "vilan-lsp.stderr")
try:
    server.request("initialize", {"processId": os.getpid(), "rootUri": root.resolve().as_uri(), "capabilities": {}})
    server.notify("initialized", {})
    fds = [attach(int(t)) for t in os.listdir(f"/proc/{server.pid}/task")]
    for scenario_name in scenarios:
        scenario = next(s for s in lat.SCENARIOS if s["name"] == scenario_name)
        companions = []
        for rel in scenario.get("also_open", []):
            d = lat.Document(server, root / rel); t = time.perf_counter(); d.open(); server.wait_publish(d.uri, t); server.settle(); companions.append(d)
        doc = lat.Document(server, root / scenario["file"]); t = time.perf_counter(); doc.open(); server.wait_publish(doc.uri, t); server.settle()
        samples = []
        for _ in range(runs):
            at = lat.anchor_offset(doc.text, scenario["edit"], scenario, "edit")
            before = total(fds); t = time.perf_counter()
            doc.insert(at, scenario["text"]); server.wait_publish(doc.uri, t); server.settle()
            samples.append(total(fds) - before)
            t = time.perf_counter(); doc.delete(at, len(scenario["text"])); server.wait_publish(doc.uri, t); server.settle()
        doc.close()
        for c in companions: c.close()
        server.settle()
        print(f"{name} {scenario_name}: instructions:u per edit median {statistics.median(samples)/1e9:.2f}G (min {min(samples)/1e9:.2f}G, max {max(samples)/1e9:.2f}G)")
finally:
    server.stop()
