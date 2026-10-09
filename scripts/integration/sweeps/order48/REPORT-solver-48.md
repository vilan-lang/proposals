## solver-48: Order 48 report

All 14 items are closed, and every gate is green on the final tip.

**Tip and base.** The tip is `solver-48` @ **1380eee3**: 20 commits on `origin/next` @ **202c37e0**, not pushed, worktree `vilan/.claude/worktrees/solver-48`. I started from base e75bc57c. While I worked, the integrator merged native-48, debug-48, std-48, incr-48 (twice), editor-48, layout-48 and suite-48 ahead of solver. I rebased six times and re-ran the full gates after each rebase. The last rebase moved only comments in analyzer.rs plus harness files. The numbers below say which base they come from. `LANE-STATUS.md` (untracked) lists every sha.

### Per item (final shas)

- **B566** (fcb35d7d, fix). The cause is in the JS emitter only; native was already right (F34). `emit_default_instance` keyed an inherited default's instance by (default, receiver) and bound only the trait's parameters. The concrete-receiver (`OnType`) route also passed no own-generic values. Defaults now bind their own generics positionally and key the instance on them, on both routes.
  - Pins: `traits::b566_*` (4); `native_differential::a_trait_default_with_its_own_generic_binds_it_on_both_backends`. The two-bindings pin is red with the key planted back.
- **B567** (b62f9aea, fix). The item's premise was half wrong. B299 already makes `impl Iterator<type T>` mean the binder form. The two real gaps:
  - `for x in self` in such a body took the trait-default channel. It now takes the impl's own `OnConstraint(subject)` channel.
  - A `Self` return of a parameterized bare-trait impl typed as the bare trait. Because of this, std's `it.iter()` was refused. It is now read as the implicit binder.
  - Pins: `traits::b567_*` (3); `native_differential::a_loop_over_self_in_a_bare_trait_impl_runs_on_both_backends`. Natively the `Self` return is refused ("does not emit a trait object"; filed F?1).
- **B557** (8dea8123, fix, plus cleanup 579691e5). A tuple-bounded binder now filters admission by shape (`impl_subject_admits` → `tuple_bound_admits_shape`). The bound proof now reads the binder's arity and element bound (`satisfies_trait_bound_by_impls`). The conformance check's "provided by another impl" test uses admission instead of `compare_type`. `tuple_blanket_excludes` is subsumed and deleted.
  - Pins: `bounds::b557_*` (5).
- **B443 + E260's tuple case** (c8945385 feature; 788a5f40 fmt; 73bf8dad performance). This landed solver-47's `compare.vl` and `hash.vl` blankets plus a new `debug.vl` tuple blanket.
  - `debugging::s4_debug_covers_a_tuple` is un-ignored and green. dbg is unaffected: `printer::written_debug` skips std impls.
  - Solver-47's "~20 red pins" did not recur. Only 4 pins moved, all as intended: tuple `==` left a refusal list, a `len` refusal now names the import, and two pins that B557's earlier draft had moved went back.
  - Cost: the `Tuple` import made every method call scan all impls in `tuple_member_name`. That was +11% at perf `plain:160`. It is now indexed, and the cost is +0.4%.
  - Natively, the three blankets are refused at `TupleKeys` (filed F?2).
  - Pins: `tuples::b443_*` (5).
- **B562** (5fd34e11, fix). A method receiver at a `self` parameter is no longer a view value-read (`check_view_value_reads`). Both emitters already read a scalar view through at that point.
  - Pins: `borrows::b562_*` (4); `native_differential::a_method_on_a_scalar_view_auto_derefs_on_both_backends`.
- **B501's remainder** (0e44d8b9, fix). An argument call whose binding is foreign-open now waits until it is directed, or until the fixpoint stalls. The outer call seeds each argument call's expectation from the parameter type it decided (`seed_call_argument_expectations`), on the free path, its deferral branch, and the method path.
  - The ignored pin is un-ignored and extended: method, two arguments, nested let, and the undirected refusal.
- **B563** (b35ead83, **breaking**). Conformance now compares closure `context` clauses order-free at every closure position (`context_clauses_agree`).
  - Estate: 0. std, corpus and docs fences pass their gates; examples 11/11 check clean; a kolt scratch copy checks clean.
  - Pins: `traits::b563_*` (3).
