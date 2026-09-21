# hygiene-39 hand-backs (proposals repo is read-only; this is the markdown)

## N112 — decision text for the tracker item

**RULED (recommendation built, 2026-09-21): KEEP B355's warning. `Error.note`
stays one note; `footnotes: Vec<Note>` is not built.**

B355's broad gate is the first place a second footnote looked wanted: with
diagnostics already standing, the context pass pushes nothing and reports one
warning counting the checks that did not run. Attaching that count to the
primary error instead would be a footnote about a *different subject* — the
primary error is one wrong expression, the deferral is a statement about a
pass — and it would have to hang off whichever diagnostic happened to be last
(`context.rs` already takes `program.diagnostics.len() - 1` purely as a source
id to render against, never as a claim of relation). That is not a relation a
reader can read.

The general rule, now written at `error::Note`: **a second fact that is not a
second LOCATION for THIS error is its own diagnostic, not another line under
this one.** C3's "one, not a list" is what keeps diagnostics terse, and the one
shape that genuinely is a chain already has its own field — `Error.trace`
(E78's requirement trace), deliberately not this one.

Cost of the alternative, for the record: the field is one line, and every
consumer gains a list to order and to truncate — the terminal renderer, the HMR
overlay, the language server's related information, the playground — while the
terseness rule stops being enforced by the type.

Landed as comments at `crates/vilan-core/src/error.rs` (`Note`'s doc) and
`crates/vilan-core/src/context.rs` (B355's gate), commit 839f50e4. No behaviour
change. N112 CLOSES.

## D9 — PREMISE STALE, nothing to write; recommend CLOSE

All three paragraphs D9 asks for are **already in** `editing-dx.md`, at its
tail under `### Order 37 as built (2026-09-17, lane editor-37)` (lines
~2649–2671), written by the integrator at proposals commit `8d4c73c`
("order 37: papers as-built — … editing-dx …"). Checked against the tree at
`c3f7d1a3`, every claim in them is true as built:

- **the E114 sentence** — `Document::unused_import_spans` (the fade) and the
  Organize Imports edit builder both call `Document::import_leaf_is_used`
  (`crates/vilan-lsp/src/document.rs:4623` and `:4707`); the doc comment above
  `unused_import_spans` states the identity in the same words. ✓
- **E69's numbers** — recounted from the generated table: 31 globals, 71
  events, 59 SVG presentation attributes (`SVG_GLOBAL_ATTRIBUTES`), 1,645
  per-tag pairs over **104** distinct tags with their own attributes. ✓ (For
  the record, `SVG_ELEMENTS` has 61 entries; 58 of them carry own attributes,
  which with 46 HTML-only is the 104 — the paper's numbers are consistent, just
  not the same set.)
- **E69's two shaping rules** — both are stated *in the generator* and are what
  the paper says: `SPELLABLE` drops a namespaced index entry (`xml:space`,
  `xlink:href`) because the head's attribute production cannot spell one, and
  `SVG_ROOT_DESCRIPTION` reads "SVG root" off the HTML index's own description
  cell rather than naming `svg` by hand. ✓
- **E193** — `struct_initializer_context` resolves the head through
  `path_struct_id` → `path_entity_id` (scope chain, then namespace per
  segment), with the program-wide first-name scan kept as an explicit
  `or_else` fallback for mid-edit buffers, exactly as the paragraph says; and
  `nominal_id_by_name` still scans, which the paragraph also says (E195). ✓

**Recommendation: close D9 as already landed.** One structural nit, the
integrator's call and not worth a commit on its own: the block is a `###` at
the very end of the file, after `## 20. Where the completion engine lives now
(K9)`, so it reads as a subsection of §20 rather than of §18 where the item
placed it. If it is ever tidied, `## 21. What shipped — Order 37 (editor-37)`
is the shape the rest of the paper uses.

## N109 — the two `vilan-rust` lines, for native-a-39

`crates/vilan-rust/src/lib.rs`, in the named-callee path (~line 4125 at
`c3f7d1a3`), DELETE:

```rust
        if Some(target) == self.program.list_new_fn_id {
            return Ok("Vec::new()".to_string());
        }
        if Some(target) == self.program.list_push_fn_id {
            let receiver = self.place_argument(&function_call.argument_ids, 0, depth)?;
            let item = self.value_argument(&function_call.argument_ids, 1, depth)?;
            return Ok(format!("{receiver}.push({item})"));
        }
```

and ADD two arms to `emit_intrinsic` (~line 4623, beside `Intrinsic::ListLen`),
where `next()` yields the arguments in order:

```rust
            Intrinsic::ListNew => "Vec::new()".to_string(),
            Intrinsic::ListPush => format!("{}.push({})", next(), next()),
```

Two cautions. (1) `ListPush`'s receiver is a PLACE (`place_argument`) and its
item a VALUE (`value_argument`); `emit_intrinsic`'s `next()` must yield the
same two renderings the deleted arm did, or the byte identity moves — check
what `next()` is bound to before taking the one-liner. (2) The deleted checks
sit ABOVE `self.program.intrinsics.get(&target)`, so deleting them is what
makes the rows fire; nothing else changes order.

Once those two lines are gone, `Program::list_new_fn_id` and
`Program::list_push_fn_id` (`crates/vilan-core/src/analyzer.rs`, ~line 50815)
have no readers left and go with them, together with the two assignments that
fill them in the `List` intrinsics loop (~line 59520). The field doc says so.

## B366 — what the Rust emitter can delete, for native-a-39

`crates/vilan-rust/src/lib.rs`, `bind_parameters` (~line 3355): the first
branch is dead.

```rust
        if parameters.contains(&pattern) {
            out.entry(pattern).or_insert(concrete);
            return;
        }
```

With it goes the paragraph of its doc comment that justifies a second copy of
`impl_select::bind_subject` ("it binds a `Type::Generic` node, and a nominal
declaration's parameter can appear in its own body as the constraint id itself
(whose `Type` is `Any`)"). What remains — being TOLD which ids are parameters
rather than reading `Generic(..)` alone — is still a real difference from
`bind_subject`, so the function itself stays; only the branch and the claim go.

The invariant is gated now: `crates/vilan-core/tests/nominal_generic_spelling.rs`.
Evidence that the branch is dead is in the lane report (census: 131
`Generic(..)`, 0 bare, over 44 declared parameters; and `bind_parameters` is
entered twice across a Rust-backend build of all 131 corpus programs, both
times taking the `Generic(..)` arm).
