# The tracker migrates to the per-item format (N17)

Status: PROPOSED 2026-08-28 (backlog N17). N17 itself was RULED 2026-08-28:
"Yes, the per-item tracker format (including the move into `projects/`)
should happen." This paper answers the sub-questions the ruling left open
and is the migration runbook. Nothing here is executed — it prepares the
same way `proposals-repo.md` §9 prepared the N15 cutover; the migration
runs SERIAL between cycles, never during an order, because it rewrites the
surface every lane's records touch (N17's own STATUS line).

## 0. What this is answering

`projects/README.md` already specifies the per-item format and
`projects/kolt.local/tracker/` is its live pilot (26 items, one project,
flat zero-padded IDs). This paper is the recommendation set for taking
that format repo-wide, onto `tracker/backlog.md` — today's single planning
surface, 12 open section letters (A–N, F and H currently empty but
retired), **39 open items**, 77 KB — plus its append-only sibling
`tracker/backlog-archive.md` (124 tombstones, 128 KB).

## 1. Wholesale vs per-section

**Recommend wholesale — one cutover, one commit stack.**

The per-section option (migrate A, ship it, migrate B next cycle, …)
sounds lower-risk but buys nothing here and costs real complexity:

- **The item count is tiny.** 39 open items across 12 letters is not the
  950-commit, 105-file scale N15 extracted; a mechanical script (§9)
  produces the whole tree in one pass, and a human can review the whole
  diff in one sitting.
- **A straddle window defeats the format's own motive.** The point of
  per-item files is that agents stop contending over one long surface.
  Migrating section-by-section means, for however many cycles the
  straddle lasts, some sections still share one `backlog.md` (still
  contended) while others use per-item files — and the hygiene gate,
  citation resolution, and every lane brief have to carry two regimes
  at once for no reader's benefit.
- **N15's own precedent agrees.** §7.3 there deliberately reordered steps
  so "the move itself is one trivially-auditable diff." A 39-item split
  is smaller than that move by two orders of magnitude; there is no
  scale argument for staging it.

Per-section would only earn its keep if sections had independent owners
or the count were in the hundreds. Neither holds.

## 2. ID stability

**Recommend: one project (`projects/vilan/tracker/`), filenames are the
existing letter+number IDs verbatim, unpadded — `items/B147.md`,
`items/N17.md`, `items/A26.md`.**

**One project, not one per section.** Sections (A–N) are thematic
groupings inside one backlog, not independent bodies of work — items
cross-reference across letters constantly (N17 itself cites D15, E92;
process.md §5.4(c) reasons about "the backlog's B section" as one part of
one whole). Splitting into twelve `projects/<letter>/` trees would
fragment that mesh, multiply INDEX/archive files for no contention
benefit (the benefit — one file per item — is already captured without
also splitting the project boundary), and there is no reading of "project"
in `projects/README.md` that means "backlog section." `INDEX.md` keeps
the section structure as its internal grouping instead (§3 below), which
is exactly what a reader asking "what's open in section B" needs.

**Filenames carry the ID verbatim, not `kolt.local`'s zero-padded scheme.**
`projects/README.md` today says IDs are "zero-padded, sequential,
per-project" — that is correct for the pilot's flat single-namespace ID
space and wrong for vilan's, which is letter+number, per-section, and has
never been zero-padded. Recommend amending `projects/README.md` with one
clause in the same stack as the vilan migration: an ID inherited from a
pre-migration numbering scheme keeps its original shape (letter+number,
unpadded) rather than being renumbered to the pilot's convention. The
spec should describe both real shapes it now governs, not just the first
one.

**Why verbatim over a redirect table — the deciding measurement.** A
scan of `proposal/*.md` for the `[A-N]\d{1,3}` shape returns on the order
of **2,800 hits across 99 files** (noisy — it also catches step labels
like sizes and section numbers — but even generously discounted this is
thousands of real ID citations, the dominant form being bare prose like
"backlog B141" or "→ B147 filed"). Renumbering, or minting a redirect
layer a reader must resolve, means either a rewrite sweep across the
whole paper corpus or a permanent indirection every future reader pays.
Carrying the ID verbatim as the filename costs nothing at every one of
those 2,800 sites: the string "B141" is still the string a citation names,
and it is still a real path.

**What "backlog B141" resolves to after the move**: `git grep` for the ID
now has exactly two possible hits, matching today's two-state resolution
(open in `backlog.md` vs. tombstoned in `backlog-archive.md`) one-for-one:

