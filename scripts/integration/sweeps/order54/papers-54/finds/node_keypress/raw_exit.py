import os, pty, sys, select, time
for mode in ["exit", "throw"]:
    pid, fd = pty.fork()
    if pid == 0:
        os.execvp("sh", ["sh", "-c", f"node raw_exit.mjs {mode} 2>/dev/null; stty -a | tr ' ' '\\n' | grep -x -e '-\\?icanon' -e '-\\?echo'"])
    out = b""
    end = time.time() + 3
    while time.time() < end:
        r, _, _ = select.select([fd], [], [], 0.05)
        if r:
            try:
                chunk = os.read(fd, 4096)
            except OSError:
                break
            if not chunk:
                break
            out += chunk
    print(mode, out.decode().split())
