native-47: final report

Branch `native-47`, tip **aea487f7**. Base: origin/next @e5e15ca7. Worktree: `/home/reed/code/vilan-lang/vilan/.claude/worktrees/native-47`. There are 6 commits, one per item, each with an `## Unreleased` CHANGELOG entry and its family marker. I created `## Unreleased` in the F90 commit.

origin/next has since moved to c43d6ab9. Those commits are only the Dependabot workflow bumps (R-i, `.github/workflows/*`), so none of my files changed and I did not rebase. Every number below is on e5e15ca7 + my commits.

F90's sha is in the untracked `LANE-STATUS.md`. The finds are in `proposals/scripts/integration/sweeps/order47/newitems47-native.json`: 12 items, placeholder ids, `|` escaped. Their repros are in `sweeps/order47/native-47/finds/` (14 `.vl` files).

## Items

| item | verdict | sha | note |
|---|---|---|---|
| F90 | FIXED | 8141e53c | **Two causes.** (1) A subscript read through a `Shared` view rendered as the place's own borrow, `(cell).borrow_mut()[i]`. That temporary lives to the end of the statement, so the compound write's re-read collided with the write. (2) The B105 compound-subscript hoist built its own statement and skipped F62's settle-the-value-first rule. **Fix:** a subscript is now a link of F62's scoped-borrow spine, `(cell).read_with(\|view\| view[i])`, with each index settled in a `let`, root first, for both `read()` and `write()`. Both assignment paths now share a new `finish_assignment`. **Shapes checked:** subscript, field, tuple slot, each nested under the others, a value reading the same cell, a captured `mut`, a module `mut`, and subscript reads in the same statement as a `&mut` loan, a push or a loop. All aborted or worked as noted on 0.44.0 and are now identical on both backends. As a side effect, `cell.read()[i]` no longer copies the whole list. |
| F89 | FIXED | 4049b166 | A pattern's subject was copied only when it was a binding or a field, not a subscript or tuple slot. This was true at all four sites: `match`, `if is`, the `&&` conjunction and the `?` lift. **Fix:** one predicate, `subject_is_a_place`, used at all four sites. A spine read through a `Shared` view is already a copy and takes no second one. |
| F85 | FIXED | 8d4d9c8f | The item's premise was right. An argument's position resolved only the head of the parameter type, so `\|T\| U` stayed the callee's generics. **Fix:** a new `argument_position` rebuilds the whole type under the call's substitution (`substituted`) and uses it when that closes it. This also fixed a generic METHOD's closure (`held.map(\|v\| Maybe::Just(v * 2))`). **Still refused:** a BLOCK-bodied closure. The analyzer records `U` as `Maybe` with no type arguments; filed as B?3. |
| F86 | FIXED | 6bc31b5e | **Premise half right.** The receiver half (`Maybe::Just(3).and_then(big)`, `.describe()`) was closed by F85's rule, because the receiver is argument 0. The `nest(self): Maybe<Maybe<T>>` case was refused even on a `let`-bound receiver, which is a separate cause. `nominal_entries` resolved an instance's arguments at the head only, binding the enum's `T` to `Maybe<T>`, and rendering then recursed until the guard gave up. **Fix:** a new `deeply_resolved` (and a `mint` helper factored out of `substituted`). |
| F88 | FIXED | e06e2e0a | F81's rule ("the tails are already the copies") now covers a block as well as `if`/`match`. `is_conditional` is renamed `yields_through_value_tails` and the change applies at both of its sites. |
| F50 | FIXED | aea487f7 | **(1)** `native-copy-census.tsv` gains a 4th column, `capture_copies`: the values a closure's capture prelude copies, excluding handle bumps (boxed cell, closure, `Shared`/`Weak`/executor handles, `str`) and scalars. `VILAN_NATIVE_REPORT_COPIES=1` appends `capture-copies=` to its existing line. **(2)** The leak census gains p10 as a row that is live by design: `native_probe_captured_cycle 1 1`. Spec §6.9 now states the native limit. |

## Fixtures and pins

