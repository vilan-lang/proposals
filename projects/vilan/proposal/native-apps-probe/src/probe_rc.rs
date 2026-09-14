//! Probe A — `board.vl` hand-translated to Rust with C14 representation (a):
//! the reactive cell is a real `Rc<RefCell<..>>` with deterministic drop, and
//! the cell -> subscriber -> closure -> cell back edge is broken by `Weak`.
//!
//! Emitter conventions used here (this is what the emitter would have to
//! generate; nothing is hand-optimised beyond what the last-use pass already
//! computes today):
//!   * `str`        -> `Rc<str>`     (immutable; a rule-1 copy is a refcount bump)
//!   * `List<T>`    -> `Vec<T>`      (rule-1 copy = `.clone()`, elided at last use)
//!   * `struct`     -> `#[derive(Clone)] struct`
//!   * a captured MUTABLE binding (spec §6.9) -> `Rc<RefCell<T>>`
//!   * `print`      -> `println!`
//!   * `panic`      -> `std::panic::panic_any` / `catch_unwind` for `guarded`

use std::cell::RefCell;
use std::rc::{Rc, Weak};

// ---------------------------------------------------------------- runtime ---

/// std::reactive's `Subscriber`. `notify` is a boxed `Fn` — vilan closures are
/// not `Copy`, may be stored in a `List`, and capture bindings, so `Rc<dyn Fn>`
/// is the shape (an `Rc`, not a `Box`, because the subscriber list is itself
/// copied by rule 1 in several std paths).
#[derive(Clone)]
struct Subscriber {
    id: i32,
    notify: Rc<dyn Fn()>,
}

thread_local! {
    static NEXT_SUBSCRIBER_ID: RefCell<i32> = const { RefCell::new(0) };
}

fn fresh_id() -> i32 {
    NEXT_SUBSCRIBER_ID.with(|c| {
        let id = *c.borrow();
        *c.borrow_mut() = id + 1;
        id
    })
}

/// The cell body. `SignalCell<T>` in vilan is a plain struct copied by rule 1;
/// on native it becomes a handle to this, so the handle is what copies.
struct CellBody<T> {
    value: T,
    subscribers: Vec<Subscriber>,
    /// M66's lazily stamped identity: `None` until someone asks.
    id: RefCell<Option<i32>>,
}

/// `SignalCell<T>` — the vilan-visible value. Cloning it is `Shared::clone`:
/// another handle to the SAME cell, retaining.
struct SignalCell<T> {
    inner: Rc<RefCell<CellBody<T>>>,
}

impl<T> Clone for SignalCell<T> {
    fn clone(&self) -> Self {
        SignalCell {
            inner: Rc::clone(&self.inner),
        }
    }
}

/// The non-retaining twin the subscriber closure holds — destruction.md §10's
/// `Weak<T>`/C1. This is the edge that would otherwise make every subscription
/// a cycle.
struct WeakCell<T> {
    inner: Weak<RefCell<CellBody<T>>>,
}

impl<T: Clone + 'static> SignalCell<T> {
    fn new(value: T) -> SignalCell<T> {
        SignalCell {
            inner: Rc::new(RefCell::new(CellBody {
                value,
                subscribers: Vec::new(),
                id: RefCell::new(None),
            })),
        }
    }

    fn downgrade(&self) -> WeakCell<T> {
        WeakCell {
            inner: Rc::downgrade(&self.inner),
        }
    }

    /// `get(self): T` — a rule-1 value return, so it copies.
    fn get(&self) -> T {
        self.inner.borrow().value.clone()
    }

    /// M66: `Shared::identity` stamps on first read.
    fn identity(&self) -> i32 {
        let body = self.inner.borrow();
        let mut slot = body.id.borrow_mut();
        match *slot {
            Some(id) => id,
            None => {
                let id = fresh_id();
                *slot = Some(id);
                id
            }
        }
    }

    fn set(&self, value: T) {
        self.inner.borrow_mut().value = value;
        self.notify();
    }

    fn notify(&self) {
        // The subscriber list is cloned out before the walk: a notify may
        // `set`, and holding the `RefCell` borrow across an arbitrary closure
        // is the native equivalent of JS's re-entrancy hazard (it would panic
        // rather than corrupt, which is the honest native answer).
        let subscribers = self.inner.borrow().subscribers.clone();
        for subscriber in subscribers {
            (subscriber.notify)();
        }
    }

    /// `observe` — std/reactive.vl's comment already says the notify closure
    /// must capture the VALUE CELL and not the signal. Under `Rc` it must
    /// capture a WEAK cell, or the closure in the cell's own subscriber list
    /// keeps the cell alive forever.
    fn sub(&self, observer: impl Fn(T) + 'static) -> Subscription<T> {
        // PROBE FINDING R-1: a vilan closure VALUE is used in two places here
        // (stored in the subscriber list, then called once immediately), and
        // `impl Fn` is moved by the first use. Every closure that crosses a
        // parameter boundary must therefore be boxed into a counted handle at
        // the boundary — `Rc<dyn Fn(..)>` — not taken by value.
        let observer: Rc<dyn Fn(T)> = Rc::new(observer);
        let id = fresh_id();
        let weak = self.downgrade();
        let observer_for_list = Rc::clone(&observer);
        self.inner.borrow_mut().subscribers.push(Subscriber {
            id,
            notify: Rc::new(move || {
                if let Some(cell) = weak.inner.upgrade() {
                    let value = cell.borrow().value.clone();
                    observer_for_list(value);
                }
            }),
        });
        observer(self.get());
        Subscription {
            cell: self.downgrade(),
            id,
        }
    }
}

