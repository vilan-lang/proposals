# A formalized filesystem — handles, atomicity, directories, watch (kolt.local 031)

> Status: PROPOSED 2026-08-26 (cycle 31, work order 13, lane
> `fs-formalization`), for owner review. Design-first, with **one slice
> shipped ahead of the ruling**: `rename` + `write_atomic` + the todo
> example's fix (§10), because that slice has a live data-loss bug behind
> it (§2) and needs no design decision this paper is asking for. Tracker:
> `../projects/kolt.local/tracker/items/031.md`; it should become PROPOSED
> with this paper as its record.
>
> The owner's vision, verbatim (2026-08-26): "the fs api is a little
> undercooked. I'm not sure how this would look exactly, but I have a
> vision of a formalized file system. One where files can be opened, read
> incrementally, read & write atomically, watch, etc. The fs module would
> have a few basic functions for the most common operations and everything
> else would be through the system methods. fs is also missing functions
> for managing directories: read, scan, write, watch, etc."
>
> The owner's principle, also verbatim, which this paper adopts as a
> standing rule (§4): "the idea of sync vs async was supposed to be
> superseded by the async model of Vilan. Calling `async read_bytes` should
> feel sync to the caller (unless they explicitly promise-ify it with the
> `async` keyword) ... sync variants of async operations must be
> justified."
>
> Governing records this paper builds on rather than re-decides:
> `destruction.md` (SHIPPED Tier 1 2026-07-19 — the resource class, `Drop`,
> no public `close()`, `drop(x)` as the early form; Tier 2 §10 still gated
> on the native arc); `platform-coloring.md` §3.1 (a type is colorless;
> color is on code); `async-polymorphism.md` §(closure adaptation — a
> plain, value-returning closure parameter is asyncness-polymorphic);
> `windows-support.md` (case-exact resolution, which path-shaped tooling
> must not undermine). `std-shape.md` is untouched: this is std's process
> layer, not a package candidate.
>
> ~~This paper answers kolt.local **020** (file/directory watch) in §8~~
> **SUPERSEDED by the Q6 ruling, 2026-08-28: 020 owns the whole watch
> surface, shape and mechanism, and §8 is a cross-reference to what it
> shipped.** What this paper contributed and what held is the one
> constraint: the watch resource is designed to MATCH `File`. It does
> **not** answer **017** (path tooling); §9 states the seam. §14 is the
> prior-art assessment — what node's filesystem delivers cleanly and what
> this paper deliberately routes around.
>
> **SHIP NOTE, 2026-08-27 (cycle 33, order 15, lane `fs-writes`, vilan
> b6c72d4f).** S1 AND S2 both shipped, in one commit — twelve functions:
> `write_bytes` (the gap that mattered most; `read_bytes` had shipped and
> `writeFile` stayed bound only at `str`, so bytes could come in and never
> go out), `write_bytes_atomic`, `append`, `copy`, `remove`, `update`,
> `create_dir`, `create_dir_all`, `remove_dir`, `remove_dir_all`,
> `copy_dir`, and `scan_dir` with `Entry`. Thirteen pins, every one
> plant-proved; the binary round trip is asserted over a payload UTF-8
> cannot survive, with the LENGTH checked separately because the 483→853
> favicon was a length symptom. No sync variant was added and none was
> tempting. §11's sequencing for S2 and §10's glue claim were both wrong
> and are struck below. **S3 (the handle) now waits on Q1 alone** — B141,
> its other prerequisite, was fixed in Order 13.
>
> **SHIP NOTE, 2026-08-28 (cycle 35, order 17, lane `fs-handles`, vilan
> d359131b).** S3 SHIPPED WHOLE — the handle tier as §3.2 drew it. `File`
> is a `resource external struct` on the `Database` template, with one
> mechanical divergence §3.2 did not draw: the host's open is a *module
> function*, not a constructor, so there is no extern-new — the five
> constructors are plain associated funs over one raw `open(path, flags)`
> extern, and the flags string stays unspellable from user code.
> Positional `read_at`/`write_at` ride the 4-argument host form
> (`read(buffer, offset, length, position)` — every argument explicit, no
> overload, no version cliff), with the `{ bytesRead }`/`{ bytesWritten }`
> results read through opaque raw structs; handle `stat` returns a bare
> `Stat` (no `Option` — the handle is open, and no TOCTOU window exists
> between probe and act, pinned by unlinking the path under an open handle
> and reading on); `truncate`, `sync`, `data_sync` complete the tier, and
> `sync` closes §5.2's durability gap. Q1 was applied exactly as ruled
> (§5.1's ruling record) and took TWO glue seams: `__fs_close` for the
> destructor, `__fs_close_awaited` for `with_file`. Q2 was built as
> recommended (§12). Q3 was executed, family breaking — and its real
> blast radius was ~20 sites, not §1's three: the consumer census counted
> std and the examples, but the *test tree* had made `exists` its
> canonical `@process` function precisely because it was synchronous —
> nine coloring pins and five e2e probe programs — and the
> module-initializer coloring pins could not migrate to any fs function
> at all (a module-level `let` cannot await, and the module is now async
> end to end), so they stand on `std::process::env` and a module-level
> `Database` now. B141's two broken spellings are pinned POSITIVE (corpus
> `file.vl`, runtime e2e, typing pin) — §11.1 inverted into a gate. The
> Drop wiring and the awaited close were both plant-proved red-first
> (§11.1's and §5's amendments carry the details), and the full workspace
> suite closed at 4433 passed, exit 0.
>
> **Two claims S3 disproved are struck where made**: §5's module-level
> `File` bullet (inexpressible — async constructors × the
> module-initializer rule) and §11.1's clean bill for the chained idiom
> (the value is right; the temporary handle is never closed — a
> pre-existing, `Database`-included gap in temporary-resource teardown,
> recorded there as an owner question, deliberately not fixed en
> passant). One scope note: `with_file` opens read-mode, matching
> §5.1(c)'s sketch; whether writing bodies get scoped forms is left for
> S5's ergonomics pass alongside `Reader`.
>
> **SHIP NOTE, 2026-08-28 (cycle 36, order 18, lane `watch-020`).** S4
> SHIPPED — but from **kolt.local 020**, not from §8: the owner's Q6
> ruling gave 020 the whole watch surface, shape and mechanism, and §8 is
> now a cross-reference to what it built. `Watcher` is `File`'s lifetime
> model entire, which is the one constraint this paper contributed and the
> reason S4 followed S3. Three of §8's specifics were superseded on 020's
> own reasoning — a stat-diffing poll rather than `fs.watch`, a
> three-variant `ChangeKind` rather than the two-variant under-promise,
> and an addressable `Change.path` rather than a relative one — while §8's
> pull shape and its "no ruling needed for teardown" both held, the latter
> for a mechanism §8 did not anticipate (`clearTimeout` is as synchronous
> as `FSWatcher.close()` would have been). The destructor turned out to be
> load-bearing in a way no other resource in this paper is: a pending host
> timer holds node's event loop open, so an undropped watcher is a program
> that never exits — plant-proven as a hang.
>
> **SHIP NOTE, 2026-08-31 (cycle 40, order 22, lane `fs-s5`). S5 SHIPPED,
> and with it the paper's whole sequence: S0–S5 are all built and 031 has
> nothing open.** Two slices in one commit. `Reader` (§3.4) is the
> incremental read the owner's vision named — a cursor over `read_at`, so
> no host position ever enters the tier — and it is twenty lines, which is
> the deferral's dividend: the primitive under it was already right, and
> building the wrapper turned up nothing that would have changed it. Seven
> determinations recorded in §3.4's build note; the sharpest is that the
> `Shared<i53>` position the sketch drew is **forced by the language, not
> chosen** — `next` awaits, and an async function cannot take a `&mut`
> parameter. The second slice closes the scope note S3 left three days
> ago: the four WRITING scoped forms (§5.3), which is where the awaited
> close is actually worth something, since the OS is entitled to report a
> write's failure at `close(2)`. One implementation
> (`scoped_file(own file, body)`), five callers, so the ordering that IS
> the idiom cannot drift; the corpus golden moved by exactly that refactor
> and was regenerated against verified output. Nothing new was needed from
> the compiler: `Reader` is a `resource` by containment and every R-rule
> lands on it unmodified, which is the destruction paper's inference rule
> collecting its second std customer.


## 1. What exists, measured

`vilan/std/src/process/fs.vl` was 135 lines before this lane touched it
(§10): eleven functions and two types. In full, with their sync/async
status:

