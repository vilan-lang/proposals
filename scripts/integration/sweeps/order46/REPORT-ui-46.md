# ui-46 — final report (A157)

**Branch `ui-46` @ f5b7b0dd** (`f5b7b0dd792135195df2b3a0f5f7ddc3bf12d204`): 4 commits on `origin/next` @c3da9fa3. Worktree: `vilan/.claude/worktrees/ui-46`. Nothing is pushed. Since I started, origin/next has moved to 57d6adc2 (an `editors/vscode` dependency bump). I did not rebase, so every gate number below is on c3da9fa3 + 4.

## What was built, per step
1. **Browser** (bb8b85b2):
   - `View::autofocus` calls `register_autofocus(autofocus_elements, self.element)` and writes **no attribute**. Its bounded clock (microtask, then rAF, then rAF; B271) now runs through `autofocus_settled(element)`. An attempt that finds the element inside a live focus scope's root ends the clock without focusing, so the scope's show decides.
   - `focus_initial` walks `root.query_selector_all("*")` and picks, in order: the first registered descendant in tree order; else the first native `[autofocus]`; else the first tabbable; else the panel.
   - `AUTOFOCUS_MARKER` and `attribute_written_for` are deleted. The browser `attr` writes `name` as spelled, so `.attr("autofocus","")` writes the native attribute.
   - No `autofocus`/`data-autofocus` attribute is left by `.autofocus()` (pinned).
2. **Server** (same commit): `View::autofocus` is now `self.attr("autofocus", "")`, and `attr` serves every name as written.
3. **Steer** (495fdf8c, relocated in f5b7b0dd):
   - `check_written_autofocus` is a post-build pass called right after A155's `check_class_written_twice`.
   - It recognises an element-head attribute by the desugar's zero-width `attr` member span; a written `.attr(` spans its name, so it is never steered.
   - It skips std, dependencies and derived code, and warns at the attribute's name.
   - The LSP publishes the code and offers the quick fix. One `NEW` ledger row.
4. **Pins**: red first, every one, by mutation: the in-scope deferral was planted out and the steer call commented out. Listed below.
5. **Docs** (f372afd3):
   - `guide/ui.md` (the `autofocus` and focus-scope sections, including the scope-before-content point) and `std/browser.md` (the `attr` and `autofocus` rows).
   - The comments in both twins are corrected: A121 §6.1 and A151's wording are gone.
   - A151's CHANGELOG entry under `## Unreleased` is rewritten as one A157 entry, `<!-- family: feature -->`.
6. **Kolt patch**: details in its own section below.

## The scope-before-content check
**Confirmed for the registry: the scope does not need to exist before its content.**
- `focus_initial` (browser/ui.vl) walks `self.root.query_selector_all("*")` when the show calls it, and asks `autofocus_registered(autofocus_elements, candidate)` for each candidate.
- Registration is keyed by element and happens at build time, so order does not matter.
- The pin proves it: `early` mounts later through a `when`, after its sibling `late` registered, and the show still starts on `early` (tree order).

**Portals.** `focus_initial` uses DOM descent, not A128's reach test. `focus_reaches_from` (the stack) is used only by the wrap, the guard and `on_leave`.
- A submenu portal's registered element is found by the submenu's own scope (its root contains it), never by the parent menu's.
- A portal with no scope of its own counts as outside: its element self-focuses on the clock, and no show picks it. Its tabbables behave the same way.

**Where ordering does matter** (not the registry, and older than A157): the scope's restore target.
- `focus_scope` captures `restore = active_element()` at install.
- If the content was built before the scope was installed, e.g. `let content = <input .autofocus()/>; <div .on_mount(|e| focus_scope(e, Contain))>{content}</div>`, the content's microtask runs first and takes focus.
- The scope then remembers the input, and closing returns focus nowhere. Probe: `open=inner`, `closed=inner` (detached); with the content written inline, `closed=opener`.
- **kolt is not affected**: `overlay.vl` calls `focus_scope(panel_element, ..)` synchronously in the same render that built the body.
- Filed as B?1.

## The WeakSet binding as written (browser/ui.vl, private)
```vilan
external struct AutofocusRegistry;
[extern(new, "WeakSet")]
external fun autofocus_registry(): AutofocusRegistry;
[extern(method, "add")]
external fun register_autofocus(registry: AutofocusRegistry, element: Element): void;
[extern(method, "has")]
external fun autofocus_registered(registry: AutofocusRegistry, element: Element): bool;
let autofocus_elements: AutofocusRegistry = autofocus_registry();
```
- These are free functions rather than an `impl`, on purpose: std_twin_parity counts the members of every declared type, so an `impl` would have needed three allowlist entries.
- Emitted JS: `const autofocus_elements = new WeakSet();`.
- `std_twin_parity` is green with no allowlist change.

## Pins
- `ui_rows`:
  - `a157_a_scope_starts_on_the_first_registered_descendant_and_the_dom_carries_no_marker` covers:
    - no attribute on any registered element, outside or inside a scope;
    - outside a scope, focus on mount;
    - inside one, the clock defers;
    - first in tree order of two registered, ahead of an earlier native `[autofocus]` and the first tabbable;
    - the native fallback in a scope with nothing registered;
    - `.attr("autofocus","")` writing the native attribute.
  - `a157_the_server_render_carries_the_native_autofocus` covers the method, `.attr(..)` and element syntax.
  - These replace the `a151_*` pin.
