### Breaking changes, and what to change

Every breaking entry below, one line each with its migration, so the list is whole even where the release page is cut short. "Net-zero": the earlier shape never shipped in v0.40.0.

#### Language

- A bare trait at a struct field is refused: write `dyn Trait`, or the concrete type if the field needs an inherent method.
- `Self<i32>` is refused: write the type's name (`Cell<i32>`).
- An explicit type argument outranks an argument that knows less: drop the arguments or make them agree.
- `lazy` is a keyword: rename any name spelled `lazy`.
- A type's method namespace is per importing file: pick between two extending imports with a selector; an `impl` in a module with curated exports needs `export impl`.
- A type segment replaces an import path's namespace: reach a module member at its module.
- Importing an unexported item warns: import the exported name, or mark the reach (`{ #hidden }`).
- `export (helper);` and `export * helper;` are refused: `export` takes an item or an import.
- The right operand of a generic-bounded operator is checked: use one type, or bound `P: Add<Q>`.
- A condition typed by a generic parameter is refused: pass a `bool`.
- A `::` path may not cross a line break: join the line, or `import a::b::c as d;`.
- A negated capture in a `for` condition or `match` guard is refused: bind after the test.
- An `is` capture is in scope only where its test passed: read it in the then-branch or after `&&`.
- An operator trait's method is required at impl time: implement it.
- `fun main` takes no parameters: read `std::process::args()`.
- An operator on a generic left operand needs a bound: `<T: Add>` (`Sub`, `PartialEq`, `PartialOrd` likewise).
- `resource struct`/`resource enum` are `[resource] struct`/`[resource] enum`; the old spelling is refused, naming the new.
- Net-zero: a file's platform is `[platform("browser")] mod self;`, not a bare `[platform(..)];`.

#### Standard library

- Every std length, position and count is `usize`, and `list[i]` takes one: convert with `.as_usize()`/`.as_i32()` (the quick fix inserts them); a `-1` sentinel becomes `None`; count down with `for i > 0 { i -= 1; … }`. A negative `.as_usize()` is 0; `std::fs` offsets stay `i53`; a `usize` in an rpc signature moves its contract hash (rebuild both halves); frames do not change.
- `std::random::range` is `[low, high)`: for the old range, `range(low, high + 1)`.
- `unwrap_or`/`expect` on `Option` and `Result` take their argument `lazy`: hoist a fallback whose side effect must run.
- The six `View` parent methods are gone: `parent.swap(s, r)` is `parent.child(swap(s, r))`, `bind_each*` is `each*`; the quick fix rewrites them.
- std curates its exports: reaching an unexported item warns; use the documented name.

#### Reactive

- `map`, `switch`, `combine`, `flatten` and `and_then` return cold nodes, not `SignalCell`s: drop the `SignalCell<U>` annotation, or add `.cell()` where a cached cell is wanted; a `Source`-typed parameter takes a node unchanged. `.cell()` in a module binding's initializer is refused: build it under an owner, or write `.cell_global()`. The rpc mirrors lose their own `map`. `Resource<T>`'s constructor is ``source.load(fetch)``.
- Keyed `each*` and `reconcile` need `K: PartialEq + Hashable`: `[derive(Hashable)]`, or an `impl` hashing the fields `eq` reads.
- `Source::on_change` is the requirement, `sub` derived: rename an impl's `fun sub` to `fun on_change`, dropping its immediate call.
- `Optimistic<T>` is `Optimistic<T, S: Signal<T>>`: write the second parameter where the type is spelled.
- Net-zero: `KeyedCursor` is `DeltaCursor` (`KeyedCell` is new in this release).

#### Style

- A `css` block's declarations are calls: `property(value);`.
- Conditions are values: `not(inner)` is `cond.not()`; `within(name, value, inner)` is `.on(within(attribute(name).eq(value)), inner)`; `child_relation` is deleted (its steer names the replacement).
- Deprecated for one release: `Style::attribute`/`within`'s value form; write `.on(attribute(name).eq(value), inner)`, or `.on(attribute(name), inner)` for presence.
- Net-zero: `std::style::prelude` is new; its 46 names are the designed ones.

#### rpc and the wire

- The Wire visitor's receivers are `&mut`: a hand `impl … with Wire` takes `&mut S` / `&mut D`; `[derive(Wire)]` needs nothing.
- `[derive(Wire)]` emits only the wire codec: write `[derive(Json, Wire)]` to keep the JSON pair.
- An `[rpc]` method returning a source has a sync stub answering `RemoteSource<T>`: drop the `!` and the unwrap; read `status()` for errors.
- Net-zero: an awaited `void` stub answers `Result<void, RpcError>`.

#### Tooling

- `[doc(hidden)]` is refused: delete it; an unexported item is what it promised.
