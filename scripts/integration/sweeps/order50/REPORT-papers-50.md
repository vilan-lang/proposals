## papers-50: the std-prefix paper is written (no tree change)

**Paper:** `/home/reed/code/vilan-lang/proposals/projects/vilan/proposal/std-prefix.md` (546 lines, uncommitted). It is measured against the installed `vilan 0.47.0 (5fe24f868)` = next @5fe24f86.

**Sections:** §0 the ask and the answer · §1 ground truth (1.1 std's share per pass, 1.2 what an in-memory hit removes, 1.3 the server leg in the LSP, 1.4 what std mints and in what order, 1.5 the base-cache key and why it is process-bound) · §2 blocker census · §3 what S6's windows give · §4 the prefix defined (std-first order, std resolves alone, the key, contents) · §5 serialization form · §6 invalidation rule · §7 the doors, sized · §8 the readers that need a cross-process id · §9 interactions · §10 what could not be measured · §11 finds · §12 Q1–Q12 · §13 slices.

**Supporting files** (proposals repo, uncommitted):
- Probes, tools and raw output: `/home/reed/code/vilan-lang/proposals/scripts/integration/sweeps/order50/papers-50/probes/`
- Repros: `.../papers-50/finds/`
- Finds file: `/home/reed/code/vilan-lang/proposals/scripts/integration/sweeps/order50/newitems50-papers.json` (4 items)

### The answer in three sentences
1. A persisted std prefix can be built without S7 and without saving ASTs. After the walk the analyzer runs on its own IR. Every address-keyed structure §6.15 named is read only by the walk (`analyzer.rs:38806/38837`), so it is dead once std has walked. What actually blocks it is that std's ids depend on the package around them: std modules a package module asks for load after that module (find B603). So the canonical order has to become std-first (emitted declarations reorder once), and std has to resolve alone, with M121's reach record as the guard.
2. The ceiling is the in-memory hit, made cross-process. It removes 53% of std's cost; the other 47% (std's checks tail and post passes, which re-run on every analysis even on a hit) waits for M134/S7.
3. Door (a) is recommended: a file per (platform, std module set) beside the materialized std, keyed by format version, a hash of vilan-core's sources, std's content hash, platform, the std closure and macro limits. Door (b), the fork-server, is declined. Door (c) is mostly the base cache's budget, so fix that first, then pin an in-process std-only prefix.

### The three measurements
Instructions are deterministic counts. CPU shares are medians of 3 runs at loadavg 4–9 (other lanes were building). "Std alone" is a probe that loads the same std module set with no package code; its std entity counts match kolt's exactly.

| pass (CPU ms) | empty web (all std) | kolt client: leg / std | kolt server: leg / std |
|---|---|---|---|
| load+walk | 61 | 237 / 102 (43%) | 149 / 96 (64%) |
| base | 36 | 255 / 73 (29%) | 76 / 72 (95%) |
| build | 3.4 | 20 / 6.4 | 11 / 6.6 |
| checks + tail | 60 | 434 / 119 (27%) | 160 / 116 (73%) |
| post-passes | 15 | 404 / 33 (8%) | 64 / 27 (42%) |
| total CPU | 180 | 1,469 / 341 (23%) | 492 / 325 (66%) |
| instructions | 1.371 G | 11.09 G / 2.36 G (21%) | 3.39 G / 2.22 G (66%) |

- **perf-47 correction:** the empty node program (0.24 G) is std too. Even a program that fails to parse pays it, so the whole floor is std.
- **In-memory hit vs cold:** empty web 1.397 → 0.647 G; kolt client's std 2.40 → 1.13 G; kolt server's std 2.26 → 1.06 G.
- **LSP pause row:** 14.54 G at the default budget vs 10.76 G with `VILAN_BASE_CACHE_BUDGET_MIB=4096` (x0.74; CPU 2,870 → 2,030 ms). The server world misses 4 of 6 pauses at the default and 1 of 6 at the larger budget.

