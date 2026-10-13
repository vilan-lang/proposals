#![allow(unused_imports, unused_parens, unused_variables, unused_mut, unused_braces)]
#![allow(dead_code)]
#![allow(unreachable_patterns, non_camel_case_types, non_snake_case, clippy::all)]
use vilan_rt::Js as _;
use vilan_rt::Json as _;
use vilan_rt::Subscript as _;

#[derive(Clone, PartialEq)]
struct Holder_10071_0 {
    value: i32,
}
impl vilan_rt::Js for Holder_10071_0 {
    fn js(&self) -> String {
        vilan_rt::js_items(&[&self.value as &dyn vilan_rt::Js])
    }
}
impl vilan_rt::Json for Holder_10071_0 {
    fn json(&self) -> String {
        vilan_rt::json_array(&[self.value.json()])
    }
}

fn unwrap_7387_0(mut this: Option<Holder_10071_0>, mut caller_10094: vilan_rt::Location) -> Holder_10071_0 {
    match (this).clone() {
        Some(x_7391) => x_7391,
        _ => vilan_rt::panic_at(&(vilan_rt::str_new("expected Some but got None")), caller_10094),
    }
}

fn build_10076_0() -> Option<Holder_10071_0> {
    Some(Holder_10071_0 { value: make_10069() })
}

fn make_10069() -> i32 {
    (7i32)
}

fn main() {
    vilan_rt::main_guard(|| {
    let held_10083 = unwrap_7387_0(build_10076_0(), vilan_rt::Location("main.vl:26:42"));
    vilan_rt::print(&(held_10083.value));
    vilan_rt::executor::run_pending();
    });
}
