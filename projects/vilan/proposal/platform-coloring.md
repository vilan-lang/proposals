# Platform coloring — function-granular platform checking

**Status: proposed.** (§8 — F27 R3, platform-fenced twin items — added
2026-09-24.) The successor granularity to `platform-model.md`: that
document made *modules and layers* the unit of platform truth; this one makes
**functions** the unit for application code, with layers remaining the
declaration mechanism at library boundaries. Motivated concretely by the
`[service]` placement problem (below) and by backlog §E.8's diagnostic
standard. Companion reading: `platform-model.md` (the layer model this builds
on), `library-packages.md` (L1/L2), `transport-rpc.md` §4.2 (the service
macro this liberates).

## 1. The problem

A `[service]` struct must live in a `common` library package today, because
both the browser and the server compile it — and platform checking is
module-granular, so *everything* in that module must resolve on *both*
platforms. The bodies of `[rpc]` methods are compiled by a build that will
never run them, and they pay for it:

```vilan
// common/src/lib.vl — compiled into BOTH builds
impl TodoStore {
    [rpc]
    fun add(self, label: str): i32 {
        self.db.insert(label)      // ✗ cannot exist: `std::db` is @process,
        …                          //   and this module also serves the browser
    }
}
```

So every server resource reaches the service through injected values and
closures, threaded from `server/main.vl` into struct fields. Kolt does this
dance today; the walkthrough and todo examples do it in miniature. The
`context` API cannot rescue it: `let db: Context<Db> = Context::new()` in
`common` already *names* `Db`, and naming a `@process` type from
browser-compiled code is the violation. Contexts solve value plumbing, not
the type-level wall.

The deeper statement of the problem: **the compiler checks platform at the
granularity of "what is compiled together" instead of "what actually runs
on this platform."** The client needs the service's *contract* — signatures,
exposed element types, the hash, the generated stub. Only the server needs
the bodies. The module system currently cannot express that split without
splitting packages.

## 2. The design in one paragraph

Every function gets an inferred **platform requirement** — the set of
platforms it can run on — seeded by std's layer declarations and propagated
through the call graph, exactly as async-ness is inferred today (same
`CallGraph`, same fixpoint shape, same dispatch-candidate treatment for
generics and traits). A build **checks requirements only on code reachable
from its entry point**. Unreachable code is still parsed, analyzed, and
type-checked — it just isn't platform-admitted. An `[rpc]` body that calls
`std::db` is `@process`-colored; the browser build compiles the same module,
generates the same stub and hash from the signatures, and never reaches the
body — so nothing errors. Reach it, and the error names the chain.

## 3. Rules

### 3.1 Color is on code, not on types

- A **function's** requirement = the intersection of the platforms of
  everything it transitively calls or reads, seeded by definition site: a
  function defined in a layer module (e.g. `std/src/process/db.vl`) requires
  that layer's platforms; base-layer and user code start unconstrained.
- A **type is colorless.** `struct Store { db: Db }` is declarable anywhere;
  a field, parameter, or return type may name a platform-specific type
  freely. Color flows through the only way to *obtain* such a value — calling
  colored constructors/functions — so a browser-reachable path can never
  actually hold a `Db`. (Types are erased in the JS backend; there is nothing
  a type name alone can do at runtime.)
- A **module-level initializer** (a `let` at module scope) is code: its
  requirement is checked like a function reachable from every entry that
  loads the module. `let db: Context<Db> = Context::new()` is fine anywhere —
  `Context::new` is neutral; it is `db.run(open_db(), …)` that is colored.

### 3.2 Propagation

- Direct calls and reads: union into the caller, per the call graph.
- Trait/generic dispatch: color via **dispatch candidates**, exactly as
  `async_infer` does — an impl's member for the method, the trait default,
  and the same-named-members over-approximation when a multi-bound parameter
  loses precision. Over-approximate is sound (it can only reject more).
