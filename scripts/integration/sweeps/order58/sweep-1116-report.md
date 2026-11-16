# Sweep 1116 report (Order 58)

Drafted only; nothing applied. 23 closes, 4 kept open (27 stamped ids still in INDEX.md).

## CLOSE

| id | lane | commit | ancestor of next | in v0.56.0 changelog |
|---|---|---|---|---|
| B718 | emit-58a | 2ff194fb | yes (exit 0; stamp lane shas also checked) | yes |
| B719 | emit-58a | 2ff194fb | yes (exit 0; stamp lane shas also checked) | yes |
| B720 | emit-58b | 98ac8519 | yes (exit 0; stamp lane shas also checked) | yes |
| B721 | emit-58b | 98ac8519 | yes (exit 0; stamp lane shas also checked) | yes |
| B722 | emit-58a | 2ff194fb | yes (exit 0; stamp lane shas also checked) | yes |
| B723 | emit-58a | 2ff194fb | yes (exit 0; stamp lane shas also checked) | yes |
| B724 | emit-58b | 98ac8519 | yes (exit 0; stamp lane shas also checked) | yes |
| B725 | emit-58a | 2ff194fb | yes (exit 0; stamp lane shas also checked) | yes |
| B726 | emit-58a | 2ff194fb | yes (exit 0; stamp lane shas also checked) | yes |
| B731 | owner-ruling | d20bbfd9 | yes (exit 0; stamp lane shas also checked) | no (ruling) |
| B735 | b735-58 | 01aedb35 | yes (exit 0; stamp lane shas also checked) | yes |
| E361 | integrator | ad0add35 | yes (exit 0; stamp lane shas also checked) | no (shipped v0.55.1) |
| F149 | db-58 | 52081c5b | yes (exit 0; stamp lane shas also checked) | yes |
| F151 | http-58 | 9e09acf0 | yes (exit 0; stamp lane shas also checked) | yes |
| F152 | http-58 | 9e09acf0 | yes (exit 0; stamp lane shas also checked) | yes |
| F156 | std-58 | 9e09acf0 | yes (exit 0; stamp lane shas also checked) | yes |
| F157 | std-58 | 9e09acf0 | yes (exit 0; stamp lane shas also checked) | yes |
| F158 | std-58 | 9e09acf0 | yes (exit 0; stamp lane shas also checked) | yes |
| F160 | poll-58 | 095164d9 | yes (exit 0; stamp lane shas also checked) | yes |
| F163 | peer-58 | 46ff5439 | yes (exit 0; stamp lane shas also checked) | yes |
| F164 | bind-58 | 47650db8 | yes (exit 0; stamp lane shas also checked) | yes |
| M175 | db-58 | 52081c5b | yes (exit 0; stamp lane shas also checked) | yes |
| M195 | db-58 | 52081c5b | yes (exit 0; stamp lane shas also checked) | yes |

## KEEP OPEN

| id | reason |
|---|---|
| B705 | emit-58a fixed the mutating-call-with-receiver-read shape, but the stamp says STILL OPEN: the original shape, a `let v = &mut xs` view held across a later read of `xs`. The changelog entry covers only the fixed shape. |
| B732 | Note only (a minimal repro exists); not fixed. |
| F1 | Arc item; chunk 0, S1b and M2 landed, further slices remain. |
| M199 | Partial: viewed-only patterns borrow in place (merged @20b9fc49), but kolt's word_list() return shape is unchanged natively (0.498 s) and the copy at a return stays until M201. |

## Named in the changelog, not stamped

- B709: changelog heads name it only through B719's text; the item itself says SHIPPED in v0.55.0 (tag fc9efaa1) but is still a row in INDEX.md. Looks fully done (probably missed in the v0.55.0 sweep) - a human should confirm and close.
- M202: item says "REMAINING: about +0.09% recording cost on element-dense programs; explain the examples' +0.1%". Not done; keep open.

## Inconsistencies / human look

- B731 and E361 have no v0.56.0 entry by design; B731 has no commit, so its `commit` field is the release head d20bbfd9 (placeholder; edit if you prefer another value). E361's commit is the fold ad0add35 (tag 00f7daa3 is on release/0.55).
- The emit-lane stamps say "merged locally @2ff194fb / @98ac8519"; both are ancestors of next, so they were kept as given.
- B720 is closed on the emitter fix, but its analyzer cause B727 remains open (confirm B727 is a real INDEX row, it is).
- F156 is closed although the fs File handle tier and the watcher stay refused natively; check those have their own items.
- F164 and M199 each carry an earlier stamp (CI note / PARTIAL FIX) superseded by later ones; no disagreement found. B709's open state contradicts its SHIPPED stamp.
