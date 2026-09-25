# Order 42 — running notes (cycle 60; GO 2026-09-25 off vilan next @d65d4e75)

## GO
- The owner: "Go with all recs." R-a–R-e as recommended; stamped A130, B413, B415, I5 (stamps42-go.json); the cut plan's Q1–Q5 recorded in go-items42.
- Ledger next id 570; shared_census 143; 35 unreleased breaking entries; kolt RED 4/4 (A125, owner-owed); website 7 uncommitted (owner's).
- Worktrees: vilan/.claude/worktrees/{std,solver,collections,native,syntax,index,reactive}-42 off origin/next @d65d4e75; proposals/.claude/worktrees/papers-42 (branch papers-42).
- Merge order: std, solver, collections, native, syntax (rebased), index (rebased), reactive (rebased, LAST); then the seal, CI, THE CUT.

## mid-order
- syntax-42 QUESTION: `resource enum` is a shipped form (the brief said struct only — my under-count). ANSWERED (a): `[resource]` on struct AND enum, a pure respelling; stamped on B413.

## papers-42 — REPORTED 2026-09-25 (branch papers-42 MERGED → proposals main): B414 `contextual-keywords.md` (28 hard / 6 contextual; `as`/`sync` already contextual; Q1–Q6 OWNER — Q6 relayed to syntax-42: B413 must DELETE the `resource` KEYWORDS row); the as-built notes in reactive-pipeline §11 (B411 correction), incremental-collections §13 Q5, index-type §5.4/§9 (17 goldens move — cut-plan §3.1 invalidated), signal-cell-representation §15 (C14 re-scoped; S5 rec DROP — owner); `release-notes-summary.md` (5,215 chars; finalize table with six [[FINALIZE]] lines + [[SPELLING]]); HEADROOM re-measured: 12,559 before the summary, 7,595 after — the train's ≥ 3 breaking entries at ~2,771 chars each EXCEED it → a breaking entry would DROP from the release body. OWNER/INTEGRATOR CALL: raise `CAP` in release.yml 110,000 → 120,000 before the tag (GitHub's body cap is 125,000). FILED: F41 (native `r#self`/`r#super` field emission — live), B416 (`[derive(Wire)]` local vs a field named `deserializer`), B417 (a method named `Self`), D14 (lexical §2.2 omits `as`/`only`), E225 (bindgen RESERVED drift). Four ⟦INTEGRATOR⟧ placeholders in the papers for the sweep.
