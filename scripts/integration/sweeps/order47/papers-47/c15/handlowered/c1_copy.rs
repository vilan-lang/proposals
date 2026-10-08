#![allow(unused_imports, unused_parens, unused_variables, unused_mut, unused_braces)]
#![allow(dead_code)]
#![allow(unreachable_patterns, non_camel_case_types, non_snake_case, clippy::all)]
use vilan_rt::Js as _;
use vilan_rt::Json as _;

fn main() {
    vilan_rt::main_guard(|| {
    let mut label_9421 = vilan_rt::str_new("before");
    let show_9423 = { let label_9421 = label_9421.clone(); std::rc::Rc::new(move || { (label_9421).clone() }) as std::rc::Rc<dyn Fn() -> vilan_rt::Str> };
    { let __assigned = vilan_rt::str_new("after"); label_9421 = __assigned; };
    vilan_rt::print(&((show_9423)()));
    vilan_rt::executor::run_pending();
    });
}
