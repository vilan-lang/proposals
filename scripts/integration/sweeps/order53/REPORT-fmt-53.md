# REPORT fmt-53 (Order 53, Sonnet 5.5) - E321

Tip b5d136e5 on base fe19e1c1 (origin/next, after std-53's merge). One commit, family `tooling`: "E321: vilan fmt breaks a long call's arguments one per line everywhere, tuples included". Files: crates/vilan-core/src/formatter.rs, CHANGELOG.md. Nothing pushed. fmt-53-STATUS.md untracked. analyzer.rs, mono.rs and the emitters untouched (no perf leg).

## What changed in formatter.rs
- All five `hole_depth > 0` uses dropped (Call arm, call-subject door x2, split-chain subject, tuple split). The `hole_depth` field and the hole's own context remain (a hole still resets the refusal).
- Refusal 1 (a call met inside another call's INLINE attempt never breaks): the call-subject door of the inline chain attempt now requires `!arguments_blocked` (the ungated door was what made kolt sidebar.vl:80's closure body chain break).
- Refusal 2 (operands of a chain of 3+ never break their own arguments): `print_split_binary_chain` now keeps `arguments_blocked = true` (it used to unblock for the split operands - the cause of markdown.vl's `code_at(\n1,\n)`).
- Two corrections the ungated layout needed: (a) a call whose OPENING line (up to the `(`) is already over the budget keeps its arguments inline (closure parameters, long `let` head - splitting bought nothing); (b) the `on(..)` head's sorted condition values now print in the split layout too (`print_call_argument`; the old `head.is_none()` guard made `format(format(x)) != format(x)` once the gate was gone: a real idempotence gap, first run sorted and kept the line, second broke it).

## Pins
- New module `argument_layout`, 11 tests (assert_construct: token round trip, idempotence, canonical round trip): plain long call, nested call in a closure argument, call subject + link on its own line, struct-literal argument, closure argument, lone over-wide argument left alone, lone argument that fits takes its line, tuple slot comes apart, chain of three never breaks operands' arguments (store.vl / markdown.vl shapes), call in another call's inline attempt never breaks (sidebar.vl shape), hand-wrapped call collapses when it fits. 8 red on the base, 3 are guards that pass there (one of them red when only the gates are dropped).
- Re-pinned one by one (9, each an "out of scope / stays inline" pin whose input is now in scope): an_earlier_argument_is_still_not_reachable, a_single_link_right_operand_leaves_the_line_long, a_single_link_and_a_plain_long_call_stay_inline, the_same_call_outside_markup_stays_inline, an_earlier_argument_does_not_recurse_and_the_line_stays_long, an_expression_bodied_closure_argument_stays_inline, a_statement_whose_opening_line_fits_is_left_alone (body call now breaks), an_empty_struct_literal_at_an_over_budget_tail_stays_inline (literal stays `Empty {}`), on_head_order::the_condition_values_sort_into_the_canonical_slot_order (now split). closure_parameters_do_not_break passes unchanged thanks to correction (a). hole_call_layout's 9 pass unchanged.
- Fmt "goldens": none moved. The corpus test, the formatter idempotency tests over the std files (fixed points) and fmt_declines / fmt_wrap_comments all pass untouched; the only expectation changes are the nine unit pins above.

## Gates (on b5d136e5; formatter logic identical for every run, only a rustfmt wrap and one unused import changed after the suite)
- Full suite `cargo nextest run --workspace --cargo-profile ci-test -E 'not binary(deep_nesting)' -j 6 --no-fail-fast`: 10647 run, 10647 passed, 38 skipped (includes ci_ignored_pins, hygiene, corpus, check_scope_differential, native differential default mode). That run preceded the rustfmt/unused-import tidy; the formatter unit tests were re-run after it: 509/509.
- Native differential sweep mode (VILAN_NATIVE_DIFFERENTIAL=1): 282 run, 282 passed, 1 skipped.
- `cargo clippy --workspace --all-targets -- -D warnings` clean; `cargo fmt --check` clean.
- `vilan fmt --check .` over the worktree: NOT clean by design - it names exactly the 34 files the integrator reformats in the merge commit (std 18, native tests 13, examples 2, test/ 1; listed by `vilan fmt --check .`). On the final code, fmt over scratch copies of the seven estates: `--check` rc=0 on all seven afterwards (fixed points).
- Canary, vilan-lsp, perf, RSS: not run (no walk, record, table, analyzer, mono or emitter touched; the formatter is not on the check path).

## The estate on the final code (diff lines / files; +lines -lines)
| estate | files | + | - | diff lines |
| std | 18 | 472 | 141 | 1236 |
| kolt | 7 | 154 | 27 | 303 |
| native tests | 13 | 101 | 14 | 244 |
| website | 6 | 77 | 8 | 152 |
| examples | 2 | 12 | 3 | 35 |
| test/ | 1 | 4 | 1 | 15 |
| benchmarks | 0 | 0 | 0 | 0 |
| total | 47 | 820 | 194 | 1985 |
(The sample before the refusals was 2,097 diff lines in 49 files; the refusals removed the store.vl x2, store_core, markdown, kolt styles x2 and sidebar shapes.) Full diffs: sweeps/order53/fmt-53/finds/e321-<estate>.diff.
Kolt patch: sweeps/order53/fmt-53/kolt-e321.patch (`diff -ruN` a/src vs b/src, -p1 from the kolt root, lucide and search-dict excluded; 7 files; applied clean to a pristine copy and re-verified identical to the reformatted copy). The website (6 files) is reformatted at the fold by `vilan fmt`.

## Where a premise was wrong
- The brief and E321 said "three gates"; there are FIVE `hole_depth` uses (the tuple split is the fifth; the owner ruled it in).
- "The two refusals re-pinned" were not pins to restore: the ungated door and `print_split_binary_chain` bypassed them (the chain split explicitly unblocked its operands), so two lines of code, not only pins, were needed.
- fmt-52's "1,813 lines in 60 files" does not reproduce (47-49 files, 1,985-2,097 diff lines); it counted differently.

## Finds (sweeps/order53/newitems53-fmt-53.json)
- E?1: a call statement exactly 100 columns before its `;` stays on one 101-column line (the Call arm measures before the `;`; chains split). Repro finds/call_at_exactly_the_budget_before_its_semicolon.vl. XS.
- E?2: a two-operand chain whose right operand is a call (`a == b + 1 && starts_with(..)`, std store_core.vl two sites) breaks the call's arguments with the `&&` inline - a fifth shape beside the owner's four accepted; owner's taste.

## Questions for the owner
1. The two-operand chain with a call operand (E?2): keep (the rule as ruled), refuse it like the 3+ chain, or break a 2-operand `&&`/`||` at its operator? Rec: keep for now; two sites in std only.
2. The 100-column-plus-`;` edge (E?1): fix in the same stream next order? Rec: yes, XS.
3. Merge: the integrator runs `vilan fmt .` over the tree in the merge commit (34 files); kolt's patch and the website at the fold as planned.
