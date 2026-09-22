#!/usr/bin/env bash
# I5's literal-inference census (Order 40, lane papers-40).
#
# B370 (Order 39) ruled that an unsuffixed literal takes its type FROM CONTEXT
# everywhere, and closed the two positions where it did not. I5's S1 depends on
# that law holding for the type an index will be: every `list[0]`,
# `take(3)`, `let n = 0` in the estate must land on `usize` without a suffix.
#
# `usize` does not exist yet, so the probe uses `u53` — what `usize` IS on the
# JS targets under the owner's ruling 1 — as the stand-in. Each position is its
# own file, checked on its own, so one failure cannot mask another.
#
# Usage: i5_literal_positions.sh <worktree> <scratch-dir>
set -euo pipefail

WORKTREE="${1:?usage: i5_literal_positions.sh <worktree> <scratch>}"
SCRATCH="${2:?usage: i5_literal_positions.sh <worktree> <scratch>}"
VILAN="$WORKTREE/target/debug/vilan"
DIR="$SCRATCH/literals"
rm -rf "$DIR"
mkdir -p "$DIR"

case_number=0
check() {
	local name="$1"
	local body="$2"
	case_number=$((case_number + 1))
	local file="$DIR/case_${case_number}_${name}.vl"
	printf '%s\n' "$body" > "$file"
	if ( cd "$DIR" && "$VILAN" check "$(basename "$file")" > "$file.log" 2>&1 ); then
		printf 'PASS\t%s\n' "$name"
	else
		printf 'FAIL\t%s\t%s\n' "$name" "$(grep -m1 '^Error:' "$file.log" | cut -c1-110)"
	fi
}

PRELUDE='fun take(count: u53): u53 { count }
struct Holder { at: u53 }
'

check argument            "$PRELUDE"'fun main() { let _ = take(3); }'
check annotated_let       "$PRELUDE"'fun main() { let n: u53 = 0; let _ = take(n); }'
check binary_right        "$PRELUDE"'fun main() { let n: u53 = 4; let _ = take(n + 1); }'
check binary_left         "$PRELUDE"'fun main() { let n: u53 = 4; let _ = take(1 + n); }'
check list_elements       "$PRELUDE"'fun main() { let xs: List<u53> = [0, 1, 2]; let _ = xs.len(); }'
check struct_field        "$PRELUDE"'fun main() { let h = Holder { at = 0 }; let _ = take(h.at); }'
check return_position     "$PRELUDE"'fun zero(): u53 { 0 }
fun main() { let _ = take(zero()); }'
check comparison          "$PRELUDE"'fun main() { let n: u53 = 4; if n > 0 { print("yes"); } }'
check compound_assign     "$PRELUDE"'fun main() { mut n: u53 = 4; n -= 1; let _ = take(n); }'
check match_literal       "$PRELUDE"'fun main() { let n: u53 = 4; match n { 0 => print("zero"), _ => print("more") } }'
check tuple_element       "$PRELUDE"'fun main() { let pair: (u53, str) = (0, "a"); let _ = take(pair.0); }'
check closure_parameter   "$PRELUDE"'fun main() { let f = |n: u53| take(n); let _ = f(7); }'
check generic_call        "$PRELUDE"'fun identity<T>(value: T): T { value }
fun main() { let n: u53 = identity(5); let _ = take(n); }'
check bare_let_then_use   "$PRELUDE"'fun main() { let n = 0; let _ = take(n); }'
check option_some         "$PRELUDE"'fun main() { let found: Option<u53> = Some(0); match found { Some(let n) => { let _ = take(n); }, None => {} } }'
check list_index_literal  "$PRELUDE"'fun main() { let xs: List<str> = ["a", "b"]; print(xs[0]); }'
check list_index_u53      "$PRELUDE"'fun main() { let xs: List<str> = ["a", "b"]; let i: u53 = 0; print(xs[i]); }'
check list_get_u53        "$PRELUDE"'fun main() { let xs: List<str> = ["a", "b"]; let i: u53 = 0; match xs.get(i) { Some(let s) => print(s), None => {} } }'
check len_into_u53        "$PRELUDE"'fun main() { let xs: List<str> = ["a", "b"]; let n: u53 = xs.len(); let _ = take(n); }'
check downward_loop       "$PRELUDE"'fun main() { let xs: List<str> = ["a", "b"]; mut i: u53 = xs.len().as_u53(); for i > 0 { i -= 1; print(xs[i.as_i32()]); } }'
check underflow_runs      "$PRELUDE"'fun main() { mut i: u53 = 0; i -= 1; print(i"{i}"); }'