All pins are in `crates/vilan-cli/tests/native_differential.rs`, each with its own `native/*.vl` fixture. Each fixture is `vilan fmt`-clean and was red on 0.44.0.
- **F90:** `a_compound_write_at_a_subscript_through_a_shared_view_is_identical_on_both_backends` (`native/shared_indexed_writes.vl`). Aborted on 0.44.0.
- **F89:** `a_pattern_over_an_indexed_element_copies_it_on_both_backends` (`native/indexed_match_subjects.vl`). Ten E0507s on 0.44.0. Covers `Option<str>`, an enum with a `Hash` payload, a tuple, a field element, a loaned parameter's element, a nested subscript, `is`, a destructuring `let` and a `?` lift.
- **F85:** `a_closure_handed_to_a_generic_callee_builds_at_the_calls_position_on_both_backends` (`native/generic_callee_closures.vl`).
- **F86:** `a_variant_constructor_as_a_receiver_is_identical_on_both_backends` (`native/variant_receivers.vl`).
- **F88:** `a_deref_of_a_blocks_view_reads_the_value_on_both_backends` (`native/deref_of_a_block_view.vl`). Six rustc errors on 0.44.0.
- **F50:** `the_capture_column_counts_a_copied_capture_and_no_handle`. I planted a bug and it went red (6 against 1). The leak-table row also pins it.

## Censuses moved

- **Native copy census:** every row gains column 4. I diffed columns 1–3 and none moved. Column 4 is non-zero in 9 of 37 rows: `reactive-flatten` 37, `dyn-objects` 25, `reactive-on-change` 22, `list-cell` 21, `delta-law` 12, `reactive-selector` 11, `shared-compound-write` 11, `native_probe_board` 4, `bytes-aliasing` 1.
- **Native leak census:** one new row, `native_probe_captured_cycle 1 1` (by design). Every other row is unchanged and 0 live.
- **Unchanged:** the JS copy-elision census, the shared census and all JS goldens. No corpus golden moved.

## std workarounds removed (F89)

All three bind-before-match sites:
- `vilan/std/src/reactive/store_core.vl` `prune_empty`: now `match path[depth - 1]`.
- `vilan/std/src/reactive/store.vl` map feed: now `match olds[index]`.
- `vilan/std/src/reactive/store.vl` set feed: now `match olds[index]`. This one had no comment.

The A142/A149 store pins stay green on both backends. store-47 owns that std area and merges after me.

## The 27 refused programs

None of them maps to an open tracker item. F1 is only the umbrella discussion. Two are refused by design; the other 25 are new and filed as 9 grouped items.

