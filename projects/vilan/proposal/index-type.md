# One spelling for an index — `usize` (I5)

Tracker I5. Written by lane papers-40 of Order 40, on vilan `next` @49de3915
(`vilan 0.40.0 (49de39157)`). The owner ruled the design on 2026-09-21 (four
rulings) and the wire question on 2026-09-22; this paper does not reopen any of
them. What it owes is the EVIDENCE: the exact census, by parse; the proof that
the wire does not move; and the slices, sized.

**Every claim below about what the compiler does today is a probe that was
run**, named inline and kept under
`scripts/integration/sweeps/order40/papers-40/probes/`. Nothing here is derived
from reading the compiler alone.

Related: `proposal/numeric-types.md` (the sized family and its literal rules),
B370 (CLOSED Order 39 — literal inference as a general law, whose remaining
gaps §4 measures), A101 (the `css` codemod, the migration precedent),
A108 (Wire receivers — the other breaking item in the same train),
A112 (`incremental-collections.md` §13, whose `Splice(at, ..)` is to be BORN
`usize`), `proposal/transport-rpc.md` §8 (the `Patch`/`Delta` frames §6 proves).

Probes (all re-runnable; each takes the worktree and a scratch directory):

| probe | what it establishes |
| --- | --- |
| `i5_census.rs` | the census, by parse — a `vilan-core` example over the estate |
| `i5_classify.py` | the index-kind verdict for every std integer position |
| `i5_wire_flip.sh` + `i5_wire_patch.vl` | §6 — a real `Patch` frame, three standard libraries, byte-compared |
| `i5_contract_hash.sh` + `i5_contract_hash.vl` | §7 — what moves a service's contract hash |
| `i5_literal_positions.sh` | §4 — the 21 literal positions, pass/fail |

Census outputs, checked in beside this paper:
`sweeps/order40/papers-40/i5-std-index-sites.tsv` (every std integer position
with its verdict and the reason), `i5-estate-index-namings.tsv`,
`i5-sentinels-and-loops.tsv`.

---

## 1. What is settled, and what this paper adds

The owner's rulings, restated so the build has one place to read them:

1. **`usize` is a DISTINCT numeric type**, not an alias — `u53` on the JS
   targets unless revisited, the platform word natively.
2. **An underflowing `usize` subtraction is UNSPECIFIED, never memory-unsafe.**
   No check is emitted. On JS the value simply leaves the type's range; natively
   Rust's own rule applies (panic in debug, wrap in release). Every backend's
   existing bounds check still stands between an out-of-range index and memory.
3. **Literal inference is a GENERAL LAW**, not an exception for `usize`: an
   unsuffixed literal takes its type from context everywhere.
4. Everything else as I5 proposed: what counts as an index and what does not;
   the codemod, the naming diagnostic and the quick fix; A112's `Splice(at, ..)`
   born `usize`; **no `isize`** — a signed offset is `i53`; and the timing, in
   the breaking train BEFORE the held v0.41.0 cut.
5. (2026-09-22) **A length or position crossing rpc KEEPS its wire width**:
   frames byte-identical, the contract hash does not move.

What this paper adds: §3 the census; §4 the measurement that ruling 3 is not
yet delivered in five positions, which is what S1 is; §5 the underflow rule
measured on both backends; §6 the wire proof, and the rule it forces on
`usize`'s own `Wire` impl; §7 the one sentence ruling 5 needs qualifying with;
§8 the migration; §9 the slices; §11 the open questions.

**The item's premise held, with one correction.** I5 says std spells index
positions "as `i32` almost everywhere (~100 signature sites) and as `i53` in a
dozen more". By parse: **105 index-kind positions, and every one of them is
spelled `i32`** (87 bare, 18 inside a wrapper such as `Option<i32>` or
`List<i32>`). The `i53` positions the item was thinking of are `fs.vl`'s file
offsets — seven of the ten STREAM positions in §2.2 — which this paper argues
are a different kind and should NOT become `usize` (§11 Q1).

---

## 2. What an index is

### 2.1 The rule

A position is **index-kind** when its value is

- a POSITION into a sequence (a list, a string, a byte buffer, a storage area),
- a LENGTH, COUNT or CAPACITY of one, or
- the ANSWER of a search for a position.

It is not index-kind when the value is an identity (a channel, a connection, a
subscriber, a request), an element VALUE (a byte, a character code, a colour
channel, a database column), a duration, a port, a status code, or an operand of
the numeric family's own algebra.

This is the rule the classifier applies, site by site, in
`i5_classify.py`; its name rules are in the open and every site the name rule
would get wrong carries a hand-written override with its reason. The output is
the checked-in verdict table, auditable row by row.

### 2.2 Three kinds that are NOT `usize`, and why each is separate

The census made three boundaries visible that I5's text did not name. Each one
is where an index meets a non-index integer, and each one is where the migration
will need an explicit conversion.

