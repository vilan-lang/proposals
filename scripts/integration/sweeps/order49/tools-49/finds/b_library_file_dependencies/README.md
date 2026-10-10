B586's other half (not built by tools-49): `file_project` roots a `[library]` file at its
layer root now, but still hands it NO dependency workspace, where the language server's
`[library]` arm resolves `[library.dependencies]` (`resolve_dependencies`). Repro, from
this directory:

    vilan check lib/src/user.vl

reports `cannot find module 'dep' to import` (and `cannot find 'd' in this scope`), while
`vilan check lib` (the contract check) and the editor resolve `dep`. Rec: file mode of a
`[library]` file resolves the library's dependency workspace the way the `[package]` arm
does (it needs `package_dir`/the workspace plumbing `file_project` gives a package; not
tried, because the plumbing assumes a `[package]` manifest). Sizing S.
