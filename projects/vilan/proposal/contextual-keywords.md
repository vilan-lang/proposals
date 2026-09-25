# Contextual keywords — which reserved words a name may use, and where (B414)

Tracker B414. Written by lane papers-42 of Order 42 on 2026-09-25, against vilan
`next` @d65d4e75 (`vilan 0.40.0 (d65d4e759)`, both install locations). Nothing in
the compiler tree changed; every claim about what the language does today is a
probe that was run or a line of the tree that was read, and says which.

Probes: `scripts/integration/sweeps/order42/papers-42/probes/b414/` —
`run_all.sh <scratch>` regenerates everything, output captured in `run_all.out`:
the 44-word × 9-position name matrix (`gen.sh`), the precedent program for the
contextual words that already exist (`precedent.vl`), a JSON key the derive
cannot reach (`json_type.vl`), bindgen over keyword-named members (`w.d.ts`), a
native field that cannot be emitted (`self_field.vl`), and a derive-hygiene
failure (`wire_shadow.vl`).

Related: B413 (`resource` → `[resource]`, R-c: this train or v0.42.0), B415
(`mod self;`, `self` a reserved module name), `css-block.md` §5.4 and Q3 (the
ruling that took `css` as a HARD keyword), `lazy.md` §5 (why `lazy` became hard:
"grep-verified free of identifier uses", not a contextual-vs-hard ruling),
N113 (the `void` member rule), N63 (the tour's reserved-word section), M86 (the
borrowing read that wanted `with` and is `peek`; RULED 2026-09-25: `peek`
keeps its name), `grammar.md` §3.2 (`as` and `only`, contextual since E142).

---

## 0. The ask, and the answer up front

The owner's note: not every keyword needs banning as an IDENTIFIER — `with`,
`as`, `in`, `layer`, `sync`… should be usable as names where the grammar
cannot confuse them; the DECLARATION keywords stay reserved.

**The answer.** Of the 35 words `lexing.rs::KEYWORDS` reserves, **six can become
contextual at no grammatical cost** — `with`, `borrows`, `own`, `dyn`, `lazy`,
and `resource` once B413 lands — and a seventh, `jump`, can too, against the
item's "control flow stays hard" line (Q1). The other 28 stay HARD, each for a
reason the grammar states (§3). Three words the item names are already not
keywords: **`as` and `sync` have been contextual since E142 / the closure-type
marker**, and **`layer` is no word the compiler knows** — no keyword, no
contextual gate, no production (§1).

The mechanism is not new. vilan already has seven contextual words (`as`,
`only`, `context`, `sync`, `self`, `Self`, `void`) plus the attribute names and
jump targets, and the probe program `precedent.vl` uses four of them as names
beside their keyword readings in one file and prints `42`. What makes it cheap
is one property of the grammar (§2): **no expression ever puts two names side
by side**, so a contextual word followed by a name is the keyword and followed
by anything else is a name.

The ask has a wider half the item did not name (§5): at MEMBER positions — after
a `.`, as a declared field, as a method name inside an `impl` — every word, hard
or not, is unambiguous today, and the one real collision in the estate is
there: a JSON document with a `"type"` key cannot be decoded by
`[derive(Json)]` at all, because no field can be called `type`. That is Q2.

## 1. Ground truth — what is reserved today

**The table.** `crates/vilan-core/src/lexing.rs::KEYWORDS` (the one source of
truth; `grammar_sync.rs` generates both editor grammars from it and gates the
bytes) holds 35 spellings, and the lexical spec §2.2 prints the same 35:

```text
async  await  borrows  const  css   dyn   else   enum   export  external
false  for    fun      if     impl  import  in   is     jump    lazy
let    macro  match    mod    mut   null  own    resource  ret  struct
trait  true   type     use    with
```

