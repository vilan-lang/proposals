M88 probes (lane papers-43; vilan 0.41.1 (1a33340f2)). Never build in place: copy to a scratch dir.
- doors/d*.vl: each prepends base.vl.in's `trait Src` + `struct Root` (already inlined). Run each with
  `vilan check` then `vilan run` (JS) and `vilan run --backend rust` (native). d5 needs host.mjs as its extern.
  Crashing on JS after a clean check: d1, d1b, d2, d3, d12, d24, d25, d26 (and B430's tuple shape, d4).
- dyn_census.py <prog>.analyze.out --js <emitted.js>: the per-(trait, args) occupant census from a
  `vilan build -d` Program dump, cross-checked against `Object.create({` tables in the emitted JS.
- sweep.sh <scratch>: counts emitted vtables over the corpus, the examples and the benchmarks.
- bench/: bench_dyn{,2}.vl vs bench_direct{,2}.vl (a `dyn Step` field vs the concrete field), built with
  `vilan build`, timed by cpu.js (child CPU time via process.cpuUsage, 5 alternating runs). ifdyn.vl shows
  the emitted pair and dispatch shapes.
