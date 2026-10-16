A void `main` whose TAIL is a `match` (void arms) is emitted on JS with
`process.exit($f)` after it, which ends the process while a spawned task is
still pending; natively the program waits for it. A tail `if` and a tail
`print(..);` (with its semicolon) do not take that path.

  vilan run match_tail.vl                 -> "the tail is a match" (task lost)
  vilan run --backend rust match_tail.vl  -> "the tail is a match", "the spawned task finished"
  vilan run call_tail.vl                  -> the same loss: `print("..")` with no `;`
  vilan run print_tail.vl / if_tail.vl    -> both lines on both backends

The decision is syntactic (transformer.rs, main's tail: `Expr::Void` or none
-> discard; anything else -> `process.exit(<tail>)`), so a VOID-TYPED tail
expression - a call with no semicolon, a `match` of void arms - is forwarded
to `process.exit` as the exit code (`undefined`: exit 0) and ends the process
with work still queued.

Seen on vilan 0.51.0 (4b41c7ff5) and on std-54's tree. Met while pinning
A173 S1's held-open stdin (the emitted exit hid the JS pump's `unref`).
