# v0.41.0 — the release-notes breaking-changes summary (cut plan Q3)

Written by lane papers-42 of Order 42 on 2026-09-25, against vilan `next`
@d65d4e75 and the cut plan (`sweeps/order41/papers-41/cut-plan.md` §2, §5.3,
§8 Q3 — RULED yes at GO, R-a). The integrator FINALIZES it at the sweep and
writes it into the `release: v0.41.0` commit, after `cut-release.sh --commit
0.41.0` retitles the section and before the tag.

## 1. Where it goes

Between the section heading `## v0.41.0 — <date>` and the section's first
`<!-- family:` line. `release.yml`'s notes step keeps `entries[0]` — the text
before the first `\n<!-- family:` — unconditionally, so the summary always
reaches the GitHub release body even when whole entries are cut. It is written
into the RELEASE commit because `cut-release.sh` refuses prose under
`## Unreleased`.

Shape rules, checked on this draft: no line starts with `**` (the seal's parity
count reads `**` heads under `## Unreleased`; harmless in a released section,
kept clean anyway), no `<!-- family:` text, no `## ` heading (the notes step's
awk ends the section at the next `## `; the summary uses `###`/`####`).

## 2. What to finalize — every `[[…]]` token goes

| token | lane | action |
|---|---|---|
| `[[FINALIZE I5 S2]]` | index-42 | check the line against the entry's own migration line; delete the token |
| `[[FINALIZE A124 S2c]]` + `[[SPELLING]]` | reactive-42 | the `Resource` constructor's spelling from the report; the rest against the entry; delete the tokens |
| `[[FINALIZE B413: in the train]]` / `[[FINALIZE B413: held, this line instead]]` | syntax-42, R-c | keep EXACTLY ONE of the two lines per R-c; if held, the `<!-- deprecates: -->` marker must be on B413's announcement entry |
| `[[FINALIZE B407: if breaking]]`, `[[FINALIZE B405: if breaking]]` | solver-42 | keep a line only if its CHANGELOG entry carries `<!-- family: breaking -->`; else delete it |
| (B415's net-zero line) | syntax-42 | untagged — it lands in this train either way; delete it only if B415's entry is not family breaking |
| any OTHER breaking entry this order adds | — | one line in its group, in this voice |

The count to check at the end: one line per `<!-- family: breaking -->` in the
section (35 before this order, plus this order's), the combined lines noted in §4.

## 3. The summary (the text between the rules, verbatim)

---

### Breaking changes, and what to change

Every breaking entry below, one line each with its migration, so the list is whole even where the release page is cut short. "Net-zero": the earlier shape never shipped in v0.40.0.

#### Language

- A bare trait at a struct field is refused: write `dyn Trait`, or the concrete type if the field needs an inherent method.
- `Self<i32>` is refused: write the type's name (`Cell<i32>`).
- An explicit type argument outranks an argument that knows less: drop the arguments or make them agree.
- `lazy` is a keyword: rename any name spelled `lazy`.
- A type's method namespace is per importing file: pick between two extending imports with a selector; an `impl` in a module with curated exports needs `export impl`.
- A type segment replaces an import path's namespace: reach a module member at its module.
- Importing an unexported item warns: import the exported name, or mark the reach (`{ #hidden }`).
- `export (helper);` and `export * helper;` are refused: `export` takes an item or an import.
- The right operand of a generic-bounded operator is checked: use one type, or bound `P: Add<Q>`.
- A condition typed by a generic parameter is refused: pass a `bool`.
- A `::` path may not cross a line break: join the line, or `import a::b::c as d;`.
- A negated capture in a `for` condition or `match` guard is refused: bind after the test.
- An `is` capture is in scope only where its test passed: read it in the then-branch or after `&&`.
- An operator trait's method is required at impl time: implement it.
- `fun main` takes no parameters: read `std::process::args()`.
- An operator on a generic left operand needs a bound: `<T: Add>` (`Sub`, `PartialEq`, `PartialOrd` likewise).
- [[FINALIZE B407: if breaking]] A negative literal at an unsigned type is refused: use `None`, a fallback, or a signed type.
- [[FINALIZE B405: if breaking]] A fractional literal at an integer position is refused: write an integer, or `.as_f64()` the other side.
- [[FINALIZE B413: in the train]] `resource struct`/`resource enum` are `[resource] struct`/`[resource] enum`; the old spelling is refused, naming the new.
- [[FINALIZE B413: held, this line instead]] Deprecated: `resource struct`/`enum` become `[resource] struct`/`enum` in v0.42.0.
- Net-zero: a file's platform is `[platform("browser")] mod self;`, not a bare `[platform(..)];`.

#### Standard library

- [[FINALIZE I5 S2]] Every std length, position and count is `usize`, and `list[i]` takes one: convert with `.as_usize()`/`.as_i32()` (the quick fix inserts them); a `-1` sentinel becomes `None`; count down with `for i > 0 { i -= 1; … }`. A negative `.as_usize()` is 0; `std::fs` offsets stay `i53`; a `usize` in an rpc signature moves its contract hash (rebuild both halves); frames do not change.
- `std::random::range` is `[low, high)`: for the old range, `range(low, high + 1)`.
- `unwrap_or`/`expect` on `Option` and `Result` take their argument `lazy`: hoist a fallback whose side effect must run.
- The six `View` parent methods are gone: `parent.swap(s, r)` is `parent.child(swap(s, r))`, `bind_each*` is `each*`; the quick fix rewrites them.
- std curates its exports: reaching an unexported item warns; use the documented name.

#### Reactive

- [[FINALIZE A124 S2c]] `map`, `switch`, `combine`, `flatten` and `and_then` return cold nodes, not `SignalCell`s: drop the `SignalCell<U>` annotation, or add `.cell()` where a cached cell is wanted; a `Source`-typed parameter takes a node unchanged. `.cell()` in a module binding's initializer is refused: build it under an owner, or write `.cell_global()`. The rpc mirrors lose their own `map`. `Resource<T>`'s constructor is `[[SPELLING]]`.
- Keyed `each*` and `reconcile` need `K: PartialEq + Hashable`: `[derive(Hashable)]`, or an `impl` hashing the fields `eq` reads.
- `Source::on_change` is the requirement, `sub` derived: rename an impl's `fun sub` to `fun on_change`, dropping its immediate call.
- `Optimistic<T>` is `Optimistic<T, S: Signal<T>>`: write the second parameter where the type is spelled.
- Net-zero: `KeyedCursor` is `DeltaCursor` (`KeyedCell` is new in this release).

#### Style

- A `css` block's declarations are calls: `property(value);`.
- Conditions are values: `not(inner)` is `cond.not()`; `within(name, value, inner)` is `.on(within(attribute(name).eq(value)), inner)`; `child_relation` is deleted (its steer names the replacement).
- Deprecated for one release: `Style::attribute`/`within`'s value form; write `.on(attribute(name).eq(value), inner)`, or `.on(attribute(name), inner)` for presence.
- Net-zero: `std::style::prelude` is new; its 46 names are the designed ones.

#### rpc and the wire

- The Wire visitor's receivers are `&mut`: a hand `impl … with Wire` takes `&mut S` / `&mut D`; `[derive(Wire)]` needs nothing.
- `[derive(Wire)]` emits only the wire codec: write `[derive(Json, Wire)]` to keep the JSON pair.
- An `[rpc]` method returning a source has a sync stub answering `RemoteSource<T>`: drop the `!` and the unwrap; read `status()` for errors.
- Net-zero: an awaited `void` stub answers `Result<void, RpcError>`.

#### Tooling

- `[doc(hidden)]` is refused: delete it; an unexported item is what it promised.

---

## 4. Notes for the integrator

**Coverage.** The 35 entries of cut plan §2, one line each, except where two
entries share one migration: A95's condition-values entry (`:706` in the plan)
carries the superseded A93 entry (`:872`); A95's deprecation (`:700`) carries
A89's interim `Option<str>` shape (`:1080`) — a v0.40.0 user goes straight to
the new form. The four net-zero entries are marked, per Q2 (kept as written).

**Size.** 5,215 characters as drafted (with the tokens); **4,963 finalized** in
the worst case (both solver lines kept, B413 in the train, a 22-character
constructor spelling). Under the 6,000 the brief allows.

**The headroom — measured, and it does not fit as it stands.** Re-running the
cut plan's §5.3 check on d65d4e75 (`notes_cap_check.sh` with `TMPDIR` in
scratch; then the breaking family's end located): section 1,608,194 characters;
the step keeps 42 entries (all 35 breaking + 7 miscompile); **the breaking
family ends at character 97,441 — headroom 12,559** (the plan's 12,656 was on
1265ea5d). **With this summary in place the headroom is 7,595.** This order's
breaking entries will spend it: I5 S2, A124 S2c and B415 at least, plus B413 and
B407/B405 if they ride — at the window's mean of 2,771 characters per breaking
entry (max 5,635), three entries already reach ~8,300. So **as the cap stands,
the release body will drop one or more BREAKING entries** — which the brief
forbids — although each one's migration line survives in the summary.

**Q — how is the headroom restored?** Options: (a) raise `release.yml`'s notes
margin `CAP = 110_000` to `120_000` — GitHub's limit is 125,000 characters and
the appended pointer is ~250, so 4,750 stays spare; one line, committed before
the tag (the tagged tree's workflow is the one that runs), and the step is
tag-guarded so no rehearsal exercises it — run its Python over the `--out`
section instead; (b) keep 110,000 and shorten the train entries until the
breaking family ends under it; (c) accept a dropped entry because the summary
carries its line. *Rec: (a)*, measured again over the finalized section before
tagging; (b) is fragile (the next union moves it) and (c) breaks the rule the
brief states. Not decided here — the integrator's or the owner's call at the
cut.
