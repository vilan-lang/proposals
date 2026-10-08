## perf-47: final report

**Branch `perf-47` @ `83fea42526e3974c42e3660b65e864b20debcb17`.** Worktree `vilan/.claude/worktrees/perf-47`. It is based on `origin/next` @e5e15ca7, has not been rebased (origin/next has since moved to 99285bc4), and nothing is pushed. 11 commits, 24 files changed against the base. `LANE-STATUS.md` (untracked) lists the shas.

### Method
- **Counts:** hardware `instructions:u` via `scripts/perf_count.py`, release build with one codegen unit, warm macro tables.
- **kolt:** a scratch copy of kolt's working tree, with `VILAN_STD` set to a copy of the base's std (with `macro_std` beside it).
- **Profiles:** callgrind on the `profiling` build.
- **Work units:** `--explain-cost` and `VILAN_COUNTERS`.
- No wall times. The machine ran at load 18–32 throughout.

### Per item

**M111: done @e98d3842 (one-disease root).**
- **Cause:** the memo was not the main problem. `applying_implementations` was called about 1,560 times per kolt leg. The memo hit about 30%, missing every bound-directed call with trait arguments.
- Each miss then cost about 8.8 M instructions. Beneath it, `subject_applies` ↔ `provides_trait` and `provided_trait_argument_sets` ↔ `bind_bound_binders` re-proved every blanket bound: about 870k proofs and 790k provider scans, each one allocating a supertrait closure per impl.
- **Fix:**
  - The arguments-carrying questions are memoized by id.
  - `provides_trait` scans only the trait's providers (an index built once).
  - The proofs and provider sets are memoized per Program.
  - The proof memo is exact under B408's cycle cut: a YES is always stored; a NO only when no cut reached below the question; nothing is stored when a `RecursionGuard` tripped.
- **Result (sequential):** kolt check 25.30 G → 15.49 G (−38.8%). Overlapped: 25.42 G → 15.62 G. Peak RSS is flat (208.8 → 209.3 MB sequential). Client-leg allocations went from 44.5 M to 14.6 M.
- kolt's `dist/` is byte-identical between base and tip. Corpus unchanged.

**M118: done @07673f28.**
- **Cause:** asked what a `dyn Flow<X>` provides `Flow` at, `trait_args_for(_pattern)` reconciled the object against every `Flow` implementor through the erasure arm, to arrive at X. Each attempt minted about 11k slots, and an unannotated closure re-queued the call, paying it again.
- The owner's note that the cost needs the closure inside a selector fits: the inline match keeps the stage type open, so the selector's call is re-attempted.
- **Fix:** an object answers for its own trait. Before skipping the scan, I checked the answers were identical to the scan's over the corpus, inference, docs and module_resolution suites plus kolt (a temporary env-gated comparison, since removed).
- **Results (kolt v10/v11 variants):**

  | | `find` before | `find` after | total check before → after |
  |---|---:|---:|---:|
  | v10 (unannotated) | 45,435 | 1,872 | 27.49 G → 15.49 G |
  | v11 (annotated) | 15,981 | 1,462 | 26.34 G → 15.49 G |

  `messages` is 1,147. An annotation is now worth about 400 units, not 30,000, so the "suggest an annotation" diagnostic has no case to fire on here.
- The `selections` column now counts: the emission walk charges each computed selection to the declaration being emitted.

**M119: closed by M111, no code commit.**
- F78's per-stage defaults were paid in the emitter's selection.
- At base, F78 cost reactive-ui +4.4% (2,596 M with it vs 2,486 M with its std change reverted). At tip, F78 *saves* 3.5% (1,951 M vs 2,022 M).
- reactive-ui is 1,951 M, below its pre-F78 count of 2,447 M, with the defaults kept.

**M117: the store exhibits patch can go to kolt.**
- The patch is migrated to the new std paths and applied on a scratch copy; nothing was written to kolt.
- At base it cost +2.25 G (+8.9%). At tip it costs +0.69 G (+4.4%):
  - **+0.29 G (+1.9%) is std's store modules loaded on both legs.** I measured this with only an unused `import std::reactive::store::Store` added. It is M120's tax.
  - **+0.39 G (+2.5%) is kolt's own new code.** Solver work units rise only about 1.2%. The largest lines are the bound audit (+102 M, filed as M?1), in-place-write reachability (+74 M), and proportional emission.
