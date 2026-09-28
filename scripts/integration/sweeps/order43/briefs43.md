# Order 43 — AFTER THE TRAIN: kolt's mirror finds (A134–A137), the unsound `&mut`-place assignment (B433), the solver's leftovers, the extension the editor never received (E222 shipped, E229), A122's build and the contextual keywords (drafted 2026-09-28, off vilan next @762c6aa5; AWAITING GO)

**Base.** Order 42 sealed at 6ac84f41 on 2026-09-26 and v0.41.0 was cut at that seal; v0.41.1 (B432: the
playground wasm's `Instant::now` abort; N134, N135) was cut from `release/0.41` on 2026-09-27 and FOLDED:
`origin/main` = 1a33340f (the fold), `origin/next` = 762c6aa5 (main merged back; CI 36358009990 green).
Nothing has landed on next since the fold — the CHANGELOG has NO `## Unreleased` section today (0
entries, 0 breaking). Toolchain `vilan 0.41.1 (1a33340f2)` in both locations. Ledger next id **576**
(max 575). Tracker **124 open** after today's seven (A134–A137, B433, E228, E229). Shared-census literal
141 (the Order 42 seal's, unchanged). `release/0.41` is KEPT until v0.42.0 ships (releases.md §7.3 step
5). Kolt is at f04d4cb (`wip`, the owner's) plus five uncommitted files — the owner's own edits and,
at the owner's word on 2026-09-28, the integrator's model.vl: A134's seven sites, A136's memo shape
(`.cell_global()` in the makers, the lease at the call site), `get_channels` on the demand shape; kolt
checks 0/0, builds and formats clean, its browser runtime UNVERIFIED all week. The owner's VS Code runs
extension **0.40.0** (`~/.vscode-server/extensions/vilan-lang.vilan-0.40.0`) while the tree is at 0.41.1
with E222's `vilan.autoClosing.generics` — see R-a.

**The shape.** Not a train. No breaking commit is planned and no cut is proposed at the seal (R-g):
the `## Unreleased` section is empty, and everything below is a fix, a build of a ruled design, or a
paper. Three things set the order's priority. **First, B433 is UNSOUND** — an assignment whose target
is a call returning `&mut T` is checked against nothing (`Shared<Option<i32>>.write() = 5` compiles and
emits `cell.v = 5`; every read of the slot then misreads it) — and it bit kolt silently the same day it
was found: the owner's own cache line never cached. solver-43 lands it first. **Second, the week of
kolt on the flip produced four std finds in one file** (A134–A137, `sweeps/order43/probes/kolt-mirrors/`):
a handle stub inside a cold `and_then` re-mints per pull, the very shape the Order 40 census prescribed
(A134); an `[rpc]` body returning `.map(..).cell()` defeats A92's dedup and leaks a process-lifetime
subscription per call (A135); a `Memo` maker's `.cell()` dies with its first caller (A136); two mirrors
of one deduped channel misbehave in-process (A137, an observation). reactive-43 builds the two
recommended doors — the client dedups mirrors per ORIGIN (the twin of A92), the dispatcher runs
handlers under the connection's owner — and writes the two rules where the next reader will look.
**Third, the owner's ask on angle brackets is a DELIVERY gap, not a missing fix**: E222 landed in Order
41 with the `type` override AND the setting (`vilan.autoClosing.generics`, default on; `false` is the off
switch), the release ships `vilan-vscode.vsix`, and the installer never installs it (E229). editor-43
closes that gap first, then E228 (completion after `Shared.read().`), then the keyword-table drift
(E225 + K24 from one generated source). Around those: the solver's leftovers by name (B400's saved
patch, B418, B403, B401, B419, B423, B426–B431, B424's ruling), A122's build in its own lane after the
solver (the Tuple trait, `TupleKey`, `divorce`, the for-over-a-mapped-tuple rule — Q1–Q7 ruled at
Order 41), B414's contextual keywords per papers-42's paper, native's five finds (F41, F42, F44, F46 +
F45 if ruled), the hygiene tail, and papers-43 (E227's hint attribute, M88, C15, A131).

**Seven lanes + papers.** Merge order: hygiene-43 (droppable, first), solver-43, tuples-43 (rebased onto
solver-43's merge), reactive-43, native-43, editor-43, syntax-43 (rebased; touches the lexer, the
parser, the formatter, the grammar). papers-43 merges to proposals only. No cut after the seal:
toolchain both locations from the sealed tip, AND the vsix into the local vscode-server (E229 door d).

## Asked at GO (the owner)
- **R-a — angle brackets.** The fix and the switch exist (E222, Order 41): with the 0.41.1 extension a
  `<` in type position places its `>` and typing `>` steps over it; `"vilan.autoClosing.generics":
  false` turns it off. Today's one-line fix for your editor, from the vilan checkout, then reload:
  `code --install-extension vilan/editors/vscode/vilan-0.41.1.vsix --force`. Order 43 makes delivery
  automatic (E229: install.sh/ps1 install the vsix when `code` is on PATH; the extension warns on a
  server/extension version mismatch; the seal's toolchain refresh installs it locally). E214 closes on
  your confirmation that the doubled `>` is gone with 0.41.1 — or stays open with the symptom. Rec: yes
  to all three doors; the marketplace publish (door c) as its own L-item after.
- **R-b — B433's rule.** The assignment through a `&mut T` place takes the plain place's rule (refuse
  with `Expected T, but got U`); red-first pins for `i32`/struct/`List` into `Option<..>`; then a sweep
  of std, the examples and kolt for `write() = <bare>` at an `Option`-typed cell (kolt: none left after
  today). Rec: refuse; no lenient door.
- **R-c — the mirror doors.** A134 (a) + (c): the generated client dedups mirrors per origin (method +
  described args), released with the last lease, and the stub's doc + remote-sources.md say a stub in a
  cold select is idempotent because of it; A135 (b) + (c): handlers run under the connection's owner,
  and a handle-returning `[rpc]` whose tail is a derivation constructor gets a warning with the memo
  steer; A136 (a) + (b): memo.vl's doc rewritten (what the maker BUILDS outlives the caller) and a
  warning for `.cell()`/`effect` syntactically inside a `get_or` maker. Rec: all as recommended; A137
  is settled over a socket before anything is built on it.
- **R-d — A122 builds now** (Q1–Q7 ruled 2026-09-25) in tuples-43 with B183 and B399. Rec: yes.
- **R-e — B414 builds per the paper** (`with`, `as`, `only` … contextual; D14's spec list corrected from
  the same table); `self::` paths / `export self::*` stay DEFERRED. Rec: yes / deferred.
- **R-f — E227 is a paper first** (the `[hint(Trait<..>)]` attribute; Q1 the marker's spelling, Q2
  nested nodes, Q3 conditional impls, Q4 `vilan.inlayHints.abbreviate`, Q5 hover shows both). Built in
  editor-43 only if the marker is ruled at GO. Rec: paper; build in Order 44.
- **R-g — no cut this order.** `## Unreleased` is empty and nothing here is breaking (A134's dedup is
  additive; B433 refuses code that was already wrong). v0.42.0 waits for a breaking need. Rec: hold.
- **R-h — B424** (an unconstrained generic at a call — `err.or_else(|e| Ok(7))` leaves `F` unbound): a
  RULING item; rec: refuse with a steer to annotate, as B392's family does.
- **R-i — F45** (the native HTTP server's graceful stop): build (a `stop()` handle + SIGTERM) or park.
  Rec: build, S.

## Mechanics (every lane)
briefs42.md's "Mechanics" stands in full (briefs41's + Order 41's rules: never `git config`; the item's
text is a HYPOTHESIS — verify the premise and say so; a passing probe must be shown to BUILD something;
every std-touching lane gates `-p vilan-cli --test native_differential` default AND
`VILAN_NATIVE_DIFFERENTIAL=1`; the golden suites are `corpus`, `split`, `examples`,
`copy_elision_census`; a `-p <crate>` spec with zero tests exits non-zero; probe over a scratch copy,
never `vilan build vilan/test/<x>.vl`; a lane answers no question itself — SendMessage; worktrees
`vilan/.claude/worktrees/<lane>-43` off `origin/next` @762c6aa5, never the main checkout, never `git
stash`, never push; one commit per item with its CHANGELOG entry under a fresh `## Unreleased` head
(the first lane to commit CREATES the section; family markers as before); ledger rows written `NEW`
from id 576; scratch files under `scratchpad/<lane>/`; a lane that needs another lane's fix
cherry-picks for its own gates only and rebases before it reports; count words in docs pages are
declared in the report; scratch targets under the worktree's `target/`; a 1Password outage is waited
out; the seal runs `cargo test --doc`, the whole-set native differential and CI's vilan-fmt leg; goldens
two lanes moved are REGENERATED over the merged tree; tracker writes through `file_items.py` /
`stamp_items.py` / `close_batch.py`; model Opus, never Fable; the PATH export; `touch build.rs` when the
sha goes stale), PLUS this week's lessons as RULES:
- **An in-process probe is not a socket probe.** A133 and A137 both differ between `duplex_pair` and a
  socket. A mirror find is verified over a socket (the `reactive_channels` pins, or the todo example's
  server) before it is called a mechanism; an in-process-only observation is filed as one.
- **A cold select must be pure, and the doc says so where the impure call is minted.** The Order 40
  census prescribed `and_then(|client| client.get_x())` and it never worked; a lane that recommends an
  app-side spelling RUNS it (the probe dir is the place) before the census says it.
- **A `.cell()` inside a maker, a memo, a module-level cache or any structure that outlives the caller
  is `.cell_global()` or a bug** — reactive-43 writes the rule into memo.vl and remote-sources.md;
  every lane reads it.
- **A repro prints through a typed helper**, never through a method whose resolution the probe is
  itself testing (A137's `sub` observer typed as `List<str>` where `Option<List<str>>` was expected —
  noted on A137, not filed).
- **The toolchain refresh at the seal includes the extension** (E229 door d) — the integrator's step,
  every seal, until the installer does it.

## Lane hygiene-43 — DROPPABLE, lands FIRST: N133, N106, L22, L18, M84, M12
1. **N133** — `native_differential`'s per-test staging dirs are removed at test end (a `Drop` guard;
   2,788 stale dirs after one run today); the seal script sweeps `target/tmp/` once. 2. **N106** — the
   JS side pins `f64` printing (`Infinity`, `-0`, `1e21`) against the Rust side in the differential, or
   the divergence is documented by name. 3. **L22** — `publish-brew`'s `app-id` → `app-id`'s v3
   spelling per the action's deprecation notice; the workflow lint that would have caught it. 4.
   **L18** — the pages repo pins its workflow actions by sha like the fleet. 5. **M84** — `Ord::clamp`
   over an integer takes one `compare` (an integer default in number.vl). 6. **M12** — the corpus
   leak-soak FAILS when its corpora are absent instead of passing vacuously. Sizing S. Owns the test
   binaries named, the two workflows, number.vl's `clamp`.

## Lane solver-43 — B433 FIRST (UNSOUND; sha to LANE-STATUS.md the moment it lands), then B400 (saved patch), B418, B403, B401, B419, B423, B426, B427, B428, B429, B430, B431, B425, B424 (RULED at GO), B416, B417, B385 (verify), E226
1. **B433** — the assignment rule for a target that is a call (or any non-path place) typed `&mut T`
   is the plain place's; the three red-first pins + the two green ones (`write() = Some(..)`,
   `write() += 1`); the sweep of std/examples/kolt for `write() =` at an `Option`-typed cell,
   findings listed in the report. 2. **B400 + B418** — copy elision on JS with a `Shared::read()`
   temporary live across a write (B400's patch from solver-42's report; B418's branch/argument
   siblings) — the `copy_elision_census` golden moves are classified. 3. **B403** — the analyzer
   accepts a static call on a bounded impl generic nothing binds (native miscompile). 4. **B401** — the
   inherited-default lookup honours impl admission (the four-module case). 5. **B419** — a blanket over
   a supertrait found through a one-block subtrait impl (b243's `#[ignore]` comes off). 6. **B423**,
   **B426**–**B429** — the literal-typing family after B407: a sibling arm types a literal, a constant
   `0 - 1` at unsigned is refused, `i8 = 128` is off by one, unary `-` on unsigned, and B427's
   destructuring `let` of a closure parameter. 7. **B430**, **B431** — the `dyn` tail: a tuple variable
   into a `(dyn A, dyn B)` position erased element-wise; a B412 erasure at a resource refused. 8.
   **B425** — the context pass under-threads an argument. 9. **B424** per R-h. 10. **B416**, **B417**
   — `[derive(Wire)]`'s field-name collision; a method named `Self` refused at declaration. 11.
   **B385** — verify the generic-recursive-type overflow on 762c6aa5 (Order 40's lane may have landed
   the guard); close with the pin or fix. 12. **E226** — the regime-3 `;` steer reaches through
   `.map(..).cell()`. 13. index-42's two `0usize` suffixes drop (B406 residual closed). Sizing L.
   Owns analyzer.rs, impl_select.rs, mono.rs, transformer.rs (JS emit) — everything named.

## Lane tuples-43 — A122's build (RULED Q1–Q7), B183, B399; REBASES onto solver-43's merge before it reports
1. **A122** — the `Tuple` trait, `TupleKey<T, U>`, `divorce<T: (2..)>(source: SignalCell<T>)`, and the
   `for` over a mapped tuple rule per the ruling; kolt channel.vl:19's `// TODO: Implement` is the
   customer (the owner applies). 2. **B183** — the tuple comprehension's zip form. 3. **B399** — the
   element bound in `T: (2..: PartialEq)` reaches `U` in a comprehension body. Pins red-first; the
   grammar (EBNF + `grammar_sync`) if a spelling is new. Sizing M. Owns the comprehension rows of
   analyzer.rs AFTER solver-43 (rebase, never cherry-pick), the tuple lowering in transformer.rs,
   reactive.vl's `divorce`.

## Lane reactive-43 — A134 (RULED R-c), A135, A136, A137 (settle over a socket), A133, A132; the two rules written
1. **A134** — `ReactiveClient` dedups minted mirrors per origin (method + described args), the table
   released with the mirror's last lease; the stub's doc (rpc.vl ~5900) and remote-sources.md say why a
   stub in a cold select is safe; pins: two stub calls for one origin are one mirror, one `Subscribe`;
   the kolt shape (`sweeps/order43/probes/kolt-mirrors/` section A) reads 1, 2. 2. **A135** — the
   dispatcher runs each handler under the connection's owner (the `Service::factory` seam); a
   handle-returning `[rpc]` whose tail is a derivation constructor warns with the memo steer (a ledger
   row); pin: N calls of `get_channels` leave ONE subscription on the store cell after disconnect. 3.
   **A136** — memo.vl's head and `get_or` doc rewritten; the warning for `.cell()`/`effect` inside a
   `get_or` maker (a ledger row); pin over the probe's F/G. 4. **A137** — section H over a socket (the
   `reactive_channels` harness); if clean, fold into A133 with the note; if not, the mechanism named
   and fixed. 5. **A133** — door (a): the in-process transport delivers the seed through the draining
   turn like a socket. 6. **A132** — `map_each`'s reference cycle (the handler captures the source it
   subscribes to) — a weak edge or a cursor the source owns; the native leak census re-run. Sizing M.
   Owns rpc.vl, rpc_server.vl (this order only — A135), reactive.vl's `subscribe_pulling`/`AndThen`
   docs, memo.vl, remote-sources.md, the guide's mirror pages.

