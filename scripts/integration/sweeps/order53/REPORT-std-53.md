## std-53 hand-back (Order 53)

All four items are done: B633, A172, A171 (door (a)) and B630. There are four commits, nothing is pushed, and every gate is green.

- **Base:** b923bfc6.
- **Tip:** 3d882aaa on branch `std-53`, worktree `/home/reed/code/vilan-lang/vilan/.claude/worktrees/std-53`.
- `std-53-STATUS.md` is untracked and current.
- None of my processes are running.

### Commits

1. **c7b76d4f, B633 (fix).** `[derive(Wire)]` now works on a generic struct or enum whose fields use its type parameter.
   - **Analyzer:** the Wire boundary reads each field under the derived impl's own binders. This is B622's helper, generalised from Hashable to any derived trait and renamed `member_under_derive_binders`.
   - **`resolved_type_is_wire`:**
     - It gains a `Type::Generic` arm.
     - A type's name alone now answers only for non-generic derives. A generic derived type is judged by its arguments through the impl table.
     - So `Page<|| i32>` is refused at a field and at an `[rpc]` signature, while `Handle<Session>` stays sendable because its phantom parameter keeps a bare binder.
   - **Negative twin:** it names the bound to add, using a new steer, `argument_bound_steer`. The message reads: "'Pair<T>' does not implement trait 'Wire', ...; generic parameter 'T' is missing the bound ': Wire' its impl asks of it". The steer works for any trait.
   - **C7's pin:**
     - `borrows::a_wire_type_with_a_parameter_typed_field_is_rejected` became `b633_a_wire_type_with_a_parameter_typed_field_binds_its_parameter` (now the positive case).
     - It has a negative twin: `b633_an_unbounded_parameter_sending_a_generic_wire_type_is_refused_naming_the_bound`.
   - **Other pins:** `generics::b633_*` (3), `native_differential::b633_*` (`native/derive_wire_over_generic_fields.vl`, new).
   - **Docs:** std/encoding.md.
   - **Estate:** there are 0 generic Wire derives in kolt, the website, the examples or std's corpus. The only generic derive anywhere is std's `Handle<T>`, which is phantom and unchanged.
2. **0321ced5, A172 (feature).** `List::to_array<const N>(self): Option<[T; N]>`, built as an intrinsic on both emitters.
   - **JS:** a helper, `__list_to_array(list, N)`, which the macro interpreter also runs. It returns a copy when the length matches.
   - **Native:** `<[_; N]>::try_from((receiver).to_vec()).ok()`.
   - **How `N` is read:** each emitter reads the call's `N` from, in order:
     - the written argument;
     - the own-generic record;
     - `method_call_substitution`'s binding of the external's `const N`, resolved through the active instance.
   - **Unbound `N`:** this used to be an emitter internal error. B424's refusal now reads an `external` member's return generics too, so it reports "cannot infer the length 'N'".
   - **B623's array decoder:** `FromJson` for arrays now decodes into a `List` and converts. The separate length-0 impl is removed.
   - **Pins:** `array_lengths::a172_*` (2), `native_differential::a172_*` (`native/list_to_array.vl`). Docs: collections.md. The paper's §9 row is marked built.
3. **80bf31f5, A171 (feature).** An array type can now start a path: `[i32; 3]::default()`, `[str; 2]::from_json(..)`.
   - **Parser:** `[T; n]` before `::` is read as the array type, but only when a token scan finds the matching `]` followed by `::`, and the element parses as a type. Everywhere else `[` still opens a list or repeat literal.
   - **Resolver:** in the static-path drain, an array is handled like a nominal type. The head binds the impl's element type and length.
   - **What works:** nested arrays, a generic element, a `const N`, and `self`-methods called through the path (`[i32; 2]::to_list(xs)`).
   - **Refusal:** a list literal or a value repeat before `::` is refused with this text: "a bracket heads a `::` path only as a fixed-array type, `[T; n]` (`[i32; 3]::default()`): a list or repeat literal is a value and names no type to look a member up in; write the element type and the length, or `List<T>::` for a list".
   - **Derives:** the Default and Json derives now write an array field's path directly (`TypeExpr::is_path_head` accepts the bracketed form). `default_of` and `from_json_value_of` remain available as conveniences. The Wire derive's `{type}::rebuild` now parses for an array field; arrays are still not Wire ("arrays Wire on a need").
   - **Spec:** a line in grammar §3.6 (the `path` production plus prose) and in names §4.6.
   - **Pins:** parser `a171_*`, `array_lengths::a171_*` (2), `native_differential::a171_*` (`native/array_path_head.vl`).
   - This commit also carries B633's ledger row next to A171's: two NEW rows in the tsv, and both in proposals' `diagnostics-ledger.md`.
