import { createHash } from "node:crypto";
import { readFile } from "node:fs/promises";
import { createServer } from "node:http";
import { buffer } from "node:stream/consumers";
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
function __env(key) {
	const value = process.env[key];
	return value === undefined ? [ 1 ] : [ 0, value ];
}
function __force(cell) {
	if (cell.state === 2) return cell.value;
	if (cell.state === 1) throw "lazy initialization cycle: `" + cell.name + "`";
	if (cell.state === 3) throw "lazy `" + cell.name + "` is poisoned: its initializer panicked: " + cell.value;
	cell.state = 1;
	try {
		cell.value = cell.thunk();
	} catch (failure) {
		cell.state = 3;
		cell.value = failure;
		throw failure;
	}
	cell.state = 2;
	cell.thunk = null;
	return cell.value;
}
function __json_kind(value) {
	if (value === null) return "null";
	if (Array.isArray(value)) return "array";
	return typeof value;
}
function __json_tag(value) {
	return typeof value === "string" ? value : Object.keys(value)[0];
}
function __lazy(name, thunk) {
	return { name: name, state: 0, value: undefined, thunk: thunk };
}
function __list_pop(list) {
	return list.length === 0 ? [ 1 ] : [ 0, list.pop() ];
}
function __list_sort_by(list, compare) {
	return list.slice().sort(compare);
}
function __parse_i32(text) {
	const trimmed = text.trim();
	const value = Number(trimmed);
	return /^[+-]?[0-9]+$/.test(trimmed) && value >= -2147483648 && value <= 2147483647 ? [ 0, value ] : [ 1 ];
}
async function __sha256(data) {
	return new Uint8Array(await crypto.subtle.digest("SHA-256", data));
}
function __shared_new(value) {
	return { v: value };
}
function __substring(text, start, end) {
	if (0 <= start && start <= end && end <= text.length) return text.substring(start, end);
	throw "substring out of range: the length is " + text.length + " but the range is " + start + ".." + end + " — substring requires 0 <= start <= end <= len and never clamps or swaps; to drop a known affix use strip_prefix/strip_suffix, and for the rest of the string pass s.len() as the end";
}
class __Task {
	constructor(run, origin, nursery) {
		this.origin = origin;
		this.observed = false;
		this.nursery = nursery;
		this.owned = !!nursery;
		this.rejected = false;
		this.error = undefined;
		this.promise = run();
		this.promise.then(null, (error) => {
			this.rejected = true;
			this.error = error;
			if (this.owned && !__nursery_is_cancel(error)) this.nursery.__fail(this);
			if (!this.observed && !this.owned) {
				globalThis.setTimeout(() => {
					if (!this.observed) console.error("unhandled task error (spawned in " + this.origin + "): " + String(error));
				}, 0);
			}
		});
		if (nursery) nursery.children.push(this);
	}
	then(onFulfilled, onRejected) {
		this.observed = true;
		return this.promise.then(onFulfilled, onRejected);
	}
}
function __task(run, origin, nursery) {
	return new __Task(run, origin, nursery);
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
function attach_ambient_signal(options, $R) {
	const $V = ambient_signal($R);
	let $W = null;
	if ($V[0] === 0) {
		const signal = $V[1];
		$W = options.signal = signal;
	} else {
		$W = undefined;
	}
	return $W;
}
async function bytes(self) {
	return new Uint8Array(await (self.arrayBuffer()));
}
function post(url, body3) {
	return [ url, "POST", body3, [  ] ];
}
async function post_bytes(url, body3, $X) {
	const options = Object();
	options.method = "POST";
	options.body = body3;
	attach_ambient_signal(options, $X);
	return await (fetch(url, options));
}
function header(self, name, value2) {
	self[3].push([ name, value2 ]);
	return self;
}
async function send(self, $Q) {
	const options = Object();
	options.method = self[1];
	options.headers = self[3];
	if (self[1] !== "GET") {
		options.body = self[2];
	}
	attach_ambient_signal(options, $Q);
	return await (fetch(self[0], options));
}
function to_hex(self) {
	const digits = "0123456789abcdef";
	let out = "";
	const $as = new4(0, self.length);
	while (true) {
		const $at = next($as);
		if ($at[0] !== 0) {
			break;
		}
		const index = $at[1];
		const byte = self.at(index);
		out = out + __substring(digits, Math.trunc(byte / 16), Math.trunc(byte / 16) + 1) + __substring(digits, byte % 16, byte % 16 + 1);
	}
	return out;
}
function set(self, index, value2) {
	self.fill(value2, index, index + 1);
}
function concat(a, b) {
	const joined = new Uint8Array(a.length + b.length);
	joined.set(a, 0);
	joined.set(b, a.length);
	return joined;
}
function encode_utf8(text2) {
	return new TextEncoder().encode(text2);
}
function decode_utf8(bytes3) {
	return new TextDecoder().decode(bytes3);
}
function remote_address(self) {
	const raw = self.remoteAddress;
	let $bB = null;
	if (__json_kind(raw) === "string") {
		$bB = String(raw);
	} else {
		$bB = "";
	}
	return $bB;
}
function path(self) {
	return self[0].url;
}
function method(self) {
	return self[0].method;
}
function body(self) {
	return new TextDecoder().decode(self[1]);
}
function bytes2(self) {
	return __clone(self[1]);
}
function header2(self, name) {
	const lowered = to_lowercase_ascii(name);
	const headers = self[0].headers;
	if (!(has_field(headers, lowered))) {
		return [ 1 ];
	}
	return [ 0, String(headers[lowered]) ];
}
function send2(self, chunk) {
	self[0].write(chunk);
}
function on_close(self, handler) {
	self[0].on("close", handler);
}
function builder() {
	return [ 200, [  ], [ 0, "" ] ];
}
function code(self, code2) {
	self[0] = code2;
	return self;
}
function set_header(self, name, value2) {
	self[1].push([ name, value2 ]);
	return self;
}
function body2(self, body3) {
	self[2] = [ 0, body3 ];
	return self;
}
function body_bytes(self, body3) {
	self[2] = [ 1, __clone(body3) ];
	return self;
}
function streaming(self, on_open) {
	self[2] = [ 2, on_open ];
	return self;
}
function build(self) {
	return [ self[0], __clone(self[1]), self[2] ];
}
async function etag_of(body3) {
	return "\"" + __substring(to_hex(await (__sha256(body3))), 0, 32) + "\"";
}
function if_none_match_matches(header3, etag) {
	if (header3.trim() === "*") {
		return true;
	}
	const target = strip_weak(etag.trim());
	for (const candidate of header3.split(",")) {
		if (strip_weak(candidate.trim()) === target) {
			return true;
		}
	}
	return false;
}
function strip_weak(tag) {
	if (tag.startsWith("W/")) {
		return __substring(tag, 2, tag.length);
	}
	return tag;
}
function etag_response(request, etag, body3, content_type) {
	const method2 = method(request);
	let $aw = null;
	if (method2 === "GET" || method2 === "HEAD") {
		const $au = header2(request, "If-None-Match");
		let $av = null;
		if ($au[0] === 0) {
			const header3 = $au[1];
			if (if_none_match_matches(header3, etag)) {
				return set_header(code(builder(), 304), "ETag", etag);
			}
			$av = undefined;
		} else {
			$av = undefined;
		}
		$aw = $av;
	}
	$aw;
	return body_bytes(set_header(set_header(builder(), "ETag", etag), "Content-Type", content_type), body3);
}
function builder2() {
	return [ 3000, (request) => {
		return build(body2(code(builder(), 404), "Not Found"));
	}, (server) => {
		return;
	}, (server) => {
		return;
	}, [ 1 ], [  ], [  ], [ 1 ] ];
}
function start(self) {
	const request_handler = self[1];
	const on_start2 = self[2];
	const server = __clone(self);
	const port2 = self[0];
	const upgrade_handler = self[4];
	const node_server = createServer(async (node_request, node_response) => {
		const content = await (buffer(node_request));
		const response = await (request_handler([ __clone(node_request), content ]));
		node_response.statusCode = response[0];
		if (response[1].length === 0) {
			node_response.setHeader("Content-Type", "text/plain");
		}
		for (const header3 of response[1]) {
			const $cB = header3;
			const name = $cB[0];
			const value2 = $cB[1];
			node_response.setHeader(name, value2);
		}
		const $cC = response[2];
		let $cD = null;
		if ($cC[0] === 0) {
			const text2 = $cC[1];
			$cD = node_response.end(text2);
		} else if ($cC[0] === 1) {
			const bytes3 = $cC[1];
			$cD = node_response.end(bytes3);
		} else {
			const on_open = $cC[1];
			$cD = on_open([ __clone(node_response) ]);
		}
		return $cD;
	});
	const $cE = upgrade_handler;
	let $cF = null;
	if ($cE[0] === 0) {
		const handler = $cE[1];
		$cF = node_server.on("upgrade", handler);
	} else {
		$cF = undefined;
	}
	$cF;
	node_server.listen(port2, () => {
		let started = __clone(server);
		started[0] = bound_port(node_server);
		started[5] = [ 0, __clone(node_server) ];
		on_start2(started);
		return;
	});
}
function bound_port(node_server) {
	return node_server.address().port;
}
function port(self, port2) {
	self[0] = port2;
	return self;
}
function on_request(self, handler) {
	self[1] = handler;
	return self;
}
function on_start(self, callback) {
	self[2] = callback;
	return self;
}
function build2(self, $aj) {
	const assets = __clone(self[6]);
	const cache = self[7];
	const fallback = self[1];
	return [ self[0], fold_service_requests(self[5], async (request) => {
		return await (respond_from_build(assets, cache, fallback, request));
	}, $aj), self[2], self[3], fold_service_upgrades(self[5], self[4], $aj), [ 1 ] ];
}
async function respond_from_build(assets, cache, fallback, request) {
	const $ak = asset_for(assets, path(request));
	let $al = null;
	if ($ak[0] === 0) {
		const asset = $ak[1];
		const $am = cache;
		let $an = null;
		if ($am[0] === 0) {
			const policy = $am[1];
			$an = await (cached_asset_response(asset, policy(asset[0]), request));
		} else {
			$an = await (asset_response(asset));
		}
		$al = $an;
	} else {
		$al = await (fallback(request));
	}
	return $al;
}
async function asset_response(asset) {
	return build(body_bytes(set_header(builder(), "Content-Type", asset[2]), await (asset_body(asset))));
}
async function cached_asset_response(asset, policy, request) {
	const body3 = await (asset_body(asset));
	let $ax = null;
	if (policy[0]) {
		$ax = etag_response(request, await (etag_of(body3)), body3, asset[2]);
	} else {
		$ax = body_bytes(set_header(builder(), "Content-Type", asset[2]), body3);
	}
	let response = $ax;
	if (policy[1] !== "") {
		response = set_header(__clone(response), "Cache-Control", policy[1]);
	}
	return build(response);
}
function asset_for(assets, path2) {
	const route = __at(path2.split("?"), 0);
	for (const asset of assets) {
		if (asset[0] === route) {
			return [ 0, asset ];
		}
	}
	return [ 1 ];
}
async function asset_body(asset) {
	let $aq = null;
	if (is_watching()) {
		$aq = await (readFile(asset[1]));
	} else {
		$aq = __clone(asset[3]);
	}
	return $aq;
}
function has_field(self, name) {
	return Object.hasOwn(self, name);
}
function from_json_value(value2) {
	let $bN = null;
	if (__json_kind(value2) === "string") {
		$bN = [ 0, String(value2) ];
	} else {
		$bN = [ 1, "expected a string" ];
	}
	return $bN;
}
function new2() {
	return [ "", false, [  ], [  ] ];
}
function value(self, text2) {
	if (self[1]) {
		self[0] = self[0] + ",";
	}
	self[0] = self[0] + text2;
	self[1] = true;
}
function open2(self, opener) {
	value(self, opener);
	self[2].push(true);
	self[1] = false;
}
function close(self, closer) {
	self[0] = self[0] + closer;
	const $e = __list_pop(self[2]);
	let $f = null;
	if ($e[0] === 0) {
		const saved = $e[1];
		$f = saved;
	} else {
		$f = false;
	}
	self[1] = $f;
}
function result(self) {
	return self[0];
}
function begin_struct(self, fields) {
	open2(self, "{");
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
	open2(self, "[");
}
function end_list(self) {
	close(self, "]");
}
function begin_variant(self, name, arity) {
	self[3].push(arity);
	let $g = null;
	if (arity === 0) {
		value(self, JSON.stringify(name));
	} else {
		open2(self, "{");
		self[0] = self[0] + JSON.stringify(name) + ":";
		self[1] = false;
		if (arity > 1) {
			self[0] = self[0] + "[";
		}
		$g = undefined;
	}
	return $g;
}
function end_variant(self) {
	const $h = __list_pop(self[3]);
	let $i = null;
	if ($h[0] === 0) {
		const opened = $h[1];
		$i = opened;
	} else {
		$i = 0;
	}
	const arity = $i;
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
	const $p = self[1];
	let $q = null;
	if ($p[0] === 0) {
		const _reason = $p[1];
		$q = false;
	} else {
		$q = true;
	}
	return $q;
}
function report(self, reason) {
	const $n = self[1];
	let $o = null;
	if ($n[0] === 0) {
		const _first = $n[1];
		$o = undefined;
	} else {
		self[1] = [ 0, reason ];
		$o = undefined;
	}
	return $o;
}
function top(self) {
	let $s = null;
	if (!(ok(self)) || $r(self[0])) {
		$s = JSON.parse("null");
	} else {
		$s = __clone(__at(self[0], self[0].length - 1));
	}
	return $s;
}
function take(self) {
	if (!(ok(self))) {
		return JSON.parse("null");
	}
	const $u = __list_pop(self[0]);
	let $v = null;
	if ($u[0] === 0) {
		const value2 = $u[1];
		$v = value2;
	} else {
		report(self, "unexpected end of document");
		$v = JSON.parse("null");
	}
	return $v;
}
function begin_struct2(self) {

}
function field2(self, name) {
	const subject = top(self);
	let $t = null;
	if (ok(self)) {
		if (Object.hasOwn(subject, name)) {
			self[0].push(subject[name]);
		} else {
			report(self, "missing field \'" + name + "\'");
		}
		$t = undefined;
	}
	return $t;
}
function end_struct2(self) {
	take(self);
}
function begin_list2(self) {
	const subject = take(self);
	let $w = null;
	if (ok(self)) {
		const elements = subject;
		let index = elements.length - 1;
		while (index >= 0) {
			self[0].push(__clone(__at(elements, index)));
			index = index - 1;
		}
		$w = elements.length;
	} else {
		$w = 0;
	}
	return $w;
}
function end_list2(self) {

}
function variant_tag(self) {
	let $x = null;
	if (ok(self)) {
		$x = __json_tag(top(self));
	} else {
		$x = "";
	}
	return $x;
}
function begin_variant2(self, name, arity) {
	const subject = take(self);
	let $A = null;
	if (ok(self) && arity > 0) {
		let $z = null;
		if (Object.hasOwn(subject, name)) {
			const payload = subject[name];
			let $y = null;
			if (arity === 1) {
				self[0].push(payload);
			} else {
				const elements = payload;
				let index = elements.length - 1;
				while (index >= 0) {
					self[0].push(__clone(__at(elements, index)));
					index = index - 1;
				}
				$y = undefined;
			}
			$z = $y;
		} else {
			report(self, "missing payload for variant \'" + name + "\'");
		}
		$A = $z;
	}
	return $A;
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
	let $B = null;
	if (ok(self)) {
		$B = String(value2);
	} else {
		$B = "";
	}
	return $B;
}
function i32_value2(self) {
	const value2 = take(self);
	let $C = null;
	if (ok(self)) {
		$C = Number(value2);
	} else {
		$C = 0;
	}
	return $C;
}
function u32_value2(self) {
	const value2 = take(self);
	let $D = null;
	if (ok(self)) {
		$D = Number(value2);
	} else {
		$D = 0;
	}
	return $D;
}
function i53_value2(self) {
	const value2 = take(self);
	let $E = null;
	if (ok(self)) {
		$E = Number(value2);
	} else {
		$E = 0;
	}
	return $E;
}
function f64_value2(self) {
	const value2 = take(self);
	let $F = null;
	if (ok(self)) {
		$F = Number(value2);
	} else {
		$F = 0.0;
	}
	return $F;
}
function bool_value2(self) {
	const value2 = take(self);
	let $G = null;
	if (ok(self)) {
		$G = Boolean(value2);
	} else {
		$G = false;
	}
	return $G;
}
function fail(self, reason) {
	report(self, reason);
}
function failed(self) {
	return self[1];
}
function opened_reader(text2) {
	const $l = __try_parse_json(text2);
	let $m = null;
	if ($l[0] === 0) {
		const root = $l[1];
		$m = new3(root);
	} else {
		let reader = new3(JSON.parse("null"));
		report(reader, "malformed JSON");
		$m = reader;
	}
	return $m;
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
		const $j = frame;
		let $k = null;
		if ($j[0] === 0) {
			const text2 = $j[1];
			$k = opened_reader(text2);
		} else {
			const bytes3 = $j[1];
			$k = opened_reader(decode_utf8(bytes3));
		}
		let reader = $k;
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
function fold_unsigned(value2, modulus) {
	const truncated = Math.trunc(value2);
	const wrapped = truncated % modulus;
	let $a = null;
	if (wrapped < 0) {
		$a = wrapped + modulus;
	} else {
		$a = wrapped;
	}
	return $a;
}
function fold_signed(value2, modulus, half) {
	const wrapped = fold_unsigned(value2, modulus);
	let $b = null;
	if (wrapped >= half) {
		$b = wrapped - modulus;
	} else {
		$b = wrapped;
	}
	return $b;
}
function as_i32(self) {
	const widened = Number(self);
	return Number(fold_signed(widened, 4294967296, 2147483648));
}
function new4(start2, end) {
	return [ start2, end ];
}
function next(self) {
	let $ar = null;
	if (self[0] < self[1]) {
		const value2 = self[0];
		self[0] = self[0] + 1;
		$ar = [ 0, value2 ];
	} else {
		$ar = [ 1 ];
	}
	return $ar;
}
function call(self, request, $N) {
	return __task(async () => {
		const $O = request;
		let $P = null;
		if ($O[0] === 0) {
			const body3 = $O[1];
			const response = await (send(post(self[0], body3), $N));
			$P = [ 0, [ 0, await (response.text()) ] ];
		} else {
			const body4 = $O[1];
			const response2 = await (post_bytes(self[0], body4, $N));
			$P = [ 0, [ 1, await (bytes(response2)) ] ];
		}
		return $P;
	}, "call");
}
function send3(self, frame) {
	const $bd = self[0].v;
	let $be = null;
	if ($bd[0] === 0) {
		const handler = $bd[1];
		$be = handler(frame);
	} else {
		$be = undefined;
	}
	return $be;
}
function on_frame(self, handler) {
	self[1].v = [ 0, handler ];
}
function duplex_pair() {
	const slot_a = __shared_new([ 1 ]);
	const slot_b = __shared_new([ 1 ]);
	const a = [ slot_b, slot_a ];
	const b = [ slot_a, slot_b ];
	return [ a, b ];
}
function rpc_subprotocol() {
	return "vilan-rpc";
}
function tag_duplex_bytes(payload) {
	const tag = new Uint8Array(1);
	set(tag, 0, 0x64);
	return concat(tag, payload);
}
function tag_rpc_bytes(request, payload) {
	const header3 = new Uint8Array(5);
	set(header3, 0, 0x72);
	set(header3, 1, request);
	set(header3, 2, request >> 8);
	set(header3, 3, request >> 16);
	set(header3, 4, request >> 24);
	return concat(header3, payload);
}
function tag_client_bytes(request, payload) {
	const header3 = new Uint8Array(5);
	set(header3, 0, 0x73);
	set(header3, 1, request);
	set(header3, 2, request >> 8);
	set(header3, 3, request >> 16);
	set(header3, 4, request >> 24);
	return concat(header3, payload);
}
function on_connection(self, connection) {
	self[3] = connection;
	return self;
}
function encode_request(codec, method2, args) {
	const $M = codec[0]();
	const serializer = $M[0];
	const finish = $M[1];
	serializer[0](2);
	serializer[1]("method");
	serializer[9](method2);
	serializer[1]("args");
	serializer[3](args.length);
	for (const describe of args) {
		describe(serializer);
	}
	serializer[4]();
	serializer[2]();
	return finish();
}
function open_request(codec, frame) {
	const deserializer = codec[1](frame);
	deserializer[0]();
	deserializer[1]("method");
	const method2 = deserializer[10]();
	deserializer[1]("args");
	const arity = deserializer[3]();
	return [ method2, deserializer, arity, 0 - 1 ];
}
function encode_reply(codec, outcome) {
	const $aG = codec[0]();
	const record = $aG[0];
	const finish = $aG[1];
	let serializer = record;
	const $aH = outcome;
	let $aI = null;
	if ($aH[0] === 0) {
		const describe = $aH[1];
		serializer[5]("Success", 1);
		describe(serializer);
		serializer[6]();
		$aI = undefined;
	} else {
		const error = $aH[1];
		serializer[5]("Failure", 1);
		$aJ(error, serializer);
		serializer[6]();
		$aI = undefined;
	}
	$aI;
	return finish();
}
async function respond(self, frame) {
	const request = on_connection(open_request(self[0], frame), self[2]);
	const $bo = request[1][17]();
	let $bp = null;
	if ($bo[0] === 0) {
		const reason = $bo[1];
		$bp = [ 1, [ 1, reason ] ];
	} else {
		$bp = await (self[1](request));
	}
	const outcome = $bp;
	return encode_reply(self[0], outcome);
}
function register_client_channel(connection, codec, send4) {
	client_channels.v.push([ connection, [ send4, __clone(codec) ] ]);
}
function drop_client_channel(connection) {
	let kept = [  ];
	for (const entry of client_channels.v) {
		const $ce = entry;
		const id = $ce[0];
		const channel = $ce[1];
		if (id !== connection) {
			kept.push([ id, __clone(channel) ]);
		}
	}
	client_channels.v = kept;
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
			while (!($r(turn[0].v)) && budget > 0) {
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
function ws_accept_key(key) {
	return createHash("sha1").update(key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11").digest("base64");
}
function anonymous() {
	return [ "", "" ];
}
function header_text(headers, name) {
	let $bC = null;
	if (Object.hasOwn(headers, name)) {
		const value2 = headers[name];
		if (__json_kind(value2) === "string") {
			return [ 0, String(value2) ];
		}
		$bC = undefined;
	}
	$bC;
	return [ 1 ];
}
function reject_status(reject) {
	const $bU = reject;
	let $bV = null;
	if ($bU[0] === 0) {
		$bV = "401 Unauthorized";
	} else if ($bU[0] === 1) {
		$bV = "403 Forbidden";
	} else if ($bU[0] === 2) {
		$bV = "429 Too Many Requests";
	} else {
		$bV = "503 Service Unavailable";
	}
	return $bV;
}
function reject_announcement(reject) {
	return "__reject:" + reject_code(reject);
}
function reject_code(reject) {
	const $bS = reject;
	let $bT = null;
	if ($bS[0] === 0) {
		$bT = "401";
	} else if ($bS[0] === 1) {
		$bT = "403";
	} else if ($bS[0] === 2) {
		$bT = "429";
	} else {
		$bT = "503";
	}
	return $bT;
}
function tells_the_client(reject) {
	const $bL = reject;
	let $bM = null;
	if ($bL[0] === 0) {
		$bM = true;
	} else if ($bL[0] === 1) {
		$bM = true;
	} else if ($bL[0] === 3) {
		$bM = true;
	} else {
		$bM = false;
	}
	return $bM;
}
function refuse_upgrade(request, socket, reject) {
	if (socket.destroyed) {
		return;
	}
	const headers = request.headers;
	const speaks_rpc = selected_protocol(offered_protocols(headers)) === rpc_subprotocol();
	if (tells_the_client(reject) && speaks_rpc && Object.hasOwn(headers, "sec-websocket-key")) {
		write_upgrade_101(socket, headers);
		socket.write(text_frame(reject_announcement(reject)));
		socket.write(close_frame());
		socket.destroy();
		return;
	}
	const status = reject_status(reject);
	socket.write("HTTP/1.1 " + status + "\r" + "\n" + "Connection: close" + "\r" + "\n" + "Content-Length: 0" + "\r" + "\n" + "\r" + "\n");
	socket.destroy();
}
function write_upgrade_101(socket, headers) {
	const key = $bO(from_json_value(headers["sec-websocket-key"]), "");
	const selected = selected_protocol(offered_protocols(headers));
	let $bR = null;
	if (selected === "") {
		$bR = "";
	} else {
		$bR = "\r\nSec-WebSocket-Protocol: " + selected;
	}
	const echo = $bR;
	socket.write("HTTP/1.1 101 Switching Protocols\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Accept: " + ws_accept_key(key) + echo + "\r\n\r\n");
}
function offered_protocols(headers) {
	let offered = [  ];
	const $bJ = header_text(headers, "sec-websocket-protocol");
	let $bK = null;
	if ($bJ[0] === 0) {
		const raw = $bJ[1];
		for (const part of raw.split(",")) {
			const name = part.trim();
			if (name.length > 0) {
				offered.push(name);
			}
		}
		$bK = undefined;
	} else {
		$bK = undefined;
	}
	$bK;
	return offered;
}
function selected_protocol(offered) {
	for (const name of offered) {
		if (name === rpc_subprotocol()) {
			return name;
		}
	}
	for (const name2 of offered) {
		if (!(name2.startsWith("token."))) {
			return name2;
		}
	}
	return "";
}
function admit_handshake(service, remote) {
	const cutoff = Date.now() - service[10];
	let kept = [  ];
	let seen = 0;
	for (const entry of service[11].v) {
		const $bF = entry;
		const address = $bF[0];
		const at = $bF[1];
		let $bG = null;
		if (at > cutoff) {
			kept.push([ address, at ]);
			if (address === remote) {
				seen = seen + 1;
			}
			$bG = undefined;
		}
		$bG;
	}
	if (seen >= service[9]) {
		service[11].v = kept;
		return false;
	}
	kept.push([ remote, Date.now() ]);
	service[11].v = kept;
	return true;
}
function client_address(service, request, socket) {
	const peer = remote_address(socket);
	if (!(service[14])) {
		return peer;
	}
	const $bD = header_text(request.headers, "x-forwarded-for");
	let $bE = null;
	if ($bD[0] === 0) {
		const raw = $bD[1];
		for (const part of raw.split(",")) {
			const candidate = part.trim();
			if (candidate.length > 0) {
				return candidate;
			}
		}
		$bE = peer;
	} else {
		$bE = peer;
	}
	return $bE;
}
async function gate_upgrade(service, request, socket) {
	const remote = client_address(service, request, socket);
	if (service[8] > 0 && service[7].v >= service[8]) {
		return [ 1, [ 2 ] ];
	}
	if (service[9] > 0 && !(admit_handshake(service, remote))) {
		return [ 1, [ 2 ] ];
	}
	const $bH = service[6];
	let $bI = null;
	if ($bH[0] === 1) {
		$bI = [ 0, anonymous() ];
	} else {
		const check = $bH[1];
		const gate = check;
		let settled = false;
		let expired = false;
		if (service[13] > 0) {
			socket.setTimeout(service[13]);
			socket.on("timeout", () => {
				if (!(settled)) {
					settled = true;
					expired = true;
					refuse_upgrade(request, socket, [ 2 ]);
				}
				return;
			});
		}
		const outcome = await (gate([ request.url, request.headers, offered_protocols(request.headers), remote ]));
		if (service[13] > 0) {
			socket.setTimeout(0);
		}
		if (expired) {
			return [ 1, [ 2 ] ];
		}
		settled = true;
		$bI = outcome;
	}
	return $bI;
}
function fresh_connection() {
	const id = next_connection.v;
	next_connection.v = id + 1;
	return id;
}
function path_matches_route(path2, route) {
	return path2 === route || path2.startsWith(route + "?");
}
function services_by_mount(services) {
	return __list_sort_by(__clone(services), (a, b) => {
		let $az = null;
		if (a[3].length > b[3].length) {
			$az = -1;
		} else if (a[3].length < b[3].length) {
			$az = 1;
		} else {
			$az = 0;
		}
		return $az;
	});
}
function events_response(service) {
	const id = fresh_connection();
	const on_connect = service[4];
	const on_disconnect = service[5];
	return build(streaming(set_header(set_header(builder(), "Content-Type", "text/event-stream"), "Cache-Control", "no-cache"), (stream) => {
		send2(stream, "data: __conn:" + id + "\n" + "\n");
		const $aR = duplex_pair();
		const app_end = $aR[0];
		const wire_end = $aR[1];
		on_frame(wire_end, (frame) => {
			const $aS = frame;
			let $aT = null;
			if ($aS[0] === 0) {
				const body3 = $aS[1];
				$aT = send2(stream, "data: " + body3 + "\n" + "\n");
			} else {
				const _bytes = $aS[1];
				$aT = undefined;
			}
			return $aT;
		});
		connections.v.push([ id, wire_end ]);
		on_close(stream, () => {
			drop_connection(id);
			on_disconnect(id);
			return;
		});
		on_connect(id, app_end);
		return;
	}));
}
function send_response(request, $aX) {
	const content = body(request);
	const target = $aY(__parse_i32(connection_id_of(path(request))), __lazy("fallback", () => {
		return 0 - 1;
	}));
	for (const entry of connections.v) {
		const $bb = entry;
		const id = $bb[0];
		const wire = $bb[1];
		if (id === target) {
			$bf(($bc) => {
				send3(wire, [ 0, content ]);
				return;
			}, $aX);
		}
	}
	return build(body2(code(builder(), 204), ""));
}
async function rpc_frame_response(service, request) {
	const $bl = service[1];
	let $bm = null;
	if ($bl[0] === 0) {
		const protocol = $bl[1];
		const reply = await ($bq([ 0 ], async ($bn) => {
			return await (respond(protocol, [ 1, bytes2(request) ]));
		}));
		const $br = reply;
		let $bs = null;
		if ($br[0] === 0) {
			const frame = $br[1];
			$bs = build(body2(set_header(builder(), "Content-Type", "application/json"), frame));
		} else {
			const frame2 = $br[1];
			$bs = build(body_bytes(set_header(builder(), "Content-Type", "application/octet-stream"), frame2));
		}
		$bm = $bs;
	} else {
		$bm = build(body2(code(builder(), 501), "this service builds one instance per connection (Service::factory), and a POST rpc frame carries no connection to build for \u{2014} connect over the WebSocket transport instead"));
	}
	return $bm;
}
function unauthorized_response(service, route) {
	let $aP = null;
	if (route === "rpc") {
		const envelope = encode_reply(service[2], [ 1, [ 4 ] ]);
		const $aN = envelope;
		let $aO = null;
		if ($aN[0] === 0) {
			const frame = $aN[1];
			$aO = build(body2(set_header(code(builder(), 401), "Content-Type", "application/json"), frame));
		} else {
			const frame2 = $aN[1];
			$aO = build(body_bytes(set_header(code(builder(), 401), "Content-Type", "application/octet-stream"), frame2));
		}
		$aP = $aO;
	} else {
		$aP = build(body2(code(builder(), 401), "this service authorizes its connections at the WebSocket upgrade, and the SSE/POST legs carry no handshake to authorize \u{2014} connect over the WebSocket transport instead"));
	}
	return $aP;
}
async function service_response(service, request, $aD) {
	const path2 = path(request);
	const gated = $aE(service[6]);
	let $aV = null;
	if (path_matches_route(path2, service[3] + "events")) {
		let $aQ = null;
		if (gated) {
			$aQ = [ 0, unauthorized_response(service, "events") ];
		} else {
			$aQ = [ 0, events_response(service) ];
		}
		$aV = $aQ;
	} else if (path_matches_route(path2, service[3] + "send")) {
		let $aW = null;
		if (gated) {
			$aW = [ 0, unauthorized_response(service, "send") ];
		} else {
			$aW = [ 0, send_response(request, $aD) ];
		}
		$aV = $aW;
	} else if (path_matches_route(path2, service[3] + "rpc")) {
		let $bk = null;
		if (gated) {
			$bk = [ 0, unauthorized_response(service, "rpc") ];
		} else {
			$bk = [ 0, await (rpc_frame_response(service, request)) ];
		}
		$aV = $bk;
	} else {
		$aV = [ 1 ];
	}
	return $aV;
}
async function services_answer(services, request, $aA) {
	let answer = [ 1 ];
	for (const service of services) {
		if ($aB(answer)) {
			answer = await (service_response(service, request, $aA));
		}
	}
	return answer;
}
function fold_service_requests(services, fallback, $ay) {
	const sorted = services_by_mount(services);
	return async (request) => {
		const $bt = await (services_answer(sorted, request, $ay));
		let $bu = null;
		if ($bt[0] === 0) {
			const response = $bt[1];
			$bu = response;
		} else {
			$bu = await (fallback(request));
		}
		return $bu;
	};
}
function service_for_upgrade(services, request) {
	const path2 = request.url;
	let answer = [ 1 ];
	for (const service of services) {
		if ($aB(answer) && path_matches_route(path2, service[3])) {
			answer = [ 0, __clone(service) ];
		}
	}
	return answer;
}
function fold_service_upgrades(services, fallback, $bv) {
	let $bw = null;
	if (services.length === 0) {
		$bw = fallback;
	} else {
		const sorted = services_by_mount(services);
		$bw = [ 0, async (request, socket, head) => {
			const $bz = service_for_upgrade(sorted, request);
			let $bA = null;
			if ($bz[0] === 0) {
				const service = $bz[1];
				const $bW = await (gate_upgrade(service, request, socket));
				let $bX = null;
				if ($bW[0] === 0) {
					const session = $bW[1];
					$bX = accept_socket(request, socket, head, service, session, $bv);
				} else {
					const reject = $bW[1];
					$bX = refuse_upgrade(request, socket, reject);
				}
				$bA = $bX;
			} else {
				const $cz = fallback;
				let $cA = null;
				if ($cz[0] === 0) {
					const handler = $cz[1];
					$cA = handler(request, socket, head);
				} else {
					$cA = socket.destroy();
				}
				$bA = $cA;
			}
			return $bA;
		} ];
	}
	return $bw;
}
function accept_socket(request, socket, head, service, session, $bY) {
	const headers = request.headers;
	if (!(Object.hasOwn(headers, "sec-websocket-key"))) {
		socket.destroy();
		return;
	}
	write_upgrade_101(socket, headers);
	const id = fresh_connection();
	register_client_channel(id, service[2], (frame) => {
		const $bZ = frame;
		let $ca = null;
		if ($bZ[0] === 0) {
			const body3 = $bZ[1];
			$ca = socket.write(text_frame("s:0:" + body3));
		} else {
			const bytes3 = $bZ[1];
			$ca = socket.write(binary_frame(tag_client_bytes(0, bytes3)));
		}
		return $ca;
	});
	const protocol = service[0]([ id, __clone(session), client_address(service, request, socket) ]);
	service[7].v = service[7].v + 1;
	const on_connect = service[4];
	const on_disconnect = service[5];
	const $cb = duplex_pair();
	const app_end = $cb[0];
	const wire_end = $cb[1];
	on_frame(wire_end, (frame) => {
		const $cc = frame;
		let $cd = null;
		if ($cc[0] === 0) {
			const body3 = $cc[1];
			$cd = socket.write(text_frame("d:" + body3));
		} else {
			const bytes3 = $cc[1];
			$cd = socket.write(binary_frame(tag_duplex_bytes(bytes3)));
		}
		return $cd;
	});
	connections.v.push([ id, __clone(wire_end) ]);
	let closed = false;
	const teardown = () => {
		if (!(closed)) {
			closed = true;
			service[7].v = service[7].v - 1;
			drop_connection(id);
			drop_client_channel(id);
			on_disconnect(id);
		}
		return;
	};
	let greeted = false;
	if (service[12] > 0) {
		socket.setTimeout(service[12]);
		socket.on("timeout", () => {
			if (!(greeted)) {
				socket.destroy();
			}
			return;
		});
	}
	const parser = new6();
	const receive = (chunk) => {
		let $cf = null;
		if (!(greeted)) {
			greeted = true;
			if (service[12] > 0) {
				socket.setTimeout(0);
			}
			$cf = undefined;
		}
		$cf;
		for (const event of feed(parser, chunk)) {
			const $co = event;
			let $cp = null;
			if ($co[0] === 0) {
				const frame = $co[1];
				let $ct = null;
				if (frame.startsWith("r:")) {
					const rest = __substring(frame, 2, frame.length);
					const parts = rest.split(":");
					const id_text = __at(parts, 0);
					if (id_text.length < rest.length) {
						const payload = __substring(rest, id_text.length + 1, rest.length);
						__task(async () => {
							const reply = await ($bq([ 0 ], async ($cq) => {
								return await (respond(protocol, [ 0, payload ]));
							}));
							const $cr = reply;
							let $cs = null;
							if ($cr[0] === 0) {
								const answer = $cr[1];
								socket.write(text_frame("r:" + id_text + ":" + answer));
								$cs = undefined;
							} else {
								const bytes4 = $cr[1];
								const id3 = $aY(__parse_i32(id_text), __lazy("fallback", () => {
									return 0 - 1;
								}));
								socket.write(binary_frame(tag_rpc_bytes(id3, bytes4)));
								$cs = undefined;
							}
							return $cs;
						}, "accept_socket");
					}
					$ct = undefined;
				} else if (frame.startsWith("d:")) {
					$bf(($cu) => {
						send3(wire_end, [ 0, __substring(frame, 2, frame.length) ]);
						return;
					}, $bY);
				}
				$cp = $ct;
			} else if ($co[0] === 2) {
				const payload2 = $co[1];
				$cp = socket.write(pong_frame(payload2));
			} else if ($co[0] === 3) {
				socket.write(close_frame());
				socket.destroy();
				$cp = undefined;
			} else {
				const bytes3 = $co[1];
				if (bytes3.length > 0 && bytes3.at(0) === 0x64) {
					$bf(($cv) => {
						send3(wire_end, [ 1, bytes3.slice(1, bytes3.length) ]);
						return;
					}, $bY);
				} else if (bytes3.length >= 5 && bytes3.at(0) === 0x72) {
					const id2 = bytes3.at(1) | bytes3.at(2) << 8 | bytes3.at(3) << 16 | bytes3.at(4) << 24;
					const payload3 = bytes3.slice(5, bytes3.length);
					__task(async () => {
						const reply = await ($bq([ 0 ], async ($cw) => {
							return await (respond(protocol, [ 1, __clone(payload3) ]));
						}));
						const $cx = reply;
						let $cy = null;
						if ($cx[0] === 1) {
							const answer = $cx[1];
							socket.write(binary_frame(tag_rpc_bytes(id2, answer)));
							$cy = undefined;
						} else {
							const answer2 = $cx[1];
							socket.write(text_frame("r:" + id2 + ":" + answer2));
							$cy = undefined;
						}
						return $cy;
					}, "accept_socket");
				}
				$cp = undefined;
			}
			$cp;
		}
		return;
	};
	if (head.length > 0) {
		receive(head);
	}
	socket.on("data", receive);
	socket.on("close", teardown);
	socket.on("end", () => {
		teardown();
		socket.destroy();
		return;
	});
	socket.on("error", () => {
		return socket.destroy();
	});
	socket.write(text_frame("__conn:" + id));
	on_connect(id, app_end);
}
function drop_connection(target) {
	let kept = [  ];
	for (const entry of connections.v) {
		const $aU = entry;
		const id = $aU[0];
		const wire = $aU[1];
		if (id !== target) {
			kept.push([ id, __clone(wire) ]);
		}
	}
	connections.v = kept;
}
function connection_id_of(path2) {
	const parts = path2.split("c=");
	return __at(parts, parts.length - 1);
}
function to_lowercase_ascii(self) {
	const lowercase = "abcdefghijklmnopqrstuvwxyz";
	const length = self.length;
	let out = "";
	let index = 0;
	while (index < length) {
		const unit = self.charCodeAt(index);
		if (unit >= 65 && unit <= 90) {
			const letter = as_i32(unit - 65);
			out = out + __substring(lowercase, letter, letter + 1);
		} else {
			out = out + __substring(self, index, index + 1);
		}
		index = index + 1;
	}
	return out;
}
function ambient_signal($S) {
	const $T = $S;
	let $U = null;
	if ($T[0] === 0) {
		const n = $T[1];
		$U = [ 0, n.signal_of() ];
	} else {
		$U = [ 1 ];
	}
	return $U;
}
function is_watching() {
	const $ao = __env("VILAN_WATCHING");
	let $ap = null;
	if ($ao[0] === 0) {
		const value2 = $ao[1];
		$ap = value2 === "1";
	} else {
		$ap = false;
	}
	return $ap;
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
function variant_tag2(self) {
	return self[5]();
}
function begin_variant4(self, name, arity) {
	self[6](name, arity);
}
function end_variant4(self) {
	self[7]();
}
function str_value4(self) {
	return self[10]();
}
function i32_value4(self) {
	return self[11]();
}
function fail2(self, reason) {
	self[16](reason);
}
function encode_frame(opcode, payload) {
	const length = payload.length;
	let header3 = new Uint8Array(2);
	if (length < 126) {
		set(header3, 1, length);
	} else if (length < 65536) {
		header3 = new Uint8Array(4);
		set(header3, 1, 126);
		set(header3, 2, length >> 8);
		set(header3, 3, length);
	} else {
		header3 = new Uint8Array(10);
		set(header3, 1, 127);
		set(header3, 6, length >> 24);
		set(header3, 7, length >> 16);
		set(header3, 8, length >> 8);
		set(header3, 9, length);
	}
	set(header3, 0, 0x80 | opcode);
	return concat(header3, payload);
}
function text_frame(text2) {
	return encode_frame(0x1, encode_utf8(text2));
}
function binary_frame(payload) {
	return encode_frame(0x2, payload);
}
function pong_frame(payload) {
	return encode_frame(0xA, payload);
}
function close_frame() {
	return encode_frame(0x8, new Uint8Array(0));
}
function new6() {
	return [ __shared_new(new Uint8Array(0)), __shared_new(0), __shared_new(new Uint8Array(0)), __shared_new(false) ];
}
function feed(self, chunk) {
	let events = [  ];
	if (self[3].v) {
		return events;
	}
	self[0].v = concat(self[0].v, chunk);
	let scanning = true;
	while (scanning) {
		const buffer2 = self[0].v;
		const available = buffer2.length;
		let $cn = null;
		if (available < 2) {
			scanning = false;
		} else {
			const first = buffer2.at(0);
			const second = buffer2.at(1);
			const fin = (first & 0x80) !== 0;
			const opcode = first & 0x0F;
			const masked = (second & 0x80) !== 0;
			let length = second & 0x7F;
			let header3 = 2;
			let valid = true;
			let $cg = null;
			if (length === 126) {
				if (available < 4) {
					valid = false;
					scanning = false;
				} else {
					length = buffer2.at(2) << 8 | buffer2.at(3);
					header3 = 4;
				}
				$cg = undefined;
			} else if (length === 127) {
				if (available < 10) {
					valid = false;
					scanning = false;
				} else {
					const oversized = buffer2.at(2) !== 0 || buffer2.at(3) !== 0 || buffer2.at(4) !== 0 || buffer2.at(5) !== 0 || (buffer2.at(6) & 0x80) !== 0;
					if (oversized) {
						self[3].v = true;
						events.push([ 3 ]);
						return events;
					}
					length = buffer2.at(6) << 24 | buffer2.at(7) << 16 | buffer2.at(8) << 8 | buffer2.at(9);
					header3 = 10;
				}
				$cg = undefined;
			}
			$cg;
			let $cm = null;
			if (valid) {
				const mask_at = header3;
				let $ch = null;
				if (masked) {
					$ch = header3 + 4 + length;
				} else {
					$ch = header3 + length;
				}
				const total = $ch;
				let $cl = null;
				if (available < total) {
					scanning = false;
				} else {
					let $ci = null;
					if (masked) {
						$ci = mask_at + 4;
					} else {
						$ci = mask_at;
					}
					const payload_at = $ci;
					const payload = buffer2.slice(payload_at, payload_at + length);
					let $cj = null;
					if (masked) {
						let index = 0;
						while (index < length) {
							set(payload, index, payload.at(index) ^ buffer2.at(mask_at + (index & 3)));
							index = index + 1;
						}
						$cj = undefined;
					}
					$cj;
					self[0].v = buffer2.slice(total, available);
					for (const event of dispatch(self, fin, opcode, payload)) {
						events.push(event);
					}
					if (self[3].v) {
						return events;
					}
					$cl = undefined;
				}
				$cm = $cl;
			}
			$cn = $cm;
		}
		$cn;
	}
	return events;
}
function dispatch(self, fin, opcode, payload) {
	let events = [  ];
	if (opcode === 0x9) {
		events.push([ 2, __clone(payload) ]);
		return events;
	}
	if (opcode === 0xA) {
		return events;
	}
	if (opcode === 0x8) {
		self[3].v = true;
		events.push([ 3 ]);
		return events;
	}
	if (opcode === 0x0) {
		if (self[1].v === 0) {
			self[3].v = true;
			events.push([ 3 ]);
			return events;
		}
		self[2].v = concat(self[2].v, payload);
		if (fin) {
			const complete_opcode = self[1].v;
			const complete = self[2].v;
			self[1].v = 0;
			self[2].v = new Uint8Array(0);
			events.push(emit(self, complete_opcode, complete));
		}
		return events;
	}
	if (opcode === 0x1 || opcode === 0x2) {
		if (fin) {
			events.push(emit(self, opcode, payload));
		} else {
			self[1].v = opcode;
			self[2].v = __clone(payload);
		}
		return events;
	}
	self[3].v = true;
	events.push([ 3 ]);
	return events;
}
function emit(self, opcode, payload) {
	let $ck = null;
	if (opcode === 0x1) {
		$ck = [ 0, decode_utf8(payload) ];
	} else {
		$ck = [ 1, __clone(payload) ];
	}
	return $ck;
}
function echo_over_http(url) {
	return [ [ url ], json_codec() ];
}
function $r(self) {
	return self.length === 0;
}
function $J(self, serializer) {
	i32_value3(serializer, self);
}
function $ac(deserializer) {
	return i32_value4(deserializer);
}
function $ai(deserializer) {
	return str_value4(deserializer);
}
function $af(deserializer) {
	const tag = variant_tag2(deserializer);
	const $ag = tag;
	let $ah = null;
	if ($ag === "Transport") {
		begin_variant4(deserializer, "Transport", 1);
		const p0 = $ai(deserializer);
		end_variant4(deserializer);
		$ah = [ 0, p0 ];
	} else if ($ag === "Decode") {
		begin_variant4(deserializer, "Decode", 1);
		const p02 = $ai(deserializer);
		end_variant4(deserializer);
		$ah = [ 1, p02 ];
	} else if ($ag === "Remote") {
		begin_variant4(deserializer, "Remote", 1);
		const p03 = $ai(deserializer);
		end_variant4(deserializer);
		$ah = [ 2, p03 ];
	} else if ($ag === "Contract") {
		begin_variant4(deserializer, "Contract", 1);
		const p04 = $ai(deserializer);
		end_variant4(deserializer);
		$ah = [ 3, p04 ];
	} else if ($ag === "Unauthorized") {
		begin_variant4(deserializer, "Unauthorized", 0);
		end_variant4(deserializer);
		$ah = [ 4 ];
	} else if ($ag === "Unavailable") {
		begin_variant4(deserializer, "Unavailable", 0);
		end_variant4(deserializer);
		$ah = [ 5 ];
	} else {
		fail2(deserializer, "unknown variant \'" + tag + "\'");
		const f0 = $ai(deserializer);
		$ah = [ 0, f0 ];
	}
	return $ah;
}
async function $K(transport, codec, method2, args, $L) {
	const outcome = await (call(transport, encode_request(codec, method2, args), $L));
	const $Y = outcome;
	let $Z = null;
	if ($Y[0] === 1) {
		const reason = $Y[1];
		$Z = [ 1, [ 0, reason ] ];
	} else {
		const reply_frame = $Y[1];
		let deserializer = codec[1](reply_frame);
		const tag = deserializer[5]();
		const $aa = tag;
		let $ab = null;
		if ($aa === "Success") {
			deserializer[6]("Success", 1);
			const value2 = $ac(deserializer);
			const $ad = deserializer[17]();
			let $ae = null;
			if ($ad[0] === 1) {
				$ae = [ 0, value2 ];
			} else {
				const reason2 = $ad[1];
				$ae = [ 1, [ 1, reason2 ] ];
			}
			$ab = $ae;
		} else if ($aa === "Failure") {
			deserializer[6]("Failure", 1);
			const error = $af(deserializer);
			deserializer[7]();
			$ab = [ 1, error ];
		} else {
			$ab = [ 1, [ 1, "unrecognized reply envelope" ] ];
		}
		$Z = $ab;
	}
	return $Z;
}
async function $H(self, value2, $I) {
	return await ($K(self[0], self[1], "echo", [ (serializer) => {
		serializer = __clone(serializer);
		return $J(value2, serializer);
	} ], $I));
}
function $aB(self) {
	const $aC = self;
	return $aC[0] === 1;
}
function $aE(self) {
	const $aF = self;
	return $aF[0] === 0;
}
function $aM(self, serializer) {
	str_value3(serializer, self);
}
function $aJ(self, serializer) {
	const $aK = self;
	let $aL = null;
	if ($aK[0] === 0) {
		const p0 = $aK[1];
		begin_variant3(serializer, "Transport", 1);
		$aM(p0, serializer);
		end_variant3(serializer);
		$aL = undefined;
	} else if ($aK[0] === 1) {
		const p02 = $aK[1];
		begin_variant3(serializer, "Decode", 1);
		$aM(p02, serializer);
		end_variant3(serializer);
		$aL = undefined;
	} else if ($aK[0] === 2) {
		const p03 = $aK[1];
		begin_variant3(serializer, "Remote", 1);
		$aM(p03, serializer);
		end_variant3(serializer);
		$aL = undefined;
	} else if ($aK[0] === 3) {
		const p04 = $aK[1];
		begin_variant3(serializer, "Contract", 1);
		$aM(p04, serializer);
		end_variant3(serializer);
		$aL = undefined;
	} else if ($aK[0] === 4) {
		begin_variant3(serializer, "Unauthorized", 0);
		end_variant3(serializer);
		$aL = undefined;
	} else {
		begin_variant3(serializer, "Unavailable", 0);
		end_variant3(serializer);
		$aL = undefined;
	}
	return $aL;
}
function $aY(self, fallback) {
	const $aZ = self;
	let $ba = null;
	if ($aZ[0] === 0) {
		const x = __clone($aZ[1]);
		$ba = x;
	} else {
		$ba = __clone(__force(fallback));
	}
	return $ba;
}
function $bf(body3, $bg) {
	const $bh = $bg;
	let $bi = null;
	if ($bh[0] === 0) {
		const current = $bh[1];
		$bi = body3(current);
	} else {
		const fresh = new5();
		const result2 = body3(fresh);
		drain(fresh);
		fresh[3].v = true;
		$bi = result2;
	}
	return $bi;
}
async function $bq(policy, body3) {
	const fresh = new5();
	const result2 = await (body3(fresh));
	drain(fresh);
	fresh[3].v = true;
	return result2;
}
function $bO(self, fallback) {
	const $bP = self;
	let $bQ = null;
	if ($bP[0] === 0) {
		const x = __clone($bP[1]);
		$bQ = x;
	} else {
		$bQ = __clone(fallback);
	}
	return $bQ;
}
const client_channels = __shared_new([  ]);
const draining_turns = __shared_new([  ]);
const connections = __shared_new([  ]);
const next_connection = __shared_new(0);
(async () => {
	start(build2(on_start(on_request(port(builder2(), 59779), (request) => {
		const $c = header2(request, "content-type");
		let $d = null;
		if ($c[0] === 0) {
			const value2 = $c[1];
			$d = value2;
		} else {
			$d = "(none)";
		}
		const seen = $d;
		console.log("  [server] " + method(request) + " " + path(request) + " content-type=" + seen);
		return build(body2(set_header(builder(), "Content-Type", "application/json"), "{\"Success\":1}"));
	}), async (server) => {
		console.log("--- the SHIPPED HttpTransport, text frame (json codec)");
		const client = echo_over_http("http://localhost:59779/rpc");
		await ($H(client, 1, [ 1 ]));
		console.log("--- HttpTransport::call directly, a Binary frame");
		const transport = [ "http://localhost:59779/rpc-bytes" ];
		await (call(transport, [ 0, "{}" ], [ 1 ]));
		console.log("--- a hand fetch with NO header chained");
		const bare = await (send(post("http://localhost:59779/bare", "{}"), [ 1 ]));
		console.log("  bare status=" + bare.status);
		console.log("--- a hand fetch with the header chained");
		const typed = await (send(header(post("http://localhost:59779/typed", "{}"), "Content-Type", "application/json"), [ 1 ]));
		console.log("  typed status=" + typed.status);
		process.exit(0);
		return;
	}), [ 1 ]));
})().catch(($cG) => {
	console.error(String($cG));
	process.exit(1);
});
