# Order 41 — the solver under the train, `usize` S1, the pipeline's protocol and nodes, and the native rpc server (drafted 2026-09-24, off vilan next @1265ea5d; GO 2026-09-24)

**GO 2026-09-24.** The owner: "Go with all recs. `isize` can exist too if useful." R-a–R-e stand as recommended (the train is Order 42's; I5 §11 Q1–Q5 as recommended; `[deprecated]` on a type; C14 S4 the tail; M86's borrowing read). ONE AMENDMENT for index-41: I5's ruling 4 ("no `isize`") is relaxed — `isize` MAY exist if useful; build it only if the family's tables make it free, keep a signed offset `i53` where one exists today, and say which in the report.

**Base.** Order 40 sealed at 1265ea5d on 2026-09-22 (CI 35790429797 green 11/11 after one N126 flake
re-run; local seal green on fceb3223 + the doc-fence commit; toolchain `vilan 0.40.0 (1265ea5d3)` in
both locations; `origin/next` IS 1265ea5d — nothing has landed since). Ledger next id **566**
(`crates/vilan-cli/tests/diagnostics-ledger.tsv`, max 565). Tracker 113 open. Every ruling this
order builds was made by the owner on 2026-09-22 after the seal and is stamped on its item
(`sweeps/order40/rulings41.json`): A124 Q1–Q5 + dyn-40's four, E222, F33, A112's
fallback-then-switch, E215's 84. Kolt is at 9a057c6 (`wip`, the owner's) with the owner's
uncommitted edits (channel.vl, sidebar.vl, styles.vl, views.vl modified; comp/login.vl deleted;
command_palette.vl, login_page.vl, lib/reactive2.vl untracked); `vilan check` on 1265ea5d3 = **4
errors, all A125's bound** (`Theme` and `Command` lack `Hashable` at an `each_values`, plus the two
cascading `Slot` refusals) — the owner owes the two hand `Hashable` impls (by id), then the rest of
the owed list at the end. vilan-website carries 7 uncommitted files (the owner's). vilan-playground
(not a git repository) has `todo/src/store.vl:14` `[expose] notes: Signal<List<Note>>` — a
bare-trait FIELD, refused on 1265ea5d by dyn-40's rule; the integrator's one-liner at GO (`dyn
Signal<List<Note>>`; if `[expose]` refuses a `dyn` field, that is a filing, not a workaround).

**The shape.** Three kinds of work, and one thing this order deliberately does NOT do. **The
breaking train is v0.41.0's, and it is Order 42's** — the CHANGELOG's `## Unreleased` section
already carries **35** `breaking` entries since v0.40.0 (2026-09-01), and the owner ruled (A124 Q5)
that the combinator flip rides the SAME train as I5's `usize` respelling, so the cut waits for both.
Both papers say the same thing about that train: I5's §10 recommends S1 and S2 in SEPARATE orders
("one breaking commit over 56 files wants a clean base … not the same order that moved the solver
underneath it"), and the pipeline paper's S2c is "one pass over `SignalCell<` annotations" that
wants S2a and S2b green first. So Order 41 lands EVERYTHING the train depends on and PREPARES both
breaking steps as saved patches with their estate censuses — the way A112's supertrait switch was
saved last order — and Order 42 opens by merging them last and cutting (R-a). **The solver under the
train** — B395 first (A112's ruled spelling waits on it; the switch patch is saved), B389's five
literal positions (I5 S1 cannot start without them), then B396, B390, B391, B392, E220 and the B393
probe. **The native rpc server** — F18 slice 3: F33 RULED (a shared mutable buffer), the two seams
(`now_millis`, SHA-1 `digest`), `Server::builder()` natively, the rpc server over the upgrade
handover with a real accept key, the keyed pins against it, kolt's `server.vl` as written; F34
beside it because A124 S2 makes a derived signal the common case and none builds natively today.
Around them: the editor's ruled E222 and the rest of E213, F27's ruled R1, hygiene's eight, the
collections tail (the switch, `each_by`, M86's copies), and three papers (A122's `std::tuple`, F27
R3, the CUT PLAN itself).

**Eight lanes**, four fewer than Order 40 — no ui lane (A121 is done bar S3, which is one S item),
no fmt lane (E219 is one S item, folded into editor-41, which owns formatter.rs this order), no dyn
lane (done), and the two train lanes are Order 42's. Merge order at the end; native-41 rebases once
after reactive-41 (F34's `map` half must be re-run on S2b's nodes).

## Rulings — all RULED 2026-09-22 after the seal (the owner); what each lane BUILDS from them
- **A124 Q1–Q5 + dyn-40's four (reactive-41).** Q1 the root KEEPS the name `SignalCell<T>` (not the
  sketch's `Initial<T>`). Q2 `.or(default)` RESETS on a re-pend; a separate `.latest(default)`
  holds. Q3 `.cell()` does NOT compare; a separate `.distinct()` node carries `T: PartialEq`. Q4
  `on_settle` is PUBLIC, the node author's requirement. Q5 the combinator flip (S2c) RIDES v0.41.0 —
  "a major step forward with the language; with nothing advertised there are few or no users to
  worry about" — so S2c lands in the same breaking train as I5 S2 and the cut waits for both (this
  order prepares it; R-a says when it merges). dyn's four: the object's table carries FOUR slots
  (defaults reached through a bound become slots so overrides run); `map` through a `dyn` stays
  refused until S2c makes it a blanket (then the blanket `impl dyn Source<T> with Source<T>` reaches
  it — a pin in the prepared patch); the JS pair with the prototype table stays; trait-objects §5(i)
  RATIFIED (an async impl under a sync declaration is refused at the coercion).
- **A112 (solver-41 → collections-41).** S3 ships on the two-bound spelling as the DECLARED fallback
  until B395 is fixed, then switches by the saved patch
  (`sweeps/order40/probes/a112-s3/s3-supertrait-switch.patch`); B395 goes FIRST in the solver lane.
- **E222 (editor-41).** RULED — build the client-side `type` override as priced: behind
  `vilan.autoClosing.generics` (default on), the server asked `opens_a_generic_list`, `<>` inserted
  and the next `>` swallowed; the extension declares the capability in `initializationOptions` and
  `on_type_edits` stands down for `<` when it is set (non-VS-Code clients keep `onTypeFormatting`).
- **F33 (native-41).** RULED (a) — a shared `Rc<RefCell<Vec<u8>>>`-style mutable buffer natively
  (JS's semantics) for `alloc`/`fill`/`copy_into`, landed with the two seams as F18 slice 3.
- **E215.** 84 STANDS unless re-ruled (std's written margin is ~80; no re-run this order). Not a
  lane.
- **Earlier rulings this order builds on:** I5 rulings 1–5 (distinct type; underflow unspecified,
  never memory-unsafe; literal inference a general law; no `isize`; wire width KEPT); F27 R1
  (module-level `[platform(..)]` is the platform the item is ANALYZED under; the function fence
  gains the same resolution meaning) and R3 (platform-fenced twin items); A112 §13; A121 Q1–Q6 (S3 =
  A128).
- **Asked at GO (rec in each):**
  - **R-a — the train's order.** Rec: Order 42 opens with two lanes (I5 S2; A124 S2c) that MERGE the
    patches Order 41 saved, each with its estate re-sweep, merged LAST; the v0.41.0 cut at Order
    42's seal. The alternative — launch both train lanes inside Order 41 the moment index-41 and
    reactive-41 report — saves a day and does exactly what both papers warn against (a 56-file
    breaking commit rebased on a solver that moved in the same order). If the owner wants the cut
    sooner, say so at GO and the two lanes are briefed as Order 41's ninth and tenth, merged after
    native-41.
  - **R-b — I5 §11 Q1–Q5** (index-type.md), recs: Q1 `fs.vl`'s STREAM offsets stay `i53` (a stream
    offset is not an index; the book says so); Q2 a `usize` in a user contract surface LETS the hash
    move (rebuild both halves — rendering it as `u53` would let two halves disagree about
    negatives); Q3 `usize::max_value()` answers the JS guarantee (2⁵³) on every backend, as R6 of
    Order 37 settled `i53`/`u53`; Q4 the native refusal wording = N120 (the program's own
    unspecified subtraction, the vilan span named); Q5 the `42usize` suffix YES, and its appearance
    in ordinary code is a bug report against §4. S1 needs Q3 and Q5; the rest are S2's.
  - **R-c — B382.** Rec: build `[deprecated("…")]` on a TYPE (and on a re-export), rendered by
    E213's greying — papers-40's recommendation; NO type alias (no customer; `export import … as`
    already exists). S, editor-41.
  - **R-d — C14 S4** (the counted `Shared` representation natively, unblocked since F1 S1b). Rec:
    the droppable TAIL of native-41 — the rpc server is the exit and S4 must not delay it; S5 (a JS
    counted mode as an instrument) stays queued.
  - **R-e — M86's read path.** Rec: a borrowing read on `ListCell` (`with(|&List<T>| U)`-shaped, or
    the `DeltaSource` consumer that never reads the whole) IS a new public name; build it only if
    the measurement says the copies dominate (s3-40 measured 6.28 of 6.30 M Ir per push in the
    WRITE's copies — they do), and the per-push Ir claims in incremental-collections.md are
    re-stated after it.

## Mechanics (every lane)
briefs40.md's "Mechanics" stands in full (briefs39's rules + Order 39's six lessons: never `git
config`; the item's text is a HYPOTHESIS — verify the premise and say so; a passing probe must be
shown to BUILD something; every std-touching lane gates `-p vilan-cli --test native_differential`
default AND `VILAN_NATIVE_DIFFERENTIAL=1`; the golden suites are `corpus`, `split`, `examples`,
`copy_elision_census`; a `-p <crate>` spec with zero tests exits non-zero; `vilan build
vilan/test/<x>.vl` overwrites the golden — probe over a scratch copy; a BREAKING lane re-sweeps the
estate INCLUDING the `.vl` consts inside Rust tests, vilan-website and vilan-playground; SendMessage
works — a lane answers no question itself; worktrees off `origin/next` @1265ea5d, never the main
checkout, never `git stash`, never push, `kill <pid>` of recorded PIDs only; one commit per item
with its CHANGELOG entry and family marker; ledger rows written `NEW` (next id 566), a rowed message
is ONE `\`-continued literal; long runs in the FOREGROUND with a timeout; perf in thread CPU or
callgrind Ir + loadavg, never wall; kolt and proposals READ-ONLY, kolt never copied into the vilan
tree; model Opus, never Fable; never rebuild while your own whole-crate run is in flight;
`node_size` for node.rs lanes; `markdown_golden` + `book_sync` for docs lanes; a native wall is
measured on the EXIT program with the host census — F29's fix landed, so the census now walks
refused arguments; no edit to a file a foreground gate is reading; poll a log line, not a process),
PLUS Order 40's lessons as RULES:
- **Any lane editing `vilan/docs/spec/grammar.md` gates `grammar_ebnf` + `grammar_sync`** (std-40's
  `http` terminal reddened the merge).
- **`shared_census` is in every std gate list** (two lanes moved it at the merge last order; the
  literal is 140 on 1265ea5d).
- **std opts into `wrap_comments` at 84** — a std lane runs `vilan fmt vilan/std` before EVERY
  commit, or fmt reddens the seal.
- **Two lanes touching one record shape merge textually clean and fail at BUILD** — the merge
  helper's build step is the tripwire; the integrator runs it after every merge, no exceptions.
- **The interpreter differential EXCLUDES by name what the macro world refuses** (a `dyn` call is
  refused at expansion time); a new corpus program needs its `corpus_manifest!` row.
- **A depth cap in the solver answers NO when it gives up** (B394 — the cap's lenient yes was an
  UNSOUNDNESS); a new fixpoint or recursion guard states which way it fails closed.
- **`cargo fmt` JOINS a `\`-continued string literal and leaves the indentation inside** — a
  multi-line `.vl` fixture is a `concat!` or a one-line program (N123's first line; hygiene-41
  writes it into AGENTS.md and every lane obeys it now).
- **Doc comments are compiled by CI's doc-test leg** (`cargo test --doc`, which nextest skips —
  seal.sh runs it now): an indented sketch in a `///` comment is a ```text fence.
- **Tool shell PATH**: some sessions lack `~/.cargo/bin` and node — prefix `export
  PATH="$HOME/.cargo/bin:$HOME/.nvm/versions/node/v24.2.0/bin:$PATH"`; and `touch build.rs` when
  `vilan --version`'s sha goes stale in a worktree.

## Lane hygiene-41 — DROPPABLE, lands FIRST: N123, N121, N124, N126, N120, N122, A127, A128
1. **N123** — four sentences in AGENTS.md's lane section (the `\`-continuation trap;
   `semantic_tokens` answers `(Span, TokenKind, u32)`; grammar.md gates; `shared_census`
   everywhere). 2. **N121** — the stack-remaining probe: ONE `ensure_sufficient_stack`-style guard
   at the four analyzer entry points B385/B387 went through (a NEW helper module; NOT a walk-by-walk
   edit — solver-41 owns analyzer.rs's walks and you land first), a deep recursion becomes a
   diagnostic; the pin at the playground's fence `lib.rs:472` (ledger 293) that N119 could not
   reach; vilan-lsp's twin. 3. **N124** — a B354-style multi-file pin in `module_resolution.rs`
   where an `only` import declines one of two traits' same-named defaults (F26's admission
   parameter, planted `None` must red). **N126** — option (a): a BOUNDED re-read (≤ 50 ms) of
   `/proc/self/fd` only while the count is above baseline; the plant (`1, 2, 7`) still reds; MEASURE
   the finalizer window (GC does not run inside 50 ms on a warm heap — show it). **N120** — the CLI
   names the overflowing expression from rustc's span and says the JS backend would have run on (I5
   Q4's wording; index-41 reads your sentence). **N122** — B271's private `focus()` override retires
   onto the shared stub; one pin that the stub refuses a `focus()` the platform would.
   4. **A127** — `over_http_with(mount, codec, headers)` beside `over_http` (a second constructor,
      not a field); the headers ride every POST; a pin over the S4 table's 401 row turning 200 with
      the header. **A128** — A121 S3: `related_target` + the `focusout` path (`Contain` learns
      "focus left me, and to there"; `Wrap` may dismiss on Tab-out), both ui twins. Sizing M. Owns
      AGENTS.md, the new stack-guard module + the four entry-point lines, vilan-lsp's guard twin,
      module_resolution.rs tests, the fs test, the CLI's rustc-refusal wording, the DOM stub +
      B271's suite, rpc.vl's `HttpTransport` constructors, std::ui's focus module in both twins.

## Lane solver-41 — B395 FIRST, B389 (I5 S1's blocker), B396, B390, B391, B392, E220, B393 (probe)
1. **B395** — member selection through a blanket checks the blanket's bound at the ARGUMENTS the
   supertrait is implemented at, not the trait id (`impl_select.rs`'s `subject_applies`, the B268
   id-vs-arguments gap): the item's repro prints 2; a std-shaped FIXTURE with `DeltaFeed<T> with
   Source<List<T>>` turns the three reds green (`reactive-on-change.vl`'s `Stored<i32>`, the
   keyed-mirror pin's `effect_on_change`, the native corpus leg); B394's five soundness pins stay
   green. REPORT the moment it lands — collections-41 applies the saved switch on your merge. 2.
   **B389** — the FIVE literal positions (a literal LEFT of a binary operator; the elements of an
   ANNOTATED list literal; a literal MATCH pattern; a GENERIC call's return; a bare `let n = 0` used
   later at the type), one red-first pin per position for `i53`, `u32` and `f64`, the 14 passing
   positions as controls (`sweeps/order40/papers-40/probes/i5_literal_positions.sh` is the census).
   REPORT when landed — index-41's S1 starts on your merge. 3. **B396** — a second bound over `T` on
   a generic function's `S` (either order) must not stop the key closure binding `T` (the a52 pin's
   refusal back to its two errors, then zero). **B390** — a refused impl subject does not enter the
   candidate set (or enters poisoned and is skipped by specificity): the repro reports ONE error, at
   the impl. **B391** — the exported-impl admission of a `[service]` PEER's members (`export impl
   Door` beside a plain `impl Peer` with an `[rpc] fun ping`): the spurious "not exported" refusal
   goes; the fix is not in `[service]`. **B392** — a let-bound closure with an unannotated parameter
   takes its type from its first call site (one round after the fixpoint stalls): both shapes + the
   annotated control. 4. **E220** — substitute the supertrait's arguments before rendering the
   missing member (`List<i32>`, not `i32`).
   5. **B393 the PROBE** — a trait static reached through an instance-only generic, JS vs native; if
      JS answers wrongly it is a MISCOMPILE: bind as native does and SHARE the function in `mono.rs`
      (then N125's four functions are yours — say so; native-41 does the crate rename regardless).
      Sizing L. Owns analyzer.rs (impl selection, bound tracking, literal typing, closure inference,
      the missing-member sentence), impl_select.rs, transformer.rs's
      `inherited_substitution`/`call_substitution`, mono.rs.

## Lane index-41 — I5 S1 (after B389), A126, E218; S2 PREPARED, not applied
1. **S1 the type** — `usize` in `type_.rs`'s three tables, analyzer.rs (the numeric-type rows ONLY —
   the solver lane owns the rest; you merge after it), transformer.rs, bindgen.rs, vilan-rust's
   scalar map (Rust `usize`), vilan-rt; `grammar_sync` + the book theme; `number.vl`'s family
   (index-type.md §2.3's table):
   `Add`/`Sub`/`Mul`/`Ord`/`Default`/`Hashable`/`Json`/`FromJson`/`Debug`/`Display`, `as_usize` on
   the eleven other numeric types and the `as_*` back, `checked_sub`/`saturating_sub`; `impl usize
   with Wire` at **`i32`'s width** (§6 — a `usize` round-trip through both codecs byte-compared
   against `i32`'s); `usize::max_value()` = 2⁵³ on every backend (Q3's rec — if R-b rules otherwise,
   the integrator tells you); the `42usize` suffix (Q5). 2. **The subscript** — B386 (solver-40)
   typed `xs[i]`'s index as `i32`; S1 admits `usize` there as well, with `i32` still accepted until
   S2 moves it — say HOW (a two-type admission at the subscript only, named in a comment that S2
   deletes). 3. **The book** — the family's pages; the underflow rule stated where `u53`'s range
   rule is (unspecified, never memory-unsafe; JS runs on negative, native panics in debug); an
   underflowing program pinned OUT of the native differential BY NAME. 4. **Pins** — the 21 literal
   positions as a corpus program (with its `corpus_manifest!` row); the wire round-trip; the suffix;
   `let n: usize = 0; n - 1` on both backends under the exclusion. 5. **A126** — `Display` for
   `i53`, `u53`, `u8`, `i8`, `i16`, `u16`, `i64`, `u64` (and `usize`) in display.vl, both twins
   where they exist; a pin per type through a `T: Display` bound. **E218** — `Expected u53, but got
   i32 instead.` carries the `as_*` steer (`as_i32()` / `as_usize()`) and a quick fix (the
   binary-operator path, ledger 357, is the model); the S2 naming diagnostic (§8.2) is NOT yours. 6.
   **S2 PREPARED** — under `sweeps/order41/index-41/`: the codemod (§8.1 — not A101's) as a script,
   run over a scratch copy of the tree and DIFFED (the 105 positions; the 76 WIRE/STREAM/SEQUENCE
   positions left alone with an explicit conversion where they meet an index; the 7 sentinels and 8
   loops by hand, each named); the goldens' movement measured (§5.4 says none should); kolt's three
   sites named for the owner (`rotary.vl` is the one that needs thought). NOTHING of S2 lands on
   next. Sizing L. Owns type_.rs, number.vl, display.vl, bindgen.rs's scalar rows, vilan-rust's
   scalar map, vilan-rt's numeric shim, the book's numbers pages, the subscript's index admission.

## Lane reactive-41 — A124 S2a (the protocol), S2b (the nodes); S2c PREPARED, not applied; the guide
1. **S2a the protocol** — `observe` takes an id (`observe<T>(signal, observer)` at reactive.vl:1241
   today; S2a's `observe` threads ONE subscriber id per leaf chain so door 2's dedup-on-enqueue
   absorbs a diamond's duplicate notify); `on_settle` PUBLIC on the read trait as the node author's
   requirement (Q4), `on_change` still the one every application writes; the no-payload notify
   behind the S1 probe's flag becomes the protocol; the diamond's COUNT pin
   (`reactive_lifetimes.rs:1036` re-expressed: the effect fires ONCE with the settled pair, under
   cold arms); door 2's pins re-run unchanged. No surface change. 2. **S2b the nodes** — `Map<S,
   U>`, `Switch<S, I>`, `Combine` over the tuple bound, `.cell()` (does NOT compare — Q3;
   owner-tied, `as_derivation()`-marked, A28's story), `.distinct()` (carries `T: PartialEq`),
   `Resource<T>` (pending → settled → pending again, `failed` a third state) with `.or(default)`
   (RESETS — Q2), `.latest(default)` (holds), `.optional()`, `.is_pending()`. The combinators
   `map`/`combine`/`flatten`/`switch`/`and_then` STILL return `SignalCell` this order — nothing
   moves. `.cell()` and `.distinct()` are the first public names; the node types are constructible
   this order only through spellings S2c removes or replaces — keep them std-internal (the S1
   probe's `Cold` names, unexported) and say which. The S1 probe file `reactive_pipeline.vl` retires
   INTO the real module (or is deleted with its numbers kept in the CHANGELOG entry). Pins from the
   item: a 5-deep cold chain evaluates ZERO times with no subscriber and once per leaf; twice for
   two leaf subs and once with a `.cell()` between; `pending.or(0)` reads `0` before completion and
   the value after, its downstream `map` written on `T`; the owner's disposal releases a `Switch`'s
   rolling inner registration; the shared-census literal moves by exactly the `.cell()` count (140
   on 1265ea5d). 3. **S2c PREPARED** — under `sweeps/order41/reactive-41/`: the flip (the five
   combinators return nodes; the blanket over `dyn Source<T>` so `map` through a `dyn` works —
   dyn-40's refusal pin becomes a pass) as a saved patch off your S2b commit, plus the estate CENSUS
   it breaks: every `SignalCell<` annotation naming a combinator's result (std's internal uses in
   `std::ui`/`std::rpc`/`std::router`; the corpus; docs fences; vilan-website; vilan-playground; the
   `.vl` consts in Rust tests) and every `update` reached on a derivation (paper §5 (2) — a rename
   to `.cell()`); kolt's counts for the owner (the paper's 19 fields / 3 `dyn`; the annotated
   locals). NOTHING of S2c lands on next. 4. **The guide** — the derivations section rewritten for
   S2b's names: "a chain is cold; `.cell()` where you share or read hot; `dyn Source<T>` where you
   store"; reactive-pipeline.md gets an "as built" note. Sizing L. Owns reactive.vl,
   reactive_pipeline.vl, the guide's derivations section, reactive-pipeline.md's note;
   `shared_census` in the gate list.

## Lane collections-41 — the A112 switch (after solver-41), S3b, M86
1. **The switch** — apply `sweeps/order40/probes/a112-s3/s3-supertrait-switch.patch` on solver-41's
   B395 merge (the integrator tells you when): `DeltaFeed<T> with Source<List<T>>` as ruled, the
   three fallback sentences deleted (delta.vl, the docs, the CHANGELOG's B395 note), `each`'s bound
   where §13 wanted it if B396 landed (else it stays on the `Slot` impls — say which). ONE std
   commit. If a fourth gap appears, file it and STOP the switch — the fallback is declared and
   correct. 2. **S3b** — `each_by` on the op path (`place_each`'s Splice/SetAt arms reach it; the
   1,000-row and 300-turn pins run over `each_by` too). 3. **M86** — MEASURE first: a 1,000-row
   push's Ir split between the derivation and the copies (s3-40 read 6.28 of 6.30 M in the WRITE's
   `SignalCell::get` deep-clone and the per-observer copy); then, per R-e, the read that borrows or
   the `DeltaSource` consumer that never reads the whole; the per-push claims in
   incremental-collections.md re-stated with the new numbers. Sizing M. Owns delta.vl, `ListCell`,
   `each*`/`reconcile` in both ui twins, incremental-collections.md's numbers.

## Lane editor-41 — E222 (RULED), E221, F27 R1 (RULED), B382 (R-c), E219
1. **E222** — the client-side `type` override in extension.ts behind `vilan.autoClosing.generics`
   (default on): the server's `opens_a_generic_list` request, `<>` inserted, the next `>` swallowed;
   the capability declared in `initializationOptions`; `on_type_edits` stands down for `<` when it
   is set (non-VS-Code clients keep today's `onTypeFormatting`); the TS half textually pinned;
   Vim-emulation coexistence is why it is a setting. 2. **E221** — E213 S2: `[internal("reason")]`
   on nominals, enum variants, traits, module bindings; the docs generator's collapsed "Internal"
   heading; the opt-in `[lints] internal_use = "warn"` (a NEW `[lints]` manifest section — schema,
   LSP `TABLES`, completion: the four-file set).
   3. **F27 R1** — `[platform("browser")]` at MODULE level (a file-leading attribute; also on `impl`
      blocks and nominals): everything inside requires that platform AND it is the platform the item
      is ANALYZED under (it outranks every heuristic and E113's `default-entry` colouring — the
      owner's own case, which R2 could not reach); reaching it from a server entry reports the
      colouring chain; the FUNCTION fence gains the same resolution meaning (measured last order: it
      has none); the status line's "analyzed as: declared"; the quick fix inserts the attribute.
      Name the resolver file you touch; if it is analyzer.rs, tell the integrator before your first
      commit (solver-41 owns its walks). 4. **B382** (per R-c) — `[deprecated("use …")]` admitted on
      a TYPE and on a re-export, greyed by E213's mechanism, hover renders the reason; NO alias. 5.
      **E219** — an attribute line and the signature below it have SEPARATE budgets: the repro
      reprints unchanged. Sizing M–L. Owns vilan-lsp, extension.ts + package.json, the docs
      generator, formatter.rs (this order's only formatter change), the attribute admission for
      `[internal]`/`[deprecated]`, the platform resolver.

## Lane native-41 — F18 slice 3 (F33 RULED + the seams → `Server::builder()` → the rpc server → kolt's server leg), F34, N125; C14 S4 the droppable tail (R-d)
1. **F33** — native `Bytes` gains the shared mutable buffer (RULED a): `alloc`/`fill`/`copy_into`
   mutate in place through the shared handle; an ALIASING program (two bindings, one buffer, a write
   seen through both) byte-compared on both backends; `slice`/`get` unchanged. 2. **The seams** —
   `now_millis` and SHA-1 `digest` in vilan-rt (dependency-free — hand-written as SHA-256 was; the
   RFC 6455 accept key's test vector as the pin). 3. **`Server::builder()` builds natively** — the
   bare `Server::builder().port(0).on_request(..).on_start(..).build().start()` census goes 6 → 0
   (F22 landed for the `turn(.., || protocol.respond(..))` shape; F33 + the seams are the rest);
   `serve_build`'s conditional-GET arm. 4. **The rpc server** — `std::rpc_server` natively over
   `vilan-rt::http`'s upgrade handover with a real accept key; the wire byte-identical to node (the
   keyed rpc pins run against a native server — the contract hash unmoved). 5. **THE EXIT** — kolt's
   `server.vl` (137 lines, read-only) as written: a corpus program of its SHAPE (never kolt itself)
   built natively serves a login AND a keyed subscription over one socket byte-for-byte with node;
   native-apps.md §12's whole-set table updated (121 / 83 / 38 at the seal); the host census
   (post-F29) on the exit program. 6. **F34** — native `map` (a generic parameter bound through a
   trait default with a closure argument — B379's neighbour) and `flatten` (the `?` on an `Option`
   payload inside a blanket), differential-pinned; built on today's shape FIRST, then re-run on
   reactive-41's S2b merge (your one rebase, by your resumed agent) so a `.cell()` chain builds
   natively too. 7. **N125** — `vilan-embedded-std` → `vilan-embedded` (22 files across cli/lsp/wasm
   + the release scripts; one mechanical commit; `release_scripts` gate); the four per-emitter
   functions ONLY if solver-41's B393 probe says JS and native must agree (ask the integrator).
   8. **C14 S4 (R-d, TAIL, droppable)** — `Shared<T>` as the counted resource natively (retain on
      clone, release at last use on Tier 1's dataflow, `Weak` at the two std sites already weak);
      the SCC gate as the exit; STOP if it touches the rpc-server path. Sizing L. Owns vilan-rust's
      lowering (bytes, time, the reactive combinators), vilan-rt (bytes/time/sha1 modules, the
      counted representation), the crate rename, native-apps.md §12.

## Lane papers-41 — A122 (`std::tuple`), F27 R3, the v0.41.0 CUT PLAN; NO tree change
1. **A122** — `proposal/tuple-module.md`: the `Tuple` trait as a blanket `impl type T: (2..) with
   Tuple` (imported as `std::tuple::Tuple`, B318's selector admits it) with `entries()`, `get(key)`,
   `map`; `TupleKey<T, U>` (a key carries WHICH tuple family it indexes AND the element type at that
   position — the fact the analyzer already knows for `(U in T: F<U>)` to exist); the tuple
   comprehension as the trait's DESUGAR (one mechanism), B183's zip as
   `a.entries().zip(b.entries())`; `divorce` as three lines beside `combine`; the per-position
   firing claim (every output cell fires on every source change unless a `PartialEq`-gated write is
   wanted — say which and why); the typing work sized (per-position `U` reified in a key type; M–L);
   positions born `usize` — the build is AFTER I5 S2 (Order 42 at the earliest).
   2. **F27 R3** — a section of platform-coloring.md (or a short paper): platform-fenced twin ITEMS
      in one file (`[platform("browser")] impl X with Slot` beside `[platform("@process")] impl X
      with Slot`): coherent iff the platform sets are DISJOINT; each analyzed only under a platform
      it admits; a build selects by its entry; the editor analyzes once per declared platform and
      unions the diagnostics; the NEW invariant stated honestly (every item is checked under at
      least one platform it admits, which bends §2's "unreachable code is still type-checked"); R4
      (app-level layers) as the documented, unbuilt fallback; sized, with F17's native window chrome
      as the second customer. 3. **The CUT PLAN** — `sweeps/order41/papers-41/cut-plan.md`: the 35
      unreleased `breaking` entries digested for the release notes (grouped: language, std surface,
      reactive, style, rpc/wire, tooling — each with its migration line); the two trains'
      composition (I5 S2's commit, A124 S2c's commit; the order they merge; each one's estate sweep
      and the goldens it may move); what the cut does NOT wait for (kolt's migration — R4; A122; C14
      S5); L23's rehearsal checklist re-run as a dry list against 1265ea5d (the 125,000-character
      notes cap, the release scripts, the toolchain install in both locations); the version bump's
      files. The integrator merges nothing from this lane to vilan. Sizing M.

## Ownership map (conflict avoidance)
- reactive.vl + reactive_pipeline.vl + the guide's derivations: reactive-41. delta.vl, `ListCell`,
  `each*`/`reconcile` in both ui twins: collections-41. number.vl, display.vl: index-41. rpc.vl's
  `HttpTransport` constructors, std::ui's focus module, the DOM stub: hygiene-41. std's
  `vilan.toml`: nobody (84 stands).
- analyzer.rs: solver-41 (impl selection, bounds, literal typing, closure inference, the
  missing-member sentence); index-41 (the numeric-type rows + the subscript admission ONLY, merged
  after solver-41); hygiene-41 (four entry-point lines for N121, merged FIRST); editor-41 (the
  platform resolver — tell the integrator if it is in analyzer.rs). impl_select.rs, mono.rs:
  solver-41. type_.rs, bindgen.rs: index-41. transformer.rs: solver-41 (the two substitution
  functions); index-41 (the `usize` rows). formatter.rs: editor-41 (E219 only). parsing.rs:
  editor-41 (`[platform]` at module level, `[deprecated]` on a type); index-41 (the `usize` suffix
  token) — the two touch different productions; index-41 merges later and rebases if the attribute
  production moved.
- vilan-rust: native-41 (bytes/time/reactive lowering, the crate rename); index-41 (the scalar map
  row); solver-41 nothing. vilan-rt: native-41.
- vilan-lsp: editor-41; hygiene-41 (the stack-guard twin in server main only). AGENTS.md:
  hygiene-41.
- Merge order: hygiene-41, editor-41, solver-41, collections-41 (the switch — rebased on solver-41's
  B395 merge; goldens), index-41 (after solver-41's B389; goldens; `grammar_sync`), reactive-41
  (goldens; `shared_census`), native-41 (one rebase after reactive-41, by its resumed agent; the
  whole native set + the differential), papers-41 to proposals only. After EVERY merge that moved
  goldens: `scripts/integration/regen_goldens.sh` over the merged tree; the merge helper's BUILD
  step after every merge without exception. Every gate list includes `native_differential`; std
  lanes `shared_census` and `vilan fmt vilan/std`; grammar.md lanes `grammar_ebnf` + `grammar_sync`;
  docs lanes `markdown_golden` + `book_sync`; node.rs lanes `node_size`.

## At the sweep (integrator, proposals)
- Close per the reports; I5 stays OPEN (S1 landed, S2 the train); A124 stays OPEN (S2a/S2b landed,
  S2c the train, S3 kolt); A112 closes at the switch (S3b landed) or stays open on S3b alone; F18
  stamped with the exit (kolt's server leg natively) or the narrower exit as reached; F27 stamped R1
  built / R3 papered; B382 re-titled to `[deprecated]` on a type and closed; C14 stamped S4 if
  reached.
- Kolt at the owner's word: A125's two hand `Hashable` impls (Theme, Command — by id, NOT the
  derive); A123's eight sites; A121's overlay lines + six `autofocus` attributes; the connection-v3
  worktree's two `dyn Signal` fields; A120's §9.7.10 rewrite; A127's header token if kolt's login
  page holds one; the three I5 sites named by index-41 (`rotary.vl` first) — with S2, not before.
- The integrator at GO: vilan-playground `todo/src/store.vl:14` → `dyn Signal<List<Note>>` (or the
  filing).
- **Order 42's queue: THE TRAIN** — lane index-42 (I5 S2: the saved codemod applied as ONE breaking
  commit, the naming diagnostic + quick fix, the estate re-sweep, the goldens measured) and lane
  reactive-42 (A124 S2c: the saved flip applied, the estate's `SignalCell<` annotations, `map`
  through `dyn`), both merged LAST; I5 S3 (the native casts) + S4 (A112's `// I5` markers, std::ui's
  positions, `KeyedCell.positions`) after S2; the v0.41.0 CUT at the seal per the cut plan; then
  A122's build; A124 S3 (kolt) at the owner's word; C14 S5 optional; E215's width if re-ruled; F27
  R3 if its paper is ruled.
