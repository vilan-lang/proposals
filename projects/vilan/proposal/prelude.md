# The prelude — a manifest-configurable ambient scope (B156)

> **Status: PROPOSED 2026-08-31** (work order 21, cycle 39; tracker item
> [[B156]]). Written to the ruled frame on B156: the census draws the
> default set, the design questions below are settled here, and the
> numbered **owner questions** in §14 are the owner's.
>
> Everything measured here was measured mechanically against the estate at
> `vilan` @ `2ad39dd0` (v0.39.0), kolt @ its 0.38.0 migration, and the
> website @ its v0.38.0 deploy. Every behavioural claim about the shipped
> compiler was probed against the installed `vilan 0.39.0 (2ad39dd09)`;
> the probes are transcribed in §11.

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

### 3.4 One name the census disqualifies outright

`Display` ranks 12th overall and 5th in applications — and it is **two
different std names**: `std::display::Display` (the `to_string`/`format`
trait, 9 units) and `std::style::Display` (the CSS `display` property
enum, 14 units). They live in the base layer together and cannot both be
ambient. Any prelude containing `Display` must first rename one of them.
Noted here because it is the one place the census found the estate
already colliding with *itself*, and it happens to be a name a
reflex-driven prelude would have included: making the trait ambient is
what would let `.to_string()` work everywhere (§11.6.1 shows a re-exported
trait does carry its methods through).

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

**The headline: for the recommended set of §5, the collision count
outside std is ZERO.** Not one estate file declares `print`, `Option`,
`Some`, `None`, `Result`, `Ok` or `Err`. The two real collisions
(`Signal`, `Default`) are both against names the recommended set does not
include, and both would be resolved silently and correctly by the
shadowing rule of §9 — but only if that rule is implemented the way §9.2
insists, which is the one place this feature can genuinely break code.

The website's `let format = || { … }` is the near-miss worth keeping in
view: a real application, a real closure, a name that a slightly larger
prelude would have made ambient. It is exactly why the prelude must be
the weakest scope and not merely a low-priority import.

## 5. The default set the data draws

**Recommendation — the default std prelude is these seven names:**

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

**Rejected, with the reason:**

- **`Signal` (61 overall, rank 1 in applications).** The strongest
  rejection to argue and the most likely to be overturned (§14 Q1). For:
  it is universal (base layer — SSR needs it), unambiguous, and the
  single most-imported name in real application code. Against: it fails
  (b) squarely — reactivity is a domain, not a language feature; a vilan
  CLI tool or a compiler plugin never touches it; it is the one candidate
  with a real estate collision (`test/match-patterns.vl`); and it buys
  four percentage points. The clean answer is that `Signal` is precisely
  what the **custom** prelude exists for: an application whose every file
  is reactive declares one, and the census says that application is
  every application vilan has.
- **The style/UI cluster** (`view`, `View`, `style`, `Display`, `Length`,
  `space`, `Color`, `AlignItems`, `FlexDirection`, `Style`, `Overflow`,
  `Cursor`, `Position`, `JustifyContent`, `UserSelect`, `mount_root`) —
  sixteen names, nine of them in the application top sixteen, and the
  single largest block of imports in application code. Rejected as a
  block: domain-level by definition, `Display` is ambiguous (§3.4),
  `view`/`View` are platform-**layered** (`std/src/browser/ui.vl` and
  `std/src/process/ui.vl` each declare them), and putting sixteen CSS
  names in every vilan program's ambient scope is exactly the "platform-
  colored names presumably never" line B156 drew. This cluster is the
  best argument in the census for the custom prelude, and `std-shape.md`
  has already narrowed a split to it.
- **Platform-colored names** (`Server`, `Response`, `fs`, `storage`,
  `router`, `mount_root`, `db`, …) — refused categorically. A name whose
  module lives in a `[library.layer.…]` overlay cannot be ambient without
  making a browser build's ambient scope differ from a node build's, and
  the platform-coloring model reports reachability errors *at the use
  site* (§4.3 of the spec) — an ambient name would move the error's
  cause off-screen.
- **`Shared` (25)** — 9 of its 25 are std's own files and 10 more are doc
  fences, leaving **6 units of real non-std code** in the whole estate.
  Fails (d).
- **`Map`, `Set`, `Range` (10, 6, 11)** — the plausible "inherent-ish"
  candidates B156 asked about. All three fail (d) outright: `Range` is 11
  units, `Map` 10, `Set` 6, against `Result`'s 36. `List` is already
  ambient (§4.7) and is the reason these look like they belong; the data
  says they do not. Reconsider if a future census moves them.
