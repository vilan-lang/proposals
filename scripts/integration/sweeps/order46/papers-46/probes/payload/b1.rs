#![allow(unused_imports, unused_parens, unused_variables, unused_mut, unused_braces)]
#![allow(dead_code)]
#![allow(unreachable_patterns, non_camel_case_types, non_snake_case, clippy::all)]
use vilan_rt::Js as _;
use vilan_rt::Json as _;

#[derive(Clone, PartialEq)]
struct P_9419 {
    x: i32,
    tags: Vec<vilan_rt::Str>,
}
impl vilan_rt::Js for P_9419 {
    fn js(&self) -> String {
        vilan_rt::js_tuple(&[self.x.js_nested(), self.tags.js_nested()])
    }
}
impl vilan_rt::Json for P_9419 {
    fn json(&self) -> String {
        vilan_rt::json_array(&[self.x.json(), self.tags.json()])
    }
}

fn unwrap_or_6594_0(mut this: Option<i32>, mut fallback_6596: i32) -> i32 {
    match (this).clone() {
        Some(x_6599) => x_6599,
        _ => fallback_6596,
    }
}

fn map_6611_0(mut this: Option<P_9419>, mut r#fn_6613: std::rc::Rc<dyn Fn(P_9419) -> i32>) -> Option<i32> {
    match (this).clone() {
        Some(x_6617) => Some((r#fn_6613)(x_6617)),
        None => None,
        _ => vilan_rt::panic_with("unreachable match leg"),
    }
}

fn main() {
    vilan_rt::main_guard(|| {
    let mut held_9421: Option<P_9419> = Some(P_9419 { x: (1i32), tags: vec![vilan_rt::str_new("a")] });
    match (held_9421).clone() {
        Some(mut p_9430) => {
            p_9430.x = (2i32);
        },
        None => {
        },
        _ => vilan_rt::panic_with("unreachable match leg"),
    };
    vilan_rt::print(&(vilan_rt::str_concat(&vilan_rt::str_concat(&vilan_rt::str_new(""), &vilan_rt::str_new("(1) Some(mut p), p.x = 2: held.x=")), &vilan_rt::js_of(&(unwrap_or_6594_0(map_6611_0((held_9421).clone(), { std::rc::Rc::new(move |mut p_9449: P_9419| { p_9449.x }) as std::rc::Rc<dyn Fn(P_9419) -> _> }), (0i32)))))));
    match (held_9421).take() {
        Some(mut p_9456) => {
            p_9456.x = (3i32);
            held_9421 = Some(p_9456);
        },
        None => {
        },
        _ => vilan_rt::panic_with("unreachable match leg"),
    };
    vilan_rt::print(&(vilan_rt::str_concat(&vilan_rt::str_concat(&vilan_rt::str_new(""), &vilan_rt::str_new("(2) take, write, put back: held.x=")), &vilan_rt::js_of(&(unwrap_or_6594_0(map_6611_0(held_9421, { std::rc::Rc::new(move |mut p_9480: P_9419| { p_9480.x }) as std::rc::Rc<dyn Fn(P_9419) -> _> }), (0i32)))))));
    vilan_rt::executor::run_pending();
    });
}