- **B558** (bf5ebd2b, fix; clippy 94973c84). The new message is "Expected T, but got str instead: inside the impl that declares it, a bare `Cell::new(..)` is `Self::new(..)` … Write `Cell<str>::new(..)`". It has one NEW ledger row.
  - The item's premise was wrong: the steered spelling `Cell<str>::new(label)` was itself refused in the declaring block. It now applies the written instantiation to the rigid binder (`written_rigid_path_bindings`).
  - Pins: `generics::b558_*` (2); `native_differential::a_written_instantiation_inside_the_declaring_impl_runs_on_both_backends`.
- **B559** (5bd14db9; note 1380eee3, fix). A written `Task<..>` now assimilates its payload in the written-type drain.
  - Pins: `std_surface::b559_*`. `a_chain_of_nested_tasks_rejects_the_deep_type` was re-worded.
  - Natively, `async { async {..} }` fails rustc. That failure predates this change; filed F?4.
- **B564** (c7beefa2, fix). The cause is in `compare_type`, not the lookup route. Its value-vs-trait arm admitted only Struct/Enum; it now also admits Closure, Function, Tuple and Array.
  - Pins: `traits::b564_*`; native pin `a_two_tier_blanket_reaches_a_closure_on_both_backends`.
  - std's `[derive(Storable)]` can now call `store_diff` on closure fields (std-48's choice).
- **B565** (e0f95323, fix). A `Type::Function` receiver now takes the impl-member route.
  - Pin: `traits::b565_*`. Native refuses (filed F?3).
- **B545's view half** (efa26374, **breaking**). Under `match &mut`/`&`, a one-slot leaf of a payload's tuple pattern is now a payload view. This works on both backends, including nested patterns, aggregates and `is`. A sub-tuple or generic leaf is still refused with the whole-tuple steer; ledger rows 658/659 were re-keyed.
  - Breaking: a one-slot leaf read as a value under `&place` now needs `*`. Estate: 0 tuple patterns under view subjects.
  - Pins: `borrows::b545_*` (3); native pin `a_one_slot_tuple_leaf_under_a_view_subject_writes_in_place_on_both_backends`.
- **M124** (bcfbbbf4, performance). The rule, written in `object_trait_arguments`, `spec/types.md` §5.12 and the CHANGELOG:
  - `dyn Tr<A>` provides `Tr` at `A`.
  - It provides each supertrait at the arguments its `with` clauses thread from `A`.
  - It provides any other trait only through a blanket. A nominal implementor is never evidence for it.
  - Effect: the probe dropped from 4,357 to 97 type slots.
  - **No answer moved.** Under rule 2 the a142 answer is `One[bool]` instead of a nominal-echo fallback `bool`. Every object-provider answer over the a142 program and over kolt is the same list.
  - Pins: `std_surface::m124_*` (2).
- **M123** (8bb76a9b, performance), measured at base e75bc57c (callgrind, profiling build, kolt scratch, sequential):
  - Before: `check_generic_bound_satisfaction` was **1.92 G of 17.56 G (10.95%)**.
  - What the profile named: about 1.5 M instructions per inner question, mostly the provider table (supertrait closures and threaded arguments).
  - The fix, a memo per trait for the length of the audit (`bound_providers`), plus a tabling inner-proof memo: a YES is stored always; a NO is stored only when every cycle cut closed at or below the question.
  - After: **0.62 G of 16.35 G (3.77%)**. The inner memo alone reached only 1.86 G.
  - Pin: `bounds::m123_a_no_under_an_outer_cycle_is_not_remembered`, red with provisional NOs stored.

### Breaking edges for the v0.46.0 cut
- B563 and B545, estate 0 each (std, corpus, docs, examples, kolt).
- B557's conformance refusal can in principle break a program; estate 0, entry marked `fix`.

### Needs a ruling
- **B?2**: does a parameter's tuple bound, contained in a blanket's subject bound, count as a declared bound under B173? (An abstract `T: (2..: PartialEq)` value is not `PartialEq` today.)

### Finds
Filed in `sweeps/order48/newitems48-solver.json` (7 items), repros in `sweeps/order48/solver-48/finds/`:
- **F?1**: native, a bare-trait impl member's `Self` return.
- **F?2**: native, `TupleKeys` refuses the tuple blankets.
- **F?3**: native, a blanket at a function item's type.
- **F?4**: native, `async { async {..} }` gets rustc E0308 (predates my changes).
- **B?1**: `match &mut pair { (mut a, _) => a += 10 }` — a silent no-op on JS and a rustc failure natively.
- **B?2**: the ruling above.
- **B?3**: `fold(0, |acc: usize, n: usize| ..)` — the literal binds `i32` before the annotated closure is read (also at base).

### Gates (final tip 1380eee3 over base 202c37e0)