**WIRE (61 positions).** The `Serialize`/`Deserialize` seam —
`begin_list(length: i32)`, `begin_struct(fields: i32)`,
`begin_variant(name, arity: i32)`, `i32_value`/`i53_value`, and the closure
fields of `Serializer`/`Deserializer` that carry them. These integers are what
the CODEC writes. Keeping them `i32` is not a convenience: it is what makes
ruling 5 true, and §6 measures the four bytes per position that go astray when
it is not respected.

**STREAM (10 positions).** `fs.vl`'s file offsets and lengths: `read_at`,
`write_at`, `raw_read`/`raw_write`'s `position`, `seek`, `Reader.cursor`,
`truncate(length)`, `Stat.size`. A file offset is a position in a byte stream
that is not in memory, and its range is a property of the filesystem, not of the
address space. Seven of them are already `i53` for exactly that reason.
Recommendation in §11 (Q1): **leave them `i53`**.

**SEQUENCE (5 positions).** `delta.vl`'s log sequence numbers — `DeltaCursor.at`,
`DeltaLog.version`, `DeltaLog.base`, `at()`, `oldest()`. A sequence number is
monotonic and never indexes anything; `DeltaLog.limit` beside it IS a length and
IS index-kind. They are five lines apart in one file, which is exactly why the
rule has to be about meaning rather than about the module.

### 2.3 The type's family in `number.vl`

`usize` is declared the way every sized integer is
(`vilan/std/src/number.vl:744-810`): `export external struct usize;` beside
`i53`/`u53`, with a `label_usize` extern (`[extern("Number")]`, the identity at
the JS level) and the `fold_unsigned` conversion shape the family already has.

What the family owes it, read off `u53`'s own impls (six files):

| file | impls `usize` needs |
| --- | --- |
| `number.vl` | `Eq`, `PartialEq`, `PartialOrd`, `Ord`, `Default`, `Add`, `Sub`, `Mul`, `Div`, and the inherent block (`max_value`, `min_value`, `min`, `max`, `pow`, `rem`) |
| `number.vl` | `as_usize` on every other numeric type (11 of them), and `usize`'s own `as_i8 … as_f64` |
| `hash.vl` | `Hashable` |
| `json.vl` | `Json`, `FromJson` |
| `debug.vl` | `Debug` |
| `wire.vl` | `Wire` — **at `i32`'s width**, see §6 |
| `display.vl` | `Display` — **which `u53` does NOT have today** (`display.vl` impls `str`, `i32`, `f64`, `bool`, `u32`, `BigInt` and nothing else; interpolation of a `u53` works through the compiler's own path, but a `T: Display` bound refuses it — measured). `usize` should have one: an index in an error message is universal. See find F-f. |

On the compiler side the type is named in six source files and two gates:
`type_.rs`'s three tables (`SCALAR_PRIMITIVE_NAMES`, `NUMERIC_PRIMITIVE_NAMES`,
`NUMERIC_SUFFIXES`), `analyzer.rs` (13 mentions of `u53` is the measure),
`transformer.rs`, `bindgen.rs`, `vilan-rust/src/lib.rs`'s scalar map
(`"usize" => "usize"`, the one line that makes the native backend's casts
disappear), `vilan-rt`, plus `grammar_sync.rs` and the book's
`theme/vilan.js` number regex. Eleven doc pages name the family
(`spec/types.md`, `spec/lexical.md`, `spec/appendix.md`, `std/numbers.md`,
`tour/values-and-types.md`, `guide/native.md`, `guide/services.md`,
`std/encoding.md`, `appendix/glossary.md`, `appendix/errors.md`, the theme).

**The suffix.** `42usize` follows from `NUMERIC_SUFFIXES`. It should exist and
should be almost never needed — if the migration leaves suffixes behind in
ordinary code, §4 has not been finished.

---

## 3. The census, by parse

`i5_census.rs` is a `vilan-core` example: it parses every `.vl` file with the
compiler's own `parsing::parse`, walks the tree with `Node::for_each_child` (the
exhaustive visitor), and reports one row per finding with the type text taken as
the SOURCE SLICE of the annotation's span. It also reads the fenced `vilan`
blocks out of `vilan/docs` (507 fences; 153 report parse errors, all of them
signature-listing fences with bodyless declarations — rows are still collected
from what parsed) and the `.vl` program CONSTS inside Rust test files, which a
`.vl`-file sweep cannot see.

### 3.1 std — 105 index-kind positions, all spelled `i32`

86 signature positions and 19 struct fields. By module:

