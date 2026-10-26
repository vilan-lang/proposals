# incr-55 find: the reach verdict reads a blanket binder differently after build()

`src/b.vl` declares `impl type T { fun len(self): i32 { 0 } }` in a package module; std's own
resolve looks `len` up on its lists and strings (receivers asked under std's RIGID binder scopes).

With the tier oracle on (`VILAN_TIER_ORACLE=on`, P6a), the oracle's verdict over the tiers' log:

- asked BEFORE `build()` (as the entry is about to walk; where §4.2's guard asked): hit, `member len`;
- asked AFTER `build()` (where M121's entry/hot verdict `impl_reach` asks): NO hit, the same log and
  the same impl (`implementations[316]`, subject `Generic(TypeId(9214))`).

So `impl_subject_admits(receiver, Generic(binder))` under a rigid `rigid_binder_scope` answers
differently once `build()` has run. M121's post-build verdict over an entry blanket asked about a
package's rigid `List<T>` still hits (checked on 0.52.0: `impl-reached member len (hot false, entry
true)`), so the difference is narrower than "every blanket"; not chased further in incr-55.

    VILAN_TIER_ORACLE=on VILAN_COUNTERS=1 vilan check src/main.vl   # tier-oracle=1 (asked pre-build)
