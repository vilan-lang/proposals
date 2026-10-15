## editor-53 report (Order 53, Sonnet 5.5)

**Tip b8ecfee3, base b923bfc6 (origin/next = the v0.50.0 fold), branch `editor-53` in `vilan/.claude/worktrees/editor-53`. Nothing pushed. No processes of mine are running; `editor-53-STATUS.md` is untracked.** E315, E316, E317 and E322 are done and gated. E310's `[hint]`-host note: I never met the need in `hover_blocks.rs` (nothing in this lane's paths reads a trait hover), so nothing was built.

### Commits (oldest first)
| sha | item | family |
|---|---|---|
| e4259301 | E315: the member segment of a written `a::B` path records its type-reference row | fix |
| 10e68c74 | E316: a signature label prints an implicit parameter's bound | fix |
| 88eaddf4 | E317: a generic enum's variant in value position hovers with the instantiation its position settled | fix |
| 84b5e55a | E322: `element_link` reads the desugar's marks | fix |
| b2ee310a | E311's pin updated: `Length` in `padding(style::Length::px(4))` now paints Struct (that pin had asserted the E315 gap) | fix (no entry) |
| b8ecfee3 | E317 follow-up: one pass over the calls, the cache-hot scope test first (measured, see below) | performance (no entry; folded under E317's) |

Each of the four items has its `## Unreleased` entry with a family marker (4 bold heads, 4 markers). The two commits without an entry are a pin edit and a speed-up of E317's own code. The integrator may want to squash b2ee310a into e4259301 and b8ecfee3 into 88eaddf4; `git commit --fixup` needs `rebase -i`, which this environment refuses.

### Where each premise was wrong or incomplete
- **E315:** right as filed, and wider. The row mint is in the drain of the written `a::B` paths (`prepped_type_static_accessors`), which also serves a TYPE ANNOTATION (`x: style::Length` had no row for `Length` either; confirmed red before the fix). A module in the middle of a longer path (`deep` in `lib::deep::Overlay::fresh()`) gets its Namespace row from the same arm.
- **E316:** right. The writer is `signature_type_label` (it lives in `analyzer.rs`, not `hover_labels.rs`), so the lane's edit there is a three-line call into a new `Analyzer::implicit_parameter_bound` in `hover_labels.rs`.
- **E317:** the premise was WRONG in one respect. `Some(1)` and a bound `None` did not read `Option<i32>::…`; EVERY value-position variant read the bare enum, because no variant reference tables a type on its own id (a bare reference is typed by its context, and a call's result is tabled only where something asked for it). E306's instantiation was dead code outside pattern sites. So the fix is a new table, not a fallback to an existing one: `Analyzer::variant_use_labels` reads `expected_types` (return tail, `ret`, annotation), then the type of the binding the value initializes (`Variable::initial`), then the declared parameter of a plain call's argument; a constructor call's label belongs to its callee. No new `Program` field: the labels go into `expr_types`, which records and reuse already restore. A method argument (`h.take(None)`) also works.
- **E322:** the marks have exactly the key the stages have (the `MemberAccessor` entity), so the lookup is direct. But `element_head_links` marks ONLY the head `Chain` links (`.f()`); an event, an attribute and a child are not marked. Those are built on a zero-width name anchor (`elements.rs`), so the new `element_link` is: head is an element (the `<` byte of the head's span, kept because `css { }` blocks also lower to zero-width-anchored links and hint as before) AND (the link is in `element_head_links` OR its recorded member-name span is empty). `title(<b/>)` itself is a type error (an element is no `AttrValue`), so the pin uses `title(Some("a") as Option<str>)`, which ends in a `>` the same way; it was red before (a hint on the head link's line).

### Functions changed in analyzer.rs (the listed arm and two small ones)
- `Analyzer::resolve_world`: the `prepped_type_static_accessors` drain, `Some(member_id)` arm - the E315 row mint (the listed arm).
- `Analyzer::signature_type_label`: E316's early return (three lines).
- `analyze_over_world`: one loop after the label tables calling `variant_use_labels` and inserting into `expr_types` (E317; empty without the reading aids).
- `mono.rs` and the emitters: untouched.
Beyond analyzer.rs: `hover_labels.rs` (`implicit_parameter_bound`, `variant_use_labels`), `written_types.rs` (`element_link`), and the pins in `crates/vilan-lsp/src/editor_review_tests.rs`. `perf` with the analyzer change: late writes unaffected (nothing writes after the build; the new table is read-only over the analyzer).

### Pins (all in `editor_review_tests`)
`e315_a_type_in_the_middle_of_a_module_path_paints_and_hovers` (`style::Length::px(4)`, `style::Overflow::Hidden`, a three-module path through a re-exported module, an enum leaf, a head type unchanged, the declarations on hover), `e315_a_middle_segment_is_a_reference_of_its_type` (annotation tokens; find-references from the middle segment reaches 3 spellings, each exactly `Length`), `e316_an_implicit_parameter_prints_its_trait_arguments` (one argument, two parameters of one trait at `str` and `i32`, an explicit `<S: Shows<str>>` beside an implicit one, declaration and call site), `e317_a_returned_variant_hovers_with_the_expected_instantiation` (tail, `ret`, bound `None`, `Some(1)`, argument, `Ok`, `Err`), `e322_a_head_link_after_an_element_valued_item_mints_no_hint` (view and alone); E306's pin now asserts `Option<i32>::None` exactly; E311's pin gained `Length`. Each new pin was red before its fix.

### Gates (tip b8ecfee3; box load 4-16, other lanes building)
- Full suite, `--cargo-profile ci-test -E 'not binary(deep_nesting)' -j 6`: **10622/10622** passed (38 skipped). Inside it: native_differential 279, check_scope_differential 16, permutation_differential 7, edit_replay_differential 27, replay_differential 2, id_windows 10, ci_ignored_pins 12, hygiene 3, the vilan-lsp binary 1133.
- Native differential sweep mode (`VILAN_NATIVE_DIFFERENTIAL=1`): 279/279.
- Deep-nesting canary at 1536 KiB: 18/18.
- `cargo clippy --workspace --all-targets -- -D warnings`: clean. `cargo fmt --check`: clean. `vilan fmt --check .`: exit 0.
- `scripts/ci-local.sh perf`: green, T2 verdict green, growth x1.929. No `[[bump]]` row (no std growth).
- kolt cold check (the copy of the owner's tree, lucide carried, checked clean under 0.50.0): peak RSS medians of 5, interleaved: base 266.3 / 265.8 MB, tip 267.1 / 257.8 MB (within 3%). Instructions: base 10.61 / 10.62 G, tip 10.56 G (one tip run read 14.15 G, an outlier I could not reproduce; the other three runs sit at 10.56-10.62).
- The kolt sweeps with `VILAN_EDITOR_KOLT` (six `#[ignore]` tests, kolt copy): all pass, including `kolt_no_hover_splits_a_word` and `kolt_every_enum_binding_hovers_with_its_chunk`. The token probe at `views.vl:218` now reads `style` Namespace, `Overflow` Enum, `Hidden` EnumMember; line 217 `Length` Struct.

### lsp-latency (scripts/lsp-latency.py, kolt copy, release binaries; base = the installed 0.50.0 b923bfc6)
Keystroke columns (hover / completion / inlay / tokens, wall ms) and the idle columns do not move: leaf 3.1/1.2/0.5/0.7 base against 2.9/1.1/0.4/0.5 tip, every row within the noise at all four columns, all under 5 ms. Instructions to idle (G), base -> tip (final binary, 5 runs on the three rows re-taken; the other rows from the 3-run pass of the same tip minus the last speed-up):
| row | base | tip |
|---|---|---|
| leaf keystroke | 3.44 | 3.46 |
| leaf + pause | 8.54 | 8.58 |
| world mode | 3.82 | 3.83 |
| shared.vl | 1.33 | 1.34 |
| model.vl | 1.30 | 1.30 |
| importers open | 4.63 | 4.65 |
| css | 5.58 | 5.61 |
| parse break / repair | 5.56 / 5.69 | 5.58 / 5.70 |
That is +0.2 to +0.6 %. A bisect (E317's call removed) put E317's scan at about 0.02 G of the leaf row before the speed-up (b8ecfee3 cut it to one pass over `function_calls` and tests scope before any map lookup). Peak VmHWM tracked the base within the run-to-run spread.

### Finds (`sweeps/order53/newitems53-editor-53.json`, repros in `sweeps/order53/editor-53/finds/`)
- **E?1:** module segments of a qualified pattern (`lib::deep::Mode::On =>`) and of a struct initializer path paint nothing.
- **E?2:** a generic enum's payload variant in value position hovers without its payload (`Option<i32>::Some` where a pattern reads `Option<i32>::Some(i32)`).
- **M?1:** E317's scan (and E313's rows) walk the world per analysis; M148 should fold them into the per-item rows.

### Questions for the owner
1. **E310's `[hint]`-host note:** closed as "no need met" (nothing in this lane's paths shows a `[hint]` trait). Recommendation: leave E310 as shipped and reopen only if a kolt hover of a hinted trait reads wrong.
2. **Squash b2ee310a and b8ecfee3 at the merge?** Recommendation: yes - both are follow-ups of their item (a pin edit; a speed-up of the same function), and the merge keeps one commit per item.
3. **E?2 (payload on a generic variant's hover):** XS and now cheap. Recommendation: take it with the next editor lane.
4. **M?1 versus M148:** I left E317's scan as a bounded +0.2-0.5 % because M148 (incr-53a) is about to re-shape the rows. Recommendation: have incr-53a fold `variant_use_labels` into M148's per-item rendering rather than carrying two scans; no action for this merge.
