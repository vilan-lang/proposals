Hover on `Some` in `let some = Some(1);` reads `Option<i32>::Some` (E317), where a pattern hover on `Some(let n)` reads
`Option<i32>::Some(i32)` (E241): `variant_value_hover` (vilan-lsp document.rs) spells the declared payload only for an
enum with no parameters ("a generic one's instantiation is the head's") and so never states the payload of a generic
enum's variant. The instantiation is now known (E317), so the payload could be substituted the way
`pattern_labels` does (`pretty_print_type` under `applied_substitution`).
