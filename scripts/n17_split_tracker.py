#!/usr/bin/env python3
"""PREPARE SCRIPT for the N17 tracker migration — NOT RUN.

Part of the migration runbook at `proposal/tracker-migration.md` §9. Do
not execute against the live tree; this writes to a staging directory so
its output can be reviewed (§8 step 2 of the runbook) before anything is
materialized into `projects/vilan/tracker/` or `tracker/chronicle.md`.

Splits a `backlog.md`-shaped file (one `## <LETTER>. <title>` heading per
section, numbered top-level items `N. **title** (...)` inside each) into:

  <out>/items/<LETTER><N>.md   one file per open item, field-block + body
  <out>/INDEX.md               one table per section, grouped as today's
                                `## <LETTER>.` headings are
  <out>/chronicle.md           everything before the first section
                                heading (the Now/Next/Later narrative),
                                verbatim minus the numbering-rules
                                paragraph (that content now lives in
                                projects/README.md)

Field-block enrichment (kind/area/source/status) is best-effort — see
tracker-migration.md §7.5: body text is the losslessness bar, metadata is
not. The `status:` line in particular is a naive single-line grab of the
first `STATUS: ...` line in the body and WILL truncate a wrapped
sentence (verified on N17 itself, whose real STATUS line runs to four
lines) — the body carries the full text either way, so nothing is lost,
but a reviewer should rewrite each `status:` line to a short summary by
hand rather than trust the auto-extracted one verbatim. The body is
copied from the first line after the item's title line through the line
before the next top-level item or the next section heading, dedented not
at all (backlog.md items are already at column 0).

Usage (once reviewed and intended to actually run):
    python3 scripts/n17_split_tracker.py tracker/backlog.md --out staging/
"""

import argparse
import pathlib
import re
import sys

SECTION_RE = re.compile(r"^## ([A-Z])\.\s*(.*)$")
ITEM_RE = re.compile(r"^(\d+)\.\s+\*\*(.*)$")
STATUS_RE = re.compile(r"^\s*STATUS:\s*(.*)$")


def parse_sections(text: str):
    lines = text.split("\n")
    header_end = None
    sections = []
    cur = None
    for i, line in enumerate(lines):
        m = SECTION_RE.match(line)
        if m:
            if header_end is None:
                header_end = i
            if cur is not None:
                cur["end"] = i
            cur = {
                "letter": m.group(1),
                "title": m.group(2).strip(),
                "start": i,
                "end": len(lines),
            }
            sections.append(cur)
    if cur is not None:
        cur["end"] = len(lines)
    if header_end is None:
        header_end = len(lines)
    header = "\n".join(lines[:header_end])
    return header, sections, lines


def parse_items(section, lines):
    body_lines = lines[section["start"] + 1 : section["end"]]
    items = []
    cur = None
    for line in body_lines:
        m = ITEM_RE.match(line)
        if m:
            if cur is not None:
                items.append(cur)
            cur = {
                "id": f"{section['letter']}{m.group(1)}",
                "title_line": m.group(2),
                "body": [],
            }
        elif cur is not None:
            cur["body"].append(line)
    if cur is not None:
        items.append(cur)
    return items


def extract_status(body_lines):
    for line in body_lines:
        m = STATUS_RE.match(line)
        if m:
            return m.group(1).strip()
    return "open"


def render_item_file(item_id, section, item):
    title = item["title_line"]
    # title_line still carries the closing "**" and any trailing
    # parenthetical (size/flag/source) — split it off best-effort so the
    # h1 is clean; leave the parenthetical in the body's first line if
    # the split is ambiguous rather than lose it.
    close = title.find("**")
    if close != -1:
        h1 = title[:close].strip()
        rest = title[close + 2 :].strip()
    else:
        h1 = title.strip()
        rest = ""
    status = extract_status(item["body"])
    body = "\n".join(item["body"]).strip("\n")
    lines = [
        f"# {item_id} — {h1}",
        "",
        f"- status: {status}",
        "- kind: TBD  # best-effort — reviewer fills in at materialization",
        f"- area: {section['title']}",
        "- source: TBD  # from the original title parenthetical, if any",
        "",
    ]
    if rest:
        lines.append(f"_Original title parenthetical: {rest}_")
        lines.append("")
    lines.append(body)
    lines.append("")
    return "\n".join(lines)


def render_index(sections_items):
    out = ["# Vilan tracker — open items", ""]
    out.append(
        "`backlog <ID>` resolves to `items/<ID>.md` if open, or a "
        "tombstone in `archive.md` (or the frozen chain it points at) if "
        "closed — see `proposal/tracker-migration.md` §2."
    )
    out.append("")
    for section, items in sections_items:
        if not items:
            continue
        out.append(f"## {section['letter']}. {section['title']}")
        out.append("")
        out.append("| ID | Title | Kind | Discussion |")
        out.append("|----|-------|------|------------|")
        for item in items:
            h1 = item["title_line"].split("**")[0].strip()
            out.append(f"| [{item['id']}](items/{item['id']}.md) | {h1} | TBD | |")
        out.append("")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("backlog", type=pathlib.Path)
    ap.add_argument("--out", type=pathlib.Path, required=True)
    args = ap.parse_args()

    text = args.backlog.read_text(encoding="utf-8")
    header, sections, lines = parse_sections(text)

    items_dir = args.out / "items"
    items_dir.mkdir(parents=True, exist_ok=True)

    sections_items = []
    total = 0
    for section in sections:
        items = parse_items(section, lines)
        sections_items.append((section, items))
        for item in items:
            path = items_dir / f"{item['id']}.md"
            path.write_text(render_item_file(item["id"], section, item), encoding="utf-8")
            total += 1

    (args.out / "INDEX.md").write_text(render_index(sections_items), encoding="utf-8")
    (args.out / "chronicle.md").write_text(header + "\n", encoding="utf-8")

    print(f"sections: {len(sections)}", file=sys.stderr)
    print(f"items written: {total}", file=sys.stderr)
    for section, items in sections_items:
        print(f"  {section['letter']}: {len(items)}", file=sys.stderr)
    print(f"staged at: {args.out}", file=sys.stderr)
    print(
        "REVIEW BEFORE MATERIALIZING — kind/source fields are TBD "
        "placeholders (see the runbook §7.5 on the losslessness bar).",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
