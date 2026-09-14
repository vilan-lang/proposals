//! Probe B — the same `board.vl`, hand-translated with C14 representation (b):
//! owner-attached generational storage. A cell is PLAIN DATA (four integers);
//! the values live in a program-wide slab partitioned by owner; disposing an
//! owner bumps its partition's generation and frees the partition wholesale,
//! so every handle into it reads `None` instead of a ghost value.
//!
//! Two facts this shape forces, both recorded in the paper:
//!   * `Arena<T>` is generic, and one owner owns cells of MANY types, so the
//!     slot must be type-erased (`Box<dyn Any>` here) with a downcast per read.
//!   * a handle is pure data, so it needs a ROOT to look up through: the slab
//!     is a thread-local. That is one shared root for the program instead of
//!     one counted box per cell field.

use std::any::Any;
use std::cell::RefCell;
use std::marker::PhantomData;
use std::rc::Rc;

// ---------------------------------------------------------------- the slab ---

#[derive(Clone)]
struct Subscriber {
    id: i32,
    notify: Rc<dyn Fn()>,
}

struct Slot {
    generation: u32,
    value: Option<Box<dyn Any>>,
    subscribers: Vec<Subscriber>,
    /// M66's lazily stamped identity.
    identity: Option<i32>,
}

struct Partition {
    /// Bumped on disposal: every handle minted under the old value goes stale.
    generation: u32,
    slots: Vec<Slot>,
    free: Vec<u32>,
    cleanups: Vec<Rc<dyn Fn()>>,
    disposed: bool,
}

struct Slab {
    partitions: Vec<Partition>,
    next_subscriber_id: i32,
}

thread_local! {
    static SLAB: RefCell<Slab> = RefCell::new(Slab {
        // Partition 0 is the ROOT partition: module-level cells live here and
        // it is never disposed.
        partitions: vec![Partition {
            generation: 0,
            slots: Vec::new(),
            free: Vec::new(),
            cleanups: Vec::new(),
            disposed: false,
        }],
        next_subscriber_id: 0,
    });
}

fn fresh_id() -> i32 {
    SLAB.with(|s| {
        let mut slab = s.borrow_mut();
        let id = slab.next_subscriber_id;
        slab.next_subscriber_id = id + 1;
        id
    })
}

/// `Owner` — eight bytes of plain data, `Copy`, storable in a struct field and
/// on the wire.
#[derive(Clone, Copy, PartialEq, Eq, Debug)]
struct Owner {
    partition: u32,
    generation: u32,
}

const ROOT: Owner = Owner {
    partition: 0,
    generation: 0,
};

impl Owner {
    fn new() -> Owner {
        SLAB.with(|s| {
            let mut slab = s.borrow_mut();
            let partition = slab.partitions.len() as u32;
            slab.partitions.push(Partition {
                generation: 0,
                slots: Vec::new(),
                free: Vec::new(),
                cleanups: Vec::new(),
                disposed: false,
            });
            Owner {
                partition,
                generation: 0,
            }
        })
    }

    fn is_live(self) -> bool {
        SLAB.with(|s| {
            s.borrow()
                .partitions
                .get(self.partition as usize)
                .is_some_and(|p| p.generation == self.generation && !p.disposed)
        })
    }

    fn defer(self, cleanup: Rc<dyn Fn()>) {
        let live = self.is_live();
        if live {
            SLAB.with(|s| {
                s.borrow_mut().partitions[self.partition as usize]
                    .cleanups
                    .push(cleanup);
            });
        } else {
            cleanup();
        }
    }

    /// Disposal: run the cleanups, then free the whole partition and bump its
    /// generation. No per-cell teardown, no counting, no cycle to break.
    fn dispose(self) {
        if !self.is_live() {
            return;
        }
        let cleanups = SLAB.with(|s| {
            let mut slab = s.borrow_mut();
            let partition = &mut slab.partitions[self.partition as usize];
            partition.disposed = true;
            std::mem::take(&mut partition.cleanups)
        });
        let mut failure: Option<String> = None;
        for cleanup in cleanups {
            let outcome = std::panic::catch_unwind(std::panic::AssertUnwindSafe(|| cleanup()));
            if let Err(payload) = outcome {
                if failure.is_none() {
                    failure = Some(describe_panic(payload));
                }
            }
        }
        SLAB.with(|s| {
            let mut slab = s.borrow_mut();
            let partition = &mut slab.partitions[self.partition as usize];
            // THE WHOLESALE FREE — one line, O(1) in the number of cells for
            // the drop of the Vec, and every outstanding handle goes stale.
            partition.slots.clear();
            partition.free.clear();
            partition.generation += 1;
            partition.disposed = false;
        });
        if let Some(message) = failure {
            panic!("{message}");
        }
    }
}

