#!/usr/bin/env python3
"""Drive kolt's real server (a scratch copy) on one backend and print its
login exchange, one line per exchange: status, content-type, body with any
64-hex token masked. Usage: exchange.py <leg-name> <command...>
Both legs share the scratch kolt.db, so a legs' ORDER is the cross-backend
check: an account registered by one leg must log in on the other."""
import json, re, socket, subprocess, sys, time, http.client

leg = sys.argv[1]
script = sys.argv[2]
command = sys.argv[3:]
proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
line = proc.stdout.readline()
if not line.startswith("kolt: "):
    print("server did not announce:", line, proc.stderr.read())
    sys.exit(1)
port = int(line.strip().rsplit(":", 1)[1].strip("/"))

def call(method, path, body=None):
    connection = http.client.HTTPConnection("127.0.0.1", port, timeout=60)
    payload = None if body is None else json.dumps(body)
    started = time.process_time()
    connection.request(method, path, body=payload, headers={"Connection": "close"})
    response = connection.getresponse()
    data = response.read().decode()
    headers = {k.lower(): v for k, v in response.getheaders()}
    connection.close()
    tokens = re.findall(r"[0-9a-f]{64}", data)
    masked = re.sub(r"[0-9a-f]{64}", "<token:64hex>", data)
    return (f"HTTP/1.1 {response.status} {response.reason}", headers.get("content-type"),
            headers.get("cache-control"), headers.get("content-length"), masked), tokens

steps = [s.split("|") for s in script.split(";")]
seen_tokens = []
for method, path, *body in steps:
    payload = json.loads(body[0]) if body else None
    answered, tokens = call(method, path, payload)
    seen_tokens.extend(tokens)
    print(f"{leg}\t{method} {path}\t" + "\t".join(str(x) for x in answered))
print(f"{leg}\ttokens\t{len(seen_tokens)}\tdistinct={len(set(seen_tokens))}\t" + ",".join(seen_tokens))
proc.terminate()
proc.wait()
