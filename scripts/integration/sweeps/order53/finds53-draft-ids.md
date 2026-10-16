# Order 53 finds: placeholder ids, sections, filing notes (draft for the integrator)

Method: every `newitems53-*.json` was checked with file_items.py's own rules, read-only (required fields present, id starts with its section letter, no unescaped pipe in title or discussion, a section heading exists in INDEX). **No file needed a fix**: no `Q` sections, no pipe problems, no missing fields. `filed/newitems53-<lane>.json` are therefore byte-identical copies of the originals (lane names are the files' own: debug-53, editor-53, fmt-53, incr-53a, incr-53b, incr-53c, native-53, solver-53, std-53). Nine files, 30 finds (the brief said twelve files; Order 53 has nine lanes with finds, there is no tools/seal file).

Placeholders collide ACROSS files (`E?1` is in four files, `B?1` in four): file one lane at a time, or allocate real ids per lane before merging into one spec. In-body cross references to placeholders: incr-53a M?3 names "E?1" (its own E?1); incr-53c M?2 names "M?1" (its own); solver-53 B?3 names "native-53's B?2" (a DIFFERENT file); std-53 A?1 names its own B?1. Fix those by hand after allocation (not done: "do not rewrite content").

Current max id per section (INDEX + items + archive): A172, B634, E322, F141, M152, N177 (the next free number is one above).