- **Open** → `projects/vilan/tracker/items/B141.md`.
- **Closed** → a tombstone naming it in `projects/vilan/tracker/archive.md`
  (post-cutover closures) or in the frozen chain (`archive/backlog.md` →
  `archive/backlog-2026-07-18.md` → `archive/backlog-<cutover-date>.md` →
  `archive/backlog-archive.md`, for anything closed before the cutover —
  see §6). No ID is ever live in one place and dead in another; the
  verification pass (§7) is exactly checking that invariant.

No rewrite of the citation corpus is required or recommended. A one-line
pointer at the top of `projects/vilan/tracker/INDEX.md` states the
resolution rule above for a reader who has not seen this paper.

## 3. The Now/Next/Later block and the order chronicle

**Not an item — recommend a new file, `tracker/chronicle.md`, holding
exactly the narrative that is not item data.**

`tracker/backlog.md`'s first ~540 lines (before `## A.`) are the running
release/cycle narrative: the "single planning surface" framing, the
numbering rules, the "owner questions parked in papers and on items"
recall paragraph, and the **Now / Next / Later** block itself — the
history of every order, train, and ruling batch back to the 2026-08-18
re-baseline. None of it is a tracked, closeable unit; all of it is
exactly what N15 already ruled should stay structurally separate from the
papers "so it can move elsewhere later without touching the papers"
(`proposals-repo.md` §8). That ruling's logic extends one level further
here: the narrative should also stay separate from the *per-item* data,
so each can evolve on its own cadence — items close constantly, the
narrative is appended to once per cycle close.

`tracker/chronicle.md` carries the header block and the Now/Next/Later
section forward verbatim (a cut-paste, not a rewrite), plus a pointer to
`projects/vilan/tracker/INDEX.md` where the numbering-and-closing rules
used to live inline (those rules are now `projects/README.md`'s job,
already written). Every future cycle close updates `chronicle.md` the
same way it updates `backlog.md`'s header today.

## 4. The index-completeness gate

**Two independent things, both named "index completeness" today —
keep the papers check as is; generalize the tracker check.**

`check_hygiene.py`'s current index-completeness block checks one thing:
every `proposal/*.md` has exactly one row in `proposal/README.md`. That
check is about papers, is untouched by this migration (no paper moves),
and needs no change.

What the migration adds is a **second, analogous** check that does not
exist yet at all: every `projects/<project>/tracker/items/<ID>.md` has
exactly one row in that project's `INDEX.md`, and no `INDEX.md` row
points at a file that is not there. `kolt.local`'s `INDEX.md` is
gitignored today, so nothing has ever gated it; `projects/vilan/tracker/`
will be the first *tracked* per-item tracker, so this is the first time
the gap is reachable. Recommend generalizing rather than special-casing
vilan: loop over every tracked `projects/<project>/tracker/` directory
found (the discovery pattern the dangling-cite check already uses, next
paragraph) and apply the same one-row-per-file / no-orphan-row rule the
papers check applies to `proposal/README.md`. A draft patch is in
`scripts/n17-hygiene-index-completeness.patch` (§9).

**The dangling-`[[link]]` rule (N24) needs no widening — it already
generalizes.** Read the comment at `check_hygiene.py:135-139`: it scans
`projects/[^/]+/tracker/` generically and states outright — *"When N17's
migration lands tracked per-item trackers, this rule covers them from day
one."* That is correct as written; `projects/vilan/tracker/` starts
covered the moment its files are tracked, with zero code change. The only
edit owed there is the STRUCTURAL LIMIT paragraph's framing: today it
reads as describing a hypothetical; after the cutover it should read as
describing `.local` projects specifically (the case that still applies),
not as forward-looking about vilan's own tracker anymore. One sentence,
cosmetic, not a gate change.

## 5. Ratified surface names

**Bare ID citations ("backlog B141") carry untouched (§2). Literal
filename citations get N15's banner-stub device. Structural-phrase
citations get one dated note each — found by grep, not by sweep.**

- `process.md` §5.4(c) — *"No known miscompile is open in the backlog's
  B section"* — is the sharpest case: a ratified trigger condition
  reasoning about a literal section. It still resolves correctly after
  the move (every B-item is still an ID starting with `B`, grouped under
  `## B.` in `INDEX.md`), but the phrase "the backlog's B section" no
  longer names one file. Recommend one dated note at that clause in the
  same stack as the cutover, in the style already used at
  `proposals-repo.md` §4's "*Post-cutover note (2026-08-28): …*" —
  pointing at `projects/vilan/tracker/INDEX.md`'s `## B.` group.
