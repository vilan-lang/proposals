#!/usr/bin/env python3
"""B485 marker census: every declaration marker's site count over std,
macro_std, examples and kolt, plus the ORDER stacked markers appear in.

Usage: census.py <vilan-tree> <kolt-root>   (vilan-tree = the repo's `vilan/` dir)

Strips `//` comments and "..." strings (vilan has no block comments), then
counts by regex. Approximate by construction: it is a lexer-free count, so a
marker spelled inside a css block or a macro body's source span counts too.
The counts are what the migration-cost table in keywords-vs-attributes.md
cites; re-run to refresh.
"""
import os
import re
import sys
from collections import Counter, defaultdict

tree, kolt = sys.argv[1], sys.argv[2]
CORPORA = {
    "std": [os.path.join(tree, "std/src"), os.path.join(tree, "macro_std")],
    "examples": [os.path.join(tree, "examples")],
    "kolt": [os.path.join(kolt, "src")],
}
SKIP = ("/dist/", "/node_modules/", "/target/", "/worktrees/")


def files(roots):
    for root in roots:
        for dirpath, _, names in os.walk(root):
            if any(s in os.path.relpath(dirpath, root) .join("//") for s in SKIP):
                continue
            for n in names:
                if n.endswith(".vl"):
                    yield os.path.join(dirpath, n)


STRING = re.compile(r'"(?:\\.|[^"\\])*"')


def strip(src):
    out = []
    for line in src.split("\n"):
        line = STRING.sub('""', line)
        i = line.find("//")
        if i >= 0:
            line = line[:i]
        out.append(line)
    return out


# (label, regex) — counted per occurrence
KEYWORD_SITES = [
    ("export <decl>", r"\bexport\s+(?!\*|\(|import\b|\[)"),
    ("export [attr] <decl>", r"\bexport\s+\["),
    ("export import (re-export)", r"\bexport\s+import\b"),
    ("export(in ..)", r"\bexport\s*\(\s*in\b"),
    ("export *;", r"\bexport\s+\*\s*;"),
    ("external fun", r"\bexternal\s+fun\b"),
    ("external struct", r"\bexternal\s+struct\b"),
    ("async fun / async external", r"\basync\s+(fun|external)\b"),
    ("async (expr / closure type)", r"\basync\b(?!\s+(fun|external)\b)"),
    ("const let", r"\bconst\s+let\b"),
    ("const fun", r"\bconst\s+fun\b"),
    ("const <expr>", r"\bconst\b(?!\s+(let|fun)\b)"),
    ("macro fun", r"\bmacro\s+fun\b"),
    ("macro <invocation/block>", r"\bmacro\b(?!\s+fun\b)"),
    ("mut binding (statement head)", r"^\s*(export\s+)?mut\s+[A-Za-z_(]"),
    ("&mut", r"&mut\b"),
    ("own <param>", r"\bown\s+(self\b|[a-z_]\w*\s*:)"),
    ("lazy let", r"\blazy\s+(let|mut)\b"),
    ("lazy <param>", r"\blazy\s+[a-z_]\w*\s*:"),
    ("dyn <Trait>", r"\bdyn\s+[A-Z]"),
    ("borrows", r"\bborrows\s+[a-z_]\w*"),
    ("context <clause>", r"[)>\]a-zA-Z0-9]\s+context\s+[a-z_]"),
    ("sync (closure type)", r"\(\s*sync\s*\|"),
    ("[platform] mod self;", r"\]\s*mod\s+self\s*;"),
]

ATTR = re.compile(r"\[\s*([a-z_]\w*)\s*[\](]")
DECL_HEAD = re.compile(
    r"^\s*((?:(?:export(?:\s*\(\s*in\s+[^)]*\))?|async|external|const|macro|lazy|pub)\s+|\[[^\[\]]*(?:\([^()]*\))?[^\[\]]*\]\s*)+)"
    r"(fun|struct|enum|trait|impl|let|mut|mod|import|type)\b"
)
HEAD_TOKEN = re.compile(r"export(?:\s*\(\s*in\s+[^)]*\))?|async|external|const|macro|lazy|\[\s*([a-z_]\w*)[^\]]*\]")

