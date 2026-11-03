# `SqlValue`: typing `std::db`'s bind lists (M175)

- status: PAPER 2026-11-03 (lane papers-56, Order 56; owner questions open; not built)
- item: M175 — `List<any>` lets a struct, a list or a tuple through to a run-time
  refusal (JS) or a rustc error (native); M165's typed half (R-c)
- lineage: M165 (the boundary half, archive.md:2658), F150 and A176 (what `any`
  holds), B679 (an `Option` through a generic body), `trait-objects.md` (the `dyn`
  machinery this rides)
- evidence: vilan `next` @ed9f0db9 (the integration worktree), kolt copy @0de9e2e

## 1. The problem

`Statement::run`/`all`/`first` take `parameters: List<any>`
(`vilan/std/src/db.vl:99-110`, over the externs at `:72-78`), and `any` "unifies
with every type" (`vilan/docs/spec/types.md:31-32`). So `.run([id, point])`
type-checks. On node the shared binder throws at the call, naming the INDEX and a
guessed JS shape, never the vilan type (`__db_bind`,
`crates/vilan-core/src/transformer.rs:1912-1928`). Natively the value reaches
`vilan_rt::Any::from(..)` (`crates/vilan-rust/src/lib.rs:6043-6061`), and `Any` has
`From` impls for the integers, the floats, `bool`, `str` and `Option` of those only
(`crates/vilan-rt/src/lib.rs:1734-1794`): a struct is rustc's E0277 (F150).

What M165 taught: (1) the conversions an `Option` and a `bool` need already exist
in `Any` and its binder (`crates/vilan-rt-sqlite/src/lib.rs:341-354`); JS needed
the analyzer to record where an `Option` LANDS at `any`
(`note_any_option_coercion`, `analyzer.rs:49336-49391`), because the JS value
carries no type. (2) That record is static, so an `Option` reaching `any` through
a generic body is missed on JS (B679). (3) `Any`'s holdable set IS the set a bind
needs — and `Bytes` is outside it: the JS binder already passes a `Uint8Array`
(`transformer.rs:1922`), while `Any` has no BLOB arm ("no `std::db` signature can
produce" one, `vilan-rt-sqlite/src/lib.rs:336-337`), so `.run([bytes])` builds on
node and fails rustc natively today.

## 2. The three shapes, in kolt

Measured in the kolt copy:

| shape | count | example |
|---|---|---|
| a literal at the call | **336** (`grep -rnoE '\.(run\|all\|first)\(\['`: store.vl 287, mcp.vl 17, tracker_import.vl 14, mcp_write.vl 10, files.vl 8; 12 of them `[]`) | `store.vl:142` `.run([id, name, address, salt, hash_password(password, salt), now_seconds()])` |
| a list built, then passed | **3** | `store.vl:1766-1773` `mut parameters: List<str> = [org]; parameters.push_many(distinct); ... .first(parameters)`; `mcp.vl:712` and `:745` pass `word_filter`'s `List<str>` (`mcp.vl:798-809`, a `push` per word) |
| a generic helper | **0** (no `List<any>`, no generic bind helper) | B679's repro: `fun collect<T>(value: T): List<any>` |

Every kolt server path runs on node (`vilan.toml:69`, no native target), so every
element an exercised path binds has passed the binder; the build lane's `check`
of kolt is the full census of element types.

## 3. The design

```vilan
/// A value SQLite stores: what a bind list holds.
export trait SqlValue {
	/// The value as the host binder takes it.
	fun sql_value(self): any;
}
impl i32 with SqlValue { fun sql_value(self): any { self } }
// ... the same one-liner for i8 u8 i16 u16 u32 i53 u53 usize f32 f64, str, bool, Bytes
impl Option<type T: SqlValue> with SqlValue {
	fun sql_value(self): any {
		match self { Some(let value) => value.sql_value(), None => sql_null() }
	}
}

export impl Statement {
	fun run(self, parameters: List<dyn SqlValue>): i32 {
		statement_run(self, parameters.map(|each| each.sql_value()))
	}
	// all / first alike
}
```

- **A literal's elements are erased at the element.** A `dyn` coercion is per
  value, where it lands, and a list literal hands each element the position
  (`types.md:1714-1719`; arms of an `if` likewise, `:1751-1752`). So the 336
  literals compile unchanged, `Some(4)` and `if c { some } else { none }`
  included (the forms `crates/vilan-cli/tests/native/db_bind_conversions.vl:22-26`
  pins today). `SqlValue` is object-safe: one receiver member, no `Self`, not
  generic (`types.md:1690-1698`).
- **The externs keep `List<any>`, private.** The map hands the host a list of
  host values: an `i32` landing at `any` is `Any::from` natively and itself on JS;
  `Option` converts in its own impl, so the M165 landing record and B679 no
  longer matter to `std::db`. `sql_null` is one extern (`null` / `Any::Null`).
  `run_guarded` (`db.vl:180`) is already internal.
- **BLOB.** `Any` gains `Blob(Bytes)`, the native `bind` writes `Value::Blob`
  and `read` keeps a BLOB as one (`vilan-rt-sqlite/src/lib.rs:362-364` reads it as
  text today); `Row::bytes(name)` reads it back on both backends.
- **The JS binder stays the host seam**, narrowed: typed code can no longer
  reach its refusal branch (`transformer.rs:1924-1925`), so it stays as the
  backstop for the internal callers.
- **Cost.** One pair per element on JS (`[value, vtable]`, `transformer.rs:6809-6810`)
  and one mapped list per call — against a statement prepare and a step, which
  is where a bind's cost is (`vilan-rt-sqlite/src/lib.rs:338-340` makes the same
  argument for its owned `Value`s).

