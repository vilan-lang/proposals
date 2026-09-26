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

## Order 28 — cycle 46: CI in five minutes, the context boundary, the rulings of the fifth (2026-09-05 → 2026-09-05)

Opened on the owner's "Go" of 2026-09-05, the day after Order 27's seal,
on the rulings of that morning: E142 no line-crossing `::` (import
aliasing as its prerequisite), N55 the fmt gate, E141 a profile guard
(release measures 0.04 ms against the 0.2 ms budget — the slowness was
the debug profile), E143 expand on rename plus the formatter's
shorthand, A49 inverted to `on_change`-required, B220 arrays join, B184
Q3 the hidden argument prints as `C<A>`, B242 (the owner's proposal:
`context` clauses on `fun`) accepted for a paper section and a build.
The cut HELD until the owner has tested kolt on 49b896d0. Thirteen lanes
off 49b896d0 (CI green there): l19-ci (TOP for DX — ci-local.sh shared
with ci.yml, rust-cache + partitions, the fmt gate, N57), context-28
(B241/B232/B242), rigid-28 (B233/B234/B235), checker-28
(B236/B237/B240/B220), b184-b218, std-28 (A49/A47/A48), rpc-28 (A39,
keyed deltas — the large one), editor-28 (E138–E141/E143/E144),
parse-fmt-28 (E142+aliasing/B231/B238/D6/the shorthand), perf-28
(M36–M39/M41/M27's fix half), m19-t1b (M40), compile-perf-28 (the other
session's M30/M31/M34/M35), hygiene-28 (N53/N54/N56). Held: A46's form,
B183's six. First integration act: the helpers committed to
`scripts/integration/` so they stop being rebuilt every order.

MERGED (fourteen lanes, in the order they landed): hygiene-28 (ce0eaac5), checker-28 (a9dcf2ea),
rigid-28 (b9da587d), parse-fmt-28 (c283ce7b), editor-28 (961b0a48), b184-b218 (b294101f),
context-28 (712128cf; its paper section into proposals main at 6a278cc), perf-28 (20c6ff80),
std-28 (7e0066ae), rpc-28 (8bb37b40), m19-t1b (7d2a3f7a), compile-perf-28 (fb3ba88f), l19-ci
(516173cc, merged LAST with its reformat regenerated over the merged tree). Ledger rows 389–399
assigned (next 400); CHANGELOG parity 178/178.

SEALED 2026-09-05 at 757d3f4b: union 6502/6502 (15 skipped) at 516173cc — the three commits after it are a harness attribute and two Windows-only pin repairs, clippy green on the tip, clippy, the Windows cross-check, audit and fmt green
locally; CI GREEN on all eleven jobs (run 34000577748), the first run with the cache and two partitions per OS: ubuntu 14 and 13 min, Windows 18 and 11 (25 and 30 before, and this run's cache was cold) — after one clippy round on a harness attribute and two Windows-only rounds. The order's verdicts: CI's own clock — the Linux legs verbatim in
`scripts/ci-local.sh` with ci.yml calling it, the cache and two partitions per OS, the fmt gate
after one reviewed reformat of 101 files, the modules differential in its own binary (L19 steps 1
and 3, N55, N57); the context BOUNDARY — B241's cascade rooted, B232's residual, and B242 built as
the owner proposed (`fun f(): T context settings`, the subset rule over strict reads, a wider
clause a warning, callers checked against the declaration, trait methods deferred with a message);
two UNSOUND accepts refused with zero-site censuses (B233 two rigid parameters on an operator,
B234 a rigid parameter as a condition) and B235's `= Self` default no longer a bound; B237 a
MISCOMPILE nobody had filed as one (an assignment beside a guard capture targeted a top-level
function and compiled clean); trait-typed FIELDS as sugar over a hidden parameter grounded per
literal with the `C<A>` display (B184/B218), byte-identical emission; `Source` inverted to
`on_change`-required (A49), a refused client told so on the only channel the host WebSocket
leaves (A47), the verifier bounded (A48); keyed deltas and per-key subscription over the wire
(A39: an edit 123,753 → 95 bytes, a leased key's later events 0; the `List<T>` macro form the
residue A51); tranche 1b restoring six class D passes per reused module (411 → 367 → 341 ms on
kolt's client leg); the other session's compile-time finds −26% Ir on a cold check with `check`
in parallel across entries; E138 a PHANTOM and B238's premise wrong, both said so; M38 measured
and withdrawn; `::` no longer crosses a line and imports alias (E142); rename at a shorthand
expands and the formatter canonicalizes the shorthand (E143). Forty-one closes; twenty-six
filed (B243–B254, E145–E149, M42–M44, M46, N58, A50–A52, L20); M27 narrowed, M36 designed,
E121 annotated; prose ledger rows 386–399 written, three of them Order 27's omission.

PROCESS:
- Lane m19-t1b ran a broad `pkill -f cargo-nextest` and killed sibling runs (checker-28's LSP
  gate re-run; perf-28's and context-28's whole-suite runs), then said so in its report; for a
  while it read as memory pressure. The own-PIDs rule stands; briefs restate it in capitals
  naming this incident.
- A FOURTH semantic conflict no build could see: std-28's `Source` inversion (a default `sub` calling
  the `on_change` requirement) met rpc-28's forward closures stored in plain `|| Subscription` fields,
  and `async_infer` resolved the default body's `self.get()` against EVERY same-named member — the
  `[service]`-generated async `get` colored `sub` async and std's own fields were refused; neither
  lane's tree had both halves. Bisected to the rpc-28 merge, fixed the same hour by lane a49-async
  (a default body's self call resolves against the trait's own subjects; B254 the sibling). Rule: a
  lane that turns a requirement into a default grep-lists the generic callers of that member.
- Three SEMANTIC conflicts git resolved textually and the build caught: E142's alias widened a
  shared tuple B236's collector destructured (patched at integration so the covered set carries
  the alias); E143's per-span rename edits versus parse-fmt-28's alias pins; perf-28's completion
  read-count pin versus the merged tree's zero reads (M39 over M29). Rule: a lane widening a
  shared tuple greps its destructurings; the build is the gate that sees semantics.
- The fold helper learned three things from one lane (b184-b218): carry a lane's NEW top-level
  consts (by raw-string terminator, not the next column-0 line — the first attempt truncated a
  fixture and swallowed the next one), and DROP the functions a lane deleted (a refusal the lane
  removed survived and failed); each committed to `scripts/integration/` the same hour.
- My own target-name miss (`--test docs` in vilan-cli) stopped rigid-28's chain once; the
  standing rule applies to the integrator.
- 1Password's agent went down mid-order: three lanes stopped at their commit or push exactly as
  briefed; their work was committed and pushed from their worktrees after the owner's unlock.
- Three lanes measured milliseconds under lane load and two items (M37, M38) were filed on wall
  readings; perf-28 restated them in callgrind Ir. Rule: perf items carry Ir or process CPU with
  loadavg, never wall.
- One lane authored commits with the gmail address and GitHub's email-privacy rule refused the
  push; rewritten to the noreply identity. Briefs name the identity.
- CI's first answer on the seal was red on WINDOWS ONLY, the fourth seal running: E140's cone pin
  compared the server's manifest directory (kept in the URI's short spelling, and the key of E124's
  package clock) against a canonical path — now canonical where it is discovered, with the package
  root beside it; and M27's entity-table pin PANICKED on a host with no thread CPU clock instead of
  declining the cost claim as the budget gates do — and once it declined, the same pin's cost RATIO
  failed on the Windows clock's ~16 ms granularity against a 0.014 ms table; a second commit
  declines the cost claim on Windows outright (the shape claims hold everywhere). The ubuntu
  partitions passed in 10–13 minutes on a cold cache (25 before). Rule restated: every path
  canonical at its source; a pin that needs a clock the host lacks, or finer than the host has,
  declines.
