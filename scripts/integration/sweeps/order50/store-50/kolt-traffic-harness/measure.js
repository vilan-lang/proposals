// Measure kolt's REAL client traffic: the built bundle under the shared DOM
// stub, signed in with a seeded token, deep-linked to the seeded channel. Every
// WebSocket frame is counted and its bytes summed (as sent and as received,
// the `d:`/`r:` prefixes included), per phase:
//   open    - from connect until the 50th message's row has painted
//   rename  - a writer renames the channel; until the client has painted it
//   message - a writer adds one message; until it has painted
const fs = require("fs");
const path = require("path");
const dist = process.argv[2];
const state = JSON.parse(fs.readFileSync(process.argv[3]));
eval(fs.readFileSync(path.join(__dirname, "stub.js"), "utf8") + "\ninstallStubDocument({ rootTag: 'root' });");
global.location.pathname = "/c/" + state.channel;
global.historyEntries = [global.location.pathname];
const backing = new Map([["kolt.token", state.token]]);
const storage = { getItem: (k) => (backing.has(k) ? backing.get(k) : null), setItem: (k, v) => backing.set(k, String(v)), removeItem: (k) => backing.delete(k) };
global.localStorage = storage; global.sessionStorage = { getItem: () => null, setItem: () => {}, removeItem: () => {} };
global.window.localStorage = storage;
global.window.matchMedia = () => ({ matches: false, addEventListener() {}, removeEventListener() {} });
global.matchMedia = global.window.matchMedia;
global.navigator = global.navigator || { platform: "Linux" };
let phase = "open";
const tally = {};
const count = (dir, data) => {
  const t = (tally[phase] = tally[phase] || { up: 0, upBytes: 0, down: 0, downBytes: 0 });
  const bytes = Buffer.byteLength(String(data));
  if (dir === "up") { t.up++; t.upBytes += bytes; } else { t.down++; t.downBytes += bytes; }
  if (process.env.TRACE) console.log(phase + " " + dir + " " + String(data).slice(0, 160));
};
const NativeWebSocket = global.WebSocket;
global.WebSocket = class extends NativeWebSocket {
  constructor(url, protocols) {
    super(new URL(url, "ws://localhost:59401").toString(), protocols);
    this.addEventListener("message", (m) => count("down", m.data));
  }
  send(data) { count("up", data); super.send(data); }
};
const until = (probe, label, ms = 20000) => new Promise((resolve, reject) => {
  const started = Date.now();
  const tick = () => { let v; try { v = probe(); } catch (e) { v = null; } if (v) return resolve(v);
    if (Date.now() - started > ms) return reject(new Error("timeout: " + label)); setTimeout(tick, 10); };
  tick();
});
const text = () => flatten(documentRoot);
async function writer() {
  return new Promise((resolve) => {
    const ws = new NativeWebSocket("ws://localhost:59401/", ["vilan-rpc", "token." + state.token]);
    let next = 1000; const pending = new Map();
    ws.onmessage = (m) => { const f = String(m.data);
      if (f.startsWith("__conn:")) resolve({ call(method, args) { const id = next++; ws.send("r:" + id + ":" + JSON.stringify({ method, args })); return new Promise((res) => pending.set(id, res)); }, close() { ws.close(); } });
      else if (f.startsWith("r:")) { const rest = f.slice(2); const i = rest.indexOf(":"); const p = pending.get(Number(rest.slice(0, i))); if (p) p(JSON.parse(rest.slice(i + 1))); } };
  });
}
require(path.join(dist, "client.js"));
(async () => {
  await until(() => text().includes("message number 49 says hello"), "the 50th message paints");
  await new Promise((r) => setTimeout(r, 300));
  const w = await writer();
  phase = "rename";
  await w.call("set_channel_name", [state.channel, "general-renamed"]);
  await until(() => text().includes("general-renamed"), "the rename paints");
  await new Promise((r) => setTimeout(r, 300));
  phase = "message";
  await w.call("add_message", [state.channel, "one more message"]);
  await until(() => text().includes("one more message"), "the new message paints");
  await new Promise((r) => setTimeout(r, 300));
  w.close();
  console.log(JSON.stringify(tally));
  process.exit(0);
})().catch((e) => { console.error("FAIL " + e.message); console.log(JSON.stringify(tally)); process.exit(1); });
