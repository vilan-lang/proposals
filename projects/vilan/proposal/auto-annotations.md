# `auto` annotations — types the toolchain writes and keeps current (B570)

> Status: **DRAFT 2026-10-08 — for the owner's ruling.** Written by lane papers-b-48 of
> Order 48 against `vilan 0.45.0 (e75bc57c3)` = `origin/next` @e75bc57c, read at that
> commit in the worktree `vilan/.claude/worktrees/papers-b-48`. Nothing in the vilan tree
> changed. Every claim about today's behaviour is a probe that was run or a line that was
> read, and says which.
>
> Probes: `scripts/integration/sweeps/order48/papers-b-48/probes/b570/` (cited `uN`), re-run
> by `probes/run_all.sh <scratch>`, output in `probes/run_all.out`. The counts of what an
> opt-in would write come from `papers-b-48/census/` (a walker over the tree's own parser);
> the interface numbers from incr-47's S0 session (`sweeps/order47/REPORT-incr-47.md`) and
> `incremental-analysis.md` §2.3.
>
> Related:
> - B570 (this paper), with the owner's stamp of 2026-10-05 accepting the integrator's six
>   points as the starting position;
> - M110 and `incremental-analysis.md` (§5: S5 the id-window spike, S6 the interface
>   firewall, S7 per-item records), incr-47's S0 fingerprints (`vilan_core::incremental`);
> - B571 (`type-ascription.md`: `as auto T`) and E278 (per-stage hints), B569
>   (`named-tuple-fields.md`), written beside it;
> - E227 (`inlay-hint-abbreviation.md`, built: `[hint(..)]`, `~Pipe<T>`), B161 (a bare trait
>   at a binding is checked and the concrete type kept), `opaque-returns.md` (ruled door
>   (ii), opacity at returns — unbuilt);
> - the existing `vilan check --fix` loop and `vilan.organizeImports.onSave`.

## 0. The ask, and the answer up front

The owner: an annotation marked `auto` is written by the toolchain, not the author. Editing
the body so the inferred type changes rewrites it; a bare `auto` is filled. His four aims:
(1) the compiler may skip or defer type work; (2) the author writes `auto` and gets the type;
(3) it does an inlay hint's job but lives in the file, so a reader without an IDE sees it;
(4) an opt-in to write `auto` wherever a type is not written.

**Accepted as the starting position (2026-10-05):** returns and module bindings first; a
stale `auto` is refused by `check`/`build` with a `--fix` (the lockfile reading); the rewrite
lives in `check --fix` and an editor on-save action, not the syntactic formatter; say what
is written for long stage types; `auto` is output only and does not direct inference; the
opt-in is per package, exported items by default.

**The answer.**

1. **`auto T` is a signature, not a constraint.** The body is inferred exactly as if the
   annotation were absent; CALLERS read `T`; `check` compares the two and refuses a
   difference as stale, with the rewrite as its fix. In any program that checks, `T` is the
   inferred type, so the annotation changes nothing a program does — that is "output only" —
   and yet the item's interface can be read from the parse alone, which is the firewall.
2. **The lockfile reading, made precise.** `check`, `build`, `run` and `test` refuse a stale
   `auto T`; callers are checked against the WRITTEN `T` in between (so a clean analysis and
   an incremental one agree, which M110's differential demands); `vilan check --fix` rewrites
   in its existing fix loop; the editor rewrites on save through
   `editor.codeActionsOnSave`, as `vilan.organizeImports.onSave` does. `vilan fmt` never
   touches an `auto`. A bare `: auto` locks nothing, so it is a WARNING with the fill as its
   fix (Q4).
3. **Long stage types: `auto` writes what the inlay hint shows**, with E227's `~Pipe<T>`
   written as the bare trait `Pipe<T>` — checked as B161 checks a bare trait at a binding
   (admitted, concrete type kept). So `fun doubled(..): auto Pipe<str>` where the type is
   `Derive<Distinct<Derive<SignalCell<i32>, i32, i32>, i32>, i32, str>` (u02). It does not
   churn when an upstream stage is added. It is no firewall (callers still hold the concrete
   type); the firewall for a pipe is the opaque return, a real annotation (§6).
4. **The firewall win is real and measurable.** In incr-47's S0 session (40 kolt keystrokes)
   interfaces moved on 4 — all broken mid-statement states in `model.vl`, whose hot set is
   12 of 27 modules. Under `auto` those 4 move nothing. Past S0, `auto` turns 99 of kolt's
   262 hand-written functions (38% omit their return) and 32 of its 33 module bindings into
   items whose interface is SYNTACTIC: S6 can decide "interface unchanged" before the edited
   module is walked, and S7 can check callers without waiting for a body (§9).
5. **The opt-in** (`[check] auto = "exported"` in `vilan.toml`) would write 54 annotations in
   kolt (25 exported returns, 29 exported module bindings; 99 counting inherent methods), 234
   in the website (all module bindings, mostly `const` style values: `auto Style`),
   and 17 in std's exported free surface (126 with its inherent methods). Void returns are
   never written.

## 1. Ground truth (0.45.0)

| probe | program | result |
|---|---|---|
| u01 | `fun five() { 5 }`, `let x: f64 = five();` | "Expected f64, but got i32 … convert with `.as_f64()`" — an inferred return is decided by its BODY, not its callers |
| u02 | `fun doubled(cell) { cell.derive(..).distinct().derive(\|v\| i"{v}") }` | the return renders `Derive<Distinct<Derive<SignalCell<i32>, i32, i32>, i32>, i32, str>` |
| u03 | `mut items = [];` at module level, `items.push("a")` in `main` | checks, prints `1` — a module binding's type is decided by a USE in another function |
| u04 | `import std::web::style::prelude::auto; let a = auto();` | checks — `auto` is a std function's name (`Length::auto()`, the style prelude's `auto()`) |

Read in the tree:

- **`vilan check --fix` already exists**: "apply the fixes the diagnostics carry to the
  package's own files, repeating until a round finds nothing more to fix" — moved std paths,
  numeric mismatches. A stale `auto` is one more diagnostic carrying a fix.
- **The editor already rewrites on save**: `vilan.organizeImports.onSave`
  (`editors/vscode/package.json:156`) is "a client-only concern — `editor.codeActionsOnSave`"
  (`vilan-lsp/src/main.rs:80`), and the server advertises `source.fixAll`
  (`main.rs:1407`).
- **`vilan fmt` is syntactic**: it reprints from `parse_preserving_groups`' tree and leaves
  a file it cannot parse untouched. It has no analysis to fill a type from.
- **S0's fingerprints** (`vilan_core::incremental`): per item, "a function's declaration
  label (the inferred return included), async, the contexts …, its platform requirement …,
  and `borrows`/`bumps`; a type's shape; a module binding's type", content-hashed text with
  no `TypeId`.
- **E227's renderer** (`analyzer/hint_labels.rs`) prints a hinted node as `~Trait<..>` only
  when the instantiation is ADMITTED by an impl of that application, else in full.

u01 and u03 are the two halves of the interface problem: a function's inferred return needs
its body analysed before callers know it, and a module binding's type can need a body
ELSEWHERE (i7 in `incremental-analysis.md` §2.2).

## 2. The grammar

```text
annotation  = ":" ( "auto" [ type ] | type ) ;    (* return, module `let`, local `let` *)
ascription  = "as" [ "auto" ] type ;              (* B571 *)
```

`auto` is **contextual**, by the rule `dyn` already follows (`parse_type_atom`, B414): at an
annotation's head it is the marker, except `auto::`, which is a path into a module named
`auto`. After the marker comes a type, or the annotation's end (`=`, `{`, `;`, `,`, `)`, or a
`context`/`borrows` clause). `auto` stays an ordinary name everywhere else, so std's
`Length::auto()` and the style prelude's `auto()` are untouched (u04); no type in the estate
is named `auto`.

