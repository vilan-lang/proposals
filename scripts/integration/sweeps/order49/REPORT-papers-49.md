## papers-49: the array-lengths paper (I2 with A163)

The paper is written, along with 6 finds (repros plus a JSON entry each). I changed nothing in the vilan tree and committed nothing; the integrator commits proposals. All probes ran on the installed `vilan 0.46.0 (92c621848)`, which is next @445c9346's compiler, on both backends. No cargo build was needed.

**Paper:** `/home/reed/code/vilan-lang/proposals/projects/vilan/proposal/array-lengths.md` (518 lines, in the type-ascription paper's form). Sections:
- §0 The ask, and the answer up front
- §1 Ground truth (0.46.0)
- §2 What "every length" needs (A163's four, located)
- §3 The representation
- §4 The grammar
- §5 The rules (what `const N` means, inference, inside a body, selection, `len()`'s type, the length literal)
- §6 Named lengths and the staging fork
- §7 The narrow door
- §8 Mono and the two emitters
- §9 Conversions, slicing, the std surface
- §10 The estate
- §11 B582 alone
- §12 Interactions
- §13 Finds
- §14 Questions
- §15 Slices

Also under `scripts/integration/sweeps/order49/papers-49/`:
- `probes/`: 42 probe programs, `run_all.sh`, and `run_all.out` (the outputs quoted in the paper).
- `census/`: `census.py` and `census.out`.

### The answer in three sentences
1. A length should be a type-level number: `Type::Array(TypeId, usize)` becomes `Type::Array(TypeId, TypeId)`, with a new `Type::Length(n)`, so a length binder is an ordinary generic and the existing substitution map (`HashMap<TypeId, TypeId>`), `bind_subject`, `reconcile_type` and both `write_type_key`s take it as they are.
2. `[type T; _]` is `[type T; const N]` with the name declined (as B294's `_` relates to `type T`); it costs the same four changes as the named form, so the ruling "goes with I2" holds: one slice ships both head spellings, and the next adds `<const N>` to generic lists. `<const N>` means a `usize` length and nothing else, monomorphized like a type.
3. The staging fork goes away for the subset that needs no evaluation: a length may be a literal, a const parameter, or a name bound immutably to an integer literal (const-eval's existing `classify` line), resolved before the fixpoint; anything needing arithmetic or a call is refused with the reason.

### Estate
- **9 `[T; n]` sites in total, every length a literal of 4 or less:**
  - corpus: 7, all in `fixed-arrays.vl` (lengths 2, 3, 4)
  - the book's tour: 2 (lengths 4, 3)
  - std, examples, kolt (a `cp -r` copy), the website, the playground, benchmarks and macro_std: 0 each
- **Non-literal lengths: 0.** The compiler refuses them today.
- **Array impl subjects: 0 anywhere.**
- **What breaks:** the new forms are additive. B?1 (below) is breaking in principle, but its estate is 4 `.len()` calls on arrays, all passed to `print`, so no edits and no goldens move.

### Questions and recommendations
1. **Representation:** R2, the length as a TypeId, over an inline enum or a subject-only wildcard.
2. **Spellings:** `[type T; _]` and `[type T; const N]` in impl subjects, `<const N>` in generic lists, and a number as a generic argument (`zeros<4>()`).
3. **Constraint form:** a bare `<const N>` meaning a `usize` length, with no other value kinds and no bounds in v1.
4. **Named lengths:** an immutable `let` or `const let` whose initializer is an integer literal or another such name, imports included. Arithmetic is refused.
5. **`N` as a value:** yes, a `usize` folded per instance. A `const` expression may not read it.
6. **`len()`'s type:** `usize`, fixed now and independently (slice S0b).
7. **The narrow door alone:** no; `_` and `const N` ship together in S2.
8. **Structs and enums generic over a length:** yes, in S3.
9. **Conversions:** `to_list()` and `to_array(): Option<[T; N]>`, explicit only, no coercion.
10. **Slicing:** out of I2. A `slice(from, to): List<T>` copy method in std; a range literal `a..b` would be its own item.
11. **JS:** keep one instance per length; erase the length from the key only if a measurement shows code size matters.
12. **Native:** keep `[T; N]`, close F109 as fixed by F100, and box large arrays.
13. **std's first wave after S2:** Items (A161), PartialEq/Eq, Hashable, Debug (E283's array half), to_list, iter.

**Slices** (§15 has the table with sizes, needs and gates):
- now, in solver-49: S0 = B582 (XS); S0b = B?1 (XS)
- after the M110 S5 verdict (they touch the analyzer core):
  - S1 (M): the R2 representation, byte-identical output.
  - S2 (M): the impl heads.
  - S3 (M): generic lists.
  - S4 (S): named lengths, with E?1.
  - S5 (S): std.
  - S6 (S): the book and spec.

### Finds
The entries are in `sweeps/order49/newitems49-papers.json` with placeholder ids. Repros are in `sweeps/order49/papers-49/finds/`.
- **B?1:** `[T; n].len()` is typed `i32` where every other length is `usize`; I5 S2 missed it because it is a compiler fold, not a std signature. `a[a.len() - 1]` passes the check, runs on JS, and is refused by rustc.
- **B?2:** the subscript's `usize` check lets through an index whose type is not known yet when the subscript resolves. `xs[one()]` and `xs[n.max(0)]` with `i32` answers check clean. A negative index panics with "-1" on JS and "18446744073709551615" natively.
- **E?1:** non-literal array lengths get poor diagnostics:
  - In type position the parser says "found '[' expected a type".
  - The fallback length 0 causes cascading errors.
  - Any numeric suffix is accepted as a length (`3f64`, `2i8`).
  - An empty array's out-of-range message says "valid indices are 0 to 0".
- **F?1:** natively, any struct with an array field fails to build, because vilan-rt has no `Js` impl for `[T; N]`.
- **F?2:** natively, `[0; 4000000]` overflows the stack while JS runs it.
- **D?1:** `spec/grammar.md` has no production for the `[T; n]` type or the `[v; n]` repeat literal.
- **Not filed:** F109 does not reproduce on 0.46.0. F100 already lowers the directed literal to a Rust array, and F109's own repro prints `1` on both backends. native-49 should confirm and close it.

### What B582 unlocks alone
- **The fix:** add one arm to `register_subject_binders` (analyzer.rs:36157), `Node::ArrayType(element, _) => recurse into element`. Selection already binds through an array's element, so nothing else is needed and it waits for nothing.
- **What it enables:** element-generic impls at one literal length each, such as `impl [type T: PartialEq; 2] with PartialEq` and the nested `impl Option<[type T; 2]>`.
- **What it does not enable:** A161 or any impl covering every length. std would need one impl per length, a table I recommend against.
- **Later:** it is the arm S2 extends to register the length binder.
