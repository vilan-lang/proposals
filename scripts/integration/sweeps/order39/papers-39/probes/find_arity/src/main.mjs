function __at(list, index) {
	if (index >= 0 && index < list.length) return list[index];
	throw "index out of bounds: the length is " + list.length + " but the index is " + index;
}
function __clone(value) {
	if (Array.isArray(value)) return value.map(__clone);
	if (value instanceof Set) return new Set([ ...value ].map(__clone));
	if (value instanceof Map) return new Map([ ...value ].map(([ k, v ]) => [ __clone(k), __clone(v) ]));
	return value;
}
function __json_tag(value) {
	return typeof value === "string" ? value : Object.keys(value)[0];
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
function __try_parse_json(text) {
	try {
		return [ 0, JSON.parse(text) ];
	} catch (error) {
		return [ 1 ];
	}
}
function __with_finally(body, after) {
	try {
		body();
	} finally {
		after();
	}
}
function new2() {
	return [ "", false, [  ], [  ] ];
}
function value(self, text) {
	if (self[1]) {
		self[0] = self[0] + ",";
	}
	self[0] = self[0] + text;
	self[1] = true;
}
function open(self, opener) {
	value(self, opener);
	self[2].push(true);
	self[1] = false;
}
function close(self, closer) {
	self[0] = self[0] + closer;
	const $t = __list_pop(self[2]);
	let $u = null;
	if ($t[0] === 0) {
		const saved = $t[1];
		$u = saved;
	} else {
		$u = false;
	}
	self[1] = $u;
}
function result(self) {
	return self[0];
}
function begin_struct(self, fields) {
	open(self, "{");
}
function field(self, name) {
	if (self[1]) {
		self[0] = self[0] + ",";
	}
	self[0] = self[0] + JSON.stringify(name) + ":";
	self[1] = false;
}
function end_struct(self) {
	close(self, "}");
}
function begin_list(self, length) {
	open(self, "[");
}
function end_list(self) {
	close(self, "]");
}
function begin_variant(self, name, arity) {
	self[3].push(arity);
	let $v = null;
	if (arity === 0) {
		value(self, JSON.stringify(name));
	} else {
		open(self, "{");
		self[0] = self[0] + JSON.stringify(name) + ":";
		self[1] = false;
		if (arity > 1) {
			self[0] = self[0] + "[";
		}
		$v = undefined;
	}
	return $v;
}
function end_variant(self) {
	const $w = __list_pop(self[3]);
	let $x = null;
	if ($w[0] === 0) {
		const opened = $w[1];
		$x = opened;
	} else {
		$x = 0;
	}
	const arity = $x;
	if (arity > 1) {
		self[0] = self[0] + "]";
	}
	if (arity > 0) {
		close(self, "}");
	}
}
function null_value(self) {
	value(self, "null");
}
function some_value(self) {

}
function str_value(self, value2) {
	value(self, JSON.stringify(value2));
}
function i32_value(self, value2) {
	value(self, "" + value2);
}
function u32_value(self, value2) {
	value(self, "" + value2);
}
function i53_value(self, value2) {
	value(self, "" + value2);
}
function f64_value(self, value2) {
	value(self, "" + value2);
}
function bool_value(self, value2) {
	value(self, "" + value2);
}
function new3(root) {
	let stack = [  ];
	stack.push(__clone(root));
	return [ stack, [ 1 ] ];
}
function ok(self) {
	const $E = self[1];
	let $F = null;
	if ($E[0] === 0) {
		const _reason = $E[1];
		$F = false;
	} else {
		$F = true;
	}
	return $F;
}
function report(self, reason) {
	const $C = self[1];
	let $D = null;
	if ($C[0] === 0) {
		const _first = $C[1];
		$D = undefined;
	} else {
		self[1] = [ 0, reason ];
		$D = undefined;
	}
	return $D;
}
function top(self) {
	let $H = null;
	if (!(ok(self)) || $i(self[0])) {
		$H = JSON.parse("null");
	} else {
		$H = __clone(__at(self[0], self[0].length - 1));
	}
	return $H;
}
function take(self) {
	if (!(ok(self))) {
		return JSON.parse("null");
	}
	const $J = __list_pop(self[0]);
	let $K = null;
	if ($J[0] === 0) {
		const value2 = $J[1];
		$K = value2;
	} else {
		report(self, "unexpected end of document");
		$K = JSON.parse("null");
	}
	return $K;
}
function begin_struct2(self) {

}
function field2(self, name) {
	const subject = top(self);
	let $I = null;
	if (ok(self)) {
		if (Object.hasOwn(subject, name)) {
			self[0].push(subject[name]);
		} else {
			report(self, "missing field \'" + name + "\'");
		}
		$I = undefined;
	}
	return $I;
}
function end_struct2(self) {
	take(self);
}
function begin_list2(self) {
	const subject = take(self);
	let $L = null;
	if (ok(self)) {
		const elements = subject;
		let index = elements.length - 1;
		while (index >= 0) {
			self[0].push(__clone(__at(elements, index)));
			index = index - 1;
		}
		$L = elements.length;
	} else {
		$L = 0;
	}
	return $L;
}
function end_list2(self) {

}
function variant_tag(self) {
	let $M = null;
	if (ok(self)) {
		$M = __json_tag(top(self));
	} else {
		$M = "";
	}
	return $M;
}
function begin_variant2(self, name, arity) {
	const subject = take(self);
	let $P = null;
	if (ok(self) && arity > 0) {
		let $O = null;
		if (Object.hasOwn(subject, name)) {
			const payload = subject[name];
			let $N = null;
			if (arity === 1) {
				self[0].push(payload);
			} else {
				const elements = payload;
				let index = elements.length - 1;
				while (index >= 0) {
					self[0].push(__clone(__at(elements, index)));
					index = index - 1;
				}
				$N = undefined;
			}
			$O = $N;
		} else {
			report(self, "missing payload for variant \'" + name + "\'");
		}
		$P = $O;
	}
	return $P;
}
function end_variant2(self) {

}
function is_null(self) {
	return ok(self) && top(self) === null;
}
function null_value2(self) {
	take(self);
}
function str_value2(self) {
	const value2 = take(self);
	let $Q = null;
	if (ok(self)) {
		$Q = String(value2);
	} else {
		$Q = "";
	}
	return $Q;
}
function i32_value2(self) {
	const value2 = take(self);
	let $R = null;
	if (ok(self)) {
		$R = Number(value2);
	} else {
		$R = 0;
	}
	return $R;
}
function u32_value2(self) {
	const value2 = take(self);
	let $S = null;
	if (ok(self)) {
		$S = Number(value2);
	} else {
		$S = 0;
	}
	return $S;
}
function i53_value2(self) {
	const value2 = take(self);
	let $T = null;
	if (ok(self)) {
		$T = Number(value2);
	} else {
		$T = 0;
	}
	return $T;
}
function f64_value2(self) {
	const value2 = take(self);
	let $U = null;
	if (ok(self)) {
		$U = Number(value2);
	} else {
		$U = 0.0;
	}
	return $U;
}
function bool_value2(self) {
	const value2 = take(self);
	let $V = null;
	if (ok(self)) {
		$V = Boolean(value2);
	} else {
		$V = false;
	}
	return $V;
}
function fail(self, reason) {
	report(self, reason);
}
function failed(self) {
	return self[1];
}
function opened_reader(text) {
	const $A = __try_parse_json(text);
	let $B = null;
	if ($A[0] === 0) {
		const root = $A[1];
		$B = new3(root);
	} else {
		let reader = new3(JSON.parse("null"));
		report(reader, "malformed JSON");
		$B = reader;
	}
	return $B;
}
function json_codec() {
	return [ () => {
		let writer = new2();
		const record = [ (fields) => {
			return begin_struct(writer, fields);
		}, (name) => {
			return field(writer, name);
		}, () => {
			return end_struct(writer);
		}, (length) => {
			return begin_list(writer, length);
		}, () => {
			return end_list(writer);
		}, (name, arity) => {
			return begin_variant(writer, name, arity);
		}, () => {
			return end_variant(writer);
		}, () => {
			return null_value(writer);
		}, () => {
			return some_value(writer);
		}, (value2) => {
			return str_value(writer, value2);
		}, (value2) => {
			return i32_value(writer, value2);
		}, (value2) => {
			return u32_value(writer, value2);
		}, (value2) => {
			return i53_value(writer, value2);
		}, (value2) => {
			return f64_value(writer, value2);
		}, (value2) => {
			return bool_value(writer, value2);
		} ];
		return [ record, () => {
			return [ 0, result(writer) ];
		} ];
	}, (frame) => {
		const $y = frame;
		let $z = null;
		if ($y[0] === 0) {
			const text = $y[1];
			$z = opened_reader(text);
		} else {
			const bytes = $y[1];
			$z = opened_reader(decode_utf8(bytes));
		}
		let reader = $z;
		return [ () => {
			return begin_struct2(reader);
		}, (name) => {
			return field2(reader, name);
		}, () => {
			return end_struct2(reader);
		}, () => {
			return begin_list2(reader);
		}, () => {
			return end_list2(reader);
		}, () => {
			return variant_tag(reader);
		}, (name, arity) => {
			return begin_variant2(reader, name, arity);
		}, () => {
			return end_variant2(reader);
		}, () => {
			return is_null(reader);
		}, () => {
			return null_value2(reader);
		}, () => {
			return str_value2(reader);
		}, () => {
			return i32_value2(reader);
		}, () => {
			return u32_value2(reader);
		}, () => {
			return i53_value2(reader);
		}, () => {
			return f64_value2(reader);
		}, () => {
			return bool_value2(reader);
		}, (reason) => {
			return fail(reader, reason);
		}, () => {
			return failed(reader);
		} ];
	} ];
}
function decode_utf8(bytes) {
	return new TextDecoder().decode(bytes);
}
function on_connection(self, connection) {
	self[3] = connection;
	return self;
}
function open_request(codec, frame) {
	const deserializer = codec[1](frame);
	deserializer[0]();
	deserializer[1]("method");
	const method = deserializer[10]();
	deserializer[1]("args");
	const arity = deserializer[3]();
	return [ method, deserializer, arity, 0 - 1 ];
}
function encode_reply(codec, outcome) {
	const $ac = codec[0]();
	const record = $ac[0];
	const finish = $ac[1];
	let serializer = record;
	const $ad = outcome;
	let $ae = null;
	if ($ad[0] === 0) {
		const describe = $ad[1];
		serializer[5]("Success", 1);
		describe(serializer);
		serializer[6]();
		$ae = undefined;
	} else {
		const error = $ad[1];
		serializer[5]("Failure", 1);
		$af(error, serializer);
		serializer[6]();
		$ae = undefined;
	}
	$ae;
	return finish();
}
async function respond(self, frame) {
	const request = on_connection(open_request(self[0], frame), self[2]);
	const $aa = request[1][17]();
	let $ab = null;
	if ($aa[0] === 0) {
		const reason = $aa[1];
		$ab = [ 1, [ 1, reason ] ];
	} else {
		$ab = await (self[1](request));
	}
	const outcome = $ab;
	return encode_reply(self[0], outcome);
}
function decode_failed(request) {
	return request[1][17]();
}
function new4() {
	return [ __shared_new([  ]), __shared_new([  ]) ];
}
function on(self, method, handler) {
	self[0].v.push([ method, handler ]);
	return __clone(self);
}
async function handle(self, request) {
	const $Y = $X($W(self[0].v, (route2) => {
		return route2[0] === request[0];
	}));
	let $Z = null;
	if ($Y[0] === 0) {
		const route = $Y[1];
		$Z = await (route[1](request));
	} else {
		$Z = [ 1, [ 2, "unknown method: " + request[0] ] ];
	}
	return $Z;
}
function into_protocol(self, codec) {
	return [ __clone(codec), async (request) => {
		return await (handle(self, request));
	}, 0 - 1, __clone(self[1].v) ];
}
function session_of(connection) {
	for (const entry of reactive_sessions.v) {
		const $o = entry;
		const id = $o[0];
		const session = $o[1];
		if (id === connection) {
			return [ 0, __clone(session) ];
		}
	}
	return [ 1 ];
}
function new5() {
	return [ __shared_new([  ]), __shared_new(new Map()), __shared_new(false), __shared_new(false), __shared_new(false) ];
}
function drain(turn) {
	if (!(turn[2].v)) {
		turn[2].v = true;
		draining_turns.v.push(__clone(turn));
		__with_finally(() => {
			let budget = 100000;
			while (!($i(turn[0].v)) && budget > 0) {
				const wave = turn[0].v;
				turn[0].v = [  ];
				turn[1].v = new Map();
				for (const subscriber of wave) {
					if (subscriber[2].v) {
						subscriber[1]();
					}
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
function begin_list3(self, length) {
	self[3](length);
}
function end_list3(self) {
	self[4]();
}
function begin_variant3(self, name, arity) {
	self[5](name, arity);
}
function end_variant3(self) {
	self[6]();
}
function str_value3(self, value2) {
	self[9](value2);
}
function i32_value3(self, value2) {
	self[10](value2);
}
function i32_value4(self) {
	return self[11]();
}
function add(self, left, right) {
	return left + right;
}
function dispatcher(self) {
	self = __clone(self);
	return on(on(on(new4(), "add", (__request) => {
		return $h([ 0 ], ($a) => {
			const left = $b(__request, 0);
			const right = $b(__request, 1);
			const $d = decode_failed(__request);
			let $e = null;
			if ($d[0] === 0) {
				const reason = $d[1];
				$e = [ 1, [ 1, reason ] ];
			} else {
				$e = $f(add(self, left, right));
			}
			return $e;
		});
	}), "__contract", (_) => {
		return $j(contract_hash(self));
	}), "__attach", (__request) => {
		return $h([ 0 ], ($l) => {
			const connection = $b(__request, 0);
			const $m = decode_failed(__request);
			let $n = null;
			if ($m[0] === 0) {
				const reason = $m[1];
				$n = [ 1, [ 1, reason ] ];
			} else {
				const $p = session_of(connection);
				let $q = null;
				if ($p[0] === 0) {
					const session = $p[1];
					const channels = [  ];
					$q = $r(channels);
				} else {
					$q = [ 1, [ 2, "unknown connection" ] ];
				}
				$n = $q;
			}
			return $n;
		});
	});
}
function contract_hash(self) {
	return "7cfbb529";
}
function $c(deserializer) {
	return i32_value4(deserializer);
}
function $b(request, index) {
	let deserializer = __clone(request[1]);
	return $c(deserializer);
}
function $g(self, serializer) {
	i32_value3(serializer, self);
}
function $f(value2) {
	return [ 0, (serializer) => {
		serializer = __clone(serializer);
		return $g(value2, serializer);
	} ];
}
function $i(self) {
	return self.length === 0;
}
function $h(policy, body) {
	const fresh = new5();
	const result2 = body(fresh);
	drain(fresh);
	fresh[3].v = true;
	return result2;
}
function $k(self, serializer) {
	str_value3(serializer, self);
}
function $j(value2) {
	return [ 0, (serializer) => {
		serializer = __clone(serializer);
		return $k(value2, serializer);
	} ];
}
function $s(self, serializer) {
	begin_list3(serializer, self.length);
	for (const element of self) {
		$g(element, serializer);
	}
	end_list3(serializer);
}
function $r(value2) {
	return [ 0, (serializer) => {
		serializer = __clone(serializer);
		return $s(value2, serializer);
	} ];
}
function $W(self, predicate) {
	let result2 = [  ];
	for (const item of self) {
		if (predicate(item)) {
			result2.push(__clone(item));
		}
	}
	return result2;
}
function $X(self) {
	return __list_get(self, 0);
}
function $af(self, serializer) {
	const $ag = self;
	let $ah = null;
	if ($ag[0] === 0) {
		const p0 = $ag[1];
		begin_variant3(serializer, "Transport", 1);
		$k(p0, serializer);
		end_variant3(serializer);
		$ah = undefined;
	} else if ($ag[0] === 1) {
		const p02 = $ag[1];
		begin_variant3(serializer, "Decode", 1);
		$k(p02, serializer);
		end_variant3(serializer);
		$ah = undefined;
	} else if ($ag[0] === 2) {
		const p03 = $ag[1];
		begin_variant3(serializer, "Remote", 1);
		$k(p03, serializer);
		end_variant3(serializer);
		$ah = undefined;
	} else if ($ag[0] === 3) {
		const p04 = $ag[1];
		begin_variant3(serializer, "Contract", 1);
		$k(p04, serializer);
		end_variant3(serializer);
		$ah = undefined;
	} else if ($ag[0] === 4) {
		begin_variant3(serializer, "Unauthorized", 0);
		end_variant3(serializer);
		$ah = undefined;
	} else {
		begin_variant3(serializer, "Unavailable", 0);
		end_variant3(serializer);
		$ah = undefined;
	}
	return $ah;
}
const reactive_sessions = __shared_new([  ]);
const draining_turns = __shared_new([  ]);
(async () => {
	const echo = [ 0 ];
	const protocol = into_protocol(dispatcher(echo), json_codec());
	const quote = "\"";
	const two = "{" + quote + "method" + quote + ":" + quote + "add" + quote + "," + quote + "args" + quote + ":[1,2]}";
	const one = "{" + quote + "method" + quote + ":" + quote + "add" + quote + "," + quote + "args" + quote + ":[1]}";
	const none = "{" + quote + "method" + quote + ":" + quote + "add" + quote + "," + quote + "args" + quote + ":[]}";
	const three = "{" + quote + "method" + quote + ":" + quote + "add" + quote + "," + quote + "args" + quote + ":[1,2,3]}";
	const wrong = "{" + quote + "method" + quote + ":" + quote + "add" + quote + "," + quote + "args" + quote + ":[" + quote + "x" + quote + ",2]}";
	for (const body of [ two, one, none, three, wrong ]) {
		const $ai = await (respond(protocol, [ 0, body ]));
		let $aj = null;
		if ($ai[0] === 0) {
			const reply = $ai[1];
			$aj = console.log("" + body + "  ->  " + reply);
		} else {
			const _bytes = $ai[1];
			$aj = console.log("binary");
		}
		$aj;
	}
})().catch(($ak) => {
	console.error(String($ak));
	process.exit(1);
});
