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
	const $p = __list_pop(self[2]);
	let $q = null;
	if ($p[0] === 0) {
		const saved = $p[1];
		$q = saved;
	} else {
		$q = false;
	}
	self[1] = $q;
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
	let $r = null;
	if (arity === 0) {
		value(self, JSON.stringify(name));
	} else {
		open(self, "{");
		self[0] = self[0] + JSON.stringify(name) + ":";
		self[1] = false;
		if (arity > 1) {
			self[0] = self[0] + "[";
		}
		$r = undefined;
	}
	return $r;
}
function end_variant(self) {
	const $s = __list_pop(self[3]);
	let $t = null;
	if ($s[0] === 0) {
		const opened = $s[1];
		$t = opened;
	} else {
		$t = 0;
	}
	const arity = $t;
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
	const $A = self[1];
	let $B = null;
	if ($A[0] === 0) {
		const _reason = $A[1];
		$B = false;
	} else {
		$B = true;
	}
	return $B;
}
function report(self, reason) {
	const $y = self[1];
	let $z = null;
	if ($y[0] === 0) {
		const _first = $y[1];
		$z = undefined;
	} else {
		self[1] = [ 0, reason ];
		$z = undefined;
	}
	return $z;
}
function top(self) {
	let $D = null;
	if (!(ok(self)) || $o(self[0])) {
		$D = JSON.parse("null");
	} else {
		$D = __clone(__at(self[0], self[0].length - 1));
	}
	return $D;
}
function take(self) {
	if (!(ok(self))) {
		return JSON.parse("null");
	}
	const $F = __list_pop(self[0]);
	let $G = null;
	if ($F[0] === 0) {
		const value2 = $F[1];
		$G = value2;
	} else {
		report(self, "unexpected end of document");
		$G = JSON.parse("null");
	}
	return $G;
}
function begin_struct2(self) {

}
function field2(self, name) {
	const subject = top(self);
	let $E = null;
	if (ok(self)) {
		if (Object.hasOwn(subject, name)) {
			self[0].push(subject[name]);
		} else {
			report(self, "missing field \'" + name + "\'");
		}
		$E = undefined;
	}
	return $E;
}
function end_struct2(self) {
	take(self);
}
function begin_list2(self) {
	const subject = take(self);
	let $H = null;
	if (ok(self)) {
		const elements = subject;
		let index = elements.length - 1;
		while (index >= 0) {
			self[0].push(__clone(__at(elements, index)));
			index = index - 1;
		}
		$H = elements.length;
	} else {
		$H = 0;
	}
	return $H;
}
function end_list2(self) {

}
function variant_tag(self) {
	let $I = null;
	if (ok(self)) {
		$I = __json_tag(top(self));
	} else {
		$I = "";
	}
	return $I;
}
function begin_variant2(self, name, arity) {
	const subject = take(self);
	let $L = null;
	if (ok(self) && arity > 0) {
		let $K = null;
		if (Object.hasOwn(subject, name)) {
			const payload = subject[name];
			let $J = null;
			if (arity === 1) {
				self[0].push(payload);
			} else {
				const elements = payload;
				let index = elements.length - 1;
				while (index >= 0) {
					self[0].push(__clone(__at(elements, index)));
					index = index - 1;
				}
				$J = undefined;
			}
			$K = $J;
		} else {
			report(self, "missing payload for variant \'" + name + "\'");
		}
		$L = $K;
	}
	return $L;
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
	let $M = null;
	if (ok(self)) {
		$M = String(value2);
	} else {
		$M = "";
	}
	return $M;
}
function i32_value2(self) {
	const value2 = take(self);
	let $N = null;
	if (ok(self)) {
		$N = Number(value2);
	} else {
		$N = 0;
	}
	return $N;
}
function u32_value2(self) {
	const value2 = take(self);
	let $O = null;
	if (ok(self)) {
		$O = Number(value2);
	} else {
		$O = 0;
	}
	return $O;
}
function i53_value2(self) {
	const value2 = take(self);
	let $P = null;
	if (ok(self)) {
		$P = Number(value2);
	} else {
		$P = 0;
	}
	return $P;
}
function f64_value2(self) {
	const value2 = take(self);
	let $Q = null;
	if (ok(self)) {
		$Q = Number(value2);
	} else {
		$Q = 0.0;
	}
	return $Q;
}
function bool_value2(self) {
	const value2 = take(self);
	let $R = null;
	if (ok(self)) {
		$R = Boolean(value2);
	} else {
		$R = false;
	}
	return $R;
}
function fail(self, reason) {
	report(self, reason);
}
function failed(self) {
	return self[1];
}
function opened_reader(text) {
	const $w = __try_parse_json(text);
	let $x = null;
	if ($w[0] === 0) {
		const root = $w[1];
		$x = new3(root);
	} else {
		let reader = new3(JSON.parse("null"));
		report(reader, "malformed JSON");
		$x = reader;
	}
	return $x;
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
		const $u = frame;
		let $v = null;
		if ($u[0] === 0) {
			const text = $u[1];
			$v = opened_reader(text);
		} else {
			const bytes = $u[1];
			$v = opened_reader(decode_utf8(bytes));
		}
		let reader = $v;
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
	const $Y = codec[0]();
	const record = $Y[0];
	const finish = $Y[1];
	let serializer = record;
	const $Z = outcome;
	let $aa = null;
	if ($Z[0] === 0) {
		const describe = $Z[1];
		serializer[5]("Success", 1);
		describe(serializer);
		serializer[6]();
		$aa = undefined;
	} else {
		const error = $Z[1];
		serializer[5]("Failure", 1);
		$ab(error, serializer);
		serializer[6]();
		$aa = undefined;
	}
	$aa;
	return finish();
}
async function respond(self, frame) {
	const request = on_connection(open_request(self[0], frame), self[2]);
	const $W = request[1][17]();
	let $X = null;
	if ($W[0] === 0) {
		const reason = $W[1];
		$X = [ 1, [ 1, reason ] ];
	} else {
		$X = await (self[1](request));
	}
	const outcome = $X;
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
	const $U = $T($S(self[0].v, (route2) => {
		return route2[0] === request[0];
	}));
	let $V = null;
	if ($U[0] === 0) {
		const route = $U[1];
		$V = await (route[1](request));
	} else {
		$V = [ 1, [ 2, "unknown method: " + request[0] ] ];
	}
	return $V;
}
function into_protocol(self, codec) {
	return [ __clone(codec), async (request) => {
		return await (handle(self, request));
	}, 0 - 1, __clone(self[1].v) ];
}
function session_of(connection) {
	for (const entry of reactive_sessions.v) {
		const $h = entry;
		const id = $h[0];
		const session = $h[1];
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
			while (!($o(turn[0].v)) && budget > 0) {
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
function dispatcher(self) {
	self = __clone(self);
	return on(on(new4(), "__contract", (_) => {
		return $a(contract_hash(self));
	}), "__attach", (__request) => {
		return $n([ 0 ], ($c) => {
			const connection = $d(__request, 0);
			const $f = decode_failed(__request);
			let $g = null;
			if ($f[0] === 0) {
				const reason = $f[1];
				$g = [ 1, [ 1, reason ] ];
			} else {
				const $i = session_of(connection);
				let $j = null;
				if ($i[0] === 0) {
					const session = $i[1];
					const channels = [  ];
					$j = $k(channels);
				} else {
					$j = [ 1, [ 2, "unknown connection" ] ];
				}
				$g = $j;
			}
			return $g;
		});
	});
}
function contract_hash(self) {
	return "00001505";
}
function $b(self, serializer) {
	str_value3(serializer, self);
}
function $a(value2) {
	return [ 0, (serializer) => {
		serializer = __clone(serializer);
		return $b(value2, serializer);
	} ];
}
function $e(deserializer) {
	return i32_value4(deserializer);
}
function $d(request, index) {
	let deserializer = __clone(request[1]);
	return $e(deserializer);
}
function $m(self, serializer) {
	i32_value3(serializer, self);
}
function $l(self, serializer) {
	begin_list3(serializer, self.length);
	for (const element of self) {
		$m(element, serializer);
	}
	end_list3(serializer);
}
function $k(value2) {
	return [ 0, (serializer) => {
		serializer = __clone(serializer);
		return $l(value2, serializer);
	} ];
}
function $o(self) {
	return self.length === 0;
}
function $n(policy, body) {
	const fresh = new5();
	const result2 = body(fresh);
	drain(fresh);
	fresh[3].v = true;
	return result2;
}
function $S(self, predicate) {
	let result2 = [  ];
	for (const item of self) {
		if (predicate(item)) {
			result2.push(__clone(item));
		}
	}
	return result2;
}
function $T(self) {
	return __list_get(self, 0);
}
function $ab(self, serializer) {
	const $ac = self;
	let $ad = null;
	if ($ac[0] === 0) {
		const p0 = $ac[1];
		begin_variant3(serializer, "Transport", 1);
		$b(p0, serializer);
		end_variant3(serializer);
		$ad = undefined;
	} else if ($ac[0] === 1) {
		const p02 = $ac[1];
		begin_variant3(serializer, "Decode", 1);
		$b(p02, serializer);
		end_variant3(serializer);
		$ad = undefined;
	} else if ($ac[0] === 2) {
		const p03 = $ac[1];
		begin_variant3(serializer, "Remote", 1);
		$b(p03, serializer);
		end_variant3(serializer);
		$ad = undefined;
	} else if ($ac[0] === 3) {
		const p04 = $ac[1];
		begin_variant3(serializer, "Contract", 1);
		$b(p04, serializer);
		end_variant3(serializer);
		$ad = undefined;
	} else if ($ac[0] === 4) {
		begin_variant3(serializer, "Unauthorized", 0);
		end_variant3(serializer);
		$ad = undefined;
	} else {
		begin_variant3(serializer, "Unavailable", 0);
		end_variant3(serializer);
		$ad = undefined;
	}
	return $ad;
}
const reactive_sessions = __shared_new([  ]);
const draining_turns = __shared_new([  ]);
(async () => {
	const service = [ 0 ];
	const protocol = into_protocol(dispatcher(service), json_codec());
	const quote = "\"";
	const body = "{" + quote + "method" + quote + ":" + quote + "add" + quote + "," + quote + "args" + quote + ":[1,2]}";
	const $ae = await (respond(protocol, [ 0, body ]));
	let $af = null;
	if ($ae[0] === 0) {
		const reply = $ae[1];
		$af = console.log("reply=" + reply);
	} else {
		const _bytes = $ae[1];
		$af = console.log("binary");
	}
	$af;
	const hash = contract_hash(service);
	console.log("contract_hash=" + hash);
})().catch(($ag) => {
	console.error(String($ag));
	process.exit(1);
});
