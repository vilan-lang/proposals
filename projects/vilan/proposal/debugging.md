# Debugging vilan programs — `dbg`, `dbg_stack`, and a breakpoint debugger (E257)

> Status: **PAPER, drafted 2026-10-03** for the owner to rule on (Q1–Q12).
> Written by lane papers-b-46 of Order 46. Nothing in the compiler, std, kolt or
> the website changed. Every claim about today's behaviour is a probe that was
> run on the installed `vilan 0.43.0 (fe092e8d1)` (JS backend) or a line that
> was read at `next` @7ee822af (`.claude/worktrees/integration`, which has
> native-46 merged). The native backend was **read, not run**: running it
> builds with cargo, and four lanes were building on the machine.
>
> Probes: `scripts/integration/sweeps/order46/papers-b-46/dbg/probes/`, re-run
> by `run_all.sh` (output `run_all.out`), cited as `dN`.
>
> Related: E257 (this item), F68 (print layout across backends; ruled: keep
> node's layout until `dbg` lands), F87 (native tuple printing, fixed on
> native-46), `options.rs`'s debug/release presets, `spec/contexts.md` (hidden
> parameters, the mechanism `[track_caller]` would reuse), `reactive-turns.md`
> and `reactive-layers.md` (what "a reactive turn" is), `opaque-returns.md`,
> `macro-engine.md` (why `dbg` cannot be a macro), `incremental-analysis.md`
> (the sibling paper).

## 0. The ask, and the answer up front

The owner: *"`print` is not great at the moment. Ideally there would be a
`dbg` which accepts any number of values and prints them nicely. Perhaps a
`dbg_stack()` that prints every scoped variable at that location (a sort of
'stack snapshot'). A breakpoint debugger would be useful too."*

**What `print` does today.** It is `console.log` bound to a parameter of type
`any` (`std/src/io.vl:7-8`). So it prints vilan values in their **JavaScript
representation** (d1):

