#!/usr/bin/env python3
"""fold_tests_by_name.py <file> <base-rev> <lane-ref> [--allow-edit a,b]
Resolve a conflicted Rust test file as HEAD's copy plus the lane's NEW top-level `fn`s appended
whole (brace-matched, with their preceding `#[…]`/`//` lines). Refuses if the lane changed an
existing fn OR an existing top-level const/static relative to <base-rev> unless it is named in
--allow-edit (then the lane's version replaces HEAD's). Whitespace-insensitive comparison. Test
MODULES (`mod x { … }`) are NOT handled — resolve those as the merged prefix plus each original's
tail located by an anchor.

N81 (Order 36) fixed three shapes this tool got wrong:
  * a MULTI-LINE STRING CONST whose first line ends in `"\\` (a Rust line continuation). Its body
    lines sit at column 0 and spell `struct`/`impl`/`fn`/`//` there, so the item scanner read them
    as item starts: the const was truncated to its first line and its 32-line body vanished
    (visibility-a-35's merge, lexer errors at the gate's build). Every item start is now taken only
    on a line that BEGINS outside a string literal or comment (`code_line_starts`).
  * a test HEAD RENAMED: a fn in BASE and in the lane but gone from HEAD was appended as "new" and
    resurrected under its old name. A name present in BASE is never new; it was deleted or renamed
    on HEAD and stays gone (reported).
  * an EDITED existing const: the fold carried NEW consts only, so a lane's edit to a program const
    beside its pin was dropped silently. An edited const is refused like an edited fn, and taken
    from the lane when --allow-edit names it.
"""
import re, subprocess, sys
path, base_rev, lane = sys.argv[1:4]
allow = set(sys.argv[sys.argv.index("--allow-edit") + 1].split(",")) if "--allow-edit" in sys.argv else set()
def show(ref): return subprocess.run(["git", "show", f"{ref}:{path}"], capture_output=True, text=True).stdout

def code_line_starts(lines):
    """For each line, whether it BEGINS outside a string literal or a block comment — the only
    lines a column-0 item regex may be trusted on.

    A Rust string literal SPANS LINES: a raw newline is part of it, and a `\\` before the newline
    only swallows the break and the next line's indentation. So `const X: &str = "\\` carries
    program text at column 0 for as many lines as it likes, and that text spells `struct`, `impl`,
    `fn`, `//` and `#[` exactly as Rust does; a `&format!("…` fixture with its vilan program
    written out over twenty lines is the same shape without the backslash. Raw strings (`r#"…"#`,
    any hash depth) are the third. The state is carried across lines so none of the three is read
    as code. `//` is tested BEFORE `"`, so a quote or an apostrophe in a comment opens nothing —
    the one thing that could make the scan run away."""
    out, state, hashes = [], None, 0
    for line in lines:
        out.append(state is None)
        i = 0
        while i < len(line):
            c = line[i]
            if state is None:
                m = re.match(r'r(#*)"', line[i:])
                if m: state, hashes = "raw", len(m.group(1)); i += m.end(); continue
                if line.startswith("//", i): break          # a line comment: the rest is prose
                if line.startswith("/*", i): state = "block"; i += 2; continue
                if c == '"': state = "str"; i += 1; continue
                if c == "'" and i + 2 < len(line) and line[i + 2] == "'": i += 3; continue
                i += 1
            elif state == "str":
                if c == "\\": i += 2; continue
                if c == '"': state = None
                i += 1
            elif state == "block":
                if line.startswith("*/", i): state = None; i += 2; continue
                i += 1
            else:
                if line.startswith('"' + "#" * hashes, i): state = None; i += 1 + hashes; continue
                i += 1
    return out

def fns(src):
    lines = src.split("\n"); code = code_line_starts(lines); res = {}; n = 0
    while n < len(lines):
        m = re.match(r"^(pub(\(crate\))? )?(async )?fn ([A-Za-z_][A-Za-z0-9_]*)", lines[n]) if code[n] else None
        if m:
            name, start = m.group(4), n
            # The header above a fn: attributes and comments back to the previous blank line or item end —
            # a MULTI-LINE `#[ignore = "…"]` has continuation lines that start with neither `#[` nor `//`
            # (Order 29, rule1-29: a pin lost its `#[test]` at the fold and clippy called it unused).
            i = n - 1
            while i >= 0 and lines[i].strip() != "" and not lines[i].startswith("}") and not re.match(r"^(pub(\(crate\))? )?(async )?fn ", lines[i]): i -= 1
            block = i + 1
            while block < n and not (lines[block].startswith("#[") or lines[block].startswith("//")): block += 1
            start = block
            # Brace depth counted OUTSIDE string literals: a pin's raw-string vilan program can hold an
            # unbalanced brace (Order 29, smalls-29: one such pin made its fn run to EOF and every lane
            # that appended to the file read as "edited it").
            depth, end, seen, state, hashes = 0, n, False, None, 0
            while end < len(lines):
                line, i = lines[end], 0
                while i < len(line):
                    c = line[i]
                    if state is None:
                        # N81: `//` before `"` — a comment holding a quote or an apostrophe used
                        # to open a string here that nothing closed, and the fn then ran to EOF.
                        if line.startswith("//", i): break
                        m2 = re.match(r'r(#*)"', line[i:])
                        if m2: state, hashes = "raw", len(m2.group(1)); i += m2.end(); continue
                        if c == '"': state = "str"; i += 1; continue
                        if c == "'" and i + 2 < len(line) and line[i+2] == "'": i += 3; continue
                        if c == "{": depth += 1; seen = True
                        elif c == "}": depth -= 1
                        i += 1
                    elif state == "str":
                        if c == "\\": i += 2; continue
                        if c == '"': state = None
                        i += 1
                    else:
                        if line.startswith('"' + "#" * hashes, i): state = None; i += 1 + hashes; continue
                        i += 1
                if seen and depth == 0 and state is None: break
                end += 1
            res[name] = (start, end, "\n".join(lines[start:end+1])); n = end + 1
        else: n += 1
    return res

