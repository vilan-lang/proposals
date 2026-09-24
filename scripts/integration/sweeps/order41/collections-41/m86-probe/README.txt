M86 / A112 S3b measurement probe (lane collections-41, Order 41).

app.vl: one browser-target program, variant and push count read from the
environment (M86_VARIANT, M86_PUSHES) through an extern:
  0 ListCell write alone        1 ListCell + each (op path)
  2 ListCell + no-op subscriber 3 bare SignalCell update
  4 SignalCell + each (pass)    5 ListCell + each_by
  6 ListCell + map_each         7 ListCell size() alone
  8 ListCell + each, one set_at per iteration (a row rebuild)
harness.js = crates/vilan-cli/tests/support/dom/stub.js + ui_rows.js +
  global.__param = (name) => Number(process.env["M86_" + name.toUpperCase()]);
  require("./app.js");
Build: VILAN_STD=<worktree>/vilan/std <worktree>/target/debug/vilan build .
slope.sh <variant> [low] [high]: callgrind Ir of `node --jitless harness.js`
at two push counts; per-push Ir is the slope; loadavg recorded per line.
Results: results-before.txt (tree at 1265ea5d / after S3b for variant 5),
results-after.txt (after M86, b979c0af's tree).
