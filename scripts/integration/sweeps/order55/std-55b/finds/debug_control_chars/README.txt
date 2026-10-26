`str::debug()` (std/debug.vl, E275: `dbg`'s spelling) escapes `\\`, `\"`, `\n`,
`\t`, `\r` and `\0` and passes every OTHER control character through raw. A value
holding an ESC (a `Key::Paste` of pasted terminal output, a line read from a
log with colour codes) prints a LIVE escape sequence: `vilan run debug_esc.vl |
od -c` shows `K e y : : P a s t e ( " a 033 [ 1 m b " )`, and on a terminal the
rest of the output turns bold. Rust's Debug writes `\u{1b}`. Spelling such an
escape needs a decided literal form (B652, parser-55, is settling `\x`/`\u`).
