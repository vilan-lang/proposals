#!/usr/bin/env bash
# papers-39's probes, re-runnable. Every `.out` beside a probe is this script's
# capture on `vilan 0.40.0 (c3f7d1a38)` (= origin/next @c3f7d1a3), node 24.2.0.
#
#   ./run_all.sh
#
# Ports used: 59777 (a120_http_leg), 59778 (a120_stub_over_http). A probe that
# is EXPECTED to be red says so in its header comment and its `.out` ends with
# a non-zero `[exit N]`.
set -u
here="$(cd "$(dirname "$0")" && pwd)"

single() {                       # a one-file probe: `vilan run`
	local dir="$1" file="$2"
	( cd "$dir" && { echo "\$ vilan run $file"; timeout 120 vilan run "$file" 2>&1; echo "[exit $?]"; } \
		> "${file%.vl}.out"; rm -f "${file%.vl}.mjs" )
}

pkg_check() {                    # a package probe whose answer is the DIAGNOSTIC
	local dir="$1"
	( cd "$dir" && { echo "\$ vilan check ."; timeout 300 vilan check . 2>&1; echo "[exit $?]"; } > check.out )
}

pkg_run() {                      # a package probe: build, assert the artifact, run
	local dir="$1" artifact="$2" entry="$3"
	(
		cd "$dir"
		{
			echo "\$ vilan build ."
			timeout 300 vilan build . 2>&1
			echo "[build exit $?]"
			if [ -f "$artifact" ]; then
				echo "[artifact $artifact: $(wc -c < "$artifact") bytes]"
			else
				echo "[artifact $artifact: MISSING — this probe passed VACUOUSLY, do not believe it]"
			fi
			if [ -n "$entry" ]; then
				echo "\$ node $entry"
				timeout 120 node "$entry" 2>&1
				echo "[run exit $?]"
			fi
		} > run.out
	)
}

for file in "$here"/b363_positions/*.vl; do single "$here/b363_positions" "$(basename "$file")"; done
for file in "$here"/find_json_internal/*.vl; do single "$here/find_json_internal" "$(basename "$file")"; done

pkg_run   "$here/b363_rpc_void"          src/main.mjs      src/main.mjs
pkg_run   "$here/a120_http_leg"          src/main.mjs      src/main.mjs
pkg_run   "$here/a120_stub_over_http"    dist/server.mjs   dist/server.mjs
pkg_run   "$here/a120_content_type"      src/main.mjs      src/main.mjs
pkg_check "$here/a120_refusals"
pkg_run   "$here/find_arity"             src/main.mjs      src/main.mjs
pkg_run   "$here/find_json_reader"       src/main.mjs      src/main.mjs
pkg_run   "$here/find_export_impl"       src/main.mjs      src/main.mjs
pkg_run   "$here/a121_missing_bindings"  dist/client.js    ""
pkg_run   "$here/a121_focus_scope"       dist/client.js    ""

echo "done — outputs are the .out files beside each probe"
