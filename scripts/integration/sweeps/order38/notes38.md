# Order 38 — running record (integrator)

Opened 2026-09-21 off 0fa109eb (Order 37's sealed tip 31c13567 + 9e4ab461 Dependabot-against-next + 0fa109eb the 1.98.1 toolchain pin). Ten lanes — see go-items38.json. Rulings R1–R8 all as recommended ("Go with all recs (including the before go points)").

- GO: 0fa109eb pushed to origin/next (9e4ab461..0fa109eb); worktrees are cut only after its CI run reads green (first CI run under 1.98.1 — the rust-cache is cold). A110/A111/A112/B359 + briefs38 + this file committed at GO.
- Watch-outs from Order 37: lanes kill by PID only; a lane that cannot sign says so at its first commit; a rowed message is one `\`-continued literal; a deleted list-const entry is named like an edited one; new test files use the scratch root; a new crate runs agents_map + third_party_notices; the split golden regenerates once over the merged tree, judged gensym-normalized; verify every `--test` name against crates/<crate>/tests before a merge; never launch a merge before reading the previous one's outcome.