**What a refusal reads like.**

- A literal element: `.run([id, point])` is refused at `point` by the trait
  check of the `dyn` position — "`Point` does not implement `SqlValue`". The lane
  adds a steer naming the impl set (a number, a `str`, a `bool`, `Bytes`, or an
  `Option` of one), the sentence F150 (2) wanted.
- A push: `params.push(point)` on a `List<dyn SqlValue>` — refused at the
  argument, the same check (`push` is a coercion position, `types.md:1720-1721`).
- A built concrete list: `.first(parameters)` with `parameters: List<str>` —
  "a `List<str>` does not become a `List<dyn SqlValue>` as a whole: ... rebuild it
  element by element under the object type — `let objects: List<dyn SqlValue> =
  value.map(|element| element);`" (`analyzer.rs:49113-49141`, the existing
  sentence).
- A generic helper: `fun collect<T>(value: T)` erasing `T` into `dyn SqlValue`
  is judged per instantiation, so `collect(point)` is refused at the call and
  `collect(Some(1))` binds `1` on both backends.

**User types.** A kolt `UserId { uuid }` may `impl UserId with SqlValue { fun
sql_value(self): any { self.uuid.sql_value() } }` and bind `user` instead of
`user.uuid`. A user impl that returns a struct at `any` is F150 (2)'s refusal
once that lands.

## 4. The alternatives, and why not

- **A variadic tuple**, `fun run<T: (..: SqlValue)>(self, ...parameters: T)`
  (`types.md:1341-1343`, spread `:1402-1410`): static per element and no
  erasure, but every one of the 336 calls changes spelling (`run(a, b)`), and a
  list of run-time length — `store.vl:1766`'s `IN (?, ?, ...)`, `word_filter`'s
  `LIKE` per word — has no tuple at all. Shape 2 would have no spelling.
- **Keep `List<any>` and refuse an unholdable value at `any`** (F150 (2), A176
  (2)): not breaking (a built `List<str>` is absorbed by `any`), and the refusal
  names the vilan type. But `any` stays std's public surface, there is no `Bytes`
  in the type, and a user newtype cannot bind. It is the right fallback if the
  owner wants no break.
- **A generic `run<P: SqlParams>`** with impls for `List<T: SqlValue>`: a
  heterogeneous literal `[id, 1.5]` has no element type to infer, so it breaks
  the 336.

## 5. Recommendation and sizing

Build §3, **M**, **BREAKING**: the 336 literals compile unchanged; the 3 built
`List<str>` sites in kolt do not (the item's "estate: 0" counted `List<any>`, and
`any` absorbed `List<str>`). The patch, the owner's: type `parameters` at
`store.vl:1766` and `word_filter`'s list (`mcp.vl:798-800`) as
`List<dyn SqlValue>`, and push per element instead of `push_many`. In the vilan
estate the one pin that builds a `List<any>` (`db_bind_conversions.vl:27`) moves.

| file | what |
|---|---|
| `vilan/std/src/db.vl` | the trait, 15 impls, `sql_null`, three signatures and their maps, `Row::bytes` |
| `crates/vilan-rt/src/lib.rs` | `Any::Blob`, `From<Bytes>`, its `Js`/`Json` arms |
| `crates/vilan-rt-sqlite/src/lib.rs` | `bind`/`read` BLOB arms, the `bytes` column reader |
| `transformer.rs` | `__db_null`; the binder's sentence |
| `analyzer.rs` | the steer naming the impl set at a `dyn SqlValue` refusal |
| docs | `vilan/docs/std/process.md:22-25`, a `SqlValue` paragraph |
| pins | the three refusals; `Option` at depth 2 and through a generic (B679's shape) on both backends; a BLOB round trip on both backends; `db_bind_conversions.vl` moved |

With it, `any` has no public std bind-list user, so A176's (1)/(3) can be ruled
for user code alone.

## Questions for the owner

1. `List<dyn SqlValue>` (breaking: 3 kolt sites), or keep `List<any>` with
   F150 (2)'s checker refusal (not breaking, untyped)? Rec: `SqlValue`.
2. `Bytes` as BLOB in this lane, with `Row::bytes`? Rec: yes — it is a rustc
   error natively today.
3. Is `SqlValue` open to user impls (a `UserId`)? Rec: open; F150 (2) keeps a
   user impl honest.
4. The variadic tuple form refused outright (not offered beside the list)? Rec:
   yes — two spellings for one call, and the run-time-length case has none.
