# Vilan tracker — open items

`backlog <ID>` resolves to `items/<ID>.md` if open, or a tombstone in `archive.md` (or the frozen chain it points at) if closed — see `proposal/tracker-migration.md` §2.

## A. Reactive core & UI (`std::reactive`, `std::ui`)

| ID | Title | Kind | Discussion |
|----|-------|------|------------|
| [A7](items/A7.md) | SSR tail | design | |
| [A8](items/A8.md) | UI styling — the tail | design | |
| [A14](items/A14.md) | Reactive residuals | design | |
| [A32](items/A32.md) | NEW — custom signals with compatibility: `Source` is the trait, the question is reach | design | owner-proposed; trait already shipped |
| [A34](items/A34.md) | NEW — a typed style token has no mid-value spelling in a css block | design | b148's census find; real gap revealed |
| [A35](items/A35.md) | NEW — the element desugar's `view` is capturable; the shadowed case has no diagnostic | design | lucide lane's find |

## B. Type system & the type solver

| ID | Title | Kind | Discussion |
|----|-------|------|------------|
| [B3](items/B3.md) | Variadic-generics tail | feature | |
| [B11](items/B11.md) | `!` / `?.` tail | design | |
| [B146](items/B146.md) | NEW — the context coverage check's refinement consumes node-owned dispatch sites only | feature | |
| [B147](items/B147.md) | NEW — a module/file-level default for `[platform(...)]` | design | |
| [B149](items/B149.md) | NEW — an async function returning a `Task` mistypes as the task | bug | the pin names it since Order 21; the gap itself stays open |
| [B156](items/B156.md) | NEW — a manifest-configurable prelude: std ambient names by default, overridable | design | RULED 2026-08-29: write the paper |
| [B157](items/B157.md) | NEW — static-or-dynamic component values: the trait-bound pattern vs a `union` former | design | owner-proposed; both problems probe-solved, blanket impl the one gap |
| [B161](items/B161.md) | NEW — a trait annotation as a checked constraint on bindings | design | owner-proposed with exact semantics; A32's companion |
| [B162](items/B162.md) | NEW — trait-associated functions: `Signal::new` with a default body | design | RULED 2026-08-29; A32's companion |
| [B165](items/B165.md) | NEW — `type` binders do not resolve inside an impl head's bounds | bug | blocks B157's generic blanket; Order 23 |
| [B168](items/B168.md) | NEW — a bound's bare generic argument loses its constraints in a generic body | bug | a33's find; pin ignored, three signatures wait |
| [B169](items/B169.md) | NEW — an unbounded generic right operand still escapes `+`'s typing | bug | b148's residual; pin ignored |
| [B170](items/B170.md) | NEW — binary operators skip the check for non-nominal LEFT operands | bug | audit 6 F3; b148's other half |
| [B171](items/B171.md) | NEW — the spec's `is`-binding scope sentence is false; the true scope wants a ruling | design | b166's find |
| [B172](items/B172.md) | NEW — a module-qualified type path is a parse error in every type position | bug | templates lane; the web prelude makes it load-bearing |
| [B173](items/B173.md) | NEW — a blanket impl never satisfies a bound for a generic value | design | b168's find; ruling wanted, pin waits |

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
| [E107](items/E107.md) | NEW — no completion at a builder chain's dot on its own line | bug | owner report; the completion-context class |
| [E108](items/E108.md) | NEW — a type-position unresolved name in a dependency attributes to std's lib.vl | bug | prelude lane's find |
| [E109](items/E109.md) | NEW — the `pub` rule's cascade; `public` refused as `pub` | bug | audit 6 F10+F21 |
| [E110](items/E110.md) | NEW — the web-set steer's claimed LSP suppression does not exist | bug | audit 6 F22 |
| [E111](items/E111.md) | NEW — semantic tokens and inlay hints drift after a `Some(let …)` pattern | bug | owner report; tuple payload, B167's territory in the span subsystem |

## G. Macros & const

| ID | Title | Kind | Discussion |
|----|-------|------|------------|
| [G2](items/G2.md) | Const-eval tail | feature | |
| [G9](items/G9.md) | NEW — a workspace member's own `[build] run` never runs, and nothing says so | design | |
| [G12](items/G12.md) | NEW — `read_dir_all` fuel charged on the result, not the walk | design | audit 4; the basis is the question |
| [G17](items/G17.md) | NEW — a `generated` root through a symlink fails open | bug | audit 6 F5 |
| [G18](items/G18.md) | NEW — fmt/watch follow dir symlinks unguarded: hang + escape | bug | audit 6 F6 |
| [G19](items/G19.md) | NEW — the const channel's lexical fence vs symlink escape | design | audit 6 F7; OWNER QUESTION |
| [G20](items/G20.md) | NEW — file-mode `check` ignores the manifest | bug | audit 6 F11 |
| [G21](items/G21.md) | NEW — the watcher gives const directories the hook reading | bug | audit 6 F23; safe |

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
| [M15](items/M15.md) | NEW — the const-pass scaling gate is wall-clock and reds under lane load | perf | bit a lane verdict; pick (a) or (b) |
| [M16](items/M16.md) | NEW — T-independent generic bodies emit per-monomorphization copies | perf | audit 6 F18 |

## N. Hygiene & rot — NEW SECTION

| ID | Title | Kind | Discussion |
|----|-------|------|------------|
| [N16](items/N16.md) | NEW — the recurring codebase audit | process | |
| [N20](items/N20.md) | NEW — `.claude/` is live configuration that no gate can see, and it had three dead pointers in it | process | |
| [N21](items/N21.md) | `cargo fmt` is gated; the clippy and cargo-audit legs remain | process | |
| [N23](items/N23.md) | NEW — 37 `pub` items in `vilan-core` are never referenced outside their own file | process | |
| [N27](items/N27.md) | NEW — nothing ever runs the `#[ignore]`d pins, so an expired pin reason is undetectable by machine | process | |
| [N28](items/N28.md) | NEW — `book_sync`'s mdBook backstop runs whatever `mdbook` is on PATH, no version check | process | |
| [N34](items/N34.md) | NEW — the normative EBNF has no gate | process | smalls' N32 finding |
| [N35](items/N35.md) | NEW — `hmr_css_matrix` reads the bundle while the watcher writes it | bug | load-dependent race, seen once |
| [N36](items/N36.md) | NEW — the diagnostics ledger is three orders stale | process | audit 6 F8+F9+F20 |
| [N37](items/N37.md) | NEW — the errors appendix is ungated, flagship messages missing | process | audit 6 F12 |
