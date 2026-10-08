## syntax-b-46: final report

The tool refused to write `REPORT-syntax-b-46.md` ("subagents return findings as text"), so the full report is below for you to save as `sweeps/order46/REPORT-syntax-b-46.md`. The new finds were written to `proposals/scripts/integration/sweeps/order46/newitems46-syntax-b.json`.

**Branch tip: `f62d64f0`** on `syntax-b-46` (worktree `vilan/.claude/worktrees/syntax-b-46`, off `origin/next` @7ee822af). Six commits, nothing pushed. Each has its CHANGELOG entry under `## Unreleased` with a `<!-- family: … -->` marker, and the trailer `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.

| item | status | sha |
|---|---|---|
| B536, with B485 S3 (BREAKING) | LANDED | 9f6ad451 |
| B524 (BREAKING, for `macro async fun`) | LANDED | a6662c91 |
| E256 | LANDED | 4e19c83a |
| B523 | LANDED | 2ac71f8b |
| E252 | LANDED | 8458a5b5 |
| K28 (all 20 fence lines) | LANDED | f62d64f0 |

**Gates at the tip** (all from base 7ee822af; machine load was 9 to 25 from other lanes):

| gate | result |
|---|---|
| `cargo nextest run --workspace -j 6` | 9460/9460, 32 skipped |
| `deep_nesting` with `VILAN_CANARY_STACK_KIB=1536` | 18/18 |
| `native_differential` with `VILAN_NATIVE_DIFFERENTIAL=1` | 154/154 |
| `cargo clippy --workspace --all-targets -- -D warnings` | clean |
| `cargo fmt --check` | clean |
| `scripts/ci-local.sh vilan-fmt` | green |

- No corpus golden moved.
- `parse_differential` and `vilan fmt --check` over std and the fixtures are unchanged, so canonical-order programs parse and format byte-identically.
- After B536 and B524 went in, I ran the whole workspace suite once. Its only red was `grammar_ebnf`, caused by an illustrative fence I had added to grammar.md; I turned it into prose.
- Every new pin was planted red first.

## B536 and B485 S3: one order for a declaration head

### The order, as `grammar.md` §3.2 now states it

A declaration head is written as:
1. its attributes, by rank;
2. then its keywords, in Q8's order: `export` (with its `(in PATH)`), then `const` or `lazy`, then `async`, then `external` or `macro`;
3. then the declaration word (`fun`, `struct`, `enum`, `trait`, `impl`, `let`, `mut`, `mod`, `import`, `use`).

The attribute ranks are `parsing::attribute_rank`, unchanged. They are also the order the printer itself writes, which a pin now checks:
1. generation: `[derive(..)]`, `[service(..)]`, `[client_service(..)]`, a macro attribute (kept in written order among themselves);
2. the labels: `[deprecated(..)]`, then `[internal(..)]`, then `[hint(..)]`;
3. the binding: `[extern(..)]`;
4. the checks: `[must_use]`, then `[rpc]`, then `[trait_only]`;
5. the fence: `[platform(..)]`;
6. the class: `[resource]`.

A head in any other order still parses and analyzes exactly like the canonical one (syntax-46's canonicalizer). What changes is the diagnostic it carries, one per head, spanning the run of markers as written:
- **Attributes out of rank, and nothing else out of order:** a WARNING. Its text: "a declaration's attributes are written in one order — `[derive]` and the other generators, `[deprecated]`, `[internal]`, `[hint]`, `[extern]`, `[must_use]`, `[rpc]`, `[trait_only]`, `[platform]`, `[resource]`: write `<the head in THE order>`".
- **A keyword ahead of an attribute, or two keywords inverted:** the existing error, unchanged in text.
  - **S3:** this now includes `export` and `macro` ahead of the attributes, for example `export [derive(Wire)] struct`, `export [deprecated(..)] import …`, `macro [deprecated(..)] fun`, and a run split across the marker (`[a] export [b] fun`).
- The written order is read off the tokens' spans, not their places in the token stream. B445's rotation has already turned a canonical `[..] export` into the `export [..]` the productions read, so stream order would misread it.

### The warning channel (new)

The parser had no way to report a warning, so I added one:
- `parsing::parse_with_warnings(source) -> (tree, errors, warnings)`. `parse()` is unchanged and drops the warnings.
- The warnings reach every reporting path:
  - the clean-parse cache: `CleanParse { ast, text, warnings }` via `parse_clean_cached_with_warnings`; `parse_clean_cached` keeps its signature;
  - the module loader: `LoadedModule.parse_warnings`, on all three paths (clean, error cache, owned);
  - `report_module_parse_warnings`, called at the three load seams, attributes each warning to its module's `SourceId`;
  - the entry: `vilan_core::add_entry_parse_warnings`, called from both `analyze_source` and the CLI's pipeline, before the post-passes order the diagnostics.
- A warning never makes a source unclean, so nothing is re-parsed and no helper sees a degraded tree.
- **analyzer.rs:** the loader part is about 40 lines: the struct field, the three constructors, the reporter and its three calls. I did not touch the inference code.

### `vilan fmt`

- It rewrites every non-canonical head to THE order, and the output is idempotent. That includes the refused heads: the formatter's `parse` accepts a source whose only errors are `MarkerOrder` refusals, because the tree is the canonical head's. So `vilan fmt` is the migration path for S3.
- The safety net's two passes (`lead_export_past_attribute_runs` and `sort_attribute_runs`) are replaced by one, `canonicalize_marker_heads`. It runs through the parser's own scanner (`parsing::marker_run_in_written_order`), so the net and the parser cannot disagree.

### The API for editor-46's quick fix

Everything is in `vilan_core::parsing`:
- `pub enum MarkerOrderDiagnostic { Attributes, Keywords }`, with:
  - `code()`, the stable codes to publish as the LSP `Diagnostic.code`: `marker-order/attributes` (the warning) and `marker-order/keywords` (the error, S3 included);
  - `is_warning()`;
  - `of_message(&str) -> Option<Self>`, which matches on the message's fixed head. The pipeline's `Error` has no code field, as with B520.
- `pub fn marker_order_fix(source: &str, message: &str, span: Span) -> Option<MarkerOrderFix>`, where `MarkerOrderFix { code: &'static str, title: String, span: Span, replacement: String }` means "replace `span` with `replacement`".
  - `span` is the diagnostic's own span, the run as written.
  - The replacement permutes the run's units exactly as written (arguments and `(in PATH)` included) into THE order. Whatever stood between them (blanks, line breaks, comments) stays where it stood.
  - The title is "Write `[deprecated(..)] [must_use] export fun`".
  - It returns `None` for any other diagnostic, and when the span no longer covers a marker run (a stale buffer).
- The warning arrives in `Program.warnings`, with its file in `warning_sources`, so the LSP publishes it with severity Warning through its existing warning path.

### Estate counts for S3 (checked before building)

`export [`, `macro [`, and a bare `export`/`macro` line followed by an attribute:
- **0** in std, the corpus (`vilan/test`), `vilan/examples`, the native fixtures, the book (fences and prose) and kolt.
- `vilan check` on kolt (read-only) with this compiler: exit 0, no marker-order diagnostics. **No kolt patch is needed.**
- The only sites were about 25 old-order strings in Rust tests:
  - `diagnostics.rs` 8, `workspace.rs` 3, `vilan-lsp/document.rs` 4, `platform_color.rs` 3, `parsing.rs` 6, `inference/platform.rs` 1;
  - each was rewritten to the canonical order, or turned into a refusal pin where the test was about reading the old side (B445's "both sides", B487's const label, the split run).
  - No assertion was weakened.

### The 29 swaps, re-classified

Papers-45's six stacks are re-read in THE order (attributes, then `export`, then the other keywords):
- **Canonical:** the six stacks themselves. Each parses with no diagnostic, and the printer writes it in the order itself (a pin parses the print with warnings on).
- **Warns:** 18. These are every swap of two attributes.
- **Refused:** 11. Each one puts a keyword ahead of an attribute (`export` included) or inverts two keywords:
  - `external fun` stack: platform↔export, export↔async, async↔external;
  - async `fun` stack: platform↔export, export↔async;
  - `external struct`: resource↔export, export↔external;
  - `struct`: resource↔export;
  - `trait`: resource↔export;
  - `lazy let`: internal↔export, export↔lazy.
- All 29 format to the stack.
- A second pin writes each stack in the order before B485 (`export` first) and checks it is refused and formatted to the stack.

### Pins

All were planted red: the warning taken out, `export`/`macro` exempted again, the entry path removed, the module path removed, and the `analyze_source` path removed.
- `parsing::tests::b536_every_adjacent_marker_swap_is_canonical_warned_or_refused`
- `b485_s3_export_ahead_of_the_attributes_is_refused_and_formatted`
- `b536_attributes_out_of_rank_warn_and_read_in_it`: seven heads, plus non-warning controls (THE order, ties, one attribute, a list indexed by a list).
- `b536_the_marker_order_fix_writes_the_head_in_the_order`: nine fixes, comments kept, each re-parsing clean, plus the codes and the recognizer.
- `b486_keywords_take_one_order_and_come_after_the_attributes`, now with S3's shapes.
- `inference::platform::b536_an_attribute_order_warning_rides_the_analysis`.
- `diagnostics::b536_an_attribute_order_warning_renders_in_its_file_and_is_not_fatal`: through the binary, an entry and a module, under `build` and `check`.

**Census and ledger:** the marker census moves (an attribute after `export` is no longer taken; `export` follows the attributes, one order only). One `NEW` ledger row, for the warning. The refusal's row 615 is unchanged.

## B524: `async macro fun`

Decided by Q8's table (door (b)):
- `async macro fun` is canonical and reads clean.
- `macro async fun`, the one order the macro production read before, gets the marker-order refusal with "write `async macro fun`". That makes it BREAKING for the old spelling.
- The printer writes `async macro fun` under the attributes, so `vilan fmt` migrates it.
- Pins: `formatter::reformats::b524_an_async_macro_prints_async_macro_fun`, plus the B536 parser pins' async-macro cases. Both were planted red.
- The census's `async`/`macro` pair flips.

## E256

`self as name` now sorts right after a bare `self` and ahead of every member. One key change (`BranchKey::SelfAlias`), shared by the printer, the safety net and Organize Imports (`organize_import_runs`), so all three agree. Two renames of one namespace order by their alias.
- No `self as` group exists in the estate, so no file moved.
- Pin: `formatter::import_sorting::e256_an_aliased_self_heads_the_group_after_a_bare_self`, including Organize Imports' output. Planted red.
- One sentence added to grammar.md §3.2.

## B523

**Where the change is:** the analyzer function **`Analyzer::resolve_prepped_local`**, its unresolved-name branch. This is a 9-line change. When the unbound name is `return`, the message is `ForeignSpelling::Return.message()`, word for word. So the code (`foreign-spelling/return`) and editor-46's existing fix (`foreign_spelling_fix`, which writes `ret`) apply unchanged.

**What it covers:** `return;`, `return (x)`, `return -x` and `{ return }`, each with one diagnostic spanning exactly `return`. A program that binds `return` reads it as before.

**Known residue:** `return (y);` as the last STATEMENT of a value body also gets "this body ends without producing a value", which is true of what was written. Filed as B?1.

Pin: `inference::returns::b523_an_unbound_return_is_steered_to_ret` (the four shapes, each fix applied and compiled, plus the bound control). Planted red. No new ledger row: the message is row 611's. One sentence added to `lexical.md`.

## E252

The printer parenthesized an index used as a callee (`(adders[2])(30)`), and the safety net then declined the file. The parser always reads `X[i](args)` as a call of the index, and an author's own parentheses are a `LiftGroup` node that prints them itself, so an index callee now prints as written.

Pin: `formatter::reformats::e252_a_call_through_an_indexed_closure_prints_as_written`, eight shapes checked through `reprint`. Planted red.

**This exposed a gap (N?1):** the first version of this pin went through `assert_formats(source, source)` and stayed green with the bug planted. `format` hands the source back unchanged on a decline, so an identity expectation cannot tell a decline from a clean reprint.

## K28

All 20 fence lines now put `[resource]` on its own line:
- `tour/resources.md` 6
- `guide/persistence.md` 3
- `std/process.md` 4
- `std/reactive.md` 4
- `std/misc.md` 1
- `spec/memory.md` 2

Where a summary aligns a trailing comment, the comment keeps its column. The docs gate and `markdown_golden` are green.

## Not measured

The brief's rule asks a lane that touches an analyzer pass to report kolt instruction counts before and after. I did not measure them:
- `perf_compare.py` refuses a CPU verdict above load 2, and the machine sat at 9 to 25 all session.
- The B523 lines run only on a failed name resolution.
- The loader adds one slice field per module, and per parse one sort of an empty vector.
- The seal's perf leg will cover it.

## New finds (`newitems46-syntax-b.json`)

- **N?1:** `assert_formats(x, x)` identity pins are vacuous when the formatter declines. That is 10 literal calls in `formatter.rs`, plus loops. Rec: have `assert_formats` assert `reprint(source).is_ok()` first.
- **B?1:** the `return (y);` statement cascade described under B523.
- **N?2:** nine comments in `analyzer.rs`, `node.rs` and `inference/modules.rs` still spell `export [..]`. Also, native's `reassigned_closures.vl` binds `let third = adders[2];` only to dodge E252 and can call `adders[2](30)` directly now.

## Needs the owner or the integrator

1. **The owner:** does B536's attribute-order warning become an error in v0.45.0? B536's own rec is yes, once `vilan fmt` has had a release to migrate code.
2. **The owner:** `vilan fmt` now formats a source whose only errors are marker-order refusals; that is how it migrates S3. If formatting an erroring file should stay off, it is a one-line revert in `formatter::parse`. The refusals would then be fixed only by the quick fix.
3. **The integrator, merge notes:**
   - Ledger: one `NEW` row.
   - The marker census golden moves in two commits.
   - `analyzer.rs` changes in two places: the module loader's warning plumbing (B536) and `resolve_prepped_local` (B523). solver-b-46 rebases over both.
   - editor-46 builds the quick fix on `MarkerOrderDiagnostic` and `marker_order_fix`, and publishes the warning's code.
   - CHANGELOG: two BREAKING entries (B536 with S3, and B524).

---

Final message:
- Branch tip `f62d64f0`, six commits, all gates green.
- B536 + S3 (9f6ad451): attributes out of rank warn, `export`/`macro` ahead of them refused, fmt migrates, fix API in place; no kolt patch needed (estate count 0).
- B524 (a6662c91): `async macro fun` is canonical; `macro async fun` steered.
- E256 (4e19c83a): `self as name` sorts after `self`, in fmt and Organize Imports.
- B523 (2ac71f8b): unbound `return` gets the `ret` steer, in `resolve_prepped_local`.
- E252 (8458a5b5): fmt no longer declines `adders[2](30)`.
- K28 (f62d64f0): all 20 book fence lines fixed.
- For the owner: does the attribute warning become an error in v0.45.0, and is fmt formatting a marker-order-refused file acceptable?