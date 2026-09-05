# Declared context requirements (tracker B242)

Status: **SHIPPED 2026-09-05** (Order 28, lane context-28) — the design
note behind spec §8.6. The normative text lives in
`vilan/docs/spec/contexts.md`; this file records the decisions and what
was deliberately left out.

The `std::context` mechanism itself is designed in
[`ambient-owner.md`](ambient-owner.md) §5 (the closure-type clause) and
specified in spec §8. Nothing here changes how contexts are threaded.

## 1. The problem: a requirement inferred from a body is reported anywhere

A function's context requirement is INFERRED: it is whatever its body
transitively reads, and it flows to every caller. That is convenient and
it is also why the diagnostics are hard to read. The requirement is a
fact about a BODY, so every diagnostic about it is a fact about a body,
and it surfaces wherever inference breaks rather than where the reader
made a decision:

- **B229**: one mistyped `run` argument left the `run` unselected, the
  context looked bound nowhere, and every strict read of it fenced —
  three refusals about a missing `run` the program plainly writes.
- **B241**: one missing argument on a call to a context-reading function
  produced three "can't be used as a value" refusals and five coverage
  fences, four of them inside `std`'s `reactive.vl`, in code the program
  never touched.

Both are the same shape: an inferred requirement has no boundary, so a
break anywhere propagates as far as inference does. Both were fixed at
the mechanism (the calls are recorded now), but the class stays open as
long as the requirement is a fact about a body.

## 2. The design: state it on the signature

`fun render(row: Row): str context (app_ctx, turn_scope)` declares the
requirement. Three rules follow, and all three are the same idea — the
requirement is now a fact about the SIGNATURE:

1. **Subset.** The body's strict reads must be a subset of the clause,
   checked at the declaration.
2. **Callers see the clause only.** A call from code that is neither
   under a `run` nor declaring the context itself is refused AT THE CALL,
   naming the clause and the callee. One hop.
3. **The declaring body is never the site of a coverage refusal.** Its
   signature says the value arrives; the check moved to where that
   promise is made or broken.

Rule 3 is what makes the clause a boundary. Nothing a caller is told
depends on the callee's body any more, so a cascade from an unresolved
call cannot cross it — B241's shape with a clause reports the arity error
and nothing else.

## 3. Decisions taken

**Spelling and position.** The clause `context <name>` / `context (a, b)`
is the one closure types already use (§8.5) — one spelling for one idea.
It sits after the return type, which the type grammar's own `context`
suffix already parses greedily; the declaration peels it back off, so
`fun f(): i32 context settings` binds the clause to the FUNCTION and
`i32` is the return type. That reading is also what the writer meant: the
same text was previously refused ("a `context` clause is only supported
on a parameter's closure type"), so nothing legal changed meaning.

**A wider clause is a warning, not an error.** Declaring a context the
body does not yet read is a deliberate API surface: the signature is the
promise, and adding the read later must not be a breaking change for
callers. The function takes the value and ignores it. Making this an
error would have made the forward-compatible declaration impossible to
write, which is most of the reason to declare anything.

**Safe reads are not part of the subset.** A `get_safe` imposes no
requirement on anyone (§8.2), so it cannot make a clause wrong. This is
load-bearing rather than tidy: every `async` spawn is an implicit safe
read of the standard library's ambient nursery, so a subset rule over ALL
reads would force `context ambient_nursery` onto every function
containing a spawn.

**An undeclared function keeps inference.** The two forms coexist; the
declaration is an opt-in boundary, not a migration.

## 4. Deferred: trait and `impl` methods

A clause on a member is REFUSED, with a message that says why: a
dispatched call selects its callee at the call site, so there is no
single declaration to check the requirement against. The shape a future
version needs:

- The clause belongs on the trait's **declaration**, and every
  implementation's override must declare a subset of it — the same
  subset rule, one level up. An impl that declared MORE would be a
  requirement the call site could not see.
- Coverage at a dispatch site is then checked against the TRAIT's clause,
  and the existing dispatch refinement (`dispatch_refine`, spec §8.3)
  narrows it per instantiation exactly as it narrows the inferred
  requirement today.
- An inherited default body's reads check against the trait's clause,
  since that is the declaration it is written under.

Nothing about the free-`fun` form needs to change to admit this; the
refusal is a stop, not a fork.

## 5. Editor

Hover renders the clause in the signature label, after `borrows` and
`bumps`, exactly as it is written. The subset refusal spells out the
clause the body needs, and **Declare the inferred contexts** writes that
spelling over the clause's own name list — the message and the edit are
one string, so they cannot disagree.

## 6. Not done

- **A quickfix on an UNDECLARED function** ("write down what this body
  infers"). It wants an insertion point in a signature the diagnostic
  does not anchor in — the refusal is at the call, in a different
  function — so it needs a span the parser does not record yet.
- **A `context` clause on a closure LITERAL's signature.** Closure types
  carry one already (§8.5); a literal's own declaration does not.
- **Nested-type interaction.** `fun f(): &mut i32 context turn` binds the
  clause to the REFERENT (the type grammar's suffix, one level in) and is
  refused there. Rare, and the refusal is honest, but it is the one place
  the peel does not reach.
