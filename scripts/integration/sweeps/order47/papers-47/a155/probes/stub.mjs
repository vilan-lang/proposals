// The smallest DOM the probes reach: every element records its class writes.
let n = 0;
const all = [];
class El {
  constructor(tag) { this.tag = tag; this.id = ++n; this.attrs = {}; this.writes = []; this.children = []; this.style = { setProperty() {}, removeProperty() {}, getPropertyValue: () => "" }; all.push(this); }
  setAttribute(k, v) { if (k === "class") this.writes.push(String(v)); this.attrs[k] = String(v); }
  removeAttribute(k) { if (k === "class") this.writes.push("<removed>"); delete this.attrs[k]; }
  hasAttribute(k) { return k in this.attrs; }
  set className(v) { this.setAttribute("class", v); }
  set textContent(v) { this.text = v; }
  appendChild(c) { this.children.push(c); return c; }
  insertBefore(c) { this.children.push(c); return c; }
  append(...c) { this.children.push(...c); }
  addEventListener() {}
  replaceChildren(...c) { this.children = [...c]; }
  remove() {}
}
globalThis.document = {
  createElement: (t) => new El(t), createElementNS: (_, t) => new El(t),
  createTextNode: (t) => ({ textContent: t, remove() {} }), createDocumentFragment: () => new El("#fragment"),
  getElementById: (id) => (globalThis.__app ??= new El("#" + id)), head: new El("head"), body: new El("body"),
  createComment: () => ({ remove() {} }),
};
globalThis.window = globalThis;
process.on("exit", () => {
  for (const e of all) if (e.writes.length) console.log(`<${e.tag}#${e.id}> class writes: ${JSON.stringify(e.writes)} -> final "${e.attrs.class ?? ""}"`);
});
await import(process.argv[2]);
