#!/usr/bin/env bash
# A155 runtime census: a COPY of std (beside a copy of macro_std, which a moved
# std needs) whose class writers report a second class write on one element via
# console.trace: the process twin at its shared `set_attribute`, the browser twin
# at each writer's entry (`has_attribute("class")`). Point a build at it with
# VILAN_STD=<out>/std. Usage: instrument_std.sh <vilan checkout>/vilan <out>
set -eu
SRC=${1:?vilan dir}; OUT=${2:?out}
mkdir -p "$OUT"; cp -r "$SRC/std" "$OUT/std"; cp -r "$SRC/macro_std" "$OUT/macro_std"
cd "$OUT/std/src" && python3 - <<'PY'
p = "process/web/ui.vl"; s = open(p).read()
old = """	if !found {
		updated.push(Attribute { name, value });
	}
	attributes.write() = updated;
}"""
assert old in s
s = s.replace(old, old[:-len("	attributes.write() = updated;\n}")] + """	if found && name == "class" {
		a155_trace("A155-DOUBLE ssr: class written again -> \\"" + value + "\\"");
	}
	attributes.write() = updated;
}

[extern("console.trace")]
external fun a155_trace(message: str): void;""")
open(p, "w").write(s)
p = "browser/web/ui.vl"; s = open(p).read()
for fn, tag in [("fun class(self, name: str): View {", "class"), ("fun styled(self, style: Style): View {", "styled"),
                ("fun bind_class<S: Flow<str>>(self, own source: S): View {", "bind_class"),
                ("fun bind_styled<S: Flow<Style>>(self, own source: S): View {", "bind_styled")]:
    assert fn in s
    s = s.replace(fn, fn + f'\n\t\ta155_check(self.element, "{tag}");', 1)
for head, tag in [("	fun attr<V: AttrValue>(self, name: str, own value: V): View {\n", "attr(class)"),
                  ("	fun bind_attr<V: AttrBinding>(self, name: str, own source: V): View {\n", "bind_attr(class)")]:
    assert head in s
    s = s.replace(head, head + f'\t\tif name == "class" {{\n\t\t\ta155_check(self.element, "{tag}");\n\t\t}}\n', 1)
s += """

[extern("console.trace")]
external fun a155_trace(message: str): void;

fun a155_check(element: Element, writer: str) {
	if element.has_attribute("class") {
		a155_trace("A155-DOUBLE client: " + writer + " over an earlier class writer");
	}
}
"""
open(p, "w").write(s)
PY
echo "instrumented std at $OUT/std"
