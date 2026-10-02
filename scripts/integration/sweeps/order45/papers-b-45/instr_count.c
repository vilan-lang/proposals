/* performance-gates.md §1's probe: does this machine expose the hardware instruction
 * counter (instructions:u) to user space? Runs argv[1..] with the counter enabled on
 * exec, inherited by threads, and prints the user-space instruction count.
 *   gcc -O2 -o instr_count instr_count.c && ./instr_count vilan check . */
#define _GNU_SOURCE
#include <linux/perf_event.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/syscall.h>
#include <sys/wait.h>
#include <unistd.h>
int main(int argc, char **argv) {
  int go[2]; if (pipe(go)) return 2;
  pid_t child = fork();
  if (child == 0) { char c; close(go[1]); if (read(go[0], &c, 1) != 1) _exit(3); execvp(argv[1], argv + 1); _exit(4); }
  struct perf_event_attr a; memset(&a, 0, sizeof a);
  a.type = PERF_TYPE_HARDWARE; a.size = sizeof a; a.config = PERF_COUNT_HW_INSTRUCTIONS;
  a.disabled = 1; a.enable_on_exec = 1; a.inherit = 1; a.exclude_kernel = 1; a.exclude_hv = 1;
  int fd = syscall(SYS_perf_event_open, &a, child, -1, -1, 0);
  if (fd < 0) { perror("perf_event_open(instructions:u)"); kill(child, 9); return 1; }
  close(go[0]); if (write(go[1], "x", 1) != 1) return 2; close(go[1]);
  int status; waitpid(child, &status, 0);
  long long n = 0; if (read(fd, &n, sizeof n) != sizeof n) { perror("read"); return 1; }
  printf("instructions:u %lld\n", n); return 0;
}
