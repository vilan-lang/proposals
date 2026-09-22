//! I5's census, BY PARSE (Order 40, lane papers-40).
//!
//! Run as a `vilan-core` example over the worktree:
//!
//! ```text
//! cp probes/i5_census.rs crates/vilan-core/examples/i5_census.rs
//! cargo run --example i5_census -- <root.vl or dir> ... > census.tsv
//! ```
//!
//! It parses every `.vl` file it is given (directories are walked) with the
//! compiler's own `parsing::parse` and writes one TSV row per finding. No
//! grep: every row comes from an AST node, and the type text is the SOURCE
//! SLICE of the annotation's span.
//!
//! Row kinds:
//!   SIG     a function signature position (parameter or return) whose written
//!           type mentions a numeric scalar
//!   FIELD   a struct field whose written type mentions a numeric scalar
//!   LET     a `let` with a written type that mentions a numeric scalar
//!   NEG1    a `-1` literal (unary minus over the literal `1`)
//!   DEC     a `x -= <expr>` compound assignment (loop_depth says whether it is
//!           inside a `for`)
//!   FOR     a `for <cond>` loop header (the condition's source text)
//!   INDEX   a `subject[index]` subscript (the index expression's source text)
//!   LEN     a call whose callee's last member is `len` (the receiver's text)
//!   SUFFIX  a numeric literal written WITH a type suffix
//!
//! Columns: kind, file, line, owner (impl/trait subject or module), function,
//! position, text, extra.

use std::fmt::Write as _;
use std::path::{Path, PathBuf};

use vilan_core::node::{BinaryOp, Node, Parameter, Pattern};
use vilan_core::parsing;
use vilan_core::span::{Span, Spanned};

/// The scalar numeric type names a written annotation may mention. `usize` is
/// here so a re-run AFTER I5's S1/S2 counts the migration.
const SCALARS: &[&str] = &[
    "i8", "i16", "i32", "i53", "i64", "u8", "u16", "u32", "u53", "u64", "f32", "f64", "usize",
    "isize",
];

struct Context {
    file: String,
    source: String,
    line_starts: Vec<usize>,
    owner: Vec<String>,
    function: Vec<String>,
    loop_depth: u32,
    rows: Vec<String>,
}

impl Context {
    fn line(&self, span: Span) -> usize {
        match self.line_starts.binary_search(&span.start) {
            Ok(index) => index + 1,
            Err(index) => index,
        }
    }

    fn text(&self, span: Span) -> String {
        let slice = self
            .source
            .get(span.start..span.end)
            .unwrap_or("<span out of range>");
        slice.split_whitespace().collect::<Vec<_>>().join(" ")
    }

    fn row(&mut self, kind: &str, span: Span, position: &str, text: &str, extra: &str) {
        let line = self.line(span);
        let owner = self.owner.last().cloned().unwrap_or_default();
        let function = self.function.last().cloned().unwrap_or_default();
        let mut row = String::new();
        let _ = write!(
            row,
            "{kind}\t{}\t{line}\t{owner}\t{function}\t{position}\t{text}\t{extra}",
            self.file
        );
        self.rows.push(row);
    }
}

/// Every scalar the written type text mentions, as whole identifiers.
fn scalars_in(text: &str) -> Vec<&'static str> {
    let mut found = Vec::new();
    let bytes = text.as_bytes();
    for scalar in SCALARS {
        let mut from = 0;
        while let Some(at) = text[from..].find(scalar) {
            let start = from + at;
            let end = start + scalar.len();
            let before_ok = start == 0 || !is_word(bytes[start - 1]);
            let after_ok = end == bytes.len() || !is_word(bytes[end]);
            if before_ok && after_ok && !found.contains(scalar) {
                found.push(*scalar);
            }
            from = end;
        }
    }
    found
}

fn is_word(byte: u8) -> bool {
    byte.is_ascii_alphanumeric() || byte == b'_'
}

fn pattern_name(pattern: &Pattern<'_>) -> String {
    match pattern {
        Pattern::Binding(name, ..) => (*name).to_string(),
        Pattern::Wildcard => "_".to_string(),
        Pattern::Tuple(elements) => {
            let names: Vec<String> = elements.iter().map(|(p, _)| pattern_name(p)).collect();
            format!("({})", names.join(","))
        }
        _ => "<pattern>".to_string(),
    }
}

fn record_parameter(context: &mut Context, parameter: &Parameter<'_>) {
    let Some(declared) = parameter.declared_type.as_deref() else {
        return;
    };
    let text = context.text(declared.1);
    let scalars = scalars_in(&text);
    if scalars.is_empty() {
        return;
    }
    let name = pattern_name(&parameter.pattern);
    context.row("SIG", declared.1, &name, &text, &scalars.join("+"));
}

