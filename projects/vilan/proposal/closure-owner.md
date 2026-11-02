# Closure parameters and the owner they build under (B677, door 2)

Status: **RULED 2026-11-02 as §5 recommends (the owner's "do B677"; lane solver-56 builds door 2, rides v0.54.0)** — originally a QUESTION for the owner, Order 56 — written by rpc-55 (Order 55,
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
