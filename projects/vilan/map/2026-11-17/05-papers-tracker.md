# Papers and tracker audit (read-only), 2026-11-17

Latest release v0.56.1. Sources: `proposals/projects/vilan/proposal/` (182 entries), tracker `INDEX.md` (217 open rows), `archive.md` (1,440 closed bullets), chronicle, order records, `CHANGELOG.md` of the integration worktree (next @6edafda5).

Method notes: dates come from `git log` on the proposals repo (first = diff-filter=A, last = last touching commit). Note that 2026-08-28 as a first date for most older papers is the N17/N15 migration commit, not the writing date. "Declared status" is the first line in the first 40 lines containing "status" and a status word, else the first status-word line in 15 lines. Ids in head are the tracker-id-shaped tokens in the first 30 lines, flagged O = open in INDEX.md, C = tombstoned in archive.md, ? = in neither (retired in the frozen eras before archive.md, or not an item id). Classification is mine: status line plus tracker state plus changelog cross-check; where the header says nothing I inferred and marked it in the note.

## 1. Papers table

| file | title | first | last | declared status (quoted) | ids in head | class | note |
|---|---|---|---|---|---|---|---|
| README.md | Proposal directory index | 2026-08-28 | 2026-11-09 |  | ?N15 | SUPERSEDED/STALE | index frozen "as of 2026-08-03, re-verified 2026-08-18"; omits every paper after August |
| affine-moves.md | A consuming call is a move — closing B60 | 2026-08-28 | 2026-08-28 | > **Status: SHIPPED 2026-08-04** (backlog B60, found by the B53 follow-up arc | ?B53 ?B60 ?B62 | BUILT | SHIPPED 2026-08-04 |
| ambient-owner.md | The ambient owner (backlog A5) | 2026-08-28 | 2026-08-28 | Status: **COMPLETE 2026-07-07** — the basics (`owner_scope`/`get_owner`/ | ?A5 ?B15 | BUILT | COMPLETE 2026-07-07 |
| analysis-reuse.md | Analysis reuse — the E3 arc (leak closure, the prelude checkpoint) | 2026-08-28 | 2026-09-21 | > **Status: Phase 1 SHIPPED 2026-07-21; Phase 2 CLOSED BY MEASUREMENT same | ?E23 ?E28 ?E3 ?E30 | BUILT | Phase 1 shipped, Phase 2 closed by measurement; later work is the M-series |
| analyzer-pass-map.md | The analyzer pass map — every pass, what it reads and writes, what ord | 2026-10-09 | 2026-11-03 |  | OM110 | IN PROGRESS | reference map for the M110 arc (M110 open); "PAPER drafted 2026-10-08" |
| analyzer-refactor.md | Analyzer stabilization refactor | 2026-08-28 | 2026-08-28 |  | ?B145 | UNKNOWN | no status; B145 retired; a 2026-08 refactor note |
| argument-tail-descent.md | A statement's split reaches its call's last argument | 2026-08-28 | 2026-08-28 |  |  | BUILT | implemented 2026-08-01 |
| array-lengths.md | Array lengths — `[type T; _]`, `<const N>`, and the names a length may | 2026-10-10 | 2026-10-15 | > Status: **BUILT 2026-10-10 (Order 50, lane lang-50): S1–S6, S4 included — see §16.** Drafted | CA122 CA161 CA163 CB177 CB220 CB294 CB582 CE283 CF109 CG24 OI2 CI5 CL1 | BUILT | BUILT 2026-10-10 (Order 50); I2 tail still open |
| async-polymorphism.md | Async polymorphism: adaptation, `sync` contracts, scopes, and the para | 2026-08-28 | 2026-08-28 | **Status: Part A SHIPPED 2026-07-17** (four slices: `sync` marker 3b5e1db, | ?J1 ?J2 | IN PROGRESS | Part A SHIPPED 2026-07-17; Part B (structured layer) = J1 phases, J-items open |
| auto-annotations.md | `auto` annotations — types the toolchain writes and keeps current (B57 | 2026-10-09 | 2026-10-09 | > Status: **DRAFT 2026-10-08 — for the owner's ruling.** Written by lane papers-b-48 of | CB161 CB569 CB570 CB571 CE227 CE278 OM110 | BUILT | header DRAFT, but B570 CLOSED 2026-10-10 (Order 49) |
| b33-emission-order.md | B33 — module initialization order: dependency-ordered, specified, cycl | 2026-08-28 | 2026-08-28 | > **Status: RATIFIED 2026-07-25 — all §5 calls per recommendation** ((a) | ?B33 ?E16 ?E17 ?F7 | BUILT | RATIFIED 2026-07-25; B33 not open |
| backed-enums.md | Backed enums — a variant carries the value the host speaks (B76) | 2026-08-28 | 2026-08-28 | > Status: RATIFIED 2026-08-08 (owner review) — as drafted, every settled | ?B107 ?B76 ?E31 | BUILT | RATIFIED 2026-08-08; B76 retired; backed enums in std |
| backlog-2026-07-18.md | backlog-2026-07-18.md — moved (N15) | 2026-08-28 | 2026-08-28 |  | ?N15 | SUPERSEDED/STALE | stub "moved (N15)" to archive/ (marked) |
| backlog-2026-08-18.md | backlog-2026-08-18.md — moved (N15), renamed `tracker/backlog.md` (202 | 2026-08-28 | 2026-08-28 |  | ?N15 | SUPERSEDED/STALE | stub "moved (N15)" (marked) |
| backlog-archive.md | backlog-archive.md — moved (N15) | 2026-08-28 | 2026-08-28 |  | ?N15 | SUPERSEDED/STALE | stub "moved (N15)" (marked) |
| backlog.md | backlog.md — moved (N15) | 2026-08-28 | 2026-08-28 |  | ?N15 | SUPERSEDED/STALE | stub "moved (N15)" (marked) |
| beta.md | Beta — executing the ratified contract, and the annex that extends it | 2026-08-28 | 2026-08-28 | > Status: **RATIFIED 2026-08-18 as recommended** ("Go with the | ?B73 OD5 | RULED NOT BUILT | RATIFIED 2026-08-18, but the beta switch DEFERRED 2026-08-26 (chronicle); L3 open |
| bindgen.md | bindgen — generating `external` bindings from TypeScript headers (E31) | 2026-08-28 | 2026-08-28 | > **Status: RATIFIED 2026-08-04 (owner review)** — with three owner notes: | ?B76 ?E31 OE37 | IN PROGRESS | RATIFIED 2026-08-04; E37 open (bindgen probe); not found shipped |
| bits-and-bytes.md | Bits and bytes — the binary floor (backlog I2, codec prerequisites 1–2 | 2026-08-28 | 2026-08-28 |  | OI2 | BUILT | implemented 2026-07-02 |
| build-hooks.md | Build hooks and build-time accumulation — one staleness rule, one orde | 2026-08-28 | 2026-09-13 | > Status: DRAFT 2026-08-27 (cycle 34, work order 16, lane `build-hooks`), for | ?E96 ?G5 ?G6 | BUILT | header DRAFT 2026-08-27; ruled Q1-Q7 2026-08-28; [[build.hook]] in 25 changelog mentions |
| build-trust.md | Build-code trust — two tiers (E96) | 2026-08-28 | 2026-08-28 | > Status: **RULED 2026-08-26** by the owner, both tiers as proposed. Tier 1 | OD5 ?E93 ?E94 ?E95 ?E96 ?L14 OL15 ON16 | BUILT | RULED 2026-08-26; E96 retired; D5/L15/N16 named open |
| bundle-boundaries.md | Bundle boundaries — a function attribute that marks a fetch seam (M18) | 2026-09-01 | 2026-09-01 |  | OM18 | DRAFT/OPEN | DESIGN NOTE 2026-09-01, "recommendation awaiting a ruling"; M18 open |
| bundle-splitting.md | Bundle splitting — route chunks from whole-program reachability (A16) | 2026-08-28 | 2026-09-01 | > **Status: SHIPPED — arc complete, 2026-08-04** (drafted 2026-08-03; user | ?A16 ?B30 | BUILT | SHIPPED 2026-08-04 |
| canvas.md | Canvas — a typed 2D drawing surface over `std::canvas` (backlog A17) | 2026-08-28 | 2026-08-28 | > Status: DEFERRED 2026-08-04 (owner call) — pending the bindgen probe on | ?A17 OE37 | DRAFT/OPEN | DEFERRED 2026-08-04 (owner call) pending bindgen probe; E37 open |
| capture-clones.md | Pattern captures copy — closing B53's findings | 2026-08-28 | 2026-08-28 | > **Status: SHIPPED 2026-08-03** (backlog B53, second pass). The first pass | ?B53 | BUILT | SHIPPED 2026-08-03 |
| chain-seam-split.md | Chain seam split — a `})` that continues is not a line | 2026-08-28 | 2026-08-28 |  |  | BUILT | implemented 2026-08-01 |
| claims-and-epochs.md | Claims and epochs — one law for the memory model, and its closure | 2026-08-28 | 2026-08-28 | > **Status: RATIFIED 2026-07-18 (drafted and ratified the same day) — descriptive + | ?C4 ?C6 ?C7 | BUILT | RATIFIED 2026-07-18, descriptive |
| class-writes.md | Class writes — an element that writes its class more than once (A155) | 2026-10-08 | 2026-10-08 | > Status: **DRAFT 2026-10-05 — for the owner's ruling** (R-k: "census in papers-47, no build"). | CA155 CK26 | BUILT | header DRAFT 2026-10-05; A155 CLOSED |
| closure-captures-on-native.md | Closure captures on a native backend — §6.9 priced on Rust (C15) | 2026-09-28 | 2026-09-28 |  | CC14 CC15 OF1 | BUILT | C15 closed; priced §6.9 on Rust; no status line |
| closure-captures.md | Closure captures — what §6.9's shared binding costs, and which narrowe | 2026-10-08 | 2026-10-08 | > Status: **DRAFT 2026-10-05 — for the owner's ruling.** Written by lane papers-47 of Order 47 | CC15 CC16 CF16 CF39 CF47 CF48 CF49 CF50 | BUILT | header DRAFT 2026-10-05; C15/C16 closed |
| closure-owner.md | Closure parameters and the owner they build under (B677, door 2) | 2026-10-26 | 2026-11-03 | Status: **BUILT 2026-11-03 (lane solver-56 05f25ec2 + 211e6259; merged to next; rides v0.54.0, BREAKING; B677  | CB677 CM172 | BUILT | BUILT 2026-11-03 (v0.54.0) |
| closure-type-views.md | Views in closure types — carry `&`/`&mut` in `Type::Closure`, not in a | 2026-10-08 | 2026-10-08 | > Status: **DRAFT 2026-10-03 — for the owner's ruling.** Written by lane papers-46 of Order 46 | CB309 CB400 CB465 CB467 CB495 CF18 CF69 | BUILT | header DRAFT 2026-10-03; B309/B400/B465/B467 etc. closed |
| compiler-bindings.md | Compiler Bindings | 2026-08-28 | 2026-08-28 |  |  | DRAFT/OPEN | "idea sketch, unscheduled" |
| composite-spanning-split.md | A composite holding a spanning element breaks | 2026-08-28 | 2026-08-28 |  |  | BUILT | implemented 2026-08-01 |
| const-eval.md | `const` — compile-time evaluation as a language feature | 2026-08-28 | 2026-09-14 | Status: **SHIPPED 2026-07-10** — the full v1, same-day as the proposal. | ?B35 ?M4 | BUILT | SHIPPED 2026-07-10 |
| contexts.md | Declared context requirements (tracker B242) | 2026-09-05 | 2026-09-17 | Status: **SHIPPED 2026-09-05** (Order 28, lane context-28) — the design | CB229 CB241 CB242 | BUILT | SHIPPED 2026-09-05 |
| contextual-keywords.md | Contextual keywords — which reserved words a name may use, and where ( | 2026-09-25 | 2026-09-25 |  | CB413 CB414 CB415 CE142 CM86 CN113 CN63 | BUILT | no status; B414 CLOSED (Order 46) |
| css-block.md | A first-class `css { … }` block — the element syntax's twin on the sty | 2026-08-28 | 2026-09-17 | > Status: **THE ARC IS COMPLETE — S1–S5 SHIPPED.** S1 and S2 on 2026-08-28 in |  | BUILT | arc COMPLETE S1-S5 |
| db-migrations.md | Database migrations — an ordered, recorded schema history (kolt.local  | 2026-08-29 | 2026-08-29 | > Status: PROPOSED 2026-08-29 (cycle 38, work order 20, lane |  | UNKNOWN | PROPOSED 2026-08-29; no tracker id in head; whether std::db migrations were built not determined |
| dead-code-paint.md | Dead-code paint for top-level items (E124) | 2026-09-03 | 2026-09-03 |  | CE114 CE124 | BUILT | PAPER 2026-09-03; E124 CLOSED (built Order 27) |
| debugging.md | Debugging vilan programs — `dbg`, `dbg_stack`, and a breakpoint debugg | 2026-10-08 | 2026-10-26 |  | OE257 CF68 CF87 | IN PROGRESS | header "PAPER drafted 2026-10-03" but has "As built" sections; E257 open |
| deferred-row-build.md | The deferred row build — `each` stops building rows its own drain cuts | 2026-09-28 | 2026-09-28 |  | CA112 CA129 OA131 CA91 CA98 CI5 | DRAFT/OPEN | paper for A131 (open); no status line |
| deprecation.md | Deprecation — the machinery for the one-minor window (L4) | 2026-08-28 | 2026-09-29 | > Status: PROPOSED 2026-08-20 (cycle 25, work order 7); RULED 2026-08-22 | ?L4 | BUILT | RULED 2026-08-22; L4 shipped (v0.3x) |
| design-language.md | The design language — one visual system for site, playground, and docs | 2026-08-28 | 2026-08-28 | > Status: **RATIFIED 2026-08-18 as recommended** ("Go with the | ?K1 ?K10 CK15 ?K4 OK5 ?K6 ?K9 | IN PROGRESS | RATIFIED 2026-08-18; K5 open (slices 1-2 shipped) |
| destruction-impl-plan.md | C4 implementation plan — deterministic destruction, to completion | 2026-08-28 | 2026-08-28 | > **Status: COMPLETE 2026-07-19 — all five slices shipped; the ledger is in | CC1 ?C4 | BUILT | COMPLETE 2026-07-19 |
| destruction.md | Deterministic destruction — the owned-resource class (backlog C4) | 2026-08-28 | 2026-09-01 | > **Status: SHIPPED 2026-07-19 — Tier 1 complete, S1–S5.** The ledger: 5ae93f3 (surface) | ?B29 CC1 OC2 ?C4 ?C6 ?C7 ?C8 ?C9 ?F3 ?F4 OJ4 | BUILT | SHIPPED 2026-07-19 (Tier 1) |
| dev-refresh.md | Dev-time freshness — data a running server serves (backlog E55, genera | 2026-08-28 | 2026-08-28 | > **Status: RULED 2026-08-11 — §3's recommendation is DECLINED; §5 records the | ?E55 | BUILT | RULED 2026-08-11 (declined §3 rec; E55 retired) |
| devirtualize-single-impl-dyn.md | Devirtualizing a single-implementor `dyn Trait` — measured first (M88) | 2026-09-28 | 2026-09-28 |  | CA124 CB398 ?B4 CB412 CB430 CB431 OM88 | DRAFT/OPEN | M88 open; "a rec, not a ruling" |
| diagnostics-ledger.md | The diagnostics ledger (diagnostics-standard.md §5) | 2026-08-28 | 2026-11-13 |  | ?A13 ?B29 ?C3 ?C4 ?E76 | IN PROGRESS | generated living ledger; touched 2026-11-13 |
| diagnostics-standard.md | The diagnostics standard — rules, then an audit | 2026-08-28 | 2026-09-21 | Status: **ACCEPTED 2026-07-16** — all four open questions signed off by the | ?A1 ?A2 ?A3 ?B13 ?E7 ?E8 ?H6 | IN PROGRESS | ACCEPTED 2026-07-16; audit ongoing via ledger |
| dial-cancel.md | A dial that can be cancelled, and a dial with a deadline (A179) | 2026-11-02 | 2026-11-02 | - status: BUILT 2026-11-02 (lane std-56 fdb52613 + 73a10909 + 37688072; merged to next 79a620f9; rides v0.54.0 | CA179 CA47 CA52 | BUILT | BUILT 2026-11-02 |
| distribution.md | Distribution — npm, marketplace, brew (F7) + the project-model deferra | 2026-08-28 | 2026-08-28 | > **Status: RATIFIED 2026-07-25 — calls (a)–(f) all per recommendation** | ?B33 ?F5 ?F7 ?F8 ?F9 | BUILT | RATIFIED 2026-07-25; F7 shipped (npm/brew/vsix) |
| docs-audit-2026-08-18.md | Docs currency audit against v0.34.0 — the record (backlog D15) | 2026-08-28 | 2026-08-28 | STATUS: SHIPPED 2026-08-18 | CD15 | BUILT | SHIPPED 2026-08-18; a dated record against v0.34.0 |
| docs-port.md | The docs port — the book, the brand, and the run button (K6) | 2026-08-28 | 2026-08-28 | > Status: **RATIFIED 2026-08-19 as recommended** ("Recommendations in | ?K11 OK13 OK5 ?K6 ?K7 ?N14 | IN PROGRESS | RATIFIED 2026-08-19; K13 open (steps 1+ shipped) |
| docs-site.md | The rendered docs site (D1 polish, item 5) | 2026-08-28 | 2026-08-28 |  | ?D1 | UNKNOWN | no status; D1 polish note |
| documentation.md | Documentation (D1a) — the user-facing reference | 2026-08-28 | 2026-08-28 |  | ?D1 | UNKNOWN | no status; D1a |
| draft-reconnect.md | `Draft` on reconnect — auto re-push, and a debounced commit (A14) | 2026-08-28 | 2026-08-28 |  | ?A12 OA14 ?A6 ?K6 | BUILT | proposed 2026-08-04 "implemented in the same arc" |
| e63-drafts | (dir) | 2026-08-28 | 2026-08-28 |  |  | UNKNOWN | dir: kolt-server.patch, todo-app.patch (2026-08 drafts) |
| editing-dx.md | In-progress-change diagnostics — the DX survey (E49) | 2026-08-28 | 2026-09-17 | > Status: RATIFIED 2026-08-11 ("The recommendations for editing-dx.md … look | ?E49 | BUILT | RATIFIED 2026-08-11; E49 retired |
| editor-latency.md | Editor latency — the two paths (E121) | 2026-09-01 | 2026-09-08 |  | ?B38 OE121 | IN PROGRESS | PAPER 2026-09-01; E121 open |
| element-clones.md | Stores and returns copy — closing A20 and B54 | 2026-08-28 | 2026-08-28 | > **Status: SHIPPED 2026-08-04** (backlog A20 and B54, one slice). B53 | ?A20 ?B53 ?B54 | BUILT | SHIPPED 2026-08-04 |
| element-syntax.md | Element syntax — markup as sugar over the `view` chain | 2026-08-28 | 2026-08-28 | Status: **ALL FIVE SLICES SHIPPED 2026-08-01 — the arc is complete** (branch `element-syntax`; §10 carries eac | ?H8 | BUILT | ALL FIVE SLICES SHIPPED 2026-08-01 |
| expression-lifting.md | Expression lifting — `a? + 10` and `a? + b?` (B11 deferred tail) | 2026-08-28 | 2026-08-28 | Status: **v1 SHIPPED 2026-07-16** (same day: accepted after the five review | OB11 ?B28 | IN PROGRESS | v1 SHIPPED 2026-07-16; B11 tail open |
| filesystem.md | A formalized filesystem — handles, atomicity, directories, watch (kolt | 2026-08-28 | 2026-08-31 | > Status: PROPOSED 2026-08-26 (cycle 31, work order 13, lane |  | BUILT | header PROPOSED 2026-08-26; built in Order 17 (chronicle), fs::Watcher exists |
| fixed-arrays.md | `[T; n]` — fixed-length arrays (backlog I2) | 2026-08-28 | 2026-08-28 |  | ?F3 ?F4 OI2 | IN PROGRESS | no status; array-lengths built; I2 tail open |
| fn-coercion.md | Named functions as closure values (backlog B20) | 2026-08-28 | 2026-09-14 | Status: **SHIPPED 2026-07-11**. Found building A10: `current_path().map(parse)` | ?A10 ?B18 ?B20 CB340 ?J2 | BUILT | SHIPPED 2026-07-11 |
| focus-scope.md | Focus scopes — a tabbable query, a trap, and a restore (A121) | 2026-09-21 | 2026-09-21 | Related: A45 (`View::on_mount` / `View::autofocus` / `Element::focus`, CLOSED | CA121 CA45 CA59 CA96 CB271 | BUILT | A121 CLOSED |
| frontend.md | The handwritten frontend — replacing chumsky (H6) | 2026-08-28 | 2026-08-28 | > **Status: SHIPPED 2026-07-22 — the arc is complete, chumsky is deleted.** | ?H6 | BUILT | SHIPPED 2026-07-22 |
| fullstack-dx.md | Full-stack setup — the document, the assets, a server that grows (E56) | 2026-08-28 | 2026-08-28 | > Status: RATIFIED 2026-08-11 as recommended ("The recommendations for … | ?E49 ?E56 | BUILT | RATIFIED 2026-08-11 |
| generic-left-operand-census.md | The generic left operand — the estate census behind B174's breaking st | 2026-09-01 | 2026-09-01 |  | CB169 CB174 CB179 | BUILT | CENSUS 2026-09-01; B174 CLOSED |
| gfx-path-images | (dir) | 2026-11-12 | 2026-11-13 |  |  | BUILT | dir: images for gfx-path.md (built) |
| gfx-path.md | Paths and icons in `std::gfx` and `std::ui` (native-ui.md part P5) | 2026-11-12 | 2026-11-13 | Status: RULED 2026-11-12. The owner accepted all thirteen recommendations of section 9 ("Accept all recs"); th | OF175 | BUILT | RULED 2026-11-12; F175 S1-S4 landed 2026-11-13 (tracker F175 still "open") |
| hash-map-lend.md | A `HashMap` read or written in place: `peek`, `modify`, `update` — and | 2026-10-31 | 2026-11-03 | - status: BUILT 2026-10-31 (lane b689, commit aae8ae6e, merged into next 26257f20; rides v0.54.0) - designed t | CB689 CM182 | BUILT | BUILT 2026-10-31 |
| hashable-keys.md | Hashable keys for `Map` / `Set` (backlog I1) | 2026-08-28 | 2026-08-28 | Status: **PROPOSED 2026-07-14**. | ?I1 | BUILT | header PROPOSED 2026-07-14; Hashable exists (42 changelog mentions) |
| hmr.md | Hot module replacement — closing the dev loop (A13) | 2026-08-28 | 2026-09-17 | > **Status: RATIFIED 2026-07-20 — implementation underway (S0 first).** The §10 | ?A13 OA7 ?F5 ?F7 | BUILT | RATIFIED 2026-07-20; A13 retired, HMR shipped; A96 follow-up |
| image.md | `std::image` — decode, resize, crop and encode pictures on both backen | 2026-11-02 | 2026-11-02 | - status: BUILT 2026-11-02 (lane m185 @92c6cfff; merged to next 8e8c463c; rides v0.54.0; M185 closed; owner Q1 | CF19 CM185 CN134 | BUILT | BUILT 2026-11-02; Q6-Q7 open |
| import-foundation.md | The import foundation — root values, projections, and `use` (A183) | 2026-11-02 | 2026-11-02 |  | CA181 CA182 OA183 ?B57 CB688 CE359 | IN PROGRESS | PAPER, ruled in principle 2026-11-03; A181/A182 built, A183 open |
| incremental-analysis.md | Incremental analysis — why an edit re-analyses the whole entry, and th | 2026-10-08 | 2026-10-08 |  | CM104 OM110 OM19 OM73 OM79 OM99 | IN PROGRESS | PAPER 2026-10-03; M110 arc ongoing |
| incremental-collections.md | Incremental collections — a change structure for `std::reactive` (A112 | 2026-09-21 | 2026-09-25 | Related: A54 (`KeyedCell`, CLOSED Order 31 — the machinery this lifts), A39 | CA110 OA111 CA112 CA39 CA54 CA98 CA99 CB359 | BUILT | A112 CLOSED; A111/A131 open follow-ons |
| index-type.md | One spelling for an index — `usize` (I5) | 2026-09-22 | 2026-09-25 | B370 (CLOSED Order 39 — literal inference as a general law, whose remaining | CA101 CA108 CA112 CB370 CI5 | BUILT | I5 CLOSED (usize everywhere) |
| inlay-hint-abbreviation.md | Inlay-hint abbreviation — a type shown by the trait it is used as (E22 | 2026-09-28 | 2026-09-28 |  | CA123 CA124 CB382 OE121 CE206 CE213 CE221 CE227 CI5 | BUILT | E227 CLOSED |
| iterator-adapters.md | Iterator adapters and the pipeline ergonomics (I3) | 2026-08-28 | 2026-08-28 | > Status: RATIFIED 2026-08-04 (owner review) — all recommendations stand, | ?B4 ?B55 ?B56 ?B57 ?B58 OI3 CI5 | IN PROGRESS | RATIFIED 2026-08-04; I3 remainder open |
| json-field-default.md | `[default(..)]` on a `[derive(Json)]` field (M174) | 2026-11-03 | 2026-11-03 |  | CA142 OI3 CM166 OM174 | DRAFT/OPEN | PAPER 2026-11-03, owner Qs open, not built; M174 open (rec: build) |
| keywords-vs-attributes.md | Keywords and attributes — which one a marker becomes, and the order th | 2026-10-01 | 2026-10-02 | > Status: **RULED 2026-10-01** — Q1–Q11 as recommended (the owner); the build is queued for Order 46. Drafted  | CB318 CB413 CB414 CB415 CB445 CB485 CE227 CF60 CG24 | BUILT | RULED 2026-10-01; B413-415 CLOSED |
| kolt-migration.md | Kolt → vilan — the migration driver | 2026-08-28 | 2026-08-28 |  |  | SUPERSEDED/STALE | "LIVING DOCUMENT 2026-07-11"; last touched 2026-08-28; the migration moved on |
| lazy.md | `lazy` — defer to first demand | 2026-08-28 | 2026-09-17 | > **Status: RATIFIED 2026-07-21.** The §6 calls (user): **(a) poison** — a | ?A13 ?F5 ?F7 | BUILT | RATIFIED 2026-07-21; lazy shipped (A100 etc.) |
| leak-soak.md | The leak soak — looking thoroughly for what does not plateau (M2) | 2026-08-28 | 2026-08-28 | > **Status: SHIPPED 2026-08-18.** Two instruments. Tier 1 is | ?M2 ?M7 | BUILT | SHIPPED 2026-08-18 |
| length.md | Lengths as data — A178 | 2026-10-31 | 2026-10-31 | - status: BUILT 2026-10-31 - S1 + S2 landed on next (lane std-a178 @5d984949, merged 7911d954; rides v0.54.0); | OA106 CA178 OA8 CB340 | BUILT | BUILT 2026-10-31 (S3 codemod is kolt's) |
| library-packages.md | Library packages (replaces roadmap P4) | 2026-08-28 | 2026-08-28 |  | ?L1 ?L2 OL3 | IN PROGRESS | L1+L2 implemented; L3 sketched, L3 open |
| lifetimes.md | The lifetime model — one liveness notion, two backends, and a measured | 2026-08-28 | 2026-09-17 | > Status: **S1, S2, S3 AND S4 SHIPPED 2026-08-29** (cycle 37, order 19; | CA28 CA30 | BUILT | S1-S4 SHIPPED 2026-08-29 |
| local-shadowing.md | Local shadowing — positional visibility for local bindings (B34) | 2026-08-28 | 2026-08-28 | > **Status: IMPLEMENTED 2026-07-28.** The shadowing semantics are the user's | ?B33 ?B34 | BUILT | IMPLEMENTED 2026-07-28 |
| lsp-snapshot-consistency.md | LSP snapshot consistency | 2026-08-28 | 2026-08-28 |  | ?H6 | BUILT | approved for implementation 2026-07-28 (no shipped line) |
| macro-engine.md | The macro engine (roadmap #9) | 2026-08-28 | 2026-08-28 | Status: **COMPLETE — every scheduled phase SHIPPED as of 2026-07-07.** Phases |  | BUILT | COMPLETE 2026-07-07 |
| macros-post-parse.md | Macros: the normalized `macro_std` contract | 2026-08-28 | 2026-08-28 | Status: **DESIGN COMPLETE, DEFERRED ENTIRELY (2026-07-16).** The user |  | RULED NOT BUILT | DESIGN COMPLETE, DEFERRED ENTIRELY 2026-07-16 (parked) |
| markdown.md | The markdown story — std::markdown, the anchor pin, and the docs-port  | 2026-08-28 | 2026-08-28 | > Status: DRAFT 2026-08-24 (cycle 28, work order 10, lane | OK13 | IN PROGRESS | header DRAFT 2026-08-24; step 1 shipped, K13 open |
| memory-management-impl-plan.md | Memory Management — Implementation Plan | 2026-08-28 | 2026-08-28 |  |  | BUILT | phases 1-5 complete; tail in C-items |
| memory-management-rev-1.md | memory-management-rev-1.md — moved (N15) | 2026-08-28 | 2026-08-28 |  | ?N15 | SUPERSEDED/STALE | stub (marked moved/superseded) |
| memory-management.md | memory-management.md — moved (N15) | 2026-08-28 | 2026-08-28 |  | ?N15 | SUPERSEDED/STALE | stub (marked moved) |
| method-resolution.md | Method resolution — a deliberate precedence rule (B57) | 2026-08-28 | 2026-08-28 | > Prior status: RATIFIED 2026-08-04 (owner review) — implement as recommended: | ?B127 ?B57 ?B73 | BUILT | RATIFIED 2026-08-04; B57 retired |
| mirrored-store.md | The mirrored `Store` — a server's `Store<T>` mirrored by the client, o | 2026-10-08 | 2026-10-08 | > Status: **DRAFT 2026-10-03 — for the owner's ruling** (R-d: a paper this order, nothing | CA134 CA137 CA142 CA144 CA146 CA149 CA150 CA152 CA153 CA39 CA54 CA79 C | BUILT | header DRAFT 2026-10-03; A153 (mirrored Store) CLOSED |
| mut-parameters.md | `mut` parameters | 2026-08-28 | 2026-08-28 | Status: SHIPPED 2026-08-03 (backlog H9; tester report). Semantics settled | ?H9 | BUILT | SHIPPED 2026-08-03 |
| named-tuple-fields.md | Named tuple fields — labels for a tuple's positions, with no declarati | 2026-10-09 | 2026-10-09 | > Status: **DRAFT 2026-10-08 — for the owner's ruling.** Written by lane papers-b-48 of | CA122 OB183 CB309 CB414 CB495 CB525 CB569 CB570 CB571 | BUILT | header DRAFT 2026-10-08; B569 CLOSED 2026-10-10 |
| native-apps-probe | (dir) | 2026-09-14 | 2026-09-14 |  |  | IN PROGRESS | dir: the F1 probe code (Order 36-37), F1 open |
| native-apps.md | Native apps — an emit-Rust backend, a desktop platform, and a third `s | 2026-09-14 | 2026-09-24 | Tracker **F1** (filed 2026-09-14 as a DISCUSSION with owner questions; RULED to a paper at | CA95 CC1 CC12 CC14 OF1 | IN PROGRESS | F1 open; S1a built (v0.4x), F1 S1b pending |
| native-objective.md | The native objective: a Rust web server, then a Rust desktop app | 2026-11-09 | 2026-11-10 | Status: RULED 2026-11-09 - the owner accepted every recommendation in §3 (S1-S7, D1-D8) as a ruling. §5 (Kolt) | ?D1 CD8 OF1 OF15 CF152 OF17 OF27 ?M1 | IN PROGRESS | RULED 2026-11-09 (S1-S7, D1-D8); work continues |
| native-ui.md | Native UI: a graphics API, a UI framework on it, and components on tha | 2026-11-10 | 2026-11-10 | Status: RULED 2026-11-10. The owner accepted every recommendation in section 9 |  | IN PROGRESS | RULED 2026-11-10; parts built in v0.56.0, more remain |
| numeric-types.md | Sized numeric types (backlog F2, roadmap #15) | 2026-08-28 | 2026-08-28 | Status: **SHIPPED 2026-07-07.** Adds the sized | ?F2 ?F3 ?F4 | BUILT | SHIPPED 2026-07-07 |
| opaque-returns.md | Opaque returns — what `fun f(): Trait` should hide (B460's opacity) | 2026-10-01 | 2026-10-01 | > Status: **RULED 2026-10-01** — Q1–Q11 as recommended (the owner); the build is queued for Order 46. Drafted  | CA142 CB161 CB184 CB186 CB253 ?B4 CB460 CB461 CB473 CB474 CB475 CE227  | BUILT | RULED 2026-10-01; B460 CLOSED |
| optimistic-lifecycle.md | The optimistic-write → reconcile lifecycle (A14) | 2026-08-28 | 2026-08-28 | header reads **SHIPPED**, declaring "**A6 is COMPLETE**". Reopening a | OA14 ?A6 | IN PROGRESS | header SHIPPED but reopened (A14 open, owner Q9) |
| org-migration.md | Org migration — `ReedSyllas/vilan` → `vilan-lang/vilan` (F9) | 2026-08-28 | 2026-08-28 | > **Status: MIGRATION COMPLETE — all slices done** (markers added 2026-07-29; | ?F9 | BUILT | MIGRATION COMPLETE |
| p6-followups.md | P6 follow-ups — the post-completion ladder (2026-07-02) | 2026-08-28 | 2026-09-08 | > **Status (2026-07-03): the ladder is COMPLETE — all five items ✅, and the "Final |  | BUILT | ladder COMPLETE 2026-07-03 |
| payload-views.md | Payload views — a pattern that binds a writable view into an enum payl | 2026-10-08 | 2026-10-08 | > Status: **DRAFT 2026-10-03 — for the owner's ruling** (R-k carried B509's ruling to Order 47. | CA149 CB509 | BUILT | header DRAFT 2026-10-03; B509 CLOSED 2026-10-04 |
| per-module-analysis-reuse.md | Per-module analysis reuse — M19 tranche 2 (E121's diagnostics path) | 2026-09-03 | 2026-09-03 |  | OE121 OM19 CM21 CM22 CN43 | IN PROGRESS | PAPER 2026-09-03; M19 open |
| percent-encoding.md | `std::url`: percent-encoding on both backends (M181) | 2026-11-02 | 2026-11-02 | - status: BUILT 2026-11-02 (lane std-56 a5df8059; merged to next 79a620f9; rides v0.54.0; M181 closed; Q1 buil | ?G1 CM181 | BUILT | BUILT 2026-11-02 |
| perf-baseline.jsonl | (file) | 2026-08-28 | 2026-08-29 |  |  | SUPERSEDED/STALE | baseline data from 2026-08-29; later series replaced it (budgets.toml/ceilings) |
| perf-baseline.md | The performance baseline — the harness, and the first numbers (M1) | 2026-08-28 | 2026-08-29 | > **Status: SHIPPED 2026-08-18.** The harness is | ?M1 | SUPERSEDED/STALE | SHIPPED 2026-08-18; numbers are July/Aug, harness since replaced |
| performance-gates.md | Performance gates — what fails a build for being slow (M105) | 2026-10-02 | 2026-10-02 | > Status: **RULED 2026-10-02** — Q1–Q12 as recommended (the owner); the build (S1–S8) is Order 46's, the seal- | OE121 CE236 CM100 OM101 CM103 CM104 CM105 OM99 | BUILT | RULED 2026-10-02; M105 CLOSED (built Order 46) |
| platform-coloring.md | Platform coloring — function-granular platform checking | 2026-08-28 | 2026-09-24 |  | OF27 ?L1 ?L2 | IN PROGRESS | "proposed" 2026-09-24; [platform] function-granular exists; F27 open |
| platform-model.md | Build model: backends, platforms, and layers | 2026-08-28 | 2026-08-28 |  | ?L1 ?L2 OL3 | BUILT | implemented 2026-06-23 |
| playground-completion.md | Playground completion — the completion core's seam for wasm (K9) | 2026-08-28 | 2026-08-28 | > Status: DESIGNED AND BUILT 2026-08-22 (lane k9-playground-completion, | ?E52 ?E57 ?K9 | BUILT | DESIGNED AND BUILT 2026-08-22 |
| positional-slots.md | Positional slots — `when`, `swap` and `each` as `Slot` VALUES | 2026-09-11 | 2026-09-14 |  | CA42 CA46 CA71 CA85 CB253 CB268 | BUILT | A85 CLOSED; "As built" sections |
| prelude.md | The prelude — a manifest-configurable ambient scope (B156) | 2026-08-31 | 2026-09-14 |  | CB156 | BUILT | AMENDED 2026-08-31; B156 CLOSED |
| process.md | Process — releasing, protecting, and taking contributions | 2026-08-28 | 2026-08-28 | > Status: RATIFIED 2026-08-07 (owner review) — as drafted, with two | OD5 | BUILT | RATIFIED 2026-08-07 (release process; rule text still current in main) |
| proposals-repo.md | The proposals move to their own repo (N15) | 2026-08-28 | 2026-08-28 | Status: PROPOSED 2026-08-20 (backlog N15; absorbs N2's archive-consolidation | ?N15 ?N2 | BUILT | header PROPOSED 2026-08-20; N15 executed (repo exists) |
| r11-instantiations.md | R11's instantiations on a served keystroke — the largest remaining che | 2026-10-16 | 2026-10-16 | > Status: **DRAFT 2026-10-16 — for the owner's ruling (Q1–Q4).** Written by lane incr-53c of | CB344 CB463 CB469 OC2 OM110 CM149 OM19 CM94 | BUILT | header DRAFT 2026-10-16; door B built Order 54 (v0.52.0) |
| reactive-batching.md | Reactive batching — deferred notification & the `batch` turn | 2026-08-28 | 2026-09-30 |  | ?J2 | BUILT | implemented as designed 2026-07-02 |
| reactive-layers.md | Reactive layers — sources and move-only pipes, tracked reads as sugar, | 2026-09-29 | 2026-09-30 | > Status: **RATIFIED DESIGN, unbuilt** (2026-09-29, revision 2). The owner ruled | CA124 CA142 CB458 CB462 CB463 | BUILT | header "RATIFIED DESIGN, unbuilt"; A142 CLOSED, layers shipped |
| reactive-lens-lab | (dir) | 2026-11-05 | 2026-11-06 |  |  | IN PROGRESS | dir: lens lab (A185); S1-S3,S5 landed |
| reactive-lens-probe | (dir) | 2026-11-05 | 2026-11-05 |  |  | IN PROGRESS | dir: lens probe (A185) |
| reactive-lens.md | Reactive lens: one reactive wrapper for any structure, with the shape  | 2026-11-05 | 2026-11-09 | **RATIFIED rev 2.2 (recommendations accepted as rulings 2026-11-08; see §10a). S1 LANDED on `next` @09100b52 ( | CA112 OA138 CA142 OA185 OB711 OB712 OB715 ?L7 OL8 | IN PROGRESS | RATIFIED rev 2.2; S1,S2,S3,S5 landed; S3b parked, S4 waits B711, S6/S7 open |
| reactive-maps-sets.md | Reactive maps and sets — the Map and Set shapes, and the order a hash  | 2026-09-29 | 2026-10-01 | > Status: **RULED 2026-10-01** — Q1–Q7 and Q9 (Q8 on 2026-09-29) as recommended (the owner, at Order 45's GO); | CA112 OA138 CA142 CA39 CA54 CA79 ?I1 OI10 CI8 CI9 | IN PROGRESS | RULED 2026-10-01; S0-S2 built; A138/I10 rows still open |
| reactive-pipeline.md | Reactive pipeline — every combinator is a cold node, `get()` pulls, a  | 2026-09-22 | 2026-09-30 | > Status: **DRAFT** (awaiting owner review). R1–R5 were RULED by the owner on | CA123 CA124 | BUILT | header DRAFT awaiting owner review; A123/A124 CLOSED, built |
| reactive-traits.md | Reactive traits — `Source` reads, `Signal` writes, `SignalCell` stores | 2026-08-31 | 2026-08-31 | > **Status: PROPOSED 2026-08-31** (work order 22, cycle 40; tracker items | CA32 CA33 CB157 CB158 CB161 CB162 | BUILT | header PROPOSED 2026-08-31; A32/A33 CLOSED, traits exist |
| reactive-turns.md | Reactive turns — flush is scoped, not global (A6 redesigned) | 2026-08-28 | 2026-09-22 | Status: **SHIPPED 2026-07-09** — `get_safe` (§5.1), the Turn machinery + | OA14 ?A6 ?J2 | BUILT | SHIPPED 2026-07-09 |
| releases.md | Releases — installation and updates | 2026-08-28 | 2026-09-27 |  |  | BUILT | living release-process doc; touched 2026-09-27; no status line |
| remote-sources.md | Remote sources — subscribe by demand, unsubscribe at zero (A25) | 2026-08-28 | 2026-09-29 | > Status: **BUILT 2026-08-19** on lane `a25-remote-sources` — all three | ?A25 | BUILT | BUILT 2026-08-19 |
| requirement-polymorphism.md | Requirement polymorphism — the coverage fence follows instantiation ch | 2026-08-28 | 2026-08-28 | Status: **BOTH SLICES SHIPPED 2026-08-02** (backlog B51) — the recorded | ?B51 ?H8 | BUILT | BOTH SLICES SHIPPED 2026-08-02 |
| ret-checking.md | Return-position type checking (backlog B10) | 2026-08-28 | 2026-08-28 |  | ?B10 ?B126 ?B133 | BUILT | implemented 2026-07-04, amended 08-22/08-24 |
| roadmap.md | roadmap.md — moved (N15) | 2026-08-28 | 2026-08-28 |  | ?N15 | SUPERSEDED/STALE | stub "moved (N15)", superseded (marked) |
| router.md | `std::router` — history-API routing (backlog A10) | 2026-08-28 | 2026-08-31 |  | ?A10 | BUILT | SETTLED 2026-07-11; std::router exists; A72 open tail |
| rpc-revoke.md | Revoke by value: one connection's mirror of one store (A175, A174 door | 2026-11-03 | 2026-11-03 |  | CA120 CA153 CA174 OA175 | DRAFT/OPEN | PAPER 2026-11-03, owner Qs open, not built; A175 open |
| rule4-completion.md | Rule-4 completion — the `borrows` root-set and the `bumps` effect (C10 | 2026-08-28 | 2026-08-28 | > **Status: COMPLETE 2026-07-19 — all four slices shipped same day.** 144d44e (S1 | ?A13 ?C10 ?C6 ?E2 | BUILT | COMPLETE 2026-07-19 |
| signal-cell-representation.md | The signal cell's representation — `Shared` boxes, counted handles, or | 2026-09-14 | 2026-09-25 | Tracker **C14** (filed 2026-09-14; RULED to a paper at Order 36's GO). Written by lane | OA87 CA92 CC1 CC14 OF1 CM60 CM66 | BUILT | C14 CLOSED (S1-S3 Order 37) |
| signal-update.md | `Signal::update` — mutate the stored value in place (A18) | 2026-08-28 | 2026-08-28 | > **Status: IMPLEMENTED 2026-08-03.** The design is the project owner's call | ?A18 | BUILT | IMPLEMENTED 2026-08-03 |
| signature-layout.md | Signature layout — the width rule reaches a declaration | 2026-08-28 | 2026-08-28 |  |  | BUILT | implemented 2026-08-01 |
| specification.md | The language specification (D1b) | 2026-08-28 | 2026-08-28 |  |  | BUILT | no status; spec lives in vilan/docs/spec (exists) |
| split-comment-attachment.md | Comment attachment inside split constructs | 2026-08-28 | 2026-08-28 |  | ?E13 | BUILT | implemented 2026-08-01 |
| sql-value.md | `SqlValue`: typing `std::db`'s bind lists (M175) | 2026-11-03 | 2026-11-03 |  | OA176 OB679 OF150 CM165 CM175 | BUILT | header "not built, owner questions open"; M175 CLOSED 2026-11-16 (v0.56.0) |
| ssr.md | Server-side rendering — render and replace (A7) | 2026-08-28 | 2026-08-28 | > **Status: v1 SHIPPED 2026-07-23 — arc complete for S1 + S2** (S1 the | ?A21 OA7 CD7 | IN PROGRESS | v1 SHIPPED 2026-07-23; A7 tail open |
| std-prefix.md | The std prefix — std analyzed once per toolchain build and loaded by e | 2026-10-10 | 2026-10-26 | > Status: **DRAFT 2026-10-10 — for the owner's ruling (Q1–Q12).** Written by lane papers-50 of | CB422 CB553 OE121 OE292 OM110 OM120 CM121 CM134 OM19 CM24 CM33 OM36 CM | IN PROGRESS | header DRAFT 2026-10-10 (Q1-Q12); P1-P6 largely built (v0.51-v0.53); M120/M36 open |
| std-shape.md | std vs official packages — the distribution shape (L10) | 2026-08-28 | 2026-08-28 | > Status: PROPOSED 2026-08-20 (cycle 26, work order 8, lane | ?L10 ?L4 | IN PROGRESS | header PROPOSED 2026-08-20; partly RULED (split on hold 2026-08-28) |
| std-surface.md | The std surface audit — the ranked gap list (I4) | 2026-08-28 | 2026-08-28 | > **Status: v1 SHIPPED, 2026-08-03** (audit drafted 2026-08-03; user | CI4 | BUILT | v1 SHIPPED 2026-08-03 |
| store-assume-keeper.md | The assumed handle's fallback, kept at the variant's end — not copied  | 2026-11-02 | 2026-11-02 | - status: BUILT 2026-11-02 (lane b693 @6d8b902e, merged to next 2f89bee9; rides v0.54.0; B693 closed; owner Q1 | CA149 CB526 CB689 CB693 | BUILT | BUILT 2026-11-02; owner Q1-Q2 open |
| store-path-sharing.md | A store handle's path is shared, not copied (M186) | 2026-11-02 | 2026-11-02 | - status: BUILT 2026-11-03 (lane m186 25e305fc + 0221febf; merged to next; rides v0.54.0; M186 closed; Q1 expo | CA142 CB689 CB693 CM186 | BUILT | BUILT 2026-11-03 |
| store.md | `Store` — the fine-grained version of a type, generated from its shape | 2026-09-29 | 2026-10-01 | > Status: **RULED 2026-10-01** — Q1–Q12 as recommended (the owner, at Order 45's GO); the build is Order 45's. | CA112 CA119 OA138 CA142 CB158 CB460 OF1 ?I1 OI10 | BUILT | RULED 2026-10-01; A142 CLOSED (built Order 45) |
| struct-keys.md | Struct keys: `S.x`, typed paths into a struct | 2026-11-05 | 2026-11-05 |  | CA144 CB569 OB711 | DRAFT/OPEN | filed by kolt 2026-11-05; B711 open (PROPOSED); lens S4 waits on it |
| style-conditions.md | `Style`'s condition model — conditions as values (A95) | 2026-09-13 | 2026-09-14 | vilan `e4d192e3`). A95 was RULED to the paper at the Order 34 GO (R2): the | CA36 CA89 CA93 CA95 CB311 | BUILT | A95 CLOSED |
| style-variants.md | Style variants — the base+delta recipe | 2026-08-31 | 2026-08-31 | (kolt.local 015). **§8 Q3 RULED ACCEPTED 2026-08-31**: `Style::when` | CA36 | BUILT | A36 CLOSED; Q3 accepted |
| suite-speed.md | Suite speed — the measured profile (E21) | 2026-08-28 | 2026-08-28 | > **Status: AUDIT DONE 2026-08-02; E26 measured and CLOSED NEGATIVE the same | ?E21 ?E25 ?E26 ?E29 ?E30 | BUILT | AUDIT DONE 2026-08-02 |
| temporary-drop.md | When a resource temporary dies — statement-end, and why (backlog C11) | 2026-08-28 | 2026-08-29 | > Status: **CLOSED — SHIPPED 2026-08-29** (cycle 37, order 19, lane | CC11 | BUILT | CLOSED - SHIPPED 2026-08-29 |
| terminal.md | Terminal input — `scan()` made real, and a key stream for key-driven p | 2026-10-16 | 2026-11-03 | > Status: **DRAFT 2026-10-16 — for the owner's ruling (Q1–Q4, plus Q5 and Q6 that the ground | OA173 | IN PROGRESS | header DRAFT 2026-10-16; A173 S1/S2 shipped v0.52-0.53, S3 open |
| top-level-await.md | Top-level await — the design half (J3) | 2026-08-28 | 2026-08-28 | > Status: RATIFIED 2026-08-07 (owner review) — §8.2: the null | ?B86 ?B87 ?J3 CJ6 | BUILT | RATIFIED 2026-08-07; J3 retired |
| tracker-migration.md | The tracker migrates to the per-item format (N17) | 2026-08-28 | 2026-08-28 | Status: PROPOSED 2026-08-28 (backlog N17). N17 itself was RULED 2026-08-28: | ?N15 CN17 | BUILT | header PROPOSED 2026-08-28; N17 CLOSED same day (executed) |
| trait-objects.md | Trait objects — one representation, two meanings (B4) | 2026-08-28 | 2026-09-04 | > Status: RATIFIED 2026-08-07 (owner review) — Q1 answered: trait | ?B29 ?B4 ?B57 ?B72 | IN PROGRESS | RATIFIED 2026-08-07; B4 tail (devirtualize M88 open) |
| trait-typed-fields.md | A trait annotation on a struct field (B184) | 2026-09-01 | 2026-09-03 |  | CB161 CB184 CB186 | BUILT | header REVISION 2 DISCUSSION REQUIRED; B184 CLOSED |
| transparent-references.md | Transparent references — implicit place, explicit value | 2026-08-28 | 2026-08-28 |  | ?A1 | BUILT | implemented 2026-06-21 |
| transport-robustness.md | Transport robustness — reconnect, backoff, re-subscription (K6) | 2026-08-28 | 2026-08-28 | Status: **SHIPPED 2026-07-11** (same day). Findings while landing it: | ?B21 ?K6 | BUILT | SHIPPED 2026-07-11 |
| transport-rpc.md | Transport / RPC library (roadmap P6) | 2026-08-28 | 2026-09-21 |  |  | IN PROGRESS | no status line; largely built (BUILT/As built markers); A76/A81/A97 tails open |
| try-and-lift.md | `!` and `?` — early return and lifted chains (backlog B11) | 2026-08-28 | 2026-08-28 | Status: **BOTH SLICES SHIPPED 2026-07-04** — `!` and `?.` are live (`void` also became | OB11 | BUILT | BOTH SLICES SHIPPED 2026-07-04 |
| tuple-comprehension.md | The tuple comprehension — the suite question (B183, revision 2) | 2026-09-01 | 2026-09-03 | > **Status: PROPOSED 2026-09-03** (work order 26, lane b183-paper-2; | OB183 OB3 | IN PROGRESS | header PROPOSED 2026-09-03; zip form landed v0.42.0, concrete arm open (B183) |
| tuple-module.md | `std::tuple` — a tuple you can walk, keyed by position (A122) | 2026-09-24 | 2026-09-24 | > **Status: PROPOSED 2026-09-24** (work order 41, lane papers-41; tracker | CA122 CA124 OB183 CI5 | BUILT | header PROPOSED 2026-09-24; A122 CLOSED |
| type-ascription.md | Type ascription — `EXP as T`, a constraint and never a cast, and per-s | 2026-10-09 | 2026-10-09 | > Status: **DRAFT 2026-10-08 — for the owner's ruling.** Written by lane papers-b-48 of | CB161 CB248 CB259 CB414 CB495 CB539 CB569 CB570 CB571 CE227 CE261 CE27 | BUILT | header DRAFT 2026-10-08; B571 CLOSED 2026-10-10 |
| type-solver.md | Type solver — capability characterization (backlog B1) | 2026-08-28 | 2026-08-28 |  | ?B1 | BUILT | analysis complete, B1 closed |
| ui-styling.md | UI styling — typed atomic styles, compiled | 2026-08-28 | 2026-09-11 | Status: **CORE SHIPPED 2026-07-10; TAIL SHIPPED 2026-08-04, including the | OA7 OG2 | BUILT | CORE + TAIL SHIPPED; A8 tail row open |
| unit-literal.md | The unit literal (B363) — vilan has one, and it is spelled `void` | 2026-09-21 | 2026-09-21 | Related: A107 (the awaited `void` rpc return, CLOSED Order 38 — | CA107 CA120 CB363 CE208 | BUILT | B363 CLOSED |
| validating-from-json.md | Validating per-type `from_json` (backlog I3) | 2026-08-28 | 2026-08-28 | Status: **SHIPPED 2026-07-14**. Both `FromJson` methods return | OI3 | BUILT | SHIPPED 2026-07-14 |
| variadic-generics.md | Variadic generics via mapped tuples over flat storage | 2026-08-28 | 2026-08-28 |  |  | IN PROGRESS | implemented; keyof/elision deferred (B3 open) |
| view-invalidation.md | Views and invalidating events — rule 4 completed, `await` included (C3 | 2026-08-28 | 2026-08-28 | Status: **SHIPPED 2026-07-09** — both phases, same day (E2 commit + E3 | OC2 ?C3 ?E1 ?E2 ?E3 | BUILT | SHIPPED 2026-07-09 |
| visibility.md | Visibility and the import surface — default-private, the reach, and th | 2026-09-13 | 2026-09-17 | Tracker **B318** (the owner's design, filed 2026-09-12; RULED to the paper at Order 34's GO, | CB317 CB318 ?B4 ?B6 ?C3 CE168 CE169 | BUILT | B318 CLOSED |
| watch-mode.md | `--watch` mode (roadmap P5) | 2026-08-28 | 2026-08-28 |  |  | BUILT | implemented 2026-07-02 |
| web-playground.md | Web playground — the compiler in the visitor's browser (D11) | 2026-08-28 | 2026-08-28 | > **Status: LIVE AND COMPLETE — NOTHING REMAINS BY CHOICE (2026-08-02)** — | ?D10 ?D11 OD5 ?F9 | BUILT | LIVE AND COMPLETE 2026-08-02 |
| windows-support.md | Windows support — first-class native Windows for the toolchain | 2026-08-28 | 2026-08-28 | > **Status: RATIFIED 2026-07-24.** All §10 calls settled by the user: | ?F5 ?F7 ?H7 | BUILT | RATIFIED 2026-07-24; Windows legs in CI |

### Totals per class

| class | count |
|---|---|
| BUILT | 121 |
| IN PROGRESS | 35 |
| RULED NOT BUILT | 2 |
| DRAFT/OPEN | 8 |
| SUPERSEDED/STALE | 11 |
| UNKNOWN | 5 |
| total | 182 |

Of the 182 entries, 5 are directories (e63-drafts, gfx-path-images, native-apps-probe, reactive-lens-lab, reactive-lens-probe) and 1 is a data file (perf-baseline.jsonl). 7 are one-paragraph stubs marked "moved (N15)" (backlog x4, roadmap, memory-management x2); with README.md, kolt-migration.md, perf-baseline.md and perf-baseline.jsonl they make the SUPERSEDED/STALE class. RULED NOT BUILT holds only two papers (beta.md, macros-post-parse.md) because the ruled papers of Orders 44-58 have all been built at least in part (class IN PROGRESS) or fully (BUILT); papers that sit unbuilt are mostly DRAFT/OPEN with owner questions.

### The 15 papers most likely to mislead a reader today (stale, not marked)

1. `auto-annotations.md` - Header: "DRAFT 2026-10-08 — for the owner's ruling". B570 was CLOSED 2026-10-10 (Order 49) and the feature ships (`: auto T`); a reader would think it unbuilt.
2. `type-ascription.md` - Header "DRAFT 2026-10-08". B571 CLOSED 2026-10-10; `EXP as T` and its fmt layout (B571 S3) are in the changelog.
3. `named-tuple-fields.md` - Header "DRAFT 2026-10-08". B569 CLOSED 2026-10-10 (named tuple fields shipped, Order 49).
4. `payload-views.md` - Header "DRAFT 2026-10-03". B509 CLOSED 2026-10-04 (payload views built Order 46).
5. `mirrored-store.md` - Header "DRAFT 2026-10-03 — for the owner's ruling"; its own text says S3/S4 "being built this order". A153 (the mirrored Store) is CLOSED; a mirrored store is how kolt syncs today.
6. `r11-instantiations.md` - Header "DRAFT 2026-10-16 (Q1-Q4)". Door B was built in Order 54 (v0.52.0, "R11 door B"); the paper still reads as a pending ruling.
7. `std-prefix.md` - Header "DRAFT 2026-10-10 (Q1-Q12)". P1-P6 slices shipped across v0.50-v0.53 (the persisted std prefix is the default); only M120/M36 rows remain open.
8. `reactive-layers.md` - Header "RATIFIED DESIGN, unbuilt (2026-09-29)". A142 is CLOSED and the layers (Source / move-only pipes) are the live std::reactive; "unbuilt" is wrong since Orders 43-45.
9. `reactive-pipeline.md` - Header "DRAFT (awaiting owner review)". A123/A124 CLOSED; the cold-node pull pipeline is built.
10. `reactive-traits.md` - Header "PROPOSED 2026-08-31". A32/A33 CLOSED; Source/Signal/SignalCell traits are in std.
11. `sql-value.md` - Header "PAPER ... owner questions open; not built". M175 CLOSED 2026-11-16 and ships in v0.56.0 (`List<dyn SqlValue>`).
12. `terminal.md` - Header "DRAFT 2026-10-16 (Q1-Q4)". A173 S1 (`prompt`) and S2 (`process::keys()`) shipped in v0.52-v0.53; only S3 (line editor) is open. Its Q5/Q6 and "as built" paragraphs are the real state.
13. `build-hooks.md` - Header "DRAFT 2026-08-27". Ruled 2026-08-28 (Q1-Q7) and `[[build.hook]]` is built (G9/G10, 25 changelog mentions); chronicle calls it done.
14. `filesystem.md` - Header "PROPOSED 2026-08-26". Built in Order 17 (kolt.local 031; `fs::Watcher`, atomic writes exist); no sign in the file.
15. `README.md` - The proposal directory index is "as of 2026-08-03, re-verified 2026-08-18"; 38 papers from the later orders are not listed in it (grep by file name), so it is the first file a reader opens and the least complete. Its statuses for old rows are right; it silently omits everything since August.

Also stale-but-unmarked, just outside the 15: `proposals-repo.md` and `tracker-migration.md` (both "PROPOSED"; N15 and N17 executed Aug 2026), `perf-baseline.md` (SHIPPED, but numbers are July/August and the harness was replaced by the budgets/ceilings series), `kolt-migration.md` ("LIVING DOCUMENT 2026-07-11", untouched since 08-28), `markdown.md` (DRAFT; std::markdown step 1 shipped), `hashable-keys.md` (PROPOSED 2026-07-14; Hashable exists), `tuple-module.md` (PROPOSED; A122 closed), `trait-typed-fields.md` (rev 2 "DISCUSSION REQUIRED"; B184 closed), `closure-captures.md`, `closure-type-views.md`, `class-writes.md` (all DRAFT; ids closed), `beta.md` (RATIFIED, but beta deferred 2026-08-26), `debugging.md` (header "PAPER, drafted"; has "As built" sections).

## 2. Tracker statistics

Open rows: 217 (matches 217 item files). Filed date = "filed YYYY-MM-DD" in the item status line, else the first date in the status line, else the first date in the row, else the earliest date in the first 40 lines of the file, else the git add date of the item file. Source counts: earliest-in-head 26, status 30, filed 118, row 36, git-add 7. Caveat: 30 items carry the frozen-era dates 2026-07-18 or 2026-08-18 (the re-baselines of the old trackers), which are upper bounds on their true age; the "oldest" per section is therefore usually such an item. Age is as of 2026-11-17.

Kind buckets are derived from the Kind column plus title (miscompile/unsound wins first, then paper, then section M => performance and section N => hygiene, then design/owner, bug, else feature). They are approximate.

| section | open | bug | miscompile/unsound | feature | design/owner | performance | hygiene | paper | oldest (id, filed, days) | median age (d) | older than 60 d |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A reactive core & UI | 24 | 1 | 0 | 6 | 14 | 0 | 0 | 3 | A7, 2026-07-18, 122 | 60 | 12 |
| B type system & solver | 55 | 30 | 6 | 12 | 6 | 0 | 1 | 0 | B3, 2026-07-18, 122 | 14 | 7 |
| C memory model | 2 | 1 | 0 | 0 | 1 | 0 | 0 | 0 | C2, 2026-08-28, 81 | 81 | 2 |
| D documentation | 1 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | D5, 2026-07-18, 122 | 122 | 1 |
| E LSP & tooling | 23 | 9 | 0 | 5 | 5 | 0 | 3 | 1 | E62, 2026-08-18, 91 | 22 | 5 |
| F native & rendering | 24 | 4 | 0 | 9 | 7 | 2 | 1 | 1 | F1, 2026-09-14, 64 | 7.5 | 3 |
| G macros & const | 4 | 0 | 0 | 1 | 3 | 0 | 0 | 0 | G2, 2026-07-18, 122 | 80.5 | 3 |
| I collections | 3 | 0 | 0 | 1 | 2 | 0 | 0 | 0 | I2, 2026-07-18, 122 | 122 | 2 |
| J concurrency | 3 | 0 | 0 | 2 | 1 | 0 | 0 | 0 | J4, 2026-07-18, 122 | 122 | 2 |
| K web presence | 4 | 0 | 0 | 4 | 0 | 0 | 0 | 0 | K5, 2026-08-18, 91 | 82.5 | 3 |
| L release engineering | 5 | 0 | 0 | 1 | 2 | 0 | 2 | 0 | L3, 2026-08-20, 89 | 81 | 4 |
| M performance | 43 | 0 | 1 | 0 | 0 | 41 | 0 | 1 | M10, 2026-08-26, 83 | 36 | 13 |
| N hygiene | 26 | 0 | 0 | 0 | 0 | 1 | 25 | 0 | N16, 2026-08-18, 91 | 13 | 4 |
| all | 217 | 45 | 7 | 41 | 42 | 44 | 32 | 6 | - | 22 | 61 |

Section H does not exist in INDEX.md (retired). Largest sections: B 55, M 43, N 26, A 24, F 24, E 23.

### Decision queue (items waiting on the owner)

Method: a keyword scan (owner, ruling, question, rec, decide) over row, kind, status line and the first 30 lines of each item file hits 52 rows plus 33 more by file head; most are informational (RULED already, or "owner's item" meaning the owner filed it). I read the hits and kept the ones that are genuinely open decisions. Not kept: A180, A183, F175 (RULED), A185 (ruled, see below), E62 (DEFERRED by ruling). L3 is kept for its deferred ruling. "rec" = the item file carries a recommendation.

| id | filed | age d | rec? | the question |
|---|---|---|---|---|
| A14 | 2026-07-18 | 122 | no | optimistic-lifecycle.md §9: the paint-less action-state cell, and does the free `optimistic` survive it (one parked owner question) |
| D5 | 2026-07-18 | 122 | no | Public traction plan - needs a dedicated session with the owner |
| L3 | 2026-08-20 | 89 | no | std tier sweep: beta.md §5.1 table ruling DEFERRED 2026-08-20 until the beta switch |
| B147 | 2026-08-28 | 81 | no | Module/file-level default for `[platform(...)]` (design-gated on attribute-default semantics) |
| B183 | 2026-09-01 | 77 | yes | Tuple comprehension: the concrete arm and the six questions of §R8 (zip form already shipped) |
| M18 | 2026-09-01 | 77 | yes | Function attribute marking a bundle boundary (owner-proposed, exploratory; bundle-boundaries.md rec awaiting ruling) |
| A37 | 2026-09-03 | 75 | no | Build `[gone]` (trait-member reachable only through the trait)? Owner "not sure how valuable"; not queued |
| L20 | 2026-09-05 | 73 | no | Run the Windows test leg natively on the WSL2 host (owner's own step of L19) |
| A87 | 2026-09-11 | 67 | no | Add `Owner::release()` (run cleanups, stay live)? rec: only when a caller appears |
| B298 | 2026-09-11 | 67 | no | Name for an anonymous binder in a diagnostic (trait-typed-fields.md rev 2 §Q3) |
| A97 | 2026-09-13 | 65 | yes | Wire contract: one `Unsubscribe` per `Subscribe` (as built), or the server forgives double-Subscribe? |
| F1 | 2026-09-14 | 64 | yes | GPU-rendered native apps discussion; owner questions (mostly overtaken by native-objective.md/native-ui.md rulings: close or rewrite) |
| F15 | 2026-09-14 | 64 | no | Three-layer `std::ui` rule and an N-way twin-parity gate |
| A106 | 2026-09-17 | 61 | yes | Widen `std::style::prelude` with the types and make it ambient in std::web files (door 2)? rec: widen + document now, door 2 after a collision census |
| F17 | 2026-09-17 | 61 | no | How to write UI once for native and web (owner's discussion) |
| F27 | 2026-09-21 | 57 | yes | Userland platform-specific code (platform-coloring.md §8, R3's six questions) |
| M88 | 2026-09-27 | 51 | yes | Devirtualize single-implementor `dyn Trait`: a rec, not a ruling; paper-sized |
| I10 | 2026-09-28 | 50 | yes | Injected ordering strategy for hash maps/sets - already answered in reactive-maps-sets.md Q7 (insertion order, SortedMap for key order): close? |
| F115 | 2026-10-08 | 40 | yes | F102 analyzer half: language rule vs backend fix for a closure capturing a binding while a `&mut` view is held (owner question) |
| L24 | 2026-10-09 | 39 | no | Native Windows self-hosted runner on the WSL host (owner asked 2026-10-09) |
| E297 | 2026-10-12 | 36 | no | "The edited item's diagnostics published first" has no honest reading inside one analysis: what to promise? |
| A173 | 2026-10-16 | 32 | yes | terminal.md owner questions (S3 line editor needs terminal size, ESC literal, cursor report, grapheme widths) |
| E339 | 2026-10-16 | 32 | yes | fmt: a binary's right-operand call counts the `;`? (owner rec KEEP) |
| A175 | 2026-10-26 | 22 | no | rpc-revoke.md: five questions on `Connection::revoke(store)` |
| M174 | 2026-10-26 | 22 | yes | json-field-default.md: five questions; rec: build next order (not breaking) |
| B715 | 2026-11-09 | 8 | yes | Review the one caveat of the supertrait-default-method mono fix (fix landed with A185 S2) |
| B737 | 2026-11-11 | 6 | yes | Rule `std::ui` on `MaybeSignal` vs `Bindable` (trial builds natively, two example apps refused at check: "purely design, for the owner") |
| N207 | 2026-11-16 | 1 | no | Tracker ids are allocated per local branch (kolt-* branches collide): ruling on a process fix |

Queue size: 28 items; 14 carry a recommendation in the file, 14 do not (the "rec" test is a text match, so treat it as indicative).

The 10 oldest: A14 (2026-07-18, 122 d); D5 (2026-07-18, 122 d); L3 (2026-08-20, 89 d); B147 (2026-08-28, 81 d); B183 (2026-09-01, 77 d); M18 (2026-09-01, 77 d); A37 (2026-09-03, 75 d); L20 (2026-09-05, 73 d); A87 (2026-09-11, 67 d); B298 (2026-09-11, 67 d). Ties at 2026-07-18 / 2026-08-18 are re-baseline dates, so the true order among them is not determined.

Stale status lines found while reading (items whose own status contradicts later facts): A185 says "unruled" but the paper was RATIFIED rev 2.2 with R1-R17 on 2026-11-08 and S1/S2/S3/S5 landed; F175 says "open" though S1-S4 landed and its 13 decisions were RULED 2026-11-12; B713 "OPEN" though SHIPPED v0.55.0; B737 "open" though FIXED.

### Open items that look ALREADY DONE (candidates for closing)

| id | evidence | confidence |
|---|---|---|
| B713 | item body: MERGED a6dc370e, "SHIPPED in v0.55.0 (tag fc9efaa1)"; changelog v0.55.0 head names B713 | high |
| N192 | changelog v0.54.0 head "N192: a native server reads past a request's head by at most one slice ..."; order56 Q11 text: "N192 as a REAL native bug (fixed, 6dbbab39)" | high |
| N193 | changelog v0.54.0 head "N193: scripts/cut-release.sh rebuilds std::image's committed wasm blob"; Q11 RESOLVED | high |
| E99 | changelog v0.39.0: "`-d` dumps the raw parse now, and its help says what each stage is" - exactly the item's ask | high |
| B715 | status: "FIXED on next with A185 S2 (lane lens-s2)", shipped v0.55.0; held open only for the owner's review of one caveat | medium-high |
| B737 | item: "FIXED on next @70399859 (merged 0e65bdc6)"; changelog v0.56.0 F168 entry; what remains is the MaybeSignal design call (split into a new item) | medium-high |
| F175 | item: S1-S4 LANDED 2026-11-13 (Path, Icon, kit wiring, Lucide package); changelog v0.56.0 heads; gfx-path.md R1-R13 built; open decisions are none | medium-high |
| A138 | reactive-maps-sets.md S0-S2 landed Order 45 (v0.43.0 changelog: HashMapCell/`at(key)`, `MapEntry`); item row still "consider ... MapCell"; remainder = KeyedCell re-founding, `min_by` | medium |
| I10 | decided in reactive-maps-sets.md Q7 and stamped on the item 2026-10-01; no build item remains | medium |
| M199 | merged to next @20b9fc49 (v0.56.0, three changelog heads); item keeps the alias-tracking remainder = M201 | medium |
| M106 | `vilan check --explain-cost` shipped v0.44.0 (changelog); the "suggest a type annotation" half is the rest | low-medium |
| E334 | generator fixed (v0.53.0 changelog E334); stamped not closed deliberately because the gate still asserts nothing (E343) | low |
| B183 | zip form shipped v0.42.0 ("A tuple comprehension ZIPS"); concrete arm remains | low (partial) |
| M202 | "PARTLY DONE 2026-11-11 (lane m202-58)", v0.56.0 changelog head M202 | low (partial) |
| B705 | emit-58a built the receiver-read case; the `let v = &mut xs` held-across-statement shape remains | low (partial) |
| M101 | Order 45 note: the cache it wanted is no longer needed; v0.44.0 changelog entry on entry-world analysis | low |

### Closed counts per month (archive.md, `CLOSED 2026-MM`)

| month | closed |
|---|---|
| 2026-08 | 43 |
| 2026-09 | 728 |
| 2026-10 | 582 |
| 2026-11 (to the 16th) | 87 |
| total | 1,440 (= number of archive bullets; every bullet carries a CLOSED date) |

Items closed before 2026-08-28 live in the frozen eras under `archive/` and are not counted.

## 3. The chronicle's "Now / Next / Later"

File: `/home/reed/code/vilan-lang/proposals/tracker/chronicle.md` (2,972 lines; file last changed 2026-11-16). The block is at lines 76-873 under the file title "Vilan Backlog — open items (re-baselined 2026-08-18)" (the title itself is stale: the open list moved to `projects/vilan/tracker/INDEX.md` on 2026-08-28).

Is it current? No. The latest date inside the block (lines 76-873) is 2026-09-01; the latest release it mentions is v0.40.0 (and its Now paragraph speaks of cycles 19-26 and v0.35.0/v0.36.0). Today is 2026-11-17 and v0.56.1 is out: 16 minor releases, orders 22-58 and about 11 weeks have passed. The block is a historical snapshot, not a planning surface, and it is not labelled as one.

What later entries contradict:
- "Now": "cycles 19-26 closed ... v0.35.0 SHIPPED 2026-08-21, nothing active". The file itself records cycles through Order 58 / cycle 63+ (v0.56.0 and v0.56.1 on 2026-11-16).
- "Next": the parked rulings B127 (blanket deleted, shipped), L10/N15 (N15 executed 2026-08-28; the proposals repo exists), L4 (deprecation shipped), M9 (overlay loads shipped), K9 (playground completion built 2026-08-22), E69/E80, B125/B126/B130 and "N8's sunset" are all done or closed. "Beta" and "Kolt" accounting references stand but are two months old.
- "Later": A7/A8, B3/B11, C2, I2, J4 are still open in INDEX.md (still true), but C1 (Weak) closed 2026-09-17 (Order 37) and D5 is still waiting. The Zed extension E62 "DEFERRED" is still true.
- Structure: the chronicle has no Order 56 or Order 57 headings and no v0.54.0 / v0.55.0 / v0.55.1 headings at all (checked by grep); after Order 55's 2026-10-31 entries the next heading is Order 58's v0.56.0 publish (line 2888). Also the tail of the file is in reverse order for Orders 52-55 (headings appear twice in different arrangements, lines 2906-2970). Orders 40-58 use short GO/MERGED/SEALED/PUBLISHED entries; the longer Orders 22-39 narratives sit before them.
- There is no current "Now / Next / Later" anywhere; the live plan is distributed across `sweeps/orderNN/go-items*.json`, memory of the integrator and INDEX.md.

### Owner-question files

| file | state |
|---|---|
| `sweeps/order55/owner-questions55.md` (156 lines, Q1-Q34) | Closed out: the file's own tail says "ALL post-order questions 1-33 are now ruled" (rulings 2026-11-03); Q34 is a note (E360 renumbering). Nothing open. |
| `sweeps/order56/owner-questions56.md` (15 lines, Q1-Q11) | Q11 RESOLVED 2026-11-04 ("Delete tag, re-cut"). Q1-Q10 carry no ruling stamp. By cross-check: |
| | Q1 A180 marker trait does not hold, door 2 stays as shipped: A180 still OPEN, no recorded answer (open). |
| | Q2 B682 keep open, solver lane next order: B682 still OPEN (open). |
| | Q3 B695 kolt sites: B695 CLOSED 2026-11-03, nothing to rule (effectively resolved). |
| | Q4 M163 re-weighed: M163 still OPEN (open, informational). |
| | Q5 `implementors_in_reach` fix kept: merged and shipped in v0.54.0 (effectively accepted). |
| | Q6 M194 first next order: M194 still OPEN, never built (open). |
| | Q7 M174 paper, five questions: M174 still OPEN (open, rec: build). |
| | Q8 M175 paper: M175 CLOSED 2026-11-16, shipped v0.56.0 (resolved). |
| | Q9 A175 paper: A175 still OPEN (open). |
| | Q10 perf rows over 3 % of ceilings (budgets.toml Q6 approval): later seals (57, 58) re-based ceilings; not determined whether this exact approval was given. |
| `sweeps/order57/`, `order58/` | no owner-questions file. `order58/sweep-1116-report.md` has one owner row (B731 "owner-ruling", already ruled). `order58/kolt-patch-notes58.md` is owner homework, not questions. |
| other orders (`sweeps/order4x/5x`) | no file named owner-questions; `order53/filed/spec53-owner-terminal.json` and `order51/newitems51-owner*.json` are filed-item batches, not question lists. |

So the open owner decisions from the order records are: Q1, Q2, Q4, Q6, Q7, Q9 (and Q10 undetermined), all already in the decision queue above as A180/B682/M163/M194/M174/A175.

## 4. Other documents

Dates are from `git log -1` in the owning repo (vilan: integration worktree on next @6edafda5; vilan main = 12b8f86a, the v0.56.1 fold).

| document | last changed | still true? |
|---|---|---|
| vilan/README.md | 2026-09-28 | Mostly. Says "fast-moving alpha ... the test suite holds ~3,700 tests" (the suite is ~11,600 per the item files, Nov 2026) and "full build of the example client ~0.2 s". The crate list in "Repository structure" names 5 crates (core, cli, lsp, embedded, wasm) but `crates/` holds 19 (vilan-rt, vilan-rt-gfx/-webview/-term/-net/-sqlite/-image/..., vilan-rust, vilan-ide, vilan-image(-wasm)). Commands (`cargo install --path crates/vilan-cli`, `homebrew/`, `npm/`) exist. Stale in counts and crate list. |
| vilan/AI_STANCE.md | 2026-08-06 | Yes; a stance statement, no concrete facts to drift. |
| vilan/WISDOM.md | 2026-11-10 | Yes; newest doc (779 lines), sibling `docs/guide/wisdom.md` same date, cross-link verified (file exists). |
| vilan/AGENTS.md (522 lines) | 2026-11-13 | Current (mentions zeno/Lucide gfx work of Nov 13). |
| vilan/CLAUDE.md (106 lines) | 2026-11-10 | Current. |
| vilan/CODE_OF_CONDUCT.md | 2026-07-29 | Yes. |
| vilan/CHANGELOG.md | 2026-11-16 | Current (v0.56.1 on top, `## Unreleased` empty). |
| vilan/REPORT-*.md (9 files: editor-43/44, hygiene-43, native-43, reactive-43, solver-44, syntax-43/44, tuples-43) | 2026-09-28 / 09-30 | Tracked lane reports from Orders 43-44 sitting at the repo root; clutter, not documentation. Candidates for removal or moving to the proposals sweeps. |
| vilan/docs/README.md, SUMMARY.md | 2026-11-11 | Current (renderer pin `mdbook 0.5.4` matches README). |
| vilan/docs/guide/*.md (13 files: debugging, dev-loop, native, persistence, reactive, routing, services, ssr, styling, tracked-reads, ui, walkthrough, wisdom) | 2026-10-01 to 2026-11-13 | Recently touched all (oldest tracked-reads 10-01, dev-loop/reactive/routing/ssr/walkthrough 10-05); every guide is within ~6 weeks. Guides for reactive/routing/ssr were last edited 10-05, before the lens (v0.55) and typed elements (v0.56); whether they mention them is not determined. |
| proposals/README.md | 2026-08-28 | Partly stale. Says layout `projects/vilan/proposal/` (true), "`archive/` ... frozen eras" (true), "no `next`, no tags" and "CI is scripts/check_hygiene.py" (true), but says the proposal README is "gated: exactly one row per paper" while 38 papers (all from Sept-Nov) are missing from `proposal/README.md` by filename grep. Also does not mention branches kolt-* / worktrees. |
| proposals/projects/README.md | 2026-08-28 | Describes the per-item format; "pending the owner's ruling on the wider restructure (tracker N17)" is stale (N17 executed 2026-08-28). Layout section is right. |
| proposals/REPORT-kolt-escapes.md (99 lines) | 2026-10-26 | A one-off lane report at repo root; clutter. |
| proposal/releases.md (581 lines) | 2026-09-27 | Current: §7.3 `release/0.MINOR` patch branches is what v0.55.1 and v0.56.1 used; `cut-release.sh` and `fold-release.sh` exist in vilan/scripts. v0.41.1 is the newest release it names. |
| proposal/process.md (1,072 lines) | 2026-08-28 | RATIFIED 2026-08-07; predates the proposals-repo split and ~30 orders; sections on the sweep/seal/cut flow are in releases.md and the scripts, so process.md is the weakest-fitting. Not spot-checked beyond its header. |
| proposal/README.md | 2026-11-09 | See paper #15 above. |
| vilan-lang.github.io/README.md | last commit 2026-08-29 | Not determined whether it still matches (deploy target of the website; repo is a build output). |
| vilan-website/README.md | repo head 2026-11-03 (cf53198) | Not read in detail; the repo is current (v0.54.0 stub fix). |
| vilan-branding/README.md, SHADOWS.md | repo head 2026-08-20 | Not determined; the branding repo has not changed since August. |

Other root files worth knowing: `proposals/` has 12 tracked `fold-*.js/.err/.native` files at its root (test-artifact leftovers from the fold of 2026-09), plus `REPORT-kolt-escapes.md`.

## 5. Leftovers in the proposals repo

`git branch -a`: main, origin/main (local main == origin/main, 0 ahead / 0 behind), plus 14 local branches. Worktrees (7, all under `proposals/.claude/worktrees/`): kolt-053, kolt-image-gaps, kolt-list-any, kolt-mirror, kolt-overlay-owner, kolt-packages, papers-45.

| branch | ahead / behind main | `git diff --stat main...b` | everything on main? |
|---|---|---|---|
| closure-ret-family, diag-anchors, e83-completion-parse-once, e84-package-demotion, k13-markdown-design, l12-reserved-names, std-doc-smalls | 0 / ~1,520 | empty | Yes, fully merged (last commits 2026-08-24). Safe to delete (not done here). |
| papers-45 | 0 / 617 | empty | Yes, fully merged (2026-10-01); has a worktree. |
| kolt-053 | 25 / 182 | 21 files, 819 insertions | The files are kolt-filed items and `struct-keys.md`; main carries them (open or tombstoned) under the same ids for most (A178/A179/B688/B689/B693/B710/B711/J8/M181-M186/M199/M201 are all on main; E358 is on main as E361; the branch's M200 was renumbered M201 and M201 is on main). Not a byte-level check. |
| kolt-image-gaps | 2 / 40 | 3 files, 42 insertions | On main under the renumbered ids M204, M205 (both open). |
| kolt-list-any | 1 / 29 | 2 files, 38 insertions | ID COLLISION: branch B739 ("mixed list literal at `List<any>`") is B747 on main; main's B739 is a different, closed item. Content is on main, id differs. |
| kolt-mirror | 7 / 62 | 8 files, 185 insertions | E362-E366 and renumbered B740/B741 are on main (E363-E366 open); the branch's B740/B741 (RemoteStore mirror patch / str-backed enum) are B745 etc. on main; main's B740/B741 are different items. Id collision again. |
| kolt-overlay-owner | 1 / 40 | 2 files, 72 insertions | A186 is on main (open). |
| kolt-packages | 5 / 62 | 7 files, 132 insertions | Same E362-E366 + B736/B740 renumbering story as kolt-mirror; content on main under other ids. |

Conclusion: no work exists only on a branch, but the six `kolt-*` branches carry ids that mean something else on main (B736, B737, B739, B740, B741, M200-M203) so they must never be merged as they stand (this is N207). The eight fully merged branches and `papers-45` are reapable. 

Untracked in the main checkout (`git status --short`, 6 files, all `scripts/integration/`): `e121-state-before-ceb5b6ff.json`, `e121-state-before-eca174d4.json`, `lsp-base-b4561bf6.json`, `lsp-base-ceb5b6ff.json`, `lsp-tip-b4561bf6.json`, `lsp-tip-ceb5b6ff.json` (seal-time measurement artifacts, not committed). Nothing modified or staged.

## Appendix: verification commands run

`ls`/`wc` on INDEX.md (217 rows), `grep -c CLOSED archive.md` (1440), a script reading every item file's status line (dates), `git log` per paper (182 entries), `git branch`, `git diff --stat main...<b>`, `git status --short`, grep over CHANGELOG.md for open item ids. No file in any repository was changed.
