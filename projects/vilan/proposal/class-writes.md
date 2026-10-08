# Class writes — an element that writes its class more than once (A155)

> Status: **DRAFT 2026-10-05 — for the owner's ruling** (R-k: "census in papers-47, no build").
> Written by lane papers-47 of Order 47 against vilan `next` @b94cb47f
> (`vilan 0.44.0 (b94cb47fc)`, built in the lane's worktree). Nothing in the compiler tree
> changed. kolt and the website were read in place and built only as copies in the lane's
> scratch directory.
>
> Probes and censuses: `scripts/integration/sweeps/order47/papers-47/a155/`.
> - `probes/run.sh <vilan> <scratch>` runs thirteen probe programs (`aN`), each on the SSR leg
>   (`vilan run`, node) and on the client leg (`--platform browser`, run under `probes/stub.mjs`,
>   a DOM stub that records every class write per element). The output is in `probes_out.txt`.
> - `census_class_writers.py` finds every class writer and the element it writes (`kolt.tsv`,
>   `site.tsv`, `examples.tsv`). `args_census.py` classifies each writer's argument (`*_args.tsv`).
> - `instrument_std.sh` makes a copy of std whose class writers report a second class write on
>   one element at run time. `RUNS.txt` records what ran against it.
>
> Related: A155 (the warning, shipped in Order 46 and RULED as a warning); K26 (element syntax
> makes `class("x")` the obvious spelling); `ui-styling.md` §4 (`Style` is atomic);
> `element-syntax.md` §7 (which declined a clobber lint in 2026-08).

## 0. The ask, and the answer up front

Every one of std's class writers SETS the `class` attribute, on both ui twins. When one element
has two writers, the last one wins and the first one's classes are gone. Order 46 shipped a
warning for the case it can see. The open half of A155 is whether the writers should **append**
instead. The owner asked for a census of real double writes first.

**The answer.**

1. **Nobody writes an element's class twice.** The census covers kolt, the website and
   `vilan/examples/`: 405 class writers. The results:
   - The static census finds no element with two writers.
   - The compiler's own A155 check is silent on all three.
   - An instrumented std saw no double write on any page the website serves, nor when the
     website's client booted. That is 482 classed elements on the server and 443 in the client.
2. **What authors mean is one writer, composed with `+`.** 27 sites compose two styles into one
   writer, and three reactive sites compute the whole class list in one writer because a second
   writer would clobber the first. One example's comment says so. The website's README makes it
   a rule: "Class names come from `.styled(..)` only, once per element (compose styles with `+`)".
3. **Appending breaks `Style`.** A `Style` is atomic CSS, one class per property slot, and `+`
   resolves a conflict per property with the right side winning. If two `.styled(..)` writers
   appended their tokens, an element would carry a class for `color: red` and a class for
   `color: blue`. The sheet orders its rules by class name, which is a hash. So the colour would
   come from the hash order, not from the order the writers were written (probe a3, §3.1).
   - An append that composed with `+` (§4, door A2) would avoid this. It needs per-element state
     on both twins and a recompose on every reactive change, for zero sites.
4. **Today's warning has three gaps** (§2.3):
   - `.bind_attr("class", ..)` and `.toggle_attr("class", ..)` are writers it does not count.
   - Its sentence is wrong when the EARLIER writer is reactive: the browser re-applies the
     earlier writer on every change.
   - It cannot see across a function, which is by design.

**Rec: keep last-wins. Do not make the writers append.** Close the warning's two fixable gaps
now (filed, S each). Make the statically visible double write a refusal at the next breaking
cut after that. The migration cost is **0 sites** in kolt, the website and the examples. The
cross-function remainder stays last-wins and silent, with a trigger stated (§5).

## 1. The writers

| writer | browser twin (`std/src/browser/web/ui.vl`) | process twin (`std/src/process/web/ui.vl`) |
|---|---|---|
| `.class(name)` | `:166-169` `set_attribute("class", name)` | `:142-144` `set_attribute(self.attributes, "class", name)` |
| `.styled(style)` | `:174-177` `set_attribute("class", style.class_list())` | `:149-151` |
| `.bind_class(source)` | `:264-270`, re-set on every change | `:220-222`, read once |
| `.bind_styled(source)` | `:277-283`, re-set on every change | `:227-229`, read once |
| `attr("class", v)` (and an element head's undotted `class(..)`, which lowers to it) | `AttrValue::apply` `:2135-2192`: a `str` sets, a `Source` follows | `:695-737` |
| `bind_attr("class", s)` | `AttrBinding` (`:2209-2230`) | the twin |
| `toggle_attr("class", flag)` | `:317-327`: present as `""`, absent REMOVED | the twin |

The process twin's `set_attribute` (`:101-116`) replaces an attribute of the same name in place.
The browser twin is `Element.setAttribute`. Both are last-write-wins. Neither twin keeps any
record of who wrote the class.

A `Style` is `rules: HashMap<slot key, (class, declaration)>` (`std/src/web/style.vl:878-883`).
`class_list` space-joins every slot's class (`:2411-2422`). `Style + Style` replays the right
side's slots over the left's, so per property the right side wins, and per property family as
well (`:2424-2448`). That is how two styles compose today, and the guide teaches it
(`docs/guide/styling.md:493-502`).

## 2. What the compiler does today

### 2.1 Probes, both legs

`probes/run.sh` against b94cb47f. `card` = `padding: 4px; color: red`, `wide` =
`width: 100%; color: blue`. "client" lists the class writes the DOM stub saw, then the final
value. Reactive probes flip their signal once after mounting.

| probe | source | warns | SSR | client writes → final |
|---|---|---|---|---|
| a1 | `<div class("x") .styled(card) />` | yes | card | `x`, card → card |
| a2 | `<div .styled(card) class("x") />` | yes | `x` | card, `x` → `x` |
| a3 | `<div .styled(card) .styled(wide) />` | yes | wide | card, wide → wide |
| a4 | `<div .styled(card + wide) />` | — | `s3sbz2x s5qpnud s178flj9` | one write |
| a5 | `.styled(card) .bind_class(flag → "on"/"")` | yes | `on` | card, `on`, `""` → `""` |
| a6 | `.styled(card) .bind_attr("class", flag → "on"/"off")` | **no** | `on` | card, `on`, `off` → `off` |
| a7 | `boxed().class("x")`, where `boxed()` returns `<div .styled(card) />` | **no** | `x` | card, `x` → `x` |
| a8 | `decorate(<div class("x") />)`, where `decorate(v) = v.styled(wide)` | **no** | wide | `x`, wide → wide |
| a9 | `<div .styled(card) />.class("x")` | yes | `x` | card, `x` → `x` |
| a10 | `view("div").class("a").class("b")` | yes | `b` | `a`, `b` → `b` |
| a11 | `<div class(label) .styled(card) />`, where `label` is a `Signal<str>` | yes | card | `lbl`, card, **`lbl2`** → `lbl2` |
| a12 | `.styled(card) .toggle_attr("class", flag)` | **no** | `""` | card, `""`, removed → none |
| a13 | `<div .bind_styled(flag → card/wide) class("x") />` | yes | `x` | card, `x`, **wide** → wide |

The SSR leg and the client's first paint agree in every probe. The behaviour is last-write-wins,
as A155 says.

### 2.2 The warning

`check_class_written_twice` (`crates/vilan-core/src/analyzer.rs:53737`) runs after analysis. Its
writers are the calls named `class`, `styled`, `bind_class` or `bind_styled`, plus
`attr("class", ..)` (`:53770`). From each writer it follows the receiver while the receiver is a
dotted call of a std `View` method. That covers an element head (which lowers to such a chain),
a `view("..")` chain, and a postfix link on a closed element (a9). It does not continue through a
function of the program's own (a7, a8). It reports once per pair, at the later writer, naming
both writers. std, dependencies and generated code are skipped.

### 2.3 Three gaps

- **G1. Two writers it does not count.** `bind_attr("class", ..)` (a6) and
  `toggle_attr("class", ..)` (a12) both write the attribute. The second one REMOVES it whenever
  its flag is false. Neither warns. Filed as A?1 (S): add both names to the writer set at `:53770`, under
  the same `"class"` literal test `attr` gets.
- **G2. The sentence is wrong for a reactive earlier writer.** It tells the author "only the last
  write stays: `.styled(card)` replaces what `class(label)` wrote." That holds on the server and
  at first paint. In the browser, `class(label)`'s binding re-sets the attribute every time
  `label` changes, and from then on the element shows `label` (a11; a13 is the mirror case with
  `.bind_styled` first). The winner is whichever writer fired last. Filed as A?2 (S): when the earlier
  writer is a binding (a `Source` argument to `attr`/`class(..)`, or `bind_*`), the message says
  that the two writers take turns, rather than that the later one stays.
- **G3. It does not cross a function** (a7, a8). This is by design, and §5 measures it.

## 3. The census

### 3.1 Static

`census_class_writers.py` finds every writer and walks back from it to the element it writes:
an element head, a `view(..)` chain, or a closed element. Where the walk ends at a call of a
program function or at a variable, the site is listed for review by hand (`call:` / `var:` in
the TSVs). kolt's generated `src/lucide/` is excluded, and the one helper that styles a lucide
icon is reviewed instead.

| body | writers | elements with 2+ writers | cross-function writers | kinds |
|---|---|---|---|---|
| kolt `src/` | 122 | **0** | 1 (`styles.vl:126` `icon(v) = v.styled(icon_style)`) | `.styled` 121, `.bind_styled` 1 |
| website `src/` | 239 | **0** | 0 | `.styled` 239, all in element heads |
| `vilan/examples/` | 44 | **0** | 1 (`todo/src/todos.vl:160`, `label.styled(done_label)`) | `.styled` 33, `.class` 9, `.bind_class` 2 |
| **total** | **405** | **0** | 2 | |

Both cross-function writers were reviewed, and both write an element that has no class of its
own:

- kolt's `icon(..)` is called at 17 sites, each time on a lucide icon. `lucide_frame()`
  (`src/lucide/lib.vl:18-28`) writes presentation attributes and no class. Upstream lucide icons
  do ship `class="lucide lucide-<name>"`, and kolt's generator drops it.
- The todo example's `label` is `view("span").text(..)`, with no class.

`vilan check` with the stock std reports **0** "written twice" warnings over kolt, the website
and every example.

### 3.2 Run time

The instrumented std (`instrument_std.sh`) traces a second class write on one element. On the
process twin the trace is at `set_attribute`. On the browser twin it is at each writer's entry,
via `has_attribute("class")`. It catches a7 and a8, which the static check cannot see. Against
the website (`RUNS.txt`):

- **SSR.** `/` and `/playground` render 443 + 39 classed elements. The chrome leg exports the
  masthead. There are **0** double writes.
- **Client.** The landing page booted under the site's own DOM stub (`tests/support/home.mjs`)
  builds 443 classed elements with **0** double writes. The playground's console, runner and
  format test flows also produce **0**.

kolt's runtime half did not run: its client harness (`e2e/client-harness.js`) predates the
current std's DOM surface (`replaceState`, `removeAttribute`, `parentNode`, ranges, fragments).
kolt's static census and `vilan check` stand alone for it.

### 3.3 What each author meant

There are no double writes, so the question becomes what authors write INSTEAD of a second
writer (`args_census.py`):

| shape | sites | meaning |
|---|---|---|
| one writer, one style or one class | 373 | unambiguous |
| `.styled(a + b)` composition | 27 (kolt 13, site 14; kolt's overlay site is also in the next row) | **both, the right side winning per property**. The `+` is written exactly where a second `.styled` would have been, as the site's README tells the author to |
| a reactive writer that computes the WHOLE list | 3 (kolt `lib/overlay.vl:431`, examples `todo/src/todos.vl:144` and `reactive-ui/todos.vl:126`) | **replace my own previous value**. The todo example says why (`todos.vl:133-135`): "`bind_class` over their class lists is the recorded composition for signal-driven style switching". The overlay writes `container_style + container_scrim_style` against `container_style` rather than `.styled(container_style).bind_styled(..)` |
| a static conditional (`.class(if done { "done" } else { "" })`, a `Style::when`/`.on(..)` set) | 3 | one writer choosing its value |

The append intent appears in one place only: kolt's `icon(v)` decorator, which means "add sizing
to whatever icon I am handed". It is safe today only because lucide's class was dropped.

## 4. The doors

**A1. Append tokens** (`classList.add`, and a join on the server). The append happens at the
token level, so the writers no longer compose like styles:

- **It breaks `Style`'s per-property resolution.** In a3 the element would carry `s3sbz2x
  ss5mdns s178flj9 s5qpnud`. The sheet the build emits orders its rules by class name
  (`a3_two_styled.css`: `.s5qpnud{color:blue}` before `.ss5mdns{color:red}`). At equal
  specificity the later rule wins, so the element is **red** although `wide` (blue) was written
  last. Two different styles would hash in the other order and give the other answer. `+` exists
  precisely so that this never depends on the sheet.
- **It breaks the three whole-list reactive writers** unless every writer tracks and removes its
  own previous tokens. Naive accumulation would never remove the scrim class or the `active`
  class.
- **Two writers can share an atomic class.** Both may set `display: flex`. Removing one writer's
  tokens would then remove the other's, so per-token reference counts are needed.

Migration: 0 sites change meaning statically, but 3 sites break unless writers own their tokens.
**Not recommended.**

**A2. Append by composition.** Each element keeps its writers in order: styles fold with `+`, raw
class strings join, and a reactive writer replaces only its own slot and recomposes on every
change. `.styled(a).styled(b)` then means `.styled(a + b)`, and a7/a8 compose.

- It is sound against `Style`.
- It costs a per-element side table on the browser twin (a `WeakMap` from element to writer
  slots), a field on the process twin's `View`, and a `+` and `class_list` on every reactive
  class change. Today a reactive class change is one `setAttribute`.
- It also changes the meaning of every chain that leans on replace. The census finds none.

Migration: **0 sites**. Benefit: **0 sites**, plus the cross-function decorator pattern, which
has one safe instance. **Not recommended now.** It is the door to reopen if a component library
needs `component(..).styled(extra)` to compose (§5's trigger).

**B. Last wins, with the warning.** This is shipped. Migration 0. It leaves G1 and G2, which are
fixable, and G3, which is not.

**C. Refuse the statically visible double write.** The warning becomes an error, with the same
sentence and the same two steers ("compose them into one writer (`.styled(a + b)`)", "or drop
one").

- Migration: **0 sites** in kolt, the website and the examples, by both the census and
  `vilan check`.
- Reasons to refuse rather than warn:
  - No legitimate program needs two writers on one statically visible element. Every intent in
    §3.3 is spelled with one writer.
  - With a reactive writer involved, the result isn't even one answer: it alternates (G2).
  - The cases a person writes first by habit (`class("x")` from HTML, `.styled(base)` plus
    `.bind_class(active)` from JSX) are exactly the ones that silently lose classes.
- The cross-function remainder (a7, a8) cannot be refused at compile time, so its semantics stay
  last-wins either way.

**Rec: C, after G1 and G2 are fixed, at the next breaking cut.** That is not this order's v0.45.0:
R-k said no build, and R-c already carries two flips. Last-wins stays the meaning, and A1/A2 are
declined.

## 5. The cross-function remainder

a7 (`boxed().class("x")`) and a8 (`decorate(<div class("x") />)`) are silent on both legs and
lose a class. The census has two such writers, and both are safe (§3.1). What to do:

- **Nothing now.** The static check would need to follow a callee's returned or parameter `View`
  through program functions, which is the escape-analysis family's cost for one warning. A
  runtime check would cost one `hasAttribute` per class write in every build.
- **Trigger:** a cross-function double write found in a census. The instrumented std in this
  paper's directory is that census. It runs a package's own tests or pages under
  `VILAN_STD=<copy>`. If one appears, the choice is A2, or an explicit additive writer:
  `.also_styled(s)`, which composes with the element's existing style by `+`, leaves `.styled`
  meaning "set", and needs the per-element style only where it is called.

## 6. Sizing

| piece | size | lane |
|---|---|---|
| G1: `bind_attr("class")`, `toggle_attr("class")` counted; pins a6/a12 | S | any analyzer lane |
| G2: the alternating sentence for a reactive earlier writer; pins a11/a13 | S | same |
| C: warning → error (ledger row, steer unchanged, the A155 pins flip to refusals) | S | at a breaking cut |
| A2 / `.also_styled` | M | parked (§5 trigger) |

## 7. For the owner

- **Q1. Do the class writers stay last-wins (no append)?** Rec: **yes.** The census finds no
  element with two writers in 405 writers. The 27 `+` compositions and the 3 whole-list reactive
  writers show authors composing into one writer on purpose. Token append (A1) makes a
  property's winner depend on hash order. Composing append (A2) costs per-element state on both
  twins for zero sites.
- **Q2. Does the statically visible double write become a refusal (door C)?** Rec: **yes, at the
  next breaking cut after G1 and G2 land, with 0 sites to migrate.** Keep the warning until then.
- **Q3. Should G1 and G2 be filed and fixed now?** Rec: **yes, S each** (A?1 and A?2 in
  `newitems47-papers.json`). G2's sentence is the one place today's diagnostic tells the author
  something false.
- **Q4. The cross-function remainder: leave it silent, with the census trigger, and park A2 and
  `.also_styled` behind it?** Rec: **yes.**
- **Q5. A155: close it on this paper** once Q1–Q4 are ruled, with G1 and G2 carried as their own
  items? Rec: **yes.**
