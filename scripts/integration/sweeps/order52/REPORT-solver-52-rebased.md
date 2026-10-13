## solver-52: rebased onto origin/next 15a12456, every gate green

I rebased `solver-52` onto 15a12456 and the full gates pass on the new tip. Nothing is pushed, and none of my processes are running.

**New tip `fb9dc56e`, base `15a12456`** (previously 6ef61d58 on C1). The rebase applied cleanly.

### Commits
| commit | item | family |
|---|---|---|
| 85834bc2 | B620 (analyzer half): an element head admits only methods that hand the element back | fix (estate 0) |
| 9ab0ed0d | E309: a spaced generic call gets one steer naming the spacing | diagnostics |
| 8e4220b0 | B617: a `dyn` slot's body-less declaration threads its union's contexts | miscompile |
| fb9dc56e | B620 slice 2: the head mark sits on the link's member, so a head nests no deeper than its chain | fix (adds a sentence to B620's entry) |

**CHANGELOG parity:** `## Unreleased` has 36 bold heads and 36 family markers, which is next's 33 plus my 3. editor-52's "B620 (editor half)" entry is kept separate from mine.

### Both intents carried, with editor-52's element work
- editor-52's E303/E305 code reads element links from the source text (`written_types.rs`'s `element_link`) and from the zero-width spans of the event and attribute names. It never reads a member's node shape.
- My mark sits on the head link's member only (`Node::ElementHeadLink`), and every reader of a member's shape strips it first (`unmark_head_link`).
- So head links still get no hints, the event and attribute names are still minted as literals, and the analyzer still refuses non-View methods in a head.
- Re-probed after the rebase:
  - `<div .len() />` is refused once.
  - `pick <f64>(1, 2)` gets one steer.
  - The B617 probe prints the same six lines on JS and natively.
- I did not touch incr-52b's `impl_subject_admits` fix.

### Gates at fb9dc56e
- **Full suite** (`--cargo-profile ci-test -E 'not binary(deep_nesting)' -j 6`): 10601/10601 passed, 38 skipped.
  - Within it: `inference` 5535, `docs` 12, `diagnostics_ledger` 25, `ci_ignored_pins` 12, `hygiene` 3, `corpus` 14, `check_scope_differential` 16, `native_differential` 279, vilan-lsp binary 443.
- **Native sweep mode** (`VILAN_NATIVE_DIFFERENTIAL=1`): 279/279, 1 skipped.
- **Deep-nesting canary at 1536 KiB:** 18/18.
- **clippy** (`-D warnings`), **`cargo fmt --check`**, **`vilan fmt --check .`:** all 0.
- **`ci-local.sh perf`:** T2 green, growth x1.928. kolt late-writes=0.
- **kolt cold-check RSS:** median 276,600 KB at tip vs 278,048 KB for 0.49.0 (-0.5%). That is the same base I used before the rebase; there is no 15a12456 release binary to compare against.
- **kolt copy check:** 0 errors.

### Unchanged since the first hand-back
The functions changed, the finds (`newitems52-solver-52.json`: E?1 and E?2), and the owner questions are all the same.

**One suggestion for editor-52 (not done here):** `element_link` could check `element_head_links` instead of inferring a head link from the text. The text test gets one shape wrong: a head item whose attribute value is itself an element, such as `title(<b/>) .f()`.
