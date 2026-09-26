#![allow(unused_imports, unused_parens, unused_variables, unused_mut, unused_braces)]
#![allow(dead_code)]
#![allow(unreachable_patterns, non_camel_case_types, non_snake_case, clippy::all)]
use vilan_rt::Js as _;
use vilan_rt::Json as _;

#[derive(Clone, PartialEq)]
struct SignalCell_8212_0 {
    value: vilan_rt::Shared<i32>,
    subscribers: vilan_rt::Shared<Vec<Subscriber_7069>>,
}
impl vilan_rt::Js for SignalCell_8212_0 {
    fn js(&self) -> String {
        vilan_rt::js_tuple(&[self.value.js_nested(), self.subscribers.js_nested()])
    }
}
impl vilan_rt::Json for SignalCell_8212_0 {
    fn json(&self) -> String {
        vilan_rt::json_array(&[self.value.json(), self.subscribers.json()])
    }
}

#[derive(Clone)]
struct Subscriber_7069 {
    id: i32,
    notify: std::rc::Rc<dyn Fn() -> ()>,
    live: vilan_rt::Shared<bool>,
    derived: bool,
}
impl PartialEq for Subscriber_7069 {
    fn eq(&self, other: &Self) -> bool {
        self.id == other.id && std::rc::Rc::ptr_eq(&self.notify, &other.notify) && self.live == other.live && self.derived == other.derived
    }
}
impl vilan_rt::Js for Subscriber_7069 {
    fn js(&self) -> String {
        vilan_rt::panic_with("the rust backend cannot print a value holding \
                 a function")
    }
}
impl vilan_rt::Json for Subscriber_7069 {
    fn json(&self) -> String {
        vilan_rt::panic_with("the rust backend cannot hash or serialize a \
                 value holding a function")
    }
}

#[derive(Clone, PartialEq)]
struct Distinct_9121_0 {
    up: SignalCell_8212_0,
}
impl vilan_rt::Js for Distinct_9121_0 {
    fn js(&self) -> String {
        vilan_rt::js_tuple(&[self.up.js_nested()])
    }
}
impl vilan_rt::Json for Distinct_9121_0 {
    fn json(&self) -> String {
        vilan_rt::json_array(&[self.up.json()])
    }
}

fn new_8309_0(mut value_8310: i32) -> SignalCell_8212_0 {
    let mut subscribers_8311: Vec<Subscriber_7069> = vec![];
    SignalCell_8212_0 { value: vilan_rt::Shared::new(value_8310), subscribers: vilan_rt::Shared::new(subscribers_8311) }
}

fn distinct_9232_0(this: &SignalCell_8212_0) -> Distinct_9121_0 {
    Distinct_9121_0 { up: (this).clone() }
}

fn get_9129_0(this: &Distinct_9121_0) -> i32 {
    pull_upstream_8915_0(&this.up)
}

fn pull_upstream_8915_0(this: &SignalCell_8212_0) -> i32 {
    get_8225_0(&this)
}

fn get_8225_0(this: &SignalCell_8212_0) -> i32 {
    (this.value).get()
}

fn main() {
    vilan_rt::main_guard(|| {
    let count_15200 = new_8309_0((1i32));
    let parity_15204 = distinct_9232_0(&count_15200);
    vilan_rt::print(&(get_9129_0(&parity_15204)));
    vilan_rt::executor::run_pending();
    });
}
