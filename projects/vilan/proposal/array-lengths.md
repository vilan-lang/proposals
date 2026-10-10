# Array lengths — `[type T; _]`, `<const N>`, and the names a length may be (I2 with A163)

> Status: **DRAFT 2026-10-09 — for the owner's ruling.** Written by lane papers-49 of
> Order 49 against `vilan 0.46.0 (92c621848)`, the compiler of `origin/next` @445c9346 (the
> v0.46.0 fold + L17, a release-tooling change), read in the worktree
> `vilan/.claude/worktrees/integration`. Nothing in the vilan tree changed. Every claim about
> today's behaviour is a probe that was run or a line that was read, and says which.
>
> Probes: `scripts/integration/sweeps/order49/papers-49/probes/` (cited `pNN`), re-run by
> `probes/run_all.sh` (both backends), output in `probes/run_all.out`. The estate counts come
> from `papers-49/census/census.py` (a regex walker over `.vl` files and the book's `vilan`
> fences, string literals and `//` comments stripped; every hit listed in `census.out` and
> read by hand).
>
> Related:
> - I2 (this paper; `fixed-arrays.md` §7 is its origin), A163 (RULED 2026-10-09: "not its own
>   slice; goes with I2"), A161 (`[T; n]` as `Items<T>`; waits on this), B582 (an array impl
>   head cannot bind its element), F109 (the native list literal at an array type), E283
>   (`Debug` misses `[T; n]`);
> - history: B177 (array comparators made structural), B220 (arrays are impl subjects for
>   methods), B294 (`_` as the anonymous binder), A122 (the tuple family `T: (2..)` and
>   `Tuple::len`), G24 (`const let`), I5 (`usize`, the index type).

## 0. The ask, and the answer up front

A163's four, for a head over every length, set against fixed-arrays.md §7's const-generic
lengths:

```vilan,fragment
impl [type T; _] with Items<T> { .. }            // A163's narrow door: every length, unnamed
fun total<const N>(values: [i32; N]): i32 { .. } // §7: the length a generic parameter
let header: [u8; SIZE] = ..;                     // §7: the length a name
```

**The answer.**

1. **A length is a type-level number.** `Type::Array(TypeId, usize)` becomes
   `Type::Array(TypeId, TypeId)`, whose second id resolves to a new `Type::Length(n)` or to a
   length-kinded generic. A length binder is then an ordinary generic and every machine
   A163 lists already takes it: the substitution map (`SubstitutionContext =
   HashMap<TypeId, TypeId>`, `type_.rs:196`), `bind_subject`, `reconcile_type`, both
   `write_type_key`s. A side enum would need a second binding map threaded through all of them.
2. **`_` and `const N` are one feature, spelled two ways.** `[type T; _]` is
   `[type T; const N]` with the name declined, which is how B294's `_` relates to `type T`. The
   narrow door costs the same four changes as the named form, so the ruling stands: one
   machine, both spellings in one slice. In a generic list (`fun`, `struct`, `enum`, `trait`)
   the parameter is `<const N>`; the keyword is `const` because `N` is a value, not a type.
3. **`<const N>` means a length and nothing else.** It is a `usize` parameter,
   monomorphized like a type, equal by value. It takes no annotation, no other value kinds
   and no bounds in v1. Inside a body, `N` and `self.len()` are `usize` values, folded per
   instance.
4. **The staging fork goes away for the subset that needs no evaluation.** A length may be
   written as a literal, as a name whose binding is immutable and whose initializer is an
   integer literal (or another such name), or as a const parameter. `const_eval::classify`
   already draws the same literal line. Names resolve with the other names, before the
   fixpoint. A length that needs arithmetic or a call needs const-eval, which runs after
   analysis, so it is refused and the message says why.
5. **The estate is 9 sites, every length a literal.** They are 7 in the corpus
   (`fixed-arrays.vl`, lengths 2, 3, 4) and 2 in the book's tour (4, 3). std, the examples,
   kolt, the website, the playground and the benchmarks have 0. A non-literal length cannot
   exist today because the compiler refuses one. Everything here is additive, except one fix
   with no edits (6).
6. **Four things are true on the tree whatever is ruled.** B582 is a one-arm fix that waits
   for nothing (§11). `[T; n].len()` answers `i32` where every other length answers `usize`
   (find B?1). F109 no longer reproduces on 0.46.0, because F100 lowered the directed literal
   (§8.3). The subscript's `usize` check misses a call index (find B?2).

## 1. Ground truth (0.46.0)

