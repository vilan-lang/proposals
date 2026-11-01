# Lane b689 — B689 (store keyed step copies the whole value) + M182 (HashMap in-place update)

Worktree: /home/reed/code/vilan-lang/vilan/.claude/worktrees/b689 (branch `b689` off origin/next @7911d954).
Design: /home/reed/code/vilan-lang/proposals/projects/vilan/proposal/hash-map-lend.md — READ IT FIRST, build what it says; deviations go in the report with the reason.
Items: /home/reed/code/vilan-lang/proposals/.claude/worktrees/kolt-053/projects/vilan/tracker/items/B689.md and M182.md (the owner's text and repros).

Shell: every command starts with
`export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$HOME/.nvm/versions/node/v24.2.0/bin:$PATH"; export CARGO_BUILD_JOBS=6`
and runs from the worktree by absolute path (the shell's cwd resets between calls). Suite: `cargo nextest run --workspace -j 6 > suite.log 2>&1; echo $?` — never pipe a gate through grep/head/tail. Never `git stash`, never `git config`, never `--no-verify`, never touch /home/reed/code/kolt or the integration worktree. Commit on `b689` only; do not merge or push.

## Order of work

1. `vilan_rt::Map` (crates/vilan-rt/src/lib.rs:1442): tombstone onto the value (`Vec<(K, Option<V>)>`), `lend`, `lend_mut`; unit tests (design §4.7). `cargo test -p vilan-rt`.
2. The two intrinsics: analyzer enum (analyzer.rs:75641) + binding table (:90940); transformer helpers beside `__map_get` (:2662, :11080, the helper name list :15827); interpreter arms beside `__map_get` (:2547; `call_value` at :1518 calls a closure value); native rendering (vilan-rust/src/lib.rs:16196). Check captures.rs:391 and any other `match` over `Intrinsic` the compiler forces you to complete.
3. `NativeMap` externals (vilan/std/src/js/native_map.vl), then `HashMap` on two tables with `peek`/`modify`/`update` (vilan/std/src/hash_map.vl), then every std reader of `.table` on a HashMap: vilan/std/src/reactive/store.vl:151-255 (`value_at` and the Storable diff). `HashSet` is untouched.
4. The store's `at` twins (store.vl:758 and :787) per design §3.3.
5. Pins per design §4: inference pins in crates/vilan-core/tests/inference/std_surface.rs (NativeMap/HashMap live there) and the codegen-shape pin for the B689 repro; a native-differential program under crates/vilan-cli/tests/native/; docs per §5; CHANGELOG entries under `## Unreleased` with family markers (see the A178 entries for the form — ONE bold head per entry).
6. Corpus goldens (`cargo test -p vilan-cli --test corpus`): `HashMap::get`'s emitted JS changes, so goldens that use maps move. Rebuild the debug binary first, READ the diff of one moved golden to confirm it is the expected shape change and nothing else, then regenerate. Say in the report which goldens moved and why.
7. Measure: the B689 repro (below) with the lane's built `vilan` on node before (origin/next's binary: `cargo run -p vilan-cli --` from a clean checkout is not needed — the baseline is recorded here: 10.66 / 30.2 / 240 ms) and after; the M182 repro likewise (baseline from the item: 13.6 / 149 / 2784 ms). Report the numbers; they are not a gate.
8. Gates, in this order: `cargo fmt`; `cargo clippy --workspace --all-targets -- -D warnings`; `cargo test -p vilan-core --test inference`; `cargo test -p vilan-core --test docs`; `cargo test -p vilan-cli --test corpus`; `cargo test -p vilan-rt`; then the full nextest suite ONCE at the end, after every edit. perf/budgets.toml: only if the seal's instruments would move (std grows by a few hundred lines in `hash_map.vl`; follow what A178 did at perf/budgets.toml:282 if `vilan check` instructions on the browser/reactive samples move past the budget — measure with the perf scripts named in perf/README or budgets.toml comments).

## Repros

B689 (vilan.toml: `[package] name = "b689" version = "0.1.0" entry = "main.vl"`, source at src/main.vl):

```
import std::hash_map::HashMap;
import std::reactive::store::Store;

[extern("(() => performance.now())")]
external fun clock_ms(): f64;

[derive(PartialEq, Storable)]
struct Record {
	title: str,
	notes: List<str>,
}

[derive(Storable)]
struct State {
	records: HashMap<i32, Record>,
}

fun read_title(size: i32, reads: i32): f64 {
	mut notes: List<str> = [];
	mut index = 0;
	for index < size {
		notes.push("a note of some length, repeated");
		index += 1;
	}
	mut records: HashMap<i32, Record> = HashMap::new();
	records.insert(1, Record { title = "first", notes });
	let store = Store::new(State { records });
	let started = clock_ms();
	mut count = 0;
	mut read = 0;
	for read < reads {
		count += store.records().at(1).some().title().get().map_or(|title| title.len(), 0usize).as_i32();
		read += 1;
	}
	count > 0 then clock_ms() - started else 0f
}

fun main() {
	print(i"10 notes: {read_title(10, 2000)} ms");
	print(i"1000 notes: {read_title(1000, 2000)} ms");
	print(i"10000 notes: {read_title(10000, 2000)} ms");
}
```

M182: the `grow` program in the item (groups.get / push / insert, 1000 / 4000 / 16000), and its rewrite on `update`.

## Report (hand back)

Commit sha(s) on `b689`; files touched; every gate's exit code (the suite's from `echo $?`, with the count line from suite.log); the goldens moved and why; the repro timings before/after on node and the native probe's output; deviations from the design with reasons; anything out of scope you found, as a find (id-less: title, repro, where). Do not quote agent ids. Keep the report under 60 lines.
