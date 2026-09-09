# Order 31 — running record (integrator)

Opened 2026-09-09 off c3ed9239. Lanes: handles-31 (TOP), reverse-31, mutself-31, keyed-31 (droppable), rpc-smalls-31. Briefs: briefs31.md. Ledger next id 407.
- PROCESS (GO): the three-item filing ran with an unescaped pipe in B281 (INVALID, exit 1), but the commit after it still ran — the `&&` chain was broken by a heredoc terminator (the line after `EOF` starts a new command). Rule: a heredoc ends a chain; put heredocs in their own call or first. Filed at 94b9903 after the escape.
