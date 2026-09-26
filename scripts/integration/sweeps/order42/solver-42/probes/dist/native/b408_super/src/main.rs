#![allow(unused_imports, unused_parens, unused_variables, unused_mut, unused_braces)]
#![allow(dead_code)]
#![allow(unreachable_patterns, non_camel_case_types, non_snake_case, clippy::all)]
use vilan_rt::Js as _;
use vilan_rt::Json as _;

#[derive(Clone, PartialEq)]
struct Root_9311 {
    v: i32,
}
impl vilan_rt::Js for Root_9311 {
    fn js(&self) -> String {
        vilan_rt::js_tuple(&[self.v.js_nested()])
    }
}
impl vilan_rt::Json for Root_9311 {
    fn json(&self) -> String {
        vilan_rt::json_array(&[self.v.json()])
    }
}

#[derive(Clone, PartialEq)]
struct Word_9323 {
    w: vilan_rt::Str,
}
impl vilan_rt::Js for Word_9323 {
    fn js(&self) -> String {
        vilan_rt::js_tuple(&[self.w.js_nested()])
    }
}
impl vilan_rt::Json for Word_9323 {
    fn json(&self) -> String {
        vilan_rt::json_array(&[self.w.json()])
    }
}

fn through_9354_0(mut s_9355: Root_9311) -> i32 {
    let (a_9360, b_9361,) = twice_9339_0(&s_9355);
    (a_9360 + b_9361)
}

fn twice_9339_0(this: &Root_9311) -> (i32, i32) {
    (get_9314(&this), get_9314(&this),)
}

fn get_9314(this: &Root_9311) -> i32 {
    (this.v).clone()
}

fn generic_t_9365_0(mut s_9366: Root_9311) -> i32 {
    let (a_9372, __9373,) = twice_9339_0(&s_9366);
    a_9372
}

fn generic_t_9365_1(mut s_9366: Word_9323) -> vilan_rt::Str {
    let (a_9372, __9373,) = twice_9339_1(&s_9366);
    a_9372
}

fn twice_9339_1(this: &Word_9323) -> (vilan_rt::Str, vilan_rt::Str) {
    (get_9326(&this), get_9326(&this),)
}

fn get_9326(this: &Word_9323) -> vilan_rt::Str {
    (this.w).clone()
}

fn with_own_9375_0(mut s_9376: Root_9311) -> vilan_rt::Str {
    let (n_9382, w_9383,) = pair_with_9346_0(&s_9376, vilan_rt::str_new("x"));
    vilan_rt::str_concat(&vilan_rt::str_concat(&vilan_rt::str_new(""), &vilan_rt::js_of(&(n_9382))), &w_9383)
}

fn pair_with_9346_0(this: &Root_9311, mut u_9348: vilan_rt::Str) -> (i32, vilan_rt::Str) {
    (get_9314(&this), (u_9348).clone(),)
}

fn main() {
    vilan_rt::main_guard(|| {
    vilan_rt::print(&(through_9354_0(Root_9311 { v: (2i32) })));
    vilan_rt::print(&(generic_t_9365_0(Root_9311 { v: (3i32) })));
    vilan_rt::print(&(generic_t_9365_1(Word_9323 { w: vilan_rt::str_new("hi") })));
    vilan_rt::print(&(with_own_9375_0(Root_9311 { v: (4i32) })));
    vilan_rt::executor::run_pending();
    });
}
