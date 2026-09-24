# The v0.41.0 cut plan

Written by lane papers-41 of Order 41 on 2026-09-24, against vilan `next`
@1265ea5d (`vilan 0.40.0 (1265ea5d3)`, both install locations). The cut itself
is Order 42's, at its seal (briefs41 R-a, GO'd 2026-09-24). This plan changes
nothing in the compiler tree; every claim cites the CHANGELOG entry
(`CHANGELOG.md:<line of its bold head>` on 1265ea5d), the script, or the
tracker item it comes from. Where a claim was RUN rather than read, it says so.

**The runs behind it** (all read-only against the vilan tree; the dry run's
full output is `cut-dry-run-1265ea5d.txt` beside this plan, and
`notes_cap_check.sh <tree> <version>` re-runs §5.3):

- `scripts/cut-release.sh --against 1265ea5d --date 2026-09-24 --out <scratch> 0.41.0`
  — the cut's own dry run (§5.2), including its CI read and sweep (a) over all
  651 entries. **It REFUSED** (one entry untraceable, §7 F0); the proposed
  section was then produced by the script's own rewrite parser.
- The release-notes step of `release.yml` (the 125,000-character cap) re-run
  locally over that proposed section (§5.3).
- `scripts/fold-release.sh v0.41.0 --dry-run` (§5.6).
- The marker parity count from `releases.md` §7.2 step 3 (§5.1).
- `git grep -F 0.40.0` for the bump (§6).

## 1. What the cut is

`## Unreleased` on 1265ea5d holds **651 entries** — 35 `breaking`, 39
`miscompile`, 153 `fix`, 113 `feature`, 61 `performance`, 188 `tooling` + 62
`diagnostics` (counted by marker; the parity count is 651 markers / 651 heads).
It has accumulated since v0.40.0 (2026-09-01, `CHANGELOG.md:2058`). Order 41
adds its own entries; Order 42 adds the two breaking TRAINS (§3) and whatever
else it lands; the cut is taken at Order 42's seal, on the commit CI verified
green.

The beta switch is DEFERRED (owner, 2026-08-26, `proposal/beta.md` head), so
v0.41.0 is an alpha minor: no deprecation promise, no mandatory `### Breaking`
heading — the family order `cut-release.sh` writes is the whole structure.

## 2. The 35 breaking entries, digested for the release notes

Grouped as the brief asks; the id beside each line is the item its entry names. Each line: what changed, then the migration drawn
from the entry itself. **"Net-zero vs v0.40.0"** marks an entry whose
"before" never shipped — it broke a shape introduced and changed inside this
same Unreleased window — verified against the `v0.40.0` tag
(`git show v0.40.0:<path>`). Those need no migration line for a v0.40.0 user
and are candidates to fold into their feature entry at the cut (§8 Q2).

### 2.1 Language

