# Vilan tracker — open items

`backlog <ID>` resolves to `items/<ID>.md` if open, or a tombstone in `archive.md` (or the frozen chain it points at) if closed — see `proposal/tracker-migration.md` §2.

## A. Reactive core & UI (`std::reactive`, `std::ui`)

| ID | Title | Kind | Discussion |
|----|-------|------|------------|
| [A7](items/A7.md) | SSR tail | design | |
| [A8](items/A8.md) | UI styling — the tail | design | |
| [A14](items/A14.md) | Reactive residuals | design | |
| [A34](items/A34.md) | NEW — a typed style token has no mid-value spelling in a css block | design | b148's census find; real gap revealed |
| [A37](items/A37.md) | NEW — `[gone]` trait-member attribute: reachable only through the trait (method surface, for blanket impls) | design discussion | NOT queued; the owner unsure of its value |
| [A46](items/A46.md) | NEW — fragment syntax `<>..</>` lowering to a `List<View>` literal (reverses element-syntax.md §7's refusal); NOT a multi-root View | feature | owner's ask (kolt); S–M for the list lowering, L for a marker-node fragment; owner to say which |
| [A50](items/A50.md) | NEW — A49's residuals: `bind_each_by` hands the row render a WRITABLE `SignalCell<T>` (a read-only projection needs a wrapper type — no trait objects); `Selector<T>` is a handle with `.of(key)` where Solid returns a function (a closure spelling needs a context-carrying closure type; `sync`/`context` are parameter-only) | design | std-27/std-28's open questions; OWNER |
| [A51](items/A51.md) | NEW — A39's residue: the `List<T>` keyed exposure has NO macro form (`[expose(keyed)]` reads two written types; vilan has no associated types), refused with a steer to `Map<K, V>` or the hand-wired `expose_keyed`; `keyed_diff` is O(N) CPU per change per connection (bytes are O(change)) | design | rpc-28's residue; OWNER Q on the spelling |
| [A52](items/A52.md) | NEW — rpc smalls: `[expose]`/`[service]` cannot take a GENERIC source field in either spelling (the generated `session.expose(self.tasks)` cannot infer `T` through the supertrait; `[service]` rejects a generic subject); `RemoteSource<T>` has inherent `sub`/`map`/`or` but no `impl … with Source<T>` (a mirror is not a Source); `RpcError` has no `PartialEq`; a 503-class `Reject` arm for infrastructure refusals (429 chosen); should bare `connect_socket(url)` also offer `vilan-rpc`? | design | b184-b218 + std-28's finds and open questions; OWNER on the last two |

## B. Type system & the type solver

| ID | Title | Kind | Discussion |
|----|-------|------|------------|
| [B3](items/B3.md) | Variadic-generics tail | feature | |
| [B11](items/B11.md) | `!` / `?.` tail | design | |
| [B146](items/B146.md) | NEW — the context coverage check's refinement consumes node-owned dispatch sites only | feature | |
| [B147](items/B147.md) | NEW — a module/file-level default for `[platform(...)]` | design | |
| [B149](items/B149.md) | NEW — an async function returning a `Task` mistypes as the task | bug | the pin names it since Order 21; the gap itself stays open |
| [B183](items/B183.md) | NEW — tuple comprehension `(item in tuple => EXP)` + the zip form | design | owner-proposed |
| [B243](items/B243.md) | NEW — a supertrait's default body does not substitute the impl's trait argument into a closure PARAMETER type when reached through a single-block sub-trait impl: `impl X<type T> with Signal<T>` types `x.map(\|v\| ..)`'s `v` as the trait's abstract `T` | bug | std-28's find; pre-existing, B164/B168-adjacent; A49 puts `sub` into the affected set — kolt's StorageSignalCell must SPLIT its impl until this lands |
| [B244](items/B244.md) | NEW — a conditional `Wire` impl reached through two generic parameters at once has no concrete receiver: `ops.describe(s)` on `List<Delta<K, T>>` compiles and fails at EMISSION with the never-silent `internal: a call resolved to Wire's requirement describe, which has no body` | bug | rpc-28's find; worked around element by element; B220's emission-side family |
| [B245](items/B245.md) | NEW — defaulted trait parameters, two more sites: the written `b: B` type id of `Add<B = Self>` is not the trait's recorded constraint id (B180's binding lookup misses; worked around), and impl CONFORMANCE reads the `= Self`/clause ambiguity B235 fixed for calls (`impl Blender with Mixed` still refuses) | bug | rigid-28's finds 1 and 2; the full Mixer program still does not compile |
| [B246](items/B246.md) | NEW — `fun bump<P: Add>(a: P) { a + 1 }` (a concrete right operand against a bounded parameter) still compiles and is UNSOUND for a struct whose `Add` declares `B = Self`; pinned as the boundary — close it, at what census cost? | design | rigid-28's find 3; OWNER Q |
| [B247](items/B247.md) | NEW — an i-string hole containing an OPERATOR is silently not a hole: `print("{1 + 2}")` emits the literal `{1 + 2}` | bug | rigid-28's find 4; silent |
| [B248](items/B248.md) | NEW — `match x { .. } + 1` in LEADING statement position is still refused: the block-like dispatch precedes the expression tower (B231 admitted block-likes as operands, not as heads) | bug | parse-fmt-28's find; low |
| [B249](items/B249.md) | NEW — the missing-member diagnostic's suggested declaration renders the TRAIT's parameter names unsubstituted: `impl Counted with Source<i32>` is told to `declare fun on_change(self, observer: \|T\| void)` for a `T` it does not have | bug | std-28's find 3; generic impls are right and pinned |
| [B250](items/B250.md) | NEW — file mode's two remaining disagreements: a dependency file opened as the entry has `package_of_source[SourceId(0)]` remapped to the dependency (an `import <depname>::…` in that file stops resolving); and `Declared` mode still loads a sibling's import of ANOTHER declared entry as a module while file mode refuses it — agreement per package, not per leg | design | checker-28's finds; OWNER Q on the second |
| [B251](items/B251.md) | NEW — a struct parameter reachable ONLY through another parameter's bound never grounds (`struct Held<T> { list: Signal<List<T>> }` leaves `T = any`), and the written form ACCEPTS `Held<i32, SignalCell<List<str>>>`: the bound is not checked against the written arguments at a struct's parameter list (UNSOUND) | bug | b184-b218's find 2; pre-existing, B186 family — the call-side recovery does not reach a struct literal |
| [B252](items/B252.md) | NEW — a refused RETURN annotation does not stand its uses down (`cannot call method 'who' on unknown` follows), where a refused closure parameter does (B182's stand-down) | bug | b184-b218's find 3; the return position's strongest practical argument (B253) |
| [B253](items/B253.md) | NEW — a bare trait in RETURN position (`fun f(): Trait`): the last value position that refuses; the case each way | design | b184-b218's question; OWNER decision; `fun get(): C` for a sugared struct is a SEPARATE, harder question |
| [B254](items/B254.md) | NEW — `async_infer::dispatch_candidates` still resolves `OnType(Some(receiver), member)` against EVERY same-named member when the receiver is KNOWN (only the `_for` call sites narrow): the miscoloring class a49-async fixed for trait default bodies, reachable via an inherited default on a concrete value | bug | lane a49-async's find (the merged-tree async regression's sibling) |

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
| [E145](items/E145.md) | NEW — rename through an import ALIAS collapses it (`greet as hello` → `greeting as greeting`); the fix is an alias entity of its own, which also restores references.rs INVARIANT 1 (an alias row's text is not its definition's name — the sole documented exception); the formatter does not drop a redundant `as x`; `as` is in neither highlighting grammar | editor | parse-fmt-28's finds; the E142 build's residue |
| [E146](items/E146.md) | NEW — formatter gaps N55's reformat exposed: `self` sorts LAST in an import group (ASCII order; 37 groups incl. std's prelude.vl/web.vl); an `if`/`match` arm body becomes a block mid-builder-ladder; a declaration's `context` clause prints where written (`fun f(): T borrows p context c` not round-tripped); a comment between a field name and its value relocates below the statement | editor | l19-ci + context-28 + parse-fmt-28's finds |
| [E147](items/E147.md) | NEW — a binary-operator chain has NO break rule: macro_std's hand-wrapped three-line `\|\|` condition became one 182-character line under N55's reformat (four lines over 100 in a tree whose target is 100) | editor | l19-ci's find; the worst of the reflows |
| [E148](items/E148.md) | NEW — the "declare the inferred contexts" quickfix fires only on the SUBSET refusal (a declared-but-narrow clause); on an UNDECLARED function it needs a signature insertion span the parser does not record, and the triggering diagnostic sits in a different function | editor | context-28's find; the more valuable half of B242's quickfix |
| [E149](items/E149.md) | NEW — editor-28's smalls: `diagnostics_budget`'s `#[ignore]` reason should record its load-dependence (690–831 ms at loadavg ~100, a quiet box passes); hovering `==` answers nothing (no operator-token hover); `Document::references` hands back DERIVED_SOURCE rows (only `references_across` drops them); rename at a shorthand CARET renames whichever side declaration order gives | editor | editor-28's finds |

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
| [L20](items/L20.md) | NEW — L19's step 2, the owner's own: the Windows test leg run natively on the WSL2 host (`powershell.exe -c "cargo nextest run --workspace"` with a Windows toolchain), the one leg that is compile-only locally — three seals running, Windows had the last word | process | the owner's 'whenever' (2026-09-04); a `scripts/ci-windows-host.sh` wrapper once it works |

