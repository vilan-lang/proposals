# Order 54 finds: real ids, sections, filing notes (draft for the integrator; PASS 1 of 2)

Method: every `newitems54-<lane>.json` for the eight MERGED lanes (papers-54, editor-54, std-54, debug-54, native-54, incr-54a, solver-54, incr-54b) was turned into `filed/spec54-<lane>.json` with REAL ids, checked against file_items.py's own rules by a read-only re-implementation (required fields, id starts with its section letter, no existing item/INDEX row/tombstone, no unescaped pipe in title or discussion, section heading exists, no leftover `X?n` placeholder anywhere). No scripts were run. Fixes applied to the lanes' files: three titles carried an unescaped `|` inside backticks (incr-54a B648, native-54 N180 twice) and were escaped to `\|` (papers-54's B643 already had it); papers-54's F?3 cross-references to its own B?2 now say B644; the fixed finds' status fields say FIXED (they are closed on arrival); E332's status/body carry the narrowing note.

Maxima at the start (INDEX + items + archive tombstones): A173, B642, E331, F143, M161, N178 (matches Order 53's end). Sections without finds are untouched.

File ONE lane at a time in this order (ids are distinct across files, so the order is only for tidiness): papers-54, editor-54, std-54, debug-54, native-54, incr-54a, solver-54. incr-54b has NO new items (its file is `"items": []`; no spec written).

## Next free id per section (reserved for pass 2: incr-54c, then fmt-54)

| section | next free |
|---|---|
| A | A174 |
| B | B650 |
| E | E337 |
| F | F148 |
| M | M163 |
| N | N182 |

Pass 2 notes: fmt-54's `newitems54-fmt-54.json` already exists (E?1, E?2, E?3 -> three E ids) and would take E337..E339 if incr-54c files no E item; merge order is incr-54c then fmt-54, so allocate incr-54c first. incr-54c's finds (M138's seeded form is M138 itself; its likely finds are M/B/N) continue at M163 / B650 / N182. closes54-draft-second-pass.json (E330) references fmt-54's E?3: replace the wording with the real id once allocated.

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
