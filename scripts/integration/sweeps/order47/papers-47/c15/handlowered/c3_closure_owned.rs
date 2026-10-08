#![allow(unused_imports, unused_parens, unused_variables, unused_mut, unused_braces)]
#![allow(dead_code)]
#![allow(unreachable_patterns, non_camel_case_types, non_snake_case, clippy::all)]
use vilan_rt::Js as _;
use vilan_rt::Json as _;

fn main() {
    vilan_rt::main_guard(|| {
    let n_9421 = (0i32);
    let mut fs_9423: Vec<std::rc::Rc<dyn Fn() -> i32>> = vec![];
    for _i_9430 in (vec![(0i32), (1i32), (2i32)]).clone().into_iter() {
        fs_9423.push({ let n_9421 = std::cell::Cell::new(n_9421); std::rc::Rc::new(move || { {
            { let __assigned = (n_9421.get() + (1i32)); n_9421.set(__assigned); };
            n_9421.get()
        } }) as std::rc::Rc<dyn Fn() -> i32> });
    }
    for f_9444 in (fs_9423).clone().into_iter() {
        vilan_rt::print(&((f_9444)()));
    }
    vilan_rt::executor::run_pending();
    });
}
