## solver-52: final report

B620's analyzer half, E309 and B617 are all done, and every gate is green at the tip. Nothing is pushed and I have not rebased. `origin/next` has since moved to f40e2b47 (native-52 is merged), and I am waiting for your word before rebasing. No processes are left running. `solver-52-STATUS.md` is untracked and current.

**Branch `solver-52`, tip `6ef61d58`, base `029d5ab4` (C1).**

### Commits
| commit | item | family |
|---|---|---|
| 2ae15d7e | B620 (analyzer half): an element head admits only methods that hand the element back | fix (estate 0) |
| 99d9da3e | E309: a spaced generic call gets one steer naming the spacing | diagnostics |
| 20ff28f9 | B617: a `dyn` slot's body-less declaration threads its union's contexts | miscompile |
| 6ef61d58 | B620 slice 2: the head mark sits on the link's member, so a head nests no deeper than its chain | fix (no entry of its own; it adds a sentence to B620's entry) |

Each item's commit carries a `## Unreleased` CHANGELOG entry with a family marker (3 entries).

### B620
- **Premise held.** `<div .len() />` silently evaluated to the `usize` (it ran and printed 3). With children it failed with `usize has no method 'child'` at a zero-width span, and at a use site with "Expected View, but got usize".
- **How it works.**
  - The element desugar marks each head chain link's member as `Node::ElementHeadLink(tag, member)` (a new `Node` variant).
  - The analyzer records the marked calls (`element_head_links`).
  - `resolve_method_call`'s `Found` arm refuses a method whose return type is not the receiver's type. A trait default's `Self` is admitted, and so is an open generic.
  - The refusal sits at the method's name, for example "`len` is a method of `View` (from `Measure`), but an element head takes only methods that hand the element back (`View`); call it on the element instead: `<div />.len()`".
  - A refused link becomes `Expr::Error`, so the follow-on errors (the `.child`, the next link, the use site) no longer appear.
  - `<div />.len()` is admitted. A missing method keeps today's member error. Admitted links emit the same JS as the hand-written chain (pinned).
- **Why slice 2 exists.** Slice 1 wrapped the whole link in a forwarding node, which doubled the walk depth: a head of about 250 links was refused where the written chain checks fine up to 490. Slice 2 moves the mark onto the member and adds a pin that 450 links check both ways.
- **Estate: 0.** kolt copy, the website's `src`, the 11 examples, the 298 corpus programs.
- **Docs and ledger.** Spec paragraph in §3.6 (`vilan/docs/spec/grammar.md`). Ledger: a `NEW` row in the TSV and in `proposals/projects/vilan/proposal/diagnostics-ledger.md`.
- **Pins.** 8 in `inference/styling.rs`; 3 of them were proven red with the check disabled.

### E309
- **Premise held.** `pick <f64>(1, 2)` produced three refusals.
- **How it works.**
  - The walk notes the shape `L <M>(args)`: names or paths, a space before the `<`, a parenthesized list after the `>`.
  - It holds back the operands' "is a type, not a value" refusals.
  - After solving, when `L` is a generic function or a generic struct/enum, one steer at `L <M>` replaces all three.
  - For any other left side (values compared twice, a non-generic function), the held refusals are pushed as before.
- **Where the brief was wrong.** The parser cannot decide this case alone, because whether the name is generic is only known after resolution. The parser's seam that is reused is `tighten_generic_list` (now `pub(crate)`).
- **Spec, ledger, pins.** One sentence added to §3.6. Ledger rows `NEW` in both places. 2 new pins in `ascription.rs`, plus an updated E291 pin: its function case now uses a non-generic `pick`.

### B617
- **Where the premise was wrong.** JS was already right in every shape I built: the `dyn` call site's candidates already include the blanket impl, and the call threads the value. The bug was native only. The object-table slot is typed by the trait's body-less declaration (`Flow::start`), which had no hidden parameters, so B606's stand-in passed `None`. Natively a safe read printed `blanket, no scope` where JS printed `blanket under s`; a strict read was refused.
- **dispatch_refine.rs.**
  - New `object_slot_declaration_unions`: for each dyn-dispatched member whose declaration has no body, every impl member of the declaring trait, blankets included.
  - The per-trait candidate loop is now shared as `trait_member_candidates` by `candidates_of`, `bound_candidates` and the new union.
