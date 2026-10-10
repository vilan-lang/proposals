## native-50: final report

All seven items are done. The whole-set native triple went from **130/127/3/0 to 130/128/2/0**. Two of the items turned out to also fix silent wrong answers that were already on the base, so their entries carry the `miscompile` marker.

**Tip `9610e079`** on branch `native-50` (worktree `vilan/.claude/worktrees/native-50`), rebased onto **origin/next @33444b25** after your note. Nothing is pushed. There are 8 commits, each with its own `## Unreleased` entry and family marker; I counted them after the rebase and none was lost. The rebase hit conflicts only in CHANGELOG.md. My entries now sit after tools-50's, separated by `---`. `LANE-STATUS.md` is untracked and current.

### Items
| item | state | commit | pin |
|---|---|---|---|
| F126 | DONE (fix) | 2614c183 | `f126_print_of_a_location_writes_its_text_on_both_backends` |
| F128 | DONE (fix) | d7d1b2f0 | `f128_a_dereference_of_a_value_binding_reads_the_value_on_both_backends` |
| F127 | DONE (fix) | 49cb53e9 | `f127_a_spread_of_a_tuple_literal_is_its_parts_on_both_backends` |
| F125 | DONE (miscompile) | f76a5e10 | `f125_a_bigint_as_text_writes_its_digits_on_both_backends` |
| F123 | DONE (miscompile) | de2a340b | `f123_a_std_lookup_over_a_shared_views_field_reads_in_place_on_both_backends`; F114's emission pin now expects 0 copies |
| F122 | DONE (fix) | 9025b5e6 | `f122_a_fixed_array_past_one_kib_lives_on_the_heap_on_both_backends` |
| F124 §2.1 | DONE (feature) | 97b82fc8 | `f124_a_nested_loan_group_reborrows_on_both_backends` |
| F124 §2.2 | DONE (feature) | 9610e079 | `f124_an_interleaved_loan_group_shares_one_cell_on_both_backends`, `f124_two_loans_in_one_call_and_a_projected_interleaved_view_are_refused_by_name` |

Where the item text was wrong, or more was going on:
- **F126:** `vilan_rt::Location` now prints as its text at the top level, as JS does. Inside a list or an `Option`, the printer already writes `<Location>` on both backends. Interpolating a Location (`i"{site}"`) is refused by the checker on both backends, as before.
- **F128:** the premise was half wrong. `filter`'s predicate is `|T| bool`, so the element arrives by value, and the checker accepts `*` on a plain value (JS treats it as the value). The fix: a `*` over a by-value parameter, or over a local whose initializer is clearly a value, emits the value itself. A binding misjudged as a value can only fail rustc's build, never change an answer.
- **F127:** a spread of a tuple literal now contributes its parts directly, each written at its slot's type (`3.0f64`), evaluated once and in order, nested spreads included.
- **F125:** this had a silent wrong answer on 0.47.0. `i"{big * big}"` printed `144n` natively against JS's `144`, and `"x" + (big + 1n)` printed `x13n`. An operator's result records no type, so it fell through to node's `n`-suffixed rendering. A `BigInt` in a concatenation now renders through a new `vilan_rt::bigint_text`.
- **F123:** also a silent wrong answer on the base. `cell.read().seen.contains(mark(cell, "late"))`, where `mark` inserts `"late"`, printed `false` natively and `true` on JS. The copy of the set was taken before the argument ran.
  - `HashSet::contains`, `HashMap::get` and `contains_key` now read through the cell, with the borrow taken after the arguments, when the key hashes with std's own code (scalars, `str`, `BigInt`, `bool`, and tuples, arrays or `List`s of those).
  - A user key type, whose own `hash` could touch the cell, keeps the copy.
  - The general version of the early-copy bug is filed as F129 (below).
- **F122:** the array type stays `[T; N]`. Past the threshold it renders as a new `vilan_rt::HeapArray<T, N>`, which derefs to the array, is built on the heap and clones element by element. (A plain `Box<[T; N]>` would still build its clone on the stack.) A slot-by-slot pattern over such an array is refused by name.

### F122's threshold: 1 KiB (1024 bytes, estimated as element size × length)
Measured on a debug build with the 8 MB main stack:
- An inline array costs 4 to 5 copies of itself in the frame that builds it: `[0; 400000]` ran, `[0; 500000]` overflowed.
- Recursion pays that again in every frame. A function holding a local `[i32; 256]` (1 KiB) recursed past 7000 frames natively; node itself fails between 5000 and 7000.
- At `[i32; 512]` (2 KiB), the native build overflowed at 5000 frames while JS answered.

