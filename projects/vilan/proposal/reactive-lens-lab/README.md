# The reactive lens lab

The working code behind `../reactive-lens.md` (tracker A185). Built on vilan 0.54.0, JS backend. Nothing here is std: it is a library and its experiments, kept so every number and claim in the paper can be re-run.

## Run

```bash
vilan test src
```

runs every `src/*_test.vl`. One file: `vilan run src/laws_test.vl`.

The node benchmark (best of five runs per row):

```bash
vilan build src/bench.vl && node run_bench.mjs 5 src/bench.mjs
```

## What is here

| File | What it is |
|---|---|
| `src/lens.vl` | The library: `Change`, the `Handler` trait, the `Positional` (blocked table) and `Keyed` handlers, `Lens`, slots and parts, nesting, the `Resizable` and `Lookup` shape traits, the bridges to std's ops (`items()`, `rows()`), `index_by`, `move_item`, `reconcile_by_key`. |
| `src/laws_test.vl` | The paper's laws on std's turns, parts, moves, the diff door, std's `map`/`filter`/`memo` over a lens, the index by key, the keyed handler. |
| `src/fuzz_test.vl` | 9,000 random writes against a plain model: slot identity and the operators' law checked after each. |
| `src/tracked_test.vl` | Tracked reads (`derive(|| ..)`) over a slot's parts. |
| `src/nested_test.vl` | A lens inside a lens: `list.slot(1).sequence(..)`. |
| `src/keyed_test.vl` | The keyed side (std's map operators, length, the diff door), the planned write and the truth check. |
| `src/wire.vl`, `src/wire_test.vl` | A server lens and a client lens joined by one patch vocabulary: seed, follow, lag, loss, per-key subscription, a one-patch reorder. |
| `src/loaded.vl`, `src/async_test.vl`, `src/async_real_test.vl` | Loading phases, refresh, pagination and optimistic writes over the lens; the second test file runs on real tasks. |
| `src/structures_test.vl`, `src/struct_*.vl` | More structures: rope, gap buffer, sorted index, sets, a flat tree, a 2D grid with a handler of its own. |
| `src/kolt_test.vl` | Six of kolt's situations ported. |
| `src/boiler_*.vl`, `count_lines.py`, `count_names.py` | The boilerplate comparison: a `RopeCell` written the way std writes `ListCell`, and three kolt sites before and after. |
| `src/bench.vl`, `src/bench_derived.vl`, `run_bench.mjs` | The node benchmarks against std's `Store`, plain signals and `ListCell`. |
| `src/bench_memory.vl`, `measure_heap.mjs` | Heap held per watched row: `vilan build src/bench_memory.vl && node --expose-gc measure_heap.mjs src/bench_memory.mjs`. |
| `repro-b712/` | The minimal reproduction of B712 (a non-exported trait impl in a module with an explicit export surface). |
| `browser/` | The lens's entry for the DOM measurements, the same workloads written for kolt's prototype, and the raw measurements. |

The browser measurements (real DOM rows, seven contenders) reuse kolt's own harness (`kolt/planning/proposal/live/web/measure.mjs`) on a scratch copy of `kolt/planning/proposal/live/`, with `src/lens.vl` and `browser/heavy_lens.vl` added to it. The files under `browser/` that import `pkg::live` build only there.
