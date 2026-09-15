# Visibility and the import surface — default-private, the reach, and the per-importer method namespace

Tracker **B318** (the owner's design, filed 2026-09-12; RULED to the paper at Order 34's GO,
R1). Written by lane `paper-visibility-34` of Order 34 on vilan `next` @`e4d192e3`; every
probe is `vilan 0.40.0 (e4d192e3e)`, the toolchain at that sha in **both** install locations.
**No compiler change lands from this lane.** The build is Order 35's, on §9's slices.

Related: **B317** (a type's associated function under a bare name — builds this order in
`lang-34`, and is the one piece of B318's surface that ships before the paper does),
**E168**/**E169** (Organize Imports over-prunes and over-keeps — `editor-34`), `prelude.md`
§7–§9/§11/§14, vilan's spec `docs/spec/names.md` §4 (the one-namespace rule at §4.6), `dead-code-paint.md` §1.5
(the `generated` root), `method-resolution.md` §3/§13 (the precedence B318 relaxes),
`diagnostics-standard.md` B6/C3, `std-surface.md` §5 (the B4 method steer).

---

## 0. What the probes changed about the design

Three of B318's premises do not survive contact with the shipped compiler. Each is answered
in place below; they are collected here because they are the parts a build would have hit
first.

1. **`#` is NOT lexically free.** B318 records it as free, "the css lexer refuses `#333`
   inside a block only". It does not: `#` is refused by the LEXER, unconditionally, at
   `lexing.rs:281` with the curated rule `HASH_IS_NOT_A_TOKEN` (`lexing.rs:949`), ledger row
   **335**, and an LSP quickfix that keys on the constant by prefix
   (`document.rs:4839`, css-block §7.2 fix 1). `lexical.md` §2.5 states the governing
   principle — "lexing is greedy and context-free: no token depends on parse state". Probe
   P3 and P10c. Taking `#` costs a token, a retired curated rule, a re-homed quickfix and a
   ledger edit. Four punctuation marks that DO lex today and mean nothing in an import path
   (`!`, `^`, `?`, `%` — probe P11) are the zero-lexer-cost alternatives. §2.3 recommends
   paying for `#` anyway, and says exactly what the bill is.
2. **`export(PATH)` collides with a form that compiles clean today.** `export (helper);`
   is accepted by `vilan check` with no diagnostic (probe P2d): `parse_export`
   (`parsing.rs:5653`) takes any statement, and a parenthesized expression is one. The
   collision is harmless in practice — zero occurrences of `export` followed by `(` in the
   whole estate — but the grammar needs a rule, and the right rule also fixes a nonsense
   form. §2.2.
3. **std's unexported top-level item count is not 364.** Measured at `e4d192e3`: **664**
   top-level declarations across 63 files (347 `fun`, 166 `struct`/`enum`/`trait`, 109
   `external fun`, 27 module-level `let`), and **zero** of them carry `export` — the 11
   `export` lines in std are all `export import`. The likely origin of 364 is std's own
   manifest comment, "264 names across 59 files" (`prelude.md` §10.1), which is itself now
   stale. §6 has the real numbers, and the number that actually sizes the migration is not
   664 but **118** — the items another std file imports by name.

And one premise that survives better than B318 claims: **the two warnings need no new
machinery.** `Program::warnings` / `Program::warning_sources` (`analyzer.rs:45523`) already
exist, the CLI already renders them non-fatally (`vilan-cli/src/main.rs:6368` — "they do not
enter `errs`, so they don't block codegen"), the language server already publishes them at
`DiagnosticSeverity::WARNING` (`publish.rs:374`), and they already carry ledger rows (row
386 is one). Five warnings ship today. B318's two are a sixth and a seventh.

---

## 1. The model, stated once

**Visibility is one bit on an importable.** Nothing else changes shape.

- Every top-level item of a module is **private** unless marked. `export` before a
  declaration sets the bit and otherwise changes nothing — the item stays local, the item
  stays callable, the item's `impl`s stay where they are.
- `export *;` at a module's top level sets the bit on **every** item of that module. It is
  the one-line opt-in to today's everything-public, and it is what the codemod writes.
- `export(in PATH)` narrows the bit to a **scope subtree**: `export(in mod)` keeps one item
  private under an `export *;`; `export(in pkg)` publishes to the item's own package and no
  further; `export(in pkg::a)` publishes to the module subtree rooted at `pkg::a`.
- **Visibility never gates ACCESS.** The bit is consulted by exactly three things:
  completion (a private item of another module is not offered), the add-import quickfix
  (`import_candidates`, `document.rs:4605` — a private item is not a candidate), and the
  "import it first" steer (`import_steer_inner`, `analyzer.rs:37840` — a private item is not
  steered toward). Resolution itself is unchanged: `resolve_import` (`analyzer.rs:33446`)
  binds what the path names, exported or not.
- **A reach is spelled.** `import a::{ #hidden };` imports a private item deliberately. The
  marker means "I know this is private and I want it anyway". Reaching a **dependency's**
  private item this way is no diagnostic at all — RULED, and correct: whether an item should
  be exported is the author's judgement and the consumer's need is real evidence against it.
- A **plain** `import a::hidden;` of a private item is a WARNING with two fixes (§5). That
  one warning is the whole reason the default can flip without breaking a program.

Two consequences worth stating because they are what make the bit cheap:

**`export` on a declaration is a no-op TODAY.** `collect_importables` (`analyzer.rs:4231`)
calls `unwrap_item` (`analyzer.rs:4312`), which strips `Node::Export` along with derive,
service and macro-attribute wrappers, so `export fun f` and `fun f` produce byte-identical
importable rows. Probe P0: a second file importing an unmarked `fun hidden` from `a.vl`
compiles with no errors. The flip therefore adds a field to `Importable` and a set to the
analyzer; it does not rewrite the import walk.

**One package already writes the marker.** `macro_std` marks 26 of its 31 top-level
declarations `export` (`meta.vl`, `build.vl`, `lib.vl`) — a library written as if
default-private already existed, whose author's intent the compiler currently discards. That
is the single best argument that the marker reads the way B318 wants it to read, and the
single best argument that its current meaning (nothing) is a trap.

### 1.1 Where the bit lives

`Importable` (`analyzer.rs:4149`) gains `exported: Visibility`, and
`collect_importables` stops stripping `Node::Export` blindly: the wrapper's presence, and
its `(in PATH)` argument when it has one, become the row's visibility instead of being
discarded. `module_importables` (`analyzer.rs:49388`) — the on-demand, parse-cached reader
the language server uses for completion and for add-import candidates — then answers the
question with no analyzer at all, which is what keeps the three tooling consumers cheap.

Inside a loaded program the analyzer additionally keeps

```
exported_entities:  HashSet<Id>              // items whose declaration carried `export`
export_all_modules: HashSet<Id>              // modules carrying `export *;`
export_scopes:      HashMap<Id, ExportScope> // the `(in PATH)` narrowings
```

all three filled during declaration hoisting, beside the scope map `resolve_import` already
writes into. "Is `id` visible to file `f`" is then a set lookup plus, for a narrowed export,
one module-path prefix test.

`Visibility` is deliberately NOT a field on `Function`/`Struct`/`Enum`/`Trait`: those
structs are read by the solver and the transformer on hot paths, and visibility is a
property of a NAME IN A MODULE, not of a definition — the same definition is public through
one module's re-export and private in the module that declares it. Keeping it on the
importable row and in two analyzer sets is the honest shape and the cheap one.

---

## 2. Grammar, probed

Every spelling B318 proposes was written into a scratch package
(`vilan.toml` = `[package] name="probe" root="." entry="app.vl" target="browser"`) and run
through the installed `vilan check`. The verdicts:

| # | spelling | verdict | what the shipped parser does |
|---|---|---|---|
| P0 | `import pkg::a::{ helper, hidden };` (neither marked) | **clean** | the baseline: `export` on a declaration means nothing today |
| P1 | `export *;` | **needs a rule, no collision** | `found ';' expected an expression` — `*` starts a prefix-deref expression and finds no operand |
| P1b | `export * helper;` | parses (as `export` of `*helper`) | so the rule must be a `*` + `;` lookahead, not "`*` after `export`" |
| P2 | `export(in pkg) fun helper()…` | **needs a rule** | `expected ';' to end this statement` at the `)` |
| P2b | `export(in mod) fun …` | needs a rule | `unclosed '('` + `found 'mod' expected an expression` |
| P2c/d | `export(pkg) …` / **`export (helper);`** | **COLLIDES** | `export (helper);` **compiles clean today** (§2.2) |
| P3 | `import a::{ #hidden };` | **LEXER refusal** | `` `#` is not a vilan token `` — row 335, not a parser matter (§2.3) |
| P3b | `import a::#hidden;` | LEXER refusal | same |
| P4 | `import pkg::a only;` | **needs a rule, no collision** | `expected ';'` at the gap after `a` |
| P5 | `import a::{ (impl Thing) };` | **needs a rule, no collision** | statement fails; recovery reports `found 'import' expected an expression` |
| P5b | `import a::{ (impl List<i32>)::{ first, last } };` | needs a rule | same |
| P5c | `import a::{ (impl List<_>) };` | needs a rule | same; `_` lexes as an identifier |
| P6 | `export mod m { … }` + `import pkg::a::m::helper;` | **WORKS TODAY** | an inline `mod` is a full namespace on the import path |
| P6b | `import pkg::a::m::*;` | **needs a rule, no collision** | `*` lexes; the statement does not parse |
| P6c | `import pkg::a::m::inside;` (unmarked member) | works today | `mod` is fully transparent today |
| P6d | `import pkg::a::m;` then `m::helper()` | works today | a `mod` is importable as a module |
| P7 | an intermediate module's `impl`s | **arrive** (§3.1) | confirms B318's claim, with a control |
| P8 | two modules declaring `Thing::tag`, both loaded | refused at the declaration | the crux's exhibit (§3) |
| P8b | the same two, only one loaded | **clean** | today's "global" namespace is really per-PROGRAM |
| P9 | `impl Holder<str>::join` + `impl Holder<type T: Show>::join`, one module | refused | B318's open (i), reproduced (§10 i) |
| P10 | `export impl Holder<i32> { … }` | **parses today** (as a no-op) | the marker is already spellable on an impl |
| P10b | `import a::{ (impl _) };` | needs a rule | — |
| P10c | `import a::{ #(impl Thing) };` | LEXER refusal | the `#` cost again |
| P11 | `import a::{ !hidden }` / `^` / `?` / `%` | **lex; parser refuses** | four zero-lexer-cost marker candidates |

### 2.1 `export *;` — the lookahead

`parse_export` (`parsing.rs:5653`) is two lines: eat `Token::Export`, then `parse_statement`.
The rule is a lookahead **before** that call: `Token::Export` followed by the operator `*`
followed by `;` is the module-wide export, and nothing else in the language has that shape
(P1 proves the `;` never arrives on the expression path; P1b proves a following NAME does,
so the lookahead must include the `;`). One new node — `Node::ExportAll(span)` — and one new
named parser rule constant, which per AGENTS.md needs **both** `RULE_STATEMENT_SITES` and
N65's `CURATED_RULE_STATEMENTS` edits.

`export *;` is a **module-level** item: inside a body it takes the existing refusal
(`analyzer.rs:26055`, "`export` is a module-level item and cannot appear inside a body").

### 2.2 `export(in PATH)` — and the form it displaces

`export (helper);` compiles clean today. It is `export` wrapping an expression statement,
and it publishes nothing, checks nothing, and emits nothing — a form with no reading. The
estate contains **zero** occurrences of `export` followed by `(` (grepped across `vilan/`,
kolt and the website), so the right rule is the one that takes the parenthesis AND closes
the hole:

> `export` takes an ITEM, an `import`/`use`, or `*;`. A `(` after `export` opens a
> visibility scope. `export <expression>;` is refused with a curated rule naming the three
> things `export` can take.

That is one refusal row (breaking in principle, unreachable in practice — no program in the
estate trips it) and it buys an unambiguous `export(in mod)` / `export(in pkg)` /
`export(in pkg::a)` without a contextual-keyword dance. `in` is already `Token::In`
(`for … in`), so the inner grammar is `"(" "in" path ")"`.

**Recommendation: keep `in` (B318's spelling), and refuse `export(pkg)` without it** with a
steer naming `export(in pkg)`. The word is what makes the form read as a scope rather than
as a call, and P2c shows the un-`in`'d form is exactly the one that looks like a call.

### 2.3 `#` — the real bill, and the recommendation

The `#` byte reaches `skip_illegal` (`lexing.rs:274`) and produces `HASH_IS_NOT_A_TOKEN`.
Making it a token costs:

| item | cost |
|---|---|
| `Token::Hash` + `is_operator_byte`/`skip_illegal` edit | S |
| ledger row **335** retired or rewritten | one row edit + `--test diagnostics_ledger` |
| `HASH_IS_NOT_A_TOKEN`'s curated text re-homed to the **css block parser** (a `Hash` token inside a `css` block body is the hex-colour mistake, and the message and its fix must survive) | M — it moves from a context-free rule to a context-ful one, which is exactly what `lexical.md` §2.5 says lexing must not do; the parser is where the context lives |
| the LSP quickfix at `document.rs:4839` re-keyed off the new message | S |
| `lexical.md` §2.4's "`#id` selectors are unwritable" sentence gains "the byte is the import reach marker; it is still not a css token" | S |
| estate impact | **zero** — 217 `#` bytes across 18 `.vl` files (`vilan/`, `crates/`, kolt, the website), and **0** of them outside a string literal or comment |

The alternative is a marker that already lexes: `!`, `^`, `?` or `%` (P11 — all four lex and
all four fail only at the parser). `!hidden` reads as negation, `?hidden` as the try
operator, `%hidden` as modulo, `^hidden` as xor — none of them reads as "reach past a
fence", and all four are operators whose appearance inside a path would have to be
explained. A contextual keyword (`import a::{ private hidden }`) reads fine but spends a
word inside a brace set where every other element is a bare name.

**Recommendation: pay for `#`.** It is the only candidate with no competing reading, the
estate cost is nil, and the css rule it displaces is better off in the parser anyway — the
lexer currently refuses `#` in a position (an import path) where the css-colour advice is
simply wrong advice, which probe P3's output demonstrates verbatim. The paper records the
bill so the ruling is conscious; if the owner prefers not to spend it, the fallback is `^`
(the only one of the four that is not also a prefix or postfix operator in expression
position) and everything else in this paper is unchanged.

### 2.4 `only` — free

`only` does not occur as an identifier anywhere in `vilan/`, kolt or the website: **zero**
occurrences outside comments and string literals (397 raw hits, all prose). A trailing
`only` before the `;` of an import statement is unambiguous (P4: today it is a parse error),
it cannot shadow an item called `only` (that item is reached as `a::only`, a path segment,
which the rule never sees), and it follows `as`'s precedent exactly — `as` is contextual,
recognized only where a path segment has ended (`parsing.rs:5688`–`5706`, the E142 comment).

The rule belongs in `parse_import_statement` (`parsing.rs:5623`), not in the path grammar:
`only` qualifies the STATEMENT, not a leaf. `use … only;` is refused — `use` never brought
impls in the first place.

### 2.5 The selector — `{ (impl TYPE) }` and `{ (impl TYPE)::{ m, n } }`

Every selector form lexes and none parses (P5, P5b, P5c, P10b). The grammar addition lives
in `parse_namespace_set` (`parsing.rs:5727`), which today calls
`parse_namespace_single_path` per element and therefore requires each element to begin with
a name. A new element production, tried first:

```text
selector    = "(" "impl" type-expr ")" [ "::" ( NAME | path-set ) ] ;
```

where `type-expr` is the ordinary type grammar with `_` admitted as a placeholder at any
argument position, and no binders (`type T`) are written — RULED. `(impl _)` is the
whole-module impls-only form. `_` already lexes as an identifier (`is_ident_start` admits
`_`), so the placeholder needs a type-position rule, not a lexer one.

Two grammar facts worth pinning when this is built:

- The current failure mode is bad. A selector in a brace set makes the WHOLE statement fail
  to parse, and the recovery reports `found 'import' expected an expression` **at the
  `import` keyword** (P5/P5b/P5c/P10b, all four identical). Any build of this slice should
  add the curated rule for a malformed selector before it adds the selector, or a typo
  inside a selector will report at column 1.
- `as` is refused on a method selector (RULED: methods are called by name on a receiver).
  The refusal has a home already — the alias production is a tail of
  `parse_namespace_single_path`, and the selector is a sibling production that simply does
  not offer it, so the refusal is a curated message rather than a grammar branch.

### 2.6 `export mod` and `::*`

`export mod m { … }` needs **nothing**. P6/P6c/P6d: an inline `mod` already parses, already
registers as a namespace on the import path, already lets `import pkg::a::m::helper;` bind a
member, and already lets `import pkg::a::m;` bind the module for `m::helper()` qualification.
Only the `export` marker's meaning is new, and that is §1's bit.

`import path::m::*;` is the one new row (P6b). `prelude.md` §8's "No globs" was written
under everything-public, where a glob imports whatever the source module happens to gain;
under explicit exports a glob imports exactly the named set, which is the property that
sentence was protecting. The paper's recommendation is B318's: `::*` is legal over any
module once exports are explicit, and `export mod` is the idiom for a curated set.

One rule the build must state: **a glob over a module with no `export` marks at all imports
nothing** and warns ("`pkg::a` exports no names; `import pkg::a::*;` binds nothing"). The
alternative — a glob over a private module importing everything privately — makes the reach
implicit, which is the one thing §1 rules out.

### 2.7 Probe reproduction

All probes ran under `scratchpad/paper-visibility-34/probe/`, one scratch package, `vilan
check` per spelling. The module set: `a.vl` (an exported `helper`, a private `hidden`, a
`struct Thing` with a static `make`, and an `export mod m`), `x.vl`/`x/y.vl` (the
intermediate-module impl exhibit), `z.vl` (the collision exhibit), `gen.vl` (the generic
same-module pair). Nothing was written into any vilan worktree.

---

## 3. The per-importer method namespace — the crux

### 3.1 What is true today

**An `impl` block is registered by LOADING, and registration is program-wide.**
`self.implementations` (`analyzer.rs:27455`) is one flat `Vec` for the whole program; there
is no per-file filter anywhere. The analyzer's own steer says so in its doc comment
(`unimported_trait_method_steer`, `analyzer.rs:37810`): *"Discoverability here is module
reachability, not the method's home: an `impl` block registers when its FILE loads, so
importing any name the file declares is the fix"*.

Probe **P7** makes the consequence concrete, and it is the strongest single argument for
`only` and for selectors:

```vilan
// x.vl          — never imported by app.vl
import pkg::a::Thing;
impl Thing { fun bump(self): i32 { self.x + 1 } }

// x/y.vl
export fun y_helper(): i32 { 8 }

// app.vl
import pkg::a::Thing;
import pkg::x::y::y_helper;        // loads x.vl as a path node (names.md §4.1)
fun main(): i32 { Thing::make().bump() + y_helper() }   // ← compiles clean
```

`app.vl` never names `x`. It imports something two levels UNDER `x`, `names.md` §4.1's
"a child pulls its parent" loads `x.vl`, and `x.vl`'s extension impl arrives with it. The
control (P7b, dropping the `y_helper` import) reports `Thing has no method 'bump'`. Today a
file's method surface is a function of which files the whole PROGRAM happens to have loaded.

**The collision rule is a declaration-site rule over that loaded set.** Probe P8: two
modules each declaring `impl Thing { fun tag(self) }`, both reached from one entry, report

> `'tag' is already defined for 'Thing' by module 'x'; remove or rename this one`

at the SECOND declaration, with a cross-file note at the first
(`check_duplicate_inherent_members`, `analyzer.rs:6933`; the message is built in
`report_duplicate_declarations`, `analyzer.rs:7523`, and the ` by module 'x'` clause in
`other_module_clause`, `analyzer.rs:7514`). Probe P8b: drop one of the two imports and the
program is clean. So `names.md` §4.6's "a type has ONE namespace, globally" is, in the
shipped compiler, "one namespace per PROGRAM" — and a program is already a smaller thing
than the ecosystem. B318 moves it one step further in the direction it already leans.

### 3.2 The rule, defined

> **A file's method namespace for a type is the union of the impls that file's import
> statements admit.** An `import a::b;` admits every impl declared in `a`'s file and in
> every file on the path to it (today's meaning, unchanged). `import a::b only;` admits
> none. `import a::{ (impl T) }` admits exactly the impls of `a` whose subject unifies with
> `T`. Two admitted impls declaring one inherent name for one subject are a **refusal at
> the IMPORT**, spanned on the second import statement, naming both blocks.

**Refused at the import, not at the call** — a single answer, chosen for three reasons.
(1) The import list is where the file expresses its intent, and it is the only place the fix
lives: the fix is a selector, and a selector is written in an import. (2) A call-site
refusal fires N times for one mistake and fires only on the paths the file happens to
exercise, so a file can be half-broken. (3) It preserves today's property that the refusal
is a DEFINITION-ORDER-INDEPENDENT fact about a file, which is the whole reason B57 exists
(`method-resolution.md` §3/§4: "which one dies is decided by the order the modules happened
to load in").

The message, in the existing family's voice and with the existing cross-file note:

> 'tag' is already defined for 'Thing' by module 'x', which this file also imports; a file
> may take only one. Select one — `import pkg::z::{ (impl Thing)::tag };` — or drop an
> import

One ledger row `NEW`, one C3 note at the other import statement. The declaration-site rule
`check_duplicate_inherent_members` **stays** for the same-module case (§10 (i)) and is
narrowed to it.

### 3.3 What `candidates_of` and `impl_members_for_bound` become

Both are in `dispatch_refine.rs` and both are NAME-keyed and program-wide, which the module
documents at length (`dispatch_refine.rs:276`, the B254/B258 silence class: *"every override
of every trait declaring the name, whatever the receiver"*). `solver-34` is adding a doc
comment per consumer under B279; this paper's requirement is one line longer than a comment:

- `candidates_of(program, name)` (`dispatch_refine.rs:149`) gains a **file** parameter and
  filters the per-trait implementation loop by that file's admitted-impl set. Its consumers
  are `context.rs:641`, `const_eval.rs:1768/1789/1808` and `inference/bounds.rs`'s harness —
  every one of them holds a call id, and a call id yields a file (below).
- `impl_members_for_bound(program, subject, member, traits)`
  (`dispatch_refine.rs:206`) gains the same parameter and filters
  `program.implementations.iter()` by it before the subject test. `impl_members_for` and
  `known_receiver_candidates` thread it through.
- `impl_select::applying_implementations` (`impl_select.rs:589`) — the EMISSION-side
  selector — gains it too. This is the one that is not free; §3.5.

The admitted set itself is one map, built once after import resolution:

```
file_impls: HashMap<SourceId, Vec<usize>>   // indices into program.implementations
```

`Implementation` (`analyzer.rs:1754`) carries no declaring source today; it needs one field
(the impl block's own `Id` is already minted at registration — `impl_id: id` at
`analyzer.rs:27431` — so `source_of(impl_id)` answers, and storing the `SourceId` directly
avoids the linear `source_ranges` scan `source_of` is, which M27 already flagged as a
whole-program-loop hazard).

### 3.4 How a call consults it

`Constraint::MethodCall { id, .. }` (`analyzer.rs:2262`) anchors on the CALL expression, and
the analyzer's own comment at `analyzer.rs:2363` establishes the invariant this needs:
*"`call_id` is caller-side always"*. So the calling file is `program.id_ranges_of` /
`source_of(call.id)` with no new plumbing and no new field on the constraint — which is why
the analyzer half of this crux is genuinely cheap.

**Unification at the call is the receiver's type against the selector's type** (B318's open
(b), answered in §10 b): the selector is a TYPE-level filter on the impl set, and it is
applied by the same `impl_select::subject_applies` that already decides whether an impl's
subject pattern covers a concrete type. `(impl List<i32>)` admits the block
`impl List<type T>` (the pattern covers `List<i32>`) but, in a file that wrote that
selector, the admitted block serves ONLY receivers whose type unifies with `List<i32>`: a
`List<str>` receiver in that file finds no admitted impl and reports the ordinary
`List<str> has no method 'first'` with the existing "import it first" steer naming the
unselected block. `(impl List<_>)` admits the same block for every argument. `(impl _)`
admits every impl of the module.

### 3.5 The one hard part: emission re-asks

`impl_select::select_member` (`impl_select.rs:694`) is called from the **transformer**, twice
(`transformer.rs:8038` and `transformer.rs:9576`), to resolve a member at MONOMORPHIZATION —
a generic body specialized at a concrete type has to find the impl that provides an inner
`self.tag()`. `select_member` takes `maxima(...).first()`, i.e. with two equally specific
inherent impls both declaring the name it picks one arbitrarily. That is precisely the
silent pick B57 exists to prevent, and today it is unreachable only because the
declaration-site refusal makes the pair impossible. **Relaxing the refusal to per-importer
re-opens it unless the transformer is taught the file too.**

The answer, and it is a clean one: the file a monomorphized body resolves under is **the
file the body was DECLARED in**, not the file that instantiated it. A generic function in
`a.vl` means what `a.vl`'s imports say it means, at every instantiation — which is the same
rule `prelude.md` §7 already rules for the prelude ("a consumer cannot change what a
dependency's source means"), and the only rule under which a library is analysable at all.
The transformer knows the enclosing function it is emitting, so the parameter is
`source_of(enclosing_fn)` and the two call sites thread it.

**Pin to write when this is built:** an impl in `b.vl`, a generic body in `a.vl` that calls
`x.tag()`, and a caller in `c.vl` that instantiates it at a type `b.vl`'s impl serves —
resolves under `a.vl`'s selector set, and is refused if `a.vl` admitted no `tag`. That pin
is the one that will fail if anyone implements "the instantiating file's set".

### 3.6 The reference index and the steers

- **The reference index** (`references.rs`, read through `Document::reference_index`) is
  keyed by `Definition`, which is a definition id — unchanged. What changes is that a
  selector element is a new kind of import leaf that must `record_reference` at its TYPE's
  span (so go-to-definition on the `Thing` in `(impl Thing)` lands on the struct) and at
  each method name's span in `::{ first, last }` (so rename reaches them). Without those
  rows, `import_leaf_is_used` cannot see a selector at all and Organize Imports will delete
  it — the E168 failure mode, one construct over.
- **`impl PATH` resolves in the IMPORTER's scope** (RULED). `import item::Struct as S;`
  followed by `import item::{ (impl S) }` is legal, and so is the qualified
  `(impl item::Struct)`. Mechanically this is `try_get_type_id_by_name`
  (`analyzer.rs:24283`) against the importing file's module scope, run AFTER that file's
  other imports have bound — which means selector resolution is a second pass over a file's
  import list, not a single walk. One ordering rule, stated: **plain leaves bind first,
  selectors resolve second**, in one file, and a selector naming an alias the same statement
  introduces is legal.
- **The B4 method steer** (`collect_impl_method_steers`, `analyzer.rs:4361`;
  `unimported_trait_method_steer`, `analyzer.rs:37819`) keys on `(subject head, method)` →
  the importable name that makes the block visible. Under selectors its answer changes from
  "import any name this module declares" to "admit this impl", so the steer's text becomes
  `; import std::display::Display to use it (`import std::display::{ (impl i32) };`)` only
  when the file already imports that module `only` or with a narrower selector — otherwise
  the existing text is still the shortest fix and stays. The steer's index is built from
  std's files (`build_std_indexes_if_needed`) and needs no visibility filter of its own:
  a private impl is still reachable, and the steer names the module, not the item.

### 3.7 What this buys, in one sentence

Two independent packages may each write `impl Style { fun helper(self) }` and both stay
installable in one program; the file that wants both is the file that has to choose, and it
has a spelling for choosing. That is the property `names.md` §4.6 forbids today, and it is
the reason the crux is worth its cost.

---

## 4. The exposure warning

**RULED wording**, with the agreement fix B318 itself asks for:

> ``S`` is returned here. `my_fun` is exported, but `S` is not. A consumer can call
> `my_fun`, but **cannot** name the return type.

("are unable" → "cannot" — the subject is "a consumer", singular. "is unable" also agrees;
"cannot" is shorter and reads better in a one-line diagnostic. One ledger row `NEW`.)

**Reach — the signature positions, and only these:**

| position | example |
|---|---|
| a module-level `let`'s type | `export let registry: Table = …` |
| a parameter type | `export fun f(t: S)` |
| a return type | `export fun f(): S` |
| an exported struct's field types | `export struct Box { item: S }` |
| an exported enum's variant payloads | `export enum E { One(S) }` |
| a trait bound | `export fun f<T: MyTrait>(t: T)` |
| a generic argument in any of the above | `export fun f(): List<S>`, `Map<K, S>` |

**Never a body.** A private type used inside an exported function's body is exactly the
encapsulation the feature exists to permit.

**Where it lives.** B318 and the brief say "after declaration hoisting, before bodies". In
the shipped analyzer that is not a place a signature's TYPES are known: written annotations
resolve through the constraint fixpoint, and the checks that read resolved signature types
all run post-`build()` in the `unless_cancelled!` family at `analyzer.rs:53950`–`53990`.
The warning's home is there, immediately before `check_duplicate_module_declarations()`
(`analyzer.rs:53968`) — after `check_trait_conformance()`, which is where the family's own
comment says signature types are settled, and before the duplicate family so an exposure
warning reads ahead of a collision error about the same declaration.

It pushes to `self.warnings` / `self.warning_sources`, not `self.diagnostics`. That matters
beyond severity: 62 sites in the compiler gate on `diagnostics.is_empty()`, including the
organizer's "a file carrying a diagnostic never prunes" (`document.rs:4176`), and a warning
must not disable Organize Imports.

**The fix.** "Export `S`" is a workspace edit that inserts `export ` before `S`'s
declaration wherever it lives (`program.source_of(S)` + the declaration's own span — the same
pair `Document::definition` already uses, `document.rs:3011`). When `S` belongs to a
**dependency** there is no fix and the message gains one sentence:

> `S` is declared by `depname` and cannot be exported from here — the shape has to change, or
> `depname` has to export it.

**One case B318 does not cover, ruled here:** a signature position that names a type from a
`[library]`'s *own* package but a different module, where that type is exported — no
warning. The check is "is the named type visible to a consumer of THIS module", which for a
`export(in pkg)` type inside a package whose own exported function is `export(in pkg)` too
is satisfied. The check therefore compares VISIBILITY LEVELS, not booleans: the warning
fires when the type's level is strictly narrower than the item's.

---

## 5. The plain-reach warning — what makes the flip non-breaking

Recommended, not ruled. A plain `import a::hidden;` where `hidden` is private:

> `pkg::a::hidden` is not exported by `pkg::a`. Importing it anyway is allowed — mark the
> reach: `import pkg::a::{ #hidden };`

with two fixes: **Export `hidden`** (a workspace edit on `a.vl`, the §4 fix reused) and
**Import as `#hidden`** (a one-token insertion at the leaf).

**Why a warning and not an error.** The census (§6) says the estate holds **294** cross-file
item imports that would become errors on the day of the flip, across eight packages, plus 10
doc snippets. As a warning, every one of them keeps compiling, `vilan check` prints the list,
and the codemod (`export *;` at the top of each module) or the curation pass clears them at
the author's pace. As an error, the flip is a release where nothing builds until the whole
estate moves in one commit — including kolt's generated `src/lucide/lib.vl`, whose 1,820
items are written by `scripts/lucide.mjs` and cannot be edited by hand at all (the generator
has to learn to emit `export *;`). The cost of the warning is one release in which a private
item is only softly private; the cost of the error is a flag day. §8 rules the sequence.

**The qualified reach.** B318 discusses import leaves. The other door is
`import pkg::a;` followed by `a::hidden()` — no leaf to mark. Measured: **5** distinct
`module::item` pairs over 8 sites in std, **14** pairs over 15 sites in kolt (every one of
them a lucide icon), **0** in the website and **0** in macro_std. So the door is narrow. The
recommendation: **the same warning fires at the qualified path segment**, with the "Export"
fix and a second fix that rewrites the call site to a marked import
(`import pkg::a::{ #hidden };` + `hidden()`). If that second fix is judged too invasive for
a first slice, ship the warning with the Export fix alone — 19 sites in the whole estate is
not a number that needs a refactoring.

**`#` on a whole module, a private `mod`, a private impl, a `::*` member** — B318's open
(d), answered in §10 d.

---

## 6. The migration census

Measured at `e4d192e3` (kolt at its 2026-09-13 working state, read once into scratch and
censused from the copy; the website at `vilan-website/src`). "Needs `export`" counts
DISTINCT top-level items that at least one OTHER file of the same package imports by name —
the items a curation pass must mark, and the exact set the `export *;` codemod makes
unnecessary.

| package | files | top-level items | `export`-marked today | needs `export` | import statements touched | intra-package import statements |
|---|---:|---:|---:|---:|---:|---:|
| **std** | 63 | 664 | 0 | **118** | 155 | 208 |
| **macro_std** | 3 | 31 | **26** | **0** | 0 | 13 |
| **kolt** (hand-written) | 23 | 130 | 0 | **72** | 58 | 143 |
| kolt `src/lucide` (generated) | 1 | 1,820 | 0 | 0 by name (14 by qualification) | 0 | 2 |
| **website** | 11 | 333 | 0 | **81** | 21 | 64 |
| examples (13 packages) | 29 | 109 | 0 | **15** | 16 | — |
| templates (3) | 8 | 9 | 0 | **3** | 5 | — |
| benchmarks | 7 | 24 | 0 | **5** | 6 | — |
| cli test projects (2) | 2 | 19 | 0 | 0 | 0 | — |
| `vilan/test` corpus | 131 | — | 0 | **0** | 0 | 1 file uses `import pkg::` |
| docs snippets | 48 files, 462 fences | — | 0 | — | 10 `import pkg::` lines | — |
| **TOTAL** | | | **26** | **294** | **261** | |

std's 118 sit in 28 of its 63 modules: `reactive` 23, `rpc` 17, `operators` 12, `wire` 9,
`json` 7, `ws` 6, `bytes`/`compare`/`style`/`time` 5 each — 94 across those ten — and 24
names spread over the other 18 (`fetch` 3; `base64`/`crypto`/`io`/`iterator` 2; the rest one
apiece). That list IS std's curated export surface, and it is
an extremely useful artifact on its own: 118 of 664 declarations — **18%** — are the ones
std's own files depend on across a file boundary, and everything else is either a module's
private machinery or public API reached only by consumers (which the curation pass must
decide about separately, from the docs and `std/` pages rather than from the imports).

**macro_std needs zero new marks.** It marks 26 of 31 declarations already, its single
intra-package item reach is `use meta::Source;` in `lib.vl`, and `Source` is one of the 26.
It is the estate's proof that the marker is writable.

**The codemod.** For kolt, the website, the examples, the templates and the benchmarks:
`export *;` as the first line of every module that another file imports from — **43** modules
by named import, plus kolt's generated `src/lucide/lib.vl` (whose 14 reaches are qualified,
not named), so **44** one-line edits, mechanical and reviewable, preserving today's semantics
exactly. The lucide line is emitted by `scripts/lucide.mjs` — one string in the generator, not
a hand edit; `[package] generated = "src/lucide"` already keeps `vilan fmt` off the file, so
nothing else about it moves. For std: no codemod — **curate**, module by module, using
the 118 as the floor and the docs as the ceiling.

**What is NOT affected**, and it is most of the corpus: the 131 single-file programs under
`vilan/test` (one of them uses `import pkg::`), the `.mjs` goldens, the split emission
golden, and every docs snippet that is one file. The flip's blast radius is the
multi-file packages and nothing else.

---

## 7. Tooling

### 7.1 Completion

Three surfaces, and the first two need only the bit.

- **Inside an import path.** `OriginListing::completions` (`completion.rs:3343`) offers a
  module's names through `module_importables`. With `exported` on the row it filters —
  except when the cursor sits after a reach marker, where it offers the private ones and
  nothing else. That is the marker earning its keep: `import a::{ #` is a discovery gesture.
- **Add-import.** `Document::import_candidates` (`document.rs:4605`) already filters
  `importable.kind != Reexport`; it gains `&& importable.exported`. `auto_import_completions`
  (`completion.rs:2414`) uses the already-loaded `Program` maps instead and gains the
  `exported_entities` test. Both skip private items — a private item is never *proposed*,
  which is the whole of "visibility gates completion".
- **After `impl ` in an import.** New: the module's impl SUBJECTS, from the same parsed AST
  `module_importables` walks (`collect_importables`'s neighbour `collect_impl_method_steers`
  already enumerates `(subject head, method)` pairs — the subject list is its first
  projection). After `)::`, the selected block's method names. Both answers come from the
  parse cache, no analyzer, which is the §2.1 property of this whole family.

### 7.2 Organize Imports under selectors

`prune_import_branch` (`formatter.rs:1454`) asks `keep(span)` of each terminal segment. A
selector is a new terminal kind, so the recursion gains one arm, and the predicate
(`Document::import_leaf_is_used`, `document.rs:4494`) gains one question for it:

> **A selector is used when the file resolves a method to an impl the selector admits.**

That is rule (2)'s question (`document.rs:4559` — "did this file resolve anything DECLARED
in the file this import reaches into?") narrowed from a FILE to an IMPL, and it is strictly
easier to answer, because the answer is the analyzer's own resolution rather than a
provenance guess. Which means **E168 and E169's fix is the same predicate this slice
generalizes**: `editor-34` builds `import pkg::a;` as the rewrite target this order, and the
visibility slice re-points it at `import pkg::a::{ (impl Style) };` — the precise, minimal
statement that says what the file actually needs. E168's own item says so ("re-pointed at
B318's selectors later"). Nothing in editor-34's work is wasted; it is the same `keep`
predicate with a narrower target.

**Canonical spelling and sort position** (B318's open (e), §10 e): selectors sort **after**
every name in a brace set, ordered by their rendered type text, methods inside a selector
sorted like any set. `branch_key` (`formatter.rs:429`) gains a `BranchKey::Selector(String,
Box<BranchKey>)` variant ordered after `BranchKey::Path`, which gives the ordering for free
in both `vilan fmt` and the organizer — they share the key, which is the property
`formatter.rs:1414`'s comment says must never break.

`#` is **kept as written**, on both paths. It is a fact about the author's intent, not a
formatting decision, and stripping it would silently re-arm the §5 warning.

### 7.3 `vilan fmt`

Unchanged in posture: fmt sorts and never prunes — `formatter.rs:1412`–`1420` states it
("Pruning is deliberately NOT part of `vilan fmt` (fmt has no analyzer), so it lives only
behind this entry point"). It gains only the renderers for the new statement shapes —
`export *;`, `export(in PATH) <item>`, `only`, `#`, the selector — and the sort key above.

### 7.4 The `pub` curated rule must be rewritten

`visibility_marker_rule` (`parsing.rs:255`) is the one curated rule whose text quotes a word
from the source, and every sentence of it becomes false on the day of the flip:

> "`pub` is not a vilan keyword: **a module's items are importable as they stand** —
> `import pkg::util::helper;` reaches `fun helper` with nothing marking it — so the fix is to
> delete the word. (`export` exists, but it **RE-exports** something this module imported…)"

Under B318 the fix is not to delete the word; it is to write `export`. The rewrite is a row
EDIT (the text changes, the firing does not), it must keep quoting the author's own marker
(`pub` or `public` — E109's F21), and because the message's FIRING is unchanged it does not
drag `-p vilan-lsp` along. This is the single most user-visible docs-adjacent edit in the
whole feature, because it is the message a Rust or Swift writer meets in their first hour.

### 7.5 `[doc(hidden)]` — the marker that already means this, and does not work

`[doc(hidden)]` parses (`parsing.rs:6091`), lands on `Function::doc_hidden`
(`analyzer.rs:742`, doc-commented "callable, but omitted from editor completion"), is
round-tripped by the formatter (`formatter.rs:3456`), is pinned callable
(`inference/generics.rs:3331`) — and **nothing in `vilan-ide` or `vilan-lsp` reads it**.
Grep: zero hits for `doc_hidden` in either crate. Meanwhile `docs/appendix/editor.md:87`
tells the reader to *"Use `[doc(hidden)]` to keep a name out of consumers' completion without
forbidding it"* — which is, word for word, B318's model, and which the tool does not do.

That is a defect independent of this feature (filed as a FIND in §11, F1) and a design
question for it. **Recommendation:** after the flip, `[doc(hidden)]` on a **top-level item**
is redundant with "not exported" and is refused with a steer naming `export`'s absence; it
**stays** on an impl or trait MEMBER, which has no `export` marker of its own and is exactly
where "public but not advertised" is still a real posture. That keeps one concept per
surface instead of two overlapping ones.

### 7.6 The editor page's dead-code paint

`docs/appendix/editor.md:83`–`88` rules that *"A `[library]` never fades a top-level item …
every top-level item is surface a consumer may import — which is what keeps you from having
to fork a library that forgot to export something."* Under B318 the second clause is still
true (the `#` reach is the no-fork guarantee, and it is now explicit rather than accidental)
and the first becomes **wrong for a private item**: an unexported, unreferenced top-level
item in a library IS dead, with no world the editor cannot see. That is a real new capability
for `dead-code-paint.md`'s family and it is out of scope here — FIND F2.

---

## 8. Rollout

**Recommendation: two releases, and the warning is the whole first one.**

| release | what ships | posture |
|---|---|---|
| N | the bit, `export`/`export *;`/`export(in PATH)`, the reach marker, `only`, both warnings, all tooling. **The default is still public**: an unexported item is importable and the plain reach WARNS. | additive; nothing in the estate stops compiling |
| N+1 | the plain reach of a **same-package** private item becomes an ERROR. A **dependency's** private item stays a marked-or-unmarked reach with no diagnostic, forever (RULED). | breaking, with one release of warnings behind it |

Three reasons for the shape. (a) The estate's own numbers (§6) say 294 items across six
packages move; one release of warnings is what turns that from a flag day into 44 one-line
edits plus one std curation pass. (b) The `#` reach means "error" never blocks anybody —
the escalation only forces the marker to be written, and the marker is a one-character edit
the quickfix performs. (c) `prelude.md` §12 sets the precedent for splitting an additive
half from a breaking half under separate CHANGELOG family markers, and this is the same
shape.

**std's own posture** (B318's open (h), §10 h). `prelude.md` §10.1 rules `prelude = false`
for std on greppability and bootstrapping, and the same argument runs here with the opposite
conclusion: **std curates from release N**, before anybody has to. std is the one package
whose import surface is a published contract, the 118 are already measured, and a std that
ships `export *;` would be teaching the codemod as the answer for a library — which it is
not. The 118 are the floor; the ceiling is whatever the `docs/std/` pages document, and the
difference between the two is the interesting part of the curation pass.

---

## 9. Slices for Order 35

Five build slices plus an estate sweep. Sizes are per the order's own vocabulary (S ≈ one
lane-day of a lane's capacity, M ≈ half a lane, L ≈ a lane).

**S1 — the bit and the warnings. M.**
`Importable.exported`; `collect_importables` stops discarding `Node::Export`;
`exported_entities`/`export_all_modules`/`export_scopes`; `export *;` (a node, a parser
lookahead, both rule-constant lists); `export(in PATH)` + the `export <expression>;`
refusal; the exposure warning in the post-build family; the plain-reach warning at the
import leaf and at a qualified path; three quickfixes (Export `S`, Export `hidden`, Import
as `#hidden`); completion + add-import + steer filters. Rows: 4 `NEW` (the exposure
warning, the plain-reach warning, `export` takes an item, a glob over an unexported module),
1 EDIT (`visibility_marker_rule`). Pins: the bit
round-trips through `module_importables`; an unexported item still imports (warning, not
error); `export *;` silences a module; `export(in mod)` hides one item under it;
`export(in pkg)` from a dependency warns at the consumer; the exposure warning in all seven
signature positions plus a body control; the dependency-`S` no-fix arm. **This slice alone
is shippable and is release N's additive half.**

**S2 — the reach marker. S.**
`Token::Hash`; row 335 retired; `HASH_IS_NOT_A_TOKEN`'s text re-homed to the css block
parser with the quickfix re-keyed; `#` on an import leaf; `lexical.md` §2.4's sentence.
Pins: `#hidden` imports and does not warn; `#` on an exported item warns ("already
exported — the marker is redundant"); `#333` inside a `css` block still reports the colour
rule with its fix; `#` outside an import and outside a css block still refuses.

**S3 — `only` and the selectors. L.**
`only` in `parse_import_statement`; the selector production with `_`; `file_impls`;
selector resolution as a second pass over a file's import list, in the importer's scope;
`impl PATH` through an alias and qualified; the E168/E169 predicate re-pointed at selectors;
the formatter's selector key and renderer; completion after `impl ` and after `)::`. Pins:
P7's exhibit refused under `only` and admitted without it; `(impl List<i32>)` serves a
`List<i32>` and not a `List<str>` in one file; `(impl List<_>)` serves both; `(impl _)`
admits the module's impls and no names; a method selector refuses `as`; a selector survives
Organize Imports when its impl is used and prunes when it is not; fmt/organize agreement
extended.

**S4 — the per-importer namespace. L.**
The import-site refusal replacing the cross-module half of
`check_duplicate_inherent_members`; `candidates_of` / `impl_members_for_bound` /
`impl_members_for` / `known_receiver_candidates` / `applying_implementations` file-scoped;
`Implementation` gains its declaring source; the transformer's two `select_member` sites
threaded with the ENCLOSING function's file. Pins: P8's pair refused at the second import
with the selector fix named; each module imported alone is clean; a selector resolves the
pair; §3.5's monomorphization pin (the declaring file's set, not the instantiating one);
B279's consumer list re-asserted under the filter. **Depends on S3 and on `solver-34`'s
B279 landing first.**

**S5 — docs. M.**
`names.md`: a new **§4.8 Visibility** (the bit, the four forms, the reach, the two
warnings); **§4.6 rewritten** (one namespace per type *per importing file*; the
declaration-site rule narrowed to one module; the selector as the disambiguator beside
`Trait::member`); §4.3 gains `only`, the selector and `::*`; §4.1's "a child pulls its
parent" gains the impl consequence P7 exhibits. `grammar.md` §3.2: the four new
productions. `tour/projects.md`: a visibility section beside the prelude key.
`appendix/editor.md`: the completion filter, the Organize Imports row, the `[doc(hidden)]`
determination. `appendix/errors.md`: the two warnings and the rewritten `pub` rule.
`prelude.md` §8's "No globs" annotated as overtaken. `glossary.md`: `export`, `private`,
`reach`.

**S6 — the estate sweep. M.**
The 73-file `export *;` codemod (kolt, the website, the examples, the templates, the
benchmarks) — including one line in `scripts/lucide.mjs` — and std's curation of its 118.
Runs after S1 and before release N+1's escalation, and is the slice that must not be folded
into another: it is a diff nobody reads and everybody has to be able to revert.

Order of build: **S1 → S2 → S3 → S4**, with S5 tracking each and S6 last. S1 and S2 are
independent of S3/S4 and could ship a release earlier if the owner wants the flip's warning
period to start sooner than the selectors are ready — which is the recommended shape,
because the warning period is the long pole and the selectors are the expensive one.

---

## 10. Open questions — B318's (a)–(i), answered

**(a) The per-importer method namespace: refused at the import or at the call?**
**At the IMPORT**, spanned on the second import statement, with a C3 note at the first and
the selector named as the fix (§3.2). One refusal per file per collision rather than one per
call; the fix lives where the message points; and it keeps the rule independent of which
code paths a file happens to exercise. `candidates_of` and `impl_members_for_bound` become
file-scoped through a `file_impls` map; the calling file comes free from the constraint's
anchor id (`analyzer.rs:2363`: "`call_id` is caller-side always"). The reference index is
unchanged except that selector elements must record references at their type and method
spans, or Organize Imports will delete them.

**(b) What a type-level selector unifies against.**
The **receiver's type at the call**, through the existing `impl_select::subject_applies`.
`(impl List<i32>)` admits the block `impl List<type T>` but that admitted block serves only
receivers unifying with `List<i32>` in that file; a `List<str>` receiver reports the ordinary
"has no method" with the import steer. `_` is a wildcard at any argument position;
`(impl _)` is every impl of the module (§3.4).

**(c) `export(in PATH)` general, or the two spellings?**
**General**, with `mod` and `pkg` as reserved path heads — the two spellings are the two
useful cases, but a general path costs nothing extra (the grammar is `"(" "in" path ")"`
either way, and `pkg`/`mod` are already root-shaped words) and it is the difference between
a feature and a pair of special cases. The visibility test is one module-path prefix
comparison, and `mod` means "this module and its inline `mod` blocks" while `pkg` means
"the item's own package" — matching `names.md` §4.2's existing roots.

**(d) Does `#` reach a private `mod`, a private impl, a private `::*` member?**
- a private **`mod`**: **yes** — `import pkg::a::{ #m };` and `import pkg::a::#m::helper;`.
  A `mod` is an importable row like any other (P6d) and the bit applies to it uniformly.
- a private **impl**, spelled `{ #(impl T) }`: **yes, and it is required** — an extension
  impl in a default-private module is invisible to a selector otherwise, and B318 already
  rules `export impl …` as the marker (which parses today, P10). `#(impl T)` is the reach
  for the one somebody forgot to mark.
- a private member reached by **`::*`**: **no.** A glob imports the exported set, full
  stop; a glob that reached private names would make the reach implicit, which §1 forbids.
  `import a::*;` plus `import a::{ #hidden };` is the spelling, and it reads correctly.

**(e) Organize Imports and the selector sort.**
Prune per selector, on the narrowed rule (2) of §7.2; E168's rewrite target becomes
`import a::{ (impl Style) };`; selectors sort **after** the names in a brace set, by
rendered type text, via a new `BranchKey` variant so fmt and the organizer keep sharing one
key. `#` and `only` are kept verbatim.

**(f) Completion in an import.**
After `impl ` — the module's impl SUBJECTS (the first projection of
`collect_impl_method_steers`'s pair list). After `)::` — the selected block's method names.
Both from the parse cache, no analyzer. And, new here: after a reach marker, the module's
**private** names and only those.

**(g) The default flip's rollout.**
**Warning-only for one release, then the error** (§8) — and the error is for a
SAME-PACKAGE private item only; a dependency's private item reached explicitly is never a
diagnostic, at any release, as RULED. 294 items across eight packages and one generated file
is what makes the warning release non-negotiable.

**(h) std's own posture.**
**std curates from release N.** The 118 measured cross-file imports are the floor;
`docs/std/`'s documented surface is the ceiling. std must not ship `export *;`: it is the
one package whose surface is a contract, and `export *;` as std's answer would teach the
codemod as the library idiom. This is the opposite conclusion to `prelude.md` §10.1's
`prelude = false`, and for a compatible reason — both rulings pick the option that keeps
std's own source honest about what it means.

**(i) Two same-named methods in ONE module's blocks.**
Reproduced (probe P9): `impl Holder<str> { fun join }` beside
`impl Holder<type T: Show> { fun join }` in one file is refused today at the second
declaration, `'join' is already defined for 'Holder<T>'`. **Recommendation: the
declaration-site rule STAYS for one module, narrowed to it.** Three reasons. (1) A file has
one import statement per module, so a selector cannot take one of the two without a
second, per-block spelling that B318 does not propose and that would have to name blocks,
not types. (2) `subjects_collide` (`analyzer.rs:7400`) already implements exactly the right
test — "can one value be served by both" — and it is a fact about the module, independent of
any importer. (3) The author of a module can always rename; the author of a file importing
two modules cannot. So: `check_duplicate_inherent_members` keeps its pairwise loop and gains
one filter — report only when both declarations are in the SAME file; cross-file pairs move
to §3.2's import-site refusal. `check_duplicate_block_members` (B84) and
`check_duplicate_trait_impls` (B98) are untouched.

### Further questions the probes raised

**(j) What does `export` mean on an `impl`?**
`export impl Holder<i32> { … }` parses today as a no-op (P10). Under B318 it must mean "this
block is selectable by an importer of this module", and its absence must mean "this block is
private to the module unless reached with `#(impl T)`". **But**: an impl for a type declared
in ANOTHER module, in a default-private module nobody imports, then contributes nothing to
anybody — which is a behaviour change for the P7 shape, and a welcome one. The paper
recommends it; it is called out because it is the single behaviour change in this feature
that a program can observe without writing any new syntax, and it deserves its own pin.

**(k) Does a `[library]`'s private item fade?** Out of scope; FIND F2 (§11).

**(l) Is a reach a REFERENCE for the purposes of rename?**
Yes, and it already is: `resolve_import` records a reference per path segment
(`record_reference`), and the marker adds no segment. Renaming `hidden` rewrites
`{ #hidden }`. Stated because a marker that broke rename would be worse than no marker.

**(m) What does the entry file do?**
An entry (`main.vl`, kolt's `client.vl`) is imported by nothing, so every one of its items is
private and none of them warns. Correct, and worth a pin: the flip must not make an
application's own entry noisy.

**(n) Does visibility travel through a re-export?**
`export import pkg::a::hidden;` publishes `hidden` from the re-exporting module
(`collect_importables`'s first branch, `analyzer.rs:4233`). **Recommendation: yes, and it is
the sanctioned way to widen** — a re-export is an explicit act of publication by a module
that can see the item, which is exactly `prelude.md` §8's "extend by re-export" mechanism one
level down. A re-export of a private item of ANOTHER module warns under §5 like any other
plain reach, and `export import pkg::a::{ #hidden };` is the marked form.

---

## 11. Finds — candidate tracker items

**F1 (editor / bug). `[doc(hidden)]` is parsed, stored, formatted and documented, and no
tool reads it.** `Function::doc_hidden` (`analyzer.rs:742`) says "omitted from editor
completion"; `docs/appendix/editor.md:87` tells users to reach for it; `grep -rn doc_hidden
crates/vilan-ide crates/vilan-lsp` returns **nothing**. Either completion filters on it or
the docs stop promising it. Independent of B318, and it should be settled BEFORE the
visibility slices, because §7.5's determination is about which of the two markers survives.
Evidence: the grep, `inference/generics.rs:3331` (`doc_hidden_method_stays_callable` — the
only pin, and it pins the half that works).

**F2 (editor / feature). A library's unexported top-level item becomes fadeable.**
`Document::unused_local_spans`'s doc comment (`document.rs:4194`–`4204`) rules top-level
items out of the fade with an argument that B318 dissolves: *"There is no visibility marker
in the language: `pub fun helper()` is a parse error … So a top-level `fun`/`struct`/`enum`/
`let` is module surface — a file the editor never analyzed may import it."* After the flip, a
private item is not module surface, and `docs/appendix/editor.md:83` ("A `[library]` never
fades a top-level item") is wrong for the private half. The catch is that the answer is
package-wide, not single-entry — which is exactly the "whole-package design that WOULD reach
the top level, and its cost" that comment already defers to. `dead-code-paint.md`'s family.

**F3 (diagnostics / bug). A malformed import statement reports at column 1.**
Probes P5, P5b, P5c, P6b, P10b and P11 all produce
`found 'import' expected an expression` **on the `import` keyword** — the whole statement
fails to parse and recovery reports the statement head, not the offending token. That is
today's behaviour for any import the grammar cannot read, and it is exactly the shape
`editing-dx.md` §4.4's gap anchor exists to avoid. Worth a row independent of B318; with
B318 it becomes acute, because the new import forms multiply the ways to mistype one.

**F4 (hygiene). `export <expression>;` compiles clean and means nothing.**
`export (helper);` and `export * helper;` both pass `vilan check` (P2d, P1b). `parse_export`
accepts any statement and the analyzer walks it, publishing nothing. One curated refusal
naming what `export` takes. Zero estate impact (grepped). Shippable today, independent of
B318, and §2.2 needs it anyway.

**F5 (docs). std's manifest quotes a stale census.** `vilan/std/vilan.toml` says std's
resolution is "264 names across 59 files"; measured at `e4d192e3` it is 664 top-level
declarations across 63. One comment edit.

---

## 12. Corrections to the brief

1. **Point 2's parenthetical is wrong about `#`.** "`#` is free lexically (the css lexer
   refuses `#333` inside a block only) — confirm" — it is not free; the refusal is
   unconditional and lives in `lexing.rs`, with a ledger row and an LSP quickfix keyed on it
   (§0.1, §2.3). The paper prices it and still recommends it.
2. **Point 6's "364 unexported top-level items" is not reproducible.** The measurement is
   664 declarations / 0 marked / **118** cross-file-imported (§0.3, §6). 118 is the number
   that sizes std's curation; 664 is the number that sizes nothing.
3. **Point 4's "after declaration hoisting, before bodies" is not where signature types are
   known.** The exposure warning's home is the post-`build()` check family at
   `analyzer.rs:53950`+, after `check_trait_conformance` (§4).
4. **Point 3's framing — "the check moves to the importer" — is right for the cross-module
   case and wrong for the same-module one.** §10 (i) recommends the declaration-site rule
   stays, narrowed to one module; only cross-module pairs move.
5. **Point 3 does not mention emission.** `impl_select::select_member` is called from the
   TRANSFORMER at monomorphization (`transformer.rs:8038`, `9576`) and picks the first
   maximum. Per-importer selection has to reach it, or B57's silent-pick hazard returns
   (§3.5). This is the largest single cost in the feature and it was not in the brief's
   sizing.

---

## 13. Rulings (owner, 2026-09-13)

1. **`#` — pay for it.** `#` becomes a token: the `HASH_IS_NOT_A_TOKEN` curated rule is retired,
   its quickfix (css-block §7.2 fix 1, keyed on the constant) is re-homed on the css block's own
   refusal, ledger row 335 is edited. §2.3's bill is the bill.
2. **`export` on an `impl` block means what it means on every other declaration.** An impl a
   consumer cannot see contributes NO methods to that consumer; AMBIENT impls do not come
   through either — the only reach is an explicit `#` import (`{ #(impl T) }`). §10 (j) is
   answered in the strict direction, which is also the one that makes the per-importer
   namespace (§3) exact: what a file can call is what it imported, exported or reached.
   **`[doc(hidden)]` is superseded** — its one purpose (technically available, absent from
   completion) is what a private item now is; S1 retires it (§11 F1: parsed, stored,
   formatted, documented, read by no tool).
3. **M67 (the base cache)** — the owner asked for a recommendation; recorded on the item.
4. **E163's local `npm ci`** — keep it no; the local gate stays network-free.

---

## 14. As built — Order 35 (2026-09-13, lanes visibility-a-35 and visibility-b-35)

**S1 (bit + warnings), S2 (`#`) and S3 (`only` + selectors) landed; S4 (the per-importer
namespace), S5 (docs beyond what each slice touched) and S6 (the estate sweep) are Order 36's.**

- **S1.** `Importable.exported: Visibility { Private, Exported, Scoped }`; `export *;` is a
  node (`Node::ExportAll`, a `*`+`;` lookahead — `export * helper;` is a real deref); `export(in
  PATH)` rides the export node as an optional scope with `mod`/`pkg` enforced exactly — a
  GENERAL path parses, stores and reprints but is ADMITTED (the subtree test needs source paths,
  which live on `Program`; B336). `export (helper);` / `export * helper;` are refused (B321).
  The exposure warning fires ONCE PER DECLARATION (not per position — B5; the fix is the same
  edit) in the post-build family, with the ruled wording; the plain-reach warning at the import
  leaf and, with a second wording, at a qualified path (there is no leaf to mark); a
  redundant-marker warning. Access is never gated. `[doc(hidden)]` retired outright (the fixed
  attribute ORDER changed: grammar.md, the marker gate, two doc fences).
- **Two rollout pieces §8 did not have, both built:** (a) the warnings are SILENT when the
  importing file is a `std_sources` member — std's 118 cross-file imports would otherwise fire in
  front of every user (800 warnings in the `todo` example alone); S6's curation lifts it; (b) a
  module with NO marker is UNCURATED and offers everything to completion, the add-import quickfix
  and the "import it first" steer — a strict gate on day one would hide every std name; the
  exemption gates the tooling and the exposure warning and deliberately NOT the plain-reach
  warning, which is what tells an author to curate. Also: a self-import never warns; a REFUSED
  import earns no visibility warning on top. Consequence: the exposure warning fires zero times
  on today's estate; the plain-reach warning fires kolt 272 / website 130 / benchmarks 34 /
  examples 56 / std 0, every package still compiling.
- **§9 S1's pin "`export(in pkg)` from a dependency warns at the consumer" contradicts the
  ruling** (a dependency's private item is no diagnostic) and was not built. §4's "Export `S`"
  workspace edit is NOT expressible — `Document::QuickFix` is single-file (E177); the two
  same-file fixes ship (`Import as #leaf`, `Delete the #`), the Export fixes are message steers.
  vilan-ide's two completion filters are not yet on the bit (E178).
- **S2.** `Token::Hash`; row 335 DELETED and a new `flagship` row for the css block's `#333`
  refusal (the head changed, so an edit was not available); `#` on an import leaf; a `#` on an
  exported item warns (redundant). Taking `#` forced one line in vilan-ide's exhaustive
  `Token` match.
- **S3.** `only` as a trailing modifier (contextual, like `as`); the `(impl TYPE)` selector as a
  brace-set element AND an arm in `parse_namespace_path_inner` (§2.5 named only the set); `_`
  cost ZERO grammar — B294's anonymous binder already is the hole; a selector COMMITS at its
  two-token gate so a typo reports inside it; six curated rule statements, no ledger rows (row
  229's population — §9's "one row" for the `as` refusal was wrong). `Implementation.source`
  STORED; `file_impls` as `ImportImplRestriction`/`ImportImplSelector` + the post-build pass
  `check_impl_selector_admission`, subjects walked in the importer's scope, admission unified
  BOTH WAYS (`subject_applies(impl, selector)` for the concrete reading, `subject_applies(selector,
  impl)` for the placeholder — §3.4 was incomplete); the FILE-LEVEL admission refusal (one row).
  E168/E169's predicate re-pointed (`ModuleRescue::{No, Module, Selector}`; the rewrite is
  `import a::{ (impl T) };` when one subject); `BranchKey::Selector` after names (§7.2 as
  written); completion after `impl ` and `)::`. `#(impl T)` is NOT built (needed `Token::Hash`
  from the other lane; the seam is `at_impl_selector`). A selector-only statement's module is
  looked up by FILE NAME (`module_source_by_name`) because `resolve_import` never walks a
  statement that binds nothing — S4 should give `resolve_import` a `bind: bool`. A selector
  admitting no impl is silent (B338).
- **What S4 receives:** `Implementation.source`, `Program::import_impl_restrictions` and
  `impl_selector_members`; `check_impl_selector_admission`'s `restricted` map IS `file_impls`
  inverted — lift it into a `Program` field, feed `candidates_of` / `impl_members_for_bound` /
  `applying_implementations`, delete the post-hoc call check for the import-site collision
  refusal; and the `export impl` ruling (an invisible impl contributes no methods; no ambient
  impls) is RECORDED on the bit but its enforcement is S4's.
- **Finds filed:** B335 (`source_of` lies on a module segment when `x.vl` and `x/` coexist —
  Organize Imports probably wrong there), B336, B338, E177, E178, N84 (`cargo test` vs nextest
  shared state in two prelude-shaped `modules::` tests).

## 15. As built — Order 36 (2026-09-14, lanes visibility-36 and sweep-36)

**S4 landed whole: the per-importer namespace, the import-site refusal, the
`export impl` gate, `#(impl T)`, and B330's call refusal.** With it, B335, B336
and B338. S6 (the estate sweep and std's curation) and S5 (the docs) landed from
sweep-36, merged last. B318's arc is complete.

- **The map is the `restricted` map, INVERTED.** §3.3 wrote `file_impls:
  HashMap<SourceId, Vec<usize>>`, which every lookup would have to SEARCH; the
  question every consumer actually asks is "may THIS file take THIS member", and
  the map that answers it in one probe is keyed by the pair. `ImplAdmission`
  carries `restricting` (files whose statements restrict anything),
  `admitted: (importer, declaring file) -> member ids` (absence = unrestricted,
  an EMPTY entry = `only`), `selector_of` for the message, plus `hidden` and
  `reached` for the export gate. `check_impl_selector_admission` split into
  `build_impl_admission` — run at the TOP of `post_analysis_passes`, ahead of
  `context::thread_contexts` and of emission, because both read it — and
  `check_call_site_admission`, which is what the old pass's second half became.
- **The analyzer's in-walk lookup is NOT scoped, and cannot be.** A selector's
  question is `impl_select::subject_applies`, which reads a FINISHED program, so
  `impl_member_candidates` stays program-wide and the call is CORRECTED after the
  build rather than resolved differently. §3.4's "the calling file comes free
  from the constraint's anchor id" is right about the id and wrong about the
  timing: the in-walk resolution happens before any of this exists.
- **File-scoped, each named:** `candidates_of`, `impl_members_for`,
  `impl_members_for_bound`, `known_receiver_candidates` (which derives the file
  itself from its call id), `impl_select::applying_implementations`,
  `select_member`, `select_implementation`, `applying_trait_ids`. Consumers
  threaded: `context::analyze`'s `dispatch_candidates` and `dispatch_admits`,
  `const_eval`'s three site scans, `dispatch_refine::refined_edges`, and the
  transformer's four lookups. `const_eval`'s refusal DIRECTION survives an
  admission filter, which the receiver narrowing it still refuses does not: an
  impl the calling file cannot reach has no runtime path there to refuse.
- **§3.5 built as written.** The transformer carries `current_admitting_file`,
  set from `enter_instance(function_id)` — the DECLARING file. The pin that
  fails under "the instantiating file's set" is
  `b318_a_monomorphized_body_resolves_under_the_file_that_declared_it`, and it
  needed a new `transform_package` helper: a `select_member` decision is
  emission's, so analysis alone cannot see it. One thing §3.5 did not foresee: a
  body-less call target stops being only a compiler bug, so `select_member_here`
  records the losing lookup and the never-silent check (B55) reports it in the
  author's terms instead of "internal: … please report this program".
- **§3.5 met the codecs at the merge.** A derived `Wire` visitor is a generic
  body declared in `wire.vl`, so at monomorphization it resolves under
  `wire.vl`'s set — and a codec block the curation had left private
  (`json`'s `JsonWriter`/`JsonReader`, `binary`'s `BinaryReader`, `fetch`'s
  three body blocks) contributed nothing to it: sixteen inference pins went red
  on the merged tree and green once those blocks were `export impl`. The rule
  is the one the paper wanted; the lesson is that a curation decided on a
  9b22ec36 tree has to be re-decided on the tree it merges into.
- **The import-site refusal.** `check_duplicate_inherent_members` keeps the
  same-module case and banks the rest as `Program::cross_module_collisions`;
  `refuse_imported_member_collisions` decides them against what each file's
  statements carried. Two geometries: both blocks imported reports at the LATER
  statement with a note at the earlier; one block the file's OWN reports at the
  single import with the note at the declaration, which is the sentence the
  duplicate family has always shown (`a_duplicate_static_across_modules_names_
  the_other_module` passes unedited). A compiler-synthesized member belongs to
  the file whose attribute generated it (`declaring_module_source`), so a backed
  enum's `value` colliding with a hand-written one stays a same-module pair.
- **`export impl` and `#(impl T)`.** `Implementation` gains `impl_id` and
  `module_scope`; `Program::hidden_impls` is the blocks a CURATED module does not
  export, computed at the commit; the export gate runs BEFORE the selector filter
  in both predicates, and the call earns its own refusal ahead of the selector arm
  ("widen your selector" is bad advice about a block no unmarked selector widens
  onto). The parser seam is `parse_namespace_single_path`, which owns `#` and
  routes back to `parse_impl_selector` past it; `at_reach_marked_impl_selector`
  lets the outside-a-set rule earn the same refusal. §14's "the seam is
  `at_impl_selector`" was right.
- **BREAKING, one program in the tree.** `vilan/macro_std/src/meta.vl` and
  `build.vl` are curated and their ten extension blocks carried no marker, so
  every `[derive(..)]` in the estate lost the builders' methods. They are
  `export impl` now. Nothing else: std's only curated files declare no impl, and
  everything the Order 35 migration touched carries `export *;`.
- **B330 refused at the call, narrowly.** The pair is banked only where
  `bound_argument_positions_overlap`'s `(Generic, Generic)` arm admits it
  (`bounds_differ_only_at_binder_bounds`), and decided by
  `impl_select::declaring_maxima` — how many maxima declare the member for this
  receiver under THIS file's set. Asking the SELECTION ORDER rather than the
  subjects is what keeps A86's `Read<type I>` beside `Read<Option<type I>>` —
  std's own `flatten` pair — out of it: tier 1 ranks them, so there is one
  maximum and nothing to report. Two fixes: a selector at the import across
  modules, B315's "narrow one bound" within one.
- **`resolve_import` gained `bind: bool`** and `module_source_by_name` is
  deleted. A selector-only statement is queued with `bind: false`, walks, records
  each segment's reference and stops one line short of binding. The file-name
  match it replaces was a host-dependent string comparison (the Order 35 seal fix
  9b22ec36) that also guessed between two packages of the same shape.
- **Finds closed beside it:** B335 (the namespace placeholder range is corrected
  in place, which also restores `source_ranges` to disjoint and keeps
  `source_lookup` on its binary search — three vilan-lsp pins had recorded the
  lie and now record the fix), B336 (`export(in pkg::a)` was read as
  `export(in pkg)` because the reserved heads were matched on `scope.first()`;
  the subtree test is now a post-build pass over banked rows), B338 (two rows at
  the selector). E178's `Program` surface — `exported_entities` and
  `curated_modules` — lands here too, for vilan-ide's fourth completion consumer.
- **Rows:** 9 `NEW` (491–499). **Cost, measured** on kolt's client leg (`vilan
  check`, CPU user+sys, 15 interleaved pairs against 9b22ec36): **+2.4 % on min,
  +1.0 % on median**, after hoisting the per-file question
  (`ImplAdmission::restricts`) out of the per-block loops — it read +3.9 % /
  +2.3 % before. kolt pays: its `views.vl` writes `import std::map::{ (impl
  Map<_, _>) };`, the estate's first selector.

**S6 — the estate sweep and std's curation (sweep-36, merged last).** The
non-std codemod is 24 files in one commit: the examples' 12 modules, the three
`vilan init` scaffolds, the corpus's three module-directory fixtures, and the
six benchmark modules whose Order-35 markers moved down from above the module
comment into E181's slot. The set was taken from the WARNING rather than from
§6's census — every package checked file by file, the declaring module read off
each `is not exported by` — which is why `examples/fullstack/common` is absent:
its only cross-file reach is from a path dependency, and that is silent by the
ruling. kolt was verified read-only and warns 0; the website's seven modules and
the playground's two were marked by the integrator (website 130 → 0). **std's
curation is 548 of 856 declarations exported and 308 private**, over 63 files:
33 modules answer yes for every item and take the bare `export *;` (162 items),
27 are curated declaration by declaration (694 items, 386 marked), and
`lib.vl`/`prelude.vl`/`web.vl` declare nothing and are untouched. 319 `impl`
blocks carry the marker, because an impl a consumer cannot see contributes no
methods and a curated module has to say which blocks it publishes. Criterion (a)
was read out of `check_plain_reaches` with the suppression lifted — **152 items
across 45 modules**, not §6's 118, which was measured before std grew — and the
ceiling was the reference plus the estate's imports. The exposure warning is what
made the pass honest: it fired 44 times over three rounds and every firing was a
curation error fixed by exporting the type (`arena::Slot` behind `Arena`'s
field, `fetch::Header` behind http's `Request`, `style::Condition` behind every
condition constructor), never by quieting the check. The `std_sources` arm of
`check_plain_reaches` is deleted; std is now held to the rule every other
package is held to, and `every_std_module_is_clean_under_full_scan` is the proof,
green under both layers with the plain-reach and exposure warnings at 0 — after
the integrator re-ran the curation over the MERGED tree, where `cell_identity`
(M66), the four codec blocks above and `swap_split` (A99's fold) had arrived
private. **Two S1 defects were in the way.** `export` on a transparent wrapper —
`export [derive(Wire)] struct Handle` — parsed, formatted and round-tripped
through `Importable.exported` and was dropped in entity-id space, because the
wrapper mints an entity of its own and the `Node::Export` arm recorded that one;
ten of std's marked declarations, `time::Duration` and `rpc::RpcError` among
them, could not be exported until `transparent_declarations` was added. And
`needs_semicolon` excluded every `Export`, so `export let x = 1;` printed without
its terminator, failed to re-parse, and the formatter BAILED — handing back the
whole file unformatted, silently, since a bail is not a diagnostic and `vilan
fmt --check` reads a bailed file as already-formatted. §6's own numbers are
stale by three orders: std is 741 declarations by the manifest's grep, 856
counting every declaration kind, and its manifest now carries a recipe that
survives the marker. `::*` is NOT built and not documented.