- Monomorphization: a generic function's requirement is computed **per
  instantiation** — `save<T: Persist>(x: T)` is `@process` only for the `T`s
  whose `Persist` impl is. *(Landed 2026-07-14, v0.5.0: the walk threads
  each call's recorded bindings — `method_call_substitution` plus the call's
  solved generic arguments, the same channels monomorphization reads —
  composing them under the caller's like `emit_instance`; a dispatch whose
  receiver resolves under those bindings descends only into the member that
  instantiation selects (nominal impl match, else its traits' defaults);
  anything unresolved keeps every candidate, over-approximate but sound.
  Visited states key on (node, resolved bindings), so distinct
  instantiations re-walk and recursion terminates. Emission's binding
  reachability and the async-initializer gate consume the SAME traversal
  (`platform_color::reachable_bindings`), preserving emitted ⊆ admitted
  under the refinement. Found and fixed while landing it: a resolved call's
  SUBJECT (the callee's name, incl. wired method subjects) was recorded as
  a fn-coercion reference — a context-free duplicate edge that would have
  defeated the refinement; call subjects no longer record. Hover's
  `requirements` map deliberately stays entry-independent and
  over-approximate — a function's hover shows what it COULD require.)*
- Closures, v1 rule: a closure literal's body color **propagates to the
  function that creates it**. Creating a `@process` closure marks the creator
  `@process`. This is deliberately conservative: it keeps closure *values*
  colorless as data (no coloring of fields/params holding them), and it is
  exactly right for the service macro (`dispatcher()` creates the route
  closures containing user bodies, so `dispatcher()` is `@process`; the stub
  creates none). Loosening to invocation-site coloring — letting neutral code
  *store* colored closures it never calls — is recorded as a future step; it
  is the platform analogue of J2's async-type-in-field limitation and should
  probably land with it.
- A named function passed as a *value* (fn-to-closure coercion,
  fn-coercion.md) has no creation event for that rule, so **the reference is
  the charge**: `apply(save)` colors the passer with `save`'s body color,
  and the later value-indirect calls stay uncharged — same shape as the
  closure rule, anchored at the coercion site. *(Added 2026-07-13; shipped
  with the initializer work — the reference edge was missing entirely, so a
  browser build could pass a `@process` function into a callback and ship
  it.)*
- **Module-level initializers** (added 2026-07-13, closing the recorded v1
  gap): a binding's initializer runs iff something reachable references it —
  F6, the transformer's stated emission semantics ("a dropped binding's
  initializer does not run; top-level side effects are not a promise"). So a
  *reference* to a module-level binding is an edge to it, and the binding's
  out-edges are its initializer's calls, its created closures (the creator
  rule, with the binding as creator — global closures previously charged
  nobody), and its references to other bindings. Chains render the binding
  as a frame: `main → cache → read_file_to_str (std::fs)`. A `const`-marked
  initializer is evaluated at compile time and ships as a serialized value —
  it has no edges and seeds nothing, wherever it is defined. Emission
  consumes the same reachability (`CallGraph::reachable_bindings`): a
  dropped binding is never even walked, so its callees — and their
  `import … from "node:…"` extern lines, which previously leaked into every
  bundle and would kill a real browser at module parse — never emit.
  Admission and emission share one successor expansion
  (`CallGraph::successors`), so *emitted ⊆ admitted* holds by construction.

### 3.3 Checking

- Each build has an entry (today: the package `target`'s main). Every
  function **reachable** from that entry must admit the build's platform.
  Reachability is the analyzer's existing notion (the one behind
  reachable-subset std loading and abstract-fn removal).
- Everything else in loaded modules is parsed, name-resolved, and
  type-checked as today — type errors in unreached server code still fail a
  client build. Only the *platform admission* check is reachability-scoped.
  (The machinery half-exists: off-platform modules are already "still loaded
  for typing" with the error reported at the import — analyzer.rs's
  cross-platform import path. This proposal moves the report from the import
  site to reachable use, and deletes it when there is no reachable use.)
- Cross-package imports stop being platform checkpoints for applications: a
  browser app may depend on a `@process`-targeted package, reach its neutral
  items, and never its colored ones.

### 3.4 What layers still do

Declared layers remain the **boundary contract** for `std` and for published
`[library]` packages: a library *promises* platforms per layer, and
`check_library_contract` keeps verifying every module of every layer against
its promise (definition-site, as today — a library must not compile-or-not
depending on who imports it). Coloring consumes those declarations as its
seeds. Application packages — the ones with entries — get inference. A
private path-dependency library may choose either: declare layers and be
contract-checked, or declare none and let its items color inferentially
through the app's build.

### 3.5 Macros

Macro-world code executes at compile time on the host; it is outside the
coloring domain entirely (it already lives in a separate hermetic world).
Macro *output* is ordinary source and colors ordinarily. `[service]`
generation needs no changes: stub + hash derive from signatures; bodies and
`dispatcher()` color `@process` by inference in each world that compiles
them.

### 3.6 Diagnostics (the §E.8 standard, built in from day one)

A violation is reported at the **user's code with the chain**, never at a
std frame:

```
Error: `render_page` cannot run on `browser`
  it requires @process because it calls `std::fs::read_to_string`
    render_page (client/src/main.vl:41)
    → load_template (client/src/main.vl:88)
    → std::fs::read_to_string (@process)
  reachable from the browser entry via `main → route → render_page`
```

The chain is the propagation path the fixpoint already walked; rendering it
is bookkeeping (record one predecessor per colored node, like async_infer's
divergence notes). An error inside macro-generated code names the generating
item (`the route generated for [rpc] fun add`), using the macro engine's
provenance.

## 4. What this unlocks

### 4.1 The service moves home

```vilan
// server/src/store.vl — the service lives WITH its resources
[service(TodoClient)]
struct TodoStore {
    [expose] todos: Signal<List<Todo>>,
}

impl TodoStore {
    [rpc]
    fun add(self, label: str): i32 {
        let db = db_scope.get();          // a Context<Db>, established in main
        db.insert(label)                   // direct std::db use — @process body
    }
}
```

The client package depends on the server package (or a `service` package the
server also uses), imports `TodoClient`, and compiles: the stub and contract
hash are signature-derived; `add`'s body and `dispatcher()` are
`@process`-colored and unreachable from the browser entry. **The injected
closure/value pattern becomes a choice, not a requirement** — and `context`
becomes the natural way to hand resources to handlers (capture-at-creation
through `dispatcher()` already works; the wire-turn machinery proved it).

### 4.2 Single-package full-stack (the package-targets endgame)

Once checking is per-entry-reachability, the three-package ceremony is not
load-bearing. A manifest can declare two entries in one package:

```toml
[package]
name = "todo"

[entry.client]
target = "browser"

[entry.server]
# target defaults to node; path defaults to <name>.vl under the root
```

`vilan build` compiles each entry against its platform; functions color by
inference; the service struct sits wherever it reads best; `common` becomes
taste. (The `EntrySection` remnant in the manifest parser is the fossil of
the old `[server]`/`[client]` sections — this is that idea done right.)

Design, settled at implementation (2026-07-13):

- **Keys.** `[entry.<name>]` takes `target` (same vocabulary and validation
  as `[package] target`; the early sketch's `platform =` key is spelled
  `target` so the manifest has one word for it) and `path` (resolved
  against the package `root`, like `[package] entry`; default `<name>.vl`
  — so `[entry.server]` alone means `src/server.vl`). `target` defaults to
  node. Entries therefore live under the source root by construction, and
  `pkg::` resolves from any of them.
- **Validation.** Entries require a `[package]`; they are mutually
  exclusive with the single-entry keys `[package] entry`/`target` (one
  manifest, one way to say it). An entry name must be a valid identifier
  (it names `dist/<name>.js`); `path` must be relative and free of `..`;
  at least one entry when the table appears.
- **Lowering.** A multi-entry package lowers onto the existing workspace
  orchestration: one build unit per entry, all sharing the package's
  source root, dependencies, and `[build]` options, with outputs at
  `<package dir>/dist/<name>.js` (assets — e.g. a browser entry's CSS —
  beside them, as today). Build order is *semantic*, not
  declaration-order: browser-class entries build first (stable among
  themselves), so a process entry that serves bundles always finds them
  fresh. A `[project]` member may itself declare entries and contributes
  one unit per entry; duplicate output names across a workspace are
  rejected at lowering. `--platform`/`--stdout` don't apply to multi-entry
  builds (exactly as they don't to workspaces).
- **`vilan run` / `vilan check`.** The workspace rules apply unchanged:
  `run` builds everything and runs the single node-platform entry (zero or
  several is an error naming the ambiguity); `check` checks every entry,
  always (§7 decision 4).
- **Editor.** A file matching an entry's path analyzes under that entry's
  target; any other file under the root has no single platform (it may be
  reached from several entries), so its platform is inferred from its own
  imports — harmless, because a module has no `main` and thus no
  admission walk; it still gets hover colors, which are
  platform-independent.
- **The legacy `[server]`/`[client]` pair is retired.** No manifest in the
  tree uses it; `validate` now rejects it with a migration hint pointing
  at `[entry.server]`/`[entry.client]` (the serde fields survive solely to
  render that hint), and the CLI/LSP lowering paths are gone.

## 5. What does NOT change

- `std`'s layers, the resolution order, and the platform registry
  (`platform-model.md` §§3–7) — unchanged; they are the seeds.
- `check_library_contract` for `[library]` packages — unchanged.
- Wire safety: `[derive(Wire)]`'s recursive-syntactic field check stays
  exactly as conservative as it is (analyzer-stabilization notes why);
  coloring neither relaxes nor depends on it.
- Type checking of unreached code, the docs gate, goldens: everything still
  compiles end to end; only platform admission narrows to reachable code.
- Existing multi-package apps keep building bit-for-bit: package targets
  become entry seeds, imports that check today keep checking.

## 6. Delivery

- **Phase 1 — the inference + reachability check** (the substance): the
  coloring fixpoint over `CallGraph` (per-instantiation, dispatch-candidate
  rules), reachability-scoped admission replacing import-site rejection for
  app builds, chain-rendering diagnostics. Manifest untouched. Exit
  criterion: the todo example's service moves into `server/` with direct
  `std::db`-style access (via a small on-disk store; the example keeps
  `todos.json`), client build green, and the error chain renders for a
  deliberate violation.
- **Phase 2 — polish** *(SHIPPED)*: LSP surfacing (colors as hover info;
  violations as live diagnostics under the document's entry), error-format
  bake-off, `--platform` interaction audit (`vilan check` of a multi-entry
  package checks every entry). Landed as: chains label library frames with
  their module (`boot (server::store) → exists (std::fs)`); `vilan check`
  audited (it funnels through the same pipeline as `build`, proven on a
  violating file); live editor diagnostics pinned (manifest `target` drives
  the platform, scratch files infer theirs from imports); and hover shows a
  function's requirement via `platform_color::requirements` — an
  entry-independent per-function fixpoint (multi-source BFS per layer label,
  caller-ward over the same edge expansion as the admission walk) whose
  witness links render a shortest via-chain, e.g. ``requires the `process`
  layer of `std` (via `save → write_file (std::fs)`)``.
- **Phase 3 — multi-entry packages**: the `[entry.<name>]` manifest form,
  `vilan build`/`run` orchestration, the walkthrough rewritten as one
  package (docs: services guide, platform guide, walkthrough — same
  commits).
- **Recorded, not scheduled**: invocation-site closure coloring (with J2's
  field-typed async closures), inferred layer synthesis for publishing a
  colored library, wasm as a third color exercising >2-platform sets.

Tests, per case (the harness patterns exist): seed pickup from a layer
module; propagation through direct call / trait impl / trait default /
multi-bound fallback; per-instantiation generics (same function admitted and
rejected under different `T`s); closure-creation coloring (`dispatcher()`
shape); module-initializer coloring; elision (colored body unreachable from
the entry compiles + runs); the moved-service e2e over `local_rpc` and over
the http mount; chain-rendering `assert_fails_spanning` pins; a
`[library]` contract check unchanged under the new pass.

## 7. Decisions (settled with the user, 2026-07-13)

1. **Terminology**: "platform requirement" in diagnostics and the spec;
   "coloring" in the guide, where the async rhyme helps teach it.
2. **Explicit annotation**: none in v1 — pure inference. A declared
   `[platform(…)]` fence (checked against inference, like a type
   annotation) is cheap to add later where teams want boundaries.
3. **Dependency direction pre–phase 3**: blessed — a client may depend on
   the package that defines the service; it is temporary scaffolding until
   single-package entries land.
4. **`vilan check` on multi-entry packages**: checks all entries, always —
   the contract-check spirit. `--platform` narrows a `build`, not a
   `check`.

## 8. Platform-fenced twin items (F27 R3)

> **Added 2026-09-24** (work order 41, lane papers-41; tracker [[F27]] R3).
> The owner RULED R3 on 2026-09-21 — "platform-fenced twin items in one file
> for userland twins (disjoint platform sets = coherent; each analyzed only
> under a platform it admits; the editor checks once per declared platform),
> NOT app-level layers (R4 stays the documented fallback, unbuilt)". This
> section is the design that ruling asked for, and the build is NOT this
> order's: **R1 — `[platform(..)]` at module level, on `impl` blocks and on
> nominals, as the platform an item is ANALYZED under — is being built this
> order by lane editor-41**, and R3 is written as the step after it. Where R3
> leans on R1's exact shape, §8.8 says so, and the integrator reconciles the
> two after editor-41 reports.
>
> Every "today" below was probed on `vilan 0.40.0 (1265ea5d3)` over scratch
> copies; the programs are `scripts/integration/sweeps/order41/papers-41/probes/f27_*.vl`,
> re-run by `run_probes.sh` in the same directory.

### 8.1 The ask

kolt's `conditional_value.vl` (gone from kolt since; its shape reproduced in
F27's record) is a user `Slot` impl over the BROWSER twin's `Region`, and
"technically a server-side implementation should exist too". std answers that
shape with layers — `std/src/browser/ui.vl` and `std/src/process/ui.vl` both
write `impl View with Slot` — and an application has no layers. R3 lets it
write the two in one file:

```vilan
import std::ui::{ Region, Slot, View };

struct ConditionalValue<T> { … }

[platform("browser")]
impl ConditionalValue<type T> with Slot {
	fun place(self, parent: View) { … region.anchor … }   // the browser twin's Region
}

[platform("@process")]
impl ConditionalValue<type T> with Slot {
	fun place(self, parent: View) { … }                    // renders once, server side
}
```

### 8.2 What happens today

| # | Program | `--platform node` | `--platform browser` |
|---|---|---|---|
| f27_01 | the two fenced impls above, over a local trait | `'Show' is already implemented for 'Thing'` (B98) **and** `cannot find 'platform' in this scope` — the attribute is not admitted on an `impl` | the same two |
| f27_02 | two fenced FUNCTIONS of one name | `'where_am_i' is already declared in this module` (B57) | the same |
| f27_03 | a `[platform("browser")]` function reading `region.anchor` | `struct 'Region' has no field 'anchor'` — the fence has no resolution meaning (F27's measurement, re-run); R6's note names the browser twin | no errors |
| f27_04 | a `[platform("browser")]` function no entry reaches, with a type error in its body | `Expected i32, but got str` | the same — §2's "unreachable code is still type-checked", as shipped |

So three things stand in the way, and R1 removes the first two for a SINGLE
fenced item: the attribute on an `impl` (f27_01's second error), and the
fence's resolution meaning (f27_03). The third — two items of one identity
coexisting — is R3's own.

### 8.3 The rule

**R3.1 — Coherent iff DISJOINT.** Two items of one identity — two impls of one
`(trait, trait arguments, subject)` (B98's pair key), or two module-level
declarations of one name (B57's) — are admitted exactly when both carry a
fence and the fences' HOST sets are disjoint. The sets are computed over the
host vocabulary the fence checker already enumerates (`platform_color.rs`,
`known_hosts()`: node, deno, bun, browser); `@process` is {node, deno, bun}.
`browser` beside `@process` is disjoint; `@process` beside `node` is not, and
the refusal names the host both admit ("both impls admit `node`: a build for
`node` would have two"). An unfenced item beside a fenced one overlaps
everywhere and is refused the same way — there is no "default plus a
platform override"; the default is spelled as the complement fence (§8.7 Q4).

**R3.2 — Each is analyzed only under a platform it admits.** An analysis runs
under one platform (a LEG). In a leg, an item whose fence excludes that leg's
platform is not collected at all: no entity, no impl registration, no emission.
This is exactly how std's twins already avoid B98 — "exactly one file named
`ui` loads per build and the two impls never land in `self.implementations`
together" (`analyzer.rs`, the platform-twins carve-out of
`check_duplicate_trait_impls`) — moved from file granularity to item
granularity. Inside the admitted twin, R1's resolution meaning holds: the one
`import std::ui::Region` at the top of the file means the browser twin's
`Region` in the browser leg and the process twin's in the process leg, because
each twin's body is only ever analyzed in a leg that resolves `std::ui` to its
own layer.

A leg keeps a small FENCED-OUT table (name or impl key → its fence), so a
reach to a twin the leg excludes, with no twin of its own, reports R1's
colouring chain ("`window_controls` requires `browser`; reached from `server`
through …") rather than `cannot find 'window_controls'`.

**R3.3 — A build selects by its entry.** A build's leg is its entry's platform
(`[package] target` or `[entry.<name>] target`, §4.2), so the build compiles
the twin its entry admits and never sees the other. Reachability, admission and
emission are unchanged: they run in the leg, over what the leg collected.

**R3.4 — Twins agree on their signatures.** Two trait impls agree by
construction (the trait fixes every member's signature). Two free functions of
one name must have the same written signature — parameters, return type,
generics, bounds — or shared code would type-check in one leg and not the other
with no single place to say why. Checked at the pair, leg-independently, over
the parsed signatures ("the `browser` and `@process` twins of `where_am_i` must
agree: this one returns `str`, that one `i32`"). This is the userland form of
std's twin-parity gate (`std_twin_parity.rs`) — for one pair, at compile time.

**R3.5 — A missing twin is an ordinary miss.** The fences need not cover every
host. A `deno` build of a file with only `browser` and `node` twins finds none,
and the reach reports exactly what R3.2's table says.

### 8.4 The editor and `vilan check` — once per declared platform, diagnostics unioned

This machinery EXISTS, for a different reason. A module shared between the legs
of a multi-entry package (E113) is already analyzed by the editor once per
further leg — `ProjectContext::shared_platforms`, each leg's program analyzed
by `Document::diagnostics_under` and dropped, its diagnostics merged into the
primary's with a same-place-and-words dedup (`vilan-lsp/src/document.rs`, the
`shared_diagnostics` merge) — and `vilan check` checks such a file under every
color the build compiles it under (`check_once`, `vilan-cli/src/main.rs:673`).
R3's editor half is therefore:

1. **A file's fence platforms join its legs.** Every platform set a twin in the
   file declares, not covered by a leg the file already has, adds one leg — in
   the editor's `shared_platforms` and in `vilan check`'s platform list alike.
   A file with no fenced twins pays nothing.
2. **Requests inside a fenced-out twin route to the leg that admits it.** Today
   "hover/goto/completion stay the primary leg's", and the further leg's
   program is dropped; under R3 the cursor inside the `@process` twin of a file
   whose primary leg is browser would get no hover at all. The further leg's
   program is KEPT for files carrying twins, and requests whose position falls
   inside a fenced item are answered by the leg that admits it. That is the
   one real editor cost: memory and one extra analysis per keystroke, for those
   files only. Measured on this tree, a file importing `std::ui` checks in
   0.23 s of CPU under either platform (child-process CPU, load average 12), so
   the second leg is one more of those — the `lsp-legs` phase line (E106)
   already counts it.
3. **Dead-code paint and "unloaded" gray** do not paint a twin grey because the
   primary leg did not collect it; a fenced-out twin is live in its own leg.
4. **Go-to-definition on a call to a twin** answers both locations (LSP
   `Location[]`), the admitting leg's first.

### 8.5 The invariant, stated honestly

§2 says "Unreachable code is still parsed, analyzed, and type-checked — it just
isn't platform-admitted", and §3.3 that "type errors in unreached server code
still fail a client build". **R3 bends both, deliberately.** A browser build
never collects the `@process` twin, so a type error in it does not fail the
browser build (f27_04 would pass a browser build if its function were a twin
fenced to `@process`). The replacement:

> **Every item is type-checked under at least one platform it admits, and
> `vilan check` and the editor check every item under every platform its fence
> and the file's legs name.** A single-leg `vilan build --platform browser`
> checks the browser leg's items and no others.

What still holds unchanged: an UNFENCED item is checked in every leg, reached or
not, exactly as §2 says; only a fenced item's body is leg-scoped, and only
because its sibling exists. A CI that runs only a browser build of a package
with process twins no longer type-checks them — `vilan check` does, and the
guide should say so where it introduces twins.

### 8.6 R4 — app-level layers, the documented fallback (unbuilt)

The alternative F27 recorded: an application declares layers the way std and a
`[library]` do (`[package.layer.browser]` → `src/browser/x.vl` and
`src/process/x.vl`), and the twins are two FILES. All of its machinery exists —
the layered search roots (`PackageSpec::search_roots`), `check_library_contract`,
the twin-parity idea — so it is the cheapest to build and needs no new
coherence rule. It is also what the owner called clunky: one shared type with
two `Slot` impls becomes three files and a manifest section, and the shared
file's imports resolve differently from the twins'. **Ruled the fallback, not
the design; not built.** It stays the answer if R3's editor cost (§8.4 item 2)
proves unaffordable, which is the one place R3 could fail on measurement.

### 8.7 Open questions, with a recommendation each

**Q1 — which items may be twinned in the first build?** *Rec: trait impls and
free functions only.* Trait impls carry their parity for free (R3.4); functions
need one signature comparison. Twin NOMINALS (a struct with different fields per
platform, as std's `Region` is) and twin inherent impls are HELD: their
parity is F27 R5's open question for std itself (the twin-parity gate is
field-blind), and a userland struct whose fields differ by platform raises
layout and `Wire` questions no customer has asked.

**Q2 — must the fences cover every host?** *Rec: no* (R3.5): a missing twin is
an ordinary miss with the colouring chain.

**Q3 — the single-leg build checks one leg.** *Rec: accept it*, as §8.5 states;
`vilan check` is the all-legs answer, and the guide says so.

**Q4 — a default plus a platform override?** An unfenced impl beside a
`[platform("browser")]` one would be "specialization by platform". *Rec:
refuse* (R3.1) — the default is the complement fence, written out; it keeps
coherence a set question with no ranking.

**Q5 — do twin functions have to agree?** *Rec: yes, exactly* (R3.4).

**Q6 — keep the further leg's program in the editor?** *Rec: yes, for files
carrying twins only* (§8.4 item 2) — the alternative is no hover or completion
inside half of the file.

### 8.8 Where R3 depends on R1 as built

- R1 admits `[platform(..)]` on `impl` blocks and nominals (f27_01's
  `cannot find 'platform'` goes away) and gives the fence a RESOLUTION meaning
  (f27_03 passes under the fence). R3 assumes both.
- R1 decides what a file with a single item-level fence is analyzed under. R3
  assumes the file keeps its ambient platform for unfenced items and a fenced
  item is analyzed in the leg its fence names — i.e. R1's "analyzed under" for an
  ITEM already implies a second leg when the item's fence differs from the
  file's. If editor-41 instead makes a lone item-level fence colour the whole
  file, §8.4 item 1 is where R3 generalises it (one leg per declared set), and
  nothing else here moves.
- R1's quick fix inserts the module-level attribute; R3 adds none — twins are
  written on purpose.

### 8.9 Size, and the second customer

| Piece | Where | Size |
|---|---|---|
| R3.2 leg filtering at collection + the fenced-out table | the analyzer's collection pass | S–M |
| R3.1 the disjointness carve-out in B98's and B57's checks | `check_duplicate_trait_impls`, `report_duplicate_declarations` | S |
| R3.4 the signature agreement check for twin functions | a pair check over parsed signatures | S |
| §8.4 1 — fence platforms join the legs (editor + `vilan check`) | `vilan-lsp` project context, `check_once` | S |
| §8.4 2–4 — routing requests to the admitting leg, paint, goto | `vilan-lsp` | M |
| R3.2's chain message for a fenced-out reach | `platform_color.rs` | S |
| the spec (§2's invariant restated), the guide's platform page | docs | S |

**M–L**, as F27's build order sized it, after R1.

**The second customer is F17's native window chrome.** F17 asks how UI code is
written once for native and web "with named exceptions (native window chrome:
close/minimize/maximize buttons …)". Under R3 an exception is a twin:

```vilan
[platform("native")]
fun window_controls(parent: View) { … place the platform's buttons … }

[platform("browser")]
fun window_controls(parent: View) {}      // the browser draws its own chrome
```

— one call site in shared UI code, one leg each. It needs the `native` host in
the vocabulary (native-apps.md §5's slice list: `[library.layer.native] platform
= ["native"]`, and §9 Q2's "does `native` join `@process`?"), which is F1's
work, not R3's; R3's disjointness is over the host vocabulary, so a new host is
one more row in `known_hosts()`.

### 8.10 The recommendations, collected

1. **Build R3 after R1**: fenced twins coherent iff their host sets are disjoint
   (R3.1), each collected only in a leg it admits (R3.2), the build's entry
   selecting the leg (R3.3), twin functions agreeing on their signatures
   (R3.4).
2. **Reuse E113's legs**: a file's fence platforms join the legs the editor and
   `vilan check` already run and union; keep the further leg's program for
   files with twins, so requests inside a twin are answered by its own leg
   (§8.4).
3. **State the new invariant in the spec** where §2's sentence stands (§8.5).
4. **First build: trait impls and free functions**; twin nominals and inherent
   impls held behind F27 R5 (§8.7 Q1).
5. **R4 stays the documented, unbuilt fallback** (§8.6).
6. **F17's window chrome is the second customer**, arriving with F1's `native`
   host (§8.9).
