#!/usr/bin/env python3
"""Publication hygiene for the proposals repo, plus index completeness.

Ported from the compiler repo's gate (crates/vilan-cli/tests/hygiene.rs)
per proposals-repo.md §6: the three prose-applicable checks — absolute
home paths, personal mailboxes, pre-migration owner strings — as one
script, one workflow. The fourth check (index completeness: every paper
has exactly one row in proposal/README.md) is the gate the compiler repo
never had; it would have caught the duplicated design-language.md row.
The fifth (tracker N24) is the per-item tracker link rule: a `[[name]]`
cite in a tracked `projects/<project>/tracker/` file must resolve to a
live item file or to that tracker's archive.

Needles are assembled at runtime so this file never trips itself.
"""

import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

# Documents *about* the org migration, which necessarily name the old
# owner (carried over from the compiler gate's allowlist, re-rooted to
# this repo's layout). Everything else must stay swept (F9 S4).
OWNER_STRING_ALLOWLIST = {
    "projects/vilan/proposal/org-migration.md":
        "the migration plan itself — the old owner is its subject",
    "archive/backlog-2026-07-18.md":
        "the F9 backlog entry states the problem in terms of the old owner",
    "projects/vilan/proposal/releases.md":
        "release history quotes the install one-liner as it was published",
    "archive/backlog.md":
        "the historical record — ship records moved from the distilled file "
        "(2026-08-03) name the old owner as their subject, same as the F9 entry",
}

# Files that legitimately carry a consumer-mailbox address. Empty on
# purpose: THIRD-PARTY-NOTICES.txt (the compiler gate's one entry) did
# not move here.
PERSONAL_MAILBOX_ALLOWLIST = {}


def tracked_text_files():
    listing = subprocess.run(
        ["git", "ls-files", "-z"], cwd=ROOT, check=True, capture_output=True
    ).stdout
    for name in listing.decode("utf-8").split("\0"):
        if not name:
            continue
        try:
            text = (ROOT / name).read_bytes().decode("utf-8")
        except (FileNotFoundError, UnicodeDecodeError):
            continue  # deleted-but-staged / binary
        yield name, text


