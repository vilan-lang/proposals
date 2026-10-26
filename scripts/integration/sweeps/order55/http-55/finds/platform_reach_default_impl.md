# http-55 find: an `impl Default` in a `@process` std module refuses every browser
# app that reaches a generic `N::default()`

Met building M164: http.vl (a `[platform("@process")] mod self;` module) briefly
carried `export impl BodyLimits with Default { fun default(): BodyLimits { .. } }`.
`vilan check` on kolt's copy (b04095a, lucide carried) then refused the CLIENT
entry, at kolt's `channel_page`:

    `default` requires the `@process` platform its file declares and cannot run on `browser`
    reachable from the entry: main → closure → closure → closure → app_shell → closure →
    main_shell → closure → closure → page_for → channel_page → closure → closure →
    child (std::web::ui) → place (std::web::ui) → place_swap (std::web::ui) →
    follow (std::web::ui) → sub (std::reactive) → observe_flow (std::reactive) →
    start (std::reactive) → start (std::reactive::delta) → default (std::default) →
    default (std::http)

`std::reactive::delta`'s `MapSum::start` calls `N::default()` for a stage's own `N`
(delta.vl ~3711); the platform reach counts EVERY `Default` impl in the world as a
callee of that static call, including one the browser can never instantiate
(`BodyLimits` is not an `N` any client flow carries). The lane worked around it
(`BodyLimits::new()`, an inherent function). A minimal package repro (a `@process`
package module with `impl Default`, a browser entry using a `SignalCell`) did NOT
reproduce it — the reach needs the dyn-dispatched flow path kolt's `ui::each`/`sum_by`
takes — so the kolt copy is the repro.
