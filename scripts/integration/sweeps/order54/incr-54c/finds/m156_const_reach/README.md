# M156 evaluated - the drop plan's roots the const pass reaches, on kolt

A temporary probe (not kept): `drop_plan_stats` recorded `plan_resource_drops`' scan roots, and
`const_eval::evaluate` printed, after the pass, the union of the const world's lowered functions
(`ConstWorld::reach_memo` / `union_memo` closures' `functions`) with their nested closures
(`CallGraph::closure_children_of`), intersected with the roots.

    VILAN_M156_PROBE=1 vilan check src/client.vl   (and src/server.vl), kolt copy, incr-54c tip

    client: sites 167, lowered functions 187, reached bodies 188 of 5,745;
            drop roots 301 (248 functions, 53 closures); reached by the const pass: 0
    server: sites 1, lowered functions 0; drop roots 256 (225 functions, 31 closures); reached: 0

On the served keystrokes (`lsp-latency.py`, leaf + css rows, the probe in vilan-lsp): every
analysis read 0 of its 290-301 roots reached (166 / 99 sites, 158-187 functions lowered).
