#![allow(unused_imports, unused_parens, unused_variables, unused_mut, unused_braces)]
#![allow(dead_code)]
#![allow(unreachable_patterns, non_camel_case_types, non_snake_case, clippy::all)]
use vilan_rt::Js as _;
use vilan_rt::Json as _;

#[derive(Clone, PartialEq)]
struct A_9303 {
}
impl vilan_rt::Js for A_9303 {
    fn js(&self) -> String {
        vilan_rt::js_tuple(&[])
    }
}
impl vilan_rt::Json for A_9303 {
    fn json(&self) -> String {
        vilan_rt::json_array(&[])
    }
}

#[derive(Clone, PartialEq)]
struct Holder_9313_0 {
    v: A_9303,
}
impl vilan_rt::Js for Holder_9313_0 {
    fn js(&self) -> String {
        vilan_rt::js_tuple(&[self.v.js_nested()])
    }
}
impl vilan_rt::Json for Holder_9313_0 {
    fn json(&self) -> String {
        vilan_rt::json_array(&[self.v.json()])
    }
}

#[derive(Clone, PartialEq)]
struct B_9308 {
}
impl vilan_rt::Js for B_9308 {
    fn js(&self) -> String {
        vilan_rt::js_tuple(&[])
    }
}
impl vilan_rt::Json for B_9308 {
    fn json(&self) -> String {
        vilan_rt::json_array(&[])
    }
}

#[derive(Clone, PartialEq)]
struct Holder_9313_1 {
    v: B_9308,
}
impl vilan_rt::Js for Holder_9313_1 {
    fn js(&self) -> String {
        vilan_rt::js_tuple(&[self.v.js_nested()])
    }
}
impl vilan_rt::Json for Holder_9313_1 {
    fn json(&self) -> String {
        vilan_rt::json_array(&[self.v.json()])
    }
}

fn name_9322_0(this: &Holder_9313_0) -> vilan_rt::Str {
    label_9306()
}

fn label_9306() -> vilan_rt::Str {
    vilan_rt::str_new("A")
}

fn make_9318_0(mut v_9319: A_9303) -> Holder_9313_0 {
    Holder_9313_0 { v: (v_9319).clone() }
}

fn name_9322_1(this: &Holder_9313_1) -> vilan_rt::Str {
    label_9311()
}

fn label_9311() -> vilan_rt::Str {
    vilan_rt::str_new("B")
}

fn make_9318_1(mut v_9319: B_9308) -> Holder_9313_1 {
    Holder_9313_1 { v: (v_9319).clone() }
}

fn parse_9326_0(mut text_9327: vilan_rt::Str) -> Option<Holder_9313_1> {
    None
}

fn is_none_6535_0(this: &Option<Holder_9313_1>) -> bool {
    matches!(this, None)
}

fn main() {
    vilan_rt::main_guard(|| {
    vilan_rt::print(&(name_9322_0(&make_9318_0(A_9303 {  }))));
    vilan_rt::print(&(name_9322_1(&make_9318_1(B_9308 {  }))));
    let p_9342 = parse_9326_0(vilan_rt::str_new("x"));
    vilan_rt::print(&(is_none_6535_0(&p_9342)));
    vilan_rt::executor::run_pending();
    });
}
