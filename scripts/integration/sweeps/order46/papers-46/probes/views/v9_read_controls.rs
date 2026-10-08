#![allow(unused_imports, unused_parens, unused_variables, unused_mut, unused_braces)]
#![allow(dead_code)]
#![allow(unreachable_patterns, non_camel_case_types, non_snake_case, clippy::all)]
use vilan_rt::Js as _;
use vilan_rt::Json as _;

#[derive(Clone)]
struct Sink_9490 {
    f: std::rc::Rc<dyn Fn(&vilan_rt::Str) -> ()>,
}
impl PartialEq for Sink_9490 {
    fn eq(&self, other: &Self) -> bool {
        std::rc::Rc::ptr_eq(&self.f, &other.f)
    }
}
impl vilan_rt::Js for Sink_9490 {
    fn js(&self) -> String {
        vilan_rt::panic_with("the rust backend cannot print a value holding \
                 a function")
    }
}
impl vilan_rt::Json for Sink_9490 {
    fn json(&self) -> String {
        vilan_rt::panic_with("the rust backend cannot hash or serialize a \
                 value holding a function")
    }
}

thread_local! {
    static MODULE_OUT_9479: vilan_rt::Shared<vilan_rt::Shared<vilan_rt::Str>> = vilan_rt::Shared::new(vilan_rt::Shared::new(vilan_rt::str_new("")));
}

fn with_city_9483(city_9484: &vilan_rt::Str, mut f_9485: std::rc::Rc<dyn Fn(&vilan_rt::Str) -> ()>) -> () {
    (f_9485)(&city_9484);
}

fn main() {
    vilan_rt::main_guard(|| {
    let city_9492 = vilan_rt::str_new("Oslo");
    with_city_9483(&city_9492, { std::rc::Rc::new(move |c_9499: &vilan_rt::Str| { {
        (MODULE_OUT_9479.with(|cell| cell.get())).set(((*c_9499)).clone());
    } }) as std::rc::Rc<dyn Fn(&vilan_rt::Str) -> _> });
    vilan_rt::print(&(vilan_rt::str_concat(&vilan_rt::str_concat(&vilan_rt::str_new(""), &vilan_rt::str_new("(a) fun parameter, bare literal: out=")), &(MODULE_OUT_9479.with(|cell| cell.get())).get())));
    let spelled_9515 = { std::rc::Rc::new(move |c_9517: &vilan_rt::Str| { {
        (MODULE_OUT_9479.with(|cell| cell.get())).set(((*c_9517)).clone());
    } }) as std::rc::Rc<dyn Fn(&vilan_rt::Str) -> _> };
    (spelled_9515)((city_9492).clone());
    vilan_rt::print(&(vilan_rt::str_concat(&vilan_rt::str_concat(&vilan_rt::str_new(""), &vilan_rt::str_new("(b) annotated let, spelled view: out=")), &(MODULE_OUT_9479.with(|cell| cell.get())).get())));
    let sink_9537 = Sink_9490 { f: { std::rc::Rc::new(move |c_9540: &vilan_rt::Str| { {
        (MODULE_OUT_9479.with(|cell| cell.get())).set(((*c_9540)).clone());
    } }) as std::rc::Rc<dyn Fn(&vilan_rt::Str) -> _> } };
    (sink_9537.f)(&city_9492);
    vilan_rt::print(&(vilan_rt::str_concat(&vilan_rt::str_concat(&vilan_rt::str_new(""), &vilan_rt::str_new("(c) struct field, bare literal: out=")), &(MODULE_OUT_9479.with(|cell| cell.get())).get())));
    vilan_rt::executor::run_pending();
    });
}
