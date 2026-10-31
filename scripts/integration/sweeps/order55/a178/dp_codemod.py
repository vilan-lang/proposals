#!/usr/bin/env python3
"""A178 S3 - kolt's lengths in design pixels: `rem(n / 16)` becomes `dp(n)`.

Run over a PACKAGE root (the directory holding `vilan.toml`); every `.vl` file
under `src/` is scanned, except the package's `generated = "..."` roots.

    dp_codemod.py <root> --check     print the unified diff, change nothing
    dp_codemod.py <root> --apply     rewrite the files (and delete the scale)

The rewrites (proposal/length.md section 6; the owner's word on the scale):

  1. `rem(<n> / 16)` -> `dp(<n>)`, negatives and decimals included; the
     qualified `Length::rem(<n> / 16)` -> `Length::dp(<n>)`.
  2. `rem(0)` -> `dp(0)` (and `Length::rem(0)` -> `Length::dp(0)`).
  3. A module-level numeric constant `let <name> = <n>f;` whose EVERY use is
     `rem(<name> / 16)` (comments, strings and import lists aside) becomes
     `const let <name> = dp(<n>);`, and each `rem(<name> / 16)` becomes
     `<name>`. A constant with any other use is LEFT ALONE and printed.
  4. The scale (`const let size = Scale::new(0.25);`, kolt's B340 customer):
     every `size(<n>)` call in the declaring file and in the files importing
     `size` from it becomes `dp(<4n>)` written out; `size` leaves those import
     lists; the declaration, its `Scale` import and `src/lib/scale_step.vl` are
     deleted. Refused, and printed, if `size` is used any other way.

Why this is CSS-identical: a `dp` length renders in `rem` wherever a property
prefers rem and wherever no property chooses (a `css` block's undotted
declaration is `raw`, a several-argument value goes through `piece`), as
`<n> / 16` - the same f64 division `rem(<n> / 16)` performed at the site - so
the text and the content-hashed class names do not move. The one place a `dp`
renders otherwise is the width of a DOTTED px-role builder (`.border(..)`,
`.border_left(..)`, ...: a hairline renders px). A site there is LEFT ALONE and
printed: rewriting it changes that rule (`0.125rem` -> `2px`), which may well
be what a hairline wants, but is the owner's call, not a codemod's.

`dp` is ambient in a css block exactly as `rem` is, so a bare `rem(..)` site
(which compiled, so it was in a block) takes a bare `dp(..)`; the scale's
`size(..)` sites are all in blocks in kolt, and a `vilan check` says so if one
is not. A constant's declaration is outside any block: the file's
`std::web::style::prelude` import gains `dp`, and a file without one is
written `style::Length::dp(..)` (the web prelude's ambient `style` module).

Anything else that divides by 16 - `rem((a + b) / 16)`, `rem(name / 16)` for a
name the tool could not prove - is left as written and printed under REVIEW.
Run `vilan fmt` over the result (an import list may want re-wrapping).

stdlib only. Exit status 0; 2 on a usage error.
"""

from __future__ import annotations

import argparse
import difflib
import os
import re
import sys

NUMBER = r"-?\d+(?:\.\d+)?f?"
SIXTEEN = r"16(?:\.0+)?f?"
# A `rem(` CALL: not a method (`.rem(`), not part of a longer name or a
# hyphenated CSS property.
QUALIFIER = r"(?P<qualifier>(?:\w+::)*Length::)?"
CALL_HEAD = r"(?<![\w.:\-])" + QUALIFIER + r"rem\(\s*"
LITERAL_SITE = re.compile(CALL_HEAD + r"(?P<number>" + NUMBER + r")\s*/\s*" + SIXTEEN + r"\s*\)")
ZERO_SITE = re.compile(CALL_HEAD + r"(?P<number>0(?:\.0+)?f?)\s*\)")
NAME_SITE = re.compile(CALL_HEAD + r"(?P<name>[A-Za-z_]\w*)\s*/\s*" + SIXTEEN + r"\s*\)")
ANY_SIXTEEN = re.compile(r"(?<![\w.\-])(?:(?:\w+::)*Length::)?rem\([^;\n]*/\s*" + SIXTEEN)
CONSTANT_DECLARATION = re.compile(
    r"^(?P<export>export )?let (?P<name>[A-Za-z_]\w*) = (?P<number>" + NUMBER + r");$", re.M
)
SIZE_SITE = re.compile(r"(?<![\w.:\-])size\(\s*(?P<number>-?\d+(?:\.\d+)?)f?\s*\)")
SCALE_DECLARATION = re.compile(r"^(?:export )?const let size = Scale::new\(0\.25f?\);\n", re.M)
SCALE_IMPORT = re.compile(r"^import pkg::lib::scale_step::Scale;\n", re.M)
# The builders whose LENGTH argument renders a `dp` in px (std's `Role::Px`).
PX_ROLE_HEAD = re.compile(r"\.(?:border|border_top|border_right|border_bottom|border_left)\(\s*$")


