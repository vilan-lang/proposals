# The served keystroke's checks phase, per pass (incr-51b, Order 51)

How taken: `VILAN_COUNTERS=1 VILAN_PHASE_TIMING=passes scripts/lsp-latency.py --source <kolt copy> --lsp <bin>/vilan-lsp --runs 2 --scenario "leaf keystroke, world mode" --scenario "leaf keystroke"`, the server's stderr under `<scratch>/vilan-lsp.stderr`; the rows below are the LAST served keystroke of the world-mode scenario (hot-set world, base-cache hit). Release builds of the C0 tree (base, 765c931d) and the S7 tree (tip1). Box load ~1.2.

| pass (`[vilan pass]` name) | base ms | S7 ms |
|---|---:|---:|
| the drop extents, shared cells and capture plan | 48.7 | 48.9 |
| analyzer.check_resource_generic_instantiations() (R11) | 47.9 | 47.5 |
| analyzer.compute_resource_types() | 21.1 | 17.3 |
| analyzer.check_generic_bound_satisfaction() (the bound audit) | 16.0 | 16.1 |
| the remaining tables, labels and records | 14.2 | 16.2 |
| analyzer.infer_bumps() | 12.6 | 14.1 |
| liveness::LastUse::compute | 12.3 | 11.3 |
| the stage hints and auto fills | 10.4 | 10.6 |
| analyzer.check_resource_moves() | 10.0 | 10.4 |
| analyzer.compute_clone_sites() | 9.6 | 11.0 |
| the view, clone and hmr plans | 5.8 | 6.3 |
| analyzer.check_view_escape() | 5.6 | 6.0 |
| analyzer.plan_resource_drops() | 5.0 | 5.5 |
| analyzer.check_container_resource_arguments() (R10) | 4.1 | 4.1 |
| analyzer.check_invalidation() | 3.8 | — |
| analyzer.record_lazy_arguments() | 3.5 | 4.3 |
| (phase line) checks | 264.8 | 271.9 |

S7's counters on that keystroke: `records-served=39 records-stale=7 records-filed=7` (46 filed on the open). The item records serve, and the phase does not move: every pass above sweeps the whole program's entities (the client leg's 150k) and skips a reused one by a binary search each, or is whole-program by construction (R11; the six held table passes of the first row). The door is M?1 (live-range iteration + records for the held passes), with M?2 (the bound audit's site walk) as its smallest piece.
