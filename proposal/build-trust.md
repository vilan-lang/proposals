# Build-code trust — two tiers (E96)

> Status: **RULED 2026-08-26** by the owner, both tiers as proposed. Tier 1
> BUILT the same day (cycle 30, work order 12, lane `build-trust`): the docs
> sentence landed in the book, the spec, the tour, the CLI appendix, and the
> hook's own code comment. Tier 2 is a **ruling with no enforcement point
> today** — dependencies cannot carry build hooks, so nothing enforces it and
> nothing needs to; it is the constraint that kolt.local 027 and the registry
> work (tracker §D item 5, "D5") build to. Tracker: `../tracker/backlog.md`
> §E item 96.
>
> The owner also required **strict security here before beta**, not at it —
> recorded as a standing bar in `beta.md` §2's "Before" list, alongside the
> sibling boundary findings (E93, E94, E95, L14, L15) and D5's registry as
> tier 2's enforcement point. This paper does not re-record that; it is
> beta.md's to hold.
>
> Provenance: filed by Order 11's `audit-1` lane (N16's first security pass)
> as E96, sharpened by the owner's question of 2026-08-26 — what does this
> actually need? — answered: formulate it now, in one short section, cheaply,
> because 027's `build.vl` / `vilan install` hook is the thing that needs it
> and the answer shapes that design.

## 1. Why this has its own paper

The subject is one sentence wide and three designs deep, and no existing
paper owns it. `library-packages.md` owns where a dependency's *modules* come
from, not what a dependency is allowed to do to your machine.
`distribution.md` ships the toolchain (npm, brew, marketplace) rather than
what the toolchain executes. `platform-model.md` is layers and backends;
`fullstack-dx.md` is E56's server-and-document charter. Grafting a security
doctrine onto any of them buries it at exactly the moment two future designs
need to cite it by name: `build-trust.md §3` reads right, and
`library-packages.md §8` does not.

The tracker is not the home either. Tracker items are archived to a
tombstone when they close, and this ruling has to outlive its item by
however long it takes the registry to exist.

## 2. Tier 1 — first-party build code runs, silently and unsandboxed

**Building a project executes its `[build] run` hooks with the developer's
own privileges.** No sandbox, no allowlist, no timeout, no prompt. This is
the same trust `cargo build`, `npm run`, or opening the folder in an editor
with a language server already assumes, and it is the same trust for the
same reason: the manifest is the developer's own file. **Vilan does not
prompt for code you wrote.**

That is carried by **a docs sentence, not a consent gate**. A first-run
consent gate was proposed alongside the sentence and **declined by the
owner** — the cargo-vs-make decision, made on purpose. A gate that fires on
your own manifest teaches one lesson only, which is how to dismiss gates.

### 2.1 What the mechanism actually is, verified

`BuildHooks::run` in `crates/vilan-cli/src/main.rs` hands each command to the
platform shell — `sh -c` on unix, `cmd /C` on Windows — with inherited
stdio, inherited environment, and the manifest's directory as the working
directory. It is reached from `vilan build`, `vilan run`, and every
`--watch`/HMR round; `vilan check` produces no artifacts and so runs none.
There is no allowlist, no sandbox, no timeout, and no environment scrubbing,
and the only validation is that a hook is not the empty string. The command
is echoed to stderr (`Running <command>`) before the spawn, unconditionally —
that echo is the whole honesty budget, and it is enough, because the
terminal always names what ran.

Two facts bound the blast radius today, and both are load-bearing for this
tier being *first-party* rather than merely *unsandboxed*:

- **Only the addressed manifest contributes hooks.** `Project::hooks`
  carries the hooks of the manifest that was resolved; a dependency's
  `[build] run` is never read, and a `[library]` declares none. A bare
  `vilan build file.vl` runs none at all.
- **Nothing fetches and then runs.** `vilan upgrade` is the only command
  that touches the network; a git dependency is fetched once and cached, and
  fetching it executes nothing.

### 2.2 What the docs said before, and what they say now

The audit's finding was not that the docs were wrong. It was that the
execution was *deliberate and documented in the code* — the shell choice,
the before-not-after ordering, the fail-loud rule all reasoned out in
comments — while **no user-facing page anywhere stated the consequence**.
The strongest sentence in the whole corpus was the book's "Each is a command
line for your shell (`sh -c` / `cmd /C`), so pipes, globs and `&&` work",
which describes capability and never authority.

Three places read *safer* than the truth, which is the sharper half of the
finding:

