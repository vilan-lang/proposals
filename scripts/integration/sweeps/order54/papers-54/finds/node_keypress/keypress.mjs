// A173 ground truth: what node's emitKeypressEvents (no readline interface)
// decodes for each sequence, and whether a lone ESC is ever delivered alone.
import readline from "node:readline";
const start = Date.now();
readline.emitKeypressEvents(process.stdin);
if (process.stdin.isTTY) process.stdin.setRawMode(true);
process.stdin.on("keypress", (str, key) => {
  const t = Date.now() - start;
  process.stdout.write(JSON.stringify({ t, str, name: key.name, ctrl: key.ctrl, meta: key.meta, shift: key.shift, seq: key.sequence }) + "\r\n");
  if (key.name === "q" && !key.ctrl) { process.stdin.setRawMode && process.stdin.isTTY && process.stdin.setRawMode(false); process.exit(0); }
});
process.stdin.on("end", () => { process.stdout.write("END\n"); });
