#!/usr/bin/env bash
# A131 probes (lane papers-43): the 300-turn walk re-run on the installed
# toolchain. walk/ = order42's walk-diagnostic.vl ported to usize indexes (the
# in-tree `pick(bound: usize)` helper of ui_rows.rs's A112_S3_WALK); trace/ = the
# same plus the id each transient row carried and the op that minted it;
# control/ = ui_rows.rs's A112_S3_WALK verbatim (the pin's tail).
# harness.js = crates/vilan-cli/tests/support/dom/{stub,ui_rows}.js + the
# `__lists` tail of ui_rows.rs:4928-4940, then `require("./app.js")`.
# Usage: run_all.sh <scratch-dir>   (copies each probe there; never builds in place)
set -u
export PATH=$HOME/.cargo/bin:$HOME/.nvm/versions/node/v24.2.0/bin:$PATH
here=$(cd "$(dirname "$0")" && pwd)
scratch=${1:?scratch dir}
vilan --version
for d in walk trace control; do
  mkdir -p "$scratch/$d" && cp "$here/$d"/{app.vl,vilan.toml,harness.js} "$scratch/$d/"
  echo "== $d"
  (cd "$scratch/$d" && vilan build . >/dev/null && node harness.js)
done
