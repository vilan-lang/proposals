#![allow(unused_imports, unused_parens, unused_variables, unused_mut, unused_braces)]
#![allow(dead_code)]
#![allow(unreachable_patterns, non_camel_case_types, non_snake_case, clippy::all)]
use vilan_rt::Js as _;
use vilan_rt::Json as _;

thread_local! {
    static MODULE_OUT_9479: vilan_rt::Shared<vilan_rt::Shared<vilan_rt::Str>> = vilan_rt::Shared::new(vilan_rt::Shared::new(vilan_rt::str_new("")));
}

fn main() {
    vilan_rt::main_guard(|| {
    let city_9484 = vilan_rt::str_new("Oslo");
    let by_value_9486 = { std::rc::Rc::new(move |mut c_9488: vilan_rt::Str| { {
        (MODULE_OUT_9479.with(|cell| cell.get())).set(c_9488);
    } }) as std::rc::Rc<dyn Fn(vilan_rt::Str) -> _> };
    let as_view_9495 = (by_value_9486).clone();
    (as_view_9495)((city_9484).clone());
    vilan_rt::print(&(vilan_rt::str_concat(&vilan_rt::str_concat(&vilan_rt::str_new(""), &vilan_rt::str_new("value closure called through a view type: out=")), &(MODULE_OUT_9479.with(|cell| cell.get())).get())));
    let by_view_9509 = { std::rc::Rc::new(move |mut c_9511: vilan_rt::Str| { {
        (MODULE_OUT_9479.with(|cell| cell.get())).set(((*c_9511)).clone());
    } }) as std::rc::Rc<dyn Fn(vilan_rt::Str) -> _> };
    let as_value_9519 = (by_view_9509).clone();
    (as_value_9519)(city_9484);
    vilan_rt::print(&(vilan_rt::str_concat(&vilan_rt::str_concat(&vilan_rt::str_new(""), &vilan_rt::str_new("view closure called through a value type: out=")), &(MODULE_OUT_9479.with(|cell| cell.get())).get())));
    vilan_rt::executor::run_pending();
    });
}
