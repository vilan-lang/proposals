#![allow(unused_imports, unused_parens, unused_variables, unused_mut, unused_braces)]
#![allow(dead_code)]
#![allow(unreachable_patterns, non_camel_case_types, non_snake_case, clippy::all)]
use vilan_rt::Js as _;
use vilan_rt::Json as _;

#[derive(Clone, PartialEq)]
struct Root_9306 {
    v: i32,
}
impl vilan_rt::Js for Root_9306 {
    fn js(&self) -> String {
        vilan_rt::js_tuple(&[self.v.js_nested()])
    }
}
impl vilan_rt::Json for Root_9306 {
    fn json(&self) -> String {
        vilan_rt::json_array(&[self.v.json()])
    }
}

fn ok_9324_0(mut s_9325: Root_9306) -> bool {
    steady_9317_0(&s_9325)
}

fn steady_9317_0(this: &Root_9306) -> bool {
    (get_9309(&this) == get_9309(&this))
}

fn get_9309(this: &Root_9306) -> i32 {
    (this.v).clone()
}

fn main() {
    vilan_rt::main_guard(|| {
    vilan_rt::print(&(ok_9324_0(Root_9306 { v: (1i32) })));
    vilan_rt::executor::run_pending();
    });
}
