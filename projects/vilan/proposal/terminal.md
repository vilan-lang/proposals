# Terminal input — `scan()` made real, and a key stream for key-driven programs (A173)

> Status: **DRAFT 2026-10-16 — for the owner's ruling (Q1–Q4, plus Q5 and Q6 that the ground
> truth raised).** Written by lane papers-54 of Order 54 against `origin/next` @b7c7afe0, read in
> `vilan/.claude/worktrees/papers-54`. The probes ran on the installed toolchain,
> `vilan 0.51.0 (4b41c7ff5)` in both locations (v0.51.1 is not cut yet at b7c7afe0; nothing in
> `process.vl`, the `__scan` helper or vilan-rt moved between them), node v24.2.0, Linux under
> WSL2. A paper, not a slice: nothing in the tree changed. Every claim about today's behaviour is a
> line that was read or a probe that was run, and says which. Probes live under
> `scripts/integration/sweeps/order54/papers-54/finds/`.
>
> Related: destruction.md (resources, `Drop`, R9's no-capture rule, §5 synchronous drop),
> async-polymorphism.md (why a callback channel is fire-and-forget), spec `execution.md` §7
> (nurseries, cancellation echoes), native-apps.md §8 Q7 / Order 37 R8 (vilan-rt takes no
> dependencies) and the three `vilan-rt-*` crates that answer it, std `fs.vl`'s watch tier
> (`Watcher::next`, the pull shape this paper copies) and `fetch.vl`'s `BodyReader`.

## 0. The ask, and the answer up front

**The ask** (the owner, after Order 53: "how can we improve stdin scanning?"): a per-key primitive
— `scan_key` awaited per iteration, or a callback — that `scan_char`/`scan_line` could be built on,
with backspace handling.

**The answer.**

1. **`scan()` does not work at all today on JS, and does not exist natively** (§1.1). The item
   said it reads to EOF and so blocks an interactive prompt; the truth is worse: the helper calls
   `require("fs")` inside an ES module (`.mjs` since B86b, v0.33.0, 2026-08-07), the
   `ReferenceError` is swallowed by the helper's own `catch`, and every `scan()` answers `""`
   whatever stdin holds. Nobody noticed in two months because nothing calls it: zero uses in the
   tree, the corpus, kolt or the website. So **S1 is a fix, not an improvement**, and it costs
   nothing to break.
2. **S1 first, and S1 is the line reader done right** (§5): incremental (to the next newline, no
   read-to-EOF), awaiting (an `async` extern carrying the ambient cancel signal, so a key loop and a
   timer coexist), EOF distinguishable from a blank line, implemented natively, and a way to print a
   prompt WITHOUT a newline — which std cannot do today (`print` is `console.log`; there is no
   other stdout door), so an interactive prompt cannot even be written. The terminal stays in
   COOKED mode for lines: the kernel's line discipline already does echo, backspace, Ctrl-U and
   Ctrl-W, and that is the backspace handling the owner asked for, for free.
3. **Keys are a PULL stream on a RESOURCE** (§2, §3): `let keys = process::keys();` puts the
   terminal in raw mode and `Drop` restores it; `keys.next()` awaits the next `Key` (`None` when
   stdin closes) and carries the ambient cancel signal, exactly `Watcher::next`'s shape. The shape
   was PROBED end to end on both backends with a stand-in resource (§1.4): the `Drop` runs at the
   handle's last use after a `jump break`, on a panic, and when a nursery cancels the child that
   owns it. A callback is the wrong door for the reasons `fs.vl` already wrote down; a reactive
   `Source<Key>` is derivable from the stream by a task, never the reverse.
4. **The decoder is written ONCE, in vilan, in std** (§4): each backend supplies only raw BYTES
   (node: `setRawMode` + `'data'`; native: termios raw mode / the Windows console's VT input mode),
   and one std state machine turns bytes into `Key`s. Identical decoding on both backends is then a
   property of construction rather than of a differential that chases two decoders (node's
   `emitKeypressEvents` and crossterm's disagree on several sequences — §4.1), and the native
   differential still pins it over piped fixtures.
5. **A pipe decodes the same grammar, deterministically** (§4.3): on a non-TTY stdin there is no
   raw mode and no escape timeout — the decoder takes unbounded lookahead (the bytes are all coming
   or EOF is), so `printf 'j\x1b[Aq' | vilan run menu.vl` drives a menu exactly as a person would,
   the corpus can test key programs, and both backends agree byte for byte.
6. **A `for key in keys` loop is not available today, and the paper does not need it** (§1.3): the
   trait form is REFUSED (`Iterator::next` takes `&mut self`, and an async function cannot), and
   the inherent form passes the checker and then MISCOMPILES on both backends (two finds, filed).
   S2 ships the `for { match keys.next() { .. } }` loop `Watcher` documents; `for key in keys`
   arrives for free when the miscompile is fixed (Q6).

## 1. Ground truth

### 1.1 `process::scan()` — the one stdin door

- **std** (`vilan/std/src/process.vl`): `external fun scan(): str;` — synchronous, doc "Reads the
  next line from standard input (empty string at EOF)". No `[extern]`: the analyzer maps the item
  to `Intrinsic::Scan` by name (`analyzer.rs` ~88693, `module_member("process", "scan")`).
- **JS** (`transformer.rs::helper_source("__scan")`, ~1314): a module-level array filled ONCE by
  `require("fs").readFileSync(0, "utf-8").split("\n")`, wrapped in `try { } catch { stdin = []; }`,
  then one element per call, `""` past the end. Emitted as `__scan()` by the intrinsic's lowering
  (~10402).
- **The probe** (`finds/scan_native/scan_native.vl`, three `scan()`s printed): `printf 'a\r\nb\n' |
  vilan run scan_native.vl` prints `first=[] second=[] third=[]`. Re-running the emitted
  `scan_native.mjs` with the `catch` logging shows `ReferenceError: require is not defined` — an ES
  module has no `require`. The process-leg artifacts became `.mjs` in e5a809c0 ("name process-leg
  build artifacts .mjs (B86b, §8.1 ruling)", first in v0.33.0); `scan()` has answered `""` on every
  call since. Filed as a find (F-1).
- **Had it worked**: it would have read to EOF before answering the first line (an interactive
  prompt hangs until Ctrl-D), kept a trailing `\r` on CRLF input, and been unable to tell a blank
  line from EOF (`""` for both — a `for { let line = scan(); if line == "" { jump break; } .. }`
  loop stops at the first blank line of a piped file).
- **Native**: `vilan run --backend rust scan_native.vl` refuses with a named diagnostic: "the
  `rust` backend does not emit the intrinsic `Scan` yet — this is F1's slice S1b …". Not silent.
  The same refusal names `args` (intrinsic `Args`), `exit` and `cwd` (host bindings); `env` works
  (`finds/scan_native/process_native.vl` prints `$HOME`). So native has one of `std::process`'s
  five functions (F-4).
- **Estate**: `scan()` has zero callers in the vilan tree (std, examples, `vilan/test`, the
  in-crate test programs), kolt (`src/lucide`'s `scan()` is an icon) and the website. The docs name
  it in `docs/std/process.md` and `docs/guide/persistence.md` as "read a line from stdin".
- **The corpus and the differential** run every program with stdin `Stdio::null()`
  (`corpus.rs` ~1120) and have no stdin fixture: the item's "so the corpus and the differential
  keep working" has nothing to keep — the pipe pins in S1 are new harness, not regressions guarded.
- **Output**: `std::io::print` is `[extern("console.log")]` (always a newline) and natively
  `println!`. There is NO way to write `name? ` and leave the cursor after it. vilan-rt's `print`
  is line-buffered (`println!` through Rust's `LineWriter`), so a native prompt must also FLUSH
  before it blocks on stdin.

### 1.2 Values arriving over time: what std already does

- **`fs::Watcher`** (`fs.vl` ~851–1020): a `[resource] external struct`; `next(self): Change`
  awaits `raw_next(self, ambient_signal())` — the ambient nursery's `CancelSignal` handed to the
  host, so a cancelled nursery parked on a change drains. Never ends (no `Option`: a watch has no
  end). `Drop` calls the synchronous `stop_watch` (a `clearTimeout`), which the doc notes needs no
  exception to destruction.md §5. The doc comment argues PULL NOT CALLBACK in full: a `|Change|
  void` observer is a void channel (fire-and-forget under async-polymorphism.md, so a handler
  cannot await), and R9 forbids a closure capturing a resource, so a handler could not hold an
  open `File`.
- **`fs::Reader`** (~742): `[resource]`, cursor in a `Shared<i53>`, `next(self, size): Bytes`
  awaiting, EMPTY at EOF. Its doc states the rule that decides §1.3: "`next` awaits the read, and an
  async function cannot take a `&mut` view — the view would be held across the suspension".
- **`fetch::BodyReader::read_chunk`** (`fetch.vl` ~106): `async external`, `ChunkResult { done,
  value }`. It does NOT take the signal itself: `fetch` attaches the ambient signal to the REQUEST
  (`attach_ambient_signal(options)`), and aborting the request errors the body stream. So the
  "carry the ambient signal" model is the watcher's, per wait; the fetch model is per-operation.
- **Native**: vilan-rt's executor (`executor.rs`) is single-threaded with a timer list and an
  `IoSource` registry polled once per turn (1 ms idle interval, "the price of" R8: no
  epoll/kqueue without libc). There is no stdin source.

### 1.3 Does a `for` over an awaiting `next` work? (probes, `finds/async_iterator_for/`)

- **The trait form is refused.** `impl Ticks with Iterator<i32> { fun next(&mut self) .. time::sleep(5) .. }`
  → `an async function cannot take '&mut' parameters: the view would be held across its suspension
  points. Pass a value, or a Shared/handle.` (`async_iterator_for.vl`). That is why `Watcher` and
  `Reader` avoided the trait: `Iterator<T>::next(&mut self)` cannot be async, by the language's
  own soundness rule, not by taste.
- **The inherent form passes the checker and miscompiles.** spec §3.5 accepts "any type providing
  the iterator protocol" for `for x in`, and a by-value inherent `next(self): Option<T>` that
  awaits (cursor in a `Shared`) checks clean (`async_inherent_for_in.vl`). Then:
  - JS awaits the call but drops the threaded CONTEXT argument (`await (next($g))` where `next`
    is `async function next(self, $a)`), so `sleep`'s `ambient_signal($b)` reads `undefined[0]` →
    `TypeError: Cannot read properties of undefined (reading '0')`, exit 1.
  - native emits `while let Some(t) = next_11159(&mut iterator)` — no `.await` AND no context
    argument; cargo refuses it ("a BACKEND defect").
  - The context half is not about async: a SYNC `next` that reads a context (`ambient_signal()`)
    in an ordinary `impl .. with Iterator<i32>` crashes the same way on JS and fails cargo on native
    (`finds/for_in_context_next/for_in_context_next.vl`), while the same `next` called directly
    works. Filed as F-2 (miscompile: the `for`-in's implicit `next` call is outside the context
    threading pass) and F-3 (native: the implicit `next` of an awaiting subject is not awaited).
- **The pull loop works today on both backends** (`async_pull_loop.vl`): `for { match t.next() {
  Some(let v) => .., None => jump break } }` over the awaiting inherent `next`, and the same loop
  spawned as a nursery child is cancelled and joined cleanly (exit 0, both backends).
- **A nursery BODY parked on IO when its own nursery cancels** propagates the rejection
  (`finds/nursery_body_cancel/`: JS prints `AbortError: This operation was aborted`, native "the
  program failed", both exit 1). That is spec `execution.md` §7 as written ("a body suspended on
  cancellable IO when the signal fires observes the rejection, which then propagates") — not a bug,
  but it decides the idiom: a key loop that something else cancels runs as a spawned CHILD, not as
  the nursery body.

### 1.4 The resource shape, probed (`finds/resource_keys_shape/`)

A `[resource] struct Keys { left: Shared<i32> }` with `open` printing "raw on", an awaiting
`next(self): Option<i32>`, and `Drop` printing "raw off" (`resource_keys_shape.vl`), on BOTH
backends, identical output:

- broken out of with `jump break` after three keys: `raw off` prints at the handle's LAST USE
  (spec `memory.md`: "whose owner's last use runs its destructor"), before the code after the loop;
- opened inside a spawned child that the body cancels: `raw on`, `raw off`, `cancelled and joined`,
  exit 0 — the cancellation unwinds the child and runs the `Drop`;
- a `panic` while the handle is live (`panic_drop.vl` / `panic_drop_native.vl`): `Drop` runs on
  both backends (JS before the panic report, native after it);
- `process::exit` does NOT run `Drop` (JS; native has no `exit` yet) — so the restore also needs a
  runtime-level guard (§3.3).

And node itself restores the terminal when a raw-mode program exits without restoring, by
`process.exit` or by an uncaught throw (`finds/node_keypress/raw_exit.py`: `icanon echo` after
both) — node's `ResetStdio` at exit.

### 1.5 What node's keypress decoder answers (`finds/node_keypress/keypress.out`)

Driven through a pty (`drive.py`), `readline.emitKeypressEvents` + `setRawMode(true)`:
arrows `\x1b[A..D` → up/down/right/left; `\x1b[H`, `\x1bOH`, `\x1b[1~` → home; `\x1b[F`,
`\x1b[4~` → end; `\x1b[5~`/`6~` pageup/pagedown; `\x1b[3~` delete; `\x1b[2~` insert; `\x1bOP` f1,
`\x1b[15~` f5, `\x1b[24~` f12; `\x7f` AND `\b` → backspace; `\t` tab; `\x1b[Z` tab+shift; `\r` →
"return" but `\n` → "enter"; `\x03` → c+ctrl (raw mode turns ISIG off: Ctrl-C is a KEY, not a
SIGINT); `\x04` d+ctrl; `\x1b[1;5C` right+ctrl; `\x1b[1;2A` up+shift; `\x1bx` x+meta; `é` → no
`name` at all (only `str`); bracketed paste → `paste-start`, the pasted characters ONE KEYPRESS
EACH, `paste-end`; a lone `\x1b` is delivered ~500 ms later as `escape` **with `meta: true`**.
These are the reference rows the std decoder's pins quote; §4.1 says where vilan should differ.

## 2. The doors

### 2.1 Pull vs callback vs a reactive `Source<Key>`

- **Pull (recommended)**: `keys.next(): Option<Key>`, awaited. The `for` loop, `jump break`,
  `?`-style early exits, ordinary locals for state, error flow and nursery cancellation all come
  for free; the handle can be held by a scope that also owns a `File`. It is the shape the language
  already chose twice (`Watcher`, `Reader`) and wrote the argument for.
- **Callback** (`on_key(|Key| ..)`): a void channel — fire-and-forget, so a handler cannot await a
  read or a sleep; R9 forbids it capturing a resource; and "when does raw mode end" has no scope to
  answer it (a registration is not an owner). Rejected for the reasons `fs.vl` gives.
- **Reactive `Source<Key>` / a `Cell<Key>`** (for a reactive terminal UI): DERIVED, not primary —
  a spawned task `for { match keys.next() { Some(let k) => last_key.set(k), None => jump break } }`
  builds it in four lines, and owns the resource while it does. The reverse (a stream from a
  source) loses keys: a cell holds the latest value, two presses in one turn are one. Nothing to
  ship for it in S2; a docs example.

### 2.2 A free function vs a RESOURCE

Raw mode is TERMINAL STATE that outlives the call that set it. A free `scan_key()` would have to
enter and leave raw mode per call (a flicker of cooked mode between keys: a key pressed between
two calls is echoed and line-buffered — lost to the program until Enter) or leave it on with no
owner to turn it off. A resource owns it: `process::keys()` enters raw mode, its `Drop` restores at
the last use, on `jump break`, on a panic, on a cancelled task (§1.4). destruction.md's rule, with
`Watcher`'s synchronous teardown as the model (restoring termios is one synchronous `tcsetattr`; on
node one synchronous `setRawMode(false)`), so no exception to §5.

A `scan_char()` falls out as a filter over the stream (`keys.next()` until a `Char`), not as a
second primitive.

### 2.3 Cooked `scan()` vs line editing on keys

`scan()` stays on COOKED mode. The kernel line discipline (and the Windows console's line input)
already gives echo, Backspace, Ctrl-U (kill line), Ctrl-W (kill word), and on Windows history —
that IS the owner's "backspace handling", and it costs std nothing. Line editing built on keys means
a line editor in std (cursor movement, wide characters and grapheme widths, wrapping, history,
completion): readline/rustyline-sized, and only worth it on a shown need (S3). The key stream is
for KEY-DRIVEN programs — menus, pagers, games, a TUI — where a line is not the unit.

## 3. The surface (S1 + S2)

### 3.1 Lines (S1)

```vilan
/// The next line of standard input without its line ending (`\n` or `\r\n`), awaiting
/// one if none has arrived; `None` once stdin has ended and every line was read. A last
/// line with no newline is still a line.
external fun read_line(): Option<str>;        // async extern, carries ambient_signal()

/// `read_line()`, with `""` at end of input — the existing door, kept.
fun scan(): str { read_line().unwrap_or("") }

/// Writes `text` with NO newline (flushed), then `scan()`s — the one-line interactive shape.
fun prompt(text: str): str
```

Names are Q1's; `prompt` is Q2. `read_line` is the honest door (EOF is not a blank line) and
`scan` is its convenience, so nothing that compiles today changes meaning except that it now works.

### 3.2 Keys (S2)

```vilan
/// A key-driven view of the terminal: raw mode while the handle lives, restored at its last use.
[resource]
export external struct Keys;

export fun keys(): Keys                       // process::keys()

export impl Keys {
	/// The next key, awaiting one; `None` once stdin has ended. Carries the ambient cancel signal.
	fun next(self): Option<Key>
	/// The same stream with the modifier set on every key (an editor's door, §3.2.1).
	fun next_press(self): Option<Press>
}

export enum Key {
	Char(str),     // one Unicode scalar as typed (shift applied: "A"); vilan has no char type
	Ctrl(str),     // Ctrl + a scalar: Ctrl("c") is 0x03, Ctrl("d") 0x04 (raw mode: no SIGINT, no EOF)
	Alt(str),      // ESC-prefixed scalar: Alt("x")
	Enter, Tab, BackTab, Backspace, Delete, Insert, Escape,
	Up, Down, Left, Right, Home, End, PageUp, PageDown,
	F(i32),        // F1..F12
	Paste(str),    // a bracketed paste, WHOLE (never keystrokes - a pasted "\n" is not Enter)
}

export struct Press { key: Key, ctrl: bool, alt: bool, shift: bool }
```

#### 3.2.1 Why `Key` is flat and the modifier set is a second door

vilan's patterns are variants with positional payloads, literals and tuples — no struct patterns
(spec §3.10). The common program matches `Key::Char("q") | Key::Ctrl("c") => jump break`,
`Key::Up => ..`: a flat enum whose two common chords (Ctrl/Alt + a scalar) are VARIANTS reads
cleanly. Modifiers on named keys (Ctrl+Right, Shift+Up) are an editor's need: `next_press()` returns
the same decoded key normalized (`Char("c")` + `ctrl`) with all three flags; `next()` is
`next_press()` flattened (ctrl+scalar → `Ctrl`, alt+scalar → `Alt`, modifiers on a named key
dropped, Shift+Tab → `BackTab`). One decoder, two views.

#### 3.2.2 The decisions inside the enum

- **`\r` and `\n` are both `Enter`** (node splits "return"/"enter"; a terminal's Enter key sends
  `\r` in raw mode, a pipe's newline is `\n`; one key to the program). `\r\n` on a pipe is ONE
  `Enter`.
- **`\x7f` and `\x08` are both `Backspace`** (node agrees; terminals differ on which they send).
- **Ctrl-C is a key** (`Ctrl("c")`), as in node's and crossterm's raw mode. A program that never
  handles it cannot be interrupted while it holds `Keys` — the docs' loop sample handles it, and Q5
  asks whether the runtime should instead restore and exit 130 by default.
- **A lone Escape is `Escape`, never `Alt` of nothing** (node's `meta: true` quirk not copied),
  decided by a 50 ms timeout on a TTY (node waits 500 ms, which reads as lag; vim's `ttimeoutlen`
  100, tmux users set 10–50) — a constant, no knob.
- **Unrecognized sequences are dropped**, not delivered as garbage `Char`s (a well-formed CSI is
  consumed to its final byte, so an unknown key never leaks `[1;9X` as typing).
- **Bracketed paste is switched on** with the handle (`\x1b[?2004h`, off in `Drop`), delivered as
  one `Paste(str)`.

### 3.3 Restore guarantees

Raw mode ends at, in order of how often each happens: the handle's last use (`Drop`); a panic
(`Drop` runs on both backends, §1.4); a cancelled task (`Drop` runs, §1.4); `process::exit` and an
uncaught failure (node's `ResetStdio` on JS, §1.4; natively the runtime keeps the saved termios
state and restores it from a panic hook and from vilan-rt's `exit` path); SIGTERM/SIGHUP (node: its
own handlers reset stdio; natively only if the program links `vilan-rt-signal` — otherwise the
shell's `reset`, stated in the docs); SIGKILL (nothing can). One `Keys` at a time: a second
`keys()` while one lives panics with a message (two owners of one terminal mode cannot both restore
it).

## 4. The decoder

### 4.1 One decoder, in vilan, in std — not two decoders reconciled

The alternative the item named — node's `emitKeypressEvents` on JS, crossterm (or a hand-rolled
termios decoder) natively, held together by the native differential — puts TWO decoders behind one
`Key` type, and they disagree today on rows that matter: node says "return" for `\r` and "enter"
for `\n`, gives no name to non-ASCII scalars, delivers bracketed-paste content as individual
keypresses, waits 500 ms for a lone Escape and marks it `meta`; crossterm (from its documentation;
not probed — no crate builds here) maps `\n` to Enter only outside raw mode, has a `Paste` event,
and decides a lone Escape by read-chunk boundary with no timeout. A differential over a PIPE cannot
even see the timeout rows. Each disagreement would be a translation table on one side, tested only
where a pty harness can reach.

**Recommended instead: the backends deliver BYTES, std decodes.** A `KeyDecoder` state machine in
`std::process` (vilan source, ~250 lines): UTF-8 assembly from the lead byte; C0 controls
(`\r`/`\n` Enter, `\t` Tab, `\x7f`/`\b` Backspace, `\x01`–`\x1a` `Ctrl`); `ESC` + scalar `Alt`;
CSI `ESC [ params final` (arrows, Home/End in both spellings, `~`-keys 1–6 and the F-key numbers,
`Z` BackTab, the xterm modifier parameter `;2..;8`); SS3 `ESC O P..S`/`H`/`F`; the paste brackets
`ESC[200~`..`ESC[201~` accumulated into one `Paste`. It compiles on both backends from one source,
so identical decoding is a property of construction; the native differential runs its pins (§4.4)
anyway, because the BYTE sources are per-backend. Cost of keys is human-speed; a vilan state machine
is free at that rate.

### 4.2 The byte sources

- **JS**: `process.stdin.setRawMode(true)`, `'data'` as `Buffer`s (no `setEncoding` — the decoder
  wants bytes), the same pump as S1's line reader (§5) with `pause()`/`unref()` whenever nobody
  waits. On Windows libuv's raw mode delivers the console's keys as VT sequences, so the same
  decoder applies.
- **Native, unix**: `tcgetattr` → save → `cfmakeraw` (ICANON, ECHO, ISIG, IEXTEN, ICRNL off), then
  OPOST|ONLCR set again so `\n` still returns the carriage for `print` (libuv's raw mode does the
  same, so both backends print alike) → `tcsetattr`; restore the saved struct
  on drop. Bytes come from S1's stdin reader thread (§5.2) in byte mode.
- **Native, Windows**: `GetConsoleMode`/`SetConsoleMode` on the input handle: clear
  `ENABLE_LINE_INPUT | ENABLE_ECHO_INPUT | ENABLE_PROCESSED_INPUT`, set
  `ENABLE_VIRTUAL_TERMINAL_INPUT` — the console then delivers VT sequences as bytes (Windows 10
  1607+), and the SAME std decoder applies; `ENABLE_VIRTUAL_TERMINAL_PROCESSING` on the output
  handle for S2's redraws. No `ReadConsoleInputW` record translation.

**The dependency (Q3).** Every one of those calls is FFI — `unsafe` — and vilan-rt takes no
dependencies and forbids `unsafe` by ruling (Order 37 R8, its Cargo.toml). The repo has answered
that three times the same way: a SEPARATE `vilan-rt-*` crate with one dependency, named by the
emitted cargo project only when the program reaches the surface (`vilan-rt-sqlite`/rusqlite,
`vilan-rt-crypto`/getrandom, `vilan-rt-signal`/ctrlc). So: **`vilan-rt-term`**, linked only by a
program that calls `process::keys()`, depending on `libc` (unix) and `windows-sys` (Windows) —
BOTH already in the compiler's own lockfile (`Cargo.lock`: libc 0.2.189, windows-sys 0.61.2), so
the third-party notices already carry them — for ~80 lines of mode switching. NOT crossterm: it
brings mio, signal-hook and parking_lot for an event loop and a decoder this design does not use,
and its decoder would be the second decoder §4.1 removes. NOT a dependency-free `stty raw -echo`
subprocess: unix-only, and its restore depends on `stty` being on PATH at drop time.

S1 needs none of this: a cooked-mode line read is `std::io::stdin()` — dependency-free, in
vilan-rt.

### 4.3 The pipe rule (Q4)

When stdin is NOT a TTY (`process.stdin.isTTY` false; natively `std::io::IsTerminal`), `keys()`
does not touch terminal modes (there are none) and decodes **the same grammar with unbounded
lookahead and no timeout**: the decoder waits for the bytes that complete a sequence or for EOF,
and a lone ESC is `Escape` only when the next byte cannot continue a sequence or EOF arrives. Because
a pipe's bytes are fixed in advance, the decoded stream is DETERMINISTIC — independent of chunk
boundaries and timing — so:

- `printf 'jj\rq' | vilan run menu.vl` and `vilan run menu.vl < script.keys` drive a key program;
- the corpus can pin a key program with a stdin fixture, and the native differential compares the
  two backends byte for byte on it;
- `\n` is `Enter` (§3.2.2), so a line-oriented fixture still reads naturally;
- `None` at EOF ends the loop.

The alternative the item sketched — bytes degrade to `Char`/`Enter` only, escapes passed through
as `Char("\u{1b}")` — makes a key program untestable through a pipe exactly where it is most worth
testing (arrows), and a third alternative, refusing `keys()` on a non-TTY, removes the corpus
entirely. A `Keys` over a pipe enabling bracketed paste writes nothing (no terminal to tell).

### 4.4 The identical-decoding gate

1. **Unit pins on the std decoder** (`vilan test` / corpus programs feeding byte strings to
   `KeyDecoder` directly): one per row of §1.5's table, the vilan answer beside node's, plus
   malformed CSI, a sequence split across two chunks, paste content containing ESC and `\n`, a
   4-byte UTF-8 scalar split across chunks.
2. **Corpus + native differential over stdin fixtures**: a key program with a `<name>.stdin`
   beside it (the harness learns to pipe a fixture instead of `Stdio::null()` — new in S1), run
   both ways.
3. **One pty pin per backend** (unix only, cfg-gated; python's `pty` or a tiny Rust pty in the
   test): raw mode is entered, a lone ESC arrives as `Escape` after the timeout, `Drop` restores
   `icanon echo` (`stty -a` after the program, as `finds/node_keypress/raw_exit.py` does).

## 5. S1 in detail — what std-54 builds

### 5.1 JS

Retire `Intrinsic::Scan` and the `__scan` helper: `read_line` becomes an ordinary
`[extern("__stdin_line")] async external fun stdin_line(signal: Option<CancelSignal>): Option<str>`
(the watch tier's pattern), so the intrinsic table, `const_eval`'s impure list entry and the
interpreter's free-name arm lose a special case (the extern is impure by construction). The helper
(prototyped in `finds/node_scan_line/scan_line.mjs` and `scan_line_unref.mjs`, both probed):

- one shared stdin pump: `'data'` appends to a buffer, `'end'` marks the end; waiters queue;
- a line is handed out at the first `\n` (a trailing `\r` stripped); at end the remainder (if any)
  then `None`;
- `resume()` + `ref()` while a waiter is pending, `pause()` + `unref()` when none is — **without
  the `unref` a PIPE keeps the process alive until the writer closes** (probed: 3.4 s with a writer
  that stays open, 0.47 s with it); with it the process exits as soon as `main` ends, and a silent
  writer still makes a pending `read_line` wait (5 s probed) — a pending promise is not a handle,
  the `ref()` is what holds the loop;
- an abort on the signal removes that waiter and rejects it with the cancellation echo; a line that
  arrives later stays in the buffer for the next reader (cancellation abandons the WAIT, never a
  line);
- on a pty (`drive_tty.py`): the prompt appears before any input, each line answers as it is typed,
  the process exits by itself after the last read.

`prompt(text)`: `process.stdout.write(text)` then the read (node's stdout write to a TTY is
synchronous; to a pipe it is synchronous on Linux, so ordering with `console.log` holds).

### 5.2 Native

vilan-rt (no dependency, no `unsafe`): a lazily started stdin READER THREAD (std's `Stdin` has no
non-blocking mode) that reads ON DEMAND — a request channel says "a line" (S2: "bytes") — and sends
the result back over `std::sync::mpsc`; an `IoSource` that is LIVE only while a `read_line` waits
(so an idle stdin never holds the executor open, the native twin of `unref`) and whose `poll` is a
`try_recv`. A cancelled wait leaves the thread blocked in its read; the line it eventually gets is
queued for the next reader. The thread is detached; returning from `main` ends the process with it.
`prompt` writes with `print!` and FLUSHES (Rust's stdout is a `LineWriter`). The 1 ms idle poll
while a human types is the executor's documented price; a refinement (block on the channel until
the next timer deadline when the stdin source is the only live work) is worth a follow-up, not S1.
std-54's reader is a listed arm in native-54's crate (briefs54 ownership map).

While there: `args`, `exit` and `cwd` are three lines of Rust std each and are refused today
(F-4); S1 is the moment to make `std::process` whole natively so the S1 pins (which want `exit`
for a failing prompt) and every CLI example build both ways.

### 5.3 The pins

- the pipe: `printf 'ann\r\nbob' | prog` reads `ann`, `bob`, then `None`; a blank line is `Some("")`;
  both backends (corpus stdin fixtures, native differential);
- the interactive prompt (`vilan run`, both backends): a program prints a prompt, reads a line,
  prints the answer — driven by a scripted stdin that writes AFTER the prompt appears (a pipe whose
  writer waits for the prompt on the child's stdout; a pty where the platform has one);
- awaiting: a timer task ticking while `read_line` waits keeps ticking (the JS helper and the
  native source never block the loop);
- cancellation: a `read_line` in a cancelled child returns control, the program exits 0;
- the old `scan()` at EOF answers `""` forever (unchanged contract).

Family: `fix` (scan was broken), with the docs' `std::process` section rewritten. Not breaking: no
caller exists.

## 6. Slices

| Slice | What | Size | Order |
|---|---|---|---|
| **S1** | `read_line`/`scan` incremental + awaiting on both backends; `Intrinsic::Scan` retired for an extern; native reader thread + `IoSource`; `prompt` if Q2; native `args`/`exit`/`cwd` (F-4); corpus/differential stdin fixtures; the prompt pin; docs | S–M | 54 (std-54) |
| **S2** | `Keys` + `keys()`; `Key`/`Press`; the std `KeyDecoder`; the shared byte pump (JS); `vilan-rt-term` (libc / windows-sys) for raw mode; the pipe rule; bracketed paste; restore guards; `io::write` (no-newline stdout — every redraw needs it); the §4.4 gate | M | 55 |
| **S3** | line editing on keys (`read_line_edited` or a `LineEditor`): cursor, history, completion | M–L | on a shown need |

(`Key`'s declaration alone may land in S1 as a type with no reader, per briefs54, if Q1 is ruled.)

## 7. Questions for the owner

1. **The names.** Rec: `process::keys(): Keys`, `Keys::next(): Option<Key>`, `Key`, and
   `Keys::next_press(): Option<Press>` for the modifier set (§3.2.1); for lines,
   `process::read_line(): Option<str>` (EOF distinguishable) with `scan()` kept as
   `read_line().unwrap_or("")`. Alternatives: `scan_key`/`scan_line` (reads as one-shot calls, hides
   the raw-mode resource); `stdin::keys()` (a new module for two functions).
2. **A `prompt(text)` twin of `scan()`.** Rec: **yes** — `process::prompt(text): str`, the text
   written with NO newline and flushed, then the line read. Today a program cannot print a prompt
   that leaves the cursor on its line at all (`print` always ends the line), so without it S1's
   "interactive prompt works" cannot be written. The general no-newline `io::write(text)` waits for
   S2, where redraws need it with cursor control.
3. **The native decoder's dependency policy.** Rec: **no crossterm, no hand-rolled decoder in
   Rust** — the decoder is std vilan (§4.1); natively only RAW MODE needs FFI, in a separate
   `vilan-rt-term` crate on `libc` + `windows-sys` (both already in the lockfile), linked only when
   a program reaches `keys()`, exactly as `vilan-rt-signal`/`-crypto`/`-sqlite` are. S1 needs no
   dependency at all.
4. **The exact pipe-degradation rule.** Rec: **decode the full grammar on a pipe, with unbounded
   lookahead and no timeout** (§4.3) — deterministic, so key programs are testable through
   `vilan run < file`, the corpus and the native differential; `\r`, `\n` and `\r\n` are each ONE
   `Enter`; no terminal mode is touched; `None` at EOF. Not "`Char`/`Enter` only".
5. **Ctrl-C under `keys()`** (raised by the ground truth: raw mode turns ISIG off on both node and
   termios). Rec: deliver it as `Key::Ctrl("c")` (node's and crossterm's behaviour; a pager or an
   editor binds it), with the docs' loop sample ending on it — rather than the runtime restoring
   and exiting 130, which would make the key unbindable.
6. **`for key in keys`** (§1.3). Rec: fix F-2/F-3 (the `for`-in's implicit `next` threads contexts
   and awaits on both backends) as their own items in Order 55, after which `for key in keys { .. }`
   works over S2's inherent awaiting `next(self)` with no new language rule; S2 does not wait on
   it and documents the `for { match .. }` loop meanwhile.

## 8. Finds filed (`sweeps/order54/newitems54-papers-54.json`; F-1 = `B?1`, F-2 = `B?2`, F-3 = `F?3`, F-4 = `F?4`, and `E?5` the no-newline stdout gap of Q2)

- **F-1** `process::scan()` answers `""` on every call on JS since v0.33.0 (`require` in an ES
  module, swallowed by the helper's `catch`). Closed by S1.
- **F-2** a `for x in subject` whose `next` reads a context (any IO wait, `ambient_signal()`) is
  emitted without the threaded context argument on both backends — check-clean programs crash
  (JS `TypeError`) or fail cargo (native). `miscompile`.
- **F-3** native: a `for`-in over a subject whose inherent `next` awaits is emitted without
  `.await`; cargo refuses.
- **F-4** native implements `env` but refuses `scan`, `args`, `exit` and `cwd`.