def mask(text: str) -> str:
    """`text` with every comment and string literal blanked to spaces (newlines
    kept), so positions line up and nothing inside one is matched. An i-string's
    holes are code and stay; `\"\"\"` raw strings are blanked whole."""
    out = list(text)
    index = 0
    length = len(text)

    def blank(start: int, end: int) -> None:
        for position in range(start, end):
            if out[position] != "\n":
                out[position] = " "

    while index < length:
        if text.startswith("//", index):
            end = text.find("\n", index)
            end = length if end == -1 else end
            blank(index, end)
            index = end
        elif text.startswith('"""', index):
            end = text.find('"""', index + 3)
            end = length if end == -1 else end + 3
            blank(index, end)
            index = end
        elif text[index] == '"':
            interpolated = index > 0 and text[index - 1] == "i"
            start = index
            index += 1
            depth = 0
            segment = index
            while index < length:
                character = text[index]
                if character == "\\":
                    index += 2
                    continue
                if interpolated and character == "{" and depth == 0:
                    blank(segment, index)
                    depth = 1
                elif interpolated and depth > 0:
                    if character == "{":
                        depth += 1
                    elif character == "}":
                        depth -= 1
                        if depth == 0:
                            segment = index + 1
                elif character == '"':
                    break
                index += 1
            blank(segment if interpolated else start + 1, index)
            index += 1
        else:
            index += 1
    return "".join(out)


def number_text(number: str) -> str:
    return number[:-1] if number.endswith("f") else number


def quadruple(number: str) -> str:
    value = float(number) * 4
    return str(int(value)) if value == int(value) else repr(value)


def generated_roots(root: str) -> list[str]:
    try:
        manifest = open(os.path.join(root, "vilan.toml"), encoding="utf-8").read()
    except OSError:
        return []
    roots = []
    for match in re.finditer(r"^generated\s*=\s*(.+)$", manifest, re.M):
        roots += [os.path.normpath(value) for value in re.findall(r'"([^"]+)"', match.group(1))]
    return roots


def sources(root: str) -> list[str]:
    generated = generated_roots(root)
    found = []
    for directory, subdirectories, files in os.walk(os.path.join(root, "src")):
        subdirectories.sort()
        relative = os.path.relpath(directory, root)
        if any(relative == g or relative.startswith(g + os.sep) for g in generated):
            subdirectories[:] = []
            continue
        found += [os.path.join(directory, name) for name in sorted(files) if name.endswith(".vl")]
    return found


IMPORT_LIST = re.compile(r"^import (?P<path>[\w:]+)::\{(?P<body>[^}]*)\};", re.M)


def import_lists(text: str):
    """Every `import a::b::{ .. };` brace list: (start, end, module path, names)."""
    for match in IMPORT_LIST.finditer(text):
        names = [name.strip() for name in match.group("body").split(",") if name.strip()]
        yield match.start(), match.end(), match.group("path"), names


def import_spans(text: str) -> list[tuple[int, int]]:
    spans = [(match.start(), match.end()) for match in IMPORT_LIST.finditer(text)]
    spans += [(match.start(), match.end()) for match in re.finditer(r"^import [^{\n]*;$", text, re.M)]
    return spans


def edit_import(text: str, module: str, add: str | None = None, remove: str | None = None) -> str:
    for start, end, path, names in list(import_lists(text)):
        if path != module:
            continue
        if remove in names:
            names = [name for name in names if name != remove]
        if add and add not in names:
            types = [name for name in names if name[:1].isupper()]
            values = sorted([name for name in names if not name[:1].isupper()] + [add])
            names = types + values
        if not names:
            end = end + 1 if text[end:end + 1] == "\n" else end
            return text[:start] + text[end:]
        if "\n" in text[start:end]:
            replacement = "import " + path + "::{\n" + "".join(f"\t{name},\n" for name in names) + "};"
        else:
            replacement = "import " + path + "::{ " + ", ".join(names) + " };"
        return text[:start] + replacement + text[end:]
    return text


