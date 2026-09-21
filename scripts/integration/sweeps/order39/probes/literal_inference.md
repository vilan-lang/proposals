# Where an unsuffixed integer literal takes its type from context (vilan 0.40.0 c3f7d1a38, 2026-09-21)

WORKS (14): annotated `let`; argument position; return position; binary op with a typed LEFT (`a + 1`);
comparison (`a > 3`); struct field; enum payload (`Some(4)` against `Option<u53>`); generic method argument
(`xs.push(8)` on `List<u53>`); closure return; match arm value; if-branch value; `f64` from an integer
literal; compound assignment (`a += 1`); index position (`xs[1]`).

FAILS (2):
- a literal as the LEFT operand with a typed right — `1 + a` (a: u53) →
  "`+` adds two values of the same type, but the operands are `i32` and `u53` … suffix the literal or convert"
- the elements of an annotated LIST literal — `let xs: List<u53> = [1, 2, 3];` →
  "Expected List<u53>, but got List<i32> instead."

## MISCOMPILE — an EXPRESSION of literals in a typed position (the owner's kolt report: `Length::rem(4f / 16)`)

`fun rem(value: f64)`: `rem(4 / 16)` prints **0**, no diagnostic. Same for `let x: f64 = 4 / 16;` (0),
a return (`fun half(): f64 { 4 / 16 }` → 0), a method argument (`List<f64>::push(1 / 4)` → 0), a struct
field (`S { v = 1 / 4 }` → 0). Emitted JS: `const x = Math.trunc(4 / 16);` beside `const y = 4 / 16;` for
`4f / 16`. The checker RE-TYPES the literals from the context (the expression is accepted as `f64`) AFTER
the operator was dispatched as INTEGER division. Controls: an `i32` VARIABLE in the same positions is
correctly refused ("Expected f64, but got i32"); `rem(4 * 2)`, `1 + 2`, `10 - 3`, `7 % 2`, `-4`, `(4)`
give the right VALUE only because integer and float agree there — the same wrong dispatch is underneath.
