#!/usr/bin/env python3
"""A178 S3 - kolt's lengths in design pixels: `rem(n / 16)` becomes `dp(n)`.

Run over a PACKAGE root (the directory holding `vilan.toml`); every `.vl` file
under `src/` is scanned, except the package's `generated = "..."` root.

    dp_codemod.py <root> --check     print the unified diff, change nothing
    dp_codemod.py <root> --apply     rewrite the files (and delete the scale)

The rewrites (proposal/length.md section 6; the owner's word on the scale):

  1. `rem(<n> / 16)` -> `dp(<n>)`, negatives and decimals included; the
     qualified `Length::rem(<n> / 16)` -> `Length::dp(<n>)`.
  2. `rem(0)` -> `dp(0)` (and `Length::rem(0)` -> `Length::dp(0)`).
  3. A module-level numeric constant `let <name> = <n>f;` whose EVERY use is
     `rem(<name> / 16)` (comments and import lists aside) becomes
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
`<n> / 16` - the same f64 division `rem(<n> / 16)` performed at the site, so
the text and the content-hashed class names do not move. The one place a `dp`
renders differently is a DOTTED px-role builder (`.border(..)`'s width): a
rewrite landing there is printed as a hazard, so a non-identical sheet has a
named cause.

`dp` is ambient in a css block exactly as `rem` is, so a bare `rem(..)` site
(which compiled, so it was in a block) takes a bare `dp(..)`. A constant's
declaration is outside any block: the file's `std::web::style::prelude` import
gains `dp`, and a file without one is written `style::Length::dp(..)` (the
web prelude's ambient `style` module).

Anything else that divides by 16 - `rem((a + b) / 16)`, `rem(name / 16)` for a
name the tool could not prove - is left as written and printed under REVIEW.

stdlib only. Exit status 0; 1 on a usage error.
"""

from __future__ import annotations

import argparse
import difflib
import os
import re
import sys

NUMBER = r"-?\d+(?:\.\d+)?f?"
SIXTEEN = r"16(?:\.0+)?f?"
# A `rem(` CALL: not a method (`.rem(`), not part of a longer name.
QUALIFIER = r"(?P<qualifier>(?:\w+::)*Length::)?"
CALL_HEAD = r"(?<![\w.:\-])" + QUALIFIER + r"rem\(\s*"
LITERAL_SITE = re.compile(CALL_HEAD + r"(?P<number>" + NUMBER + r")\s*/\s*" + SIXTEEN + r"\s*\)")
ZERO_SITE = re.compile(CALL_HEAD + r"(?P<number>0(?:\.0+)?f?)\s*\)")
NAME_SITE = re.compile(CALL_HEAD + r"(?P<name>[A-Za-z_]\w*)\s*/\s*" + SIXTEEN + r"\s*\)")
ANY_SIXTEEN = re.compile(r"(?<![\w.\-])(?:(?:\w+::)*Length::)?rem\([^;\n]*/\s*" + SIXTEEN)
CONSTANT_DECLARATION = re.compile(r"^(?P<export>export )?let (?P<name>[A-Za-z_]\w*) = (?P<number>" + NUMBER + r");$", re.M)
SIZE_SITE = re.compile(r"(?<![\w.:\-])size\(\s*(?P<number>\d+(?:\.\d+)?)f?\s*\)")
SCALE_DECLARATION = re.compile(r"^(?:export )?const let size = Scale::new\(0\.25f?\);\n", re.M)
SCALE_IMPORT = re.compile(r"^import pkg::lib::scale_step::Scale;\n", re.M)
PX_ROLE_BUILDERS = ("border", "border_top", "border_right", "border_bottom", "border_left")


def strip_comments(line: str) -> str:
    """The line without a `//` comment. Strings are not modelled beyond the
    obvious: a `//` inside a string literal is rare in style code, and a false
    strip only makes the tool MORE conservative (a use it cannot see is a use
    it does not rewrite... except in classification, where it hides one - so
    the classifier below also refuses a name it finds inside a string)."""
    in_string = False
    index = 0
    while index < len(line):
        character = line[index]
        if character == '"' and (index == 0 or line[index - 1] != "\\"):
            in_string = not in_string
        elif not in_string and line.startswith("//", index):
            return line[:index]
        index += 1
    return line


def number_text(number: str) -> str:
    return number[:-1] if number.endswith("f") else number


def quadruple(number: str) -> str:
    value = float(number) * 4
    return str(int(value)) if value == int(value) else repr(value)


def sources(root: str, generated: list[str]) -> list[str]:
    found = []
    for directory, subdirectories, files in os.walk(os.path.join(root, "src")):
        subdirectories.sort()
        relative = os.path.relpath(directory, root)
        if any(relative == g or relative.startswith(g + os.sep) for g in generated):
            subdirectories[:] = []
            continue
        for name in sorted(files):
            if name.endswith(".vl"):
                found.append(os.path.join(directory, name))
    return found