1. **The spec's inert halo.** `spec/platform.md` §11.4's `[build]` bullet
   opened "Build options never change program semantics (§7.6), only the
   emitted text" and then introduced `run` in the next sentence. True of
   `preset`/`indent`/`spaces`, catastrophically false of `run`, with nothing
   separating them. The same adjacency appeared in the LSP's `[build]` hover.
2. **The "step" framing.** The tour said `[build] run` "*names* a command",
   the book called a hook "a step Vilan doesn't do", and the on-ramp called
   the whole feature "pre-build commands" — all of which imply a slot in a
   pipeline Vilan owns rather than an unbounded command line.
3. **The network rule standing alone.** `appendix/cli.md` opened with "One
   rule up front: `vilan upgrade` is the only command that touches the
   network", presented as *the* statement of the toolchain's blast radius on
   the page that documents `vilan build`. It scoped the reader's threat model
   to the network and left local execution unmentioned.

The lane landed the sentence in four places, in each page's own voice — the
book's `guide/dev-loop.md` (where hooks are taught), `spec/platform.md`
§11.4 (because the spec is the contract), `tour/projects.md` (where the
"names a command" phrasing was), and `appendix/cli.md` (both under `vilan
build` and as the counterweight to the network rule) — plus the LSP's `run`
hover and a trust-model comment on `BuildHooks::run` that tells the next
reader the gate was declined on purpose.

## 3. Tier 2 — dependency-authored build code is a different tier

**Code a third party wrote, running at install or build time with your
privileges, does not run by default. It requires an explicit per-dependency
opt-in recorded in the manifest.**

This is the npm-postinstall class. The tier boundary is authorship, not
mechanism: the same `sh -c` that is unremarkable when it runs a line you
typed into your own manifest is a supply-chain execution primitive when it
runs a line a stranger shipped. Tier 1's justification — "the manifest is
yours" — simply does not extend, so neither does its silence.

Three properties the opt-in must have, ruled with it:

- **Per dependency, not per project.** A blanket "allow hooks" switch
  reconstructs the default it replaces.
- **Recorded in the manifest.** Not a flag, not an environment variable, not
  a remembered answer in a cache: a reviewable line in a file that lands in
  the diff, so granting a dependency execution is something a code review can
  see and a revert can undo.
- **Absent means no.** A dependency that declares a hook and has no opt-in
  builds fine and its hook does not run; that is a normal outcome, not an
  error to be dismissed.

**There is no enforcement point today.** Dependencies cannot carry hooks —
§2.1's `Project::hooks` never reaches a dependency's manifest — so this tier
ships as a constraint, not as code. Deciding it now was the point: it was
decided while the registry and 027 are still on paper, when the decision is
free.

## 4. What must build to this

- **kolt.local 027** (`../projects/kolt.local/tracker/items/027.md`) — the
  kolt-dogfood build-script design (`build.vl` / a `vilan install` hook). This
  is the near-term driver and the reason the ruling was taken early: an
  install-time hook raises tier 2's question at tier 2's stakes, and 027's
  paper needs to design against an answer rather than propose one. 027's
  **Trust** design question — which already states the tier boundary it was
  asking about, "first-party `build.vl` in your own manifest is a different
  trust tier than a dependency's hook" — is **answered here** and is no
  longer 027's to open: a `build.vl` the app's own manifest names is tier 1
  and runs; anything a dependency ships is tier 2 and does not. What stays
  027's are its other three questions (hook point, caching/idempotence, what
  the script sees), none of which this paper touches.
- **The registry (tracker §D item 5, "D5")** — tier 2's enforcement point,
  named as such in `beta.md` §2. A registry is what makes third-party build
  code reachable in the first place, so the opt-in's concrete manifest
  syntax, its resolution rules, and its interaction with transitive
  dependencies are the registry design's to specify, against §3's three
  properties.
- **`beta.md` §2** already holds the schedule half: strict security here is a
  standing bar the switch does not cross without. The reason is structural —
  beta is the posture in which somebody other than the author runs `vilan
  build` on code they did not write, so tier 2 stops being hypothetical
  exactly when the promise is made.

## 5. What this paper does not do

- It does not specify tier 2's manifest syntax. That belongs with the design
  that first has a dependency hook to opt into (§4), against §3's properties.
- It does not sandbox tier 1, or propose to. The ruling is that first-party
  build code runs as the developer; a sandbox would be a different ruling and
  would break every hook that exists to touch the filesystem.
- It does not add a consent gate anywhere. Declined, and the decline is
  recorded in the code so it is not rediscovered as an oversight.
- It does not restate `beta.md` §2's bar. Cited, not copied — one home each.
