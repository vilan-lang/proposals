#![allow(unused_imports, unused_parens, unused_variables, unused_mut, unused_braces)]
#![allow(dead_code)]
#![allow(unreachable_patterns, non_camel_case_types, non_snake_case, clippy::all)]
use vilan_rt::Js as _;
use vilan_rt::Json as _;

#[derive(Clone, PartialEq)]
struct S_9300 {
    r#self: i32,
    r#super: i32,
}
impl vilan_rt::Js for S_9300 {
    fn js(&self) -> String {
        vilan_rt::js_tuple(&[self.r#self.js_nested(), self.r#super.js_nested()])
    }
}
impl vilan_rt::Json for S_9300 {
    fn json(&self) -> String {
        vilan_rt::json_array(&[self.r#self.json(), self.r#super.json()])
    }
}

fn main() {
    vilan_rt::main_guard(|| {
    let s_9302 = S_9300 { r#self: (1i32), r#super: (2i32) };
    vilan_rt::print(&(vilan_rt::str_concat(&vilan_rt::str_new(""), &vilan_rt::js_of(&((s_9302.r#self + s_9302.r#super))))));
    vilan_rt::executor::run_pending();
    });
}
