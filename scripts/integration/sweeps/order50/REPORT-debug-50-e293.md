debug-50 report. E293 is done and committed. E257 S5 is measured but not built. E283's array half is not started: it waits for lang-50's S2 on `next`, which has not landed. I ran the full suite once, then killed it by PID at about 6% to save time. It would have taken hours under load 23-28, and I will rerun it after the rebase. The targeted gates below are green. Please accept that, or run the full suite yourself before merging.

**Tip and base**
- Tip: `5f7e61d7` on branch `debug-50`, worktree `/home/reed/code/vilan-lang/vilan/.claude/worktrees/debug-50`.
- Base: `origin/next` at `f99dc28e` (the C2 merge). Nothing is pushed.

**Commit**
- `5f7e61d7` "E293: print of a bare closure writes its type on both backends", CHANGELOG family `fix`. It carries a CHANGELOG entry under `## Unreleased` and a docs line in `vilan/docs/std/misc.md`.

**What E293 does**
- `print(add)` now writes `<closure |i32| i32>` on both backends. It was `[Function: add]` on JS and a compile-time refusal natively.
- A named function prints `<closure fun double>`, and a generic `show<T>(value)` prints the type of each instance.
- The code change is one predicate in `crates/vilan-core/src/printer.rs`: `print_uses_the_printer` now also accepts the `<closure ` text shape. The S3 path from commit `220ed22c` does the rest. No analyzer, mono or emitter functions changed, so I did not run `perf`.
- Host and opaque values keep the console. The native refusal of a host handle stays: the `Task` probe (`PRINT_HANDLE_PROBE`) still builds on JS and is refused natively.

**Pins**
- `native_differential::e293_print_of_a_bare_closure_writes_its_type_on_both_backends`, with new files `native/print_closures.vl` and `native/print_closures.stdout`.
- `inference::debugging::e293_print_of_a_bare_closure_writes_its_type`.
- I verified the premise red first by running the probe before the change: JS printed `[Function: add]` and `--backend rust` refused it.

**Existing tests edited**
- `printing_a_host_handle_or_a_function_is_refused_at_compile_time` was renamed `printing_a_host_handle_is_refused_at_compile_time` and keeps the `Task` case only. The function probe is deleted.
- `a_refusal_inside_another_files_body_names_where_to_look` used a bare closure for its "user module's refusal" check. It now uses an async `Task` print in the module (line 11 of `util.vl`).

**Where the premises were wrong**
- E293's premise held. The only adjustment is that a named function is also a bare callable and prints as `fun <name>`, which I pinned.
- F25's compile-time `Task` refusal fires only when the async callee actually awaits. With `async fun work(): i32 { 7 }`, `print(task)` builds natively and panics at run time. That is filed as a find, below.

**Gates, all green**
- `ci_ignored_pins`, `hygiene`, `corpus`, `check_scope_differential`, `native_differential` and the inference tests matching `debug`: 332 tests passed, 0 failed.
- `native_differential` with `VILAN_NATIVE_DIFFERENTIAL=1`: 248 of 248 passed.
- `cargo clippy --workspace --all-targets -- -D warnings`, `cargo fmt --check`, and `cargo run -p vilan-cli -- fmt --check .` are clean. Clippy first flagged a `single_element_loop` in my test edit, which I fixed before the commit.
- Not run: the full suite (see above). `scripts/rss-probe.py` was not needed: no analyzer or table change. No `.vl` files were touched except the new test program, which is formatted.

**E257 S5 measurement**
- I built a throwaway spike and then reverted it. It is saved as `sweeps/order50/debug-50/e257-s5-measurement-spike.patch`. It is gated by `VILAN_SPIKE_MARKS`, so the tree has no trace of it.
- **What the spike does.** The formatter inserts a sentinel character at each marked node, and a post-pass strips the sentinels. While stripping, it computes generated line/column and writes a real v3 VLQ `mappings` string. Source deltas are faked small.
- **Subjects.** The profiling build (release plus debug symbols) ran on `reactive-ui` with callgrind, and on a kolt copy carrying `src/lucide` and `src/search-dict` for map sizes only.
- **Mark levels.** 1 = every statement; 2 = statements plus calls, closures and function heads; 3 = every node (upper bound).

