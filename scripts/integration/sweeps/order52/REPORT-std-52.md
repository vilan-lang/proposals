## std-52 hand-back (Order 52)

All four items are committed, nothing is pushed, and every gate is green. One commit (B622) changes analyzer.rs, which is outside my ownership; it is listed under item 3 and in question 1.

**Base:** 697c9517. **Tip:** 37005906 on branch `std-52`, worktree `/home/reed/code/vilan-lang/vilan/.claude/worktrees/std-52`. No processes of mine are running. `std-52-STATUS.md` is untracked and up to date.

### Commits
1. **feb03f5b, B621 (fix).** Marker `Eq` impls next to each `PartialEq` impl, bounded by what the type holds: `bool`, `List<T: Eq>`, `Option<T: Eq>`, `Result<T: Eq, E: Eq>`, `HashSet<T: Hashable + Eq>`, `HashMap<K: Hashable + Eq, V: Eq>`.
   - Files: compare.vl, option.vl, result.vl, hash_set.vl, hash_map.vl.
   - Pins: `traits::b621_*` (2). Docs: std/traits.md.
   - The premise held. HashSet and HashMap were mentioned in the item but not in the brief; I added them because the item recommends them.
2. **10b45647, B623 (feature).** Arrays now have `Default` (`impl [type T: Default; const N]`), `Json`, and `FromJson`.
   - `FromJson` checks the length: "expected an array of 2 elements, found 1".
   - Length 0 has its own, more specific impl. There is no `List`→array conversion to build from, so the general impl seeds with the first element and overwrites the rest.
   - New std helpers: `std::default::default_of<T>()` and `std::json::from_json_value_of<T>(value)`. An array type can't start a path (`[i32; 2]::default()` doesn't parse), so these spell the call another way.
   - macro_std gains `TypeExpr::is_path_head`. The Default and Json generators (struct fields and enum payloads) use the helpers only for a member whose type can't start a path. The import is added only when needed, so derives over ordinary types emit exactly what they did before.
   - The new json.vl code sits at the end of the file: the corpus goldens record std line numbers (json.vl:521/669/719), and this keeps them byte-identical.
   - **No Wire impl for arrays was written.**
   - Pins: `array_lengths::b623_*` (4), plus `native_differential::b623_*` (`native/array_std_second_wave.vl`). Docs: collections, traits, encoding.
3. **fe519fd7, B622 (fix). Ownership exception: analyzer.rs, incr-52a's file.**
   - Functions touched: `check_hashable_boundary` (one call), `resolved_type_is_hashable` (a new `Type::Generic` arm, and the name shortcut now applies to non-generic derives only), and a new `hashable_member_under_binders`.
   - The boundary now reads each field under the derived impl's own type parameters.
   - Second half of the fix: a generic derived type used as a field was judged `Hashable` by its name alone. Once B622 lets generic derives exist, that let `Holder<|| i32>` hash two different closures to the same key without any error. It is now judged through the impl table.
   - Pins: `generics::b622_*` (3), plus `native_differential::b622_*` (`native/derive_over_generic_fields.vl`). Docs: collections.md.
4. **37005906, B615 (miscompile, pins only).** No compiler change; the corpus is untouched.

### Where premises were wrong
- **B615:** already fixed on the base. It was filed against ca407da0, before B578 landed, and v0.49.0 prints `8`. I probed 19 more shapes — binary and unary values, method and closure parameters, `&str`/`&bool`/`&f64`, a field, element or index of a call's result, unwrap, a struct-literal field, string interpolation, two views in one call. All are identical on both backends. I pinned them all and checked the pin fails when B578's call arm is disabled.
- **B622:** the item says the Wire boundary "has the same shape to compare against". It doesn't: Wire refuses parameter-typed fields too, and on purpose. That is C7's guard, pinned by `borrows::a_wire_type_with_a_parameter_typed_field_is_rejected`. I first fixed both boundaries, hit that pin, and withdrew the Wire half. Wire is unchanged.
- **B623:** the item's suggested `default_of` helper was the right call, but the same path problem also hits the derived `FromJson` decoder in three places, and the plan to mirror `List`'s decode assumed a `List`→array conversion (`to_array`, array-lengths.md §9) that was never built.

