# Does SIGTERM to `vilan run` reach the program it started?
import subprocess, sys, time, os, signal
W = sys.argv[1]
env = dict(os.environ, VILAN_STD=W + "/vilan/std")
p = subprocess.Popen([W + "/target/debug/vilan", "run", "prompt.vl"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, env=env)
p.stdout.read(6)  # "name? "
kids = subprocess.run(["pgrep", "-P", str(p.pid)], capture_output=True, text=True).stdout.split()
print("vilan run", p.pid, "children", kids)
p.send_signal(signal.SIGTERM); p.wait()
time.sleep(0.5)
for k in kids:
    alive = os.path.exists(f"/proc/{k}")
    print("child", k, "alive after SIGTERM to vilan run:", alive)
    if alive:
        os.kill(int(k), signal.SIGKILL)
