// node --expose-gc measure_heap.mjs src/bench_memory.mjs
// Collects and prints the heap at each line the program prints starting MEASURE.
const log = console.log;
console.log = (...args) => {
	if (String(args[0]).startsWith("MEASURE")) {
		globalThis.gc();
		globalThis.gc();
		log(`${args[0]} | ${(process.memoryUsage().heapUsed / 1048576).toFixed(1)} MB`);
	} else {
		log(...args);
	}
};
await import(new URL(process.argv[2], `file://${process.cwd()}/`));
