# Build hooks and build-time accumulation — one staleness rule, one ordered channel (kolt.local 027 + 028)

> Status: DRAFT 2026-08-27 (cycle 34, work order 16, lane `build-hooks`), for
> owner review. Design-only: this lane wrote no production code. Its claims
> about compiler behavior were **probed** against a `target/debug/vilan` built
> this session from `next` at `48169ea7`; §0.2 lists every probe, and every
> claim in the paper is marked *verified* or *inferred*. Tracker:
> `../projects/kolt.local/tracker/items/027.md` and `028.md`; both should
> become PROPOSED with this paper as their record.
>
> **Trust is not this paper's to invent.** `build-trust.md` shipped E96 tier 1
> in Order 12 and carries tier 2 forward as a ruling with no enforcement point.
> §4 below **extends** that model in three places and re-decides none of it.
> Its §4 already answered 027's Trust question — a `build.vl` your own manifest
> names is tier 1 and runs — and this paper takes that as settled.
>
> **The paper's one-sentence answer**, since it is smaller than either item
> guessed: **both mechanisms already exist**, and what the items are actually
> asking for is a *policy* on each — a **staleness predicate** on the hook that
> `[build] run` already is, and a **declared order** on the accumulator that
> `asset::emit` already is. Neither ask needs a new execution model, a new
> command, or a second trust tier.
>
> **Ship note (2026-08-28, Order 17, lane `emit-kinds`):** §5.2's findings
> (a) and (d) are FIXED — backlog G5/G6. The cascade comparator is fenced to
> the `css` kind; **every other kind orders lexically by line**, chosen
> because it is a pure function of the contribution set (§5.1's rule) and
> exactly the bytes `emit_keyed(kind, line, line)`'s desugar produces for an
> un-keyed `emit` (§5.3) — S3 lands on these bytes unchanged. Emitted CSS
> held byte-identical across the corpus. The stale-flush prune shipped per
> Q7's recommendation, per kind: each flush records the kind files it wrote
> (`.vilan-asset-kinds` beside the outputs, removed with its last entry) and
> the next build prunes a recorded file whose kind emitted nothing — the
> pruner acts only on its own record, never on a filename it merely finds,
> and the general sweep stays filed with E92. (b) framing and (c) the
> per-leg unit are untouched, awaiting the §10 rulings.
>
> **Ship note (2026-08-28, Order 18, lane `build-hooks-s1s2`): S1 and S2
> BUILT**, on the §10 rulings. §3's predicate ships as written — the stamp at
> `dist/.build-hooks.json` (Q2), skipped hooks announced (`Fresh <name>`),
> `--rerun-hooks` on `vilan build`, and §3.2's unsoundness accepted and
> documented in the book, the spec and the code. §4.3's note ships as Q4 ruled:
> one dim line, once per build, naming the dependency, never a warning, exit
> code unchanged — and the opt-in is `build-hooks = true` on the dependency's
> own declaration (Q6), shipped refusing everything. Four things the paper
> underdetermined, decided in the building and recorded here as the paper's
> now:
>
> - **`inputs`/`outputs` are literal paths, and a glob is a manifest error.**
>   §2.1's prose writes `inputs = ["src/static/**"]`; §2.3's normative
>   declaration does not, and §3.1 digests *declared* paths. A pattern left
>   unmatched would digest as a file that is never there, match "missing"
>   forever, and freeze the hook after its first run — silently, which is the
>   one outcome this design cannot afford. So a declared path is a file **or a
>   directory** (digesting its whole tree, which is what the copy case
>   actually needs), and a `*`/`?`/`[` in one is refused with a message naming
>   the fix. No matcher, no dependency, and the failure is loud.
> - **The fingerprint is compared whole**, so adding, removing or renaming a
>   declared path is a change without a rule of its own. §3.1 lists the
>   conditions separately; comparing the recorded structure subsumes them.
> - **A hook's `run` takes a string or a list**, exactly as `[build] run`
>   does, rather than a lone string. One vocabulary across the three keys, no
>   refusal to write, no new parsing.
> - **Every stamp read failure is "no stamp".** A truncation, a hand edit, a
>   version this binary does not know: each costs one hook run and can never
>   cost a wrong build. That property is what makes the stamp cheap enough to
>   hand-roll its (small) JSON reader rather than grow the `vilan` binary a
>   dependency.
>
> **Not built, and why.** `emit_keyed` is S3's and was left alone. **Q5's
> second module root (`[package] generated`) is in no slice of §8** — S1
> through S5 never mention it — so it was not built and its module-resolution
> cost is still unmeasured; it needs a slice of its own before it needs a
> probe. G7's reserved-kind refusal belongs to a sibling lane and was not
> touched; the seam is `recordable_emit_kind`, which this lane did not go
> near. §9's watch-round pin is not built either: the freshness gate is
> per-round by construction (each round calls the same hook runner) and the
> e2e pins prove the transitions through repeated `build`/`run` invocations,
> but a pin that actually drives N watch rounds is still owed.
>
> **One silence this lane found and did not close.** In a `[project]`
> workspace, a *member's* own `[build] run` never runs — hooks come from the
> root manifest alone — and nothing says so. That is the §4.3 defect in a
> different place and a different tier (a member is the user's own code, so
> it is tier 1 being ignored, not tier 2 being refused). Filed here rather
> than fixed: whether a member's hooks should run is a real question about
> what a workspace build *is*, and it is not S1's or S2's.
>
> **Ship note (2026-08-28, Order 19, lane `emit-keyed`): S3 BUILT**, on Q3's
> ruling. `std::asset::emit_keyed(kind, key, line)` ships as §5.3 wrote it —
> the flush orders a kind by `(key, line)` and writes the line — and the
> paper's byte gate is met three ways: the corpus goldens (`.css` assets
> included) unchanged, every example-tree stylesheet byte-identical against a
> binary built from this lane's branch point, and a differential (inference
> pin + assets e2e) pushing one line set through both spellings and comparing
> the written files. Four things the paper left to the building, decided here
> and recorded as the paper's now:
>
> - **The identity is spelled ONCE, at the recording site.** `emit` and
>   `emit_keyed` share one interpreter arm: one fence call, one push, and the
>   un-keyed spelling contributes its line as its own key. §5.3's "one line of
>   desugar" is that line. This is what makes "nothing existing moves" a
>   property of the construction rather than a claim the tests have to
>   re-establish — there is no second path along which an existing kind's
>   bytes could move. The pin that holds it reads the CONTRIBUTION
>   (`an_unkeyed_emit_records_the_line_as_its_own_key`), because the assembled
>   file cannot distinguish a correct desugar from any other constant key.
> - **Dedup considers the key: the unit is the `(key, line)` PAIR**, as §5.3's
>   "a function of the set of `(key, line)` pairs" and §9's "dedup is per pair"
>   both say. One line under two keys survives twice — a ranked list repeating
>   an entry is the shape — and identical pairs collapse. For an un-keyed
>   `emit` the pair is `(line, line)`, so dedup-per-pair IS dedup-by-line, and
>   the shipped behavior is untouched.
> - **`css` REFUSES `emit_keyed`**, at the same const-time fence, with its own
>   message naming the cascade and `std::style`. §5.6 reserves `css` against a
>   build *hook* and G7's fence admits it for `emit`; the keyed spelling is the
>   third case and it is a refusal, because `assemble_assets`'s comparator
>   reads the line and never the key — a key accepted here would be silently
>   dropped, which is a wrong answer where a refusal costs nothing. It is also
>   what keeps §5.3's noted migration open: a key that had been quietly ignored
>   could not be given a meaning later without breaking whoever had passed one.
> - **The key gets NO validation of its own**, deliberately, and that follows
>   from the identity rather than from indifference. `emit`'s rules for a line
>   are none; since `emit(kind, line)` is `emit_keyed(kind, line, line)`, a key
>   validated more strictly than a line would start refusing `emit` calls that
>   have always been legal. The key is never written, so nothing downstream
>   constrains it either.
>
> **What is shared, and what could not be planted.** The kind fence stayed one
> function reading G7's one list — `build_owned_emit_kind` now has three
> consumers (the prune, `emit`, `emit_keyed`) and still one list — and the
> const-only set grew `emit_keyed` beside `emit`, so a runtime path reaching
> the keyed spelling is refused at the outermost crossing and NAMED for it.
> Four plants proved the new pins non-vacuous: a key-ignoring flush (reddens
> the four order/dedup pins), an un-keyed key that is not the line (reddens the
> recording pin, and — when made non-monotone — the differential), `emit_keyed`
> dropped from the const-only set (reddens all three fence pins), and `css`
> admitted (reddens the refusal). **The fifth plant does not exist by
> construction:** a flush-side re-derivation cannot be written, because the
> flush is handed only what `EmittedAsset` carries and the key→line relation is
> not invertible — two keys may share a line and one key may cover many. That
> is §11's rejected alternative made unreachable rather than merely declined.
>
> **Not built here.** S4's framing and prune-by-declaration, and S5's
> `build.vl`, are untouched. §5.3's CSS migration (`Style::rule` passing a band
> character as its key) stays out of scope and is now fenced against rather
> than merely unbuilt — taking it means changing the comparator and this
> refusal together, which is the right coupling.
>
> **Ship note (2026-08-29, Order 20, lane `genroot`): S6 BUILT** — Q5's
> generated root, with the formatter exclusion Order 19's lucide evidence run
> found. §12 is the whole design and it is new in this revision; the short
> version is that the ruling's two halves are one manifest key
> (`[package] generated`, and the same key on `[library]`), that `vilan fmt`
> and the language server's formatting handler both leave a `.vl` file under
> it byte-identical, and that this kills the fmt↔hook loop §12.1 states. Three
> things the building decided beyond the paper, recorded here as its now:
>
> - **The exclusion is a `vilan-core` predicate, not a CLI walk filter.** The
>   language server formats one buffer reached by its exact path; the CLI walks
>   directories. Only a predicate over a *path* can be the same rule in both,
>   so `manifest::generated_root_covering` is the one implementation and both
>   front ends call it. Filtering in the walker would have been smaller and
>   would have left format-on-save — §12.1's involuntary case — unfixed.
> - **`fmt`'s walker is NOT the exclusion point, deliberately.** `fmt` and the
>   watcher share `collect_vl_files`, and the watcher must keep seeing generated
>   modules: a generated `.vl` that changed is a source input that has changed,
>   and a round that ignored it would compile stale bytes. The exclusion is a
>   partition applied after collection, in `fmt` alone.
> - **A generated root does not have to exist**, and nothing checks that it
>   does. §12.3 argues it; the building confirmed the shape is free, because the
>   predicate is a prefix test over declared paths and never a filesystem probe
>   of the root itself.
>
> **Not built here.** The **module-root half of Q5** — making the generated root
> a second search root so `pkg::icons` resolves out of it — is measured in §12.6
> and left to its own slice. §12.6 also records the configuration that works on
> the shipped resolver today (`generated` as a subdirectory of `root`, reached
> as `<name>/lib.vl`), which is what keeps this slice from shipping a
> declaration with no consumer.

