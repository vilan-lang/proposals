// papers-b-48 census: a read-only syntactic walk over .vl files with the
// tree's own parser (vilan-core @ the worktree's HEAD). Prints one line per
// finding: KIND<TAB>file:line<TAB>detail<TAB>source-snippet.
use std::collections::BTreeMap;
use vilan_core::lexing;
use vilan_core::node::Node;
use vilan_core::parsing;
use vilan_core::span::Spanned;
use vilan_core::token::Token;

fn tok_str(t: &Token) -> String {
    format!("{t}")
}

fn line_of(src: &str, off: usize) -> usize {
    src[..off.min(src.len())].bytes().filter(|b| *b == b'\n').count() + 1
}

fn snippet(src: &str, s: usize, e: usize) -> String {
    let e = e.min(src.len());
    let mut t: String = src[s..e].chars().take(90).collect();
    t = t.replace('\n', " ").replace('\t', " ");
    t
}

struct Ctx<'a> {
    file: &'a str,
    src: &'a str,
    toks: Vec<(Token<'a>, usize, usize)>,
    counts: BTreeMap<String, usize>,
    export_all: bool,
}

impl<'a> Ctx<'a> {
    fn prev_tok(&self, start: usize) -> String {
        // the last token ending at or before start
        let mut best: Option<&(Token, usize, usize)> = None;
        for t in &self.toks {
            if t.2 <= start {
                best = Some(t);
            } else {
                break;
            }
        }
        best.map(|t| tok_str(&t.0)).unwrap_or_else(|| "<bof>".into())
    }
    fn next_tok(&self, end: usize) -> String {
        for t in &self.toks {
            if t.1 >= end {
                return tok_str(&t.0);
            }
        }
        "<eof>".into()
    }
    fn bump(&mut self, k: String) {
        *self.counts.entry(k).or_default() += 1;
    }
    fn emit(&mut self, kind: &str, s: usize, e: usize, detail: &str) {
        println!(
            "{kind}\t{}:{}\t{detail}\t{}",
            self.file,
            line_of(self.src, s),
            snippet(self.src, s, e)
        );
    }
}

fn classify_assign(prev: &str, next: &str) -> &'static str {
    match (prev, next) {
        ("{" | ";" | "}" | "<bof>" | "]", ";") => "statement",
        ("{" | ";" | "}" | "]", "}") => "block-tail",
        ("=>", _) => "match-arm-or-comprehension-body",
        ("|" | "||", _) => "closure-body",
        ("then" | "else", _) => "then-else-branch",
        ("(", ")") => "parenthesized",
        ("(", _) | (",", _) => "argument-or-tuple-entry",
        ("=" | "+=" | "-=" | "*=" | "/=" | "%=", _) => "right-of-assignment-or-let",
        _ => "other",
    }
}

fn walk<'a>(cx: &mut Ctx<'a>, node: &Spanned<Node<'a>>, top: bool, under_export: bool, in_impl: bool) {
    let (n, sp) = node;
    match n {
        Node::Assign(_, _, _) => {
            let prev = cx.prev_tok(sp.start);
            let next = cx.next_tok(sp.end);
            let class = classify_assign(&prev, &next);
            cx.bump(format!("assign.{class}"));
            if class != "statement" {
                cx.emit(&format!("ASSIGN.{class}"), sp.start, sp.end, &format!("prev={prev} next={next}"));
            }
        }
        Node::LiftGroup(inner) => {
            if let Node::Assign(..) = &inner.0 {
                cx.bump("assign.in-group".into());
                cx.emit("ASSIGN.GROUP", sp.start, sp.end, "");
            }
        }
        Node::Tuple(items) => {
            cx.bump(format!("tuple.arity{}", items.len()));
        }
        Node::LetDestructure(..) => cx.bump("let-destructure".into()),
        Node::MemberAccessor(_, member) => {
            if let Node::Number(..) = member.0 {
                cx.bump("tuple-index-access".into());
            }
        }
        Node::Func(_) | Node::Let(..) if in_impl => {
            count_item(cx, node, "method", top);
        }
        Node::Func(_) | Node::Let(..) => {
            let ex = if under_export || cx.export_all { "exported" } else { "private" };
            count_item(cx, node, ex, top);
        }
        _ => {}
    }
    let mut kids: Vec<&Spanned<Node<'a>>> = Vec::new();
    n.for_each_child(&mut |c| kids.push(c));
    let child_top = matches!(n, Node::Module(..)) || (top && matches!(n, Node::Export(..)));
    let child_export = matches!(n, Node::Export(..));
    let child_impl = matches!(n, Node::Impl(..) | Node::Trait(..));
    for k in kids {
        walk(cx, k, child_top, child_export, child_impl);
    }
}

fn count_item<'a>(cx: &mut Ctx<'a>, node: &Spanned<Node<'a>>, ex: &str, top: bool) {
    match &node.0 {
        Node::Func(f) if !f.external && f.body.is_some() => {
            let has_rt = f.return_type.is_some();
            let tail_void = f
                .body
                .as_ref()
                .map(|b| matches!((b.0).1.0, Node::Void))
                .unwrap_or(true);
            let k = match (has_rt, tail_void) {
                (true, _) => "written",
                (false, true) => "omitted-void-tail",
                (false, false) => "omitted-value-tail",
            };
            cx.bump(format!("fun.{ex}.{k}"));
        }
        Node::Let(_, ty, val, _, _, _) if top => {
            let k = if ty.is_some() { "written" } else if val.is_some() { "inferred" } else { "none" };
            cx.bump(format!("modlet.{ex}.{k}"));
        }
        _ => {}
    }
}

fn main() {
    let mut total: BTreeMap<String, usize> = BTreeMap::new();
    let mut parse_fail = 0;
    let mut files = 0;
    for path in std::env::args().skip(1) {
        let src = match std::fs::read_to_string(&path) {
            Ok(s) => s,
            Err(_) => continue,
        };
        files += 1;
        let (toks, _) = lexing::tokenize(&src);
        let toks: Vec<(Token, usize, usize)> =
            toks.into_iter().map(|(t, s)| (t, s.start, s.end)).collect();
        // `as` tokens (an Ident) with their neighbours
        let mut as_ctx = Vec::new();
        for (i, t) in toks.iter().enumerate() {
            if let Token::Ident("as") = t.0 {
                let prev = if i > 0 { tok_str(&toks[i - 1].0) } else { "<bof>".into() };
                let next = toks.get(i + 1).map(|t| tok_str(&t.0)).unwrap_or_default();
                as_ctx.push((t.1, prev, next));
            }
        }
        let (tree, errors) = parsing::parse_preserving_groups(&src);
        let mut cx = Ctx { file: &path, src: &src, toks, counts: BTreeMap::new(), export_all: false };
        for (off, prev, next) in as_ctx {
            cx.bump("as-token".into());
            println!("AS\t{}:{}\tprev={prev} next={next}\t{}", path, line_of(&src, off), snippet(&src, off.saturating_sub(30), off + 30));
        }
        if !errors.is_empty() {
            parse_fail += 1;
            println!("PARSE-ERRORS\t{path}\t{}", errors.len());
        }
        if let Some((list, _)) = tree {
            cx.export_all = list.iter().any(|n| matches!(n.0, Node::ExportAll));
            for item in &list {
                walk(&mut cx, item, true, false, false);
            }
        }
        for (k, v) in cx.counts {
            *total.entry(k).or_default() += v;
        }
    }
    println!("TOTAL\tfiles={files} parse_fail={parse_fail}");
    for (k, v) in total {
        println!("TOTAL\t{k}\t{v}");
    }
}