| Entry | What changed | Migration |
|---|---|---|
| `CHANGELOG.md:205` (A124 R3) | A bare trait at a struct FIELD is refused; the message names `dyn Trait` (B184's hidden parameter withdrawn at fields; parameters and bindings unchanged). | Write `dyn Trait` — or the concrete type where the field needs an INHERENT method: the playground's `store.vl:14` took `SignalCell<List<Note>>` because `dyn Signal` has no `update` (notes41, GO). |
| `:313` | `Self<i32>` is refused. | Write the type's name (`Cell<i32>`); a bare `Self` is untouched. |
| `:604` (B352) | An explicit type ARGUMENT survives an argument that knows less; a trait's own arguments are no longer inert. | Delete the arguments or make them agree: `Signal<i32>::new("x")` → `Signal<str>::new("x")` or `Signal::new("x")`. |
| `:688` (A100) | `lazy` is a hard keyword; a `lazy` parameter defers its argument. | Rename any binding, parameter, field or type called `lazy`. |
| `:747` (B318 S4) | A type's method namespace is per IMPORTING FILE; two packages extending one type can both be installed. | A file importing two modules that extend one type with one method name picks one with a selector or drops an import; an `impl` in a module with curated exports needs `export impl` (or `export *;`). |
| `:768` (B317/B332) | A type segment REPLACES an import path's namespace, struct as well as enum. | Zero-hit census in the estate; a module member reached through a type-named prefix is spelled at its module. |
| `:812` (B318) | A plain import of an item its module does not export WARNS. | A warning, not an error: add the reach marker (`import pkg::a::{ #hidden }`) or import the exported name; the quick fix is one character. |
| `:827` (B318) | `export (helper);` and `export * helper;` are refused. | `export` takes an item or an `import`/`use`; zero hits in the estate. |
| `:1518` (B180) | The RIGHT operand of a generic-bounded operator is checked against the bound. | `fun sum<P: Add, Q>(a: P, b: Q)` → make them one type, or say so: `P: Add<Q>`. |
| `:1521` | A condition that is a generic parameter of its own declaration is refused. | Pass a `bool`; zero hits in the estate. |
| `:1530` (E135) | A `::` path may not cross a line break. | Join the line, or `import a::b::c as d;`. |
| `:1695` (B171/B195) | A negated capture in a `for` condition or a `match` guard is refused (the `if` rule, extended). | Bind in the body after the test; zero hits in the estate. |
| `:1882` (B197) | An operator trait's method is required at impl time. | Implement the method (`impl P with Add { fun add(..) }`); zero empty impls in the estate. |
| `:2001` (B171) | An `is` capture is in scope only where its test PASSED: not in a `||` arm, not in `else`. | Read the capture in the then-branch or after `&&`. |
| `:2006` (B178) | `fun main` takes no parameters. | Read `std::process::args()`. |
| `:2047` (B169/B174/B179/B181) | A native operator on a generic LEFT operand needs a bound that provides it. | `<T>` → `<T: Add>` (`Sub`, `PartialEq`, `PartialOrd` likewise); the estate's whole migration was one bound. |

### 2.2 std surface

| Entry | What changed | Migration |
|---|---|---|
| `:295` (A118) | `std::random::range` is `[low, high)`, as its doc always said. | Wanted the old range: `range(low, high + 1)`. |
| `:637` (A103) | `Option::unwrap_or`/`expect` and `Result::unwrap_or`/`expect` take their argument `lazy`. | A fallback with a side effect that must run: hoist it (`let v = expensive(); opt.unwrap_or(v)`). |
| `:732` (A99) | The six `View` parent methods are retired: `when`, `swap`, `swap_split`, `bind_each`, `bind_each_values`, `bind_each_by`. | `parent.swap(s, r)` → `parent.child(swap(s, r))`, or `{swap(s, r)}` in a child hole; `bind_each*` → `each*`; the editor's quick fix rewrites it in place. |
| `:750` (B318 S5+S6) | std curates its exports: 548 of 856 declarations exported. | Reaching an unexported std item warns (`:812`); use the documented name or the reach marker. |

### 2.3 Reactive

| Entry | What changed | Migration |
|---|---|---|
| `:167` (A125) | `each`/`each_values`/`each_by`/`reconcile` keys need `K: PartialEq + Hashable`. | `[derive(Hashable)]` on a struct/enum key equal by all fields; a hand `impl Key with Hashable` hashing exactly the fields `eq` reads otherwise. |
| `:340` (A112) | `KeyedCursor` is `DeltaCursor`; `KeyedCell`'s `record`/`trim` are the log's. | **Net-zero vs v0.40.0** — `KeyedCell` is itself new in this window (absent from the v0.40.0 tree). |
| `:1593` (A43/A49) | `Source::on_change` is the trait's REQUIREMENT; `sub` is derived. | Per implementation: rename `fun sub` to `fun on_change`, drop the immediate call, delegate to the inner source's `on_change`. Callers unchanged. |
| `:1935` (A32/A33) | `Optimistic<T>` is `Optimistic<T, S: Signal<T>>`. | Nothing at a call; spell the second parameter where the type is written out (`Optimistic<str, SignalCell<str>>`). |

### 2.4 Style

| Entry | What changed | Migration |
|---|---|---|
| `:640` (A101) | A `css` block's declarations are CALLS: `property(value);`. | Rewrite `property: value;`; the old spelling is refused at the `:` with the call form named. |
| `:1080` (A89) | `Style::attribute`/`within` take `value: Option<str>`; a `not(inner)` marker. | The entry's own line: every call passes `Some(..)`. For a v0.40.0 user (who had `value: str`): skip this shape and go straight to `:700`'s — the `not` marker half is **net-zero** (added and retired inside the window, `:706`). |
| `:700` (A95) | The `Option<str>` form enters its one-release deprecation window. | `.on(attribute(name).eq(value), inner)` for the exact form, `.on(attribute(name), inner)` for presence; the old call still compiles and warns. |
| `:706` (A95) | Conditions are values with `.not()`; `child_relation` is DELETED; `within` takes a condition. | `not(inner)` → `cond.not()`; `within(name, value, inner)` → `.on(within(attribute(name).eq(value)), inner)`; `child_relation(..)` → `attribute(..)`/`within(..)` (its steer). |
| `:872` (A93) | `Style::child_relation` checks its token. | **Superseded** by `:706`, which deletes the method. |
| `:292` (A106/A117) | `std::style::prelude` publishes its 46 designed names, not 21 alias spellings. | **Net-zero vs v0.40.0** — the prelude is new in this window (no `std::style::prelude` in the v0.40.0 tree). |

### 2.5 rpc / wire

| Entry | What changed | Migration |
|---|---|---|
| `:499` (A108) | The Wire visitor's receivers are `&mut`. | A hand-written `impl .. with Wire`: `serializer: &mut S` / `deserializer: &mut D`; a describer closure `\|s: Serializer\| id.describe(s)` → `\|mut s: Serializer\| id.describe(&mut s)`; `[derive(Wire)]` types need nothing. |
| `:1047` (B289/B301) | `[derive(Wire)]` emits the wire codec only; the JSON pair is `[derive(Json)]`'s. | A type that wants both asks for both: `[derive(Json, Wire)]`. |
| `:1086` (the entry names no item) | An `[rpc]` method returning a source has a SYNC stub answering `RemoteSource<T>` directly, and calls nothing until leased. | Drop the `!` and the `Option` unwrap; read `status()` where you read `Err`; `std::memo::Memo<K, V>` keeps one handle per id. |
| `:496` (B363) | An awaited `void` stub answers `Result<void, RpcError>`. | **Net-zero vs v0.40.0** — A107's `Option<RpcError>` shape (its feature entry sits just above, `CHANGELOG.md:493`) never shipped; kolt's `model.vl` is the one known site of it. |

### 2.6 Tooling

| Entry | What changed | Migration |
|---|---|---|
| `:818` (B318/E109) | `[doc(hidden)]` is retired (refused, the item still parses). | Delete the attribute; an unexported item is what it promised (and never delivered: the editor never read it). |

No other breaking entry is CLI- or editor-only; the diagnostics and editor
work of the window is all `tooling`/`diagnostics`-family and non-breaking.

**Net for a v0.40.0 user: 30 breaking changes with a migration line**, four
net-zero entries (`:340`, `:292`, `:496`, and the `not`-marker half of
`:1080`), and one superseded entry (`:872`).

## 3. The two breaking trains Order 42 merges LAST

Both are PREPARED this order as saved patches with their estate censuses
(briefs41, lanes index-41 §6 and reactive-41 §3) and merged by two Order 42
lanes after every other lane (R-a). What each one carries, and what its merge
must re-run, as the papers state it:

### 3.1 First: I5 S2 — `usize` at the std positions (ONE commit)

- **The patch** — `sweeps/order41/index-41/`: the codemod (`index-type.md`
  §8.1, a fixed-point loop over the naming diagnostic's fixes, NOT A101's text
  rewriter) run over a scratch tree and diffed; the 105 std index positions
  (`index-type.md` §3.1), the 76 WIRE/STREAM/SEQUENCE positions left alone with
  an explicit conversion where they meet an index (§2.2, §9 S2), the 7
  sentinels and 8 `>= 0` loops by hand, each named in the commit (§3.4, §3.5);
  the naming diagnostic and quick fix (§8.2, §8.3; E218 carries the steer
  already, from index-41).
- **The estate sweep** — std; the corpus; the docs' fences; the 251 explicit
  namings in 56 files, **207 of them inside `.vl` consts in Rust test files**
  (`index-type.md` §3.2); vilan-website; vilan-playground (not a git
  repository — its six programs `vilan check`ed, per notes41's sweep item);
  kolt's three sites are the OWNER's (`rotary.vl` the one that needs thought,
  §9 S2).
- **Goldens** — `index-type.md` §5.4: the JS emission does not change, so
  `corpus`, `split`, `examples` and `copy_elision_census` must NOT move; a moved
  JS golden is a finding, not a regen. The native census
  (`crates/vilan-cli/tests/native-copy-census.tsv`) and the native differential
  may move where std's signatures reach Rust's `usize` — read the diff before
  regenerating. `grammar_sync` does not move (the type and suffix are S1's,
  this order).
- **Its release-notes line** (R-b, GO'd "all recs"): a length or position in
  std is `usize`; `.as_usize()`/`.as_i32()` convert, the quick fix inserts
  them; file offsets in `std::fs` stay `i53` (Q1); a `usize` in an rpc
  signature moves the contract hash, so rebuild both halves (Q2); frames are
  byte-identical (ruling 5, §6).

### 3.2 Second: A124 S2c — the combinator flip (ONE commit)

- **The patch** — `sweeps/order41/reactive-41/`: `map`/`combine`/`flatten`/
  `switch`/`and_then` return nodes (`reactive-pipeline.md` §5 S2c); the blanket
  over `dyn Source<T>` so `map` through a `dyn` works — dyn-40's refusal pin
  becomes a pass (the A124 dyn ruling).
- **The estate sweep** — every `SignalCell<` annotation naming a combinator's
  result: std's internal uses in `std::ui`, `std::rpc` and `std::router`; the
  corpus; the docs' fences; vilan-website; vilan-playground; the `.vl` consts in
  Rust tests; every `update` reached on a derivation renamed to `.cell()`
  (§5 (2)). kolt's counts (19 fields, 3 needing `dyn`, the annotated locals,
  §4.2) are the owner's, at A124 S3.
- **Goldens** — THIS train moves them: every corpus/split/example program
  whose emitted JS constructs a combinator now builds a node instead of a cell
  (`corpus`, `split`, `examples`); `copy_elision_census` may fall (a node holds
  no value to clone); the `shared_census` literal moves by the cells the flip
  removes (140 on 1265ea5d; S2b moves it first by the `.cell()` count). Then
  `regen_goldens.sh` over the merged tree, the whole native set and the native
  differential — F34's native `map` is re-run on nodes by native-41 this order.
- **Its release-notes line** (`reactive-pipeline.md` §5): same names, new
  return types; `let x: SignalCell<U> = s.map(..)` becomes `let x = s.map(..)`
  or `s.map(..).cell()` where a cell is wanted; a `Source`-typed parameter takes
  a node unchanged; `.cell()`, `.distinct()` and `Resource<T>` (S2b, Order 41)
  are the new names.

### 3.3 Why this order, and how it answers the bisect worry

I5 S2 FIRST, because its goldens must not move: merged onto a green base, any
golden movement is a defect in it and is caught by the gate as such. A124 S2c
SECOND, because it moves goldens by design, and landing it on a tree whose
goldens were just shown unmoved makes every movement attributable to the flip.
The pipeline paper's Q5 worry — "two breaking trains in one cut makes a bisect
between them impossible" (`reactive-pipeline.md` §9) — is met at COMMIT
granularity rather than at release granularity: each train is one commit, each
merge is followed by the merge helper's build step, the golden regen and the
full gate (briefs41's Mechanics and ownership map), so `git bisect` between
the two is one step. The reverse order is not wrong, only noisier; §8 Q1 asks.

Both merges touch std, and their overlaps are small and known in advance: I5
S4 (A112's `// I5` markers, `std::ui`'s row positions, `KeyedCell.positions`)
is deliberately AFTER S2 (`index-type.md` §9, briefs41 Order 42 queue), so S2c
and S2 do not compete for `std::ui`'s position code.

## 4. What the cut does NOT wait for

- **kolt's migration** — A124 R4 RULED 2026-09-22: "the v0.41.0 cut may come
  BEFORE the migration if that works better — it is not a blocker on the cut"
  (`reactive-pipeline.md` §5). The same holds for kolt's I5 sites (the owner's)
  and the owed list at the owner's word (briefs41 "At the sweep"). kolt is RED
  on 1265ea5d3 for A125's two hand `Hashable` impls regardless (briefs41 Base).
- **A122's build** — `proposal/tuple-module.md` §7: after the train, Order 42 at
  the earliest, not part of the cut.
- **C14 S5** — the JS counted mode, "optional, queued" (C14's Order 37 record;
  R-d keeps it queued).
- **L22** — `publish-brew`'s `app-id` input is deprecated upstream at
  `create-github-app-token` v3.1.0; `release.yml` pins v2.2.2, so the cut is
  unaffected until the v3 bump (L22's own text).
- **The beta switch** — deferred (§1).

## 5. The rehearsal, re-derived as a dry list against 1265ea5d (L23)

L23 (CLOSED 2026-09-21) made `release.yml` dispatchable as a dry run — every
publishing step guarded on the ref being a `v*` tag — and its third rehearsal
(run 35645802713, on c3f7d1a3) was green. `release.yml`, `cut-release.sh`,
`fold-release.sh`, `bump-version.sh` and `install-dev.sh` are unchanged since
c3f7d1a3 (`git log c3f7d1a3..1265ea5d` over the five paths is empty). The list,
with what was RUN today marked:

### 5.1 Before the cut

1. **The seal is green on origin** — `cut-release.sh` reads `ci.yml`'s run at
   the exact sha and refuses anything else (releases.md §7.2 step 4, L17).
   **RUN**: `ok ci.yml is green on origin at 1265ea5d`.
2. **Marker parity** under `## Unreleased` (releases.md §7.2 step 3's manual
   cross-check after any CHANGELOG union). **RUN**: `651 651`.
3. **Every entry's commit is an ancestor of the tag commit** (sweep (a),
   releases.md §7.1). **RUN** — see 5.2.
4. **The trains' CHANGELOG entries carry `<!-- family: breaking -->` directly
   above their heads** (the script refuses otherwise, never guesses).
5. **Rehearse `release.yml` on the sealed commit**: `gh workflow run release.yml
   -R vilan-lang/vilan --ref next`, and require green — the gate (ubuntu +
   windows), fmt/clippy/audit, five platform builds, wasm, vsix, the asset list
   (ten assets). Recommended at Order 42's seal although the workflow has not
   changed since rehearsal 3, because the TREE has (N125 renames a crate the
   build embeds; v0.41.0 is the first release carrying `vilan-rt` and
   `vilan-rt-sqlite` embedded, F19).

### 5.2 The cut's dry run — RUN against 1265ea5d

`cut-release.sh --against 1265ea5d --date 2026-09-24 --out <scratch> 0.41.0`:

- CI: `ok ci.yml is green on origin at 1265ea5d`.
- Sweep (a): **650 `ok`, 1 RED — the cut REFUSES on 1265ea5d** (§7 F0): `no
  commit in this repository introduced this entry`, for the `performance`
  entry at `CHANGELOG.md:1893` ("The viewport semantic-token request now costs
  the viewport …", E122). Five `note: … touched records only` (34d12d06,
  01684b36, aec708ac, 5b0faf43, f30897ee) — not fatal, each to be confirmed.
- Lifetimes: no section printed — **no `deprecates:`/`removes:` marker exists
  anywhere in the CHANGELOG** (§7 F4).
- Order: breaking 35, miscompile 39, fix 153, feature 113, performance 61,
  tooling + diagnostics 250 — the script's `rank_of` puts `diagnostics` with
  `tooling`.
- The script refused before writing `--out` (the RED above). The proposed
  section was therefore produced by running the script's OWN parser — its
  `CHANGELOG_AWK` program, extracted verbatim, in `mode=rewrite` — which is
  what the apply step runs; nothing in the tree changed (`git status` clean
  before and after).

### 5.3 The release-notes cap — RUN locally over the proposed section

GitHub caps a release body at **125,000 characters**; `release.yml`'s "Release
notes from the changelog" step (`release.yml:445`, added after v0.40.0's
publish failed with HTTP 422 at 221,530 characters, commit d9532a9e) keeps
WHOLE entries up to a **110,000-character** margin — splitting on
`\n<!-- family:` and counting `len(text)` of the decoded text, i.e. characters,
GitHub's unit — and appends a pointer to the CHANGELOG for the rest. The step is
guarded on a tag ref, so **no rehearsal exercises it**; running its Python over
the proposed section is the only rehearsal it gets.

Run over that rewritten section: the `## v0.41.0` section is **1,527,325
characters** (1,536,391 bytes) — 12× the cap and 7× v0.40.0's 221,530. The step
keeps **41 entries — all 35 `breaking` and the first 6 `miscompile`** — at
108,416 characters and points at the CHANGELOG for the other **610**. The
breaking family ends at character 97,344, so the headroom before a BREAKING
entry is dropped is **12,656 characters**.

What that means: **the GitHub release body will carry the breaking family whole
and only the first few miscompiles** — the other ~610 entries are behind the
link. The breaking family alone reaches character 97,344 today, and Order 41 and Order
42 add to it (the two trains' entries at least), so the margin before the cap
starts dropping BREAKING entries is 12,656 characters — four or five entries of
this window's typical length (35 breaking entries average 2,749). §8 Q3 recommends a
digest preamble (§2 of this plan, shortened) placed between the version heading
and the first entry at the cut: the step keeps `entries[0]` — the text before
the first `<!-- family:` — unconditionally, so a preamble always survives.

### 5.4 The cut, the tag, the publish

1. `scripts/cut-release.sh --commit 0.41.0` on the sealed commit — retitle and
   order, `bump-version.sh 0.41.0` (§6), the `release: v0.41.0` commit.
   **Fix §7 F0, F1 and F4 first**: the sweep refuses one entry, the `git add`
   list omits three bumped manifests, and A95's deprecation has no marker.
2. Amend the release commit's body with the release's prose (the script's own
   instruction) — and, if §8 Q3 is taken, the preamble.
3. `git tag v0.41.0`; `git push origin next`; `git push origin v0.41.0` — the
   human's steps, printed verbatim by the script (releases.md §7.2 steps 4–5).
4. Watch `release.yml` to green: the gate re-runs the full suite on the tagged
   tree; ten assets; five publish channels, four one-way. The notes step
   truncates per 5.3.

### 5.5 The fold

`scripts/fold-release.sh v0.41.0` (releases.md §7.2 steps 6–10): merge the tag
into `main` with `Merge v0.41.0 — main catches the release train`, fast-forward
`next`, dispatch `docs.yml` FIRST and `deploy.yml` SECOND (they push the same
pages repo from different concurrency groups), verify
`https://vilan-lang.org/playground/manifest.json` reads `v0.41.0`, then
`install-dev.sh` from the main worktree.

### 5.6 The toolchain in both locations — RUN

`fold-release.sh v0.41.0 --dry-run` today: `RED no tag v0.41.0` (expected —
nothing is cut), and both binaries reported `stale`:
`/home/reed/.vilan/bin/vilan is vilan 0.40.0 (1265ea5d3)` and
`/home/reed/.cargo/bin/vilan is vilan 0.40.0 (1265ea5d3)`. Step 10 runs
`install-dev.sh`, which installs into `~/.vilan/bin` and refreshes an existing
copy in `~/.cargo/bin`, then asserts `--version` in both; `vilan-lsp` has no
`--version`, so restart the language server by hand. Which binary a shell finds
differs between interactive and non-interactive shells, which is why both.

## 6. The version bump's files

`git grep -F 0.40.0` outside `CHANGELOG.md` on 1265ea5d finds 18 files. What
`bump-version.sh 0.41.0` changes, and what it does not:

| File | Line | Bumped by |
|---|---|---|
| `crates/vilan-cli/Cargo.toml` | 3 | `bump-version.sh` (sed over `crates/*/Cargo.toml`) |
| `crates/vilan-core/Cargo.toml` | 3 | same |
| `crates/vilan-embedded-std/Cargo.toml` | 3 | same — **`crates/vilan-embedded/` after N125** |
| `crates/vilan-ide/Cargo.toml` | 3 | same |
| `crates/vilan-lsp/Cargo.toml` | 3 | same |
| `crates/vilan-wasm/Cargo.toml` | 3 | same |
| `crates/vilan-rt/Cargo.toml` | 17 | same — **not in `cut-release.sh`'s `git add` list** (§7 F1) |
| `crates/vilan-rt-sqlite/Cargo.toml` | 18 | same — **not in the list** |
| `crates/vilan-rust/Cargo.toml` | 9 | same — **not in the list** |
| `Cargo.lock` | 9 member entries | `cargo update --workspace` |
| `editors/vscode/package.json` | 5 | `npm version` |
| `editors/vscode/package-lock.json` | 3, 9 | `npm version` |
| `THIRD-PARTY-NOTICES.txt` | 1207 (`Covers: vilan-cli 0.40.0, …`, nine crates) | **nothing** — `cargo about generate about.hbs -o THIRD-PARTY-NOTICES.txt` (CLAUDE.md); `third_party_notices` is name-level by design, so no gate notices (§7 F2) |
| `CHANGELOG.md` | the section heading | `cut-release.sh` (retitle) |

Not to bump — history that names the release: `release.yml:454`,
`scripts/fold-release.sh:216`, `analyzer.rs:49922`,
`tests/inference/generics.rs:5852`, `tests/inference/platform.rs:8914`. Each
Cargo.toml has exactly one line starting `version =` (its `[package]` one), so
the script's anchored `sed` touches nothing else.

## 7. Finds — to fix before the cut

**F0 (the cut REFUSES today) — sweep (a) cannot trace a head reworded inside a
merge.** The E122 entry's head was introduced by dff2c268 ("close E122 and
E123", 2026-09-01) and REWORDED — "(measured before E121's keystroke path
landed, at loadavg 8.2–11.9)" appended — in the conflict resolution of merge
f261a90d ("Merge lane e122 (Order 25)"). `cut-release.sh`'s derivation is `git
log --all -S"**<head>**" -- CHANGELOG.md`, and `git log` shows no diff for a
merge without `-m`, so no commit "introduced" the current head and the entry
REDs although its code landed (f261a90d is an ancestor of 1265ea5d; `git log
--all -m -S…` finds it). Fix now, S: a `<!-- commit: f261a90d -->` line
directly above the entry's `<!-- family: performance -->` — the override the
script documents for exactly this. Fix for good, S: the derivation adds `-m`
(or falls back to it when the plain search is empty), with a `release_scripts`
pin that rewords a head in a merge. Either way the cut cannot run on 1265ea5d
as it stands; the next CHANGELOG union can add another.

**F1 (the cut's own commit would be wrong) — `cut-release.sh`'s
`RELEASE_FILES` omits three crates.** `scripts/cut-release.sh:621–624` stages
`CHANGELOG.md Cargo.lock` and the manifests of `vilan-cli`, `vilan-core`,
`vilan-embedded-std`, `vilan-lsp`, `vilan-wasm`, `vilan-ide`, plus the
extension's two files — the six crates v0.40.0 had (`git show 4150fa7c
--stat`). `vilan-rt`, `vilan-rt-sqlite` and `vilan-rust` arrived after v0.40.0
(F1 S1a, Order 37; F18 slice 2). `bump-version.sh` bumps all nine, so
`--commit` would leave three bumped manifests UNSTAGED — the `release:` commit
and the tag would carry them at 0.40.0 beside a `Cargo.lock` that says 0.41.0,
and the worktree dirty. The printed manual `git add` line has the same
omission. Native builds are unaffected (they depend on `vilan-rt` by path,
`vilan-rust`'s `cargo_manifest`), so this is a wrong tag tree rather than a
broken binary. Fix: derive the list (`crates/*/Cargo.toml`) instead of naming
it, with a `release_scripts` pin that the list covers every workspace member —
S, and it lands with or before N125, which renames one entry in the same list
(N125's text names "the release scripts").

**F2 (cosmetic) — `THIRD-PARTY-NOTICES.txt` will say 0.40.0 in a 0.41.0
release.** Nothing in the cut regenerates it. Regenerate in the release commit
if `cargo about` is available; otherwise accept it, since the check is
name-level on purpose (`third_party_notices.rs`'s header).

**F3 (notes) — the release body will drop 610 entries and has 12,656
characters of headroom before it drops a BREAKING one** (§5.3). Not a defect —
the step does exactly what it was written to do — but the first cut where the
margin is this thin.

**F4 (the next minor would refuse) — A95's deprecation carries no lifetime
marker.** `CHANGELOG.md:700` opens the one-release deprecation window of
`Style::attribute`'s and `Style::within`'s `Option<str>` form (style-conditions
§12 (iv), per the entry), but no `<!-- deprecates: KEY -->` line sits above it
— none exists anywhere in the CHANGELOG. `cut-release.sh` REFUSES a `removes:`
whose `deprecates:` never shipped in a released section
(`proposal/deprecation.md` §3), so the ruled removal at v0.42.0 would be
refused, and the cut's "deprecations still in their window" report stays empty
when it should name these two. Fix before the cut, S: two marker lines above
`:700`'s family marker — `<!-- deprecates: std::style::Style::attribute -->`
and `<!-- deprecates: std::style::Style::within -->` (the KEY is the fully
qualified path; the exact spelling of an argument-FORM deprecation is the
entry author's, §8 Q5).

## 8. Open questions, with a recommendation each

**Q1 — which train merges first?** *Rec: I5 S2, then A124 S2c* (§3.3): the
train whose goldens must not move goes first, so the one that moves them by
design lands on a verified baseline. Nothing in the rulings fixes the order.

**Q2 — fold the four net-zero entries at the cut?** `:340`, `:292`, `:496` and
the `not`-marker half of `:1080` break nothing a v0.40.0 user wrote. *Rec: keep
them as written* — the family is the author's judgement (releases.md §7.2 step
3), and against the unreleased shapes kolt DID write (`model.vl`'s `Option`
stub) they are breaking; the preamble of Q3 says which are net-zero instead.

**Q3 — a digest preamble in the release section?** The notes step always keeps
the text before the first entry, so a preamble is the one place the WHOLE
breaking list is guaranteed to reach the GitHub release body. `cut-release.sh`
refuses prose under `## Unreleased`, so it is written into the `release:`
commit (after the retitle, before the tag) — the script already tells the
cutter to amend that commit. *Rec: yes — one line per §2 row, ~6,000
characters*, written at the cut from this plan with Order 41's and 42's
breaking entries added.

**Q4 — rehearse `release.yml` again at Order 42's seal?** *Rec: yes* (§5.1
item 5) — one dispatch, nothing published; the tree changed under the workflow
(N125, the embedded native runtime) even though the workflow did not.

**Q5 — how is a deprecated argument FORM keyed?** F4's deprecation is of one
form of `attribute`/`within` (the `Option<str>` value), not of the methods, and
`deprecation.md` §3's KEY is a path. *Rec: key the method path and say "the
`Option<str>` form" in the entry* — the removal's `removes:` then names the
same path and the pairing check holds.

## 9. The recommendations, collected

0. **Unblock the cut first**: the `commit:` marker for the E122 entry (F0)
   and the two `deprecates:` markers for A95 (F4) — CHANGELOG-only edits any
   lane can carry; the `-m` fallback in sweep (a) with its pin.
1. **Merge I5 S2's commit, then A124 S2c's**, each followed by the build step,
   `regen_goldens.sh` (S2c only — S2 must move no JS golden) and the full gate;
   cut at Order 42's seal (§3).
2. **Fix F1 before the cut** — derive `RELEASE_FILES` from the workspace, with
   a pin; do it with N125's rename (§7).
3. **Regenerate `THIRD-PARTY-NOTICES.txt`** in the release commit if `cargo
   about` is to hand (§7 F2).
4. **Write the digest preamble** from §2 into the release commit so every
   breaking change reaches the release body (§8 Q3).
5. **Rehearse `release.yml` by dispatch on the sealed commit**, and run §5.3's
   notes check over the `--out` section before tagging (§5).
6. **Do not wait** for kolt, A122, C14 S5 or L22 (§4).
