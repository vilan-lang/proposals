#!/usr/bin/env python3
"""Patch a RELOCATED copy of std with A110 door 2 — the two-phase settle.

papers-38's own door-2 instrument, so the section has a measurement even if
lane reactive-38's does not arrive. It is a SCRATCH build (a std copy reached
through `$VILAN_STD`, with its `macro_std` sibling beside it); nothing here is
proposed as the implementation.

Four changes to `std/src/reactive.vl`:

  1. `Subscriber` carries `derived: bool`; `observe` tags it from a module-level
     flag that the derivation combinators raise while they attach (`map`,
     `combine`, `selector`, both `flatten`s). A `Subscriber.kind` set at
     `on_change` time is what a real build would use — A110 door 2 says so —
     and the flag is the cheap scratch equivalent.
  2. `Turn` gains a `deferred` queue, held in ASCENDING id order.
  3. `drain` runs two phases per settle: derivations to a fixpoint (parking
     every effect it meets), then the parked effects in ascending id.
  4. `Subscription::dispose` scrubs `deferred` as well as `pending`, so a
     disposed observer parked in phase 1 does not fire in phase 2. (Door 1's
     liveness bit is lane reactive-38's and is NOT reproduced here; this scrub
     is what keeps the instrument faithful for the ordering question.)

Line-based, and every anchor is a whole stripped line, so the file's own
indentation is reused rather than transcribed.

    python3 patch_door2.py <std>/src/reactive.vl
"""

import sys

path = sys.argv[1]
lines = open(path).read().split("\n")
edits = 0


def find(needle, start=0):
    """The index of the one line whose stripped form is `needle`."""
    hits = [i for i, line in enumerate(lines) if i >= start and line.strip() == needle]
    assert len(hits) == 1, f"{len(hits)} hits for {needle!r}"
    return hits[0]


def find_first(needle, start=0):
    for i, line in enumerate(lines):
        if i >= start and line.strip() == needle:
            return i
    raise AssertionError(f"no hit for {needle!r}")


def indent_of(index):
    line = lines[index]
    return line[: len(line) - len(line.lstrip("\t"))]


def insert_after(index, block, extra=""):
    """Insert `block` (a list of unindented lines) after `index`."""
    global lines, edits
    pad = indent_of(index) + extra
    lines = lines[: index + 1] + [pad + line if line else "" for line in block] + lines[index + 1 :]
    edits += 1


def insert_before(index, block, extra=""):
    global lines, edits
    pad = indent_of(index) + extra
    lines = lines[:index] + [pad + line if line else "" for line in block] + lines[index:]
    edits += 1


def swap(index, text):
    global lines, edits
    lines[index] = indent_of(index) + text
    edits += 1


# --- 1. the subscriber record ------------------------------------------------
insert_after(
    find("notify: || void,"),
    [
        "// door-2 INSTRUMENT: true for a DERIVATION's subscriber (`map`,",
        "// `combine`, `selector`, `flatten`), false for an effect and for an",
        "// `at_settle` action.",
        "derived: bool,",
    ],
)

insert_before(
    find("export fun fresh_id(): i32 {"),
    [
        "/// door-2 INSTRUMENT: raised while a derivation combinator is attaching,",
        "/// so `observe` can tag the subscriber it mints.",
        "let minting_derivation: Shared<bool> = Shared::new(false);",
        "",
        "fun as_derivation<T>(attach: sync || T): T {",
        "\tminting_derivation.write() = true;",
        "\tlet result = attach();",
        "\tminting_derivation.write() = false;",
        "\tresult",
        "}",
        "",
    ],
)

# `observe`'s literal: the `id,` line immediately after the push.
push = find("signal.subscribers.write().push(Subscriber {")
assert lines[push + 1].strip() == "id,"
insert_after(push + 1, ["derived = minting_derivation.read(),"])

swap(
    find("let deferred = [Subscriber { id, notify = action }];"),
    "let deferred = [Subscriber { id, notify = action, derived = false }];",
)

# --- 2. the turn's effect queue ---------------------------------------------
insert_after(
    find("draining: Shared<bool>,"),
    [
        "// door-2 INSTRUMENT: the effects phase 1 met, in ASCENDING id order.",
        "deferred: Shared<List<Subscriber>>,",
    ],
)

insert_after(
    find("draining = Shared::new(false),"),
    ["deferred = Shared::new([]),"],
)