/// `Subscription` holds the subscriber list. Weak again: a live subscription
/// must not be what keeps a dead cell alive.
struct Subscription<T> {
    cell: WeakCell<T>,
    id: i32,
}

trait Disposable {
    fn dispose(&self);
}

impl<T> Disposable for Subscription<T> {
    fn dispose(&self) {
        if let Some(cell) = self.cell.inner.upgrade() {
            cell.borrow_mut().subscribers.retain(|s| s.id != self.id);
        }
    }
}

/// `Owner` — its two `Shared` boxes become one `Rc<RefCell<..>>` body.
#[derive(Clone)]
struct Owner {
    inner: Rc<RefCell<OwnerBody>>,
}

struct OwnerBody {
    cleanups: Vec<Rc<dyn Fn()>>,
    disposed: bool,
}

impl Owner {
    fn new() -> Owner {
        Owner {
            inner: Rc::new(RefCell::new(OwnerBody {
                cleanups: Vec::new(),
                disposed: false,
            })),
        }
    }

    fn take<T: Disposable + 'static>(&self, item: T) -> Rc<T> {
        let item = Rc::new(item);
        if self.inner.borrow().disposed {
            item.dispose();
        } else {
            let held = Rc::clone(&item);
            self.inner
                .borrow_mut()
                .cleanups
                .push(Rc::new(move || held.dispose()));
        }
        item
    }
}

impl Disposable for Owner {
    fn dispose(&self) {
        if !self.inner.borrow().disposed {
            self.inner.borrow_mut().disposed = true;
            let cleanups = std::mem::take(&mut self.inner.borrow_mut().cleanups);
            let mut failure: Option<String> = None;
            for cleanup in cleanups {
                // `guarded` — every cleanup runs past a throwing one.
                let outcome = std::panic::catch_unwind(std::panic::AssertUnwindSafe(|| cleanup()));
                if let Err(payload) = outcome {
                    if failure.is_none() {
                        failure = Some(describe_panic(payload));
                    }
                }
            }
            if let Some(message) = failure {
                panic!("{message}");
            }
        }
    }
}

fn describe_panic(payload: Box<dyn std::any::Any + Send>) -> String {
    if let Some(s) = payload.downcast_ref::<&str>() {
        (*s).to_string()
    } else if let Some(s) = payload.downcast_ref::<String>() {
        s.clone()
    } else {
        "panicked".to_string()
    }
}

// ------------------------------------------------------------ user program ---

#[derive(Clone)]
struct Todo {
    #[allow(dead_code)]
    id: i32,
    #[allow(dead_code)]
    title: Rc<str>,
    done: bool,
}

#[derive(Clone)]
struct Board {
    #[allow(dead_code)]
    name: Rc<str>,
    todos: Vec<Todo>,
}

impl Board {
    fn new(name: Rc<str>) -> Board {
        Board {
            name,
            todos: Vec::new(),
        }
    }

    fn add(&mut self, todo: Todo) {
        self.todos.push(todo);
    }

    /// `fun open(self): i32` — a BARE `self` is a loan (§6.8 R3), so `&self`.
    fn open(&self) -> i32 {
        let mut n = 0;
        // `for todo in self.todos` iterates a place it does not own: a read-only
        // temporary, so no copy (spec §6.1's "a temporary that only reads").
        for todo in &self.todos {
            if !todo.done {
                n += 1;
            }
        }
        n
    }
}

fn main() {
    let mut board = Board::new("inbox".into());
    board.add(Todo {
        id: 1,
        title: "write the paper".into(),
        done: false,
    });
    board.add(Todo {
        id: 2,
        title: "read the census".into(),
        done: true,
    });

    // Rule 1: `mut snapshot = board.todos` COPIES. The emitter cannot elide
    // this one — `board.todos` is read again below.
    let mut snapshot = board.todos.clone();
    snapshot.push(Todo {
        id: 3,
        title: "ghost".into(),
        done: false,
    });
    println!("{}", board.todos.len()); // 2
    println!("{}", snapshot.len()); // 3

    let count: SignalCell<i32> = SignalCell::new(board.open());

    // §6.9: `seen` is a binding captured by a closure AND read after it. The
    // emitter has no choice: a mutably-captured binding becomes a shared cell.
    let seen: Rc<RefCell<Vec<i32>>> = Rc::new(RefCell::new(Vec::new()));

    let owner = Owner::new();
    let seen_in_closure = Rc::clone(&seen);
    let _sub = owner.take(count.sub(move |value| {
        seen_in_closure.borrow_mut().push(value);
    }));

    board.add(Todo {
        id: 4,
        title: "ship it".into(),
        done: false,
    });
    count.set(board.open());

    println!("{}", seen.borrow().len()); // 2
    owner.dispose();
    count.set(99);
    println!("{}", seen.borrow().len()); // 2
    println!("{}", count.get()); // 99 — the ghost read, preserved

    // Beyond the .vl program: what the REPRESENTATION buys, printed so the
    // probe measures it rather than asserting it.
    println!("identity={}", count.identity());
    println!("strong={} weak={}", Rc::strong_count(&count.inner), Rc::weak_count(&count.inner));
    drop(_sub);
    drop(owner);
    let weak = count.downgrade();
    drop(count);
    println!("after-drop-upgrade-is-none={}", weak.inner.upgrade().is_none());
}
