//! TEMPORARY timing probes (incr-50 measurement; not for commit).
thread_local! {
    static LAST: std::cell::Cell<Option<std::time::Instant>> = const { std::cell::Cell::new(None) };
    static ACC: std::cell::RefCell<Vec<(&'static str, f64)>> = const { std::cell::RefCell::new(Vec::new()) };
}
pub(crate) fn on() -> bool {
    static ON: std::sync::OnceLock<bool> = std::sync::OnceLock::new();
    *ON.get_or_init(|| std::env::var("VILAN_CTX_PROBE").is_ok())
}
fn cpu_now() -> f64 {
    let mut ts = libc_timespec { tv_sec: 0, tv_nsec: 0 };
    unsafe { clock_gettime(3, &mut ts) };
    ts.tv_sec as f64 * 1000.0 + ts.tv_nsec as f64 / 1e6
}
#[repr(C)]
struct libc_timespec { tv_sec: i64, tv_nsec: i64 }
unsafe extern "C" { fn clock_gettime(clk: i32, ts: *mut libc_timespec) -> i32; }
thread_local! { static LAST_CPU: std::cell::Cell<f64> = const { std::cell::Cell::new(0.0) }; }
pub(crate) fn start() {
    if on() { LAST.with(|l| l.set(Some(std::time::Instant::now()))); LAST_CPU.with(|c| c.set(cpu_now())); ACC.with(|a| a.borrow_mut().clear()); }
}
pub(crate) fn probe(label: &'static str) {
    if !on() { return; }
    let now = std::time::Instant::now();
    let cpu = cpu_now();
    let _last = LAST.with(|l| l.replace(Some(now))).unwrap_or(now);
    let last_cpu = LAST_CPU.with(|c| c.replace(cpu));
    let ms = cpu - last_cpu;
    ACC.with(|a| { let mut a = a.borrow_mut(); if let Some(row) = a.iter_mut().find(|(l, _)| *l == label) { row.1 += ms; } else { a.push((label, ms)); } });
}
pub(crate) fn report(head: &str) {
    if !on() { return; }
    ACC.with(|a| { let a = a.borrow(); let total: f64 = a.iter().map(|r| r.1).sum(); let mut s = format!("[probe {head}] total {total:.1}cpu"); for (l, ms) in a.iter() { s.push_str(&format!(" {l} {ms:.1}")); } eprintln!("{s}"); });
}
