## incr-53b hand-back (Order 53) — M144, std-prefix P3, N177 → C2

All three items are built and pinned on branch `incr-53b`. Nothing is pushed; none of my
processes are running; `incr-53b-STATUS.md` is untracked and current.

- **Tip:** `78b70b21` on branch `incr-53b`.
- **Base:** C1 `6fe278ca` (the incr-53a merge). Not rebased.
- Worktree `vilan/.claude/worktrees/incr-53b` (the base worktree I used for the base binaries is
  reaped). Kolt was read as a `cp -r` copy under `target/incr-53b-scratch/kolt` (lucide and
  search-dict carried); no git command ran in kolt or the website.

### Commits (oldest first)
| sha | Item / slice | Family |
|---|---|---|
| `a2935296` | M144: non-std module nodes mint after std's walk (P3's first step) | performance |
| `d53382d9` | std-prefix P3: the std-only prefix world persisted and loaded across processes (the serializer, the key, the load fixups, the std import index, the consumers) | performance |
| `78b70b21` | N177: const-site keys are a function of the site's content | tooling |

CHANGELOG `## Unreleased`: 18 heads, 18 markers (three mine).

### What each does, and where the premise was wrong

**M144.** The drain registers a non-std module's SOURCE at discovery (SourceId, text, package,
parse diagnostics — nothing that mints) and holds its NODE back (`DeferredMint` in `analyzer.rs`);
std's modules mint and walk as before, then std's `lib.vl`, then the package's and the dependencies'
nodes mint in `load_hot_modules`' order (namespaces, then modules and the entry's alias, each in
discovery order) and walk. `mint_module_node` is the one mint both the drain's std arm and the
deferred mint call. The repro read Id(8149)/Id(8151) at C1 and Id(8149) both after.
- Premise right: std's ids are a function of the std set.
- Premise wrong in two places: (1) the paper's "reorder-only golden diff" never materialized — the
  corpus and the permutation differential are byte-identical (nothing in the goldens depends on
  where a module NODE sits); (2) the two shapes still do not number a whole program alike: the
  std-only world's `resolve_world` mints ~600 entities before the package's nodes mint, the
  canonical path mints them before its one resolve, so a package item's id (and the native
  backend's `name_<id>`) differs across shapes — filed (M?1) with a repro; §4.2's hardening is the
  door.
- Pin: `module_resolution::m144_a_std_items_id_does_not_move_with_the_packages_module_count`.

**P3.** `crates/vilan-core/src/prefix_file/{codec,mod}.rs` (new): an in-tree serde binary codec
(varints, positional fields, one string table every borrowed `&str` points into — a loaded world's
names and the std texts are slices of the leaked file) and the file (magic, an inline header
carrying the §6 key in clear + the canonical std roots + lengths + a checksum, temp-and-rename
write, a `Miss` for every way a read fails). serde derives across the world's types (~150 types in
`analyzer.rs`, `analyzer/*.rs`, `type_.rs`, `node.rs`, `macros.rs`, `error.rs`, `id.rs`, `span.rs`,
`target.rs`, `counters.rs`; lifetime-carrying types take
`#[serde(bound(deserialize = "'de: 'static"))]`). The census landed as the paper's §13 "As built
(P3)" paragraph says (appended, uncommitted in the proposals checkout). The hooks: `base_cache_admit`
loads on an absent std-prefix key (once per key per process) and either inserts the world as a
stored one (validated by content through the same lookup) or — a one-shot process, the in-memory
store off — hands it over directly; `prefix_file_write` after the std-only world's BUILD (not its
store: the CLI stores nothing) when the process looked for the file and missed, refusing a world
with late-round mints (B619) or overlay-served std; the six derive/boundary queues drained before
the store; paths re-rooted both ways through the key's canonical std roots; `id_windows.source_keys`
recomputed on load; the macro registry's files re-rooted. Switches: `incremental::world_cache_dir`
(`VILAN_WORLD_CACHE=off|<dir>`, else a front-end default; off under hash shuffle and in a clean
analysis), the census's `prefix_file` / `prefix_file_bytes` / `prefix_file_micros` and the
counters line's `prefix-file=` columns, `analyzer::prefix_file_counts` / `prefix_files_forget`
(test surface). Consumers: `vilan` and `vilan-lsp` set `vilan_embedded::default_world_cache_root()`
= `~/.vilan/cache/worlds`; `.cargo/config.toml` says `VILAN_WORLD_CACHE = "off"` for every test
process (P5 flips it). The format carries a tier list (`["std"]`) from version 1.
- Premises wrong in detail: (1) "the closure costs microseconds" — in a fresh process `std_closure`
  PARSES std to collect imports (31 ms on a one-import program, 105–162 ms per kolt leg, release),
  which ate most of the saving; the paper's own "std import graph ships in the prefix index" is
  now real: `std_import_index` (a 3 KB `std-index/<hash>.index` per std content beside the worlds,
  built by parsing once) makes the closure 4–11 ms; (2) a loaded world inserted into the base cache
  AND cloned for the analysis cost kolt +48 % peak RSS — the CLI's canonical path retains nothing —
  hence the one-shot serve; (3) `span_map` stays `&'src Span` (322 sites, solver-53 live in the
  checks) and comes back as references into one leaked slice per load, rather than the paper's tree
  change; (4) std's 39 `[hint(..)]` attributes keep AST type nodes re-resolved on every checks
  phase, so the AST family derives serde and the nodes ride by value — a row the census did not
  list; (5) the write has to ride the BUILD, not the store (the CLI switches the in-memory store
  off), and a bug of the first cut was exactly that — kolt wrote nothing until it was moved.
