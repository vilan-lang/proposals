#!/usr/bin/env python3
"""Harness for changelog_union.py's patch-release path (order 54). Read-only against the vilan
repo (`git show` only); the end-to-end cases run in throwaway repos under a temp dir.
Findings baked in: next@00df2f09 ALREADY lacks `## Unreleased` (editor-54's merge dropped the
heading and filed E327/E328 under `## v0.51.1`), so the literal shape is also reconstructed
from its parents: 9002d272 (fold, no Unreleased) + editor-54 (e5a89f27)."""
import importlib.util, os, subprocess, sys, tempfile, shutil
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.normpath(os.path.join(HERE, "..", "..", "..", "changelog_union.py"))
W = os.environ.get("VILAN_INTEGRATION", os.path.expanduser("~/code/vilan-lang/vilan/.claude/worktrees/integration"))
spec = importlib.util.spec_from_file_location("changelog_union", SCRIPT)
cu = importlib.util.module_from_spec(spec); spec.loader.exec_module(cu)

def git_show(ref): return subprocess.run(["git", "-C", W, "show", f"{ref}:CHANGELOG.md"], capture_output=True, text=True, check=True).stdout
def sections(text):
    ls = text.split("\n"); b = cu.unreleased_bounds(ls)
    return ls, b
def heads(text, b_ls=None):
    ls, b = sections(text)
    return [h for h, _ in cu.parse_entries(ls[b[0]:b[1]])] if b else []
def tag(h): return h[:14]
ok = 0
def check(cond, msg):
    global ok
    if not cond: print("FAIL:", msg); sys.exit(1)
    ok += 1; print("ok  :", msg)

# ---- case 1: the literal shape, reconstructed (fold + editor-54, then std-54)
fold, editor, std = git_show("9002d272"), git_show("e5a89f27"), git_show("std-54")
check(cu.unreleased_bounds(fold.split("\n")) is None, "9002d272 (the fold) has no `## Unreleased`")
check(cu.patch_shape(fold, editor), "fold + editor-54 is the patch shape")
head1, n1 = cu.union_from_copies(fold, editor)
h1 = heads(head1)
check(n1 == 2 and len(h1) == 2 and h1[0].startswith("**E327") and h1[1].startswith("**E328"),
      f"step 1: Unreleased = E327, E328 (E331 dropped, it is in v0.51.1) -> {[tag(h) for h in h1]}")
check(head1.split("\n")[:25] == fold.split("\n")[:25], "step 1: output starts with HEAD's header")
i = head1.index("## v0.51.1"); j = fold.index("## v0.51.1")
check(head1[i:] == fold[j:], "step 1: from `## v0.51.1` onward equals HEAD's file")

check(cu.patch_shape(head1, std), "HEAD(E327,E328 Unreleased) + std-54 is the patch shape (E331 overlap)")
out, n = cu.union_from_copies(head1, std)
ls = out.split("\n")
check(sum(1 for x in ls if x.startswith("## Unreleased")) == 1, "exactly one `## Unreleased`")
h = heads(out)
want = ["**E327", "**E328", "**F?4", "**A173 S1 + B?1", "**A173 S1 + E?5"]
check(len(h) == 5 and h[0].startswith("**E327") and h[1].startswith("**E328"), f"HEAD's two editor-54 entries first -> {[tag(x) for x in h]}")
std_order = [x for x in heads(std) if not x.startswith("**E331")]
check(h[2:] == std_order and len(std_order) == 3, "then std-54's three, in the lane's order: " + ", ".join(tag(x) for x in std_order))
check(not any(x.startswith("**E331") for x in h), "no E331 in Unreleased")
check(out.startswith(head1[:head1.index("## ")]), "output starts with HEAD's header")
check(out[out.index("## v0.51.1"):] == head1[head1.index("## v0.51.1"):], "from `## v0.51.1` onward equals HEAD's file (incl. the commit marker)")
check("<!-- commit: e79fec2d -->" in out and out.count("<!-- commit: e79fec2d -->") == 1, "commit marker kept once, in v0.51.1")
ulines = ls[cu.unreleased_bounds(ls)[0]:cu.unreleased_bounds(ls)[1]]
check(sum(x.startswith("<!-- family:") for x in ulines) == sum(x.startswith("**") for x in ulines) == 5, "marker/headline parity 5/5")
check(ulines[-1] == "" and ls[cu.unreleased_bounds(ls)[1]].startswith("## v0.51.1"), "one blank line before `## v0.51.1`")
again, n2 = cu.union_from_copies(out, std)
check(n2 == 0 and again == out, "idempotent: merging std-54 again adds nothing")

