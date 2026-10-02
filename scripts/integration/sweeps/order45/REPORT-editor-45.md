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
