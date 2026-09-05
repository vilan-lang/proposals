#!/usr/bin/env bash
# seal.sh — the pre-seal verdict on the integration tip: union, clippy, the Windows cross-check,
# audit, fmt, changelog parity. Logs beside this script. CI green on the tip is still the last word.
set -u
S=$(cd "$(dirname "$0")" && pwd)
W=${VILAN_INTEGRATION:-$HOME/code/vilan-lang/vilan/.claude/worktrees/integration}
cd "$W" || exit 1
tip=$(git rev-parse --short=8 HEAD); echo "tip=$tip loadavg=$(cut -d' ' -f1-3 /proc/loadavg)"
cargo nextest run --workspace > "$S/suite-$tip.log" 2>&1; u=$?; grep -E '^\s+Summary' "$S/suite-$tip.log" | tail -1; echo "union exit=$u"
cargo clippy --workspace --all-targets -- -D warnings > "$S/clippy-$tip.log" 2>&1; c=$?; echo "clippy exit=$c"
cargo check --target x86_64-pc-windows-msvc -p vilan-cli -p vilan-core -p vilan-lsp --tests > "$S/win-$tip.log" 2>&1; w=$?; echo "windows exit=$w"
cargo audit --deny unsound > "$S/audit-$tip.log" 2>&1; a=$?; echo "audit exit=$a"
cargo fmt --all --check > "$S/fmt-$tip.log" 2>&1; f=$?; echo "fmt exit=$f"
python3 - "$W/CHANGELOG.md" <<'PY'
import sys
ls = open(sys.argv[1]).read().split("\n")
s = next(i for i, l in enumerate(ls) if l.startswith("## Unreleased"))
e = next((i for i in range(s + 1, len(ls)) if ls[i].startswith("## ")), len(ls))
print("changelog parity", sum(l.startswith("<!-- family:") for l in ls[s:e]), "/", sum(l.startswith("**") for l in ls[s:e]))
PY
echo "verdict: union=$u clippy=$c windows=$w audit=$a fmt=$f"
