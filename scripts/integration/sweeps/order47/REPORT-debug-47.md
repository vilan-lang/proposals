## debug-47 — final report

**Branch `debug-47`, tip `4eab4128`**, on base `origin/next` @e5e15ca7. It is not yet rebased onto solver-47. Worktree: `/home/reed/code/vilan-lang/vilan/.claude/worktrees/debug-47`. Nothing was pushed.

**Built:** S0, S1, S1b (except `dyn`), S4 (partly), E259 and N136.
**Not built:** S2 (`dbg_stack()`), the `dyn` show slot, and S4's written-impl override. Details below.

### Gates (all on tip 4eab4128)
- `cargo nextest run --workspace -j 6`: **9663 passed**, 0 failed, 34 skipped.
- `VILAN_NATIVE_DIFFERENTIAL=1` native_differential: 166/166 passed.
- deep_nesting with `VILAN_CANARY_STACK_KIB=1536`: 18/18 passed.
- clippy `-D warnings`, `cargo fmt --check`, `ci-local vilan-fmt`, `wasm` and `windows`: all green.
- `ci-local perf`: T2 verdict green; growth x1.938 (limit x2.3).

### Commits, one per slice
| slice | sha | status |
|---|---|---|
| S0 `[track_caller]` (E258) | bbd25ec8 | done |
| S1 `dbg(..)` | a8bf2794 | done |
| S1b handles | c3389638 | done except `dyn` |
| S4 `Debug` (E260) | bf0a785f | done except the tuple case and the written-impl override |
| E259 instance names | da207fb0 | done |
| N136 number printing | f2a0e352 | done |
| pins/goldens re-read after the full suite | eeadb83d | — |
| perf fix: lazy site locator | 4eab4128 | — |

Each slice has its own CHANGELOG entry under a new `## Unreleased` section, with a family marker. There are 4 `NEW` ledger rows (two refusals for `[track_caller]`, the `dbg` release refusal, and "`dbg` takes no type arguments").

### S0: `[track_caller]` and panic locations (closes E258)
**How it works**
- New attribute `[track_caller]`, ranked between `[must_use]` and `[rpc]`. It is added to the spec, both highlighting grammars and the marker census.
- A post-analysis pass (`crates/vilan-core/src/track_caller.rs`, run right after the context pass) gives each tracking function a hidden trailing `std::debug::Location` parameter.
  - Every static call gets an `Expr::CallerLocation(site)` argument, or the enclosing tracking function's own parameter.
  - A closure is a boundary: a panic inside it reports the closure's own site.
- std marks these as tracking: `panic`, `assert`, `Option::unwrap`/`expect`, `Result::unwrap`/`unwrap_err`/`expect`/`expect_err`, `List::remove`/`insert`.
- Every `xs[i]` read, write and `&mut` view reports its own site.
- `std::debug::caller()` returns a `Location` with `text()`, `file()`, `line()`, `column()` and `Display`.
- Paths are relative to the package root (the directory holding `vilan.toml`, e.g. `src/main.vl`); std's read `std/src/…`.

