#!/usr/bin/env bash
# B382's premise, probed (Order 40, lane papers-40).
#
#   1. `type X = Y;`                      — does the language have it?
#   2. `import … as` / `export import … as` — can a name be re-exported renamed?
#   3. `[deprecated]` on a type            — admitted?
#
# Usage: b382_aliases.sh <worktree> <scratch-dir>
set -uo pipefail

WORKTREE="${1:?usage: b382_aliases.sh <worktree> <scratch>}"
SCRATCH="${2:?usage: b382_aliases.sh <worktree> <scratch>}"
VILAN="$WORKTREE/target/debug/vilan"
DIR="$SCRATCH/b382"
rm -rf "$DIR"
mkdir -p "$DIR/single"

single() {
	printf '%s\n' "$2" > "$DIR/single/probe.vl"
	printf '%-34s ' "$1"
	if ( cd "$DIR/single" && "$VILAN" check probe.vl > probe.log 2>&1 ); then
		echo "ACCEPTED"
	else
		grep -m1 '^Error:' "$DIR/single/probe.log" | cut -c1-110
	fi
}

echo "--- 1. type alias"
single "type X = Y;" 'struct Cursor { at: i32 }
type KeyedCursor = Cursor;
fun main() { let c: KeyedCursor = Cursor { at = 0 }; print(i"{c.at}"); }'

echo "--- 2. import … as"
single "import … as, alias used" 'import std::map::Map as Table;
fun main() { mut t: Table<str, i32> = Table::new(); t.insert("a", 1); print(i"{t.len()}"); }'
single "import … as, ORIGINAL used" 'import std::map::Map as Table;
fun main() { mut t: Map<str, i32> = Map::new(); t.insert("a", 1); print(i"{t.len()}"); }'

echo "--- 3. [deprecated]"
single "on a fun (control)" '[deprecated("use b")]
fun a(): i32 { 1 }
fun b(): i32 { 2 }
fun main() { print(i"{a()}"); }'
single "on a struct" '[deprecated("use Cursor")]
struct OldCursor { at: i32 }
fun main() { let c = OldCursor { at = 0 }; print(i"{c.at}"); }'
single "on an export" 'struct Cursor { at: i32 }
[deprecated("use Cursor")]
export struct Cursor2 { at: i32 }
fun main() { print("x"); }'

echo "--- the deprecation warning a fun DOES get"
( cd "$DIR/single" && printf '%s\n' '[deprecated("use b")]
fun a(): i32 { 1 }
fun b(): i32 { 2 }
fun main() { print(i"{a()}"); }' > probe.vl && "$VILAN" check probe.vl 2>&1 | head -3 )

echo "--- 4. export import … as, across a package, over every item kind"
mkdir -p "$DIR/pkg/src"
cat > "$DIR/pkg/vilan.toml" <<'EOF'
[package]
name = "b382"
target = "node"
prelude = "std::prelude"
EOF
cat > "$DIR/pkg/src/inner.vl" <<'EOF'
export struct DeltaCursor { at: i32 }
export struct Pair<T> {
	left: T,
	right: T,
}
export trait Named {
	fun name(self): str;
}
export enum Side {
	Left,
	Right,
}
export fun make(value: i32): i32 { value + 1 }
EOF
cat > "$DIR/pkg/src/re.vl" <<'EOF'
export import pkg::inner::DeltaCursor as KeyedCursor;
export import pkg::inner::Pair as Duo;
export import pkg::inner::Named as Labelled;
export import pkg::inner::Side as Edge;
export import pkg::inner::make as build;
EOF
cat > "$DIR/pkg/src/main.vl" <<'EOF'
import pkg::re::{ KeyedCursor, Duo, Labelled, Edge, build };
import pkg::inner::DeltaCursor;

// The alias is TRANSPARENT: a `KeyedCursor` value satisfies a `DeltaCursor`
// parameter, so it is a second NAME and not a second type.
fun takes(c: DeltaCursor): i32 { c.at }

// An impl written on the ALIAS, implementing the ALIASED trait.
impl Duo<type T> with Labelled {
	fun name(self): str { "duo" }
}

fun main() {
	let cursor = KeyedCursor { at = 3 };
	print(i"{takes(cursor)}");
	let d: Duo<i32> = Duo { left = 1, right = 2 };
	let side = match Edge::Left { Edge::Left => "L", Edge::Right => "R" };
	print(i"{d.name()} {build(1)} {side}");
}
EOF
( cd "$DIR/pkg" && "$VILAN" run 2>&1 | head -5 )
