# The A110 door-2 instrument (lane papers-38, Order 38)

Seven scratch copies of `std`, reached through `$VILAN_STD`, so door 2 could be
MEASURED without building the compiler and without touching the vilan tree.
`reactive-turns-order-within-a-wave.md` §7.4–§7.6 stands on these; the captured
numbers and transcripts are `../probes/door2_measurement.out`,
`../probes/door2_variants.out` and `../probes/door2_cost.out`.

## Rebuilding it

```sh
T=<the vilan worktree>/vilan          # e.g. …/.claude/worktrees/papers-38/vilan
D=$(pwd)

# The control. NOTE the macro_std sibling — a std copied WITHOUT it resolves
# and then fails to expand `[derive]`, blaming std's own compare.vl
# (a FIND: door2_measurement.out §5).
mkdir -p $D/baseline && cp -r $T/std $D/baseline/std && cp -r $T/macro_std $D/baseline/macro_std

# door 2, phase 2 off a SNAPSHOT of the parked queue.
mkdir -p $D/vilan && cp -r $T/std $D/vilan/std && cp -r $T/macro_std $D/vilan/macro_std
python3 patch_door2.py $D/vilan/std/src/reactive.vl
```

`popped`, `popped-scrub`, `scrubonly`, `fast` and `nosort` are the five
variants the section compares, each a small edit on top of `vilan` or
`baseline`; `door2_measurement.out`'s header lists what each one changes, and
`diff -u baseline/std/src/reactive.vl <variant>/std/src/reactive.vl` is the
edit itself. `fast` is the one the cost numbers and the estate sweep use
— a keyed park SET for O(1) dedup and liveness, one insertion sort per settle,
and `dispose` resolving the draining turn.

## What the instrument is NOT

It is not a proposed implementation. Three shortcuts, each named where it
matters:

- the derivation/effect split is a module-level flag raised by the combinators
  while they attach, where a real build gives `Subscriber` a `kind` set at
  `on_change` time (A110 door 2 says so);
- door 1's per-subscriber liveness bit is NOT reproduced — `fast`'s park set is
  the same idea one scope up, and if door 1 has landed, phase 2 should read its
  flag instead;
- the sort is an insertion sort, which §7.5 measures as 60% of door 2's cost
  and names as the thing to replace.

## The sweep

`sweep/` is `vilan/test` (131 programs) and `sweep2/` is
`vilan/examples` + `vilan/benchmarks` (36), each run under `baseline/std` and
`fast/std` with exit codes and stdout captured. Regenerate with the loop in
`door2_measurement.out` §4; the result was zero output differences in the test
corpus and two noise differences (wall-clock rates, a pid) outside it.