| probe | program | result (JS; native the same unless said) |
|---|---|---|
| p01 | `impl [type T; 3] with Count { .. }` | "cannot find type 'T'" at the binder (B582) |
| p16 | `impl Option<[type T; 2]> with Count` | the same, nested |
| p02 | `impl [i32; 3] with Count { fun count(self) { self[0] + self[1] + self[2] } }` | `6` |
| p20/p21 | two impls `[i32; 2]`, `[i32; 3]` of one trait, called directly and through `fun sum_of<T: Total>(value: T)` | `3`, `6`; natively two instances `sum_of_9875_0(.. [i32; 2])`, `sum_of_9875_1(.. [i32; 3])` |
| p06/p26 | `fun first<T>(values: [T; 3]): T` at `[i32; 3]`, `[str; 3]`, `[0; 3]` | `7`, `x`, `0`: a generic ELEMENT works in a function |
| p15 | `fun keep<T>(value: T): T` at `[i32; 3]` and `[i32; 4]` | `3`, `4`: a whole-type parameter takes any length (and can do nothing array-shaped with it) |
| p17 | `first<T>(values: [T; 3])` at `[i32; 4]` | "Expected [T; 3], but got [i32; 4] instead." |
| p03 | `impl [i32; _] with Count` | parse: "found '[' expected a type" |
| p24 | `impl [i32; type N] with Count` | the same |
| p07 | `fun total<const N>(values: [i32; N])` | parse: "found '[' expected a type in parameter type" |
| p38 | `fun total<const N>(values: List<i32>)` | parse: "unclosed `<` in generic parameters" |
| p04 | `let SIZE = 4; .. let a: [u8; SIZE] = ..` | parse: "found '[' expected a type in type annotation" (find E?1) |
| p05/p39 | `[0u8; SIZE]` (`const let SIZE = 4`), `[0; n]` (local) | "an array length must be a non-negative integer literal (a `const` length is not supported yet)", then p05 cascades: "index 0 is out of range for an array of length 0 (valid indices are 0 to 0)" (E?1) |
| p18b | `[i32; 3.0]` | the same refusal, then "this array literal has 3 elements, but its type is `[_; 0]`" (E?1) |
| p18/p37 | `[i32; 3u8]`, `[i32; 3f64]`, `[0; 2i8]` | accepted as lengths 3, 3, 2 (E?1) |
| p08 | `xs.push_many(a)`, `a: [i32; 3]` | "'[i32; 3]' does not implement trait 'Items<i32>'" (A161) |
| p09 | `a.iter()` | "[i32; 3] has no method 'iter'"; `for v in a` works |
| p10/p29 | `let m: usize = a.len();` / `fun size(self): usize { self.len() }` | "Expected usize (an index: …), but got i32 instead" (B?1) |
| p36 | `xs.len() + a.len()` | "`+` adds two values of the same type, but the operands are `usize` and `i32`" (B?1) |
| p32 | `a[a.len() - 1]` | checks, JS `3`; natively rustc refuses `usize - i32` (B?1 meets B?2) |
| p41/p42 | `xs[one()]`, `xs[n.max(0)]` with `i32` answers; `xs[minus_one()]` | check clean (a typed `let i: i32` is refused, p35); `minus_one()`: JS "the index is -1", natively "the index is 18446744073709551615" (B?2) |
| p11/p11b | `let a: [i32; 3] = xs;` / `let xs: List<i32> = a;` | "Expected [i32; 3], but got List<i32>" and the converse; no conversion exists |
| p12 | `a[1..3]` | parse: "expected a field or method name after `.`"; there is no range syntax |
| p19/p34 | `a == b`; `[derive(PartialEq)]` over a `[u8; 4]` field | "type '[i32; 3]' does not implement the `PartialEq` operator; add `impl [i32; 3] with PartialEq`" |
| p13 | F109's own repro | **`1` on both backends**: emitted `let fixed_9881 = [(1i32), (2i32), (3i32)];` |
| p14/p27/p28/p31 | `[0; 4]`, a returned `[5; 2]`, `[i32; 0]`, `dbg(fixed)` | identical on both backends |
| p23 | `List<[i32; 2]>` push and read | `3` both |
| p22/p30 | a struct with a `rgba: [u8; 4]` field | JS `255`; natively rustc E0277 "the trait bound `[u8; 4]: Js` is not satisfied" in the struct's emitted `Js` impl (find F?1) |
| p40 | `mut big = [0; 4000000]` | JS `7`; natively "thread 'main' has overflowed its stack" (find F?2) |
| p25 | `a[3]` on `[i32; 3]` | compile error, the literal out-of-range check |

Read in the tree:

- **The length is a `usize` in the type** (`type_.rs:119`: `Array(TypeId, usize)`). The parser
  takes only a number token (`parse_array_length`, `parsing.rs:7768`, inside an `attempt`, so a
  name fails the whole `[..]` type and the type parser reports the `[`). The analyzer reads it
  with `array_length_literal` (`analyzer.rs:36910`), which takes any suffix and answers `0` on
  failure. `Expr::Repeat(Id, usize)` and `Expr::ArrayLen(Id, usize)` carry it as well.