fn describe_panic(payload: Box<dyn Any + Send>) -> String {
    if let Some(s) = payload.downcast_ref::<&str>() {
        (*s).to_string()
    } else if let Some(s) = payload.downcast_ref::<String>() {
        s.clone()
    } else {
        "panicked".to_string()
    }
}

/// `SignalCell<T>` — sixteen bytes of plain data. `Copy`, so rule 1's copy is
/// free and nothing counts.
struct SignalCell<T> {
    partition: u32,
    partition_generation: u32,
    index: u32,
    generation: u32,
    _t: PhantomData<T>,
}

impl<T> Clone for SignalCell<T> {
    fn clone(&self) -> Self {
        *self
    }
}
impl<T> Copy for SignalCell<T> {}

impl<T: Clone + 'static> SignalCell<T> {
    fn new_in(owner: Owner, value: T) -> SignalCell<T> {
        SLAB.with(|s| {
            let mut slab = s.borrow_mut();
            let partition_generation = slab.partitions[owner.partition as usize].generation;
            let partition = &mut slab.partitions[owner.partition as usize];
            let (index, generation) = match partition.free.pop() {
                Some(index) => {
                    let slot = &mut partition.slots[index as usize];
                    slot.value = Some(Box::new(value));
                    slot.subscribers.clear();
                    slot.identity = None;
                    (index, slot.generation)
                }
                None => {
                    let index = partition.slots.len() as u32;
                    let generation = partition.generation;
                    partition.slots.push(Slot {
                        generation,
                        value: Some(Box::new(value)),
                        subscribers: Vec::new(),
                        identity: None,
                    });
                    (index, generation)
                }
            };
            SignalCell {
                partition: owner.partition,
                partition_generation,
                index,
                generation,
                _t: PhantomData,
            }
        })
    }

    fn is_live(self) -> bool {
        SLAB.with(|s| {
            let slab = s.borrow();
            slab.partitions
                .get(self.partition as usize)
                .is_some_and(|p| {
                    p.generation == self.partition_generation
                        && p.slots
                            .get(self.index as usize)
                            .is_some_and(|slot| slot.generation == self.generation)
                })
        })
    }

    /// THE SEMANTIC CHANGE. `get` on a cell whose owner is disposed answers
    /// `None`, where today it answers the last value forever.
    fn try_get(self) -> Option<T> {
        SLAB.with(|s| {
            let slab = s.borrow();
            let partition = slab.partitions.get(self.partition as usize)?;
            if partition.generation != self.partition_generation {
                return None;
            }
            let slot = partition.slots.get(self.index as usize)?;
            if slot.generation != self.generation {
                return None;
            }
            slot.value.as_ref()?.downcast_ref::<T>().cloned()
        })
    }

    fn identity(self) -> Option<i32> {
        SLAB.with(|s| {
            let mut slab = s.borrow_mut();
            let next = slab.next_subscriber_id;
            let partition = slab.partitions.get_mut(self.partition as usize)?;
            if partition.generation != self.partition_generation {
                return None;
            }
            let slot = partition.slots.get_mut(self.index as usize)?;
            if slot.generation != self.generation {
                return None;
            }
            match slot.identity {
                Some(id) => Some(id),
                None => {
                    slot.identity = Some(next);
                    slab.next_subscriber_id = next + 1;
                    Some(next)
                }
            }
        })
    }

    fn set(self, value: T) {
        let wrote = SLAB.with(|s| {
            let mut slab = s.borrow_mut();
            let Some(partition) = slab.partitions.get_mut(self.partition as usize) else {
                return false;
            };
            if partition.generation != self.partition_generation {
                return false;
            }
            let Some(slot) = partition.slots.get_mut(self.index as usize) else {
                return false;
            };
            if slot.generation != self.generation {
                return false;
            }
            slot.value = Some(Box::new(value));
            true
        });
        if wrote {
            self.notify();
        }
    }

    fn notify(self) {
        let subscribers = SLAB.with(|s| {
            let slab = s.borrow();
            slab.partitions
                .get(self.partition as usize)
                .filter(|p| p.generation == self.partition_generation)
                .and_then(|p| p.slots.get(self.index as usize))
                .filter(|slot| slot.generation == self.generation)
                .map(|slot| slot.subscribers.clone())
                .unwrap_or_default()
        });
        for subscriber in subscribers {
            (subscriber.notify)();
        }
    }

    /// The subscriber's closure captures the HANDLE — plain data, no back edge,
    /// no `Weak`, nothing to break. This is the whole argument for (b).
    fn sub(self, observer: impl Fn(T) + 'static) -> Subscription<T> {
        let observer: Rc<dyn Fn(T)> = Rc::new(observer);
        let id = fresh_id();
        let observer_for_list = Rc::clone(&observer);
        let cell = self;
        SLAB.with(|s| {
            let mut slab = s.borrow_mut();
            if let Some(partition) = slab.partitions.get_mut(cell.partition as usize) {
                if partition.generation == cell.partition_generation {
                    if let Some(slot) = partition.slots.get_mut(cell.index as usize) {
                        slot.subscribers.push(Subscriber {
                            id,
                            notify: Rc::new(move || {
                                if let Some(value) = cell.try_get() {
                                    observer_for_list(value);
                                }
                            }),
                        });
                    }
                }
            }
        });
        if let Some(value) = self.try_get() {
            observer(value);
        }
        Subscription { cell: self, id }
    }
}