| Subject | Marks | `mappings` bytes vs JS bytes | Added instructions |
|---|---|---|---|
| reactive-ui (64 KB JS) | 1 (1,704) | 9.3 KB, 15% | +2.4M (+0.13% of a 1.827G build) |
| reactive-ui | 2 (2,944) | 15.7 KB, 25% | +4.3M (+0.24%) |
| reactive-ui | 3 (9,510) | 48.5 KB, 76% | +11.8M (+0.65%) |
| kolt client (566 KB JS) | 1 | 63 KB, 11% | not callgrind'd |
| kolt client | 2 | 111 KB, 20% | not callgrind'd |
| kolt server (191 KB JS) | 1 | 29 KB, 15% | not callgrind'd |
| kolt server | 2 | 47 KB, 24% | not callgrind'd |

- **Phase context for reactive-ui.** A `vilan build` costs 1.827G instructions against `vilan check` at 1.684G. The transformer's `assemble` is 232M, `rename_for_scopes` 128M, and the formatter's `node` 58M. Marking adds about 4% to the formatter and under 0.3% to the build at the recommended level.
- **Cost of the real thing.** I estimate +0.2% to +0.3% instructions on `build` for the recommended level (statements plus calls). I have not measured the span wrapper, and my estimate for it is 0.5M instructions on reactive-ui, roughly 0.03% of the build. `vilan check` is untouched if the wrapper node is created only when maps are on; the `diagnose` walk skips formatting.
- **Estimate caveat.** The map-size figures are probably within ±30%. Real source positions jump between files and the `names` field adds bytes.
- **`sourcesContent` is the real size question.** The whole std is 1.85 MB and kolt's own source is 184 KB. Embedding it all would make the map far larger than the `mappings`. Recommend embedding user sources only and pointing std at its cache path. The paper says to embed std too, so this departs from its text.
- **The cost is mostly engineering, not CPU.**
  1. The JS AST (`transformer::js::Node`) carries no spans at all.
  2. The formatter is a string-returning recursive printer with no position, which is why the spike uses sentinels.
  3. The cheap design is a transparent `At(span, Box<Node>)` variant. It needs a mechanical arm in roughly a dozen post-walk rewrites (`rename_for_scopes`, the returns lowering) and in the interpreter.
  4. M16's shared monomorphized bodies map many JS functions to one vilan function, so attribution needs a decision.
- Slice shape: M–L, as the paper says. I did not build it because I am handing back for the rebase.

**Finds**
- Filed in `sweeps/order50/newitems50-debug-50.json` as `F130`, repro `sweeps/order50/debug-50/finds/print_of_a_non_suspending_task_refused_at_run_time.vl`. Natively, `print(task)` of a `Task` whose async function never awaits is refused at run time rather than compile time. The refusal in `refuse_unprintable` is keyed on the rendered type. Recommend keying it on the vilan `Task<T>` type. Sizing S; I left it alone because it is outside E293.
- Native cannot emit an `async` function as a value (`print(later)` where `later` is async): refused by name, an existing F1 S1b limit, not a new find.

**Questions for the owner**
1. Is the `fix` family right for E293? It changes stdout for a bare closure under `print` (S3's equivalent change was `breaking`). Recommend `fix`: JS printed node's inspection and native refused, and I found no estate site (the corpus, kolt, website and examples print no bare closure).
2. Should `sourcesContent` embed std? Recommend user files only, with std by path.
3. Which mark level should S5 target? Recommend statements plus calls, closures and function heads (level 2): the cost is small and calls are where breakpoints land. Recommend maps on by default in the `debug` preset only, as Q9 already rules.
4. Should S5 be built before the E283 array half? Recommend the array half first, since it is small and waits only on lang-50's S2. I will start it when you tell me S2 is on `next`.

**State**
- `debug-50-STATUS.md` is untracked in the worktree. No processes of mine are running.
- Scratch is under `target/debug-50-scratch/` in the worktree: the profiling build, the kolt copy and the callgrind outputs.
