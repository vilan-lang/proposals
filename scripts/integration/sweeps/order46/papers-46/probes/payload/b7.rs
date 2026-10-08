#![allow(unused_imports, unused_parens, unused_variables, unused_mut, unused_braces)]
#![allow(dead_code)]
#![allow(unreachable_patterns, non_camel_case_types, non_snake_case, clippy::all)]
use vilan_rt::Js as _;
use vilan_rt::Json as _;

#[derive(Clone, PartialEq)]
enum E_10280 {
    A(P_10279),
    B,
}
impl vilan_rt::Js for E_10280 {
    fn js(&self) -> String {
        match self {
            E_10280::A(p0) => vilan_rt::js_tuple(&["0".to_string(), p0.js_nested()]),
            E_10280::B => vilan_rt::js_tuple(&["1".to_string()]),
        }
    }
}
impl vilan_rt::Json for E_10280 {
    fn json(&self) -> String {
        match self {
            E_10280::A(p0) => vilan_rt::json_array(&["0".to_string(), p0.json()]),
            E_10280::B => vilan_rt::json_array(&["1".to_string()]),
        }
    }
}

#[derive(Clone, PartialEq)]
struct P_10279 {
    x: i32,
    big: Vec<i32>,
}
impl vilan_rt::Js for P_10279 {
    fn js(&self) -> String {
        vilan_rt::js_tuple(&[self.x.js_nested(), self.big.js_nested()])
    }
}
impl vilan_rt::Json for P_10279 {
    fn json(&self) -> String {
        vilan_rt::json_array(&[self.x.json(), self.big.json()])
    }
}

fn payload_10283() -> P_10279 {
    let mut big_10284: Vec<i32> = vec![];
    let mut i_10286 = (0i32);
    while (i_10286 < (10000i32)) {
        big_10284.push(i_10286);
        i_10286 = (i_10286 + (1i32));
    }
    P_10279 { x: (0i32), big: big_10284 }
}

fn through_variant_10304(held_10305: &mut E_10280, mut f_10306: std::rc::Rc<dyn Fn(&mut P_10279) -> ()>) -> () {
    match (held_10305).clone() {
        E_10280::A(mut p0_10309) => {
            (f_10306)(&mut p0_10309);
            (*held_10305) = E_10280::A((p0_10309).clone());
        },
        _ => {
        },
    }
}

fn direct_10323(held_10324: &mut P_10279, mut f_10325: std::rc::Rc<dyn Fn(&mut P_10279) -> ()>) -> () {
    (f_10325)(&mut *held_10324);
}

fn main() {
    vilan_rt::main_guard(|| {
    let mut e_10331 = E_10280::A(payload_10283());
    let t0_10336 = vilan_rt::time::now_millis();
    let mut n_10339 = (0i32);
    while (n_10339 < (2000i32)) {
        through_variant_10304(&mut e_10331, { std::rc::Rc::new(move |p_10350: &mut P_10279| { {
            p_10350.x = ((p_10350.x).clone() + (1i32));
        } }) as std::rc::Rc<dyn Fn(&mut P_10279) -> _> });
        n_10339 = (n_10339 + (1i32));
    }
    let t1_10366 = vilan_rt::time::now_millis();
    let mut s_10369 = payload_10283();
    n_10339 = (0i32);
    while (n_10339 < (2000i32)) {
        direct_10323(&mut s_10369, { std::rc::Rc::new(move |p_10384: &mut P_10279| { {
            p_10384.x = ((p_10384.x).clone() + (1i32));
        } }) as std::rc::Rc<dyn Fn(&mut P_10279) -> _> });
        n_10339 = (n_10339 + (1i32));
    }
    let t2_10400 = vilan_rt::time::now_millis();
    let x_10403 = match (e_10331).clone() {
        E_10280::A(p_10406) => p_10406.x,
        E_10280::B => (0i32),
        _ => vilan_rt::panic_with("unreachable match leg"),
    };
    vilan_rt::print(&(vilan_rt::str_concat(&vilan_rt::str_concat(&vilan_rt::str_concat(&vilan_rt::str_concat(&vilan_rt::str_new(""), &vilan_rt::str_new("(a) derive's through-variant write: ")), &vilan_rt::js_of(&((t1_10366 - t0_10336)))), &vilan_rt::str_new(" ms  x=")), &vilan_rt::js_of(&(x_10403)))));
    vilan_rt::print(&(vilan_rt::str_concat(&vilan_rt::str_concat(&vilan_rt::str_concat(&vilan_rt::str_concat(&vilan_rt::str_new(""), &vilan_rt::str_new("(b) direct, through a &mut lend:   ")), &vilan_rt::js_of(&((t2_10400 - t1_10366)))), &vilan_rt::str_new(" ms  x=")), &vilan_rt::js_of(&(s_10369.x)))));
    vilan_rt::executor::run_pending();
    });
}
