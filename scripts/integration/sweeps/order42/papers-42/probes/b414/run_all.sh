#!/bin/bash
# B414 probes (papers-42). Usage: run_all.sh <scratch-dir>. Needs `vilan` on PATH.
# Prints the 44-word x 9-position name matrix (ok = checks clean, X = refused),
# then the precedent, JSON, bindgen, native-field and derive-hygiene probes.
set -u
HERE=$(cd "$(dirname "$0")" && pwd); OUT=${1:?scratch dir}; mkdir -p "$OUT"; cd "$OUT"
vilan --version
POS="let param field method function variant closure alias typename"
printf "%-9s" word; for p in $POS; do printf "%-9s" $p; done; echo
for w in async await const css dyn else enum export external for fun if impl import in is jump lazy let macro match mod mut null own borrows ret resource struct trait type use with context sync as only self Self void layer; do
  "$HERE/gen.sh" $w w_$w; printf "%-9s" $w
  for p in $POS; do if vilan check w_$w/$p.vl >/dev/null 2>&1; then printf "%-9s" ok; else printf "%-9s" X; fi; done; echo
done
echo "== precedent.vl (as/only/sync/context as names beside their keyword readings)"; vilan run "$HERE/precedent.vl"
echo "== json_type.vl (a JSON key \"type\" and [derive(Json)])"; vilan run "$HERE/json_type.vl"
echo "== bindgen over w.d.ts (members lazy/css/dyn/type/with)"; vilan bindgen --platform browser -o widget.vl "$HERE/w.d.ts" && vilan check widget.vl 2>&1 | grep -m1 -E "^Error" || echo "widget.vl checks clean"
echo "== juxt.vl (a closure literal's return type followed by a local named context)"; vilan run "$HERE/juxt.vl"
echo "== self_field.vl on JS, then native"; vilan run "$HERE/self_field.vl"; vilan run --backend rust "$HERE/self_field.vl" 2>&1 | grep -m2 "cannot be a raw identifier"
echo "== wire_shadow.vl ([derive(Wire)] with a field named deserializer)"; vilan check "$HERE/wire_shadow.vl" 2>&1 | grep -m2 "^Error"
