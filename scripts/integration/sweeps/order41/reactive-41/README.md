# reactive-41 — A124 S2c PREPARED (not landed)

- `s2c-flip.patch` — `map`, `switch`, both `flatten`s and `and_then` return cold
  nodes (`Map`, `Switch`, `FlattenOption`, `AndThen` — the last two new); `map` is a
  blanket (reaches through `dyn Source<T>`; dyn-40's refusal pin flips to a pass);
  the `_node` spellings go; the mirror's own `map` goes and `or` returns a node;
  docs, examples, the split fixture, goldens, census numbers and the A124 pins
  follow; one `breaking` CHANGELOG entry. Off vilan `reactive-41` @ b3fa0a47
  (S2b 29c0f2bb + the guide commit); `git apply --check` clean there; builds.
  The suite over it: 19 red, all listed in `census.md` (5 find-blocked, 8 A25,
  4 behaviour re-derivations, 1 diagnostic, 1 no-cycle gate); corpus, split,
  examples, docs, markdown, copy census and the native differential green.
- `s2c-combine.patch` — ON TOP of the flip: `combine` over
  `(U in T: dyn Source<U>)` returning `Combine<T>`, `combine_node` retired.
  Builds; every `combine((a, b))` then throws at run time
  (`source[1].get is not a function`) until the mapped-tuple coercion find is fixed.
- `census.md` — the estate census by area.
- `finds/` — minimal repros of the compiler finds (each still red on next @9ffa397e).