# ---- case 2: the file as found (next@00df2f09: no Unreleased, E327/E328 already misfiled in v0.51.1)
bad = git_show("00df2f09")
check(cu.patch_shape(bad, std), "00df2f09 + std-54 is the patch shape")
out2, n2 = cu.union_from_copies(bad, std)
check(n2 == 3 and heads(out2) == std_order, "as-found HEAD: Unreleased created with std-54's three only")
check(out2[out2.index("## v0.51.1"):] == bad[bad.index("## v0.51.1"):], "as-found HEAD: from `## v0.51.1` onward equals HEAD's file")

# ---- case 3: the ordinary case is not the patch shape, and stays byte-identical end to end
E = lambda fam, name, extra="": f"<!-- family: {fam} -->\n**{name}: text.**{extra}\n"
def doc(unreleased): return "# Changelog\n\n<!-- header -->\n\n## Unreleased\n\n" + unreleased + "\n## v1.0.0 — 2026-01-01\n\n<!-- family: fix -->\n**Z1: old.**\n"
base = doc("")
a = doc(E("fix", "A1") + "\n"); b = doc(E("feature", "B1") + "\n" + E("fix", "B2") + "\n")
check(not cu.patch_shape(a, b), "ordinary: no overlap -> not the patch shape")

def sh(cwd, *cmd, env=None): return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, env=env)
def make_repo(root, head_text, lane_text, base_text):
    shutil.rmtree(root, ignore_errors=True); os.makedirs(root)
    g = lambda *c: sh(root, "git", "-c", "user.name=t", "-c", "user.email=t@t", *c)
    g("init", "-q", "-b", "next"); open(f"{root}/CHANGELOG.md", "w").write(base_text); g("add", "."); g("commit", "-qm", "base")
    g("checkout", "-q", "-b", "lane"); open(f"{root}/CHANGELOG.md", "w").write(lane_text); g("commit", "-qam", "lane")
    g("checkout", "-q", "next"); open(f"{root}/CHANGELOG.md", "w").write(head_text); g("commit", "-qam", "head")
    g("merge", "--no-ff", "--no-commit", "lane")
def run_script(script, root):
    r = sh(root, sys.executable, script, "lane"); return r.returncode, r.stdout.strip(), open(f"{root}/CHANGELOG.md").read()

orig = os.environ.get("CHANGELOG_UNION_ORIG")
tmp = tempfile.mkdtemp(prefix="clu-")
try:
    if orig:
        make_repo(f"{tmp}/o", a, b, base); make_repo(f"{tmp}/n", a, b, base)
        ro, rn = run_script(orig, f"{tmp}/o"), run_script(SCRIPT, f"{tmp}/n")
        check(ro == rn, f"ordinary (conflicting hunk): old and new script give identical exit/stdout/file ({ro[0]}, {ro[1]})")
        check("**A1" in rn[2] and "**B2" in rn[2] and rn[2].index("**A1") < rn[2].index("**B1"), "ordinary: HEAD side then lane side")
    # ---- case 4: end to end, the patch shape in a throwaway repo (HEAD = fold + editor; lane = std-branched-before-patch)
    make_repo(f"{tmp}/p", head1, std, git_show("b7c7afe0"))
    code, msg, text = run_script(SCRIPT, f"{tmp}/p")
    check(code == 0 and text == out, f"end to end in a temp repo (mid-merge, working tree conflicted or auto-merged): exit 0, file == union_from_copies ({msg})")
finally:
    shutil.rmtree(tmp, ignore_errors=True)
print(f"ALL {ok} CHECKS PASSED")
