# solver-c-45 REPORT (condensed by the integrator; Opus) — tip 7477edc5 on e071b662; 4/4 LANDED (family: miscompile)

B504 a6443601, B506 8002442d, B505 40731e12, B496 7477edc5 — all held, three wider than filed.

THE SHARED CAUSE, two halves. (1) Who holds the cell: `compute_boxed_locals` picked every viewed scalar variable, but only a `let` and a `mut` parameter were ever DECLARED as the cell — pattern captures, destructuring, `is`, guarded legs, `for` elements, immutable parameters, closure parameters and rvalues had none, so `[value, 0]` was built over a `[0]` that did not exist. Now every binder declaration goes through `declare_cell_if_boxed`; a cell-less scalar view gets a fresh cell; a view of a view is the view. (2) Who decides "pair or not": the analyzer decided on the generic body; now the emitter asks the place's own type under the INSTANCE (view bindings, transient captures, `for e in &mut xs`, `mut x: T` parameters). A view handed back through a return keeps the generic body's verdict (`fixed_view_refs`; a control pin).
B505: the implicit receiver at `&self`/`&mut self` is recorded (`receiver_views`) — before this a scalar `&self` receiver never worked on JS at all (`x.bump()` on `i32`). B496: the refusal covers view EXPRESSIONS (`out = &a`, a `borrows` call, branch leaves); the spelled copy `*inner(&holder)` / `*if ..` now copies.

Gates on the rebased tip: nextest 9266/9266 (32 skipped); native_differential 123/123 both modes; check_scope_differential 15/15; fmt, clippy, `vilan fmt --check` std clean. NO golden moved; censuses unchanged. Ledger: no NEW rows; row 15's prose gains "since Order 45 also raised at a view expression … (B496)".
store.vl after this: `through_local` (B506), the read-side rebinds in `some` and `assume` (B504) can go; the WRITE side's rebind stays until F79.
Finds FILED: B511 (HIGH: a qualified blanket call is not monomorphized), B512, F79, F80, F81.
