#![allow(unused_imports, unused_parens, unused_variables, unused_mut, unused_braces)]
#![allow(dead_code)]
#![allow(unreachable_patterns, non_camel_case_types, non_snake_case, clippy::all)]
use vilan_rt::Js as _;
use vilan_rt::Json as _;

#[derive(Clone)]
struct Sw_9326_0 {
    up: Root_9312,
    select: std::rc::Rc<dyn Fn(i32) -> Word_9319>,
}
impl PartialEq for Sw_9326_0 {
    fn eq(&self, other: &Self) -> bool {
        self.up == other.up && std::rc::Rc::ptr_eq(&self.select, &other.select)
    }
}
impl vilan_rt::Js for Sw_9326_0 {
    fn js(&self) -> String {
        vilan_rt::panic_with("the rust backend cannot print a value holding \
                 a function")
    }
}
impl vilan_rt::Json for Sw_9326_0 {
    fn json(&self) -> String {
        vilan_rt::panic_with("the rust backend cannot hash or serialize a \
                 value holding a function")
    }
}

#[derive(Clone, PartialEq)]
struct Root_9312 {
    v: i32,
}
impl vilan_rt::Js for Root_9312 {
    fn js(&self) -> String {
        vilan_rt::js_tuple(&[self.v.js_nested()])
    }
}
impl vilan_rt::Json for Root_9312 {
    fn json(&self) -> String {
        vilan_rt::json_array(&[self.v.json()])
    }
}

#[derive(Clone, PartialEq)]
struct Word_9319 {
    w: vilan_rt::Str,
}
impl vilan_rt::Js for Word_9319 {
    fn js(&self) -> String {
        vilan_rt::js_tuple(&[self.w.js_nested()])
    }
}
impl vilan_rt::Json for Word_9319 {
    fn json(&self) -> String {
        vilan_rt::json_array(&[self.w.json()])
    }
}

fn show_9305_d0(this: &Sw_9326_0, mut f_9307: std::rc::Rc<dyn Fn(vilan_rt::Str) -> vilan_rt::Str>) -> vilan_rt::Str {
    (f_9307)(get_9336_0(&this))
}

fn get_9336_0(this: &Sw_9326_0) -> vilan_rt::Str {
    get_9322(&(this.select)(get_9315(&this.up)))
}

fn get_9322(this: &Word_9319) -> vilan_rt::Str {
    (this.w).clone()
}

fn get_9315(this: &Root_9312) -> i32 {
    (this.v).clone()
}

fn shown_9345_0(mut r_9346: Sw_9326_0, mut f_9347: std::rc::Rc<dyn Fn(vilan_rt::Str) -> vilan_rt::Str>) -> vilan_rt::Str {
    show_9305_d0(&r_9346, (f_9347).clone())
}

fn main() {
    vilan_rt::main_guard(|| {
    let s_9354 = Sw_9326_0 { up: Root_9312 { v: (2i32) }, select: { std::rc::Rc::new(move |mut n_9359: i32| { Word_9319 { w: vilan_rt::str_concat(&vilan_rt::str_concat(&vilan_rt::str_new(""), &vilan_rt::str_new("w")), &vilan_rt::js_of(&(n_9359))) } }) } };
    vilan_rt::print(&(show_9305_d0(&s_9354, { std::rc::Rc::new(move |mut text_9371: vilan_rt::Str| { vilan_rt::str_concat(&text_9371, &vilan_rt::str_new("!")) }) })));
    vilan_rt::print(&(shown_9345_0(s_9354, { std::rc::Rc::new(move |mut text_9381: vilan_rt::Str| { vilan_rt::str_concat(&text_9381, &vilan_rt::str_new("?")) }) })));
    vilan_rt::executor::run_pending();
    });
}
