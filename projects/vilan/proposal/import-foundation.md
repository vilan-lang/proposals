# The import foundation — root values, projections, and `use` (A183)

**Status:** PAPER, Order 56 (lane lang-56a, 2026-11-03). Ruled in principle by the owner
2026-11-03 ("I like using the formal definition as the foundation our sugar is built on");
the model below is the spec's semantic definition of `import` (`names.md` §4.3.1, written
with this paper), not new syntax. Its first slices are A181 (absolute subjects, the bare
one-selector form, `*`), A182 (leaf-only admission, the prelude as the admission place) and
E359 (the quick-fix's spelling); the inline root heads and the dependency/platform roots
are later slices. §6 is the one ruling this paper asks the owner to make deliberately; §10
lists the rest with recommendations.

Prior art: `vilan/docs/spec/names.md` §4.1–§4.3, §4.6–§4.8; `visibility.md` §2.5, §3.2,
§3.6; `method-resolution.md` (B57); `prelude.md` §8; the B688 close (tracker archive,
2026-11-03). Probes: the integrator's kolt copy run (`sweeps/order56` scratch,
`kolt-exp.log`: a module-qualified selector subject works, an absolute one is refused
"`pkg` is a namespace, not a value"), the `selfsuper` probe (user aliases `as self` / `as
super` compile and run), and this lane's seven-shape probe under `vilan 0.53.1`
(`scratchpad/lang-56a/probe-inline`), cited by letter below.

---

## 1. The three primitives

The whole import surface is sugar over three things. Each is written in the spec's
metalanguage; only the first two have (or will have) a surface spelling.

