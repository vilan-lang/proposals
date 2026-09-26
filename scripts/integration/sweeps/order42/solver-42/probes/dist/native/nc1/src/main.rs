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
struct Turn_7147 {
    pending: vilan_rt::Shared<Vec<Subscriber_7069>>,
    pending_derived: vilan_rt::Shared<Vec<Subscriber_7069>>,
    queued: vilan_rt::Shared<vilan_rt::Map<vilan_rt::Hash, bool>>,
    queued_derived: vilan_rt::Shared<vilan_rt::Map<vilan_rt::Hash, bool>>,
    draining: vilan_rt::Shared<bool>,
    settled: vilan_rt::Shared<bool>,
    scheduled: vilan_rt::Shared<bool>,
}
impl vilan_rt::Js for Turn_7147 {
    fn js(&self) -> String {
        vilan_rt::js_tuple(&[self.pending.js_nested(), self.pending_derived.js_nested(), self.queued.js_nested(), self.queued_derived.js_nested(), self.draining.js_nested(), self.settled.js_nested(), self.scheduled.js_nested()])
    }
}
impl vilan_rt::Json for Turn_7147 {
    fn json(&self) -> String {
        vilan_rt::json_array(&[self.pending.json(), self.pending_derived.json(), self.queued.json(), self.queued_derived.json(), self.draining.json(), self.settled.json(), self.scheduled.json()])
    }
}

#[derive(Clone)]
struct Owner_7855 {
    cleanups: vilan_rt::Shared<Vec<std::rc::Rc<dyn Fn() -> ()>>>,
    disposed: vilan_rt::Shared<bool>,
}
impl PartialEq for Owner_7855 {
    fn eq(&self, other: &Self) -> bool {
        self.cleanups == other.cleanups && self.disposed == other.disposed
    }
}
impl vilan_rt::Js for Owner_7855 {
    fn js(&self) -> String {
        vilan_rt::panic_with("the rust backend cannot print a value holding \
                 a function")
    }
}
impl vilan_rt::Json for Owner_7855 {
    fn json(&self) -> String {
        vilan_rt::panic_with("the rust backend cannot hash or serialize a \
                 value holding a function")
    }
}

#[derive(Clone)]
struct Subscription_7615 {
    subscribers: vilan_rt::Weak<Vec<Subscriber_7069>>,
    id: i32,
    live: vilan_rt::Shared<bool>,
    release: vilan_rt::Shared<Option<std::rc::Rc<dyn Fn() -> ()>>>,
}
impl PartialEq for Subscription_7615 {
    fn eq(&self, other: &Self) -> bool {
        self.subscribers == other.subscribers && self.id == other.id && self.live == other.live && self.release == other.release
    }
}
impl vilan_rt::Js for Subscription_7615 {
    fn js(&self) -> String {
        vilan_rt::panic_with("the rust backend cannot print a value holding \
                 a function")
    }
}
impl vilan_rt::Json for Subscription_7615 {
    fn json(&self) -> String {
        vilan_rt::panic_with("the rust backend cannot hash or serialize a \
                 value holding a function")
    }
}

thread_local! {
    static MODULE_MINTING_DERIVATION_7074: vilan_rt::Shared<vilan_rt::Shared<bool>> = vilan_rt::Shared::new(vilan_rt::Shared::new(false));
}

thread_local! {
    static MODULE_NEXT_SUBSCRIBER_ID_7093: vilan_rt::Shared<vilan_rt::Shared<i32>> = vilan_rt::Shared::new(vilan_rt::Shared::new((0i32)));
}

thread_local! {
    static MODULE_DRAINING_TURNS_7191: vilan_rt::Shared<vilan_rt::Shared<Vec<Turn_7147>>> = vilan_rt::Shared::new(vilan_rt::Shared::new(vec![]));
}

thread_local! {
    static MODULE_RELEASING_TURNS_7195: vilan_rt::Shared<vilan_rt::Shared<Vec<Option<Turn_7147>>>> = vilan_rt::Shared::new(vilan_rt::Shared::new(vec![]));
}

fn new_8309_0(mut value_8310: i32) -> SignalCell_8212_0 {
    let mut subscribers_8311: Vec<Subscriber_7069> = vec![];
    SignalCell_8212_0 { value: vilan_rt::Shared::new(value_8310), subscribers: vilan_rt::Shared::new(subscribers_8311) }
}

