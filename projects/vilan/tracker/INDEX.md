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

## B. Type system & the type solver

| ID | Title | Kind | Discussion |
|----|-------|------|------------|
| [B3](items/B3.md) | Variadic-generics tail | feature | |
| [B11](items/B11.md) | `!` / `?.` tail | design | |
| [B146](items/B146.md) | NEW — the context coverage check's refinement consumes node-owned dispatch sites only | feature | |
| [B147](items/B147.md) | NEW — a module/file-level default for `[platform(...)]` | design | |
| [B149](items/B149.md) | NEW — an async function returning a `Task` mistypes as the task | bug | the pin names it since Order 21; the gap itself stays open |
| [B174](items/B174.md) | NEW — an unbounded generic LEFT operand of `+` still concatenates | bug | operators' residual; breaking step deferred, pin waits |
| [B183](items/B183.md) | NEW — tuple comprehension `(item in tuple => EXP)` + the zip form | design | owner-proposed |
| [B184](items/B184.md) | NEW — trait annotations on struct fields, one-instantiation rule | design | owner-proposed; discussion REQUIRED |
| [B187](items/B187.md) | NEW — a negated `is` whose then-branch diverges binds the continuation | design | owner question off B171 |
| [B189](items/B189.md) | NEW — three cascade siblings B182's stand-down does not reach | bug | b182's finds |
| [B190](items/B190.md) | NEW — a struct literal through a module-qualified path does not parse | bug | b172's find |
| [B191](items/B191.md) | NEW — a let-bound self-call in a recursive tail cannot resolve (B126's orphaned residue) | bug | N27's first catch |
| [B192](items/B192.md) | NEW — a partial generic-argument list leaves the rest uninferred | bug | b186's find |
| [B193](items/B193.md) | NEW — a trait default's `self + self` miscompiles (host `+` over lowered structs) | bug | operators-tail's find; pin waits |
| [B194](items/B194.md) | NEW — `[derive]` on a generic type generates erased impls | design | b188's STOP; reflection surface + bound ruling STOPPED at the ruling boundary: the ruled default breaks C7's phantom Handle<T>; reachability refinement measured green — OWNER'S WORD |
| [B197](items/B197.md) | NEW — an operator impl with no method compiles and panics naming nothing | bug | audit 7 F12 |
| [B199](items/B199.md) | NEW — an `is` capture through a call argument reads the missing payload | bug | b195's find; off-spine |
| [B200](items/B200.md) | NEW — unary `-` on a non-numeric operand keeps the operand's type (`-true` is `-1` typed bool) | bug | b196's find; pin waits |
| [B201](items/B201.md) | NEW — `[derive]` inside an inline `mod` generates at file top level | bug | cascade-25's find |
| [B202](items/B202.md) | NEW — `[expose]` of a non-Source field leaves the macro's `_` placeholder as a type | bug | cascade-25's find; B189's residual |
| [B203](items/B203.md) | NEW — watch/HMR leg-skip decided before any leg compiles; cross-leg artifact inputs can skip stale | bug | perf-25's find; pre-existing |
| [B204](items/B204.md) | NEW — should `panic(…)` diverge for the checker as it does for paint? | bug | e114-rest's find; language question |
| [B205](items/B205.md) | NEW — `self.add(self)` in a trait default over a supertrait: supertrait `Self` not specialized to the subtrait | bug | operators-25's find |
| [B206](items/B206.md) | NEW — conformance steer renders `B = Self` as the trait name (`b: PartialEq`) | bug | operators-25's find; pre-existing |

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
| [E114](items/E114.md) | NEW — gray out unused imports, declarations, unreachable code | feature | owner-proposed; DiagnosticTag door |
| [E120](items/E120.md) | NEW — every std import steer is silently dead in the playground | bug | playground lane's find |
| [E121](items/E121.md) | NEW — the editor-latency mandate: <10 ms keystroke path, <500 ms errors | design | owner-set target; ARC, paper first |
| [E122](items/E122.md) | NEW — `semantic_tokens_range` computes the full stream then filters | bug | latency paper's find; no design needed |
| [E123](items/E123.md) | NEW — `did_open` analyzes inline, blocking a tokio worker | bug | latency paper's find |
| [E124](items/E124.md) | NEW — gray top-level dead items in a single-entry package? (no visibility marker → top-level is surface) | editor | OWNER'S DECISION; E114's residual |

## G. Macros & const

| ID | Title | Kind | Discussion |
|----|-------|------|------------|
| [G2](items/G2.md) | Const-eval tail | feature | |
| [G9](items/G9.md) | NEW — a workspace member's own `[build] run` never runs, and nothing says so | design | |
| [G12](items/G12.md) | NEW — `read_dir_all` fuel charged on the result, not the walk | design | audit 4; the basis is the question |
| [G22](items/G22.md) | NEW — a `.vl` file reached under two names collects twice | bug | symlinks' residual |
| [B198](items/B198.md) | NEW — Windows: generated-root containment fails open for a not-yet-written product | bug | audit 7 hazard (c); ruling; pin lands red |

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
| [M20](items/M20.md) | NEW — a chunk snapshots dependencies by value; wrong-order evaluation binds `undefined` forever | bug | m18-paper's P3; latent, route-partition-safe |
| [M21](items/M21.md) | NEW — an entry with any `pkg::` import bypasses the BASE_CACHE | perf | editor-perf's find; 250-290 ms/keystroke |
| [M22](items/M22.md) | NEW — a watch round recompiles every leg, not the reached one | perf | editor-perf's HMR measurement |
| [M23](items/M23.md) | NEW — M9's overlay rule refuses the base cache for an entry importing an OPEN buffer (client.vl `base` 1.4–2.7 s every keystroke) | performance | perf-25's find; largest item on E121's diagnostics path |
| [M24](items/M24.md) | NEW — BASE_CACHE has no eviction; M21 multiplies retained worlds per package | performance | perf-25's find; M11's standing finding |
| [M25](items/M25.md) | NEW — completion is the keystroke path's whole remaining budget (per-module sweep + per-request read_dir; kolt burst 12 ms) | performance | keystroke-path's find; E121's next tranche |

## N. Hygiene & rot — NEW SECTION

| ID | Title | Kind | Discussion |
|----|-------|------|------------|
| [N16](items/N16.md) | NEW — the recurring codebase audit | process | |
| [N20](items/N20.md) | NEW — `.claude/` is live configuration that no gate can see, and it had three dead pointers in it | process | |
| [N23](items/N23.md) | NEW — 37 `pub` items in `vilan-core` are never referenced outside their own file | process | |
| [N35](items/N35.md) | NEW — `hmr_css_matrix` reads the bundle while the watcher writes it | bug | load-dependent race, seen once |
| [N42](items/N42.md) | NEW — the gates' exemption lists have no stale-exemption check | process | hygiene's find |
| [N43](items/N43.md) | NEW — the phase-timing line mislabels two buckets | process | editor-perf's find |
| [N44](items/N44.md) | NEW — resources.md states the pre-last-use scope-end law; memory.md needs adjudication | process | audit7-records' find |
| [N45](items/N45.md) | NEW — the ignored-pins backstop is blind to `cfg(windows)` pins | process | audit7-windows' find |
| [N46](items/N46.md) | NEW — the watch pins' talking timeout reds under lane load (strike three) | process | the union's last named flake |
| [N47](items/N47.md) | NEW — an output-asserting docs form (`vilan,run` + transcript) | process | docs-law's proposal |
| [N48](items/N48.md) | NEW — std's own dead code: two rpc.vl sites | hygiene | e114-rest's find |
