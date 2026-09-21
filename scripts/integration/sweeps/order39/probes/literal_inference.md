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
