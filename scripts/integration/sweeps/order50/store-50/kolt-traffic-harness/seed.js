// Seed a kolt server over its raw protocol: register two users, one channel,
// 50 messages alternating authors. Prints the token of user A and the channel id.
const base = "http://localhost:59401";
async function register(name) {
  const r = await fetch(base + "/api/register", { method: "POST", body: JSON.stringify([["username", name], ["password", "hunter2hunter2"]]) });
  const j = await r.json();
  if (!j.Ok) throw new Error("register " + name + ": " + JSON.stringify(j));
  return j.Ok.token;
}
function connect(token) {
  return new Promise((resolve, reject) => {
    const ws = new WebSocket("ws://localhost:59401/", ["vilan-rpc", "token." + token]);
    let next = 0; const pending = new Map();
    ws.onmessage = (m) => {
      const f = String(m.data);
      if (f.startsWith("__conn:")) resolve({ call(method, args) {
        const id = next++; ws.send("r:" + id + ":" + JSON.stringify({ method, args }));
        return new Promise((res) => pending.set(id, res));
      }, close() { ws.close(); } });
      else if (f.startsWith("r:")) { const rest = f.slice(2); const i = rest.indexOf(":"); pending.get(Number(rest.slice(0, i)))(JSON.parse(rest.slice(i + 1))); }
    };
    ws.onerror = reject;
  });
}
(async () => {
  const a = await register("amy" + process.pid), b = await register("bob" + process.pid);
  const ca = await connect(a), cb = await connect(b);
  const made = await ca.call("create_channel", ["general"]);
  const channel = made.Success;
  for (let i = 0; i < 50; i++) {
    const r = await (i % 2 ? cb : ca).call("add_message", [channel, "message number " + i + " says hello"]);
    if (!r.Success || !r.Success.Ok && r.Success.Ok !== 0) throw new Error("add_message " + JSON.stringify(r));
  }
  ca.close(); cb.close();
  require("fs").writeFileSync(process.argv[2], JSON.stringify({ token: a, channel }));
  console.log("seeded channel " + channel);
  process.exit(0);
})().catch((e) => { console.error(e); process.exit(1); });
