## perf-46 is rebased onto `origin/next` @7ee822af and green — tip **@5b31a201** (5b31a2017cbf57c04cdf010e0f338613f6b2b9bb), not pushed

The rebase replayed 13 commits plus one new one: the reference ceilings re-taken on the rebased tree. Every gate you asked for passes on 5b31a201.

### What conflicted
- **Only `CHANGELOG.md`, in every commit.** Each conflict was my entry and the syntax/native/solver-a entries inserted at the same place under the one `## Unreleased`. I kept both sides each time; my entries follow theirs.
  - Checked after: one `## Unreleased`, 37 family markers for 37 entry heads, my ten entries each present once, no conflict markers left.
- **No source conflicts.** solver-a-46's `analyzer.rs` changes merged cleanly with mine.
- I left the `---` separators as each side wrote them; your Unreleased section already mixes both styles.

### The things my fixes lean on, checked on the merged tree
- **Late type-slot writes are still zero** (the counter that must stay at 0 after the constraint fixpoint).
  - Measured with the release build and `VILAN_COUNTERS=1` over 145 corpus files, all 11 examples, and both kolt copies.
  - The inference suite also runs with the `debug_assert` that fires on any such write, so it covers solver-a's new passes, `check_trait_method_scope` included.
  - Nothing needed changing.
- **My member/trait indexes agree with solver-a's blanket-through-bounds path.** The debug build runs the old full scan beside the index and asserts the two give the same candidates; that held across the whole suite.
- **The M107 doubling pin and the M108 slot pin both pass.**

### Re-measured numbers

Hardware instruction counts and peak RSS (per-child, via `wait4`). Release builds, macro caches warm, kolt's scratch copy at @984a1dfb.

| | v0.43.0 (fe092e8d) | next @7ee822af | perf-46 @5b31a201 |
|---|---:|---:|---:|
| kolt `vilan check` instructions | 25.63 G | 26.03 G | **23.92 G** (23.76 G sequential) |
| kolt peak RSS | 328 MB | 329 MB | **252 MB** (199 MB sequential) |
| kolt working tree, instructions / RSS | 26.47 G / 431 MB | 26.70 G / 417 MB | **24.34 G / 282 MB** |
| Doubling, plain package 160 → 320 modules | 6.40 → 19.16 G = x2.99 | 6.42 → 19.23 G = x2.99 | **2.89 → 5.61 G = x1.94** |
| Plain package 320 → 640 modules | — | — | 5.61 → 13.06 G = x2.33 |

- The three merged lanes cost next +1.6% on kolt (25.63 → 26.03 G). On my tip that shows as about +1.1% over the pre-rebase figure (23.61 → 23.92 G).
- **Ceilings:** `perf/budgets.toml`'s `reference` rows are now taken on the rebased tip (@5b31a201, stamped "rebased on next @7ee822af"). The examples total 29.9 G and the generated kolt-shaped app is 9.95 G.
- The LSP memory high-water figure (687 MB) is from before the rebase. I did not re-run the LSP harness, and nothing in the rebase touched the language server session.

### Gates on 5b31a201

| gate | result |
|---|---|
| full workspace suite | 9465/9465 |
| native differential, default | 154/154 |
| native differential, `VILAN_NATIVE_DIFFERENTIAL=1` | 154/154 |
| `check_scope_differential` | 15/15 |
| `ci-local.sh fmt` | green |
| `ci-local.sh clippy` | green |
| `ci-local.sh vilan-fmt` | green |
| `ci-local.sh perf` (reference class) | T2 verdict green, all 12 rows within ceiling, growth x1.940 |

### The seal line for `proposals/scripts/integration/seal.sh`, base v0.43.0
This replaces the `perf_compare.py` call on line 34; the `cargo build … -p vilan-cli -p vilan-lsp` on line 32 stays as it is:

```sh
lsp_json=()
if [ -f "$W/scripts/lsp-latency.py" ]; then
    python3 "$W/scripts/lsp-latency.py" --kolt "$HOME/code/kolt" --commit 984a1dfb --runs 5 \
        --lsp "${VILAN_PERF_LSP_BASE:-$HOME/.vilan/bin/vilan-lsp}" --json "$S/lsp-base-$tip.json" > "$S/lsp-base-$tip.log" 2>&1 &&
    python3 "$W/scripts/lsp-latency.py" --kolt "$HOME/code/kolt" --commit 984a1dfb --runs 5 \
        --lsp "$W/target/release/vilan-lsp" --json "$S/lsp-tip-$tip.json" > "$S/lsp-tip-$tip.log" 2>&1 &&
    lsp_json=(--lsp-json "$S/lsp-base-$tip.json" "$S/lsp-tip-$tip.json")
fi
python3 "$W/scripts/perf_gate.py" seal --class reference \
    --tip "$W/target/release/vilan" --tip-std "$W/vilan/std" \
    --base "${VILAN_PERF_BASE:-$HOME/.vilan/bin/vilan}" \
    --kolt "$HOME/code/kolt" --commit 984a1dfb --runs 5 \
    --sha "$(git -C "$W" rev-parse HEAD)" "${lsp_json[@]}" > "$S/perf-$tip.log" 2>&1; pf=$?
[ $pb -ne 0 ] && pf=$pb; grep -E "T3 kolt|T2 VERDICT|PERF VERDICT|OWNER|RED|wrote" "$S/perf-$tip.log"; echo "perf exit=$pf"
```

- **Base binary.** `~/.vilan/bin/vilan` must still be v0.43.0 when this runs; otherwise pin it with `VILAN_PERF_BASE`.
- **Base std.** The kolt copy goes to the system temp directory, outside any checkout, so the base uses its own embedded std and needs no `--base-std`. `seal` refuses to run a copy that sits inside a checkout without one.
- **Verdict file.** It writes `~/.vilan/perf-verdicts/perf-<sha>.json`, which is the default location `cut-release.sh` now reads.
- **Load.** The CPU verdict comes out red above loadavg 2, so run it quiet.
- **`--advance`.** Add it only on the final seal of the order. It counts that seal toward E121's two-greens-then-blocking rule and rewrites `perf/budgets.toml`.