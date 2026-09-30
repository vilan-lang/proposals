#!/usr/bin/env python3
"""I9's estate codemod: `std::map::Map` -> `std::hash_map::HashMap` and
`std::set::Set` -> `std::hash_set::HashSet`.

Usage: codemod_i9.py [--check] PATH...

PATH is a file or a directory (walked for .vl, .md and .rs files; `target`,
`node_modules`, `dist`, `.git` and `.claude` are skipped). `--check` prints the
files that WOULD change and exits 1 if any would, without writing.

What it rewrites, per file kind:

- `.vl`: the whole file (see `rewrite_vilan`).
- `.md`: every ```vilan fence (any `vilan,...` info string). A fence with no
  import of its own inherits the bare names the document's earlier fences bound
  (a `vilan,fragment` beside the example that imported `Map`). Prose is NOT
  touched: it needs a reader (`Map` in prose may be the JS `Map` or the reactive
  node), and the script lists the prose lines that still say `Map`/`Set` so a
  person can take them.
- `.rs`: every raw string literal (`r"…"`, `r#"…"#`) that imports the old
  modules — the shape the inference/CLI pins embed programs in. Line-joined
  programs (`"import std::map::Map;\\n",` rows) are rewritten when a literal in
  the same file imports the old module and the literal itself is vilan-shaped;
  the script lists what it left for a person.

`rewrite_vilan` is semantic enough for the estate and no more:

1. Import statements. A path through `std::map`/`pkg::map`/`macro_std::map`
   becomes `…::hash_map`, and the `Map` leaves under it become `HashMap`
   (`std::map::Map`, `std::map::{ Map }`, `std::map::{ (impl Map<_, _>) }`,
   `std::map::Map as M`); the same for `set`/`Set`. An import of anything else
   is left alone — `import std::reactive::{ Map as MapNode }` is the reactive
   node, not the hash map.
2. The body. When an import BOUND the bare name (`Map`, not `Map as M`), every
   `Map` word outside import statements becomes `HashMap` — code, comments and
   strings alike (a comment in a file that imports the hash map talks about the
   hash map). A module import (`import std::map;`) rewrites `map::Map` in the
   body. Qualified paths (`std::map::Map`) are rewritten anywhere.
3. Never touched: `new Map`/`new Set`/`instanceof Map` (JS text in a string),
   `NativeMap`, `MapNode` and every other word that merely contains the name.

The deprecated alias modules themselves (`std/src/map.vl`, `std/src/set.vl`)
and `macro_std`'s re-export list are excluded: they are the old names on
purpose.
"""

import os
import re
import sys

SKIP_DIRS = {"target", "node_modules", "dist", ".git", ".claude"}
EXCLUDED_SUFFIXES = (
    os.path.join("vilan", "std", "src", "map.vl"),
    os.path.join("vilan", "std", "src", "set.vl"),
    os.path.join("vilan", "macro_std", "src", "lib.vl"),
)

KINDS = (
    # (old module, new module, old leaf, new leaf)
    ("map", "hash_map", "Map", "HashMap"),
    ("set", "hash_set", "Set", "HashSet"),
)

IMPORT_STATEMENT = re.compile(
    r"(?m)^([ \t]*(?:export\s*(?:\(\s*in[^)]*\)\s*)?(?:\[[^\]]*\]\s*)?)?import\s)([^;]*;)"
)


def matching_brace(text, open_index):
    depth = 0
    for index in range(open_index, len(text)):
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
            if depth == 0:
                return index
    return len(text)


def branch_end(text, start):
    """The end of the path branch that begins at `start` (just after `::`)."""
    index = start
    while index < len(text) and text[index] in " \t\n":
        index += 1
    if index < len(text) and text[index] == "{":
        return matching_brace(text, index) + 1
    depth = 0
    while index < len(text):
        character = text[index]
        if character in "(<":
            depth += 1
        elif character in ")>":
            depth -= 1
        elif depth == 0 and character in ",;}":
            return index
        index += 1
    return index