| program | refusal | class | filed as |
|---|---|---|---|
| arena.vl | `Option` with a VIEW payload outside a match subject | NEW (F21 remainder) | F?10 |
| async-await.vl | the program's own `[extern("node:timers/promises","setTimeout")]` | by design: a user host binding outside the native table. std's `sleep` is native; adding this binding would be one more table row | — |
| capture-clones.vl | guarded `match` leg | NEW | F?4 |
| css-block.vl | `const` value that is not plain data | NEW | F?9 |
| expression-lift.vl | `?` over a user `Lift` | NEW | F?7 |
| fixed-arrays.vl | `[value; n]` (the message also doubles a backtick) | NEW | F?11 |
| for-mut-container.vl | `for` over a user iterator | NEW | F?6 |
| generic-method-return.vl | field read of an unresolved subject | NEW (a generic call's type is read unsubstituted) | F?2 |
| lift-chain.vl | same | NEW | F?2 |
| match-patterns.vl | guarded leg | NEW | F?4 |
| math.vl | host `is_finite` | NEW | F?11 |
| multiline-string.vl | triple-quoted string | NEW | F?11 |
| preflight.vl | non-plain `const` | NEW | F?9 |
| resource.vl, resource_exit.vl, resource_take.vl | `resource` WITH `Drop` (F56 built only the Drop-less half) | NEW | F?8 |
| self-return.vl | unresolved subject | NEW | F?2 |
| set.vl | `for` over a `HashSet` | NEW | F?6 |
| side-effect-let.vl | mapped-tuple parameter | NEW | F?12 |
| signal-update.vl | closure handed a `&mut` view that re-reads the same place | by design (R3's ruled residue) | — |
| spread-parameters.vl, tuple-spread.vl | spread parameter | NEW | F?5 |
| style-when.vl, style.vl, theme.vl | non-plain `const` | NEW | F?9 |
| transparent-references.vl | a view binding aliasing another | NEW (F21 remainder) | F?10 |
| try-assert.vl | `!` through a user `Try` | NEW | F?7 |

Whole-set counts: 129 enumerated, 102 identical, 27 refused, 0 broken. This is unchanged from base: no program flipped, because each one's first wall is outside this lane's items.

## Finds filed beyond the 27

- **F?1:** an `is` capture to the left of `&&` in an `if`, read in the BODY, is rustc E0425. The emitted crate is edition 2024, so a let-chain would express it directly.
- **F?2:** a generic call used directly as an `if is` subject (`if wrap("x") is ..`, `if bound.nest() is ..`), a field subject or under `?.` reads the callee's declared return. It also accounts for three of the 27.
- **B?3 (solver):** a block-bodied closure at a generic callee is recorded with `U = Maybe<>` (no arguments) and an unresolved local. Native `is_grounded` also passes an argument-less generic vacuously. My experiment that fixed both sides only moved the refusal to the next use, so I reverted it and kept the diff in the scratch dir.
- **Not filed:** `apply(1, \|_k\| Maybe::Nothing)` is B540's shape, already the solver's.

## Gates (all on tip aea487f7)

- `cargo nextest run --workspace -j 6`: **9643/9643** passed, 33 skipped.
- `native_differential` with `VILAN_NATIVE_DIFFERENTIAL=1` (whole binary, so both modes): **167/167**. This includes the leak gate and copy census tables. Platform-free 129/102/27/0, platform-bound 9/6/3/0, async 7/4/3/0. The default mode was also green (165/165) during the work.
- Both native censuses regenerated; the moves are explained above.
- `check_scope_differential` (vilan-core): 15/15 in the suite.
- `corpus` (vilan-cli): 13/13 in the suite.
- `cargo clippy --workspace --all-targets -D warnings`: clean.
- `cargo fmt --all --check`: clean.
- `scripts/ci-local.sh vilan-fmt`: green. I renamed my scratch probes to `.vl.txt` first.
- `scripts/ci-local.sh windows`: green.
- `scripts/ci-local.sh perf`: T2 verdict green, growth x1.940.
- Docs, markdown_golden and book_mirrors: 16/16.
- The machine's load average was about 21 throughout.

## Emitter functions touched (vilan-rust/src/lib.rs only)

- `shared_view_field_read` and `reads_through_a_shared_view` (new `Step::Index`); `expression_inner`'s Index and Dereference arms.
- `assignment`, `hoist_compound_target`, and the new `finish_assignment`.
- New `subject_is_a_place`, used by `conjunction`, `if_branch`, `match_expr` and `lift_split`.
- `call_arguments_adapting` and the new `argument_position`.
- `nominal_entries` (now `&mut`), and the new `deeply_resolved`, `deeply_resolved_all` and `mint`.
- `is_conditional` renamed to `yields_through_value_tails`; `copy_a_consumed_place_read`.
- `closure`, the new `capture_is_a_copy`, and the `Emitted.capture_copies` field.

No analyzer or mono pass was touched, so I owe no instruction counts or late-write check.

## Changes outside vilan-rust and vilan-rt

- **vilan-cli `src/native.rs`:** `record_copy_census` takes a third argument, and the report line appends `capture-copies=`.
- **vilan-cli `src/main.rs`:** one line passes `emitted.capture_copies`.
- **`vilan/docs/spec/memory.md` §6.9:** one new paragraph, "Native limit: a captured binding can close a cycle". No fence and no heading. docs-47 owns that directory.
- **std** `reactive/store.vl` and `store_core.vl`: the F89 workaround removals above.
- I did not touch `inspect.rs` (debug-47's area).

## Needs a ruling

Nothing blocking. Two choices I made that the integrator may want to confirm:
- **Family markers:** F89, F85, F86 and F88 are `fix`, as native-46's rustc-refusal entries were. F90 is `miscompile`, matching F83, since it was a runtime abort. F50 is `tooling`.
- **Filing granularity:** I filed the refused list as 9 grouped items rather than one per program.
