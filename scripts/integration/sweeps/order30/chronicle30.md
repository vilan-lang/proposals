MERGED (fifteen lanes, in the order they landed): rpc-paper-30 (12b3b75d; proposals only, transport-rpc
§9 with rulings R1–R7 and R-A38b), dom-30 (3ab3004d), b258 (46e4c400; the mdBook golden regenerated
above it), hygiene-30 (2f99e32d), std-30 (78f696d0; the golden again), build-30 (c9e238eb; macros.rs
resolved by hand — N63's path move under M51's per-flush temp), editor-30 (f2b9ce9f; the DOM stub
hand-unioned, its `find()` brace restored), rule1-30 (c517395f; the copy-elision census regenerated,
322), solver-30 (4bef4ead), m19-t1d (a85370ca; a duplicate `Event::target` removed), smalls-30
(3c161046), view-30 (3a1cdea6; `ui_rows.rs` rebuilt function-level from the three real versions),
perf-30 (2db51d7a), css-30 (9d3a8d86; `RULE_STATEMENT_SITES` 20 → 21), fmt-30's rules (dc39bf75) with
the reformat regenerated over the merged tree LAST (88147380: 6 files, lines over 100 columns
107 → 105). Seventy-one commits, 116 files, +14,192/−1,005. Ledger rows 400–406 assigned (132 and 355
edited in place, 360 deleted; next 407); CHANGELOG parity 270/270.

SEALED 2026-09-08 at c3ed9239 (88147380 plus one seal repair: the LSP's add-import quickfix pin
re-aimed at the `View` type, because B270 made the element head hygienic and no lane gate ran
vilan-lsp): union 6847/6847 (21 skipped) at c3ed9239; clippy, the Windows cross-check, audit and fmt green locally;
CI GREEN on all eleven jobs (run 34246342479: ubuntu and Windows partitions as listed in notes30.md; the run at 88147380 was superseded by the repair push). The
order's verdicts: the MISCOMPILE — B258's silent `undefined` through an inherited field had its
root in the context pass (`known_receiver_candidates` shared across receivers), fixed with the
default override emitted and the miss REFUSED rather than emitted (B279 asks for the structural
guard); the RULE 1 LANDING — B267's cell-aware last-use elision put B256's place treatment within
noise on the reactive pins, so `Shared::read()` is a place and storing one copies (B274 found the
docs' `read().push` promise unmet — an owner ruling); the CSS BLOCK MADE USABLE — B270's hygienic
seed (`Node::StdItem`: the block means `std::style::style` and an element `std::ui::view` whatever
the scope holds, neither needing an import), the auto-`const` (A68), chain links (A69), the style
prelude ambient inside a block (A70, itself an A65 module directory), typed holes through `piece`
(A34) and the `:hover` steer with a versioned CSS property index for completion (E153); kolt's
`button_style_base` 392 → 260 characters; A64 ruled in §15 (`.when` for a rule-set change, CSS
variables for a value change); the RPC PAPER — §9 answers the owner's three points with the
per-connection instance that already exists (A38's factory), return-typed signal handles as the
unbuilt half of §8, and client-declared functions; the sketch's `&mut self` REFUSED by the
generator and `mut self` silently losing writes is B272; the CHILD CONTRACT — a `Source` of `str`,
`View` or `List<View>` may be a child (B268's root: bound arguments dropped at impl matching),
`toggle_attr` for boolean attributes (A66), `show` writing inline display (A60); std and dom grown
by kolt's externs (`Storage` typed, `Event::code/target/current_target`, `parse_bool`, `Debounce`,
`DomRect`, `PathParts` with `FromPath`) so twenty-one hand-written externs and three FIXMEs can
leave kolt; the SOLVER — B261/B262/B263 with the diagnosis of B263 corrected in the fixing, and an
UNSOUND impl `with` clause found unchecked (B273); the EDITOR — an alias in type position renames
alone (B264, per TypeScript), the namespace's nowhere-to-point (E152), `autofocus` retried across
frames (B271); the FORMATTER — `for`/`match` heads split (E150) and the element-head attribute
sorter (E151) with its evaluation-order bargain stated (E156, an owner ruling); PERFORMANCE — R10
in the Class A window (M48: 153,302 → 24,459 sites, kolt keystroke thread CPU 280–340 → 60–70 ms),
tiered legs (M51: kolt wall 23.8 → 15.7 s), M53's −8.2% Ir cold and −12.9% warm, M52's union key
measured and REFUSED (the browser leg is 82% of base — M55 names where the headroom is); HYGIENE —
N59–N64 done (caches under `dist/.cache/`, N61's wall-bound sweep, the ledger's rule-site count).
Forty-four closes; twenty-eight filed (B272–B280, A71–A73, E154–E158, M54–M59, N65–N69); M19 and
A53–A56 carry status updates; prose ledger row 406 written, rows 132 and 355 edited.

PROCESS:
- The seal found what no lane gate ran: B270's element hygiene killed the LSP's only pin of the old
  element-import behaviour, in a package (vilan-lsp) outside css-30's `--test` list and outside
  its whole-suite run's timing. Rule: a lane that changes WHAT a diagnostic fires on runs
  `-p vilan-lsp` too (the quickfix and steer pins live there); the merge helper's gate list is per
  lane, and the seal's union is the floor.
- The mdBook golden went red twice (dom-30's routing section under b258's merge; hygiene-30's
  reserved-words section under std-30's) — the merge helper now regenerates it for any merge that
  touches `vilan/docs/`.
- The merge helper's target validator refused a lane-added binary (hygiene-30's
  `reachability_and_depth`) and then my own wrong crate for `release_emission`; it accepts files on
  the lane branch now, and the crate table is in the mechanics block.
- Two hand unions of `ui_rows.rs`'s DOM stub: the first dropped `find()`'s closing brace (the hunk
  cut mid-method) and redded every ui_rows test with a JS SyntaxError; the second (view-30) broke a
  delimiter and was rebuilt FUNCTION-LEVEL from the three real versions with the fold helper's own
  extractors. Rule: `node --check` of the extracted stub before the amend; an edited shared CONST
  is a hand union, never a fold.
- Two lanes given overlapping members in one file (dom-30 and std-30 both declared `Event::target`
  in dom.vl) merged cleanly and failed the full-scan pin; a named owner per member in the brief.
- css-30's 21st curated rule met hygiene-30's rule-site count (20): the pin doing its job; a lane
  adding a parser rule statement bumps `RULE_STATEMENT_SITES`.
- The copy-elision census conflicted a third order running (rule1-30): regenerated over the
  merged tree, 322.
- My CI watcher looked in the proposals checkout for a vilan run (a persisted cwd) and missed a
  run that appeared after its first two minutes of polling; the watcher pins the repository and
  reads the run list until the id appears.
- No `git stash`, no pattern kills, no 1Password outage this order. notes30.md is the record.
