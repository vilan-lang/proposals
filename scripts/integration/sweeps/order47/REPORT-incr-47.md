## incr-47 report (M110 S0 + the edit-replay differential + S1; stopped before S2)

**Branch `incr-47`, tip `974d5dc416d353e811054dbbe98bf7c6ea13b0d1`.** It sits on `origin/next` @e5e15ca7 with no rebase. Since then next has gained only the Dependabot CI bumps, which touch none of my files. Nothing is pushed. Worktree: `vilan/.claude/worktrees/incr-47`. Scratch, logs, the kolt copy and the binaries are under `target/incr-47-scratch/`.

### Per slice

| slice | sha | status |
|---|---|---|
| S0 — measure, no behaviour change | 306940ee | done |
| Q3 — the edit-replay differential | b7cc8fc1 | done; green on S0's tree |
| S1 — hot-set worlds | 974d5dc4 | done; acceptance met for `views.vl`; served for only one of the four session files (below) |
| S2, S3, S4 | — | not built: stopped by R-a (reason below) |

**S0 (306940ee)** — what was built:
- **The hot seed.** `Workspace::hot_seeds` names the file being edited. The LSP sets it in `did_change` (the last-edited canonical path) and `analyze_world` passes it on.
- **The hot set.** It is the reverse import closure of the seed, closed over cycles. It is computed syntactically before the drain, from the same `import`/`use` paths and `deepest_module_or_namespace` resolution the loader uses, plus ancestor edges for nested modules (`hot_set_closure`).
- **Fingerprints.** `vilan_core::incremental` (new) computes per-item interface fingerprints:
  - a function's declaration label (the inferred return included), async, the contexts it requires and declares, its platform requirement without the via-chain, and `borrows`/`bumps`;
  - a type's shape;
  - a module binding's type.
  
  There is also one global-facts fingerprint: impl headers with the member names each provides, traits, resource-declared types. All of these are content-hashed text with no `TypeId`.
- **The phase line**, under `VILAN_PHASE_TIMING`: `[vilan phase] hot-set n/m interface-moved k global-moved b unknown-interfaces u hot-world w hot-refusal r`, plus `interface-moved-items`. Fingerprinting only runs under `VILAN_INCREMENTAL=measure|verify`, so latency runs don't pay for it.
- **Counters** (Q9, under `VILAN_COUNTERS`): `[vilan counters] incremental base-hits/misses/stores, hot-world, sources-walked, records-replayed, functions-checked`.
- **Verify mode.** `VILAN_INCREMENTAL=verify` makes the LSP run a clean analysis beside every analysis and log `[vilan incremental] verify identical|DIFFERS`.
- **The harness.** `scripts/lsp-latency.py --session` runs the scripted session, and the harness gains a `leaf keystroke, world mode` row.

**Differential (b7cc8fc1)** — new binary `crates/vilan-core/tests/edit_replay_differential.rs`:
- **How a step works.** Each step sets an overlay edit, runs an incremental analysis with the edited file as seed, then a clean one (`incremental::clean_analysis`: no cache lookup or store, no checks record, no hot set). It compares `incremental::render_observation`: diagnostics and warnings with file, span, note and trace; every hover, declaration and hint label at its (file, span); every resolved name and type reference. It also compares the emitted JS. Every edit is undone and compared again.
- **The classes leg** covers all §6 classes (i1–i7, written return, field rename, impl in an unimported module, derive, import, const callee, cycle, a prefix module changing under a seed elsewhere, browser reaching node). It adds three hazard fixtures: a foreign impl the prefix calls, a context grounded only by a hot module, and two modules pushing into one binding.
- **The corpus leg** hosts every corpus program as a module, with an importer and a bystander.

