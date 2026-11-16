# Kolt under v0.56.0: the patch and what it leaves

Prepared 2026-11-16 on a scratch copy of the owner's `vilan-migration` branch at `acaa026`
(`~/.vilan/gates/kolt-056/kolt`), then applied to the checkout at the owner's word ("Patch Kolt").
The two patches drafted earlier in the order (`repros/kolt-db58.patch`, `repros/kolt-m1.patch`) were
written against the tree before its `src/server`, `src/client`, `lib/` reorganisation and no longer
apply; this replaces the first. The second was the native-server trial and is not part of running
Kolt on 0.56.0.

## Required (the breaking change: `std::db` parameters are `List<dyn SqlValue>`, M175)

Under 0.56.0 the unpatched tree has three errors, all "a `List<str>` does not become a
`List<dyn SqlValue>` as a whole":

- `src/server/mcp.vl`: `word_filter` takes and answers `List<dyn SqlValue>` (its two `.all(parameters)`
  callers at the search were the errors); `import std::db::{ Row, SqlValue };`.
- `src/server/store.vl`: `body_problem` builds `mut parameters: List<dyn SqlValue> = [org];` and pushes
  each upload id (`push_many` of a `List<str>` does not convert as a whole);
  `import std::db::{ Database, Migration, Row, SqlValue };`.

The four `Role` binds already say `.value()` (the owner's own fix), so nothing else moves. This patch
does NOT compile under 0.55.1 (`SqlValue` is new), so it goes in with the toolchain.

- `Dockerfile`: `ARG VILAN_VERSION=0.56.0`.

## Applied to the owner's checkout (2026-11-16, local commits on `vilan-migration`, NOT pushed)

- `5358089` chore(vilan): build with 0.56.0 - std::db parameters are List<dyn SqlValue> (the three
  files above).
- `755da23` docs: Vilan tracker items by their numbers on the tracker's main branch. Kolt-side
  sessions filed these items on local branches of the proposals repository, where their numbers were
  already other items on main; they are on main now as `B741 -> B746` (a backed enum through `&mut`;
  12 comments and `docs/WISDOM.md`), `B740 -> B745` (`docs/WISDOM.md`), `E362 -> E367`
  (`lib/search-dict`), `E363 -> E368` (`scripts/src/test.vl`), `B739 -> B747` (`src/server/mcp.vl`).
  `CLAUDE.md` (untracked) still shows `vilan-lang E362` as its example of the convention; left alone.

NOT touched: `src/client/sidebar/sidebar.vl`. The owner's working tree already carries an uncommitted
edit there that removes the empty import of line 31 (the line that panicked the 0.55.1 language
server, E362, fixed in 0.56.0) and the file's import of itself; it is his to commit.

## Verified

In the owner's checkout after the two commits, under the installed 0.56.0: `vilan check .` exit 0 with no errors or warnings. On the scratch copy with the same patch, under the v0.56.0 binary: `vilan check .` exit 0, no errors, no
warnings; `vilan fmt --check .` reports only the 21 files under `planning/` that 0.55.1 reports too
(and the one there that does not parse); `vilan run scripts/src/test.vl` passes every folder (the
copy needed `dist/spell/en_US.words` supplied, a generated file).

## Optional adoptions, NOT applied (the owner's code decisions)

- `src/server/mcp_write.vl:40,45` and `src/server/files.vl:186`: `std::base64::encode` ships (F158);
  the local helpers can go.
- `src/server/account_guard.vl:105`: `Request::peer_address` ships (F163); the `external fun` can go.
- `src/server/mcp.vl` `channel_hits`: its parameters are `List<any>` pushed one by one. The reason
  given (B747, a mixed literal at an annotated `List<any>`) still holds in 0.56.0, but the list can now
  be `List<dyn SqlValue>`, which a mixed literal satisfies.
- The mirrored enums written as plain enums (B746): the fix is ready on branch `b746-58` and is
  proposed as v0.56.1. After it, they can be backed again; reading a backed enum through a view then
  needs `*` (the patched copy already checks clean under the fix).
