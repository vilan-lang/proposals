## layout-48 report: both items are done and every gate is green on next @8ab08bb2

**Branch:** `layout-48`, tip **7754011a**, on origin/next @**8ab08bb2** (that is incr-48 and std-48 merged). Two commits, nothing pushed.
- **Worktree:** `vilan/.claude/worktrees/layout-48`. `LANE-STATUS.md` there is untracked and current.
- **Rebase history:** origin/next moved three times while I worked. I rebased e75bc57c → dfe0c5fc → ecf3aef5 → 8ab08bb2.
- **Every gate below is from 8ab08bb2.** Because incr-48 has already merged, the brief's planned rebase onto incr-48 is done.

### Item 1: F28 + E266 + B548 (B549 closes with it), commit 9b4b201d, family `fix`

**F28.** The twelve single-platform std modules moved into the base root, each led by a module declaration. Import paths do not change.
- `[platform("browser")] mod self;`: `src/web/{dom,router,storage,dev}.vl`.
- `[platform("@process")] mod self;`: `src/{fs,http,db,process,watch,build}.vl`, `src/web/document.vl`, `src/rpc/server.vl`.
- **`std::web::ui` stays layered** (`src/browser/web/ui.vl`, `src/process/web/ui.vl`). Its twin structs differ, and twin structs (F27 R5) are not built. So the layer directories do not fully disappear yet.
- **Messages changed** to the ruled label: "requires the `browser` platform its file declares" instead of "the `browser` layer of `std`".

**What stopped Order 46's attempt, and what is different now:**
- (a) `router`'s fence walk ran against the process `ui` twin and reported six violations inside std.
- (b) `infer_platform` only took browser evidence from the layer directory.
- (c) New this time, found on the kolt copy: once `rpc::server` declared `@process`, every function in it became a fence. That walk reached `std::web::dom`'s `Event::key`.
  - The cause was a pre-existing imprecision. For a parameter with two bounds (`T: Wire + Keyed<K>`), dispatch looked only at the first bound and then fell back to every method named `key` in the program.
  - Fixed in `async_infer::dispatch_candidates`, which now looks the member up in every bound.

**The real cause of B548/B549, and where the item's premise was wrong:**
- B548's diagnosis is right: one program has one platform, so a twin import binds the build's side.
- The brief's literal fix ("bind the importing file's side") would need two `std::web::ui` modules in one program. I did not build that. Element syntax, the web prelude and unfenced shared modules would still bind the build's side, so a browser-declared file would get type mismatches in a node build instead.
- What I built instead:
  1. **Twin stand-in rule.** A fence walk for a host does not charge a reach into a layered module's twin when that host has its own twin of it. A module with no twin, such as `std::fs`, is still charged.
  2. **Spec §11.3 as already written.** "Of the entries that reach the file only those it admits type-check it": a module whose own platform excludes the build is loaded so its names bind, but that build reports nothing from inside it. An import of it stays legal, and a call into it is one error at the caller.
  3. **`vilan check` keeps coverage.** A declared module in the user's own package that only excluding legs load is checked as the file itself, under its declared platform.
- For B549 itself, the last remaining error was a misattributed `resolve_world` miss ("cannot find 'render' in module 'ui'", printed with no location). I anchored it in its own file.

**E266:** `infer_platform` now treats a std module whose file declares only `browser` as browser evidence, exactly as it treated a browser-layer-only module.

**Also in this commit:**
- The library contract holds a declared base file to its own declared platform.
- Fence promises in std or an external dependency are no longer re-walked in a consumer's build. Before this, they cost 6% of kolt's check; what the consumer's own entry reaches is still checked.
- Spec §11.1 and §11.3, the platforms tour, the errors appendix, the glossary and the std pages are updated.

### Item 2: B556, commit 7754011a, family `fix`

