# Opaque returns — what `fun f(): Trait` should hide (B460's opacity)

> Status: **RULED 2026-10-01** — Q1–Q11 as recommended (the owner); the build is queued for Order 46. Drafted 2026-10-01 (R-j: a paper this order,
> nothing built). This is the follow-up B460's build named: "opacity is a later
> slice after a paper". Written by lane papers-45 of Order 45 against
> `vilan 0.42.0 (6e6830dfc)`, reading `next` @6e6830df. Nothing in the compiler
> or std changed. Every claim about today's behaviour is a probe that was run
> (JS, and `--backend rust` where it says so) or a line that was read.
>
> Probes: `scripts/integration/sweeps/order45/papers-45/probes/opaque/`, re-run
> by `probes/run_all.sh <scratch>`, output in `probes/run_all.out`. They are
> cited as `oN`.
>
> Related:
> - B460 (archive: door (i), built at d161af2d) and B253 (the refusal it
>   reversed);
> - B161 (a bare trait at a `let`), B186 (at a parameter), B184
>   (`trait-typed-fields.md`), B461 (nested);
> - B4 and `trait-objects.md` (`dyn`), M88 (devirtualizing `dyn`);
> - E227 (`inlay-hint-abbreviation.md`, the `~Trait` hints);
> - A142 (`reactive-layers.md` §4.3 and §5);
> - B473, B474, B475 (calls through a bound, and `dyn` tables).

## 0. The ask, and the answer up front

B460 shipped door (i). A bare trait written as the return type of a free `fun`
or an inherent method means the ONE concrete type the body produces. The
compiler checks that this type implements the trait and dispatches statically.
The type is **not hidden**: callers hold the concrete type. A trait method's
bare-trait return stays refused. The open question is opacity: should callers
see only the trait?

**The answer.**

1. **Today the annotation hides nothing.**
   - A caller of `fun counter(..): Source<i32>` can call `set` (a `Signal`
     method), bind the result as `SignalCell<i32>`, and pass it where only a
     `SignalCell` is accepted (o1).
   - A diagnostic prints the full node chain,
     `Derive<Distinct<Derive<SignalCell<i32>, i32, i32>, i32>, i32, str>`,
     where the signature says `Pipe<str>` (o7).
   - Changing the body under the same signature breaks a caller in another
     module (o8).
2. **Two defects sit on the way, and they need fixing whichever door is
   ruled.**
   - The annotation's arguments never reach the body, so
     `SignalCell::new(None)` under `Source<Option<i32>>` types as
     `SignalCell<Option<unknown>>`. JS runs it; native refuses to emit it (o2).
   - Native gives every instance of a generic bare-trait-returning function the
     return type of one instantiation, and rustc refuses the result (o5).
3. **Opacity costs nothing at run time on either backend.**
   - The checker hides the type; the emitters reveal it. Dispatch stays static.
   - The JS output is unchanged for a caller that uses only the trait's
     members.
   - Native reveals per instantiation in mono.

   What it does cost:
   - one new `Type` variant, smaller than `dyn`'s (which needed tables);
   - callers lose the concrete type's own members;
   - two functions returning the same concrete type return two different types.
4. **The recommendation is to make the trait annotation opaque now (door
   (ii)), reversing door (i)'s "not hidden".** Three reasons:
   - **The flip costs nothing today.** Zero bare-trait returns exist in std,
     the examples or kolt.
   - **The transparent reading already has two spellings.** Write the concrete
     type, or write nothing: an unannotated return is inferred, whether the
     function is exported or not (o11). The trait annotation should then mean
     what it reads as.
   - **It gives one rule for every bare-trait position:** *a bare trait
     annotation is what the other side of a signature sees.* At a parameter the
     body sees only the trait (B186, o10). At a return the caller sees only the
     trait. At a `let` there is no other side, so the annotation is checked and
     the binding keeps the concrete type (B161, o10).
5. **Trait methods get an associated opaque type per impl (S2).** That retires
   std's 14 `dyn Pipe` sites in `transient.vl` and `rpc.vl`: 8 signatures and
   6 lets that exist only to coerce. Through `dyn Trait` such a method is
   refused with a steer until a customer needs automatic erasure.
