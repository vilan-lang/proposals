# When a resource temporary dies — statement-end, and why (backlog C11)

> Status: PROPOSED 2026-08-28 (cycle 36, work order 18, lane `c11-paper`),
> for owner review. The DIRECTION is not in question and this paper does not
> reopen it. The owner, verbatim, 2026-08-28: **"Write the paper. Those
> should not leak."** Rejecting the spelling is off the table; what is open
> is the *mechanics*, and this paper recommends one of the two the tracker
> named — **(b) statement-end drop**, over (a) scope-end drop.
>
> Backlog item: `tracker/backlog.md` §C item 11. Found by Order 17's
> `fs-handles` lane while generating `vilan/test/file.mjs`, recorded in
> `filesystem.md` §11.1 ("GATE INVERTED AT SHIP") and in that paper's ship
> note as a struck claim.
>
> Governing records this paper builds on rather than re-decides:
> **`destruction.md`** — RATIFIED, Tier 1 SHIPPED 2026-07-19. Its §4 affine
> rules, its §5 timing law, its §7 lowering and its §8 interactions are
> treated as ground. This paper argues *against that ground* only in the one
> place the ground is silent, and it names that silence rather than reading
> a permission into it. Also: `filesystem.md` §5/§5.1 (the `File` handle and
> Q1's ruled fire-and-forget close), `expression-lifting.md` §2 (the lift
> region, which is the nearest existing precedent for "a value that lives
> inside one statement").
>
> **Every probe below was run against a release binary built from
> `vilan` `next` @6edf6261** in a scratch worktree, and every block marked
> *verbatim* is emitted or printed output, unedited. Where a candidate
> lowering does not exist yet, it was hand-written into the compiler's own
> emitted JavaScript and executed; those blocks say so.
>
> **Two premises in the lane's own brief are corrected by §2**: there is no
> "B141 lifting" — B141 was a printer parenthesization fix and lifts
> nothing — and the loop is **not** the decisive case between the options,
> because a loop body is already a drop scope. §5.2 gives the case that is.

---

## 1. The finding, exactly

A resource born and consumed inside one expression is neither dropped nor
rejected. It is not a leak of *some* handles under *some* conditions; it is
every such handle, on every resource type, on every path, until process exit.

```vilan
// std::db — the constructor is synchronous.
Database::open(":memory:").exec("CREATE TABLE b (id INTEGER)");

// std::fs — the constructor is asynchronous. Same outcome.
print(File::open("p.txt").read_at(buffer, 0));
```

Both compile clean, exit 0, and produce the right *value*. Neither closes
anything. The reason is one sentence, and the compiler already writes it down
about a neighbouring case (`crates/vilan-core/src/analyzer.rs:8431`):

> `drop<T>(own value: T)` takes its argument by move, so a **value**
> argument — a call result — is owned by the `drop` expression itself and
> must be destroyed there: it is never bound, so no scope-end teardown and
> no R2 overwrite can reach it.

The drop planner enrolls **bindings**. `collect_resource_bindings`
(`analyzer.rs:7303`) iterates `self.variables` and `self.parameters` and
nothing else; the result lands in `Program::dropped_bindings: HashSet<Id>`.
An expression temporary has no `Id` in that space, so it is in no drop set,
so `Drop` — the safety net the whole `resource` class is built around — does
not reach it. `destruction.md`'s §5 timing law speaks of "still-owned
resource **locals**". A temporary is not a local. The ratified file is not
wrong here; it is **silent**, and the silence is the bug.

This matters more than a normal gap because `filesystem.md` §11.1 makes the
offending spelling the *intended idiom* of the `File` tier:

> S3 is the first surface whose *intended idiom* is the exact shape B141
> mis-compiles … `File::open(path).read_at(buffer, 0)`, a postfix straight
> off an implicitly-awaited call.

B141 made that spelling produce the right value. Nothing made it clean up.
The tier shipped with its own idiom leaking, pinned POSITIVE for value and
silent about the handle — which is what the ship note said out loud rather
than fixing en passant.

### 1.1 What B141 was, and was not

The lane brief asked "where does the transformer lift an awaited receiver
today (the B141 fix's lifting)?" **It does not.** B141 (`d8bc9a85`,
"transformer: parenthesise an await under a postfix") added a single
string-rendering helper, `fn postfix_subject`
(`crates/vilan-core/src/transformer.rs:7800`), the counterpart to the
existing `fn operand`. It wraps a postfix *subject* in parentheses when the
subject binds looser than a postfix does. The commit's own summary of the
alternative it rejected is instructive and is quoted again in §6.3:

> The alternative was to emit `(await x)` unconditionally at every site; it
> was rejected because it is a producer-side defensive wrap in a printer that
> decides parentheses at the consumer … The context-aware rule moves **zero**
> goldens.

`fn maybe_await` (`transformer.rs:2311`) returns `js::Node::Await(..)` and
never touches the statement block. So there is no temporary today, with no
binding, no name, and no statement position. **Both options in this paper
must invent the lift; neither inherits one.** That is the single most
important correction this lane makes to its own premise, because it moves
the two options much closer together in implementation cost than the framing
suggested (§6.3), and it means "attach a drop to the existing temporary" is
not an available shortcut for either.

---

## 2. What the machinery does today — the seams, probed

Two halves.

**Analyzer.** `fn plan_resource_drops` (`analyzer.rs:7637`) is the whole
planner. Enrollment is `collect_resource_bindings` (`7303`), filtered of
loans by `binding_or_param_is_view` (`7643`, B94). The scope-end decision is
five lines (`analyzer.rs:7939`):

```rust
// Scope end: a resource local declared here and still owning its value
// drops here. Either way it leaves scope, so it no longer counts as owned
// for any enclosing scope.
for variable_id in &declared_here {
    if owned.remove(variable_id) {
        dropped.insert(*variable_id);
    }
}
```

`plan_scope` (`7894`) runs once per **scope**: function body, closure return,
`Expr::Block`, each `if` arm, each `match` leg, each loop body. There is no
per-expression owner. `plan_expr`'s `Expr::Call` arm (`8041`) walks a
non-`Local` subject with `consuming = false` and mints nothing — which is
the leak, stated as code.

**Transformer.** `fn walk_scope_body` (`transformer.rs:6740`) scans a
statement list; on each owning statement it emits the declaration and
recurses with `index + 1` *inside a new* `js::Node::Try` (built at
`6761`). N resource locals in one block therefore produce N nested
`try`/`finally`s, dropping in reverse declaration order. Classification is
`fn statement_teardown` (`6659`) returning `enum ScopeTeardown` (`1732`):
`None` / `Binding(Id)` / `Captures(Vec<Id>)`. The declaration deliberately
stays **outside** its own `try` (`transformer.rs:6736`: "a panic
mid-acquisition never drops an unacquired value"). The drop call itself is
`fn resource_drop_of(type_id, value)` (`6879`) — **type-keyed and value-node
agnostic; it will drop any JS expression node handed to it.**

Two facts about that shape, both confirmed by probe, both load-bearing later:

- **A loop body is a drop scope**, and so is an `if` arm. A bare nested block
  is a drop scope emitted flattened into its parent.
- **The `try` does not start at the top of the scope.** It starts immediately
  after the owning declaration and runs to the scope's end. So "join the
  enclosing scope's drop set" does *not* mean "hoist to the top of the
  function" — the declaration already lands where option (b) would put it.
  The two options differ only in **where the `finally` closes.** This is the
  central mechanical fact of the paper.

**Naming.** `NameGenerator::next_name` (`transformer.rs:8940`) mints `$a`,
`$b`, … under `NameStyle::Readable` and bare `a`, `b`, … under release.
Minted names enter `NameGenerator::minted` only, never `names: HashMap<Id,
String>` — so a transformer-minted temporary is **invisible to every analysis
pass**, all of which have already run.

**The two precedents that make either option buildable.** (i)
`is_bindings: HashMap<Id, js::Node>` (`transformer.rs:1543`) is an existing
side table mapping an analyzer id to an emitted accessor, and the drop path
already reads it back (`capture_drop_nodes`, `transformer.rs:6707`) — the
precedent for "a transformer-minted name the drop machinery can still find".
(ii) B68's `drop_sink_value_types: HashMap<Id, TypeId>`
(`analyzer.rs:8445` / `Program`), which types an **unbound resource-valued
expression** keyed on the *argument expression's id*, with a never-silent
guard (`unresolved_drop_sinks`, reported at `transformer.rs:2154`). That is
already the right key space for C11 — an expression id, not a binding id —
and it already fires for exactly one expression position. Widening its
population rule is the analyzer half of either option.

Nothing anywhere special-cases a resource-typed temporary. The only
acknowledgement of unbound resource values in the tree is B68's, scoped to
arguments of `drop` itself.

---

## 3. The probes

All emitted output is verbatim, from `vilan build` at `next` @6edf6261,
readable (dev) naming.

### P1 — `Database`: the leak with a synchronous constructor

Source: a bound handle as control, then the temporary spelling.

```js
const db = new DatabaseSync(":memory:");
try {
	db.exec("CREATE TABLE a (id INTEGER)");
	console.log("bound done");
	new DatabaseSync(":memory:").exec("CREATE TABLE b (id INTEGER)");
	console.log("temp done");
} finally {
	$a(db);
}
```

The bound handle gets `try`/`finally`. The temporary gets nothing — no
declaration, no `finally`, no `$a`. This is not `File`-specific and not
async-specific.

### P2 — `File`: the same, with an asynchronous constructor

```js
const file = await (open2("p2.txt"));
try {
	console.log(await (read_at(file, buffer, 0)));
	console.log(await (read_at(await (open2("p2.txt")), buffer, 0)));
	console.log((await (read_file_to_str("p2.txt"))).length);
	await (unlink("p2.txt"));
} finally {
	$a(file);
}
```

Line 3 is C11: `await (open2("p2.txt"))` sits inline in argument position,
unbound. Note also that `const file = …` is **outside** the `try` — §2's
mid-acquisition law, visible.

### P3 — the loop, and the correction

```js
for (const i of [ 1, 2, 3 ]) {
	total = total + (await (stat(await (open2("p3.txt")))))[0];
	console.log("iteration " + i);
}
console.log(total);
for (const j of [ 1, 2, 3 ]) {
	const f = await (open2("p3.txt"));
	try {
		total = total + (await (stat(f)))[0];
		console.log("bound iteration " + j);
	} finally {
		$a(f);
	}
}
```

The bound handle's `try`/`finally` is **inside the loop body** — the loop
body is a drop scope, so a bound handle closes per iteration. This is the
correction: **a temporary written in a loop body would be freed per
iteration under *both* options.** The loop separates the options by one live
handle and by holding duration, not by N. §5.2 has the measurement and §6.1
the argument.

### P4 — scope granularity, and the one position neither option can hoist out of

```js
if (cond) {
	const a = await (open2("p4.txt"));
	try {
		console.log((await (stat(a)))[0]);
	} finally {
		$a(a);
	}
}
const b = await (open2("p4.txt"));
try {
	console.log((await (stat(b)))[0]);
} finally {
	$a(b);
}
if (cond) {
	console.log((await (stat(await (open2("p4.txt")))))[0]);
}
console.log(cond && (await (stat(await (open2("p4.txt")))))[0] > 0);
```

An `if` arm is a drop scope; a bare block is a drop scope emitted flattened.
The last line is the residue §7 owns: a temporary born on the right of a
short-circuit is **conditionally evaluated**, so no lift to a preceding
statement position is legal for it, under either option.

### P5 — the move checker already separates the leak from the non-leak

```js
console.log(await (consume(await (open2("p5.txt")))));
$a(await (open2("p5.txt")));
const f = await (make());
console.log((await (stat(f)))[0]);
$a(f);
console.log((await (stat(await (open2("p5.txt")))))[0]);
```

Line 1: a temporary moved into an `own` parameter — the callee drops it, and
must not be double-dropped. Line 2: a temporary moved into std's `drop` sink
(B68). Line 3: a temporary moved *out* of a helper by `ret`, then bound.
**Only line 5 — the loan-taking receiver — leaks.** The predicate this paper
needs is therefore not new analysis: it is "a resource-typed value that is
neither a place nor moved anywhere", and the move checker already computes
both halves (`collect_resource_value_places`, `analyzer.rs:7329`, plus
`plan_expr`'s `consuming` flag).

### P6 — the leak, measured

Ten temporaries in a loop vs ten bound handles in a loop, printing
`readdirSync("/proc/self/fd").length` around each. **Verbatim program
output:**

```
start fds: 21
after 10 temporaries: 31
after 10 bound handles: 31
200
```

Ten descriptors acquired and never released; the bound loop is net zero (all
ten of its handles opened *and* closed). The value (`200`) is right in both.

### P7 — the decisive measurement: both candidate lowerings, hand-written

Three straight-line statements in one scope, each opening a temporary and
printing the fd count *inside* the statement, plus a count before (`A`) and
after (`B`) all three. `TODAY` is the compiler's own emitted file. The other
two are that file with the candidate lowering hand-written in (the drop
helper and `__fs_close` copied verbatim from `vilan/test/file.mjs`); all
three were executed. **Verbatim output:**

```
### TODAY (no drop) ###
A fds=21
1 size=10 fds=22
2 size=10 fds=23
3 size=10 fds=24
B fds=24
### (b) STATEMENT-END ###
A fds=21
1 size=10 fds=22
2 size=10 fds=22
3 size=10 fds=22
B fds=21
### (a) SCOPE-END ###
A fds=21
1 size=10 fds=22
2 size=10 fds=23
3 size=10 fds=24
B fds=24
```

Read the third block carefully. **Scope-end is observationally identical to
today at every point inside the scope.** Its `B` is 24, not 21, because `B`
is still inside the scope — the drop fires after the scope's last statement,
which no observation in the scope can precede. §6.1 turns that into the
argument.

The (a) lowering used is the existing `walk_scope_body` shape, nested to
scope end:

```js
const $t1 = await (open2("p7.txt"));
try {
console.log("1 size=" + (await (stat($t1)))[0] + " fds=" + __fd_count());
const $t2 = await (open2("p7.txt"));
try {
…
} finally { $a($t2); }
} finally { $a($t1); }
```

and the (b) lowering is the same shape with the `finally` closed at the
statement:

```js
const $t1 = await (open2("p7.txt"));
try {
	console.log("1 size=" + (await (stat($t1)))[0] + " fds=" + __fd_count());
} finally { $a($t1); }
const $t2 = await (open2("p7.txt"));
try {
…
```

### P8 — the error path

A statement that throws *after* its temporary is born. **Verbatim:**

```
### error path, TODAY ###
A fds=21
caught: statement threw
B fds=22
### error path, (b) statement-end ###
A fds=21
caught: statement threw
B fds=21
```

Today a caught mid-statement throw leaks the handle permanently. Both options
fix it, because both lower to `finally` and JS routes `throw`, `ret`,
`jump break`/`jump continue` through it natively — `destruction.md` §5's
"every exit runs drops" holds for either without a new mechanism.

### P9 — the loop, both options measured

Ten iterations, an `await` in the loop body *after* the temporary, printing
the fd count after the loop. **Verbatim:**

```
in-loop TODAY  peak fds=31
in-loop (b) stmt-end  peak fds=21
in-loop (a) scope-end peak fds=22
```

31 vs 22 vs 21. The loop is decisive against **today** (+10, unbounded in
the iteration count) and separates the two options by exactly one handle.
Stated plainly because the brief expected otherwise.

### P10 — Q1's fire-and-forget close composes with statement-end

`File`'s `Drop` initiates `close()` without awaiting it (`filesystem.md`
§5.1, RULED 2026-08-27). Five back-to-back statement-end drops with **no
further await inside the statement**, counting fds immediately after each
`finally`. **Verbatim:**

```
A fds=21
  after stmt 1 fds=21
  after stmt 2 fds=21
  after stmt 3 fds=21
  after stmt 4 fds=21
  after stmt 5 fds=21
B (after a tick) fds=21
```

No accumulation, and the descriptor is back before the next statement is
observed. This is a measurement, not a mechanism claim — what it establishes
is that the Q1 ruling needs no revisiting for either option: the drop *call*
is the same `$a` in both, and statement-end does not make an un-awaited close
observably late. `Database`'s close is synchronous, so its release is exact.

### P11 — closures and `with_file`

```js
const sizes = await ($a([ "p9.txt", "p9.txt" ], async (p) => {
	return (await (stat(await (open2(p)))))[0];
}));
const both = await ($b("p9.txt", async (f) => {
	return (await (stat(f)))[0] + (await (stat(await (open2("p9.txt")))))[0];
}));
```

A closure body is its own scope, so a temporary inside one is a
**tail-position** temporary: the return value must be computed before any
teardown, so both options lower it as `try { … } finally { … }` around the
return. Identical under (a) and (b). R9 is untouched — a temporary is not a
capture, and `with_file`'s `f` is a per-call parameter, which `destruction.md`
R9 already exempts. `with_file`'s own awaited close is unaffected: it owns a
*binding*, and the benign destructor re-entry `filesystem.md` §5.1 records
(the host close is idempotent, probed) is not made worse by a temporary in
the body, which is a different handle.

---

## 4. What `destruction.md` actually constrains

Read before claiming. The ratified file says four things that bear on this,
and one of them is a silence.

1. **§5, timing.** "At the owner's scope end, still-owned resource **locals**
   drop in reverse declaration order … Every exit runs drops: fall-through,
   `ret`, `jump break`/`jump continue` … and panic unwinding." *A temporary
   is not a local and has no declaration.* The file legislates the timing of
   locals and says nothing about temporaries. **This is the silence, and it
   is why the leak is a gap rather than a violation.**
2. **§7, lowering.** "`try`/`finally` per resource-owning **scope**. Only
   scopes that own resources pay. The `finally` drops still-owned locals in
   reverse order; **R7 makes 'still-owned' static, so there are no runtime
   flags.**" The no-runtime-flags clause is the real constraint on both
   options, and §7 of this paper is where it bites.
3. **§5, early teardown.** "moving into `drop(db)` destroys at its
   (immediate) scope end. No public `close()` surfaces … no double-close
   states." Nothing here forbids a second *compiler-inserted* drop point; it
   forbids a second *user-visible* teardown path. Neither option adds one.
4. **§4 R7.** "A binding must be moved on every path through a scope or on
   none … This keeps end-of-scope ownership static — no runtime drop flags in
   v1." Read as a doctrine rather than a rule about bindings, R7 is the
   language's standing answer to "when the compiler cannot tell statically
   whether a value is live, refuse rather than flag." §7 applies it.

And one constraint that is not in `destruction.md` but is in the house
doctrine it cites (§4, R2's B99 amendment) — **two spellings of the same
thing must not be distinguishable**:

> `slot.held` and `view.held` are the same expression shape and differ only
> in what the root binding is, so an answer that consulted the root would
> make the two spellings distinguishable — the thing B81/B88/B94 exist to
> forbid.

This is the strongest argument *against* the recommendation, and §6.2 takes
it at full strength.

---

## 5. The two options, measured

Both options need the same three new pieces: an analyzer predicate marking a
resource-typed expression as an **owning temporary**, a transformer lift of
that expression to a minted declaration at a statement position, and a
`resource_drop_of` call in a `finally`. They differ in **one thing**: where
the `finally` closes.

### 5.1 Option (a) — scope-end

The temporary joins the enclosing scope's drop set. Lowering is *exactly*
today's `walk_scope_body` shape, with a fourth `ScopeTeardown` variant
(`Temporary`), the declaration outside the `try` and the rest of the scope
nested inside.

- Composes with `destruction.md` §5's reverse-declaration order by taking a
  position in it — the temporary is declared where its statement is, so
  "reverse declaration order" extends naturally.
- Needs no change to §7's "per resource-owning scope".
- **Measured (P7): observationally identical to today at every point inside
  the scope.** Peak live handles in a straight-line scope with N temporaries
  is N.
- **Measured (P9): one live handle in a loop body** — the loop body is its
  own scope, so it does free per iteration.

### 5.2 Option (b) — statement-end

The temporary's drop region is the statement it is born in. Lowering is the
same shape, non-recursive: declaration, `try` around the one statement,
`finally`, then the scope continues normally.

- **Measured (P7): peak one live handle** regardless of how many temporaries
  the scope contains; the count returns to baseline while still inside the
  scope.
- **Measured (P9): zero observed live handles** after the loop; peak one.
- **Measured (P8): the error path is covered** by the same `finally`.
- **Measured (P10): composes with Q1's fire-and-forget close** with no
  observable lag.

### 5.3 The case that separates them

Not the loop. **A scope that does not end.**

`filesystem.md` §5 records — this is the S3 correction that struck the
module-level bullet — that a process-lifetime `File` **cannot** be a module
global (every constructor is async; a module initializer cannot await), so:

> The serve-forever handle is a LOCAL in `main` instead: owning across awaits
> is legal, and **a `main` that never returns never drops it.**

That is the fs paper's *recommended idiom* for a long-running program. Under
option (a), every resource temporary anywhere in such a `main` joins that
scope's drop set — a scope that, by design, never ends. **The fix would be a
no-op for exactly the program shape the filesystem paper names as the
idiom**, and P7's `B fds=24` is that no-op measured: three temporaries, three
descriptors, still held at the last observation the scope can make.

`destruction.md` §5 already legislates one class of never-dropping resource
("Module-level resources never drop — process lifetime; Rust-statics
precedent; documented"). It did so **deliberately, for a named class, with a
corollary making that class loan-only** so the decision cannot be
accidentally inherited. Option (a) would silently extend "never drops" to a
second class the owner has not ruled on, in the one program shape where it
matters most. That is not a small difference in timing; it is the difference
between fixing C11 and appearing to.

---

## 6. Recommendation — **(b), statement-end**

### 6.1 The argument

A temporary should die where it stops being reachable, and for a temporary
that is the end of its statement. Three reasons, in order of weight:

1. **(a) does not reliably fix the thing the ruling asked to fix.** §5.3.
   "Those should not leak" is a statement about the resource's lifetime, and
   (a) makes that lifetime *the enclosing scope's* — which for the serve-
   forever `main` the fs paper recommends is the process. Measured, not
   argued: P7's scope-end column is byte-for-byte the same as today's at
   every observation.
2. **(b) bounds the live-handle count by the program's nesting, not its
   length.** N temporaries in a straight-line scope hold N descriptors under
   (a) and one under (b) — P7, three temporaries over a baseline of 21:
   (a) climbs to 24 and stays there for the life of the scope, (b) never
   exceeds 22 and is back at 21 before the scope ends. Descriptor exhaustion
   is a real failure mode with a terrible diagnostic (`EMFILE` from an
   unrelated later `open`),
   and the whole point of `Drop` as a *net* is that the net catches things
   before they pile up.
3. **(b) is what a user who wrote the shorter spelling asked for.** Binding a
   value is how vilan says "keep this"; not binding it is how it says the
   opposite. Rust decided this exactly the same way — temporaries drop at the
   end of the enclosing statement, `let` extends to scope end — and vilan's
   `resource` class is Rust-shaped by explicit design (`destruction.md` §5:
   "`&mut self`, exactly Rust's shape"). Adopting Rust's answer to Rust's
   question is the conservative move, not the novel one.

### 6.2 The strongest counterargument, at full strength

**Statement-end makes two spellings of the same operation
distinguishable, and the house doctrine forbids that.**

```vilan
let f = File::open(p);        // the handle lives to scope end
print(f.stat().size);
```
```vilan
print(File::open(p).stat().size);   // the handle lives to statement end
```

Under (b) these two programs — which a reader would call the same program,
one of them refactored — have different resource lifetimes. `destruction.md`
§4's B94/B99 amendments say, in terms, that making two spellings of one thing
distinguishable is "the thing B81/B88/B94 exist to forbid", and they paid
real implementation cost to avoid it. Option (a) does not have this problem
at all: under (a) there is exactly one timing law in the language — *scope
end* — and the temporary is simply a local whose declaration the compiler
wrote for you. A user learns one rule. Under (b) they learn two, and the
second one is invisible in the source (nothing marks where a statement's
drop region begins).

There is a sharpened version of this that is worth stating too: (b) makes a
**refactor** change behavior. Extracting `File::open(p).stat().size` into
`let f = File::open(p); f.stat().size` lengthens the handle's life; inlining
it shortens it. On Windows, where an open handle blocks a rename or delete
(`filesystem.md` §5.1's honesty note on Q1), that refactor can turn a working
program into a failing one, or the reverse. That is a genuine cost and it is
not hypothetical.

**Why the recommendation stands anyway.** The doctrine those amendments state
is narrower than it first reads, and its own examples show it: B94/B99 are
about *the same expression* being read differently depending on what its root
binding happens to be — `slot.held` and `view.held`, where the user wrote the
same thing and the compiler consulted something the user did not write. Here
the user wrote something different. `let` is not incidental syntax; in a
language with affine resources it is the *only* way to name a value, and
naming a value is the whole of what "keep it" means. The two programs are not
one program in two spellings; they are a program that names a handle and a
program that does not, and R1 already makes the difference load-bearing (the
bound one can be used again; the temporary cannot be used at all). A language
that says "binding extends life, not binding does not" has one rule, stated
once, with a syntactic marker — the `let` — that is exactly where the reader
looks.

And the counterargument cuts both ways on the refactor point: under (a) the
*other* refactor is the dangerous one. Moving a statement earlier in a scope,
or wrapping a scope's tail in a long-running loop, silently extends every
temporary's life to cover it, with nothing in the source to notice.

### 6.3 Implementation size — the honest comparison

**Not materially different, and both are small.** §2 established that the
declaration lands at the same statement position under both, so the delta is
where the `finally` closes: (a) recurses into the scope tail using
`walk_scope_body`'s existing recursion; (b) does a non-recursive
single-statement wrap. Both call `resource_drop_of`, which is already
value-node agnostic. Both need the same analyzer predicate and the same
transformer lift, and neither can reuse a lifting that does not exist (§1.1).

Two places the sizes genuinely differ, both small and both in (b)'s favour:

- **The id space.** `dropped_bindings` is `HashSet<Id>` over *bindings*. (a)
  wants the temporary to be *in* a scope's drop set, which either means
  minting a synthetic binding entity in the analyzer — and then teaching R2,
  R7 and R11 that such a thing exists — or maintaining a parallel per-scope
  side table with its own ordering. (b) wants a per-statement fact keyed on
  the *expression id*, which is precisely the shape B68 already built
  (`drop_sink_value_types: HashMap<Id, TypeId>`, `analyzer.rs:8445`),
  never-silent guard included.
- **Emitted bytes.** (a) re-nests and re-indents the entire tail of every
  scope containing a temporary; (b) touches the offending statement. This is
  the same trade B141's own fix made when it chose the context-aware
  `postfix_subject` over a blanket wrap because "the context-aware rule moves
  **zero** goldens" — the house preference for the narrow edit is on the
  record, from this exact code path.

### 6.4 The ordering question (a) opens and (b) closes

`destruction.md` §5 fixes scope-end drops in **reverse declaration order**.
Under (a), a temporary takes a position in that order and the spec must say
which — including for `f(File::open(a), File::open(b))`, two temporaries in
one statement interleaved with bindings declared before and after. Under (b)
the question does not arise: a temporary is destroyed before the next
statement runs, so it never interleaves with a scope-end drop set at all. Two
temporaries in one statement drop in reverse birth order within their own
`finally`, and that is the whole rule.

---

## 7. The narrowest amendment each option needs

### 7.1 Under (b) — the recommendation

Two additions to `destruction.md`, no deletions.

**§5, a new bullet after "Timing and order":**

> **Temporaries.** A resource-typed value that is neither bound nor moved is
> an *owning temporary*: it is owned by the statement in which it is
> constructed, and drops at that statement's end, before any enclosing
> scope's drops and in reverse construction order among the temporaries of
> that statement. A resource that is bound (`let f = …`) or moved (into an
> `own` parameter, into `drop`, into `ret`, into an aggregate literal) is not
> a temporary and is unaffected.

**§7, one clause widened:**

> `try`/`finally` per resource-owning scope **or statement**. Only scopes and
> statements that own resources pay.

### 7.2 Under (a)

One addition and one **edit to a ratified sentence** — §5's "still-owned
resource **locals** … in reverse **declaration** order" must be widened to
cover a thing that is neither a local nor declared, and §6.4's ordering must
be specified. That is a larger amendment surface than (b)'s, which is a
secondary argument, not a primary one.

### 7.3 The residue both options share: the conditional temporary

P4's last line: `cond && File::open(p).stat().size > 0`. The temporary is
born on a conditionally-evaluated operand, so it cannot be lifted to a
preceding statement position without changing the program (the `open` would
run when `cond` is false). Ternary arms and non-block `match`-arm expressions
are the same shape. The only lowerings available are a runtime liveness flag
(`let $t = undefined; … finally { if ($t !== undefined) $a($t); }`) or a
refusal.

**Recommend the refusal**, and read it straight off `destruction.md` §7's
"R7 makes 'still-owned' static, so there are no runtime flags":

> **R7, extended to temporaries.** A resource temporary must be constructed
> on every path through its drop region or on none. A resource constructor in
> a conditionally-evaluated operand — the right of `&&`/`||`, a ternary or
> `match`-arm expression that is not a block — is rejected: "this resource
> would be created only on some paths; bind it, or put the expression in a
> block."

This is identical under both options and is deliberately narrow: it refuses a
*spelling*, never a program — `let f = File::open(p); cond && f.stat().size > 0`
is the fix and it is one keystroke's worth of restructuring, exactly the
shape R7 already asks for. It also keeps the recommendation honest about not
introducing runtime drop flags into v1 by a side door.

---

## 8. Non-goals

- **Reopening the direction.** Rejecting the temporary spelling is off the
  table by ruling. This paper does not price it.
- **Reopening Q1.** `File`'s fire-and-forget close stands (`filesystem.md`
  §5.1, RULED 2026-08-27, scoped to `File` alone). P10 verifies it composes
  with the recommendation rather than assuming it.
- **Async drop.** `destruction.md` §5's "drop is synchronous in v1" is
  untouched, and nothing here needs it relaxed.
- **Drop flags for v1.** §7.3 refuses rather than flags, on purpose.
- **Tier 2 / `Weak<T>` / refcounting.** C11 is a Tier 1 gap.
- **Rewriting the corpus.** `vilan/test/file.vl` and `db.vl` contain the
  offending spellings deliberately (B141's positive pins). Their goldens will
  move when this lands; that is the fix being visible, and §9's plan gates it.
- **`List<Resource>`.** R10 still rejects it; nothing here changes what a
  temporary may be built from.

---

## 9. Test plan sketch

Every case red-first against a plant, per the house rule.

**Emission (goldens, byte-level).** `vilan/test/file.mjs` and `db.mjs` move
— the two existing B141 positive pins acquire `finally`s. That movement *is*
the gate: assert the new bytes, and assert the value pins still pass
unchanged (the fix must not alter what the programs print).

**Execution pins** (`crates/vilan-core/tests/inference.rs`, alongside B141's
ten at `inference.rs:9512`; per B145's split, into the subject module the
split creates):

1. `a_temporary_receiver_drops_at_statement_end` — the P7 shape, asserting an
   fd/close counter returns to baseline *within* the scope.
2. `a_temporary_in_a_loop_body_drops_each_iteration` — P9, peak 1.
3. `a_temporary_drops_when_its_statement_throws` — P8, the `finally` path.
4. `a_temporary_drops_before_a_later_statements_temporary_is_built` — the
   ordering fact (b) buys.
5. `two_temporaries_in_one_statement_drop_in_reverse_construction_order`.
6. `a_temporary_moved_into_an_own_parameter_is_not_dropped_twice` — P5 line 1,
   the double-close counter-pin. **The critical negative.**
7. `a_temporary_moved_into_the_drop_sink_is_not_dropped_twice` — P5 line 2.
8. `a_temporary_returned_by_ret_is_not_dropped` — P5 line 3.
9. `a_temporary_in_a_closure_body_drops_in_the_closure` — P11.
10. `a_temporary_in_a_tail_position_drops_after_the_value_is_computed`.
11. `a_conditionally_constructed_resource_temporary_is_refused` — §7.3, with
    its diagnostic text (ledger row; `diagnostics-standard.md` applies).
12. `a_bound_resource_still_drops_at_scope_end` — the control, proving the
    existing law did not move.

**Runtime e2e** (`crates/vilan-cli/tests/fs.rs`, beside B141's at `:1019`):
a program that opens N temporaries in a straight-line scope and asserts the
descriptor count is flat — the P6/P7 measurement, made permanent.

**Macro-interpreter arm.** `destruction.md` §7's recorded gotcha: "Every
helper needs its macro-interpreter arm." A statement-region drop is a new
emission shape; the equivalence gate must be checked, not assumed.

**Coloring.** `destruction.md` §8's synthetic ownership edge (a scope owning a
droppable `T` reaches `T`'s drop impl in the call graph) must extend to a
*statement* owning one, or a `@process`-needing drop behind a temporary will
be invisible to reachability. Pin it — this is the interaction most likely to
be missed, and E98 (the double-drawn coloring diagnostic, filed by the same
lane) is adjacent.

---

## 10. Placement

**This should be a `destruction.md` amendment, not a standing paper**, and it
is written as a paper anyway because the ratified file is amended at build
time, not by this lane. §7.1 is the amendment text, ready to lift: two
additions to §5 and one widened clause in §7, plus §7.3's R7 extension in §4.
The rest of this file is the argument and the evidence for the ruling, which
is what `destruction.md` should *not* carry — it carries decisions, with the
one-line "(amended YYYY-MM-DD — finding)" provenance the file already uses
throughout §4.

Recommendation for the build lane: land §7.1 and §7.3 into `destruction.md`
with the usual amendment markers, add a line to `filesystem.md` §11.1
retiring the struck honesty note, and archive this file — its job is done
once its text is in the ratified record. It should **not** become a second
place to look up when a resource dies.

---

## 11. Open questions for the owner

**Q1 — statement-end or scope-end?** The paper recommends **(b) statement-end**,
on §5.3's never-ending-scope argument and §6.1's measurements, having stated
§6.2's distinguishability objection at full strength. If the objection wins,
(a) is coherent and cheap — it just does not fix the serve-forever `main`,
and that limit would need saying out loud in `destruction.md` §5 beside the
module-level bullet, since it becomes the same class of documented
never-drop.

**Q2 — refuse the conditionally-constructed temporary (§7.3), or flag it?**
The paper recommends the refusal, extending R7's doctrine rather than
admitting v1's first runtime drop flag. The cost is that
`cond && File::open(p).stat().size > 0` stops compiling; the fix is a `let`.
This is the one place the recommendation makes a currently-accepted program
an error, so it is the owner's call and not the lane's.

**Q3 — does the corpus keep the temporary spellings?** `file.vl` and `db.vl`
carry them as B141's positive pins, and their goldens will grow `finally`s.
Keeping them is recommended (the idiom should be gated where it is taught),
but it means the fs tier's documented idiom is also the language's example of
a compiler-inserted drop — worth a deliberate yes rather than a default.
