"""No test may rewrite canonical project state in the real repository.

MEASURED 2026-08-26. test_sv_memory_unreadable_2026-08-26.py ran sv's main()
with cwd=REPO -- the actual repository -- and no --dry-run. sv did what sv does:
it regenerated docs/CURRENT_STATE.md, resources/ONBOARDING.md and
resources/RECOVERY.md in the working tree. On EVERY suite run.

That is why those three files sat perpetually modified in git status, and it is
how unrelated content kept being swept into commits by sv's auto-staging -- the
same route that put a literal "BROKEN-STAMP" into resources/MEMORY_EXCLUSIONS.md
and shipped it in commit 80faf11.

Verified both ways before fixing: sv --dry-run dirties 0 files and still prints
every string the test asserts on; the live run dirties 3.

This file is the guard, not the fix. It reads the test corpus and fails if any
test invokes sv's main against the real repository without --dry-run.

WHY STATIC RATHER THAN RUNTIME. A runtime check ("are these files clean?")
depends on test ordering and on what the developer happened to leave dirty
before running pytest. Reading the corpus does not.
"""
import ast
import pathlib
import re

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
TESTS = REPO / "bench" / "tests"

# Files sv regenerates. Rewriting any of these from a test dirties the tree.
CANONICAL = [
    "docs/CURRENT_STATE.md",
    "resources/ONBOARDING.md",
    "resources/RECOVERY.md",
    "resources/MEMORY_EXCLUSIONS.md",
]

# An invocation of sv's CLI entry point from inside a test.
# Split in 2 on 2026-11-14: the script NAME and the in-process entry point
# are different things and were conflated in 1 alternation, which is how a
# `read_text()` of the sv source read as an invocation of it.
SV_SCRIPT = re.compile(r"cdsfl_sv\.py")
SV_MAIN_FN = re.compile(r"(?:cdsfl_)?sv\.main")
DRY = re.compile(r"--dry-run")
# cwd pointing at the real repository rather than a tmp_path
REAL_CWD = re.compile(r"cwd\s*=\s*(REPO|REPO_ROOT|str\(REPO\)|str\(REPO_ROOT\))\b")


def _test_files():
    return sorted(p for p in TESTS.glob("test_*.py"))


def test_the_corpus_is_actually_being_read():
    """A scan that silently matches nothing passes forever."""
    files = _test_files()
    assert len(files) > 50, f"only {len(files)} test files found; the glob is wrong"
    assert any(sv_invocation_call_sites(p.read_text(encoding="utf-8", errors="replace"))
               for p in files), (
        "no test invokes sv.main() anywhere, so this guard is inert. If the sv "
        "end-to-end test was deleted, delete this guard with it."
    )


def sv_invocation_call_sites(src: str) -> list[tuple[int, str, bool]]:
    """Every call site that RUNS sv: (line, call source, is_in_process).

    Separated from the offender predicate on 2026-11-14 so the anti-vacuity
    check and the live check share 1 finder. The anti-vacuity check used to scan
    for the retired `SV_MAIN` alternation, which matched a `read_text()` of the
    sv source as readily as a call of it -- so it could have reported the guard
    live while 0 invocations existed.
    """
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return []
    out: list[tuple[int, str, bool]] = []
    for n in ast.walk(tree):
        if not isinstance(n, ast.Call):
            continue
        call = ast.unparse(n)
        fn = ast.unparse(n.func)
        is_subproc_sv = "subprocess" in fn and bool(SV_SCRIPT.search(call))
        is_inproc_sv = bool(SV_MAIN_FN.fullmatch(fn))
        if is_subproc_sv or is_inproc_sv:
            out.append((n.lineno, call[:120], is_inproc_sv))
    return out


def _enclosing_functions(tree):
    """node -> innermost enclosing function, so argv patched 2 lines above counts."""
    owner = {}
    for fn in ast.walk(tree):
        if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for sub in ast.walk(fn):
                owner[sub] = fn
    return owner