---

## 0. What already shipped, and why both items are smaller than they look

Item 027 opens "the ask: a `build.vl` file, configured in the manifest, that
`vilan build` executes for arbitrary code". Item 028 opens "the want on top of
[`emit`]: a build-time global variable that is built up over the course of the
build … then emitted to a file with `emit` in one step at the end."

Read against the tree, both sentences describe something that exists:

- **`[build] run` is build-time execution of arbitrary code.** It shipped as
  A9. It runs every command in the manifest's `[build] run` list, through the
  platform shell, in the manifest's directory, with the developer's full
  privileges, before every `build` / `run` / watch round. It is E96 tier 1 and
  the ruling that made it tier 1 is written on its own function.
- **`asset::emit` is a build-time accumulator with an arbitrary name.** The
  `kind` argument is not restricted to `css`. Any kind accumulates, deduplicates
  by line, orders canonically, and flushes to `<output>.<kind>` beside the
  bundle. The generalization item 028 proposes — "user-declared named
  accumulators" — is *the parameter that is already there*.

So the honest framing for both items is not "build this mechanism". It is
**"this mechanism has no policy, and the policy is the whole feature."**
That is what this paper designs.

### 0.1 The order's own principle, applied

Order 16's organizing principle is *a built app needs nothing but `dist/`*.
It bears on both items in a way neither item states:

- A hook's outputs are **inputs to the build**, never its artifacts. Anything
  a hook wants inside `dist/` goes there because the compiler put it there
  (029), not because the hook copied it. §6 turns this into 027's biggest
  scope cut.
- An accumulator's flush **is** a `dist/` artifact, and today a kind that stops
  being emitted leaves its last file behind (probe P8). A stale file in `dist/`
  is strictly worse than a missing one under this order's principle, because it
  ships.

### 0.2 The probes — what is verified, and what is inferred

Every probe ran against `target/debug/vilan` built this session from `next`
(`48169ea7`), in a scratch project outside every repo.

| # | Claim | Result |
|---|---|---|
| **P1** | `emit` takes an arbitrary kind; dedups by line; orders by content, not by write order | **VERIFIED.** Kind `index`; wrote `10 alpha`, `2 beta`, `10 alpha`, `1 gamma`, `zz delta` across two modules; got four lines in lexical order, `10 alpha` once. |
| **P1b** | Const-eval order does not leak into the bytes | **VERIFIED.** Swapping the two `import`s in the entry and rebuilding produced a **byte-identical** `main.index`. |
| **P2** | The flush comparator is CSS's, and it is applied to every kind | **VERIFIED.** A kind named `manifest` had its `@media (min-width: …)` lines reordered by numeric width, and a plain line beginning `z` (0x7A) sorted **before** them despite `@` being 0x40 — the `Option` key in the comparator forces every media line last regardless of bytes. A kind named `json` had two object lines sorted, which is the dead end for building a JSON array. |
| **P3** | `asset::read` is package-root-relative and refuses escapes | **VERIFIED.** `../../../etc/hostname` refused lexically, at the `const` expression, before any filesystem look. `data/note.txt` resolved against the **source root** (`src/`), not the project directory. |
| **P3b** | `asset::read` cannot carry binary | **VERIFIED.** A file with PNG magic bytes fails the build: *"stream did not contain valid UTF-8"*. |
| **P4** | `[build] run` re-runs on every build, with no caching | **VERIFIED.** Two consecutive `vilan build .` with no source change ran both hooks both times (an appending hook logged two lines). `vilan check .` ran none. |
| **P5** | A dependency's `[build] run` is ignored — **silently** | **VERIFIED.** A path dependency declaring `run = ["echo DEPENDENCY-HOOK-RAN"]` produced no output, no warning, no note. Only the app's own hook ran. |
| **P6** | A hook can generate a vilan module that the same build then compiles | **VERIFIED.** With `src/icons.vl` absent, a `[build] run` hook wrote it and `vilan run .` compiled and ran it in one command. Also verified: **modules are flat** — `pkg::generated::icons` does not resolve, so a generated module must sit directly under `root`. |
| **P7** | Accumulators are per **leg**, not per build | **VERIFIED.** A two-entry package emitting kind `routes` from both legs produced `dist/client.routes` and `dist/server.routes` as separate files. Neither appears in `dist/client.chunks.json`, so `serve_build` cannot see them. |
| **P8** | A kind that stops emitting leaves a stale artifact | **VERIFIED.** Removing the last `emit("routes", …)` from the server leg and rebuilding left `dist/server.routes` on disk, unchanged and unmentioned. |

Two claims in this paper are **inferred from source, not probed**, and are
marked as such where they are used: that macro expansion cannot touch the asset
channel (`interpreter::run_entry` constructs the interpreter with
`allow_assets = false`, and both `__emit_asset` and `__read_asset` refuse on
that flag), and that a `vilan build` can reach the network on a git-dependency
cache miss (`git_deps()` returns `GitDeps::fetching(…)` and is the policy
`build`/`check`/`run`/`test` all pass).

---

## 1. 027's mechanism already exists — it is called `[build] run`

### 1.1 What it does today, measured

