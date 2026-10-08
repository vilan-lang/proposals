function area(self) {
	return self[0] * self[1];
}
function $a(items) {
	let sum = 0;
	for (const item of items) {
		const part = area(item);
		sum = sum + part;
	}
	return sum;
}
const points = [ [ 1, 2 ], [ 3, 4 ] ];
const shadow = 1;
const shadow2 = shadow + 1;
console.log($a(points) + shadow2);
