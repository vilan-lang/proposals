function __at(list, index) {
	if (index >= 0 && index < list.length) return list[index];
	throw "index out of bounds: the length is " + list.length + " but the index is " + index;
}
function inner(values) {
	return __at(values, 5);
}
function outer() {
	return inner([ 1, 2 ]) + 1;
}
console.log(outer());
