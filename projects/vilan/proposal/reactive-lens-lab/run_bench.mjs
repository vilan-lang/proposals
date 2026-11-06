// Runs a built bench several times and prints the best time per row:
//   node run_bench.mjs 5 src/bench.mjs [another.mjs ..]
import { execFileSync } from "node:child_process";
const [times, ...files] = process.argv.slice(2);
const best = new Map();
const draws = new Map();
for (const file of files) {
	for (let run = 0; run < Number(times); run++) {
		const out = execFileSync(process.execPath, [file], { encoding: "utf8", maxBuffer: 1 << 26 });
		for (const line of out.split("\n")) {
			const parts = line.split(" | ");
			if (parts.length != 4) continue;
			const key = parts[0] + " | " + parts[1];
			const ms = parseFloat(parts[2]);
			if (!best.has(key) || ms < best.get(key)) best.set(key, ms);
			draws.set(key, parts[3]);
		}
	}
}
for (const [key, ms] of best) console.log(`${key} | ${ms} ms | ${draws.get(key)}`);
