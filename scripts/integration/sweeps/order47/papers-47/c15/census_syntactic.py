#!/usr/bin/env python3
"""C15 syntactic census: `mut NAME` locals that a closure (or `async` spawn body)
in the same scope mentions. Heuristic (manual review follows): scope = lines
after the declaration until the enclosing block closes; closure = `|..|` / `||`
in a closure position (after `(`, `,`, `=`, `{`, `return`, `=>`, line start) or
`async {`; body = the brace-matched block, else the rest of the expression.
For each site: W_in = closures that WRITE it (assign/compound/field-assign/
mutating method); R_in = closures that only read; out_after = mentions outside
every closure after the first capture (w = write, r = read);
before = writes between declaration and first capture.
Class: (i) no closure writes AND no write outside after capture
       (ii) exactly one closure writes, no mention outside after capture,
            no other closure mentions it
       (iii) everything else.
Usage: census_syntactic.py FILE... > table
"""
import re, sys
MUTATING = r"(push|pop|insert|remove|clear|extend|sort|sort_by|retain|truncate|append|take|replace|drain|swap|set|write|reverse|push_str|shift|unshift|splice|dedup|fill|resize|delete|add|get_or_insert|entry)"
READONLY = {"len","is_empty","get","contains","contains_key","clone","map","iter","read","identity","to_string","starts_with","ends_with","as_i32","as_usize","keys","values","is_some","is_none","unwrap","unwrap_or","find","filter","any","all","first","last","join","split","trim","slice","index_of","eq","cmp","hash","copy","downgrade","upgrade","borrow","result"}
def closures(text):
    """yield (start, end) char spans of closure bodies (including params)."""
    spans = []
    i = 0
    n = len(text)
    pat = re.compile(r"(?:(?<=[(,={\[])|(?<=return)|(?<==>)|(?<=^)|(?<=\n)|(?<=[(,={\[]\s)|(?<=\s\s)|(?<=\t))\s*(\|[^|\n]*\||\|\||async\s*(?=\{))", re.M)
    for m in pat.finditer(text):
        s = m.start(1)
        # reject logical-or: previous non-space char an identifier char or ')' or ']'
        k = s - 1
        while k >= 0 and text[k] in " \t":
            k -= 1
        prev = text[k] if k >= 0 else "\n"
        word = re.search(r"(\w+)\s*$", text[:s])
        if (prev.isalnum() or prev in ")]_\"'") and not (word and word.group(1) in ("return", "async")):
            continue
        j = m.end(1)
        while j < n and text[j] in " \t":
            j += 1
        # optional return annotation `: T` before `{`
        if j < n and text[j] == ":":
            b = text.find("{", j)
            j = b if b != -1 else j
        if j < n and text[j] == "{":
            depth = 0
            e = j
            while e < n:
                if text[e] == "{": depth += 1
                elif text[e] == "}":
                    depth -= 1
                    if depth == 0: break
                e += 1
            spans.append((s, e + 1))
        else:
            depth = 0
            e = j
            while e < n:
                c = text[e]
                if c in "([{": depth += 1
                elif c in ")]}":
                    if depth == 0: break
                    depth -= 1
                elif (c == "," or c == "\n" or c == ";") and depth == 0: break
                e += 1
            spans.append((s, e))
    return spans

def inside(pos, spans):
    return [sp for sp in spans if sp[0] <= pos < sp[1]]

def is_write(text, pos, name):
    after = text[pos + len(name):pos + len(name) + 60]
    if re.match(r"\s*(=(?!=)|\+=|-=|\*=|/=|%=|\|=|&=)", after): return True
    if re.match(r"(\.\w+|\[[^\]]*\])+\s*(=(?!=)|\+=|-=|\*=|/=)", after): return True
    if re.match(r"\." + MUTATING + r"\(", after): return True
    # any other method call: unknown receiver mode -> counted as a WRITE unless
    # it is a known read-only method (conservative; reviewed by hand)
    m = re.match(r"\.(\w+)\(", after)
    if m and m.group(1) not in READONLY: return True
    return False

def scope_end(text, decl_pos):
    # enclosing block closes where brace depth drops below the declaration's
    depth = 0
    for e in range(decl_pos, len(text)):
        c = text[e]
        if c == "{": depth += 1
        elif c == "}":
            if depth == 0: return e
            depth -= 1
    return len(text)

def lineno(text, pos): return text.count("\n", 0, pos) + 1

rows = []
for path in sys.argv[1:]:
    text = open(path).read()
    # strip // comments (keep offsets)
    text = re.sub(r"//[^\n]*", lambda m: " " * len(m.group(0)), text)
    spans = closures(text)
    for m in re.finditer(r"^[ \t]+mut\s+(\w+)\b", text, re.M):
        name = m.group(1)
        if name == "self": continue
        start = m.end()
        end = scope_end(text, start)
        # the declaration's own initializer might contain a closure; skip to end of line
        occ = [o.start() for o in re.finditer(r"(?<![\w.])" + re.escape(name) + r"\b(?!\s*:(?!:))", text[start:end])]
        occ = [start + o for o in occ]
        # shadowing: stop at a re-declaration of the name
        cut = re.search(r"(?:let|mut)\s+" + re.escape(name) + r"\b", text[start:end])
        if cut:
            occ = [o for o in occ if o < start + cut.start()]
        caps = {}
        first_cap = None
        for o in occ:
            ins = [sp for sp in inside(o, spans) if sp[0] > m.start()]
            if ins:
                sp = min(ins, key=lambda s: s[0])  # outermost closure after decl
                caps.setdefault(sp, []).append(o)
                first_cap = o if first_cap is None else min(first_cap, sp[0])
        if not caps: continue
        writers = [sp for sp, os in caps.items() if any(is_write(text, o, name) for o in os)]
        readers = [sp for sp in caps if sp not in writers]
        outside = [o for o in occ if not [sp for sp in inside(o, spans) if sp[0] > m.start()]]
        before_w = [o for o in outside if o < first_cap and is_write(text, o, name)]
        after = [o for o in outside if o > first_cap]
        after_w = [o for o in after if is_write(text, o, name)]
        if not writers and not after_w:
            cls = "i"
        elif len(writers) == 1 and not readers and not after:
            cls = "ii"
        else:
            cls = "iii"
        rows.append((path, lineno(text, m.start()), name, cls, len(writers), len(readers),
                     len(after) - len(after_w), len(after_w), len(before_w),
                     [lineno(text, sp[0]) for sp in caps]))
print("file:line\tname\tclass\tW_closures\tR_closures\tread_after\twrite_after\twrite_before\tclosure_lines")
for r in rows:
    print(f"{r[0]}:{r[1]}\t{r[2]}\t{r[3]}\t{r[4]}\t{r[5]}\t{r[6]}\t{r[7]}\t{r[8]}\t{r[9]}")
from collections import Counter
c = Counter(r[3] for r in rows)
print(f"# sites {len(rows)}  i={c['i']} ii={c['ii']} iii={c['iii']}", file=sys.stderr)
