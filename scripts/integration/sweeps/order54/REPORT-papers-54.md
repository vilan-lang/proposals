# papers-54 hand-back (Order 54): terminal.md (A173) and std-prefix P6 (M157)

## Tree
- base = tip = b7c7afe0 (origin/next), branch `papers-54`, worktree `vilan/.claude/worktrees/papers-54`. NO commits, NO tree change; nothing pushed. analyzer.rs / mono.rs / emitters: no function changed.
- Gates: none apply (no tree change). Probes ran on the installed `vilan 0.51.0 (4b41c7ff5)` in both locations. v0.51.1 is not cut at b7c7afe0, and nothing it would touch differs.

## Papers (proposals checkout, uncommitted, for the integrator)
1. `projects/vilan/proposal/terminal.md` (A173, NEW). The integrator got an interim message the moment it was written.
2. `projects/vilan/proposal/std-prefix.md` §14 "P6 — §4.2 hardened from guard to rule" (M157, appended).

## Where the premises were wrong
- A173 "`__scan` reads all of stdin to EOF, so a prompt blocks": wrong, and worse. In the emitted `.mjs` the helper's `require("fs")` throws a ReferenceError (B86b, v0.33.0), and its own catch swallows it. So `scan()` returns "" on EVERY call, whatever stdin holds. Zero callers on the estate.
- A173 "no native scan": true, but the gap is wider. Native refuses scan, args, exit and cwd with a named diagnostic; only env works.
- A173 "the corpus/differential keep working on a pipe": nothing to keep. The corpus runs with stdin null and no program reads stdin.
- A173 "verify for over an awaiting next": the trait form is REFUSED (`&mut self` cannot be async). The inherent form passes the checker and then MISCOMPILES on both backends (B?2, F?3).
- A173 "BodyReader carries the ambient signal": not per read. The request carries it.
- A173 (implicit): std cannot print a prompt at all. There is no no-newline stdout (E?5).
- M157 "~600 entities": the gap is 621, confirmed. It is a PERMUTATION: both shapes mint the same entities, and max id 10904 is the same in both. Single-file programs are already one layout (57/57 corpus native emissions byte-identical across shapes).

## Measurements (instructions, 3 runs each, load 4–5)
Cold `vilan check`, three shapes:

| Subject | off | on, no file | on, loaded file |
|---|---|---|---|
| M157 repro | 252.94 M | 667.85 M | 157.77 M |
| kolt (both legs) | 10.210 G | 10.260 G (+0.49 %) | 8.765 G (−14.2 %) |
| todo | refused (defines-a-macro) | refused | refused |

- The middle column is an upper bound on door A's cost. Its excess is the closure parse with no index (107 ms) plus the guard's `everything` reach log during std's resolve. That attribution comes from phase lines; P6a measures it first.
- Guard census on the estate: zero `impl-reached` refusals.
  - kolt: both legs served.
  - corpus: 138 served, 8 not taken (macro worlds).
  - examples: 10 served; todo refused for defines-a-macro.
- Node probes: raw-mode exit restore; the keypress table; the incremental line pump.
  - The pump must `unref()` stdin while nobody waits: with a pipe whose writer stays open, node otherwise runs 3.4 s instead of 0.47 s.

## Finds (`sweeps/order54/newitems54-papers-54.json`; repros under `sweeps/order54/papers-54/finds/`)
- B?1: `process::scan()` returns "" on every call on JS since v0.33.0 (fix; S1 replaces it).
- B?2 MISCOMPILE, both backends: a `for x in subject` whose `next` reads a context (any std IO wait, or `ambient_signal()`) is emitted without the threaded context argument. A check-clean program crashes on JS with a TypeError, and native fails cargo.
- F?3: native emits no `.await` on a for-in over an awaiting inherent `next`.
- F?4: native implements env but refuses scan, args, exit and cwd (rec: into A173 S1).
- E?5: std has no no-newline stdout (prompt in S1, `io::write` in S2).
- N?6: the prefix census prints no reason for programs that silently skip the prefix (macro worlds).

## Questions for the owner
terminal.md:
1. The names. Rec: `process::keys(): Keys` (a resource; Drop restores), `Keys::next(): Option<Key>` plus `next_press(): Option<Press>` for modifiers, a flat `Key`. For lines, `read_line(): Option<str>` with `scan()` kept as `read_line().unwrap_or("")`.
2. A `prompt(text)` twin. Rec: YES. Today a prompt cannot be printed at all.
3. The native decoder's dependencies. Rec: no crossterm and no Rust decoder. ONE decoder in std vilan, so decoding is identical by construction. Raw mode goes in a separate `vilan-rt-term` crate on libc + windows-sys (both already in Cargo.lock), linked only by programs that call `keys()`. Windows uses VT input mode. S1 needs no dependency.
4. The pipe rule. Rec: the full grammar on a non-TTY, with unbounded lookahead and no timeout. It is deterministic, so key programs are testable via `vilan run < file`, the corpus and the differential. `\r`, `\n` and `\r\n` are each one Enter; `None` at EOF.
5. Ctrl-C under `keys()`. Rec: deliver it as `Key::Ctrl("c")`.
6. `for key in keys`. Rec: fix B?2/F?3 in Order 55; S2 ships the `for { match .. }` loop meanwhile.

std-prefix P6:

7. Door A (the rule) vs door B (id-free native names). Rec: A.
8. The rule's statement: "std's and a dependency's declarations resolve before the entry package's exist." Rec: family `fix` (estate 0), with the guard kept as a test oracle.
9. The tier boundary with dependencies. Rec: std + dependencies together before the package (today's shape). P6c only on need.
10. The B553/B239 deferral. Rec: it defers only the package half.
11. The CLI default `on`. Rec: in the order after P6a, together with P5 and M158; not this order.

## Housekeeping
- Removed my own scratch copies under `vilan/.claude/worktrees/papers-54/target/papers-54-scratch/`: kolt, corpus, examples, todo, m157dbg, and the `wc` world-cache dir I pointed `VILAN_WORLD_CACHE` at.
- Removed the `dist/` dirs my native probe runs wrote under `papers-54/finds/`.
- `~/.vilan/cache/worlds` was never written: every run used `off` or the scratch dir.
- No process running.
