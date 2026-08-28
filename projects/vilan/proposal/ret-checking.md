# Return-position type checking (backlog B10)

Status: **implemented with this note** (2026-07-04). Pins: the two `#[ignore]`s named in
B10, un-ignored, plus the per-case suite below. **Rule 3 amended 2026-08-22 (B126)** — see
"Rule 3, amended" below; the original wording is kept there for the record. **Rule 4
amended 2026-08-24 (B133)** — see "Rule 4, amended" below, likewise.

## The gap (bigger than B10 recorded)

B10 said the solver never constrains a `ret` against the enclosing signature. Probing
showed the gap is wider: **the tail expression isn't checked either**. `fun bad(): i32 {
"nope" }` compiled clean — `Constraint::ReturnType` runs `infer_type(body, expected =
declared)` which *directs* inference (return-position generic binding) but never
*verifies* the result. Every "Expected X, but got Y" in the suite came from let-annotation
and argument checking; return position had none.

## Semantics (settled by probe, pinned)

1. **`ret` returns from the nearest enclosing callable** — function, closure, or `async`
   block (probed: a `ret` in a closure exits the closure; in an `async {}` it settles the
   block). The check is therefore scoped per-callable.
2. **In a function with a declared return type `R`:** the tail and every `ret v` check
   `typeof(v)` against `R` through the same constraint (`reconcile_type` — the same
   unification the let-annotation check uses, so generic returns bind, not just match).
   A **bare `ret`** checks a synthesized void value against `R` — so it is legal exactly
   when `R` is void, and errors as `Expected i32, but got void instead.` otherwise. No
   special case: bare `ret` is `ret <void>`.
3. **In a function with no declared return type:** the return type is **inferred from
   the body's return positions** — the tail, when the body can reach it, and every
   `ret` — and they must agree. (Amended 2026-08-22, B126; the original wording and why
   it was wrong are under "Rule 3, amended" below.)
   - The tail counts only when it is **reachable**: a body whose last statement leaves
     (`{ ret 1; }` — its synthesized void tail is dead code) or whose tail itself
     diverges (an exhaustive `if`/`else` of `ret`s, B124) contributes no tail value, so
     `fun f(x: bool) { ret 1; }` is `i32` (pin
     `b126_a_ret_only_body_infers_its_return_type`), and so is
     `fun f(x: bool) { if x { ret 1; } else { ret 2; } }` — which used to type `never`
     and let `let y: str = f(false)` through (pin
     `b126_an_exhaustive_if_else_of_rets_infers_from_the_rets`). `fun f() { 5 }` is `i32`
     exactly as before (pin `b126_a_tail_only_body_still_infers_from_its_tail`).
   - A tail the body CAN reach is evidence like any `ret`: `{ if x { ret 1; } 2 }` is
     `i32` (pin `b126_a_ret_and_a_tail_that_agree_infer_one_type`); a body that can end
     without a value — a last statement that does not leave, or a tail that is an `if`
     with no `else` — is void on that path, and a `ret 1` disagrees with it (pins
     `b126_a_value_ret_beside_a_fall_through_is_refused`,
     `b126_a_value_ret_beside_an_else_less_if_tail_is_refused`).
   - A **bare `ret`** is `ret <void>` (rule 2's reading, no special case): it agrees with
     a void body and disagrees with a value tail (pin
     `b126_a_bare_ret_in_a_value_tailed_function_is_refused`). A `ret` of a void call
     beside a value tail is the same disagreement (pin
     `b126_a_void_ret_beside_a_value_tail_is_refused`).
   - **Disagreement is one refusal per disagreeing `ret`**, anchored at that `ret`,
     naming the `ret`'s type, the inferred type, and where the inferred type came from —
     the tail, an earlier `ret`, the body ending without a value, or an `if` with no
     `else` — with a note at that origin (ledger rows 244–245; pins `b126_a_ret_disagreeing_with_the_tail_is_refused_at_the_ret`,
     `b126_rets_that_disagree_are_refused_at_the_later_ret`). The evidence is read in
     one order: the tail first (when reachable), then the `ret`s in source order, each
     inferred WITH the running type as its expectation so a return-position generic in
     a `ret` binds from the tail (pin `b126_a_ret_of_a_generic_call_binds_from_the_tail`).
     A function with a disagreement has no inferred type — its calls type as `any` — so
     the refusal never cascades into an `Expected i32, but got void` at a call site (B5;
     the disagreement pins assert the cascade's absence).
   - A **self-call** inside the body contributes nothing — its type IS the answer being
     computed — so `fun count(n: i32) { if n == 0 { ret 0; } ret 1 + count(n - 1); }` is
     `i32` from `ret 0`, and a function whose only return evidence is self-calls is
     `never` (pins `b126_a_recursive_unannotated_function_infers_from_its_other_returns`,
     `b126_mutually_recursive_unannotated_functions_infer_together`,
     `b126_a_function_that_only_calls_itself_is_never`). A self-call bound by a `let`
     and read in the tail (`let x = g(n - 1); x + 1`) still does not resolve — the
     binding's type is not read through its initializer on the inference path — exactly
     as before the amendment; recorded, not a regression (`#[ignore]` pin
     `b126_a_let_bound_self_call_read_in_the_tail_resolves`, asserting what should hold).
   - The rule is the function's, not the shape's: an `async fun` without an annotation
     infers the same way and a call to it yields that type (pin
     `b126_an_async_function_without_annotation_infers_from_its_rets`); a nested closure's
     `ret`s stay on the closure's own frame under rule 4 (pin
     `b126_a_nested_closures_rets_stay_on_the_closures_frame`); a generic function's
     `ret` of its own parameter agrees with a tail of that type at every instantiation
     (pin `b126_a_generic_function_infers_from_a_ret_of_its_parameter`). Every reader
     sees the same answer: closure coercion on both its paths (pin
     `b126_a_ret_only_function_coerces_to_a_closure_slot`), the `for` protocol's
     unannotated `next` (pin `b126_an_unannotated_next_that_leaves_by_ret_drives_the_loop`),
     and trait conformance (pin
     `b126_an_unannotated_impl_method_conforms_by_its_unified_type`). The old rule-3 pin
     `ret_with_a_value_in_an_undeclared_void_function_is_allowed` is re-pinned as
     `b126_a_void_ret_agrees_with_a_void_body`: same program, the new reason.