counts = defaultdict(Counter)
attrs = defaultdict(Counter)
orders = defaultdict(Counter)
order_examples = {}
nfiles = Counter()

for corpus, roots in CORPORA.items():
    for path in files(roots):
        nfiles[corpus] += 1
        with open(path, encoding="utf-8") as fh:
            lines = strip(fh.read())
        text = "\n".join(lines)
        # A head written across lines (`[must_use]` on its own line above the
        # `fun`) is joined onto the line below it, so the attribute and the
        # order counts see the whole head.
        joined = []
        carry = ""
        for line in lines:
            if re.match(r"^\s*(export\s+)?(\[[^\[\]]*(?:\([^()]*\))?[^\[\]]*\]\s*)+$", line):
                carry += line.strip() + " "
                continue
            joined.append((carry + line.strip()) if carry else line)
            carry = ""
        lines = joined
        for label, rx in KEYWORD_SITES:
            counts[corpus][label] += len(re.findall(rx, text, re.M))
        # Attributes: a `[name` that opens a line (after optional `export`),
        # or follows another attribute's `]` on the same head.
        for line in lines:
            m = re.match(r"^\s*(export\s+)?((?:\[[^\[\]]*(?:\([^()]*\))?[^\[\]]*\]\s*)+)", line)
            if not m:
                continue
            # skip array literals / index expressions: the run must be followed
            # by a declaration word, `export`, end of line (stacked across
            # lines), or a field name `name:`
            rest = line[m.end():]
            if not re.match(r"^(export\b|async\b|external\b|fun\b|struct\b|enum\b|trait\b|impl\b|let\b|mut\b|lazy\b|mod\b|import\b|[a-z_]\w*\s*:|[A-Z]\w*\s*[,(=]|[A-Z]\w*\s*$|\s*$)", rest):
                continue
            for a in ATTR.findall(m.group(2)):
                attrs[corpus][a] += 1
        # Stacked-marker order on one-line declaration heads.
        for line in lines:
            m = DECL_HEAD.match(line)
            if not m:
                continue
            seq = []
            for t in HEAD_TOKEN.finditer(m.group(1)):
                if t.group(1):
                    seq.append("[" + t.group(1) + "]")
                elif t.group(0).startswith("export"):
                    seq.append("export")
                else:
                    seq.append(t.group(0))
            if len(seq) < 2:
                continue
            key = " ".join(seq) + " " + m.group(2)
            orders[corpus][key] += 1
            order_examples.setdefault(key, f"{os.path.relpath(path, os.path.dirname(roots[0]))}: {line.strip()[:110]}")

corpora = list(CORPORA)
print("files:", ", ".join(f"{c} {nfiles[c]}" for c in corpora))
print()
print("## Keyword sites")
print("| marker | " + " | ".join(corpora) + " | total |")
print("|---|" + "---:|" * (len(corpora) + 1))
for label, _ in KEYWORD_SITES:
    row = [counts[c][label] for c in corpora]
    print(f"| `{label}` | " + " | ".join(map(str, row)) + f" | {sum(row)} |")
print()
print("## Attribute sites (declaration and field heads)")
names = sorted({a for c in corpora for a in attrs[c]}, key=lambda a: -sum(attrs[c][a] for c in corpora))
print("| attribute | " + " | ".join(corpora) + " | total |")
print("|---|" + "---:|" * (len(corpora) + 1))
for a in names:
    row = [attrs[c][a] for c in corpora]
    print(f"| `[{a}]` | " + " | ".join(map(str, row)) + f" | {sum(row)} |")
print()
print("## Stacked-marker orders (one-line heads with two or more markers)")
keys = sorted({k for c in corpora for k in orders[c]}, key=lambda k: -sum(orders[c][k] for c in corpora))
print("| order | " + " | ".join(corpora) + " | total | first site |")
print("|---|" + "---:|" * (len(corpora) + 1) + "---|")
for k in keys:
    row = [orders[c][k] for c in corpora]
    print(f"| `{k}` | " + " | ".join(map(str, row)) + f" | {sum(row)} | `{order_examples[k]}` |")
