# Performance gates — what fails a build for being slow (M105)

> Status: **RULED 2026-10-02** — Q1–Q12 as recommended (the owner); the build (S1–S8) is Order 46's, the seal-time comparison exists. Drafted 2026-10-02, for the owner to rule on (Q1–Q12). Written by
> lane papers-b-45 of Order 45. Nothing in the compiler changed. Every number
> was measured on the owner's machine with the released `vilan 0.42.1
> (44f45dd3b)` and `vilan-lsp 0.42.1` (`~/.vilan/bin`), or is cited and marked
> as cited. The machine is an AMD Ryzen 7 9800X3D (8 cores, 16 threads), WSL2,
> 30 GB. Other lanes were running throughout, so every timing has its 1-minute
> loadavg beside it. That load is the condition this paper has to design for,
> not a flaw in the record.
>
> Probes and raw logs: `scripts/integration/sweeps/order45/papers-b-45/`. The
> paper cites them by file name. `variance.py` runs interleaved `vilan check`
> runs (wall, CPU, loadavg). `instr_count.c` counts hardware user-space
> instructions through `perf_event_open`. `callgrind_runs.sh` runs repeated
> callgrind passes. `gen_slope.py` writes a generated package of N modules. The
> `*.csv`/`*.txt` files are their outputs. kolt is a `git archive` of
> `984a1dfb` plus its untracked `src/search-dict`, in a scratch directory.
>
> Related: M105 (this item), M103/M104/M101/M99/M100 (the open perf work),
> E236 (the LSP harness, ruling R-i), E121 and `editor-latency.md` (the editor
> mandate and its rulings Q1–Q6), `perf-baseline.md` (the harness, and §1.4's
> rule against timing assertions in the gate), `REPORT-perf-kolt-45.md`
> (v0.42.0's 3× regression), `perf_compare.py` + `seal.sh` (the seal's perf
> leg, built this order).

## 0. The ask, and the answer up front

The owner asked whether the test suite checks timings or only results. He
wants strict time-to-completion limits for two reasons: to catch regressions,
and to show where optimization is needed. He also reported that `vilan check`
and the LSP feel slow on his high-end machine and sluggish on a MacBook.

**Today the suite checks results, not time.** Only a handful of cheap
counter and shape pins run in the gate. The full `perf_baseline` run and all
four E121 budget tests are `#[ignore]`d. v0.42.0 shipped a 3.3× CPU and 3.9×
memory regression on kolt with every gate green (`REPORT-perf-kolt-45.md`).

The measurements below settle what can carry a strict limit:

1. **Wall time can't, anywhere.** kolt's `vilan check` read 3.19 s to 13.54 s
   across ten runs of the same binary on the same input (§2.1).
2. **CPU time can, but only on a quiet machine.** The same check read 3.19 s
   to 5.80 s of CPU as the load moved from 10 to 20. In the LSP, a kolt leaf
   keystroke read 2,280 ms of CPU to diagnostics at load 16, against 1,130 ms
   at load 2.5. That is 2× from load alone (§2.1).
3. **Instruction counts can, on any Linux machine, under any load.** Hardware
   `instructions:u` read kolt's check as 33,397,995,953 to 33,398,036,048
   across five runs at load 21–24, a spread of **1.2 parts per million**,
   while wall time on those same runs went 3.46 s to 10.16 s. Callgrind's Ir
   is as stable (0.12 ppm) but runs about 70× slower (§2.2).

So the recommendation is three tiers of gate, each in the place it can be
trusted:

- **Compiler counters and shape pins in the normal gate**, on every lane and
  every merge. They are deterministic and the same on every machine and
  profile.
- **Instruction-count budgets per corpus program in a required CI job**, and
  at the seal.
- **CPU-time comparison against the previous release on kolt, on the owner's
  quiet machine**, at the seal and the cut. The cut refuses to tag over a red
  verdict.

"Strict time to completion" is honoured literally in that last tier. Elsewhere
an instruction budget stands in for it, converted at the reference machine's
measured rate of about 11 G instructions per CPU-second on kolt (§2.4).

Two measurements change the optimization order (§7):

- **`vilan check` is superlinear in package size.** On a generated plain-code
  package, doubling from 24,485 to 48,965 lines multiplies instructions by
  3.35, and the world-resolution fixpoint, the build and the emission walk
  each grow 4.5× per doubling. That is quadratic, filed below as find 1. A
  two-size shape pin in the gate would have caught it.
- **kolt's check runs on one thread at a time.** Wall equals CPU to three
  digits (3.191 s against 3.187 s). The phase split says parallel analysis
  could give ×1.8–2.5 wall on 8 cores, ×1.9–2.8 on 16, and up to ×3.2 with
  the two entries overlapped.

## 1. What is gated today

Very little, and none of it on time:

