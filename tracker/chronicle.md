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
rerun follows CI.
