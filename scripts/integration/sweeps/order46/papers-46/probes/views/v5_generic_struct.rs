#![allow(unused_imports, unused_parens, unused_variables, unused_mut, unused_braces)]
#![allow(dead_code)]
#![allow(unreachable_patterns, non_camel_case_types, non_snake_case, clippy::all)]
use vilan_rt::Js as _;
use vilan_rt::Json as _;

#[derive(Clone)]
struct Holder_9418_0 {
    f: std::rc::Rc<dyn Fn(&mut i32) -> ()>,
}
impl PartialEq for Holder_9418_0 {
    fn eq(&self, other: &Self) -> bool {
        std::rc::Rc::ptr_eq(&self.f, &other.f)
    }
}
impl vilan_rt::Js for Holder_9418_0 {
    fn js(&self) -> String {
        vilan_rt::panic_with("the rust backend cannot print a value holding \
                 a function")
    }
}
impl vilan_rt::Json for Holder_9418_0 {
    fn json(&self) -> String {
        vilan_rt::panic_with("the rust backend cannot hash or serialize a \
                 value holding a function")
    }
}

fn main() {
    vilan_rt::main_guard(|| {
    let mut n_9421 = (1i32);
    let h_9423 = Holder_9418_0 { f: { std::rc::Rc::new(move |x_9426: &mut i32| { {
        (*x_9426) = ((*x_9426) + (5i32));
    } }) as std::rc::Rc<dyn Fn(&mut i32) -> _> } };
    (h_9423.f)((n_9421).clone());
    vilan_rt::print(&(vilan_rt::str_concat(&vilan_rt::str_concat(&vilan_rt::str_new(""), &vilan_rt::str_new("through Holder<T>: n=")), &vilan_rt::js_of(&(n_9421)))));
    vilan_rt::executor::run_pending();
    });
}
