# solver-a-45 REPORT (condensed by the integrator; Opus, 508k tokens) — tip 2477ae79 off 6e6830df

| item | sha | note |
|---|---|---|
| B473 | 30b6eb56 | premise held, both backends; the analyzer recorded the BOUND's trait, not the declaring trait — fixed at the method call, the generic `for`'s `next`, the qualified `Sub::name(x)`; B359's sub-trait face moved into `mono::select_member_through_subtraits` |
| B467 + B439 | 5dbc8430 | moved ahead of R-c (R-c depends on it): a closure's own view parameters are not captures |
| R-c: B483 + B466 + B465 | 851c747c | std storing constructors take `own` (`Shared::new`, `ListCell::of`, `ListCell::with_limit`, `Tracked::new`); JS: an `own` parameter of a copied type is a dead owner at its last use; `*view` is a copy candidate; new pass `adopt_closure_parameter_views`; `out = c` (c a view) refused without `*` — for `fun` too (0.42.0 accepted it and leaked the pair). |
| B474 | 0e0a8e2d | pins only; B473 was the root |
| B453 | 14999345 | the JS view of a tuple position is (tuple, flat offset) |
| B444 | d9b4bad8 | a scalar view at a binary operand / by-value argument is read through on JS |
| B464 | 2477ae79 | BREAKING: a bare place at a closure view parameter is refused (`&mut place`); rpc.vl `KeyedCell::update` one line |

Gates at the tip (base 6e6830df): nextest 9173/9173 (39 skipped); doc-tests; whole-set native differential 100/100; fmt, clippy, `vilan fmt --check` clean. Walk untouched.
Goldens: 15 corpus programs + split `app.js` (all R-c, runtime-identical). Copy census 578 → 557. Native copy census: moved column only.
Ledger: no NEW rows; two rows' prose gain "since Order 45 also raised at an assignment of a view into a value place (B465) / at a bare place passed to a closure-typed view parameter (B464)".
For reactive-45: `SignalCell::new`/`Signal::new` still take a bare `value` (copied inside at `Shared::new`) — make it `own` per R-c. Kolt: no edit needed (checked on a scratch copy).
Finds FILED: F69, F70, B495, B496.