- Literal `backlog.md` / `backlog-archive.md` path citations (a small,
  greppable set — `AGENTS.md`, `CLAUDE.md`, `projects/README.md`'s own
  "the wider restructure (tracker N17)" line, and any paper that links
  the file rather than an ID) get the exact device
  `proposal/backlog.md` already demonstrates: a one-paragraph stub at the
  old path naming where the content lives now and the `git log --follow`
  escape hatch. No new device to invent.
- **Do not sweep the paper corpus.** N15 §5's own rule for the weaker
  comment-citations applies here even more strongly, because the corpus
  is larger: *"update opportunistically, never as a sweep."* The 2,800-ish
  bare-ID citations need nothing; only the handful of structural-phrase
  and literal-filename citations do, and grep finds all of them in one
  pass (§7's verification includes that grep).

## 6. The archive

**`tracker/backlog-archive.md` freezes and chains, N15-style — it does
not get rewritten per-item.**

The 124 existing tombstones are historical prose, not live data; nothing
about them benefits from being split into 124 files, and doing so would
be pure churn against the exact N15 precedent this project already has
for "old, unambiguously-archive material": freeze the file, chain it
after its predecessors, leave a banner where it was. `backlog.md` already
lives at the end of exactly that chain today
(`archive/backlog.md` → `archive/backlog-2026-07-18.md` →
`tracker/backlog.md`), and `backlog-archive.md` is its append-only
sibling. The cutover extends the same chain one more link:

```
archive/backlog.md                      (alpha era, frozen 2026-07-18)
  → archive/backlog-2026-07-18.md       (cycles 15–19, frozen 2026-08-18)
  → archive/backlog-<cutover-date>.md   (re-baseline era, frozen at cutover — NEW)
archive/backlog-archive.md              (the 124 tombstones, frozen at cutover — NEW,
                                          undated: terminal, not itself re-baselined)
  → projects/vilan/tracker/archive.md   (live going forward, starts with a header
                                          chaining back to the frozen files above,
                                          exactly as tracker/backlog-archive.md's own
                                          header chains back today)
```

`tracker/backlog.md` and `tracker/backlog-archive.md` both become banner
stubs at their old paths, same device as `proposal/backlog.md` (§5). Any
ID closed before the cutover resolves in the frozen chain forever; any ID
closed after resolves in the new `archive.md`. §7's ID census checks both
halves of that split are honest — no ID double-counted, none dropped.

## 7. Verification checklist (the executor runs this)

1. **Item count.** Count numbered top-level items in the frozen
   `tracker/backlog.md` per section (the census script counts
   `^\d+\.\s+\*\*` boundaries per `## [A-Z]\.` heading — this is exactly
   how §1's 39 was computed) and confirm it equals the number of
   `projects/vilan/tracker/items/*.md` files created.
2. **ID census, both directions.**
   - Every ID present as an open item in the frozen `backlog.md` has
     exactly one `items/<ID>.md`.
   - No ID appears in *both* `items/` and any archive surface (frozen
     chain or new `archive.md`) — an item is open xor closed, never both.
   - Every ID tombstoned in `backlog-archive.md` before the cutover
     still resolves via the frozen chain (spot-check by grep, not full
     replay — the file is frozen unmodified, so this is really "the
     banner stub exists and the frozen file's content is byte-identical
     to pre-move").
3. **Link resolution.** Sample citations of the heaviest-cited IDs
   (`B141`, `N15`, `N17`, `D15`, `B147`, …) across `proposal/*.md` and
   confirm each still resolves per §2's two-state rule. Grep for the
   structural phrases named in §5 (`"backlog's [A-N] section"`, literal
   `backlog.md`/`backlog-archive.md` path mentions) and confirm each has
   its dated note or banner stub.
4. **Hygiene green.** `python3 scripts/check_hygiene.py` exits 0 —
   including the new per-project index-completeness check (§4) and the
   pre-existing N24 dangling-`[[link]]` check now actually exercised
   against tracked data for the first time.
5. **Body losslessness.** Every `items/<ID>.md` body (everything after
   the field-block header) is a byte-for-byte match, modulo leading
   whitespace, of that item's original numbered-list body in the frozen
   `backlog.md`. Field-block metadata (kind/area/source) is allowed to be
   best-effort and touched up later; body text is not.
6. **Narrative preservation.** `tracker/chronicle.md`'s content is a
   byte-for-byte match of `tracker/backlog.md`'s pre-`## A.` header block,
   minus the numbering-rules paragraph that moved to `projects/README.md`.

`scripts/n17_verify_migration.py` (§9) automates 1, 2, and 4; 3, 5, and 6
are reviewed by a human against the script's diff output.

## 8. Cutover sequence, with rollback

Runs entirely inside one lane, between cycles, on a branch off `main` —
no different in kind from any other lane's worktree, except that no other
lane may be in flight against `tracker/` while it runs (N17's own
sequencing note).

1. **Freeze window chosen.** Between orders; confirmed no open lane
   touches `tracker/backlog.md` or `tracker/backlog-archive.md`.
2. **Dry-run the split.** Run `scripts/n17_split_tracker.py` (§9) against
   the current `tracker/backlog.md` into a staging directory (not the
   live tree). Review the generated `items/*.md`, `INDEX.md`, and
   `chronicle.md` content by hand against §7.5–6.
3. **Freeze and stub the old files, in one commit.** `git mv
   tracker/backlog.md archive/backlog-<date>.md`; `git mv
   tracker/backlog-archive.md archive/backlog-archive.md`; write the two
   banner stubs at the vacated `tracker/` paths (§5/§6's device). This
   commit is pure `git mv` + two small new files — content-preserving,
   trivially auditable, same shape as N15 §7 step 4.
4. **Materialize the new tree, in the next commit.** Copy the reviewed
   staging output into `projects/vilan/tracker/{items/,INDEX.md,
   archive.md}` and `tracker/chronicle.md`. `archive.md` opens with the
   chain-pointer header (§6).
5. **Land the fix list, in the same or next commit.** The
   index-completeness patch (§4, `scripts/n17-hygiene-index-
   completeness.patch`); `AGENTS.md` / `CLAUDE.md` / `projects/README.md`
   pointer updates; the `process.md` §5.4(c) dated note (§5); the
   `projects/README.md` ID-shape amendment (§2).
6. **Run the verification checklist (§7).** All six checks pass before
   this stack merges.
7. **Push.** Suite is prose-only (`proposals-repo.md` §6) — the hygiene
   workflow is the whole gate; confirm it green on the pushed branch,
   same as any other lane.
8. **First post-cutover cycle checklist.** Lane briefs that touch vilan
   tracker items cite `projects/vilan/tracker/items/<ID>.md`; the closing
   discipline is `projects/README.md`'s (delete the file, drop the INDEX
   row, land one tombstone in `archive.md`) instead of the old
   sweep-into-`backlog-archive.md` habit; `tracker/chronicle.md` gets the
   cycle-close narrative update instead of `backlog.md`'s header.

**Rollback.** Before push: discard the branch, nothing external touched
(identical posture to N15 §9's local-only prepare). After push but before
any lane has opened or closed a vilan item under the new layout: `git
revert` the two structural commits — they are pure moves and additions
with no other repo state depending on the new paths yet, so the revert is
clean, unlike N15's cross-repo rollback problem (there is only one repo
here). After a lane has already closed an item under the new layout: do
not revert — that item's tombstone now exists only in the new
`archive.md`, and reverting would drop it. The freeze-window discipline
in step 1 exists specifically so this case cannot occur mid-migration.

## 9. Prepared scripts (written, NOT run)

Three scripts, all under `scripts/`, all deliberately not executed by
this paper — mirroring `proposals-repo.md` §9's own posture ("nothing
here is executed... the extracted repo, the runbook, and the compiler-side
freeze patch sit in the lane's scratch space"):

- **`scripts/n17_split_tracker.py`** — parses a frozen `backlog.md`-shaped
  file into per-item files, an `INDEX.md`, and a `chronicle.md`, writing
  to a staging directory (never the live tree). Implements §8 step 2.
- **`scripts/n17_verify_migration.py`** — recomputes the census over the
  frozen original and the staged/materialized output, checks the §7.1–2
  invariants, and shells out to `check_hygiene.py`. Implements §8 step 6
  (automatable half).
- **`scripts/n17-hygiene-index-completeness.patch`** — a unified diff
  against today's `scripts/check_hygiene.py` adding the §4 per-project
  index-completeness loop. Illustrative: `check_hygiene.py` may have
  changed by execution time (this migration is explicitly deferred to a
  future between-cycles window), so re-derive the patch against its
  state then rather than applying this one blind.

All three are inert until an executor runs them by hand at cutover time.