4. **In closures and `async` blocks:** their return types are *inferred*, by **the same
   reachable-tail unification as rule 3**. (Amended 2026-08-24, B133; the original
   conservative rule and why it was lifted are under "Rule 4, amended" below.)
   - The evidence is the REACHABLE tail plus every `ret`, built and folded by the same
     machinery as a function's (`return_evidence` + `unify_return_evidence`, one rule,
     not two copies): `|x| { ret x * 2; }` is `|i32| i32` (pin
     `b133_a_ret_only_closure_body_infers_its_return_type`), an exhaustive `if`/`else`
     of value-`ret`s agrees with a `|i32| str` slot and runs (pin
     `b133_a_closure_of_rets_infers_like_a_function`, re-pinned from
     `a_closure_of_rets_loses_the_false_mismatch_and_keeps_rule_4s_guidance` — same
     program, the new rule), and `async { ret 1; }` settles as a task of `i32` (pin
     `b133_an_async_block_of_rets_settles_with_their_type`).
   - A closure whose rets are its only evidence binds a caller's return-position
     generic bottom-up, exactly as its tail would (pins
     `b133_a_closure_ret_binds_a_callers_return_generic`,
     `b133_a_from_fn_callback_that_leaves_by_ret_types` — the I5/B19 abstract-target
     shape, refused by the pre-lift rule); a return-position generic IN a `ret` binds
     from the running type or the held target (pin
     `b133_a_ret_of_a_generic_call_binds_from_the_target`).
   - **Disagreement is one refusal per disagreeing `ret`**, at that `ret`, in the
     closure's wording, with a note at the origin (rule 3's origin vocabulary). The
     conservative "make the ret'd value the body's tail" steer survives exactly where
     the genuine disagreement remains — a value-`ret` beside a body path that CAN end
     without a value (pins `b133_a_value_ret_beside_a_reachable_fall_through_keeps_the_steer`,
     `b133_a_value_ret_beside_an_else_less_if_tail_keeps_the_steer`); a `ret`
     disagreeing with a reachable tail or an earlier `ret` reports at that `ret` (pins
     `b133_a_ret_disagreeing_with_the_tail_is_refused_at_the_ret`,
     `b133_rets_that_disagree_are_refused_at_the_later_ret`,
     `b133_an_async_blocks_disagreeing_rets_are_refused`); a bare `ret` beside a value
     tail is still refused (pin `b133_a_bare_ret_beside_a_value_tail_is_still_refused`).
   - **When the closure's return type is KNOWN** — its own annotation, or the ground
     target S3's route held the body to (B125's expectation, a receiver-/argument-bound
     generic) — the `ret`s check against that type instead, rule 2's regime, once, at
     the `ret` (pins `b133_a_dead_tail_ret_is_checked_against_the_target`,
     `b133_a_dead_tail_ret_reports_once_under_an_expectation` — the B5 probe extended
     to `ret`s: the call and the `let` add nothing).
   - A closure that never types (unbound, never called) leaves the check deferred,
     matching how loosely such a closure types everywhere else — which now includes a
     never-called `{ ret 1; }`, refused by the pre-lift rule's void vote and quiet
     today (pin `b133_a_never_called_ret_closure_stays_quiet`).