`BuildHooks::run` hands each command to `sh -c` (or `cmd /C`), with inherited
stdio and environment, in the manifest's own directory, echoing `Running
<command>` to stderr first. It is reached from `build`, `run`, and every watch
round; `check` produces no artifacts and runs none (P4). A failure fails the
build, naming the command. There is no allowlist, no sandbox, no timeout, no
prompt — and that is a **ruling**, not an omission (`build-trust.md` §2).

Two of its properties matter more than the item credits:

- **It runs before the compile, so its outputs are compiled.** P6 proves the
  lucide pipeline end to end: with `src/icons.vl` absent from a clean tree, one
  `vilan run .` ran the generator, compiled the module it wrote, and printed the
  value out of it. Nothing about "generate vilan from external sources" is
  blocked today.
- **Only the addressed manifest contributes hooks.** P5 confirms
  `build-trust.md` §2.1's claim empirically: a path dependency's `[build] run`
  never ran. §4.3 is about the fact that it also never *said* so.

### 1.2 What the lucide case needs that this does not have

Take the motivating case literally — a script that downloads lucide, generates
a package's worth of icon views, and caches — and subtract what P6 already
delivers. Four things are left:

1. **It re-runs on every build.** P4. Downloading and regenerating a thousand
   icons on every `vilan build`, and on every watch round, is not "once, then
   cached"; it is the opposite. **This is the whole of the caching question,
   and it is the only one of the four that blocks the case outright.**
2. **The generated sources are indistinguishable from hand-written ones.**
   They land under `root`, flat (P6), with nothing marking them as products.
3. **The hook is shell, not vilan.** A cross-platform download-and-generate
   step written as a `sh -c` one-liner is a portability problem the manifest
   cannot see, and the generator cannot share a line of code with the app it
   generates for.
4. **Nothing in the build knows the generated files exist.** They are not
   declared, not tracked as build inputs, and not cleaned.

(1) and (4) are one problem. (2) is a naming decision. (3) is `build.vl` — and
it is the *last* of the four in importance, not the first, which is why §8
sequences it last.

### 1.3 The four asks that survive

027 asks for a hook point, a trust model, a caching rule, and a statement of
what the script sees. Answered in order: **§2** (one mechanism, and the trigger
falls out of the caching rule rather than being chosen), **§4** (E96 extended
in three places, no second model), **§3** (a declared-input staleness
predicate), **§4.5 and §6** (the script sees the filesystem and nothing else —
it has no artifact channel at all, because 029 owns that).

---

## 2. Hook point — one mechanism, and the trigger falls out

The item offers install-time and build-time and says *"possibly one mechanism
with two trigger points rather than a choice"*. The argument for one mechanism
is stronger than that: **there is one trigger point, and the two cases the item
names are two settings of the caching rule.**

### 2.1 Install-time is build-time with an empty input set

Ask what actually distinguishes the two cases in the item's own words. "Install
fits dependency-shaped generation (fetch once, generate, cache)"; "build fits
app-shaped work (029's resource copying)". Both descriptions are about **when
the inputs change**, and neither is about **what runs**. Fetch-once-and-cache is
a hook whose inputs never move. Copy-when-sources-changed is a hook whose inputs
are source files.

So state it as a predicate rather than a schedule. A hook declares what it reads
and what it writes; it runs when an output is missing or an input's digest has
moved, and is skipped otherwise (§3). Then:

- **The lucide case** declares `inputs = ["lucide.lock"]` (or nothing at all)
  and runs exactly once on a clean checkout, then never again — including
  across every watch round, which is the behavior the item asks for.
- **The copy case** declares `inputs = ["src/static/**"]` and runs when they
  move.
- **Today's behavior** is the case with **no declaration**: run every time. That
  is what makes the change backward-compatible to the byte.

One trigger point, before the compile, where `[build] run` already is. The two
"trigger points" the item was choosing between are the two ends of one dial.

### 2.2 The two honest arguments for a `vilan install` command, and why neither survives

**"Install is where the network is."** It is not, and has not been since git
dependencies shipped. `vilan build` fetches a declared git dependency on a cache
miss — shelling to `git`, with the user's own credential helpers, `insteadOf`
rewrites and SSH keys (*inferred from `git_dep.rs` and `git_deps()`; not
probed*). `appendix/cli.md` states this accurately in its second clause, and the
network threshold an install command would supposedly guard is already behind
`vilan build`.

**"Install is where consent happens."** This is the real argument, and
`build-trust.md` §3 already spent it: tier 2's opt-in is *recorded in the
manifest* — "not a flag, not an environment variable, not a remembered answer in
a cache: a reviewable line in a file that lands in the diff." A line in the
manifest **is** the consent moment, it survives a fresh clone, and it is
reviewable by someone who was not at the terminal. A command that prompts is the
weaker instrument, and §2's ruling declined a prompt on exactly this ground.

There is no third argument. `vilan install` is a **non-goal** (§7), recorded
as a decision.

### 2.3 The declaration

Today's `run = [...]` list has no place to hang per-hook facts, so the design
adds the array-of-tables form beside it, with the string/list form unchanged:

```toml
[build]
run = ["npx tailwindcss -i src/app.css -o src/generated.css"]   # unchanged: every build

