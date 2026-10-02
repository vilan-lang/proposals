#!/usr/bin/env python3
"""gen_slope.py OUTDIR MODULES — performance-gates.md §6's probe: a generated node package of
MODULES modules (~100 lines each: structs with derives, an Option match, a list loop, arithmetic),
one entry importing all of them. Two sizes give the MARGINAL cost of 1,000 lines over the fixed
cost of the std reach. Plain code only: no views, no styles, no reactive — a floor, not kolt."""
import os, sys

out, modules = sys.argv[1], int(sys.argv[2])
os.makedirs(os.path.join(out, "src"), exist_ok=True)
open(os.path.join(out, "vilan.toml"), "w").write('[package]\nname = "slope"\n\n[entry.main]\n')
for m in range(modules):
    lines = ["import std::range::Range;", "", "export *;", ""]
    for k in range(6):
        lines += [
            "[derive(PartialEq, Debug)]",
            f"struct Item{m}_{k} {{ id: i32, name: str, weight: i32 }}",
            "",
            f"fun make{m}_{k}(id: i32): Item{m}_{k} {{",
            f"\tItem{m}_{k} {{ id, name = \"item\", weight = id * {k + 1} }}",
            "}",
            "",
            f"fun pick{m}_{k}(items: List<Item{m}_{k}>, wanted: i32): Option<i32> {{",
            "\tmut found = None;",
            "\tfor item in items {",
            "\t\tif item.id == wanted { found = Some(item.weight); }",
            "\t}",
            "\tfound",
            "}",
            "",
            f"fun score{m}_{k}(n: i32): i32 {{",
            f"\tmut items: List<Item{m}_{k}> = [];",
            f"\tfor i in Range::new(0, n) {{ items.push(make{m}_{k}(i)); }}",
            f"\tmatch pick{m}_{k}(items, n / 2) {{",
            "\t\tSome(let w) => w + 1,",
            "\t\tNone => 0,",
            "\t}",
            "}",
            "",
        ]
    lines += [f"fun total{m}(n: i32): i32 {{", "\t" + " + ".join(f"score{m}_{k}(n)" for k in range(6)), "}", ""]
    open(os.path.join(out, "src", f"m{m}.vl"), "w").write("\n".join(lines))
main = [f"import pkg::m{m}::total{m};" for m in range(modules)]
main += ["", "fun main() {", "\tmut sum = 0;"] + [f"\tsum = sum + total{m}(3);" for m in range(modules)] + ["\tprint(sum);", "}", ""]
open(os.path.join(out, "src", "main.vl"), "w").write("\n".join(main))