**S1 (974d5dc4)** — what was built:
- **The stored world.** `BaseCacheKey.hot` holds the hot set's paths plus the load requests its modules write. The drain holds hot modules back and loads what they request into the prefix (so lucide, reached from `views.vl`, lands in the prefix). The prefix resolves and is stored. On hit and miss alike, `load_hot_modules` then loads, expands and walks the hot set, and the entry walks after it.
- **M19's terms re-pointed.** Records are read, validated and written over the stored prefix only (`World::prefix_len`), hot sources are never replayed, and a prefix note pointing into a hot source is unrecordable.
- **Guards.** Each refusal is reported as `hot-refusal`, and the analysis is then built canonically. Late refusals are remembered per key, so a refusal costs one wasted attempt, not one per keystroke. The guards:
  - an impl the prefix could reach (a subject not declared in the hot set, unless the impl is inherent and no non-hot package module spells its member names);
  - a hot module importing a prefix module that has a use-inferred binding (an element slot, or a non-ground type, closed over prefix imports);
  - a hot module that defines a macro;
  - a hot module that imports the entry;
  - a derive-generated reference into the hot set;
  - a module the hot shape cannot load.
- **Macro-name references** (`[derive(Wire)]` → its `macro fun`) are now queued at the walk and resolved at the top of `resolve_world`. They used to depend on load order: the corpus leg caught `arena` losing the reference in a reordered world, and the canonical path had the same order-dependence.
- **Never emitted.** A hot-set program is never emitted, because the CLI names no seeds. Its JS is compared against a clean analysis of the same shape (`clean_analysis_keeping_hot_shape`). Its editor rendering is compared against the canonical clean analysis.

**Planted bugs** — each turns the differential red (tests `the_differential_sees_*`):
- `HotSetReplay`: a hot module replayed from a record, with the dirty bit waived for it.
- `PrefixUnvalidated`: the stored prefix served without its content check.
- `ImplGuardOff`: the impl guard dropped.
- `UseInferredGuardOff`: the use-inferred-binding guard dropped (the context and binding-push edits go red).

**Counter pins** (`a_keystroke_rewalks_its_hot_set_and_nothing_else`):
- A leaf keystroke re-walks 2 sources, a cycle member 3, a shared module 3, the entry 1, each as a base-cache hit.
- `WholePackageHot` is the planted hot set covering the whole package; under it every count moves.

**Measured win against the paper** (release builds, kolt working tree on 0.44.0, medians of 5, instructions:u):

| row | base e5e15ca7 | tip 974d5dc4 |
|---|---:|---:|
| `views.vl` keystroke, world mode | 12.58 G | **9.03 G (−28%)** |
| CPU to diagnostics, same row (loadavg 12–25) | 2720 ms | 1760 ms |
| `model.vl` + importers open (instructions) | 12.93 G | 12.95 G |
| `model.vl` + importers open (CPU to own diagnostics) | 2800 ms | 3180 ms |
| lone rows: leaf / `model.vl` / css / parse break / parse repair | 8.28 / 1.88 / 9.36 / 9.36 / 9.48 G | 8.28 / 1.88 / 9.39 / 9.36 / 9.47 G |
| Find References, first / warm | 8.50 G / 0 | 8.49 G / 0 |
| peak VmHWM | 931 MB | 980 MB (+5%: one more stored world) |

- The `model.vl` + importers row is unchanged in instructions: `model.vl`'s hot set is refused by the impl guard. The CPU difference is load, not work.
- The acceptance target was ≤ 10 G and the paper estimated −30–35%; the `views.vl` row lands at 9.03 G, −28%.
- In S1's session, `views.vl` keystrokes are 1 hit per keystroke, 2 sources walked (from 86), 84 records replayed, 110 functions checked (from 2,170). Clean keystrokes cost 9.13–9.16 G (from 12.7 G), broken ones 5.69 G (from 9.3 G).
- `theme.vl`, `model.vl` and `styles.vl`: refused (`hot-refusal impl`) on every keystroke, so they are unchanged.

### S0's what-a-keystroke-invalidates table (40 keystrokes, world mode, client.vl open)