| position | `auto` | slice |
|---|---|---|
| a free `fun`'s return, an inherent method's return | yes | S1 |
| a module `let` / `mut` | yes | S1 |
| `as auto T` (B571) | yes | S2 |
| a local `let` | yes | S3 |
| a trait impl member's return | refused: the trait fixes it, nothing is inferred | — |
| a parameter, a field, a trait declaration, a closure parameter | refused: nothing is inferred there | — |

## 3. What it means: a signature, not a constraint

For an item annotated `auto T`:

1. **The body is inferred as if unannotated.** `T` never enters it as an expected type: a
   literal is not coerced (`fun f(): auto f64 { 5 }` infers `i32` and is STALE, never an
   `f64`), a `None` takes no argument from it, a stage is not erased to a `dyn`.
2. **Everything outside reads `T`.** Callers, importers, hover at a use, the S0 fingerprint.
3. **`check` compares** the inferred type with `T` (§4.1) and refuses a difference.

In a program that checks, (1) and (2) give the same type, so `auto` changes no program's
meaning; deleting every `auto` from a checking program leaves it checking and emitting the
same code. That is "output only" (accepted point 5), and §7 says why the body must not read
`T`. What (2) buys is that the interface no longer depends on the body.

**Why callers read the written `T` and not the inferred one** while the two differ: M110's
edit-replay differential requires the incremental analysis's diagnostics to equal a clean
analysis's. An incremental analysis that firewalls on `T` (§9) checks callers against `T`;
so must the clean one, or the two differ exactly in the stale state. It is also the lockfile
reading: what is written is what was promised, and the stale diagnostic says so —
"`load` now returns `str`; its 3 callers were checked against the written `auto i32`.
`vilan check --fix` rewrites it and re-checks them."

