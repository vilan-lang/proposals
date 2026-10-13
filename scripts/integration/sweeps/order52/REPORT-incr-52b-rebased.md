## incr-52b, rebased onto next

The branch is rebased onto `origin/next` @`dcfdcba1`. New tip **`03673792`** (was `0570d9b7`). Every gate is green again. Nothing pushed; none of my processes are running; `incr-52b-STATUS.md` is untracked and current.

### The rebase
- **Only `CHANGELOG.md` conflicted**, on B624's entry. I kept both sides, mine above upstream's. The other five commits applied with no conflict.
- **Your expected meeting points all merged cleanly:**
  - `analyze_inner`, `impl_subject_admits` (the closure fix stays), `base_cache_admit` / `evict_to_budget`, and `context.rs` all merged without trouble.
  - vilan-lsp's `main()` has N176's `memory::limit_arenas()` followed by my `set_std_prefix_layering_default(true)`.
- **Marker parity:** 45 heads and 45 markers (next has 40, plus my 5 entries).
- **One addition after the rebase, folded into the B618 commit:** two `[[bump]]` rows in `perf/budgets.toml` for `example:todo` (classes `ci` and `reference`, ratio 1.01, item B618), plus one CHANGELOG clause.
  - Why: todo spawns without importing `std::task`, so it now loads `task.vl`. That is ×1.0077 against next (4,209.9M → 4,242.3M), the cost B618 already documents.
  - Before the rebase this was hidden, because the old base was 0.8% heavier on todo.
  - The `ci` rows hold to 0.5% tolerance, so I added the rows as a precaution. Drop them if CI's count shows they aren't needed.

### Commits on `03673792` (oldest first)
| sha | Item | Family |
|---|---|---|
| `28c2651b` | B624 | fix |
| `50dc6984` | std-prefix P2 | performance |
| `cc3ddb02` | Closure is no receiver of a `Callable` struct's impl (your B631) | miscompile |
| `8fd66ae4` | M145 | performance |
| `006391fa` | B618 (with the todo bump rows) | fix |
| `03673792` | P2 follow-up: no layering for std-only worlds or a file open on its own | performance |

### Gates on `03673792`
The suite, native differential, canary and lint were run on the rebased tree before the bump-row fixup. That fixup changed only `perf/budgets.toml` and `CHANGELOG.md`, and the T2 gate was re-run after it.

- **Full suite** (ci-test profile, `not binary(deep_nesting)`, `-j 6`): 10,617/10,617 passed, 38 skipped. Within it:
  - ci_ignored_pins 12, hygiene 3, corpus 14
  - check_scope_differential 16, permutation_differential 7, edit_replay_differential 27, id_windows 10
  - native_differential 279, vilan-lsp 1,128
- **Native differential, sweep mode:** 279/279 (1 skipped).
- **Deep-nesting canary at 1536 KiB:** 18/18.
- **Lint and format:** clippy `-D warnings`, `cargo fmt --check` and `vilan fmt --check .` are clean.
- **`ci-local.sh perf`:** T2 green, and green again after the bump rows. Against next @`dcfdcba1` on the same box:
  - Every row is between −0.07% and +0.03%, except `example:todo` at +0.77% (B618, covered by the bump rows).
- **Late writes:** 0 on kolt.
- **RSS on kolt** (9-run medians): next 276,412 and 276,388 KB; tip 276,124 and 276,652 KB. That is −0.1% and +0.1%.

### Seven lsp-latency rows (the seal's reference)
Kolt @dee494ab, lucide carried, `--runs 5`, quiet box (load average 0.6–1.0). Each cell is instructions in G, then CPU ms to diagnostics.

| Row | next @dcfdcba1 | merged tip `03673792` | pre-rebase tip `0570d9b7` |
|---|---|---|---|
| leaf | 3.48 / 510 | 3.47 / 520 | 3.41 / 530 |
| leaf + pause | 8.60 / 1340 | 8.59 / 1350 | 8.46 / 1330 |
| world | 3.86 / 550 | 3.85 / 550 | 3.79 / 560 |
| shared | 1.35 / 220 | 1.35 / 210 | 1.34 / 210 |
| model | 1.31 / 210 | 1.31 / 210 | 1.30 / 210 |
| importers open | 4.69 / 610 | 4.67 / 620 | 4.60 / 630 |
| css | 5.80 / 750 | 5.62 / 750 | 5.86 / 770 |
| parse break | 5.77 / 760 | 5.59 / 750 | 5.84 / 780 |

- **Merged tip against next:** instructions are flat to −0.4% on every row except css (−3.1%) and parse break (−3.1%).
- **Against my pre-rebase tip,** the merged tree is about 2–3% heavier in instructions on the leaf, pause, world and importers rows and about 4% lighter on css and parse break. The base moved by those amounts too, so these shifts come from the merged lanes, not from my commits.
- **E292 stays open:** leaf is 520 ms CPU and css and parse break are 750 ms, against the 500 ms target.

The list, the finds (B?1 = your B631, B?2, M?1, Q?1, N?1) and the four owner questions are unchanged from my previous hand-back. Still not built: M146 (dependencies), M137, M138, M133's incr half.