4. **3d882aaa, B630 (fix).** `serve_build` now serves the build's source maps.
   - `write_chunks` writes a `"maps"` list: the bundle's map (a new `bundle_map` argument), then each chunk's map.
   - `LegBuild` gains a `maps: List<str>` field. It is read where present, like `assets`, and `artifacts()` routes the maps after the chunks.
   - A `release` build writes, and so lists, a map only when `[build] source-maps = true` asks for it.
   - **Pins:**
     - `serve_build::b630_a_built_page_reaches_its_source_maps_through_serve_build`: a split leg's bundle and three chunk maps are each served as `application/json` with the build's bytes, and each script's last line names its map.
     - `b630_a_release_build_serves_a_map_only_when_it_asks_for_one`: covers release with and without `source-maps`.
   - **Golden:** the split fixture's `app.chunks.json` golden now lists its four maps. The other split goldens are byte-identical.
   - **Probes and docs:** every `LegBuild` literal in the document and shell_check probes gains `maps = []`. Docs: process.md and persistence.md.

### Ownership exceptions (listed arms)

**analyzer.rs** (incr-53a's file):

| Function | Change |
|---|---|
| `check_wire_boundary` | one call |
| `check_hashable_boundary` | the renamed helper's call |
| `hashable_member_under_binders` -> `member_under_derive_binders` | gains a trait parameter |
| `resolved_type_is_wire` | Generic arm; name fast path for non-generic derives only; its doc block moved onto it from `record_refused_rpc_wire_type`, where it had drifted |
| `check_generic_bound_satisfaction_sites` | one `or_else` -> `argument_bound_steer` (new) |
| `Intrinsic::ListToArray` | new variant, plus its row in `analyze_over_world`'s List table |
| `member_return_generics` | now reads an `ExternalFunction`'s return |
| `check_generic_bound_satisfaction_declarations` | return/parameter generic sets computed only when the member has its own generics |
| `walk_path_head_type_node` | the bracket refusal |
| `resolve_world`'s static-accessor drain | `Type::Array` arm and `has_concrete_args` |

**Other files:**
- **vilan-rust** (native-53's file): `emit_intrinsic` (one dispatch), `list_to_array` (new), and one exhaustiveness arm in `intrinsic`.
- **formatter.rs** (fmt-53's file): one expression-printer arm, `Node::ArrayType(..) => print_type`.
- **transformer.rs:** `emit_intrinsic`'s arm, `list_to_array_length` (new), and the helper's text and reserved name.
- **mono.rs:** untouched.

### Where a premise was wrong

- **A172:** the item says only that the intrinsic was unbuilt. It also needed B424's refusal to reach an `external` member's return generics. Without that, an unbound `N` was an emitter panic, not a diagnostic.
- **A171:** the item frames it as parser plus resolver. It also needed a formatter arm (`vilan fmt` declined the new head), and a parse-cost fix.
  - A speculative type parse at every `[` that starts an expression cost todo +0.8% in instructions.
  - A token scan (`bracket_closes_before_a_separator`) removed that cost before the commit was finalised (the commit was amended).
- **B630:** the premise held. It also needed `LegBuild`'s field and the fixture golden; see Q1.
- **B633:** the premise held. "Naming the bound to add" needed a new steer: the refusal only said "does not implement".
- **Doubled reporting:** a non-Wire field is reported 2-3 times (the generated `describe`/`rebuild` errors beside the boundary). This is already B614, not a new find.
  - A171 changes the array-field text in that set from "this expression cannot be used as a type" to "cannot find 'rebuild' in [u8; 3]".

### Gates (tip 3d882aaa)

| Gate | Result |
|---|---|
| Full suite, `--cargo-profile ci-test -E 'not binary(deep_nesting)' -j 6` | **10,631/10,631** passed (38 skipped) |
| - inside it: `ci_ignored_pins` | 12 |
| - inside it: `hygiene` | 3 |
| - inside it: `corpus` | 14 (byte-identical; no golden moved) |
| - inside it: `check_scope_differential` | 16 |
| - inside it: `native_differential` | 282 |
| `VILAN_NATIVE_DIFFERENTIAL=1` sweep | 282 passed, 1 skipped |
| Deep-nesting canary, 1536 KiB | 18/18 |
| vilan-lsp binary | 1,128/1,128 (27 skipped) |
| clippy `-D warnings`, `cargo fmt --check`, `vilan fmt --check .` | clean |
| `scripts/ci-local.sh perf` | T2 green, growth x1.929 |
| Late writes | 0 |

**Instructions on the three smallest examples** (this machine is the reference 9800X3D; base is the installed v0.50.0 binary at b923bfc6, tip is the release build):

| Example | Base | Tip | Change |
|---|---|---|---|
| math | 253.44M | 251.61M | -0.72% |
| watch | 315.78M | 313.85M | -0.61% |
| todo | 4210.06M | 4198.25M | -0.28% |

No `[[bump]]` row is needed. The reduction comes from the guard on `check_generic_bound_satisfaction_declarations`, which had computed the return and parameter generic sets for every wired call.

**kolt cold check RSS** (`rss-probe.py`, `MALLOC_ARENA_MAX=1` on both sides, three interleaved pairs of 5 runs, load average about 20):
- Tip/base median ratios: 0.990, 0.995, 0.969.
- kolt and website copies check clean under the tip.

`ci-local.sh windows` was not run: no cfg-gated code was added.

### Finds

Filed in `sweeps/order53/newitems53-std-53.json`, with repros in `sweeps/order53/std-53/finds/`. Both paths say order53.

- **A?1 (inference/design):** an expected type does not reach a call's own generic through a method on the call's result. `let a: [i32; 2] = xs.to_array().unwrap();` and `let x: i32 = make().unwrap_or(3);` are refused with "cannot infer". This is the same on v0.50.0, and B627 is related.
- **B?1 (diagnostics):** the "cannot infer" steer spells a method call as a free call: `to_array<4>(...)` and `get<...>(...)` instead of `xs.to_array<4>()`.

### Questions for the owner

1. **B630 adds a field to the exported `std::build::LegBuild`.** A hand-built `LegBuild { .. }` literal must now write `maps = []`. There are none in kolt, the website or the examples; only the compiler's own probes construct one, and I updated those. I marked it `fix`.
   **Rec:** keep `fix` with the CHANGELOG sentence naming the field. The alternative is to call it `breaking`, which would contradict R-j's "none".
2. **The array-head parse probe is a token scan to the matching `]`.** That is linear per list literal, and repeats at each nesting level. On unbalanced, broken input it scans to the end of the file once per unclosed `[`.
   **Rec:** keep it. An alternative is a parser-level array-head flag set by the lexer, but that is unnecessary at the measured cost.
3. **`default_of` / `from_json_value_of`:** after A171 no generator reaches them for a type that could succeed. Tuples, closures and references have no `Default`/`FromJson`; the helpers now only give a better refusal than a parse error.
   **Rec:** keep them as documented conveniences (R-h), and retire them in a later std pass if nothing outside std uses them.
4. **The `argument_bound_steer` sentence also improves Hashable and every other trait.** It sits in the checks' message composition.
   **Rec:** merge as is, rebased onto C1. If C1 moves `check_generic_bound_satisfaction_sites`, the `or_else` carries over unchanged.