- **114 `Type::Array` sites in the compiler's sources**: analyzer.rs 75, vilan-rust 14,
  transformer 4, bindgen 4+2, impl_select 5, printer 3, hint/hover labels 3, and one each in
  mono, const_eval, context, contract_hash.
- **The comparators compare lengths by value**: `reconcile_type` (`:47053`, "unify only at the
  SAME length"), `compare_type_rigid` (`:47469`, B177's arm), `impl_subject_matches`
  (`:21851`), impl_select's `subject_shape_matches` (`:110`) and `instantiation_agrees`'
  `elements_agree` (`:730`).
- **Selection already binds THROUGH an array's element**: `bind_subject`'s array arm
  (`impl_select.rs:652`, "`[T; n]` against `[i32; n]` binds `T = i32`"), and
  `collect_subject_binders` in both files (`analyzer.rs:21890`, `impl_select.rs:457`). The
  registration walk that declares the binder does not (`register_subject_binders`,
  `analyzer.rs:36157`: arms for a binder, generic arguments, tuples and closure types, no
  `Node::ArrayType`). That missing arm is B582. The parser's selector walk has the arm
  (`collect_selector_binders`, `parsing.rs:128`).
- **Mono keys write the literal**: `Arr[` element `;` n `]` in the JS emitter
  (`transformer.rs:12868`) and in vilan-rust (`lib.rs:1864`). `rust_type` renders
  `[{element}; {length}]` (`lib.rs:2378`).
- **`len` is an intercept, not a member** (`analyzer.rs:52377`): ahead of method lookup, an
  array subject's `len` resolves to `Expr::ArrayLen(subject, n)`, typed
  `primitive_struct_type("i32")` (`:44119`). The JS emitter folds a pure subject to the literal
  and otherwise reads `.length` in place (`transformer.rs:7902`).
- **The precedent for "generic over a count"** is the tuple family: `T: (2..)`, the bound
  `"(" [NUMBER] ".." [NUMBER] [":" type] ")"` (`spec/grammar.md` §3.3, `tuple-bound`), and
  `impl type T: (2..) with Tuple { external fun len(self): usize; .. }`
  (`std/src/tuple.vl:68`), an intrinsic whose emission reads the instance's concrete arity.

## 2. What "every length" needs (A163's four, located)

| A163's need | where it lands today | what changes |
|---|---|---|
| (1) a length binder or wildcard in subject position | `parse_array_length` takes a number only; `register_subject_binders` has no array arm | the length position takes `_`, `const IDENT`, a name, or a number (§4); the walk gains the arm (B582) and registers a length binder |
| (2) the comparators admit it | five comparators compare `usize`s | they compare the length **ids** as they compare any type argument: a length hole matches any length in shape matching, binds it in `bind_subject`/`reconcile_type`, and is rigid in `compare_type_rigid` |
| (3) mono keys by the receiver's length and substitutes it into `self` | keys write the literal | unchanged in form. The key writes the substituted length, which is a `Length(n)` after substitution, so `Arr[i32;3]` stays byte-identical. An unsubstituted one writes `G<id>`, as a generic does |
| (4) what `self.len()` means inside | the intercept needs a `usize` | `Expr::ArrayLen(subject, length_id)`, typed `usize`, folded at emission from the instance's substitution (JS may always read `.length`) |

Needs (2) and (3) are where the representation decides the cost. The rest of the paper follows
from §3's choice.

## 3. The representation

Three ways to carry a length that is not yet a number:

| | `Type::Array(element, length)` with … | binding a length | cost |
|---|---|---|---|
| **R1** | `length: ArrayLength`, an enum `Fixed(usize) \| Param(TypeId)` | a SECOND map beside `SubstitutionContext`, threaded through `reconcile_type`, `bind_subject`, `substituted`, both key writers and every caller | the 114 sites change shape AND every substitution path doubles |
| **R2** | `length: TypeId`, resolving to `Type::Length(n)` or to a `Type::Generic(c)` whose constraint is marked length-kinded | the existing map: `N ↦ Length(3)` is one more entry | the 114 sites read the length through one helper (`array_length(id) -> Option<usize>`); nothing else new |
| **R3** | unchanged `usize`, plus a wildcard admitted only in impl subjects (the head matches any length, `Self` is the receiver's concrete type) | none; the instance is keyed by the concrete receiver | no name for the length; a generic body still needs SOME type for `self` before mono, so it needs a "length unknown" value anyway, which is R1's `Param` |

**Recommendation: R2.** It is the only option where A163's (2) and (3) cost nothing beyond
the fan-out. Named lengths (§6) fit it too: `[u8; SIZE]` across an import is a length id that
resolves when the import does, the way a named type's id is resolved late (`walk_type_node`'s
mapped-type arm already defers ids to `build()`). R3 is the narrow door alone. It cannot
relate two lengths (`zip(a: [T; N], b: [U; N])`), and it still needs R1's placeholder.

`Type::Length(n)` is not a value type. It never stands where a value's type stands, and it
prints as the number. Two kind checks keep it there: a length binder written as a type (`let
x: N`) is refused ("`N` is a length, not a type"), and a type written as a length (`[i32;
T]`) is refused the other way. Identity is numeric: `[u8; SIZE]` with `SIZE = 4` is
`[u8; 4]`, and diagnostics print `[u8; 4]`.

The contract hash (`contract_hash.rs:208`) writes the resolved number, so an rpc signature
holding `[u8; 4]` keeps its hash (a pin).

## 4. The grammar

```text
array-type   = "[" type ";" array-length "]" ;
repeat       = "[" expression ";" array-length "]" ;           (* the literal *)
array-length = NUMBER                    (* unsuffixed or `usize`-suffixed, §5.6 *)
             | IDENT                     (* a const parameter, or a named length, §6 *)
             | "_"                       (* impl subjects only: an anonymous length binder *)
             | "const" IDENT ;           (* impl subjects only: a named length binder *)
generic-param = … | "const" IDENT ;      (* NEW: `<T, const N>` *)
generic-arg   = type | NUMBER ;          (* NEW: `zeros<4>()`, `Matrix<2, 3>` *)
```

- **In an impl subject** the length position introduces a binder the way the element position
  does: `[type T; _]`, `[type T; const N]`, `Option<[type T; const N]>`. `_` and `const N`
  elsewhere are refused with B294's sentence: a binder is introduced in an impl subject or a
  generic list, nowhere else.
- **In a generic list** `const N` declares a length parameter: `fun total<const N>(values:
  [i32; N])`, `struct Ring<T, const N> { slots: [T; N], at: usize }`. A use of `N` is the IDENT
  arm.
- **A number as a generic argument** is new (`zeros<4>()`). A NAME as a generic argument is
  read as today's type path and resolved by the parameter's kind: at a `const` position it
  must name a length (§6), at a type position a type. No expression is admitted (`f<{2 *
  K}>()` is not a form).
- `[type T; const N]` reads "an array of any `T`, of any length, call it `N`". It is the impl
  head's spelling of `<T, const N>`, the way `Option<type T>` is the head's spelling of `<T>`.

## 5. The rules

### 5.1 What `const N` means (fixed-arrays.md §7's debt, answered)

- **A length parameter, monomorphized like a type.** Each distinct binding is an instance,
  keyed as `Arr[..;n]` is keyed today. Two bindings are the same exactly when the numbers are.
- **Only lengths.** No other value may be a generic argument: no strings, no structs, no
  enum values, no `i32`. Nothing in the estate asks for one. Widening it later is
  `<const K: T>`, and the bare form keeps meaning a length.
- **Unconstrained in v1.** `N` ranges over `0 ..= usize::max_value()`. A bound such as "non-empty"
  would reuse the tuple family's `(lo..hi)` grammar (`const N: (1..)`). None is proposed
  until a std signature needs one (Q3).

### 5.2 Inference

A length binds wherever a type argument binds:

- **From an argument**: `total(row)` with `row: [i32; 3]` binds `N = 3`.
- **From a directed literal**: `total([1, 2, 3])`. The literal's expected type `[i32; N]`
  directs it to an array (`infer_type_inner`'s context-direction arm, `:43815`), and its
  element count binds `N`. A bound `N` checks the count as today ("this array literal has 3
  elements, but its type is `[_; 4]`").
- **From the expected type**: `let z: [i32; 4] = zeros();`.
- **Explicitly**: `zeros<4>()`.
- **Two uses of one `N` must agree**: `zip<T, U, const N>(a: [T; N], b: [U; N])` at `[i32; 2]`
  and `[str; 1]` is refused "Expected [str; 2], but got [str; 1]". Two `_` are independent.
- A length nothing binds is refused at the call by B580's rule (R-c): "cannot infer `N` …
  write the type, or `zeros<4>()`".

### 5.3 Inside a length-generic body

- `N` (when named) is a **`usize` value** in expression position, and `self.len()` (any
  spelling) is the same value. Both are `Expr::ArrayLen`-style folds resolved per instance:
  the literal where the instance is known, `.length` on JS where the subject is side-effectful
  (today's rule, `transformer.rs:7902`), the literal or Rust's `.len()` natively.
- `[value; N]` is a repeat of the parameter's length. It emits as today with the instance's
  number.
- `for x in self` and `self[i]` (runtime-checked) work at element `T`.
- **Refused while the length is a parameter**: a literal out-of-range index (`self[3]`, since
  there is no length to check against at that point; the runtime check stays), and an array
  binder `let [a, b] = self` ("a destructuring needs the length; this array's is `N`").
- **A `const` expression may not read `N`**, because the const pass evaluates once per site and
  `N` differs per instance. The free-variable refusal names it: "`N` is a length parameter;
  it is fixed per instance, not at this site".

### 5.4 Selection and specificity

A length hole is a hole. `subject_shape_matches` answers yes from `[type T; _]` to `[i32; 3]`
and no in the other direction, so `impl [i32; 3] with X` outranks `impl [type T; _] with X` by
the existing specificity order (`method-resolution.md` §13.4(a), whose first tier is exactly this asymmetry), with no new rule. `ImplSubjectBucket::Array`
(`analyzer.rs:10790`) is already one bucket for every array.

### 5.5 `len()` answers `usize`

Fixed-arrays §10 typed `len()` as `i32` "matching `List.len()`". I5 S2 (v0.41.0) moved every
std length to `usize`. `ArrayLen` is a compiler fold, not a std signature, so the census did
not see it, and it still answers `i32` (B?1). The language now has `List::len(): usize`,
`Tuple::len(): usize` and `[T; n].len(): i32`. The type checker says `i32` while the native
emission renders Rust's `usize` `.len()`, so p32 checks and then rustc refuses it. This is
fixed independently (S0b), before any of the rest.

### 5.6 The length literal

A length is a count, so its literal is unsuffixed or `usize`-suffixed. Today any suffix is
accepted (`3u8`, `3f64`, `2i8` are lengths, p18, p37) and only a fraction is refused. The refusal for a
non-literal length names what IS admitted (§6) and does not cascade: the substituted `0`
produces p05's "valid indices are 0 to 0" and p18b's `[_; 0]` (E?1).

## 6. Named lengths and the staging fork

The fork, from fixed-arrays.md §7: const-eval is post-analysis (it "refuses to run on any
diagnostic, assembles mini-programs from the analyzed program"), and a length is needed while
the program is analyzed. R2 settles WHEN a length is needed: when the type's id is resolved.
For a literal that is the walk. For a name it is name resolution in `resolve_world`, which
precedes the fixpoint. For a parameter it is a binding made during the fixpoint like any
other. So the fork only bites a length that needs EVALUATION.

**Which names a length may be, without const-eval:** an immutable binding (`let` or `const
let`, at any scope the name resolves in, imported included) whose initializer is
- an integer literal, unsuffixed or `usize` (`const let SIZE = 16;`), or
- another such name (`const let ROW = SIZE;`), with a cycle refused.

This is `const_eval::classify`'s literal arm (`const_eval.rs:2801`: an immutable binding whose
initializer is a literal is `Known::Ok`), read syntactically at resolution. A length is
compile-time-known by the same definition a `const` expression already uses, so there is
one definition, which is const-eval.md §9.1's argument for the free-variable rule.

**Refused, with the reason:** `const let SIZE = 2 * K;`, `const let SIZE = table().len();`, a
`mut`, a parameter. "An array length is a literal, a const parameter, or a name bound to a
literal; `SIZE`'s initializer needs evaluating, and const evaluation runs after the program
is typed". A syntactic integer folder (`+ - * / %` over literal-named lengths, a DAG with no
evaluator) would admit `2 * K` and stays out of v1 (Q4). A STAGED analysis (const-eval
before types) is not proposed. Nothing in the estate asks for it, and it would split the
analysis in two.

Why not `const let` only: `const let SIZE = compute();` is a `const let` that still cannot be
a length, so the keyword does not mark the line that matters. The initializer's shape
does. The steer at a refused `let` name says both: "bind it to a literal; `const let` keeps
it compile-time".

## 7. The narrow door: `impl [type T; _] with Items<T>`

The door is the anonymous binder of §4. Once R2 and the head grammar exist, A161 is exactly:

```vilan
impl [type T; _] with Items<T> {
	fun push_onto(own self, target: &mut List<T>) {
		for item in self {
			target.push(item);
		}
	}
}
```

**It is a special case of `<const N>`**, in the same sense that `Option<_>` is a special
case of `Option<type T>` (B294): the parameter exists, and the author declines to name it.
Building the door alone would still take all four of A163's changes (the binder, the
comparators, the key, the `len` fold). The only work it saves is the generic-list form of
§4 and the inference of §5.2, which is S3. So the ruled order holds: S2 ships the head with
both spellings, and S3 adds generic lists.

## 8. Mono and the two emitters

### 8.1 Keys

The key writers stay as they are and write the substituted length. Pinned: the corpus and both
native censuses are byte-identical through S1 and S2, because no estate program has a
parametric length.

### 8.2 JS

An array is a JS array, so a length-generic body reads the same for every length. Each
instance is still emitted separately: per-length instances are what the key gives today
(p21's two `sum_of` instances), and erasing the length from the JS key would be an optimization
with a correctness condition (the body must not fold `N` to a literal). That waits for a
measurement that shows the code size matters (Q11).

### 8.3 Native: `[T; N]`, not `Vec`

F109 asked whether to "lower a list literal whose expected type is `[T; n]` to a Rust array
literal, or render `[T; n]` as `Vec<T>` throughout". F100 (v0.46.0, CHANGELOG: "a list
literal a `[T; n]` position directs is an array, not a `Vec`") did the former. F109's repro
prints `1` on both backends (p13), so it should close on native-49's confirmation. **Keep
`[T; N]`.** Inline storage is the reason fixed arrays exist (fixed-arrays.md's preamble), and
monomorphization means the emitted Rust never needs Rust's const generics: every instance is a
concrete `[i32; 3]`. vilan-rt's own helpers may use them (`impl<T: Json, const N: usize> Json
for [T; N]`, `vilan-rt/src/lib.rs:1862`).

Two native holes remain, both outside this design:
- **F?1**: a struct with an array field does not build. The emitted `Js` impl casts `&self.rgba
  as &dyn vilan_rt::Js`, and vilan-rt has no `Js` for `[T; N]` (p30). One impl in vilan-rt
  fixes it.
- **F?2**: a large array lives on the stack. `[0; 4000000]` aborts natively with a stack
  overflow while JS prints `7` (p40). Inline is right for a pixel and wrong for a 16 MB table;
  the fix is to keep the type and box the storage (`Box<[T; N]>`) above a size threshold
  fixed in the emitter.

## 9. Conversions, slicing, and the std surface that follows

None of these is a language change once S2/S3 exist. They are std, and each consumer below
is what the any-length head buys.

| surface | written as | needs | note |
|---|---|---|---|
| `Items<T>` (A161) | §7's impl | S2 | `push_many(arr)`; p08's refusal goes |
| `arr.to_list(): List<T>` | `impl [type T; _]` inherent | S2 | explicit; no coercion (p11b stays refused) |
| `list.to_array(): Option<[T; N]>` | `fun to_array<const N>(self)` on `List`, an intrinsic (JS `xs.length === N ? Some(xs.slice()) : None`; Rust `<[T; N]>::try_from(v).ok()`) | S3 | fallible, so `Option` (Q9); `N` from the expected type or `to_array<3>()` |
| `PartialEq`/`Eq`, `Hashable` | `impl [type T: PartialEq; _] with PartialEq` … | S2 | p19/p34's refusal goes; `HashMap<[u8; 4], ..>` keys |
| `Debug` (E283's array half) | `impl [type T: Debug; _] with Debug` | S2 | `dbg` already prints arrays (p31) |
| `iter()` | `impl [type T; _]` inherent | S2 | p09; std chooses the iterator type |
| slicing | `xs.slice(from, to): List<T>` on `List` and arrays, a copy | nothing new | see below |

**Slicing does not want a range type for this.** Today there is no range syntax (p12: `a[1..3]`
dies in the parser, and `..` is taken by the tuple bound `(2..)` and the call spread
`draw(..pair)`). `std::range::Range` is an `i32` iterator struct (`std/src/range.vl`), and
`Bytes::slice(from: usize, to: usize)` is the only slice in std. A sub-array with a static
length (`a[1..3]: [T; 2]`) needs length arithmetic at the type level (§6's folder, then
`to - from`), which this paper does not propose. A slice of an array is a `List` copy (value
semantics, no slice views), written as a method like `Bytes::slice`. A range LITERAL
`a..b` is a language item of its own, if wanted (Q10).

## 10. The estate

| tree | `.vl` files (+ book fences) | `[X; n]` sites | lengths | non-literal |
|---|---|---|---|---|
| std | 70 | 0 | — | 0 |
| corpus (`vilan/test`) | 148 | 7, all in `fixed-arrays.vl` | 3, 2, 2, 4, 3, 3, 2 (+ the nested `[[i32; 2]; 2]`'s inner 2) | 0 |
| the book (`docs`, `vilan` fences) | 64 fences | 2, `tour/values-and-types.md:276-277` | 4, 3 | 0 |
| examples | 40 | 0 | — | 0 |
| benchmarks, macro_std | 8, 3 | 0 | — | 0 |
| kolt (a copy of the working tree, `src/lucide` and `src/search-dict` included) | 32 | 0 | — | 0 |
| vilan-website (whole checkout) | 21 | 0 | — | 0 |
| vilan-playground | 6 | 0 | — | 0 |

Every length in the estate is a literal ≤ 4, and no impl anywhere has an array subject. The
compiler's own Rust tests hold the rest of the arrays (`tests/inference/tuples.rs` alone
spells 60). **Nothing breaks**: the representation change (S1) is meant to be
byte-identical, and the new forms are additive. **B?1's `usize` is breaking in principle**,
but the estate has 4 `.len()` calls on arrays (3 in `fixed-arrays.vl`, 1 in the tour), all
passed to `print`, so no edit and no golden moves. The compiler's pins that assert the `i32`
change with it.

## 11. B582 alone

**The fix**: `register_subject_binders` (`analyzer.rs:36157`) gains
`Node::ArrayType(element, _) => self.register_subject_binders(element, scope_id)`. XS, solver.
Selection already binds through the element (`impl_select.rs:652`), and
`collect_subject_binders` already descends arrays in both files. It is queued in solver-49 and
waits for nothing in this paper.

**What it unlocks on its own:**
- Element-generic impls **at one literal length each**: `impl [type T: PartialEq; 2] with
  PartialEq`, `impl [type T: Display; 3] with Display`, the nested `impl Option<[type T; 2]>`
  (p16). Each instance is keyed by `T` at that length, as p06 already shows for functions.
- **Not A161, and not any "every length" impl.** A std `Items<T>` would be one impl per
  length, the table Rust shipped for lengths 0 to 32 before its const generics. This paper
  recommends against shipping such a table: it fixes an arbitrary ceiling into std and adds
  N impls to every array selection.
- Structurally it is the first brick: the arm it adds is the arm S2 extends to register the
  LENGTH binder.

## 12. Interactions

- **M110 / the analyzer core.** S1 changes a `Type` variant's shape across the analyzer, mono
  and both emitters. Under R-a it lands after the S5 spike's verdict (Order 50 or later), and
  as an analyzer change it runs `ci-local.sh perf` and keeps late writes at zero. S0 (B582)
  and S0b (B?1) are small enough to ride solver-49 now.
- **B580 (R-c)**: an unbound length is a hole like an unbound type; the "cannot infer" message
  carries the explicit `f<4>()` form.
- **B571 (`as`)**: `[1, 2, 3] as [i32; 3]` directs a literal exactly as an annotated `let`
  does. With S3, `[1, 2, 3] as [i32; N]` inside a length-generic body binds nothing new. The
  ascribed type ends at its `]` (type-ascription.md §5.3).
- **The tuple family (A122)**: `Tuple::len(self): usize` is the per-instance intrinsic model
  for §5.3. The `(lo..hi)` bound is the model for a length bound if Q3 is ever reopened. A
  tuple is heterogeneous and an array homogeneous, so neither replaces the other.
- **E283** (debug-49) wants `[T; n]` "beside `List`": that half waits on S2; the other types
  do not.
- **Wire / rpc**: an `[u8; 4]` field's hash is unchanged by S1 (pinned). A length-generic rpc
  signature is not a thing: rpc signatures are concrete.
- **const-eval**: §5.3's refusal. A `const let` holding an array (`const let T: [i32; 3] =
  const build();`) is unaffected.

## 13. Finds (filed to `newitems49-papers.json`, repros in `papers-49/finds/`)

1. **B?1**: `[T; n].len()` answers `i32` where every other length is `usize` (I5 S2 missed
   the compiler fold). `let m: usize = a.len()` and `xs.len() + a.len()` are refused, and
   `a[a.len() - 1]` checks and is refused by rustc. `finds/array_len_answers_i32.vl`.
2. **B?2**: the subscript's `usize` check passes an index whose type is not known when the
   subscript resolves (`xs[one()]`, `xs[n.max(0)]`, `i32` answers). Nothing checks it again,
   so a negative index panics with "-1" on JS and "18446744073709551615" natively.
   `finds/subscript_index_unchecked_call.vl`.
3. **E?1**: a non-literal array length has four poor answers. In type position the parser
   says "found '[' expected a type" (plus a cascade, "cannot find 'a'"). In a repeat literal
   the refusal is followed by cascades off the substituted `0`. Any suffix makes a length
   (`3f64`, `2i8`). The empty array's out-of-range message says "valid indices are 0 to 0".
   `finds/array_length_*.vl`.
4. **F?1**: natively a struct with an array field does not build (no `Js` for `[T; N]` in
   vilan-rt). `finds/native_struct_array_field.vl`.
5. **F?2**: natively a large fixed array overflows the stack. `finds/native_big_array_stack.vl`.
6. **D?1**: `spec/grammar.md` §3.9's `type` production has no array type, and §3.6's `list`
   production has no repeat literal. The spec does not state the grammar of `[T; n]` at all.
- **Not filed, stated**: F109 no longer reproduces on 0.46.0 (§8.3); native-49 owns its close.

## 14. Open questions, each with a recommendation

- **Q1. The representation.** R2 (a length is a type-level number, `Type::Array(TypeId,
  TypeId)`), R1 (an inline enum and a second binding map) or R3 (an impl-subject wildcard
  only). **Rec: R2.** It reuses the substitution map, the binders and the key writers, it
  serves named lengths across imports, and it costs one helper at the 114 sites.
- **Q2. The spellings.** `[type T; _]` and `[type T; const N]` in impl subjects; `<const N>` in
  `fun`/`struct`/`enum`/`trait` generic lists; a number as a generic argument (`zeros<4>()`).
  **Rec: yes.** `const` because the parameter is a value; `_` because B294 already means
  "a binder I decline to name".
- **Q3. The constraint form.** Bare `<const N>` means a `usize` length, with no annotation, no
  other value kinds and no bounds in v1. **Rec: bare.** `<const K: T>` and `const N: (1..)`
  stay open, spelled so they could be added without breaking.
- **Q4. Named lengths.** An immutable binding (`let` or `const let`, any scope, imports
  included) whose initializer is an integer literal or another such name: `classify`'s
  literal line, resolved before the fixpoint. **Rec: yes.** Arithmetic (`2 * K`) is refused,
  and a syntactic folder is a later item only if a program asks.
- **Q5. `N` as a value.** Inside a body `N` is a `usize` expression, folded per instance, and
  a `const` expression may not read it. **Rec: yes.**
- **Q6. `len()`'s type.** `usize`, now, independent of the rest (B?1). **Rec: yes, S0b**:
  zero estate edits.
- **Q7. The narrow door first?** Ruled no (A163 goes with I2). This paper finds the door
  costs the same four changes, so **Rec: S2 ships `_` and `const N` together**, and S3 the
  generic lists.
- **Q8. Structs and enums generic over a length** (`struct Ring<T, const N> { slots: [T; N] }`).
  **Rec: yes, in S3**: the same generic-list production and the same key. The estate asks for
  none, so it may trail S3's functions in the same slice.
- **Q9. Conversions.** `arr.to_list()` and `list.to_array(): Option<[T; N]>`, explicit
  methods, no coercion (fixed-arrays.md §7 said "not coercion"). **Rec: `Option`**, not
  `Result`: the one way to fail is the length, and the caller knows both lengths.
- **Q10. Slicing.** **Rec: out of I2.** Slicing is a `slice(from, to): List<T>` copy method on
  `List` and arrays (std, S), and a range literal `a..b` is its own language item if wanted.
  Static sub-array types (`[T; 2]` from `a[1..3]`) are not proposed.
- **Q11. JS instances per length.** **Rec: keep per-length instances** (the key as it is).
  Erase the length from the JS key only after a measurement shows the code size matters, and
  only for bodies that never fold `N`.
- **Q12. Native rendering.** **Rec: keep `[T; N]`**, close F109 as fixed by F100 (p13), and
  box the storage above a threshold (F?2).
- **Q13. std's first wave after S2.** **Rec: `Items` (A161), `PartialEq`/`Eq`, `Hashable`,
  `Debug` (E283's half), `to_list`, `iter`.** `to_array` comes with S3; `Wire`/`Display`
  wait for someone to ask.

## 15. Slices

| Slice | Content | Size | Needs | Gate |
|---|---|---|---|---|
| S0 | **B582**: the registration walk's array arm; pins: `impl [type T; 3]`, `impl Option<[type T; 2]>`, a bound on the element, both backends | XS | — | solver-49 (now) |
| S0b | **B?1**: `ArrayLen` typed `usize`; pins (p10, p29, p32 natively); the compiler's `i32` pins move | XS | — | solver-49 (now); breaking in principle, estate 0 edits |
| S1 | **R2**: `Type::Array(TypeId, TypeId)`, `Type::Length(n)`, the length helper; `Expr::Repeat`/`ArrayLen` carry ids; the 114 sites; kind checks; no behaviour change | M | — | after the M110 S5 verdict (core alone); corpus + both native censuses + copy census byte-identical; contract hash unchanged (pin); `ci-local.sh perf`; late writes 0 |
| S2 | **Heads**: `_` and `const N` in impl subjects (parser + registration); comparators bind/hole/rigid; the per-instance `len`/`N` fold on both emitters; §5.3's refusals; specificity (§5.4) | M | S1, S0 | the native differential over a length-generic impl at three lengths; pins per comparator, red first |
| S3 | **Generic lists**: `<const N>` on `fun`/`struct`/`enum`/`trait`; numeric generic arguments; inference from arguments, directed literals and expected types (§5.2); B580's message | M | S2 | pins per inference door; both backends |
| S4 | **Named lengths**: §6's names (local, top-level, imported, chained), resolved before the fixpoint; E?1's refusals and the length-literal suffix rule | S | S1 | pins per name shape and per refusal; ledger rows |
| S5 | **std**: Q13's list; A161 and E283's array half close; the native differential | S | S2 (S3 for `to_array`) | `check_scope_differential`; both backends |
| S6 | **Book and spec**: grammar §3.9 and §3.6's `list` production (D?1), types §5.x (lengths, `const N`), the tour's arrays paragraph | S | S2–S4 | — |

Native F?1 and F?2 are independent of every slice (native lane).
