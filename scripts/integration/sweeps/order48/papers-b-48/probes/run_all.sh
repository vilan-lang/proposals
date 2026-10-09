#!/usr/bin/env bash
# papers-b-48 probes: copies each probe to a scratch dir, runs `vilan check`
# and (when it checks) `vilan run`, and prints both. Usage: run_all.sh <scratch>
# Run against `vilan 0.45.0 (e75bc57c3)` = origin/next @e75bc57c.
set -u
here="$(cd "$(dirname "$0")" && pwd)"
scratch="${1:?scratch dir}"
mkdir -p "$scratch"
vilan --version
for dir in b569 b571 b570; do
  for f in "$here/$dir"/*.vl; do
    name="$(basename "$f")"
    cp "$f" "$scratch/$name"
    echo "=================== $dir/$name"
    if (cd "$scratch" && vilan check "$name") > "$scratch/$name.check" 2>&1; then
      echo "[check: clean]"
      cat "$scratch/$name.check"
      echo "[run]"
      (cd "$scratch" && timeout 30 vilan run "$name" 2>&1) | head -20
    else
      echo "[check: refused]"
      sed 's|'"$scratch"'/||g' "$scratch/$name.check" | head -30
    fi
  done
done