| gate | what it asserts | where | cost |
|---|---|---|---|
| `the_const_pass_scales_with_its_const_sites_and_not_with_their_square` | a ratio of two sizes of one input stays under 6× (`perf-baseline.md` §6.3) | nextest | 4.4–5.4 s (seal logs) |
| `perf_baseline_harness_smoke` ×2, two statistics pins | the instrument works | nextest | 0.7–1.3 s |
| M94/M95/M97/M98 counter pins (`r11_instantiations_do_not_mint_a_type_slot_per_place_in_the_program`, `classifying_an_instantiation_mints_no_slot_its_substitution_cannot_change`, `a_refinement_after_the_passes_computes_no_selection_the_passes_already_made`, `a_second_emission_of_one_program_computes_no_impl_selection`) | a count (type slots, selections computed) on a small program, or its growth between two sizes | nextest | one small analysis each |
| `perf_baseline_full_run`, `perf_baseline_lsp_edit_latency` | nothing (they report) | `#[ignore]`, weekly `ignored-pins.yml` (advisory) | minutes |
| `keystroke_path_budget`, `keystroke_path_budget_view`, `diagnostics_budget`, the exhibit gate | E121's budgets, release-only (E141) | `#[ignore]` | minutes |
| `perf_compare.py` in `seal.sh` | kolt check CPU and RSS, tip vs previous release, red past ×1.10 | the seal, on the owner's machine | about 10 kolt checks |

