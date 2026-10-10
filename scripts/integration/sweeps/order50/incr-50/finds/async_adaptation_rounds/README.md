# M138 — `async_infer::compute_adaptation` runs twice per analysis over every function (2 × 11 ms on kolt's client leg); its cold half is not in M110 S3's record

Repro: apply `async-probes.patch` (needs the probe module from the sibling find), build, then
`VILAN_CTX_PROBE=1 vilan check .` on a kolt copy. The client leg prints
`[probe async] ... adaptation 22.6 ... running-bindings 31.8` and `[probe adapt-keys] 4585` twice: the
outer loop in `infer` runs the base fixpoint, then `compute_adaptation` over ALL functions as (f, ∅)
instance keys (4,585 on kolt), and repeats both whenever the adaptation grew the async set — on kolt
always once more. Order 50 seeded the base fixpoint from the record's cold result (S3b) and took
`reachable_bindings` off the common path; the adaptation stays whole-program because a seeded form has
to carry the cold instances `(callee, bits)`, their origins and the diagnostics they produce in the
record, and a cold instance reached only through a hot call is minted by the hot caller. Sizing M.
