# The prelude — a manifest-configurable ambient scope (B156)

> **Status: AMENDED 2026-08-31** (work order 22, cycle 40; tracker item
> [[B156]]) — first proposed in work order 21, cycle 39. The amendment
> rewrites the paper to the **first ruling batch** on B156 (2026-08-29
> evening), which changed three things and dissolved a fourth:
>
> 1. **Two std preludes, not one** — a base set for programs in general and
>    a **web** set for applications, the manifest key selecting between
>    them. The census's own finding (§3.2) — that no single fixed set
>    serves both corpora — is now the design rather than an observation
>    about it. §5 is rewritten around this.
> 2. **Ambient MODULE names are a first-class prelude concept**, beside
>    ambient member names. The web set carries the module `style`, not its
>    sixteen members. §5.2 defines the concept; §5.3 applies it.
> 3. **The `Display` collision is DISSOLVED** by (2), not managed: bare
>    `Display` is `std::display::Display`'s alone, the CSS enum is
>    `style::Display`, and the style enum never renames. §3.4 and §14 Q2
>    are settled accordingly.
> 4. **The alias-only re-exports in std die** — `std::print` named, and the
>    sweep that finds the rest. §10.2 is the ruling and the sweep's full
>    census.
>
> §9.2's implementation mandate is untouched and remains the paper's load-
> bearing constraint: the prelude is a **resolution scope**, never
> synthesized file-head imports.
>
> Everything measured here was measured mechanically against the estate at
> `vilan` @ `2ad39dd0` (v0.39.0), kolt @ its 0.38.0 migration, and the
> website @ its v0.38.0 deploy. Every behavioural claim about the shipped
> compiler was probed against the installed `vilan 0.39.0 (2ad39dd09)`;
> the probes are transcribed in §11. The amendment's own census
> re-verifications were run against `vilan` @ `093bf567`.

## 1. The ask, and the finding that reframes it

The ask, from the owner (2026-08-29): a **prelude** — a set of names in
scope with no `import` — set to a std one by default, overridable per
package with a custom one, spelled in the manifest.

The finding that reframes it: **vilan already has a prelude.** Three of
them, in fact, and the spec already uses the word.

- **The spec's prelude.** `docs/spec/names.md` **§4.7** is titled *The
  prelude* and defines one today: "A small set of names is in scope
  without imports: the primitive types (`i32`, `str`, `bool`, …), `List`,
  `void`, and the boolean/`null` literals' types. Everything else
  (including `Option`, `Result`, `print`) must be imported. (The exact
  prelude is the lang-item table, appendix §A.4.)" The glossary entry
  (`docs/appendix/glossary.md`) says the same. The census below found
  **not one** `import` of `i32`, `bool`, `f64`, `void` or `List` anywhere
  in the estate, and exactly one of `str` — `import pkg::string::str;` in
  std's own `display.vl`. 264 distinct std names are imported across six
  corpora and effectively none of them is a primitive. §4.7's prelude
  works, silently, everywhere.
- **The macro prelude, in program code.** `crates/vilan-core/src/macros.rs`
  `scope_for` composes a file's macro scope in three layers, and layer one
  is literally commented `// 1. The std prelude.` — every std macro is in
  scope in every file with no import. Its type doc states the ordering
  rule verbatim: "same-file definitions shadow imported ones, which shadow
  the std prelude — the ordinary name-resolution order."
- **The macro world's ambient meta prelude.** `world_prelude_nodes`
  (macros.rs:682) puts ten `meta` reflection types plus `source`/`fresh`
  in scope in every macro body with no import, and states its selection
  principle: "Libraries (`option`, `build`, …) stay explicit imports; the
  ambient set is exactly the surface a macro exists to talk to."

So the language has an ambient scope for **types the compiler builds in**,
an ambient scope for **macros**, and an ambient scope for **macro-body
reflection** — and no ambient scope for ordinary std values and types.
That is the gap B156 closes. This is not a new mechanism in vilan; it is
the one namespace that was left out of a pattern the language already
applies three times, with the shadowing rule already ruled and shipped in
one of them.

There is a fourth witness, and it is the sharpest. `std/src/lib.vl` — the
file that makes `std::print` and `std::panic` reachable by those short
names — carries this comment:

```
// The prelude is universal (core) — every entry is `std::print`/`std::panic`/…,
// reachable on any target. Platform I/O (`scan`) lives in `std::process` (Node)
// and is imported explicitly, so it is gated when building for the browser.
```

A curated, hand-picked, platform-neutral set of names already exists,
already calls itself the prelude, and already applies the exact
admission test §5 will need — universal only, nothing platform-colored.
The only thing it does not do is make its names ambient. Its members are
`Default`, `assert`, `panic`, `print`, the numeric primitives, and `str`.

### 1.1 The case, in one probe

The strongest argument for the feature is not the line count. It is this:

```vilan
fun main(): i32 {
	let list = [10, 20, 30];
	let found = list.get(1);
	match found {
		Some(let n) => 0,
		None => 0,
	}
}
```

```
Error: cannot find 'Some' in this scope
Error: cannot find 'None' in this scope
```

The language handed the user an `Option` — `Option<T>` is a **lang item**
(appendix §A.4: "`?.` results, view-returning lookups"), produced by a
construct the user wrote without naming a type — and then refused to let
them take it apart, because they had not imported names they never wrote.
`?.` has the same shape. A language that can *manufacture* a value at a
use site should be able to *name* it at that use site.

Worse: in exactly this case the compiler's own import steer goes silent.
On a bare `Some(1)` the diagnostic reads `` cannot find 'Some' in this
scope; import it first (`import std::option::Some;`) ``. Route the `Option`
through `list.get(…)` and the steer disappears, leaving the bare "cannot
find" with no remedy offered. (Reproduced five ways in §11.6.5; the trigger
isolates to calling a `List` method that returns `Option` — a list
literal alone, or importing `std::iterator`/`std::map`/`std::result`,
all keep the steer. The mechanism is the ambiguity filter in
`build_std_indexes_if_needed` (analyzer.rs:28247), which drops any name
more than one module scope binds; **why the `.get()` path trips it and
the others do not is unconfirmed and is a defect worth its own filing** —
see §14 Q8.)

## 2. The census — method

The census is mechanical and reproducible. It counts **imported std
names**, not import statements, because the prelude's unit of decision is
a name.

**Corpora** (all read-only, all at the shas above):