## Lane native-43 — F41, F42, F44, F46, F45 (R-i), the copy census
1. **F41** — a field named `self`/`super` is MANGLED (`self_`, with the read-back in the emitter), not
   raw-quoted. 2. **F42** — `KeyedCell` builds natively (the unbound generic parameter at struct
   position). 3. **F44** — a closure pushed into the list it reads: the recursive-type refusal —
   box the closure type at the emitter. 4. **F46** — an argument that moves the receiver's place is
   evaluated first (native-42's `&mut`-argument rule, applied to a by-value move). 5. **F45** per R-i.
   6. The native copy census regenerated over the tip (`VILAN_REGENERATE_NATIVE_COPY_CENSUS=1`), the
   leak census re-run after reactive-43's A132. Sizing M. Owns vilan-rust, vilan-rt, the native tests.

## Lane editor-43 — E229 FIRST (the delivery), E214 verified, E228, E225 + K24 (one keyword table), B422, E224, E182, E199 as time allows
1. **E229** — install.sh/ps1 install `vilan-vscode.vsix` when `code` is on PATH (opt-out flag; the
   summary line says so); the extension compares `serverInfo.version` with its own at start and shows
   ONE notification with the install command when they differ; the seal script's toolchain refresh
   installs the vsix locally (door d — write it into `scripts/`). 2. **E214** — with 0.41.1 in the
   owner's editor: a pin that `>` typed after an auto-placed `>` steps over it (the `type` override's
   map), and the `false` setting leaves `onTypeFormatting` in charge; closes at the owner's word. 3.
   **E228** — completion after `cell.read().` on `Shared<T>`: the three harness pins (`read().`,
   `write().`, a plain `Option` local) + the `let`-first variant; fix what fails. 4. **E225 + K24** —
   ONE generated keyword table: `vilan --print-keywords` (or a test that writes `keywords.json`) feeds
   bindgen's `RESERVED` and the site's editor list; D14's spec list from the same source (syntax-43
   owns the lexer's table; editor-43 owns the consumers). 5. **B422** — the base-cache key carries the
   std root. 6. **E224** — deprecation warns at import leaves for functions as for types. 7. **E182**,
   **E199** if time allows. Sizing M. Owns vilan-lsp, editors/vscode, bindgen's reserved list, the
   installer scripts, `scripts/` seal refresh.

