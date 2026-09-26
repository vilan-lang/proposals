#![allow(unused_imports, unused_parens, unused_variables, unused_mut, unused_braces)]
#![allow(dead_code)]
#![allow(unreachable_patterns, non_camel_case_types, non_snake_case, clippy::all)]
use vilan_rt::Js as _;
use vilan_rt::Json as _;

#[derive(Clone, PartialEq)]
struct Root_9310 {
    v: i32,
}
impl vilan_rt::Js for Root_9310 {
    fn js(&self) -> String {
        vilan_rt::js_tuple(&[self.v.js_nested()])
    }
}
impl vilan_rt::Json for Root_9310 {
    fn json(&self) -> String {
        vilan_rt::json_array(&[self.v.json()])
    }
}

fn through_9326_0(mut s_9327: Root_9310) -> i32 {
    doubled_9320_0(&s_9327)
}

fn doubled_9320_0(this: &Root_9310) -> i32 {
    (get_9313(&this) * (2i32))
}

fn get_9313(this: &Root_9310) -> i32 {
    (this.v).clone()
}

fn main() {
    vilan_rt::main_guard(|| {
    vilan_rt::print(&(through_9326_0(Root_9310 { v: (21i32) })));
    vilan_rt::executor::run_pending();
    });
}
