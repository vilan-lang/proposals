## debug-49: final report

All four items are done. The branch is rebased onto C3, and the full gates pass on the rebased tree. Two of my commits touch other lanes' files and are flagged under owner questions 6 and 7.

**Branch.** Tip `220ed22c` on `debug-49`, rebased once onto `origin/next` @77b23af2 (C3), as you asked. The work started from @71d61dde. Worktree: `/home/reed/code/vilan-lang/vilan/.claude/worktrees/debug-49`. Nothing pushed. `LANE-STATUS.md` is untracked and current.

### Commits
| sha | item | family |
|---|---|---|
| e3fcd171 | E281 + E282 | tooling |
| ec6dd3af | S2 `dbg_stack()` | feature |
| 69d6c67d | E283 | fix |
| d869ff85 | `perf:` ci `[[bump]]` rows for my std additions (no CHANGELOG entry, as store-49's) | — |
| 220ed22c | S3 `print` of non-scalars | **breaking** (question 2) |

Each item commit carries its own `## Unreleased` entry. New ledger rows (`NEW`): "`dbg_stack()` takes no arguments…" and "`dbg_stack()` left in a release build…".

### Item 1 — E281 + E282: done
- **Move record (E281).** At a `dbg_stack()` call, the concrete move scan stores every moved resource binding: moved on all paths with the move's span, or moved on some paths. The record is `Program::dbg_stack_moves`, keyed by the call. R11's per-instantiation scan adds the generic half.
- **View record (E282).** The invalidation scan stores each capture view that is past its last use and that a rule-4 event has since reached. The record is `Program::dbg_stack_invalidated`. It follows the arms of an `if`/`match` and applies an event later in a loop to an earlier call in the same loop.
- **Pins:**
  - `inference::debugging::e281_e282_the_move_and_view_scans_record_their_state_at_a_dbg_stack_call`, on debug-48's repro.
  - `e281_a_binding_moved_on_some_paths_is_recorded_so`.
  - `e282_an_invalidation_follows_the_paths_and_the_loops_to_a_dbg_stack_call`.
  - I planted the bug three ways (no record, no loop handling, no per-arm handling) and each pin went red.
- **Where the item text was wrong:**
  - The view scan never kept a "dead view" state to read; I had to add one, along with the arm and loop tracking.
  - A capture view with zero uses in its arm never enters the live set at all, so it counts as already past its last use.
  - The two scans run inside M19 T1's Class A window, which skips reused modules. So B575's rule applies: a module holding a `dbg_stack()` call is marked unrecordable, and both records are re-derived on every analysis (question 1).

### Item 2 — S2 `dbg_stack()`: done
- **What it does.** The expansion (`expand_dbg_stacks`, in the new file `analyzer/dbg_stack.rs`) runs after every check and before the last-use dataflow. It lists:
  - parameters and locals, innermost scope first;
  - each shadowed binding directly under the one hiding it, as `x (shadowed at L:C)`;
  - inside a closure, its own bindings and then only the bindings it already captures, marked `(captured)`;
  - views as `view T (a view into rows)`.
- **What it does not read.** These print a fixed text instead of being read:
  - `<moved at L:C>` and `<moved on some paths>`;
  - `<view, invalidated by push at L:C>` (or `by assignment`);
  - `<pipe, not sampled>`;
  - `<lazy, not forced>` for a lazy parameter (my addition).
- **Cells and liveness.** Cells print their value without tracking: a `set` on a captured cell does not re-run the effect. Every binding it reads becomes a minted `Ref` argument, so it counts as a use at the call.
- **Backends.** The line text is spelled once, in `printer.rs`. Both backends print byte-identical output. Release builds refuse it, and `[build] dbg = "strip"/"keep"` apply as for `dbg`.
- **Pins:**
  - 10 `inference::debugging::s2_*` pins.
  - `native_differential::s2_dbg_stack_prints_the_scope_the_same_on_both_backends`.
  - `infer_preset::a_release_build_refuses_strips_or_keeps_a_dbg_stack_as_dbg`.
- **Where the brief was wrong:**
  - "Captured by clone" is not something the analyzer knows about closure captures (the capture plan is about pattern captures), so closures say only `(captured)`.
  - In a generic body, a `T`-typed binding that is moved where an instantiation makes `T` a resource now prints as moved in every instance. Reading it would make the resource instance clone a resource; I saw a double drop before fixing this.
- **Also fixed:** on JS, `dbg(view)` of a scalar view printed the `(base, key)` pair (`first = 0,1,1`), where native printed `1`.

### Item 3 — E283: done (one native gap)
- **std `Debug` impls**, spelled as `dbg` prints them:
  - `HashMap` and `HashSet`, in insertion order;
  - `Shared`, with `<cycle>` when a cell is met again inside its own rendering (this uses one module-level cell in `shared.vl`, which added a row to the shared census);
  - `SignalCell`, read without tracking;
  - `BigInt`.
- **Derive changes.** Closure fields and payloads print their written type. Fixed-array fields with a literal length print element by element, nested and empty arrays included. `debug.vl` gains no import.
- **Not covered.**
  - `T: Debug` over `[T; n]` waits on array-lengths S2.
  - A bare closure still refuses `T: Debug`.
- **BigInt natively.** The `BigInt` impl is JS-only for now: the native backend cannot render a `BigInt` as text at all (filed as F?1).
- **Pins:**
  - `e283_the_derive_takes_stds_handles`.
  - `e283_the_derive_prints_a_closure_and_a_literal_length_array_field`.
  - `e283_t_debug_takes_stds_handles_and_cuts_a_cycle`.
  - `native_differential::e283_debug_takes_every_type_dbg_prints_on_both_backends`.

### Item 4 — S3: measured, then built
- **Measurement.** I prototyped the analyzer's recording of each non-number `print` argument's type and compared release builds, counting user-space instructions.
  - The eleven ci rows plus genapp and plain: between +0.000% and +0.034% against the build without it.
  - kolt `vilan check`: +0.11% at the median, against a 0.4% spread between runs, so within noise.
- **What it does.** `print` of an aggregate now writes `dbg`'s printer output on one line:
  - a struct, enum, option, tuple, list, map, set, `Shared`, cell, pipe or `dyn`;
  - a float inside keeps its `.0`;
  - a backed enum prints its name (`Color::Red`, `Ordering::Less`).
- **What does not change.** Top-level numbers, strings and bools print as before. Host values and a bare closure still go to `console.log` (question 3).
- **Interpreter.** The macro engine's interpreter gained the printer's document helpers, so its equivalence suite stays green.
- **`inspect.rs`** stays: it still renders the values `print` keeps.
- **Estate:**
  - kolt 0 sites, website 0, examples 0;
  - corpus 9 programs, every runtime diff reviewed;
  - 34 test expectations updated: the outputs moved to the new format, and the backed-enum lowering pins now print `.value()`.
- **Pins:**
  - `s3_print_writes_an_aggregate_through_the_printer_on_one_line`.
  - `s3_print_of_a_generic_value_and_a_dyn_prints_per_instance`.
  - `native_differential::s3_print_writes_aggregates_through_the_printer_on_both_backends`.

### Goldens that moved
- **Corpus `.mjs`, in S3 only:** `adapt`, `default`, `dyn-objects`, `enum-discriminant`, `format`, `gap-b`, `generic-inference`, `iterator-adapters`, `trait-default`. Re-judged after the rebase: 0 moved.
- **New native fixtures:** `native/dbg_stack.*`, `native/debug_handles.*`, `native/print_aggregates.*`. No existing native golden moved.
- **`markdown_anchors.golden`** (in S2): two new headings, regenerated with mdbook 0.5.4.
- **I kept a std location stable on purpose.** The corpus embeds `reactive.vl` line numbers, so `SignalCell`'s `Debug` impl and its import sit at the end of that file.

### Perf
- **The analyzer changes cost nothing.** My compiler changes measure x0.9994–x1.0002 against the base: the records and the expansion are free without a `dbg_stack()` call.
- **The cost is in std.**
  - Rows: math +0.66%, watch +1.0%, the rest +0.17% to +0.45%, plain:320 +1.69%.
  - Cause: every generic `.debug()` call that std adds pays O(all `Debug` impls) inside `async_infer::dispatch_candidates`, which also dedups quadratically. I confirmed this with callgrind and filed it as M?1.
  - Hence the twelve ci `[[bump]]` rows (x1.004–x1.013, item M120).
- **`scripts/ci-local.sh perf` after the rebase:** T2 green, growth x2.021.

### Gates on the rebased tree
- `cargo nextest run --workspace`: 9996 passed, 33 skipped.
- `VILAN_NATIVE_DIFFERENTIAL=1 native_differential`: 224/224.
- clippy `-D warnings`, `cargo fmt --check` and `vilan fmt --check .` are clean.
- The full suite includes `corpus`, `check_scope_differential`, `edit_replay_differential`, `permutation_differential`, `ci_ignored_pins` and `hygiene`.

### Pass map
I edited `proposal/analyzer-pass-map.md` §3 in the proposals repo; it is uncommitted, for you to commit. The edits are new rows for `mark_dbg_stack_modules_unrecordable` and `expand_dbg_stacks`, plus the record writes added to the `check_invalidation`, moves and R11 rows.

### Finds filed
In `sweeps/order49/newitems49-debug.json`; repros are under `sweeps/order49/debug-49/finds/`.
- **F?1:** native renders no `BigInt` as text.
- **F?2:** `print(caller())` natively is passed to rustc and fails with E0277, instead of a named refusal. It reproduces on the base too.
- **M?1:** `dispatch_candidates` scans every impl per generic trait call site, with a quadratic dedup.

### Questions for the owner
1. **B575 by recompute.** Modules that hold a `dbg_stack()` call are never recorded for reuse, rather than carrying the two records in M19's record. Recommend keeping this: debug code is transient, and the cost is zero otherwise. incr-49 should confirm.
2. **S3's family.** I marked it `breaking` because program stdout changes, following debug-48's E275. Recommend keeping it, or reclassify it as `feature`.
3. **Bare closure under `print`.** It still goes to `console.log` on JS and is still refused natively (F25), while a closure inside an aggregate prints its type on both backends. Recommend a follow-up that prints `<closure …>` on both and retires F25's function half.
4. **Generic moved bindings.** In `dbg_stack()`, a binding moved in any resource instantiation prints as moved in every instance. Recommend accepting this.
5. **The ci bumps.** All are under 3%, so no approval is needed. Recommend fixing M?1 next order and re-taking the rows at the seal.
6. **Files outside my ownership, edited without integrator sign-off.**
   - `interpreter.rs`: I added the printer's document helpers, which S3 needs.
   - `vilan-cli/src/main.rs`: one call to the `dbg_stack()` release refusal.
   - `vilan-rust/src/lib.rs`: the `print` and `dbg_stack()` dispatch lines.
   - Recommend the integrator check these against native-49's and incr-49's maps.
7. **The perf commit.** `d3743fad`/`d869ff85` touches `perf/budgets.toml`, which is your domain. Drop or reword it as you prefer; without it the ci rows likely refuse on math and watch.
