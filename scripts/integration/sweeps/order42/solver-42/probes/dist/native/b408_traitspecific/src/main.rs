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

#[derive(Clone, PartialEq)]
struct Leaf_9311 {
    v: i32,
}
impl vilan_rt::Js for Leaf_9311 {
    fn js(&self) -> String {
        vilan_rt::js_tuple(&[self.v.js_nested()])
    }
}
impl vilan_rt::Json for Leaf_9311 {
    fn json(&self) -> String {
        vilan_rt::json_array(&[self.v.json()])
    }
}

fn doubled_9335(this: &Root_9310) -> i32 {
    (1000i32)
}

fn through_9338_0(mut s_9339: Root_9310) -> i32 {
    doubled_9335(&s_9339)
}

fn through_9338_1(mut s_9339: Leaf_9311) -> i32 {
    doubled_9327_0(&s_9339)
}

fn doubled_9327_0(this: &Leaf_9311) -> i32 {
    (get_9320(&this) * (2i32))
}

fn get_9320(this: &Leaf_9311) -> i32 {
    (this.v).clone()
}

fn main() {
    vilan_rt::main_guard(|| {
    vilan_rt::print(&(doubled_9335(&Root_9310 { v: (21i32) })));
    vilan_rt::print(&(through_9338_0(Root_9310 { v: (21i32) })));
    vilan_rt::print(&(through_9338_1(Leaf_9311 { v: (4i32) })));
    vilan_rt::executor::run_pending();
    });
}
