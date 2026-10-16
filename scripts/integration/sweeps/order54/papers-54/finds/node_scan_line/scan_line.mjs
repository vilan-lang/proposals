// A173 S1 sketch: an incremental, awaiting line reader over process.stdin
// (no read-to-EOF). Pauses stdin whenever nobody is waiting so an idle stdin
// never holds the process open; "" at EOF; a trailing "\r" stripped.
const state = { buffer: "", ended: false, waiters: [], started: false };
function pump() {
  while (state.waiters.length > 0) {
    const newline = state.buffer.indexOf("\n");
    if (newline >= 0) {
      let line = state.buffer.slice(0, newline);
      state.buffer = state.buffer.slice(newline + 1);
      if (line.endsWith("\r")) line = line.slice(0, -1);
      state.waiters.shift()(line);
    } else if (state.ended) {
      const rest = state.buffer;
      state.buffer = "";
      state.waiters.shift()(rest);
    } else {
      process.stdin.resume();
      return;
    }
  }
  process.stdin.pause();
}
function scan() {
  if (!state.started) {
    state.started = true;
    process.stdin.setEncoding("utf8");
    process.stdin.on("data", (chunk) => { state.buffer += chunk; pump(); });
    process.stdin.on("end", () => { state.ended = true; pump(); });
  }
  return new Promise((resolve) => { state.waiters.push(resolve); pump(); });
}
const t0 = Date.now();
process.stdout.write("name? ");
const name = await scan();
console.log(`hello [${name}] at ${Date.now() - t0 >= 300 ? "after-wait" : "immediately"}`);
const next = await scan();
console.log(`next [${next}]`);
setTimeout(() => console.log("timer still fires"), 50);