| value | `print` shows |
|---|---|
| `Point { x = 1, y = 2 }` | `[ 1, 2 ]` (field names gone) |
| `Shape::Circle(1.5)`, `Shape::Empty` | `[ 0, 1.5 ]`, `[ 2 ]` (a variant index) |
| `Some(5)`, `None`, `Ok(1)` | `[ 0, 5 ]`, `[ 1 ]`, `[ 0, 1 ]` |
| `(1, "two", 3.0)` | `[ 1, 'two', 3 ]` |
| `3.0` | `3` |
| a `dyn Area` field | `[ [ [ 2, 3 ], {} ] ]` (the value and its method table) |
| `Shared::new(Point {..})` | `{ v: [ 7, 8 ] }` |
| a `SignalCell<i32>` holding 3 | `[ { v: 3 }, { v: [] } ]` (its internals) |
| a closure | `[Function: add]` |
| a `HashMap<str, i32>` | `[ Map(1) { 'one' => [ 'one', 1 ] } ]` |
| a tree four levels deep | `[ 1, [ [ 0, 1 ], [ 1, [Array] ] ] ]` (node's depth cut drops data) |
| a pipe, a `[resource]` struct | refused: "`any` is a data sink" (d1, d9) |

The native backend writes the same bytes on purpose. `vilan-rt/src/inspect.rs`
is a port of node's `util.inspect`, and every type implements a `Js` trait that
renders the JS layout (`vilan-rt/src/lib.rs:75`), so F68's two outputs agree.
The compiler itself already calls this layout wrong. An i-string hole holding
a struct is refused because "concatenating it renders the value's runtime
shape — a struct is a tuple, an enum a tagged array — not the value" (d12).
`print` renders exactly that shape.

`Debug` does not fill the gap. `[derive(Debug)]` gives `Point { x = 1, y = 2 }`
(d2), but only scalars and derived types implement it. A struct with a `List`
or `Option` field cannot derive it, and `T: Debug` refuses lists, tuples and
options (d3, d4).

A panic carries **no location on either backend**: `panic`, `assert` and an
index out of bounds throw a bare string, and node prints the message alone
(d6, d7). There are **no source maps** (no `.map`, no `sourceMappingURL`, d5),
and `vilan run` starts node with no flags (`vilan-cli/src/main.rs:7361`).
Generic functions emit as `$a` even in the readable debug build (d5, d8).

**The answer, in four parts.**

1. **`dbg(a, b, ..)` is a compiler intrinsic**, not a function or a macro. A
   function cannot see its arguments' source text or its call site, and a
   macro runs before types exist (§3.1). It prints each argument as
   `[src/views.vl:42:5] expr = value` to stderr, in **vilan's own literal
   syntax** (`Point { x = 1, y = 2 }`, `Some(5)`, `[1, 2]`, `3.0`). The output
   comes from a type-directed printer the compiler generates, identical on
   both backends. It returns its argument (a tuple for several, unit for
   none). In statement position it reads its arguments in place instead of
   moving them, so `dbg(guard);` does not consume a resource. A release build
   refuses it (§3).
2. **`dbg_stack()`** is the same intrinsic expanded from the scope the
   compiler knows at that point. It covers parameters and locals (shadowed
   ones marked), captures in a closure, a moved binding as
   `<moved at 40:9>`, a view and what it views, a cell by its current value
   read without tracking, and a pipe by its type alone, since sampling would
   start it. The cost is one printer call per binding at that site, and only
   in debug builds (§4).
3. **A breakpoint debugger in stages.** Source maps for the JS backend first
   (names, std on the ignore list, generated code mapped to its attribute).
   Then `vilan run --inspect` and a VS Code launch type that hands off to
   VS Code's own JavaScript debugger. That gives breakpoints and stepping in
   `.vl` files with JS-shaped values. vilan-shaped values come next, from a
   debug-info sidecar read by a small DAP proxy. The same sidecar later
   drives lldb pretty-printers for native, which is last (§5).
4. **`print` adopts the same printer** for non-scalar values once `dbg` has
   shipped. A struct then prints as a struct. Strings and numbers print as
   they do today, so most of the 145 corpus programs' output is unchanged.
   **Reactive introspection** ("who woke this effect") is a debug-build trace
   in `std::reactive` plus async stack tagging, built on one new primitive,
   `[track_caller]`. The same primitive gives panics their location (§6).

**The first slice is S0, and it is small and useful on its own.** Panics,
asserts and index errors report `panicked at src/views.vl:12:5: …` on both
backends, through `[track_caller]`. S1 is `dbg` itself (§9).

## 1. Ground truth on 0.43.0

### 1.1 `print` (d1)

The full output is in `run_all.out`. Beyond the table in §0:

- **Long lists** use node's grouped columns (22 numbers print in four rows).
  F68 was about exactly that, and the ruling keeps it until `dbg` lands.
- **Strings** print raw at the top level and quoted (`'two'`) inside a
  container. That is node's rule.
- **Nested tuples** splice flat (`(1, (2, "x"))` is `[ 1, 2, 'x' ]`). Native
  copies this since F87 (`Js::js_tuple_slots`).
- **`print` takes exactly one argument** (d10: "`print` expects 1 argument,
  but got 2").
- **Resources and pipes cannot be printed at all.** The refusal's advice,
  "debug-print its fields instead", has no tool behind it for a field that
  is itself a list or an option, because `Debug` does not cover those (§1.2).

### 1.2 `Debug` and `.debug()` (d2–d4)

`std/src/debug.vl` defines `trait Debug { fun debug(self): str; }`. Its impls
cover `str`, `bool` and the numeric types, all through `JSON.stringify`
(`:12-35`, `:111-150`). The derive is a prelude macro (`:39-105`) that glues
`self.field.debug()` calls into `"T { a = " + … + " }"`.

- A derived struct and enum print well: `Line { from = Point { x = 1, y = 2 },
  to = Point { x = 3, y = 4 }, label = "di\"ag" }`, `Circle(1.5)`, `Empty`.
- `3.0.debug()` is `"3"`, because `JSON.stringify` drops the `.0`.
- `[derive(Debug)] struct Bag { items: List<i32>, maybe: Option<i32> }` fails
  inside the generated code: "`List<i32>` has no method 'debug'", and the same
  for `Option<i32>`.
- `fun show<T: Debug>(value: T)` refuses `[1, 2]`, `(1, 2)` and `Some(1)`.

So `Debug` is a derive for leaf records, not a way to look at a program's data.

### 1.3 What the emitted JS looks like to a debugger (d5, d8)

```js
function area(self) { return self[0] * self[1]; }
function $a(items) {            // fun total<T: Area>(items: List<T>)
	let sum = 0;
	for (const item of items) { const part = area(item); sum = sum + part; }
	return sum;
}
const points = [ [ 1, 2 ], [ 3, 4 ] ];
const shadow = 1;
const shadow2 = shadow + 1;     // the shadowing `let shadow`
console.log($a(points) + shadow2);
```

A JS debugger stopped here shows `self = [1, 2]`, a function called `$a`, a
local called `shadow2`, and no `main` (its body is the module's top level).
Async functions take hidden context parameters such as `$a` and `$c`
(`incremental-analysis.md` probe i6). Generic functions are named `$a`
because the instance's id has no source name in the naming seed, so
`name_for` falls back to a fresh `$` name (`transformer.rs:13920-13926`). That
is find 2.

### 1.4 Panics (d6, d7)

```js
function __at(list, index) {
	if (index >= 0 && index < list.length) return list[index];
	throw "index out of bounds: the length is " + list.length + " but the index is " + index;
}
```

`panic` and `assert` lower to `throw message`. Node prints:

```text
node:internal/modules/run_main:105
    triggerUncaughtException(
    ^
index out of bounds: the length is 2 but the index is 5
(Use `node --trace-uncaught ...` to show where the exception was thrown)
```

There is no file, no line and no stack, because a thrown string carries none.
Native mirrors node on purpose: the message alone on stderr, exit code 1
(`vilan-rt/src/lib.rs:344-360`, F25). That is find 1.

### 1.5 Source maps, flags, presets

- No source maps exist. `grep` finds no `sourceMappingURL` and no map writer
  in `crates/`. `vilan build` writes no `.map` (d5).
- `vilan run` starts `node <script> <args>` with no inspector or source-map
  flags (`main.rs:7361-7370`).
- The `debug` preset (the default) gives indented output with readable names
  and no const inference. The `release` preset minifies, obfuscates names and
  folds consts (`options.rs:84-100`). A release stack trace therefore names
  nothing, and source maps matter most there.
- The VS Code extension contributes no debugger (`editors/vscode/package.json`).

### 1.6 Variadic and macro-like forms today

- **`print`** is a one-parameter `external fun` taking `any`.
- **`const expr`** is a keyword form. **`Context::new/run/get`** are
  intrinsics: std declares them as `external fun`, and the context pass
  rewrites their call sites away (`std/src/context.vl:9-13`). That is the
  precedent for `dbg`: a std declaration that exists to be typed, with a
  compiler lowering.
- **Macros** (`macro fun`, attributes, `macro {}` blocks) run **before name
  resolution and type checking**, and see one *item* at a time
  (`spec/macros.md` §10.2). They never see an expression's type.
- **Variadic generics** exist over tuple packs, `fun combine<T: (2..)>(sources:
  (U in T: dyn Source<U>))` (`std/src/reactive.vl:2682`), called with one tuple
  argument, `combine((a, b))`. There is no variadic *call*.
- **There is no `{x=}`-style debug hole** in i-strings (d11), and a struct in a
  hole is refused (d12).

## 2. The printer — what "nicely" means

Everything below rests on one new piece: a **type-directed printer** the
compiler generates per type, the same on both backends.

### 2.1 The format

Vilan's own literal syntax, as close to what the user would type as the type
allows:

```text
Point { x = 1, y = 2 }
Shape::Circle(1.5)          Shape::Empty
Some(5)    None    Ok(1)    Err("no")
(1, "two", 3.0)
[1, 2, 3]
HashMap { "one" => 1, "two" => 2 }      HashSet { 1, 2 }
Shared(Point { x = 7, y = 8 })
SignalCell(3)
dyn Area(Point { x = 2, y = 3 })
<closure |i32, i32| -> i32>
<pipe Derive<SignalCell<i32>, i32, i32>>
```

- **Layout:** one line when it fits in 80 columns at its indentation;
  otherwise one entry per line, indented two spaces, with a trailing comma
  (node's break rule, vilan's syntax).
- **Strings** are quoted and escaped as vilan writes them. **Floats** keep
  their `.0` (`3.0`), and integers do not.
- **No depth cut.** Node's depth-2 `[Array]` threw away data in d1.
- **A length cap**: 100 entries, then `… 900 more`.
- **Cycles** (only `Shared` can form one) print `<cycle>`, detected by
  identity during one print.
- **Enum variants** print qualified (`Shape::Circle(..)`), except the
  prelude's `Some`/`None`/`Ok`/`Err`.

### 2.2 How it is generated

- **JS:** one `__show_<Type>` per type that reaches a `dbg`, built from the
  type's layout: field order, variant tags, the dyn table. Generic type
  constructors take their element printers as arguments
  (`__show_List(__show_i32)`), so `List<T>` costs one printer, not one per
  `T`.
- **Native:** a second generated trait beside the existing `Js` impls
  (`vilan-rust/src/lib.rs:2786` for structs, `:2964` for enums), with
  `impl<T: Show> Show for List<T>`. Rust monomorphizes it. The number
  formatting reuses `vilan-rt`'s `js_number` port, so floats agree to the byte.
- **Generic code on JS.** JS does not monomorphize a plain generic (`first`
  is one `$a` for `i32` and `str`, d8). So `dbg(x)` with `x: T` is treated as
  an **implicit bound** every type satisfies, and dispatched like a bound:
  per-instantiation emission, which the transformer already does for
  `T: Area`. The alternative, a runtime type descriptor passed beside every
  generic value, costs every program, not only programs that debug.
- **Customisation.** A type with a written `Debug` impl prints through it. std
  ships impls for its handle types (`Shared`, `SignalCell`, `HashMap`,
  `HashSet`, tasks), so the internals in §0's table never show. Everything
  else is structural.
- **`dyn`.** The method table gains a `show` slot in debug builds, one
  function reference per (trait, type) table. Release builds refuse `dbg` and
  carry no slot.

### 2.3 Size and cost

A printer exists only for a type some `dbg`, `dbg_stack` or (after §6.1)
`print` reaches. Reachability already prunes emission, so a program that never
calls `dbg` pays nothing. The printer's run-time cost is paid only when the
`dbg` line runs.

## 3. `dbg(..)`

### 3.1 Why an intrinsic

Each requirement rules out one of the existing mechanisms:

- `dbg` must print each argument's **source text** and the **call site's
  file:line**. A function receives values, never spans.
- It must print in a **type-directed** way. A `macro fun` runs before types
  exist and sees one item (`spec/macros.md` §10.1–10.2), so it cannot know
  that `x` is a `Point`.
- It must take **any number of arguments of any types**. A mapped tuple pack
  (`T: (1..)`) would make the call `dbg((a, b))`, and still could not see the
  source text.

So, like `Context::run`, std declares `dbg` and `dbg_stack` as `external fun`
in `std::debug`, re-exports them from the prelude, and the compiler owns
their typing and lowering. It is the one place a call takes a variable number
of arguments, and the analyzer's arity check makes one exception for it.

### 3.2 The form

```vilan,fragment
dbg(count);                         // [src/views.vl:42:5] count = 3
dbg(user.name, rows.len());         // two lines, one per argument
let total = dbg(price * qty) + tax; // prints, then yields price * qty
dbg();                              // [src/views.vl:44:5]
```

- **Output:** one line (or block) per argument,
  `[<path>:<line>:<col>] <expr> = <value>`. The expression text is the
  argument's source, whitespace-collapsed. The path is relative to the package
  root.
- **Returns:** the argument for one, a tuple for several, `()` for none.
- **Moves.** In **statement position** (the result unused) the arguments are
  read in place, as views: nothing moves, so `dbg(guard);` leaves the resource
  where it was. In **expression position** a single argument moves through and
  comes back out, so `let g = dbg(make_guard());` owns the guard. Rust's
  `dbg!` always moves, which is its best-known trap; an intrinsic can do
  better because it knows its own position.
- **Stream:** stderr on node, deno, bun and native. The browser has no
  stderr, so it uses `console.log`. `console.error` would show every line as
  a red error with a stack, and `console.debug` is hidden by Chrome's default
  filter.
- **Both backends identical**, byte for byte, gated by `native_differential`
  with stderr compared.

### 3.3 Release builds

Three options:

1. **Keep:** Rust prints in release.
2. **Strip:** `dbg(x)` becomes `x`.
3. **Refuse:** a release build fails with "`dbg` left in a release build",
   and a quick fix removes the call, keeping its argument.

**Rec: refuse (option 3)**, with `[build] dbg = "strip"` or `"keep"` for a
project that wants otherwise. A browser release prints to every user's
console, which leaks data, and stripping silently is how a debugging line
survives for a year. Debug builds (including `vilan test` and `vilan run`)
take it with no warning. The editor marks each `dbg` with a faint hint so a
leftover is visible.

## 4. `dbg_stack()`

### 4.1 What it prints

```text
[src/channel.vl:58:3] dbg_stack() in channel_component
  channel: Channel = Channel { id = 3, name = "general" }
  rows: List<Row> = [Row { id = 1, .. }, Row { id = 2, .. }]
  guard: Guard = <moved at 54:9>
  row: view Row = Row { id = 7, .. }          (a view into rows)
  count: SignalCell<i32> = SignalCell(3)      (read without tracking)
  label: Derive<SignalCell<i32>, i32, str> = <pipe, not sampled>
  x: i32 = 2
  x (shadowed at 51:6): i32 = 1
  on_close: <closure || -> ()> (captured by clone)
```

### 4.2 What the compiler knows, and the rules

The analyzer has the scope chain at the call (`scopes`, `name_to_id_map`), each
binding's resolved type, the move checker's state at that point, the view
checker's invalidation verdicts and the closure capture plan. So `dbg_stack()`
expands statically into one printer call per binding. There is nothing to
look up at run time, and it is the same on both backends.

- **Which bindings:** the function's parameters and every local visible at
  the point, innermost scope first. In a closure, its parameters, its locals,
  then its captures marked as such. Module-level bindings are **not** listed,
  because there are too many and they are not "the stack".
- **Shadowed bindings** are listed under the visible one, marked. JS keeps
  them alive under a renamed identifier (`shadow2`, §1.3). The native emitter
  must keep them addressable in a function containing `dbg_stack`, which means
  renaming there too.
- **Moved:** `<moved at L:C>`. Moved on some paths only: `<moved on some
  paths>`. No value is read in either case.
- **Views:** printed through the view, with what it views. A view the checker
  says may be invalidated at this point (an owner `push` since) prints
  `<view, invalidated by push at L:C>` and is not read.
- **Cells:** `SignalCell` and the other handles print their current value
  through `get()`, which A142 makes the plain, untracked read. A
  `dbg_stack()` inside an effect therefore subscribes to nothing.
- **Pipes:** type only. `sample()` takes `own self` and runs the pipe's
  bodies, so looking would change the program.
- **Liveness:** each listed binding counts as a use at that point. That can
  extend a value's life to the `dbg_stack` line. On native, the worst case is a
  clone where a move used to be. That is honest, and it only exists in debug
  builds, since release refuses `dbg_stack` exactly as it refuses `dbg`.

### 4.3 Cost

One printer call per binding per site, plus the printers (shared with `dbg`).
Inside a generic function on JS, the implicit bound (§2.2) forces
per-instantiation emission of that function. That is the one way a
`dbg_stack` grows code beyond its own site, and it is visible.

## 5. A breakpoint debugger

### 5.1 Source maps for the JS backend (S5)

The transformer builds strings (`transformer.rs`, 14.7k lines, and
`chunks.rs` for bundles). It needs a position-tracking writer: each emitted
statement and expression records (generated line:col → `.vl` file, line:col,
original name). The output is a v3 map per emitted chunk, carrying:

- **`names`**, so `$a` shows as `total`, `shadow2` as `shadow`, and the hidden
  context parameters as generated;
- **`sourcesContent`**, so std's sources come from the map and not from the
  std cache's path;
- **`ignoreList`** (ECMA-426) for std and the runtime helpers (`__at`,
  `__clone`), so "step into" skips the reactive machinery and the user stays
  in their own code;
- **generated code** (a derive's impl, a macro's items) mapped to the
  attribute that produced it. The diagnostics standard already anchors errors
  there.
- **Monomorphized instances:** several JS functions map to one vilan
  function. A breakpoint on the vilan line binds in all of them. Both Chrome
  DevTools and VS Code's JavaScript debugger do this for any map.

`vilan build` writes `.mjs.map` beside its output in the `debug` preset, and
in `release` only when `[build] source-maps = true`. `vilan run` passes
`--enable-source-maps`, so node rewrites `Error.stack` into `.vl` coordinates.
Together with S0's thrown `Error`s, an uncaught panic then prints a vilan
stack.

### 5.2 `vilan run --inspect`, and VS Code (S6)

```text
$ vilan run --inspect-brk src/main.vl
Debugger listening on ws://127.0.0.1:9229/…  (open chrome://inspect, or run "Vilan: Debug" in VS Code)
```

- **The CLI** adds `--inspect`/`--inspect-brk[=port]`, passes them to node
  with `--enable-source-maps`, and for a project runs the node entry, as
  `vilan run` does today.
- **The extension** contributes a `vilan` debug type. Its launch
  configuration resolves to VS Code's built-in JavaScript debugger: `program`
  is the built output, source maps on, `outFiles` the dist directory,
  `skipFiles` the std cache. A pre-launch `vilan build` keeps them in step.
  "Debug" on a `fun main` becomes a code lens.
- **The browser leg:** `vilan run --watch` already serves the bundle, and
  serving the maps beside it lets Chrome DevTools show the `.vl` sources.

What the user gets: breakpoints in `.vl` files, stepping, async call stacks
(vilan async functions are JS async functions), and vilan names. Values are
still JS-shaped: `self = [1, 2]`.

### 5.3 vilan-shaped values in the debugger (S7) — the doors

- **D1. A debug-info sidecar plus a DAP proxy.** `vilan build` writes
  `<chunk>.vdbg.json`. It holds, per function scope, each binding's vilan name,
  generated name and vilan type, and per type, the layout §2.2's printer
  uses. A small DAP adapter (`vilan-dap`) sits between VS Code and node's
  inspector and rewrites the variables and watch panes by static type:
  `[1, 2]` under a binding typed `Point` becomes `Point { x = 1, y = 2 }`,
  expandable by field. The same sidecar is the input for native
  pretty-printers (§5.4). Size L.
- **D2. Type tags in debug builds plus custom formatters.** Debug builds stamp
  each struct and enum value with a hidden type marker, so Chrome's custom
  formatters and the JavaScript debugger's description hooks can name it. It
  is cheaper to build (M), but it changes the debug build's run-time
  representation. Every allocation pays, and `__clone`, equality and HMR's
  transfer would all have to carry the tag. The debug and release builds would
  then differ in more than names, which the presets were designed to avoid.
- **D3. Stay at S6.** JS-shaped values, vilan sources and names. It costs
  nothing more.

**Rec: D3 now, D1 next.** D1 is the only door that also serves native, and it
leaves the runtime alone. The source-map *scopes* proposal in TC39-TG4
(original scopes and bindings carried in the map) is converging on part of
D1's sidecar. If browsers ship it, the sidecar's scope half becomes the
standard field, and only the type layouts stay vilan's own.

### 5.4 Native (S9)

- rustc writes DWARF for the generated `main.rs`, and Rust has no `#line`
  directive, so a debugger shows the generated Rust. Struct fields keep their
  vilan names (`self.{field}`, `vilan-rust/src/lib.rs:2805`), so lldb already
  prints a struct near vilan's shape.
- **Line mapping:** the emitter records a `.vl` span per generated line, and a
  post-build step rewrites the binary's `.debug_line` program to point at the
  `.vl` files (a DWARF writer such as `gimli`'s). Then lldb, gdb and CodeLLDB
  set breakpoints in `.vl` files directly.
- **Pretty-printers:** lldb Python formatters (and gdb's) generated from D1's
  type layouts, for the runtime's own types (lists, strings, cells, maps).
- **Rec:** last. Until then, document "debug the generated Rust with
  CodeLLDB", which works today because native builds are debug by default.

### 5.5 Stepping across reactive turns and async

- **Async** is node's: vilan async functions are JS `async` functions, and the
  inspector's async stack traces chain the awaits. The map's `names` hides
  the generated context parameters.
- **Reactive turns.** A `set` notifies, the turn queues relays, a drain runs
  them at the end of the extent or on a microtask (`std/src/reactive.vl:253-260`,
  `:521`, `:649`), and the effect runs inside the drain. With std on the
  ignore list, "step into" a `set` lands in the next *user* frame that runs,
  which is the effect body if the drain is synchronous. If the drain is on a
  microtask, the effect is a new stack.
- **Linking that new stack to its cause** is what V8's async stack tagging
  API (`console.createTask`) is for. In debug builds std wraps each queued
  relay in a task named after the cell, so Chrome DevTools shows the `set`
  that woke the effect under the effect's frames. Whether node's inspector
  honours it needs a probe in S8. The tracing log (§6.2) works either way.

## 6. What `print` becomes, and reactive introspection

### 6.1 `print` after `dbg`

- **P1. Unchanged.** `print` stays node's `util.inspect`. F68's ruling stands
  forever, structs keep printing as arrays, and `dbg` is the only way to see a
  value.
- **P2. `print` adopts the printer for non-scalar values.** A struct, enum,
  option, tuple, list or map prints in §2.1's syntax. Strings print raw and
  numbers print as `print` prints them today (`3.0` stays `3`, which is
  `Display`'s rule; `dbg` keeps the `.0`, which is `Debug`'s). Scalars still
  lower to `console.log(x)`, so most of the corpus's 1,100 `console.log`
  sites do not move. Only the prints of aggregates change, in `.mjs` and in
  stdout. Resources print through a view, as `dbg` does.
- **P3. `print` requires `Display`.** Clean, but every `print(list)` in every
  program breaks.

**Rec: P2, as its own slice after S1.** A struct printed as `[ 1, 2 ]` is a
bug from the user's side, and the compiler's own i-string refusal already
says why. P2 also closes F68 for good: both backends print the printer's
bytes, and `inspect.rs` retires.

### 6.2 "Who woke this effect"

The reactive graph lives in std (`std::reactive`), so its introspection can
too. It needs one compiler primitive.

- **`[track_caller]` and `std::debug::caller()`.** A function marked
  `[track_caller]` takes a hidden `Location` parameter filled with the static
  call site, the way a context is threaded (`spec/contexts.md` §8.1: hidden
  parameters, compiled away). A call through a function value passes the
  value's own call site. This is Rust's `#[track_caller]`, and it is the
  same mechanism S0 uses for panics.
- **The trace.** In debug builds, `Signal::new` and `set` are
  `[track_caller]`, so a cell knows where it was made and each write knows
  where it came from. `std::reactive::trace(true)` logs each wake:

  ```text
  [reactive] effect at views.vl:30 woken by count (store.vl:12), set at channel.vl:88
  ```

- **The async stack.** The same locations name the `console.createTask` tasks
  in §5.5.
- **Release** builds compile `[track_caller]` on these std functions away and
  `trace` to nothing.

A graph view (a devtools panel listing cells, pipes, effects and their edges)
is a later piece that reads the same records. It is not sliced here.

## 7. Prior art, briefly

- **Rust:** `dbg!` (stderr, file:line, expression text, returns its argument,
  moves it), `{:#?}`, `#[track_caller]`, clippy's `dbg_macro` lint.
- **Swift:** `dump()` prints structure by reflection, and `print` uses
  `CustomStringConvertible`.
- **Kotlin and TypeScript** debug through source maps or JVM debug info into
  the host debugger, which is S5–S6's route.
- **Elm:** `Debug.log` is refused by `elm make --optimize`, which is §3.3's
  recommendation.
- **The source-map scopes proposal** (TC39-TG4): a standard home for part of
  D1's sidecar.

## 8. Finds, for the integrator to file

Written to `sweeps/order46/newitems46-papers-b.json`.

1. **E?1 — a panic carries no location on either backend.** `panic`,
   `assert` and an index out of bounds `throw` a bare string on JS (d6, d7),
   so node prints the message with no file, no line and no stack, and points at
   `node --trace-uncaught`. Native prints the message alone by design (F25).
   Rec: S0, `[track_caller]` on std's panic paths plus a thrown `Error`. Sizing
   S–M.
2. **E?2 — a generic function emits as `$a` in the readable (debug) build.**
   `fun first<T>` becomes `function $a(items)`, and `fun total<T: Area>` the
   same (d5, d8). The instance's id has no source name in the naming seed
   (`transformer.rs:13920-13926`), so every stack trace and every debugger
   shows `$a`. Rec: name instances after their source function (`first`,
   `first2` for a second instance). Sizing XS–S; corpus goldens move.
3. **E?3 — `Debug` covers only scalars and derived types.** `[derive(Debug)]`
   on a struct with a `List` or `Option` field fails inside the generated code
   (d3). `T: Debug` refuses `List`, tuples and `Option` (d4). `3.0.debug()` is
   `"3"`. Rec: fold into this paper's S4 (`Debug` through the printer). Sizing
   S.

## 9. Open questions, each with a recommendation

- **Q1. `dbg`'s output format.** **Rec:** vilan literal syntax, one line when
  it fits 80 columns, else one entry per line; floats keep `.0`; no depth cut;
  100 entries per container; `<cycle>` (§2.1).
- **Q2. What `dbg` returns, and moves.** **Rec:** the argument, a tuple for
  several, `()` for none. In statement position it reads in place; in
  expression position a single argument moves through (§3.2).
- **Q3. The stream.** **Rec:** stderr on node, deno, bun and native;
  `console.log` in the browser (§3.2).
- **Q4. Release builds.** **Rec:** refuse `dbg` and `dbg_stack` with a quick
  fix; `[build] dbg = "strip" | "keep"` to override; no warning in debug
  builds, a faint editor hint instead (§3.3).
- **Q5. `dbg_stack`'s scope.** **Rec:** parameters, locals and captures
  visible at the point, shadowed ones marked; no module bindings; moved,
  invalidated views and pipes shown without a value; cells by untracked
  `get()`; each listed binding counts as a use (§4.2).
- **Q6. Generic `T` on JS.** **Rec:** an implicit bound every type satisfies,
  dispatched like any bound (per-instantiation emission), not a run-time type
  descriptor (§2.2).
- **Q7. `Debug`.** **Rec:** every type is debuggable structurally; a written
  `Debug` impl overrides how `dbg` prints that type; std ships impls for its
  handles; `[derive(Debug)]` keeps compiling and becomes redundant (§2.2,
  find 3).
- **Q8. `print`.** **Rec:** P2, adopting the printer for non-scalars (strings
  and numbers unchanged), as its own slice after `dbg` ships; F68 closes with
  it (§6.1).
- **Q9. Source maps by default.** **Rec:** on in the `debug` preset, opt-in in
  `release` (`[build] source-maps = true`); `vilan run` always passes
  `--enable-source-maps` (§5.1).
- **Q10. How far to take the debugger.** **Rec:** S5 + S6 (maps, `--inspect`,
  a VS Code launch type; JS-shaped values) now; D1's sidecar and proxy (S7)
  next; native (S9) last (§5.3, §5.4).
- **Q11. `[track_caller]`.** **Rec:** add it, with `std::debug::caller()`, as
  the one primitive behind panic locations (S0) and the reactive trace (S8).
  Locations stay in release panics, since they are short strings and the most
  useful part of a production error report (§6.2).
- **Q12. Reactive tracing.** **Rec:** debug builds only;
  `std::reactive::trace(true)` logs each wake with the cell, its creation site
  and the waking `set`'s site; async stack tagging where the host honours it
  (§6.2).

## 10. Slices

| slice | content | size | gate | what exists |
|---|---|---|---|---|
| **S0** | `[track_caller]` + `std::debug::caller()`; std's `panic`, `assert`, index and unwrap paths report `panicked at src/x.vl:L:C: <message>`; JS throws an `Error` (so a stack exists) | S–M | a pin per panic path, both backends (`native_differential` with stderr) | the context pass's hidden parameters; `__at`; `panic_with` |
| **S1** | the printer (§2) for scalars, strings, structs, enums, tuples, `List`, `Option`/`Result`; `dbg(..)` as an intrinsic: variadic, expression text, location, returns, statement reads in place, stderr, release refusal | M | pins per shape and per form; native/JS byte-identical; a release-refusal pin | the `Js` impl generation (`vilan-rust/src/lib.rs:2786`, `:2964`); `Context`'s intrinsic pattern |
| S1b | handles and the rest: std `Debug` impls for `Shared`, `SignalCell`, `HashMap`, `HashSet`, tasks; the dyn table's `show` slot; closures and pipes by type; cycles | S | pins per handle | S1 |
| S2 | `dbg_stack()` | S–M | pins: shadowing, moved, maybe-moved, views (valid and invalidated), captures, cells inside an effect (subscribes to nothing), pipes | the scope table, the move and view checkers, the capture plan |
| S3 | `print` adopts the printer for non-scalars (P2); `inspect.rs` retires; F68 closes | M | corpus goldens regenerated and reviewed; native differential | S1 |
| S4 | `Debug` through the printer: every type debuggable, written impls override, the derive redundant (find 3) | S | pins for d3/d4's cases | S1 |
| S5 | source maps: a position-tracking writer, v3 maps with `names`, `sourcesContent` and `ignoreList`, generated code mapped to its attribute; `--enable-source-maps` in `vilan run`; instance naming (find 2) | M–L | a map-decoding pin per construct (function, closure, mono instance, derive, std frame); an uncaught panic's stack names `.vl` lines | the transformer, `chunks.rs` |
| S6 | `vilan run --inspect[-brk]`; a `vilan` debug type in the extension resolving to VS Code's JavaScript debugger; a "Debug" code lens | S | an extension test for the resolved configuration; a scripted inspector session that hits a `.vl` breakpoint | S5 |
| S7 | D1: the `.vdbg.json` sidecar and `vilan-dap`, values by static type | L | scripted DAP sessions comparing panes against `dbg` output | S1's layouts, S5 |
| S8 | reactive trace (`trace(true)`), cell and set locations via `[track_caller]`, async stack tagging (probe node first) | M | a pin per wake path; trace lines compared | S0 |
| S9 | native: `.debug_line` remapping to `.vl`, lldb/gdb formatters from the sidecar | L | a scripted lldb session | S7 |

**Order.** S0 first: small, useful alone, and it builds the primitive S8
needs. Then S1 + S1b (the owner's `dbg`), then S2, then S3 and S4 together
(both re-point existing output at the printer), then S5 → S6 → S7 → S8 → S9.
S5 can start in parallel with S1 in another lane: they touch different halves
of the transformer.
