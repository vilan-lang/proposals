# Drive a prompt program on a pty: the prompt must appear BEFORE any input,
# each typed line (cooked mode: Enter sends \r, ICRNL turns it into \n, with
# echo) answers, Backspace edits the line, and Ctrl-D at the second prompt ends
# the input. Usage: drive.py <argv...>
import os, pty, sys, select, time
pid, fd = pty.fork()
if pid == 0:
    os.execvp(sys.argv[1], sys.argv[1:])
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
print("before input:", read_for(1.0))
os.write(fd, b"annx\x7f\r")   # a typo, Backspace, Enter
print("after line 1:", read_for(0.5))
os.write(fd, b"\x04")          # Ctrl-D at an empty line: end of input
print("after ctrl-d:", read_for(1.0))
_, status = os.waitpid(pid, 0)
print("exit code:", os.waitstatus_to_exitcode(status))
