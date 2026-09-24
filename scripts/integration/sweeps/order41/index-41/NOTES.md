# I5 S2, PREPARED — lane index-41, Order 41

Nothing here is on a branch. It is S2 (`proposal/index-type.md` §9) run end to
end over a SCRATCH copy of `index-41` @ `7c746d47` (A126 + E218 + I5 S1 + the
cherry-picked B389), measured, and saved so that Order 42's `index-42` lane can
re-run it on its own base and review the result rather than author it.

## The files

| file | what it is |
| --- | --- |
| `run_s2.sh` | the whole run: `run_s2.sh <vilan worktree> <scratch>`. Archives the worktree twice (a pristine BASE, the TREE the migration runs on), applies everything below, measures, diffs. `STOP_AFTER=codemod` stops after step 3 (how `hand.patch` is made). `LITERAL_GAPS=0` leaves out `b389-gap-literals.patch`. |
| `compiler.patch` | S2's compiler half: the subscript's expectation becomes `usize`, S1's two-type admission (`i32` beside `usize`) is DELETED, and a numeric index of another width carries E218's conversion (`… convert with `.as_usize()``), so the codemod and the quick fix both reach it. Ledger row 558 re-keyed. |
| `i5_s2_codemod.rs` | the codemod, a `vilan-core` example (§8.1 — NOT A101's text rewriter). `signatures`: the 105 INDEX rows of `order40/papers-40/i5-std-index-sites.tsv`, located BY PARSE and keyed by (kind, module, owner, function, position, written type) — never by line — and respelled `i32` → `usize`. `fix`: the fixed-point loop over the compiler's own diagnostics (library `analyze_source`, so each arrives with its file and byte span, std's own included). |
| `hand.patch` | the hand edits, made against the codemod's output: the 7 sentinels and 8 loops (named below) and the residue the codemod declines. |
| `b389-gap-literals.patch` | two `0usize` suffixes for a gap B389 did not close (finds, below). Drop it when the gap is fixed. |
| `out/` | the measured run: `summary.txt`, `signatures.tsv` (the 105 rewrites), `fix-codemod.tsv` (every edit the loop wrote, `FIX kind file line before after`), `goldens.tsv` + `golden-diffs/`, `examples.tsv`, `s2.diff` (sources), `s2-compiler.diff`, `s2.stat`, kolt before/after. |

## The numbers (run on `7c746d47`)

- **Signatures: 105 of 105** verdict rows found and respelled, 0 unmatched (the census
  ran at 49de3915; keys survive the drift to 7c746d47).
- **The loop wrote 214 edits**, then reached a fixed point: 169 conversions named by
  E218 (at the declared type's direction), 41 operand conversions (the binary-operator
  refusal between `usize` and another width — the NON-index side converts), 4 counters
  declared `usize` at their `let` (a bare name bound by an unsuffixed literal; B389's law
  makes this rare — it was 42 before B389 was picked). By area: std 156, macro_std 6,
  the corpus 52. Direction in std: 60 `.as_i32()` (an index meeting a WIRE `i32` — the
  `begin_list`/`i32_value` seam, byte values, the codec — which is exactly "the 76
  WIRE/STREAM/SEQUENCE positions left alone with an explicit conversion where they meet
  an index"), 101 `.as_usize()`. **No `.as_i53()` was needed**: the STREAM offsets
  (fs.vl, §11 Q1 — they stay `i53`) never met an index in std.
- **Residue after the loop, before hand edits:** std 30 (node) / 18 (browser),
  macro_std 4, corpus 67 — most of it the MACRO-WORLD echo (a `[derive(..)]` in any file
  fails while std has an error, so one std residue shows as dozens of `has no method
  'debug'`). After `hand.patch` + the gap patch: **0 everywhere** (std on both
  platforms, macro_std, all 141 corpus programs).
- **Goldens: 121 byte-identical, 17 moved, 0 fail to build** (138 with goldens). §5.4
  predicted none would move; each move is a conversion or a hand-rewritten loop, never a
  change in how an index itself emits:

  | golden | why it moved |
  | --- | --- |
  | element-clones, iterator-adapters, list-sort | `List::reverse`'s loop rewritten `for index > 0 { index -= 1; … }` (hand, L5) — every program that reaches `reverse` emits std's new body |
  | reconcile-index, reactive-keyed, time | `reconcile`'s chain rewritten to `Option<usize>` (hand, S1–S3/L6–L8) and/or `json` loops (L3/L4) |
  | list-search | the corpus's two `-1` sentinels (hand, S6/S7) |
  | crypto, delta-law, list-cell, option-view, for-mut-container | `.as_usize()` where the program's own `i32` met a `usize` (an `i32` counter indexing, a length compared) |
  | adapt, capture-clones, mut-parameters, side-effect-let | `.as_i32()` where a `usize` length met the program's `i32` (a closure's or function's declared `i32` return) |
  | usize-literals | its two boundary conversions (`get(at.as_i32())`, `len().as_usize()`) flip direction — by design, S2 deletes them |

- **Examples: 11 of 11 check clean** under the migrated std (they were 4 refused before
  B389's law was picked).
- **The diff:** 40 files, +379 −332 (std 31, macro_std 2, corpus 7), plus
  `compiler.patch`.

## The seven sentinels and the eight loops — by hand, each named (`hand.patch`)

None of these is a type error the compiler can see, which is why §8.1 hands them to a
person. Measured the hard way: with B389 in, `mut last_applied = -1; … last_applied =
index;` COMPILES as a `usize` (the binding takes its type from the assignment, and a
negative literal is not refused at an unsigned type — find F2 below), and every `for x
>= 0 { …; x -= 1 }` over a `usize` compiles and never terminates on JS / panics natively.

Sentinels (`-1` → `None` / a real fallback):

- S1–S3 `std/src/reactive.vl` `reconcile`: `next_same.push(-1)`, `None => -1`,
  `mut found = -1` — the chain is `Option<usize>`; `first` drops an exhausted key with
  `remove` where it stored `-1`.
- S4 `std/src/browser/ui.vl` `settled_steps`: `mut highest = -1` → `Option<usize>`.
- S5 `std/src/process/db.vl` `refuse_inserted_migration`: `mut last_applied = -1` →
  `Option<usize>` (the check runs only when something was applied).
- S6–S7 `vilan/test/list-search.vl:10,15`: `index_of(..).unwrap_or(-1)` →
  `unwrap_or(usize::max_value())` (output unchanged; the golden moves).

Downward loops (`for x >= 0 { …; x -= 1 }` → `x = len; for x > 0 { x -= 1; … }`):

- L1 `std/src/browser/ui.vl` `settled_steps`; L2 `row_references`
- L3 `std/src/json.vl` `begin_list`; L4 `begin_variant`
- L5 `std/src/list.vl` `reverse` (also: `self.len() - 1` UNDERFLOWS on an empty list)
- L6–L8 `std/src/reactive.vl` `reconcile` (the build loop, the head walk, the chain walk)

The other hand edits, each a site the codemod declined (multi-line value, a type inside
a type, a position the census did not cover):

- `iterator.vl` `impl Enumerated<..> with Iterator<(i32, T)>` → `(usize, T)` — an impl's
  TRAIT ARGUMENT, which the census's SIG/FIELD walk does not see.
- `json.vl` `begin_list`'s answer `elements.len().as_i32()` (WIRE, the arm is multi-line).
- `compare.vl` `index_of`'s counter, `markdown.vl`'s three `mut close: Option<i32>`,
  `document.vl`'s `List<(i32, str)>` insertions — annotated LOCALS (census kind LET,
  never classified).
- `document.vl` `skip_raw_text` and `index_of`: the dead `if from < 0 { 0 } else { from }`
  clamps removed (the rpc.vl:4641 shape §6 warns about), and `text.len() - needle.len()`
  guarded — it underflows when the needle is longer.
- `reactive.vl` `ReconcilePlan.removed` built as `List<usize>`; `ui.vl`
  `rows[index.as_usize()]` — `RowStep`'s payload stays `i32` until S4.
- corpus: `adapt.vl`, `capture-clones.vl` (four sites back into their functions' `i32`
  world: `cells.len().as_i32() + weight`), `reconcile-index.vl` (its copy of `reconcile`'s
  `removed`).

## What the codemod does NOT do, on purpose

- It never converts at a span that is not a whole, single-line expression on token
  boundaries (a closure's return mismatch anchors at the closing brace; a macro-world
  echo can index into GENERATED text and land mid-name — both were seen, both are
  declined).
- It fixes a `macro fun` body only where the re-reported span really sits inside one;
  other `in this macro:` reports are echoes and are counted, not edited.
- It declares a counter `usize` instead of converting at its uses only when the counter
  is a bare `let`/`mut` of an unsuffixed integer literal in the same function, and a file
  with such declarations takes ONLY them in that round (declaration-first keeps the diff
  free of `.as_usize()` on values that end up `usize` anyway).
- It leaves the review cost visible: `markdown.vl` (29 edits), `delta.vl` (24),
  `browser/ui.vl` (22) are the three files the S2 lane should read line by line; every
  edit is in `out/fix-codemod.tsv`.

## Not in the 105 — for Order 42 to decide, not to discover

- **macro_std** (`vilan/macro_std/src/meta.vl`, `build.vl`): `Arguments::len(): i32`,
  `get(index: i32)`, `indent(tabs: i32)` — index-kind, never censused. The codemod
  converts at them (6 edits); respelling them is a macro-surface change.
- **Enum payloads** the census could not see: `RowStep::Keep(i32)`/`Refresh(i32)`,
  `Delta::Insert(K, T, i32)` — S4's (A112's `// I5` markers), converted at here.
- **A112's newer positions** in `delta.vl`/`reactive.vl` (after the census's base):
  converted at, not respelled.

## kolt — for the owner, with S2, not before (checked on a scratch COPY, never in place)

kolt's own errors before S2 are A125's four (`Theme`/`Command` want `Hashable`). Under
the migrated std, **five files** meet S2 — the paper's census counted three namings;
inference carries kolt's code, so the sites are where a `len()` or a std index meets
kolt's own `i32`:

1. **`src/lib/rotary.vl:53–57` — first, and it needs thought.** `focus(key, offset)`:
   `(key + offset) % nodes.len()` with `nodes: Map<i32, Element>` — `Map::len()` answers
   `usize` after S2. The arithmetic is signed on purpose (`offset` is `-1`/`+1`, and the
   `index < 0` wrap), so the fix is ONE conversion into the signed world,
   `let count = nodes.len().as_i32();`, and the body keeps its `i32`s (`nodes` is keyed
   by `i32`, so `nodes.get(index)` is unaffected). Respelling `key` as `usize` would put
   the wrap in unsigned arithmetic, which is wrong.
2. `src/command_palette.vl:182–232` and `src/theme.vl:125–200` — the same selection
   pattern twice: `selected_index = Signal::new(0)` (an `i32`), `filtered.get(selected)`,
   `x >= list.len() - 1` and `if x <= 0 { list.len() - 1 }`. **`len() - 1` underflows on
   an empty list** (`-1` on JS, a native panic) — today it is `-1` by type. Either make
   the index `usize` and guard the empty list, or keep it `i32` and convert `len()` once.
   (`command_palette.vl` is the owner's untracked file.)
3. `src/lib/search.vl:7,14,24,44` — `table: SignalCell<List<(i32, str)>>` is
   `enumerate()`'s tuple written out: it becomes `(usize, str)`; `List<(i32, str)>::new()`
   and `Set<i32>` beside it follow.
4. `src/server.vl:84` — `for i in Range::new(0, 8) { hash.code_at(i) }`: `code_at` takes a
   `usize` index; `Range` yields `i32` → `code_at(i.as_usize())`, or a `usize` range.

## Finds met while preparing (not fixed here)

- **F1 — B389 gap: a literal argument to a generic constructor inside a struct literal's
  field is not typed from the field.** `import std::shared::Shared; struct S { count:
  Shared<u53> } fun main() { let s = S { count = Shared::new(0) }; }` →
  `Expected Shared<u53>, but got Shared<i32> instead.` (std's `rpc.vl` `RemoteSource` and
  `KeyedSource` meet it at `usize`; `b389-gap-literals.patch` is the two suffixes.)
- **F2 — a negative literal is accepted at an unsigned type.** `let n: usize = -1;`,
  `let m: u53 = -1;` and `let k: u8 = -1;` compile and print `-1`: the literal range
  check does not see the unary minus. Combined with B389's bare-`let` law this is what
  lets every `-1` sentinel compile silently as a `usize` after S2.
- **F3 — `as_usize`/`as_u53` of a negative value differs by backend.** `(-5i8).as_usize()`
  is `-5` on JS (the conversion truncates, it does not fold) and `0` natively (Rust's
  saturating `f64 as usize`). `u53` has had this since its introduction; `usize` mirrors
  `u53` on purpose (ruling 1) — which answer is right (fold into [0, 2^53], saturate, or
  "unspecified like underflow") is a ruling, not a lane's choice.
