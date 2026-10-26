`for tick in ticks` over a [resource] struct whose inherent `next(self): Option<T>`
awaits (the `process::Keys` shape). Put res_for.vl in a directory with a
`vilan.toml` ([package] name/root/entry) and run:

  vilan run res_for.vl                  # JS: raw on, tick 5..3, raw off, after loop, ... done (exit 0)
  vilan run --backend rust res_for.vl   # native: cargo refuses the emitted Rust

Native emits (main.rs):
    let ticks_11253 = open_11210();
    {
        let mut iterator = ticks_11253;          // the resource MOVES into the loop
        while let Some(tick_11258) = { let awaited = (next_11220(&mut iterator, None)).await; ... } { .. }
    }
    std::mem::drop(ticks_11253);                 // the analyzer's last-use drop of the moved binding
error[E0382]: use of moved value: `ticks_11253`

`vilan_rust::Emitter::for_each_iterator` consumes the subject (`consumed_value_of`)
where the analyzer treats the loop as a LOAN of the resource (its `Drop` runs after
the loop, as on JS). Measured on next @ed1a3ddf + std-55b (A173 S2).
