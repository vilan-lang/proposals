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

#[derive(Clone, PartialEq)]
struct SignalCell_8212_1 {
    value: vilan_rt::Shared<vilan_rt::Str>,
    subscribers: vilan_rt::Shared<Vec<Subscriber_7069>>,
}
impl vilan_rt::Js for SignalCell_8212_1 {
    fn js(&self) -> String {
        vilan_rt::js_tuple(&[self.value.js_nested(), self.subscribers.js_nested()])
    }
}
impl vilan_rt::Json for SignalCell_8212_1 {
    fn json(&self) -> String {
        vilan_rt::json_array(&[self.value.json(), self.subscribers.json()])
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

fn cell_9203_0(this: &SignalCell_8212_0, mut context_15433: Option<Turn_7147>, mut context_15454: Option<Owner_7855>) -> SignalCell_8212_0 {
    let cached_9205 = new_8309_0(get_8225_0(&this));
    as_derivation_7079();
    let _owned_9212 = register_with_owner_7971(on_settle_8250_0(&this, mint_subscriber_7109({ let this = (*this).clone(); let cached_9205 = cached_9205.clone(); let context_15433 = context_15433.clone(); std::rc::Rc::new(move || { {
        set_8320_0(&cached_9205, get_8225_0(&this), (context_15433).clone());
    } }) })), (context_15433).clone(), (context_15454).clone());
    cached_9205
}

fn get_8225_0(this: &SignalCell_8212_0) -> i32 {
    (this.value).get()
}

fn as_derivation_7079() -> () {
    (MODULE_MINTING_DERIVATION_7074.with(|cell| cell.get())).set(true);
}

fn register_with_owner_7971(mut subscription_7972: Subscription_7615, mut context_15421: Option<Turn_7147>, mut context_15464: Option<Owner_7855>) -> Subscription_7615 {
    match (context_15464).clone() {
        Some(owner_7976) => take_7872_0(&owner_7976, (subscription_7972).clone(), (context_15421).clone()),
        None => subscription_7972,
        _ => vilan_rt::panic_with("unreachable match leg"),
    }
}

fn take_7872_0(this: &Owner_7855, mut item_7874: Subscription_7615, mut context_15402: Option<Turn_7147>) -> Subscription_7615 {
    if (this.disposed).get() {
        dispose_7690(&item_7874, (context_15402).clone());
    } else {
        (this.cleanups).borrow_mut().push({ let item_7874 = item_7874.clone(); let context_15402 = context_15402.clone(); std::rc::Rc::new(move || { {
            dispose_7690(&item_7874, (context_15402).clone());
        } }) });
    }
    item_7874
}

fn dispose_7690(this: &Subscription_7615, mut context_15410: Option<Turn_7147>) -> () {
    let ambient_7692 = match (context_15410).clone() {
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

fn set_8320_0(this: &SignalCell_8212_0, mut value_8322: i32, mut context_15369: Option<Turn_7147>) -> () {
    (this.value).set((value_8322).clone());
    notify_8331_0(&this, (context_15369).clone());
}

fn notify_8331_0(this: &SignalCell_8212_0, mut context_15427: Option<Turn_7147>) -> () {
    match (context_15427).clone() {
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
                while (!(is_empty_2643_0(&(turn_7312.pending_derived).get())) && (budget_7331 > (0i32))) {
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

fn is_empty_2643_0(this: &Vec<Subscriber_7069>) -> bool {
    ((this.len() as i32) == (0i32))
}

fn is_quiescent_7176(this: &Turn_7147) -> bool {
    (is_empty_2643_0(&(this.pending).get()) && is_empty_2643_0(&(this.pending_derived).get()))
}

fn map_8157_d0(this: &SignalCell_8212_0, mut transform_8159: std::rc::Rc<dyn Fn(i32) -> i32>, mut context_15383: Option<Turn_7147>, mut context_15444: Option<Owner_7855>) -> SignalCell_8212_0 {
    let derived_8161 = new_8309_0((transform_8159)(get_8225_0(&this)));
    as_derivation_7079();
    let _owned_8170 = register_with_owner_7971(on_change_8230_0(&this, { let transform_8159 = transform_8159.clone(); let derived_8161 = derived_8161.clone(); let context_15383 = context_15383.clone(); std::rc::Rc::new(move |mut value_8176: i32| { {
        set_8320_0(&derived_8161, (transform_8159)(value_8176), (context_15383).clone());
    } }) }), (context_15383).clone(), (context_15444).clone());
    derived_8161
}

fn on_change_8230_0(this: &SignalCell_8212_0, mut observer_8232: std::rc::Rc<dyn Fn(i32) -> ()>) -> Subscription_7615 {
    observe_8258_0((this).clone(), (observer_8232).clone())
}

fn observe_8258_0(mut signal_8259: SignalCell_8212_0, mut observer_8260: std::rc::Rc<dyn Fn(i32) -> ()>) -> Subscription_7615 {
    let cell_8262 = (signal_8259.value).downgrade();
    attach_8283_0(signal_8259, mint_subscriber_7109({ let observer_8260 = observer_8260.clone(); let cell_8262 = cell_8262.clone(); std::rc::Rc::new(move || { {
        match (cell_8262).upgrade() {
            Some(live_8276) => (observer_8260)((live_8276).get()),
            None => {
            },
            _ => vilan_rt::panic_with("unreachable match leg"),
        }
    } }) }))
}

fn cell_9203_1(this: &SignalCell_8212_1, mut context_15433: Option<Turn_7147>, mut context_15454: Option<Owner_7855>) -> SignalCell_8212_1 {
    let cached_9205 = new_8309_1(get_8225_1(&this));
    as_derivation_7079();
    let _owned_9212 = register_with_owner_7971(on_settle_8250_1(&this, mint_subscriber_7109({ let this = (*this).clone(); let cached_9205 = cached_9205.clone(); let context_15433 = context_15433.clone(); std::rc::Rc::new(move || { {
        set_8320_1(&cached_9205, get_8225_1(&this), (context_15433).clone());
    } }) })), (context_15433).clone(), (context_15454).clone());
    cached_9205
}

fn new_8309_1(mut value_8310: vilan_rt::Str) -> SignalCell_8212_1 {
    let mut subscribers_8311: Vec<Subscriber_7069> = vec![];
    SignalCell_8212_1 { value: vilan_rt::Shared::new(value_8310), subscribers: vilan_rt::Shared::new(subscribers_8311) }
}

fn get_8225_1(this: &SignalCell_8212_1) -> vilan_rt::Str {
    (this.value).get()
}

fn on_settle_8250_1(this: &SignalCell_8212_1, mut subscriber_8252: Subscriber_7069) -> Subscription_7615 {
    attach_8283_1((this).clone(), subscriber_8252)
}

fn attach_8283_1(mut signal_8284: SignalCell_8212_1, mut subscriber_8285: Subscriber_7069) -> Subscription_7615 {
    (signal_8284.subscribers).borrow_mut().push(reissued_7514((subscriber_8285).clone()));
    Subscription_7615 { subscribers: (signal_8284.subscribers).downgrade(), id: subscriber_8285.id, live: (subscriber_8285.live).clone(), release: vilan_rt::Shared::new(None) }
}

fn set_8320_1(this: &SignalCell_8212_1, mut value_8322: vilan_rt::Str, mut context_15369: Option<Turn_7147>) -> () {
    (this.value).set((value_8322).clone());
    notify_8331_1(&this, (context_15369).clone());
}

fn notify_8331_1(this: &SignalCell_8212_1, mut context_15427: Option<Turn_7147>) -> () {
    match (context_15427).clone() {
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

fn map_8157_d1(this: &SignalCell_8212_0, mut transform_8159: std::rc::Rc<dyn Fn(i32) -> vilan_rt::Str>, mut context_15383: Option<Turn_7147>, mut context_15444: Option<Owner_7855>) -> SignalCell_8212_1 {
    let derived_8161 = new_8309_1((transform_8159)(get_8225_0(&this)));
    as_derivation_7079();
    let _owned_8170 = register_with_owner_7971(on_change_8230_0(&this, { let transform_8159 = transform_8159.clone(); let derived_8161 = derived_8161.clone(); let context_15383 = context_15383.clone(); std::rc::Rc::new(move |mut value_8176: i32| { {
        set_8320_1(&derived_8161, (transform_8159)(value_8176), (context_15383).clone());
    } }) }), (context_15383).clone(), (context_15444).clone());
    derived_8161
}

fn distinct_9232_0(this: &SignalCell_8212_0) -> Distinct_9121_0 {
    Distinct_9121_0 { up: (this).clone() }
}

fn sub_8106_d0(this: &Distinct_9121_0, mut observer_8108: std::rc::Rc<dyn Fn(i32) -> ()>) -> Subscription_7615 {
    let subscription_8109 = on_change_9134_0(&this, (observer_8108).clone());
    (observer_8108)(get_9129_0(&this));
    subscription_8109
}

fn on_change_9134_0(this: &Distinct_9121_0, mut observer_9136: std::rc::Rc<dyn Fn(i32) -> ()>) -> Subscription_7615 {
    on_settle_9143_0(&this, pulling_8889_0((this).clone(), (observer_9136).clone()))
}

fn on_settle_9143_0(this: &Distinct_9121_0, mut subscriber_9145: Subscriber_7069) -> Subscription_7615 {
    let last_9146 = vilan_rt::Shared::new(pull_upstream_8915_0(&this.up));
    let relayed_9152 = settle_upstream_8919_0(&this.up, subscriber_of_7122({ let this = (*this).clone(); let subscriber_9145 = subscriber_9145.clone(); let last_9146 = last_9146.clone(); std::rc::Rc::new(move || { {
        let now_9160 = pull_upstream_8915_0(&this.up);
        if (now_9160 != (last_9146).get()) {
            (last_9146).set(now_9160);
            wake_7525((subscriber_9145).clone());
        }
    } }) }, true));
    also_retiring_7639((relayed_9152).clone(), subscriber_9145);
    relayed_9152
}

fn pull_upstream_8915_0(this: &SignalCell_8212_0) -> i32 {
    get_8225_0(&this)
}

fn settle_upstream_8919_0(this: &SignalCell_8212_0, mut subscriber_8921: Subscriber_7069) -> Subscription_7615 {
    on_settle_8250_0(&this, subscriber_8921)
}

fn wake_7525(mut subscriber_7526: Subscriber_7069) -> () {
    defer_subscriber_7479(None, subscriber_7526);
}

fn defer_subscriber_7479(mut turn_7480: Option<Turn_7147>, mut subscriber_7481: Subscriber_7069) -> () {
    match (turn_7480).clone() {
        Some(ambient_7484) => enqueue_7199(ambient_7484, vec![reissued_7514((subscriber_7481).clone())]),
        None => {
            match last_6957_0(&(MODULE_DRAINING_TURNS_7191.with(|cell| cell.get())).get()) {
                Some(draining_7497) => enqueue_7199(draining_7497, vec![reissued_7514((subscriber_7481).clone())]),
                None => {
                    if (subscriber_7481.live).get() {
                        (subscriber_7481.notify)();
                    }
                },
                _ => vilan_rt::panic_with("unreachable match leg"),
            }
        },
        _ => vilan_rt::panic_with("unreachable match leg"),
    }
}

fn also_retiring_7639(mut handle_7640: Subscription_7615, mut subscriber_7641: Subscriber_7069) -> () {
    let previous_7642 = (handle_7640.release).get();
    (handle_7640.release).set(Some({ let subscriber_7641 = subscriber_7641.clone(); let previous_7642 = previous_7642.clone(); std::rc::Rc::new(move || { {
        (subscriber_7641.live).set(false);
        match (previous_7642).clone() {
            Some(release_7658) => (release_7658)(),
            None => {
            },
            _ => vilan_rt::panic_with("unreachable match leg"),
        }
    } }) }));
}

fn pulling_8889_0(mut source_8890: Distinct_9121_0, mut observer_8891: std::rc::Rc<dyn Fn(i32) -> ()>) -> Subscriber_7069 {
    mint_subscriber_7109({ let source_8890 = source_8890.clone(); let observer_8891 = observer_8891.clone(); std::rc::Rc::new(move || { (observer_8891)(get_9129_0(&source_8890)) }) })
}

fn get_9129_0(this: &Distinct_9121_0) -> i32 {
    pull_upstream_8915_0(&this.up)
}

fn main() {
    vilan_rt::main_guard(|| {
    let count_15201 = new_8309_0((1i32));
    let scaled_15205 = cell_9203_0(&map_8157_d0(&count_15201, { std::rc::Rc::new(move |mut n_15210: i32| { (n_15210 * (10i32)) }) }, None, None), None, None);
    let labelled_15214 = cell_9203_1(&map_8157_d1(&scaled_15205, { std::rc::Rc::new(move |mut n_15219: i32| { vilan_rt::str_concat(&vilan_rt::str_concat(&vilan_rt::str_new(""), &vilan_rt::str_new("#")), &vilan_rt::js_of(&(n_15219))) }) }, None, None), None, None);
    let parity_15225 = distinct_9232_0(&map_8157_d0(&count_15201, { std::rc::Rc::new(move |mut n_15230: i32| { (n_15230 % (2i32)) }) }, None, None));
    let changes_15234 = vilan_rt::Captured::new((0i32));
    let _watch_15236 = sub_8106_d0(&parity_15225, { let changes_15234 = changes_15234.clone(); std::rc::Rc::new(move |mut value_15240: i32| { {
        changes_15234.set(((changes_15234.get()).clone() + (1i32)));
    } }) });
    set_8320_0(&count_15201, (3i32), None);
    set_8320_0(&count_15201, (4i32), None);
    set_8320_0(&count_15201, (6i32), None);
    let now_15257 = get_8225_0(&scaled_15205);
    let label_15260 = get_8225_1(&labelled_15214);
    let odd_15263 = get_9129_0(&parity_15225);
    vilan_rt::print(&(vilan_rt::str_concat(&vilan_rt::str_concat(&vilan_rt::str_concat(&vilan_rt::str_concat(&vilan_rt::str_concat(&vilan_rt::str_concat(&vilan_rt::str_concat(&vilan_rt::str_new(""), &vilan_rt::js_of(&(now_15257))), &vilan_rt::str_new(" ")), &label_15260), &vilan_rt::str_new(" ")), &vilan_rt::js_of(&(odd_15263))), &vilan_rt::str_new(" ")), &vilan_rt::js_of(&(changes_15234.get())))));
    vilan_rt::executor::run_pending();
    });
}
