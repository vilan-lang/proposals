#!/usr/bin/env python3
"""PREPARE SCRIPT for the N17 tracker migration — NOT RUN.

Part of the migration runbook at `proposal/tracker-migration.md` §9,
automating the checklist at §7 items 1, 2, and 4 (item count, ID census,
hygiene). Items 3, 5, and 6 (link-resolution sampling, body
losslessness, narrative preservation) are reviewed by hand — this script
does not attempt them.

Compares the ID set implied by a frozen pre-migration backlog file
against the ID set actually materialized as `projects/<project>/tracker/
items/*.md` plus whatever an archive surface (old or new) already
accounts for, and reports any mismatch. Then shells out to
`check_hygiene.py`.

Usage (once the migration is materialized and ready to verify):
    python3 scripts/n17_verify_migration.py \\
        --frozen-backlog archive/backlog-<date>.md \\
        --project vilan \\
        --archive-old archive/backlog-archive.md \\
        --root .
"""

import argparse
import pathlib
import re
import subprocess
import sys

SECTION_RE = re.compile(r"^## ([A-Z])\.")
ITEM_RE = re.compile(r"^(\d+)\.\s+\*\*")


def census_open_ids(backlog_text: str):
    """Every ID that was an open top-level item in the frozen file."""
    ids = set()
    letter = None
    for line in backlog_text.split("\n"):
        m = SECTION_RE.match(line)
        if m:
            letter = m.group(1)
            continue
        m = ITEM_RE.match(line)
        if m and letter:
            ids.add(f"{letter}{m.group(1)}")
    return ids


def materialized_ids(items_dir: pathlib.Path):
    if not items_dir.is_dir():
        return set()
    return {p.stem for p in items_dir.glob("*.md")}


def mentioned_ids(archive_text: str, candidate_ids):
    """Which of candidate_ids are named (word-bounded) in archive_text."""
    found = set()
    for cid in candidate_ids:
        if re.search(
            r"(?<![0-9A-Za-z_-])" + re.escape(cid) + r"(?![0-9A-Za-z_-])",
            archive_text,
        ):
            found.add(cid)
    return found


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frozen-backlog", type=pathlib.Path, required=True)
    ap.add_argument("--project", default="vilan")
    ap.add_argument("--archive-old", type=pathlib.Path, action="append", default=[])
    ap.add_argument("--root", type=pathlib.Path, default=pathlib.Path("."))
    args = ap.parse_args()

    offenders = []

    backlog_text = args.frozen_backlog.read_text(encoding="utf-8")
    open_ids = census_open_ids(backlog_text)

    items_dir = args.root / "projects" / args.project / "tracker" / "items"
    live_ids = materialized_ids(items_dir)

    new_archive = args.root / "projects" / args.project / "tracker" / "archive.md"
    new_archive_text = new_archive.read_text(encoding="utf-8") if new_archive.exists() else ""

    old_archive_text = ""
    for path in args.archive_old:
        old_archive_text += path.read_text(encoding="utf-8") + "\n"

    # 1. Every open ID from the frozen backlog has exactly one items/<ID>.md.
    missing = sorted(open_ids - live_ids)
    if missing:
        offenders.append(f"missing item files for open IDs: {missing}")

    # 2. No ID is double-counted: nothing in items/ also HEADS a tombstone
    #    anywhere (old or new archive). A mere mention inside another
    #    item's tombstone prose is expected and fine — D5, N16, K5 are
    #    named constantly — so only a tombstone HEAD counts as archived:
    #    the archive bullet form `- **<ID>.` / `- **<ID> `/`- **<ID> +`.
    def heads_tombstone(text, cid):
        return re.search(
            r"^- \*\*" + re.escape(cid) + r"[ .+]", text, re.M
        ) is not None
    for lid in sorted(live_ids):
        if heads_tombstone(new_archive_text, lid) or heads_tombstone(
            old_archive_text, lid
        ):
            offenders.append(f"{lid}: live in items/ AND heads a tombstone")

    # 3. Extras: a materialized item file whose ID was never open in the
    #    frozen backlog (typo, stale leftover, or a real find — flagged
    #    for human review either way).
    extras = sorted(live_ids - open_ids)
    if extras:
        offenders.append(f"item files with no matching frozen-backlog ID: {extras}")

    print(f"open IDs in frozen backlog: {len(open_ids)}")
    print(f"materialized item files: {len(live_ids)}")

    if offenders:
        print("\nID CENSUS OFFENDERS:")
        for o in offenders:
            print(f"  - {o}")
    else:
        print("ID census: clean")

    print("\nrunning check_hygiene.py ...")
    result = subprocess.run(
        [sys.executable, str(args.root / "scripts" / "check_hygiene.py")],
        cwd=args.root,
    )

    if offenders or result.returncode != 0:
        print("\nVERIFICATION FAILED", file=sys.stderr)
        return 1
    print("\nVERIFICATION PASSED (census + hygiene)")
    print("Remember: §7 items 3/5/6 (link sampling, body losslessness, "
          "narrative preservation) still need a human pass.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
