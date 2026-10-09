"""Minimal LSP driver: open the entry, collect publishDiagnostics, apply edits, report per-file diagnostics.
usage: lspprobe.py LSP PKGDIR ENTRY_REL  (edits: a keystroke appended as a comment line to the entry, then undone)"""
import json, os, subprocess, sys, time, threading, queue
lsp, root, entry_rel = sys.argv[1], os.path.abspath(sys.argv[2]), sys.argv[3]
edit_rel = sys.argv[4] if len(sys.argv) > 4 else entry_rel
env = dict(os.environ)
p = subprocess.Popen([lsp], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=open(os.path.join(root, '..', os.path.basename(root) + '.lsp.stderr'), 'wb'), env=env, cwd=root)
q = queue.Queue()
def reader():
    f = p.stdout
    while True:
        line = f.readline()
        if not line: return
        if line.startswith(b'Content-Length:'):
            n = int(line.split(b':')[1]); f.readline(); body = f.read(n); q.put(json.loads(body))
threading.Thread(target=reader, daemon=True).start()
nid = [0]
def send(method, params, req=False):
    msg = {"jsonrpc": "2.0", "method": method, "params": params}
    if req:
        nid[0] += 1; msg["id"] = nid[0]
    b = json.dumps(msg).encode(); p.stdin.write(b"Content-Length: %d\r\n\r\n" % len(b) + b); p.stdin.flush()
    return nid[0]
diags = {}
def pump(quiet=3.0, total=60):
    start = time.time(); last = time.time()
    while time.time() - start < total:
        try:
            m = q.get(timeout=0.2)
        except queue.Empty:
            if time.time() - last > quiet: return
            continue
        last = time.time()
        if m.get("method") == "textDocument/publishDiagnostics":
            uri = m["params"]["uri"]; diags[uri] = [(d["range"]["start"]["line"], d["message"][:90]) for d in m["params"]["diagnostics"]]
        elif "id" in m and "method" in m:
            send_resp = {"jsonrpc": "2.0", "id": m["id"], "result": None}
            b = json.dumps(send_resp).encode(); p.stdin.write(b"Content-Length: %d\r\n\r\n" % len(b) + b); p.stdin.flush()
uri_of = lambda rel: "file://" + os.path.join(root, rel)
send("initialize", {"processId": os.getpid(), "rootUri": "file://" + root, "capabilities": {}}, req=True)
pump(1)
send("initialized", {})
texts = {}
def open_(rel):
    texts[rel] = open(os.path.join(root, rel)).read()
    send("textDocument/didOpen", {"textDocument": {"uri": uri_of(rel), "languageId": "vilan", "version": 1, "text": texts[rel]}})
open_(entry_rel)
if edit_rel != entry_rel: open_(edit_rel)
pump(4)
def show(tag):
    print("==", tag)
    for uri in sorted(diags):
        print("  ", uri.split(root)[-1], diags[uri])
show("after open")
version = [1]
def change(rel, text):
    version[0] += 1; texts[rel] = text
    send("textDocument/didChange", {"textDocument": {"uri": uri_of(rel), "version": version[0]}, "contentChanges": [{"text": text}]})
orig = texts[edit_rel]
change(edit_rel, orig + "\n// keystroke\n"); pump(4); show("after keystroke 1 in " + edit_rel)
change(edit_rel, orig + "\n// keystroke 2\n"); pump(4); show("after keystroke 2 in " + edit_rel)
change(edit_rel, orig); pump(4); show("after undo")
send("shutdown", {}, req=True); pump(1, 3); send("exit", {})
try: p.wait(5)
except Exception: p.kill()