## 4. Stale, and who rewrites

### 4.1 The comparison

Two types are the same when their RESOLVED forms are equal — A144's resolution, so an alias
and its target match, `hash_map::HashMap<str, i32>` and `HashMap<str, i32>` match, and a
spelling the author chose is never rewritten while it still means the inferred type. B569's
labels take part (a label change is a type change a reader should see). A bare trait in an
`auto` type matches by E227's admission (§6). An `auto` whose inferred type is still a hole
(`unknown`) is neither filled nor stale: it reports the hole ("cannot infer the return of
`f`: …"), as an unannotated item would.

### 4.2 The command line

- **`vilan check`, `build`, `run`, `test`**: a stale `auto T` is an ERROR at the annotation,
  carrying the rewrite as a machine-applicable fix. CI catches drift with the command it
  already runs; no new flag.
- **`vilan check --fix`**: applies the rewrite in its existing loop (each round is a full
  analysis; the loop repeats until nothing is left), so a rewrite that changes what callers
  see re-checks them in the next round, and a caller's own `auto` that moves as a result is
  rewritten in the round after.
- **A bare `: auto`** is a WARNING ("unfilled `auto`: the return is `i32`"), with the fill
  as its fix. It promised nothing, so nothing can be stale, and an unfilled `auto` must not
  stop `vilan run` on a scratch file. Callers read the inferred type through it, as through
  no annotation.

### 4.3 The editor

- **On save**: a code action of kind `source.fixAll.vilan.auto` that the client fires
  through `editor.codeActionsOnSave` when `vilan.autoTypes.onSave` is set — the
  `organizeImports.onSave` shape. It edits only `auto` annotations, from the analysis the
  editor already holds (no extra analysis), and it does nothing when the file has errors
  other than stale or unfilled `auto`s: a type filled from a broken program is noise.
- **While typing**: a stale `auto` shows its diagnostic, and an inlay hint after it shows the
  type it would become (`: auto i32` ⟶ ` str`), so aim (3)'s "the file shows the type" holds
  between saves too.
- **A quick fix** on any unannotated return or module binding: "Add `auto` type".

### 4.4 Not the formatter (accepted point 3)

`vilan fmt` stays syntactic. Giving it an analysis mode would make formatting need the whole
analysed world, fail on a program that does not check, and cost a full analysis per format
(today it is a parse) — on kolt an analysis is 9–14 G instructions (incr-47's S1 rows,
editor-46's 14.3 G keystroke), against a parse and a reprint per format. The formatter only prints an `auto T` canonically (one space after
`auto`).

## 5. Naming the type

`--fix` writes the shortest spelling that RESOLVES in the file:

- a name in scope as itself (`Channel`); else through an imported module (`reactive::Derive`);
  else the full path (`std::reactive::Derive`). It never adds an import (that changes the
  scope and can shadow).
- B569's labels as hover prints them: `auto (min: i32, max: i32)`.
- A type the file CANNOT name — a private type of another module (B318 visibility), an
  `[internal]` std type — is not written: the fix declines with a note ("`f` returns
  `rpc::Held`, which this module cannot name"), and the item stays unfilled.
- A void return is written only when the author wrote `: auto` on it; the opt-in never writes
  `auto void`.

## 6. Long stage types

u02's return is `Derive<Distinct<Derive<SignalCell<i32>, i32, i32>, i32>, i32, str>`: 62
characters, and it changes whenever a stage is added or removed upstream. Three doors:

| door | written | churn | firewall |
|---|---|---|---|
| (a) the full type | `auto Derive<Distinct<Derive<SignalCell<i32>, i32, i32>, i32>, i32, str>` | every upstream stage | yes: the full type is the interface |
| (b) the hint's trait, as a bare trait | `auto Pipe<str>` | only when the carried type changes | no: callers still hold the concrete type |
| (c) nothing; steer to an opaque return | `: Pipe<str>` (a real annotation; opacity, door (ii)) | none | yes, and stronger: callers see only the trait |

**Recommendation: (b) for `auto`, with (c) as the steer.** The rule is one sentence:
**`auto` writes what the inlay hint shows, with E227's `~X` written as the bare trait `X`.**
The check for a bare trait at any depth of an `auto` type is E227's admission (the
instantiation is admitted by an impl of that application), and B161's reading at a binding:
checked wide, kept narrow. Elsewhere in the type, equality. So:

- the file reads as the editor did (aim (3)), at the length a reader wants;
- E278's code action and `auto` share ONE writer (`type-ascription.md` §11);
- a function returning a pipe gets a stable `auto Pipe<str>` that goes stale only when what
  it carries changes;
- the FIREWALL for such a function is (c), which the author chooses deliberately because it
  narrows what callers may do. `--fix` never writes (c): it changes the program.

Under (b) the S0 fingerprint of such an item must still include the concrete inferred type
(callers may reach concrete members, and mono needs it). The firewall arithmetic of §9 counts
only fully-written `auto` types.

## 7. Output only (accepted point 5)

If `auto T` directed inference, a stale `T` would change what the body MEANS: `fun f():
auto f64 { 5 }` would quietly make `5` an `f64`, `auto dyn Flow<i32>` would erase, and the
"lock" would be an annotation the toolchain overwrote — so a `--fix` could change runtime
behaviour. Output only makes the rewrite safe by construction: it can only make the written
type agree with a meaning that does not depend on it. The cost is that `auto` cannot be used
to steer inference; that is what a plain annotation, or B571's `as T`, is for.

## 8. The opt-in (accepted point 6)

```toml
[check]
auto = "exported"   # "off" (default) | "exported" | "all"
```

Per package. Under `"exported"`, `vilan check` WARNS on an exported item whose type is
inferred and not `auto`-annotated, with the `auto` as its fix, so `check --fix` (and the
on-save action) writes them; under `"all"` the same for every return and module binding.
"Exported" is an item reachable from outside the module: `export`-marked, or in a file with
`export *;` (B318), and the methods of an inherent `impl` on an exported type (they are
called through it). Void returns are skipped.

What it would write today (census, syntactic: no return type and a value-producing tail;
module `let`s with no annotation):

| estate | exported returns | inherent methods | private returns | exported module bindings | private module bindings | `"exported"` writes |
|---|---:|---:|---:|---:|---:|---:|
| kolt (hand-written; lucide omitted) | 25 | 45 | 3 | 29 | 3 | 54 (99 with methods) |
| vilan-website | 0 | 0 | 0 | 234 | 6 | 234 (240 with `"all"`) |
| `vilan/examples` | 3 | 0 | 7 | 14 | 0 | 17 |
| std (if it opted in) | 16 | 109 | 57 | 1 | 2 | 17 (126 with methods) |

kolt writes 262 functions by hand, of which 163 write their return, 73 omit it over a value
and 26 over `void` (the earlier census in `incremental-analysis.md` §2.3 counted 95 of 256 as
"inferred return" by a looser pattern). 224 of the website's 240 module bindings are
`const` initializers — 191 of them style chains (`const style()..`, `const (base + style()..)`)
and 29 design tokens (`token(..)`, `Length::px(..)`, `Color::hex(..)`) — whose `auto` is a
short `Style` or token type; the rest are string constants.

**Default off**, as accepted. A package turns it on when it wants the firewall or the
readable signatures.

## 9. The interface firewall, quantified

### 9.1 What S0 measured

incr-47's S0 session: ten keystrokes in each of four kolt files (world mode, `client.vl`
open).