#[derive(Clone, Copy)]
struct Subscription<T> {
    cell: SignalCell<T>,
    id: i32,
}

impl<T: Clone + 'static> Subscription<T> {
    fn dispose(self) {
        SLAB.with(|s| {
            let mut slab = s.borrow_mut();
            if let Some(partition) = slab.partitions.get_mut(self.cell.partition as usize) {
                if partition.generation == self.cell.partition_generation {
                    if let Some(slot) = partition.slots.get_mut(self.cell.index as usize) {
                        slot.subscribers.retain(|s| s.id != self.id);
                    }
                }
            }
        });
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
    fn open(&self) -> i32 {
        let mut n = 0;
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

    let mut snapshot = board.todos.clone();
    snapshot.push(Todo {
        id: 3,
        title: "ghost".into(),
        done: false,
    });
    println!("{}", board.todos.len()); // 2
    println!("{}", snapshot.len()); // 3

    let owner = Owner::new();
    // The cell is minted INTO an owner — the call now needs one, which is the
    // API change the paper prices. `ROOT` is the module-level answer.
    let count: SignalCell<i32> = SignalCell::new_in(owner, board.open());
    let _root_example: SignalCell<i32> = SignalCell::new_in(ROOT, 0);

    let seen: Rc<RefCell<Vec<i32>>> = Rc::new(RefCell::new(Vec::new()));
    let seen_in_closure = Rc::clone(&seen);
    let sub = count.sub(move |value| {
        seen_in_closure.borrow_mut().push(value);
    });
    owner.defer(Rc::new(move || sub.dispose()));

    board.add(Todo {
        id: 4,
        title: "ship it".into(),
        done: false,
    });
    count.set(board.open());

    println!("{}", seen.borrow().len()); // 2
    println!("identity={:?}", count.identity());
    owner.dispose();
    count.set(99); // a write to a dead cell: silently dropped
    println!("{}", seen.borrow().len()); // 2
    // THE DIFFERENCE: no ghost. `get` after disposal is `None`.
    println!("after-dispose-get={:?}", count.try_get());
    println!("cell-live={} owner-live={}", count.is_live(), owner.is_live());
    println!("root-cell-live={}", _root_example.is_live());
    println!(
        "handle-size={} owner-size={}",
        std::mem::size_of::<SignalCell<i32>>(),
        std::mem::size_of::<Owner>()
    );
}
