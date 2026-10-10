# M?1 — two admitted blocks providing one trait default with different arguments are one candidate, the first registered

`first_i32/` and `first_str/` are the same program; only the module names of the two impl blocks differ, which reverses their load order.
`vilan check .` in each: `first_i32` is clean (`item` is `i32`, the `impl Box with Counting<i32> {}` block registered first); `first_str` is refused
(`let copy: i32 = item` — `item` is `str`, the `Counting<str>` block registered first). `inherited_default_candidates` dedups candidates by MEMBER id
(the trait's one `next`) after admission narrowing, so two admitted homes with different trait arguments collapse to whichever block registered first;
`rank_member_candidates`' homes rule (B73 R1: a home is `(trait, the arguments THIS receiver instantiates)`) would call the pair ambiguous.
The declined/admitted shape is fixed by M128 (incr-49); this both-admitted shape is the residue.
