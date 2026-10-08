editor-46 follow-ups — the branch tip is **9532930b** (9532930b0ccc5ad659a9970617b3a5d5295f8bce), rebased onto origin/next @7ee822af, not pushed. All three follow-ups are built: the M104 hybrid (7dcf17f2), the canonical hover order (fe5431ac) and the E255 warning (80e1ba1f). M115 is confirmed, but its stop-gap measured as no win, so I did not build it.

**Rebase onto 7ee822af.** Only CHANGELOG conflicted, and I kept both sides. Commit 6ca409d3 puts one `---` rule between every Unreleased entry; that commit touches CHANGELOG only. solver-a's new `ImplSelector` fields need nothing here, because the E251 merge code never constructs an `ImplSelector`. Neither the full LSP suite nor inference showed a B515 warning in this lane's test programs.

## 1. M104 hybrid (7dcf17f2)
- **A file open alone** keeps its own analysis for keystroke diagnostics, as on v0.43.0. It records the entry it belongs to (`Document::lone_world`).
- **A second open document of the same world** (or the entry itself open) switches both to the entry's world, as before.
- **Closing back to one document** re-analyzes the survivor on its own, and the world it stops reading retires.
- The decision is made once, in `analyze_world`, from a single pass over the open documents.
- **The owner's condition holds.** Find References, rename and prepare-rename on a lone file read the entry's world.
  - That world is built on demand (`Backend::reference_world`) and joins the request as one more neighbour of the existing cross-document union.
  - It is kept until an edit stales it (`did_change` drops it) and evicted once no lone document belongs to it.
  - It is never published; the lone file's own analysis owns its diagnostics.
- **Pins:**
  - `m104_a_lone_module_keeps_its_own_cheap_analysis`.
  - `m104_find_references_on_a_lone_module_reaches_files_that_are_not_open`, checked before and after an edit, plus rename. With the entry world removed it returns only `["model.vl"]`, which is the owner's original bug.
  - `m104_the_switch_both_ways_leaves_no_stale_diagnostics`: while served, the module's own group carries no error and the world's does; back to lone, the reverse holds and the world has retired.
  - The earlier world-mode pins now open two documents where they meant world mode.

**Latency, same method as before** (`scripts/lsp-latency.py --kolt ~/code/kolt --commit 984a1dfb --runs 5`, profiling builds). The machine was at load 20–25, so compare instructions.

| edit | v0.43 base | first build (all-entry-world) | hybrid |
|---|---|---|---|
| `model.vl` alone | 2.37 G | 14.26 G | **2.42 G** |
| `shared.vl` alone | 2.82 G | 17.50 G | **2.83 G** |
| leaf `views.vl` alone | 9.27 G | 14.35 G | 9.37 G |
| css file alone | 10.10 G | 14.25 G | 10.15 G |
| `model.vl` + 3 importers, every open file settled | 41.61 G (4 analyses) | 14.70 G (1) | **14.83 G (1)** |
| opening `model.vl` beside its importers | 740 ms | 80 ms | 60 ms |

