#!/usr/bin/env python3
"""merge_tools_harness.py [--tools DIR] — the pins for N81's three shapes plus the union step.

Each case builds a throwaway git repository with a BASE commit, a HEAD branch and a LANE branch,
runs the tool the way `merge_fold.sh` / `merge_lane.sh` run it, and asserts on the resolved file.
Nothing here touches the vilan checkout. Run it as `python3 merge_tools_harness.py`; it prints one
line per case and exits non-zero on the first failure.

The four shapes (tracker N81, Order 35's finds):
  1. the `"\\` continuation  — a multi-line string const whose body lines sit at column 0 and
                               spell `struct`/`impl`/`//` there (visibility-a-35's merge).
  2. the renamed-on-HEAD test — a fn in BASE and the lane but gone from HEAD is not resurrected.
  3. the edited const        — a lane's edit to an existing const is refused, and taken under
                               --allow-edit, rather than dropped in silence.
  4. the duplicate constant  — two lanes bumping one scalar `const N: usize = …;` resolve to one
                               line, not two (Order 35, `RULE_STATEMENT_SITES` 28 and 29).
"""
import os, shutil, subprocess, sys, tempfile

TOOLS = os.path.dirname(os.path.abspath(__file__))
if "--tools" in sys.argv: TOOLS = os.path.abspath(sys.argv[sys.argv.index("--tools") + 1])
FAILURES = []

def run(cmd, cwd, check=True, env=None):
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True,
                            env={**os.environ, **(env or {})})
    if check and result.returncode != 0:
        raise AssertionError(f"{cmd} failed in {cwd}:\n{result.stdout}\n{result.stderr}")
    return result

def repo(files):
    """A fresh repository with `files` (path → text) committed on `base`."""
    root = tempfile.mkdtemp(prefix="n81_")
    run(["git", "init", "-q", "-b", "base"], root)
    run(["git", "config", "user.email", "harness@example.invalid"], root)
    run(["git", "config", "user.name", "N81 harness"], root)
    write(root, files)
    run(["git", "add", "-A"], root); run(["git", "commit", "-q", "-m", "base"], root)
    return root

