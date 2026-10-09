# Named tuple fields — labels for a tuple's positions, with no declaration (B569)

> Status: **DRAFT 2026-10-08 — for the owner's ruling.** Written by lane papers-b-48 of
> Order 48 against `vilan 0.45.0 (e75bc57c3)` = `origin/next` @e75bc57c, read at that
> commit in the worktree `vilan/.claude/worktrees/papers-b-48`. Nothing in the vilan tree
> changed. Every claim about today's behaviour is a probe that was run or a line that was
> read, and says which.
>
> Probes: `scripts/integration/sweeps/order48/papers-b-48/probes/b569/` (cited `nN`),
> re-run by `probes/run_all.sh <scratch>`, output in `probes/run_all.out`. The estate counts
> come from `papers-b-48/census/` — a walker over the tree's OWN parser
> (`vilan_core::parsing::parse_preserving_groups`, so every parenthesized group is kept)
> that classifies every `Node::Assign` by the tokens around it. Raw output beside it.
>
> Related:
> - B569 (this paper), with the owner's two stamps (2026-10-05) as the starting position;
> - B571 (`type-ascription.md`: `EXP as T`) and B570 (`auto-annotations.md`), written
>   beside it;
> - B309 and B495 (`closure-type-views.md`): a part of `Type::Closure` that unification
>   carries and does not compare — the precedent for where labels live;
> - A122 (`tuple-module.md`), `variadic-generics.md`, `tuple-comprehension.md` (B183): the
>   tuple family, `keys()`, mapped tuples, spread parameters;
> - B525 (the contract hash renders a type's SHAPE), B414 S4 (member names are any word).

## 0. The ask, and the answer up front

The owner's sketch, with his 2026-10-05 correction of the third line:

```vilan,fragment
let point_1: (x: f64, y: f64) = (x = 5, y = 7); // (5, 7)
let point_2: (x: f64, y: f64) = (5, 7);         // (5, 7)
let point_3: (x: f64, y: f64) = (y = 7, x = 5); // (5, 7): by name
print(i"point x={point_1.x}, y={point_1.y}");
```

**Ruled already (2026-10-05):** a labelled literal matches a labelled expected type BY NAME;
labelled and unlabelled convert freely; differently-named labels reconcile by position; the
same label set in a different order does not reconcile (refused or warned — this paper picks).

**The answer.**

1. **Labels are a property of the tuple TYPE that unification carries and does not
   compare** — exactly B309's `context` clause and B495's parameter modes in
   `Type::Closure`. `Type::Tuple(Vec<TypeId>)` gains a labels slot. Two tuple types are
   compatible when their elements are; one rule refuses a pair whose labels CONTRADICT.
2. **The contradiction is REFUSED, not warned**, and the rule is one notch wider than the
   ruling's case: a label that both sides carry at DIFFERENT positions (§4.3). The same set
   reordered is the common case of it; `(x, y)` into `(y, z)` is the same mistake.
   A refusal can later relax to a warning without breaking a program; the reverse cannot.
3. **Assignment leaves value position.** `x = 5` stays legal where its value is discarded —
   a statement, a block's tail, a `match` arm, a closure's expression body, a `then`/`else`
   statement branch — and is refused wherever its value would be USED: inside parentheses, as
   an argument or a tuple or list entry, as a `let` initializer, on the right of another `=`.
   **The estate has 0 sites to rewrite**: of 1,696 assignments across std, the corpus, the
   examples, the docs, kolt and the website, none is in value position (§3).
4. **`(x = 5)` is a one-slot labelled tuple** `(x: i32)`, distinct from `i32` — the label is
   what makes it a tuple, where `(5)` stays a group. That is what makes named arguments
   reachable through a spread parameter (§8).
5. **Labels are read** by `p.x`, hover, `dbg`, the formatter, mapped tuples and B571's `as`;
   **they are erased** at mono, in both emitters (a label is a slot offset), and in the
   contract hash. Tuples have no `Wire` or `Json` impl today (n06); when they gain one it is
   positional, because two label sets that reconcile must encode alike.
6. **The book steers to a struct** the moment a shape has an identity: named in two
   signatures, carrying methods or derives, crossing the wire, or wider than three fields.

The build is four slices (§11), S1 breaking only in name: the assignment refusal, at 0 estate.

## 1. Ground truth (0.45.0)

| probe | program | result |
|---|---|---|
| n01 | `mut x = 0; let y = (x = 5);` | checks; `y` is `void` ("Expected i32, but got void") |
| n02 | `takes(x = 5)` (a `void` parameter), `let pair = (x = 6, 1);` | checks; `pair: (void, i32)` |
| n03 | `let p: (x: f64, y: f64) = (5, 7);` | parse error: "found ':' expected ',' or ')' in type annotation" |
| n04 | `let p = (x = 5, y = 7);` (no `x`, `y` in scope) | "cannot find 'x' in this scope", same for `y` — two assignments |
| n05 | `let h: \|swapped: i32\| i32 = g;` with `g: \|other: i32\| i32` | checks and runs (`2`): closure-type parameter names are not significant |
| n06 | `p.to_json()` on `(f64, f64)` | "(f64, f64) has no method 'to_json'" — no `Json` for tuples |
| n06b | `dbg((5.0, "a"))` | `[n06b_tuple_dbg.vl:6:2] p = (5.0, "a")` |
| n07 | `let a = (5); let b: i32 = a; let c = (5,);` | `(5)` is `i32`; `(5,)` is a parse error |
| n08 | `let (a, b) = p; (x, y) = (y, x);` | checks; prints `3`, `21` |
| n09 | `whole.keys().len()` over `T: (2..)` | `3` |
| n10 | `fun draw(...at: (f64, f64))`, `draw(1, 2)` | `12` |
| n11 | the same `draw((3, 4))` | "Expected (f64, f64), but got ((i32, i32))" — find B?2 |

What the tree holds, read:

- **Tuple types** are `Type::Tuple(Vec<TypeId>)` (`type_.rs:114`), structural: "equal iff
  element-wise equal" (`spec/types.md` §5.1). One-element tuples do not exist as distinct
  types; `(T)` is `T` (§5.1), and a spread parameter is what makes 0- and 1-arity tuple
  VALUES reachable (§5.9).
- **Tuples store flat.** "chains traverse nested tuples over the FLAT storage"
  (`vilan/test/tuple-access.vl`), and `std::tuple`'s intrinsics read "the concrete tuple
  layout of the instance … a position's slot offset is a property of the whole tuple type"
  (`std/src/tuple.vl`). A label is therefore a name for an offset the emitters already
  compute; it costs nothing at run time.
- **The precedent is in the closure type.** `Type::Closure(params, ret, contexts, modes)`
  carries a `context` clause that "UNIFICATION IGNORES" (`type_.rs:62`) and B495's modes,
  which it compares. Closure-type parameters already take documentation names
  (`|value: T| U`, `spec/grammar.md` §3.9: "only the types are significant"), and n05
  shows two types differing only in those names are one type.
- **`name = value` is already the language's named-entry spelling** in two places: a struct
  literal's field (`Point { x = 1, y = 2 }`, grammar §3.8 `init-field`) and an attribute's
  argument (`[expose(keyed = str)]`, `[reactive(name = "..")]`,
  `[service(KoltClient, client = KoltHandlers)]`). A labelled tuple literal is the third, and
  reads the same.
- **Assignment is an expression**, parsed by `Parser::parse_assignment`
  (`parsing.rs:7340`), which every `parse_expression` tries first wherever an expression
  stands (`parse_secondary_inner`, `parsing.rs:4876`). Its type is `void` (n01).
- **Where `Type::Tuple` is matched**: at ~126 sites in vilan-core
  (93 in `analyzer.rs`, 13 in `transformer.rs`, 4 in `analyzer/`, 3 in `printer.rs`, one
  each in `mono.rs` and `contract_hash.rs`, the rest in `impl_select` and friends) and 13
  in `vilan-rust`. That is the mechanical cost of a labels slot (§10).

## 2. The grammar

```text
tuple-type   = "(" [ tuple-slot { "," tuple-slot } [ "," ] ] ")" ;
tuple-slot   = [ MEMBER ":" ] type ;          (* labelled: every slot, or none *)

tuple        = "(" ( spread | entry "," entry { "," entry } [ "," ] ) ")"
             | "(" labelled-entry ")" ;        (* the one-slot labelled tuple *)
entry        = spread | labelled-entry | expression ;
labelled-entry = MEMBER "=" expression ;      (* `=`, the struct literal's spelling *)
```

- **A label is a MEMBER** (any word, B414 S4), as a struct field is: `(type: str, if: bool)`
  is legal, read `p.type`.
- **All or nothing.** A tuple TYPE labels every slot or none; so does a literal's written
  entries. A spread contributes its operand's slots with their labels (§6.2), so
  `(..p, z = 3)` over `p: (x: f64, y: f64)` is `(x: f64, y: f64, z: i32)`; a spread of an
  unlabelled tuple beside written labels is refused ("label every slot, or none: `..pair`
  brings two unlabelled slots"). A label written twice is refused.
- **No ambiguity with what exists.** In a type, `( IDENT ":"` begins a labelled slot,
  `( IDENT "in"` a mapped tuple (`(U in T: F<U>)`), anything else a type — decided at the
  second token. In a literal, `MEMBER "="` at an entry's head is a label once assignment
  has left value position (§3); `==`, `=>` and the compound `+=` are different tokens. A
  tuple comprehension (`(x in xs => e)`) begins `IDENT "in"`.
- **No shorthand.** `(x, y)` is positional, so it cannot also mean `(x = x, y = y)` the way
  `Point { x, y }` does. Write the labels.
- **Destructuring by name** reuses the literal's spelling, label then binder:
  `let (y = top, x = left) = p;` binds `top = p.y`, `left = p.x`. Positional destructuring
  (`let (a, b) = p;`) is unchanged and ignores labels. A `match` pattern takes the same
  form (`(x = 0, y = let v)`). This is S3, after the core.

## 3. The ban on assignment in value position

### 3.1 Why it is needed

Inside parentheses `x = 5` must mean ONE thing. Today it is an assignment (n01, n02, n04);
with labels it is a slot. The owner's rule is that assignment in expression position goes,
and a block still assigns.

### 3.2 The rule, precisely

An assignment is legal where its value is DISCARDED, and refused where its value is USED.

| position | today | after | estate |
|---|---|---|---:|
| expression statement `x = 5;` | legal | legal | 1,657 |
| a block's tail `{ x = 5 }` | legal (value `void`) | legal | 1 (kolt `lib/interact.vl:119`) |
| a `match` arm body `A => x = 5,` | legal | legal | 26 (std 14, corpus 12) |
| a closure's expression body `\|v\| total += v` | legal | legal | 12 (corpus 10, docs 2) |
| a `then`/`else` statement branch `c then x = 5;` | legal | legal | 0 |
| inside parentheses `(x = 5)` | an assignment, `void` | **the one-slot labelled tuple** | 0 |
| a tuple entry `(x = 6, 1)` | `(void, i32)` | **a label** (here: mixing refused) | 0 |
| a call argument `f(x = 5)` | passes `void` | **a named argument** to a spread parameter (§8), refused elsewhere | 0 |
| a list entry, a `let` initializer, the right of another `=`, an operand, a condition, a field value | legal, `void` | refused | 0 |

The refusal names the fix: "an assignment is a statement and has no value: write `x = 5;`
before this, and use `x`" — and inside parentheses, where the author may have meant a
label, "`(x = 5)` is a tuple with the label `x`; to assign, write `x = 5;`".

The four discarded-value positions other than the statement keep working because nothing
there could be a label, and requiring braces in them would rewrite 38 sites (the arms and closure bodies) for no reading
it disambiguates. (The stricter rule — assignment only as a statement or inside braces —
is Q3's alternative.)

### 3.3 The estate

Counted with the census walker over each estate's `.vl` files and, for the docs, every
```` ```vilan ```` fence of `vilan/docs` and `README.md` extracted to its own file (601
fences; 177 do not parse as a program, being signatures or fragments, and their RECOVERED
trees were walked, plus a regex pass over all 177 for `( name =` and `, name =`, which found
only attribute arguments).

| estate | files | assignments | statement | block tail | arm | closure body | **value position** |
|---|---:|---:|---:|---:|---:|---:|---:|
| std (`vilan/std`, `macro_std`) | 73 | 1,062 | 1,048 | 0 | 14 | 0 | **0** |
| corpus (`vilan/test`, benchmarks, `crates/**/*.vl`) | 242 | 459 | 437 | 0 | 12 | 10 | **0** |
| `vilan/examples` | 29 | 9 | 9 | 0 | 0 | 0 | **0** |
| docs fences | 601 | 58 | 56 | 0 | 0 | 2 | **0** |
| kolt (a `cp -r` copy, `src/`, lucide included) | 31 | 91 | 90 | 1 | 0 | 0 | **0** |
| vilan-website (a `cp -r` copy) | 15 | 17 | 17 | 0 | 0 | 0 | **0** |
| **total** | 991 | **1,696** | 1,657 | 1 | 26 | 12 | **0** |

**The ban breaks nothing that exists.** It is still a breaking change in the language (n01
compiles today), so it rides a minor version with a CHANGELOG `breaking` entry.

## 4. Matching

### 4.1 A labelled literal

- **Against a labelled expected type: by name** (ruled). `point_3` is `(5, 7)`. The literal's
  label set must equal the type's: a missing label ("`(x: f64, y: f64)` needs `y`") and an
  extra one ("`z` is not a label of `(x: f64, y: f64)`") are refused, as a struct literal's
  are. Each entry is checked against its slot's type, so `(y = 7, x = 5)` gives both
  literals `f64`.
- **Against an unlabelled expected type: by position, labels dropped.** `(x = 5, y = 7)` at
  a `(f64, f64)` parameter is `(5, 7)`. Unlabelled and labelled convert freely (ruled).
- **With no expected type:** its type is its written order with its labels:
  `let q = (y = 7, x = 5);` is `(y: i32, x: i32)`.
- **An unlabelled literal against a labelled type: by position** (ruled; `point_2`), taking
  the type's labels.

### 4.2 Two tuple VALUES

| from | into | result |
|---|---|---|
| `(f64, f64)` | `(x: f64, y: f64)` | position; takes the labels |
| `(x: f64, y: f64)` | `(f64, f64)` | position; drops the labels |
| `(w: f64, h: f64)` | `(x: f64, y: f64)` | position (ruled: differently named labels reconcile) |
| `(x: f64, y: f64)` | `(y: f64, x: f64)` | **refused** (§4.3) |
| `(x: f64, y: f64)` | `(y: f64, z: f64)` | **refused** (§4.3: `y` moves from 1 to 0) |

A binding, a parameter, a field and a return take the labels of their DECLARED type; an
unannotated binding keeps its initializer's. A join (`if`/`else` arms, `match` legs, a
list's elements) checks each later arm against the first arm's type as it does today, so
literal arms match by name; two VALUES whose labels contradict are refused there too.

Labels go through generics as part of the type a parameter binds: `fun id<T>(t: T): T`
returns `id(p).x`. A generic position written unlabelled (`(A, B)`) drops them, as any
unlabelled position does.

### 4.3 The contradiction: refuse, and one notch wider

**The rule:** two tuple types whose elements are compatible are refused when some label
appears in BOTH at different positions. Nested tuples are checked slot by slot.

**Refuse, not warn — four reasons:**

1. **There is no safe default.** `(x: f64, y: f64)` landing at `(y: f64, x: f64)` is either a
   reorder (the author meant `y` to get `p.y`) or a swap (positionally, `y` gets `p.x`). The
   two readings give different values, and a warning runs one of them.
2. **The labels exist to catch exactly this.** A positional reconcile under a warning is the
   bug the labels were written to prevent, shipped.
3. **The fix is mechanical, and the error carries both.** "`p` is `(x: f64, y: f64)` and this
   wants `(y: f64, x: f64)`: by name, write `(y = p.y, x = p.x)`; by position, drop the
   labels with `(p.0, p.1)`". Two quick fixes.
4. **A refusal can relax to a warning later; a warning cannot tighten without breaking
   programs.** vilan's warnings are not errors in CI, so a warned swap would land.

**Why wider than the ruling's case.** The ruled case is the same label SET reordered. The
same mistake with one label renamed — `(x: f64, y: f64)` into `(y: f64, z: f64)` — moves `y`
too, and a rule keyed on set equality lets it through. "A shared label at a different
position" covers both and nothing else: disjoint label sets reconcile (ruled), and shared
labels at the same positions agree.

## 5. What reads the labels

| reader | behaviour |
|---|---|
| `p.x` | resolved at analysis to the slot, like a struct field; emitted as the slot (`p.0`'s code). `p.0` keeps working. A label that is not on the type: "`(x: f64, y: f64)` has no label `z`; its labels are `x`, `y`". |
| assignment through a label | `p.x = 3;` on a `mut p`, as `counter.0 = counter.0 + 1;` is today (`vilan/test/tuple-access.vl`). |
| hover, inlay hints, signature help, completion | print the labels: `p: (x: f64, y: f64)`. Completion after `p.` offers the labels before the `Tuple` members. |
| diagnostics | print the labels of the types they name, so §4.3's refusal reads. |
| `dbg` | prints the literal: `p = (x = 5.0, y = 7.0)` (n06b prints `(5.0, "a")`). `dbg` is an intrinsic printer that knows the static type at its call; inside a generic body over `T` it prints what the instantiation knows, which after erasure (§6) is unlabelled. |
| `Debug` | tuples have no `Debug` impl yet (`std/src/debug.vl:48`: "A TUPLE is not covered yet"). When one lands it prints positionally, for the same reason as `Wire` (§6.1). |
| the formatter | prints labels as written, `(x: f64, y: f64)` and `(x = 5, y = 7)`, one space after `:` and around `=`. |
| `keys()` / `entries()` / `get()` (A122) | unchanged: a key is a POSITION (`TupleKey<T, U>`). A `key.label()` would need labels in the instantiation key, which §6.3 erases; it is future work (Q8). |
| mapped tuples | `(U in T: F<U>)` carries `T`'s labels position by position, because a mapping preserves positions by construction. So `combine((x = a, y = b))` is `SignalCell<(x: i32, y: i32)>` and `.derive(\|v\| v.x + v.y)` reads. A tuple comprehension `(v in t => e)` carries `t`'s labels the same way. |
| `as` (B571) | `(5, 7) as (x: f64, y: f64)` labels an unlabelled value; a labelled literal under `as` matches by name. |
| `auto` (B570) | writes the labels as hover prints them: `fun bounds(..): auto (min: i32, max: i32)`. |

## 6. What erases them

### 6.1 Wire and JSON

Tuples have **no `Wire` and no `Json` impl** today (n06; none in `std/src/wire.vl` or
`json.vl`). When they gain one it is **positional** — an array — labelled or not:

- two label sets that reconcile (§4.2) are the same value moving through one position, so
  they must encode alike, and a by-name object would make `(x: f64, y: f64)` and
  `(w: f64, h: f64)` two wire formats for one compatible type;
- the binary codec reads by position already (B525: "the binary reader advances by position
  and ignores names").

A shape whose JSON should be an object with names is a struct (§9).

### 6.2 The contract hash (B525)

B525 writes a struct's field NAMES into the contract hash because the JSON codec reads
structs by name. A tuple's codec is positional, so **labels stay out of the hash**: adding,
renaming or removing a label changes no contract. Reordering slots changes the hash, as it
changes the types.

### 6.3 Mono and the emitters

Labels are **erased at monomorphization**: `show<(x: i32, y: i32)>` and `show<(i32, i32)>`
are one instantiation, so labels never multiply emitted code. JS emits a label read as the
slot offset it already computes over flat storage; the native backend emits Rust tuples
(`(f64, f64)`) and `p.x` as `p.0`. Nothing in `vilan-rt` changes.

## 7. One field: `(x = 5)`

Three readings: a one-slot labelled tuple, a grouping of an assignment, a refusal.

- A **group** is what `(5)` is, and what `(x = 5)` is today (n01). §3 removes the
  assignment reading.
- A **refusal** (Swift's choice: it refuses a one-element tuple with a label) keeps the
  `(2..)` world tidy, but it closes the door to named arguments: a spread function with one
  named parameter is called `f(x = 5)`, which is `f((x = 5))` (§8).
- **Recommendation: the one-slot labelled tuple**, type `(x: i32)`. The label is what makes
  it a tuple: `(5)` stays `i32`, `(x = 5)` is `(x: i32)`, and the type `(x: i32)` is a
  1-arity tuple, not `i32`. `p.x` reads it. Such values already exist as spread packs
  (§5.9), so this adds a spelling, not a kind. It does NOT meet `T: (2..)` (arity 1), as a
  1-pack does not today.

## 8. The door: named arguments through spread parameters

A spread parameter over a concrete tuple works today (n10: `fun draw(...at: (f64, f64))`,
`draw(1, 2)` is `12`). Label the tuple and the call site writes names:

```vilan,fragment
fun draw(...at: (x: f64, y: f64)): f64 { at.x * 10 + at.y }

draw(1, 2);          // positional, as today
draw(x = 1, y = 2);  // the collected tuple is the labelled literal (x = 1, y = 2)
draw(y = 2, x = 1);  // by name (§4.1): the same call
```

Nothing new is needed past §2–§4: `f(a, b)` collects into `f((a, b))`, so `draw(x = 1, y = 2)`
collects into the labelled literal `(x = 1, y = 2)` against the expected pack type
`(x: f64, y: f64)`, and §4.1 matches it by name. Mixing positional and named arguments is
refused (all or nothing, §2).

What it does not give: **defaults** (`draw(x = 1)` with `y` defaulted) need optional slots,
which a tuple has not got; that is the next ask, and it is a struct-with-defaults question
(Q7). And n11 (find B?2) says a spread function called with ONE built tuple collects it into
a one-slot pack, where the spec's comment says the two calls are one; under that rule
`draw(p)` with `p: (x: f64, y: f64)` is refused and the spelling is `draw(..p)`. This paper
leans on the behaviour, not the comment.

## 9. When the book steers to a struct

A named tuple is a struct with no name, no declaration and no impls. The book's guidance
(the tour's tuples page and the reference's §5.1):

**Use a named tuple when** the shape lives in one place and passes through:

- several values returned at once: `fun bounds(xs: List<i32>): (min: i32, max: i32)`;
- a pair whose positions a reader has to remember: kolt's `lib/search.vl` builds
  `List<(usize, usize)>` ranges and reads `range.0` / `range.1` for start and end
  (`:447`–`:456`, `:742`–`:748`), and `lib/overlay.vl:144` returns `(f64, f64)` that callers
  read as x and y — `(start: usize, end: usize)` and `(x: f64, y: f64)` say it in the type;
- the arguments of a combinator: `combine((x = a, y = b))`;
- a call with several same-typed parameters, through a spread (§8).

**Use a struct when** the shape has an identity:

- it is named in more than one signature (a type alias for a tuple would be a struct by
  another name);
- it needs methods, an `impl`, a derive (`Wire`, `Json`, `Storable`, `PartialEq` by
  intent), field visibility or defaults;
- it crosses the wire or the store with names (§6.1);
- it has more than three fields, or fields that are themselves tuples.

An inherent `impl` on a labelled tuple type is refused with the steer to a struct: labels are
not an identity (§4.2), so `impl (x: f64, y: f64)` would also answer for `(w: f64, h: f64)`.

How often the estate reaches for positions today, as a sense of the demand: the census counts
**87 `.0`/`.1`… reads in std, 121 in the corpus, 52 in kolt, 8 in the docs fences**, and 63,
37, 4 and 12 destructuring `let`s.

## 10. The representation

`Type::Tuple(Vec<TypeId>)` → `Type::Tuple(Vec<TypeId>, TupleLabels)`, where `TupleLabels` is
`Option<Box<[Symbol]>>` (`None` = unlabelled; one label per slot otherwise).

- **Unification carries it and does not compare it**, as B309's clause: the reconcile arm
  keeps the side that has labels (the declared side where one is declared) and applies §4.3.
- **`Eq`/`Hash` of `Type` ignore labels** — two types that unify must not key apart in the
  maps that compare them, and mono must not split instantiations (§6.3). This is the one
  place labels differ from B495's modes, which DO take part (they are calling conventions).
  The printer reads them.
- **Not a side table.** `closure-type-views.md` §0 measured why: types are not interned,
  every walk mints a fresh id, and a side band keyed by the written annotation is lost
  through every reconcile, substitution and generic return. Labels must flow through `T`.
- **The cost:** ~126 destructuring sites in vilan-core and 13 in vilan-rust gain a `_` (or
  `..`); the reconcile and compare arms (a handful) gain the merge and the refusal; the walk
  of `Node::Tuple`-as-type and the literal walk read labels; member access resolves a
  label. One new `Node` shape (the labelled entry) in the parser and the formatter.

## 11. Slices

| Slice | Content | Size | Needs |
|---|---|---|---|
| S1 | **Breaking.** The assignment refusal in value position (§3.2), with its two steers; the estate re-counted on the tree it lands on (0 today); a `breaking` CHANGELOG entry | S | — |
| S2 | The labels: the grammar (§2), `TupleLabels` in `Type::Tuple`, literal matching (§4.1), reconcile and the contradiction refusal (§4.2–§4.3), `p.x` read and write, hover/diagnostics/printer/formatter, erasure at mono, the one-slot tuple (§7), mapped tuples and comprehensions carry labels; pins on both backends | M–L | S1 |
| S3 | By-name destructuring and patterns (`let (y = top, x = left) = p;`); `dbg` prints labels | S | S2 |
| S4 | Named arguments through spread parameters (§8): the collected tuple is the labelled literal; signature help shows names | S | S2, B?2's ruling |

## 12. Interactions

- **B571 (`as`).** `(5, 7) as (x: f64, y: f64)` labels a value; `(y = 7, x = 5) as (x: f64,
  y: f64)` matches by name. The ascription's type ends at the tuple type's `)` (B571 §5).
- **B570 (`auto`).** An `auto` annotation writes labels as hover prints them; a label change
  in an inferred type makes an `auto` stale exactly as a type change does (labels are
  printed, so a stale check compares the printed type — B570 §4).
- **E227 (`[hint]`).** A labelled tuple nested in a hinted node abbreviates in place:
  `(x: ~Pipe<i32>, y: i32)`.
- **B183 (`tuple-comprehension.md`).** A comprehension's binder walks positions, as now;
  the result carries the source's labels.
- **The tour and the reference.** §5.1's tuple line gains labels; grammar §3.4 states the
  assignment's positions; §3.6 the labelled entry; §5.9 the named-argument call.

## 13. Finds (filed to `newitems48-papers-b.json`)

1. **B?2** — a spread function called with one tuple collects it into a one-slot pack
   (`draw((3, 4))`: "Expected (f64, f64), but got ((i32, i32))"), where `spec/types.md`
   §5.9 writes `log(1, "hi") == log((1, "hi"))`. Repro `finds/spread_called_with_one_tuple.vl`.
   §8 leans on the behaviour.
2. **B?1** (met while writing B571's steer; filed from there) — `let xs = [];` and
   `let o = None;` with nothing to ground them check clean and fail natively.

## 14. Open questions, each with a recommendation

- **Q1. Where the labels live.** In `Type::Tuple` beside the elements, a side table, or a new
  `Type::LabelledTuple` variant. **Rec: a labels slot in `Type::Tuple`, carried by
  unification and ignored by `Eq`/`Hash` (§10).** A side table is lost through every
  reconcile (B495's lesson); a separate variant doubles every tuple arm.
- **Q2. The same label set in a different order: refuse or warn.** **Rec: refuse, with the
  by-name and by-position quick fixes (§4.3),** and widen the rule to "a label both sides
  carry at different positions", which covers the ruled case and its one-rename twin.
- **Q3. Which positions keep assignment.** (a) Statement, block tail, `match` arm, closure
  expression body, `then`/`else` statement branch; (b) statement and block tail only (arms
  and closure bodies take braces). **Rec: (a).** Nothing in those positions could be a
  label, and (b) rewrites 38 sites (26 arms, 12 closure bodies) for no disambiguation. Both
  break 0 sites in value position.
- **Q4. `(x = 5)`.** A one-slot labelled tuple, a group, or a refusal. **Rec: the one-slot
  labelled tuple `(x: i32)` (§7)** — it is what makes a one-parameter named call work.
- **Q5. Mixed labelled and unlabelled slots in one tuple** (`(x: f64, f64)`, Swift allows
  it). **Rec: refuse — all or nothing.** It keeps §4's table to four rows and the spread rule
  to one line; the first program that needs a partial label is the time to look again.
- **Q6. Wire/JSON when tuples gain an impl.** Positional array, or a by-name object for a
  labelled tuple. **Rec: positional, always (§6.1),** and labels stay out of the contract
  hash (§6.2). A by-name encoding makes two reconciling types two formats.
- **Q7. Named arguments (§8): ship S4, and are defaults in scope?** **Rec: ship S4 as the
  labelled literal against the pack (no new rule), and leave defaults out** — defaults are
  optional slots, which is a struct-literal question (a struct with field defaults as a
  spread pack), worth its own item.
- **Q8. `keys()` and labels.** Expose a key's label (`key.label(): Option<str>`) or not.
  **Rec: not now.** It needs labels in the instantiation key, which multiplies emitted
  code per label set; erasure (§6.3) is the cheap and predictable rule. Revisit with a
  customer (a generic `Display` for named tuples would be one).
- **Q9. An `impl` on a labelled tuple type.** **Rec: refused with the steer to a struct
  (§9);** labels are not an identity.
- **Q10. Spread with labels.** `(..p, z = 3)` concatenates labels; a labelled spread beside
  unlabelled entries is refused. **Rec: as stated (§2),** one rule with Q5.
