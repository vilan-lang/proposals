N164's mechanism, measured. The old burst pin typed keystroke k at t = k x (DEBOUNCE_MS + 20) and the server's
debounce task for keystroke k wakes at t + DEBOUNCE_MS: a 20 ms margin before keystroke k+1 supersedes it. A
debounce task that wakes later than that sees a newer generation and returns without analyzing, so a host with
> 20 ms of scheduling jitter on the timer wake folds the burst (every task superseded; only the last analyzes:
"1 started", the Windows-shard message).

Repro on Linux (load does NOT do it: 40 busy loops, load 35 on 16 cores, 6 runs, started=8 every time; SIGSTOP
stalls do not either): in `a_burst_of_edits_performs_one_complete_analysis_plus_at_most_one_partial` take the
sleep to `DEBOUNCE_MS - 40` -> `the burst must actually schedule analyses ... — 1 started`. The new form waits for
the server's `started` counter, so it has no margin to lose.

The second M26 burst (the CPU-ratio pin near `per_keystroke < full_cpu`, main.rs, same sleep) has the same
shape but cannot go red from folding: a folded burst costs LESS CPU per keystroke. Left as is.