- Not built (filed, M?2): M19's checks record and S2's tables in the file (Q9) — the record is
  filed after the world's analysis and only under the prefix key in P1's shape; a layered build
  never consults it. P4's housekeeping (filed, N?1).

**N177.** `const_cache::Keyer` walks each lowered node by variant and content: a name bound
inside the program being hashed (a parameter, a `let`/`const`, a `for..of` binding, a label, a
function's own name) hashes as the ordinal of its first occurrence (the emitter appends ids to
declared names — `flush_stylesheet13056`), a name that reaches a WORLD declaration as that
declaration's content DIGEST (memoized by address for the pass, as the item recommended; a digest
computed across a recursion marker is not memoized), a free name by its text; the emitter's
`Mark`/`At` ids and the functions' `origin`s are dropped, a closure's `origin` kept only under
`snapshots` (the one id the interpreter reads, into `ConstValue::Callable { body }`). A first cut
without the memo re-hashed every site's world and read +0.74 % on `genapp:46` and +5 % on kolt's
leaf keystroke (3.30 → 3.48 G); the digests bring those back (the rows below). Kolt: 109 keys
today (the item said 113); 30/109 shared with the marks and origins stripped alone, 109/109 with
the renaming; the two tables and `dist` byte-identical.
- Pin: `const_disk_cache::n177_the_table_is_the_same_over_the_std_prefix_and_the_canonical_world`.

