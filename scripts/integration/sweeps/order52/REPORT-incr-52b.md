## incr-52b hand-back (Order 52)

The lane stopped short of the full list. B624, P2 layering with E294's pinned half, M145 and B618 are built, and every gate is green on the final tip. Not built: M146 (dependencies hot), M137, M138 and M133's incr half. One miscompile found along the way is fixed in its own commit.

- **Tip:** `0570d9b7` on branch `incr-52b`.
- **Base:** C1 `029d5ab4`. I did not rebase onto `e4255f60`, as you asked.
- Nothing is pushed and none of my processes are running. `incr-52b-STATUS.md` is untracked and current.

### Commits (oldest first)
| sha | Item | Family |
|---|---|---|
| `0d612b20` | B624: S7's item records stay on over the std prefix (plus source-key alignment) | fix |
| `5417b6ed` | std-prefix P2: the server builds a missed world over the pinned std prefix | performance |
| `e3ca0a48` | A closure is no longer a receiver of a `Callable` struct's impl (found under M145) | miscompile |
| `9c55f347` | M145: the prefix guard re-asks each question under the rigidity the lookup had | performance |
| `e8e35ce9` | B618: `async e` is always `Task<T>` | fix |
| `0570d9b7` | P2 follow-up: no layering for std-only worlds or for a file open on its own | performance |

CHANGELOG markers: 10 heads, 10 markers.

### What each does
- **B624.**
  - The slot-write census did run over the prefix's package re-walk. The real cause was a list literal's element slot (and a `List::new()` hole). It was minted lazily in the window of whichever constraint asked first, which was the pusher (`a_spoil` loads first). So `bag`'s type named a slot in another item's window, and no edge carried the edit back to `bag`.
  - The slot is now minted in its owner's window (`IdWindows::anchor_at_owner`, `element_slot_of`). Item records are enabled for prefix worlds again.
  - Found on the way: std's `lib.vl` and dependency surfaces registered a source without its path key. Every later source was keyed by the next file's path, and the last one by 0. Each source now registers its own key, with a debug assert.
  - Pins: `a_push_into_an_unedited_modules_binding_stales_its_item_record_over_the_std_prefix` is red without the fix. The classes package over the prefix now passes with records on.
  - Of incr-51c's 11 forced-prefix failures, the item-record plant now passes. The remaining 10 are S1-only census counts and plants, and the two package-table pins.
- **P2 (layering).**
  - A world the server has to build (an S1 or canonical miss of a declared entry, with package modules or a hot set) now takes std from the prefix world, keyed by platform and std closure.
  - It walks and resolves its own package modules over that prefix under §4.2's guard. It is stored under its own key, and S1's hot set then walks over it. Hits are unchanged.
  - The declared entries pin their prefixes: sized into the budget, never evicted, unpinned when the package's last document closes.
  - Switch: `VILAN_STD_PREFIX=off|layered|on`. The server defaults to layered; the CLI is unchanged.
  - Pins: `every_edit_class_answers_what_a_clean_analysis_answers_with_the_prefix_layered` (102 analyses, 50 layered builds, 40 of them over a served prefix, 45 S1 hits, 597 item records served, 0 divergences) and vilan-lsp's `a_world_rebuilt_after_an_edit_takes_std_from_the_pinned_prefix`.
  - With layering forced on, the four differentials and the corpus pass. What fails is census-shaped only: base_cache count pins and one reach-questions pin.
- **Closure/`Callable` miscompile.**
  - `twice.call(5f)` on a closure compiled to `Scale`'s `call` and printed `NaN`. `impl_subject_admits` was using the call operator's coercion when matching an impl subject.
  - An impl on a struct or enum head no longer admits a closure or function receiver. Pins are in `callable.rs`. The estate count is 0.
  - **This touches inference (`impl_subject_admits`); solver-52 should know.**
- **M145.**
  - The item's premise was wrong: the receiver was not `Type::Unknown`. It was std's own generic `T`, which the lookup treats as fixed (rigid), but the guard's verdict re-read it with nothing fixed, as a hole any impl declaring `get` could fill.
  - Each logged question now records the rigid-binder scope it was asked under, and the verdict re-asks under it (`Asked::scopes`, `reach_admits`).
  - Fixing that exposed a second refusal: kolt's `impl Scale with Callable`, which was the miscompile above.
  - **Kolt's client is now served over the prefix.** Kolt's `dist` is byte-identical with the prefix forced on and off (the `.cache` directory differs; see N?1).
  - Pins: `m145_a_package_impl_on_its_own_type_is_served_over_the_std_prefix` is red without the fix. The refusing case is now a package impl on `SignalCell<T>`.
- **B618.**
  - The premise reproduced. Always-loading `task.vl` costs the empty program 15% (246M → 282M instructions), so instead an `async` expression seeds `std::task` the way an element seeds `std::web::ui` (`collect_std_item_modules`).
  - The empty program moves by +0.01%. A program that spawns without importing `std::task` pays about 36M once.
  - Tests updated: the compat pin is inverted, the RPC pin's async return is now written `Task<str>`, native's F130 probe needle now reads `Task`, and marker census a25 is regenerated.
  - Estate 0, so the family is `fix`. The spec's execution chapter now states the rule.
- **P2 follow-up.** Layering a std-only world rebuilt it on every keystroke with no records replayed: `shared.vl` went 1.33 → 2.13G. Layering a file open on its own cost +2.3% per hit: leaf 3.41 → 3.49G. Both are excluded now.

