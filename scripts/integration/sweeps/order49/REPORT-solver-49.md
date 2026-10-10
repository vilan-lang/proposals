## solver-49 report (Order 49, wave 2)

The list is done: 19 items DONE (B584 included), M132 DONE, and M131 measured with its own fix HELD. The full suite is green on the rebased tip. B596 (lang-a's struct-literal evaluation-order miscompile) is NOT taken; please queue it for Order 50.

**Tip and base.** Branch `solver-49` @ **a4d6e500**, 20 commits on origin/next @ **b04e912a** (debug-49 merged), not pushed. I started from 71d61dde and rebased twice: onto 77b23af2 (C3), then onto b04e912a. Only CHANGELOG and ledger-TSV conflicts came up, resolved by keeping both sides' entries. lang-a-49 is merging now; its `Type::Tuple(elems, _)` change will touch my arms in analyzer.rs on the next rebase. Worktree: `vilan/.claude/worktrees/solver-49`. `LANE-STATUS.md` is untracked and current. The `solver-49-base` perf worktree is reaped.

### Gates on a4d6e500
- `cargo nextest run --workspace -j 6`: **10034 / 10034 passed**, 31 skipped. This covers inference, module_resolution, edit_replay + permutation differentials, check_scope_differential, corpus, docs, diagnostics_ledger, ci_ignored_pins and hygiene.
- `native_differential` with `VILAN_NATIVE_DIFFERENTIAL=1`: 227/227. The corpus census moved from 130/126/4/0 to **130/127/3/0**: capture-clones.vl is now identical on both backends, because B579 removed its last wall.
- `cargo fmt --check` and `clippy -D warnings` are clean. Every commit compiles on its own (checked with `rebase --exec`).
- `scripts/ci-local.sh perf`: green, T2 verdict green, growth x1.938. Late writes are 0.

### Per item (shas on a4d6e500)
- **B583 DONE** (c317f775, fix). The rule is now in spec names.md §4.6: std's files reach every std trait and no package trait. So a package trait's impl, blanket or not, is never a method candidate at a call inside std. A package impl *of a std trait* still is. The filter (`retain_std_reach`) only narrows the candidate list, never empties it. Pins: `modules::b583_*` (2).
  - The general case is not fixed: a std trait the *user's* file never imports still makes that file's call ambiguous. Filed as B?1.
- **B588 DONE** (4d827dc7, fix, as ruled). A tuple bound contained in a tuple blanket's subject bound now counts as a declared bound (`tuple_blanket_trait_ids`). Dispatch still happens per instance. The refusal no longer calls a tuple-bounded parameter "unbounded". Pins: `bounds::b588_*` (3) plus a native pin.
- **B589 DONE** (18f85890, then 08803237 for the ordering, fix). A fully annotated closure's written parameter types are read first, using the walk's `parameter_modes` record.
  - The premise needed one correction: reading them *before* typed value arguments broke B306 and B438. The order is now: typed values, then generics derived from bounds, then written closure parameters, then literals. Pins: `generics::b589_*` (2).
- **B554 DONE** (341ec360, diagnostics). When two files disagree about a module binding's element slot, the error now lands on the declaration with both types sorted and a trace hop at each use, and the slot settles on `any`. The permutation pin `b554_an_element_conflicts_blame_is_a_fact_about_the_program` is **un-ignored and green**. Two uses in the same file keep the old message. Pins: `modules::b554_*` (2).
- **M130 DONE** (b0b75c31, fix). Inherited-default candidates are keyed by home. Two homes count as different only when some position has concrete, differing arguments; keying more strictly broke b245 and kolt (`DeltaFeed` reaches `Source`'s `effect` through its supertrait). Ambiguity is reported at the loop and at the call (providers sorted). Pins: `modules::m130_*` (2).
- **B579 DONE** (b6c3e524, **breaking**). `-`, `*`, `/`, `%` over two different integer types are refused with `+`'s sentence; the editor quick fix applies. `f64 * i32` is left as it was (see question 1). Pins: `index_type::b579_*` (2).
- **B580 DONE** (a3b09ffa, **breaking**). A user `let` whose type keeps a hole is refused at its initializer. Like the residual sweep, it only fires when no other error is present.
  - It exposed an inference bug, fixed in the same commit: `Holder<str>::Empty` (a payload-less variant at a written instantiation) had held a hole per parameter.
  - What the item text got wrong: a binding whose *uses* state its type (`let s = Slot::Bare; want(s)`, `let n = None; n.unwrap_or("d")`) is also refused, because inference never carries a use's type back into the binding. B357's pin was reshaped to keep the direct-use cases legal. See question 2.
  - Pins: `collections::b580_*` (2), `bounds::b580_*`, `a_never_pushed_lists_len_is_refused_at_the_literal`.
- **B581 DONE** (5c03832a, door (a)). types.md §5.9 is corrected and the existing behaviour is pinned (`tuples::b581_*`).
- **B590 DONE** (f9d79ef9, **breaking**). `[T; n].len()` is now `usize`. Pins: `fixed_array_len_..._as_usize`, `b590_*`.
- **B582 DONE** (cafa73b0, fix). The `Node::ArrayType` arm in `register_subject_binders`. Pin: `tuples::b582_*`.
- **B591 DONE** (a6cbb31b, **breaking**). An index that is still untyped is recorded and re-checked at the end of each fixpoint (`recheck_lenient_subscript_indexes`). A negative call index is now refused as `i32`. I tried deferring the subscript first; it cost every program a round of retries, so I dropped it. Pin: `index_type::b591_*`.
- **B587 DONE** (8e8942e0, miscompile). A top-level tuple pattern under a view subject now binds views. The emitters needed no change and both backends agree. Pins: `borrows::b587_*` (2) plus a native pin. The refusals still say "payload" for a tuple subject (filed E?1).
- **F108 solver half DONE** (a9a801ea, fix). An empty list literal's slot is now filled from the parameter's bound (`push_many([])`). I re-pointed native-48's attribution pin to a probe that is still refused natively, `Option::None.is_some()`. Pins: `collections::f108_*` plus a native pin.
- **B574 DONE** (a3900520, diagnostics). The premise was wrong: the bound's miss already goes through `import_steer`. The real cause was std's import index, which read the derive macro `Storable` and the trait `Storable` as two homes and dropped the name. Macros now index in their own namespace. Pin: `modules::b574_*`.
- **A164 DONE** (31d6db3a, diagnostics). The mismatch now says "the `null` value". Pin: `modules::a164_*`.
- **E285 DONE** (fce6bd52, diagnostics). The list literal's element check now carries E272's fragment marker. Pin: `modules::e285_*`.
- **B585 DONE** (2afab85e, diagnostics). The six static-path arms in `resolve_world` now use `push_anchored`. Pins: `module_resolution::b585_*` (6).
- **B584 DONE** (eba3c589, fix). I built it on the context pass as it stands (S3 moved to Order 50) and did not edit context.rs.
  - The cause was in method resolution: a call on a `Context` whose value slot is still open bound nothing, so `get()` stayed typed as the abstract `T`. Such a call now binds the impl's parameter to the open slot itself (`bind_open_context_slot`).
  - Pins: `modules::b553_a_module_context_grounded_only_by_an_entry_run` (un-ignored) and `b584_*`. The native build prints 6.
  - I updated incr's ERD plant test: the context edit is now order-free even with the use-inferred guard off. That guard's context arm can be retired (incr's decision).
- **M132 DONE** (a4d6e500, performance). `async_infer` dispatch candidates are memoized per (trait, member), and unions dedup with a set. Candidates and their order are unchanged. This is the large perf win in the table below.
- **M131: measured, fix HELD.** Release builds, reactive-ui, std variants via `VILAN_STD`:

  | measurement | instructions | share of reactive-ui |
  |---|--:|--:|
  | both A165 arms + helper | 12.05M | 0.65% |
  | `Flow<Option<View>>` blanket alone | 7.36M | 0.39% |
  | `Option<V: Slot>` arm | 1.64M | 0.09% |
  | helper body | 2.9M | 0.16% |
  | both arms after M132 | 10.9M | — |
  | blanket after M132 | 6.87M | — |

  A callgrind diff puts the blanket's cost partly in the post passes (platform_color's reachable-bindings walk and `callee_substitution`, which are incr's) and partly in the analyzer's bound proofs. Door (a) needs a memo keyed safely against B401 admission and M121's reach record, so it is filed as M?1 rather than rushed.

### Breaking entries and their estates
Counted on a kolt copy, the website's `src`, the 11 examples, and vilan/test (std itself is clean).

| item | estate | change made |
|---|---|---|
| B579 | 1 corpus site, capture-clones.vl:143 | `weight.as_usize()`; golden is renames only, runtime identical |
| B580 | 1 kolt site, `src/sidebar.vl:65` (`Signal::new(None)`) | fix: annotate `SignalCell<Option<Channel>>` |
| B591 | 1 corpus file, compound-index.vl, 3 sites | counter is now `usize`; golden unchanged |
| B590 | 0 edits | — |

Outside the estate, compiler test programs had to change: 11 test programs that index with an `i32` call (B591), plus never-pushed-list pins (B580).

### Perf rows
Tip vs current next b04e912a, release, instructions:u, millions:

| subject | next | tip | ratio |
|---|--:|--:|--:|
| math | 257.9 | 253.6 | x0.983 |
| watch | 326.2 | 319.6 | x0.980 |
| browser | 1,451.2 | 1,431.9 | x0.987 |
| fullstack | 3,067.2 | 3,000.0 | x0.978 |
| router | 1,710.2 | 1,657.3 | x0.969 |
| reactive-ui | 1,860.8 | 1,802.6 | x0.969 |
| ssr | 3,847.7 | 3,707.1 | x0.964 |
| canvas | 1,462.1 | 1,442.1 | x0.986 |
| rpc | 2,012.5 | 1,890.2 | x0.939 |
| todo | 5,024.2 | 4,720.2 | x0.940 |
| walkthrough | 5,105.2 | 4,826.0 | x0.945 |
| genapp:46 | 8,788.7 | 8,744.9 | x0.995 |
| plain:160 | 3,077.3 | 2,921.9 | x0.950 |
| plain:320 | 6,217.3 | 5,662.7 | x0.911 |

Before M132, my items alone had cost up to +0.7%. I cut that to at most x1.0027 by removing per-call allocations and slot mints, borrowing in `type_has_hole`, and re-checking subscripts at the end of the fixpoint instead of deferring them. The ci rows can be ratcheted down at the seal; no bump.

### Finds
All in `sweeps/order49/newitems49-solver.json`, repros under `sweeps/order49/solver-49/finds/`:
- **B?1**: a std trait a user file never imports still makes that file's call ambiguous.
- **B?2**: a binding's hole that a call's bare-trait parameter states is not grounded (kolt's sidebar shape).
- **B?3**: an expression hole that no binding holds checks clean but is refused natively.
- **E?1**: tuple view refusals still say "payload".
- **M?1**: the post-pass and bound-proof cost of a std `Slot` blanket (M131's remainder).

### Questions for the owner
1. **B579's scope.** Should `f64 * i32` (float and integer) be refused too? Natively it is already refused. Rec: yes, in Order 50, after counting the estate.
2. **B580 and bindings whose uses state the type.** Today `let n = None; n.unwrap_or("d")` is refused, though Rust infers it. Rec: build fill-from-use for the argument and receiver channels in Order 50 (B?2); it would also take kolt's one site to 0.
3. **R-h's breaking list.** B590 and B591 are marked `breaking` beside B579 and B580. Rec: list all four at the v0.47.0 cut.
4. **B596.** Not taken here because next keeps moving and each rebase re-runs a ~45-minute suite. Rec: queue it for Order 50 as you proposed.