def rewrite_import(statement):
    """Rewrites one import statement's body; answers (new text, bindings).

    bindings: the set of names the statement binds bare that the body must
    follow — "Map"/"Set" for the leaf, "map"/"set" for a module import.
    """
    bindings = set()
    for old_module, new_module, old_leaf, new_leaf in KINDS:
        # Rooted paths (`std::map`, `pkg::map`, `macro_std::map`), and a
        # `map::` segment inside a rooted brace set (`std::{ map::Map, io }`).
        rooted = re.compile(
            r"\b((?:std|pkg|macro_std)::)" + old_module + r"\b(?!_)"
        )
        in_set = re.compile(r"(?<=[{,])(\s*)" + old_module + r"(?=\s*(::|,|}|\sas\s))")
        if not rooted.search(statement) and not (
            re.search(r"\b(?:std|pkg|macro_std)::\{", statement) and in_set.search(statement)
        ):
            continue
        statement = rooted.sub(lambda m: m.group(1) + new_module, statement)
        if re.search(r"\b(?:std|pkg|macro_std)::\{", statement):
            statement = in_set.sub(lambda m: m.group(1) + new_module, statement)
        # The leaves under each `new_module` path.
        out = []
        cursor = 0
        pattern = re.compile(r"\b" + new_module + r"\b")
        for match in pattern.finditer(statement):
            if match.start() < cursor:
                continue
            after = match.end()
            if statement.startswith("::", after):
                end = branch_end(statement, after + 2)
                branch = statement[after + 2 : end]
                renamed = re.sub(r"\b" + old_leaf + r"\b", new_leaf, branch)
                # Whether the leaf is bound bare (no alias on it).
                for leaf in re.finditer(r"\b" + new_leaf + r"\b", renamed):
                    rest = renamed[leaf.end():]
                    before = renamed[: leaf.start()]
                    inside_selector = before.count("(") > before.count(")")
                    if inside_selector:
                        continue
                    if re.match(r"\s+as\s+\w+", rest):
                        continue
                    bindings.add(old_leaf)
                out.append(statement[cursor:after + 2])
                out.append(renamed)
                cursor = end
            else:
                # A module import: `import std::hash_map;` or `… as m`.
                rest = statement[after:]
                if re.match(r"\s*(;|,|})", rest):
                    bindings.add(old_module)
        out.append(statement[cursor:])
        statement = "".join(out)
    return statement, bindings


def rename_body(text, bindings):
    for old_module, new_module, old_leaf, new_leaf in KINDS:
        text = re.sub(
            r"\b((?:std|pkg|macro_std)::)" + old_module + r"::" + old_leaf + r"\b",
            lambda m: m.group(1) + new_module + "::" + new_leaf,
            text,
        )
        if old_module in bindings:
            text = re.sub(
                r"(?<![\w:])" + old_module + r"::" + old_leaf + r"\b",
                new_module + "::" + new_leaf,
                text,
            )
        if old_leaf in bindings:
            text = re.sub(
                r"(?<!new )(?<!instanceof )(?<![\w$])" + old_leaf + r"\b(?![\w$])",
                new_leaf,
                text,
            )
    return text


def rewrite_vilan(text, inherited=frozenset()):
    """Rewrites a vilan source text; answers (new text, bindings)."""
    bindings = set(inherited)
    pieces = []
    cursor = 0
    for match in IMPORT_STATEMENT.finditer(text):
        pieces.append(("body", text[cursor : match.start()]))
        rewritten, bound = rewrite_import(match.group(2))
        bindings |= bound
        pieces.append(("import", match.group(1) + rewritten))
        cursor = match.end()
    pieces.append(("body", text[cursor:]))
    out = []
    for kind, piece in pieces:
        out.append(rename_body(piece, bindings) if kind == "body" else piece)
    return "".join(out), bindings


FENCE = re.compile(r"(?ms)^(```vilan[^\n]*\n)(.*?)(^```)")


def rewrite_markdown(text):
    inherited = set()
    out = []
    cursor = 0
    for match in FENCE.finditer(text):
        out.append(text[cursor : match.start(2)])
        body, bound = rewrite_vilan(match.group(2), frozenset(inherited))
        inherited |= bound
        out.append(body)
        cursor = match.end(2)
    out.append(text[cursor:])
    return "".join(out)


RAW_STRING = re.compile(r'(?s)r(#*)"(.*?)"\1')
OLD_IMPORT = re.compile(r"\b(?:std|pkg)::(?:map|set)\b(?!_)|\b(?:std|pkg)::\{[^}]*\b(?:map|set)::")


