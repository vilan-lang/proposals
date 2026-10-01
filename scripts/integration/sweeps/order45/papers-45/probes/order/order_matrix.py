#!/usr/bin/env python3
"""B445 / B485 §6: which ORDERS of two stacked markers the parser accepts today.

For each declaration kind, every ordered pair (A, B) of markers that may both
sit on it is written as `A B <decl>` in its own file and checked with the
installed `vilan check`. A pair is OK when the file checks clean, PARSE when
the first error is a parse error ("expected", "found", "cannot find '<attr>'"),
and RULE for a refusal with its own message (printed so a semantic refusal is not mistaken for
an ordering one).

Usage: order_matrix.py <scratch-dir>   (prints a markdown table per kind)
"""
import itertools
import os
import subprocess
import sys

scratch = sys.argv[1]
os.makedirs(scratch, exist_ok=True)

KINDS = {
    "fun (with body)": (
        ["export", '[deprecated("use g")]', '[internal("why")]', "[must_use]", '[platform("browser")]', "async"],
        "fun f(): i32 { 1 }",
        "",
    ),
    "struct": (
        ["export", "[derive(PartialEq)]", '[deprecated("use T")]', '[internal("why")]', '[platform("browser")]', "[resource]"],
        "struct S { a: i32 }",
        "",
    ),
    "trait": (
        ["export", "[resource]", '[deprecated("use U")]', '[internal("why")]', '[platform("browser")]'],
        "trait T { fun t(self): i32; }",
        "",
    ),
    "impl": (
        ["export", '[platform("browser")]', '[internal("why")]'],
        "impl S { fun s(self): i32 { 1 } }",
        "struct S { a: i32 }\n",
    ),
    "module let": (
        ["export", '[deprecated("use y")]', '[internal("why")]', "lazy"],
        "let x = 1;",
        "",
    ),
}


def first_error(path):
    out = subprocess.run(["vilan", "check", path], capture_output=True, text=True)
    text = out.stdout + out.stderr
    for line in text.splitlines():
        if line.startswith("Error:"):
            return out.returncode, line[len("Error: "):].strip()
    return out.returncode, ""


def classify(code, msg):
    if code == 0 and not msg:
        return "OK"
    low = msg.lower()
    if low.startswith("expected") or "found" in low or low.startswith("cannot find '") or "unexpected" in low:
        return "PARSE"
    return "RULE"


for kind, (markers, decl, prelude) in KINDS.items():
    print(f"### {kind}: `{decl}`")
    print()
    print("| first \\ second | " + " | ".join(f"`{m}`" for m in markers) + " |")
    print("|---|" + "---|" * len(markers))
    notes = []
    for a in markers:
        cells = []
        for b in markers:
            if a == b:
                cells.append("—")
                continue
            # an `external fun`/`external struct` needs `external` somewhere;
            # when neither marker of the pair is it, append it in its place
            # (immediately before the declaration word) so the pair is legal.
            tail = decl
            src = f"{prelude}{a} {b} {tail}\nfun main() {{}}\n"
            name = f"{kind.replace(' ', '_').replace('(', '').replace(')', '')}__{markers.index(a)}_{markers.index(b)}.vl"
            path = os.path.join(scratch, name)
            with open(path, "w") as fh:
                fh.write(src)
            code, msg = first_error(path)
            c = classify(code, msg)
            cells.append(c)
            if c != "OK":
                notes.append(f"- `{a} {b} {tail}` — {c}: {msg[:140]}")
        print(f"| `{a}` | " + " | ".join(cells) + " |")
    print()
    if notes:
        print("<details><summary>first errors</summary>\n")
        print("\n".join(notes))
        print("\n</details>\n")


# The full canonical stack per kind (the production order), then every
# ADJACENT swap of it. The canonical stack must check clean; each swap shows
# whether that one inversion is accepted, refused as a parse error, or refused
# with its own message.
FULL = {
    "external fun": ["export", '[deprecated("use g")]', '[internal("why")]', '[extern("f")]', "[must_use]", '[platform("node")]', "async", "external"],
    "fun": ["export", '[deprecated("use g")]', '[internal("why")]', "[must_use]", '[platform("node")]', "async"],
    "external struct": ["export", '[deprecated("use T")]', '[internal("why")]', '[platform("node")]', "[resource]", "external"],
    "derived struct": ["export", "[derive(PartialEq)]", '[deprecated("use T")]', '[internal("why")]', '[platform("node")]', "[resource]"],
    "trait": ["export", '[deprecated("use U")]', '[internal("why")]', '[platform("node")]', "[resource]"],
    "module let": ["export", '[deprecated("use y")]', '[internal("why")]', "lazy"],
}
TAILS = {
    "external fun": "fun f(): i32;",
    "fun": "fun f(): i32 { 1 }",
    "external struct": "struct H;",
    "derived struct": "struct S { a: i32 }",
    "trait": "trait T { fun t(self): i32; }",
    "module let": "let x = 1;",
}
print("### Adjacent swaps of the full canonical stack")
print()
print("| kind | canonical stack | result | each adjacent swap |")
print("|---|---|---|---|")
for kind, stack in FULL.items():
    tail = TAILS[kind]
    path = os.path.join(scratch, f"full_{kind.replace(' ', '_')}.vl")
    with open(path, "w") as fh:
        fh.write(" ".join(stack) + " " + tail + "\nfun main() {}\n")
    code, msg = first_error(path)
    base = classify(code, msg) + (f" ({msg[:80]})" if msg else "")
    swaps = []
    for i in range(len(stack) - 1):
        s2 = stack[:]
        s2[i], s2[i + 1] = s2[i + 1], s2[i]
        p2 = os.path.join(scratch, f"swap_{kind.replace(' ', '_')}_{i}.vl")
        with open(p2, "w") as fh:
            fh.write(" ".join(s2) + " " + tail + "\nfun main() {}\n")
        c2, m2 = first_error(p2)
        swaps.append(f"`{s2[i]}`↔`{s2[i + 1]}`: {classify(c2, m2)}" + (f" — {m2[:90]}" if m2 else ""))
    print(f"| {kind} | `{' '.join(stack)} {tail}` | {base} | " + "<br>".join(swaps) + " |")
