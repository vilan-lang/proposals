debug-50 final report. The E283 array half is done and committed. Tip `bf912087` on branch `debug-50`, based on `origin/next` `6c8b922d` (fast-forward merge). Nothing is pushed, no processes of mine are running, and the worktree is kept.

**Commits since the last report**
- `bf912087` "E283 array half: the Debug derive leaves array fields to std's any-length impl", family `fix`, with its CHANGELOG entry and a docs edit to `std/debug.md`. The earlier E293 commit `5f7e61d7` is already on `next`.

**What I found, and where the premise was wrong**
- lang-50's `impl [type T: Debug; _] with Debug` is complete and correct on both backends. I probed these shapes on JS and native and the bytes match `dbg`, `print` and the List/HashMap conventions:
  - Plain, nested and empty arrays, and arrays of structs, options and strings (including escaped quotes).
  - A derived struct with array fields (2-D, struct elements, option-wrapped, empty) and a generic `Fixed<T>` with a `[T; 3]` field.
  - An enum with array payloads, an array in a tuple, in a list and in a `HashMap` value.
  - A generic `show<T: Debug>`, a `const N` function, and `print` / `dbg` of the whole.
- The one thing to change was the derive's `debug_member` in `vilan/std/src/debug.vl`. It still unrolled every literal-length array element by element. It now unrolls only arrays of closures, which have no impl to call (each prints `<closure |i32| i32>`). All other array fields go through the std impl at any length. Output is byte-identical, so no estate output moved (the corpus passes).
- The E283 CHANGELOG text from Order 49 said the array half "waits on S2". The new entry supersedes that.

**Pins**
- `native_differential::e283_debug_takes_a_fixed_array_of_every_length_on_both_backends`, with new files `native/debug_arrays.vl` and `native/debug_arrays.stdout`.
- `inference::debugging::e283_debug_takes_a_fixed_array_of_every_length`.
- The JS pin covers closure arrays too; the native pin leaves them out, because of find F133 below.

**Gates, all green**

| Gate | Result |
|---|---|
| Full suite (ci-test, `not binary(deep_nesting)`, `-j 6`, run to the end) | 10271 passed, 0 failed, 31 skipped (ignored), 756 s |
| `native_differential` with `VILAN_NATIVE_DIFFERENTIAL=1` | 259 of 259 passed |
| `ci_ignored_pins`, `hygiene`, `corpus`, `check_scope_differential`, docs | in the full suite |
| `cargo clippy --workspace --all-targets -- -D warnings` | clean |
| `cargo fmt --check` | clean |
| `cargo run -p vilan-cli -- fmt --check .` | clean |
| `cargo test --workspace --doc` | ok |

- I did not run `ci-local.sh perf` or the RSS probe. The commit changes no analyzer, mono or emitter code, only a 4-line macro condition and tests.
- E257 S5 stays measured, not built.

**Finds** (in `sweeps/order50/newitems50-debug-50.json`; repros in `sweeps/order50/debug-50/finds/`)
- `F?1` (filed earlier): natively `print(task)` of a `Task` whose async function never awaits is refused at run time, not compile time.
- `B611`: every `[derive(..)]` over a struct with `<const N>` fails with "`N` is a length parameter … not the type `N`". Cause: macro_std's `GenericParameter` has no const flag, so `derive_binders` spells `type N`. Repro: `derive_over_a_const_generic_struct.vl`. This blocks `[derive(Debug)]` over `[T; N]`. It is in the macro surface and lang-50's area, not my files.
- `F132`, a native miscompile: an array literal is emitted as `vec![..]` where the expected type is `[T; n]` in two nested positions.
  - **Position 1:** a tuple slot of a struct-literal field, or of a `let` used by a call.
  - **Position 2:** a variant payload inside a list literal passed to `print`.
  - rustc refuses with "expected `[i32; 3]`, found `Vec<i32>`". JS is fine. Repros: `native_struct_field_tuple_holding_an_array_literal.vl` and `native_array_literal_in_a_variant_inside_a_list_literal.vl`.
- `F133`: natively a struct with an array-of-closures field (`[|i32| i32; 2]`) is refused by name, while `Option` and `List` of closures are admitted, so `[derive(Debug)]` over it builds on JS only.

**Questions for the owner**
1. Should the const-generic derive gap (`B611`) be fixed by adding `is_const` to `GenericParameter`? I recommend yes, as a small slice for the next order. It is the natural completion of E283's array half.
2. Is family `fix` right for `bf912087`? I recommend yes, since output is byte-identical and the derive is simplified.
3. For the seal: the two native miscompiles (`F132`) are silent only on rustc refusal, not wrong output, so I recommend they do not block it.
