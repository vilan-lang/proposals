#!/usr/bin/env bash
# Re-run every papers-38 probe and capture its output beside it.
#
#   ./run_all.sh            the nine plain .vl probes (no valgrind, ~1 min)
#   ./run_all.sh --cost     also the two Ir measurements — `each`'s scan half
#                           against the delta path, and door 2's per settle.
#                           Generates the programs from the two templates and
#                           runs callgrind. ~25 min. Needs valgrind and node.
#   ./run_all.sh --door2    also the A110 door-2 ordering comparison across the
#                           scratch stds in ../door2 (which ../door2/README.md
#                           says how to build).
#
# Toolchain: vilan 0.40.0 (0fa109eb7), node v24.2.0, valgrind-3.24.0. Every
# output is captured beside the probe as <name>.out; the two measurement legs
# write each_cost.out and door2_cost.out.
set -u
cd "$(dirname "$0")"
DOOR2="$(cd .. && pwd)/door2"

for probe in \
	probe_c_self_receivers \
	probe_a_mut_receivers \
	probe_b_list_adopts_trait \
	probe_law_randomized \
	probe_fold_needs_removed \
	probe_keyed_cell_today \
	probe_per_element_owner \
	probe_per_element_index_hazard \
	probe_a110_wave_order
do
	printf '=== %s\n' "$probe"
	timeout 600 vilan run "$probe.vl" > "$probe.out" 2>&1
	printf 'exit=%s\n' "$?" >> "$probe.out"
	cat "$probe.out"
done

case "${1:-}" in
--door2)
	printf '=== door 2, across the scratch stds\n'
	{
		echo "### probe_a110_door2_nesting.vl, five stds"
		for variant in baseline vilan popped popped-scrub fast; do
			echo "--- VILAN_STD=door2/$variant/std"
			VILAN_STD="$DOOR2/$variant/std" timeout 200 vilan run probe_a110_door2_nesting.vl 2>&1
		done
		echo
		echo "### probe_scrub_misses_draining_turn.vl"
		for variant in baseline scrubonly fast; do
			echo "--- VILAN_STD=door2/$variant/std"
			VILAN_STD="$DOOR2/$variant/std" timeout 200 vilan run probe_scrub_misses_draining_turn.vl 2>&1
		done
	} > door2_variants.out 2>&1
	cat door2_variants.out
	;;
--cost)
	printf '=== each_cost (callgrind Ir)\n'
	python3 - <<'PY'
template = open('each_cost_template.vl').read()
for mode, name in ((0, 'scan'), (1, 'delta')):
	for repeats in (1, 21):
		source = template.replace('__MODE__', str(mode)).replace('__REPEATS__', str(repeats))
		open(f'each_cost_{name}_{repeats}.vl', 'w').write(source)
for rows in (500, 2000):
	for repeats in (1, 11):
		source = (template.replace('__MODE__', '0').replace('__REPEATS__', str(repeats))
			.replace('let rows_total: i32 = 1000;', f'let rows_total: i32 = {rows};'))
		open(f'each_scale_{rows}_{repeats}.vl', 'w').write(source)
PY
	: > each_cost.out
	uptime >> each_cost.out
	for program in each_cost_scan_1 each_cost_scan_21 each_cost_delta_1 each_cost_delta_21 \
		each_scale_500_1 each_scale_500_11 each_scale_2000_1 each_scale_2000_11
	do
		timeout 240 vilan build "$program.vl" > /dev/null 2>&1 || { echo "BUILD FAILED $program" >> each_cost.out; continue; }
		printf '%s ' "$program" >> each_cost.out
		timeout 1800 valgrind --tool=callgrind --callgrind-out-file=/dev/null \
			node --jitless "$program.mjs" 2>&1 | grep 'I   refs:' >> each_cost.out
	done
	uptime >> each_cost.out
	cat each_cost.out

	printf '=== door2_cost (callgrind Ir)\n'
	python3 - <<'PY'
template = open('door2_cost_template.vl').read()
for turns in (1, 201):
	open(f'door2_cost_{turns}.vl', 'w').write(template.replace('__TURNS__', str(turns)))
PY
	: > door2_cost.out
	uptime >> door2_cost.out
	for variant in baseline nosort fast popped-scrub; do
		for turns in 1 201; do
			VILAN_STD="$DOOR2/$variant/std" timeout 300 vilan build "door2_cost_$turns.vl" > /dev/null 2>&1 \
				|| { echo "BUILD FAILED $variant $turns" >> door2_cost.out; continue; }
			mv "door2_cost_$turns.mjs" "door2_${variant}_$turns.mjs"
			printf '%s ' "door2_${variant}_$turns" >> door2_cost.out
			timeout 900 valgrind --tool=callgrind --callgrind-out-file=/dev/null \
				node --jitless "door2_${variant}_$turns.mjs" 2>&1 | grep 'I   refs:' >> door2_cost.out
		done
	done
	uptime >> door2_cost.out
	cat door2_cost.out
	;;
esac
