## fix-46: report

**Branch `fix-46`, tip `a2972aa2`**, three commits on `origin/next` @98cae8a0. Nothing pushed. Worktree is `/home/reed/code/vilan-lang/vilan/.claude/worktrees/fix-46`; scratch and logs are in its `target/fix-46-scratch/`.
- `adbeec05` M116: `codegen-units = 1` (addition B).
- `586632e8` perf: the seal across a breaking release, `--tip-kolt` and `--source` (addition A).
- `a2972aa2` A154: `vilan check --fix` applies the moved-std-path rewrite, with the E268 brace-list fix.

**Gates on the final tree:** all green.
- `cargo nextest run --workspace -j 6`: 9,637 passed, 33 skipped.
- `cargo clippy --workspace --all-targets -D warnings`, `cargo fmt --check`, `ci-local.sh vilan-fmt` and `ci-local.sh windows`.

### 1. `vilan check --fix`: how it finds its sites, and why
It works from the analyzer's own `std-path/moved` refusals, not a separate syntactic pass over import lines. The reasons:
- **No successful analysis needed.** The refusal is raised exactly where an import stops resolving. A v0.43.0 package opened with v0.44.0 is refused at every old import, and those refusals are all the pass needs.
- **Only the analyzer knows two things a syntactic pass would have to guess.** It knows which `std::web::X` is the old prelude path (X is a name the prelude exports) and which is an ordinary typo. And it knows which files the program reaches. A syntactic pass would need a copy of that logic plus std's prelude list.
- **The editor and the command share one function.** `parsing::moved_std_module_edit` returns `Ok(fix)` or `Err(reason)`, and the LSP quick fix and `--fix` both call it. They cannot disagree.

How a run goes:
- **Manifests first.** `prelude = "std::web"` is rewritten by `manifest::rewrite_moved_prelude` before the project is resolved, because an old value stops resolution. It finds the value's span through `toml::Spanned` and replaces only that span, so comments and layout stay. A workspace's member manifests are rewritten too.
- **Then rounds.** A round that applies moved paths applies nothing else, because numeric diagnostics read under unresolved imports are not trustworthy. Rounds repeat until nothing changes, then the normal check runs.
- **Canonical files stay canonical.** If `vilan fmt` already left a file canonical, it is reprinted after the rewrite, because a moved import can sort to a new place. Without this, kolt had 11 files failing `fmt --check` after the fix.
- **Generated files are not rewritten.** A file under the package's declared `[package] generated` root (an existing manifest key, not a new convention) is named in the report and left alone. That covers kolt's `src/lucide/lib.vl`.
- **E268 (`std::web::{ Signal, dom::x }`) is now rewritten correctly**, in the editor and in `--fix`. It becomes `std::web::{ prelude::Signal, dom::x }`. The children of `std::web` are read off `MOVED_STD_MODULES` (every module whose new path is `web::<child>`); any other name gets `prelude::` in front.
- **Two shapes are left for a hand, with a reason.** `std::web::{ self, .. }`: `self` bound the old prelude as `web`. A list holding a reach marker, a selector or a nested group under the old web path. The LSP offers no edit for these.
- `StdPathFix.replacement` is now a `String`, because the E268 edit is computed.

### 2. The report wording
```
fixed 6 moved std paths in 4 files
  src/main.vl: 1
  src/state.vl: 3
  src/views.vl: 1
  vilan.toml: 1
left 1 moved std path in generated files — the project regenerates them, so change what generates them
  src/lucide/lib.vl: 1 (under the package's `generated` root, src/lucide)
left 1 moved std path for a hand — no one edit rewrites it correctly
  src/main.vl:1:13: the brace list names `self`, which bound the old web prelude as `web`; …
fixed 0 numeric mismatches in 0 files
```
- The moved and left lines appear only when there is something to say.
- The numeric line is always printed, worded as before, so the existing pins are untouched.
- A second run prints only `fixed 0 numeric mismatches in 0 files` and writes nothing.
- Paths are printed through `Path::strip_prefix(cwd).display()`, so nothing assumes a separator.

### 3. Pins (all shown red first)
- **`check_fix` (8 new):**
  - three files plus the manifest migrated by one run, then a clean check;
  - a file run (`check <file> --fix`);
  - a second run writing nothing;
  - the `self` list left with its reason;
  - a generated file named and not written;
  - a moved path and a numeric mismatch in one run;
  - a workspace member's manifest;
  - nothing to fix writes nothing (mtimes compared).
  - With the fix disabled, 7 of the 8 went red. The nothing-to-fix pin passes either way; that is what it asserts.
