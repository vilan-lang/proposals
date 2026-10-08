Error: the `rust` backend does not emit a value of type `an unresolved type` yet — this is F1's slice S1b, whose scope is structs, enums, generics, `Option`/`Result`, `str`, `List`, `Map`/`Set`, closures, `impl`s, traits, operators, `?`, `print`, `panic` and the reactive cell. Build this program with `--backend js`.
    ╭─[ v1_let_typed.vl:14:10 ]
    │
 14 │ ╭─▶     let h = |c| {
    ┆ ┆   
 16 │ ├─▶     };
    │ │            
    │ ╰──────────── the `rust` backend does not emit a value of type `an unresolved type` yet — this is F1's slice S1b, whose scope is structs, enums, generics, `Option`/`Result`, `str`, `List`, `Map`/`Set`, closures, `impl`s, traits, operators, `?`, `print`, `panic` and the reactive cell. Build this program with `--backend js`.
────╯
