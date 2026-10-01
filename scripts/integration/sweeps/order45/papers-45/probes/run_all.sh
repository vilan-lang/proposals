#!/usr/bin/env bash
# papers-45 probes — regenerates run_all.out. Usage: run_all.sh <scratch-dir>
# Needs the installed `vilan` (0.42.0 when these were taken), python3, node,
# and cargo for the `--backend rust` rows.
set -u
export PATH="$HOME/.cargo/bin:$HOME/.nvm/versions/node/v24.2.0/bin:$PATH"
HERE="$(cd "$(dirname "$0")" && pwd)"
SCRATCH="${1:?scratch dir}"
TREE="${VILAN_TREE:-/home/reed/code/vilan-lang/vilan/.claude/worktrees/integration/vilan}"
KOLT="${KOLT_ROOT:-/home/reed/code/kolt}"
mkdir -p "$SCRATCH"
strip() { grep -vE '^\s*(│|╭|─|╰|┆|├|$)' | grep -vE 'Compiling|Finished|Running|Locking' | head -"${1:-8}"; }
{
echo "# vilan: $(vilan --version)"
echo
echo "## census.py (B485 §1, §5)"
python3 "$HERE/census/census.py" "$TREE" "$KOLT"
echo
echo "## order_matrix.py (B485 §6, B445)"
python3 "$HERE/order/order_matrix.py" "$SCRATCH/order"
echo
echo "## B485 marker probes"
for f in resource_erasure resource_erased resource_drop_on_data trait_only must_use const_fun const_fun_broken const_labels const_stale_steer platform_impl_dispatch; do
  [ -f "$HERE/census/$f.vl" ] || continue
  cp "$HERE/census/$f.vl" "$SCRATCH/"
  echo "### $f.vl (js)"; (cd "$SCRATCH" && vilan run "$f.vl" 2>&1 | strip 6)
done
echo
echo "## B460 opacity probes (js)"
for f in "$HERE"/opaque/*.vl; do
  b=$(basename "$f"); cp "$f" "$SCRATCH/"
  echo "### $b (js)"; (cd "$SCRATCH" && vilan run "$b" 2>&1 | strip 8)
done
echo
echo "## B460 opacity probes (rust)"
for b in o1_leak o2_annotation_does_not_flow o3_branches_dyn o5_generic o5_generic_one o5_generic_concrete o6_recursion o7_pipe_ok; do
  echo "### $b.vl (rust)"; (cd "$SCRATCH" && timeout 900 vilan run --backend rust "$b.vl" 2>&1 | strip 8)
done
echo
echo "## o8: the module boundary (v1, then v2 with the same signature)"
rm -rf "$SCRATCH/o8"; mkdir -p "$SCRATCH/o8"
printf '[package]\nname = "o8"\nroot = "."\nprelude = "std::prelude"\n' > "$SCRATCH/o8/vilan.toml"
cp "$HERE/opaque/o8_module/main.vl" "$SCRATCH/o8/"
cp "$HERE/opaque/o8_module/counters_v1.vl.txt" "$SCRATCH/o8/counters.vl"
echo "### v1"; (cd "$SCRATCH/o8" && vilan run . 2>&1 | strip 4)
cp "$HERE/opaque/o8_module/counters_v2.vl.txt" "$SCRATCH/o8/counters.vl"
echo "### v2"; (cd "$SCRATCH/o8" && vilan run . 2>&1 | strip 4)
} 2>&1
{
echo
echo "## fmt_today.vl through vilan fmt (B485 §6)"
cp "$HERE/order/fmt_today.vl" "$SCRATCH/fmt_today.vl"
(cd "$SCRATCH" && vilan fmt fmt_today.vl >/dev/null 2>&1; cat fmt_today.vl)
} 2>&1
