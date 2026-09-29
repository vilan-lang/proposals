# native-44 — PARTIAL report (2026-09-29; saved by the integrator: the lane's tool environment refused to create the report file)

Branch `native-44` off 07e8db37, three commits; LANE-STATUS.md written untracked-in-intent (it is TRACKED on next, a leftover from Order 43, so it shows as a working-tree modification; never staged).

| item | verdict | sha | pins (native_differential) |
|---|---|---|---|
| F56 | LANDED | 834de493 | `a_resource_without_drop_builds_the_same_on_both_backends`, `a_resource_is_moved_not_copied_at_its_move_sites_natively`, `a_resource_with_drop_is_still_refused_by_name_natively` |
| F53 | LANDED | 6465fc7b | `a_closure_body_erased_to_an_object_is_identical_on_both_backends` |
| item 3 (first pass) | LANDED | 78097e9f | `a_field_read_off_a_shared_read_is_identical_on_both_backends` |
| item 3 (rest) | OPEN | — | reactive-44 had no commits yet |
| item 4 (censuses) | NOT STARTED | — | after reactive-44's merge |

Every pin red first (F56 against the base emitter and against a revert of each half; F53 and the parity pin against the previous commit).

- **F56** (premise confirmed — every runnable prototype program refused at its first pipe node): a `[resource]` struct or enum is refused only when it HAS a `Drop` impl (read from `Program::drop_method_checks`, keyed on std's own `Drop`, plus the impl blocks declaring them); a Drop-less resource wrapping a `Drop` one is still refused at the member. No clone at a move site: the emitter re-decides "copy unless this instance is a resource" per instance, as the JS emitter does (the nested `Map`'s `up` copy is gone); a destructuring `match` over an owned resource no longer copies its subject. Fixture `crates/vilan-cli/tests/native/pipe_prototype.vl` (Appendix A's library): the fused chain, the switch, the `own` parameter, sealing twice, and a branch next to a resource enum print the same bytes natively. `r3_branch` and the `dyn Up` case are analyzer refusals on both backends. `docs/guide/native.md` updated.
- **F53** (premise confirmed — rustc E0271/E0308): an expression-bodied closure takes the block body's value path (the `dyn` erasure applies); the closure's cast names the object type as its return; a call through a closure-typed variable or parameter now has a return type.
- **Item 3, first pass** (over reactive-44's uncommitted std + its 27 reactive tests, with this lane's compiler): `Shared::read()` typed natively (the `Switch` node's `(followed.read().pull)()`), `write()` still refused (find 3); `|| v` over a non-`Copy` capture (rustc E0525, FnOnce) fixed by F53's value path.

## Finds
1. A Drop-less resource cannot become `dyn` (analyzer, both backends) — FILED B470, RULED allow (R39).
2. Pipe nodes move a field out of `own self`; refused at a concrete resource field ("v1 has no partial moves"); generic nodes pass only because the rule is not re-checked per instantiation — FILED B469, RULED door (a) (R38).
3. `a.write().n = a.write().n + 1` (vilan/test/shared.vl) stays refused by name natively (typing `write()` field reads would keep the right side's `RefCell` borrow alive across the left's — needs a temporary). Not filed.
4. `crypto.vl` fails natively on the base toolchain (rustc E0382 moved `salt_…`), unseen because the sweep skips non-platform-free programs — FILED F57.
5. Under reactive-44's uncommitted std only: `list-cell.vl`/`delta-law.vl` refused natively ("unbound generic type parameter (parameter 1 of struct `ListCell`)") at `impl type S: Source<type T> with Flow<T>`'s `pull = || self.get()` with S = `ListCell<X>`; not reproduced standalone — chased on reactive-44's commit.
6. `check_scope_differential::std_sources_are_recorded_and_the_entry_is_not` failed once under load, then passed alone and on the next full run — possibly flaky; noted, not filed.

## Gates at 78097e9f
native_differential 81/81 default; `VILAN_NATIVE_DIFFERENTIAL=1` 127 enumerated / 97 identical / 30 refused / 0 broken (Order 43: 125/94/31/0; the three corpus resource programs all have `Drop` and stay refused); corpus 12, split 13, examples 6, copy_elision_census 2 green at 6465fc7b (78097e9f touches only the native emitter); check_scope_differential 15/15; vilan-rt 80; clippy `-D warnings` + fmt clean; the native copy census did not move. Ledger: none.

## Owed after reactive-44's merge
Native parity over its committed layout (find 5 first, then B470's native half — the erased pair of a resource without cloning); the native copy census regenerated; the native leak census re-run (pipe instances release their stage owners and subscriptions; list-cell stays 0).