- **`Display` / `format` / `panic` / `assert` / `Default`** — `Display`
  is ambiguous (§3.4). `format` is 7 units and has the website's
  block-scope collision. `panic` (10 units, 9 of them std's own),
  `Default` (4 units, all four std's own) and `assert` (1 unit, in
  `examples`) are barely imported outside std at all. All three are
  already in `std/src/lib.vl`'s short-name set, which is a different
  thing from being ambient.

**A note on `Display` and the trait-method tax.** `.to_string()` on an
`i32` fails today with `i32 has no method 'to_string'; import
std::display::Display to use it` — a whole class of import that exists
only to unlock methods, and one a prelude *could* abolish (§11.6.1 confirms
a re-exported trait carries its methods through). It is left out here
only because the name is ambiguous. Renaming `std::style::Display` — the
CSS enum, the younger and more replaceable of the two — would clear the
way, and is put to the owner as §14 Q2.

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

**Recommended:**

```toml
[package]
prelude = "std"                     # the default; may be omitted entirely
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
   story — declare one. Same key, same values, both sections.
2. **The value is a string or `false`.** `"std"` names the default;
   `false` means no prelude; any other string is a **module path** in the
   grammar `import` already accepts (`pkg::…`, a dependency name, or
   `std::…`). Not a table, not a list, not a merge spec — see §8.
3. **Omitting the key means `"std"`.** The feature's whole point is that
   the common case is silent. A package that says nothing gets the
   default set; the manifest gains a line only when the answer is
   unusual. This also makes the key **additive to every existing
   manifest in the estate** with no edit.
4. **`prelude = "std"` written out is legal and identical to omitting
   it.** Someone will write it to be explicit; refusing it buys nothing.
5. **It is not inherited from a `[project]` workspace root.** A workspace
   root's `[project]` section carries `packages` and shared
   `dependencies`; a semantic key must not travel that edge either, for
   the reason §7 gives. Each member states its own. (Owner question
   §14 Q3 — this is the one place a convenience argument exists.)
6. **`false`, not `"none"` or `""`.** TOML has a boolean; the value is a
   yes/no about a whole mechanism. `split` in `[package]`/`[entry.…]` set
   the precedent for a bare bool.
7. **The key is validated at manifest load**, beside `target`'s
   validation: `false` or a syntactically valid module path, with the
   path's *resolution* diagnosed at build time against the package's own
   modules and dependencies, pointing at the manifest line.

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

## 10. std's own posture

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

1. **A new steer arm for the "not in this package's prelude" case.** When
   a name is absent from the file's scope, is absent from the package's
   prelude, and *is* in the **default std** prelude, the steer should say
   so rather than propose an import — this is the misdirection a custom
   or `false` prelude creates, and the only new class of confusion the
   feature introduces. Proposed wording, keeping the existing prefix
   intact so the LSP parser is unaffected:
   `` cannot find 'Some' in this scope; it is in the std prelude, which
   this package does not use (`[package] prelude` in vilan.toml) ``.
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
| `docs/spec/names.md` §4.7 | Rewrite: the ambient set becomes the primitives + `List`/`void` **and** the seven prelude names; state per-package scoping, the `prelude` key, and the weakest-scope rule. |
| `docs/spec/names.md` §4.4 | The scope ladder gains its weakest rung, and gains the item-vs-import precedence §9.2 exposed, which §4.4 does not currently state. |
| `docs/spec/appendix.md` §A.4 | The lang-item table gains a "in the default prelude" column — `Option` is already a lang item and this is where the two ideas meet. |
| `docs/appendix/glossary.md` | The `prelude` entry's definition changes. |
| `docs/appendix/errors.md` | The "everything, even `print`, is imported explicitly" sentence goes; the new steer arm gets an entry. |
| `docs/tour/hello-vilan.md` §Imports | The teaching surface: hello-world stops opening with an import. |
| `docs/tour/projects.md` | The `vilan.toml` page documents the `prelude` key on `[package]` and `[library]`. |
| `docs/appendix/editor.md` | The auto-import description gains the strip behaviour. |

No new page and no `SUMMARY.md` change: §4.7 exists, and a prelude that
needs its own chapter is too big.

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

**Determination: shipping the default prelude is ADDITIVE. Nothing in the
estate breaks, and no file must be edited.**

The four ways this could have broken code, and why none of them does:

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

**The migration is therefore optional and mechanical**, and has a shape:
run Organize Imports across a package, review the 419-statement deletion,
commit. The estate's own numbers: 46 statements in std (which will not
take them, §10), 150 in `test`, 21 in `examples`, 190 in `docs` fences, 7
in kolt, 5 in the website. 62 of 121 test files and 60 of 185 doc fences
lose their import block entirely.

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

## 13. Determinations

1. **§5** The default std prelude is seven names: `print`, `Option`,
   `Some`, `None`, `Result`, `Ok`, `Err`. Admission test: universal,
   language-level, unambiguous, top-of-census in more than one corpus.
2. **§5** `Signal` is excluded — rank 1 in application code, but
   domain-level, +4 percentage points, and the one candidate with a real
   estate collision. It is the exemplar of what a custom prelude is for.
3. **§5** The style/UI cluster and all platform-colored names are
   excluded categorically.
4. **§3.4** `Display` is disqualified by ambiguity: `std::display::Display`
   and `std::style::Display` both exist in the base layer.
5. **§6.2** The key is `prelude`, on **both** `[package]` and
   `[library]` — B156's `[package]`-only spelling could not state std's
   own posture, because std is a `[library]`.
6. **§6.2** Values: `"std"` (the default), a module path, or `false`.
   Omitted means `"std"`. Not inherited from `[project]`.
7. **§6.1** The key qualifies under the manifest charter because the
   ambient scope must be known before the first file resolves and governs
   the file that would declare it — a bootstrapping hole, not a
   preference.
8. **§7** A file resolves under the prelude of the package that owns it.
   Never inherited: not from a consumer to a dependency, not from a
   dependency to a consumer, not from a workspace root, not per layer.
9. **§8** A custom prelude REPLACES the std one. Extension is spelled by
   re-exporting std names from the custom module. The shipped
   `export import` suffices — probed, including types, enum variants and
   traits-with-methods. No globs.
10. **§9.1** The prelude is the weakest scope. A local declaration or an
    explicit import wins silently, with no diagnostic.
11. **§9.2** The prelude MUST NOT be implemented as synthesized imports
    at file head. Done that way it would silently break the two estate
    files that declare `Signal` and `Default`. Recommended: seed the
    module scope before real imports, so items and imports overwrite it.
12. **§9.2** Prelude bindings must be invisible to the reference index
    that `import_leaf_is_used` reads, or Organize Imports will prune real
    imports.
13. **§10** std compiles with `prelude = false`, stated explicitly in its
    own manifest. It forgoes 46 statements of savings and keeps its
    resolution greppable.
14. **§11.1** Organize Imports STRIPS imports the prelude covers, matched
    on same-name-and-same-definition. `vilan fmt` is unchanged.
15. **§11.2** Prelude names are ordinary in-scope completions with no
    import edit; `auto_import_completions` and both add-import actions
    stop offering them by the existing "already in scope" filter.
16. **§11.3** Go-to-definition needs no change.
17. **§11.4** The unresolved-name diagnostic gains one arm — "it is in
    the std prelude, which this package does not use" — keeping the
    existing message prefix so the LSP's string parser is unaffected.
18. **§11.5** `docs/spec/names.md` §4.7 is the normative home; it exists
    already. Eight files edited, no new page.
19. **§12** The change is additive. Zero collisions outside std for the
    recommended set; redundant imports are not diagnosed by the compiler,
    so nothing must be edited. Migration is a mechanical Organize Imports
    sweep, with the 190 doc-fence deletions done by hand in the same
    change as the docs edits.

## 14. Owner questions

1. **Is `Signal` in the default set?** The census says it is the
   most-imported name in application code (21 of 42 app files, ahead of
   `print` at 15) and the eighth-ranked overall. §5 excludes it as
   domain-level and worth four percentage points, and points at the
   custom prelude instead. This is the determination most likely to be
   wrong, and it is the one that decides whether the default prelude is a
   *language* prelude or an *application* prelude.

2. **Should `std::style::Display` be renamed, so `Display` can join the
   prelude later?** The trait `std::display::Display` is what makes
   `.to_string()` work; the estate imports it 24 times, and today's
   diagnostic for the missing import (`i32 has no method 'to_string';
   import std::display::Display to use it`) is a tax on every program
   that prints a number. It cannot enter the prelude while the CSS enum
   holds the same name in the same layer. Renaming the CSS one is cheap
   in alpha and impossible later.

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

6. **Organize Imports strips prelude-covered imports — is that the right
   aggression?** §11.1 chooses strip over leave. Strip means running the
   action on an old file produces a large, mechanical diff; leave means
   the estate carries 419 dead statements indefinitely and new files
   copy-paste them forward. There is no third option that keeps one
   canonical spelling per file.

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

9. **Does anything else deserve a place at the seven's table on
   *ergonomic* rather than census grounds?** The census answers "what is
   imported"; it cannot answer "what would be written if it were free".
   `Map`, `Set` and `Range` all fail the frequency test decisively (10, 6,
   11 units) and are excluded on the data — but `List` is already ambient
   and they are its siblings, so the ruling deserves to be conscious
   rather than arithmetic.
