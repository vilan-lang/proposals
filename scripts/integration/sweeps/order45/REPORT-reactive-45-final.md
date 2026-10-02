# reactive-45 FINAL REPORT (condensed by the integrator; Opus) — tip 1658fc57 on d9d786ed; phase 1 (see REPORT-reactive-45-phase1.md) + phase 2

Phase-1 shas after the rebase: J7+M92 f7bf840e; field writes 98b0ffc9; M93 ad64727b; A146 7ba8502c; A135 tail f00fcabf; R-k 0a25e542; A144 b8c46377; fmt 041c1fd8; censuses 2de3f1ce, 76edffa6.

Phase 2:
- R-c: `SignalCell::new`/`Signal::new` take `own` — d9fa90a0.
- B482's std half — 71da0df7 (+0a82ae37, 1658fc57), BREAKING: `on_change`, `sub`, `effect_on_change`, a mirror's inherent `sub`, `std::ui`'s `on`/`on_event` take their callback `context tracking` and call under `tracking.clear(..)`. COMPILER CHANGE in context.rs: a trait member's clause parameter joins one carrier class with the same parameter of every implementing member (without it a literal through a bound read the context as present on JS, and every native program using `effect` was refused by rustc). Migration: wrap a callback VALUE in a literal (`|v| react(v)`) or type it `(|T| void) context tracking`.
- F60 — 84da04a5: premise CORRECTED — `[must_use]` exists on functions only; built as a TYPE RULE in analyzer.rs `check_must_use` (a discarded statement whose type is a struct implementing std's `Pipe`/`CollPipe`, or `dyn Pipe`, warns). One NEW ledger row: "unused pipe: a pipe runs nothing until it is consumed — …".
- Workarounds removed — 7b26e61e (+0c6631ff fmt): the 14 duplicate `Source` arms; `map_each`'s detour; the B478 wrappers in router comments, four guide pages and two examples; transient.vl's B477 comment. Left: `scoped_effect`'s `|v| body(v)` (a clause conversion), `MaybeSignal`'s wrapper (B482's migration).

Gates on the final tip: nextest 9253/9254 → the one (B249's steer text) fixed in 1658fc57; native_differential 119/119 both modes; check_scope_differential 15/15; fmt, clippy, `vilan fmt --check` std clean.
Goldens: 14 corpus + split (R-c), 11 corpus + split (B482), list-cell. JS copy census 567 → 585 (phase 1 over next) → 571. Leak census 0 live. Phase-1 CHANGELOG entries quote census numbers from earlier bases.
Kolt: nothing to apply (no callback values, no `track()`).
Finds FILED: F78, B510 (both not live); B500, B501, F74 from phase 1. A struct-level `[must_use]` attribute is possible later (parser).
