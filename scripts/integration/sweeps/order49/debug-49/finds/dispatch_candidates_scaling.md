debug-49's find (perf): `async_infer::dispatch_candidates` costs O(impls of the trait) per generic
trait call site, with an O(candidates^2) dedup (`precise.contains`), and is asked per site from
async inference, the call graph and init order.

Measured building E283 (instructions:u, release, tip binary, plain:320 = 320 modules each with a
`[derive(PartialEq, Debug)]` struct):
- std with E283's `impl HashMap<type K: Hashable + Debug, type V: Debug> with Debug` (two generic
  `.debug()` calls in its body): 6,222,316,449; the same body with ONE call: 6,173,218,966; with
  none: 6,123,286,843. Each generic `.debug()` call std adds costs ~50M (0.8%) on plain:320 and
  ~12M on plain:160 — superlinear in module count, because every derived impl is a candidate.
- callgrind, plain:160, with vs without that impl: +50.4M inclusive in
  `vilan_core::async_infer::dispatch_candidates` (under `async_infer::infer` /
  `compute_adaptation`), the whole delta.
Fix shape: index `program.implementations` by trait once (or memo per (trait, member)), dedup
with a set. Owner: whoever owns async_infer.rs (incr-49's post-pass map lists it as stage 10).
