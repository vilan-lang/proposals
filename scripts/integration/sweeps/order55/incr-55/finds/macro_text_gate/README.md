# incr-55 find: the macro-defining bypass is textual

`analyze_inner`'s `base_cacheable` refuses any entry whose TEXT contains `macro`
(`entry_source.contains("macro")`), so a comment or a string that says the word makes the entry
uncacheable: no base cache, no std prefix (N179 now names it `macro-text`). On the corpus: `crypto`,
`db`, `file`, `watch` say it only in a comment ("Excluded from the macro interpreter gate"):

    VILAN_STD_PREFIX=on VILAN_PHASE_TIMING=1 vilan check vilan/test/crypto.vl
    # ... prefix-world 0 prefix-refusal macro-text
