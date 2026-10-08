#!/bin/sh
# Re-runs the debugging probes (d1..d12) on the installed vilan, JS backend.
cd "$(dirname "$0")"
vilan --version
for f in d1_print d2_debug d3_debug_list d4_debug_generic d6_panic d7_panic2 d9_resource d10_print_two d12_interp_struct; do
  echo "== $f.vl"; vilan run $f.vl 2>&1 | head -40; echo "(exit $?)"
done
for f in d5_emit d8_mono_names d6_panic d7_panic2; do
  echo "== emitted $f.mjs"; vilan build $f.vl >/dev/null 2>&1; cat $f.mjs; echo "-- sourceMappingURL lines: $(grep -c sourceMappingURL $f.mjs)"; ls $f.mjs.map 2>/dev/null || echo "-- no .map file"
done
