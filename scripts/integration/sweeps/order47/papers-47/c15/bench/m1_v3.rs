#![allow(unused_imports, unused_parens, unused_variables, unused_mut, unused_braces)]
#![allow(dead_code)]
#![allow(unreachable_patterns, non_camel_case_types, non_snake_case, clippy::all)]
use vilan_rt::Js as _;
use vilan_rt::Json as _;

#[inline(never)]
fn with_value_9420(mut seed_9421: i32, f_9422: &dyn Fn(i32) -> ()) -> () {
    (f_9422)((seed_9421 * (3i32)));
}

fn main() {
    vilan_rt::main_guard(|| {
    let mut total_9430 = (0i32);
    let mut k_9432 = (0i32);
    while (k_9432 < (200000i32)) {
        let seed_9438 = (k_9432 % (7i32));
        let out_9442 = vilan_rt::Captured::new((0i32));
        with_value_9420(seed_9438, &(|mut v_9448: i32| { {
            { let __assigned = (v_9448 + (1i32)); out_9442.set(__assigned); };
        } }));
        total_9430 = (total_9430 + out_9442.get());
        k_9432 = (k_9432 + (1i32));
    }
    vilan_rt::print(&(total_9430));
    vilan_rt::executor::run_pending();
    });
}
