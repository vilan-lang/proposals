# The unit literal (B363) — vilan has one, and it is spelled `void`

Tracker B363. Written by lane papers-39 of Order 39, on vilan `next` @c3f7d1a3
(`vilan 0.40.0 (c3f7d1a38)`), which is the toolchain every result below was
measured on. The owner is asked to rule §7 (five questions); the build, if it is
taken, is §8 — S1 (S) then S2 (XS) then S3 (S, breaking).

Related: A107 (the awaited `void` rpc return, CLOSED Order 38 —
`transport-rpc.md` §9.6c, whose `Option<RpcError>` rests on this item's
premise), A120 (`service-as-http-api.md`, this lane's sibling paper),
`proposal/try-and-lift.md` (the `!` operator, whose `Try<T, void>` impl is the
unit literal's oldest customer), `spec/types.md` §5.1 and §5.6,
`spec/lexical.md` §2.2–§2.3, `spec/grammar.md` §3.3 and §3.9, E208 (a refused
written type argument — the neighbour of the `internal:` error §5.6 records).

Probes: `scripts/integration/sweeps/order39/papers-39/probes/b363_positions/`
(eight programs, each with its captured output — four green, four red by
design), `probes/b363_rpc_void/` (a package) and
`probes/find_json_internal/` (§5.6's find), re-runnable with
`probes/run_all.sh`. Every claim below that a probe can check is named beside
its probe.

---

## 1. The answer up front

B363 says: *"vilan has NO UNIT LITERAL: `Ok(())` does not parse … so
`Result<void, E>`, `Option<void>` and any generic instantiated at nothing have
no constructible value."*

**The first clause is true. The rest is false, and the compiler, the
specification and std all already say so.**

- `parsing.rs`'s own comment, on the function that reads it: *"A single-token
  literal, including `void` (the unit value — a bare `void` identifier in
  expression position)."*
- `spec/types.md:27`: *"**`void`**: the unit; one value, also written `void`."*
- `spec/lexical.md:194`, under **Other literals**: *"`void` (the unit value; a
  contextual identifier, not a keyword)."*
- And the load-bearing one — `std/src/option.vl:19-29`, the implementation of
  the `!` operator on an `Option`:

  ```vilan
  impl Option<type T> with Try<T, void> {
  	fun verdict(self): Verdict<T, void> {
  		match self {
  			Some(let value) => Verdict::Good(value),
  			None => Verdict::Bad(void),        // ← a generic, instantiated at
  		}                                       //   void, CONSTRUCTED
  	}

  	fun from_bad(bad: void): Option<T> { None }
  }
  ```

  The comment above it reads *"its residual `void` (the unit — the absence
  carries no information)"*. That is the prelude, in the machinery behind `!`,
  building exactly the value B363 says has none. It is the one `void` value site
  in the whole estate (`grep` over every `.vl` in the tree) and it has been there since try-and-lift
  shipped.

So `Ok(void)` works. `probes/b363_positions/04_void_expression.vl`:

```
Ok(void).is_ok()=true Some(void).is_some()=true None.is_none()=true
```

And every position the item asks about works —
`probes/b363_positions/05_every_position.vl`, nine cases, verbatim:

```
1. `void` as a declared-void function's tail: ok
2. `fun f(): Result<void, E>` + a match on Ok: bound
3. a generic instantiated at void (`id<T>(T) -> T` at void): ok
   (the body ran)
4. a closure returning nothing where `|| T` is expected: T = void
5. a declared `void` PARAMETER, called with `void`: true
6. List<void> holds 3
7. Option<Option<void>>: true
8. `!` through a Result<void, E>: true
9. `.map(|_| void)` — Option<void> from a derivation: true
```

**What B363 actually is, therefore, is not a design question about whether to
have a unit literal. It is three documentation and diagnostic gaps around one
the language has had all along, and one surface — A107's — chosen on a premise
that was never checked past the `()` spelling.**

## 2. The premise check, clause by clause

| the item says | measured |
|---|---|
| `Ok(())` does not parse | **TRUE.** `probes/b363_positions/01` |
| the refusal is *"unclosed ( in expression"* | **FALSE.** It is `found ')' expected an expression`, spanned on the `)`. `01` |
| `Result<void, E>` has no constructible value | **FALSE.** `Ok(void)` and `Ok({})` both build. `04` |
| `Option<void>` has no constructible value | **FALSE.** `Some(void)`. `04` |
| "any generic instantiated at nothing has no constructible value" | **FALSE**, and std relies on the opposite (`Try<T, void>`, §1) |
| A107's stub answers `Option<RpcError>` *because* of the above | the stub does answer that; **the reason is wrong.** `Result<void, RpcError>` is writable and runs — `probes/b363_rpc_void` |

That last row matters more than the others, because A107's CHANGELOG entry says
the shape was *"probed before the surface was chosen"*. It was — and the probe
tested `Ok(())`, which is the one spelling that fails, and concluded a language
fact from it. `probes/b363_rpc_void` is the same probe with `void` in the hole:

```
ack: Ok
ack2: Unavailable
```

from

```vilan
fun call_ack_shaped(ok: bool): Result<void, RpcError> {
	if ok { Ok(void) } else { Err(RpcError::Unavailable) }
}
```

No `Wire` impl is asked of `void` by that: only the ack's `bool` crosses the
wire, and the `Result` is built on the client side after the envelope is read.

## 3. What `void` is, precisely

One value, one spelling, `undefined` at runtime. `probes/b363_positions` plus
the emitted JS for `Ok(void)`:

```js
function okvoid() {
	return [ 0, undefined ];
}
```

— the ordinary `Result` runtime form (`[tag, payload]`) with `undefined` in the
payload slot, because `void` emits nothing and an omitted argument reads
`undefined`. `[void]` emits `[ undefined ]`. There is no boxing, no sentinel and
no special case: `void` is the absence of a value *used as* a value, and JS
already has exactly that.

Three spellings mean it, and they are interchangeable (`04`):

```vilan
let bare = void;              // the literal
let empty_block: void = {};   // a block with no tail — spec/grammar.md §3.5
let inferred = f();           // any call to a void-returning function
```

And `void` is a **contextual identifier, not a keyword** (`spec/lexical.md`
§2.2 lists it among the contextual keywords, and `parsing.rs` matches
`Token::Ident("void")`). §5.3 is what that costs.

## 4. What `void` is NOT: a value with no traits

`probes/b363_positions/06_traits_on_void.vl` is red on purpose, three ways:

```
Error: `==` needs a value on the left, and this operand is `void`: the
expression it comes from produces no value — a function that returns nothing,
an `if` with no `else`, a statement

Error: 'void' does not implement trait 'PartialEq', required by a generic
bound of this call
   [ …/option.vl:277 ] impl Option<type T: PartialEq> with PartialEq {

Error: `+` on `str` concatenates, and `void` has no string form …
```

Read those three together and the whole of B363's real content appears.

- **The direct `void == void` refusal is GOOD and should stay.** It catches the
  common mistake — `if f() == g()` where both return nothing — and its sentence
  names the three ways a reader gets there. `spec/types.md` §5.7 already rules
  it: *"`void` is refused outright: an expression that produces no value has no
  operand to be."*
- **The generic `Some(void) == Some(void)` refusal is a different thing**, and
  it is the one an author would trip over for a real reason: `Option<void>` as a
  presence flag and `Map<K, void>` as a set (which builds today — `08`) both
  want comparison, and neither is the mistake the direct refusal guards.
- **And the two do not have to agree**, because the direct case is refused
  *before* dispatch, in the operator's own arm. An `impl void with PartialEq`
  makes the generic case work and leaves the direct refusal exactly as it is.
  §7 Q3 asks for it.
- `Display` and `Debug` are a different answer: there is nothing to print, and
  the `i"{void}"` refusal already says so well. Q4 declines them.
- `Wire` is the one that must NOT be added, and §6 says why.

The tension the spec carries and this paper is asked to resolve: types.md line
27 calls `void` *"the unit; one value"* and types.md §5.7 calls it *"an
expression that produces no value"*. Both are useful sentences and they
describe the same thing from two ends. The reconciliation, for the spec, is one
sentence: **`void` denotes the absence of information, and a type whose values
carry no information has exactly one value — so it is both "no value" (there is
nothing to read out) and "one value" (there is something to store).** The
operators are refused because reading it out is the meaningless act; a generic
parameter is satisfied because storing it is not.

## 5. Five divergences, all measured

### 5.1 `()` in EXPRESSION position does not parse, and never will

`()` is not in `spec/grammar.md`'s `tuple` production
(`tuple = "(" ( spread | expression "," entry … ) ")"` — the first element is
mandatory), so the parse failure is the spec being followed, not a gap. `01`,
`02`. The refusal's TEXT is what is wrong (§5.2).

### 5.2 The refusal does not name the spelling that works

```
Error: found ')' expected an expression
 4 │     let outcome: Result<void, str> = Ok(());
   │                                          ┬
   │                                          ╰── found ')' expected an expression
```

A reader coming from Rust, Swift or OCaml writes `()`, gets a parser's generic
"expected an expression", and has no path from there to `void` — which is the
entire reason B363 was filed as *"vilan has no unit literal"* by someone who had
read enough of the tree to file it. **This is the item's one certain build**,
and it is a `recover`-shaped arm in the parser: an empty `( )` in expression
position is refused BY NAME —

```
`()` is not an expression: the unit VALUE is written `void`
(`Ok(void)`, `let nothing = void;`), and `()` alone is not a type either —
`spec/types.md` §5.1
```

### 5.3 `()` in TYPE position exists, and nothing can satisfy it

`probes/b363_positions/03`:

```
Error: Expected (), but got void instead.
 5 │     let a: () = void;
```

So the compiler has a distinct `()` type, prints it as `()`, and **nothing
constructs a value of it** — not `void`, not `{}`. `Option<()>` and `List<()>`
are writable as long as they stay empty (`03`, `08`).

Two specification citations disagree about whether it should exist at all:

- `spec/types.md:15` — *"`()` and one-element tuples do not exist as distinct
  types (`(T)` is `T`; the unit is `void`)."*
- `spec/grammar.md:614` — `"(" [ type { "," type } [ "," ] ] ")"` — the
  bracketed list is OPTIONAL, so the grammar admits `()`.

The compiler follows the grammar. `(T)` correctly collapses to `T` (`03`'s
sibling: `let x: (i32) = 1;` builds), so half of types.md's sentence holds and
half does not. **Estate census: zero `.vl` files in the tree name `()` as a
type** (`grep -rn ': ()\|<()>' --include='*.vl' vilan/` → 0), so removing it is
non-breaking.

### 5.4 `void` is missing from the grammar's `literal` production

```text
literal = NUMBER | STRING | "true" | "false" | "null" ;
```

`spec/grammar.md:416`. `void` is not there, while `spec/lexical.md`'s **Other
literals** names it and the parser reads it there. The grammar's `atom` does
cover `IDENT`, so `void` parses *in the grammar* as an ordinary identifier —
which describes a different language from the one that ships, and §5.5 is the
observable difference.

### 5.5 `let void = 3;` binds something unreadable

`probes/b363_positions/07`:

```
 fun main() {
 	let void = 3;
 	let y: i32 = void;   ← Error: Expected i32, but got void instead.
 }
```

The binding is created and is unreachable: `parse_literal` intercepts
`Ident("void")` before the identifier path, so every `void` in expression
position is the literal, whatever is in scope. `lexical.md` §2.2's promise for a
contextual keyword — *"All remain usable as ordinary identifiers elsewhere"* —
is false for this one. Estate census: **zero** `let void`/`mut void`/`fun void`
in the tree. Harmless, and it should be refused at the BINDING (`void` is the
unit literal and cannot be bound) rather than left to fail at the first read.

### 5.6 A find with no `void` in it

Probing §4 turned up an `internal:` error that has nothing to do with this item
and is reported as a find in the lane report. `probes/find_json_internal`:
`Ok<void, str>(void).to_json()` and `Ok<Opaque, str>(Opaque { seed = 1 }).to_json()`
both produce

```
internal: a call resolved to `Json`'s requirement `to_json`, which has no body
… please report this program
```

while the same expressions with the type arguments inferred from an annotation
(`01`, `02` in that directory) refuse cleanly with *"'Opaque' does not implement
trait 'Json'"*. The trigger is **written type arguments on a variant
constructor**, not `void`; it sits beside E208.

## 6. A107's surface, and the breaking edge

If B363 is resolved as §7 recommends, `transport-rpc.md` §9.6c's one stated
reason disappears and the awaited void's stub can answer
`Result<void, RpcError>`:

```vilan
fun call_ack<Tx: Transport>(..): Result<void, RpcError> {
	match call::<bool, Tx>(transport, codec, method, args) {
		Ok(let _ran) => Ok(void),
		Err(let error) => Err(error),
	}
}
```

**Should it?** The case for: every other stub answers `Result<_, RpcError>`, so
a call site handling several methods handles one shape, `!` works through it,
and `Option<RpcError>` reads backwards (`None` is the good case, which is the
opposite of `Option`'s meaning everywhere else in std). The case against: the
`Option` is honest about there being nothing to carry, and moving it is
breaking.

**What must NOT follow, either way: `void` does not get a `Wire` impl.** Today a
user who writes the other spelling is refused precisely
(`probes/b363_rpc_void`, the commented method):

```
return type of `[rpc]` method `try_touch` is `Result<void, str>`, which is not
Wire: every `[rpc]` parameter and return must be Wire (…)
```

That refusal is correct and must survive. An `impl void with Wire` would admit
`[rpc] fun f(): Result<void, str>` as a SECOND awaited-void shape with its own
contract entry (`f()->Result<void, str>;` beside `f()->void;`) and its own reply
encoding, where A107 deliberately made the ack the one shape. `Result<void, E>`
stays a client-side type: nothing about it crosses.

**The breaking surface, enumerated** (this is the whole of it):

| site | what moves |
|---|---|
| `std/src/rpc.vl` `call_ack` | its return type, and two lines of its doc comment (the "no unit literal" paragraph becomes the `Result` rationale) |
| `std/src/rpc.vl` the generator | `.returns("Option<RpcError>")` → `.returns("Result<void, RpcError>")` — one string |
| `docs/guide/services.md:184` and `:198` | the paragraph, and the "for a language reason" sentence, which is no longer true |
| `crates/vilan-core/tests/inference/traits.rs:4032`, `generics.rs:3257` | two doc comments |
| `crates/vilan-cli/tests/service_layer.rs:4399` | the pin's comment and its match |
| **kolt**, `src/model.vl:99` | `fun remove_message(..): Option<RpcError>` → `Result<void, RpcError>`, and its `Err(let error) => Some(error)` arm |
| **kolt**, `src/channel.vl:81` | `if channel.remove_message(..) is Some(let error)` → `is Err(let error)` |

Two vilan source lines, four comments, one pin, two kolt lines. No wire byte, no
contract hash, no golden: the reply envelope is untouched and the contract entry
stays `name(args)->void;` (which is what the server declared, and the server did
not change). Nothing else in the estate calls an awaited-void stub — the census
is the seven rows above and they are all of `grep -rn 'Option<RpcError>'`.

## 7. Open questions, each with a recommendation

**Q1 — a unit literal, `void` as an expression, or nothing?** (the item's own
question)

> **Rec: NOTHING TO BUILD, and the item is a documentation-and-diagnostic
> item.** vilan has a unit literal; it is `void`; the parser, both spec
> chapters and `std::option`'s `Try` impl all already rely on it. What is
> missing is that a reader cannot find it: §5.2's refusal does not name it,
> `guide/`'s type pages do not show it in a value position, and the grammar's
> `literal` production omits it. Admitting `()` as a SECOND spelling is the
> alternative and the recommendation is against it — two spellings for one
> value, and `()` would then mean one thing as an expression and another
> (§5.3) as a type.

**Q2 — the `()` type: delete it, alias it to `void`, or leave it?**

> **Rec: DELETE IT**, and refuse `()` in type position by name ("the unit type
> is written `void`"), which makes the compiler agree with `spec/types.md:15`
> and makes the grammar's optional list mandatory. Zero estate hits, so it is
> non-breaking. Aliasing it to `void` is the alternative and is worse than
> either extreme: it would make `()` legal as a type and illegal as an
> expression, which is the trap that produced this item.

**Q3 — `impl void with PartialEq`?**

> **Rec: YES** (§4). It is total and constant (`void == void` is always true),
> it unblocks `Option<void>` and `Map<K, void>` — both of which already build —
> and it does NOT weaken the direct-operand refusal, because that one fires
> before dispatch, in the operator's own arm. The two diagnostics stay as
> measured: a bare `f() == g()` gets "this operand is `void`", and
> `Some(void) == Some(void)` compares. The alternative is to leave it and tell
> a `Map<K, void>` author to use `Map<K, bool>`, which is a lie in the value.

**Q4 — `Display`, `Debug`, `Hashable` for `void`?**

> **Rec: NO to `Display` and `Debug`; `Hashable` only if a `Set<void>` ever has
> a customer (nothing asks).** `i"{void}"`'s refusal is already the best
> sentence in this area and printing an empty string or `"()"` would make a
> logging bug silent. `Debug` has the same shape with a weaker excuse.

**Q5 — does A107's stub become `Result<void, RpcError>`?** (§6)

> **Rec: YES, as a `breaking` note in the same order as the diagnostic.** The
> uniformity is worth two lines of std and two of kolt: `Option<RpcError>` reads
> inverted against every other `Option` in std (`None` is the success), `!` does
> not work through it, and a call site that handles `add_message` and
> `remove_message` in one `match` currently needs two shapes. And the reason
> recorded in three places for the current shape is not true, which is its own
> argument for moving now rather than after a third place cites it. The
> alternative — keep `Option<RpcError>` and correct the three rationales to
> "because there is nothing for an `Ok` to carry, and `Option` says so" — is
> defensible, costs nothing, and is the right answer if the owner would rather
> not move kolt.

One thing this paper has decided rather than asked, and will re-open if the
owner disagrees: **`void` does not get a `Wire` impl** (§6) — an awaited void
has one wire shape and it is the ack.

## 8. Slices

### S1 — the two refusals and the documentation (S)

`()` in expression position refused by name, pointing at `void` (§5.2); `()` in
type position refused by name (§5.3, Q2); `let void = ..` refused at the
binding (§5.5); `void` added to `grammar.md`'s `literal` production (§5.4) and
to whatever `grammar_sync` checks it against; `spec/types.md` §5.1's sentence
made true by the deletion; §4's reconciling sentence into `types.md` §5.7
beside the operator refusal; one `guide/` fence showing `Ok(void)` and
`Option<void>` in a value position, because a gated fence is how this stops
being rediscovered.

**Exit:** an `assert_fails` pin per refusal with its message asserted (not
`contains`-tested for a substring the old text also satisfies); a green pin for
each of `05_every_position.vl`'s nine rows as an `inference` case; the docs
gate compiling the new fence; `grammar_sync` green against the amended EBNF,
and RED first against the current one (which is the non-vacuity proof, and is
free: the production is missing a token).

### S2 — `impl void with PartialEq` (XS)

Q3. In `std::compare` beside the primitive impls.

**Exit:** `Some(void) == Some(void)`, `Map<str, void>` equality, and a control
pin that a bare `void == void` STILL gets the operand refusal — which is the
whole of what makes S2 safe, and the pin that would go red if the impl were
allowed to reach the operator arm.

### S3 — A107's return type (S, breaking)

Q5. §6's table, in one commit, with the `breaking` note and the CHANGELOG entry
correcting the record.

**Exit:** `service_layer`'s awaited-void pin on the new shape, its ORDER
assertion unchanged (the handler still runs before the ack — that is A107's
content and S3 must not touch it); the contract hash for a void method
byte-identical; the connectionless POST-leg twin of the same pin; the estate
sweep over the merged tree, which is seven rows and is expected to be exactly
seven.

Sizing: S1 S + S2 XS + S3 S. The whole item is one order's afternoon, and S1
alone is what stops it being filed again.

## 9. What this does not do

- **A second spelling.** Q1: `()` is refused, not admitted.
- **`void` as a keyword.** It stays a contextual identifier; §5.5 refuses the
  one binding that could shadow it, which is cheaper than moving a token class
  and than the estate sweep a new keyword would owe.
- **`Never` and `void`.** They are different types with different rules
  (`spec/types.md:29-35`: `Never` unifies by erasure and yields to whatever it
  meets; `void` unifies with `void`) and nothing here changes either.
- **`Wire`/`Json` for `void`** (§6, and §5.6's find is not this item's).
- **A one-element tuple.** `(T)` is `T` today and correctly so; only `()` is in
  question.
