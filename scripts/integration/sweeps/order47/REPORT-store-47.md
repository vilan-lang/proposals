## store-47: final report

**Tip `dba2e840` on branch `store-47`**, worktree `vilan/.claude/worktrees/store-47`, rebased onto `origin/next` at **`0af433fb`** (solver-47 merged). Nothing is pushed. I fetched again just before reporting: next has not moved, and perf-47, debug-47 and incr-47 have not merged yet. Every number below is against base `0af433fb`.

### Per item

| item | verdict | sha | real cause / note |
|---|---|---|---|
| **A149 S4** | DONE | 130e30d8 | Ruled door R-e. A field std marks `[internal]` no longer resolves as a member in code outside std. On `Store<T>` and `StoreSome<T>`, a member that names a field of `T` now resolves to that field's projection call: `app.address.city` is `app.address().city()`. Hover and completion work for it. |
| `store_opaque` goes (B508's remainder) | DONE, std half only | 712387a8 | The item's premise was partly wrong. B508 lets a blanket reach a closure **one** tier deep, but not two: `impl type T: StoreLeaf with Storable` still doesn't reach a closure. So the derive now sends closure fields and payloads through `StoreLeaf`'s bare tier (`store_leaf_diff`), as it does coarse fields, and the internal helper is deleted. The derive still recognises a closure by its written type text. Making it fully uniform needs a solver fix, filed as B?1; I made no inference change. |
| B547 std side | DONE | 3e690443 | solver-47's fix is on next. The derive's generated code now imports through `std::reactive::store` instead of working around the bug through `store_core`. Checked: a compiler without B547's fix plus this std gives "'Storable' is not a trait"; the tip compiler runs it. |
| B546 | DONE | de212fec | `View::autofocus` now records which element it took focus from, in a host `WeakMap`. A focus scope that finds focus already inside itself at install follows that record back out (bounded walk) to pick its restore target. Browser twin only; the process twin's `focus_scope` was already a no-op. |
| A158 | DONE | 0fd7233a, plus dba2e840 (mdBook anchor golden for the new docs heading) | `List::push_many(items)` takes a new trait `Items<T>` in `std::iterator`. `List<T>`, `HashSet<T>` and every `Iterator<T>` implement it. Works on both backends; the doc comment has an example. **ListCell decision: yes, one delta per batch.** `ListCell::push_many` and `Tracked::push_many` record a single `Splice`. `extend` stays as the list-only spelling. These are inherent methods, not `SequenceCell` defaults, because a trait default with its own generic hits a compiler internal error (B?4). |

### What changes for users
- **Breaking:** reading a std-internal field outside std is now refused, with its reason. This covers `store.path`, `store.lend`, a `StoreFlag`'s `read`, and `Region.anchor`.
  - The comment on the anchor field said hand-written `Slot`s need it, so I added `[internal] Region::end()` on both ui twins.
  - `hmr_swap`'s user `Slot` now uses `region.end()`.
  - The f27 platform fixtures in `workspace.rs` and in vilan-lsp's `document.rs` now read `region.live` instead.
- Two cases are refused with a reason:
  - A renamed projection: `request.get`, where the field `get` projects as `verb()`, would otherwise have silently reached the handle's own `get()`.
  - A type that doesn't derive `Storable`.
- Assigning through field syntax (`app.name = "Bob"`) is refused once, with a steer to `.set(..)`, instead of two errors.

### Pins
- **S4:**
  - `inference::store::a149_s4_*` (9).
  - `vilan-ide` `completion::tests::a149_s4_*` (4); planting each IDE fix's removal turns at least one of the four red.
  - `native_differential::a149_s4_field_syntax_reads_and_writes_the_same_on_both_backends` (`native/store_field_syntax.vl`).
- **store_opaque:** `inference::store::a149_a_closure_payload_is_a_leaf_with_no_equality` and `native_differential::a149_a_closure_leaf_wakes_on_every_covering_write_on_both_backends`.
- **B546:** `ui_rows::b546_a_scope_installed_after_its_content_took_focus_restores_the_opener` (red on base std: `closed=inner`), `b546_the_restore_target_is_followed_out_of_the_scope` (red with a one-step walk) and the control `b546_a_scope_installed_before_its_content_restores_the_opener_as_before`.
- **A158:** `inference::std_surface::a158_*` (3), `inference::collections::a158_a_list_cell_pushes_a_batch_as_one_splice`, `native_differential::a158_push_many_appends_the_same_on_both_backends`.
- **B547:** `module_resolution::a149_s3_a_storable_derive_in_an_imported_module_resolves_and_keys_its_map`, with its comment updated.
- Diagnostics ledger: two `NEW` rows, for the internal-field refusal and the no-projection refusal.

### Needs a ruling
1. A158 adds a new public trait, `Items<T>`, which is surface growth. The name and its home in `std::iterator` are my choice. Fixed-size arrays (`[T; n]`) are not `Items`.
2. Building a struct with std-internal fields outside std (a `Store { root = .. }` literal) is still allowed. The ruling covered member reads only.
3. Field syntax doesn't extend to enum variants (`presence.online` is not `online()`), which matches the paper's S4 scope.

### Finds filed
In `sweeps/order47/newitems47-store.json`, repros under `sweeps/order47/store-47/finds/`.
- **B?1:** a blanket chain two tiers deep doesn't reach a closure. This is B508's remainder.
- **B?2:** a blanket doesn't reach an unannotated function-item binding (`let f = nothing; f.leaf()`).
- **E?3:** member completion on a generic struct also offers methods from inherent impls at *other* type arguments; on `Store<App>` it offers `city`/`path` from `impl Store<Address>`.
- **B?4:** internal compiler error when a trait default with its own generic parameter calls its bound's member ("…requirement has no body… please report").
- **B?5:** internal compiler error when a blanket's subject is a trait (`impl Iterator<type T> with X<T>`). std's own `impl Iterator<type T> with Iterable<T>` is that shape, which leaves `Iterable` unusable.
- **F?6:** an empty `[]` passed to a parameter whose element type is fixed only by its bound is refused natively, with no span.

### Gates
- `cargo nextest run --workspace -j 6` on 3e690443: 9684 run, 9682 passed, 34 skipped.
  - The 2 failures were the mdBook anchor golden pins (`markdown_golden` and `vilan-lsp` `book_sync`), red because of A158's new docs heading.
  - I regenerated the golden in dba2e840 and re-ran both pins green; the full suite has not been re-run since.
- On dba2e840, all green:
  - `native_differential` with `VILAN_NATIVE_DIFFERENTIAL=1`: 172/172.
  - `check_scope_differential`: 15/15.
  - clippy `--workspace --all-targets -D warnings` and `cargo fmt --all --check`.
  - `ci-local.sh` `vilan-fmt`, `windows` and `perf` (T2 verdict green).
- The late-write assert passed inside the suite's inference run.

### Instructions, base vs tip
Release builds, one binary built at the base. "+ store patch" is kolt with the held store patch applied to a scratch copy and moved to the new std paths. I ran no git commands in kolt.

| | base | tip | change |
|---|---:|---:|---:|
| kolt check | 27.00 G | 27.13 G | +0.5% |
| kolt + store patch | 29.30 G | 29.45 G | +0.5% |
| math | 244.6 M | 245.7 M | +0.5% |
| browser | 1,487.8 M | 1,491.5 M | +0.25% |
| router | 1,909.9 M | 1,917.8 M | +0.4% |
| fullstack | 3,516 M | ~3,530–3,550 M | +0.4% to +1.0% (tip runs differed) |

- The store patch's own cost is unchanged: +2.30 G (+8.5%) at base and +2.32 G at tip.
- The increase comes from std, not the compiler: the tip binary with the base std measures within noise of the base. Isolated, A158's four std files cost about 0.16 G on kolt; its blanket over every iterator is about 0.09 G of that.
- These bases predate perf-47's provider index (M111), which may absorb part of the blanket cost. Please re-measure after perf-47 merges.

### Functions touched outside std
- **analyzer.rs:**
  - `resolve_field_accessor` (the hidden-field check, the field-syntax tier, and the two new refusals).
  - `same_named_field_steer` (now takes the call id and skips hidden fields).
  - `first_non_place` and `resolve_place_assignment` (the assignment steer).
  - New: `internal_field_hidden`, `field_syntax`, `read_field_through_projection`.
  - The registration block that records `Store`/`StoreSome` beside `primitive_struct_ids`.
  - Fields `field_syntax_handles` and `field_syntax_reads`; `Program::field_syntax_handles`; the `Field.internal` doc comment.
- **New module** `crates/vilan-core/src/field_syntax.rs` (`Surface::read`, `Surface::projected_fields`, `Program::field_syntax`).
- **labels.rs:** new `internal_field_out_of_reach`, the one rule the analyzer and the editor share.
- **vilan-ide `completion.rs`** (editor-47's file, kept to a small seam): `member_completions` calls a new `push_field_syntax`; `nominal_member_completions` skips std-internal fields; `live_receiver_type_id`'s `x.f` arm falls back to the projection and skips hidden fields.
- **vilan-lsp `document.rs`:** test fixtures only (the f27 tests).
- mono.rs, impl_select.rs and the emitters are untouched.
