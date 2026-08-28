# vilan-lang/proposals

The vilan project's design memory — every proposal, tracker, and archived
planning surface — extracted from `vilan-lang/vilan` at freeze sha
`18f24cdff65c27b84766a06feba13c9130a88328` with full history (`git filter-repo`; the plan is
`proposal/proposals-repo.md`, ruled 2026-08-22).

Layout, as ruled:

- `proposal/` — the papers, a 1:1 image of the compiler repo's old
  `vilan/proposal/`, so `proposal/X.md §n` citations resolve here
  verbatim and stay greppable. Files that moved below leave one-line
  stubs at their old paths so relative `record:` citations still land.
  `proposal/README.md` is the per-file index (gated: exactly one row
  per paper).
- `projects/vilan/tracker/` — THE open-work tracker, per-item since the
  N17 migration (2026-08-28): one file per open item in `items/`,
  `INDEX.md` the open list, `archive.md` the tombstones. The cycle
  narrative lives at `tracker/chronicle.md`; the pre-migration eras are
  frozen under `archive/` with banner stubs at the old `tracker/` paths,
  so a "backlog B141" citation always resolves (see
  `proposal/tracker-migration.md` §2).
- `archive/` — the dead generations: the frozen tracker eras
  (`backlog.md`, `backlog-2026-07-18.md`), the superseded `roadmap.md`,
  and the superseded memory-management chain (`memory-management.md`,
  `memory-management-rev-1.md`).

Conventions: one branch (`main`), no `next`, no tags, no release train —
prose has no release. Sessions work in `.claude/worktrees/<lane>`
branched from `main`, never this checkout; integration merges `--no-ff`
per cycle. CI is `scripts/check_hygiene.py` (publication hygiene ported
from the compiler repo's gate, plus index completeness).

History notes: commit shas cited *inside* the records are compiler-repo
shas and resolve in `vilan-lang/vilan`. Pre-move history also stays
queryable there forever (`git log -S <needle> -- vilan/proposal/` works
against deleted paths); here, `git log --follow proposal/<paper>.md`
spans the whole timeline.
