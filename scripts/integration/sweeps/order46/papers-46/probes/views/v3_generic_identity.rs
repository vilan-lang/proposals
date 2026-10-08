#![allow(unused_imports, unused_parens, unused_variables, unused_mut, unused_braces)]
#![allow(dead_code)]
#![allow(unreachable_patterns, non_camel_case_types, non_snake_case, clippy::all)]
use vilan_rt::Js as _;
use vilan_rt::Json as _;

thread_local! {
    static MODULE_OUT_9479: vilan_rt::Shared<vilan_rt::Shared<vilan_rt::Str>> = vilan_rt::Shared::new(vilan_rt::Shared::new(vilan_rt::str_new("")));
}

fn hold_9483_0(mut x_9484: std::rc::Rc<dyn Fn(vilan_rt::Str) -> ()>) -> std::rc::Rc<dyn Fn(vilan_rt::Str) -> ()> {
    (x_9484).clone()
}

fn main() {
    vilan_rt::main_guard(|| {
    let city_9488 = vilan_rt::str_new("Bergen");
    let f_9490 = hold_9483_0({ std::rc::Rc::new(move |mut c_9494: vilan_rt::Str| { {
        (MODULE_OUT_9479.with(|cell| cell.get())).set(((*c_9494)).clone());
    } }) as std::rc::Rc<dyn Fn(vilan_rt::Str) -> _> });
    (f_9490)((city_9488).clone());
    vilan_rt::print(&(vilan_rt::str_concat(&vilan_rt::str_concat(&vilan_rt::str_new(""), &vilan_rt::str_new("through hold<T>: out=")), &(MODULE_OUT_9479.with(|cell| cell.get())).get())));
    vilan_rt::executor::run_pending();
    });
}
