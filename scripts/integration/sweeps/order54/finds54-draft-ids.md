# Order 54 finds: real ids, sections, filing notes (draft for the integrator; PASS 1 + PASS 2 (incr-54c, fmt-54 appended))

Method: every `newitems54-<lane>.json` for the eight MERGED lanes (papers-54, editor-54, std-54, debug-54, native-54, incr-54a, solver-54, incr-54b) was turned into `filed/spec54-<lane>.json` with REAL ids, checked against file_items.py's own rules by a read-only re-implementation (required fields, id starts with its section letter, no existing item/INDEX row/tombstone, no unescaped pipe in title or discussion, section heading exists, no leftover `X?n` placeholder anywhere). No scripts were run. Fixes applied to the lanes' files: three titles carried an unescaped `|` inside backticks (incr-54a B648, native-54 N180 twice) and were escaped to `\|` (papers-54's B643 already had it); papers-54's F?3 cross-references to its own B?2 now say B644; the fixed finds' status fields say FIXED (they are closed on arrival); E332's status/body carry the narrowing note.

Maxima at the start (INDEX + items + archive tombstones): A173, B642, E331, F143, M161, N178 (matches Order 53's end). Sections without finds are untouched.

File ONE lane at a time in this order (ids are distinct across files, so the order is only for tidiness): papers-54, editor-54, std-54, debug-54, native-54, incr-54a, solver-54. incr-54b has NO new items (its file is `"items": []`; no spec written).

## Next free id per section (after pass 2)

| section | next free |
|---|---|
| A | A174 |
| B | B652 |
| E | E340 |
| F | F148 |
| M | M164 |
| N | N183 |

Pass 2 consumed B650-B651, E337-E339, M163, N182 (incr-54c then fmt-54, in that order).

## Allocation table

| lane | placeholder | id | sec | title (short) | filing note |
|---|---|---|---|---|---|
| papers-54 | B?1 | B643 | B | `process::scan()` answers "" on EVERY call on the JS backend since v0.33.0: the `__scan` helper calls `require("fs")` inside the emitted ES module ... | file, then CLOSE ON ARRIVAL (fixed by std-54, merge ed729e58) - closes54-draft-on-arrival.json |
| papers-54 | B?2 | B644 | B | A `for x in subject` whose `next` reads a context - any std IO wait (`time::sleep`, through `ambient_signal()`), or `task::ambient_signal()` itself... | file, then CLOSE ON ARRIVAL (fixed by solver-54, merge 68666705) - closes54-draft-on-arrival.json |
| papers-54 | F?3 | F144 | F | Native: a `for x in subject` over a type whose INHERENT `next(self): Option<T>` awaits (the checker accepts it - spec §3.5's iteration protocol) is... | file, then CLOSE ON ARRIVAL (fixed by native-54, merge a6a1d983) - closes54-draft-on-arrival.json |
| papers-54 | F?4 | F145 | F | The native backend implements `process::env` but refuses `scan` (intrinsic `Scan`), `args` (intrinsic `Args`), `exit` and `cwd` (host bindings `pro... | file, then CLOSE ON ARRIVAL (fixed by std-54, merge ed729e58) - closes54-draft-on-arrival.json |
| papers-54 | E?5 | E332 | E | std has no way to write to stdout WITHOUT a newline: `io::print` is `console.log` (JS) / `println!` (native) and there is no other stdout door, so ... | file OPEN, narrowed (prompt(text) shipped in S1; the general io::write closes with A173 S2) |
| papers-54 | N?6 | N179 | N | Under `VILAN_STD_PREFIX=on` the phase census prints `prefix-world 0 prefix-refusal -` for a program that silently does not take the prefix (8 corpu... | file; XS census legibility |
| editor-54 | E?1 | E333 | E | a generic enum's variant as a LIST or TUPLE element or as a method receiver hovers bare - `Some` in `[Some(1), None]`, `(Some("a"), 2)` and `Some(4... | file; next editor lane (rec yes) |
| editor-54 | E?2 | E334 | E | the `#[ignore]`d E126 gate `keystroke::gate::the_view_exhibit_tracks_the_recorded_application_shape` fails on its own generated exhibit: `Combine<(... | file; to keystroke.rs's gate owner, run at the base first (rec yes) |
| std-54 | B?1 | B645 | B | A `void` `main` whose TAIL is a void-typed expression - a `match` of void arms, a call written with no `;` (`print("x")`) - is emitted on JS with `... | file, then CLOSE ON ARRIVAL (fixed by native-54, merge a6a1d983) - closes54-draft-on-arrival.json |
| std-54 | F?2 | F146 | F | A native program parked on `read_line`/`prompt` burns CPU while it waits: ~0.12 s of CPU per 5 s of a silent, open stdin (~2.4 %, debug build) agai... | file; S2's key loop needs it |
| std-54 | E?3 | E335 | E | SIGTERM to `vilan run` does not reach the program it started: node (or the native binary) keeps running, orphaned - a supervisor, an editor task or... | file; run's child gets the signal, exit 128+n |
| debug-54 | B?1 | B646 | B | `[track_caller]` is refused on every trait member, so the reactive trace (E257 S8) cannot name where a cell made by `Signal::new` was made, where a... | file; a RULING for Order 55 (rec yes: track_caller as part of a trait member's contract) |
| debug-54 | E?2 | E336 | E | vilan-dap names a std frame by V8's own inference, not by its vilan function: a closure std passes to `with_finally` shows as `running_wake.v`, oth... | file; XS-S, use the map's names |
| native-54 | F?1 | F147 | F | `Option::take` / `Option::replace` over a receiver that lives in a cell natively — a module-level binding (`module_maybe.take()`), a field of one, ... | file, then CLOSE ON ARRIVAL (fixed by native-54, merge a6a1d983) - closes54-draft-on-arrival.json |
| native-54 | B?2 | B647 | B | A callee that WRITES a module-level `mut` binding it was handed a loan of answers differently: `lent_and_grow(&module_items)` (the callee pushing i... | file; checker refusal, diagnostics, estate first (solver-54 if time, else Order 55); NOT covered by solver-54's B639 (that is a later ARGUMENT writing a lent place) |
| native-54 | N?3 | N180 | N | A by-value read of a module-level binding at a consuming position was copied TWICE natively: `has_N((MODULE_ITEMS.with(\\|cell\\| cell.get())).clon... | file, then CLOSE ON ARRIVAL (fixed by native-54, merge a6a1d983) - closes54-draft-on-arrival.json |
| incr-54a | M?1 | M162 | M | Every wired method call's member reference (`wire_method_call`'s span-less `Expr::Local(member)`) rode EVERY R11 instantiation's candidate slice as... | file, then CLOSE ON ARRIVAL (fixed by incr-54a, merge 5d2a077a) - closes54-draft-on-arrival.json |
| incr-54a | B?2 | B648 | B | `ConstWorld::prepare` REPLACED a const site's reach with its prelude's when the prelude's walk required code: `const twice(add(1))` beside `const l... | file, then CLOSE ON ARRIVAL (fixed by incr-54a, merge 5d2a077a) - closes54-draft-on-arrival.json |
| incr-54a | N?3 | N181 | N | `vilan check .` on kolt (two legs) is not instruction-deterministic: identical runs of one binary read 13.04 / 13.41 / 13.54 / 13.62 G instructions... | file; measure one leg at a time |
| solver-54 | B?1 | B649 | B | A VIEW of a scalar handed to a BY-VALUE parameter checks clean and answers differently on the two backends - `numbers.contains(&2)`, `numbers.index... | file; refuse with a 'drop the &' steer after the estate count (rec yes, Order 55) |

Cross references resolved: papers-54 F?3 (F144) -> its B?2 is B644; solver-54's and native-54's fixes of papers-54/std-54 finds are recorded in the on-arrival texts (B644 by solver-54 68666705; F144 + B645 by native-54 a6a1d983; B643 + F145 by std-54 ed729e58). The close texts of F143 (-> B647), E328 (-> E333, E334) and M155 (-> M162) in closes54-draft.json name the real ids, so file BEFORE closing.

## On-arrival closes (9)

`closes54-draft-on-arrival.json` (real ids, no placeholders, close_batch shape): B643, B644, F144, F145, B645, F147, N180, M162, B648. Procedure: file_items for the lane specs first, then close_batch (it needs the item file and INDEX row). Note that B645 is std-54's find fixed by native-54; B644 is papers-54's find fixed by solver-54.

## Counts

Finds filed: 20 (papers-54 6, editor-54 2, std-54 3, debug-54 2, native-54 3, incr-54a 3, solver-54 1, incr-54b 0). By section: B 7 (B643..B649), E 5 (E332..E336), F 4 (F144..F147), M 1 (M162), N 3 (N179..N181), A 0. Closed on arrival: 9. Left open: 11 (B646, B647, B649, E332, E333, E334, E335, E336, F146, N179, N181).

## Not filed / skipped

None skipped: every find in the eight files is allocated. incr-54b: no finds (its two design deviations from the paper are in the paper's 'As built at C2' paragraph).

## PASS 2 (incr-54c, fmt-54)

Specs: `filed/spec54-incr-54c.json` then `filed/spec54-fmt-54.json` (file in that order). Pipe escapes in titles checked; no leftover placeholders.

| lane | placeholder | id | sec | title (short) | filing note |
|---|---|---|---|---|---|
| incr-54c | B?1 | B650 | B | S3b's cold async seed counted a value a HOT module assigned into a cold binding | file, then CLOSE ON ARRIVAL (INCR54C, fixed with M138's seeded form) |
| incr-54c | B?2 | B651 | B | a std NAMESPACE the import names was not part of the prefix key (wrong diagnostic over a shared prefix) | file, then CLOSE ON ARRIVAL (INCR54C, 376c94b7) |
| incr-54c | M?3 | M163 | M | M156 measured: const pass reaches 0 of ~300 drop roots but the soundness gate cannot be checked at plan time; doors (a)/(b)/(c) | file OPEN (design question; rec (c) this order); M156 is STAMPED, not closed |
| incr-54c | N?4 | N182 | N | first analysis over a LOADED prefix examines ~390 more impl rows (derived index rebuilt once per process) | file OPEN; Order 55 beside P6 |
| fmt-54 | E?1 | E337 | E | a call followed by `!`/`?`/a field never breaks its arguments | file OPEN (S, next order) |
| fmt-54 | E?2 | E338 | E | a call inside an element hole is measured without the hole's `}` | file OPEN (XS; ask at the sweep whether the hole's `}` counts) |
| fmt-54 | E?3 | E339 | E | binary right operand vs the call statement's `;` (101-column asymmetry) | file OPEN as a design question, owner rec KEEP; E330's close names it |

Pass-2 counts: 7 finds (B 2, E 3, M 1, N 1); 2 on-arrival closes (B650, B651); 5 open (E337, E338, E339, M163, N182). Totals after both passes: 27 finds, 11 on-arrival closes, 16 open.

## Merged one-shot files

`closes54.json` (35 closes = first pass 16 + first-pass on-arrival 9 + E331 + second pass 9 [M138, M158, B635, N157, E329, E325, E330 + on-arrival B650, B651]; ids unique; tokens `INCR54C` and `FMT54` remain in `commit`) and `stamps54.json` (7 stamps: E292 [incr-54c rows appended], E257, A173, M157, L24, M156, M36). Order: file_items per lane (papers, editor, std, debug, native, incr-54a, solver, incr-54c, fmt) -> close_batch closes54.json (it checks item files wholesale, so ALL on-arrival ids and E339 must be filed first) -> stamp_items stamps54.json. The component drafts are kept.
