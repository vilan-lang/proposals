# M79 — resolving an entry-shaped world BEFORE the store: the eleven queues and the deferral rule

> Handed back by lane perf-38 of Order 38 as a section for
> `projects/vilan/proposal/analysis-reuse.md` (it belongs after §6.7, the
> two-phase `resolve_world` shape, and before §6.13's expansion hoist).
> Nothing in it is built: M79's build is Order 39's at the earliest, and the
> ruling questions in §M79.6 are asked, not answered. The marks are CPU as
> well as wall since M78, so the figures below are absolutes, not shares.

## M79.1 Where this stands after Orders 37 and 38

**M70 (Order 36).** A module a front end opened AS the entry — whose own
package imports it back, so `pkg::<entry>` aliases the open file's scope —
gets its world STORED. It is stored *unresolved*: `analyze_inner` skips the
pre-entry `resolve_world` for this shape, because `seed_preludes` drains the
prelude queue and in the open-file order the modules have not resolved their
imports yet, so a prelude module's re-exports would bind to nothing (B239).

**M73 (Order 37).** `resolve_world` was split into reported stages and
measured. The constraint FIXPOINT is 79-96 % of the pass on all nine measured
kolt files; `preludes` and `use-drain` read 0.0 ms; `imports` 0.1-1.2 ms. And
the structural half: a file whose world is stored RESOLVED runs `resolve_world`
TWICE - once before the store and once inside the post-entry `build()` - with
the second run at 1.2-8.9 % of the first. So the pass is already proven
re-runnable over a world it has settled, by every ordinary analysis in the
tree. The whole of what an open module pays per keystroke is that its FIRST
run happens after the store instead of before it.

**M76 (Order 38, lane perf-38).** The *checks* half of that cost is now
recovered without moving the resolve at all: an entry-shaped world files its
M19 T1 checks record, and the reading side is narrowed by two guards - T0's
type-slot dirty bit and a new alias-reach closure over resolved import edges.
Measured paired on the six kolt files (release, thread CPU medians, seven
keystrokes per leg, loadavg 30-42): `theme.vl` 1,118.9 -> 914.1 ms (-18.3 %),
`styles.vl` -20.0 %, `app_overlay.vl` -19.0 %, `app_context.vl` -15.4 %,
`prefs.vl` -13.1 %, `sidebar.vl` -2.8 %. `reused` went from 0/69 to 59/69.

M76 therefore CHANGES M79's prize. The `build` stage it does not touch:
`theme.vl` reads `build 156.0ms/156.0cpu` of a ~685 ms analysis on a quiet box
(`vilan check src/theme.vl`, release, three reps, medians, loadavg 11.3-13.0),
beside `load+walk 128.0/127.9`, `checks 264.5/264.5` and `post-passes
136.1/136.1`. The `resolve_world` line inside that build reads
`fixpoint 137.9ms/137.9cpu` of a `151.3/151.3` pass - 91 % of it, on both
clocks. So M79's remaining prize is ~150 ms of ~685, about 22 %, and the
recoverable part of it is whatever fraction of the fixpoint can settle before
the store. It is no longer "the largest remaining cost": M76 took that title
off the checks phase, and there is no single dominant stage left.

## M79.2 The eleven queues

`resolve_world` is a drain of eleven queues, each `std::mem::take`n so a second
run over a reused base never sees an item twice (S2, section 6.3). The design
requires every one of them to be able to HOLD AN ITEM BACK - drain the
non-deferred part and re-park the rest for the post-entry run. Their order in
the function is their dependency order; the reported stage each falls in is
named beside it.

| # | queue | reported stage | carries a `SourceId`? |
|---|---|---|---|
| 1 | `prepped_imports` | `imports` | yes, per item |
| 2 | `prepped_uses` | `use-drain` | yes, per item |
| 3 | `prepped_binder_inheritance` | `binder-bounds` | no - `(TypeId, name, position, scope_id)` |
| 4 | `prepped_std_items` | `locals` | no - `(Id, module, item)` |
| 5 | `prepped_locals` | `locals` | no - `(Id, name)` |
| 6 | `prepped_assignments` | `locals` | no - `(Id, Id)` |
| 7 | `prepped_type_locals` | `locals` | yes, per item |
| 8 | `prepped_type_static_accessors` | `types` | via `PreppedTypePath` |
| 9 | `prepped_static_accessors` | `types` | no - `(Id, TypeId, name)` |
| 10 | `prepped_trait_impls` | `conformance` | via `TraitImplCheck` |
| 11 | `guard_continuations` | `divergence+guards` | no - a guard record |

`seed_preludes` (stage `preludes`) is not a queue of this kind: it is a pass
over the packages' declared prelude modules, and it is the one item M70's own
comment names as order-sensitive. The `contexts` and `fixpoint` stages drain
the CONSTRAINT queue, a different structure (`drain_once`, priority-ordered)
that is re-entrant by construction - it is the one part of this that already
holds items back, and it does so for a different reason (a deferred
constraint).

Seven of the eleven carry no source. That is the whole of M79's cost, and
section M79.4 is about it.

## M79.3 The deferral rule

**The rule.** A file is DEFERRED - its queue items held back for the
post-entry run - when its own resolution can be answered by the open file's
declarations. Seed the set with the files whose imports resolve into the entry
(`SourceId(0)`, which is what the `pkg::<entry>` alias binds), then close it
transitively under "imports from a deferred file": a file whose import
resolves into a deferred file inherits the dependency, because the name it
binds is only as settled as the file it comes from.

**The rule is already implemented, for M76's question.**
`Analyzer::alias_reaching_sources` computes exactly this closure, over
`import_targets` - one `(importing SourceId, resolved target Id)` pair per
import leaf and per `use` binding, recorded where the path resolves. M79 reads
the same set; it does not need a second one.

**A correction to M79 as filed.** The item estimated the set by SOURCE PATHS -
"files carrying `import pkg::<entry-alias>`, closed transitively, kolt: 9 of 26
package files for every one of the six, leaving ~60 of ~69 sources resolvable
before the store". Measured over resolved edges it is 4 sources, not 9, for
each of the five 69-source files, and 0 for `sidebar.vl`, whose 55-source world
holds no alias-reaching module at all. (Phase line: `reused 59/69 entry-dirty 6
alias-reaching 4`; the dirty and alias-reaching sets overlap in one file, which
is why 68 - 6 - 4 leaves 59 and not 58.) The path estimate over-counted because
a written `pkg::<name>` is not the same thing as a name that resolves into the
entry: several of kolt's `pkg::` imports name a module whose own resolution
never reaches the open file. So MORE is resolvable pre-store than the item
assumed, and the rule's fallback is further away than it feared.

**The fallback.** M79's own condition stands: if the package PRELUDE module
lands in the deferred set, fall back to today's wholesale deferral. kolt's
prelude is `std::web`, a std module, which can never reach a package entry, so
on kolt the fallback is dead code - but a package whose prelude is
`pkg::<something>` that transitively imports the open file must take it,
because `seed_preludes` binds into every scope at once and cannot bind half.

## M79.4 What it costs: the seven source-less queues

An item in `prepped_locals` is `(Id, name)`. To hold it back, the drain must
answer "which file is this `Id` from" - and inside `resolve_world` that
question has no cheap answer: `source_of_id` binary-searches
`sorted_source_ranges`, which `seal_frozen_ranges` seals AFTER `build()`.
Before sealing it degrades to a linear scan of ~70 ranges, asked once per queue
item. On kolt that is the wrong order of magnitude for `prepped_locals` and
`prepped_assignments`, which are per-expression.

Three ways out, in increasing order of cost and of confidence:

1. **Seal the ranges earlier.** `sorted_source_ranges` is derived from
   `source_ranges`, and every module's range is pushed by the load walk, which
   is complete before the store. Only the ENTRY's range is pushed later. So a
   pre-entry seal over the module ranges alone is already correct for the
   question being asked ("is this id a module's, and whose"), and an id outside
   every sealed range is the entry's by elimination. One binary search per item.
2. **Stamp the source at PREP time.** Each of the seven queues grows a
   `SourceId` field, filled by the walk that pushes the item (which always
   knows `current_source_id`). Exact, no lookup at drain time, and mechanical -
   seven tuple types plus their push sites - but it widens seven structures
   pushed per expression, and M46's world-weight budget reads their size.
3. **Defer by SCOPE rather than by file.** Every one of the seven carries a
   scope or an entity that resolves to one, and a scope belongs to a module.
   Cheaper than (2), less exact than (1); recorded because it is the shape the
   item's own "scope-chain territory" note gestures at.

**Recommendation: (1), with `type_id_sources` for the queues that carry a
`TypeId` and no `Id`** - `prepped_binder_inheritance` is the case, and
`type_id_sources` already answers it (it is what T0's dirty bit reads), so (1)
plus that table covers all eleven without (2).

**The other cost, and the real risk.** B222, B236 and B237 live in exactly
this machinery - the ordering of the drains and what a re-parked item sees when
it resolves late. A deferral that re-parks an item changes the ORDER in which
two items resolve, and three known defects are about that order. Any slice here
owes each of them a pin that stays green, and a differential is the only thing
that can hold it: the same shape M76 built for the checks half - every corpus
program as the opened file of a package, analyzed warm twice, pre-store-resolved
against wholesale-deferred, byte-identical diagnostics, per-file attribution and
emitted JS. That harness exists now
(`replay_differential::an_entry_shaped_world_agrees_between_replayed_and_rederived_module_checks`
and `replay_harness::write_open_module_package`); M79's version swaps the switch
it flips.

## M79.5 Slices

- **S1 - the instrument and the set.** Report the deferred set on the phase
  line (`alias-reaching` is already there, M76) and add the per-QUEUE item
  counts, split deferred / not, so the next slice is sized on counts rather
  than on an estimate. No behaviour change. Size: S.
- **S2 - the pre-entry seal.** `seal_frozen_ranges`' module half, taken before
  the store, so every drain can ask "whose id is this" in a binary search.
  Pinned by the existing `source_of_id` callers, which must answer identically
  before and after. Size: S.
- **S3 - the two source-carrying drains.** `prepped_imports` and `prepped_uses`
  hold back their deferred items and run pre-store for the rest. These are the
  two stages M73 measured at 0.1-1.2 ms and 0.0 ms, so S3 buys nothing on its
  own - it is the slice that proves the re-park mechanism against
  B222/B236/B237 on the cheapest possible surface. Size: M.
- **S4 - the remaining nine, and the fixpoint.** The prize, and the whole of
  the risk. Size: L.
- **S5 - the fallback.** The prelude-in-the-set condition, with a fixture whose
  package prelude reaches the open file. Size: S.

## M79.6 The ruling questions

1. **Is M79 still worth building?** M76 moved the answer. The prize is ~22 % of
   an entry-shaped keystroke, most of it in S4, which is the slice that
   re-orders eleven drains with three known ordering defects living in them.
   *Recommendation: build S1 and S2 (cheap, no behaviour change, and S2 is
   useful to M76's own narrowing), then RE-SIZE S4 against S1's counts before
   committing to it.* A 22 % win is worth having; it is not worth a miscompile
   in the resolve order, and the honest position is that S1 says which it is.
2. **Does the deferral set stay a per-FILE set now that it measures 4 sources?**
   At that size a per-file set is nearly a per-file exception list, and the
   fallback (wholesale deferral) is 69. *Recommendation: yes, per-file,
   unchanged - the number being small is the argument FOR the rule.*
3. **Does S4 run the fixpoint twice, or hold constraints back?** M73 proved a
   second whole run costs 1.2-8.9 % of the first, so the simplest S4 resolves
   everything it can pre-store and lets the post-entry `build()` re-run the
   whole fixpoint rather than re-parking constraints. *Recommendation: re-run it
   whole - re-parking constraints is where B222/B236/B237 live, and a
   proven-safe 8 % second run is the better trade.*
