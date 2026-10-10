#!/bin/bash
# E294 repro (papers-50): the LSP's "leaf keystroke + pause" row on kolt, at the
# default base-cache budget and at a budget that holds every world. The pause's
# union analyses (the client ENTRY's world, the server ENTRY's world) are not
# live entries (M67), so each store evicts the other: the server world is rebuilt
# cold - std included - on most pauses.
#   ./run.sh <kolt-copy-with-src/lucide-and-src/search-dict> <scratch-dir>
# Never point it at the owner's checkout; it copies the tree it is given.
set -e
kolt=$1; scratch=$2
script=${LSP_LATENCY:-/home/reed/code/vilan-lang/vilan/.claude/worktrees/integration/scripts/lsp-latency.py}
lsp=${VILAN_LSP:-$HOME/.vilan/bin/vilan-lsp}
for budget in default 4096; do
  if [ "$budget" = default ]; then unset VILAN_BASE_CACHE_BUDGET_MIB; else export VILAN_BASE_CACHE_BUDGET_MIB=$budget; fi
  VILAN_PHASE_TIMING=passes VILAN_COUNTERS=1 python3 "$script" --source "$kolt" --lsp "$lsp" \
    --scratch "$scratch/lsp-$budget" --runs 5 --scenario "leaf keystroke + pause" > "$scratch/lsp-$budget.out" 2>/dev/null
  err="$scratch/lsp-$budget/vilan-lsp.stderr"
  echo "budget $budget: $(grep 'keystroke + pause' "$scratch/lsp-$budget.out" | cut -d'|' -f3-6)"
  echo "  server world (58 sources): misses $(grep -c 'sources-walked=58' "$err"), hits $(grep -c 'records-replayed=57' "$err")"
  echo "  client entry world (89 sources): misses $(grep -c 'sources-walked=89' "$err"), hits $(grep -c 'records-replayed=88' "$err")"
done