### Blocker census (counts)
- The Analyzer has **415 fields** (229 at §6.15): 243 maps/sets, 264 mention `Id`, 88 `TypeId`, 69 carry `'src`, 4 `&'static str`, 3 keyed by address, 4 `RefCell`, 2 `Arc`. The 18 entity types hold 38 `&'src str` fields and no AST node.
- Std rows in kolt client's std set:
  - Address-keyed macro maps: 37 / 0 / 0, plus 0 anonymous blocks. All dead after the walk, so dropped.
  - Generated-item trees: 37. Dropped.
  - `span_map`: 57,356 `&'src Span` rows. Can hold the `Span` by value.
  - Six check queues holding `&'src Node`, drained after the store. Pre-drained for std.
  - All strings: borrowed from the file buffer via serde.
  - Derived indices and memos: rebuilt or dropped.
- **Id lanes (the one hard row):** 55,693 entity ids / 8,665 scopes / 97,141 type slots / 60 sources. Std's ids fall in at least 9 runs cut by package ids; 5,632 are minted after 81k package ids.
- Resident std world: 20.9 MB (empty web) / 35.5 MB (kolt client's std). Estimated file 3.5–5 / 6–8 MB, load 10–40 ms. Both are estimates, not measured.

### Questions and recommendations
- **Q1** One file per (platform, std module set) — yes.
- **Q2** Std-first canonical order — yes, as P0 right after S6's C2.
- **Q3** Std resolves alone, with the reach record refusing the prefix when a package impl could answer — yes.
- **Q4** Key by the std closure, not the entry's seeds — yes.
- **Q5** Build identity is a vilan-core source hash, not `VILAN_BUILD_SHA` — yes.
- **Q6** Location `~/.vilan/std-cache/<hash>/prefix/`, override `VILAN_WORLD_CACHE`, written on the first miss.
- **Q7** Fork-server — decline.
- **Q8** Budget first, then a pinned prefix; no sharing between the browser and node legs (their std sets differ).
- **Q9** M19's records and S2's tables go in the same file — yes.
- **Q10** No prefix in the playground bundle for now.
- **Q11** Prefix off under hash shuffle and in `clean_analysis` — yes.
- **Q12** Encoding is serde with borrowed strings — yes.

### Slices
| slice | content | size | needs |
|---|---|---|---|
| P0 | std-first order | S | S6 C2 |
| P1 | in-process std-only prefix | M | P0 |
| P2 | LSP budget + pinned prefix | S | P1 (budget alone needs nothing) |
| P3 | serializer, with a loaded-vs-built round-trip differential | M–L | P1 |
| P4 | key + `vilan cache` integration | S | P3 |
| P5 | suite (N157) | S | P4 |
| M135 | const cache on disk | S | nothing |

### Projected savings with door (a)
These are estimates: the hit residue plus a load cost from §5.
- empty web −49%
- kolt server leg −29%
- kolt client leg −9%
- N157: about 1,500–2,300 of the suite's 13,002 CPU-s (12–18%)

### Finds filed (placeholder ids, each with a repro)
- **B603** — the load order depends on who imports a std module. Adding a redundant entry `import std::path;` reorders the emitted module even though the reachable set is unchanged; on kolt's server, `import std::db;` reorders 18 lines.
- **E294** — the pause analyses' worlds evict each other under M67's 192 MiB budget. This is a quarter of the pause row. I did not run the v0.46.0 base binary, so whether it explains the seal's x1.17 is still open.
- **G28** — the macro-expansion table is stamped with the version only, so dev builds of the same version are served the previous build's expansions.
- **M135** — S4's const cache is in memory only. Every cold kolt client check re-evaluates the same 112 const sites (const pass 173–251 ms CPU).

No processes left running. The kolt copies are in my session scratch only; I ran no git anywhere.
