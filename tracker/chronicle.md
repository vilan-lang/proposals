# Vilan Backlog — open items (re-baselined 2026-08-18)

**The single planning surface.** Everything open lives here; nothing else
is tracked anywhere else. The chain: `backlog.md` (the alpha capture,
frozen 2026-07-18) → `backlog-2026-07-18.md` (the cycle 15–19 era, frozen
2026-08-18) → this file. `roadmap.md` is superseded the same day — its
ranked-strategy role is the **Now / Next / Later** block below; its Done
chronicle stays where it is as history.

The rules, tightened where the last tracker drifted:

- **Open items only.** When an item ships, its tombstone paragraph moves
  to [`backlog-archive.md`](backlog-archive.md) in the same sweep that
  closes it, and the number is retired. A `STATUS: OPEN` line whose body
  says "COMPLETE" (how E55/E56/I4 read by the end) is the exact failure
  this rule exists to prevent.
- **Item numbers are stable identifiers**, per-section, never reused.
  Numbering continues from the frozen tracker (highest retired: A24,
  B124→125 below, C10, D14, E61, F13, G4, H9, I5, J6).
- **Carried items keep their live remainder only**; full shipped context
  lives in the frozen file, cited as `History:`.
- `STATUS: OPEN` / `OPEN (blocked: <what>)` / `OPEN (proposal-first)` /
  `OPEN (deferred: <demand gate>)` — same legend as before, plus the
  explicit deferred form for demand-gated items.

