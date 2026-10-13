## std-52 rebased onto f40e2b47: all gates green, nothing pushed

**Base:** f40e2b47. **New tip:** 15bc448d on branch `std-52`, worktree `/home/reed/code/vilan-lang/vilan/.claude/worktrees/std-52`. None of my processes are running.

### Rebase
- **Conflicts:** only `CHANGELOG.md`, once per commit. Each time I kept next's entries and added mine after them.
- **analyzer.rs** merged without conflict. `check_hashable_boundary` is still in the same `unless_cancelled!` block after C1; S7b did not reroute it. So B622's `hashable_member_under_binders` and the `Type::Generic` arm in `resolved_type_is_hashable` apply unchanged.
- **Ruling 1:** B615's CHANGELOG entry is dropped. I amended the commit, which keeps its pins and native probe and now carries no `family:` line.
- **Ruling 2:** no Wire line for arrays was ever written.
- **CHANGELOG parity:** next's 11 family markers are all intact, and mine add 3: B622 `fix`, B623 `feature`, B621 `fix`.

### Commits
| Commit | Item | Family |
|---|---|---|
| 0005db09 | B621 | fix |
| 1654a90c | B623 | feature |
| 5dfefbb3 | B622 | fix |
| 15bc448d | B615 | pins only, no entry |

B622 is still the ownership exception in analyzer.rs: `check_hashable_boundary` (one call), `resolved_type_is_hashable` (a Generic arm; the name shortcut now applies only to non-generic derives), and the new `hashable_member_under_binders`. mono.rs and the emitters are untouched.

### Gates (rerun in full after the rebase)
| Gate | Result |
|---|---|
| Full suite, `--cargo-profile ci-test -E 'not binary(deep_nesting)' -j 6` | 10,555 / 10,555 passed (32 skipped) |
| — `ci_ignored_pins` | 12 |
| — `hygiene` | 3 |
| — `corpus` | 14 |
| — `check_scope_differential` | 16 |
| — `native_differential`, default mode | 278 |
| Native differential, `VILAN_NATIVE_DIFFERENTIAL=1` sweep | 278 / 278 (1 skipped) |
| Deep-nesting canary at 1536 KiB | 18 / 18 |
| `vilan-lsp` binary | 1103 / 1103 (21 skipped) |
| clippy, `cargo fmt --check`, `cargo run -p vilan-cli -- fmt --check .` | clean |
| `scripts/ci-local.sh perf` | T2 green, growth ×1.931 |
| Late writes | 0 on kolt (12 analyses) |
| kolt cold-check RSS | ratio **1.0149** |

The RSS ratio compares tip against a release build of f40e2b47, as the median of 12 interleaved base/tip pairs. The allocator heap-peak counter turned out not to be deterministic: it swings about 4% between runs on the same binary. So the RSS ratio is the reading that holds, and it is inside 3%.

Finds (5) are in `sweeps/order52/newitems52-std-52.json`, with repros under `sweeps/order51/std-52/finds/`.

### Questions still open for the owner
1. **B622's ownership exception.** It is now rebased onto C1 and green. My recommendation is to merge it as is.
2. **Relaxing C7's Wire guard** so a reached type parameter can appear in a Wire field (`[derive(Wire)] struct Page<T> { items: List<T> }`). My recommendation is yes, in a later order. Whoever does it should change `resolved_type_is_wire` the same day so a generic derived type is judged by its arguments, not its name.
3. **Array types as path heads** (finding A?1). My recommendation is door (a): admit `[i32; 3]::default()` directly.
4. **B621's `HashSet`/`HashMap` bound.** I bounded them on the element being `Eq`. My recommendation is to keep that as written.
