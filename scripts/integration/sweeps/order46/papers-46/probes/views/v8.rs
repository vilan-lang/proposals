#![allow(unused_imports, unused_parens, unused_variables, unused_mut, unused_braces)]
#![allow(dead_code)]
#![allow(unreachable_patterns, non_camel_case_types, non_snake_case, clippy::all)]
use vilan_rt::Js as _;
use vilan_rt::Json as _;

#[derive(Clone, PartialEq)]
struct Counter_9418 {
    n: i32,
}
impl vilan_rt::Js for Counter_9418 {
    fn js(&self) -> String {
        vilan_rt::js_tuple(&[self.n.js_nested()])
    }
}
impl vilan_rt::Json for Counter_9418 {
    fn json(&self) -> String {
        vilan_rt::json_array(&[self.n.json()])
    }
}

fn main() {
    vilan_rt::main_guard(|| {
    let mut c_9420 = Counter_9418 { n: (1i32) };
    let bump_9423 = Some({ std::rc::Rc::new(move |x_9427: &mut i32| { {
        (*x_9427) = ((*x_9427) + (10i32));
    } }) as std::rc::Rc<dyn Fn(&mut i32) -> _> });
    match (bump_9423).clone() {
        Some(f_9437) => (f_9437)((c_9420.n).clone()),
        None => {
        },
        _ => vilan_rt::panic_with("unreachable match leg"),
    };
    vilan_rt::print(&(vilan_rt::str_concat(&vilan_rt::str_concat(&vilan_rt::str_new(""), &vilan_rt::str_new("through a match capture: n=")), &vilan_rt::js_of(&(c_9420.n)))));
    let all_9453 = vec![{ std::rc::Rc::new(move |x_9456: &mut i32| { {
        (*x_9456) = ((*x_9456) + (100i32));
    } }) as std::rc::Rc<dyn Fn(&mut i32) -> _> }];
    for g_9466 in (all_9453).clone().into_iter() {
        (g_9466)((c_9420.n).clone());
    }
    vilan_rt::print(&(vilan_rt::str_concat(&vilan_rt::str_concat(&vilan_rt::str_new(""), &vilan_rt::str_new("through a loop binding: n=")), &vilan_rt::js_of(&(c_9420.n)))));
    vilan_rt::executor::run_pending();
    });
}
