#!/bin/sh
# N?1's measurement, repeatable from a vilan checkout (suite-48, Order 48).
# Builds vilan-core at opt-level 1 into a separate target dir, then compares an
# inference test's CPU and the edit tax with the default (opt-level 0) build.
#   sh test-profile-opt-level.sh /path/to/vilan
set -eu
cd "$1"
O1="target/opt-level-probe"
cargo build -p vilan-core --test inference
CARGO_TARGET_DIR="$O1" cargo build --config 'profile.dev.package.vilan-core.opt-level=1' -p vilan-core --test inference
for binary in "$(ls -t target/debug/deps/inference-* | grep -v '\.d$' | head -1)" \
              "$(ls -t "$O1"/debug/deps/inference-* | grep -v '\.d$' | head -1)"; do
    echo "== $binary"
    # Forty-one tests, every 130th of the list from the 11th: CPU incl. children.
    "$binary" --list 2>/dev/null | grep ': test$' | sed 's/: test$//' | awk 'NR%130==11' |
        while read -r name; do "$binary" --exact "$name" > /dev/null 2>&1; done
    times
done
# The edit tax: one comment line inserted mid-file (shifts every later span),
# rebuilt at each level, then restored.
cp crates/vilan-core/src/analyzer.rs /tmp/analyzer.rs.keep
sed -i '40000i // probe' crates/vilan-core/src/analyzer.rs
time cargo build -p vilan-core --test inference
time env CARGO_TARGET_DIR="$O1" cargo build --config 'profile.dev.package.vilan-core.opt-level=1' -p vilan-core --test inference
cp /tmp/analyzer.rs.keep crates/vilan-core/src/analyzer.rs