def line_of(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("root")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true", help="print the diff, change nothing")
    mode.add_argument("--apply", action="store_true", help="rewrite the files")
    arguments = parser.parse_args()
    root = os.path.abspath(arguments.root)
    if not os.path.isfile(os.path.join(root, "vilan.toml")):
        print(f"{root} holds no vilan.toml", file=sys.stderr)
        return 2
    files = sources(root)
    original = {path: open(path, encoding="utf-8").read() for path in files}
    masked = {path: mask(body) for path, body in original.items()}
    review: list[str] = []
    counts = {"literal": 0, "zero": 0, "constant use": 0, "size": 0, "px-role kept": 0}

    def where(path: str, offset: int) -> str:
        number = line_of(original[path], offset)
        return f"{os.path.relpath(path, root)}:{number}: {original[path].split(chr(10))[number - 1].strip()}"

    def in_spans(offset: int, spans) -> bool:
        return any(start <= offset < end for start, end in spans)

    def px_role(path_text_masked: str, offset: int) -> bool:
        return PX_ROLE_HEAD.search(path_text_masked[max(0, offset - 80):offset]) is not None

    # --- 3. constants, decided over the whole package before any rewrite ----
    proven: dict[str, tuple[str, str, str]] = {}
    for path, body in original.items():
        for declaration in CONSTANT_DECLARATION.finditer(masked[path]):
            name = declaration.group("name")
            word = re.compile(r"(?<![\w.:\-])" + re.escape(name) + r"(?!\w)")
            others, sites = [], 0
            for other_path, other_masked in masked.items():
                imports = import_spans(other_masked)
                rewritable = []
                for site in NAME_SITE.finditer(other_masked):
                    if site.group("name") == name and not site.group("qualifier"):
                        if px_role(other_masked, site.start()):
                            others.append(where(other_path, site.start()) + "  (a px-role builder)")
                        rewritable.append((site.start(), site.end()))
                sites += len(rewritable)
                for use in word.finditer(other_masked):
                    if other_path == path and use.start() == declaration.start("name"):
                        continue
                    if in_spans(use.start(), imports) or in_spans(use.start(), rewritable):
                        continue
                    others.append(where(other_path, use.start()))
            if sites == 0:
                continue
            if others:
                review.append(
                    f"constant `{name}` kept as an f64 ({where(path, declaration.start())}) - other uses: "
                    + "; ".join(others)
                )
                continue
            proven[name] = (path, declaration.group("number"), declaration.group("export") or "")

    # --- 4. the scale --------------------------------------------------------
    scale_home = next((path for path, body in masked.items() if SCALE_DECLARATION.search(body)), None)
    scale_files: list[str] = []
    home_module = ""
    if scale_home is not None:
        home_module = "pkg::" + os.path.relpath(scale_home, os.path.join(root, "src"))[:-3].replace(os.sep, "::")
        scale_files = [scale_home] + [
            path
            for path in files
            if path != scale_home
            and any(module == home_module and "size" in names for _s, _e, module, names in import_lists(masked[path]))
        ]
        refused = []
        for path in scale_files:
            body = masked[path]
            imports = import_spans(body)
            declaration = SCALE_DECLARATION.search(body)
            for use in re.finditer(r"(?<![\w.:\-])size(?!\w)", body):
                if in_spans(use.start(), imports):
                    continue
                if declaration and declaration.start() <= use.start() < declaration.end():
                    continue
                if SIZE_SITE.match(body, use.start()):
                    if px_role(body, use.start()):
                        refused.append(where(path, use.start()) + "  (a px-role builder)")
                    continue
                refused.append(where(path, use.start()))
        if refused:
            review.append("the scale is kept - `size` is used other than as `size(<n>)`: " + "; ".join(refused))
            scale_files = []

    # --- the rewrites ----------------------------------------------------------
    text = dict(original)
    for path in files:
        body, shadow = original[path], masked[path]
        edits: list[tuple[int, int, str]] = []

        for site in LITERAL_SITE.finditer(shadow):
            if px_role(shadow, site.start()):
                counts["px-role kept"] += 1
                review.append("px-role builder, left as written (a dp there renders px): " + where(path, site.start()))
                continue
            counts["literal"] += 1
            edits.append((site.start(), site.end(), (site.group("qualifier") or "") + "dp(" + number_text(site.group("number")) + ")"))
        for site in ZERO_SITE.finditer(shadow):
            if px_role(shadow, site.start()):
                counts["px-role kept"] += 1
                review.append("px-role builder, left as written (a dp there renders px): " + where(path, site.start()))
                continue
            counts["zero"] += 1
            edits.append((site.start(), site.end(), (site.group("qualifier") or "") + "dp(0)"))
        for site in NAME_SITE.finditer(shadow):
            if site.group("name") in proven and not site.group("qualifier"):
                counts["constant use"] += 1
                edits.append((site.start(), site.end(), site.group("name")))
        if path in scale_files:
            imports = import_spans(shadow)
            for site in SIZE_SITE.finditer(shadow):
                if in_spans(site.start(), imports):
                    continue
                counts["size"] += 1
                edits.append((site.start(), site.end(), "dp(" + quadruple(site.group("number")) + ")"))
        for start, end, replacement in sorted(edits, reverse=True):
            body = body[:start] + replacement + body[end:]

        if path in scale_files:
            if path == scale_home:
                body = SCALE_DECLARATION.sub("", body)
                body = SCALE_IMPORT.sub("", body)
                body = re.sub(r"\n\n\n+", "\n\n", body)
            else:
                body = edit_import(body, home_module, remove="size")
        for name, (home, number, export) in proven.items():
            if home != path:
                continue
            has_prelude = any(module == "std::web::style::prelude" for _s, _e, module, _n in import_lists(body))
            constructor = "dp" if has_prelude else "style::Length::dp"
            body = re.sub(
                r"^" + re.escape(export) + r"let " + re.escape(name) + r" = " + re.escape(number) + r";$",
                f"{export}const let {name} = {constructor}({number_text(number)});",
                body,
                count=1,
                flags=re.M,
            )
            if has_prelude:
                body = edit_import(body, "std::web::style::prelude", add="dp")
        text[path] = body

    for path in files:
        shadow = mask(text[path])
        for site in ANY_SIXTEEN.finditer(shadow):
            number = line_of(text[path], site.start())
            line = text[path].split("\n")[number - 1].strip()
            if not any(line in entry for entry in review):
                review.append(f"left as written: {os.path.relpath(path, root)}:{number}: {line}")

    deleted = []
    if scale_files:
        scale_file = os.path.join(root, "src", "lib", "scale_step.vl")
        still = [
            path for path in files
            if path != scale_file and re.search(r"\bscale_step\b|\bScale\b", mask(text[path]))
        ]
        if os.path.exists(scale_file) and not still:
            deleted.append(scale_file)
        elif os.path.exists(scale_file):
            review.append("src/lib/scale_step.vl kept: still named in " + ", ".join(os.path.relpath(p, root) for p in still))

    # --- write or show ----------------------------------------------------------
    changed = [path for path in files if text[path] != original[path] and path not in deleted]
    for path in changed:
        relative = os.path.relpath(path, root)
        if arguments.check:
            sys.stdout.writelines(
                difflib.unified_diff(
                    original[path].splitlines(keepends=True),
                    text[path].splitlines(keepends=True),
                    fromfile="a/" + relative,
                    tofile="b/" + relative,
                )
            )
        else:
            with open(path, "w", encoding="utf-8") as handle:
                handle.write(text[path])
    for path in deleted:
        relative = os.path.relpath(path, root)
        if arguments.check:
            sys.stdout.writelines(
                difflib.unified_diff(original[path].splitlines(keepends=True), [], fromfile="a/" + relative, tofile="/dev/null")
            )
        else:
            os.remove(path)

    report = sys.stderr
    print("# A178 dp codemod - " + ("--check (nothing written)" if arguments.check else "--apply"), file=report)
    for path in changed:
        removed = added = 0
        for line in difflib.unified_diff(original[path].split("\n"), text[path].split("\n"), lineterm="", n=0):
            if line.startswith("-") and not line.startswith("---"):
                removed += 1
            elif line.startswith("+") and not line.startswith("+++"):
                added += 1
        print(f"#   {os.path.relpath(path, root)}: -{removed} +{added}", file=report)
    for path in deleted:
        print(f"#   {os.path.relpath(path, root)}: deleted", file=report)
    print(
        f"# {len(changed)} files changed, {len(deleted)} deleted; rem(n / 16) -> dp(n): {counts['literal']}; "
        f"rem(0) -> dp(0): {counts['zero']}; constant uses -> the constant: {counts['constant use']}; "
        f"size(n) -> dp(4n): {counts['size']}; px-role sites kept: {counts['px-role kept']}",
        file=report,
    )
    made = ", ".join(f"{name} ({os.path.relpath(home, root)})" for name, (home, _n, _e) in sorted(proven.items()))
    print("# constants made const dp: " + (made or "none"), file=report)
    for line in review:
        print("# REVIEW " + line, file=report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