| Name | Kind | Async? | Notes |
|---|---|---|---|
| `read_file_encoded(path, encoding)` | binding, `node:fs/promises` `readFile` | async | renamed off `read_file_bytes` 2026-08-11 (F13) |
| `read_bytes(path)` | binding, `readFile` with no encoding | async | host `Buffer` *is* a `Uint8Array`, so it binds to `Bytes` with no conversion |
| `write_file(path, contents: str)` | binding, `writeFile` | async | **text only** |
| `exists(path)` | binding, `node:fs` `existsSync` | **sync** | justified in its doc comment as "so boot code can branch on it directly" |
| `read_file_to_str(path)` | plain vilan over `read_file_encoded` | async | |
| `read_dir(path)` | binding, `readdir` | async | names only, no kind, not path-joined, order not guaranteed |
| `read_dir_all(path)` | glue `__fs_read_dir_all` (`{ recursive: true }`) | async | relative paths, host separator, no kind |
| `RawStat` / `Stat` / `stat(path)` | glue `__fs_stat` | async | `Option<Stat>`: `size`, `modified_at_ms`, `is_directory`; ENOENT → `None` by design |
| `read_file_bytes_sync(path, encoding)` | binding, `node:fs` `readFileSync` | **sync** | despite the name, returns `str` |
| `read_file_to_str_sync(path)` | plain vilan over the above | **sync** | |

Eleven functions — and four of them are two operations spelled twice
(`read_file_to_str` over `read_file_encoded`, `read_file_to_str_sync` over
`read_file_bytes_sync`), so the *distinct* capability count is nine.
**Two of the eleven are synchronous.**

**Measured against the owner's sentence, of the seven capabilities named,
one exists, one half-exists, and five are absent.** 031 established this;
reading the file confirms it, and adds two findings the item did not have:

- **There is no binary write at all.** `write_file` is typed
  `(path: str, contents: str)`. `read_bytes` exists, so bytes can come *in*
  and can never go *out*. The host's `writeFile` accepts a `Uint8Array`
  directly — this is a one-line binding that nobody has written, and it is
  the exact mirror of the read that F13 added.
- **`exists` is a second synchronous entry** and nobody has audited it.
  §4 applies the rule to it.

The consumer base is small enough to name entirely — eight call sites
across three files, and one of those files is an example:

```
std/src/process/build.vl:106      fs::exists
std/src/process/build.vl:187      fs::exists
std/src/process/build.vl:194      fs::read_file_to_str_sync
std/src/process/build.vl:229      fs::read_file_to_str_sync
std/src/process/document.vl:604   fs::read_file_to_str
examples/todo/src/store.vl:108    fs::write_file
examples/todo/src/store.vl:116    fs::exists
examples/todo/src/store.vl:117    fs::read_file_to_str
```

Both `read_file_to_str_sync` call sites are `build.vl`'s, and both are
being removed right now by kolt.local 030's lane. **After that lane lands,
`read_file_to_str_sync` has zero callers in the tree.** That is not an
argument for deleting it in this paper — it is 030's to delete — but it is
the fact that makes §4's rule cheap to enforce: there is almost nothing to
grandfather.

## 2. The motivating bug — the todo example loses everything on a crash

031 filed this as "a crash mid-write leaves a torn file". Read against the
code it is worse than that, and the worse version is the one worth
motivating a design with.

`examples/todo/src/store.vl` persists through a subscription:

```vilan
fun persist(list: List<Todo>) {
	match encode(json_codec(), list) {
		Frame::Text(let text) => fs::write_file(storage, text),
		Frame::Binary(let _bytes) => {},
	}
}

fun load(): List<Todo> {
	if fs::exists(storage) {
		let stored: Result<List<Todo>, str> = decode(json_codec(), Frame::Text(fs::read_file_to_str(storage)));
		match stored {
			Ok(let list) => list,
			Err(let _reason) => [],      // <- a corrupt file reads back as empty
		}
	} else {
		[]
	}
}
```

and `boot` wires them:

```vilan
let stored = load();
let store = TodoStore { todos = Signal::new(stored), .. };
let _persisting = store.todos.sub(|list| persist(list));
```

`Signal::sub` calls `observer(self.get())` before it returns
(`std/src/reactive.vl:431` — verified, and the store's own comment says so:
"`sub` fires immediately with the current value, so a first run writes the
file eagerly"). So the failure is a **three-step ratchet**, not a torn file:

1. The process dies partway through `writeFile`. `todos.json` is truncated
   or half-written.
2. Next boot, `decode` fails on the torn JSON, `load` returns `[]` — by
   design, the codec is validating and the comment says "empty (not a
   crash) if the file is corrupt".
3. `sub` fires immediately with that `[]`, `persist` writes `[]` to disk,
   **and the torn file — the only remaining evidence that there was ever
   any data — is overwritten with an empty list.**

The user's todos are gone, silently, with a clean exit code. Every one of
those three steps is defensible in isolation; the composition is a
data-loss bug, and the thing that breaks the chain at step 1 is atomic
replace.

**The toolchain's own Rust already does this, in three separate
subsystems, and vilan code cannot.** Every one of them stages to a
process-namespaced sibling and renames it into place:

- `crates/vilan-embedded-std/src/lib.rs:90-125` (`materialize_into`) — the
  std cache. Its module doc states the invariant outright: "an existing
  directory is complete by construction: the tree is written to a temporary
  sibling and atomically renamed into place".
- `crates/vilan-cli/src/upgrade.rs:447-484` (`install_binaries`) — stages
  each binary as `.{name}.upgrade-{pid}`, then renames over it. "The swap
  is atomic per binary."
- `crates/vilan-core/src/git_dep.rs:244-270` — `.staging-{key}-{pid}`, then
  rename, with the same benign-race handling.

And the corpus harness leans on the property as a correctness argument:
"its temp and cache paths are process-namespaced or **written by atomic
rename**" (`crates/vilan-cli/tests/corpus.rs:410-412`).

Meanwhile `std::fs` exposed no `rename` binding at all, so a vilan program
had no way to express the durability discipline its own compiler relies on
three times over. That asymmetry — the language's implementation being able
to do what the language cannot — is the sharpest single argument for this
whole paper. §10 closes this particular instance of it.

§10 ships the fix.

## 3. The shape: a few free functions, everything else through the handle

The owner's structural sentence is "The fs module would have a few basic
functions for the most common operations and everything else would be
through the system methods." That is a real architectural rule and this
paper takes it literally, which means the free-function tier has an
**admission test**, not just a list:

> **A free function earns its place iff it is a complete operation on a
> path — open, act, close — with no state the caller needs to hold between
> calls.** Anything that needs to be held is a method on the thing that
> holds it.

Read whole file: complete. Replace whole file: complete. Read 64 KiB at
offset 3 GiB: not complete — it needs a handle, so it is a method. This
gives a principled boundary rather than a taste call, and it predicts the
existing surface correctly: everything in `fs.vl` today is a complete
path operation, which is exactly why the module has no types in it.

### 3.1 The free-function tier

Existing, kept as-is:

```vilan
fun read_file_to_str(path: str): str;
fun read_bytes(path: str): Bytes;
fun write_file(path: str, contents: str);
fun stat(path: str): Option<Stat>;
fun read_dir(path: str): List<str>;
fun read_dir_all(path: str): List<str>;
```

Proposed additions, in the order §11 sequences them:

```vilan
// --- shipped in this lane (§10) ---
fun rename(from: str, to: str);                     // node:fs/promises `rename`
fun write_atomic(path: str, contents: str);         // temp sibling + rename

// --- S1: the write gaps. All bindings or plain vilan; no new machinery. ---
fun write_bytes(path: str, contents: Bytes);        // `writeFile`; the missing mirror of `read_bytes`
fun write_bytes_atomic(path: str, contents: Bytes); // the byte twin of `write_atomic`
fun append(path: str, contents: str);               // `appendFile`
fun copy(from: str, to: str);                       // `copyFile`
fun remove(path: str);                              // `unlink`
fun update(path: str, revise: |str| str);           // read → revise → write_atomic

// --- S2: directories (§7) ---
fun scan_dir(path: str): List<Entry>;               // `readdir { withFileTypes: true }`
fun create_dir(path: str);                          // `mkdir`
fun create_dir_all(path: str);                      // `mkdir { recursive: true }`
fun remove_dir(path: str);                          // `rmdir`
fun remove_dir_all(path: str);                      // `rm { recursive: true, force: true }`
fun copy_dir(from: str, to: str);                   // `cp { recursive: true }`
```

Every one of those is async — no keyword at the call site, and none in the
declaration either, since asyncness is inferred from the bindings they
await (§4). `rename`, `write_bytes`, `append`, `copy`, `remove`,
`create_dir` and `remove_dir` are direct
`[extern("node:fs/promises", "…")]` declarations with no host glue.
`create_dir_all`, `remove_dir_all`, `copy_dir` and `scan_dir` each need an
options object, which the extern binding forms cannot spell — they ride
the `__fs_*` glue seam that `__fs_stat` and `__fs_read_dir_all` already
established in `transformer.rs`.

