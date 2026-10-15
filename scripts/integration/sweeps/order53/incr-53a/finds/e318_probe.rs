//! Scratch probe (not committed): does a const site's value depend on the
//! emitter tables the E318 flag skips?
use std::path::PathBuf;
use vilan_core::analyzer::Workspace;

fn std_spec() -> vilan_core::PackageSpec {
    vilan_core::manifest::resolve_std(&PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("../../vilan/std"))
}

fn run(skip: bool) -> String {
    let dir = std::env::temp_dir().join(format!("e318probe{}{}", std::process::id(), skip));
    let _ = std::fs::create_dir_all(&dir);
    let entry = dir.join("main.vl");
    let source = "fun build(): usize {\n\tlet a = [1, 2];\n\tmut b = a;\n\tb.push(3);\n\ta.len()\n}\n\nfun main() {\n\tlet n = const build();\n\tprint(n);\n}\n";
    std::fs::write(&entry, source).unwrap();
    let leaked: &'static str = Box::leak(source.to_string().into_boxed_str());
    let workspace = Workspace { skip_emitter_tables: skip, ..Workspace::default() };
    let std = std_spec();
    let out = std::thread::Builder::new().stack_size(256 << 20).spawn(move || {
        let (program, errors) = vilan_core::analyze_source(leaked, &std, &dir, &entry, None, &workspace);
        let program = program.expect("program");
        let mut values: Vec<String> = program.const_results.values().map(|v| format!("{v:?}")).collect();
        values.sort();
        format!("errors={errors:?} consts={values:?}")
    }).unwrap().join().unwrap();
    out
}

#[test]
fn probe() {
    let emitting = run(false);
    let skipping = run(true);
    eprintln!("emitting: {emitting}\nskipping: {skipping}");
    assert_eq!(emitting, skipping);
}
