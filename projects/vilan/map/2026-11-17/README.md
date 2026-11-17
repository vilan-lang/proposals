# Survey notes behind MAP.md (2026-11-17, v0.56.1)

Five read-only surveys, one file each, written by subagents and kept as written. They carry the
evidence for [MAP.md](../../MAP.md): file paths, line numbers and the commands behind each count.
Nothing was built or run for them beyond reading, `grep`, `wc`, `git log` and `gh`.

| File | Scope |
|---|---|
| 01-repos-infra.md | repositories, crates, CI and release, the website, leftovers |
| 02-std.md | the standard library module by module, `std::fs`, the reactive stack and the lens |
| 03-native-gpu-desktop.md | the Rust backend, native build times, the GPU layer and UI, desktop apps |
| 04-compiler-core.md | the pipeline, incremental analysis, performance, tooling, correctness debt |
| 05-papers-tracker.md | all 182 papers classified, tracker statistics, the owner's decision queue |
| 06-lsp-latency-today.md | added later the same day: the language server measured on today's Kolt, one keystroke profiled, the levers ranked (it corrects survey 04 on what the incremental work built) |

## Known corrections (the integrator's, after reading them)

- 04 and 05 say the chronicle has no entries for Orders 56 to 58. Orders 56 and 57 are missing;
  the Order 58 and v0.56.1 entries exist (written 2026-11-16).
- 04's "anomaly" (one Kolt commit reading 46.1 G, then 33.7 G) is not the exhibit copy: the sources
  are byte-identical. The lower figure appears at every seal run across a breaking change, where
  the two sides check different trees (v0.54.0, v0.56.0), and the higher at ordinary seals
  (v0.55.0, v0.56.1). The cause is not found; tracker N208.
- 03 could not reproduce the "330/330" in an Order 57 stamp. Nor can I; treat that figure as
  unexplained.
- 01's Homebrew finding was verified by hand: the formula is at v0.41.1 and the repository has the
  secret `TAP_APP_ID`, not the `TAP_APP_CLIENT_ID` the job reads.
- 03's table of what Kolt's Electron shell uses (C3) is generalised here: Kolt is a private
  repository and this one is public. The unedited notes are on the owner's machine under
  `~/.vilan/gates/map/`.
- Percentages in these files are the surveyors' own; MAP.md states which it adopted and on what
  basis.
- The surveys counted 217 open tracker rows; three were filed after them (L25, N208, N209).