def generated_roots(root: str) -> list[str]:
    try:
        manifest = open(os.path.join(root, "vilan.toml"), encoding="utf-8").read()
    except OSError:
        return []
    roots = []
    for match in re.finditer(r'^generated\s*=\s*(.+)$', manifest, re.M):
        roots += [os.path.normpath(value) for value in re.findall(r'"([^"]+)"', match.group(1))]
    return roots


def import_lists(text: str):
    """Every `import a::b::{ .. };` brace list: (start, end, module path, names)."""
    for match in re.finditer(r"^import (?P<path>[\w:]+)::\{(?P<body>[^}]*)\};", text, re.M):
        names = [name.strip() for name in match.group("body").split(",") if name.strip()]
        yield match.start(), match.end(), match.group("path"), names


def write_import(path: str, names: list[str], multiline: bool) -> str:
    if multiline:
        return "import " + path + "::{\n" + "".join(f"\t{name},\n" for name in names) + "};"
    return "import " + path + "::{ " + ", ".join(names) + " };"


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
        multiline = "\n" in text[start:end]
        replacement = write_import(path, names, multiline) if names else ""
        if not names:
            end = end + 1 if text[end:end + 1] == "\n" else end
        return text[:start] + replacement + text[end:]
    return text


def word_uses(text: str, name: str):
    """(line number, line, column) of each whole-word `name` outside comments."""
    pattern = re.compile(r"(?<![\w.:\-])" + re.escape(name) + r"(?![\w])")
    for number, line in enumerate(text.split("\n"), start=1):
        code = strip_comments(line)
        for match in pattern.finditer(code):
            yield number, line, match.start()


