# B382 — is a type alias worth having? (one page, for the owner)

Lane papers-40, Order 40, on vilan `next` @49de3915 (`vilan 0.40.0 (49de39157)`).
The brief's R-c: a recommendation, no build this order.

**Every claim below was probed on the worktree.** The probe files are
`probes/b382_*` in this directory; each was run with the worktree's own
`target/debug/vilan`.

---

## The item's premise is two-thirds wrong

B382 says three things are missing, "any one of which would have served" A112's
RULED deprecated `KeyedCursor` re-export. Measured:

| B382's claim | verdict |
| --- | --- |
| (1) `type Alias = Existing;` cannot be written | **TRUE.** `Error: found 'type' expected an expression`, then `cannot find type 'KeyedCursor'` |
| (2) `import … as` cannot re-export under another name | **FALSE.** It works, it is transparent, and it re-exports |
| (3) `[deprecated]` is a function attribute | **TRUE.** On a struct: `Error: cannot find 'deprecated' in this scope` — the attribute falls through to macro resolution |

### What (2) actually does today

```vilan
// src/inner.vl
export struct DeltaCursor { at: i32 }

// src/re.vl
export import pkg::inner::DeltaCursor as KeyedCursor;

// src/main.vl
import pkg::re::KeyedCursor;
import pkg::inner::DeltaCursor;
fun takes(c: DeltaCursor): i32 { c.at }
fun main() { print(i"{takes(KeyedCursor { at = 3 })}"); }   // prints 3
```

Compiles and runs. The alias is **transparent** — a `KeyedCursor` value passes
to a `DeltaCursor` parameter, so it is a second NAME, not a second type, which
is exactly what a transparent alias is for. A second probe extends it to every
item kind in one program:

- a generic struct (`Pair<T>` as `Duo`) used as `Duo<i32>`;
- a trait (`Named` as `Labelled`);
- an enum (`Side` as `Edge`) including variant paths (`Edge::Left`) and matching
  on them;
- a function (`make` as `build`);
- and an **impl written on the alias with the aliased trait**:
  `impl Duo<type T> with Labelled { … }`.

All of it compiles and runs (`duo 2 L`). And `import std::map::Map as Table;`
in a leaf file renames in scope: the ORIGINAL name is then not in scope
(`cannot find type 'Map'`), so the alias is a rename, not an addition.

Three of B382's four proposed pins — "alias to a generic with parameters",
"alias in an impl subject", "alias across a re-export" — therefore already pass
against `export import … as`. Only the fourth ("hover renders `= Existing`") is
about a feature that does not exist.

### What (3) costs

`deprecated` is already in the parser's `KNOWN_ATTRIBUTE_MARKERS`
(`parsing.rs:1088`), but `parse_deprecated_attribute` (`parsing.rs:7320`) is
called only on the function path, and `Func` is the only node with a
`deprecated: Option<&str>` field (`node.rs:86`). The machinery that USES it —
the non-fatal warning carrying the steer verbatim — already works and is
measured:

```
Warning: `a` is deprecated; use b
 4 │ fun main() { print(i"{a()}"); }
   │                       ┬
   │                       ╰── `a` is deprecated; use b
```

So admitting it elsewhere is: call the same parse helper on the
struct/enum/trait/import/export item paths, carry the string on those nodes
(`Struct` and `Enum` are already boxed for `node_size`'s ceiling — check
`node_size` in the gate list), and raise the same warning from the name-lookup
site instead of the call site. The editor half is E213's greying, which Order
40's editor lane is already building for `[doc(internal)]` — the same mechanism,
a different tag.

---

## Recommendation

**Do (3). Do not do (1) — not for this reason.**

1. **(3) `[deprecated("use …")]` on a type, an import and an export.** Small,
   it reuses a warning path that already exists and is already correct, and it
   closes B382's actual complaint: A112's ruling WAS expressible and the lane
   did a hard rename anyway. Size S–M. Pins: the warning on a use of a
   deprecated struct, of a deprecated enum variant's enum, of a deprecated
   re-export reached through the alias, and NOT on the declaration itself; one
   ledger row is not needed (the message is the existing one), but the
   attribute's grammar row is, and `grammar_sync` gates it.

2. **(1) `type X = Y;` stays OPEN with no customer.** Every use B382 names is
   served by `export import … as` today, and the one thing an alias adds that
   the import form does not is an alias to a COMPOUND type — `type Handler =
   |str, i32| void;`, `type Rows = List<(usize, str)>;` — which is a real want
   but a different want, and nothing in the estate has asked for it in writing.
   It is also not free: a transparent alias has to be resolved at name lookup
   in the parser's type production, printed by the formatter, rendered by hover
   and the LSP's semantic tokens, and — the part that bites — decided one way or
   the other in every diagnostic that prints a type. Today
   `pretty_print_type` has one answer per type; with aliases it has two (what
   the user wrote, what it resolves to) and every message has to choose. That is
   the cost, and it should be paid when a compound alias is what somebody
   actually wants.

3. **If the owner wants (1) anyway**, the cheap and honest version is the one
   that adds nothing to the type system: `type X = Y;` is sugar that the
   resolver expands at name lookup, with NO nominal identity, hover rendering
   `type X = Y`, and the formatter printing it on one line. That is the
   `M`-sized shape B382 proposes, and the estimate looks right — with the
   caveat above about diagnostics, which is where the hours actually go.

**One thing to fix in the tracker either way**: B382's claim (2) is false, and
the item should be restamped, because the next lane to read it will otherwise
build an aliasing feature the language already has.
