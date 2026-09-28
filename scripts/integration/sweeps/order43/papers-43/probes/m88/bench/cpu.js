const { spawnSync } = require("child_process");
for (let r = 0; r < 5; r++) for (const p of ["bench_dyn2", "bench_direct2"]) {
  const t0 = process.cpuUsage(); // parent
  const res = spawnSync("node", ["-e", `const s=process.cpuUsage(); import('./${p}.mjs').then(()=>{const u=process.cpuUsage(s); console.error(((u.user+u.system)/1000).toFixed(0));})`], { encoding: "utf8" });
  console.log(p, res.stdout.trim(), "cpu_ms", res.stderr.trim());
}
