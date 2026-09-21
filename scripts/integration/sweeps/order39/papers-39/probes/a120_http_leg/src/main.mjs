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
function __hash(value) {
	return (typeof value === "object" && value !== null) ? JSON.stringify(value) : value;
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
function __list_get(list, index) {
	return index >= 0 && index < list.length ? [ 0, __clone(list[index]) ] : [ 1 ];
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
let __shared_identity_next = 1;
function __shared_identity(cell) {
	return cell.__id ??= __shared_identity_next++;
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
function attach_ambient_signal(options, $cx) {
	const $cB = ambient_signal($cx);
	let $cC = null;
	if ($cB[0] === 0) {
		const signal = $cB[1];
		$cC = options.signal = signal;
	} else {
		$cC = undefined;
	}
	return $cC;
}
function get(url) {
	return [ url, "GET", "", [  ] ];
}
function post(url, body3) {
	return [ url, "POST", body3, [  ] ];
}
function header(self, name, value2) {
	self[3].push([ name, value2 ]);
	return self;
}
async function send(self, $cw) {
	const options = Object();
	options.method = self[1];
	options.headers = self[3];
	if (self[1] !== "GET") {
		options.body = self[2];
	}
	attach_ambient_signal(options, $cw);
	return await (fetch(self[0], options));
}
function to_hex(self) {
	const digits = "0123456789abcdef";
	let out = "";
	const $cM = new4(0, self.length);
	while (true) {
		const $cN = next($cM);
		if ($cN[0] !== 0) {
			break;
		}
		const index = $cN[1];
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
function decode_utf8(bytes2) {
	return new TextDecoder().decode(bytes2);
}
function eq(self, b) {
	return self === b;
}
function hash(self) {
	return __hash(self);
}
function remote_address(self) {
	const raw = self.remoteAddress;
	let $dP = null;
	if (__json_kind(raw) === "string") {
		$dP = String(raw);
	} else {
		$dP = "";
	}
	return $dP;
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
function bytes(self) {
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
	let $cS = null;
	if (method2 === "GET" || method2 === "HEAD") {
		const $cQ = header2(request, "If-None-Match");
		let $cR = null;
		if ($cQ[0] === 0) {
			const header3 = $cQ[1];
			if (if_none_match_matches(header3, etag)) {
				return set_header(code(builder(), 304), "ETag", etag);
			}
			$cR = undefined;
		} else {
			$cR = undefined;
		}
		$cS = $cR;
	}
	$cS;
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
			const $eP = header3;
			const name = $eP[0];
			const value2 = $eP[1];
			node_response.setHeader(name, value2);
		}
		const $eQ = response[2];
		let $eR = null;
		if ($eQ[0] === 0) {
			const text2 = $eQ[1];
			$eR = node_response.end(text2);
		} else if ($eQ[0] === 1) {
			const bytes2 = $eQ[1];
			$eR = node_response.end(bytes2);
		} else {
			const on_open = $eQ[1];
			$eR = on_open([ __clone(node_response) ]);
		}
		return $eR;
	});
	const $eS = upgrade_handler;
	let $eT = null;
	if ($eS[0] === 0) {
		const handler = $eS[1];
		$eT = node_server.on("upgrade", handler);
	} else {
		$eT = undefined;
	}
	$eT;
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
function build2(self, $cD) {
	const assets = __clone(self[6]);
	const cache = self[7];
	const fallback = self[1];
	return [ self[0], fold_service_requests(self[5], async (request) => {
		return await (respond_from_build(assets, cache, fallback, request));
	}, $cD), self[2], self[3], fold_service_upgrades(self[5], self[4], $cD), [ 1 ] ];
}
async function respond_from_build(assets, cache, fallback, request) {
	const $cE = asset_for(assets, path(request));
	let $cF = null;
	if ($cE[0] === 0) {
		const asset = $cE[1];
		const $cG = cache;
		let $cH = null;
		if ($cG[0] === 0) {
			const policy = $cG[1];
			$cH = await (cached_asset_response(asset, policy(asset[0]), request));
		} else {
			$cH = await (asset_response(asset));
		}
		$cF = $cH;
	} else {
		$cF = await (fallback(request));
	}
	return $cF;
}
async function asset_response(asset) {
	return build(body_bytes(set_header(builder(), "Content-Type", asset[2]), await (asset_body(asset))));
}
async function cached_asset_response(asset, policy, request) {
	const body3 = await (asset_body(asset));
	let $cT = null;
	if (policy[0]) {
		$cT = etag_response(request, await (etag_of(body3)), body3, asset[2]);
	} else {
		$cT = body_bytes(set_header(builder(), "Content-Type", asset[2]), body3);
	}
	let response = $cT;
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
	let $cK = null;
	if (is_watching()) {
		$cK = await (readFile(asset[1]));
	} else {
		$cK = __clone(asset[3]);
	}
	return $cK;
}
function has_field(self, name) {
	return Object.hasOwn(self, name);
}
function from_json_value(value2) {
	let $eb = null;
	if (__json_kind(value2) === "string") {
		$eb = [ 0, String(value2) ];
	} else {
		$eb = [ 1, "expected a string" ];
	}
	return $eb;
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
	const $L = __list_pop(self[2]);
	let $M = null;
	if ($L[0] === 0) {
		const saved = $L[1];
		$M = saved;
	} else {
		$M = false;
	}
	self[1] = $M;
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
	let $N = null;
	if (arity === 0) {
		value(self, JSON.stringify(name));
	} else {
		open2(self, "{");
		self[0] = self[0] + JSON.stringify(name) + ":";
		self[1] = false;
		if (arity > 1) {
			self[0] = self[0] + "[";
		}
		$N = undefined;
	}
	return $N;
}
function end_variant(self) {
	const $O = __list_pop(self[3]);
	let $P = null;
	if ($O[0] === 0) {
		const opened = $O[1];
		$P = opened;
	} else {
		$P = 0;
	}
	const arity = $P;
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
	const $W = self[1];
	let $X = null;
	if ($W[0] === 0) {
		const _reason = $W[1];
		$X = false;
	} else {
		$X = true;
	}
	return $X;
}
function report(self, reason) {
	const $U = self[1];
	let $V = null;
	if ($U[0] === 0) {
		const _first = $U[1];
		$V = undefined;
	} else {
		self[1] = [ 0, reason ];
		$V = undefined;
	}
	return $V;
}
function top(self) {
	let $Z = null;
	if (!(ok(self)) || $p(self[0])) {
		$Z = JSON.parse("null");
	} else {
		$Z = __clone(__at(self[0], self[0].length - 1));
	}
	return $Z;
}
function take(self) {
	if (!(ok(self))) {
		return JSON.parse("null");
	}
	const $ab = __list_pop(self[0]);
	let $ac = null;
	if ($ab[0] === 0) {
		const value2 = $ab[1];
		$ac = value2;
	} else {
		report(self, "unexpected end of document");
		$ac = JSON.parse("null");
	}
	return $ac;
}
function begin_struct2(self) {

}
function field2(self, name) {
	const subject = top(self);
	let $aa = null;
	if (ok(self)) {
		if (Object.hasOwn(subject, name)) {
			self[0].push(subject[name]);
		} else {
			report(self, "missing field \'" + name + "\'");
		}
		$aa = undefined;
	}
	return $aa;
}
function end_struct2(self) {
	take(self);
}
function begin_list2(self) {
	const subject = take(self);
	let $ad = null;
	if (ok(self)) {
		const elements = subject;
		let index = elements.length - 1;
		while (index >= 0) {
			self[0].push(__clone(__at(elements, index)));
			index = index - 1;
		}
		$ad = elements.length;
	} else {
		$ad = 0;
	}
	return $ad;
}
function end_list2(self) {

}
function variant_tag(self) {
	let $ae = null;
	if (ok(self)) {
		$ae = __json_tag(top(self));
	} else {
		$ae = "";
	}
	return $ae;
}
function begin_variant2(self, name, arity) {
	const subject = take(self);
	let $ah = null;
	if (ok(self) && arity > 0) {
		let $ag = null;
		if (Object.hasOwn(subject, name)) {
			const payload = subject[name];
			let $af = null;
			if (arity === 1) {
				self[0].push(payload);
			} else {
				const elements = payload;
				let index = elements.length - 1;
				while (index >= 0) {
					self[0].push(__clone(__at(elements, index)));
					index = index - 1;
				}
				$af = undefined;
			}
			$ag = $af;
		} else {
			report(self, "missing payload for variant \'" + name + "\'");
		}
		$ah = $ag;
	}
	return $ah;
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
	let $ai = null;
	if (ok(self)) {
		$ai = String(value2);
	} else {
		$ai = "";
	}
	return $ai;
}
function i32_value2(self) {
	const value2 = take(self);
	let $aj = null;
	if (ok(self)) {
		$aj = Number(value2);
	} else {
		$aj = 0;
	}
	return $aj;
}
function u32_value2(self) {
	const value2 = take(self);
	let $ak = null;
	if (ok(self)) {
		$ak = Number(value2);
	} else {
		$ak = 0;
	}
	return $ak;
}
function i53_value2(self) {
	const value2 = take(self);
	let $al = null;
	if (ok(self)) {
		$al = Number(value2);
	} else {
		$al = 0;
	}
	return $al;
}
function f64_value2(self) {
	const value2 = take(self);
	let $am = null;
	if (ok(self)) {
		$am = Number(value2);
	} else {
		$am = 0.0;
	}
	return $am;
}
function bool_value2(self) {
	const value2 = take(self);
	let $an = null;
	if (ok(self)) {
		$an = Boolean(value2);
	} else {
		$an = false;
	}
	return $an;
}
function fail(self, reason) {
	report(self, reason);
}
function failed(self) {
	return self[1];
}
function opened_reader(text2) {
	const $S = __try_parse_json(text2);
	let $T = null;
	if ($S[0] === 0) {
		const root = $S[1];
		$T = new3(root);
	} else {
		let reader = new3(JSON.parse("null"));
		report(reader, "malformed JSON");
		$T = reader;
	}
	return $T;
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
		const $Q = frame;
		let $R = null;
		if ($Q[0] === 0) {
			const text2 = $Q[1];
			$R = opened_reader(text2);
		} else {
			const bytes2 = $Q[1];
			$R = opened_reader(decode_utf8(bytes2));
		}
		let reader = $R;
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
	let $cO = null;
	if (wrapped < 0) {
		$cO = wrapped + modulus;
	} else {
		$cO = wrapped;
	}
	return $cO;
}
function fold_signed(value2, modulus, half) {
	const wrapped = fold_unsigned(value2, modulus);
	let $cP = null;
	if (wrapped >= half) {
		$cP = wrapped - modulus;
	} else {
		$cP = wrapped;
	}
	return $cP;
}
function as_i32(self) {
	const widened = Number(self);
	return Number(fold_signed(widened, 4294967296, 2147483648));
}
function new4(start3, end) {
	return [ start3, end ];
}
function next(self) {
	let $cL = null;
	if (self[0] < self[1]) {
		const value2 = self[0];
		self[0] = self[0] + 1;
		$cL = [ 0, value2 ];
	} else {
		$cL = [ 1 ];
	}
	return $cL;
}
function send3(self, frame) {
	const $bP = self[0].v;
	let $bQ = null;
	if ($bP[0] === 0) {
		const handler = $bP[1];
		$bQ = handler(frame);
	} else {
		$bQ = undefined;
	}
	return $bQ;
}
function on_frame(self, handler) {
	self[1].v = [ 0, handler ];
}
function clear_on_frame(self) {
	self[1].v = [ 1 ];
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
	const $dc = codec[0]();
	const record = $dc[0];
	const finish = $dc[1];
	let serializer = record;
	const $dd = outcome;
	let $de = null;
	if ($dd[0] === 0) {
		const describe = $dd[1];
		serializer[5]("Success", 1);
		describe(serializer);
		serializer[6]();
		$de = undefined;
	} else {
		const error = $dd[1];
		serializer[5]("Failure", 1);
		$df(error, serializer);
		serializer[6]();
		$de = undefined;
	}
	$de;
	return finish();
}
function for_connection(self, connection) {
	self[2] = connection;
	return self;
}
async function respond(self, frame) {
	const request = on_connection(open_request(self[0], frame), self[2]);
	const $dC = request[1][17]();
	let $dD = null;
	if ($dC[0] === 0) {
		const reason = $dC[1];
		$dD = [ 1, [ 1, reason ] ];
	} else {
		$dD = await (self[1](request));
	}
	const outcome = $dD;
	return encode_reply(self[0], outcome);
}
function decode_failed(request) {
	return request[1][17]();
}
async function notified(run) {
	await (run());
	return [ 0, (serializer) => {
		serializer = __clone(serializer);
		return $A(true, serializer);
	} ];
}
function no_connection_for_handle(request) {
	return [ 1, [ 2, "`" + request[0] + "` returns a signal handle, and this request arrived on no connection: a handle\'s reply is a channel id minted in the CONNECTION\'s capability table, and the connectionless legs \u{2014} the `{mount}rpc` POST route, and a `local_rpc` transport no `for_connection` stamped \u{2014} have none. Reach this method over the socket transport, which is what every generated `Client::connect` uses" ] ];
}
function new5() {
	return [ __shared_new([  ]), __shared_new([  ]) ];
}
function handles(self, methods) {
	self[1].v = __clone(methods);
	return __clone(self);
}
function on(self, method2, handler) {
	self[0].v.push([ method2, handler ]);
	return __clone(self);
}
async function handle(self, request) {
	const $aq = $ap($ao(self[0].v, (route2) => {
		return route2[0] === request[0];
	}));
	let $ar = null;
	if ($aq[0] === 0) {
		const route = $aq[1];
		$ar = await (route[1](request));
	} else {
		$ar = [ 1, [ 2, "unknown method: " + request[0] ] ];
	}
	return $ar;
}
function into_protocol(self, codec) {
	return [ __clone(codec), async (request) => {
		return await (handle(self, request));
	}, 0 - 1, __clone(self[1].v) ];
}
function encode_update(codec, channel, describe) {
	const $bO = codec[0]();
	const serializer = $bO[0];
	const finish = $bO[1];
	serializer[5]("Update", 2);
	serializer[10](channel);
	describe(serializer);
	serializer[6]();
	return finish();
}
function register_session(connection, wire, codec, $at) {
	reactive_sessions.v.push([ connection, new6(wire, codec, $at) ]);
}
function drop_session(connection, $by) {
	let kept = [  ];
	for (const entry of reactive_sessions.v) {
		const $bz = entry;
		const id = $bz[0];
		const session = $bz[1];
		if (id === connection) {
			dispose(session, $by);
		} else {
			kept.push([ id, __clone(session) ]);
		}
	}
	reactive_sessions.v = kept;
}
function session_of(connection) {
	for (const entry of reactive_sessions.v) {
		const $G = entry;
		const id = $G[0];
		const session = $G[1];
		if (id === connection) {
			return [ 0, __clone(session) ];
		}
	}
	return [ 1 ];
}
function register_client_channel(connection, codec, send4) {
	client_channels.v.push([ connection, [ send4, __clone(codec) ] ]);
}
function drop_client_channel(connection) {
	let kept = [  ];
	for (const entry of client_channels.v) {
		const $es = entry;
		const id = $es[0];
		const channel = $es[1];
		if (id !== connection) {
			kept.push([ id, __clone(channel) ]);
		}
	}
	client_channels.v = kept;
}
function fresh_channel() {
	const id = next_channel.v;
	next_channel.v = id + 1;
	return id;
}
function keyed(self) {
	const $bJ = self[1];
	let $bK = null;
	if ($bJ[0] === 0) {
		const _reader = $bJ[1];
		$bK = true;
	} else {
		$bK = false;
	}
	return $bK;
}
function same_demand(left, right) {
	const $aE = left;
	let $aF = null;
	if ($aE[0] === 1) {
		const $aG = right;
		let $aH = null;
		if ($aG[0] === 1) {
			$aH = true;
		} else {
			const _present = $aG[1];
			$aH = false;
		}
		$aF = $aH;
	} else {
		const a = $aE[1];
		const $aI = right;
		let $aJ = null;
		if ($aI[0] === 1) {
			$aJ = false;
		} else {
			const b = $aI[1];
			$aJ = eq(a, b);
		}
		$aF = $aJ;
	}
	return $aF;
}
function new6(transport, codec, $au) {
	const server = [ __clone(transport), __clone(codec), __shared_new([  ]), __shared_new([  ]) ];
	on_frame(server[0], (frame) => {
		$bu(($av) => {
			return receive(server, frame, [ 0, $av ]);
		}, $au);
		return;
	});
	return server;
}
function dynamic_channel_for(self, identity, keyed2) {
	for (const entry of self[2].v) {
		const $bI = entry;
		const id = $bI[0];
		const capability = $bI[1];
		let $bL = null;
		if (capability[2] && capability[3] === identity) {
			if (keyed(capability) === keyed2) {
				return [ 0, id ];
			}
			$bL = undefined;
		}
		$bL;
	}
	return [ 1 ];
}
function capability_of(self, channel) {
	for (const entry of self[2].v) {
		const $aB = entry;
		const id = $aB[0];
		const capability = $aB[1];
		if (id === channel) {
			return [ 0, __clone(capability) ];
		}
	}
	return [ 1 ];
}
function forward_for(self, channel, key) {
	for (const forward of self[3].v) {
		let $aK = null;
		if (forward[0] === channel) {
			if (same_demand(forward[1], key)) {
				return [ 0, forward ];
			}
			$aK = undefined;
		}
		$aK;
	}
	return [ 1 ];
}
function open_forward(self, channel, key, start3) {
	const $aL = forward_for(self, channel, key);
	let $aM = null;
	if ($aL[0] === 0) {
		const held = $aL[1];
		$aM = held[3].v = held[3].v + 1;
	} else {
		const subscription = start3();
		self[3].v.push([ channel, key, subscription, __shared_new(1) ]);
		$aM = undefined;
	}
	return $aM;
}
function close_forward(self, channel, key, $aP) {
	let kept = [  ];
	let remaining = 0;
	for (const forward of self[3].v) {
		let keep = true;
		let $ba = null;
		if (forward[0] === channel && same_demand(forward[1], key)) {
			const after = forward[3].v - 1;
			forward[3].v = after;
			if (after <= 0) {
				dispose2(forward[2], $aP);
				keep = false;
			}
			$ba = undefined;
		}
		$ba;
		let $bb = null;
		if (keep) {
			kept.push(__clone(forward));
			if (forward[0] === channel) {
				remaining = remaining + 1;
			}
			$bb = undefined;
		}
		$bb;
	}
	self[3].v = kept;
	return remaining === 0;
}
function start2(self, channel) {
	const $aC = capability_of(self, channel);
	let $aD = null;
	if ($aC[0] === 0) {
		const capability = $aC[1];
		$aD = open_forward(self, channel, [ 1 ], capability[0]);
	} else {
		$aD = undefined;
	}
	return $aD;
}
function start_key(self, channel, deserializer) {
	const $bp = resolve_key(self, channel, deserializer);
	let $bq = null;
	if ($bp[0] === 1) {
		$bq = undefined;
	} else {
		const resolved = $bp[1];
		$bq = open_forward(self, channel, [ 0, __clone(resolved[0]) ], resolved[1]);
	}
	return $bq;
}
function resolve_key(self, channel, deserializer) {
	const $bj = capability_of(self, channel);
	let $bk = null;
	if ($bj[0] === 1) {
		$bk = [ 1 ];
	} else {
		const capability = $bj[1];
		const $bl = capability[1];
		let $bm = null;
		if ($bl[0] === 1) {
			$bm = [ 1 ];
		} else {
			const resolve = $bl[1];
			const resolved = resolve(deserializer);
			const $bn = deserializer[17]();
			let $bo = null;
			if ($bn[0] === 0) {
				const _reason = $bn[1];
				$bo = [ 1 ];
			} else {
				$bo = [ 0, resolved ];
			}
			$bm = $bo;
		}
		$bk = $bm;
	}
	return $bk;
}
function release_demand(self, channel, $aN) {
	release_hold(self, channel, [ 1 ], $aN);
}
function release_hold(self, channel, key, $aO) {
	const drained = close_forward(self, channel, key, $aO);
	if (drained && dynamic_channel(self, channel)) {
		revoke(self, channel, $aO);
	}
}
function dynamic_channel(self, channel) {
	const $bc = capability_of(self, channel);
	let $bd = null;
	if ($bc[0] === 0) {
		const capability = $bc[1];
		$bd = capability[2];
	} else {
		$bd = false;
	}
	return $bd;
}
function stop_key(self, channel, deserializer, $br) {
	const $bs = resolve_key(self, channel, deserializer);
	let $bt = null;
	if ($bs[0] === 1) {
		$bt = undefined;
	} else {
		const resolved = $bs[1];
		$bt = release_hold(self, channel, [ 0, __clone(resolved[0]) ], $br);
	}
	return $bt;
}
function revoke(self, channel, $be) {
	let kept = [  ];
	for (const forward of self[3].v) {
		if (forward[0] === channel) {
			dispose2(forward[2], $be);
		} else {
			kept.push(__clone(forward));
		}
	}
	self[3].v = kept;
	let remaining = [  ];
	for (const entry of self[2].v) {
		const $bf = entry;
		const id = $bf[0];
		const capability = $bf[1];
		if (id !== channel) {
			remaining.push([ id, __clone(capability) ]);
		}
	}
	self[2].v = remaining;
}
function receive(self, frame, $aw) {
	const deserializer = self[1][1](frame);
	const tag = deserializer[5]();
	deserializer[6](tag, 2);
	const channel = deserializer[11]();
	const $ax = deserializer[17]();
	let $ay = null;
	if ($ax[0] === 0) {
		const _reason = $ax[1];
		$ay = undefined;
	} else {
		let $bg = null;
		if (deserializer[8]()) {
			deserializer[9]();
			const $az = tag;
			let $aA = null;
			if ($az === "Subscribe") {
				$aA = start2(self, channel);
			} else if ($az === "Unsubscribe") {
				$aA = release_demand(self, channel, $aw);
			} else {
				$aA = undefined;
			}
			$bg = $aA;
		} else {
			const $bh = tag;
			let $bi = null;
			if ($bh === "Subscribe") {
				$bi = start_key(self, channel, deserializer);
			} else if ($bh === "Unsubscribe") {
				$bi = stop_key(self, channel, deserializer, $aw);
			} else {
				$bi = undefined;
			}
			$bg = $bi;
		}
		$ay = $bg;
	}
	return $ay;
}
function dispose(self, $bA) {
	for (const forward of self[3].v) {
		dispose2(forward[2], $bA);
	}
	self[3].v = [  ];
	self[2].v = [  ];
	clear_on_frame(self[0]);
}
function fresh_id() {
	const id = next_subscriber_id.v;
	next_subscriber_id.v = id + 1;
	return id;
}
function new7() {
	return [ __shared_new([  ]), __shared_new(new Map()), __shared_new(false), __shared_new(false), __shared_new(false) ];
}
function drain(turn) {
	if (!(turn[2].v)) {
		turn[2].v = true;
		draining_turns.v.push(__clone(turn));
		__with_finally(() => {
			let budget = 100000;
			while (!($p(turn[0].v)) && budget > 0) {
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
function dispose2(self, $aQ) {
	self[2].v = false;
	const $aR = [ 0, self[0] ];
	let $aS = null;
	if ($aR[0] === 0) {
		const subscribers = $aR[1];
		let kept = [  ];
		for (const subscriber of subscribers.v) {
			if (subscriber[0] !== self[1]) {
				kept.push(__clone(subscriber));
			}
		}
		subscribers.v = kept;
		$aS = undefined;
	} else {
		$aS = undefined;
	}
	$aS;
	const $aT = $aQ;
	let $aU = null;
	if ($aT[0] === 0) {
		const established = $aT[1];
		$aU = [ 0, established ];
	} else {
		$aU = $aV(draining_turns.v);
	}
	const ambient = $aU;
	const $aW = ambient;
	let $aX = null;
	if ($aW[0] === 0) {
		const turn = $aW[1];
		let kept_pending = [  ];
		for (const subscriber2 of turn[0].v) {
			if (subscriber2[0] !== self[1]) {
				kept_pending.push(__clone(subscriber2));
			}
		}
		turn[0].v = kept_pending;
		turn[1].v.delete(hash(self[1]));
		$aX = undefined;
	} else {
		$aX = undefined;
	}
	$aX;
	const $aY = self[3].v;
	let $aZ = null;
	if ($aY[0] === 0) {
		const release = $aY[1];
		self[3].v = [ 1 ];
		releasing_turns.v.push(ambient);
		__with_finally(release, () => {
			__list_pop(releasing_turns.v);
			return;
		});
		$aZ = undefined;
	} else {
		$aZ = undefined;
	}
	return $aZ;
}
function ws_accept_key(key) {
	return createHash("sha1").update(key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11").digest("base64");
}
function anonymous() {
	return [ "", "" ];
}
function of(identity) {
	return [ identity, "" ];
}
function header_text(headers, name) {
	let $dQ = null;
	if (Object.hasOwn(headers, name)) {
		const value2 = headers[name];
		if (__json_kind(value2) === "string") {
			return [ 0, String(value2) ];
		}
		$dQ = undefined;
	}
	$dQ;
	return [ 1 ];
}
function token(self) {
	for (const offered of self[2]) {
		if (offered.startsWith("token.")) {
			return [ 0, __substring(offered, 6, offered.length) ];
		}
	}
	return [ 1 ];
}
function reject_status(reject) {
	const $ei = reject;
	let $ej = null;
	if ($ei[0] === 0) {
		$ej = "401 Unauthorized";
	} else if ($ei[0] === 1) {
		$ej = "403 Forbidden";
	} else if ($ei[0] === 2) {
		$ej = "429 Too Many Requests";
	} else {
		$ej = "503 Service Unavailable";
	}
	return $ej;
}
function reject_announcement(reject) {
	return "__reject:" + reject_code(reject);
}
function reject_code(reject) {
	const $eg = reject;
	let $eh = null;
	if ($eg[0] === 0) {
		$eh = "401";
	} else if ($eg[0] === 1) {
		$eh = "403";
	} else if ($eg[0] === 2) {
		$eh = "429";
	} else {
		$eh = "503";
	}
	return $eh;
}
function tells_the_client(reject) {
	const $dZ = reject;
	let $ea = null;
	if ($dZ[0] === 0) {
		$ea = true;
	} else if ($dZ[0] === 1) {
		$ea = true;
	} else if ($dZ[0] === 3) {
		$ea = true;
	} else {
		$ea = false;
	}
	return $ea;
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
	const key = $ec(from_json_value(headers["sec-websocket-key"]), "");
	const selected = selected_protocol(offered_protocols(headers));
	let $ef = null;
	if (selected === "") {
		$ef = "";
	} else {
		$ef = "\r\nSec-WebSocket-Protocol: " + selected;
	}
	const echo4 = $ef;
	socket.write("HTTP/1.1 101 Switching Protocols\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Accept: " + ws_accept_key(key) + echo4 + "\r\n\r\n");
}
function offered_protocols(headers) {
	let offered = [  ];
	const $dX = header_text(headers, "sec-websocket-protocol");
	let $dY = null;
	if ($dX[0] === 0) {
		const raw = $dX[1];
		for (const part of raw.split(",")) {
			const name = part.trim();
			if (name.length > 0) {
				offered.push(name);
			}
		}
		$dY = undefined;
	} else {
		$dY = undefined;
	}
	$dY;
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
function new8(protocol, $as) {
	return [ (connection) => {
		return for_connection(__clone(protocol), connection[0]);
	}, [ 0, __clone(protocol) ], __clone(protocol[0]), "/", (connection, wire) => {
		return register_session(connection, wire, protocol[0], $as);
	}, (connection) => {
		return drop_session(connection, $as);
	}, [ 1 ], __shared_new(0), 0, 0, 10000.0, __shared_new([  ]), 0, 0, false ];
}
function at(self, prefix) {
	self[3] = prefix;
	return self;
}
function authorize(self, check) {
	self[6] = [ 0, check ];
	return self;
}
function admit_handshake(service, remote) {
	const cutoff = Date.now() - service[10];
	let kept = [  ];
	let seen = 0;
	for (const entry of service[11].v) {
		const $dT = entry;
		const address = $dT[0];
		const at2 = $dT[1];
		let $dU = null;
		if (at2 > cutoff) {
			kept.push([ address, at2 ]);
			if (address === remote) {
				seen = seen + 1;
			}
			$dU = undefined;
		}
		$dU;
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
	const $dR = header_text(request.headers, "x-forwarded-for");
	let $dS = null;
	if ($dR[0] === 0) {
		const raw = $dR[1];
		for (const part of raw.split(",")) {
			const candidate = part.trim();
			if (candidate.length > 0) {
				return candidate;
			}
		}
		$dS = peer;
	} else {
		$dS = peer;
	}
	return $dS;
}
async function gate_upgrade(service, request, socket) {
	const remote = client_address(service, request, socket);
	if (service[8] > 0 && service[7].v >= service[8]) {
		return [ 1, [ 2 ] ];
	}
	if (service[9] > 0 && !(admit_handshake(service, remote))) {
		return [ 1, [ 2 ] ];
	}
	const $dV = service[6];
	let $dW = null;
	if ($dV[0] === 1) {
		$dW = [ 0, anonymous() ];
	} else {
		const check = $dV[1];
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
		$dW = outcome;
	}
	return $dW;
}
function with_service(self, service) {
	self[5].push(__clone(service));
	return self;
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
		let $cV = null;
		if (a[3].length > b[3].length) {
			$cV = -1;
		} else if (a[3].length < b[3].length) {
			$cV = 1;
		} else {
			$cV = 0;
		}
		return $cV;
	});
}
function events_response(service) {
	const id = fresh_connection();
	const on_connect = service[4];
	const on_disconnect = service[5];
	return build(streaming(set_header(set_header(builder(), "Content-Type", "text/event-stream"), "Cache-Control", "no-cache"), (stream) => {
		send2(stream, "data: __conn:" + id + "\n" + "\n");
		const $dm = duplex_pair();
		const app_end = $dm[0];
		const wire_end = $dm[1];
		on_frame(wire_end, (frame) => {
			const $dn = frame;
			let $do = null;
			if ($dn[0] === 0) {
				const body3 = $dn[1];
				$do = send2(stream, "data: " + body3 + "\n" + "\n");
			} else {
				const _bytes = $dn[1];
				$do = undefined;
			}
			return $do;
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
function send_response(request, $ds) {
	const content = body(request);
	const target = $dt(__parse_i32(connection_id_of(path(request))), __lazy("fallback", () => {
		return 0 - 1;
	}));
	for (const entry of connections.v) {
		const $dw = entry;
		const id = $dw[0];
		const wire = $dw[1];
		if (id === target) {
			$bu(($dx) => {
				send3(wire, [ 0, content ]);
				return;
			}, $ds);
		}
	}
	return build(body2(code(builder(), 204), ""));
}
async function rpc_frame_response(service, request) {
	const $dz = service[1];
	let $dA = null;
	if ($dz[0] === 0) {
		const protocol = $dz[1];
		const reply = await ($B([ 0 ], async ($dB) => {
			return await (respond(protocol, [ 1, bytes(request) ]));
		}));
		const $dF = reply;
		let $dG = null;
		if ($dF[0] === 0) {
			const frame = $dF[1];
			$dG = build(body2(set_header(builder(), "Content-Type", "application/json"), frame));
		} else {
			const frame2 = $dF[1];
			$dG = build(body_bytes(set_header(builder(), "Content-Type", "application/octet-stream"), frame2));
		}
		$dA = $dG;
	} else {
		$dA = build(body2(code(builder(), 501), "this service builds one instance per connection (Service::factory), and a POST rpc frame carries no connection to build for \u{2014} connect over the WebSocket transport instead"));
	}
	return $dA;
}
function unauthorized_response(service, route) {
	let $dk = null;
	if (route === "rpc") {
		const envelope2 = encode_reply(service[2], [ 1, [ 4 ] ]);
		const $di = envelope2;
		let $dj = null;
		if ($di[0] === 0) {
			const frame = $di[1];
			$dj = build(body2(set_header(code(builder(), 401), "Content-Type", "application/json"), frame));
		} else {
			const frame2 = $di[1];
			$dj = build(body_bytes(set_header(code(builder(), 401), "Content-Type", "application/octet-stream"), frame2));
		}
		$dk = $dj;
	} else {
		$dk = build(body2(code(builder(), 401), "this service authorizes its connections at the WebSocket upgrade, and the SSE/POST legs carry no handshake to authorize \u{2014} connect over the WebSocket transport instead"));
	}
	return $dk;
}
async function service_response(service, request, $cZ) {
	const path2 = path(request);
	const gated = $da(service[6]);
	let $dq = null;
	if (path_matches_route(path2, service[3] + "events")) {
		let $dl = null;
		if (gated) {
			$dl = [ 0, unauthorized_response(service, "events") ];
		} else {
			$dl = [ 0, events_response(service) ];
		}
		$dq = $dl;
	} else if (path_matches_route(path2, service[3] + "send")) {
		let $dr = null;
		if (gated) {
			$dr = [ 0, unauthorized_response(service, "send") ];
		} else {
			$dr = [ 0, send_response(request, $cZ) ];
		}
		$dq = $dr;
	} else if (path_matches_route(path2, service[3] + "rpc")) {
		let $dy = null;
		if (gated) {
			$dy = [ 0, unauthorized_response(service, "rpc") ];
		} else {
			$dy = [ 0, await (rpc_frame_response(service, request)) ];
		}
		$dq = $dy;
	} else {
		$dq = [ 1 ];
	}
	return $dq;
}
async function services_answer(services, request, $cW) {
	let answer = [ 1 ];
	for (const service of services) {
		if ($cX(answer)) {
			answer = await (service_response(service, request, $cW));
		}
	}
	return answer;
}
function fold_service_requests(services, fallback, $cU) {
	const sorted = services_by_mount(services);
	return async (request) => {
		const $dH = await (services_answer(sorted, request, $cU));
		let $dI = null;
		if ($dH[0] === 0) {
			const response = $dH[1];
			$dI = response;
		} else {
			$dI = await (fallback(request));
		}
		return $dI;
	};
}
function service_for_upgrade(services, request) {
	const path2 = request.url;
	let answer = [ 1 ];
	for (const service of services) {
		if ($cX(answer) && path_matches_route(path2, service[3])) {
			answer = [ 0, __clone(service) ];
		}
	}
	return answer;
}
function fold_service_upgrades(services, fallback, $dJ) {
	let $dK = null;
	if (services.length === 0) {
		$dK = fallback;
	} else {
		const sorted = services_by_mount(services);
		$dK = [ 0, async (request, socket, head) => {
			const $dN = service_for_upgrade(sorted, request);
			let $dO = null;
			if ($dN[0] === 0) {
				const service = $dN[1];
				const $ek = await (gate_upgrade(service, request, socket));
				let $el = null;
				if ($ek[0] === 0) {
					const session = $ek[1];
					$el = accept_socket(request, socket, head, service, session, $dJ);
				} else {
					const reject = $ek[1];
					$el = refuse_upgrade(request, socket, reject);
				}
				$dO = $el;
			} else {
				const $eN = fallback;
				let $eO = null;
				if ($eN[0] === 0) {
					const handler = $eN[1];
					$eO = handler(request, socket, head);
				} else {
					$eO = socket.destroy();
				}
				$dO = $eO;
			}
			return $dO;
		} ];
	}
	return $dK;
}
function accept_socket(request, socket, head, service, session, $em) {
	const headers = request.headers;
	if (!(Object.hasOwn(headers, "sec-websocket-key"))) {
		socket.destroy();
		return;
	}
	write_upgrade_101(socket, headers);
	const id = fresh_connection();
	register_client_channel(id, service[2], (frame) => {
		const $en = frame;
		let $eo = null;
		if ($en[0] === 0) {
			const body3 = $en[1];
			$eo = socket.write(text_frame("s:0:" + body3));
		} else {
			const bytes2 = $en[1];
			$eo = socket.write(binary_frame(tag_client_bytes(0, bytes2)));
		}
		return $eo;
	});
	const protocol = service[0]([ id, __clone(session), client_address(service, request, socket) ]);
	service[7].v = service[7].v + 1;
	const on_connect = service[4];
	const on_disconnect = service[5];
	const $ep = duplex_pair();
	const app_end = $ep[0];
	const wire_end = $ep[1];
	on_frame(wire_end, (frame) => {
		const $eq = frame;
		let $er = null;
		if ($eq[0] === 0) {
			const body3 = $eq[1];
			$er = socket.write(text_frame("d:" + body3));
		} else {
			const bytes2 = $eq[1];
			$er = socket.write(binary_frame(tag_duplex_bytes(bytes2)));
		}
		return $er;
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
	const parser = new9();
	const receive2 = (chunk) => {
		let $et = null;
		if (!(greeted)) {
			greeted = true;
			if (service[12] > 0) {
				socket.setTimeout(0);
			}
			$et = undefined;
		}
		$et;
		for (const event of feed(parser, chunk)) {
			const $eC = event;
			let $eD = null;
			if ($eC[0] === 0) {
				const frame = $eC[1];
				let $eH = null;
				if (frame.startsWith("r:")) {
					const rest = __substring(frame, 2, frame.length);
					const parts = rest.split(":");
					const id_text = __at(parts, 0);
					if (id_text.length < rest.length) {
						const payload = __substring(rest, id_text.length + 1, rest.length);
						__task(async () => {
							const reply = await ($B([ 0 ], async ($eE) => {
								return await (respond(protocol, [ 0, payload ]));
							}));
							const $eF = reply;
							let $eG = null;
							if ($eF[0] === 0) {
								const answer = $eF[1];
								socket.write(text_frame("r:" + id_text + ":" + answer));
								$eG = undefined;
							} else {
								const bytes3 = $eF[1];
								const id3 = $dt(__parse_i32(id_text), __lazy("fallback", () => {
									return 0 - 1;
								}));
								socket.write(binary_frame(tag_rpc_bytes(id3, bytes3)));
								$eG = undefined;
							}
							return $eG;
						}, "accept_socket");
					}
					$eH = undefined;
				} else if (frame.startsWith("d:")) {
					$bu(($eI) => {
						send3(wire_end, [ 0, __substring(frame, 2, frame.length) ]);
						return;
					}, $em);
				}
				$eD = $eH;
			} else if ($eC[0] === 2) {
				const payload2 = $eC[1];
				$eD = socket.write(pong_frame(payload2));
			} else if ($eC[0] === 3) {
				socket.write(close_frame());
				socket.destroy();
				$eD = undefined;
			} else {
				const bytes2 = $eC[1];
				if (bytes2.length > 0 && bytes2.at(0) === 0x64) {
					$bu(($eJ) => {
						send3(wire_end, [ 1, bytes2.slice(1, bytes2.length) ]);
						return;
					}, $em);
				} else if (bytes2.length >= 5 && bytes2.at(0) === 0x72) {
					const id2 = bytes2.at(1) | bytes2.at(2) << 8 | bytes2.at(3) << 16 | bytes2.at(4) << 24;
					const payload3 = bytes2.slice(5, bytes2.length);
					__task(async () => {
						const reply = await ($B([ 0 ], async ($eK) => {
							return await (respond(protocol, [ 1, __clone(payload3) ]));
						}));
						const $eL = reply;
						let $eM = null;
						if ($eL[0] === 1) {
							const answer = $eL[1];
							socket.write(binary_frame(tag_rpc_bytes(id2, answer)));
							$eM = undefined;
						} else {
							const answer2 = $eL[1];
							socket.write(text_frame("r:" + id2 + ":" + answer2));
							$eM = undefined;
						}
						return $eM;
					}, "accept_socket");
				}
				$eD = undefined;
			}
			$eD;
		}
		return;
	};
	if (head.length > 0) {
		receive2(head);
	}
	socket.on("data", receive2);
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
		const $dp = entry;
		const id = $dp[0];
		const wire = $dp[1];
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
function ambient_signal($cy) {
	const $cz = $cy;
	let $cA = null;
	if ($cz[0] === 0) {
		const n = $cz[1];
		$cA = [ 0, n.signal_of() ];
	} else {
		$cA = [ 1 ];
	}
	return $cA;
}
function is_watching() {
	const $cI = __env("VILAN_WATCHING");
	let $cJ = null;
	if ($cI[0] === 0) {
		const value2 = $cI[1];
		$cJ = value2 === "1";
	} else {
		$cJ = false;
	}
	return $cJ;
}
function begin_struct3(self, fields) {
	self[0](fields);
}
function field3(self, name) {
	self[1](name);
}
function end_struct3(self) {
	self[2]();
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
function bool_value3(self, value2) {
	self[14](value2);
}
function str_value4(self) {
	return self[10]();
}
function i32_value4(self) {
	return self[11]();
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
function new9() {
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
		let $eB = null;
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
			let $eu = null;
			if (length === 126) {
				if (available < 4) {
					valid = false;
					scanning = false;
				} else {
					length = buffer2.at(2) << 8 | buffer2.at(3);
					header3 = 4;
				}
				$eu = undefined;
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
				$eu = undefined;
			}
			$eu;
			let $eA = null;
			if (valid) {
				const mask_at = header3;
				let $ev = null;
				if (masked) {
					$ev = header3 + 4 + length;
				} else {
					$ev = header3 + length;
				}
				const total = $ev;
				let $ez = null;
				if (available < total) {
					scanning = false;
				} else {
					let $ew = null;
					if (masked) {
						$ew = mask_at + 4;
					} else {
						$ew = mask_at;
					}
					const payload_at = $ew;
					const payload = buffer2.slice(payload_at, payload_at + length);
					let $ex = null;
					if (masked) {
						let index = 0;
						while (index < length) {
							set(payload, index, payload.at(index) ^ buffer2.at(mask_at + (index & 3)));
							index = index + 1;
						}
						$ex = undefined;
					}
					$ex;
					self[0].v = buffer2.slice(total, available);
					for (const event of dispatch(self, fin, opcode, payload)) {
						events.push(event);
					}
					if (self[3].v) {
						return events;
					}
					$ez = undefined;
				}
				$eA = $ez;
			}
			$eB = $eA;
		}
		$eB;
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
	let $ey = null;
	if (opcode === 0x1) {
		$ey = [ 0, decode_utf8(payload) ];
	} else {
		$ey = [ 1, __clone(payload) ];
	}
	return $ey;
}
function login(self, username, password) {
	let $h = null;
	if (password === "hunter2") {
		$h = [ 0, [ "tok-" + username, username ] ];
	} else {
		$h = [ 1, "wrong password" ];
	}
	return $h;
}
function echo(self, value2) {
	return value2 + self[0];
}
function touch(self, label) {
	console.log("  [server] touch(" + label + ")");
}
function plain_too(self) {
	return 1;
}
function watch(self) {
	return __clone(self[0]);
}
function echo2(self, value2) {
	return value2;
}
function echo3(self, value2) {
	return value2;
}
function envelope(method2, args) {
	const quote = "\"";
	return "{" + quote + "method" + quote + ":" + quote + method2 + quote + "," + quote + "args" + quote + ":" + args + "}";
}
async function show(label, url, body3, $cv) {
	const response = await (send(header(post(url, body3), "Content-Type", "application/json"), $cv));
	const text2 = await (response.text());
	console.log("" + label + ": status=" + response.status + " body=" + text2);
}
function dispatcher(self) {
	self = __clone(self);
	return on(on(on(on(on(new5(), "login", (__request) => {
		return $o([ 0 ], ($c) => {
			const username = $d(__request, 0);
			const password = $d(__request, 1);
			const $f = decode_failed(__request);
			let $g = null;
			if ($f[0] === 0) {
				const reason = $f[1];
				$g = [ 1, [ 1, reason ] ];
			} else {
				$g = $i(login(self, username, password));
			}
			return $g;
		});
	}), "echo", (__request) => {
		return $o([ 0 ], ($q) => {
			const value2 = $r(__request, 0);
			const $t = decode_failed(__request);
			let $u = null;
			if ($t[0] === 0) {
				const reason = $t[1];
				$u = [ 1, [ 1, reason ] ];
			} else {
				$u = $v(echo(self, value2));
			}
			return $u;
		});
	}), "touch", async (__request) => {
		return await ($B([ 0 ], async ($x) => {
			const label = $d(__request, 0);
			const $y = decode_failed(__request);
			let $z = null;
			if ($y[0] === 0) {
				const reason = $y[1];
				$z = [ 1, [ 1, reason ] ];
			} else {
				$z = await (notified(() => {
					return touch(self, label);
				}));
			}
			return $z;
		}));
	}), "__contract", (_) => {
		return $C(contract_hash(self));
	}), "__attach", (__request) => {
		return $o([ 0 ], ($D) => {
			const connection = $r(__request, 0);
			const $E = decode_failed(__request);
			let $F = null;
			if ($E[0] === 0) {
				const reason = $E[1];
				$F = [ 1, [ 1, reason ] ];
			} else {
				const $H = session_of(connection);
				let $I = null;
				if ($H[0] === 0) {
					const session = $H[1];
					const channels = [  ];
					$I = $J(channels);
				} else {
					$I = [ 1, [ 2, "unknown connection" ] ];
				}
				$F = $I;
			}
			return $F;
		});
	});
}
function contract_hash(self) {
	return "d82b084e";
}
function dispatcher2(self) {
	self = __clone(self);
	return on(on(on(on(handles(new5(), [ "watch" ]), "plain_too", (__request) => {
		return $o([ 0 ], ($bB) => {
			return $v(plain_too(self));
		});
	}), "watch", (__request) => {
		return $o([ 0 ], ($bC) => {
			return $bD(__request, watch(self));
		});
	}), "__contract", (_) => {
		return $C(contract_hash2(self));
	}), "__attach", (__request) => {
		return $o([ 0 ], ($bW) => {
			const connection = $r(__request, 0);
			const $bX = decode_failed(__request);
			let $bY = null;
			if ($bX[0] === 0) {
				const reason = $bX[1];
				$bY = [ 1, [ 1, reason ] ];
			} else {
				const $bZ = session_of(connection);
				let $ca = null;
				if ($bZ[0] === 0) {
					const session = $bZ[1];
					const channels = [  ];
					$ca = $J(channels);
				} else {
					$ca = [ 1, [ 2, "unknown connection" ] ];
				}
				$bY = $ca;
			}
			return $bY;
		});
	});
}
function contract_hash2(self) {
	return "69929f86";
}
function dispatcher3(self) {
	self = __clone(self);
	return on(on(on(new5(), "echo", (__request) => {
		return $o([ 0 ], ($cb) => {
			const value2 = $r(__request, 0);
			const $cc = decode_failed(__request);
			let $cd = null;
			if ($cc[0] === 0) {
				const reason = $cc[1];
				$cd = [ 1, [ 1, reason ] ];
			} else {
				$cd = $v(echo2(self, value2));
			}
			return $cd;
		});
	}), "__contract", (_) => {
		return $C(contract_hash3(self));
	}), "__attach", (__request) => {
		return $o([ 0 ], ($ce) => {
			const connection = $r(__request, 0);
			const $cf = decode_failed(__request);
			let $cg = null;
			if ($cf[0] === 0) {
				const reason = $cf[1];
				$cg = [ 1, [ 1, reason ] ];
			} else {
				const $ch = session_of(connection);
				let $ci = null;
				if ($ch[0] === 0) {
					const session = $ch[1];
					const channels = [  ];
					$ci = $J(channels);
				} else {
					$ci = [ 1, [ 2, "unknown connection" ] ];
				}
				$cg = $ci;
			}
			return $cg;
		});
	});
}
function contract_hash3(self) {
	return "730dc56d";
}
function dispatcher4(self) {
	self = __clone(self);
	return on(on(on(new5(), "echo", (__request) => {
		return $o([ 0 ], ($cn) => {
			const value2 = $r(__request, 0);
			const $co = decode_failed(__request);
			let $cp = null;
			if ($co[0] === 0) {
				const reason = $co[1];
				$cp = [ 1, [ 1, reason ] ];
			} else {
				$cp = $v(echo3(self, value2));
			}
			return $cp;
		});
	}), "__contract", (_) => {
		return $C(contract_hash4(self));
	}), "__attach", (__request) => {
		return $o([ 0 ], ($cq) => {
			const connection = $r(__request, 0);
			const $cr = decode_failed(__request);
			let $cs = null;
			if ($cr[0] === 0) {
				const reason = $cr[1];
				$cs = [ 1, [ 1, reason ] ];
			} else {
				const $ct = session_of(connection);
				let $cu = null;
				if ($ct[0] === 0) {
					const session = $ct[1];
					const channels = [  ];
					$cu = $J(channels);
				} else {
					$cu = [ 1, [ 2, "unknown connection" ] ];
				}
				$cs = $cu;
			}
			return $cs;
		});
	});
}
function contract_hash4(self) {
	return "730dc56d";
}
function dispatcher_for(self) {
	return dispatcher4(self);
}
function $b(value2) {
	let subscribers = [  ];
	return [ __shared_new(value2), __shared_new(subscribers) ];
}
function $a(value2) {
	return $b(value2);
}
function $e(deserializer) {
	return str_value4(deserializer);
}
function $d(request, index) {
	let deserializer = __clone(request[1]);
	return $e(deserializer);
}
function $n(self, serializer) {
	str_value3(serializer, self);
}
function $m(self, serializer) {
	begin_struct3(serializer, 2);
	field3(serializer, "token");
	$n(self[0], serializer);
	field3(serializer, "user");
	$n(self[1], serializer);
	end_struct3(serializer);
}
function $j(self, serializer) {
	const $k = self;
	let $l = null;
	if ($k[0] === 0) {
		const value2 = $k[1];
		begin_variant3(serializer, "Ok", 1);
		$m(value2, serializer);
		end_variant3(serializer);
		$l = undefined;
	} else {
		const error = $k[1];
		begin_variant3(serializer, "Err", 1);
		$n(error, serializer);
		end_variant3(serializer);
		$l = undefined;
	}
	return $l;
}
function $i(value2) {
	return [ 0, (serializer) => {
		serializer = __clone(serializer);
		return $j(value2, serializer);
	} ];
}
function $p(self) {
	return self.length === 0;
}
function $o(policy, body3) {
	const fresh = new7();
	const result2 = body3(fresh);
	drain(fresh);
	fresh[3].v = true;
	return result2;
}
function $s(deserializer) {
	return i32_value4(deserializer);
}
function $r(request, index) {
	let deserializer = __clone(request[1]);
	return $s(deserializer);
}
function $w(self, serializer) {
	i32_value3(serializer, self);
}
function $v(value2) {
	return [ 0, (serializer) => {
		serializer = __clone(serializer);
		return $w(value2, serializer);
	} ];
}
function $A(self, serializer) {
	bool_value3(serializer, self);
}
async function $B(policy, body3) {
	const fresh = new7();
	const result2 = await (body3(fresh));
	drain(fresh);
	fresh[3].v = true;
	return result2;
}
function $C(value2) {
	return [ 0, (serializer) => {
		serializer = __clone(serializer);
		return $n(value2, serializer);
	} ];
}
function $K(self, serializer) {
	begin_list3(serializer, self.length);
	for (const element of self) {
		$w(element, serializer);
	}
	end_list3(serializer);
}
function $J(value2) {
	return [ 0, (serializer) => {
		serializer = __clone(serializer);
		return $K(value2, serializer);
	} ];
}
function $ao(self, predicate) {
	let result2 = [  ];
	for (const item of self) {
		if (predicate(item)) {
			result2.push(__clone(item));
		}
	}
	return result2;
}
function $ap(self) {
	return __list_get(self, 0);
}
function $aV(self) {
	return __list_get(self, self.length - 1);
}
function $bu(body3, $bv) {
	const $bw = $bv;
	let $bx = null;
	if ($bw[0] === 0) {
		const current = $bw[1];
		$bx = body3(current);
	} else {
		const fresh = new7();
		const result2 = body3(fresh);
		drain(fresh);
		fresh[3].v = true;
		$bx = result2;
	}
	return $bx;
}
function $bH(cell) {
	return __shared_identity(cell[0]);
}
function $bS(signal, observer) {
	const id = fresh_id();
	const cell = signal[0];
	const live = __shared_new(true);
	signal[1].v.push([ id, () => {
		const $bT = [ 0, cell ];
		let $bU = null;
		if ($bT[0] === 0) {
			const live2 = $bT[1];
			$bU = observer(live2.v);
		} else {
			$bU = undefined;
		}
		return $bU;
	}, live ]);
	return [ signal[1], id, live, __shared_new([ 1 ]) ];
}
function $bV(self) {
	return __clone(self[0].v);
}
function $bR(self, observer) {
	const subscription = $bS(self, observer);
	observer($bV(self));
	return subscription;
}
function $bG(self, source) {
	const $bM = dynamic_channel_for(self, $bH(source), false);
	let $bN = null;
	if ($bM[0] === 0) {
		const held = $bM[1];
		$bN = held;
	} else {
		const channel = fresh_channel();
		const transport = __clone(self[0]);
		const codec = __clone(self[1]);
		const starter = () => {
			return $bR(source, (value2) => {
				send3(transport, encode_update(codec, channel, (serializer) => {
					serializer = __clone(serializer);
					$w(value2, serializer);
					return;
				}));
				return;
			});
		};
		self[2].v.push([ channel, [ starter, [ 1 ], true, $bH(source) ] ]);
		$bN = channel;
	}
	return $bN;
}
function $bD(request, source) {
	const $bE = session_of(request[3]);
	let $bF = null;
	if ($bE[0] === 0) {
		const session = $bE[1];
		$bF = $v($bG(session, source));
	} else {
		$bF = no_connection_for_handle(request);
	}
	return $bF;
}
function $cl(build3, codec, $cm) {
	return [ (connection) => {
		return for_connection(into_protocol(dispatcher_for(build3(connection)), codec), connection[0]);
	}, [ 1 ], __clone(codec), "/", (connection, wire) => {
		return register_session(connection, wire, codec, $cm);
	}, (connection) => {
		return drop_session(connection, $cm);
	}, [ 1 ], __shared_new(0), 0, 0, 10000.0, __shared_new([  ]), 0, 0, false ];
}
function $cX(self) {
	const $cY = self;
	return $cY[0] === 1;
}
function $da(self) {
	const $db = self;
	return $db[0] === 0;
}
function $df(self, serializer) {
	const $dg = self;
	let $dh = null;
	if ($dg[0] === 0) {
		const p0 = $dg[1];
		begin_variant3(serializer, "Transport", 1);
		$n(p0, serializer);
		end_variant3(serializer);
		$dh = undefined;
	} else if ($dg[0] === 1) {
		const p02 = $dg[1];
		begin_variant3(serializer, "Decode", 1);
		$n(p02, serializer);
		end_variant3(serializer);
		$dh = undefined;
	} else if ($dg[0] === 2) {
		const p03 = $dg[1];
		begin_variant3(serializer, "Remote", 1);
		$n(p03, serializer);
		end_variant3(serializer);
		$dh = undefined;
	} else if ($dg[0] === 3) {
		const p04 = $dg[1];
		begin_variant3(serializer, "Contract", 1);
		$n(p04, serializer);
		end_variant3(serializer);
		$dh = undefined;
	} else if ($dg[0] === 4) {
		begin_variant3(serializer, "Unauthorized", 0);
		end_variant3(serializer);
		$dh = undefined;
	} else {
		begin_variant3(serializer, "Unavailable", 0);
		end_variant3(serializer);
		$dh = undefined;
	}
	return $dh;
}
function $dt(self, fallback) {
	const $du = self;
	let $dv = null;
	if ($du[0] === 0) {
		const x = __clone($du[1]);
		$dv = x;
	} else {
		$dv = __clone(__force(fallback));
	}
	return $dv;
}
function $ec(self, fallback) {
	const $ed = self;
	let $ee = null;
	if ($ed[0] === 0) {
		const x = __clone($ed[1]);
		$ee = x;
	} else {
		$ee = __clone(fallback);
	}
	return $ee;
}
const reactive_sessions = __shared_new([  ]);
const client_channels = __shared_new([  ]);
const next_channel = __shared_new(0);
const next_subscriber_id = __shared_new(0);
const draining_turns = __shared_new([  ]);
const releasing_turns = __shared_new([  ]);
const connections = __shared_new([  ]);
const next_connection = __shared_new(0);
(async () => {
	const plain = [ 100 ];
	const handled = [ $a(7) ];
	const gated = [ 0 ];
	start(build2(on_start(on_request(with_service(with_service(with_service(with_service(port(builder2(), 59777), at(new8(into_protocol(dispatcher(plain), json_codec()), [ 1 ]), "/plain/")), at(new8(into_protocol(dispatcher2(handled), json_codec()), [ 1 ]), "/handle/")), authorize(at(new8(into_protocol(dispatcher3(gated), json_codec()), [ 1 ]), "/gated/"), (handshake) => {
		const $cj = token(handshake);
		let $ck = null;
		if ($cj[0] === 0) {
			const found = $cj[1];
			$ck = [ 0, of(found) ];
		} else {
			$ck = [ 1, [ 0 ] ];
		}
		return $ck;
	})), at($cl((connection) => {
		return [ "x" ];
	}, json_codec(), [ 1 ]), "/perconn/")), (request) => {
		return build(body2(code(builder(), 404), "nope path=" + path(request) + " method=" + method(request)));
	}), async (server) => {
		const base = "http://localhost:59777";
		console.log("base=" + base);
		console.log("--- 1. a plain method over POST");
		await (show("echo(7)", base + "/plain/rpc", envelope("echo", "[7]"), [ 1 ]));
		console.log("--- 2. a Result-returning method, both arms");
		await (show("login ok", base + "/plain/rpc", envelope("login", "[\"ada\",\"hunter2\"]"), [ 1 ]));
		await (show("login err", base + "/plain/rpc", envelope("login", "[\"ada\",\"nope\"]"), [ 1 ]));
		console.log("--- 3. the awaited void (A107) over POST");
		await (show("touch", base + "/plain/rpc", envelope("touch", "[\"from-http\"]"), [ 1 ]));
		console.log("--- 4. the contract route");
		await (show("__contract", base + "/plain/rpc", envelope("__contract", "[]"), [ 1 ]));
		console.log("--- 5. __attach over POST (the mirror handshake)");
		await (show("__attach", base + "/plain/rpc", envelope("__attach", "[0]"), [ 1 ]));
		console.log("--- 6. an unknown method");
		await (show("nosuch", base + "/plain/rpc", envelope("nosuch", "[]"), [ 1 ]));
		console.log("--- 7. a garbled body");
		await (show("garbled", base + "/plain/rpc", "not json at all", [ 1 ]));
		console.log("--- 8. wrong arity");
		await (show("echo()", base + "/plain/rpc", envelope("echo", "[]"), [ 1 ]));
		console.log("--- 9. a handle method on this leg (A78)");
		await (show("plain_too", base + "/handle/rpc", envelope("plain_too", "[]"), [ 1 ]));
		await (show("watch", base + "/handle/rpc", envelope("watch", "[]"), [ 1 ]));
		console.log("--- 10. a gated service\'s POST leg");
		await (show("gated echo", base + "/gated/rpc", envelope("echo", "[7]"), [ 1 ]));
		console.log("--- 11. a factory service\'s POST leg");
		await (show("perconn echo", base + "/perconn/rpc", envelope("echo", "[7]"), [ 1 ]));
		console.log("--- 12. GET on the rpc route, and the other two legs");
		const getr = await (send(get(base + "/plain/rpc"), [ 1 ]));
		console.log("GET /plain/rpc: status=" + getr.status + " body=" + await (getr.text()));
		const sendr = await (send(post(base + "/plain/send", "hi"), [ 1 ]));
		console.log("POST /plain/send: status=" + sendr.status + " body=" + await (sendr.text()));
		console.log("--- 13. an unmounted path");
		const miss = await (send(post(base + "/nope/rpc", envelope("echo", "[7]")), [ 1 ]));
		console.log("POST /nope/rpc: status=" + miss.status + " body=" + await (miss.text()));
		process.exit(0);
		return;
	}), [ 1 ]));
})().catch(($eU) => {
	console.error(String($eU));
	process.exit(1);
});
