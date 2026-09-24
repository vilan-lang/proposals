# A124 S2c — the estate census (reactive-41, Order 41)

Measured, not grepped: the flip (`s2c-flip.patch`, off reactive-41's tip b3fa0a47)
was applied to a scratch copy, the compiler built, and every area compiled with
it (`vilan check`, the corpus built program by program, the whole workspace
suite with `VILAN_STD` pointed at the patched std — without it, subprocess tests
under the worktree resolve the worktree's own std and read green). Base for
comparison: the same programs on the S2b tip.

| area | sites the flip breaks | what they are | migration |
|---|---:|---|---|
| std (`std::ui`, `std::router`) | 0 | — | — |
| std (`std::rpc`) | 4 | `RemoteSource::map`/`KeyedSource::map` (trait overrides of the default `map` that no longer exists — and an inherent `map` cannot stand beside the blanket) and the two `or`s that returned their cells | in the patch: the two `map`s deleted, `or` returns a `Map` node (A25's owner law moves to the leaf — OWNER QUESTION) |
| corpus (`vilan/test`) | 0 compile | 4 goldens move, runtime-identical: `dyn-objects`, `reactive-flatten`, `reactive-on-change`, `reactive`; JS copy census 405 → 400 (3 programs improve) | regenerated in the patch |
| docs fences | 0 compile | prose: the guide's "this release" paragraph, the reference's `Source`/join signatures, At a glance, the `.cell()` section | in the patch |
| examples (`vilan/examples`) | 9 | router 1, walkthrough 3, todo 3 (+2 cascades), reactive-ui 2 — derivations flowing into `SignalCell`-typed parameters/annotations | `.cell()` at the `let`, in the patch |
| split fixture (Rust test) | 1 | the router shape | `.cell()`, in the patch; 4 split goldens move |
| `.vl` consts in Rust tests | 30 pins outside A124's own (22 inference, 8 vilan-cli) | **11 annotation-only**, fixed in the patch by `.cell()` (`a_derivation_outside…`, `an_and_then_is_a_derivation…`, `a_switch_is_a_derivation…`, `b225` (a field), `b129`, five `reactive_lifetimes` apps, `router_swap…`); **5 blocked by a compiler find** (`b243`, `b371` ×4: a blanket method is not reachable through an abstract bound — `S has no method 'map'`); **8 are A25's mirror-`map` law** (`a25_*` ×6, `e74_*` ×2, markdown.rs) — owner question; **4 behaviour pins** the cold model re-expresses, left red for Order 42 to re-derive: `a113_the_owned_forms…` (a map inside a boundary registers nothing now: `map=0`, `flatten=0+0`, `ownerless map=0`), `batch_commits_value…` (a read inside a batch pulls the committed value: `doubled=10`, was `0`), `switch_and_and_then_mint…`, `switch_calls_its_selector…` (ids/selector calls counted at construction: `0`); **1 diagnostic** (`missing_return_value_regime_3…`: the void-body steer is not reached through `.map(..).cell()`); **1 no-cycle gate** — `a_disposed_exemplar_holds_no_reactive_cycle` reds: unmounted `cycles=1` (SCC of 7), the exemplar's module-level `path.map(..).cell()` leaf capturing its node strongly (root list → record → notify → node → root) for as long as it is subscribed, and a module-level cell is never disposed | see the left column |
| vilan-website | 0 | (2 pre-existing `bind_each` errors, A99, unchanged) | — |
| vilan-playground | 1 | `todo/src/client.vl:22`: `app(token, route)` hands `current_path().map(parse)` to a `Signal<Route>` (WRITABLE) bound — the one estate site of §5 (2)'s class | `.cell()` |
| `update` reached on a derivation | 0 | none anywhere in the estate | — |
| kolt (`/home/reed/code/kolt`, 9a057c6 + the owner's uncommitted edits) | 17 primary (+6 cascades); base's 4 A125 errors unchanged | 11 function RETURN types `SignalCell<U>` over a derivation (`lib/overlay.vl:447`, `model.vl:83`, `:96`, `:111`, `:119`, `:134`, `lib/storage.vl:120`, `store.vl:190`, `:197`, `:249`, `channel.vl:27` — `divorce`'s pair); 1 local annotation (`client.vl:64`, `AppContext.route`'s source); 1 FIELD (`Searchable.table`, `lib/search.vl:14`/`:37` — the paper's "always derived, read hot" → `.cell()`); 3 `combine((..))` calls given a node (`sidebar.vl:320`, `channel.vl:46`, `command_palette.vl:183`, each +1 cascade) | `.cell()` at each (the paper's 8 shared sites are among them); `Command.name` (the one `dyn` field) does not break — it holds cells today |

Blocking the flip as a whole (all still reproduce on next @9ffa397e, after
solver-41): a blanket method is not reachable through an abstract bound
(`finds/blanket_method_not_reachable_through_an_abstract_bound.vl`) — every
generic `s.map(..)` in user code breaks; the mapped-tuple `dyn` coercion
(`finds/mapped_tuple_dyn_parameter_does_not_coerce.vl`) blocks `combine`
(`s2c-combine.patch` crashes every `combine((a, b))` at run time until it is
fixed); the no-cycle gate (above).
