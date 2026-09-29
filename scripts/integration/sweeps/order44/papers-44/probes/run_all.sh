#!/usr/bin/env bash
# papers-44 probes: re-run every program the two papers cite and print what each
# printed. `store.md` cites store/, `reactive-maps-sets.md` cites maps/.
# Usage: run_all.sh [scratch-dir]   (native builds go under the scratch dir)
# Needs `vilan` (0.41.1, 07e8db37), node and cargo on PATH.
set -u
here="$(cd "$(dirname "$0")" && pwd)"
scratch="${1:-$(mktemp -d)}"
mkdir -p "$scratch"
TIMEFORMAT="user=%U"
# Paths in diagnostics are printed relative, so the captured output is portable.
clean() { sed -e "s#$here/#probes/#g" -e "s#$scratch/#scratch/#g" -e "s#$HOME#~#g"; }
# Every ms a probe prints is wall time inside one process: read the ratios
# within one run, and the load average printed here, before the absolutes.
echo "# vilan: $(vilan --version)"
echo "# load average at start: $(cut -d' ' -f1-3 /proc/loadavg)"

js() {
	echo "=== $1 (js)"
	(cd "$scratch" && vilan run "$here/$1" "${@:2}" 2>&1 | grep -vE '^\s*$' | tail -40 | clean)
}

native() {
	echo "=== $1 (rust)"
	cp "$here/$1" "$scratch/" && (cd "$scratch" && vilan run --backend rust "$(basename "$1")" 2>&1 | tail -8 | clean)
}

# ---- store.md
js store/store_lens.vl
js store/store_derive.vl
js store/std_lens.vl
js store/compose_modify.vl
js store/derive_tiers.vl
js store/leaf_tier.vl
js store/extend_instantiation.vl
js store/field_reach.vl
js store/map_eq.vl
js store/set_eq.vl
js store/find_bare_place_call.vl
native store/find_bare_place_call.vl
js store/find_view_closure_read.vl
native store/find_view_closure_read.vl
js store/find_deref_copy_aliases.vl
js store/find_view_field.vl

# ---- reactive-maps-sets.md
js maps/order.vl
native maps/order.vl
js maps/per_key.vl
js maps/keyed_census.vl
js maps/void_value.vl
js maps/find_struct_default_param.vl
for n in 0 20000 200000; do js maps/churn.vl "$n"; done
for f in churn_native_0_2000 churn_native_200000_0 churn_native_200000_2000; do
	native "maps/$f.vl" >/dev/null
	dir="$scratch/dist/native/$f"
	(cd "$dir" && cargo build --release -q 2>/dev/null)
	bin="$(find "$dir/target/release" -maxdepth 1 -type f -perm -u+x | head -1)"
	for run in 1 2 3; do
		t=$( { time "$bin" >/dev/null; } 2>&1 )
		echo "=== maps/$f.vl (rust, release) $t"
	done
done
echo "# load average at end: $(cut -d' ' -f1-3 /proc/loadavg)"