Sixteen free functions all told. That is more than "a few", and the paper
should say why it is still the right cut: **twelve of the sixteen are the
same two verbs (read, write) crossed with the four nouns the host
distinguishes (text, bytes, file, directory).** The surface is wide because
the host's is; it is not deep, and none of it holds state.

### 3.2 The handle tier

```vilan
/// An open file. A `resource`: it moves rather than copies, and its `Drop`
/// closes the underlying host handle at the owner's scope end.
resource external struct File;

impl File {
	fun open(path: str): File;             // "r"  — read, must exist
	fun create(path: str): File;           // "w"  — create or truncate
	fun create_new(path: str): File;       // "wx" — create, FAIL if it exists
	fun append_to(path: str): File;        // "a"
	fun modify(path: str): File;           // "r+" — read/write, must exist

	/// Reads into `buffer` starting at byte `position`; returns the number of
	/// bytes actually read, `0` at end of file. Short reads are normal and
	/// are not an error.
	fun read_at(&self, buffer: Bytes, position: i53): i32;

	/// Writes `buffer` at byte `position`; returns the number written.
	fun write_at(&self, buffer: Bytes, position: i53): i32;

	fun stat(&self): Stat;
	fun truncate(&self, length: i53);

	/// Flushes this file's data and metadata to the storage device — the
	/// durability primitive (`fsync`). Nothing else in std can do this.
	fun sync(&self);
	fun data_sync(&self);                  // `fdatasync` — data only
}

impl File with Drop {
	fun drop(&mut self);                   // §5
}
```

Three design calls are embedded there and each is argued below: **the modes
are named constructors, not a flags string** (§3.3); **reads are positional,
not cursored** (§3.4); and **there is no `close()`** (§5).

### 3.3 Modes are constructors, not a flags string

Node spells modes as a string: `open(path, "wx")`. Binding that directly
would be one function instead of five, and it would be wrong here. `"wx"`
is an untyped, unvalidated, unmemorable enum with eleven members whose
failure mode is a runtime `EINVAL`; a typo in it is a typo the compiler
cannot see. Five named constructors are five entries in a doc page, each
of which says in its name what it does to a file that already exists —
which is the only thing anyone ever needs to look up.

`create_new` is deliberately in the v1 set and not deferred: it is
**"write atomically" on its second reading**. `write_atomic` (§10) makes a
replace atomic; `create_new` makes a *creation* exclusive, which is how
one process claims a name without racing another. Between them they cover
both meanings of the word that a JS runtime can actually deliver — see the
non-goal on locking (§9).

### 3.4 Reads are positional; a cursor is a wrapper, not a primitive

Node's `FileHandle.read` maintains an internal file position when the
caller passes `null` for `position`. Binding that as the primitive would
put **hidden mutable state behind a `&self` loan**: two loans of the same
`File`, each calling `read`, would silently interleave and each would
observe the other's position moves. That is the aliasing hazard rule 4
exists to talk about, expressed in a place where rule 4 cannot see it
(the state lives in host code).

So the primitive is positional and stateless, and the cursor — which is
genuinely what most callers want — becomes an ordinary vilan value layered
on top, whose position is a field the move checker *can* see:

```vilan
resource struct Reader {
	file: File,          // containment: `Reader` is a resource by inference,
	position: Shared<i53>,  //  and needs no modifier of its own (destruction.md §3)
}

impl Reader {
	fun of(file: own File): Reader;
	/// The next `size` bytes, shorter at the end, empty at EOF.
	fun next(&self, size: i32): Bytes;
}
```

This is the shape `fetch.vl`'s `BodyReader` already established for HTTP
bodies (`read_chunk()` → `ChunkResult { done, value }`), and 031's Q2 asked
whether to mirror it. The answer this paper recommends is: **mirror the
ergonomics, not the mechanism.** `BodyReader` is cursored because a
`ReadableStream` has no addressable positions; a file does, and throwing
that away at the primitive layer would make `read_at` unreachable forever.
Build the cursor from the position, never the position from the cursor.

`Reader` is v1.5, not v1 (§11) — the primitive is the thing that must be
right first, and a cursor written a cycle later costs nothing.

**BUILT 2026-08-31 (S5, cycle 40, Order 22, lane `fs-s5`).** The sketch
above shipped; the shipped surface, which the sketch's signatures
approximate rather than state, is:

```vilan
resource struct Reader {
	file: File,
	cursor: Shared<i53>,
}

impl Reader {
	fun of(own file: File): Reader;
	fun next(self, size: i32): Bytes;   // empty at EOF
	fun position(self): i53;
	fun seek(self, position: i53);
}
```

The seven determinations the sketch left open are recorded below, each
with the evidence that settled it. Two of them were decided by the
language rather than by taste, which is the more interesting half.

**(i) The position is a `Shared<i53>`, and that is FORCED, not chosen.**
The sketch wrote `position: Shared<i53>` beside `fun next(&self, …)`
without saying why the obvious shape — a plain `i53` field behind
`&mut self` — was not used. Probed at build time: it does not compile.
`next` awaits the read, and **an async function cannot take a `&mut`
parameter** ("the view would be held across its suspension points"),
which is a standing rule already pinned in
`crates/vilan-core/tests/inference/bounds.rs`. A `Shared` cell is what the
language leaves, so the sketch was right for a reason it did not know it
had. Re-pinned in the Reader's own shape as
`a_cursor_method_that_awaits_cannot_take_a_mut_view`.

This is worth reading twice, because it looks at first like the very
hazard the section above rejects — mutable state reached through a
non-exclusive loan. It is not the same thing, and the difference is the
whole design: the host's cursor is state **the move checker cannot see**,
living in host code under an opaque handle; this cursor is an ordinary
vilan field, **named, readable (`position()`), writable (`seek()`), and
carried by a value that moves**. The hazard was never mutation; it was
mutation that no rule and no reader could observe.

**(ii) `next` returns `Bytes`, empty at EOF — no `ChunkResult` twin.**
Mirroring `BodyReader`'s *ergonomics* means the pull loop, and mirroring
its *mechanism* would have meant a two-field result. `BodyReader` needs
`{ done, value }` because a `ReadableStream` may legitimately yield an
empty chunk mid-stream, so emptiness cannot carry the end there. A file's
read cannot: `read_at` answers `0` only at or past the end. So the
emptiness IS the signal, and a `finished()` field would be one the caller
could always derive. The doc comment states the one trap this leaves —
**stop on empty, not on short** — since a short chunk is not a promise
that the next one is empty.

**(iii) Each `next` allocates and slices; chunks do not alias.** A chunk
is `buffer.slice(0, count)` off a buffer minted for that call, so a chunk
is never a window on memory the next call overwrites. The alternative —
one reused buffer, handed out repeatedly — is faster and is a trap in a
language with no lifetimes on `Bytes`. A caller who wants the reuse has
`read_at` directly, which is exactly what the primitive is for.

**(iv) The cursor is visible in both directions: `position()` and
`seek()`.** One line each, and they are what makes (i)'s argument
checkable rather than rhetorical — the host cursor this replaces cannot
be read at all. Seeking past the end is not an error; the next read is
empty.

**(v) Cursored and positional reads interleave, deliberately.** `Reader`'s
fields are reachable as **loans**, so `reader.file.read_at(buffer, p)`
reads any part of the file without disturbing the cursor — the property
the host's hidden position would have destroyed, now demonstrable in one
program. R5 keeps the door one-way: the `File` cannot be moved out of a
live `Reader` (`cannot move a resource field out of a live aggregate`).
Pinned both ways — the loan compiles, the move is refused — and the
interleave itself is pinned against a real file and plant-proven.

**(vi) No `Reader::open(path)` convenience.**
`Reader::of(File::open(path))` is the spelling, and composing the two
names says WHICH constructor opened the file — a reader over a `modify`
handle is as legitimate as one over an `open` handle, and a single-name
form would have to pick `"r"` silently. The composition also exercises
the temporary rule in its good direction: the temporary is **moved** into
an `own` parameter, so `temporary-drop.md`'s statement-end close does not
fire (verified on the emitted bytes and at runtime — the reader reads
fine on the following statement).

**(vii) No `Writer`, and no `with_reader`.** A write cursor would be
state with nothing to hold: `File::append_to`'s handle IS the sequential
writer, because the host ignores position on it, and every other write is
positional by choice. And the scoped form exists so that a close
*failure* is observable (§5.3); a `Reader` never writes, so its `Drop`'s
fire-and-forget close loses nothing a caller could act on. (`with_file`'s
body receives its file as a loan in any case, and `Reader::of` needs an
owned one — so a `with_reader` would have had to be a separate opener
rather than a composition.)

`Reader` is a `resource` **by containment** (destruction.md §3), which
buys the whole R-rule surface with nothing declared: it moves, a closure
cannot capture it, no `List`/`Map`/`Set` holds it, and its scope-end
teardown reaches through the plain struct into the `File` it owns —
`drop(reader)` is the early form. All four pinned on the real type, and
the teardown pinned at runtime against `/proc/self/fd`.