fn cell_9203_0(this: &SignalCell_8212_0, mut context_15350: Option<Turn_7147>, mut context_15371: Option<Owner_7855>) -> SignalCell_8212_0 {
    let cached_9205 = new_8309_0(get_8225_0(&this));
    as_derivation_7079();
    let _owned_9212 = register_with_owner_7971(on_settle_8250_0(&this, mint_subscriber_7109({ let this = (*this).clone(); let cached_9205 = cached_9205.clone(); let context_15350 = context_15350.clone(); std::rc::Rc::new(move || { {
        set_8320_0(&cached_9205, get_8225_0(&this), (context_15350).clone());
    } }) })), (context_15350).clone(), (context_15371).clone());
    cached_9205
}

fn get_8225_0(this: &SignalCell_8212_0) -> i32 {
    (this.value).get()
}

fn as_derivation_7079() -> () {
    (MODULE_MINTING_DERIVATION_7074.with(|cell| cell.get())).set(true);
}

fn register_with_owner_7971(mut subscription_7972: Subscription_7615, mut context_15338: Option<Turn_7147>, mut context_15381: Option<Owner_7855>) -> Subscription_7615 {
    match (context_15381).clone() {
        Some(owner_7976) => take_7872_0(&owner_7976, (subscription_7972).clone(), (context_15338).clone()),
        None => subscription_7972,
        _ => vilan_rt::panic_with("unreachable match leg"),
    }
}

fn take_7872_0(this: &Owner_7855, mut item_7874: Subscription_7615, mut context_15319: Option<Turn_7147>) -> Subscription_7615 {
    if (this.disposed).get() {
        dispose_7690(&item_7874, (context_15319).clone());
    } else {
        (this.cleanups).borrow_mut().push({ let item_7874 = item_7874.clone(); let context_15319 = context_15319.clone(); std::rc::Rc::new(move || { {
            dispose_7690(&item_7874, (context_15319).clone());
        } }) });
    }
    item_7874
}

fn dispose_7690(this: &Subscription_7615, mut context_15327: Option<Turn_7147>) -> () {
    let ambient_7692 = match (context_15327).clone() {
        Some(established_7696) => Some(established_7696),
        None => last_6957_0(&(MODULE_DRAINING_TURNS_7191.with(|cell| cell.get())).get()),
        _ => vilan_rt::panic_with("unreachable match leg"),
    };
    release_under_7725((this).clone(), ambient_7692);
}

fn last_6957_0(this: &Vec<Turn_7147>) -> Option<Turn_7147> {
    vilan_rt::list_get(&this, (((this.len() as i32) - (1i32))) as i64)
}

fn release_under_7725(mut handle_7726: Subscription_7615, mut ambient_7727: Option<Turn_7147>) -> () {
    (handle_7726.live).set(false);
    match (handle_7726.subscribers).upgrade() {
        Some(subscribers_7737) => {
            let mut kept_7739: Vec<Subscriber_7069> = vec![];
            for subscriber_7744 in ((subscribers_7737).get()).clone().into_iter() {
                if (subscriber_7744.id != handle_7726.id) {
                    kept_7739.push((subscriber_7744).clone());
                }
            }
            (subscribers_7737).set(kept_7739);
        },
        None => {
        },
        _ => vilan_rt::panic_with("unreachable match leg"),
    };
    match (ambient_7727).clone() {
        Some(turn_7764) => {
            let mut kept_pending_7766: Vec<Subscriber_7069> = vec![];
            for subscriber_7772 in ((turn_7764.pending).get()).clone().into_iter() {
                if (subscriber_7772.id != handle_7726.id) {
                    kept_pending_7766.push((subscriber_7772).clone());
                }
            }
            (turn_7764.pending).set(kept_pending_7766);
            (turn_7764.queued).borrow_mut().remove(&hash_507(&handle_7726.id));
            let mut kept_derived_7795: Vec<Subscriber_7069> = vec![];
            for subscriber_7801 in ((turn_7764.pending_derived).get()).clone().into_iter() {
                if (subscriber_7801.id != handle_7726.id) {
                    kept_derived_7795.push((subscriber_7801).clone());
                }
            }
            (turn_7764.pending_derived).set(kept_derived_7795);
            (turn_7764.queued_derived).borrow_mut().remove(&hash_507(&handle_7726.id));
        },
        None => {
        },
        _ => vilan_rt::panic_with("unreachable match leg"),
    };
    match (handle_7726.release).get() {
        Some(release_7831) => {
            (handle_7726.release).set(None);
            (MODULE_RELEASING_TURNS_7195.with(|cell| cell.get())).borrow_mut().push(ambient_7727);
            { let body = (release_7831).clone(); let after = { std::rc::Rc::new(move || { {
                vilan_rt::list_pop(&mut (MODULE_RELEASING_TURNS_7195.with(|cell| cell.get())).borrow_mut());
            } }) }; vilan_rt::with_finally(move || body(), move || after()) };
        },
        None => {
        },
        _ => vilan_rt::panic_with("unreachable match leg"),
    }
}

