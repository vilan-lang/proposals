#![allow(unused_imports, unused_parens, unused_variables, unused_mut, unused_braces)]
#![allow(dead_code)]
#![allow(unreachable_patterns, non_camel_case_types, non_snake_case, clippy::all)]
use vilan_rt::Js as _;
use vilan_rt::Json as _;
use vilan_rt::Subscript as _;

fn main() {
    vilan_rt::main_guard(|| {
    let mut pair_9877 = ((1i32), (2i32),);
    match &mut pair_9877 {
        (mut a_9884, b_9885,) => {
            a_9884 = (a_9884 + (10i32));
        },
        _ => vilan_rt::panic_with("unreachable match leg"),
    };
    vilan_rt::print(&(pair_9877.0));
    vilan_rt::executor::run_pending();
    });
}
