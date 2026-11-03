# Order 55 owner questions (for the integrator to present after the seal)

Drafted 2026-10-27 by the seal-sweep clerk from the nine lanes' hand-back messages (rpc-55 also in REPORT-rpc-55.md) and notes55.md. Every question carries the lane's own recommendation; "Rec" is the lane's, not a ruling. Placeholder ids in the lanes' text are replaced by the real ids of allocated55-draft.json (finds are filed by the sweep, so those numbers exist once finds55-draft.json has been applied). Items the order CLOSES are named by id; the owner holds the one ruling already deferred (closure-owner.md, below).

## Already held by the owner

- **closure-owner.md (B677 door 2), 2026-10-26:** the owner rules at the Order 56 draft, not mid-order. rpc-55 shipped door 1 (the warning) as built. The paper's rec: make a closure parameter answering `View` / `impl Slot` carry `context owner_scope` by default, `sync` implied, behind this order's warning, no opt-out spelling until a caller wants the creation owner.
- **A live F5 check of the Order 54 debugger additions (standing)**, now also the S8 trace line with the effect's place (B646) and the `a closure in <name>` frames (E336).

## rpc-55 (Fable; M172, B677, M165 rpc half, A174 door 2)

1. **B677 door 2** (`closure-owner.md`): make a closure parameter answering `View` carry `context owner_scope` by default? Rec: yes, narrowed to `View` / `impl Slot`, `sync` implied, in Order 56 behind this order's warning; no opt-out spelling until a caller wants the creation owner. (Held for the Order 56 draft, see above.)
2. **`MaybeSignal::bind(react: |T| void)`** is the one std site the warning would flag (gated out as library code): should `react` carry the clause so a reaction's registrations die with the run? Rec: no - a reaction is a DOM write; leave it, noted in the paper's section 3.
3. **M165's log line wording:** the brief asked to keep the runtime's `unhandled task error (spawned in accept_socket)` line; the task no longer dies, so the lane's line (`rpc `m` threw, and the call was answered with the error: ...`) replaced it. Rec: accept the lane's line.
4. **A174 door 1** (revoke by value, filed as A175): Order 56? Rec: yes, S-M, with what door 2 taught (channel by root identity, grant by path identity, `session.revoke(channel)` or `release_grant(base)`).
5. **M173** (the store's per-key diff, K^2 hash copies at K keys released one turn each): a std lane in Order 56? Rec: yes - a key-touch write diffs that key alone; `node_empty` asks `len()`.

## incr-55 (Opus; P6a / M157, N182, N179, M156, E292)

1. **P6a's cost rows:** +0.04 to +0.69 % on six example rows, carried by 12 `[[bump]]` rows (1.002-1.008). Rec: accept - plain packages and kolt go down about 0.5-1 %, the css row goes down 18 %, and the cost is the prefix shape's own.
2. **M163 under R-n door (c):** the ruling rested on about 4 ms; on the owner's current kolt `plan_resource_drops` reads 30-110 ms. Rec: close M156 as ruled (done in the sweep), keep M163 OPEN with the new figure (stamped), decide again inside Order 56's E292 re-baseline, door (a) if the pass still matters once `check_view_escape` is dealt with.
3. **RULED 2026-10-27 (owner):** the seal's pass 2 runs the perf leg on the ANCHORED kolt@46c5b59 (seal-55b.sh); the re-anchor and the E121 re-baseline are filed for Order 56 as **N186** (tooling-56, first; E340 is the incr door on the new series). The question as asked: **The E292 series on the current kolt** has four unmeasurable rows and the rest read 3x or more the old series (E340). Rec: re-anchor `lsp-latency.py`'s model.vl and parse-break scenarios and start a new series before Order 56 picks a door, as N174 did; update seal.sh's kolt commit at the same time (N175 is done).
4. **N183, the text-based macro gate** (`entry_source.contains("macro")`). Rec: Order 56, size S; count the estate first since the fix changes which programs are cached.
5. **The tier oracle** (`VILAN_TIER_ORACLE`, a world field + key bit). Rec: keep it - cheap, and P6b (Order 56) can re-run the estate census under it.

## std-55 (Opus; M166, M165 boundary, M171, M169, M167, M168, M170, D16)

1. **M171 and M168 are `breaking` by the estate rule.** Rec: keep both markers; kolt takes the two-declaration patch (M171; `std-55/kolt-m171-std_ext.patch`).
2. **What does `any` hold (A176 / F150)?** Rec: refuse a value `any` cannot hold at the checker (number, `str`, `bool`, or an `Option` of those), `print` and `canonical_hash` excepted; that also lets M165's message name the vilan type. Count the estate first (expected 0).
3. **`SqlValue` (M175).** Rec: Order 56, as filed.
4. **`[default(..)]` (M174).** Rec: a parser/solver lane builds it - it spans the attribute table, `meta::Field` and the derive.
5. **`ui::nothing()` cannot be decorated:** a builder call such as `attr` throws on it. Rec: leave it documented; a placeholder that silently swallowed `attr` would hide mistakes.
6. **M167 adds a `SignalCell<HistoryEntry>` instance to every routed client**, about 50 lines in the split fixture, whether or not the app reads `current_entry()`. Rec: accept.
7. **F149, NULL column reads** (JS `null` vs native `0` / `""`). Rec: make JS coerce to the native answers, in the next std lane.

## parser-55 (Opus; B652, B653, B655, B654, B656, B658, B660, B661, B663)

1. **One-line `[extern("...")]` bodies are JS source, yet the lexer now validates their escapes as string escapes:** `/\d/` in one is refused, and writing `\\d` would emit a different regex. Rec: keep - estate 0, B654's triple-quoted form is the spelling for host code, and one escape grammar for every `"..."` beats a context-dependent lexer; say so in the extern docs.
2. **B658's recovery renames the `is` test's single capture to the `let`'s name** (keeping the capture's own name when the block reads it). Rec: keep - it reads the way the author meant in both kolt shapes and the message prints the respelled statement.
3. **B655 also refuses `let` / `mut` and expression statements in impl bodies**, beyond the item's struct/enum/trait/impl/mod (a `let` there was a runtime ReferenceError; associated constants, if wanted, would be a designed feature). Rec: keep the refusal.
4. **B652's family:** `miscompile` (lane prompt, the tracker's kind) vs `fix` (R-o). Rec: `miscompile` - the value differed from the spec on both backends. (The CHANGELOG entry carries `miscompile`.)
5. **`check` / `build` now print parse errors before analyzer errors** (a listed arm in main.rs). Rec: keep; tooling may want a `tests/diagnostics.rs` pin (parser side only is pinned).

