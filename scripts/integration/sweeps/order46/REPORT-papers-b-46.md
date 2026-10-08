## papers-b-46: both papers are written, and no tree was changed

**The papers:**
- `/home/reed/code/vilan-lang/proposals/projects/vilan/proposal/incremental-analysis.md` (M110)
- `/home/reed/code/vilan-lang/proposals/projects/vilan/proposal/debugging.md` (E257)

**Probes and scripts:** `/home/reed/code/vilan-lang/proposals/scripts/integration/sweeps/order46/papers-b-46/`
- `incr/`: `probes/i1`–`i7` with `run_all.sh` and `run_all.out`; `census.py`, `edit_classes.py`, `hot_set.py`; their outputs; `phase-kolt-0430.txt`.
- `dbg/probes/`: `d1`–`d12` with `run_all.sh` and `run_all.out`.

**New items:** `sweeps/order46/newitems46-papers-b.json` (M?1, E?1, E?2, E?3).

The report file itself was not written; this message is the report.

**What I could not measure.** I ran no cargo, no LSP session and no native build; loadavg was 7–13.
- All LSP numbers are cited from editor-46 and perf-b-45.
- My own measurements are static censuses, kolt's git history, and one `VILAN_PHASE_TIMING=passes vilan check` of a scratch copy of kolt.
- The native backend was read, not run.

### Paper 1: incremental-analysis.md (M110)

**Why every keystroke costs so much:**
- It runs per 150 ms pause, not per keystroke, but each pause re-analyses the whole entry world. Superseded analyses are cancelled.
- **Since M104, M19's reuse almost never fires.** A cache hit needs every loaded file except the entry to be unchanged (`analyzer.rs:66657-66666`). Under M104 the edited file is a module of the entry's world, so every edit outside `client.vl` misses: the world is evicted, rebuilt cold and cloned back into the cache (`:66935`).
- editor-46's numbers fit this exactly: `model.vl`, `views.vl` and the css file all converge on about 14.3 G instructions. That is about 1.3 s of CPU; E121's 500 ms target is about 5.5 G.
- Nothing records what an answer depended on. Ids are minted per occurrence, inference is one global constraint fixpoint, and four passes run from callees back to callers.

**This language makes body edits non-local.** Each of these probes ran on 0.43.0:
- i1: a body edit changes an inferred return type, and the error lands in the caller.
- i6: a body edit makes every caller async and gives each a hidden context parameter.
- i2: a context read added three calls deep produces a coverage error that names all three callers.
- i7: a `push` inside one function changes the type of a module-level binding, which breaks a sibling function that neither calls nor is called by it.
- i4: a `const` in another function fails.
- i5: a browser entry fails, and the error lands on an unedited function's body.
- i3: an impl in a module the user never imports changes method resolution. There is still no orphan rule.

How often this can happen in kolt:
- 37% of kolt's hand-written functions infer their return type.
- In the owner's `wip` commits, 57% of the edited function bodies were in those functions.

**Headline recommendation: firewalls inside today's analyzer, not a query-system rewrite now.** Each slice ships a measured win, and each boundary it creates is one a query system would need later.
- **S0:** per-item interface fingerprints (signature, inferred return, effects) and a global-facts fingerprint (impl headers, trait members, resource-ness), so we can finally measure what a keystroke invalidates.
- **S1, hot-set worlds (the cheapest step):** store the entry's world minus the edited module and everything that imports it. On kolt that "hot set" is 0.5–15% of the package's lines for every module except the generated lucide file. The measured analogue is the pre-M104 `views.vl` keystroke, which fell from 14.35 G to 9.27 G (−35%).
- **S2–S4:** reuse the remaining passes (resource classification, bound checks, liveness) over the unchanged part of the world, seed the contexts/async/platform passes from the stored result, and add the const cache. These are estimated to reach 4–5 G, inside E121.
- **S5–S7:** a spike on per-item id windows, then the interface firewall, then "a body keystroke re-checks one function".
- Find References stays whole-entry because the analysed world is always the entry's whole world.
- No behaviour difference is enforced by a new edit-replay differential (incremental against clean, byte for byte, with a planted bug per slice) plus a `VILAN_INCREMENTAL=verify` mode for dogfooding on kolt.
- The CLI benefits too: `--watch` and HMR get every slice directly, the records are persistable from day one, and per-module records split the checks phase for parallel analysis.

