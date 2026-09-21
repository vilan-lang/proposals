function debug(self) {
	const $f = self;
	let $g = null;
	if ($f[0] === 0) {
		const p0 = $f[1];
		$g = "Transport(" + JSON.stringify(p0) + ")";
	} else if ($f[0] === 1) {
		const p02 = $f[1];
		$g = "Decode(" + JSON.stringify(p02) + ")";
	} else if ($f[0] === 2) {
		const p03 = $f[1];
		$g = "Remote(" + JSON.stringify(p03) + ")";
	} else if ($f[0] === 3) {
		const p04 = $f[1];
		$g = "Contract(" + JSON.stringify(p04) + ")";
	} else if ($f[0] === 4) {
		$g = "Unauthorized";
	} else {
		$g = "Unavailable";
	}
	return $g;
}
function call_ack_shaped(ok) {
	let $a = null;
	if (ok) {
		$a = [ 0, undefined ];
	} else {
		$a = [ 1, [ 5 ] ];
	}
	return $a;
}
const $b = call_ack_shaped(true);
let $c = null;
if ($b[0] === 0) {
	const nothing = $b[1];
	$c = console.log("ack: Ok");
} else {
	const failure = $b[1];
	$c = console.log("ack: Err");
}
$c;
call_ack_shaped(true);
const $d = call_ack_shaped(false);
let $e = null;
if ($d[0] === 0) {
	const nothing2 = $d[1];
	$e = console.log("ack2: Ok");
} else {
	const failure2 = $d[1];
	$e = console.log("ack2: " + debug(failure2));
}
process.exit($e);
