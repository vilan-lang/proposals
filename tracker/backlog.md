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
rebuilt 2026-08-28 — each waits on a ruling, none blocks unrelated
work): optimistic-lifecycle.md §9 (the paint-less action-state cell;
whether the free `optimistic` survives it), draft-reconnect.md §4
(default debounce for `bind_draft`), bindgen.md §8 Q1/Q2/Q3/Q6,
filesystem.md §12 Q2+Q6 (Q1/Q3/Q5 RULED 2026-08-27; Q4 answered in
code — `Entry` shipped boolean-shaped with S2), css-block.md §12 Q2–Q6
(Q1 answered in code — the trait shipped as `CssValue`; Q3's
v0.40.0-deadline wording is void now that beta is deferred, though the
keyword question itself stands), build-hooks.md §10 Q1–Q7, kolt.local
025(b) (the `serve_build` caching policy — re-opens the fullstack-dx
§5.10 fence), kolt.local 008 (the preflight reset's contents and
opt-in shape), E97 (the mutex-poisoning posture — pick one and write
down why), A26 (does a failed `__attach` get the contract-mismatch
`Closed` treatment — a ruling, not a patch), N17 (the full-repo
per-item migration's open questions, waiting per the 2026-08-26
kolt.local-only scoping), beta.md §5.1 (the tier table — DEFERRED
2026-08-20, re-present with the beta switch's pre-work, not before).
RULED 2026-08-26, as recommended: markdown.md §11 (K13's watcher —
recorded inputs, never the wide glob; built at the docs-app rung).
RULED 2026-08-27, recorded on their items: kolt.local 031 Q1 ((a)+(c)
scoped to `File` — S3 unblocked), Q3 (delete `fs::exists`), Q5 (the
sixteen free functions stand); kolt.local 014 DELETE, merged with 009
into one relation axis — Order 17 builds both.

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
  live use; the clean rerun waits on that run, which is also the first
  live proof of the fmt job and the windows gate legs. LESSONS: lanes
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

## A. Reactive core & UI (`std::reactive`, `std::ui`)

7. **SSR tail** (S3 demand-gated; factoring undesigned)
   STATUS: OPEN (blocked: kolt/walkthrough SSR factoring undesigned; S3 demand-gated on real usage)
   v1 (render + replace) SHIPPED 2026-07-23. Live remainder: **S3, the
   Wire initial-state blob**, stays unbuilt by decision (demand-gated per
   ssr.md §6c — the double-fetch stands); and the S2 amendment's real
   open scope — **kolt and the walkthrough cannot SSR under v1** (views
   read the live rpc client at build time, handlers capture it,
   browser-layer imports), an applicability factoring question recorded
   only in ssr.md's amendment. Resumability = A7b, ssr.md §7.
   History: backlog-2026-07-18.md §A item 7.

8. **UI styling — the tail** (entangled pieces only)
   STATUS: OPEN (blocked: A7/G2 — liveness-tied emission)
   The 2026-08-04 slices closed everything unentangled. Remainder:
   critical CSS and liveness-tied dead-style elimination, riding A7/G2's
   liveness-tied emission — nothing else. Adjacent open find: A22
   (same-family rule ordering). History: backlog-2026-07-18.md §A item 8.

14. **Reactive residuals** (S–M)
    STATUS: OPEN (narrowed — one mechanism + two parked owner questions)
    Live remainder: `batch` async-join drain affinity — `batch` kept its
    `sync` fence at the turn merge; joining an ambient turn from an
    awaiting body is unresolved. The optimistic lifecycle and `Draft`
    auto re-push both SHIPPED 2026-08-04; their parked owner questions
    are indexed in this file's header. History: backlog-2026-07-18.md §A
    item 14.

26. **NEW — a failed `__attach` on reconnect is swallowed, leaving every mirror bound to dead channel ids** (S–M; N16 audit run 2, 2026-08-27)
    STATUS: OPEN (not reproduced — needs a live-server failure harness)
    `vilan/std/src/rpc.vl:1497`, in `reattach_mirrors`:
    `match attached { Err(let _failed) => {}, ... }`. If `__attach` fails the
    `rebinds` loop is skipped entirely: **the socket reports connected, every
    mirror stays pointed at the previous connection's channel ids, and nothing
    reports it.** The function's own doc comment promises three things, and
    the sibling contract-mismatch branch is handled loudly
    (`ConnectionState::Closed` + `close()`, with a comment); the swallow nine
    lines up at `:1489` carries a written justification. This one has neither.
    Zero coverage: `git grep "__attach\|reattach" -- crates/vilan-cli/tests`
    is empty, and `transport_robustness.rs` covers only the happy re-sync
    path. Probably wants the same `Closed` treatment as the contract
    mismatch — which is a ruling, not a patch.

27. **NEW — `std::dom` cannot listen on `window` at all** (M, proposal-first; found by Order 16's `website-harness` lane, 2026-08-27)
    STATUS: OPEN (proposal-first — new public std surface, touches L3's tier sweep)
    `std::dom` binds element listeners only. Everything that needs a
    window-level event hand-rolls a private binding: `std::router` has its own
    zero-arg `window.addEventListener`, and the website has a third. So std
    can never hand a caller a `message`, `resize`, `popstate` or `storage`
    event — which is why K18 could not be fixed in std and had to bind its own
    `external struct` locally.
    The shape is an `on_window` plus a typed event, and the reason it is
    proposal-first rather than a small add: a window `message` handler needs a
    typed `data`, which is a bindgen-shaped question, and the surface lands in
    beta.md §5's tier table. Note the trap recorded by the lane that found it:
    adding `Event::origin()` alone would be **dead surface**, since nothing in
    std delivers an event that could carry it.

## B. Type system & the type solver

3. **Variadic-generics tail** (M–L)
   STATUS: OPEN (remainder: keyof + symbolic pack concatenation, flat-tuple elision, B4-linked dispatch)
   B3a (spread parameters) SHIPPED 2026-08-04; tuple-value spread's
   circle closed. Remainder: `keyof`; symbolic pack concatenation;
   eliding the flat-tuple construction copy; trait-typed-value dispatch
   (→ B4). Record: variadic-generics.md §S/§T. History:
   backlog-2026-07-18.md §B item 3.

11. **`!` / `?.` tail** (M)
    STATUS: OPEN (design-gated only — try-and-lift.md §12.1/§12.2)
    The bare-`?` trait path shipped. Remainder, both genuinely
    undesigned: §12.1 closure `!` (arg-becomes-Result, RpcOutcome×Try
    collision, which closures may host a `!`) and §12.2 Signal/Promise
    Lift opt-ins (Signal::map SUBSCRIBES — `signal?` would mint an
    unowned subscription per render, the A21 leak shape). Recorded §11:
    B29 does not cover a wrong-shaped Lift impl. History:
    backlog-2026-07-18.md §B item 11.

145. **NEW — the two files every lane appends to have outgrown their own governing paper** (M, mechanical; N16 audit run 2, 2026-08-27)
     STATUS: OPEN
     `crates/vilan-core/tests/inference.rs` is **66,830 lines** — the single
     per-case pin surface every lane in every order appends to, which makes it
     the merge-conflict magnet of a six-lane order and the suite's dominant
     compile unit. `crates/vilan-core/src/analyzer.rs` is **38,798 lines**,
     and its own governing paper opens "`crates/vilan-core/src/analyzer.rs`,
     ~9000 lines" (`proposal/analyzer-refactor.md:3`) — a premise stale by
     4.3×, which matters because that paper's plan was costed against the
     smaller number. Neither file is tracked anywhere: `grep -i
     "analyzer.rs\|inference.rs"` over the live backlog returned zero hits
     before this filing. The cheap half is splitting `inference.rs` by
     subject, mechanically; the analyzer half is `analyzer-refactor.md`'s
     premise wanting a re-measure before its plan is trusted.

146. **NEW — the context coverage check's refinement consumes node-owned dispatch sites only** (S–M; found by Order 17's compiler-fences lane, 2026-08-28)
     STATUS: OPEN
     B143's fix taught the const-only check to follow refined dispatch at
     every site class — and extracting the machinery into `dispatch_refine.rs`
     showed the context COVERAGE check (the H8 owner-fence refinement) reads
     refined edges only for node-owned sites: top-level and initializer-owned
     dispatch still take the union, so a forwarding shape there stays
     conservatively fenced. Deliberately preserved during B143 — a bug-fix
     lane should not change shipped coverage semantics — but the two
     consumers of one module now run different diets, which is exactly how
     they drift apart. Also recorded here, B143's accepted residual: an
     iterator-protocol dispatch in a bare top-level `for` statement has no
     graph node and is invisible to BOTH checks.

## C. Memory model

1. **`Weak<T>`** (M)
   STATUS: OPEN (blocked: Tier 2 refcounting, the native arc)
   Fully specified in destruction.md §10 (incl. the scoped
   `get(&self): Option<&T> borrows self` twin from claims-and-epochs.md
   §5a). Deterministic `upgrade() → None` needs a release event, which
   only exists once handles are refcounted; GC-timing `WeakRef` rejected
   2026-07-07. History: backlog-2026-07-18.md §C item 1.

2. **Dynamic rule-4 remainder** (M)
   STATUS: OPEN (blocked: F4's native memory story)

11. **NEW — a resource born and consumed as an expression temporary is never dropped** (M — semantics ruling first; found by Order 17's fs-handles lane, 2026-08-28)
    STATUS: OPEN (proposal-first — filesystem.md §5's amendment records the
    finding; the ruling touches destruction.md's ratified ground)
    `File::open(p).read_at(b, 0)`'s receiver — and equally
    `Database::open(":memory:").exec(…)` — is neither dropped nor rejected:
    the drop planner tracks bindings, an expression temporary has none, so
    the handle leaks until process exit. Value-correct, Drop-net-unreachable,
    and S3's intended idiom makes the spelling routine (the B141 fix made it
    WORK; nothing makes it clean up). The fix is an unratified semantics
    call — scope-end drop of the lifted temporary, statement-end, or reject
    the temporary form — and each option moves observable teardown timing,
    so it is the owner's, paper-first.
   Cross-handle aliased writes (two `Shared` handles, one cell) need
   runtime generations / poisoned views; semantically empty on JS. Build
   with the native memory story, likely debug-mode-only. History:
   backlog-2026-07-18.md §C item 2.

## D. Documentation

5. **Public traction plan** (M; a PLAN first, not execution)
   STATUS: OPEN (blocked: needs a dedicated session with the owner)
   Blogs, website, and other resources for public traction. Candidate
   skeleton in the frozen entry (landing page, "why vilan" essay, deep
   dives, demos, distribution as on-ramp). Public-exposure choices
   interact with the pseudonym discipline; voice/positioning are the
   owner's calls. Overlaps §K's web arc — coordinate, don't duplicate.
   History: backlog-2026-07-18.md §D item 5.

## E. LSP & tooling

37. **bindgen v2 — the remainder** (M–L)
    STATUS: OPEN (remaining: (c) the oxc swap-in seam and (d) the override-table direction, both unscheduled; the 183-globals "read a global" language question; §11.6's shallow `--only` mode; §8 Q1/Q2/Q3/Q6 remain the owner's)
    (a)(b)(e) SHIPPED 2026-08-06 (92.3% of lib.dom declarations). Record:
    bindgen.md §11. History: backlog-2026-07-18.md §E item 37.

62. **NEW — Zed language extension** (M–L; owner's 2026-08-18 list, item 4)
    STATUS: DEFERRED (owner ruling 2026-08-18: a tree-sitter grammar is one more thing to maintain after every syntax change — revisit when the syntax settles, i.e. at or after the beta switch) Strategy ratified 2026-08-25: skeleton-grade static grammars + semantic tokens as truth; E91 makes the tables generated so this grammar is born gated.
    Zed extensions are Rust→WASM: a tree-sitter grammar plus glue
    launching `vilan-lsp` (which already ships per-release). The grammar
    is the bulk of the work and pays twice — GitHub's syntax
    highlighting consumes tree-sitter grammars too. Survey question for
    the order: what the existing `editors/` assets (TextMate grammar?)
    can seed.

69. **NEW — attribute-NAME completion in an element head is a semantics decision** (S–M; deferred by the E67 lane 2026-08-18)
    STATUS: DEFERRED (owner ruling 2026-08-22: if offered at all, the vocabulary should be GENERATED — not handcrafted or hand-maintained; decide later. The generation source is the open question when revisited — §9.3's objection was a second source of truth, which a generated, gated table answers)
    `<div .|>` now completes the View's methods and `<div |>` the dotted
    links + `on:` — but attribute NAMES (`name(..)`, `type(..)`, …) are
    not offered, because the desugar has no table of them to consume
    ("no special-cased names in the lowering table, ever"), and a list in
    the LSP would be a second source of truth with nothing to gate it;
    deriving one from DOM bindings was rejected (IDL property names ≠
    attribute names). Offering them means amending §9.3 (a curated
    vocabulary the desugar validates AND completion reads) — the owner's
    call. Also not attempted: tag-name completion and the child position.
    Record: editing-dx.md §18.

97. **NEW — mutex poisoning is defended in one function and not in its neighbour thirty lines later** (S; N16 audit run 2, 2026-08-27)
    STATUS: OPEN
    `crates/vilan-core/src/lib.rs:235/241` take `PARSE_CLEAN_CACHE` and
    `PARSE_CLEAN_BROKEN` with
    `.unwrap_or_else(std::sync::PoisonError::into_inner)`;
    `lib.rs:269/272/286/296` take **the same two mutexes** with
    `.lock().unwrap()`, as do the five macro-world caches
    (`macros.rs:753/757/812/870/1664/1766`). One file records the defensive
    belief and contradicts it in the same file.
    Every guard was traced: none is held across panic-prone code today, so
    poisoning is not currently reachable. But the fenced pipeline is precisely
    the architecture where a *caught* panic leaves a global poisoned, and the
    consequence is asymmetric — one poisoned cache turns a one-shot compiler
    bug into a language server that answers "internal error: the compiler
    panicked" for the rest of the session. The work is to pick one posture and
    write down why, not to add locks.

98. **NEW — a browser build constructing a `@process` resource draws the coloring diagnostic twice** (S; found by Order 17's fs-handles lane, 2026-08-28)
    STATUS: OPEN
    The second error is for the `drop` edge and anchors inside std's OWN
    source (the std-cache path) — `Database` shows it identically, so this
    is the resource class, not `File`. One user mistake, two diagnostics,
    one of them pointing the user at std's internals. Wants the drop-edge
    diagnostic suppressed or folded into the construction site's; the
    construction-site error alone already names the platform rule.

## G. Macros & const

2. **Const-eval tail** (S–M)
   STATUS: OPEN (remainder is deferred-with-question, const-eval.md §8)
   Remainder, each deferred-with-question in §8: expression-level const
   spans (needs per-node provenance or a spanned IR), cross-analysis
   memoization (cache-key question; measured 7–9% of warm analysis — of
   direct interest to §M's perf arc), a const budget knob. Liveness-tied
   emission stays A7-entangled. History: backlog-2026-07-18.md §G item 2.

7. **NEW — an `emit` kind colliding with the build's own output namespace overwrites real files, source included** (S–M; found by Order 17's emit-kinds lane, probe-verified, 2026-08-28)
   STATUS: OPEN — flagged as an early-fix candidate: the failure writes over
   user source
   `emit("vl", "CLOBBERED")` in a bare build **overwrites the entry source
   file**, exit 0 — probe-verified against the built binary. E94's
   one-segment fence checks the kind's SHAPE, not its namespace, so kinds
   colliding with the leg's own outputs (`vl`, `mjs`, `js`, `chunks.json`,
   the `<arm>.js` family) all write where the build writes. The clean fix
   wants build-hooks.md §5.6's reserved-kind ruling — and G6's pruner
   already ships the refusal predicate; the same list applied at emit time
   is the obvious shape. Record: the emit-kinds lane report (Order 17).

8. **NEW — `run` and single-file watch never sweep the stale CSS sidecar** (S; found by Order 17's emit-kinds lane, 2026-08-28)
   STATUS: OPEN
   The build path calls `sweep_stale_sidecar`; the `run` and single-file
   watch paths do not, so a stale `<entry>.css` survives `vilan run` after
   the styles that produced it are gone. Pre-existing asymmetry adjacent to
   G6's fix (whose per-kind prune IS wired into every path — this is the
   older sidecar sweep lagging behind that standard). One call plus the pin.

## I. Collections

2. **Fixed-arrays tail** (M; fixed-arrays.md §7)
   STATUS: OPEN (blocked: const-generics design — what `const N` means)
   Const-named / const-generic lengths (`[u8; SIZE]`, `<const N>`):
   proposal first (the constraint form, the staging fork — const-eval is
   post-analysis, lengths are needed mid-fixpoint). Then `List` ↔
   `[T; n]` conversions, slicing (wants a range type), generic
   `[T; N].len() → N`. History: backlog-2026-07-18.md §I item 2.

3. **Iterator adapters — the remainder** (S–M)
   STATUS: OPEN (remaining: S6/Iterable under B4)
   The arc SHIPPED 2026-08-06; §4 option (ii) REFUSED by owner ruling.
   Live remainder: S6/`Iterable` waits on B4 (trait-typed-value
   dispatch). Record: iterator-adapters.md §11. History:
   backlog-2026-07-18.md §I item 3.

## J. Concurrency

4. **Free-spawn lint** (S once unblocked)
   STATUS: OPEN (blocked: Tier 2 counted closure environments)
   The rule ("a spawn happens inside a `nursery` extent or an
   `OwnedNursery.enter` — anything else is a lint") cannot ship while
   std's three legitimate free spawns remain (Draft.commit, the RPC SSE
   pump, streaming `on_open`); they become ownable with §10's counted
   captures. The lint ships the same day they migrate, zero baked-in
   exceptions. History: backlog-2026-07-18.md §J item 4.

5. **Async recorded opens — the deferred pair** (S each)
   STATUS: OPEN (deferred: demand-gated)
   Live remainder: per-task cancel handles (resolved-for-delays by
   `std::time::Timer` 2026-07-28; handles stay deferred — no field case
   has asked for cancelling a computation, only a delay); the free-spawn
   lint rides J4. Everything else in the entry shipped. History:
   backlog-2026-07-18.md §J item 5.

## K. Web presence (site, playground, docs delivery) — NEW SECTION

The website, playground, and docs repos had no tracker home; that gap is
part of why planning fragmented. Spans `vilan-website` and
`vilan-lang.github.io`; compiler-repo work stays in §A–§J.

5. **The design language — adopt** (M–L; owner's items 3 + 11)
   STATUS: OPEN (RATIFIED 2026-08-18; SLICE 1 SHIPPED 2026-08-18 — web-tokens → website@561dcff; SLICE 2 SHIPPED 2026-08-18 — web-slice2 8c98bbc → website@6e549d2, deployed, with K9 (dropped on evidence) and K10 (editor theme reads tokens via CSS vars); owner on merge: "could use some refinement, but definitely moving in the right direction" — a refinement pass rides slice 3 or its own item once the owner names the specifics; slice 3 = the docs, with K6 — its design now lands in docs-port.md
   §3.1 S2–S3 (mdBook is token-driven: 42 CSS custom properties per theme
   in one `variables.css` override, and it already ships a light/dark
   picker); K6 RULED 2026-08-19 — SLICE 3 SHIPPED 2026-08-19, both halves: the book (k6-book → next 0eaa38c0: `variables.css` role tokens on `html.light`/`html.navy`, design-language.md §2.5 the light palette; live at the v0.35.0 fold) and the site (web-chrome + web-art-light → website@cb3752a, deployed: every token carries both values behind `prefers-color-scheme`, the art re-lit onto the roles, `shadow`/`art-error` tokens; owner: "Approved"). What stays open under K5: the refinement pass the owner named at slice 2 (specifics pending), and K10's one-token-source generation now that three mirrors exist)
   design-language.md is ratified: kolt's `visual-overhaul-2` role
   tokens (`up`/`down`/`stroke`/`primary`, verbatim) carrying the brand
   palette, tool surfaces fully utilitarian, the hero fenced as the one
   indulgence, CommitMono V143 with the owner's feature settings (§2.3),
   light theme with K6, editor stays CodeMirror 6. Slices: **(1)** the
   token system in `theme.vl` + site chrome (masthead, page, footer)
   restyled onto it + CommitMono self-hosted for code blocks + K1's nav
   link; **(2)** the playground page + editor onto the tool register,
   with K10 (generated editor theme) and K9; **(3)** the docs, riding
   K6. Every slice: before/after screenshots for the owner's review
   BEFORE merge — the website deploys on every push to `main`.

8. **Website features & small visual upgrades** (S–M each; owner's item 11)
   STATUS: OPEN (umbrella — refine into concrete items under K5's ratified language)

13. **NEW — the docs on the vilan framework, the port proper — behind its markdown prerequisite** (L; filed by the K6 ruling 2026-08-19)
    STATUS: OPEN (STEP 1 SHIPPED 2026-08-25 — std::markdown built strict per the ruled markdown.md (fa742f146 merged 7b9b55ce): 456/456 mdBook-exact anchors with a real-build golden, 0.9 ms/page, `Items` carries BLOCK bodies (the build's correction, OWNER NOD 2026-08-25; golden regen rule also nodded); STEP 2 SHIPPED 2026-08-26 (lane k13-step-2, 5d434d29) — `std::asset::read` is the channel’s input direction (package-root-relative, escape-refused, const-only under emit’s machinery), every read a tracked build input (watch trigger + per-leg skip + in-process pin), the fuel budget 1M → 16M on measurement (the largest page parses at 2,001,457 fuel, pinned against the real book page); the watcher question RULED 2026-08-26 with Order 12's answer batch (markdown.md §11 carries the record): the recorded-inputs mechanism, never `**/*` — build the recorded-inputs watcher (dynamic `workspace/didChangeWatchedFiles` re-registration from `Program::const_input_files`) when the docs-app rung lands, and accept next-edit freshness until then; NEXT: the router/docs-app rung; STEP 3 DONE 2026-08-20 — the site took rung 2 whole, website@6036e21, record fullstack-dx.md §16.11: pixel-identical both pages both schemes, the shells deleted, the hatch census is the ladder's fit report, §15.2's declined helpers all found customers → E79)
    The owner's literal item 10 ("transitioning the docs to the vilan
    framework"), filed as its own item so it stays reachable while K6
    ships option B. docs-port.md §2.1 proved the port is *unavailable*
    today, not merely expensive: a `const` cannot read a file nor return a
    `View`, and the 1M fuel budget is exhausted by a char-scan of a page
    the size of the book's largest. §3.3 gives the honest order: (1) a
    markdown story — a `std::markdown` (or package) parser producing a
    plain-data AST, or a `[build] run` pre-step emitting generated `.vl`
    from `.md` (no compiler change; the cheaper proof); (2) a const input
    channel, only if the parser is to run at compile time, with the fuel
    question answered first; (3) a router and rung-2 adoption on the site
    (`Document::of` + `serve_build` + `split = true`), which fullstack-dx.md
    §16.2 notes the compiler repo cannot yet demonstrate either (E65).
    Each step is independently valuable — the test of a real prerequisite.
    **L10's paper (std-shape.md, 2026-08-20) names `std::markdown` as the
    first candidate official package — its §6 Q4 asks whether the markdown
    story should be built package-shaped from day one.**
    The 32 LSP deep links and 417 in-book links pin mdBook's anchor
    algorithm as a compatibility surface (§4 Q3) that any renderer must
    reproduce. Record: docs-port.md §2.1, §3.3, §4 Q1.

## L. Release engineering & beta — NEW SECTION

The alpha→beta transition. The *contract* is RATIFIED (process.md §5,
2026-08-07: three promises, no spec freeze, the four-condition trigger,
the v0.40.0 jump); beta.md (RATIFIED 2026-08-18) is the execution
charter — its status block also records the owner's "should we defer
beta?" and the answer: **the trigger already defers the declaration**
(none of the four conditions hold today; (b) earliest 2026-08-29; (c)
waits on B73; (d) on D5), so the pre-switch items below proceed at
ordinary priority as low-regret hygiene, and nothing beta-branded ships
publicly until the trigger fires. The alpha framing in README/CHANGELOG
is **correct until the switch commit** — do not "fix" it as rot.
(L1 — ratify beta.md — CLOSED 2026-08-18; the archive's first entry.)
**DEFERRED until further notice (the owner, 2026-08-26):** "Things are
moving too quick, public traction hasn't taken place. We have no
userbase." This supersedes the trigger arithmetic above — stop the
per-train (a)–(d) accounting; the switch reopens on the owner's word,
and D5 (public traction) is the real gate. Everything else in this
section keeps its ordinary low-regret priority; the alpha-framing rule
stands unchanged.

3. **std tier sweep** (M)
   STATUS: OPEN (table DRAFTED 2026-08-20, beta.md §5; ruling DEFERRED 2026-08-20 by the owner — "the answers to those questions might change from now until we officially enter beta" — re-present §5.1 with the beta switch's pre-work, not before; the docs page lands at ratification)
   The census: 56 public modules (54 std + 2 macro_std; canvas has no
   module yet — §4 Q4's Tier 3 binds when it lands). Proposed: 32 Tier 1,
   23 Tier 2 (with promote-on-quiet clocks and holds where an open item
   gates), 1 Tier 3 (`into`, B127's deletion question). §5.1's arguable
   rows: iterator straight to Tier 1; operators under B11's open item vs
   an item-level carve; into at Tier 3; process/dom at Tier 1 against
   their Tier-2 directories; wire's tier vs §5.2(3)'s unconditional
   Breaking pricing.
   Enumerate the public std surface, propose the Tier 1/2/3 table
   (beta.md §3.2), owner rules, docs publish it.

8. **Contribution scaffolding** (M)
   STATUS: OPEN (blocked: D5 — deferred with it, process.md §9.2)
   CONTRIBUTING.md, SECURITY.md, CODEOWNERS, issue/PR templates,
   private vulnerability reporting. Revisit when D5's session happens;
   scaffolding for an audience arrives with the audience.

15. **NEW — release artifacts are checksummed but unsigned** (M; N16 audit run 1, 2026-08-26)
    STATUS: OPEN — **the S half SHIPPED 2026-08-27** (Order 15, lane security-tail): `install.sh` fails closed, refusing rather than warning when no sha256 tool is on PATH, pinned. The M half REMAINS and is the whole of this item now: `sha256sums.txt` is produced and consumed same-origin (release.yml → the release assets), so it authenticates the TRANSFER and not the pipeline that produced it. Signing/provenance/attestation is the work; sensibly deferred until D5 gives it an audience, and the CHANGELOG says so explicitly rather than implying coverage.
    SHA256SUMS is produced and consumed same-origin (release.yml → the
    release assets), so it authenticates transport, not the pipeline;
    no signing/attestation. And install.sh skips verification entirely
    when no sha256 tool is on PATH rather than refusing. Fix the S half
    now (fail closed); signing/provenance is the M half — sensibly
    deferred until D5 gives it an audience, but recorded. Record:
    audit-1's report (Order 11).

16. **NEW — `std::markdown`'s ~20 strict-parse refusals enter the diagnostics ledger** (S; N16 audit run 1, 2026-08-26)
    STATUS: OPEN
    markdown.vl ships ~20 `ParseError` messages — the runtime-refusal
    class of ledger rows 230–239, un-rowed, every one carrying the
    em-dash style the process-layer REWORD parking already covers. Owed
    as their own verdict batch (wording B-rules + C2 pins), priced with
    the same owner ruling on std refusal style (beta.md §3.1's identity
    surface). Record: audit-1's report; the ledger's Order 11 batch
    note.

## M. Performance & footprint — NEW SECTION

Owner's items 7 (perf) and 8 (leaks). The 2026-08-18 survey found the
seams already cut: the four pipeline phases are independently callable
library entry points (`parsing::parse` → `analyzer::analyze` →
`post_analysis_passes` → `transformer::transform`, the same seam
`VILAN_PHASE_TIMING` marks), a purpose-built per-site leak harness
exists (`leak_tally` + vilan-lsp's `leak_measurement` module), and the
suite's liveness bounds already use measured-reference thresholds
(`support/mod.rs`'s `reference_compile()`), never fixed seconds.
Corpora measured: todo 119 lines (smoke only), kolt 943, website 2,996,
std 15,024 (the cold-compile stand-in).

10. **NEW — mechanize the BASE_CACHE transmute's completeness claim** (M; N16 audit run 1, 2026-08-26)
    STATUS: OPEN (deferred: nice-to-have)
    The unsafe audit verified the safety argument, but one leg rests on
    a ~150-field hand-maintained completeness claim; a compile-time
    assertion or generated check would close the honest gap. Record:
    audit-1's report (Order 11).

## N. Hygiene & rot — NEW SECTION

Owner's items 1–2 (repo refactoring, rot, consolidation, README;
rotted/poorly-written code). Seeded by the 2026-08-18 rot survey (all
four repos, read-only). What the survey found and this order already
fixed in the same sweep: the proposal index's stale/missing rows,
AGENTS.md's dead arc pointer, roadmap.md routing readers to the dead
backlog (banners landed with the re-baseline). What it cleared as
NOT rot: `about.hbs`/`about.toml` (live, `cargo about` consumers),
npm's `0.0.0-placeholder` and the homebrew formula's 0.14.0 seed pin
(both deliberate and test-documented), the bindgen module's 63
`TODO(bindgen)` hits (an emission vocabulary, not debt), and the
README/CHANGELOG alpha framing (correct until the beta switch — §L).

8. **Pages repo housekeeping** (S–M umbrella)
   STATUS: OPEN (narrowed 2026-08-20 — the three orphaned brand files are deleted and the 404 shim's sunset is PROPOSED in the pages README ("at the beta switch", proposed-not-ruled — the one open half); N12's README shipped 2026-08-19; K12/N13 closed 2026-08-20)
   The local checkout is 41 commits behind its origin (refresh before
   trusting any file-presence claim there — the survey's "no sitemap"
   class of findings were checkout staleness, not site defects). Then:
   no README distinguishing bot-generated files (`docs/`, `index.html`,
   `client.*`, `playground/` — pushed by two different workflows) from
   hand-owned (`assets/`); three orphaned brand files nothing
   references (`icon-512.png`, `light_lockup.png`,
   `dark_wordmark_flat.svg` — delete); the pre-v0.15 `404.html`
   deep-link shim deserves a recorded sunset condition. (The
   `book.toml` leak and mdBook fonts rode K6 — both closed 2026-08-19;
   the README is N12, shipped the same day, and names `chrome/` as the
   new bot-owned prefix; the stale-checkout note is moot — pulled
   2026-08-19; wasm retention is K11.)

16. **NEW — the recurring codebase audit** (RECURRING; the owner's standing ask, filed 2026-08-25)
    STATUS: RECURRING — one audit lane every other work order, rotating
    focus. Track here: last run Order 11 2026-08-26 (security +
    diagnostics; L13's re-key carried); **RUN 2 CLOSED in Order 16
    (2026-08-27), three orders late** — 13 findings filed (A26, B144, B145,
    E97, N19–N25) plus one S-sized tidy landed inline with its own gate;
    grades: error handling B+, dead code A, tidy & structure B−, stale-path
    class B. Its sharpest structural find: the documents agents read first
    (`AGENTS.md`, `.claude/**`) are the only documents in the tree with no
    gate, which is why a crate went five days missing from the repo map and
    why three agent definitions pointed at a path that did not exist. It was — the line said "next due Order 13"
    and Orders 13, 14 and 15 all shipped without an audit lane, which is
    the failure this line exists to make visible and did not. Run 2's
    dimensions: error handling, dead code, tidy & structure. Next due
    **Order 18** (update this line each run — and if it goes stale again,
    the fix is a gate, not a bigger note).
    A standing audit over all four repos (vilan primary; website,
    proposals, pages secondary), SURVEY-FIRST like the 2026-08-18 rot
    survey: findings are FILED as tracker items with evidence, never fixed
    inline — except S-sized tidies the lane can land with pins. Each run
    picks 2–3 dimensions from the rotation and states which; the report
    grades what it swept so coverage is honest across runs. The rotation:
    - **Security**: `cargo audit`/dependency advisories; the `unsafe`
      inventory (each block's SAFETY comment against reality — the
      BASE_CACHE transmute class); injection/escaping surfaces (the
      website's served HTML, the playground share codec, the HMR
      endpoints); secrets/tokens in tracked files; the release pipeline's
      supply chain (pinned actions, checksum gates).
    - **Tidy & structure**: directory/module layout drift, files that
      outgrew their name, orphaned assets/fixtures, stale scratch or
      generated files tracked by mistake.
    - **Dead code**: unreferenced items the compiler cannot see (feature-
      gated, test-only helpers gone stale, cfg'd-out paths), dead exports,
      the `#[cfg_attr(not(test), allow(dead_code))]` inventory re-argued.
    - **Error handling**: `unwrap`/`expect`/`panic!` in non-test code
      audited against the panic-fence and Result discipline; swallowed
      errors; error messages that lost their context.
    - **Diagnostics**: a ledger sweep (with L13's mechanical re-key),
      heads that drifted from house rules, missing C3 notes/steers on
      newer refusals.
    - **Debugging**: VILAN_PHASE_TIMING/debug-dump coverage of newer
      passes; leak_tally site coverage; whether the perf baseline still
      reproduces.
    - **Tests**: vacuous pins (plant-audit a sample), #[ignore]d pins
      whose reason expired, per-case gaps on newer features, goldens
      whose regeneration story rotted, suite wall-time creep.
    Each run ends by updating this item's last-run/next-due line and
    filing its findings; a dimension with zero findings says so
    explicitly (absence of evidence recorded, not implied).

17. **NEW — per-item tracker files: restructure the repo under the `projects/` format** (M, proposal-first; the owner's ask, 2026-08-26)
    STATUS: OPEN (SCOPED 2026-08-26 by the owner: kolt.local only for
    now — but "note that it needs to expand out to everything at the
    end"; the full-repo migration is the recorded end state, its open
    questions below wait until then)
    One file per item (`tracker/items/<ID>.md`), an INDEX of open
    items, a tombstone archive — the owner's format, piloted in the
    gitignored `projects/kolt.local/` and specified in
    `projects/README.md` (both landed 2026-08-26). The motive:
    per-item files let subagents read, edit, and close items without
    contending over one long planning surface — "ideally, the rest of
    the repo would be restructured under this format too", and that
    restructure is this item. Open questions for the ruling: whether
    the A–N backlog migrates wholesale or per-section; ID stability
    across the move (numbers are stable identifiers, never reused);
    what the hygiene gate's index-completeness check becomes when
    INDEX files multiply; how process.md §5's ratified surface names
    carry. Relation to N15: orthogonal — N15 moved the directory 1:1
    and ruled "ONE surface for tracking" (§8); this changes the
    surface's internal grain, and a ruling here amends that sentence,
    not the move.
20. **NEW — `.claude/` is live configuration that no gate can see, and it had three dead pointers in it** (S; N16 audit run 2 + the Order 16 launch, 2026-08-27)
    STATUS: OPEN — the three instances are fixed; the structural gap is the item
    `crates/vilan-cli/tests/hygiene.rs:22` scans `git ls-files`, and
    `.gitignore:3` ignores `.claude` — so every file agents read *first* is
    the one class of file with no gate at all. Three instances found, all
    fixed 2026-08-27: (1) all three `.claude/agents/*.md` pointed at
    the pre-N15 checkout path for `AGENTS.md` — the repo root as it stood
    before N15 split the toolchain and proposals repos — so every subagent
    began by reading a missing file; (2) `.claude/settings.local.json` grants
    a read on **another user's home directory** — a cargo glob rooted at a
    home-directory entry for a user who does not exist on this machine, with a
    doubled separator — and `Bash(node src/vilan-source/*)`, a path that has never
    existed in this tree; (3) `vilan-reviewer.md:13` hardcodes
    `git -C <main checkout>`, contradicting AGENTS.md's "git is scoped to your
    worktree", so a reviewer launched from it reviews the wrong diff, and
    `vilan-implementer.md:35` still forbids editing `vilan/proposal/`, a
    tombstone directory since N15.
    Also unowned: `.claude/agent-memory/` is 62 files / 472K nothing has
    written in 26 days, with a `MEMORY.md` describing a pre-N15 world. Retire
    it or revive it; half-alive is the worst of the three.
    The fix is a gate, not another fix pass: have `hygiene.rs` check
    `.claude/agents/*.md`, `.claude/settings*.json` and AGENTS.md-referenced
    paths **for existence**, not just for the three needles it looks for now.

21. **`cargo fmt` is gated; the clippy and cargo-audit legs remain** (S; N16 audit run 2, 2026-08-27; narrowed 2026-08-28)
    STATUS: OPEN — the formatting half SHIPPED 2026-08-28 (Order 17, lane
    release-gate, vilan 3eeb5dea): the drift reformatted (whitespace-only,
    proven), `rust-toolchain.toml` pins 1.90.0, a `fmt` job in ci.yml feeds
    `check` — with the discovery that the toolchain file OUTRANKS the CI
    action's `rustup default`, so the suite/wasm/release legs now declare
    `RUSTUP_TOOLCHAIN: stable` explicitly or the pin would have silently
    dropped their cross-compile targets. The live remainder is the rest of
    the item's own list: no clippy leg, no `cargo audit` leg. One clippy
    candidate already recorded: the dead `Document::use_in_entry_or_generated`
    warning three Order 17 lanes each reported. Archive holds the full
    original finding.
    Reproducible, exit 1, four hunks in two files
    (`crates/vilan-cli/tests/fs.rs:927`,
    `crates/vilan-core/tests/mime_table_sync.rs:76/157/438`, rustfmt
    1.8.0-stable). CLAUDE.md makes `cargo fmt` a per-change rule, so three
    separate Order 16 lanes each hit this churn, each reverted it, and each
    reported it — the drift is now costing every lane a decision.
    `ci.yml`'s jobs are `changes`, `test`, `wasm`, `check`: **no
    `cargo fmt --check`, no clippy, no `cargo audit`.** And there is no
    `rust-toolchain.toml` and no `rustfmt.toml` while CI tracks a floating
    `stable`, so a future rustfmt default silently reformats the tree for
    whoever runs it next with no gate to notice. Verified safe to reformat:
    the `mime_table_sync` gate compares `CURATED.to_vec()` as values, not
    text. Fix is pin the toolchain, land the reformat once, add the check.

23. **NEW — 37 `pub` items in `vilan-core` are never referenced outside their own file** (S, mechanical; N16 audit run 2, 2026-08-27)
    STATUS: OPEN (low priority — over-exposure, not rot)
    Not dead, over-exposed: e.g. `StyleCategory`/`StyleMethod`
    (`formatter.rs:524/563` — 67 and 66 in-file uses, zero elsewhere), all six
    analyzer constraint structs (`analyzer.rs:1673–1847`), `manifest.rs`'s
    five section types. `pub(crate)` or private would do, and the crate
    boundary would then mean something. Recorded with it, because the audit
    re-argued it rather than counting it: exactly one item is *actually*
    unreferenced — `leak_tally::outstanding_total` — and the verdict is
    **KEEP**, because it completes a symmetric instrument API and deleting it
    leaves the instrument lopsided.