**Questions for the owner (each with my recommendation):**
- Q1: firewalls rather than a rewrite; revisit after S4 is measured.
- Q2: the hot set is the edited module plus its reverse import closure, including import cycles.
- Q3: the edit-replay differential blocks every slice from S1 on.
- Q4: no language change; inferred returns and effects go into the interface fingerprint, and M106 may later suggest annotations.
- Q5: the const cache key is the site's content, the content hashes of its callee closure, its input files and std's stamp.
- Q6: S5 stays a spike until S4 is measured.
- Q7: records carry no TypeIds and are content-keyed; the on-disk world stays at step 7 of the ruled order.
- Q8: an effect change always re-checks the callers.
- Q9: add per-edit counters to M105's tier 1.
- Q10: no special case for broken bodies mid-typing; S0 measures how often it matters.

### Paper 2: debugging.md (E257)

**What 0.43.0 does today:**
- `print` is `console.log` taking `any`, so it shows the JS representation:
  - `Point` prints as `[ 1, 2 ]`; `Some(5)` as `[ 0, 5 ]`; `None` as `[ 1 ]`; `Shape::Circle(1.5)` as `[ 0, 1.5 ]`.
  - A dyn value shows its method table, `Shared` and `SignalCell` show their internals, and `3.0` prints as `3`.
  - node's depth cut prints deep data as `[Array]`.
  - Resources and pipes are refused outright.
- Native deliberately writes node's bytes (`vilan-rt/src/inspect.rs`).
- The compiler already refuses to interpolate a struct into a string because that would render "the value's runtime shape", which is exactly what `print` shows.
- `Debug` covers only scalars and derived types.
- Panics carry no location on either backend.
- There are no source maps, and `vilan run` passes no flags to node.
- Generic functions are emitted as `$a` even in the readable debug build.

**Headline recommendation:**
- **`dbg` is a compiler intrinsic.** It must see argument source text, the call site and types, which neither a function nor a macro (macros run before types exist) can. It takes any number of arguments and prints `[file:line:col] expr = value` to stderr (`console.log` in the browser), using a generated printer that writes vilan's own literal syntax and is identical on both backends.
  - It returns its argument (a tuple for several).
  - In statement position it reads in place, so `dbg(guard);` does not consume a resource.
  - Release builds refuse it.
- **`dbg_stack()`** expands statically from the scope at that point. It shows parameters, locals and captures; shadowed bindings are marked; moved bindings show where they moved; invalidated views show no value; cells show their value through the untracked `get()`; pipes show their type only.
- **Debugger in stages:** source maps (with names, std on the ignore list, generated code mapped to its attribute), then `vilan run --inspect` plus a VS Code launch type that hands off to the built-in JavaScript debugger, then vilan-shaped variable values through a debug-info sidecar and a small DAP proxy. Native comes last, reusing the same sidecar for lldb/gdb pretty-printers.
- **`print`** adopts the printer for non-scalar values once `dbg` ships; strings and numbers print as today, which limits corpus churn, and F68 closes.
- **"Who woke this effect"** is a debug-build trace in `std::reactive` plus async stack tagging, built on one new primitive, `[track_caller]`.
- **First slice, S0 (S–M):** `[track_caller]` gives panics, asserts, index errors and unwrap their vilan location on both backends. It is small, useful alone, and builds what S8 needs. S1 (M) is `dbg` itself.

**Questions for the owner (each with my recommendation):**
- Q1: output in vilan literal syntax; one line when it fits 80 columns; floats keep `.0`; no depth cut; at most 100 entries per container.
- Q2: returns the argument, a tuple for several; reads in place in statement position.
- Q3: stderr everywhere except the browser, which uses `console.log`.
- Q4: release builds refuse `dbg`, with `[build] dbg = "strip"` or `"keep"` as an override.
- Q5: `dbg_stack` scope as above, with no module-level bindings; each listed binding counts as a use.
- Q6: a generic `T` on JS gets an implicit bound every type satisfies, emitted per instantiation like any bound.
- Q7: every type is debuggable; a written `Debug` impl overrides; std ships impls for its handle types.
- Q8: `print` adopts the printer for non-scalars, as its own slice after `dbg`.
- Q9: source maps on in debug builds, opt-in in release.
- Q10: build source maps plus `--inspect` now, the sidecar and proxy next, native last.
- Q11: add `[track_caller]`, and keep locations in release panics.
- Q12: reactive tracing in debug builds only.

### New items filed (`newitems46-papers-b.json`)

- **M?1 (HIGH):** since M104, every keystroke in a module of an entry world misses the base cache and re-stores the whole world. This undoes M19's reuse; incremental-analysis S1 is the fix, and there is an XS stop-gap (skip the store when an open buffer is inside the world).
- **E?1:** a panic carries no location on either backend; JS throws a bare string.
- **E?2:** generic function instances are emitted as `$a` in the readable debug build, so stack traces and debuggers show `$a`.
- **E?3:** `Debug` covers only scalars and derived types: deriving it fails on a struct with a `List` or `Option` field, `T: Debug` refuses lists, tuples and options, and `3.0.debug()` is `"3"`.