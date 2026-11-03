# Closure parameters and the owner they build under (B677, door 2)

Status: **BUILT 2026-11-03 (lane solver-56 05f25ec2 + 211e6259; merged to next; rides v0.54.0, BREAKING; B677 closed) — RULED 2026-11-02 as §5 recommends (the owner's "do B677")** — originally a QUESTION for the owner, Order 56 — written by rpc-55 (Order 55,
2026-10-26) as B677's paper half (R-b: door 1, the warning, shipped in Order 55;
door 2, this page, not built). One recommendation at the end.

## 1. The question

Should a closure PARAMETER whose result is `View` (or that builds effects)
default to the **call-time** ambient owner, rather than the owner it was
**made** with?

Today a closure captures its context at creation (spec §8.4), and a `context`
clause on the closure's TYPE is the one thing that defers a context to the call
(§8.5). `owner_scope` is a context like any other, so:

```vilan
fun with_org(slug: str, body: |OrgSummary, RemoteStore<OrgState>| View): View {
	<div>{when_loaded(root, |me| swap(org_of(me, slug), |org| body(org, store)))}</div>
}
```

builds whatever `body` builds — every effect, every store hold — under the
owner the CALLER of `with_org` was made with, not under the `swap` instance
that called it. The `swap`'s owner releases what the swap body registered;
`body`'s registrations went elsewhere. Nothing is released when the branch
re-instantiates (a reconnect, a navigation), and everything goes at once when
the creation owner finally goes — through M172's release, 12 s for 30 hovers.

The fix is one clause: `body: (sync |…| View) context owner_scope`. Then
`body` takes the owner at the call, and the program is right. The question is
whether the language should make that the default for the parameters where
"builds under the owner" is what the result type already says.

## 2. The exhibit: kolt's wrappers

Kolt at b04095a (2026-10-24) had typed six wrappers with the clause after
B677's filing — each one a parameter that had been plain and had leaked:

| site | parameter | what it built under the wrong owner |
| --- | --- | --- |
| `org_pages.vl:132` `with_org` | `body: (sync \|OrgSummary, RemoteStore<OrgState>\| View) context owner_scope` | the organization's whole page: every hold on the org store |
| `states.vl:119` `when_loaded` | `render: (sync \|RemoteStore<P>\| View) context owner_scope` | the view over an arrived store |
| `settings.vl:832` `with_account` | `body: (sync \|RemoteStore<AccountState>\| View) context owner_scope` | the account page |
| `panels.vl:1674` the picker | `probes: (sync \|SignalCell<List<(K, str)>>\| View) context owner_scope` | a store hold per listed name, per opening (the 12 s) |
| `panels.vl:1670` the picker | `glyph: (sync \|\| View) context owner_scope` | an icon view per opening |
| `lib/overlay.vl:588` `Overlay::attach` | `body: (sync \|\| View) context owner_scope` | an overlay's content |

A seventh is still plain, and the Order 55 warning finds it (door 1's nested
rule): `panels.vl:781` `panels_view(panels, page: (|str| View) context page_focus)`,
called at `:922` and `:2068` as `focused_page(.., || page(now))` inside a `swap`.
The clause names `page_focus`, so `page_focus` is injected — and `owner_scope`
is captured, exactly as a bare `|str| View` would capture it (probed:
`rpc-55/finds/b677_mixed_clause.vl` prints `-a`/`-b` only at the root's
dispose). `page` is the literal `|path| page_for(..)` made at `views.vl:202`,
under the app root. Every page kolt navigates to is therefore built under the
app root and released only when the app root goes. Patch note for the owner:
`page: (sync |str| View) context (owner_scope, page_focus)` at `:781`, `:824`,
`:945`, `:1834`.

Seven of seven are `View`-returning. None wanted the creation owner.

## 3. What breaks

A caller that RELIED on the creation owner. Under door 2 a `|…| View`
parameter would build under the body that calls it; a program that passed a
view-building closure into a helper and meant its registrations to belong to
the caller's scope — "build this once, keep it while I live, whichever body
shows it" — would see them released with the showing body instead.

Counted in the estate (kolt at b04095a, the website, the eleven examples, the
corpus, the native tests; the Order 55 warning, which fires on exactly the
sites door 2 would change): **0 user sites** that call a plain `|…| View`
parameter inside an owner body, kolt's `page` excepted (which wants the call
owner). The one site in std is `MaybeSignal::bind(react: |T| void)` — a
`void` reaction, outside door 2's `View` rule, and gated out of the warning as
library code.

So the breaking set, today, is empty. That is the strongest argument for door
2 and also its weakest: an estate of two apps proves little about the shape a
third one will want.