6. **It lands after B473 and B474.** Opacity sends every call on an opaque
   value through bound dispatch, and that path has two open miscompiles.

Eleven questions (§8), each with a recommendation. Slices S0–S3 (§9).

## 1. Today, measured on 0.42.0

### 1.1 What leaks through the return

| probe | program | result |
|---|---|---|
| o1 | `fun counter(start: i32): Source<i32> { SignalCell::new(start) }`; the caller does `c.set(5)`, `let x: SignalCell<i32> = counter(2)`, `wants_cell(counter(3))` | compiles and runs on JS and native: `5`, `2`, `3` |
| o1_reveal | `let n: i32 = counter(1);` | "Expected i32, but got SignalCell<i32> instead." |
| o7 | `fun doubled_label(self): Pipe<str> { self.count.derive(..).distinct().derive(..) }`; `let wrong: i32 = m.doubled_label();` | "Expected i32, but got Derive<Distinct<Derive<SignalCell<i32>, i32, i32>, i32>, i32, str> instead." |
| o10 | `let a: Source<i32> = SignalCell::new(1); a.set(2);` against `fun read_only(s: Source<i32>) { s.set(9); … }` | the `let` compiles (checked, kept narrow, B161); the parameter is refused, "Source has no method 'set'" (an implicit generic, B186) |
| o11 | `fun counter(start: i32) { SignalCell::new(start) }` (no annotation), and an `export`ed twin | compiles; callers get `SignalCell<i32>` and `.set` works |

o11 matters for the default. Door (i)'s reading is *exactly* the unannotated
function plus a trait check. Writing `: Source<i32>` today adds a check and
nothing else. The reader is told "a Source", and the caller is handed a
writable cell.

### 1.2 What breaks across a module boundary

o8 is a package of two modules. `counters.vl` exports
`fun counter(start: i32): Source<i32>`, and `main.vl` calls `counter(1).set(7)`.

- **v1:** the body returns `SignalCell::new(start)`. Prints `7`.
- **v2:** the body returns `SignalCell::new(start).derive(|x| x).memo()`, a
  sealed read-only memo. The signature is unchanged and still honest.
  `main.vl` stops compiling: "MemoCell<i32> has no method 'set'".

Under door (i) a library's return annotation does not bound what its callers
may depend on. The concrete type *is* the API, whatever the signature says.

### 1.3 Two defects (needed under either door)

- **The annotation does not reach the body (o2, o2_reveal).**
  `fun nothing(): Source<Option<i32>> { SignalCell::new(None) }` compiles. The
  call's type is `SignalCell<Option<unknown>>`, which `check_opaque_returns`
  accepts, because an unknown argument satisfies the bound. JS runs it, since
  `None` needs no type there. Native refuses: "the `rust` backend does not
  emit a value of type `an unresolved type` yet". The same initializer under a
  `let a: Source<Option<i32>>` annotation types correctly.

  The cause is in d161af2d. The function is made to "type as if its return
  were unannotated" (`function.return_type_id = None`), and the trait is
  checked only after the build. A `let` constraint, by contrast, takes part in
  inference. The fix is to push the annotation into the tail as an
  expectation: solve the tail type's impl of the trait against the written
  arguments. Opacity needs this as well, since the hidden type must be
  inferred from the same expectation.
- **Native returns one instantiation's type for every instance (o5).**
  `fun wrap<T>(x: T): Source<T> { SignalCell::new(x) }`, called with `1` and
  with `"s"`, emits `fn wrap_…_0(x: i32) -> SignalCell_…_0` and
  `fn wrap_…_1(x: Str) -> SignalCell_…_0`. `SignalCell_…_0` is the `Str` cell,
  and rustc refuses with E0308. Two controls:
  - one instantiation builds (o5_generic_one);
  - the concrete annotation `SignalCell<T>` builds with both (o5_generic_concrete).

  The JS pin `b460_a_generic_fun_and_an_inherent_method_pick_per_instantiation`
  calls `wrap` twice and passes, because JS carries no return types.

### 1.4 What already works

