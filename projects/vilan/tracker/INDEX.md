# Vilan tracker — open items

`backlog <ID>` resolves to `items/<ID>.md` if open, or a tombstone in `archive.md` (or the frozen chain it points at) if closed — see `proposal/tracker-migration.md` §2.

## A. Reactive core & UI (`std::reactive`, `std::ui`)

| ID | Title | Kind | Discussion |
|----|-------|------|------------|
| [A7](items/A7.md) | SSR tail | design | |
| [A8](items/A8.md) | UI styling — the tail | design | |
| [A14](items/A14.md) | Reactive residuals | design | |
| [A37](items/A37.md) | NEW — `[gone]` trait-member attribute: reachable only through the trait (method surface, for blanket impls) | design discussion | NOT queued; the owner unsure of its value |
| [A46](items/A46.md) | NEW — fragment syntax `<>..</>` lowering to a `List<View>` literal (reverses element-syntax.md §7's refusal); NOT a multi-root View | feature | owner's ask (kolt); S–M for the list lowering, L for a marker-node fragment; owner to say which |
| [A53](items/A53.md) | NEW — a GENERIC source field for `[expose]`/`[service]` (A52's split-off): `ServiceItem` (meta.vl) carries no generics so the expansion cannot spell `impl Store<type T>`; the contract hash is built from WRITTEN types so every instantiation hashes identically (a `Store<Task>` client would connect to a `Store<Note>` server); `Client::connect(url, codec)` has nowhere for the element type to come from — three answers wanted before a build | design | rpc-29's investigation (2026-09-06), both spellings pinned red (f162e63c); B184's trait-typed-field carve-out is the other spelling's refusal |
| [A54](items/A54.md) | NEW — a `Delta`-producing CELL for the keyed exposure (A51's split-off): `keyed_diff` re-keys two snapshots and `KeyedSource::apply` reaches `index_of` per op, both O(N) — 1,000 rows 1.08 ms per change per connection, 10,000 rows 8.83, linear in the collection and in connections (`getrusage`, loadavg 128–169) — irreducible while the source is `List`-valued: only the MUTATION knows what changed | design | rpc-29's measurement and decision (2026-09-06); a new std type with mutators, a `Source` impl, `expose_keyed_cell`, its own attribute spelling, an op-log trimming policy and a `Reset` fallback |
| [A55](items/A55.md) | NEW — the mirror seams A52 left: `KeyedSource` is still not a `Source` (A52 covered `RemoteSource` only), and a `RemoteSource<List<T>>` is a `Source<Option<List<T>>>`, so `bind_each` still takes `or([])` — a `Source<Option<List<T>>>` sibling for `bind_each`, or the boundary stays deliberate | design | rpc-29's finds and open Q (2026-09-06); the boundary is pinned and documented today |
| [A56](items/A56.md) | NEW — two rpc rulings after A51/A52: `[expose(keyed = K)]` over a `Map<K2, V>` whose argument disagrees with `K2` — today the argument silently wins and the mismatch surfaces as a plain type error at the mirror (refuse at the attribute?); and A48's `authorize_timeout` still answers 429 now that `Reject::Unavailable` is 503 (std refusing on the app's behalf is not the app's judgement — re-rule or leave) | design | rpc-29's open questions (2026-09-06) |
| [A67](items/A67.md) | NEW — A65's ruling left open: `import pkg::a::b` where `a.vl` DECLARES an item `b` and `a/b.vl` also exists takes the FILE (longest module prefix wins, documented in `longest_module_prefix`), not an ambiguity error — unlike `a.vl` + `a/lib.vl`, which is one | design | lane a65's find (2026-09-08); OWNER Q — my recommendation: the ambiguity error, one rule for both collisions |
| [A71](items/A71.md) | NEW — a reactive element child APPENDS on replacement, like `when`/`swap`: `std::dom` has no `insertBefore`, so a `Source<View>` child's position is lost after its first change — a marker node and `insert_before` would keep it; is "put it last" the contract? | design | view-30's find 2 and open question 2 (2026-09-08); OWNER Q — my recommendation: keep position (a child that moves on update is a bug a reader cannot see in the source) |
| [A72](items/A72.md) | NEW — `std::router` after A62: `segments` (raw) and `parse_path().segments` (decoded) disagree on `%20` — two forms of one question, making `segments` decode is the tidier end state (a behaviour change not taken); and `current_path()` is pathname-only so `parse_path(current_path().get())` never sees a query — there is no SIGNAL over the full URL (`location_url()` is a read), so an app routing on `?q=` still wires its own `popstate` | feature | dom-30's finds 1 and 2 (2026-09-08) |
| [A73](items/A73.md) | NEW — std-30's two unshipped halves: `Storage` key ITERATION (today `len` + `key_at` by hand; a `keys(): List<str>` or an iterator) and `Debounce::flush()` (fire the pending callback now — a form that unloads before the window closes needs it) | feature | std-30's open questions (a) and (b) (2026-09-08) |
| [A74](items/A74.md) | NEW — RETURN-TYPED SIGNAL HANDLES (transport-rpc §9.2, the owner's point 1; §8's unbuilt half): an `[rpc]` method returning `SignalCell<T>` / `S: Source<T>` / `Option<SignalCell<T>>` becomes a stub returning `Result<RemoteSource<T>, RpcError>`; the reply carries a plain-Wire `ChannelId` exported into the connection's capability table inside the reply's turn; the mirror remembers its minting call (`origin`) and is re-issued on reconnect; R3 AS RULED (owner, 2026-09-09): demand decides — lease-zero defers to the turn's settle then one microtask look, `Unsubscribe` on a DYNAMIC channel is a revoke, a re-acquire re-mints from `origin`, a never-leased handle is released with its ambient owner; no new frame; R7: a source-returning method is a getter by declaration | feature | Order 31 lane handles-31 (TOP); the kolt exhibit `get_messages(conversation, amount): List<MessageId>` + `get_message(id): SignalCell<MessageBody>` (store.vl:102–109) |
| [A75](items/A75.md) | NEW — CLIENT-DECLARED FUNCTIONS, notifications only in v1 (transport-rpc §9.3, the owner's point 3; rulings R1 + R4): `[client_service]` on the browser struct generates its dispatcher, contract hash and a typed `<Name>Proxy`; `[service(X, client = H)]` appends `client:<method>(..)->void;` to the server's contract surface; `Connection::client()` hands the factory a typed proxy; a one-way reverse lane (text `s:<id>:<payload>`, binary tag `0x73`) in the server's id namespace; the handler instance supplied at connect; an old client's silent drop of `s:` frames is fenced by the contract hash; awaited server→client calls are v2 | feature | Order 31 lane reverse-31; kolt's TODO at store.vl:93 ("how client functions can be called from the server"); first use: `session_revoked()` |

## B. Type system & the type solver

| ID | Title | Kind | Discussion |
|----|-------|------|------------|
| [B3](items/B3.md) | Variadic-generics tail | feature | |
| [B11](items/B11.md) | `!` / `?.` tail | design | |
| [B146](items/B146.md) | NEW — the context coverage check's refinement consumes node-owned dispatch sites only | feature | |
| [B147](items/B147.md) | NEW — a module/file-level default for `[platform(...)]` | design | |
| [B149](items/B149.md) | NEW — an async function returning a `Task` mistypes as the task | bug | the pin names it since Order 21; the gap itself stays open |
| [B183](items/B183.md) | NEW — tuple comprehension `(item in tuple => EXP)` + the zip form | design | owner-proposed |
| [B272](items/B272.md) | NEW — an `[rpc] fun f(&mut self, …)` REFUSES the build (the generator emits `fun dispatcher(self)` by value and every route closes over that copy — rpc.vl ~:3249/:3188/:3193) with a diagnostic on the STRUCT that recommends the receiver the author just wrote; the admitted `mut self` compiles and SILENTLY LOSES the write (the next call on the same connection reads the old value); only `Shared<T>` fields persist per connection — the owner's `is_authenticated: bool` sketch cannot be written today | bug | rpc-paper-30's 9.1 verification (2026-09-08), pinned `a_mut_self_rpc_mutation_is_lost_where_a_shared_field_survives`; R-A38b in transport-rpc §9.5 |
| [B273](items/B273.md) | NEW — UNSOUND: an impl's `with` clause is bound-checked by NOTHING and arity-checked by nothing — `impl CatBox with Holder<Cat>` compiles with `Cat` implementing no `Label`, and `impl CatBox with Holder<Cat, i32>` compiles too (B188's arity check misses the position); the tour (data-and-traits.md) asserts the opposite in prose | bug | solver-30's find 1 (2026-09-08), pinned `#[ignore]`d as `b262_an_impl_with_clauses_trait_argument_is_still_unchecked`; predates B262 — a site apart from the `prepped_type_locals` drain |
| [B274](items/B274.md) | NEW — `shared.read().push(x)` GROWS the cell: a temporary read stays free under the B256 ruling and a `&mut self` receiver is not a considered position, so the write lands in the cell; four doc sites say the write is lost (tour/memory-model.md:172, :240; std/cells.md:36; appendix/gotchas.md:44) and spec/memory.md:377 says `read()` copies — a ruling: copy at a `&mut self` receiver on a temporary read (the docs' promise, the narrow remnant of clone-at-every-read), or rewrite the five sites | design | rule1-30's find (2026-09-08); OWNER Q — my recommendation: the copy, it is what every reader of those pages already believes |
| [B275](items/B275.md) | NEW — `satisfies_trait_bound` drops trait ARGUMENTS on a SUPERTRAIT match (v1, documented in-source): a program with only `Source<str> with Place` still ADMITS `slot(signal_of_panel)` at the analyzer, and only the emission filter's never-empty fallback keeps it from an internal-error report — closing the gap turns it into a real bound refusal at the call site | bug | view-30's find 1 and open question 1 (2026-09-08); B268 fixed the direct-bound half |
| [B276](items/B276.md) | NEW — a leg that BUNDLES anything is never `Fresh` under `build --watch`: `asset::bundle` records `content_hash_bytes(&bytes)` (const_eval.rs ~487) while `current_source_hash` re-hashes with `read_source` + `content_hash`, and the two never agree, so `leg_is_current` always fails — kolt bundles heavily and its watch reuses nothing today; reproduced under `VILAN_SEQUENTIAL_BUILD=1`, so pre-existing (M22/E12 class) | bug | build-30's find 1 (2026-09-08); forced its watch pin onto a bundle-free fixture |
| [B277](items/B277.md) | NEW — `std::time::Debounce`'s driving loop runs under the ambient nursery, so a nursery cancellation unwinds it with `running` still true and leaves that `Debounce` value INERT (every later `run` is swallowed); not pinned | bug | std-30's open question (c) (2026-09-08) |
| [B278](items/B278.md) | NEW — an i-string hole cannot contain an ESCAPED QUOTE: `i"{x.get(\"k\")}"` is a parse error, so a call with a string argument inside a hole must be bound first; cost a lane an iteration | bug | std-30's find 3 (2026-09-08) |
| [B279](items/B279.md) | NEW — the silence behind B258 has no STRUCTURAL guard: nothing forbids a future over-approximation promoting a node to strict that coverage's narrower edge set never fences — the result would again be a silent `undefined`; and B254 + B258 are one class (a NAME-keyed `candidates_of` list consumed as receiver-specific) with a third instance named in `impl_members_for_bound`'s doc — a sweep of `candidates_of` consumers is owed (the const-only capability check reads edges as refusals and is safe by direction) | bug | b258's finds 1 and 3 (2026-09-08) |
| [B280](items/B280.md) | NEW — `freshen_list_element_slots`' EXTERNAL-function path is unguarded: B263 guarded only the declared-function return, so an external method returning `List<T>` reached through a bounded receiver would still erase the caller's rigid `T`; no exhibit found | bug | solver-30's find 2 (2026-09-08) |
| [B281](items/B281.md) | NEW — the server's receive loop SERIALIZES frames TCP coalesced into one read: `for event in parser.feed(chunk) { … turn(FlushPolicy::AtEnd, \|\| protocol.respond(…)) … }` (rpc_server.vl ~1117–1176) awaits each event's `respond` before parsing the next, so a handler that awaits something only the NEXT frame's handler supplies never completes — on a fast local link coalescing is the common case; a present-tree hazard and the prerequisite of every awaited server→client call | bug | transport-rpc §9.3's "the router never blocks on a handler" (rpc-paper-30, 2026-09-08); Order 31 lane reverse-31 with a red-first pin |

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
| [E154](items/E154.md) | NEW — E150's third: a `for x in <iterable>` head lacks the split permission rule B gave `for` conditions and `match` subjects (a 117-column iterable is left untouched); the obvious one-line sibling | editor | fmt-30's find 1 (2026-09-08); OWNER Q — my recommendation: yes |
| [E155](items/E155.md) | NEW — PRE-EXISTING, confirmed on f0f4e301: on kolt's generated `src/lucide/lib.vl` `vilan fmt` rejoins a hand-broken four-link `.child` ladder into one over-budget line and then breaks INSIDE an element argument (`.child(<path⏎ d(…)⏎/>)`), which reads worse than the source; visible only because kolt excludes `src/lucide` from its fmt gate | editor | fmt-30's find 2 (2026-09-08) |
| [E156](items/E156.md) | NEW — E151 moves EVALUATION ORDER: an attribute value is an arbitrary expression, so sorting attributes reorders when their values run; the sorter documents the bargain (the style-chain sorter took the same one) rather than refusing impure values — a ruling: accept, or refuse to reorder a head whose values are not literals or pure paths | design | fmt-30's semantics note (2026-09-08); OWNER Q — my recommendation: accept and document, as the chain did; a side-effecting attribute value is already a smell the formatter should not be the first to notice |
| [E157](items/E157.md) | NEW — a block-like head followed by `::` takes B248's parenthesize steer, which is not a fix there (`(match x {..})::foo` is not valid either); `::` is a `Token::Op` and needs its own arm | editor | smalls-30's find 1 (2026-09-08); pre-existing B248 behaviour |
| [E158](items/E158.md) | NEW — editor smalls from Order 30: `references.rs`'s `narrow` trusts that an `Anchor::Start`/`End` span spells its definition's name — B264 fixed the alias case, and every other table whose span is DERIVED rather than recorded has the same exposure (a sweep); `is_namespace_module` discriminates on "attributed to `SourceId(0)` and has a children scope" — the `pkg::<entry>` alias arm is the other `SourceId(0)` entity and the discriminator is thin, a third such entity needs a real marker | editor | editor-30's finds 1 and 2 (2026-09-08) |

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
| [M19](items/M19.md) | OPEN — an unchanged package module is re-analyzed every LSP analysis / HMR round; T1a–T1d landed (Order 30), next M55/M56/M57 | perf | E106's prime hypothesis; lucide's 636 KB |
| [M27](items/M27.md) | NEW — `lsp-index` editor tables 110–584 ms per keystroke, outside analyze and every tranche — MEASURED (e126): on the phase line after `capture_landed`, with `lsp-landed`; the per-module fix half stays | performance | m19-paper's find; measurement half landed Order 27 |
| [M36](items/M36.md) | NEW — the base cache is process-global and in-memory, so one process per corpus program re-analyzes std: a 3.5–5 s floor per test (infer differential 12 → 47 s, release 56 s) | performance | hygiene-27's find; N49 paid this bill silently |
| [M54](items/M54.md) | NEW — `LastUse`/`source_of` residuals from perf-30's re-pricing: the restored tables are CLONED into `LastUse::compute`'s walk state (8.9M Ir per analysis — needs `&mut Analyzer` or a read-through layer); `collect_unfollowable_loans` is 68% of the warm `LastUse` (whole-program by nature, a loan crosses modules — a record DESIGN); `Program::source_of` is still a linear scan of ~60 ranges and now the residual in `arrival_by` (`source_lookup` exists but is not the default); and `compute_shared_read_bindings` (B267) adds a second whole-program `collect_written_roots()` walk beside the capture pass's | performance | perf-30's and rule1-30's finds (2026-09-08) |
| [M55](items/M55.md) | NEW — module-level SHARING across the platform axis: M52's union key was refused because kolt's browser leg is 82% of all base time and no seed union crosses the platform; the node legs load 48 and 49 sources from disjoint seeds but the FILES overlap — sharing a module's analyzed world across legs (and platforms where coloring allows) is where kolt's remaining base-cache headroom is | performance | perf-30's M52 conclusion and open question 2 (2026-09-08); OWNER Q — M19's next tranche or its own item |
| [M56](items/M56.md) | NEW — R10's residue after T1d is the ENTRY's share of the sweep: 24,459 of 153,302 sites still walked, because the tier enumerates `expr_id_to_expr_map`/`variables`/`parameters` whole and ids minted after the world was stored fall in no range — removing it needs a source→entity index, §3.5's missing module boundary | performance | m19-t1d's find 2 (2026-09-08); the next tranche's shape |
| [M57](items/M57.md) | NEW — the corpus replay differential is BLIND to the R10 seam (and to T1b's): the golden corpus as modules declares almost no resource and none in a container, so a dropped-keys plant leaves `replay_differential` green — an R10 probe (a `List<Guard>` in every third module) would make the standing gate see it; it means editing a shared test function, which needs an owner's word or a lane that owns the file | performance | m19-t1d's find 1 and open question 1 (2026-09-08); OWNER Q |
| [M58](items/M58.md) | NEW — on a WARM analysis `post_analysis_passes` is 62.7% of the work (57.1% after M53): the warm profile is a different shape from the cold one, and every lane profile so far has used the cold one — the keystroke path is the warm shape | performance | perf-30's find 1 (2026-09-08); a rule for M briefs as much as an item |
| [M59](items/M59.md) | NEW — build-30's two follow-ups: persist the leg RECORD into `dist/` so a plain `build` gets the schedule's edges (and the artifact-edge guard's redo) from the second build on, not only under `--watch`; and give the HMR round's own compile loop (`run --watch`, ~main.rs:1340) the same tiering — it writes `dist/` after the whole loop, so the guard's shape differs | performance | build-30's open questions 1 and 2 (2026-09-08) |

## N. Hygiene & rot — NEW SECTION

| ID | Title | Kind | Discussion |
|----|-------|------|------------|
| [N16](items/N16.md) | NEW — the recurring codebase audit | process | |
| [N20](items/N20.md) | NEW — `.claude/` is live configuration that no gate can see, and it had three dead pointers in it | process | |
| [N23](items/N23.md) | NEW — 37 `pub` items in `vilan-core` are never referenced outside their own file | process | |
| [N35](items/N35.md) | NEW — `hmr_css_matrix` reads the bundle while the watcher writes it | bug | load-dependent race, seen once |
| [N47](items/N47.md) | NEW — an output-asserting docs form (`vilan,run` + transcript) | process | docs-law's proposal |
| [N65](items/N65.md) | NEW — ledger hygiene: parser CURATED rule statements (`CSS_BLOCK_IS_BRACE_INITIAL`, `IMPORTANT_HAS_NO_PLACE`, E153's `:hover` rule) are not enumerated by the ledger gate, so E153's "row EDIT" had no row to edit; and `resource_derive_refusal`'s message carries no ledger row at all (a helper-built `msg:` the ledger's checks cannot reach or miss) — unrowed messages, not red ones | hygiene | css-30's find 1 and smalls-30's find 3 (2026-09-08) |
| [N66](items/N66.md) | NEW — harness notes from Order 30: the replay harness drives kolt's client clean only with `pkg_root = <repo>/src` (the manifest's `root`) — the repo root gives 22 spurious "cannot find … in the imported path" errors and 39 sources instead of 69, a trap for anyone measuring a real package; `reused_source` and `container_site_visited` are two spellings of one predicate at two granularities | hygiene | m19-t1d's finds 4 and 5 (2026-09-08) |
| [N67](items/N67.md) | NEW — two rulings the hygiene lane left: does N63's "every on-disk cache under `dist/.cache/`" include `dist/.build-hooks.json` (a stamp under build-hooks §3.3 Q2, deliberately not moved), and build-hooks.md:1035's Q5 (`generated` as a second module root "since a subdirectory cannot be imported today") is overtaken by A65 — the generated root can be an ordinary subdirectory of `root` (`src/lucide/*.vl` resolves as `pkg::lucide::*`; the manifest key `generated_root_problem` still exists) | process | hygiene-30's open question and N64's reported note (2026-09-08); OWNER Qs on the build-hooks paper |
| [N68](items/N68.md) | NEW — the weakest survivor of N61's wall-bound sweep: `service_layer.rs:1667` bounds a raw handshake at 2,500 ms against a 300 ms claim — not over a build, but still wall on a shared box | hygiene | hygiene-30's find 1 (2026-09-08) |
| [N69](items/N69.md) | NEW — `element_view_import_note` (analyzer.rs ~21871, "element syntax lowers to std::ui::view; add `import std::ui::{ view, View };`") is UNREACHABLE after B270 whenever std holds `ui::view`: the element seeds a scope-independent `std::ui::view` and a miss degrades to the site's scope only when std lacks the item; the note has no ledger row, so no gate notices a dead note — and the seal found the only pin of the old behaviour in vilan-lsp (the add-import quickfix's element target), which no lane gate ran | hygiene | the Order 30 seal repair (2026-09-08): the quickfix pin re-aimed at the `View` type; B270's element side pinned from the editor too |
