#![allow(unused_imports, unused_parens, unused_variables, unused_mut, unused_braces)]
#![allow(dead_code)]
#![allow(unreachable_patterns, non_camel_case_types, non_snake_case, clippy::all)]
use vilan_rt::Js as _;
use vilan_rt::Json as _;

#[derive(Clone, PartialEq)]
struct Id_9308_0 {
    v: i32,
}
impl vilan_rt::Js for Id_9308_0 {
    fn js(&self) -> String {
        vilan_rt::js_tuple(&[self.v.js_nested()])
    }
}
impl vilan_rt::Json for Id_9308_0 {
    fn json(&self) -> String {
        vilan_rt::json_array(&[self.v.json()])
    }
}

#[derive(Clone, PartialEq)]
struct Id_9308_1 {
    v: (i32, i32),
}
impl vilan_rt::Js for Id_9308_1 {
    fn js(&self) -> String {
        vilan_rt::js_tuple(&[self.v.js_nested()])
    }
}
impl vilan_rt::Json for Id_9308_1 {
    fn json(&self) -> String {
        vilan_rt::json_array(&[self.v.json()])
    }
}

#[derive(Clone, PartialEq)]
struct Id_9308_2 {
    v: Vec<i32>,
}
impl vilan_rt::Js for Id_9308_2 {
    fn js(&self) -> String {
        vilan_rt::js_tuple(&[self.v.js_nested()])
    }
}
impl vilan_rt::Json for Id_9308_2 {
    fn json(&self) -> String {
        vilan_rt::json_array(&[self.v.json()])
    }
}

#[derive(Clone, PartialEq)]
struct Id_9308_3 {
    v: Option<i32>,
}
impl vilan_rt::Js for Id_9308_3 {
    fn js(&self) -> String {
        vilan_rt::js_tuple(&[self.v.js_nested()])
    }
}
impl vilan_rt::Json for Id_9308_3 {
    fn json(&self) -> String {
        vilan_rt::json_array(&[self.v.json()])
    }
}

fn through_9320_0(mut s_9321: Id_9308_0) -> vilan_rt::Str {
    label_9317_0(&s_9321)
}

fn label_9317_0(this: &Id_9308_0) -> vilan_rt::Str {
    vilan_rt::str_new("id override")
}

fn through_9320_1(mut s_9321: Id_9308_1) -> vilan_rt::Str {
    label_9317_1(&s_9321)
}

fn label_9317_1(this: &Id_9308_1) -> vilan_rt::Str {
    vilan_rt::str_new("id override")
}

fn through2_9326_0(mut s_9327: Id_9308_1) -> vilan_rt::Str {
    label_9317_1(&s_9327)
}

fn through_9320_2(mut s_9321: Id_9308_2) -> vilan_rt::Str {
    label_9317_2(&s_9321)
}

fn label_9317_2(this: &Id_9308_2) -> vilan_rt::Str {
    vilan_rt::str_new("id override")
}

fn through_9320_3(mut s_9321: Id_9308_3) -> vilan_rt::Str {
    label_9317_3(&s_9321)
}

fn label_9317_3(this: &Id_9308_3) -> vilan_rt::Str {
    vilan_rt::str_new("id override")
}

fn main() {
    vilan_rt::main_guard(|| {
    vilan_rt::print(&(through_9320_0(Id_9308_0 { v: (1i32) })));
    let b_9338 = Id_9308_1 { v: ((1i32), (2i32),) };
    vilan_rt::print(&(through_9320_1((b_9338).clone())));
    vilan_rt::print(&(through2_9326_0(b_9338)));
    vilan_rt::print(&(through_9320_2(Id_9308_2 { v: vec![(1i32)] })));
    vilan_rt::print(&(through_9320_3(Id_9308_3 { v: Some((1i32)) })));
    vilan_rt::executor::run_pending();
    });
}
