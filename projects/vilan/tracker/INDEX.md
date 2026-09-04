# Vilan tracker — open items

`backlog <ID>` resolves to `items/<ID>.md` if open, or a tombstone in `archive.md` (or the frozen chain it points at) if closed — see `proposal/tracker-migration.md` §2.

## A. Reactive core & UI (`std::reactive`, `std::ui`)

| ID | Title | Kind | Discussion |
|----|-------|------|------------|
| [A7](items/A7.md) | SSR tail | design | |
| [A8](items/A8.md) | UI styling — the tail | design | |
| [A14](items/A14.md) | Reactive residuals | design | |
| [A34](items/A34.md) | NEW — a typed style token has no mid-value spelling in a css block | design | b148's census find; real gap revealed |
| [A36](items/A36.md) | NEW — `Style::when(condition, delta)` conditional-merge combinator | feature | RULED ACCEPTED 2026-08-31 (style-variants Q3); ready to queue |
| [A37](items/A37.md) | NEW — `[gone]` trait-member attribute: reachable only through the trait (method surface, for blanket impls) | design discussion | NOT queued; the owner unsure of its value |
| [A38](items/A38.md) | NEW — the rpc service is one process-wide instance; transport-rpc Q9 says the instance IS the connection's session (per-connection factory + injected globals) | design | owner's ask (kolt); a paper-vs-implementation gap; prerequisite of A39 and A40 |
| [A39](items/A39.md) | NEW — `[expose]` resyncs the whole value on every change; a message edit costs the channel (keyed deltas + per-key subscription over the wire) | design | owner's ask (kolt); a recipe exists today but stops at the generated client; needs A38 first |
| [A40](items/A40.md) | NEW — the rpc WebSocket upgrade authorizes nothing and never echoes a subprotocol; a pre-upgrade `authorize` hook + a token subprotocol (transport-rpc Q4's transport half) | design | owner's ask (kolt); DoS surface; auth mechanism stays dev-land; needs A38 for the Session to live in |
| [A41](items/A41.md) | NEW — the dynamic-expose path leaks and goes dead: `ReactiveServer::stop` never removes the `sources` entry; `reattach_mirrors` rebinds only `__attach`'s positional list | bug | rpc triage lane's find while writing A39's recipe |
| [A42](items/A42.md) | NEW — `bind_each` demands both `T: PartialEq` AND a key fn; split the value-keyed and key-fn forms (kolt writes the key twice and gets a stale row) | design | owner's ask (kolt); additive, no rename; M |
| [A43](items/A43.md) | NEW — `Source` has no lazy subscribe: land the `observe`-shaped member (`on_change`) that reactive-traits Q5 owes, rather than flipping `sub`/`effect` | design | owner's ask (kolt: eager is often not wanted); OWNER DECISION flip vs additive; S; unblocks A44 and `Source::map` widening |
| [A44](items/A44.md) | NEW — `Source::selector()`: O(2) per-key selection notification (Solid's `createSelector`); the owner's `sub_condition` is O(n) and lands inside the notify loop | feature | owner's idea (kolt); needs A43's `on_change`; M |
| [A45](items/A45.md) | NEW — no element mount hook: `View::on_mount(\|el\| ..)` and `View::autofocus()`; kolt focuses three modal inputs with three UUIDs, three timers and a private `focus` extern | feature | owner's ask (kolt); S; SSR twin no-op |
| [A46](items/A46.md) | NEW — fragment syntax `<>..</>` lowering to a `List<View>` literal (reverses element-syntax.md §7's refusal); NOT a multi-root View | feature | owner's ask (kolt); S–M for the list lowering, L for a marker-node fragment; owner to say which |

## B. Type system & the type solver

| ID | Title | Kind | Discussion |
|----|-------|------|------------|
| [B3](items/B3.md) | Variadic-generics tail | feature | |
| [B11](items/B11.md) | `!` / `?.` tail | design | |
| [B146](items/B146.md) | NEW — the context coverage check's refinement consumes node-owned dispatch sites only | feature | |
| [B147](items/B147.md) | NEW — a module/file-level default for `[platform(...)]` | design | |
| [B149](items/B149.md) | NEW — an async function returning a `Task` mistypes as the task | bug | the pin names it since Order 21; the gap itself stays open |
| [B183](items/B183.md) | NEW — tuple comprehension `(item in tuple => EXP)` + the zip form | design | owner-proposed |
| [B184](items/B184.md) | NEW — trait annotations on struct fields, one-instantiation rule | design | owner-proposed; discussion REQUIRED |
| [B213](items/B213.md) | NEW — `vilan fmt` walks once per root; overlapping roots double-report a file | bug | watch-26's find |
| [B216](items/B216.md) | NEW — a parameterized supertrait clause loses `Self` in a default body (B205's gate) | bug | cascade-26's find |
| [B217](items/B217.md) | NEW — generated-code type misses via the `prepped_*` route are not anchored at the derive | bug | cascade-26's find |
| [B218](items/B218.md) | NEW — two implicit generics of one trait print the same name: `Expected X, but got X` (Q3's diagnostic face) | bug | b211-b212's find |
| [B219](items/B219.md) | NEW — `compare_type_rigid` does not consult `rigid_binder_scope`; the documented twins disagree | bug | b211-b212's find |
| [B220](items/B220.md) | NEW — an array receiver has B210's emission-side hole (`resolve_member_on_type` excludes arrays) | bug | b209-b210's find; a decision |
| [B221](items/B221.md) | NEW — a diverging non-last statement does not exempt the return tail (B124's list) | bug | b204's find; pre-existing |
| [B222](items/B222.md) | NEW — a panicking guard does not bind the continuation: B187 decides during the walk, B204's leaves settle after | bug | found at integration; pin ignored naming it |
| [B223](items/B223.md) | NEW — `for` conditions and `match` guards have no polarity frame; a negated capture binds where an `if` refuses | bug | b214-b215's find; refuses programs that compile today |
| [B224](items/B224.md) | NEW — a condition's `&&`/`\|\|` short-circuit is lost in codegen: the right operand's statements hoist before the `if`; an `else if` condition hoists above its whole chain | bug | owner's find (kolt); RELEASED MISCOMPILE; crashes on the miss path, side effects run when short-circuited |
| [B225](items/B225.md) | NEW — the struct-literal door reopens the enclosing impl's OWN rigid parameter: `impl Pair<type T> { fun make(x: T) { Pair { b = "s", a = x } } }` silently returns `Pair<str>` (B219's first live consequence) | bug | owner's find (kolt's `impl Searchable<type T>`); UNSOUND ACCEPT; M with a census — B211 shipped the door deliberately |
| [B226](items/B226.md) | NEW — a self-import (or a cycle back) into the ENTRY module makes it load as a module and skips its walk and derive expansion: `main` and every `[derive]` vanish | bug | owner's find (kolt: 'SidebarTab does not implement PartialEq' in views.vl, fine in a new file); S–M; no self-import or cycle detection exists |
| [B227](items/B227.md) | NEW — an `any` parameter FILLS an unfilled closure parameter instead of coercing: one `print(x)` types `x` as `any` and silences every later check on it (`on:keydown(\|event\| ..)`'s `event: any` is this) | bug | owner's two finds (kolt) are one defect; S — add `Type::Any` to B13's adopt guard, skip without deferring |
| [B228](items/B228.md) | NEW — a ZERO-argument method call anchors its arity diagnostic on the DECLARATION, so a std callee's error renders against std's file at the caller's offsets (`<div .styled() />` looks undiagnosed) | bug | owner's find (kolt); S — `MethodArgCheck` already carries `call_id` |
| [B229](items/B229.md) | NEW — an unresolved value argument silently deletes the `run` site: every context read then fences, burying the real initializer error; and the 'flows through this call' note spans the whole receiver chain | bug | owner's find (kolt: 'context threading breaks fairly often'); (b) M, (a) S; B146's sibling gap |
| [B230](items/B230.md) | NEW — `?` inside a `let` initializer double-wraps: `let v = probe()? > 0; Ok(v)` returns `Ok(Ok(true))` and an `Err` becomes `Ok(Err(..))`, never propagated (RELEASED MISCOMPILE) | bug | lane b224's find (2026-09-04); independent of B224 — the `?`-lift restructures above the expression; same-day lane b230 |
| [B231](items/B231.md) | NEW — a `match` expression as a binary operand (`flag && match probe() { .. }`) is a parse error: `found 'else' expected an expression` | bug | lane b224's find (2026-09-04); pre-existing parser limit |

## C. Memory model

| ID | Title | Kind | Discussion |
|----|-------|------|------------|
| [C1](items/C1.md) | `Weak<T>` | design | |
| [C2](items/C2.md) | Dynamic rule-4 remainder | design | |
| [C13](items/C13.md) | a closure over a view parameter escapes through a storing callee | bug | pinned ignored; spec §6.9's honesty limit |

## D. Documentation

| ID | Title | Kind | Discussion |
|----|-------|------|------------|
| [D5](items/D5.md) | Public traction plan | design | |

## E. LSP & tooling

| ID | Title | Kind | Discussion |
|----|-------|------|------------|
| [E37](items/E37.md) | bindgen v2 — the remainder | feature | |
| [E62](items/E62.md) | NEW — Zed language extension | feature | |
| [E69](items/E69.md) | NEW — attribute-NAME completion in an element head is a semantics decision | feature | |
| [E99](items/E99.md) | NEW — the `-d` dump's `.parse.out` is the post-desugar tree, and no dump shows the raw parse | process | |
| [E106](items/E106.md) | NEW — the language server slows down over a session | bug | owner report; measure first |
| [E121](items/E121.md) | NEW — the editor-latency mandate: <10 ms keystroke path, <500 ms errors | design | owner-set target; ARC, paper first |
| [E124](items/E124.md) | RULED 2026-09-03 — no visibility markers: a `[package]`'s top-level dead code = unreached by ANY entry (the pruner's definition unioned across entries); libraries no top-level gray; `[doc(hidden)]` the soft surface; `[keep]` reserved | editor | PAPER first, then build — an upcoming order |
| [E126](items/E126.md) | NEW — the diagnostics gate's exhibit misses kolt's cost 178× on call substitutions; needs a view-shaped generator | editor | m19-paper's find; M19-t1 gate prerequisite |
| [E127](items/E127.md) | NEW — no `did_change_watched_files` handler; disk-read module listings stale until re-analysis | editor | m25-e125's find |
| [E128](items/E128.md) | NEW — hover renders `= Self` as the trait's name | editor | cascade-26's find; B206's other half |
| [E129](items/E129.md) | NEW — a code `::`-path completes only its LAST segment: `style::FlexDirection::` and `style::Color::` offer nothing | editor | owner's find (kolt); the import arm already descends; S–M |
| [E130](items/E130.md) | NEW — member completion is blind on a call whose DECLARED return is a type parameter: `SignalCell<T>::get()`'s `.` offers nothing (E107's other half) | editor | owner's find (kolt); S, substitute through `method_call_substitution` |
| [E131](items/E131.md) | NEW — member completion resolves a CALL receiver in ANALYZED coordinates: a receiver typed since the landing answers the OLD expression's type (`<div .styled(const style::style().` offers View's members) | editor | owner's find (kolt); E125's twin for completion; S gate now, M with M29 |
| [E132](items/E132.md) | NEW — linkedEditingRange answers in ANALYZED coordinates; the client mirrors keystrokes into unrelated live text (E125's twin; CORRUPTS working code) | bug | owner's find (kolt): 'unrelated text deleted or changed'; fix verified S (564/564); interim: editor.linkedEditing off |
| [E133](items/E133.md) | NEW — the reference index is end-exclusive: rename and find-references miss with the caret at `name\|` | bug | owner's find (kolt); fix verified S (564/564); hover has the same rule separately |
| [E134](items/E134.md) | NEW — a struct-init shorthand's two references share one span; the index dedup drops the variable's use (unused-local fade + find-references), and rename at that span serves only one name | bug | owner's find (kolt); one root cause for both halves; M — a design decision, not the one-line widen |
| [E135](items/E135.md) | NEW — an incomplete `a::` path rolls the `::` back: the failure surfaces as a missing `;`, or the path re-binds to the NEXT line's identifier and swallows that statement | bug | owner's find (kolt: broke element parsing); S — the `Length::css` arm is the model |
| [E136](items/E136.md) | NEW — a multi-value element attribute declines the WHOLE element; its curated diagnostic is discarded and the span lands on the tag | bug | owner's find (kolt: `<div raw("inert", x) ..>`); S — mirror the `.`-chain arm |
| [E137](items/E137.md) | NEW — the formatter never breaks a ONE-link chain: a single `.map(closure)` stays inline at any width (220 columns) | bug | owner's find (kolt); M — small change, golden churn over the byte-gated corpus |

## G. Macros & const

| ID | Title | Kind | Discussion |
|----|-------|------|------------|
| [G2](items/G2.md) | Const-eval tail | feature | |
| [G9](items/G9.md) | NEW — a workspace member's own `[build] run` never runs, and nothing says so | design | |
| [G12](items/G12.md) | NEW — `read_dir_all` fuel charged on the result, not the walk | design | audit 4; the basis is the question |

## I. Collections

| ID | Title | Kind | Discussion |
|----|-------|------|------------|
| [I2](items/I2.md) | Fixed-arrays tail | design | |
| [I3](items/I3.md) | Iterator adapters — the remainder | feature | |

## J. Concurrency

| ID | Title | Kind | Discussion |
|----|-------|------|------------|
| [J4](items/J4.md) | Free-spawn lint | design | |
| [J5](items/J5.md) | Async recorded opens — the deferred pair | feature | |

## K. Web presence (site, playground, docs delivery) — NEW SECTION

| ID | Title | Kind | Discussion |
|----|-------|------|------------|
| [K5](items/K5.md) | The design language — adopt | feature | |
| [K8](items/K8.md) | Website features & small visual upgrades | feature | |
| [K13](items/K13.md) | NEW — the docs on the vilan framework, the port proper — behind its markdown prerequisite | feature | |
| [K14](items/K14.md) | NEW — the playground's buffers carry no prelude; examples teach the old spelling | design | v0.40.0 deploy's find; OWNER QUESTION |

## L. Release engineering & beta — NEW SECTION

| ID | Title | Kind | Discussion |
|----|-------|------|------------|
| [L3](items/L3.md) | std tier sweep | design | |
| [L8](items/L8.md) | Contribution scaffolding | design | |
| [L15](items/L15.md) | NEW — release artifacts are checksummed but unsigned | feature | |
| [L16](items/L16.md) | NEW — `std::markdown`'s ~20 strict-parse refusals enter the diagnostics ledger | process | |
| [L18](items/L18.md) | NEW — the pages repo is the one repo in the fleet with unpinned workflow actions | process | |

## M. Performance & footprint — NEW SECTION

| ID | Title | Kind | Discussion |
|----|-------|------|------------|
| [M10](items/M10.md) | NEW — mechanize the BASE_CACHE transmute's completeness claim | perf | |
| [M12](items/M12.md) | NEW — the corpus leak-soak passes in 0.005 s asserting nothing when its corpora are absent | perf | |
| [M17](items/M17.md) | NEW — cross-subject body sharing, M16's residual | perf | separate decision |
| [M18](items/M18.md) | NEW — a function attribute marking a bundle boundary | design | owner-proposed; lucide the exhibit |
| [M19](items/M19.md) | NEW — an unchanged package module is re-analyzed every LSP analysis / HMR round | perf | E106's prime hypothesis; lucide's 636 KB |
| [M27](items/M27.md) | NEW — `lsp-index` editor tables 110–584 ms per keystroke, outside analyze and every tranche | performance | m19-paper's find |
| [M28](items/M28.md) | NEW — `plan_resource_drops` 350–600 ms, whole-program switch on any resource type | performance | m19-paper's find; Q4 |
| [M29](items/M29.md) | NEW — completion tranche 3: whole-buffer tokenize/parse per request; member completion 2.63 ms | performance | m25-e125's finds |

## N. Hygiene & rot — NEW SECTION

| ID | Title | Kind | Discussion |
|----|-------|------|------------|
| [N16](items/N16.md) | NEW — the recurring codebase audit | process | |
| [N20](items/N20.md) | NEW — `.claude/` is live configuration that no gate can see, and it had three dead pointers in it | process | |
| [N23](items/N23.md) | NEW — 37 `pub` items in `vilan-core` are never referenced outside their own file | process | |
| [N35](items/N35.md) | NEW — `hmr_css_matrix` reads the bundle while the watcher writes it | bug | load-dependent race, seen once |
| [N47](items/N47.md) | NEW — an output-asserting docs form (`vilan,run` + transcript) | process | docs-law's proposal |
| [N51](items/N51.md) | NEW — `watch.vl` never terminates; the corpus's rule for non-terminating programs | hygiene | hygiene-26's find; OWNER'S QUESTION |
| [N52](items/N52.md) | NEW — `infer_differential.rs` has the pre-N49 single-test shape; split it, share the list | hygiene | hygiene-26's find |
