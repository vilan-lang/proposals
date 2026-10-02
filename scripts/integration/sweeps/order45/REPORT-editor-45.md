# editor-45 REPORT (condensed by the integrator; Opus) — tip b228cd4c on baa57390; ALL TEN items landed

| item | sha | note |
|---|---|---|
| Hover arc E235 + E237 + E238 + E239 | 8ffd9659 | E235: the printer dropped EVERY convention (`own x`, `&T`, `&mut T`, externals'), not only the receiver's `own`; E238: the header prints as the block declares it — `impl Memo<type K: Hashable, type V>` (the ruling's `impl Memo<K: Hashable, V>` is not real syntax); E239: `self: <subject>` under the header; E237: the type's definition one level deep, 12 members then `…`. New `analyzer/hover_labels.rs`. |
| E234 | fba0dc02 | + an optional arity's composite name doubled the escape |
| E241 | ad26bbd8 | `None` → `Option<i32>::None`; `Some(let v)` → `Option<i32>::Some(i32)`; `_` was `void` (wrong) → `_: Option<i32>` |
| E240 | 9fd92a8b | a type parameter hovers as `type I: Read<U>` + "A type parameter of `fun pick<..>`" at the declaration and every use; a trait in a bound hovers as the trait |
| B437 + B436 | 5b464105 | B437 CORRECTED: a real JS MISCOMPILE — the vtable key lacked the trait's arguments (`dyn Shape<str>` over a type that is also `Shape<i32>` dispatched the i32 impl) |
| E236 | 86b70efb, b228cd4c | `scripts/lsp-latency.py --kolt DIR [--commit SHA] [--lsp BIN] [--runs N] [--json out] [--callgrind DIR --scenario ..]` |
| E242 | 6f5942f4 | diagnostics follow edits until the next analysis |

E236 baseline (kolt @984a1dfb; medians of 5; load 5–7; CPU→diagnostics ms, tip / base ba2eebd9): leaf 1120/1150; shared.vl 370/430; model.vl 370/430; css 1230/1310; parse break 1230/1320; repair 1250/1300. Keystroke-path requests ≤ 2.5 ms (E121's <10 ms met); diagnostics over E121's 500 ms except shared/model. VmHWM 565–733 MB. v0.42.0: one smoke run at load ~70 — 7.1 s leaf, 3.0 s shared, 7.1 s css (indicative only). CPU moves ~30% with load on this host: gate only from quiet runs. Tables: sweeps/order45/editor-45/.
Callgrind (css keystroke, 58.0 G Ir): post_analysis_passes 57% (impl_members_for_bound's uncached path 31%; subject_applies 35% incl.; refined_edges 25%); analyze_inner 38%; const-eval 13%; malloc+free 21% self.

Gates on baa57390: nextest 9224/9224 (40 skipped) at 5b464105; after E242 vilan-lsp + vilan-ide 991/991; fmt, clippy, vscode 18/18; no golden moved. No arm added to `walk_expr_node_inner`.
Finds FILED: M101, M102, B502, B503.

## ADDENDUM 2 (2026-10-02) — final rebase onto 4fdf7cc1, tip b6c96444
Gates: nextest 9383/9383 (vilan-lsp 966, vilan-ide 26); fmt, clippy, vilan-fmt leg, vscode 18/18. Hover spot-checks: `Store<User>` shows its block and "Shown as `~Signal<User>`"; `HashMapCell` renders under its new name. Harness (E244): an `instructions:u` column, an analyses column, a `leaf keystroke + pause` row, kolt's `src/search-dict/` copied; `perf_compare.py`'s flags unchanged.
THE TABLE (kolt @984a1dfb, medians of 5, load 1–3; v0.42.1 → tip): leaf 1140 → 1040 ms CPU, 14.16 → 9.27 G instr; leaf + pause 2750 → 2480 ms, 34.37 → 21.89 G (3 analyses); shared.vl 390 → 310, 4.76 → 2.82 G; model.vl 360 → 300, 5.10 → 2.36 G; model.vl with importers open: own diagnostics 430 → 390 ms, ALL SETTLED 5540 → 5540 ms, 58.04 → 41.55 G (4 analyses); css 1190 → 1170, 14.61 → 10.09 G; parse break/repair 1210/1260 → 1140/1180. Worst keystroke-path wall 2.1 → 10.2 ms (hover, importers-open row; E245). VmHWM 803 → 1013 MB (M108).
Finds FILED: E245, B518.