[[build.hook]]
name    = "lucide"
run     = "sh scripts/lucide.sh"
inputs  = ["scripts/lucide.sh", "lucide.lock"]
outputs = ["src/icons.vl"]
```

`name` is required in the table form and is what every message and the stamp
file key on. Hooks run in declaration order, `run = [...]` entries first,
exactly as today.

---

## 3. Caching and idempotence — the staleness predicate

### 3.1 The stamp

After a hook runs, the build records, under its name: the digest of the hook's
command string, the digest of every declared input (with `None` for a declared
input that was **missing**, recorded exactly as `asset::read`'s
`ProjectReader` already records its misses — a file that was not there is a
dependency, and its appearance must invalidate), and the digest of every
declared output.

A hook is **fresh** — and skipped — when it has a stamp, every declared output
exists and re-digests to its recorded value, every declared input re-digests to
its recorded value, and the command string is unchanged. Otherwise it runs.

Content, never mtime. That is not a new rule in this tree: the watch loop's leg
reuse already decides by content and says why — *"Reuse is decided by CONTENT,
never by mtime: a leg qualifies only when every source its artifact was compiled
from re-hashes, right now, to the hash it was compiled with"*. A hook stamp that
trusted mtime would be the same bug the watcher already refused.

A hook with **no `inputs` and no `outputs`** is never fresh and always runs.
That is today's behavior, and it is the default.

A skipped hook prints one dim line (`Fresh lucide`), not silence. A build that
quietly stops running a step the manifest declares is the failure mode this
whole design has to avoid, and the echo is what `BuildHooks::run` already
treats as its honesty budget.

### 3.2 The known unsoundness, and why it is smaller than today's

The digest is over **declared** inputs. A hook that reads a file it did not
declare can be skipped when it should have run. Say it plainly rather than
hedge it:

- **The failure is a stale artifact, not a wrong program.** A generated
  `src/icons.vl` that is one revision behind still compiles as itself; the
  compiler hashes what it actually read, and every downstream reuse decision
  keys on that. There is no path where the build believes it compiled bytes it
  did not compile.
- **`--rerun-hooks` is the escape**, and `vilan build` with a changed manifest
  already forces a full round, so editing the hook's own declaration re-runs it
  by construction.
- **The comparison is not against a sound system.** Today's hook has no
  staleness story at all: it runs every time, which is *always* correct and
  *never* cheap. The design trades a bounded, escapable staleness for the case
  the item exists to enable, and a hook that declares nothing keeps the old
  behavior exactly.

### 3.3 Where the stamp lives

`dist/.build-hooks.json`, in the project's own `dist/`. Not `~/.vilan/`: a
machine-global cache keyed on a project path is the thing nobody can reason
about from a clone, and a stale one is unreachable to `rm -rf`. Putting it in
`dist/` makes `rm -rf dist` mean *rebuild everything, hooks included*, which is
the sentence a user already believes. Q2 in §10 puts this to the owner.

---

## 4. Trust — extending E96, not restating it

`build-trust.md` ruled two tiers on 2026-08-26 and this paper adopts them
without amendment. Its §4 already discharged 027's Trust question: *"a
`build.vl` the app's own manifest names is tier 1 and runs; anything a
dependency ships is tier 2 and does not."* Nothing below reopens that. Three
things below **extend** it, each because building 027 puts the model somewhere
`build-trust.md` could not see from where it stood.

### 4.1 A `build.vl` is tier 1, and a staleness gate does not change that

A skipped hook is not a security property and must never be described as one.
Freshness is a cost optimization over code that is already trusted to run. If
a hook is dangerous, running it once is the whole of the damage. Recorded here
so nobody later reads `inputs`/`outputs` as a fence.

### 4.2 The sharpening: tier 2's threshold is the git dependency, not the registry

`build-trust.md` §3 says *"There is no enforcement point today. Dependencies
cannot carry hooks … so this tier ships as a constraint, not as code"*, and §4
names the registry as the enforcement point.

The second half needs sharpening, and 027 is the reason. **Third-party code
already reaches the machine.** Git dependencies shipped: a `vilan build` of a
project declaring one fetches a stranger's repository into
`~/.vilan/`, shelling to `git` with the user's credentials, and compiles it.
The only thing standing between that and the npm-postinstall class is one line
of Rust — `Project::hooks` reads the addressed manifest's hooks and no other's.

That relocates the deadline. Tier 2 does not become live when a registry
exists; **it becomes live the first time a dependency's hook is read**, and
that is 027's decision to make, not the registry's. The registry raises the
*volume* of third-party code, not its *kind*.

Two consequences:

- **The opt-in syntax is this design's to specify**, not deferred to a design
  that does not exist. §8's S2 specifies it and ships it *refusing everything*,
  so the syntax is fixed and reviewable before anything can cross it.
- **A precision note on the citation.** `build-trust.md` §4 names "the registry
  (tracker §D item 5, 'D5')" as tier 2's enforcement point. §D item 5 in
  `tracker/backlog.md` is **"Public traction plan"**, and `distribution.md` §5
  says explicitly that *"A true registry is a D5-era decision, demand-gated"* —
  there is no registry item, in §D or anywhere. So tier 2 as written is pinned
  to an enforcement point that is not scheduled and not tracked. That is a
  second, independent reason to specify the opt-in here.

### 4.3 The sharpening: "absent means no" has to be *said*

`build-trust.md` §3's third property is *"Absent means no. A dependency that
declares a hook and has no opt-in builds fine and its hook does not run; that
is a normal outcome, not an error to be dismissed."* Right, and P5 shows what
that looks like today: **nothing at all**. The dependency's `run = ["echo
DEPENDENCY-HOOK-RAN"]` produced no output, no warning, no note; the manifest
key was never read.

Under tier 2 that silence is a defect of a specific kind. "Absent means no" and
"the toolchain did not notice" are indistinguishable from the terminal, so:

- A user who *wanted* the hook debugs the dependency, the shell, and their PATH
  before suspecting a policy they were never told about.
- A user who did *not* want it learns nothing about a dependency that is asking
  for execution — which is exactly the fact a supply-chain-conscious reader
  most wants surfaced.

**The extension: a dependency that declares a build hook and has no opt-in
prints one line, once per build, naming the dependency.** A note, not a warning
— it is a normal outcome, and §3's own words forbid making it an error to be
dismissed. This is the same move `build-trust.md` §2 made for tier 1: the fix
for an undocumented consequence is a sentence, and the terminal always names
what happened.

### 4.4 What a vilan-authored `build.vl` does not buy

A hook written in vilan runs under an interpreter whose capability model
(`const-eval.md` §2) is narrower than a shell's by construction. It is tempting
to sell that as containment. **Do not.** Two reasons, both recorded as
decisions:

- **Tier 1 is trusted, so containment on it buys nothing.** `manifest.rs` makes
  exactly this argument about path dependencies already: *"Against a manifest
  that can execute arbitrary shell, a rule about which directory it may name
  reads a package it was free to run code from anyway — it buys nothing and,
  worse, advertises a containment property the trust model explicitly declines
  to offer."* A capability list on a first-party `build.vl` is the same
  advertisement.
- **A `build.vl` that could not touch the filesystem or the network would not
  do the job.** The lucide case is a download and a write. A hook's capability
  set is therefore "the process leg of std", which is a shell with better
  syntax, not a sandbox.

What `build.vl` *does* buy is real and worth having on its own: it is
reviewable in the language of the project, it is cross-platform without a
`cmd /C` branch, it can share types and code with the app it generates for, and
it is `vilan fmt`-able and LSP-visible. Those are ergonomics claims, and they
are the honest ones.

### 4.5 The seam: a hook makes files, const-eval makes lines

027 asks for the seam between "const-eval inside the compiler" and "a real
process the build spawns" to be stated, *"since both generate build output"*.
Here it is, as one rule:

> **A hook produces files, which are build inputs. Const-eval produces lines,
> which are build artifacts. Nothing crosses between them except through the
> filesystem, and every crossing is a declared `outputs` entry.**

Three properties fall out, and they are why the rule is worth writing down:

- **Ordering is total and needs no coordination.** Every hook runs before any
  `const` runs, because hooks run before the compile. There is no interleaving
  to order and no race to lose.
- **The compiler stays the only writer of `dist/`.** A hook that wants
  something in `dist/` writes a file the compiler then carries there (029).
  Under Order 16's principle that is not a restriction; it is the point.
- **The channel keeps its determinism story.** `const-eval.md` §9.5 rests on
  there being no clock and no io in the const world. A hook may fetch; a
  `const` may not, ever. §7 records that as permanent.

---

## 5. 028 — the accumulator already generalized; the ordering did not

### 5.1 std's CSS pipeline, read as the template

The item's guess is right, and the code says so plainly. `Style::rule` is
described in its own doc comment as *"the one chokepoint"*: it hashes the slot,
calls `emit("css", render_rule(…))`, and returns a new `Style`. Every style in
the program contributes through it, from wherever it happens to construct.
`assemble_assets` then flushes.

But the mechanism that makes it deterministic is not the one the item names.
It is not that the flush is sorted. It is that **every contribution is a
self-contained line whose content determines its position**, so the output is a
function of the *set* of contributions and never of the sequence. The dedup and
the sort are two ways of saying the same thing: the write order is not an input.

P1b measures it. Swapping two `import` statements in the entry — which changes
the order modules are walked and therefore the order `const_exprs` is
populated — produced a **byte-identical** asset file.

That is the design rule for 028, and it is the only one that matters:

> **No accumulator ever gets "the order I called `emit` in". Every order must
> be a function of the set of contributions.**

### 5.2 Four gaps, each measured

The generalization the item proposes — user-declared named accumulators — is
already there: `kind` is a free parameter, fenced only to one path segment
because it becomes a filename (E94). P1, P2 and P7 used the kinds `index`,
`manifest`, `json` and `routes` without touching the compiler. What is missing
is the policy:

**(a) One comparator, applied to every kind.** `assemble_assets` sorts lexically
with a numeric override for `@media (min-width: …)`. Its doc comment justifies
this *as CSS*: `'.' < ':' < '@'` gives the cascade bands, and the numeric
override fixes B35's `1024px`-before-`640px` bug. All correct — and all a CSS
cascade rule. P2 applied it to a kind named `manifest` and watched a line
beginning `z` sort **before** two `@media` lines, because the sort key is
`(Option<width>, line)` and `None` precedes `Some` — so every media line lands
last regardless of its first byte. Harmless for CSS, where nothing else starts
above `@`. Arbitrary for anything else.

`const-eval.md` §3 already promises the fix: it says the channel *"orders
deterministically — **a kind-specific rule**"* and names license manifests and
service-worker precache lists as riders. The implementation has one rule. **028
is that promise being kept**, and it should be argued as a documented-behavior
gap rather than as a new feature. *(FIXED 2026-08-28 — backlog G5; the ship
note above records the chosen non-css rule.)*

**(b) No framing.** Lines are joined with `\n` plus a trailing newline. There is
no header, no footer, no separator choice. P2's `json` kind is the dead end made
concrete: two object lines come out sorted and comma-terminated, and there is no
way to open a bracket, close it, or drop the last comma. Any format that is not
a line-oriented text file is out of reach.

**(c) The unit is a leg, not a build.** P7: a two-entry package emitting the
same kind from both legs produced `dist/client.routes` and `dist/server.routes`
as separate files, because each leg is a separate compile with its own asset
vector. The item's "over the course of the build" is ambiguous, and today's
answer is the narrower one. `const-eval.md` §3 states this correctly (*"a
two-target build evaluates consts per compile"*), so it is a limit, not a bug —
but 028 should not be read as promising a cross-leg accumulator.

**(d) Stale flushes are not pruned.** P8: deleting the last `emit` for a kind
and rebuilding left the previous file in `dist/`, unchanged and unmentioned.
Under Order 16's principle that is the worst of the four, because the stale file
ships. It is also E92's shape (a stale superseded `dist` artifact after a
rename), which is already filed. *(FIXED 2026-08-28 — backlog G6, the per-kind
half of Q7; the general sweep stays with E92.)*

### 5.3 The answer: the contribution carries its key

*(BUILT 2026-08-28, Order 19, lane `emit-keyed` — S3. The ship note above
records the four things the building decided: the identity spelled once at the
recording site, dedup per `(key, line)` pair, `css` refusing the keyed
spelling, and no validation on the key.)*

The smallest surface that closes (a) without inventing an ordering language:

```vilan
// std::asset — the ordered sibling of `emit`.
fun emit_keyed(kind: str, key: str, line: str): void;
```

The flush sorts by `(key, line)` and writes `line`. `emit(kind, line)` becomes
exactly `emit_keyed(kind, line, line)` — today's behavior, spelled as a special
case of the general one, so nothing existing moves and the CSS sheet is
byte-identical by construction.

Why this and not a manifest `order = "…"` key, or a comparator:

- **The key is a property of the contribution, and the contributor is the only
  code that knows it.** A route's sort key is its path; an icon's is its name; a
  ranked entry's is a zero-padded index. Nothing at the flush can compute those
  from the line without re-parsing the line, which is the invented second source
  of truth this tree refuses on principle.
- **It preserves the determinism rule exactly.** The key is a const-time value.
  The output stays a function of the set of `(key, line)` pairs, and write order
  still cannot leak.
- **It costs one function and one line of desugar**, and it is a strictly
  additive change to a channel with one existing consumer.

The keyed form also gives CSS a migration it does not need but could take:
`Style::rule` could pass a band character as its key instead of relying on
`'.' < ':' < '@'`, which would let the load-bearing comment on `render_rule`
stop being load-bearing. Out of scope here, noted so the option is not lost.
*(As built, `emit_keyed("css", …)` is REFUSED rather than ignored, which is
what keeps this migration takeable: the comparator and the refusal would change
together, where a key that had been silently dropped could never be given a
meaning afterwards.)*

### 5.4 Framing belongs to the manifest, order belongs to the contribution

For (b), the split is deliberate:

```toml
[build.asset.routes]
extension = "json"       # dist/<leg>.json rather than dist/<leg>.routes
header    = "["
footer    = "]"
join      = ",\n"
```

Order is a contribution property, so it is spelled at the contribution
(`emit_keyed`). Framing is an output-file property, so it is spelled where the
build's other output facts live. Each fact stays where its author is, and
neither surface has to grow the other's vocabulary.

A kind with no `[build.asset.<kind>]` table keeps today's framing exactly:
`\n`-joined, newline-terminated, `<output>.<kind>`.

### 5.5 Should the hook own aggregation instead? No — and the CSS pipeline is the proof

The item records the alternative — *"a build script (027) owns the aggregation
outright"* — and it should be refused, on evidence rather than taste.

**Aggregation's entire value is that the contributors are inside the program.**
A hook is a process. It sees the filesystem; it does not see a `Style::rule`
call inside a component three modules deep, a route registered by the module
that defines it, or an icon referenced from one branch of a `match`. To
aggregate those, a hook would have to parse and analyze vilan — that is, be the
compiler.

The CSS sheet is the existence proof. Nothing outside the compiler could have
produced it: its lines come from wherever styles happen to construct, its dedup
is what lets independent constructions compose, and its class names are hashes
of slots that only the const evaluator ever computes. Handing that to a script
would mean writing a second front end.

So: **aggregation stays in the const world; the hook consumes its output the
way it consumes any other file.** That is §4.5's seam, arrived at from the other
side, which is a good sign for the seam.

The corollary is the item's own closing line, inverted: 028 does **not** close
into 027 if 027 lands first. They are different mechanisms answering different
questions, and 028 is the smaller and better-founded of the two.

### 5.6 The reserved kind

`css` is reserved. A manifest declaring `[build.asset.css]` is an error that
names `std::style` and says the sheet's framing is the styling system's. The
reason is `assemble_assets`'s own documented soundness argument: the sort and
the band order are a cascade property, and a user-supplied header, footer or
join would break the sheet in ways nothing else in the build could detect.

*(As built, `css` is now THREE answers rather than one, from the same argument.
The per-kind prune refuses it — the sidecar is `sweep_stale_sidecar`'s file
(G6). `asset::emit` ADMITS it — the styling system's own writes go through that
door (G7). `asset::emit_keyed` REFUSES it, Order 19's S3: the same sentence
above about the sort being a cascade property says a contribution's key has
nowhere to apply here, and a key silently ignored is a wrong answer where a
refusal costs nothing. The manifest table of §5.4 is still S4's and still
reserved. All three read one list, `const_eval::build_owned_emit_kind`, and
differ only in what they do with its answer.)*

---

## 6. Does 029 make 027 smaller? — the cross-lane answer

**Yes, in one specific place, and the paper shrank there. No, in the place the
item's motivating case actually lives.**

### 6.1 What 029 absorbs

027's fourth design question presumes *"an artifact channel into `dist`"* for
the hook. **029 takes that whole question away.** Its import-file mechanism is
the compiler-side registration of a file as a build artifact, riding the
`BuildAsset` pipeline that `serve_build` already consumes, with reachability
(unreferenced files do not ship) and fingerprinting available where names are
minted. A hook copying files into `dist/` would be the same feature with none
of those properties — no reachability, no manifest entry, and the app still
resolving paths itself.

The order's own principle settles it: `dist/` has one writer, and it is the
compiler. **027 gets no output channel at all.** That is this paper's largest
cut, and §7 records it as a non-goal rather than an omission.

The input direction is likewise already covered and does not need duplicating.
`std::asset::read` is the const INPUT channel: package-root-relative,
escape-refused before any filesystem look, const-only, and every read — hit and
miss alike — recorded as a tracked build input that the watcher rounds on (P3).

### 6.2 The three things it cannot absorb, each measured

029 does **not** shrink 027's motivating case, for three reasons that are facts
about the tree rather than judgments:

1. **`asset::read` returns `str` and refuses non-UTF-8** (P3b: a file with PNG
   magic bytes fails the build with *"stream did not contain valid UTF-8"*). It
   cannot carry a PNG, a font, or a favicon — which is to say it cannot carry
   most of `src/static/` in kolt, which holds five `.png`s, a `.ico` and an
   `asset/` and a `font/` directory beside its two text files. 029 therefore
   needs its own bytes-carrying registration regardless of `read`. The *output*
   half of that is ready — `BuildAsset.content` is `Bytes` end to end since
   kolt.local 030, and the comment recording why measures the damage on kolt's
   own favicon: 483 bytes on disk, 853 after a lossy UTF-8 decode — and the
   *input* half is 029's to build. **This is a finding the `asset-bundle` lane
   should have before it commits to a framing.**
2. **Nothing in the const world reaches the network.** `check_capabilities`
   refuses `[extern]` host bindings and the impure helpers; there is no clock in
   the host table at all. That is not an oversight to route around — it is what
   `const-eval.md` §9.5's determinism rests on. lucide is a **download**, and no
   const function will ever perform one.
3. **Nothing in the const world produces vilan source.** `emit` writes an asset
   file that is never compiled. Macros — the one mechanism that creates items
   and types — are fenced out of the asset channel in both directions:
   `interpreter::run_entry` constructs the interpreter with `allow_assets =
   false`, and both `__emit_asset` and `__read_asset` refuse on that flag
   (*inferred from source; not probed*). So a macro cannot read a file, and a
   `const` cannot write code.

Which leaves exactly one implementation of "generate vilan from external
sources", today and under 029: **a process that runs before the compile and
writes `.vl` files under `root`** — verified end to end by P6.

### 6.3 What the paper shrank, concretely

- 027 has **no artifact channel** and no `dist/` interaction. §7.
- 027 has **no read channel**. `asset::read` is the const input side and needs
  nothing from a hook.
- 027's remaining core is three things: **run once, know when to run again, and
  say what it produced.** That is §3, and it is why S1 is the first slice.

---

## 7. Non-goals

Each recorded so that declining it is a decision, not an omission.

- **A `vilan install` command.** §2.2: the network threshold is already behind
  `vilan build`, and the consent moment is a manifest line by E96 §3's own
  ruling. The staleness predicate makes install-time a setting, not a command.
- **An artifact channel for hooks.** §6.1. `dist/` has one writer. A hook that
  wants a file shipped writes it where 029 can register it.
- **A sandbox, allowlist, timeout or prompt on a first-party hook.**
  `build-trust.md` §2 and §5 declined all four; a `build.vl` written in vilan
  does not reopen it, and §4.4 refuses to advertise its capability model as
  containment.
- **Dependency hooks actually running.** S2 fixes the syntax and the silence.
  Letting one execute is a later decision with its own gate, and "absent means
  no" is the shipped behavior in the meantime.
- **Any network capability in the const world.** Permanent. §4.5 and
  `const-eval.md` §9.5.
- **Ordering by contribution sequence.** No accumulator ever gets the order
  `emit` was called in. §5.1.
- **Cross-leg accumulators.** P7's per-leg unit stays; a whole-build accumulator
  would need a flush phase after every leg compiles, and nothing has asked for
  one.
- **Binary output from `emit`.** The channel is lines of text, and its dedup and
  sort are line operations. Bytes are 029's.
- **Retiring or changing `[build] run`.** It does not move. A hook with no
  `inputs`/`outputs` behaves exactly as it does today, byte for byte and line
  for line.
- **A hook that post-processes the emitted bundle.** `BuildHooks`'s own comment
  already declares this a different feature; nothing here changes that.
- **A lockfile, a resolver, or a dependency-graph pass over hooks.** Hooks run
  in declaration order; there is no hook-to-hook dependency edge in v1.

---

## 8. Slices

Suite-gated, docs in the same commit, per-case pins. The first slice is
standalone and needs no ruling on anything else in this paper.

- **S1 — the staleness gate on the hook that exists.** *(BUILT 2026-08-28, Order 18.)* `[[build.hook]]` with
  `name`/`run`/`inputs`/`outputs`; the `dist/.build-hooks.json` stamp; skip when
  fresh with a dim `Fresh <name>` line; `vilan build --rerun-hooks`. **No new
  language surface, no `build.vl`, no install command, no trust change.**
  *Standalone value:* today every hook re-runs on every build and every watch
  round (P4), so a Tailwind bridge, a codegen step or a resource pipeline pays
  full cost on every keystroke-triggered round. This slice makes an expensive
  hook free on the common path, and it is 027's entire caching answer delivered
  first. It ships value even if the owner rules against `build.vl` outright.
  Gate: a hook with no declaration runs on every build exactly as before; a
  declared hook runs once, then is skipped until an input moves; a missing
  declared output re-runs it; a changed command string re-runs it.
- **S2 — the tier-2 boundary, said and spelled.** *(BUILT 2026-08-28, Order 18; the opt-in is `build-hooks = true` on the dependency's own declaration.)* The per-dependency opt-in key
  in the manifest, parsed and validated, against `build-trust.md` §3's three
  properties (per dependency, recorded in the manifest, absent means no); the
  one-line note when a dependency declares a hook with no opt-in (§4.3). **No
  dependency hook runs in this slice** — every one is still refused. The point
  is to fix the syntax and end the silence (P5) before anything can cross.
  Gate: a dependency hook with an opt-in present still does not run, and says
  so; a dependency hook with no opt-in prints exactly one line naming the
  dependency; neither case changes the build's exit code.
- **S3 — `emit_keyed`, and the CSS byte gate.** *(BUILT 2026-08-28, Order 19,
  lane `emit-keyed`; the ship note above records what the building decided.)*
  The one-function ordered surface
  in `std::asset`; `emit` implemented as `emit_keyed(kind, line, line)`; `css`
  reserved. **The gate on the whole slice: byte-identical emitted CSS across the
  corpus and the whole example tree.** This is the slice that keeps
  `const-eval.md` §3's "kind-specific rule" promise. *(Met: the corpus goldens
  hold `.css` bytes directly, and every example-tree stylesheet was hashed
  against a binary built from the branch point and came out identical.)*
- **S4 — declared accumulators: framing and pruning.** `[build.asset.<kind>]`
  with `extension`/`header`/`footer`/`join`; kinds with no table keep today's
  framing verbatim; the stale-flush prune (P8) so a kind that stops being
  emitted stops shipping. Gate: an undeclared kind's bytes are unchanged; a
  declared kind round-trips through a real format (a JSON array is the fixture,
  since P2 shows it is unreachable today); a removed kind's file is gone from
  `dist/` after one build.
- **S5 — `build.vl`.** The hook body written in vilan, executed by the
  toolchain's own interpreter with the process leg of std, declared as
  `[[build.hook]] script = "build.vl"` beside `run`. Last on purpose:
  everything above is what makes it cheap (S1), safe to extend to dependencies
  (S2), and unnecessary as an aggregation mechanism (S3/S4) — and it is the
  slice most likely to be ruled differently. Gate: a `build.vl` and the
  equivalent `run` one-liner produce byte-identical outputs and identical
  stamps.

- **S6 — the generated root, and the formatter's exclusion.** *(BUILT
  2026-08-29, Order 20, lane `genroot`; §12 is the design, and the ship note
  above records what the building decided.)* Q5's ruled declaration —
  `[package] generated` (and the same key on `[library]`) — parsed and
  validated, with `vilan fmt`, `vilan fmt --check` and the language server's
  formatting handler all leaving a `.vl` file under it byte-identical, through
  one shared predicate. **The gate on the slice is the loop:** a hook whose
  declared output `vilan fmt` would reformat stays `Fresh` across a
  build → fmt → build cycle. The **module-root half** of Q5 (the generated root
  as a second search root) is measured in §12.6 and is not in this slice.
  *Standalone value:* the loop §12.1 states is live in the shipped tree today,
  it is silent from both sides, and format-on-save runs it without anyone
  typing a command — so this slice is a defect fix before it is a feature, and
  it does not wait on module resolution because the loop does not involve one.

