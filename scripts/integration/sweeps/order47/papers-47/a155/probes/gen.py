import sys
cases = [
 ("a1_attr_then_styled", '<div class("x") .styled(card) />'),
 ("a2_styled_then_attr", '<div .styled(card) class("x") />'),
 ("a3_two_styled", '<div .styled(card) .styled(wide) />'),
 ("a4_composed", '<div .styled(card + wide) />'),
 ("a5_styled_then_bind_class", '<div .styled(card) .bind_class(flag.derive(|on| if on { "on" } else { "" })) />'),
 ("a6_styled_then_bind_attr_class", '<div .styled(card) .bind_attr("class", flag.derive(|on| if on { "on" } else { "off" })) />'),
 ("a7_helper_then_class", 'boxed().class("x")'),
 ("a8_decorator", 'decorate(<div class("x") />)'),
 ("a9_postfix_on_element", '<div .styled(card) />.class("x")'),
 ("a10_class_then_class", 'view("div").class("a").class("b")'),
 ("a11_reactive_attr_class", '<div class(label) .styled(card) />'),
 ("a12_styled_then_toggle_attr_class", '<div .styled(card) .toggle_attr("class", flag) />'),
 ("a13_bind_styled_then_class", '<div .bind_styled(flag.derive(|on| if on { card } else { wide })) class("x") />'),
]
head = '''import std::web::ui::{ View, view, render };
import std::web::style::Style;
import std::reactive::{ Signal, SignalCell };

let card = const css { padding("4px"); color("red"); };
let wide = const css { width("100%"); color("blue"); };

fun boxed(): View { <div .styled(card) /> }
fun decorate(v: View): View { v.styled(wide) }

fun main() {
	let flag = Signal::new(true);
	let label = Signal::new("lbl");
	let v = BODY;
	print(render(v));
}
'''
for name, body in cases:
    open(f"{name}.vl", "w").write(head.replace("BODY", body))
# browser variants: no render (the browser twin mounts); the DOM stub reports
bhead = head.replace("import std::web::ui::{ View, view, render };", "import std::web::ui::{ View, view, mount_root };").replace("\tlet v = BODY;\n\tprint(render(v));\n", "\tlet _owner = mount_root(\"app\", || BODY);\n\tflag.set(false);\n\tlabel.set(\"lbl2\");\n")
for name, body in cases:
    open(f"b_{name}.vl", "w").write(bhead.replace("BODY", body))