def sv_offender_call_sites(src: str) -> list[tuple[int, str]]:
    """Call sites that RUN sv against the REAL repository with no --dry-run.

    ★ CALL-SCOPED AND AST-BASED SINCE 2026-11-14, AND THE REWRITE IS A REPAIR OF
    A FALSE ACCUSATION, not a relaxation. The predicate was 3 regexes ANDed over
    the WHOLE FILE: any mention of `cdsfl_sv.py"` anywhere, any `cwd=REPO`
    anywhere, and no `--dry-run` anywhere. On the full-suite run of 2026-11-14 it
    accused `test_the_co_author_trailer_is_not_doubled_2026-11-14.py`, which
    invokes no sv CLI at all: established by AST rather than by reading, its only
    subprocess call is `git log -1 --format=%B 4a802768`, read-only, and its 4
    mentions of `cdsfl_sv.py` are 1 prose line, 1 `import`, 1 `read_text()` for
    an AST parse and 1 assertion message. A substring is not a call -- the shape
    this project has now met repeatedly -- and the remedy the guard printed,
    "pass --dry-run", would have put a meaningless flag string into a file with
    nothing to pass it to.

    ★ AND THE FIRST REWRITE WAS WRONG IN THE OTHER DIRECTION, which is why this
    docstring names the mechanism. It assumed an in-process `sv.main()` writes
    relative to the process cwd, so all 3 in-process call sites in the corpus
    were flagged. sv does not: it writes under `repo_root()`, and all 3 of them
    monkeypatch `sv.repo_root` to a tmp directory. A probe that assumes the wrong
    write target manufactures its own failures.

    Measured over 937 test files on 2026-11-14: old predicate 1 offender (a false
    positive), this one 0. Producer:
    `scripts/the_sv_mutation_guard_accused_a_clean_file_2026-11-14.py`.
    """
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return []
    owner = _enclosing_functions(tree)
    by_line = {n.lineno: n for n in ast.walk(tree) if isinstance(n, ast.Call)}
    out: list[tuple[int, str]] = []
    for lineno, call, is_inproc_sv in sv_invocation_call_sites(src):
        n = by_line.get(lineno)
        f = owner.get(n) if n is not None else None
        scope = ast.unparse(f) if f is not None else call
        if is_inproc_sv:
            # Safe iff the write target is redirected away from the real repo.
            if "repo_root" in scope or "chdir" in scope:
                continue
        elif not REAL_CWD.search(call):
            continue        # runs somewhere else entirely; nothing to police
        if not DRY.search(scope):
            out.append((n.lineno, call[:120]))
    return out


@pytest.mark.parametrize("path", _test_files(), ids=lambda p: p.name)
def test_no_test_runs_sv_against_the_real_repo_without_dry_run(path):
    src = path.read_text(encoding="utf-8", errors="replace")
    sites = sv_offender_call_sites(src)
    assert not sites, (
        f"{path.name} invokes sv against the REAL repository with no --dry-run, "
        f"at line(s) {', '.join(str(ln) for ln, _ in sites)}: "
        + "; ".join(c for _, c in sites)
        + ". sv regenerates "
        + ", ".join(CANONICAL[:3])
        + " when it runs, so every suite run would dirty the working tree. Pass "
          "--dry-run: it exercises the same path and writes nothing (measured "
          "2026-08-26 -- dry run dirties 0 files, live run dirties 3)."
    )


