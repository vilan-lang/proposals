#!/usr/bin/env bash
# C15 probes + census (lane papers-43; installed vilan 0.41.1 (1a33340f2)).
# Usage: run_probes.sh <scratch-dir>. Copies the probes, a scratch copy of
# vilan/test (the corpus) and of kolt (src + vilan.toml) there; never builds in
# place. Env knobs read: VILAN_NATIVE_REPORT_BOXED (boxed-bindings=N on a full
# build), VILAN_NATIVE_LEAK_CENSUS (cells minted/live after main's thread exits),
# VILAN_NATIVE_REPORT_COPIES (the consumed-copy census line).
set -u
export PATH=$HOME/.cargo/bin:$HOME/.nvm/versions/node/v24.2.0/bin:$PATH
here=$(cd "$(dirname "$0")" && pwd)
S=${1:?scratch dir}; mkdir -p "$S"; export CARGO_TARGET_DIR=$S/target
cp -r "$here/probes" "$S/"
rm -rf "$S/corpus" && cp -r /home/reed/code/vilan-lang/vilan/vilan/test "$S/corpus"
mkdir -p "$S/kolt" && cp -r /home/reed/code/kolt/src /home/reed/code/kolt/vilan.toml "$S/kolt/"
cd "$S/probes"
for p in p1_spec p2_readonly_mut p3_two_writers p4_list p5_immut_list p6_self_ref p7_mut_closure p7b_mut_closure_uncaptured p8_list_of_closures p9_holder p10_cycle p11_mut_param p12_mut_param_read; do
  echo "== $p"; echo "js: $(vilan run $p.vl 2>&1 | tail -1)"
  VILAN_NATIVE_REPORT_BOXED=1 vilan build --backend rust $p.vl 2>&1 | grep -E 'boxed-bindings|^error\['
  VILAN_NATIVE_LEAK_CENSUS=1 vilan run --backend rust $p.vl 2>&1 | grep -vE 'Compiling|Finished|Running|warning|^error|-->|^ *\||^ *[0-9]+ \|' | tail -3
done
# (a) corpus: emit-only census of distinct Captured declarations
python3 "$here/census_corpus.py" "$S/corpus"
# (b)/(c) syntactic census (classes i/ii/iii)
(cd /home/reed/code/vilan-lang/vilan/vilan/std/src && python3 "$here/census_syntactic.py" $(find . -name '*.vl' | sort))
(cd "$S/kolt/src" && python3 "$here/census_syntactic.py" $(find . -name '*.vl' -not -path './lucide/*' | sort))
# kolt's server, natively
(cd "$S/kolt" && VILAN_NATIVE_REPORT_BOXED=1 vilan build --backend rust src/server.vl 2>&1 | grep boxed)
