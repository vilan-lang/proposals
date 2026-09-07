Order 29 is sealed at <TIP> on next. Twelve lanes merged; union <UNION>; clippy, the Windows cross-check, audit and fmt green locally; CI <CI>. The train is <PARITY> entries; the cut stays held until you have tested kolt.

**Your crash, closed at the root.** Assignment from a live aggregate never copied (B257): a bare local read interns no type, so the clone pass dropped every plain local on the right of `=`. That one fix closed the `bind_each` crash with no std change (B255), and the same root was under `List::insert`, `Arena`'s slot writes, `SignalCell::set` and the iterator folds. B256, the `Shared::read()` seam, was built and measured and is HELD: +12–25% CPU on the reactive pins, +344% on a raw `get()`. The way through is B267, a cell-aware last-use elision, since both hot std reads have a dead or walked source. Your `set(filter)` workaround is no longer needed.

**Unsound accepts and a miscompile.** B251's struct-parameter accept and B246's bounded-operator hole are refused on zero-site censuses; B245's Mixer program compiles end to end with a workaround deleted. B244 turned out to be a silent miscompile: two instantiations of one doubly-generic function shared an emission, and `send_patch` had been avoiding it by hand.

**Performance.** The drop planner restores per module (M42) with its premise corrected by measurement: the cost was the enrolment gate, no type crosses, 154 of 3,398 bodies walked. `Node` boxed from 320 to 144 bytes, the macro worlds on the phase line with an on-disk expansion table, a warm kolt check 10.7% fewer instructions. `remove`/`insert` over `splice` with the panic kept. M36 is a spike, not a build: four address-keyed structures make world serialization infeasible, and the measurement reframes it as a suite-wide floor, about a third of vilan-core's suite CPU.

**Editor and std.** An import alias is an entity of its own; rename preserves it, and the red-first pass found an alias of a different length had no references at all. The formatter's seven rules and the chain break landed with one reformat: lines over 100 columns 150 → 107. The mirror is a `Source`, a 503 arm exists, `[expose(keyed = K)]` is the keyed spelling; the incremental diff was measured linear in the collection and declined, rightly, as its own item (A54).

**Closed 30, filed 26** (B258–B267, A53–A56, M48–M53, N59–N63, E150). Two premises overturned: B247 (a plain string has no holes) and M42's.

**Questions for you**, each on its item:
1. B256/B267: build the cell-aware elision first (my rec), land at the numbers, or clone at every read.
2. A53: a generic source field — three structural answers wanted before a build.
3. A56: refuse a disagreeing `keyed = K` over a `Map<K2, V>`; keep 429 for `authorize_timeout`.
4. B264: what go-to-definition at an import alias should answer.
5. N63: where the on-disk caches live (`vilan check` now creates `dist/`; my rec `dist/.cache/`).
6. E150: E147's threshold, count or measured (my rec count).
7. Still held: the cut, A46's form, B183's six.

**Process.** <PROCESS>

**Your editor build** (next only):

```bash
cargo install --path ~/code/vilan-lang/vilan/.claude/worktrees/integration/crates/vilan-cli --force && cargo install --path ~/code/vilan-lang/vilan/.claude/worktrees/integration/crates/vilan-lsp --force
```
