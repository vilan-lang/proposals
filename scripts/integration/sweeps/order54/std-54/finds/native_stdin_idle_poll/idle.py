# CPU a program burns while a read waits on a silent, open stdin pipe.
import subprocess, sys, time, os
for argv in [sys.argv[1:2], sys.argv[2:]]:
    p = subprocess.Popen(argv, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL)
    time.sleep(1.0)
    def ticks():
        f = open(f"/proc/{p.pid}/stat").read().rsplit(")", 1)[1].split()
        return int(f[11]) + int(f[12])
    a = ticks(); time.sleep(5.0); b = ticks()
    hz = os.sysconf("SC_CLK_TCK")
    print(argv[-1].split("/")[-1], f"{(b-a)/hz:.2f} s CPU over 5 s waiting")
    p.stdin.close(); p.wait()