## solver-55 (Opus; B646, B649, B647, B659, B667, B670, B664, B665)

1. **Kolt perf:** the lane costs kolt's warm package check +0.24 % instructions (B646 +0.11 %). Rec: accept as a kolt bump at the seal; the examples already carry `[[bump]]` rows (1.005 B646, 1.004 the rest). (See the integrator's items.)
2. **B665's narrowing:** a style constructor returning its style and called at run time still reports at the caller ("evaluate this call inside a `const`"). Rec: keep - such a function is written to be called inside `const`, and 15 existing pins rely on it.
3. **B685, the JS fallback-view miscompile** (`opt.unwrap_or(&0) + 1` prints `0,01`). Rec: the transformer lane reads the fallback out where B577 reads the payload; S.
4. **E345, placing UI bindings and derivations in the trace.** Rec: yes, after this order - thread a location through `follow` and the `bind_*` helpers and mark `Pipe::memo`.
5. **B646 guard for compiler-called trait members:** std must not mark `[track_caller]` on a member the compiler calls implicitly (operators, string interpolation, derives); nothing enforces it. Rec: refuse the attribute on those traits' members, an S follow-up in a solver lane.

## tooling-55 (Sonnet; E335, E336, E333, N175, E334)

1. **E341:** should a `--watch` session kill or forward to its current child on SIGTERM / SIGHUP? Rec: yes - the watch loop registers its pid in the same registry; the hook forwards, waits briefly, exits 130. XS-S, Order 56's tooling lane.
2. **E343 / E334:** should the E126 exhibit grow to track today's kolt, or the recording be retaken and the band widened? Rec: leave the gate ignored until the incr work settles, then re-record once from kolt in release and size the exhibit to roughly 0.5-1x of kolt.
3. **E335 off Linux:** a terminal Ctrl-C reaches the child twice (the si_code test is Linux-only). Acceptable? Rec: yes for now (node's default handler is idempotent); verify on macOS at the next release if anyone runs vilan there.
4. **E333's open ends:** B682 (an un-annotated `Ok` / `Err` list) belongs to solver - rec: schedule it with the next solver lane; E342 is small - rec: fold into the tooling lane.

## http-55 (Opus; M164)

1. **An over-cap read ends the handler as a cancellation**, not through a `Result`-typed read. Rec: accept - code after a refused read must not run; M176's stream gives the typed form.
2. **Stopping node from reading during the 500 ms linger uses node internals** (`request._dumped`, a per-socket `destroySoon`). Rec: accept - the only way to stop node reading a refused body; if node renamed the flag it falls back to read-and-discard (slower, still correct).
3. **The 500 ms linger** after a refused or unread over-cap body is Go's `rstAvoidanceDelay`. Rec: accept; add a timeout setting only when someone needs one.
4. **The rpc POST leg answers a bare `413`**, not an envelope (`HttpTransport` reports `Transport(413)`). Rec: accept; a row for `docs/std/rpc.md`'s status table can go in with the merge (not yet edited).
5. **M179 (handler panic ends the node server; native never answers)** in Order 56, size S. Rec: yes - report the panic once and answer 500 on both backends.

## std-55b (Opus; A173 S2, E332, F146)

1. **THIRD-PARTY-NOTICES:** `vilan-rt-term` is in the Covers line by hand; a regeneration moves 146 lines (every workspace version 0.41.1 -> 0.52.0, three licence blocks reordered). Rec: regenerate at the v0.53.0 cut, not in a lane. (See the integrator's items.)
2. **The decoder's standing cost:** +0.9-1.4 % `vilan check` instructions on every program that loads `std::process`, kolt RSS +1.9 %, because the ruled name `process::keys` puts the decoder in `std::process` (the alternative, a separate module with another import path, is a Q1 re-ruling). Rec: accept; the bump rows carry it.
3. **F153, the native `for` over a resource.** Rec: a native lane in Order 56 (S: borrow a resource place subject instead of moving it). Until then `for key in keys` builds on JS only and the docs teach the `match` loop.
4. **E346, debug escaping of control characters** (`dbg` of a `Paste` prints a live ESC). Rec: fix now that B652 settles the literal spelling; count the goldens it would move first.
5. **N185, tokio's unsound advisory.** Resolved in-order by the integrator's commit 1d666757 (the lane recommended exactly that); closed on arrival in the sweep. No decision left.
6. **Bracketed paste with a redirected stdout** is switched on only when stdout is also a terminal. Rec: keep.

## fmt-55 (Sonnet; B671, E337, E338; E339 kept)

1. **B671 keeps the written `;`** on if/for/bare-block statements as well as `match`. Rec: keep as written - the tree cannot tell a redundant `;` from a value-discarding one without types, and dropping would change meaning for a `match` with non-unit arms.
2. **E338 / E337 move one kolt line** (`task_table.vl:429`, 101 columns, becomes a 5-line hole). Take the reflow into kolt with the Order 55 patch? Rec: yes, and let kolt's own `vilan fmt` do it; it is mechanical.
3. **E347 (`return f(..)` never breaks)** is a clear XS gap of the E329/E337 kind. Rec: next order, or a fold into a later fmt lane.
4. **E348 / E349:** rec: do not build now (no estate line); leave open as low priority.
5. **E350:** rec: leave - the decline is honest and names the right line.

## The integrator's own

1. **The runner.** `vilan-linux-1` (the self-hosted trusted-ubuntu runner) was OFFLINE during the order, so the trusted ubuntu legs queued; the owner brought it online ("proceed with the merges and the seal") and the ubuntu legs ran green on 6e9f5d57. Check it online before the seal's CI and the cut. L24 (R-p, the Windows runner's routing) still waits for the owner to register `vilan-windows`; until then a Windows-only verdict is CI's (F148 is the live example: the native Windows `Keys` cancellation pin is ignored on Windows).
2. **THIRD-PARTY-NOTICES regeneration at the cut** (std-55b Q1): regenerate with `cargo about` at the v0.53.0 cut and read the 146-line move (workspace versions, reordered licence blocks); the `vilan-rt-term` Covers entry was added by hand.
3. **The kolt bump at the seal** (solver-55 Q1): kolt's warm package check is +0.24 % instructions under the lane (B646 +0.11 %); add the kolt `[[bump]]` row at the seal. Also the seal's base is a clone COPY of the owner's working tree (seal-55.sh), now with N175's no-default `VILAN_PERF_KOLT_COMMIT`, and the E292 series needs its re-anchor (E340) before the series is meaningful again.
4. **Kolt patch notes for the owner** (kolt is the owner's; no lane edited it): REQUIRED for 0.53.0 - M171 (delete `default_prevented` + `stop_propagation` from `impl Event` in `src/lib/std_ext.vl`; patch `std-55/kolt-m171-std_ext.patch`; this is the `lib/std_ext.vl:38` comment line) and M164 (`src/files.vl:235`: `request.max_body_bytes(max_upload_bytes.as_usize()).bytes()`; optionally `src/mcp.vl:109`). Expected warnings until applied: B677 at `src/panels.vl:922` and `:2068` (type `page: (sync |str| View) context (owner_scope, page_focus)` at `:781`, also `:824`, `:945`, `:1834`). One formatter reflow: `src/task_table.vl:429` (E338). Optional adoptions: M170 (`ui::nothing()` for the 41 `styles::nothing()` uses, `ui::each_owned` for three effect-only rows; the `styles.vl:147` comment line), M166 (`lib/rich_text/style.vl:14` comment line; the hand-written `TextStyle` FromJson stays until M174), M167, M169, M165 (`done then 1 else 0` at store.vl:2446/2876/3491/4493), M168 (`.host("127.0.0.1")`), B654 (triple-quoted externs at dictionary.vl:17, std_ext.vl:105, reactions.vl:52), B652 (document_test.vl workaround comment), A174 (`close_connection(self.connection, "signed out")` for sign-out and member removal), B659 / B667 / B670 (workarounds become optional).
5. **B657 part 1 (the `..base` diagnostic)** was named for parser-55 in the brief but was not built; stamped on B657 as an Order 56 candidate. Rec: put it in Order 56's parser lane (S).
6. **E334 stamped, not closed:** the gate still asserts nothing (the exhibit/kolt size mismatch, E343). If the owner prefers E334 closed with E343 carrying the remainder, move it into the closes.

## Post-order lanes (2026-10-31): fmt-e352 and std-a178

fmt-e352 (E352 + E353, shipped v0.53.1):
1. The 18-file kolt reflow under E352's evened-out rule - PROCEEDED on the lane's rec (the rule applied evenly; the patch in fmt-e352/kolt-e352-vs-written.diff).
2. The `--check` skip listing on stdout beside `would reformat` - as built (rec yes).
3. Follow-ups, unfiled until you want them: an attribute form `[fmt(skip)]`; a region form (`off`/`on`); skipping a top-level import inside the sorted block; the then-form CONDITION line still has no width permission (the arms do now).

std-a178 (A178 S1 + S2, merged to next for v0.54.0):
4. Should `Style::raw` pick the role from the property NAME, so a css block's undotted `border(dp(1), ..)` writes `1px` as the dotted `.border(..)` chain does? Today the block's `border(..)` goes through `raw`/`piece` and writes `0.0625rem`. Lane rec: yes (the multi-argument `piece` path would need the lowering to pass the property). Integrator rec: yes, as a Order 56 std slice - a hole and a chain must not disagree on a hairline.
5. Should the role-taking `with_length_as` come back now that fmt-e352 has landed? It needs a `STYLE_BARRIER_METHODS` row in formatter.rs (the lane dropped it to stay out of the fmt lane's file). Rec: yes, with (4).
6. `PartialOrd` bridges px/rem/dp but `==` is structural: `px(16) <= rem(1)` and `>=` are both true while `!=` also holds. Lane rec: keep as the paper has it and settle when `Ord` comes. Integrator rec: agree; note it in the docs.
7. The codemod left four sites for you: `avatar_gap` (used inside a sum), `views.vl:323`, and `sidebar.vl:127-128` `.border_left/right(rem(2/16))` where `dp(2)` would render `2px` under the border role (today `0.125rem`). Rec: take `dp(2)` there - a hairline in px is the point of the role.
8. Two finds filed: B690 (JS miscompile: a module `const let` read only through operator dispatch is never declared) and F154 (native: a str-backed enum's `.value()` at run time does not compile). B690 is a miscompile - rec Order 56's first solver/emitter item.

b689 (B689 + M182, merged to next 26257f20 for v0.54.0; design + as-built in proposal/hash-map-lend.md):
9. Names: `peek` (the in-place read, after `ListCell::peek`/`HashMapCell::peek`), `modify` (the in-place write of the `Option` slot) and `update` (M182's word; the value-level grouping form). Rename at review if `modify` beside `update` reads wrong - a one-line codemod.
10. `update(key, lazy missing: V, change)` over M182's `|| V`: `lazy` is the ratified spelling for "evaluated only on the miss" (`unwrap_or`, `expect`). Say if `|| V` is wanted.
11. `HashMap` is two `NativeMap` tables (keys + values) rather than one table of pairs: the price of a real `&Option<V>` place without unsafe in vilan-rt (§2 of the paper weighs the always-`Some` wrapper and a two-parameter NativeMap). A second index per map; every write touches both inside one method.
12. B691 (JS MISCOMPILE, found on the way): an enum value is never copied at a value seam - `mut b = a` of an `Option<List<i32>>` aliases `a`'s payload. It is why `get`/`get_or_insert` kept the table's own `get` rather than `peek`. Order 56 head with B690/B688?

b693 (B693, merged to next 2f89bee9 for v0.54.0; design + as-built in proposal/store-assume-keeper.md):
13. The keeper's life outside any owner: `assume()` at the top of `main` (the existing A142 S7 pin's shape) stands its keeper on the store for the store's life - `register_with_owner`'s leak-as-today rule, as the paper recommends. The stronger law (refuse `assume()` outside an owner, a COMPILE error as `on_cleanup` has) is A130's conversation. Say if you want the refusal.
14. The restated rule: "a reader in the turn that ends the variant reads the payload AS IT STOOD WHEN THE VARIANT ENDED" (docs + CHANGELOG), in place of "the LAST payload a read through the live variant saw". Never older; ratify or revert the wording (the mechanism satisfies both).
15. B694 (the lane's find): the server `ui` twin's one-shot owners (`when`, `when_live`, `swap`, `each` rows, `when_some`) are never disposed, so a server that SSRs pages over a long-lived store accumulates a keeper per render (and already accumulated every subscription a body made). Kolt's server renders no views today. Rec: dispose each owner right after its body placed its view (S); Order 56 std lane.

m185 (M185, merged to next 8e8c463c for v0.54.0; design + as-built in proposal/image.md; the lane built Q1-Q5 on the recs):
16. The wasm blob COMMITTED (`crates/vilan-image-wasm/vilan_image.wasm`, ~1 MB, rebuilt by `scripts/build-image-wasm.sh`, checked by CI's wasm leg) rather than built inside `cargo build` by a build.rs on every machine. Rec: commit.
17. WebP encoding is LOSSLESS only (the `image` crate's pure-Rust encoder; lossy means libwebp in C on both hosts); `quality` ignored for WebP and documented. Rec: accept; JPEG for photos.
18. Synchronous decode/encode only (a 12 MP JPEG is ~100-200 ms of the event loop on node, a tenth natively); a worker-backed `decode_async` is a follow-up item. Rec: accept for the avatar case.
19. JPEG has no alpha: a transparent picture is flattened onto WHITE on encode (the crate's default drops to black). Rec: white.
20. The default decode pixel limit: 50,000,000 (`decode` = `decode_within(bytes, 50_000_000)`; a 12 MP photo decodes, a 60,000-square bomb is refused from the header). Rec: 50 MP.
21. The web playground's compiler (vilan-wasm) is built WITHOUT the codec (vilan-core's `image-codec` feature; the artifact would grow 9 %, 7.58 -> 8.35 MB, for a `@process` module the browser never runs), so a playground program that reaches `std::image` is refused by a sentence naming the feature and the CLI. The alternative is a lazily fetched blob beside the playground's wasm. Rec: the refusal; file the lazy blob only if someone asks.
22. `resized`'s 50,000,000-pixel RESULT cap is a PANIC at the caller (`[track_caller]`: the box is the program's choice, a bug to fix), where `decode`'s pixel limit is an `Err` (the upload's claim, to handle). Ratify the split or make both `Err` (a one-line change in image.vl; the seam already carries it as `Err`).

post-order sync (2026-11-02 evening):
23. Your M186 (cut_row's live DOM Range per row; the Table page's 8.5 s leave) collided with lane b693's M186 (the path-list copies), filed on main the same day and already designed + in a lane; your item is M187 on main (its text unchanged but the status line). If you had M186 noted anywhere, read M187. Rec: M187 is the next std::ui item (S, browser) - queue it with M187's own lane after the five in flight.
24. B677 door 2: your "do B677" is read as the closure-owner.md ruling AS RECOMMENDED (View + impl Slot, sync implied, no opt-out spelling; the door-1 warning's View half removed). Say if you meant the lint door only.
25. A179: built as dial-cancel.md recommends - the dial honours the ambient CancelSignal (`RpcError::Cancelled`), and `std::rpc::dial_within(ms, dial)` is a free function over any dial answering `RpcError::Timeout` (no generated `connect_with_timeout`). Two new RpcError arms: an exhaustive match in kolt gains two (the lane lists any).
26. M181: `std::url::{percent_encode, percent_decode}` as a module (not str methods); the router re-exports the decoder. Kolt's `src/lib/std_ext.vl` pair can go under 0.54.0.
27. M181's decoder is TOTAL per `%XX` RUN now (the native implementation's rule; byte-identical on both backends): `"%zz%20"` decodes to `"%zz "` where `std::web::router::percent_decode`'s old whole-text fallback kept it as written; a run that is not valid UTF-8 as a whole (`%41%FF`) stays as written. Kolt's own `decode_uri_component` extern is the old whole-text form - the two differ only on a text mixing a malformed escape with a good one. Rec: accept; drop kolt's two externs under 0.54.0.
28. B695 (std-56's find): `"😀".substring(0, 1)` is half a surrogate pair on JS and the whole emoji natively (`len()` 2 on both). A spec call: which backend is right at a surrogate boundary. Rec: the code-point rounding on both (the half is unrepresentable natively); then pin every UTF-16-indexed `str` operation on the differential.
29. A179: the cancel arms are JS-only because the native backend has no WebSocket dial (F1 S1b); `dial_within` works natively over any dial. Nothing to rule; noted so the native client's dial (when F1 S1b lands) inherits the same two arms.
30. E121 TARGETS for the new series (N186; the exhibit is your current kolt @2684c70, three times the Order 54 one). Lane incr-56's base-vs-base figures (instructions; quiet CPU estimated at ~135 ms/G from the Order 54/55 quiet seals) and its proposed targets (~1.1x quiet, to be re-taken at a quiet seal): leaf keystroke 10.01 G ~1350 ms -> 1500; shared.vl 1.60 G ~215 -> keep 500; model.vl 3.90 G ~525 -> 600; importers open 20.28 G ~2740 -> 3000; css 8.85 G ~1195 -> 1300; parse break 16.97 G ~2290 -> 2500. The 500 ms mandate stays the ARC's goal for leaf/css/parse break (E121's words are yours; the number per exhibit is a ruling). The e121 state was reset (all six rows green_seals 0, blocking -> reporting; the old state kept beside it). Rec: take the proposed numbers as the series' first targets with `mandate` kept on the three, re-taken at the Order 56 seal on a quiet box.
31. N186 (3): the next seal script needs `VILAN_PERF_KOLT_DIR=$HOME/.vilan/perf-exhibit/order56/kolt` and `VILAN_PERF_KOLT_COMMIT=2684c70` (no VILAN_PERF_TIP_KOLT unless the release is breaking). Say if the exhibit should be a newer commit of your tree.
32. B688 is BREAKING for kolt: 86 sites in 34 files need an import naming the block's module (the full list in kolt-patch-notes55; `app_overlay`'s menu/modal are 64 of them). Alternatives you could rule instead: (a) keep the fix and patch kolt (rec - the rule the diagnostic always stated; a build then agrees with `vilan test`); (b) widen the exemption to blocks in the PACKAGE's own modules (kolt's app_overlay/styles would resolve everywhere as before; std's `join` would still need Display) - loses the per-file promise inside a package; (c) a `vilan fix`-style codemod that adds the named imports (S; the quick-fix data exists per site).
33. E359 (solver-56's find): B688's quick-fix steers to the module's first export (`import pkg::styles::search_mark_style;`) - say if a selector-only import form for a block exists or should (`import pkg::styles::{ (impl Style) }`), else the message will say any name from the module serves.

## Rulings 2026-11-03 (the owner, on Qs 1-33)

- RULED as recommended: Q1-Q2, Q4-Q7, Q8 + Q12 (B690/B691 head Order 56's solver lane), Q10 (`lazy`), Q14, Q15 (B694 -> Order 56 std lane), Q16-Q18, Q20-Q21, Q23 (M187 -> its own std::ui lane), Q27, Q28 (B695: code-point rounding on both backends; then pin every UTF-16-indexed str operation), Q32 (keep B688; kolt patched - see below).
- Q19 RULED "follow the most established standard": the programmatic standard is BLACK (a browser canvas's `toDataURL('image/jpeg')`, sharp/libvips, Rust's `image` crate all composite a transparent JPEG onto black); white is the print/export convention (ImageMagick's default `-background`, Photoshop's matte). -> JPEG alpha flattens onto BLACK; with Q22 (`resized` answers `Result`, as `decode` does) = one image follow-up item (lane: std).
- Q13 RULED: refuse `assume()` outside an owner at compile time (as `on_cleanup`'s contract) - `assume` carries `context owner_scope`; the A142 S7 top-of-main pin moves inside an owner; estate census. A new B item for a std/solver lane.
- Q31: the exhibit is kolt's NEWEST commit, 0de9e2e (vilan-migration, 2026-11-02, two past 2684c70); the clone at ~/.vilan/perf-exhibit/order56/kolt is on it (lucide + search-dict carried). v0.54.0 is BREAKING (B688), so the seal's tip side needs the B688 imports: the owner's commit of today's patch becomes the one exhibit for both sides once it exists; until then VILAN_PERF_KOLT_COMMIT=0de9e2e for the base and VILAN_PERF_TIP_KOLT = the same tree + the patch. The series' first figures (Q30) were taken at 2684c70 and are re-taken on the chosen commit at the Order 56 seal.
- Q30 answered in the reply (the 500 ms mandate vs 1,350 ms on this exhibit): not unrealistic as the ARC's goal, unreachable by one order; interim per-exhibit targets as proposed.
- Q33 answered + RULED by the facts: the impl selector exists (`import pkg::styles::{ (impl Style) };`, spec names.md), but the subject must resolve in the importing file's scope and a selector SET admits only what it names - the honest steer is the plain module import kolt already uses (`import pkg::styles;`, like its `import pkg::model;`), which admits every impl on the path. E359's fix: steer to `import {module_path};`.
- Q9 / Q11 / Q24: questions back to the owner in the reply (an `entry()` facade and `update`'s name; the two-table map's cost and the two-parameter NativeMap; generalizing door 2 beyond View).
- Q32 DONE: kolt's working tree at 0de9e2e carries the 37 import lines in 34 files UNCOMMITTED (solver-56/kolt-b688-imports.patch): `import pkg::app_overlay;` (the module form), `import pkg::styles;`, `import std::display::Display;`, `import std::hash_set::HashSet;` - a copy checks clean under next (0 diagnostics); the owner commits. Two forms tried first and dropped: `(impl Overlay)` (the subject must be in scope) and `(impl _)` (a selector set declined impls a plain import admitted - six `prevent_default` errors appeared).
- Q31/Q32 2026-11-03 ~15:30: the owner's word 'You commit it' - the B688 import patch is COMMITTED on kolt's vilan-migration as 3fb5d74 (not pushed; 34 files, +37). That commit is the ONE exhibit for both seal sides: `VILAN_PERF_KOLT_COMMIT=3fb5d74`, no VILAN_PERF_TIP_KOLT; the clone at ~/.vilan/perf-exhibit/order56/kolt is on it.
- Q9 + Q11 RULED 2026-11-03 (rec accepted, one slice): M191 - `HashMap` on one table (the two-parameter NativeMap, tombstones on both backends) and the entry idiom on it (`slot(key)` borrows self + `Option::get_or_insert`); `update` goes. Order 56 std lane after a short paper slice (hash-map-lend.md §9).
- Q30 RULED 2026-11-03 (rec accepted): the interim targets on the [[e121]] rows (leaf 1500, model 600, importers 3000, css 1300, parse break 2500, shared 500; mandate kept on the three); E121 stamped. Open: Q24 only.
- Q24 RULED 2026-11-03 (rec accepted with a reservation): door 2 generalizes to a MARKER TRAIT on the result type (owner-registered-on-creation types) - A180, paper slice (closure-owner.md §7) then Order 56's solver lane. ALL post-order questions 1-33 are now ruled.
- 2026-11-03 ~18:00 the owner on the impl-selector problems: part A option 4 (absolute-path subjects) RULED -> A181 (with the bare `m::(impl T)` form and absolute paths in every subject position); part B 'B1-leaf' RULED -> A182 (a plain import admits the leaf's blocks only; directory bodies via prelude/explicit import; the package prelude blessed). E359 rides A181.
34. Your E357 (a path through an imported FUNCTION reports only the 'could not be resolved' cascade, never the cause) collided with parser-56's E357 (lone-file fmt); yours is E360 on main. Your E356 note (5c8a5fc1: `[must_use]` exists; infer it for own-self builders) arrived after E356 was CLOSED exactly that way (solver-56: the builder shape inferred from the declaration, `[must_use]`'s severity) - nothing to do. Rec for E360: Order 56's solver lane beside B690/B691 (a diagnostics item: name the cause at the path's head).

