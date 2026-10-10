lang-b-49 is finished: tip e3b01166 sits on base b61f00bd, origin/next with solver-49 merged on top of lang-a-49. It is 13 commits, not pushed, and all gates pass on the rebased tree. Worktree: /home/reed/code/vilan-lang/vilan/.claude/worktrees/lang-b-49. LANE-STATUS.md is untracked. The pre-rebase states are kept as local branches lang-b-49-prerebase, -prerebase2 and -prerebase3.

## Commits (all DONE)
| sha | slice |
|---|---|
| 05197dd8 | B571 S1: `value as T`, a constraint, never a cast |
| 01523e5a | B571 S2: an ascription's refusals teach once |
| 6c318cdd | B571 S3: the formatter lays ascriptions out |
| 05cf4b2b | B571 S4 / E278: per-stage inlay hints |
| 61914567 | B571 S2 follow-up: a parenthesized value keeps its parens in the numeric rewrite |
| 91de7d5e | B570 S1: `auto` annotations |
| 3225c044 | B570 S2: `value as auto T` |
| 96de53fa | B570 S3: the editor keeps `auto` types current |
| 1cc1cd15 | B570 S4: the `[check] auto` opt-in |
| a510fef0 | B571 S3 follow-up: `as (T)` prints as `as T` |
| 5048e4f5 | E284: a spaced `a < b > (c)` names both readings |
| 252868c0 | B571 S1 follow-up: the walkers and coercion sites see through an ascription |
| e3b01166 | B570 S3 follow-up: the editor page lists the `auto` fixes |

Each commit message names its pins. Every commit has a `## Unreleased` CHANGELOG entry with a family marker and NEW ledger rows.

**Expr::Ascribe arms in incr's files, as approved:** only `track_caller.rs::own_body_children`, plus the two lines in `analyze_over_world` (`stage_hints`, `auto_fills`) and the `check_auto_annotations` call. `stage_hints` is built for every id on every analysis. The reuse pin is `entry_world_tests::e278_a_stage_hint_is_served_on_a_module_reused_after_an_edit_elsewhere`. The other mechanical arms are in liveness.rs, call_graph.rs, init_order.rs and transformer.rs.

## Changes made for lang-a-49's tuple labels (B569)
Each was folded into the commit of the slice it belongs to, and each pin was proven to go red with the fix removed:
- **Labels are written out.** Stage hints, the "Ascribe this stage" action and `auto` fills all write a labelled tuple with its labels. Pins: `stage_hint_tests::a_labelled_tuple_stage_hints_its_labels` and `b570_a_bare_auto_fills_a_labelled_tuple_with_its_labels`.
- **When `auto` counts as stale.** A written `auto` type agrees with the inferred one by B569's own reconcile rule. The one exception is a label the two carry at different slots, which is reported as stale with a rewrite. Pins: `b570_tuple_labels_that_reconcile_agree` and `b570_a_contradicting_tuple_label_is_stale`. One line was added to spec/types.md.
- **A real bug fixed:** `as (x: T)` is a one-slot labelled tuple, not a group. fmt was dropping its parentheses and then declining its own output. Pin: `reformats::b571_a_redundant_parenthesized_ascription_prints_bare`, extended.
- **Mismatch message.** An ascription whose labels contradict the value's now carries B569's sentence and both rewrites. Pin: `b571_tuple_labels_through_an_ascription_read_as_at_a_binding`.
- **Native probe.** B571_PROBE gained the labelled rows, and they are identical on both backends.

## Gates on b61f00bd
- fmt check and clippy `-D warnings` are clean.
- Full nextest suite: 10165/10165 passed, 31 skipped.
- Native differential with `VILAN_NATIVE_DIFFERENTIAL=1`: 233/233.
- VS Code: `npm test` 28/28, tsc clean.

## Perf (local class, instructions:u, base b61f00bd vs tip)
T2 is green.

