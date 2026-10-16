let __vilan_stdin = null, __vilan_stdin_index = 0;
function __scan() {
	if (__vilan_stdin === null) {
		try {
			__vilan_stdin = require("fs").readFileSync(0, "utf-8").split("\n");
		} catch (error) {
			__vilan_stdin = [];
		}
	}
	return __vilan_stdin_index < __vilan_stdin.length ? __vilan_stdin[__vilan_stdin_index++] : "";
}
const first = __scan();
const second = __scan();
const third = __scan();
console.log("first=[" + first + "] second=[" + second + "] third=[" + third + "]");
//# sourceMappingURL=scan_native.mjs.map