| file | hot set | interface moved | what moved |
|---|---|---|---|
| `views.vl` | 2/27 | 0 of 10 | — |
| `theme.vl` | 11/27 | 0 of 10 | — |
| `model.vl` | 12/27 | **4 of 10** | `Channel::create`'s signature, mid-statement (broken text) |
| `styles.vl` (css) | 11/27 | 0 of 10 | — |

"Interfaces almost never move, and the global facts never did" (REPORT-incr-47). Every move
was a broken intermediate state of one function's inferred return.

### 9.2 What `auto` changes

1. **The broken-state moves go to zero.** With `auto` on `Channel::create`, a half-typed body
   is a stale (or broken) body inside `model.vl`; the interface is the written text and does
   not move. Under S6 those 4 keystrokes — 10% of the session, all in the file with the
   largest hot set — re-walk 1 module instead of 12.
2. **The firewall decision moves before the walk.** With inferred returns, S6 must re-walk
   the edited module to compute its fingerprint before it knows whether importers can be
   reused. With every exported item `auto`-annotated (or written), the fingerprint is a
   function of the PARSE: "interface unchanged" is known before analysis starts, so importers
   are reused without waiting, and S7's per-item records can re-check a body and its callers
   in either order — the independence `incremental-analysis.md` §5 names as the shared
   prerequisite of S5–S7 and parallel analysis.
