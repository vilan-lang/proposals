SIGTERM to `vilan run` does not reach the program it started.

  python3 term.py <vilan worktree>     (runs <worktree>/target/debug/vilan run prompt.vl)
  vilan run 900435 children ['900574']
  child 900574 alive after SIGTERM to vilan run: True

`vilan run` waits on node (or the native binary) with `Command::status()` and
installs no handler, so a supervisor, an editor task or a test harness that
stops `vilan run` with SIGTERM (or kills it) orphans the program - here parked
on stdin; a server keeps its port. Ctrl-C in a terminal is unaffected (SIGINT
goes to the whole foreground process group). `exit_code_of` also reports a
child killed by a signal as exit 1 rather than 128+signal.
Met by std-54's interactive-stdin harness: a red step killed `vilan run` and
left the native binary running (`process.rs`'s `Conversation::abandon` now
closes the child's stdin first).
