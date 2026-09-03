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
| [B187](items/B187.md) | NEW — a negated `is` whose then-branch diverges binds the continuation | design | owner question off B171 |
| [B191](items/B191.md) | NEW — a let-bound self-call in a recursive tail cannot resolve (B126's orphaned residue) | bug | N27's first catch |
| [B199](items/B199.md) | NEW — an `is` capture through a call argument reads the missing payload | bug | b195's find; off-spine |
| [B201](items/B201.md) | NEW — `[derive]` inside an inline `mod` generates at file top level | bug | cascade-25's find |
| [B202](items/B202.md) | NEW — `[expose]` of a non-Source field leaves the macro's `_` placeholder as a type | bug | cascade-25's find; B189's residual |
| [B203](items/B203.md) | NEW — watch/HMR leg-skip decided before any leg compiles; cross-leg artifact inputs can skip stale | bug | perf-25's find; pre-existing |
| [B204](items/B204.md) | RULED 2026-09-03 — `panic(…)` is `never`, reconciling through erasure; the checker agrees | bug | BUILD; N48's `0 - 1` idiom goes with it |
| [B205](items/B205.md) | NEW — `self.add(self)` in a trait default over a supertrait: supertrait `Self` not specialized to the subtrait | bug | operators-25's find |
| [B206](items/B206.md) | NEW — conformance steer renders `B = Self` as the trait name (`b: PartialEq`) | bug | operators-25's find; pre-existing |
| [B207](items/B207.md) | NEW — LSP containment test canonicalizes an unsaved buffer lexically (B198's shape) | bug | hygiene-25's find |
| [B208](items/B208.md) | NEW — a watch round's second trigger is LOST (round 2 never fires in 300 s) — N46's real mechanism | bug | hygiene-25's find; undiagnosed |
| [B209](items/B209.md) | NEW — `for x in tuple` binds `any`: writes silently discarded, `let s: str = x` accepted (MISCOMPILE) | bug | b183-paper-2's find; lane b209-b210 refuses the loop now; unroll is Q2 |
| [B210](items/B210.md) | NEW — a tuple receiver resolves no methods at any arity (B170's Add reached via the operator path only) | bug | b183-paper-2's find |
| [B211](items/B211.md) | NEW — a body re-binds its own generic parameter: `swap(A, B)` prints A's impl reading a B's field (MISCOMPILE) | bug | b184-paper-2's bycatch; lane b211-b212 same day |
| [B212](items/B212.md) | NEW — duplicate top-level type declarations unrefused (resolve by order); a struct as a bound gets no sort refusal | bug | b184-paper-2's bycatch; lane b211-b212 |
| [B213](items/B213.md) | NEW — `vilan fmt` walks once per root; overlapping roots double-report a file | bug | watch-26's find |
| [B214](items/B214.md) | NEW — `ret` inside `main` emits an illegal top-level `return` (compiles, throws at run — MISCOMPILE) | bug | bindings-26's find; lane b214-b215 |
| [B215](items/B215.md) | NEW — a bare `let b = x is Some(let n)` binds `n` afterwards; the capture never materializes (MISCOMPILE) | bug | bindings-26's find; lane b214-b215 |
| [B216](items/B216.md) | NEW — a parameterized supertrait clause loses `Self` in a default body (B205's gate) | bug | cascade-26's find |
| [B217](items/B217.md) | NEW — generated-code type misses via the `prepped_*` route are not anchored at the derive | bug | cascade-26's find |
| [B218](items/B218.md) | NEW — two implicit generics of one trait print the same name: `Expected X, but got X` (Q3's diagnostic face) | bug | b211-b212's find |
| [B219](items/B219.md) | NEW — `compare_type_rigid` does not consult `rigid_binder_scope`; the documented twins disagree | bug | b211-b212's find |
| [B220](items/B220.md) | NEW — an array receiver has B210's emission-side hole (`resolve_member_on_type` excludes arrays) | bug | b209-b210's find; a decision |

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
| [E125](items/E125.md) | NEW — `semanticTokens/range` answers in analyzed coordinates; `full` answers live through the anchor | editor | e122-fold's find; keystroke-path design call |
| [E126](items/E126.md) | NEW — the diagnostics gate's exhibit misses kolt's cost 178× on call substitutions; needs a view-shaped generator | editor | m19-paper's find; M19-t1 gate prerequisite |
| [E127](items/E127.md) | NEW — no `did_change_watched_files` handler; disk-read module listings stale until re-analysis | editor | m25-e125's find |
| [E128](items/E128.md) | NEW — hover renders `= Self` as the trait's name | editor | cascade-26's find; B206's other half |

## G. Macros & const

| ID | Title | Kind | Discussion |
|----|-------|------|------------|
| [G2](items/G2.md) | Const-eval tail | feature | |
| [G9](items/G9.md) | NEW — a workspace member's own `[build] run` never runs, and nothing says so | design | |
| [G12](items/G12.md) | NEW — `read_dir_all` fuel charged on the result, not the walk | design | audit 4; the basis is the question |
| [G22](items/G22.md) | NEW — a `.vl` file reached under two names collects twice | bug | symlinks' residual |

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
| [M23](items/M23.md) | NEW — M9's overlay rule refuses the base cache for an entry importing an OPEN buffer (client.vl `base` 1.4–2.7 s every keystroke) | performance | perf-25's find; largest item on E121's diagnostics path |
| [M24](items/M24.md) | NEW — BASE_CACHE has no eviction; M21 multiplies retained worlds per package | performance | perf-25's find; M11's standing finding |
| [M25](items/M25.md) | NEW — completion is the keystroke path's whole remaining budget (per-module sweep + per-request read_dir; kolt burst 12 ms) | performance | keystroke-path's find; E121's next tranche |
| [M26](items/M26.md) | NEW — superseded analyses run to completion (dropped at land, never cancelled); did_open registers no pending generation | performance | e122's find; E121's cancellation step |
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
| [N48](items/N48.md) | NEW — std's own dead code: two rpc.vl sites | hygiene | e114-rest's find |
| [N49](items/N49.md) | NEW — `release_differential` is the union's 615 s critical path; split per program | hygiene | hygiene-25's find |
| [N50](items/N50.md) | NEW — three more exemption tables without N42's inverse check | hygiene | hygiene-25's find |
| [N51](items/N51.md) | NEW — `watch.vl` never terminates; the corpus's rule for non-terminating programs | hygiene | hygiene-26's find; OWNER'S QUESTION |
| [N52](items/N52.md) | NEW — `infer_differential.rs` has the pre-N49 single-test shape; split it, share the list | hygiene | hygiene-26's find |