**A root value — `(import X)`.** `X` is `pkg` (the importing file's own package), `std`,
or a dependency's manifest name; later a versioned or platform-conditioned root (§9). It
EVALUATES to a *namespace value*: the package's module tree, standing at its source root.
It is a value, not a binding — nothing in any scope is named `pkg` — which is exactly what
`names.md` §4.2 means by "the root names are reserved": a root is reached by evaluation,
never by lookup, so no package can shadow one or vanish behind one.

**Projections — `::name`, `::(impl T)`, `::*`.** A projection takes a value and yields a
value, and what it yields depends on what it is applied to:

| applied to | `::name` yields | `::(impl T)` yields | `::*` yields |
|---|---|---|---|
| a namespace (a root, a pure directory) | the module `name`; a directory with no body is itself a namespace (§4.1) | — (a namespace declares no blocks) | every module (unused by any surface form) |
| a module | its item `name`, or its submodule `name` — never both: a segment naming both is the §4.2 ambiguity error, refused at the declaration | the SET of `impl` blocks the module declares whose subject unifies with `T` (optionally `with Tr`: those implementing `Tr`) | every item the module exports (the glob of `visibility.md` §2.6) |
| a type (an enum, a struct, an array type written whole) | the member `name` of the type's namespace — a variant, a static, a `self` method (§4.6); "a type segment replaces the path's namespace" (§4.3) is this row: a type value has no items to project | — | its whole namespace (unused) |
| a set of blocks | the members named `name` across the set (one block answers, or the §4.6 refusal) | — | every member of every block in the set |
| a set of members | — | — | — |

`::{ a, b }` is the union of two projections of one value, nothing more. So a path is a
root value with projections applied left to right, and at every `::` there is a value with a
kind: `(import pkg)` is a namespace, `(import pkg)::m` a module, `(import pkg)::m::S` a
type, `(import pkg)::m::S::new` a static, `(import pkg)::m::(impl S)` a set of blocks,
`(import pkg)::m::(impl S)::bump` a set of members (one), and
`(import pkg)::m::(impl S)::*` the members of every `S` block `m` declares.

**`use P` — the binding form.** `use` takes a path's value and brings it into the file's
scope, by kind:

- a module or an item → BOUND under its leaf name (or the `as` name): `m`, `S`, `print`;
- a type's member → bound under its name (`Some`, `rem`); a `self` method is refused here,
  as today (§4.3: "a method is called on a value, not imported");
- a set of blocks, or a set of members → ADMITTED: the members join the file's method
  namespace for their subjects (§4.6's "one namespace per importing file"). Nothing is bound
  by name; `s.bump()` resolves because the file admitted a block declaring `bump` for `S`.

`use` is the metalanguage's word and NOT a surface keyword (§3). `export use P` is `use P`
whose result the module also publishes — importers see it "as if declared here" (§4.8).

That is all. Everything the language spells today is one of these three, and §2 says which.

## 2. The elaboration table

Every spelling the language has, one row each, with what it elaborates to. The path `a` in
a row stands for any root-headed module path (`pkg::m`, `std::web::style`, `dep::x`), and
`a` on the right is short for the elaborated root form `(import a₀)::…`. The marks:
**U** unchanged today (the elaboration is a description of what ships); **C** changes
meaning (the elaboration differs from today's behaviour, and the slice named is the
change); **N** newly legal (the spelling does not parse or does not resolve today).

| # | spelling | elaborates to | mark |
|---|---|---|---|
| 1 | `import a::b;` | `use a::b; use a::b::(impl *)::*;` — the leaf bound, the LEAF MODULE's blocks admitted. When `b` is an item of `a`, the leaf module is `a`: `use a::b; use a::(impl *)::*;` | **C** (A182): today the blocks of every module ON THE PATH are admitted too — `use a::(impl *)::*;` for a directory body `a` above `b` — the one implicit term the surface never wrote (§8) |
| 2 | `import a::b as c;` | `use a::b as c; use a::b::(impl *)::*;` — `as` renames the binding and nothing else (§4.3) | U |
| 3 | `import a::{ b, c as d, self };` | `use a::b; use a::c as d; use a; use a::(impl *)::*;` — one `use` per member; `self` is the namespace the set sits in (`a`), and the admission term is the leaf module's once. A set under a TYPE (`Option::{ self, Some, None }`) is the same: `use …::Option; use …::Option::Some; …` | **C** (A182) for the admission term, as row 1; the bindings U |
| 4 | `import a::b only;` | `use a::b;` — no admission term at all | U |
| 5 | `import a::{ (impl T) };` | `use a::(impl T)::*;` — these blocks and no other of `a`'s: a set with a selector IS the statement's whole admission out of `a` (§4.3 "these implementations only") | U |
| 6 | `import a::{ (impl T with Tr) };` | `use a::(impl T with Tr)::*;` | U |
| 7 | `import a::{ (impl T)::first };` | `use a::(impl T)::first;` — one member into the type's namespace for this file | U |
| 8 | `import a::{ (impl T)::{ first, last } };` | `use a::(impl T)::first; use a::(impl T)::last;` | U |
| 9 | `import a::{ (impl *) };` | `use a::(impl *)::*;` — every block `a` declares, which is row 1's admission term written out | **N** (A181): the spelling. `(impl _)` is the retired spelling of the same thing (row 26) |
| 10 | `import a::(impl T);` and `import a::(impl T)::first;` | as rows 5 and 7 — the one-selector set without braces, as `a::b` is the one-name set without braces; `vilan fmt` writes it so | **N** (A181): refused today by the parser (`parsing.rs:1376`, "a brace-set ELEMENT"), and the formatter keeps a lone selector's braces for that reason (`formatter.rs:5870`) |
| 11 | `import a::{ (impl pkg::x::T) };` | `use a::(impl (import pkg)::x::T)::*;` — the subject is a type path, and a type path's head may be a root (row 20) | **N** (A181): today "`pkg` is a namespace, not a value" at the subject (kolt-exp.log); the module-qualified `(impl x::T)` after `import pkg::x;` already works |
| 12 | `import a::{ #hidden };` | `use #a::hidden;` — the reach marker travels on the projection; it changes what the use may take (§4.8), not what the path means | U |
| 13 | `export *;` | `export use self::*;` — every item of this module published (`self` as in row 22) | U |
| 14 | `export import a::b;` | `export use a::b;` — the re-export; the admission term of row 1 rides along as today | U |
| 15 | `export import a::{ (impl T) };` | `export use a::(impl T)::*;` — a re-exported ADMISSION: every importer of this module (and every file of a package whose prelude it is) admits the blocks, as if this module declared them | **N** (A182): parses today, admits in the re-exporting file only |
| 16 | the package prelude (`[package] prelude`) | `use P::*;` for the prelude module `P`'s exports, placed before every file's first statement and as the weakest rung (§4.4, §4.7) — the prelude is a module, and ambient names are its exports | U |
| 17 | `mod self;` | the implicit `use (import pkg)::<this file's path> as self;` made explicit, as the host of the file's attributes (§4.1, §4); binds nothing new | U |
| 18 | `import pkg::m;` (the module form) | `use (import pkg)::m; use (import pkg)::m::(impl *)::*;` — row 1 with a module leaf | U |
| 19 | `m::x` inline, after row 18 | lookup of the binding `m` (a module value), then `::x` — the path head is a NAME in scope, and a name is resolved by the §4.4 ladder; the projections after it are §1's | U |
| 20 | `pkg::m::S` inline (a type, a struct-literal head, a static, a call) | `(import pkg)::m::S` — a BARE ROOT HEAD anywhere elaborates to the root value (§3) | **N** (inline roots, §9): today "`pkg` is a namespace, not a value" in type and value position (probes B, C) and "unknown struct: `pkg::m::S`" at a literal head (probe, §10 finds) |
| 21 | `(import pkg)::m::S` inline | itself — the explicit root, for a head a local binding shadows or a root that is not a plain name (`(import "dep@2")`, `(import std on browser)`: §9) | **N** (inline roots) |
| 22 | `self::x` | `(import pkg)::<this file's module path>::x` — an implicit, location-derived, reserved binding every file begins with (§4) | **N**: today `self` is an ordinary alias name (`import pkg::m::a as self;` compiles — the selfsuper probe, re-run as probe G) and the spec never mentions `super` |
| 23 | `super::x` | `(import pkg)::<the parent of this file's module path>::x` — one level only (§4) | **N** |
| 24 | `use T::{ a, b };` (the surface `use` statement, grammar §3.2) | `use T::a; use T::b;` with `T` a lexical binding — the metalanguage's `use` over a non-root head, which is what the statement always was ("loads nothing, the type being in scope already") | U today; §3 and Q1 recommend retiring the keyword, since `import T::{ a, b };` means the same under the bare-head rule |
| 25 | `T::member` in an expression (`List<str>::new()`, `Option::None`, `[i32; 3]::default()`) | lookup of `T`, then `::member` as a type projection — the statics and variants of §4.6 | U |
| 26 | `(impl _)` | `(impl *)` — read as row 9 with an error and a fix for one release, then refused; `vilan fmt` rewrites | **C** (A181): the spelling retires, the meaning does not |

Counts: **15 unchanged, 3 changed, 8 newly legal** (26 rows).

Three things the table makes visible that the prose never did:

- The ONLY implicit term anywhere is row 1's admission, and today it has one more implicit
  term than it shows (the path's directory bodies). A182 is the deletion of that term.
- A selector set (rows 5–11) is not a restriction ON an import; it is an import whose
  admission term is written out instead of defaulted. `only` (row 4) is the term deleted.
  This is why "a set naming one means these implementations only" and "`only` is for
  statements without a selector" are one rule, and why A182's "nothing implicit can be
  dropped by adding a selector" is the model's default rather than a pin to defend.
- Admission is a `use` whose result is a set, so it composes with `export` (row 15) exactly
  as binding does. The prelude is the place a package writes that once (§8).

## 3. One keyword

`import` is the surface's one word for the model, in two positions:

- **Statement position** — `import P;` is `use P′;`, where `P′` is `P` with a bare root
  head wrapped: `import pkg::m::S;` ≡ `use (import pkg)::m::S;`. The statement is the
  sugar, and the table above is its definition.
- **Path-head position** — `(import X)` is the root value itself, legal wherever a path
  stands: an expression, a type, a pattern, a selector subject, a struct-literal head.

**Bare root heads elaborate.** A path whose first segment is `pkg`, `std` or a dependency
name, in ANY position, reads as `(import that)::…`. Today this holds in import statements
only (`resolve_import_root`, `analyzer.rs:54360`); everywhere else the head is looked up as
a name and refused as "a namespace, not a value" (`analyzer.rs:70800`; probes B and C).
The explicit form exists for the two cases the bare one cannot serve: a local binding that
shadows a root's name (a struct field named `std`), and a root that is not a plain name
(§9). The bare head is what people write; the parenthesized head is what it means.

**Why no `use` keyword in the surface.** The metalanguage needs a word for "bring this
value into scope" that is not "load and bring", because the elaboration applies `use` to
things that load nothing (a set of blocks, a type's variant, the file's own module as
`self`). The surface does not: loading is idempotent and cycle-tolerant (§4.3), so a user
never needs to say "and do not load it", and a second keyword that means "the same, but I
promise it is already here" is a distinction only the compiler can check. Today's `use
T::{ a, b }` statement (row 24) is the one surface use of the word, and under the
bare-head rule `import T::{ a, b };` — `T` a name in scope, not a root — means exactly
the same. The estate writes nine of them (std 4, corpus 3, docs 2; kolt and the website 0).
Q1 recommends retiring the keyword with a one-release read-as-`import` and a formatter
rewrite; the grammar loses one production and the spec one paragraph.

## 4. `self` and `super`

**Implicit, location-derived, reserved.** Every file begins with two bindings nobody
writes:

```text
use (import pkg)::<this file's module path> as self;
use (import pkg)::<its parent's module path>  as super;
```

They are the model's reading of `names.md` §4.1's "a file `routes.vl` in a package's
source root is the module `routes`": the file knows its own path, so the bindings are
derived from the location and nothing else. Nothing is new in the resolver — probe G shows
the two aliases resolving today when a user writes them by hand (`super::helper() +
self::make().x` prints the expected sum). What is new: (a) they are implicit, so every
file has them; (b) they are **reserved** — a user `as self` / `as super` is refused ("the
file's own module; it cannot be rebound"; the estate writes none); (c) `super` is **one
level**: `super::super::x` is refused with the absolute spelling as the fix, as Rust
practice discourages chains and as the model prefers an absolute path over a relative
walk; a root-level file has no parent, and its `super` is refused by name.

**`self` in two positions is one `self`.** In a set (`import pkg::m::{ self, Theme }`,
row 3) `self` is the namespace the set sits in; at a path head (`self::x`, row 22) it is
the namespace the FILE sits in; in statement position (`mod self;`, row 17) it is that
same module as a declaration host. "The thing we are standing in" — the keyword is already
reserved for the third (`mod self { … }` is refused, §4.1), and the second only extends
the reservation to a head position where today it would be an alias.

**What it is for.** Three uses, in rising order of weight:

1. *Readability and shadowing* — `self::Item` says "mine" when an import or a prelude
   name would otherwise win the §4.4 ladder (the explicit-import-beats-declaration rung).
2. *A directory body's children* — a file `a.vl` with `a/b.vl` beside it reaches `b` as
   `self::b`, and an `import self::b::X;` reads as what it is.
3. *Hygiene in generated code* — a derive or a macro that names the host module's own
   declarations writes `self::Item` and is correct whatever the file imports; today an
   expansion has to name the item bare and hope nothing shadows it. **Derives emit
   `self::`** once the binding is blessed (the derive table already carries each std
   derive's module as an absolute path, `macros.rs:72`; the host side gets the same
   treatment).

**Moves.** A move changes what `self` and `super` denote — that is the intent: the file
now belongs where it was moved to — and leaves ABSOLUTE self-references pointing at the
old path. So the LSP's move refactor rewrites absolute paths (`pkg::old::x` → `pkg::new::x`,
in the moved file and in every importer) and leaves relative ones alone; `super` is
stable within one parent, which is the common move (a rename in place). A file's own
references written through `self` are move-stable by construction.

## 5. `_` and `*`

Two symbols, two meanings, stated once each where they are first defined (the spec edits
ride with this paper's table):

- **`_` is UNSPECIFIED** — a hole. `let _ =` a name not kept; a `_` arm a pattern that
  binds nothing; `List<_>` in an impl subject an element left open (the anonymous binder
  of `types.md` §5.4); `impl [type T; _]` a length left open. In every position `_` says
  "there is something here and I am not saying what".
- **`*` is EVERYTHING** — a set operation. `export *;` every item; `::*` every member or
  every export; `(impl *)` every block the module declares.

So `(impl *)` replaces `(impl _)` (row 26): a selector that takes every block is naming a
set, not leaving a hole. `(impl List<_>)` stays `_`: the element is a hole in a type, and
`List<*>` — a set in a type position — is not a type and is not introduced. The parser
accepts `*` at the whole-subject position and refuses `_` there with the steer; inside a
type it is the other way round. Estate: 24 `(impl _)` lines in-repo (13 of them one test
fixture, `module_resolution.rs`; 4 analyzer messages, 2 parser, 2 formatter, 1
transformer, 1 each in `names.md` and `grammar.md`), 21 in kolt (`std::display::{ Display,
(impl _) }` ×8, `pkg::lib::std_ext::{ …, (impl _) }` ×6, and the rest), 0 on the website.

## 6. The ruling to make: does an inline absolute path admit?

Row 20 makes `pkg::m::S { x = 1 }` legal with no import of `m`. `visibility.md` §3.2
defines a file's method namespace as "the union of the impls that file's IMPORT STATEMENTS
admit", and the paper's argument for it was *intent in one place*: the import list is where
a file says what it reaches, the only place a fix (a selector) can be written, and the
thing tooling reads to answer "what does this file reach". An inline root is a reach that
is not in the import list. Three ways to read it:

**(A) Explicit at its site; admits nothing.** An inline absolute path satisfies §3.2's
intent for what it NAMES — an item (`pkg::m::S`, `pkg::m::helper()`), a member named by
path (`pkg::m::S::new()`, `(import pkg)::m::(impl S)::bump` if anyone writes it) — and
nothing else. A bare method call on a receiver (`s.bump()`) still needs the file to ADMIT
the block: an import statement with an admission term (row 1, 5–11, 18) or the prelude.
"What does this file reach" is the import list plus the file's inline roots, both
syntactic, both greppable, both visible to the reference index (an inline root records
references exactly as an import's segments do, `record_reference`). Organize Imports
touches statements only; an inline root is never "unused". **Cost:** a file that writes
`pkg::m::S { … }` inline and calls `.bump()` on it gets B688's refusal naming the admission
to add — one statement, and the message already says which.

**(B) An inline root also admits the leaf's blocks.** `pkg::m::S` anywhere in the file
reads as row 1 for `pkg::m` too. **Cost:** the method namespace becomes a function of the
file's BODY — deleting an expression silently drops methods elsewhere in the file; two
files with identical import lists resolve `s.bump()` differently; Organize Imports cannot
see or prune the admission; the LSP's "what does this file reach" has to walk every path
in every body; and the admission is order-free but not location-free, which is the
property §3.2 was written to keep. It also re-admits by accident the thing A182 removes
on purpose (a parent's blocks arriving through a mention of a child).

**(C) Keep today's refusal.** Inline roots stay illegal; everything goes through the import
list. **Cost:** rows 11, 20–23 do not exist — no absolute selector subject (A181's
reason), no `self::` for derives, no quick-fix the compiler can emit without reading the
file's imports (E359's reason), and the §4.7 shadowed-prelude dead end stays (`std::io::print(x)`
"is refused; recover by importing the module and qualifying through it").

**Recommendation: (A).** It is the only reading under which the import list stays the
whole of a file's method namespace and inline roots stay the whole of its item reach —
two lists, each complete for its kind, both syntactic. The sentence for `visibility.md`
§3.2: *an import statement is where a file admits blocks; a path is where it names
things; a path admits nothing.*

## 7. What the resolver becomes

One function — `project(value, segment) -> value` over §1's kinds — applied from a root
value, plus `use` over the result. The three namespaces of `names.md` §4.2 stop being
three lookup tables keyed by a first segment and become three ROOT VALUES (`(import
std)`, `(import pkg)`, `(import dep)`); the "namespace vs value vs type" distinction stops
being a per-position rule and becomes the KIND of the value at each `::`. Where today's code
already is that function, and where it is not:

| piece | today | under the model |
|---|---|---|
| the root | `resolve_import_root` (`analyzer.rs:54360`): `pkg` → the package's namespace id, a dependency name → its namespace, else `module_id_by_name` (`std`) | IS `(import X)`; unchanged, called from every path head rather than from import statements only |
| module and item projection | `resolve_import`'s segment walk (`:54377`–`:54770`): `member_or_submodule` (`:37996`) answers `::name` on a module (item first, then the directory child), an `Expr::Module` hit descends, an `Expr::Enum`/`Expr::Struct` hit swaps in a type segment | IS `::name` on a namespace/module; unchanged |
| type projection | `type_namespace_member` (`:38027`): a type's statics and methods by name, found through the scope the walk stands in (an enum's variants scope first); B332's "a type segment REPLACES the namespace" (`:54596`) is the diagnostic for projecting an item name off a type | IS `::name` on a type. The B332 message stays as a steer, but the RULE it states is no longer a rule: a type value has no items, so the projection fails and the steer spells the module path — "retired as a rule, kept as a message" |
| type-position paths | `PreppedTypePath` (`:3358`), drained in `resolve_world` after the lexical type queue; the head is a NAME, and a root name is refused at `:70800` ("a namespace, not a value") | the head may be a root: route a `pkg`/`std`/dep head to `resolve_import_root` and continue with the same drain. This one edit is A181's absolute subject AND the inline type-position root of row 20 |
| expression paths | `resolve_prepped_local` (`:69414`) → `resolve_value_name_at` (`:37849`); a root head misses as a name and gets the same refusal; a struct-literal head gets "unknown struct" instead (probe, §10) | the same routing at the head; the two refusals retire together |
| the selector subject | `bank_import_restriction` (`:54141`) walks the subject with `walk_type_node` in a scope of its own, so it resolves "in the importing file's scope" — the module-qualified form works because `import pkg::x;` bound `x` there; the absolute form is a root head and is refused (kolt-exp.log) | the subject is a type path (row 11): the type-position edit above covers it; `queue_selector_paths` (`:54111`) already walks the selector's MODULE path through `resolve_import`, so the path half is done |
| admission | `ImplAdmission` (`:7629`–`:7760`): keyed `(importing file, declaring file)`, absent = unrestricted, empty = `only`, else the admitted member ids; `admits_member` / `admits_impl` read by `candidates_of` (`dispatch_refine.rs:275`), `applying_implementations` (`impl_select.rs:1163`) and `select_member` (`impl_select.rs:1495`) | IS `use` of a set: an entry per `(file, module)` is the set rows 5–11 wrote. Unchanged by A182 — the leaf-only change is in the reach, below |
| the selector's unification | `selector_takes` / `selector_reaches` (`:38685`, `:38694`), `selector_admits` (`:94420`) | IS `::(impl T)` on a module |
| the reach (B688) | `trait_reach_by_file` (`:64666`): the files a user file reaches = the declaring file of every name its scope binds, every file an import resolved into (`:64718`), and every file on an import statement's PATH (`:64740`, via `statement_sources` `:94261`); `check_trait_method_scope` (`:65175`) asks it for extension blocks only (`extension_block_file` `:65042`), never for a block in its subject's home, an always-loaded std module (`:65057`, `ALWAYS_LOADED_STD` `:85930`) or the entry | the path clause becomes a LEAF clause (row 1): the files an import's leaf stands in. That is A182's whole edit site (§8). The exemptions stay: they are not reach rules, they are the statement that a type's own blocks travel with the type |
| `self` / `super` | none — alias names (probe G) | two implicit `use … as` rows seeded per file where the prelude's are seeded (`resolve_world`'s prelude stage), reserved in `resolve_import`'s alias check |

What the LSP gains: hover on an import shows its elaboration (row by row: "admits 3 blocks
of `pkg::m` for `S`"); go-to-definition and rename over projections (a selector's type and
member names record references already, `visibility.md` §3.6); the move refactor of §4.
The formatter: canonical sugar forms — the bare form of a one-selector set (row 10,
`formatter.rs:5870`'s rule loses its selector exception), `(impl _)` → `(impl *)`, and
later `use` → `import` (Q1). The estate: nothing moves under the model itself — every
current spelling is a sugar form — and A182's census (§8) says what moves under its one
changed term.

## 8. Admission under the model

**Leaf-only (A182 part 1).** Row 1's admission term is the LEAF module's blocks, and the
directory-body rule of `names.md` §4.1 ("a plain `import pkg::a::b;` admits every block
declared along the path — `a`'s as well as `a::b`'s") is retired: `a`'s blocks arrive
through `import pkg::a;`, `import pkg::a::{ (impl T) };`, or a prelude that re-exports
them, and through nothing else. The reason is the table: that rule was the only term in
any elaboration the surface did not write, and it had the property §3.2 exists to prevent
— a statement's admission depended on files the statement never named, so rewriting a
plain import as a selector set could decline blocks the author never knew it admitted
(E359's note records six such errors on a kolt probe). `only` is unchanged (row 4). The exemptions of the reach rule stay as they are (§7): a block in its subject's home
module, or in a module of one of the subject's arguments, is the type's own surface and
travels with the type; a block of an always-loaded std module arrives in every build; the
entry's blocks serve its build.

**The prelude as the place (A182 part 2).** Row 15: a package prelude that writes `export
import pkg::app_overlay::{ (impl Overlay) };` admits those blocks to every file of the
package, once. The manifest already allows `prelude = "pkg::…"` and replaces std's set
entirely (`prelude.md` §8: "extend by re-export"), so kolt's prelude module is the web
prelude's ten lines re-exported plus one admission line — and the 28 `import
pkg::app_overlay;` statements B688 asked of it (29 files; one wrote the selector) become
zero. `prelude.md` §8's "no globs" was written under everything-public and
`visibility.md` §2.6 already recommends `::*` over an explicit export set; `export import
std::web::prelude::*;` would make the prelude module two lines, and is Q8.

**The census (what A182 moves).** The script is
`scratchpad/lang-56a/census.py` (its log beside it, `census.log`); it lists std's
directory bodies that carry `impl` blocks — `std::process` (4 blocks, 0 extension),
`std::rpc` (32, 3 extension: `SocketMessage`, `AbortHook`, `WebSocket`), `std::reactive`
(43, 1: a blanket), `std::web::style` (27, 7: `str`/`i32`/`f64`/`u32`/`BigInt`/`bool` with
`CssPiece`/`CssValue`) — and, for every file of std (76), the corpus `vilan/test` (152),
the docs fences (301, `fragment` excluded), the website (11) and the kolt copy (127),
finds the files whose ONLY reach to such a body is an import whose path runs through it to
a deeper leaf (`import std::reactive::store::Store;`, `std::rpc::server::Session`), with
the package's prelude counted as uses every file begins with, and intersects the file's
called method names with the body's. Kolt has no directory body of its own (`src/lucide/lib.vl`
carries no block).

Result: **0 files call a method that arrives only through a directory body's EXTENSION
block** — the set A182 can refuse. Two name-level candidates on HOME blocks, both exempt by
the type's-own-surface rule and both false positives on inspection: `reactive.vl` reaching
`std::reactive` (its own file; always admitted) and kolt's `store.vl` calling `.status()` /
`.get()` on `RemoteSource`/`SignalCell` values (`rpc.vl`'s and `reactive.vl`'s own blocks,
reached by the type; `Signal` is in the web prelude anyway). Twenty-nine files in the
estate do import THROUGH an impl-carrying body (kolt 14, docs 9 — `std/store.md` alone 9
fences — corpus 7, the website 0), and none of them calls a block the through-path alone
delivers: the only blocks a directory body carries today are its own types' and a handful
of primitive-extension blocks nobody reaches that way. So A182 is BREAKING by rule and
moves nothing by count; the `CHANGELOG` entry says so, and the pins carry the weight (a
three-file repro, the explicit import, the prelude, the selector-drops-nothing shape).
The census is a regex over names and over-approximates; the lane building A182 re-runs it
against the compiler's own refusal.

## 9. The slices

| slice | content | size | gate / pins |
|---|---|---|---|
| **A181** (lang-56b, first) | (1) root heads in type-position paths (`PreppedTypePath` routes `pkg`/`std`/dep heads to `resolve_import_root`), which gives absolute selector subjects in every position — tuple elements, generic arguments, array elements, closure types — and the module-qualified and bare-name rules stay; (2) the bare one-selector form `a::(impl T)` / `a::(impl T)::first` in the parser, fmt canonicalizing a one-selector set to it; (3) `*` at the whole-subject position, `_` there refused with the steer, fmt rewriting, the estate's 24 + 21 sites moved; (4) the `_`/`*` sentences in `names.md` §4.3 and `types.md` §5.4 (in with this paper's table) | S–M | each subject position with an absolute path, red before; the bare form parses, formats, round-trips; the estate's selectors unchanged (`(impl Overlay)`, `(impl bool with Display)`); `(impl _)` steered |
| **A182** (after A181) | the reach's path clause → leaf clause (`trait_reach_by_file:64740`); `export import a::{ (impl T) }` admits in importers and through a prelude; the census re-run on the compiler; `names.md` §4.1's paragraph and §4.6's "every block declared in `a`'s file and in every file on the path" rewritten to the leaf; `visibility.md` §12 note; CHANGELOG `breaking` | M (the code is S; the pins and the spec are the M) | a directory-body block no longer reaches a child's importer; the explicit import does; the prelude does; a selector beside a plain statement drops nothing it did not name (probe E's shape, as a pin) |
| **E359** (with A181) | the quick-fix emits `import {module}::(impl {absolute subject});` — row 10 with row 11 — and names the block in the sentence; until A181 lands, the module import | S | the fix compiles in a file that imports nothing from the module |
| **inline roots** (S, later this order or next) | bare root heads in expression, type, pattern and struct-literal position elaborate (row 20); `(import X)` parses in path-head position (row 21); the two "namespace, not a value" refusals and "unknown struct: `pkg::…`" retire; §4.7's shadowed-prelude recovery sentence goes (`std::io::print(x)` inline is legal); `self`/`super` seeded and reserved (rows 22–23); derives emit `self::`; the reference index records inline roots | S for the resolver, S for `self`/`super`, M with the LSP move refactor | probes B, C, G green; a shadowed head needs the explicit form; `super::super` refused; `as self` refused |
| **dependency / platform roots** (design, later) | `(import "name@2")` a versioned root for two majors of one dependency in one build; `(import std on browser)` a platform-conditioned root for F27's layers; what `pkg` means inside a library consumed by two packages | paper | — |

What each pins: A181 pins that the subject of a selector is a TYPE PATH and nothing else
(no binders, no values); A182 pins that admission is syntactic and leaf-shaped; E359 pins
that the compiler can spell any admission it asks for without reading the file; the inline
roots pin that a root is a value and `self` is a binding; the last slice pins the root's
grammar before it has to carry a version.

## 10. Owner questions, finds

**Q1 — retire the surface `use` keyword?** Rec: YES, as the one-keyword ruling implies.
`import T::{ a, b };` with `T` a name in scope means the same (row 24); one release
reading `use` as `import` with a steer, `vilan fmt` rewriting; the estate's nine sites go
with the sweep. Alternative: keep it as the spelling of row 24 forever — two keywords for
one `use`, which the ruling declined.

**Q2 — `super` one level only?** Rec: YES. `super::super::x` refused with the absolute path
as the fix. Alternative: unbounded chains, as Rust allows and its style guides discourage.

**Q3 — the user `as self` / `as super` refusal: at once, or after a release?** Rec: at
once, with the inline-roots slice; the estate writes none, and the aliases were never
documented.

**Q4 — `import self::child::X;` legal?** Rec: YES (row 22: a directory body reaching its
own children); `import self;` and `import self::x;` of the file's own item are refused as
redundant ("`x` is this file's own").

**Q5 — §6's ruling.** Rec: (A), an inline path admits nothing.

**Q6 — the `(impl _)` window.** Rec: read as `(impl *)` with an error carrying the fix for
v0.54.0, refused from v0.55.0; fmt rewrites from v0.54.0.

**Q7 — E359's final spelling.** Rec: the bare form with the absolute subject, `import
pkg::app_overlay::(impl pkg::lib::overlay::Overlay);`, and the sentence names the block
("`menu` is declared by `impl Overlay` in `pkg::app_overlay`; admit it: …").

**Q8 — does a re-exported admission (row 15) travel to ANY importer of the re-exporting
module, or through a prelude only?** Rec: any importer — a re-export is "as if declared
here", and the model has no second kind of `export use`. Beside it: `export import
std::web::prelude::*;` as the two-line package prelude, which `visibility.md` §2.6 already
recommends and `prelude.md` §8 declined under everything-public; rec: allow it with this
slice, the §2.6 rule intact (a glob over an unexported module binds nothing and warns).

**Q9 — `self`/`super` under `[platform]`-layered std, where one module path has two files?**
Rec: `self` is the file, as the layers already are per file; no new rule.

Finds (id-less, for the integrator to file):

- A struct-literal head with a root (`pkg::m::S { x = 1 }`) answers "unknown struct:
  `pkg::m::S`" where a type or value position answers "`pkg` is a namespace, not a value"
  (probe, main.vl variant 1 vs B/C) — two messages for one mistake, both retired by the
  inline-roots slice; until then the literal's should say what the other two say.
- The formatter keeps a lone selector's braces only because the parser refuses the bare
  form (`formatter.rs:5870` cites `parsing.rs:1376`); A181 edits both or neither.
- `trait_reach_by_file`'s path clause (`:64740`) builds `statement_path_index` per call for
  every restricting file; under leaf-only the index is the statement's leaf file, already
  in `import_targets` — the clause may delete rather than change.
- `names.md` §4.7's last paragraph ("a shadowed prelude name has no qualified spelling at
  the use site") documents a limitation the inline-roots slice removes; the sentence goes
  with it, and the ledger row behind the refusal.
- `grammar.md` §3.2's `use` production and its paragraph are Q1's; the `path-branch`
  production gains `"(" "import" NAME ")"` as a head alternative with the inline-roots
  slice, and `impl-selector` loses its brace-only status with A181.