def write(root, files):
    for path, text in files.items():
        full = os.path.join(root, path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        open(full, "w").write(text)

def branch(root, name, files, message):
    run(["git", "checkout", "-q", "-b", name, "base"], root)
    write(root, files)
    run(["git", "add", "-A"], root); run(["git", "commit", "-q", "-m", message], root)

def case(name, body):
    try:
        body()
        print(f"ok    {name}")
    except AssertionError as error:
        FAILURES.append(name)
        print(f"FAIL  {name}\n      {error}")

# --- the fixture shapes ------------------------------------------------------

CONTINUATION = '''\
/// The exposure exhibit, in miniature: a multi-line string const whose first
/// line ends in a backslash, so its body sits at column 0.
const EXPOSURE_MODULE: &str = "\\
struct Hidden {\\n\\
\\tx: i32,\\n\\
}\\n\\
\\n\\
impl Hidden {\\n\\
\\tfun mark(self): i32 { self.x }\\n\\
}\\n\\
\\n\\
// a comment inside the program text, at column 0\\n\\
export fun reachable(): i32 { 3 }\\n";
'''

# The header shape that matters: a MULTI-LINE `use … { … };`. `use vilan_core::{` starts with
# `use ` and does not end the item, and the fold used to insert its carried consts after the last
# line that merely STARTS with `use ` — which put them inside the brace list, exactly as
# visibility-a-35's merge shipped them ("the header lines were dropped inside a `use { }` block").
HEADER = (
    "//! A test file.\n\n"
    "use std::path::Path;\n"
    "use vilan_core::{\n"
    "    EntryMode, Error, Layer, MacroLimits, PackageSpec, Platform, PlatformPattern,\n"
    "    Workspace, analyze_source,\n"
    "};\n\n"
)

def base_file(extra_fns="", const_text=CONTINUATION):
    return (
        HEADER
        + const_text
        + "\n#[test]\nfn the_first_pin() {\n    assert_eq!(1, 1);\n}\n"
        + "\n#[test]\nfn the_second_pin() {\n    assert_eq!(2, 2);\n}\n"
        + extra_fns
    )

PATH = "crates/vilan-core/tests/module_resolution.rs"

# --- 1. the `"\` continuation ------------------------------------------------

def continuation_survives_the_fold():
    root = repo({PATH: base_file()})
    branch(root, "head", {PATH: base_file() + "\n#[test]\nfn a_head_only_pin() {\n    assert!(true);\n}\n"},
           "head adds a pin")
    branch(root, "lane", {PATH: base_file() + "\n#[test]\nfn a_lane_only_pin() {\n    assert!(true);\n}\n"},
           "lane adds a pin")
    run(["git", "checkout", "-q", "head"], root)
    out = run(["python3", os.path.join(TOOLS, "fold_tests_by_name.py"), PATH, "base", "lane"], root)
    text = open(os.path.join(root, PATH)).read()
    assert "export fun reachable(): i32 { 3 }" in text, f"the const body vanished:\n{text}"
    assert text.count("const EXPOSURE_MODULE") == 1, f"the const was duplicated:\n{text}"
    assert "a_lane_only_pin" in text and "a_head_only_pin" in text, f"a pin was lost:\n{text}"
    assert HEADER in text, f"the header moved:\n{text}"
    shutil.rmtree(root)

def continuation_survives_the_item_merge():
    root = repo({PATH: base_file()})
    branch(root, "head", {PATH: base_file() + "\n#[test]\nfn a_head_only_pin() {\n    assert!(true);\n}\n"},
           "head adds a pin")
    branch(root, "lane", {PATH: base_file() + "\n#[test]\nfn a_lane_only_pin() {\n    assert!(true);\n}\n"},
           "lane adds a pin")
    run(["git", "checkout", "-q", "head"], root)
    # round-trips exactly is an ASSERT inside the tool: a mis-split reads as a crash there
    run(["python3", os.path.join(TOOLS, "merge_items_by_name.py"), PATH, "base", "lane"], root)
    text = open(os.path.join(root, PATH)).read()
    assert "export fun reachable(): i32 { 3 }" in text, f"the const body vanished:\n{text}"
    assert text.count("const EXPOSURE_MODULE") == 1, f"the const was duplicated:\n{text}"
    assert "a_lane_only_pin" in text and "a_head_only_pin" in text, f"a pin was lost:\n{text}"
    shutil.rmtree(root)

# --- 2. the renamed-on-HEAD test ---------------------------------------------

def a_head_rename_is_not_resurrected():
    root = repo({PATH: base_file()})
    # HEAD renamed `the_second_pin` to `the_second_pin_renamed`
    renamed = base_file().replace("fn the_second_pin()", "fn the_second_pin_renamed()")
    branch(root, "head", {PATH: renamed}, "head renames a pin")
    branch(root, "lane", {PATH: base_file() + "\n#[test]\nfn a_lane_only_pin() {\n    assert!(true);\n}\n"},
           "lane adds a pin")
    run(["git", "checkout", "-q", "head"], root)
    out = run(["python3", os.path.join(TOOLS, "fold_tests_by_name.py"), PATH, "base", "lane"], root)
    text = open(os.path.join(root, PATH)).read()
    assert "fn the_second_pin_renamed()" in text, f"HEAD's rename was lost:\n{text}"
    assert "fn the_second_pin()" not in text, f"the old head was resurrected:\n{text}\n{out.stdout}"
    assert "a_lane_only_pin" in text, f"the lane's new pin was lost:\n{text}"
    assert "NOT resurrected" in out.stdout, f"the skip was not reported:\n{out.stdout}"
    shutil.rmtree(root)

def a_head_rename_is_not_resurrected_by_the_item_merge():
    root = repo({PATH: base_file()})
    renamed = base_file().replace("fn the_second_pin()", "fn the_second_pin_renamed()")
    branch(root, "head", {PATH: renamed}, "head renames a pin")
    branch(root, "lane", {PATH: base_file() + "\n#[test]\nfn a_lane_only_pin() {\n    assert!(true);\n}\n"},
           "lane adds a pin")
    run(["git", "checkout", "-q", "head"], root)
    out = run(["python3", os.path.join(TOOLS, "merge_items_by_name.py"), PATH, "base", "lane"], root)
    text = open(os.path.join(root, PATH)).read()
    assert "fn the_second_pin()" not in text, f"the old head was resurrected:\n{text}\n{out.stdout}"
    assert "a_lane_only_pin" in text, f"the lane's new pin was lost:\n{text}"
    shutil.rmtree(root)

# --- 3. the edited const -----------------------------------------------------

EDITED = CONTINUATION.replace("export fun reachable(): i32 { 3 }", "export fun reachable(): i32 { 4 }")

def an_edited_const_is_refused():
    root = repo({PATH: base_file()})
    branch(root, "head", {PATH: base_file() + "\n#[test]\nfn a_head_only_pin() {\n    assert!(true);\n}\n"},
           "head adds a pin")
    branch(root, "lane", {PATH: base_file(const_text=EDITED)
                          + "\n#[test]\nfn a_lane_only_pin() {\n    assert!(true);\n}\n"},
           "lane edits the const beside its pin")
    run(["git", "checkout", "-q", "head"], root)
    out = run(["python3", os.path.join(TOOLS, "fold_tests_by_name.py"), PATH, "base", "lane"],
              root, check=False)
    assert out.returncode == 1, f"the edit was taken silently:\n{out.stdout}"
    assert "EXPOSURE_MODULE" in out.stdout, f"the refusal does not name the const:\n{out.stdout}"
    text = open(os.path.join(root, PATH)).read()
    assert "{ 4 }" not in text, "a refused fold must not write the file"
    shutil.rmtree(root)

def an_edited_const_is_taken_under_allow_edit():
    root = repo({PATH: base_file()})
    branch(root, "head", {PATH: base_file() + "\n#[test]\nfn a_head_only_pin() {\n    assert!(true);\n}\n"},
           "head adds a pin")
    branch(root, "lane", {PATH: base_file(const_text=EDITED)
                          + "\n#[test]\nfn a_lane_only_pin() {\n    assert!(true);\n}\n"},
           "lane edits the const beside its pin")
    run(["git", "checkout", "-q", "head"], root)
    out = run(["python3", os.path.join(TOOLS, "fold_tests_by_name.py"), PATH, "base", "lane",
               "--allow-edit", "EXPOSURE_MODULE"], root)
    text = open(os.path.join(root, PATH)).read()
    assert "export fun reachable(): i32 { 4 }" in text, f"the lane's const was dropped:\n{text}"
    assert text.count("const EXPOSURE_MODULE") == 1, f"the const was duplicated:\n{text}"
    assert "a_head_only_pin" in text and "a_lane_only_pin" in text, f"a pin was lost:\n{text}"
    shutil.rmtree(root)

# --- the base behaviours the fixes must not break ----------------------------

def a_lane_deleted_fn_is_still_dropped():
    root = repo({PATH: base_file()})
    branch(root, "head", {PATH: base_file() + "\n#[test]\nfn a_head_only_pin() {\n    assert!(true);\n}\n"},
           "head adds a pin")
    branch(root, "lane", {PATH: base_file().replace(
        "\n#[test]\nfn the_second_pin() {\n    assert_eq!(2, 2);\n}\n", "")}, "lane deletes a pin")
    run(["git", "checkout", "-q", "head"], root)
    run(["python3", os.path.join(TOOLS, "fold_tests_by_name.py"), PATH, "base", "lane"], root)
    text = open(os.path.join(root, PATH)).read()
    assert "fn the_second_pin()" not in text, f"the lane's deletion was not honoured:\n{text}"
    assert "fn the_first_pin()" in text and "a_head_only_pin" in text, f"too much went:\n{text}"
    shutil.rmtree(root)

def a_new_lane_const_still_rides_along():
    root = repo({PATH: base_file()})
    branch(root, "head", {PATH: base_file() + "\n#[test]\nfn a_head_only_pin() {\n    assert!(true);\n}\n"},
           "head adds a pin")
    branch(root, "lane", {PATH: base_file() + '\nconst LANE_FIXTURE: &str = "x";\n'
                          + "\n#[test]\nfn a_lane_only_pin() {\n    let _ = LANE_FIXTURE;\n}\n"},
           "lane adds a fixture and its pin")
    run(["git", "checkout", "-q", "head"], root)
    out = run(["python3", os.path.join(TOOLS, "fold_tests_by_name.py"), PATH, "base", "lane"], root)
    text = open(os.path.join(root, PATH)).read()
    assert "const LANE_FIXTURE" in text, f"the new const did not ride along:\n{text}\n{out.stdout}"
    assert "a_lane_only_pin" in text, f"the pin was lost:\n{text}"
    shutil.rmtree(root)


LANE_CONTINUATION = '''\
/// The lane's own fixture, in the shape that broke the fold.
const LANE_MODULE: &str = "\\
struct Planted {\\n\\
\\tx: i32,\\n\\
}\\n\\
\\n\\
use pkg::a::{ b };\\n\\
\\n\\
export fun planted(): i32 { 9 }\\n";
'''

def a_lane_added_continuation_const_is_carried_whole():
    """The shape N81 is filed on: the lane adds a NEW const whose first line ends in `"\\`. It
    must arrive complete, and in the header's own region rather than inside the `use { }`."""
    root = repo({PATH: base_file()})
    branch(root, "head", {PATH: base_file() + "\n#[test]\nfn a_head_only_pin() {\n    assert!(true);\n}\n"},
           "head adds a pin")
    branch(root, "lane", {PATH: base_file() + "\n" + LANE_CONTINUATION
                          + "\n#[test]\nfn a_lane_only_pin() {\n    let _ = LANE_MODULE;\n}\n"},
           "lane adds a continuation const and its pin")
    run(["git", "checkout", "-q", "head"], root)
    out = run(["python3", os.path.join(TOOLS, "fold_tests_by_name.py"), PATH, "base", "lane"], root)
    text = open(os.path.join(root, PATH)).read()
    assert "const LANE_MODULE" in text, f"the new const did not ride along:\n{text}\n{out.stdout}"
    assert "export fun planted(): i32 { 9 }" in text, \
        f"the const's body vanished — it was cut at the first column-0 line:\n{text}"
    assert HEADER in text, f"the header was broken open:\n{text}"
    assert text.index("};") < text.index("const LANE_MODULE"), \
        f"the const landed inside the multi-line use block:\n{text}"
    assert "a_lane_only_pin" in text and "a_head_only_pin" in text, f"a pin was lost:\n{text}"
    shutil.rmtree(root)

# --- 4. the duplicate constant at the union ----------------------------------

LEDGER = "crates/vilan-cli/tests/diagnostics_ledger.rs"

def ledger_file(sites, extra_curated=""):
    return (
        "//! The ledger gate.\n\n"
        f"const RULE_STATEMENT_SITES: usize = {sites};\n\n"
        "const CURATED_RULE_STATEMENTS: &[(&str, &str)] = &[\n"
        '    ("a_rule", "a head"),\n'
        f"{extra_curated}"
        "];\n\n"
        "const ROWS_THE_ENUMERATION_CANNOT_REACH: &[(&str, &str)] = &[\n"
        '    ("400", "a reason"),\n'
        "];\n"
    )

def both_sides_bumping_one_constant_resolve_to_one_line():
    root = repo({LEDGER: ledger_file(23)})
    branch(root, "head", {LEDGER: ledger_file(28, '    ("head_rule", "h"),\n')}, "head adds five rules")
    branch(root, "lane", {LEDGER: ledger_file(29, '    ("lane_rule", "l"),\n')}, "lane adds six rules")
    run(["git", "checkout", "-q", "head"], root)
    merged = run(["git", "merge", "--no-ff", "--no-commit", "lane"], root, check=False)
    assert "<<<<<<<" in open(os.path.join(root, LEDGER)).read(), "the fixture did not conflict"
    mapping = os.path.join(TOOLS, "row-mapping-n81harness.json")
    open(mapping, "w").write('{"by_key": {}, "by_old_id": {}, "edited": []}')
    try:
        out = run(["python3", os.path.join(TOOLS, "apply_row_mapping.py"), "n81harness"], root, check=False)
    finally:
        os.remove(mapping)
    text = open(os.path.join(root, LEDGER)).read()
    assert "<<<<<<<" not in text, f"markers survived:\n{text}"
    assert text.count("const RULE_STATEMENT_SITES") == 1, \
        f"the scalar constant was unioned twice — the Order 35 break:\n{text}\n{out.stdout}"
    assert "const RULE_STATEMENT_SITES: usize = 34;" in text, \
        f"the two lanes' deltas were not summed through the base:\n{text}\n{out.stdout}"
    # the LIST constant is the case the union exists for: both entries survive
    assert '("head_rule", "h")' in text and '("lane_rule", "l")' in text, \
        f"the list constant lost an entry:\n{text}"
    shutil.rmtree(root)

def a_non_numeric_both_sides_change_stops_the_chain():
    root = repo({LEDGER: ledger_file(23).replace("usize = 23;", 'usize = 23;\nconst NAME: &str = "base";')})
    branch(root, "head", {LEDGER: ledger_file(23).replace("usize = 23;", 'usize = 23;\nconst NAME: &str = "head";')},
           "head renames it")
    branch(root, "lane", {LEDGER: ledger_file(23).replace("usize = 23;", 'usize = 23;\nconst NAME: &str = "lane";')},
           "lane renames it")
    run(["git", "checkout", "-q", "head"], root)
    run(["git", "merge", "--no-ff", "--no-commit", "lane"], root, check=False)
    mapping = os.path.join(TOOLS, "row-mapping-n81harness.json")
    open(mapping, "w").write('{"by_key": {}, "by_old_id": {}, "edited": []}')
    try:
        out = run(["python3", os.path.join(TOOLS, "apply_row_mapping.py"), "n81harness"], root, check=False)
    finally:
        os.remove(mapping)
    assert out.returncode != 0, f"a both-sides change that cannot be summed must stop:\n{out.stdout}"
    text = open(os.path.join(root, LEDGER)).read()
    assert text.count("const NAME") == 1, f"it was duplicated anyway:\n{text}"
    assert '"head"' in text, f"HEAD's line was not the one kept:\n{text}"
    shutil.rmtree(root)

for name, body in [
    ("the continuation const survives the fold", continuation_survives_the_fold),
    ("the continuation const survives the item merge", continuation_survives_the_item_merge),
    ("a head rename is not resurrected by the fold", a_head_rename_is_not_resurrected),
    ("a head rename is not resurrected by the item merge", a_head_rename_is_not_resurrected_by_the_item_merge),
    ("an edited const is refused", an_edited_const_is_refused),
    ("an edited const is taken under --allow-edit", an_edited_const_is_taken_under_allow_edit),
    ("a lane-deleted fn is still dropped", a_lane_deleted_fn_is_still_dropped),
    ("a new lane const still rides along", a_new_lane_const_still_rides_along),
    ("a lane-added continuation const is carried whole", a_lane_added_continuation_const_is_carried_whole),
    ("both sides bumping one constant resolve to one line", both_sides_bumping_one_constant_resolve_to_one_line),
    ("a non-numeric both-sides change stops the chain", a_non_numeric_both_sides_change_stops_the_chain),
]:
    case(name, body)

print()
if FAILURES:
    print(f"{len(FAILURES)} FAILED: {FAILURES}"); sys.exit(1)
print("all merge-tool pins green")
