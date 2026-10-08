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
function twice(n) {
	return n * 2;
}
function $a(items) {
	return __clone(__at(items, 0));
}
console.log($a([ 1, 2 ]));
console.log($a([ "a", "b" ]));
console.log(twice(3));
