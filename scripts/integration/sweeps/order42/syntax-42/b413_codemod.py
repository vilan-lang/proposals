#!/usr/bin/env python3
"""B413's codemod: the `resource` KEYWORD becomes the `[resource]` attribute.

    resource struct S { .. }           ->  [resource] struct S { .. }
    resource external struct Db;       ->  [resource] external struct Db;
    resource enum E { .. }             ->  [resource] enum E { .. }

Usage: b413_codemod.py [--check] PATH...   (files or directories)

- `.vl` files: every occurrence (code and comments — a comment that quotes a
  declaration should quote the spelling that parses).
- `.md` files: ONLY inside ``` fences (prose is edited by hand: it may be
  describing the old spelling on purpose).
- `.rs` files: every occurrence (the `.vl` programs Rust tests carry as string
  consts, and the comments beside them). Files that pin the OLD spelling on
  purpose (the parser's refusal of it) must be excluded by the caller.

`--check` rewrites nothing and exits 1 if any site would move (the residue
gate). Prints `path: N` per file touched and a total. Never touches git.
"""
import os
import re
import sys

PATTERN = re.compile(r"(?<![\w\[])resource(\s+)(external\s+struct|struct|enum)\b")

# What may stand before a DECLARATION's `resource` on its line: nothing but
# indentation, or a token that ends where a declaration may begin — `export`,
# an attribute's `]`, a string's opening `"` / an escaped `\n` (the `.vl`
# programs Rust tests carry), a backtick (a quoted declaration), `{`, `(`, `;`.
# Anything else is PROSE ("the resource enum `Handle`", a diagnostic's text),
# which names the KIND and keeps its word.
DECLARATION_PREFIX = re.compile(r'(^[ \t]*|(export|\]|"|\\n|`|\{|\(|;)[ \t]*)$')


def rewrite(text):
    count = 0

    def replace(match):
        nonlocal count
        line_start = text.rfind("\n", 0, match.start()) + 1
        if not DECLARATION_PREFIX.search(text[line_start:match.start()]):
            return match.group(0)
        count += 1
        return "[resource]" + match.group(1) + match.group(2)

    return PATTERN.sub(replace, text), count


def rewrite_markdown(text):
    out, count, inside = [], 0, False
    for line in text.splitlines(keepends=True):
        if line.lstrip().startswith("```"):
            inside = not inside
            out.append(line)
            continue
        if inside:
            line, n = rewrite(line)
            count += n
        out.append(line)
    return "".join(out), count


def files(paths):
    for path in paths:
        if os.path.isdir(path):
            for root, dirs, names in os.walk(path):
                dirs[:] = [d for d in dirs if d not in ("target", "node_modules", "dist", ".git")]
                for name in sorted(names):
                    if name.endswith((".vl", ".md", ".rs")):
                        yield os.path.join(root, name)
        else:
            yield path


def main(argv):
    check = "--check" in argv
    paths = [a for a in argv if a != "--check"]
    total = 0
    for path in files(paths):
        with open(path, encoding="utf-8") as handle:
            text = handle.read()
        if path.endswith(".md"):
            new, count = rewrite_markdown(text)
        else:
            new, count = rewrite(text)
        if count:
            total += count
            print(f"{path}: {count}")
            if not check:
                with open(path, "w", encoding="utf-8") as handle:
                    handle.write(new)
    print(f"total: {total}")
    return 1 if (check and total) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
