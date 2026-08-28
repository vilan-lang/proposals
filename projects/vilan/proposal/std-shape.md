# std vs official packages — the distribution shape (L10)

> **SUPERSEDED IN PART 2026-08-28 — read §7 first.** The owner approved
> a *namespace* split (`std::` core, `vilan::` auxiliary) that §2 never
> costed because it was never offered: a split with no distribution
> change at all. §2's Shape A/Shape B framing and §5's sentence (2) —
> "the hard split is declined" — no longer describe the live decision;
> everything else in this paper stands, including the bundle-with-
> releases mechanism, the exact-pins-only fence, promises attaching to
> the train, §4's compiler contract, and §6's four reserved names. §7
> is the amendment: the partition, the churn, the sequencing.
>
> Status: PROPOSED 2026-08-20 (cycle 26, work order 8, lane
> `l10-std-shape`). Proposal-only — no code ships with this paper.
> Tracker: backlog-2026-08-18.md §L item 10.
>
> The owner's question (2026-08-20): restructure std into `std` and
> `official packages` — "or maybe std should be more of a namespace
> under which all of the official packages are published?" The
> orchestrator's inline recommendation, which this paper argues for
> and against: the NAMESPACE model, sequenced behind a registry.
>
> This paper decides nothing the ratified papers decided, and it leans
> on one thing that is deliberately NOT ratified: beta.md §5's tier
> table is a DRAFT whose ruling the owner deferred to the beta
> switch's pre-work (2026-08-20 — "the answers to those questions
> might change"). Everywhere this paper uses the tier seam it cites
> the draft as a draft. process.md §5 (RATIFIED 2026-08-07) is the
> promise floor; beta.md §3.2/§3.3 (RATIFIED 2026-08-18) price it by
> tier; deprecation.md (PROPOSED 2026-08-20, L4) is the machinery and
> already defers user-package promises to "L10's world" (§6).

## 1. Today's physical reality — verified against the loader

**One embedded package (well: two, positionally married).**
`crates/vilan-embedded-std/build.rs` walks `vilan/std` and
`vilan/macro_std` at the workspace root and embeds every `.vl` and
`vilan.toml` into the binary as a sorted `FILES` table plus a
`CONTENT_HASH` over the whole set (60 `.vl` files today: 43
`std/src/*.vl`, 9 `std/src/process/*.vl`, 5 `std/src/browser/*.vl`, 3
`macro_std/src/*.vl` — the same census beta.md §5 tiered into 56
public modules). `vilan_embedded_std::materialize` writes the trees
once to `~/.vilan/std-cache/<CONTENT_HASH>/` (atomic rename, complete
by construction, age-pruned by `vilan upgrade`), and the loader then
reads ordinary files. An installed binary is fully offline and
batteries-included by construction — the std is *inside* it.

**What "the std package" means to the compiler.** `std` is an ordinary
`[library]` (library-packages.md L2): `vilan/std/vilan.toml` declares
`name = "std"` plus two platform layers (`process` for `@process`,
`browser`). `vilan-cli/src/main.rs:2303` (`std_dir`) resolves the
package directory — `$VILAN_STD`, else the nearest checkout ancestor,
else the embedded materialization — and
`vilan-core/src/manifest.rs:975` (`resolve_std`) reads the manifest
into a layered `PackageSpec`. The analyzer then builds **one flat,
root-scoped namespace**: it inventories module stems by a
non-recursive `read_dir` of the base root and each layer root
(analyzer.rs:34289), registers a single `std` module
(`module_id_by_name.insert("std", …)`, analyzer.rs:34358), and loads
`lib.vl` plus every module reachable from it and from the entry's
imports. Two consequences worth stating plainly:

- **std paths are exactly two segments deep** — `std::<stem>::<item>`.
  There is no nesting; a module *is* a file stem in some layer root.
- **Dependencies are already isolated namespaces.** A `Dep` module
  "resolves under its layered roots into its own isolated namespace,
  reachable from a dependent as `<import-name>::name`"
  (analyzer.rs:34381–34395), loaded in a canonical std → deps → pkg
  order. The *mechanism* for "a package whose modules sit under a
  named root" exists; only `std` as that root does not.

`macro_std` is found positionally — `std.base_root.parent().parent()
.join("macro_std")` (macros.rs:310) — so "the std package" is really
"the toolchain pair"; any pinning story must cover both.

**Versioned with the toolchain, and only with it.** The `Library`
manifest struct has no version field at all (manifest.rs:98); the
only version anywhere is the workspace's (0.34.0) and the
`CONTENT_HASH` that keys the cache. `vilan upgrade` replaces the
binary (and `vilan-lsp` beside it) from a GitHub release asset — and
the embedded std with it, atomically, as a side effect of being the
same file. There is no seam at which std could currently be at a
different version than the compiler.

**What a "package" can even be today.** Path dependencies, and git
dependencies pinned to exactly one `tag`/`rev` — "no resolver, no
lockfile, no 'it built yesterday' class of bug" (git_dep.rs header),
content-addressed in `~/.vilan/git-deps`, offline with a warm cache,
nothing fetched passively. The registry spelling (`dep = "1.2"`) is
*parsed and refused*: "registry dependency `{name}` is not yet
supported" (manifest.rs:772). The grammar reserves the future; D5
owns whether that future gets an audience.

## 2. The two shapes

**Shape A — the hard split.** `std` keeps a core; the framework layer
moves out as `official-packages` (or per-package names): `import
reactive::Signal`, or `import official::reactive::Signal`. Separate
versioning, separate docs, an honest name for what is and is not the
standard library.

**Shape B — the namespace.** `std::` becomes the *publishing
namespace* for official packages: the framework modules become
separately-versioned packages published under `std::`, and each
toolchain release bundles a pinned, offline-working set.
`import std::reactive::Signal` never changes spelling; the binary
stays batteries-included; a package can rev between trains for
projects that opt in.

Costed on the six axes:

**Import churn.** A is a churn event with a blast radius the tier
draft already measured: the Tier 2 candidate layer includes the
modules the todo app, the website, and kolt all stand on
(`reactive`/`ui`/`style`/`rpc`/`router`/…), plus 585KB of book whose
every fence is compile-gated. Every one of those spellings changes,
once, for every user, and the old spellings need L4's deprecation
machinery on day one of its life. B is zero churn *by construction* —
today's spellings already are the namespace model's spellings, which
is the single strongest fact in this paper: **the tree is already
forward-compatible with B and already incompatible with A.**

