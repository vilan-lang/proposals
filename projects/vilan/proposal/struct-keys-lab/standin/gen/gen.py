# Generates optic/src/bench.vl: covering writes, old scheme (lib.vl: copy every
# watched place before, compare after) vs key diff (keyed.vl).
out=[]
w=out.append
w('''import pkg::lib::{ Optic, optic };
import pkg::keyed::{ KOptic, koptic };
import pkg::key::{ Key, Keys, FieldEntry, KeyStep, Differs, field_key, index };
import std::reactive::{ Source, Signal };
import std::time::now_millis;
''')
for k in range(6):
    last = k==5
    tail = "leaf2: str," if last else f"child: D{k+1},"
    w(f'[derive(PartialEq, Keys)]\nstruct D{k} {{\n\tname: str,\n\tf1: str,\n\tf2: str,\n\tf3: str,\n\t{tail}\n\titems: List<str>,\n}}\n')
    ctor = f'D{k} {{ name = tag, f1 = "a", f2 = "b", f3 = "c", ' + ('leaf2 = "z", ' if last else f'child = mk{k+1}(tag, n), ') + 'items = items(n) }'
    w(f'fun mk{k}(tag: str, n: usize): D{k} {{\n\t{ctor}\n}}\n')
w('''fun items(n: usize): List<str> {
	mut out: List<str> = [];
	mut i: usize = 0;
	for i < n {
		out.push(i"item {i}");
		i += 1;
	}
	out
}
''')
for k in range(3):
    w(f'fun name{k}(o: Optic<D0, D{k}>): Optic<D0, str> {{\n\to.field("name", |u, read| read(&u.name), |u, change| change(&mut u.name))\n}}\n')
    w(f'fun child{k}(o: Optic<D0, D{k}>): Optic<D0, D{k+1}> {{\n\to.field("child", |u, read| read(&u.child), |u, change| change(&mut u.child))\n}}\n')
w('''fun items0(o: Optic<D0, D0>): Optic<D0, List<str>> {
	o.field("items", |u, read| read(&u.items), |u, change| change(&mut u.items))
}

fun tagged(n: usize, tag: str): List<str> {
	mut out: List<str> = [];
	mut i: usize = 0;
	for i < n {
		out.push(i"{tag} {i}");
		i += 1;
	}
	out
}

fun every_item(i: usize, k: usize): D0 {
	mut d = mk0(v(1), k);
	d.items = tagged(k, v(i));
	d
}

fun median(own xs: List<f64>): f64 {
	mut i: usize = 1;
	for i < xs.len() {
		mut j = i;
		for j > 0 && xs[j - 1] > xs[j] {
			let t = xs[j];
			xs[j] = xs[j - 1];
			xs[j - 1] = t;
			j -= 1;
		}
		i += 1;
	}
	xs[xs.len() / 2]
}

/// median of 5 runs, ns/op
fun bench(label: str, n: usize, body: |usize| void) {
	mut w: usize = 0;
	for w < n / 4 + 1 {
		body(w);
		w += 1;
	}
	mut runs: List<f64> = [];
	mut r = 0;
	for r < 5 {
		let start = now_millis();
		mut i: usize = 0;
		for i < n {
			body(i);
			i += 1;
		}
		let ms = now_millis() - start;
		runs.push(ms * 1000000.0 / n.as_f64());
		r += 1;
	}
	let m = median(runs);
	print(i"{label} | {m} ns/op");
}

let vals: List<str> = ["alpha", "beta"];
fun v(i: usize): str {
	vals[i % 2]
}

fun main() {
	let N: usize = 200000;
	let rn: usize = 20000;
	for k in [0 as usize, 10, 100] {
		let root = optic(mk0("x", k));
		let it = items0(root);
		let leaf = name2(child1(child0(root)));
		let _o = leaf.on_change(|_s| {});
		mut subs = [];
		mut j: usize = 0;
		for j < k {
			subs.push(it.at(j).on_change(|_s| {}));
			j += 1;
		}
		let kroot = koptic(mk0("x", k));
		let kit = kroot.at(D0::items());
		let kleaf = kroot.at(D0::child().then(D1::child()).then(D2::name()));
		let _ko = kleaf.on_change(|_s| {});
		mut ksubs = [];
		mut jj: usize = 0;
		for jj < k {
			ksubs.push(kit.at_maybe(index<str>(jj)).on_change(|_s| {}));
			jj += 1;
		}
		bench(i"L old leaf set depth3, {k} watched", N, |i| { leaf.set(v(i)); });
		bench(i"L key leaf set depth3, {k} watched", N, |i| { kleaf.set(v(i)); });
		bench(i"B0 construct mk0 only, {k} items", rn, |i| { mk0(v(i), k); });
		bench(i"B2 old ROOT set (leaf differs), {k} watched", rn, |i| { root.set(mk0(v(i), k)); });
		bench(i"B2 key ROOT set (leaf differs), {k} watched", rn, |i| { kroot.set(mk0(v(i), k)); });
		bench(i"B3 old ROOT set (nothing differs), {k} watched", rn, |i| { root.set(mk0(v(1), k)); });
		bench(i"B3 key ROOT set (nothing differs), {k} watched", rn, |i| { kroot.set(mk0(v(1), k)); });
		bench(i"B4 old ROOT set (every item differs), {k} watched", rn, |i| { root.set(every_item(i, k)); });
		bench(i"B4 key ROOT set (every item differs), {k} watched", rn, |i| { kroot.set(every_item(i, k)); });
		bench(i"U old ROOT update (name), {k} watched", rn, |i| { root.update(|u| u.name = v(i)); });
		bench(i"U key ROOT update (name), {k} watched", rn, |i| { kroot.update(|u| u.name = v(i)); });
		assert_same(root.get().child.child.name, kroot.get().child.child.name);
	}
}

fun assert_same(a: str, b: str) {
	if a != b {
		print(i"MISMATCH {a} vs {b}");
	}
}
''')
open(__import__('sys').argv[1],'w').write(''.join(x if x.endswith('\n') else x+'\n' for x in out))