## 4. The rule: sync variants must name the caller that cannot suspend

**Stated as a rule, for this surface and any future one:**

> A synchronous variant of an asynchronous operation is admitted only with
> a **named caller in the tree that structurally cannot suspend** — named
> in the doc comment, at the call site, in a form a later reader can go and
> check. "Boot code", "a callback", "the hot path" are not names. If the
> named caller is removed, the sync variant goes with it.

The rule is enforceable because vilan's async model is real and
implemented, not aspirational: a caller writes no keyword, no `Task` or
`Promise` enters their type, asyncness propagates by inference to `main`,
and **there is no way to declare a function synchronous, so there is no
call-from-sync refusal to work around.** The usual justification for a sync
variant in other languages — "my caller is sync and cannot await" — is
therefore not a thing that can be true in vilan by accident. It can only be
true structurally.

**And exactly one structure makes it true: a module-level binding
initializer, which cannot await.** That is the one hard rule in the model,
and it is therefore the one shape that can ever satisfy the test:

```vilan
let config = fs::read_file_to_str_sync("config.json");   // module scope: cannot await
```

**No code in the tree is that shape today.** Which yields the paper's
sharpest sentence about the existing surface: *at the moment of writing, of
the two synchronous entries in `std::fs`, zero are justified.*

### 4.1 The cautionary tale (kolt.local 030)

`read_file_to_str_sync` carries this justification in `fs.vl`:

> "It exists because a synchronous request handler has no other option, and
> `serve_build`'s dev-mode revalidation is exactly that."

That named caller **did not exist**. `Server.request_handler` is declared
`async |Request| Response`; `on_request` takes an async handler; the
emitted node callback is `async (req, res) => { … await … }` and already
awaits `read_request_bytes` twice before a byte is written. The claim was
already untrue the day it was written — the handler channel went async
2026-07-13, the sync read arrived 2026-08-11 — and `http.vl` carried the
same false sentence in a second file. **Fifteen days, two files, three
adversarial checks to dislodge it.**

The lesson this paper takes is not "someone was careless". It is that the
justification was *unfalsifiable as written*: "a synchronous request
handler" names a category, and a category is never wrong, it is only
unfindable. The rule above demands a name precisely because a name can be
looked up and found missing in one grep.

### 4.2 The rule applied to what exists

- **`read_file_to_str_sync` / `read_file_bytes_sync`** — justification
  false (030). Both call sites are being deleted by 030's lane; after it
  lands the function has zero callers. **Deleting it is 030's lane's call,
  not this paper's**, and this paper takes no position beyond: it cannot be
  re-justified except by a module-level initializer, and there is none.
- **`exists`** — bound to `existsSync`, justified as "so boot code can
  branch on it directly". *That is a category, not a name*, and it fails
  the rule by the same test that caught 030. Its three call sites
  (`build.vl:106`, `build.vl:187`, `store.vl:116`) are all inside async
  functions on paths that already await. **Recommendation:** `exists`
  becomes async, bound over `fs/promises.access` or expressed as
  `stat(path).is_some()` — at which point it is arguably not needed at
  all, since `stat` answers strictly more. Flagged here for 030's sweep
  rather than actioned, since that lane owns the file.
- **Everything this paper proposes is async.** No entry above has a sync
  twin, and none is requested.

### 4.3 The one thing the rule must not become

A rule that forbids sync variants outright would be wrong, and this one
does not. If a module-level `let` genuinely needs a file at load time, the
sync read is the *only* expressible answer and the rule admits it — with
that binding named. The rule is about evidence, not prohibition.

## 5. The handle's lifetime — and the one hard problem in this paper

`Database` is the template and this paper follows it exactly
(`std/src/process/db.vl`, `destruction.md` §9):

```vilan
resource external struct File;                 // `resource` REQUIRED at leaves:
                                               //  an external struct is opaque, so a
                                               //  host-object resource must say so itself

/// Closes the underlying host handle — the one host operation with no public
/// surface. Reachable only from `File`'s `Drop`, so a handle closes exactly
/// once, at teardown. There is no public `close()` to fall out of sync with
/// the destructor; `drop(file)` is the early form.
[extern("__fs_close")]
external fun close_handle(file: File): void;

impl File with Drop {
	fun drop(&mut self) {
		close_handle(self);
	}
}
```

**No public `close()`, ever.** This is not stylistic. `destruction.md` §5:
"No public `close()` surfaces to keep in sync with destructors, no
double-close states." A public `close()` on a value that also has a
destructor is a second teardown path the type system cannot see, and the
double-close bug is exactly what the `resource` class was built to make
unrepresentable. `drop(file)` — a move into std's `fun drop<T>(own value: T) {}`
— is early teardown, and it is a move, so the binding is dead afterwards
and R1 rejects any later use. The user-visible ergonomics are *better* than
`close()`: you cannot forget it, and you cannot do it twice.

What the rest of `destruction.md` buys, unmodified, the moment `File` is a
resource:

- **R1** — `let b = a` moves; a stale handle is a compile error, not a
  `EBADF` at runtime.
- **R3** — `own file` is a move and *only* a move (a data `own` argument
  silently copies at non-last-use; a resource one errors).
- **R5** — a `File` field is loan-only; moving it out of a live aggregate
  is rejected. `Option::take` is the sanctioned partial move, which is how
  `Reader` (§3.4) would ever release its file early.
- **R7** — no conditional moves: `let f = open(); if c { consume(f); }` is
  an error, so scope-end ownership stays static and no runtime drop flags
  are needed.
- ~~**Module-level `File` never drops** and is **loan-only** — process
  lifetime, the serve-forever idiom, exactly `Database`'s.~~ **DISPROVED
  BY S3 (2026-08-28): a module-level `File` is inexpressible.** Every
  constructor is async (`fsPromises.open` is), and a module-level
  initializer cannot await — §J.3, the model's one hard rule, the same
  rule §4 of this paper leans on. `Database` escapes only because
  `node:sqlite`'s open is synchronous. The serve-forever handle is a
  LOCAL in `main` instead: owning across awaits is legal, and a `main`
  that never returns never drops it. Pinned
  (`a_module_level_file_initializer_is_refused_for_awaiting`), and the
  docs teach the `main`-local idiom.
- **Across `await`** — owning a `File` across a suspension is legal; frames
  own their locals. This matters a great deal here, since every method on
  the handle suspends.

And two constraints that shape the surface, both worth stating because they
are not obvious:

- **R9 — a closure cannot capture a resource.** So no `fs` API may be
  callback-shaped over an open handle. This is half of what decides the
  watch tier's pull shape (§8), and it is why `update(path, |str| str)`
  (§3.1) takes a *path* rather than a handle.
- **R10 — `List`/`Map`/`Set` reject resource type arguments in v1.** There
  is no `List<File>`. `Option<File>` is the sanctioned container. A program
  that wants a pool of open files cannot have one until R10's recorded
  v1.5 (move-in/view-out containers) lands. **This should be said out loud
  in the docs entry for `File`**, because "open several files" is an
  ordinary thing to want and the diagnostic will otherwise read as
  arbitrary.

### 5.1 The hard problem: `drop` is synchronous and `FileHandle.close()` is not

`destruction.md` §5, unambiguous: **"`drop` is synchronous in v1.** An
`async`/awaiting drop body is rejected … Async-drop is unsolved in Rust for
good reasons; not v1's fight."

`Database` satisfies this by luck of its host: `node:sqlite`'s
`DatabaseSync.close()` *is* synchronous. **`node:fs/promises`'s
`FileHandle.close()` is not** — it returns a promise. So `File` is the
first resource in std whose host teardown is asynchronous, and this paper
cannot ship the handle without the owner ruling on it. Three options, with
a recommendation:

**(a) Fire-and-forget the async close from `drop`.** `__fs_close` calls
`handle.close()` and does not await it, attaching a rejection handler so
the failure is reported rather than crashing the process as an unhandled
rejection. Honest reading of what this costs:

- *Correctness of already-written data: unaffected.* `FileHandle` does not
  buffer in user space — a `write()` that has resolved has already been
  handed to the OS. `close()` releases the descriptor; it does not flush a
  vilan-side buffer. So there is no window in which acknowledged data is
  lost. (Durability against power loss is `sync()`'s job and always was —
  §5.2.)
- *Process exit: unaffected.* The pending close keeps a handle on node's
  event loop, so the runtime does not exit before it completes.
- *What is actually lost:* the close's **error** is not observable by the
  program, and the descriptor's release is not observable either — a
  program that drops a handle and immediately unlinks or re-opens the path
  is racing the close. On POSIX that race is benign; on Windows it is not
  (a file with an open handle cannot always be renamed or deleted), which
  makes this a `windows-support.md`-adjacent honesty note rather than a
  free lunch.