So 1 KiB is the largest size where an inline array costs no recursion depth compared with JS. `[i32; 256]`, `[u8; 1024]` and `[str; 64]` stay inline; `[i32; 257]` goes to the heap. `[0; 4000000]` now runs.

### Triple after each step
- 130/127/3/0 at base, after F126, after F125/F127/F128, and after F122. F123 was checked in default mode only; it cannot change what is refused.
- 130/128/2/0 after F124 §2.2, and again on the rebased tip. transparent-references.vl flipped.
- **The two still refused:** async-await.vl (the host `sleep`) and signal-update.vl (a closure given a `&mut` view that re-reads the same place).
- Both native modes ran at every gate. The copy and leak censuses match their tables and did not move.

### F124's two lowerings, and what each bought
The emitter groups each root binding with its view bindings. Only groups that contain an alias are touched. It walks each function body once to get the order of accesses (a `let` counts after its initializer; a binding touched in a loop counts again at the loop's end).
- **§2.1, nested intervals** (no view's parent touched while the view lives): the alias becomes `let c = &mut *b;`, a plain Rust reborrow with zero run-time cost. A shared view's alias copies the `&`. This makes every forwarding shape build; it flips no corpus program on its own.
- **§2.2, interleaved:** the root moves into the existing `Captured` cell and each view becomes a handle on it (`let b = a.clone();`, the same cell). Reads, writes, `&mut` calls and compound writes are momentary borrows. A compound write through a `borrows` call settles its value before borrowing. This is what flipped transparent-references.vl. The cost is one heap cell per promoted root and a borrow check per access.
- **Still refused by name:**
  - a call given two loans of one promoted root, one of them `&mut` (it would abort at run time);
  - a view of a field, element or slot of an interleaved root;
  - a view that a closure names;
  - a group in an `async` body;
  - a view bound from a `borrows` call over a group member.

### Gates
- **Full suite:** 10167 / 10167 passed (31 skipped) on the rebased tip, and 10161 / 10161 before the rebase.
- `native_differential` in both modes, the corpus, `ci_ignored_pins` and `hygiene` passed after every item and again after the rebase.
- clippy `-D warnings` and `cargo fmt --check` are clean.
- **`scripts/ci-local.sh perf`:** T2 green, growth ×1.931. I changed no analyzer code, so the pass map is unchanged.
- **Functions changed in vilan-rust:**
  - existing: `rust_type_inner`, `spread_tuple`, `as_string`, `declaration`, `assignment`, `place_lives_in_a_cell`, `binding_holds_a_view`, `names_a_mutable_loan`, the call-argument path, and the Repeat, List and const-array arms;
  - new: `dereferences_a_value`/`local_holds_a_value` (F128), `std_lookup_runs_no_user_code`/`hashes_without_user_code` (F123), `holds_a_bigint` (F125), `estimated_size`/`array_lives_on_the_heap` (F122), `compute_loan_groups`, `log_accesses`, `loan_interleaves`, `loan_group_refusal`, `refuse_two_loans_of_one_promoted_root` (F124).
- **Caveat:** §2.1's own commit got only its pins checked in isolation. Its gate run picked up the §2.2 source edit halfway through, so that run actually tested the later code. The tip itself is fully gated.

### Finds filed
In `sweeps/order50/newitems50-native.json`, with repros under `sweeps/order50/native-50/finds/`:
- **F129 (miscompile, native):** an argument read through a `Shared` view is copied out of the cell before a later argument that writes the cell runs. `has(cell.read().items, grow(cell))` prints `false` natively and `true` on JS, silently.
- **B604 (checker):** a closure parameter over the result of a `.map` is not checked. `let probe: str = length` passes the checker where `length: usize`; rustc then refuses it natively.

### Questions for the owner
1. **F122's threshold:** keep 1 KiB? I recommend yes: it is measured, and it keeps native recursion depth at or beyond node's. 4 KiB would cost about half that depth for programs with array locals.
2. **F129's fix:** I recommend the next native order evaluates the later arguments first and takes the cell copy last, the order the spec's §6.9 native note gives for views. F123 already does this for the three lookups.
3. **F124 §2.3:** should a view into part of a cell get a lens handle (`vilan_rt::Place<T>`)? I recommend waiting for a real program. Nothing in std, kolt or the corpus writes the shape.
4. **`*` on a plain value** (found during F128): the checker accepts it, though rule R6 only defines `*` on views. Should it warn? I recommend a non-breaking steer rather than an error.

The proposals-repo files (the finds and the json) are for the integrator to commit.
