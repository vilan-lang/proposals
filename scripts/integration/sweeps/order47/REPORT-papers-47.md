## papers-47 report

I wrote both papers and left them uncommitted in the proposals checkout. Nothing changed in the vilan tree. I built the compiler in a new worktree, `vilan/.claude/worktrees/papers-47` (branch `papers-47` off origin/next @b94cb47f, no commits; reap it when you're done). Probes ran on copies in its `target/papers-47-scratch/`. I ran no git command in kolt or the website.

- `/home/reed/code/vilan-lang/proposals/projects/vilan/proposal/class-writes.md` (A155)
- `/home/reed/code/vilan-lang/proposals/projects/vilan/proposal/closure-captures.md` (C15; a sequel to papers-43's `closure-captures-on-native.md`)
- Probes, censuses, benchmarks and run logs: `proposals/scripts/integration/sweeps/order47/papers-47/{a155,c15,finds}/`

### A155: recommendation
- **Nobody writes an element's class twice.**
  - kolt, the website and the examples hold 405 class writers. No element has two, and `vilan check` gives 0 warnings on all three.
  - The website was also run with an instrumented copy of std: 482 classed elements on the server (`/` and `/playground`), 443 in the client boot, 0 double writes.
  - Authors compose into one writer instead: 27 sites use `.styled(a + b)`, and 3 reactive writers compute the whole class list themselves.
- **Appending would break styles.** A style is one class per property, so two appended styles that both set `color` leave the winner to the stylesheet's hash order (probe a3: red wins although blue was written last). An append that composed with `+` would avoid that, but it needs per-element state on both twins, for 0 sites.
- **Rec: keep last-wins and never append.** Fix two gaps in today's warning now, then make a visible double write a compile error at the next breaking cut. That costs **0 sites** to migrate. Calls through a function of the program's own stay silent. Today both the server render and the client are plain last-write-wins (§2.1 has thirteen probes on both).

### C15: recommendation
- **What boxing costs.**
  - JS: 0 cells.
  - Native: one 40-byte allocation and about 152 instructions per boxed scalar, measured with callgrind. The closure's own allocation, about 178 more, is paid by every closure, boxed or not.
  - A `Store` write costs about 4,150 instructions and 15 allocations; its 3 boxes are about 11% of that.
- **Where boxes appear.** There are 16 distinct boxed sites:
  - the test corpus: 113 of 145 programs emit natively, with 5 boxes;
  - kolt's native server: 7, all from std or generated code;
  - the `rpc` example: 4;
  - a `Store` probe: 5.

  Bindings in std that closures capture and write grew from 12 to 43, nearly all the store's out-parameter closures.
- **Soundness of the narrower rules.**
  - The brief's rule (one closure that never escapes stays unboxed) is **unsound** if the closure gets a copy. §6.9's own example is the counterexample: hand-lowered, it prints `before` where the rule says `after`.
  - It is sound only as a borrow, with a third condition: no access from the enclosing function between the closure's creation and its last use. rustc then re-checks the result, so a wrong classification fails to compile rather than printing a wrong answer.
  - "Written only before the capture" is sound only when judged by control flow; read off the source text, a loop breaks it (probe c2).
  - Moving the binding into the closure is sound only if the closure is created once per binding; created in a loop, the hand-lowered version prints `1 1 1` for `1 2 3`.
- **Nothing to gain today.** The sound rules reach 3 sites, all cold. The store's 4 hot sites fit the borrow rule's shape, but their callee is a closure value, which the existing escape analysis treats as keeping everything. Every narrower rule also needs a second closure representation natively.
- **Rec: keep §6.9 and the box-everything rule (R3), and build no narrower rule now.** The closure-captures paper parks the three narrower rules, each with its condition. Fix the deep-copy bug (F49 plus its new field-read twin) before the store runs natively on the server. Answer the reentrancy abort the way F39 was answered, by refusing it at compile time. A std-only option is on offer: put the store write's three out-parameters in one struct, about 7% of a write.
- **Tracker drift:** F50 is effectively done at this base (its census column, its leak-census row and its spec note are all present), though the tracker still lists it OPEN.

### Questions for the owner (each paper gives its recommendation)
- **A155**
  - Q1: writers stay last-wins, no append? (rec yes)
  - Q2: the visible double write becomes an error at the next breaking cut, 0 sites? (rec yes)
  - Q3: fix the two warning gaps now? (rec yes)
  - Q4: leave cross-function double writes silent, with a census trigger, and park the append options behind it? (rec yes)
  - Q5: close A155 on the paper? (rec yes)
- **C15**
  - Q1: keep §6.9 and R3 unchanged? (rec yes)
  - Q2: record the brief's rule as unsound and keep the borrow version on file as the candidate? (rec yes)
  - Q3: refuse the reentrancy case at compile time? (rec yes)
  - Q4: widen F49 to field reads and fix it before the store's server half runs natively? (rec yes)
  - Q5: offer the one-struct option to the lane that builds the store's server half? (rec yes)
  - Q6: close C15 and F50? (rec yes)

### Finds filed
In `sweeps/order47/newitems47-papers.json`; repros are in `papers-47/finds/`.
- **A?1:** the A155 warning ignores `.bind_attr("class", ..)` and `.toggle_attr("class", ..)`. Both clobber the class silently; the second removes it.
- **A?2:** the A155 warning says the later writer stays, which is false when the earlier writer is reactive. In the browser the earlier binding re-applies on every change.
- **B?1:** running `vilan check main.vl` from inside a package's `src/` ignores the package (its prelude and std). The path's parent is empty, so no manifest is found. kolt and every example package fail that way; an absolute path works.
- **F?1:** natively, a closure that writes a captured variable while a `&mut` reference to it is live aborts with "a cell was read while it is being updated". JS prints 11 and 102, and the program declares no shared cell.
- **F?2:** natively, reading one field of a boxed variable copies the whole value. In the store that is six whole copies of its internal bookkeeping struct per write; it is F49's sibling.

Not filed: kolt's client e2e harness is too old for the current std (it lacks `replaceState`, `removeAttribute`, `parentNode`, ranges and fragments), so A155's run-time census could not run kolt's client. kolt is covered by the static census and `vilan check` only. Port 59401 was already in use on the machine, so my kolt copy used 59447.
