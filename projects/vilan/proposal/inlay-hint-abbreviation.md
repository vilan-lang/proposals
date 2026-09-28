# Inlay-hint abbreviation — a type shown by the trait it is used as (E227)

Tracker E227. Written by lane papers-43 of Order 43 on 2026-09-28, against vilan
`next` @762c6aa5 (content-identical to `main` @1a33340f, the v0.41.1 fold;
`vilan 0.41.1 (1a33340f2)` in both install locations). Nothing in the compiler
tree changed. Every claim about what the tree does is a line that was read (cited
`file:line`, paths under `vilan/` unless they start `crates/`) or a probe that was
run, and says which.

Probes: `scripts/integration/sweeps/order43/papers-43/probes/e227/` —
`run_all.sh <scratch>` copies the probes to a scratch dir and checks each; output
in `run_all.out`. The probes render the full type of every pipeline node through a
deliberate annotation mismatch (`let shown: i32 = selected;`), and test whether
`~` lexes anywhere.

Related: A124 (the push-pull pipeline — why a derivation's type spells its whole
upstream), A123 (`switch` / `and_then` as cold nodes), I5 (the iterator adapters as
structs), E213 / E221 (`[internal("…")]`, the precedent for an attribute that
changes only what the EDITOR does), B382 (`[deprecated]` on a struct), E206 (the
per-call-site label table, the precedent for a second label map), E121 (the landed
snapshot the hints are served from), `trait-objects.md` §0 (why `dyn` is part of a
type's printed name).

---

## 0. The ask, and the answer up front

The owner, after kolt's v0.41.0 migration: kolt's `selected_command`
(`src/command_palette.vl:210`, a `combine(..).map(..)`) hints as
`Map<Combine<(List<Command>, usize)>, (List<Command>, usize), Option<Command>>`,
and the one fact a reader wants — it is a source of `Option<Command>` — is the last
argument of four.

**The answer.** An inlay hint is a reading aid, not the type. It may abbreviate
where hover, completion, signature help and every diagnostic keep the full type.
The abbreviation is declared by the type's author with one attribute,
**`[hint(Source<U>)]`** on `struct Map<S, T, U>`, and renders with a marker that
cannot be written as a type: **`: ~Source<Option<Command>>`**. The rules are:

1. **No heuristic.** A type without the attribute renders exactly as it does today.
2. **The abbreviation never promises what the value lacks.** It is printed only
   when the instantiated type is ADMITTED by an impl of the named trait
   application, which is the solver's own question (§4.2). Otherwise the hint
   falls back to the full type. This is Q3's answer. The item's first reading,
   "the impl must be unconditional over the type's own parameters", would exclude
   every node the item was filed for (§6, Q3).
3. **Recursive.** A hinted node nested inside any type abbreviates in place:
   `(~Source<Option<str>>, i32)` (Q2).
4. **Inlay hints only.** A hover shows the full type and, beneath it, the
   abbreviation (Q5). The hint's own tooltip carries the full type. A setting
   `vilan.inlayHints.abbreviate` (default on) switches abbreviation off live,
   without re-analysis (Q4).

std carries **fourteen** attributes, not "~10": six reactive nodes and eight
iterator adapters (§5). The iterator adapters are the case rust-analyzer's
`impl Iterator<Item = ..>` hint was invented for, and the item did not list them.
Two of the item's candidates are corrected. `RemoteSource<T>`'s application is
`Source<Option<T>>` (`std/src/rpc.vl:3591`), not `Source<T>`, and it stays
unabbreviated as a leaf (§5.3). `Memo` implements no trait at all
(`std/src/memo.vl:44-48`), so it has nothing to be shown as.

Sizing **S–M**, about 3 days in one editor lane (§8). This paper is R-f's
deliverable. The build waits for Order 44 and for the marker ruling (Q1).

## 1. Ground truth — where a hint comes from today

**The label is rendered by the analyzer, once, as a string.** At the end of
analysis the analyzer pre-renders a label for every typed expression, variable
and parameter into `Program::expr_types: HashMap<Id, String>`
(`crates/vilan-core/src/analyzer.rs:63575-63614`; the field and its doc at
`analyzer.rs:54711-54715`). Every label goes through the same renderer,
`pretty_print_type` (`analyzer.rs:53020`) → `pretty_print_type_inner`
(`analyzer.rs:53138`), whose struct arm prints the name and the arguments
verbatim (`analyzer.rs:53310-53317`). The type tables do not leave the analyzer.
The LSP holds strings and `TypeId`s (`expr_type_ids`, `analyzer.rs:54731-54735`),
but it has no renderer. So **the abbreviation has to be rendered in the analyzer
too**. The LSP cannot re-derive it from a string.

**The hint reads that string verbatim.** `Document::inlay_hints`
(`crates/vilan-lsp/src/document.rs:3848-3874`) walks `program.variables`. It skips
annotated bindings and bindings outside the entry file, and emits
`": {label}"` from `expr_types` at the end of the name span. It runs once per
landed analysis: `capture_landed` stores its answer in the snapshot
(`document.rs:1960`). The request handler (`crates/vilan-lsp/src/main.rs:3627-3674`)
re-maps the landed hints, withholds those inside the edit window, and sends
each as an `InlayHint` with `text_edits: None` and `tooltip: None`
(`main.rs:3661-3669`). The provider is gated by `vilan.inlayHints.enabled`
(`main.rs:62`, parsed at `main.rs:95-101`; declared in
`editors/vscode/package.json:101-105`).

**The hover reads the same string.** `binding_hover` (`document.rs:3572-3599`)
fences `let name: {label}` from `expr_types`. Every other surface (completion
detail, signature help, member hover) and every diagnostic is rendered through
the same `pretty_print_type`.

**What the reader sees today** (`run_all.out`, each a full type the renderer
produced):

| written | rendered |
|---|---|
| `combine((names, index)).map(\|(list, at)\| list.get(at))` | `Map<Combine<(List<str>, usize)>, (List<str>, usize), Option<str>>` |
| `index.distinct().map(\|i\| i + 1)` | `Map<Distinct<SignalCell<usize>, usize>, usize, usize>` |
| `flag.switch(\|on\| if on { a } else { b })` | `Switch<SignalCell<bool>, bool, SignalCell<i32>, i32>` |
| `maybe.map(..).flatten()` | `FlattenOption<Map<SignalCell<Option<i32>>, Option<i32>, Option<SignalCell<i32>>>, SignalCell<i32>, i32>` |
| `[1, 2, 3, 4].iter().map(..).filter(..).take(1)` | `Taken<Filtered<Mapped<ListIterator<i32>, i32, i32>, i32>, i32>` |
| `[1, 2].iter().zip(..).enumerate().skip(1)` | `Skipped<Enumerated<Zipped<ListIterator<i32>, ListIterator<i32>, i32, i32>, (i32, i32)>, (usize, (i32, i32))>` |
| `(selected, 3)` | `(Map<Combine<(List<str>, usize)>, (List<str>, usize), Option<str>>, i32)` |

There is a second cost the item did not name. The reactive node is called `Map`,
and so is the hash map (`std::map::Map<K, V>`). The analyzer's own
never-determined steer suggests `` `: Map<str, i32>` `` as its example annotation
(`run_all.out`, `nodes3.vl`). A hint that opens with `Map<` is ambiguous on its
face, and the abbreviation removes the word.

## 2. Which trait — the author declares it

A type implements many traits, and three ways of choosing one were considered
and rejected in the item. The paper keeps the rejection and adds a fourth
option.

- **(a) A heuristic** ("the trait with a type argument", "the first trait the doc
  names", "the only exported trait impl"). Every one picks wrong somewhere, and
  silently. `KeyedCell<K, T>` implements both `Source<List<T>>` and
  `DeltaSource<List<T>, SeqOp<T>>` (`rpc.vl:4252`, `rpc.vl:4276`). `ListCell<T>`
  implements `Source`, `Signal`, `SequenceCell` and `DeltaSource`
  (`delta.vl:900`, `:915`, `:933`, `:956`).
- **(b) The root of the supertrait chain.** Right for `Map`, wrong for any type
  whose root trait is `PartialEq`.
- **(c) The use site.** The binding's later uses would decide the hint. That
  needs a second pass, and the hint would change as the code below it changes.
- **(d) A marker on the IMPL instead of the type**
  (`[hint] export impl Map<type S: Source<type T>, T, type U> with Source<U>`).
  It is the cheapest spelling. The trait application is already written, the
  parameters are in scope, and the impl's bounds are exactly the admission
  condition. It is **rejected** for two reasons. First, the fact moves off the
  declaration a reader of the type is looking at. Second, `[deprecated]` and
  `[internal]` on an impl are refused precisely because "nobody names" an impl
  (`vilan/docs/spec/grammar.md`, the attribute-prefix paragraph after the
  `[deprecated]` rule). A label that belongs to the TYPE should sit on the type.
  §4.2's admission check gives the struct spelling everything (d) gives, at the
  cost of one declaration-time match.

**Rec: the struct or enum declares it** — `[hint(Trait<args>)]`, with the
arguments written in the type's own parameters. One line per type, no guessing,
and a package author has the same lever for their own combinators.

## 3. The attribute

### 3.1 Syntax and placement

```vilan
/// `map` as a NODE: the upstream and the transform, nothing else.
[hint(Source<U>)]
export struct Map<S, T, U> {
	up: S,
	transform: |T| U,
}
```

It is one more member of the item-label prefix that E221 and B382 built.
`parse_item_labels` (`crates/vilan-core/src/parsing.rs:7573-7587`) reads
`[deprecated]? [internal]? [platform]?` ahead of a struct, an enum, a trait or a
module `let`, into the boxed `Labels` node (`crates/vilan-core/src/node.rs:1398-1412`).
The hint joins as `[deprecated]? [internal]? [hint(..)]? [platform]?`. It is a
label ABOUT the declaration, so it sits with the other two and ahead of
`[platform]`, which is about analysis. The new field is
`Labels::hint: Option<Spanned<Node<'src>>>`, and its argument is parsed by the
ordinary `parse_type` (`parsing.rs:5237`). It is the first built-in attribute
whose argument is a TYPE: `[derive(..)]` takes names, and `[deprecated]` /
`[internal]` take strings. The attribute stands before the `<S, T, U>` it
mentions. Resolution happens in the analyzer, in the declaration's generic
scope, exactly as a field type does. That scope-before-declaration shape is the
one Rust's `#[..]` attributes have.

The three-place rule: `hint` is added to `KNOWN_ATTRIBUTE_MARKERS`
(`parsing.rs:1108-1122`). `grammar_sync.rs` holds both highlighting grammars to
that table (`crates/vilan-cli/tests/grammar_sync.rs:16-23,61`), and the
appendix's contextual-word line gains the word (`vilan/docs/spec/appendix.md:36-40`).
`hint` stays an identifier everywhere else, as every attribute name is.

### 3.2 What the analyzer checks at the declaration

All of the following are refusals with a steer, and none of them is a warning:

1. **The host is a struct or an enum.** A `[hint]` on a trait, a module `let`, a
   function or an `impl` is refused. There is no type for it to abbreviate.
2. **The argument is a trait application**, not a nominal type, a `dyn` type or a
   tuple. The message names what was written.
3. **Its arguments mention only the declaration's own parameters and concrete
   types.** A free name is refused, as a field type naming an undeclared
   parameter is.
4. **Some impl provides it.** At least one impl of that trait, whose subject's
   head is this type, must provide that trait application under the parameter
   mapping of its subject. This is a STRUCTURAL match over the impl table, not a
   solver query. Under the struct's bare parameters the query would fail for
   every reactive node, because `Map<S, T, U>` states no bound and its impl asks
   `S: Source<T>` (§6, Q3). The refusal reads
   `` `[hint(Source<U>)]`: no impl of `Source<U>` for `Map<S, T, U>` ``. This is
   what stops a hint from naming a trait the type never implements, which is the
   `Signal`-for-`Map` mistake the item's own sketch made and corrected.
5. **At most one** `[hint]` per declaration.

The table is `Analyzer::hint_attributes: HashMap<Id /* struct|enum */, (Id /* trait */,
Vec<TypeId> /* args, in the declaration's generics */)>`. It sits beside
`item_labels` (`analyzer.rs:4287`, filled at `:31733`, `:31958`, `:32091`).
It is one table and one resolution site.

## 4. Rendering

### 4.1 Where it applies

**Inlay hints only.** Hover (§6, Q5), completion detail, signature help, member
hover, the declaration labels and every diagnostic keep `pretty_print_type`'s
full rendering. A diagnostic states what a type IS, and a refusal that said
`~Source<i32>` where the solver compared `Map<..>` would be the
one-representation-two-meanings confusion that `Type::Dyn`'s printing arm is
written against (`analyzer.rs:53327-53340`: "a diagnostic that said `Source<i32>`
for an object and for a bound would be the … confusion trait-objects.md §0 is
about, printed").

### 4.2 The rule

`pretty_print_type_inner` gains a mode flag, `Abbreviate`, threaded like
`depth`. Only the struct and enum arms (`analyzer.rs:53310`, `:53342`) read it.
When the type's id is in `hint_attributes`, and the instantiation is ADMITTED by
an impl of the hinted application, the renderer:

1. pushes `~`;
2. pushes the trait's name;
3. renders the trait's arguments under the substitution that maps the
   declaration's parameters to this instantiation's arguments, recursively in the
   same mode.

Admission is the solver's existing question: does this concrete instantiation
satisfy that impl's bounds? The query exists in two forms,
`type_implements_trait` / `type_implements_trait_at` (`analyzer.rs:7904`,
`:18393`), and `impl_select::select_implementation`
(`crates/vilan-core/src/impl_select.rs:967`). Otherwise the renderer prints the
full type, which is today's text. A non-admitted instantiation is unusual,
because each node is built only by a combinator whose own bounds imply the impl's
(§5.1's "built by" column). The fallback exists so the abbreviation can never
lie, not because anyone will see it often.

One wrinkle for the build. `type_implements_trait_at` takes `&mut self`
(`analyzer.rs:18393-18398`), and the label loop borrows the analyzer immutably
(`analyzer.rs:63583-63597`, M32's borrow). The build answers the admission
question per `(struct id, argument ids)` into a small cache BEFORE that loop, or
it uses the immutable `select_implementation`. Either way it is one lookup per
distinct hinted instantiation, not per binding.

### 4.3 Storage — a second label map, sparse

The abbreviated label is rendered only for `analyzer.variables` (the only ids
`inlay_hints` reads, `document.rs:3856`). It is stored only where it DIFFERS from
the full label, in `Program::hint_labels: HashMap<Id, String>`. That is E206's
precedent: `call_signature_labels` "exists only where the substitution CHANGED
the rendering" (`analyzer.rs:54717-54729`). A program with no hinted type pays
one map lookup per variable. `inlay_hints` then returns
`(offset, label, full: Option<String>)`. The snapshot keeps both forms, and the
handler picks one per `vilan.inlayHints.abbreviate` (§6, Q4) and puts the full
type in the hint's `tooltip` whenever it abbreviated.

The abbreviated hint's `text_edits` stays `None` (`main.rs:3664`). An editor that
"inserts the hint on double-click" must never write `~Source<..>` into a file. It
would not lex (§6, Q1), and inserting the full type would be the only honest
edit. A future "insert inferred type" action reads `expr_types`, never
`hint_labels`.

## 5. std's attributes

### 5.1 The fourteen

Every row was read at the cited struct and impl. "Unconditional" means the
impl's header asks nothing of the struct's own parameters beyond what the struct
declaration itself states. That is the item's literal test, and §6 Q3 explains
why it is the wrong test.

| type (struct at) | the trait impl (at) | attribute | impl's bounds on the struct's parameters | unconditional? | built by |
|---|---|---|---|---|---|
| `Map<S, T, U>` (`reactive.vl:1830`) | `impl Map<type S: Source<type T>, T, type U> with Source<U>` (`:1835`) | `[hint(Source<U>)]` | `S: Source<T>` | no | `map` (`reactive.vl:2105`, in `impl type S: Source<type T>` `:2099`) |
| `Switch<S, T, I, U>` (`:1872`) | `… with Source<U>` (`:1877`) | `[hint(Source<U>)]` | `S: Source<T>`, `I: Source<U>` | no | `switch` (`:2112`); `flatten` over a source of sources (`:1721`) |
| `Combine<T: (2..)>` (`:1924`) | `impl Combine<type T> with Source<T>` (`:1928`) | `[hint(Source<T>)]` | none (the struct's own `T: (2..)`) | **yes** | `combine` (`:1613`) |
| `FlattenOption<S, I, U>` (`:1954`) | `… with Source<Option<U>>` (`:1958-1960`) | `[hint(Source<Option<U>>)]` | `S: Source<Option<I>>`, `I: Source<U>` | no | `flatten` over `Source<Option<..>>` (`:1748`) |
| `AndThen<S, T, I, U>` (`:2005`) | `… with Source<Option<U>>` (`:2010-2012`) | `[hint(Source<Option<U>>)]` | `S: Source<Option<T>>`, `I: Source<Option<U>>` | no | `and_then` (`:1769`) |
| `Distinct<S, T>` (`:2067`) | `impl Distinct<type S: Source<T>, type T: PartialEq> with Source<T>` (`:2071`) | `[hint(Source<T>)]` | `S: Source<T>`, `T: PartialEq` | no | `distinct` (`:2166`, in `impl type S: Source<type T: PartialEq>` `:2163`) |
| `Mapped<I, T, U>` (`iterator.vl:189`) | `impl Mapped<type I: Iterator<T>, type T, type U> with Iterator<U>` (`:194`) | `[hint(Iterator<U>)]` | `I: Iterator<T>` | no | `Iterator::map` (`iterator.vl:13`) |
| `Filtered<I, T>` (`:203`) | `… with Iterator<T>` (`:208`) | `[hint(Iterator<T>)]` | `I: Iterator<T>` | no | `filter` (`:18`) |
| `FilterMapped<I, T, U>` (`:229`) | `… with Iterator<U>` (`:234`) | `[hint(Iterator<U>)]` | `I: Iterator<T>` | no | `filter_map` (`:28`) |
| `Taken<I, T>` (`:256`) | `… with Iterator<T>` (`:261`) | `[hint(Iterator<T>)]` | `I: Iterator<T>` | no | `take` (`:35`) |
| `Skipped<I, T>` (`:271`) | `… with Iterator<T>` (`:276`) | `[hint(Iterator<T>)]` | `I: Iterator<T>` | no | `skip` |
| `Enumerated<I, T>` (`:291`) | `… with Iterator<(usize, T)>` (`:296`) | `[hint(Iterator<(usize, T)>)]` | `I: Iterator<T>` | no | `enumerate` |
| `Zipped<I, J, T, U>` (`:307`) | `… with Iterator<(T, U)>` (`:312`) | `[hint(Iterator<(T, U)>)]` | `I: Iterator<T>`, `J: Iterator<U>` | no | `zip` |
| `Chained<I, J, T>` (`:326`) | `… with Iterator<T>` (`:332`) | `[hint(Iterator<T>)]` | `I: Iterator<T>`, `J: Iterator<T>` | no | `chain` |

The iterator adapters are declared without `export` but published by
`iterator.vl`'s `export *;` (`iterator.vl:3`). Their names reach every user's
hints, as the probe shows.

**What the fourteen do to the table in §1:**

| full | abbreviated |
|---|---|
| `Map<Combine<(List<str>, usize)>, (List<str>, usize), Option<str>>` | `~Source<Option<str>>` |
| `Map<Distinct<SignalCell<usize>, usize>, usize, usize>` | `~Source<usize>` |
| `Switch<SignalCell<bool>, bool, SignalCell<i32>, i32>` | `~Source<i32>` |
| `FlattenOption<Map<..>, SignalCell<i32>, i32>` | `~Source<Option<i32>>` |
| `Taken<Filtered<Mapped<ListIterator<i32>, i32, i32>, i32>, i32>` | `~Iterator<i32>` |
| `Skipped<Enumerated<Zipped<..>, (i32, i32)>, (usize, (i32, i32))>` | `~Iterator<(usize, (i32, i32))>` |
| `(Map<Combine<..>, .., Option<str>>, i32)` | `(~Source<Option<str>>, i32)` |

kolt's `selected_command` becomes `: ~Source<Option<Command>>`.

### 5.2 The one change std makes to its docs

`Map`'s doc comment (`reactive.vl:1822-1829`) and each adapter's doc gain nothing.
The attribute is its own documentation. `vilan/docs/std/reactive.md`'s node
section gains one sentence saying that the editor shows a node by the trait it
is used as, and names the attribute for a package author.

### 5.3 What carries no attribute, and why

The rule of thumb for std, and the one the book should give a package author, is
this: **hint a type whose parameters carry its PROVENANCE (an upstream type), not
a leaf whose name is information.** Abbreviating a leaf throws away the one
thing its hint says.

- `SignalCell<T>` (`reactive.vl:1353`), `ListCell<T>` (`delta.vl:723`),
  `KeyedCell<K, T>` (`rpc.vl:4009`): writable leaves. `~Source<List<User>>` for
  a `KeyedCell<UserId, User>` hides both the key and the fact that it can be
  written.
- `RemoteSource<T>` (`rpc.vl:3524`; `with Source<Option<T>>` at `:3591`, not
  `Source<T>` as the item sketched) and `KeyedSource<K, T>` (`rpc.vl:4362`;
  `with Source<Option<List<T>>>` at `:4423-4425`): mirrors. The name says the
  value is remote, which is exactly what a reader of an `[rpc]` call site wants
  to see.
- `Memo<K, V>` (`memo.vl:44`): implements no trait (its only impl is inherent,
  `memo.vl:48`). §3.2's check 4 would refuse a hint on it.
- `Selector`, `Resource`, `Draft`, `Optimistic` (`reactive.vl:1681`, `:2208`,
  `:2548`, `:2764`): inherent impls only. There is nothing to abbreviate to.
- `ListIterator<T>`, `IteratorFromFn<T>`, `Range` (`iterator.vl:160`, `:139`,
  `range.vl:9`): short leaves already.

## 6. The owner's questions, answered

**Q1 — the marker's spelling.** Candidates: `~T`, `impl T`, `«T»`.

- `~` **lexes nowhere in vilan.** `let x: ~i32 = 1;` and `let x = ~1;` both stop
  at the lexer with "found '~' expected a token" (`run_all.out`, `tilde.vl`,
  `tilde2.vl`). A reader cannot mistake `~Source<i32>` for something they could
  write. A copy-paste of it fails loudly and at once, not at a type check three
  lines later. It is one ASCII character, so it costs the hint nothing.
- `impl` is a HARD keyword (`crates/vilan-core/src/lexing.rs:75`) with a meaning
  (a block). Rust readers will take `impl Source<i32>` for Rust's
  return-position `impl Trait`, which vilan does not have, and the question "why
  can't I write the type the editor showed me" follows. It also costs five
  characters.
- `«T»` is not typable on most keyboards, renders unevenly across fonts, and
  would be the only non-ASCII glyph the toolchain prints.

**Rec: `~`** (`: ~Source<Option<Command>>`), with the hint's tooltip carrying the
full type (§4.3).

**Q2 — does a nested node abbreviate?** **Rec: yes.** The substitution is the
renderer's recursion, so it costs nothing extra. `(Map<..>, usize)` →
`(~Source<A>, usize)`, `Option<Map<..>>` → `Option<~Source<A>>`, and a source of
sources → `~Source<~Source<i32>>`. A hinted node's own upstream arguments
disappear, because the outer abbreviation swallows them. A non-hinted outer type
keeps its shape and abbreviates only its hinted arguments.

**Q3 — may the attribute name a trait the type implements only conditionally?**
The item's proposed test was "the impl must be unconditional over the type's own
parameters", with a note to check that `Map`'s blanket qualifies. **It does
not**, and neither does any other node except `Combine`. §5.1's table has 13 of
14 impls asking a bound the struct declaration does not state: `Map`'s impl asks
`S: Source<T>` (`reactive.vl:1835`), while `struct Map<S, T, U>` states none
(`:1830`). Taken literally, the test abolishes the feature. **Rec: the test is
per instantiation, at render time** (§4.2). The attribute may name any trait
application that SOME impl of the type provides (the declaration check, §3.2 (4)).
The hint abbreviates an instantiation only when the solver admits it under that
impl's bounds, and prints the full type otherwise. That is strictly stronger
than the unconditional test, and it is the property the owner actually asked
for: the abbreviation never claims a trait the value lacks.

**Q4 — an editor setting to turn it off.** **Rec: `vilan.inlayHints.abbreviate`,
boolean, default `true`, applied live.** It is declared in
`editors/vscode/package.json` beside `vilan.inlayHints.enabled` (`:101-105`), and
parsed in `Config::from_settings` beside `/inlayHints/enabled` (`main.rs:95-101`)
as `/inlayHints/abbreviate`. Because the snapshot stores both labels (§4.3),
toggling needs no re-analysis. The config is read per request
(`did_change_configuration` replaces it whole, `main.rs:3234-3247`), so the
next hint request answers in the new mode. `did_change_configuration` sends
no refresh today. The build adds one `inlayHint/refresh` (`main.rs:2219`'s arm)
when the `abbreviate` value changes, so hints already on screen switch at once. `false` shows today's full types.

**Q5 — does hover show both?** **Rec: yes, when they differ.** The fence stays the
declaration with the full type. `binding_hover` is unchanged
(`document.rs:3578-3586`). Beneath the fence (and above the doc comment), one
plain line reads *Shown as `~Source<Option<Command>>` (`[hint]` on `Map`)*. It
sits outside the fence because the fence is vilan and `~` is not. The reader who
wonders what the hint means hovers the name, and so learns the mapping. The
hint's tooltip answers the reverse question from the hint itself.

## 7. Pins

The three LSP pins the item names, as `document.rs` tests beside
`inlay_hints_show_inferred_types_only` (`document.rs:14983`):

1. `inlay_hint_abbreviates_a_hinted_node`:
   `let s = combine((a, b)).map(..)` hints `: ~Source<Option<str>>`.
2. `inlay_hint_abbreviates_a_nested_node_inside_a_tuple`:
   `let p = (s, 3)` hints `: (~Source<Option<str>>, i32)`.
3. `inlay_hint_leaves_an_unhinted_type_whole`: a `SignalCell<i32>`, a
   `List<i32>` and a `RemoteSource<User>` hint exactly as they do today, and a
   program with no hinted type produces a `hint_labels` table that is empty.

Beside them:

- The analyzer's five refusals (§3.2), one pin each.
- `config_parses_inlay_hints_abbreviate` next to `main.rs:754-824`'s config pins.
- A hover pin: both lines appear, and only when they differ.
- A handler pin: an abbreviated hint carries the full type as `tooltip` and no
  `text_edits`.
- An iterator pin: `.iter().map(..).take(1)` hints `: ~Iterator<i32>`.

## 8. Sizing

**S–M, about 3 days, one lane (editor), Order 44.**

| piece | where | size |
|---|---|---|
| `[hint(..)]` in the label prefix, `Labels::hint`, `KNOWN_ATTRIBUTE_MARKERS` + the grammars + the appendix line | `parsing.rs`, `node.rs`, the two tmLanguage copies, `appendix.md`, `grammar.md` §3.3 attributes | S |
| `hint_attributes` + the five declaration checks | `analyzer.rs` (the `item_labels` sites) | S |
| the `Abbreviate` mode, the admission cache, `hint_labels` | `analyzer.rs` renderer + label loop | S–M |
| hint/tooltip/setting/hover | `document.rs`, `main.rs`, `package.json` | S |
| std's 14 attributes + the one doc sentence | `reactive.vl`, `iterator.vl`, `docs/std/reactive.md` | S |
| pins (§7) | `document.rs`, `main.rs`, analyzer tests | S |

There is no golden impact. No diagnostic's text changes, and the JS and native
output are untouched, since the attribute is erased after analysis. One CHANGELOG
entry is additive.

## 9. Not in scope

- Diagnostics that print a long node type. A refusal must say what the type IS.
  If kolt's diagnostics read badly with long node types, that is a separate
  diagnostics-standard question (eliding repeated arguments, say), not this
  attribute.
- Abbreviating a signature's declared return type (`fun map<U>(..): Map<S, T, U>`
  in completion detail). The declaration is the contract, and it stays exact.
- A user-side override per binding. The annotation `let s: Map<..> = ..` already
  suppresses the hint (`document.rs:3857`).

## 10. For the owner

- **Q1** the marker: **rec `~`**.
- **Q2** nested nodes: **rec yes**, recursive.
- **Q3** conditional impls: **rec per-instantiation admission at render time**,
  plus a structural declaration check. The unconditional-only rule would exclude
  13 of the 14 std types.
- **Q4** `vilan.inlayHints.abbreviate`: **rec default on, live**.
- **Q5** hover shows both: **rec yes**, full type in the fence and the
  abbreviation beneath it. The hint's tooltip also shows the full type.
- **Q6** (new): the attribute's host. **Rec: the struct or enum**
  (`[hint(Source<U>)] struct Map`), over a marker on the impl (§2 (d)).
- **Q7** (new): include the eight iterator adapters in std's set. **Rec: yes.**
  They are the textbook case.

**Side find while probing (for the solver, not this paper).**
`maybe.and_then(|v| SignalCell::new(Some(v)))` leaves `and_then`'s `U` unbound:
"the type of 'y' is never fully determined: `AndThen<SignalCell<Option<i32>>,
i32, SignalCell<Option>, U>`" (`run_all.out`, `nodes5.vl`). The same closure
returning `SignalCell::new(Some(1))`, or a pre-typed cell, resolves. The closure
parameter's type (from the impl's `S: Source<Option<T>>` binder) does not reach a
generic constructor's argument in the body. It rendered `SignalCell<Option>` with
the argument lost. It is unfiled as far as a tracker grep shows.
