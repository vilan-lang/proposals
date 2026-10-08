function assert(condition, message) {
	let $a = null;
	if (!(condition)) {
		$a = (() => {
			throw message;
		})();
	}
	return $a;
}
function check(n) {
	assert(n > 3, "n too small");
}
check(1);
