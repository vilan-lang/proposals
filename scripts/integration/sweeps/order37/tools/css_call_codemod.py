#!/usr/bin/env python3
"""A101 — rewrite every `css` block declaration from `property: value;` to `property(value);`.

Run over a DIRECTORY; every `.vl`, `.rs` and `.md` file under it is scanned for
`css { … }` blocks and rewritten in place (or reported with --dry-run).

The three rewrites (the CHANGELOG's `breaking` entry):
  1. a declaration `property: value;`  becomes the call `property(value);`
  2. a `{expr}` hole becomes the expression itself (there are no holes left)
  3. a dotted head with no block, `.method { }`/`.method`, already spells
     `.method();` (A69) — untouched here, it is named for the reader

Value rules (R10/R11/R12):
  * exactly one `{expr}` hole      -> the expression, verbatim              (1 argument)
  * a text value the CSS typer types -> the typed constructor (`100%` -> `pct(100)`)
  * any other text value           -> a string literal                     (1 argument)
  * text + holes, whitespace-separated -> N arguments, space-joined by the desugar
  * text + holes, GLUED (`{150}ms`) -> one i-string argument, holes kept
  * `--custom: v;`                 -> `--custom(v);` (R12, the property production
                                      already admits the leading dashes)

Escaping: a block inside a Rust string literal is decoded first (`\\"` -> `"`,
`\\n` -> newline, `r#"…"#` verbatim), rewritten in the DECODED text, and only the
rewritten spans are re-encoded back into the literal — nothing outside a
declaration is touched.

Exit status is 0 unless a file could not be parsed back after the rewrite.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from dataclasses import dataclass, field

# --- the CSS value typer (R11) ------------------------------------------------
#
# The typed constructor for a value E167's converter would have carried as a
# typed hole. Every name here is a free function of `std::style::prelude`, which
# is AMBIENT inside a css block, so a typed rewrite needs no import. The table is
# deliberately SMALL: a value it does not type stays a string literal, and the
# lowering-identity gate makes the two byte-identical, so the choice is
# readability only.

_UNIT_CONSTRUCTOR = {
    "px": "px",
    "rem": "rem",
    "em": "em",
    "vh": "vh",
    "vw": "vw",
    "%": "pct",
}

_NUMBER = re.compile(r"^(\d+(?:\.\d+)?)(px|rem|em|vh|vw|%)$")


def _number_text(digits: str) -> str:
    """`4` and `4.0` both spell the f64 the constructor takes; `1.5` keeps its
    fraction. The constructors take `f64`, and vilan reads a bare `4` as one in
    that position, so the digits pass through as written."""
    return digits


def typed_constructor(value: str) -> str | None:
    """The typed `std::style::prelude` constructor for a whole CSS value, or
    `None` when the value has none (and so stays a string)."""
    match = _NUMBER.match(value.strip())
    if match is None:
        return None
    digits, unit = match.groups()
    name = _UNIT_CONSTRUCTOR[unit]
    return f"{name}({_number_text(digits)})"


# --- the block scanner --------------------------------------------------------


@dataclass
class Hole:
    start: int  # at the `{`
    end: int  # just past the `}`


@dataclass
class Text:
    start: int
    end: int


@dataclass
class Declaration:
    start: int  # at the property's first byte
    end: int  # just past the `;`
    property_start: int
    property_end: int
    colon: int
    value_start: int
    value_end: int  # just before the `;`
    pieces: list


@dataclass
class Block:
    open_brace: int
    close_brace: int
    declarations: list = field(default_factory=list)
    nested: int = 0
    links: int = 0


def _skip_trivia(text: str, at: int, stop: int) -> int:
    while at < stop:
        character = text[at]
        if character.isspace():
            at += 1
            continue
        if text.startswith("//", at):
            end = text.find("\n", at)
            at = stop if end < 0 or end > stop else end
            continue
        if text.startswith("/*", at):
            end = text.find("*/", at)
            at = stop if end < 0 or end + 2 > stop else end + 2
            continue
        return at
    return at


def _skip_string(text: str, at: int) -> int:
    """Past the string literal opening at `at` (a `"`)."""
    at += 1
    while at < len(text):
        if text[at] == "\\":
            at += 2
            continue
        if text[at] == '"':
            return at + 1
        at += 1
    return at


def _balanced(text: str, at: int, stop: int) -> int:
    """Past the bracket opening at `at`, string- and comment-aware."""
    openers = "([{"
    closers = ")]}"
    depth = 0
    while at < stop:
        character = text[at]
        if character == '"':
            at = _skip_string(text, at)
            continue
        if text.startswith("//", at):
            end = text.find("\n", at)
            at = stop if end < 0 else end
            continue
        if character in openers:
            depth += 1
        elif character in closers:
            depth -= 1
            if depth == 0:
                return at + 1
        at += 1
    return at


_PROPERTY = re.compile(r"-*[A-Za-z_][A-Za-z0-9_]*(?:-[A-Za-z0-9_]+)*")
_IDENT = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
_CSS_KEYWORD = re.compile(r"(?<![A-Za-z0-9_])css\s*\{")


def string_regions(text: str) -> list[tuple[int, int]]:
    """The `"…"` spans of `text` read as VILAN source — where a `css {` is data
    rather than code.

    The shape that needs it is a macro's `source("const css { … }")`: the block
    inside is a vilan STRING, and rewriting it would put bare `"` inside the
    string that holds it. A human migrates those; this keeps the codemod from
    corrupting them."""
    regions = []
    at = 0
    while at < len(text):
        if text.startswith("//", at):
            end = text.find("\n", at)
            at = len(text) if end < 0 else end
            continue
        if text[at] == '"':
            end = _skip_string(text, at)
            regions.append((at, end))
            at = end
            continue
        at += 1
    return regions


def find_blocks(text: str, vilan_source: bool = False) -> list[Block]:
    """Every `css { … }` block in `text`, outermost first, each with its own
    declarations (a nested rule's declarations belong to the nested Block that
    `parse_body` records for it).

    `vilan_source` says the text IS vilan code (a `.vl` file, or the decoded
    content of a Rust string literal), where a `css {` inside a string literal
    is data and is left alone."""
    blocks: list[Block] = []
    regions = string_regions(text) if vilan_source else []
    for match in _CSS_KEYWORD.finditer(text):
        open_brace = match.end() - 1
        if any(start < open_brace < end for start, end in regions):
            continue
        close = _balanced(text, open_brace, len(text))
        if close > len(text) or text[close - 1 : close] != "}":
            # The block does not CLOSE in this text. In a `.vl` file that is a
            # syntax error; in a Rust fixture it is a `concat!` whose block
            # spans several literals, and migrating the half that is here would
            # leave the other half behind. Reported and skipped whole.
            print(
                "  LEFT FOR A HUMAN (the block does not close in this text — a "
                f"`concat!` split?): {text[open_brace - 4 : open_brace + 40]!r}"
            )
            continue
        block = Block(open_brace=open_brace, close_brace=close - 1)
        _parse_body(text, open_brace + 1, close - 1, block, blocks)
        blocks.append(block)
    return blocks


def _parse_body(text: str, start: int, stop: int, block: Block, blocks: list[Block]) -> None:
    at = start
    while True:
        at = _skip_trivia(text, at, stop)
        if at >= stop:
            return
        if text[at] == ".":
            head = at + 1
            name = _IDENT.match(text, head)
            if name is None:
                return
            after = name.end()
            after = _skip_trivia(text, after, stop)
            if after < stop and text[after] == "(":
                after = _balanced(text, after, stop)
                after = _skip_trivia(text, after, stop)
            if after < stop and text[after] == "{":
                inner_close = _balanced(text, after, stop) - 1
                nested = Block(open_brace=after, close_brace=inner_close)
                block.nested += 1
                _parse_body(text, after + 1, inner_close, nested, blocks)
                blocks.append(nested)
                at = inner_close + 1
                continue
            if after < stop and text[after] == ";":
                block.links += 1
                at = after + 1
                continue
            return
        declaration = _parse_declaration(text, at, stop)
        if declaration is None:
            return
        block.declarations.append(declaration)
        at = declaration.end


def _parse_declaration(text: str, at: int, stop: int) -> Declaration | None:
    name = _PROPERTY.match(text, at)
    if name is None:
        return None
    colon = _skip_trivia(text, name.end(), stop)
    if colon >= stop or text[colon] != ":":
        return None
    value_start = _skip_trivia(text, colon + 1, stop)
    cursor = value_start
    pieces: list = []
    text_from = value_start
    while cursor < stop:
        character = text[cursor]
        if character == '"':
            cursor = _skip_string(text, cursor)
            continue
        if character == "{":
            # A `{` ALWAYS opens a hole, at any depth — `calc({w} + 2px)` is
            # the shape that matters, and the value parser this replaces
            # tracked no parens either: `(`, `[` and their partners are
            # ordinary value text.
            if text_from < cursor:
                pieces.append(Text(text_from, cursor))
            end = _balanced(text, cursor, stop)
            pieces.append(Hole(cursor, end))
            cursor = end
            text_from = end
            continue
        if character == ";":
            break
        if character == "}":
            return None
        cursor += 1
    if cursor >= stop:
        return None
    value_end = cursor
    if text_from < value_end:
        pieces.append(Text(text_from, value_end))
    return Declaration(
        start=at,
        end=cursor + 1,
        property_start=name.start(),
        property_end=name.end(),
        colon=colon,
        value_start=value_start,
        value_end=value_end,
        pieces=pieces,
    )


# --- the rewrite --------------------------------------------------------------


@dataclass
class Counts:
    blocks: int = 0
    declarations: int = 0
    hole: int = 0
    typed: int = 0
    string: int = 0
    joined: int = 0
    interpolated: int = 0
    skipped: int = 0


def _hole_text(text: str, piece: Hole) -> str:
    return text[piece.start + 1 : piece.end - 1].strip()


def _string_literal(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def rewrite_declaration(
    text: str, declaration: Declaration, counts: Counts
) -> str | None:
    """The declaration's replacement text `property(arguments);`, or `None` when
    it has no mechanical rewrite and is left for a human."""
    name = text[declaration.property_start : declaration.property_end]
    pieces = declaration.pieces
    holes = [piece for piece in pieces if isinstance(piece, Hole)]
    if len(pieces) == 1 and isinstance(pieces[0], Hole):
        counts.hole += 1
        return f"{name}({_hole_text(text, pieces[0])});"
    if not holes:
        raw = text[declaration.value_start : declaration.value_end].strip()
        typed = typed_constructor(raw)
        if typed is not None:
            counts.typed += 1
            return f"{name}({typed});"
        counts.string += 1
        return f"{name}({_string_literal(raw)});"
    # Mixed. The pieces are N arguments when every boundary between them is
    # whitespace — the desugar joins N arguments with exactly one space, so a
    # GLUED boundary (`{150}ms`, `calc({w} + 2px)`) would gain a space it never
    # had. Those keep one argument, spelled as the i-string the desugar already
    # builds for them.
    glued = False
    for index, piece in enumerate(pieces[:-1]):
        left = text[piece.end - 1]
        right = text[pieces[index + 1].start]
        left_text = text[piece.start : piece.end]
        right_text = text[pieces[index + 1].start : pieces[index + 1].end]
        if not left_text.endswith((" ", "\t")) and not right_text.startswith((" ", "\t")):
            glued = True
            break
        del left, right
    if glued:
        # An i-string hole holds ONE expression and a nested brace ends it
        # early, so a glued hole carrying a struct literal, a block or a
        # `match` has no i-string spelling. Those are left exactly as written
        # and reported, for a human to bind the value first.
        if any(
            isinstance(piece, Hole) and ("{" in _hole_text(text, piece) or "}" in _hole_text(text, piece))
            for piece in pieces
        ):
            counts.skipped += 1
            return None
        counts.interpolated += 1
        body = ""
        for piece in pieces:
            if isinstance(piece, Hole):
                # `piece(..)` is `std::style::prelude`'s, ambient inside a block:
                # it renders the value AND puts its `:root` line on the sheet,
                # which is exactly what the desugar did for every hole of a
                # mixed value before A101. Uniform over every hole, so the
                # rewrite is byte-identical whatever the hole's type.
                body += "{piece(" + _hole_text(text, piece) + ")}"
            else:
                body += text[piece.start : piece.end].replace("\\", "\\\\").replace('"', '\\"')
        return f'{name}(i"{body}");'
    counts.joined += 1
    arguments = []
    for piece in pieces:
        if isinstance(piece, Hole):
            arguments.append(_hole_text(text, piece))
        else:
            run = text[piece.start : piece.end].strip()
            if run:
                arguments.append(_string_literal(run))
    return f"{name}({', '.join(arguments)});"


def rewrite_text(
    text: str, counts: Counts, vilan_source: bool = False
) -> tuple[str, list[tuple[int, int, str]]]:
    """`text` with every declaration rewritten, and the edits that did it."""
    blocks = find_blocks(text, vilan_source)
    edits: list[tuple[int, int, str]] = []
    for block in blocks:
        counts.blocks += 1
        for declaration in block.declarations:
            counts.declarations += 1
            replacement = rewrite_declaration(text, declaration, counts)
            if replacement is None:
                print(
                    "  LEFT FOR A HUMAN (a glued hole carrying braces): "
                    f"{text[declaration.start:declaration.end]!r}"
                )
                continue
            edits.append((declaration.start, declaration.end, replacement))
    edits.sort(key=lambda edit: edit[0])
    out = []
    cursor = 0
    for start, end, replacement in edits:
        out.append(text[cursor:start])
        out.append(replacement)
        cursor = end
    out.append(text[cursor:])
    return "".join(out), edits


# --- Rust string literals -----------------------------------------------------


@dataclass
class Literal:
    start: int  # the first byte of the literal's CONTENT
    end: int  # just past its content
    raw: bool
    hashes: int = 0  # a raw string's `#` count
    open_start: int = 0  # the `r` of `r#"`, for a delimiter bump


def rust_string_literals(source: str) -> list[Literal]:
    """Every string literal's content span, raw strings included. Line and block
    comments and char literals are skipped so a `"` inside one never opens a
    literal."""
    literals: list[Literal] = []
    at = 0
    length = len(source)
    while at < length:
        character = source[at]
        if source.startswith("//", at):
            end = source.find("\n", at)
            at = length if end < 0 else end + 1
            continue
        if source.startswith("/*", at):
            end = source.find("*/", at)
            at = length if end < 0 else end + 2
            continue
        if character == "r" and at + 1 < length and source[at + 1] in '#"':
            hashes = 0
            scan = at + 1
            while scan < length and source[scan] == "#":
                hashes += 1
                scan += 1
            if scan < length and source[scan] == '"':
                closing = '"' + "#" * hashes
                end = source.find(closing, scan + 1)
                if end < 0:
                    break
                literals.append(
                    Literal(scan + 1, end, raw=True, hashes=hashes, open_start=at)
                )
                at = end + len(closing)
                continue
        if character == '"':
            scan = at + 1
            while scan < length:
                if source[scan] == "\\":
                    scan += 2
                    continue
                if source[scan] == '"':
                    break
                scan += 1
            literals.append(Literal(at + 1, scan, raw=False))
            at = scan + 1
            continue
        if character == "'":
            # A char literal or a lifetime; neither can hold a `css` block.
            if at + 1 < length and source[at + 1] == "\\":
                at += 4
            else:
                at += 2
            continue
        at += 1
    return literals


_ESCAPES = {"n": "\n", "t": "\t", "r": "\r", "0": "\0", '"': '"', "'": "'", "\\": "\\"}


def decode(content: str) -> tuple[str, list[int]]:
    """A non-raw literal's content, decoded, with the raw offset of each decoded
    character (plus a final offset just past the last one)."""
    out = []
    offsets = []
    at = 0
    while at < len(content):
        if content[at] == "\\" and at + 1 < len(content):
            escape = content[at + 1]
            if escape in _ESCAPES:
                out.append(_ESCAPES[escape])
                offsets.append(at)
                at += 2
                continue
            if escape == "\n":
                # A line continuation: the newline and the indent that follows
                # it are not in the string.
                at += 2
                while at < len(content) and content[at] in " \t":
                    at += 1
                continue
            if escape == "u" and at + 2 < len(content) and content[at + 2] == "{":
                end = content.find("}", at)
                out.append(chr(int(content[at + 3 : end], 16)))
                offsets.append(at)
                at = end + 1
                continue
            if escape == "x":
                out.append(chr(int(content[at + 2 : at + 4], 16)))
                offsets.append(at)
                at += 4
                continue
        out.append(content[at])
        offsets.append(at)
        at += 1
    offsets.append(len(content))
    return "".join(out), offsets


def encode(text: str) -> str:
    return text.replace("\\", "\\\\").replace('"', '\\"')


def rewrite_rust(source: str, counts: Counts) -> str:
    edits: list[tuple[int, int, str]] = []
    for literal in rust_string_literals(source):
        content = source[literal.start : literal.end]
        if "css" not in content:
            continue
        if literal.raw:
            _, inner = rewrite_text(content, counts, vilan_source=True)
            closing = '"' + "#" * literal.hashes
            # A replacement holding the literal's own closing delimiter would
            # END it — `color("#333")` inside `r#"…"#` closes at the `"#`. The
            # fix is the one a human would make: one more `#` on each
            # delimiter, which changes nothing about the literal's content.
            if literal.hashes and any(closing in text for _, _, text in inner):
                edits.append(
                    (
                        literal.open_start,
                        literal.start,
                        "r" + "#" * (literal.hashes + 1) + '"',
                    )
                )
                edits.append(
                    (
                        literal.end,
                        literal.end + 1 + literal.hashes,
                        '"' + "#" * (literal.hashes + 1),
                    )
                )
            for start, end, replacement in inner:
                edits.append((literal.start + start, literal.start + end, replacement))
            continue
        decoded, offsets = decode(content)
        _, inner = rewrite_text(decoded, counts, vilan_source=True)
        for start, end, replacement in inner:
            edits.append(
                (
                    literal.start + offsets[start],
                    literal.start + offsets[end],
                    encode(replacement),
                )
            )
    edits.sort(key=lambda edit: edit[0])
    out = []
    cursor = 0
    for start, end, replacement in edits:
        out.append(source[cursor:start])
        out.append(replacement)
        cursor = end
    out.append(source[cursor:])
    return "".join(out)


# --- the driver ---------------------------------------------------------------

SKIP_DIRECTORIES = {".git", "target", "node_modules", "dist", ".claude"}
SKIP_FILES = {"CHANGELOG.md"}


def walk(root: str):
    for directory, subdirectories, files in os.walk(root):
        subdirectories[:] = [name for name in subdirectories if name not in SKIP_DIRECTORIES]
        for name in sorted(files):
            if name in SKIP_FILES:
                continue
            if name.endswith((".vl", ".rs", ".md")):
                yield os.path.join(directory, name)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", help="the directory to rewrite")
    parser.add_argument("--dry-run", action="store_true", help="report, write nothing")
    parser.add_argument("--census", action="store_true", help="count blocks, rewrite nothing")
    arguments = parser.parse_args()

    total = Counts()
    per_file: list[tuple[str, Counts]] = []
    for path in walk(arguments.root):
        with open(path, encoding="utf-8") as handle:
            source = handle.read()
        if "css" not in source:
            continue
        counts = Counts()
        if path.endswith(".rs"):
            rewritten = rewrite_rust(source, counts)
        else:
            rewritten, _ = rewrite_text(
                source, counts, vilan_source=path.endswith(".vl")
            )
        if counts.declarations == 0 and counts.blocks == 0:
            continue
        per_file.append((path, counts))
        for field_name in vars(counts):
            setattr(total, field_name, getattr(total, field_name) + getattr(counts, field_name))
        if not arguments.dry_run and not arguments.census and rewritten != source:
            with open(path, "w", encoding="utf-8") as handle:
                handle.write(rewritten)
    width = max((len(path) for path, _ in per_file), default=0)
    for path, counts in per_file:
        print(
            f"{path:<{width}}  blocks {counts.blocks:>3}  declarations {counts.declarations:>4}"
            f"  hole {counts.hole:>4}  typed {counts.typed:>3}  string {counts.string:>4}"
            f"  joined {counts.joined:>3}  i-string {counts.interpolated:>3}"
            f"  left {counts.skipped:>2}"
        )
    print(
        f"\nTOTAL  blocks {total.blocks}  declarations {total.declarations}  "
        f"hole {total.hole}  typed {total.typed}  string {total.string}  "
        f"joined {total.joined}  i-string {total.interpolated}  "
        f"left for a human {total.skipped}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