### Functions changed
- **analyzer.rs:**
  - New: `element_slot_of` (replaces `list_literal_element_slot` and the inline mint in `freshen_list_element_slots`), `hot_set_imports_a_use_inferred_binding` (factored out of `analyze_inner`), `std_prefix_keys`, `Layered`, `LayeredRefusal`, `finish_layered_world`, `ImplReachLog::kept_by`/`absorb`, `Asked`, `reach_scope`, `reach_admits`, `BaseCacheState::entry_prefixes`/`pinned_keys`/`prune_entry_prefixes`, `base_cache_prefix_stats`, `base_cache_pinned_prefixes`.
  - Changed: `analyze_inner` (the layering decision, both arms, the lib and module source keys), `resolve_package_over_prefix`, `impl_reach`, `note_member_query`, `note_trait_query`, `note_receiver`, `impl_subject_admits`, `base_cache_admit` (new `learn` parameter), `note_hot_refusal` (now keyed by the refused key), `evict_to_budget`, `base_cache_budget_in_force`, `collect_std_item_modules`, the `enable_item_records` site.
- **Elsewhere:** `id_windows.rs` (`saved_anchor`, `restore_anchor`, `anchor_at_owner`); `incremental.rs` (`std_prefix_layering` and its setters, `Census::prefix_layered`); vilan-lsp `main()` turns layering on (one line, plus the test).
- **Outside my area:** two lines in `crates/vilan-cli/tests/native_differential.rs` (the F130 needle and its doc comment).
- No mono.rs or emitter change.

### Gates on `0570d9b7`
- **Full suite** (ci-test profile, `not binary(deep_nesting)`, `-j 6`): 10,540/10,540, 32 skipped. Within it:
  - ci_ignored_pins 12, hygiene 3, corpus 14
  - check_scope_differential 16, permutation_differential 7, edit_replay_differential 27, id_windows 10
  - native_differential 270, vilan-lsp 1,104
- **Native differential, sweep mode:** 270/270.
- **Canary at 1536 KiB:** 18/18.
- **Lint and format:** clippy `-D warnings`, `cargo fmt --check` and `vilan fmt --check .` are clean.
- **`ci-local.sh perf`:** T2 green. Against the base on the same box, every row is between −0.01% and +0.05%, except `example:todo` at −0.80% (likely the closure-admission fix). No bump row.
- **Late writes:** 0 on kolt, with the prefix off and on.
- **RSS on kolt** (9-run medians): base 268,552 / 269,428 KB, tip 267,184 / 269,048 KB, so −0.5% / −0.1%.

### E292 / lsp-latency rows
Kolt @dee494ab, lucide carried, `--runs 5`. All seven rows ran, including model.vl keystroke and parse break. Instructions are in G.

| Row | base | tip, layering off | tip, layered |
|---|---|---|---|
| leaf | 3.41 | 3.41 | 3.41 |
| leaf + pause | 8.45 | 8.43 | 8.45 |
| world | 3.79 | 3.78 | 3.78 |
| shared | 1.33 | 1.33 | 1.33 |
| model | 1.30 | 1.30 | 1.30 |
| importers open | 4.62 | 4.59 | 4.60 |
| css | 6.02 | 5.84 | 5.85 |
| parse break | 6.00 | 5.82 | 5.83 |

- **CPU is not a reading here.** The load average was 7–20 the whole time, because other lanes and editor-52's own lsp-latency run were active. Base CPU ms for comparison: leaf 770, css 1760, parse break 1280. The CPU rows need a quiet box at the seal.
- **E292 stays open.**
- **P2 does not move these rows.** They are keystroke hits, and E294 already keeps the pause worlds. P2 only acts on world builds.
- **Pause row world builds:** across a full layered run, 126 analyses: 106 hits and 20 world builds. Of those, 13 were layered, and 2 of the 13 were served the prefix. The harness starts a fresh server per scenario, so the prefix is mostly cold.
- **Cold opens:** the open rows' CPU reads somewhat higher layered (for example views.vl 1960 → 2490 ms), but under that load I can't separate the cost from noise.
- The prefix pays off in long sessions. The vilan-lsp pin above shows a rebuild after an edit taking std from the pinned prefix.

### Finds
Filed in `sweeps/order52/newitems52-incr-52b.json`; the repro is in `sweeps/order51/incr-52b/finds/`.
- **B?1:** the closure/`Callable` miscompile, fixed in `e3ca0a48`.
- **B?2:** the source-key misalignment, fixed in `0d612b20`.
- **M?1:** M137's premise is unsafe as written. vilan-rust's F31 liveness tracks "last use" per read entity, so one shared reference entity read in two calls would be marked a last use twice and moved twice. Not built.
- **Q?1:** dependencies (M146) not built. The hot load lacks the drain's dependency machinery. Recommendation: a dependency tier in the prefix instead.
- **N?1:** const-site cache keys depend on the world's shape: 109 of 113 differ on kolt with the prefix forced on, though the output is identical. P3 will need content-based keys.

I also added an "As built (P2)" note to `proposal/std-prefix.md` in the proposals checkout, uncommitted, for you to commit.

### Questions for the owner
1. **Keep layering on by default in the server?** It is neutral on every keystroke row, saves std on later world builds in a session, and may cost on a cold open. I recommend yes, with a quiet-box CPU check of the open rows at the seal, and turning it off if a cold open is measurably worse.
2. **Dependencies (M146):** port the dependency loading into the hot load, as ruled, or put dependencies in the prefix as their own tier? I recommend the tier: it reuses the existing loader and matches the std → dependencies → package order.
3. **M137:** I recommend exempting context hidden-parameter reads from F31's last-use candidates before sharing the reference entities, and measuring the copies that adds.
4. **The closure/`Callable` fix sits in inference, which is solver-52's area.** I recommend merging it as its own commit; it is 14 lines and pinned.
