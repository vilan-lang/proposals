# Chunk 0: kolt's server on the native backend (census, 2026-11-09)

vilan 0.55.0, kolt exhibit order57 @c745405, on a copy at `~/.vilan/native-census/kolt`.
Diff of the copy: `~/.vilan/native-census/kolt-census.diff` (12 files, +257/-81, each edit tagged
`CENSUS-n`). Repros: `~/.vilan/native-census/repros/` (each fails natively, passes on JS).

## Outcome

The server BUILDS natively after 23 workarounds and SERVES: 24 HTTP probes, a 38-step rpc + MCP
session over the WebSocket and live `[expose]` patches all answered the same bytes as node (apart
from random tokens and the documented `Connection: close` / no `Date`). 16 of kolt's 23 unit tests
pass natively. kolt's e2e harness fails against the JS server too (stale DOM stub), so it cannot
judge native yet.

| | ready | idle RSS |
|---|---|---|
| native release | ~80 ms | 14.0 MB |
| native debug | ~170 ms | 16.9 MB |
| node | ~183 ms | 77.2 MB |

Emit 1.3 s; rustc 8.8 s debug, 37 s release; release binary 9.8 MB.

## The stops, by item

| Item | Stop | kolt sites | Size |
|---|---|---|---|
| B718 | `!` on a host-bound method's result: "unresolved receiver" | store.vl:5239, dates.vl:53-55, rich_text/clipboard.vl:125 | S |
| B719 | B709 follow-ups: let-else with an awaited scrutinee (rustc parse error); `for X is Some(let y)` emits `while matches!` and loses `y` | files.vl:265, mcp.vl:121, mcp_write.vl:648; store.vl:5390 | S |
| B720 | a closure returning `Ok`/`Err` emits `Result<>` (E0107) | mcp.vl:423, mcp.vl:500 | S-M |
| B721 | `List<str>` at a `List<any>` parameter (E0308); std's own `Database::migrate` fails rustc the same way | store.vl:5560 (migrate), store.vl:1769, mcp.vl:720, 753 | S-M |
| B722 | `*` on a tuple-pattern closure binder (E0277/E0614/E0599) | tracker_import.vl:159, mcp.vl:675, 867, store.vl:3612, 5216, 5222 | S |
| B723 | `str + str` emits `Rc<str> + Rc<str>` (E0369) | dictionary.vl:76, coedit.vl | S |
| B724 | a closure over a `&mut` capture is FnMut, emitted as Fn (E0525) | rich_text/clipboard.vl:120 | M |
| B725 | a self-recursive async fn needs boxing (E0733) | dictionary.vl:92 | S |
| B726 | `List<T>::new()` popped before its first push: untyped `Vec::new()` (E0282) | lib/search.vl:743 (tests only) | S |
| B705 | `list.insert(list.position(..), x)` E0502 (known) | store.vl:4919 | S |
| F156 | std members native refuses: `str::index_of`/`last_index_of`, `Instant::to_iso`, the fs options object (`scan_dir`, `create_dir_all`, `remove_dir_all`, `copy_dir`) | tracker_import.vl:141, 239, files.vl:50, 172, markdown.vl:343, mcp.vl:55, 649, handoff_rules.vl:25, store.vl:5387 | S-M |
| F157 | SIGTERM with a detached forever task: the server stops listening, the process stays alive; the second-signal message is wrong | files.vl:126 | S-M |
| F158 | new std members, both backends: padded `std::base64::encode`/`decode`, `JsonValue::keys` | files.vl:187, mcp_write.vl:34, 38 | S |
| M199 | a `Shared` read copies the payload: native spell check 13.2 s for 500 words vs 4 ms on JS | dictionary.vl:47 | M |

kolt's own (the owner's patch, after the std side lands): `now_seconds` -> `std::time::now_millis`;
`decode/encode_uri_component` -> `std::url`; the two base64 bindings and `keys_of` -> F158's members;
the dictionary (`WordList`, five JS bindings, pure logic) ported to vilan. No node module blocks:
`node:crypto` pbkdf2 already builds natively.

Two workarounds in the copy drop behavior and are NOT the fix: `keys_of` (MCP `update_task` loses
the unknown-field error and case-insensitive keys) and the stubbed `near_words`/`completions_in`.
