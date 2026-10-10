#!/bin/bash
# G28 repro (papers-50): the macro-expansion table a build writes is stamped
# with the toolchain VERSION and macro_std's hash - not the build. Every dev
# build between two releases says the same version, so a build that changes the
# macro engine or the const interpreter is served the previous build's
# expansions from dist/.cache (and from ~/.vilan/check-cache for `vilan check`).
set -e
here=$(cd "$(dirname "$0")" && pwd); work=$(mktemp -d)
cp -r "$here/vilan.toml" "$here/src" "$work/"; cd "$work"
vilan build . >/dev/null
echo "binary: $(vilan --version)"
echo "table header:"; head -3 dist/.cache/macro-expansions
echo "(no build sha in the stamp: two builds of $(vilan --version | cut -d' ' -f2) share every entry)"
rm -rf "$work"
