# kolt-m1: kolt's server on the native backend (census 2, 2026-11-10)

Compiler: local next @3511caa1 (`vilan 0.55.1 (3511caa1b)`), release build at
`~/.vilan/native-m1/bin/vilan`. kolt: a clone of `vilan-migration` @629d901 at
`~/.vilan/native-m1/kolt`. Patch: `~/.vilan/native-m1/kolt-m1.patch` (6 files, +193/-63, fmt clean).

## Outcome

**M1's build half holds, with 1 workaround** (23 before). The server builds with
`--backend rust` from kolt's tree and serves. The one workaround drops a behavior
(see W1). A second change (W2) is a performance workaround, not a build stop.

- 26 HTTP probes: same status, headers and body bytes as node. Only random tokens differ.
- 38-step rpc + MCP session over the WebSocket: byte-identical to node after normalization.
  This includes MCP `update_task` with case-insensitive keys and the "no field X" error,
  which the first census had to drop.
- kolt's server and shared tests: 11 of 11 pass natively and on JS. Library tests: 6 of 7
  pass natively. `rich_text/document_test` stops on `grapheme_before`, an `Intl.Segmenter`
  binding the client editor uses. That is M3 work, not the server's.
- SIGTERM stops the native server cleanly (F157 holds).
- Not checked: kolt has no e2e suite in this tree any more. No reverse proxy (caddy or nginx)
  is installed on this machine, so the proxy run was not done. Keep-alive was exercised by the
  load runs (16 keep-alive sockets, 0 errors).

## Remaining stops

| Item | What it is | kolt-side workaround | Size |
|---|---|---|---|
| NEW (std gap; kolt's comment calls it "M201", which is not in the tracker) | std's `Request` has no peer address. kolt binds `request.socket.remoteAddress` through a JS `[extern]`, and the native backend refuses it. The two-arm `[extern(js=, rust=)]` from ruling S2 is not built yet. | W1: `peer_address` returns `""`. Natively every client shares one sign-in throttle bucket unless `KOLT_TRUST_PROXY=1` (which M1's proxy deployment sets anyway). | S (std: `Request::remote_address` on both backends) |
| M199 | A `Shared` read copies the whole value natively. `word_list()` copies the 123k-word list once per word checked. | W2: the WordList helpers became `impl WordList` methods, which take `&self` natively, so each lookup no longer copies the list. The one copy per word that is left is M199 itself. | M (compiler) |
| NEW-1 (compiler; repro below) | An indexed read through a `Shared` view in a `for` condition, with a `str` parameter as a method argument, moves the parameter inside the loop: rustc E0382. | None needed. Only an abandoned variant of W2 hit it. | S |
| minor | Building a single file natively, or `vilan run` on a `*_test.vl`, writes `<file>.css` next to the source (for example `src/server/main.css`). | None. Delete the stray files. | XS |

Every census-1 stop has cleared: B718-B726, B705, F156, F157 and F158 all hold on kolt's
code, with no hoists, shims or loops needed.

NEW-1 repro: `~/.vilan/native-m1/repros/loop-cond-move/main.vl`. It prints 2 on JS and fails
rustc natively with E0382.

## Measurements

Same machine, same build, a fresh data dir each time, 3 runs each. Other lanes were running,
so the numbers are noisy; the medians are below. Full rows: `~/.vilan/native-m1/measure.txt`.

| | ready | CPU to ready | idle RSS | RSS after session | peak RSS | CPU per req, /api/session | CPU per req, static |
|---|---|---|---|---|---|---|---|
| native release | ~80 ms | 10-20 ms | 14.2 MB | 16.8 MB | 16.8 MB | ~31 us | ~27 us |
| native debug | ~190 ms | ~110 ms | 17.3 MB | 20.4 MB | 20.4 MB | ~130 us | ~137 us |
| node | ~290 ms | ~170 ms | 77.5 MB | 81.3 MB | ~111 MB | ~74 us | ~125 us |

- Requests per second are capped by the node load client (16 sockets, one process): about
  9-11k native release and 12-15k node on /api/session. Server CPU per request is the fairer
  number: native release costs about 0.4x node on a session check (a DB read) and about 0.2x
  on a static file.
- Build: emit plus debug cargo about 15 s cold and 3 s warm. Release cargo build 71 s.
  The release binary is 10.2 MB.
- Spelling, native release versus node:
  - 500 words: 0.96 s versus 5 ms. M199 is the whole gap; it was 10.1 s before W2.
  - A one-edit suggestion (`recieve`): 10 ms versus 1-2 ms.
  - A two-edit suggestion (`acommodatoin`): 122 ms versus 198 ms. Before W2 it took more than
    60 s and timed out.

## Patch hunks by category

(a) Needed by the new compiler on any backend (db-58 / M175):
- `store.vl`: import `SqlValue`; `body_problem` builds a `List<dyn SqlValue>` element by
  element; `role_owner` / `role` become `.value()` at 4 bind sites (`create_organization`,
  `create_invite`, `accept_invite`, `owners`).
- `mcp.vl`: import `SqlValue`; `word_filter` takes and returns `List<dyn SqlValue>`.
- kolt uses `Server::builder()`, not a struct literal, so the F152 timeouts field needs no edit.
- NULL reads (F149): every nullable column kolt reads is behind an `is_null` guard. No panic
  showed up in the probes or the session.

(b) Ruling S2, both backends (host bindings move to std or to vilan):
- `mcp_write.vl`: `keys_of` becomes `JsonValue::keys` (behavior kept); `base64_of` becomes
  `std::base64::encode`.
- `files.vl`: `decode_base64` becomes `std::base64::decode(..).unwrap_or(empty)`. std's decoder
  is strict where node's `Buffer` was lenient; a malformed data URL now gives empty bytes,
  which the existing `len() > 0` check already refuses.
- `dictionary.vl`: `WordList` and its five JS bindings are ported to vilan (`HashMap` plus the
  sorted list, the edit-distance `near_words`, the binary-search `completions_in`). This is a
  real port, not a stub; the results match node on the tests and probes.
- Already done in kolt before this census: `now_seconds` (via `now_millis`) and the URI helpers
  (`std::url`).

(c) Native only:
- W1 `account_guard.vl`: `peer_address` returns `""`.
- W2 `dictionary.vl`: the WordList helpers are `impl WordList` methods. This shape is harmless
  on JS, so it could stay as the port's final form.

## Files

- `~/.vilan/native-m1/kolt-m1.patch`: the patch.
- `~/.vilan/native-m1/kolt-server-release`: the native release server.
- `~/.vilan/native-m1/bin/vilan`: the compiler used.
- `~/.vilan/native-m1/repros/loop-cond-move/`: the NEW-1 repro.
- `~/.vilan/native-m1/tools/`: start, probe, session, spell and load scripts, `measure.sh`
  and `tests.sh`. They kill only their own pids.
- Logs: `probe-*.txt`, `sess-*.txt`, `measure.txt`, `spell.txt`, `tests.txt`, `tests-lib.txt`.