# the lane's top-level consts/statics (fixtures its fns read), by item boundary
_start = re.compile(r"^(pub(\(crate\))? )?(const|static|fn|async fn|use|mod|struct|enum|impl|type|macro_rules!|#\[|///|//)")
def top_consts(src):
    ls = src.split("\n"); code = code_line_starts(ls)
    starts = [i for i, l in enumerate(ls) if code[i] and _start.match(l)]; out = {}
    for k, i in enumerate(starts):
        m = re.match(r"^(pub(\(crate\))? )?(const|static) ([A-Za-z_][A-Za-z0-9_]*)", ls[i])
        if not m: continue
        end = starts[k + 1] if k + 1 < len(starts) else len(ls); s0 = i
        while s0 > 0 and (ls[s0-1].startswith("///") or ls[s0-1].startswith("#[")): s0 -= 1
        out[m.group(4)] = "\n".join(ls[s0:end]).rstrip("\n")
    return out

def norm(t): return re.sub(r"\s+", "", t)
head, base, lane_src = show("HEAD"), show(base_rev), show(lane)
hf, bf, lf = fns(head), fns(base), fns(lane_src)
hc, bc, lc = top_consts(head), top_consts(base), top_consts(lane_src)
changed = [n for n in lf if n in bf and norm(lf[n][2]) != norm(bf[n][2]) and n not in allow]
# N81: an edited CONST is refused exactly as an edited fn is. It used to be dropped in silence —
# the fold carried new consts only — so a lane's edit to a program const beside its pin reached
# `next` as HEAD's old text under the lane's new pin.
changed_consts = [n for n in lc if n in bc and norm(lc[n]) != norm(bc[n]) and n not in allow]
if changed or changed_consts:
    print(f"REFUSED: the lane edited existing fns: {changed}; consts: {changed_consts} "
          f"(pass --allow-edit a,b to take the lane's version)"); sys.exit(1)
# N81: a fn in the BASE but not in HEAD was DELETED or RENAMED on HEAD. It is not new, and
# appending it resurrects a head under its old name (the Order 35 find).
resurrected = [n for n in lf if n not in hf and n in bf]
new = [n for n in lf if n not in hf and n not in bf]
# functions the lane DELETED (in the base, not in the lane) are removed from HEAD's copy too
deleted = [n for n in bf if n not in lf and n in hf]
head_text = head
for n in deleted:
    head_text = head_text.replace(hf[n][2] + "\n", "", 1).replace(hf[n][2], "", 1); print(f"dropped the lane-deleted {n}")
for n in allow:
    if n in hf and n in lf: head_text = head_text.replace(hf[n][2], lf[n][2], 1); print(f"took the lane's {n}")
    elif n in hc and n in lc: head_text = head_text.replace(hc[n], lc[n], 1); print(f"took the lane's const {n}")
appended = "\n\n".join(lf[n][2] for n in new)
carried = {k: v for k, v in lc.items() if k not in hc and k not in bc}
if carried:
    hl = head_text.split("\n")
    code = code_line_starts(hl)
    # N81: the insertion point is the END of the last top-level `use` ITEM, not the last line
    # that merely STARTS with `use `. `use vilan_core::{` opens a multi-line item, and inserting
    # after that line put the carried consts INSIDE the brace list — the visibility-a-35 merge
    # shipped a file whose header lines had moved into a `use { }` block, and the build failed in
    # the lexer rather than anywhere that named the fold.
    last_use = 0
    for i, line in enumerate(hl):
        if code[i] and re.match(r"^(pub(\(crate\))? )?use ", line):
            end = i
            while end < len(hl) - 1 and not hl[end].rstrip().endswith(";"): end += 1
            last_use = end
    hl[last_use+1:last_use+1] = [""] + list(carried.values())
    head_text = "\n".join(hl); print(f"carried top-level consts: {sorted(carried)}")
if resurrected: print(f"NOT resurrected (deleted or renamed on HEAD): {sorted(resurrected)}")
open(path, "w").write(head_text.rstrip("\n") + ("\n\n" + appended + "\n" if appended else "\n"))
print(f"folded {path}: head_fns={len(hf)} lane_new={len(new)} {new}")
