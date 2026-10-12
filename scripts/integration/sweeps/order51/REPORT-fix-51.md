fix-51 hand-back (Opus 5.5). Branch `fix-51`. Nothing pushed, and none of my processes are still running.

**Shas**
- Base: ca407da0 (origin/next)
- Tip: c98db578
- Worktree: /home/reed/code/vilan-lang/vilan/.claude/worktrees/fix-51
- Status file (untracked): fix-51-STATUS.md

**Commits** (each one has a `## Unreleased` CHANGELOG entry with a family marker, except the ledger and pin-only commits)
1. b868dca0, **B577**, miscompile. When a call hands back a scalar view wrapped in an enum (`Some(&self.items[i])`), JS now reads the payload out wherever the option is used as a value. That covers `unwrap_or`, `map`, `is_some`, a forwarding method, a `let`, an `is` capture, a `!` lift, a list of options and a parameter typed `Option<&str>`. The read is a new `__payload_view_read` helper, and the const interpreter runs it too. A `match` keeps the pair only for a leg that captures it; a literal leg beside that capture tests the read-out value. `Option<&mut T>` gets the same read, because only the capturing `match` can write through it.
2. af7569fb, **B578**, miscompile. `&` of a call result (`&xs.len()`, `&seven()`, a generic return, an unannotated fn, a closure, a generic method) and `&` of a value `if`/`match`/block now get their own one-slot cell where the pointee is a scalar. A call that returns a view is re-borrowed as itself, not wrapped again.
3. c98db578, B578 pin for the generic-body case (`&identity(value)` inside a generic fn or method). This was a TypeError on the base.
4. 8d43b8a1, **G26**, fix. The const interpreter now handles `indexOf`/`lastIndexOf` in UTF-16 units, returning -1 when absent and placing an empty needle at 0 and at the length. A census pin evaluates every `str` method std declares at expansion time and checks each against its runtime answer.
5. 980ac416, **G27**, fix. A `macro fun` inside an inline `mod` is now registered under its mod-qualified name. Lookup goes from the innermost enclosing mod outward. A sibling mod and the file's top level still cannot see it. A name defined in two mods of one file is refused by name, since a file's macros compile into one world. Spec §10.1 updated.
6. 8a38a905, **G25**, fix.
   - The trait-object vtable is now recorded as a keyed emission in the const world. Const evaluation can therefore dispatch through `dyn`: `const let T: i32 = total()`, `const make().get()` and a `List<dyn>` inside a const fn all work.
   - A const result that is or holds a trait object is refused with a message saying so. It used to say "a `Shared` cell".
   - `[derive(Json)]`/`[derive(Wire)]` over a `dyn` member (a field, a `List<dyn>` field, or an enum payload) is refused above the generators by a new `dyn_member_derive_refusal`, placed next to B117's resource refusal.
   - Docs updated: spec/const.md §9.4 and std/encoding.md.
7. 102b5f90, diagnostics, my own find (B?2). `[derive(Storable)]` without `import std::reactive::store::Storable;` used to blame "a compiler load-ordering bug (B21's class)". It now writes the import line.
8. 073788b6, tooling. Three NEW rows in diagnostics-ledger.tsv. The matching prose rows are appended to proposals/projects/vilan/proposal/diagnostics-ledger.md, uncommitted, for you to commit.

**Where the premises were wrong**
- **B577:** wider than a list element and `unwrap_or`. Every value consumer of a wrapped scalar view was broken, a scalar field (`Some(&self.title)`) too, and so were `Option<&mut i32>` consumers and literal match legs (`Some("first")` compared the pair). It is not specific to `&str`.
- **B578:** not specific to generic `&T`. A concrete `&usize` parameter also threw. A `let v = &seven()` used later and value `if`/`match`/block operands were broken the same way. The root cause is that a call's result stores no type of its own, so the transformer's scalar test answered "no".
- **G25:** the const half is not about `const let C: dyn Src` alone. Any const evaluation that builds a `dyn` internally failed, because the vtable was never recorded as reached. The `dyn` const result itself cannot be data, so it is refused by name.
- **G26:** matched the premise. The census found no other missing `str` method.
- **G27:** the macro was not merely out of scope. A `macro fun` inside a mod was not registered at all.

**Gates**
- Full suite (`--cargo-profile ci-test -E 'not binary(deep_nesting)' -j 6`): 10287/10287 passed, 31 skipped.
  - Inside it: ci_ignored_pins 12, hygiene 3, corpus 13 (JS corpus byte-identical, no goldens regenerated), check_scope_differential 15, native_differential default mode 261, diagnostics_ledger 25, docs 12.
