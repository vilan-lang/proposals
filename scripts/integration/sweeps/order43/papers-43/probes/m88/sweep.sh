#!/bin/bash
# M88 corpus sweep: build every vilan/test/*.vl (scratch copy) and every example/benchmark
# project to JS, count emitted vtables (`Object.create({`, the sole producer is emit_vtable)
# and `[1].member(` object-dispatch sites.
export PATH=$HOME/.cargo/bin:$HOME/.nvm/versions/node/v24.2.0/bin:$PATH
S=${1:?scratch dir holding test/ examples/ benchmarks/ copies of vilan/vilan/{test,examples,benchmarks}}
cd $S/test
for f in *.vl; do
  out=$(vilan build --stdout "$f" 2>/dev/null) || { echo "FAIL $f"; continue; }
  n=$(printf '%s' "$out" | grep -c 'Object\.create({')
  [ "$n" -gt 0 ] && echo "test/$f vtables=$n"
done
for d in $S/examples/* $S/benchmarks; do
  (cd $d && vilan build . >/dev/null 2>&1) || echo "FAIL $d"
  for js in $(find $d -path '*/node_modules' -prune -o \( -name '*.js' -o -name '*.mjs' \) -newer $S/test/dyn-objects.vl -print); do
    n=$(grep -c 'Object\.create({' $js); [ "$n" -gt 0 ] && echo "${js#$S/} vtables=$n"
  done
done
echo done