| module | positions | module | positions |
| --- | --- | --- | --- |
| `document.vl` | 19 | `storage.vl` | 3 |
| `bytes.vl` | 15 | `list.vl` | 3 |
| `markdown.vl` | 10 | `delta.vl` | 3 |
| `rpc.vl` | 9 | `arena.vl` | 3 |
| `fs.vl` | 9 | `style.vl` | 1 |
| `iterator.vl` | 7 | `set.vl` | 1 |
| `string.vl` | 5 | `reactive.vl` | 1 |
| `option.vl` | 5 | `native_map.vl` | 1 |
| `binary.vl` | 5 | `memo.vl` | 1 |
| `json.vl` | 1 | `map.vl` | 1 |
| `crypto.vl` | 1 | `compare.vl` | 1 |

Written forms: 87 bare `i32`, 8 `Option<i32>` (every `index_of`), 3 `List<i32>`,
2 `Shared<Map<Hash, i32>>` (`KeyedCell`/`KeyedSource`'s `positions`), 2
`Shared<i32>`, and one each of `Option<(i32, T)>`, `(List<(str, str)>, i32)` and
`List<(i32, str)>`.

Against the same 856 std signature positions with a numeric type, the other
verdicts are: 410 NOT index-kind, 61 WIRE, 10 STREAM, 5 SEQUENCE. The 410
include the whole of `number.vl` (the family's own algebra), every channel and
connection id in `rpc.vl`, every duration, every colour channel and every
character code.

Two shapes worth calling out because the migration will meet them:

- `Bytes` is the sharpest test of the rule: `get(index: i32): i32` migrates its
  INDEX and keeps its ANSWER (a byte value). 15 index-kind positions in
  `bytes.vl`, and the byte values beside them stay `i32`.
- `Iterator`'s `Enumerated` answers `(i32, T)` and is declared
  `impl Enumerated<..> with Iterator<(i32, T)>`. That tuple is the one std type
  whose migration is visible in every `enumerate()` caller's type.

### 3.2 The estate — 251 explicit namings, in 56 files

Positions outside std that write an index-kind type by name (same name rule,
integer types only):

| area | namings | files |
| --- | --- | --- |
| `vilan/test` + `examples` + `benchmarks` + `macro_std` | 33 | 18 |
| `vilan/docs` fences | 8 | 5 |
| `.vl` consts inside Rust tests | 207 | 30 |
| kolt | 3 | 3 |
| vilan-website (30 `.vl`) + vilan-playground (6) | **0** | 0 |

**The `.vl` consts inside the Rust tests are the estate's real bulk** — 207 of
the 251, across 30 files, with `crates/vilan-core/tests/inference/` holding most
of them. They are the surface a `.vl`-file sweep cannot see and the surface a
text codemod cannot safely rewrite (they live inside `r#"…"#` literals).

**kolt names three**, and the item's guess was right about the rest: kolt writes
84 integer-typed positions and 81 of them are IDENTITIES (`id`, `channel_id`,
`task_id`, `message_id`, `workspace_id`, `next_id`) or crypto parameters.
Inference carries the rest of the application across untouched. The three are

- `lib/search.vl:7` — `table: SignalCell<List<(i32, str)>>`, which is
  `enumerate()`'s tuple written out: it becomes `List<(usize, str)>`.
- `lib/rotary.vl:53` — `fun focus(self, key: i32, offset: i32)`, called
  `self.focus(key, -1)` and `self.focus(key, 1)` (rotary.vl:29 and :41). This is
  the estate's best example of ruling 4's "a signed offset is `i53`": `key`
  becomes `usize`, `offset` stays signed, and the body's
  `(key + offset) % nodes.len()` with its `if index < 0 { nodes.len() + index }`
  wrap has to be written in the signed world and converted once at the end.

### 3.3 `.len()` and `[]` — what does NOT need a codemod

| area | `.len()` calls | `[]` subscripts |
| --- | --- | --- |
| std | 231 | 136 |
| corpus + examples + benchmarks | 117 | 93 |
| docs fences | 50 | 28 |
| `.vl` consts in Rust tests | 699 | 375 |
| kolt | 28 | 11 |
| website + playground | 12 | 6 |
| **total** | **1,137** | **649** |

These 1,786 sites are the reason the migration is survivable: under a CONSISTENT
migration not one of them changes. `len()` answers `usize`, the subscript takes
`usize`, and the text stays as it is. §5.3 measures that the emitted JavaScript
is byte-identical too.

### 3.4 `-1` sentinels — 125 literals, 7 of them index sentinels

The `-1` census is 125 literals estate-wide, and reading each one in context is
the whole point of doing it by parse: most are Option defaults over VALUES
(`numbers.get(a).unwrap_or(-1)` in `vilan/test/arena.vl`, where the arena holds
`i32` values) and are untouched.

The seven that die:

| site | shape |
| --- | --- |
| `std/src/reactive.vl:1699,1725,1734` | `reconcile`'s index chain — `next_same.push(-1)`, `None => -1`, `mut candidate = -1` |
| `std/src/browser/ui.vl:1282` | `mut highest = -1` in `settled_steps` |
| `std/src/process/db.vl:331` | `mut last_applied = -1` in `refuse_inserted_migration` |
| `vilan/test/list-search.vl:10,15` | `xs.index_of(20).unwrap_or(-1)` — the corpus's two |

`std::reactive`'s `reconcile` is worth the owner's attention: it is a
`-1`-terminated linked list of positions (`first`, `next_same`, `head`,
`candidate`) walked by `for head >= 0`, and it is the function A125 is changing
in this same order. §9 puts it in S2 and not earlier.

### 3.5 Downward loops — 24 decrements, 8 of them unsafe

24 `x -= …` sites estate-wide: 16 in std, 3 in docs fences, 5 in Rust-test
consts, **none in the corpus, in kolt, or on the websites**.

Of std's loop guards, 13 are written `for x > 0 { … x -= 1 }` — the style
ruling 2 prescribes, which never reaches the edge. **Eight are written
`for x >= 0 { … x -= 1 }`**, and every one of them breaks under an unsigned
index (the guard becomes always-true and the decrement at zero underflows):

```
std/src/browser/ui.vl:1307   settled_steps
std/src/browser/ui.vl:1347   row_references
std/src/json.vl:636          begin_list
std/src/json.vl:685          begin_variant
std/src/list.vl:81           reverse
std/src/reactive.vl:1702     reconcile
std/src/reactive.vl:1727     reconcile
std/src/reactive.vl:1736     reconcile
```

Eight sites is a hand edit, not a codemod — and eight is a number worth knowing
before the lane starts, because a codemod that silently rewrote them would
produce an infinite loop rather than a diagnostic.

---

## 4. Literal inference under B370 — the law, and the five positions that do not have it yet

Ruling 3 makes literal inference a general law, and I5's S1 depends on it: if an
unsuffixed `0` does not take `usize` from its context, every `list[0]`,
`take(3)` and `let n = 0` in the estate needs a suffix, and the migration stops
being survivable.

`i5_literal_positions.sh` writes 21 one-case files and checks each on its own,
using `u53` — what `usize` IS on the JS targets under ruling 1 — as the
stand-in. **14 pass, 7 fail.** Five of the seven are literal-inference failures
and are S1's work; the other two (`xs.get(i)`, `let n: u53 = xs.len()`) fail
because there is no `usize` yet and std's signatures are `i32` — they are the
migration's conversion boundary, and they are in the table so the two kinds of
failure are not confused:

| position | verdict |
| --- | --- |
| a call argument `take(3)` | PASS |
| an annotated `let n: u53 = 0` | PASS |
| the RIGHT operand `n + 1` | PASS |
| a struct field `Holder { at = 0 }` | PASS |
| a return `fun zero(): u53 { 0 }` | PASS |
| a comparison `n > 0` | PASS |
| a compound assignment `n -= 1` | PASS |
| a tuple element `(u53, str) = (0, "a")` | PASS |
| a closure parameter `\|n: u53\| …` applied to `7` | PASS |
| `Some(0)` into `Option<u53>` | PASS |
| `xs[0]` and `xs[i]` with `i: u53` | PASS (but see §12's find) |
| a `for i > 0 { i -= 1 }` downward loop | PASS |
| `mut i: u53 = 0; i -= 1;` (the underflow itself) | PASS — it compiles and runs; §5 says what it does |
| **the LEFT operand `1 + n`** | **FAIL** — ``+` adds two values of the same type, but the operands are `i32` and `u53`` |
| **the elements of an annotated list literal `let xs: List<u53> = [0, 1, 2]`** | **FAIL** — `Expected List<u53>, but got List<i32> instead.` |
| **a literal match pattern `match n { 0 => … }`** | **FAIL** — `literal pattern of type i32 cannot match type u53` |
| **through a generic call `let n: u53 = identity(5)`** | **FAIL** — `Expected u53, but got i32 instead.` |
| **a bare `let n = 0` used later at `u53`** | **FAIL** — `Expected u53, but got i32 instead.` |
| `xs.get(i)` with `i: u53` | FAIL — `Expected i32, but got u53 instead.` (the boundary, not the law) |
| `let n: u53 = xs.len()` | FAIL — `Expected u53, but got i32 instead.` (the boundary) |

The same five fail for `i53`, `u32` and `f64` and all five PASS for `i32`: the
literal is not typed from context in these positions at all — it defaults to
`i32` and then has to match.

**The first two are B370's own two gaps, and they are still open.** B370 closed
as a MISCOMPILE fix (an expression of literals in a typed position took its
operator from the default width — `rem(4 / 16)` printing `0`); it did not
deliver the inference law the same ruling states. I5's S1 owes all five, and
they are the S1 work: the type is the cheap half.

The last one is the one that decides how much of the estate moves. A bare
`let n = 0;` later used as an index is today an `i32` binding; under the law it
takes `usize` from its use. Without it, `vilan/test`'s and kolt's untouched
files stop being untouched.

---

## 5. Underflow, as ruled, measured

### 5.1 On the two backends

`mut n: u53 = 3; for four rounds { n = n - 1; print(n) }`:

```
JS      n = 2   n = 1   n = 0   n = -1      (and keeps running)
native  n = 2   n = 1   n = 0   attempt to subtract with overflow   (debug panic)
```

Exactly what ruling 2 says: unspecified, backend-defined, and never quiet about
memory. Written down for the book:

- **On JS** the value leaves the type's range and becomes negative. Nothing
  traps. `0u53 - 1u53` prints `-1`.
- **Natively** Rust's rule applies: a panic in a debug build, a wrap in a release
  build. A CONSTANT underflow does not even compile — rustc's
  `deny(arithmetic_overflow)` refuses `0_u64 - 1_u64` at compile time.

### 5.2 The native differential cannot cover an underflowing program

This is not a caution, it is measured: the same program prints `-1` on one
backend and panics on the other. `native_differential` compares outputs, so an
underflowing program is legitimately outside its reach. The book states the
rule; the differential's corpus must not contain one.

There is a second consequence the paper owes the native lane. Today the CLI
reports a rustc refusal as `cargo build refused the emitted Rust. That is a
BACKEND defect, not a defect in the vilan program`. Under ruling 2 that sentence
becomes a false accusation for the one class of programs the ruling calls
unspecified. §11 Q4.

### 5.3 The bounds check is what makes "never memory-unsafe" true

Every list subscript emits `__at`:

```js
function __at(list, index) {
	if (index >= 0 && index < list.length) return list[index];
	throw "index out of bounds: the length is " + list.length + " but the index is " + index;
}
```

The `index >= 0` half looks dead once indexes are unsigned. **It is not, and it
must stay**: an underflowed `usize` on JS is exactly the negative number that
half exists to catch. Measured — a `u53` index decremented past zero and used:

```
index is -1
index out of bounds: the length is 2 but the index is -1
```

That is the whole of ruling 2's safety claim, working today, with no new code.

### 5.4 The JS emission does not change

Two programs, one written with `i32` throughout and one with `u53` throughout
(no conversions in either), compiled and diffed: **the emitted `.mjs` files are
byte-identical**. The loop, the comparison, the addition and the subscript all
emit the same text; `u53` differs from `i32` in emission only where a conversion
(`as_u53`, `as_i32`) is WRITTEN.

So the corpus goldens are a genuine measure of the migration's quality: a golden
that moves means a conversion was introduced that should not have been, or a
`Math.trunc`/`>>>` verdict changed. Claim (v) of the item holds.

`checked_sub`/`saturating_sub` are still worth having (ruling 2 says so), and
they are ordinary std functions on the family — no compiler support, no emission
change. Recommend `usize::checked_sub(self, other): Option<usize>` and
`saturating_sub(self, other): usize`, written in `number.vl` beside `diff`, in
S1.

---

## 6. The wire proof — the frames do not move

Ruling 5: a length or position that crosses rpc keeps its wire width, frames
byte-identical.

`i5_wire_flip.sh` builds a REAL `Patch` frame — `std::rpc`'s `encode_patch` over
a `List<Delta<i32, str>>`, the frame a keyed exposure sends — under both codecs,
against three standard libraries, and byte-compares the dumps. The ops are
`Insert(7, "hello", 3)`, `Update(7, "there")`, `Remove(7)`, `Reset(["a","b"])`;
the third payload of `Insert` is the POSITION under test.

**A — std as it is** (`Delta::Insert(K, T, i32)`):

```
binary  104  …496e73657274 07000000 0568656c6c6f 03000000 …
text     96  {"Patch":[5,[{"Insert":[7,"hello",3]},…]]}
```

**B — the naive migration** (`Delta::Insert(K, T, u53)`, the position's own
`Wire` impl deciding the width). This is the CONTROL, and it must move or C
proves nothing:

```
binary  108  …496e73657274 07000000 0568656c6c6f 0000000000000840 …
text     96  (unchanged)
```

Four bytes more, per position: `u53`'s `Wire` impl writes through `i53_value`,
which the binary codec spells as an eight-byte f64 bit pattern, where
`i32_value` is four bytes little-endian. The JSON codec is unmoved — a number
renders as a number — which is itself worth knowing: **a deployment on the text
codec would not notice, and a deployment on the binary codec would corrupt every
frame.**

**C — the same `u53` position with the wire width pinned at `i32`**
(`serializer.i32_value(index.as_i32())` / `deserializer.i32_value().as_u53()`):

```
binary  104  … identical to A, byte for byte …
text     96  (unchanged)
```

`diff` A vs C is empty. The round-trip is exercised in all three runs
(`encode_binary` → `decode_binary` → the `Insert` arm read back, `7 hello 3`),
so the READ half is proved too, not only the write.

**The rule this forces, which the build must not get wrong:**

> `impl usize with Wire` describes through `serializer.i32_value(self.as_i32())`
> and rebuilds through `deserializer.i32_value().as_usize()`. It does NOT ride
> `u53`'s impl. A `usize` past `i32::MAX` on the wire is a protocol error, not a
> widening.

That is a real restriction and it should be stated as one. A wire list longer
than 2³¹ elements cannot be described; nothing in std can produce one (a JS
array cannot exceed 2³²−1 and a frame that large is not a frame), and the
alternative — widening every position by four bytes — was ruled out.

**The cascade, measured as a side-effect.** Flipping the type of ONE payload in
ONE enum produced **9 compile errors across `rpc.vl`** (at 2511, 2608, 2656,
2725, 3963 and 4637–4645). One of them is instructive:
`rpc.vl:4641` reads `if bounded < 0 { bounded = 0; }` — a clamp that becomes
dead code under an unsigned type and WRONG under ruling 2, because the value it
was clamping can now arrive already wrapped. The codemod cannot see that; a
human has to.

---

## 7. The contract hash — where ruling 5 needs one more sentence

`std::rpc` builds the hashed surface string from `parameter.type_.render()`
(`vilan/std/src/rpc.vl:5327` for a method, `:5378` for a `client = H` handler;
`service_hash` at `:4880`, applied at `:5382`) — **the type AS WRITTEN**, which
is what `analyzer.rs:53303` says in so many words. So the question "does the contract hash move" has two
different answers, and the paper owes both.

`i5_contract_hash.sh` prints `Pages::contract_hash()` for a service whose rpc
method is `fun page(self, at: T): str`, respelling `T`:

| written type | hash |
| --- | --- |
| `i32` | `be3fd1fe` |
| `u53` | `5b458905` |
| `i53` | `a7d0d499` |
| `u32` | `c8e7a262` |
| `i16` | `fa24f7f8` |

And for a position INSIDE a std frame type, with the same service:

| std | hash |
| --- | --- |
| as it is | `be3fd1fe` |
| `Delta::Insert`'s index respelled `u53` | `be3fd1fe` |

So:

1. **Ruling 5 holds exactly as ruled for std's frame types.** `Patch`, `Delta`
   and `KeyedCell.positions` are not named in any contract surface — the surface
   carries method signatures and each `[expose]`d field's ELEMENT type — so
   changing a position inside them moves no hash. Which is also why §6's rule is
   load-bearing: **the hash cannot catch a std frame-width change** (it did not
   move while the bytes moved by four per position). Nothing but the discipline
   in §6 protects a mixed-version deployment.

2. **A user's own rpc signature is a different matter.** `[rpc] fun page(at: i32)`
   rewritten to `at: usize` moves THAT service's hash, by construction. The
   consequence to state in the migration guide: a service and its clients
   migrate together, in the same release, as they already must for any signature
   change. Recommended wording for the book: "changing an rpc parameter's
   written type moves the contract hash — including a change from `i32` to
   `usize`, even though the bytes on the wire are the same. Rebuild both halves."

   The alternative — rendering `usize` in the surface as its wire spelling so a
   migrated server still accepts a pre-migration client — is NOT recommended
   (§11 Q2): it would hash `page(i32)` and `page(usize)` the same, and the two
   disagree about whether a negative is meaningful, which is precisely the kind
   of disagreement the hash exists to refuse.

---

## 8. The migration

### 8.1 The codemod is not A101's codemod

A101's precedent is a 665-line text rewriter
(`sweeps/order37/tools/css_call_codemod.py`) that touched 227 blocks with no
golden moved. **I5's codemod cannot be that**, for two reasons the census makes
concrete:

- The sites that need changing are decided by TYPE, not by text. `fun f(at: i32)`
  may be an index or a task id — kolt's 84 integer positions divide 3 to 81 on
  exactly that question — and a bare `let n = 0` has no annotation to rewrite at
  all.
- 207 of the estate's 251 namings live inside `r#"…"#` literals in Rust test
  files, where a text pass has to re-encode what it rewrites (A101's codemod has
  a whole section for that) and where a wrong rewrite fails as a test, not as a
  build.

**Recommended shape: a fixed-point loop over the compiler's own diagnostics.**

1. The compiler gains the naming diagnostic (§8.2) with a machine-readable fix.
2. A driver runs `vilan check` over a package, applies every fix the diagnostics
   carry, and repeats until the diagnostic count stops falling.
3. What is left is what needs a human: the sentinels (§3.4, seven sites), the
   downward loops (§3.5, eight sites) and the signed-offset arithmetic (kolt's
   `rotary.vl`). All of them are refused by name; none of them is rewritten
   silently.

This needs one CLI affordance that does not exist today: `vilan check` has no
`--fix` and no machine-readable diagnostic output. The LSP already has the
mechanism (`document.rs`'s bulk quick fix, "Write all N `css` declarations as
calls", is A101's codemod delivered as a code action), so the cheapest route is
to put the edit-producing function in `vilan-ide` and give both the CLI and the
LSP a call to it. Sized in S2.

### 8.2 The naming diagnostic

Today an index mismatch says, in full:

```
Expected u53, but got i32 instead.
```

`argument_mismatch` (`analyzer.rs:38938`) steers only for a TRAIT-typed
parameter; a numeric mismatch gets the plain sentence. The binary-operator path
already does better (ledger row 357: ``+` adds two values of the same type …
there are no implicit conversions; suffix the literal or convert with `as_*``),
and that is the shape to copy.

Recommended message, one ledger row, one `\`-continued literal:

> `Expected `usize` (a position), but got `i32`: there are no implicit
> conversions — write `…as_usize()`, or make the binding a `usize`.`

With the reverse for an index used where a value is wanted
(``…as_i32()``). The note anchors on the parameter's declaration, the way
`argument_mismatch` already does.

### 8.3 The quick fix

`Insert `.as_usize()`` / `Insert `.as_i32()`` at the offending expression, plus
the file-wide `Convert all N indexes in this file` built on the same bulk
mechanism as the `css` action. The LSP's code-action titles are gated by
`book_sync`, so the titles land in the book's editor page in the same change.

---

## 9. The slices

**S1 — the type, the family, the literal law. (M–L, no std signature moved.)**

- `usize` in `type_.rs`'s three tables, `analyzer.rs`, `transformer.rs`,
  `bindgen.rs`, `vilan-rust`'s scalar map, `vilan-rt`; `grammar_sync` and the
  book theme.
- `number.vl`'s family (the table in §2.3), including `as_usize` on the eleven
  other numeric types and `checked_sub`/`saturating_sub`.
- `impl usize with Wire` at **`i32`'s width** (§6), `Hashable`, `Json`/`FromJson`,
  `Debug`, `Display`.
- **The five literal positions of §4.** This is the majority of S1's risk and it
  is compiler work in the solver, not in the numeric family. It is also work the
  whole language wants independently of I5 — every one of the five fails for
  `i53`, `u32` and `f64` today.
- The book: the family's pages, and the underflow rule stated where `u53`'s
  range rule is stated.
- Pins: the 21 positions of `i5_literal_positions.sh` as a corpus program; a
  `usize` round-trip through both codecs byte-compared against `i32`'s
  (§6's probe, as a test); an underflowing program pinned OUT of the native
  differential by name.

S1 moves no std signature, so it is mergeable on its own and breaks nothing.

**S2 — the std signatures, the codemod, the estate. ONE breaking commit, merged
last in its order. (L.)**

- The 105 positions of §3.1, with the WIRE/STREAM/SEQUENCE boundaries of §2.2
  left alone — 76 positions across those three kinds — and an explicit
  conversion written wherever one of them meets an index.
- The seven sentinels and the eight `>= 0` loops, by hand, each one named in the
  commit message.
- The naming diagnostic and the quick fix (§8.2, §8.3), and the fix-producing
  function shared with the CLI.
- The estate: 251 namings in 56 files, of which 207 are inside Rust test
  consts; the goldens are the measure (§5.4 says none should move).
- kolt's three sites are the owner's, and `rotary.vl` is the one that needs
  thought rather than a rewrite.

**S3 — the native backend drops its casts. (S.)** `vilan-rust` emits
`((xs).len() as i32)` at every length today; with `usize` mapping to Rust's
`usize` the cast disappears. Measurable: the emitted `main.rs` for the
copy-elision census, before and after.

**S4 — the positions that were not born `usize`. (S–M.)** A112's `ListCell` and
`map_each` were written `i32` with a `// I5` marker at each position
(collections-40's own note); `Splice(at, ..)` is ruled to be born `usize` and
is not built yet; `std::ui`'s row positions; `KeyedCell.positions`. If A112 S2
lands before S2 of this item, S4 is where its markers are cleared.

---

## 10. The cut

The v0.41.0 cut is HELD and already carries A101 and A108. **S2 is the breaking
train and the cut waits for it**, per ruling 4.

S1 is not breaking and can land in any order. S2 cannot start before S1, and S1
cannot finish before §4's five literal positions are closed — so the dependency
chain the cut actually waits on is

```
§4's five positions  →  S1  →  S2  →  the cut
```

Order 41 can hold S1 and, if S1 lands early in it, S2 in the same order; the
paper's own recommendation is that **S1 and S2 are separate orders**, because S2
is one breaking commit over 56 files and wants a clean base and a full estate
re-sweep at its merge, which is not something to do in the same order that moved
the solver underneath it.

---

## 11. Open questions, with a recommendation each

**Q1 — do file offsets become `usize`?** `fs.vl`'s nine STREAM positions are
positions in a byte stream that is not in memory. `usize` is the platform word
natively, so on a 32-bit target it is 32 bits, and a file larger than 4 GiB
would not be addressable — while the JS range guarantee (2⁵³) would say it is.
That is the one place ruling 1's "the range guarantee is the JS one" and the
native representation genuinely disagree.
**Rec: leave them `i53`** (seven already are), and say in the book that a stream
offset is not an index. It costs one conversion where a file read fills a buffer
— and that conversion is honest, because the two ranges really are different.

**Q2 — does `usize` render as itself in a contract surface?** §7 measured that
respelling an rpc parameter moves the hash.
**Rec: let it move.** Rendering `usize` as `u53` in the surface would let a
pre-migration client connect to a migrated server, and the two disagree about
negatives. The migration guide says: rebuild both halves.

**Q3 — `usize::MAX`?** `u53::max_value()` is `9007199254740992`. Natively
`usize::MAX` is `2^64-1`, and a program that prints it would differ by backend —
another shape the native differential cannot hold.
**Rec: `usize::max_value()` answers the JS guarantee (2⁵³) on every backend**,
the way R6 of Order 37 settled `i53`/`u53`, so the value is portable; a program
wanting the platform's real ceiling is asking a native question and should ask it
natively.

**Q4 — the native backend's refusal wording.** rustc refuses a constant
underflow at compile time and the CLI reports it as a BACKEND defect.
**Rec: the native backend recognises `arithmetic_overflow` in rustc's output and
reports it as the program's own unspecified subtraction**, naming the vilan
source span, with the book's underflow rule quoted. Small, and it belongs with
S3.

**Q5 — is the `usize` suffix (`42usize`) worth having?** It follows from the
family's tables at no cost.
**Rec: yes, and treat its appearance in ordinary code as a bug report against
§4.**

---

## 12. Finds — bugs met while measuring, not fixed here

**F-a (HIGH, MISCOMPILE) — a list subscript does not type-check its index.**
`vilan check` accepts an index of ANY type, and a wrong one produces
`undefined` in a typed binding:

```vilan
fun main() {
	let xs: List<str> = ["a", "b"];
	let at: f64 = 1.5;
	let found: str = xs[at];      // `vilan check` → no errors
	print(i"len={found.len()}");  // TypeError: Cannot read properties of undefined
}
```

`xs["a"]`, `xs[true]` and the WRITE form `xs[k] = v` with a `str` key are all
accepted too. The emitted `__at(xs, at)` passes the bounds check (`1.5 >= 0 &&
1.5 < 2`) and reads `xs[1.5]`, which is `undefined`. The native backend refuses
the same program with an unrelated rustc error, so the differential would not
have caught it either. **This is I5's business as well as a bug**: S1 must type
the subscript's index at `usize`, and there is nothing to migrate because the
position is unchecked today.
Repro: the four lines above, `vilan check` then `vilan run`.

**F-b (native backend) — an assignment's right-hand side is emitted at the
default width.** `mut i: T = 5; i -= 1;` emits `(i_N - (1i32))` for every
non-`i32` integer type and the Rust build fails:

```
vilan run --backend rust  with  fun main() { mut i: u53 = 5; i -= 1; print(i"{i}"); }
  → error[E0308]: mismatched types … expected `u64`, found `i32`
```

`i = i - 1` fails the same way; `let j = i + 1` (a binding, not an assignment)
is fine, and JS is fine in both. Measured for `i53`, `u32`, `u53` and `u8`.
It is the same class as B370 — a literal taking the default width instead of the
context's — and it BLOCKS I5 natively: every downward loop over a `usize` would
refuse to build.

**F-c (inference) — the five positions of §4**, which B370's ruling covers and
B370's fix did not deliver. Whether that is a re-open of B370 or a new item is
the integrator's call; the paper recommends a NEW item, since B370's closed text
is specifically about emission verdicts and this is about typing.

**F-d (diagnostic) — `Expected u53, but got i32 instead.` carries no steer**,
while the binary-operator path (ledger 357) does. §8.2 is the fix and it is
S2's.

**F-f (std surface) — the sized numeric family has no `Display`.**
`std::display` implements `Display` for `str`, `i32`, `f64`, `bool`, `u32` and
`BigInt` only, so a `fun show<T: Display>(v: T)` refuses a `u53`
(`'u53' does not implement trait 'Display', required by a generic bound of this
call`) while `print(i"{n}")` on the same value works — interpolation does not go
through the trait. Not I5's to fix, but I5 must not inherit it: `usize` gets a
`Display` impl in S1, and the family's gap is worth an item of its own.
Repro: `fun show<T: Display>(v: T): str { v.to_string() }` called with a `u53`.

**F-e (minor) — the bounds message prints a negative index as `-1`**
(`index out of bounds: the length is 2 but the index is -1`) for a `usize`. That
is honest and should stay; it is noted only so nobody "fixes" it into printing
the wrapped magnitude, which would hide ruling 2's whole point.