- **Unit pins:** `parsing::tests::a154_*` and `e268_*` (mixed, nested, aliased, multiline and block-scoped lists; self and marker; a stale span), and `manifest::tests::a154_the_moved_prelude_value_is_rewritten_in_place`.
- **LSP:** `moved_std_path_tests::a_mixed_web_list_moves_only_the_prelude_names` and `a_web_list_naming_self_is_offered_no_edit`.
- **Windows:** a module comment in `check_fix` explains how the pins avoid separators. The expected paths are built with `Path::join`.

**Docs:** the `--fix` entry in `appendix/cli.md` is rewritten (both fix kinds, the report, idempotence). The A154 CHANGELOG entry gains "One command migrates a package: `vilan check --fix`" and the details, still under `## Unreleased` with its `family: breaking` marker.

### 4. Real-world proofs, compared with the hand-written patches
**kolt** (a `cp -r` copy; no git run in `~/code/kolt`):
- Prepared base: owner tree + `kolt-a152-message-row` + `kolt-a150-model-states`.
  - **a150 has one rejected hunk** (`Channel::find` in `model.vl`): the owner's tree no longer matches its context, and the leftover `find` still calls the removed `transient_of`. I replaced that call with `client.get_channel(channel_id).states()` by hand in both copies. The integrator's recipe will hit the same rejection.
  - `kolt-autofocus` reports "already applied".
