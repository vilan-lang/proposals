## papers-b-48 report: three papers, estates counted, 3 finds

I made no change to the vilan tree. Nothing is committed in proposals; the papers are left for you.

### Papers
- `/home/reed/code/vilan-lang/proposals/projects/vilan/proposal/named-tuple-fields.md` (B569)
- `/home/reed/code/vilan-lang/proposals/projects/vilan/proposal/auto-annotations.md` (B570)
- `/home/reed/code/vilan-lang/proposals/projects/vilan/proposal/type-ascription.md` (B571 + E278)

Supporting material is under `proposals/scripts/integration/sweeps/order48/papers-b-48/`:
- `probes/` — 33 probes; re-run with `run_all.sh <scratch>`, output in `run_all.out`.
- `census/` — a walker built on the tree's own parser (`parse_preserving_groups`). It classifies every assignment by the tokens around it, and also counts `as` tokens, tuples, and functions or module bindings with no annotation. Raw output for each estate is beside it.
- `finds/` — the repros.

The probes ran on the installed `vilan 0.45.0 (e75bc57c3)`, which is the same commit as origin/next. The only cargo build was the census crate, once.

### Recommendations and key numbers

**B569, named tuple fields.**
- Labels become a slot in `Type::Tuple`. Unification carries them but does not compare them, and `Eq`/`Hash` ignore them. This is the same shape as B309's closure clause.
- The same label set in a different order is refused, not warned. The paper widens the rule slightly: refuse any label that both sides carry at different positions. The error offers two quick fixes, by name and by position.
- `(x = 5)` becomes a one-slot labelled tuple. That is what makes named arguments work through a spread parameter.
- Assignment is refused wherever its value would be used. It stays legal as a statement, a block tail, a match arm, a closure body, or a then/else branch.
- **Estate: 1,696 assignments across std, the corpus, the examples, the docs (601 code blocks), a copy of kolt and a copy of the website. None is in a value position, so the ban breaks 0 sites.**
- Labels are erased at mono, in both emitters and in the contract hash. Tuples have no Wire or Json impl today; when they get one it should be positional.

**B571, `EXP as T`.**
- It types exactly like `let tmp: T = EXP`: the expected type flows in, and every coercion an annotated binding does applies, including `as dyn Flow<i32>` erasure (E261 inline). It is not a binding, so no copy, and it is a value, never a place.
- It is a postfix in the chain tier, and `as` stays contextual. `as` is a legal binding name today; the estate has none.
- The whitespace rule costs nothing: `vilan fmt` already writes `List <i32>` as `List<i32>` and `a<b` as `a < b`. The estate has 0 spaced generic lists.
- **`as` in expression position = 0**, confirmed: `1 as f64` is a parse error, and all 24 `as` tokens in the estate are import aliases.
- E278: the hint is spelled `as ~Pipe<T>`. The code action writes the bare trait `as Pipe<T>`, which is checked and keeps the concrete type (confirmed by probe a16), or `as auto T` once B570 lands.

**B570, `auto` annotations.**
- `auto T` is a signature, not a constraint. The body is inferred as if unannotated, callers read `T`, and `check` refuses a mismatch as stale with `--fix`, which plugs into the existing `check --fix` loop. The editor rewrites on save through a `source.fixAll` action, the same way `organizeImports.onSave` works.
- For long stage types, `auto` writes what the inlay hint shows, with `~X` written as the bare trait `X`.
- Firewall: in incr-47's S0 session, 4 of 40 interface moves were all broken mid-typing states of one function in `model.vl` (hot set 12 of 27); under `auto` they become 0. In kolt, 99 of 262 hand-written functions omit their return type (38%) and 32 of 33 module bindings are inferred; under `auto` their interfaces can be read from the parse alone. 57% of the owner's body edits were in functions with an inferred return.
- Opt-in "exported" would write 54 annotations in kolt (99 counting inherent methods), 234 in the website, and 17 in std (126 with methods).

### Questions for the owner (each has a recommendation in its paper)
- **B569:**
  - Q1 where labels live: a slot in `Type::Tuple`.
  - Q2 a reordered label set: refuse, with the wider rule.
  - Q3 which positions keep assignment: the permissive set, which breaks 0 (the stricter set rewrites 38).
  - Q4 `(x = 5)`: a one-slot labelled tuple.
  - Q5 mixing labelled and unlabelled slots: refuse.
  - Q6 Wire/Json: positional, and labels stay out of the contract hash.
  - Q7 named arguments: ship them, without defaults.
  - Q8 labels in `keys()`: not now.
  - Q9 an `impl` on a labelled tuple: refused.
  - Q10 spread with labels.
- **B571:**
  - Q1 typing like an annotated let.
  - Q2 postfix precedence.
  - Q3 extend the whitespace rule to expression position: later, as its own item.
  - Q4 allow `as` after a match/if brace: yes.
  - Q5 value, not place.
  - Q6 keep `as` contextual.
  - Q7 `--fix` rewrites `n as f64` to `n.as_f64()`.
  - Q8 E278 writes the bare trait.
  - Q9 closure types after `as` are read greedily, and the formatter parenthesizes them.
- **B570:**
  - Q1 signature semantics.
  - Q2 callers are checked against the written `T` while it is stale.
  - Q3 door (b) for stage types.
  - Q4 a bare `auto` is a warning.
  - Q5 its own on-save setting.
  - Q6 what counts as "exported".
  - Q7 qualify type names, never add imports.
  - Q8 locals at S3.
  - Q9 std opts in, measured first.

### Finds, filed in `sweeps/order48/newitems48-papers-b.json` (repros in `papers-b-48/finds/`)
- **B?1:** a binding nothing can type checks clean. `let xs = []; xs.len()` and `let o = None;` pass `vilan check` and run on JS. Natively, the first is refused with a misleading "F1 slice S1b" message, and the second is emitted untyped (rustc would refuse it; not built here).
- **B?2:** spec/behaviour mismatch. `spec/types.md` §5.9 says `log(1, "hi") == log((1, "hi"))`, but a spread function called with one tuple collects it into a one-slot pack and refuses it. This matters for the named-arguments door.
- **E?1** (low): `a < b > (c)`, spaced, is read as a generic call and gives the error "cannot call this as a function: it is i32".

### To reap
- Worktree `/home/reed/code/vilan-lang/vilan/.claude/worktrees/papers-b-48`, on local branch `papers-b-48` at e75bc57c. It has no commits and is clean.
- Its `target/papers-b-48-scratch/` holds the copies of kolt and the website, the census build and the probe scratch.
- Delete the branch along with the worktree.
