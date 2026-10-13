## native-52: final report

F135, F136 and F137 are done. B617 was not taken because the analyzer core belongs to incr-52a. I also fixed two of my own finds (F?2 native, F?3 JS) and filed two more (F?1, F?4). Every gate is green at the tip.

**Branch `native-52`, tip `757c784a`, base `697c9517`.** Nothing is pushed and I have not rebased. Each commit carries its own `## Unreleased` entry with a family marker (6 commits, 6 entries). `native-52-STATUS.md` is untracked and current. No processes are left running.

### Commits
| commit | item | family |
|---|---|---|
| 1092eaf2 | F135 slice 1: `read()` copies where it is evaluated, on both backends (R-a door 1) | fix (estate 0) |
| f58b1c60 | F?2 (my find): natively a scalar `&` view of a captured binding now waits for the later arguments | miscompile |
| 5e82daa6 | F136: an aggregate holding a map of closures builds natively | fix |
| 04a2bb2b | F137: a generic enum's derived `PartialEq` builds natively | fix |
| d2771ee4 | F?3 (my find): on JS, a `&mut self` call on a read's field (`cell.read().items.push(9)`) no longer writes the cell | miscompile |
| 757c784a | F135 slice 2: one `[derive]` expansion's span never contains another expansion's write | fix |

