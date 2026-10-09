#!/usr/bin/env bash
# papers-b-48's estate census. Builds the walker against the vilan tree's own
# parser and runs it over each estate. Usage:
#   run_census.sh <vilan worktree at origin/next> <kolt copy> <website copy>
# Copy census/ under <worktree>/target/ first (the crate's path dependency is
# ../../../crates/vilan-core). NEVER point it at the live kolt or website
# checkouts' git: it only reads .vl files, but take copies anyway.
set -eu
wt="$1"; kolt="$2"; site="$3"
here="$(cd "$(dirname "$0")" && pwd)"
dest="$wt/target/papers-b-48-scratch/census"
mkdir -p "$dest/src"; cp "$here/Cargo.toml" "$dest/"; cp "$here/src/main.rs" "$dest/src/"
(cd "$dest" && CARGO_BUILD_JOBS=6 cargo build -q)
C="$dest/target/debug/papers-b-census"
cd "$wt"
$C $(find vilan/std vilan/macro_std -name '*.vl') > "$here/std.txt"
$C $(find vilan/test vilan/benchmarks crates -name '*.vl') > "$here/corpus.txt"
$C $(find vilan/examples -name '*.vl') > "$here/examples.txt"
$C $(find "$kolt/src" -name '*.vl') > "$here/kolt.txt"
$C $(find "$site" -name '*.vl' -not -path '*/node_modules/*') > "$here/website.txt"
# docs: every ```vilan fence of vilan/docs and README.md, one file per fence
# (see the paper's §estate for the extractor), then: $C <fences> > docs.txt
