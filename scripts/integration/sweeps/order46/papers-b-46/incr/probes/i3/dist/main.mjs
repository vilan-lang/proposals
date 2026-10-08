function greet(self) {
	return "hi";
}
function use_it() {
	const foo = [ 1 ];
	return greet(foo);
}
console.log(use_it());