The counter pins are the right kind of gate. They are deterministic, and each
one pins exactly the mechanism a regression broke. They were added after the
regressions they guard against, though. Nothing gated the aggregate, so a new
mechanism could regress (R39's resource traits, `REPORT-perf-kolt-45.md`)
without any counter seeing it. `perf_compare.py` is the first aggregate gate,
and §8 finds two defects in it.

## 2. The metric, measured

### 2.1 Wall and CPU time move with load; CPU much less than wall, but still too much

Ten interleaved runs per subject, at ambient load that rose from 8.7 to 20.4
during the probe (`variance-ambient.csv`):

| subject | lines | wall min–max (spread) | CPU min–max (spread) | CPU CV |
|---|---:|---|---|---:|
| `examples/math` | 22 | 0.038–0.243 s (381%) | 0.037–0.094 s (110%) | 27% |
| `examples/walkthrough` | 628 | 1.03–4.41 s (221%) | 1.03–2.09 s (71%) | 22% |
| kolt | 24,288 | 3.19–13.54 s (242%) | 3.19–5.80 s (62%) | 21% |

The CPU column follows the load. kolt's first five runs at load 9–10 read
3.19–4.31 s. The last five at load 17–20 read 4.19–5.80 s. Five more runs at
a steadier load of 10.2–10.8 (`variance-website-kolt.csv`) read 3.10–3.77 s,
a 19% spread with a CV of 6.9%.

To show the cause directly, a controlled probe added 16 busy-loop processes
(`variance-spin16.csv`). kolt's CPU median went from 3.47 s to 4.75 s (+37%),
and the spread inside that run fell to 14%.

CPU time inflates under load because the 9800X3D shares each core between two
SMT threads, and a neighbour on the sibling thread slows the compiler's thread
while the CPU clock keeps running. A shared CI runner is a loaded machine by
construction, which `perf-baseline.md` §1.4 already recorded (E32/E39/E40).

The LSP behaves the same way. `lsp-variance.txt` is E236's harness, ten runs
of two scenarios at load 16.6–16.9:

| edit | CPU to diagnostics, min–median–max | CV | the same row at load 2.5 (`editor-45/r2-base.txt`) |
|---|---|---:|---:|
| leaf keystroke (`views.vl`) | 1,910–2,280–2,680 ms | 13% | 1,130 ms |
| `model.vl` keystroke | 580–615–640 ms | 3% | 370 ms |

A quiet-machine CPU budget therefore holds only on a quiet machine. E121's
Order 27 note (2.3× at loadavg 80–125) and editor-45 (about 30% over load 5–7)
recorded the same thing. The seal can enforce a CPU budget only if it refuses
to measure above a load ceiling. `perf_compare.py` has no such ceiling today
(§8, find 3).

### 2.2 Instruction counts don't move

The same binary, the same inputs, counted two ways:

| metric | subject | runs | spread | load during | wall during |
|---|---|---:|---:|---|---|
| `instructions:u` (hardware, `instr_count.c`) | math | 10 | 10 ppm (252,303,893–252,306,503) | 21–24 | 0.05–0.50 s |
| | walkthrough | 5 | 0.9 ppm (10.634 G) | 21–24 | 1.27–5.36 s |
| | kolt | 5 | 1.2 ppm (33.398 G) | 21–24 | 3.46–10.16 s |
| callgrind Ir | math | 3 | 1.7 ppm (258.88 M) | 16–18 | — |
| | walkthrough | 3 | 0.17 ppm (10.689 G) | 16–18 | — |
| | kolt | 3 | 0.12 ppm (33.479 G) | 8.5–18 | — |
| peak RSS (`wait4`) | kolt | 3 | 0.04% (265,096–265,204 KB) | ~7 | — |

The small residual comes from per-process randomness such as hash seeds and
ASLR. Even 10 ppm is a thousand times smaller than a 1% regression.

The two counters agree to within 2.6% (math), 0.5% (walkthrough) and 0.24% (kolt). Callgrind also counts the dynamic loader
and counts some instructions differently, so a budget must name which counter
it uses.

**Hardware counters work on this machine.** `perf_event_open` with
`PERF_COUNT_HW_INSTRUCTIONS`, `exclude_kernel`, `inherit` (it follows the
second entry's thread) and `enable_on_exec` runs at native speed under WSL2.
`perf_event_paranoid` is 2, which allows counting your own children. Whether
GitHub's `ubuntu-latest` runners expose a virtual PMU was **not measured**.
That is slice S2's first job, and callgrind is the fallback.

Peak RSS is also stable enough to budget, at 0.04%.

### 2.3 What each candidate gate costs

| gate | subject | cost measured here |
|---|---|---|
| `instructions:u` | math | native: 0.05 s quiet |
| | all eleven examples | 45.2 G instructions in total, about 4–5 s of CPU (`examples-instructions.csv`) |
| | kolt | native: 3–10 s wall depending on load |
| callgrind | math | 3.9–6.0 s |
| | walkthrough | 63–87 s |
| | kolt | 125–229 s (125 at load 8.5, 229 at load 18; callgrind's own wall moves with load too) |
| `perf_compare.py` (5 interleaved runs, two binaries) | kolt | about 10 checks, 30–60 s, plus the copy |
| E236 harness | 2 scenarios × 10 runs | minutes (not timed) |
| a counter or shape pin | a small program | one or two analyses of a small program, as today's pins |

Under callgrind the whole example set would take about 5–6 minutes (45 G
instructions at the measured 6–8 s per G for walkthrough). With hardware
counters it takes seconds. The callgrind fallback is affordable for a CI job.
It is not affordable for a per-test gate.

### 2.4 Converting time budgets into instruction budgets

On this machine, kolt's check runs 33.40 G instructions in 2.97–3.28 s of CPU
at load 7–10 (`kolt-rss.txt`, `variance-website-kolt.csv`). That is
**10.2–11.2 G instructions per CPU-second**. At that rate E121's 500 ms to
diagnostics is about **5–5.5 G instructions**, and a 1 s `vilan check` is about
11 G. The rate is a property of this workload on this microarchitecture: Zen 5
with the X3D cache. It is the conversion factor for the reference machine
class, and the seal re-measures it each time on the quiet run (Q3).

Two limits apply:

- Instruction counts are per ISA. A MacBook runs ARM instructions, so a count
  budget doesn't transfer to it (§6.3).
- Counts differ between debug and release builds by more than a constant.
  `perf-baseline.md` §2.4 measured debug/release at 5.6–9.7× depending on the
  subject. Instruction budgets must be taken on release binaries. nextest
  builds debug, which is why the in-gate tier is compiler counters (§3).

### 2.5 Where "strict time to completion" can be honoured literally

| place | literal time limit? | what carries the limit |
|---|---|---|
| The owner's machine, quiet (load guard), at the seal and the cut | **yes, CPU time**: E121's absolute targets and the ×1.10 release comparison | CPU via `perf_compare.py` and the E236 harness |
| CI (shared runners, 4 vCPU public / 2 private, cited from GitHub's runner table) | no: a loaded machine by construction | instruction budgets per corpus program |
| A lane's worktree on the loaded dev machine | no: load 6–24 all day | compiler counters and shape pins in nextest; instruction counts on demand |
| A MacBook | not measured | an informational CPU row in the nightly (§6.3) |

## 3. The three tiers, and where each runs

**Recommendation: three tiers, each red in a different place.**

| tier | metric | runs in | refuses |
|---|---|---|---|
| **T1 counters and shapes** | compiler counters (type slots minted, impl selections computed, analyses run per LSP edit, const fuel, expressions walked) as exact numbers on fixed small programs, or as growth ratios between two sizes (M4's method) | `cargo nextest` (debug is fine: counts don't depend on profile) | every lane's gate and every merge |
| **T2 instruction budgets** | `instructions:u` (callgrind Ir where there is no PMU) per corpus program, on a release build, against `perf/budgets.toml` | a new required CI job `perf`; the seal (adds kolt and the website) | a PR or merge to next; the seal |
| **T3 time against the previous release** | CPU time and peak RSS on kolt (`vilan check`, E236 rows), tip vs installed release, interleaved; refused above a load ceiling | `seal.sh` (exists); `cut-release.sh` reads the seal's verdict | the seal; the release tag |
| **report** | the full `perf_baseline`, E236's table, a profiling-build callgrind top 25, a macOS row | a nightly or weekly workflow, and the cut | nothing: it names the next optimization |

**Why counters in nextest and not instruction counts:** nextest builds debug,
runs 9,000+ tests in parallel, and runs on every lane's loaded worktree.
Instruction counts there would be debug counts (§2.4). Counters are
deterministic everywhere.

The four M94–M98 pins show the shape that works:

- a count on a small program, or the growth of a count between two sizes;
- with a message that names the mechanism.

The family to add: a two-size package-growth pin (§6.2, red today), analyses
per LSP edit (M104's shape), and a bytes-allocated counter.

**Why T2 is a separate CI job and not part of the suite:** it needs a release
build, which costs minutes on a cold cache and nothing on a warm one. It also
needs a machine whose counter it can trust. Keeping it out of the test matrix
leaves the two test shards as they are.

**Why T3 stays on the owner's machine:** kolt is private, and the owner's rule
(E121 Q6) is that kolt never enters vilan's codebase. CPU time also means
nothing on a shared runner (§2.1). The seal is the one point where a quiet,
known machine runs the tip against the release.

**The cut refuses.** `cut-release.sh` already refuses to cut over CI that isn't
green, fail-closed, with `--allow-red-ci` as a loud override (L17). The
performance verdict should join it:

- The seal writes `perf-<sha>.json`, holding the verdict, the load, both
  versions and the rows.
- The cut refuses when the commit to be tagged has no green verdict.
- `--allow-perf-regression "<reason>"` overrides, and the reason goes into the
  release notes. A release that knowingly gets slower says so.

## 4. Budgets and tolerances

**Recommendation:** a ratchet with explicit bumps.

The file is `perf/budgets.toml` in the compiler repo. Each row holds:

- a corpus program;
- its counter;
- its ceiling;
- the release or seal the ceiling was measured at;
- a list of bumps, each with a ratio, a reason and a tracker item.

**Setting a ceiling.** The seal sets each ceiling to the measured count ×
(1 + tolerance). Nobody sets one by hand. The first ceilings are v0.42.1's
counts, which S3 records.

**Tolerance.** Start at **1%** for instruction counts. The noise is at most
10 ppm (§2.2), so the 1% isn't for noise. It absorbs two things not yet
measured:

- the run-to-run difference between CI runner CPUs, since glibc picks
  `memcpy`/`strlen` variants by CPU feature at load time;
- small nondeterminism from hashing.

S2 measures both. If the spread between runners is under 0.2%, the tolerance
drops to 0.5%. If it is several percent, the CI job switches to an A/B
comparison in one job: the previous release's published Linux binary,
downloaded, against the tip, on the same runner. That cancels the machine.

**Measure cumulatively, against the ceiling, not against the parent commit.**
A per-commit 1% threshold lets twenty 0.9% regressions through in one order.
A ceiling doesn't.

T3 keeps `perf_compare.py`'s ×1.10 on CPU and RSS. That is the seal's
tolerance for a quiet-machine CPU measurement whose run-to-run spread at load
around 10 is 6.9% CV (§2.1). It is red only when the load guard passed.

**When a feature legitimately costs more.** The PR that adds the cost adds a
`[[bump]]` row in the same commit: subject, new ratio, a reason in one
sentence, and the tracker item. CI stays green because the ceiling moved
within the same commit. The seal lists every bump since the last release in
the seal report. **The owner approves a bump over 3%, or any bump on kolt's
T3 rows, at the seal.** Smaller bumps ride with the lane's report. That keeps
the owner's attention on the costs that matter without a ruling per percent.

**Locking in an improvement.** At each seal, any subject measured more than
2% under its ceiling has its ceiling lowered to the new count × (1 +
tolerance). The bumps list resets at each release. An improvement is
therefore locked in within one order, and a later change that gives it back
goes red.

## 5. The reference corpus

**Recommendation:** in public CI, the examples plus a generated app shaped like
kolt. The website and kolt run at the seal.

kolt must stand in somewhere, because the examples don't look like it.
`examples-instructions.csv` shows that what a program costs is mostly what it
imports. That matches `perf-baseline.md` §4.4 and perf-kolt-45 ("cost follows
the import closure"):

| example | lines | instructions | note |
|---|---:|---:|---|
| math | 22 | 0.25 G | the reference unit |
| watch | 29 | 0.32 G | |
| browser | 51 | 2.04 G | `std::web` reach alone |
| fullstack | 91 | 4.53 G | |
| router | 132 | 2.57 G | |
| reactive-ui | 234 | 3.31 G | |
| ssr | 115 | 6.31 G | two entries |
| canvas | 437 | 2.05 G | |
| rpc | 464 | 3.01 G | |
| todo | 428 | 10.14 G | two entries |
| walkthrough | 628 | 10.63 G | two entries |
| **website** (sibling repo, `src/` only) | 4,163 | 18.24 G | four entries; entries 2–4 run in parallel |
| **kolt** | 24,288 (18,200 generated lucide) | 33.40 G | two entries, serial |

The examples measure the reach of std and the per-entry fixed cost, which a
change to std moves. They are cheap: 45 G instructions in total. They don't
stand in for kolt's shape: views, `css { }`, the reactive pipe model, an
18,200-line generated icon module, a widely imported model file, and 82
modules in one world. The regression that v0.42.0 shipped only shows at that
shape.

**The stand-in is a generated app shaped like kolt.** It extends the
`keystroke.rs` exhibit generator, E126's view-shaped package of 1,791
functions, and is seeded and committed as a generator, not as output. The
seal calibrates it against kolt: each order, the per-phase split of the
generated app (`VILAN_PHASE_TIMING=passes`) is compared with kolt's. If any
phase's share drifts more than 10 points, re-tuning it becomes a tracker item.
That uses kolt as evidence only, which the owner's rule allows. Nothing of
kolt enters the repo: no fixture, no golden, no copied file (E121 Q6).

**kolt at the seal.** kolt is used as `perf_compare.py` uses it now: a `git
archive` of a pinned commit into scratch, plus the untracked search dictionary,
with the tip and the release run interleaved. The pinned commit has to compile
under both binaries. Where a breaking release makes that impossible, the seal
records that the comparison covered different work. `perf_compare.py` already
prints that note.

**The website at the seal.** It is public, so CI could check it out. It moves
with its own repo, though, which makes a CI ceiling flaky by provenance.
Recommendation: run it at the seal at a pinned commit, beside kolt.

## 6. Targets, not only regressions

### 6.1 E121's numbers as enforced budgets

**Recommendation:** enforce them on kolt at the seal, on the reference
machine. They report red without blocking until first met, then block.

Today's quiet-machine row (`editor-45/r2-base.txt`, v0.42.1, load 2.5)
against the 500 ms target:

| edit | CPU to diagnostics | E121 |
|---|---:|---|
| leaf keystroke | 1,130 ms | **2.3× over** |
| `shared.vl` | 390 ms | met |
| `model.vl` | 370 ms | met |
| `model.vl` with importers open: every open file settled | 5,500 ms | **11× over** (M104) |
| css keystroke | 1,230 ms | 2.5× over |
| parse break / repair | 1,270 / 1,290 ms | 2.5× over |
| keystroke-path requests | ≤ 1.8 ms wall, ≤ 3.1 ms idle CPU | met (<10 ms) |

A target that is red today can't block a seal, or every seal is red.

E236's ruling R-i sets the order: a report first, then a gate once the numbers
hold over two orders. Applied per row, each row becomes blocking at the first
seal where it is green on two consecutive seals. From then on it can't be lost
again.

In CI, the generated app's diagnostics-path cost is budgeted in instructions:
500 ms ≈ 5–5.5 G on the reference class (§2.4). The keystroke-path budget
stays as E141 ruled: a release figure, pinned by the existing
`keystroke_path_budget` test once it runs in the nightly in release.

### 6.2 A `vilan check` budget per 1,000 lines, and the superlinearity it finds

**Recommendation:** budget the shape first, then a per-kLOC target as a
reported number.

A per-1,000-lines figure is only meaningful if cost is linear in lines. It
isn't. `gen_slope.py` writes N plain modules of about 153 lines each: structs
with derives, a list loop, an `Option` match, arithmetic, no views or styles.
`slope.csv` and `slope-phases.txt` hold the results:

| modules | lines | instructions | CPU | peak RSS |
|---:|---:|---:|---:|---:|
| 1 | 158 | 0.63 G | 0.04 s | 28 MB |
| 10 | 1,535 | 0.90 G | 0.06 s | 37 MB |
| 40 | 6,125 | 2.23 G | 0.22 s | 65 MB |
| 80 | 12,245 | 5.09 G | 0.47 s | 104 MB |
| 160 | 24,485 | 14.62 G | 1.46 s | 184 MB |
| 320 | 48,965 | 49.03 G | 5.25 s | 349 MB |

Each doubling multiplies the cost by 2.3, 2.9, then 3.35, an exponent of about
1.8 and rising. At 49,000 lines that is 107 ms of CPU per 1,000 lines, against
36 ms at 6,000.

The per-phase split names the quadratic parts. Thread-CPU, 160 → 320 modules:

| phase | 160 → 320 | factor per doubling |
|---|---|---:|
| world resolution `fixpoint` | 363 → 1,683 ms | ×4.63 |
| `emission-walk` | 421 → 1,912 ms | ×4.55 |
| `build` | 126 → 564 ms | ×4.47 |
| `check_duplicate_trait_impls` | 24 → 144 ms | ×6.10 |
| `platform-color` | 12 → 61 ms | ×5.13 |
| `load+walk` | 342 → 480 ms | ×1.40 (linear) |

A doubling factor above 4 is quadratic in modules or declarations. The probe
doesn't separate which. This is find 1 (§8).

The gate that catches this is cheap, and it is the M4 method again. Check a
generated package at two sizes in one process, interleaved, and bound the
ratio of the counter (instructions, or a compiler counter such as expressions
walked). The bound is ×2.3 per doubling: linear plus margin. Today's
24k → 49k measurement is ×3.35, so the pin is red now. It should land
`#[ignore]`d with find 1's item named, and be un-ignored when the fix lands.

**The per-kLOC target, set from comparators:**

| tool | input | measured or cited | CPU per 1,000 input lines |
|---|---|---|---:|
| `vilan check` 0.42.1 | generated plain code, 6,125 lines | measured | 36 ms |
| | generated plain code, 24,485 lines | measured | 60 ms |
| | generated plain code, 48,965 lines | measured | 107 ms |
| | kolt, 24,288 lines (plus std reach) | measured, 2.97–3.47 s | 122–143 ms |
| `cargo check` (rustc 1.90.0) | `syn` 2.0.117 alone, 50,059 lines, features full+visit+fold+extra-traits, dependencies already checked | measured, 1.22–1.56 s CPU at load 18.7 (`comparators-rustc.txt`) | 24–31 ms |
| `tsc` 5.9.3 `--noEmit` | three local projects, 1.1–1.9 k lines of TS over 72–137 k lines of library and `.d.ts` | measured, tsc "Total time" 0.72–1.11 s (`comparators-tsc.txt`) | 5–11 ms (all lines; `.d.ts` checks lightly) |
| `tsc` (JS implementation) | VS Code 1,505,000 LOC: 77.8 s; Playwright 356,000: 11.1 s; date-fns 104,000: 6.5 s | **cited**, TypeScript team, "A 10x Faster TypeScript" (2025); machine not stated | 31–62 ms |
| TypeScript native port | VS Code: 7.5 s | **cited**, same post | 5 ms |

**Recommended target:** on the reference machine, the marginal cost of a
generated plain-code package is **≤ 30 ms of CPU per 1,000 lines**, measured
as the slope between 24k and 49k lines. Today that slope is 155 ms. The
target is rustc's check on `syn`, and below the cited JS `tsc`. Add a fixed
std-reach cost per entry of ≤ 150 ms for a browser entry; `examples/browser`
is about 190 ms today (2.04 G at about 11 G/s).

For kolt this means a `vilan check` of about 1 s CPU, against 3.0–3.5 s today.
The number is reported per release. It becomes a gate only through the shape
pin above and the T2 ceilings.

### 6.3 Machine classes, and the MacBook

The owner's MacBook complaint wasn't measured: no Mac is attached to this
lane. Instruction budgets are per ISA, so a Mac can't share the x86 ceilings.

**Recommendation:** three classes. Only one of them carries time budgets.

- **R, the reference.** The owner's 9800X3D, quiet (load guard below 2), at
  the seal and the cut. E121's targets and the T3 comparison run here. The
  instructions-per-second conversion (§2.4) is re-measured here.
- **CI.** `ubuntu-latest`, 4 vCPU / 16 GB for a public repo, 2 / 8 for a
  private one (cited from GitHub's runner table). Instruction ceilings only.
- **M, a common dev machine.** GitHub's `macos-14` runner, 3 M1 cores and
  7 GB (cited). The nightly records `vilan check` CPU on the generated app and
  on the website. This is informational: a shared VM's CPU time is noisy
  (§2.1), but a trend over releases is a real signal. The 7 GB matters too,
  because the LSP's VmHWM on kolt is 926 MB on v0.42.1 and 1,042 MB on next
  (`r2-*.txt`).

### 6.4 The per-release report

**Recommendation:** the cut writes `perf/report-vX.Y.Z.md`. It holds:

- the T2 table (every corpus program, this release's count against the last
  release's, with bumps);
- the T3 kolt rows;
- E121's table with targets met and missed;
- the per-kLOC slope;
- the top 25 functions by inclusive instructions from a callgrind run of the
  generated app and kolt on a `profiling`-profile build.

The release binary is stripped. A callgrind of v0.42.1 on kolt resolves only
`malloc`/`free` by name and leaves the compiler's own frames as addresses, so
the profile needs the profiling build (E236's harness says so too).

The report's first line names the single most expensive phase. That answers
"what to optimize next" every release, without a lane having to go and find
out.

## 7. The structural levers, sized from the numbers

**Recommendation for the order of the work:** M103 → M104 → find 1 (the
quadratic) → M101 → an allocator probe → M100 → an on-disk world cache →
parallel analysis within an entry. Cheap and large first, then the
architectural changes.

### 7.1 Where the CPU goes in kolt's check

kolt's check is about 100% single-threaded today. `check_workspace` runs the
first member alone on the calling thread to warm the process caches, then the
rest in threads (`main.rs` 5406–5444). With two entries the second has nothing
to overlap with, so wall equals CPU: 3.1913 s wall against 3.1871 s CPU.

The website, with four entries, overlaps entries 2–4: 1.29 s wall against
1.95 s CPU.

The phase split for kolt (`phase-kolt.txt`, thread-CPU ms, load ~6):

| entry | load+walk | base | build | checks | post-passes (of which contexts+graph) | emission walk | drop | total |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| client (82 modules) | 245 | 334 | 34 | 596 | 808 (368) | 587 | 31 | 2,635 |
| server (53 modules) | 57 | 91 | 22 | 172 | 196 (134) | 35 | 8 | 581 |

On the first check after a cache wipe, macro worlds add about 100 ms. Later
checks read them from `~/.vilan/check-cache`.

### 7.2 Each lever, with its expected gain

| lever | what it removes | expected gain | basis |
|---|---|---|---|
| **M104**: analyse an entry's world once per edit, publish to every open document in it | the dependents sweep (`reanalyze_dependents`) runs one full analysis per open dependent, serially | settle with 3 importers open: 5,500 ms → about 1,100–1,700 ms CPU (−70–80%) | `r2-base.txt`: 420 ms to the edited file, 5,570 ms to idle; the six open files are re-analysed one after another, though most of them sit in the client's one entry world |
| **find 1**: the quadratic phases | fixpoint, build, emission walk at ×4.5 per doubling | at 24k lines they are 910 of 1,460 ms; scaled linearly from 12k they would be 484 ms (−29% of the check); at 49k, 4,159 of 5,250 ms against 968 linear (−61%); the gain grows with size | `slope-phases.txt` |
| **M101**: cache `impl_members_for_bound` across analyses, cache const-eval by content | 31% + 13% of a css keystroke; `refined_edges` 25% | leaf and css keystrokes: 1,130–1,230 → about 550–650 ms CPU (−45–55%) | editor-45's callgrind of the css keystroke, 58.0 G instructions |
| **allocator**: `malloc` + `free` | 21.7% of kolt check instructions (`free` 13.1%, `malloc` 8.5%) | a ceiling of −22%; the real gain from a faster allocator or arenas is not measured, and a one-line probe (mimalloc or jemalloc behind a feature) measures it | callgrind of v0.42.1 on kolt, `cgk/cg.kolt.0` (scratch) |
| **M100**: overlap kolt's two entries | the server's 581 ms waits for the client | wall 3.2 → 2.6 s (×1.22); CPU unchanged; peak memory up | the phase split |
| **on-disk world cache** for the CLI | `load+walk` + `base`: client 579 of 2,635 (22%), server 148 of 581 (25%) | −22–24% CPU per cold `vilan check`; up to about −57% if per-module analyses were reusable too (the LSP's warm leaf keystroke is 1,130 ms against the cold client's 2,635) | the phase split; M99 |
| **parallel analysis within an entry** | the per-function work: `checks`, `emission-walk`, `const-interp` (pessimistic, p = 0.54 client / 0.36 server), plus `load+walk` and post-passes minus `contexts+graph` (optimistic, p = 0.71 / 0.56) | kolt wall, entries still serial: ×1.79–2.48 on 8 cores, ×1.90–2.77 on 16; with entries overlapped too, ×2.31–3.21 on 8 and ×2.46–3.64 on 16; CPU unchanged or higher, memory higher | Amdahl over the phase split (§7.3) |
| skip the `Program` drop at CLI exit | `program-drop` | −1% (39 ms) | the phase split |

### 7.3 What Amdahl says, and what it doesn't

Serial work stays serial in both projections: the world-resolution fixpoint
(`base`, 334 ms on the client), the build, `contexts+graph` (the whole-program
call graph and context threading), and the drop. Under that assumption the
best 16-thread figure is ×2.8 within an entry. That is the ceiling until the
fixpoint itself is parallel or incremental.

Two cautions:

- The 9800X3D has 8 physical cores. Its 16 threads aren't 16× the throughput,
  so the 8-core row is the realistic one for this machine.
- A MacBook Air has 4 performance and 4 efficiency cores, so 8 is optimistic
  there.

Parallel analysis is the largest wall-time lever and the largest design. The
analyzer mints ids sequentially by load order (`editor-latency.md`), and the
caches are process-global mutexes. It needs its own paper.

It also interacts with E121's ruling Q3, which makes the 500 ms a CPU-clocked
budget. Parallel analysis lowers wall time but not CPU, so on its own it can
never turn E121's gate green (Q10).

## 8. Finds, for the integrator to file

1. **`vilan check` is quadratic in package size.** On a generated plain-code
   package, 24k → 49k lines multiplies instructions by 3.35 (14.6 G → 49.0 G,
   5.25 s CPU at 49k). The world-resolution `fixpoint` (×4.63 per doubling),
   `emission-walk` (×4.55), `build` (×4.47), `check_duplicate_trait_impls`
   (×6.10) and `platform-color` (×5.13) are the quadratic phases. A shape pin
   at two sizes should land with the fix. Reproduce with
   `gen_slope.py OUT 160` and `320`, then `VILAN_PHASE_TIMING=passes vilan
   check .`. Severity HIGH: every app's check cost grows with it. Sizing:
   measure first (modules or declarations?), then S–M per phase.
2. **`perf_compare.py`'s peak-RSS verdict is vacuous.** It reads
   `getrusage(RUSAGE_CHILDREN).ru_maxrss`, which is the maximum over every
   child reaped so far, not the child that just ran. Base and tip are
   interleaved, so after the first pair both read max(base, tip), and the RSS
   ratio is ×1.00 whatever the tip does. A two-child probe showed it: a 300 MB
   child, then a 20 MB child, both read 308 MB. The fix is
   `os.wait4(pid, 0)` per child, which returns that child's own rusage. kolt
   under `wait4` reads 265 MB on v0.42.1. Sizing XS.
3. **`perf_compare.py`'s CPU verdict has no load guard.** It records the load
   but never refuses on it. The same binary's kolt CPU moved 3.19 → 5.80 s as
   the load rose from 10 to 20 (§2.1). Interleaving cancels drift only when
   both binaries see the same load. Fix: refuse a CPU verdict above a 1-minute
   loadavg ceiling (2 on this 16-thread machine, ruling Q3), and add an
   `instructions:u` column that is valid at any load. Sizing S.
4. **`perf_compare.py`'s LSP leg compares nothing, and the harness it needs
   isn't on next.** It prints both tables and "compare the two LSP tables row
   by row". `scripts/lsp-latency.py` exists only on the unmerged `editor-45`
   branch, so `seal.sh`'s LSP leg is skipped until that merges. Fix: compare
   each row's `diagnostics_cpu_ms` median against ×1.10 from the JSON, once
   editor-45 merges. Sizing XS.
5. **`malloc` + `free` are 21.7% of kolt's check instructions** (callgrind of
   v0.42.1). editor-45 found 21% in an LSP keystroke. An allocator probe,
   mimalloc or jemalloc as a global allocator behind a feature, measured with
   `instructions:u` and CPU on kolt, sizes it. Sizing S to measure.

## 9. Open questions, each with a recommendation

- **Q1. The gated metric.** **Rec:** compiler counters and shape pins in
  nextest; `instructions:u` (callgrind Ir without a PMU) per corpus program on
  release builds in CI and at the seal; CPU time only on the reference machine
  at the seal and the cut; never wall (§2, §3).
- **Q2. "Strict time to completion."** **Rec:** literal CPU limits on the
  quiet reference machine at the seal and the cut. Everywhere else an
  instruction budget converted at the seal's measured rate (about 11 G
  instructions per CPU-second on kolt) stands in for it (§2.4, §2.5).
- **Q3. The quiet-machine guard.** **Rec:** the seal refuses a CPU verdict
  when the 1-minute loadavg is above 2, and reports instruction counts
  regardless (find 3).
- **Q4. Where each tier refuses.** **Rec:** T1 in every gate; T2 as a
  required CI job `perf` and at the seal; T3 at the seal. `cut-release.sh`
  refuses a tag without a green seal verdict at that sha, with
  `--allow-perf-regression "<reason>"` written into the release notes (§3).
- **Q5. Budgets.** **Rec:** ceilings in `perf/budgets.toml`, set by the seal
  (measured × 1.01), compared cumulatively, never per commit. Ceilings drop
  automatically at the seal after a >2% improvement (§4).
- **Q6. Bumps.** **Rec:** a `[[bump]]` row in the same commit as the cost,
  with a reason and an item. The seal lists them, and the owner approves any
  bump over 3% or on kolt's T3 rows (§4).
- **Q7. Tolerance.** **Rec:** 1% on instructions until S2 measures the spread
  between CI runners (0.5% if under 0.2%; A/B against the release binary in
  one job if it is several percent); ×1.10 on CPU and RSS at T3 (§4).
- **Q8. The corpus.** **Rec:** the examples plus a seeded generator shaped
  like kolt in CI. The generator is calibrated against kolt's phase split at
  each seal. The website and kolt at pinned commits run at the seal only, and
  kolt never enters the repo (§5).
- **Q9. E121 as budgets.** **Rec:** enforced on kolt at the seal on the
  reference machine. Each row reports red until it has been green on two
  consecutive seals, then blocks. In CI the generated app's diagnostics path
  carries an instruction ceiling of about 5–5.5 G (§6.1).
- **Q10. E121's CPU clock once analysis is parallel.** **Rec:** keep the CPU
  budget as the gate, and add a wall target on the quiet reference machine
  when parallel analysis lands. Revisit the ruling then, since parallelism
  can't turn a CPU budget green (§7.3).
- **Q11. A `vilan check` budget per 1,000 lines.** **Rec:** gate the shape
  now (a two-size pin, ≤ ×2.3 per doubling, `#[ignore]`d until find 1 is
  fixed). Report the target of ≤ 30 ms CPU per 1,000 lines marginal plus
  ≤ 150 ms of std reach per browser entry, on the reference machine (§6.2).
- **Q12. The order of the optimization work.** **Rec:** M103, M104, find 1,
  M101, the allocator probe, M100, an on-disk world cache, then parallel
  analysis within an entry under its own paper (§7.2).

## 10. Slices

| slice | content | size | what exists |
|---|---|---|---|
| S1 | `perf_compare.py`: per-child `wait4` RSS (find 2); the load guard (find 3); an `instructions:u` column via a small `perf_event_open` helper (`instr_count.c` here); the LSP rows compared automatically (find 4); `perf-<sha>.json` written for the cut | S | `perf_compare.py`, `seal.sh`'s perf leg |
| S2 | A one-off CI probe: does `ubuntu-latest` expose `instructions:u`? What is the spread between runners for one binary over the examples (ten runs over different jobs)? It decides absolute ceilings vs A/B, and the tolerance | S | `instr_count.c` |
| S3 | `scripts/perf-gate.py` + `perf/budgets.toml` (v0.42.1's counts as the first ceilings) + a required CI job `perf` (release build cached, the examples, the callgrind fallback) + the seal's ceiling ratchet | M | the examples; the release workflow's build cache |
| S4 | The kolt-shaped generator (from E126's exhibit generator in `keystroke.rs`), seeded; its phase-split calibration against kolt at the seal | M | E126's exhibit generator; `VILAN_PHASE_TIMING=passes` |
| S5 | Compiler counters: a `VILAN_COUNTERS=1` line (analyses run, type slots minted, impl selections computed, expressions walked, bytes allocated through a counting allocator) and T1 pins: the two-size package-growth pin (find 1), analyses per LSP edit (M104) | S–M | `impl_select::applying_computed`, `type_id_to_type_map` sizes, `const-fuel-max` |
| S6 | `cut-release.sh` refuses without a green `perf-<sha>.json` at the commit to be tagged; `--allow-perf-regression "<reason>"` | S | the L17 refusal and its override, the pattern to copy |
| S7 | A nightly `perf.yml`: `perf_baseline_full_run`, the four E121/E126 gates in release, a profiling-build callgrind top 25 on the generated app, the macOS-14 row; `perf/report-vX.Y.Z.md` written at the cut | M | `perf_baseline.rs`, `keystroke.rs` gates, `ignored-pins.yml`'s pattern |
| S8 | E121 rows promoted to blocking per Q9 | XS each | the seal's E236 rows |

S1 and S5's growth pin go first. S1 makes the seal's existing verdict
truthful, and the growth pin pins find 1. S2 must run before S3 sets any
tolerance. Sizing for M105 as filed is M for the paper and M for the build.
Measured here, it is S1+S2+S5+S6 (S each, about one lane) plus S3+S4+S7
(M each, a second lane).