- Nothing disproportionate is left that is the derive's fault.

**M120: measured; door (c) not built.**
- An empty browser program with the web prelude is 1.48 G instructions; without the prelude it is 0.24 G. So 1.23 G is std analysis every web program pays.
- Cost of importing one std module unused, on a node program:

  | module | cost |
  |---|---:|
  | `http` / `rpc::server` | +1.62 G |
  | `rpc` | +1.43 G |
  | `web::document` | +1.19 G |
  | `web::ui` | +1.08 G |
  | `store` | +0.96 G |
  | `reactive` | +0.76 G |
  | `markdown` | +72 M |

- On the browser leg: `rpc` +692 M, `store` +114 M, `markdown` +95 M, `transient` +82 M; most other modules are under 20 M.
- Door (c) is not cheap: the tax is the reactive core and the ui twins themselves.
- **What the structural fix (b) needs from incr-47's records:**
  - a deterministic, entry-independent std world prefix per (toolchain sha, std+`macro_std` content hash, platform/layer, prelude);
  - stable ids across processes, which today depend on load order;
  - a serialization of the analyzer tables S1 keeps as the "stored prefix";
  - S0's global-facts fingerprint (impl headers, trait members, resource-ness, generated impls), so a user impl of a std trait invalidates or extends the cached std facts rather than silently missing them;
  - S5's interface firewall, so std bodies are never re-checked.

**M113: done @0bce95e0.**
- **Cause:** not a lookup. The per-package macro-expansion table capped at 4,096 entries and kept the same smallest keys on every flush. A 640-module package (~7,700 expansions) re-ran about 3,600 of them on every warm check — 1.9 G of the doubling.
- **Fix:** cap raised to 65,536.
- **Result:** plain 640: 13.11 G → 11.22 G. Doubling 320→640: x2.33 → x1.99. 160→320 stays x1.94.

**M112: done @de928710.**
- It was kolt's drift, not the generator's. With M111 fixed, kolt's emission walk share is 5.0% against the generator's 4.0%, and calibrate passes.
- New option: `perf_gate.py calibrate --kolt-tree DIR` calibrates without running git in kolt.
- The nearest phase is now the const pass: 3.0% vs 12.2% (filed as M?3).

**M114: done @41f69ae5.**
- I read 14 runs of the `perf` job. Every run fell back to callgrind (no PMU on the runners). The same code counted the same within 0.01% across four runner CPUs.
- So 12 `ci` rows are adopted from run 37319616657 (c43d6ab9, the fold plus Dependabot) at a row-level tolerance of 0.5%, per Q7.
- I added `ratchet --tolerance`, and a row's own `tolerance` now overrides the file's. Reference rows and bumps are untouched.

**M109: done @d1391a12.**
- **Causes:**
  1. Rule 2 donated whole bindings but never their disjoint fields. It now does, for bindings that built their value by construction; pattern captures are excluded.
  2. A `&mut` loan to a closure binding made the owner opaque to the last-use pass. That loan is now treated as call-bounded.
  3. Natively, the field-liveness rule (F37) did not follow tuple elements; it does now.
- The derive's multi-payload write step and a single payload lent to a closure no longer copy back, on either backend.
- **Pin:** `__clone` calls for 100 writes go from 400 to 200, the copy *out* staying (Q6). The probe: 320 → 151 ms on JS.
- No golden or census moved. An earlier, broader version did move goldens: it donated `entry[1]` from a wrapped-view capture of a map, which is unsound. I caught it in corpus and restricted the rule.

**M90: done @832f1db2, plus @83fea425 (pass cost).**
- A read-only `let` of a stable place shares the place on JS. The conditions are B53's capture-share conditions, plus:
  - the value's type is "plain": host types are excluded, because `Bytes::set` mutates through a bare `self` — the first version reddened `bytes-aliasing`;
  - the binding is read only through projections and loans.