| file | hot set | interface moved | global moved | base hit/miss/store | sources walked | functions checked | instructions (clean / broken text) |
|---|---|---|---|---|---:|---:|---|
| `views.vl` | 2/27 | 0 on 10/10 | 0 | 0/1/1 every keystroke | 86 | 2170 | 12.7 / 9.3 G |
| `theme.vl` | 11/27 | 0 on 10/10 | 0 | 0/1/1 | 86 | 2170 | 12.8 / 9.7 G |
| `model.vl` | 12/27 | 1 on 4 of 10 (`Channel::create` mid-statement), 0 otherwise | 0 | 0/1/1 | 86 | 2170 | 12.6 / 9.6 G |
| css (`styles.vl`) | 11/27 | 0 on 10/10 | 0 | 0/1/1 | 86 | 2170 | 12.7 / 9.6 G |

- M115 is confirmed: every keystroke is a miss that stores a cold world.
- Interfaces almost never move, and the global facts never did.
- Q10: broken states moved one interface in only 4 keystrokes. One function signature renders `unknown` throughout, not from typing.
- Full tables: `target/incr-47-scratch/session-s0.md` / `session-s1.md` (and `.json`).

### Where I stopped among S2–S4, and why

Stopped **before S2**, per R-a.
- **S1 falls well short of its estimate in coverage.** The paper predicted −30–35% "on every kolt edit outside lucide and the entry". Measured: −28% for `views.vl` and 0% for `theme.vl`, `model.vl` and the css file.
- **The cause is order.** The prefix resolves before the hot set walks, so a hot impl the prefix can reach would change the answer. §4.1's claim that the dirty bit and Class B/C re-runs cover this does not hold; it is the same reason an impl in the entry is invisible to modules today (find B?1).
- **S2–S4 would inherit the narrow coverage.** S2 and S3 sit on S1's prefix and would serve only the `views.vl` class until that is fixed (M?1).
- **For Order 48: S4 is the biggest lever left.** In the phase split of a warm `views.vl` hot-set keystroke:
  - checks are ~850 ms CPU;
  - post-passes are ~1,180 ms, of which the const pass is ~600 ms, re-run every keystroke at fuel 248,917.
  
  S4 does not depend on S1 (refused and lone analyses pay the const pass too). I recommend ordering it ahead of S2.

### Functions touched

**vilan-core `analyzer.rs`:**
- Data: `Workspace` (+`hot_seeds`), `BaseCacheKey` (+`hot`), `World` (+`prefix_len`, `hot`).
- New: `HotWorld`, `HotSet`, `hot_set_closure`, `hot_impls_stay_in_the_hot_set`, `load_hot_modules`, `hot_world_refused`, `refuse_hot_world`.
- Moved to module level from inside `analyze_inner`, unchanged: `Origin`, `load_order_key`, `load_order_entry`, `ensure_module_node`, `module_children_scope`.
- Cache and driver: `base_cache_lookup_locked` (plant only), `base_cache_clear`, `analyze_cancellable` (census reset), `analyze_inner` (signature +`allow_hot`, clean switch, hot decision, drain deferral and request seeding, guards, phase 2, census), `analyze_over_world` (prefix-bounded record lookup/store, reuse candidates).
- Analyzer methods and fields: `take_reuse_record`, `record_reusable_window` / `reaches_outside_the_world` (now `&self`), `record_macro_reference` (now queues), new `resolve_macro_references` / `resolve_macro_reference`, `resolve_world` (one call at its top), new `census_checks_scope`, `use_inferred_module_bindings`, `type_mentions_any`; fields `reuse_prefix_len`, `pending_macro_references`.
- Seams with solver-47 and debug-47: `resolve_world` (one line), `record_macro_reference`, `take_reuse_record`.