## M. Performance & footprint — NEW SECTION

| ID | Title | Kind | Discussion |
|----|-------|------|------------|
| [M10](items/M10.md) | NEW — mechanize the BASE_CACHE transmute's completeness claim | perf | |
| [M12](items/M12.md) | NEW — the corpus leak-soak passes in 0.005 s asserting nothing when its corpora are absent | perf | |
| [M17](items/M17.md) | NEW — cross-subject body sharing, M16's residual | perf | separate decision |
| [M18](items/M18.md) | NEW — a function attribute marking a bundle boundary | design | owner-proposed; lucide the exhibit |
| [M19](items/M19.md) | NEW — an unchanged package module is re-analyzed every LSP analysis / HMR round | perf | E106's prime hypothesis; lucide's 636 KB |
| [M27](items/M27.md) | NEW — `lsp-index` editor tables 110–584 ms per keystroke, outside analyze and every tranche — MEASURED (e126): on the phase line after `capture_landed`, with `lsp-landed`; the per-module fix half stays | performance | m19-paper's find; measurement half landed Order 27 |
| [M32](items/M32.md) | NEW — allocation ~19% of a cold check: the parser moves `Node` by value, 1.1M `Type` clones | performance | kolt-benchmark's find; census recorded, two slices |
| [M33](items/M33.md) | NEW — four macro-world compiles per CLI process, ~18% of a small entry, cached only in-process | performance | kolt-benchmark's find; phase line hides them |
| [M36](items/M36.md) | NEW — the base cache is process-global and in-memory, so one process per corpus program re-analyzes std: a 3.5–5 s floor per test (infer differential 12 → 47 s, release 56 s) | performance | hygiene-27's find; N49 paid this bill silently |
| [M42](items/M42.md) | NEW — M19 tranche 1c: a resolved-`Type` record for the drop planner (`plan_resource_drops`, `record_drop_sink_argument_types`, `build_drop_glue`, `compute_resource_types`) so it can be restored per reused module — no `TypeId` may cross the record (ids are minted per occurrence against the entry's buffer) | performance | m19-t1b's deferral; the largest single item left in the phase (59–149 ms warm) |
| [M43](items/M43.md) | NEW — the const-eval interpreter's environment maps (`interpreter::lookup`/`assign`) still hash with SipHash: 83M of the 85M Ir left in `sip.rs` after M31, 1.3% of a kolt client check — the comment that left them there ("not in the cold-analysis hot path") is false | performance | compile-perf-28's find |
| [M44](items/M44.md) | NEW — M35's measured shortfall: a multi-entry `check` starts its second member cold and recomputes the base world (1.13× one entry at +63% CPU if all start cold; the shipped design keeps CPU flat at −16% wall); a base-cache "under construction" claim so a second cold member WAITS for the first's world (M23's territory); `build` and `check_single`'s per-platform loop are still sequential | performance | compile-perf-28's finds 3 and 4 |
| [M46](items/M46.md) | NEW — `CHECKED_CACHE`'s new table slice is bounded by an 8M-row budget beside the key bound; a real BYTE budget in M24's shape (and M36's on-disk world, whose `World` serialization does not exist yet) is the honest shape | performance | m19-t1b's find; M36 stays open with its design |

## N. Hygiene & rot — NEW SECTION

| ID | Title | Kind | Discussion |
|----|-------|------|------------|
| [N16](items/N16.md) | NEW — the recurring codebase audit | process | |
| [N20](items/N20.md) | NEW — `.claude/` is live configuration that no gate can see, and it had three dead pointers in it | process | |
| [N23](items/N23.md) | NEW — 37 `pub` items in `vilan-core` are never referenced outside their own file | process | |
| [N35](items/N35.md) | NEW — `hmr_css_matrix` reads the bundle while the watcher writes it | bug | load-dependent race, seen once |
| [N47](items/N47.md) | NEW — an output-asserting docs form (`vilan,run` + transcript) | process | docs-law's proposal |
| [N58](items/N58.md) | NEW — smalls from Order 28: E128's own pin imports `std::operators::PartialEq` (the misleading line that seeded the E138 phantom); a crashed differential leaves `file-corpus-<n>/` in crates/vilan-core ungitignored; markdown docs fences are outside the `vilan fmt --check` gate; `transport_robustness` flaked once on `EADDRINUSE` under lane load (N40's family — a second strike earns an item) | hygiene | hygiene-28, editor-28, l19-ci's finds |