| row | base | tip | change |
|---|---|---|---|
| math | 254.3M | 255.9M | +0.64% |
| watch | 320.5M | 322.4M | +0.59% |
| browser | 1435.5M | 1443.0M | +0.52% |
| fullstack | 3005.5M | 3021.8M | +0.54% |
| router | 1660.4M | 1667.7M | +0.44% |
| reactive-ui | 1806.0M | 1814.4M | +0.47% |
| ssr | 3712.3M | 3730.7M | +0.50% |
| canvas | 1445.2M | 1453.6M | +0.59% |
| rpc | 1893.2M | 1901.8M | +0.45% |
| todo | 4726.3M | 4747.1M | +0.44% |
| walkthrough | 4833.3M | 4854.9M | +0.45% |
| genapp:46 | 8758.9M | 8890.5M | +1.50% |
| plain:160 | 2924.7M | 2953.3M | +0.98% |
| plain:320 | 5663.9M | 5727.3M | +1.12% |

Growth is x1.939 on the tip and x1.937 on the base.

**A regression I found and fixed before landing.** The first comparison showed genapp +15.5%. Callgrind traced it to E278's chain-head lookup, a reverse scan of `chain_stages` on every method call, which is quadratic in a program's calls. It is now a `chain_heads` map, folded into 05cf4b2b. What remains on genapp, about 130M, is the stage-hint, `auto`-fill and written-spelling work, which runs on every analysis including plain CLI `check`. Of that, about 41M is the settled-solver `infer_type` calls.

## B570 S0 numbers (kolt, 31 commits)
- 9 of 30 commit pairs would move an `auto` line under door (b), 8 of 30 by full type.
- 28 of 30 commits do not check clean on today's compiler, so only one pair is clean.
- At the tip:
  - 63 function and 35 `let` candidates;
  - 1 stage-typed return: `model.vl::user` becomes `auto Source<Option<User>>`;
  - 1 type that cannot be written: `shared.vl::hash` returns `Hash`.

## std opt-in measurement
Under "exported", std would gain one annotation, `std::base64::alphabet: auto str`; every other non-void return in std is already written. The paper's syntactic count was 17, or 126 with methods. I did not take the opt-in: it reads only the entry package's manifest, so it would do nothing for std.

## What the papers got wrong on the tree
- `as` can begin a statement, because it is a name. An ascription at a statement head is admitted only on the closing brace's line.
- The analyzer does not record call types, despite §11's "already types every call node". Stage hints and `auto` fills ask the settled solver and roll back its diagnostics.
- auto §5's full-path tier does not resolve (A901).
- auto §8's std count was 17/126; the measured count is 1.
- The view-of-ascription refusal is wider than the paper: any `&(x as T)` is refused.
- An ascription ends a `?.` continuation rather than being absorbed into it.
- Neither paper anticipated tuple labels. They were handled as described above.
- Unverified: declaration labels may not include an unannotated function's inferred return, because `render_function_signature` reads only `return_type_id`. This is for incr-49.

## Finds
Entries are in proposals/scripts/integration/sweeps/order49/newitems49-lang-b.json, uncommitted and passing `file_items.py --check`. Repros are under sweeps/order49/lang-b-49/finds/. I filed nothing new after the rebases.
- **E901:** the whitespace rule for a spaced generic list in expression position.
- **F901:** native filter dereferences a scalar view.
- **B901:** narrowing at an annotated `let` reports twice.
- **A901:** a full std path in type position.

## Questions for the owner (recommendation in brackets)
1. An ascription ends a `?.` continuation. [keep]
2. Any view of an ascription is refused. [keep]
3. A mutating method called through an ascription is refused. [keep]
4. The `[check] auto` opt-in reads only the entry package, so it does nothing for std. [don't take it now; revisit with M120]
5. E278's "Ascribe every stage" uses the refactor action kind. [keep]
6. Locals got `auto` in S1. [fine]
7. A901, the full-path tier. [keep declining]
8. E901, the expression-position whitespace rule. [decide after a census]
9. Labels under `auto`: they agree by B569's reconcile rule, and only a label at two different slots is stale. [keep: it is the language's own rule]
10. Stage hints and `auto` fills are computed on every analysis, including CLI `check`, which never reads them. That is about 1.5% on genapp. [accept for now; skipping them for CLI-only analyses is a cheap later item]
11. The declaration-label observation above, for incr-49.
