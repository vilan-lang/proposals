
MERGED (fourteen lanes, in the order they landed): hygiene-28 (ce0eaac5), checker-28 (a9dcf2ea),
rigid-28 (b9da587d), parse-fmt-28 (c283ce7b), editor-28 (961b0a48), b184-b218 (b294101f),
context-28 (712128cf; its paper section into proposals main at 6a278cc), perf-28 (20c6ff80),
std-28 (7e0066ae), rpc-28 (8bb37b40), m19-t1b (<M19TIP>), compile-perf-28 (<CPTIP>), l19-ci
(<L19TIP>, merged LAST with its reformat regenerated over the merged tree). Ledger rows 389–399
assigned (next 400); CHANGELOG parity <PARITY>.

SEALED <DATE> at <TIP>: union <UNION>, clippy, the Windows cross-check, audit and fmt green
locally; CI <CI>. The order's verdicts: CI's own clock — the Linux legs verbatim in
`scripts/ci-local.sh` with ci.yml calling it, the cache and two partitions per OS, the fmt gate
after one reviewed reformat of 101 files, the modules differential in its own binary (L19 steps 1
and 3, N55, N57); the context BOUNDARY — B241's cascade rooted, B232's residual, and B242 built as
the owner proposed (`fun f(): T context settings`, the subset rule over strict reads, a wider
clause a warning, callers checked against the declaration, trait methods deferred with a message);
two UNSOUND accepts refused with zero-site censuses (B233 two rigid parameters on an operator,
B234 a rigid parameter as a condition) and B235's `= Self` default no longer a bound; B237 a
MISCOMPILE nobody had filed as one (an assignment beside a guard capture targeted a top-level
function and compiled clean); trait-typed FIELDS as sugar over a hidden parameter grounded per
literal with the `C<A>` display (B184/B218), byte-identical emission; `Source` inverted to
`on_change`-required (A49), a refused client told so on the only channel the host WebSocket
leaves (A47), the verifier bounded (A48); keyed deltas and per-key subscription over the wire
(A39: an edit 123,753 → 95 bytes, a leased key's later events 0; the `List<T>` macro form the
residue A51); tranche 1b restoring six class D passes per reused module (411 → 367 → 341 ms on
kolt's client leg); the other session's compile-time finds −26% Ir on a cold check with `check`
in parallel across entries; E138 a PHANTOM and B238's premise wrong, both said so; M38 measured
and withdrawn; `::` no longer crosses a line and imports alias (E142); rename at a shorthand
expands and the formatter canonicalizes the shorthand (E143). Forty-one closes; twenty-six
filed (B243–B254, E145–E149, M42–M44, M46, N58, A50–A52, L20); M27 narrowed, M36 designed,
E121 annotated; prose ledger rows 386–399 written, three of them Order 27's omission.

PROCESS:
- Lane m19-t1b ran a broad `pkill -f cargo-nextest` and killed sibling runs (checker-28's LSP
  gate re-run; perf-28's and context-28's whole-suite runs), then said so in its report; for a
  while it read as memory pressure. The own-PIDs rule stands; briefs restate it in capitals
  naming this incident.
- A FOURTH semantic conflict no build could see: std-28's `Source` inversion (a default `sub` calling
  the `on_change` requirement) met rpc-28's forward closures stored in plain `|| Subscription` fields,
  and `async_infer` resolved the default body's `self.get()` against EVERY same-named member — the
  `[service]`-generated async `get` colored `sub` async and std's own fields were refused; neither
  lane's tree had both halves. Bisected to the rpc-28 merge, fixed the same hour by lane a49-async
  (a default body's self call resolves against the trait's own subjects; B254 the sibling). Rule: a
  lane that turns a requirement into a default grep-lists the generic callers of that member.
- Three SEMANTIC conflicts git resolved textually and the build caught: E142's alias widened a
  shared tuple B236's collector destructured (patched at integration so the covered set carries
  the alias); E143's per-span rename edits versus parse-fmt-28's alias pins; perf-28's completion
  read-count pin versus the merged tree's zero reads (M39 over M29). Rule: a lane widening a
  shared tuple greps its destructurings; the build is the gate that sees semantics.
- The fold helper learned three things from one lane (b184-b218): carry a lane's NEW top-level
  consts (by raw-string terminator, not the next column-0 line — the first attempt truncated a
  fixture and swallowed the next one), and DROP the functions a lane deleted (a refusal the lane
  removed survived and failed); each committed to `scripts/integration/` the same hour.
- My own target-name miss (`--test docs` in vilan-cli) stopped rigid-28's chain once; the
  standing rule applies to the integrator.
- 1Password's agent went down mid-order: three lanes stopped at their commit or push exactly as
  briefed; their work was committed and pushed from their worktrees after the owner's unlock.
- Three lanes measured milliseconds under lane load and two items (M37, M38) were filed on wall
  readings; perf-28 restated them in callgrind Ir. Rule: perf items carry Ir or process CPU with
  loadavg, never wall.
- One lane authored commits with the gmail address and GitHub's email-privacy rule refused the
  push; rewritten to the noreply identity. Briefs name the identity.
- CI's first answer on the seal was red on WINDOWS ONLY, the fourth seal running: E140's cone pin
  compared the server's manifest directory (kept in the URI's short spelling, and the key of E124's
  package clock) against a canonical path — now canonical where it is discovered, with the package
  root beside it; and M27's entity-table pin PANICKED on a host with no thread CPU clock instead of
  declining the cost claim as the budget gates do. The ubuntu partitions passed in 11 and 8 minutes
  on a cold cache (25 before). Rule restated: every path canonical at its source; a pin that needs
  a clock the host lacks declines.
- The helpers now live in `proposals/scripts/integration/` (Order 28's first act); the scratchpad
  was wiped once more mid-session and nothing was lost to it.