| file (lane) | placeholder | section | title (short) | filing note |
|---|---|---|---|---|
| debug-53 | E?1 | E | vilan-dap shows a type with a written Debug impl by structure (sidecar names no function) | file; Order 54 beside S8 (owner rec yes) |
| debug-53 | E?2 | E | vilan-dap prints a dyn binding as `dyn Area(<?>)` when the program prints nothing (no show slot) | file |
| debug-53 | E?3 | E | fmt moves a trailing comment after a one-line if/else into the then-branch | file (area Editor; a formatter bug) |
| debug-53 | E?4 | E | vilan-dap shows no async parent frames (S8 prerequisite) | file |
| editor-53 | E?1 | E | module segments of a qualified pattern / struct initializer paint nothing | file |
| editor-53 | E?2 | E | a generic enum's payload variant in value position hovers without its payload | file; next editor lane (owner rec yes) |
| editor-53 | M?1 | M | E317's label scan costs ~+0.5% instructions per keystroke; fold into M148's rows | **FIXED by incr-53a (M148 (2), 6fe278ca): file, then close on arrival** (closes53-draft-on-arrival.json) |
| fmt-53 | E?1 | E | a call statement exactly 100 columns before `;` stays on one 101-column line | file; XS, next order |
| fmt-53 | E?2 | E | a two-operand chain with a call operand breaks the call's arguments while `&&` stays inline | file (layout question; kept for now, owner rec yes) |
| incr-53a | E?1 | E | E318 as ruled is unsound (const pass emits through the transformer; drop plan feeds the call graph) | **RECOMMEND DO NOT FILE**: E318 is closed as unsound (closes53-draft-unsound.json) and its close text carries the doors; M?3 below reads "E?1" as E318. If filed anyway, close it on arrival |
| incr-53a | M?1 | M | E145 alias spans + type-reference labels rendered over every file every analysis (~11-15 ms) | file; next editor row, in M148's shape |
| incr-53a | M?2 | M | R11's three span indexes over the whole world (7.5-14 ms) | file; the R11 paper (incr-53c) is its context |
| incr-53a | M?3 | M | plan_resource_drops re-plans every enrolled body per keystroke (5-9 ms) | file; body says "after E?1" (read: after E318's const-reach question) |
| incr-53b | M?1 | M | package item ids differ between the prefix shape and the canonical shape (std-prefix 4.2; P6) | file; owner rec: paper it as P6 |
| incr-53b | N?1 | N | the world cache grows unpruned (P4) | **FIXED by incr-53c (P4, 69b607bd): file, then close on arrival** |
| incr-53b | M?2 | M | the prefix file carries no M19/S2 records (std-prefix Q9) | file; Order 54 with P5 |
| incr-53c | M?1 | M | a LONE open document's keystroke is never seeded, so M110 S3's record is unread on the common row | file; rec (b) a Workspace flag |
| incr-53c | M?2 | M | M138's seeded adaptation, carried (three parts) | file; body names its own M?1 |
| incr-53c | M?3 | M | M133's residue: platform coloring fans out at two dispatch shapes (A165's arm still 5.4 M) | file; Order 54 |
| incr-53c | M?4 | M | M147 residue: per-site globals copy in reach_from/prepare | file; small |
| incr-53c | B?1 | B | context::apply's canonical order is cold-first per section (latent determinism, no instance) | file; XS |
| native-53 | F?1 | F | closure-VALUE call arguments rooted at a captured binding copied in the wrong order natively | **FIXED in native-53 (41e7a705; merge b529975d): file, then close on arrival**; status field already says FIXED |
| native-53 | B?2 | B | a `&mut` receiver over an uncaptured binding beside a later argument that RE-BINDS its root checks clean | **FIXED by solver-53 (e9c08894; merge c5b59f0f): file, then close on arrival** (re-bind only; the in-place twin is solver-53's B?3) |
| native-53 | F?3 | F | a module-level `mut` binding beside a later argument that writes it differs JS vs native | file; follows F138's order on both backends (owner rec yes) |
| solver-53 | B?1 | B | B627 residue: `take(make().unwrap_or(5))` still "cannot infer" | file (area Type inference) |
| solver-53 | B?2 | B | a generic struct literal no field grounds, settled by a later annotation, runs on JS and is refused natively | file (NOT native-53's B?2; section B though area says native targets) |
| solver-53 | B?3 | B | in-place twin of native-53's B?2: `log.items.push({ log.items.push(1); 9 })` checks clean, rustc E0499 | file; widen the lent-root check next order (owner rec yes); title names native-53's B?2, fix the reference to the allocated id |
| solver-53 | B?4 | B | B627 residue: undetermined static as an unannotated tail is an internal error on JS | file; XS-S |
| std-53 | A?1 | A | an expected type does not reach a call's own generic through a method on its result | **FIXED by solver-53 with B627 (af6ea4ea; merge c5b59f0f): file, then close on arrival.** Note solver-53's B?1 is the residue. Section A is std-53's choice (area Type inference); a B placement would sit beside B627 - your call, the id letter must match the section |
| std-53 | B?1 | B | B424's "cannot infer" fix-it spells a METHOD call's fix as a free call | file (not fixed by solver-53) |

## Counts

By section (30 finds as written): A 1, B 7, E 9, F 2, M 10, N 1. By file: debug-53 4, editor-53 3, fmt-53 2, incr-53a 4, incr-53b 3, incr-53c 5, native-53 3, solver-53 4, std-53 2.

Recommended filing: skip incr-53a's E?1 (E318's close carries it) = 29 filed (E 8). Five are closed on arrival (native F?1, std A?1, native B?2, editor M?1, incr-53b N?1), leaving 24 open: A 0, B 6 (incr-53c B?1; solver-53 B?1-B?4; std-53 B?1), E 8, F 1 (native F?3), M 9 (incr-53a M?1-M?3, incr-53b M?1 M?2, incr-53c M?1-M?4), N 0.

## On-arrival closes

`closes53-draft-on-arrival.json`: five entries keyed by placeholder id with `finds_lane`. Procedure: file the lane's spec, read the ids it allocates, replace `id` (delete `finds_lane` and the top-level `note`), run close_batch AFTER file_items. close_batch requires the item file and INDEX row to exist, so file first.

## Allocated ids (planned; NOTHING FILED YET - the scripts were denied, see the hand-back)

Integrator decisions applied to `filed/newitems53-*.json`: incr-53a E?1 removed (M?3's body now says E318); incr-53c M?2 removed (folded into M138's stamp); std-53 A?1 moved to section B (placeholder B?2, body reference to its B?1 resolved). Filing specs with REAL ids and resolved cross references: `filed/spec53-<lane>.json` (file in this order, one at a time). Map: `allocated53.json`.

| lane | placeholder | allocated |
|---|---|---|
| debug-53 | E?1 | E323 |
| debug-53 | E?2 | E324 |
| debug-53 | E?3 | E325 |
| debug-53 | E?4 | E326 |
| editor-53 | E?1 | E327 |
| editor-53 | E?2 | E328 |
| editor-53 | M?1 | M153 |
| fmt-53 | E?1 | E329 |
| fmt-53 | E?2 | E330 |
| incr-53a | M?1 | M154 |
| incr-53a | M?2 | M155 |
| incr-53a | M?3 | M156 |
| incr-53b | M?1 | M157 |
| incr-53b | N?1 | N178 |
| incr-53b | M?2 | M158 |
| incr-53c | M?1 | M159 |
| incr-53c | M?3 | M160 |
| incr-53c | M?4 | M161 |
| incr-53c | B?1 | B635 |
| native-53 | F?1 | F142 |
| native-53 | B?2 | B636 |
| native-53 | F?3 | F143 |
| solver-53 | B?1 | B637 |
| solver-53 | B?2 | B638 |
| solver-53 | B?3 | B639 |
| solver-53 | B?4 | B640 |
| std-53 | B?2 | B641 |
| std-53 | B?1 | B642 |

Cross references resolved in the specs: solver-53 B639's title ("native-53's B636's in-place twin"); std-53's B641 body names B642. Closes/stamps: `closes53.json` (36 closes: 28 + M133 + B619 + E318 + the 5 on-arrival, real ids) and `stamps53.json` (6 stamps: E257, E292, M138, L24, N157, M36). The drafts are kept.
