# native-45 REPORT (condensed by the integrator; Opus, 475k tokens) — tip 6984d3a0, 15 commits off 6e6830df

| item | verdict | sha | note |
|---|---|---|---|
| F62 | LANDED | 00497b58 | a field read through a view is one scoped borrow (`Shared::read_with`); a `write()` place settles its reads first; `shared.vl` joins DEFAULT_SUITE |
| F57 | LANDED | d82420ba | host by-value args copy; a `match` literal pattern takes its subject's width; new gate `every_platform_bound_program_is_identical_or_named` |
| F60 native half | pin only | 695a65d7 | premise CORRECTED: dropped pipes already built; the repro is B476/B477 |
| F61 | LANDED | 6a349e57 | closure TYPE orders hidden context slots by declaration; std's ordering comment dropped (reactive.vl, 4 lines) |
| F63 | LANDED | 8b67df2a | a closure's expression body is a consuming position |
| F64 | LANDED | c7faf517 | premise CORRECTED: the refusal was a literal through `write()`; a `match` leg handing back a place copies |
| F52 | LANDED | 0b715614 | module `lazy let` → `lazy` parameter passes a thunk |
| F54 | LANDED | c7ab8089 (+b1a48eee) | comparisons and `&&`/`\|\|` clear the inherited expectation |
| F55 | LANDED | b11433ac | a written annotation over an Option/Result variant initializer is emitted |
| M91 | LANDED | 50f4ee97 | `vilan_rt::Map` compacts when tombstones outnumber live; order kept |
| F65 | STOPPED | f52f927e, 6984d3a0 | the analyzer's `inferred_return_types` — to solver-b-45; ignored pin; `F` added to ci_ignored_pins' families |

Gates at the tip (base 6e6830df): nextest 9163 run / 9162 passed / 42 skipped (the one failure fixed by 6984d3a0, re-run 12/12); doc-tests green; native_differential default 104 + 1 skipped; whole-set 128/99/29/0 (base 128/98/30/0); async 7/4/3/0; platform-bound 8/4/4/0; fmt + clippy clean. Copy census: `shared` row added, elided-only moves; leak census 36 rows, 0 live.

For reactive-45: `OwnerCell` and `TrackRuns` can return to field writes; reactive.vl's TrackRuns comment and delta.vl's `ElementHold` comment are stale.
Finds FILED: F66, F67, F68, E243.
