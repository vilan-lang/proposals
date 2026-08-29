# Vilan tracker — open items

`backlog <ID>` resolves to `items/<ID>.md` if open, or a tombstone in `archive.md` (or the frozen chain it points at) if closed — see `proposal/tracker-migration.md` §2.

## A. Reactive core & UI (`std::reactive`, `std::ui`)

| ID | Title | Kind | Discussion |
|----|-------|------|------------|
| [A7](items/A7.md) | SSR tail | design | |
| [A8](items/A8.md) | UI styling — the tail | design | |
| [A14](items/A14.md) | Reactive residuals | design | |
| [A27](items/A27.md) | NEW — `std::dom` cannot listen on `window` at all | design | |
| [A28](items/A28.md) | `map`/`combine`/`flatten` derivations undetachable — a live std leak | bug | FIX-NOW; lifetimes.md S1 |
| [A29](items/A29.md) | `DuplexEnd.me` never cleared — a session retained per disconnect | bug | lifetimes.md S1 |

## B. Type system & the type solver

| ID | Title | Kind | Discussion |
|----|-------|------|------------|
| [B3](items/B3.md) | Variadic-generics tail | feature | |
| [B11](items/B11.md) | `!` / `?.` tail | design | |
| [B146](items/B146.md) | NEW — the context coverage check's refinement consumes node-owned dispatch sites only | feature | |
| [B147](items/B147.md) | NEW — a module/file-level default for `[platform(...)]` | design | |
| [B148](items/B148.md) | NEW — `str + <any struct>` type-checks and renders the runtime tuple | bug | |
| [B149](items/B149.md) | NEW — an async function returning a `Task` mistypes as the task, pinned but never itemed | bug | |
| [B150](items/B150.md) | `drop(x)` is not exception-safe | bug | lifetimes.md §6/S3 |
| [B151](items/B151.md) | mR2 overwrite double-drops when the RHS throws | bug | FIX-NOW — double close today |
| [B152](items/B152.md) | bare `ret <expr>` emits `return return` | bug | |
| [B153](items/B153.md) | `Option::replace` declares a loan and keeps the value | bug | FIX-NOW shaped; unlocks C11's predicate widening |

## C. Memory model

| ID | Title | Kind | Discussion |
|----|-------|------|------------|
| [C1](items/C1.md) | `Weak<T>` | design | |
| [C2](items/C2.md) | Dynamic rule-4 remainder | design | |
| [C12](items/C12.md) | view-capture ban documented but unenforced | bug | lifetimes.md §2.2/S5 |
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
| [E98](items/E98.md) | NEW — a browser build constructing a `@process` resource draws the coloring diagnostic twice | bug | |
| [E99](items/E99.md) | NEW — the `-d` dump's `.parse.out` is the post-desugar tree, and no dump shows the raw parse | process | |
| [E100](items/E100.md) | module-load parse errors carry no span | bug | 798-errors-at-line-1, measured |
| [E101](items/E101.md) | `str::index_of`/`find` + three cause-less diagnostics | feature | one small lane |

## G. Macros & const

| ID | Title | Kind | Discussion |
|----|-------|------|------------|
| [G2](items/G2.md) | Const-eval tail | feature | |
| [G9](items/G9.md) | NEW — a workspace member's own `[build] run` never runs, and nothing says so | design | |
| [G10](items/G10.md) | hook `inputs` declared to the stamp, not the watcher | bug | the lucide run's biggest find |
| [G11](items/G11.md) | `vilan build --explain` — every output names its contributors | feature | owner-filed 2026-08-29; tier-agnostic |

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
| [M11](items/M11.md) | NEW — the compiler's largest retentions are invisible to the leak tally | perf | |
| [M12](items/M12.md) | NEW — the corpus leak-soak passes in 0.005 s asserting nothing when its corpora are absent | perf | |
| [M13](items/M13.md) | NEW — the perf baseline is stale, and its rows carry no provenance to re-record it against | process | |

## N. Hygiene & rot — NEW SECTION

| ID | Title | Kind | Discussion |
|----|-------|------|------------|
| [N16](items/N16.md) | NEW — the recurring codebase audit | process | |
| [N20](items/N20.md) | NEW — `.claude/` is live configuration that no gate can see, and it had three dead pointers in it | process | |
| [N21](items/N21.md) | `cargo fmt` is gated; the clippy and cargo-audit legs remain | process | |
| [N23](items/N23.md) | NEW — 37 `pub` items in `vilan-core` are never referenced outside their own file | process | |
| [N27](items/N27.md) | NEW — nothing ever runs the `#[ignore]`d pins, so an expired pin reason is undetectable by machine | process | |
| [N28](items/N28.md) | NEW — `book_sync`'s mdBook backstop runs whatever `mdbook` is on PATH, no version check | process | |
