# M137 — `context::apply` materializes one reference entity per threaded argument (66,189 on kolt's client leg: ~40 ms of `entity_map` inserts + 14 ms of argument pushes per analysis)

Repro (next @5fe24f86, release): apply `context-probes.patch` (and drop `probe.rs` into
`crates/vilan-core/src/`, `pub(crate) mod probe;` in lib.rs — the CPU-time probes incr-50 measured with),
build `vilan-cli`, then on a kolt copy carrying `src/lucide`:

    VILAN_CTX_PROBE=1 vilan check .

The client leg prints `[probe plan] thread_calls 66189 gets 19 param_nodes 6899 ... entity_map 179212` and
`[probe apply-split] mint 39.5ms push 14.3ms`: every call to a needy function gets a fresh
`Expr::Local(parameter)` entity per context (`ThreadForm::Param`), inserted into a 179k-entry map that
doubles under the inserts, and every call's `argument_ids` reallocates for the push. The whole context
pass is 115 ms on that leg; `apply` is 26–48 of it, on every analysis, served keystrokes included (the
mutation log replays the cold rows; applying them is still a tree edit per row).

Candidate fix: one reference entity per (node, context) — the same `Expr::Local(parameter)` read in every
threaded call of that node — cuts the mints to ~6.9k (one per param node). It changes the tree shape the
emitters read (an entity shared by several calls' argument lists), so it is gated by the native
differential and the corpus goldens; an emitter keyed by argument entity (a per-entity memo) would have
to be checked first. Sizing S–M.