S1 through S4 are independent of S5 and of each other in the sense that
matters: none of them requires a ruling on any of §10's questions except its
own. S6 is likewise independent: it is the half of Q5 that needs no compiler
change, and §12.6 records why taking it first is the right order rather than a
convenient one.

---

## 9. Test plan (per case, as always)

- **Manifest parsing** — the table form beside the string and list forms; a
  `[[build.hook]]` with no `name` refused, naming the key; duplicate names
  refused; `inputs`/`outputs` accepting a bare string and a list; an empty
  command still refused (the existing pin); a `[build.asset.css]` table refused,
  naming `std::style`; an unknown key in either table refused the way unknown
  `[build]` keys already are.
- **Staleness, one pin per transition** — cold run (no stamp); fresh skip; input
  digest moved; input **appeared** where it had been recorded missing; output
  deleted; output edited by hand; command string changed; `--rerun-hooks`; a
  hook with no declaration running on every one of three consecutive builds; a
  failing hook leaving **no** stamp, so the next build re-runs it.
- **Watch rounds** — a declared hook runs once across N rounds while its inputs
  are untouched, and runs again on the round after one moves. This is the pin
  that proves the lucide case, because the watch loop is where P4's cost is
  worst.
- **Hook/compile ordering** — the P6 case as a fixture: a generated module
  absent from a clean tree, present and compiled after one command; the
  generated file recorded as a build input; a second build with the module
  present skipping the hook and still compiling.
