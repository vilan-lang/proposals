//! I5 S2's codemod (Order 41, lane index-41) — `proposal/index-type.md` §8.1.
//!
//! NOT A101's text rewriter. The sites that change are decided by TYPE, not
//! by text, so this is two passes over the compiler's own answers:
//!
//! 1. `signatures` — the 105 std positions the census VERDICT table
//!    (`sweeps/order40/papers-40/i5-std-index-sites.tsv`, rows `INDEX`) names
//!    are located BY PARSE (the compiler's own `parsing::parse`, walked with
//!    `Node::for_each_child`, the same owner/function naming the census used)
//!    and keyed by (kind, module, owner, function, position, written type) —
//!    never by line, because lines drift between the census's base and the
//!    tree this runs on. In each located annotation the word `i32` becomes
//!    `usize`; every other word is untouched (`Option<i32>` →
//!    `Option<usize>`, `List<(i32, str)>` → `List<(usize, str)>`). A verdict
//!    row that matches nothing is reported and fails the run: a codemod that
//!    silently skipped a position is the one failure this pass exists to
//!    prevent.
//!
//! 2. `fix` — the fixed-point loop §8.1 recommends, over the compiler's own
//!    diagnostics. Every entry program is analyzed through the library
//!    (`analyze_source`, so a diagnostic arrives with its FILE and its BYTE
//!    SPAN — std's own files included); the diagnostics that carry a
//!    mechanical fix are applied; the loop repeats until a round applies
//!    nothing. Two families carry one:
//!    - E218's steer (`… There are no implicit numeric conversions; convert
//!      with `.as_X()``): the conversion the message names, written after the
//!      value its span covers, parenthesized unless the value is already a
//!      postfix operand — the language server's quick fix, applied in bulk.
//!      This is where a WIRE, STREAM or SEQUENCE position meets an index: the
//!      declared type decides the direction, so `begin_list(xs.len())`
//!      becomes `begin_list(xs.len().as_i32())` and the wire width stays.
//!    - the binary-operator refusal (ledger 357's family: "`<` compares two
//!      values of the same type, but the operands are `usize` and `i32`"),
//!      when one operand is `usize` and the other another integer width: the
//!      NON-index operand converts to `usize`. The direction is the
//!      migration's (an index met a non-index; the index wins), and the
//!      operand is found by parse — the `Binary` node whose span is the
//!      diagnostic's.
//!    Everything else is RESIDUE: printed, never guessed at. The sentinels
//!    (§3.4) and the `>= 0` loops (§3.5) are refused here by construction —
//!    none of them is a type error the compiler can see, which is exactly why
//!    §8.1 hands them to a human (NOTES.md names each).
//!
//! Run as a `vilan-core` example over a SCRATCH copy of the tree:
//!
//! ```text
//! cp i5_s2_codemod.rs <scratch>/crates/vilan-core/examples/
//! cargo run --example i5_s2_codemod -- signatures <verdicts.tsv> <scratch>/vilan/std/src
//! cargo run --example i5_s2_codemod -- fix <scratch>/vilan/std <platform> <entry.vl>...
//! ```
//!
//! `platform` is `node` or `browser`; each entry is analyzed on its own, with
//! its own directory as the package root.

use std::collections::{BTreeMap, BTreeSet};
use std::path::{Path, PathBuf};

use vilan_core::analyzer::NUMERIC_CONVERSION_STEER;
use vilan_core::node::{Node, Pattern};
use vilan_core::span::{Span, Spanned};
use vilan_core::target::Platform;
use vilan_core::{Workspace, analyze_source, parsing};

// --- pass 1: the signatures -------------------------------------------------------

/// One `INDEX` row of the verdict table.
#[derive(Clone, Debug, PartialEq, Eq, PartialOrd, Ord)]
struct Site {
    kind: String,
    module: String,
    owner: String,
    function: String,
    position: String,
    written: String,
}

fn read_sites(verdicts: &Path) -> Vec<Site> {
    let text = std::fs::read_to_string(verdicts).expect("read the verdict table");
    let mut sites = Vec::new();
    for line in text.lines().skip(1) {
        let columns: Vec<&str> = line.split('\t').collect();
        if columns.len() < 8 || columns[0] != "INDEX" {
            continue;
        }
        sites.push(Site {
            kind: columns[1].to_string(),
            module: columns[2].to_string(),
            owner: columns[4].to_string(),
            function: columns[5].to_string(),
            position: columns[6].to_string(),
            written: columns[7].to_string(),
        });
    }
    sites
}

/// A declared-type annotation the walk met, keyed the way the census keyed it.
struct Annotation {
    site: Site,
    span: Span,
}

struct Walk<'a> {
    module: String,
    source: &'a str,
    owner: Vec<String>,
    function: Vec<String>,
    found: Vec<Annotation>,
}