3. **The use-inferred module binding stops reaching across bodies.** u03's shape — a module
   binding typed by a use in another function — is i7, the global fixpoint, and incr-47's S1
   refuses a hot set that imports such a binding (its "use-inferred binding" guard). An `auto`
   on the binding makes its type a declared fact: the guard has nothing to refuse there.
   kolt has 32 module bindings whose type is inferred (29 exported); all are candidates.
4. **How often it matters on edits.** `incremental-analysis.md` §2.3: of 294 function bodies
   the owner changed under an unchanged signature in his `wip` commits, **167 (57%) were in
   functions with an inferred return** — each one an edit whose interface the firewall must
   recompute today and could read from the file under `auto`.

What `auto` does not change: the clean-keystroke cost when nothing moved (S6 already reuses
importers when the recomputed fingerprint is equal), and stage-typed items written as door
(b) (§6), whose fingerprint still carries the concrete type.

## 10. Churn and merge conflicts

- **Every change of an annotated item's inferred type becomes a diff line.** That is the
  point for an exported item — an API change a reviewer should see — and it is rare: S0 saw
  0 interface moves in 36 clean keystrokes. How often a COMMIT moves one in kolt is not
  measured here (lanes run no git in kolt); S0 of the build measures it by running `check
  --fix` across the owner's last N commits in a copy.
- **Stage types** are where churn would concentrate; door (b) keeps it to changes of the
  carried type.
- **Merge conflicts** happen only when two branches change one signature line. Resolution is
  mechanical: take either side, run `vilan check --fix`. Because the comparison is on resolved
  types (§4.1), a conflict that is only spelling resolves to either spelling without a
  further rewrite. A git merge driver is not needed for the first release.
- **No churn from formatting or spelling**: `--fix` rewrites only when the TYPE differs.

## 11. Interactions

- **B571 (`as auto T`).** An ascription the toolchain writes: output only, checked equal,
  stale refused, `as auto` filled. `a() as auto A .b() as auto B` is E278's per-stage hints
  frozen into the file; the first stage whose type moves is the first stale one.