# --- 3. the two-phase drain -------------------------------------------------
# Replace the whole `for !turn.pending…` loop inside `with_finally`.
loop_start = find("for !turn.pending.read().is_empty() && budget > 0 {")
# The loop's closing brace is the line at the loop's own indentation.
pad = indent_of(loop_start)
loop_end = next(
    i for i in range(loop_start + 1, len(lines)) if lines[i] == pad + "}"
)
body = [
    "for (!turn.pending.read().is_empty() || !turn.deferred.read().is_empty()) && budget > 0 {",
    "\t// PHASE 1 — derivations to a FIXPOINT. Every effect met on the way",
    "\t// is parked on the TURN (not in a local, so `dispose`'s scrub can",
    "\t// still reach it).",
    "\tfor !turn.pending.read().is_empty() && budget > 0 {",
    "\t\tlet wave = turn.pending.read();",
    "\t\tturn.pending.write() = [];",
    "\t\t// The wave is out of the queue, so its ids are free to re-enter",
    "\t\t// it — a cascade re-enqueuing an observer this wave already ran",
    "\t\t// is the propagation `drain`'s loop exists for.",
    "\t\tturn.queued.write() = NativeMap::new();",
    "\t\tmut ran_derivation = false;",
    "\t\tfor subscriber in wave {",
    "\t\t\tif subscriber.derived {",
    "\t\t\t\t(subscriber.notify)();",
    "\t\t\t\tbudget -= 1;",
    "\t\t\t\tran_derivation = true;",
    "\t\t\t} else {",
    "\t\t\t\tpark_effect(turn, subscriber);",
    "\t\t\t}",
    "\t\t}",
    "\t\tif !ran_derivation {",
    "\t\t\tjump break;",
    "\t\t}",
    "\t}",
    "\t// PHASE 2 — the parked effects, ASCENDING by subscriber id, which is",
    "\t// parent-before-child because `fresh_id` is monotonic and a parent's",
    "\t// effect is created before anything its render creates.",
    "\tlet ordered = turn.deferred.read();",
    "\tturn.deferred.write() = [];",
    "\tfor subscriber in ordered {",
    "\t\t(subscriber.notify)();",
    "\t\tbudget -= 1;",
    "\t}",
    "}",
]
lines = lines[:loop_start] + [pad + line for line in body] + lines[loop_end + 1 :]
edits += 1

insert_before(
    find("/// Settle the AMBIENT turn's pending notifies now. With no ambient turn there"),
    [
        "/// door-2 INSTRUMENT: park one effect on the turn, deduped by id and held",
        '/// in ascending id order — the "bucketed insert" A110 door 2 names as the',
        "/// alternative to a per-wave sort.",
        "fun park_effect(turn: Turn, subscriber: Subscriber) {",
        "\tmut held = turn.deferred.read();",
        "\tmut index = 0;",
        "\tmut found = false;",
        "\tfor index < held.len() {",
        "\t\tif held[index].id == subscriber.id {",
        "\t\t\tfound = true;",
        "\t\t}",
        "\t\tindex += 1;",
        "\t}",
        "\tif !found {",
        "\t\tmut at = 0;",
        "\t\tfor at < held.len() && held[at].id < subscriber.id {",
        "\t\t\tat += 1;",
        "\t\t}",
        "\t\theld.insert(at, subscriber);",
        "\t\tturn.deferred.write() = held;",
        "\t}",
        "}",
        "",
    ],
)

# --- 4. the dispose scrub reaches the parked effects too --------------------
insert_after(
    find("turn.queued.write().remove(self.id.hash());"),
    [
        "// door-2 INSTRUMENT: and the effects phase 1 parked.",
        "mut kept_deferred: List<Subscriber> = [];",
        "for subscriber in turn.deferred.read() {",
        "\tif subscriber.id != self.id {",
        "\t\tkept_deferred.push(subscriber);",
        "\t}",
        "}",
        "turn.deferred.write() = kept_deferred;",
    ],
)

# --- the derivation combinators raise the flag while they attach ------------
# Each is a `register_with_owner(<attach>)` whose closing line gains one `)`.
for opener, closer in (
    ("let _owned = register_with_owner(self.on_change(|value| {", "}));"),
    ("let _owned = (source in sources => register_with_owner(source.on_change(|_| {", "})));"),
    ("let _owned = register_with_owner(source.on_change(|value| {", "}));"),
    ("let _outer = register_with_owner(self.sub(|inner| {", "}));"),
    ("let _outer = register_with_owner(self.sub(|held| {", "}));"),
):
    index = find_first(opener)
    pad = indent_of(index)
    lines[index] = pad + opener.replace("register_with_owner(", "register_with_owner(as_derivation(|| ", 1)
    end = next(i for i in range(index + 1, len(lines)) if lines[i] == pad + closer)
    lines[end] = pad + closer.replace("}", "}", 1).replace(";", ";", 1)[:-1] + ");"
    edits += 1

open(path, "w").write("\n".join(lines))
print(f"patched {path}: {edits} edits")