### Measured rows (release `vilan`, the tree's std, box at load 6–10 with four lanes building)
| row | canonical | over the loaded prefix |
|---|---:|---:|
| `vilan check time.vl` instructions | 726.2 M | 674.0 M (−7.2 %); the writing run 787.6 M (+8 %, once) |
| `vilan check time.vl` peak RSS | 55.5 MB | 56.3 MB |
| kolt `vilan check .` (both legs) instructions | 10.68 G | 9.27 G (−13.2 %) |
| kolt peak RSS | 266 MB | 274 MB (+2.7 %) |
| std tier file | — | 1.01 MB (corpus), 6.06 MB (kolt server), 6.39 MB (kolt client); the index 2,959 B |
| file read + decode | — | 8 ms (corpus), 41 / 52 ms (kolt server / client) |
| closure (index / parsing) | — | 4–8 ms vs 31 ms (corpus); 6 / 11 ms vs 134 / 114 ms (kolt) |
| hit clone (the server; the CLI takes none) | — | 4–5 ms |
| package resolve over the prefix (P1's, unchanged) | — | 0.5 ms (corpus), 9–25 ms (kolt server), 220–360 ms (kolt client) |

Debug-profile loads, for the record: 62–67 ms (corpus), 268 / 295 ms (kolt) — the suite's
differentials pay those. The "tens of ms against ~600 ms of std analysis" row the brief asked
for reads, on kolt's legs: 41 / 52 ms of file against a canonical `load+walk 336 + base 236 ms`
(server) and `631 + 535 ms` (client) under load; the loaded leg's remaining `load+walk` is the
package's own walk and P1's package resolve.

### Gates on the tip
- **Full suite** (`--cargo-profile ci-test -E 'not binary(deep_nesting)' -j 6`): 10,668 run, 10,662 passed, 6 failed on the first tip — all six one bug of mine (`LeakSite::PrefixFile` added as the enum's FIRST variant overran the 21-row site table: the leak report, and through it three macro-failure pins); fixed (the variant last, the table 22) and folded into the P3 commit; the four red binaries + `leak_tally` rerun in full: 5,659/5,659. Within the suite: `ci_ignored_pins` 12, `hygiene` 3, `corpus` 14 (goldens byte-identical, none regenerated), `check_scope_differential` 21, `permutation_differential` 7 (the prefix leg included), `edit_replay_differential` 27 (the layered leg included), `replay_differential` 2, `id_windows` 11, `module_resolution` 263 (M144's pin), `native_differential` 285 (default mode), `prefix_roundtrip_differential` 3 (new), `prefix_roundtrip_native` 2 (new), `const_disk_cache` 5 (N177's pin), vilan-lsp 1,134 (the cold-start pin included), the codec's and the file's unit tests 8.
- **Native differential, sweep mode** (`VILAN_NATIVE_DIFFERENTIAL=1`): 285/285.
- **Canary** at 1536 KiB (dev profile): 18/18.
- **vilan-lsp binary** (nextest): 1,134/1,134 (+1 pin).
- **clippy `-D warnings`**, **`cargo fmt --check`**, **`vilan fmt --check .`**: clean.
- **`ci-local.sh perf`**: T2 green. Against the base binary (C1) measured on the same box, instructions: ten rows within 0.1 % (−0.00 … +0.098 %), four over it: `plain:160` +0.140 %, `plain:320` +0.131 %, `example:todo` +0.114 %, `genapp:46` +0.113 % (the attribution note at the end). The cache is never touched by the perf leg: the CLI's default is the canonical shape (`VILAN_STD_PREFIX` off), so "cache absent" and "cache present" are one measurement there; the loaded-prefix rows are the table above.
- **RSS** (`scripts/rss-probe.py`, kolt, 5 runs, medians): base 268,016 KB, tip 267,880 KB (−0.05 %).
- **Late writes**: 0 on kolt's two legs canonical, over the built prefix and over the loaded file; `late-round-mints` 0.
- **`records-served` on a served keystroke**: the 40-keystroke `--session` script, base vs tip: every census column identical (hot set, base hit/miss/store, sources walked, records replayed, functions checked); the session's instruction total 177.35 → 170.24 G (the cold opens over the file).
- **The seven editor rows on a cold start** (`lsp-latency.py --source <kolt copy> --runs 3`, base @6fe278ca vs tip, CPU ms, loadavg 6–10 with four lanes building — CPU is a claim about the load, instructions the number): open rows views 1630 → 1470 (1220 in the first tip run), views beside an importer 30 → 40, shared 650 → 600 (490), model 600 → 560 (500), model beside 3 importers 120 → 30 (40), styles 1280 → 1570 (1190), channel 2420 → 1270 (1160). Edit rows, instructions G base → tip: leaf 3.30 → 3.30, leaf + pause 8.17 → 8.18, world 3.65 → 3.65, shared 1.23 → 1.23, model 1.21 → 1.21, importers open 4.48 → 4.48, css 5.51 → 5.51, parse break 5.50 → 5.50 (CPU: leaf 710 → 580, pause 1740 → 1510, importers open 890 → 750, css 1010 → 980, parse break 980 → 910). E292 stays open (css and parse break are the whole-file re-walk's).

### Functions changed
- **analyzer.rs:** `analyze_inner` (M144: `DeferredMint`, the walk closure, the deferred mint
  loop, the prelude loops after it; P3: `prefix_file_wanted`, the pre-drain, the write, the
  `prefix-admit` mark, `late_round_mints_before`), new `mint_module_node`, `DeferredMint`;
  `base_cache_admit` (new `std` parameter; the load arm), `base_cache_lookup_locked` (the content
  check factored into `stored_world_contents_match`), `base_cache_store` (the scrub factored into
  `scrubbed_world`), new `prefix_file_key`, `std_closure_content`, `prefix_file_load`,
  `prefix_file_write`, `std_spec_roots`, `World::reroot_std_paths`, `prefix_file_counts`,
  `prefix_files_forget`, `StdImportIndex` + `std_import_index`, `std_closure` (over the index),
  `std_prefix_keys` (the `prefix-closure` mark), `resolve_package_over_prefix` (a mark),
  `Analyzer::drain_boundary_checks`, `PhaseMarks::unstarted`; `BaseCacheState` (+2 sets);
  `World`/`Analyzer`/`HotWorld` and ~120 further types: derives and `#[serde(skip)]` rows.
- **const_cache.rs:** `site_key` (the memo is now `world_digests: &mut HashMap<usize, u64>`),
  `hash_node` → `Keyer` + `Scope` (the digest, the renaming, the content walk); `evaluate`
  threads the memo; **const_eval.rs:** the pass's memo field renamed `world_digests`.
- **incremental.rs:** `world_cache_dir`, `set_world_cache_default`, `set_world_cache`, the census
  fields, `report`'s counters line. **macros.rs:** `MacroRegistry::reroot_files`, `MacroDef.world`
  skipped. **leak_tally.rs:** `LeakSite::PrefixFile`. **lib.rs:** `mod prefix_file`.
- **vilan-embedded:** `default_world_cache_root`. **vilan-cli main:** the default root.
  **vilan-lsp main:** the default root + the cold-start pin. **Cargo:** serde `rc`, indexmap
  `serde` (features of crates already here; Cargo.lock moved accordingly). **.cargo/config.toml:**
  `VILAN_WORLD_CACHE = "off"`.
- No mono.rs or emitter change. Nothing in inference / the checks / dispatch_refine (solver-53's)
  beyond derive attribute lines above type definitions in `analyzer.rs`.

### Finds
`sweeps/order53/newitems53-incr-53b.json`; repro under `sweeps/order53/incr-53b/finds/`.
- **M?1** — a package item's id (and native name) still differs between the canonical and the
  prefix shape after M144 (std's resolve mints before the package's nodes); §4.2's hardening or
  id-free native names close it. Repro `m144_prefix_shape_package_ids/run.sh`.
- **N?1** — the world cache grows per (build id, platform, closure) and nothing prunes it (P4).
- **M?2** — M19's record and S2's tables are not in the file yet (Q9); the step is named.

### Questions for the owner
1. **The record in the file (M?2).** Append the prefix key's `WorldChecks` (minus `per_item`) at
   the end of the analysis that built the prefix and insert it into `CHECKED_CACHE` on load? It
   buys the paper's 53 % → ~45 % on the CLI's `VILAN_STD_PREFIX=on` leg only (a layered build never
   reads it). **Rec:** Order 54 with P5, measured in instructions on the cold rows first.
2. **The CLI's default.** `VILAN_STD_PREFIX` stays `off` for the CLI (the file is used only under
   `on|layered`); with the file in, a cold `vilan check` reads −7 % (corpus) / −13 % (kolt) over it.
   Turn the CLI's default to `on` once P4's bound is in? **Rec:** not this order — the prefix shape's
   package ids differ from the canonical ones (M?1), so native output would change spelling by
   default; after §4.2 hardens, yes.
3. **§4.2 hardening** (M?1): make "std resolves alone" the canonical order too, so the two shapes
   are one layout and native bytes agree across them. **Rec:** paper it as P6 with M?1's repro.
4. **The span rows.** Keep the per-load leaked span slice (≈460 KB on kolt's client std) or do
   the by-value tree change (322 sites) once solver-53 is merged? **Rec:** the tree change in
   Order 54, behind the round-trip differential.

### The perf residue, attributed
`ci-local.sh perf` is green (T2); against the base binary four rows sit 0.01–0.04 % over the
0.1 % cold-row rule. A release build of the M144-only commit (`a2935296`) measured on the same
box: M144 alone is +0.024 % (`plain:320`), +0.032 % (`plain:160`), +0.029 % (`genapp:46`),
−0.009 % (`example:math`) and **+0.80 % on `example:todo`** — todo defines a macro, so its five
macro worlds re-drain, and the new walk order (std's modules, std's `lib.vl`, then the package)
settles their fixpoints in a different number of rounds; the full tip reads +0.114 % on todo, so
N177's keyer is cheaper there than the `Debug` rendering it replaced (−0.7 %), and the plain
rows' +0.13 % is P3/N177's canonical-path share (≤0.11 %) over M144's. No row is near the 3 %
bump bound and none moved a budget, so no `[[bump]]` row is written; if the seal's perf leg
wants the plain rows under 0.1 %, the candidates are `prefix_file_wanted`'s evaluation and
the `Scope` pre-pass of the keyer, both on the canonical path — I would measure a tip-minus-N177
binary first (one more release build) and say which.

### The other legs
- `ci-local.sh windows` (clippy for `x86_64-pc-windows-msvc` over the workspace's tests): ok,
  33 s. The code I cfg-gated is `target_arch = "wasm32"` (the prefix file's clock; B432's
  rule), not glibc-only, and `ci-local.sh wasm`: ok, 80 s.
- The home directory: my tip servers wrote `~/.vilan/cache/worlds` during the latency runs
  (the shipped default); the whole root was mine (the installed 0.50.0 never writes it) and is
  removed. The lane's files live under `target/incr-53b-scratch/`.

---

## Rebased onto `c5b59f0f` (the solver-53 merge) — 2026-10-16

- **Tip:** `05c21b00` on branch `incr-53b` (M144 `747f3046`, P3 `0a660ee0`, N177 `05c21b00`). **Base:** `c5b59f0f`. Nothing pushed; none of my processes running; the base worktree I used for the base binaries is reaped; `~/.vilan/cache/worlds` (written by my tip servers under the shipped default) removed again.
- **Conflicts met:** none — `git rebase origin/next` applied all three commits cleanly. solver-53's `Analyzer` field `swept_residual_generics: HashSet<TypeId>` sits inside the struct my derive covers and is plain resolve state, so it rides the derive (no skip row needed); no other type my codec serialises gained a field (checked `git diff 6fe278ca c5b59f0f` for struct rows). CHANGELOG `## Unreleased`: 25 heads, 25 markers (my three kept).
- **Gates on `05c21b00`:** `cargo fmt --check`, clippy `-D warnings`, `vilan fmt --check .` clean. Full suite (`--cargo-profile ci-test -E 'not binary(deep_nesting)' -j 6`): **10,697/10,697** (37 skipped) — within it `ci_ignored_pins` 12, `hygiene` 3, `corpus` 14, `check_scope_differential` 21, `permutation_differential` 7, `edit_replay_differential` 27, `replay_differential` 2, `id_windows` 11, `module_resolution` 263, `native_differential` 288, `prefix_roundtrip_differential` 3, `prefix_roundtrip_native` 2, `const_disk_cache` 5, the codec/file unit tests 8, vilan-lsp 1,134 (the cold-start pin included). Native differential sweep mode: 288/288. Canary 1536 KiB: 18/18. `ci-local.sh windows` ok (24 s), `wasm` ok.
- **`ci-local.sh perf`:** T2 green. Instructions vs a base binary built from `c5b59f0f` on the same box: `example:todo` −0.732 %, eleven rows within 0.1 % (+0.022 … +0.088), `genapp:46` +0.104 %, `plain:320` +0.107 %, `plain:160` +0.151 % — the residue profile of the first report (M144's walk order on the plain rows, ≤0.03 %, plus P3/N177's canonical-path share); no budget moved, no `[[bump]]`.
- **RSS** (`rss-probe.py`, kolt, 5 runs, medians): base 268,352 KB, tip 269,688 KB (+0.5 %).
- **Editor rows** (`lsp-latency.py --source <kolt copy> --runs 3`, base `c5b59f0f` vs tip, loadavg 6–10): edit rows' instructions identical — leaf 3.28 → 3.29 G, pause 8.13 → 8.15, world 3.64 → 3.64, shared 1.22 → 1.22, model 1.21 → 1.21, importers open 4.46 → 4.47, css 5.50 → 5.51, parse break 5.49 → 5.50, parse repair 5.62 → 5.62 (CPU within ±40 ms either way). Open rows with NO prefix file present (the tip's first start writes it): views 1160 → 1160 ms, shared 470 → 490, model 490 → 450, model beside 3 importers 40 → 40, styles 1210 → 1260, channel 1220 → 1140 — the write costs nothing visible. Open rows on a COLD start WITH the file present (a second server start): see below.
- **Cold start WITH the file present** (the tip server started once to write both legs' tiers — 6,826,883 and 6,485,757 bytes under the rebased std — then started again, `--runs 3`): open rows base → tip: views 1160 → 1130 ms, views beside an importer 40 → 50, shared 470 → 510, model 490 → 500, model beside 3 importers 40 → 40, styles 1210 → 1180, channel 1220 → 1140; keystroke instructions identical (leaf 3.28 → 3.29 G, world 3.64 → 3.64, importers open 4.46 → 4.47, css 5.50 → 5.51, parse break 5.49 → 5.50). On this box the file's saving on an open — std's load+walk+base, tens of ms against a package walk and checks it does not remove — is within the load's noise; the session script read the same servers at 177.35 → 170.24 G over its ten cold-ish opens, and the CLI's cold rows (−7.2 % corpus, −13.2 % kolt in instructions) are the clean number.
- **Late writes** 0 and `records-served` unchanged as before (the session's 40 keystrokes identical in every census column on the first tip; the keystroke rows above say the same of the rebased one).
- The report above (sizes, loads, the premise notes, the finds, the questions) stands for the rebased tip; every sha in it maps `a2935296 → 747f3046`, `d53382d9 → 0a660ee0`, `78b70b21 → 05c21b00`.