| Corpus | Root | Unit | Units | With ≥1 std import |
|---|---|---|---:|---:|
| std | `vilan/vilan/std/src` | `.vl` file | 59 | 45 |
| test | `vilan/vilan/test` | `.vl` file | 121 | 121 |
| examples | `vilan/vilan/examples` | `.vl` file | 28 | 22 |
| docs | `vilan/vilan/docs` | ` ```vilan ` fence | 186 | 185 |
| kolt | `kolt/src` | `.vl` file | 9 | 9 |
| website | `vilan-website/src` | `.vl` file | 11 | 11 |

A docs **fence** is the unit, not the file: a fenced example is a
standalone program-shaped thing, and counting files would hide that one
page shows a dozen. Fences in `examples/*.md` contribute nothing (two
fences, no imports).

**Parsing.** Every `import …;` statement is joined across lines and
expanded through nested brace groups, so
`import std::{ print, option::Option::{ self, Some, None } };` yields
four names, not one. Each yielded name is tagged by the form it arrived
in — **path** (`import std::reactive::Signal;`), **braced**
(`import std::asset::{ bundle, bundle_as };`), or **braced-self**
(`Option::{ self, … }`, which binds the container). Inside `std/src`,
`pkg::` **is** `std` and is counted as such; everywhere else `pkg::` is
the local package and is excluded. `macro_std::` and test-fixture roots
(`common::`) are excluded. A name is counted **once per unit**, so the
tables are "how many files/fences would stop needing this import", not
raw occurrences.

**Totals.** 1,051 import statements across the estate, of which **955
are std imports** (91%). They bring in **264 distinct std names**. 97 of
those 264 are imported in exactly one place; 31 in ten or more. It is a
steep long-tail distribution, which is the precondition for a prelude
being worth anything at all.

## 3. The census — results

### 3.1 The whole estate, top 26 of 264

| Name | std | test | examples | kolt | website | docs | **total** | home |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| `print` | 1 | 121 | 10 | 3 | 2 | 148 | **285** | `std::print` |
| `Option` | 36 | 30 | 5 | 2 | 3 | 29 | **105** | `std::option::Option` |
| `None` | 31 | 29 | 5 | 2 | 3 | 31 | **101** | `std::option::Option::None` |
| `Some` | 30 | 30 | 5 | 2 | 3 | 31 | **101** | `std::option::Option::Some` |
| `Signal` | 4 | 8 | 10 | 4 | 7 | 28 | **61** | `std::reactive::Signal` |
| `Err` | 10 | 9 | 6 | 2 | 0 | 12 | **39** | `std::result::Result::Err` |
| `Ok` | 10 | 9 | 6 | 2 | 0 | 12 | **39** | `std::result::Result::Ok` |
| `Result` | 10 | 9 | 5 | 2 | 0 | 10 | **36** | `std::result::Result` |
| `View` | 2 | 2 | 6 | 0 | 7 | 19 | **36** | `std::ui::View` |
| `view` | 1 | 2 | 6 | 1 | 7 | 19 | **36** | `std::ui::view` |
| `Shared` | 9 | 2 | 2 | 0 | 2 | 10 | **25** | `std::shared::Shared` |
| `Display` | 1 | 8 | 3 | 1 | 7 | 4 | **24** | *two homes — see §3.4* |
| `mount_root` | 0 | 0 | 5 | 1 | 2 | 16 | **24** | `std::ui::mount_root` |
| `Response` | 1 | 0 | 5 | 1 | 1 | 13 | **21** | `std::http::Response` |
| `Server` | 0 | 0 | 4 | 1 | 1 | 15 | **21** | `std::http::Server` |
| `style` | 0 | 4 | 3 | 1 | 7 | 6 | **21** | `std::style::style` |
| `Color` | 0 | 3 | 3 | 1 | 5 | 7 | **19** | `std::style::Color` |
| `space` | 0 | 3 | 3 | 0 | 7 | 6 | **19** | `std::style::space` |
| `Length` | 0 | 3 | 2 | 2 | 7 | 4 | **18** | `std::style::Length` |
| `Style` | 2 | 4 | 3 | 1 | 0 | 6 | **16** | `std::style::Style` |
| `Bytes` | 12 | 1 | 0 | 0 | 1 | 1 | **15** | `std::bytes::Bytes` |
| `json_codec` | 0 | 1 | 6 | 3 | 0 | 4 | **14** | `std::json::json_codec` |
| `Drop` | 3 | 3 | 0 | 0 | 0 | 7 | **13** | `std::drop::Drop` |
| `require_build` | 0 | 0 | 4 | 1 | 1 | 7 | **13** | `std::build::require_build` |
| `PartialEq` | 9 | 3 | 0 | 0 | 0 | 0 | **12** | `std::compare::PartialEq` |
| `Range` | 4 | 2 | 1 | 2 | 0 | 2 | **11** | `std::range::Range` |

There is a **cliff, and then a shelf**. `print` (285) stands alone; the
`Option` trio (105/101/101) is the second tier; `Signal` (61) is a tier
of one; the `Result` trio (39/39/36) is the fourth. Below 36 the
distribution flattens into a shelf of domain names — nothing between
`Result` at 36 and `Range` at 11 gains more than 6 over its neighbour.

The B156 hypothesis — `print`, `Option` + variants, `Result` + variants —
**is confirmed by the data**: those seven names are ranks 1–4 and 6–8, and
the only interloper is `Signal`.

### 3.2 The census embarrasses the hypothesis in one place

Rank the same data over **application code only** — the 42 files in
`examples`, `kolt` and `website` that actually build things:

| Rank | Name | app units (of 42) | examples | kolt | website |
|---:|---|---:|---:|---:|---:|
| 1 | `Signal` | 21 | 10 | 4 | 7 |
| 2 | `print` | 15 | 10 | 3 | 2 |
| 3 | `view` | 14 | 6 | 1 | 7 |
| 4 | `View` | 13 | 6 | 0 | 7 |
| 5= | `Display` | 11 | 3 | 1 | 7 |
| 5= | `Length` | 11 | 2 | 2 | 7 |
| 5= | `style` | 11 | 3 | 1 | 7 |
| 8= | `Option`/`Some`/`None` | 10 | 5 | 2 | 3 |
| 8= | `space` | 10 | 3 | 0 | 7 |
| 11 | `Color` | 9 | 3 | 1 | 5 |
| 12 | `json_codec` | 9 | 6 | 3 | 0 |
| 13= | `AlignItems`, `FlexDirection` | 8 | 2 | 1 | 5 |
| 15 | `Err` | 8 | 6 | 2 | 0 |

**`print` is not the most-imported name in real vilan code — `Signal`
is.** `print`'s 285 is largely a corpus artifact: 269 of them are tests
and doc fences, where printing *is* the program's observable. And **nine
of the top sixteen application names are the style/UI cluster**
(`view`, `View`, `Display`, `Length`, `style`, `space`, `Color`,
`AlignItems`, `FlexDirection`).

This is the census's real lesson, and §5 and §6 both turn on it: **no
single fixed std prelude serves both corpora.** A prelude sized for the
test/docs corpus is `print`-shaped; a prelude sized for applications is
`Signal`- and `style`-shaped. That is an argument *for* the manifest key
being a genuine feature rather than an escape hatch — and an argument for
keeping the *default* set to names that are language-level rather than
domain-level, since the domain sets disagree with each other.

### 3.3 What a prelude actually deletes

Whole import **statements** removed, by candidate set (a statement counts
only if *every* name it binds is in the set):

| Set | stmts deleted | of 955 | units left with no import at all |
|---|---:|---:|---|
| **A** — `print`, `Option`/`Some`/`None`, `Result`/`Ok`/`Err` | **419** | **44%** | test 62/121, docs 60/185, apps 0/42 |
| **B** — A + `Signal` | 458 | 48% | test 64/121, docs 64/185, apps 0/42 |
| **C** — B + `Shared` | 483 | 51% | test 66/121, docs 66/185, apps 0/42 |
| **D** — `print` alone | 274 | 29% | test 47/121, docs 48/185, apps 0/42 |

Two honest readings. First, the marginal return falls off a cliff:
`print` alone buys 29%, the core seven buy 44%, and every further name
buys three or four points. Second, **the core seven clear the import
block entirely from 62 of 121 test files and 60 of 185 doc fences, and
from zero of 42 application files.** An application always imports more
than a prelude can reasonably carry; its win is line-level, not
block-level. That asymmetry is worth stating plainly to the owner,
because "no more import boilerplate" is true of the corpus and the docs
and false of kolt.

### 3.4 One name the census found colliding — and the ruling that dissolved it

`Display` ranks 12th overall and 5th in applications — and it is **two
different std names**: `std::display::Display` (the `to_string`/`format`
trait, 9 units) and `std::style::Display` (the CSS `display` property
enum, 14 units). They live in the base layer together and cannot both be
ambient. The paper as first proposed concluded that any prelude containing
`Display` must first rename one of them, and put the rename to the owner
as §14 Q2.

**The ruling dissolved the question instead of answering it.** The web
prelude carries **the module `style`, not its members** (§5.2, §5.3).
Under that shape the two names never contend:

| Spelling | Means | How it is in scope |
|---|---|---|
| `Display` | `std::display::Display`, the `to_string`/`format` trait | admissible bare — the collision is gone |
| `style::Display` | `std::style::Display`, the CSS `display` enum | through the ambient **module** `style` |

Three consequences, each a determination (§13.4a–c):

- **The CSS enum never renames.** `std::style::Display` keeps its name,
  which is the right name for the CSS property it models, and no estate
  file, doc fence or golden moves.
- **`Display` the trait becomes ADMISSIBLE bare.** It is not admitted here
  — it still has to clear §5.1's four-part test on its own merits, and it
  does not (9 units outside style's 14, below `Result` at 36). But the
  disqualifier is gone, so the door is open for a later census. The
  `.to_string()` tax (§5's closing note) is now a frequency question, not
  an ambiguity one.
- **The lesson generalises.** An ambient *module* costs one name and buys
  a whole namespace, and it buys it **without ever contending with a bare
  member name of the same spelling**. That is why §5.2 promotes ambient
  modules to a first-class concept rather than treating `style` as a
  special case.

## 4. The census — the breaking half

For every candidate name, does any estate file **declare** it, such that
an ambient binding would collide? Scanned: file-scope declarations (`fun`
/`struct`/`enum`/`trait`/`let`/`type`/`const`, with or without `export`),
`use` re-bindings, and nested (block-scope) `let`/`fun`.

**File-scope declarations of a candidate name — 19 total, 17 of them in
std declaring its own name at its definition site.** The two that are not:

| File | Declaration | Collides with |
|---|---|---|
| `vilan/test/match-patterns.vl:6` | `enum Signal { Quit, Finished }` | `std::reactive::Signal` |
| `vilan/test/default.vl:3` | `trait Default { … }` | `std::default::Default` |

**`use` re-bindings — 4, all inside std**: `use Option::{ None, Some };`
in `option.vl` and `use Result::{ Err, Ok };` in `result.vl`, at the
enums' own definition sites.

**Nested (block-scope) shadows — 3**, all of them legal today and legal
under the rule §9 sets:

| File | Binding | Shadows |
|---|---|---|
| `vilan/test/fixed-arrays.vl:38` (and one sibling) | `let view = &mut buf[2];` | `std::ui::view` |
| `vilan-website/src/playground.vl:296` | `let format = \|\| { … };` | `std::display::format` |

**The headline: for the base set of §5.1, the collision count outside std
is ZERO.** Not one estate file declares `print`, `Option`, `Some`, `None`,
`Result`, `Ok` or `Err`. Re-verified mechanically at `vilan` @ `093bf567`
for the amendment: the file-scope scan over `vilan/` outside `std/` returns
empty for all seven, and the block-scope scan returns empty too. The two
real collisions (`Signal`, `Default`) are both against names the base set
does not include, and both would be resolved silently and correctly by the
shadowing rule of §9 — but only if that rule is implemented the way §9.2
insists, which is the one place this feature can genuinely break code.

### 4.1 The web set's collision census

The web set (§5.3) adds five ambient names — two modules and three
members. Scanned the same way, at `093bf567`:

| Ambient name | Kind | File-scope declarations outside std | Verdict |
|---|---|---:|---|
| `Signal` | member | 1 — `vilan/test/match-patterns.vl:6` `enum Signal { Quit, Finished }` | shadowed correctly by §9.1; and that file's package takes the **base** prelude, so `Signal` is never ambient there in the first place |
| `view` | member | 0 file-scope; 2 block-scope (`vilan/test/fixed-arrays.vl:38` and one sibling, `let view = &mut buf[2];`) | shadowed correctly by §9.1; base-prelude packages again |
| `View` | member | 0 | clean |
| `style` | **module** | 0 | clean |
| `ui` | **module** | 0 | clean |

Two notes the ambient-module concept forces, both of which the census
makes concrete:

- **`std::style::style` is a function inside the module `style`** (`fun
  style(): Style`, `std/src/style.vl:623`), and the estate calls it bare
  60 times in `vilan/` alone. Every one of those files carries `import
  std::style::style;` — an **explicit import**, which under §9.1 beats the
  ambient module binding. So bare `style()` keeps working everywhere it
  works today, and the ambient module only surfaces in files that did not
  import the function. This is the first real demonstration that ambient
  modules need no precedence rule of their own: §9.1's single ladder
  already ranks them.

  **The other half of that, found in the build and recorded here because
  the ruling did not foresee it:** a name has ONE binding, so a file that
  imports the *function* `style` no longer reaches the *module* `style` —
  `style::Display` stops resolving **in that file**. The compiler says so
  plainly (`` cannot resolve `Display` here: fn style(): Style is not a
  module ``) and the estate pays nothing, because all 60 call sites import
  the enums they use explicitly and none of them writes `style::…`. But it
  is a real property of ambient modules and a user will meet it: within one
  file you take the module or the member, not both. It is the ordinary
  shadowing rule rather than anything the prelude adds, and the recovery is
  the ordinary one — drop the member import and write `style::style()`, or
  import the enums you need. Pinned as
  `shadowing_an_ambient_module_costs_that_files_qualified_spelling`.
- **`mount_root` is browser-only inside a layered module.**
  `std/src/browser/ui.vl:731` declares it; `std/src/process/ui.vl` does
  not. The module `ui` resolves on both platforms (both layers declare
  it), so an ambient `ui` is platform-safe; `ui::mount_root` on a node
  build reports at the use site, which is exactly what the
  platform-coloring model is for (§4.3 of the spec). An ambient bare
  `mount_root` would have moved that error's cause off-screen. This is
  the mechanism §5.3 uses to admit the module and refuse the member.

The website's `let format = || { … }` is the near-miss worth keeping in
view: a real application, a real closure, a name that a slightly larger
prelude would have made ambient. It is exactly why the prelude must be
the weakest scope and not merely a low-priority import.

## 5. The two std preludes

**Ruled: std ships TWO preludes.** The census's sharpest finding (§3.2) is
that `print` is not the most-imported name in real vilan code — `Signal`
is — and that nine of the top sixteen application names are the style/UI
cluster. The paper as first proposed recorded that as a tension and
resolved it by shrinking the default to language-level names, pointing
applications at a custom prelude. The ruling resolves it the other way:
**std supplies both sets, and the manifest key picks one.**

That is the better answer for a reason the paper's own §3.3 table shows.
The base set clears the import block entirely from 62 of 121 test files
and 60 of 185 doc fences — and from **zero of 42 application files**. A
prelude that never empties an application's import block is a prelude that
does not serve the corpus vilan is actually for. The web set is what
serves it, and it can be domain-shaped precisely *because* it is not the
default: nothing is imposed on a CLI tool or a compiler plugin.

| | base | web |
|---|---|---|
| Selected by | omitting the key (or `prelude = "std::prelude"`) | `prelude = "std::web"` |
| Ambient members | `print`, `Option`, `Some`, `None`, `Result`, `Ok`, `Err` | the base seven **+** `Signal`, `view`, `View` |
| Ambient modules | — | `style`, `ui` |
| Admission test | §5.1 — universal, language-level, unambiguous, top-of-census in more than one corpus | §5.3 — the base test with (b) read as *web*-domain-level, plus a per-file-friction test |
| Collisions outside std | 0 | 1 member (`Signal`), shadowed correctly; 0 modules |

### 5.1 The base set

**The base std prelude is these seven names:**

```
print
Option, Some, None
Result, Ok, Err
```

Each is admitted by a rule, not by rank alone. The admission test the
data supports, and which `std/src/lib.vl` already applies informally:

> **A name belongs in the default prelude if it is (a) universal — in
> std's base layer, reachable on every target; (b) language-level rather
> than domain-level — the language itself can produce it, or every
> program regardless of domain uses it; (c) unambiguous — exactly one std
> definition claims the name; and (d) at the top of the census in more
> than one corpus.**

- **`print`** — rank 1 overall (285), rank 2 in applications, present in
  every corpus. Universal (`std::io`, re-exported at `std::print`; the
  Node-only `scan` deliberately is not). It is the one name a program
  needs before it can be observed at all, which is why it dominates the
  teaching corpora. (b) is carried by ubiquity rather than by language
  production.
- **`Option`, `Some`, `None`** — ranks 2–4 (105/101/101), and the only
  names in the census that (b) admits on the strongest possible ground:
  `Option<T>` is a **lang item** (§A.4), produced by `?.` and by
  view-returning lookups. §1.1's probe is the argument. Universal,
  unambiguous, rank 1 in std, ranks 2–4 in `test` and in the docs, and
  present in all six corpora — the only candidate besides `print` that is.
- **`Result`, `Ok`, `Err`** — ranks 6–8 (39/39/36). Universal,
  unambiguous, present in five of six corpora. Admitted under (b) as the
  co-star of the `!` operator: `Try`/`Verdict`/`Lift` are lang items and
  `Result` is the type the language's own error-propagation form is
  taught and written in. Weaker than `Option`'s claim — nothing in the
  language *manufactures* a `Result` — but it is unarguable that `Option`
  and `Result` travel together, and splitting them would leave the `!`
  operator's canonical type an import away while `?.`'s is not.

Seven names, 419 of 955 std import statements (44%), zero collisions
outside std.

**Rejected from the base set:**

- **Platform-colored names** (`Server`, `Response`, `fs`, `storage`,
  `router`, `db`, …) — refused categorically, from **both** sets. A name
  whose module lives in a `[library.layer.…]` overlay and is declared by
  only *one* layer cannot be ambient without making a browser build's
  ambient scope differ from a node build's, and the platform-coloring
  model reports reachability errors *at the use site* (§4.3 of the spec)
  — an ambient name would move the error's cause off-screen. §5.3 shows
  the one shape that survives this: a module BOTH layers declare.
- **`Shared` (25)** — 9 of its 25 are std's own files and 10 more are doc
  fences, leaving **6 units of real non-std code** in the whole estate.
  Fails (d) in both corpora.
- **`Map`, `Set`, `Range` (10, 6, 11)** — the plausible "inherent-ish"
  candidates B156 asked about. All three fail (d) outright: `Range` is 11
  units, `Map` 10, `Set` 6, against `Result`'s 36. `List` is already
  ambient (§4.7) and is the reason these look like they belong; the data
  says they do not. Reconsider if a future census moves them.
- **`format` / `panic` / `assert` / `Default`** — `format` is 7 units and
  has the website's block-scope collision. `panic` (10 units, 9 of them
  std's own), `Default` (4 units, all four std's own) and `assert` (1
  unit, in `examples`) are barely imported outside std at all. All four
  are in `std/src/lib.vl`'s short-name set — which is a different thing
  from being ambient, and which §10.2 now deletes outright.
- **`Display`** — no longer rejected for *ambiguity* (§3.4 dissolved
  that), but still short of (d): 9 units for the trait, against
  `Result`'s 36. See the note below.
- **`Signal` and the style/UI cluster** — not rejected. **Moved to the
  web set** (§5.3), which is what the ruling created it for.

**A note on `Display` and the trait-method tax.** `.to_string()` on an
`i32` fails today with `i32 has no method 'to_string'; import
std::display::Display to use it` — a whole class of import that exists
only to unlock methods, and one a prelude *could* abolish (§11.6.1 confirms
a re-exported trait carries its methods through). It was left out of the
first draft because the name was ambiguous; §3.4's dissolution removes
that objection and leaves only frequency, which it does not yet clear.
Recorded as the live candidate for the next census (§14 Q9).

### 5.2 Ambient module names — a first-class concept

**Determination: a prelude may make a MODULE name ambient, beside member
names. `style::Display` with no import is as much a prelude effect as
bare `Some` is.**

This is the ruling's structural contribution, and it is worth stating as
a concept rather than as a fact about `style`, because it changes what a
prelude can be sized to carry.

**What it buys.** A member entry costs one ambient name and buys one
name. A **module** entry costs one ambient name and buys a whole
namespace — every present member and every future one — at the price of
one qualifying segment at each use site. For a cluster like
`std::style`'s sixteen enums, that is sixteen-for-one.

**Why it cannot collide.** A qualified use (`style::Display`) and a bare
use (`Display`) are different syntax reaching different resolutions.
Making the module `style` ambient therefore does not put `Display`,
`Color`, `Length` or `space` into the bare namespace at all — which is
precisely how §3.4's collision dissolves rather than being adjudicated.
The general rule: **an ambient module contributes exactly one name to the
bare namespace — its own.**

**Why it needs no new precedence rule.** §9.1's ladder already ranks
every binding; a module binding is a binding. The estate proves the case
that matters: `std::style::style` is a *function* whose name equals its
module's, and 60 call sites in `vilan/` write it bare. Each of those
files carries `import std::style::style;`, which is an explicit import
and therefore beats the ambient module. Bare `style()` keeps working;
files that did *not* import it see the module instead. One ladder, no
special case, zero breakage — verified in §4.1.

**The admission test for a module.** A module is admissible when it is
(a) **reachable on every platform the set targets** — either base-layer,
or declared by *every* layer (`std::ui` is declared by both
`browser/ui.vl` and `process/ui.vl`, so it qualifies; `std::fs`, declared
only by `process`, does not); (b) **a namespace a program in the set's
domain reaches into repeatedly**, so the qualifier earns its keep; and
(c) unambiguous as a bare name, like any member.

**What it does not change.** Platform coloring still reports at the use
site. `ui::mount_root` on a node build is an error *at the call*, which
is where it belongs and where it reads. An ambient module never suppresses
that check — it only spares the import line.

**Selection is uniform.** A prelude module publishes an ambient module by
re-exporting it (`export import pkg::style;`), exactly as it publishes an
ambient member (`export import pkg::reactive::Signal;`). §8's "one
mechanism" holds: there is no second syntax and no second list.

### 5.3 The web set

**Determination — the web prelude is the base seven plus five names:
three members and two modules.**

```
                       print, Option, Some, None, Result, Ok, Err   (the base seven)
members                Signal, view, View
modules                style, ui
```

Admitted against §5.1's test with (b) read as *web*-domain-level, plus
one further test the ruling's "the prelude is a floor, not a ceiling"
forces: **(e) the name is written in many of a web app's files, not once
per app.** A prelude removes per-file friction; a name written once has
none to remove.

| Name | Kind | App units (of 42) | Admitted because |
|---|---|---:|---|
| `Signal` | member | **21** (rank 1) | Base-layer, so SSR reaches it; unambiguous; the single most-imported name in real application code — ahead of `print` at 15. Ruled in by the owner. |
| `view` | member | 14 (rank 3) | `std::ui`, declared by both layers. The builder every view-producing file calls, densely — a view tree is many `view("div")` calls, and `ui::view` at each would be noise the module entry cannot justify. |
| `View` | member | 13 (rank 4) | The type half of the same idea; admitting one without the other splits a pair that always travels together (every `fun card(): View` needs it). |
| `style` | **module** | 11 for the function, and 11 + 11 + 10 + 9 + 8 + 8 beneath it for `Display`/`Length`/`space`/`Color`/`AlignItems`/`FlexDirection` | Ruled in. Base-layer, one ambient name for a sixteen-name namespace, and the move that dissolves §3.4. |
| `ui` | **module** | — (see below) | Declared by *both* layers, so platform-safe. Carries `mount_root` and the rest of the UI surface at `ui::…` without putting a once-per-app name into the bare namespace. |

**Rejected from the web set, with the reason:**

- **`mount_root` (8 app units)** — fails (e) decisively: a web app calls
  it **once**, in its entry file. It is also browser-only inside a
  layered module (`std/src/browser/ui.vl:731`; `process/ui.vl` has no
  such declaration), so bare ambience would move a platform error's cause
  off-screen. Reachable as `ui::mount_root`, which is the ambient-module
  concept doing exactly the job §5.2 describes.
- **`json_codec` (9 app units)** — the closest call, and it fails on
  where its uses are: 6 in `examples` and 3 in kolt, and **zero in the
  website** — the only genuine web application in the corpus. It is an
  RPC-and-examples name, not a web-app name, and it is a plain function
  in `std::json` that a program touches at its serialization boundary,
  not throughout. Reachable in one line.
- **The rest of the style cluster** (`Length`, `space`, `Color`,
  `AlignItems`, `FlexDirection`, `Style`, `Overflow`, `Cursor`,
  `Position`, `JustifyContent`, `UserSelect`, `TextAlign`, `WhiteSpace`)
  — all reached through `style::`. Putting them in the bare namespace
  would be thirteen names for what one already buys, and would re-open
  §3.4.
- **`Shared`, `Range`, `Map`, `Set`** — fail (d) in the application
  corpus as they do in the whole one.
- **`Server`, `Response`, `fs`, `router`, `storage`, `db`** — one-layer
  names; refused by §5.1's categorical rule, which the web set does not
  relax.

**What the web set costs.** One real collision in the whole estate —
`vilan/test/match-patterns.vl`'s `enum Signal` — and that file's package
takes the base prelude, so the name is never ambient there. Under §9.1 it
would resolve to the local `enum` even if it were. §4.1 is the census.

**What the web set buys.** The website's eleven files import `Signal` in
7, `view`/`View` in 7, and the style cluster in 7; kolt's nine import
`Signal` in 4 and the cluster in 2. This is the first candidate set in
the paper that would empty import blocks in **application** files, which
§3.3 showed the base seven never do.

## 6. The manifest spelling, and why this key belongs in toml

### 6.1 The charter argument

The 035/027 ruling is that manifests carry **pre-compiler facts only** —
anything the compiler can learn by reading code belongs in code. The
prelude passes that test on the strictest reading available, and it is
worth stating why precisely, because most "just put it in the manifest"
requests do not:

**The ambient scope must be known before the first file resolves, and it
governs the file that would otherwise declare it.** A `prelude` declared
in vilan source would have to be resolved by a resolver that does not yet
know what is in scope — including in the prelude module itself, and
including in whichever file carried the declaration. That is not a
layering preference; it is a bootstrapping hole. Compare the keys already
in `[package]`: `root`, `entry`, `target` and `default-entry` are all
facts the build must know **to find and interpret the source at all**.
`prelude` is the same kind of fact: it is what the source *means*, fixed
before the source is read.

The counter-argument, recorded because it is the honest one: a
`prelude` key is unlike `root`/`entry`/`target` in that it changes the
**semantics** of every file rather than the **selection** of files. That
is real, and it is the reason §7's scoping rule is not optional — a
semantic key that a dependency could impose on its consumer, or a
consumer on its dependency, would be indefensible. Confined to one
package's own files, it is the same shape as `target`: a per-package fact
that the package's own author states once.

### 6.2 The spelling

**Recommended, as amended by the ruling:**

```toml
[package]
prelude = "std::prelude"            # the default; may be omitted entirely
prelude = "std::web"                # the web set
prelude = "pkg::my_prelude"         # a module in this package
prelude = false                     # no prelude at all
```

and the identical key on `[library]`:

```toml
[library]
name = "std"
prelude = false
```

Determinations behind that spelling:

1. **The key is `prelude`, in `[package]` and in `[library]`.** B156's
   provisional `[package] prelude` is **incomplete**: std is not a
   `[package]`. `vilan/vilan/std/vilan.toml` opens `[library]\nname = "std"`,
   and `manifest.rs` carries `Package` and `Library` as separate structs.
   A key that exists only on `[package]` could not state std's own
   posture (§10) and could not let any library — the whole D5 registry
   story — declare one. Same key, same values, both sections. The
   implementation template is `generated`, the one key already validated
   by a single free helper called from both `validate_package` and
   `validate_library`.
2. **The value is a MODULE PATH or `false`, and there is no third
   grammar.** This is the amendment's determination and it replaces the
   first draft's `"std"`-names-the-default rule. Every accepted string is
   a module path in the grammar `import` already takes; the two std
   preludes are simply two std modules:

   | Value | Means |
   |---|---|
   | *(omitted)* | `"std::prelude"` |
   | `"std::prelude"` | the base seven (§5.1) |
   | `"std::web"` | the web set (§5.3) |
   | `"pkg::…"`, `"<dep>::…"`, any `"std::…"` module | that module's exports |
   | `false` | no prelude |

   The ambient names are, in **every** case, exactly the named module's
   exports (§8). Selecting the web set is not a mode the compiler knows
   about — it is a module path like any other, and `std::web` is a real
   file in std whose contents a reader can open. That is the property
   worth paying for: **the two std preludes are written in vilan, in std,
   in the same mechanism a user's custom prelude uses.** There is no
   built-in list in Rust to drift out of sync with the docs.
3. **Omitting the key means `"std::prelude"`.** The feature's whole point
   is that the common case is silent. A package that says nothing gets
   the base set; the manifest gains a line only when the answer is
   unusual. This makes the key **additive to every existing manifest in
   the estate** with no edit.
4. **`prelude = "std"` is REFUSED, with a curated diagnostic.** The first
   draft made it a legal synonym for the default. The alias sweep (§10.2)
   is what changes the answer: after it, `std`'s root module exports
   nothing, so `prelude = "std"` would silently mean *an empty prelude* —
   a trap that looks like the most obvious spelling in the language.
   Refuse it and name the fix:

   ```
   invalid `[package] prelude`: `std` is the package root, not a prelude
   module; use `"std::prelude"` (the default set) or `"std::web"`
   ```

   This is the same posture the reserved-package-name refusal takes: the
   obvious wrong guess is caught by name and redirected, rather than
   accepted into a silent misbehaviour.
5. **It is not inherited from a `[project]` workspace root.** A workspace
   root's `[project]` section carries `packages` and shared
   `dependencies`; a semantic key must not travel that edge either, for
   the reason §7 gives. Each member states its own. (Owner question
   §14 Q3 — this is the one place a convenience argument exists.)
6. **`false`, not `"none"` or `""`.** TOML has a boolean; the value is a
   yes/no about a whole mechanism. `split` in `[package]`/`[entry.…]` set
   the precedent for a bare bool. `prelude = true` is **refused** — the
   affirmative is spelled by omitting the key or naming a module, and an
   untagged string-or-bool deserialize accepts `true` syntactically, so
   the refusal has to be explicit (the precedent is
   `project_false_is_an_error_rather_than_a_no_op`).
7. **The key is validated at manifest load**, lexically: `false`, or a
   path whose every segment is an identifier and whose root is `pkg`,
   `std`, or a key declared in this section's `dependencies` table. The
   path's *resolution* — does that module exist, does it export anything
   — is diagnosed at build time. Manifest diagnostics in this compiler
   carry no span (they render at offset 0 of `vilan.toml`, a decision
   recorded in the LSP), so each refusal names its own key spelling in
   its text, as `[package] target` and `[package] generated` do.
8. **The key is part of the editor surface.** `manifest_completion.rs`'s
   `TABLES` listing and `editors/vscode/schemas/vilan-toml.schema.json`
   both enumerate `[package]`/`[library]` keys under
   `additionalProperties: false`, and `schema_and_listing_agree` fails
   until a new key is in both. The prelude key is not done until it
   completes in the editor.

## 7. Scoping: per package, never inherited

**Determination: a file resolves under the prelude declared by the
manifest of the package that owns the file. Nothing else.**

Consequences, each deliberate:

- A **dependency's** files resolve under the dependency's own prelude. A
  consumer cannot change what a dependency's source means, and a
  dependency cannot inject names into its consumer.
- A **workspace member** resolves under its own `[package] prelude`, not
  the root's (see §6.2 determination 5, and §14 Q3).
- A **library layer** (`[library.layer.<name>]`) resolves under the
  library's one prelude; layers select source, they do not re-scope it.
  A per-layer prelude would let the same module name mean different
  things per platform, which is the one thing platform layering is
  careful never to do.
- **std's own files** resolve under std's declared prelude (§10).
- A **custom prelude module's own file** resolves under its package's
  prelude like any other file — which is to say, under itself. That is
  not circular in practice, because the prelude's contribution to a file
  is a set of *bindings*, resolved after the module graph is loaded; but
  it must be stated, and the implementation must not recurse. The safe
  rule: **the prelude module's own file gets no prelude.** (§14 Q4.)

The composability argument is short and decisive: two packages that
disagree about what `Signal` means must both keep compiling, in the same
build, forever. Anything other than per-package scoping breaks that the
first day two dependencies disagree, and there is no version of "the
consumer wins" that is not a supply-chain hazard.

## 8. Override replaces; extend by re-export

**Determination: `prelude = "pkg::my_prelude"` REPLACES the std prelude
entirely. The ambient names are exactly that module's exports. Extending
the std set is spelled by re-exporting std's names from the custom
module.**

One mechanism, no merge rules, no precedence table between a default set
and an added set, and no way for a later std release to silently collide
with a name a package added. The cost is one line per inherited name in
the custom module, paid once.

**The shipped `export` suffices — probed, and it does more than needed.**
§11.6.1 records the probe in full. A user module containing:

```vilan
export import std::display::Display;
export import std::print;
export import std::option::Option::{ self, Some, None };
export import std::result::Result::{ self, Ok, Err };

export fun shout(message: str): void { print(message); }
```

re-exports all of it — the plain function `print`, the *types*
`Option`/`Result` via `self`, the **enum variants** `Some`/`None`/`Ok`/`Err`,
a **trait** whose methods (`.to_string()`) then work at the consumer, and
its own local `shout` — and a consumer importing those leaf names from
that module compiles and runs. No new syntax is needed for the mechanism
this determination rests on.

Two seams the implementation must respect, both already visible:

- `formatter.rs` `prune_import_branch` never prunes `Node::Export(_)`
  ("surface, not usage"). A custom prelude module is nothing but
  re-exports whose names it never uses, so Organize Imports must leave it
  alone — and does, already, by that existing rule.
- A prelude module that re-exports a *platform-layered* name
  (`std::ui::view`) makes its package's ambient scope platform-dependent.
  The prelude does not need a new rule for this: platform coloring
  already reports at the point code becomes reachable. But the docs must
  say it, because "my prelude broke my server build" is otherwise a
  mystifying error.

**No globs.** `export import pkg::x::*` does not exist and this proposal
does not ask for it; a prelude whose contents change when its source
module gains a name is a prelude nobody can read.

## 9. Shadowing: the prelude is the weakest scope

### 9.1 The rule

**Determination: the prelude is the weakest binding in the language. In
order of increasing precedence: prelude → module items and explicit
imports → enclosing scopes → the innermost local binding. A local
declaration or an explicit import of a prelude name wins, silently, with
no diagnostic.**

This is the UA-stylesheet posture, and it is what §4.7's existing prelude
already does for `List` and the primitives. It is also the rule
`macros.rs` already states for macros — "same-file definitions shadow
imported ones, which shadow the std prelude — the ordinary name-resolution
order" — so this determination adds no new concept to the language, only
a fourth namespace to an existing sentence.

Silently, not with a warning: a warning on shadowing a prelude name is a
warning on writing `fun print` in your own file, which is the user's
business, and the census (§4) says it happens twice in the whole estate.

**The escape hatch, and its absence.** A shadowed prelude name has **no
qualified spelling at the use site**: `std::print(x)` inline is refused —
"`std` is a namespace, not a value; import the module first
(`import std::…;`) and qualify through its name" (§11.6.3). Recovery is
`import std::io;` then `io::print(…)`. That is the existing rule for
every shadowed import and needs no change, but the docs must say it in
the prelude's own section, because the prelude is the first scope a user
will shadow without meaning to.

### 9.2 The implementation mandate — the one way this breaks code

**In the shipped compiler, an explicit import BEATS a same-file
declaration, silently.** Probed (§11.6.2):

```vilan
import std::print;
import std::io;

fun print(message: str): void { io::print("[mine] " + message); }

fun main(): i32 { print("who wins?"); 0 }
```

prints `who wins?` — not `[mine] who wins?`. The file's own `fun print`
is dead. `macros.rs:678` names the mechanism in its own doc comment:
"imports overwrite hoisted function bindings, so the exclusion is how the
prelude yields."

That sentence is the whole risk of this feature. `world_prelude_nodes`
implements the macro-body prelude as **synthesized import nodes spliced
into the AST** (`lib.rs:585`), and therefore has to filter every name the
file defines out of the synthesized text *before* parsing it, because
otherwise the prelude would clobber the file's own declarations.

**Therefore: a value/type prelude MUST NOT be implemented as synthesized
imports at file head.** Implemented naively that way, this feature
silently breaks `test/match-patterns.vl` (its own `enum Signal` replaced
by `std::reactive::Signal`) and `test/default.vl` (its own `trait
Default` replaced by std's) — the exact two collisions §4 found, turned
from non-events into miscompiles. Two acceptable implementations:

1. **Bind at the weakest layer.** The single mutation is
   `resolve_import`'s `scope.name_to_id_map.insert(bind_name, target_id)`
   (analyzer.rs:24959), drained from `prepped_imports` in `resolve_world`.
   Seed the module scope with the prelude's bindings **first**, and let
   real imports and hoisted items overwrite them — an
   `entry(..).or_insert(..)` discipline for the prelude and an unchanged
   `insert` for everything else.
2. **Filter, as macros do.** Exclude from the prelude every name the file
   declares or explicitly imports, then synthesize. Proven to work, but
   it re-derives at every file what option 1 gets from ordering, and it
   has to see the file's imports before it can filter — a second pass the
   macro path can afford and the main path should not have to.

Option 1 is recommended. One further constraint either way:
`resolve_import` calls `record_reference` per path segment, and
`Document::import_leaf_is_used` (document.rs:2388) reads exactly that
reference index to decide whether a leaf is unused. Prelude bindings must
be **invisible to that index**, or Organize Imports will start pruning
real imports because "the prelude already references them."

## 10. std's own posture, and the alias sweep

### 10.1 std compiles with no prelude

**Determination: std compiles with `prelude = false`, stated explicitly
in `vilan/vilan/std/vilan.toml`.**

Three reasons, in order of weight:

1. **std's own resolution stays greppable.** 264 names, 59 files, a
   library whose every symbol is somebody's lang item: "where does this
   name come from" must be answerable by reading the file. std is the one
   codebase in the world where the import block is doing real work.
2. **The bootstrapping order is trivial rather than delicate.** The std
   prelude's members are std definitions; std compiling under them is a
   loop the implementation would have to reason about. `false` deletes
   the question.
3. **It exercises `false`.** The one package guaranteed to be built by
   every user of the language is the one proving the "no prelude" path
   works.

The cost is that std keeps its 169 std-internal import statements and
gains nothing — 46 of them (27%) would otherwise have vanished. That is
the right trade for a base library, and it is what the census's std
column exists to price.

Stated explicitly rather than left to a special case: a reader of
`std/vilan.toml` should see the posture, and the compiler should have no
"std is different" branch it can drift out of sync with.

One consequence of §6.2 determination 2 that must be said out loud: **std
declaring `prelude = false` does not stop std from *containing* the
prelude modules.** `std/src/prelude.vl` and `std/src/web.vl` are ordinary
std modules that std's own files compile without using, exactly as
`std/src/style.vl` is a module std's `io.vl` never imports. The posture is
about resolution, not about contents.

### 10.2 The alias sweep

**Determination: std's alias-only re-exports are DELETED.** Every entry in
`std/src/lib.vl` exists for one reason — to let a caller write
`std::print` instead of `std::io::print` — and that reason is what the
prelude now serves, better. Ruled by the owner on `std::print` by name,
and extended by the same ruling to "a sweep of std for names whose whole
job was import brevity."

**The census. `std/src/lib.vl` is the whole surface** — it is the only
`lib.vl` in std, and `export import` appears nowhere else in the package.
Six statements, thirteen names, and every one of them is an alias for a
name that already has a real home:

| Alias | Real home | Estate uses of the alias | Verdict |
|---|---|---:|---|
| `std::print` | `std::io::print` | **2,278** import statements | **delete** — ruled by name; the base prelude carries `print` |
| `std::panic` | `std::io::panic` | 8 | **delete** — same shape, no other purpose |
| `std::assert` | `std::io::assert` | 4 | **delete** — same shape |
| `std::Default` | `std::default::Default` | **0** | **delete** — dead on arrival; nothing in the estate ever wrote it |
| `std::str` | `std::string::str` | 0 | **delete** — and doubly dead: `str` is a §4.7 primitive, ambient everywhere already |
| `std::BigInt`, `std::f32`, `std::f64`, `std::i8`, `std::i16`, `std::i32`, `std::i53`, `std::u8`, `std::u16`, `std::u32`, `std::u53` | `std::number::…` | 0 | **delete** — the numerics are §4.7 primitives; the aliases spell a name that was never needed |

Two findings the census turns up, both worth recording:

- **Eleven of the thirteen aliases have zero uses in the entire estate.**
  `std::Default`, `std::str` and the ten numerics were never written by
  anyone, in std, the corpus, the docs, the examples, kolt or the
  website. They are pure surface area — the exact shape of thing the
  ruling is aimed at.
- **std does not use its own aliases.** Every `std/src/*.vl` file spells
  its imports `pkg::io::print`, `pkg::default::Default` and so on. So
  "migrate std's own uses" is a null migration: the only std file that
  changes is `lib.vl` itself.

**What `lib.vl` becomes.** Emptied of aliases, `std/src/lib.vl` has no
job left. It is deleted, and the two prelude modules stand in its place
as the curated, named surfaces:

```vilan
// std/src/prelude.vl — the base prelude (§5.1)
export import pkg::io::print;
export import pkg::option::Option::{ self, Some, None };
export import pkg::result::Result::{ self, Ok, Err };
```

```vilan
// std/src/web.vl — the web prelude (§5.3)
export import pkg::io::print;
export import pkg::option::Option::{ self, Some, None };
export import pkg::result::Result::{ self, Ok, Err };
export import pkg::reactive::Signal;
export import pkg::style;                    // the MODULE (§5.2)
export import pkg::ui;                       // the MODULE (§5.2)
export import pkg::ui::{ view, View };
```

Note that `web.vl` re-states the base seven rather than deriving them.
That is §8's determination — **override replaces, extension is spelled by
re-export** — applied to std itself. std does not get a merge rule the
users do not have.

**The breaking posture, stated plainly.** This half of the change is
**breaking**, and it is the only breaking half. Deleting `std::print`
turns 2,278 statements into errors at once. The migration is mechanical
and has two shapes, and the paper prescribes which goes where:

| Surface | Migration | Why |
|---|---|---|
| Rust test fixtures, `vilan/test/*.vl`, `vilan/benchmarks` | rewrite `std::print` → `std::io::print` | A pure textual substitution that preserves every fixture's meaning exactly and cannot depend on the prelude reaching that fixture's package. Redundant under the prelude, but §12 already rules redundant imports harmless, and Organize Imports will strip them on demand. |
| `vilan/docs` fences, `vilan/examples`, `README.md`, the CLI templates | **delete the import** | These are the teaching surfaces. A doc fence that imports what the prelude supplies teaches the wrong thing, and the docs gate compiling every fence is the feature's best end-to-end proof. |

The asymmetry is deliberate: the bulk sweep must be the transformation
that cannot be wrong, and the curated sweep must be the one that shows
the feature.

**Rename diagnostics at the old spellings.** `std::print` will be typed
from muscle memory for a long time, and the generic failure —
`cannot find 'print' in the imported path` — names neither the removal
nor the two ways forward. Each deleted alias gets a curated arm:

```
`std::print` was removed: `print` is in the default prelude (no import
needed), and its module path is `std::io::print`
```

The same arm serves `panic`, `assert` and `Default` with the prelude
clause dropped where it does not apply, and the numerics and `str` with
"is a primitive and always in scope" in its place.

## 11. The tooling half

Four touchpoints, all of which exist today and all of which change.

### 11.1 Organize Imports — mint nothing, and STRIP

**Determination: Organize Imports removes an import the prelude covers.**

The alternatives were: leave them (harmless, but the estate then carries
419 dead statements forever and every new file written by copy-paste
carries more), or strip them. Strip, for three reasons: (a) the action's
existing contract is already "prune the leaves the analyzer reports as
unused", and a prelude-covered import *is* unused in the only sense the
action knows — removing it changes nothing about what the file means;
(b) it gives the migration a mechanical, reviewable, per-file path (§12);
(c) leaving them creates two spellings of the same file with no rule for
which is canonical, which is the thing this action exists to prevent.

The mechanics are already in place and need almost nothing:

- `formatter.rs::organize_import_runs(source, keep)` (line 1232) takes a
  `keep: &dyn Fn(Span) -> bool` predicate and does all the leaf-granular
  work: `{ a, b }` → `{ a }`, a statement pruned to nothing is deleted
  with its line break and trailing comment, a run pruned to nothing is
  deleted whole. **The formatter needs no change at all.**
- The predicate lives in `Document::import_leaf_is_used`
  (`vilan-lsp/src/document.rs:2388`). This is the one edit: a leaf whose
  bound name is in the file's effective prelude, and which resolves to
  the *same definition* the prelude binds, is not used. The
  same-definition check matters — `import my_lib::print;` where the
  prelude binds `std::print` must survive, because it is not redundant.
- The existing gate stays: pruning is already `.filter(|_| self.diagnostics
  .is_empty() && !self.is_stale())`. A broken file sorts and never prunes.
- **`vilan fmt` does not change.** formatter.rs:116–120 already rules
  that "the pruning of unused imports is the editor's job, not the
  formatter's", and formatter.rs:1141–1150 states it sharply: "Pruning is
  deliberately NOT part of `vilan fmt` (fmt has no analyzer)". A prelude
  is an analyzer fact. `vilan fmt` keeps sorting and keeps its hands off.
- The client-side `vilan.organizeImports.onSave` setting (default
  `false`, `editors/vscode/src/extension.ts`) then makes the strip
  opt-in-on-save for free, with no new setting.

Minting: `Analysis::auto_import_completions` and the two add-import
actions must never propose an import for a name the prelude already
binds — which falls out of the completion determination below, since
those actions are driven by "not in scope".

### 11.2 Completion — prelude names are in scope, undecorated

**Determination: prelude names are offered by `scope_completions`, not by
`auto_import_completions`, and carry no import edit.**

`Analysis::scope_completions` (`vilan-ide/src/completion.rs:1546`) walks
`scope.name_to_id_map` outward from the cursor. If §9.2's option 1 is
taken — prelude names seeded into the module scope's own map — **this
touchpoint needs no code change whatsoever**: the names are simply in the
map, and they arrive undecorated because nothing marks them.
`auto_import_completions` (line 1450) already skips anything in
`in_scope`, so it stops offering them and stops attaching `AutoImport`
edits by the same mechanism.

That is the strongest single argument for implementation option 1 in §9.2:
completion, go-to-definition and the add-import actions all fall out
correct, with no per-touchpoint prelude awareness.

### 11.3 Go to definition — already works

`Document::definition` (`vilan-lsp/src/document.rs:1693`) resolves through
`program.entity_map` and `program.type_references` to a definition `Id`,
then answers `program.source_of(id)`. It never consults the import node.
Because `resolve_import` binds a leaf name straight to the target
definition `Id`, an imported name is already indistinguishable from a
locally declared one at this layer. **A prelude that binds into
`name_to_id_map` gets go-to-definition for free**, landing in the std
source file exactly as an explicit import does today.

### 11.4 Diagnostics — a new arm, and a sentence to delete

The unresolved-name diagnostic is built in `analyzer.rs` (~30348 for
values, ~30527 for types) as `cannot find '{name}' in this scope{steer}`,
with `steer` from `Analyzer::import_steer` (28233) producing
`` ; import it first (`import std::{module}::{name};`) ``. `vilan-lsp`'s
`fn unresolved_name` (document.rs:2771) **parses these strings by prefix**
to drive the "Import `X` from …" quickfix — so the message shape is load-
bearing and must not be reflowed casually.

Three determinations:

1. **A new steer arm for the "not in this package's prelude" case**, in
   two shapes now that there are two std sets. When a name is absent from
   the file's scope and from the package's effective prelude, but *is* in
   one of std's, the steer names the set rather than proposing an import.
   Both keep the existing message prefix intact so the LSP's string
   parser is unaffected:

   - **The web-set arm — the one the ruling makes load-bearing.** A
     package on the base prelude writing bare `Signal`, `view`, `View`
     or `style` is the single most likely confusion the two-set design
     creates, and the fix is one manifest line:
     `` cannot find 'Signal' in this scope; it is in the prelude of the
     web set — set `prelude = "std::web"` in vilan.toml ``.
   - **The no-prelude arm.** A package with a custom or `false` prelude
     writing a base-set name:
     `` cannot find 'Some' in this scope; it is in the std prelude, which
     this package does not use (`[package] prelude` in vilan.toml) ``.

   The arms are ordered: the web arm fires when the name is in
   `std::web` and not in the effective prelude; the no-prelude arm when
   the name is in `std::prelude` and not in the effective prelude. A
   package already on `std::web` never sees the web arm, because the
   name resolves.
2. **Never steer toward an import of a name the prelude already binds.**
   `import_steer` must consult the effective prelude before offering.
   With option 1 of §9.2 this is automatic: a prelude-bound name is in
   scope and never reaches the diagnostic.
3. **`docs/appendix/errors.md` must lose a sentence it now asserts.** Its
   "Names and imports" entry reads "Usually a missing `import`:
   everything, even `print`, is imported explicitly." Under this proposal
   that is false, and it is the first thing a confused user reads.

The `.get()` steer-loss defect of §1.1 is **not** created by this
proposal and is not fixed by it — but the recommended set makes it
unreachable for `Some`/`None`, which is the case it was found in.
§14 Q8 asks whether to file it anyway.

### 11.5 Docs — one normative home, eight edits

`docs/spec/names.md` **§4.7** is the normative home; it already exists and
already carries the sentence this proposal deletes. The full edit list:

| File | Edit |
|---|---|
| `docs/spec/names.md` §4.7 | Rewrite: the ambient set becomes the primitives + `List`/`void` **and** the prelude's names; state the **two std sets**, ambient **module** names (§5.2), per-package scoping, the `prelude` key, and the weakest-scope rule. |
| `docs/spec/names.md` §4.4 | The scope ladder gains its weakest rung, and gains the item-vs-import precedence §9.2 exposed, which §4.4 does not currently state. |
| `docs/spec/appendix.md` §A.4 | The lang-item table gains a "in the default prelude" column — `Option` is already a lang item and this is where the two ideas meet. |
| `docs/appendix/glossary.md` | The `prelude` entry's definition changes. |
| `docs/appendix/errors.md` | The "everything, even `print`, is imported explicitly" sentence goes; the new steer arms and the **alias-removal** arm (§10.2) get entries. |
| `docs/tour/hello-vilan.md` §Imports | The teaching surface: hello-world stops opening with an import. |
| `docs/tour/projects.md` | The `vilan.toml` page documents the `prelude` key on `[package]` and `[library]`, and the `"std::web"` value. |
| `docs/appendix/editor.md` | The auto-import description gains the strip behaviour. |

No new page and no `SUMMARY.md` change: §4.7 exists, and a prelude that
needs its own chapter is too big.

Beyond the eight, §10.2's sweep touches **every fence that imports a
deleted alias** — 150 of them for `std::print` alone. Those are not
"docs edits" in the §11.5 sense; they are the migration, and §10.2 rules
that the docs corpus takes the *delete* shape so the fences teach the
prelude rather than a redundant import.

### 11.6 The probes, transcribed

All run against `vilan 0.39.0 (2ad39dd09)` in a scratch package.

**11.6.1 — `export import` re-exports everything a prelude needs.** A
module of the four `export import` lines and the one `export fun` in §8,
consumed by
`import pkg::myprelude::{ Display, print, Option, Some, None, Result, Ok,
Err, shout };` and a `main` that matches on both enums and calls
`.to_string()`: **runs**, printing `some 7` / `ok 1` / `re-export works`.
Before `Display` was added to the re-export list the only errors were
`i32 has no method 'to_string'; import std::display::Display to use it` —
i.e. the trait's methods travel through the re-export exactly as its name
does.

**11.6.2 — an explicit import beats a same-file declaration, silently.**
Transcribed in §9.2. Output `who wins?`, not `[mine] who wins?`.

**11.6.3 — no qualified escape hatch at the use site.** `std::print(x)`
written inline: `` `std` is a namespace, not a value; import the module
first (`import std::…;`) and qualify through its name ``.

**11.6.4 — the language produces an `Option` you cannot name.**
Transcribed in §1.1.

**11.6.5 — the steer-loss reproduction.** `Some(1)` bare →
`` ; import it first (`import std::option::Some;`) ``. Same, plus a list
literal → steer present. Same, plus `import std::iterator::ListIterator`
/ `std::map::Map` / `std::result::Result` → steer present. Via
`list.get(1)` → **steer absent**, both for `Some` and for `None`.

## 12. Migration and breaking posture

**Determination: shipping the preludes is ADDITIVE. Removing the aliases
(§10.2) is BREAKING. The change has two halves and they have opposite
postures, which is why the CHANGELOG carries them as separate entries
under separate family markers.**

The additive half first — the four ways *the prelude* could have broken
code, and why none of them does:

1. **A collision with a locally declared name.** §4: zero, outside std,
   for the recommended seven. And §9's rule means even the two that do
   exist (`Signal`, `Default`, both against non-members) would resolve to
   the local declaration — **provided §9.2's mandate is honoured.** This
   is not automatic; it is the implementation's single obligation.
2. **A now-redundant `import` becoming an error.** It does not: unused
   imports are not diagnosed by the compiler at all. formatter.rs:116–120
   rules that pruning "is the editor's job, not the formatter's", and the
   pruning that exists is a *code action*, never a build step. All 419
   redundant statements keep compiling, unchanged, forever.
3. **A change to what an existing name resolves to.** Impossible for a
   program that compiles today: every name in it already resolves, and
   every existing binding outranks the prelude.
4. **A dependency's meaning changing.** Excluded by §7.

**The prelude's own migration is therefore optional and mechanical**, and
has a shape: run Organize Imports across a package, review the
419-statement deletion, commit. The estate's own numbers: 46 statements in
std (which will not take them, §10), 150 in `test`, 21 in `examples`, 190
in `docs` fences, 7 in kolt, 5 in the website. 62 of 121 test files and 60
of 185 doc fences lose their import block entirely.

**The alias sweep's migration is not optional.** §10.2 prices it: 2,278
`import std::print` statements, 8 `std::panic`, 4 `std::assert`, 25 braced
forms naming a dying alias inside a larger `std::{ … }` group, and zero
uses of the other eleven aliases. It is mechanical in both its shapes and
neither shape requires judgement per site, but it must land in the same
change as the prelude — an estate where the alias is gone and the prelude
has not arrived does not compile.

Per the standing rule, **the breaking census includes the website and kolt
repos**. Neither imports `std::panic`, `std::assert` or `std::Default`;
both import `std::print` (2 units and 3 units respectively) and take the
delete shape, since both are application code the prelude serves.

Two migration notes the census forces:

- **The docs are the largest single beneficiary and the largest hazard.**
  190 of the 419 deletions are in fenced examples, and doc fences are not
  compiled by Organize Imports. They must be swept by hand or by a
  targeted script, and a half-swept docs tree teaches two conventions at
  once. Recommendation: docs are swept in the same change that lands
  §11.5's edits, not later.
- **The breaking census must include the website repo**, per the standing
  rule. It contributes 5 deletions and 1 near-miss (`let format`), and
  its `[package]` manifest needs no edit.

`std-shape.md`'s reserved-import-names work and the D5 registry are the
places this interacts with the future: once packages are published,
`prelude` becomes part of a package's published contract, and a library
that changes its prelude changes what its own source means but never what
a consumer's does (§7). That is the property that makes it safe to ship
before the registry rather than after.

### 12.1 What the build surfaced

Two defects the implementation found that the paper had not, both fixed in
the same change and both worth recording as evidence for how this feature
fails:

- **The base cache did not key on the prelude.** `BaseCacheKey` carried the
  platform, the entry's std seeds, the workspace and the macro budgets — but
  a stored world holds its modules' scopes *already seeded* with their
  ambient set, so a `std::web` world was served to a base-prelude program.
  It surfaced as a pin that passed alone and failed in a full run, which is
  the signature of process-global state. The key and
  `workspace_fingerprint` now carry the entry package's prelude and every
  dependency's.
- **The add-import quickfix offered a prelude module.** Once `std::web`
  existed, an unresolved `view` offered both `std::ui` and `std::web`, and
  the menu went ambiguous. The cause was drift the prelude merely exposed:
  the analyzer's B4 steer has always excluded re-exports
  (`collect_declared_names`: "pointing at a module that merely forwards it
  would name the wrong file") and the LSP's quickfix path did not. Bringing
  the quickfix into line with the analyzer's rule fixes it generally —
  nobody should ever be told to `import std::web::view`.

A third, **pre-existing and not this paper's**, was found while probing
per-package isolation and is worth a filing: a **type-position** unresolved
name inside a dependency module is attributed to std's `lib.vl` at a
nonsense span, where the value-position twin attributes correctly. The
value site calls `attribute_new_diagnostics` and the type site does not.
Reproduced on the shipped `vilan 0.39.0` with no prelude in play.

## 13. Determinations

1. **§5** std ships **two** preludes. The **base** set is seven names:
   `print`, `Option`, `Some`, `None`, `Result`, `Ok`, `Err`. Admission
   test: universal, language-level, unambiguous, top-of-census in more
   than one corpus.
2. **§5.3** The **web** set is the base seven plus the members `Signal`,
   `view`, `View` and the **modules** `style` and `ui`. Admitted against
   the base test with domain-level read as web-domain-level, plus a
   per-file-friction test (e) that `mount_root` fails and `json_codec`
   fails on corpus placement.
3. **§5.2** A prelude may make a **MODULE** name ambient, beside member
   names — a first-class concept, not a special case for `style`. An
   ambient module contributes exactly one name to the bare namespace, is
   admissible only if every targeted layer declares it, needs no new
   precedence rule (§9.1's ladder ranks it), and does not suppress
   platform-coloring checks at the use site.
4. **§3.4** The `Display` collision is **DISSOLVED**, not managed: bare
   `Display` is `std::display::Display`'s alone, the CSS enum is reached
   as `style::Display` through the ambient module, and
   `std::style::Display` never renames. `Display` the trait becomes
   admissible bare and is held out on frequency alone.
5. **§5.1** All platform-colored names — those a single layer declares —
   are excluded categorically from **both** sets.
6. **§6.2** The key is `prelude`, on **both** `[package]` and
   `[library]` — B156's `[package]`-only spelling could not state std's
   own posture, because std is a `[library]`.
7. **§6.2** Values: a **module path**, or `false`. There is no third
   grammar and no built-in set name: `"std::prelude"` and `"std::web"`
   are real std modules whose exports *are* the ambient names, written in
   vilan in the same mechanism a custom prelude uses. Omitted means
   `"std::prelude"`. `prelude = "std"` and `prelude = true` are refused
   with curated diagnostics. Not inherited from `[project]`.
8. **§6.1** The key qualifies under the manifest charter because the
   ambient scope must be known before the first file resolves and governs
   the file that would declare it — a bootstrapping hole, not a
   preference.
9. **§7** A file resolves under the prelude of the package that owns it.
   Never inherited: not from a consumer to a dependency, not from a
   dependency to a consumer, not from a workspace root, not per layer.
10. **§8** A custom prelude REPLACES the std one — and so does
    `std::web`, which re-states the base seven rather than deriving them.
    Extension is spelled by re-exporting. The shipped `export import`
    suffices — probed, including types, enum variants and
    traits-with-methods. No globs.
11. **§4.1** An ambient module is beaten by an explicit member import of
    the same spelling. `import std::style::style;` keeps bare `style()`
    working in all 60 estate call sites while the module `style` is
    ambient elsewhere — §9.1's one ladder, no special case.
12. **§9.1** The prelude is the weakest scope. A local declaration or an
    explicit import wins silently, with no diagnostic.
13. **§9.2** The prelude MUST NOT be implemented as synthesized imports
    at file head. Done that way it would silently break the two estate
    files that declare `Signal` and `Default`. Recommended: seed the
    module scope before real imports, so items and imports overwrite it.
14. **§9.2** Prelude bindings must be invisible to the reference index
    that `import_leaf_is_used` reads, or Organize Imports will prune real
    imports.
15. **§10.1** std compiles with `prelude = false`, stated explicitly in
    its own manifest. It forgoes 46 statements of savings and keeps its
    resolution greppable — and still *contains* the two prelude modules,
    which is a fact about contents, not resolution.
16. **§10.2** std's thirteen alias-only re-exports are **DELETED** and
    `std/src/lib.vl` with them: `print`, `panic`, `assert`, `Default`,
    `str` and the ten numerics. Eleven of the thirteen had zero estate
    uses; std used none of its own. Each old spelling gets a curated
    rename diagnostic. This is the change's breaking half.
17. **§11.1** Organize Imports STRIPS imports the prelude covers, matched
    on same-name-and-same-definition. `vilan fmt` is unchanged.
18. **§11.2** Prelude names are ordinary in-scope completions with no
    import edit; `auto_import_completions` and both add-import actions
    stop offering them by the existing "already in scope" filter.
19. **§11.3** Go-to-definition needs no change.
20. **§11.4** The unresolved-name diagnostic gains **two** arms — the web
    arm ("it is in the prelude of the web set — set
    `prelude = \"std::web\"`") and the no-prelude arm — both keeping the
    existing message prefix so the LSP's string parser is unaffected.
21. **§11.5** `docs/spec/names.md` §4.7 is the normative home; it exists
    already. Eight files edited, no new page, plus the fence sweep §10.2
    prescribes.
22. **§12** The prelude half is additive — zero collisions outside std
    for the base set, re-verified at `093bf567`, and redundant imports
    are not diagnosed by the compiler. The alias half is breaking and its
    migration is mandatory and mechanical: rewrite in the fixture
    corpora, delete in the teaching corpora.

## 14. Owner questions

**Q1 and Q2 are CLOSED by the ruling batch of 2026-08-29.** Q6 is closed
in passing. The rest remain open, and three new ones are added at the end
by the amendment's own determinations.

1. ~~**Is `Signal` in the default set?**~~ **CLOSED — neither answer.**
   The ruling created a second std prelude and put `Signal` in it. The
   question was framed as a choice between a *language* prelude and an
   *application* prelude; the ruling refused the framing and shipped
   both. §5 is rewritten around it.

2. ~~**Should `std::style::Display` be renamed?**~~ **CLOSED — no, and
   the question is dissolved.** Ambient module names (§5.2) mean the CSS
   enum is `style::Display` and never contends with the trait. The enum
   keeps its name, `Display` becomes admissible bare, and nothing in the
   estate moves. §3.4.

3. **Should a `[project]` workspace root be able to set a default
   `prelude` its members inherit unless they override?** §6.2
   determination 5 says no, on the "a semantic key must not travel any
   edge" principle. The counter is purely convenience: a workspace whose
   every member wants the same custom prelude states it N times. `[project]`
   already carries inherited `dependencies`, so the edge exists.

4. **Does the custom prelude module's own file get a prelude?** §7
   proposes **no** — the module that defines the ambient scope is the one
   file that resolves without it, which makes the implementation
   non-recursive and the file honest. The alternative (it gets its own
   prelude, i.e. itself) is defensible and slightly more uniform.

5. **Is `prelude = false` on std the right posture, or should std eat its
   own cooking?** §10 argues `false` on greppability and bootstrapping,
   at a cost of 46 import statements. The opposite ruling — std uses the
   std prelude — is a legitimate "no special cases" position and would
   make the feature's blast radius maximal on day one, which has its own
   virtue as a test.

6. ~~**Organize Imports strips prelude-covered imports — is that the
   right aggression?**~~ **CLOSED by the order — strip.** §11.1's
   reasoning stands and the ruling adopted it. Recorded here because the
   sweep (§10.2) leans on it: the fixture corpora keep redundant
   `std::io::print` imports that only the strip will ever clear.

7. **Should `prelude` be part of a package's published contract at D5,
   with a compatibility rule?** §12 argues it is safe because a package's
   prelude never affects a consumer. But a library that changes its
   prelude changes what its own future source means, and a registry may
   want that visible in the package metadata rather than only in the
   tarball's manifest. Not blocking; it wants an answer before D5.

8. **File the steer-loss defect?** §1.1/§11.6.5: `cannot find 'Some' in
   this scope` loses its `; import it first (…)` steer when the `Option`
   came from `list.get(…)`, in exactly the beginner case where the
   language produced the value. Reproducible; mechanism unconfirmed. The
   recommended prelude makes it unreachable for `Some`/`None`
   specifically, but the ambiguity filter that causes it presumably
   affects other names too.

9. **Does anything else deserve a place at the base set's table on
   *ergonomic* rather than census grounds?** The census answers "what is
   imported"; it cannot answer "what would be written if it were free".
   `Map`, `Set` and `Range` all fail the frequency test decisively (10, 6,
   11 units) and are excluded on the data — but `List` is already ambient
   and they are its siblings, so the ruling deserves to be conscious
   rather than arithmetic. **The amendment adds one candidate to this
   question**: `Display`, now that §3.4 has cleared its ambiguity. It is
   9 units on the data — below the bar — but it is the name whose absence
   taxes `.to_string()` on every program that prints a number, which is
   the purest "would be written if it were free" case in std.

**New, from the amendment's own determinations:**

10. **Is `"std::prelude"` the right spelling for the default set, given
    that it is never written?** §6.2 determination 2 buys one uniform
    value grammar — every value is a module path — at the cost of a
    stuttery name for a set nobody types (it is the omitted default). The
    alternatives were `prelude = "std"` (nicer, but requires the root
    module to *be* the prelude, which the alias sweep forecloses) and a
    package-names-its-prelude-module convention (`"std"` → `std::prelude`
    by rule), which is one more rule than the paper wanted. If the
    stutter matters, `"std::base"` and `"std::core"` were the runners-up
    and both collide with existing std terminology for the universal
    layer.

11. **Is `ui` the right second ambient module, or should the web set
    carry `view`/`View` only?** §5.3 admits the module chiefly so
    `mount_root` is reachable without being bare. The counter is that a
    web app touches `ui::` for essentially nothing else once `view` and
    `View` are ambient, which makes the module entry earn very little —
    and an ambient module the reader never sees used is a name in scope
    for nothing.

12. **Should `std::web` re-state the base seven, or should the two sets
    share a module?** §10.2 writes the seven twice — once in
    `std::prelude`, once in `std::web` — because §8 forbids merge rules
    and std must not get a mechanism users lack. The cost is a
    seven-line duplication in std that a future edit can desynchronise.
    The alternative is `export import pkg::prelude::{ … }` inside
    `web.vl`, which is *re-export*, not merge, and so is arguably already
    legal under §8 — worth confirming rather than assuming.

## 15. Census amendment — Order 23

`std::web` gained `SignalCell` beside `Signal` (now the write TRAIT,
A32): six base names + two ambient modules. Reason: B161 admits a trait
at a `let` annotation only, while a struct field, a return type and a
generic argument need a real type — exactly the sites the web census
counted `Signal` at (21 of 42 app files). Without the cell in the set,
any app storing a signal re-adds the import the prelude exists to
delete. The prelude is read off `web.vl` itself, so the LSP web-set
steer picked the name up with no second table.
