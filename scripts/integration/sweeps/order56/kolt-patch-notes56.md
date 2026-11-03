# Kolt under v0.54.0 (tag 3891c987; toolchain `vilan 0.54.0 (56008e46d)`) — the owner's patches from Order 56 (kolt branch vilan-migration @3fb5d74 = the B688 imports, committed by the integrator on the owner's word)

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

## The order of adoption under v0.54.0 (tag 7c11bea4)

1. B688's imports are in (vilan-migration @3fb5d74, committed by the integrator on the owner's word; not pushed).
2. `vilan fmt .` under 0.54.0: rewrites the 21 `(impl _)` lines to `(impl *)` (A181 - the compiler READS `(impl _)` this release but reports an error; next release refuses it), collapses the 4 lone-selector sets, and applies E354's receiver-literal reflow (the 37-file drift the owner has been carrying). One commit.
3. Nothing else is required: A182 drops no method in kolt (the compiler's census), M191 has 0 `update`/`modify` users in kolt, B695 changes no kolt answer the owner relies on (owner question 3 for the initial-letter site), B677/E356/B690/B691/E360 0 sites.
4. Optional, when the owner wants them: M185's `std::image` for the upload thumbnails; M176/M177 for the raw `X-Kolt-Filename` POST (multipart form uploads); `Connection::revoke` when A175 lands.
5. Checked: both entries (`src/server.vl`, `src/client.vl`) check clean with 0 errors 0 warnings under 7c11bea4's parent (305f8721) on the exhibit + the A181 patch (~/.vilan/perf-exhibit/order56/kolt-tip).
