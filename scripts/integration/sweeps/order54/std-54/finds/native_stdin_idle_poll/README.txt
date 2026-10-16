CPU a program burns while `prompt`/`read_line` waits on a silent, open stdin:
  python3 idle.py <native prompt binary> node prompt.mjs
std-54's measurement (debug native binary, node v24.2.0, load ~26 on 16 cores):
  native 0.12 s CPU over 5 s waiting (~2.4 %), node 0.00 s.
The native executor polls its I/O sources every IO_POLL_INTERVAL (1 ms) while a
read waits (proposal/terminal.md §5.2 names it as the documented price and the
refinement).