- `VILAN_NATIVE_DIFFERENTIAL=1` sweep: 261/261.
- Deep-nesting canary at 2 MiB: 18/18.
  - At `VILAN_CANARY_STACK_KIB=1536` it is 17/18: `a_thirty_level_chain_still_fits_libtests_own_two_mib_thread` aborts with SIGABRT.
  - It fails identically on a base checkout at ca407da0. That is N169, incr-51a's item, not mine.
- `cargo clippy --workspace --all-targets -D warnings`, `cargo fmt --check` and `vilan fmt --check .` are all clean.
- `scripts/ci-local.sh perf`: green (T2, growth ×1.929).
  - Against the base release, all 14 rows are between -0.04% and +0.16% in instructions (e.g. plain:320 +0.163%, genapp:46 +0.089%). No bump needed.
- kolt cold-check RSS median: base 269124 KB, tip 268528 KB (-0.2%). Kolt checks clean.
- `scripts/ci-local.sh wasm`: green.
- Website playground smoke (`smoke-playground.mjs`) on a scratch copy with the tip wasm: all claims ok. The website `node scripts/test.mjs` with the tip toolchain: PASS (6 files).

**Probe** (all on scratch copies, no git in the website or kolt)
- The website's `vilan build .`, all 11 examples and a kolt copy all build byte-identical between base and tip.

**Changed in analyzer.rs / mono.rs / emitters**
- analyzer.rs and mono.rs: none.
- Emitter, transformer.rs:
  - B577: `walk_entity_seams`, the `Expr::Match` arm of `walk_entity_inner`, `helper_source`, Transformer fields. New functions: `read_out_a_payload_view`, `payload_view_read`, `payload_view_variants`, `scalar_view_variant`, `captures_a_wrapped_scalar_view`, `pattern_reads_a_kept_payload`.
  - B578: `value_resolves_to_scalar` and `scalar_view_of_place`. New functions: `call_result_resolves_to_scalar`, `call_returns_a_view`.
  - G25: `emit_vtable` and `EmissionRecorder`.
- Late writes are untouched, since the analyzer is untouched.
- Also changed: interpreter.rs (`call_host`, `call_string_method`, `utf16_position`, `value_to_const`, `closure_captures`, the `Vtable` eval) and macros.rs (`macro_funs`/`MacroFunSite`, `scoped_macro_name`, `MacroScope::get`, `register_file`, `dyn_member_derive_refusal`, `IMPORTED_STD_DERIVES`, the `Derive` arm).
- No other lane's files touched, except new tests in native_differential.rs (two test fns plus `native/payload_view_element_reads.vl` and `native/views_of_call_results.vl`), which the brief's "pinned on both backends" asked for.

**Finds** (filed in sweeps/order51/newitems51-fix-51.json; repros in sweeps/order51/fix-51/finds/)
- **F?1** (native-51's): natively, a literal leg (`Some("first") =>`) of a match over a call returning `Option<&str>` emits Rust that rustc refuses (E0277).
- **B?1** (analyzer): the Wire/Hashable derive field check prints a `dyn` field's type as `_`, and it still fires after G25's refusal, so the same field is reported twice.
- **B?2**: the Storable steer above, already fixed.
- **G?1** (question): a mod's macro cannot be reached from outside the mod, so `export macro fun` inside an inline mod exports nothing.
- **N?1** (native-51's): vilan-rust `type_of` looks up `inferred_return_types` by call id, but that table is keyed by function id, so the lookup never hits.

**Questions for the owner**
1. G?1: should an `export macro fun` inside an inline mod be importable? Recommendation: refuse `export` there with a steer now, and make it importable once inline-mod imports are specified.
2. B577 also reads out `Option<&mut T>` payloads at value positions on JS, where native refuses them by name (F99's open half). Is JS answering with a copy acceptable until F99's second half lands? Recommendation: yes. The analyzer already refuses writes there, so the read-out cannot lose a write.
3. G25 refuses `dyn` const results, and Json/Wire derives over `dyn` members, by name rather than supporting them. Recommendation: keep that permanent. A vtable is code, and a `dyn` value has no type to decode into.
4. The ledger rows landed as a separate commit, because no rebase was allowed. Fold them into the G25 and G27 commits at merge if you prefer. Recommendation: either is fine.
