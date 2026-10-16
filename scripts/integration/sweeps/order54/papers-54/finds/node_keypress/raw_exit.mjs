// A173: does node restore the terminal when a raw-mode program exits without
// restoring (process.exit, an uncaught throw)?
process.stdin.setRawMode(true);
if (process.argv[2] === "throw") throw new Error("boom");
process.exit(0);