def main():
    home_needles = [
        "/" + "home" + "/",
        "/" + "Users" + "/",
        "C:\\" + "Users" + "\\",
    ]
    mailbox_needles = [
        "@" + provider + "."
        for provider in ["gmail", "outlook", "hotmail", "yahoo", "icloud", "proton"]
    ]
    owner_needles = [
        "reed" + "syllas" + "/" + "vilan",
        "reed" + "syllas" + "." + "github" + ".io",
    ]

    offenders = []
    files = list(tracked_text_files())
    for name, text in files:
        for number, line in enumerate(text.splitlines(), 1):
            lowered = line.lower()
            if any(needle in line for needle in home_needles):
                offenders.append(
                    f"{name}:{number}: absolute home path: {line.strip()}"
                )
            if name not in PERSONAL_MAILBOX_ALLOWLIST and any(
                needle in lowered for needle in mailbox_needles
            ):
                offenders.append(
                    f"{name}:{number}: personal mailbox: {line.strip()}"
                )
            if name not in OWNER_STRING_ALLOWLIST and any(
                needle in lowered for needle in owner_needles
            ):
                offenders.append(
                    f"{name}:{number}: pre-migration owner string: {line.strip()}"
                )

    # Index completeness: every proposal/*.md has exactly one row in
    # proposal/README.md (stubs included — their rows say where the file
    # went), and no row is duplicated.
    index = (ROOT / "projects" / "vilan" / "proposal" / "README.md").read_text(encoding="utf-8")
    rows = re.findall(r"^\| `([^`]+)` \|", index, flags=re.M)
    row_counts = {}
    for row in rows:
        row_counts[row] = row_counts.get(row, 0) + 1
    for name, _ in files:
        parts = name.split("/")
        if (
            len(parts) == 4
            and parts[:3] == ["projects", "vilan", "proposal"]
            and parts[3].endswith(".md")
            and parts[3] != "README.md"
        ):
            parts = [None, parts[3]]
            count = row_counts.get(parts[1], 0)
            if count != 1:
                offenders.append(
                    f"proposal/README.md: `{parts[1]}` has {count} index rows "
                    "(want exactly 1)"
                )
    for row, count in row_counts.items():
        if count > 1:
            offenders.append(
                f"proposal/README.md: `{row}` appears in {count} rows "
                "(want exactly 1)"
            )

    # Per-project tracker index completeness (tracker N17): the same
    # one-row-per-file rule as proposal/README.md above, generalized to
    # every TRACKED projects/<project>/tracker/ directory — every
    # items/<ID>.md has exactly one row in that tracker's INDEX.md, and
    # no INDEX.md row points at a file that is not there. A gitignored
    # `.local` project is invisible here by construction, same posture
    # as the dangling-cite check below.
    tracker_item_files = {}  # project -> {id}
    for name, _ in files:
        m = re.fullmatch(r"projects/([^/]+)/tracker/items/([^/]+)\.md", name)
        if m:
            tracker_item_files.setdefault(m.group(1), set()).add(m.group(2))
    index_row_re = re.compile(r"^\|\s*\[([^\]]+)\]\(items/([^)]+)\.md\)")
    for project, item_ids in tracker_item_files.items():
        index_path = f"projects/{project}/tracker/INDEX.md"
        index_text = next((body for name, body in files if name == index_path), None)
        if index_text is None:
            offenders.append(f"{index_path}: missing (project has tracker items)")
            continue
        row_counts_by_id = {}
        for line in index_text.splitlines():
            m = index_row_re.match(line)
            if m and m.group(1) == m.group(2):
                row_counts_by_id[m.group(1)] = row_counts_by_id.get(m.group(1), 0) + 1
        for item_id in item_ids:
            count = row_counts_by_id.get(item_id, 0)
            if count != 1:
                offenders.append(
                    f"{index_path}: `{item_id}` has {count} INDEX rows "
                    "(want exactly 1)"
                )
        for row_id, count in row_counts_by_id.items():
            if row_id not in item_ids:
                offenders.append(
                    f"{index_path}: `{row_id}` row has no items/{row_id}.md"
                )

    # Dangling per-item tracker cites (tracker N24): closing an item
    # DELETES its `items/<ID>.md` and leaves a tombstone in archive.md,
    # so a `[[cite]]` of a closed item dangles unless the archive still
    # names it. Rule: every `[[name]]` in a tracked file under
    # `projects/<project>/tracker/` resolves to the live
    # `projects/<project>/tracker/items/<name>.md`, or to a mention in
    # that tracker's `archive.md`. Scope is deliberate — the `[[...]]`
    # cite convention belongs to the per-item format (projects/README.md),
    # and the wider repo uses the same brackets for TOML array-of-tables
    # headers and nested array types, which are not cites.
    # STRUCTURAL LIMIT, recorded here and on N24: this gate scans TRACKED
    # files only, so a gitignored `.local` tracker (projects/*.local/) is
    # invisible to it by construction — there, dangling-cite hygiene is
    # convention, recorded on N24, not enforcement. Since N17's migration,
    # `projects/vilan/tracker/` is tracked and this rule covers it like
    # any other project; the limit now names `.local` projects only.
    tracked_names = {name for name, _ in files}
    cite_pattern = re.compile(r"\[\[([^\[\]\n]+)\]\]")
    archive_texts = {
        name.split("/")[1]: body
        for name, body in files
        if re.fullmatch(r"projects/[^/]+/tracker/archive\.md", name)
    }
    for name, text in files:
        parts = name.split("/")
        if len(parts) < 4 or parts[0] != "projects" or parts[2] != "tracker":
            continue
        project = parts[1]
        archive_text = archive_texts.get(project, "")
        for number, line in enumerate(text.splitlines(), 1):
            # A [[name]] inside a backtick code span is spelling (TOML's
            # [[table]] arrays, e.g. `[[build.hook]]`), not an item cite —
            # the gate's first live run caught exactly this (G9.md).
            line = re.sub(r"`[^`]*`", "", line)
            for cite in cite_pattern.findall(line):
                if f"projects/{project}/tracker/items/{cite}.md" in tracked_names:
                    continue
                if re.search(
                    r"(?<![0-9A-Za-z_-])" + re.escape(cite) + r"(?![0-9A-Za-z_-])",
                    archive_text,
                ):
                    continue
                offenders.append(
                    f"{name}:{number}: dangling item cite [[{cite}]]: no "
                    f"items/{cite}.md, and the tracker's archive.md never "
                    "names it"
                )

    if offenders:
        print("hygiene offenders:")
        print("\n".join(offenders))
        return 1
    print(f"hygiene clean: {len(files)} tracked text files scanned")
    return 0


if __name__ == "__main__":
    sys.exit(main())