def rust_plain_literals(text):
    """(start, end, is_in_concat_id) spans of plain `"…"` literal CONTENTS.

    A small tokenizer: line comments, raw strings and char literals are
    skipped, so a quote inside one of them never opens a literal. Each span
    carries the id of the `concat!(…)` it sits in (or None), so a program
    split across rows is rewritten as one program.
    """
    spans = []
    index = 0
    concat_stack = []  # (paren depth at open, id)
    depth = 0
    next_id = 0
    length = len(text)
    while index < length:
        character = text[index]
        if text.startswith("//", index):
            newline = text.find("\n", index)
            index = length if newline < 0 else newline
            continue
        raw = re.match(r'r(#*)"', text[index:index + 70])
        if raw and (index == 0 or not (text[index - 1].isalnum() or text[index - 1] == "_")):
            closing = '"' + raw.group(1)
            end = text.find(closing, index + len(raw.group(0)))
            index = length if end < 0 else end + len(closing)
            continue
        if character == "'":
            char = re.match(r"'(\\.[^']*|[^\\'])'", text[index:index + 12])
            if char:
                index += len(char.group(0))
                continue
            index += 1
            continue
        if text.startswith("concat!(", index):
            depth += 1
            concat_stack.append((depth, next_id))
            next_id += 1
            index += len("concat!(")
            continue
        if character == "(":
            depth += 1
        elif character == ")":
            if concat_stack and concat_stack[-1][0] == depth:
                concat_stack.pop()
            depth -= 1
        elif character == '"':
            start = index + 1
            cursor = start
            while cursor < length and text[cursor] != '"':
                cursor += 2 if text[cursor] == "\\" else 1
            spans.append((start, cursor, concat_stack[-1][1] if concat_stack else None))
            index = cursor + 1
            continue
        index += 1
    return spans


def decode(literal):
    return literal.replace("\\n", "\x00\n")


def encode(literal):
    return literal.replace("\x00\n", "\\n")


def rewrite_rust(text):
    out = []
    cursor = 0
    for match in RAW_STRING.finditer(text):
        body = match.group(2)
        if not OLD_IMPORT.search(body):
            continue
        rewritten, _ = rewrite_vilan(body)
        out.append(text[cursor : match.start(2)])
        out.append(rewritten)
        cursor = match.end(2)
    out.append(text[cursor:])
    text = "".join(out)

    # Plain literals: a whole program in one escaped string, or a program
    # split across a `concat!`'s rows.
    spans = rust_plain_literals(text)
    groups = {}
    for start, end, group in spans:
        groups.setdefault(group, []).append((start, end))
    replacements = []
    for group, members in groups.items():
        units = [[member] for member in members] if group is None else [members]
        for unit in units:
            joined = "".join(decode(text[start:end]) for start, end in unit)
            if not OLD_IMPORT.search(joined):
                continue
            _, bindings = rewrite_vilan(joined)
            for start, end in unit:
                piece = decode(text[start:end])
                rewritten, _ = rewrite_vilan(piece, frozenset(bindings))
                if rewritten != piece:
                    replacements.append((start, end, encode(rewritten)))
    for start, end, new in sorted(replacements, reverse=True):
        text = text[:start] + new + text[end:]
    return text


def rewrite_path(path):
    if path.endswith(EXCLUDED_SUFFIXES):
        return None
    with open(path, encoding="utf-8") as handle:
        text = handle.read()
    if path.endswith(".vl"):
        new = rewrite_vilan(text)[0]
    elif path.endswith(".md"):
        new = rewrite_markdown(text)
    elif path.endswith(".rs"):
        new = rewrite_rust(text)
    else:
        return None
    return (text, new) if new != text else None


def walk(paths):
    for root in paths:
        if os.path.isfile(root):
            yield root
            continue
        for directory, subdirectories, files in os.walk(root):
            subdirectories[:] = sorted(d for d in subdirectories if d not in SKIP_DIRS)
            for name in sorted(files):
                if name.endswith((".vl", ".md", ".rs")):
                    yield os.path.join(directory, name)


LEFTOVER = re.compile(r"\b(?:std|pkg)::(?:map|set)\b(?!_)")


def main(argv):
    check = "--check" in argv
    paths = [argument for argument in argv if argument != "--check"]
    changed = []
    for path in walk(paths):
        result = rewrite_path(path)
        if result is None:
            continue
        changed.append(path)
        if not check:
            with open(path, "w", encoding="utf-8") as handle:
                handle.write(result[1])
    for path in changed:
        print(("would rewrite " if check else "rewrote ") + path)
    # What is left for a person: old paths the rewrite could not reach.
    for path in walk(paths):
        if path.endswith(EXCLUDED_SUFFIXES):
            continue
        with open(path, encoding="utf-8") as handle:
            for number, line in enumerate(handle, 1):
                if LEFTOVER.search(line):
                    print(f"left for a person: {path}:{number}: {line.rstrip()}")
    return 1 if (check and changed) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
