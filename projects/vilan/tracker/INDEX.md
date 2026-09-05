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
| [A39](items/A39.md) | NEW — `[expose]` resyncs the whole value on every change; a message edit costs the channel (keyed deltas + per-key subscription over the wire) | design | owner's ask (kolt); a recipe exists today but stops at the generated client; needs A38 first |
| [A46](items/A46.md) | NEW — fragment syntax `<>..</>` lowering to a `List<View>` literal (reverses element-syntax.md §7's refusal); NOT a multi-root View | feature | owner's ask (kolt); S–M for the list lowering, L for a marker-node fragment; owner to say which |
| [A47](items/A47.md) | NEW — a refused client burns the full retry budget (~24 s of backoff) and reports `Transport("could not reach …")`: the host WebSocket surfaces no HTTP status, so a 401 is indistinguishable from an unreachable server | design | rpc-27's find; wants a host-specific error read or a post-upgrade refusal frame |
| [A48](items/A48.md) | NEW — `authorize` is awaited inside the upgrade handler, so a slow verifier holds an unanswered socket (its own DoS surface); `handshake_rate` mitigates, a verification timeout is the honest addition | design | rpc-27's find |
| [A49](items/A49.md) | NEW — std-27's residuals: `Source::on_change` as a requirement later (migration paid); `bind_each_by`'s render gets a writable `SignalCell<T>` (a read-only projection needs a wrapper type); `Selector<T>` is a handle where Solid returns a function | design | RULED 2026-09-05: invert to on_change-required; Order 28 std lane |

## B. Type system & the type solver

| ID | Title | Kind | Discussion |
|----|-------|------|------------|
| [B3](items/B3.md) | Variadic-generics tail | feature | |
| [B11](items/B11.md) | `!` / `?.` tail | design | |
| [B146](items/B146.md) | NEW — the context coverage check's refinement consumes node-owned dispatch sites only | feature | |
| [B147](items/B147.md) | NEW — a module/file-level default for `[platform(...)]` | design | |
| [B149](items/B149.md) | NEW — an async function returning a `Task` mistypes as the task | bug | the pin names it since Order 21; the gap itself stays open |
| [B183](items/B183.md) | NEW — tuple comprehension `(item in tuple => EXP)` + the zip form | design | owner-proposed |
| [B184](items/B184.md) | NEW — trait annotations on struct fields, one-instantiation rule | design | RULED 2026-09-05: Q3 = print `C<A>`; build queued Order 28 (fields only, bare grammar) |
| [B218](items/B218.md) | NEW — two implicit generics of one trait print the same name: `Expected X, but got X` (Q3's diagnostic face) | bug | RULED 2026-09-05: print `C<A>`; Order 28 with B184 |
| [B220](items/B220.md) | NEW — an array receiver has B210's emission-side hole (`resolve_member_on_type` excludes arrays) | bug | RULED 2026-09-05: arrays join; Order 28 |
| [B231](items/B231.md) | NEW — a `match` expression as a binary operand (`flag && match probe() { .. }`) is a parse error: `found 'else' expected an expression` | bug | lane b224's find (2026-09-04); pre-existing parser limit |
| [B232](items/B232.md) | NEW — a leftover `Constraint::MethodCall` after the fixpoint produces no residual diagnostic of its own; B229's clean-program guard exists only because of it | bug | context-27's find; giving MethodCall a residual lets the guard go |
| [B233](items/B233.md) | NEW — `fun sum<P: Add, Q>(a: P, b: Q): P { a + b }` compiles and `sum(1, "two")` runs: the operator-dispatch site retains away the free binders, so two different rigid parameters meet on an operator (UNSOUND) | bug | b225-b219's find; B211's sibling |
| [B234](items/B234.md) | NEW — `fun f<T>(x: T) { if x { } }` compiles: a rigid parameter satisfies a `bool` condition (UNSOUND) | bug | b225-b219's find |
| [B235](items/B235.md) | NEW — a `= Self`-defaulted trait parameter is read as a BOUND when the member is reached through a sub-trait's parameterized clause: `trait Mixer<A = Self, B = Self>` under `trait Mixed with Mixer<i32, str>` refuses `i32` | bug | cascade-27's find; B216's two-parameter pin uses undefaulted parameters because of it |
| [B236](items/B236.md) | NEW — the entry-cycle refusal (B226) still cascades three follow-ons: `cannot find 'X' in the imported path` and two `cannot find type` | bug | checker-27's find; the stand-down machinery could root them |
| [B237](items/B237.md) | NEW — `prepped_assignments` wiring skips a target whose local resolves late: an assignment to a guard continuation binding never reaches the wiring's own `cannot assign to this expression` arm | bug | divergence-27's find; the refusal survives via `check_readonly_mutation` (pinned) |
| [B238](items/B238.md) | NEW — `disabled` is not usable as a binding name (parse error): a reserved-word leak | bug | std-27's find while writing A42's pins |
| [B240](items/B240.md) | NEW — file mode's residues after B239: B226's refusal is pushed once PER IMPORTED NAME at one span (raw LSP diagnostics do not dedup); file mode cannot see that ANOTHER file is a declared entry (`views.vl` importing `pkg::client::helper` is clean in file mode, refused by `check .`); a DEPENDENCY file opened as the entry would lose its own derives (`base_cacheable` pre-marks SourceId(0), undone only under `!entry_is_module`) | bug | b239's finds |
| [B241](items/B241.md) | NEW — an ARITY-invalid call to a context-reading function cascades into the context pass: `channel_component(stub_user)` (one argument short) yields the arity error PLUS three "reads context X, so it can't be used as a value" at the call and five "can be reached without an enclosing run" fences, four of them in std's reactive.vl | bug | the owner's report (2026-09-05); B229's family, the callee side; reproduced on a kolt copy from its own directory |
| [B242](items/B242.md) | NEW — `context` clauses on `fun` declarations (`fun f(x: f64) context settings`): an explicit requirement that anchors coverage diagnostics at the declaration and stops cascades like B241 at the boundary | design | the owner's proposal (2026-09-05); the closure-type clause exists (ledger row 47) — extend the grammar; RECOMMEND yes, optional; paper section + build in Order 28 |

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
| [D6](items/D6.md) | NEW — the grammar EBNF lists `!` and `?.` but no bare `?` postfix (grammar.md ~334), and spec §5.10's heading still reads "`!` and `?.`" | docs | b230's find; the grammar_ebnf/grammar_sync gates |

## E. LSP & tooling

| ID | Title | Kind | Discussion |
|----|-------|------|------------|
| [E37](items/E37.md) | bindgen v2 — the remainder | feature | |
| [E62](items/E62.md) | NEW — Zed language extension | feature | |
| [E69](items/E69.md) | NEW — attribute-NAME completion in an element head is a semantics decision | feature | |
| [E99](items/E99.md) | NEW — the `-d` dump's `.parse.out` is the post-desugar tree, and no dump shows the raw parse | process | |
| [E106](items/E106.md) | NEW — the language server slows down over a session | bug | owner report; measure first |
| [E121](items/E121.md) | NEW — the editor-latency mandate: <10 ms keystroke path, <500 ms errors | design | owner-set target; ARC, paper first |
| [E138](items/E138.md) | NEW — hover on `PartialEq::eq` and `PartialOrd::lt` returns nothing through both routes (default body, generic bound) where `Add::add`/`Sub::sub`/`Mul::mul` resolve | editor | cascade-27's find; a target-resolution gap, not rendering |
| [E139](items/E139.md) | NEW — hover at the end of a bare USE (`let _ = count\|`) still hovers the enclosing function: `vilan_ide::analysis::entity_at` is separately end-exclusive (shared with completion's receiver resolution) | editor | editor-sync-27's find; E133 fixed declarations only |
| [E140](items/E140.md) | NEW — E124's residue: paper §6.1 pins 4, 10, 11, 16, 19 unbuilt; withdrawal is package-wide, not the depends_on cone; the union analyses ignore M26's per-document scheduler | editor | e124-build's residue; no false gray appeared |
| [E141](items/E141.md) | NEW — the keystroke gate's per-request completion budget is a RELEASE figure and the gate has no profile guard: red at 289e2a2b under debug (0.705–0.813 ms vs 0.2), invisible because `#[ignore]`d | editor | RULED 2026-09-05: not slow in release (0.04 ms); profile guard; Order 28 |
| [E142](items/E142.md) | NEW — should a `::` path be allowed to cross a line break? E135's unfixed face: `style::` ⏎ `print(..)` is the legal path `style::print` and swallows the next statement | design | RULED 2026-09-05: no line-crossing `::` + import aliasing; Order 28 |
| [E143](items/E143.md) | NEW — rename at a struct-init shorthand refuses (E134); should it EXPAND to `A { new = old }` instead? | design | RULED 2026-09-05: expand; + formatter shorthand; Order 28 |
| [E144](items/E144.md) | NEW — derive-template double claims: two expansions of one `[derive(..)]` index the same DERIVED_SOURCE offsets (`Ordering` and `JsonKind` both claim 304..312) | editor | editor-sync-27's find; collapsed to one row as before; low |

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
| [L19](items/L19.md) | NEW — CI's verdict takes 30 minutes because both test legs compile the workspace COLD (ubuntu 25 min, windows 30; every other job under 3): a local gate script shared with ci.yml, rust-cache + nextest partitions on GitHub, the Windows leg on the owner's host | tooling | the owner's ask (2026-09-04); QUEUED for Order 28 (steps 1 and 3); step 2 is the owner's own setup |

## M. Performance & footprint — NEW SECTION

| ID | Title | Kind | Discussion |
|----|-------|------|------------|
| [M10](items/M10.md) | NEW — mechanize the BASE_CACHE transmute's completeness claim | perf | |
| [M12](items/M12.md) | NEW — the corpus leak-soak passes in 0.005 s asserting nothing when its corpora are absent | perf | |
| [M17](items/M17.md) | NEW — cross-subject body sharing, M16's residual | perf | separate decision |
| [M18](items/M18.md) | NEW — a function attribute marking a bundle boundary | design | owner-proposed; lucide the exhibit |
| [M19](items/M19.md) | NEW — an unchanged package module is re-analyzed every LSP analysis / HMR round | perf | E106's prime hypothesis; lucide's 636 KB |
| [M27](items/M27.md) | NEW — `lsp-index` editor tables 110–584 ms per keystroke, outside analyze and every tranche — MEASURED (e126): on the phase line after `capture_landed`, with `lsp-landed`; the per-module fix half stays | performance | m19-paper's find; measurement half landed Order 27 |
| [M30](items/M30.md) | NEW — `callee_bindable_generics` scans every impl/trait declaration list per call: 857k calls, ~9% of a client check | performance | kolt-benchmark's find (2026-09-04); orthogonal to M19 |
| [M31](items/M31.md) | NEW — the analyzer's 35 `IndexMap`s still hash with SipHash: 7.4M calls, 6.7% of a client check | performance | kolt-benchmark's find; E48's residual, an alias |
| [M32](items/M32.md) | NEW — allocation ~19% of a cold check: the parser moves `Node` by value, 1.1M `Type` clones | performance | kolt-benchmark's find; census recorded, two slices |
| [M33](items/M33.md) | NEW — four macro-world compiles per CLI process, ~18% of a small entry, cached only in-process | performance | kolt-benchmark's find; phase line hides them |
| [M34](items/M34.md) | NEW — `vilan check` of an entry runs the whole transformer (16% of a small entry) for one diagnostic | performance | kolt-benchmark's find; decision first |
| [M35](items/M35.md) | NEW — a multi-entry `check`/`build` compiles entries sequentially; one of sixteen threads | performance | kolt-benchmark's find; ≤18% on kolt, N× on balanced packages |
| [M36](items/M36.md) | NEW — the base cache is process-global and in-memory, so one process per corpus program re-analyzes std: a 3.5–5 s floor per test (infer differential 12 → 47 s, release 56 s) | performance | hygiene-27's find; N49 paid this bill silently |
| [M37](items/M37.md) | NEW — `collect_unfollowable_loans` is 60% of `LastUse` (450 of 758 ms on kolt's client): three full sweeps of `expr_id_to_expr_map`, the first allocating a `Vec<Convention>` per call only to test `is_some()` | performance | m28's find; byte-identical win of M28's order |
| [M38](items/M38.md) | NEW — `collect_resource_bindings` is ~100 ms on kolt's client: `type_is_resource` over every variable and parameter type with field recursion | performance | m28's find; answer-identical pre-filter |
| [M39](items/M39.md) | NEW — completion's remaining cost is documentation rendering: `doc_first_paragraph` reads the declaring module's whole text per request (0.415 → 0.324 ms with it stubbed) | performance | completion-27's find; the fourth completion tranche |
| [M40](items/M40.md) | NEW — M19 tranche 1b: Class D (`LastUse`, the ten `compute_*`, `infer_bumps`, the hover render — 34% of the phase) and the drop planner produce tables the emitter reads, so freezing them is cache-and-restore, not skip | performance | m19-t1's deferral; the remaining two-thirds of the phase |
| [M41](items/M41.md) | NEW — `type_id_sources` adds ~4 bytes per `TypeId` to every stored world, invisible to `base_cache_world_bytes` (text-proportional): M11/M24's tally under-reports | performance | m19-t1's find |

## N. Hygiene & rot — NEW SECTION

| ID | Title | Kind | Discussion |
|----|-------|------|------------|
| [N16](items/N16.md) | NEW — the recurring codebase audit | process | |
| [N20](items/N20.md) | NEW — `.claude/` is live configuration that no gate can see, and it had three dead pointers in it | process | |
| [N23](items/N23.md) | NEW — 37 `pub` items in `vilan-core` are never referenced outside their own file | process | |
| [N35](items/N35.md) | NEW — `hmr_css_matrix` reads the bundle while the watcher writes it | bug | load-dependent race, seen once |
| [N47](items/N47.md) | NEW — an output-asserting docs form (`vilan,run` + transcript) | process | docs-law's proposal |
| [N53](items/N53.md) | NEW — `interpreter.rs` still has the un-raised `NODE_TIMEOUT = 30 s` and one whole-corpus test at 58 s: N52's shape one layer over | hygiene | hygiene-27's find |
| [N54](items/N54.md) | NEW — `vilan/test/file.vl` writes a fixed `file-corpus.txt` relative to CWD and is run by both differentials concurrently: latent cross-talk of the kind `watch.vl` was fixed for | hygiene | hygiene-27's find |
| [N55](items/N55.md) | NEW — 96 `.vl` files (7 under std) already differ from their own formatter; there is no repo-wide `vilan fmt --check` gate. Decide: a CI gate after one reformat, or an explicit hand-formatted statement | design | RULED 2026-09-05: add the gate; Order 28 with L19 |
| [N56](items/N56.md) | NEW — `vilan check <absolute path>` with the cwd inside ANOTHER vilan checkout resolves that checkout's std: 37 `macro PartialEq's definition did not compile` cascades on kolt's sidebar.vl from the vilan tree, 0 from kolt's own directory | hygiene | b239's find; cost the lane a false alarm |
| [N57](items/N57.md) | NEW — M19 T1's corpus-as-modules differential runs inside vilan-core's inference binary and adds 60–170 s to every `-p vilan-core` run; give it its own binary in the slow group | hygiene | the owner unsure (2026-09-05, Q6); orchestrator's call: keep the gate, move it |