- The helpers now live in `proposals/scripts/integration/` (Order 28's first act); the scratchpad
  was wiped once more mid-session and nothing was lost to it.

## Order 29 — cycle 47: the rule 1 holes, the solver's unsound tail, the phase line's last slice (2026-09-06 → 2026-09-07)

Opened on the owner's "Go" of 2026-09-06, the evening of Order 28's seal, off
757d3f4b (CI green there). The order's seed was the owner's kolt find of the
same evening — a `remove` through `SignalCell::update` throwing from
`reconcile` — which turned out to be std keeping the live list under an
in-place mutation (B255) over two rule 1 holes: `Shared::read()` handing out
storage (B256) and ASSIGNMENT from a live aggregate never copying (B257, a
miscompile the spec's own example exposes rewritten as an assignment). Twelve
lanes: rule1-29 (TOP: B257, B256 under the default ruling that a read result
is a PLACE, B255's pins), solver-29 (B251 unsound, B245, B246 census-first),
checker-29 (B244/B252/B243/B254), smalls-29 (B247/B249/B248 refuse-with-steer/
B250 per leg), editor-29 (E145's alias entity, E148, E149), fmt-29 (E146/E147
plus E145's collapse, merges LAST with its reformat regenerated over the merged
tree), rpc-29 (A52, A51 as `[expose(keyed = K)]`), m19-t1c (M42), perf-29
(M43/M44/M46/M47 splice), compile-perf-29 (the other session's M32/M33, skipped
if taken), m36 (World serialization behind a flag — the largest, droppable),
hygiene-29 (N58). Rulings the lanes run on: B256 place treatment; B246 close
on a clean census; A51 the attribute argument; E145 preserve, collapse, extend;
B250 refuse per leg with a note on the remap; B253 keep the refusal, no build;
A50 close as designed. Held: the cut (until kolt is tested on 757d3f4b), A46's
form, B183's six. L20 is the owner's own. Two owner topics queued for after the
launch: CSS block syntax / compact styling, and complex rpc signal tracking in
kolt.

MERGED (twelve lanes, in the order they landed): hygiene-29 (ce45efbf), m36 (02cc1663), checker-29
(7954e76f; B244 relabeled miscompile at 8b6fe23d), m19-t1c (1987354d), smalls-29 (4ca53bf9),
rule1-29 (69fbfe59, the reactive-flatten golden regenerated), editor-29 (37512be8), solver-29
(f1253961, two folds then fmt), rpc-29 (a96fb519; the ledger repaired at 68e0bf26), perf-29
(a1a224ac; analyzer, census and list-splice golden by hand; the split golden regenerated at
a145993c), compile-perf-29 (37ce54fc), fmt-29's seven rules (6cedfe36) with the reformat
regenerated over the merged tree LAST (637cc4d7: 81 files, lines over 100 columns 150 → 107).
Ledger rows 400–404 assigned (399 edited in place; next 405); CHANGELOG parity 221/221.

SEALED 2026-09-07 at a5473227 (637cc4d7 plus one seal repair: a pin's attributes restored, M46's reason named): union 6665/6665 (23 skipped) at a5473227; clippy, the Windows cross-check, audit and fmt green
locally; CI GREEN on all eleven jobs (run 34143208240: ubuntu 15 and 13 min, Windows 18 and 15; the first round at 637cc4d7 was cancelled by the repair push). The order's verdicts: the RULE 1 HOLES — assignment from a live aggregate
copies (B257, a miscompile whose root was a bare local read interning no type; the same root
fixed `List::insert`, `Arena`'s slot writes, `SignalCell::set` and the iterator folds), which
alone closed the owner's kolt crash (B255, no std change) — and B256 built, measured and HELD
(+12–25% CPU on the reactive pins, +344% on a raw `get()`; a cell-aware last-use elision, B267,
is the way through); the SOLVER'S UNSOUND TAIL — B251's struct-parameter accept and B246's
bounded-operator hole both refused on zero-site censuses, B245's Mixer program compiling end to
end with B216's workaround deleted; B244 a silent MISCOMPILE nobody had filed as one (one
emission shared across instantiations); the DROP PLANNER restored per module with its premise
corrected by measurement (M42: the cost was the enrolment gate, no type crosses; 154 of 3,398
bodies walked), and R10 named as the next largest line (M48); World SERIALIZATION shown
infeasible by four address-keyed structures and M36 reframed as a suite-wide floor (~31% of
vilan-core's suite CPU); the parser's `Node` boxed 320 → 144 bytes and the macro worlds on the
phase line with an on-disk expansion table (−10.7% Ir on a warm kolt check); `remove`/`insert`
over `splice` with the panic kept; the base cache's under-construction claim and byte budget;
the formatter's seven rules and the chain break; an import alias as an entity of its own
(rename preserves it; an alias of a different length had NO references at all); the mirror as a
`Source`, a 503 arm, `[expose(keyed = K)]` with the incremental diff measured and rightly
declined (A54). Two premises overturned in print: B247 (a plain string has no holes — the
adjacent malformed-hole gap fixed instead) and M42's. Thirty closes; twenty-six filed (B258–B267,
A53–A56, M48–M53, N59–N63, E150); B256, M36 and M19 carry status updates; prose ledger rows
400–404 written, row 399 reworded, row 229's site note corrected.

PROCESS:
- The fold helper counted braces per line without regard to string literals: a raw-string pin
  with an unbalanced brace ran its "function" to EOF, and the first lane to append to the file
  (smalls-29) read as having edited it. Fixed the same hour (string-aware scanner, verified on
  the three real versions); a helper that reads Rust test files is string-aware or it is wrong.
- The ledger renumber treated a lane's EDITED row 399 as a new row and orphaned HEAD's — the
  `every_indexed_row_still_lives_in_the_tree` gate caught it after the merge committed. Fixed at
  the root: an existing id with changed text is an edit decided against the merge base (env
  overrides for dry runs); verified on the real three-way ledger before the repair.
- The fold's glob took a `.tsv` under tests for a Rust test file and overwrote the copy-elision
  census with HEAD's copy; regenerated by the census's own switch over the merged goldens (305).
  The fold folds `*.rs` only now.
- Two goldens two lanes moved together were regenerated from the merged tree (reactive-flatten:
  checker-29's renumbering + rule1-29's three clones; the SPLIT golden: rule1-29's six clones in
  the cell setters + checker-29's pruned `sub` default, which no lane gate had run). The split
  binary is a default merge gate now.
- My own target-name misses, three: `corpus_harness` in several briefs (the binary is `corpus`),
  `std_surface` and `module_resolution` at gates (vilan-core inference modules). The merge helper
  validates every `--test` name against the crate's tests directory before it merges anything.
- Two hand folds left rustfmt drift (solver-29): caught by the helper's fmt check, amended.
- m19-t1c's analyzer change (`drop_roots` in a flat count) met perf-29's byte estimate of the
  same count — predicted in the notes at m19-t1c's merge, resolved by hand at perf-29's.
- Lane rpc-29 deviated from its brief's conditional (build the incremental diff if the cost
  grows) and reported instead, with the reason (the O(N) scan is irreducible for a List-valued
  source): the right call, recorded as A54. Lane m36 likewise stopped at the spike.
- The reformat lane kept its tree-wide reformat as a separate final commit, and it was dropped
  and regenerated over the merged tree with the merged compiler — the pattern held.
- No `git stash`, no pattern kills, no 1Password outage this order. Every sweep artifact was
  written to the repo as it happened (notes29.md), nothing to the scratchpad as a record.

## a65 — a single lane between Orders 29 and 30: module directories (2026-09-07 → 2026-09-08)

Opened on the owner's "Go on A65 as its own lane now" of 2026-09-07 off a5473227; one Opus lane,
three commits (cd2ff4c5 core, 8e08af4e editor, 7e5db561 spec/docs). MERGED at 0a2ab908, ledger
row 405. SEALED 2026-09-08 at f0f4e301 after one repair — the new `module-dirs` corpus golden had
no row in the copy-elision census (zero copies, total unchanged); union 6690/6690, clippy, the
Windows cross-check, audit, fmt green locally, parity 224/224; CI GREEN on all eleven jobs (run
34175510571; the first run at 0a2ab908 was red on partition 1 of both OSes for the census). The
verdict: a package's modules may live in directories under Rust's rule — `a.vl` or `a/lib.vl` is
the body, `a/b.vl` is `a::b`, a bodiless directory is a namespace whose refusal names its
children; submodules are NOT brought into scope by a parent import (pinned); the editor knows
the tree. One close (A65), three filed (A67 the item-versus-file collision ruling, E152 the
namespace's nowhere-to-point, N64 three doc notes). Kolt's `lib/` move follows on the sealed tip.
PROCESS: my CI watcher twice looked for the run before GitHub had created it and watched
nothing — the run id must be read after the push has propagated, not after a fixed sleep.

## Order 30 — cycle 48: the miscompile, the rule 1 landing, the css block made usable, the rpc paper (2026-09-08 → 2026-09-08)

Opened on the owner's "Go" of 2026-09-08, off f0f4e301 (a65's sealed tip, CI green there).
Fifteen lanes: b258 (TOP: the default-override miscompile through an inherited field), rule1-30
(B267 the cell-aware last-use elision, then B256 landed on the numbers), css-30 (B270 first —
the block seeds a bare `style` and fails under the web prelude — then the paper section and
A68 auto-const / A69 chain links / A70 the hole prelude / A34 / E153), rpc-paper-30 (transport-rpc
§9 from the owner's three points: per-connection mutable state, return-typed signal handles,
client-declared functions; A53–A56 fold in; paper only), view-30 (B268 the `Child` trait,
A66 `toggle_attr`, A60's `View::show` no-op on flex containers), std-30 (A57/A58/A61/A63),
dom-30 (A59/A62), solver-30 (B261/B262/B263), smalls-30 (B259/B260/B265/B266), editor-30
(B264 per TypeScript, E152, B269, B271), fmt-30 (E150/E151, LAST), m19-t1d (M48), perf-30
(M49/M50/M52/M53), build-30 (M51), hygiene-30 (N59–N64). Rulings in force: A67 the ambiguity
error; `.hover` stays, `:hover` gets a steer; the `Child` trait before any `View`-as-trait
decision; the rpc proxy injected through `Connection`. Held: the cut (kolt under test), A46's
form, B183's six, M36's fork harness, A64 (rides css-30's paper section).

MERGED (fifteen lanes, in the order they landed): rpc-paper-30 (12b3b75d; proposals only, transport-rpc
§9 with rulings R1–R7 and R-A38b), dom-30 (3ab3004d), b258 (46e4c400; the mdBook golden regenerated
above it), hygiene-30 (2f99e32d), std-30 (78f696d0; the golden again), build-30 (c9e238eb; macros.rs
resolved by hand — N63's path move under M51's per-flush temp), editor-30 (f2b9ce9f; the DOM stub
hand-unioned, its `find()` brace restored), rule1-30 (c517395f; the copy-elision census regenerated,
322), solver-30 (4bef4ead), m19-t1d (a85370ca; a duplicate `Event::target` removed), smalls-30
(3c161046), view-30 (3a1cdea6; `ui_rows.rs` rebuilt function-level from the three real versions),
perf-30 (2db51d7a), css-30 (9d3a8d86; `RULE_STATEMENT_SITES` 20 → 21), fmt-30's rules (dc39bf75) with
the reformat regenerated over the merged tree LAST (88147380: 6 files, lines over 100 columns
107 → 105). Seventy-one commits, 116 files, +14,192/−1,005. Ledger rows 400–406 assigned (132 and 355
edited in place, 360 deleted; next 407); CHANGELOG parity 270/270.

SEALED 2026-09-08 at c3ed9239 (88147380 plus one seal repair: the LSP's add-import quickfix pin
re-aimed at the `View` type, because B270 made the element head hygienic and no lane gate ran
vilan-lsp): union 6847/6847 (21 skipped) at c3ed9239; clippy, the Windows cross-check, audit and fmt green locally;
CI GREEN on all eleven jobs (run 34246342479: ubuntu 16 and 14 min, Windows 19 and 18; the run at 88147380 was cancelled by the repair push). The
order's verdicts: the MISCOMPILE — B258's silent `undefined` through an inherited field had its
root in the context pass (`known_receiver_candidates` shared across receivers), fixed with the
default override emitted and the miss REFUSED rather than emitted (B279 asks for the structural
guard); the RULE 1 LANDING — B267's cell-aware last-use elision put B256's place treatment within
noise on the reactive pins, so `Shared::read()` is a place and storing one copies (B274 found the
docs' `read().push` promise unmet — an owner ruling); the CSS BLOCK MADE USABLE — B270's hygienic
seed (`Node::StdItem`: the block means `std::style::style` and an element `std::ui::view` whatever
the scope holds, neither needing an import), the auto-`const` (A68), chain links (A69), the style
prelude ambient inside a block (A70, itself an A65 module directory), typed holes through `piece`
(A34) and the `:hover` steer with a versioned CSS property index for completion (E153); kolt's
`button_style_base` 392 → 260 characters; A64 ruled in §15 (`.when` for a rule-set change, CSS
variables for a value change); the RPC PAPER — §9 answers the owner's three points with the
per-connection instance that already exists (A38's factory), return-typed signal handles as the
unbuilt half of §8, and client-declared functions; the sketch's `&mut self` REFUSED by the
generator and `mut self` silently losing writes is B272; the CHILD CONTRACT — a `Source` of `str`,
`View` or `List<View>` may be a child (B268's root: bound arguments dropped at impl matching),
`toggle_attr` for boolean attributes (A66), `show` writing inline display (A60); std and dom grown
by kolt's externs (`Storage` typed, `Event::code/target/current_target`, `parse_bool`, `Debounce`,
`DomRect`, `PathParts` with `FromPath`) so twenty-one hand-written externs and three FIXMEs can
leave kolt; the SOLVER — B261/B262/B263 with the diagnosis of B263 corrected in the fixing, and an
UNSOUND impl `with` clause found unchecked (B273); the EDITOR — an alias in type position renames
alone (B264, per TypeScript), the namespace's nowhere-to-point (E152), `autofocus` retried across
frames (B271); the FORMATTER — `for`/`match` heads split (E150) and the element-head attribute
sorter (E151) with its evaluation-order bargain stated (E156, an owner ruling); PERFORMANCE — R10
in the Class A window (M48: 153,302 → 24,459 sites, kolt keystroke thread CPU 280–340 → 60–70 ms),
tiered legs (M51: kolt wall 23.8 → 15.7 s), M53's −8.2% Ir cold and −12.9% warm, M52's union key
measured and REFUSED (the browser leg is 82% of base — M55 names where the headroom is); HYGIENE —
N59–N64 done (caches under `dist/.cache/`, N61's wall-bound sweep, the ledger's rule-site count).
Forty-four closes; twenty-eight filed (B272–B280, A71–A73, E154–E158, M54–M59, N65–N69); M19 and
A53–A56 carry status updates; prose ledger row 406 written, rows 132 and 355 edited.

PROCESS:
- The seal found what no lane gate ran: B270's element hygiene killed the LSP's only pin of the old
  element-import behaviour, in a package (vilan-lsp) outside css-30's `--test` list and outside
  its whole-suite run's timing. Rule: a lane that changes WHAT a diagnostic fires on runs
  `-p vilan-lsp` too (the quickfix and steer pins live there); the merge helper's gate list is per
  lane, and the seal's union is the floor.
- The mdBook golden went red twice (dom-30's routing section under b258's merge; hygiene-30's
  reserved-words section under std-30's) — the merge helper now regenerates it for any merge that
  touches `vilan/docs/`.
- The merge helper's target validator refused a lane-added binary (hygiene-30's
  `reachability_and_depth`) and then my own wrong crate for `release_emission`; it accepts files on
  the lane branch now, and the crate table is in the mechanics block.
- Two hand unions of `ui_rows.rs`'s DOM stub: the first dropped `find()`'s closing brace (the hunk
  cut mid-method) and redded every ui_rows test with a JS SyntaxError; the second (view-30) broke a
  delimiter and was rebuilt FUNCTION-LEVEL from the three real versions with the fold helper's own
  extractors. Rule: `node --check` of the extracted stub before the amend; an edited shared CONST
  is a hand union, never a fold.
- Two lanes given overlapping members in one file (dom-30 and std-30 both declared `Event::target`
  in dom.vl) merged cleanly and failed the full-scan pin; a named owner per member in the brief.
- css-30's 21st curated rule met hygiene-30's rule-site count (20): the pin doing its job; a lane
  adding a parser rule statement bumps `RULE_STATEMENT_SITES`.
- The copy-elision census conflicted a third order running (rule1-30): regenerated over the
  merged tree, 322.
- My CI watcher looked in the proposals checkout for a vilan run (a persisted cwd) and missed a
  run that appeared after its first two minutes of polling; the watcher pins the repository and
  reads the run list until the id appears.
- No `git stash`, no pattern kills, no 1Password outage this order. notes30.md is the record.

## Order 31 — cycle 49: the rpc order (2026-09-09 → 2026-09-09)

Opened on the owner's "Go" of 2026-09-09, off c3ed9239 (Order 30's sealed tip, CI green
there), on the owner's framing of the day: "improving the rpc system — the last feature
blocking a functional system in kolt." The design is transport-rpc §9 (rpc-paper-30's), and
the owner ruled its list the same morning: R1 `[service(X, client = H)]` + `[client_service]`;
R2 `[expose]` stays as sugar with its hash entry verbatim; R4 notifications only in v1 with the
receive-loop fix landing now; R5 no `bind_each` sibling; R6 refuse the keyed-map mismatch, keep
429; R7 a source-returning method is a getter by declaration; R-A38b (a) the generator honours
`&mut self`, plus `mut self` refused. R3 the owner REVERSED from the paper's explicit
`Release` frame to demand-decides, out of their own SolidJS auto-dispose experience (the
unmount-then-mount window inside one tick): lease-zero defers to the turn's settle and then
one microtask look; an `Unsubscribe` on a dynamic channel is a revoke; a re-acquire re-mints
from the mirror's `origin`; a never-leased handle goes with its ambient owner; no new frame —
the origin field closes A41's long-gap remount, which was the paper's reason for the frame.
Five Opus lanes: handles-31 (TOP: A74, the plain half of §9.2 with R3 as ruled and R7),
reverse-31 (A75 + B281 the receive loop), mutself-31 (B272), keyed-31 (A54 `KeyedCell` + A55's
`Source` impl; droppable; the keyed RETURN mapping deferred to the next order), rpc-smalls-31
(A56). An ownership map splits rpc.vl's generator three ways; two hash pins in every generator
lane keep kolt's shipped services connecting through the order. The paper edits, the closes
(A53 answered, A54–A56, B272, B281) and Q9's amendment are the integrator's at the sweep; the
kolt migration (store.vl's three TODOs plus Order 30's 23 collision errors) follows at the
owner's word after the seal. Briefs: `scripts/integration/sweeps/order31/briefs31.md`.

MERGED (five lanes, in the order they landed): rpc-smalls-31 (09d8e78a), mutself-31 (f53d999c),
reverse-31 (f139af8a; three append-append conflicts by hand — both new analyzer fns, both guide
sections in order, the anchor golden regenerated), handles-31 (4962ce93; the generator's route and
stub hunks composed by hand: `route_outcome` takes the replier, the notification arm ahead of the
handle arms; one missing brace cost a 122-red gate round before the amend), keyed-31 (cc2a49b1;
the channels test file folded by name, nine fns and five consts; one semantic clash git merged
textually — `Capability.dynamic` missing at the keyed-cell export — fixed by one field), and one
integrator docs commit (65af4be0: the interleave caveat, B287). Twenty-two commits, 26 files,
+6,074/−322. Ledger rows 407–411 assigned (next 412); CHANGELOG parity 283/283.

SEALED 2026-09-09 at 65af4be0: union 6872/6872 (22 skipped); clippy, the Windows cross-check, audit and fmt green
locally; CI GREEN on all eleven jobs (run 34383623175: ubuntu 16 and 16 min, Windows 19 and 20). The order's verdicts, against the owner's
framing that rpc was the last feature blocking a functional kolt: PER-CONNECTION MUTABLE STATE —
the generated dispatcher declares `mut self` and the routes capture the binding, so `&mut self`
writes the connection's instance in place (B272), and `mut self` is refused so the silent loss
cannot recur; the owner's `is_authenticated: bool` sketch compiles as written. RETURN-TYPED
HANDLES — `fun get_message(id): SignalCell<MessageBody>` reaches the client as a
`RemoteSource<MessageBody>` minted from a channel id, with the demand-decides release rule the
owner reversed R3 to: a hundred handles cost ten forwards, a released one is revoked and re-minted
from its origin with the cached value painted first, a never-leased one goes with its owner, and
the order added zero wire frames (A74). CLIENT-DECLARED FUNCTIONS — `[client_service]` on the
browser struct, `client = H` on the server's, a typed proxy through the connection, one reverse
lane, notifications only, and the receive loop no longer serializing a chunk's frames (A75, B281,
red-first). THE KEYED PATH — the delta cell takes a change from 12× growth over 10× rows to 1.3×,
and the client's apply path was the bigger half (A54); the keyed mirror is a `Source` (A55); the
keyed-map mismatch is refused at the attribute and 429 stands well-founded (A56). Eight closes
(A53 answered, A54, A55, A56, A74, A75, B272, B281); fifteen filed (B282–B287, A76–A81, E159, M60,
N70). Rulings the lanes left for the owner: the microtask hop's scope (dynamic-only as built, or
every mirror at the cost of four A25 pins); the keyed per-key hop; B287 (an awaiting `&mut self`
handler may now be interleaved — refuse or document); same-module handlers only; an awaitable ack
for a void method's forward stub; bare `[expose]` over a `KeyedCell` as the keyed channel.

PROCESS:
- No SendMessage in this build: a running lane cannot be steered. mutself-31's two items for
  reverse-31 became merge-time checks (the `mut self` guard on `[client_service]` came free
  through the shared arm; the interleave caveat was one integrator sentence). Rule: brief for
  the interaction up front, or plan a merge-time check.
- The merge validator refused a multi-file test target (`tests/inference/main.rs`); it accepts
  that layout now. Attribute refusals pin in vilan-core's `inference`, wire behaviour in
  vilan-cli's `service_layer` — in the mechanics block.
- A hand-composed generator block came out one brace short and the whole `[service]` macro
  failed to parse: 122 red, the HMR pins burning 300 s each. Rule: brace-count and smoke-compile
  (`--test examples`, 15 s) before the gates — the DOM-stub rule again.
- Two lanes added a field and a construction site to one std struct; git merged it textually and
  seven keyed pins went red on "`Capability` expects 3 fields". Rule: grep every `Name {` after a
  merge that touched a struct's shape.
- The lanes' scratchpad is shared: keyed-31 read mutself-31's probe file. Lanes namespace
  scratch by lane name.
- A heredoc terminator ends an `&&` chain; the GO commit went through with an INVALID spec once.
- One ssh timeout to GitHub on a proposals push, retried clean. No `git stash`, no pattern kills,
  no 1Password outage. notes31.md is the record.

## Order 32 — cycle 50: the kolt-findings order (2026-09-11 → 2026-09-11)

Opened on the owner's "adjust order or go" of 2026-09-11, off 65af4be0 (Order 31's sealed
tip, CI green there). The order is what kolt found while dogfooding the rpc seal: three
soundness holes (B288 and B290, closure typing through a user generic struct and an
unannotated closure parameter's `is` pattern, both accepting programs that must refuse;
B273, an impl's `with` clause bound-checked by nothing), two reactive-core robustness
defects (B291, an `Owner` with no disposed state, so a late registration leaks for the
session; B292, a drain with no exception safety, so one throwing observer turns the graph
off), the Wire predicate as a syntactic allowlist (B289, with A82's std `Result`/`u53`
impls), a Chrome per-tab drag wedge std's `link` arms (B293), and — the owner's asks of the
day — A85 positional slots (a paper this order, `when`/`swap`/`bind_each` as `Slot` values
at an anchor, A71 built as its brick), B294 (`_` as the anonymous type binder), A86
(`flatten` as a blanket over `Source`) and E161 (the generic-head highlighting). Rulings
asked at the draft (P1–P3 the sync unleased handle stub with server dedup by identity and a
std `Memo`; P4 B287; P5 A71) were not given, so the defaults stand: rpc-32 is not in this
order (a breaking stub change waits for an explicit ruling — its brief stands for the next
order), B287 stays stated-unenforced, A71 is built. Six Opus lanes: solver-32 (TOP: B288,
B290, B273, B275, B280), reactive-32 (B291, B292, B283, B277, A86), wire-32 (B289 then A82,
one lane), rpc-smalls-32 (B282, B284, B285, A78), ui-32 (B293, A83, A71, the A85 paper),
smalls-32 (B294, E161). Landing order smalls → ui → reactive → wire → rpc-smalls → solver.
The record-only rulings from Order 31 (hop scope dynamic-only, no keyed hop, same-module
handlers, sync void forward stubs, `__contract` kept, bare `[expose]` over a `KeyedCell`,
`reattach_mirrors`' `replay`, `keyed_log_limit` fixed) are written as built at the sweep
unless the owner objects. Kolt follow-ups wait for the owner's word after the seal; the cut
(held since Order 29) waits for the owner's kolt test on it. Briefs:
`scripts/integration/sweeps/order32/briefs32.md`.

MERGED (six lanes, in the order they landed, not the brief's): rpc-smalls-32 (64e4765b; ledger
rows 412 and 413), smalls-32 (f8e23015; row 414), reactive-32 (20e0e6af; `inference/traits.rs`
folded by name), wire-32 (fb898003; row 411 re-keyed) — these two held back from pushing by the
split emission golden, which reactive-32's two runtime helpers moved, and regenerated once over
the merged tree (85f5c56c) — ui-32 (08c9f9d6, the same golden regenerated again over that tree
at 4d38678c; seven DOM stubs edited by the lane, no fold needed), and solver-32 (5a0d0b49;
`bounds.rs` folded with the un-ignored B262 pin taken from the lane, `service_layer.rs` by
name; analyzer.rs auto-merged — the ownership map held across four lanes that touched it).
One integrator miss: the wire-32 merge was chained behind the reactive-32 check in one command
and ran before the split failure had been read; recovered by the one regeneration. No ledger
rows beyond 412–414; CHANGELOG parity 303/303 at the last merge.

SEALED 2026-09-11 at 5a0d0b49: union 6971/6971 (23 skipped; 1 slow); clippy, the Windows
cross-check, audit and fmt green locally; CHANGELOG parity 303/303; CI GREEN on all eleven jobs (run 34633671304: ubuntu 17 and 15 min, Windows 16 and 18). Six lanes,
26 commits over the six merges plus two golden regenerations; ledger rows 412–414 assigned (next
415) and row 411 re-keyed. The order's verdicts, against the kolt dogfooding that opened it: the
three soundness holes are closed (B288's two real roots were the struct-literal door and the
readiness gate, not the closure-return sites the brief named; B290 was one missing defer in
`resolve_is`; B273 draws its boundary at the impl's own binder), the reactive core survives a
late registration and a throwing observer (B291's single-use `Owner` is the one breaking
consequence, disclosed; B292's finally costs ~1.3 kIr per drain and nothing per notify), the
Wire predicate reads the impl table at all four boundaries and std carries `Result` and the
sized scalars (B289/A82 — `[derive(Wire)]` still emitting the JSON impls is the residue, B301),
std's `link` no longer arms the Chrome drag wedge (B293, with `View::link_to`), every reactive
child keeps its position at one node per region and zero per row (A71, which also fixed a latent
kolt bug for free), `_` is the anonymous type binder and two of them were one parameter until
today (B294), the generic-head highlighting is traced to its two layers and fixed in both
(E161), and A86 (`flatten` as a blanket) was dropped honestly behind two impl-selection gaps
(B299, B300). What the order did not do: rpc-32 (the sync unleased handle stub, identity dedup,
`Memo`, A79) waits for the owner's P1–P3; B287 stays stated and unenforced; A85's surface is the
paper's ruling. Kolt does not build on this toolchain until `views.vl:57` maps its `Source<bool>`
to a string (B275's correct refusal); the rest of its follow-ups wait for the owner's word. The
sweep: 20 closed, 22 filed (B295–B307, A87, A88, E162, E163, N71–N73, M61, M62); the eight
Order 31 record-only questions stand as built, not ruled. Lane worktrees and branches reaped.
Process, for the next order: pins live in `tests/inference/<module>.rs`; the split golden moves
on any `std::reactive` emission change and is regenerated once over the merged tree; a merge is
never chained behind another's outcome check in one command; the integrator pushes lane branches
(lanes never push — the mechanics block's "push the branch" is retired).

## Order 33 — cycle 51: the surface order (2026-09-11 → 2026-09-12)

Opened on the owner's "Go with your recommendations on all rulings" of 2026-09-11, off
5a0d0b49 (Order 32's sealed tip, CI green there). Every ruling Order 32 left in the queue is
therefore ruled as recommended, the same day: A85's surface (five value forms `when`/`swap`/
`each`/`each_values`/`each_by` as `Slot` structs with the parent methods as sugar, render
closures still `View`, no `Group`, B253 unchanged; `each` beside `bind_each`; the split
recognizer learns the value form; "a render closure may yield a `Slot`" filed as A91); A46 as
the `List<View>` literal; A88 the boundary removes what it placed; P1–P3 the sync unleased
handle stub with server dedup by source identity and a std `Memo` (filed as A92, with A79 in
the same shape); P4 B287 refused; B299 desugared to `impl type S: Trait<..>`; B307's under-supply
refused with B273's binder boundary kept; A84's direction (data-attribute rules + custom
properties) measured before it is confirmed; `View::link_to` kept, `Vec2` gains
`length_squared`, `Region` public, A87 declined until a caller appears, E163's two
devDependencies added, E154 yes, E156 accept and document, A82's lanes and sticky tag kept,
A78's wiring refusal kept, B292's abandon-the-wave kept; A90 (`var("--")` checked at const
time) filed at GO. The order is the UI surface kolt is written against — styles, positional
slots, fragments — plus the solver residue Order 32 pinned and the owner's daily loop. Eight
Opus lanes: solver-33 (TOP: B300 → A86, B304, B296, B305, B306, B299, B297; B286 droppable),
styles-33 (A89 with the owner's `not` marker, B308, A90, `Vec2::length_squared`, the A84
measurement), rpc-smalls-33 (B295, B303, B301 with a census, B307, N70, B287), dx-33 (B276,
E106, M58), editor-33 (E160, E163, E162, E157, E159, E154, E156, E158), hygiene-33 (droppable,
lands first: N73, N71, N72, M61, N69, N68, N65), slots-33 (A85, A46, A88), rpc-33 (A92, A79 —
briefs32's rpc-32 text re-anchored). Landing order hygiene → editor → styles → rpc-smalls → dx
→ solver → slots → rpc. Ledger next id 415. Kolt follow-ups wait for the owner's word after the
seal; the cut waits for the owner's kolt test. Briefs:
`scripts/integration/sweeps/order33/briefs33.md`.

MERGED (eight lanes, in the order they landed): hygiene-33 (a7c1db5f; ledger row 415), editor-33
(c9a72294 + 99e822b6 — E157's new rule constant joined N65's curated list at the merge, the two
lanes having branched before either existed), slots-33 (31592245; guide/ui.md auto-merged),
rpc-smalls-33 (44ee8529; rows 416–418 — the lane had numbered its rows itself and one collided
with hygiene-33's, resolved by marking it NEW), dx-33 (34933b5c), styles-33 (4a70f301; rows
419–424), rpc-33 (ca5e0777 + 288ce830 — rpc.vl's generator hunks scripted: the lane's A92/A79
structure with B295's module qualification re-applied; `service_layer.rs` needed an ITEM-LEVEL
three-way merge because the fold-by-name tool carries new program constants but not edited ones,
a tool that now lives beside the others as `merge_items_by_name.py`), and solver-33 (e4d192e3; the un-ignored A86 pins and the a52 markdown pin taken from the lane; ledger row 425 — B299's steer).
The corpus, split and markdown goldens merged consistently across lanes and were regenerated only
where the merged tree said so. One outage: the 1Password agent that signs commits and answers
GitHub went silent for about an hour mid-order; every lane and the integrator prepared their
commits as idempotent scripts and landed them when it returned — nothing was committed unsigned.
CHANGELOG parity 343/343 at the eighth merge; ledger next id 426.

SEALED 2026-09-11 at e4d192e3: union 7132/7132 (26 skipped); clippy, the Windows cross-check,
audit and fmt green locally; CHANGELOG parity 343/343; CI GREEN on all eleven jobs (run 34659832905: ubuntu 13 and 12 min, Windows 22 and 20). Eight lanes; ledger rows
415–425 assigned (next 426). The order's verdicts, against its own framing as the surface order:
the styles surface is the owner's `new_button_style` made spellable (A89's presence attribute and
the `not` marker that negates its enclosing condition, A90's dashes check, with the A84
measurement confirming the ruled direction — a rendered button four times cheaper, five hundred
times with a const class list — on the condition that B308 lands with it, which it could not
this order: emission is const-only and every application path is runtime, so B308 wants the
retraction design and a ruling); the positional-slots surface is HALF built — the fragment
literal (A46) and a boundary that removes what it placed (A88) — and the value forms are not
expressible until a `context` clause can live on a struct field (B309), which the lane proved by
measurement rather than argument; the solver residue is closed in full (B300 binding a bound's
own binders as a worklist, which unblocked A86's `flatten` blankets; B304 reframed from "inherent
method" to receiver-resolution timing; B296 shrunk to two sibling arguments of one call; B305's
erased list; B306's silence measured at eighteen refused programs and kept; B299 the desugar;
B297; B286 at no measurable cost); the daily loop is faster and understood (B276: kolt's watch
rounds 5.15 → 1.26 s CPU, the client leg `Fresh`; E106: the suspected leak refuted, the growth
named — one retained analysis per open document, the owner's live server at 4.1 GB — and filed
as M63/M64; M58: the warm profile taken and a 6.44% hoist landed); the rpc surface is the sync
unleased handle stub (A92: a hundred minted handles cost one source and no call; dedup by
identity with a frame-shape discriminator; `std::memo`) and the keyed return (A79); the editor
gained struct-initializer completion (E160), the parity gate for documented enums (E159) and
five more, with E163 stopped one CI step short; hygiene consolidated nine DOM stubs, gated the
curated rule statements and ruled the join order unpromised. What the order did not do: A85's
value forms (B309 first, the re-ruling asked), B308 (ruling asked), E163's tokeniser (an `npm
ci` step asked). Two miscompiles came out of it — `Map::entries()`'s tuple layout (B310) and a
`pseudo` name carrying a `:` (B311, live in kolt) — and the 1Password outage that cost an hour
of wall time cost no correctness. The sweep: 37 closed, 16 filed (A93 A94 B312–B316 E164–E166
M63–M65 N74–N76) plus the 5 filed mid-order (B309 B310 B311, A90–A92 at GO). Kolt's follow-ups
at the owner's word: views.vl:57's `.map`, store.vl:27's impl, styles.vl:48–49's `pseudo`
(B311), views.vl:165's `child_relation` → `attribute` + `not`, the overlay's manual remove
(A88), the eight `|..: Event|` annotations (B304), model.vl onto `std::memo` and `.or()` (A92),
`var("--button-color")`. Lane worktrees and branches reaped. Process, for the next order: a
lane writes `NEW` for every ledger row; a named rule-statement constant needs two edits; a lane
that edits a program CONST beside its pin needs `merge_items_by_name.py`; the split golden and
the corpus goldens are checked over the merged tree, not regenerated by reflex; a bare `ssh -T`
is not the probe for git's agent.

## Order 34 — cycle 52: the foundations order (2026-09-13 → 2026-09-13)

Opened on the owner's "Go with your recommendations on all rulings" of 2026-09-13, with one change
of spelling (A80's mutable pattern binding is `Some(mut x)`, after the variable declaration
syntax), off e4d192e3 (Order 33's sealed tip, CI green there; nothing landed between). The
order is named for what it carries: two DESIGN PAPERS before any build — B318, visibility and
the import surface (default-private, `export *;`, `export(PATH)`, the `#` reach with no
diagnostic on a dependency, the exposure warning in the owner's wording, `export mod` + `::*`,
the parenthesised impl selectors `(impl T)` with `_` and `only`), and A95, `Style`'s condition
model rebuilt on typed condition values and compiler canonicalisation — each written by its own
lane and ruled before Order 35 builds them. Beside the papers: B317 (the associated-function
import, a spec bug the prelude sketch exposed) builds now; the two miscompiles Order 33 found
(B310 `Map::entries`' tuple layout; B311 fenced, its real fix A95's); the tooling that bit while
writing kolt (E167 the css converter that never fired, E168/E169 Organize Imports' over-prune
and over-keep, A96 HMR's websocket error per remote source); the language server's memory
(M63 retention at N=2, M64 `malloc_trim` with `libc` promoted); B316's arm accepted; A67's
ambiguity error and B274's copy; E163's CI step; and the re-ruling A85 waited on — B309 in
shape (1), the `context` clause in the closure type, built by slots-34 with A85/A91 following
in Order 35. A92 and A79, built in rpc-33 and left open for three questions, closed at GO with
those questions ruled as built; rpc-33's three unfiled finds filed as B319, M66, A97. Ten
lanes, all Opus; ledger next id 426; the owner's one action at GO is kolt's `child_relation`
site, which A93's fence will break.

**MERGED (2026-09-13).** Ten lanes, nine merges (the visibility paper lane built nothing): tm-34
d4ad9d30 (E163's scope pins with the CI step, E164's grammar fixes — 14 characters of scope
moved across the whole estate, every one a tag's closing bracket), paper-style-34 131cc9ec
(A95's paper; B311's wrap fence and A93's relation fence, rows 426–427 — kolt's site had already
moved, so nothing broke), hygiene-34 d06b158d (N74, N75's stubs, N76 keyed by text, N66's guard,
N35's read-until-parse; N67 written into build-hooks.md), editor-34 16033751 (B314 — which
turned out to have made renaming any type with `Self` in its impls impossible; E168/E169 as one
predicate; E167 inlining std's shorthand bodies; E165; M65 −7.9 % on the completion index; E155
with zero blast radius), dx-34 77f329a6 (M63 at N=2: kolt's 19 files open 1,090 → 510 MiB, the
floor now the base cache's 270 MiB; M64's `malloc_trim`; E166), rpc-34 b5808e18 (A96 confirmed
under a socket stub — two `Unsubscribe` frames on a closing socket and a zombie redial, gone;
B312, B313, B319 — rows 428–429), solver-34 462e049e (B310's tuple layout on the instantiated
body — three directions, not a call boundary; B315 as jointly-inhabitable bounds, row 430; B302;
B279's sweep with its refusal backed out as not an invariant; B316's two arms), lang-34
c059ab81 (B317 through an `ImplNamespace`; A80's two refusals — the sugar already parsed; A67
as the ambiguity error, row 431 — the declaration had been winning and the file unreachable;
B274's copy; B278; rows 431–432, row 118 edited), and slots-34 36fb64ed last (B309 in shape
(1): the clause in `Type::Closure`, resolution before the fixpoint, 87 match sites audited, the
leak slots-33 measured now impossible by construction; row 57 deleted, 219/221 edited, row 433).
The papers: visibility.md (989 lines — `#` is a lexer refusal, std is 664/118 not 364, the
per-importer namespace must reach monomorphization) and style-conditions.md (674 lines — the
variadic `.on` cannot be spelled, `on<C: IntoConditions>` can; A95 reduces B308 and does not
delete it). One process lesson: a backgrounded tool call with a timeout SIGTERMs its gates at
the deadline — hygiene-34's first run died at 600 s with 541 tests unrun and no red gate; every
later merge ran detached with a waiter. Seal started on 36fb64ed.

**SEALED (2026-09-13) at vilan next @36fb64ed.** The local seal: union 0, clippy 0, the Windows
cross-check 0, audit 0, fmt 0, changelog parity 376/376; CI run 34768306284 green on all eleven
jobs (both Ubuntu and both Windows test legs — the Windows legs now running `npm ci` for the
extension's tokeniser, E163's one unverified step, verified). Ledger rows 426–433 (57 deleted,
118/219/221 edited; next 434). The sweep: 35 closed, 26 filed (B320–B332, E170–E174, M67–M69,
N77 N79 N80, D7, and G23 — the const-eval end-of-evaluation hook the owner ruled for B308 the
same afternoon, reading the style paper: "a proper build step hook for styling would fix the
issue for good"); tracker 95 open. Two papers stand for Order 35: visibility.md, whose S1 (the
bit and the two warnings) is shippable alone and whose S4 (the per-importer namespace) has to
reach monomorphization; and style-conditions.md, whose first slice is now G23 and whose surface
is `.on(CONDITION, STYLE)` with `within(condition)`. B309 landed, so A85 and A91 build next on a
clause-carrying constructor parameter and a field spelled without `sync`. Toolchain refreshed in
both locations (vilan 0.40.0 (36fb64ed2)); the ten lane worktrees and branches reaped. The
owner's kolt `child_relation` site had moved before the fence landed, so the order shipped with
no owner action pending. One number for the day: kolt's nineteen files open in the language
server went from 1,090 MiB to 510 MiB, and what remains is the base cache's ruling (M67).

## Order 35 — cycle 53: the papers' first slices (2026-09-13 → 2026-09-13)

Opened on the owner's "Go with your recommendations on all rulings" of 2026-09-13, the same day Order
34 sealed, off 36fb64ed. Both papers are built from their first slices: style-35 lays G23 (the
const-eval end-of-evaluation hook the owner ruled for B308 — "a proper build step hook for
styling would fix the issue for good"), moves emission onto it, then lands A95's condition values
behind the existing surface with byte-identical stylesheets as the gate; visibility-a-35 lands
the bit, the two warnings in the owner's wording, `export *;`, `export(in PATH)`, `export` on an
impl in the strict form, `[doc(hidden)]` retired, and `#` as a token (row 335 retired), while
visibility-b-35 lands `only` and the parenthesised selectors with `_`. slots-35 builds A85 and A91
on the clause B309 landed. Around them, the finds Order 34 filed: the clause's three silent
corners, two rpc checks and three solver residues (solver-35); the loader's `lib` double name and
the type-segment scope, census-gated (lang-35); five editor items (editor-35); the base cache's
ruled budget, measured before its default is set (dx-35); std's stale census, the derive
fallback's deletion, the harness predicate and the std cache that never pruned (hygiene-35). Eight
rulings, all as recommended; Order 36's queue named at the sweep: B318 S4 and S6, A95 S2 with
kolt's migration, S3, S5, M55.

**MERGED (2026-09-13).** Nine lanes, nine merges: editor-35 c525d303 (E170–E174: a head item's name is an
attribute, the book's tag regex, the converter reads the file's own `impl Style`, the fade names the
rewrite, the session summary on demand), hygiene-35 492b1769 (N77's census, N79's derive
generators deleted — 729 lines, six names, five modules — behind one refusal, N80, L21's cache
that prunes itself), lang-35 871fd753 (B331: `a/lib.vl` no longer a module under its own
directory; B332: a type segment replaces the walk's namespace, on a zero-hit census of 287 files;
D7), dx-35 03df116d (M67 measured before it was set: 192 MiB, seven worlds, M63's floor met at 305
MiB — and a miss is 21–295 ms, not the 3.5 s the brief expected; M68; M69), style-35 7f05e26f
(G23 the end-of-evaluation hook, whose registry had to be host-held; B308 closed with every
sheet's dead share at zero; A95's S1 behind 145 byte-identical artifacts, rows 437–453),
visibility-a-35 b62c8bf8 (S1 and S2 with two rollout pieces the paper lacked — std's imports
silent, an uncurated module offers everything — B320, B321, `#` a token, `[doc(hidden)]` retired,
rows 454–461, row 335 gone), solver-35 592e45d3 (the clause's three corners, B326, B327, B328,
B329, B330 documented), visibility-b-35 fdaea14b (S3: `only` and the parenthesised selectors,
`_` free from B294, `file_impls` and the admission refusal, the organizer re-pointed — a hand
merge of nine files, the two visibility lanes' adjacent additions unioned, one arity threaded,
two stranded braces closed, and visibility-a's B320 pins re-read against S3, since one lane had
pinned the world the other was removing), and slots-35 baaa7911 last (A85's value forms and A91's
regions, kolt two wrappers lighter, the third B253's). Ledger rows 434–463. Three process lessons
for the tools: a multi-line string const splits the item folders, a renamed test comes back under
its old name, and a conflict-unioned constant keeps both lines.

**SEALED (2026-09-13) at vilan next @9b22ec36.** The seal on baaa7911 read union 7409/7411, clippy 0,
Windows cross-check 0, audit 0, fmt 0, parity 414/414 — the two reds were the new plain-reach
warning landing where a workspace pin and the benchmark runner demanded silence, fixed with the
estate's own `export *;` line (3473a550); CI on that tip then went red on both Windows test legs
for two of S3's selector pins, whose module lookup matched a `/`-joined suffix against canonical
paths as strings — a `\`-separated path never matched — fixed by comparing path components
(9b22ec36); CI run 34783… green on all eleven jobs at 9b22ec36. Ledger rows 434–463 (335
retired, 163 re-keyed; next 464). The sweep closed 29 and filed 19 (M70, the seven kolt files the
base cache can never serve, at the top; B333–B339; E175–E179; A98; N81–N85, three of them the
merge tools' own defects); tracker 86 open. Both papers stand amended: visibility.md §14 (S1–S3 as
built — the std suppression and the uncurated-module exemption the rollout needed, `#` a token,
`[doc(hidden)]` gone; S4–S6 next) and style-conditions.md §13 (G23 with a host-held registry,
B308 closed at zero dead share, S1 behind 145 identical artifacts; `Condition` one type,
`within(hover())` waiting on the slot key; S2, S3, S5 next). A85 and A91 landed on B309, two of
kolt's three wrappers removable. Toolchain refreshed in both locations (vilan 0.40.0
(9b22ec364)); nine worktrees reaped. Lessons for the process, all filed: a backgrounded gate
with a timeout dies at the deadline; a `Claude`-authored commit is refused at the push; the item
folders split a continued string const, resurrect a renamed test, and drop an edited const;
the ledger-tuple union keeps both lines of a constant; two lanes can pin contradictory premises
about one grammar; and the seal's Windows leg compiles but never runs.

## Order 36 — cycle 54: the papers' second slices, the breaking surface, and the callable bridge (2026-09-14 → )

Opened on the owner's "Go with your recommendations on all rulings" of 2026-09-14, the day after Order
35 sealed, off 9b22ec36. Both Order 34 papers turn their remaining slices into the user-visible half:
visibility-36 builds B318's S4 (the per-importer method namespace, monomorphization resolving under the
DECLARING file), sweep-36 the S6 estate sweep with std's curation (R5) and the S5 docs, merged last as
one revertible diff; style-36 builds A95's S2 (the condition surface, BREAKING: the `not` marker and
`child_relation` go, `within(hover())` lands on a structured slot key — R1–R3), S3 and S5. The owner's
rulings of 2026-09-14 become code: lang-a-36 retires the six `View` parent methods for the free slot
functions (A99) beside A98 and B334 (R4); lang-b-36 builds B340 (`Callable` — in the owner's framing
"closures are formally callable structs"), then G24 (`const let`/`const fun`, the snapshot as a
`Callable` struct) and B333; lang-c-36 builds A100 (`lazy` parameters and module bindings — the paper
ratified 2026-07-21 that never entered the tracker). editor-36 repairs Organize Imports (E180, the
rescue that broke kolt's lucide file; R9) and gives `export *;` its place (E181) with E175–E179; perf-36
takes M70 (seven kolt files never cached), M55 (R6) and M66 (R8); hygiene-36 fixes the merge tools
(N81) and the lane-load flakes; paper-native-36 writes the cell-representation paper (C14) and the
native-apps paper (F1, R10: emit-Rust, desktop first). Ten Opus lanes; ledger next id 464; tracker 94
open at GO.

**MERGED (2026-09-15) — all ten lanes at vilan next @da8cb6e0.** hygiene-36 262ee97d (N81's tools landed in
proposals, N82–N85, B337, B339); editor-36 97623395 (E180 — the organizer's rescue no longer binds a
taken name and kolt's lucide organizes clean; E181 the marker's slot after the leading import BLOCK;
E175–E179); lang-c-36 06eba0e5 (A100: `lazy` in three homes, thunk/force/forward, the memo cell, the
cycle trap and poison; `lazy` was not a free identifier); perf-36 cfc5136e+6c034487 (M70 the entry-aliased
key — six kolt files served, 8–14 % per keystroke; B341 the desugar seeds in the key; M66 the lazily
stamped identity; M55 measured and declined: kolt has two legs, the ceiling is 3.4 %; the split golden
regenerated at the merge); style-36 10e5031a (A95's arc complete — the `not` marker and `child_relation`
gone, `within(hover())` on the guard's inner token with every stylesheet byte-identical over 145
artifacts; R3 built for its purpose, the triple-beside-each-slot storage measured at +9.4 % and refused;
one hand fold in the formatter's pass chain); lang-a-36 49611256 (A99's six methods gone, A98's
reconciler, B334's receiverless rule; one hand fold in the language server's quick-fix arms); lang-b-36
365dd9ff (B340 `Callable` with no transformer change, G24's snapshot by substitution, B333; the fixed
merge tools summed `RULE_STATEMENT_SITES` 34 + 8 + 1 = 43 on their first outing; two merge fixes — the
thunk closures' `origin`, the editor page's count word); visibility-36 414d5476 (B318 S4 whole: the
admission map keyed by the pair, the monomorphized body resolving under its declaring file, the
import-site refusal, the `export impl` gate, `#(impl T)`, B330 at the call; B335/B336/B338; the E178
`Program` surface; macro_std's ten blocks `export impl`); sweep-36 da8cb6e0 (the 24-file codemod, std's
curation 548 of 856, the suppression dropped; four marker files hand-folded, and the curation RE-RUN over
the merged tree — the codec and fetch blocks a derived `Wire` visitor reaches at monomorphization had to
be exported, and style-36's table-sync reader had to strip the marker). The paper lane landed
`signal-cell-representation.md` (C14 recommends the counted `Shared`) and `native-apps.md` (F1: emit Rust,
desktop first, a third `View` twin) with a built Rust probe. Ledger rows 464–499 (next 500); seven
retired; four re-keyed. Two seal fixes followed: the wasm playground's router fixture (9da581a6) and the
suite's test threads raised to 8 MiB (d783fbf4) after the Windows shard aborted on a stack overflow in the
analyzer's walk — the frames grew this order, the recursion did not.

**SEALED (2026-09-15) at vilan next @d783fbf4.** The local seal on da8cb6e0 read union 7582/7583 (the one red
was the wasm playground's router fixture still writing `View::swap`), clippy 0, the Windows cross-check 0,
audit 0, fmt 0, changelog parity 445/445; the union re-run over the fixed tree 7583/7583. CI on da8cb6e0
found what the local seal cannot: the second Windows test shard ABORTED on a stack overflow in the
analyzer's expression walk — nine levels of nesting in a module-cycle pin, the frames grown by this order's
lazy, const, callable and visibility arms — so the suite now runs on 8 MiB test threads (`.cargo/config.toml`,
N97 filed for the frame itself). CI on d783fbf4: green on all eleven jobs (run 34913736715). Toolchain
refreshed in both locations (vilan 0.40.0 (d783fbf4c)). Sweep: 31 closed, 29 filed, tracker 105 open; ten
worktrees and branches reaped. Kolt owes three edits at the owner's word (the nine A99 sites, one
`:placeholder` pseudo, a manifest comment); the website carries seven uncommitted `export *;` markers.


## Order 37 — cycle 55: the native foundations, the css call surface, and the honest tools (2026-09-17 → )

Opened on the owner's "you may begin (go)" of 2026-09-17, two days after Order 36 sealed, off d783fbf4.
The two native papers turn into code under thirteen rulings taken as recommended, two of them steered
at GO: native-a-37 builds C14's first three slices on JS (R1 = (a), the counted `Shared`: the 19
frame-scoped cells become locals, `Weak` lands JS-lowered, `observe` and `Subscription` hold weak back
edges, the SCC gate the exit); native-b-37 lands C16's refusal first and then F1's S1a — a `Backend::Rust`
arm, the `vilan-rust` emitter and a dependency-free `vilan-rt`, `board.vl` and the platform-free corpus
byte-identical against the JS backend, no async and no UI — under the owner's amendment that the native
products come in the order CLI programs → web servers (F18, "a huge win in and of itself") → a UI layer
only after a design conversation about writing UI once for native and web (F17; R4's three-layer rule
recorded, not ruled). css-37 builds the owner's A101 (css declarations become calls; BREAKING over 138
blocks; R10–R12) with E183, merged last. solver-37 takes the A99-reachable value-form family (B351,
B347) with B349/B350 and, from the GO-day kolt sweep, B352 (three closure-typing exhibits) and B353 (a
possibly unsound `set`); lazy-37 the retrofit A103 behind its differential, B344/B345 and A102 (R13);
diagnostics-37 the cascades kolt's upgrade exposed (E189, E190, E185, E191) and B343 (R9: the clause
stays after the return type); editor-37 the spec-generated attribute completion E69 with E184,
E186–E188, E192 and E193; perf-37 M72–M75 (kolt's store.vl never cached); dx-37 the three tools that lie
(B346, N90, N91, N92, B342); hygiene-37 N94–N97, N86–N89, first. The kolt sweep (46 comment lines)
filed twelve items and found fourteen comments stale against std that shipped in Orders 30–32 — kolt's
migrations at the owner's word. Ten Opus lanes; ledger next id 500; tracker 120 open at GO.

**MERGED (2026-09-17) — all ten lanes at vilan next @710e4790.** perf-37 07eb16b7 (M72 — a `[service]`
entry reaches the base cache, kolt's store.vl 482 → 196 ms CPU per keystroke; M75's indexes; M73 measured
and re-pointed at M79; M74 measured, the factor stays); native-b-37 2de69376 (C16 — a view-capturing closure
handed to a keeping callee is refused, C13's pin un-ignored; F1 S1a — `Backend::Rust`, the dependency-free
`vilan-rt` and the `vilan-rust` emitter, 17 corpus programs byte-identical against JS and 0 differing, 51 of
the 98 refusals being monomorphisation; the J6 executor designed; F18 sized — joining `@process` is free and
the rpc server is extern-free); editor-37 16cab90b (E69's generated attribute table with an offline gate;
E184; E186–E188; E192 a false positive that Organize Imports would have turned into a broken build; E193's
head resolution); diagnostics-37 88261dda (E189's narrow rule at the root — kolt's pre-migration tree
184 → 9 — with the broad gate built, measured and withheld for B279's soundness face; E190; E185 whose root
cause is B354; B343 under R9; one hand fold in `analyze_over_world`); hygiene-37 4aa16957 (N94–N97, N86–N89
— 34 ledger rows, the walk's frame measured at 42,464 bytes per level with a canary, `export const` was
refused and is not; seven commits re-signed; one tmpfs merge fix for perf-37's new pins); native-a-37
ae0c2564 (C14 S1–S3 under R1 — eight of nineteen cells, `Weak`, the two back edges weak, a match-capture
aliasing miscompile found and fixed, the SCC exit test corrected as unachievable on JS; the split golden
regenerated over the merged tree); solver-37 4ee1003d (B353 unsound and fixed — a method call in an
unannotated closure body checked once; B351; B347's fill; B349; B350; B352's two bugs with two exhibits that
do not reproduce; the split golden regenerated again); dx-37 0996563b (B346 — one toolchain root for `std`
and `macro_std`; N90's `fmt` exit 2; N91 stale, the pin landed; N92's check cache out of the package; B342
measured, the heading corrected); lazy-37 7d2cf8a5 (A103 behind a 304-program differential with zero
observable differences, `Option::expect` new; B344; B345; A102 under R13); css-37 710e4790, last (A101 —
declarations as calls over 227 blocks with no golden moved and three converter bugs fixed on the way; E183;
three hand folds, the curated-list union's resurrected constant and an E187 pin re-spelled at the merge).
Ledger rows 500–545 (457 retired; 158/294/330 re-keyed); the split golden regenerated twice; sweep 45 closed
/ 33 filed; tracker 108 open. Seal and CI running on 710e4790.

**SEALED (2026-09-17) at vilan next @31c13567.** CI 35266821255 green on all eleven jobs; the local seal green
on the same tip (union 7,739/7,739, clippy, the Windows cross-check, audit, fmt, changelog parity 493/493)
after two seal fixes: 84cacb87 (AGENTS.md's repo map names the two new crates; two scratch sites in
split.rs; the native differential stages its corpus per process — its four tests had shared one directory
and each began by deleting it) and 31c13567 (five Windows-only reds CI found where the local seal cannot
look: the check-cache pins hashed the package path in Windows' extended-length form where the CLI does not
— aligned on the CLI's own function — and the M75 shape pin read `/proc`, so it exists only on Linux).
Toolchain refreshed in both locations (`vilan 0.40.0 (31c13567b)`). Ten worktrees and their branches
reaped, local and remote. Ledger rows 500–545 (457 retired; 158/294/330 re-keyed); sweep 45 closed / 33
filed; tracker 108 open. Two miscompiles fixed this order (B353's unchecked closure body; the match-capture
aliasing under B267's walk) and one breaking surface landed (A101's declarations as calls). Order 38's queue,
the rulings owed (B355's gate, A108's Wire receivers, the lazy gate's wording, the F17 conversation) and
kolt's owed migrations are in `sweeps/order37/notes37.md` and `go-items37.json`.

## Order 38 — cycle 56: generics on the native backend, the scheduler's dead observers, and the breaking Wire receivers (2026-09-21 → )

Opened on the owner's "Go with all recs (including the before go points)" of 2026-09-21, four days after
Order 37 sealed, off 0fa109eb — the sealed tip plus the 1.98.1 toolchain pin, pushed at GO with the
worktrees cut only after its CI run reads green. Eight rulings, all as recommended: B359's default-body
receiver is the TRAIT's member, always (R1); A108's Wire receivers move to `&mut self`, BREAKING, merged
last (R2); B355's broad gate behind a non-diagnostic face for B279's fence (R3); A110's door 1 — a
subscriber liveness flag, so a disposed observer never fires inline or in a later wave — is built while
door 2's ordering rule is a `reactive-turns.md` section ruled afterwards (R4); F1 S1b and J6's executor
run in parallel with F18's http/db/rpc left to Order 39 (R5); a `void` rpc return is admitted (R6);
`std::style::prelude` gains its four types with the ambient door only at a zero-collision census (R7);
the golden gate reads "runtime output" (R8). native-a-38 takes F19 and then S1b whole (generics — 51 of
the backend's 98 refusals — module-level bindings, operators, `?`, the intrinsics; `board.vl` flips to a
byte-identical comparison); native-b-38 J6; solver-38 B359 with B354 (HIGH), B355–B357 and E199;
reactive-38 A110 door 1, A105, A73 and door 2's measurement; std-38 the kolt sweep's gaps (A104, A109,
I4, I3, A106); perf-38 M78 first, then M76, M77, M80, M81 and M79's paper section; editor-38 E198, N108,
E194–E197, E200, E201; hygiene-38 N98–N105, N107, L23, first; wire-38 A108 and A107, last; papers-38 the
A112 incremental-collections paper (the receiver question already probed: two traits over one `splice`
primitive) and door 2's section. Filed since the seal and committed at GO: A110, A111, A112, B359. Ten
Opus lanes; ledger next id 546; tracker 115 open at GO.

**MERGED (2026-09-21) — all nine code lanes at vilan next @c3f7d1a3; papers-38's two documents in proposals.**
std-38 972e2a1b (A104 — `Result` crosses JSON in the codecs' own `{"Ok":…}` spelling; A109; I4 — three
containers were missing `Default`, not six; I3's `filter_map` twice; A106's door 1, with R7 CORRECTED — the
language has no wildcard import — and door 2 shut on a 6/40 collision census); hygiene-38 3964b830 (N98's
prose-literal gate over eight crates, 38 sites; N99–N105, N107; N102 38 → 3, → 0 by the integrator; L23's
dispatch rehearsal, whose FIRST run failed in four seconds at an unguarded changelog step — fixed on next);
editor-38 a3c78b0a (E198's residence/frozen split; N108, whose diagnosis was wrong — a `const { … };`
statement lost its terminator and the decline named the file's first item; E194–E197, E200, E201); perf-38
e09f5ea6 (M78's CPU phase marks; M76 — kolt reused 0/69 → 59/69, −10 to −14 % thread CPU per keystroke on a
quiet box; M77; M80 — eleven goldens back; M81 — `__lazy(` 84 → 19; M79 as a paper that re-sizes itself);
solver-38 5e54eed5 (B359 under R1 — one affected shape in the estate, `Ord::clamp` over the integers; B354 —
three of six codec blocks private again; B356; B357; B355's broad gate behind a non-diagnostic face — kolt
copy 35 → 1, E191 closed; E199 not built; one hand fold in `dispatch_refine.rs` against perf-38); reactive-38
62f401dd (A110 door 1 — THREE faces, and the DOM face is a hard crash on the base, so kolt's latch is
load-bearing; the scrub fix papers-38 found and relayed mid-order; A105; A73; door 2 measured at +23.5 %
bucketed; four goldens regenerated over the merged tree, runtime-identical); native-a-38 00f396f6 (F19; F1 S1b
— generics by reproducing the JS emitter's mechanism; the whole-set differential 29 → 47 byte-identical and
4 broken → 0, the base having been RED where §10 said 0; three unsigned commits re-signed by rebase); wire-38
7ef8db82 (A108 BREAKING — `Shared::new(` 128 → 118, the wire byte-identical, kolt migrates by rebuilding;
A107 — an awaited `void` answers `Option<RpcError>` because the language has no unit literal; the census
literal hand-folded to a MEASURED 121; solver-38's B354 fixture migrated at the merge); native-b-38 c3f7d1a3
(J6's executor, dependency-free with no `unsafe`; rebased onto S1b by the lane's own RESUMED agent — `nursery.vl`
byte-identical, the whole set at 49; `board.vl`'s recorded wall was a FALSE POSITIVE and its real one is the
host type `Hash`, so THE ORDER'S NATIVE EXIT IS NOT REACHED — F20; one merge fix, the boxed-binding count ×
A108). papers-38: `incremental-collections.md` (the law over 555 randomized checks; a delta-driven `each`
16,040× cheaper at 1,000 rows, today's `reconcile` scan quadratic — M82) and reactive-turns §7. The owner
ruled both papers mid-order (A112 §13 Q1–Q4, A110 door 2 — all as recommended) and filed E202–E207, A113,
A114. Five cross-lane folds, every one green on both branches and red or conflicted only on the merged tree.
One process incident: a lane typed a READ as a WRITE into the shared `.git/config` (`commit.gpgsign =
user.signingkey`) and `git commit` died in every worktree for an hour — three lanes committed through
plumbing, one repaired it, the lane that did it said so. Ledger rows 546–548; sweep 38 closed / 32 filed +
the owner's eight.

**SEALED (2026-09-21) at vilan next @c3f7d1a3.** CI 35642858068 green on all eleven jobs; the local seal green
on the same tip ON ITS FIRST RUN (union 7,867/7,867, the whole-set native differential — a seal leg from this
order on — clippy, the Windows cross-check, audit, fmt, changelog parity 539/539). Toolchain refreshed in both
locations (`vilan 0.40.0 (c3f7d1a38)`). Ten worktrees and their branches reaped, local and remote. Ledger rows
546–548. Sweep: 37 closed (L23 held for a green rehearsal) / 32 filed, plus the owner's eight mid-order
(E202–E207, A113, A114); tracker 118 open. One miscompile fixed (B359's default-body hijack), two native ones
(a loaned parameter cloned before a mutating call; a string-literal escape), one leak that was a crash (A110
door 1), one BREAKING surface (A108's Wire receivers — the wire itself byte-identical). NOT reached: the native
exit (`board.vl` stops at the host type `Hash` — F20). One admission: `next` was RED for about an hour between
wire-38's merge and native-b-38's — native-a's boxed-binding pin × A108 — because wire-38's merge gates did
not include the native differential and newer pushes cancelled the CI runs that would have said so; the second
release rehearsal is what caught it. The template's merge gates gain `native_differential` for every lane
touching std. L23's rehearsal: run 1 failed in four seconds (an unguarded changelog step — fixed), run 2 on a
pre-fix tree failed on that same red, run 3 (35645802713) is on the sealed tip. Kolt on c3f7d1a38: four errors,
all "std now ships what kolt hand-wrote" (`Default` for `List`/`Map` — model.vl:117, prefs.vl:102; `Json` /
`FromJson` for `Result` — shared.vl:86/101, whose removal changes kolt's persisted shape from `[0, v]` to
`{"Ok": v}`) — the owner's word. Order 39's queue, the rulings owed and kolt's owed list are in
`sweeps/order38/notes38.md` and `go-items38.json`.

## Order 39 — cycle 57: the native server's first request, the rulings built, and the bugs kolt keeps finding (2026-09-21 → )

Opened on the owner's "Go" the evening Order 38 sealed, off c3f7d1a3, with R1–R9 recorded as recommended.
Between the seal and GO the owner gave kolt's word twice: the migration to c3f7d1a38 (committed at 8c3f84f) and
a sweep of kolt's 28 TODO/FIXME/BUG lines — five items filed, of which B369 had BROKEN kolt's build: an
internal error, minimized from the app to twenty lines (a generic constructor function with an undeclared
return type loses its parameter), with a one-line workaround in kolt. The order takes one slice of each kind
of work Order 38 left. NATIVE: native-a-39 finishes the emitter's three large refusal classes (F20 — `Hash`,
`lazy` parameters, overloaded operators, 29 of 68) to flip `board.vl`, the exit Order 38 missed; native-b-39
builds the first host a server needs — HTTP over `std::net`, by hand, because `vilan-rt` stays
dependency-free (R1; SQLite is a separate crate and Order 40's) — after F23 and F24. THE RULED PAPERS: reactive-39
builds A110 door 2 (nested-forms ordering, bucketed, on door 1) with A114's scoped effect (R2) and A113's pins
and guide table (R3); collections-39 builds A112 S1 (the delta log lifted into `std::reactive`) and S3 (the
delta-driven `each`) with M82's index for the quadratic scan. THE BUGS: solver-39 (B369 first; the three
refusals of R4; B365, B368 under R5, B367, E199, E208); std-39 (A116's `derive(Json)` crash, A118 under R7,
A117, A115, A119 `when_some` under R6, A72). THE OWNER'S EDITOR ASKS: editor-39 (E207 first, E206, E204,
E202/E203 under R9, E211, E212) and fmt-39, merged last (E209, E210, E205's comment reflow under R8).
hygiene-39 first (N109–N112, B366, D9); papers-39 writes A120, A121 and B363. Ten Opus lanes; ledger next id
549; tracker 122 open at GO.


**MERGED (2026-09-22, tip 051e2254).** Every lane reported and every lane is on `next`, in the brief's order
with one addition: void-result-39 (0976fd19) went first, because papers-39's first report proved B363's premise
FALSE — `void` IS the unit value, `Ok(void)` builds, only the `()` spelling fails — and the owner ruled A107's
stub to `Result<void, RpcError>` the same hour. Then hygiene (a7cc20f4), editor (b5958d7f), std (ca5edca7),
solver (6b4f2f2b + a707bb63 — one hand fold in ui_rows.rs where two lanes appended at the file's end and the
conflict's common suffix fell outside the hunks; and a stale E16 pin re-pointed at E212's contract), reactive
(87c2ee6c + 4f990aa2 — nine goldens runtime-identical; the shared census 121 → 128), collections (0630f769 —
the census 132 MEASURED on the merged tree, the copy-elision TSV regenerated 325 → 349, `delta-law.mjs` the one
golden that moved and runtime-identical), native-a (5d85ac37, clean), native-b (fec0b1fa, clean, after its
agent's own rebase), fmt LAST (051e2254, clean; markdown golden regenerated into the merge). One integrator
commit between: reactive-39's find 2 (1d8dfbb2 — a mirror's `map` is a derivation too; `as_derivation`
exported).

What the order built, in one line each. **`board.vl` FLIPPED** and then a native `std::http` server answered
`GET /` over a real socket byte-for-byte with node on every compared field — the whole set 49 → 69 identical
of 119, 0 differing, 0 broken; the premise "one wall" was wrong (five gaps, six defects, a live native
miscompile fixed on the way), and the host census under-reported (F29). **A110 door 2** made effect order a
contract (derivations to a fixpoint, effects ascending by id) at +23.5 % Ir per wave, and kolt's latch went in
full; **A114** `scoped_effect`; **A113**'s rows measured by subscriber count. **A112 S1** lifted `KeyedCell`'s
log into `std::reactive` without moving a wire byte, with THE LAW in the suite (400 randomized turns); S3 was
WRITTEN and held back by two solver gaps (B378, B379) rather than shipped weakened; **M82** took `reconcile`
from quadratic to linear (355 M → 29 M Ir at 1,000 rows). **B370** was a MISCOMPILE from the owner's kolt
report (`rem(4 / 16)` → 0); **B369**'s and **B366**'s and **B361**'s premises were each wrong in a way the fix
had to correct. The editor got the owner's seven (E207's root cause, both hover lines, field docs, `<` and the
backtick pairing, the completion edit, the macro refusal once); the formatter reads its own output back,
names the diverging line, and can reflow comments behind an opt-in key. std shipped `when_some`, `AttrValue`
for `Option<str>`, `navigate_replace`, `[low, high)`, a 67 → 46 prelude, and — from a papers-39 find — a JSON
reader that poisons on the wrong kind. Papers: A120 (§9.7 of transport-rpc — half wrong as filed, the client
already works), A121 (focus scope), and B363's correction.

The owner asked, mid-order, and each was filed and most ruled the same day: `usize` everywhere (I5 — a
distinct type, literal inference a general law), the `[platform]`/layer question (F27, F28), `[doc(internal)]`
(E213), the `<` overtype VS Code cannot give a server (E214), the reverse of `combine` (A122 — a `std::tuple`
design), and "are we missing signal primitives?" (A123 `and_then`/`switch`, probed working; A124 the
read-tracked `computed` paper with the totality argument against a lazy pipeline; B371, B372 found probing).
Kolt migrated twice at the owner's word (c3f7d1a38, then 4f990aa2c: the latch retired, `when_some` from std,
`conditional_value.vl` deleted, `navigate_replace`, 77 `Nf / M` suffixes dropped with the fold verified in the
emitted JS).

Incidents, each with its rule: the integrator TRUNCATED 25 tracker items with an `open(p,'w')` over a
read of the same file (restored from git; `stamp_items.py` now reads-all-then-writes-then-asserts); a lane typed
`git config <key> <value>` as a read and broke every worktree's signing for an hour (lanes never run `git
config`); 1Password locked mid-order (stop, merge from local branches, stage, sign after unlock — nothing
unsigned); the integrator edited std in the integration worktree while a merge helper's split gate was still
running (set aside within seconds; the rule: never); an `until ! pgrep -f "<helper>"` loop that matched
itself. Score on "the item's text is a hypothesis": papers-39 1 false + 1 half wrong of 3; hygiene-39 1 wrong,
1 stale, 1 mis-sited of 6; solver-39 three premise corrections of nine; native-a's one wall was five.

**SEALED (2026-09-22, tip 49de3915).** One commit after MERGED: the owner reported the language server
aborting on a recursive `SignalMapper` enum mid-seal, and it was the compiler — R10's resource-in-container
walk descends a GENERIC recursive type forever because each substitution mints a fresh type id for the inner
application; a head-keyed guard beside the instantiation-keyed one, four pins (three abort without it; the
fourth keeps R10's diagnostic through a recursive generic's member), B385 filed and fixed in the same hour.
Seal green twice (051e2254, then 49de3915): union 8,093/8,093, the native whole set 119 → 69 identical / 50
refused by name / 0 / 0 / 0, clippy, Windows, audit, fmt, changelog parity 588. CI 35683785688 green 10/10.
Toolchain `vilan 0.40.0 (49de39157)` in both locations; kolt checks clean on it. Ten worktrees reaped. The
sweep: 38 closed, 28 filed (A125, B373–B385, E215–E217, F29–F32, M85, N113–N118), 8 stamped; 123 open.
Papers as built: transport-rpc §9.7 (A120), native-apps §12, diagnostics-standard C3 (N112), the A122/A123/A124
reads on their items. Order 40's queue is in `sweeps/order39/go-items39.json`; the v0.41.0 cut stays HELD
behind one release note for four breaking entries.

## Order 40 — GO 2026-09-22 (cycle 58) off vilan next @49de3915

The owner ruled everything the seal left open in one sitting — A124 R1–R5 after rewriting the item from a read-tracked `computed` into the push-pull pipeline their `reactive2.vl` sketch describes (cold nodes, `get` pulls, no-payload notify, `.cell()` where sharing is wanted, a `Resource` family outside the trait, `dyn Source<T>` at fields with the bare-trait field refused), A125 yes, I5's wire width kept, F32 the `i128` limit, E215 R1–R3, B362 thunk, A120 Q1–Q5 and A121 Q1–Q6 as their papers recommend, N119 wanted — and said "Go with all recs" to briefs40's three GO questions (dyn this order; the cut holds; B382 a recommendation). Twelve Opus lanes: hygiene, solver (B377 first; B378/B379 unblock A112 S3), reactive (A123 + the A124 paper and its S1 probe), collections (A125, A112 S3/S2), dyn (the one language feature), native-a (F18 slice 2: json, the SQLite crate, the rpc server, kolt's server leg), native-b (F30/F29/F31/F21/F22/F26), std (B374/B375 then A120 S1–S5), ui (A121), editor (F27/E213/E214/E216), fmt (E215/E217, last), papers (I5, B382). Ledger next id 550; 124 open.

## Order 40 — MERGED 2026-09-22 @3e4e6c51 (twelve lanes; the S3 lane and the seal to follow)

The integrator's process died mid-order with seven lanes running; their worktrees held every commit, the orphaned test runs were killed by PID, and all seven were relaunched fresh on the `opus` alias at the owner's word with resume prompts (a shell-snapshot quirk hid cargo and node from the tool shell — recorded). Merged in order: reactive-40 (A123, the A124 paper `proposal/reactive-pipeline.md` and its S1 probe measured at a quarter of five map cells per frame), ui-40 (A121 S1+S2, the DOM reads, N113's fourth edge), hygiene-40 (nine items), editor-40 (F27 R6+R2, E213 as `[internal("reason")]`, E216; E214 STOPPED, premise false — a ruling on the client-side override), std-40 (B374, B375, B373, B383, N117, A120 S1–S5 — nothing slipped), solver-40 (B377 miscompile, B378/B379, B362 thunk, B380, B372 premise half false, B381 premise false, B371, the subscript index refusal, and a SECOND B385-class abort found by collections-40 and fixed the same day: a supertrait-blanket recursion), collections-40 (A125 breaking, A112 S2; S3 stopped on that abort, then unblocked), native-a-40 (std::json natively, `vilan-rt-sqlite`, F32's i128 limit, a login server with kolt's shape over a real socket — the builder blocked on F22 + a mutable-Bytes ruling), native-b-40 (F30/F29/F31/F21/F22/F26 with an admission bug fixed in the inherited half-work; rebased by its resumed agent), dyn-40 (`dyn Trait` on both backends, the bare-trait field refused and steered — B4 reopened in scope, B184 withdrawn at fields; eight holes fixed; rebased likewise), fmt-40 last (E215 with std opting in at 84 — its written margin is ~80, the owner may re-rule; E217; the reflow re-run over the merged tree at the fold). Papers-40: the I5 paper landed; B382's premise two-thirds false. Ledger 550–565. Folds: the std `Shared` census twice, E213's four-tuple vs std-40, the `http` EBNF terminal, two by-name test folds, `FormatOptions::comment_width` across the LSP and the playground. Whole native set 121 / 83 identical / 38 refused / 0 / 0.

## Order 40 — SEALED 2026-09-22 @1265ea5d (CI 35790429797 green 11/11)

After the merge: the s3-40 lane, launched off the merged tree for A112 S3, found the compiler UNSOUND before the seal — a blanket's supertrait bound satisfied itself through a depth cap that answered yes when it gave up (B394, fixed within the hour by solver-40b: a structural in-progress guard, and the cap now answers no); the ruled supertrait spelling then proved to break existing programs through a third solver gap (B395), so S3 shipped on the two-bound spelling, declared, with the switch saved as a patch. Seal green on fceb3223: union 8,307/8,307, the whole native set 121 programs / 83 identical / 38 refused by name / 0 / 0, clippy, Windows, audit, fmt, parity 651. CI's first run went red on its doc-test leg alone — two indented lowering sketches in the native emitter's doc comments compiled as Rust, a leg the seal's nextest union skips; fenced as text (1265ea5d), and seal.sh now runs the doc-tests. The second run flaked once on an unpolled descriptor-count pin under load (N126) and went green on the re-run. Toolchain `vilan 0.40.0 (1265ea5d3)` in both locations; fourteen worktrees reaped. The sweep: 29 filed (four archived for the record — B386 the unchecked subscript index, B387 the supertrait-blanket overflow, B388 the native literal width, B394 the unsound bound), 40 closed, 8 stamped; 113 open. Kolt on the new toolchain is red on four errors, all A125's breaking bound, owed by the owner as two hand `Hashable` impls by id, then A123's eight sites and A121's overlay lines. Rulings owed before Order 41's brief: the pipeline paper's Q1–Q5 and dyn-40's four, E222, F33, E215's width. Order 41's queue is in `sweeps/order40/go-items40.json`; the v0.41.0 cut stays HELD behind I5's breaking train.

## Order 41 — GO 2026-09-24 (cycle 59) off vilan next @1265ea5d

Drafted and launched the same day, two days after Order 40's seal, off a `next` that had not moved. The owner's word: "Go with all recs. `isize` can exist too if useful." — R-a the breaking train (I5 S2 + A124 S2c) is Order 42's, merged last with the v0.41.0 cut at its seal, so this order lands everything the train depends on and SAVES both breaking steps as patches with their estate censuses; R-b I5 §11's five as recommended, with ruling 4 relaxed (`isize` permitted if free); R-c `[deprecated]` on a type and no alias; R-d C14 S4 as native-41's tail; R-e M86's borrowing read. Eight Opus lanes (four fewer than Order 40): hygiene-41 first, solver-41 (B395 first, B389 for I5 S1), index-41 (I5 S1 + A126 + E218; S2 prepared), reactive-41 (A124 S2a + S2b; S2c prepared), collections-41 (the A112 switch after B395, S3b, M86), editor-41 (E222, E221, F27 R1, B382, E219), native-41 (F18 slice 3 to kolt's server leg, F34, N125, C14 S4 tail), papers-41 (A122, F27 R3, the cut plan). Briefs at `scripts/integration/sweeps/order41/briefs41.md`; ledger next id 566; 113 open; the CHANGELOG's Unreleased section carries 35 breaking entries. Kolt red 4/4 on the installed toolchain (A125's two hand `Hashable` impls, the owner's).

## Order 41 — MERGED 2026-09-24 @9bc243d9 (all seven vilan lanes + the papers lane; the seal to follow)

Merged in report order rather than the brief's, one hand fold each: hygiene-41 (7f32f846, clean), solver-41 (9ffa397e, clean — B395's real cause was the analyzer's inherited-default candidates, not `subject_applies`; B389's five positions plus a stall step; B397's `combine` miscompile fixed the same day it was found), collections-41 (30dfd05b — a cherry-picked B395 duplicated a CHANGELOG head and left an empty-side EOF conflict in the bounds tests), editor-41 (fee137a9, clean; its node-shape changes broke nothing already on next), reactive-41 (6baa9a17 — one emitted-JS golden moved by two lanes, regenerated and runtime-identical), index-41 (e8d5dda6 — its first merge was ABORTED on a cherry-picked B389 against solver-41's later edits and the lane REBASED; then the native copy census folded and regenerated, and one deterministic gate red: two lanes each wrote 'Fifteen' quick fixes where the merged server builds sixteen), native-41 (9bc243d9 — rebased by its agent onto the six, the copy census regenerated, F34 re-run over a `.cell()` chain and pinned). papers-41 merged to proposals (03c7a5e): the A122 `std::tuple` paper, F27 R3 as platform-coloring.md §8, and the v0.41.0 cut plan whose dry run REFUSED on 1265ea5d — fixed on next the same day (the E122 entry's `commit:` marker, A95's two `deprecates:` markers; `release_files()` derived in N125). Two process incidents: a shared-scratchpad `changelog.py` put native-41's entries into hygiene-41's CHANGELOG (each lane fixed its own side), and the integrator's ad-hoc stamp helper truncated 22 tracker item files (restored from history, nothing lost — stamps go through `stamp_items.py` from now on). The 1Password SSH agent was down for about an hour mid-order; nothing signed around it. Landed on next: I5 S1 (`usize`; S2 prepared, 17 goldens move, kolt five files; `isize` not built), A124 S2a + S2b (S2c prepared and BLOCKED on B408/B398/A25/the no-cycle gate), A112 complete through S3b + the ruled switch, M86 (a `ListCell` write 6.27 M → 39.7 K Ir), F18 slice 3's exit (the rpc server and kolt's server-leg shape native, byte-identical; whole set 124 / 91 / 33 / 0), F33/F34/N125, E222/E221/F27 R1/B382/E219, the solver's nine incl. two miscompiles, hygiene's seven with N121's stack guard, A127. Filed mid-order: 32 items (B397–B412, A129, I6, F35–F40, M87, N127–N131, E223, E224); 145 open before the sweep. Ledger max 569; shared census 143.

## Order 41 — SEALED 2026-09-25 @d65d4e75 (CI 36137702888 green 11/11)

Sealed the morning after the merges, on a tip three small commits past 9bc243d9: the formatter fix E219 itself made necessary (two `[internal]`-labelled signatures in reactive.vl now fit on one line), N120's pin taught the Windows path separator, and the replay pin's base-cache budget lifted for its two legs — the seal's one flake, which a bisect lane proved PRE-EXISTING (LRU eviction under sixteen workers; flaky on the Order 40 seal too; N132 filed for the honest pin). The first seal run was cut off by a session restart and the first CI run went red on exactly those three plus a runner-image setup failure; the second seal ran green start to finish (union 8,524/8,524; doc-tests; the whole native set 124 / 91 identical / 33 refused / 0; clippy; Windows; audit; fmt; changelog parity 688/688) and CI agreed. Toolchain `vilan 0.40.0 (d65d4e759)` in both locations. Nine worktrees reaped. Sweep: 33 filed mid-order (B397–B412, A129, I6, F35–F40, M87, N127–N132, E223, E224), 29 closed, the rest stamped as they reported → **117 open**. Kolt is red 4/4 on the new compiler until the owner adds A125's two hand `Hashable` impls. Order 42 is queued in go-items41: the train's solver blockers first (B408, B398, B406, B407), then I5 S2 and A124 S2c as two lanes merged last with the v0.41.0 cut at that seal, and ten owner decisions before it (A25 at the leaf, the no-cycle gate, `Resource`'s public name, I6, A129, F40, A128's `on_leave`, `peek`, editor-41's five confirmations, B405).

## Order 42 — GO 2026-09-25 (cycle 60) off vilan next @d65d4e75

The train, at last. Drafted and launched the day Order 41 sealed, off a `next` that had not moved, on the ten rulings the owner made that morning plus F27 R3's six and four design items filed from the owner's side questions (A130 `.cell_global()`, B413 the `resource` keyword dissolved into `[resource]`, B414 contextual keywords, B415 `[platform(..)] mod self;`). The owner's word: "Go with all recs." — the cut plan's five yes, `isize` unbuilt, B413 in the train only if ready, `export self::*` deferred, A130's refusal static-only. Eight Opus lanes: std-42 first (A128, the hygiene tail), solver-42 (B408/B398/B406/B407 first, each sha reported the moment it lands, then B405 and the rest), collections-42 (A129, M87), native-42 (F40's crate — kolt's `server.vl` natively as written — and the five native finds), then the breaking train: syntax-42 (`mod self;`, `[resource]`, A122's grammar alternative), index-42 (`usize` S2 from the prepared codemod, one breaking commit), reactive-42 (the combinator flip from the saved patch, one breaking commit, merged last); papers-42 (contextual keywords, the as-built notes, the release-notes summary). Then the v0.41.0 cut after CI. Briefs at `scripts/integration/sweeps/order42/briefs42.md`; ledger next id 570; 121 open; kolt red 4/4 on A125 until the owner's two impls.

## Order 42 — MERGED 2026-09-26 @38f04a50 (all eight lanes; solver-42 in three batches; the seal to follow, then the v0.41.0 cut)

The train arrived. Merged in report order with the train last: std-42 (165d5446), collections-42 (d33d60bb), native-42 (eb14929b — kolt's real `server.vl` builds natively with zero host gaps and its login is byte-identical with node, cross-backend over one database file; the native leak gate; F35–F39), solver-42's first four blockers (eafd61ef — merged before the lane finished, so the train could move), syntax-42 (badf2bfb — `[platform(..)] mod self;`, `[resource]` with the `resource` keyword gone, A122's grammar alternative), index-42 (73de48f6 — `usize` at every std index in ONE breaking commit, 32 goldens moved and every one runtime-identical, S3's casts gone, S4's markers cleared, the wire byte-identical), solver-42's second batch (0ed1864e — B409/B410/B405/the B406 follow-up), reactive-42 (b3174862 — the combinator flip in ONE breaking commit, A25 at the leaf, `.cell_global()` with A130's static refusal, `Resource<T>` public; `Upstream` and the per-node `on_settle` retired on the solver's fixes; shared census 143 → 141), and solver-42's third batch (38f04a50 — B411/B412/B404/E223/B421; one add/add test conflict folded by rebuilding the file from both sides). papers-42 merged to proposals (contextual keywords, the as-built notes, the release-notes summary, C14 re-scoped). Two 1Password outages waited out, one session restart, one lost scratch script recreated durably. Mid-order: 29 items filed (B418–B431, F42–F46, A131–A133, K24, E226, B426…), 47 stamped as they reported; three owner questions ruled the morning after (B400 scope the check, B403 `Type::f()` inside its own impl is `Self::f()`, B420 by-design). Left for Order 43 by name: B400's patch, B401, B403, B418, B419, B423, the phantom parameters, A122's build, F27 R3, kolt's `kolt-i5.patch` + 14 flip edits (the owner's, with A125's two impls). Ledger max 575; shared census 141.

## Order 42 — SEALED 2026-09-26 @6ac84f41 (CI 36253522176 green 11/11; the v0.41.0 cut to follow)

Sealed on a tip three small commits past the merges: the seal itself was green on 38f04a50 the day after the merges (union 8,687/8,687; doc-tests; the whole native set; clippy; the Windows leg now clippy with `-D warnings`; audit; fmt; changelog parity 724/724) and CI agreed on everything but the tree's vilan-source formatter, which flagged three example files the flip had edited unformatted — the same leg that bit Order 41, so `seal.sh` now runs it; the fix (ba1dffb4) was formatting only, and the owner's `CAP` raise to 120,000 (6ac84f41) followed so that v0.41.0's four new breaking entries cannot push one out of the release body. Toolchain `vilan 0.40.0 (38f04a50d)` in both locations; the playground's three exhibits green on it; kolt red on it exactly as the train predicted, with its `usize` patch, its fourteen flip edits and A125's two impls written out for the owner. Eight worktrees reaped. Sweep: 30 filed mid-order and at the seal (B418–B431, F42–F46, A131–A133, K24, E226, N133 …), 36 closed, the rest stamped as they reported → **115 open**. Landed on next: I5 complete (`usize` at every index, one breaking commit, 32 goldens runtime-identical), A124 complete through the flip (one breaking commit; `Upstream` and the per-node `on_settle` retired on the solver's fixes; A25 at the leaf; `.cell_global()`), `[resource]` in place of the keyword, `mod self;`, A122's grammar alternative, kolt's real server native with a crypto crate of one dependency, the native leak gate (first catch: `map_each`), F35–F39, A128, A129, M87, the hygiene tail incl. the honest replay pin, twelve solver fixes incl. four miscompiles. The cut's dry run traced every one of the 724 entries. Rulings the morning of the seal: B400 (scope the check), B403 (`Type::f()` inside its impl is `Self::f()`), B420 (by design), the `CAP` raise. Order 43 opens on the leftovers by name: B400's saved patch, B401, B403, B418, B419, B423, B426–B431, the phantom parameters, A122's build, F27 R3, A133, F45, E224's rule, the kolt patches at the owner's word.
