# Kolt under v0.54.0 — the owner's patches from Order 56 (kolt branch vilan-migration @3fb5d74 = the B688 imports, committed by the integrator on the owner's word)

Everything here is the OWNER's to apply; no lane and no integrator edits ~/code/kolt without the owner's word. Order: B688 is in (3fb5d74); then the items below in the order they ride.

## lang-56b — A181: `(impl _)` → `(impl *)` (21 lines in 18 files)

`(impl _)` is READ as `(impl *)` this release with an error carrying the fix, refused next release; `vilan fmt` rewrites it. Both kolt entries check with 20 errors each (the same lines) until the rewrite; with it, both check clean. Patch: sweeps/order56/lang-56b/kolt-a181-impl-star.patch (or just `vilan fmt .` under 0.54.0 — it does the same rewrite). Also 4 lone-selector sets (`m::{ (impl T) }`) that fmt collapses to `m::(impl T)` — formatting drift only.

## lang-56b — A182: leaf-only admission

The compiler's census on the kolt copy: 0 files lose a method. Nothing to do.

## solver-56 — B695: a cut inside a surrogate pair (BREAKING on JS)

0 sites depend on a half; 0 empty-pattern literals. Sites that can meet a pair at run time: the per-unit walkers (markdown, search, files, shared, org_pages) rebuild their text unchanged; the fixed-width cuts (task_assignees.vl:50's initial letter is now `""` for an emoji-initial name — was a lone half; mcp_write, file_page, measure, dictionary) answer the floored cut. Owner question 3 in owner-questions56.md: whether task_assignees.vl:50 should take the first code point instead.

## solver-56 — B690 / B691 / E360 / B646 guard

0 kolt sites change; kolt client and server check clean with the lane's binary. (B691 copies enum payloads at value seams on JS — kolt's behaviour where it aliased before is now the native one.)

## tooling-56 — N183 / E346 / E347

N183: 0 kolt files affected. E346: `dbg`/`print` of a str holding control characters now prints `\u{..}` escapes (a `Key::Paste` no longer writes a live ESC). E347: no printer change; the kolt copy's 37-file fmt drift is the owner's pending E352/E354 reflow, the same list before and after.

## incr-56

Nothing: analyzer-internal (the editor's keystroke on kolt reads −20.7 % instructions).