**Example:** `values[5]` on a two-element list prints `panicked at d6_panic.vl:1:37: index out of bounds: the length is 2 but the index is 5` on both backends, exit 1.
- On node this line is the header of an uncaught `Error` (node's stack follows).
- Natively the line prints alone.
- A caught panic (`guarded`, a task failure) still answers its message alone.
- Release builds keep locations too (Q11).

**Refused:** `[track_caller]` on a trait method, and a tracking function taken as a value.

**Native change in `vilan-rt`:** `List::insert` past the end now panics as it does on JS (it used to clamp).

**Pins**
- `inference/debugging.rs` `s0_*` (4).
- `native_differential` `s0_every_panic_path_reports_its_vilan_site_on_both_backends` (15 paths, fixture `native/panic_locations.vl`) and `s0_caller_and_a_caught_panic_read_the_same_on_both_backends`.
- Proved non-vacuous by planting a bug.

### S1: `dbg(..)`
**How it works**
- `dbg` is a std `external fun` in the prelude; a program's own `dbg` still wins.
- The analyzer intercepts it in `resolve_call_subject` and types it in `infer_type`'s Call arm: the argument, a tuple for several, `()` for none.
- A *statement* reads its arguments in place (`Ref` conventions, no resource temporary). An *expression* moves them through (`Own`, and an aggregate is copied).
- Printers are generated per concrete type a `dbg` reaches. Both emitters build them from one classification, `vilan_core::printer::shape_of`:
  - JS: `__show_*` functions in `transformer/dbg.rs`, laid out by the `__dbg_*` runtime.
  - Native: `show_*` functions in `vilan-rust/src/dbg.rs`, laid out by `vilan_rt::show`.
- Output goes to stderr (`console.log` in the browser).
- Generic `T` prints per instantiation (Q6).
- `[build] dbg = "strip"`/`"keep"`: the release preset refuses at each call (checked in the CLI's `compile_to_js`); the debug preset prints.

**Example, identical bytes on both backends:**
```
[d1.vl:8:2] p = Point { x = 1, y = 2 }
[d1.vl:10:2] Shape::Circle(1.5) = Shape::Circle(1.5)
[d1.vl:19:14] 2 * 3 = 6
[d1.vl:25:2] -0.0 = 0.0
```
A value past 80 columns breaks one entry per line with trailing commas; a list stops at 100 entries with `… N more`.

**Pins**
- `inference/debugging.rs` `s1_*` (7).
- `manifest::tests::the_dbg_policy_follows_the_preset_and_the_key_overrides_it`.
- `infer_preset` release refuse/strip/keep (2).
- `native_differential::s1_dbg_writes_the_same_bytes_on_both_backends`: both stderrs equal the committed `native/dbg_printer.stderr`.

### S1b: handles
- `HashMap { "ada" => 36, "alan" => 41 }`, `HashSet { "a", "b" }`
- `Shared(Point { x = 7, y = 8 })`, `SignalCell(3)` (read without tracking)
- `<pipe Derive<SignalCell<i32>, i32, i32>>`
- `Shared(Link { label = "head", next = Some(<cycle>) })`
- Tasks print `<Task>`.

These are recognised by name **and** std residence. Pin: `native_differential::s1b_std_handles_print_as_themselves_on_both_backends` against `native/dbg_handles.stderr`.

**Not built:** a `dyn` value still prints `<dyn Area>`. Showing its value needs a `show` slot in the dyn tables on both emitters.

### S4: `Debug` (closes E260 except the tuple case)
- std adds `Debug` impls for `List<T: Debug>`, `Option<T: Debug>` and `Result<T: Debug, E: Debug>`.
- `f32`/`f64` keep `.0`: `3.0.debug()` is `"3.0"`.
- `[derive(Debug)]` on a struct with `List`/`Option` fields compiles.

**Held:** tuples. A tuple-family blanket impl is admitted for non-tuples at the bound check (find **B?4**), which made every type `Debug`. It is pinned `#[ignore = "E260: …B?4…"]`.

**Not built:** "a written `Debug` impl overrides how `dbg` prints that type" (Q7). That needs an owner decision, see below.

**Pins:** `s4_debug_covers_every_container_the_printer_prints`, `native_differential::s4_debug_over_containers_is_identical_on_both_backends`.

### E259: readable instance names
- In the readable build, an instance is named after its function (`first`, then `first2` for a second body); std reads `unwrap` and `is_some`, not `$f`.
- The names join the scope renamer's renameable set; a shared instance body's undeclared name is dropped from it.
- Release builds keep short names.
- Pins: `e259_a_generic_instance_is_named_after_its_function`; the two B102 pins now ask the instance memo (`instances_minted`).

### N136: number printing
- The analyzer records numeric `print` arguments (every integer width, `f32`, `f64`; not `BigInt`). JS wraps them in `String(x)`, so `print(0.0 * -1.0)` and `print(zero * -1)` print `0` on both backends.
- `f64-print-negative-zero.vl` moved from `OUTSIDE_THE_DIFFERENTIAL` into the default suite.
- Pins: `n136_print_writes_negative_zero_as_zero`, `native_differential::negative_zero_prints_zero_on_both_backends`.

### What the native backend refuses
I added no new refusals. Two pre-existing gaps shaped the fixtures:
- A closure whose body only panics does not build (**F?1**).
- A nested generic variant built inside a list is refused (**F?2**).

### Goldens and censuses moved
All moved goldens were judged by `regen_goldens.sh`; runtime output is identical except the negative-zero program, which is the intended change.
- 123 corpus `.mjs` files changed across the branch:
  - S0: 42 (location arguments);
  - E259: 81 (names), then 7 more re-compacted (names only);
  - N136: 86 (`String(..)` wrap).
- The split fixture, the `infer_preset` goldens, the copy and leak censuses (one new row each), and the markdown anchor golden (mdbook v0.5.4) also moved.
- Two `file.vl` witnesses were re-read.

### Frame measurement
- I added no arm to `walk_expr_node_inner`; the new analyzer branches are in `resolve_call_subject` and `infer_type_path`'s Call arm.
- `VILAN_DEPTH_STATS=1` on 13/33/103-level `.trim()` chains (release builds): expr-walk is 0.12 / 0.14 / 0.21 MiB on both base and tip, and infer is identical.
- The late-write assert held throughout the inference suite.

### Instructions, base (installed `vilan 0.44.0 e5e15ca7b` with base std) vs tip (release)
| subject | change |
|---|---|
| kolt `vilan check` (scratch copy) | 25,439,699,770 → 25,536,986,280 (+97M, +0.38%); exit 0 on both |
| math | +1.84% |
| watch | +1.63% |
| browser | +0.61% |
| fullstack | +0.55% |
| router | +0.59% |
| reactive-ui | +0.59% |
| ssr | +0.40% |
| canvas | +0.45% |
| rpc | +0.64% |
| todo | +0.49% |
| walkthrough | +0.34% |
| genapp:46 | +0.31% |
| plain:160 / plain:320 | +0.41% / +0.35% |

For a program that does not call `dbg`, the intrinsic itself adds only an id comparison per call resolution, empty-map lookups, and no printers. The fixed cost is S0 (the pass, the location arguments, std's tracking functions) plus S4/S0 std growth in the always-loaded `debug.vl`. Making the site locator lazy cut fullstack from +25.7M to +17.9M.

### Functions touched
- **vilan-core `analyzer.rs`**
  - Structs: `Function` and `ExternalFunction` (`track_caller`); `Expr` (new `CallerLocation`).
  - Analyzer fields and init, std id capture (`caller`, `dbg`), `Program` fields and construction.
  - Function-declaration walk (trait-method refusal); `check_unlowered_externals`; `drop_scan_children` and three other exhaustive `Expr` matches.
  - `resolve_call_subject` (dbg intercept, N136 recording); `infer_type_path` Call arm; `callee_conventions`; `compute_clone_sites`; `record_resource_temporaries`.
  - New: `resolve_dbg_call`, `dbg_call_type`, `classify_dbg_calls`, `is_a_number_type`.
- **vilan-core, other files**
  - `analyzer/liveness.rs`, `call_graph.rs`, `init_order.rs`: one exhaustive match each.
  - `parsing.rs`: `KNOWN_ATTRIBUTE_MARKERS`, `attribute_rank`, `parse_function`.
  - `node.rs`: `Func`. `formatter.rs`: function head printing.
  - `lib.rs`: `post_analysis_passes`, the synthesized `Func`. `interpreter.rs`: `__panic` host call.
  - `options.rs`: `DbgPolicy`. `manifest.rs`: `Build.dbg`, `build_options`.
  - New files: `track_caller.rs`, `printer.rs`.
- **vilan-core `transformer.rs`**
  - `helper_source` (`__at*`, `__panic`, `__dbg`, `__nursery_run`, `__force`); new `close_helper_dependencies`; `RESERVED_NAMES`.
  - Both assembly points; `Transformer` fields and new.
  - `walk_entity_inner` (CallerLocation, Index); the `__at_view` mint; both `__at_put` sites.
  - Call lowering (panic, caller, dbg, extern print); new `subscript_location` and `number_print_arguments`.
  - `expr_has_side_effects`; `emit_instance_with_bits`; `emit_default_instance`.
  - `NameGenerator` (`instance_name`, `forget_instance_name`, `instance_sources`); `rename_for_scopes`.
  - New `transformer/dbg.rs`.
- **vilan-rust `lib.rs`**
  - `PRELUDE`, `emit`, `Emitter` fields/new/`run`, `rust_type_inner` (`Location`).
  - `expression` (CallerLocation, Index), `mutable_place` (Index), `call_expression` (panic, caller, dbg).
  - New `caller_location_argument`, `subscript_location`, `rust_literal`; `scalar_host_binding` (`Location::text`); `intrinsic` (`ListRemove`/`ListInsert`).
  - New `dbg.rs`.
- **vilan-rt**
  - `lib.rs`: `Location`, `Panic`, `panic_at`, `panic_location`, `panic_report`, `run_guarded_main`'s hook, `describe_panic`, `list_remove`, `list_insert`, `Subscript`, `out_of_bounds`, `Shared::address`.
  - New `show.rs`.
  - `executor.rs`: `Failure::Panic` (now carries the location), `raise`, `classify`, `report_unobserved`, the nursery join.
  - **`inspect.rs` is untouched** (for native-47).
- **Other crates**
  - vilan-ide: `call_parameter_names` hides the hidden parameter.
  - vilan-cli: `compile_to_js` (release refusal).
- **std**
  - Edited: `debug.vl`, `io.vl`, `option.vl`, `result.vl`, `list.vl`, `display.vl`, `prelude.vl`.
- **Docs**
  - New: `guide/debugging.md`, `std/debug.md`.
  - Edited: `SUMMARY.md`; spec pages `grammar`, `lexical`, `appendix`, `execution` and `platform`; `appendix/cli.md` (the `[build] dbg` key); `tour/control-flow` and `tour/data-and-traits`; `std/option-result`, `std/misc`; `theme/vilan.js` (attribute and builtin lists).

### What comes next
- **S2 `dbg_stack()`:** not built. It needs:
  - the scope's bindings at the call site, with shadowed ones;
  - each listed binding minted as a `Ref` argument so liveness counts it as a use;
  - the move checker's verdicts before the expansion (a moved resource must print `<moved at L:C>`, not be read);
  - the view-invalidation verdicts;
  - and the capture plan for closures.
- **S1b `dyn`:** a `show` slot in the dyn tables of both emitters.
- **S3:** `print` of non-scalars can reuse `printer.rs` and `__dbg_layout`/`vilan_rt::show` directly.
- **S5 (source maps):** the site locator is the line/column source for both.
- **S6:** no dependency on this branch.

### Finds
In `proposals/scripts/integration/sweeps/order47/newitems47-debug.json`:
- **F?1:** a closure whose body only panics is refused by rustc natively (E0271).
- **F?2:** a nested generic variant inside a list is refused natively as "instantiated at `any`", even with an annotation.
- **B?4:** a tuple-family blanket impl (`impl type T: (2..: X)`) satisfies `X` for a non-tuple at the bound check, then emission dies with an internal error. This blocks E260's tuple case.

### Decisions for the owner
1. **Q7's override.** A derived `Debug` prints enum variants unqualified (`Circle(1.5)`), while the printer qualifies them (`Shape::Circle(1.5)`). Should a derived or written `Debug` impl override how `dbg` prints a type? If so, should the derive change its spelling to match? And should `.debug()` work on every type without a derive (an implicit bound for all types)?
2. **N136 and generics.** `print(x)` with `x: T` grounded to a float is not wrapped, because the recording is static. Is that acceptable, or should JS use a per-instance check?
3. **Statement form.** Only a `dbg(..);` written as a statement reads in place. A block-tail `dbg(guard)` moves, as Rust's does.
4. **`-0.0` under `dbg`** prints `0.0` under the `String(x)` rule; Rust prints `-0.0`.
5. **Q1's layout** puts a long numeric list one entry per line, which reads poorly. Should lists be grouped instead?
