# Vilan tracker — open items

`backlog <ID>` resolves to `items/<ID>.md` if open, or a tombstone in `archive.md` (or the frozen chain it points at) if closed — see `proposal/tracker-migration.md` §2.

## A. Reactive core & UI (`std::reactive`, `std::ui`)

| ID | Title | Kind | Discussion |
|----|-------|------|------------|
| [A7](items/A7.md) | SSR tail | design | |
| [A8](items/A8.md) | UI styling — the tail | design | |
| [A14](items/A14.md) | Reactive residuals | design | |
| [A34](items/A34.md) | NEW — a typed style token has no mid-value spelling in a css block | design | b148's census find; real gap revealed |
| [A35](items/A35.md) | NEW — the element desugar's `view` is capturable; the shadowed case has no diagnostic | design | lucide lane's find |
| [A36](items/A36.md) | NEW — `Style::when(condition, delta)` conditional-merge combinator | feature | RULED ACCEPTED 2026-08-31 (style-variants Q3); ready to queue |

## B. Type system & the type solver

| ID | Title | Kind | Discussion |
|----|-------|------|------------|
| [B3](items/B3.md) | Variadic-generics tail | feature | |
| [B11](items/B11.md) | `!` / `?.` tail | design | |
| [B146](items/B146.md) | NEW — the context coverage check's refinement consumes node-owned dispatch sites only | feature | |
| [B147](items/B147.md) | NEW — a module/file-level default for `[platform(...)]` | design | |
| [B149](items/B149.md) | NEW — an async function returning a `Task` mistypes as the task | bug | the pin names it since Order 21; the gap itself stays open |
| [B171](items/B171.md) | NEW — the spec's `is`-binding scope sentence is false; the true scope wants a ruling | design | b166's find |
| [B172](items/B172.md) | NEW — a module-qualified type path is a parse error in every type position | bug | templates lane; the web prelude makes it load-bearing |
| [B173](items/B173.md) | NEW — a blanket impl never satisfies a bound for a generic value | design | b168's find; ruling wanted, pin waits |
| [B174](items/B174.md) | NEW — an unbounded generic LEFT operand of `+` still concatenates | bug | operators' residual; breaking step deferred, pin waits |
| [B175](items/B175.md) | NEW — `T::default()` under a multi-bound infers as the bound, not `T` | bug | operators' find; blocks closing the Trait skip-hole |
| [B177](items/B177.md) | NEW — an array impl's return check refuses with a self-contradicting message | bug | operators' find |
| [B178](items/B178.md) | NEW — `fun main(p: bool)` compiles and emits broken JS | bug | traits-core's find; refuse-or-emit ruling |
| [B180](items/B180.md) | NEW — a nominal left's declared `B` is never checked at dispatch | bug | b179's find; Order 24 top slot |
| [B181](items/B181.md) | NEW — `&&`/`||` accept a generic operand, emit the value as the bool | bug | b179's find; one-line right half |
| [B182](items/B182.md) | NEW — a refused bare-trait field cascades ~50 errors, roots printed last | bug | kolt migration's lesson |
| [B183](items/B183.md) | NEW — tuple comprehension `(item in tuple => EXP)` + the zip form | design | owner-proposed |
| [B184](items/B184.md) | NEW — trait annotations on struct fields, one-instantiation rule | design | owner-proposed; discussion REQUIRED |
| [B186](items/B186.md) | NEW — `fun f(x: Trait)` as an implicit generic (the §7.3 parameter sugar) | design | owner-ruled WANTED; Order 24 |
| [B187](items/B187.md) | NEW — a negated `is` whose then-branch diverges binds the continuation | design | owner question off B171 |
| [B188](items/B188.md) | NEW — an under-supplied type argument is erased, not refused (`seven1` through an `i32`) | bug | papers' find; LIVE MISCOMPILE + ICE; FIX-NOW |
| [B189](items/B189.md) | NEW — three cascade siblings B182's stand-down does not reach | bug | b182's finds |
| [B190](items/B190.md) | NEW — a struct literal through a module-qualified path does not parse | bug | b172's find |

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
| [E112](items/E112.md) | NEW — `line_indices` caches a closed workspace file forever | bug | editor-health's find |
| [E114](items/E114.md) | NEW — gray out unused imports, declarations, unreachable code | feature | owner-proposed; DiagnosticTag door |
| [E115](items/E115.md) | NEW — an element tag's closing `>` on its own line is not highlighted | bug | owner report |
| [E116](items/E116.md) | NEW — a file's platform color does not update when it becomes reachable | bug | owner report; E113 follow-up |
| [E117](items/E117.md) | NEW — a ghost diagnostic lingers after a comment/uncomment round-trip | bug | owner report; stale-publish ordering |
| [E118](items/E118.md) | NEW — the formatter lays out an inline element closure argument oddly | bug | owner report |
| [E119](items/E119.md) | NEW — a field miss on an overlaid std type should name the overlay and why | bug | owner ruling, A35's companion |
| [E120](items/E120.md) | NEW — every std import steer is silently dead in the playground | bug | playground lane's find |

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
| [M20](items/M20.md) | NEW — a chunk snapshots dependencies by value; wrong-order evaluation binds `undefined` forever | bug | m18-paper's P3; latent, route-partition-safe |

## N. Hygiene & rot — NEW SECTION

| ID | Title | Kind | Discussion |
|----|-------|------|------------|
| [N16](items/N16.md) | NEW — the recurring codebase audit | process | |
| [N20](items/N20.md) | NEW — `.claude/` is live configuration that no gate can see, and it had three dead pointers in it | process | |
| [N23](items/N23.md) | NEW — 37 `pub` items in `vilan-core` are never referenced outside their own file | process | |
| [N27](items/N27.md) | NEW — nothing ever runs the `#[ignore]`d pins, so an expired pin reason is undetectable by machine | process | |
| [N28](items/N28.md) | NEW — `book_sync`'s mdBook backstop runs whatever `mdbook` is on PATH, no version check | process | |
| [N35](items/N35.md) | NEW — `hmr_css_matrix` reads the bundle while the watcher writes it | bug | load-dependent race, seen once |
| [N38](items/N38.md) | NEW — two shipped sentences disagree on the reserved-name set | process | records' find; shared constant |
| [N39](items/N39.md) | NEW — `ISTRING` is used normatively, never declared in §2 | process | records' find |
| [N40](items/N40.md) | NEW — `free_port()`'s bind-release-rebind race, two e2e suites | process | perf's find |
| [N41](items/N41.md) | NEW — the ledger gate's catch-all row + helper blind spot | process | b179's find; day-one customer |
