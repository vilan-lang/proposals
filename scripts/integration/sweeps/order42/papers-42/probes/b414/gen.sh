#!/bin/bash
# gen.sh WORD -> writes p_<pos>_WORD.vl
W=$1; D=$2; mkdir -p $D
cat > $D/let.vl <<V
fun main() { let $W = 1; let y = $W + 1; }
V
cat > $D/param.vl <<V
fun f($W: i32): i32 { $W + 1 }
fun main() { let y = f(1); }
V
cat > $D/field.vl <<V
struct S { $W: i32 }
fun main() { let s = S { $W = 1 }; let y = s.$W + 1; }
V
cat > $D/method.vl <<V
struct S { n: i32 }
impl S { fun $W(self): i32 { self.n } }
fun main() { let s = S { n = 1 }; let y = s.$W() + 1; }
V
cat > $D/function.vl <<V
fun $W(): i32 { 1 }
fun main() { let y = $W() + 1; }
V
cat > $D/variant.vl <<V
enum E { $W, Other }
fun main() { let e = E::$W; }
V
cat > $D/closure.vl <<V
fun main() { let g = |$W: i32| $W + 1; let y = g(1); }
V
cat > $D/alias.vl <<V
import std::io::print as $W;
fun main() { $W("x"); }
V
cat > $D/typename.vl <<V
struct $W { n: i32 }
fun main() { let s = $W { n = 1 }; }
V