def in_import_list(text: str, line_number: int) -> bool:
    lines = text.split("\n")
    line = lines[line_number - 1]
    if line.startswith("import "):
        return True
    # A line of a multi-line brace list: walk up to its `import` head.
    for back in range(line_number - 2, -1, -1):
        above = lines[back]
        if above.startswith("import ") and "{" in above and "}" not in above:
            return True
        if not above.startswith("\t") or above.strip().endswith(";"):
            return False
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("root")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true", help="print the diff, change nothing")
    mode.add_argument("--apply", action="store_true", help="rewrite the files")
    arguments = parser.parse_args()
    root = os.path.abspath(arguments.root)
    files = sources(root, generated_roots(root))
    original = {path: open(path, encoding="utf-8").read() for path in files}
    text = dict(original)
    review: list[str] = []
    hazards: list[str] = []
    counts = {"literal": 0, "zero": 0, "constant use": 0, "size": 0}

    def where(path: str, line_number: int) -> str:
        return f"{os.path.relpath(path, root)}:{line_number}"

    # --- 3. constants, decided over the whole package before any rewrite ----
    proven: dict[str, tuple[str, str, str]] = {}  # name -> (file, number, export)
    for path, body in original.items():
        for declaration in CONSTANT_DECLARATION.finditer(body):
            name = declaration.group("name")
            other = []
            for other_path, other_body in original.items():
                site_lines = {
                    other_body.count("\n", 0, site.start()) + 1: site
                    for site in NAME_SITE.finditer(other_body)
                    if site.group("name") == name
                }
                for line_number, line, column in word_uses(other_body, name):
                    if other_path == path and line.startswith(declaration.group(0)):
                        continue
                    if in_import_list(other_body, line_number):
                        continue
                    if line_number in site_lines and re.search(
                        CALL_HEAD + re.escape(name) + r"\s*/\s*" + SIXTEEN + r"\s*\)",
                        strip_comments(line),
                    ):
                        uses_on_line = len(list(re.finditer(r"(?<![\w.:\-])" + re.escape(name) + r"(?!\w)", strip_comments(line))))
                        sites_on_line = len(list(re.finditer(CALL_HEAD + re.escape(name) + r"\s*/\s*" + SIXTEEN + r"\s*\)", strip_comments(line))))
                        if uses_on_line == sites_on_line:
                            continue
                    if '"' in line and name in re.sub(r'"[^"]*"', "", line) is False:
                        continue
                    other.append(where(other_path, line_number) + ": " + line.strip())
            rem_uses = sum(
                1
                for other_body in original.values()
                for site in NAME_SITE.finditer(other_body)
                if site.group("name") == name
            )
            if other or rem_uses == 0:
                if rem_uses:
                    review.append(
                        f"constant `{name}` ({where(path, body.count(chr(10), 0, declaration.start()) + 1)}) kept as an f64: "
                        + ("; ".join(other) if other else "no rem(.. / 16) use")
                    )
                continue
            proven[name] = (path, declaration.group("number"), declaration.group("export") or "")

    # --- 4. the scale: which files call `size(..)` meaning the Scale ------
    scale_files: list[str] = []
    scale_home = None
    for path, body in original.items():
        if SCALE_DECLARATION.search(body):
            scale_home = path
    if scale_home is not None:
        home_module = "pkg::" + os.path.relpath(scale_home, os.path.join(root, "src"))[:-3].replace(os.sep, "::")
        scale_files = [scale_home] + [
            path
            for path, body in original.items()
            if path != scale_home
            and any(path_ == home_module and "size" in names for _s, _e, path_, names in import_lists(body))
        ]
        refused = []
        for path in scale_files:
            body = original[path]
            for line_number, line, column in word_uses(body, "size"):
                code = strip_comments(line)
                if in_import_list(body, line_number) or SCALE_DECLARATION.match(line + "\n"):
                    continue
                if SIZE_SITE.match(code, column):
                    continue
                refused.append(where(path, line_number) + ": " + line.strip())
        if refused:
            review.append("the scale is kept: `size` is used other than as `size(<n>)`: " + "; ".join(refused))
            scale_files = []

    # --- the rewrites -----------------------------------------------------------
    for path in files:
        body = text[path]

        def literal(match: re.Match) -> str:
            counts["literal"] += 1
            return (match.group("qualifier") or "").replace("Length::", "Length::") + "dp(" + number_text(match.group("number")) + ")"

        def zero(match: re.Match) -> str:
            counts["zero"] += 1
            return (match.group("qualifier") or "") + "dp(0)"

        def constant(match: re.Match) -> str:
            name = match.group("name")
            if name not in proven or match.group("qualifier"):
                return match.group(0)
            counts["constant use"] += 1
            return name

        body = LITERAL_SITE.sub(literal, body)
        body = ZERO_SITE.sub(zero, body)
        body = NAME_SITE.sub(constant, body)
        if path in scale_files:
            def scaled(match: re.Match) -> str:
                counts["size"] += 1
                return "dp(" + quadruple(match.group("number")) + ")"

            lines = body.split("\n")
            for index, line in enumerate(lines):
                if line.startswith("import ") or SCALE_DECLARATION.match(line + "\n"):
                    continue
                code = strip_comments(line)
                lines[index] = SIZE_SITE.sub(scaled, code) + line[len(code):]
            body = "\n".join(lines)
            if path == scale_home:
                body = SCALE_DECLARATION.sub("", body)
                body = re.sub(r"\n\n\n+", "\n\n", body)
                body = SCALE_IMPORT.sub("", body)
            else:
                body = edit_import(body, home_module, remove="size")
        for name, (home, number, export) in proven.items():
            if home != path:
                continue
            has_prelude = any(p == "std::web::style::prelude" for _s, _e, p, _n in import_lists(body))
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

    # --- hazards and leftovers ----------------------------------------------
    for path in files:
        for number, line in enumerate(text[path].split("\n"), start=1):
            code = strip_comments(line)
            for builder in PX_ROLE_BUILDERS:
                if re.search(r"\." + builder + r"\(\s*(?:style::Length::|Length::)?dp\(", code) and not re.search(
                    r"\." + builder + r"\(\s*(?:style::Length::|Length::)?dp\(", strip_comments(original[path].split("\n")[number - 1] if number <= original[path].count("\n") + 1 else "")
                ):
                    hazards.append(where(path, number) + ": " + line.strip())
            if ANY_SIXTEEN.search(code):
                review.append("left as written: " + where(path, number) + ": " + line.strip())

    deleted = []
    if scale_home is not None and scale_files:
        scale_file = os.path.join(root, "src", "lib", "scale_step.vl")
        still = [p for p in files if p != scale_file and re.search(r"\bscale_step\b|\bScale\b", strip_comments(text[p]))]
        if os.path.exists(scale_file) and not still:
            deleted.append(scale_file)
        elif os.path.exists(scale_file):
            review.append("src/lib/scale_step.vl kept: still named in " + ", ".join(os.path.relpath(p, root) for p in still))

    # --- report ------------------------------------------------------------------
    changed = [path for path in files if text[path] != original[path]]
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
        if arguments.check:
            print(f"--- a/{os.path.relpath(path, root)}\n+++ /dev/null  (deleted)")
        else:
            os.remove(path)

    print("\n# summary", file=sys.stderr)
    for path in changed:
        old = original[path].split("\n")
        new = text[path].split("\n")
        moved = sum(1 for line in difflib.ndiff(old, new) if line[:1] in "-+")
        print(f"#   {os.path.relpath(path, root)}: {moved} lines -/+", file=sys.stderr)
    for path in deleted:
        print(f"#   {os.path.relpath(path, root)}: deleted", file=sys.stderr)
    print(
        f"# {len(changed)} files; rem(n / 16) -> dp(n): {counts['literal']}; rem(0) -> dp(0): {counts['zero']}; "
        f"constant uses: {counts['constant use']}; size(n) -> dp(4n): {counts['size']}",
        file=sys.stderr,
    )
    print("# constants made dp: " + (", ".join(f"{name} ({os.path.relpath(home, root)})" for name, (home, _n, _e) in sorted(proven.items())) or "none"), file=sys.stderr)
    for line in hazards:
        print("# HAZARD (a dp under a px-role builder renders px, not rem): " + line, file=sys.stderr)
    for line in review:
        print("# REVIEW " + line, file=sys.stderr)
    if arguments.check:
        print("# --check: nothing written", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