- **Tier 2 boundary** — a path dependency declaring a hook, with and without an
  opt-in: neither runs; the no-opt-in case prints exactly one line naming the
  dependency; the opt-in case parses and is refused with its own message; the
  line appears once per build, not once per member; the exit code is unchanged
  in every case. The P5 fixture, promoted from a probe to a pin.
- **`emit_keyed`** — same key, different lines (stable secondary sort on the
  line); different keys, same line (both survive, dedup is per pair); identical
  pairs deduped; keys that are not lexically ordered by their lines (the case
  plain `emit` cannot express); a key computed from a const function; the
  const-only fence refusing `emit_keyed` outside a `const` exactly as it refuses
  `emit`.
- **Determinism — the arc's headline gate** — P1b promoted to a pin, per kind: a
  program's asset files are **byte-identical** across a rebuild after its
  entry's `import` order is permuted, and after a module is added that emits
  nothing. Plus the standing one: **byte-identical emitted CSS across the whole
  corpus and example tree** on every slice.
- **Framing** — an undeclared kind byte-identical to today; a declared kind with
  header/footer/join producing a valid JSON array (the P2 dead end, closed); a
  declared `extension` renaming the file and *not* colliding with the bundle or
  the chunks manifest; the prune removing a kind's file when the last `emit` for
  it goes away, and **not** removing the bundle, the chunks manifest, or a file
  the compiler did not write.
- **Per-leg** — P7 promoted: a two-leg package emitting the same kind produces
  two files with the two legs' own contents, and each leg's framing is applied
  independently.
- **The generated root** — the manifest pins: the key parses on `[package]` and
  on `[library]`; an absent key is today's behavior; a root that escapes the
  package (`../gen`) is refused lexically, naming the key; an absolute root is
  refused; `generated = "."` is refused; `generated` equal to `root` is refused
  naming both keys; a root that does not exist yet is **accepted** (a clean
  checkout is the normal case). The formatter pins: a file under the root is
  left byte-identical by `vilan fmt`; the same file is not reported by
  `vilan fmt --check`, which still exits zero; a file **outside** the root under
  the same package still formats (the negative that makes the others
  non-vacuous); a file under the root named explicitly on the command line is
  still left alone; the note appears once per run and names the root, and does
  not appear when the exclusion skipped nothing.
- **The loop — S6's headline gate** — a `[[build.hook]]` whose declared output
  is a `.vl` file the formatter would reformat, driven end to end: build (the
  hook runs), `vilan fmt` (the file is untouched), build again — the hook is
  **`Fresh`**, and the generated bytes never moved. Planted against the
  exclusion removed, where the same cycle re-runs the hook, which is the defect
  in the shipped tree.
- **Docs gate** — every example in this paper's final book page compiles;
  `appendix/cli.md`, `guide/dev-loop.md` and `spec/platform.md` §11.4 each carry
  the freshness rule in their own voice, beside the trust sentence E96 already
  put there, and the same three carry the generated root and its exclusion.

---

## 10. Open questions for the owner

> **RULED 2026-08-28 (the owner): all seven as recommended.** Q1 — S1
> first, `build.vl` decided on evidence. Q2 — the stamp lives in `dist/`.
> Q3 — `emit_keyed`, the contribution carries its key. Q4 — one dim line,
> once per build, naming the un-opted-in dependency. Q5 — a second module
> root (`[package] generated = "generated"`), auto-gitignored by
> `vilan init`; still flagged as the highest-unknown-cost piece (module
> resolution). Q6 — **tier 2's threshold is the git dependency, i.e.
> now**: the opt-in is specified in S2 and ships refusing everything, and
> the registry inherits the syntax. Q7 — per-kind (already built as G6's
> fix in Order 17); the general sweep stays filed with E92. The same
> ruling accepted G7's recommendation: the reserved-kind refusal at emit
> time (§5.6), built from the pruner's own predicate list.