impl Walk<'_> {
    fn text(&self, span: Span) -> String {
        let slice = self.source.get(span.start..span.end).unwrap_or("");
        slice.split_whitespace().collect::<Vec<_>>().join(" ")
    }

    fn record(&mut self, kind: &str, span: Span, position: &str) {
        let written = self.text(span);
        if !has_word(&written, "i32") {
            return;
        }
        self.found.push(Annotation {
            site: Site {
                kind: kind.to_string(),
                module: self.module.clone(),
                owner: self.owner.last().cloned().unwrap_or_default(),
                function: self.function.last().cloned().unwrap_or_default(),
                position: position.to_string(),
                written,
            },
            span,
        });
    }
}

fn has_word(text: &str, word: &str) -> bool {
    word_offsets(text, word).next().is_some()
}

/// The byte offsets at which `word` occurs in `text` as a whole identifier.
fn word_offsets<'a>(text: &'a str, word: &'a str) -> impl Iterator<Item = usize> + 'a {
    let bytes = text.as_bytes();
    let is_word = |byte: u8| byte.is_ascii_alphanumeric() || byte == b'_';
    text.match_indices(word).map(|(at, _)| at).filter(move |&at| {
        let end = at + word.len();
        (at == 0 || !is_word(bytes[at - 1])) && (end == bytes.len() || !is_word(bytes[end]))
    })
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

fn walk(context: &mut Walk<'_>, node: &Spanned<Node<'_>>) {
    let mut pushed_owner = false;
    let mut pushed_function = false;
    match &node.0 {
        Node::Func(function) | Node::MacroFun(function) => {
            let name = function.name.0.to_string();
            context.function.push(name.clone());
            for parameter in &function.parameters.0 {
                if let Some(declared) = parameter.declared_type.as_deref() {
                    let position = pattern_name(&parameter.pattern);
                    context.record("SIG", declared.1, &position);
                }
            }
            if let Some(return_type) = function.return_type.as_deref() {
                context.record("SIG", return_type.1, "<ret>");
            }
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
            context.owner.push(owner);
            for field in fields.iter().flat_map(|fields| &fields.0) {
                let (field_name, declared, ..) = &field.0;
                if let Some(declared) = declared {
                    context.record("FIELD", declared.1, field_name.0);
                }
            }
            pushed_owner = true;
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
}

fn vl_files(root: &Path, files: &mut Vec<PathBuf>) {
    let mut entries: Vec<PathBuf> = std::fs::read_dir(root)
        .into_iter()
        .flatten()
        .flatten()
        .map(|entry| entry.path())
        .collect();
    entries.sort();
    for entry in entries {
        if entry.is_dir() {
            vl_files(&entry, files);
        } else if entry.extension().is_some_and(|extension| extension == "vl") {
            files.push(entry);
        }
    }
}

fn signatures(verdicts: &Path, std_src: &Path) {
    let sites = read_sites(verdicts);
    let wanted: BTreeSet<&Site> = sites.iter().collect();
    let mut matched: BTreeSet<Site> = BTreeSet::new();
    let mut files = Vec::new();
    vl_files(std_src, &mut files);
    let mut rewritten = 0usize;
    for file in files {
        let source = std::fs::read_to_string(&file).expect("read a std file");
        let module = file.file_name().unwrap().to_string_lossy().into_owned();
        let (parsed, _) = parsing::parse(&source);
        let Some(parsed) = parsed else {
            eprintln!("did not parse: {}", file.display());
            continue;
        };
        let mut context = Walk {
            module,
            source: &source,
            owner: Vec::new(),
            function: Vec::new(),
            found: Vec::new(),
        };
        for item in &parsed.0 {
            walk(&mut context, item);
        }
        let mut edits: Vec<(Span, String)> = Vec::new();
        for annotation in context.found {
            if !wanted.contains(&annotation.site) {
                continue;
            }
            let written = &source[annotation.span.start..annotation.span.end];
            let mut replacement = String::with_capacity(written.len() + 8);
            let mut cursor = 0;
            for at in word_offsets(written, "i32").collect::<Vec<_>>() {
                replacement.push_str(&written[cursor..at]);
                replacement.push_str("usize");
                cursor = at + 3;
            }
            replacement.push_str(&written[cursor..]);
            println!(
                "SIG-REWRITE\t{}\t{}\t{}\t{}\t{}\t{} -> {}",
                annotation.site.kind,
                annotation.site.module,
                annotation.site.owner,
                annotation.site.function,
                annotation.site.position,
                annotation.site.written,
                replacement.split_whitespace().collect::<Vec<_>>().join(" ")
            );
            matched.insert(annotation.site.clone());
            edits.push((annotation.span, replacement));
        }
        rewritten += edits.len();
        if !edits.is_empty() {
            let updated = apply(&source, edits);
            std::fs::write(&file, updated).expect("write a std file");
        }
    }
    let missing: Vec<&Site> = sites.iter().filter(|site| !matched.contains(*site)).collect();
    eprintln!(
        "signatures: {} verdict rows, {} annotations rewritten, {} rows unmatched",
        sites.len(),
        rewritten,
        missing.len()
    );
    for site in &missing {
        eprintln!("  UNMATCHED {site:?}");
    }
    if !missing.is_empty() {
        std::process::exit(1);
    }
}

/// Applies non-overlapping `(span, replacement)` edits to `source`, last first.
fn apply(source: &str, mut edits: Vec<(Span, String)>) -> String {
    edits.sort_by_key(|(span, _)| std::cmp::Reverse((span.start, span.end)));
    let mut text = source.to_string();
    let mut floor = usize::MAX;
    for (span, replacement) in edits {
        if span.end > floor {
            continue; // overlaps an edit already applied; the next round sees it
        }
        text.replace_range(span.start..span.end, &replacement);
        floor = span.start;
    }
    text
}

// --- pass 2: the fixed-point loop over the diagnostics ------------------------------

/// Whether `written` takes a method call as it stands (the language server's
/// rule, `document.rs`'s `is_postfix_operand`).
fn is_postfix_operand(written: &str) -> bool {
    if !written
        .chars()
        .next()
        .is_some_and(|first| first.is_alphabetic() || first == '_')
    {
        return false;
    }
    let mut depth = 0usize;
    let mut in_string = false;
    let mut escaped = false;
    for character in written.chars() {
        if in_string {
            match character {
                _ if escaped => escaped = false,
                '\\' => escaped = true,
                '"' => in_string = false,
                _ => {}
            }
            continue;
        }
        match character {
            '"' => in_string = true,
            '(' | '[' | '{' => depth += 1,
            ')' | ']' | '}' => match depth.checked_sub(1) {
                Some(outer) => depth = outer,
                None => return false,
            },
            _ if depth > 0 => {}
            _ if character.is_alphanumeric() || matches!(character, '_' | '.' | '?') => {}
            _ => return false,
        }
    }
    depth == 0 && !in_string
}

fn converted(written: &str, method: &str) -> String {
    if is_postfix_operand(written) {
        format!("{written}.{method}()")
    } else {
        format!("({written}).{method}()")
    }
}

const INTEGER_WIDTHS: &[&str] = &["i8", "u8", "i16", "u16", "i32", "u32", "i53", "u53"];

/// The two operand types a binary-operator refusal names, when it is one.
fn binary_operands(message: &str) -> Option<(String, String)> {
    let rest = message.split("but the operands are `").nth(1)?;
    let (left, rest) = rest.split_once("` and `")?;
    let (right, _) = rest.split_once('`')?;
    Some((left.to_string(), right.to_string()))
}

/// The right or left operand span of the `Binary` node whose span is `span`.
fn operand_span(source: &str, span: Span, left: bool) -> Option<Span> {
    let (parsed, _) = parsing::parse(source);
    let parsed = parsed?;
    fn find(node: &Spanned<Node<'_>>, span: Span, left: bool) -> Option<Span> {
        if let Node::Binary(_, lhs, rhs) = &node.0
            && node.1.start == span.start
            && node.1.end == span.end
        {
            return Some(if left { lhs.1 } else { rhs.1 });
        }
        let mut found = None;
        node.0.for_each_child(&mut |child| {
            if found.is_none() && child.1.start <= span.start && span.end <= child.1.end {
                found = find(child, span, left);
            }
        });
        found
    }
    parsed.0.iter().find_map(|item| find(item, span, left))
}

#[derive(Default)]
struct Round {
    edits: BTreeMap<PathBuf, Vec<(Span, String)>>,
    residue: BTreeSet<(String, usize, String)>,
    steered: usize,
    operands: usize,
    echoes: usize,
}

fn analyze_entry(std_dir: &Path, platform: Platform, entry: &Path, round: &mut Round) {
    let source = std::fs::read_to_string(entry).expect("read an entry");
    let leaked: &'static str = Box::leak(source.into_boxed_str());
    let root = entry.parent().unwrap_or(Path::new(".")).to_path_buf();
    let std_spec = vilan_core::manifest::resolve_std(std_dir);
    let entry = entry.to_path_buf();
    let result = std::thread::Builder::new()
        .stack_size(512 * 1024 * 1024)
        .spawn(move || {
            let (program, diagnostics) = analyze_source(
                leaked,
                &std_spec,
                &root,
                &entry,
                Some(platform),
                &Workspace::default(),
            );
            let mut located = Vec::new();
            for (index, error) in diagnostics.iter().enumerate() {
                let path = program
                    .as_ref()
                    .and_then(|program| {
                        program
                            .source_path(program.diagnostic_source(index))
                            .map(Path::to_path_buf)
                    })
                    .unwrap_or_else(|| entry.clone());
                located.push((path, error.span, error.msg.clone()));
            }
            located
        })
        .expect("spawn the analysis")
        .join()
        .expect("the analysis thread");
    for (path, span, message) in result {
        // A macro world compiles std a second time, and re-reports std's own
        // errors prefixed `in this macro:` at the INVOCATION. Fixing std fixes
        // them; editing at the invocation would be editing the wrong file.
        if message.starts_with("in this macro:") || message.contains("definition did not compile")
        {
            round.echoes += 1;
            continue;
        }
        let text = std::fs::read_to_string(&path).unwrap_or_default();
        let line = text[..span.start.min(text.len())].matches('\n').count() + 1;
        // E218's steer: the declared type names the conversion.
        if let Some(at) = message.find(NUMERIC_CONVERSION_STEER)
            && let Some(method) = message[at + NUMERIC_CONVERSION_STEER.len()..].strip_suffix("()`")
            && let Some(written) = text.get(span.start..span.end)
            && !written.is_empty()
        {
            round
                .edits
                .entry(path.clone())
                .or_default()
                .push((span, converted(written, method)));
            round.steered += 1;
            continue;
        }
        // The binary-operator refusal between `usize` and another integer
        // width: the non-index operand converts to `usize`.
        if let Some((left, right)) = binary_operands(&message) {
            let other_is_integer = |name: &str| INTEGER_WIDTHS.contains(&name);
            let convert_left = match (left.as_str(), right.as_str()) {
                ("usize", other) if other_is_integer(other) => Some(false),
                (other, "usize") if other_is_integer(other) => Some(true),
                _ => None,
            };
            if let Some(convert_left) = convert_left
                && let Some(operand) = operand_span(&text, span, convert_left)
                && let Some(written) = text.get(operand.start..operand.end)
            {
                round
                    .edits
                    .entry(path.clone())
                    .or_default()
                    .push((operand, converted(written, "as_usize")));
                round.operands += 1;
                continue;
            }
        }
        round
            .residue
            .insert((path.display().to_string(), line, message.replace('\n', " ")));
    }
}

fn fix(std_dir: &Path, platform: &str, entries: &[PathBuf]) {
    let platform = match platform {
        "node" => Platform::Node {
            version: vilan_core::target::NODE_LTS,
        },
        "browser" => Platform::Browser,
        other => panic!("unknown platform {other}"),
    };
    let mut total_steered = 0;
    let mut total_operands = 0;
    for round_number in 1.. {
        let mut round = Round::default();
        for entry in entries {
            analyze_entry(std_dir, platform, entry, &mut round);
        }
        let mut applied = 0;
        for (path, mut edits) in std::mem::take(&mut round.edits) {
            edits.sort_by_key(|(span, _)| (span.start, span.end));
            edits.dedup_by_key(|(span, _)| (span.start, span.end));
            applied += edits.len();
            let source = std::fs::read_to_string(&path).expect("read an edited file");
            for (span, replacement) in &edits {
                let line = source[..span.start].matches('\n').count() + 1;
                println!(
                    "FIX\t{}\t{line}\t{}\t{}",
                    path.display(),
                    source[span.start..span.end].replace('\n', "⏎"),
                    replacement.replace('\n', "⏎")
                );
            }
            std::fs::write(&path, apply(&source, edits)).expect("write an edited file");
        }
        total_steered += round.steered;
        total_operands += round.operands;
        eprintln!(
            "round {round_number}: {} edits applied ({} conversions named by E218, {} operands), {} residue, {} macro-world echoes",
            applied,
            round.steered,
            round.operands,
            round.residue.len(),
            round.echoes
        );
        if applied == 0 {
            for (path, line, message) in &round.residue {
                println!("RESIDUE\t{path}\t{line}\t{message}");
            }
            eprintln!(
                "fixed point: {total_steered} E218 conversions, {total_operands} operand conversions, {} residue diagnostics",
                round.residue.len()
            );
            return;
        }
    }
}

fn main() {
    let arguments: Vec<String> = std::env::args().skip(1).collect();
    match arguments.first().map(String::as_str) {
        Some("signatures") if arguments.len() == 3 => {
            signatures(Path::new(&arguments[1]), Path::new(&arguments[2]));
        }
        Some("fix") if arguments.len() >= 4 => {
            let entries: Vec<PathBuf> = arguments[3..].iter().map(PathBuf::from).collect();
            fix(Path::new(&arguments[1]), &arguments[2], &entries);
        }
        _ => {
            eprintln!(
                "usage: i5_s2_codemod signatures <verdicts.tsv> <std/src>\n       \
                 i5_s2_codemod fix <std dir> <node|browser> <entry.vl>..."
            );
            std::process::exit(2);
        }
    }
}