fn walk(context: &mut Context, node: &Spanned<Node<'_>>) {
    let mut pushed_owner = false;
    let mut pushed_function = false;
    let mut entered_loop = false;

    match &node.0 {
        Node::Func(function) | Node::MacroFun(function) => {
            let name = function.name.0.to_string();
            for parameter in &function.parameters.0 {
                let saved = context.function.clone();
                context.function.push(name.clone());
                record_parameter(context, parameter);
                context.function = saved;
            }
            if let Some(return_type) = function.return_type.as_deref() {
                let text = context.text(return_type.1);
                let scalars = scalars_in(&text);
                if !scalars.is_empty() {
                    let saved = context.function.clone();
                    context.function.push(name.clone());
                    context.row("SIG", return_type.1, "<ret>", &text, &scalars.join("+"));
                    context.function = saved;
                }
            }
            context.function.push(name);
            pushed_function = true;
        }
        Node::Impl(subject, traits, _) => {
            let subject_text = context.text(subject.1);
            let trait_text: Vec<String> = traits.iter().map(|t| context.text(t.1)).collect();
            let owner = if trait_text.is_empty() {
                format!("impl {subject_text}")
            } else {
                format!("impl {subject_text} with {}", trait_text.join("+"))
            };
            context.owner.push(owner);
            pushed_owner = true;
        }
        Node::Trait(name, ..) => {
            context.owner.push(format!("trait {}", name.0));
            pushed_owner = true;
        }
        Node::Struct(name, _, _, _, fields) => {
            let owner = format!("struct {}", name.0);
            for (field_name, declared, _) in fields.iter().flat_map(|fields| &fields.0).map(|f| &f.0)
            {
                let Some(declared) = declared else { continue };
                let text = context.text(declared.1);
                let scalars = scalars_in(&text);
                if scalars.is_empty() {
                    continue;
                }
                context.owner.push(owner.clone());
                context.row("FIELD", declared.1, field_name.0, &text, &scalars.join("+"));
                context.owner.pop();
            }
            context.owner.push(owner);
            pushed_owner = true;
        }
        Node::Let(name, Some(declared), ..) => {
            let text = context.text(declared.1);
            let scalars = scalars_in(&text);
            if !scalars.is_empty() {
                context.row("LET", declared.1, name.0, &text, &scalars.join("+"));
            }
        }
        Node::Unary('-', inner) => {
            if let Node::Number(whole, fraction, suffix) = &inner.0 {
                if *whole == "1" && fraction.is_none() {
                    let extra = suffix.unwrap_or("");
                    context.row("NEG1", node.1, "", "-1", extra);
                }
            }
        }
        Node::Number(_, _, Some(suffix)) => {
            let text = context.text(node.1);
            context.row("SUFFIX", node.1, "", &text, suffix);
        }
        Node::Assign(target, Some(BinaryOp::Sub), value) => {
            let target_text = context.text(target.1);
            let value_text = context.text(value.1);
            let depth = context.loop_depth;
            context.row("DEC", node.1, &target_text, &value_text, &depth.to_string());
        }
        Node::For(condition, _) => {
            let condition_text = condition
                .as_deref()
                .map(|condition| context.text(condition.1))
                .unwrap_or_else(|| "<infinite>".to_string());
            context.row("FOR", node.1, "", &condition_text, "");
            context.loop_depth += 1;
            entered_loop = true;
        }
        Node::ForIn(pattern, iterable, _) => {
            let binder = pattern_name(&pattern.0);
            let iterable_text = context.text(iterable.1);
            context.row("FOR", node.1, &binder, &iterable_text, "in");
            context.loop_depth += 1;
            entered_loop = true;
        }
        Node::Index(subject, index) => {
            let subject_text = context.text(subject.1);
            let index_text = context.text(index.1);
            let literal = matches!(index.0, Node::Number(..));
            context.row(
                "INDEX",
                node.1,
                &subject_text,
                &index_text,
                if literal { "literal" } else { "" },
            );
        }
        // `xs.len()` parses as MemberAccessor(xs, Call(Accessor("len"), ..)) —
        // the CALL is the member, not the callee.
        Node::MemberAccessor(receiver, member) => {
            if let Node::Call(callee, _, _) = &member.0 {
                if matches!(&callee.0, Node::Accessor(name) if *name == "len") {
                    let receiver_text = context.text(receiver.1);
                    context.row("LEN", node.1, &receiver_text, "len()", "");
                }
            }
        }
        _ => {}
    }

    let mut children: Vec<&Spanned<Node<'_>>> = Vec::new();
    node.0.for_each_child(&mut |child| children.push(child));
    for child in children {
        walk(context, child);
    }

    if pushed_owner {
        context.owner.pop();
    }
    if pushed_function {
        context.function.pop();
    }
    if entered_loop {
        context.loop_depth -= 1;
    }
}

