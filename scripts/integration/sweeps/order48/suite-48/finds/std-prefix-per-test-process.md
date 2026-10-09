# Why N151's door (a) cannot reach most of the suite (suite-48, Order 48)

Measured on next @dfe0c5fc, debug test profile, one full `cargo nextest run --workspace -j 6`
with a target runner recording each test process's CPU (user+sys, children included):

- 9,797 tests, 13,002 CPU-s. `inference` is 4,737 CPU-s (36.4%): 5,212 tests, 0.91 s each.
- A 41-test sample of `inference` (`VILAN_PHASE_TIMING=1`, every 130th test): 46 analyses
  (1.12 per test), 967 ms CPU per test, of which load+walk 343 ms + base 174 ms = 53.5% is
  the std world (std's share of checks and post-passes comes on top).
- nextest runs every test in its own PROCESS, so a std world built in-process dies with the
  test that built it. Where one process does run many analyses it already shares: the docs
  gate's 279 analyses hit the base cache 166 times (`VILAN_COUNTERS=1`). The differentials'
  CLEAN legs are cold by construction (that is what they compare against).

So "one std world per test binary" needs either a cross-process std (M36 §6.15) or a
fork-server harness; S1's `load_hot_modules` can extend a stored world only inside the
process that stored it.