- **context.rs** (the candidate union only; `apply` not touched): per context, after every refusal, a declaration whose union contains a needy member joins `needs` without propagating further. It joins `strict` too when any member reads strictly.
- **vilan-rust, a listed arm in native-52's file (please tell them):** `object_slot_arguments`.
  - The `None` stand-in is kept only for a trait default's declaration.
  - For a body-less declaration, a missed context now refuses.
  - A bare declared value handed to a safe impl is passed as `Some(..)`.
- **Pins.** New native probe `native/dyn_slot_blanket_context.vl` with the `native_differential` test `b617_a_dyn_slot_hands_a_blanket_impl_the_contexts_it_reads` (red without the union: the backend refuses). JS pin `dyn_objects::b617_…`.

### Gates at tip 6ef61d58
- **Full suite** (`--cargo-profile ci-test -E 'not binary(deep_nesting)' -j 6`): 10544/10544 passed, 32 skipped.
  - Within it: `ci_ignored_pins` 12, `hygiene` 3, `corpus` 14, `check_scope_differential` 16, `native_differential` 271, vilan-lsp binary 386.
- **Native sweep mode** (`VILAN_NATIVE_DIFFERENTIAL=1`): 271/271, 1 skipped.
- **Deep-nesting canary at 1536 KiB:** 18/18.
- **clippy, `cargo fmt --check`, `vilan fmt --check .`:** all 0.
- **`ci-local.sh perf`:** T2 green, growth x1.928. kolt late-writes=0.
- **kolt cold-check RSS:** median 260,788 KB at tip vs 264,644 KB for the installed 0.49.0 (-1.5%). I had no C1 release binary to compare against.
- The full suite and canary were re-run after slice 2.

### Functions changed
- **analyzer.rs**
  - Changed: `walk_expr_node` (the stray-mark arm), `walk_member_accessor_entity`, `walk_ascribe_entity` (stage), `resolve_method_call` (`Found` arm), `walk_binary_entity`, `resolve_prepped_local` (the held refusal), `finalize_build` (the operator loop skips steered comparisons).
  - New: `hands_back_the_element`, `refuse_element_head_link`, `note_spaced_generic_call`, `steer_spaced_generic_calls`, `names_something_generic`.
- **Other files:** `elements.rs` `build_chain`; `node.rs` (new variant, `for_each_child`, new `unmark_head_link`); `lib.rs` platform sniff (peels the mark); `parsing.rs` `tighten_generic_list` visibility.
- **mono.rs and the JS emitter:** untouched.

### Finds
In `sweeps/order52/newitems52-solver-52.json`; repros are in `sweeps/order51/solver-52/finds/`, as the brief's path says.
- **E?1:** E309's residue. A spaced generic method call (`h.make <str>("a")`) still gets the cascade, because `h.make` is resolved as a field before anything knows `make` is a generic method.
- **E?2:** A method named without parentheses (`p.norm`, `<input .autofocus />`) says "has no field". There is no steer to `.norm()`, and E119's twin note wrongly claims only the browser twin declares `autofocus`.

### Questions for the owner
1. **Family for B620.** I used `fix` because the estate is 0, as R-e says. Even so, a program that compiled before (`let n = <div .len() />;`) is now refused. **Rec:** keep `fix` with estate 0, and mention the new refusal in the v0.50.0 notes.
2. **Should B617's union also widen trait DEFAULTS' declarations** (for example `Source::attach_observer`)? Doing that would make every direct caller of a default thread values it never reads, which changes goldens and adds cost. **Rec:** no for now. The `None` stand-in stays for defaults only, and a strict miss there is still refused by name.
3. **The E309 steer for a generic TYPE** (`List <i32>(3)`) suggests `List<i32>(3)`, which then fails as "a type, not a value". **Rec:** keep it, since the item asked for the spacing to be named. A later item could steer a type to `::new(..)`.
4. **E?2:** should a field miss check for a method of the same name and steer to the call? **Rec:** yes, as a small `diagnostics` item in the next order.

### Rebase note
Since my base, native-52 has merged. My vilan-rust edit is confined to `object_slot_arguments` and two of its comments; native-52's changes are elsewhere in that file. Conflicts I expect: only CHANGELOG ordering and the tails of the two ledger files.