- `--fix` changed 28 paths in 19 files (18 `.vl` plus `vilan.toml`) and left `src/lucide/lib.vl`, naming it.
- Compared with base + `kolt-a154-std-paths.patch`, every `.vl` file and `vilan.toml` is byte-identical except:
  - `src/store.vl:7` and `src/theme.vl:313`: comments that mention old paths (prose is out of reach).
  - `scripts/lucide.mjs:228` (the generator's import string) and `:71`, `e2e/lucide-check.js:10`: JS, out of scope.
- After the one `lucide.mjs` line was edited by hand: `vilan build .` is green (lucide regenerated), `vilan check` has 0 errors, `fmt --check` is clean, and a second `--fix` is a no-op.
- Your extra check: `--fix` on the fully hand-migrated tree is a no-op, byte-identical.

**website** (a `cp -r` copy):
- `--fix` changed 10 paths in 10 files (9 `.vl` plus `vilan.toml`).
- Compared with `website-a154-std-paths.patch` (`.vl` and toml parts), the only differences are prose: comments in `client.vl:74`, `page.vl:4,633`, `playground_page.vl:5` and `vilan.toml:5,22`, and one **string literal**, `page.vl:673` `leaf("std::ui")`. That is display text, not an import; the hand patch changed it and `--fix` rightly does not.
- After the fix: `vilan build .` is green and `fmt --check src` is clean.
- `fmt --check .` also flags a stray nested `.claude/worktrees/k14` inside the website tree. That copy predates this change and is unrelated.

### 5. Addition A: the seal across a breaking release
- **`perf_gate.py seal --tip-kolt DIR`:**
  - The tip's source is a prepared tree, copied as it stands with no git. The base keeps `--kolt`/`--commit`.
  - Before anything is measured, each side runs `check` once on its own source. An error refuses the seal by name ("REFUSED  the tip's source (the prepared tree …) does not check under the tip compiler (exit 1): …"), prints `PERF VERDICT: REFUSED` and writes no verdict. A failure during measurement is red, never a ratio.
  - The console, the verdict (`t3.sources`, `t3.different_sources`, the note) and `perf_gate.py report` all say that the two sides checked different sources and that the cause is a breaking release.
  - `--tip-kolt` without `--kolt` is refused.
- **`lsp-latency.py --source DIR`:**
  - It replays the edit script over the prepared tree and records the source in `--json`. The seal notes when the two JSONs differ.
  - Every anchor of the chosen scenarios is looked up before the server starts. A missing anchor, or an edit anchor that occurs twice, refuses the run and names each one.
  - A relative `--lsp` path is now resolved before the server starts in the copy; it previously crashed.
  - Checked against the migrated kolt: every anchor occurs exactly once, **except the `shared.vl keystroke` scenario, whose three anchors are missing** from today's `src/shared.vl` (filed as N?2). A real `--source` run of two scenarios was green.
- **Pins in `perf_gate_script` (3 new; the first two are red on the old script):**
  - the refusal (tip broken, base broken, `--tip-kolt` alone);
  - a whole seal through `main()` with `perf_count.measure` stubbed: each side measured in its own copy (ratio 2.000), the note in the console, the verdict and the report, and the LSP note;
  - the harness refusing a tree its edit script does not land in.
- **The seal invocation:**
```
cd <next checkout at the seal sha>
LSP_SCEN=(--scenario "leaf keystroke" --scenario "leaf keystroke + pause" --scenario "model.vl keystroke" --scenario "model.vl keystroke, importers open" --scenario "css keystroke" --scenario "parse break")
scripts/lsp-latency.py --kolt ~/code/kolt --commit 984a1dfb --lsp <v0.43.0 vilan-lsp> "${LSP_SCEN[@]}" --json /tmp/lsp-base.json
scripts/lsp-latency.py --source <MIGRATED> --lsp target/release/vilan-lsp "${LSP_SCEN[@]}" --json /tmp/lsp-tip.json
scripts/perf_gate.py seal --tip target/release/vilan --base <v0.43.0 vilan> \
    --kolt ~/code/kolt --commit 984a1dfb --tip-kolt <MIGRATED> \
    --class reference --lsp-json /tmp/lsp-base.json /tmp/lsp-tip.json --advance
```
  - `<MIGRATED>` = `cp -r ~/code/kolt`, then apply a152, a150 (fix the one rejected `find` hunk as above), and either a154 or my `vilan check --fix`, plus the `lucide.mjs` line. Then `vilan build .` once, so lucide regenerates.
  - The six scenarios leave out `shared.vl keystroke`, which the migrated tree lacks. I could not confirm that 984a1dfb holds all six anchors, because that needs git in kolt. The preflight will say so loudly if not.
  - Add `--base-std` only if `--scratch` sits inside a vilan checkout.

### 6. Addition B: M116, `codegen-units = 1`
- Added under `[profile.release]` with a comment explaining why. `profiling` inherits it and `wasm-release` already had it.
- `release.yml` builds `cargo build --release` with only `--remap-path-prefix` in `RUSTFLAGS`. `.cargo/config.toml` sets only `[env]`, `~/.cargo` has no `config.toml`, and nothing else touches codegen units.
- `perf/budgets.toml` is untouched.

| | Before (16 units) | After (1 unit) |
|---|---|---|
| Clean `cargo build --release -p vilan-cli -p vilan-lsp`, wall | 63 s (load 0.66 → 3.08) | 144 s (load 0.91 → 1.44) |
| Kolt `vilan check`, `instructions:u`, median of 4 | 25,766.25M (spread ±25k) | 25,290.52M (spread ±15k) |

- The check figures are from `perf_count.py` with `VILAN_SEQUENTIAL_CHECK=1` on the migrated kolt. After is **−1.85%**. The before binary re-measured afterwards gave the same count (25,766.3M).
- Peak RSS: 210.4 → 209.3 MB. Binaries: vilan 14.4 → 12.9 MB, vilan-lsp 15.6 → 13.7 MB.

### 7. Finds (`proposals/…/order46/newitems46-fix.json`)
- **E?1:** a bare `import std::web;` (v0.43.0's prelude-as-module import, used as `web::Signal`) gets A65's generic namespace refusal. It carries no `std-path/moved` code and no fix, so `--fix` cannot migrate it. Rec: raise the moved refusal there, with the edit `import std::web::prelude as web;`.
- **N?2:** `lsp-latency.py`'s `shared.vl keystroke` anchors are gone from today's kolt. Re-anchor or retire the scenario when the seal's base moves past 984a1dfb.
- E268 (layout-46's find) is FIXED on this branch; close it at the merge.

### 8. Decisions for the owner
1. **E268 rewrite.** I rewrite the mixed list (`prelude::` before prelude names) rather than refuse it, as E268's recommendation allowed. Acceptable?
2. **A generated file is left, never rewritten.** kolt's `scripts/lucide.mjs:228` still needs its one-line hand edit (its patch already has it).
3. **The `kolt-a150-model-states` patch no longer applies cleanly** to the owner's tree (the `find` hunk). The owner should look at it before applying.