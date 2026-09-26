globalThis.__param = (name) => Number(process.env["M87_" + name.toUpperCase()]);
await import("./app.mjs");