**Docs shape.** Today: one book, one std reference, one planned tiers
page (beta.md §5's docs note). Under A the book splits — a std
reference plus per-package docs, two places to search, and K13's
markdown story would land in the second one. Under B the book keeps
covering `std::*` as one surface; a published package's page gains a
version line. The docs gate (`cargo test --test docs`) keeps
compiling every fence against the bundled set either way only if the
sources stay in this repo — see CI below.

**Batteries-included / offline.** Today this property is not
engineered, it is *structural* (§1). B preserves it by generalizing
the same structure: the embedded `FILES` table becomes "core + the
pinned set", materialized identically. Opt-in newer package versions
cost one fetch into a content-addressed cache — exactly the git-dep
story, warm-cache offline included. A *without* bundling loses the
property outright (the tracker's phrasing stands: a split without
distribution is import churn for no capability); A *with* bundling
rebuilds B's machinery and then adds the churn on top.

**Version skew.** The real cost center, and it cuts against B, so
honestly: today skew is impossible; B makes it a supported state.
Three mitigations keep it from becoming a resolver: (1) the bundled
set is resolved *by the release engineer at cut time* — one coherent
set, tested as one tree, hashed into the binary; (2) an override is a
whole-package exact pin in `vilan.toml` (no ranges — the git-dep
stance extends unchanged); (3) the compiler-known names bound what a
package rev may do (§4). What B may NOT quietly become is per-package
version *ranges* — that is a resolver and a lockfile, the two things
the dependency design deliberately refused. A has the same skew
surface plus one more axis (core vs packages vs compiler).

**What beta's promises attach to.** process.md §5.2's window is
denominated in *minors*, and every train is a minor — the deprecation
sweep literally checks "a released `## vX.Y.Z` section"
(deprecation.md §3). Under A, each package grows its own changelog
and its own minor clock, and "one minor of warning" fragments into
per-package arithmetic — deprecation.md's question generalizes badly
(windows per package, audited where?). Under B the clean answer is:
**promises attach to the toolchain train and its bundled set.** The
pinned set is std for promise purposes; its deprecations ride the one
CHANGELOG the cut script already audits; an out-of-train package
version a project opts into is explicitly outside the window (the
same posture deprecation.md §6 already takes for user packages).

**CI / test surface.** Today one workspace gates everything: the
corpus byte-gate, the docs gate, the std-warning-clean gate, the
module-resolution tests — all against the in-tree std. A multiplies
repos, CI surfaces, and a cross-repo version matrix. B costs nothing
now, and even when publishing is real the cheap shape is
**monorepo-published**: package sources stay in this repo (the tier
seam as directory structure), the registry receives snapshots at cut
time, and the suite keeps testing the exact set the binary bundles.
The new leg B eventually owes: build each publishable package against
its declared toolchain floor.

**The honest case against B** — three arguments, none disposable:

1. **It reintroduces version resolution in miniature.** Pinned set +
   exact overrides is defensible; but the moment two `std::` packages
   depend on each other, "override one" implies a coherence check the
   toolchain must own. Small, but permanent, and it is exactly the
   class of machinery this project has twice declined to build.
2. **It spends the `std` brand.** Today `std::` means "ships with
   your compiler, at your compiler's version." Under B it means
   "blessed by the project, version varies." The spelling no longer
   tells the user which promise they hold — the tiers page and a
   `vilan` command have to. A's names are honest at the price of
   churn; B's continuity is bought with a blurred word.
3. **Nothing demands it yet.** Zero packages exist, no registry
   exists, and 56 modules ship happily as one tree. The house has
   twice taken the null recommendation on demand surveys
   (trait-objects.md, top-level-await.md). The strongest version of
   this argument: B's whole virtue is that *choosing* it costs
   nothing — which is equally an argument that the correct amount to
   build today is nothing.

## 3. Sequencing — nothing splits before a registry exists

1. **Now: decide, build nothing.** The decision is free precisely
   because B is spelling-compatible with today. Record the direction;
   keep one std; keep the alpha/beta work (L3's tiers, L4's
   machinery) exactly as planned. The tier table — cited as the draft
   it is — is the seam definition: Tier 1 core is the inseparable
   floor (§4 makes that structural, not just editorial), the Tier 2
   framework layer is the candidate publishing surface. The seam gets
   re-read when the deferred §5.1 ruling happens at the switch.
2. **The registry is D5's world.** There is no registry
   (manifest.rs:772 refuses the reserved spelling), and a registry
   without users is a service bill — process.md §7.1 already named D5
   the policy's urgent dependency. When it exists, *user* packages
   exercise it first; std is deliberately not the registry's pilot
   customer.
3. **The namespace switch is additive.** When publishing is real and
   a reason exists (a package that wants to rev between trains, or
   K13's markdown story wanting a home — see below), the framework
   modules become packages published under `std::`, each toolchain
   release bundling the pinned set. No spelling changes; no book
   split; users who do nothing observe nothing.
4. **The hard split is never on the path.** It is not a fallback
   position of B; it is a different, churn-priced product. Declining
   it now is a real decision, not a deferral.

**K13's markdown story is the first candidate — say it now.** A
`std::markdown` (docs-port.md §3.3: a parser producing a plain-data
AST) is new (no churn either way), demand-backed (the docs port is
blocked on it), pure vilan, platform-neutral, and compiler-uncoupled.
Under B it can ship *in* std at Tier 2 tomorrow and be re-homed as
the first published `std::` package later with zero spelling change —
the model's proof case. Under A it would have to guess its permanent
name before the split exists. If the markdown story is built before
any of this, building it package-shaped (own directory, no
compiler-known names, no cross-layer entanglement) costs nothing and
keeps the proof available.

## 4. What the compiler must grow — either shape, mostly B's

**Package identity for std modules.** Today a std module's identity
is a file stem in a layer root; the analyzer neither knows nor needs
a package boundary inside the namespace. B's eventual loader change:
the std namespace is populated from a **manifest of entries**, each
either "embedded" or "package `<name>` at exact version `<v>`, hash
`<h>`" — resolved through the same isolated-namespace machinery
`Origin::Dep` already implements, grafted under the `std` root
instead of a sibling root. Root-scoped flatness survives (a package
supplies stems); the platform-layer mechanism survives (any
`[library]` may declare layers — `std::ui`'s two halves stay one
module). One hygiene rule should land *before* any of this matters:
`Manifest::validate` reserves nothing today, so nothing stops a user
declaring a dependency whose import-name is `std` — at best silently
shadowed by the real namespace, at worst ambiguous (the failure mode
is untested because the case is unconsidered, which is the point) —
reserve `std`, `pkg`, and `macro_std` as dependency import-names now
(small, and correct under every shape including the status quo).

**A per-release pinning manifest.** It already exists in degenerate
form: the embedded `FILES` table + `CONTENT_HASH` *is* a pinned,
hashed, offline set of everything std-shaped, and the cache layout
already knows how to hold multiple sets side by side. B generalizes
it to named entries with versions; the binary still embeds the
bundled sources (batteries stay structural, not fetched); the
manifest is what `vilan --version`-style tooling and the docs read.
`macro_std` rides the same manifest — its positional discovery
(macros.rs:310) becomes an entry like any other.

**Tier 1 is structurally inseparable — verified, not asserted.** The
compiler holds Tier 1 core by identity, not by import: the prelude
primitives are std source whose ids the analyzer captures at load
(`list.vl`'s `List::new`/`push` lower to `[]`/`.push`; `str`, `bool`,
`null` are module-defined); the transformer resolves `print` out of
the std scope by name and panics without it (transformer.rs:1665);
`context`/`nursery` intrinsics are captured the same way. A
separately-versioned Tier 1 is therefore fiction — core std and the
compiler are one artifact with one version, under every shape. And
the entanglement does not stop cleanly at the tier seam, which B must
price: `Signal` (reactive) is captured for HMR transfer
classification (analyzer.rs:35361), `JsonValue` (json) for lowering,
and a `[service]` attribute force-loads `std::rpc` because the
`service` macro lives there (analyzer.rs:34448). **Compiler-known
names are part of the toolchain contract**: a published package's rev
may not move or rename them except in step with a toolchain release.
Each publishable package therefore declares a minimum toolchain (a
single floor, not a range), and the compiler-known-name list should
be written down once, as the packages' side of the contract.

**`vilan upgrade` and a registry coexist by scope.** `upgrade` stays
what it is: whole-toolchain, binary + embedded set, atomic, steered
away when npm/Homebrew own the install (upgrade.rs). Package version
choice is *per project, in `vilan.toml`* — an exact-pin override of a
bundled entry — so there is no second global mutable state and no
`vilan upgrade std::x` command. The registry cache mirrors git-deps:
content-addressed, never stale, warm-cache offline, fetched only by a
build that declares the pin. The one new interaction: `upgrade`
moving the bundled set forward must warn when a project's explicit
pin now *lags* the bundle — a diagnostic, not a resolver.

## 5. Recommendation

> **Sentence (2) below is superseded — see §7.** The hard split was
> declined as a *distribution* split, and that decline stands. What the
> owner approved 2026-08-28 is a namespace seam inside one bundled
> toolchain: neither Shape A nor Shape B, and §7 names it Shape C.

**The namespace model, as a recorded direction — and no construction
now.** Ratify three sentences: (1) `std::` is the publishing
namespace; if official packages ever exist they are published under
it, each toolchain release bundling a pinned offline-working set, and
promises attaching to the train's bundled set; (2) the hard split is
declined — spelling churn and a split book buy nothing the tier
table's published promises don't already deliver; (3) nothing is
built until D5's registry exists and a concrete package wants out of
the train — with `std::markdown` (K13) named as the expected first
case. The honest counter-arguments (§2) are answered by the
sequencing, not dismissed: the resolver-in-miniature risk is fenced
by exact-pins-only, the brand question is deferred to the moment a
package first actually revs off-train (nothing is blurred while the
set and the train are identical), and the null-demand point is
conceded — which is why the recommendation ships zero code. One
hygiene exception: file the reserved-import-name rule (§4) as a
small backlog item now.

## 6. Owner questions

> **RULED 2026-08-22 — all five as recommended** (namespace-over-split as
> recorded direction, zero construction now; the window in package
> revs; the tier seam may carry the sequencing; `std::markdown` built
> package-shaped when K13 reaches it; the reserved names are L12's to
> build).
> **2026-08-24**: the `[library] name` exemption is the PERMANENT line — a
> library's own name never binds an import root; reserved *published*
> names become the registry's refusal when publishing exists (D5).

1. **The direction.** Ratify namespace-over-split as recorded intent
   (§5's three sentences), building nothing now? This forecloses only
   the hard split; every future choice about *when* stays open.
   Recommend: yes — today's spellings already commit us cheaply.
2. **What the window is denominated in.** When packages can rev
   between trains: recommend beta's promises attach to the toolchain
   train and its bundled set only — an opted-into off-train package
   version carries no deprecation window (deprecation.md §6's posture
   generalized). The alternative — per-package windows on per-package
   minors — multiplies L4's audit surface. Accept?
3. **May the sequencing lean on the draft tier seam?** §3 treats the
   deferred tier table's Tier 1/Tier 2 boundary as the seam defining
   what could ever publish, subject to re-reading at the switch. If
   you expect the seam itself (not just row assignments) to move,
   this paper's §3 step 3 should wait for the ruling instead.
4. **Build `std::markdown` package-shaped?** When K13's markdown
   story is built, build it as if published (own directory, no
   compiler-known names) so it can become the first `std::` package
   without rework — at essentially zero extra cost. Accept?
5. **The one code item.** Reserve `std`/`pkg`/`macro_std` as
   dependency import-names in `Manifest::validate` — file now as a
   small hygiene item (correct under every shape)?

**Ship note (L12), 2026-08-24.** The reserved names shipped, exactly at
the §4 seam: `Manifest::validate` refuses `std`, `pkg`, and `macro_std`
as a `[package] name` and as a dependency key in any of the three
`dependencies` tables, with one head family (`` `std` is a reserved
package name: the standard library owns it (`std`, `pkg`, and
`macro_std` are all reserved); rename the package `` — ledger row 248),
riding the existing channels: the CLI refuses before any dependency
work, the editor publishes on the `vilan.toml` (the F5 S5 channel). The
probe confirmed §4's "unconsidered" verdict in the worse direction: a
dependency named `std` did not sit beside the namespace, it silently
*replaced* it (the analyzer binds dependency edges before the global
roots, so every `import std::…` resolved into the dependency), `pkg`
was silently dead (the self-package root always wins), and `macro_std`
both shadowed the macro world's std and satisfied the macro-body
hermeticity check by spelling alone. `[library] name` is deliberately
exempt — std itself is `[library] name = "std"` (likewise macro_std), a
context-free validation cannot tell the owner from an impostor, and a
library's own name, unlike a dependency key, never binds an import
root; the exemption is pinned as a complement, and the registry (D5's
world) owns refusing reserved *published* names when publishing exists.
Family `breaking` (a today-legal manifest stops compiling); docs: tour
"Projects and dependencies", spec §4.2 and §11.4.

**Ship note (the `vilan` reservation), 2026-08-26.** The set grew its
fourth name: `vilan` joined at the same seam (Order 11, lane
std-dogfood, vilan 9198d8f9) — the recorded first step of the owner's
2026-08-26 position on the namespace question this paper ruled ("we can
package this `vilan::` namespace in all vilan releases just like std
until a package registry is up" — a re-ruling of §5's declined Shape A
still to come; kolt.local tracker item 026 carries the argument).
Reserving the name is neutral to however that lands and cheapest before
any user package claims it. The refusal parenthetical now names four
(the quoted head above is L12's as shipped then; ledger row 248
re-keyed), the reason string is "the language owns its own name", the
`[library]` exemption is unchanged, and the pins mirror L12's
per-position set (plant-proven). Family `breaking`, L12's precedent.

---

## 7. Amendment — the `std::`/`vilan::` partition (2026-08-28)

> Status: PROPOSED 2026-08-28 (cycle 36, work order 18, lane
> `std-shape-amendment`), written against kolt.local tracker item 026
> (**APPROVED 2026-08-28**). Proposal-only — no code ships with this
> section; the migration is its own later arc. Measured against vilan
> `6fcb64d4` (v0.37.0), the website checkout, and kolt, all read-only.
>
> **Placement.** A new section rather than an edit of §2/§5, because
> §§1–5 are the record that produced the 2026-08-22 ruling and rewriting
> them would erase the reasoning the owner ruled on. §6's 2026-08-26 ship
> note already forward-references "a re-ruling of §5's declined Shape A
> still to come" — this is that re-ruling, landing exactly where the note
> points. The two pointers added above (the header banner and the §5
> note) are the whole in-place edit.

### 7.1 What was ruled

The owner, verbatim (2026-08-28, approving kolt.local 026):

> **"I want `std::` for true core, and `vilan::` for auxiliary
> features. `ui` would fall under `vilan::` because cli only programs
> are somewhat common and first-party. But, something like `option`
> would be in `std::`."**

That sentence carries the ruling *and* its two calibration anchors:
`ui` → `vilan::`, `option` → `std::`. The justification it gives for
`ui` is the load-bearing part — a program shape (CLI-only) that is
common and first-party must not be made to carry the framework's
vocabulary. The seam is therefore drawn by **program shape**, not by
stability, not by platform leg, and not by age.

It stands on the owner's 2026-08-26 position, already recorded in §6's
second ship note: *"we can package this `vilan::` namespace in all vilan
releases just like std until a package registry is up."* That sentence is
the reason this amendment costs so much less than §2's Shape A: the
`vilan` namespace is not a distribution event. It is a second
toolchain-owned root, embedded in the same binary, cut on the same
train, hashed into the same `CONTENT_HASH`.

**What is superseded.** §2's binary framing (hard split vs publishing
namespace) and §5 sentence (2) ("the hard split is declined — spelling
churn and a split book buy nothing…"). The decline of Shape A *as a
distribution split* stands and is not reopened.

**What survives, unamended.** §1's physical reality; §3's "nothing
splits before a registry exists" (still true — nothing splits here);
§4's whole compiler contract, which this amendment leans on harder than
§4 anticipated; §5 sentences (1) and (3) as they apply to *publishing*;
§6's four reserved names, one of which (`vilan`) was reserved for
precisely this. The one §3 line that needs re-spelling is its naming of
`std::markdown` as the first publishable candidate — under §7.4 that
module is `vilan::markdown`, and the argument for building it
package-shaped is unchanged.

### 7.2 Shape C — a namespace split that is not a distribution split

Call the approved shape **C: the two-root toolchain.** Two toolchain-owned
import roots, `std` and `vilan`, both embedded, both materialized from the
same `FILES` table, both cut on the same train, one CHANGELOG, one book,
one version. Version skew remains *impossible*, exactly as §1 describes it
today. `macro_std` is unaffected and stays a third root of its own.

§2 costed Shape A on six axes and four of them were reasons to decline it.
Under Shape C, **exactly one of those four lands**:

| §2's cost of the split | Under Shape C |
| --- | --- |
| **Import churn** — "a churn event with a blast radius the tier draft already measured" | **Lands, in full.** Measured in §7.7: 939 import lines, ~1,665 textual mentions, 230 files. This is the price, and it is paid knowingly and once. |
| **Docs shape** — "the book splits, two places to search" | **Does not land.** One book, one std reference part, one `SUMMARY.md`. The pages are organized by topic already (§7.8); they gain a namespace column, not a second home. |
| **Batteries-included / offline** — "A *without* bundling loses the property outright" | **Does not land.** Bundling is the premise of the owner's own sentence. `build.rs` walks a third package; the property stays structural, not engineered. |
| **Version skew** — "A has the same skew surface plus one more axis" | **Does not land.** No second version exists to skew. `vilan::` is at the toolchain's version by construction, like `std::` and `macro_std`. |
| **What beta's promises attach to** — "per-package windows on per-package minors" | **Does not land.** One train, one CHANGELOG, one clock. §5's answer (promises attach to the train and its bundled set) is unchanged and now trivially true. |
| **CI / test surface** — "A multiplies repos, CI surfaces, and a cross-repo version matrix" | **Does not land.** One workspace, one corpus gate, one docs gate. The `vilan` tree is another directory the same suite compiles. |

That table is the honest case *for* the amendment and it should be read
as the whole of it: the owner is buying a naming honesty that §2 priced
only in a bundle with five costs that Shape C does not incur. §2's
strongest sentence — "the tree is already forward-compatible with B and
already incompatible with A" — remains literally true and is now simply
the statement of the bill, not an argument against paying it.

**The honest case against, three arguments, none disposable:**

1. **939 import lines is a real number, and it recurs in every
   snapshot.** Not just the tree: 654 of them live in the compiler's own
   Rust test fixtures (§7.7), where a moving stem appears inside string
   literals the byte-gate compares. This is a mechanical edit, but a wide
   one, and it lands in the same trains as the corpus's entity-id
   ordering shift (§7.8).
2. **`std::` stops being the answer to "where is anything".** Today a
   user who knows one root can find every module. Afterwards they must
   know which side of a judgement call a module fell on — and §7.4 shows
   the judgement is genuinely close for eight rows. The mitigation is the
   moved-name diagnostic (§7.8), not documentation.
3. **The seam will be re-argued the first time a module changes
   character.** `markdown` is auxiliary today and would be core in a
   docs-shaped language; `fetch` is core today and would be auxiliary in
   a language that shipped no client at all. Shape B had no such rows
   because it had no such line. Shape C creates a boundary that will
   attract re-litigation, and the answer has to be that a later move is
   cheap (it is: the same mechanical edit, on a smaller set).

None of the three defeats the ruling. They are why §7.9's questions are
the ones they are.

### 7.3 The seam principle, made testable

The owner's sentence is a principle, not a table. Three tests turn it
into one, applied in order, plus a tiebreak:

- **T1 — Structural.** The compiler knows the module by identity: it is
  prelude (needs no import), or its names are captured at load
  (§4's list), or the transformer resolves out of it by name. §4 already
  proved these are inseparable from the toolchain under *every* shape.
  → **`std::`**, no argument available.
- **T2 — Universal by shape.** Nearly every program of some common,
  first-party shape (CLI, browser page, server) needs it *regardless of
  the other shapes*. This is the owner's own test, read forwards: `ui`
  fails it because a CLI program never wants it; `process` and `fs` pass
  it because a CLI program is nothing without them.
  → **`std::`**.
- **T3 — Opinionated.** The module encodes a first-party opinion about
  *how to build an application* — a rendering model, a reactivity model,
  a styling system, a transport, a storage engine, a document format. A
  program that disagrees with the opinion still has a complete language.
  → **`vilan::`**.
- **Tiebreak — the burden of proof is on the move.** A module that
  passes none of the three (a pure, dependency-light, platform-neutral
  algorithm with no framework flavour and no universality claim) stays
  **`std::`**. Moving costs churn and buys nothing; staying costs
  nothing and can be revisited. This is what settles `base64` and
  `random`, and it is the rule that keeps the amendment from turning
  into a general re-sort of the tree.

Two anchors check the tests: `option` is T1 (prelude, and
`module_scopes.get("option")` is a compiler capture) → `std::` ✓.
`ui` is T3 and fails T2 by the owner's own reasoning → `vilan::` ✓.

### 7.4 The partition

The census is §1's, re-walked at `6fcb64d4`: **58 public modules** —
45 `std/src/*.vl` less `lib.vl` and `native_map.vl` (43 public), 9
`std/src/process/*.vl` and 5 `std/src/browser/*.vl` of which
`process/ui.vl` + `browser/ui.vl` are the two halves of the one module
`std::ui` (13 distinct), and 2 in `macro_std`. Two modules joined since
beta.md §5's 56-module count: `markdown` (2026-08-24) and `path`
(2026-08-27), neither tiered.

**36 stay `std::`. 20 become `vilan::`. `macro_std`'s 2 are untouched.**

#### 7.4.1 `std::` — the true core (36)

| Module | Leg | Tier (§5 draft) | Why core |
| --- | --- | --- | --- |
| `option` | base | 1 | **Owner's anchor.** T1: prelude, captured at load; the tree's most-imported name. |
| `result` | base | 1 | T1: prelude; the error model's bedrock — `try`/`?` desugars through it. |
| `boolean` | base | 1 | T1: the built-in `bool`, module-defined, captured. |
| `null` | base | 1 | T1: the built-in unit; dependency-free by design. |
| `number` | base | 1 | T1: the scalar types; prelude. |
| `string` | base | 1 | T1: `str`; prelude. |
| `list` | base | 1 | T1: `List::new`/`push` lower to `[]`/`.push` (§4). |
| `map` | base | 1 | T1: the built-in map; captured as an element-slot container. |
| `set` | base | 1 | T1: the built-in set; rides `map`'s machinery. |
| `native_map` | base | — | Not public — `map`/`set`'s internal building block; captured at load. Follows them. |
| `range` | base | 1 | T2: `a..b` is syntax; every loop and slice reaches it. |
| `iterator` | base | 1 | T2: the protocol `list`/`map`/`range` implement; splitting it from them is incoherent. |
| `compare` | base | 1 | T1: `PartialEq`/`Ord` — a derive target and the collections' contract. |
| `hash` | base | 1 | T1: `Map`/`Set`'s key contract (I1). Inseparable from the collections. |
| `default` | base | 1 | T1: prelude `Default`; a derive target. |
| `display` | base | 1 | T2: `Display`/`format` — every program that prints anything. |
| `debug` | base | 1 | T2: `[derive(Debug)]`; every program that debugs anything. |
| `operators` | base | 2 | T1: `Add`…`BitOr` are the language's own desugaring targets; captured ×2. |
| `into` | base | 2 | T2: after B127's DELETE the module is the `Into` trait — conversion vocabulary beside `Default`/`Display`. |
| `io` | base | 1 | T1: the transformer resolves `print` out of std scope by name and **panics without it** (transformer.rs). Structurally unmovable. |
| `math` | base | 1 | T2: named core by the seam definition; `number` already depends on it. |
| `arena` | base | 1 | T2: the ownership model's own construct (docs `std/cells.md`), captured at load; a memory-model teaching surface, not a battery. |
| `shared` | base | 1 | T1: `Shared` is captured and used in HMR classification; the reference model. |
| `drop` | base | 1 | T1: destruction.md §5's ratified hook, captured ×2 — a language feature that happens to live in std. |
| `promise` | base | 1 | T1: `async`/`await` types through `Promise<T>`; captured. **The async substrate.** |
| `task` | base | 1 | T1: `nursery`/structured spawn, captured ×2. The async substrate. |
| `context` | base | 1 | T1: spec §8's mechanism; `Context` captured and registered as an element-slot container. |
| `time` | base | 1 | T2: `Instant`/`Duration`/`Timer` — the async substrate's clock; a CLI that measures anything needs it. |
| `random` | base | 1 | Tiebreak: pure, tiny, platform-neutral, no framework flavour. Nothing is bought by moving it. |
| `json` | base | 1 | T1 **and** T2: `JsonValue` is captured for lowering; the seam definition names json-ish primitives as core; broadest breadth in the tree. |
| `bytes` | base | 1 | T2: the byte value type under every codec and every file read; 13 std consumers. |
| `wire` | base | 2 | T1-adjacent **and forced**: `std::json` imports `Wire`/`Serializer`/`Codec` directly, and the `Wire` derive is compiler-dispatched. See §7.5 — a `vilan::wire` would make core depend on auxiliary, which is unrepresentable. beta.md §5.1 Q5 already argued it earns Tier 1 on day one. |
| `base64` | base | 1 | Tiebreak: RFC 4648 §5, pure vilan, const-capable, no framework flavour. **OWNER-DECIDES** — see §7.4.3. |
| `path` | base | — | Pure string manipulation, no host binding, no platform leg. Pairs with `fs`; follows it. |
| `fs` | process | 2 | T2 by shape: reading and writing files is what a CLI program *is*. **OWNER-DECIDES** — see §7.4.3. |
| `process` | process | 1 | T2 by the owner's own reasoning: args/env/stdin/exit is the substrate of the CLI-only programs the ruling protects. |
| `fetch` | base | 1 | T2: the host `fetch` global, thin, universal across both legs. **OWNER-DECIDES** — see §7.4.3. |

#### 7.4.2 `vilan::` — the first-party batteries (20)

| Module | Leg | Tier (§5 draft) | Why auxiliary |
| --- | --- | --- | --- |
| `ui` | both | 2 | **Owner's anchor.** T3: the rendering model. Both platform halves move as one module. |
| `reactive` | base | 2 | T3: signals are *the* framework opinion. kolt reports it "feels core" (026) — but it is core to an application shape, which is exactly what `vilan::` names. It is also `ui`'s substrate, and the anchor drags it. |
| `style` | base | 2 | T3: a styling system with breakpoints and an ordering rule; a CLI program has no use for it. |
| `dom` | browser | **1** | T3: `ui`'s host binding, one layer down. Tier 1 by age and quiet (a genuine Tier-1 row on the auxiliary side — see §7.6), but a CLI program never touches an element. Splitting it from `ui` across roots would be incoherent. |
| `storage` | browser | 2 | T3: the browser key-value binding; same argument as `dom`, one layer out. |
| `dev` | browser | 2 | T3: the HMR hooks (hmr.md §4) — a dev-mode contract for the app framework. |
| `router` | browser | 2 | T3: client-side routing, an application-architecture opinion. |
| `asset` | base | 2 | T3: the bundler's asset pipeline; meaningless outside a built app. |
| `build` | process | 2 | T3: the build/bundle driver (`LegBuild`); an app-shaped concern. |
| `watch` | process | 2 | T3: the dev-mode file watcher; pairs with `dev`, and the pair settles together. |
| `document` | process | 2 | T3: the SSR document builder — a document *format* opinion. |
| `http` | process | 2 | T3: **http-serving.** `serve_build`/`serve_service`; a server framework's front door. |
| `ws` | base | 2 | T3: RFC 6455 frames existing to serve the server's upgrade path; one narrow consumer. |
| `rpc` | base | 2 | T3: the client transport; the `[service]` macro's home. |
| `rpc_server` | process | 2 | T3: `Service`; the server half of the same opinion. |
| `binary` | base | 2 | T3: the schema-ordered codec that rides the transport family (transport-rpc §6.2). **OWNER-DECIDES** — see §7.4.3. |
| `db` | process | 2 | T3: the `node:sqlite` seam — a storage engine choice, one example's worth of breadth. |
| `crypto` | base | 2 | T3: an HS512-era minimum shaped by one consumer. **OWNER-DECIDES** — see §7.4.3, and note the one edge it creates. |
| `jwt` | base | 2 | T3: HS512-only auth tokens; an application-security opinion sitting on `crypto`. |
| `markdown` | base | — | T3: a document format. §3 named `std::markdown` the first publishable candidate; under this partition it is `vilan::markdown`, and §3's "build it package-shaped" advice is unchanged and now cheaper to honour. |

#### 7.4.3 The borderline rows, argued

Eight rows where a reasonable owner rules the other way. Each carries a
recommendation; §7.9 batches the four that matter most.

**`fs` → `std::` (recommended).** *For:* T2 — a CLI program that cannot
read a file is a toy, and the owner's justification for moving `ui` is
that CLI programs are common and first-party. Rust, Go and Python all
put the filesystem in core. *Against:* it is `@process`-only, so a
browser program lives without it — and "lives without it" is the
auxiliary test. *Resolution:* platform-legging is orthogonal to this
seam. `std` already layers, and layering answers "does this exist on
your platform", not "is this the language". If `fs` moves, `path`
follows it and `std`'s process layer empties.

**`path` → `std::` (recommended).** Pure string work over a
platform-neutral notion; it declares no layer and binds no host. It
follows `fs` only in spirit — it can stay core even if `fs` moves.

**`process` → `std::` (recommended).** The strongest of the eight. This
is *the* CLI module, and the ruling's stated purpose is to stop CLI
programs carrying framework weight. Putting `process` in `vilan::` would
invert the sentence that produced the seam. Tier 1 already; beta.md §5.1
Q4 flagged only that it makes its directory non-uniform.

**`fetch` → `std::` (recommended).** *For:* it is a binding to a host
global present on both legs, ~1 file, no opinion — the same class as
`random`. Being an HTTP *client* is not an application architecture.
*Against:* Rust keeps clients out of std. *Resolution:* the seam
definition distinguishes http-*serving* (auxiliary) from fetching; and
`watch` (auxiliary) already depends on `fetch`, so the edge runs the
right way either way.

**`base64` → `std::` (recommended, tiebreak).** *For:* pure, const-capable,
zero platform coupling, and the burden of proof is on the move. *Against:*
it fails T2 honestly — most programs never encode base64 — and `jwt`
(auxiliary) is its only consumer today. *Resolution:* the tiebreak. If the
owner prefers a tighter core, this is the cheapest row to move: 2 import
lines tree-wide.

**`wire` → `std::` (recommended, and effectively forced).** `std::json`
imports seven names from it and the `Wire` derive is compiler-dispatched
from `json.vl`. A `vilan::wire` would require `std::json` to depend on the
auxiliary root — see §7.5, where that is shown to be unrepresentable, not
merely ugly. The alternative is moving `json` too, which contradicts the
seam definition's "json-ish primitives" and §4's `JsonValue` capture.

**`binary` → `vilan::` (recommended).** *For:* it exists for the transport
family and has no consumer outside it. *Against:* it is the other
implementation of `wire`'s `Codec`/`Frame`, and splitting the two codecs
across roots reads oddly. *Resolution:* `json` is the codec every program
meets and `binary` is the one the RPC layer meets; the seam is about
programs, not about trait families. Cheapest row in the moving set (5
sites tree-wide) if the owner disagrees.

**`crypto` → `vilan::` (recommended, with one required fix).**
`std/src/process/fs.vl:31` reads `import pkg::crypto::random_uuid;` —
used twice, for the unique suffix on atomic temp-file writes. That is the
tree's **only** core→auxiliary edge (§7.5) and it must go. Two ways:
(a) re-home `random_uuid` (and arguably `random_bytes`) into
`std::random`, where a random-value generator arguably belonged anyway —
a surface rename, family `breaking`; or (b) generate the temp suffix
inside `fs` from `std::random`, a purely internal change with **zero
surface impact**. Recommend (b) for the migration and (a) as a separate
tidy if the owner wants the surface honest. The third option — `crypto`
stays `std::` as a host-capability binding like `fetch` — is coherent,
and leaves `jwt` as the only auxiliary user of a core module, which is
fine.

### 7.5 Seam integrity — two hard constraints, both checked

**(1) No core module may import an auxiliary one.** This is not a
preference. `vilan` depends on `std` (a global root, always loaded);
`std` cannot depend on `vilan` without a cycle between two
toolchain-owned packages, and §1's load order (std → deps → pkg) has no
place to express it. Measured across all 56 modules at `6fcb64d4`, the
recommended partition produces **exactly one violation**:

```
std/src/process/fs.vl:31:import pkg::crypto::random_uuid;
```

Everything else is clean. The full intra-tree graph was walked: 36 core
modules import only core; the 20 auxiliary modules import 77 core names
and 21 auxiliary ones. `wire` is in the core list *because* the walk put
`json → wire` on the wrong side when it was not (§7.4.3).

**(2) The layers re-cut, and `std` loses one entirely.** Of the five
`browser/` files, all five are auxiliary; of the nine `process/` files,
seven are. After the partition:

- `std/vilan.toml` declares **one** layer, `process`, holding exactly
  `fs.vl` and `process.vl`. `[library.layer.browser]` is **deleted** —
  the core has no browser-specific module left. Core becomes
  platform-neutral except for two files, which is a clean outcome and
  worth saying out loud.
- `vilan/vilan.toml` declares **both** layers: `process` = build, db,
  document, http, rpc_server, ui, watch; `browser` = dev, dom, router,
  storage, ui. The two-halves-one-module mechanism for `ui` carries over
  unchanged — §4 already noted any `[library]` may declare layers.

### 7.6 How this seam relates to beta.md §5's tier seam

**Orthogonal — and the cross-tab proves it rather than asserting it.**
Mapping the partition onto the draft tier table's rows:

| | Tier 1 | Tier 2 | untiered (post-census) | total |
| --- | --- | --- | --- | --- |
| **`std::`** | 31 | 4 (`operators`, `wire`, `fs`, `into`) | 1 (`path`) | **36** |
| **`vilan::`** | 1 (`dom`) | 18 | 1 (`markdown`) | **20** |
| **`macro_std::`** | 0 | 2 | 0 | **2** |

All four quadrants are populated, and the two off-diagonal cells are the
argument. `vilan::dom` is Tier 1 — two months old, untouched since
08-01, and still something a CLI program never imports. `std::fs` is
Tier 2 — reworked 08-11, surface still moving, and still something
nearly every non-browser program needs. Neither cell is a mistake in
either table; they are two different questions:

- **The tier seam asks: how hard is it to change this?** It is a promise
  about *churn cost over time*, priced by process.md §5.2's window and
  audited at the cut.
- **The namespace seam asks: is this the language, or a battery?** It is
  a statement about *what a program must know*, and it is fixed at the
  spelling.

Collapsing them would force one of two falsehoods: demote the whole
`vilan::` half to Tier 2 (a lie about `dom`), or redraw the tier table
along a line it was never measured on. Keep both. The tiers page
(beta.md §5's `docs/std/tiers.md`, still unwritten) gains a namespace
column; it does not merge.

**One thing the namespace seam does subsume.** §3 step 1 asked the tier
seam to double as "the seam definition of what could ever publish", and
§6 Q3 asked whether the sequencing may lean on it. It no longer needs
to: **`vilan::` is the publishing surface** if publishing ever happens,
and `std::` is the inseparable floor §4 already proved. That is a
simplification of beta.md §5.1's deferred ruling, not a complication —
the tier questions get to be purely about stability again.

### 7.7 Churn accounting — measured, not estimated

All counts at vilan `6fcb64d4`, website and kolt checkouts as of
2026-08-28, over the 20 moving stems. Two measures: **import lines**
(the mechanical re-spell) and **all textual mentions** (import lines plus
prose, doc comments, type paths, and the message text of tests).

**Import statement lines, per module and corpus:**

| Module | std tree | examples | corpus | docs fences | website | kolt | crates fixtures | total |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `reactive` | 5 | 10 | 9 | 31 | 8 | 5 | 185 | **253** |
| `ui` | 2 | 10 | 2 | 18 | 13 | 2 | 108 | **155** |
| `style` | 2 | 3 | 1 | 6 | 8 | 2 | 128 | **150** |
| `http` | 1 | 4 | 0 | 12 | 2 | 1 | 37 | **57** |
| `rpc` | 1 | 3 | 0 | 1 | 0 | 3 | 47 | **55** |
| `build` | 2 | 4 | 0 | 5 | 1 | 1 | 28 | **41** |
| `asset` | 1 | 0 | 1 | 0 | 1 | 1 | 29 | **33** |
| `document` | 0 | 3 | 0 | 5 | 1 | 1 | 22 | **32** |
| `markdown` | 0 | 0 | 0 | 3 | 0 | 0 | 17 | **20** |
| `router` | 0 | 4 | 0 | 2 | 0 | 3 | 11 | **20** |
| `db` | 0 | 1 | 1 | 3 | 0 | 1 | 13 | **19** |
| `rpc_server` | 1 | 2 | 0 | 2 | 0 | 1 | 12 | **18** |
| `crypto` | 2 | 0 | 1 | 1 | 0 | 0 | 5 | **9** |
| `dom` | 2 | 2 | 0 | 0 | 0 | 0 | 2 | **6** |
| `binary` | 0 | 0 | 1 | 0 | 0 | 0 | 4 | **5** |
| `jwt` | 0 | 0 | 1 | 0 | 0 | 0 | 2 | **3** |
| `watch` | 1 | 0 | 0 | 0 | 0 | 0 | 2 | **3** |
| `ws` | 1 | 0 | 0 | 0 | 0 | 0 | 1 | **2** |
| `dev` | 1 | 0 | 0 | 0 | 0 | 0 | 0 | **1** |
| `storage` | 0 | 0 | 0 | 0 | 0 | 0 | 1 | **1** |
| **total** | **22** | **46** | **17** | **89** | **34** | **21** | **654** | **883** |

The "std tree" column counts `import pkg::<moving>` lines *inside* std —
21 of which are auxiliary→auxiliary and keep their `pkg::` spelling for
free, plus the one `fs → crypto` line that must be eliminated. The edit
std actually owes is the other direction: **77** `import pkg::<core>`
lines inside the 20 moving files become `import std::<core>`. So:

**Grand total of import lines to re-spell: 939** — 77 (auxiliary→core
inside the new package) + 1 (the `fs` edge) + 46 + 17 + 89 + 34 + 21 +
654.

**All textual mentions and files touched, per corpus:**

| Corpus | files | mentions |
| --- | ---: | ---: |
| `std/src` + `macro_std/src` | 27 | 92 |
| `examples/` | 32 | 73 |
| `test/` (the corpus byte-gate) | 15 | 22 |
| `benchmarks/` | 5 | 13 |
| `docs/` (the book — 89 of these are compile-gated fence imports) | 58 | 517 |
| `crates/*/src` (the compiler itself) | 15 | 93 |
| `crates/*/tests`, `benches` (vilan fixtures inside Rust) | 39 | 743 |
| vilan-website | 23 | 66 |
| kolt (`src/` + `e2e/`) | 9 | 25 |
| kolt `worktrees/connection-v3` (in-flight branch) | 7 | 21 |
| **total** | **230** | **1,665** |
| *proposals repo (this repo) — historical, NOT rewritten* | *351* | *2,183* |

Three things this table says that a guess would have missed:

1. **The compiler's own test fixtures are the largest corpus** — 743
   mentions in 39 files, because inline vilan programs live in Rust
   string literals. They are also the least visible: nothing in the
   proposal's earlier reasoning counted them.
2. **The proposals repo must not be swept.** 2,183 mentions across 351
   papers are the record of what was decided when. Rewriting `std::ui`
   to `vilan::ui` in a 2026-07 paper would falsify it. The rule is:
   papers keep their spelling; this section is the pointer.
3. **kolt is small.** 21 import lines across 9 files, plus 21 mentions in
   its in-flight `connection-v3` worktree. The one real user's migration
   is one `sed` and a rebuild (§7.8).

**Compiler-side follow set — 7 hardcoded sites, all located.** §4 warned
that compiler-known names are part of the toolchain contract. Of the
stem-keyed captures in `analyzer.rs`, four name a moving module:
`module_scopes.get("reactive")` (the `Signal` capture, for HMR transfer
classification), `.get("asset")`, and `.get("dev")` ×2. Three more are
the `[service]` force-load, `to_load.push((Origin::Std, "rpc"))` at
analyzer.rs:36448, :36657 and :36921. Everything else the compiler holds
by identity — `List`, `Map`, `Set`, `Shared`, `Context`, `JsonValue`,
`Promise`, `operators` ×2, `drop` ×2, `task` ×2, `option`, `result`,
`io`, `arena`, `boolean`, `native_map` — stays in `std::` by
construction. One further site is inside the tree: `std/src/rpc.vl:1836`,
the `service` macro's emitted import block, which names `std::rpc` and
`std::reactive` in a string literal (and `std::wire`/`std::result`/
`std::option`, which do not move).

### 7.8 Migration sequencing

**No deprecation is owed, and an alias window is not cheap.**
`CHANGELOG.md`'s standing header is explicit: "Minor versions (`0.X`)
may change the language, the standard library, and the wire protocol
without a deprecation period." Beta is DEFERRED indefinitely (beta.md,
2026-08-26), so the window in which this is free is open now and its
closing date is unknown — which argues for doing it sooner rather than
later. The kind-hearted instinct is a one-release alias (`std::ui` keeps
resolving, with a warning). **It should be declined, on evidence:**
deprecation.md §7's ship record says the machinery's "placement stays
functions-only" and, explicitly, "an `import` line alone does not warn —
the loader mints no value reference for it". An alias window would
require the two things that record deferred (module-level placement and
import-site warnings), built for a one-release lifetime, on the very
seam that is moving. That is more machinery than the migration.

**Buy the kindness on the failure path instead.** A moved import already
fails at `analyzer.rs:24849` — `cannot find '{part}' in the imported
path`. Add a 20-entry moved-stem table so the message steers: *"`ui`
moved to the `vilan` namespace; use `import vilan::ui::…`"*. One
diagnostic family, one table, deletable at any later train, and strictly
better than a silent alias — it forces the fix and names it. This is the
recommended kindness, and it is the answer to "is an alias window cheap
enough to be kind": no, and it isn't the kind thing either.

**The mechanical plan, in order:**

1. **Clear the seam violation first, alone, on its own train.** Remove
   `fs → crypto` (§7.4.3 option (b): zero surface impact). Nothing else
   depends on this landing first, and it makes the partition
   *representable*, which nothing else does.
2. **Create the package.** `vilan/vilan/` beside `vilan/std/` and
   `vilan/macro_std/`, with `[library] name = "vilan"` and both layers
   (§7.5). The `[library] name` exemption ratified 2026-08-24 is exactly
   what permits this: "a library's own name never binds an import root",
   so `vilan` being a reserved *dependency* name does not block it being
   a library's own name. **L12's reserved-names set needs nothing** —
   §6's 2026-08-26 ship note already put `vilan` in it, for this. The
   only follow-up is the comment at manifest.rs:1576–1600, whose text
   ("held ahead of the official-package namespace re-ruling") describes a
   ruling that has now happened.
3. **Move the 20 files** (`git mv`, preserving `--follow` history for the
   tier table's age column), and re-spell the 77 auxiliary→core imports
   from `pkg::` to `std::`. Auxiliary→auxiliary imports keep `pkg::` and
   cost nothing.
4. **Teach the toolchain the third root.** `build.rs`'s
   `for package in ["std", "macro_std"]` gains `"vilan"` (one line;
   `CONTENT_HASH` covers it automatically). `std_dir`
   (vilan-cli/src/main.rs:2588) and `resolve_std`
   (vilan-core/src/manifest.rs:1032) gain a sibling resolver — the
   pattern already exists at macros.rs:313, where `macro_std` is found
   positionally from std's root. `analyzer.rs:36358` registers a second
   global root; `Origin` (analyzer.rs:36391) gains a variant and the
   canonical load order (the WO-1b comment at :36396–36403) gains a tier
   between std and deps. **Expect the corpus byte-gate to move**: entity
   ids are minted in load order, so the emitted declaration order shifts
   for every program that touches a moved module. That diff is the
   gate working, not a regression, but it wants its own commit.
5. **Follow the 7 hardcoded sites** (§7.7) and the one emitted import
   block at `rpc.vl:1836`.
6. **Sweep the corpora** in descending order of size: crates fixtures
   (654), docs fences (89), examples (46), website (34), corpus (17),
   kolt (21). A whole-repo `sed` is **unsafe**: `crates/` is Rust, where
   `std::fs`, `std::io`, `std::path` and `std::process` are Rust's own
   and must not move. Restrict the sweep to the 20 moving stems, which
   share no name with a Rust std module — that restriction is what makes
   the edit mechanical.
7. **Land the moved-name diagnostic** with (or just before) the sweep,
   so the release that breaks the spelling is the release that explains
   it.

**CHANGELOG family: `breaking`** — L12's and the `vilan`-reservation's
precedent, and the entry deserves the migration table inline (20 stems,
old spelling → new). One entry, one bold head, per the writing note.

**Docs and book.** The reference is organized by topic, not by module:
18 pages under `docs/std/`, listed at `SUMMARY.md:34–51`. Six are wholly
auxiliary (`reactive.md`, `style.md`, `rpc.md`, `browser.md`, `dev.md`,
`markdown.md`); four are mixed and need either a split or a per-item
namespace note (`net.md` — `fetch` core, `http`/`ws` auxiliary;
`process.md` — `fs`/`process` core, the rest auxiliary; `encoding.md` —
`json`/`base64`/`wire` core, `binary` auxiliary; `misc.md`). The rest are
untouched. The part heading ("The std reference") wants renaming; the
tiers page beta.md §5 specified — still unwritten — gains its namespace
column at the same time. 517 mentions across 58 doc files, of which 89
are compile-gated fences that the docs gate will catch automatically.

**What breaks for kolt, the one real user.** 21 import lines across 9
files (`src/{store,probe,views,app_context,client,routes,server,theme}.vl`
plus `e2e/`), touching 11 moving modules — `reactive` ×5, `rpc` ×3,
`router` ×3, `ui` ×2, `style` ×2, and one each of `rpc_server`, `http`,
`document`, `db`, `build`, `asset`. Its core imports (`option`,
`result`, `json`, `time`, `shared`, …) do not move. That is a
single-pass edit and a rebuild, with the moved-name diagnostic naming
every site. The in-flight `worktrees/connection-v3` branch carries a
second copy (7 files, 21 mentions) and should be rebased after, not
before. The one coordination point: kolt's migration is beta trigger
condition (a), so this edit should not land mid-flight in a kolt arc.

### 7.9 Owner questions

> **RULED 2026-08-28 (the owner) — and the partition NARROWS, and the split
> GOES ON HOLD.** Verbatim: "`fs`, `path`, `process`, `fetch`, `wire`,
> `binary`, `base64` all stay `std::`. The only items I see moving to
> `vilan::` at this point are `markdown.vl`, `browser/*`,
> `process/document.vl`, `process/ui.vl`. Basically, the browser stuff.
> Despite browser features being first-class and heavily supported, cli
> programs are still the default. I want what is needed for those to be
> included in std. Maybe we hold off on the split for now. There's no
> reason to rush it now." So the ruled seam is MUCH narrower than §7.4's
> recommendation — reactive, style, http, ws, rpc, db, storage, asset et
> al. all STAY `std::` under this ruling; the moving set is the
> browser-and-document cluster plus markdown — and the split itself is
> DEFERRED with no execution planned. This section's tables remain the
> costed record for whenever the hold lifts; §7.4's assignments outside
> the owner's named set are superseded.

Four, batched for one ruling. Everything not listed is proposed as
tabled in §7.4.

1. **The four core-side borderline rows: `fs`, `path`, `process`,
   `fetch` — all `std::`?** Recommend yes, on the owner's own reasoning:
   the ruling exists to keep CLI-only programs light, and these four are
   what a CLI-only program is made of. The alternative reading — "browser
   programs live without `fs`, so it is auxiliary" — makes the seam a
   platform question, which `std`'s layer mechanism already answers
   better. If any one moves, `std`'s process layer empties and the core
   becomes fully platform-neutral; that is a tidier tree and a worse
   answer to "what does a CLI program import".
2. **`wire` stays `std::`, and `binary` and `base64` move/stay as
   tabled?** `wire` is effectively forced (`std::json` imports it, and a
   core→auxiliary edge is unrepresentable — §7.5), so the real question
   is whether the owner would rather move `json` too. Recommend no:
   `json` is compiler-known and the seam definition names it core.
   `binary` → `vilan::` (5 sites) and `base64` → `std::` (2 sites) are
   both cheap to rule either way; recommend as tabled.
3. **`crypto` → `vilan::`, and how to clear the one seam violation?**
   Recommend `vilan::crypto`, clearing `std/src/process/fs.vl:31` by
   generating the temp-file suffix from `std::random` — zero surface
   impact, no CHANGELOG entry. The alternative, re-homing `random_uuid`
   into `std::random`, is a better-shaped surface and costs one
   `breaking` entry; take it as a separate tidy if you want it. Third
   option: `crypto` stays `std::` as a host-capability binding beside
   `fetch`, which also clears the edge and moves one fewer module.
4. **No alias window, plus the moved-name diagnostic?** Recommend yes.
   Alpha owes nothing (CHANGELOG's standing header), and an alias would
   need the module-placement and import-site-warning machinery
   deprecation.md §7 explicitly deferred — built for one release, on the
   seam that is moving. The steer on the existing failure path
   (analyzer.rs:24849) is one diagnostic family, deletable later, and it
   forces the fix rather than hiding it. Sub-question, if you want it
   batched: **should the migration wait for kolt's current arc to
   land?** Recommend yes — kolt's migration is beta trigger (a), and
   re-spelling under it mid-flight buys nothing.
