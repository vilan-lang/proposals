#!/usr/bin/env bash
# seal.sh — the pre-seal verdict on the integration tip: union, the whole-set native differential, clippy, the Windows cross-check,
# audit, fmt, changelog parity. Logs beside this script. CI green on the tip is still the last word.
set -u
S=$(cd "$(dirname "$0")" && pwd)
W=${VILAN_INTEGRATION:-$HOME/code/vilan-lang/vilan/.claude/worktrees/integration}
cd "$W" || exit 1
tip=$(git rev-parse --short=8 HEAD); echo "tip=$tip loadavg=$(cut -d' ' -f1-3 /proc/loadavg)"
cargo nextest run --workspace > "$S/suite-$tip.log" 2>&1; u=$?; grep -E '^\s+Summary' "$S/suite-$tip.log" | tail -1; echo "union exit=$u"
# The DOC-TESTS: nextest skips them, CI's test leg runs them (Order 40: two indented lowering sketches in
# vilan-rust's doc comments compiled as Rust and reddened CI after a green seal). ~1 min.
cargo test -q --doc --workspace > "$S/doctest-$tip.log" 2>&1; d=$?; echo "doc-tests exit=$d"
# The WHOLE-SET native differential (Order 38's lesson: the default suite is ten programs; the
# whole set was red at the base for a whole order and no seal looked). ~1 min.
VILAN_NATIVE_DIFFERENTIAL=1 cargo nextest run -p vilan-cli --test native_differential > "$S/native-$tip.log" 2>&1; n=$?; echo "native whole-set exit=$n"
cargo clippy --workspace --all-targets -- -D warnings > "$S/clippy-$tip.log" 2>&1; c=$?; echo "clippy exit=$c"
cargo clippy --target x86_64-pc-windows-msvc --workspace --exclude vilan-rt-sqlite --all-targets -- -D warnings > "$S/win-$tip.log" 2>&1; w=$?; echo "windows exit=$w"
cargo audit --deny unsound > "$S/audit-$tip.log" 2>&1; a=$?; echo "audit exit=$a"
cargo fmt --all --check > "$S/fmt-$tip.log" 2>&1; f=$?; echo "fmt exit=$f"
# The tree's VILAN sources (CI's `vilan-fmt` job): Orders 41 and 42 both went red on CI here after a green seal —
# a formatter rule landed in the same order as std edits formatted under the old rule.
scripts/ci-local.sh vilan-fmt > "$S/vilan-fmt-$tip.log" 2>&1; vf=$?; echo "vilan-fmt exit=$vf"
# CI's `wasm` leg and the stack canary's MARGIN (Order 44: both were CI-only finds after a green seal — the playground
# smoke program spelled a renamed method; the walk frame grew past Windows's 2 MiB thread). The canary honours
# VILAN_CANARY_STACK_KIB (deep_nesting.rs, added in Order 45); 1536 leaves ~25% under the 2 MiB it must hold.
scripts/ci-local.sh wasm > "$S/wasm-$tip.log" 2>&1; wa=$?; echo "wasm exit=$wa"
VILAN_CANARY_STACK_KIB=1536 cargo nextest run -p vilan-core --test deep_nesting > "$S/canary-$tip.log" 2>&1; cn=$?; echo "canary@1.5MiB exit=$cn"
# The PERFORMANCE verdict (Order 45, M105): the tip against the PREVIOUS RELEASE (the installed toolchain, or
# $VILAN_PERF_BASE / $VILAN_PERF_LSP_BASE) on kolt, by CPU time — `vilan check` and, when the tree carries it, the
# LSP edit-latency harness. Red past x1.10. v0.42.0 shipped a 3x regression with every other leg green. Run the
# seal on a QUIET machine: CPU time moves ~30% with load here.
cargo build -q --release -p vilan-cli -p vilan-lsp > "$S/perf-build-$tip.log" 2>&1; pb=$?
# Since Order 46 (M105 S6, fix-46): `perf_gate.py seal` writes the verdict the cut requires. ACROSS A BREAKING RELEASE the
# base and the tip cannot check one source, so the tip gets its own prepared, migrated kolt in $VILAN_PERF_TIP_KOLT
# (a plain directory: no git; built once so generated files exist). Without it, both sides check kolt@$VILAN_PERF_KOLT_COMMIT.
# `shared.vl keystroke` is left out: its anchors are gone from today's kolt (N145). Add --advance by exporting
# VILAN_PERF_ADVANCE=1 on the order's FINAL seal only. Run QUIET (load <= 2).
commit="${VILAN_PERF_KOLT_COMMIT:-984a1dfb}"; kolt="$HOME/code/kolt"
# The suite above leaves the load high; the CPU verdict goes red past load 2, so wait for quiet (at most 15 min).
for _ in $(seq 1 90); do awk '{exit !($1 < 1.5)}' /proc/loadavg && break; sleep 10; done; echo "perf leg starts at loadavg=$(cut -d' ' -f1-3 /proc/loadavg)"
scen=(--scenario "leaf keystroke" --scenario "leaf keystroke + pause" --scenario "shared.vl keystroke" --scenario "model.vl keystroke" --scenario "model.vl keystroke, importers open" --scenario "css keystroke" --scenario "parse break")
tip_kolt=(); tip_src=(--kolt "$kolt" --commit "$commit")
if [ -n "${VILAN_PERF_TIP_KOLT:-}" ]; then tip_kolt=(--tip-kolt "$VILAN_PERF_TIP_KOLT"); tip_src=(--source "$VILAN_PERF_TIP_KOLT"); fi
lsp_json=()
python3 scripts/lsp-latency.py --kolt "$kolt" --commit "$commit" --runs 5 --lsp "${VILAN_PERF_LSP_BASE:-$HOME/.vilan/bin/vilan-lsp}" "${scen[@]}" --json "$S/lsp-base-$tip.json" > "$S/lsp-base-$tip.log" 2>&1 &&
python3 scripts/lsp-latency.py "${tip_src[@]}" --runs 5 --lsp "$W/target/release/vilan-lsp" "${scen[@]}" --json "$S/lsp-tip-$tip.json" > "$S/lsp-tip-$tip.log" 2>&1 &&
lsp_json=(--lsp-json "$S/lsp-base-$tip.json" "$S/lsp-tip-$tip.json")
adv=(); [ -n "${VILAN_PERF_ADVANCE:-}" ] && adv=(--advance)
python3 scripts/perf_gate.py seal --class reference --tip "$W/target/release/vilan" --tip-std "$W/vilan/std" \
    --base "${VILAN_PERF_BASE:-$HOME/.vilan/bin/vilan}" --kolt "$kolt" --commit "$commit" "${tip_kolt[@]}" --runs 5 \
    --sha "$(git rev-parse HEAD)" "${lsp_json[@]}" "${adv[@]}" > "$S/perf-$tip.log" 2>&1; pf=$?
[ $pb -ne 0 ] && pf=$pb; grep -E "T3 kolt|T2 VERDICT|PERF VERDICT|REFUSED|OWNER|RED|different sources|wrote" "$S/perf-$tip.log"; echo "perf exit=$pf"
python3 - "$W/CHANGELOG.md" <<'PY'
import sys
ls = open(sys.argv[1]).read().split("\n")
s = next(i for i, l in enumerate(ls) if l.startswith("## Unreleased"))
e = next((i for i in range(s + 1, len(ls)) if ls[i].startswith("## ")), len(ls))
print("changelog parity", sum(l.startswith("<!-- family:") for l in ls[s:e]), "/", sum(l.startswith("**") for l in ls[s:e]))
PY
echo "verdict: union=$u doctests=$d native=$n clippy=$c windows=$w audit=$a fmt=$f vilan-fmt=$vf wasm=$wa canary=$cn perf=$pf"
