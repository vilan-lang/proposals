#!/usr/bin/env python3
"""usage: count_lines.py FILE [START END]  -- non-blank, non-comment (// or ///) lines in 1-based inclusive range"""
import sys
def count(path, a=1, b=None):
    n = 0
    for i, l in enumerate(open(path, encoding="utf-8"), 1):
        if i < a or (b is not None and i > b): continue
        s = l.strip()
        if not s or s.startswith("//"): continue
        n += 1
    return n
if __name__ == "__main__":
    p = sys.argv[1]
    a = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    b = int(sys.argv[3]) if len(sys.argv) > 3 else None
    print(count(p, a, b))