fn census_file(path: &Path, label: &str, rows: &mut Vec<String>) {
    let Ok(source) = std::fs::read_to_string(path) else {
        eprintln!("unreadable: {}", path.display());
        return;
    };
    census_source(&source, label, rows);
}

fn census_source(source: &str, label: &str, rows: &mut Vec<String>) {
    let mut line_starts = vec![0usize];
    for (offset, byte) in source.bytes().enumerate() {
        if byte == b'\n' {
            line_starts.push(offset + 1);
        }
    }
    let (parsed, errors) = parsing::parse(source);
    if !errors.is_empty() {
        eprintln!("parse errors ({}): {label}", errors.len());
    }
    let Some(parsed) = parsed else {
        eprintln!("did not parse: {label}");
        return;
    };
    let mut context = Context {
        file: label.to_string(),
        source: source.to_string(),
        line_starts,
        owner: Vec::new(),
        function: Vec::new(),
        loop_depth: 0,
        rows: Vec::new(),
    };
    for item in &parsed.0 {
        walk(&mut context, item);
    }
    rows.append(&mut context.rows);
}

/// Every fenced ```vilan block in a markdown file, as its own pseudo-file.
fn census_markdown(path: &Path, label: &str, rows: &mut Vec<String>) {
    let Ok(text) = std::fs::read_to_string(path) else {
        return;
    };
    let mut in_fence = false;
    let mut block = String::new();
    let mut start_line = 0usize;
    for (index, line) in text.lines().enumerate() {
        let trimmed = line.trim_start();
        if !in_fence && (trimmed.starts_with("```vilan") || trimmed.starts_with("```vl")) {
            in_fence = true;
            block.clear();
            start_line = index + 2;
            continue;
        }
        if in_fence && trimmed.starts_with("```") {
            in_fence = false;
            census_source(&block, &format!("{label}#fence@{start_line}"), rows);
            continue;
        }
        if in_fence {
            block.push_str(line);
            block.push('\n');
        }
    }
}

/// The `.vl` program CONSTS inside Rust test files: any raw string literal
/// (`r#"…"#`) whose text parses as vilan AND names a `fun`/`struct`/`let`.
fn census_rust_consts(path: &Path, label: &str, rows: &mut Vec<String>) {
    let Ok(text) = std::fs::read_to_string(path) else {
        return;
    };
    let mut from = 0usize;
    while let Some(at) = text[from..].find("r#\"") {
        let start = from + at + 3;
        let Some(end_at) = text[start..].find("\"#") else {
            break;
        };
        let end = start + end_at;
        let block = &text[start..end];
        from = end + 2;
        if block.contains("fun ") || block.contains("struct ") || block.contains("let ") {
            let line = text[..start].bytes().filter(|byte| *byte == b'\n').count() + 1;
            census_source(block, &format!("{label}#const@{line}"), rows);
        }
    }
}

fn collect(path: &Path, base: &Path, files: &mut Vec<PathBuf>) {
    if path.is_dir() {
        let mut entries: Vec<PathBuf> = std::fs::read_dir(path)
            .into_iter()
            .flatten()
            .flatten()
            .map(|entry| entry.path())
            .collect();
        entries.sort();
        for entry in entries {
            let name = entry.file_name().and_then(|n| n.to_str()).unwrap_or("");
            if name == "target" || name == "node_modules" || name == ".git" || name == "dist" {
                continue;
            }
            collect(&entry, base, files);
        }
        return;
    }
    let extension = path.extension().and_then(|e| e.to_str()).unwrap_or("");
    if matches!(extension, "vl" | "md" | "rs") {
        files.push(path.to_path_buf());
    }
}

fn main() {
    let arguments: Vec<String> = std::env::args().skip(1).collect();
    if arguments.is_empty() {
        eprintln!("usage: i5_census <path> ...");
        std::process::exit(2);
    }
    let mut rows = Vec::new();
    for argument in &arguments {
        let root = PathBuf::from(argument);
        let mut files = Vec::new();
        collect(&root, &root, &mut files);
        for file in files {
            let label = file.display().to_string();
            match file.extension().and_then(|e| e.to_str()).unwrap_or("") {
                "vl" => census_file(&file, &label, &mut rows),
                "md" => census_markdown(&file, &label, &mut rows),
                "rs" => census_rust_consts(&file, &label, &mut rows),
                _ => {}
            }
        }
    }
    println!("kind\tfile\tline\towner\tfunction\tposition\ttext\textra");
    for row in rows {
        println!("{row}");
    }
}
