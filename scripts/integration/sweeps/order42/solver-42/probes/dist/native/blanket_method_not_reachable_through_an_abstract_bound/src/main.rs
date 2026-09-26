#![allow(unused_imports, unused_parens, unused_variables, unused_mut, unused_braces)]
#![allow(dead_code)]
#![allow(unreachable_patterns, non_camel_case_types, non_snake_case, clippy::all)]
use vilan_rt::Js as _;
use vilan_rt::Json as _;

#[derive(Clone, PartialEq)]
struct Root_9305 {
    v: i32,
}
impl vilan_rt::Js for Root_9305 {
    fn js(&self) -> String {
        vilan_rt::js_tuple(&[self.v.js_nested()])
    }
}
impl vilan_rt::Json for Root_9305 {
    fn json(&self) -> String {
        vilan_rt::json_array(&[self.v.json()])
    }
}

fn through_9323_0(mut s_9324: Root_9305) -> i32 {
    let (a_9329, b_9330,) = twice_9316_0(&s_9324);
    (a_9329 + b_9330)
}

fn twice_9316_0(this: &Root_9305) -> (i32, i32) {
    (get_9308(&this), get_9308(&this),)
}

fn get_9308(this: &Root_9305) -> i32 {
    (this.v).clone()
}

fn main() {
    vilan_rt::main_guard(|| {
    vilan_rt::print(&(through_9323_0(Root_9305 { v: (2i32) })));
    vilan_rt::executor::run_pending();
    });
}
