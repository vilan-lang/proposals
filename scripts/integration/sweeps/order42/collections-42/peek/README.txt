`ListCell::peek` after B400 (collections-42). DRAFT, built and probed on a SCRATCH std copy over
collections-42's tree (the compiler at d65d4e75 + c64bf317/01eb9b00's std) — B400 not applied.

peek-weak-get.patch (against vilan/std/src/delta.vl): `peek` lends the cell's own list through
`self.items.downgrade().get()` (a second-class `&List<T>` view) instead of handing the closure's
`&List<T>` parameter the temporary `self.items.read()` — the argument B400 closes.
- JS today: compiles and runs; peek-probe.vl prints `3 b` / `4`; M86's copy pin program reads
  `peek=1001 third=r wholes=0` (unchanged) with the patch applied.
- native: REFUSED — "the `rust` backend does not emit the intrinsic `WeakGet` yet". No corpus program
  and no native-differential program reaches `ListCell::peek` today (the users are docs/std/reactive.md's
  example and ui_rows' M86 pin, both JS), so no exclusion by name is needed until one does.
