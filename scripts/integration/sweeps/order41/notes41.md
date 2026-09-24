# Order 41 — running notes (cycle 59; GO 2026-09-24 off vilan next @1265ea5d)

## GO
- The owner: "Go with all recs. `isize` can exist too if useful." R-a–R-e as recommended; I5 ruling 4 amended (isize permitted if free) — stamped on I5, A124, B382, C14, M86, A112, F18, E222, F33, F27, A122.
- Ledger next id 566; shared_census literal 140; 35 unreleased breaking entries; kolt RED 4/4 (A125, owner-owed).
- Playground store.vl:14 → `dyn Signal<List<Note>>` (integrator, at GO).
- Worktrees: vilan/.claude/worktrees/{hygiene,solver,index,reactive,collections,editor,native}-41 off origin/next @1265ea5d; proposals/.claude/worktrees/papers-41 (branch papers-41).
- Playground store.vl:14: `dyn Signal<List<Note>>` refuses line 27's `self.notes.update(..)` (`update` is INHERENT on SignalCell, not a trait member — the pipeline paper §5 (2)'s class); the field takes the concrete `SignalCell<List<Note>>` instead; `vilan check` clean on 1265ea5d3.