**(b) Build `File` over raw descriptors instead**, `node:fs`'s
`openSync`/`closeSync`, so `drop` is genuinely synchronous. Rejected: it
buys a synchronous teardown by making every *open* synchronous too — the
node promises API is `FileHandle`-based and has no free-function positional
read on a bare fd — so each read would need hand-promisified callback glue,
and the whole surface would block the event loop at exactly the moments the
async model exists to avoid. Trading the correct thing for the incidental
one.

**(c) Provide a scoped form as the primary idiom** and let `Drop` be the
safety net rather than the main path:

```vilan
/// Opens `path`, runs `body` with the file, and closes it — awaiting the
/// close, so a failure to close is a failure of `with_file`.
fun with_file<T>(path: str, body: |&File| T): T;
```

This is well-founded and not a hack: `async-polymorphism.md` settled that
**a plain, value-returning closure parameter is asyncness-polymorphic** —
the instance goes async when the argument closure is, so `with_file`
genuinely awaits an awaiting body. (The contrast is instructive:
`Signal::sub`'s observer is `|T| void`, a *void* channel, which is why
persistence in §2 is fire-and-forget. Value-returning is the whole
difference.) And R9 does not bite, because the file arrives as a
**parameter**, not a capture — `destruction.md` R9 says so explicitly for
injected bodies: "parameters are per-call, not captures".

**Recommendation: (a) and (c) together.** `File::open` + `Drop` is the
model, matching `Database` and keeping the no-public-`close()` law intact;
`with_file` is the *documented* idiom, and is the only spelling in which a
close error is observable. That is the same division `Database` would have
made if `node:sqlite` had forced the question. This is **Open question
Q1** (§12) — it is the one call this paper cannot make for the owner,
because it decides whether `drop`'s synchronicity is a v1 simplification or
a law.