| probe | program | result |
|---|---|---|
| o3 | arms `s` and `s.derive(..).memo()` under `Source<i32>` | refused with the steer: "`pick` returns `Source<i32>`, a trait: that is ONE type the body picks … return `dyn Source<i32>`" |
| o3_branches_dyn | the same arms under `dyn Source<i32>` | `1`, `2` on JS and native |
| o4 | `trait Model { fun count(self): Source<i32>; }` and its impl | refused at both, with a steer to `dyn Source` (the steer drops the `<i32>`, find 4) |
| o6 | `fun deep(n): Source<i32> { if n == 0 { SignalCell::new(0) } else { deep(n - 1) } }` | `0` on JS and native |
| o7_pipe_ok / o7_pipe_moved | a pipe returned by an inherent method; used twice | runs (`4`, `10`, `10` on both backends); a second use is refused, "use of `p` after it was moved", because the concrete node type is `[resource]` |

### 1.5 `[rpc]` and the service macro (o9)

`[rpc] fun doubled(self): Source<i32>` on a `[service]` struct fails inside the
generated code, with two errors:

- "in code generated by this attribute: 'MemoCell<i32>' does not implement
  trait 'Wire'";
- "'Source' is a trait, not a type … or a generic for a return, `<T: Source>`".

The second steer is B253's, stale since B460. The macro reads the *written*
return (a `TypeExpr`). It sees `Source<i32>`, which it neither mirrors as a
handle nor can copy into the client stub. The concrete spelling `MemoCell<i32>`
works (o9_rpc_concrete), with a warning whose text names the wrong method
(find 5). Macros see the written type under either door, so an opaque return
reaches a macro exactly as it does now.

### 1.6 The estate

