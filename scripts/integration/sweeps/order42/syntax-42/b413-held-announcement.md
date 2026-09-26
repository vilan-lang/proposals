# B413 — the v0.41.0 announcement, ONLY if R-c holds B413 for v0.42.0

If syntax-42's B413 commit merges in this train, IGNORE this file: that
commit's own `family: breaking` entry is the removal, in the same release
that removes it (alpha: no window owed, and a `removes:` in v0.41.0 would be
refused by `cut-release.sh`, since no released section carries its
`deprecates:`).

If B413 is HELD, insert the entry below under `## Unreleased` in next's
CHANGELOG at the train's seal (before the cut), and at the v0.42.0 merge add
`<!-- removes: resource keyword -->` above B413's own entry head (the KEY is
a proposal — any spelling works if both markers use the same one).

```markdown
<!-- family: breaking -->
<!-- deprecates: resource keyword -->
**The `resource` keyword is going: v0.42.0 declares a resource type with the `[resource]` attribute — `[resource] struct Session { … }`, `[resource] external struct Database;`, `[resource] enum Holder { … }` — and REFUSES `resource struct`.** B413 (ruled R-c, 2026-09-25): the keyword dissolves into an attribute on the struct or enum; the word `resource` stays (it becomes an ordinary name everywhere else, which frees `Resource<T>`'s constructor). Nothing changes in this release. Migration, mechanical: every `resource struct` / `resource external struct` / `resource enum` becomes `[resource] struct` / `[resource] external struct` / `[resource] enum` (the codemod is `sweeps/order42/syntax-42/b413_codemod.py` in the proposals repository).
```
