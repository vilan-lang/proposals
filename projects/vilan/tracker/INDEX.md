# Vilan tracker — open items

`backlog <ID>` resolves to `items/<ID>.md` if open, or a tombstone in `archive.md` (or the frozen chain it points at) if closed — see `proposal/tracker-migration.md` §2.

## A. Reactive core & UI (`std::reactive`, `std::ui`)

| ID | Title | Kind | Discussion |
|----|-------|------|------------|
| [A7](items/A7.md) | SSR tail | design | |
| [A8](items/A8.md) | UI styling — the tail | design | |
| [A14](items/A14.md) | Reactive residuals | design | |
| [A34](items/A34.md) | NEW — a typed style token has no mid-value spelling in a css block | design | b148's census find; real gap revealed |
| [A36](items/A36.md) | NEW — `Style::when(condition, delta)` conditional-merge combinator | feature | RULED ACCEPTED 2026-08-31 (style-variants Q3); ready to queue |
| [A37](items/A37.md) | NEW — `[gone]` trait-member attribute: reachable only through the trait (method surface, for blanket impls) | design discussion | NOT queued; the owner unsure of its value |

## B. Type system & the type solver

| ID | Title | Kind | Discussion |
|----|-------|------|------------|
| [B3](items/B3.md) | Variadic-generics tail | feature | |
| [B11](items/B11.md) | `!` / `?.` tail | design | |
| [B146](items/B146.md) | NEW — the context coverage check's refinement consumes node-owned dispatch sites only | feature | |
| [B147](items/B147.md) | NEW — a module/file-level default for `[platform(...)]` | design | |
| [B149](items/B149.md) | NEW — an async function returning a `Task` mistypes as the task | bug | the pin names it since Order 21; the gap itself stays open |
| [B183](items/B183.md) | NEW — tuple comprehension `(item in tuple => EXP)` + the zip form | design | owner-proposed |
| [B184](items/B184.md) | NEW — trait annotations on struct fields, one-instantiation rule | design | owner-proposed; discussion REQUIRED |
| [B213](items/B213.md) | NEW — `vilan fmt` walks once per root; overlapping roots double-report a file | bug | watch-26's find |
| [B216](items/B216.md) | NEW — a parameterized supertrait clause loses `Self` in a default body (B205's gate) | bug | cascade-26's find |
| [B217](items/B217.md) | NEW — generated-code type misses via the `prepped_*` route are not anchored at the derive | bug | cascade-26's find |
| [B218](items/B218.md) | NEW — two implicit generics of one trait print the same name: `Expected X, but got X` (Q3's diagnostic face) | bug | b211-b212's find |
| [B219](items/B219.md) | NEW — `compare_type_rigid` does not consult `rigid_binder_scope`; the documented twins disagree | bug | b211-b212's find |
| [B220](items/B220.md) | NEW — an array receiver has B210's emission-side hole (`resolve_member_on_type` excludes arrays) | bug | b209-b210's find; a decision |
| [B221](items/B221.md) | NEW — a diverging non-last statement does not exempt the return tail (B124's list) | bug | b204's find; pre-existing |
| [B222](items/B222.md) | NEW — a panicking guard does not bind the continuation: B187 decides during the walk, B204's leaves settle after | bug | found at integration; pin ignored naming it |
| [B223](items/B223.md) | NEW — `for` conditions and `match` guards have no polarity frame; a negated capture binds where an `if` refuses | bug | b214-b215's find; refuses programs that compile today |

## C. Memory model

| ID | Title | Kind | Discussion |
|----|-------|------|------------|
| [C1](items/C1.md) | `Weak<T>` | design | |
| [C2](items/C2.md) | Dynamic rule-4 remainder | design | |
| [C13](items/C13.md) | a closure over a view parameter escapes through a storing callee | bug | pinned ignored; spec §6.9's honesty limit |

## D. Documentation

| ID | Title | Kind | Discussion |
|----|-------|------|------------|
| [D5](items/D5.md) | Public traction plan | design | |

## E. LSP & tooling

| ID | Title | Kind | Discussion |
|----|-------|------|------------|
| [E37](items/E37.md) | bindgen v2 — the remainder | feature | |
| [E62](items/E62.md) | NEW — Zed language extension | feature | |
| [E69](items/E69.md) | NEW — attribute-NAME completion in an element head is a semantics decision | feature | |
| [E99](items/E99.md) | NEW — the `-d` dump's `.parse.out` is the post-desugar tree, and no dump shows the raw parse | process | |
| [E106](items/E106.md) | NEW — the language server slows down over a session | bug | owner report; measure first |
| [E121](items/E121.md) | NEW — the editor-latency mandate: <10 ms keystroke path, <500 ms errors | design | owner-set target; ARC, paper first |
| [E124](items/E124.md) | RULED 2026-09-03 — no visibility markers: a `[package]`'s top-level dead code = unreached by ANY entry (the pruner's definition unioned across entries); libraries no top-level gray; `[doc(hidden)]` the soft surface; `[keep]` reserved | editor | PAPER first, then build — an upcoming order |
| [E126](items/E126.md) | NEW — the diagnostics gate's exhibit misses kolt's cost 178× on call substitutions; needs a view-shaped generator | editor | m19-paper's find; M19-t1 gate prerequisite |
| [E127](items/E127.md) | NEW — no `did_change_watched_files` handler; disk-read module listings stale until re-analysis | editor | m25-e125's find |
| [E128](items/E128.md) | NEW — hover renders `= Self` as the trait's name | editor | cascade-26's find; B206's other half |

## G. Macros & const

| ID | Title | Kind | Discussion |
|----|-------|------|------------|
| [G2](items/G2.md) | Const-eval tail | feature | |
| [G9](items/G9.md) | NEW — a workspace member's own `[build] run` never runs, and nothing says so | design | |
| [G12](items/G12.md) | NEW — `read_dir_all` fuel charged on the result, not the walk | design | audit 4; the basis is the question |

## I. Collections

| ID | Title | Kind | Discussion |
|----|-------|------|------------|
| [I2](items/I2.md) | Fixed-arrays tail | design | |
| [I3](items/I3.md) | Iterator adapters — the remainder | feature | |

## J. Concurrency

| ID | Title | Kind | Discussion |
|----|-------|------|------------|
| [J4](items/J4.md) | Free-spawn lint | design | |
| [J5](items/J5.md) | Async recorded opens — the deferred pair | feature | |

## K. Web presence (site, playground, docs delivery) — NEW SECTION

| ID | Title | Kind | Discussion |
|----|-------|------|------------|
| [K5](items/K5.md) | The design language — adopt | feature | |
| [K8](items/K8.md) | Website features & small visual upgrades | feature | |
| [K13](items/K13.md) | NEW — the docs on the vilan framework, the port proper — behind its markdown prerequisite | feature | |
| [K14](items/K14.md) | NEW — the playground's buffers carry no prelude; examples teach the old spelling | design | v0.40.0 deploy's find; OWNER QUESTION |

## L. Release engineering & beta — NEW SECTION

| ID | Title | Kind | Discussion |
|----|-------|------|------------|
| [L3](items/L3.md) | std tier sweep | design | |
| [L8](items/L8.md) | Contribution scaffolding | design | |
| [L15](items/L15.md) | NEW — release artifacts are checksummed but unsigned | feature | |
| [L16](items/L16.md) | NEW — `std::markdown`'s ~20 strict-parse refusals enter the diagnostics ledger | process | |
| [L18](items/L18.md) | NEW — the pages repo is the one repo in the fleet with unpinned workflow actions | process | |

## M. Performance & footprint — NEW SECTION

| ID | Title | Kind | Discussion |
|----|-------|------|------------|
| [M10](items/M10.md) | NEW — mechanize the BASE_CACHE transmute's completeness claim | perf | |
| [M12](items/M12.md) | NEW — the corpus leak-soak passes in 0.005 s asserting nothing when its corpora are absent | perf | |
| [M17](items/M17.md) | NEW — cross-subject body sharing, M16's residual | perf | separate decision |
| [M18](items/M18.md) | NEW — a function attribute marking a bundle boundary | design | owner-proposed; lucide the exhibit |
| [M19](items/M19.md) | NEW — an unchanged package module is re-analyzed every LSP analysis / HMR round | perf | E106's prime hypothesis; lucide's 636 KB |
| [M27](items/M27.md) | NEW — `lsp-index` editor tables 110–584 ms per keystroke, outside analyze and every tranche | performance | m19-paper's find |
| [M28](items/M28.md) | NEW — `plan_resource_drops` 350–600 ms, whole-program switch on any resource type | performance | m19-paper's find; Q4 |
| [M29](items/M29.md) | NEW — completion tranche 3: whole-buffer tokenize/parse per request; member completion 2.63 ms | performance | m25-e125's finds |

## N. Hygiene & rot — NEW SECTION

| ID | Title | Kind | Discussion |
|----|-------|------|------------|
| [N16](items/N16.md) | NEW — the recurring codebase audit | process | |
| [N20](items/N20.md) | NEW — `.claude/` is live configuration that no gate can see, and it had three dead pointers in it | process | |
| [N23](items/N23.md) | NEW — 37 `pub` items in `vilan-core` are never referenced outside their own file | process | |
| [N35](items/N35.md) | NEW — `hmr_css_matrix` reads the bundle while the watcher writes it | bug | load-dependent race, seen once |
| [N47](items/N47.md) | NEW — an output-asserting docs form (`vilan,run` + transcript) | process | docs-law's proposal |
| [N51](items/N51.md) | NEW — `watch.vl` never terminates; the corpus's rule for non-terminating programs | hygiene | hygiene-26's find; OWNER'S QUESTION |
| [N52](items/N52.md) | NEW — `infer_differential.rs` has the pre-N49 single-test shape; split it, share the list | hygiene | hygiene-26's find |