**RULED 2026-08-27, BUILT 2026-08-28 (S3).** The owner: "Do (a)+(c) but
don't make this a general rule; just apply it for File." Exactly the
recommendation, with its scope cut to the narrowest form: `File`'s `drop`
initiates the close without awaiting it, `with_file` is the documented
idiom whose close IS awaited, `Drop` is the safety net — and
destruction.md's "drop is synchronous in v1" is NOT reopened as a general
law. The deeper question was declined rather than answered; the next
resource with asynchronous host teardown argues its own case.
Mechanically the ruling took two glue seams, not one: `__fs_close`
(drop's fire-and-forget, the rejection routed to stderr) and
`__fs_close_awaited` (`with_file`'s awaited close — an awaited close with
no public method surface cannot be spelled binding-side). The destructor
still runs behind `with_file` and re-enters `close()`; benign, because
the host close is idempotent (probed before building on it).

### 5.2 `sync()` is the durability primitive and it only exists on a handle

Nothing in `std::fs` today can call `fsync`, and nothing can once §10's
`write_atomic` ships either: node exposes fsync only as
`FileHandle.sync()`. This is worth stating plainly because it bounds what
§10 claims. `write_atomic` gives **atomicity** — no reader ever observes a
half-written file, and a crash leaves either the old file or the new one.
It does not give **durability** — after a power loss the rename may not
have reached the platter, and the honest guarantee needs `fsync` on the
file *and* on the containing directory. Full durability is therefore a
capability that **only the handle tier can deliver**, which is one more
reason handles are the real work and §10 is the cheap part.

### 5.3 The scoped form is a family, one per constructor

**Written 2026-08-31 (S5), because S3 shipped `with_file` read-only and
the section above never said what the other four modes get.** §5.1's
ruling gave the tier one scoped form, over `File::open`. That was the
right first slice and the wrong resting place, for a reason the ruling's
own honesty note contains: the awaited close exists so that a close
*failure* is observable — and **a close failure is information almost
exclusively on a writing handle.**

That is not a stylistic claim. A write that has resolved was handed to
the OS, but the OS is entitled to report its failure at close time rather
than at write time: a full disk, an exceeded quota, a network filesystem
that defers the error to `close(2)` (NFS is the classic case, and it is
why POSIX says a program that ignores `close`'s return value may lose
data it believes it wrote). Under the destructor that error goes to
stderr — §5.1's honest cost, accepted — and the program carries on
believing it wrote. So the tier shipped with the awaited close available
in exactly the mode where it matters least.

The family, one per constructor:

```vilan
fun with_file<T>(path: str, body: |File| T): T;             // File::open
fun with_file_create<T>(path: str, body: |File| T): T;      // File::create
fun with_file_create_new<T>(path: str, body: |File| T): T;  // File::create_new
fun with_file_append<T>(path: str, body: |File| T): T;      // File::append_to
fun with_file_modify<T>(path: str, body: |File| T): T;      // File::modify
```

Four determinations, recorded:

**(a) Five named forms, not one form with a mode argument.** §3.3's
argument against node's flags string does not stop at the constructor
tier: a mode is an untyped enum whose typo the compiler cannot see, and
threading one through `with_file` would reintroduce exactly what the five
constructors exist to prevent. The suffix IS the constructor.

**(b) They earn their place by the tier's own admission test (§3).** Each
is a complete operation on a path — open, act, close — holding no state
the caller needs between calls. Q5's ruling ("the sixteen stand") is not
disturbed: this is the same test applied, not an exception to it.

**(c) The names are stem-first, `with_file_<constructor>`.** House style
across this module puts the stem first and the qualifier after
(`read_dir`/`read_dir_all`, `write_bytes`/`write_bytes_atomic`), which
groups the family in a doc page and in a completion list. `create_new`
keeps its full name rather than being prettified, because a name that
does not match its constructor is a name a reader has to look up twice.

**(d) One implementation, five callers.** The close-before-return
ordering IS the idiom, so it is written once — a private
`scoped_file(own file: File, body)` the five forms delegate to — rather
than five times, where a later addition could quietly drop the `await`.
The emitted shape is `try { body; await close; return } finally { drop }`,
so a throwing body still releases the handle through the safety net, and
the existing emission pin (`with_file_awaits_the_close_before_returning`)
covers all five by covering the one. The corpus golden `file.mjs` moved
by exactly that refactor and was regenerated against verified output.

What this does NOT change: the destructor is still the safety net and
still fire-and-forget, `close_awaited` is still not a public `close()`
(it is a free function the completion list never offers on a `File`), and
Q1's ruling is still scoped to `File` alone.

## 6. Platform coloring

All of this is `@process`. `std/vilan.toml` declares the layer
(`[library.layer.process] platform = ["@process"]`), so every function
defined in `std/src/process/fs.vl` is seeded `@process` by definition site
and propagates into its callers by the existing fixpoint. Nothing new is
needed, and the handle does not disturb it:

- **A type is colorless** (`platform-coloring.md` §3.1). `resource external
  struct File` may be *named* anywhere — a struct field, a signature — and
  a browser build that names it is legal. Color flows only through the way
  to *obtain* one, and every constructor (`File::open`, …) is `@process`.
  So a browser-reachable path can never hold a `File`, exactly as it can
  never hold a `Db`.
- **The implicit `Drop` edge cannot widen color, and the argument is
  one line**: to drop a `File` you must own a `File`, and to own one you
  must have called a `@process` constructor. Every owner of a `File` is
  therefore already `@process` before the destructor edge is considered.
  This holds for `Database` today and is the reason nobody has had to think
  about it; it is worth writing down once, here, since `File` is the second
  instance and there will be more.
- **`with_file`'s closure** colors by the creator rule (§3.2): a
  `@process` closure literal marks the function that creates it. Correct
  and unremarkable — the caller was already `@process` for having called
  `with_file`.

**The browser story is that there is none, deliberately.** Browsers do have
filesystems now — the Origin Private File System and the File System Access
API, both handle-shaped, both async, one of them permission-prompted. A
future `std::browser::opfs` could plausibly borrow this paper's *shape*.
It must not borrow this paper's *module*: the security models are not the
same (a page asks a human for permission; a process does not), the failure
modes are not the same, and a shared name would promise a portability that
cannot exist. `std::fs` is `@process` and stays there. Recorded as a
non-goal (§9), not as an omission.

## 7. Directories

The owner named four verbs — "read, scan, write, watch". Read exists, scan
half-exists, write is absent, watch is §8.

**`read` vs `scan` is a real distinction and the surface should keep it.**
`read_dir` answers "what names are in here" and is one host call.
`scan_dir` answers "what *is* each of these", and today costs a `stat` per
entry — the doc comment says so ("a caller that needs to know file
vs. directory calls `stat` per entry"), which for a thousand-entry
directory is a thousand extra syscalls to recover information the host
already had and threw away. `readdir { withFileTypes: true }` returns
`Dirent`s carrying the kind for free.

```vilan
/// One directory entry with its kind — the information `read_dir` discards.
struct Entry {
	name: str,
	is_directory: bool,
	is_file: bool,
	is_symlink: bool,
}

fun scan_dir(path: str): List<Entry>;
```

Three booleans rather than an enum, deliberately: a host dirent can be a
FIFO, a socket, a block or character device or an unknown, and an enum
would either enumerate all nine — five of which no vilan program will ever
meet — or need a catch-all variant that means "one of five things I did not
model". Booleans answer the three questions anyone asks and stay honest
about not being exhaustive. (If the owner prefers an enum, it is Q4.)

`is_symlink` is in the struct despite symlinks being a non-goal elsewhere
(§9): a *scan* that silently reports a symlink as a file is how recursive
walkers end up in loops, and the cost of telling the truth here is one
boolean.

The remaining directory verbs are the free functions listed in §3.1:
`create_dir` / `create_dir_all` / `remove_dir` / `remove_dir_all` /
`copy_dir`, plus `rename` (shipped) which is "move" for directories as
well as files. All five ride the `__fs_*` glue seam for their options
objects except `create_dir` and `remove_dir`, which are direct bindings.

**Not proposed: a directory handle.** The free-function test (§3.3) rules
it out — every directory operation is a complete path operation, and node
exposes `opendir()`/`Dir` only as a lazily-iterating cursor whose sole
advantage over `readdir` is memory on directories with millions of entries.
That is a real use case for a backup tool and not one for anything vilan
targets. Recorded as a v2 shape, not designed here.

## 8. Watch — see kolt.local 020

> **Q6 RULED 2026-08-28 (the owner): "Make 020 own the watch surface."**
> Shape AND mechanism both. This section had absorbed 020's shape question
> while leaving it the mechanism; it is now a cross-reference. The sketch
> it carried is in the repository history, and where the shipped tier
> diverges from it, the shipped tier is right.

**SHIPPED 2026-08-28 (cycle 36, Order 18, lane `watch-020`)** as S4, from
020. `std::fs` has `Watcher` — a `resource external struct` carrying §5's
lifetime model entire (it moves, no closure captures it, no `List` holds
it, release reachable only from `Drop`, no public `stop()`) — plus
`Change { path, kind }`, `ChangeKind { Created, Modified, Removed }`,
`Watcher::watch` / `Watcher::watch_all` (`read_dir` / `read_dir_all`'s
reach), and a pull-shaped `next()`. The surface and its reasoning live in
`vilan/docs/std/process.md` and in `std/src/process/fs.vl`'s own comments.

What this paper contributed and what held: **the watch resource is
designed to MATCH `File`**, which is why S4 was sequenced after S3. Four
notes for a reader who arrives here first:

- **The mechanism is a stat-diffing poll** at the compiler's own 300 ms
  (`watch-mode.md`), not `node:fs`'s `watch`. 020's standing argument won,
  and this section's "the surface is mechanism-agnostic" claim is what made
  that free.
- **`ChangeKind` has three variants, not the two sketched here.** Two was
  an under-promise calibrated to what `fs.watch` can distinguish; a poller
  tells creation from modification from removal on every platform, so
  under-promising would have been a loss rather than honesty. A rename
  arrives as `Removed` plus `Created`.
- **`Change.path` is addressable, not relative** — the watched root joined
  with the entry, ready for `read_file_to_str`. (`read_dir`'s bare names
  serve callers who want the name; a change's caller wants to act on it,
  and a single-file watch has no meaningful relative form.)
- **Q1's exception is not inherited, and this section's reason survived the
  mechanism change**: `clearTimeout` is synchronous, as `FSWatcher.close()`
  would have been. The destructor is load-bearing for a different reason —
  a pending host timer holds the event loop open, so an undropped watcher
  is a program that never exits.

The pull shape argued here stands, with the argument sharpened: R9 rules
out a handler holding a `File` open across events, and — the half this
section did not name — a `|Change| void` observer is a *void* channel, so
`async-polymorphism.md` makes it fire-and-forget, unable to await the read
of the file it was just told about.

## 9. Non-goals

Stated explicitly so that each is a decision with a reason rather than a
hole someone finds later.

- **File locking.** Node cannot do advisory locking (`flock`) without a
  native addon, and the userland substitutes (lockfiles via exclusive
  `mkdir` or `O_EXCL` create) are a *policy* with retry, staleness and
  ownership semantics — a package, not a std primitive. What std gives
  instead is the two atomic operations the OS actually provides:
  `write_atomic` (atomic replace) and `create_new` (exclusive create), out
  of which a lockfile package can be built correctly.
- **Streams and backpressure.** `createReadStream`/`createWriteStream` are
  the right tool for piping gigabytes, and binding them means designing a
  stream abstraction for std — which is its own paper, would want to serve
  HTTP bodies and `fetch.vl`'s `BodyReader` too, and should not be invented
  as a side effect of a filesystem design. Positional reads (§3.4) cover
  incremental access without it.
- **Path manipulation.** join/basename/dirname/normalize/resolve are
  kolt.local **017**, deliberately not here. The seam: **this paper
  produces and consumes plain `str` paths and takes no position on a `Path`
  type.** If 017 later mints one, every signature above accepts it by
  whatever conversion 017 designs; nothing here forecloses it. Note that
  `read_dir`'s doc comment already names a module that does not exist
  ("join with `path` yourself"), which is 017's problem, not this paper's
  to fix.
- **Permissions, ownership, timestamps.** `chmod`/`chown`/`utimes` — zero
  demand in the tree or in kolt, and `windows-support.md`'s world makes
  POSIX mode bits a lie half the time. Bind them when something needs them.
- **Symlink creation and resolution.** `symlink`/`readlink`/`realpath`
  omitted for the same reason, with the same trigger. `scan_dir` *reports*
  symlinks (§7) because a walker that cannot see them is dangerous; it does
  not follow or create them.
- **A virtual/in-memory filesystem for tests.** Tempting and out of scope:
  it is an abstraction over this surface, belongs to whoever owns testing
  ergonomics, and designing it now would distort the primitives to be
  mockable rather than to be right.
- **A browser filesystem.** §6 — OPFS and the File System Access API exist,
  and are a different security model wearing similar shapes. Not this
  module, possibly a future `std::browser` one.
- **Anything requiring a native addon**: `mmap`, `sendfile`, `io_uring`,
  extended attributes, file change journals. Out of reach of a
  JS-targeting language by construction, and worth saying once so it is
  not re-proposed.

## 10. What this lane shipped

**Commit `f82f72aa`** on branch `fs-formalization` (off `next`), full
workspace suite green at the end: 4232 passed, 0 failed, 6 skipped.

One slice, shipped ahead of the ruling because it needs no ruling: it uses
only primitives that already exist plus one binding, it fixes a live
data-loss bug (§2), and nothing in §12's open questions changes its shape.

**`std/src/process/fs.vl`** — additive, one new section placed between
`read_file_to_str` and `read_dir`, deliberately far from the sync block at
the file's tail that kolt.local 030's lane is editing concurrently:

```vilan
/// Renames (moves) `from` to `to`, replacing `to` if it exists. Within one
/// filesystem this is atomic: a reader of `to` sees either the old file or
/// the new one, never a mix. ACROSS filesystems the host raises `EXDEV` —
/// so `write_atomic` below keeps its temporary a sibling of its target.
[extern("node:fs/promises", "rename")]
async external fun rename(from: str, to: str): void;

/// Writes `contents` to `path` atomically: to a uniquely-named sibling
/// first, then `rename` over the target. A crash at any point leaves either
/// the previous file or the complete new one — never the truncated
/// half-write a plain `write_file` leaves, which is what silently loses a
/// JSON store on the next boot that reads it back.
///
/// Atomic, NOT durable: after a power loss the rename may not have reached
/// the device. Durability needs `fsync`, which node exposes only on an open
/// file handle — see `proposal/filesystem.md` §5.2.
///
/// The temporary is a sibling (a rename across filesystems is not atomic
/// and would fail) and is uniquely named (concurrent writers must not share
/// one), so a crash can leave a `.<uuid>.tmp` file behind. That is the
/// correct trade: a stray temporary is recoverable, a torn target is not.
fun write_atomic(path: str, contents: str) {
	let temporary = i"{path}.{random_uuid()}.tmp";
	write_file(temporary, contents);
	rename(temporary, path);
}
```

`random_uuid` is `std::crypto`'s existing binding to `crypto.randomUUID`
(base layer, so available under `@process`); the import is the only other
line the file gains.

**`examples/todo/src/store.vl`** — one call changed, `fs::write_file` →
`fs::write_atomic`, with the comment above `persist` rewritten to name the
three-step ratchet rather than the one-step version. §2's failure is closed
at its first step.

**Four files, and `transformer.rs` is not one of them.** The precedent
commit for a `std::fs` addition (`read_dir_all`, b49eda85) touched five,
because its `{ recursive: true }` option object had to be spelled as host
glue. Nothing here needs glue: `rename` is a direct
`[extern("node:fs/promises", "rename")]` binding, which lowers to a named
import and a bare call with no registry entry, and `write_atomic` is plain
vilan over `write_file` and `rename`. So the concurrently-edited
`transformer.rs` is untouched, and so is every other lane's file.

| File | Change |
|---|---|
| `vilan/std/src/process/fs.vl` | +33: the `rename` binding, `write_atomic`, the `random_uuid` import |
| `crates/vilan-cli/tests/fs.rs` | +127: four pins |
| `vilan/docs/std/process.md` | +19: two signature lines and the "One write that cannot tear" paragraph |
| `CHANGELOG.md` | +5: one `family: feature` entry under `## Unreleased` |

The uniqueness source is `std::crypto`'s existing `random_uuid`
(`[extern("crypto.randomUUID")]`, base layer, so reachable under
`@process`). It is a deliberate choice over the simpler `<path>.tmp`: two
concurrent writers sharing one temporary would corrupt each other's
replace, which is the failure this function exists to prevent, and the
toolchain's own Rust namespaces its staging paths by pid for exactly this
reason. The cost is that a crashed run strands a `.tmp` sibling, since
`vilan` has no `try`/`catch` to remove it — stated in the doc comment.

The four pins: creation, replacement (asserting from Rust that the target's
directory holds exactly one file afterwards, so a stranded temporary fails
the test), the throwing posture when the target's directory is missing
(which also pins that the temporary is a *sibling* and not a system temp
file), and `rename`'s two halves — the source stops existing and an
occupied destination is replaced. That last one is not incidental: an
overwriting rename is the entire reason temp-sibling-plus-rename *is* an
atomic replace.

**One thing this lane deliberately did NOT fix**, because another lane owns
it: `vilan/docs/std/process.md` still repeats the false sync justification
— "the sync one exists for a read that must complete inside a callback that
cannot suspend — `serve_build`'s dev-mode revalidation is the case it was
added for". That is a **third** copy of the sentence 030 found in `fs.vl`
and `http.vl`, in a file 030's lane has no other reason to open, and it
should die in the same sweep rather than in this commit. Flagged here so it
is not missed; not touched.

## 11. Sequencing — what is v1

The paper should be honest about the shape of the work, which is lopsided:
**the handle is most of the design and most of the risk; everything else is
bindings.**

- **S0 — atomic write. SHIPPED (§10).** One binding, five lines of vilan,
  one example fixed, a live data-loss bug closed. No design decision.
- **S1 — the write gaps.** `write_bytes`, `write_bytes_atomic`, `append`,
  `copy`, `remove`, `update`. All direct bindings or plain vilan over them.
  No new machinery, no glue, no ruling needed. `write_bytes` in particular
  is a one-line binding closing an asymmetry that has been open since F13
  added `read_bytes`. **Do this next regardless of what the owner rules
  below.**
- **S2 — directories** (§7). `scan_dir` + `Entry`, `create_dir(_all)`,
  `remove_dir(_all)`, `copy_dir`. ~~Needs option-object glue at the existing
  `__fs_*` seam — mechanical, but it touches `transformer.rs`, so it wants
  a lane of its own rather than a corner of another.~~ **CORRECTED
  2026-08-27 (Order 15, lane fs-writes): this prediction was FALSE, and the
  lane disproved it with a scratch probe against the real host before
  building on it.** An options object needs no glue: `[extern("Object")]`
  mints a fresh `{}` and `[extern(set, …)]` fills it in — both forms
  already existed, and `std::fetch` has been building `RequestInit` this
  way all along. So S2 touches `transformer.rs` not at all, wanted no lane
  of its own, and **SHIPPED in S1's commit**.
- **S3 — the handle** (§3.2, §5). `File`, the five constructors, positional
  read/write, `stat`, `truncate`, `sync`, the `Drop` ruling, `with_file`.
  ~~**Gated on Q1** (§12), and **blocked on B141** (below).~~ This is the big
  piece and it unlocks incremental reads, durability, and TOCTOU-free
  read-then-act. **SHIPPED WHOLE 2026-08-28 (cycle 35, Order 17, lane
  `fs-handles`) — see the ship note at the top.** Q1 was ruled 2026-08-27
  ((a)+(c), `File`-scoped; §5.1's ruling record); B141 had been fixed in
  Order 13, and §11.1's argument now runs inverted — its two broken
  spellings ride S3 as positive gates.
- ~~**S4 — watch** (§8). `Watcher` as a resource, answering 020.~~
  **SHIPPED 2026-08-28 (cycle 36, Order 18, lane `watch-020`)**, and from
  020 rather than from §8 — the owner's Q6 ruling gave 020 the whole
  surface, shape and mechanism. The sequencing argument held exactly as
  written: S4 followed S3 so the two resources are designed to match
  rather than converge later, and `Watcher` is `File`'s lifetime model
  entire.
- ~~**S5 — incremental-read ergonomics.** `Reader` (§3.4), and only once S3
  is real. Deferred deliberately: a cursor over a wrong primitive is worse
  than no cursor.~~ **SHIPPED 2026-08-31 (cycle 40, Order 22, lane
  `fs-s5`)**, and the deferral paid: the cursor is a twenty-line wrapper
  because the primitive under it was right, and building it turned up
  nothing that would have changed `read_at`. It carried the slice §5.1
  left unfinished as well — the four WRITING scoped forms (§5.3), where
  the awaited close is the half that matters. Determinations recorded in
  §3.4's build note (seven) and §5.3 (four). **With this the paper's
  sequencing is complete: S0–S5 all shipped, and 031 has nothing open.**

### 11.1 A hard prerequisite the handle tier has, which nothing else does

**Backlog B141 blocks S3.** A field or method access directly off an
implicitly-awaited call reads the *promise*, not the value —
`read_bytes(p).len()` compiles clean, exits 0, and evaluates to
`undefined`. It is live in released toolchains (verified on 0.36.0 and on
`next`), it is silent, and binding the result to a `let` first is always
correct, which is why std and the corpus have never tripped over it.

A handle API is *made of* the broken spelling:

```vilan
File::open(path).read_at(buffer, 0)     // method off an async call -> undefined, silently
File::open(path).stat().size            // twice over
```

Every other slice in this paper is free functions returning values that
callers bind. S3 is the first surface whose *intended idiom* is the exact
shape B141 mis-compiles, and shipping it before the fix would hand users a
type-checked API that returns `undefined` in its most natural spelling.
**B141 is therefore not "a bug we should also fix" — it is S3's
prerequisite**, and this paper recommends it be sequenced as one.

**GATE INVERTED AT SHIP (2026-08-28).** B141 was fixed in Order 13, and
S3 pins both spellings above POSITIVE — a corpus golden
(`vilan/test/file.vl`), a runtime e2e that prints the read count and the
size, and a typing pin. One honesty note the fix does not cover, found
while generating that golden: the chained spelling's temporary handle is
never CLOSED. The drop planner tracks *bindings*, and a resource born and
consumed as an expression temporary is neither dropped nor rejected — on
`File` and `Database` alike (verified: `Database::open(":memory:").exec(…)`
emits no close at all). The value is right; the handle leaks until
process exit, and `Drop`'s safety net does not reach it. Whether the
lifted temporary should drop at scope end, drop at statement end, or be
rejected outright is a destruction-semantics call this paper does not own
and leaves to the owner — flagged in the ship note, deliberately not
"fixed" en passant.

> **NOTE RETIRED 2026-08-29.** The owner ruled statement-end
> (`temporary-drop.md`, closed; built as the special case of
> `lifetimes.md` §6's last-use rule, since a temporary's last use IS its
> statement). `File::open(p).read_at(b, 0)`'s receiver is now lifted to a
> minted `const` and closed in a `finally` at that statement's end, on
> `File` and `Database` alike; `vilan/test/file.mjs`'s golden grew the
> `finally`s with its runtime output unchanged, and the fd staircase is a
> permanent e2e (`crates/vilan-cli/tests/fs.rs`) reading back to baseline
> where the leak read +1, +2 and +7. The tier's intended idiom no longer
> leaks, and this paper's honesty note has nothing left to be honest
> about.

## 12. Open questions for the owner

Each is answerable on its own; none blocks S1 or S2.

- **Q1 — `drop` is synchronous; `FileHandle.close()` is not. Which gives?**
  (§5.1.) The options are (a) `drop` initiates the close without awaiting
  it — data already written is safe, the close *error* is unobservable, and
  a drop-then-rename race is benign on POSIX and not on Windows; (b) build
  the handle on raw synchronous descriptors, blocking the event loop at
  every open (recommended against); (c) make the scoped `with_file(path,
  |file| …)` the documented idiom, where the close *is* awaited, with `Drop`
  as the safety net. **Recommendation: (a) + (c).** The deeper question the
  owner is really being asked: is `destruction.md`'s "drop is synchronous
  in v1" a simplification that async teardown may later revisit, or a law?
  `File` is the first resource in std to put weight on the answer.
  **RULED 2026-08-27: (a)+(c), scoped to `File` only — §5.1's ruling
  record. The deeper question was deliberately left open.**
- **Q2 — incremental reads: positional primitive, or cursored?** (§3.4.)
  Recommendation: positional `read_at`/`write_at` as the primitive, with a
  `Reader` wrapper deferred to S5 — because a cursor can be built from a
  position and a position cannot be recovered from a cursor, and node's
  implicit-position mode would put hidden mutable state behind a `&self`
  loan. **BUILT AS RECOMMENDED 2026-08-28 (S3): the positional pair
  shipped (4-argument host form, offset and length explicit); `Reader`
  stays S5. The recommendation is load-bearing surface now rather than a
  pending question. CLOSED WHOLE 2026-08-31 (S5): the `Reader` shipped
  too, over `read_at` exactly as recommended, and the build confirmed the
  order mattered — see §3.4's build note.**
- **Q3 — does `exists` survive?** (§4.2.) It is a synchronous binding whose
  justification is a category ("boot code"), all three of its callers are
  already async, and `stat(path).is_some()` answers strictly more. Delete
  it, make it async, or keep it with a named module-level caller. This
  overlaps 030's sync sweep and should probably be ruled there; it is
  raised here because the rule in §4 is what condemns it. **RULED
  2026-08-27: DELETED, family breaking — executed in S3's commit. The
  real blast radius is recorded in the ship note: ~20 sites, because the
  test tree had made `exists` its canonical `@process` function precisely
  for its syncness.**
- **Q4 — `Entry`'s kind: three booleans or an enum?** (§7.) Recommendation:
  booleans, because a host dirent has nine kinds and an enum must either
  model five nobody will meet or carry a catch-all that means "one of
  five things I did not model".
- **Q5 — is the free-function tier still "a few"?** (§3.1.) Sixteen names
  at S2, which is more than the vision's word. The defence is that twelve
  of them are two verbs crossed with four nouns the host distinguishes, and
  that none of them holds state. If the owner wants a genuinely small tier,
  the cut is to drop the `_all` recursive directory variants and the
  `_atomic` byte twin and let callers compose — at the cost of the
  composition being wrong in ways `{ recursive: true }` is not. **RULED
  2026-08-27: the sixteen stand ("That's fine"). No cuts.**
- **Q6 — does this paper's name and scope stand?** It is proposed as
  `proposal/filesystem.md` (subject-named, like `markdown.md` and
  `destruction.md`; `fs.md` reads as a module note rather than a design).
  It also absorbs 020's *shape* question while leaving 020 its mechanism
  question — confirm that is the right division, or say 020 should own the
  whole watch surface and §8 should shrink to a cross-reference.
  **RULED 2026-08-28: the name and scope stand, but 020 owns the watch
  surface whole — shape AND mechanism. §8 is now a cross-reference (it
  shrank when S4 shipped, Order 18), and the tier it points at is 020's
  design: a stat-polling `Watcher` with a three-variant `ChangeKind`.
  The one constraint this paper contributed carried: the watch resource
  matches `File`.**

## 13. What this paper does not change

- **`stat`'s error posture stays as designed.** ENOENT → `None`, everything
  else throws. `fs.vl`'s header explains why (a prober asking "is this here
  yet" wants an answer, not an exception) and dev-refresh.md's mtime poller
  is the motivating customer. Every new function above keeps the *other*
  posture — throw host-side on any failure — because that is what the rest
  of the module already promises and a split posture per-function would be
  worse than either posture consistently.
- **The `__fs_*` glue seam stays the seam.** ~~Options objects that the
  extern forms cannot spell go through `transformer.rs`, exactly as
  `__fs_stat` and `__fs_read_dir_all` already do.~~ **CORRECTED 2026-08-27
  (Order 15): the extern forms CAN spell an options object** —
  `[extern("Object")]` plus `[extern(set, …)]`, the `RequestInit` route
  `std::fetch` already uses. Four of this paper's functions took it and
  the compiler was untouched, which leaves `__fs_read_dir_all` as the odd
  one out rather than the precedent; it could be retired the same way by
  whoever is next in that file for another reason. This paper still
  proposes no new mechanism for host interop and needs none — it simply
  named the wrong existing one.
- **std vs packages.** `std-shape.md` is untouched: the filesystem is
  process-layer std, not a package candidate. Nothing here is a
  registry-shaped question.

## 14. Prior art — node's filesystem, honestly assessed

The host is `node:fs` / `node:fs/promises` (and its Deno and Bun
compat surfaces — `std/vilan.toml`'s process layer covers all three with
one set of `node:` bindings). This section records what a JS-targeting
language can take from it cleanly and what is a trap, since several of the
decisions above are decisions *against* node rather than for it.

**Takes cleanly, and this paper takes them:**

- **`FileHandle` as the handle.** `fsPromises.open()` returns an object
  with `read`, `write`, `stat`, `truncate`, `sync`, `datasync`, `close`,
  `readFile`, `writeFile`. It is genuinely the right abstraction and maps
  onto a `resource external struct` with no impedance — this is the same
  interop `Database` already relies on for `node:sqlite`.
- **`rename` as atomic replace.** Overwrites the destination, atomic within
  a filesystem, `EXDEV` across one. Node exposes exactly the POSIX
  semantics and nothing is lost in translation. §10 ships it.
- **`readdir { withFileTypes: true }` → `Dirent`.** The kind comes back for
  free, which is the whole of §7's `scan_dir`.
- **`{ recursive: true }` on `mkdir`, `rm`, `cp`, `readdir`.** Ordinary,
  well-specified, already precedented in std by `read_dir_all`'s glue.
- **Positional `read`/`write` on a handle.** `read(buffer, offset, length,
  position)` is the POSIX `pread`/`pwrite` shape and is what §3.4 binds.

**Traps, each of which this paper routes around rather than inherits:**

- **The flags string.** `open(path, "wx")` is an eleven-member untyped enum
  whose failure mode is a runtime `EINVAL`. §3.3 replaces it with named
  constructors. This is the clearest case where binding node faithfully
  would be binding node badly.
- **`read`'s implicit position.** Passing `null` for `position` makes the
  handle stateful, which §3.4 rejects: hidden mutable state behind a
  `&self` loan is invisible to rule 4 because it lives in host code.
- **`FileHandle.close()` is async.** §5.1 — the one genuinely hard problem
  in this paper, and it is entirely node's doing. Note that the JS
  ecosystem's own answer is `await using` / `Symbol.asyncDispose`, which
  `FileHandle` implements: that is *asynchronous destruction*, precisely
  what `destruction.md` §5 declines for v1. The languages disagree, and Q1
  asks the owner which way vilan resolves it.
- **`fs.watch`.** The least portable thing node exposes. Events coalesce
  and also duplicate; `"rename"` covers create, delete and rename with no
  way to distinguish them without a `stat`; recursive watching is not
  universally available; macOS can report a null filename; and inode-based
  watching loses the file when an editor saves by write-temp-then-rename —
  which §10 has now taught vilan programs to do too. **This is the one
  prior-art bullet the shipped tier declines outright**: 020's
  stat-polling argument won (§8), so none of this list is inherited — the
  poller distinguishes creation, modification and removal on every
  platform, and a watch may start on a path that does not exist yet, which
  `fs.watch` cannot do at all. What polling costs instead is stated at the
  surface: interval latency, blindness to a change that cancels itself out
  inside one interval, and one `stat` per watched entry per interval.
- **Streams vs handle reads.** `createReadStream` is the right tool for
  piping gigabytes with backpressure and the wrong thing to bind
  piecemeal — §9 makes it a non-goal pending a std stream story that would
  serve `fetch.vl`'s `BodyReader` too.
- **No advisory locking.** `flock` is not reachable without a native addon,
  and every userland substitute is a policy with staleness and ownership
  semantics. §9 declines it and points at `create_new` (exclusive create)
  as the primitive a lockfile package would actually be built from.
- **`existsSync` as an ergonomic trap.** It is the one fs call people reach
  for by habit, it is synchronous, and it is a TOCTOU race in every
  read-then-act use. Q3 asks whether it survives at all; `stat` answers
  strictly more, and a handle answers it without the race.

**Not node, but worth naming:** Deno's `FsFile` closes *synchronously* and
implements `Symbol.dispose` rather than `asyncDispose` — so the same
program shape that forces §5.1's question on node would not force it on
Deno. Since std's process layer serves all three runtimes through one set
of `node:` bindings, vilan takes node's constraint. That is a cost of the
portability choice, and it is the right cost; it is recorded here so the
constraint is not mistaken for a law of filesystems.