- **Cause:** `find_project_root` walked up the path as typed. `Path::parent("main.vl")` is `""`, so the walk stopped there and found no package.
- **Fix:** it now climbs the real directories (through `..`) and stops when climbing no longer moves. The answer keeps the user's spelling, so error paths render as the user typed them.
- **A second bug fixed by the same change:** from inside a package, `vilan check ../scratch/x.vl` used to compile a manifest-less scratch file under the working package's manifest.
- `vilan check --fix`'s manifest lookup uses the same walk, so it is fixed too.

### Pins (each shown red with its fix removed, then green)
- `module_resolution`:
  - Order 46's three `f28_*` pins, red on the fenced tree before the fixes.
  - `f28_a_declared_module_is_checked_by_the_builds_it_admits`
  - `f28_contract_holds_a_declared_base_file_to_its_own_platform`
  - `f28_a_dependencys_promise_is_not_rewalked_in_a_consumers_build`
  - four `b548_*` pins
  - `b549_a_browser_build_importing_the_document_module_checks_clean` (un-ignored)
  - `a_qualified_module_member_miss_is_anchored_in_its_own_file`
- `inference::platform::a_member_of_a_second_bound_reaches_only_that_bounds_implementors`
- `workspace::f28_vilan_check_checks_a_declared_module_no_leg_admits`
- `workspace::b556_a_file_addressed_from_inside_its_package_finds_the_package` and `workspace::b556_a_file_outside_the_working_package_is_not_claimed_by_it`
- I also updated existing pins and the shared census for the new label and paths. No ledger rows were added (no new message forms).

### Needs your ruling
1. **The B548 mechanism:** a module its build excludes is not reported by that build, plus the twin stand-in rule, instead of binding the importing file's twin. Rec: accept. Spec §11.3 already says it.
2. **Fence promises of std and external dependencies are not re-walked in consumer builds.** This bends the docs' "every compile" to "every compile of the package that declares it". Rec: accept.
3. **The `vilan check` extra leg** for declared modules that no leg admits. Rec: accept.

### Finds
Filed in `sweeps/order48/newitems48-layout.json`, repros under `layout-48/finds/`:
- **B?1:** `resolve_world`'s other path-resolution refusals inside a module are drawn against std's `lib.vl`. I fixed only the one arm B549 needed.
- **E?2:** E266's other half. A `pkg::` or dependency module that declares `browser` is not yet browser evidence.
- **B?3:** `vilan check` on a nested `[library]` file resolves `pkg::` from the file's own directory. It fails the same way on 0.45.0.

### Gates (all on 8ab08bb2, tip 7754011a)
- `cargo nextest run --workspace -j 6`: 9,847 passed, 34 skipped. This includes `check_scope_differential`, `std_twin_parity`, the docs gate, the examples, corpus and diagnostics_ledger.
- `native_differential` with `VILAN_NATIVE_DIFFERENTIAL=1`: 202/202. The default mode ran inside the suite.
- clippy `-D warnings`: clean. `cargo fmt --all --check`: clean.
- `ci-local.sh` vilan-fmt, wasm, windows and perf: all green. Perf T2 green, growth ×1.999.
- **kolt check** (release, `VILAN_SEQUENTIAL_CHECK=1`): 15,620.1M → 15,712.4M instructions, +0.59%. RSS flat at about 205 MB.
- **Scratch copies of kolt and the website** (copied with `cp`, no git run in either): `vilan check .` is clean on all entries, and `vilan build .` builds kolt's 2 legs and the website's 4.

### Functions touched
- **analyzer.rs:** `check_library_contract`, and one arm of `resolve_world`. Late writes stay at zero; the inference suite runs with that assert.
- **lib.rs:** `infer_platform` (plus a nested `declares_only_browser`), `post_analysis_passes`.
- **platform_color.rs:** new `sources_outside_the_build`, `drop_diagnostics_outside_the_build` and `twin_stands_in`; changed `check_fences` and `Traversal::walk`.
- **async_infer.rs:** `dispatch_candidates`.
- **vilan-cli main.rs:** `find_project_root`, `check_single`, `check_workspace`, and new `check_declared_modules_no_leg_admits`.

No permission refusals came up.