fn hash_507(this: &i32) -> vilan_rt::Hash {
    vilan_rt::canonical_hash(&this)
}

fn on_settle_8250_0(this: &SignalCell_8212_0, mut subscriber_8252: Subscriber_7069) -> Subscription_7615 {
    attach_8283_0((this).clone(), subscriber_8252)
}

fn attach_8283_0(mut signal_8284: SignalCell_8212_0, mut subscriber_8285: Subscriber_7069) -> Subscription_7615 {
    (signal_8284.subscribers).borrow_mut().push(reissued_7514((subscriber_8285).clone()));
    Subscription_7615 { subscribers: (signal_8284.subscribers).downgrade(), id: subscriber_8285.id, live: (subscriber_8285.live).clone(), release: vilan_rt::Shared::new(None) }
}

fn reissued_7514(mut subscriber_7515: Subscriber_7069) -> Subscriber_7069 {
    Subscriber_7069 { id: subscriber_7515.id, notify: (subscriber_7515.notify).clone(), live: (subscriber_7515.live).clone(), derived: subscriber_7515.derived }
}

fn mint_subscriber_7109(mut notify_7110: std::rc::Rc<dyn Fn() -> ()>) -> Subscriber_7069 {
    let derived_7111 = (MODULE_MINTING_DERIVATION_7074.with(|cell| cell.get())).get();
    (MODULE_MINTING_DERIVATION_7074.with(|cell| cell.get())).set(false);
    subscriber_of_7122((notify_7110).clone(), derived_7111)
}

fn subscriber_of_7122(mut notify_7123: std::rc::Rc<dyn Fn() -> ()>, mut derived_7124: bool) -> Subscriber_7069 {
    Subscriber_7069 { id: fresh_id_7098(), notify: (notify_7123).clone(), live: vilan_rt::Shared::new(true), derived: derived_7124 }
}

fn fresh_id_7098() -> i32 {
    let id_7099 = (MODULE_NEXT_SUBSCRIBER_ID_7093.with(|cell| cell.get())).get();
    (MODULE_NEXT_SUBSCRIBER_ID_7093.with(|cell| cell.get())).set((id_7099 + (1i32)));
    id_7099
}

fn set_8320_0(this: &SignalCell_8212_0, mut value_8322: i32, mut context_15286: Option<Turn_7147>) -> () {
    (this.value).set((value_8322).clone());
    notify_8331_0(&this, (context_15286).clone());
}

fn notify_8331_0(this: &SignalCell_8212_0, mut context_15344: Option<Turn_7147>) -> () {
    match (context_15344).clone() {
        Some(turn_8336) => enqueue_7199(turn_8336, (this.subscribers).get()),
        None => {
            match last_6957_0(&(MODULE_DRAINING_TURNS_7191.with(|cell| cell.get())).get()) {
                Some(draining_8348) => enqueue_7199(draining_8348, (this.subscribers).get()),
                None => {
                    for subscriber_8360 in ((this.subscribers).get()).clone().into_iter() {
                        if (subscriber_8360.live).get() {
                            (subscriber_8360.notify)();
                        }
                    }
                },
                _ => vilan_rt::panic_with("unreachable match leg"),
            }
        },
        _ => vilan_rt::panic_with("unreachable match leg"),
    }
}

