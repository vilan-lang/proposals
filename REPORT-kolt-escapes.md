# Review: the `kolt-escapes` tracker items (2026-10-26)

> 2026-10-26, after the review: APPLIED. M662→M165, M666→M166, M668→M167, M669→M168, M674→M169, M675→M170, M676→M171, M678→M172; B672 folded into B652, B673 into B661 (tombstoned); INDEX rows moved to their sections; the review notes below added to B652, B661, B664, B667, M167, M172 and A72; kolt's three comments updated; `kolt-escapes` fast-forwarded onto `main` (not pushed). Ids below are as filed.

Thirty items filed 2026-10-19 → 10-24 on the proposals branch `kolt-escapes`
(worktree `.claude/worktrees/kolt-escapes`, 30 commits ahead of `main`, fast-forward
clean). Not on `main`, not in `INDEX.md` there, not in the Order 55 queue
(tracker/chronicle.md:2882). Kolt itself: 168 commits 10-17 → 10-24 on vilan 0.52.0.

## Verified on 0.52.0 (d18f50d8)

Reproduced as filed: B652, B653, B654, B655, B657, B658, B659, B660, B663, B664 (package
form), B667, B670, B671, B673, B677, M666. Read in std source and confirmed: M662
(`List<any>` at db.vl:67–98), M664/M676 (dom.vl:741 has only `prevent_default`),
M668 (router.vl:90/111 write `""`), M669 (http.vl:610 `listen(port, cb)`; build.vl:152),
M674 (no `position` on `Iterator`/`List`), M678 (mirror.vl:1524/967), A174 (no
`Connection::close`; `revoke` at rpc.vl:3036 is internal), M164 (http.vl:133
`read_request_bytes` whole). Not re-run: B656, B661 (same as B673), B665, D16.

## Corrections to the items

1. **B652 is not a JS-emitter bug.** `vilan run --backend rust` prints `4 9 11` too. The
   lexer never decodes `\x..` / `\u{..}`; both backends re-escape the raw text. Retitle
   (lexer, both backends) and drop the "two emission paths" reading — the
   context-dependent `"́"` case may still be an emitter detail, pin it separately.
2. **B672 duplicates B652** (the `\u{10FFFF}` case is B652's second line). Fold B672's
   "reject unknown escapes" door into B652 and tombstone B672.
3. **B673 duplicates B661** (same parse, same two asks). Fold, tombstone B673. B518
   (closed, Order 46) fixed the *printer* for this type; the parser hint is new.
4. **B664**: single-file `impl X with PartialEq` reports the right span. The loss is
   package-only (three-module repro: no span at all). Say so, so the fix targets the
   package path.
5. **M678** names the right structures (`StoreMint.holds: Shared<List<MintHold>>`,
   `MirrorView.slots: Shared<List<ClientSlot>>`) but the same read-copy-and-rebuild
   pattern is also on the server side: `release_slot` (`slots: Shared<List<MirrorSlot>>`,
   mirror.vl:599) and `release_grant` (`grants`, :616). Four lists, not two.
6. **B667** is a sibling of B191 (closed Order 26: a let-bound self-call deadlock);
   cite it.
7. **M668** is a third face of A72 (router; `navigate_replace` was built at Order 39).
   Keep it standalone (it is a different ask) but cross-link.

## Numbering

The tracker numbers per section (A173, B651, E339, M163, N182 on `main`). The branch
files A174, M164, D16 and B652–B661 by that rule, then from 10-20 switches to a shared
counter: M662, B663, B664, B665, M666, B667, M668, M669, B670–B673, M674–M676, B677,
M678. Kolt source cites M666, M675, M676, B677 and B652. Decide before merging: renumber
M662/M666/M668/M669/M674/M675/M676/M678 → M165–M172 (and B663.. keep: the B run is
contiguous) and fix the five kolt comments, or accept the gap. Uniqueness is all
`backlog <ID>` needs, so either works; the INDEX order looks odd with M164 beside M662.

## By weight

Silent wrong behaviour (fix first):
- B652(+B672) escapes, both backends — lexer, S.
- B653 duplicate field in a struct literal — checker, S.
- B655 `struct` inside `impl` dropped — parser, S (pin enum/trait/impl/mod too).
- M666 derived `FromJson` refuses a missing `Option` field — json.vl:965, S. Breaks every
  stored JSON on a schema add.
- M662 `std::db` binds `Option`/struct → throws; an `[rpc]` body that throws never
  answers (second bug, rpc server `accept_socket` task). Boundary conversion S now;
  `SqlValue` typing M is an owner call.
- B677 the silent owner trap (the 12 s freeze with M678). Diagnostic half S; the design
  half (warn when a plain closure parameter builds under a context body, or default
  `|…| View` parameters to the call-time owner) needs a ruling.

Performance: M678 quadratic holds/release — M, rpc/mirror.vl; four lists to key by id.

Robustness / security (std, M each): M164 unbounded request bodies (`max_body_bytes` +
lazy read first), A174 no revoke/close (door 2, `Connection::close`, is the S half),
M669 bind address (S) + `require_build` beside the module (S).

Inference (checker, S each): B659 (literal `i32` default beats the sibling closure's
result; two shapes), B667 (self-call in a match arm), B670 (binary-op result on an
inferred parameter is `unknown`).

Parser diagnostics (S each, one lane): B654 (multiline attribute string — or accept it,
rec), B656, B657 part 1, B658, B660, B661(+B673), B663, B664, B665 (const-eval site).

Tooling: B671 fmt declines a `match` statement with valued arms and names the wrong
line — with E337–E339.

API gaps, std S: M674 `position`, M676 `stop_propagation`, M668 history state.
M675 (empty `View` + a keyed owner scope with no view) is S–M and a design door.

Docs: D16 (the tour and gotchas contradict B231).

Owner rulings needed: B657 part 2 (struct update `..base`), M675's door, B677's design
half, M662's typing, A174 door 1 vs 2, M164's default cap, M669's lookup rule, the
numbering.

## Suggested Order 55 shape

parser-55 (Sonnet/Opus): B652, B653, B655, B654, B656, B658, B660, B661, B663.
solver-55: B659, B667, B670, B664, B665.
std-55: M666, M662 (boundary), M674, M676, M668, M669, D16.
rpc-55 (Fable, the one high-complexity lane): M678, B677 diagnostic + paper, A174 door 2.
http-55: M164 (cap + lazy body).
fmt-55: B671 with E337–E339.