**Q1. Does `build.vl` get built at all, or is `[build] run` plus a staleness
gate the whole answer?** S1 delivers every blocking property of the lucide case
(§1.2) without one line of new language surface; `build.vl`'s remaining value is
ergonomics — cross-platform, reviewable, shares code with the app.
*Recommendation:* **build S1 first and decide `build.vl` on evidence.** If the
lucide pipeline is written and the shell one-liner is the thing that hurts, that
is the argument; today it is a prediction.

**Q2. Where does the hook stamp live — `dist/.build-hooks.json`, or under
`~/.vilan/`?** *Recommendation:* `dist/`. A machine-global cache keyed on a
project path is unreasonable from a fresh clone and unreachable to `rm -rf
dist`, which is the sentence users already believe means "rebuild everything".

**Q3. `emit_keyed`, or a manifest `order` key?** *Recommendation:*
`emit_keyed`. The sort key is a property of the contribution, and the
contributor is the only code that can compute it; a flush-side comparator would
have to re-derive it by parsing the line, which is the invented second source of
truth this tree refuses elsewhere.

**Q4. Does an un-opted-in dependency hook print a line, or stay silent?**
`build-trust.md` §3 calls the refusal "a normal outcome, not an error to be
dismissed", which argues for silence; §4.3 argues that silence is
indistinguishable from the toolchain not noticing. *Recommendation:* **one dim
line, once per build, naming the dependency** — a note, never a warning, never
an error. The precedent is E96's own fix for tier 1: the answer to an
undocumented consequence is a sentence.

**Q5. Do generated sources need a declared home?** P6 verified two things that
bear on this: a generated module must sit directly under `root` (module paths
are flat — `pkg::generated::icons` does not resolve), and once there it is
indistinguishable from a hand-written module. A thousand generated icon modules
in `src/` beside twelve hand-written ones is not a source tree anyone can read.
*Recommendation:* declare one, as a **second module root** (`[package]
generated = "generated"`) rather than a subdirectory of `root`, since a
subdirectory cannot be imported today; auto-`.gitignore` it in `vilan init`.
Flagged as the question with the most unknown implementation cost in the paper —
it touches module resolution, which nothing else here does.

**Q6. Is tier 2's threshold the registry, or the git dependency?**
`build-trust.md` §4 says the registry, and cites a tracker item that turns out
to be the traction plan (§4.2). Third-party code already reaches the machine on
a `vilan build`. *Recommendation:* **the git dependency, i.e. now** — specify
the opt-in in S2, ship it refusing everything, and let the registry inherit a
syntax that already exists rather than mint one under pressure. Whichever way
this goes, `build-trust.md` §4's citation should be corrected.

**Q7. Should the flush prune be a general `dist/` sweep or a per-kind one?**
S4 prunes a kind's file when the kind stops emitting. E92 is the same shape for
a renamed bundle, and a general "delete what this build did not write" sweep
would close both. *Recommendation:* **per-kind in S4**, and file the general
sweep against E92 — a sweep that deletes files in `dist/` needs its own careful
ruling about what it is allowed to touch, and it should not ride an accumulator
slice.

---

## 11. Alternatives rejected

- **A `vilan install` command with an install-only hook.** §2.2: neither
  argument for it survives. The network is already behind `vilan build`, and
  E96 §3 already ruled that consent is a manifest line rather than a prompt. It
  would also add a state — "installed" — that nothing else in the toolchain has,
  and a way for a build to be wrong because a command was not run.
- **A trigger enum (`on = "install" | "build"`).** Rejected in favor of the
  staleness predicate (§2.1): the enum makes the user classify their hook, and
  the classification is derivable from what the hook reads. Two names for one
  dial is how the dial gets set wrong.
- **mtime-based freshness.** Rejected on the watch loop's own recorded ground:
  reuse is decided by content, never by mtime, and a hook stamp that trusted
  mtime would reintroduce a bug the watcher already fixed.
- **Sandboxing a first-party `build.vl`.** Rejected twice over —
  `build-trust.md` §5 declined it as a ruling, and `manifest.rs` already
  records the argument that a containment property the trust model does not
  offer is worse than none, because it advertises. §4.4.
- **A mutable const-time global with a flush.** This is 028's literal wording
  and it is the one shape that cannot be made deterministic: a mutable global's
  contents are a function of write order, and write order is const-eval order,
  which changes when an import moves. P1b measures what the current design
  buys — byte-identical output across a permuted import order — and a mutable
  global forfeits exactly that.
- **A flush-side comparator (a user-supplied ordering function).** Rejected: the
  flush runs after evaluation, so a comparator would have to re-derive each
  line's sort key by parsing the line. `emit_keyed` carries the key from where
  it is known, at the cost of one parameter.
- **Letting the hook own aggregation.** §5.5, with the CSS pipeline as the
  existence proof: the contributors are inside the program, and a process that
  could see them would be the compiler.
- **Giving hooks a channel into `dist/`.** §6.1: 029 owns `dist/`, with
  reachability, a manifest entry and fingerprinting that a copy step cannot
  have. The order's principle is that `dist/` has one writer.
