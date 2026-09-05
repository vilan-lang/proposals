#!/usr/bin/env python3
"""edit28.py [--check] — Order 28's sweep edits: prose ledger rows 386–399, M27/M36/E121 corrections, remote-sources §8 spelling."""
import sys, re
check = "--check" in sys.argv
import os
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..", "projects", "vilan") + "/"
ledger = P + "proposal/diagnostics-ledger.md"
s = open(ledger).read()
assert "| 386 |" not in s and "| 385 |" in s
rows = [
 (386, "analyzer.rs (the entry's module loader, B226 — Order 27, rowed late)", "`pkg::{name}` is this program's own entry file, so this import…", "QUALIFIES — the self-import WARNING: names the file, says why it binds nothing. (Lane checker-27; rowed at Order 28's sweep, an Order 27 omission.) `-`."),
 (387, "analyzer.rs (the entry's module loader, B226 — Order 27, rowed late)", "`pkg::{name}` is this program's entry file, which is the…", "QUALIFIES — the cycle ERROR: a sibling importing the entry; states that the entry is the program and steers to a shared module. Fires for a DECLARED entry only since B239; once per import statement since B240. (Lane checker-27; rowed late.) `-`."),
 (388, "parsing.rs (`parse_static_accessor`, E135 — Order 27, rowed late)", "a name after `::`", "QUALIFIES — an expectation word (a slot of row 204's `found {found} expected {expected}`), rowed because the order asked; sibling expectations are not rowed — the convention is recorded here, not changed. (Lane parse-fmt-27; rowed late.) `-`."),
 (389, "analyzer.rs (the condition check, B234)", "this {construct} is `{label}`, and a condition must be `bool`: `bool`'s set is `bool` itself and no trait names it, so no bound on `{label}` can prove membership", "QUALIFIES — a rigid parameter as a condition, refused through the shared rigidity predicate; names the construct and says why no bound helps. (Lane rigid-28.) `-`."),
 (390, "parsing.rs (`parse_static_accessor`, E142)", "a name after `::` on the same line: a `::` path does not cross a line break, because `a::` at the end of a line joins whatever the next line starts with — join the line, or import the path under a shorter name (`import a::b::c as d;`) and write `d`", "QUALIFIES — the owner's line rule with both repairs named, the alias one being new grammar in the same lane. (Lane parse-fmt-28.) `-`."),
 (391, "analyzer.rs (a trait-typed field's mention at a position that cannot ground it, B184)", "`{name}` {reason}carries a hidden type parameter — and nothing here can supply one", "QUALIFIES — the sugar's own refusal at the annotation, naming the positions that work. (Lane b184-b218.) `-`."),
 (392, "analyzer.rs (a mismatch through a trait-typed field, B218)", "Expected {struct}, but got {rendered} instead. '{struct}' has a trait-typed field, so the annotation on", "QUALIFIES — the ruled display: the hidden argument SHOWS (`C<A>` vs `C<B>`), with the initializer note; a deliberate deviation from B186's rule at the one place it did not work. (Lane b184-b218.) `-`."),
 (393, "analyzer.rs (the post-solve residual sweep, B232)", "this call could not be resolved: the type of {operand} is never determined", "QUALIFIES — a stalled `MethodCall` finally speaks for itself, naming the operand; B229's clean-program guard went with it. (Lane context-28.) `-`."),
 (394, "analyzer.rs (a `context` clause on a trait or impl method, B242)", "a `context` clause on a trait or `impl` method is not supported yet: a dispatched call selects its callee at the call site, so the requirement cannot be checked against one declaration. Declare it on a free `fun` and call that from the method", "QUALIFIES — the deferred half of B242, refused with the reason and a repair. (Lane context-28.) `-`."),
 (395, "analyzer.rs (a `context` clause naming a non-context, B242)", "this `context` clause names a value that is not a context", "QUALIFIES — plain. (Lane context-28.) `-`."),
 (396, "context.rs (a caller of a declared clause outside `run`, B242)", "context `{context}` is required by `{name}`'s `context` clause, but this code can be reached without an enclosing `run` — call it under `{context}.run(..)`, or declare `context {context}` here too", "QUALIFIES — checked against the DECLARATION, one hop, both repairs named. (Lane context-28.) `-`."),
 (397, "context.rs (the subset rule, B242)", "`{name}`'s body reads {contexts}, which this `context` clause does not declare — write `{spelling}`", "QUALIFIES — the declared set must cover the body's strict reads; the spelling to write is in the message (and the quickfix reads it back). (Lane context-28.) `-`."),
 (398, "context.rs (a wider clause, B242)", "this `context` clause declares `{context}`, which `{name}`'s body never reads; callers must supply it anyway", "QUALIFIES — a WARNING: a forward-compatible surface is allowed and its cost stated. (Lane context-28.) `-`."),
 (399, "analyzer.rs (`check_expose_fields`, A39)", "{label} is `[expose(keyed)]`d, but its element is not written as a `Map<K, V>`: a keyed mirror is a `KeyedSource<K, T>`, and the `[service]` expansion reads BOTH types off the annotation (there are no associated types to read the key from). Write the field as `SignalCell<Map<K, V>>`, or drop `keyed` for a channel that resends the whole value on every change", "QUALIFIES — the macro half's residue (A51) stated as a refusal with both repairs. (Lane rpc-28.) `-`."),
]
lines = s.split("\n")
at = next(i for i, l in enumerate(lines) if l.startswith("| 385 |"))
new_rows = [f"| {n} | {site} | `{msg}` |{verdict} |" for n, site, msg, verdict in rows]
lines[at+1:at+1] = new_rows
s2 = "\n".join(lines)
# M27 / M36 / E121
D = P + "tracker/items/"
m27 = open(D + "M27.md").read(); assert "Order 28" not in m27
m27 = m27.replace("\n- kind:", "\n- status update 2026-09-05 (Order 28, lane perf-28 @799c897f): `entity_spans` is per MODULE (0.014 ms vs the whole-program scan's 8–11 ms, 591–798×, same rows); the rest of `lsp-index` is still whole-program, and the per-module half needs entity ids stable across analyses — M19 T1's world gives them; the fold e126 named (one declaration sweep, one occurrence walk) is still open. NARROWED to that.\n- kind:", 1)
m36 = open(D + "M36.md").read(); assert "Order 28" not in m36
m36 = m36.replace("\n- kind:", "\n- status update 2026-09-05 (Order 28, lane perf-28 @0ce9b060): MEASURED and DESIGNED, not built — cold 370 / warm 180 / floor 190 ms (51% of a cold analysis) at loadavg 106; the build needs `World` serialization, which does not exist; the design is in the `#[ignore]`d measurement's doc and the changelog. A lane of its own.\n- kind:", 1)
e121 = open(D + "E121.md").read(); assert "Order 28 note" not in e121
e121 = e121.replace("\n- kind:", "\n- Order 28 note (2026-09-05): M19 tranche 1b landed (lane m19-t1b @d3fe3276): six class D passes restored per reused module; kolt's client leg 351/369 → 331/341 ms (min/median, quiet box, loadavg 15.6). Arc record on the client leg: 411 → 367 (T1) → 341 (T1b). `diagnostics_budget` in release is LOAD-DEPENDENT (690–831 ms at loadavg ~100, a quiet box passes) — E149 records it in the gate's reason. T1c (the drop planner's resolved-`Type` record) = M42.\n- kind:", 1)
rs = P + "proposal/remote-sources.md"; r = open(rs).read()
n_old = r.count('{"Subscribe":0}')
r2 = r.replace('{"Subscribe":0}', '{"Subscribe":[0,null]}')
if check:
    print(f"edits valid: {len(rows)} prose rows after 385 (line {at+1}); M27/M36/E121 ok; remote-sources §8 spellings to fix: {n_old}"); sys.exit(0)
open(ledger, "w").write(s2); open(D + "M27.md", "w").write(m27); open(D + "M36.md", "w").write(m36); open(D + "E121.md", "w").write(e121); open(rs, "w").write(r2)
print("edits applied")
