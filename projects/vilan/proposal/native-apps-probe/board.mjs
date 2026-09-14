function __clone(value) {
	if (Array.isArray(value)) return value.map(__clone);
	if (value instanceof Set) return new Set([ ...value ].map(__clone));
	if (value instanceof Map) return new Map([ ...value ].map(([ k, v ]) => [ __clone(k), __clone(v) ]));
	return value;
}
function __guarded(body) {
	try {
		body();
		return [ 1 ];
	} catch (error) {
		return [ 0, error && error.message ? error.message : String(error) ];
	}
}
function __hash(value) {
	return (typeof value === "object" && value !== null) ? JSON.stringify(value) : value;
}
function __list_get(list, index) {
	return index >= 0 && index < list.length ? [ 0, __clone(list[index]) ] : [ 1 ];
}
function __list_pop(list) {
	return list.length === 0 ? [ 1 ] : [ 0, list.pop() ];
}
function __shared_new(value) {
	return { v: value };
}
function __with_finally(body, after) {
	try {
		body();
	} finally {
		after();
	}
}
function hash(self) {
	return __hash(self);
}
function fresh_id() {
	const id = next_subscriber_id.v;
	next_subscriber_id.v = id + 1;
	return id;
}
function enqueue(turn, subscribers) {
	for (const subscriber of subscribers) {
		const key = hash(subscriber[0]);
		if (!(turn[1].v.has(key))) {
			turn[1].v.set(key, true);
			turn[0].v.push(__clone(subscriber));
		}
	}
	if (turn[3].v && !(turn[4].v) && !(turn[2].v)) {
		turn[4].v = true;
		queueMicrotask(() => {
			turn[4].v = false;
			drain(turn);
			return;
		});
	}
}
function drain(turn) {
	if (!(turn[2].v)) {
		turn[2].v = true;
		draining_turns.v.push(__clone(turn));
		__with_finally(() => {
			let budget = 100000;
			while (!($r(turn[0].v)) && budget > 0) {
				const wave = turn[0].v;
				turn[0].v = [  ];
				turn[1].v = new Map();
				for (const subscriber of wave) {
					subscriber[1]();
					budget = budget - 1;
				}
			}
			return;
		}, () => {
			__list_pop(draining_turns.v);
			turn[2].v = false;
			return;
		});
	}
}
function dispose(self, $g) {
	let kept = [  ];
	for (const subscriber of self[0].v) {
		if (subscriber[0] !== self[1]) {
			kept.push(__clone(subscriber));
		}
	}
	self[0].v = kept;
	const ambient = $g;
	const $h = ambient;
	let $i = null;
	if ($h[0] === 0) {
		const turn = $h[1];
		let kept_pending = [  ];
		for (const subscriber2 of turn[0].v) {
			if (subscriber2[0] !== self[1]) {
				kept_pending.push(__clone(subscriber2));
			}
		}
		turn[0].v = kept_pending;
		turn[1].v.delete(hash(self[1]));
		$i = undefined;
	} else {
		$i = undefined;
	}
	$i;
	const $j = self[2].v;
	let $k = null;
	if ($j[0] === 0) {
		const release = $j[1];
		self[2].v = [ 1 ];
		releasing_turns.v.push(ambient);
		__with_finally(release, () => {
			__list_pop(releasing_turns.v);
			return;
		});
		$k = undefined;
	} else {
		$k = undefined;
	}
	return $k;
}
function new2() {
	return [ __shared_new([  ]), __shared_new(false) ];
}
function dispose2(self) {
	let $B = null;
	if (!(self[1].v)) {
		self[1].v = true;
		let failure = [ 1 ];
		for (const cleanup of self[0].v) {
			const $v = __guarded(cleanup);
			let $w = null;
			if ($v[0] === 0) {
				const message = $v[1];
				if ($x(failure)) {
					failure = [ 0, message ];
				}
				$w = undefined;
			} else {
				$w = undefined;
			}
			$w;
		}
		self[0].v = [  ];
		const $z = failure;
		let $A = null;
		if ($z[0] === 0) {
			const message2 = $z[1];
			$A = (() => {
				throw message2;
			})();
		} else {
			$A = undefined;
		}
		$B = $A;
	}
	return $B;
}
function new3(name) {
	return [ name, [  ] ];
}
function add(self, todo) {
	self[1].push(__clone(todo));
}
function open(self) {
	let n = 0;
	for (const todo of self[1]) {
		if (!(todo[2])) {
			n = n + 1;
		}
	}
	return n;
}
function $a(value) {
	let subscribers = [  ];
	return [ __shared_new(value), __shared_new(subscribers), fresh_id() ];
}
function $c(signal, observer) {
	const id = fresh_id();
	const cell = signal[0];
	signal[1].v.push([ id, () => {
		observer(cell.v);
		return;
	} ]);
	return [ signal[1], id, __shared_new([ 1 ]) ];
}
function $d(self) {
	return __clone(self[0].v);
}
function $b(self, observer) {
	const subscription = $c(self, observer);
	observer($d(self));
	return subscription;
}
function $e(self, item, $f) {
	if (self[1].v) {
		dispose(item, $f);
	} else {
		self[0].v.push(() => {
			dispose(item, $f);
			return;
		});
	}
	return __clone(item);
}
function $r(self) {
	return self.length === 0;
}
function $s(self) {
	return __list_get(self, self.length - 1);
}
function $n(self, $o) {
	const $p = $o;
	let $q = null;
	if ($p[0] === 0) {
		const turn = $p[1];
		$q = enqueue(turn, self[1].v);
	} else {
		const $t = $s(draining_turns.v);
		let $u = null;
		if ($t[0] === 0) {
			const draining = $t[1];
			$u = enqueue(draining, self[1].v);
		} else {
			for (const subscriber of self[1].v) {
				subscriber[1]();
			}
			$u = undefined;
		}
		$q = $u;
	}
	return $q;
}
function $l(self, value, $m) {
	self[0].v = __clone(value);
	$n(self, $m);
}
function $x(self) {
	const $y = self;
	return $y[0] === 1;
}
const next_subscriber_id = __shared_new(0);
const draining_turns = __shared_new([  ]);
const releasing_turns = __shared_new([  ]);
let board = new3("inbox");
add(board, [ 1, "write the paper", false ]);
add(board, [ 2, "read the census", true ]);
let snapshot = __clone(board[1]);
snapshot.push([ 3, "ghost", false ]);
console.log(board[1].length);
console.log(snapshot.length);
const count = $a(open(board));
let seen = [  ];
const owner = new2();
$e(owner, $b(count, (value) => {
	seen.push(value);
	return;
}), [ 1 ]);
add(board, [ 4, "ship it", false ]);
$l(count, open(board), [ 1 ]);
console.log(seen.length);
dispose2(owner);
$l(count, 99, [ 1 ]);
console.log(seen.length);
console.log($d(count));
