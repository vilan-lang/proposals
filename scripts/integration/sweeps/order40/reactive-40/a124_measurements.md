# A124 S1 — the measurements behind `proposal/reactive-pipeline.md` §6

Lane reactive-40, Order 40. Tree: `next @49de3915` + this lane's A123 commit,
worktree `.claude/worktrees/reactive-40`. Toolchain: `target/debug/vilan` built
in that worktree with `vilan/std/src/reactive_pipeline.vl` present.

## Method

callgrind Ir, `node --jitless`, on the program EMITTED by `vilan build` (not on
the compiler). Per-iteration Ir is the **slope between 1 and 201 iterations**, so
node's startup (~168 M Ir) and the graph's construction cancel — the method
`reactive-turns.md` §7.5 established for door 2's cost table.

    valgrind --tool=callgrind --callgrind-out-file=/dev/null node --jitless <program>.mjs

loadavg 25.6 / 44.1 / 52.9 at the first batch, 58.8 at the second, 54.7 at the
third (twelve lanes building). Ir is an instruction count and does not move with
load; wall-clock is not used anywhere in this file.

Every program prints `total=21105`, the same value on both models — the control
that the two are computing the same thing.

## The programs

Each is a five-deep derivation over one root. `cold` uses
`std::reactive_pipeline`'s `map_node`; `eager` uses today's `Source::map`.

| id | shape |
|---|---|
| `meas` | build the chain once, then per frame: `root.set(frame)` and `total += chain.get()` — a PULL leaf |
| `measw` | build the chain once plus one leaf subscriber, then per frame: `root.set(frame)` — a PUSHED leaf |
| `measb` | per iteration: build a whole new five-deep chain and read it once — CONSTRUCTION cost |

## Raw counts

| program | Ir @ 1 | Ir @ 201 | slope / iteration |
|---|---:|---:|---:|
| `meas` cold | 168,719,153 | 170,783,746 | **10,323** |
| `meas` eager | 169,817,102 | 178,762,005 | **44,725** |
| `measw` cold | 169,691,509 | 172,178,729 | **12,436** |
| `measw` eager | 169,856,730 | 178,429,577 | **42,864** |
| `measb` cold | 167,974,738 | 178,265,786 | **51,455** |
| `measb` eager | 169,122,510 | 194,178,098 | **125,278** |

## The table as the paper prints it

| a five-deep derivation | cold pipeline | five `map` cells | ratio |
|---|---:|---:|---:|
| construct, then read once | 51,455 Ir | 125,278 Ir | 0.41× |
| per frame: one write, one pull read | 10,323 Ir | 44,725 Ir | 0.23× |
| per frame: one write, one pushed leaf | 12,436 Ir | 42,864 Ir | 0.29× |

## The evaluation counts (not Ir — the semantic claim)

`a124_s1_evidence.vl` in this directory, run through the same toolchain:

    built evals=0
    cold, no subscriber: evals=0        # three root writes, zero work
    one pull: 9 evals=5                 # the reader pays the five
    one leaf sub: evals=5
    two leaf subs: evals=10             # the cold contract, by design
    cell between: upper=2 lower=6       # the segment above a `.cell()` runs once
    diamond: (20,102)(20,102)           # twice, and SETTLED both times

The same four claims are pinned in
`crates/vilan-core/tests/inference/lifetimes.rs` under `a124_s1_*`, each shown
red with its mechanism planted back:

| pin | planted bug | red reading |
|---|---|---|
| `..._a_cold_chain_with_no_subscriber_evaluates_nothing` | the node registers at construction | `0 / 45 / 9 / 50` |
| `..._a_cold_chain_evaluates_once_per_leaf_subscriber` | `on_settle` written as a blanket over the payload path | `15 / 30` |
| `..._a_cell_between_runs_the_segment_above_it_once` | `.cell()` does not register upstream | `0 / 0` |
| `..._a_diamond_pulls_a_settled_pair_and_fires_twice` | `Combine` registers only its left arm | `(20,102)` once |
