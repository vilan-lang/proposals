# Drive scan_line.mjs on a pty: the prompt must appear BEFORE any input is
# written (the interactive prompt S1 pins), then answer, then the process
# must exit with the terminal still open (stdin paused, not holding the loop).
import os, pty, sys, select, time
pid, fd = pty.fork()
if pid == 0:
    os.execvp("node", ["node", sys.argv[1] if len(sys.argv) > 1 else "scan_line.mjs"])
def read_for(t):
    out = b""; end = time.time() + t
    while time.time() < end:
        r, _, _ = select.select([fd], [], [], 0.02)
        if r:
            try: c = os.read(fd, 4096)
            except OSError: break
            if not c: break
            out += c
    return out
t0 = time.time()
first = read_for(0.6)
print("before input:", first)
os.write(fd, b"ann\r")
print("after line 1:", read_for(0.3))
os.write(fd, b"bob\r")
rest = read_for(1.5)
print("after line 2:", rest)
wpid, status = os.waitpid(pid, os.WNOHANG)
print("exited by itself:", wpid == pid, "status", status)
