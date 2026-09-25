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
        Node::Impl(subject, traits, _, _) => {
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
        Node::Struct(name, _, _, _, fields, _) => {
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

/// Whether `written` is a whole expression on its own. A diagnostic's span is
/// not always one — a closure's return-position mismatch anchors at the
/// body's closing brace — and a conversion written after half an expression
/// is a syntax error, not a migration.
///
/// A MULTI-LINE value is declined as well: `(if … { … } else { … }).as_i32()`
/// parses, and it is the conversion a reviewer should see written by hand at
/// the arm or the binding instead.
fn parses_as_expression(written: &str) -> bool {
    if written.contains('\n') || written.trim() != written || written.ends_with('.') {
        return false;
    }
    let probe = format!("fun probe() {{\n\tlet value = ({written});\n}}\n");
    let (parsed, errors) = parsing::parse(&probe);
    parsed.is_some() && errors.is_empty()
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

/// The declaration to respell instead of converting at a use: when the value
/// a fix would convert to `usize` is a bare local name, and that name's
/// binding in the same function is `let`/`mut NAME = <unsuffixed integer>;`
/// with no annotation, the honest migration is `NAME: usize` at the binding —
/// the counter IS an index — not a `.as_usize()` at every use. Answers the
/// span to insert `: usize` at (the end of the name), or `None`.
fn literal_binding_of(source: &str, use_span: Span, written: &str) -> Option<Span> {
    let is_name = written
        .chars()
        .next()
        .is_some_and(|first| first.is_ascii_lowercase() || first == '_')
        && written.chars().all(|c| c.is_ascii_alphanumeric() || c == '_');
    if !is_name {
        return None;
    }
    let (parsed, _) = parsing::parse(source);
    let parsed = parsed?;
    // The innermost function around the use.
    fn enclosing<'a, 'src>(
        node: &'a Spanned<Node<'src>>,
        at: usize,
        found: &mut Option<&'a Spanned<Node<'src>>>,
    ) {
        if node.1.start <= at && at < node.1.end {
            if matches!(node.0, Node::Func(_) | Node::MacroFun(_)) {
                *found = Some(node);
            }
            node.0.for_each_child(&mut |child| enclosing(child, at, found));
        }
    }
    let mut function = None;
    for item in &parsed.0 {
        enclosing(item, use_span.start, &mut function);
    }
    let function = function?;
    fn declaration(node: &Spanned<Node<'_>>, name: &str, before: usize, best: &mut Option<Span>) {
        if let Node::Let(binding, None, Some(value), _, _, _) = &node.0
            && binding.0 == name
            && node.1.start < before
            && matches!(value.0, Node::Number(_, None, None))
        {
            *best = Some(binding.1);
        }
        node.0.for_each_child(&mut |child| declaration(child, name, before, best));
    }
    let mut best = None;
    declaration(function, written, use_span.start, &mut best);
    best
}

/// Whether `span` starts and ends on token boundaries of `source` — neither end
/// cuts an identifier in two. A re-reported macro-world span can index into
/// GENERATED text and land mid-name in the file it is attributed to (`quo|te(`);
/// no fix is written at such a span.
fn on_token_boundaries(source: &str, span: Span) -> bool {
    let bytes = source.as_bytes();
    let word = |byte: u8| byte.is_ascii_alphanumeric() || byte == b'_';
    let start_ok = span.start == 0
        || !(word(bytes[span.start - 1]) && bytes.get(span.start).copied().is_some_and(word));
    let end_ok = span.end >= bytes.len()
        || !(word(bytes[span.end]) && span.end > 0 && word(bytes[span.end - 1]));
    start_ok && end_ok
}

/// Whether `span` lies inside the body of a `macro fun` declared in `source`.
fn inside_macro_body(source: &str, span: Span) -> bool {
    let (parsed, _) = parsing::parse(source);
    let Some(parsed) = parsed else {
        return false;
    };
    fn search(node: &Spanned<Node<'_>>, span: Span) -> bool {
        if node.1.start > span.start || span.end > node.1.end {
            return false;
        }
        if matches!(node.0, Node::MacroFun(_)) {
            return true;
        }
        let mut found = false;
        node.0.for_each_child(&mut |child| found = found || search(child, span));
        found
    }
    parsed.0.iter().any(|item| search(item, span))
}

#[derive(Default)]
struct Round {
    /// Per file: (span, replacement, kind). The same std diagnostic arrives
    /// once per ENTRY that loads the module, so the counts below are taken
    /// after the per-file dedup, never from the raw reports.
    edits: BTreeMap<PathBuf, Vec<(Span, String, &'static str)>>,
    residue: BTreeSet<(String, usize, String)>,
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
        let text = std::fs::read_to_string(&path).unwrap_or_default();
        // A macro world compiles the `macro fun` bodies std declares (the
        // derives), hermetically — the program world never walks them, so their
        // errors arrive only re-reported, prefixed `in this macro:`. One whose
        // span sits inside a `macro fun` body of the file it names is a real
        // site in that body and is fixed like any other; the rest are echoes
        // (a failed definition, or a span into generated code) that fixing the
        // source they came from retires.
        let message = match message.strip_prefix("in this macro: ") {
            Some(inner) if inside_macro_body(&text, span) => inner.to_string(),
            Some(_) => {
                round.echoes += 1;
                continue;
            }
            None if message.contains("definition did not compile") => {
                round.echoes += 1;
                continue;
            }
            None => message,
        };
        let line = text[..span.start.min(text.len())].matches('\n').count() + 1;
        // E218's steer: the declared type names the conversion.
        if let Some(at) = message.find(NUMERIC_CONVERSION_STEER)
            && let Some(method) = message[at + NUMERIC_CONVERSION_STEER.len()..].strip_suffix("()`")
            && let Some(written) = text.get(span.start..span.end)
            && !written.is_empty()
            && on_token_boundaries(&text, span)
            && parses_as_expression(written)
        {
            if method == "as_usize"
                && let Some(name) = literal_binding_of(&text, span, written)
            {
                round.edits.entry(path.clone()).or_default().push((
                    Span::from(name.end..name.end),
                    ": usize".to_string(),
                    "DECL",
                ));
                continue;
            }
            round
                .edits
                .entry(path.clone())
                .or_default()
                .push((span, converted(written, method), "E218"));
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
                && on_token_boundaries(&text, operand)
                && parses_as_expression(written)
            {
                if let Some(name) = literal_binding_of(&text, operand, written) {
                    round.edits.entry(path.clone()).or_default().push((
                        Span::from(name.end..name.end),
                        ": usize".to_string(),
                        "DECL",
                    ));
                    continue;
                }
                round
                    .edits
                    .entry(path.clone())
                    .or_default()
                    .push((operand, converted(written, "as_usize"), "OPERAND"));
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
    let mut total_declarations = 0;
    for round_number in 1.. {
        // Entries are analyzed in parallel (each on its own large-stack
        // thread), then their reports merged: a round's answer is the union,
        // whatever order the analyses finished in.
        let parallelism = std::thread::available_parallelism()
            .map(|count| count.get().clamp(1, 6))
            .unwrap_or(2);
        let chunks: Vec<&[PathBuf]> = entries.chunks(entries.len().div_ceil(parallelism)).collect();
        let partials: Vec<Round> = std::thread::scope(|scope| {
            let handles: Vec<_> = chunks
                .into_iter()
                .map(|chunk| {
                    scope.spawn(move || {
                        let mut partial = Round::default();
                        for entry in chunk {
                            analyze_entry(std_dir, platform, entry, &mut partial);
                        }
                        partial
                    })
                })
                .collect();
            handles
                .into_iter()
                .map(|handle| handle.join().expect("an analysis worker"))
                .collect()
        });
        let mut round = Round::default();
        for partial in partials {
            for (path, edits) in partial.edits {
                round.edits.entry(path).or_default().extend(edits);
            }
            round.residue.extend(partial.residue);
            round.echoes += partial.echoes;
        }
        let mut applied = 0;
        let mut steered = 0;
        let mut operands = 0;
        let mut declarations = 0;
        for (path, mut edits) in std::mem::take(&mut round.edits) {
            // Declarations FIRST: a counter respelled `usize` retires every
            // conversion its uses would otherwise collect, so a file with any
            // declaration to make takes only those this round and is
            // re-analyzed before a single `.as_*()` is written into it.
            if edits.iter().any(|(_, _, kind)| *kind == "DECL") {
                edits.retain(|(_, _, kind)| *kind == "DECL");
            }
            edits.sort_by_key(|(span, _, _)| (span.start, span.end));
            edits.dedup_by_key(|(span, _, _)| (span.start, span.end));
            let source = std::fs::read_to_string(&path).expect("read an edited file");
            for (span, replacement, kind) in &edits {
                let line = source[..span.start].matches('\n').count() + 1;
                println!(
                    "FIX\t{kind}\t{}\t{line}\t{}\t{}",
                    path.display(),
                    source[span.start..span.end].replace('\n', "⏎"),
                    replacement.replace('\n', "⏎")
                );
            }
            applied += edits.len();
            steered += edits.iter().filter(|(_, _, kind)| *kind == "E218").count();
            operands += edits.iter().filter(|(_, _, kind)| *kind == "OPERAND").count();
            declarations += edits.iter().filter(|(_, _, kind)| *kind == "DECL").count();
            let plain: Vec<(Span, String)> =
                edits.into_iter().map(|(span, text, _)| (span, text)).collect();
            std::fs::write(&path, apply(&source, plain)).expect("write an edited file");
        }
        total_steered += steered;
        total_operands += operands;
        total_declarations += declarations;
        eprintln!(
            "round {round_number}: {applied} edits applied ({steered} conversions named by E218, {operands} operands, {declarations} counters declared `usize`), {} residue, {} macro-world echoes",
            round.residue.len(),
            round.echoes
        );
        if applied == 0 {
            for (path, line, message) in &round.residue {
                println!("RESIDUE\t{path}\t{line}\t{message}");
            }
            eprintln!(
                "fixed point: {total_steered} E218 conversions, {total_operands} operand conversions, {total_declarations} counters declared `usize`, {} residue diagnostics",
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
