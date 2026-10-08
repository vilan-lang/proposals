#!/usr/bin/env bash
# papers-46 probes — regenerates run_all.out. Usage: run_all.sh [scratch-dir]
# Needs the installed `vilan` (0.43.0 when these were taken) and node. Runs NO
# cargo: native rows are `vilan build --backend rust --stdout` (emitted Rust,
# read, not built).
set -u
export PATH="$HOME/.cargo/bin:$HOME/.nvm/versions/node/v24.2.0/bin:$PATH"
HERE="$(cd "$(dirname "$0")" && pwd)"
SCRATCH="${1:-$HERE/.scratch}"
mkdir -p "$SCRATCH"
strip() { grep -vE '^\s*(│|╭|─|╰|┆|├|$)' | head -"${1:-12}"; }
run() { # dir file [lines]
  cp "$HERE/$1/$2" "$SCRATCH/"
  echo "### $1/$2 (js)"; (cd "$SCRATCH" && vilan run "$2" 2>&1 | strip "${3:-12}")
}
emit() { # dir file pattern
  cp "$HERE/$1/$2" "$SCRATCH/"
  echo "### $1/$2 (rust, emitted, grep '$3')"
  (cd "$SCRATCH" && vilan build --backend rust --stdout "$2" 2>&1 | grep -E "$3" | head -8)
}
{
echo "# vilan: $(vilan --version)"
echo
echo "## A153 — mirrored store"
run store s1_today_traffic.vl 40
run store s2_store_wire_bytes.vl 20
for v in 1 2 3; do run store "s3_hash_v$v.vl" 3; done
run store s4_map_field_is_a_leaf.vl
run store s4b_no_at.vl 3
run store s5_rpc_store_return.vl 6
run store s6_owner_rule_today.vl
run store s7_identity_eq_leaf.vl
echo
echo "## B495 — views in closure types"
for f in v1_let_typed v2_value_into_view v3_generic_identity v4_option_capture v5_generic_struct v6_direct_control v7_let_literal_adopt v7b_let_literal_read v8_spelled_through_option v9_read_controls; do
  run views "$f.vl" 6
done
emit views v1_let_typed.vl 'Error|dyn Fn'
emit views v2_value_into_view.vl 'dyn Fn'
emit views v3_generic_identity.vl 'fn hold|dyn Fn'
emit views v5_generic_struct.vl 'dyn Fn|\(h_[0-9]+\.f\)'
emit views v8_spelled_through_option.vl 'dyn Fn|\(f_[0-9]+\)|\(g_[0-9]+\)'
emit views v9_read_controls.vl 'dyn Fn'
echo "### views/v1_let_typed.vl (js, emitted)"; (cd "$SCRATCH" && vilan build --stdout v1_let_typed.vl 2>/dev/null | sed -n '5,11p')
echo
echo "## B509 — payload views"
for f in b1_today b2_match_ref_mut b3_pattern_spellings b3b_ref_let b4_wrapped_view_fn b5_some_mut_fn b6_cost b7_derive_shape_cost b8_subject_frozen_precedent b9_wrapped_subject_write b10_match_ref_read b11_rule4_liveness b12_view_subject b12b_view_subject_spelled; do
  run payload "$f.vl" 6
done
echo "### payload/b7_derive_shape_cost.vl (js, emitted through_variant)"; (cd "$SCRATCH" && vilan build --stdout b7_derive_shape_cost.vl 2>/dev/null | grep -A9 "function through_variant")
emit payload b7_derive_shape_cost.vl 'clone|fn through_variant'
emit payload b1_today.vl 'take|held_[0-9]+ = Some'
emit payload b9_wrapped_subject_write.vl 'match first|bag_[0-9]+\.items ='
} 2>&1