What ALSO changes under door 2, and is not a break: a `|…| View` parameter
becomes an injected closure, with §8.5's restrictions — it can be called,
forwarded to a same-clause position, or passed to `run`; it cannot be stored
in a plain field or a `List` (B324's rule: a literal written into an external
aggregate is born clause-less). A component that keeps a `List<|| View>` of
builders would have to type the element with the clause, which B309 lets it
do. The sync marker rides too: `(sync |…| View) context owner_scope` refuses an
async argument, which a view builder never is.

## 4. The two doors, sized

**The lint door (shipped in Order 55 as door 1, S).** The checker warns at a
call to a plain `|…| View` parameter anywhere lexically inside an
owner-establishing body (nested literals included), and at a direct call to a
plain `|…| void` parameter in such a body. User code only. The fix is the
clause, named in the message. Cost: nothing changes in any program; a leak
becomes a warning the author sees at the call. Residue: a `|…| View`
parameter called OUTSIDE any owner body (a helper that builds and returns a
view for its caller to place) is not flagged, and is the same trap one hop
later — the warning reads the lexical body, and the trap is dynamic.

**The language door (door 2, M).** A closure parameter whose declared result
type is `View` (and `impl Slot`? — the trait the UI places; `View` is the
estate's spelling) carries `context owner_scope` by default: the clause is
implied, the `sync` marker with it, and a written clause adds to it. The
analyzer's `clause_of_type` answers the implied clause for such a type; the
landing rules, the carrier classes and the hidden-parameter threading then
work as for a written clause. Sized M: the type pass (the implied clause at
every closure type whose result is `View`, declared or inferred), the
diagnostics that print a closure type (the implied clause shown or not), the
formatter (nothing — it is not written), the docs (§8.5 gains the rule), and
the estate (every `|…| View` parameter in std, the website and kolt becomes
injected: the seven kolt wrappers lose their written clause or keep it, and
any stored `|…| View` must be typed). An opt-out needs a spelling
(`(|| View) context ()`?) for the caller that does want the creation owner —
no such caller exists today, so the spelling can wait for one.

Not a door: making ALL closure parameters call-time for `owner_scope`. A
`|| void` callback is as often an event handler as a provider, and an event
handler's registrations do belong to the owner it was made with (the component
that armed it).

## 5. Recommendation

**Door 2, narrowed to `View`, in Order 56 — behind the Order 55 warning for
one order.** Seven of seven real sites wanted the call owner; the breaking set
is empty; the semantics are the ones every author assumed (a view is built
where it is shown). The warning ships first so that any site door 2 would
change is already named in the estate's build logs by the time the rule lands,
and the implied clause makes the seven written clauses redundant rather than
wrong (a written `context owner_scope` on a `View` parameter stays accepted).
If the owner prefers to wait, the lint door is adequate for the shape kolt
met, and `page`'s patch note is the one open leak this paper knows of.

Questions the ruling settles:

1. `View` only, or every result type that is a `Slot` (`impl Slot`,
   `Option<View>` once M170's `nothing()` lands)? Rec: `View` and `impl Slot`;
   `Option<View>` on a shown need.
2. Does the implied clause carry `sync`? Rec: yes — a view builder that awaits
   is a different thing (`Pending` states exist for it).
3. The opt-out spelling, if any. Rec: none until a caller wants the creation
   owner; file it then.

## 6. As built (lane solver-56, 2026-11-03)

Door 2 as §4's paragraph: the implied `context owner_scope` (+ `sync`) on a closure parameter whose declared result is `View` or `impl Slot`, answered by `clause_of_type`; a written clause accepted (redundant); a written clause naming ANOTHER context keeps it after the implied `owner_scope`; `async`-marked and `external` parameters left as written. The implied clause lives in the parameter's type, so diagnostics print it as a written one; `sync` prints from the marker. Door 1's `|…| View` warning removed (unreachable), its `|…| void` half kept (row 765). Spec §8.5. Estate: std 0, website/examples/corpus 0, one test program's stored field typed; kolt checks clean with 0 warnings (the seven written clauses accepted, `page`'s two door-1 warnings gone). No golden moved. Q1–Q3 as recommended.

## 7. The owner's ruling on generality (2026-11-03): a marker trait on the result type (A180)

The owner read §4's door 2 as only vaguely general and asked what makes it so. The answer: the result type is a proxy for the rule - a closure that BUILDS something owner-registered belongs where it is called; one that REACTS belongs where it was made - and the general form is a marker trait on the result type (the types a value of which registers with the ambient owner on creation), with the implied clause following the trait instead of the names `View` / `impl Slot`. RULED: accepted as recommended, with the owner's reservation on record ('not fully convinced on the struct type carrying markers like this, but no evidence to doubt it'). A180 carries the slice; its paper half must show the evidence (the census of owner-registered types, the counter-evidence that would refute it, the opt-out question) before the lane builds.


## 8. The evidence for the marker trait (A180's paper half, lane solver-56, Order 56): it does not hold — door 2 stays as shipped

§7's ruling asked for evidence before the build, and named what would refute the design. The census below reads std at `next` 5fd01232 (paths under `vilan/std/src`; R = `reactive.vl`, B = `browser/web/ui.vl`, P = `process/web/ui.vl`), the website, the corpus and kolt at 0de9e2e (a copy). **Verdict: the defining property — "a value of the type registers with the ambient owner on creation" — is true of NO std type.** Registration is something FUNCTIONS do, and the same type comes out of registering and non-registering functions alike. A marker on the result type therefore cannot mean what §7 says it means, and the one candidate it would have to carry beyond `View`/`Slot` to be general (`Subscription`) is the counter-example (4) asked for. The lane STOPPED here, as A180's brief directs: nothing was built, door 2 (`View`/`impl Slot` by name, §6) stays as shipped.

### 8.1 Census: what registers, and where (1)

The ambient owner is `owner_scope: Context<Owner>` (R:1322); the three ways in are `get_owner().take/defer` (strict), `register_with_owner` (R:1349) and `defer_to_owner` (R:1359) (both owner-optional, "leak-as-today" outside one).

| type | does CREATING a value register? | where registration actually happens |
| --- | --- | --- |
| `View` | **no** — `view(tag)` is `create_element` (B:102-108); `nothing()` B:127; B's header: "a `View` carries no owner" | the binding METHODS on a built view: `bind_text` B:285 → `follow` (B:86-88, `get_owner().take(flow.sub(..))`), `bind_class` B:294, `bind_attr` B:330, `show` B:554, `focus_scope` B:510 → B:2877; SSR (P) registers nothing anywhere |
| `Slot` implementors (B:893; 12 impls B:898-2474) | **no** — a slot value is data (`Swap`, `Each`, `WhenSome` are structs whose closure fields carry the clause, B:1105-1109) | `Slot::place`, at PLACING: the flow arms defer + `follow` (B:932-933, B:986, B:1020, B:1064), the region arms make per-row `Owner::new` + `run_with_owner` (B:1343-1360, B:1445-1463, B:1663, B:1974, B:2495); the static arms (`View`, `str`, `List<View>`) register nothing |
| `Subscription` | **no**, by design — `Flow::sub`/`on_change` (R:2137-2150), `on_settle` (R:2012), `attach_observer` (R:2023), `observe` (R:2600) hand it back `[must_use]`: "You hold the `Subscription`; `effect` is the owner-tied spelling" (R:2141) | `.effect`/`.effect_on_change` register and return `void` (R:2229, R:2166) — no handle type exists |
| `Owner` | **no** — `Owner::new` (R:1117) is unparented; `comp` (R:1452) and `mount_root` (B:2405) likewise | parenting is explicit: `owner.take(child)` or a boundary's `defer(|| owner.dispose())` |
| `SignalCell` | **no** — `SignalCell::new` (R:2711) | **yes** out of `.cell()` (R:2395 `register_with_owner`), `unzip` (R:2798), `Selector::of` (R:3042), `KeyedSource::of` (rpc.vl:6079); **no** out of `.cell_global()` (R:2411) |
| `MemoCell` and the collection memos | — (no public constructor) | **yes** out of `.memo()` (R:2378 → `.cell()`), `ListMemo`/`HashMapMemo`/`HashSetMemo` seals (reactive/delta.vl:1279, :2689, :2873), `RemoteStoreSome::state` (rpc/mirror.vl:2229/2232); **no** out of `.memo_global()` (R:2401) |
| `Resource`, `Transient`, `Store<P>` from `assume` | constructors no | `Source::load` (R:3762), `.transient()` → `hold` (reactive/transient.vl:284), `StoreSome::assume` (reactive/store_core.vl:1149) |
| `Task` / `Nursery` | **no owner at all** — a task registers with `ambient_nursery` (task.vl:95) at the `async` expression; `nursery()` task.vl:127 | — (as §7 expected) |
| plain data | no | — |

So the partition §7 assumed — a set of types whose values register, and a set whose values do not — does not exist: `SignalCell` is in both columns depending on the function that made it, `MemoCell` likewise (`memo` vs `memo_global`), and `View`, the type door 2 was built on, registers nothing when made. What `View` and `Slot` really mark is narrower and true: **the code that BUILDS one is where bindings, effects and holds are made** (B's binding methods and `place`), which is why the builder belongs at the call. That is a property of the result type's *producers*, and std's two UI types are the place it holds without exception.

### 8.2 Is every marked type a closure result, and no unmarked one? (2)

Std's closure parameters answering a view are all written `C: Slot` with the clause already (B:1114-2589, P:548-998, web/remote.vl:31; door 2 makes them redundant, §6). For the wider candidates:

- **`MemoCell`** — supported: kolt writes `name_of: (sync |K| MemoCell<str>) context owner_scope` (panels.vl:1868) and `entries_of: (sync || MemoCell<List<(K, str)>>) context owner_scope` (panels.vl:1913) — builders whose product registers at the call, clause written by hand after B677. No std fun parameter answers a `MemoCell`.
- **`SignalCell`** — no closure parameter in std, the website, the corpus or kolt answers one (`render: |SignalCell<T>| C` takes it as an ARGUMENT, B:925-976).
- **`Subscription`** — answered by closure positions that must NOT take the call owner (8.3).
- **`Owner`**, **`Task`** — no closure parameter answers either.

### 8.3 The counter-evidence (4): a closure answering a would-be-marked type that must not take the call owner

`Subscription` is what a general marker would have to carry to be more than `View` by another name ("Subscription from `on_settle`/`attach_observer`/`observe`", §7's own list), and its closure positions are exactly the REACTING/attaching kind §7 says belongs where it was made:

- `Connection::open_forward(self, channel, key, start: || Subscription)` (rpc.vl:3008) — a `fun` parameter, door 2's own position: `start()` runs inside the call and its handle goes into the connection's `live` table (rpc.vl:3011-3014), released by `close_forward` per demand, never by an owner. Implying `context owner_scope` (+ `sync`) there would make `start` an injected closure for nothing — `.sub` registers nothing — and §3's restrictions would then bind its callers: the starters arrive from `Capability.start` / `KeySubscription.start` FIELDS (rpc.vl:2473, :2529), plain closures that B324's rule makes clause-less.
- `Instance.attach: |Subscriber| Subscription` (R:2083) and the delta stages' `attach` fields (reactive/delta.vl:1188, :1753, :2623, :2816, :3328) — the pipeline's attach channel; registration is the SEAL's (`cell`, `seal_*`), deliberately after the attach.
- kolt's `ProxySignal.on_settle: |Subscriber| Subscription` (lib/proxy_signal.vl:6) — the same attach shape in user code.

The last two are fields (door 2 implies nothing on a field, §6), but they show what the type means in the language: a `Subscription` is the handle a caller HOLDS, and a closure answering one is an attach, not a build. Marking it would put door 2's clause on `open_forward` — the first site a marked non-UI type reaches — where it is wrong. Without `Subscription` (and with `SignalCell`/`MemoCell` registering only through some of their producers), the marker's set is `View` + `Slot` + possibly the memo family: not a general property of types, but a list.

### 8.4 The opt-out (5)

The census answers it the way the reservation feared: std ALREADY has an opt-out, and it is spelled on the PRODUCER — `.memo_global()`/`.cell_global()` (R:2401, R:2411), "a cell that lives as long as the program". A marker on `MemoCell` would imply the call owner for a closure answering `memo_global()`'s product too, which wants no owner at all; widening the set makes an opt-out spelling necessary on the closure (`(|| MemoCell<T>) context ()`?) the first time such a closure appears. With door 2's two names no such closure can exist (a view always registers what it binds through its builder), which is why §5 Q3 could defer it.

### 8.5 Estate (what a build would have moved)

std: 0 closure parameters answer a `Subscription`-free marked type beyond the `C: Slot` sites door 2 already covers; 1 `fun` parameter answers `Subscription` (`open_forward`, rpc.vl:3008 — the counter-example). Website and corpus: 0 closure types answering `Subscription`, `SignalCell`, `MemoCell` or `Owner` (grep of every `.vl`). kolt (0de9e2e copy): 2 closure parameters answering `MemoCell`, both already clause-written (panels.vl:1868, :1913); 1 field answering `Subscription` (proxy_signal.vl:6).

### 8.6 Recommendation (owner question)

Keep door 2 as shipped (`View`/`impl Slot` by name — the two types whose BUILDER is where registration happens, without exception). If the owner wants the memo family covered (kolt's two `MemoCell` builders are the evidence for it), the honest generalization is a list, not a trait: add `MemoCell` (and the three collection memos) to `answers_a_view`'s set, with `.memo_global()` closures as the opt-out question it then raises. A marker trait a user type opts into is not supported by the census: the property it would name is a property of functions, and the first non-UI type it would carry (`Subscription`) is refuted by std's own `open_forward`.