### Gates
| Gate | Result |
|---|---|
| Full suite, `--cargo-profile ci-test -E 'not binary(deep_nesting)' -j 6` | 10,531 / 10,531 passed (32 skipped) |
| — inside it: `ci_ignored_pins` | 12 |
| — inside it: `hygiene` | 3 |
| — inside it: `corpus` | 14 |
| — inside it: `check_scope_differential` | 16 |
| — inside it: `native_differential` | 273 |
| `VILAN_NATIVE_DIFFERENTIAL=1` sweep | 273 passed, 1 skipped |
| Deep-nesting canary at 1536 KiB | 18 / 18 |
| `vilan-lsp` binary | 1103 / 1103 |
| clippy, `cargo fmt --check`, `cargo run -p vilan-cli -- fmt --check .` | clean |
| `scripts/ci-local.sh perf` | T2 green, growth ×1.929 |
| Late writes (kolt and probes) | 0 |

**RSS on a kolt copy** (base release built from 697c9517 vs tip): 12 interleaved pairs give a median ratio of **1.0074**. Separate 11-run blocks read between −1.8% and +3.5% because four other lanes were loading the machine. The deterministic allocator counter shows heap peak 242.2 → 242.3 MB (+0.04%) and type slots +0.3%.

Analyzer functions changed are the three listed under B622. No changes to mono.rs or any emitter.

### Finds
Filed in `sweeps/order52/newitems52-std-52.json`; repros in `sweeps/order51/std-52/finds/`.
- **B?1 (JS miscompile):** a module-level scalar binding read only through `&NAME` is never declared on JS (`ReferenceError`); native is correct. Most likely the reference isn't counted when it resolves.
- **B?2 (JS internal error):** a static method whose type parameter only an expected type fixes, called through a chain (`Holder::build().unwrap()`), hits "internal: … please report"; native prints 7.
- **B?3 (false refusal):** a generic struct literal with a `None` field next to a field that fixes `T` is typed `Page<T>` and refused at its use. This reproduces on v0.49.0.
- **A?1 (design):** an array type can't start a path (`[i32; 3]::default()`).
- **A?2:** `list.to_array()` from array-lengths.md §9 was never built.

### Questions for the owner
1. **B622 lives in analyzer.rs, incr-52a's file while S7b reshapes the checks.** It is three small functions in one commit. Recommendation: merge std-52 after C1, rebasing that commit onto it. If C1 moves `check_hashable_boundary`, the change carries over as-is.
2. **Wire for arrays (B623): is the "arrays Wire on a need" rule lifted?** Recommendation: keep holding it until there is a need and A?2's `to_array` exists. The Wire generator would also need the same path-spelling treatment in its three `{type}::rebuild` sites.
3. **Relax C7's Wire guard so a parameter reached by a field can be Wire** (`[derive(Wire)] struct Page<T> { items: List<T> }`)? Recommendation: yes, in a later order. B194's type-parameter binding makes it sound, provided `resolved_type_is_wire` judges a generic derived type by its arguments on the same day. That code shape is the withdrawn half of B622 and can be revived.
4. **A?1, array path heads.** Recommendation: door (a), allow `[i32; 3]::default()` in expression position. The two new std helpers would then stay as conveniences or be retired.
5. **B615's CHANGELOG entry.** It is marked `miscompile` and labelled "(pins; no behaviour change since v0.49.0)". Should a pins-only close carry an entry at all? Recommendation: keep it, so the cut lists the item as closed, unless the release-notes policy says pins-only work is noted on the tracker only.
6. **B621's `HashSet`/`HashMap` bound.** I bounded both by element `Eq`, the conservative choice, rather than by any `Hashable` element (hash identity is total). Recommendation: keep it as written; widening it later breaks nothing.
