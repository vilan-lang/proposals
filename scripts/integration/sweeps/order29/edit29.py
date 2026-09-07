#!/usr/bin/env python3
"""edit29.py [--dry] — Order 29's sweep edits (repo-relative): prose ledger rows 400–404 after 399,
row 399 reworded (rpc-29), row 229's site note corrected; status updates on B256, M36, M19."""
import os, re, sys
dry = "--dry" in sys.argv
root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..")
def path(*p): return os.path.normpath(os.path.join(root, *p))
def edit(rel, fn):
    p = path(rel); s = open(p).read(); t = fn(s)
    assert t != s, f"no change in {rel}"
    if dry:
        import difflib
        for l in difflib.unified_diff(s.splitlines(), t.splitlines(), rel, rel + " (new)", lineterm="", n=0): print(l[:220])
    else: open(p, "w").write(t)

ROW399 = "{label} is `[expose(keyed)]`d, but nothing names its KEY type: a keyed mirror is a `KeyedSource<K, T>`, and the `[service]` expansion reads both types off the annotation (there are no associated types to read the key from). A `Map<K, V>` element names both and takes the bare form; anything else names the key in the attribute — write `[expose(keyed = K)]`, or drop `keyed` for a channel that resends the whole value on every change"
NEW_ROWS = """| 400 | analyzer.rs (`entry_as_dependency_module_note`, B250) | `this file is being checked as a module of `{package}` — it lives inside that package, so its siblings are `pkg::` here, not `{package}::`. Write `import pkg::…` for a module of `{package}` itself` |QUALIFIES — a NOTE beside the unresolved import: the file is a module of its own package while it is the open entry, and the spelling to write is in the message. (Lane smalls-29.) `-`. |
| 401 | analyzer.rs (`check_written_nominal_bounds`, B251) | `'{type}' does not implement trait '{trait}', required by the bound on parameter` |QUALIFIES — a struct's written argument checked against its parameter's bound, both types and the trait named; the declaration note carries the parameter. (Lane solver-29.) `-`. |
| 402 | analyzer.rs (`refuse_operator_right_operand_on_bound`, B246) | `a bound promises a trait's METHODS, never that `{name}` ADMITS an` |QUALIFIES — the unsound accept refused with the rewrite the author meant (`<P: Add<i32>>`); an implicit binder is offered the written-out rewrite, not a name it lacks. (Lane solver-29.) `-`. |
| 403 | analyzer.rs (`check_expose_fields`, A51) | `{label} names a key with `[expose(keyed = …)]`, but its collection is not written as a `List<T>` or a `Map<K, V>`: those are the two the keyed exposure can read, and the `[service]` expansion picks between them off the annotation before any type resolves. Write the field as `SignalCell<List<T>>`` |QUALIFIES — the two collections a keyed exposure reads, named, with the field spelling to write. (Lane rpc-29.) `-`. |
| 404 | analyzer.rs (`check_expose_fields`, A51) | ``[expose(keyed = …)]`'s argument is a TYPE — the key type the mirror is keyed by, as in `[expose(keyed = str)]`. It is written here because a keyed mirror is a `KeyedSource<K, T>` and a `List<T>` names only the element; a `Map<K, V>` element names both, and takes the bare `[expose(keyed)]`` |QUALIFIES — the one attribute argument that is a type, with the example spelled and the reason it exists. (Lane rpc-29.) `-`. |"""

def ledger(s):
    lines = s.split("\n"); out = []
    for l in lines:
        if l.startswith("| 399 | "):
            head, rest = l.split(" | `", 1)
            tail = rest[rest.index("` |QUALIFIES"):] if "` |QUALIFIES" in rest else rest[rest.index("` |"):]
            tail = tail.replace("(Lane rpc-28.)", "(Lane rpc-28; reworded by rpc-29 for `keyed = K`.)")
            out.append(head + " | `" + ROW399 + tail); out.append(NEW_ROWS)
        elif l.startswith("| 229 | parsing.rs ParseErrorReason::Rule (nine sites:"):
            out.append(l.replace("(nine sites: ", "(nine sites at Order 22 — twenty-two by Order 29, B247's malformed hole and B248's block-like head among them: ", 1))
        else: out.append(l)
    return "\n".join(out)
edit("projects/vilan/proposal/diagnostics-ledger.md", ledger)

def status(rel, line):
    def fn(s):
        i = s.index("\n- kind:")
        return s[:i] + "\n" + line + s[i:]
    edit(rel, fn)
status("projects/vilan/tracker/items/B256.md", "- status update 2026-09-07 (Order 29, lane rule1-29 @47d7a599): the default ruling IMPLEMENTED and MEASURED, then HELD — std copies deep aggregates per notify (`bind_each`'s `row_views`/`row_owners` reads, `drain`'s wave list): +20% CPU on `bind_each` at 500 rows, +12% on A44's selector, +25% on a batch drain, +344% on a raw `get()` (node, loadavg 101–104, medians of nine); three ignored pins carry the numbers. Three options: land at these numbers; clone at every read (worse); or B267 first — a cell-aware last-use elision, since both hot std reads have a dead or walked source — then re-measure and land. Recommended: B267 first.")
status("projects/vilan/tracker/items/M36.md", "- status update 2026-09-07 (Order 29, lane m36 @c40716b1; analysis-reuse.md §6.15): SPIKE, nothing built, no flag — serializing the analyzed world is NOT feasible: four structures are keyed by leaked AST addresses (`macro_item_invocations`/`macro_expression_expansions`/`macro_failed_sites`, `MacroRegistry::blocks_by_module`, `MacroDef::world`, `GeneratedItems::nodes`); inputs-plus-reconstruction buys only the 90 ms parse share (resolve is 210 ms). REFRAMED as suite-wide: every test process pays 240–330 ms and nextest gives each its own process — 5,089 × 240 ms ≈ 1,221 s ≈ 31% of vilan-core's 3,949 s suite CPU, against 86 s for the two differentials; a `fork()`-based warm-base harness needs no relocation (copy-on-write keeps every address key valid) but nextest owns the spawn. CI saving if a cache shipped: a few percent of wall (the legs are compile-dominated). Stays open with §6.15 as its design; M50 is its accounting find.")
status("projects/vilan/tracker/items/M19.md", "- status update 2026-09-07 (Order 29, lane m19-t1c @f49008e9): tranche 1c landed — the drop planner's enrolment restored per module as `drop_roots: Vec<Id>` (no type crosses; the cost was M28's per-body gate, not the typed rows): the gate walks 154 of 3,398 bodies on kolt's client, `plan_resource_drops` 4,729 → 627 ms cold/warm, leg warm CPU 5,875 → 5,615 ms (debug, loadavg 97–190); world reuse 58/58. Foreign-touch decisions recorded in place (`check_hmr_transfer_bounds` re-runs; `compute_capture_clone_sites` is residue; `compute_resource_types` not restorable in principle). Next: M48 (R10 = T1d, the largest line left), M49 (the fingerprint split, `LastUse` re-priced).")
print("edit29: done" + (" (dry)" if dry else ""))
