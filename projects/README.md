# Projects

Per-project trackers, one directory per project. This is the per-item
format piloted for kolt (2026-08-26) and — pending the owner's ruling on
the wider restructure (tracker N17) — the shape the rest of this repo
migrates toward: one file per item, so agents can read, edit, and close
items without contending over one long planning surface.

## Layout

    projects/<name>/tracker/items/<ID>.md   one item per file
    projects/<name>/tracker/INDEX.md        every OPEN item, one row each
    projects/<name>/tracker/archive.md      finished items, one tombstone each

- **IDs** are zero-padded, sequential, per-project, never reused.
- **Item files** open with `# <ID> — <title>`, then a short field block
  (`status` / `kind` / `area` / `discussion` / `source`, plus optional
  `flag` and `see-also` lines), then the body.
- **Closing an item**: delete its file, drop its INDEX row, and land one
  tombstone paragraph in `archive.md` — the same tombstone discipline as
  `tracker/backlog.md`, per file instead of per section.

## `.local` projects

A directory ending in `.local` (e.g. `projects/kolt.local/`) is personal
and machine-local: gitignored, never committed, and invisible to the
hygiene gate (which scans tracked files only). Use it for projects whose
tracker should ride beside the vilan planning surfaces without being
published with them.
