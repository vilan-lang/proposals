Repro (vilan-lsp, package with `lib.vl` = `export import pkg::inner::deep;` and `inner/deep.vl` exporting
`struct Overlay { open: bool }` and `enum Mode { On, Off }`; client.vl imports `pkg::lib`):

    fun classify(mode: lib::deep::Mode): i32 {
        match mode {
            lib::deep::Mode::On => 1,
            lib::deep::Mode::Off => 0,
        }
    }
    let o = lib::deep::Overlay { open = false };

Semantic tokens over `lib::deep::Mode::On =>`: only `Mode` (Enum) and `On` (EnumMember) - `lib` and `deep` carry no
Namespace token. Over `lib::deep::Overlay { open = false }`: only `Overlay` (Struct). The same segments in a value path
(`lib::deep::Overlay::fresh()`) and a type annotation (`x: lib::deep::Overlay`) paint Namespace since E315.
Cause: the pattern arm of `resolve_pattern` (analyzer.rs ~43255, "Record each `::`-separated segment") records only the
variant and the enum before it; the struct initializer records only its type name.
