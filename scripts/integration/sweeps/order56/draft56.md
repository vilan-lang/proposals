# Order 56 — draft (2026-11-03, after the post-Order 55 rulings)

Base: next @5fd01232 (CI green 14/14; every post-order lane landed: B693, M185, M186, parser-56, std-56, incr-56, solver-56; six perf bumps; the E121 interim targets). Exhibit: kolt @3fb5d74 (`VILAN_PERF_KOLT_COMMIT=3fb5d74`, no tip copy). Open items: 160. The release at the seal is **v0.54.0, BREAKING** (B688, B677 door 2; A182 and M191 if they land; the dp codemod optional).

Cap: FIVE lanes at once (CARGO_BUILD_JOBS=6, nextest -j 6). Fable 5.1 only where named; the rest Opus 5.5 (Sonnet for the tooling lane's small items). Every lane's gates end with the vilan-fmt leg and ONE full suite; every lane that touches the analyzer runs the differentials.

## Wave 1 (five lanes)

**lang-56** — the import foundation. (1) **A183 the paper** (FABLE, S–M, deliberately: the language's resolution model — root values, projections, `use`; the elaboration table for every current spelling; `import` the one keyword in two positions; bare root heads as sugar; `self`/`super` as implicit location-derived reserved bindings, `super` one level; the inline-path-vs-admission ruling with a rec; the slices). Then on Opus: (2) **A181** absolute-path subjects in every type position, the bare `m::(impl T)` form, `(impl *)`, `_` = unspecified / `*` = everything in the spec; (3) **A182** leaf-only admission + the package prelude — the ESTATE CENSUS first (std, website, corpus, docs, kolt), breaking; (4) **E359** rides A181. Order: paper → A181 → A182 → E359. The analyzer's resolver is this lane's; the solver lane stays out of `resolve_*`.

**solver-56** (Opus) — **B690** + **B691** first (the two JS miscompiles: a module `const let` read only through operator dispatch never declared; an enum value never copied at a value seam), then **E360** (a path through an imported function reports only the cascade), **A180** (door 2's marker trait: the paper slice WITH THE EVIDENCE — the census of owner-registered types, the counter-example, the opt-out question — then the build), **B695** (a cut inside a surrogate pair rounds to the code point on both backends; every UTF-16-indexed `str` operation pinned on the differential), then **B682** (un-annotated `Ok`/`Err` list) and the **B646 guard** (refuse `[track_caller]` on compiler-called trait members) if time.

**std-56** (Opus) — **M191** (the paper slice first: hash-map-lend.md §9 → the two-parameter NativeMap with tombstones on both backends, `slot(key)` borrows self, `Option::get_or_insert`, `update` removed; measured on kolt's map-heavy sites), **M190** (image: `resized` answers `Result`; JPEG onto black; blob rebuilt), **B696** (`assume` carries `context owner_scope`; estate census), **B694** (the server twin disposes its one-shot owners), **A178's two** (`Style::raw` picks the role from the property name; `with_length_as` back), then **M173** (the store's per-key diff) and **M179** (a handler panic answers 500 on both backends) if time.

**incr-56** (Opus) — on the N186 series (exhibit 3fb5d74; base = a release build of 5fd01232 kept aside): **M188** (a per-callee retaining summary over a body-expression index, the S7 record form), **M189** (the capture scan as a per-closure memo), then the next post-pass by cost — contexts+graph (~180 ms) or the const post-pass (~200 ms) — as a record; **M163** re-weighed with the new `plan_resource_drops` figure. Alone in the CHECKS phase; merges after solver-56 and lang-56, with the differentials re-run on the merged tree.

**tooling-56** (Sonnet; Opus for B687) — **B687 FIRST** (M164's refused-body case asserts on the SERVER's byte count — zero is the contract — or windows-skips the Node leg by name; three recurrences), **N188** (the 900 s corpus-as-modules differential split per program), **E357** (a lone file outside a project reflows no comments), **E358** (the harness records the phase line and the analysis count per sample so an outlier names its cause), **E341** (`--watch` forwards SIGTERM/SIGHUP), **E342** (fold), **N183** (the text-based macro gate), **E346** (debug escaping of control characters), **E347** (`return f(..)` never breaks — fmt).

## Wave 2 (as lanes free)

- **ui-56** (Opus): **M187** (`cut_row`'s live DOM Range per row: no Range per row; `close` removes the run in one step; skip under a closing ancestor; the process twin in step), then **E345** (UI bindings and derivations in the trace).
- **native-56** (Opus): **F153** (a native `for` over a resource), **F154** (a str-backed enum's `.value()` natively), and the F1 S1b question (the native WebSocket dial inherits A179's two arms).
- **http-56** (Opus): **M176** (`Request::body_stream()`), **M177** (multipart on the stream).
- **papers**: **M174** (`[default(..)]`), **M175** (`SqlValue`), **A175** (revoke by value, door 1).

## The seal and the cut

1. `df -h` at GO; `cargo clean` the integration target at the seal.
2. seal-56.sh: `VILAN_PERF_KOLT_DIR=$HOME/.vilan/perf-exhibit/order56/kolt`, `VILAN_PERF_KOLT_COMMIT=3fb5d74`, no `VILAN_PERF_TIP_KOLT`; the e121 rows' interim targets re-taken on a quiet box (the advance conditional on a green verdict — incr-56's patch is in); the kolt `[[bump]]` row if the warm check moved.
3. The v0.54.0 cut (BREAKING): the notices regenerated; `--release` absorbs the 23+ bump rows and re-bases the ci ceilings; kolt under 0.54.0: B688 (committed 3fb5d74), then `vilan fmt .` (E354's six sites + any A182 imports), M181's externs dropped, `dial_within` in the connect loop, the dp codemod optional, `update` sites rewritten to `slot` if M191 lands; delete release/0.53 after the fold.
4. Records: sweeps/order56/; the chronicle; owner questions; memory.

## Standing owner-owed

The kolt adoptions above; the F5 check of the debugger additions; L24 (the Windows runner); the `any` question (std-55 Q2); E334/E343 (the E126 exhibit).
