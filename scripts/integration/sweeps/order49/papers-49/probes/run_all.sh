#!/usr/bin/env bash
# Runs every probe: `vilan run` (JS) and `vilan run --backend rust`; prints the outputs.
export PATH="$HOME/.cargo/bin:$HOME/.nvm/versions/node/v24.2.0/bin:$PATH"
cd "$(dirname "$0")"
vilan --version
for f in ${@:-p*.vl}; do
  echo "=================== $f"
  echo "--- js:"
  timeout 120 vilan run "$f" 2>&1 | sed 's/\x1b\[[0-9;]*m//g' | head -30
  echo "--- native:"
  timeout 300 vilan run --backend rust "$f" 2>&1 | sed 's/\x1b\[[0-9;]*m//g' | grep -v "^\s*Compiling\|^\s*Finished\|^\s*Running" | head -30
done
