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
