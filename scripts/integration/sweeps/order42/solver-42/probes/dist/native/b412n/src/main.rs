#![allow(unused_imports, unused_parens, unused_variables, unused_mut, unused_braces)]
#![allow(dead_code)]
#![allow(unreachable_patterns, non_camel_case_types, non_snake_case, clippy::all)]
use vilan_rt::Js as _;
use vilan_rt::Json as _;

trait ObjectSrc_9299_0: vilan_rt::Js + vilan_rt::Json {
    fn get(&self) -> i32;
}

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

impl ObjectSrc_9299_0 for Root_9305 {
    fn get(&self) -> i32 {
        get_9308(self)
    }
}

#[derive(Clone, PartialEq)]
struct Twice_9312 {
    v: i32,
}
impl vilan_rt::Js for Twice_9312 {
    fn js(&self) -> String {
        vilan_rt::js_tuple(&[self.v.js_nested()])
    }
}
impl vilan_rt::Json for Twice_9312 {
    fn json(&self) -> String {
        vilan_rt::json_array(&[self.v.json()])
    }
}

impl ObjectSrc_9299_0 for Twice_9312 {
    fn get(&self) -> i32 {
        get_9315(self)
    }
}

fn erase_9325_0(mut s_9326: Root_9305) -> vilan_rt::Dyn<dyn ObjectSrc_9299_0> {
    vilan_rt::Dyn::<dyn ObjectSrc_9299_0>::new(std::rc::Rc::new(s_9326))
}

fn get_9308(this: &Root_9305) -> i32 {
    (this.v).clone()
}

fn shown_9329_0(mut s_9330: Twice_9312) -> i32 {
    show_9321(vilan_rt::Dyn::<dyn ObjectSrc_9299_0>::new(std::rc::Rc::new(s_9330)))
}

fn show_9321(mut source_9322: vilan_rt::Dyn<dyn ObjectSrc_9299_0>) -> i32 {
    ObjectSrc_9299_0::get((source_9322).object())
}

fn get_9315(this: &Twice_9312) -> i32 {
    ((this.v).clone() * (2i32))
}

fn erase_9325_1(mut s_9326: vilan_rt::Dyn<dyn ObjectSrc_9299_0>) -> vilan_rt::Dyn<dyn ObjectSrc_9299_0> {
    s_9326
}

fn main() {
    vilan_rt::main_guard(|| {
    vilan_rt::print(&(ObjectSrc_9299_0::get((erase_9325_0(Root_9305 { v: (1i32) })).object())));
    vilan_rt::print(&(shown_9329_0(Twice_9312 { v: (2i32) })));
    let object_9349 = vilan_rt::Dyn::<dyn ObjectSrc_9299_0>::new(std::rc::Rc::new(Twice_9312 { v: (5i32) }));
    vilan_rt::print(&(ObjectSrc_9299_0::get((erase_9325_1(object_9349)).object())));
    vilan_rt::executor::run_pending();
    });
}
