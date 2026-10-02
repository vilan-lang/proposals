# solver-b-45 REPORT (condensed by the integrator; Opus, 767k tokens) — tip 3f89b642, 13 commits on ba2eebd9 (rebase onto solver-a-45's merge OWED)

| item | sha | note |
|---|---|---|
| B475 | 55f59ca0 | a `dyn` table counts a bound's member in BOTH directions (`dyn Source` meets `S: Flow`); 3 dyn_objects pins + the collections pin un-ignored; golden `dyn-objects`; copy census 578 → 588; native copy census dyn-objects 2/21 → 31/57 |
| B476 + B477 | b39eda7a | blanket-provided arguments grounded at the home, the bound check and satisfaction; specificity reads bound ARGUMENTS (either declaration order); bare total-join `flatten()` refused once with the `switch(\|inner\| inner)` steer (F60's shape) |
| B478 | cc746fd4 | named functions and variants at all four clause landings; native adapts arity (vilan-rust `function_value`, `variant_closure`); ledger 219/220 re-keyed |
| B480 + B484 | e70e0943 | B484 held; B480 did NOT reproduce on next; native: an object provides its supertraits' arguments |
| B479 | 80c19142 | a generic carried by the receiver counts as an answer; native build still refused (F71) |
| B482 (context pass) | 769604c8 | BREAKING; calls under `C.clear(..)` through an injected value pass `None`; a literal reaching such a position takes `C` as an `Option`; strict read refused at the author's read; `Program::cleared_clause_contexts` for native; one NEW ledger row |
| B468 | 3f34dd48 | omitted defaulted struct/enum arguments padded from the declaration |
| B481 | c7cf4e9a | reproduced as filed; admission walks call AND for-each sites |
| B455 remainder | STOPPED | ruled (B) `(impl Box with One)` — Order 46 |
| B472 | 1566cfb6 | alias re-exports indexed; steers to `HashMap`/`HashSet` |
| B454 | bfd6d69b | premise corrected: a self-binding no longer replaces a held binding; `result-combinators` identical natively |
| B471 control pin | 8da64b60 | |
| F65 | 1a909f32 | the function-level `inferred_return_types` record is written only under an empty substitution; native-45's pin un-ignored |

Gates at 3f89b642 on ba2eebd9: nextest 9209/9209 (35 skipped); whole-set native 128/100/28/0; fmt, clippy clean; `vilan fmt --check` std clean, the TREE red on five native-45 fixtures (`tests/native/{dropped_pipes,generic_inferred_return,option_closure_fields,shared_view_fields,shared_view_places}.vl`) already on next. perf-45's memo key still determines the answer (checked).
NEW ledger row: "context `{name}` is read here, but this closure is called with `{name}` CLEARED: …" — B482 (R-g): a strict read inside a callback literal a callee calls under `clear`; anchored at the author's read; steer to `get_safe`. Pins inference::bounds b482_*.
For reactive-45: delete all 14 duplicate `impl type S: Source<..> with Slot/AttrValue/AttrBinding` arms (browser/ui.vl, process/ui.vl) — probed clean; transient.vl's "declared BEFORE … (B477)" comment; `|n| f(n)` wrappers; B482's std half builds on 769604c8. Kolt: no edit required; `count.derive(Some)` now works.
Finds FILED: F71, B497. Noted: B482's type-keyed native rendering (a shared interned closure type id would be a false refusal, never a miscompile).