| what | std | examples | kolt |
|---|--:|--:|--:|
| free/inherent functions returning a bare trait | 0 | 0 | 0 |
| trait methods returning `dyn Pipe<..>` (B460's trait-method case) | 8 signatures + 6 coercing lets (`transient.vl`, `rpc.vl`) | 0 | 0 |
| `dyn Source<..>` | 6 (`combine`'s mapped tuple, two `rpc.vl` lets) | 0 | 0 |
| `[rpc]` methods returning a concrete handle (`MemoCell<..>`) | — | — | 3 (`store.vl`) |

Nobody depends on door (i)'s transparency yet. kolt's `reactive2.vl` sketch
(deleted in the owner's working tree) wrote `dyn` at every returned pipe
"because bare ones there wait on B460". Every use of those values in the
sketch is a `Flow`/`Pipe` member: `.memo()`, `.effect()`, `.derive()`.

## 2. The opaque type kind

### 2.1 What it is

**An opaque type is a rigid stand-in for the body's type, named by the
function that defines it:**

```
Type::Opaque(definer, captured)
```

- `definer` is the function, or for a trait method (§4) the method together
  with the impl.
- `captured` is every type parameter in scope at the definition: the
  function's own and its enclosing impl's.

**Identity.** Two opaque types are equal when they have the same `definer` and
equal `captured` arguments. `counter(1)` and `counter(2)` are the same type.
`wrap(1)` and `wrap("s")` are not. Two different functions that both return a
`SignalCell<i32>` behind `Source<i32>` return different types. A list holding
both needs `dyn Source<i32>`, as in Rust.

**Capture all.** Rust's `impl Trait` always captured every type parameter in
scope, and edition 2024 extended that to every lifetime as well, because the
partial rule for lifetimes surprised people more than it helped. vilan has no
lifetime parameters, so "every type parameter in scope" is the whole rule, and
it is where Rust ended up.

**What it implements:**

- the written trait, its supertraits, and every blanket impl whose bound
  those satisfy, as for a generic `T: Trait`;
- **nothing else**, so an impl written for the concrete type
  (`impl SignalCell<type T> with Display`) does not apply.

**Inside the definer the opaque is revealed.** The body's own recursive call
(o6) has the body's type, which keeps o6 compiling.

This is the type checker's existing generic machinery turned around. At a
parameter (B186) the CALLER picks the type and the BODY sees a
`Generic(constraint)`. At an opaque return the BODY picks the type and the
CALLER sees a rigid type with the same member resolution. Most of the code
path exists already: member lookup through a bound is what
`Generic(constraint)` does.

### 2.2 Inference

- **Rigid.** `mut v = counter(1); v = SignalCell::new(2);` is refused. So is
  `let x: SignalCell<i32> = counter(1)` (o1's second line).
- **Coerces to `dyn`.** `let d: dyn Source<i32> = counter(1)` is legal. The
  opaque implements the trait, and the emitter builds the table from the
  revealed type.
- **A trait annotation over an opaque** (`let s: Source<i32> = counter(1)`)
  checks as today.
- **The body is inferred against the annotation** (S0's o2 fix). The hidden
  type is the tail's type, solved with the written arguments as its
  expectation.
- **Branches.** Arms of two types are refused with today's steer to `dyn`
  (o3). Opacity changes nothing here.

### 2.3 Dispatch

A call on an opaque receiver resolves through the trait, the way a call on a
generic `T: Trait` does. At mono the revealed type picks the impl, with B158's
specificity applied as for a generic, so the call is direct and static.

**This is why B473 and B474 come first.** Both are miscompiles of calls
through a bound:

- B473: a supertrait default runs when the type overrides it;
- B474: a bound's `sub` is emitted as `RemoteSource`'s inherent `sub`.

Today `counter(1).get()` dispatches on the concrete type. Under opacity it
dispatches through the bound. Opacity would route ordinary call sites into
exactly the path those bugs live on.

### 2.4 The emitters

- **JS.** No new emission. The transformer decides dispatch from the revealed
  type, so a program whose callers use only trait members emits the same bytes
  as under door (i). Goldens do not move.
- **Native.** Mono reveals `Opaque(definer, captured)` per instantiation. That
  is the computation o5 currently gets wrong, so S0's fix is the same code.
  F59 (a field read on an inferred return) closed in Order 44. Opacity removes
  field reads on such returns from callers altogether.
- **Against `dyn`.** `dyn` costs the `(value, table)` pair at every coercion
  and an indirect call at every dispatch. B460's own door (b) recorded that
  devirtualizing it (M88) would not recover that cost for returns. It also carries B475's
  table hole: a pipe over a `dyn Source` throws at run time. An opaque has no
  table and no indirection.

### 2.5 Diagnostics, hover and hints

**Diagnostics print the trait application, with a note naming the definer:**
`Pipe<str>` ("the type `doubled_label` returns"). o7's 80-character chain
becomes nine characters. A mismatch between two opaque types names both
definers.

**Hover** shows `shown: Pipe<str>` for the binding. Inside the definer's
module it adds the hidden type on a second line, which is what a library
author debugging the body needs. E237 (the type's definition under hover)
already shows a trait-typed value's required members, and an opaque value is
exactly that case.

**E227's `~Trait` inlay hints are unchanged.**

- They abbreviate a *concrete* type whose members are still reachable. That is
  a different fact, and the `~` marks it.
- An opaque value's hint is plain `: Pipe<str>`. That is its type, not an
  abbreviation.
- `[hint(..)]` stays for chains built inline, `let p = s.derive(..).distinct()`,
  which are concrete.
- **`~Trait` should not become the writable opaque spelling.** In a hint it
  means "concrete, shown as"; as written syntax it would mean "hidden". One
  glyph would carry two meanings.

### 2.6 API stability, and what still leaks

**Under opacity the body may change its concrete type freely, provided the
new type implements the same trait.** That is o8's v2.

Three per-type facts cannot be hidden, because whole-program analyses
compute them from the concrete type: resource-ness, platform and asyncness.
Rust faces the same problem with its auto traits (`Send`, `Sync`) and lets
them leak. The proposal:

- **Resource-ness is fixed by the trait, not leaked.**
  - An opaque of a `[resource] trait` (`Pipe`, `Flow`, `CollPipe`, `CollFlow`,
    `RowFeed`) is move-only, even when the hidden type is data. A `Flow<i32>`
    whose body is a copyable `SignalCell` still moves.
  - An opaque of a data trait whose body produces a resource is refused, with
    a steer to mark the trait `[resource]` or to return the concrete type.
  - This is §5.12's rule for `dyn` (a `dyn` of a data trait cannot hold a
    resource), applied to opaques. It keeps the copy-or-move fact in the
    signature, where §4 of `keywords-vs-attributes.md` wants a reader to find
    it.
- **Platform and asyncness leak,** as they already do for every generic
  instantiation ("decided at each instantiation, like the platform and
  asyncness bits", memory.md §6.8). A body that becomes browser-only still
  breaks a node caller, loudly, with the call chain in the message. That is
  the same exposure Rust accepts for `Send`.

### 2.7 What it costs to build

`dyn` (699c51d9) landed in 26 files with +1,958/−30 lines, and
`Type::Dyn` is matched at 67 sites in vilan-core and 8 in vilan-rust. An
opaque is smaller. It needs no table, no coercion record, no slot
compatibility check and no runtime. Its parts:

- the variant;
- reveal at mono and in the transformer;
- the printer;
- member lookup, borrowed from `Generic`;
- the class rule (§2.6).

Sizing **M**. Two things change beyond the new code. The pin that reads a
field through the return (`b460_a_free_fun_returns_the_one_type_its_body_picks`'s
`make(2).side`) flips to a refusal. The ledger row that says "callers see that
type — the return is not hidden" is reworded.

## 3. The default: checked-not-hidden, or opaque

There are three doors.

- **(i) Keep door (i) and add opacity as an opt-in.** The trait annotation
  stays a check, and opacity gets its own spelling, e.g. `some Source<i32>`
  (Swift's). B414 makes `some` free as a contextual word. Rust's `impl Trait`
  would read like a declaration head here.
  - For: nothing built changes.
  - Against:
    - The plain annotation remains a *third* spelling of the transparent
      reading, beside the concrete type and no annotation (o11).
    - It is the shortest spelling, and it promises less than it delivers.
    - Everyone who writes it, including the pipe model's model methods
      (`reactive-layers.md` §4.3), gets o8's breakage by default and must
      learn a second word to avoid it.
- **(ii) Flip.** `: Trait` at a return is opaque. The transparent reading is
  spelled by the concrete type or by no annotation.
  - For:
    - The annotation means what it says.
    - One rule covers parameter and return: what the other side of the
      signature sees.
    - Diagnostics and hovers read as the signature does.
    - Today it is free (§1.6).
  - Against:
    - It reverses part of a ruling made on 2026-09-29.
    - A `let` and a return now behave differently. But that is the rule's
      point: a `let` has no other side.
    - Callers that want concrete members must ask the author to write the
      concrete type.
- **(iii) Opaque only across a module boundary.** Callers in the defining
  module see the concrete type, and everyone else sees the trait.
  - For: an author's own module keeps its convenience.
  - Against: a function's type would depend on where it is called from.
    Moving a caller between modules changes what compiles, and hover differs
    by file. No language does this. Rust's closest relative, type-alias
    `impl Trait`, scopes the *definition*, not the use.

**Rec: (ii), now.** The flip is free only while §1.6's first row is zero.
Every model method written as door (i) after this point is a later migration.
The pipe model is the customer, and its consumers (`.memo()`, `.cell()`,
`.effect()`, `.sample()`, `.derive()`) are all trait members (§1.6). Under (ii)
its model methods also read the way §4.3 calls them: "the pipe model's
`impl Iterator`".

## 4. Trait-method returns: an associated opaque per impl

`trait TransientSource<T, E> { fun latest(self): Pipe<Option<T>>; }` lets
each impl's body pick its own type. That is an associated opaque type per
impl, which Rust stabilised as return-position `impl Trait` in traits (1.75).

**At a call, the type depends on the receiver:**

| receiver | the call's type |
|---|---|
| a concrete type (the impl is known) | `Opaque((latest, impl), captured)`, that impl's opaque |
| a generic `S: TransientSource<T, E>` | the projection `Opaque((latest, S), captured)`, rigid, resolved at mono by `S`'s impl |
| `dyn TransientSource<T, E>` | no single type. Door (a): the method is not callable through `dyn`, refused with a steer to write `dyn Pipe<..>` in the trait for that method, and the rest of the trait stays `dyn`-compatible. Door (b): the slot erases automatically to `dyn Pipe<Option<T>>`, so `dyn` callers pay the pair and static callers do not. |

**Rec: (a), with (b) on a customer.** Nothing in the estate holds a
`dyn TransientSource`; the count is 0. Door (b) also needs `Pipe`'s table to
be complete, which is B475's open hole.

**The default for a trait default method's body** (a provided method that
returns a bare trait) is the same: the default's body defines the opaque for
every impl that does not override it.

**The std migration (S2):**

- `transient.vl` and `rpc.vl` change their eight `dyn Pipe<..>` signatures to
  `Pipe<..>`;
- their six `let pipe: dyn Pipe<..> = …;` lines, which exist only to coerce,
  disappear;
- every static `latest()`/`is_pending()` call stops building a pair.

`reactive-layers.md` §5's comment ("a bare trait return waits on B460")
resolves.

**This is breaking for an implementor outside std** that wrote
`dyn Pipe<..>` in its own `impl … with TransientSource`. The count in kolt
and the examples is 0.

## 5. Interactions

- **`[resource] trait`.** §2.6. An opaque of a resource trait moves; a data
  trait cannot hide a resource. This matches `dyn`.
- **`dyn`.** Opaque is "one type, static, free"; `dyn` is "any type, erased,
  the pair". Branches of two types keep the steer to `dyn` (o3). An opaque
  coerces to `dyn` like any implementor.
- **E227 `~Trait`.** §2.5: hints stay for concrete chains, and no `~` is used
  for opaques.
- **B461, nested bare traits.** `Option<Source<i32>>` in a return is refused
  today. Under opacity it would be an `Option` of an opaque, a natural
  extension. **Rec: defer** until S1 has shipped and something asks for it.
- **Macros and `[rpc]`.** A macro sees the written type, so `[service]` sees
  `Source<i32>`. On the client side an `[rpc]` return of `Source<T>` arguably
  *is* an opaque: the client holds a mirror (`RemoteSource`), not the server's
  cell. That is a wire design, not this paper's. **Rec:** the service macro
  refuses a bare-trait `[rpc]` return at the method, with a steer to the
  concrete handle type (`MemoCell<T>`), until the wire meaning is designed.
  The refusal replaces o9's two errors inside generated code.
- **A144, the contract hash.** It hashes the RESOLVED type. For an opaque
  `[rpc]` return, the resolved type is the trait application, not the hidden
  type, so a body change does not move the hash. That is the point of opacity
  at a wire boundary. Moot until the `[rpc]` refusal above is lifted.
- **B473/B474.** §2.3. These are prerequisites.

## 6. Prior art, briefly

- **Rust:** `impl Trait` in return position is opaque and captures every
  generic (edition 2024). Auto traits leak. It is allowed in trait methods
  since 1.75, and such methods are not `dyn`-compatible. Hiding is the only
  meaning; the transparent reading is spelled by naming the type.
- **Swift:** `some P` is opaque and `any P` is the existential, the analogue
  of `dyn`. Since Swift 5.7, `some` is also accepted at parameters, and the
  `ExistentialAny` upcoming feature makes a bare `P` in type position an
  error that steers to `any P`. The language is moving toward making every
  existential spelled out, with `some` as the default way to say "a P".
- **Kotlin, C#:** no opaque types. An interface return is the erased
  existential, the analogue of `dyn`.
- **TypeScript:** structural typing makes the question moot. A return type
  annotation *is* the caller's view, so it hides members. That is the reading
  vilan users coming from TS will expect from `: Source<i32>`.

Every language that has an opaque type makes the annotation hide. None
annotates a return with an interface and then hands the caller the concrete
type.

## 7. Finds (met while probing, for the integrator to file)

1. **A bare-trait return's arguments do not reach the body.** M.
   `fun nothing(): Source<Option<i32>> { SignalCell::new(None) }` types as
   `SignalCell<Option<unknown>>`, the after-build check accepts it, and native
   refuses to emit "an unresolved type". Repro: `probes/opaque/o2_*.vl`. Rec:
   S0, the annotation as an expectation on the tail. A `let` already does
   this.
2. **Native: a generic bare-trait-returning function instantiated twice gives
   every instance one instantiation's return type.** M, native build refused
   (rustc E0308); JS is correct. Repro: `probes/opaque/o5_generic.vl`, with
   controls `o5_generic_one.vl` and `o5_generic_concrete.vl`. Rec: S0, the
   native return type per instance from that instantiation's inferred return.
   Also pin it in `native_differential`, because the JS pin calls `wrap` twice
   and cannot see this.
3. **`[rpc]` with a bare-trait return fails inside generated code, with a
   stale steer.** L. The steer is B253's "a generic for a return, `<T: Source>`",
   and nothing points at the method. Repro: `probes/opaque/o9_rpc.vl`. Rec:
   the service macro refuses at the method with a steer to the concrete handle
   (§5). The generic "is a trait, not a type" text also drops its stale
   return clause.
4. **The trait-method refusal steers to `dyn Source` without the trait's
   arguments,** where `dyn Source<i32>` is meant. L. The arms steer prints
   them. Repro: `probes/opaque/o4_trait_method.vl`. Rec: print the written
   application.
5. **The fresh-handle `[rpc]` warning always says `.cell()`/`.cell_global()`,
   though it fires on `.memo()` too.** L. `lifetime_steers.rs` matches both
   but names one. Repro: `probes/opaque/o9_rpc_concrete.vl`. Rec: name the
   method the body called, and steer to its `_global` twin.

## 8. Open questions, each with a recommendation

- **Q1. The default.** Should `fun f(): Trait` be opaque, or stay checked and
  transparent? **Rec: opaque, door (ii), now,** while no site depends on
  transparency (§1.6, §3).
- **Q2. The transparent spelling under (ii).** **Rec: none new.** Write the
  concrete type, or omit the annotation (o11). If Q1 keeps door (i) instead:
  `some Trait` as a contextual opt-in.
- **Q3. Identity and capture.** **Rec:** an opaque is its definer plus every
  type parameter in scope: the function's and its impl's (capture all, §2.1).
- **Q4. What leaks.** **Rec:** resource-ness is fixed by the trait (a data
  trait cannot hide a resource; a `[resource]` trait's opaque moves), while
  platform and asyncness leak as per-instantiation bits (§2.6).
- **Q5. Inside the definer.** **Rec:** revealed, so recursion (o6) and the
  body's own uses see the concrete type.
- **Q6. Printing.** **Rec:** diagnostics and hover print the trait
  application and name the definer. Hover in the definer's module adds the
  hidden type. No `~` for opaques (§2.5).
- **Q7. Trait methods.** **Rec:** an associated opaque per impl (S2). Calls
  through `dyn` are refused with a steer (door (a), §4); automatic erasure
  waits for a customer.
- **Q8. Several bounds** (`fun f(): Source<i32> + Display`). **Rec: defer**
  until a customer exists. The single-trait form covers the pipe model.
- **Q9. `[rpc]` returns.** **Rec:** the service macro refuses a bare-trait
  `[rpc]` return with a steer to the concrete handle until the wire meaning is
  designed (§5).
- **Q10. Nested opaques** (`Option<Source<T>>` in a return, B461's shape).
  **Rec: defer,** refused as today.
- **Q11. Sequencing.** **Rec:** S1 merges after B473 and B474, which are
  solver-a-45's this order.

## 9. Slices

| slice | content | size | needs |
|---|---|---|---|
| S0 | The two defects, needed under any door: the annotation as the tail's expectation (find 1); native's per-instance return type (find 2), pinned in `native_differential`; the trait-method steer's arguments (find 4); the service macro's refusal of a bare-trait `[rpc]` return (find 3); the warning's method name (find 5) | S | — |
| S1 | `Type::Opaque` for free functions and inherent methods: identity, capture-all, member lookup through the trait, reveal in the transformer and in mono, the class rule (§2.6), printing and hover (§2.5); `spec/types.md` "A trait annotation on a return" rewritten; the B460 pins that read a concrete member through the return flipped to refusals; the ledger row's "not hidden" text replaced | M | S0; B473 and B474 merged |
| S2 | Trait-method returns as associated opaques; the `dyn` call refused with a steer; std's 14 `dyn Pipe` sites in `transient.vl`/`rpc.vl` rewritten; `reactive-layers.md` §5's comment resolved | M | S1 |
| S3 | On a customer: several bounds, nested opaques, automatic erasure through `dyn` | — | S2 |

S1 is BREAKING for a caller that reaches a concrete member through a
bare-trait return. The estate has none (§1.6). It rides the next minor
release (R-h proposes v0.43.0 at this order's seal; S1 cannot make that, so
v0.44.0).
