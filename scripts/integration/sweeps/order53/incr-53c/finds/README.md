# incr-53c finds (Order 53)

- `m138-async-probe.patch` — the temporary async-pass probe (apply to the tip, `VILAN_ASYNC_PROBE=1`,
  run `scripts/lsp-latency.py` with `VILAN_PHASE_TIMING=1`): prints the seam state per analysis
  (`seam / seeded / record / matches / cold`), the base fixpoint and adaptation times per round and
  the decisions pass time. It is how the lone-document keystroke was seen to be UNSEEDED
  (`seeded false record false` on every `leaf keystroke` analysis; `seeded true` on the world-mode
  row) — find M?1 of `newitems53-incr-53c.json`.
- R11's instance census (the R11 paper §1.3) came from a temporary counter in
  `check_resource_generic_instantiations` (`VILAN_R11_PROBE`), not kept: it counted the worklist's
  instances, admissions, std callees and violations.