**The contextual words that already exist.** `grammar_sync.rs::CONTEXTUAL_WORDS`
lists `context`, `sync`, `as`, `self`, `Self`, `void` — each pinned to lex as
`Token::Ident`, with a test that fails the day one is promoted ("move it to the
keyword check"). `grammar.md` §3.2 adds `only` (the trailing import modifier).
The lexical spec §2.2 lists `context`, `sync`, `void`, `self`, `Self`, the
attribute names and the jump targets `break`/`continue` — and **omits `as` and
`only`**, which `grammar.md` documents as contextual (a doc drift, §12 find 5).

**The probe matrix** (`run_all.out`): each word at nine name positions — a
`let` binding, a parameter, a struct field (declared, initialised and read), a
method (declared and called), a free function, an enum variant, a closure
parameter, an import alias, a type name.

| words | let | param | field | method | function | variant | closure | alias | type |
|---|---|---|---|---|---|---|---|---|---|
| all 35 keywords | X | X | X | X | X | X | X | X | X |
| `context` `sync` `as` `only` `self` | ok | ok | ok | ok | ok | ok | ok | ok | ok |
| `Self` | ok | ok | ok | **X** | ok | ok | ok | ok | ok |
| `void` | X | X | ok | ok | X | ok | X | X | ok |
| `layer` | ok | ok | ok | ok | ok | ok | ok | ok | ok |

So a keyword is refused at EVERY position today, including the ones where no
production could start with it (a field declaration, the name after `.`). The
`void` row is N113's deliberate rule (a binder named `void` could never be read
back; a member may be called `void` because it is "reached through a receiver,
not through the atom production" — the same argument §5 makes for every word).
The `Self` method cell is a find (§12 find 4).

**Premise corrections to B414's title:**

1. **`as` is already contextual** — `import std::io::print as as;` compiles
   (`precedent.vl`), and E142 made it so on purpose.
2. **`sync` is already contextual** — `fun apply(sync: (sync |i32| i32), …)`
   compiles: a parameter named `sync` whose type opens with the `sync` marker.
3. **`layer` is not a keyword, not a contextual word, and heads no
   production** — `grep` finds it only in comments (`std/src/ws.vl:1` "the frame
   layer") and in `source_layers`/`layer_platforms`, internal Rust names. Nothing
   was ever renamed around it.
4. **`in` is not a "contextual" candidate the grammar gets for free** — it sits
   BETWEEN two names (`for x in xs`), which is the one shape §2's property does
   not cover (§3.3).

## 2. The property that makes it cheap

A contextual keyword costs lookahead only where the word could ALSO start a
name's use. vilan's expression grammar never juxtaposes two names: an operand
is followed by an operator, a `.`, a `(`, a `[`, a `!`, a `?`, a `,`, a `;`, a
closer or a block — never by an identifier. So:

> **The LL(2) rule.** A contextual word followed by a NAME (an identifier, or a
> keyword that begins the word's own production) is the keyword. Followed by
> anything else, it is a name.

Where it holds, and where it does not:

- It holds for every word whose keyword reading is a PREFIX that must be
  followed by a name or a fixed keyword: `own x`, `lazy let`, `lazy x`,
  `dyn Trait`, `jump break`, `resource struct` (§4).
- For words that sit AFTER a type in a signature or an item head (`with`,
  `borrows`, and the existing `context`), the rule is POSITIONAL: the parser is
  already in `parse_impl`/`parse_trait` after the subject, or in the function
  header after the return type, where no name can appear.
- It FAILS for words that prefix an EXPRESSION that may itself open with `(`,
  `-` or `[`: `ret -1` (return minus one, or `ret` minus one?), `await (x)`
  (await a parenthesis, or call `await`?), `const (a)`, `async (x)`. Those stay
  hard (§3.2).
- It FAILS for words that sit BETWEEN two names — `x is Some(..)`,
  `for x in xs`, `(U in T: …)` — because there the word's neighbours ARE names.
  Position still disambiguates each one (`for_header_binder_width` scans for the
  token), but at a cost no one has asked to pay (§3.3).

**The one place a type is followed by a name**, checked because `with` and
`borrows` follow types: a closure LITERAL's return annotation, `|x: i32|: i32
context + x`, where the body begins right after the type. Probe `juxt.vl`
prints `42` with a local named `context` as that
body. Neither `with` nor `borrows` has a reading there (a closure literal takes
no `borrows` clause and is no item head), so the positional rule is unaffected;
the EDITOR's regex must not paint there (§6).

Element heads and `css` bodies are already exempt: `grammar.md` §3.6 spells an
element or property name as `NAME { "-" NAME }` where NAME is "an identifier or
any keyword" — `<input type("text")>` has always worked.

## 3. The classification — all 35

| class | words | why |
|---|---|---|
| HARD — declaration | `fun` `struct` `enum` `trait` `impl` `type` `mod` `macro` `import` `use` `export` `external` `let` `mut` (14) | the item's own line; each heads a statement or an item (`starts_item` / `starts_statement_or_item`, `parsing.rs:676–720`), and those two functions are the parser's RECOVERY sync points |
| HARD — expression heads | `if` `else` `for` `match` `ret` `await` `async` `const` (8) | each begins a secondary expression; `ret`/`await`/`async`/`const` prefix an expression that may open with `(` or `-` (§2) |
| HARD — between names | `in` `is` (2) | §3.3 |
| HARD — literals | `true` `false` `null` (3) | a literal is an atom; `null` also names the bootstrap `struct null` |
| HARD — by ruling | `css` (1) | `css-block.md` Q3, RULED 2026-08-28 "Take the keyword": the headed form needs `css [` and `css :root`, which collide with an index and a path |
| CONTEXTUAL — proposed | `with` `borrows` `own` `dyn` `lazy` (5) | §4 |
| CONTEXTUAL — with B413 | `resource` (1) | §4.6 |
| CONTEXTUAL — asked | `jump` (1) | §4.7, Q1 |

14 + 8 + 2 + 3 + 1 + 5 + 1 + 1 = 35.

### 3.1 `external` stays hard, although it could go

`external` is a declaration modifier (`external fun`, `external struct`,
`resource external struct`) and is LL(2)-decidable exactly like `lazy`. It stays
HARD because it is on the owner's declaration side of the line, it is a
recovery sync point, and no program has wanted a name `external`. Recorded so
that the choice is visibly a choice.

### 3.2 The expression heads

`jump` is the only expression head whose keyword reading is ALWAYS followed by a
name (`jump break`, `jump continue` — `parse_jump`, `parsing.rs:4752`, reads
`eat_ident` and nothing else), which is why it is §4.7 and not here. Every other
head in this row takes an arbitrary expression after it, and the LL(2) rule
cannot tell `ret (x)` from a call.

### 3.3 `in` and `is`

Both can be made contextual — `for_header_binder_width` already locates the
header's `in` by scanning, `is` is only read after a complete operand, and B248/
B259 make a block-like form COMPLETE at its brace so nothing can hang an `is` on
it. But `for in in ins { }` is grammatical under that rule, the for-header's
recovery (which reports an unreadable binder BY NAME, B368) would lose the token
it scans for, and nothing in the estate or the tracker has ever wanted either
name. JavaScript, Rust, Kotlin, Swift and Python all keep both hard. **Rec:
hard.**

## 4. The six (and a seventh) — productions, name positions, lookahead

For each: the productions the word starts or joins (read in `parsing.rs` at the
lines named), the positions where it would become a NAME, and the test the
parser uses.

### 4.1 `with`

- **Keyword reading:** the implemented-trait list of an `impl` head
  (`parse_impl`, `:6454`) and the supertrait list of a `trait` head
  (`parse_trait`, `:6487`). Nowhere else — not in bounds (`T: A + B`), not in
  expressions.
- **Becomes a name at:** every position — binding, parameter, field, method
  (`list.with(|xs| …)` is M86's original spelling), free function, module.
- **Test:** positional. After `parse_type()` returns the impl subject, or after
  the trait's generic parameters, `peek == Ident("with")`. A type path never
  consumes a following identifier (`type-path = IDENT { "::" IDENT }
  [generic-args]`), and a bound list ends at it (`impl type T: Foo with Bar`).
- **Touch points:** `parsing.rs` 2, `completion.rs::head_is_not_an_initializer`
  (`Token::With` is one of the heads after which a `{` is not a struct literal —
  it becomes `Ident("with")` in head position), `keyword_lexeme`/`KEYWORD_DOCS`.

### 4.2 `borrows`

- **Keyword reading:** the return clause `: T borrows p` (`:5886`), a function
  header only.
- **Becomes a name at:** every position.
- **Test:** positional — after the return type, before `context` and the body.
  This is exactly `context`'s position one token later, and `context` is
  contextual today (`parse_context_clause`, `:5576`, "so `std::context` paths
  stay legal").
- **Touch points:** `parsing.rs` 1, `formatter.rs` 2, `completion.rs` 1.

### 4.3 `own`

- **Keyword reading:** a parameter's convention prefix, `own x: T`
  (`parse_function_parameter`, `:6009`), for a `fun` and a closure literal.
  One parser site in the whole file.
- **Becomes a name at:** every position, including a parameter NAMED `own`
  (`fun f(own: Owner)`) and a closure parameter (`|own| own.dispose()`).
- **Test:** LL(2) at a parameter head: `own` followed by an identifier, `mut`,
  `lazy`, `(` or `[` (a binder) is the convention; followed by `:`, `,`, `)`,
  `|` it is the parameter's name. The existing recoveries (`own mut x`,
  `own lazy x`) read the same tokens they read today.
- **Why it matters:** the tour (N63) singles it out — "`own` … and `jump` …
  both are short, ordinary English words that make good variable names in every
  other language" — and `own` is the natural name of the thing A124's rulings
  keep asking for (the owner a leaf is subscribed under).

### 4.4 `dyn`

- **Keyword reading:** a TYPE position only, `dyn type-path` (`parse_dyn_type`,
  `:5304`, reached from `parse_type`'s head check at `:5270`).
- **Becomes a name at:** binding, parameter, field, method, function, module.
  NOT a type name (types are Capitalized; §11 rec keeps `dyn` the keyword at
  every type-position head except `dyn::`).
- **Test:** in type position, `dyn` followed by `::` is a path head (a module
  named `dyn`); otherwise the keyword. Outside type position it never had a
  reading.

### 4.5 `lazy`

- **Keyword reading:** (a) a statement/expression head, `lazy let` / `lazy mut`
  (`parse_secondary_inner` dispatch `:2678`, `parse_let` `:4776`), including
  after labels (`labelled-let`); (b) a parameter prefix, `lazy message: str`
  (`:6007`, `:6029`).
- **Becomes a name at:** every position.
- **Test:** LL(2). At a statement head, `lazy` + `let`/`mut` is the modifier;
  `lazy` + identifier is today's "the binder word is missing" recovery
  (`parse_let`: `lazy name = …` is taken as `let` and reported) — two juxtaposed
  names are never an expression, so that reading survives; anything else is an
  expression statement over a name (`lazy = 3;`, `lazy.force()`). At a
  parameter head, as `own`.
- **Recovery:** `lazy` is in `starts_statement_or_item` (`:709`). The sync
  check becomes `Ident("lazy")` followed by `let`/`mut` — one token of
  lookahead in a function that already peeks.
- **History:** A100 made it hard on 2026-09-15 with "grep-verified free of
  identifier uses" (`lazy.md` §5); the only program in the tree that used it
  (`vilan/test/reactive-on-change.vl`'s `let lazy = …`) was renamed `quiet`.
  Swift, whose `lazy` this is, keeps it a contextual declaration modifier.
  The v0.41.0 notes will say "`lazy` is a keyword" (CHANGELOG `:799`); a later
  demotion makes that entry's migration unnecessary, never wrong.

### 4.6 `resource` — with B413

- **Keyword reading today:** a type-declaration modifier, `resource struct`,
  `resource enum`, `resource external struct` (`:6270`, `:6345`), plus a steer
  for a misplaced one (`parse_misplaced_resource`, `:7712`).
- **After B413** the modifier is the attribute `[resource]` and the keyword has
  no reading of its own. **For the dissolution to free the word, B413 must
  REMOVE `resource` from `KEYWORDS`** and keep its refusal/steer of the old
  spelling by LL(2) (`Ident("resource")` followed by `struct`/`enum`/`external`
  at a statement head). If B413 keeps `Token::Resource` in the lexer to hang the
  steer on, the collision A124 met (the constructor `resource(..)`) survives the
  dissolution — see §12 find 1; this is time-sensitive for syntax-42.
- **Becomes a name at:** every position; A124's pending family can spell its
  constructor `resource(..)` beside the type `Resource<T>` (the TYPE name was
  never blocked — identifiers are case-sensitive, `Resource` is not `resource`).

### 4.7 `jump` — asked (Q1)

- **Keyword reading:** `jump break` / `jump continue` at a secondary-expression
  head (`:2677`, `parse_jump` `:4752`).
- **Becomes a name at:** every position — `fun jump(self)` on a game entity,
  `let jump = …`.
- **Test:** LL(2): `jump` + identifier is the statement; anything else is a name.
- **The cost:** one worse message — `jump;` (target forgotten) would read a
  binding named `jump` and, when none is in scope, report "cannot find `jump`"
  instead of today's "expected a jump target". A one-line rule restores it (a
  bare `jump` that resolves to nothing names the two targets).
- **Against it:** the item lists control flow as hard, and `jump` is control
  flow. For it: its production is a keyword + a name, the one shape the LL(2)
  rule was made for, and the tour already apologises for the word.

### 4.8 The positions, collected

| word | binding | param | field | method | function | module | type name | test |
|---|---|---|---|---|---|---|---|---|
| `with` | yes | yes | yes | yes | yes | yes | yes | position (item head) |
| `borrows` | yes | yes | yes | yes | yes | yes | yes | position (after return type) |
| `own` | yes | yes | yes | yes | yes | yes | yes | LL(2) at a parameter head |
| `dyn` | yes | yes | yes | yes | yes | yes | **no** | LL(2) in type position (`dyn::` is a path) |
| `lazy` | yes | yes | yes | yes | yes | yes | yes | LL(2) at a statement or parameter head |
| `resource` (B413) | yes | yes | yes | yes | yes | yes | yes | LL(2) steer only |
| `jump` (Q1) | yes | yes | yes | yes | yes | yes | yes | LL(2) at an expression head |

## 5. The member positions — the wider question (Q2)

§4 moves SIX words. A different cut moves ALL of them at a narrower set of
positions: the positions a name is reached through a receiver or a path, never
through the atom production. N113 already states the principle for `void` ("a
member — a struct field, a method — may still be called `void`: it is reached
through a receiver").

**The member positions:** the name after `.` and `?.` (field read, method
call, a markup head's `.member`); a field in a struct declaration; a field in a
struct literal WITH `=` (`S { type = t }`); a method's name after `fun` inside
an `impl` or `trait` body (the parser already knows — `within_member_body`); a
path segment after `::` (`S::type(..)`, `E::If`, an import path's inner
segments). Not: a shorthand init field (`S { type }` reads a binding), a free
function, a binding, a parameter, a module declared with `mod`, an import LEAF
without `as` (it binds a name). Each member position is entered after a token
that commits (`.`, `::`, `fun` inside a member body, `{`/`,` in a struct body),
so no lookahead is needed at all — the parser takes `eat_member_name` (any
identifier or keyword) where it takes `eat_ident` today.

**The evidence that it is wanted — three exhibits, all probed:**

1. **A JSON `"type"` key is unreachable by `[derive(Json)]`.** There is no field
   rename attribute, so a struct must spell the key as a field, and `type` is
   refused as one. `json_type.vl`: `Event { type_ = "click" }.to_json()` prints
   `{"type_":"click","id":1}`, and decoding `{"type":"click","id":1}` answers
   `refused: missing field type_`. Every discriminated-union protocol a program
   talks to (webhooks, JSON-RPC notifications, ActivityPub, LSP payloads) has
   this key. The member tier fixes the declaration, the read (`e.type`) and the
   literal (`Event { type = t }`).
2. **bindgen escapes host members with `_`** — `bindgen.rs::RESERVED` suffixes
   a TS member that lands on a reserved word, so the DOM's `Event.type` binds as
   `external fun type_(self): str` (`examples/canvas/canvas.vl:34`, seven sites
   there) and a TS `with()` as `with_`. Under the member tier a METHOD may be
   called `type`, and the escape is needed only for free functions.
3. **The macro API names a field `type_`** — `macro_std::meta`'s field and
   parameter records (`meta.vl:56`), read 37 times across `rpc.vl` (21),
   `json.vl` (9), `default.vl` (1) and `meta.vl` (6).

**What does NOT become legal under either tier:** kolt's lucide icons
`import_()` and `type_()` (`src/lucide/lib.vl:7822`, `:15039`) are FREE
functions of hard words, and stay escaped.

**The cost.** Every emitter must survive a member named for any word — the JS
emitter already escapes JS-reserved names; `vilan-rust::sanitize` raw-escapes
Rust keywords, and **cannot** raw-escape `self`/`Self`/`super`/`crate` (§12
find 2, a live defect today). Derive macros that bind a LOCAL per field
(`json.vl:995`, `let {field.name} = …::rebuild(deserializer);`) would emit
`let type = …` and must bind fresh names instead — the same change that fixes
§12 find 3. The formatter, the LSP's member completion and the book grammars
paint member names already (semantic `Property`/`Method` tokens, §6).

## 6. The editor's painting rule

**The rule: a contextual keyword used as a name paints as a name; in its
keyword position it paints as the keyword.** Two layers deliver it, and the
second is already right by construction:

1. **Semantic tokens** (`vilan-lsp` `Document::semantic_tokens`, `:3874`) come
   from the ANALYZED program: declarations, parameters, identifier-sized
   reference entities, method-call and field-read names (`Method`/`Property`).
   A word in its keyword position binds no entity and gets no token; a word used
   as a name gets its entity's token, which VS Code draws over the TextMate
   layer. An unresolved reference stays untokenized and keeps TextMate's paint —
   which is why layer 2 must not paint a bare name as a keyword.
2. **TextMate and highlight.js** (the book has no semantic layer) must paint
   the keyword reading only where it is one. The existing three show how:
   `context` is anchored after a type-ending character and before a name,
   `sync` only right after `(`, `as` with an identifier character before it and
   a name after it (`vilan.tmLanguage.json` keywords patterns 5–7, hand-written
   beside the generated lists). The LL(2) rule translates directly: **paint `W`
   as a keyword only where it is followed by whitespace and a name** —
   `\b(own|lazy|dyn|jump)\b(?=\s+[A-Za-z_])` — and, for the two positional
   words, also preceded by a type-ending character:
   `(?<=[A-Za-z0-9_>\)\]])\s+(with|borrows)\b(?=\s+[A-Za-z_(&|])`. `let with = 1`,
   `x.with(f)`, `fun own(self)` and `own: Owner` all fail the lookahead and stay
   names. The closure-literal body after a return type (§2) is the one place the
   `with|borrows` pattern could misfire (`|x|: T with` over a local named
   `with`) — rare, and the semantic layer overrides it in the editor.

`grammar_sync.rs` moves each demoted word from `KEYWORD_ROLES` to
`CONTEXTUAL_WORDS` (whose own test then pins it to lex as `Ident` and to be
coloured by at least one grammar), and `regex_matches` pins each anchored rule
on both sides (`impl A with B` paints; `let with = 1` does not).

**Completion and hover.** `completion.rs::keyword_lexeme` is exhaustive over
`Token` and keys `KEYWORD_DOCS`; a demoted word loses its token arm, so hover
on `with` in an `impl` head needs the raw-parse read `keyword_hover` already
uses for markup (a per-request parse that knows the head's span). `as` and
`context` have no keyword hover today — the precedent is to lose it; the rec is
to keep it (S1 carries it). Keyword completion is position-aware already
(`with` is offered after an impl subject), so it needs no change beyond the
token-to-text read.

## 7. The estate — what becomes legal

Searched: std, macro_std, `vilan/test`, examples, docs, templates, benchmarks,
the `.vl` consts in Rust tests, vilan-website, vilan-playground, kolt
(read-only), for `<keyword>_` escapes and for the records of every rename made
around a keyword (CHANGELOG, tracker, sweeps).

| spelling today | would have been | legal under | record |
|---|---|---|---|
| `ListCell::peek` | `with` | §4 (and §5) | M86; RULED 2026-09-25: `peek` keeps its name — nothing to undo |
| `reactive-on-change.vl`'s `quiet` | `lazy` | §4 | A100's entry (`CHANGELOG.md:799`); a test local, nothing to undo |
| `Resource`'s respelled constructor | `resource(..)` | §4.6 (B413) | A124 Q-name, RULED; reactive-42 respells it now and may revert after B413 + B414 |
| `Length::raw(..)`, `.text` | `Length::css(..)`, `.css` | §5 only | css-block Q3; `css` stays hard at atoms — nothing to undo |
| `type_` (bindgen output, `canvas.vl` ×7) | `type` | §5 only | bindgen's escape |
| `macro_std` `type_` (×37 reads) | `type` | §5 only | the macro API; renaming it is a breaking macro-API change — not proposed |
| JSON key `"type"` via `[derive(Json)]` | unreachable today | §5 only | `json_type.vl` |
| kolt `import_()`, `type_()` | `import`, `type` | neither | free functions of hard words |

Nothing else: the `<keyword>_` grep over every tree above finds `type_` (44 in
the vilan tree) and kolt's two icons, and no other escape. The honest reading
is that §4 is **cheap and wanted but not blocking anything today** (its exhibits
are one renamed method and one respelled constructor), and §5 is **the one with
a program it cannot write** (the JSON key).

## 8. Risks

**Error messages at a misparse — measured today, and what changes.** A keyword
used as a name produces poor messages NOW (the matrix's stderr): `let with =
1;` → "found 'let' expected a statement or '}'" anchored on `let`;
`struct S { with: i32 }` → "unclosed `{` in struct body"; a method
`fun own(self)` → "found 'fun' expected an expression or '}'"; `fun f(in: i32)`
drops the whole function and reports "cannot find 'f' in this scope" at its
call. Only `css` (`CSS_IS_A_KEYWORD`, `parsing.rs:269`, a dedicated rule in
`emit_failure`), `resource` and `void` have steers. Demoting a word REMOVES its
misparses outright. The new risk is the reverse — a keyword reading the author
meant and did not get:

- `own x` outside a parameter (`let own x = …`) reads a binder `own` then a
  stray name: "expected `=`". Mitigation, one rule per LL(2) word: a
  contextual word followed by a name WHERE ITS READING IS NOT ADMITTED reports
  the word's placement ("`own` is a parameter convention; a `let` owns its
  value already") — `parse_misplaced_resource` is the precedent.
- `impl S wiht Trait` (typo) reads the same today and after: "expected `{`".
- `jump;` — §4.7.

**Recovery.** `lazy` (and `resource`, until B413) are sync points in
`starts_statement_or_item`; the demoted check peeks one more token (§4.5).
`with`, `borrows`, `own`, `dyn`, `jump`-as-keyword are not sync points today
(`jump` is — it moves to the same LL(2) check).

**Generated code.** Derive macros and `macro_std::build` emit source text that
the parser re-reads; a field or parameter NAME is spliced into `let` positions
in at least two emitters (`json.vl:995`, `rpc.vl:5692`). Under §4 a field
named `lazy` splices `let lazy = …`, which still parses; under §5 a field named
`type` would not. §5's slice owns that.

**Emitters.** JS escapes its reserved words (`transformer.rs::RESERVED_NAMES`, `:12211`, which
includes `with` and `in`); a binding named `with` emits safely (probe: `let as`
and `let self` run on both backends). Rust: `sanitize` raw-escapes `dyn`, `as`,
`in`, `type`… — valid raw identifiers — but not `self`/`Self`/`super`/`crate`
(§12 find 2).

**bindgen.** Its `RESERVED` list is a hand copy of the keyword table and has
DRIFTED: it lacks `css`, `dyn` and `lazy`, so a TS member named any of them
emits a method the parser refuses — `w.d.ts` with members `lazy`, `css`, `dyn`
generates `external fun lazy(self)` etc. and `vilan check widget.vl` fails at
the first (`expected ';' to end this statement`). §12 find 6; S1 generates the
list from `KEYWORDS` minus the demoted words.

**The docs gate.** `docs.rs` holds the tour's reserved-word section to
`KEYWORDS` in both directions (N63), and the lexical spec §2.2 prints the
list; both follow each demotion in the same commit (the three-place rule).

## 9. Prior art, briefly

Kotlin splits its words into hard keywords, SOFT keywords (contextual:
`by`, `get`, `set`, `where`, …) and MODIFIER keywords usable as identifiers
(`enum`, `external`, `const`, `lazy` is not a keyword at all). C# has added
every keyword since 1.0 as contextual (`async`, `await`, `var`, `where`,
`with`, `record`). Swift's declaration modifiers (`lazy`, `mutating`,
`dynamic`) are contextual. Python 3.10/3.12 made `match`, `case` and `type`
SOFT keywords — `type` precisely because it is too common a name to reserve.
Rust has weak keywords (`union`, `raw`, `safe`) and raw identifiers (`r#type`)
for the rest. JavaScript admits every reserved word as a property name
(`obj.if`, `{ type: 1 }`) — §5's rule — and has never needed a raw-identifier
syntax for members because of it.

## 10. Slices

**S1 — the positional four: `with`, `borrows`, `own`, `dyn`. (M.)** Four
`KEYWORDS` rows and `Token` variants go; seven parser sites read
`Ident(word)` by position or LL(2); `formatter.rs` (2 `Borrows` sites),
`completion.rs` (`keyword_lexeme`, `head_is_not_an_initializer`,
`KEYWORD_DOCS` via the raw-parse hover); `grammar_sync.rs` moves the four to
`CONTEXTUAL_WORDS` with anchored rules and `regex_matches` pins; the lexical
spec, `grammar.md`, the tour's list and its gate; bindgen's `RESERVED`
GENERATED from `KEYWORDS` (fixes find 6). Pins: the matrix for the four
(every position `ok`), each keyword reading unchanged (the corpus goldens do
not move — no program in the tree names any of the four), the placement rule
for `own` misplaced. Not breaking: every program that compiled compiles.

**S2 — the LL(2) statement heads: `lazy` (+ `jump` if Q1). (S–M.)** The
statement dispatch and `starts_statement_or_item` peek one more token; the
`lazy name = …` recovery kept; the `jump;` rule if Q1. Pins as S1.

**S3 — `resource` with B413. (S, inside B413.)** B413's commit removes the
`KEYWORDS` row and keeps the old spelling's steer by LL(2) (find 1). If B413
is already merged holding the token, S3 is this demotion alone.

**S4 — the member tier, if Q2 is yes. (M.)** `eat_member_name` at the five
member positions; the derive emitters bind fresh locals (fixes find 3);
`vilan-rust::sanitize` suffixes the four non-raw words (fixes find 2, which
should not wait for S4); bindgen stops escaping METHOD names; pins over every
keyword at every member position on both backends, and `json_type.vl`
decoding `{"type": …}`.

None of these is in this train; the brief names Order 43 as the earliest.

## 11. Open questions, each with a recommendation

**Q1 — `jump`: contextual, against the item's "control flow stays hard"?**
Its keyword reading is always `jump` + a name, the LL(2) rule's exact shape, and
the tour apologises for the word by name. *Rec: yes, in S2, with the `jump;`
rule.* If the owner prefers the item's line as drawn, nothing else in the
paper depends on it.

**Q2 — the member tier: every word at member positions?** It is the only half
of the question with a program that cannot be written today (the JSON `type`
key) and it needs no lookahead. *Rec: yes, as S4, after S1.* The alternative
for the JSON case alone is a field-rename attribute on `[derive(Json)]`, which
is useful anyway but leaves `e.type_` in the program and bindgen's escapes in
place.

**Q3 — a raw-identifier escape (`r#type`-style) for the hard words?** *Rec:
no.* With §4 and §5 the remaining hard-word names are free functions and
bindings, where the estate's only instances (kolt's two icons) read fine with
`_`; `#` is now the import reach marker (B318), and a second meaning for it
would cost more than it buys.

**Q4 — `dyn` as a TYPE name?** *Rec: no — `dyn` stays the keyword at every
type-position head except `dyn::` (a module path).* Types are Capitalized by
convention, nothing asks, and it keeps `dyn T` a one-token decision.

**Q5 — keep keyword hover on demoted words?** Today `as` and `context` have
none. *Rec: keep it*, via the raw-parse read `keyword_hover` already does for
markup; losing a hover the user has today is a regression the demotion should
not carry.

**Q6 — does B413 remove `resource` from `KEYWORDS`?** This is B413's to build
(syntax-42, this order) and it decides whether the dissolution frees the word
at all. *Rec: yes — the row goes, the old spelling's steer is LL(2)* (§4.6,
find 1). Not a new ruling if the owner reads R-c's "dissolve the keyword" as
already meaning it; asked so the lane does not guess.

## 12. Finds — met while probing, not fixed here

1. **B413's brief does not say the lexer row goes.** "the `resource` keyword
   dissolves into `[resource]` on a struct (the word stays)" — if the lane reads
   "the word stays" as "the token stays", `resource` remains reserved and the
   constructor collision A124 met survives. Relay to syntax-42 (Q6).
2. **NATIVE: a field named `self` or `super` cannot be emitted** (live today,
   independent of B414). `self` is contextual, so `struct S { self: i32, super:
   i32 }` checks and runs on JS (`self_field.vl` prints `3`); natively
   `sanitize` writes `r#self`/`r#super` and rustc refuses: "`self` cannot be a
   raw identifier". `self`, `Self`, `super`, `crate` need a suffix, not `r#`.
   (vilan-rust, S.)
3. **Derive hygiene: `[derive(Wire)]` binds a local per field, so a field named
   `deserializer` shadows the parameter** (`json.vl:995`, `let {field.name} =
   …::rebuild(deserializer);`). `wire_shadow.vl`: five errors "in code generated
   by this attribute", the first "'i32' does not implement trait 'Deserialize'".
   Refused, not miscompiled; the fix is fresh local names (`__f0`, …), which S4
   needs anyway. `rpc.vl:5692` has the same shape over parameter names.
4. **A method named `Self` is accepted at its declaration and unreachable**:
   `impl S { fun Self(self): i32 { self.n } }` checks the declaration (then
   "cannot access field 'n' on type unknown" inside it) and `s.Self()` is "S has
   no method 'Self'". Refuse `Self` as a declared member name, as `void` is
   refused as a binder (N113). (S.)
5. **Lexical spec §2.2 omits `as` and `only`** from its contextual list, which
   `grammar.md` §3.2 documents as contextual and `grammar_sync.rs` pins (`as`).
   (docs, XS.)
6. **bindgen's `RESERVED` has drifted from `KEYWORDS`** — missing `css`, `dyn`,
   `lazy`; a TS member with one of those names generates bindings that do not
   parse (§8). Generate the list from `KEYWORDS`, with a pin. (S.)

## 13. The recommendations, collected

1. **Demote `with`, `borrows`, `own`, `dyn` (S1) and `lazy` (S2)** to contextual
   keywords by the positional and LL(2) tests of §4; keep the other 28 hard for
   the reasons §3 tabulates; `resource` goes with B413 (S3).
2. **`jump` contextual too** (Q1, S2), with the `jump;` rule.
3. **The painting rule** of §6: semantic tokens as they are; TextMate and
   highlight.js paint a contextual word as a keyword only when a name follows it
   (and, for `with`/`borrows`, a type precedes it); pinned both ways in
   `grammar_sync.rs`; keyword hover kept through the raw parse.
4. **The member tier** (Q2, S4): every word at the five member positions — the
   JSON `"type"` key is the program it unblocks.
5. **Tell syntax-42 now** that B413 should remove the `KEYWORDS` row (Q6,
   find 1).
6. **File finds 2–6** — find 2 (native `r#self`) is live today and small.
7. **No raw-identifier syntax** (Q3); `dyn` stays the keyword in type position
   (Q4).