**Owner questions parked in papers and on items** (the recall surface,
rebuilt 2026-08-28 twice — each waits on a ruling, none blocks
unrelated work). STILL OPEN: optimistic-lifecycle.md §9 (the paint-less
action-state cell; whether the free `optimistic` survives it),
beta.md §5.1 (the tier table — DEFERRED 2026-08-20, re-present
with the beta switch's pre-work, not before).
STILL PARKED from Order 18's papers: build-hooks.md's ship-note
silences (G9's workspace-member question; transitive grants OWED
before the first hook runs; `--rerun-hooks` on `run --watch`; the
once-per-build note repeating every watch round), and watch's
unbounded queue (demand-gated — a ruling only if a real producer
outruns a real consumer).
**RULED 2026-08-28, second batch (on the Order 18 close):** std-shape
§7.9 — the partition NARROWS to the browser cluster (markdown.vl,
browser/*, process/document.vl, process/ui.vl; everything a CLI needs
stays `std::`) and THE SPLIT GOES ON HOLD, no rush, no execution
planned (§7.9's note carries the verbatim). temporary-drop §11 — NOT
ruled: the owner reopens THE LIFETIME MODEL wholesale ("truly explore
every avenue"), a dedicated session to come; C11 waits on it; the
paper is that session's input. N17 EXECUTED same day (the migration —
see the chronicle). v0.38.0 CUT same day on the owner's "Cut it."
**RULED 2026-08-28, the owner's batch on the Order 17 close report**
(each recorded at its home): ui-styling §0bis.6 RATIFIED (both
determinations stand); css-block §12 Q2–Q5 as recommended (S2
unblocked); build-hooks §10 Q1–Q7 as recommended (S1 unblocked; tier
2's threshold is the git dependency, NOW; Q5's second module root
flagged highest-unknown-cost); G7 as recommended (emit-time
reserved-kind refusal); C11 "write the paper — those should not leak"
(direction ruled: temporaries must drop; mechanics to the paper);
filesystem §12 Q6 — 020 owns the whole watch surface; css-block Q3
"take the keyword" (`css` becomes a hard keyword, three std renames,
breaking) and Q6 as recommended (method spelling — the §12 note has
the full batch); N8's shim REMOVED same day (the owner: alpha, no
traction — let the old links die; executed, pages fe4bc73); kolt.local
025(b) — an OPT-IN caching hook on `serve_build`, never default;
kolt.local 008 — an opinionated Tailwind-scope preflight, plus
`display: block` for buttons/anchors/selects, opt-in and opt-out-able;
E97 — the safe posture, prevent a poisoned cache; A26 — patch it
correctly (the harness and the `Closed` treatment); kolt.local 026
APPROVED — `std::` for true core, `vilan::` for auxiliary (`ui` under
`vilan::` since CLI-only programs are common and first-party;
`option` stays `std::`) — the std-shape amendment names the partition;
N17 — the full-repo per-item migration SHOULD HAPPEN, projects/ move
included; draft-reconnect §4 — stands as written, no default debounce;
bindgen §8 Q1/Q2/Q3/Q6 as recommended, and bindgen need not be
signature-only (→ B147 filed for the module-level `[platform]`
default). Earlier: RULED 2026-08-26 markdown.md §11 (K13's watcher —
recorded inputs, built at the docs-app rung); RULED 2026-08-27
kolt.local 031 Q1/Q3/Q5 and 014-merged-with-009 (Order 17 built both).

## Now / Next / Later

- **Now** — cycles 19–26 closed. Cycle 26 (2026-08-20) shipped E78
  (the unprovided-context error underlines every uncovered call on the
  path — the owner's ask, example-as-contract), E76 (one index space at
  the ariadne boundary), E77 (hatches compose onto supplied shells,
  checked), K11 (wasm pruned to 6 + the stale-pin fallback), K13 step 3
  (the site itself on rung 2, pixel-identical), N7 (branding manifest +
  byte-equal shadow recipes), and three papers awaiting rulings: B127
  (delete the blanket — census says zero serving sites), L10 (the
  namespace model), N15 (the proposals-repo migration plan). What is
  active: nothing — **v0.35.0 SHIPPED 2026-08-21** (the owner's call, a
  day before the scheduled Saturday): the first train on the scripts
  (cut refused nothing; release 773da400, 33 entries) and the first fold
  under the ruleset (8d7fe41b, all ten steps clean, the bypass notice on
  `main` as expected), the re-themed book + masthead live, the toolchain
  at 0.35.0 in both locations. The playground-todo A25 diff turned out
  already applied by the owner; the kolt patches remain theirs. Beta
  (b): v0.35.0 is the first counted train — earliest (b) 2026-08-29.
  Wave 2 (2026-08-22, the owner's ruling batch): b126 MERGED on the nod
  (3b83d7e5 + repair aaaf4d2a); website main @f3ede99 DEPLOYED (E80 pane +
  K9 completion; live once v0.36.0's wasm ships). RULED: C3a (widened to
  any external package → E84), E79 ×7 (→ E85/E86/K17), K9 ×4, B127 DELETE,
  M9 nod, L4 ×4, N15 ×6, E69 deferred (generated vocabulary direction),
  L10 ×5 (→ L12), E87 probed and filed. Wave 2 CLOSED 2026-08-23:
  b127 SHIPPED (blanket deleted; B128 + B130 closed with it), l4 SHIPPED
  (the deprecation mechanism whole), m9 SHIPPED (overlay-owned loads,
  ASan-proven, the soak reads zero), n15 PREPARED (extraction verified,
  runbook persisted — the cutover waits on the owner creating
  `vilan-lang/proposals`). Archive 75. **Order 10 (cycle 28) CLOSED 2026-08-24** — seven lanes, all
  SHIPPED (l12 reserved names + the std-shadowing hole; e83 completion
  parse-once 60.8→5.8 ms; k13 markdown.md PROPOSED, spike-proven, build
  behind §9's rulings; e84 package demotion widened; diag-anchors E82's
  finalize_build class + B131; std-doc-smalls E85/E86/E87/I4 + K17
  deployed; closure-ret-family B132/B133/B134 incl. a RELEASED
  miscompile — the unannotated loaned-tail alias). Archive 92. next
  @12dfa484 (suite 4061); proposals main @f1890b6; website main
  @e18eb0c + one HELD commit (a359612, lands after v0.36.0).
  **v0.36.0 SHIPPED 2026-08-24/25** (the owner's call,
  early again): release 0fb5e5f0 after ONE gate incident — the wasm
  tests' stack margin (SIGABRT on CI, fixed + plant-proven before any
  publish leg ran; the tag moved cleanly; B138 files the depth) — then
  13/13 green; fold 1a4444b0 carried the N15 freeze to vilan main; the
  playground's trace pane + completion are LIVE; the held website
  commit deployed (ed7cc20). Beta accounting: v0.35.0 → v0.36.0 = two
  consecutive trains, no patch between — trigger (b)'s letter may now
  be satisfied (early cuts vs "weekly rhythm" is the owner's Q1-style
  call), and B73's fix shipped, unblocking (c); (a) kolt migration and
  (d) D5 remain. **Kolt refactored current with 0.36.0** (2026-08-25,
  the owner's ask; kolt@4289594 on its vilan-migration branch: the
  builder chain, the generated shell, the counted mirrors; build +
  10/10 probe + 16/16 e2e green — whether this satisfies (a)'s letter
  is the owner's call; E92 filed from its one dogfood finding). **The
  owner hand-migrated kolt onward** (2026-08-26 — theme system, static
  assets + caching, routed panels; kolt@1e18a88) and reports the
  experience "much better than the last time I tried… actually quite
  good"; their 26 dogfood findings are filed per-item in the
  gitignored `projects/kolt.local/` (the N17 pilot format), with D15
  filed from the verification sweep. **BETA DEFERRED until further
  notice (the owner, 2026-08-26)** — too fast, no traction, no
  userbase; the (a)–(d) accounting above is parked, D5 is the gate
  (§L's header carries the ruling). N17 SCOPED the same day: kolt.local
  only for now, full-repo expansion recorded as the end state. What is
  active: nothing — **Order 11 (cycle 29) CLOSED 2026-08-26, same day
  as the Go** (k13-step-2 included): eight lanes, all SHIPPED, merged
  on next @37787a39 (pushed; union suite 4167/4167, parity 20/20, cut
  dry-run 0 reds — v0.37.0's Unreleased holds 20 entries). b136-loop-is
  FIXED the released loop-condition `is` miscompile (every conditional-
  position form was wrong; a release-notes line is DUE at the next
  cut); b138-depth measured the analyzer and bounded its deepest path
  (B139/B140 filed from its plants — the margin-shrink unlocker and an
  exponential-time find); compiler-tooling-smalls closed
  B135/B137/E88/E92/D15; e91-grammar-gen made the grammar word lists
  generated and byte-gated; audit-1 ran N16's first pass (security +
  diagnostics: zero secrets, zero unsound unsafe; 11 findings filed as
  L14–L16, E93–E96, K18/K19, N18, M10; L13's ledger re-key LANDED —
  13 drifted keys, one class, zero dead rows); style-dogfood shipped
  kolt.local 010–013 (`Style::attribute` as the fourth condition axis,
  `size()`, `Color::var`, `Color::oklch` — 014's deprecation now
  argues against a live API); std-dogfood shipped 018/019/022(b) + the
  `vilan` reservation (std-shape.md §6's second ship note) + 005;
  k13-step-2 shipped `std::asset::read` + the measured 16M fuel answer
  (markdown.md §11; one owner question PARKED there: the LSP watcher
  glob). Archive 102. **Order 12 (cycle 30) CLOSED 2026-08-26, also
  same-day** — the owner's five rulings built: all five lanes SHIPPED,
  next @b0780c0f (pushed; union suite 4228/4228, parity 25/25, dry-run
  0 reds — v0.37.0's Unreleased holds 25 entries, TWO of them
  breaking). **substring-ban** made the rule whole (`0 <= start <= end
  <= len`, refused at compile time on literal bounds, at run time via
  a `__substring` helper on the `__at` precedent, and at const time —
  free, since the const interpreter evaluates the transformer's own
  output; the clamp-and-swap arm that would have folded a WRONG STRING
  into a build is gone) and its census found **five latent bugs the
  clamping had masked**, all fixed here — two `Document` reads past
  the end, a `<!--` probe with no room check, and BOTH rpc frame
  routers' inverted reply slice, the server-side one remotely
  triggerable by a client sending `r:7`; `strip_prefix`/`strip_suffix`
  shipped as the replacement verbs. **int-limits** shipped
  `max_value()`/`min_value()` on all eight integer types (floats
  declined on hard grounds: no exponent literal syntax, and
  `min_value()` would prejudge most-negative-finite vs
  smallest-positive-normal) and disproved an apparent i53/u53
  bounds conflict — different bounds for different constraints, not
  drift, do not re-open. **style-chain-sort** landed Tailwind's order
  with unknown methods as barriers, the table derived from style.vl
  and gated four ways, and semantic preservation PROVED on the corpus
  — note the finding: under a planted family bug the CSS-invariance
  test stayed GREEN while the slot-resolution test went red, so the
  obvious proof would have passed a wrong sort. **hmr-token** closed
  E93; **build-trust** shipped E96 tier 1 and carried tier 2 forward
  (new paper `proposal/build-trust.md`). Archive 104. One golden
  wants an owner glance: `vilan/test/style.mjs` moved 7 lines, each a
  permutation of one const-folded slot map (class-attribute token
  order, a set to CSS) — mechanically confirmed and now pinned. **Order 13 (cycle 31) ACTIVE
  2026-08-26** — the owner's ask, B141 first: seven lanes.
  b141-await-parens (the RELEASED await-precedence miscompile — a field
  or method off an implicitly-awaited call reads the promise and yields
  `undefined`, found probing the owner's async-transparency question),
  sync-justifications (delete the FALSE justifications recorded for
  std's sync functions and the sync functions themselves where nothing
  justifies them — the owner's rule: a sync variant must name the
  caller that cannot suspend), then ref-index (kolt.local 003/002/+004
  — the reference index, diagnose-then-fix), css-declare (kolt.local
  032, the declaration block that makes the owner's "this capability
  should be core, generically" steer true), depth-tail (B139 the
  margin-shrink unlocker + B140 the exponential-time find), std-smalls
  (kolt.local 024 digests + 025(a) Request::header), fs-formalization
  (kolt.local 031 — the owner's formalized-filesystem vision,
  paper-first). HELD until sync-justifications merges: bytes-and-mime
  (030's remainder + 022's table — both rewrite build.vl). 016's
  css-block paper deliberately deferred to the next order so it can
  argue against 032's shipped API. **Order 15 CLOSED 2026-08-27** — six
  lanes, all SHIPPED, next @48169ea7 (pushed; union suite 4353/4353,
  parity 46/46, dry-run 0 reds — v0.37.0's Unreleased holds 46 entries).
  The organizing principle held: every build lane turned Order 14's
  ignored pins green, and the skipped count fell 17 → 7. **B142 was
  larger than filed and that was the order's main finding** — the bound
  belongs to SIX grammars, not the expression grammar alone; nested
  `fun` at 5000 levels SIGABRT'd while four other grammars parsed 5000
  levels with zero refusals, so an expression-only bound plus a margin
  shrink would have been a false claim. Margins finally moved: 256 → 128
  MiB spawns, 64 → 16 MiB wasm, the latter measured on the profile that
  ships. **kolt.local's IDE and dev-loop sections are now EMPTY** — 001,
  033 and 007 all closed, and 007 shipped larger than filed (a third
  face nobody reported: S1's "a reload subsumes the stylesheet refresh"
  died when S2 made a swap a module swap, so every round touching code
  and styles together dropped the styles). security-tail closed
  E94/E95/L14/N18 and L15's S half, correcting L14's stale action
  inventory and finding two high-value actions it never named.
  fs-writes shipped filesystem.md's S1 AND S2 together after disproving
  the paper's own glue prediction. Two papers landed: css-block.md
  (which discharges ui-styling §8 by turning its argument against the
  shipped `declare`) and filesystem.md's corrections. Archive 112.
  ONE PROCESS INCIDENT: the push was refused by the pre-push hook —
  one lane commit carried a non-pseudonymous identity, since its
  worktree did not inherit the repo's git config. Rewritten on the
  owner's approval, trees verified byte-identical, and the lane brief
  template now names identity so a worktree cannot reintroduce it. **Order 13 CLOSED 2026-08-26** —
  nine lanes, all SHIPPED, next @3de81ed5 (pushed; union suite
  4301/4301, parity 38/38, dry-run 0 reds — v0.37.0's Unreleased holds
  38 entries, FOUR breaking). **B141 fixed first, as asked**, and it
  was wider than filed: `make()()` threw rather than going silent, and
  the EXPLICIT `(await p).f` was broken too — the author's own
  parentheses were dropped at parse and never reprinted. The fix
  generalised an open-coded special case the printer already carried at
  width one, and moved ZERO goldens (the blanket alternative was
  measured at 88). **sync-justifications** deleted both sync reads and
  the false rationale at them, took load_build/asset_body/serve_build
  async, and left `fs::exists` and `rpc_server::create_hash` with TRUE
  justifications written at the function — the latter is the one place
  in std that can name a caller which cannot suspend, so the rule is
  demonstrably satisfiable and not merely violated. **depth-tail**
  found B140 MISFILED — the exponential cost was the PARSER
  speculatively re-parsing every precedence chain (C(n)=2·C(n−1)), not
  constraint wakes; 20 levels went 9.01 s → 0.24 ms — and closed B139
  both halves, which revealed B138's premise incomplete: every analyzer
  family is bounded now, and the parser is the real margin blocker,
  filed B142. **ref-index** replaced the resolution ladder with one
  identifier-occurrence index (003 was branches (b) AND (c), never
  staleness; 002's two symptoms were two bugs — one inapplicable edit,
  one destructive; 004's under-prune culprit was `self`, not
  `Ok`/`Err`). **css-declare** shipped `declare` with ordering settled
  by `@layer` rather than a sort band. **bytes-and-mime** put real
  bytes on the wire, typed from a generated mime-db table.
  **std-smalls** shipped digests and `Request::header`.
  **fs-formalization** landed `proposal/filesystem.md` and shipped
  `write_atomic`, closing a silent total-data-loss path in the todo
  example. Archive 107. Records: fullstack-dx §5.10 now argues the
  fence from scope rather than a capability claim that cited a deleted
  function. **Order 14 (cycle 32) CLOSED 2026-08-26** — one lane,
  pin-discipline, on the owner's ask ("pin fixed bugs and pin-ignore
  unresolved bugs"). An audit of BOTH directions found real gaps.
  FIXED SIDE: B139 was under-pinned — only its depth half was pinned,
  and the TIME half's evidence was a measurement in prose plus a green
  suite, which CLAUDE.md forbids as proof; now pinned with an
  `inference_entry_count` probe and a linear sweep in BOTH source
  orders (the old plant was caller-first only, as its own comment
  said), non-vacuity proved by disabling the memo read (400 links
  4,202 → 245,200 entries). B140's two plants shared one test fn so an
  arithmetic failure hid the list shape — split. A HONEST NEGATIVE:
  B139's empty-substitution gate turned out NOT behaviourally
  pinnable — 1,157 records are written caller-shaped, but deleting the
  guard leaves 2,596 inference tests, the docs gate and the
  byte-identical corpus unchanged, and twelve candidate programs
  failed to discriminate; pinned as a guard invariant instead (red at
  4 vs 0). OPEN SIDE: ten `#[ignore]`d pins across six defects (B142,
  E94 ×2, kolt.local 001 ×3, 007 ×3, L15), each verified genuinely red
  when un-ignored — B142's SIGABRTs on stack overflow, proving the
  filing. Two items were corrected BY their pins: kolt.local 001's
  `a.|.b` face does NOT reproduce (pinned green rather than shipping a
  pin that passes while its bug is open) while a THIRD face was found
  (a space before the dot), and 007's removal path turns out to
  REASSERT a deleted stylesheet. K18 is the one open defect the pin
  rule structurally cannot reach — recorded on the item. Skipped count
  7 → 17; suite 4310/4310; next @d51e258b. **Order 15 (cycle 33) ACTIVE
  2026-08-26** — the owner's Go. Organizing principle: **turn Order 14's
  ten ignored pins green** — every build lane un-ignores pins already
  proven red, so acceptance criteria exist before the work starts. Six
  lanes: completion-class (kolt.local 001's cursor-context model +
  033, newly filed from the owner's `list.iter().|` report — member
  completion offers only what an impl block declares, so every
  DEFAULT-BODIED trait method in the language is invisible on every
  implementing type: 1 of 15 iterator methods, and `Ord`'s min/max/clamp
  too), b142-parser-depth (bound the parser, THEN collect the payoff and
  shrink the 256 MiB/64 MiB margins that B138 and B139 were both
  chasing), security-tail (L14/L15/E94/E95/N18/K19 — the owner's stated
  pre-beta bar), hmr-classification (007's full matrix, including the
  resurrection bug the pins found — a deleted stylesheet is re-injected),
  fs-writes (filesystem.md's S1, explicitly sequenced as "do next
  regardless of any ruling"; there is still no binary write at all), and
  css-block-paper (016, held from the last order so it can argue against
  `declare`'s SHIPPED API rather than a hypothetical one). HELD: 029
  (unblocked by 030+022 but design-first and would collide with fs-writes
  in fs.vl). Waiting on the owner, not on capacity: 031's six questions
  led by Q1, 014's fork, 008's posture, 022(b)/025(b)'s shared fence, 026.
  **Order 16 (cycle 34) ACTIVE 2026-08-27** — the owner's Go. Organizing
  principle: **a built app needs nothing but `dist/`**, and like Order 15's
  it is an acceptance test that exists before the work does — build a
  program that depends on a non-code resource, delete its source tree, run
  the artifact. That fails today in OUR OWN tree, not only in kolt:
  vilan-website's `deploy.yml` hand-copies `playground/editor.js`,
  `examples.js` and `worker.js` out of the source tree into `export/`
  because `vilan build` will not carry them — the site's CI is the
  workaround — and kolt's server reads `src/static/*` and `src/head.html`
  at runtime. Six lanes, closing kolt.local's whole Build section plus
  017. path-tooling (017 — `std::path`, the fork settled toward free
  functions over `str`: a `Path` type earns its keep only at
  normalize/relative and would collide with 031's unruled handle tier;
  std is its own caller, `fs.vl`'s `read_dir` doc names a module that
  does not exist), then asset-bundle HELD on it (029 — the import-file
  const function; the framing to verify is that `std::asset::read` is
  ALREADY the const INPUT channel and 029 is its OUTPUT sibling, with
  030's bytes, 022's generated mime table and 024's digests all shipped
  beneath it; this lane owns the order's gate). build-hooks (027+028,
  paper-first — trust EXTENDS `build-trust.md`'s E96 tiers rather than
  inventing a second model, and 028's template is already in the tree:
  std's own css pipeline IS a build-time accumulator, `Style::rule`
  appending through `emit` and `assemble_assets` flushing in canonical
  order; the paper must answer whether 029 makes 027 smaller).
  css-raw-typed (016's S1, deliberately the slice with NO grammar and no
  dependency on any of the paper's six questions — and a real bug fix:
  reaching for `.css` to get a token into `raw` drops its `:root` line, a
  live dangling-`var()` hazard). audit-2 (N16, **THREE ORDERS OVERDUE** —
  the item says every other order and named Order 13; 13/14/15 all ran
  without one; rotation this run: error handling, dead code, tidy &
  structure, since Order 11 took security+diagnostics and Order 14 was in
  effect the test audit). website-harness (K18+K20 — stand a runner up in
  vilan-website FIRST, since K18 is the one open defect the pin rule
  structurally cannot reach; `crates/vilan-cli/tests/hmr.rs` is the shape;
  K18 is two parts because `HostEvent` binds only `data()`; K20 rides the
  same branch, staged not deployed). CONDITIONAL 7th lane, fs-handles
  (031's S3 + 020), runs only if Q1 is ruled. Records with the order:
  kolt.local **034 filed** — 003 was ARCHIVED with branch (c) still live,
  reachable only from an archived paragraph and a red pin, so the INDEX's
  "the IDE section is empty" was false; the filing rule, not the bug, is
  the lesson. Also fixed before launch: all three `.claude/agents/*.md`
  pointed at the pre-N15 checkout path for `AGENTS.md` (the repo root before
  N15 split the toolchain and proposals repos), so every subagent began by
  reading a missing file. **A cut is the owner's open
  call** — Unreleased holds 46 entries, 5 breaking, 2 miscompile, the
  largest train since the re-baseline, and B136 + B141 both owe
  release-notes lines as RELEASED miscompiles.
  **Order 16 CLOSED 2026-08-27, same day** — six lanes, five shipped and one
  returned a paper; merged on next @23bd766e (pushed; union suite 4409/4409,
  parity 50/50, cut dry-run 0 reds — v0.37.0's Unreleased holds 50 entries).
  The gate held literally: `a_built_app_needs_nothing_but_dist` builds a
  two-leg project, **removes the source tree**, runs `dist/server.mjs` and
  fetches the resource — proven failing on `next` first (ENOENT) and passing
  after. **The order's framing was wrong in its load-bearing half and the
  lane said so.** `std::asset::read` IS the const input channel as briefed,
  but there is **no `BuildAsset` pipeline to register into** — `BuildAsset` is
  a runtime std struct derived from `chunks.json` at server boot, nothing
  compiler-side owns the name — and `emit` could never be the output vehicle:
  it accumulates *lines*, dedups and sorts them, and gives every kind one
  output name, so no `.png` survives it. `bundle` is therefore **`read`'s
  sibling, not `emit`'s**: same resolution, same lexical refusals, same
  const-only fixpoint, same build-input record, diverging only on fuel (a
  bundled file's bytes never enter the program, so a size charge would cap how
  large a resource may be rather than how much work a build does). The path IS
  the name, which settles subdirectories, collisions and renaming at once.
  **build-hooks reframed 027 and 028 out of greenfield**: `[build] run`
  already IS build-time execution and `asset::emit` already IS a named
  accumulator, so both asks are *policy* — a staleness predicate and a
  declared order — and its probes found two real defects behind 028 (one CSS
  cascade comparator applied to every kind, so `@media` sorts last in a kind
  named `manifest`; and a kind that stops emitting leaves its last file in
  `dist/`, which under this order's own principle ships). **css-raw-typed
  found a miscompile by refusing its own brief**: S1 as literally specified
  (`emit` inside the `Length`/`Color` impls) would have shipped a footgun,
  because the const-only check walks call edges and cannot follow a bounded
  generic's trait dispatch — the emit escapes into the JS as an unbound
  `__emit_asset` and throws at run time (B143, pinned `#[ignore]`d).
  **website-harness disproved K18's own prescribed fix**: an origin check
  cannot work against an opaque-origin sandbox, where every hostile frame also
  presents `"null"`; a per-Run token shipped instead, and vilan-website now has
  a harness and two CI gates, so the one defect the pin rule could not reach is
  reachable. **path-tooling** shipped `std::path` colorless and const-evaluable,
  differentialled against node's `path.posix` over 34 cases with two deliberate
  divergences. **audit-2** closed N16's three-order slip. 15 items filed:
  A26/A27, B143/B144/B145, G5/G6, E97, N19–N25. Archive 112. Records fixed:
  `build-trust.md` §4 named "the registry (tracker §D item 5)" as tier 2's
  enforcement point — **D5 is the public traction plan and no registry item
  exists anywhere**, and worse, git dependencies already deliver third-party
  code on an ordinary build, so tier 2 is reachable NOW and is 027's call, not
  a registry's. THE PROCESS FINDING: the proposals **main checkout was 8
  commits behind**, and three lanes were briefed to read the tracker and the
  papers from it — two reported papers "missing" and one filed three findings
  against stale text and withdrew them. Fast-forwarded; the brief template
  must name the integration worktree. Also: two lanes' branches merged clean
  in git and were **broken together** (the harness imports the editor bundle
  by path; the other lane moved it under `src/`), which no merge could see —
  caught by running the harness, not by reading the diff.
  **v0.37.0 SHIPPED 2026-08-27** (the owner's approval — "I have been pushing
  the cut off because I want all of the Kolt bugs fixed first. We can cut
  in-between if you must. It's fine with me this time"): release `b0d20e60`,
  50 entries (5 breaking, 2 miscompile, 17 feature, 26 tooling), all 13 jobs
  green across all five publish channels. B136 and B141 finally got the
  release-notes callout they had owed since Order 11 — written as a preamble
  at the top of the section, since `release.yml` extracts the whole section
  into the GitHub release notes. Fold `6fcb64d4`; `next` could NOT
  fast-forward onto it because the N26 fix landed after the release commit,
  which `fold-release.sh` caught as a red precondition and named the remedy
  for rather than guessing — merged by hand as `ea305f0f`.
  **ONE PROCESS INCIDENT, and it is L17.** The tree was tagged with **Windows
  CI red, and red since before the cycle began.** The orchestrator ran the
  union suite locally (Linux, 4409/4409) and treated it as the gate, which is
  what the local discipline says — and `release.yml`'s own gate is
  `ubuntu-latest` while `ci.yml` tests a ubuntu+windows matrix, so the gate
  authorizing a publish is strictly weaker than the gate deciding a commit is
  green, and nothing in `releases.md` §7.2 says to check CI on the commit
  being tagged. The `main` push then surfaced it a second way, in the
  ruleset's own bypass notice ("Required status check `check` is failing"),
  which was read as the expected bypass line and not as the signal it was.
  Severity, verified rather than assumed: two of the three Windows failures
  are **bad pins, not a broken fence** — `/etc/hostname` is not absolute to
  Windows, so a pin asserting the `is_absolute` arm's wording was handed the
  escape arm's; the path is still refused (its components carry a `RootDir`,
  neither `Normal` nor `CurDir`) and the Windows log shows exactly that
  message, so there is no security gap. Fixed in `72cdf805` (N26), each arm
  pinned on its own arm plus a new pin for the property that does not vary,
  plants confirming the split and that the invariant pin reddens only when the
  fence is gone entirely. The third failure is N25, a real Windows gap filed
  the same day independently. **Rulings received 2026-08-27** and recorded on
  their items: kolt.local 031 Q1 — (a)+(c) **scoped to `File` only**, the
  owner declining to make it a general law, so S3 is UNBLOCKED; Q3 — delete
  `fs::exists`; Q5 — the sixteen free functions stand. **014 RULED DELETE**,
  and a census run at the ruling CORRECTED the item: it claimed "the site
  estate uses the `dark` channel" and the estate is **zero** — website 0,
  examples 0, kolt 0, leaving one internal self-call, a corpus golden and six
  doc mentions, so the deprecation window would have protected nobody. The
  larger half of that ruling is the owner's ask for a general selector feature
  replacing kolt's hand-rolled `emit`, and **014 and 009 now merge**: 032's
  shipped `@layer` invariant breaks 009's specificity tie, so one relation
  axis (`within`/`children`/`divide`) covers both the ancestor theme guard and
  the Tailwind child cases while keeping ui-styling §1's promise as "a child's
  own `Style` always wins against a rule reaching in from an ancestor".
  **Order 17 (cycle 35) ACTIVE 2026-08-28** — the two rulings built, and
  the gates made honest. Eight lanes: style-relations (009+014 per the
  ruling, paper-first — the `@layer` composition and slot-key probes come
  before the build; `Style::dark` DELETED, breaking), fs-handles (031's S3
  whole on the `Database` template; `fs::exists` deleted per Q3, breaking;
  B141's old spelling pinned positive; watch deliberately follows in S4 so
  `Watcher` is designed to match `File`), compiler-fences (B143 — the
  const-only check follows bounded-generic trait dispatch — plus B144),
  ref-index-reverse (034 — un-ignore the reverse-deps pin; rename gains
  the same reach), emit-kinds (G5 kind-scoped ordering + G6 per-kind
  prune; the general sweep stays with E92), release-gate (L17 — the
  release gate gains the windows leg, §7.2 gains the tagged-commit CI
  check, the cut script refuses; rider N21, the fmt gate), hygiene-smalls
  (the K20 and K13 status drift, N19, N22, N24, this file's header recall
  surface), std-smalls (025(c), the ETag/304 helper). Two breaking
  entries; v0.38.0's Unreleased opens with this order. B145's
  `inference.rs` split is scheduled SERIAL after the fold, never
  in-cycle — it conflicts with every compiler lane by construction.
  **Order 17 (cycle 35) CLOSED 2026-08-28, same day** — eight lanes, all
  shipped; merged --no-ff, next @6edf6261 PUSHED (union suite 4482/4482
  exit 0; CHANGELOG parity 13/13 — v0.38.0's Unreleased holds 13 entries,
  TWO breaking: `Style::dark` and `fs::exists` deleted). style-relations
  built the ruling with its probes doing real work — TWO determinations
  deviate from the ruling's illustrative spellings and await the owner
  (§0bis.6: `within` must emit UNLAYERED or it loses to every base rule;
  `divide` renders `> :not(:first-child)` because the owl spelling ties
  with `children` and resolves by class-hash order, the exact forbidden
  resolution); the theme.vl-shaped corpus program is the acceptance.
  fs-handles shipped 031's S3 whole (Q1 File-scoped as ruled; Q2 as
  recommended; `fs::exists` deleted per Q3; B141's old spellings are the
  positive pins) and DISPROVED the paper's module-level-File bullet;
  its sharp find is C11 — an expression-temporary resource never drops,
  and S3's intended idiom makes that routine (owner semantics call,
  paper-first). compiler-fences closed B143 (refinement extracted into
  shared `dispatch_refine.rs`; plants proved the hole WIDER than filed —
  inherited-default and initializer shapes were live escapes; B146 files
  the coverage check's narrower diet) and B144. ref-index-reverse closed
  034 — the reverse-deps pin un-ignored, rename through the same union,
  a staleness refusal instead of skewed edits. emit-kinds closed G5/G6
  (css byte-identical gated; the pruner acts only on its own record) and
  probe-found G7: `emit("vl", …)` OVERWRITES THE ENTRY SOURCE FILE, exit
  0 — filed as an early-fix candidate. release-gate closed L17 (refusal
  proven LIVE against origin's real shas) + N21's fmt half (with the
  RUSTUP_TOOLCHAIN discovery). hygiene-smalls closed N19/N22/N24, fixed
  the K20/K13 status drift, archived the K trio + N25/N26 tombstones,
  rebuilt this file's header recall surface, and landed the dangling-
  `[[link]]` hygiene rule. std-smalls shipped 025(c) (RFC-9110 weak
  comparison; the open-builder shape so per-path Cache-Control chains on
  either arm; `serve_build` untouched — (b) stays fenced). Archive 122;
  five new items (B146, C11, E98, G7, G8); N21 narrowed to clippy/audit;
  kolt.local 12 → 9 open (009+014, 034 tombstoned; 031 → S3 shipped;
  025 → (c) shipped). Cut dry-run: the CHANGELOG sweep is GREEN (13
  parsed, ordered, families balanced); the single red is the NEW gate
  refusing the still-running CI at 6edf6261 — L17 doing its job on first
  live use. CI then completed GREEN on 6edf6261 (the first live proof of
  the fmt job, the toolchain-pin neutralization, and the ci.yml windows
  leg over the union tree — only the standing Node-20 deprecation
  annotations) and the dry-run rerun is CLEAN: zero reds, "ci.yml is
  green on origin", 13 entries ordered — the cut is one command away
  whenever the owner calls it. release.yml's own widened gate still
  awaits its first tag to prove live.
  **Order 18 (cycle 36) ACTIVE 2026-08-28** — the ruling batch, built.
  TWO WAVES around the serial pre-step: b145-split first (inference.rs
  split by SUBJECT MODULES under one test binary — tests/inference/ —
  so the suite keeps one link, the conflict magnet dies, and this
  order's own lanes append to the new files; analyzer half re-measured
  only), launched alongside the four lanes that never touch it:
  c11-paper (the expression-temporary drop paper — direction ruled, no
  leaks; mechanics recommended against destruction.md), std-shape-
  amendment (026's partition table on the ruled seam), n17-plan (the
  migration runbook; execution serial between cycles), audit-3 (N16
  run 3, no inference.rs edits). Wave 2 on the split's landing:
  css-block-s2 (the keyword taken FIRST — breaking — then grammar +
  desugar, byte-identical gate), build-hooks-s1s2 (staleness gate +
  the git-dependency trust opt-in shipped refusing everything),
  g7-g8-emit-fences, watch-020 (Watcher matches File), ruled-smalls
  (025(b) opt-in hook + 008 preflight + E97 posture), a26-reattach
  (the failure harness + Closed). All lanes Opus-capped per the
  owner's standing rule; Monitor-on-suite.log briefed as the default
  wait.
  **Order 18 (cycle 36) CLOSED 2026-08-28, same day** — eleven lanes in
  two waves, all shipped; next @460b0b3d PUSHED (union suite 4600/4600
  exit 0; CHANGELOG parity 25/25 — v0.38.0's Unreleased holds 25
  entries, FOUR breaking: Style::dark, fs::exists, the css keyword, and
  G7's fence — the lane called its own refusal breaking, honestly,
  though nothing in the estate emitted a build-owned kind).
  THE WAVE STRUCTURE WORKED: b145-split merged first (fifteen subject
  modules, one binary, counts identical leaf-for-leaf) and the six
  build lanes appended to the new files with ZERO inference conflicts —
  the magnet died the same day it was split. Ships: the css KEYWORD +
  S2 (gate held in both halves; the keyword renames moved zero
  goldens), build-hooks S1 + the trust opt-in (refusing everything;
  four underdetermined points decided in the building), G7 (the
  refusal is on the VALUE; one shared list, plant-proven across both
  consumers) + G8, watch (020's whole design — pull-shaped, polling
  v1, and the teardown question DISSOLVED: clearTimeout is
  synchronous, no second Q1 exception), A26 (the failure-mode harness
  outlives the fix), E97 (one posture + the anti-drift lock scan; ONE
  site genuinely needed clear-and-rebuild — the publish planner),
  preflight 008 (`@layer vilan.preflight` — one spec sentence orders
  everything), 025(b) (`cache_build`, url-keyed, byte-identical
  default by control flow). Papers: temporary-drop.md PROPOSED (rec
  STATEMENT-END — decided by the serve-forever main, not the loop; two
  premise corrections), std-shape.md §7 (Shape C, 36/20, one real
  dependency violation found, churn measured at 939 import lines),
  tracker-migration.md PREPARED (wholesale, verbatim-ID filenames,
  scripts tested on scratch copies; EXECUTION SERIAL between cycles),
  audit run 3 (rotation EXHAUSTED — run 4 is the first delta run;
  10 findings, 2 of its own hypotheses killed by planting). Archive
  132; filed B148/B149, G9, E99, M11–M13, L18, N27/N28; kolt.local
  9 → 6 (008, 020, 025 tombstoned — 025 COMPLETE, all three asks).
  Cut dry-run: CLEAN — CI completed green on 460b0b3d (both platforms,
  the fmt job's second live pass) and the rerun shows zero reds, 25
  entries ordered; the cut is one command away whenever the owner calls
  it. PROCESS FINDINGS: the shared
  session scratchpad bit two lanes (one wiped the other's probe
  project; notifications twice leaked a SIBLING lane's suite verdict
  into a lane that nearly reported it as its own — caught by the lane
  blocking on its own pid) — future briefs get per-lane scratchpad
  subdirectories and "verdicts from your own log, never a
  notification"; the n17-plan lane missed its paper's README index
  row (the hygiene gate caught it at merge, exactly its job); machine
  contention across eleven lanes made every timing number
  meaningless — the audit correctly refused to report suite-creep or
  perf deltas measured under load 18–46.
  LESSONS: lanes
  parked on "waiting for the suite notification" three more times
  (occurrences 6–8; the brief's discipline block alone does not prevent
  it — the one that armed a Monitor on its log self-resumed, the other
  two needed nudges: consider making Monitor-on-suite.log the briefed
  default); three lanes independently hit the same rustfmt drift and
  each handled it correctly (N21's toolchain pin ends the class); the
  CHANGELOG unions conflicted at five of eight merges, resolved
  keep-both with markers intact, parity checked at every step.
- **Next** — the owner's parked rulings (B127 §14.1; L10 §6 ×5; N15 §8
  ×6; L4's four; M9's nod; E79's §10.1 review; N8's sunset; beta.md
  §5.1 at the switch; the REWORD candidates), then the build lanes they
  unlock (B127's deletion, M9's overlay loads, N15's cutover), K9
  (design-first: the completion core's seam for wasm), E69/E80, B125,
  B126, B130, D5's session. The Zed extension (E62) is DEFERRED by
  ruling.
- **Later** — the long-gated compiler tails (A7/A8, B3/B11, C1/C2, I2,
  J4 — each blocked on a named design or the native arc), D5's traction
  plan (needs its dedicated session — and the 2026-08-26 beta deferral
  makes it the switch's actual gate), and the beta switch itself
  (DEFERRED until further notice 2026-08-26, the owner's ruling in §L's
  header; the trigger arithmetic is parked, not repealed).

---


---

**N17 EXECUTED 2026-08-28** (the first entry written INTO the chronicle
rather than migrated into it): the per-item migration ran in its serial
window per tracker-migration.md §8 — 44 open items split into
`projects/vilan/tracker/items/` with verbatim IDs, the eras frozen under
`archive/` with banner stubs at the old paths, the index-completeness
gate extended to projects and the dangling-cite rule taught to skip
backtick code spans (its first live run caught its own false-positive
class — `[[build.hook]]` is TOML, not a cite — and the fix was
plant-proven both ways). The verify script's census detector was
refined in the same pass (a tombstone HEAD counts as archived; a mere
mention does not) and passed clean: 44 = 44, hygiene green, 40 sampled
body lines lossless. From here: new items are files, closes are
tombstones in the project archive, and this file carries the narrative.

**v0.38.0 SHIPPED 2026-08-28** (the owner: "Cut it") — the fourth
scripted cut and the first tag through the widened release gate: 13/13
jobs green in 25m31s with the windows gate legs' first live run, which
closes the last unproven edge of Order 17's L17 work. Fold: main folded,
next at 6186824b, book republished, toolchains 0.38.0 both locations.
THE INCIDENT, and it is the release working as designed: the site deploy
went red because the website's own source used every spelling this train
broke — `Length::css`, the `.css` field, an extern accessor NAMED `css`,
one `fs::exists` — the same outside-the-gates class as v0.21.0's
styles.vl. The new keyword diagnostic named the fix at every site;
migrated (+ the 0.38.0 formatter's reflow, + examples.js regenerated for
its freshness gate), pushed (website de2efd6), deploy green, playground
serving v0.38.0 with six versions in the selector. Lesson re-learned
with a sharper edge: a breaking std/grammar change's census must include
THE WEBSITE, the one estate no vilan-repo gate can see — worth a line in
the cut script's own checklist someday.

---

**Order 19 (cycle 37) ACTIVE 2026-08-28** — the lifetime paper's
buildable half, and the arcs it joined; every §12 ruling in hand. TWO
WAVES. Wave 1, eight lanes off next @125b4d10: graph-repairs (lifetimes S1
— V1's proven cell-capture fix, A28 the std derivation leak pinned
25→0, Event::target_value, A29, and the SCC-walk suite gate), liveness-
dataflow (S2 — the real last-use dataflow at copy elision first, no
semantic change; GATES WAVE 2), drop-safety (B151 fix-now + B150,
red-first from the session probes), capture-spec (S5 — aliasing-as-
shipped into spec §6, the tour corrected, C12 decided in-lane),
css-block-s3s4 (the formatter + docs/editors slices), emit-keyed
(build-hooks S3, byte-identity with G5's order as the gate),
lucide-evidence (Q1's ruled method — the real icon pipeline against
[[build.hook]], the report decides build.vl), gate-smalls (M12, N27,
N28, L18, B152, E99). Wave 2 on S2's landing: lastuse-s3 (S3 whole +
the [extern(retains)] contract and std audit folded in for soundness;
the ordering amendment, family breaking; closes C11). Deferred, named:
E98/015 → Order 20, M11/M13 → a quiet machine, reuse spike → the
native arc's opening move, css-block S5 after S3/S4, audit run 4 due
Order 20. All lanes Opus; per-lane scratch subdirs; verdicts from own
logs only.

---

**Order 19 (cycle 37) CLOSED 2026-08-29** (opened 08-28; the overnight
pause was a locked signing vault, nothing else). Nine lanes in two
waves, all shipped; next @160cfa1e PUSHED — final union 4752/4752, exit
0, CHANGELOG parity 19/19 (v0.39.0's Unreleased: 2 breaking, 2
miscompile among 19). THE HEADLINE: the lifetime paper's buildable half
is BUILT — S1 (the graph repairs + the SCC gate; A28's router leak 25→0;
the V3 scope-split correction now in the paper), S2 (the last-use
dataflow; +69% elisions, goldens proven pure-clone-removal), S3 (disposal
at LAST USE, the ordering amendment family-breaking, 51 shipped pins
moved as pure reorderings), S4 (the [extern(retains)] contract + the std
audit, which caught appendChild over-marking via a split-golden deep
copy), S5 (closures capture bindings — said in spec §6.9, the tour's
false paragraph corrected, C12 ENFORCED on a zero census) — and C11
CLOSED (the temporary drops with its statement; the conditional
temporary refused, the arc's one new error). temporary-drop.md CLOSED as
the special case. Also: css-block S3+S4 (one order function, four
callers; S5 alone remains), emit_keyed (028 COMPLETE — byte-identity by
a shared interpreter arm), the lucide evidence run (Q1 CLOSED against
build.vl, four ways, pending veto; redirects filed as G10/E100/E101 +
027's reframed Q5), drop-safety (B150/B151, both miscompile-family,
RHS-first vindicated by the spec's own sentence), gate-smalls (B152's
divergent-tail generalization, E99, M12, N27, N28, L18 staged). FILED:
B153 (Option::replace declares a loan and keeps the value — the wave-2
semantics finding), C13, G10, E100, E101. LANE RULINGS AWAITING
RATIFICATION: drop-at-declaration for a never-read binding; JOIN
placement over per-arm (per-arm cannot be exception-safe without the
flag mR7 bans); retains marks the place ROOT. Owner queue also: the
ownerless-derivation refusal, caller-less ReactiveClient::dispose, the
build.vl veto window. PROCESS: a lane pkill'd every sibling's suite
(pkill -f nextest — the lesson now a hard brief rule: kill your own pid
only); rerere replayed a CHANGELOG union correctly at the wave-2 merge
but the wave-1 unions ate three family markers before parity caught
them; one conflict marker was briefly COMMITTED when a resolver's shape
assertion failed silently mid-chain — the repair discipline (parity at
every step) caught it two steps later. Wave structure verdict: second
clean run — the S2→S3 dependency cost nothing.

**Order 19 addendum, 2026-08-29:** the close's CI run came back RED on
the Windows leg — the new C11 fd-staircase e2e reads `/proc/self/fd`,
an instrument only Linux has — and THE MACHINERY WORKED END TO END: the
widened ci.yml matrix caught what the local Linux suite could not, and
`cut-release.sh` REFUSED the dry-run over the red, citing L17 by name.
This is the third instance of N26's lesson (a pin asserting one
platform's observables), now gated `#[cfg(target_os = "linux")]` with
the reason at the site (vilan f67710be) — the emission property itself
is pinned platform-independently in inference/resources.rs. The clean
rerun follows CI. — And it came: CI GREEN on f67710be, both platforms; the dry-run rerun is CLEAN, zero reds, 19 entries ordered (3 breaking, 5 feature, 2 miscompile, 9 tooling). v0.39.0 is one command away whenever the owner calls it.

---

**Order 20 (cycle 38) OPENED AND CLOSED 2026-08-29 — the narrow-grafts
order, and the day v0.39.0 shipped.** The cut came first, on the owner's
word: cut-release.sh applied clean at f67710be, release ce281993 tagged
and pushed, release.yml green on both platforms, fold-release.sh ran all
ten steps (main @2acb3f41, both deploys green, the live playground
manifest reading v0.39.0, toolchains 0.39.0 both locations), and the
breaking census came back ZERO — website and kolt both build green, as
the C12 entry's estate census predicted. Then the order: six wave-1
lanes off ce281993, two wave-2 lanes off the f36d4e15 integration tip,
one serial close step, all Opus.

SHIPPED, wave 1: the ESTATE VERBS (kolt.local 035 whole — `bundle_as`
with the collision refusal and the owned-name fence on the evaluated
target, const `read_dir`/`read_dir_all` byte-sorted with the directory a
tracked input, const `digest` closing 024's out-of-band-fingerprint
exhibit; the owner's manifest-key withdrawal held: everything landed in
the const channel); `db.migrate` (kolt.local 036 whole, paper
db-migrations.md — recorded-iff-committed inside each step's own
transaction, both drift refusals loud and pre-flight); G10 (declared
hook inputs wake the watcher through the one recorded-inputs door;
red-first proven by two pins timing out the full 300 s bound); the
GENERATED ROOT (027's Q5 slice — `[package] generated`, fmt and
format-on-save both leave products alone through one shared predicate,
the fmt-restale loop pinned dead); B153 as a MISCOMPILE (`Option::replace`
stored a bare loan — double destruction in accepted code; C11's temporary
predicate widened back with the retains exemption as new spec text; the
sweep found the internal NativeMap::insert use-after-free, filed B154);
and the diags batch (E98's doubling was TWO general causes plus a third
unfiled face, all closed by site-carrying destruction edges and one
dedup; E100's module parse errors anchor at their real spans; E101 as
`index_of`/`last_index_of` plus three refusals that name their cause).
Wave 2: `vilan build --explain` (G11, filed and shipped the same day —
builds then prints every output's contributors and every tracked input's
blast radius from records the build already keeps, one minimal
extension: ConstFact stamps the enclosing const site) and AUDIT RUN 4 —
the first delta run, and the method holds: twelve findings, six of one
new species ("the shipped sentence": prose beside code that does not
support it), all six fixed same-cycle (efb7e67c) along with the
un-pinned LSP format gate; B154/G12/G13/N29/N30/N31/E102 filed; run 5's
charter recorded on N16 (transformer-weighted delta + the shipped
sentence as a standing angle). Serial: M13 CLOSED — both perf harnesses
stamp loadavg per row and a per-run subject-count provenance row, and
the quiet-machine re-record landed at load 0.53–0.87 (the field proved
itself immediately: the first recording run's own release build polluted
the window at 8.39→3.36 and the rows said so).

CLOSED: G10, G11, B153, E98, E100, E101, M13 here; 035, 036 on
kolt.local (five open there — 027's remainder is exactly the (C) paper
decision). FILED: B154, G12, G13, N29, N30, N31, E102. PROCESS: the
estate lane self-reported one pkill-by-pattern (its own probe; rule
restated), and the integration briefly committed a conflict marker AGAIN
on the diags multi-hunk changelog union — caught by the parity check the
same turn, amended before anything left the worktree; the marker-hunt
now checks BEFORE the add, not after. The kolt probe's no-settle race
(found during the census under lane load) was fixed with a bounded
settle poll, 10/10 across three loaded runs. Final union suite and CI
verdicts recorded below when they land.

**Order 20 addendum, 2026-08-29 — the CI story, and the close's verdicts.**
The final union suite's FIRST run was red on the hygiene gate: the
audit-response commit's `git add -A` had swept `suite.log` into the tree
— the exact trap the estate lane had reported hours earlier. Untracked,
re-run green: **4846/4846, exit 0, parity 9/9**. The push's CI then came
back RED on the Windows leg — hook-watch's new added-file-under-directory
watch pin timed out its full liveness bound — and the machinery answered
properly twice over: the resumed lane agent's read-only diagnosis
eliminated every deterministic hypothesis by its own passing Windows
siblings and ranked the flake-shaped ones (H-A: the loop consumes a
snapshot difference BEFORE the action, so a round lost to a transient
action failure is lost for good), and the rerun came back GREEN —
flake-shaped confirmed. The response is pin-side and shipped (2ad39dd0):
the watcher's stderr lands in watch.log instead of the void, the timeout
panic carries the counts and that log, and the positive trigger-waits
re-touch every 20 s — a lost round is a verdict now, not a 300 s
mystery. The product-side design question is FILED as G14 (restore the
consumed difference on a failed action, or record the wait-for-next-change
posture as the ruling). And the suite.log sweep happened a THIRD time in
the hardening commit itself — pushed before the parity of habits caught
it — so the general fix finally landed: `suite.log` is gitignored, with
the three incidents as the rule's argument. **CI GREEN on 2ad39dd0, both
platforms; the v0.40.0 dry-run is CLEAN** — ok on ci.yml at the tip, 9
entries ordered (1 miscompile, 3 feature, 5 tooling), one command away
whenever the owner calls it.

---

**Order 21 (cycle 39) OPENED AND CLOSED 2026-08-29 — the ruled-queue
order, the third order closed in one day.** Nine wave-1 lanes (one a
LATE ninth, f14, ruled mid-order), audit run 5 in wave 2, and two
same-day FIX-NOW lanes off the audit's findings — twelve lanes, every
one green on its own suite.

SHIPPED: the PRELUDE PAPER (B156 — the census-drawn seven, the
three-preludes finding, nine owner questions) and the STYLE-VARIANTS
NOTE (kolt.local 015 — base+delta as a recipe, 15 probes, the
per-branch-const bundle-bloat finding, seven owner questions), both
proposals-side; B154 per the ruling (one word + the principled
two-head collapse; the sweep's use-after-free dead); G14 per the ruling
(a failed round keeps its difference, retried once; ExitCode became
readable to do it); G13 (the `.vilan-bundled` per-leg record — the
fourth writer learns the sweep rule; its own plant audit caught a
vacuous test it had just written); A30 per the ruling (`close_for_good`,
state-then-dispose, the redial negative; the THIRD terminal Closed
recorded as its own question); css-block S5 — and with it **kolt.local
016 CLOSED WHOLE**, the arc's no-S2-rework gate holding across four
orders, the server's first refactor.rewrite proven inverse; the smalls
four (E102's constructible two-errors case, N29, N30 reproduced live
before any edit, N31's gate whose FIRST catch — B149, "pinned but never
itemed" — closed by its own rule at integration); and f14 (the
to_lowercase rename + the honest _ascii pair, TWO latent bugs fixed by
the migration: the KELVIN SIGN opening a tag name, skip_raw_text's
false index claim). Between orders the owner proposed a `union` type;
the probes dissolved it into the SHIPPED trait-bound pattern
(AttrValue's own shape, user-reachable today), found the blanket-impl
accept-then-ICE (B158, RULED same day: SUPPORT with the specificity
rule — negation analyzed and declined), and B157 records the
MaybeSignal path riding it.

AUDIT RUN 5 — the transformer-weighted delta, and the emitted program
is where the bodies were: **F1, a RELEASED miscompile** (S3's widening
dead in every nested scope — the extents map and the widener keyed by
different chain ends; accepted vilan threw ReferenceError on 0.39.0),
FIXED SAME DAY as B159 (chain.last(), five shape pins red-first with
real ReferenceErrors, the audit's probes diffing exactly as predicted);
F2 the stand-down suppression, FIXED SAME DAY as E104 (per-offending-
type, non-empty guard); G15/G16/M14/E105/N33 filed; four sentence-sized
fixed in-order @167d4567 — among them run 4's bundle-identity finding
ALIVE IN A SECOND COPY four lines from the fix commit's own edits,
minting the rule: a corrected sentence gets a census. The golden-diff
centrepiece verified four of five moved goldens as pure reorderings and
caught the fifth's rotted header (resource_exit — fixed, the
pending-finally-at-exit pin gap recorded). The integrator's hand-merges
audited clean: line-multiset, zero invented lines. A CORRECTION to
Order 19's record: c8609287 moved 38 pins and added 15 (53 touched),
not the 51 the close entry said — the audit could not reconcile the
count and the commit is the authority. [RE-CORRECTED by audit run 7,
2026-09-01: the close entry's 51 WAS right — 51 modified + 17 added +
0 removed = 68 touched, derived by `grep -c '^+#\[test\]'`, hunk
contexts, and `--stat -M`; the commit MESSAGE's 38/15 was wrong on all
three counts and run 5 recalled it instead of deriving. The commit is
not the authority; the derivation is.]

CLOSED here: B154, B159, E102, E104, F14, G13, G14, A30, N29, N30, N31
(+ A28/A29/B150/B151/B152/C12 swept earlier the same day when the
ratification detail-pull found the Order 19 close had missed them —
five stale-open rows, the 022 lesson recurring at scale; close sweeps
must diff the changelog against the INDEX). FILED: B157, B158, B159,
E103, E104, E105, F14→closed, G15, G16, M14, N32, N33, plus the
prelude's E103 steer-loss and smalls' N32 grammar find. kolt.local:
016 closed whole, four open. RULINGS BANKED this order: the lifetime
trio ratified, ownerless-derivation deferred with its trigger, A30
wired, B154's route, G14's posture, B156's paper, F14's shape, B158's
support-with-specificity. Union suite at the close: parity 21/21,
verdict recorded below when the final run lands.

**Order 21 verdicts, sealing:** final union suite 4905/4905, exit 0;
next @093bf567 PUSHED; CI GREEN both platforms (the conclusion field
read explicitly, per the lesson); the v0.40.0 dry-run is CLEAN — ok on
ci.yml at the tip, 21 entries ordered (1 breaking, 2 miscompile, 3
feature, 15 tooling). The owner called nine entries light this morning;
the train now holds twenty-one, the released miscompile's fix among
them. One command away whenever the owner calls it.

## Order 22 — cycle 40: reactive foundations' groundwork, the prelude, and two FIX-NOWs (2026-08-30 → 08-31)

Eleven lanes plus a late FIX-NOW pair, two waves off next, integration
in the standing worktree; merged at 1497efa5. SHIPPED: THE PRELUDE
(B156's paper built same-order — real modules `std::prelude` (the base
seven) and `std::web` (+Signal/view/View, style and ui MODULE-CARRIED
per the ruling: a user writes `style::Display`); manifest key
`prelude =` on [package]/[library]; weakest scope, never inherited, NOT
synthesized imports — §9.2 holds; 16 aliases DELETED from std lib.vl
with `std::print`'s curated refusal naming both doors); B158
blanket impls by specificity (the owner's MaybeSignal pattern, the
union-type proposal's dissolution); a33's Source-widening of eight ui
bindings (the owner's charge verified whole — none of the eight wrote);
a31's uniform terminal-Closed (`close_for_good` sole writer, ruling
(b)); the pointer surface (Window handle, `listen`→Subscription,
pointer_x/y — kolt's drag workarounds die; A27+037); the watcher pair
G15/G16; b148's `+` admitted set (str+renderable deliberately NOT
B=Self — the i-string desugar rides it); fs-s5 (Reader + four
with_file forms — kolt.local 031 CLOSES WHOLE, the fs arc complete);
b163's pair (IfArms unification by match's rule; B164 supertrait
substitution); smalls (E103 3-door steer, E105, N32, N33, M14's
windowed compare 182,015→5); audit run 6 (24 findings; F2's web-steer
sending authors into broken programs FIXED same-cycle by dynamic
module-name exclusion; F3 non-nominal left operands → B170; the
symlink family → G17-G21; run 7 chartered for Order 24).

THE FIX-NOW PAIR (lane b166, off the owner's kolt reports): B166 —
struct-field assignment was ENTIRELY UNCHECKED; `Constraint::
FieldAssignment` routes it through the literal door's own rule
(`check_field_value` extracted, one rule both doors), estate census
149/149 via shadow-migrated copies, zero newly-refused. B167 — the
DIAGNOSIS WAS WRONG AND THE OWNER FALSIFIED IT: I claimed shadowing;
the owner renamed the binding and the new name errored too. Probes
discriminated the real class (closure-typed `is` captures never
emitted; i32 and match fine), the item was rewritten, and the lane was
REDIRECTED MID-FLIGHT — it confirmed discarding the dead theory before
writing code. Root: the `is_bindings` alias table had one reader while
locals become JS in two places; the named-callee fast path never
consulted it. The wrong-diagnosis lesson: a workaround claim is a
PREDICTION — test it before telling the owner.

PROCESS, confessed in full: b148 ran `pkill -f 'nextest run
--workspace'` and killed three sibling suites — the own-pid-only rule
now LEADS every brief. a33 left 113 armed wait-loops that kept
re-waking (disarmed by hand; one wait-loop max, disarmed at completion,
now mechanics). The std::print sweep deleted a test's own SUBJECT
import and the first restoration guessed wrong text into the wrong
test — third attempt fixed both, the reason comment now at the site;
sweeps must exclude fixtures whose subject IS the swept name. E103's
steer pins were retargeted twice (the prelude made Some ambient; then
audit F13 caught the retarget on the wrong door). fs-s5's red was
M15's load-sensitive perf gate, filed not fixed.

CLOSED here: A27, A31, A33, B148, B158, B163, B164, B166, B167, E103,
E105, G15, G16, M14, N32, N33; kolt.local 031 and 037. FILED: B166-171,
E106-E110, G17-G21, N34-N37, M15, M16, F16, B170, and b166's spec find
B171 (the `is`-binding scope sentence is FALSE in the spec — the true
scope wants a ruling). STAYS OPEN: B156 until the web templates adopt
(Order 23's lane), A32 (the paper's build IS Order 23's spine), B168,
B169. RULINGS BANKED: SignalCell; Trait::func resolves to the trait's
own default; `update` locked to SignalCell; [expose] reconciles against
`std::Source`; G19 symlinks a SUPPORTED spelling; the lucide pipeline
ruled IN ("I'd like to see what you build").

**Order 22 verdicts, sealing:** final union suite 5057/5057, exit 0;
CHANGELOG parity 40/40 at the merge tip; push + CI + the v0.40.0
dry-run recorded below when they land.

## Order 23 — cycle 41: the reactive arc built, the operator family closed, three gates minted (2026-08-31 → 09-01)

Ten wave-1 lanes + wave-2 reactive-replumb + two FIX-NOWs + the N21
solo slot; integration continuous (lanes merged as they landed, eleven
merges), final tip after b179. SHIPPED, the arc: B162 trait-associated
functions (Trait::func = the trait's own default body, ruled) + B161
constraint annotations (let-position, unify-then-meet, §12.2's
destructor hole shut by SEMANTICS) + B165 + THE REPLUMB — SignalCell
the cell, `trait Signal<T>: Source<T>`, update LOCKED to the cell,
Signal::new default-bodied, the clamping exhibit running through both
ui layers, [expose] reconciling nominal std::Source, MaybeSignal with
both blankets, AttrValue/Slot collapsed. Three general fixes forced:
trait-assoc generics bind from the call (B162's own pin was too weak
to catch it); bound-site calls no longer inherit context requirements
from same-named members on unrelated traits (MaybeSignal unshippable
without it); impl_select grounds a bound's binder before its
instantiation tier. THE OPERATOR FAMILY: B170 (the non-nominal-left
guard skip — closures concatenated their own source text), B169, B176
(FIX-NOW: the render-bound route BUILT, i-string + `+=` same hole,
never-silent guard), B179 (found by b176's lane, RULED by the owner
same day — membership in the left operand's admitted set, provable by
bound only where a trait names the set — and FIXED same day across
the whole native-left family). B168 (the undirected unifier). ALSO:
templates adopted the preludes (B156 ARC COMPLETE), the symlink family
under G19's supported-spelling doctrine, editor-health (E106's watcher
leak found via the owner's restart datapoint made rigorous, E107's
real cause NOT the line break, E111 fixed at the span source —
B167's shape again), diag-smalls, records (ledger current + THREE new
gates: diagnostics, appendix, EBNF — the EBNF gate found await/is
missing from the normative grammar), perf (M15 thread-CPU ratio: 5%
spread across loadavg 8→107; M16's 37 merged bodies, 124 corpus
programs byte-identical under node; M11 answered NOT-a-leak), N21
(clippy 217→0, audit clean, both CI legs), and THE LUCIDE PIPELINE in
the owner's kolt (1.38.0 pinned, 1791 icons, 4.3s clean build; the
reachability measurement — 645× — drew the owner's per-icon ruling
AND seeded M18, the owner's bundle-boundary attribute idea).

CI: the Order 22 tip's Windows leg RED — a REAL catch, not flake:
`import std::Default;` resolved case-insensitively to std's own
default.vl before the removed-alias steer; precedence fixed, the arm
unreachable on case-sensitive filesystems so the Windows leg IS its
end-to-end check. Every intermediate push superseded the previous run,
so the final tip's CI is the day's one completed verdict.

PROCESS, confessed: the integrator's own incidents this order — a
hand-union in generics.rs ate a pin's closing `);}` and the break rode
ONE PUSHED COMMIT because the targeted gates run after that merge
(split, corpus) never compiled the inference binary: after a
hand-union, compile the touched binary. A `cargo test` (not nextest)
targeted run raced the process-global leak tally and produced a false
red that cost a bisect: tally-bearing binaries go through nextest,
always. The close batch initially MISSED B168 — caught by the
changelog-vs-INDEX sweep (Order 19's lesson, now twice-proven); its
first run also half-executed before a stale assert, teaching
validate-all-then-mutate. Marker-eaten-at-merge recurred ~6 times
(repaired each time, parity checked before every add; families
verified against the lane branch when reinserting). The records
lane's suite hit the directory-watch talking timeout under 10-lane
load (STRIKE TWO for that pin across orders; a third earns an item);
perf found the free_port bind-release-rebind race (N40) — the fleet's
next flake family named in advance. The 1Password vault locked
mid-N21; the lane STOPPED per the rule, staged everything, and the
commits landed on the owner's unlock. One environment change disclosed:
rustup gained the Windows target so the M15 FFI arm could be
compile-checked for real.

CLOSED here (28): A32, B156, B157, B161, B162, B165, B168, B169,
B170, B176, B179, E107, E108, E109, E110, E111, G17, G18, G19, G20,
G21, M11, M15, M16, N21, N34, N36, N37. FILED (17): A35, B171 (O22's
b166), B172-B181's opens (B172-B175, B177, B178, B180, B181), E112,
G22, M17, M18, N38-N41. STAYS OPEN deliberately: E106 (instrumented,
the owner's next slow session decides), kolt.local 038 (built,
pending the owner's review+commit). RULINGS BANKED: B179's
operand-role semantics (the family's unifying principle), the bundle
call on 038 (per-icon spellings), M18 filed as the owner's idea.
OWNER QUESTIONS STANDING: B180 (the ruling's second steer is broken
until it closes — Order 24 top slot), B178 (parameterized main:
refuse or emit), B173 (may an abstract parameter satisfy a blanket
impl), B174 (the left-operand breaking step), the Optimistic type's
arity (paper §14.4), release.yml's gate carrying none of the three
hygiene legs, and THE CUT — the v0.40.0 train holds 72 entries.

**Order 23 verdicts, SEALED:** final union suite 5216/5216, exit 0;
next @6cec2321 pushed; CI SUCCESS on the final tip — both platforms
PLUS the maiden run of the new clippy and audit legs, five legs into
the required check, and the Windows leg's pass is the case-precedence
fix's end-to-end proof (the one completed CI verdict of the day —
every intermediate push superseded its predecessor's run). The v0.40.0
dry-run is CLEAN: ok on ci.yml at 6cec2321, all 72 entries sweep
clean and order (3 breaking, 13 miscompile, 14 feature, 42 tooling).
The owner's Order 21 condition — "cut after a work order or two" —
is met twice over; the cut is one command away on the owner's word,
with the website's std::print pair and art.vl's Signal drawings the
same-hour estate moves.

## v0.40.0 — SHIPPED 2026-09-01

Cut at d9532a9e (tag moved once, see below), release.yml GREEN all
legs + downstream publishes, 10 assets; folded to main (fast-forward,
main = the tag commit); site DEPLOYED and verified live (the homepage
renders the SignalCell drawing); toolchains 0.40.0 both locations
(~/.vilan from the release, ~/.cargo/bin from the tip). 74 entries:
3 breaking, 14 miscompile, 14 feature, 43 tooling.

THE ROAD TO THE CUT was three held gates, each earning its hold:
(1) E113 — the owner's persistent editor error was file-mode/LSP
coloring modules by default-entry; fixed by reachability, both
surfaces, vintage pre-Order-23 (the owner's own web-prelude adoption
exposed it by deleting the browser-evidence imports the old
inference keyed on). (2) B185 — the website migration's clean-build
gate caught `resolve_variable` grounding on an unfilled closure
parameter's Unknown — a MISCOMPILE (the dropped `__clone`, silent
sharing) hiding behind kolt's constraint-timing accident; 16 pins,
the brief's discrimination corrected on all four axes by the lane.
(3) The publish itself — GitHub's 125,000-character release-body cap
refused the 221,530-character section; fixed at the workflow (whole
entries to a 110k margin, family order guaranteeing breaking+
miscompile survive, pointer to the changelog for the rest), tag
moved pre-publication. The deploy then caught a fourth: examples.js
is GENERATED and the hand edit tripped its staleness gate — fixed at
the source examples, which surfaced K14 (a manifest-less playground
buffer carries NO prelude, so the seeded examples now teach
`import std::io::print;` — the owner's question).

ESTATE: kolt fully migrated (web prelude, module-carried style with
B172's type-position exceptions, interact.vl on the Window/
Subscription surface, store fields SignalCell) — check/build/probe/
lucide-e2e all green, client.js 64,447 B; website migrated minimal
(12 param renames, prelude sweep, art drawings) and live. PROCESS:
the chained-edit trap struck AGAIN (a failed python assert did not
gate the git chain; the changelog entry silently missed while the
tag moved) — the Order 22 sweep's sibling, now a RULE: an edit's
exit code gates the chain, or the chain does not run. The tag-move
was safe only because nothing had published; noted as the boundary.

Orders 17→23 and two cuts now ship in this chronicle's span. The
owner-question queue at rest: B180 (Order 24 top slot), B178, B173,
B174, B181, Optimistic arity, release.yml's bare gate, B183/B184
discussions, M18's paper trigger, K14's prelude door.

## Order 24 — cycle 42: the dispatch contract, the parameter sugar, the papers, audit run 7 (2026-09-01)

Thirteen wave-1 lanes + three FIX-NOWs (b188, b195, and rulings-smalls'
five same-day closes) + wave-2 audit run 7; integration continuous,
fourteen merges with hand-resolved conflicts in analyzer.rs (three
times), traits.rs (twice), document.rs, and the ledger tsv. SHIPPED:
B180 (the dispatch-path `B` check — the operator family's last door;
thirteen pre-fix miscompiles run), B172 (qualified type paths; the
templates' workarounds out), B186 (`fun f(x: Trait)` as the implicit
generic, owner-ruled the same morning — emits BYTE-IDENTICAL JS to the
written generic; `Optimistic<T, S>`), B175/B181/B177, B182 (the
cascade: provenance, per-entry dedup, roots first — 21 → 2), B188
(FIX-NOW: under-supplied type arguments ERASED — `seven1` through an
`i32`), B173 refused by ruling, B171 ruled AND the compiler fixed
(`||`-arm reads of absent payloads), B178 refuse + `process::args()`
(and `arguments`/`eval` missing from RESERVED_NAMES — a corpus golden
was unrunnable), A35, E119 (the overlay-naming note), editor-fixes
(E117 stale publish, E116 recolor — and a DEAD manifest-save sweep
found en route, E115, E118, E112, E114's unused-imports third),
hygiene (N40 first — the flake killed; N41; N39; N27's cross-check
whose FIRST run found the orphaned B126 pin; N28's residue; N38's
shared table; the three legs into release.yml), examples-adopt (ten
examples, byte-identical stylesheets), playground-prelude (K14 door
1 — with the filing corrected: the base set already reached buffers;
the web set + toggle were the gap; website branch k14 waits for the
cut). PAPERS: bundle-boundaries.md (door b through the shipped
`View.when`; two extremes that BREAK: nested boundaries — M20 — and
shared-goes-eager, 18 KB → 959 KB measured), trait-typed-fields.md
(HOLD the sugar, build the hole — B188, done), tuple-comprehension.md
(build in four pieces), the B174 census (ONE site).

THE LEDGER ROW-ID COLLISION: five lanes minted row 346 (b180, b172,
hygiene, b188, rulings-smalls) — assigned at integration 346, 347,
348-357, 358, 359-360, with B181's caught-unrowed 361. RULE MINTED:
lanes write `NEW`; the orchestrator numbers at merge. THE GATE'S
FIRST SIBLING CATCH: N41's hardened coverage check red-flagged
operators-tail's unrowed message at merge — exactly its job.

PROCESS, confessed: conflict markers SURVIVED into two pushed commits
(the tsv's trailing hunk escaped the regex; the seven ledger gates
were red on both) because the chain gated on git's exit, not the
gate's — strike three on the chained-edit rule, now spelled: THE GATE
GATES THE CHAIN. A traits.rs union guessed the wrong brace insert
(`}` where `    );\n}` was owed) — caught by the compile-the-touched-
binary rule, the Order 23 lesson holding. A gate named a nonexistent
test target; a clean merge's auto-commit made `git commit` report
nothing-to-commit and the `||` branch cried red — read the summary
lines, not the chain's tail. E114 shipped one third (unused imports)
as scoped; the declarations and unreachable-code thirds stay on the
item.

B195 (FIX-NOW #3): the negated `is` capture — a POLARITY PAIR carried
down the boolean spine, `!` a plain swap, no counter; two latent
unsoundnesses closed beyond the charge; B199 filed for the off-spine
call-argument case.

AUDIT RUN 7 (wave 2, tip b62c777b): thirteen findings. F1 HIGH — a
RELEASED miscompile: every native operator except `+` unchecked for a
bool/str/backed-enum LEFT operand (`true - 3` is a `bool` holding -2;
a `Level` matching no variant) — B196, FIX-NOW lane. F2/F3/F4/F5 —
three steers that lead INTO refusals (B178's `std::process::args()`
is a namespace path; B188's `Holder<S>` names a parameter not in
scope; the inherent-member steer vanishes on default-bodied impls):
the rule minted, A STEER IS A CLAIM AND THE PIN COMPILES IT — lane
audit7-steers. F6 — the Windows cycle guard's stop arm unreachable
(`canonical_path` never fails) + eight `#[cfg(windows)]` pin drafts —
lane audit7-windows, one landing EXPECTED RED under B198. F7/F8 — two
corpus goldens witness the OPPOSITE of their claims since c8609287
(run 5 fixed the third sibling without sweeping the file): rule
minted, A CORRECTED GOLDEN GETS A CENSUS OF ITS OWN FILE — lane
audit7-records. F9 — the "38 moved pins" was RECALLED from a commit
message; the close record's 51 was right (+17 added): the chronicle
re-corrected, and the rule sharpened — the derivation is the
authority, not the commit. F10/F11/F13 prose drifts. F12 → B197.
Steer census 14/11/3; operator matrix 216 programs, 78 wrong-running,
three roots; merge seams 0 lost / 0 invented across 20 files; the
estate sweep INCOMPLETE — lane estate-sweep. Run 8 chartered.

THE ESTATE SWEEP (audit 7's child + a duplicate lane, stopped): 366
snippets, 0 BROKEN, kolt and the website's own sources CLEAN — and
164 STALE fences on the LIVE docs site: 146 `import std::print;` plus
17 `Signal` field/return spellings. Not the sources (194/194 doc
fences compile clean at next) — the BOOK BUILD: last rebuilt
2026-08-29, v0.39.0's, because the v0.40.0 fold script REFUSED (next
had moved past the tag) and the hand-fold skipped its `docs.yml`
dispatch. Dispatched two days late; the daily cron was the safety net
nobody was watching. RULE: a hand-fold reproduces the script's
dispatches, and verifies a live fence. The two homepage panels
(art.vl, page.vl) were the only hand patches — same-line
substitutions so the depicted diagnostic's line numbers stay true.
Sequencing note for the owner: the rebuilt docs show bare `print`,
and the deployed playground compiles PRELUDE-LESS until the k14
branch ships with v0.41.0's `compile_with` — tour snippets won't paste
into the live playground until then.

THE AUDIT-RESPONSE MERGES: audit7-records (resource.vl's four false
claims repaired by adjusting the PROGRAMS, a `// witness:` corpus gate
built and proven by re-planting c8609287's exact shape — the byte
gate green, the witness gate red on all four; N44 filed for the
docs' own stale scope-end law), audit7-windows (F6's defensive fix
with the framing corrected in the code — pin 1 is a regression pin,
not a discriminator; eight `cfg(windows)` pins compiled clean for the
target; N45 filed: the ignored-pins backstop cannot see them),
audit7-steers (all three steers now COMPILE their spellings; the
sweep found row 88 held by no pin at all; rows 358/359 re-keyed).
Union on that tip: 5423/5424 — the one red the watch pin's 301 s
talking timeout at loadavg ~25, green alone in 0.7 s: STRIKE THREE,
N46 filed, the union's last named flake source.

b196 (FIX-NOW #4, audit 7's F1): the nine arithmetic/bitwise
operators now refuse a `bool`/`str`/backed-enum LEFT operand, the
admitted set named per type, per-shape steers pinned compiling;
census ZERO across 293 files and 390 fences; 48 of the audit's 216
matrix programs flip RUN→REFUSE, none the other way. Found: B200,
the unary `-` twin (`-true` is `-1` typed `bool`). The vault locked
at the merge commit — stopped per the rule, gates run unsigned,
resumed on the owner's unlock.

CLOSED here (26): B180, B172, B186, B175, B181, B177, B182, B188,
B173, B171, B178, A35, E119, E117, E116, E115, E118, E112, N40, N41,
N39, N27, N28, N38, B195, B196. FILED (26): A35→closed, B188-B200
(B189 cascade siblings, B190 qualified literal, B191 B126's orphan
re-owned, B192 partial generics, B193 trait-default self-op, B194
derive-erasure, B197 operator impl panics, B198 Windows case-fold
ruling, B199 off-spine capture, B200 unary minus), E120, M20-M22,
N42-N46. STAYS OPEN deliberately: E106 (2.2× shipped; M19/M21/M22
sized), E114 (one third), K14 (website branch parks for the cut),
B174 (census: ONE site — the owner's word), B183/B184/M18 (papers
recommend), C13/B149 (arcs). RULINGS BANKED: B178 refuse + args;
B173 refused; B171 the four boundaries + B195's negation; A35 name
the shadow; K14 door 1 + toggle; release.yml carries the three legs.
OWNER QUESTIONS STANDING: B174 (take it — one edit); b186's `&Trait`
acceptance; B198's case-fold; B197's operator-impl requirement; M18's
Q7 (M20 first — yes); the K14 sequencing (rebuilt docs paste into the
live playground only after v0.41.0 ships `compile_with`); the cut —
the train holds 37 entries with two released miscompiles fixed
(B188, B196).

**Order 24 verdicts, sealing:** final union 5437/5437, exit 0 (run unsigned on the resolved tree while the vault was locked); next @33692bb2
pushed; CI SUCCESS both platforms + clippy + audit (the first
uninterrupted run — every earlier one superseded by the next merge
push; the Windows leg's first real run of the seven live
`cfg(windows)` symlink pins — all green, pin 2's junction-reads-as-
symlink assumption HELD; the B198 pin correctly ignored); the vault locked at the last merge commit and the seal waited
on the owner's unlock, gates run unsigned meanwhile.

## Order 25 — cycle 43: the latency mandate, the operator tail, the ruled stragglers (2026-09-01, one day)

Opened on the owner's four answers to Order 24's queue (cut DEFERRED,
B174 "take it", the ruling queue accepted, the shape accepted) and a
new MANDATE: <10 ms per keystroke for tokens/hints/completion on a
large codebase, errors <500 ms — E121, an arc, paper first. Twelve
wave-1 lanes off the sealed tip 33692bb2.

THE PAPER (editor-latency.md, merged): E121's premise corrected — NO
request waits for the analysis (the five-provider burst is 15 ms;
diagnostics 1,111 ms). The real defects: every request RECOMPUTES
over the whole program (cost ∝ reachable functions — the 10 ms
budget is spent at ≈490, the 500 ms at ≈600), answers are UNMARKED-
STALE (one 409 ms window), superseded analyses NEVER CANCELLED.
Sequence N43 → M21 (analyzer.rs:40358, :40096) → M19's first tranche
(:4315/:4329) → M22 → cancellation; the KEYSTROKE PATH (§2.1) gated
on Q1. The owner ruled all six questions the same day (Q3 EXCLUDE
the debounce; kolt NEVER integrated into vilan's codebase — the gate's
exhibit is generated); the keystroke-path lane launched on the
rulings. Two mechanical finds → lane e122.

MERGED so far: docs-law (N44: 32 stale "scope end" sentences, two
fences that promised the reverse of their output — witnessed by
hand; N47 filed for an output-asserting docs form; destruction.md's
own §5 amended at integration), playground-steers (E120: the embedded
inventory + the toggle arm; the filing's removed-alias claim
corrected; rows 363/364 assigned at integration — N41's helper blind
spot, second family), m20 (call-site registry reads; the paper's D5
corrected — ReferenceError, not TypeError; no golden moved),
cascade-25 (B192: `call_substitution` RACED its three binding
channels instead of merging — the unwritten generic reached emission
abstract, over-long lists silently dropped, now refused; B189: three
provenance siblings — the unresolved-name arm, derive-templated
paths keyed on the refused SPELLING, `[expose]`'s two shapes keyed
on the element as rendered — the kolt-shaped fixture 4→2; B190: the
qualified struct literal, the last spelling off B172's type-path,
through parser, node, formatter, analyzer and the grammar; found
B201 derive-inside-mod and B202 rpc.vl's `_` placeholder), perf-25
(THE MANDATE'S FIRST CUT: kolt views.vl keystroke→diagnostics 2.04 →
0.91–1.14 s CPU — M19 tranche 1 memoizes the bound check on the
resolved Type, `checks` 2284→769 ms; M21 keys BASE_CACHE on the
entry's package root + sibling set, `base` 156–586 ms → 0.0 from
analysis 2; N43's phase labels honest with `dispatch-refine` a
deliberate slice; M22 makes `build --watch` decide with the HMR
round's own two functions — `Compiled client` + `Fresh probe` +
`Fresh server`, 2.31 → 1.55 s. FOUND, the new largest item: M23 —
M9's overlay rule refuses the store for an entry importing an OPEN
buffer, client.vl `base` 1.4–2.7 s every keystroke; M24 no eviction;
B203 the leg-skip set decided before any leg compiles), e114-rest
(the gray-out's last two thirds — and a REFRAMING the owner must
rule on: the language has no visibility marker, so a top-level item
is module surface a single-entry analysis cannot call dead; shipped
is function-local bindings + unreachable code via one shared
`Divergence` analysis (paint adds `panic` and the endless `for {}`);
both on the debounced path only, 118 → 6 ms after a per-file entity
fetch; 17 pins; E124 the single-entry-package question, N48 std's
own dead code, B204 panic-as-divergence), b174 (THE OWNER'S "TAKE
IT": an operator on an unbounded generic left operand is refused
with the bound named — 16 binaries + `&&`/`||`, supertraits counting
(std's `minmax<T: Ord>` rides `PartialOrd`'s `le`); the census
re-derived by hand, ONE live estate site in 482 traits; six pins
red-first with the pre-fix garbage run through emitted JS; a third
surface nobody priced — derive-generated `eq` over a `T` field —
exempted on the `DERIVED_SOURCE` boundary until B194), operators-25
(THE OPERATOR FAMILY CLOSED END TO END: B200 — unary `-`/`!` had NO
operand rule at all, `-true` was `-1` typed bool, `!Point{…}` false,
`-Level::High` a Level matching no variant; now an admitted set per
operator, stated not read off an impl, census zero, 15 pins; B193 —
a default's `self + self` was native JS on the payload, `Money{21}
.twice()` printed 2 and `self == self` was `===`, one defect in two
halves fixed on both sides of the analyzer/transformer seam; B197 —
the owner's "required at impl time": std's `panic("not implemented
yet")` stubs had satisfied conformance; 63 estate impls all
provide their method; breaking, migration "write the method".
13 ledger rows minted locally against already-assigned ids AND
mirrored as literals in the gate's hand-rowed table — the
integrator's mapping step; found B205 the explicit `self.add(self)`
spelling and B206 `b: PartialEq` in a steer).

hygiene-25 (N46 ANSWERED WITH NUMBERS: the CPU-clock direction
measured and rejected — a sleeping poll loop burns 1 ms/s whatever
the load, so a CPU deadline is a wall deadline in other units and
blurs starved from stuck; built the `wall-clock-waits` serial group,
38 pins, two of them found by its own anti-rot gate, two bounds
raised to 300 s (one had been GRAZED at 9.58 s of 10 on a quiet box),
106/106 green at loadavg 106–143; and the honest residual — the
recorded strike was a LOST WAKE-UP, round 2 never firing in 300 s
despite 15 re-touches, B208; N42's three inverse checks each
red-proved by removing the exemption's reason; N45 textual as
suspected, Windows clippy CLEAN after one cfg gate; B198's
canonical-or-fail on both sides of the containment test, the
Windows pin live but locally unverifiable; found B207 the LSP's
unsaved-buffer twin, N49 `release_differential` the 615 s critical
path, N50 three more exemption tables).

THE KEYSTROKE PATH (lane keystroke-path, E121 §2.1 as ruled): an
analysis captures its own tokens, hints, declaration-shape stamp and
symbol index ONCE on the analysis thread; a request re-serves the
capture through a two-sided edit anchor (a straddling span is
dropped, never clamped); the stamp is every lexer token outside a
body, so it survives a mid-keystroke syntax error. THE GATE PASSES:
release, generated 1,791-function exhibit (kolt never in the tree),
loadavg 42 — the replaced walk 1.104 ms, semanticTokens 0.004,
inlayHint 0.001, completion 0.592, the burst 0.828 ms against the
10 ms budget, asserted live against the walk it replaced. kolt
views.vl at four times the paper's load: tokens 12.2 → 0.30 ms. The
old "answer the analyzed snapshot" pin went RED and was rewritten to
the ruled contract — Q5 overturned it. What remains of the burst is
completion's per-module sweep (12 ms on kolt) — M25; the diagnostics
half of the mandate (500 ms) is M23 → M19 tranche 2 → cancellation.
A near-miss recorded: the index's first cut contributed every loaded
module's names at a scope position — 125 candidates became 3,144 —
caught only because the lane ran the kolt probe.

e122 (the paper's two mechanical finds: `semanticTokens/range`
computed the whole file then filtered per token — the 20-line
viewport cost 1.01× the file, now 0.006× through a per-analysis
stream with a line index, invalidated in the ONE place the analyzed
snapshot moves; `did_open` analyzed inline on the async handler —
open-then-request 1,271 → 8 ms once it schedules like every other
path; three pins had gone SOFT under the scheduled open — a leak
gate's twelve opens had stopped analyzing and its loop fell from
tens of seconds to 88 ms — repaired in the same commit; M26 filed
for the cancellation the paper sequenced last). Its merge collided
with the keystroke path by DESIGN, not by text — two per-analysis
token captures built in parallel from the same paper — so a fold
lane (e122-fold) reconciled them on its own worktree: one capture,
one invalidation point, the ruled architecture winning by
measurement.

STOPPED AT A RULING BOUNDARY — b194: the accepted rule (bound every
parameter under the derived trait, Rust's default) breaks C7's
shipped, pinned doctrine — std's `Handle<T>` is a PHANTOM subject,
and `impl Handle<type T: Wire> with Wire` would make `Handle<Session>`
un-sendable against "a name is not the thing it names". The lane
did not invent a second rule; it MEASURED the one amendment that
satisfies both rulings — bind a parameter iff the generated body
REACHES it, bare binder for a phantom (exact and syntactic in vilan,
which Rust's `PhantomData` forbids Rust) — 919/919 across the census
including the C7 pin, held everything uncommitted, and reported.
Family reclassified feature (nothing runs wrong today). The refined
form is COMMITTED on its branch (0a20b28a), unmerged, 8 pins each
claimed by a planted wrong rule, with the owner's question written
verbatim: accept reachability, or keep Rust's every-parameter
default and amend C7 — delete its pin and rewrite two doc pages to
say a handle's `T` must itself be Wire. The lane also corrected the
integrator: B189's covered set is diagnostic dedup on a different
axis and does not lift; b174's operator exemption does.

PROCESS, so far: the chained-edit rule broken TWICE by the
integrator on the same file (destruction.md's wrapped sentence) — a
commit message claimed an amendment that had not landed; corrected
in the next commit with the confession in its message. The shared
stash stack bit TWICE: m20's `pop` took e114-rest's stash, then
e114-rest's `pop` took e122's (one stack across every worktree of a
repo) — both recovered fully, by hash, nothing lost; RULE: lanes
never `git stash` while others run, a detached worktree or a
scratch copy is the baseline instrument — into every brief's
mechanics. The recolor pin
`a_package_import_edit_recolors…` red in two lanes' unions and
"alone" under 10-lane load, green alone at loadavg 86 in 13.8 s and
on CI — N46's family, the LSP harness's wall-clocked waits. THE
PRE-SEAL UNION on the ten-lane tip went 5565/5566, and the one red
was N46's own anti-rot gate doing its job across lanes: perf-25's
new watch pin file, written on a branch the group never saw, drove
a live watch session outside the serialized set — joined whole, one
commit. A gate written against rot within a branch caught rot
BETWEEN branches on its first union.

SEALED the same day at f261a90d: 12 lanes launched (one added mid-
order on the paper's rulings, one fold lane added at integration),
11 MERGED, b194 HELD on its branch for the owner's word. The final
tree's union 5572/5572 (the fold lane's run on the exact tree; the
pre-seal union one commit earlier 5565/5566 with the one red the
N46 gate's cross-lane catch), clippy, Windows cross-check and audit
green; CHANGELOG Unreleased 59 entries, parity 59/59 — THE TRAIN
IS NOW 59 ENTRIES, the cut deferred by the owner's word until "a
couple more of these issues" are fixed. Ledger rows 363–380 assigned
at integration (five lanes minted local ids, one against ids already
assigned, one mirrored as literals in the gate's own hand-rowed
table — the mapping step now a script). CLOSED 20: N44, E120, M20,
B192, B189, B190, N43, M21, M22, E114, B174, B200, B193, B197, N46,
N42, N45, B198, E122, E123. FILED 17: B201–B208, M23–M26, N48–N50,
E124, E125. OPEN QUESTIONS FOR THE OWNER: B194 (reachability vs
amend C7 — the lane's two-sentence question), E124 (top-level gray
in single-entry packages), B204 (panic as checker divergence), the
cut. The mandate's ledger after one order: the keystroke half MET
(0.83 ms burst on 1,791 functions; kolt tokens 12.2 → 0.30 ms); the
diagnostics half at ~0.9–1.0 s CPU on kolt against 500 ms, its path
sequenced M23 → M19 tranche 2 → M26.

ADDENDUM 2026-09-03 — THE SEAL'S CI VERDICT WAS RED, Windows only, two
tests, both Order 25's: (1) B198's new unit test probed "nowhere" under
a directory that exists in the caller's spelling, and Windows spells
the runner's temp directory as an 8.3 short name (`RUNNER~1`) that the
deepest existing ancestor RESOLVES to `runneradmin` — "the two agree"
was false exactly where the function's difference lives; the probe
now pins the resolved-anchor claim outright. (2) A watch pin the
Order 24 seal had green on Windows went red: a build hook's stamp
re-digested its INPUTS after the hook ran, so an input edited while
the hook's commands were still running was stamped as consumed and
the next round called the hook `Fresh` — a race whose window
Windows's slower `cmd` spawns opened on every run once hygiene-25's
serial group changed the pins' timing. Inputs are now digested before
the run, outputs after. Both at 53c3b8bf; CI GREEN there on all eight jobs, Windows included — the seal stands at 53c3b8bf. The
lesson for the record: a Windows pin the lane cannot run locally
(B198's) and a Linux-green race are the two shapes the cross-check
compiles but cannot see — the seal is not sealed until CI says so.

B194 LANDED 2026-09-03 at 635e3728 on the owner's word — reachability accepted over amending C7; union 5580/5580 at the merge; b174's operator exemption lifts in Order 26's first lane.

## Order 26 — cycle 44: the diagnostics half of the mandate, the ruled stragglers, four papers (2026-09-03 → )

Opened on the owner's rulings of 2026-09-03: B194 reachability
(landed at 635e3728), B204 `panic` is `never` through erasure, E124
no visibility markers (package-level union reachability + `[doc
(hidden)]`, paper first), B183 "a whole suite of monadic
transformations" (paper), B184's four cases and the `impl Trait`
noise question (paper), A37 `[gone]` filed unqueued. The cut stays
deferred (61 entries). Thirteen lanes off 635e3728 (CI green there): b194-landing,
b204, m23-m24, m26, m25-e125, cascade-26, bindings-26, watch-26,
hygiene-26, and four paper lanes — m19-paper, e124-paper,
b183-paper-2, b184-paper-2 — then a FOURTEENTH the same day:
b183-paper-2 landed within the hour (map and zip, nothing else — a
tuple body has n types, only a syntactic template can express it)
and found a released MISCOMPILE on the way, `for x in tuple` binding
`any` and discarding writes (B209), plus tuple receivers resolving no
methods at any arity (B210); lane b209-b210 builds the conservative
refusal now, the unroll waiting on the owner's Q2. Process rules carried from Order 25:
never `git stash`; ledger rows as NEW; Windows-only pins reported as
CI-verified; the integration helpers rebuilt after the scratchpad
was wiped by a session restart.

MERGED, in the order they landed:
- b183-paper-2 (tuple-comprehension revision 2: map and zip, nothing else — a tuple body has n
  types, only a syntactic template instantiated n times can express it; found B209 for-over-tuple
  binds `any` and DISCARDS writes, B210 tuple receivers resolve no methods; six §R8 questions).
- b184-paper-2 (trait-typed-fields revision 2: the language ALREADY decided the rule one level
  down — B161's per-binding locals and B186's parameters take an A and a B in one program — so the
  owner's case 4 is VALID and B184 is sugar over a hidden type parameter, byte-identical emission;
  revision 1's whole-program reservations stood against rule (a) only; dynamic is off the table
  (trait objects declined 2026-08-07, a value is a bare array); grammar bare, the LSP already
  paints trait vs struct in the same annotation position; BYCATCH two garbage runs through the
  reconcile arm trait-objects.md §1.4 called "the leak" — B211 — and duplicate declarations
  unrefused, resolving by declaration order — B212; four questions).

INTEGRATION acts: b194-landing merged first at 694dc142 (inference 3341/3341 under loadavg ~90).
The release script's family set extended at integration — Order 26's entries used `fix` and
`performance`, which the integrator's own briefs had invented; `rank_of` returned 0 and the cut
would have refused the whole section (m25-e125 caught it with `--dry-run`); releases.md §7.2 now
orders six ranks, the script and its fixture carry them, one tooling entry records it — landed in two commits because the first half-landed (see PROCESS).
m25-e125 merged at 3e7afcc8 on its LSP-side gates (588/588 across lsp/wasm/ide) after its own
union was stopped at loadavg 124 to free the box; hygiene-26 at abf2bec1 (its gates re-run once
after a wrong target crate). The release script's dry run on the real changelog then accepted
every entry's family, refusing only on its CI gate — pending, as designed. watch-26 merged at 4ca8e928
(the wall-clock group's 104 pins green in 185 s, Windows cross-check clean).
bindings-26 merged at fe02cff0 (inference 3370/3370, 672 s under load); m26 and m23-m24 queued
behind it one at a time — both rewrite the LSP's document and server files.
cascade-26 merged clean at 88f62c09 (its `NEW` ledger row assigned 381 in a separate commit — the
helper's clean-merge gap); the three remaining analyzer lanes folded behind it one at a time.
b211-b212 merged at 5e1afc7e after two fold corrections (rows 382/383; the ledger gate kept
cascade-26's shape); b209-b210 at cfb75c43 (row 384; its own gate variant dropped); b204 folded last
across B191's spec sentence — the same paragraph rewritten by both, unioned by hand.
b204 landed at 21848b3d after the semantic conflict; the ten performance entries relabeled at
620aeb35 (parity 87/87) so the train orders as one under the six ranks.
The pre-seal union on that tip, eleven code lanes and four papers in: 5855/5855, clippy, the
Windows cross-check and the audit all green, 483 s on a quiet box.
m26 merged at 72fee81a (one changelog hunk unioned with its marker restored, parity 75/75; lsp 561,
inference 3362, cli 79 green); m23-m24 merged clean behind it (parity 77/77).

PROCESS:
- b204's merge built red after a clean textual fold: a SEMANTIC conflict — bindings-26's guard
  check (B187) called the `Divergence::checker` constructor that b204 collapsed into one walk. Git
  merges text; the build is the gate that sees types. One line — and then the pin b187 had left
  `#[ignore]`d naming B204 ran for the first time and STILL failed: B187 decides the continuation
  binding while the body is walked, and B204's leaves are settled after the walk, so a panicking
  guard cannot yet bind. Two correct lanes, one seam neither could see from inside: B222, the
  pin re-ignored naming it, the spec's note retargeted rather than removed.
- The b211-b212 fold's first run refused its own plan over WHITESPACE: m26's cancellation macro
  indents the check sequence one level deeper than the lane's copy, so a literal line comparison
  called every call "new". Compared stripped, the plan held — one inserted call at HEAD's indent.
- The same fold then unioned a TEST FILE by line hunks — six alternating hunks that cut through
  function bodies — and produced a file with an unclosed delimiter. A test file with interleaved
  additions merges by WHOLE FUNCTIONS by name: the pre-merge file plus the lane's new pins
  appended entire, which is what landed. Two rules from one fold: compare stripped, merge tests
  by name.
- The rebuilt merge helper had a gap its predecessor never met: a CLEAN merge auto-commits, and a
  ledger row renumbered afterwards is staged with no merge message left to reuse — the follow-up
  commit aborted, the merge and the row both safe. Fixed in all three helpers the same hour: with
  no MERGE_HEAD, the integration commit writes its own message.
- Two gate specs named test targets that do not exist where the spec put them (`macro_std` under
  vilan-core at the b194 merge; `release_differential` under vilan-cli at hygiene-26's) — each
  stopped a chain after a clean merge and cost a re-run under load. The rule from Order 24
  ("verify target names") restated as a step: `ls crates/<crate>/tests/` before writing the spec,
  and the lane's own report names the binary its pins live in.
- The integrator's chained-edit rule broken AGAIN, third order running: a `;` placed after a
  dry-run inside a gated chain let the commit and push run after the fixture patch had failed
  its anchor — c93bfc2a landed the script's six ranks without the fixture or the entry, under a
  message that claimed both; corrected in the next commit with the confession in its message.
  The rule, restated: `&&` after every step, and an exit code you want to read goes into a
  variable, never behind a `;`.
- the scratchpad (session-specific) was wiped by a restart between Orders 25 and 26; the integration
  helpers were rebuilt from memory and self-tested before the first merge.

- e124-paper (dead-code-paint.md: the ruled definition taken literally grays 95.7% of kolt's
  top-level items — every type, since types emit no declaration used or not, and 1,815 lucide
  icons declared for 4 named; narrowed to `fun` + module-level `let` with three exemptions landed
  FIRST; per-entry sets computed out of band on a package clock because the LSP's entry is the
  open file and 9 of kolt's 12 files have no root; 16 true finds; five questions).

- m19-paper (per-module-analysis-reuse.md: NO rewrite — M21's cached world is cloned on a hit,
  so module entities already occupy a byte-identical id prefix; generalize the frozen-source seam
  to every cached source and REPLAY a package module's cached diagnostics; 83% of a warm kolt
  keystroke's analyzer CPU is one unchanged module; the key `(module × imports)` is wrong — no
  orphan rule, whole-program predicates, four passes run backwards; projection 330–420 ms then
  230–320 against the 500; found E126 the gate's exhibit misses kolt 178× on call substitutions,
  M27 `lsp-index` an unbudgeted 110–584 ms, M28 `plan_resource_drops`' whole-program switch).

- b194-landing (first code merge: b174's operator exemption on the derived-source boundary
  removed with a two-factor red-proof — removing B194's binder refuses the derived body, re-planting
  the exemption silences it again; a gap closed on the way: no pin had covered `[derive]` on a
  GENERIC ENUM, whose `PartialEq` writes `==` over payload bindings, a distinct path now pinned;
  B189's covered set confirmed dedup, not a bound; two stale Unreleased sentences amended in place;
  union 5581/5581).

- m25-e125 (completion's whole-program tables — 2,239 candidates walked to offer 20, a `read_dir`
  per request — captured once per analysis in a `CompletionIndex`: the exhibit's completion 0.63 →
  0.13 ms, kolt's burst 3.76 → 2.64, candidates identical at every position; the item's
  manifest-fingerprint cache deliberately NOT built — the server has no watched-files handler to
  hang it on (E127) and `modules_in_root` also feeds the compiler's own import steer; `range`
  through the anchor, pinned to agree with `full` byte for byte after an unlanded edit above the
  viewport; the union stalled at loadavg 115 — taken on its targeted gates, the pre-seal union
  covers the rest; found M29 the next completion slice and the RELEASE SCRIPT refusing the
  `performance` and `fix` markers this order's entries use — fixed at integration).

- hygiene-26 (N49's split found the union's 600 s: ONE corpus program, `watch.vl`, blocking forever,
  both builds killed at the deadline and the gate comparing two identical timeout strings — a
  verdict that could never differ, invisible under one shared clock; now one process per program
  with a two-way coverage gate, the binary's longest unit 607 → 14 s; N50's seven inverse checks,
  every table found clean, each red-proved by removing its reason; the seal's lesson written into
  CLAUDE.md in two sentences; found N51 — should the corpus hold a non-terminating program? — and
  N52, the infer differential's identical shape).

- watch-26 (B208 DIAGNOSED and it was NOT a lost wake-up: the watcher is a 300 ms poll with no
  event backend; the strikes were the hook-stamp race the seal fixed, unrescuable by nudges that
  rewrote identical bytes — reproduced twice, the alternatives eliminated with numbers, the Linux
  regression pin landed with a watcher trace; B203's producer-first leg schedule; B207 both sides
  through `canonical_path_of_unwritten`; G22 one identity per file in the walk; found B213 `fmt`
  walks once per root; union 5588/5588).

- bindings-26 (B199's miscompile: 'dropped off the spine' was the same `None` as 'no condition',
  so a capture in a call argument fell back to scope-wide visibility and printed `undefined` —
  narrowed instead of cleared; B187 as the owner ruled — the else-less negated `is` whose branch
  diverges binds the block, read from the FALSE-path set B195 already computed, codegen untouched;
  B191's inference deadlock; union 5609/5609; found two more accepted-then-throws — B214 `ret` in
  `main` is an illegal top-level `return`, B215 a bare `let b = x is Some(let n)` dangles — a
  sixteenth lane the same day).

- m26 (cancellation: a one-way token read from a thread-local, checked at every phase boundary
  and inside the two hot loops, every checkpoint downstream of every process-global store; a
  cancelled analysis answers `None`, never a truncated program — a draft that fell through
  panicked in the extraction tail; a 10-keystroke burst lands one analysis and cancels nine, per
  keystroke 6.0× cheaper on the exhibit and 7.8× on kolt; the mandate's diagnostics gate HOLDS
  on the exhibit at 52–59 ms CPU — and stays ignored, because E126 says the exhibit is not
  kolt, whose last keystroke is still 6 s of wall; a starvation hazard the design created was
  found and closed; union 5601/5601).

- m23-m24 (THE OVERLAY RULE: the stored base world shares the analysis's overlay copies by
  reference count — a claim per reader, `Arc::into_inner` the whole protocol, no second copy, no
  ordering rule, §7.9.2's five hazards each landing on a claim; both plants red, one of them the
  use-after-free surfacing as a wrong answer exactly as M9's own plant did; seven pins clean
  under AddressSanitizer in the adversarial shape; kolt client.vl's `base` 5 s per keystroke →
  0 on every round, CPU −30%; M24 a byte-budgeted LRU, 512 MiB, one eviction routine returning
  bytes and claims together; union 5586/5586).

- cascade-26 (B201 by PLACEMENT — generated items now carry the declaring module's path, the
  template untouched so B188's anchoring holds; B202 a refused exposure generates nothing, with a
  curated refusal added for the shape the skip alone would have made silent; B205's supertrait
  `Self` rebinding, gated off the parameterized clause where only the written name can separate
  `B` from `Self` — B216; B206 by the written name, B197's duplicate deleted; the ledger gate
  taught to hold a `NEW` row — the rule the briefs demanded, finally followable; union 5600/5600;
  found B216, B217 the `prepped_*` anchoring gap, E128 hover).

- b211-b212 (the paper's bycatch fixed the same day: a generic parameter is RIGID inside its
  own body — decided in one place from the constraint anchor's scope, asymmetric so a callee's
  binder still infers from a rigid argument, with an `inferable_generics` counterweight whose
  hardest case was the impl binder inheriting its subject's constraint id; six garbage runs
  refused, a CENSUS of 254 programs + examples + every fence + std with exactly one verdict
  change, and that one honest; B212 one declaration per name and a bound names a trait, `fun`+
  `fun` found to have RUN the second body; union 5607/5607; found B218 the display collision
  that is Q3's face, B219 the read-only twin that drifted).

- b209-b210 (the paper lane's miscompile refused the same day, with a steer that knows which
  spelling exists WHERE — positional reads on a concrete tuple, the comprehension on a mapped one;
  the `any` give-up narrowed so one broken loop reports once; census one hit, an iterators pin
  that had relied on the `any` binder; B210 by adding the tuple arm to the lookup and then finding
  two more nominal-only receiver sets one level below, the emitter's never-silent check catching
  the second; union 5597/5597; found B220, arrays have the same emission-side hole).

- b204 (the owner's ruling built: `never` already existed and already yielded — what disagreed was
  divergence, so the checker's and paint's two walks became ONE, with the two shape-blind leaves
  settled once per resolution and carried on the program; erasure removes only the diverging
  participant, so the surviving arm's mismatch still reports; a fixpoint-order bug found mid-lane
  — divergence had been read from a table that fills as calls resolve — fixed by a walk-time
  record; N48's `0 - 1` idiom deleted, and std itself is the pin; union 5592/5592; found B221).

- b214-b215 (the last lane, rebased onto the verified tip: `ret` in `main` as a labeled break —
  the function-wrapping alternative MEASURED at 115 of 124 goldens moved and rejected; the
  `js::Node` interpreter taught the new forms so the equivalence gate exercises them; a capture in
  expression position reaches its own expression and nothing after — and the filed symptom
  corrected: not a dangling name but a silently wrong value; two corpus programs had been written
  in the refused shape; union 5875/5875; found B223 — the `for` condition and the `match` guard
  have no polarity frame, the end state B215 stopped short of because it refuses programs that
  compile today).

QUEUED FOR THE OWNER: N51 (a corpus program that never terminates: keep, or a runnable
Watcher fixture?); M19's five (all-or-nothing per world; replay cached diagnostics;
the view-shaped exhibit; M28 filed; the index invariant as an assertion); E124's five (narrowed definition; withdraw-on-edit; library
opt-in via manifest; `[keep]` vs `[used]`; the free module-level slice first, and where it renders); B184's four (case 4 = consistency vs the two kolt sites the program-wide rule bought; the return position; how the hidden argument prints; bycatch first?); the cut (train 61+); B183's six §R8 questions (suite boundary;
unroll vs refuse `for x in tuple`; B209 in its own lane or the concrete arm's; `=>` tuple-only;
B210; flat_map's spread body); B184's revision-2 verdicts when the paper lands; E124's paper
questions; M19's paper questions.

SEALED 2026-09-03 at 289e2a2b (the lanes' tip 22e21d11 plus two integration commits): sixteen lanes launched (twelve at the
open, two the same day on paper-lane miscompile finds, one on the
integration's own miscompile bycatch, plus the four papers), ALL
MERGED. The lanes' tip's union 5875/5875 (245 s on a quiet box); clippy, the
Windows cross-check and the audit green; CI RED there on ONE Windows pin —
B207's `same_file` across two spellings of an unsaved path — whose
root was real: `canonical_path_of_unwritten` gave up at a `..` in the
unwritten tail and answered lexically while the plain spelling
resolved through the 8.3 temp root. The tail is folded before it
anchors, a symlinked ancestor is the Linux-runnable pin, and CI green
at 289e2a2b. Three seals running, three times CI has had the last
word over a green local union; three times it was a path spelled two
ways. CHANGELOG Unreleased 90 entries,
parity 90/90 — the train is 90 entries, the cut deferred by the
owner's word. Ledger rows 381–385 assigned at integration (the gate
now holds a `NEW` row, so lanes minted none by number). CLOSED 26:
N49, N50, M25, E125, B208, B203, B207, G22, B199, B187, B191, M26,
M23, M24, B201, B202, B205, B206, B211, B212, B209, B210, B204, N48,
B214, B215. FILED 22: B209–B223, M27–M29, N51–N52, E126–E128, and A37
unqueued. OPEN QUESTIONS FOR THE OWNER: the cut; B183's six; B184's
four; E124's five; M19's five; N51; B220. The mandate's ledger after
two orders: the keystroke half MET and its second tranche in (burst
0.10 ms on the exhibit); the diagnostics half moved by construction —
cancellation, the overlay rule, the byte budget — with the honest
number that kolt's last keystroke is still six seconds of wall and
the gate that says otherwise measures an exhibit that is not kolt
(E126). Three released miscompiles found by this order's own lanes
and fixed the same day (B209, B211, B214/B215); one composition gap
found at integration and filed (B222).

## Order 27 — cycle 45: the kolt-migration batch, the two ruled papers built, tranche 1 (2026-09-04 → 2026-09-04)

Opened on the owner's "Go" of 2026-09-04 after the kolt-migration
batch (27 points, seven read-only triage lanes, 24 items filed at
2a28613) and the owner's acceptance of E124's and M19's papers with
their five-and-five recommendations taken as defaults (E124: `fun` +
module `let`, withdraw-on-edit, no library key, no marker in v1, the
module-level slice first in the editor only; M19: all-or-nothing per
world, replay with the differential as the gate, E126 the gate's
prerequisite, M28 its own lane, the `Note.source` invariant an
assertion). Sixteen lanes off 289e2a2b (CI green there): b224 (TOP —
the `&&`/`||` short-circuit lost in codegen, a RELEASED miscompile),
b225-b219 (the struct-literal door reopening an impl's own rigid
parameter — B219's first live consequence), checker-27 (B226 entry
self-import, B227 `any` fills an inference hole, B228 zero-argument
arity anchor), divergence-27 (B222/B221/B223 behind a census),
context-27 (B229), cascade-27 (B216/B217/E128), editor-sync-27 (E132
linkedEditingRange in analyzed coordinates — CORRUPTING, its four-line
fix verified at triage; E133; E134; E127), completion-27 (E129–E131 +
M29), parse-fmt-27 (E135/E136/E137/B213), e126 (the view-shaped
exhibit + M27 measured), m19-t1, m28, e124-build, rpc-27 (A38/A40/
A41), std-27 (A42–A45 + A36), hygiene-27 (N52, N51 on its
recommendation). Held for the owner: B218 (B184's Q3), A46's form,
B220's direction, the cut. The integration helpers must be rebuilt
first (the scratchpad was wiped again between sessions).

MERGED (seventeen lanes, in the order they landed): e126 (8bcd63bf), context-27 (152e2451), b224 (940521ee),
hygiene-27 (51f3aa4b), editor-sync-27 (d8832db4), b225-b219 (9c5a4dff), cascade-27 (4e457bde),
checker-27 (8d881231), divergence-27 (0f034327), parse-fmt-27 (cddf0e75), m28, completion-27 (b536f4dd),
b230 (8d9ae5f9), rpc-27 (8009da18), e124-build (776e01ed), m19-t1 (2d9d93dc), std-27 (284998ed), and the same-day b239 (49b896d0) — the owner's evening report of seven errors in kolt's views.vl: B226's cycle refusal firing in FILE MODE, a regression this order introduced; an `EntryMode` flag, both front ends, the open-file entry taking the monolithic order.
Ledger rows 386–388 assigned (B226's two, E135's one); CHANGELOG parity 131/131.

SEALED 2026-09-05 at 49b896d0: union 6200/6200 (14 skipped, quiet box), clippy, the Windows cross-check and the audit green locally;
CI GREEN on all eight jobs (run 33932669444) after two Windows-only rounds on E127's pins and one fmt round. The order's own verdicts: a RELEASED miscompile fixed the day it was ruled (B224) and a
second found by that lane and OVERTURNED by its own lane the same day — B230's premise was wrong
(bare `?` is the expression lift, correct), the real defect an unchecked generic-variant payload,
fixed; an UNSOUND accept (B225) that was B219's first live consequence, fixed with fresh ids after
the restriction option was built and shown to break `map<U>`; the CORRUPTING editor bug (E132)
fixed in four lines; the mandate's number corrected — on a quiet box the 500 ms diagnostics
budget was already met at 289e2a2b (411 ms), M19 tranche 1 takes it to 367 with 57/57 modules
reused per keystroke, and e126's view-shaped exhibit reads 1,053 ms only under lane load; the
keystroke completion budget is a RELEASE figure that two lanes measured in debug (E141).
Forty closes; thirty filed (B232–B238, E138–E144, M36–M41, N53–N55, A47–A49, D6, B240 and N56 from b239, and L19 — the owner's CI-speed ask, queued for Order 28: a local gate script shared with ci.yml and rust-cache + nextest partitions; the Windows leg on the owner's own host);
M27's premise corrected in place; E121 annotated.

PROCESS:
- The rebuilt ledger helper deduplicated rows by message KEY across the whole file and dropped 26
  legitimate rows on the FIRST merge (rows that share a message under different ids); pushed at
  8bcd63bf, restored at 14ed3f7b within the hour, helper fixed to touch lane rows only. Rule: a
  merge helper never rewrites HEAD's rows.
- build_hooks' wall-clock-group MIRROR constant must follow every `nextest.toml` group join — it
  broke twice (E127's join, E124's join); the first was caught only by the NEXT lane's gate, because
  neither the lane's gates nor the merge gate ran build_hooks. Rule: any lane touching
  `.config/nextest.toml` runs `--test build_hooks`; the merge gate for an LSP lane includes it.
- Git interleaved two lanes' appended test MODULES in `vilan-lsp/src/main.rs` (linked_editing +
  watched_files vs dead_item_clock) and once the interleave compiled as an unclosed delimiter;
  resolved as the merged prefix (which carries the lane's clean non-test edits) plus each
  original's tail located by a 20-line anchor. Rule extended: test files merge by whole functions;
  test MODULES merge by whole modules from each original.
- The fold-by-name helper appended std-27's stale pre-N52 helpers into `release_differential.rs`
  (the lane branched before hygiene-27 moved them into the shared harness) and the core gate
  refused; repaired as HEAD's file plus the lane's three manifest rows. Rule: a lane that adds a
  corpus program after N52 adds the ROW to `corpus_harness`'s manifest, nothing to the differential
  files.
- parse-fmt-27's merge committed with a red gate and the next two merges pushed on top of it
  (the driver reported the failure but the chain continued); the red was the mirror constant
  above, fixed at 0d89f1b1. Rule: merge_fold stops the CHAIN on a gate failure (now `&&`-gated).
- Lanes shared one scratchpad and one lane read another's log as its own; briefs now name a
  lane-private subdirectory.
- checker-27 broke the "add whole test functions only" rule on purpose — two existing fixtures
  were written in the self-import form B226 now refuses — and said so.
- The seal's FIRST CI answer was red on `fmt`: the hand folds (the main.rs module-tail rebuild, the
  by-name test folds) left rustfmt drift that no local gate ran. Fixed with a rustfmt-only commit;
  the seal script now carries `cargo fmt --all --check`. Rule: every hand fold is followed by fmt.
- CI's SECOND answer was red on Windows only: two E127 pins — the runner's temp directory is spelled
  short (`RUNNER~1`), a document's package root kept that spelling, and `watched_sweep_root`
  canonicalized only the arriving path before `starts_with`; the sweep root was `None` and a deleted
  module kept being offered. The first fix canonicalized the ROOTS and did not help — the
  arriving file does not EXIST yet, so `canonical_path` fell back to lexical normalization and kept
  the URI's spelling; `canonical_path_of_unwritten` (B207's own function) is the fix, and a third
  CI round proved it. The THIRD seal in a row where Windows had the
  last word on a path spelled two ways (B198, B207, now E127): the rule stands — every path
  comparison canonicalizes BOTH sides, and any lane touching paths lists that comparison in its
  report. L19's step 2 (the Windows leg on the owner's host) is what turns this from a 35-minute
  round trip into a local gate.
- No stash incidents; no signing incidents; sixteen lanes plus the same-day b230, all merged.