- Native keeps its copy (`clone_sites` is unchanged).
- **Pin:** 510 `__clone` calls → under 10. A second pin runs the returned, captured and stored cases and confirms each keeps its copy.
- **Goldens:** `tuple-access.mjs` regenerated (a redundant clone of a fresh reslice is gone). Copy census 587 → 586.
- @83fea425 makes the pass cheap: candidates are filtered first, and the written-roots set and seam leaves are taken once for B267, M90 and the capture plan.

**M89: done @8b9287ce.**
- Vtables are deduplicated by slot set on JS; the second pair's table is `const $b = $a`.
- kolt's client: 14 tables → 10. No golden moved.

**N145: done @1968c140.** Re-anchored on `UserId`'s `Hashable` impl. The preflight passes on kolt@984a1dfb's `shared.vl` (via `git archive` on my scratch copy's `.git`, not on kolt) and on today's tree.

**N146: done @e87be71f.**
1. The cut writes names, not paths (the verdict file, and `` the prepared tree `x` `` in reports). It refuses before staging if CHANGELOG, budgets or the report contain a home path.
2. `fold-release.sh` reads origin's main via `ls-remote`, pushes main when origin's lacks the merge, and verifies origin after every push.
3. The cut runs `ratchet --from <verdict> --release` in the release commit: each bumped row's ceiling becomes its measured count, and `perf/budgets.toml` is staged. `ratchet` reads verdicts as well as measured JSON.
4. `seal --advance` no longer writes the tree. The E121 count lives in `<verdict-dir>/e121-state.json`, is read by the next seal, and is recorded in the verdict (`e121_after`).
- Every new pin is red on the old scripts.

**F49: not done.**
- **Cause:** natively, `read_binding` emits `cell.get()`, which clones the whole boxed value for a `&self` or `&` argument.
- `Shared::read_with` exists, but rewriting the call inside the borrow changes argument evaluation order relative to the borrow, and could panic on a re-entrant write that a clone tolerated. That is native-47's behaviour call, so I left it.

**M60: census only.**
- One std `get`/`set` pair remains: `optimistic`'s `previous` snapshot, which is legitimate. Nothing to move.
- The memory-model tour note (docs-47) and the editor hint (editor-47) are outside my ownership.

### Before → after table
Base e5e15ca7 → tip 83fea425 (tip build @83fea425 for the gate subjects; kolt figures from the tip build @8b9287ce, which differs from the final tip only in the M90 pass-cost refinement).

**kolt `vilan check`**

| | base | tip | change |
|---|---:|---:|---:|
| instructions, sequential | 25.30 G | 15.49 G | −38.8% |
| peak RSS, sequential | 208.8 MB | 209.3 MB | flat |
| instructions, overlapped | 25.42 G | 15.62 G | −38.6% |
| peak RSS, overlapped | 263.9 MB | 264.5 MB | flat |

**kolt `--explain-cost` top ten:** solver columns are identical (493,021 browser units at base). The selections column now counts — for example sidebar_shell 18, create_search_modal 43, `<module level>` 34.

**Gate subjects (M instructions)**

| subject | base | tip | change |
|---|---:|---:|---:|
| math | 244.3 | 245.0 | +0.3% |
| watch | 309.3 | 308.9 | −0.1% |
| browser | 1,485.4 | 1,480.9 | −0.3% |
| fullstack | 3,226.0 | 3,187.6 | −1.2% |
| router | 1,890.3 | 1,746.1 | −7.6% |
| reactive-ui | 2,595.8 | 1,950.8 | −24.8% |
| ssr | 4,164.9 | 4,055.8 | −2.6% |
| canvas | 1,493.7 | 1,489.3 | −0.3% |
| rpc | 2,107.2 | 2,074.4 | −1.6% |
| todo | 6,077.0 | 5,281.4 | −13.1% |
| walkthrough | 6,359.8 | 5,448.7 | −14.3% |
| genapp:46 | 9,875.3 | 9,616.3 | −2.6% |
| plain:160 | 2,895.7 | 2,903.5 | +0.3% |
| plain:320 | 5,616.9 | 5,631.9 | +0.3% |
| plain:640 | 13,109.6 | 11,216.1 | −14.4% |

**Doubling rows:** 160→320 x1.940 → x1.940; 320→640 x2.334 → x1.991.

### Were M111, M118 and M119 one disease?
Two diseases.
- **M111 + M119 are one:** per-site impl selection at emission, re-proving blanket chains. It also explains most of M117's +8.9% and M112's drift.
- **M118 is separate:** on the analyzer side, the provider question for a `dyn` receiver was answered by scanning every implementor through the erasure arm, re-paid per attempt.

### Functions touched
- **analyzer.rs:** `trait_args_for`, `trait_args_for_pattern`, `object_trait_arguments` [new], Program field `selection_memos` (replacing `applying_memo`) and its accessor, `compute_clone_sites`, `copy_candidate_type`, `compute_donated_projections` [new], `donate_disjoint_projections` [new], `binding_owns_a_construction` [new], `is_elidable_copy`, `compute_shared_place_lets` [new], `bindings_handed_on_whole` [new], `projection_root` [new], `root_is_stable` [new], `shared_cells_root` [new], `type_is_plain_value` [new], `value_seam_leaves` / `seam_roots_of` / `collect_branch_tail_leaves` [new; they replace `value_seam_roots` and `insert_branch_seam_roots`], `compute_shared_read_bindings` (signature), `compute_capture_clone_sites` (signature), the `analyze_over_world` pipeline and its Program literal (`shared_place_inits`), and Analyzer fields `donated_projections`, `shared_place_lets`, `shared_place_inits`.
- **analyzer/liveness.rs:** `collect_unfollowable_loans`, `callee_is_a_closure_binding` [new].
- **impl_select.rs:** memos, `memoized_proof`, `SelectionMemos`, owner attribution.
- **transformer.rs:** `function_with_name`, `maybe_clone`, `emit_vtable`.
- **util.rs:** `RecursionGuard::trips`.
- **macros.rs:** `DISK_ENTRY_CAP`.
- **vilan-rust:** `walk_liveness` arm, `liveness_spine` [new].
- **vilan-cli `main.rs`:** `print_cost_report`.
- Late writes stay zero (VILAN_COUNTERS on kolt, both legs).

### Gates on 83fea425
| gate | result |
|---|---|
| `cargo nextest run --workspace -j 6` | 9651 passed, 33 skipped |
| `native_differential` with `VILAN_NATIVE_DIFFERENTIAL=1` | 161/161 |
| clippy `-D warnings` | clean |
| `cargo fmt --check` | clean |
| `ci-local.sh vilan-fmt` | green |
| `ci-local.sh windows` | green |
| `ci-local.sh perf` | T2 green, growth x1.940 |

### Finds
Seven, in `sweeps/order47/newitems47-perf.json`:
- **M?1:** the analyzer's bound audit `check_generic_bound_satisfaction` is about 10.6% of kolt's check at the tip — M111's disease on the analyzer side.
- **M?2:** a `.derive` on a `dyn Source` still costs about 4.4k slots. Filtering nominal "echo" candidates fixes it but changes one answer (`a142_s4_filter_map_and_any_over_transients`: `bool` → `T`), which is a solver question.
- **M?3:** genapp's const-pass drift is 9.2 points, close to the 10-point calibrate threshold.
- **M?4:** the CI `perf` job builds with stable rustc, so the new `ci` ceilings will move with GitHub's stable.
- **N?5:** `VILAN_STD` pointing at a std copy without `macro_std` gives cryptic `PartialOrd`/`eq` errors instead of the existing split-toolchain refusal.
- **N?6:** `perf_gate.py measure --subject plain:640` silently measures nothing.
- **B?7:** `import std::js::null;` gets the generic parse refusal with no steer.

### Integrator notes
- **`seal.sh`:** `seal --advance` no longer edits `perf/budgets.toml`. The count goes to `~/.vilan/perf-verdicts/e121-state.json` and the verdict, and lands in the tree only through the cut's `ratchet`.
- **Corpus:** one golden moved (`tuple-access.mjs`), and the copy census is regenerated.
- **Rebase:** origin/next has moved. Expect conflicts in analyzer.rs and transformer.rs with solver-47 and debug-47, and in CHANGELOG.

### Needs the owner
1. Whether kolt takes the store exhibits patch now. It costs +4.4% at this lane's tip; the patch needs its std paths migrated.
2. Pin the CI `perf` job's toolchain (M?4).
3. M?2's semantics — what an object provides a blanket trait at — before its cheap fix.