def test_the_guard_would_catch_the_original_defect():
    """Commissioning. Feed it the code as it was on 2026-08-26 and it must fail;
    feed it the fix and it must pass. Otherwise the guard is decoration."""
    before = ("import cdsfl_sv as sv\n"
              "subprocess.run([sys.executable, '-c', \"sys.argv = ['cdsfl_sv.py']; "
              "sys.exit(sv.main())\"], cwd=REPO)\n")
    after = ("import cdsfl_sv as sv\n"
             "subprocess.run([sys.executable, '-c', \"sys.argv = ['cdsfl_sv.py', "
             "'--dry-run']; sys.exit(sv.main())\"], cwd=REPO)\n")
    elsewhere = ("import cdsfl_sv as sv\n"
                 "subprocess.run([...], cwd=tmp_path)\n")

    # ★ CALLS THE LIVE PREDICATE, 2026-11-14. It used to define its own copy of
    # the 3-regex conjunction, so the commissioning check and the live check were
    # 2 representations of 1 truth with no comparator -- the shape
    # `execute-do-not-grep` names. Fixing one would have left the other
    # asserting the retired predicate and passing.
    def offends(src):
        return bool(sv_offender_call_sites(src))

    assert offends(before), "the guard does not catch the defect it was written for"
    assert not offends(after), "the guard rejects the accepted fix"
    assert not offends(elsewhere), "the guard fires on a test that uses a tmp cwd"

    # ★ THE 4 CASES ADDED 2026-11-14, each from something actually observed.
    inproc = "import cdsfl_sv as sv\ndef t():\n    sv.main()\n"
    inproc_dry = ("import cdsfl_sv as sv\ndef t():\n"
                  "    monkeypatch.setattr(sys, 'argv', ['sv', '--dry-run'])\n"
                  "    sv.main()\n")
    inproc_redirected = ("import cdsfl_sv as sv\ndef t():\n"
                         "    monkeypatch.setattr(sv, 'repo_root', lambda: tmp_path)\n"
                         "    sv.main()\n")
    # The exact shape falsely accused on 2026-11-14: an import, an AST read of
    # the sv source, and an unrelated read-only `git log` with cwd=REPO.
    import_and_read = (
        'import cdsfl_sv as sv\n'
        'def t():\n'
        '    subprocess.run(["git", "log", "-1", "--format=%B", "4a802768"], cwd=REPO)\n'
        'def u():\n'
        '    tree = ast.parse((REPO / "scripts" / "cdsfl_sv.py").read_text())\n')
    assert offends(inproc), (
        "an in-process sv.main() with no redirect and no --dry-run writes to the "
        "real repository and must still be caught")
    assert not offends(inproc_dry), "--dry-run patched into argv above the call is the fix"
    assert not offends(inproc_redirected), (
        "sv writes under repo_root(), so a test that redirects repo_root writes "
        "nowhere near the real repository")
    assert not offends(import_and_read), (
        "importing sv, reading its source for an AST parse, and running an "
        "unrelated read-only git command is not an invocation of sv")


def test_the_producer_for_this_repair_actually_runs():
    """EXECUTE the producer, do not merely name it.

    ★ A MENTION IS NOT A REACH. `test_an_unreached_producer_set_cannot_grow_
    2026-11-08.py` admits no producer no test reaches, and the surveyor behind
    it checks whether a test NAMES the path -- so this file's docstring alone
    would have silenced that refusal while proving nothing. Recorded on
    2026-11-14 as entry B195, the unwatchable commit board, and it applies here.

    ★ IT PINS NO COUNT. The producer's figures are over the live test corpus,
    which grows, so the assertion is on its VERDICT: it exits 0 only when all 7
    of its commissioning cases are decided correctly, and it exits 1 when any is
    not. A pinned 937 would go stale on the next test file added.
    """
    producer = REPO / "scripts" / "the_sv_mutation_guard_accused_a_clean_file_2026-11-14.py"
    if not producer.is_file():
        pytest.skip("the producer is not in this checkout")
    import subprocess
    import sys as _sys
    r = subprocess.run([_sys.executable, str(producer)], capture_output=True,
                       text=True, timeout=300, cwd=str(REPO))
    assert r.returncode == 0, (
        "the producer refused: a commissioning case is decided wrongly.\n"
        + r.stdout[-2000:] + r.stderr[-800:])
    assert "fixtures decided correctly: 7 of 7" in r.stdout, (
        "the producer no longer reports all 7 commissioning cases correct:\n"
        + r.stdout[-1500:])
    assert "NEW call-scoped AST predicate flags: 0 of" in r.stdout, (
        "the live corpus now holds an offender; read the producer's output "
        "rather than assuming this guard is wrong:\n" + r.stdout[-1500:])
