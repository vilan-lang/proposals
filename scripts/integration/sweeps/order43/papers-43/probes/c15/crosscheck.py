#!/usr/bin/env python3
"""Crude cross-check for census_syntactic.py: a `mut NAME` local whose scope
has a line where NAME follows a `|` on the same line, or a line inside a block
opened by a line containing `|..| {`, `|| {` or `async {`. Prints candidates."""
import re, sys
for path in sys.argv[1:]:
    lines = open(path).read().split("\n")
    for i, line in enumerate(lines):
        m = re.match(r"^(\s+)mut\s+(\w+)\b", line)
        if not m or m.group(2) == "self": continue
        ind, name = len(m.group(1)), m.group(2)
        opener_ind = None
        for j in range(i + 1, len(lines)):
            l = lines[j]
            s = l.lstrip("\t ")
            cur = len(l) - len(s)
            if s.startswith("}") and cur < ind: break
            code = l.split("//")[0]
            if re.search(r"(\|[^|]*\||\|\||async)\s*\{\s*$", code):
                if opener_ind is None: opener_ind = cur
            elif opener_ind is not None and cur <= opener_ind and s.startswith("}"):
                opener_ind = None
            hit = re.search(r"\|[^|]*\|[^\n]*(?<![\w.])" + name + r"\b", code) or (opener_ind is not None and cur > opener_ind and re.search(r"(?<![\w.])" + name + r"\b", code))
            if hit:
                print(f"{path}:{i+1}\t{name}\tfirst-hit {j+1}")
                break