## Mechanism

- `resolve_return_type` gains the missing half: after `infer_type` resolves, `reconcile_type`
  against the declared type; `None` → the standard mismatch diagnostic at the value's span.
  This alone fixes the tail.
- The analyzer walks with a `return_type_stack: Vec<ReturnFrame>` — `Function(id, R)`
  pushed around a function body walk when a return type is declared, `Inferred { rets }`
  for unannotated functions, closures, and `async` blocks (the boundary that makes `ret`
  inner-scoped). At a `ret` the only question is declared-or-inferred; what becomes of
  the collected `rets` is the popper's business — a closure pushes
  `Constraint::ClosureReturns` (rule 4), a function stores them on its `Function` record
  and pushes `Constraint::FunctionReturns` (rule 3). `VoidFunction` (B10's "rets
  unchecked" frame) is gone: nothing is unchecked any more.
- `Node::FuncReturn` pushes `Constraint::ReturnType` for its value (or a synthesized
  `Expr::Void` entity spanned at the `ret` itself) against the innermost `Some(R)`, and
  seeds `expected_types` — so `ret` is a first-class return position: return-directed
  generic binding (`ret List::new()`) works exactly as it does for the tail.

## What turning the check on surfaced

Three fixes fell out of enforcement, all root-caused:

- **The nine operator-trait defaults were ill-typed** — `{ panic("not implemented yet"); }`
  with a semicolon makes the panic a *statement* and the block's tail void, defeating the
  existing never-typing (`panic(..)` calls type as `Any` — a mechanism whose own comment
  anticipates exactly this "sole body of a function with any return type" case). Dropping
  the semicolons restores the intended pattern; behavior identical (panic throws).
- **`reconcile_type` had no `(Trait, Trait)` arm** — a trait-typed `self` returned through
  a trait-typed signature (`impl Iterator<type T> with Iterable<T> { fun iter(self):
  Iterator<T> { self } }`) had never reached a *checking* position before. Same-id traits
  now reconcile their arguments pairwise, like the nominal `Struct`/`Enum` arms.
- **`reconcile_type` had no `(Mapped, Mapped)` arm** — a parameter typed `(U in T:
  List<U>)` returned through an identically-written mapped return walks as two distinct
  binder ids, so the arm reconciles *structurally* (sources and templates recurse; the
  binders' alpha-renaming bindings are dropped from the result).

## Rule 3, amended (B126, 2026-08-22)

### What rule 3 said, and what the code did

Rule 3 as ratified 2026-07-04 read:

> In a function with no declared return type (void): nothing is checked — neither the
> tail (existing behavior: `fun f() { 5 }` compiles, the value is discarded) nor any
> `ret v`. Consistency with the tail is the rule; a void function's return values are
> discarded, not diagnosed.

The "void" was never what the code did. An unannotated function's type was **inferred
from its tail** — `infer_type_inner`'s `Type::Function` arm read `f.body.1` when
`return_type_id` was `None`, and so did the closure-coercion readers and the `for`
protocol's `next` reader: `fun f() { 5 }` was `i32`, `let y: i32 = f()` compiled, and
B20's own coercion pin (`a_void_function_without_annotation_coerces`, despite its name:
"the return type comes from the body's inferred type") relied on it. What rule 3
described accurately was the CHECK — the walk pushed `ReturnFrame::VoidFunction`, and a
`ret` against it did nothing. So the paper was right that nothing was checked and wrong
about why: the function was not void, its `ret`s were simply invisible to the one
reader that typed it (the tail id), which is exactly the gap B124's lane found and
filed as B126.

Invisible `ret`s are not merely a missed inference — they are unsound. Probed
2026-08-22 against `next` @ 67cd3c57:

- `fun f(x: bool) { if x { ret "s"; } 2 }` with `let y: i32 = f(true); print(y)` compiled
  clean and printed `s` — a `str` under an `i32` binding.
- `fun f(x: bool) { if x { ret; } 2 }` with `let y: i32 = f(true)` printed `undefined`.
- `fun f(x: bool) { if x { ret 1; } else { ret 2; } }` typed `never` (B124's diverging
  tail) so `let y: str = f(false)` compiled and printed `2`.
- `fun f(x: bool) { ret 1; }` — B126's own example — refused `let y: i32 = f(true)` with
  `Expected i32, but got void instead.` at the CALL, the one place that had nothing to do
  with the mistake.
- An unannotated impl member `fun area(self) { ret "wide"; }` against a trait declaring
  `: i32` passed conformance (the reader saw an unmapped tail and matched leniently) and
  printed `wide`.

"Discarded, not diagnosed" was a description of an accident, and the accident
miscompiled.

### The rule, and the one place the recommended rule was overturned

The orchestrator's brief recommended lifting rule 4 to functions with "the same
conservative mix rule (a value-`ret` with a void tail → the value's type)". That clause
is unsound as stated: in `fun f(x: bool) { if x { ret 1; } }` the void tail is
**reachable** — `f(false)` falls through and hands back `undefined` — so typing the
function `i32` from its `ret` would be the `undefined`-under-`i32` miscompile again,
one layer up. The line that makes `{ ret 1; }` infer `i32` while `{ if x { ret 1; } }`
is refused is not void-vs-value; it is **reachable-vs-unreachable**, and the compiler
already draws it: B124's `expr_diverges`, asked of the tail and of the block's last
statement, is the question `check_return_position` asks before it reports "this body
ends without producing a value" for a declared function. Rule 3 asks the same question
of the same positions and reads the answer the other way — an unreachable tail is not
evidence. Nothing new is invented; the declared and inferred regimes now agree about
which positions exist.

Rule 4's "make the ret'd value the body's tail" guidance for closures was NOT lifted
by this amendment: a closure of `ret`s was still refused with that steer
(`a_closure_of_rets_loses_the_false_mismatch_and_keeps_rule_4s_guidance`), because
closure return inference was b125's open territory and a closure almost always has an
expected type from its call site, which made the conservative rule cheap there. The
asymmetry — `{ ret 1; }` infers in a function and is refused in a closure — was
recorded as an owner question in the B126 lane's report rather than settled here.
*(Lifted 2026-08-24 by B133, owner-approved — see "Rule 4, amended" below; the pin is
re-pinned as `b133_a_closure_of_rets_infers_like_a_function`: same program, the new
rule.)*

**Bare `ret` in a value-tailed function is a refusal**, not a void vote that wins or
loses by position. Rule 2 already reads a bare `ret` as `ret <void>` with no special
case, rule 4 already requires a void tail of it, and the probe above shows what the
alternative ships. The refusal anchors at the `ret`, like every other disagreement.

### Mechanism

One helper answers "what does this unannotated function return": `inferred_return_type`
(over `infer_function_returns`, which also lists the disagreements). Its evidence is the
reachable tail plus `Function.rets`, read tail-first then in source order, each item
tagged with its origin (`ReturnOrigin`: the tail, the synthesized void after a
non-leaving last statement, an else-less `if` tail, a `ret`) for the refusal's wording;
a `never`, `any` or `unknown` item constrains nothing (it is kept only as the answer of
last resort when nothing else speaks); a disagreement makes the answer `any`. Every reader that
used to read `f.body.1` goes through it: `infer_type_inner`'s `Type::Function` arm (the
call site), `function_closure_type` (a named function coerced to a closure slot),
`for_each_next_non_option_return` (the `for` protocol's unannotated `next`, B92), and
the trait-conformance return check (`MemberSignatureShape::body_tail_id` is gone — the
check asks the helper for `check.impl_function_id`). `function_closure_type_recorded`,
the read-only coercion path, reads the helper's record (`inferred_return_types`), which
the helper writes whenever it computes an exact answer.

Recursion: the helper keeps a stack of the functions it is inferring. A re-entrant ask
for a function already on the stack answers `never` — the self-call's type is the
answer under construction, so it can constrain nothing — and marks every frame nested
inside that function's as inexact, so a function whose answer was built on an
unfinished neighbour's is not recorded (its own constraint computes it top-level and
records then). `exprs_seen` still guards expression-level cycles exactly as before. Residue: a self-call
bound by a `let` and read in the tail (`let x = g(n - 1); x + 1`) is not reached by this —
the inference path does not read a `let` binding through its initializer, so the tail
stays unresolved while the binding waits on the call — and fails "could not be resolved"
as it did before the amendment; pinned `#[ignore]`d as
`b126_a_let_bound_self_call_read_in_the_tail_resolves` (B126 residue, 2026-08-22).

`Constraint::FunctionReturns { function_id }` is pushed for every bodied function
without a declared return type (not only those with `ret`s — the record is how the
read-only coercion path sees `{ ret 1; }` as `i32`). It defers while any evidence is
unresolved, like `ClosureReturns`, and reports each disagreement once, at its `ret`.

The view/resource seam readers over `return_sites` (B116's join: the tail of every
function, plus each `ret` of a DECLARED-return function) are untouched by this
amendment; a `ret` in an unannotated function is already refused as a view escape by
the generic `FunctionReturn` scan (probed: `fun pick(&self) { ret &self.x; }` reports "a
view cannot escape its scope"). Whether `return_sites` should carry unannotated `ret`s
too is an owner question in the lane's report.

*Closed 2026-08-24 (B134, owner-approved; lane closure-ret-family).* `return_sites` now
carries **every return position of every bodied function, annotated or not** — the tail
and each value-carrying `ret` (a declared bare `ret`'s synthesized void still enters, it
IS the checked value; an unannotated bare `ret` synthesizes none and has no leaves to
contribute) — and the readers that compensated for the declared-only join read it alone:
the crossing scan and `check_view_escape`'s function seams drop their
tails-from-the-functions supplements, `infer_borrows` folds over the joined positions,
and the capture-copy seam roots come from the join. Two corrections in the shipped
compiler fell out, one per spelling. (Precision note: B116's join carried the tail only
for a DECLARED-return function too — the parenthetical above overstated it; the clone-site
pass had no other function source, which is the tail defect below.)

- **The tail defect was a miscompile**: with no annotation the tail was not a clone seam
  at all (`compute_return_clone_sites` took function seams only from `return_sites`), so
  `fun grab(&self) { self.inner }` handed back the receiver's LIVE storage — probed on
  the pre-B134 binary, the program printed 99 where its annotated twin printed 3 (pin
  `b134_an_unannotated_tail_of_a_loaned_place_copies`, asserting the emitted `__clone`
  and the run).
- **The `ret` defect was the wrong refusal**: an unannotated `ret &self.inner` fell to
  the raw `Expr::FunctionReturn` escape arm (never being in `return_sites`, it got no
  seam walk) and was refused generically where its annotated twin copies; an unannotated
  `ret &self.g` of a resource likewise drew the generic escape message instead of the
  move scan's. Both spellings now answer exactly like the annotated twins, B116's own
  bar (pins, each a B116/B122 shape with the annotation removed:
  `b134_the_unannotated_ret_spelling_of_a_reference_leaf_copies`,
  `b134_the_unannotated_ret_spelling_of_a_scalar_view_reads_the_place`,
  `b134_the_unannotated_ret_spelling_of_a_borrows_call_leaf_copies` — the `borrows`
  callee keeps its declaration; the sanction is the signature's, and an unannotated
  caller has none to give —
  `b134_the_unannotated_ret_spelling_of_a_resource_reference_leaf_is_refused`,
  `b134_an_unannotated_ret_only_resource_crossing_is_named_by_the_move_scan`, and the
  unchanged half `b134_the_unannotated_ret_spelling_of_a_view_of_a_local_still_cannot_escape`).

A closure's `ret`s still never enter `return_sites` (rule 4 owns them; P4c — nothing
sanctions a view leaving a closure). Async's return-escape readers filter on a declared
closure-typed return and are unaffected. Plant (the declared-only join restored): 6 of
the 7 `b134_*` pins red — the local-view refusal rightly stays. Inference 2457/0/2,
corpus byte-identical (no corpus program had the shape), docs green; the tour's
projection-or-copy box states the rule ("an unannotated function always returns a
value").

## Rule 4, amended (B133, 2026-08-24)

> **OWNER NOD 2026-08-24** — the wording stands as written; never-called ret
> closures staying quiet is confirmed; the alias→copy upgrade impact is
> stated plainly in the CHANGELOG entry per the same ruling.

### What rule 4 said, and what was wrong with it

Rule 4 as shipped checked a closure's `ret`s against **its tail's inferred type**,
whatever the tail's reachability: the tail of `{ ret 1; }` is the parser's synthesized
void after a statement that LEAVES, the check read that dead position as a void vote,
and every value-`ret` beside it drew the conservative steer ("make the ret'd value the
body's tail"). B126 had just established, for functions, that this is exactly
backwards — an unreachable tail is not evidence, and the compiler already draws the
line (`expr_diverges`, B124's question). The asymmetry `{ ret 1; }` infers in a
function / is refused in a closure was kept at B126's merge deliberately (b125's
territory was mid-flight) and filed as its Q1; the owner approved the lift as B133.

What the conservative rule cost, probed on the pre-lift binary: a `from_fn`-style
callback that leaves only by `ret`s (`|| { .. if done { ret None; } ret Some(n); }`)
was refused outright even though its rets agree and would bind the caller's `T`
(pin `b133_a_from_fn_callback_that_leaves_by_ret_types`); an exhaustive `if`/`else`
of `ret`s under a `|i32| str` slot was refused
(pin `b133_a_closure_of_rets_infers_like_a_function`); `async { ret 1; }` was refused
(pin `b133_an_async_block_of_rets_settles_with_their_type`); and a never-called
`{ ret 1; }` was refused for a disagreement between a `ret` and dead code that no
execution can exhibit (pin `b133_a_never_called_ret_closure_stays_quiet`).

### The rule

A closure's (and an `async` block's) return type is the **unification of its
reachable tail and every `ret`** — rule 3's rule, rule 3's machinery. The evidence
construction (`return_evidence`: the tail only when the block's last statement does
not leave and the tail itself does not diverge, tagged Tail/FallThrough/IfWithoutElse;
then the `ret`s in source order) and the fold (`unify_return_evidence`: first
constraining item sets the running type, later items are inferred WITH it so
return-position generics bind, `never`/`any`/`unknown` constrain nothing, a
disagreement makes the answer `any` so nothing cascades — B5) are shared with
`infer_function_returns` — one rule, not two copies. Only the refusals' wording is
the closure's, and each carries a note at its origin in rule 3's vocabulary.

Two regimes, mirroring a function's declared/inferred split:

- **Known return type** (the closure's own annotation, or the ground target S3's
  route held the body to — B125's expectation binding, a receiver-/argument-bound
  generic): rule 2's regime. The tail was already checked by the route (anchored at
  the brace, or at the expression since B132); when the tail is DEAD the `ret`s are
  the only return positions, and they check against that type, at the `ret`
  (pins `b133_a_dead_tail_ret_is_checked_against_the_target`,
  `b133_a_dead_tail_ret_reports_once_under_an_expectation`). This is the B125
  interplay the lift had to not break: the expectation binds `U` BEFORE the closure
  types, the `ret` is checked against the bound target, and neither the call nor the
  `let` reports a second time (the B5 probe set, extended to `ret`s).
- **Inferred** (no annotation, no ground target): rule 3's regime, refusals at the
  disagreeing `ret` (pins under rule 4's restated text above). The steer survives
  only for a value-`ret` beside a body path that CAN end without a value — the
  genuine disagreement it was written for.

### Mechanism

`Closure` carries its `rets` (the twin of `Function.rets`; the walk stores what the
`Inferred` frame collected, for closures and the `async` desugar alike), and
`Constraint::ClosureReturns` slims to the closure id. `closure_return_inference`
builds the evidence over `closure_body_positions` (a block's tail + last statement,
a bare expression itself) and runs the shared fold; the `Expr::Closure` arm's
bottom-up path and the `Expr::Async` arm's payload both read it when rets exist
(an `async` block's fold is seeded with the context's `Task<T>` payload as the
initial expectation), so every reader of the closure's type sees the rets — which
is what lets a `ret`-only body bind a caller's return-position generic.

The route/constraint split and its ordering: S3's route records the target it holds
a body to (`closure_held_targets`), and `resolve_closure_returns` reads it (or the
closure's own ground annotation) for the dead-tail target check. Resolution is
monotone — a constraint that resolved is never revisited — and a deferred owning
call can resolve AFTER `ClosureReturns` did, so the route ALSO runs the dead-tail
target check on every inference attempt; both sides share
`check_closure_rets_against_target`, and a span+message dedup keeps whichever runs
second from adding anything (the same guard the route's brace report has always
used). `resolve_closure_returns` defers while any closure parameter is untyped —
the body's types can depend on them, and the call that fills them may also bring
the target — which is also what keeps a never-called closure's check deferred
(pre-lift it deferred on the tail typing `Unknown`; a dead tail types void, so that
guard no longer covers the `{ ret 1; }` shape).

Residual, recorded: a ZERO-parameter closure with internally-disagreeing rets whose
owning call defers past the first pass can have its internal refusal reported from
the parameter-free evidence regime before the target lands; the identical head +
span dedup collapses the common shapes, and no pinned program exhibits a double
report. The held-target refusal renders the target in the existing heads' "the
closure's body yields {T}" slot — for a fully-dead tail that phrasing describes the
type the closure returns rather than a value the body's tail produces; kept for
head-stability (no new ledger rows), flagged as an owner question in the lane
report.

Plants (targeted binary): the dead tail re-counted as a void vote → 10 of 15
`b133_*` pins red (the five green ones pin reachable-tail behavior the plant does
not touch); the dead-tail target check disabled → both dead-tail-target pins red
(the programs compile clean — the hole is real); the arm's rets made invisible →
`b133_a_ret_only_closure_body_infers_its_return_type` red. Inference 2450/0/2,
corpus byte-identical, docs green. Spec §5.6 and the tour's closure section updated
in the code commit.

## Excluded (recorded, not drifted into)

- ~~Closure-`ret` participation in closure return inference~~ — shipped as the
  follow-up (rule 4), then lifted to rule 3's unification by B133 (above).
- A never type: `ret`/`panic` as expressions still type void; `match` arms mixing a
  `ret` arm with value arms keep today's behavior (the arm unification is untouched).
