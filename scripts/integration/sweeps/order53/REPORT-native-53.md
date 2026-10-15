## native-53: final report

F138 is done as ruled (R-a door (1)) and B634 is done. I also fixed one find of my own (F?1, closure-value calls) and filed two more (B?2, F?3). F124 §2.3 stays deferred: no real program in my probing needed it (the corpus, kolt's server, the website server and the examples all emit natively with no loan-group refusal). Every gate is green after the rebase.

**Branch `native-53`, tip `f6c3f808`, rebased onto `origin/next` @ `fe19e1c1`** (as you asked; original base `b923bfc6`). Nothing is pushed. The rebase hit only CHANGELOG conflicts, and every entry kept its family marker. `native-53-STATUS.md` is untracked and current. None of my processes are running.

### Commits
| commit | item | family |
|---|---|---|
| 52a38b65 | F138: on JS, an argument rooted at a captured binding is read after the later arguments | miscompile |
| 41e7a705 | F?1 (my find): the same order through a closure VALUE, on both backends | miscompile |
| 951a1d7c | B634: a closure literal's body is its own write summary | performance |
| f6c3f808 | F138 slice 2: the capture table is built per emitted function, walking each closure body once (`vilan check` cost); the corpus program joins `corpus_manifest!` | (F138's entry) |

### F138, as ruled
- **The rule on JS.** An argument rooted at a captured `mut` binding now waits for the call's later arguments when they run code. This covers a `&self`/`&mut self` receiver, a `&` view, a `&mut` place, a by-value place of a value JS hands on by reference, and an intrinsic's viewed or written receiver.
  - The call's other unsettled arguments are bound to `const`s in order first. B452's spill now leaves a waiting argument alone.
  - It mirrors the native emitter's decisions (`takes_a_cell_view`, `defers_its_cell_copy`, and the intrinsic paths) rather than inventing a JS-only rule. So the controls still read where they stand on both backends: a scalar, `str`, `Option`, tuple or enum by value; an `&Option` beside a closure that writes it; an uncaptured binding; an operator operand.
- **The capture table** is `vilan_core::captures`, a new module outside the analyzer core. It is not a listed arm in `analyzer.rs`.
  - The closure scan, its children list and the table moved out of vilan-rust, which now delegates to the module. The native emission is byte-identical: all 146 corpus programs and kolt's server (473 KB) diffed.
  - The table walks each closure body once, memoizing nested closures. The old scan re-walked a nested body for every closure around it.
  - The transformer asks the table per emitted function, finding the function's closures by span. A module-level binding falls back to the whole-program table.
- **Estate: 0.** No program in kolt, the website, the examples or the corpus has a later argument that rebinds a captured binding.
  - JS output moves at four sites, and none of them rebinds: std's keyed splice (`olds.push(keyed_element(..))` and `olds[index].store_diff(..)`), kolt's `ops.push(seed_or_gone(..))`, and the website server's `wasm_pairs.push(..)`.
  - 0 corpus goldens moved. There is one new corpus program, `captured-argument-order.vl`, with witnesses and a census row of +2.
- **Repros.** `words.measured(swap())` and `words.measured(more())` print 3 and 2 on both backends.
- **Pins.**
  - `f135_a_later_argument_that_rebinds_…` is un-ignored and renamed `f138_a_later_argument_that_rebinds_a_viewed_captured_binding_answers_the_same_on_both_backends`.
  - New `f138_an_argument_rooted_at_a_captured_binding_is_read_after_the_later_arguments_on_both_backends` covers nineteen shapes, including the by-value twin `has(log.items, rep())`. The base JS differed from native on 15 of them.
  - The corpus witnesses.
- **Docs.** Spec §6.9 has its JavaScript note.

### B634
- **The change.** A call through a closure literal now answers with that literal's own write summary. That covers a literal applied where it is written, or one named by an immutable `let` through immutable aliases. A parameter, a field or a `mut` binding keeps the conservative answer.
- **Census.** I counted F135/B457 copy decisions before and after, using temporary instrumentation that is not committed:

| estate | before | after |
|---|---|---|
| kolt | 86 | 86 |
| website | 58 | 58 |
| examples | 304 | 304 |
| corpus | 85 | 85 |

  - The shape B634 sharpens does not occur anywhere in the estate, and its JS is byte-identical.
- **Pins** (each named `b634_…`):
  - writes nothing → no copy. This one is red without the change.
  - writes its cell → copy kept.
  - unknown closure value → copy kept.
- **Perf:** within +0.035% on every subject (the worst is fullstack), measured as same-tree release instructions.

### Where the premises were wrong
- **F138 is wider than "a `&`/`&self` view or a by-value place."** Natively, a `&mut` argument and an intrinsic's receiver are also taken late: `log.items.push({log = fresh(); 9})` gave native 1 vs JS 0, and `log.name.contains(..)` and `log.items.get(..)` behaved the same way. JS now follows them too.
- **The "capture table on the JS side" is not cheap to build blindly.** `vilan check` lowers `const` sites and macro code through the transformer. A naive whole-program table cost +0.15–0.55% instructions on the examples. Slice 2 brings that down to at most +0.10% (genapp:46), with the examples at or below +0.05%.
- **F129's order never reached a call through a closure VALUE.** That is native-side and pre-existing (F?1, fixed). A literal applied where it is written binds its arguments as `let`s in order on both backends, which is native's inlining, and that stays as it is.

### Gates (after the rebase, at f6c3f808)
- **Full suite** (`--cargo-profile ci-test -E 'not binary(deep_nesting)' -j 6`): 10642 run, of which 10638 passed and 4 failed.
  - The four failures were one missing roster line: my new corpus program was not in `corpus_manifest!`.
  - Fixed in slice 2. Those four binaries were then re-run in full: 615/615.
  - Within the suite: `ci_ignored_pins` 12/12, `hygiene` 3/3, `corpus` 14/14, `check_scope_differential` 16/16, `native_differential` 285/285, `copy_elision_census` 2/2, and the vilan-lsp binary all passed.
- **Native sweep mode:** 285/285.
  - The triple is 131/129/2/0, against the base's 130/128/2/0 plus the new program, which is identical.
  - Platform-bound 9/6/3/0 and async 7/4/3/0, both unchanged.
- **Deep-nesting canary at 1536 KiB:** 18/18.
- **clippy, `cargo fmt --check` and `vilan fmt --check .`:** all 0.
- **`ci-local.sh perf`:** T2 green, growth x1.929.
- **Same-tree instruction deltas vs b923bfc6** (measured before the rebase):
  - math, watch, browser, canvas, ssr and fullstack: at most +0.01%
  - router +0.024%, rpc +0.030%, reactive-ui +0.041%, todo +0.042%, walkthrough +0.054%
  - genapp:46 +0.104%; plain 160 and plain 320 +0.085% and +0.090%
- **kolt cold-check RSS** (with `MALLOC_ARENA_MAX=1`): median 272,888 KB at tip vs 275,580 KB on the installed 0.50.0, which is −1.0%. The box was at load average 21.
- **`ci-local.sh windows`:** not run, because I added no platform-gated code.

### Functions changed
- **analyzer.rs** (the listed arm, incr-53a's core): `call_reaches_an_in_place_write`; new `closure_literal_body`; doc only on `function_reaches_an_in_place_write`.
- **transformer.rs:** `walk_siblings_in_order` now delegates to the new `walk_siblings_reading_late`. The `Expr::Call` arm calls `arguments_read_late`. There are new `Transformer` fields.
- **New `transformer/argument_order.rs`:** `arguments_read_late`, `closure_value_arguments_read_late`, `reads_late`, `intrinsic_receiver_reads_late`, plus `is_captured`, `function_capture_table` and the other helpers.
- **New `vilan-core/src/captures.rs`:** `expression_children`, `push_expression_children`, `pattern_bindings(_into)`, `closure_parameter_bindings`, `scan_closure`, `captured_mut_bindings`, `closure_captures`, `is_a_mut_binding`, `mutates_its_receiver`, `reads_its_receiver_in_place`. There is one line in `lib.rs`.
- **vilan-rust:** `compute_boxed_bindings`, `closure_parameter_bindings`, `scan_closure` and `children_of` now delegate to `captures`, and the two moved free functions are gone. `closure_call_arguments` defers the copy (F?1), and its two callers pass a prelude. This is beside std-53's `list_to_array`; the rebase was clean.
- **mono.rs and vilan-rt:** untouched.

### Finds
They are in `sweeps/order53/newitems53-native-53.json`, with repros in `sweeps/order53/native-53/finds/`. I checked that both paths say order53.
- **F?1 — fixed here (41e7a705).** A closure value's argument rooted at a captured binding was copied in order natively: `check(items, push())` printed true on JS and false natively.
- **B?2 — open.** A `&mut` receiver over an UNCAPTURED binding, beside a later argument that rebinds its root (`log.items.push({ log = fresh(); 9 })`), checks clean. JS writes the old object, and native is refused by rustc with E0506, reported as a "BACKEND defect". This is a checker hole under rule 4 (§6.4).
- **F?3 — open.** A module-level `mut` binding handed to a call beside a later argument that writes it gives different answers:
  - `has(global, grow())`: JS true, native false.
  - `global.push(reset())`: one item on JS, two natively.

### Questions for the owner
1. **B?2:** should the checker refuse a rebind of a `&mut` receiver's root inside a later argument of the same call, with the steer "settle the value first: `let item = { … }; log.items.push(item)`"? **Rec: yes**, as a `diagnostics` item with an estate count first (expected 0).
2. **F?3:** should a module-level `mut` binding follow F138's order on both backends, read late when a later argument runs code (any call can reach it)? **Rec: yes**, next order, estate counted first. On the native side `defers_its_cell_copy`'s spine would admit a module root; on the JS side `is_captured` would answer true for one.
3. **F138's check-time cost** is at most +0.10% (genapp:46), with the examples at or below +0.05% and everything inside the ci rows' 0.5% tolerance. **Rec: no `[[bump]]` row.** If you want one, it is genapp:46 at 1.002, item F138.
4. **An applied closure literal** (`(|l, v| ..)(items, rebind())`) binds its arguments in order on both backends, as `let`s. That matches native's inlining, and §6.9's JS note now says so. **Rec: keep it.** The alternative would defer like a named callee on both backends, and no program in the estate does this.
