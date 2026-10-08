#!/usr/bin/env bash
# Register on first start (the config lives in the container's home volume afterwards), then run.
# RUNNER_TOKEN is the one-hour registration token from Settings > Actions > Runners > New
# self-hosted runner; it is only read when .runner is missing. The label `vilan-linux` is what
# ci.yml routes trusted ubuntu legs to.
set -euo pipefail
cd /home/runner
if [ ! -f .runner ]; then
  : "${RUNNER_TOKEN:?set RUNNER_TOKEN in .env for the first start}"
  ./config.sh --unattended --replace \
    --url "https://github.com/${RUNNER_REPO:-vilan-lang/vilan}" \
    --token "$RUNNER_TOKEN" \
    --name "${RUNNER_NAME:-$(hostname)}" \
    --labels "vilan-linux" \
    --work _work
fi
exec ./run.sh