- **First Find References on a lone `model.vl`:** 9.92 G / 1.74 s of CPU when measured at rest. The base cache is warm by then, because the dead-code clock has already analyzed the entry. Asked straight after an edit, expect about one cold client world, roughly 14 G. The warm request costs about 0 G and 7 ms.
- The harness now has a Find References row (9532930b), measured after the clock's idle window. Without that wait the first run read 22.5 G, because it also counted the clock's own entry analyses.
- Keystroke paths stay under 10 ms: completion runs 2–5 ms (E249's solver lookup), hover 1.5–3 ms.

## 2. Canonical hover order (fe5431ac)
- There is one ordering function, `hover_blocks::HoverBlocks::render`, over typed blocks.
- Every hover kind is assembled from it: function, binding, parameter, `self`, member read, field, type name, type parameter, trait in a bound, alias, pattern, namespace and operator.
- **The order:**
  1. Diagnostic: the `[deprecated]` / `[internal]` lead.
  2. Signature.
  3. **SignatureNote** — the block kind your list does not name, placed right under the signature. It holds E227's `Shown as ~Source<T>` and E240's `A type parameter of fun pick<..>`.
  4. Doc comment.
  5. Preview, under a rule: the struct, enum or trait shape, and a namespace's members.
  6. Platform: the layer a function requires.
- No entry-info block exists in hover today. Entry and world facts live in the status bar menu.
- Diagnostics at the position are not repeated in the server's hover, because VS Code already shows them in its own problems section of the hover. Rank 1 is what the program says about the hovered declaration.
- **Visible change:** a namespace's member list now sits under a rule (the E152 golden is updated).
- **Pins:** `hover_blocks::tests`, `e246_a_function_hover_orders_lead_signature_doc_platform` and `e246_a_binding_hover_orders_signature_note_doc_preview`.

## 3. E255 (80e1ba1f)
- A repeated import leaf now carries a warning with the code `duplicate-import`, for example: `Json` is already imported on line 1 — Organize Imports removes the repeat.
- **What counts as a repeat:** the same path bound under the same name, a name repeated in one group, or a `self` leaf beside the module's own import. An alias does not count. `only`, `use`, re-exports and marked or selector branches are not compared.
- It is syntactic: a new `formatter::duplicate_import_leaves`, placed next to E251's merge in syntax's file.
- It is published only for open buffers.
- **Quick fix:** "Remove the duplicate import (Organize Imports)". It applies the organize action's edit for that run.
- The editor appendix now counts nineteen quick fixes.
- **Pins:** three in `organize_duplicate_tests`.

## M115 (the base-cache finding)
- **Confirmed.** I added a temporary local counter for base-cache hits, stale evictions and stores. In world mode (`views.vl` + `model.vl` open, entry closed), a `model.vl` keystroke gave:
  - hits +0;
  - stale evictions +1;
  - stores +1, a full clone back into the cache.
- **Why it misses:** the stored world contains the module that just changed, so `base_cache_lookup_locked` evicts it and the world is rebuilt and stored again.
- **The hybrid removes the lone-file case:** `model.vl` alone is back to 2.42 G because its own world hits.
- **Stop-gap not built.** It skips the store when the world holds a dirty open buffer (an open file whose text differs from disk). I built it with a counter pin and checked the pin goes red without it, then measured:
  - `model.vl` + importers: 14.83 → 14.81 G, so the clone costs almost nothing.
  - keystroke + pause: 22.00 → 25.96 G, worse. A recurring dirty state (an undo, or the same keystroke again) used to hit the stored world, and the stop-gap throws that hit away.
  - Changes reverted. analyzer.rs is untouched in this branch, and the local counter went with them (perf-46 owns counters).
- **Composition with S1 (hot-set worlds):** I did not build it.
  - The world path: both choose which world to analyse, the server side; S1 only changes how the analyzer builds and stores that world. A world-mode keystroke in a hot-set module would then hit the prefix.
  - The lone path already gets M19's reuse today, because the lone file is its own entry.
  - Find References on a lone file builds the full entry world through the same analyzer, so S1 would make that build cheaper too. The paper's §4.5 whole-entry index stays whole-entry.
  - Nothing in the hybrid would need to change.

## Gates (on 80e1ba1f)
- vilan-lsp + vilan-ide: 1053 of 1054 passed. The one failure, book_sync, was the editor page's quick-fix count; I fixed it and book_sync then passed 15/15.
- vilan-core inference + lib + docs: 6058/6058.
- vilan-cli corpus + vscode_extension (including `npm test`): 39/39.
- Workspace clippy with `-D warnings` and fmt are clean. No golden moved apart from the hover goldens named above. No `.vl` fixture added.
- 9532930b changes only `scripts/lsp-latency.py`.

## For the owner
1. **Where the cost now lands.** The first Find References or rename on a lone file after an edit pays one entry analysis: about 10 G at rest, up to about 14 G right after an edit. Later requests reuse it until the next edit. An idle pre-build is possible by keeping the dead-code clock's entry analysis instead of dropping it; that would cost memory while a lone file is open. I did not build it.
2. **M115's real fix is S1.** The cheap stop-gap is not worth its cost.