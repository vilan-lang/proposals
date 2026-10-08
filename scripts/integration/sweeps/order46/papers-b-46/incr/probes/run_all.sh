#!/bin/sh
# Re-runs the incremental-analysis probes (i1..i7) on the installed vilan.
# Each iN shows an edit whose effect lands OUTSIDE the edited function.
cd "$(dirname "$0")"
vilan --version
for d in i1 i2 i4 i6 i7; do
  for f in $d/before.vl $d/after.vl $d/after2.vl; do
    [ -f "$f" ] || continue
    echo "== $f"; vilan check "$f" 2>&1 | head -16
  done
done
echo "== i6 emitted (async + hidden context param reach the callers)"
vilan build i6/before.vl >/dev/null 2>&1 && grep -n 'function' i6/before.mjs
vilan build i6/after.vl >/dev/null 2>&1 && grep -n 'function\|await' i6/after.mjs
echo "== i3 (impl in a module the user never imports)"
( cd i3 && printf 'import pkg::user::use_it;\nimport pkg::impls;\nfun main() { print(use_it()); }\n' > src/main.vl && vilan check . 2>&1 | head -8; echo "-- without main's import of impls:"; printf 'import pkg::user::use_it;\nfun main() { print(use_it()); }\n' > src/main.vl && vilan check . 2>&1 | head -8 )
echo "== i5 (platform colour: body edit of label, error lands in args_count)"
( cd i5 && sed -i 's/{ i"x{args_count()}" }/{ "x" }/' src/shared.vl && vilan check . 2>&1 | head -4; echo "-- after:"; sed -i 's/export fun label(): str { "x" }/export fun label(): str { i"x{args_count()}" }/' src/shared.vl && vilan check . 2>&1 | head -10 )
