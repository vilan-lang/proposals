#!/usr/bin/env bash
# sweep28.sh <tip> <union> <parity> <ci-verdict> <m19tip> <cptip> <l19tip> — Order 28's close sweep + chronicle seal record, one proposals commit
set -u
S=$(cd "$(dirname "$0")" && pwd); I=$(cd "$S/../.." && pwd)
P=$HOME/code/vilan-lang/proposals
cd "$P" || exit 1
python3 "$I/close_batch.py" "$S/closes28.json" --check && python3 "$I/file_items.py" "$S/newitems28.json" --check && python3 "$S/edit28.py" --check || { echo "VALIDATION FAILED — nothing mutated"; exit 2; }
python3 "$I/close_batch.py" "$S/closes28.json" && python3 "$I/file_items.py" "$S/newitems28.json" && python3 "$S/edit28.py" || { echo "MUTATION FAILED midway — inspect git status"; exit 3; }
python3 - "$S/chronicle28_seal.md" "$@" <<'PY'
import sys, re, datetime
tpl, tip, union, parity, ci, m19, cp, l19 = sys.argv[1:9]
rec = open(tpl).read()
for k, v in {"<TIP>": tip, "<UNION>": union, "<PARITY>": parity, "<CI>": ci, "<M19TIP>": m19, "<CPTIP>": cp, "<L19TIP>": l19, "<DATE>": datetime.date.today().isoformat()}.items():
    rec = rec.replace(k, v)
left = [k for k in ("<TIP>", "<UNION>", "<PARITY>", "<CI>", "<M19TIP>", "<CPTIP>", "<L19TIP>", "<DATE>") if k in rec]
assert not left, left
p = "tracker/chronicle.md"; s = open(p).read()
head = "## Order 28 — cycle 46: CI in five minutes, the context boundary, the rulings of the fifth (2026-09-05 → )"
if head in s: s = s.replace(head, head.replace("→ )", f"→ {datetime.date.today().isoformat()})"), 1)
open(p, "w").write(s.rstrip("\n") + "\n" + rec)
print("chronicle: seal record appended")
PY
git add -A projects/vilan/tracker projects/vilan/proposal tracker/chronicle.md && python3 scripts/check_hygiene.py || { echo "HYGIENE FAILED — staged, not committed"; exit 4; }
git commit -q -m "Order 28 sealed at vilan $1 — 41 closes, 25 filed, prose ledger rows 386–399, M27/M36/E121 corrected, chronicle cycle 46

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>" && git push -q origin HEAD && git log --oneline -1
