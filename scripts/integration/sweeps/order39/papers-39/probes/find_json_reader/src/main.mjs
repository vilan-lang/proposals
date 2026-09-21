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
function __list_pop(list) {
	return list.length === 0 ? [ 1 ] : [ 0, list.pop() ];
}
function __try_parse_json(text) {
	try {
		return [ 0, JSON.parse(text) ];
	} catch (error) {
		return [ 1 ];
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
	const $a = __list_pop(self[2]);
	let $b = null;
	if ($a[0] === 0) {
		const saved = $a[1];
		$b = saved;
	} else {
		$b = false;
	}
	self[1] = $b;
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
	let $c = null;
	if (arity === 0) {
		value(self, JSON.stringify(name));
	} else {
		open(self, "{");
		self[0] = self[0] + JSON.stringify(name) + ":";
		self[1] = false;
		if (arity > 1) {
			self[0] = self[0] + "[";
		}
		$c = undefined;
	}
	return $c;
}
function end_variant(self) {
	const $d = __list_pop(self[3]);
	let $e = null;
	if ($d[0] === 0) {
		const opened = $d[1];
		$e = opened;
	} else {
		$e = 0;
	}
	const arity = $e;
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
	const $l = self[1];
	let $m = null;
	if ($l[0] === 0) {
		const _reason = $l[1];
		$m = false;
	} else {
		$m = true;
	}
	return $m;
}
function report(self, reason) {
	const $j = self[1];
	let $k = null;
	if ($j[0] === 0) {
		const _first = $j[1];
		$k = undefined;
	} else {
		self[1] = [ 0, reason ];
		$k = undefined;
	}
	return $k;
}
function top(self) {
	let $o = null;
	if (!(ok(self)) || $n(self[0])) {
		$o = JSON.parse("null");
	} else {
		$o = __clone(__at(self[0], self[0].length - 1));
	}
	return $o;
}
function take(self) {
	if (!(ok(self))) {
		return JSON.parse("null");
	}
	const $q = __list_pop(self[0]);
	let $r = null;
	if ($q[0] === 0) {
		const value2 = $q[1];
		$r = value2;
	} else {
		report(self, "unexpected end of document");
		$r = JSON.parse("null");
	}
	return $r;
}
function begin_struct2(self) {

}
function field2(self, name) {
	const subject = top(self);
	let $p = null;
	if (ok(self)) {
		if (Object.hasOwn(subject, name)) {
			self[0].push(subject[name]);
		} else {
			report(self, "missing field \'" + name + "\'");
		}
		$p = undefined;
	}
	return $p;
}
function end_struct2(self) {
	take(self);
}
function begin_list2(self) {
	const subject = take(self);
	let $s = null;
	if (ok(self)) {
		const elements = subject;
		let index = elements.length - 1;
		while (index >= 0) {
			self[0].push(__clone(__at(elements, index)));
			index = index - 1;
		}
		$s = elements.length;
	} else {
		$s = 0;
	}
	return $s;
}
function end_list2(self) {

}
function variant_tag(self) {
	let $t = null;
	if (ok(self)) {
		$t = __json_tag(top(self));
	} else {
		$t = "";
	}
	return $t;
}
function begin_variant2(self, name, arity) {
	const subject = take(self);
	let $w = null;
	if (ok(self) && arity > 0) {
		let $v = null;
		if (Object.hasOwn(subject, name)) {
			const payload = subject[name];
			let $u = null;
			if (arity === 1) {
				self[0].push(payload);
			} else {
				const elements = payload;
				let index = elements.length - 1;
				while (index >= 0) {
					self[0].push(__clone(__at(elements, index)));
					index = index - 1;
				}
				$u = undefined;
			}
			$v = $u;
		} else {
			report(self, "missing payload for variant \'" + name + "\'");
		}
		$w = $v;
	}
	return $w;
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
	let $x = null;
	if (ok(self)) {
		$x = String(value2);
	} else {
		$x = "";
	}
	return $x;
}
function i32_value2(self) {
	const value2 = take(self);
	let $y = null;
	if (ok(self)) {
		$y = Number(value2);
	} else {
		$y = 0;
	}
	return $y;
}
function u32_value2(self) {
	const value2 = take(self);
	let $z = null;
	if (ok(self)) {
		$z = Number(value2);
	} else {
		$z = 0;
	}
	return $z;
}
function i53_value2(self) {
	const value2 = take(self);
	let $A = null;
	if (ok(self)) {
		$A = Number(value2);
	} else {
		$A = 0;
	}
	return $A;
}
function f64_value2(self) {
	const value2 = take(self);
	let $B = null;
	if (ok(self)) {
		$B = Number(value2);
	} else {
		$B = 0.0;
	}
	return $B;
}
function bool_value2(self) {
	const value2 = take(self);
	let $C = null;
	if (ok(self)) {
		$C = Boolean(value2);
	} else {
		$C = false;
	}
	return $C;
}
function fail(self, reason) {
	report(self, reason);
}
function failed(self) {
	return self[1];
}
function opened_reader(text) {
	const $h = __try_parse_json(text);
	let $i = null;
	if ($h[0] === 0) {
		const root = $h[1];
		$i = new3(root);
	} else {
		let reader = new3(JSON.parse("null"));
		report(reader, "malformed JSON");
		$i = reader;
	}
	return $i;
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
		const $f = frame;
		let $g = null;
		if ($f[0] === 0) {
			const text = $f[1];
			$g = opened_reader(text);
		} else {
			const bytes = $f[1];
			$g = opened_reader(decode_utf8(bytes));
		}
		let reader = $g;
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
function i32_value3(self) {
	return self[11]();
}
function read_two(text) {
	const codec = json_codec();
	let deserializer = codec[1]([ 0, text ]);
	deserializer[0]();
	deserializer[1]("args");
	const arity = deserializer[3]();
	const left = $D(deserializer);
	const right = $D(deserializer);
	const $E = deserializer[17]();
	let $F = null;
	if ($E[0] === 0) {
		const reason = $E[1];
		$F = reason;
	} else {
		$F = "(not poisoned)";
	}
	const failure = $F;
	return "arity=" + arity + " left=" + left + " right=" + right + " failed=" + failure;
}
function $n(self) {
	return self.length === 0;
}
function $D(deserializer) {
	return i32_value3(deserializer);
}
const quote = "\"";
console.log("[1,2]     " + read_two("{" + quote + "args" + quote + ":[1,2]}"));
console.log("[1]       " + read_two("{" + quote + "args" + quote + ":[1]}"));
console.log("[]        " + read_two("{" + quote + "args" + quote + ":[]}"));
console.log("[\"x\",2]   " + read_two("{" + quote + "args" + quote + ":[" + quote + "x" + quote + ",2]}"));
console.log("[null,2]  " + read_two("{" + quote + "args" + quote + ":[null,2]}"));
console.log("[true,2]  " + read_two("{" + quote + "args" + quote + ":[true,2]}"));
console.log("[1.5,2]   " + read_two("{" + quote + "args" + quote + ":[1.5,2]}"));
