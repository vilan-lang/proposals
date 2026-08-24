#!/usr/bin/env python3
"""Publication hygiene for the proposals repo, plus index completeness.

Ported from the compiler repo's gate (crates/vilan-cli/tests/hygiene.rs)
per proposals-repo.md §6: the three prose-applicable checks — absolute
home paths, personal mailboxes, pre-migration owner strings — as one
script, one workflow. The fourth check (index completeness: every paper
has exactly one row in proposal/README.md) is the gate the compiler repo
never had; it would have caught the duplicated design-language.md row.

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
    "proposal/org-migration.md":
        "the migration plan itself — the old owner is its subject",
    "archive/backlog-2026-07-18.md":
        "the F9 backlog entry states the problem in terms of the old owner",
    "proposal/releases.md":
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
    index = (ROOT / "proposal" / "README.md").read_text(encoding="utf-8")
    rows = re.findall(r"^\| `([^`]+)` \|", index, flags=re.M)
    row_counts = {}
    for row in rows:
        row_counts[row] = row_counts.get(row, 0) + 1
    for name, _ in files:
        parts = name.split("/")
        if (
            len(parts) == 2
            and parts[0] == "proposal"
            and parts[1].endswith(".md")
            and parts[1] != "README.md"
        ):
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

    if offenders:
        print("hygiene offenders:")
        print("\n".join(offenders))
        return 1
    print(f"hygiene clean: {len(files)} tracked text files scanned")
    return 0


if __name__ == "__main__":
    sys.exit(main())
