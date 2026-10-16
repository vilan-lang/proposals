function __shared_new(value) {
	return { v: value };
}
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
async function sleep(ms, $b) {
	await (__sleep(clamp_delay(ms), ambient_signal($b)));
}
function clamp_delay(ms) {
	let $c = null;
	if (ms < 0) {
		$c = 0;
	} else {
		$c = ms;
	}
	return $c;
}
async function next(self, $a) {
	if (self[0].v === 0) {
		return [ 1 ];
	}
	await (sleep(5, $a));
	self[0].v = self[0].v - 1;
	return [ 0, self[0].v ];
}
(async () => {
	const ticks = [ __shared_new(3) ];
	const $g = ticks;
	while (true) {
		const $h = await (next($g));
		if ($h[0] !== 0) {
			break;
		}
		const tick = $h[1];
		console.log("tick " + tick);
	}
	console.log("done");
})().catch(($i) => {
	console.error(String($i));
	process.exit(1);
});
//# sourceMappingURL=async_inherent_for_in.mjs.map
