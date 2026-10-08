function __sleep(ms, signal) {
	const sig = signal && signal[0] === 0 ? signal[1] : undefined;
	return new Promise((resolve, reject) => {
		if (sig && sig.aborted) {
			reject(sig.reason);
			return;
		}
		const timer = setTimeout(() => resolve(), ms);
		if (sig) sig.addEventListener("abort", () => {
			clearTimeout(timer);
			reject(sig.reason);
		}, { once: true });
	});
}
async function sleep(ms, $c) {
	await (__sleep(ms, ambient_signal($c)));
}
function ambient_signal($d) {
	const $e = $d;
	let $f = null;
	if ($e[0] === 0) {
		const n = $e[1];
		$f = [ 0, n.signal_of() ];
	} else {
		$f = [ 1 ];
	}
	return $f;
}
async function leaf($b) {
	await (sleep(1, $b));
	return 1;
}
async function middle($a) {
	return await (leaf($a)) + 1;
}
(async () => {
	console.log(await (middle([ 1 ])));
})().catch(($g) => {
	console.error(String($g));
	process.exit(1);
});