- Updated: `a121_the_show_takes_the_focus_and_autofocus_says_where` (markup is now `{"name":"marked"}`), `a121_the_ssr_twins_render_the_same_markup_and_trap_nothing` (now the scope only; autofocus moved to the a157 server pin), and A45's `the_ssr_twins_of_the_mount_hook_render_the_same_markup_and_run_nothing` (now `<input name="modal" autofocus="">`).
- `inference` `styling::`:
  - `a157_a_written_autofocus_in_an_element_head_warns_and_steers_to_the_method`: both platforms; bare, mid-head and `("")`; the fix applied compiles and is not steered again.
  - `a157_an_explicit_attr_call_is_not_steered`: `.attr` in a head or a chain and the method are silent; `autofocus(flag)` warns but offers no edit.
- New helper in support.rs: `warning_diagnostics_with_std_on`.
- `vilan-lsp` `written_autofocus_tests`: `a_written_autofocus_becomes_the_method` and `the_steer_is_published_with_its_code`.

## Goldens moved, all runtime-identical
None of these programs writes `autofocus`.
- `element-syntax.mjs`, `ssr-render.mjs`: the server `attr` body loses its `if (name !== "autofocus")` guard.
- The split fixture's 4 JS artifacts: `attribute_written_for` and `AUTOFOCUS_MARKER` are gone, and `apply(.., attribute_written_for(name), ..)` becomes `apply(.., name, ..)`. Everything else is temporary renumbering; with `$x` names normalised, those are the only three hunks. `app.chunks.json` did not change.

## The steer: code and fix-data API (`vilan_core::parsing`, beside B520's `foreign_spelling_fix`)
- `pub const WRITTEN_AUTOFOCUS_MESSAGE` is fixed text with no slots. It says the native attribute acts only at the initial parse, quotes Chromium's "Autofocus processing was blocked…", says to write `.autofocus()`, and names `.attr("autofocus", "")` as the spelling for a `<dialog>` or a popover.
- `pub const WRITTEN_AUTOFOCUS_CODE = "element-attribute/autofocus"`.
- `pub fn element_diagnostic_code(message) -> Option<&'static str>`.
- `pub struct ElementFix { code, title, span, replacement }` and `pub fn written_autofocus_fix(source, message, span) -> Option<ElementFix>`. It rewrites a bare `autofocus` or `autofocus("")` to `.autofocus()` in place, and returns `None` for any other value.
- `publish.rs` chains the code after ForeignSpelling's. `document.rs` offers the fix from the warnings loop, because warnings are not in `diagnostics`.

## Kolt patch
- File: `sweeps/order46/ui-46/kolt-autofocus.patch`.
- The six sites are `channel.vl` ×3, `command_palette.vl`, `sidebar.vl` and `theme.vl`. Each `autofocus` line is removed and `.autofocus()` is inserted just before the head's first dotted link, after the attributes and `on:` handlers.
- **It applies after `reactive-46/kolt-a152-message-row.patch`**: the channel.vl base is blob da54413, which is a152's result. It also stacks cleanly after store-46's `kolt-a149-s6-store-exhibits.patch`.
- solver-a-46's `kolt-b515-imports.patch` is already applied in kolt's working tree.

How I verified it, on a scratch copy (kolt working tree + a152 + a150 + mine) with the tip release binary:
- `vilan check`: 0 errors and 0 warnings. The same copy without my patch shows exactly six A157 warnings.
- `vilan build .`: both legs build. `client.js` carries `new WeakSet` and no `data-autofocus`.
- `vilan fmt --check` is clean on the four files.
- The browser runtime is not verified.

## Instructions on kolt `vilan check`
Measured with `perf_count.py`, `VILAN_SEQUENTIAL_CHECK=1`, warm cache, deterministic to about 10k instructions.

| Binary | Instructions |
|---|---|
| Base (next @c3da9fa3) | 25,612.2M |
| Final tip | 25,621.5M (+9.3M, +0.04%) |

- The pass alone costs about +15M, found by toggling only its call. The std change costs about +7.5–9.5M, found by swapping `VILAN_STD`.
- In the first placement, with the fix data in `elements.rs`, kolt read **+564M (+2.2%)** from items check never executes. Moving the items into `parsing.rs` removed it (filed as M?2).
- `ci-local perf`: T2 verdict green, growth ×1.938.

## Gates (tip f5b7b0dd)
- `cargo nextest run --workspace -j 6`: 9581/9581 passed, 33 skipped. This includes corpus, split, docs, diagnostics_ledger, std_twin_parity and check_scope_differential.
- `native_differential` with `VILAN_NATIVE_DIFFERENTIAL=1`: 157/157.
- `ci-local.sh` fmt, vilan-fmt, clippy, wasm and perf: all green.

## Finds
All three are in `sweeps/order46/newitems46-ui.json`.
- **B?1**: the restore-target ordering problem described above.
- **M?2**: kolt's instruction count moves about ±2% with unrelated item placement because of codegen-units=16 in the release profile. That makes the perf gate flaky. Options: `codegen-units = 1` for the measured and shipped profile, or a stated band.
- **E?3**: element-head completion still offers bare `autofocus`, which now warns. It could offer `.autofocus()` instead.

## Needs the owner's ruling
1. **The deferral is my reading of "outside a scope it keeps today's bounded focus-on-mount".** Inside a live scope, the method no longer focuses on its own clock. This fixes a real race: with two registered elements in an overlay, the second element's last rAF attempt could take focus from the first after the show had latched. The cost: a driver that installs `focus_scope(..)` and never calls `focus_initial()` no longer gets autofocus inside it. The docs say the show is the driver's job, and kolt calls it.
2. **`.autofocus()` on a scope's root element** counts as inside the scope, but the walk only looks at descendants. So it is ignored, and the scope starts on the first tabbable. This is an edge case and I left it as is.
3. **Server `.autofocus()` now serves the native attribute** (A157 §2 as ruled). That changes served markup for every page that chains it.