### F135, as ruled
- **Estate: 0.** I built kolt (a copy with lucide), the website's `src` (all four entries) and all eleven examples with the base and tip binaries and diffed the output: byte-identical. 0 corpus goldens moved, and kolt's native server emission is byte-identical to 0.49.0. So the family is `fix` and no kolt patch is needed.
- **JS side.** The analyzer copies a `read()` argument (a bare read, a field/slot/element of one, a receiver, or the operand of a `&`) when a later argument of the same call can write that cell in place. This applies whatever the callee is, a closure value included. A `&` of a read's scalar field is now a holder of the value read at that point, not a `(base, key)` pair over the cell's storage.
- **Native side.** F129's copy-last is reverted for `Shared` reads. F123's std lookup no longer takes its view when `clone_sites` marks the receiver.
- **Spec and docs.** §6.7 gains the rule paragraph, and std's cells page says to read after the write to see it.
- **Both repro shapes now match.** `has(cell.read().items, grow(cell))` prints `false` on both, and the field-replacement shape prints the old length on both.
- **Pins.** The F129 pins are kept with their expected output updated (both backends' stdout is now asserted). F135's pin is un-ignored. There is one new native probe and three new inference pins.
- **Slice 2 was needed because slice 1 turned two std performance pins red.** M87's `KeyedCell::locate` copied its whole index on every call, and A54's per-change cost grew 14x for ten times the rows.
  - The cause was a pre-existing imprecision in B457's span test. Every derive expansion shares `DERIVED_SOURCE`, and their spans overlap by accident, so a derived `hash` looked like a writer of every written cell.
  - Scoping that test to one derive expansion fixes it, and both pins are green again.

**Integrator: the `read()` copy seam (tell std-52).**
- `walk_entity_inner`'s `Expr::Call` argument closure: the `&`-operand copy, placed just before the `own` comment.
- `scalar_view_of_place`: the read-spine holder.
- New `is_a_shared_read_spine`.

### Where the premises were wrong
- **F135 is two rules, not one.** Its `words.measured(swap())` repro is spec §6.9's view of a captured binding, not §6.7's `read()`.
  - I kept F129's late copy for captured-binding cells: that is §6.9's stated order, and the in-place shape prints 2 on both backends.
  - The rebinding shape stays apart: natively 3, on JS 1. I moved it to its own ignored pin and filed it as F?1. The ignore reason leads with `F135`; please retarget it to F?1's allocated id.
- **F137 was native, not the solver.** The analyzer records nothing at all for a tuple literal (not an open type). The native emitter now types a tuple-literal scrutinee from its elements (`tuple_literal_type`).
- **F136 held as written.** I added `ReferenceEq` for `Map` (order-insensitive, matching std's `HashMap` equality) and for its `(key, value)` entry. The refusal message now lists the new shapes.
- **B617:** what it needs is in `context.rs`'s dispatch candidates (`dispatch_refine::known_receiver_candidates` / `candidates_of`). A `dyn` call's candidate set must include the blanket impl over a bounded generic, so the declaration threads its `start`'s `turn_scope` and `ambient_nursery`. B606's `None` in vilan-rust's object table can then retire where that union answers.

### Gates (at 757c784a)
- **Full suite** (`--cargo-profile ci-test -E 'not binary(deep_nesting)' -j 6`): 10528/10528 passed, 32 skipped. This includes the vilan-lsp binary and both native censuses.
  - Within it: `ci_ignored_pins` 12/12, `hygiene` 3/3, `corpus` 14/14, `check_scope_differential` 16/16, `native_differential` 275/275.
- **Native sweep mode:** 275/275. The triple is 130/128/2/0, unchanged from base; platform-bound 9/6/3/0 and async 7/4/3/0.
- **Deep-nesting canary at 1536 KiB:** 18/18.
- **clippy** (`--workspace --all-targets -D warnings`), **`cargo fmt --check`** and **`vilan fmt --check .`**: all 0.
- **`ci-local.sh perf`:** T2 green, growth x1.930. kolt late-writes=0.
- **kolt cold-check RSS:** median 277,972 KB at tip vs 275,344 KB on 0.49.0, +0.95%. The machine was under load and the run spread is wide.

### Functions changed
- **analyzer.rs** (incr-52a's file; these are the listed arms):
  - `compute_clone_sites`: its `Call` arm gains the F135 loop, and its B274 receiver test now asks for the read spine.
  - New: `shared_read_spine_cell`, `reaches_an_in_place_write`, `one_span_space`.
  - Changed: `spans_an_in_place_write`, `spans_a_call_reaching_a_write`, `function_reaches_an_in_place_write`.
- **transformer.rs:** `walk_entity_inner` (the `Expr::Call` argument closure), `scalar_view_of_place`, new `is_a_shared_read_spine`.
- **vilan-rust:**
  - Changed: `call_arguments_adapting`, `defers_its_cell_copy`, `reference_equality_reaches`, `check_reference_equality` (its message), `settled_value_type`.
  - New: `views_as_a_pair_on_the_js_backend`, `tuple_literal_type`, `split_at_the_top_level_comma`.
- **vilan-rt:** `ReferenceEq` for `Map<K, V>` and for `(K, V)`, plus one unit test.
- **mono.rs:** untouched.

### Finds
They are in `sweeps/order52/newitems52-native-52.json`, the path the updated brief names. Repros are in `sweeps/order52/native-52/finds/`, which is the directory you prepared; the brief still says `order51` for repros, and I moved them there.
- **F?1:** the captured binding rebound by a later argument (open; owner question 1).
- **F?2:** fixed here (f58b1c60).
- **F?3:** fixed here (d2771ee4).
- **F?4:** an assignment through a read (`cell.read().count = 3`) writes the cell on JS and a lost copy natively. Recommendation: a checker refusal steering to `write()`. That is the analyzer's checks, not mine.

### Questions for the owner
1. **F?1, the binding half of F135.** Should JS take a captured `mut` binding's view or place argument after the call's later arguments, as §6.9 already orders it? That would mean hoisting the later arguments into constants when they run code. **Rec: yes.** Only the order of a side-effect-free binding read changes. It needs a JS-side table of captured `mut` bindings, so it is analyzer plus transformer work for next order, with an estate count first.
2. **F?4.** Should an assignment through `read()` be refused by the checker ("`cell.read()` is a copy, so this assignment is lost; write through `cell.write()`")? **Rec: yes**, as a `diagnostics` item with an estate count (expected 0).
3. **B457's write summaries are coarse.** Any call through a closure value counts as "may write any cell that is written somewhere". F135 inherits this, and std's hot paths only stayed clean after the derive-span fix. **Rec:** keep it conservative for now, and file a precision item: a closure-literal write summary in place of "any write".
4. **B617:** take it in solver-52 at C1 as the brief already plans, with the needs described above. **Rec: yes.**
