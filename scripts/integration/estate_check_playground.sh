#!/usr/bin/env bash
# estate_check_playground.sh — N127's DRAFT (std-42, Order 42): `vilan check` every
# vilan-playground exhibit, so a breaking lane's estate sweep CHECKS the playground's
# programs instead of only counting them. Proposed home: proposals/scripts/integration/
# beside seal.sh (the integrator's), called from a breaking lane's re-sweep and at the seal.
#
#   estate_check_playground.sh [PLAYGROUND_DIR]   (default: $HOME/code/vilan-lang/vilan-playground)
#
# The compiler is $VILAN if set, else the `vilan` on PATH; VILAN_STD is passed through, so a
# lane checks against its own tree with VILAN=<worktree>/target/debug/vilan
# VILAN_STD=<worktree>/vilan/std. An exhibit is a directory holding a vilan.toml (checked as
# a package, every entry) or a loose top-level .vl file (checked as a file). Exit 0 only when
# every exhibit checks clean; each verdict is printed with the first error line.
set -u
dir=${1:-$HOME/code/vilan-lang/vilan-playground}
vilan=${VILAN:-vilan}
[ -d "$dir" ] || { echo "no playground at $dir"; exit 2; }
red=0; count=0
check() { # label, working dir, args...
    local label=$1 at=$2; shift 2
    count=$((count + 1))
    local out; out=$(cd "$at" && "$vilan" check "$@" 2>&1); local code=$?
    if [ $code -eq 0 ]; then echo "  ok   $label"
    else red=1; echo "  RED  $label (exit $code): $(printf '%s\n' "$out" | grep -m1 -E 'Error|error' || printf '%s\n' "$out" | head -1)"; fi
}
for manifest in "$dir"/*/vilan.toml; do
    [ -f "$manifest" ] || continue
    package=$(dirname "$manifest")
    check "$(basename "$package")/ (package)" "$package"
done
for file in "$dir"/*.vl; do
    [ -f "$file" ] || continue
    check "$(basename "$file")" "$dir" "$(basename "$file")"
done
echo "playground: $count exhibit(s), $([ $red -eq 0 ] && echo green || echo RED)"
exit $red
