m1_out_param.vl (probes/), 200,000 iterations, release, callgrind Ir (b94cb47f, 2026-10-05):
  v0  as emitted: Captured<i32> cell + Rc<dyn Fn> closure       70,528,461 Ir  400,012 allocs
  v1  Rc<Cell<i32>> cell + Rc<dyn Fn> closure                    67,128,467 Ir
  v3  Captured<i32> cell + borrowed &dyn Fn closure              34,926,860 Ir  200,012 allocs
  v2  stack Cell<i32> + borrowed &dyn Fn closure (R2a lowering)   4,528,265 Ir  12 allocs
with_value is #[inline(never)] in all four. Build: copy a variant to <dir>/src/main.rs beside the
generated Cargo.toml (vilan build --backend rust m1_out_param.vl), cargo build --release,
valgrind --tool=callgrind.
s1_store.vl (probes/), 20,000 `set`s: 83,052,896 Ir, 300,181 allocs; leak census minted=60036.