## Lane syntax-43 — B414 (RULED R-e), F27 R3 (fenced twin items) after B415, D14
1. **B414** — the contextual keywords per papers-42's paper: `with`, `as`, `only` (and the paper's
   list) accepted as identifiers where the grammar is unambiguous; the lexer's table gains the
   contextual flag; formatter and the LSP's syntax tables follow; the EBNF + `grammar_sync`; the
   keyword table exported for editor-43 (one source). 2. **F27 R3** — fenced twin items over
   `[platform("browser")] mod self;` (B415 landed): the six spellings confirmed at Order 42; kolt's
   `lib/conditional_value.vl` (deleted) was the customer — the pins are the twins in std. 3. **D14** —
   the spec's contextual-keyword list from the table. `self::` paths / `export self::*` DEFERRED (R-e).
   Sizing M. Owns lexing.rs, parsing.rs, formatter.rs, grammar.md + the EBNF, the LSP syntax tables
   (after editor-43's merge — rebase).

## Lane papers-43 — E227 (the paper), M88, C15, A131; NO tree change
1. **E227** — the `[hint(Trait<..>)]` attribute paper: Q1–Q5 with recs (marker `~T`; nested yes;
   unconditional impls only; `vilan.inlayHints.abbreviate` default on; hover shows both lines); std's
   ~10 attributes listed. 2. **M88** — devirtualize a single-implementor `dyn Trait` at build time:
   the measurement first (how many `dyn` positions in std/kolt have one coercion), then the rec. 3.
   **C15** — §6.9's closure rule on a native backend (mutably-captured bindings as shared cells): the
   cost table and the rec. 4. **A131** — the deferred row build over the drain's net effect: a
   design, sized, queued or parked. Merges to proposals only.

## Ownership map (conflict avoidance)
- analyzer.rs, impl_select.rs, mono.rs, transformer.rs: solver-43; tuples-43 the comprehension/tuple
  rows ONLY, rebased after solver-43's merge. lexing.rs, parsing.rs, formatter.rs, grammar.md: syntax-43.
  rpc.vl, rpc_server.vl, reactive.vl (docs + `divorce` is tuples-43's), memo.vl, the mirror docs:
  reactive-43. vilan-rust, vilan-rt: native-43. vilan-lsp, editors/vscode, bindgen `RESERVED`, the
  installer scripts, the seal refresh: editor-43. The test binaries named in hygiene-43, the two
  workflows, number.vl's `clamp`: hygiene-43.
- The keyword table: syntax-43 EXPORTS it (the lexer's), editor-43 CONSUMES it — editor-43 merges
  first, so syntax-43 rebases its consumer edits.
- Merge order: hygiene-43, solver-43, tuples-43 (rebased), reactive-43, native-43, editor-43, syntax-43
  (rebased). papers-43 to proposals. After every merge that moved goldens: `regen_goldens.sh`; the copy
  census; the merge helper's BUILD step; `native_differential` in every gate list.
- After the seal + CI green: NO cut (R-g). Toolchain both locations from the sealed tip + the vsix into
  the local vscode-server (E229 door d).

## At the sweep (integrator, proposals)
- Close per the reports; E214 and E222's note at the owner's word; A137 folds into A133 or stands;
  B385 closes on its pin; index-42's suffix note on B406 stamped.
- Kolt at the owner's word: commit 2026-09-28's model.vl (A134's sites, A136's memos, `get_channels`
  on the demand shape — in the tree, uncommitted); A120's §9.7.10 rewrite + A127's header token (still
  owed); the connection-v3 worktree's two `dyn Signal` fields; after A134 (a) lands, the hand `Memo`
  tables may drop to a bare stub call (optional); A122's `divorce` at channel.vl:19.
- Order 44's queue: E227's build if the marker is ruled; the `self::` paths if re-ruled; F27 R3's
  remainder; E229 door (c) as an L-item; M60 (`get`/`set` deep-copy said at the source); A111/A87 if a
  caller appears; v0.42.0 when a breaking need arrives (release/0.41 deleted at that cut).