| gate | result |
|---|---|
| `cargo nextest run --workspace -j 6` | 9924 passed, 32 skipped |
| native_differential with `VILAN_NATIVE_DIFFERENTIAL=1` | 208/208 |
| deep_nesting at `VILAN_CANARY_STACK_KIB=1536` | 18/18 |
| clippy `-D warnings` | clean |
| `cargo fmt --all --check` | clean |
| `scripts/ci-local.sh vilan-fmt`, `windows`, `perf` | green; T2 green, growth x2.004 |

- Late writes are 0 at all 12 kolt checkpoints. No arm or local was added to `walk_expr_node_inner`.
- **kolt** (perf_count, release builds, each with its own std): base b5d098ee 15.85 G → tip 14.03 G median (−11.5%). Sequential: 15.69 G → 13.86 G (−11.7%). Peak RSS about 262 MB on both. Compared with 202c37e0, b5d098ee differs only in comments and harness.

Perf subjects, tip against base b5d098ee (millions of instructions):

| subject | base | tip | change |
|---|--:|--:|--:|
| math | 253.0 | 256.5 | +1.4% |
| browser | 1,498.7 | 1,450.6 | −3.2% |
| router | 1,771.6 | 1,694.7 | −4.3% |
| reactive-ui | 1,976.9 | 1,846.7 | −6.6% |
| ssr | 4,089.9 | 3,830.0 | −6.4% |
| todo | 5,345.5 | 5,013.4 | −6.2% |
| walkthrough | 5,487.6 | 5,087.7 | −7.3% |
| genapp:46 | 9,518.6 | 8,760.5 | −8.0% |
| plain:160 | 3,023.6 | 3,051.4 | +0.9% |
| plain:320 | 6,046.6 | 6,114.2 | +1.1% |

Base growth is x2.000; the jump from the earlier x1.94 came from the layout-48 merge.

### Functions touched

**analyzer.rs, new:**
- `bare_trait_impl_self`, `bare_trait_subject_as_binder`, `tuple_bound_admits_shape`, `seed_call_argument_expectations`, `written_rigid_path_bindings`, `rigid_self_reading_mismatch`, `context_clauses_agree`, `tuple_leaf_is_one_slot`, `bound_providers`, `check_generic_bound_satisfaction_sites` (split out of `check_generic_bound_satisfaction`).
- Fields: `bound_proof_memo`, `bound_provider_memo`, `bound_proof_cut_floor`, `tuple_member_index`.

**analyzer.rs, changed:**
- `impl_subject_admits`, `satisfies_trait_bound`, `satisfies_trait_bound_by_impls`, `check_generic_bound_satisfaction`, `check_one_conformance`, `check_view_value_reads`.
- `release_bindings_to_foreign_generics` (now returns a bool).
- `resolve_call_subject`, `resolve_method_call`, `infer_type_path`, `compare_type_rigid`.
- `capture_write_refusal`, `check_mut_captures_under_view_subjects`, `payload_view_capture_modes`.
- `object_trait_arguments`, `trait_args_candidates`, `tuple_member_name`, `impl_member_candidates`.
- `finalize_build` (the for-each `Type::Trait` arm), `resolve_world` (see seams), `Analyzer::new`.

**analyzer.rs, removed:** `tuple_blanket_excludes`.

**transformer.rs:** `emit_default_instance`, `resolve_dispatch_with`, and `walk_entity_inner`'s `Expr::Call` OnType route.

**mono.rs and impl_select.rs:** untouched.

**Elsewhere:** std `compare.vl`, `hash.vl`, `debug.vl`; docs `spec/memory.md`, `spec/types.md`, `spec/execution.md`, `std/traits.md`, `std/collections.md`, `std/debug.md`.

### Seams with incr-48
- **`resolve_world`**: two edits mid-function, none at its top.
  - B559: a `Task` arm in the `prepped_type_locals` drain.
  - B557: the conformance check's `provided_elsewhere` uses `impl_subject_admits`.
- **`finalize_build`'s for-each arm** (B567).
- **The M123 memos** exist only inside `check_generic_bound_satisfaction` and are `None` outside it. Nothing is cached across analyses.
- **For incr-48 to confirm:** `tuple_member_index` is a `RefCell` keyed by `implementations.len()` and rebuilds whenever the count changes. If a reused or pre-walked world could swap the impl table for a different one of the same length inside one `Analyzer`, the cached index could go stale.

I added nothing to `analyze_inner`, `analyze_over_world`, or the pass drivers. My scratch base worktree `solver-48-base` is removed, no load generator is left running, and no permission refusals occurred.
