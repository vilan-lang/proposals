#![allow(unused_imports, unused_parens, unused_variables, unused_mut, unused_braces)]
#![allow(dead_code)]
#![allow(unreachable_patterns, non_camel_case_types, non_snake_case, clippy::all)]
use vilan_rt::Js as _;
use vilan_rt::Json as _;

fn main() {
    vilan_rt::main_guard(|| {
    let mut a_9300 = vec![(1i32), (2i32)];
    let flag_9304 = ((a_9300.len() as i32) == (2i32));
    let mut b_9309 = if flag_9304 {
        (a_9300).clone()
    } else {
        vec![]
    };
    b_9309.push((3i32));
    let mut c_9317 = (a_9300).clone();
    c_9317.push((4i32));
    vilan_rt::print(&(vilan_rt::str_concat(&vilan_rt::str_concat(&vilan_rt::str_concat(&vilan_rt::str_concat(&vilan_rt::str_concat(&vilan_rt::str_concat(&vilan_rt::str_new(""), &vilan_rt::str_new("a=")), &vilan_rt::js_of(&((a_9300.len() as i32)))), &vilan_rt::str_new(" b=")), &vilan_rt::js_of(&((b_9309.len() as i32)))), &vilan_rt::str_new(" c=")), &vilan_rt::js_of(&((c_9317.len() as i32))))));
    vilan_rt::executor::run_pending();
    });
}