**Elsewhere:**
- `lib.rs`: `post_analysis_passes` (one `incremental::report` call), `mod incremental`.
- `vilan-lsp` `main.rs`: `Backend` / `AnalysisContext` (+`edited`), `did_change`, `analyze_world` (+`edited`), `analyze_world_and_publish`.
- `vilan-lsp` `document.rs`: new `analyze_cancellable_editing`, new `analyze_on_this_thread_editing`, new `verify_against_clean`, and `analyze_in_context` (the verify call).
- `vilan-lsp` `entry_world_tests.rs`: one call site.
- `scripts/lsp-latency.py`.

### What a cross-process std cache (M120) needs from these records
- **Key.** A disk key needs a std content and toolchain stamp in place of `BaseCacheKey`'s std root paths. The per-hit content validation (`World::source_hashes`) is already the right validator.
- **Fingerprints.** The S0 fingerprints are already persistable (content-hashed text, no ids), but their item keys use absolute canonical paths. They would need std-root-relative paths to be valid across machines.
- **Diagnostic records.** M19's per-source diagnostic records are TypeId-free. Their `ModuleTables` carry entity `Id`s, so they are valid only against the identical serialized world.
- **Mechanism.** S1's `load_hot_modules` is exactly how a deserialized std world would be extended with a package's modules: a hot set covering the whole package makes the stored prefix std-only. That gives an in-process "std once per toolchain" now.
- **What blocks it.** Persisting the world itself is still blocked by M36 §6.15 (structures keyed by leaked AST addresses).

### Gates on the tip (974d5dc4)
- `cargo nextest run --workspace -j 6`: exit 0, 9644/9644 passed, 33 skipped (the differential's 7 tests included).
- `native_differential` with `VILAN_NATIVE_DIFFERENTIAL=1`: 161/161.
- `cargo clippy --workspace --all-targets -- -D warnings`: exit 0.
- `cargo fmt --check`: exit 0.
- `ci-local.sh vilan-fmt`: ok. `ci-local.sh windows`: ok. `ci-local.sh perf`: ok; CLI counts equal the seal's within 0.04%, growth x1.940.
- Late writes: 0 on all 243 counter lines of the S1 session. No `.vl` fixtures were added and no golden moved.
- The S0 commit's tree passed clippy and the differential's two legs on its own.
- Not verified: CI's Windows runtime (only the cross-clippy ran here).

### Finds — `proposals/scripts/integration/sweeps/order47/newitems47-incr.json`
- **B?1:** an impl written in the entry is invisible to every module ("`Foo has no method`"), and a module's `Context::new()` grounded only by an entry `run` reports `T` unbounded, while either works when it sits in a module. This is the root of S1's coverage limit.
- **B?2:** a module binding's element-type conflict is blamed on whichever module loads later by file name (rename `a_spoil.vl` to `z_spoil.vl` and the error moves).
- **M?1:** S1 serves only hot sets whose impls the prefix can't reach — on kolt, `views.vl` but not the theme cycle, `model.vl` or the css file. Three doors are listed there.
- **M?2:** a broken-body keystroke is ~25% cheaper than a clean one (9.3 against 12.7 G) on every file; find what stops downstream.

### Needs the owner's ruling
1. **S1's coverage.** Its premise (§4.1) does not hold for impls or use-inferred bindings, so S1 ships guarded and serves leaf-importer edits only. Which fix for M?1 / B?1 does the owner want, and should S4 (the const cache) be pulled ahead of S2 for Order 48?
2. **Is the hot-set world allowed to differ in id order?** An analysis served from it numbers the hot set's declarations after the prefix's. Everything an editor reads is byte-identical to a clean analysis, and the differential asserts that. Its JS would order declarations differently, so it is never emitted; the CLI, `--watch` and HMR never name a hot seed. Is that acceptable, or should `--watch`/HMR wait for S5's id windows?
3. **One canonical-output change rides S1.** Macro-name references now resolve when the world resolves, so go-to-definition on a `[derive]` name always finds its `macro fun` regardless of load order. No test or golden moved.
