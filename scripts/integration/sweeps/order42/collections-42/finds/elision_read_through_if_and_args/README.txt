FIND (collections-42, Order 42): JS copy elision lets a `Shared::read()` value ALIAS the live
list in shapes B400 does not name. `vilan run .` (JS) vs `vilan run --backend rust .` on
d65d4e75's compiler (collections-42 @c64bf317):

  JS:     let=3 if=4 match=4  closure-arg=5 (held 5)  fun-arg=6 (held 6)
  native: let=3 if=3 match=3  closure-arg=4 (held 5)  fun-arg=5 (held 6)

- `let b = if flag { s.read() } else { [] }` (and the `match` twin) is NOT copied, where
  `let a = s.read()` is (shared.vl §6.1) — a later `s.write().push(4)` in the SAME function
  shows through `b`. No call, no closure: a local binding.
- a `.read()` handed BY VALUE to a `fun` or a closure that writes the cell sees the write
  (B400 names the closure `&List<T>` parameter; this is the by-value `fun` parameter too).
std at collections-42 does not rely on either: A129's `reconcile_span` was first written with
the `if` form, the M86 copy pin moved 11 -> 6 on it, and the code was re-spelled so the
whole-run reads are `let` bindings (inside `held_span`) — the copy profile is the old one.