fn enqueue_7199(mut turn_7200: Turn_7147, mut subscribers_7201: Vec<Subscriber_7069>) -> () {
    for subscriber_7204 in (subscribers_7201).clone().into_iter() {
        let key_7205 = hash_507(&subscriber_7204.id);
        if subscriber_7204.derived {
            if !((turn_7200.queued_derived).get().contains_key(&key_7205)) {
                (turn_7200.queued_derived).borrow_mut().insert((key_7205).clone(), true);
                (turn_7200.pending_derived).borrow_mut().push((subscriber_7204).clone());
            }
        } else if !((turn_7200.queued).get().contains_key(&key_7205)) {
            (turn_7200.queued).borrow_mut().insert(key_7205, true);
            let mut index_7243 = ((turn_7200.pending).borrow_mut().len() as i32);
            while ((index_7243 > (0i32)) && ((turn_7200.pending).borrow_mut()[((index_7243 - (1i32))) as usize].id > subscriber_7204.id)) {
                index_7243 = (index_7243 - (1i32));
            }
            vilan_rt::list_insert(&mut (turn_7200.pending).borrow_mut(), (index_7243) as i64, (subscriber_7204).clone());
        }
    }
    if (((turn_7200.settled).get() && !((turn_7200.scheduled).get())) && !((turn_7200.draining).get())) {
        (turn_7200.scheduled).set(true);
        { let callback = { let turn_7200 = turn_7200.clone(); std::rc::Rc::new(move || { {
            (turn_7200.scheduled).set(false);
            drain_7311((turn_7200).clone());
        } }) }; vilan_rt::executor::queue_microtask(move || callback()) };
    }
}

fn drain_7311(mut turn_7312: Turn_7147) -> () {
    if !((turn_7312.draining).get()) {
        (turn_7312.draining).set(true);
        (MODULE_DRAINING_TURNS_7191.with(|cell| cell.get())).borrow_mut().push((turn_7312).clone());
        { let body = { let turn_7312 = turn_7312.clone(); std::rc::Rc::new(move || { {
            let mut budget_7331 = (100000i32);
            while (!(is_quiescent_7176(&turn_7312)) && (budget_7331 > (0i32))) {
                while (!(is_empty_2629_0(&(turn_7312.pending_derived).get())) && (budget_7331 > (0i32))) {
                    let derivations_7351 = (turn_7312.pending_derived).get();
                    (turn_7312.pending_derived).set(vec![]);
                    (turn_7312.queued_derived).set(vilan_rt::Map::new());
                    for subscriber_7368 in (derivations_7351).clone().into_iter() {
                        if (subscriber_7368.live).get() {
                            (subscriber_7368.notify)();
                        }
                        budget_7331 = (budget_7331 - (1i32));
                    }
                }
                let wave_7383 = (turn_7312.pending).get();
                (turn_7312.pending).set(vec![]);
                (turn_7312.queued).set(vilan_rt::Map::new());
                for subscriber_7400 in (wave_7383).clone().into_iter() {
                    if (subscriber_7400.live).get() {
                        (subscriber_7400.notify)();
                    }
                    budget_7331 = (budget_7331 - (1i32));
                }
            }
        } }) }; let after = { let turn_7312 = turn_7312.clone(); std::rc::Rc::new(move || { {
            vilan_rt::list_pop(&mut (MODULE_DRAINING_TURNS_7191.with(|cell| cell.get())).borrow_mut());
            (turn_7312.draining).set(false);
        } }) }; vilan_rt::with_finally(move || body(), move || after()) };
    }
}

fn is_empty_2629_0(this: &Vec<Subscriber_7069>) -> bool {
    ((this.len() as i32) == (0i32))
}

fn is_quiescent_7176(this: &Turn_7147) -> bool {
    (is_empty_2629_0(&(this.pending).get()) && is_empty_2629_0(&(this.pending_derived).get()))
}

fn main() {
    vilan_rt::main_guard(|| {
    let count_15200 = new_8309_0((1i32));
    let scaled_15204 = cell_9203_0(&count_15200, None, None);
    vilan_rt::print(&(get_8225_0(&scaled_15204)));
    vilan_rt::executor::run_pending();
    });
}
