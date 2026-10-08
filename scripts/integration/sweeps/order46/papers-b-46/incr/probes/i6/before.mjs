function leaf() {
	return 1;
}
function middle() {
	return leaf() + 1;
}
console.log(middle());