- **E278.** Its code action offers `as auto T` beside `as T`, written by §6's one writer.
- **B569.** Labels are written and compared (§4.1, §5).
- **Opaque returns** (`opaque-returns.md`, ruled door (ii), unbuilt). `fun f(): Pipe<str>` is
  a real annotation and opaque; `fun f(): auto Pipe<str>` is a lock and transparent (B161's
  reading). The paper's rule "a bare trait annotation is what the other side of a signature
  sees" holds: `auto` is not an annotation the other side sees as a constraint, only as the
  written type.
- **E227.** Its admission check is `auto`'s bare-trait check (§6).
- **M110.** S5/S6/S7 gain syntactic interfaces for annotated items (§9); the edit-replay
  differential stays byte-identical because callers read `T` in both analyses (§3).

## 12. Open questions, each with a recommendation

- **Q1. The meaning.** A signature callers read and the body ignores, checked equal; or a
  directing annotation the toolchain overwrites. **Rec: the signature (§3)** — output only
  for the body (accepted), the written type for everyone else.
- **Q2. Callers while stale.** Checked against the written `T` or the inferred type. **Rec:
  the written `T`** — the differential requires one answer for clean and incremental
  analyses, and it is the lockfile reading; the stale diagnostic names how many callers.
- **Q3. Long stage types.** Doors (a), (b), (c) of §6. **Rec: (b), "what the hint shows,
  `~X` as the bare trait `X`"**, with (c) as the documented firewall for pipe-returning
  functions; `--fix` never writes (c).
- **Q4. A bare `: auto`.** An error (unfilled is stale) or a warning. **Rec: a warning with
  the fill as its fix** — it promised nothing, and `vilan run` on a scratch file should not
  stop on it.
- **Q5. The on-save action.** A new `vilan.autoTypes.onSave` setting firing
  `source.fixAll.vilan.auto`, or folded into `source.fixAll.vilan`. **Rec: its own kind and
  setting** (default on once the package opts in, off otherwise), mirroring
  `organizeImports.onSave`; it never runs on a file with other errors.
- **Q6. What "exported" covers for the opt-in.** **Rec: `export`-marked items, everything in
  an `export *;` file, and the inherent methods of an exported type** (§8).
- **Q7. Naming a type the file cannot name.** Qualify, add an import, or decline. **Rec:
  qualify with the shortest resolving path; never add an import; decline with a note for a
  type the module cannot see (§5).**
- **Q8. Locals.** `let x: auto T` in a body (S3) or never. **Rec: S3, after returns and
  module bindings,** as accepted — a local is no interface, so it is aim (3) only.
- **Q9. std.** Should std opt in (17 exported returns + 1 binding; 126 with methods)?
  **Rec: yes, at S4**, measured first: std's interface becoming syntactic is what a
  cross-process std cache (M120) keys on, and std is the largest prefix every analysis
  carries.

## 13. Slices

| Slice | Content | Size | Needs |
|---|---|---|---|
| S0 | Measure: run a prototype `check --fix` over a copy of kolt's last N commits (the integrator's, not a lane's) and count commits that would move an `auto` line; count kolt's stage-typed returns from the analyzer | S | — |
| S1 | Grammar (§2: returns, module bindings); the meaning (§3: callers read `T`, body ignores it); the comparison (§4.1); the stale error with its fix; the bare-`auto` warning; `check --fix` wiring; naming (§5); door (b)'s bare-trait check (§6); the S0 fingerprint reads the written type for fully-written items; pins: stale refused, `--fix` round trip, callers checked against `T`, output-only (a stale `auto f64` over `5`), u03's binding locked | M | — |
| S2 | `as auto T` (B571) | S | S1, B571 S1 |
| S3 | Editor: the on-save action, the stale inlay, "Add `auto` type"; locals | S | S1 |
| S4 | The opt-in (`[check] auto`), §8's warnings; std's opt-in measured | S | S1 |
| S5 | M110 S6 reads syntactic interfaces for annotated items (with incr's lane) | — | S1, M110 S5 |
