# a generic variant inside a list, a tuple or as a method receiver hovers bare (`Option::Some`)

```vilan
fun main() {
	let list = [Some(1), None];        // `Some`, `None` hover `Option::Some` / `Option::None`
	let pair = (Some("a"), 2);         // `Option::Some`
	let mapped = Some(4).map(|v| v + 1); // `Option::Some`
}
```
E317 settles the instantiation from the return slot, an annotation, the binding the value initializes and a plain call's parameter (E328 now adds the payload there). A list/tuple element and a receiver have none of those facts: the instantiation would come from the element type of the list / tuple (`expr_types` of the container) or the call's receiver type.

# a qualified struct literal's derived reference row (fixed in E327's commit)

`lib::deep::Overlay { open = true }`: the reference index derived a second row for the literal anchored at its start and as long as the struct's name (`lib::de`), so renaming `Overlay` replaced `lib::de` with the new name, and the row overlapped the module segments' rows. Repro before the fix: rename `Overlay` -> edits `["lib::de", "Overlay"]`.