- **Building 028 on top of 027 and closing the item into it.** The item offers
  this and the tracker records it as possible. Rejected: they answer different
  questions with different mechanisms, and 028 is both smaller and better
  founded — it is a documented promise (`const-eval.md` §3's "kind-specific
  rule") being kept, on a channel with one existing consumer and a byte-level
  gate available.
- **Reserving `emit` for CSS and giving other kinds a new function.** Rejected:
  the channel is already kind-generic in code and documented as
  styling-agnostic; splitting it now would create two mechanisms where the tree
  has one, and would strand the license-manifest and precache-list riders
  `const-eval.md` §3 already names.

---

## 12. The generated root — Q5's home for products, and the formatter's exclusion

*(Added 2026-08-29, Order 20, lane `genroot`, on Q5's ruling. §10 ruled Q5 as
recommended — "a second module root (`[package] generated = "generated"`),
auto-gitignored by `vilan init`; still flagged as the highest-unknown-cost
piece (module resolution)" — and the Order 18 note recorded that it "is in no
slice of §8 … it needs a slice of its own before it needs a probe". This
section is that slice, and it arrives carrying a second problem the ruling
could not have seen: Order 19's lucide evidence run found the **formatter**
half.)*

### 12.1 The loop, stated

Q5 was argued from readability: a thousand generated icon modules in `src/`
beside twelve hand-written ones is not a source tree anyone can read. That is
true and it is not the load-bearing reason. The load-bearing reason is a
**live defect in the shipped tree**, and Order 19's lucide evidence run walked
into it:

> A `[[build.hook]]` that generates a `.vl` module declares that module in its
> `outputs`. `vilan fmt` reformats the generated file. §3.1 digests declared
> outputs by content, so the reformat re-stales the hook. The next build re-runs
> the generator, which writes the file **unformatted** again — a generator emits
> the bytes its templates produce, not the bytes `vilan fmt` would. The next
> `vilan fmt` reformats it again. **The two undo each other on every round,
> forever.**

Three properties make this worse than a nuisance and worth a section:

- **It is silent.** Neither tool is wrong. `fmt` formatted a `.vl` file, which
  is its whole job; the hook re-ran because its declared output moved, which is
  §3.1 working exactly as specified. Nothing reports a loop, because from
  either side there isn't one.
- **It defeats S1 precisely where S1 was aimed.** The freshness gate exists so
  an expensive generator is free on the common path. A developer who runs
  `vilan fmt` — or, worse, who has format-on-save enabled — pays the generator's
  full cost on the next build, every time, and the `Fresh <name>` line they were
  promised never appears.
- **The editor makes it involuntary.** Format-on-save fires on a file the
  developer merely opened to read. The loop then runs without anyone having
  typed a command, which is the version of this defect that never gets
  diagnosed.

Q5's ruling covers the **gitignore** half of "generated sources need a declared
home". This section covers the **formatter** half, and they are the same
declaration: once the build knows which directory holds products, both
consumers read one key.

### 12.2 The manifest spelling: `[package] generated`, beside `root`

The declaration is one key on the section that already declares the package's
source layout:

```toml
[package]
name      = "app"
root      = "src"
generated = "src/icons"
```

and the identical key on `[library]`, which declares a `root` for the same
reason. Not on `[project]`: a workspace declares *members*, not sources, and
each member's manifest carries its own layout — which is also what keeps a
workspace's answer per-member rather than global.

**The alternative considered, and why it loses.** The obvious rival is to hang
the fact on the hook that generates — `[[build.hook]] generated = true`, with
the root derived from `outputs`. It fails on four counts, and they compound:

- **`outputs` are files, not a root.** §2.3 and the Order 18 note fix `inputs`
  and `outputs` as literal paths with globs refused. A generator writing a
  thousand modules would have to declare a thousand outputs, or declare the
  directory — at which point the "root" is a coincidence of how the hook chose
  to spell its staleness, and changing that spelling silently changes what the
  formatter does.
- **`run = [...]` hooks have no `outputs` at all**, so the string-form hook —
  which §7 promises never moves — could never mark its products.
- **It makes the formatter read the build graph.** `vilan fmt` would have to
  parse `[build]`, walk every hook, and union their outputs, to answer a
  question about a *directory*. The coupling buys nothing: the answer is a
  property of the layout, not of which hooks happen to exist this week.
- **The formatter is not the only consumer.** Q5's ruled uses are a module root
  and a `vilan init` gitignore line. Both are layout facts, and a layout fact
  that lives in `[build]` is in the wrong file section for two of its three
  readers.

Against those, `[package] generated` is one key, declared once, read by whoever
needs it, in the table a reader already scans to learn where the code is.

**It is knowable without running hooks — and that is the requirement, not a
convenience.** `vilan fmt` runs in trees that have never been built, in CI
before any build step, and inside an editor that must not spawn a generator to
answer a formatting request. A rule that required running (or even *reading*)
hooks to know which files to leave alone would put arbitrary shell behind
format-on-save. A manifest string is a `toml::from_str` away and cannot execute
anything.

### 12.3 Validation — four refusals, each named

The value is a path relative to the manifest directory, and it is checked at
`Manifest::validate`, beside the other layout refusals:

1. **It must not escape the package.** `../shared/gen` is refused **lexically**,
   before any filesystem look — the rule `asset::read`'s `ProjectReader` already
   holds (P3), for the same reason: a path that leaves the package names files
   the manifest has no standing to speak for, and resolving it first would make
   the refusal depend on what happens to exist. A **relative** path is required;
   an absolute one is refused by the same rule (it is outside the package by
   construction, and it makes the manifest machine-specific).
2. **It must not be the package directory itself.** `generated = "."` would
   swallow the manifest, every source file and every hand-written module. The
   key names a *part* of the package.
3. **It must not be `root`.** Q5's ruling is a *second* root; a second root that
   is the first is not one. The practical damage is the same failure this whole
   design exists to avoid — `vilan fmt` would quietly stop formatting every
   hand-written module in the package — and the message names both keys, because
   the fix is to change one of them.
4. **It must be one path, not a list.** One package, one home for its products.
   A package with two generators points them at one root; they are all products,
   and a reader should have one directory to look in, one line in `.gitignore`,
   and one thing to delete.

Nothing checks that the directory *exists*. A generated root before its first
build is the normal case — that is the whole shape of "generated" — and a
manifest error on a clean checkout would be the S1 stamp's own lesson
(§3.1: a missing declared input is a recorded fact, never a failure) unlearned.

### 12.4 The exclusion: `vilan fmt` does not format a package's products

**The rule.** A `.vl` file under a declared generated root is left
**byte-identical** by `vilan fmt`, and by `vilan fmt --check`.

Four decisions inside that sentence:

- **It is applied at collection, not at the write.** `fmt` and `--check` then
  agree by construction. A `--check` that reported "would reformat" on a file
  `fmt` will never touch is a CI failure with no fix, and building the exclusion
  into the walk makes that state unreachable rather than merely untested.
- **It is unconditional — it holds however the file is reached.** Naming the
  file explicitly (`vilan fmt src/icons/lib.vl`) does not lift it. This is the
  decision most worth arguing, because "the user asked for that exact file" is a
  real principle. It loses to a stronger one: **an explicit-path exception puts
  the loop straight back through the editor.** Format-on-save reaches a file by
  its exact path and nothing else; an exclusion that only applied to directory
  walks would be an exclusion the LSP could never honor, and §12.1's worst case
  is precisely the involuntary one. One rule, no exceptions, checkable from the
  path alone.
- **The escape is the manifest, not a flag.** There is no `--format-generated`.
  §3.2 gave `--rerun-hooks` because staleness is a *guess* that can be wrong;
  this is not a guess. If a file should be formatted it is not a product: move
  it out of the root, or drop the key. Both are one-line diffs that land in
  review, which is the same instrument §2.2 chose over a prompt.
- **The editor honors it through the same code.** The LSP's formatting handler
  and the CLI reach one formatter entry, and the exclusion goes *in front of
  that entry*, once. Two implementations of one rule is how the LSP's answer
  drifts from the terminal's, and this rule in particular has to hold in the
  editor or it has not been built.

**The exclusion is announced, once per run.** One dim line per generated root
that actually skipped at least one file, naming the root and the count:

```
note: 1786 generated files not formatted (`src/icons`, `[package] generated`)
```

The reasoning is §3.1's and §4.3's, applied a third time: *a tool that quietly
stops doing what the user asked is the failure mode this design cannot afford*,
and the answer to an undocumented consequence is a sentence. Three constraints
on the line, each earned by a case above:

- **Once per run, not once per file.** A thousand generated icons is a thousand
  lines nobody reads, and §4.3's "once per build" is the same shape.
- **Only when it skipped something.** A declared root with no `.vl` files under
  it — the clean checkout — says nothing. A note about an exclusion that
  excluded nothing is noise, and noise is how the honest lines get ignored.
- **A note, never a warning, and the exit code is unchanged.** Skipping a
  product is the correct outcome, not a degraded one. `vilan fmt --check` in CI
  passes with the note, which is the behavior a generated tree needs.

### 12.5 The relationship to the ruled gitignore posture

Q5 ruled the root "auto-`.gitignore`'d by `vilan init`". The two consumers are
the same key read by different tools, and stating how they relate keeps a later
reader from inventing a coupling that isn't there:

- **`vilan init` writes the line; nothing enforces it.** A generated root that
  is committed is legal. It is a choice some projects make deliberately (a
  generated module a consumer must be able to read without the generator's
  toolchain), and a build that refused it would be legislating a workflow the
  manifest has no business in. `init` is a convenience at creation time, and the
  formatter's rule holds regardless.
- **The fmt exclusion does not read `.gitignore`, and must not.** It reads the
  manifest. Deriving the exclusion from ignore rules would make the formatter's
  behavior depend on a file with its own precedence semantics, its own global
  and per-user layers, and no relationship to what the build considers a
  product — and it would silently stop formatting `dist/`-adjacent scratch
  directories nobody declared. One key, one meaning.
- **They point at the same directory for the same reason, and that is the
  point.** Products are not authored: not reviewed as diffs, not formatted as
  source, not edited in place. The generated root is the single place a package
  says which files those are, and every tool that cares reads it.

### 12.6 What this slice does not build: the module root

Q5's ruling has two halves and this slice ships one. **The generated root is
not yet a module search root**, and a package must still put an importable
generated module where the resolver already looks.

The measurement, since Q5 called this "the question with the most unknown
implementation cost":

- **The resolution change itself is one line.** `resolve_module_in_roots`
  already takes `&[&Path]` — a dependency library is multi-rooted, because
  `[library.layer.<name>]` overlays are. The entry package is the one origin
  that is single-rooted: `Origin::Pkg => vec![pkg_root]`.
- **The cost is the thread, not the lookup.** `pkg_root: &Path` is a scalar
  through `vilan-core`'s public analysis surface and out into the CLI, the
  language server, the IDE crate and the wasm binding — ~65 references across
  five production files, several of them public signatures with callers outside
  the compiler.
- **And the semantics are a slice's worth on their own**, not a refactor's:
  which root wins when a module resolves in both (and whether that is an error
  the way `foo.vl`-plus-`foo/lib.vl` already is), what the watcher tracks, what
  go-to-definition answers, what `case_exact_mismatch` checks against.

None of that blocks the formatter half, and the formatter half should not wait
for it, because **the loop is a property of the hook, not of the import**. A
`[[build.hook]]` whose declared output is a `.vl` file re-stales on every
`vilan fmt` whether or not a single `import` names it. The exclusion pays off
the day it lands.

It also lands with a configuration that works **today**, which is what keeps
this from being a declaration with no consumer: modules are flat (P6), but a
module's *file* may be `<root>/<name>/lib.vl` as well as `<root>/<name>.vl`. So
`root = "src"` with `generated = "src/icons"` excludes the whole generated
subtree from the formatter while `src/icons/lib.vl` still imports as
`pkg::icons`, on the shipped resolver, with no compiler change. The sibling
form Q5 recommended (`generated = "gen"`, beside `src/`) parses, validates and
excludes today, and becomes importable when the second half lands — which is
the right order: the declaration is fixed and reviewable before anything
resolves through it, exactly as S2 fixed the tier-2 opt-in before anything
could cross it.
