# Drives keypress.mjs (or any command) through a pty, writing each sequence
# with a pause, and prints what came back.
import os, pty, sys, time, select
seqs = [b"a", "é".encode(), b"\x1b[A", b"\x1b[B", b"\x1b[C", b"\x1b[D", b"\x1b[H", b"\x1b[F",
        b"\x1bOH", b"\x1b[1~", b"\x1b[4~", b"\x1b[5~", b"\x1b[6~", b"\x1b[3~", b"\x1b[2~",
        b"\x1bOP", b"\x1b[15~", b"\x1b[24~", b"\x7f", b"\x08", b"\t", b"\x1b[Z", b"\r", b"\n",
        b"\x03", b"\x04", b"\x1b[1;5C", b"\x1b[1;2A", b"\x1bx", b"\x01", b"\x1b[200~pasted\x1b[201~",
        b"\x1b", b"q"]
pid, fd = pty.fork()
if pid == 0:
    os.execvp(sys.argv[1], sys.argv[1:])
out = b""
def drain(t):
    global out
    end = time.time() + t
    while time.time() < end:
        r, _, _ = select.select([fd], [], [], 0.02)
        if r:
            try:
                out += os.read(fd, 65536)
            except OSError:
                return
drain(0.8)
for s in seqs:
    os.write(fd, s)
    drain(0.15 if s != b"\x1b" else 1.2)
drain(0.5)
sys.stdout.write(out.decode("utf-8", "replace"))
